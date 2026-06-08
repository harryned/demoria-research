#!/usr/bin/env python3
"""
APPLY OVERRIDES EVERYWHERE — overrides/tfr.csv -> every blob on the site.

Run after editing overrides/tfr.csv. Rebuilds from canonical sources and
propagates to all six places Japan/etc. are read from, so nothing is stale:
  GLOBE  world map colours, rankings, country-profile score/pillars/rank
  PROJD  raw-data explorer projection lines (override-aware DHI, WPP TFR path)
  DATA   raw-data explorer + Data-section values (ind.tfr / ind.nrr)
  DATA.nso_yrs   Data-section NSO/WPP badges
  TFR    provenance const (Data section)
  births_data.json  the /births Birth Tracker (run _births_from_sheet.py)

Idempotent: canonical rebuilds (panel/projections/PROJD/GLOBE) are
deterministic; DATA/TFR propagation only sets values that differ. Running
with no override change leaves the blobs byte-stable.

Usage:  python3 _apply_dhi_override.py [--deploy]
"""
import json, csv, subprocess, sys, shutil
HTML='dhi_globe.html'

def run(cmd):
    r=subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:]); print(r.stderr[-1500:]); raise SystemExit('FAILED: '+cmd)

def get(h,v,e):
    a=h.find('const '+v+'=')+len('const '+v+'=');b=h.find(e,a);return json.loads(h[a:b])
def splice(h,s,e,obj):
    a=h.find(s)+len(s);b=h.find(e,a);return h[:a]+json.dumps(obj,separators=(',',':'))+h[b:]

def embed_projd():
    js=open('_PROJD.js').read(); i=js.find('const PROJD=')+len('const PROJD=')
    P=json.loads(js[i:js.rfind(';')])
    h=open(HTML).read(); h=splice(h,'const PROJD=',';const PYR=',P); open(HTML,'w').write(h)

def propagate_display():
    ov={}
    for r in csv.DictReader(open('overrides/tfr.csv',encoding='utf-8')):
        try: ov[(r['iso3'],int(r['year']))]=float(r['value'])
        except: pass
    h=open(HTML).read()
    DATA=get(h,'DATA',';const FCAGE='); TFR=get(h,'TFR',';const DATA=')
    for (iso,y),val in ov.items():
        if iso in DATA and y in DATA[iso]['yrs']:
            i=DATA[iso]['yrs'].index(y); ind=DATA[iso]['ind']; old=ind['tfr'][i] if i<len(ind.get('tfr',[])) else None
            if old is not None and abs(old-val)>1e-9:
                if 'nrr' in ind and i<len(ind['nrr']) and ind['nrr'][i] and old:
                    ind['nrr'][i]=round(ind['nrr'][i]*val/old,3)
                ind['tfr'][i]=val
            for fld in ('tfr','nrr'):
                s=set(DATA[iso]['nso_yrs'].get(fld,[]))
                if y not in s: s.add(y); DATA[iso]['nso_yrs'][fld]=sorted(s)
        if iso in TFR:
            TFR[iso].setdefault('nso',{})[str(y)]=val
    h=splice(h,'const DATA=',';const FCAGE=',DATA)
    h=splice(h,'const TFR=',';const DATA=',TFR)
    mk=['const GLOBE=',';const HCX=','const PROJD=','const PYR=','const TFR=','const DATA=','const FCAGE=','const HCQ_DATA=']
    assert all(h.count(m)==1 for m in mk) and h.startswith('<!DOCTYPE html>')
    open(HTML,'w').write(h)

if __name__=='__main__':
    print("1/5 panel scores");        run('python3 _build_dhi_v2_panel.py >/dev/null')
    print("2/5 projection scores");    run('python3 _build_dhi_v2_projections.py >/dev/null')
    print("3/5 PROJD (canonical)");    run('python3 _build_explorer_projections.py >/dev/null'); embed_projd()
    print("4/5 GLOBE embed + rank");   run('python3 _build_globe_data.py >/dev/null')
    print("5/5 DATA + TFR provenance"); propagate_display()
    if '--deploy' in sys.argv:
        shutil.copy(HTML,'public/index.html'); shutil.copy(HTML,'public/dhi/index.html'); print("copied to public/")
    print("DONE — review, then git add -A && commit && push  (Birth Tracker: run _births_from_sheet.py --write separately)")
