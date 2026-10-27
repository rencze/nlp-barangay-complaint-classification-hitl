# Research and implementation change log

26 October 2026. All work is local. No GitHub push/release or application deployment occurred.

Final compilation, artifact consistency checks and packaging continued into 27 October 2026 (Asia/Manila). The experiment directory retains its original 20261026 run identifier.

## Preserved

- Original 24,000-row CSV, labels, stored partitions and SHA-256 remain unchanged.
- Supplied Overleaf ZIP and PDF remain unchanged in their supplied location. The extracted source is the editing copy.
- Original supplied metrics/validation evidence is under `evidence/historical/`; source baselines for edited chapters are preserved there as well.
- Existing untracked web/generator/seed code, existing model artifacts and unrelated legacy top-level results were not overwritten.
- Thesis title, authors, chapter organization, research citations and meaningful process diagrams were retained.

## Executed and verified

- Audited source/schema/provenance, partitions, labels/languages, unique IDs, exact/normalized duplicates, scenario/template separation and lexical similarity.
- Executed archived original three-fold grouped grid over 18 SVM configurations, original NB pipeline, validation and repeated historical-test evaluation, learning-size and separate auxiliary SGD diagnostics.
- Executed archived training-only five-fold grouped stability and validation diagnostics; principal recorded metrics match at original precision. Full comparison and environment JSON record limitations and library changes.
- Saved actual reference per-record predictions and recomputed exact/continuity-corrected McNemar comparisons by aligned record IDs.
- Tested one word+character candidate, with and without three-group-fold sigmoid calibration, using only development validation. Both tie the word reference; no classification improvement is shown. Operational probability reliability is not established.
- Saved versioned research-only model artifacts, candidate config and full-precision metrics; independently checked artifact reload/inference from another entry point.
- Ran the README minimal demo in separate demo folders. Demo scores are not thesis research findings.

## Presentation and manuscript changes

- Added reproducible 360-DPI PNG and vector PDF/SVG figures under `results/figures/`: required validation/test summaries, model comparison, four actual-count confusion matrices, grouped CV/fold SD, all tuning configurations and paired statistics; additional candidate, language and learning/loss figures.
- Replaced redundant Chapter 4 sections with a coherent evidence sequence, actual reproduced metrics, image-based result presentation, per-class academic tables, paired statistics, candidate findings and explicit limitations.
- Expanded Chapter 3 with executed environment, exact raw-reference preprocessing, separate combined-feature/calibration protocol, precision/recall averaging and paired-test conventions. Historical workstation specifications remain attributed, not re-measured.
- Updated abstract and Chapter 5 to acknowledge successful reproduction and the candidate tie while retaining operational/external-validation boundaries.
- Preserved black-and-white process diagrams; replaced the software integration image with the updated editable architecture instead of adding a duplicate integration figure. Added a complementary database overview.
- Generated and compiled the standalone evaluation report using the same actual result figures and tables. CSVs are internal evidence, never the final presentation format.
- Compiled final manuscript/report with resolved numbering/references and reviewed rendered pages. `artifact_validation.json` records programmatic consistency checks; visual-QA notes document rendering.

## Reproducibility and planning changes

- Replaced incomplete README/data instructions with real schema/provenance, exact dependency pins, relative-path commands, minimal/full workflows, artifact locations and scope limits.
- Added dataset verification, saved-model evaluation, paired comparison, figure generation, manuscript preparation and artifact-validation scripts; retained original procedures for provenance.
- Added normalized data design, editable integration/ER diagram sources and detailed eight-phase full-stack roadmap with schema/API contracts, ownership/RBAC, urgent handling, case transitions, quality gates, deployment/rollback and acceptance tests.
- Identified existing prototype defects without claiming they were fixed: unauthenticated routes, SQLite/static UI, Spam auto-close, uncalibrated/fallback confidence, state conflation and non-incorporated feedback in retraining.

## Proposed or incomplete

- Next.js/FastAPI/PostgreSQL application, resident authentication, staff authorization, production inference/routing, HITL dashboard, accepted-case management, notification/deadline workflows and operational security tests are planned, not implemented by this work.
- Independent human label/language review, authentic external testing, operational calibration validation, prospective Valid audits and real feedback-driven retraining have not been demonstrated.
- +100/+250/+500 feedback points are optional research checkpoints, not minimum thresholds or proven gains.
- The missing prior probe/challenge inputs were not regenerated; their historical metrics were not represented as reproduced results.
- Public repository availability, dataset redistribution rights and institutional deployment sign-off remain outside the completed local-artifact work.

## Publication preparation — 27 October 2026

- Verified all 364 file entries in `output/GitHub_Ready_Research_Project.zip` against the working tree before publication preparation; no entries were missing or different, and no Git metadata was included.
- Prepared `research/milestone2-final-audit` using the explicit research-file allowlist; unrelated untracked prototype/generator/seed files remain excluded.
- Added `.gitattributes` to preserve research CSV bytes across Git checkouts. The staged canonical dataset retains SHA-256 `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`.
- Installed pinned requirements in the isolated `.venv-research` environment. The existing `.venv` had different/missing dependencies and was preserved.
- Staged whitespace checks report existing generated SVG/log whitespace; these evidence files were preserved without content cleanup.
- Authenticated dry-run push could not obtain GitHub credentials. Publication, pull request, anonymous verification and the dated published-commit record remain pending; remote-artifact completeness remains Partial.
- All three lightweight commands passed in `.venv-research`: `minimal_example.py`, `final_evidence_audit.py` and `validate_research_artifacts.py`; `pip check` passed. No full study training was run.
