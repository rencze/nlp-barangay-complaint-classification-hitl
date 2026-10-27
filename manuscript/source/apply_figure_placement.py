from pathlib import Path
import re
r=Path(__file__).resolve().parent
chs=r/'chapters'
for p in chs.glob('*.tex'):
    s=p.read_text()
    s=s.replace(r'\begin{figure}[p]',r'\begin{figure}[H]')
    # ensure existing [htbp] floats do not go before their relevant description
    s=re.sub(r'\\begin\{figure\}\[(?:htbp|tbp|!htbp|!h|ht)\]',r'\\begin{figure}[H]',s)
    p.write_text(s)

p=chs/'operational_workflows.tex'
s=p.read_text()
s=s.replace('\\subsection{Integrated Application Architecture and Data Separation}', '\\subsection{End-to-End Integrated Complaint Workflow}')
old=r'''Figure~\ref{fig:op-integrated} connects the proposed resident flow, model inference, HITL routing, accepted-case processing and authorized offline updates. A training data record stores source type, text version, human-verified label, correction reason and split-family ID; a case record instead stores officer assignment, administrative disposition, deadlines, actions, evidence references and resolution status. A deployment record identifies the installed model, vectorizers and calibrator as one versioned bundle. User submission content and metadata should be retained and accessed in accordance with relevant privacy and security obligations. No diagram arrow from case resolution to the classification label is allowed, because factual outcomes are not automatically text ground truth \cite{ra10173,rottger2022,sklearnpitfalls,nist}.'''
new=r'''The integrated workflow in Figure~\ref{fig:op-integrated} links the previously described modules into one end-to-end account of proposed system behavior. A complaint narrative passes through conservative NLP preprocessing, saved word/character TF--IDF transformers and a calibrated SVM. Predicted Valid narratives proceed to accepted-case management; only predicted Suspicious or Spam narratives enter routine HITL for text-label verification and a separate administrative decision. Reviewed but non-accepted submissions retain a documented clarification or rejection outcome. \emph{Accepted} is an administrative state, not a replacement for the narrative label, while \emph{Resolved} is a later case-management state, not proof that an originally Suspicious sentence was Valid.

The diagram intentionally separates live case handling from the offline learning loop. Case records store assignment, action history, response deadlines and resolution outcomes, whereas versioned human-verified narrative labels are quality-checked before they can enter the training-feedback pool. Training a new TF--IDF--SVM candidate requires a justified and authorized retraining decision; the deployed classifier changes only after successful validation and release approval. In particular, neither an Accept click nor case resolution automatically updates model weights or training labels. These are proposed control boundaries, not additional observed results from the recorded synthetic-data baseline \cite{ra10173,rottger2022,sklearnpitfalls,nist}.'''
if old not in s: raise Exception('Expected old integration text missing')
s=s.replace(old,new)
s=s.replace('figures/integrated_proposed.pdf','figures/end_to_end_workflow.pdf')
s=s.replace('\\caption{Proposed integrated system architecture connecting resident submission, text-only inference, class-based HITL, accepted-case management and controlled offline updates. Dashed edges show model release and feedback flow rather than immediate retraining.}', '\\caption{Proposed end-to-end integrated workflow connecting resident submission, NLP, TF--IDF, SVM, class-specific human review, accepted-case processing and approved offline retraining. Dashed arrows distinguish training-feedback and approved model updates from live complaint handling.}')
s=s.replace('\\subsection{System Integration Architecture: Software Components and Data Boundaries}','\\subsection{Software Component Integration and Data Boundaries}')
s=s.replace('Figure~\\ref{fig:op-system-integration} complements the preceding end-to-end process figure with a \\emph{component-level} design.', 'After the end-to-end workflow, Figure~\\ref{fig:op-system-integration} presents the complementary \\emph{software component integration} and its access boundaries.')
s=s.replace('figures/system_integration_architecture.pdf','figures/system_integration_final.pdf')
# Explicitly state placement intent for future Overleaf edits.
s=s.replace('The diagrams contain descriptive titles only; formal figure numbering is provided by this manuscript\'s captions.', "Each diagram is placed immediately after the explanatory discussion of its named process; figure numbers are assigned by LaTeX captions rather than embedded in the graphics.")
p.write_text(s)

# separate the introduction to the two consecutive diagrams in the experiment section
p=chs/'experiment_methodology.tex'
s=p.read_text()
needle='The second diagram isolates the evaluation protocol and makes clear which partition is protected from use in model experiments.'
assert needle in s
s=s.replace(' '+needle,'')
marker=r'\begin{figure}[H]\centering\includegraphics[width=.94\textwidth,height=.78\textheight,keepaspectratio]{figures/diagram_cv_workflow.pdf}'
assert marker in s
s=s.replace(marker,'Figure~\\ref{fig:cv-protocol} separately illustrates the training-only model-selection protocol and identifies the protected evaluation partition. The validation workflow is shown immediately below, apart from the broader conceptual framework.\n'+marker)
p.write_text(s)

p=r/'README.md'
s=p.read_text()
s+='''\n\n## Figure placement and integrated diagrams (October 2026 revision)\n- All figure environments in the thesis chapters now use `[H]` so they occur immediately after their explanatory paragraphs instead of floating ahead or into a different section. When a tall diagram cannot fit after a paragraph, LaTeX moves the entire diagram to the next page without allowing later content to overtake it.\n- `figures/end_to_end_workflow.pdf` is the new integrated process diagram and has editable SVG source `figures/end_to_end_workflow.svg`, plus `diagram_sources/draw_integrated_workflow.py` for regeneration.\n- `figures/system_integration_final.pdf` separately shows proposed software components and information stores; both figures are distinct from the detailed NLP/TF-IDF/SVM/HITL/retraining/case diagrams.\n- Figure identifiers and numbers are printed as LaTeX captions, not inside the diagrams.\n'''
p.write_text(s)
print('Patched operational figures and all chapter placements')
