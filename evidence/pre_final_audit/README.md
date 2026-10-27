# Revised verified thesis project

Entry point: `main.tex`; engine: pdfLaTeX. Upload the ZIP contents into Overleaf and compile. This source is self-contained: all referenced figures and citations are included. The separately delivered PDF is `Thesis2_Verified_Manuscript.pdf`.

The unchanged corpus hash is `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`. Original 18-configuration grouped experiments and five-fold grouped validation were executed and reproduced. Chapter 4 distinguishes the repeated historical synthetic test from development validation and the separate combined-feature/calibrated candidate. No independent field or HITL validation is claimed.

Final result images in `figures/verified/` are vector PDFs generated from actual executed outputs. The accompanying full research project supplies 360-DPI PNG, vector PDF/SVG, scripts, exact dependencies, prediction evidence and logs. CSVs are internal evidence and dataset files, not the final evaluation presentation.

Original supplied result files/source baselines are preserved in the full project's `evidence/historical/`; files under this extracted project's results/validation folders reflect the rerun. The remaining older changelogs/manifests describe prior stages; the updated `EXPERIMENT_MANIFEST.json`, final chapters and full-project change log define current scope. Legacy generator/update utilities are not needed to compile and should not be run to reproduce the unchanged corpus.

Research-only candidate features/calibration were evaluated on the existing synthetic development set, tying the reference classifier. Operational probability reliability, resident authentication, administrator workflow, case management and feedback-driven retraining remain implementation/validation work.
