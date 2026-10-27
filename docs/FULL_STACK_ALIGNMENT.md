# Full-stack alignment: existing code and remaining modules

27 October 2026. The selected stack remains Next.js/TypeScript, FastAPI/Python, PostgreSQL and saved scikit-learn TF-IDF/Linear SVM. Offline research artifacts are implemented and verified. The existing local `src/app.py`/static HTML/SQLite code is an exploratory prototype, not the validated selected-stack application. No deployment, operational HITL, user acceptance or feedback-driven improvement is demonstrated.

The complementary `FULL_STACK_ROADMAP.md` supplies full endpoint schemas, normalized tables, security strategy, eight development phases and release gates. This module inventory explicitly ties that plan to existing local implementation and missing functionality. A public clone at the observed original commit does not contain this prototype or the corrected study package; references below identify local evidence, not remotely published working services.

## Mandatory routing and data contracts

Resident submission -> saved NLP/TF-IDF/SVM pipeline -> Valid/Suspicious/Spam. Valid creates a policy-based Accepted disposition and an Unresolved case; Suspicious and Spam enter staff review. No automatic Spam rejection. Human-verified labels are version-specific and separate from dispositions (Accepted/Pending Clarification/Rejected) and case statuses (Unresolved/Ongoing/Resolved). Referred, Overdue and Reopened are events/flags. An accepted Suspicious original can remain labeled Suspicious; clarification creates a new independently labeled narrative version. Rejection is not automatically Spam feedback. Urgent safety handling is independent of classification.

## 1. Backend and PostgreSQL database — priority 1

- **Existing:** FastAPI exploratory app creates SQLite tables on import. No PostgreSQL migrations or normalized target schema are implemented.
- **Missing:** transactional services, permission/ownership enforcement, immutable narrative/review/decision records, migrations, state projections, append-only audit and outbox.
- **Dependencies/files:** `services/api/app/{main,config,db,dependencies}.py`, modules for complaints/reviews/cases/audit; SQLAlchemy 2, Alembic and psycopg 3; office policy definitions.
- **APIs/entities:** `/api/v1/complaints`, `/admin/reviews`, `/admin/cases`, health endpoints; users/roles/permissions, narratives, predictions, dispositions, accepted_cases, audit_events, outbox_jobs.
- **Validation/security:** FKs and same-complaint lineage, accepted-only case constraint, transaction locking/row versions, parameterized SQL, least-privilege DB access and protected migrations.
- **Acceptance:** empty/upgrade migration tests, rejected-case prevention, concurrent acceptance, rollback on error and audit/outbox consistency against real PostgreSQL. A running SQLite demo is insufficient.

## 2. Resident authentication and complaint submission — priority 2

- **Existing:** local unauthenticated submission route and static form; no Next.js account or object-ownership implementation.
- **Missing:** Next.js pages, registration/verification/login/reset, secure sessions, resident-only record retrieval, idempotent subject/narrative submission and urgency prompt.
- **Dependencies/files:** backend identity/complaint services; `apps/web/src/app/(public)/{login,register,verify,reset}` and resident new/detail pages; frontend/API contract generation.
- **APIs/entities:** auth register/login/logout/verify/reset, `/me`, POST/GET `/complaints`; users/sessions/complaints/narrative_versions.
- **Validation/security:** HttpOnly/Secure cookies, CSRF, throttling, Argon2id, strict lengths, Unicode/negation preservation, ownership checks and generic reset errors.
- **Acceptance:** observable register/login/submit/receipt path; no cross-resident access, replay duplication or client-selected role/state fields; mobile/keyboard/error-state tests. Only subject and narrative are required; no mandatory GPS/photos.

## 3. Saved SVM inference integration — priority 3

- **Existing:** research reference joblib files, saved vectorizers and independent reload/prediction tests. Local app loads another historical model with demo preprocessing, softmax margin scores and invented missing-model fallback confidence.
- **Missing:** approved read-only registry, checksum/dependency/preprocessor validation, version-specific inference persistence, class-based routing and safe pending/review handling on failure.
- **Dependencies/files:** `services/api/app/ml/{registry,inference,contracts}.py`, approved manifest, inference job and atomic accepted-case service.
- **APIs/entities:** trusted `/internal/predictions`; predictions/model_versions/narrative_versions/dispositions/cases; no resident-supplied artifact path.
- **Validation/security:** use the matching saved pipeline exactly; research reference receives raw text, candidate uses its own NFKC feature helper. Do not mix them. Never load untrusted pickle; no retraining on submit; probabilities null unless independently approved calibration supports them.
- **Acceptance:** canary classification, wrong-checksum/missing-model handling, actual version tracking and retries; Valid enters case path, other labels enter review. No fabricated fallback Valid or automatic rejection.

## 4. Administrator HITL review — priority 4

- **Existing:** exploratory list/detail/correction endpoints and static dashboard; mutable `final_label` and no authenticated role separation. These do not implement the agreed governance model.
- **Missing:** authorized queue, original-version inspection, independent verified-label and disposition fields, reasoned decisions, versioned clarification and sampled Valid quality audits.
- **Dependencies/files:** review service and `apps/web/src/app/(staff)/admin/reviews`; explicit rubric/roles, narrative comparison component.
- **APIs/entities:** review queue, POST `/admin/reviews`, `/admin/clarifications`, resident clarification responses; administrator_reviews/verified_labels/dispositions/clarification_requests/responses.
- **Validation/security:** permission and object scopes, immutable attribution/reasons, stale-review conflict handling, no assumption acceptance implies Valid or rejection implies Spam.
- **Acceptance:** Suspicious accepted without relabeling, Spam accepted/clarified/rejected by a human, new narrative independently reviewed, concurrent-review conflict logged. No operational annotation agreement claim without reviewer evidence.

## 5. Accepted-case tracking — priority 5

- **Existing:** prototype has Pending/In Progress/Resolved/Closed mutable states, which differ from the required accepted-case model.
- **Missing:** accepted-only cases, assignments, Unresolved/Ongoing/Resolved transitions, action/referral histories, policy due dates, overdue escalation, verified resolution and reconsideration/reopening.
- **Dependencies/files:** case module, deadline-policy service, staff case/assignment pages and resident timeline.
- **APIs/entities:** `/admin/cases`, assignments/actions/status-transitions/reopen; accepted_cases/case_assignments/case_actions/status_transitions/deadline_policies.
- **Validation/security:** assigned-officer/supervisor permissions, concurrency versions, verified resolution with reasons; no universal legal resolution interval hardcoded.
- **Acceptance:** no case for a rejected/pending submission; overdue emits alert/event but never resolves; referral/reopen history preserved; resident reconsideration traceable.

## 6. Resident notices and status history — priority 5 (with case path)

- **Existing:** prototype detail/audit display is exploratory; no verified resident visibility boundaries, notification outbox or retry pipeline.
- **Missing:** role-filtered timeline/notices, clarification/status/resolution notifications, delivery/read states, outbox retries and dead-letter escalation.
- **Dependencies/files:** notifications module, `jobs/outbox.py`, resident notifications/detail pages; case/review events.
- **APIs/entities:** own `/notifications`, mark-read, own complaint history; notifications/outbox_jobs/audit_events/case_actions.
- **Validation/security:** ownership filters; minimal external message content; no private narrative in routine email/log payload; idempotent dedup keys.
- **Acceptance:** case update produces one notification, retried delivery does not duplicate, failure escalates, staff-only notes stay private. Do not claim external messages were sent during planning.

## 7. Quality-checked feedback management — priority 6

- **Existing:** correction route stores a mutable label; there is no adjudicated, eligible, consent/authority-tracked feedback pool.
- **Missing:** version-specific review/adjudication, privacy/label quality screening, duplicate/conflict lineage, eligibility/exclusion reasons and immutable snapshots.
- **Dependencies/files:** feedback-quality service and staff pool page; rubric and sampling policy, controlled export/snapshot jobs.
- **APIs/entities:** authorized feedback eligibility/snapshot endpoints under `/admin/feedback`; verified_labels/feedback_examples/training_run_examples.
- **Validation/security:** no automatic training label from disposition; exclude test families/duplicates; reviewers see relevant authorized text, poison/ambiguity flags require adjudication.
- **Acceptance:** rejected/nonreviewed/conflicting records stay ineligible; original and clarified versions remain distinct; sampled Valid audits reduce review-selection blind spots without routine review of every Valid prediction.

## 8. Controlled retraining and model versioning — priority 7

- **Existing:** research scripts/artifacts; prototype retrain endpoint fetches feedback but never passes it into its invoked experiment script. Its success message is not evidence of feedback learning.
- **Missing:** authorized snapshots/jobs, actual eligible-feedback consolidation, grouped candidate evaluation/calibration, independent approval/rejection, immutable registry and rollback.
- **Dependencies/files:** `jobs/training.py`, registry/model services and staff model/training approval pages; adequate reviewed labels and a predeclared evaluation protocol.
- **APIs/entities:** `/admin/training-runs`, `/admin/models`, approve/activate/rollback; training_runs/training_run_examples/model_versions/model_approvals/audit_events.
- **Validation/security:** separate authorization/approval permissions, no HTTP blocking training, no train-on-submit, trusted artifacts, frozen input/config hashes and rollback canaries.
- **Acceptance:** rejected candidate cannot activate; failed run leaves live version untouched; rollback and lineage tested. +100/+250/+500 are experimental checkpoints, not automatic thresholds. No actual feedback-driven improvement is established.

## 9. Integration testing and deployment readiness — priority 8

- **Existing:** research/numerical checks, minimal-example execution, compiled/rendered manuscript and editable design artifacts. No selected-stack integration, security, latency, user acceptance or live-office test report exists.
- **Missing:** API/PostgreSQL integration, browser E2E, role/state/privacy/urgency tests, migration/backup restoration, load/failure tests, operations runbook and deployment review.
- **Dependencies/files:** API unit/integration/security suites; web Playwright tests; `infra` compose/proxy/backup/CI; office-approved access/deadline/retention policies.
- **APIs/entities:** all module boundaries, health/readiness, outbox/state/audit/registry relations and recovery paths.
- **Validation/security:** IDOR, CSRF, XSS/injection, brute force, token replay, model/DB outages, staff MFA, secret/dependency checks and restrained logs.
- **Acceptance:** complete resident submission -> classification/review -> accepted case -> verified resolution/reconsideration path passes; urgency survives classifier failure; backup/rollback restoration demonstrated. Actual deployment requires a separately executed, authorized action and is not implied by this plan.

MVP sequence: database/access foundation -> resident submission -> saved reference inference -> review -> cases plus notices -> feedback quality -> governed retraining -> final readiness. Begin security/integration tests with each module rather than leaving them until the end. Preserve the text-only thesis scope; advanced probability thresholds, active-learning ranking, maps, photographic/multimodal processing and predictive analytics are optional later work, not mandatory additions.
