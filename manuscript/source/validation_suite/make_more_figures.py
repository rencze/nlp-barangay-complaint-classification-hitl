from pathlib import Path
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];FIG=R/'figures'; RES=R/'results'
plt.rcParams.update({'font.size':12,'axes.titlesize':15,'axes.labelsize':12,'figure.figsize':(8.5,5.3),'pdf.fonttype':42,'savefig.bbox':'tight'})
def save(n):
 plt.savefig(FIG/(n+'.pdf'),bbox_inches='tight',pad_inches=.15);plt.savefig(FIG/(n+'.png'),dpi=220,bbox_inches='tight',pad_inches=.15);plt.close()
# hyperparam all 18 means all 1.0, alternate graphical representation a table heatmap at 1.0
grid=pd.read_csv(RES/'hyperparameter_grid_v2.csv');ng=list(dict.fromkeys(grid.ngram))
mat=np.zeros((6,3));names=[]
for i,g in enumerate(ng):
 for j,df in enumerate([2,5,10]):
  names.append('N-grams '+g+'; min_df='+str(df))
  for k,c in enumerate([.1,1.,10.]):mat[i*3+j,k]=grid[(grid.ngram==g)&(grid.min_df==df)&(grid.C==c)].cv_mean_macro_f1.iloc[0]
from matplotlib.patches import Rectangle
fig,ax=plt.subplots(figsize=(10,5.4))
for i in range(6):
 for k in range(3):
  ax.add_patch(Rectangle((k-.46,i-.46),.92,.92,edgecolor='#7697AE',facecolor='#E6F2F8',linewidth=1.1))
  ax.text(k,i,f'{mat[i,k]:.4f}',ha='center',va='center',fontsize=12,fontweight='bold')
ax.set_xlim(-.55,2.55);ax.set_ylim(5.58,-.58);ax.set_xticks(range(3),['C = 0.1','C = 1','C = 10']);ax.set_yticks(range(6),names);ax.set_xlabel('LinearSVC regularization');ax.set_title('Three-fold grouped CV: every configuration tied at 1.0000')
for sp in ax.spines.values():sp.set_visible(False)
ax.tick_params(length=0);fig.tight_layout();save('m3_hyperparameter_matrix')
sgd=pd.read_csv(RES/'sgd_hinge_loss_v2.csv');fig,ax=plt.subplots(figsize=(8.5,5));ax.plot(sgd.epoch,sgd.validation_macro_f1,marker='o',markersize=5,linewidth=2);ax.set_xlabel('Training epoch (SGD diagnostic only)');ax.set_ylabel('Validation Macro-F1');ax.set_title('Validation classification performance during SGD optimization');ax.set_ylim(.94,1.0);ax.set_xticks([1,3,5,7,9,11,13,15]);ax.grid(alpha=.18);fig.tight_layout();save('m3_sgd_epoch_macro_f1')
