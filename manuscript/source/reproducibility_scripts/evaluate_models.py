#!/usr/bin/env python3
"""Reproducible V2 baseline, group-CV tuning, held-out evaluation and diagnostics."""
import csv,json,random,collections,pathlib,sys,statistics,time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV,StratifiedGroupKFold
from sklearn.metrics import (accuracy_score,f1_score,precision_recall_fscore_support,classification_report,confusion_matrix,hinge_loss)
from sklearn.linear_model import SGDClassifier,LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]
RES=ROOT/'results';FIG=ROOT/'figures';DATA=ROOT/'data';SEED=20261026
LABELS=['Valid','Suspicious','Spam']
def read(file):return list(csv.DictReader(open(file,encoding='utf-8')))
def write_csv(path,rows):
    if not rows:return
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def simple_metrics(model,X,y):
    yp=model.predict(X)
    p,r,f,_=precision_recall_fscore_support(y,yp,labels=LABELS,zero_division=0)
    return {'n':len(y),'accuracy':round(float(accuracy_score(y,yp)),6),'macro_f1':round(float(f1_score(y,yp,average='macro')),6),
       'weighted_f1':round(float(f1_score(y,yp,average='weighted')),6),
       'precision_macro':round(float(np.mean(p)),6),'recall_macro':round(float(np.mean(r)),6),
       'confusion_matrix':confusion_matrix(y,yp,labels=LABELS).tolist(),
       'per_class':{LABELS[i]:{'precision':round(float(p[i]),6),'recall':round(float(r[i]),6),'f1':round(float(f[i]),6)} for i in range(3)}}
def plot_heat(matrix,name):
    fig,ax=plt.subplots(figsize=(6.2,5))
    im=ax.imshow(matrix,cmap='Blues');ax.set_xticks(range(3),LABELS);ax.set_yticks(range(3),LABELS)
    for i in range(3):
        for j in range(3):ax.text(j,i,str(matrix[i][j]),ha='center',va='center',color='white' if matrix[i][j]>max(map(max,matrix))/2 else 'black',fontsize=10)
    ax.set_xlabel('Predicted class');ax.set_ylabel('True class');ax.set_title(name);fig.colorbar(im,ax=ax,fraction=.04,pad=.04)
    fig.tight_layout();fig.savefig(FIG/(name.lower().replace(' ','_')+'.png'),dpi=155);plt.close(fig)
def main():
    train=read(DATA/'TRAIN_SYNTHETIC_V2.csv');valid=read(DATA/'VALIDATION_SYNTHETIC_V2.csv');test=read(DATA/'TEST_SYNTHETIC_V2.csv')
    print('Loaded',len(train),len(valid),len(test),flush=True)
    XT=[x['complaint_text'] for x in train];YT=np.array([x['classification'] for x in train]);
    XV=[x['complaint_text'] for x in valid];YV=np.array([x['classification'] for x in valid]);
    XE=[x['complaint_text'] for x in test];YE=np.array([x['classification'] for x in test]);
    groups=np.array([x['scenario_family_id'] for x in train]);
    assert set(x['scenario_family_id'] for x in train).isdisjoint(set(x['scenario_family_id'] for x in valid))
    assert set(x['scenario_family_id'] for x in test).isdisjoint(set(x['scenario_family_id'] for x in valid))
    assert set(x['scenario_family_id'] for x in train).isdisjoint(set(x['scenario_family_id'] for x in test))
    import joblib
    # Baseline fitted and evaluated independently (validation used for tuning; test final only).
    nb=Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=2,max_df=.95,sublinear_tf=True)),('nb',MultinomialNB(alpha=1.0))]);nb.fit(XT,YT)
    nbv=simple_metrics(nb,XV,YV)
    print('NB validation',nbv['macro_f1'],flush=True)
    # Common documented SVM 18 config study, grouped CV for nonoverlapping family folds.
    estimator=Pipeline([('tfidf',TfidfVectorizer(max_df=.95,sublinear_tf=True)),('svm',LinearSVC(max_iter=5000,random_state=SEED))])
    param={'tfidf__ngram_range':[(1,1),(1,2)],'tfidf__min_df':[2,5,10],'svm__C':[.1,1.,10.]}
    cv=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=SEED)
    gs=GridSearchCV(estimator,param,scoring='f1_macro',cv=cv,n_jobs=1,refit=True,return_train_score=True,verbose=0)
    gs.fit(XT,YT,groups=groups)
    params=gs.best_params_;svm=gs.best_estimator_
    joblib.dump(svm,RES/'linear_svm_v2_research_only.joblib')
    joblib.dump(nb,RES/'multinomial_nb_v2_research_only.joblib')
    svmv=simple_metrics(svm,XV,YV)
    print('SVM validation',svmv['macro_f1'], 'params',params,flush=True)
    grid_rows=[]
    for i in range(len(gs.cv_results_['params'])):
        row={'ngram':str(gs.cv_results_['params'][i]['tfidf__ngram_range']),
             'min_df':gs.cv_results_['params'][i]['tfidf__min_df'],
             'C':gs.cv_results_['params'][i]['svm__C'],
             'cv_mean_macro_f1':round(float(gs.cv_results_['mean_test_score'][i]),6),
             'cv_sd_macro_f1':round(float(gs.cv_results_['std_test_score'][i]),6),
             'cv_mean_train_macro_f1':round(float(gs.cv_results_['mean_train_score'][i]),6)}
        grid_rows.append(row)
    write_csv(RES/'hyperparameter_grid_v2.csv',grid_rows)
    # training/validation learning behavior from 6 training fractions and fixed validation set.
    rng=np.random.RandomState(SEED)
    order=rng.permutation(len(XT)); learning=[]
    for frac in [.1,.2,.35,.5,.75,1.0]:
        sample=order[:int(frac*len(XT))]
        p=Pipeline([('tfidf',TfidfVectorizer(ngram_range=params['tfidf__ngram_range'],min_df=params['tfidf__min_df'],max_df=.95,sublinear_tf=True)),('svm',LinearSVC(C=params['svm__C'],max_iter=5000,random_state=SEED))]);p.fit([XT[i] for i in sample],YT[sample]);
        learning.append({'fraction':frac,'train_n':len(sample),'training_macro_f1':round(f1_score(YT[sample],p.predict([XT[i] for i in sample]),average='macro'),6),'validation_macro_f1':round(f1_score(YV,p.predict(XV),average='macro'),6)})
    write_csv(RES/'learning_curve_v2.csv',learning)
    # SGD approximation as a separate hinge-loss experiment, not the final LinearSVC optimizer.
    vectorizer=TfidfVectorizer(ngram_range=params['tfidf__ngram_range'],min_df=params['tfidf__min_df'],max_df=.95,sublinear_tf=True)
    vt=vectorizer.fit_transform(XT);vv=vectorizer.transform(XV)
    sgd=SGDClassifier(loss='hinge',alpha=.0001,learning_rate='constant',eta0=.002,max_iter=1,tol=None,random_state=SEED)
    loss_rows=[];shuffled=np.random.RandomState(SEED)
    for epoch in range(1,16):
        perm=shuffled.permutation(len(YT))
        sgd.partial_fit(vt[perm],YT[perm],classes=np.array(LABELS))
        # multiclass decision function, use hinge_loss as diagnostic surrogate
        tr_l=hinge_loss(YT,sgd.decision_function(vt),labels=LABELS)
        va_l=hinge_loss(YV,sgd.decision_function(vv),labels=LABELS)
        loss_rows.append({'epoch':epoch,'training_hinge_loss':round(float(tr_l),6),'validation_hinge_loss':round(float(va_l),6),'validation_macro_f1':round(float(f1_score(YV,sgd.predict(vv),average='macro')),6)})
    write_csv(RES/'sgd_hinge_loss_v2.csv',loss_rows)
    # Once model/config frozen, run on test.
    svmt=simple_metrics(svm,XE,YE);nbt=simple_metrics(nb,XE,YE)
    print('SVM test',svmt['macro_f1'],'NB test',nbt['macro_f1'],flush=True)
    # Language subgroup reports; metadata strictly diagnostic.
    subgroups=[]
    for name,model in [('TF-IDF + LinearSVC',svm),('TF-IDF + MultinomialNB',nb)]:
        predictions=model.predict(XE)
        for lang in ['Bisaya','Filipino','English','Mixed']:
            ix=[i for i,x in enumerate(test) if x['language_group']==lang]
            subgroups.append({'model':name,'language_group':lang,'n':len(ix),'accuracy':round(float(accuracy_score(YE[ix],predictions[ix])),6),'macro_f1':round(float(f1_score(YE[ix],predictions[ix],average='macro')),6)})
    write_csv(RES/'subgroup_test_metrics_v2.csv',subgroups)
    # Word count ablation: train simple logistic classifier using two numeric surface length features only.
    def lengths(rows):return np.array([[len(x['complaint_text'].split()),len(x['complaint_text'])] for x in rows],dtype=float)
    simple=Pipeline([('scale',StandardScaler()),('classify',LogisticRegression(max_iter=1000,random_state=SEED))]);simple.fit(lengths(train),YT)
    length_result=simple_metrics(simple,lengths(test),YE)
    # dataset EDA
    eda=[]
    for cls in LABELS:
        r=[x for x in read(DATA/'ALL_SYNTHETIC_V2.csv') if x['classification']==cls]
        words=[len(x['complaint_text'].split()) for x in r];chars=[len(x['complaint_text']) for x in r]
        eda.append({'class':cls,'n':len(r),'mean_words':round(statistics.mean(words),2),'median_words':statistics.median(words),'mean_chars':round(statistics.mean(chars),2),'min_words':min(words),'max_words':max(words)})
    write_csv(RES/'eda_v2.csv',eda)
    # lexical similarity check between held-out test and training; nearest neighbor TF-IDF cosine as a diagnostic
    # sparse top cosine computed in small batches to keep memory bounded
    max_sims=[]
    testv=vectorizer.transform(XE)
    for start in range(0,testv.shape[0],120):
        A=testv[start:start+120]@vt.T
        max_sims.extend(np.asarray(A.max(axis=1).toarray()).ravel().tolist())
    sim={'mean_nearest_train_tfidf_cosine':round(float(np.mean(max_sims)),5),'median_nearest_train_tfidf_cosine':round(float(np.median(max_sims)),5),'fraction_over_0_9':round(float(np.mean(np.array(max_sims)>=.9)),5)}
    # Existing cross-generator stress probe, seen by previous phase - explicitly NOT blind and not authentic.
    probe_path=ROOT/'evaluation'/'prior_48_reused_diagnostic.csv'
    if probe_path.exists():
        probes=read(probe_path)
        if probes:
            txt=[p['complaint_text'] for p in probes]; true=np.array([p['classification'] for p in probes]);
            probe_metrics={name:simple_metrics(m,txt,true) for name,m in [('SVM',svm),('NaiveBayes',nb)]}
        else:probe_metrics={}
    else:probe_metrics={}
    # plots: no fixed matplotlib colors
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.boxplot([[len(x['complaint_text'].split()) for x in read(DATA/'ALL_SYNTHETIC_V2.csv') if x['classification']==c] for c in LABELS],tick_labels=LABELS,showfliers=False)
    ax.set_title('Replacement dataset: narrative word counts');ax.set_ylabel('Words');fig.tight_layout();fig.savefig(FIG/'word_count_boxplot_v2.png',dpi=155);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.3,4.7))
    ax.plot([x['train_n'] for x in learning],[x['training_macro_f1'] for x in learning],marker='o',label='Training')
    ax.plot([x['train_n'] for x in learning],[x['validation_macro_f1'] for x in learning],marker='s',label='Validation')
    ax.set_ylim(0,1.03);ax.set_title('SVM learning curve (new data)');ax.set_xlabel('Training rows');ax.set_ylabel('Macro-F1');ax.legend();fig.tight_layout();fig.savefig(FIG/'svm_learning_curve_v2.png',dpi=155);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.4,4.7))
    ax.plot([x['epoch'] for x in loss_rows],[x['training_hinge_loss'] for x in loss_rows],marker='o',label='Training')
    ax.plot([x['epoch'] for x in loss_rows],[x['validation_hinge_loss'] for x in loss_rows],marker='s',label='Validation')
    ax.set_title('SGD linear hinge-loss diagnostic (not LinearSVC internal loss)');ax.set_xlabel('SGD passes');ax.set_ylabel('Multiclass hinge surrogate');ax.legend();fig.tight_layout();fig.savefig(FIG/'sgd_hinge_curves_v2.png',dpi=155);plt.close(fig)
    plot_heat(svmt['confusion_matrix'],'SVM Test Confusion V2');plot_heat(nbt['confusion_matrix'],'NB Test Confusion V2')
    fig,ax=plt.subplots(figsize=(7.4,4.6))
    for ng in ['(1, 1)','(1, 2)']:
        points=[]
        for c in [.1,1.,10.]:points.append(max(x['cv_mean_macro_f1'] for x in grid_rows if x['ngram']==ng and x['C']==c))
        ax.plot([.1,1.,10.],points,marker='o',label='Word '+ng)
    ax.set_xscale('log');ax.set_ylim(0,1.03);ax.set_title('Grouped-CV sensitivity to SVM C');ax.set_xlabel('C (log scale)');ax.set_ylabel('Group-CV Macro-F1');ax.legend();fig.tight_layout();fig.savefig(FIG/'svm_hyperparameter_v2.png',dpi=155);plt.close(fig)
    result={'data_rows':{'train':len(train),'validation':len(valid),'test':len(test)},'hyperparameter_grid':grid_rows,'chosen_params':{x:str(y) for x,y in params.items()},'best_cv_macro_f1':round(float(gs.best_score_),6),'naive_bayes':{'validation':nbv,'test':nbt},'svm':{'validation':svmv,'test':svmt},'length_only_baseline_test':length_result,'eda':eda,'lexical_similarity':sim,'prior_48_reused_diagnostic_not_blind':probe_metrics,'sgd_loss_start_end':{'start':loss_rows[0],'end':loss_rows[-1]},'learning_curve':learning,'language_subgroups':subgroups,'notes':['All 24,000 records generated from researcher-authored micro-scenarios with rule-driven transformations; not human reviewed.','No real-world generalization claim; prior 48 probes have been inspected before and are not blind.','TF-IDF features fitted only in training/folds.','The SGD curve is not the LinearSVC internal loss trace.','Frozen generated test reused only for one result report and further generator tuning should be done with a new blind set.']}
    (RES/'model_results_v2.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print('RESULT SUMMARY',json.dumps({'chosen':result['chosen_params'],'cv':result['best_cv_macro_f1'],'svm_validation':svmv['macro_f1'],'svm_test':svmt['macro_f1'],'nb_test':nbt['macro_f1'],'length_only':length_result['macro_f1'],'probe':{k:v['macro_f1'] for k,v in probe_metrics.items()}},indent=2),flush=True)
if __name__=='__main__':main()
