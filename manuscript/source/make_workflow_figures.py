from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
out=root/'figures'
base='''digraph G {
 graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.36", ranksep="0.49", splines=ortho, compound=true, fontname="Liberation Serif", fontsize=16];
 node [shape=box, style="solid", color="black", penwidth=1.25, fontname="Liberation Serif", fontsize=13, margin="0.18,0.10"];
 edge [color="black", penwidth=1.15, arrowsize=.7, fontname="Liberation Serif", fontsize=11];
'''
flows={
'nlp_proposed':r'''
 input [shape=parallelogram,label="Input: Raw Complaint Narrative"];
 original [label="Create Privacy-Conscious ML Copy\\nRetain original securely; mask direct identifiers when feasible"];
 unicode [label="Unicode (NFC) and Whitespace Normalization"];
 lower [label="Lowercase ML Copy"];
 clean [label="Conservative Text Cleanup\\nRetain negation, meaningful terms, numbers and punctuation"];
 output [shape=parallelogram,label="Output: Preprocessed Narrative\\nTo TF-IDF Feature Extraction"];
 input->original->unicode->lower->clean->output;
 note [shape=note, fontsize=11, label="Selected design: no generic stopword deletion,\\nstemming or lemmatization."];
 output->note[style=dotted,arrowhead=none];
''',
'tfidf_proposed':r'''
 input[shape=parallelogram,label="Input: Preprocessed Complaint Narrative"];
 w [label="Word TF-IDF\\nUnigrams and bigrams"];
 c [label="Character TF-IDF\\n3--5 character n-grams (within word boundaries)"];
 concatenate [label="Concatenate Sparse Feature Matrices"];
 output[shape=parallelogram,label="Output: Combined Numerical TF-IDF Vector\\nTo SVM Prediction"];
 {rank=same; w;c};
 input->w;input->c;w->concatenate;c->concatenate;concatenate->output;
 foot [shape=note,fontsize=11,label="Fit vocabulary and IDF on training folds only;\\nreuse fitted transformers for new complaints."];
 output->foot[style=dotted,arrowhead=none];
''',
'svm_proposed':r'''
 train [label="Model Development (Offline)\\nFit TF-IDF; tune and train Linear SVM\\nCalibrate using disjoint training folds/data"];
 save [label="Validate and Version the Candidate Pipeline"];
 new [shape=parallelogram,label="Input: Combined TF-IDF Vector\\n(New complaint)"];
 apply [label="Apply Saved SVM and Calibrator\\nNo model fitting during prediction"];
 classify [label="Produce Three Calibrated Probabilities\\nP(Valid), P(Suspicious), P(Spam)"];
 choose [label="Assign Highest-Probability Text Label"];
 output [shape=parallelogram,label="Output: Predicted Class and Probability Vector\\nTo Class-Based Routing and HITL"];
 train->save [style=dashed];save->apply [style=dashed];new->apply->classify->choose->output;
''',
'hitl_proposed':r'''
 input [shape=parallelogram,label="Input: SVM Predicted Class and Class Probabilities"];
 route [shape=diamond,label="Predicted Suspicious\\nor Spam?"];
 routine [shape=parallelogram,label="Predicted Valid\\nTo Case Management"];
 inspect [label="Administrator Reviews Submission\\nOriginal narrative, prediction, supporting context"];
 verify [label="Verify or Correct Label of Text Version\\nValid / Suspicious / Spam"];
 decide [shape=diamond,label="Administrative\\nDisposition?"];
 accept [label="Accept\\nForward to Case Management"];
 clarify [label="Request Clarification\\nRecord pending review; assess response/deadline"];
 reject [label="Reject or Close\\nRecord reason under approved policy"];
 sufficient [shape=diamond,label="Sufficient basis\\nto proceed?"];
 fallback [label="Further Review / Documented Closure\\nNo automatic conversion to Spam"];
 output [shape=parallelogram,label="Reviewed Text Label and Decision Record\\nTo Feedback Quality Checking"];
 input->route;route->routine[label="No (Valid)"];route->inspect[label="Yes"];inspect->verify->decide;
 decide->accept[label="Accept"];decide->clarify[label="Clarify"];decide->reject[label="Reject"];
 clarify->sufficient;sufficient->accept[label="Yes"];sufficient->fallback[label="No"];
 verify->output[style=dashed];accept->output[style=dotted];reject->output[style=dotted];fallback->output[style=dotted];
''',
'retrain_proposed':r'''
 input [shape=parallelogram,label="Input: Human-Reviewed Text and Label Records"];
 quality [label="Verify Label Quality and Training Eligibility\\nVersion, deduplicate, check privacy and split family"];
 eligible [shape=diamond,label="Eligible for\\ntraining?"];
 audit [label="Archive for Review / Audit\\nExclude from training pool"];
 pool [label="Accumulate Verified Feedback Pool\\nCount unique cases and class coverage"];
 eligiblecheck [shape=diamond,label="Retraining justified\\nand authorized?"];
 wait [label="Keep Current Model\\nContinue feedback collection"];
 consolidate [label="Consolidate Authorized Training Dataset\\nExisting training data + new eligible examples"];
 train [label="Refit Preprocessing and TF-IDF\\nTrain Candidate Linear SVM and Recalibrate"];
 validate [label="Evaluate Candidate vs. Deployed Model\\nFixed validation set; macro-F1 and false-Spam safeguards"];
 pass [shape=diamond,label="Release criteria\\nmet?"];
 retain [label="Retain Deployed Pipeline\\nArchive unsuccessful candidate"];
 deploy [label="Approve, Version and Deploy Updated Pipeline\\nUse for future predictions only"];
 input->quality->eligible;eligible->audit[label="No"];eligible->pool[label="Yes"];
 pool->eligiblecheck;eligiblecheck->wait[label="No"];eligiblecheck->consolidate[label="Yes"];
 consolidate->train->validate->pass;pass->retain[label="No"];pass->deploy[label="Yes"];
''',
'case_proposed':r'''
 input [shape=parallelogram,label="Input: Accepted Complaint\\nSubject, narrative and relevant supporting details"];
 unresolved [label="Create Case and Acknowledge Resident\\nTracking reference; status: Unresolved"];
 assign [label="Assign Responsible Personnel\\nSet applicable response target"];
 ongoing [label="Investigate, Act and Log Progress\\nStatus: Ongoing; preserve time-stamped action history"];
 complete [shape=diamond,label="Action reported\\ncomplete?"];
 followup [label="Follow Up or Escalate\\nMonitor deadline; flag Overdue; refer if necessary"];
 verify [label="Verify Reported Completion\\nReview evidence and administrator sign-off"];
 confirmed [shape=diamond,label="Resolution\\nverified?"];
 notify [label="Notify Resident and Invite Feedback\\nProvide outcome and reconsideration channel"];
 dispute [shape=diamond,label="Outcome disputed\\nand reopening justified?"];
 resolve [shape=parallelogram,label="Status: Resolved\\nStore final audit trail and closure record"];
 reopen [label="Record Dispute and Reopen\\nReturn to Ongoing for additional action"];
 input->unresolved->assign->ongoing->complete;
 complete->followup[label="No"];followup->ongoing;
 complete->verify[label="Yes"];verify->confirmed;
 confirmed->followup[label="No"];confirmed->notify[label="Yes"];
 notify->dispute;dispute->resolve[label="No"];dispute->reopen[label="Yes"];reopen->ongoing;
''',
'integrated_proposed':r'''
 subgraph cluster_offline {label="Model Development / Controlled Updates (separate from each prediction)";style=dashed;
 dataset [label="Documented Synthetic Corpus\\n+ Independently Verified New Feedback"];
 training [label="Training and Evaluation\\nFit TF-IDF, Linear SVM; validate/calibrate"];
 release [label="Approved Versioned Model Bundle"];
 dataset->training->release;
 }
 subgraph cluster_live {label="Resident Submission and Operational Triage";style=dashed;
 submit [shape=parallelogram,label="Authenticated Resident Submission\\nSubject and Complaint Narrative"];
 prep [label="Privacy-Conscious NLP Preprocessing"];
 vector [label="TF-IDF Transformation\\nFitted word/character extractors"];
 infer [label="Saved Calibrated SVM\\nValid / Suspicious / Spam"];
 classcheck [shape=diamond,label="Predicted Suspicious\\nor Spam?"];
 hitl [label="HITL: Administrator Review\\nVerify text label; Accept / Clarify / Reject"];
 case [label="Case Management (Accepted Only)\\nUnresolved / Ongoing / Resolved"];
 feedback [label="Reviewed Text Labels + Outcome Log"];
 submit->prep->vector->infer->classcheck;
 classcheck->case[label="No: Valid"];classcheck->hitl[label="Yes"];
 hitl->case[label="Accepted"];hitl->feedback[label="Reviewed labels"];
 }
 release->infer [style=dashed,label="approved model"];
 feedback->dataset [style=dashed,label="quality checks, periodic authorized retraining",constraint=false];
'''
}
for name,content in flows.items():
    src=out/(name+'.dot');src.write_text(base+content+'\n}\n')
    cmd=['dot','-Tpdf',str(src),'-o',str(out/(name+'.pdf'))]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: print('ERROR',name,r.stderr)
    else: print(name,(out/(name+'.pdf')).stat().st_size)
