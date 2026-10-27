# Pre-testing thesis revision — 26 October 2026

- Kept the original 24,000 synthetic records, original labels, assigned split column, recorded validation and test results and existing result figures.
- Added Chapter 3 pre-rerun experimental freeze, reproducibility checklist and single-corpus scope; noted this rerun will not provide new independent validation.
- Distinguished historical pipeline comparison (different word n-grams for NB versus SVM) from any proposed estimator-only common-feature experiment.
- Explicitly prohibited treating the previously evaluated synthetic test as a fresh held-out set for modified features.
- Preserved proposed HITL, word+character TF-IDF, calibration, retraining and accountability as unevaluated system functionality.
- Aligned Chapter 2 state terminology with Unresolved/Ongoing/Resolved and administrative events.
- Exported exact recorded train/validation/test membership CSVs (no new dataset or new split).
- Fixed EXPERIMENT_MANIFEST.json outdated script path and `test_reserved` ambiguity.
- Added read-only split/hash/group preflight and RUN_LOG_TEMPLATE.md for GitHub documentation.
- Kept historical numerical results; training was NOT rerun during this editorial revision.
