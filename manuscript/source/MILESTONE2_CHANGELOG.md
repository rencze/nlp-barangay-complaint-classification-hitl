# Milestone 2 integration and manuscript consolidation

Source: user-supplied `Thesis_Milestone-2 (2).pdf`, retained research data/results, and previous black-white Overleaf manuscript.

## Requirement mapping
- Hardware/software: Chapter 3 Milestone 2 subsection and Table `m2env`; machine specification is reported from the attached milestone.
- Repository and reproducibility: Chapter 3; GitHub URL access could not be verified; working code smoke script and requirements added.
- Baseline: TF-IDF + MultinomialNB(alpha=1.0), same partitions as LinearSVC.
- Metrics: accuracy, precision, recall, per-class F1, Macro-F1 and Weighted-F1 equations; confusion matrices.
- Hyperparameters: actual 18-setting three-fold group grid; independent five-fold group stability experiment; supersedes earlier proposed stratified 80/20 and five-fold tuning.
- Statistical comparison: McNemar exact two-sided test. Recorded common synthetic test set yields b=0/c=20 and exact p=1.90734863e-6. These are derived from previously saved test summaries, not a new fitted model.

## Clutter reduction
- Removed redundant conceptual framework, old broad NLP and training pipeline, validation schematics, repeated class/language charts, duplicate hyperparameter chart, fold sizes and extra SGD F1 figure; original source files remain accessible.
- One new unified validation figure shows 24,000 = 19,213 training + 2,399 validation + 2,388 synthetic test.
- Original graph results preserved, except redundant duplicate visuals removed from main text.

## Status notes
Proposed combined word-character TF-IDF, SVM calibration, HITL/feedback retraining and live case management are not reported as completed work.
A synthetic test that has already been evaluated cannot be called untouched for new revisions.

## Reference manuscript reconciliation
- Reviewed the 88-page reference `Manuscript.pdf` (uploaded October 26, 2026); reconciled historical “reserved test” language with saved original test results.
- Abstract now reports both development validation and previously evaluated synthetic test Macro-F1 scores.
- Renamed the milestone-specific Chapter 3 heading to a formal methodology title.
