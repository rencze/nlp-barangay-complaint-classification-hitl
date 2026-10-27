"""Local visual-QA contact sheets for rendered PDF pages; not evaluation evidence."""
from pathlib import Path
from PIL import Image, ImageDraw

root=Path('tmp/pdfs')
for directory in ['thesis','report','final_thesis','final_report','milestone2_thesis','milestone2_report']:
    files=sorted((root/directory).glob('page-*.png'))
    for start in range(0,len(files),12):
        sheet=Image.new('RGB',(1500,1760),'#cccccc')
        draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(files[start:start+12]):
            im=Image.open(path).convert('RGB');im.thumbnail((480,405))
            x=(j%3)*500+(500-im.width)//2;y=(j//3)*440
            sheet.paste(im,(x,y+25));draw.text(((j%3)*500+12,y+6),path.stem,fill='black')
        sheet.save(root/(directory+'_contact_'+str(start//12+1)+'.png'))
