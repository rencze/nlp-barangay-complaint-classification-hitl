"""Recompute paired McNemar comparisons from exported per-record predictions."""
import csv
import json
import numpy as np
from research_validation import OUT, compare

if __name__ == '__main__':
    with (OUT/'predictions.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    result={}
    for split in ['validation','test']:
        models={m:{r['record_id']:r for r in rows if r['model']==m and r['split']==split} for m in ['nb','svm']}
        assert models['nb'].keys()==models['svm'].keys()
        ids=sorted(models['nb'])
        assert all(models['nb'][i]['truth']==models['svm'][i]['truth'] for i in ids)
        result[split]=compare(np.array([models['nb'][i]['truth'] for i in ids]),
            [models['nb'][i]['prediction'] for i in ids],[models['svm'][i]['prediction'] for i in ids])
    print(json.dumps(result,indent=2))
