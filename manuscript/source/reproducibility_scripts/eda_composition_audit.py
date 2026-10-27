"""Read-only audit for Chapter 3 dataset composition and length statistics."""
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
data = pd.read_csv(root / "data" / "ALL_SYNTHETIC_V2.csv")
assert len(data) == 24000
assert data['complaint_text'].notna().all()
assert not data['complaint_text'].duplicated().any()
print("Rows, columns:", data.shape)
print("Labels:\n",data['classification'].value_counts().to_string())
print("Assigned languages:\n",data['language_group'].value_counts().to_string())
print("Partitions:\n",data['split'].value_counts().to_string())
print("Provenance:\n",data['source_type'].value_counts().to_string())
counts = data['complaint_text'].astype(str).str.split().str.len()
print("Word count by label:\n",data.assign(words=counts).groupby('classification')['words'].agg(['count','mean','median','min','max']).to_string())
print("Overall word count:\n",counts.describe().to_string())
