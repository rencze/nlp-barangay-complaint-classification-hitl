"""Milestone 3: independent additional validation on training + fixed validation only.
No final test split used. CV folds are group-disjoint and TF-IDF is fitted afresh per fold.
"""
import json, sys, pathlib, time
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, confusion_matrix, classification_report

ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'validation_suite'; FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
LABELS=['Valid','Suspicious','Spam']; SEED=20261026
DATA=ROOT/'data'/'ALL_SYNTHETIC_V2.csv'
allrows=pd.read_csv(DATA).fillna('');train=allrows[allrows.split=='train'].reset_index(drop=True);val=allrows[allrows.split=='validation'].reset_index(drop=True)
assert len(allrows)==24000 and len(train)==19213 and len(val)==2399
assert not set(train.scenario_family_id)&set(val.scenario_family_id)
X=train.complaint_text.astype(str).to_numpy();y=train.classification.to_numpy();groups=train.scenario_family_id.to_numpy()
XV=val.complaint_text.astype(str).to_numpy();YV=val.classification.to_numpy()
models={
 'TF-IDF + Linear SVM':lambda:Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,1),min_df=2,max_df=.95,sublinear_tf=True)),('svm',LinearSVC(C=.1,max_iter=5000,random_state=SEED))]),
 'TF-IDF + Naive Bayes':lambda:Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=2,max_df=.95,sublinear_tf=True)),('nb',MultinomialNB(alpha=1.0))]),
}
cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED)
folds=list(cv.split(X,y,groups)); rows=[];group_rows=[]
for f,(it,iv) in enumerate(folds,1):
 a,b=set(groups[it]),set(groups[iv]);assert a.isdisjoint(b)
 group_rows.append(dict(fold=f,train_records=len(it),heldout_records=len(iv),train_families=len(a),heldout_families=len(b),overlapping_families=len(a&b),**{'heldout_'+lab.lower():int(sum(y[iv]==lab)) for lab in LABELS}))
 for name,constructor in models.items():
  start=time.time();m=constructor();m.fit(X[it].tolist(),y[it]);pred=m.predict(X[iv].tolist());pt=m.predict(X[it].tolist())
  rows.append(dict(model=name,fold=f,training_n=len(it),cv_n=len(iv),train_accuracy=accuracy_score(y[it],pt),train_macro_f1=f1_score(y[it],pt,average='macro'),cv_accuracy=accuracy_score(y[iv],pred),cv_macro_f1=f1_score(y[iv],pred,average='macro'),duration_sec=round(time.time()-start,2)))
  print(name, f, 'F1',round(rows[-1]['cv_macro_f1'],5),'seconds',rows[-1]['duration_sec'],flush=True)
pd.DataFrame(rows).to_csv(OUT/'five_fold_grouped_cv_results.csv',index=False)
pd.DataFrame(group_rows).to_csv(OUT/'five_fold_partition_audit.csv',index=False)
agg=pd.DataFrame(rows).groupby('model').agg(train_f1_mean=('train_macro_f1','mean'),cv_f1_mean=('cv_macro_f1','mean'),cv_f1_sample_sd=('cv_macro_f1','std'),cv_accuracy_mean=('cv_accuracy','mean'),total_fit_seconds=('duration_sec','sum')).reset_index()
agg.to_csv(OUT/'five_fold_grouped_cv_summary.csv',index=False)
validrows=[];predrows=[]; perclass=[];sub=[];mat={}
for name,fn in models.items():
 m=fn().fit(X.tolist(),y)
 yp=m.predict(XV.tolist());mat[name]=confusion_matrix(YV,yp,labels=LABELS).tolist()
 p,r,f,s=precision_recall_fscore_support(YV,yp,labels=LABELS,zero_division=0)
 validrows.append(dict(model=name,validation_n=len(YV),accuracy=accuracy_score(YV,yp),macro_precision=np.mean(p),macro_recall=np.mean(r),macro_f1=np.mean(f),misclassified=int(np.sum(yp!=YV))))
 for i,cl in enumerate(LABELS):perclass.append(dict(model=name,classification=cl,precision=p[i],recall=r[i],f1=f[i],support=s[i]))
 for lan in ['Bisaya','Filipino','English','Mixed']:
  ix=(val.language_group.to_numpy()==lan); sub.append(dict(model=name,language_group=lan,n=int(ix.sum()),accuracy=accuracy_score(YV[ix],yp[ix]),macro_f1=f1_score(YV[ix],yp[ix],average='macro')))
 for i,(truth,guess) in enumerate(zip(YV,yp)):
  predrows.append(dict(model=name,record_id=val.loc[i,'record_id'],classification=truth,prediction=guess,correct=truth==guess,language_group=val.loc[i,'language_group'],category_id=val.loc[i,'category_id'],complaint_text=XV[i]))
pd.DataFrame(validrows).to_csv(OUT/'validation_summary.csv',index=False)
pd.DataFrame(perclass).to_csv(OUT/'validation_per_class.csv',index=False)
pd.DataFrame(sub).to_csv(OUT/'validation_by_language.csv',index=False)
pd.DataFrame(predrows).to_csv(OUT/'validation_predictions.csv',index=False)
(OUT/'validation_confusion_matrices.json').write_text(json.dumps(mat,indent=2))
# intentionally simplistic surface-only diagnostic; no text words used (validation only)
def lengths(z):return np.array([[len(t.split()),len(t)] for t in z],dtype=float)
len_model=Pipeline([('scale',StandardScaler()),('logit',LogisticRegression(max_iter=1200,random_state=SEED))]);len_model.fit(lengths(X),y)
lp=len_model.predict(lengths(XV)); length=dict(n=len(YV),accuracy=float(accuracy_score(YV,lp)),macro_f1=float(f1_score(YV,lp,average='macro')),confusion_matrix=confusion_matrix(YV,lp,labels=LABELS).tolist())
(OUT/'length_only_validation.json').write_text(json.dumps(length,indent=2))
# exploratory character ngrams model, evaluation is diagnostic NOT tuned final SVM
cm=Pipeline([('tfidf',TfidfVectorizer(analyzer='char',ngram_range=(3,5),min_df=3,max_features=45000,sublinear_tf=True)),('svm',LinearSVC(C=.1,max_iter=5000,random_state=SEED))]);cm.fit(X.tolist(),y);cp=cm.predict(XV.tolist())
char=dict(n=len(YV),accuracy=float(accuracy_score(YV,cp)),macro_f1=float(f1_score(YV,cp,average='macro')),confusion_matrix=confusion_matrix(YV,cp,labels=LABELS).tolist())
(OUT/'character_ngram_exploratory_validation.json').write_text(json.dumps(char,indent=2))
# readability: colorblind-compatible palette / vector + png figures, no truncated labels
plt.rcParams.update({'font.size':11,'axes.titlesize':14,'axes.labelsize':11,'legend.fontsize':10,'figure.figsize':(8.3,5.3),'savefig.bbox':'tight','savefig.pad_inches':.18,'pdf.fonttype':42})
def savefig(name):
 plt.savefig(FIG/(name+'.pdf'));plt.savefig(FIG/(name+'.png'),dpi=220);plt.close()
# 5 fold train and validation f1 combined
frame=pd.DataFrame(rows);fig,ax=plt.subplots()
for nm,marker,ls in [('TF-IDF + Linear SVM','o','-'),('TF-IDF + Naive Bayes','s','--')]:
 z=frame[frame.model==nm];ax.plot(z.fold,z.cv_macro_f1,marker=marker,linestyle=ls,label=nm+' (held-out fold)',linewidth=2,markersize=7)
ax.set_xticks([1,2,3,4,5]);ax.set_ylim(max(.85,min(frame.cv_macro_f1)-.012),1.006);ax.set_xlabel('Fold');ax.set_ylabel('Held-out Macro-F1');ax.set_title('Five-fold grouped cross-validation on training data');ax.grid(alpha=.2);ax.legend(loc='lower left');fig.tight_layout();savefig('m3_grouped_fivefold_scores')
# fold group sizes
fgr=pd.DataFrame(group_rows);fig,ax=plt.subplots();ax.bar(fgr.fold-.18,fgr.heldout_records,width=.36,label='Records');ax.set_xlabel('Fold');ax.set_ylabel('Held-out records');ax.set_xticks(range(1,6));ax.set_title('Five-fold held-out partition sizes');ax.legend();fig.tight_layout();savefig('m3_folds_sizes')
# CV summary bars
fig,ax=plt.subplots(figsize=(8.2,5));xpos=np.arange(2);xs=pd.DataFrame(rows).groupby('model').cv_macro_f1.agg(['mean','std']).reindex(list(models));b=ax.bar(xpos,xs['mean'],yerr=xs['std'].fillna(0),capsize=7,width=.54);ax.set_xticks(xpos,['Linear SVM','Naive Bayes']);ax.set_ylim(0,1.08);ax.set_title('Five-fold grouped CV: mean and standard deviation');ax.set_ylabel('Macro-F1');
for i,v in enumerate(xs['mean']):ax.text(i,v+.009,f'{v:.4f}',ha='center',fontweight='bold')
fig.tight_layout();savefig('m3_cv_comparison')
# confusion matrices
for nm,key in [('TF-IDF + Linear SVM','svm'),('TF-IDF + Naive Bayes','nb')]:
 arr=np.array(mat[nm]);fig,ax=plt.subplots(figsize=(7.5,5.3));im=ax.imshow(arr,cmap='Blues',vmin=0,vmax=850)
 for i in range(3):
  for j in range(3):ax.text(j,i,str(arr[i,j]),ha='center',va='center',fontsize=15,color='white' if arr[i,j]>500 else 'black')
 ax.set_xticks(range(3),LABELS);ax.set_yticks(range(3),LABELS);ax.set_xlabel('Predicted classification');ax.set_ylabel('True classification');ax.set_title('Validation confusion matrix — '+('Linear SVM' if key=='svm' else 'Naive Bayes'));fig.colorbar(im,ax=ax,label='Number of records');fig.tight_layout();savefig('m3_validation_confusion_'+key)
# language subgroup f1 grouped bar
sd=pd.DataFrame(sub);fig,ax=plt.subplots(figsize=(9.1,5.3));xx=np.arange(4);bw=.34
for i,nm in enumerate(models):
 ys=sd[sd.model==nm].set_index('language_group').loc[['Bisaya','Filipino','English','Mixed']].macro_f1
 ax.bar(xx+(i-.5)*bw,ys,width=bw,label=nm)
ax.set_xticks(xx,['Bisaya','Filipino','English','Mixed']);ax.set_ylim(0,1.08);ax.set_ylabel('Validation Macro-F1');ax.set_title('Performance by assigned language group');ax.legend(loc='lower left');fig.tight_layout();savefig('m3_language_subgroups')
# validation compared with length-only, char diagnostic
names=['Length/characters only','Naive Bayes word TF-IDF','Linear SVM word TF-IDF','Character n-gram SVM'];scores=[length['macro_f1'],validrows[1]['macro_f1'],validrows[0]['macro_f1'],char['macro_f1']];fig,ax=plt.subplots(figsize=(9,5.4));bars=ax.barh(names,scores);ax.set_xlim(0,1.10);ax.set_xlabel('Validation Macro-F1');ax.set_title('Diagnostic feature ablation (not a final model ranking)')
for i,score in enumerate(scores):ax.text(score+.01,i,f'{score:.4f}',va='center')
fig.tight_layout();savefig('m3_feature_ablation')
# Fold plan graphic, adaptive layout in matplotlib vector
from matplotlib.patches import Rectangle
fig,ax=plt.subplots(figsize=(11,3.1));cols=['#D9EAF5','#E7E7E7'];
for i in range(5):
 for k in range(5):
  rect=Rectangle((k,i),.91,.82,facecolor=cols[0 if k==i else 1],edgecolor='#909090');ax.add_patch(rect)
  ax.text(k+.455,i+.4,'CV' if k==i else 'Train',ha='center',va='center',fontsize=11)
ax.set_xlim(-.05,5.08);ax.set_ylim(5.1,-.2);ax.set_xticks(np.arange(5)+.455,['Group set 1','Group set 2','Group set 3','Group set 4','Group set 5']);ax.set_yticks(np.arange(5)+.41,['Fold 1','Fold 2','Fold 3','Fold 4','Fold 5']);ax.set_title('Five-fold grouped CV schematic (each scenario family stays in one group)');ax.tick_params(length=0);[sp.set_visible(False) for sp in ax.spines.values()];fig.tight_layout();savefig('m3_fold_design_diagram')
report={'training_n':len(train),'validation_n':len(val),'folds':group_rows,'cv':agg.to_dict(orient='records'),'validation':validrows,'length_only':length,'char_ngram_exploratory':char,'dataset_did_not_touch_test':True,'random_state':SEED,'protocol':'5 fold StratifiedGroupKFold over training only. Pipeline refits TF-IDF within fold; fixed validation partition used as diagnostics. No test data loaded for training or evaluation.'}
(OUT/'m3_validation_summary.json').write_text(json.dumps(report,indent=2))
print('FINAL SUMMARY:',json.dumps({'five_fold':report['cv'],'validation':validrows,'length':length,'char':char},indent=2),flush=True)
