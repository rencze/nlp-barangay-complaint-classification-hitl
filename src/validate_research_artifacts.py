"""Independent consistency checks for saved predictions, figures and model reloads."""
import csv
import hashlib
import json
import sys
from pathlib import Path
import joblib
import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from research_validation import ROOT, OUT, DATA, EXPECTED_HASH, LABELS
from research_features import candidate_normalize


def main():
    metrics=json.loads((OUT/'metrics.json').read_text())
    with (OUT/'predictions.csv').open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    checks=[]
    for name,splits in metrics.items():
        for split,m in splits.items():
            records=[r for r in rows if r['model']==name and r['split']==split]
            assert len(records)==m['n']
            y=[r['truth'] for r in records];pred=[r['prediction'] for r in records]
            assert len({r['record_id'] for r in records})==len(records)
            assert abs(accuracy_score(y,pred)-m['accuracy'])<1e-12
            assert abs(f1_score(y,pred,average='macro')-m['macro_f1'])<1e-12
            assert confusion_matrix(y,pred,labels=LABELS).tolist()==m['confusion_matrix']
            assert sum(a!=b for a,b in zip(y,pred))==m['errors']
            checks.append(name+'/'+split+': prediction counts and independent metrics agree')
    assert not any(r['split']=='test' and r['model'].startswith('candidate') for r in rows)
    # All model files must reload from a different entry point (detect __main__ pickle errors).
    for path in OUT.glob('*research_only.joblib'):
        model=joblib.load(path)
        assert set(model.classes_)==set(LABELS)
        assert model.predict(['There is a blocked public drain near our house.'])[0] in LABELS
        checks.append(path.name+': reload and inference passed')
    assert 'hindi' in candidate_normalize('HINDI totoo ang sinabi.')
    assert 'wala' in candidate_normalize('WALA pa ang tulong.')
    assert 'not' in candidate_normalize('This is NOT an advertisement.')
    assert 'ñ' in candidate_normalize('señor')
    figs=ROOT/'results/figures'
    required=['validation_performance','testing_performance','model_performance_comparison',
       'svm_validation_confusion_matrix','svm_testing_confusion_matrix',
       'naive_bayes_validation_confusion_matrix','naive_bayes_testing_confusion_matrix',
       'cross_validation_results','hyperparameter_tuning_results','statistical_comparison']
    for name in required:
        for ext in ['png','pdf','svg']:assert (figs/(name+'.'+ext)).is_file()
    for path in figs.glob('*.png'):
        with Image.open(path) as im:
            assert min(im.info['dpi'])>=300
            assert im.width>=1500
    checks.append('All required figure trios exist; every PNG is at least 300 DPI')
    assert hashlib.sha256(DATA.read_bytes()).hexdigest()==EXPECTED_HASH
    for path in [ROOT/'manuscript/source/main.log',ROOT/'output/pdf/evaluation_report.log']:
        if path.exists():
            log=path.read_text(errors='replace')
            assert 'Output written on ' in log
            assert 'Overfull' not in log
            assert 'undefined references' not in log
            assert 'undefined on input' not in log
            checks.append(path.name+': compilation success, no overflow or undefined references')
    result={'passed':True,'checks':checks,'dataset_sha256':EXPECTED_HASH,
        'note':'Pixel layout inspected separately through rendered page contact sheets and full-size figures.'}
    (OUT/'artifact_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
