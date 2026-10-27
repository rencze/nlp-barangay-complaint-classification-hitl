"""Runnable smoke test; outputs are not study results."""
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

X = [
    "Sirang streetlight sa Purok 3",
    "Walang tubig mula kahapon sa sitio",
    "Hindi malinaw ang problema dito",
    "May nangyari pero di ko alam kung ano",
    "Buy cheap products click here",
    "Visit my store limited discount",
]
y = ["Valid", "Valid", "Suspicious", "Suspicious", "Spam", "Spam"]
pipe = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 1))),
                 ("svm", LinearSVC(C=0.1, random_state=20261026))])
pipe.fit(X, y)
for text in ["Sirang ilaw sa kanto", "Buy now big discount"]:
    print(text, "->", pipe.predict([text])[0])
print("Smoke test complete; no evaluation claim is made.")
