#!/usr/bin/env python3
"""Build public/bubbles/index.html — an animated bubble chart of annual births
per country, 1965-2100 (observed national + UN WPP to 2025, UN WPP 2024 medium
forecast 2026-2100). Bubbles are countries, sized by births, coloured by region,
force-packed and animated through the years. Self-contained, brand-styled.

  python3 _build_bubbles.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
exp = json.loads((ROOT / "_data_export.json").read_text())
bt = json.loads((ROOT / "public" / "births_data.json").read_text())
fc = json.loads((ROOT / "_wpp_fc_med.json").read_text())
reg = {c["iso"]: c["region"] for c in bt["countries"]}

CONT = {'East Asia': 'Asia', 'Southeast Asia': 'Asia', 'South Asia': 'Asia', 'Central Asia': 'Asia',
        'Western & Northern Europe': 'Europe', 'Central & Eastern Europe': 'Europe',
        'North America': 'North America', 'Latin America & Caribbean': 'Latin America',
        'Caucasus & Türkiye': 'Middle East & N. Africa', 'Middle East & North Africa': 'Middle East & N. Africa',
        'Gulf (nationals)': 'Middle East & N. Africa', 'Sub-Saharan Africa': 'Africa', 'Oceania': 'Oceania'}
CONTS = ['Asia', 'Africa', 'Europe', 'Latin America', 'North America', 'Middle East & N. Africa', 'Oceania']
COLORS = ['#e8b84b', '#52c17a', '#5b9bd5', '#ec6f9e', '#a68bf0', '#37c2b0', '#f0954e']

YEARS = list(range(1965, 2101))
countries = []
for iso, c in exp.items():
    b = c.get("ind", {}).get("births"); yrs = c.get("yrs")
    if not b or not yrs:
        continue
    cont = CONT.get(reg.get(iso), 'Asia')
    obs = {y: b[i] for i, y in enumerate(yrs) if b[i] is not None}
    series = []; last = 0
    for y in YEARS:
        if y in obs:
            v = obs[y]
        else:
            fv = (fc.get(iso, {}).get(str(y), {}) or {}).get("Births")
            v = fv if fv is not None else last
        v = round(v) if v and v > 0 else 0
        last = v; series.append(v)
    if max(series) <= 0:
        continue
    countries.append({"n": c["name"], "c": CONTS.index(cont), "b": series})

countries.sort(key=lambda x: -max(x["b"]))
DATA = {"years": YEARS, "conts": CONTS, "colors": COLORS, "countries": countries}

HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sixty years of births, then the forecast — Demoria Research</title>
<meta name="description" content="Every country's annual births as bubbles, 1965 to 2100 — observed, then the UN WPP 2024 projection. Demoria Research.">
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
.wrap{max-width:1180px;margin:0 auto;padding:26px 22px 40px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);text-align:center;margin-bottom:10px}
h1{font-weight:800;font-size:clamp(1.7rem,3.6vw,2.6rem);line-height:1.06;letter-spacing:-.02em;text-align:center;margin:0 0 10px}
h1 em{color:var(--gold);font-style:normal}
.sub{max-width:760px;margin:0 auto 20px;text-align:center;color:var(--mut);font-size:.98rem;line-height:1.5}
.stage{position:relative;background:radial-gradient(120% 100% at 50% 0,#12213d 0,#0a1529 70%);border:1px solid rgba(232,184,75,.22);border-radius:16px;overflow:hidden}
canvas{display:block;width:100%}
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
.ctl{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:16px;padding:12px 16px;background:rgba(255,255,255,.03);border:1px solid rgba(232,184,75,.16);border-radius:11px}
.play{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--gold);color:#0c1a33;border:0;border-radius:8px;padding:10px 18px;font-family:'Manrope';font-weight:700;font-size:.9rem;cursor:pointer;min-width:112px}
.play:hover{filter:brightness(1.06)}
.scrub{flex:1 1 260px;display:flex;align-items:center;gap:12px}
input[type=range]{flex:1;accent-color:var(--gold);height:5px}
.rng-yr{font-family:'JetBrains Mono',monospace;font-size:.82rem;color:var(--ink);min-width:38px;text-align:right}
.speeds{display:inline-flex;gap:4px}
.sp{background:transparent;border:1px solid rgba(232,184,75,.35);color:var(--mut);border-radius:6px;padding:6px 9px;font-family:'JetBrains Mono',monospace;font-size:.72rem;cursor:pointer}
.sp.on{background:rgba(232,184,75,.16);color:var(--gold);border-color:var(--gold)}
.foot{margin-top:18px;text-align:center;color:var(--mut);font-size:.78rem;line-height:1.6}
.foot a{color:var(--gold)}
@media(max-width:640px){.legend{max-width:100%;position:static;margin:10px 0 0;padding:0 4px}.tot{position:static;text-align:left;margin-top:6px}.yr{position:static;margin:8px 0 4px;padding:0 4px}.stage .over{position:static}}
</style>
</head>
<body>
<div class="topbar">
  <a class="tb-back" href="https://demoriaresearch.com"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 4 7 10 13 16"/></svg>Demoria Research</a>
  <span class="tb-title">Births &middot; 1965&ndash;2100</span>
</div>
<div class="wrap">
  <div class="eyebrow">Demoria Research &middot; The moving picture</div>
  <h1>Sixty years of births, then <em>the forecast</em></h1>
  <p class="sub">Every bubble is a country; its size is that country&rsquo;s annual births. Sixty years are observed (national statistics and the UN), then the UN&rsquo;s World Population Prospects 2024 carries the picture to 2100. Watch the world&rsquo;s cradle drift from East Asia to Africa.</p>
  <div class="stage" id="stage">
    <canvas id="cv"></canvas>
    <div class="yr"><div class="yr-n" id="yrN">1965</div><span class="yr-badge yr-obs" id="yrB">Observed</span></div>
    <div class="tot"><div class="tot-n" id="totN">0</div><div class="tot-l">births worldwide / year</div></div>
    <div class="legend" id="legend"></div>
  </div>
  <div class="ctl">
    <button class="play" id="play"><span id="playI">&#9654;</span><span id="playT">Play</span></button>
    <div class="scrub"><input type="range" id="rng" min="0" max="135" value="0" step="1"><span class="rng-yr" id="rngYr">1965</span></div>
    <div class="speeds"><button class="sp" data-s="0.06">0.5&times;</button><button class="sp on" data-s="0.12">1&times;</button><button class="sp" data-s="0.24">2&times;</button></div>
  </div>
  <p class="foot">Annual live births. Observed 1965&ndash;2025 (national statistical offices where reported, otherwise UN&nbsp;WPP&nbsp;2024); projected 2026&ndash;2100 (UN&nbsp;WPP&nbsp;2024, medium variant). 220 countries and territories. &middot; <a href="https://demoriaresearch.com/births/">Birth &amp; Fertility Tracker</a></p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
const DATA=__DATA__;
const YEARS=DATA.years, CONTS=DATA.conts, COLS=DATA.colors, CS=DATA.countries;
const N=YEARS.length;
let maxB=0; CS.forEach(c=>{c.mx=Math.max(...c.b); if(c.mx>maxB)maxB=c.mx;});

const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const stage=document.getElementById('stage');
let W=0,H=0,DPR=Math.min(window.devicePixelRatio||1,2), rScale, nodes;

function layout(){
  W=stage.clientWidth; H=Math.max(430,Math.round(Math.min(W*0.62,640)));
  cv.style.height=H+'px'; cv.width=W*DPR; cv.height=H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0);
  const maxR=Math.min(W,H)*0.135;
  rScale=d3.scaleSqrt().domain([0,maxB]).range([0,maxR]);
}
layout();

nodes=CS.map((c,i)=>({i,n:c.n,c:c.c,b:c.b,r:0,x:W/2+(Math.random()-0.5)*W*0.6,y:H/2+(Math.random()-0.5)*H*0.6}));

const sim=d3.forceSimulation(nodes)
  .alphaDecay(0).velocityDecay(0.32)
  .force('x',d3.forceX(()=>W/2).strength(0.028))
  .force('y',d3.forceY(()=>H/2).strength(0.045))
  .force('collide',d3.forceCollide().radius(d=>d.r+0.6).strength(0.86).iterations(2))
  .stop();

function births(node,yf){
  const i=Math.floor(yf), t=yf-i, a=node.b[i], b=node.b[Math.min(i+1,N-1)];
  return a+(b-a)*t;
}
function setR(yf){ nodes.forEach(nd=>{ nd.bv=births(nd,yf); nd.r=rScale(nd.bv); }); }

function draw(yf){
  ctx.clearRect(0,0,W,H);
  const fc=yf>60; // 2025 is index 60
  // bubbles
  for(const nd of nodes){
    if(nd.r<0.6) continue;
    ctx.beginPath(); ctx.arc(nd.x,nd.y,nd.r,0,6.2832);
    ctx.globalAlpha=fc?0.8:0.92; ctx.fillStyle=COLS[nd.c]; ctx.fill();
    ctx.globalAlpha=1; ctx.lineWidth=fc?1:0.8;
    ctx.strokeStyle=fc?'rgba(255,255,255,.28)':'rgba(255,255,255,.16)'; ctx.stroke();
  }
  // labels on the big ones
  ctx.textAlign='center'; ctx.textBaseline='middle';
  for(const nd of nodes){
    if(nd.r<20) continue;
    const fs=Math.max(10,Math.min(nd.r*0.42,18));
    ctx.font='700 '+fs+"px Manrope, sans-serif";
    ctx.fillStyle='rgba(12,20,38,.9)'; ctx.fillText(nd.n,nd.x,nd.y-(nd.r>34?fs*0.4:0));
    if(nd.r>34){ ctx.font='700 '+(fs*0.8)+"px 'JetBrains Mono', monospace"; ctx.fillStyle='rgba(12,20,38,.72)';
      ctx.fillText((nd.bv/1000).toFixed(1)+'M',nd.x,nd.y+fs*0.75); }
  }
}

const yrN=document.getElementById('yrN'), yrB=document.getElementById('yrB'),
      totN=document.getElementById('totN'), rng=document.getElementById('rng'), rngYr=document.getElementById('rngYr');
function ui(yf){
  const yi=Math.round(yf), yr=YEARS[yi];
  yrN.textContent=yr;
  const fc=yr>2025;
  yrB.textContent=fc?'UN WPP forecast':'Observed';
  yrB.className='yr-badge '+(fc?'yr-fc':'yr-obs');
  let tot=0; for(const nd of nodes) tot+=nd.bv||0;
  totN.textContent=(tot/1000).toFixed(0)+'M';
  rng.value=yi; rngYr.textContent=yr;
}

// legend
document.getElementById('legend').innerHTML=CONTS.map((c,i)=>
  '<span class="lg"><i style="background:'+COLS[i]+'"></i>'+c+'</span>').join('');

let yf=0, playing=false, speed=0.12, raf;
function frame(){
  if(playing){ yf+=speed; if(yf>=N-1){ yf=N-1; playing=false; syncPlay(); } }
  setR(yf);
  sim.force('collide').radius(d=>d.r+0.6);
  sim.alpha(0.5); sim.tick();
  // keep in bounds
  for(const nd of nodes){ nd.x=Math.max(nd.r+2,Math.min(W-nd.r-2,nd.x)); nd.y=Math.max(nd.r+2,Math.min(H-nd.r-2,nd.y)); }
  draw(yf); ui(yf);
  raf=requestAnimationFrame(frame);
}
function syncPlay(){ document.getElementById('playI').innerHTML=playing?'&#10073;&#10073;':'&#9654;'; document.getElementById('playT').textContent=playing?'Pause':(yf>=N-1?'Replay':'Play'); }
document.getElementById('play').onclick=()=>{ if(yf>=N-1&&!playing) yf=0; playing=!playing; syncPlay(); };
rng.oninput=e=>{ yf=+e.target.value; if(playing){playing=false;syncPlay();} };
document.querySelectorAll('.sp').forEach(b=>b.onclick=()=>{ speed=+b.dataset.s; document.querySelectorAll('.sp').forEach(x=>x.classList.toggle('on',x===b)); });
window.addEventListener('resize',()=>{ layout(); sim.force('x').initialize(nodes); });

// settle initial packing, then start
setR(0); for(let k=0;k<120;k++){ sim.force('collide').radius(d=>d.r+0.6); sim.alpha(0.6); sim.tick(); }
draw(0); ui(0); syncPlay();
raf=requestAnimationFrame(frame);
// auto-play shortly after load
setTimeout(()=>{ if(!playing&&yf<1){ playing=true; syncPlay(); } }, 900);
</script>
</body></html>"""

out = ROOT / "public" / "bubbles" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":"))))
print(f"wrote {out} ({round(out.stat().st_size/1024)} KB, {len(countries)} countries)")
