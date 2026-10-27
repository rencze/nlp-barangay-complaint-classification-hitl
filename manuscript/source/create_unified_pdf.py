from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from pathlib import Path
p=Path('/mnt/data/m2_revision/figures/m2_unified_evaluation.pdf')
c=canvas.Canvas(str(p),pagesize=(580,625))
c.setTitle('Unified Group-Aware Experimental Evaluation Protocol')
def rect(x,y,w,h,lines,head=True,fs=10.5):
 c.setLineWidth(1.1);c.rect(x,y,w,h,stroke=1,fill=0)
 n=len(lines); lh=14.3
 for i,line in enumerate(lines):
  c.setFont('Times-Bold' if i==0 and head else 'Times-Roman',fs if i else fs+0.4)
  c.drawCentredString(x+w/2,y+h/2+(n-1)*lh/2-i*lh-3.3,line)
def arrow(x1,y1,x2,y2):
 c.setLineWidth(1);c.line(x1,y1,x2,y2)
 if abs(x2-x1)<0.1:
  d=1 if y2>y1 else -1
  pth=c.beginPath();pth.moveTo(x2,y2);pth.lineTo(x2-4,y2-7*d);pth.lineTo(x2+4,y2-7*d);pth.close();c.drawPath(pth,stroke=0,fill=1)
 else:
  d=1 if x2>x1 else -1
  pth=c.beginPath();pth.moveTo(x2,y2);pth.lineTo(x2-7*d,y2+4);pth.lineTo(x2-7*d,y2-4);pth.close();c.drawPath(pth,stroke=0,fill=1)
c.setFillColor(black)
c.setFont('Times-Bold',14);c.drawCentredString(290,598,'Unified Experimental Evaluation Protocol')
rect(105,525,370,54,['24,000 synthetic complaint narratives','8,000 Valid | 8,000 Suspicious | 8,000 Spam'],fs=12)
arrow(290,525,290,508)
rect(146,462,288,44,['Group-aware partitioning','Keep scenario families together'],fs=11)
# split branch
c.line(290,462,290,445);c.line(96,445,484,445)
for x in [96,290,484]:arrow(x,445,x,414)
rect(16,356,161,57,['Training (19,213)','80.05%','Fit models and features'],fs=10.7)
rect(209,356,161,57,['Validation (2,399)','10.00%','Held out from fitting'],fs=10.7)
rect(403,356,161,57,['Synthetic test (2,388)','9.95%','Previously evaluated'],fs=10.7)
for x in [96,290,484]:arrow(x,356,x,343)
rect(16,273,161,68,['3-fold grouped grid search','18 SVM configurations','on training only'],fs=10)
rect(209,273,161,68,['Fixed validation','Accuracy / P / R / F1','Confusion and subgroups'],fs=10)
rect(403,273,161,68,['Recorded test evaluation','Accuracy / P / R / F1','Exact McNemar test'],fs=10)
arrow(96,273,96,253)
rect(16,182,161,68,['Separate 5-fold grouped CV','Selected fixed classifiers','Stability; train only'],fs=10)
arrow(96,182,96,166)
rect(16,101,161,65,['Refit fixed SVM and NB','Full training partition','Apply only to held-out'],fs=10)
# relation annotation
c.setFont('Times-Roman',11)
c.drawString(202,224,'Validation and test scores use the')
c.drawString(202,210,'selected models trained at left.')
c.drawString(202,196,'No held-out vocabulary fitting.')
# simple dashed linked model to validation and test note footer
c.setDash(3,3);c.setLineWidth(.75)
c.line(177,134,532,134);c.line(532,134,532,273)
c.setDash()
c.setFont('Times-Italic',9.9)
c.drawCentredString(290,73,'Three-fold tuning and five-fold stability analysis use only the training partition.')
c.drawCentredString(290,58,'The original test partition has already been viewed: do not reuse it for later tuning.')
c.setLineWidth(.8);c.line(22,40,558,40)
c.save();print(p)
