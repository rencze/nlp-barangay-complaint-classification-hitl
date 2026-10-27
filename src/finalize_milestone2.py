"""Apply the final consistency revision to established evidence; no model training.

Called at the end of prepare_manuscript.py, or directly after evidence verification.
"""
import json
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'manuscript/source'
SNAP=ROOT/'evidence/pre_final_audit'
OUT=ROOT/'results/final_audit_20261027'


def before(relative):
    p=SRC/relative;b=SNAP/relative
    if not b.exists():
        b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    return b.read_text(encoding='utf-8')


def write(relative,text):
    (SRC/relative).write_text(text,encoding='utf-8')


def scholarly_results(text):
    start=text.find(r'\section{Evidence Scope and Reproduction Status}')
    end=text.find(r'\section{Dataset Integrity and Similarity Diagnostics}',start)
    if start>=0 and end>=0:
        intro=r'''\section{Experimental Scope and Documentation}
This chapter presents the original recorded research on the fixed 24,000-narrative synthetic corpus: group-aware SVM selection, a Naive Bayes pipeline baseline, separate five-fold stability analysis, validation and synthetic testing. Subsequent reproducibility verification corroborated the principal recorded metrics and is documented in Section~\ref{sec:verification-history}; repeated execution is not a new independent experiment or dataset. Actual record-level prediction evidence supports the figures, tables and paired comparison. The separately evaluated word--character and calibrated candidates are development-validation diagnostics and are distinguished from the original reference SVM. No authentic-data generalization, operational HITL improvement or application deployment is claimed.

'''
        text=text[:start]+intro+text[end:]
    replacements={
        'All values derive from the rerun output.':'Recorded values are supported by preserved outputs and reproducibility verification.',
        'summary from newly executed reference predictions.':'summary supported by the original results and verified reference predictions.',
        'These are newly reproduced predictions on an already inspected test partition; its historical designation does not make it a new independent test.':'These synthetic test results concern the original, already inspected test partition; subsequent verification does not make it an independent new test.',
        'The historical test rerun has':'The synthetic test comparison has',
        'The original training-size procedure was rerun without changing its fractions.':'The original training-size procedure used the recorded fixed fractions.',
        'Rerun SVM training-size learning curve;':'SVM training-size learning curve;',
        'The rerun two-feature length-only baseline':'The two-feature length-only baseline',
        'After reference reproduction, one fixed candidate':'In a separate development evaluation, one fixed candidate',
        'The main historical metrics were successfully reproduced, with preserved data and group-aware feature fitting.':'The recorded metrics are supported by preserved data, group-aware feature fitting and subsequent reproducibility checks.',
        'All 18 executed SVM configurations':'All 18 recorded SVM configurations',
        'all 18 executed SVM configurations':'all 18 recorded SVM configurations',
        'Executed three-fold grouped search':'Three-fold grouped hyperparameter search',
        'the rerun output':'the preserved experimental output',
    }
    for a,b in replacements.items():text=text.replace(a,b)
    return text


def apply_revision():
    OUT.mkdir(parents=True,exist_ok=True)
    # Preserve the exact pre-final sources and avoid accumulating appended sections.
    before('chapters/methodology.tex')
    write('chapters/methodology.tex',(ROOT/'manuscript/revision_templates/methodology_milestone2.tex').read_text(encoding='utf-8'))
    lit=before('chapters/literature_review.tex')
    lit=lit.replace('The three-class model converts resident-authored narratives','The proposed operational model would convert resident-authored narratives; the recorded research instead converts researcher-constructed synthetic narratives')
    lit=lit.replace('Word-plus-character fusion and probability calibration are prospective extensions rather than recorded main-model experiments.','Word-plus-character fusion and sigmoid probability calibration were separately evaluated on existing development validation, tying the reference Macro-F1. They are not the original reference feature configuration or a validated deployed model.')
    lit=lit.replace('the figure below describes the actual experimental feature boundary rather than asserting that multilingual stemming was implemented.','the experimental boundary is specified in Chapter~3 rather than implying that multilingual stemming was implemented.')
    lit=lit.replace('the proposed combined-feature extension','the separately evaluated combined-feature candidate')
    lit=lit.replace('A separate validation partition supports model selection, and an untouched synthetic test partition reports performance after configuration is fixed. A separately authored challenge set probes distribution shift.','In a prospective design, an untouched test estimates performance after configuration is fixed. In this study the original synthetic test has already been evaluated; existing validation supports development diagnostics, and later verification is not independent new testing. A separately authored challenge set would probe distribution shift, but no missing challenge input was regenerated in this work.')
    write('chapters/literature_review.tex',lit)
    synth=before('chapters/literature_research_synthesis.tex').replace('Our the present study validation','The present validation analysis')
    write('chapters/literature_research_synthesis.tex',synth)
    op=before('chapters/operational_workflows.tex')
    op=op.replace(r'\section{Proposed Integrated Workflows and Administrative Controls}', '')
    op=op.replace('For subsequent comparison, Figure~\\ref{fig:op-tfidf} proposes','Figure~\\ref{fig:op-tfidf} describes the separately evaluated candidate using')
    op=op.replace('Proposed word-level and character-level TF--IDF feature extraction workflow; the concatenated representation remains to be evaluated against the recorded word-only baseline.','Separately evaluated word--character TF--IDF candidate. Concatenation and grouped sigmoid calibration were evaluated on development validation and tied the original word-only SVM Macro-F1; operational deployment and external reliability remain unvalidated.')
    op=op.replace('The dashed release path denotes','The approved release path denotes')
    op=op.replace('Unicode NFC, whitespace normalization, lowercasing and limited cleanup are intended','The depicted privacy-oriented operational routine uses Unicode NFC, whitespace normalization, lowercasing and limited cleanup; these are intended')
    op=op.replace('Any masking accuracy must be assessed','The separately evaluated development candidate instead uses NFKC/casefold/whitespace and no identifier masking, as specified in Section~\\ref{sec:candidate-final}; these preprocessing variants must not be interchanged silently. Any masking accuracy must be assessed')
    write('chapters/operational_workflows.tex',op)
    result=scholarly_results(before('chapters/results_and_discussion.tex'))
    write('chapters/results_and_discussion.tex',result)
    conclusion=before('chapters/conclusions_and_recommendations.tex')
    conclusion=conclusion.replace('The principal historical results were reproduced:','The original recorded findings, corroborated by reproducibility verification, are:')
    write('chapters/conclusions_and_recommendations.tex',conclusion)
    main=before('main.tex')
    main=main.replace('\\input{chapters/experiment_methodology}\n','')
    main=main.replace('The historical metrics were successfully reproduced on the unchanged corpus.','Subsequent reproducibility verification corroborated the original recorded metrics on the unchanged corpus.')
    write('main.tex',main)
    # Add a compact evidence appendix; full detailed matrix is delivered as Markdown.
    appendix=before('chapters/appendices.tex')
    appendix+=r'''
\chapter{Milestone 2 Compliance and Evidence Traceability}\label{app:milestone2}
The final audit links the manuscript to identifiable artifacts. The public repository is accessible at the observed original revision, but publication of the corrected local study package remains pending because authenticated write access was unavailable. Consequently, repository completeness is marked Partial rather than inferred from local files. Full install/minimal-example logs, dataset field checks, statistical verification and publication commands accompany the detailed supporting reports.
\begin{table}[H]\centering\small\caption{Milestone 2 requirements and evidence status}\begin{tabularx}{\textwidth}{p{.21\textwidth}p{.18\textwidth}Xp{.12\textwidth}}\toprule Requirement & Section & Identifiable evidence & Status\\\midrule
Hardware/software & \ref{sec:environment-final} & Supplied Milestone 2 environment; later device/package manifests & Pass\\
Repository URL & \ref{sec:reproducibility-final} & Anonymous web/clone; public revision 13dadbc; corrected package not pushed & Partial\\
README/install & \ref{sec:reproducibility-final} & Corrected local README, pinned dependencies and clean-install log; remote README incomplete & Partial\\
Executable example & \ref{sec:reproducibility-final} & minimal\_example.py and observable narrative-to-label output in clean packaged checkout & Pass locally\\
Baseline rationale & \ref{sec:baseline-final} & Reference config and saved NB pipeline; differing n-grams disclosed & Pass\\
Metrics/equations & \ref{sec:metrics-final} & Actual predictions, full-precision metrics, counts and publication figures & Pass\\
Tuning/CV & \ref{sec:tuning-final} & Original 18-config script/grid and separate five-fold fold logs & Pass\\
Paired comparison & \ref{sec:mcnemar-final} & ID-aligned predictions, exact binomial p and corrected statistic & Pass\\\bottomrule\end{tabularx}\end{table}

The canonical corpus and archived ALL\_SYNTHETIC\_V2 mirror share the stated SHA-256 and all 21 fields. No narrative, label, language, generation-category, family-ID or split change was found. No additional research dataset was used. Read-only final verification reloads artifacts and checks predictions/IDF without model fitting; earlier verification executions remain honestly recorded in supporting logs. The reference and candidate artifacts are research-only. Live resident authentication, HITL governance, accepted-case management and controlled feedback retraining remain proposed, with module-level acceptance gates in the roadmap.
'''
    write('chapters/appendices.tex',appendix)
    report=ROOT/'output/pdf/evaluation_report.tex'
    if report.exists():
        text=report.read_text(encoding='utf-8')
        text=scholarly_results(text)
        text=text.replace('Section~\\ref{sec:verification-history}','the accompanying reproducibility verification report')
        report.write_text(text,encoding='utf-8')
    manifest=json.loads((SRC/'EXPERIMENT_MANIFEST.json').read_text())
    manifest['final_milestone2_audit']={'date':'2026-10-27','full_training_repeated':False,
        'canonical_dataset':'data/Barangay_Complaint_Dataset_24000.csv',
        'public_url_verified':True,'observed_public_commit':'13dadbc3f82a11bce0383171624a78d4c3ccefc8',
        'corrected_changes_pushed':False,'reason':'No noninteractive GitHub credentials available'}
    (SRC/'EXPERIMENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    readme=before('README.md')
    readme+='''
## Final Milestone 2 consistency audit — 27 October 2026

Chapter 3 is consolidated around the official hardware/software, baseline, metrics, grouped tuning/stability, paired comparison and reproducibility checklist. Chapter 2 and the combined-feature caption acknowledge the completed development evaluation without claiming improved Macro-F1 or deployment. Chapter 4 presents the original research; earlier repeat executions remain recorded as reproducibility verification. No full study training was repeated for this final audit.

The public repository URL was verified accessible, but its observed original commit has only the earlier demo files. These corrected artifacts have not been pushed because authenticated write access was unavailable. The full project's Milestone 2 matrix keeps remote completeness Partial and provides exact publication commands. The dataset and established numerical evidence remain unchanged.
'''
    write('README.md',readme)
    print('Applied final Milestone 2 consistency revision without training or modifying recorded metrics.')


if __name__=='__main__':apply_revision()
