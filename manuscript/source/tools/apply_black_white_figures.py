#!/usr/bin/env python3
"""Recolor the NINE methodology schematics in place, preserving vector text/shapes.

Keeps all quantitative graphs, validation charts and confusion matrices untouched.
"""
from pathlib import Path
import fitz
import re

SCHEMATICS = [
 'figures/conceptual_framework.pdf',
 'figures/dataset_pipeline.pdf',
 'figures/evaluation_design.pdf',
 'figures/m3_fold_design_diagram.pdf',
 'figures/diagram_framework.pdf',
 'figures/diagram_cv_workflow.pdf',
 'figures/diagram_testing_map.pdf',
 'figures/nlp_pipeline_readable.pdf',
 'figures/nlp_training_testing_readable.pdf',
]
N=rb'[+-]?(?:\d+(?:\.\d*)?|\.\d+)' 
RGB = re.compile(rb'('+N+rb')\s+('+N+rb')\s+('+N+rb')\s+(rg|RG)(?![a-zA-Z])')
GRAY = re.compile(rb'('+N+rb')\s+(g|G)(?![a-zA-Z])')
CMYK = re.compile(rb'('+N+rb')\s+('+N+rb')\s+('+N+rb')\s+('+N+rb')\s+(k|K)(?![a-zA-Z])')

def transform(b):
 def rgb(m):
  rgb=[float(m.group(i)) for i in (1,2,3)]
  cmd=m.group(4)
  if cmd==b'RG': return b'0 0 0 RG'
  # Preserve dark lettering as black and pastel boxes as white.
  luminance=0.2126*rgb[0]+0.7152*rgb[1]+0.0722*rgb[2]
  return b'1 1 1 rg' if luminance >=0.68 else b'0 0 0 rg'
 def gray(m):
  level=float(m.group(1)); cmd=m.group(2)
  if cmd==b'G':return b'0 G'
  return b'1 g' if level>=0.68 else b'0 g'
 def cmyk(m):
  c,y,m_,k=[float(m.group(i)) for i in (1,2,3,4)]
  cmd=m.group(5)
  if cmd==b'K':return b'0 0 0 1 K'
  v=(1-c)*(1-k)*.2126+(1-y)*(1-k)*.7152+(1-m_)*(1-k)*.0722
  return b'0 0 0 0 k' if v>=0.68 else b'0 0 0 1 k'
 b=RGB.sub(rgb,b)
 b=CMYK.sub(cmyk,b)
 b=GRAY.sub(gray,b)
 return b

if __name__ == '__main__':
    for fp in SCHEMATICS:
        p = Path(fp)
        src = fitz.open(p)
        for page in src:
            for xref in page.get_contents():
                content = src.xref_stream(xref)
                src.update_stream(xref, transform(content), compress=True)
        dst = p.with_suffix('.bwtmp.pdf')
        src.save(dst, garbage=4, deflate=True)
        src.close()
        dst.replace(p)
        print('CONVERTED', p)
