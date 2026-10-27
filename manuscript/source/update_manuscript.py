from pathlib import Path
import re
P=Path(__file__).resolve().parent
ch=P/'chapters'
path=ch/'methodology.tex'; t=path.read_text()
# remove old duplicated operational figures, preserve distinct dataset/evaluation and conceptual diagrams
for label in ['fig:live','fig:ml-integration','fig:architecture','fig:state']:
    pattern=r'\\begin\{figure\}\[p\][^\n]*\\label\{'+re.escape(label)+r'\}\\end\{figure\}'
    t,n=re.subn(pattern,'',t,flags=re.S)
    if n!=1: print('WARN removal',label,n)
# replace obsolete paragraphs referencing removed figs
start=t.index('The proposed operational system consists of')
stop=t.index('\\input{chapters/data_description_and_eda.tex}',start)
t=t[:start]+r'''The proposed operational system separates resident input, inference, administrative review, case management, and controlled model maintenance. A resident-facing form collects a required Subject and Complaint Details narrative; incident date/time and Purok/Sitio or an identifying landmark are supporting contextual fields when known. Geographic maps, GPS capture and photographic uploads are outside the selected core thesis scope. The application concept uses an authenticated resident interface and an authorized staff interface; the suggested software stack is Next.js/TypeScript, FastAPI and PostgreSQL, but implementation claims require working source code and testing. No completed user-interface or government-office deployment evaluation is included in the supplied experimental evidence.

The class-prediction output is separate from the administrative disposition. Predicted Valid goes to the accepted-case workflow under the selected routing rule; predicted Suspicious or Spam goes to administrator review. Acceptance, clarification, and rejection are decisions about the submission, not automatic replacements for the text label. Proposed controls include resident status tracking, staff action logs, deadline monitoring, referrals, verification before resolution, and a reconsideration mechanism. Detailed proposed figures and the experimental--operational boundary are presented later in this chapter.

'''+t[stop:]
start=t.index('\\section{System Architecture, Operational Framework and Complaint State Machine}')
stop=t.index('\\section{Research Ethics, Reproducibility and Limitations}',start)
t=t[:start]+r'''\section{System Architecture and Operational Boundary}
The proposed system distinguishes a researcher-evaluated word-level TF--IDF/SVM baseline from a planned operational architecture that adds privacy-aware input preparation, word-plus-character features, calibrated probabilities, class-based HITL review, accepted-case management and controlled retraining. The measured model scores are not evidence that the additional production functions are already implemented or validated. Section~\ref{sec:proposed-operational-workflows} defines these interfaces, states and non-automatic feedback processes. System-level monitoring and administrator accountability are application requirements to be evaluated separately from classifier accuracy.

\input{chapters/operational_workflows.tex}

'''+t[stop:]
# method section preserves actual experiments, states feature extension
needle='Both operate solely on normalized complaint text. A \\texttt{Pipeline} fits the vectorizer within each training fold to avoid using validation or test vocabulary in training estimators \\cite{sklearn}.'
replacement=needle+r''' The recorded selected SVM uses word unigrams; an isolated exploratory character 3--5-gram model was evaluated later as an ablation. The combined word-unigram/bigram plus character-within-word 3--5-gram representation illustrated in the proposed workflow is a \emph{candidate extension}, not the feature set producing the reported SVM results. Similarly, the reported baseline does not supply fitted calibrated class probabilities. A calibrated pipeline is required and must be independently evaluated before confidence-guided administrative prioritization can operate.'''
t=t.replace(needle,replacement)
path.write_text(t)
# remove duplicate diagrams in literature review
lit=ch/'literature_review.tex'; s=lit.read_text()
s=re.sub(r'\\begin\{figure\}\[H\]\s*\\centering\s*\\includegraphics\[width=0\.97\\textwidth\]\{figures/nlp_pipeline_readable\.pdf\}\s*\\caption\{.*?\}\\end\{figure\}',r'The selected proposed preprocessing workflow is specified separately in Section~\\ref{sec:proposed-operational-workflows}, without introducing a second overlapping figure.',s,flags=re.S)
s=re.sub(r'\\begin\{figure\}\[H\]\s*\\centering\s*\\includegraphics\[width=0\.76\\textwidth\]\{figs/tfidf_flow\.png\}\s*\\caption\{.*?\}\\end\{figure\}',r'The experimental word-vector baseline and the proposed combined-feature extension are distinguished explicitly in Section~\\ref{sec:proposed-operational-workflows}.',s,flags=re.S)
s=s.replace('In this study, when barangay administrators correct system-generated classifications, the intended workflow records these corrections for adjudication and possible future offline retraining.', 'In the planned deployment, when barangay administrators correct system-generated classifications, the workflow would record version-specific corrections for quality review and possible future offline retraining.')
lit.write_text(s)
# fix optimistic introduction phrasing
intro=ch/'introduction.tex'; s=intro.read_text()
s=s.replace('enabling continuous model improvement through administrative feedback','proposing a testable route for administrator-verified feedback and controlled future model improvement')
s=s.replace('This enhances system accountability, transparency, and overall process management.','This is intended to support accountability and transparency through traceable administrative actions; operational gains have not yet been demonstrated.')
s=s.replace('by reducing manual workload and improving consistency in complaint processing, while also enhancing citizen experience through faster and more transparent complaint handling.','by potentially improving the traceability of administrative decisions; reductions in manual workload and processing time require separate field evaluation.')
intro.write_text(s)
# correct abstract and scope of unimplemented extensions
main=P/'main.tex'; s=main.read_text()
s=s.replace('The study proposes administrator verification and controlled offline feedback as safeguards; their effectiveness requires separate end-to-end testing.', 'The study proposes meaning-preserving preprocessing, combined word/character features, probability-calibrated inference, administrator verification, accountable case management and controlled offline feedback as future operational components. These extensions have not been validated by the reported word-level SVM experiments and require distinct implementation and end-to-end testing.')
main.write_text(s)
# conclusions
concl=ch/'conclusions_and_recommendations.tex'; s=concl.read_text()
s=s.replace('\\section{Concluding Statement}',r'''\subsection{Accountable Case Management and Scope Boundaries}
The proposed accepted-case workflow separates Unresolved, Ongoing and Resolved administrative statuses from Valid, Suspicious and Spam model predictions. It recommends a case tracking reference, responsible officer assignment, activity log, policy-specific response target, supervisor notification of overdue events, referral tracking, evidence review before closure and resident reconsideration. These are auditable system-design requirements rather than measured improvements in governmental response or verified legal compliance. Response duties under Republic Act No.~6713 and service-specific processing standards under Republic Act No.~11032 must be interpreted through the applicable Citizen's Charter; no universal deadline for complete incident resolution is assumed \cite{ra6713,ra11032,dcr}.

Optional image attachments, image classification, multimodal fusion, GPS maps and automated authenticity detection are deliberately deferred. A supporting location description can be requested where necessary without requiring GPS. The text-only SVM is not capable of independently deciding whether a physical incident occurred, whether an image is authentic, or whether a complaint was resolved.

\subsection{Evaluation of Proposed Extensions}
Before field deployment, independently test the combined word/character feature candidate, probability calibration and class-based review queue; conduct a double-annotation pilot and a representative audit of predicted Valid reports; evaluate a complete case-management prototype; and compare cumulative verified-feedback checkpoints of 100, 250 and 500 only if authentic, quality-checked labels are actually collected. These are experimental checkpoints, not guaranteed improvement thresholds \cite{figueroa2012,ghose2024,fleisig2024}. No results for these trials are asserted in the present manuscript.

\section{Concluding Statement}''')
concl.write_text(s)
print('updated base files')
