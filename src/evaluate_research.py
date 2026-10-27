"""Evaluate a trusted saved reference on one recorded holdout; no refitting."""
import argparse
import json
import joblib
from research_validation import OUT, audit, evaluate, write_csv

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',choices=['nb','svm'],required=True)
    p.add_argument('--split',choices=['validation','test'],default='validation')
    args=p.parse_args()
    rows=audit(record_run_metadata=False)[args.split]
    model=joblib.load(OUT/(args.model+'_research_only.joblib'))
    predictions=[]
    metrics,_=evaluate(model,rows,args.model,args.split,predictions)
    write_csv('reevaluated_'+args.model+'_'+args.split+'_predictions.csv',predictions)
    print(json.dumps(metrics,indent=2))
