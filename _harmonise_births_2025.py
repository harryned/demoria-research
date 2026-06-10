#!/usr/bin/env python3
"""Harmonise full-year-2025 births between the tracker and the DATA blob that
feeds the Data Tables / Raw Data Explorer.

Sources of truth, in order:
  1. annual reporters: births_data.json ba.cur where ba.year==2025
  2. monthly reporters with a complete 2025 (12 numeric months in the input
     sheet): the sheet's 12-month sum
Overrides DATA.ind.births@2025 (and stamps nso_yrs.births) when the tracker
figure differs from the blob by >0.5%. Countries already NSO-overridden in the
blob whose value sits within 2% of the sheet sum are left alone (their annual
official figure is the better number, e.g. Japan).

2026 (current-year) data deliberately stays OUT of the blob and the bulk
downloads — it lives on the tracker only.
"""
import json, openpyxl, shutil

GLOBE='dhi_globe.html'
shutil.copy(GLOBE, GLOBE+'.bak_harmonise')

BD=json.load(open('public/births_data.json',encoding='utf-8'))
BC={c['iso']:c for c in BD['countries']}

# sheet: complete-2025 monthly sums
ws=openpyxl.load_workbook('Birth_Tracker_Input_EXPANDED.xlsx',data_only=True)['Births']
sheet25={}
for r in range(3,ws.max_row+1):
    iso=ws.cell(r,1).value; nm=ws.cell(r,2).value
    if not(iso and nm): continue
    vals=[ws.cell(r,c).value for c in range(16,28)]
    if sum(1 for v in vals if isinstance(v,(int,float)))==12:
        sheet25[iso]=round(sum(vals))

# targets
targets={}
for iso,c in BC.items():
    if c.get('ba') and c['ba'].get('year')==2025:
        targets[iso]=('annual',c['ba']['cur'])
    elif iso in sheet25:
        targets[iso]=('sheet12mo',sheet25[iso])

# parse blob
h=open(GLOBE,encoding='utf-8').read()
i=h.find('const DATA='); s=i+len('const DATA=')
d=0;p=s
while p<len(h):
    ch=h[p]
    if ch=='{':d+=1
    elif ch=='}':
        d-=1
        if d==0: e=p+1;break
    p+=1
DATA=json.loads(h[s:e])

# Hand-curated official annuals that must never be replaced by flash/sheet sums
# (different series concept — e.g. Japan: MHLW official annual vs monthly flash).
PRESERVE={'JPN'}

changed=[]; skipped=[]
for iso,(mode,fy) in sorted(targets.items()):
    dd=DATA.get(iso)
    if not dd or 2025 not in dd['yrs']: continue
    idx=dd['yrs'].index(2025)
    cur=dd['ind']['births'][idx]*1000
    rel=abs(cur-fy)/max(fy,1)
    if iso in PRESERVE:
        skipped.append((iso,'curated official annual, preserved')); continue
    already=2025 in (dd.get('nso_yrs',{}).get('births') or [])
    if already and rel<=0.02:
        skipped.append((iso,'already-overridden, within 2%')); continue
    if rel<=0.005:
        skipped.append((iso,'within 0.5%')); continue
    dd['ind']['births'][idx]=round(fy/1000,3)
    ny=dd.setdefault('nso_yrs',{})
    yl=ny.setdefault('births',[])
    if 2025 not in yl: yl.append(2025); yl.sort()
    changed.append((iso,mode,round(cur),fy,f"{(fy-cur)/cur*100:+.1f}%"))

new_blob=json.dumps(DATA,ensure_ascii=False,separators=(',',':'))
h2=h[:s]+new_blob+h[e:]
# integrity
assert h2.count('const GLOBE=')==1 and h2.count('const DATA=')==1
json.loads(new_blob)
open(GLOBE,'w',encoding='utf-8').write(h2)

print(f"changed {len(changed)} countries' FY2025 births in DATA:")
for c in changed: print("  ",c)
print(f"skipped {len(skipped)}:",[x[0] for x in skipped])
