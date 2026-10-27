import svgwrite, cairosvg
from pathlib import Path
W,H=1380,1870
out=Path('/mnt/data/integration_work/figures/system_integration_final.svg')
d=svgwrite.Drawing(str(out), size=(f'{W}px',f'{H}px'), viewBox=f'0 0 {W} {H}')
d.add(d.rect(insert=(0,0), size=(W,H), fill='white'))
marker=d.marker(insert=(9,4),size=(10,8),orient='auto',id='arrow')
marker.add(d.path(d='M0,0 L9,4 L0,8 Z', fill='black'))
d.defs.add(marker)
font='Liberation Serif, Times New Roman, serif'

def txt(x,y,s,size=18,bold=False,anchor='middle',italic=False):
    d.add(d.text(s,insert=(x,y),font_family=font,font_size=size,font_weight='bold' if bold else 'normal',font_style='italic' if italic else 'normal',text_anchor=anchor,fill='#111111'))
def box(x,y,w,h,lines, stroke=1.8):
    d.add(d.rect(insert=(x,y),size=(w,h),fill='white',stroke='black',stroke_width=stroke))
    # lines: string or tuple (str,size,bold), array
    if isinstance(lines,str):lines=[lines]
    specs=[(v if isinstance(v,tuple) else (v,18,False)) for v in lines]
    linegap=24
    yy=y+h/2-(len(specs)-1)*linegap/2+6
    for i,(s,sz,bd) in enumerate(specs):txt(x+w/2,yy+i*linegap,s,sz,bd)
def diamond(cx,cy,rx,ry,lines):
    d.add(d.polygon(points=[(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)],fill='white',stroke='black',stroke_width=1.8))
    if isinstance(lines,str):lines=[lines]
    for i,s in enumerate(lines): txt(cx,cy-(len(lines)-1)*13+6+i*26,s,19,True)
def arrow(coords,dashed=False):
    pts=' '.join((f'{x},{y}' if i==0 else f'L{x},{y}') for i,(x,y) in enumerate(coords))
    d.add(d.path(d='M'+pts,fill='none',stroke='black',stroke_width=1.8,stroke_dasharray='9,7' if dashed else 'none',marker_end=marker.get_funciri(),stroke_linejoin='round'))
def line(coords,dashed=False):
    pts=' '.join((f'{x},{y}' if i==0 else f'L{x},{y}') for i,(x,y) in enumerate(coords))
    d.add(d.path(d='M'+pts,fill='none',stroke='black',stroke_width=1.7,stroke_dasharray='8,6' if dashed else 'none'))
def section(x,y,w,h,title):
    d.add(d.rect(insert=(x,y),size=(w,h),fill='none',stroke='#555555',stroke_width=1.2,stroke_dasharray='8,6'))
    # white title bg to interrupt dashed line
    textwidth=len(title)*10+24
    d.add(d.rect(insert=(x+20,y-13),size=(textwidth,28),fill='white'))
    txt(x+24,y+8,title,18,True,anchor='start')

# header
# no figure number embedded
txt(W/2,45,'System Integration Architecture for Barangay Complaint Reporting',28,True)
txt(W/2,78,'Proposed application components, data boundaries and controlled model updates',18,False)

# presentation layer
section(74,113,1230,197,'Presentation Layer')
box(99,143,505,56, [('RESIDENT',20,True),('Authenticated account and complaint tracking',17,False)])
box(774,143,505,56,[('BARANGAY ADMINISTRATOR',20,True),('Authorized review and case-management actions',17,False)])
box(99,224,505,62,[('Resident Portal  (Next.js / TypeScript)',19,True),('Complaint submission and case-status viewing',17,False)])
box(774,224,505,62,[('Administrator Dashboard  (Next.js / TypeScript)',19,True),('Review, disposition, progress tracking and model controls',16,False)])
arrow([(351,199),(351,224)]);arrow([(1026,199),(1026,224)])

# application layer
section(74,330,1230,784,'Online Application and Classification Services')
box(345,356,690,80,[('Application API  (FastAPI / Python)',20,True),('Access control, input validation, secure persistence',17,False),('and administrative audit logging',17,False)])
arrow([(351,286),(351,319),(530,319),(530,356)])
arrow([(1026,286),(1026,319),(835,319),(835,356)])

# ML stack
section(108,481,555,315,'Text-Only Inference (Proposed)')
box(149,508,473,63,[('Meaning-Preserving NLP',19,True),('Privacy-aware processing of complaint narrative',16,False)])
box(149,605,473,61,[('Fitted Word + Character TF-IDF',19,True),('Numerical feature transformation',16,False)])
box(149,697,473,62,[('Saved Calibrated Linear SVM',19,True),('Predicted class and class probabilities',16,False)])
arrow([(690,436),(690,461),(385,461),(385,508)])
arrow([(385,571),(385,605)]);arrow([(385,666),(385,697)])

# decision with HITL
arrow([(385,759),(385,830)])
diamond(385,900,158,70,['Predicted','Valid?'])
box(808,832,430,108,[('HITL Review: Suspicious / Spam',19,True),('Administrator confirms or corrects text label',16,False),('Accept / Request Clarification / Reject',16,False)])
arrow([(543,900),(808,900)])
txt(682,884,'No',17,True)

# cases and dispositions
box(141,1052,503,86,[('Accepted Case Management',20,True),('Unresolved → Ongoing → Resolved',18,False),('Assignment, overdue escalation and reconsideration',16,False)])
box(807,1052,431,86,[('Non-Accepted Submission',19,True),('Pending clarification or documented rejection',17,False),('Kept separate from accepted case status',16,False)])
arrow([(385,970),(385,1052)])
txt(406,1002,'Yes: predicted Valid',16)
arrow([(906,940),(906,1004),(584,1004),(584,1052)])
txt(745,994,'Accepted after review',16)
arrow([(1116,940),(1116,1052)])
txt(1157,996,'Other',16)

# Records layer
section(74,1180,1230,207,'Separated Persisted Records')
box(111,1220,543,128,[('Complaint / Case Database  (PostgreSQL)',19,True),('Submission versions, model predictions,',17,False),('administrative disposition, responsible officer,',17,False),('case statuses, action logs and audit history',17,False)])
box(737,1220,543,128,[('Human-Verified Feedback Pool',19,True),('Reviewable narrative version + verified text label',17,False),('Prediction corrections, source, provenance,',17,False),('eligibility and audit metadata',17,False)])
arrow([(385,1138),(385,1220)])
arrow([(1022,1138),(1022,1190),(608,1190),(608,1220)])
# feedback arrow from review to records on right margin (no crossing case)
arrow([(1238,886),(1308,886),(1308,1206),(1213,1206),(1213,1220)])
# tracking is delivered through API, described not arrow across diagram

# offline section
section(74,1405,1230,400,'Offline Model Maintenance — Not Triggered by Each Complaint')
box(739,1440,530,76,[('Quality Review and Dataset Consolidation',19,True),('Existing training data + eligible verified examples',16,False)])
box(739,1550,530,75,[('Candidate TF-IDF–SVM Training and Validation',19,True),('Recalibrate; compare against predefined release criteria',16,False)])
diamond(1006,1708,152,65,['Validated and','approved?'])
box(122,1682,498,91,[('Versioned Model Artifact Registry',19,True),('NLP configuration, TF-IDF vectorizers,',17,False),('Linear SVM and probability calibrator',17,False)])
arrow([(1006,1348),(1006,1440)],dashed=True)
arrow([(1006,1516),(1006,1550)])
arrow([(1006,1625),(1006,1643)])
arrow([(854,1708),(620,1708)])
txt(736,1694,'Yes',16,True)
# no branch stays existing; label, not extra large process
arrow([(1158,1708),(1265,1708)])
txt(1236,1673,'No',17,True)
txt(1251,1743,'Retain existing',16)
txt(1251,1763,'deployed model',16)
# approved bundle link to SVM, outside all boxes
line([(122,1723),(42,1723),(42,728)],dashed=True)
arrow([(42,728),(149,728)],dashed=True)
txt(51,1507,'Approved version',16,False,anchor='start')
txt(51,1527,'for future',16,False,anchor='start')
txt(51,1547,'predictions',16,False,anchor='start')
# note in foot (not part of figure naming)
txt(W/2,1840,'Solid arrows: operational flow    Dashed arrows: reviewed-data transfer or approved offline model release',17,False)

d.save()
cairosvg.svg2pdf(url=str(out),write_to='/mnt/data/integration_work/figures/system_integration_final.pdf')
cairosvg.svg2png(url=str(out),write_to='/mnt/data/integration_work/figures/system_integration_final.png',output_width=1380,output_height=1870)
print(out)
