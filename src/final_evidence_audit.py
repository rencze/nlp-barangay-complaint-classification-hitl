"""Read-only research verification. Does not fit or retrain any model."""
import ast
import csv
import hashlib
import importlib.metadata as metadata
import json
import platform
from collections import Counter
from pathlib import Path
import joblib
import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/final_audit_20261027'
RUN=ROOT/'results/verified_20261026'
CANONICAL=ROOT/'data/Barangay_Complaint_Dataset_24000.csv'
EXPECTED='35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28'
LABELS=['Valid','Suspicious','Spam']


def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def write(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')


def main():
    rows=read(CANONICAL);assert len(rows)==24000
    sha=hashlib.sha256(CANONICAL.read_bytes()).hexdigest();assert sha==EXPECTED
    records={r['record_id']:r for r in rows};assert len(records)==len(rows)
    source=ROOT/'manuscript/source/data'
    mirror=source/'ALL_SYNTHETIC_V2.csv'
    mirror_rows=read(mirror)
    assert hashlib.sha256(mirror.read_bytes()).hexdigest()==sha
    assert mirror_rows==rows
    parts={s:[r for r in rows if r['split']==s] for s in ['train','validation','test']}
    diffs={}
    for split,name in [('train','TRAIN_SYNTHETIC_V2.csv'),('validation','VALIDATION_SYNTHETIC_V2.csv'),('test','TEST_SYNTHETIC_V2.csv')]:
        other=read(source/name)
        mismatches=[r['record_id'] for r,o in zip(parts[split],other) if r!=o]
        assert len(other)==len(parts[split]) and not mismatches
        diffs[split]={'n':len(other),'all_columns_and_order_identical':True,'mismatched_records':0}
    groups={s:{r['scenario_family_id'] for r in rr} for s,rr in parts.items()}
    overlaps={a+'_'+b:len(groups[a]&groups[b]) for a,b in [('train','validation'),('train','test'),('validation','test')]}
    assert not any(overlaps.values())
    report={'canonical_path':'data/Barangay_Complaint_Dataset_24000.csv','sha256':sha,
        'mirror_path':'manuscript/source/data/ALL_SYNTHETIC_V2.csv','mirror_sha256':sha,
        'record_level_comparison':'All 21 columns and record order identical, not only record counts',
        'rows':len(rows),'columns':list(rows[0]),'splits':diffs,'scenario_group_overlaps':overlaps,
        'classes':dict(Counter(r['classification'] for r in rows)),
        'assigned_languages':dict(Counter(r['language_group'] for r in rows)),
        'generation_categories':len({r['category_id'] for r in rows}),
        'changed_narratives':0,'changed_labels':0,'changed_languages':0,'changed_category_fields':0,
        'changed_family_identifiers':0,'changed_partitions':0,
        'additional_research_data_used':False,
        'other_files_note':'Small demo/synthetic example files predate this final audit and are not part of the 24000-record study. No challenge or feedback data was added.'}
    assert report['generation_categories']==118
    write('dataset_integrity.json',report)
    predictions=read(RUN/'predictions.csv');metrics=json.loads((RUN/'metrics.json').read_text())
    verified={}
    for name,splits in metrics.items():
        model=joblib.load(RUN/(name+'_research_only.joblib'))
        verified[name]={}
        for split,m in splits.items():
            rr=[r for r in predictions if r['model']==name and r['split']==split]
            assert len(rr)==m['n'] and len({r['record_id'] for r in rr})==len(rr)
            assert all(records[r['record_id']]['classification']==r['truth'] and records[r['record_id']]['split']==split for r in rr)
            true=[r['truth'] for r in rr];pred=[r['prediction'] for r in rr]
            actual=model.predict([records[r['record_id']]['complaint_text'] for r in rr])
            assert list(actual)==pred
            v={'n':len(rr),'accuracy':float(accuracy_score(true,pred)),
               'macro_precision':float(precision_score(true,pred,average='macro',zero_division=0)),
               'macro_recall':float(recall_score(true,pred,average='macro',zero_division=0)),
               'macro_f1':float(f1_score(true,pred,average='macro')),
               'weighted_f1':float(f1_score(true,pred,average='weighted')),
               'errors':sum(a!=b for a,b in zip(true,pred)),
               'confusion_matrix':confusion_matrix(true,pred,labels=LABELS).tolist(),
               'saved_model_predictions_match_record_exports':True}
            for key in ['accuracy','macro_precision','macro_recall','macro_f1','weighted_f1']:assert abs(v[key]-m[key])<1e-12
            assert v['errors']==m['errors'] and v['confusion_matrix']==m['confusion_matrix']
            language_checks={}
            for lang in sorted({records[r['record_id']]['language_group'] for r in rr}):
                ix=[j for j,r in enumerate(rr) if records[r['record_id']]['language_group']==lang]
                score=float(f1_score([true[j] for j in ix],[pred[j] for j in ix],labels=LABELS,average='macro'))
                saved=m['assigned_language_groups'][lang]
                assert len(ix)==saved['n'] and abs(score-saved['macro avg']['f1-score'])<1e-12
                language_checks[lang]={'n':len(ix),'macro_f1':score,'matches_saved':True}
            v['language_group_checks']=language_checks
            verified[name][split]=v
    assert not any(r['model'].startswith('candidate') and r['split']=='test' for r in predictions)
    # Check training-only fitted IDF without fitting a new model or vectorizer.
    idf_checks={}
    for name in ['svm','nb']:
        model=joblib.load(RUN/(name+'_research_only.joblib'));vec=model.named_steps['tfidf']
        matrix=vec.transform([r['complaint_text'] for r in parts['train']])
        df=np.asarray((matrix>0).sum(axis=0)).ravel()
        expected_idf=np.log((1+len(parts['train']))/(1+df))+1
        assert np.allclose(vec.idf_,expected_idf,rtol=1e-12,atol=1e-12)
        assert vec.ngram_range==((1,1) if name=='svm' else (1,2)) and vec.min_df==2 and vec.max_df==.95 and vec.sublinear_tf
        idf_checks[name]={'training_n':len(parts['train']),'features':len(vec.vocabulary_),
            'idf_matches_training_document_frequencies':True,'word_ngrams':list(vec.ngram_range),
            'min_df':vec.min_df,'max_df':vec.max_df,'sublinear_tf':vec.sublinear_tf}
    paired={}
    for split in ['validation','test']:
        bymodel={name:{r['record_id']:r for r in predictions if r['model']==name and r['split']==split} for name in ['nb','svm']}
        assert bymodel['nb'].keys()==bymodel['svm'].keys()
        ids=sorted(bymodel['nb'])
        a=b=c=d=0
        for i in ids:
            nb=bymodel['nb'][i];sv=bymodel['svm'][i];assert nb['truth']==sv['truth']
            n=nb['truth']==nb['prediction'];s=sv['truth']==sv['prediction']
            if n and s:a+=1
            elif n:b+=1
            elif s:c+=1
            else:d+=1
        paired[split]={'a':a,'b':b,'c':c,'d':d,'exact_p':float(binomtest(b,b+c,.5).pvalue) if b+c else 1.,
            'corrected_chi2':max(0,abs(b-c)-1)**2/(b+c) if b+c else 0.}
    tree=ast.parse((ROOT/'manuscript/source/reproducibility_scripts/evaluate_models.py').read_text(encoding='utf-8'))
    grid=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='param' for t in n.targets))
    assert np.prod([len(v) for v in grid.values()])==18
    assert len(read(ROOT/'manuscript/source/results/hyperparameter_grid_v2.csv'))==18
    write('experimental_verification.json',{'no_model_training_performed':True,'metrics':verified,
        'paired_mcnemar':paired,'reference_idf_checks':idf_checks,'original_search_grid':grid,
        'configuration_count':18,'candidate_evaluation':'development validation only',
        'scope':'Read-only verification of stored predictions/artifacts and unchanged data; no independent new experiment.'})
    write('verification_environment.json',{'date':'2026-10-27','python':platform.python_version(),
        'packages':{p:metadata.version(p) for p in ['scikit-learn','numpy','scipy','pandas','matplotlib','joblib','Pillow','threadpoolctl']}})
    print('PASS: byte/record-level corpus integrity, 118 categories, stored configurations, model/prediction agreement, training-only IDF and paired metrics. No model fitted.')


if __name__=='__main__':main()
