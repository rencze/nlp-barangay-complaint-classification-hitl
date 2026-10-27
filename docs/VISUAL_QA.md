# Final artifact verification

Completed 27 October 2026 (Asia/Manila), following the 26 October experiment run.

- Final Milestone 2 manuscript: 78 pages. Standalone evaluation report: 15 pages. The earlier 86/16-page delivery was superseded by the consolidated final revision. Both final files were compiled with pdfLaTeX through the reference-resolution pass. Final logs contain no undefined references, missing figures or overfull boxes.
- All final manuscript/report pages were rendered. Contact sheets and full-size result figures were inspected for clipped text, overlapping table headers, labels, counts, captions and numbering. Summary tables were reformatted vertically and comparison panels enlarged for print readability. Architecture/ER connectors were rerouted around text.
- Required final figure families exist as 360-DPI PNG and vector PDF/SVG under `results/figures/`. DPI metadata is approximately 359.994 due to PNG physical-resolution encoding, exceeding 300. Fourteen figure families (42 files) are supplied.
- Original process diagrams remain monochrome and evaluation charts retain meaningful color, explicit counts, differing markers/hatching and grayscale-readable labels. The source's fixed `[H]` placement keeps each figure directly after its explanation; page breaks occur where the complete image/caption cannot fit the remaining page.
- Programmatic checks recompute accuracy, Macro-F1, mistake counts and confusion matrices from saved predictions; verify pair IDs and truths; reload all four research model artifacts from a separate entry point; check negation/Unicode preservation; and verify the unchanged dataset checksum. See `results/verified_20261026/artifact_validation.json`.
- Original principal metrics, diagnostics and five-fold values match the supplied historical evidence at recorded precision/tolerance. Differences in dependency versions and evaluation scope are disclosed.
- The Overleaf ZIP was tested for archive integrity and compiled from a fresh extraction outside the authoring source directory. No external figure path or local user path is needed to compile it. Two LaTeX passes resolve references in a fresh Overleaf project.
- The local Poppler renderer emitted fallback-font notices for Symbol/ArialUnicode in supplied legacy artwork; no resulting missing content was apparent in the rendered-page inspection. Newly generated evaluation plots embed their vector fonts.

This is artifact/numerical verification, not a live-system test, independent annotation study or authentic-data generalization result. No GitHub publication or deployment occurred.

The final Milestone 2 audit adds the checked hardware/history distinction, original-research terminology, corrected Figure 6 and compliance appendix. The corrected package was extracted into a separate directory and its minimal example, read-only evidence audit and manuscript-preparation scripts ran successfully using a fresh pinned virtual environment. No full model training was repeated for this final audit. Public access is verified, but publication of corrected files remains pending authentication.
