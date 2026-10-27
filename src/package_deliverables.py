"""Package reviewed local artifacts without publishing or modifying Git history."""
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from research_validation import ROOT, OUT

OUTPUT=ROOT/'output'


def sanitized_logs():
    dest=OUT/'logs';dest.mkdir(parents=True,exist_ok=True)
    for name in ['original_experiment_rerun.log','grouped_validation_rerun.log','supplement_rerun.log']:
        p=ROOT/'manuscript'/name
        if p.exists():
            raw=p.read_bytes()
            text=raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig',errors='replace')
            # Logs shared as evidence use portable paths; raw local console logs are excluded.
            text=text.replace(str(ROOT),'<PROJECT_ROOT>').replace(str(ROOT).replace('\\','/'),'<PROJECT_ROOT>')
            text=text.replace(str(Path.home()),'<USER_HOME>').replace(str(Path.home()).replace('\\','/'),'<USER_HOME>')
            (dest/name.replace('.log','.txt')).write_text(text,encoding='utf-8')
    # Installer output may use lowercase Windows paths; match case-insensitively.
    final_logs=ROOT/'results/final_audit_20261027'
    if final_logs.exists():
        for path in final_logs.glob('*.txt'):
            raw=path.read_bytes()
            text=raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig',errors='replace')
            for original,replacement in [(str(ROOT),'<PROJECT_ROOT>'),(str(ROOT).replace('\\','/'),'<PROJECT_ROOT>'),
                                          (str(Path.home()),'<USER_HOME>'),(str(Path.home()).replace('\\','/'),'<USER_HOME>')]:
                text=re.sub(re.escape(original),lambda m:replacement,text,flags=re.IGNORECASE)
            path.write_text(text,encoding='utf-8')


def main():
    OUTPUT.mkdir(exist_ok=True)
    sanitized_logs()
    pdf=OUTPUT/'pdf';pdf.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'manuscript/source/main.pdf',pdf/'Thesis2_Verified_Manuscript.pdf')
    shutil.copy2(pdf/'evaluation_report.pdf',pdf/'ML_Evaluation_Report.pdf')
    commands={
      'original':'python -u manuscript/source/reproducibility_scripts/evaluate_models.py',
      'grouped_validation':'python -u manuscript/source/validation_suite/run_grouped_validation.py',
      'supplement':'python -u src/research_validation.py --mode all',
      'figures':'python src/make_research_figures.py',
      'diagrams':'python src/make_system_diagrams.py',
      'manuscript':'python src/prepare_manuscript.py',
      'verification':'python src/validate_research_artifacts.py'}
    (OUT/'execution_commands.json').write_text(json.dumps(commands,indent=2),encoding='utf-8')
    source=ROOT/'manuscript/source'
    build_suffixes={'.aux','.log','.toc','.lof','.lot','.out','.synctex','.gz','.pyc','.joblib'}
    with zipfile.ZipFile(OUTPUT/'Thesis2_Verified_Overleaf.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.suffix in build_suffixes or p.name=='main.pdf':continue
            z.write(p,p.relative_to(source).as_posix())
    with zipfile.ZipFile(OUTPUT/'Validation_Testing_Figures.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'results/figures').iterdir()):
            if p.is_file():z.write(p,'results/figures/'+p.name)
    # Explicit allowlist avoids credentials, personal caches, databases and raw console logs.
    roots=['src','data','examples','docs','evidence/historical','evidence/pre_final_audit',
           'manuscript/source','manuscript/revision_templates',
           'results/figures','results/verified_20261026','results/final_audit_20261027']
    with zipfile.ZipFile(OUTPUT/'GitHub_Ready_Research_Project.zip','w',zipfile.ZIP_DEFLATED) as z:
        for filename in ['README.md','requirements.txt','.gitignore']:
            z.write(ROOT/filename,filename)
        for directory in roots:
            for p in sorted((ROOT/directory).rglob('*')):
                if not p.is_file() or '__pycache__' in p.parts or p.suffix in {'.aux','.log','.toc','.lof','.lot','.out','.pyc','.db'} or p.name=='main.pdf':continue
                z.write(p,p.relative_to(ROOT).as_posix())
        # Portable sanitized logs have .txt extensions and are already included above.
    checksums={}
    deliverables=[OUTPUT/'Thesis2_Verified_Overleaf.zip',OUTPUT/'Validation_Testing_Figures.zip',
                  OUTPUT/'GitHub_Ready_Research_Project.zip',pdf/'Thesis2_Verified_Manuscript.pdf',pdf/'ML_Evaluation_Report.pdf']
    for p in deliverables:
        checksums[p.relative_to(OUTPUT).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
        if p.suffix=='.zip':
            with zipfile.ZipFile(p) as z:assert z.testzip() is None
    (OUTPUT/'DELIVERY_MANIFEST.json').write_text(json.dumps(checksums,indent=2),encoding='utf-8')
    shutil.copy2(OUTPUT/'Thesis2_Verified_Overleaf.zip',OUTPUT/'Thesis2_Milestone2_Aligned_Overleaf.zip')
    shutil.copy2(pdf/'Thesis2_Verified_Manuscript.pdf',pdf/'Thesis2_Milestone2_Aligned_Manuscript.pdf')
    with zipfile.ZipFile(OUTPUT/'Thesis2_Complete_Deliverables.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in deliverables+[OUTPUT/'DELIVERY_MANIFEST.json']:
            z.write(p,p.relative_to(OUTPUT).as_posix())
        for p in sorted((ROOT/'docs').rglob('*')):
            if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUTPUT/'Thesis2_Complete_Deliverables.zip') as z:assert z.testzip() is None
    print(json.dumps(checksums,indent=2))


if __name__=='__main__':main()
