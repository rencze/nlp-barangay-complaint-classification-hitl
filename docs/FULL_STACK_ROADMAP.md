# Barangay complaint system: implementation roadmap

Prepared 26 October 2026. This is a design and acceptance plan, not an implementation or deployment claim. Offline classification has been reproduced on the unchanged 24,000-record synthetic corpus. The existing SQLite/HTML prototype is exploratory and does not satisfy this design.

## Architecture and version decisions

Use a modular monolith: Next.js with TypeScript for the resident and staff interfaces; FastAPI for all business rules and REST APIs; PostgreSQL for transactional records; scikit-learn for saved, versioned TF-IDF/Linear SVM inference. Serve the web and `/api/v1` through one HTTPS origin. Keep a worker process using the same backend modules for notifications, due-date checks, export and training jobs. A PostgreSQL outbox/job table is sufficient initially; Redis/Celery and separate microservices are optional only when operational evidence warrants them.

Official documentation was reviewed on 26 October 2026:

| Component | Planning decision | Official evidence / implementation gate |
|---|---|---|
| Next.js | 16.x App Router, TypeScript; choose and lock a supported patched 16.x release at implementation | [Installation](https://nextjs.org/docs/app/getting-started/installation), [v16 guide](https://nextjs.org/docs/app/guides/upgrading/version-16): Node minimum 20.9, TypeScript minimum 5.1. Use a currently supported Node LTS meeting the minimum, not an obsolete minimum merely because it runs. Run lint explicitly as well as typecheck/build. |
| FastAPI | Current stable 0.143.x line is a reviewed starting point, not a tested application lock | [Release notes](https://fastapi.tiangolo.com/release-notes/) list 0.143.2 dated 15 October 2026; current FastAPI dropped Python 3.9. Use Python 3.13, Pydantic v2, SQLAlchemy 2, Alembic and psycopg 3; resolve and lock exact compatible versions with CI before implementation. |
| PostgreSQL | 18 with current stable minor (reviewed policy lists 18.6); do not choose a release candidate | [Version policy](https://www.postgresql.org/support/versioning/) supports each major for five years and recommends the current minor. Recheck provider support and patch availability before deployment. |
| ML | Python 3.13.5; scikit-learn 1.8.0 and versions in research requirements | Preserve the research lock for research artifacts. Do not load pickles across untested dependency changes. Export a manifest, checksum and class order with every artifact. |

Framework line selection has been reviewed; frontend/backend installation and compatibility testing are future phase deliverables. Do not describe these planned versions as installed or deployed. Editable integration and database diagrams are in `docs/diagrams/`.

## Scope and routing contract

The MVP path is authenticated submission -> immutable narrative version -> saved-model prediction -> Valid directly enters accepted case management, Suspicious/Spam enters staff review -> acceptance or clarification/rejection -> case processing and resident tracking. Valid routing creates an Accepted disposition with a system actor and routing-policy version; this is an administrative action, not a human-verified label. Urgent safety handling runs independently of the classifier: an explicit urgent-help prompt, resident urgency flag and staff priority lane must work even if prediction fails or says Spam. Local emergency/referral information must be verified with the participating office before go-live. A report is never silently discarded by a model.

Required form fields: subject and narrative. Incident date/time, timezone and Purok/Sitio or landmark are optional when known. Do not require GPS, maps, photo uploads, or image classification in the initial scope. Preserve the original text and version ID; normalized inference text never replaces the resident's narrative.

| Independent concept | Allowed values | Integrity rule |
|---|---|---|
| Prediction | Valid, Suspicious, Spam | Immutable output tied to narrative and model versions |
| Human-verified label | Valid, Suspicious, Spam | Reviewer/adjudicator, rubric version and original narrative required; absence is allowed |
| Administrative disposition | Accepted, Pending Clarification, Rejected | Rejection and clarification need reasons; acceptance need not change text label |
| Case status | Unresolved, Ongoing, Resolved | Only accepted complaints have cases; deadlines do not resolve cases |
| Events/flags | Overdue, Referred, Reopened, urgent | Never classifier labels or extra primary case statuses |

A Suspicious narrative can be administratively accepted and remain labeled Suspicious. Clarification creates a new narrative version with an independent prediction and, when reviewed, its own verified label. Do not rewrite the original label based on later information. Rejection never automatically creates a Spam feedback example. Periodic stratified audits of predicted Valid reports cover class/language/error patterns without making every Valid complaint wait for routine HITL.

## Normalized data model

Use UUID primary keys, `timestamptz` timestamps stored in UTC, explicit actors and `created_at` on every event. Display timestamps in Asia/Manila. Use text enums/check constraints for the three label sets, disposition and primary statuses. Append decision histories rather than overwriting evidence; maintain a current-state projection transactionally.

| Table | Important columns / relations | Constraints and indices |
|---|---|---|
| users | id, normalized_email, password_hash, verified_at, disabled_at | Unique normalized email; never return password hash |
| roles, permissions | id, unique code | Resident, reviewer, case officer, supervisor, model approver, system admin are distinct privileges |
| user_roles, role_permissions | composite FKs | Composite PKs; no client-selected role grants |
| sessions | user_id, hashed_token, expires_at, revoked_at | Unique hashed token; expiry index; rotation and revocation |
| complaints | resident_id, tracking_reference, subject, urgent_flag, current_version_id, row_version | Unique random nonsequential reference; resident/date and priority/date indices |
| narrative_versions | complaint_id, version_no, original_text, text_hash, parent_version_id, author_id | Unique (complaint_id, version_no); (id, complaint_id) unique for same-complaint composite FKs; append-only |
| predictions | narrative_version_id, model_version_id, predicted_label, margins, probabilities, calibration_version, latency_ms | Unique (narrative_version_id, model_version_id, inference_policy_version); probability null without approved calibration |
| administrator_reviews | narrative_version_id, prediction_id, reviewer_id, reason, rubric_version | Review immutable and attributable; predictions must belong to same narrative |
| verified_labels | narrative_version_id, review_id, label, adjudicated_by, eligibility_status | Review FK; partial unique current adjudicated label per version; retain superseded labels |
| dispositions | complaint_id, narrative_version_id, state, reason, actor_id, policy_version | Rejected needs reason; current disposition projection locked during changes |
| clarification_requests | complaint_id, narrative_version_id, review_id, question, due_at | Indexed open requests and due date |
| clarification_responses | request_id, resident_id, narrative_version_id, response_text | Ownership and same-complaint FK checks; response cannot modify old narrative |
| accepted_cases | complaint_id, accepted_disposition_id, current_status, due_at, deadline_policy_id, row_version | Unique complaint_id; FK to Accepted disposition (trigger/service transaction check); status enum; status/due index |
| case_assignments | case_id, officer_id, assigned_by, started_at, ended_at | Index officer/open assignment; partial unique primary active assignment per case |
| case_actions | case_id, actor_id, event_type, reason, occurred_at, metadata | Timeline (case_id, occurred_at); referral recipient and overdue/reopened events here |
| status_transitions | case_id, from_status, to_status, actor_id, reason, action_id | Require resolution verification before Resolved; reopening event maps Resolved -> Unresolved/Ongoing |
| notifications | user_id, complaint_id, event_id, template_code, delivery_status, next_attempt_at | Unique (user_id,event_id,template_code); retry index, minimal message content |
| feedback_examples | narrative_version_id, verified_label_id, quality_reviewer_id, dedup_group_id, eligible_at, consent_basis | Unique eligible narrative/version; excluded/test membership flags; never copy disposition as label |
| training_runs | initiated_by, authorized_by, config_hash, corpus_manifest_hash, seed, state, metrics_uri | Frozen input manifests and run logs; explicit queued/running/failed/evaluated states |
| training_run_examples | training_run_id, feedback_example_id, usage_partition | Composite PK; immutable membership; disjoint fit/evaluation groups |
| model_versions | training_run_id, artifact_uri, sha256, class_order, preprocessing_version, dependency_lock_hash, calibration_method, approval_state | Immutable artifact path/checksum; rollback target; only one active version via unique partial index |
| model_approvals | model_version_id, approver_id, decision, reason, timestamp | Separate permission; record rejected as well as approved candidates |
| audit_events | actor_id, entity_type, entity_id, event_type, request_id, reason, occurred_at | Append-only application DB role; event/date/entity indices; no full narrative/token dumps |
| outbox_jobs | event_id, kind, payload_reference, state, attempts, available_at | Unique dedup key; worker claims with transactional locks; no raw secrets in job payload |
| deadline_policies | code, version, applicability, response_target, escalation_rule, calendar | Versioned policy set by office; no assumed universal legal resolution deadline |

PostgreSQL CHECK cannot verify another table's state: enforce Accepted-only case creation and narrative/review consistency with FKs where possible and tested transactional services or constraint triggers otherwise. Restrict cascade deletion for evidence; use documented retention/redaction workflows. Add FK indices (PostgreSQL does not automatically index every referencing column). Index complaint ownership, review queue, assigned cases, open clarification, due dates, model status and audit timelines. Avoid broad text search indices on private narratives until access and retention needs are established. SQL migration and ER diagrams must be kept synchronized.

## API contract

All paths below use `/api/v1`. UUIDs are internal IDs; a tracking reference is not authorization. Pagination uses a bounded cursor and maximum page size 100. Responses expose only fields appropriate to the actor. Public input never includes predicted label, verified label, actor role, model path, disposition or status.

| Method/path | Request schema | Success response / authorization |
|---|---|---|
| POST /auth/register | email, password, display_name, privacy_ack_version | 202 generic verification result; resident only, no role field |
| POST /auth/login | email, password | 200 user summary and secure session cookie; throttled |
| POST /auth/logout | CSRF token | 204; revoke server session |
| POST /auth/verify, /auth/reset-request, /auth/reset | one-use token / email / token+new_password | Generic request response, expiring hashed single-use tokens |
| GET /me | none | 200 own account, effective permissions |
| POST /complaints | subject(1-200), narrative(1-10000), incident_at?, incident_timezone?, location_text?(0-300), urgent_flag | 201 reference, complaint_id, version_id, processing_state, disposition?, case_status?; authenticated resident; Idempotency-Key required |
| GET /complaints | cursor, limit | 200 own complaints only; staff use separate scopes |
| GET /complaints/{id} | none | 200 own detail or authorized staff view; 404 for inaccessible record |
| GET /complaints/{id}/history | cursor | 200 visible resident notices/timeline; sensitive staff notes excluded |
| POST /complaints/{id}/clarifications/{request_id}/responses | response_text, revised_narrative? | 201 response_id, new version ID when revised; owner only |
| POST /complaints/{id}/feedback | rating?, comment?, reconsideration_requested, reason? | 201 feedback/reconsideration event; owner only |
| GET /admin/review-queue | label?, urgent?, assigned_to?, cursor | 200 queued predictions; reviewer permission |
| POST /admin/reviews | narrative_version_id, prediction_id, verified_label?, disposition, reason, expected_row_version | 201 review/label/disposition; separate decision and label, reviewer only |
| POST /admin/clarifications | complaint_id, narrative_version_id, question, response_due_at? | 201 request_id, resident notification; reviewer only |
| GET /admin/cases | status?, overdue?, officer?, cursor | 200 accepted cases; assignment/supervisor scope |
| POST /admin/cases/{id}/assignments | officer_id, reason, expected_row_version | 201 assignment and audit event; supervisor permission |
| POST /admin/cases/{id}/actions | action_type, reason, referral_target?, evidence_summary? | 201 timeline event; assigned officer/supervisor |
| POST /admin/cases/{id}/status-transitions | to_status, reason, verification_summary?, expected_row_version | 201 transition; Resolved requires verification; unauthorized/invalid transitions fail |
| POST /admin/cases/{id}/reopen | reason, target_status, expected_row_version | 201 Reopened action + Unresolved/Ongoing transition; supervisor |
| GET /notifications; POST /notifications/{id}/read | cursor / none | Own notifications and 204 read confirmation |
| POST /internal/predictions | narrative_version_id | 201 prediction ID/model version/label/margins/probabilities?; trusted worker credential only; no arbitrary artifact input |
| GET /admin/models; GET /admin/training-runs/{id} | none | Manifests and redacted job status; model-maintainer permission |
| POST /admin/training-runs | approved_feedback_snapshot_id, config_id, justification | 202 run_id; administrator authorization; no training in HTTP request |
| POST /admin/models/{id}/approve, /activate, /rollback | reason, expected_active_version | 201 audited gate; model-approver/supervisor permission; atomic swap |
| GET /health/live; /health/ready | none | Minimal 200/503; readiness checks DB and approved artifact; no secrets |

Example submission response:

```json
{
  "complaint_id": "<uuid>", "tracking_reference": "<random-reference>",
  "narrative_version_id": "<uuid>", "processing_state": "classified",
  "prediction": {"label": "Suspicious", "model_version": "research-reference-v1", "probabilities": null},
  "disposition": null, "case_status": null, "next_action": "Administrator review"
}
```

The example is a contract illustration, not a measured model output or a deployment-ready approved model name. For a Valid prediction, record policy-based acceptance and create an Unresolved case in one transaction. For Suspicious/Spam, `case_status` remains null until acceptance. A model-unavailable submission is retained with pending processing and review routing, not assigned a fabricated default Valid label.

## Inference and model lifecycle

Load one approved artifact at backend/worker startup from a server-controlled read-only registry path. Verify checksum, supported dependencies, preprocessing version, class order and startup canary records before readiness. Never unpickle a resident-uploaded file. Keep raw text with its immutable version, apply exactly the preprocessing saved in that artifact, then transform with its matching vectorizer and predict. Research reference pipelines use raw input and vectorizer defaults; the current `normalize_text` helper is not part of that historical pipeline. The new combined candidate uses NFKC/casefold/whitespace inside both feature branches. Record label, margins, model/config/calibration versions, input hash, timestamp and latency. Return probabilities only when a separately approved calibrated artifact meets independent reliability criteria; softmax margins are not calibrated probabilities. No probability threshold is needed for the agreed class-based routing.

Submission never retrains a model. Registry activation is transactional and audited; worker instances check the approved version, load and validate before atomically replacing their in-memory pointer. In-flight jobs record their actual version. Keep previous compatible artifacts for rollback, and test a failed activation and mixed-version deployment. Inference errors preserve the report, surface a safe pending state and create an administrative task. Set narrative length, queue size, timeouts and CPU/concurrency budgets using measurements.

## Authentication, security and privacy

Use server-side opaque sessions in HttpOnly, Secure, SameSite cookies, with CSRF protection for mutations and restrictive same-origin CORS. Hash passwords with Argon2id, never reversible encryption; generic login/reset errors, account verification, expiring one-use reset tokens, throttling and lockout with abuse safeguards. Require MFA for staff before field use. Authorization combines permission and object ownership/assignment on every backend operation. UI hiding is not authorization. Staff cannot grant themselves roles. Separate model authorization/activation permission from ordinary review.

Validate schemas strictly, reject control-only/empty text and oversized payloads, preserve Unicode and negations, escape all narrative display, parameterize SQL, prevent unsafe redirects and redact exception details. Use TLS, secret injection outside source, least-privilege DB accounts, encrypted backups, tested restoration, retention/access/export rules approved by the office and audit access to private narratives. Resident notices and external email must not include sensitive narratives. Do not log cookies/passwords, raw body dumps or personal identifiers in routine operational logs. Protect CSV exports against spreadsheet formula injection if exports are later added. Use dependency and secret scanning, account access revocation and an incident response procedure. Specific legal compliance requires institutional review; this plan makes no compliance certification.

Use 401 for absent/expired session, 403 for forbidden actions where disclosure is appropriate, 404 for inaccessible complaint IDs, 409 for concurrent-state/idempotency conflicts, 422 for invalid fields, 429 for throttling and 503 for unavailable inference dependencies. Errors include a stable code and request ID; retain diagnostic details only in authorized logs. Outbox insertion, decision/state change and audit event belong to one DB transaction.

## Proposed folders and migration strategy

```text
apps/web/src/app/(public)/{login,register,verify,reset}/
apps/web/src/app/(resident)/{dashboard,complaints,new,notifications,account}/
apps/web/src/app/(staff)/admin/{reviews,cases,assignments,models,audit}/
apps/web/src/{components,lib/api,lib/auth,schemas,styles}/
services/api/app/{main.py,config.py,db.py,dependencies.py}
services/api/app/modules/{auth,complaints,reviews,cases,notifications,models,audit}/
services/api/app/ml/{registry.py,inference.py,contracts.py}
services/api/app/jobs/{worker.py,outbox.py,deadlines.py,training.py}
services/api/{alembic/versions,tests/unit,tests/integration,tests/security}/
research/{configs,scripts,manifests,reports}/
docs/{architecture,api,operations,privacy}/
infra/{compose.yaml,proxy,backup,ci}/
```

This is a proposed structure, not a claim these directories contain a working application. Use Alembic numbered migrations reviewed in source control. Test empty-database upgrade, representative-data upgrade, rollback where safe, backup/restore, constraint failures and migration idempotency in CI against the supported PostgreSQL major. Never migrate production on arbitrary app import. Use expand/backfill/contract for incompatible schema changes and immutable audit retention. The SQLite prototype requires an explicit mapping and review; do not import its unverified demo labels as feedback.

## Pages, background work and interaction states

Resident pages: registration/login/verification/password reset, dashboard, new complaint with urgent-help prompt, receipt/reference, complaint detail and visible timeline, clarification response, notices/notifications, resolution feedback/reconsideration and account/security settings. Staff pages: review queue with urgent filters, narrative-version comparison, independent text-label and disposition controls, accepted-case dashboard, assignment/workload, due-date/overdue escalation, referral/actions, resolution verification/reopen, feedback-quality pool, model/training approval, audit search and permission management. Model metrics are research evidence; dashboard displays must not suggest calibrated confidence if unavailable.

Every page needs loading/empty/error/session-expired states, keyboard navigation, labeled fields, accessible validation, mobile layouts, confirmation for rejection/closure and conflict handling for stale records. Preserve typed drafts on recoverable errors without sending private text to analytics. Workers handle inference if queued, outbox notification delivery, retries with dead-letter escalation, overdue scans, scheduled quality-audit sampling, authorized retraining and artifact evaluation. Deadline expiration raises an event/alert and supervisor escalation; it cannot change a case to Resolved.

## Feedback and controlled retraining gates

1. Collect narrative-version-specific verified labels, reviewer identity, rubric and consent/authority basis; keep prediction and disposition separate.
2. Screen for sensitive data, label ambiguity, language quality, same/near duplicates, adversarial or poisoned feedback, representativeness and conflicting reviews. Adjudicate uncertain labels; keep exclusion reasons.
3. Approve training eligibility and create an immutable verified-feedback snapshot with hashes and grouped duplicate lineage. Exclude independent evaluation records and their relatives from fitting.
4. Periodically assess class/language balance, observed errors and review agreement. +100/+250/+500 are study checkpoints, not guaranteed minimum sample thresholds or automatic retraining triggers.
5. Administrator authorizes a queued run with a frozen configuration; consolidate approved research training data and eligible feedback without rewriting the historical corpus.
6. Refit the complete TF-IDF/SVM pipeline. Calibrate with group-separated training-only folds/held-out calibration examples. Keep development and independent evaluation distributions distinct.
7. Evaluate candidate versus the active model using predeclared Macro-F1, class-specific safety errors, subgroup support, probability reliability where relevant, latency and regression tests. Suggested acceptance: no material Macro-F1 loss, no unacceptable rise in Valid-as-Spam errors, adequate subgroup support and independently reviewed calibration for probabilities. The office/research protocol must set numerical tolerances before seeing prospective results; do not invent supported thresholds from ceiling synthetic scores.
8. An authorized approver reviews metrics, data lineage, exclusions and rollback readiness; rejected candidates remain archived. Activate an immutable version atomically, monitor, and roll back if agreed performance/safety triggers fire.

No feedback-driven improvement has been demonstrated by the current research rerun. The separately calibrated feature candidate was evaluated only on existing synthetic development data and is not approved for operational probability-based decisions.

## Phases and acceptance gates

Complexity estimates are relative (S/M/L/XL), not promised calendar dates. All phases depend on a participating office defining staff roles, service policies and privacy requirements. Scope is thesis-required unless explicitly marked later enhancement.

### Phase 1 - ML reproducibility and documentation (M)

Scope: immutable-corpus audit, original 18-config/3-fold run, fixed validation/test reproduction, separate grouped five-fold run, paired predictions, figures and research report. Dependencies: supplied CSV/archive, Python scientific environment and LaTeX. Tasks: checksum/partition verification, archive historical evidence, execute without changing settings, compare actual outputs, document version deviations, generate 360-DPI PNG/vector figures. Deliverables: scripts/configs/logs/metrics, figures, revised manuscript/PDF. Test: checksum and group assertions, paired-ID alignment, all 18 grid rows, numerical cross-checks, PDF compilation/render review. Complete when an examiner can rerun commands and obtain matching reported scores within stated precision. Risk: generator shortcuts and environment drift. Current status: experiments executed; see final changelog for artifact verification.

### Phase 2 - Backend and PostgreSQL (L)

Scope: API skeleton, schema, migrations, permissions, transactions, audit and outbox foundations. Depends on Phase 1 contracts and office policy. Tasks: implement normalized schema/services, deterministic development fixtures, OpenAPI contracts and CI. Deliverables: runnable local API/database, versioned migrations, ERD and error schema. Test: PostgreSQL constraints, concurrent acceptance, rejected-case prevention, empty/upgrade migrations, DB rollback. Complete when CI verifies schema and transactional histories and private endpoints require authorization. Risks: state conflation and migration data loss. Required; high-availability clustering is later.

### Phase 3 - Resident authentication and submission (L)

Scope: Next.js account flow, sessions, ownership, complaint form, reference, initial tracking. Depends on Phase 2. Tasks: registration/verification/reset, accessible forms, urgent prompt/flag, immutable narratives and idempotent submit. Deliverables: resident path with authorized retrieval and safe pending processing. Test: session/CSRF/IDOR, invalid/oversized/multilingual inputs, retry duplicates, mobile/keyboard and outage states. Complete when a resident can submit once, retrieve only their records and see pending/accepted/review status. Risks: account abuse and private-data leaks. Required; social login is later.

### Phase 4 - Saved SVM inference API (M)

Scope: registry-backed reference inference and class-based routing. Depends on Phases 1-3. Tasks: startup checksum/dependency checks, pipeline loading, prediction storage, acceptance transaction for Valid, review routing for others, safe failure path. Deliverables: versioned prediction service and provenance. Test: known inference records, wrong checksum/class order, missing model, inference timeout, duplicate job, no training-on-submit. Complete when every submission has one traceable prediction or recoverable pending task and routing matches policy. Risks: preprocessing mismatch and uncalibrated score claims. Required; candidate probabilities remain optional pending independent reliability evidence.

### Phase 5 - HITL staff dashboard (L)

Scope: Suspicious/Spam review, independent labels/dispositions, clarification and sampled Valid quality audit. Depends on Phases 2-4. Tasks: queue filters, original-version review, reasons, immutable decisions, narrative revision and alerts. Deliverables: review-to-accept/clarify/reject path. Test: acceptance of Suspicious without relabeling, no automatic Spam rejection, concurrent reviewers, clarified version lineage and authorization. Complete when all routes produce traceable independent decisions and resident notices. Risks: reviewer bias and accidental relabeling. Required; advanced reviewer assignment/active-learning ranking is later.

### Phase 6 - Complaint case management (L)

Scope: accepted cases only, assignments, Unresolved/Ongoing/Resolved, action histories, policy deadlines, overdue escalation, referral, verification and reconsideration/reopening. Depends on Phases 2-5. Tasks: staff/resident timeline, notifications, deadline policy configuration and supervisory controls. Deliverables: complete submission-to-reviewed-case-to-resolution path. Test: prevent cases for rejected/pending submissions; deadlines raise events without resolution; verify closure evidence, resident reconsideration and reopen history. Complete when an authorized officer can process a real workflow fixture and resident sees an accurate permitted timeline. Risks: undefined office policy, notification failures and mistaken closure. Required; analytics/SLA forecasting is later.

### Phase 7 - Feedback quality and controlled retraining (XL)

Scope: eligibility/adjudication pool, snapshots, offline jobs, candidate evaluation, approval, registry versions and rollback. Depends on Phases 1,4,5,6 and genuine approved labels. Tasks: implement the eight retraining gates, prevent test contamination and enforce separated permissions. Deliverables: auditable run lineage, comparison report and approval/rollback workflow. Test: rejected feedback, duplicates, mixed narrative versions, failed training, rejected candidate, artifact mismatch and rollback canary. Complete when an authorized end-to-end rehearsal proves lineage and release gates; improvement requires separately measured evidence. Risks: insufficient reviewed feedback, poisoning and biased selection. Governance and versioning required for the proposed HITL thesis; prospective gains and +100/+250/+500 trials are later if qualified data are unavailable.

### Phase 8 - Integration, security and deployment readiness (L)

Scope: end-to-end workflow validation, privacy/security, operational documentation and readiness assessment. Depends on Phases 2-7; basic security tests run throughout. Tasks: Playwright browser flows, API integration, load/failure testing, backups/restoration, access review, threat review, dependency checks and operator runbook. Deliverables: reproducible test report, deployment manifests, recovery/rollback instructions, limitations and user guide. Test: all routing/role/state paths, urgent handling during classifier failure, job retries, concurrency, accessibility and backup restoration. Complete when agreed tests pass, findings are resolved/accepted and office sign-off exists. Risks: deployment environment gaps and no operational validation. Required; actual hosting/deployment needs a separate authorized action and is not performed by writing this plan.

## MVP order and verification matrix

Build 1 -> 2 -> 3 -> 4 -> 5 -> 6 first so submission, staff processing and resident tracking work before advanced model maintenance. Then implement Phase 7's quality/approval workflow and Phase 8's final gates. Start unit/security/integration tests in each phase. Optional advanced calibration, monitoring analytics, active learning and prospective feedback checkpoints must not delay a working complaint path.

| Test layer | Core acceptance examples |
|---|---|
| Unit | text validation preserves negation; routing policy; independent label/disposition/status types; deadline calendar; permission predicates; registry manifest validation |
| Integration | PostgreSQL FK/state transactions; immutable narrative/review linkage; idempotency and outbox; session revocation; queued inference and model rollback |
| Browser E2E | register/login -> submit -> track; Suspicious -> clarify -> revised narrative -> accept; Spam review -> reject with reason; accept -> assign -> Ongoing -> verified Resolved -> reconsider/reopen |
| Security/privacy | cross-resident IDOR, role escalation, CSRF, XSS, injection, token reset replay, brute-force throttling, export access, no private-text logs |
| Operational | DB outage and retry, worker crash/reclaim, notification dead-letter handling, model load failure, backup restore, migration rehearsal and concurrency |
| ML | corpus/split hashes, no vocabulary leakage, group separation, per-record metrics/figures, candidate regression, real-probability calibration checks when approved |

The current `src/app.py` is not an implementation of these acceptance gates: it uses SQLite, lacks authentication, auto-closes Spam, uses softmax margins as confidence, conflates states, and its retrain endpoint fetches feedback without passing it to training. Preserve it as historical exploratory work; do not expose it publicly or cite it as validated HITL. Replace/migrate through the phased plan rather than treating the research metrics as proof that the app works.
