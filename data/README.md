# data/

This folder is reserved for the real archived complaint dataset used in the
thesis. It is intentionally kept empty in the repository.

Real complaint records obtained from participating offices may contain
personal information, so the raw dataset is **not committed to GitHub**.
Place downloaded or approved data files here locally and keep them ignored,
or store them outside the repository entirely.

Expected format for pipeline scripts (CSV, UTF-8):

| column | description                          |
|--------|--------------------------------------|
| text   | complaint narrative (Bisaya / Filipino / English / code-switched) |
| label  | one of: `valid`, `suspicious`, `spam` |

A small simulated sample with this exact format is available at
`examples/demo_complaints.csv`.
