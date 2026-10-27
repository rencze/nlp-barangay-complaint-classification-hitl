# Fixed synthetic study corpus

`Barangay_Complaint_Dataset_24000.csv` is the unchanged 24,000-record researcher-constructed corpus supplied for this study. It is not a real resident archive. SHA-256:

```text
35414af2dc63e2870928bd1853c557ed301dbdae80416a0bf37be00648d92e28
```

Use `python src/verify_dataset.py` from the project root. Do not regenerate, replace, relabel, shuffle or repartition this file.

| Columns | Purpose |
|---|---|
| record_id | Unique immutable record identifier |
| complaint_text | Only predictive input |
| classification | Target: Valid / Suspicious / Spam |
| split | Stored train / validation / test membership: 19,213 / 2,399 / 2,388 |
| scenario_family_id | Group key for scenario-disjoint partitioning and cross-validation |
| template_family_id | Generation-template audit metadata |
| language_group | Assigned Bisaya / Filipino / English / Mixed diagnostic group |
| category_id, category, category_definition | 118 scenario categories, not output classes |
| complaint_topic, review_reason, spam_type | Scenario metadata; never features |
| source_reference_ids, generation_method, generation_seed | Provenance; seed 20261026 |
| source_type, language_verified, human_label_reviewed | Synthetic/unreviewed indicators |
| length_band_intended, label_rule | Generation/rubric audit metadata |

All records have unverified language and unreviewed human labels. The test partition was evaluated before this reproduction and is not a newly independent test. Exact/normalized duplicates and family overlaps are checked; similar wording remains common. See `docs/RESEARCH_AUDIT.md`.

If missing from a repository download, obtain this exact file from the thesis artifact/dataset custodian, place it at the relative path above and verify the hash. The supplied Overleaf archive contains the identical corpus as `data/ALL_SYNTHETIC_V2.csv`. No replacement dataset is equivalent. Public redistribution/source rights should be documented by the researchers before publishing data. No GitHub publication is claimed by this local preparation.
