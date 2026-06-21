#!/usr/bin/env python3
"""Build public/cliffs/index.html — the 'Demographic Cliffs' section, reformed
into seven colour-themed, interactive cards. Each cliff has its own colour,
narrative and dataset; the chart is an explorable cohort trajectory (pick any
country, hover for year/value, peak marked, decline shaded).
Data: public/cliffs_data.json (from _build_cliffs.py)."""
import json
C=json.load(open('public/cliffs_data.json'))

# cliff meta: key, title, eyebrow, narrative, colour, unit, default flagship, who-budgets, stat-kind
META=[
 ('higher_ed','The enrollment cliff','18-YEAR-OLDS · 2010–2050',
  'The freshman class that was never born. An 18-year-old in 2043 was already born in 2025 — so the applicant pool is fixed long before it arrives.',
  '#4f5bd5','students','USA','Universities · ed-tech · student housing','decline'),
 ('kindergarten','The empty classroom','5-YEAR-OLDS · 2010–2040',
  'Tomorrow’s first grade is in this year’s maternity wards. Where births fell, classrooms empty five years later — and districts start closing schools.',
  '#2e9e5b','children','KOR','School districts · K-12 · children’s brands','decline'),
 ('baby','The vanishing cradle','ANNUAL BIRTHS',
  'A market shrinking in real time. Every birth is a future customer for formula, prams and paediatrics — and the cradle is emptying fastest where it once was fullest.',
  '#d6336c','births','CHN','Formula · diapers · maternity care','decline'),
 ('manpower','The thin ranks','MILITARY-AGE 18–25 · 2010–2050',
  'Who will hold the line? The pool of young adults a country can recruit, staff and tax is set two decades in advance — and it is narrowing.',
  '#5a6b82','young adults','KOR','Defence recruitment · entry-level labour','decline'),
 ('first_home','The first-home drought','HOUSEHOLD-FORMATION 28–35 · 2010–2055',
  'Fewer hands reaching for the keys. The cohort that forms households and buys first homes is already born — and in much of the world it has peaked.',
  '#d98a2b','first-time buyers','KOR','Homebuilders · mortgage lenders · REITs','decline'),
 ('peak_workers','Peak labour','WORKING-AGE 15–64 · 2000–2055',
  'The year the engine stops growing. A shrinking working-age population caps output, strains pensions and rewrites the investment case for a country.',
  '#1d9e8f','workers','CHN','Manufacturers · investors · site selection','decline'),
 ('silver','The silver tsunami','POPULATION 80+ · 2000–2055',
  'The wave already on its way. Everyone who will be 80 in 2050 is alive today — and the most care-intensive cohort is multiplying.',
  '#7a4fd0','people 80+','CHN','Senior living · home health · pharma','growth'),
]

NAMES={i:C[i]['name'] for i in C}
def short(nm):
    return (nm.replace('China, Taiwan Province of China','Taiwan').replace('Republic of Korea','South Korea')
              .replace('Russian Federation','Russia').replace('United States of America','United States')
              .replace('Iran (Islamic Republic of)','Iran').replace('Viet Nam','Vietnam')
              .replace('Bolivia (Plurinational State of)','Bolivia').replace('Venezuela (Bolivarian Republic of)','Venezuela'))

# compact payload: per cliff -> {y:[years], cty:{iso:[vals]}, stat:{iso:[peakYr,pctOrMult]}}
PAY={}; CLIST={}
for key,title,eye,narr,col,unit,flag,who,kind in META:
    # years axis from a country that has the series (flagship if present)
    base=C.get(flag,{}).get('cliffs',{}).get(key) or next((C[i]['cliffs'][key] for i in C if C[i]['cliffs'].get(key)),None)
    yrs=sorted(int(y) for y in base['series'])
    cty={}; stat={}
    for i,rec in C.items():
        m=rec['cliffs'].get(key)
        if not m or 'series' not in m: continue
        vals=[m['series'].get(str(y)) for y in yrs]
        if any(v is None for v in vals): continue
        cty[i]=[round(v) for v in vals]
        if kind=='growth':
            stat[i]=[m.get('v2025'),m.get('mult')]
        else:
            stat[i]=[(m.get('peak') or [None])[0], m.get('pct')]
    PAY[key]={'y':yrs,'cty':cty,'stat':stat}
    # selector list: countries with data, pop>=1M, sorted by name
    CLIST[key]=sorted([i for i in cty if (C[i]['pop'] or 0)>=1], key=lambda i:short(NAMES[i]))

cards=''
for key,title,eye,narr,col,unit,flag,who,kind in META:
    opts=''.join(f'<option value="{i}"{" selected" if i==flag else ""}>{short(NAMES[i])}</option>' for i in CLIST[key])
    cards+=('<div class="card" id="C___K__" style="--ac:__COL__"><div class="ac"></div>'
            '<div class="eye">__EYE__</div><div class="c-h">__T__</div>'
            '<p class="narr">__N__</p>'
            '<div class="ctl"><select class="csel" id="sel___K__">__OPTS__</select>'
            '<span class="stat" id="stat___K__"></span></div>'
            '<svg class="chart" id="svg___K__" viewBox="0 0 1000 360" xmlns="http://www.w3.org/2000/svg"></svg>'
            '<div class="c-foot"><div class="src">Who budgets for this &middot; <b>__WHO__</b><br>'
            'Cohort already born; UN&nbsp;WPP for projected birth-years &amp; age structure. demoriaresearch.com</div>'
            '<div class="btns"><button class="btn" onclick="dl(\'__K__\')">Download PNG</button></div></div></div>'
           ).replace('__K__',key).replace('__COL__',col).replace('__EYE__',eye).replace('__T__',title
           ).replace('__N__',narr).replace('__OPTS__',opts).replace('__WHO__',who)

TPL=r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Demographic Cliffs — Demoria Research</title>
<meta name="description" content="Seven demographic cliffs already locked in: future students, children, workers, homebuyers and retirees by country — explore any nation's trajectory.">
<meta property="og:title" content="Demographic Cliffs — the cohorts already locked in">
<meta property="og:image" content="https://demoriaresearch.com/charts/fertility-1965-2025.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://demoriaresearch.com/cliffs/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#0c1a33;--cream:#f4ecd3;--cream2:#fcf4dd;--gold2:#e8b84b;--ink:#0c1a33}
*{box-sizing:border-box;margin:0;padding:0}
body{background:linear-gradient(180deg,#0a1730,#091428);color:#fff;font-family:'Manrope',system-ui,sans-serif;min-height:100vh}
.topbar{background:var(--cream);height:50px;display:flex;align-items:center;padding:0 22px;gap:13px;position:sticky;top:0;z-index:50;border-bottom:2px solid rgba(12,26,51,.12)}
.tb-back{font-size:.66rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--navy);text-decoration:none;opacity:.72}
.tb-title{font-size:.95rem;font-weight:700;color:var(--navy)}
.wrap{max-width:1040px;margin:0 auto;padding:34px 20px 80px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold2);text-align:center;margin-bottom:10px}
h1.hd{text-align:center;font-size:clamp(1.8rem,4.5vw,2.7rem);font-weight:800;line-height:1.08;margin-bottom:12px}
h1.hd em{color:var(--gold2);font-style:normal}
.lead{text-align:center;color:rgba(255,255,255,.72);font-size:clamp(.98rem,1.3vw,1.12rem);max-width:64ch;margin:0 auto 30px;line-height:1.55}
.card{position:relative;background:var(--cream2);border-radius:16px;padding:26px clamp(16px,2.5vw,30px) 18px;box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(12,26,51,.08);margin-bottom:26px;overflow:hidden;scroll-margin-top:64px}
.card .ac{position:absolute;top:0;left:0;right:0;height:6px;background:var(--ac)}
.eye{font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ac);font-weight:700;margin-bottom:4px}
.c-h{font-size:clamp(1.4rem,3vw,2rem);font-weight:800;color:var(--ink);letter-spacing:-.01em;margin-bottom:6px}
.narr{color:rgba(12,26,51,.74);font-size:clamp(.95rem,1.3vw,1.05rem);line-height:1.5;max-width:62ch;margin-bottom:14px}
.ctl{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:6px}
.csel{font-family:'Manrope',sans-serif;font-size:.95rem;font-weight:700;color:var(--ink);background:#fff;border:1.5px solid var(--ac);border-radius:9px;padding:8px 12px;cursor:pointer;max-width:260px}
.stat{font-family:'JetBrains Mono',monospace;font-size:.82rem;color:var(--ink);background:color-mix(in srgb,var(--ac) 14%,transparent);border:1px solid color-mix(in srgb,var(--ac) 35%,transparent);border-radius:8px;padding:6px 11px;font-weight:600}
svg.chart{display:block;width:100%;height:auto}
.c-foot{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;margin-top:8px;padding-top:12px;border-top:1px solid rgba(12,26,51,.12)}
.src{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:rgba(12,26,51,.55);line-height:1.5}.src b{color:var(--ink)}
.btn{font-family:'JetBrains Mono',monospace;font-size:.64rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:9px 14px;border-radius:7px;border:0;background:var(--ac);color:#fff;cursor:pointer;opacity:.92}.btn:hover{opacity:1}
#tip{position:fixed;z-index:100;pointer-events:none;display:none;background:var(--navy);color:var(--cream);font-family:'Manrope',sans-serif;font-size:.8rem;padding:7px 10px;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5);border:1px solid rgba(232,184,75,.4)}
#tip b{color:#fff}#tip .v{font-family:'JetBrains Mono',monospace;font-size:.74rem;margin-top:2px}
</style></head><body>
<div class="topbar"><a class="tb-back" href="/dhi/">&#8249;&nbsp;Back to DHI</a><span style="color:rgba(12,26,51,.3)">|</span><span class="tb-title">Demographic Cliffs</span></div>
<div class="wrap">
<div class="eyebrow">Demoria Research &middot; Demographic Cliffs</div>
<h1 class="hd">The cohorts <em>already locked in</em></h1>
<p class="lead">Seven futures you can already see coming. Each chart is a cohort whose size is largely fixed by the people alive today — pick any country and watch its curve. Where the line falls off a cliff, the institutions built around that cohort are about to feel it.</p>
__CARDS__
<div class="note" style="text-align:center;color:rgba(255,255,255,.45);font-family:'JetBrains Mono',monospace;font-size:.68rem;letter-spacing:.06em;margin-top:10px">Young cohorts derived from national births (near-certain while already born); structural cohorts from UN&nbsp;WPP age structure.</div>
</div>
<div id="tip"></div>
<script>
const PAY=__PAY__, META=__META__, NAMES=__NAMES__;
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function tx(x,y,s,cls,ex){const t=el('text',Object.assign({x,y,class:cls},ex||{}));t.textContent=s;return t;}
function fmt(v){v=Math.abs(v);if(v>=1e6)return (v/1e6).toFixed(v>=1e7?0:1)+'M';if(v>=1e3)return (v/1e3).toFixed(0)+'k';return ''+Math.round(v);}
const tip=document.getElementById('tip');
function draw(key,iso){
  const m=META.find(x=>x[0]===key), col=m[4], kind=m[8], unit=m[5];
  const P=PAY[key], yrs=P.y, vals=P.cty[iso]; if(!vals)return;
  const svg=document.getElementById('svg_'+key); svg.innerHTML='';
  const W=1000,H=360,L=58,R=22,T=22,B=44, x0=L,x1=W-R,y0=H-B,y1=T;
  const mx=Math.max.apply(null,vals), mn=Math.min.apply(null,vals);
  const lo=Math.max(0,mn-(mx-mn)*0.12), hi=mx+(mx-mn)*0.12||mx*1.1;
  const X=i=>x0+(x1-x0)*(i/(yrs.length-1));
  const Y=v=>y0+(y1-y0)*((v-lo)/((hi-lo)||1));
  const st=el('style',{});st.textContent=".ax{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;fill:rgba(12,26,51,.5)}";svg.appendChild(st);
  // gridlines (4)
  for(let g=0;g<=3;g++){const v=lo+(hi-lo)*g/3,y=Y(v);svg.appendChild(el('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:'rgba(12,26,51,.08)','stroke-width':1}));svg.appendChild(tx(x0-8,y+4,fmt(v),'ax',{'text-anchor':'end'}));}
  // x labels (decades)
  yrs.forEach((yy,i)=>{if(yy%10===0){svg.appendChild(tx(X(i),y0+22,yy,'ax',{'text-anchor':'middle'}));}});
  // peak index
  let pk=0;for(let i=1;i<vals.length;i++)if(vals[i]>vals[pk])pk=i;
  // area (shade decline after peak deeper)
  let d='M '+X(0).toFixed(1)+' '+Y(vals[0]).toFixed(1);
  vals.forEach((v,i)=>{if(i)d+=' L '+X(i).toFixed(1)+' '+Y(v).toFixed(1);});
  const area=d+' L '+X(yrs.length-1).toFixed(1)+' '+y0+' L '+X(0).toFixed(1)+' '+y0+' Z';
  svg.appendChild(el('path',{d:area,fill:col,'fill-opacity':0.12}));
  // decline region highlight (peak -> end) for decline cliffs
  if(kind==='decline'&&pk<vals.length-1){
    let dd='M '+X(pk).toFixed(1)+' '+Y(vals[pk]).toFixed(1);
    for(let i=pk;i<vals.length;i++)dd+=' L '+X(i).toFixed(1)+' '+Y(vals[i]).toFixed(1);
    dd+=' L '+X(vals.length-1).toFixed(1)+' '+y0+' L '+X(pk).toFixed(1)+' '+y0+' Z';
    svg.appendChild(el('path',{d:dd,fill:col,'fill-opacity':0.16}));
  }
  svg.appendChild(el('path',{d,fill:'none',stroke:col,'stroke-width':3,'stroke-linejoin':'round'}));
  // marker: peak for declines, the 2025 'today' anchor for growth — label colour inline (CSS classes are global)
  const mk=(kind==='growth')?Math.max(0,yrs.indexOf(2025)):pk;
  svg.appendChild(el('circle',{cx:X(mk),cy:Y(vals[mk]),r:4.5,fill:col}));
  svg.appendChild(tx(X(mk),Y(vals[mk])-10,(kind==='growth'?('today '+yrs[mk]):('peak '+yrs[pk])),'',{'text-anchor':mk>yrs.length*0.7?'end':'middle','style':'font:700 12px Manrope,system-ui;fill:'+col}));
  // hover layer
  vals.forEach((v,i)=>{
    const r=el('rect',{x:X(i)-((x1-x0)/(yrs.length-1))/2,y:y1,width:(x1-x0)/(yrs.length-1),height:y0-y1,fill:'transparent'});
    r.addEventListener('mousemove',e=>{tip.style.display='block';tip.innerHTML='<b>'+short(NAMES[iso])+' · '+yrs[i]+'</b><div class="v">'+fmt(v)+' '+unit+'</div>';let lx=e.clientX+14;if(lx+170>innerWidth)lx=e.clientX-14-tip.offsetWidth;tip.style.left=lx+'px';tip.style.top=(e.clientY+14)+'px';});
    r.addEventListener('mouseleave',()=>tip.style.display='none');
    svg.appendChild(r);
  });
  // stat badge
  const s=P.stat[iso]; const sb=document.getElementById('stat_'+key);
  if(kind==='growth'){sb.textContent='×'+(s[1]||0).toFixed(1)+' by 2050';}
  else{const p=s[1];sb.textContent=(p>0?'+':'')+Math.round(p)+'% '+(yrs[pk]<2026?'since peak':'to '+yrs[yrs.length-1]);}
}
function short(nm){return nm.replace('China, Taiwan Province of China','Taiwan').replace('Republic of Korea','South Korea').replace('Russian Federation','Russia').replace('United States of America','United States').replace('Iran (Islamic Republic of)','Iran').replace('Viet Nam','Vietnam').replace('Bolivia (Plurinational State of)','Bolivia');}
META.forEach(m=>{const sel=document.getElementById('sel_'+m[0]);draw(m[0],sel.value);sel.addEventListener('change',()=>draw(m[0],sel.value));});
function dl(key){
  const svg=document.getElementById('svg_'+key),m=META.find(x=>x[0]===key),W=1000,H=360;
  const c=svg.cloneNode(true);c.setAttribute('width',W);c.setAttribute('height',H+34);c.setAttribute('viewBox','0 0 1000 '+(H+34));
  [].slice.call(c.querySelectorAll('rect[fill="transparent"]')).forEach(r=>r.remove());
  const g=el('g',{transform:'translate(0,34)'});while(c.childNodes.length>1){g.appendChild(c.childNodes[1]);}
  c.appendChild(g);
  const bg=el('rect',{x:0,y:0,width:W,height:H+34,fill:'#fcf4dd'});c.insertBefore(bg,c.firstChild);
  const nm=document.getElementById('sel_'+key); const lbl=nm.options[nm.selectedIndex].text;
  c.insertBefore(tx(58,22,m[1]+' — '+lbl+'  ·  demoriaresearch.com','ax',{'font-size':'13','font-weight':'700',fill:m[4]}),c.firstChild.nextSibling);
  const data=new XMLSerializer().serializeToString(c),img=new Image();
  img.onload=()=>{const s=2,cv=document.createElement('canvas');cv.width=W*s;cv.height=(H+34)*s;const x=cv.getContext('2d');x.scale(s,s);x.drawImage(img,0,0);cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='demoria-'+key+'-'+nm.value+'.png';a.click();});};
  img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(data)));
}
</script></body></html>'''
import sys
html=(TPL.replace('__CARDS__',cards)
        .replace('__PAY__',json.dumps(PAY,separators=(',',':')))
        .replace('__META__',json.dumps([list(m) for m in META],separators=(',',':')))
        .replace('__NAMES__',json.dumps(NAMES,ensure_ascii=False,separators=(',',':'))))
open('public/cliffs/index.html','w',encoding='utf-8').write(html)
print(f"wrote public/cliffs/index.html ({len(html):,} bytes), {len(META)} themed interactive cliffs")
