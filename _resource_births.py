#!/usr/bin/env python3
"""Re-source raw-data births from the ACTUAL reported annual figures
(Birth_Tracker_Input_EXPANDED.xlsx, with source URLs), replacing the
WPP-times-TFR-ratio modelled values that were mislabelled NSO.

Rules (2023-2025, where the modelling lived):
  * reported full-year figure in the sheet -> use it, tag NSO, record source
  * otherwise -> pure UN WPP births, untag (honestly WPP)
Natural change is then recomputed SINGLE-YEAR (births - deaths) from the
displayed columns, so the table is internally coherent. Source tag for
natural change: NSO if both births & deaths are NSO; DRE if it mixes a
national figure with UN deaths; WPP if both are WPP.

Deaths stay UN WPP (no national deaths collected) — documented on the page.
Run after the input sheet changes; idempotent."""
import json, openpyxl, warnings, shutil
warnings.filterwarnings('ignore')
GLOBE='dhi_globe.html'
shutil.copy(GLOBE, GLOBE+'.bak_resrc')

WPP=json.load(open('_wpp_indicators_1960_2025.json'))

# reported annual births + provenance from the sheet
ws=openpyxl.load_workbook('Birth_Tracker_Input_EXPANDED.xlsx',data_only=True)['Births']
REP={}; SRC={}
for r in range(3,ws.max_row+1):
    iso=ws.cell(r,1).value
    if not iso: continue
    d={}
    for y,col in ((2023,40),(2024,41),(2025,42)):
        v=ws.cell(r,col).value
        if isinstance(v,(int,float)) and v>0: d[y]=round(v)
    # guard against partial-year entries mislabelled annual:
    #   2025 must be >=55% of 2024 (else it's a year-to-date sum)
    if 2025 in d and 2024 in d and d[2025] < 0.55*d[2024]: del d[2025]
    if d: REP[iso]=d
    if ws.cell(r,44).value: SRC[iso]=ws.cell(r,44).value

# parse DATA blob
h=open(GLOBE,encoding='utf-8').read()
i=h.find('const DATA='); s=i+len('const DATA=')
dep=0;p=s
while p<len(h):
    c=h[p]
    if c=='{':dep+=1
    elif c=='}':
        dep-=1
        if dep==0: e=p+1;break
    p+=1
DATA=json.loads(h[s:e])

PRESERVE={'UKR'}   # keep committed wartime birth overrides
def has(ny,key,y): return y in (ny.get(key) or [])

resourced=reset=0
for iso,m in DATA.items():
    yrs=m['yrs']; ny=m.setdefault('nso_yrs',{}); dy=m.setdefault('dre_yrs',{})
    bl=set(ny.get('births',[])); bd=set(dy.get('births',[]))
    rep=REP.get(iso,{})
    if iso not in PRESERVE:
        for y in (2023,2024,2025):
            if y not in yrs: continue
            idx=yrs.index(y)
            if y in rep:
                m['ind']['births'][idx]=round(rep[y]/1000,3); bl.add(y); bd.discard(y); resourced+=1
            else:
                w=WPP.get(iso,{}).get(str(y),{}).get('Births')
                if w is not None:
                    m['ind']['births'][idx]=round(w,3); bl.discard(y); bd.discard(y); reset+=1
    ny['births']=sorted(bl);
    if bd: dy['births']=sorted(bd)
    elif 'births' in dy: del dy['births']

    # ---- single-year natural change (K), recomputed for ALL years ----
    ncN=set(); ncD=set()
    for k,yy in enumerate(yrs):
        b=m['ind']['births'][k]; de=m['ind']['deaths'][k]
        if b is None or de is None:
            m['ind']['natch5'][k]=None; continue
        m['ind']['natch5'][k]=round(b - de/1000.0,3)
        bsrcN=has(ny,'births',yy); dsrcN=has(ny,'deaths',yy)
        if bsrcN and dsrcN and not has(dy,'births',yy) and not has(dy,'deaths',yy):
            ncN.add(yy)                                   # both national -> NSO
        elif bsrcN or dsrcN:
            ncN.add(yy); ncD.add(yy)                      # national births w/ UN deaths -> DRE synthesis
    if ncN: ny['natch5']=sorted(ncN)
    elif 'natch5' in ny: del ny['natch5']
    if ncD: dy['natch5']=sorted(ncD)
    elif 'natch5' in dy: del dy['natch5']

# splice + write source map for the data page
new=json.dumps(DATA,ensure_ascii=False,separators=(',',':'))
h2=h[:s]+new+h[e:]
assert h2.count('const GLOBE=')==1 and h2.count('const DATA=')==1
open(GLOBE,'w',encoding='utf-8').write(h2)
json.dump(SRC,open('_births_sources.json','w'),ensure_ascii=False)
print(f"resourced {resourced} reported births, reset {reset} to WPP; natural change recomputed single-year")
# verification
m=DATA['FRA']; yy=m['yrs']
for y in (2023,2024,2025):
    k=yy.index(y); b=m['ind']['births'][k]; de=m['ind']['deaths'][k]; nc=m['ind']['natch5'][k]
    print(f"  FRA {y}: births={b*1000:,.0f} deaths={de:,.0f} natch={nc:+.1f}k  (nso_births={y in DATA['FRA']['nso_yrs'].get('births',[])})")
m=DATA['MDA']; yy=m['yrs']
for y in (2024,2025):
    k=yy.index(y); print(f"  MDA {y}: births={m['ind']['births'][k]*1000:,.0f} deaths={m['ind']['deaths'][k]:,.0f} natch={m['ind']['natch5'][k]:+.1f}k")
