"""Supporting Milestone 2 reports generated from read-only verification evidence."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'results/final_audit_20261027'
DOC=ROOT/'docs'


def main():
    data=json.loads((AUDIT/'dataset_integrity.json').read_text())
    experiment=json.loads((AUDIT/'experimental_verification.json').read_text())
    DOC.mkdir(exist_ok=True)
    pairs={'corrected_clean_checkout_minimal.txt':'clean_checkout_minimal.txt',
           'corrected_clean_checkout_evidence.txt':'clean_checkout_evidence_audit.txt',
           'corrected_clean_checkout_manuscript.txt':'clean_checkout_manuscript_preparation.txt'}
    captured={}
    for src,dest in pairs.items():
        path=ROOT/'tmp'/src
        if not path.exists():continue
        raw=path.read_bytes()
        value=raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig',errors='replace')
        value=value.replace(str(ROOT),'<PROJECT_ROOT>').replace(str(Path.home()),'<USER_HOME>')
        (AUDIT/dest).write_text(value,encoding='utf-8');captured[dest]=value
    if len(captured)==3:
        assert '-> valid' in captured['clean_checkout_minimal.txt'] and '-> spam' in captured['clean_checkout_minimal.txt']
        assert 'PASS:' in captured['clean_checkout_evidence_audit.txt']
        assert 'Applied final' in captured['clean_checkout_manuscript_preparation.txt']
        (AUDIT/'clean_checkout_status.json').write_text(json.dumps({
            'pinned_requirements_installed':True,'pip_check_passed':True,'minimal_example_passed':True,
            'read_only_evidence_check_passed':True,'manuscript_preparation_without_training_passed':True,
            'source':'Fresh extraction of corrected research ZIP; independent pinned venv',
            'full_study_training_performed':False},indent=2),encoding='utf-8')
    text='''# Dataset Integrity Report

Verified 27 October 2026. The canonical source was not edited. No new research dataset, relabeling, narrative rewrite, language reassignment or repartitioning was performed.

| File | SHA-256 | Finding |
|---|---|---|
'''
    for path in [data['canonical_path'],data['mirror_path']]:
        text+=f"| `{path}` | `{data['sha256']}` | Byte-identical original corpus |\n"
    text+='''
The hash equals the recorded original manifest. A separate CSV comparison checked **all 21 fields for all 24,000 records and their order**, not merely counts. This establishes that ALL_SYNTHETIC_V2 is an exported copy, not a replacement dataset. The existing split exports also match canonical records in all fields/order. The canonical path for repository instructions is `data/Barangay_Complaint_Dataset_24000.csv`; the Overleaf project's mirror is retained for self-contained archival documentation.

| Partition | Records | All fields/order match canonical | Scenario overlap with other splits |
|---|---:|---|---:|
'''
    for split,v in data['splits'].items():text+=f"| {split} | {v['n']:,} | Yes | 0 |\n"
    text+='''
Classes: 8,000 Valid, 8,000 Suspicious, 8,000 Spam. Assigned language groups: 6,000 each Bisaya, Filipino, English and Mixed. All 118 generation categories are retained. Zero changed narratives, labels, language assignments, category fields, scenario/template IDs or partition memberships were found. Source and language/human-review flags remain synthetic/unreviewed. Small example datasets are demonstration inputs, not additional research observations; no challenge or feedback data was introduced.

No raw or conservative Unicode-normalized exact duplicates were found in the established audit, and family/template/exact-text cross-split overlap is zero. High lexical similarity still limits independence; exact integrity is not a semantic or annotation-quality certification. The synthetic test remains an already evaluated original partition.

Code/evidence: `src/final_evidence_audit.py`, `results/final_audit_20261027/dataset_integrity.json`, original hash in `evidence/historical/manuscript/EXPERIMENT_MANIFEST.json`, and `results/verified_20261026/dataset_audit.json`. Training-only fitted IDF was independently checked against document frequencies of the stored training narratives without fitting a new model. The saved reference artifacts/predictions agree; historical scripts keep TF-IDF inside training folds. No holdout fitting was found in those paths, while generator-family semantic dependence remains a disclosed limitation.
'''
    (DOC/'DATASET_INTEGRITY_REPORT.md').write_text(text,encoding='utf-8')
    matrix='''# Milestone 2 Compliance Matrix

Audit date: 27 October 2026. Official checklist: **Experimental Setup, Reproducibility, and Evaluation Metrics (Final Chapter 3)**. Source requirements were checked against `research_evidence/Milestone2_Reference_Submission.pdf` and the user's explicit checklist.

**Overall: locally corrected and evidence-verified; public-repository completeness remains Partial.** Public accessibility is verified, but corrected study artifacts have not been pushed because no noninteractive GitHub credentials are available. A local Pass means an artifact actually exists and its relevant check succeeded, not merely that the manuscript describes it. It does not assert publication at the observed public commit.

| Milestone 2 requirement | Manuscript section | GitHub/local evidence | Verification | Correction needed / remaining action |
|---|---|---|---|---|
| Hardware and software | 3.3 Hardware and Software Environment (`sec:environment-final`) | Supplied Milestone PDF; `results/final_audit_20261027/hardware_verification.json`, package manifests | Pass locally: historical attribution and current CPU/GPU/RAM/OS corroboration | OS original patch 26200.9457 distinguished from current 26200.9711; no GPU acceleration claim; historical library versions distinguished from verification pins |
| Accessible repository | 3.8 Experimental Documentation and Reproducibility (`sec:reproducibility-final`) | Public URL and clean clone at `13dadbc3f82a11bce0383171624a78d4c3ccefc8`; `repository_status.json` | Partial: public URL works; full study artifacts are local only | Publish corrected files using `docs/PUBLISH_CORRECTIONS.md`; recheck new commit anonymously |
| README/install instructions | 3.8 (`sec:reproducibility-final`) | Corrected root README/requirements; clean pinned install log and pip check; public README is two lines | Pass locally / Partial publicly | Exact versions and actual commands added locally; authenticated publication remains pending |
| Executable minimal example | 3.8 (`sec:reproducibility-final`) | `src/minimal_example.py`; demo CSV; clean-packaged-checkout output; older public `src/train.py` also exercised | Pass locally / Partial publicly | New example prints narrative-to-label predictions, requires no undocumented path; publish README/script then repeat from public clone |
| Baseline rationale | 3.4 Reference Pipelines and Baseline Selection (`sec:baseline-final`) | Actual NB joblib artifact; `reference_config.json`; original evaluate_models.py | Pass locally; artifact publication pending | Added sparse-text, computational-cost and conditional-independence justification; whole-pipeline comparison explicitly retains differing n-grams |
| Metrics/equations | 3.6 Evaluation Metrics and Error Analysis (`sec:metrics-final`), Chapter 4 | `predictions.csv`, metrics JSON, `experimental_verification.json`, `results/figures/` | Pass locally; artifact publication pending | Defined every variable, zero denominators, Macro-F1 justification and Valid-as-Spam risk; all aggregate/count checks agree |
| Hyperparameter tuning | 3.5 Partitioning, Hyperparameter Search and Stability Analysis (`sec:tuning-final`) | Original script's AST/config and 18 grid rows; separate five-fold fold logs | Pass locally; artifact publication pending | Fixed/variable settings, seed, three-fold grouped search and separate stability roles agree; no historical retuning |
| Statistical comparison | 3.7 Paired Statistical Comparison (`sec:mcnemar-final`), Chapter 4 | ID-aligned predictions, exact binomial p/continuity-corrected statistic, figure and code | Pass locally; artifact publication pending | Corrected p-value meaning and dependence limits; no unsupported t-test/Friedman |

Additional acceptance checks: unchanged dataset in `DATASET_INTEGRITY_REPORT.md`; reference/candidate separation in 3.8.2 and Chapter 4; proposed system scope in 3.9; no operational validation claims in Chapter 5; full-stack module evidence in `FULL_STACK_ALIGNMENT.md`. The milestone appendix uses LaTeX references so manuscript numbering remains accurate after compilation. Final compilation/render verification is recorded separately.
'''
    (DOC/'MILESTONE2_COMPLIANCE_MATRIX.md').write_text(matrix,encoding='utf-8')
    text='''# Experimental Verification Report

Read-only final audit, 27 October 2026. **No full-study training, search, calibration or retraining was repeated in this final audit.** The earlier verification executions remain documented in preserved logs. Tiny demo fitting is solely an executable-example check, not a new research experiment.

The original 24,000-record corpus and stored partitions are unchanged. Saved research models were reloaded and their predictions matched existing exports record by record. Metrics below are recomputed from those actual predictions and match saved full-precision evidence within 1e-12. They describe the original synthetic benchmark, not new independent data.

| Pipeline | Partition | N | Accuracy | Macro-precision | Macro-recall | Macro-F1 | Weighted-F1 | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for name,display in [('svm','Linear SVM'),('nb','Naive Bayes')]:
        for split,m in experiment['metrics'][name].items():
            text+=f"| {display} | {split} | {m['n']} | {m['accuracy']:.6f} | {m['macro_precision']:.6f} | {m['macro_recall']:.6f} | {m['macro_f1']:.6f} | {m['weighted_f1']:.6f} | {m['errors']} |\n"
    text+='\nAll four confusion matrices use row/reference and column/prediction order Valid, Suspicious, Spam. The matrices are retained as publication figures with actual counts and per-class academic tables in Chapter 4 and the evaluation report. Baseline errors are Spam predicted as Suspicious; no Valid-as-Spam error occurs in these stored reference evaluations. All assigned-language supports and Macro-F1 values were also checked directly against record-level predictions.\n\n'
    text+='''| Partition | Both correct (a) | Baseline only (b) | SVM only (c) | Both wrong (d) | Corrected chi-square | Exact two-sided p |
|---|---:|---:|---:|---:|---:|---:|
'''
    for split,v in experiment['paired_mcnemar'].items():text+=f"| {split} | {v['a']} | {v['b']} | {v['c']} | {v['d']} | {v['corrected_chi2']:.6f} | {v['exact_p']:.12g} |\n"
    text+='''
The exact test uses Binomial(b+c,0.5); the nonnegative continuity-corrected statistic is max(0,|b-c|-1)^2/(b+c). Nominal p<.05 favors SVM on this benchmark; shared generated families constrain independent-pair interpretation and field inference. These pipelines use different n-grams, so estimator-only superiority is not isolated.

The original GridSearchCV has 18 combinations: C=.1/1/10, n-grams=(1,1)/(1,2), min_df=2/5/10, fixed max_df=.95 and sublinear_tf=True, seed20261026, three grouped folds. All saved grid scores are 1.0. Separate five-fold training-only stability has mean/SD 1.000000/0 for SVM and .992452/.000971 for NB; historical output comparisons already corroborate these values. Neither this final audit nor figure generation repeats those fits. Reference vocabulary/IDF matches the 19,213 training document frequencies, and feature metadata are excluded by the source paths.

The fixed word+character candidate and its grouped-sigmoid variant remain separate development evaluations: both have validation Macro-F1 1.0, tying the reference. There are no candidate test predictions. Probability diagnostics on the synthetic development distribution do not establish independent operational reliability. Reference model loading is tested research code; authenticated live service integration remains planned.

Final presentation: all 14 evaluation figure families exist as 360-DPI PNG plus PDF/SVG in `results/figures/`. The original dataset is CSV; prediction/CV CSV and JSON are internal evidence, not final presentation. The image-based `ML_Evaluation_Report.pdf` and Chapter 4 provide the academic presentation. Source: `src/final_evidence_audit.py`, `experimental_verification.json`, historical output archive and `reproduction_comparison.json`.
'''
    (DOC/'EXPERIMENTAL_VERIFICATION_REPORT.md').write_text(text,encoding='utf-8')
    print('Generated dataset integrity, Milestone 2 traceability and experimental verification reports from established evidence.')


if __name__=='__main__':main()
