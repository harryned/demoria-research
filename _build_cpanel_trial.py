"""Build dhi_cpanel_trial.html — country-panel (cpanel) layout options.
On load it opens the World map and a sample country panel (Jamaica),
with a bottom picker to switch between layouts. Every fixed option
moves "Open full country profile" to the top as a gold bar and fits
the panel with no scroll.

  Current     baseline (button at bottom, scrolls)
  1 Essentials  CTA top -> pillars -> key statistics (no chart)
  2 Trend       CTA top -> pillars -> trajectory chart (no stats)
  3 Complete    CTA top -> pillars -> small chart -> key statistics
  4 Context too CTA top, keep everything (will scroll a little)
"""
import shutil

SRC = 'dhi_globe.html'
DST = 'dhi_cpanel_trial.html'
shutil.copy2(SRC, DST)
h = open(DST).read()

h = h.replace('<title>DHI v2.0 &mdash; The World</title>',
              '<title>DHI v2.0 (cpanel trial) &mdash; The World</title>', 1)
h = h.replace('<title>DHI v2.0 — The World</title>',
              '<title>DHI v2.0 (cpanel trial) — The World</title>', 1)

CSS = r"""
/* ===== CPANEL TRIAL ===== */
/* Shared base for the fixed options (cp1-4): CTA to the top as a gold bar */
body.cpfix #cpanel{display:flex!important;flex-direction:column;padding:16px 18px 18px}
body.cpfix #cpanel > .cp-rank{order:1}
body.cpfix #cpanel > .cp-name{order:2}
body.cpfix #cpanel > .cp-cat{order:3}
body.cpfix #cpanel > .cp-scorebox{order:4}
body.cpfix #cpanel > #cp-full{order:5}
body.cpfix #cpanel > *{order:6}
body.cpfix #cp-full{margin:16px 0 8px!important;background:#e0b54a!important;color:#0c1a33!important;border:0!important;font-weight:700!important;padding:12px!important;border-radius:10px!important;box-shadow:0 8px 22px rgba(181,132,32,.28)!important;text-align:center}
body.cpfix #cp-full:hover{background:#ecc35e!important}

/* 1 — Essentials: pillars + key stats, drop chart/context/note */
body.cp1 .cp-h:has(+ #cp-traj), body.cp1 #cp-traj{display:none!important}
body.cp1 .cp-h-ctx, body.cp1 #cp-ctx, body.cp1 #cp-note{display:none!important}
body.cp1 .cp-h{margin:16px 0 9px!important}

/* 2 — Trend: pillars + trajectory, drop stats/context/note */
body.cp2 .cp-h:has(+ #cp-stats), body.cp2 #cp-stats{display:none!important}
body.cp2 .cp-h-ctx, body.cp2 #cp-ctx, body.cp2 #cp-note{display:none!important}
body.cp2 .cp-h{margin:16px 0 9px!important}
body.cp2 #cp-traj{height:150px!important}

/* 3 — Complete: pillars + small chart + key stats, drop context/note */
body.cp3 #cpanel{padding:14px 16px 14px!important}
body.cp3 .cp-name{font-size:1.3rem!important;margin:3px 0 6px!important}
body.cp3 .cp-scorebox{margin:9px 0 2px!important}
body.cp3 .cp-score{font-size:2rem!important}
body.cp3 .cp-h{margin:11px 0 6px!important}
body.cp3 .pbar{margin:3px 0!important}
body.cp3 .pbar .pt{height:5px!important}
body.cp3 #cp-traj{height:80px!important}
body.cp3 .cp-stat{padding:5px 10px!important}
body.cp3 .cp-stat .sv{font-size:.85rem!important}
body.cp3 .cp-h-ctx, body.cp3 #cp-ctx, body.cp3 #cp-note{display:none!important}
body.cp3 #cp-full{margin:12px 0 4px!important;padding:10px!important;font-size:.84rem!important}

/* 4 — Context too: keep everything, compacted (will scroll a little) */
body.cp4 #cpanel{padding:14px 16px 16px!important}
body.cp4 .cp-h{margin:12px 0 6px!important}
body.cp4 #cp-traj{height:90px!important}
body.cp4 .pbar{margin:4px 0!important}

/* picker */
#cpp{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:99999;display:flex;flex-wrap:wrap;justify-content:center;gap:4px;max-width:96vw;padding:6px 8px;background:rgba(15,28,56,.97);border:1px solid rgba(232,184,75,.55);border-radius:10px;box-shadow:0 12px 32px rgba(0,0,0,.5)}
#cpp button{font-family:'JetBrains Mono',monospace;font-size:.55rem;letter-spacing:.04em;text-transform:uppercase;font-weight:700;padding:6px 9px;border-radius:5px;border:1px solid rgba(255,255,255,.16);background:transparent;color:rgba(255,255,255,.72);cursor:pointer;white-space:nowrap}
#cpp button.on{background:#f4ecd3;color:#0c1a33;border-color:rgba(181,132,32,.65)}
#cpp .cpp-note{color:rgba(232,184,75,.85);font-size:.5rem;align-self:center;padding:0 4px;max-width:160px;line-height:1.3}
"""

PICKER = r"""
<div id="cpp" aria-label="Country panel options">
  <button data-c="cur">Current</button>
  <button data-c="1">1 &middot; Essentials</button>
  <button data-c="2">2 &middot; Trend</button>
  <button data-c="3">3 &middot; Complete</button>
  <button data-c="4">4 &middot; Context too</button>
  <span class="cpp-note">switch a country on the map to repopulate</span>
</div>
<script>
(function(){
  var btns=document.querySelectorAll('#cpp button');
  function redraw(){
    try{ if(typeof openPanel==='function' && window.__cptrialC) openPanel(window.__cptrialC); }catch(e){}
  }
  function apply(v){
    document.body.classList.remove('cpfix','cp1','cp2','cp3','cp4');
    if(v!=='cur'){ document.body.classList.add('cpfix'); document.body.classList.add('cp'+v); }
    btns.forEach(b=>b.classList.toggle('on', b.dataset.c===v));
    try{localStorage.setItem('dhi_cpp', v);}catch(e){}
    redraw();
  }
  btns.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.c)));
  var init='3'; try{ init=localStorage.getItem('dhi_cpp')||init; }catch(e){}
  // Open world + a sample country panel, then apply the chosen option.
  function boot(){
    if(typeof show!=='function' || typeof byIso==='undefined' || typeof openPanel!=='function'){ setTimeout(boot,200); return; }
    show('world');
    setTimeout(function(){
      var iso=null;
      ['JAM','USA','JPN','GBR'].some(function(k){ if(byIso[k]){iso=k;return true;} return false; });
      if(!iso){ var ks=Object.keys(byIso); iso=ks[0]; }
      window.__cptrialC=byIso[iso];
      openPanel(byIso[iso]);
      setTimeout(function(){ apply(init); }, 350);
    }, 900);
  }
  setTimeout(boot, 400);
  // keep __cptrialC in sync if the user clicks another country
  if(typeof window.__patchedOpen==='undefined'){
    window.__patchedOpen=true;
    var _t=setInterval(function(){
      if(typeof openPanel==='function'){
        clearInterval(_t);
        var orig=openPanel;
        window.openPanel=function(c){ window.__cptrialC=c; return orig(c); };
      }
    }, 150);
  }
})();
</script>
"""

assert '</style>' in h
h = h.replace('</style>', CSS + '</style>', 1)
assert '</body>' in h
h = h.replace('</body>', PICKER + '</body>', 1)
open(DST, 'w').write(h)
print('built ' + DST + ' (' + str(round(len(h)/1024/1024, 2)) + ' MB) — cpanel picker: 4 options + current')
