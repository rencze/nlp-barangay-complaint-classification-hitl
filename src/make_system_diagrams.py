"""Editable monochrome architecture and logical ER overview, not implemented software."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/diagrams';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})


def box(ax,x,y,w,h,text):
    ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='black',linewidth=1.1))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10,linespacing=1.4)


def arrow(ax,a,b,label=None):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'black','lw':1.1})
    if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,label,ha='center',fontsize=9,bbox={'facecolor':'white','edgecolor':'none','pad':1})


def save(fig,name):
    for ext in ['svg','pdf','png']:fig.savefig(OUT/(name+'.'+ext),dpi=360,bbox_inches='tight')
    plt.close(fig)


def route(ax,points,label=None,label_at=None):
    for a,b in zip(points[:-2],points[1:-1]):
        ax.plot([a[0],b[0]],[a[1],b[1]],color='black',linewidth=1.1)
    arrow(ax,points[-2],points[-1])
    if label:
        ax.text(*label_at,label,ha='center',fontsize=9,bbox={'facecolor':'white','edgecolor':'none','pad':1})


def main():
    fig,ax=plt.subplots(figsize=(12,9));ax.set(xlim=(0,12),ylim=(0,10));ax.axis('off')
    box(ax,0.3,8.5,3.1,.9,'Residents / authorized staff\nNext.js + TypeScript')
    box(ax,4.4,8.5,3.2,.9,'FastAPI modular monolith\nREST over HTTPS / RBAC')
    box(ax,8.6,8.5,3.1,.9,'PostgreSQL\nTransactional audit + outbox')
    arrow(ax,(3.4,8.95),(4.4,8.95));arrow(ax,(7.6,8.95),(8.6,8.95))
    box(ax,4.4,6.7,3.2,.9,'Versioned saved pipeline\nTF-IDF + Linear SVM')
    box(ax,.3,6.7,3.1,.9,'Urgent safety lane\nIndependent human handling')
    box(ax,8.6,6.7,3.1,.9,'Worker\nNotices / overdue / audits')
    arrow(ax,(6,8.5),(6,7.6));arrow(ax,(4.4,8.5),(1.85,7.6));arrow(ax,(10.15,8.5),(10.15,7.6))
    box(ax,1,4.7,4,.9,'Valid -> Accepted disposition\nCreate Unresolved case')
    box(ax,7,4.7,4,.9,'Suspicious / Spam\nAdministrator review')
    arrow(ax,(5.2,6.7),(3,5.6),'Valid');arrow(ax,(6.8,6.7),(9,5.6),'Review')
    arrow(ax,(7,5.15),(5,5.15),'Accept')
    box(ax,.6,2.8,4.8,.9,'Assign -> Ongoing -> verified Resolved\nReferral / overdue / reopen = events')
    box(ax,6.6,2.8,4.8,.9,'Clarify / reject with reason\nNew text version is independently labeled')
    arrow(ax,(3,4.7),(3,3.7));arrow(ax,(9,4.7),(9,3.7))
    box(ax,.6,.7,3.1,1,'Quality-screened\nverified-label pool')
    box(ax,4.45,.7,3.1,1,'Authorized offline\ntraining + evaluation')
    box(ax,8.3,.7,3.1,1,'Approval gate\nVersion registry + rollback')
    route(ax,[(7.2,4.7),(5.95,4.1),(5.95,2.15),(2.15,2.15),(2.15,1.7)],'Verified labels',(5.95,2.5))
    arrow(ax,(3.7,1.2),(4.45,1.2));arrow(ax,(7.55,1.2),(8.3,1.2))
    route(ax,[(11.4,1.2),(11.9,1.2),(11.9,6.15),(7.95,6.15),(7.95,7.15),(7.6,7.15)],'Approved model',(10,6.25))
    ax.text(6,9.8,'Proposed system integration and governance',ha='center',fontsize=16,fontweight='bold')
    ax.text(6,.1,'Research model validation does not establish application or operational HITL validation.',ha='center',fontsize=10)
    save(fig,'system_architecture')
    fig,ax=plt.subplots(figsize=(12,10));ax.set(xlim=(0,12),ylim=(0,11));ax.axis('off')
    blocks=[(.3,8.9,3.3,1.1,'USERS / ROLES / PERMISSIONS\nPK user_id; unique email\nSessions + role mappings'),
      (4.35,8.9,3.3,1.1,'COMPLAINTS\nPK id; FK resident_id\nUnique tracking reference'),
      (8.4,8.9,3.3,1.1,'NARRATIVE_VERSIONS\nPK id; FK complaint_id\nUnique (complaint, version)'),
      (.3,6.4,3.3,1.1,'MODEL_VERSIONS\nFK training_run_id\nArtifact hash + approval'),
      (4.35,6.4,3.3,1.1,'PREDICTIONS\nFK narrative + model\nPredicted label / probabilities?'),
      (8.4,6.4,3.3,1.1,'REVIEWS + VERIFIED_LABELS\nFK narrative / reviewer\nVerified label is separate'),
      (.3,3.9,3.3,1.1,'DISPOSITIONS\nFK complaint + narrative\nAccept / clarify / reject'),
      (4.35,3.9,3.3,1.1,'ACCEPTED_CASES\nUnique FK complaint_id\nUnresolved / Ongoing / Resolved'),
      (8.4,3.9,3.3,1.1,'CLARIFICATION REQUESTS\nRESPONSES -> new narrative\nFK request + complaint'),
      (.3,1.3,3.3,1.1,'FEEDBACK + TRAINING RUNS\nVerified label -> eligibility\nFrozen run-example membership'),
      (4.35,1.3,3.3,1.1,'CASE ASSIGNMENTS / ACTIONS\nSTATUS_TRANSITIONS\nFK case / officer / policy'),
      (8.4,1.3,3.3,1.1,'NOTIFICATIONS / AUDIT\nOUTBOX_JOBS\nFK actor / complaint / event')]
    for b in blocks:box(ax,*b)
    arrow(ax,(3.6,9.45),(4.35,9.45),'1:N');arrow(ax,(7.65,9.45),(8.4,9.45),'1:N')
    arrow(ax,(10.05,8.9),(6,7.5),'1:N');arrow(ax,(3.6,6.95),(4.35,6.95),'1:N');arrow(ax,(7.65,6.95),(8.4,6.95),'1:N')
    arrow(ax,(10.05,8.9),(10.05,7.5),'1:N')
    route(ax,[(4.35,9.1),(3.9,9.1),(3.9,5.5),(1.95,5.5),(1.95,5)],'1:N',(3.9,8.0))
    arrow(ax,(3.6,4.45),(4.35,4.45),'Accepted');arrow(ax,(10.05,6.4),(10.05,5),'1:N')
    arrow(ax,(6,3.9),(6,2.4),'1:N')
    route(ax,[(.3,1.85),(.1,1.85),(.1,6.95),(.3,6.95)])
    route(ax,[(8.4,6.65),(8,6.65),(8,3.0),(1.95,3.0),(1.95,2.4)],'Quality screen',(4,3.1))
    arrow(ax,(7.65,4.45),(10.05,2.4),'Events')
    ax.text(6,10.6,'Logical relational model: key entities and separation',ha='center',fontsize=16,fontweight='bold')
    ax.text(6,.45,'Arrows show selected FK relationships; full cardinalities: database.mmd.\nRoadmap specifies all tables, consistency rules, indices and transaction gates.',ha='center',fontsize=10)
    save(fig,'database_overview')


if __name__=='__main__':main()
