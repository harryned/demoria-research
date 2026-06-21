"""Refresh _globe_data.json from the rebuilt panel and re-embed it into
dhi_globe.html (between `const GLOBE=` and `;const HCX=`).

_globe_data.json carries enrichment (cat/catn/note/pop/cont/reg) absent from
the panel; that is left untouched. Everything else -- all scores and pillars
(history + projection waypoints), the proj trio, the per-variant projPil
arrays, and the 2025 rank -- is refreshed from the panel.

Pillars are stored frontend-side as [Fertility, AgeStruct, Renewal, Migration]
arrays; the panel emits them as dicts, so they are converted on the way in."""
import json

PORDER=('Fertility','AgeStruct','Renewal','Migration')
glb=json.load(open('_globe_data.json'))
panel=json.load(open('dhi_data_v2_unified.json'))['countries']
wpp=json.load(open('_wpp_indicators_1960_2025.json'))

def parr(p):
    return [p.get(k) for k in PORDER] if isinstance(p,dict) else p

changed=0
for num,e in glb.items():
    pc=panel.get(e['iso'])
    if not pc: continue
    e['scores']=dict(pc.get('scores',{}))
    e['pillars']={y:parr(p) for y,p in pc.get('pillars',{}).items()}
    if 'proj' in pc:
        e['proj']=pc['proj']
    if 'projPil' in pc:
        e['projPil']={wp:{v:parr(pl) for v,pl in trio.items()}
                      for wp,trio in pc['projPil'].items()}
    # sync 2025 population from WPP (incorporates any committed overrides)
    # NSO_POP: countries whose display population is re-based to the national
    # series (e.g. Moldova usual-resident, excl. Transnistria) — never WPP-reset.
    NSO_POP={'MDA':2.38,'UKR':30.0}
    if e['iso'] in NSO_POP:
        e['pop']=NSO_POP[e['iso']]
    else:
        p25 = wpp.get(e['iso'],{}).get('2025',{}).get('TPopulation1July')
        if p25 is not None: e['pop'] = round(p25/1000, 2)
    changed+=1

# recompute the 2025 rank (1 = highest DHI) across all entries
ranked=sorted([e for e in glb.values() if e.get('scores',{}).get('2025') is not None],
              key=lambda e:-e['scores']['2025'])
for i,e in enumerate(ranked): e['rank']=i+1

json.dump(glb,open('_globe_data.json','w'),separators=(',',':'))

blob=json.dumps(glb,separators=(',',':'))
h=open('dhi_globe.html').read()
a=h.find('const GLOBE=')+len('const GLOBE=')
b=h.find(';const HCX=')
assert a>len('const GLOBE=') and b>a, 'GLOBE/HCX markers not found'
h=h[:a]+blob+h[b:]
assert all(h.count(m)==1 for m in ('const GLOBE=',';const HCX=','const DATA=','const PROJD=','const PYR=','const TFR=','const FCAGE=')), 'splice integrity check failed - aborting'
open('dhi_globe.html','w').write(h)
print(f'globe data: {changed} entries refreshed; re-embedded into dhi_globe.html')
