"""SANDBOX: build dhi_globe_hcq.html — a copy of the live globe with an
experimental "Quality" colour lens added to the World map's "Colour map by"
control. It recolours the map (and legend, rail, panel headline) by the 5th
pillar HCQ (Human Capital & Fertility Quality) instead of the DHI composite,
so the two lenses can be flipped side by side. Nothing touches the live site.

HCQ is precomputed per ISO per year 1965-2025 and embedded as HCQ_DATA.
For projection years (>2025) the map holds the 2025 HCQ value (HC/fertility
quality isn't projected here).
"""
import json, shutil

SRC='dhi_globe.html'; DST='dhi_globe_hcq.html'

# ---------------- compute HCQ per iso per year (same defn as the timeline) -----
exp = json.load(open('_data_export.json'))
hc  = json.load(open('_human_capital.json'))['countries']
clip= lambda v: max(0.0,min(100.0,v))
def s_mother(x): return None if x is None else clip((x-2)/12*100)
def s_attain(x): return None if x is None else clip(x)
def s_equity(g): return None if g is None else clip(100-25*max(0.0,g))
def s_surv(sr):  return None if sr is None else clip((sr-0.75)/0.24*100)
PW={'mother':0.25,'attain':0.25,'equity':0.10,'surv':0.40}
def hc_interp(iso,yr,key):
    s=hc.get(iso,{})
    if not s: return None
    if str(yr) in s and key in s[str(yr)]: return s[str(yr)][key]
    lo=(yr//5)*5; hiy=lo+5
    a=s.get(str(lo),{}).get(key); b=s.get(str(hiy),{}).get(key)
    if a is None and b is None:
        av=sorted(int(y) for y in s if key in s[y])
        return s[str(min(av,key=lambda y:abs(y-yr)))][key] if av else None
    if a is None: return b
    if b is None: return a
    return a+(b-a)*((yr-lo)/5.0)
def tn(iso,yr):
    e=exp.get(iso)
    if not e or yr not in e['yrs']: return None,None
    i=e['yrs'].index(yr)
    return e['ind'].get('tfr',[None])[i], e['ind'].get('nrr',[None])[i]
def hcq(iso,yr):
    comp={'mother':s_mother(hc_interp(iso,yr,'mys_20_39_F')),
          'attain':s_attain(hc_interp(iso,yr,'uppsec_25p_T')),
          'equity':s_equity(hc_interp(iso,yr,'ggap_mys_25p'))}
    tfr,nrr=tn(iso,yr); sr=(nrr/(tfr*0.4886)) if (tfr and nrr and tfr>0) else None
    comp['surv']=s_surv(sr)
    av={k:v for k,v in comp.items() if v is not None}
    if not av: return None
    w=sum(PW[k] for k in av)
    return round(sum(PW[k]*v for k,v in av.items())/w,1)

HCQ_DATA={}
for iso in exp:
    yrs={}
    for yr in range(1965,2026):
        v=hcq(iso,yr)
        if v is not None: yrs[str(yr)]=v
    if yrs: HCQ_DATA[iso]=yrs
blob=json.dumps(HCQ_DATA,separators=(',',':'))
print('HCQ_DATA: %d countries x %d years'%(len(HCQ_DATA), 61))

# ---- per-country 2025 component breakdown + percentile, for the profile page ----
def comp2025(iso):
    yr=2025
    mysF=hc_interp(iso,yr,'mys_20_39_F'); upp=hc_interp(iso,yr,'uppsec_25p_T'); gg=hc_interp(iso,yr,'ggap_mys_25p')
    tfr,nrr=tn(iso,yr); sr=(nrr/(tfr*0.4886)) if (tfr and nrr and tfr>0) else None
    comps=[s_mother(mysF), s_attain(upp), s_equity(gg), s_surv(sr)]
    if any(c is None for c in comps): return None
    raw=[round(mysF,1), round(upp,1), round(gg,2), round(sr,3)]
    return {'comps':[round(c,1) for c in comps], 'raw':raw}

prof={}
for iso in HCQ_DATA:
    cb=comp2025(iso)
    s=HCQ_DATA[iso].get('2025')
    if cb is None or s is None: continue
    prof[iso]={'s':s, **cb}
# percentile + rank by 2025 composite
ranked=sorted(prof.items(), key=lambda kv:-kv[1]['s'])
N=len(ranked)
for r,(iso,d) in enumerate(ranked, start=1):
    d['rank']=r
    d['pct']=round(100*(N-r)/(N-1)) if N>1 else 100
profblob=json.dumps(prof,separators=(',',':'))
print('HCQ_PROFILE: %d countries (2025 components + percentile)'%N)

# ---------------- patch the globe ----------------
shutil.copy2(SRC,DST); h=open(DST).read()

# 1) embed HCQ_DATA + HCQ_PROFILE + helpers
HCQ_SECTION_JS = (
 "function hcqProfileSection(c){"
 " var p=(typeof HCQ_PROFILE!=='undefined')?HCQ_PROFILE[c.iso]:null; if(!p) return '';"
 " var ord=function(n){var s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0]);};"
 " var bar=function(lab,raw,sc){return '<div class=pbar2><div class=pl><span>'+lab+' <span class=wt>'+raw+'</span></span><b>'+sc.toFixed(0)+'<span class=\"pb-of\">/100</span></b></div><div class=pt><div class=pf2 style=\"width:'+Math.max(2,sc)+'%;background:'+ramp(sc)+'\"></div></div></div>';};"
 " var cm=p.comps, rw=p.raw;"
 " return '<section class=\"ft-section ft-hcq\">'"
 " +'<header class=\"ft-section-head\"><h2>Quality lens</h2><span class=\"ft-section-sub\">Experimental 5th pillar \\u00b7 not in the DHI score</span></header>'"
 " +'<div class=\"hcq-block\"><div class=\"hcq-top\"><div class=\"hcq-score\" style=\"color:'+ramp(p.s)+'\">'+p.s.toFixed(1)+'</div>'"
 " +'<div class=\"hcq-meta\"><div class=\"hcq-ttl\">Human Capital &amp; Fertility Quality</div>'"
 " +'<div class=\"hcq-pct\"><b>'+ord(p.pct)+' percentile</b> \\u00b7 rank '+p.rank+' of 236</div></div></div>'"
 " +'<div class=\"hcq-halves\"><div class=\"hcq-half\"><div class=\"hcq-half-h\"><span>Human Capital</span><span>60%</span></div>'"
 " + bar('Mother\\u2019s schooling', rw[0].toFixed(1)+' yrs', cm[0])"
 " + bar('Adult attainment', rw[1].toFixed(0)+'% \\u2265 upper-sec', cm[1])"
 " + bar('Gender equity', (rw[2]>=0?'+':'')+rw[2].toFixed(1)+' yr gap', cm[2])"
 " +'</div><div class=\"hcq-half\"><div class=\"hcq-half-h\"><span>Fertility Quality</span><span>40%</span></div>'"
 " + bar('Birth survival', (rw[3]*100).toFixed(0)+'% to reproduction', cm[3])"
 " +'</div></div></div></section>';"
 "}")
h=h.replace('let scoreMode=\'dhi\';',
            'let scoreMode=\'dhi\';\nconst HCQ_DATA='+blob+';\nconst HCQ_PROFILE='+profblob+';\n'
            'function hcqAt(c){ if(!c||!c.iso) return null; var yy=Math.min(2025,+(years[yi])); var hh=HCQ_DATA[c.iso]; if(!hh) return null; return (hh[String(yy)]!=null)?hh[String(yy)]:(hh[\'2025\']!=null?hh[\'2025\']:null); }\n'+HCQ_SECTION_JS, 1)

# 1b) inject the HCQ section into the FT rankings profile (renderFt), before
#     the "Key indicators" (ft-facts) section.
ft_anchor='\'<section class="ft-section ft-facts">\'+'
assert h.count(ft_anchor)==1, 'ft-facts anchor not unique: %d'%h.count(ft_anchor)
h=h.replace(ft_anchor, "hcqProfileSection(c)+'<section class=\"ft-section ft-facts\">'+", 1)

# 1b-ii) the new Quality-lens section replaces the old "Beyond the score"
#        context block on the profile — remove it (it duplicated HC + FQ).
ctx_block=("'<section class=\"ft-section ft-context\">'+\n"
 "              '<header class=\"ft-section-head\"><h2>Beyond the score</h2><span class=\"ft-section-sub\">Indicators not in the DHI composite</span></header>'+\n"
 "              '<div class=\"pf-ctx\" id=\"pf-ctx\"></div>'+\n"
 "            '</section>'+")
assert h.count(ctx_block)==1, 'ft-context block not found uniquely: %d'%h.count(ctx_block)
h=h.replace(ctx_block, '', 1)

# 1c) CSS for the profile HCQ block (cream theme)
PROF_CSS=('\n/* HCQ profile block */\n'
 '.pf-paper .hcq-h{margin-top:30px}\n'
 '.pf-paper .hcq-block{background:#fcf4dd;border:1px solid rgba(181,132,32,.30);border-radius:14px;padding:18px 20px;margin-top:4px}\n'
 '.pf-paper .hcq-top{display:flex;align-items:center;gap:16px;margin-bottom:16px}\n'
 '.pf-paper .hcq-score{font-family:\'JetBrains Mono\',monospace;font-size:2.4rem;font-weight:700;line-height:1}\n'
 '.pf-paper .hcq-ttl{font-weight:700;color:#0c1a33;font-size:.96rem}\n'
 '.pf-paper .hcq-pct{font-size:.82rem;color:rgba(12,26,51,.66);margin-top:2px}\n'
 '.pf-paper .hcq-pct b{color:#b58420}\n'
 '.pf-paper .hcq-halves{display:grid;grid-template-columns:1.5fr 1fr;gap:26px}\n'
 '.pf-paper .hcq-half-h{font-family:\'JetBrains Mono\',monospace;font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:#5d4524;margin:0 0 8px;display:flex;justify-content:space-between;border-bottom:1px solid rgba(12,26,51,.12);padding-bottom:5px}\n'
 '.pf-paper .hcq-half-h span:last-child{color:#b58420}\n'
 '@media(max-width:680px){.pf-paper .hcq-halves{grid-template-columns:1fr;gap:16px}}\n')
h=h.replace('</style></head>', PROF_CSS+'</style></head>', 1)

# 2) pillarLabel — add hcq
h=h.replace("({dhi:'DHI score',F:'Fertility Strength (FSS)',R:'Population Momentum (PMS)',A:'Workforce Sustainability (WSS)',M:'Migration Reliance (MRS)'})[scoreMode]",
            "({dhi:'DHI score',hcq:'Human Capital & Fertility Quality',F:'Fertility Strength (FSS)',R:'Population Momentum (PMS)',A:'Workforce Sustainability (WSS)',M:'Migration Reliance (MRS)'})[scoreMode]", 1)

# 3) curScore — handle hcq at the top (drives map via scoreAt, plus rail/panel)
h=h.replace('function curScore(c){\n  const y=String(years[yi]);\n  if(scoreMode!==\'dhi\'){',
            'function curScore(c){\n  const y=String(years[yi]);\n  if(scoreMode===\'hcq\'){ return hcqAt(c); }\n  if(scoreMode!==\'dhi\'){', 1)

# 4) add the "Quality" button to the Colour-map-by control (its own experimental row)
old_seg=('<div class="ss-pills"><button data-m="F" title="Fertility Strength (FSS)">Fert.</button>'
 '<button data-m="R" title="Population Momentum (PMS)">Pop.</button>'
 '<button data-m="A" title="Workforce Sustainability (WSS)">Work.</button>'
 '<button data-m="M" title="Migration Reliance (MRS)">Mig.</button></div></div>')
new_seg=old_seg[:-6]+('<div class="ss-or ss-or-exp">experimental lens</div>'
 '<button data-m="hcq" class="ss-hcq" title="Human Capital &amp; Fertility Quality — the experimental 5th pillar (quality of renewal, not quantity)"><span class="ss-hcq-l">Quality</span><span class="ss-hcq-s">human capital &amp; fertility quality</span></button>'
 '</div>')
assert old_seg in h, 'scoreSeg anchor not found'
h=h.replace(old_seg,new_seg,1)

# 5) CSS for the experimental button + a banner note when active
CSS=('\n/* HCQ experimental lens */\n'
 '.scoreseg .ss-or-exp{margin-top:10px;color:#b58420}\n'
 '#view-world .scoreseg .ss-hcq{display:block;width:100%;margin-top:7px;padding:9px 12px;border:1px dashed rgba(181,132,32,.6);border-radius:8px;background:rgba(181,132,32,.08);color:#0c1a33;cursor:pointer;text-align:left;font-family:Manrope,sans-serif;transition:background .12s,border-color .12s}\n'
 '#view-world .scoreseg .ss-hcq:hover{background:rgba(181,132,32,.16);border-color:#b58420}\n'
 '#view-world .scoreseg .ss-hcq.on{background:#b58420;border-style:solid;border-color:#b58420;color:#fff}\n'
 '.ss-hcq .ss-hcq-l{display:block;font-weight:700;font-size:.86rem}\n'
 '.ss-hcq .ss-hcq-s{display:block;font-size:.64rem;opacity:.8;margin-top:1px}\n'
 '#view-world .stage-subtitle.hcq .stage-st-l::after{content:" \\00b7 QUALITY LENS";color:#b58420;font-weight:700}\n')
h=h.replace('</style></head>', CSS+'</style></head>', 1)

# 6) when HCQ mode active, swap the stage subtitle text so it is obvious the
#    map is no longer showing the DHI. Hook the existing scoreSeg handler.
HOOK=('\n<script>(function(){\n'
 ' function syncHcqUi(){\n'
 '  try{\n'
 '   var on=(typeof scoreMode!==\'undefined\'&&scoreMode===\'hcq\');\n'
 '   var st=document.querySelector(\'#view-world .stage-subtitle\');\n'
 '   if(st){ var l=st.querySelector(\'.stage-st-l\'), r=st.querySelector(\'.stage-st-r\');\n'
 '     if(l) l.textContent= on?\'Human Capital & Fertility Quality\':\'Demographic Health Index\';\n'
 '     if(r) r.textContent= on?\'how well-educated & well-invested each new generation is \\u00b7 experimental 5th pillar \\u00b7 0\\u2013100\':\'populations most able to renew themselves through their own births \\u00b7 0\\u2013100\'; }\n'
 '  }catch(e){}\n'
 ' }\n'
 ' var seg=document.getElementById(\'scoreSeg\');\n'
 ' if(seg){ seg.addEventListener(\'click\', function(){ setTimeout(syncHcqUi,0); }); }\n'
 ' setTimeout(syncHcqUi, 400);\n'
 '})();</script>\n')
h=h.replace('</body>', HOOK+'</body>', 1)

# title tweak
h=h.replace('<title>DHI v2.0 &mdash; The World</title>','<title>DHI v2.0 (HCQ lens sandbox) &mdash; The World</title>',1)
h=h.replace('<title>DHI v2.0 — The World</title>','<title>DHI v2.0 (HCQ lens sandbox) — The World</title>',1)

open(DST,'w').write(h)
print('built',DST,'(%.2f MB)'%(len(h)/1024/1024))
