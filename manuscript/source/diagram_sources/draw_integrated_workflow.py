from pathlib import Path
import svgwrite, cairosvg
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'figures'/'end_to_end_workflow.svg'
W,H=1280,2120
D=svgwrite.Drawing(str(out),size=(f'{W}px',f'{H}px'),viewBox=f'0 0 {W} {H}')
D.add(D.rect(insert=(0,0),size=(W,H),fill='white'))
font='Liberation Serif, Times New Roman, serif'
arrow_mark=D.marker(insert=(9,4),size=(10,8),orient='auto',id='arrow')
arrow_mark.add(D.path(d='M0 0 L9 4 L0 8 Z',fill='black'))
D.defs.add(arrow_mark)

def t(x,y,s,size=22,bold=False,anchor='middle'):
    D.add(D.text(s,insert=(x,y),font_family=font,font_size=size,font_weight='bold' if bold else 'normal',text_anchor=anchor,fill='#111'))
def rect(x,y,w,h,rows):
    D.add(D.rect(insert=(x,y),size=(w,h),stroke='#111',stroke_width=2,fill='white'))
    n=len(rows);step=29
    for i,row in enumerate(rows):
        if isinstance(row,str): row=(row,21,False)
        s,sz,b=row
        t(x+w/2,y+h/2-(n-1)*step/2+7+i*step,s,sz,b)
def diamond(cx,cy,rx,ry,rows):
    D.add(D.polygon(points=[(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)],stroke='#111',stroke_width=2,fill='white'))
    for i,s in enumerate(rows):t(cx,cy-(len(rows)-1)*14+7+i*29,s,22,True)
def path(points,dashed=False,head=True):
    pp='M'+' L'.join(f'{x},{y}' for x,y in points)
    attrib={'d':pp,'stroke':'#111','stroke_width':2,'fill':'none','stroke_linejoin':'round'}
    if dashed:attrib['stroke_dasharray']='8,7'
    if head:attrib['marker_end']=arrow_mark.get_funciri()
    D.add(D.path(**attrib))
def grouping(x,y,w,h,title):
    D.add(D.rect(insert=(x,y),size=(w,h),stroke='#666',stroke_width=1.5,stroke_dasharray='10,7',fill='none'))
    D.add(D.rect(insert=(x+18,y-14),size=(len(title)*10+30,29),fill='white'))
    t(x+26,y+8,title,19,True,'start')

# Figure has no numeric label; figure number assigned by LaTeX caption.
t(W/2,52,'Integrated Barangay Complaint Classification and Management Workflow',29,True)
t(W/2,85,'Live complaint processing and controlled offline model maintenance',21)
grouping(55,133,1170,930,'A. Live Complaint Processing')
rect(363,158,554,80,[('Resident Submits Complaint',24,True),('Subject and narrative; supporting context if available',20,False)])
rect(363,277,554,76,[('Meaning-Preserving NLP',24,True),('Prepare privacy-conscious narrative for text features',19,False)])
rect(363,389,554,75,[('Fitted Word + Character TF-IDF',24,True),('Transform text using saved vectorizers',20,False)])
rect(363,497,554,75,[('Saved, Calibrated Linear SVM',24,True),('Predict Valid / Suspicious / Spam',20,False)])
path([(640,238),(640,277)]);path([(640,353),(640,389)]);path([(640,464),(640,497)]);path([(640,572),(640,610)])
diamond(640,693,200,82,['Predicted Suspicious','or Spam?'])
# valid branch left
rect(84,849,440,82,[('Accepted Case Management',24,True),('Unresolved / Ongoing / Resolved',20,False)])
# human review right
rect(761,810,440,106,[('Human-in-the-Loop Review',24,True),('Verify or correct TEXT label',20,False),('Accept / Clarify / Reject independently',19,False)])
path([(440,693),(304,693),(304,849)]);t(336,746,'No: Valid',20,True)
path([(840,693),(981,693),(981,810)]);t(920,744,'Yes',20,True)
# review outcome branch
rect(761,969,440,70,[('Non-Accepted Outcome Record',21,True),('Pending clarification or documented rejection',18,False)])
path([(761,869),(524,869)])
t(647,852,'Accepted after review',18)
path([(1102,916),(1102,969)])
t(995,949,'Clarify / reject',18)
# bottom records outside online boundary
grouping(55,1104,1170,175,'B. Separate Operational and Training Records')
rect(81,1132,535,115,[('Case and Action Records',24,True),('Disposition; assignments; deadlines;',19,False),('actions; referrals; verified resolution',19,False)])
rect(666,1132,535,115,[('Versioned Human-Verified Labels',24,True),('Narrative version; verified class;',19,False),('correction reason; audit/provenance',19,False)])
# case branch to case db
path([(304,931),(304,1132)])
# nonaccepted -> case record
path([(1102,1039),(1102,1080),(585,1080),(585,1132)])
# review label transfer via right of online group
path([(1201,860),(1232,860),(1232,1100),(982,1100),(982,1132)],dashed=True)
# offline
grouping(55,1313,1170,750,'C. Controlled Offline Model Maintenance')
rect(680,1341,520,79,[('Quality Check and Consolidate Feedback',22,True),('Only eligible verified narrative labels',20,False)])
path([(933,1247),(933,1341)],dashed=True)
path([(940,1420),(940,1445)])
diamond(940,1521,205,76,['Retraining justified','and authorized?'])
rect(75,1473,475,99,[('No Candidate Training Run',22,True),('Keep collecting verified feedback',19,False),('and retain deployed model',19,False)])
path([(735,1521),(550,1521)])
t(650,1499,'No',20,True)
rect(680,1624,520,82,[('Train, Calibrate and Validate Candidate',22,True),('Consolidated training data; fixed validation protocol',19,False)])
path([(940,1597),(940,1624)]);t(969,1609,'Yes',19,True)
path([(940,1706),(940,1724)])
diamond(940,1782,187,69,['Passes release','criteria?'])
rect(75,1880,483,96,[('Retain Deployed Model',23,True),('Archive failed candidate; current version remains',19,False)])
rect(680,1880,520,96,[('Approve and Release Versioned Pipeline',21,True),('NLP + TF-IDF + SVM + calibrated model',19,False)])
path([(753,1782),(318,1782),(318,1880)]);t(573,1765,'No',20,True)
path([(940,1851),(940,1880)]);t(969,1869,'Yes',20,True)
# Arrow from approved bundle to saved deployed model, for FUTURE requests, not online learning.
path([(680,2018),(24,2018),(24,534),(363,534)],dashed=True)
t(78,1744,'Approved model for',18,False,'start')
t(78,1767,'future predictions only',18,False,'start')
t(W/2,2096,'Solid arrows: case flow     Dashed arrows: verified training feedback and approved model release',17)
D.save()
cairosvg.svg2pdf(url=str(out),write_to=str(out.with_suffix('.pdf')))
cairosvg.svg2png(url=str(out),write_to=str(out.with_suffix('.png')),output_width=1536)
print(out)
