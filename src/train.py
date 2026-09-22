"""Train the TF-IDF + linear SVM complaint classifier.

Minimal working example (from the repository root):

    python src/train.py --data examples/demo_complaints.csv

The script performs a stratified 80/20 train-test split, fits a TF-IDF
(word + bigram) + LinearSVC pipeline with balanced class weights, prints
per-class precision/recall/F1 plus macro-F1, and saves the fitted model
and the classification report.
"""

import argparse
import csv
import os
import sys
from collections import Counter

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preprocess import normalize_text


def load_dataset(path):
    """Load a CSV with 'text' and 'label' columns; return (texts, labels)."""
    texts = []
    labels = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = {"text", "label"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(
                f"CSV must have 'text' and 'label' columns; missing: {sorted(missing)}"
            )
        for row in reader:
            text = normalize_text(row["text"])
            label = (row["label"] or "").strip().lower()
            if not text or not label:
                continue
            texts.append(text)
            labels.append(label)
    if not texts:
        raise SystemExit(f"No usable rows found in {path}")
    return texts, labels


def build_pipeline(seed):
    """TF-IDF word/bigram features feeding a class-weighted linear SVM."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
            ),
            (
                "svm",
                LinearSVC(class_weight="balanced", random_state=seed),
            ),
        ]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", required=True, help="CSV file with 'text' and 'label' columns"
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    texts, labels = load_dataset(args.data)
    print("Label distribution:", dict(Counter(labels)))

    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=labels,
    )
    print(f"Train: {len(train_texts)}  Test: {len(test_texts)}")

    pipeline = build_pipeline(args.seed)
    pipeline.fit(train_texts, train_labels)
    predictions = pipeline.predict(test_texts)

    report = classification_report(test_labels, predictions, digits=3, zero_division=0)
    print(report)

    os.makedirs(args.model_dir, exist_ok=True)
    os.makedirs(args.results_dir, exist_ok=True)

    model_path = os.path.join(args.model_dir, "tfidf_svm_model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"Saved model to {model_path}")

    report_path = os.path.join(args.results_dir, "classification_report.txt")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(f"Saved report to {report_path}")


if __name__ == "__main__":
    main()
