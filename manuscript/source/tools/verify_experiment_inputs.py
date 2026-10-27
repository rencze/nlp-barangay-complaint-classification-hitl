"""Read-only validation of the packaged synthetic dataset and recorded split exports.
Run: python tools/verify_experiment_inputs.py
This script NEVER trains a model, changes the dataset, or reports classification scores.
"""
from pathlib import Path
import csv, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'EXPERIMENT_MANIFEST.json').read_text())
SRC=ROOT/'data/ALL_SYNTHETIC_V2.csv'
sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert sha == MAN['dataset_sha256'], f'Unexpected corpus hash {sha}'
def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
whole=read(SRC)
assert len(whole)==24000
sets={}
for key,fn in [('train','TRAIN_SYNTHETIC_V2.csv'),('validation','VALIDATION_SYNTHETIC_V2.csv'),('test','TEST_SYNTHETIC_V2.csv')]:
 a=read(ROOT/'data'/fn)
 assert len(a)==MAN['splits']['test_previously_evaluated' if key=='test' else key], (key,len(a))
 assert all(x['split']==key for x in a)
 assert [x['record_id'] for x in a]==[x['record_id'] for x in whole if x['split']==key], f'{key} records diverge'
 sets[key]={x['scenario_family_id'] for x in a}
 print(f'{key}: {len(a)} rows, {len(sets[key])} scenario families')
for a,b in [('train','validation'),('train','test'),('validation','test')]:
 assert not sets[a].intersection(sets[b]),f'scenario-family overlap between {a} and {b}'
assert sum(len(x) for x in sets.values())>0
print('PASS: 24,000-record source SHA, split membership, counts and group disjointness verified.')
print('Scope: same synthetic corpus only; prior synthetic test is NOT unseen for future feature selection.')
