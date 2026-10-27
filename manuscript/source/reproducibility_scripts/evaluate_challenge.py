import csv,json,pathlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix,classification_report
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p):return list(csv.DictReader(open(p,encoding='utf-8')))
tr=load(ROOT/'data'/'TRAIN_SYNTHETIC_V2.csv')
c=load(ROOT/'evaluation'/'heldout_challenge_96.csv')
assert len(c)==96
X=[x['complaint_text'] for x in tr];y=[x['classification'] for x in tr]
XC=[x['complaint_text'] for x in c];YC=[x['classification'] for x in c]
mods={'SVM':Pipeline([('tfidf',TfidfVectorizer(max_df=.95,sublinear_tf=True,min_df=2,ngram_range=(1,1))),('svm',LinearSVC(C=10,random_state=20261026,max_iter=5000))]),'NaiveBayes':Pipeline([('tfidf',TfidfVectorizer(max_df=.95,sublinear_tf=True,min_df=2,ngram_range=(1,2))),('nb',MultinomialNB(alpha=1))])}
metrics={};rows=[]
for nm,m in mods.items():
 m.fit(X,y);pred=m.predict(XC)
 metrics[nm]={'accuracy':round(accuracy_score(YC,pred),6),'macro_f1':round(f1_score(YC,pred,average='macro'),6),'confusion_matrix':confusion_matrix(YC,pred,labels=['Valid','Suspicious','Spam']).tolist(),'report':classification_report(YC,pred,output_dict=True,zero_division=0),'by_language':{lang:{'n':sum(z['language_group']==lang for z in c),'accuracy':round(accuracy_score([YC[i] for i,z in enumerate(c) if z['language_group']==lang],[pred[i] for i,z in enumerate(c) if z['language_group']==lang]),4)} for lang in ['Bisaya','Filipino','English','Mixed']}}
 for i,z in enumerate(c):rows.append({'model':nm,'complaint_text':z['complaint_text'],'expected':YC[i],'predicted':pred[i],'language_group':z['language_group'],'challenge_type':z['challenge_type'],'correct':int(YC[i]==pred[i])})
 print(nm,metrics[nm]['accuracy'],metrics[nm]['macro_f1'],metrics[nm]['confusion_matrix'])
(ROOT/'results'/'challenge_96_metrics.json').write_text(json.dumps(metrics,indent=2))
with open(ROOT/'results'/'challenge_96_predictions.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,rows[0]);w.writeheader();w.writerows(rows)
