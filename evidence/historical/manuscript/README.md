# Barangay Complaint Classification Thesis — Updated Overleaf Project

**Updated:** 26 October 2026.  **Entry point:** `main.tex`.

## Build on Overleaf
Upload the ZIP contents as a new Overleaf project, set `main.tex` as the main file, select `pdfLaTeX`, and compile. The compiled manuscript is also provided separately as `Thesis2_Milestone2_Reconciled_Manuscript.pdf`.

## Study evidence retained unchanged
- `data/ALL_SYNTHETIC_V2.csv` — 24,000 records; SHA-256 `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`, byte-identical to the new 24,000-row CSV attachment.
- Existing reproducibility scripts, experimental results, CV fold logs, confusion matrices, source evidence records, and original model results were preserved.
- Word-level TF-IDF + Linear SVM validation is a **completed synthetic-data experiment**; combined word/character TF-IDF, probability calibration, deployed HITL, controlled batch retraining, and administrative case management are **proposed extensions** that are not claimed as evaluated.

## Revised sections
- Chapter 1: clarified research versus implementation scope and revised overconfident background statements.
- Chapter 2: grounded claims using traceable citations and aligned theory with the current results and proposed governance design.
- Chapter 3: added seven figure-number-free standalone workflow assets (numbering appears in LaTeX captions only), explicit interfaces, validated/untested boundaries, nine-labeling-case decision matrix, proposed authorized retraining checkpoints, and accountable case management.
- Conclusions: documented outstanding validation needs, potential false-Spam risks, non-guaranteed improvements, and deferred images/GPS/multimodal analysis.
- References: added sources from the attached consolidated evidence review and verified Philippine response/process rules.

## Seven new clean vector workflow figures
- `figures/nlp_proposed.pdf`
- `figures/tfidf_proposed.pdf`
- `figures/svm_proposed.pdf`
- `figures/hitl_proposed.pdf`
- `figures/retrain_proposed.pdf`
- `figures/case_proposed.pdf`
- `figures/integrated_proposed.pdf`

Editable Graphviz (`.dot`) sources and a local regeneration script `make_workflow_figures.py` are also included. The figures contain no fixed figure numbers; changing the figure order will not require image edits. The figures are vector PDFs for zooming or high-quality printing. The packaged project does not depend on Graphviz to compile because rendered vector PDFs are included.

## Important research caveats
1. This manuscript's synthetic corpus is not verified natural resident complaints; all rows have `human_label_reviewed=No`, and recorded language labels have `language_verified=No`.
2. The recorded SVM's Macro-F1 of 1.0000 on the synthetic validation dataset is **not** an external generalization claim.
3. The recorded chosen SVM uses word unigrams. A character-only ablation exists, but a concatenated word/character TF-IDF feature set has not been verified as the final trained model.
4. Class-probability calibration, queue threshold policy, HITL, 100/250/500 verified-feedback retraining comparisons, and case management are **proposed and subject to validation**.
5. No figure or prose asserts that a legally sufficient complaint is factually true merely because it is labeled Valid; accepting/rejecting a submission and the case's Unresolved/Ongoing/Resolved state are distinct from the text label.
6. Image attachments, computer vision, ensembles, and compulsory map/GPS capture are explicitly out of scope for this version.
7. Deadline tracking is policy-configurable, not a universal timeline for resolving an incident.

See `research_evidence/Consolidated_Research_Review_User_Supplied.pdf` for the original supplied evidence review. Current government/academic sources relevant to the revision also appear in `references.tex`.


## Figure placement and integrated diagrams (October 2026 revision)
- All figure environments in the thesis chapters now use `[H]` so they occur immediately after their explanatory paragraphs instead of floating ahead or into a different section. When a tall diagram cannot fit after a paragraph, LaTeX moves the entire diagram to the next page without allowing later content to overtake it.
- `figures/end_to_end_workflow.pdf` is the new integrated process diagram and has editable SVG source `figures/end_to_end_workflow.svg`, plus `diagram_sources/draw_integrated_workflow.py` for regeneration.
- `figures/system_integration_final.pdf` separately shows proposed software components and information stores; both figures are distinct from the detailed NLP/TF-IDF/SVM/HITL/retraining/case diagrams.
- Figure identifiers and numbers are printed as LaTeX captions, not inside the diagrams.

## Milestone 2 revision (October 26, 2026)
- The supplied Milestone 2 PDF has been reconciled with recorded grouped 19,213 / 2,399 / 2,388 partitions; previous planned 80/20 and five-fold hyperparameter-tuning claims are not reproduced as performed.
- `requirements.txt` and `examples/minimal_pipeline.py` are included as an executable small smoke example. It is **not** the full recorded experiment and does not generate thesis findings.
- `chapters/methodology.tex` includes the reported hardware/software, baseline, metric equations, true grid, reproducibility caveats, and paired McNemar test.
- `chapters/model_validation_diagnostics.tex` reports the previously recorded 2,388-test scores and derived exact McNemar p-value; no new experiment is claimed.
- The earlier Milestone 2 GitHub address (`https://github.com/rencze/nlp-barangay-complaint-classification-hitl`) could not be publicly verified (HTTP 404); confirm access and provide a working repository and commit before official submission.
- Redundant framework, NLP, evaluation, subgroup and diagnostics illustrations were removed from the main narrative; source images and experiment files remain in the project.

To run the bundled smoke demonstration:
```bash
python -m venv .venv
# Activate environment on your OS
pip install -r requirements.txt
python examples/minimal_pipeline.py
```
For research reproduction follow the saved scripts and EXPERIMENT_MANIFEST.json; do not treat the smoke example as a substitute for the full dataset experiments.

## Reference manuscript reconciliation (October 26, 2026)
The supplied 88-page `Manuscript.pdf` was used as the initial reference. Its supplementary validation chapter correctly excludes the 2,388-case synthetic test from the *later five-fold study* but should not call this split wholly untested: the original saved `model_results_v2.json` already evaluated it. The updated PDF reports the saved test values separately, keeps its previous evaluation history explicit, and prohibits reusing it to choose new model features or thresholds.

The Milestone 2 requirements are integrated into Chapter 3 as a normal experimental methodology section, with the submitted milestone itself stored under `research_evidence/`.


## Pre-testing manuscript revision: reproducible experiment on the original corpus

The supplied research data remain **one unchanged 24,000-record synthetic dataset**. It is exported without new generation into the recorded family-disjoint **train (19,213)**, **validation (2,399)** and **previously evaluated synthetic test (2,388)** partitions. A `test` record is **not** training data; the full 24,000 rows define the experiment, and only training rows fit the models. This project does not require obtaining a second dataset to rerun the existing experiment.

```bash
python -m venv .venv
# activate the virtual environment for your platform
python -m pip install -r requirements.txt
python tools/verify_experiment_inputs.py
python examples/minimal_pipeline.py               # smoke test only; NOT thesis results
python reproducibility_scripts/evaluate_models.py  # complete recorded baseline and SVM suite
python validation_suite/run_grouped_validation.py  # additional 5-fold training-only audit
```

**Before running the full scripts**, commit or back up `results/`, `figures/` and `validation_suite/` outputs, because the scripts may overwrite saved results. Compare newly generated metrics to the historical results; log changes in `RUN_LOG_TEMPLATE.md` rather than silently changing the manuscript. Include the commit SHA, corpus SHA-256, OS/Python versions, exact installed packages (`python -m pip freeze`) and run commands in your public/private GitHub repository. The previously viewed test set must not be reused as a supposedly unseen basis for choosing new settings. No full website or HITL deployment is necessary to demonstrate the recorded offline model evaluation.

**Comparison caveat:** the original Naive Bayes and SVM pipelines differ in word n-gram configuration. Scores in the current thesis describe those exact historical pipelines. Any next matched-feature estimator experiment or combined word+character experiment must be separately identified and must select configurations using the existing training folds/development validation only; the existing data partitions may be reused for reproducibility, but no new generalization claim follows from doing so.

`EXPERIMENT_MANIFEST.json` has been corrected to reference the actually packaged `validation_suite/run_grouped_validation.py`, and the split CSV files missing from the prior ZIP are now included.
