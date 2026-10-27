"""Fit frozen selected V2 classifiers; models are research artifacts, not approved for unattended deployment."""
import csv,pathlib,joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
R=pathlib.Path(__file__).resolve().parents[1]
with open(R/'data'/'TRAIN_SYNTHETIC_V2.csv',encoding='utf-8') as f:items=list(csv.DictReader(f))
X=[x['complaint_text'] for x in items];y=[x['classification'] for x in items]
models={'linear_svm_v2_research_only.joblib': Pipeline([('tfidf',TfidfVectorizer(max_df=.95,sublinear_tf=True,min_df=2,ngram_range=(1,1))),('svm',LinearSVC(C=.1,max_iter=5000,random_state=20261026))]),'multinomial_nb_v2_research_only.joblib':Pipeline([('tfidf',TfidfVectorizer(max_df=.95,sublinear_tf=True,min_df=2,ngram_range=(1,2))),('nb',MultinomialNB(alpha=1.0))])}
for fn,model in models.items():
 model.fit(X,y);joblib.dump(model,R/'results'/fn);print('Saved',fn)
