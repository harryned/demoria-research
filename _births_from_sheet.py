#!/usr/bin/env python3
"""
Demoria Research — populate Birth Tracker tiles from the manual input sheet.

Reads Birth_Tracker_Input.xlsx and writes births into public/births_data.json:
  • Monthly: takes the leading run of months filled in BOTH 2025 and 2026,
    sums each, sets b25/b26/mon  -> tile shows "first N months, ±X%".
  • Annual only: if no monthly 2026 but FY2025+FY2026 present, sets the
    annual block (ba) -> tile shows "2026 full year, ±X%".
  • Blank rows are left as-is ("awaiting release").

Usage:
  python3 _births_from_sheet.py            # dry run (prints what would change)
  python3 _births_from_sheet.py --write    # write into births_data.json
"""
import json, sys
from openpyxl import load_workbook

SHEET='Birth_Tracker_Input.xlsx'; DATA='public/births_data.json'
M25=range(4,16)    # cols D..O   (2025 Jan..Dec)
M26=range(16,28)   # cols P..AA  (2026 Jan..Dec)
FY25=28; FY26=29   # cols AB, AC
SRC=30             # col AD

def num(v):
    if v is None: return None
    if isinstance(v,(int,float)): return int(round(v))
    s=str(v).strip().replace(',','').replace(' ','')
    if not s: return None
    try: return int(round(float(s)))
    except: return None

def parse():
    wb=load_workbook(SHEET, data_only=True)
    ws=wb['Births']
    out={}
    for row in ws.iter_rows(min_row=3):
        iso=row[0].value
        if not iso or len(str(iso).strip())!=3: continue   # skip region banners / blanks
        iso=str(iso).strip()
        m25=[num(row[c-1].value) for c in M25]
        m26=[num(row[c-1].value) for c in M26]
        src=row[SRC-1].value
        # leading run of months present in BOTH years
        run=0
        for a,b in zip(m25,m26):
            if a is not None and b is not None: run+=1
            else: break
        if run>0:
            out[iso]={'mode':'monthly','b25':sum(m25[:run]),'b26':sum(m26[:run]),'mon':run,'src':src}
            continue
        fy25=num(row[FY25-1].value); fy26=num(row[FY26-1].value)
        if fy25 is not None and fy26 is not None:
            out[iso]={'mode':'annual','prev':fy25,'cur':fy26,'year':2026,'src':src}
    return out

def merge(parsed, write=False):
    data=json.load(open(DATA,encoding='utf-8'))
    by={c['iso']:c for c in data['countries']}
    changed=[]
    for iso,r in parsed.items():
        c=by.get(iso)
        if not c: print(f"  ! {iso} not in dataset, skipped"); continue
        if r['mode']=='monthly':
            c['b25']=r['b25']; c['b26']=r['b26']; c['mon']=r['mon']; c['ba']=None
            chg=(r['b26']-r['b25'])/r['b25']*100 if r['b25'] else 0
            changed.append((iso,f"{r['b26']:,} vs {r['b25']:,} ({r['mon']}mo)  {chg:+.1f}%"))
        else:
            c['ba']={'year':r['year'],'prev':r['prev'],'cur':r['cur']}; c['b25']=None; c['b26']=None; c['mon']=None
            chg=(r['cur']-r['prev'])/r['prev']*100 if r['prev'] else 0
            changed.append((iso,f"FY {r['cur']:,} vs {r['prev']:,}  {chg:+.1f}%"))
        if r.get('src'): c['births_source']=str(r['src'])
    if write and changed:
        data['updated']=__import__('datetime').date.today().isoformat()
        json.dump(data,open(DATA,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    return changed

if __name__=='__main__':
    write='--write' in sys.argv
    parsed=parse()
    changed=merge(parsed, write=write)
    if not changed:
        print("No births entered in the sheet yet — nothing to update.")
    else:
        print(f"{'WROTE' if write else 'Would update'} {len(changed)} countries:")
        for iso,msg in changed: print(f"  {iso}  {msg}")
        if not write: print("\nRun again with --write to apply, then deploy (cp + git push).")
