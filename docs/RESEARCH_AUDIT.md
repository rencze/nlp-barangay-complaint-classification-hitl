# Research and implementation audit

Audit date: 26 October 2026. Scope: all repository source files, existing outputs/configuration and the supplied Overleaf project, before execution of the archived research experiments. File inventory and hashes: `results/verified_20261026/pre_supplement_inventory.csv`. The repository initially contained untracked dataset, generator, web, seed and experiment files; these were preserved. No source dataset was regenerated, relabeled or replaced.

## Authoritative evidence and reproduction

The local `data/Barangay_Complaint_Dataset_24000.csv` has SHA-256 `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`, identical to the supplied archive's `ALL_SYNTHETIC_V2.csv`. Its partition rows and order match all three archived split files. The schema is `complaint_text` / `classification`, with `split` and `scenario_family_id` as audit/control fields. The original repository trainers expect `text` / `label`, so they are demo scripts, not reproduction entry points for this corpus.

The supplied ZIP remains unchanged. Original result and validation files were extracted to `evidence/historical/` before their copies were rerun under `manuscript/source/`. Thus historical evidence and newly executed results remain distinct. Original procedures were executed first: `reproducibility_scripts/evaluate_models.py`, then the independent `validation_suite/run_grouped_validation.py`. The historical model/feature/search settings were retained. Library differences are captured in `environment.json`: Python 3.13.5 and scikit-learn 1.8.0 match the manifest, but NumPy 2.4.4, SciPy 1.17.1 and pandas 3.0.2 differ from the submitted record. This is procedural/numerical reproduction, not a bitwise recreation of the original environment. Result comparisons are machine-generated in `reproduction_comparison.json`.

The original script's optional prior 48-message probe path is absent. It therefore reports no newly verified probe results. The archive has an older 96-message challenge metric file without the corresponding challenge dataset in its listed inputs; this is historical evidence only, not an independently rerun experiment. No replacement probes were invented.

## Data integrity and bias

- 24,000 records, 8,000 per class; 6,000 per assigned language group. Train/validation/test: 19,213/2,399/2,388.
- Unique record IDs; no empty required texts/groups; zero raw or NFKC/casefold/whitespace-normalized duplicate excess. Zero scenario-family overlap, template-family overlap and normalized-text overlap across the stored partitions.
- All records are synthetic researcher-constructed and unreviewed, with `language_verified=No` and `human_label_reviewed=No`. No independent linguistic or label reliability study was performed.
- Group IDs partition generation families but cannot establish independent wording or root meaning. A training-fitted reference unigram vectorizer gives nearest-training cosine >=0.90 for about 57.5% of validation and 58.0% of test narratives. Similarity is descriptive, not a rule for deleting or changing records.
- Original-script length-only logistic regression and exploratory character-only diagnostics were rerun. Their above-chance/ceiling performance and the tied grid are evidence of generator-related shortcuts, not grounds to lower scores artificially.
- Metadata such as category, label_rule, language and family ID never enters classifier features. TF-IDF is fitted only within training folds or the fixed training partition.

## Pipeline and code discrepancies

| Finding | Evidence / implication | Resolution |
|---|---|---|
| README has no runnable study instructions | Initial README was two lines | Added installation, demo/full commands, evidence boundaries and outputs |
| `data/README.md` describes an empty real-data folder | Actual corpus is synthetic, with a different schema | Replaced with verified corpus dictionary, provenance and checksum |
| Repository `run_experiments.py` differs from Chapter 3 | 80/20 row split, 192 configs, five-fold non-grouped search; default missing synthetic CSV | Preserved as legacy exploratory code; use archived 18-config grouped procedure for historical reproduction |
| Demo preprocess differs from historical reference | Demo lowercases/removes URL/punctuation and non-ASCII; archived vectorizer uses raw narrative/default tokenization | Preserve both histories; describe historical pipeline accurately and save candidate normalization inside its pipeline |
| Baseline and SVM feature ranges differ | NB uses word (1,2), selected SVM uses (1,1) | Interpret as whole-pipeline comparison, not isolated estimator superiority |
| Existing outputs may represent unrelated demo/legacy run | Top-level `results/experiment_results.json` and `models/` predate the supplied study | Leave untouched; new outputs under dated directory |
| Legacy loss curve is not final SVM loss and uses held-out test as validation | Repository SGD log-loss trace is a separate estimator | Manuscript uses the archived auxiliary SGD hinge diagnostic, correctly labeled |
| Existing app auto-closes predicted Spam | `initial_status = Closed if spam` | Documented blocker; replacement design requires review and never automatic rejection |
| Existing app exposes unprotected complaint/admin routes | No account/ownership dependencies | Treat as exploratory, not deployable; roadmap adds object-scoped RBAC |
| Existing app calls softmax margins calibrated confidence and fabricates fallback scores | `classify_text` and missing-model fallback | No operational calibration claim; roadmap requires approved artifact or safe pending/review state |
| Existing HITL route conflates mutable final label with workflow | No independent versioned disposition/verified-label model | Normalized target schema and state contracts in roadmap |
| Existing retrain route fetches but never passes feedback into training | `db_rows` used only in response message | No feedback-driven retraining demonstration; planned controlled snapshot/training gates |
| SQLite/static UI differs from preferred stack | No Next.js/PostgreSQL implementation evidence | Preserve prototype; plan selected stack without claiming implementation |

## New candidate experiment

Only after the original procedures, a fixed separate candidate was fitted: NFKC/casefold/whitespace normalization preserving negations and Unicode, word (1,2) TF-IDF plus `char_wb` (3,5) TF-IDF (45,000 cap), feature concatenation and LinearSVC C=0.1. A second candidate applies sigmoid calibration through three precomputed scenario-disjoint training folds, fitting the full feature pipeline within each fold. Both were evaluated only on the existing development validation partition. They tied the reference's perfect classification score. Calibration diagnostics are reported but do not certify field probability reliability. Candidates were never evaluated on the historical test. No improvement, operational HITL or retraining gain is claimed.

## Statistical and presentation limits

Paired model comparison aligns per-record IDs/truth labels for both reference pipelines. Exact two-sided McNemar tests and continuity-corrected chi-square statistics are reported. Generated records share families and construction rules, so independence is limited; nominal p-values do not establish generalization or an operational advantage. Fold SD is dispersion, not an independent population confidence interval. Probability reliability requires independently authored/annotated data before operational probabilities are exposed.

Final evaluation presentation uses 360-DPI PNG plus vector PDF/SVG in `results/figures/`, academic tables and the compiled PDF. CSV files remain internal machine-readable prediction/fold evidence and the original dataset, never the final presentation deliverable. No GitHub push, release, application deployment or live office testing was performed.
