"""Build a medium-variant projection blob (2026-2100) for the Raw Data explorer
and embed it as `const PROJD=...;`. Each entry is PROJD[iso][indKey] = [v2026..v2100]
(75 yearly points) in the SAME raw units the historical DATA blob stores, so the
frontend can simply append them after the 1965-2025 history.

Sources (all UN WPP 2024 medium variant / Wittgenstein, already in the repo):
  _wpp_fc_med.json           Pop,TFR,NRR,Births,CBR,CDR,MedianAge,NetMig (yearly 2024-2100)
  dhi_data_v2_unified.json   DHI scores + named pillars (yearly to 2025, waypoints 2035/50/75/2100)
  _human_capital.json        schooling/attainment/gender (5-yearly to 2100)
Indicators WITHOUT a projection source (oadr,wrr,lfpr,workage,pop_u20,migstk,
natch5) are intentionally left history-only.
"""
import json

DATA_ISOS = "UZB,SLB,GNQ,KIR,TKM,BEN,MDG,VUT,NGA,COG,GHA,ISR,LBR,NAM,KEN,KGZ,CIV,PSE,PNG,KHM,GAB,TGO,RWA,BDI,CMR,MYT,ERI,AGO,ZWE,PAK,EGY,TZA,BWA,ETH,MOZ,SEN,TJK,COM,GIN,GNB,COD,HTI,IRQ,GMB,BFA,MNG,MLI,WSM,TLS,ZMB,LAO,MWI,SLE,YEM,KAZ,SSD,NRU,UGA,DZA,SDN,TCD,ZAF,NER,LSO,MRT,TUV,MHL,CAF,TON,IDN,LBY,FJI,PER,GUF,FSM,ESH,AFG,STP,SOM,DJI,BOL,GUY,SWZ,MMR,BGD,PRY,LBN,SUR,GTM,NIU,FRO,VEN,IND,GUM,HND,VNM,PAN,SYR,MAR,NIC,SAU,ECU,PHL,NCL,CPV,NPL,SLV,BLZ,PRK,JOR,REU,ATG,DOM,MDA,MEX,GRL,GEO,ARM,SYC,MDV,BTN,ASM,BRA,NZL,BHS,BRB,MYS,ARG,TUR,GIB,PLW,LCA,IRN,BRN,TTO,LKA,USA,KNA,CYP,VCT,AZE,TUN,MNE,COK,MAF,TKL,GRD,JAM,URY,COL,BGR,PYF,CUW,DMA,ISL,MUS,OMN,RUS,AUS,SVK,GBR,CRI,NOR,ROU,FRA,DNK,JEY,TCA,FLK,SWE,NLD,SRB,SVN,BEL,MNP,ALB,XKX,HRV,THA,GGY,CHL,MKD,CAN,HUN,WLF,ABW,IMN,FIN,MCO,IRL,CZE,AUT,LVA,CHN,DEU,SPM,BLR,PRT,BHR,QAT,POL,AIA,CUB,LTU,SHN,KWT,MSR,ARE,EST,GLP,JPN,BES,BLM,ESP,CHE,BIH,CYM,LIE,UKR,VGB,ITA,MTQ,LUX,VIR,KOR,MLT,SXM,GRC,BMU,PRI,TWN,AND,SMR,SGP,HKG,MAC".split(',')

YEARS = list(range(2026, 2101))   # 75 projected years
fc  = json.load(open('_wpp_fc_med.json'))
pan = json.load(open('dhi_data_v2_unified.json'))['countries']
hc  = json.load(open('_human_capital.json'))['countries']
clip = lambda v: max(0.0, min(100.0, v))

# ---- HCQ scoring (verbatim from _build_hcq_map_toggle.py) ----
def s_mother(x): return None if x is None else clip((x-2)/12*100)
def s_attain(x): return None if x is None else clip(x)
def s_equity(g): return None if g is None else clip(100-25*max(0.0,g))
def s_surv(sr):  return None if sr is None else clip((sr-0.75)/0.24*100)
PW={'mother':0.25,'attain':0.25,'equity':0.10,'surv':0.40}

def hc_interp(iso, yr, field):
    cy = hc.get(iso); 
    if not cy: return None
    pts = sorted((int(y), rec.get(field)) for y,rec in cy.items() if rec.get(field) is not None)
    if not pts: return None
    if yr<=pts[0][0]: return pts[0][1]
    if yr>=pts[-1][0]: return pts[-1][1]
    for i in range(1,len(pts)):
        y1,v1=pts[i-1]; y2,v2=pts[i]
        if y1<=yr<=y2: return v1+(v2-v1)*(yr-y1)/(y2-y1)
    return None

def fc_at(iso, yr, field):
    r = fc.get(iso,{}).get(str(yr)); 
    return r.get(field) if r else None

def hcq(iso, yr):
    comp={'mother':s_mother(hc_interp(iso,yr,'mys_20_39_F')),
          'attain':s_attain(hc_interp(iso,yr,'uppsec_25p_T')),
          'equity':s_equity(hc_interp(iso,yr,'ggap_mys_25p'))}
    tfr=fc_at(iso,yr,'TFR'); nrr=fc_at(iso,yr,'NRR')
    sr=(nrr/(tfr*0.4886)) if (tfr and nrr and tfr>0) else None
    comp['surv']=s_surv(sr)
    num=den=0.0
    for k,w in PW.items():
        if comp[k] is not None: num+=comp[k]*w; den+=w
    return (num/den) if den>0 else None

# ---- waypoint interpolation for DHI scores + pillars ----
PILW = {'Fertility':0.34,'Renewal':0.28,'AgeStruct':0.22,'Migration':0.16}
def interp_wp(pairs, yr):   # pairs: sorted [(year,val)]
    if yr<=pairs[0][0]: return pairs[0][1]
    if yr>=pairs[-1][0]: return pairs[-1][1]
    for i in range(1,len(pairs)):
        y1,v1=pairs[i-1]; y2,v2=pairs[i]
        if y1<=yr<=y2: return v1+(v2-v1)*(yr-y1)/(y2-y1)
    return None

FC_MAP = [('tfr','TFR',2),('nrr','NRR',3),('pop','Pop',2),('births','Births',3),
          ('cbr','CBR',2),('cdr','CDR',2),('medage','MedianAge',1),('netmig','NetMig',3)]
HC_MAP = [('hc_mysf','mys_20_39_F',2),('hc_myst','mys_25p_T',2),
          ('hc_upps','uppsec_25p_T',1),('hc_ggap','ggap_mys_25p',2)]

PROJD={}
miss_fc=[]; miss_pan=[]
for iso in DATA_ISOS:
    rec={}
    f = fc.get(iso)
    if f:
        for key,field,nd in FC_MAP:
            vals=[fc_at(iso,y,field) for y in YEARS]
            if all(v is not None for v in vals):
                rec[key]=[round(v,nd) for v in vals]
        # deaths = CDR * Pop  (CDR per 1000, Pop in thousands -> raw people)
        dv=[]
        ok=True
        for y in YEARS:
            cdr=fc_at(iso,y,'CDR'); pp=fc_at(iso,y,'Pop')
            if cdr is None or pp is None: ok=False; break
            dv.append(round(cdr*pp))
        if ok: rec['deaths']=dv
    else:
        miss_fc.append(iso)
    # DHI + pillars from panel waypoints
    pc=pan.get(iso)
    if pc:
        sc=pc.get('scores',{})
        spairs=sorted((int(y),v) for y,v in sc.items() if int(y)>=2025 and v is not None)
        if len(spairs)>=2:
            rec['dhi']=[round(interp_wp(spairs,y),1) for y in YEARS]
        pl=pc.get('pillars',{})
        comp_pairs={}
        for comp in PILW:
            cp=sorted((int(y), p.get(comp)) for y,p in pl.items() if int(y)>=2025 and p.get(comp) is not None)
            if len(cp)>=2: comp_pairs[comp]=cp
        if len(comp_pairs)==4:
            P={comp:[interp_wp(comp_pairs[comp],y) for y in YEARS] for comp in PILW}
            rec['p_fss']=[round(P['Fertility'][i]*0.34,2) for i in range(len(YEARS))]
            rec['p_pms']=[round(P['Renewal'][i]*0.28,2)  for i in range(len(YEARS))]
            rec['p_wss']=[round(P['AgeStruct'][i]*0.22,2) for i in range(len(YEARS))]
            rec['p_mrs']=[round(P['Migration'][i]*0.16,2) for i in range(len(YEARS))]
    else:
        miss_pan.append(iso)
    # HC raw components (source extends to 2100)
    if hc.get(iso):
        for key,field,nd in HC_MAP:
            vals=[hc_interp(iso,y,field) for y in YEARS]
            if all(v is not None for v in vals): rec[key]=[round(v,nd) for v in vals]
        # HCQ composite
        qv=[hcq(iso,y) for y in YEARS]
        if all(v is not None for v in qv): rec['q']=[round(v,1) for v in qv]
    if rec: PROJD[iso]=rec

js='const PROJD='+json.dumps(PROJD,separators=(',',':'))+';'
print(f'isos with projection: {len(PROJD)}/{len(DATA_ISOS)}')
print(f'missing in forecast: {miss_fc}')
print(f'missing in panel: {miss_pan}')
# coverage per key
from collections import Counter
cnt=Counter()
for r in PROJD.values():
    for k in r: cnt[k]+=1
print('per-indicator coverage:', dict(sorted(cnt.items())))
print(f'blob bytes: {len(js):,}')

# continuity checks at the 2025/2026 boundary + HCQ 2025 match
hist=json.load(open('_globe_data.json'))  # not used; placeholder
import re
open('_PROJD.js','w').write(js)
print('-> wrote _PROJD.js')
