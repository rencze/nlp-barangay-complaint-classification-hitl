from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
p=Path('/mnt/data/thesis_full_2026/shared/figures/conceptual_framework.pdf')
fig,ax=plt.subplots(figsize=(8.4,9.4));fig.patch.set_facecolor('white');ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
ax.text(.5,.965,'TWO-PHASE CONCEPTUAL FRAMEWORK',ha='center',va='center',fontsize=15,fontweight='bold')
def frame(y0,y1,heading):
 ax.add_patch(FancyBboxPatch((.04,y0),.92,y1-y0,boxstyle='round,pad=0.012',edgecolor='#637F96',facecolor='#FBFCFE',lw=1.15))
 ax.text(.07,y1-.028,heading,va='center',fontsize=12,fontweight='bold',color='#304F69')
def node(x,y,w,h,heading,details,kind='normal'):
 b={'normal':('#EAF3FA','#587D97'),'good':('#E2F3E9','#47825E'),'risk':('#FCF3E3','#B08B51')}[kind]
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.005',linewidth=1.05,edgecolor=b[1],facecolor=b[0]))
 ax.text(x+w/2,y+h*.68,heading,fontsize=10.2,ha='center',va='center',fontweight='bold')
 ax.text(x+w/2,y+h*.32,details,fontsize=8.6,ha='center',va='center',linespacing=1.3)
def arrow(x1,y1,x2,y2,color='#5B7D92',rad=0):
 ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=11,linewidth=1.2,color=color,connectionstyle=f'arc3,rad={rad}'))
frame(.53,.91,'PHASE I  |  RESEARCH, GENERATION AND MODEL SELECTION')
node(.08,.733,.36,.09,'Research evidence','Laws + complaint procedures\nLinguistic / spam studies')
node(.56,.733,.36,.09,'Scenario taxonomy','118 coverage categories\n3 intended labels + 4 languages')
node(.08,.603,.36,.09,'Controlled dataset','24,000 synthetic narratives\nVariation + audit metadata')
node(.56,.603,.36,.09,'Train and validate','TF-IDF + SVM / Naive Bayes\nGrouped CV + holdout tests')
node(.30,.538,.40,.043,'Versioned research model','Release requires approval',kind='good')
arrow(.44,.777,.56,.777);arrow(.74,.733,.74,.693);arrow(.26,.733,.26,.693);arrow(.44,.646,.56,.646);arrow(.74,.603,.52,.576)
frame(.07,.49,'PHASE II  |  CITIZEN REPORTING AND HUMAN GOVERNANCE (PROPOSED)')
node(.08,.33,.36,.085,'Citizen submission','Next.js / TypeScript\nNarrative + case metadata')
node(.56,.33,.36,.085,'Backend validation','FastAPI: schema, user rights\nUrgent referral bypass')
node(.08,.20,.36,.085,'Provisional classification','Versioned TF-IDF + SVM\nValid / Suspicious / Spam')
node(.56,.20,.36,.085,'Administrator review','Confirm, correct, refer\nRecord final decision')
node(.08,.085,.36,.065,'Auditable case record','PostgreSQL + state transitions')
node(.56,.085,.36,.065,'Quality-controlled feedback','Offline update + rollback',kind='risk')
arrow(.44,.372,.56,.372);arrow(.74,.33,.74,.285);arrow(.26,.33,.26,.285);arrow(.44,.242,.56,.242);arrow(.74,.2,.74,.15);arrow(.26,.2,.26,.15);arrow(.44,.118,.56,.118)
arrow(.5,.538,.5,.492,color='#47825E')
ax.text(.57,.504,'model release to live service',color='#47825E',fontsize=8)
ax.text(.52,.077,'Feedback is queued for later OFFLINE retraining, not automatic deployment',color='#956F3B',fontsize=8,ha='center')
plt.savefig(p,bbox_inches='tight',facecolor='white',pad_inches=.17)
plt.close(fig)
print(p,p.stat().st_size)
