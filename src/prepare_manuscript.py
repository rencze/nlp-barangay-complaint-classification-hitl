"""Prepare thesis edits and a standalone evaluation report from executed evidence.

Run once against the extracted authoritative source, then compile main.tex and report.tex.
"""
import csv
import json
import shutil
from pathlib import Path
from research_validation import ROOT, OUT, LABELS

SRC=ROOT/'manuscript/source'
FIG=ROOT/'results/figures'


def original(path):
    baseline=ROOT/'evidence/historical/manuscript'/path.relative_to(SRC)
    if not baseline.exists():
        baseline.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,baseline)
    return baseline.read_text(encoding='utf-8')


def figure(stem,caption,label,width='.96',height='.72'):
    return '\n'+r'\begin{figure}[H]\centering'+'\n'+rf'\includegraphics[width={width}\textwidth,height={height}\textheight,keepaspectratio]{{figures/verified/{stem}.pdf}}'+'\n'+rf'\caption{{{caption}}}\label{{{label}}}'+'\n'+r'\end{figure}'+'\n'


def main():
    m=json.loads((OUT/'metrics.json').read_text(encoding='utf-8'))
    near=json.loads((OUT/'near_duplicate_diagnostics.json').read_text())
    env=json.loads((OUT/'environment.json').read_text())
    pair=json.loads((OUT/'paired_comparison.json').read_text())
    target=SRC/'figures/verified';target.mkdir(parents=True,exist_ok=True)
    for p in FIG.glob('*.pdf'):shutil.copy2(p,target/p.name)
    for p in (ROOT/'docs/diagrams').glob('*.pdf'):shutil.copy2(p,target/p.name)
    # A reproducibility comparison preserves original reported precision and runs.
    historical=json.loads((ROOT/'evidence/historical/results/model_results_v2.json').read_text())
    rerun=json.loads((SRC/'results/model_results_v2.json').read_text())
    comparison={}
    for key in ['chosen_params','best_cv_macro_f1','svm','naive_bayes','length_only_baseline_test','lexical_similarity','sgd_loss_start_end','learning_curve']:
        comparison[key]={'matches_historical_at_original_precision':historical.get(key)==rerun.get(key)}
    with (ROOT/'evidence/historical/validation_suite/five_fold_grouped_cv_results.csv').open() as f:old=list(csv.DictReader(f))
    with (SRC/'validation_suite/five_fold_grouped_cv_results.csv').open() as f:new=list(csv.DictReader(f))
    comparison['fivefold_metrics']={'matches_historical_within_1e_12':len(old)==len(new) and all(a['model']==b['model'] and a['fold']==b['fold'] and abs(float(a['cv_macro_f1'])-float(b['cv_macro_f1']))<1e-12 for a,b in zip(old,new))}
    savepath=OUT/'reproduction_comparison.json';savepath.write_text(json.dumps(comparison,indent=2))
    ch=r'''\chapter{Results and Discussion}
\section{Evidence Scope and Reproduction Status}
The supplied Overleaf project is the authoritative manuscript source. The archived three-fold grouped, 18-configuration experiment and the separate five-fold grouped validation procedure were executed first, without changing their feature settings, seed or partition membership. Historical outputs remain preserved separately. The local 24,000-record CSV has the same SHA-256 checksum as the archived corpus, and every stored split matches its archived records and order. The newly executed reference results reproduce the reported principal metrics at their original precision. These are repeated measurements on the same synthetic data, not independent validation on authentic complaints.

The rerun used Python 3.13.5 and scikit-learn 1.8.0. NumPy, SciPy and pandas differ from the submitted environment record; the exact executed versions and source hashes are captured with the run. Consequently, this is procedural and numerical reproduction rather than a bitwise recreation of the original software environment. A separate combined-feature candidate was evaluated only after the original procedures, as a development experiment. No new data, relabeling, operational HITL trial or application deployment was performed.

\section{Dataset Integrity and Similarity Diagnostics}
The unchanged corpus contains 8,000 examples per class and 6,000 per assigned language group. Recorded partitions remain 19,213 training, 2,399 validation and 2,388 previously evaluated synthetic test records. Raw and Unicode-normalized exact duplicate excess are both zero. Record IDs are unique, and scenario-family, template-family and normalized-text overlaps between stored partitions are zero. These checks establish identifier and exact-text separation, not independent linguistic construction.
'''
    ch+=f"A training-fitted reference unigram TF--IDF similarity diagnostic found nearest-training cosine similarity of at least 0.90 for {near['validation']['fraction_at_least_0_9']*100:.2f}\\% of validation narratives and {near['test']['fraction_at_least_0_9']*100:.2f}\\% of test narratives. Median similarities were {near['validation']['median_nearest_cosine']:.6f} and {near['test']['median_nearest_cosine']:.6f}, respectively. This descriptive lexical threshold does not adjudicate duplicates. Shared phrases and class-conditional generator rules remain plausible explanations of ceiling scores. All language and human-label review flags remain negative.\n"
    ch+=r'''
\section{Hyperparameter Search and Grouped Cross-Validation}
Figure~\ref{fig:verified-grid} presents all 18 executed SVM configurations using training-only three-fold grouped Macro-F1. Every configuration scored 1.000000 with zero recorded fold dispersion; deterministic tie handling selected $C=0.1$, word unigrams and minimum document frequency 2. The uniform grid cannot demonstrate that any parameter choice is intrinsically superior.
'''+figure('hyperparameter_tuning_results','Executed three-fold grouped search over all 18 SVM configurations. All values derive from the rerun output.','fig:verified-grid',height='.69')
    ch+=r'''
The separate five-fold stability analysis refitted the complete vectorizer/classifier pipeline within each training fold. It excluded the fixed validation and historical test records and verified zero scenario-family overlap within all folds. Figure~\ref{fig:verified-cv} reports fold values and aggregate sample standard deviations. SVM mean Macro-F1 was 1.000000 (SD 0.000000), while Naive Bayes mean Macro-F1 was 0.992452 (sample SD 0.000971). This dispersion is descriptive and is not a population confidence interval or an independent nested model-selection estimate.
'''+figure('cross_validation_results','Five-fold scenario-grouped training-only cross-validation, including fold-level values, means and sample standard deviations.','fig:verified-cv')
    for split,title,stem,sectionlabel in [('validation','Fixed Development Validation','validation','validation'),('test','Previously Evaluated Synthetic Test','testing','test')]:
        n=m['svm'][split]['n'];nb=m['nb'][split]
        ch+=f'\n\\section{{{title}}}\n'
        ch+=f"The same two frozen reference pipelines were evaluated on {n:,} {('validation' if split=='validation' else 'historically evaluated synthetic test')} narratives. Linear SVM achieved {m['svm'][split]['macro_f1']:.6f} Macro-F1 with {m['svm'][split]['errors']} errors; Naive Bayes achieved {nb['macro_f1']:.6f} Macro-F1 with {nb['errors']} errors. Figure~\\ref{{fig:verified-{sectionlabel}-summary}} gives accuracy, macro-precision, macro-recall, Macro-F1, Weighted-F1 and record counts. "
        ch+=('The validation partition is an existing development benchmark.\n' if split=='validation' else 'These are newly reproduced predictions on an already inspected test partition; its historical designation does not make it a new independent test. It was not used for candidate feature or calibration selection.\n')
        ch+=figure(stem+'_performance',f'{title} summary from newly executed reference predictions. Precision and recall are macro-averaged.',f'fig:verified-{sectionlabel}-summary',height='.44')
        for name,display in [('svm','Linear SVM'),('nb','Naive Bayes')]:
            cm=m[name][split]['confusion_matrix']
            text=('No errors occurred in the reference SVM on this within-generator partition.' if name=='svm' else f"All {m[name][split]['errors']} Naive Bayes errors were reference Spam narratives predicted as Suspicious.")
            ch+=f"\n{text} Figure~\\ref{{fig:verified-{name}-{sectionlabel}-cm}} gives the actual counts, with reference labels on rows and predictions on columns.\n"
            ch+=figure(('svm' if name=='svm' else 'naive_bayes')+'_'+stem+'_confusion_matrix',f'{display} confusion matrix on the {title.lower()} partition. Entries are narrative counts.',f'fig:verified-{name}-{sectionlabel}-cm',width='.78',height='.52')
        ch+=r'\begin{table}[H]\centering\small\caption{Per-class metrics on the '+title.lower()+r' partition}\label{tab:verified-'+sectionlabel+r'-classes}\begin{tabular}{llrrrr}\toprule'+'\n'+r'Pipeline & Class & Precision & Recall & F1 & Support\\\midrule'+'\n'
        for name,display in [('svm','SVM'),('nb','Naive Bayes')]:
            for label in LABELS:
                v=m[name][split]['report'][label]
                ch+=f"{display} & {label} & {v['precision']:.6f} & {v['recall']:.6f} & {v['f1-score']:.6f} & {int(v['support'])} \\\\\n"
        ch+=r'\bottomrule\end{tabular}\end{table}'+'\n'
    ch+=r'''
\section{Reference Pipeline Comparison}
Figure~\ref{fig:verified-comparison} compares both reference pipelines across all five aggregate metrics and both partitions. Its full 0--1 axis prevents a visually exaggerated difference near the score ceiling. Hatching and distinct labels preserve readability in grayscale. The selected SVM uses word unigrams while the Naive Bayes baseline uses unigrams/bigrams; this is a comparison of complete pipelines, not a controlled isolation of estimator choice.
'''+figure('model_performance_comparison','Reference SVM and Naive Bayes comparison on fixed validation and the previously evaluated synthetic test.','fig:verified-comparison',height='.69')
    ch+=r'''
\section{Paired Statistical Comparison}
The reference predictions were exported with record identifiers and aligned by identifier and reference label before computing McNemar's test. Figure~\ref{fig:verified-mcnemar} presents both contingency tables, continuity-corrected statistics and exact two-sided binomial p-values. Validation has $b=0,c=19$, corrected $\chi^2=17.052632$ and $p=3.814697266\times10^{-6}$. The historical test rerun has $b=0,c=20$, corrected $\chi^2=18.05$ and $p=1.907348633\times10^{-6}$.
'''+figure('statistical_comparison','Paired McNemar analysis computed from actual per-record reference predictions on both existing partitions.','fig:verified-mcnemar',width='.90',height='.70')
    ch+=r'''
Both nominal p-values are below 0.05 and favor the SVM's error incidence on this synthetic benchmark. This is not proof of field superiority, an effect of HITL, or equivalence of the underlying feature representations. Generated narratives share families and construction rules, which limits the independent-pair assumption and may make nominal p-values anticonservative. No probability of successful real-world complaint resolution follows from these tests.

\section{Assigned-Language Performance}
Language groups are generator metadata, not classifier inputs or independently verified language labels. Figure~\ref{fig:verified-languages} reports validation subgroup support and Macro-F1. Each SVM subgroup reaches the same ceiling while baseline errors vary. These findings cannot establish linguistic fairness or transfer to naturally authored code-switching.
'''+figure('language_group_validation','Validation performance by assigned language group; group supports are shown explicitly.','fig:verified-languages',height='.48')
    ch+=r'\begin{table}[H]\centering\small\caption{Previously evaluated synthetic test by assigned language group}\begin{tabular}{lrrr}\toprule Language & N & SVM Macro-F1 & NB Macro-F1\\\midrule'+'\n'
    for lang in ['Bisaya','Filipino','English','Mixed']:
        a=m['svm']['test']['assigned_language_groups'][lang];b=m['nb']['test']['assigned_language_groups'][lang]
        ch+=f"{lang} & {a['n']} & {a['macro avg']['f1-score']:.6f} & {b['macro avg']['f1-score']:.6f} \\\\\n"
    ch+=r'\bottomrule\end{tabular}\end{table}'+'\n'
    learning=rerun['learning_curve'];loss=rerun['sgd_loss_start_end']
    ch+=r'\section{Learning and Shortcut Diagnostics}'+'\n'
    ch+=f"The original training-size procedure was rerun without changing its fractions. Validation Macro-F1 was {learning[0]['validation_macro_f1']:.6f} at {learning[0]['train_n']:,} training records and reached 1.000000 from the 20\\% fraction onward (Figure~\\ref{{fig:verified-learning}}). Early saturation is consistent with easily learned generator patterns and does not establish sample sufficiency for authentic reports.\n"
    ch+=figure('svm_learning_curve','Rerun SVM training-size learning curve; sample count is not an optimizer epoch.','fig:verified-learning',height='.45')
    ch+=f"A separate SGD hinge-loss classifier supplies the epoch diagnostic in Figure~\\ref{{fig:verified-loss}}; it is not the selected LinearSVC optimizer. Training hinge loss changed from {loss['start']['training_hinge_loss']:.6f} to {loss['end']['training_hinge_loss']:.6f}, and validation loss from {loss['start']['validation_hinge_loss']:.6f} to {loss['end']['validation_hinge_loss']:.6f} over 15 passes. A decreasing auxiliary loss does not rule out generator-specific overfitting.\n"
    ch+=figure('auxiliary_sgd_loss','Measured auxiliary SGD training/validation hinge loss, explicitly separate from the final LinearSVC estimator.','fig:verified-loss',height='.45')
    length=json.loads((SRC/'validation_suite/length_only_validation.json').read_text())
    ch+=f"The rerun two-feature length-only baseline achieved {length['accuracy']:.6f} validation accuracy and {length['macro_f1']:.6f} Macro-F1. This above-chance diagnostic confirms that narrative length carries class information. A separate character-only diagnostic also reached the synthetic validation ceiling. These are diagnostics, not evidence of semantic understanding. No independent challenge dataset was executed: the archived 96-message challenge results remain historical, while the optional prior 48-message input expected by the original script was absent.\n"
    ch+=r'''
\section{Separately Evaluated Combined-Feature Candidate}
After reference reproduction, one fixed candidate combined word unigrams/bigrams with character-within-word 3--5-grams, using conservative normalization and $C=0.1$. A second version used sigmoid calibration through three scenario-grouped training folds. Both candidates were evaluated only on the 2,399 existing validation records; neither was run on the historical test. Figure~\ref{fig:verified-candidate} separates their development results from the reference measurements.
'''+figure('candidate_validation_results','Separately executed word-plus-character candidates, with and without grouped sigmoid calibration; development validation only.','fig:verified-candidate',height='.40')
    p=m['candidate_calibrated']['validation']['probability_diagnostics']
    ch+=f"Both candidates achieved 1.000000 validation Macro-F1 and zero errors, tying the word reference; therefore no classification improvement was demonstrated. The calibrated candidate yielded log loss {p['log_loss']:.8f}, multiclass Brier sum {p['multiclass_brier_sum']:.8f}, and ten-bin expected calibration error {p['ece_10_equal_width_bins']:.8f}. These probability diagnostics are measured on the same synthetic development distribution and do not certify operational reliability. Candidate calibration is now an executed research component; probability-based live decisions and field calibration validation remain proposed.\n"
    ch+=r'''
\section{Interpretation and Limits}
The main historical metrics were successfully reproduced, with preserved data and group-aware feature fitting. Perfect SVM scores must be reported faithfully, but their credibility is bounded by synthetic, unreviewed labels, repeated construction patterns, high nearest-training similarity and an already inspected test set. No new authentic data, annotation agreement study, prospective feedback trial, web-system acceptance test or complaint-resolution effectiveness study was conducted. Next steps are independent annotation and external validation, followed by the separately specified application, HITL, privacy, case-management and model-release tests.
'''
    (SRC/'chapters/results_and_discussion.tex').write_text(ch,encoding='utf-8')
    # Update evidence boundary in the authoritative source without changing citations.
    path=SRC/'chapters/methodology.tex';text=original(path)
    text=text.replace('proposed word-plus-character inference, calibration, HITL and model retraining remain separately identified as future system capabilities.','combined features and calibration are separately evaluated development candidates, while operational HITL and model retraining remain proposed system capabilities.')
    text=text.replace('No currently unimplemented probability calibration, HITL workflow, model retraining or live case management is to be described as tested merely because these design diagrams appear in Chapter~3.','A subsequent combined-feature/calibration experiment was executed on development validation only; operational HITL, feedback retraining and live case management remain untested regardless of their appearance in design diagrams.')
    text=text.replace("Public access could not be independently confirmed during this revision (the web endpoint returned an HTTP 404); a private repository or unpublished branch is possible.","The earlier manuscript recorded an HTTP 404 observation; remote visibility was not reverified during this local reproduction.")
    text=text.replace('the later, independent','the later, separate').replace('The later, independent','The later, separate')
    text=text.replace(r'\chi^2_{\mathrm{McN}} &= \frac{(|b-c|-1)^2}{b+c}',r'\chi^2_{\mathrm{McN}} &= \frac{\max(0,|b-c|-1)^2}{b+c}')
    text=text.replace('A calibrated pipeline is required and must be independently evaluated before confidence-guided administrative prioritization can operate.','A separate combined-feature sigmoid-calibrated candidate was subsequently evaluated on existing development validation only, as reported in Chapter~4. Independent probability reliability evidence remains required before operational probability-based decisions.')
    text=text.replace('The combined word-unigram/bigram plus character-within-word 3--5-gram representation illustrated in the proposed workflow is a \\emph{candidate extension}, not the feature set producing the reported SVM results.','The combined word-unigram/bigram plus character-within-word 3--5-gram representation is a separately evaluated development candidate, not the feature set producing the historical reference SVM results.')
    # Prevent historical environment and rerun status from being conflated.
    text=text.replace('Frozen Pre-Rerun Protocol and Evidence Boundary','Preserved Reproduction Protocol and Evidence Boundary')
    text=text.replace('Before rerunning the research scripts for code and GitHub documentation, the researchers will preserve','For the completed rerun, the researchers preserved')
    text=text.replace('The first task of the rerun is \\emph{reproduction}:','The first completed task was \\emph{reproduction}:')
    text=text.replace('All 18 settings scored 1.0000 mean Macro-F1 in the stored grouped grid, so the winning parameter choice is \\emph{not} proven intrinsically superior.','The grouped grid is selected by mean Macro-F1 with deterministic tie handling; observed scores and their interpretation are reported in Chapter~4.')
    # Remove outcome-specific paragraph from statistical method; results are in Chapter 4.
    start=text.find('The already saved synthetic-test confusion counts permit reconstruction')
    end=text.find('A Friedman test would concern',start)
    if start>=0 and end>=0:text=text[:start]+'Actual paired predictions, contingency counts and interpretations are reported in Chapter~4. The repeated historical test is not a new independent test. '+text[end:]
    insert=r'''
\section{Executed Rerun Environment and Separate Candidate Protocol}
The completed reproduction used Python 3.13.5, scikit-learn 1.8.0, NumPy 2.4.4, SciPy 1.17.1, pandas 3.0.2, Matplotlib 3.11.2 and joblib 1.5.3 on Windows AMD64. The workstation specifications earlier in this chapter are supplied historical specifications rather than independently measured hardware claims. Seed 20261026 was retained. The source SHA-256 was verified before and after execution, and original outputs were preserved before rerunning extracted copies. The local portable input is \path{data/Barangay_Complaint_Dataset_24000.csv}. Only \texttt{complaint\_text} enters the predictor; metadata remain excluded.

Historical reference text is passed directly to the saved scikit-learn vectorizer: default lowercasing/tokenization, no stopword removal, word n-grams, sublinear term frequency, smooth inverse document frequency and L2 normalization. The demo script's URL/punctuation-stripping helper was not retroactively inserted into the reference. The baseline uses unigrams/bigrams, \texttt{min\_df=2}, \texttt{max\_df=0.95}, and MultinomialNB $\alpha=1$. The chosen SVM uses unigrams with the same frequency/weighting settings and LinearSVC $C=0.1$. This compares complete pipelines with differing feature ranges.

After original reproduction, a single fixed combined-feature candidate applies Unicode NFKC, casefolding and whitespace normalization, without removing negations, Unicode accents, URLs or punctuation beforehand. Word TF--IDF uses $(1,2)$ n-grams, \texttt{min\_df=2}, \texttt{max\_df=0.95}; character-within-word TF--IDF uses $(3,5)$ n-grams, \texttt{min\_df=3} and a 45,000-feature cap. Both branches use sublinear weighting and default L2 normalization; their equally weighted sparse matrices are concatenated before LinearSVC $C=0.1$. No new candidate hyperparameter search was performed.

The calibrated candidate uses \texttt{CalibratedClassifierCV(method=sigmoid, ensemble=True)} with three precomputed \texttt{StratifiedGroupKFold} training-only splits. Each base feature pipeline is fitted inside its own fit fold, with its disjoint held-out group fold used for sigmoid fitting. Validation evaluates the ensemble; it never fits vocabulary, classifier or calibrator. The existing validation set is a development comparison, not new external confirmation. Candidate test evaluation was deliberately excluded. Log loss, multiclass Brier score (sum over classes), and ten equal-width confidence-bin expected calibration error describe development probability reliability. Report scores do not establish field-calibrated probabilities.

All final experimental figures are reproducibly generated from actual outputs at 360 DPI as PNG and also exported as vector PDF/SVG. CSV predictions and fold records remain machine-readable audit evidence, not the final evaluation presentation. The manuscript and standalone report use figures and academic tables with LaTeX captions and labels.
'''
    text+=insert
    text+=r'\par Macro-precision and macro-recall are $P_{\mathrm{macro}}=\frac{1}{3}\sum_c P_c$ and $R_{\mathrm{macro}}=\frac{1}{3}\sum_c R_c$. With no discordant pairs, the paired statistic is set to zero and the exact p-value to one.'+'\n'
    path.write_text(text,encoding='utf-8')
    path=SRC/'chapters/experiment_methodology.tex';extra=original(path)
    extra=extra.replace('tuned the baseline and SVM on the training partition','fitted the fixed baseline and tuned the SVM on the training partition')
    path.write_text(extra,encoding='utf-8')
    path=SRC/'chapters/operational_workflows.tex';text=original(path)
    text=text.replace('a \\emph{candidate to be tested}','a \\emph{separately evaluated development candidate}')
    text=text.replace('Rejected/Closed','Rejected')
    text=text.replace('The proposed combined word/character representation, calibrated probabilities, class-dependent administrative review, case-management controls and feedback-driven retraining require implementation and independent measurement before claims of production readiness.','The combined word/character representation and grouped sigmoid calibration were separately tested on existing synthetic development validation. Live probability reliability, class-dependent administrative review, case management and feedback-driven retraining still require independent implementation and measurement before production-readiness claims.')
    text=text.replace('Word baseline and separate exploratory character-only ablation.','Reference reproduction and separate combined-feature development experiment.')
    text=text.replace('Direct preregistered head-to-head experiment.','Independent external comparison beyond the synthetic ceiling.')
    text=text.replace('Literature and proposed decision policy, not measured deployment results.','Synthetic development calibration; HITL remains a proposed policy.')
    text=text.replace('Calibration metrics, reviewer reliability and false-Spam audits.','External probability reliability, reviewer agreement and Valid-sample audits.')
    text=text.replace('The three displayed class-probability quantities are therefore proposed outputs rather than metrics generated by the current uncalibrated SVM experiment','The three displayed class-probability quantities remain proposed operational outputs; the reference SVM is uncalibrated, while a separate candidate supplies synthetic development probability diagnostics in Chapter~4')
    # Replace the existing software-architecture image instead of adding a duplicate.
    text=text.replace('figures/system_integration_final.pdf','figures/verified/system_architecture.pdf')
    text+=r'''
\subsection{Detailed Full-Stack Implementation Plan}
The separately delivered roadmap defines the Next.js/TypeScript, FastAPI and PostgreSQL modules, REST schemas, versioned narrative/label/disposition/case tables, security controls, phased tests and acceptance gates. Figure~\ref{fig:op-system-integration} supplies the single software-integration overview; Figure~\ref{fig:verified-db} gives the complementary relational model. These are implementation plans, not validation of the existing SQLite/static-HTML prototype. Direct Valid routing records policy-based acceptance but never creates a human-verified label. Urgent human handling is independent of predicted class. The full database cardinalities and editable diagram sources accompany the roadmap.
'''
    text+=r'The relational design links immutable narrative versions to separate predictions and verified labels; accepted dispositions alone create cases. Append-only action and audit histories preserve the distinction between machine outputs and administrative decisions.'+'\n'
    text+=figure('database_overview','Proposed logical relational overview; full keys, constraints, indices and cardinalities are supplied with the roadmap.','fig:verified-db',height='.70')
    path.write_text(text,encoding='utf-8')
    path=SRC/'chapters/conclusions_and_recommendations.tex';text=original(path)
    text=text.replace('Before field deployment, independently test the combined word/character feature candidate, probability calibration and class-based review queue;','The combined word/character feature candidate and grouped sigmoid calibration have now been evaluated on existing synthetic development data only, tying the reference classifier without demonstrated classification improvement. Before field deployment, independently validate transfer and probability reliability and implement/test the class-based review queue;')
    text=text.replace('No results for these trials are asserted in the present manuscript.','No prospective feedback-checkpoint or operational HITL results are asserted in the present manuscript.')
    text=text.replace('The reported group-disjoint cross-validation and fixed validation results are high,','The principal historical results were reproduced: SVM validation/test Macro-F1 remained 1.000000 and baseline Macro-F1 was 0.992077/0.991624. A separate combined-feature candidate tied SVM on development validation; no classification improvement was demonstrated. The group-disjoint cross-validation and fixed validation results are high,')
    path.write_text(text,encoding='utf-8')
    path=SRC/'main.tex';text=original(path)
    text=text.replace('The study proposes meaning-preserving preprocessing, combined word/character features, probability-calibrated inference, administrator verification, accountable case management and controlled offline feedback as future operational components. These extensions have not been validated by the reported word-level SVM experiments and require distinct implementation and end-to-end testing.','The historical metrics were successfully reproduced on the unchanged corpus. A separate meaning-preserving word/character candidate, with and without grouped sigmoid calibration, tied the reference at 1.0000 development validation Macro-F1; no classification improvement was demonstrated and no candidate test evaluation was performed. Probability reliability outside the synthetic development distribution, administrator verification, accountable case management and controlled offline feedback require independent validation and end-to-end implementation testing.')
    path.write_text(text,encoding='utf-8')
    # Standalone report reuses actual figures and generated result prose/tables.
    manifest_path=SRC/'EXPERIMENT_MANIFEST.json'
    manifest=json.loads(original(manifest_path))
    manifest.update({'historical_environment_note':'Original versions preserved in evidence/historical; rerun versions differ as documented.',
        'rerun_environment':env,'proposed_combined_word_character_model_evaluated':True,
        'candidate_scope':'existing development validation only; no candidate test evaluation',
        'probability_calibration_executed':True,'operational_calibration_reliability_established':False,
        'synthetic_test_reproduced':True,'live_HITL_validated':False,'feedback_retraining_demonstrated':False})
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    readme=SRC/'README.md';original(readme)
    readme.write_text('''# Revised verified thesis project

Entry point: `main.tex`; engine: pdfLaTeX. Upload the ZIP contents into Overleaf and compile. This source is self-contained: all referenced figures and citations are included. The separately delivered PDF is `Thesis2_Verified_Manuscript.pdf`.

The unchanged corpus hash is `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28`. Original 18-configuration grouped experiments and five-fold grouped validation were executed and reproduced. Chapter 4 distinguishes the repeated historical synthetic test from development validation and the separate combined-feature/calibrated candidate. No independent field or HITL validation is claimed.

Final result images in `figures/verified/` are vector PDFs generated from actual executed outputs. The accompanying full research project supplies 360-DPI PNG, vector PDF/SVG, scripts, exact dependencies, prediction evidence and logs. CSVs are internal evidence and dataset files, not the final evaluation presentation.

Original supplied result files/source baselines are preserved in the full project's `evidence/historical/`; files under this extracted project's results/validation folders reflect the rerun. The remaining older changelogs/manifests describe prior stages; the updated `EXPERIMENT_MANIFEST.json`, final chapters and full-project change log define current scope. Legacy generator/update utilities are not needed to compile and should not be run to reproduce the unchanged corpus.

Research-only candidate features/calibration were evaluated on the existing synthetic development set, tying the reference classifier. Operational probability reliability, resident authentication, administrator workflow, case management and feedback-driven retraining remain implementation/validation work.
''',encoding='utf-8')
    report=ROOT/'output/pdf';report.mkdir(parents=True,exist_ok=True)
    body=ch.replace(r'\chapter{Results and Discussion}',r'\section*{Executed Findings and Evidence Scope}')
    body=body.replace('figures/verified/', '../../results/figures/')
    pre=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern,microtype}
\usepackage[margin=.8in]{geometry}
\usepackage{graphicx,float,booktabs,tabularx,array,amsmath}
\usepackage[hidelinks]{hyperref}\usepackage{xurl}
\setlength{\emergencystretch}{3em}
\title{Machine-Learning Evaluation Report\\\large Barangay Complaint Classification: Verified Reproduction}
\author{Research artifact based on the supplied thesis project}
\date{26 October 2026}
\begin{document}\maketitle
\noindent\textbf{Primary metric:} Macro-F1. Corpus: 24,000 unchanged synthetic, unreviewed narratives. Reference models: TF--IDF/Linear SVM and TF--IDF/Multinomial Naive Bayes. Candidate models are separate development experiments. Figures are available as 360-DPI PNG and vector PDF/SVG.
\section*{Experimental Configuration}
Seed 20261026; training/validation/historical test = 19,213/2,399/2,388. Python 3.13.5; scikit-learn 1.8.0; NumPy 2.4.4; SciPy 1.17.1; pandas 3.0.2; Matplotlib 3.11.2; joblib 1.5.3. Reference SVM: word unigrams, min\_df 2, max\_df .95, sublinear TF, LinearSVC C=.1; NB: word unigrams/bigrams, same frequency/weighting settings, alpha=1. Three-fold grouped search evaluates 18 combinations, followed by separate five-fold grouped stability assessment. Only training records fit vocabulary and model parameters. Dataset SHA-256: \path{35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28}.
\par Paired McNemar statistic is $\max(0,|b-c|-1)^2/(b+c)$ when $b+c>0$; exact p uses a two-sided Binomial$(b+c,0.5)$ test. Here b is baseline-only correct and c is SVM-only correct. With no discordance, statistic=0 and p=1. Family dependence limits inferential interpretation.
'''
    (report/'evaluation_report.tex').write_text(pre+body+'\n\\end{document}\n',encoding='utf-8')
    from finalize_milestone2 import apply_revision
    apply_revision()
    print('Prepared manuscript edits, copied vector figures and generated standalone report source.')


if __name__=='__main__':main()
