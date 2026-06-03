"""DHI v2.0 Stage C — projections. Computes the engine ANNUALLY 2026-2100,
then presents the waypoints 2035/2050/2075/2100 as 9-year centred means so
cohort-wave noise in the 5-yr-change indicators doesn't zigzag the headline."""
import json, math, csv
from dhi_scoring import (clip, score_Years_Sub_21,
    score_OADR, score_WRR, score_LFPR, score_Immigrant_Stock)

fc=json.load(open('_wpp_forecast_cache.json'))
cache=json.load(open('_indicator_sheets_cache.json'))
wpp=json.load(open('_wpp_indicators_1960_2025.json'))
ap=json.load(open('public/age_pyramid.json'))
regimes=json.load(open('migration_regimes.json'))
panel=json.load(open('dhi_data_v2_unified.json'))
PROJ=[2035,2050,2075,2100]
overrides={}
for r in csv.DictReader(open('overrides/tfr.csv')):
    overrides[(r['iso3'],r['year'])]=float(r['value'])

def s_F1(x):
    if x is None: return None
    if x<1.0:  return clip(100*math.exp(-6*(1.0-x)))
    if x<=1.7: return 100.0
    return max(50.0,100-18.5*(x-1.7))
def s_F2(x):
    if x is None: return None
    return clip(45+(x/0.12)*55) if x>=0 else clip(max(0,45+(x/0.25)*45))
def s_R1(x):
    if x is None: return None
    if x<=-10: return 0.0
    if x<0:    return clip((x+10)/10*28)
    if x<=12:  return clip(28+(x/12)*72)
    return clip(max(88,100-(x-12)*0.8))
def s_R2(x):
    if x is None: return None
    return clip(38+(x/0.008)*62) if x>=0 else clip(max(0,38+(x/0.03)*38))
def s_R3(x):
    if x is None: return None
    return clip(32+(x/0.10)*68) if x>=0 else clip(max(0,32+(x/0.12)*32))
def s_R4(x):
    if x is None: return None
    return clip(35+(x/0.9)*65) if x>=0 else clip(max(0,35+(x/0.6)*35))
def s_R5(r): return None if r is None else clip(30+(r-0.7)/0.35*70)
def s_R6(p): return None if p is None else (100.0 if p<=0 else clip(100-(p/0.5)*100))
def s_A4(t): return None if t is None else (100.0 if t<=0 else clip(100-(t/0.18)*100))
def s_M1(b,m):
    if b is None or m is None or b<=0: return None
    rho=m/b
    if rho>=0:
        e=72+rho/0.12*24 if rho<=0.12 else max(10.0,min(96.0,96-(rho-0.12)/0.88*86))
    else:
        e=max(0.0,min(72.0,72-(-rho)/0.60*52))
    return e
W={'Fertility':0.34,'AgeStruct':0.22,'Renewal':0.28,'Migration':0.16}
# weighted within-pillar arithmetic mean; A4 dropped from Age & Workforce.
PIL={'Fertility':{'F1':0.48,'F2':0.29,'F3':0.23},
     'AgeStruct':{'A1':0.45,'A2':0.33,'A3':0.22},
     'Renewal':  {'R1':0.25,'R2':0.22,'R3':0.18,'R4':0.08,'R5':0.15,'R6':0.12},
     'Migration':{'M1':0.55,'M2':0.45}}
def norm(g): return max(0.0,min(100.0,12+(g-20)/80*88))  # g in [20,100] -> [12,100], no top clamp under realistic inputs

def tfr(iso,y):
    """effective TFR — NSO override (history) else WPP/forecast baseline."""
    o=overrides.get((iso,str(y)))
    if o is not None: return o
    if y<=2025: return wpp.get(iso,{}).get(str(y),{}).get('TFR')
    return fc.get(iso,{}).get(str(y),{}).get('TFR')
def totpop(iso,y):
    """total population (thousands) — WPP history, forecast cache for projections."""
    if y<=2025: return wpp.get(iso,{}).get(str(y),{}).get('TPopulation1July')
    return fc.get(iso,{}).get(str(y),{}).get('Pop')
def u20share(iso,yr):
    u=popu20(iso,yr); p=totpop(iso,yr)
    return (u/(p*1000)) if (u is not None and p) else None
def workage(iso,yr):
    v=fc.get(iso,{}).get(str(yr),{}).get('WorkAge_15_64')
    return v if v is not None else cache.get(iso,{}).get(str(yr),{}).get('WorkAge_15_64')
def medage(iso,yr):
    v=fc.get(iso,{}).get(str(yr),{}).get('MedianAge')
    return v if v is not None else cache.get(iso,{}).get(str(yr),{}).get('Median_Age')
def cohort(iso,yr):
    e=ap.get(iso)
    if not e: return None
    cand=min(e['y'],key=lambda y:abs(y-yr)); f=e['f'][e['y'].index(cand)]
    return sum(f[0:3])/sum(f[3:6]) if len(f)>=6 and sum(f[3:6])>0 else None
def popu20(iso,yr):
    """under-20 population; nearest available year within +-2 if exact missing"""
    c=cache.get(iso,{}); fv=fc.get(iso,{})
    for d in (0,-1,1,-2,2):
        v=fv.get(str(yr+d),{}).get('Pop_under20')
        if v is None: v=c.get(str(yr+d),{}).get('Pop_under20')
        if v is not None: return v
    return None

def score_year(iso,yr,reg,flat_lfpr,flat_immf):
    f=fc.get(iso,{}).get(str(yr))
    if not f: return None,None
    c=cache.get(iso,{}); cy=c.get(str(yr),{})
    t0,t5=tfr(iso,yr),tfr(iso,yr-5)
    dtfr=((t0-t5)/t5) if (t0 and t5) else None
    ncs=[]
    for t in range(yr-4,yr+1):
        ft=fc.get(iso,{}).get(str(t)) or {}
        if ft.get('CBR') is not None and ft.get('CDR') is not None:
            ncs.append(ft['CBR']-ft['CDR'])
    nc5=sum(ncs)/len(ncs) if len(ncs)>=3 else None
    ysub=sum(1 for t in range(1960,yr+1) if tfr(iso,t) is not None and tfr(iso,t)<2.1)
    s0,s5=u20share(iso,yr),u20share(iso,yr-5)
    du20=(s0-s5) if (s0 is not None and s5 is not None) else None
    statn=(f.get('CBR')/1000*f.get('e0')-1) if (f.get('CBR') is not None and f.get('e0')) else None
    e65a,e65b=fc.get(iso,{}).get(str(yr-10),{}).get('e65'),f.get('e65')
    e65t=((e65b-e65a)/10) if (e65a is not None and e65b is not None) else None
    ma,mb=medage(iso,yr-10),medage(iso,yr)
    mp=((mb-ma)/10) if (ma is not None and mb is not None) else None
    oadr=f.get('OADR') if f.get('OADR') is not None else cy.get('OADR')
    oadr=(oadr/100) if oadr is not None else None
    wa0,wa5=workage(iso,yr),workage(iso,yr-5)
    lfg=(wa0/wa5-1) if (wa0 and wa5) else None
    nmv=[(fc.get(iso,{}).get(str(t),{}).get('NetMig') if t>2025
          else cache.get(iso,{}).get(str(t),{}).get('NetMig')) for t in range(yr-4,yr+1)]
    nmv=[x for x in nmv if x is not None]
    nm5=sum(nmv)/len(nmv) if len(nmv)>=3 else None
    S={'F1':s_F1(f.get('NRR')),'F2':s_F2(dtfr),'F3':score_Years_Sub_21(ysub),
       'A1':score_OADR(oadr),
       'A2':score_WRR(f.get('WRR') if f.get('WRR') is not None else cy.get('WRR')),
       'A3':score_LFPR(flat_lfpr),
       'R1':s_R1(nc5),'R2':s_R2(du20),'R3':s_R3(lfg),
       'R4':s_R4(statn),'R5':s_R5(cohort(iso,yr)),'R6':s_R6(mp),
       'M1':s_M1(f.get('CBR'),nm5),'M2':score_Immigrant_Stock(flat_immf,reg)}
    pil={}
    for p,weights in PIL.items():
        pairs=[(S[x],weights[x]) for x in weights if S[x] is not None]
        if not pairs: return None,None
        pil[p]=sum(v*w for v,w in pairs)/sum(w for _,w in pairs)
    return sum(W[p]*pil[p] for p in W),pil   # weighted arithmetic mean across pillars

FCS={'low':json.load(open('_wpp_fc_low.json')),
     'med':json.load(open('_wpp_fc_med.json')),
     'high':json.load(open('_wpp_fc_high.json'))}
PILLARS=('Fertility','AgeStruct','Renewal','Migration')
done=0
for iso,C in panel['countries'].items():
    reg=regimes.get(iso)
    flat_lfpr=cache.get(iso,{}).get('2024',{}).get('LFPR')
    immstk24=cache.get(iso,{}).get('2024',{}).get('Mig_Stock')
    pop24=wpp.get(iso,{}).get('2024',{}).get('TPopulation1July')
    flat_immf=(immstk24/(pop24*1000)) if (immstk24 and pop24) else None
    pervar={}                       # vtag -> {wp:(score,pillars)}
    for vtag in ('low','med','high'):
        fc=FCS[vtag]
        annual={}
        for yr in range(2026,2101):
            sc,pil=score_year(iso,yr,reg,flat_lfpr,flat_immf)
            if sc is not None: annual[yr]=(sc,pil)
        wpres={}
        for wp in PROJ:
            win=[annual[y] for y in range(wp-4,wp+5) if y in annual]
            if not win: continue
            sc=sum(w[0] for w in win)/len(win)
            pil={p:sum(w[1][p] for w in win)/len(win) for p in PILLARS}
            wpres[wp]=(round(sc,2),{k:round(v,1) for k,v in pil.items()})
        pervar[vtag]=wpres
    C.setdefault('proj',{})
    C.setdefault('projPil',{})
    for wp in PROJ:
        med=pervar['med'].get(wp)
        if med:
            C['scores'][str(wp)]=med[0]
            C['pillars'][str(wp)]=med[1]
            C['prov'][str(wp)]='WPP'
            done+=1
        trio={v:pervar[v][wp][0] for v in ('low','med','high') if wp in pervar[v]}
        if trio: C['proj'][str(wp)]=trio
        triop={v:pervar[v][wp][1] for v in ('low','med','high') if wp in pervar[v]}
        if triop: C['projPil'][str(wp)]=triop

panel['years']=list(range(1965,2026))+PROJ
panel['meta']['projection']='Low/Medium/High variants; waypoints 2035/2050/2075/2100 = 9-yr centred means; headline score = Medium; LFPR & immigrant stock damp-extrapolated'
json.dump(panel,open('dhi_data_v2_unified.json','w'),separators=(',',':'))
print('Stage C (smoothed) — %d projection cells'%done)
for iso in ['GBR','CHN','KOR','NER','JPN','USA']:
    s=panel['countries'][iso]['scores']
    print('  %s: 2025=%s 2035=%s 2050=%s 2075=%s 2100=%s'%(iso,s.get('2025'),s.get('2035'),s.get('2050'),s.get('2075'),s.get('2100')))
