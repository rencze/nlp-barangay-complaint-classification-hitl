import csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
urls={
'LAW-7160':('Republic Act 7160, Local Government Code of 1991, sections 16 and 17','https://officialgazette.gov.ph/1991/10/10/republic-act-no-7160/','Community issue scope, public services, public order, and potential referral; not a 60-label taxonomy'),
'LAW-9003':('RA 9003, Ecological Solid Waste Management Act','https://lawphil.net/statutes/repacts/ra2001/ra_9003_2001.html','Solid waste handling and environmental concern domain'),
'LAW-10121':('RA 10121, Disaster Risk Reduction and Management Act','https://lawphil.net/statutes/repacts/ra2010/ra_10121_2010.html','Local hazards, evacuation, disaster response'),
'LAW-9262':('RA 9262, Anti-Violence Against Women and Their Children Act','https://pcw.gov.ph/faq-republic-act-9262/','Violence-related incident and protection. No barangay mediation.'),
'LAW-11768':('RA 11768, SK Reform amendments','https://lawphil.net/statutes/repacts/ra2022/ra_11768_2022.html','SK programs and youth governance'),
'LAW-12010':('RA 12010, Anti-Financial Account Scamming Act','https://lawphil.net/statutes/repacts/ra2024/ra_12010_2024.html','Examples of financial account fraud and social engineering'),
'DCR-2024':('Davao City Reports official complaint platform','https://reports.davaocity.gov.ph/','Report, request, inquiry channels and required complaint details'),
'DCR-CHARTER':('City Government of Davao 2024 Revised Citizens Charter','https://www.davaocity.gov.ph/wp-content/uploads/2024/05/CITY-GOVERNMENT-OF-DAVAO_REVISED-CC_VOLUME-I_20240426.pdf','Administrative complaint handling and routing procedures'),
'LANG-2016':('De Leon and Parina 2016 A Study of Filipino Complaints in English and Tagalog','https://doi.org/10.17576/3L-2016-2201-15','Complaint semantic formulas and English/Tagalog expression'),
'LANG-2025':('Porlas 2025 Grammar Rules for Code-Switched Philippine Language Texts','https://doi.org/10.30564/fls.v7i10.11632','Natural grammatical patterns of Filipino, Cebuano and Surigaonon code switching, not barangay prevalence'),
'COMPLAINT-2024':('Quimbo et al. 2024 Impoliteness and Complaint Strategies in Anonymous Online Discourse','https://doi.org/10.54536/jnll.v2i1.3019','Speech acts, direct criticism and impoliteness in 60 online complaint posts'),
'SCAM-2024':('Ibanez 2024 Scammer Strategies and Social Actions in Online Filipino Transactions','https://doi.org/10.53899/spjrd.v29i1.287','Observed persuasion and linguistic tactics in ten failed Filipino scam interactions'),
'SYNTH-2025':('Chim et al. 2025 Evaluating Synthetic Data Generation from User Generated Text','https://doi.org/10.1162/coli_a_00540','Style, meaning, divergence assessment rather than authenticity claims'),
'CTRL-2020':('Ribeiro et al. 2020 Beyond Accuracy CheckList','https://aclanthology.org/2020.acl-main.442/','Behavioral challenge tests and systematic model weaknesses'),
'SYNTH-2024':('Long et al. 2024 LLMs-driven Synthetic Data Generation Curation and Evaluation survey','https://aclanthology.org/2024.findings-acl.658/','Controlled data generation and curation framework'),
'NEG-2020':('Huang et al. 2020 Counterfactually-Augmented SNLI Training Data Does Not Yield Better Generalization','https://aclanthology.org/2020.insights-1.13/','Synthetic augmentation is not guaranteed to improve robustness'),
'TEMPL-2024':('Shaib et al. 2024 Syntactic Templates in Generated Text','https://aclanthology.org/2024.emnlp-main.368/','Investigate syntactic repetition and artificial templates'),
'RUBRIC-V2':('Researcher-created text-only label rubric V2','../documents/LABELING_GUIDELINES.md','Research-specific judgment rules, not externally validated official categories'),
'SPAM-2024':('RA 12010 with research operational spam rubric','https://lawphil.net/statutes/repacts/ra2024/ra_12010_2024.html','Financial scams plus researcher-defined unrelated submissions; does not validate all spam types')
}
spec={1:'LAW-9003',2:'LAW-9003',3:'LAW-7160',4:'LAW-10121',5:'LAW-7160',6:'LAW-7160',
7:'LAW-7160',8:'LAW-7160',9:'LAW-7160',10:'LAW-7160',11:'LAW-7160',12:'LAW-7160',13:'LAW-7160',
14:'LAW-7160',15:'LAW-7160',16:'LAW-7160',17:'LAW-7160',18:'LAW-7160',19:'LAW-7160',20:'LAW-7160',21:'LAW-7160',
22:'LAW-7160',23:'LAW-7160',24:'LAW-7160',25:'LAW-7160',26:'LAW-7160',27:'LAW-7160',28:'LAW-7160',29:'LAW-7160',30:'LAW-9262',31:'LAW-7160',
32:'LAW-7160',33:'LAW-7160',34:'LAW-7160',35:'LAW-10121',36:'LAW-7160',37:'LAW-7160',38:'LAW-7160',39:'LAW-7160',40:'LAW-7160',41:'LAW-7160',42:'LAW-7160',43:'LAW-7160',44:'LAW-10121',45:'LAW-7160',46:'LAW-12010',47:'LAW-7160',48:'LAW-7160',49:'LAW-7160',50:'LAW-7160',51:'LAW-11768',52:'LAW-7160',53:'LAW-7160',54:'LAW-7160',55:'LAW-7160',56:'LAW-7160',57:'LAW-7160',58:'LAW-7160',59:'LAW-7160',60:'LAW-7160'}
with open(ROOT/'references'/'CATEGORY_REGISTER.csv',encoding='utf-8-sig') as f:items=list(csv.DictReader(f))
rows=[]
for c in items:
 label=c['classification'];idx=int(c['category_id'].split('-')[1]);
 if label=='Valid':
  p=spec[idx]; typ='Legal or governance domain basis';st='Broad documented domain; exact subcategory researcher-defined';gap='Check additional specialist law or local ordinance for precise jurisdiction' if p=='LAW-7160' else 'Law supports domain but not this exact synthetic scenario'
 elif label=='Suspicious':
  p='DCR-2024' if idx<=12 or idx>=19 else 'RUBRIC-V2';typ='Administrative procedure + operational annotation';st='Operationally motivated; not independently validated taxonomy';gap='Expert adjudication of category-specific boundary cases remains needed'
 else:
  p='SCAM-2024' if 7<=idx<=12 else 'RUBRIC-V2';typ='Scam language and Philippine research' if 7<=idx<=12 else 'Operational spam/no-report definition';st='Research observed Filipino scam language; not category prevalence' if 7<=idx<=12 else 'Researcher-defined class coverage, not official legal spam category';gap='Requires external review of examples and prevalence not inferred'
 rows.append({'classification':label,'category_id':c['category_id'],'category':c['category'],'definition':c['definition'],'primary_evidence_id':p,'primary_evidence_title':urls[p][0], 'primary_source_url':urls[p][1], 'evidence_kind':typ, 'evidence_strength_or_scope':st,'linguistic_basis_id':'LANG-2016;LANG-2025;COMPLAINT-2024', 'generation_method_basis_ids':'SYNTH-2024;SYNTH-2025;CTRL-2020;TEMPL-2024', 'source_to_category_rationale':f"{urls[p][2]}; researcher's {label} scenario-coverage operationalization",'evidence_gap':gap,'researcher_review_status':'Automated foundation assignment; requires legal/linguistic verification per category','expert_review':'Not performed'})
with open(ROOT/'references'/'SOURCE_TO_CATEGORY_EVIDENCE_MATRIX_V2.csv','w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
with open(ROOT/'references'/'SOURCE_REGISTER_V2.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['source_id','reference_title','url_or_relative_path','what_it_supports','limitations']);
 for id,(a,b,c) in urls.items():w.writerow([id,a,b,c,'Does not validate individual generated narratives or establish population prevalence.'])
print('category evidence rows',len(rows),'sources',len(urls))
