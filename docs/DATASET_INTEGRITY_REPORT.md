# Dataset Integrity Report

Verified 27 October 2026. The canonical source was not edited. No new research dataset, relabeling, narrative rewrite, language reassignment or repartitioning was performed.

| File | SHA-256 | Finding |
|---|---|---|
| `data/Barangay_Complaint_Dataset_24000.csv` | `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28` | Byte-identical original corpus |
| `manuscript/source/data/ALL_SYNTHETIC_V2.csv` | `35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28` | Byte-identical original corpus |

The hash equals the recorded original manifest. A separate CSV comparison checked **all 21 fields for all 24,000 records and their order**, not merely counts. This establishes that ALL_SYNTHETIC_V2 is an exported copy, not a replacement dataset. The existing split exports also match canonical records in all fields/order. The canonical path for repository instructions is `data/Barangay_Complaint_Dataset_24000.csv`; the Overleaf project's mirror is retained for self-contained archival documentation.

| Partition | Records | All fields/order match canonical | Scenario overlap with other splits |
|---|---:|---|---:|
| train | 19,213 | Yes | 0 |
| validation | 2,399 | Yes | 0 |
| test | 2,388 | Yes | 0 |

Classes: 8,000 Valid, 8,000 Suspicious, 8,000 Spam. Assigned language groups: 6,000 each Bisaya, Filipino, English and Mixed. All 118 generation categories are retained. Zero changed narratives, labels, language assignments, category fields, scenario/template IDs or partition memberships were found. Source and language/human-review flags remain synthetic/unreviewed. Small example datasets are demonstration inputs, not additional research observations; no challenge or feedback data was introduced.

No raw or conservative Unicode-normalized exact duplicates were found in the established audit, and family/template/exact-text cross-split overlap is zero. High lexical similarity still limits independence; exact integrity is not a semantic or annotation-quality certification. The synthetic test remains an already evaluated original partition.

Code/evidence: `src/final_evidence_audit.py`, `results/final_audit_20261027/dataset_integrity.json`, original hash in `evidence/historical/manuscript/EXPERIMENT_MANIFEST.json`, and `results/verified_20261026/dataset_audit.json`. Training-only fitted IDF was independently checked against document frequencies of the stored training narratives without fitting a new model. The saved reference artifacts/predictions agree; historical scripts keep TF-IDF inside training folds. No holdout fitting was found in those paths, while generator-family semantic dependence remains a disclosed limitation.
