"""Publication figures from executed JSON metrics and archived-procedure rerun outputs.

python src/make_research_figures.py
All PNG files are 360 DPI; PDFs and SVGs preserve vector text and lines.
"""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research_validation import OUT, ROOT, LABELS, compare

FIG=ROOT/'results/figures'
FIG.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':11,'axes.titlesize':14,
    'axes.labelsize':11,'legend.fontsize':10,'pdf.fonttype':42,'ps.fonttype':42,
    'svg.fonttype':'none','savefig.bbox':'tight','savefig.pad_inches':.16})
COLORS=['#17618D','#B46A21']


def save(fig,name):
    for ext in ['png','pdf','svg']:
        fig.savefig(FIG/(name+'.'+ext),dpi=360)
    plt.close(fig)


def table(ax,headers,rows,widths=None,fontsize=11):
    ax.axis('off')
    t=ax.table(cellText=rows,colLabels=headers,loc='center',cellLoc='center',colWidths=widths)
    t.auto_set_font_size(False);t.set_fontsize(fontsize);t.scale(1,1.75)
    for (r,c),cell in t.get_celld().items():
        cell.set_edgecolor('#9B9B9B');cell.set_linewidth(.5)
        if r==0:
            cell.set_facecolor('#E6E6E6');cell.get_text().set_weight('bold')
            if any('\n' in h for h in headers):cell.set_height(cell.get_height()*1.7)
    return t


def main():
    metrics=json.loads((OUT/'metrics.json').read_text(encoding='utf-8'))
    # Recompute paired statistics from ID-aligned actual predictions, not aggregate counts.
    with (OUT/'predictions.csv').open(newline='',encoding='utf-8') as f: predictions=list(csv.DictReader(f))
    paired={}
    for split in ['validation','test']:
        records={name:{r['record_id']:r for r in predictions if r['model']==name and r['split']==split} for name in ['nb','svm']}
        ids=sorted(records['nb']);assert records['nb'].keys()==records['svm'].keys()
        assert all(records['nb'][i]['truth']==records['svm'][i]['truth'] for i in ids)
        paired[split]=compare(np.array([records['nb'][i]['truth'] for i in ids]),
            [records['nb'][i]['prediction'] for i in ids],[records['svm'][i]['prediction'] for i in ids])
    keys=['accuracy','macro_precision','macro_recall','macro_f1','weighted_f1']
    labels=['Accuracy','Macro-\nprecision','Macro-\nrecall','Macro-F1','Weighted-F1']
    for split,title,stem in [('validation','Fixed development validation','validation'),('test','Previously evaluated synthetic test','testing')]:
        n=metrics['svm'][split]['n']
        fig,ax=plt.subplots(figsize=(7.8,4.8))
        rows=[['Evaluated records',str(n),str(n)]]
        for key,label in zip(keys,['Accuracy','Macro-precision','Macro-recall','Macro-F1','Weighted-F1']):
            rows.append([label,f"{metrics['svm'][split][key]:.6f}",f"{metrics['nb'][split][key]:.6f}"])
        rows.append(['Misclassifications',str(metrics['svm'][split]['errors']),str(metrics['nb'][split]['errors'])])
        table(ax,['Metric','Linear SVM','Naive Bayes'],rows,[.42,.29,.29],13)
        ax.set_title(title+' performance',pad=12)
        fig.text(.5,.035,'Precision and recall are macro-averaged; scores on a 0-1 scale.\nSame fixed corpus; no independent field-validation claim.',ha='center',fontsize=11)
        fig.subplots_adjust(bottom=.18,top=.85);save(fig,stem+'_performance')
    fig,axes=plt.subplots(2,1,figsize=(8.2,9.0),sharey=True)
    x=np.arange(len(keys));width=.34
    for ax,split,title in zip(axes,['validation','test'],['Validation (N = 2,399)','Previously evaluated test (N = 2,388)']):
        for j,(name,display) in enumerate([('svm','Linear SVM'),('nb','Naive Bayes')]):
            vals=[metrics[name][split][k] for k in keys]
            bars=ax.bar(x+(j-.5)*width,vals,width,label=display,color=COLORS[j],edgecolor='black',linewidth=.5,hatch='' if j==0 else '///')
            for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.4f}',ha='center',va='bottom',rotation=90,fontsize=12)
        ax.set_xticks(x,labels,rotation=0);ax.set_ylim(0,1.30);ax.set_yticks(np.linspace(0,1,6));ax.set_title(title,pad=14);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_ylabel('Score (0-1)');axes[1].set_ylabel('Score (0-1)');axes[1].legend(loc='lower right')
    fig.suptitle('Reference pipeline comparison',y=1.01);fig.tight_layout();save(fig,'model_performance_comparison')
    for name,display in [('svm','Linear SVM'),('nb','Naive Bayes')]:
        for split,stem in [('validation','validation'),('test','testing')]:
            m=metrics[name][split];arr=np.asarray(m['confusion_matrix'])
            fig,ax=plt.subplots(figsize=(6.4,5.3));im=ax.imshow(arr,cmap='Blues',vmin=0,vmax=arr.max())
            for i in range(3):
                for j in range(3):ax.text(j,i,str(arr[i,j]),ha='center',va='center',fontsize=15,color='white' if arr[i,j]>arr.max()/2 else 'black')
            ax.set_xticks(range(3),LABELS);ax.set_yticks(range(3),LABELS);ax.set_xlabel('Predicted text label');ax.set_ylabel('Reference text label')
            ax.set_title(display+' - '+('validation' if split=='validation' else 'previously evaluated test')+f"\nN = {m['n']:,}; errors = {m['errors']}")
            fig.colorbar(im,ax=ax,label='Narrative count',fraction=.045,pad=.04);fig.tight_layout()
            save(fig,('svm' if name=='svm' else 'naive_bayes')+'_'+stem+'_confusion_matrix')
    with (ROOT/'manuscript/source/validation_suite/five_fold_grouped_cv_results.csv').open() as f:cv=list(csv.DictReader(f))
    fig,(ax,tab)=plt.subplots(2,1,figsize=(9.8,7.6),gridspec_kw={'height_ratios':[2.2,1]})
    rows=[]
    for j,(full,display) in enumerate([('TF-IDF + Linear SVM','Linear SVM'),('TF-IDF + Naive Bayes','Naive Bayes')]):
        rr=[r for r in cv if r['model']==full];ys=np.array([float(r['cv_macro_f1']) for r in rr])
        ax.plot(range(1,6),ys,marker='o' if j==0 else 's',linestyle='-' if j==0 else '--',color=COLORS[j],label=display,linewidth=1.7)
        for i,v in enumerate(ys):ax.annotate(f'{v:.5f}',(i+1,v),xytext=(0,9 if j==0 else -17),textcoords='offset points',ha='center',fontsize=10)
        rows.append([display]+[f'{v:.5f}' for v in ys]+[f'{ys.mean():.6f}',f'{ys.std(ddof=1):.6f}'])
    ax.set_ylim(.987,1.003);ax.set_xticks(range(1,6));ax.set_ylabel('Held-out fold Macro-F1');ax.set_xlabel('Scenario-grouped fold');ax.grid(alpha=.2);ax.legend(loc='lower left')
    ax.set_title('Five-fold grouped cross-validation\nTraining partition only (N = 19,213)')
    table(tab,['Pipeline','F1','F2','F3','F4','F5','Mean','Sample SD'],rows,[.18,.11,.11,.11,.11,.11,.14,.13],11)
    fig.text(.5,.015,'TF-IDF refitted inside every fold. SD describes fold dispersion, not a population confidence interval.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.04,1,1]);save(fig,'cross_validation_results')
    with (ROOT/'manuscript/source/results/hyperparameter_grid_v2.csv').open() as f:grid=list(csv.DictReader(f))
    assert len(grid)==18
    fig,ax=plt.subplots(figsize=(8.4,7.8));vals=np.array([float(r['cv_mean_macro_f1']) for r in grid])[:,None]
    ax.imshow(vals,cmap='Blues',vmin=0,vmax=1,aspect='auto')
    ax.set_yticks(range(18),[f"C={r['C']}; word {r['ngram']}; min_df={r['min_df']}" for r in grid],fontsize=10)
    ax.set_xticks([0],['Three-fold grouped mean Macro-F1'])
    for i,r in enumerate(grid):ax.text(0,i,f"{float(r['cv_mean_macro_f1']):.6f}  (SD {float(r['cv_sd_macro_f1']):.6f})",ha='center',va='center',color='white',fontsize=10)
    ax.set_title('All 18 SVM hyperparameter configurations\nTraining-only grouped search; seed 20261026',pad=15)
    fig.text(.5,.018,'All candidates tie. Deterministic selection: C = 0.1, unigrams, min_df = 2.\nFixed max_df = 0.95 and sublinear_tf = True. No evidence of parameter superiority.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.07,1,1]);save(fig,'hyperparameter_tuning_results')
    fig,axes=plt.subplots(2,1,figsize=(9.4,8.0))
    for ax,split,title in zip(axes,['validation','test'],['Validation (N = 2,399)','Previously evaluated synthetic test (N = 2,388)']):
        m=paired[split]
        table(ax,['Baseline / SVM','SVM correct','SVM wrong'],[
            ['Naive Bayes correct',str(m['a_both_correct']),str(m['b_baseline_only'])],
            ['Naive Bayes wrong',str(m['c_svm_only']),str(m['d_both_wrong'])]],[.48,.26,.26],13)
        ax.set_title(title,pad=12)
        ax.text(.5,.01,f"b = {m['b_baseline_only']}; c = {m['c_svm_only']}; corrected chi-square = {m['continuity_corrected_chi2']:.6f}\nExact two-sided p = {m['exact_two_sided_p']:.10g}",transform=ax.transAxes,ha='center',va='bottom',fontsize=11)
    fig.suptitle('Paired McNemar comparison from record-level predictions',y=.98,fontsize=14)
    fig.text(.5,.045,'Nominal p < 0.05 favors SVM on this synthetic benchmark.\nShared generator/family dependence limits inference; this is not evidence of field superiority.\nCorrected statistic: max(0, |b-c|-1)^2 / (b+c); exact test: Binomial(b+c, 0.5).',ha='center',fontsize=10)
    fig.subplots_adjust(hspace=.48,top=.90,bottom=.19);save(fig,'statistical_comparison')
    fig,ax=plt.subplots(figsize=(9.8,4.0));rows=[]
    for name,display in [('svm','Reference word SVM'),('candidate_uncalibrated','Word + character SVM'),('candidate_calibrated','Calibrated word + character')]:
        m=metrics[name]['validation'];p=m.get('probability_diagnostics',{})
        rows.append([display,f"{m['macro_f1']:.6f}",str(m['errors']),f"{p['log_loss']:.8f}" if p else 'Not calibrated',f"{p['ece_10_equal_width_bins']:.8f}" if p else 'Not calibrated'])
    table(ax,['Pipeline','Macro-F1','Errors','Log loss','ECE (10 bins)'],rows,[.39,.14,.09,.19,.19],10)
    ax.set_title('Separate development candidate experiment (N = 2,399)')
    fig.text(.5,.04,'One fixed candidate; sigmoid calibration uses three grouped training folds.\nAll classification scores tie; probability diagnostics are confined to synthetic development data.\nCandidate models were not evaluated on the historical test partition.',ha='center',fontsize=10)
    fig.subplots_adjust(bottom=.27,top=.80);save(fig,'candidate_validation_results')
    fig,ax=plt.subplots(figsize=(9.3,4.8));languages=['Bisaya','Filipino','English','Mixed'];xx=np.arange(4)
    for j,(name,display) in enumerate([('svm','Linear SVM'),('nb','Naive Bayes')]):
        values=[metrics[name]['validation']['assigned_language_groups'][l]['macro avg']['f1-score'] for l in languages]
        bars=ax.bar(xx+(j-.5)*.35,values,width=.35,label=display,color=COLORS[j],hatch='' if j==0 else '///',edgecolor='black',linewidth=.5)
        for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.015,f'{v:.4f}',ha='center',rotation=90,fontsize=10)
    ax.set_xticks(xx,[l+'\nN = '+str(metrics['svm']['validation']['assigned_language_groups'][l]['n']) for l in languages]);ax.set_ylim(0,1.16);ax.set_ylabel('Validation Macro-F1');ax.set_title('Assigned-language subgroup results');ax.legend(loc='lower right');fig.tight_layout();save(fig,'language_group_validation')
    for filename,stem,xkey,ykeys,title,xlabel,ylabel in [
        ('learning_curve_v2.csv','svm_learning_curve','train_n',['training_macro_f1','validation_macro_f1'],'Reference SVM learning curve','Training records','Macro-F1'),
        ('sgd_hinge_loss_v2.csv','auxiliary_sgd_loss','epoch',['training_hinge_loss','validation_hinge_loss'],'Separate auxiliary SGD hinge-loss diagnostic','Training pass (epoch)','Multiclass hinge loss')]:
        with (ROOT/'manuscript/source/results'/filename).open() as f:rr=list(csv.DictReader(f))
        fig,ax=plt.subplots(figsize=(8.4,4.8))
        for j,(key,display) in enumerate(zip(ykeys,['Training','Validation'])):
            ax.plot([float(r[xkey]) for r in rr],[float(r[key]) for r in rr],marker='o' if j==0 else 's',linestyle='-' if j==0 else '--',color=COLORS[j],label=display)
        ax.set_title(title);ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.grid(alpha=.2);ax.legend();fig.tight_layout();save(fig,stem)
    manifest={p.name:{'bytes':p.stat().st_size,'source':'Executed reference/candidate metrics, original-script rerun grid and grouped CV'} for p in sorted(FIG.iterdir()) if p.suffix in {'.png','.pdf','.svg'}}
    (FIG/'figure_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Generated',len(manifest),'publication figure files in results/figures/')


if __name__=='__main__':main()
