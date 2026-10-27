"""Auditable supplement: unchanged corpus, fixed reference, development-only candidate.

Run from repository root: python src/research_validation.py --mode all
The original archived procedures are run separately before this supplement.
"""
import argparse
import csv
import hashlib
import importlib.metadata as metadata
import json
import platform
import re
import subprocess
import time
import unicodedata
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from scipy.stats import binomtest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, log_loss
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedGroupKFold, cross_validate
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC
from research_features import candidate_normalize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/Barangay_Complaint_Dataset_24000.csv'
OUT = ROOT / 'results/verified_20261026'
SEED = 20261026
LABELS = ['Valid', 'Suspicious', 'Spam']
EXPECTED_HASH = '35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28'


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def write_csv(name, rows):
    rows = list(rows)
    if not rows:
        return
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def audit(record_run_metadata=True):
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert digest == EXPECTED_HASH, 'Corpus changed; stop rather than silently adapt.'
    with DATA.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 24000
    assert Counter(r['classification'] for r in rows) == dict.fromkeys(LABELS, 8000)
    assert Counter(r['split'] for r in rows) == {'train':19213, 'validation':2399, 'test':2388}
    assert len({r['record_id'] for r in rows}) == len(rows)
    assert all(r['complaint_text'].strip() and r['scenario_family_id'] for r in rows)
    partitions = {s:[r for r in rows if r['split']==s] for s in ['train','validation','test']}
    groups = {s:{r['scenario_family_id'] for r in rr} for s,rr in partitions.items()}
    pairs = [('train','validation'),('train','test'),('validation','test')]
    overlap = {a+'_'+b:len(groups[a]&groups[b]) for a,b in pairs}
    assert not any(overlap.values())
    normalized = [candidate_normalize(r['complaint_text']) for r in rows]
    norm_sets = {s:{candidate_normalize(r['complaint_text']) for r in rr} for s,rr in partitions.items()}
    archive_root = ROOT/'manuscript/source/data'
    partition_equivalence = {}
    for split, filename in [('train','TRAIN_SYNTHETIC_V2.csv'),('validation','VALIDATION_SYNTHETIC_V2.csv'),('test','TEST_SYNTHETIC_V2.csv')]:
        if (archive_root/filename).exists():
            with (archive_root/filename).open(encoding='utf-8-sig',newline='') as f:
                archived = list(csv.DictReader(f))
            partition_equivalence[split] = archived == partitions[split]
            assert partition_equivalence[split]
    inventory = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or any(p in {'.git','.venv','__pycache__','tmp','output'} or p.startswith('.venv-') for p in path.relative_to(ROOT).parts):
            continue
        inventory.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,
                          'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    if record_run_metadata and not (OUT/'pre_supplement_inventory.csv').exists():
        write_csv('pre_supplement_inventory.csv',inventory)
    result = {'sha256':digest,'records':len(rows),'columns':list(rows[0]),
              'class_counts':dict(Counter(r['classification'] for r in rows)),
              'assigned_languages':dict(Counter(r['language_group'] for r in rows)),
              'partition_counts':{s:len(rr) for s,rr in partitions.items()},
              'partition_class_counts':{s:dict(Counter(r['classification'] for r in rr)) for s,rr in partitions.items()},
              'scenario_groups':{s:len(g) for s,g in groups.items()},'cross_split_group_overlap':overlap,
              'exact_duplicate_excess':len(rows)-len({r['complaint_text'] for r in rows}),
              'normalized_duplicate_excess':len(rows)-len(set(normalized)),
              'cross_split_normalized_text_overlap':{a+'_'+b:len(norm_sets[a]&norm_sets[b]) for a,b in pairs},
              'archived_partition_record_and_order_equivalence':partition_equivalence,
              'template_family_overlap':{a+'_'+b:len({r['template_family_id'] for r in partitions[a]}&{r['template_family_id'] for r in partitions[b]}) for a,b in pairs},
              'review_flags':{k:dict(Counter(r[k] for r in rows)) for k in ['source_type','language_verified','human_label_reviewed']}}
    save('dataset_audit.json',result)
    packages = ['scikit-learn','numpy','scipy','pandas','matplotlib','joblib']
    environment={'python':platform.python_version(),'os':platform.system(),'machine':platform.machine(),
         'processor':platform.processor(),'seed':SEED,'versions':{p:metadata.version(p) for p in packages},
         'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         'working_tree_note':'Uncommitted pre-existing files preserved; inventory hashes identify actual source.'}
    if record_run_metadata:
        save('environment.json',environment)
    return partitions


def reference(kind):
    return Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,1) if kind=='svm' else (1,2),
                      min_df=2,max_df=.95,sublinear_tf=True)),
                     ('model',LinearSVC(C=.1,max_iter=5000,random_state=SEED) if kind=='svm' else MultinomialNB(alpha=1.0))])


def candidate():
    features = FeatureUnion([
        ('word',TfidfVectorizer(preprocessor=candidate_normalize,ngram_range=(1,2),min_df=2,max_df=.95,sublinear_tf=True)),
        ('char',TfidfVectorizer(preprocessor=candidate_normalize,analyzer='char_wb',ngram_range=(3,5),min_df=3,max_features=45000,sublinear_tf=True))])
    return Pipeline([('features',features),('svm',LinearSVC(C=.1,max_iter=5000,random_state=SEED))])


def evaluate(model, rows, name, split, predictions):
    text = [r['complaint_text'] for r in rows]
    y = np.array([r['classification'] for r in rows])
    pred = model.predict(text)
    report = classification_report(y,pred,labels=LABELS,output_dict=True,zero_division=0)
    result = {'n':len(rows),'accuracy':float(accuracy_score(y,pred)),
              'macro_precision':report['macro avg']['precision'],'macro_recall':report['macro avg']['recall'],
              'macro_f1':report['macro avg']['f1-score'],'weighted_f1':report['weighted avg']['f1-score'],
              'errors':int(sum(y!=pred)),'report':report,
              'label_order':LABELS,'confusion_matrix':confusion_matrix(y,pred,labels=LABELS).tolist()}
    languages = {}
    for lang in sorted({r['language_group'] for r in rows}):
        idx = np.array([r['language_group']==lang for r in rows])
        languages[lang] = classification_report(y[idx],pred[idx],labels=LABELS,output_dict=True,zero_division=0)
        languages[lang]['n'] = int(idx.sum())
    result['assigned_language_groups'] = languages
    for row,truth,guess in zip(rows,y,pred):
        predictions.append({'model':name,'split':split,'record_id':row['record_id'],
                            'truth':truth,'prediction':guess,'correct':bool(truth==guess),
                            'language_group':row['language_group'],'scenario_family_id':row['scenario_family_id']})
    if hasattr(model,'predict_proba'):
        probs = model.predict_proba(text)
        onehot = (y[:,None]==model.classes_[None,:]).astype(float)
        confidence = probs.max(axis=1)
        correct = pred==y
        ece=0.0
        for low in np.linspace(0,.9,10):
            idx=(confidence>=low)&(confidence<low+.1 if low<.9 else confidence<=1)
            if idx.any():
                ece+=idx.mean()*abs(correct[idx].mean()-confidence[idx].mean())
        result['probability_diagnostics']={'log_loss':float(log_loss(y,probs,labels=model.classes_)),
             'multiclass_brier_sum':float(np.mean(np.sum((probs-onehot)**2,axis=1))),
             'ece_10_equal_width_bins':float(ece),'mean_max_probability':float(confidence.mean()),
             'scope':'Synthetic development only; does not certify operational probability reliability.'}
        write_csv(name+'_'+split+'_probabilities.csv',({'record_id':r['record_id'],**{str(c):float(p[j]) for j,c in enumerate(model.classes_)}} for r,p in zip(rows,probs)))
    return result, pred


def compare(y, baseline, svm):
    base=np.asarray(baseline)==y; other=np.asarray(svm)==y
    a,b,c,d=[int(z.sum()) for z in [base&other,base&~other,~base&other,~base&~other]]
    return {'a_both_correct':a,'b_baseline_only':b,'c_svm_only':c,'d_both_wrong':d,
            'exact_two_sided_p':float(binomtest(b,b+c,.5).pvalue) if b+c else 1.0,
            'continuity_corrected_chi2':max(0,abs(b-c)-1)**2/(b+c) if b+c else 0.,
            'limitation':'Record pairs share generated families; nominal p is descriptive and may be anticonservative under dependence. This compares pipelines, not isolated estimators.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['audit','reference','all'],default='all')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    parts=audit()
    if args.mode=='audit':
        print('Dataset audit passed.',flush=True);return
    tr=parts['train']; X=[r['complaint_text'] for r in tr]
    y=np.array([r['classification'] for r in tr]); groups=np.array([r['scenario_family_id'] for r in tr])
    results={};predictions=[];paired={}
    for name in ['nb','svm']:
        model=reference(name).fit(X,y)
        joblib.dump(model,OUT/(name+'_research_only.joblib'))
        results[name]={};paired[name]={}
        for split in ['validation','test']:
            results[name][split], paired[name][split]=evaluate(model,parts[split],name,split,predictions)
        print(name,results[name]['validation']['macro_f1'],flush=True)
    comparisons={s:compare(np.array([r['classification'] for r in parts[s]]),paired['nb'][s],paired['svm'][s]) for s in ['validation','test']}
    save('paired_comparison.json',comparisons)
    # Near-duplicate diagnostic: frozen reference vectorizer; no extra fitting on holdouts.
    svm=joblib.load(OUT/'svm_research_only.joblib');vec=svm.named_steps['tfidf']; train_v=vec.transform(X)
    near={}
    for split in ['validation','test']:
        held=vec.transform([r['complaint_text'] for r in parts[split]])
        nearest=[];similarities=[]
        for start in range(0,held.shape[0],100):
            sim=cosine_similarity(held[start:start+100],train_v)
            similarities.extend(sim.max(axis=1).tolist()); nearest.extend(sim.argmax(axis=1).tolist())
        near[split]={'mean_nearest_cosine':float(np.mean(similarities)),
                     'median_nearest_cosine':float(np.median(similarities)),
                     'fraction_at_least_0_9':float(np.mean(np.array(similarities)>=.9)),
                     'threshold_note':'Descriptive unigram lexical similarity, not an adjudicated duplicate definition.'}
        write_csv(split+'_nearest_training.csv',({'record_id':r['record_id'],'nearest_train_id':tr[i]['record_id'],'cosine':score} for r,i,score in zip(parts[split],nearest,similarities)))
    save('near_duplicate_diagnostics.json',near)
    if args.mode=='all':
        folds=list(StratifiedGroupKFold(3,shuffle=True,random_state=SEED).split(X,y,groups))
        assert all(set(groups[a]).isdisjoint(set(groups[b])) for a,b in folds)
        config={'normalization':'Unicode NFKC + casefold + whitespace; no stopword removal, negation/accents retained',
                'word_ngrams':[1,2],'word_min_df':2,'word_max_df':.95,'char_analyzer':'char_wb',
                'char_ngrams':[3,5],'char_min_df':3,'char_max_features':45000,'feature_weights':[1,1],
                'C':.1,'calibration':'sigmoid, ensemble=True, 3 precomputed scenario-grouped training folds',
                'selection':'Single fixed candidate; development comparison only, no candidate test evaluation', 'seed':SEED}
        save('candidate_config.json',config)
        print('Fitting single word + character candidate',flush=True)
        model=candidate().fit(X,y)
        results['candidate_uncalibrated']={'validation':evaluate(model,parts['validation'],'candidate_uncalibrated','validation',predictions)[0]}
        joblib.dump(model,OUT/'candidate_uncalibrated_research_only.joblib')
        print('Fitting group-disjoint calibrated candidate',flush=True)
        calibrated=CalibratedClassifierCV(candidate(),method='sigmoid',cv=folds,ensemble=True,n_jobs=1).fit(X,y)
        results['candidate_calibrated']={'validation':evaluate(calibrated,parts['validation'],'candidate_calibrated','validation',predictions)[0]}
        joblib.dump(calibrated,OUT/'candidate_calibrated_research_only.joblib')
        print('Candidate validation F1',results['candidate_calibrated']['validation']['macro_f1'],flush=True)
    save('metrics.json',results)
    write_csv('predictions.csv',predictions)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for name,splits in results.items():
        for split,m in splits.items():
            fig,ax=plt.subplots(figsize=(5.6,4.6)); matrix=np.array(m['confusion_matrix'])
            ax.imshow(matrix,cmap='Blues');ax.set_xticks(range(3),LABELS);ax.set_yticks(range(3),LABELS)
            for i in range(3):
                for j in range(3):
                    ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>matrix.max()/2 else 'black')
            ax.set_xlabel('Predicted');ax.set_ylabel('True');ax.set_title(name.replace('_',' ')+' / '+split)
            fig.tight_layout();fig.savefig(OUT/(name+'_'+split+'_confusion.png'),dpi=180);plt.close(fig)
    assert hashlib.sha256(DATA.read_bytes()).hexdigest()==EXPECTED_HASH
    print('Supplement complete; unchanged source hash verified.',flush=True)


if __name__=='__main__':
    main()
