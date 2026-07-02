#!/usr/bin/env python3
"""Build public/bubbles/index.html — an animated bubble chart of annual births
per country. Observed 1965-2025 (annual), then UN WPP 2024 projections at
5-year steps 2030-2100, with a low/median/high variant toggle. Bubbles are
countries, sized by births, coloured by region and clustered by continent.
Hover (or tap) shows the country's flag, code and births for that year; click,
tap or the Track selector pins a country to follow it; in forecast years an
uncertainty fan shows the low-high spread around the pinned/hovered bubble.

  python3 _build_bubbles.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
exp = json.loads((ROOT / "_data_export.json").read_text())
bt = json.loads((ROOT / "public" / "births_data.json").read_text())
FCS = {"L": json.loads((ROOT / "_wpp_fc_low.json").read_text()),
       "M": json.loads((ROOT / "_wpp_fc_med.json").read_text()),
       "H": json.loads((ROOT / "_wpp_fc_high.json").read_text())}
reg = {c["iso"]: c["region"] for c in bt["countries"]}
iso2 = {c["iso"]: (c.get("iso2") or "") for c in bt["countries"]}

CONT = {'East Asia': 'Asia', 'Southeast Asia': 'Asia', 'South Asia': 'Asia', 'Central Asia': 'Asia',
        'Western & Northern Europe': 'Europe', 'Central & Eastern Europe': 'Europe',
        'North America': 'North America', 'Latin America & Caribbean': 'Latin America',
        'Caucasus & Türkiye': 'Middle East & N. Africa', 'Middle East & North Africa': 'Middle East & N. Africa',
        'Gulf (nationals)': 'Middle East & N. Africa', 'Sub-Saharan Africa': 'Africa', 'Oceania': 'Oceania'}
CONTS = ['Asia', 'Africa', 'Europe', 'Latin America', 'North America', 'Middle East & N. Africa', 'Oceania']
COLORS = ['#e8b84b', '#52c17a', '#5b9bd5', '#ec6f9e', '#a68bf0', '#37c2b0', '#f0954e']

OBS = list(range(1965, 2026))
FCY = list(range(2030, 2101, 5))

countries = []
for iso, c in exp.items():
    b = c.get("ind", {}).get("births"); yrs = c.get("yrs")
    if not b or not yrs:
        continue
    cont = CONT.get(reg.get(iso), 'Asia')
    obs = []; last = 0
    for y in OBS:
        v = b[yrs.index(y)] if y in yrs else last
        v = round(v) if v and v > 0 else 0
        last = v; obs.append(v)
    var = {}
    for key in ("L", "M", "H"):
        ser = []; lf = obs[-1]
        for y in FCY:
            rec = FCS[key].get(iso, {}).get(str(y), {}) or {}
            fv = rec.get("Births")
            if fv is None and rec.get("Pop") and rec.get("CBR") is not None:
                fv = rec["Pop"] * rec["CBR"] / 1000   # low file omits Births; derive it
            v = round(fv) if fv is not None and fv > 0 else lf
            lf = v; ser.append(v)
        var[key] = ser
    if max(obs + var["M"]) <= 0:
        continue
    countries.append({"n": c["name"], "i": iso, "f": iso2.get(iso, "").lower(),
                      "c": CONTS.index(cont), "o": obs, "L": var["L"], "M": var["M"], "H": var["H"]})

countries.sort(key=lambda x: -max(x["o"] + x["H"]))
DATA = {"obs": OBS, "fcy": FCY, "conts": CONTS, "colors": COLORS, "countries": countries}

HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sixty years of births, then the forecast — Demoria Research</title>
<meta name="description" content="Every country's annual births as bubbles, 1965 to 2100 — observed, then the UN WPP 2024 projection (low/median/high). Demoria Research.">
<meta property="og:title" content="A century of births — Demoria Research">
<meta property="og:description" content="Every country's annual births as bubbles, 1965 to 2100. Watch the world's cradle shift from East Asia to Africa.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#0c1a33;--navy2:#0a1529;--gold:#e8b84b;--cream:#f4ecd3;--ink:#eef1f6;--mut:rgba(238,241,246,.6)}
*{box-sizing:border-box}
html,body{margin:0;background:var(--navy2);color:var(--ink);font-family:'Manrope',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.topbar{background:var(--cream);height:50px;display:flex;align-items:center;padding:0 22px;gap:13px;border-bottom:2px solid rgba(12,26,51,.12);position:sticky;top:0;z-index:20}
.tb-back{display:inline-flex;align-items:center;gap:7px;color:#0c1a33;text-decoration:none;font-weight:700;font-size:.82rem}
.tb-back svg{width:16px;height:16px}
.tb-title{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:rgba(12,26,51,.55)}
.wrap{max-width:1560px;margin:0 auto;padding:10px 18px 18px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);text-align:center;margin-bottom:10px}
h1{font-weight:800;font-size:clamp(1.25rem,2.4vw,1.8rem);line-height:1.06;letter-spacing:-.02em;text-align:center;margin:0 0 5px}
h1 em{color:var(--gold);font-style:normal}
.sub{max-width:840px;margin:0 auto 10px;text-align:center;color:var(--mut);font-size:.84rem;line-height:1.4}
.stage{position:relative;background:radial-gradient(120% 100% at 50% 0,#12213d 0,#0a1529 70%);border:1px solid rgba(232,184,75,.22);border-radius:16px;overflow:hidden}
canvas{display:block;width:100%;touch-action:pan-y}
.yr{position:absolute;left:22px;top:16px;pointer-events:none}
.yr-n{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:clamp(2.4rem,6vw,4rem);line-height:1;color:#fff;letter-spacing:.02em}
.yr-badge{display:inline-block;margin-top:6px;font-family:'JetBrains Mono',monospace;font-size:.6rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:4px 9px;border-radius:5px}
.yr-obs{background:rgba(82,193,122,.16);color:#7fd79b;border:1px solid rgba(82,193,122,.4)}
.yr-fc{background:rgba(232,184,75,.14);color:var(--gold);border:1px solid rgba(232,184,75,.45)}
.tot{position:absolute;right:22px;top:16px;text-align:right;pointer-events:none}
.tot-n{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:clamp(1.1rem,2.4vw,1.6rem);color:var(--gold);line-height:1}
.tot-l{font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin-top:3px;font-family:'JetBrains Mono',monospace}
.legend{position:absolute;left:22px;bottom:16px;display:flex;flex-wrap:wrap;gap:6px 14px;max-width:60%;pointer-events:none}
.lg{display:inline-flex;align-items:center;gap:6px;font-size:.72rem;color:var(--mut)}
.lg i{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
.hint{position:absolute;right:22px;bottom:16px;font-size:.68rem;color:rgba(238,241,246,.4);pointer-events:none}
.stage.cols .hint{display:none}
#tip{position:absolute;display:none;pointer-events:none;z-index:8;background:rgba(9,17,33,.97);border:1px solid rgba(232,184,75,.5);border-radius:9px;padding:9px 12px;min-width:130px;box-shadow:0 8px 24px rgba(0,0,0,.45)}
#tip img{width:30px;height:auto;border-radius:2px;display:block;margin-bottom:6px;box-shadow:0 0 0 1px rgba(255,255,255,.18)}
#tip .tt-h{font-size:.95rem;color:#fff;font-weight:700}
#tip .tt-iso{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--gold);margin-left:5px;font-weight:700}
#tip .tt-r{display:flex;align-items:center;gap:6px;font-size:.72rem;color:var(--mut);margin-top:3px}
#tip .tt-r i{width:8px;height:8px;border-radius:50%}
#tip .tt-b{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--ink);margin-top:5px}
#tip .tt-b b{color:var(--gold)}
#tip .tt-rng{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--mut);margin-top:3px}
.ctl{display:flex;align-items:center;gap:12px 16px;flex-wrap:wrap;margin-top:12px;padding:10px 14px;background:rgba(255,255,255,.03);border:1px solid rgba(232,184,75,.16);border-radius:11px}
.play{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--gold);color:#0c1a33;border:0;border-radius:8px;padding:10px 18px;font-family:'Manrope';font-weight:700;font-size:.9rem;cursor:pointer;min-width:112px}
.play:hover{filter:brightness(1.06)}
.scrub{flex:1 1 220px;display:flex;align-items:center;gap:12px}
input[type=range]{flex:1;accent-color:var(--gold);height:5px}
.rng-yr{font-family:'JetBrains Mono',monospace;font-size:.82rem;color:var(--ink);min-width:38px;text-align:right}
.seg{display:inline-flex;align-items:center;gap:4px}
.slab{font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin-right:4px}
.sp,.vb,.mb{background:transparent;border:1px solid rgba(232,184,75,.35);color:var(--mut);border-radius:6px;padding:6px 9px;font-family:'JetBrains Mono',monospace;font-size:.72rem;cursor:pointer}
.sp.on,.vb.on,.mb.on{background:rgba(232,184,75,.16);color:var(--gold);border-color:var(--gold)}
.seg select{background:rgba(255,255,255,.05);color:var(--ink);border:1px solid rgba(232,184,75,.35);border-radius:6px;padding:6px 8px;font-family:'Manrope',sans-serif;font-size:.78rem;max-width:180px;cursor:pointer}
.src{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:.62rem;color:rgba(238,241,246,.42)}
.src a{color:rgba(232,184,75,.75);text-decoration:none}
@media(max-width:640px){.legend{max-width:100%;position:static;margin:10px 0 0;padding:0 4px}.tot,.yr,.hint{position:static;text-align:left;margin:6px 0 0;padding:0 4px}.hint{display:none}}
</style>
</head>
<body>
<div class="topbar">
  <a class="tb-back" href="https://demoriaresearch.com"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 4 7 10 13 16"/></svg>Demoria Research</a>
  <span class="tb-title">Births &middot; 1965&ndash;2100</span>
</div>
<div class="wrap">
  <h1>Sixty years of births, then <em>the forecast</em></h1>
  <p class="sub">Every bubble is a country, sized by its annual births &mdash; observed to 2025, then UN&nbsp;WPP&nbsp;2024 to 2100. Hover, tap or track a country.</p>
  <div class="stage" id="stage">
    <canvas id="cv"></canvas>
    <div class="yr"><div class="yr-n" id="yrN">1965</div><span class="yr-badge yr-obs" id="yrB">Observed</span></div>
    <div class="tot"><div class="tot-n" id="totN">0</div><div class="tot-l">births worldwide / year</div></div>
    <div class="legend" id="legend"></div>
    <div class="hint" id="hint">Tap or click a bubble to follow it</div>
    <div id="tip"></div>
  </div>
  <div class="ctl">
    <button class="play" id="play"><span id="playI">&#9654;</span><span id="playT">Play</span></button>
    <div class="scrub"><input type="range" id="rng" min="0" max="1" value="0" step="1"><span class="rng-yr" id="rngYr">1965</span></div>
    <div class="seg"><span class="slab">Speed</span><button class="sp" data-s="0.05">0.5&times;</button><button class="sp on" data-s="0.10">1&times;</button><button class="sp" data-s="0.20">2&times;</button></div>
    <div class="seg"><span class="slab">Projection 2030+</span><button class="vb" data-v="L">Low</button><button class="vb on" data-v="M">Median</button><button class="vb" data-v="H">High</button></div>
    <div class="seg"><span class="slab">Layout</span><button class="mb on" data-m="circle">Circle</button><button class="mb" data-m="cols">Columns</button></div>
    <div class="seg"><span class="slab">Track</span><select id="pick"><option value="">&mdash; none &mdash;</option></select></div>
    <span class="src">NSO + UN WPP 2024 &middot; <a href="/births/">Births Tracker</a></span>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
const DATA=__DATA__;
const OBS=DATA.obs, FCY=DATA.fcy, YEARS=OBS.concat(FCY), NOBS=OBS.length, N=YEARS.length;
const CONTS=DATA.conts, COLS=DATA.colors, CS=DATA.countries;
let maxB=0; CS.forEach(c=>{ const m=Math.max(Math.max(...c.o),Math.max(...c.H)); if(m>maxB)maxB=m; });
let variant='M', mode='circle';
const SHORT=['ASIA','AFRICA','EUROPE','LAT AMERICA','N AMERICA','MENA','OCEANIA'];
let totC=new Array(7).fill(0);
const fmtTot=t=>t>=1000?(t/1000).toFixed(1)+'M':Math.round(t)+'k';

const cv=document.getElementById('cv'), ctx=cv.getContext('2d'), stage=document.getElementById('stage'), tip=document.getElementById('tip');
let W=0,H=0,DPR=Math.min(window.devicePixelRatio||1,2), rScale, nodes, centers=[];
const CC=[[0.29,0.56],[0.69,0.55],[0.47,0.17],[0.17,0.80],[0.19,0.24],[0.52,0.86],[0.90,0.82]];
function layout(){
  W=stage.clientWidth;
  const ctlEl=document.querySelector('.ctl');
  const top=stage.getBoundingClientRect().top;              // space above the stage (topbar + hero)
  const below=12+(ctlEl?ctlEl.offsetHeight:58)+18+6;
  H=Math.max(300,Math.min(980,Math.floor(window.innerHeight-top-below)));
  cv.style.height=H+'px'; cv.width=W*DPR; cv.height=H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0);
  if(mode==='cols'){
    rScale=d3.scaleSqrt().domain([0,maxB]).range([0,Math.min(W/7*0.44,Math.min(W,H)*0.14)]);
    centers=[]; for(let i=0;i<7;i++) centers.push({x:W*(0.13+(i+0.5)*0.87/7),y:H*0.50});
  } else {
    rScale=d3.scaleSqrt().domain([0,maxB]).range([0,Math.min(W,H)*0.125]);
    const cx=W/2, cy=H*0.50, sp=Math.min(W,H)*0.20; centers=[];
    for(let i=0;i<7;i++){ const th=(i/7)*6.2832-1.5708; centers.push({x:cx+Math.cos(th)*sp,y:cy+Math.sin(th)*sp*0.7}); }
  }
}
layout();

nodes=CS.map(c=>({n:c.n,iso:c.i,f:c.f,c:c.c,o:c.o,L:c.L,M:c.M,H:c.H,r:0,bv:0,x:W/2+(Math.random()-0.5)*W*0.6,y:H/2+(Math.random()-0.5)*H*0.6}));

const sim=d3.forceSimulation(nodes).alphaDecay(0).velocityDecay(0.34)
  .force('collide',d3.forceCollide().radius(d=>d.r+0.6).strength(0.88).iterations(2)).stop();
function applyForces(){
  sim.force('x',d3.forceX(d=>centers[d.c].x).strength(mode==='cols'?0.30:0.13));
  sim.force('y',d3.forceY(d=>centers[d.c].y).strength(mode==='cols'?0.06:0.15));
}
applyForces();

function valV(nd,i,v){ return i<NOBS ? nd.o[i] : nd[v][i-NOBS]; }
function birthsV(nd,yf,v){ const i=Math.floor(yf),t=yf-i,a=valV(nd,i,v),b=valV(nd,Math.min(i+1,N-1),v); return a+(b-a)*t; }
function births(nd,yf){ return birthsV(nd,yf,variant); }
function setR(yf){ totC.fill(0); for(const nd of nodes){ nd.bv=births(nd,yf); nd.r=rScale(nd.bv); totC[nd.c]+=nd.bv; } }

function draw(yf){
  ctx.clearRect(0,0,W,H);
  const fc=Math.round(yf)>=NOBS;
  for(const nd of nodes){
    if(nd.r<0.6) continue;
    ctx.beginPath(); ctx.arc(nd.x,nd.y,nd.r,0,6.2832);
    ctx.globalAlpha=fc?0.8:0.92; ctx.fillStyle=COLS[nd.c]; ctx.fill();
    ctx.globalAlpha=1; ctx.lineWidth=fc?1:0.8;
    ctx.strokeStyle=fc?'rgba(255,255,255,.28)':'rgba(255,255,255,.16)'; ctx.stroke();
  }
  // continent labels + totals (below/outside each group)
  ctx.textAlign='center'; ctx.textBaseline='alphabetic';
  ctx.font="700 12px 'JetBrains Mono', monospace";
  if(mode==='cols'){
    for(let ci=0;ci<CONTS.length;ci++){
      ctx.fillStyle=COLS[ci]; ctx.fillText(SHORT[ci],centers[ci].x,H-22);
      ctx.fillStyle='#fff'; ctx.fillText(fmtTot(totC[ci]),centers[ci].x,H-8);
    }
  } else {
    const gx=W/2, gy=H*0.50;
    for(let ci=0;ci<CONTS.length;ci++){
      let sx=0,sy=0,cnt=0,maxOut=0;
      for(const nd of nodes){ if(nd.c===ci&&nd.r>0.6){ sx+=nd.x; sy+=nd.y; cnt++;
        const d=Math.hypot(nd.x-gx,nd.y-gy)+nd.r; if(d>maxOut)maxOut=d; } }
      if(!cnt) continue;
      let dx=sx/cnt-gx, dy=sy/cnt-gy, L=Math.hypot(dx,dy);
      if(L<1){ dx=0; dy=-1; L=1; }
      const lx=Math.max(48,Math.min(W-48,gx+dx/L*(maxOut+16)));
      const ly=Math.max(15,Math.min(H-6,gy+dy/L*(maxOut+16)+4));
      const s=SHORT[ci]+' '+fmtTot(totC[ci]);
      ctx.lineWidth=3.5; ctx.strokeStyle='rgba(8,17,33,.9)'; ctx.strokeText(s,lx,ly);
      ctx.fillStyle=COLS[ci]; ctx.fillText(s,lx,ly);
    }
  }
  // ISO3 codes on bubbles where they fit
  ctx.textBaseline='middle';
  for(const nd of nodes){
    if(nd.r<11||!nd.iso) continue;
    ctx.font='700 '+Math.min(nd.r*0.8,21)+"px 'JetBrains Mono', monospace";
    ctx.fillStyle='rgba(10,18,34,.85)'; ctx.fillText(nd.iso,nd.x,nd.y);
  }
  // uncertainty fan (low-high rings) for the active bubble in forecast years
  const act=hover||pinned;
  if(act&&act.r>0.6&&fc){
    const lo=rScale(birthsV(act,yf,'L')), hi=rScale(birthsV(act,yf,'H'));
    ctx.setLineDash([4,3]); ctx.lineWidth=1.3; ctx.strokeStyle='rgba(255,255,255,.6)';
    ctx.beginPath(); ctx.arc(act.x,act.y,hi,0,6.2832); ctx.stroke();
    ctx.beginPath(); ctx.arc(act.x,act.y,Math.max(lo,0.8),0,6.2832); ctx.stroke();
    ctx.setLineDash([]);
  }
  // pinned: gold ring + name label (so you can follow a small one)
  if(pinned&&pinned.r>0.6){
    ctx.beginPath(); ctx.arc(pinned.x,pinned.y,pinned.r+3,0,6.2832); ctx.lineWidth=3; ctx.strokeStyle='#e8b84b'; ctx.stroke();
    ctx.textAlign='center'; ctx.textBaseline='alphabetic'; ctx.font="700 13px 'JetBrains Mono', monospace";
    const ly=pinned.y-pinned.r-8; ctx.lineWidth=3.5; ctx.strokeStyle='rgba(8,17,33,.92)'; ctx.strokeText(pinned.n,pinned.x,ly);
    ctx.fillStyle='#e8b84b'; ctx.fillText(pinned.n,pinned.x,ly); ctx.textBaseline='middle';
  }
  // hover: white ring
  if(hover&&hover!==pinned&&hover.r>0.6){ ctx.beginPath(); ctx.arc(hover.x,hover.y,hover.r+2.5,0,6.2832); ctx.lineWidth=2.5; ctx.strokeStyle='#fff'; ctx.stroke(); }
}

const yrN=document.getElementById('yrN'), yrB=document.getElementById('yrB'), totN=document.getElementById('totN'),
      rng=document.getElementById('rng'), rngYr=document.getElementById('rngYr'), pick=document.getElementById('pick');
const VNAME={L:'Low',M:'Median',H:'High'};
function ui(yf){
  const yi=Math.round(yf), yr=YEARS[yi], fc=yr>2025;
  yrN.textContent=yr;
  yrB.textContent=fc?('UN WPP · '+VNAME[variant]):'Observed';
  yrB.className='yr-badge '+(fc?'yr-fc':'yr-obs');
  let tot=0; for(const nd of nodes) tot+=nd.bv||0;
  totN.textContent=Math.round(tot/1000)+'M';
  rng.value=yi; rngYr.textContent=yr;
}
document.getElementById('legend').innerHTML=CONTS.map((c,i)=>'<span class="lg"><i style="background:'+COLS[i]+'"></i>'+c+'</span>').join('');
rng.max=N-1;
CS.slice().sort((a,b)=>a.n.localeCompare(b.n)).forEach(c=>{ const o=document.createElement('option'); o.value=c.i; o.textContent=c.n; pick.appendChild(o); });

// hover / pin
let mouse={x:-1,y:-1}, hover=null, pinned=null;
const fmtB=v=>v>=1e6?(v/1e6).toFixed(2)+'M':Math.round(v).toLocaleString('en');
function pickAt(mx,my){ let best=null,bd=1e9; for(const nd of nodes){ if(nd.r<3) continue; const dx=nd.x-mx,dy=nd.y-my,d=Math.sqrt(dx*dx+dy*dy); if(d<nd.r&&d<bd){ bd=d; best=nd; } } return best; }
function setPinned(n){ pinned=n; pick.value=n?n.iso:''; }
cv.addEventListener('mousemove',e=>{ const r=cv.getBoundingClientRect(); mouse.x=e.clientX-r.left; mouse.y=e.clientY-r.top; });
cv.addEventListener('mouseleave',()=>{ mouse.x=-1; mouse.y=-1; hover=null; });
cv.addEventListener('click',e=>{ const r=cv.getBoundingClientRect(); const n=pickAt(e.clientX-r.left,e.clientY-r.top); setPinned(n&&n===pinned?null:n); });
cv.addEventListener('touchstart',e=>{ const t=e.touches[0],r=cv.getBoundingClientRect(),mx=t.clientX-r.left,my=t.clientY-r.top; const n=pickAt(mx,my); if(n){ e.preventDefault(); mouse.x=-1; mouse.y=-1; setPinned(n===pinned?null:n); } else setPinned(null); },{passive:false});
pick.onchange=()=>{ pinned=pick.value?nodes.find(n=>n.iso===pick.value):null; };
function updateHover(){ if(mouse.x<0){ hover=null; cv.style.cursor=pinned?'pointer':'default'; return; } const n=pickAt(mouse.x,mouse.y); hover=n; cv.style.cursor=n?'pointer':'default'; }
function updateTip(yf){
  const t=hover||pinned;
  if(!t){ tip.style.display='none'; return; }
  const yr=YEARS[Math.round(yf)], fc=Math.round(yf)>=NOBS;
  let html=(t.f?'<img src="https://flagcdn.com/w40/'+t.f+'.png" alt="">':'')+
    '<div class="tt-h">'+t.n+'<span class="tt-iso">'+(t.iso||'')+'</span></div>'+
    '<div class="tt-r"><i style="background:'+COLS[t.c]+'"></i>'+CONTS[t.c]+'</div>'+
    '<div class="tt-b"><b>'+fmtB((t.bv||0)*1000)+'</b> births &middot; '+yr+'</div>';
  if(fc) html+='<div class="tt-rng">low&ndash;high: '+fmtB(birthsV(t,yf,'L')*1000)+' &ndash; '+fmtB(birthsV(t,yf,'H')*1000)+'</div>';
  tip.innerHTML=html; tip.style.display='block';
  const tw=tip.offsetWidth||160, th=tip.offsetHeight||84, useMouse=(hover&&mouse.x>=0);
  let tx,ty;
  if(useMouse){ tx=mouse.x+16; ty=mouse.y+16; if(tx+tw>W-6) tx=mouse.x-tw-16; if(ty+th>H-6) ty=mouse.y-th-16; }
  else { tx=t.x-tw/2; ty=t.y-t.r-th-10; if(ty<6) ty=t.y+t.r+10; }
  tip.style.left=Math.max(6,Math.min(tx,W-tw-6))+'px'; tip.style.top=Math.max(6,Math.min(ty,H-th-6))+'px';
}

let yf=0, playing=false, speed=0.10, raf;
function frame(){
  if(playing){ yf+=speed; if(yf>=N-1){ yf=N-1; playing=false; syncPlay(); } }
  setR(yf);
  sim.force('collide').radius(d=>d.r+0.6); sim.alpha(0.5); sim.tick();
  const bt=mode==='cols'?8:2, bb=mode==='cols'?36:2;
  for(const nd of nodes){ nd.x=Math.max(nd.r+2,Math.min(W-nd.r-2,nd.x)); nd.y=Math.max(nd.r+bt,Math.min(H-nd.r-bb,nd.y)); }
  updateHover(); draw(yf); ui(yf); updateTip(yf);
  raf=requestAnimationFrame(frame);
}
function syncPlay(){ document.getElementById('playI').innerHTML=playing?'&#10073;&#10073;':'&#9654;'; document.getElementById('playT').textContent=playing?'Pause':(yf>=N-1?'Replay':'Play'); }
document.getElementById('play').onclick=()=>{ if(yf>=N-1&&!playing) yf=0; playing=!playing; syncPlay(); };
rng.oninput=e=>{ yf=+e.target.value; if(playing){playing=false;syncPlay();} };
document.querySelectorAll('.sp').forEach(b=>b.onclick=()=>{ speed=+b.dataset.s; document.querySelectorAll('.sp').forEach(x=>x.classList.toggle('on',x===b)); });
document.querySelectorAll('.vb').forEach(b=>b.onclick=()=>{ variant=b.dataset.v; document.querySelectorAll('.vb').forEach(x=>x.classList.toggle('on',x===b)); });
document.querySelectorAll('.mb').forEach(b=>b.onclick=()=>{ mode=b.dataset.m; document.querySelectorAll('.mb').forEach(x=>x.classList.toggle('on',x===b)); document.getElementById('legend').style.display=(mode==='cols')?'none':''; stage.classList.toggle('cols',mode==='cols'); relayout(); });
function relayout(){ layout(); applyForces(); }
window.addEventListener('resize',relayout);
window.addEventListener('load',relayout);
if(document.fonts&&document.fonts.ready) document.fonts.ready.then(relayout);

setR(0); for(let k=0;k<130;k++){ sim.force('collide').radius(d=>d.r+0.6); sim.alpha(0.6); sim.tick(); }
draw(0); ui(0); syncPlay(); raf=requestAnimationFrame(frame);
setTimeout(()=>{ if(!playing&&yf<1){ playing=true; syncPlay(); } }, 900);
</script>
</body></html>"""

out = ROOT / "public" / "bubbles" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":"))))
print(f"wrote {out} ({round(out.stat().st_size/1024)} KB, {len(countries)} countries)")
