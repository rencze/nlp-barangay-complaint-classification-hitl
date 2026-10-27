# Barangay complaint classification — replacement research dataset V2

**Created October 26, 2026 | 24,000 controlled synthetic records | 118 generation categories**

## Files
- `data/ALL_SYNTHETIC_V2.csv`: 24,000 records; every row contains model input `complaint_text`, target `classification` and audit-only metadata.
- `data/TRAIN_SYNTHETIC_V2.csv`, `VALIDATION_SYNTHETIC_V2.csv`, `TEST_SYNTHETIC_V2.csv`: family-separated partitions (actual counts recorded in results, slight variance from 80/10/10).
- `references/CATEGORY_REGISTER.csv`: frozen 118-category taxonomy, 60 Valid / 28 Suspicious / 30 Spam.
- `references/SOURCE_TO_CATEGORY_EVIDENCE_MATRIX_V2.csv`: one row for each category, legal/policy and research basis *at varying levels of specificity*, with explicit remaining gaps.
- `references/SOURCE_REGISTER_V2.csv`: source citations and links.
- `src/content.py`, `src/generate_dataset.py`: researcher-authored multilingual incident micro-seeds and reproducible generation rules.
- `src/evaluate_models.py`, `src/evaluate_challenge.py`: reproducible model and stress experiments.
- `evaluation/heldout_challenge_96.csv`: 96 independently **researcher-drafted** (NOT authentic or expert-validated) style and boundary challenge records; evaluated once and should no longer be treated as blind for future changes.
- `evaluation/prior_48_reused_diagnostic.csv`: prior 48 stress probes. Their previous results have been inspected; NOT a blind test.

## Research statement and limits
The point of controlled synthetic data is to manipulate wording and scenario variables, inspect model feature gaps and support retraining experiments. It is NOT proof of representative authentic resident language or field-ready performance. Citations justify classes of issues and writing/robustness methods but do not make each artificial sentence an authentic report. All records are generated with a deterministic seeded rule-driven author-designed system and **have not been manually adjudicated by multiple researchers**. Repetition remains; high internal test accuracy must not be interpreted as generalization. The added 96-case challenge gives more honest resistance diagnostics. The dataset is *a research prototype* pending expert quality review, label adjudication and truly blinded out-of-generator evaluation.

**Classification rule:** Model features must use only `complaint_text`. Every other CSV column is audit/evaluation metadata and must not be passed to the vectorizer.

**Reproducibility:** From project root, with scikit-learn, numpy and matplotlib installed:

```
python src/generate_dataset.py
python src/evaluate_models.py
python src/evaluate_challenge.py
```

`generate_dataset.py` locates `references/CATEGORY_REGISTER.csv` in the delivered project. Generated random seed is 20261026; generating after changing Python/library versions may change splits or row ordering, so record environment versions and dataset checksums. The main experiment contains 18 candidates and 3 grouped CV folds. No true authentic barangay evaluation or live Human-in-the-Loop retraining was performed.

## 2026-10-26 pre-rerun correction
The three partition files named above are included in this package and were exported from `ALL_SYNTHETIC_V2.csv` using the existing `split` column, not re-generated. Verify with `python tools/verify_experiment_inputs.py`. The synthetic test was evaluated in the original saved experiment; it is not a fresh untouched test for development of revised features.
