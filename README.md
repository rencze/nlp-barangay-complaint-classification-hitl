# NLP-based barangay complaint classification with HITL planning

Reproducible research on a fixed 24,000-record **synthetic, human-unreviewed** corpus comparing TF-IDF/Linear SVM with TF-IDF/Multinomial Naive Bayes. Offline scores do not validate a live application, authentic resident language, HITL adaptation or complaint-resolution effectiveness.

## Final Milestone 2 audit

The public URL is accessible at the observed original commit `13dadbc3f82a11bce0383171624a78d4c3ccefc8`. Its older two-line README/demo source differs from this corrected local package. These corrections have not been pushed: noninteractive GitHub authentication was unavailable. See `docs/PUBLISH_CORRECTIONS.md` for exact ordinary-branch/commit/push commands. Do not treat local artifacts as already published.

The final audit checks established data/models/predictions without repeating full research training. Supporting deliverables are `docs/DATASET_INTEGRITY_REPORT.md`, `docs/MILESTONE2_COMPLIANCE_MATRIX.md`, `docs/EXPERIMENTAL_VERIFICATION_REPORT.md`, `docs/FULL_STACK_ALIGNMENT.md` and `docs/FINAL_AUDIT_CHANGELOG.md`. The overall remote-artifact requirement remains Partial until authenticated publication and a fresh public-checkout check.

## Deliverables

- `output/Thesis2_Verified_Overleaf.zip`: revised manuscript, compilable using `main.tex`.
- `output/pdf/Thesis2_Verified_Manuscript.pdf`: compiled manuscript.
- `output/pdf/ML_Evaluation_Report.pdf`: evaluation report with figures and academic tables.
- `results/figures/`: final figures, 360-DPI PNG plus vector PDF/SVG.
- `docs/FULL_STACK_ROADMAP.md`: Next.js/TypeScript, FastAPI, PostgreSQL plan and acceptance gates.
- `docs/diagrams/`: editable Mermaid/SVG and rendered architecture/database diagrams.
- `docs/RESEARCH_AUDIT.md`, `docs/CHANGELOG.md`: findings and verified/proposed/incomplete boundaries.
- `evidence/historical/`: preserved supplied results; `results/verified_20261026/`: new metrics, predictions, configs and manifests.

## Install

Use Python **3.13.5** for the recorded rerun. Create an isolated environment and install the executed scientific versions:

```powershell
python -m venv .venv-research
.venv-research\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On POSIX activate with `source .venv-research/bin/activate`. CPU execution is sufficient; GPU is not used. The supplied historical environment pinned different NumPy/SciPy/pandas versions. `results/verified_20261026/environment.json` records actual versions. This is numerical/procedural reproduction, not a bitwise original-environment claim.

## Minimal working example

```powershell
python src/minimal_example.py
```

This small demo prints narrative-to-label predictions and makes no study evaluation claim. Its demo preprocessing differs from the historical research pipeline. The older `python src/train.py --data examples/demo_complaints.csv --model-dir models/demo --results-dir results/demo` command is also executable, but its small random holdout is a demo score, not a thesis result.

For a read-only final evidence audit after installation:

```powershell
python src/final_evidence_audit.py
python src/validate_research_artifacts.py
```

The first checks all dataset fields/order, stored model configuration, predictions, metrics, paired statistics, assigned-language results and training-only IDF without fitting a model. Original study training commands below are optional reproduction commands, not necessary for this final documentation audit.

## Verify the exact dataset

```powershell
python src/verify_dataset.py
```

Input: `data/Barangay_Complaint_Dataset_24000.csv`. SHA-256: `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`. See `data/README.md` for schema/provenance. Checks stop on changed hash, split counts, labels, duplicate IDs or group overlap. Do not run generator scripts or introduce replacement data.

## Full recorded procedures

The supplied authoritative experiment source is retained under `manuscript/source/`. Historical results are archived separately. Copy a previous new-run output directory before rerunning if it must be retained; these commands refresh extracted-copy and dated rerun outputs, never the source corpus or historical evidence directory.

```powershell
python -u manuscript/source/reproducibility_scripts/evaluate_models.py
python -u manuscript/source/validation_suite/run_grouped_validation.py
python -u src/research_validation.py --mode all
python src/compare_models.py
python src/make_system_diagrams.py
python src/make_research_figures.py
python src/prepare_manuscript.py
```

First: original 18-config, three-fold scenario-grouped SVM grid, baseline, diagnostics and repeated synthetic-test evaluation. Second: separate five-fold training-only stability and validation diagnostics. Third: full-precision reference predictions/metrics and one separate word+character candidate, with and without training-group sigmoid calibration. Candidate evaluation uses development validation only; no candidate test metrics exist. Use `--mode audit` for checks or `--mode reference` to omit candidates. The test is **already inspected**, not a new independent test. The optional prior 48-message probe input is absent; no replacement challenge was fabricated.

Saved-reference evaluation without fitting:

```powershell
python src/evaluate_research.py --model svm --split validation
python src/evaluate_research.py --model nb --split test
```

Load only trusted local artifacts. Candidate serialization requires `src/research_features.py` on the Python module path (repository scripts provide that automatically). Models are research-only, not deployment-approved. Feed reference text raw to its saved TF-IDF vectorizer; do not apply demo normalization. Candidate settings: `candidate_config.json`; seed: 20261026.

## Figures and compilation

`python src/make_research_figures.py` recreates validation/test summaries, comparison, four confusion matrices, fold/aggregate CV with sample SD, all 18 tuning rows, actual-pair McNemar analysis, candidate/language results and learning/loss plots in `results/figures/`. Precision/recall summaries are macro-averaged. Hatching, labels and counts support grayscale reading. CSV is internal evidence and the original dataset format; final presentation uses figures/academic tables.

With a complete TeX Live or MiKTeX installation:

```powershell
cd manuscript/source
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cd ../../output/pdf
pdflatex -interaction=nonstopmode -halt-on-error evaluation_report.tex
pdflatex -interaction=nonstopmode -halt-on-error evaluation_report.tex
```

The manuscript preserves supplied citations and black-and-white process diagrams; experimental plots retain meaningful color. `src/prepare_manuscript.py` regenerates edited sections from preserved source baselines and executed evidence. Legacy archive update/generator scripts are historical utilities, not required commands.

## Findings and boundaries

SVM validation/test Macro-F1 = 1.000000 / 1.000000; baseline = 0.992077 / 0.991624. Five-fold mean = 1.000000 for SVM and 0.992452 for NB. Candidates tie the reference on synthetic validation; no classification improvement is established. No exact duplicates or cross-split scenario IDs were found, but lexical similarity and generation shortcuts limit generalization. Independent language/label review remains unperformed.

## Existing application prototype

Existing `src/app.py`, `src/static/`, `src/seed_db.py`, `src/run_experiments.py`, models and legacy outputs were preserved. The app uses SQLite and lacks target authentication/state/feedback safeguards. Softmax margins are not calibrated probabilities; auto-closing Spam conflicts with required review; its retrain route does not incorporate fetched feedback. It is not the planned Next.js/PostgreSQL system or deployment-ready HITL. No application deployment, GitHub push or release was performed.
