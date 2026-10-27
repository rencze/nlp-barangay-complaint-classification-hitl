# Manuscript Figure Style Audit (26 October 2026)

All **33** `\\includegraphics` references in the revised thesis were inspected. Nine colored *workflow or conceptual schematics* were replaced with black-and-white vector PDFs. The manuscript itself, its captions, cross-references, the 24,000-row dataset, recorded numerical results, and all quantitative figure assets were left unchanged.

## Nine diagrams converted to monochrome

- `figures/conceptual_framework.pdf` — Two-phase conceptual framework
- `figures/dataset_pipeline.pdf` — Synthetic data preparation workflow
- `figures/evaluation_design.pdf` — Leakage-aware evaluation procedure
- `figures/m3_fold_design_diagram.pdf` — Grouped-fold evaluation schematic (not a measured chart)
- `figures/diagram_framework.pdf` — Extended conceptual framework
- `figures/diagram_cv_workflow.pdf` — Model selection and validation protocol
- `figures/diagram_testing_map.pdf` — Experiment-to-evaluation map
- `figures/nlp_pipeline_readable.pdf` — Multilingual NLP diagram
- `figures/nlp_training_testing_readable.pdf` — Training and testing flow

## 8 already monochrome diagrams (unchanged)

- `figures/nlp_proposed.pdf`
- `figures/tfidf_proposed.pdf`
- `figures/svm_proposed.pdf`
- `figures/hitl_proposed.pdf`
- `figures/retrain_proposed.pdf`
- `figures/case_proposed.pdf`
- `figures/end_to_end_workflow.pdf`
- `figures/system_integration_final.pdf`

## 16 graphs or measured diagnostics (original color preserved)

- Result plots and learning curves (4)
- Model validation metrics, heatmaps, confusion matrices and diagnostic charts (9)
- Dataset composition and EDA plots (3)

**Verification:** The manuscript compiles successfully to 88 pages. Extracted visible text on all 88 pages is exactly identical to the previous integrated manuscript. Each revised diagram page contains only neutral black and white vector ink, with no colored pixels. All quantitative graph source assets are byte-for-byte unchanged.

**Regeneration:** Some original figure-generation Python files may recreate the former colored designs if rerun. Run `tools/apply_black_white_figures.py` after figure generation to restore monochrome diagram output. The included final diagram PDFs are already monochrome; users do not need to run the script to compile in Overleaf.
