"""Evaluate a saved TF-IDF + SVM model on a labeled CSV.

Example (from the repository root, after training):

    python src/evaluate.py --data examples/demo_complaints.csv
"""

import argparse
import os
import sys

import joblib
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train import load_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", required=True, help="CSV file with 'text' and 'label' columns"
    )
    parser.add_argument(
        "--model", default=os.path.join("models", "tfidf_svm_model.joblib")
    )
    args = parser.parse_args()

    if not os.path.exists(args.model):
        raise SystemExit(
            f"Model not found at {args.model}. Run train.py first."
        )

    pipeline = joblib.load(args.model)
    texts, labels = load_dataset(args.data)
    predictions = pipeline.predict(texts)

    print(classification_report(labels, predictions, digits=3, zero_division=0))
    print("Confusion matrix (rows = true, columns = predicted):")
    print(confusion_matrix(labels, predictions))


if __name__ == "__main__":
    main()
