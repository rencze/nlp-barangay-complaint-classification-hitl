# Updated Manuscript Change Summary — 26 October 2026

- Retained the original title, author information, 24,000-row CSV, all recorded SVM / NB results, validation partitions, generator code, figures for past experiments, and reproducibility artifacts.
- Integrated proposed end-to-end NLP, word+character TF-IDF, SVM calibration, HITL class routing, label-quality checking / controlled retraining, accepted-only case management and whole-system architectural diagrams.
- Removed duplicate outdated NLP/TF-IDF/lifecycle flow images within literature/methodology while retaining distinct experimental figures.
- Added the complete nine-case labeling/administrative outcomes policy and separated narrative version label, model prediction, review disposition, fact verification and administrative status.
- Added resident Subject/Narrative as the core intake; date/time and Purok/Sitio/landmark as when-known context; maps/GPS/image classification deferred.
- Added action logging, configurable response deadlines, overdue/escalation/referral events, completion review and resident reconsideration for accepted cases; no automatic resolution claim.
- Documented controlled retraining using existing training data + eligible verified examples and proposed cumulative checkpoints of +100/+250/+500, with separate candidate-fit and deployment authorization steps and no uncontrolled looping.
- Updated citations to verified prior research and public rules, and qualified all unimplemented functions as proposed rather than completed.
- Manuscript passes pdfLaTeX with stable references; figure numbers appear only in captions, not inside the generated vector figures.

## Integrated workflow and figure placement revision
- Added `figures/end_to_end_workflow.pdf` and its editable SVG source, with reproducible authoring code at `diagram_sources/draw_integrated_workflow.py`.
- Retained a separate `figures/system_integration_final.pdf` software-component architecture diagram; the integrated process figure and integration architecture are separately explained to avoid redundant detail.
- Replaced all thesis chapter `figure` placements using `[p]` (and other floating layouts if present) with `[H]` to keep each figure immediately after its section-specific description in the compiled reading order. Figures too tall to fit after their descriptions are moved as complete figures to the following page rather than floated past subsequent content.
- Split the paired conceptual-framework and validation figures with their own explanatory paragraph and caption in the experimental methodology.
- Validated compilation with pdfLaTeX (88 pages) and inspected the integrated workflow and diagram placement in rendered PDF pages.
