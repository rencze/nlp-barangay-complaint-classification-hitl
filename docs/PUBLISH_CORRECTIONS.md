# Publishing the corrected research package

27 October 2026. The public repository is accessible at `https://github.com/rencze/nlp-barangay-complaint-classification-hitl` and its observed main commit is `13dadbc3f82a11bce0383171624a78d4c3ccefc8`. The corrected manuscript and full study package are local and delivered as ZIPs. A noninteractive dry-run push could not authenticate; no remote write occurred. No commit or push is claimed.

Use an authenticated Git client on the researcher's computer. Do not put a personal access token into source files, command arguments or the remote URL. The commands below create a new branch and ordinary commit, leaving existing history intact. First ensure all files from `GitHub_Ready_Research_Project.zip` are present at the repository root. The ZIP contains no `.git` metadata and will not replace repository history.

```powershell
git status --short
git fetch origin
git switch -c research/milestone2-final-audit
git add .gitignore README.md requirements.txt data/README.md data/Barangay_Complaint_Dataset_24000.csv docs evidence manuscript
git add src/compare_models.py src/evaluate_research.py src/make_research_figures.py src/make_system_diagrams.py src/package_deliverables.py src/prepare_manuscript.py src/qa_contact_sheets.py src/research_features.py src/research_validation.py src/validate_research_artifacts.py src/verify_dataset.py src/minimal_example.py src/final_evidence_audit.py src/finalize_milestone2.py src/build_final_audit_reports.py
git add results/figures results/verified_20261026 results/final_audit_20261027
git diff --cached --stat
git diff --cached --check
git commit -m "Align thesis and reproducibility artifacts with Milestone 2"
git push -u origin research/milestone2-final-audit
```

If the branch name already exists, use a new unique branch name rather than force-pushing or resetting it. Inspect staged content before committing. Pre-existing untracked web/generator/seed files are intentionally not included in the explicit source allowlist above; they were preserved locally and their limitations are documented. Do not stage unrelated personal work. The corrected package may include an exploratory prototype as historical local evidence; it is not required to run the scientific workflow.

Open a normal pull request from this branch to main, review it, and merge only through the repository's normal process. Once published, verify anonymously that the README, dependency installation, canonical CSV/hash, scripts, configurations, predictions, figures and manuscript source are accessible at the new commit. Test the documented minimal example from a fresh clone and record that new commit in a dated publication note. Until then, the Milestone 2 remote-artifact completeness row remains **Partial**, even though the corrected local package passes its checks.

For a lightweight final audit after installation, run:

```powershell
python src/minimal_example.py
python src/final_evidence_audit.py
python src/validate_research_artifacts.py
```

These do not run full study training. The tiny example intentionally fits a demonstration model solely to make classification observable; it makes no thesis performance claim. The other checks reload saved models and inspect established evidence. Full retraining commands remain documented separately for an examiner who elects to reproduce the original procedures.
