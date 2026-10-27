# Experimental Verification Report

Read-only final audit, 27 October 2026. **No full-study training, search, calibration or retraining was repeated in this final audit.** The earlier verification executions remain documented in preserved logs. Tiny demo fitting is solely an executable-example check, not a new research experiment.

The original 24,000-record corpus and stored partitions are unchanged. Saved research models were reloaded and their predictions matched existing exports record by record. Metrics below are recomputed from those actual predictions and match saved full-precision evidence within 1e-12. They describe the original synthetic benchmark, not new independent data.

| Pipeline | Partition | N | Accuracy | Macro-precision | Macro-recall | Macro-F1 | Weighted-F1 | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Linear SVM | validation | 2399 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0 |
| Linear SVM | test | 2388 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0 |
| Naive Bayes | validation | 2399 | 0.992080 | 0.992267 | 0.992073 | 0.992077 | 0.992079 | 19 |
| Naive Bayes | test | 2388 | 0.991625 | 0.991780 | 0.991677 | 0.991624 | 0.991624 | 20 |

All four confusion matrices use row/reference and column/prediction order Valid, Suspicious, Spam. The matrices are retained as publication figures with actual counts and per-class academic tables in Chapter 4 and the evaluation report. Baseline errors are Spam predicted as Suspicious; no Valid-as-Spam error occurs in these stored reference evaluations. All assigned-language supports and Macro-F1 values were also checked directly against record-level predictions.

| Partition | Both correct (a) | Baseline only (b) | SVM only (c) | Both wrong (d) | Corrected chi-square | Exact two-sided p |
|---|---:|---:|---:|---:|---:|---:|
| validation | 2380 | 0 | 19 | 0 | 17.052632 | 3.81469726562e-06 |
| test | 2368 | 0 | 20 | 0 | 18.050000 | 1.90734863281e-06 |

The exact test uses Binomial(b+c,0.5); the nonnegative continuity-corrected statistic is max(0,|b-c|-1)^2/(b+c). Nominal p<.05 favors SVM on this benchmark; shared generated families constrain independent-pair interpretation and field inference. These pipelines use different n-grams, so estimator-only superiority is not isolated.

The original GridSearchCV has 18 combinations: C=.1/1/10, n-grams=(1,1)/(1,2), min_df=2/5/10, fixed max_df=.95 and sublinear_tf=True, seed20261026, three grouped folds. All saved grid scores are 1.0. Separate five-fold training-only stability has mean/SD 1.000000/0 for SVM and .992452/.000971 for NB; historical output comparisons already corroborate these values. Neither this final audit nor figure generation repeats those fits. Reference vocabulary/IDF matches the 19,213 training document frequencies, and feature metadata are excluded by the source paths.

The fixed word+character candidate and its grouped-sigmoid variant remain separate development evaluations: both have validation Macro-F1 1.0, tying the reference. There are no candidate test predictions. Probability diagnostics on the synthetic development distribution do not establish independent operational reliability. Reference model loading is tested research code; authenticated live service integration remains planned.

Final presentation: all 14 evaluation figure families exist as 360-DPI PNG plus PDF/SVG in `results/figures/`. The original dataset is CSV; prediction/CV CSV and JSON are internal evidence, not final presentation. The image-based `ML_Evaluation_Report.pdf` and Chapter 4 provide the academic presentation. Source: `src/final_evidence_audit.py`, `experimental_verification.json`, historical output archive and `reproduction_comparison.json`.
