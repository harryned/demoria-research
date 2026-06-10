#!/usr/bin/env python3
"""Typeset the DHI methodology essay as a versioned, citable PDF
(public/methodology/DHI-Methodology-v2.0.pdf) — title page with version,
date, URL and citation; body extracted from the same essay the site shows.
Upload to Zenodo for a DOI; bump METH_VERSION in _build_static_pages.py on revisions."""
import re, html, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, HRFlowable)

VERSION='2.0'; DATE='June 2026'
OUT='public/methodology/DHI-Methodology-v2.0.pdf'
NAVY=HexColor('#0c1a33'); GOLD=HexColor('#b58420'); MUT=HexColor('#5a6172')

# ---- extract the essay (same source as /methodology/) ----
h=open('dhi_globe.html',encoding='utf-8').read()
i=h.find('id="view-about"'); j=h.find('id="view-', i+20)
seg=h[i:j]
seg=seg[seg.find('<div class="essay">'):]
seg=re.sub(r'<script[\s\S]*?</script>','',seg)
seg=re.sub(r'<svg[\s\S]*?</svg>','',seg)
seg=re.sub(r'<button[\s\S]*?</button>','',seg)

# pull a linear sequence of (kind, text) blocks
blocks=[]
for m in re.finditer(r'<(h1|h2|p)[^>]*>([\s\S]*?)</\1>',seg):
    kind=m.group(1)
    txt=re.sub(r'<[^>]+>','',m.group(2))
    txt=html.unescape(txt).strip()
    txt=re.sub(r'\s+',' ',txt)
    if txt: blocks.append((kind,txt))
# part headers like "01 The index" appear as div/span pairs; capture them too
parts=re.findall(r'<span class="epart-num">([^<]*)</span><span class="epart-k">([^<]*)</span>',seg)

st_h1=ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=22,leading=27,textColor=NAVY,spaceAfter=10,spaceBefore=4)
st_h2=ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=14.5,leading=19,textColor=NAVY,spaceBefore=16,spaceAfter=6)
st_p =ParagraphStyle('p', fontName='Helvetica',fontSize=10.5,leading=15.5,textColor=HexColor('#222a3a'),spaceAfter=8)
st_eye=ParagraphStyle('eye',fontName='Courier-Bold',fontSize=8.5,leading=12,textColor=GOLD,spaceBefore=18,spaceAfter=4)
st_tc=ParagraphStyle('tc',fontName='Helvetica-Bold',fontSize=27,leading=33,textColor=NAVY,alignment=TA_CENTER)
st_ts=ParagraphStyle('ts',fontName='Helvetica',fontSize=12,leading=17,textColor=MUT,alignment=TA_CENTER,spaceBefore=10)
st_tm=ParagraphStyle('tm',fontName='Courier',fontSize=9.5,leading=14,textColor=MUT,alignment=TA_CENTER,spaceBefore=6)

def footer(canv,doc):
    canv.saveState()
    canv.setFont('Courier',7.5); canv.setFillColor(MUT)
    canv.drawString(22*mm,12*mm,f"Demoria Research · DHI Methodology v{VERSION} · {DATE}")
    canv.drawRightString(A4[0]-22*mm,12*mm,f"page {doc.page}")
    canv.restoreState()

doc=BaseDocTemplate(OUT,pagesize=A4,leftMargin=24*mm,rightMargin=24*mm,topMargin=22*mm,bottomMargin=22*mm,
                    title=f"The Demographic Health Index: Methodology (v{VERSION})",author="Demoria Research")
fr=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='f')
doc.addPageTemplates([PageTemplate(id='t',frames=[fr],onPage=footer)])

story=[Spacer(1,55*mm),
 Paragraph("The Demographic Health Index",st_tc),
 Paragraph("Methodology",st_tc),
 Paragraph(f"Version {VERSION} · {DATE}",st_ts),
 Paragraph("Demoria Research · demoriaresearch.com/methodology",st_tm),
 Spacer(1,28*mm),
 Paragraph(f"Cite as: Demoria Research ({DATE.split()[-1]}). The Demographic Health Index: Methodology (v{VERSION}). demoriaresearch.com/methodology. DOI: pending.",st_tm),
 Paragraph("Licence: free to reuse with attribution for journalism, research and education; commercial licensing by enquiry. demoriaresearch.com/licence",st_tm),
 PageBreak()]

pi=0
for kind,txt in blocks:
    if kind=='h1': continue                     # hero title already on the title page
    if kind=='h2':
        if pi<len(parts):
            story.append(Paragraph(f"{parts[pi][0]} · {parts[pi][1].upper()}",st_eye)); pi+=1
        story.append(Paragraph(txt,st_h2))
    else:
        story.append(Paragraph(txt,st_p))
story+=[Spacer(1,8*mm),HRFlowable(width='100%',thickness=0.6,color=GOLD),
 Paragraph("Data: UN World Population Prospects 2024; national statistical offices; Demoria Research estimations. "
           "Live data: demoriaresearch.com/births · profiles: demoriaresearch.com/country",st_tm)]

doc.build(story)
import os
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB, {len(blocks)} blocks)")
