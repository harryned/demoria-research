"""Build dhi_home_trial2.html — 10 home-page layout options.
All centred, all designed to fill the viewport with no empty
space and no scroll. Picker at the bottom to live-switch.
"""
import shutil

SRC = 'dhi_globe.html'
DST = 'dhi_home_trial2.html'
shutil.copy2(SRC, DST)
h = open(DST).read()

h = h.replace('<title>DHI v2.0 &mdash; The World</title>',
              '<title>DHI v2.0 (home trial 2) &mdash; The World</title>', 1)
h = h.replace('<title>DHI v2.0 — The World</title>',
              '<title>DHI v2.0 (home trial 2) — The World</title>', 1)

# ---- CSS for the 10 variants ----
CSS = r"""
/* ===== HOME TRIAL 2 — 10 layout options ===== */
/* Each variant is scoped under body.hl-X. */

/* Shared: kill the current live Editorial styles, then each variant
   replaces them. */
body[class*="hl2-"] #view-home{height:calc(100vh - 90px);overflow:hidden}
body[class*="hl2-"] #view-home .home-wrap{height:100%;display:flex;flex-direction:column;padding:0;margin:0;box-sizing:border-box;gap:0}
body[class*="hl2-"] #view-home .home-ribbon,
body[class*="hl2-"] #view-home .home-cta-h,
body[class*="hl2-"] #view-home .home-cta-h-2,
body[class*="hl2-"] #view-home .home-stats,
body[class*="hl2-"] #view-home .hc-api,
body[class*="hl2-"] #view-home .home-foot,
body[class*="hl2-"] #view-home .hh-or{display:none!important}
/* RESET hero card baseline so each variant can rebuild */
body[class*="hl2-"] #view-home .home-hero{margin:0;padding:0;max-width:none;background:none;box-shadow:none;border:0;border-radius:0;display:flex;flex-direction:column;align-items:center;text-align:center;justify-content:center}
body[class*="hl2-"] #view-home .home-hero *{text-align:center}
body[class*="hl2-"] #view-home .home-cta-grid{margin:0;max-width:none;padding:0;grid-template-rows:auto}

/* ============================================ */
/* A — CENTRED EDITORIAL 60/40 — cream hero centred, 2x3 navy right */
body.hl2-A #view-home .home-wrap{display:grid!important;grid-template-columns:1.4fr 1fr;grid-template-rows:1fr;gap:18px;padding:18px 22px}
body.hl2-A #view-home .home-hero{grid-column:1;background:#f4ecd3;border-radius:18px;padding:36px clamp(28px,4vw,52px);box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(181,132,32,.32);justify-content:center}
body.hl2-A #view-home .hh-eye{margin:0 0 8px}
body.hl2-A #view-home .hh-title{font-size:clamp(1.7rem,2.9vw,2.5rem);line-height:1.05;margin:0 0 10px}
body.hl2-A #view-home .hh-sub{font-size:.95rem;margin:0 0 22px;line-height:1.45;max-width:560px}
body.hl2-A #view-home .hh-cta{width:100%;max-width:520px;margin:0 auto}
body.hl2-A #view-home .hh-cta-row{justify-content:center}
body.hl2-A #view-home .hh-hint{margin:10px 0 0;font-size:.8rem;color:rgba(12,26,51,.62)!important}
body.hl2-A #view-home .home-cta-grid{grid-column:2;grid-template-columns:repeat(2,1fr)!important;grid-template-rows:repeat(3,1fr);gap:10px}
body.hl2-A #view-home .home-cta-grid .hc-card{padding:14px 16px;justify-content:space-between;border-radius:12px}
body.hl2-A #view-home .home-cta-grid .hc-num{font-size:.55rem}
body.hl2-A #view-home .home-cta-grid .hc-t{font-size:1rem;margin:0 0 4px}
body.hl2-A #view-home .home-cta-grid .hc-d{font-size:.72rem;line-height:1.35;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

/* ============================================ */
/* B — CENTRED STACK — single column, title top, picker middle, 6 tiles in a row */
body.hl2-B #view-home .home-wrap{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:1fr auto!important;gap:14px;padding:22px 28px;align-items:center;justify-items:center}
body.hl2-B #view-home .home-hero{grid-column:1!important;grid-row:1!important;max-width:880px;background:#f4ecd3;border-radius:18px;padding:28px 42px 32px;box-shadow:0 22px 60px rgba(0,0,0,.40),inset 0 0 0 1px rgba(181,132,32,.30);align-self:center}
body.hl2-B #view-home .hh-eye{margin:0 0 6px}
body.hl2-B #view-home .hh-title{font-size:clamp(1.8rem,3.2vw,2.7rem);line-height:1.05;margin:0 0 12px}
body.hl2-B #view-home .hh-sub{font-size:1rem;margin:0 0 22px;line-height:1.45;max-width:640px}
body.hl2-B #view-home .hh-cta{width:100%;max-width:560px;margin:0 auto}
body.hl2-B #view-home .hh-cta-row{justify-content:center}
body.hl2-B #view-home .hh-hint{margin:10px 0 0;font-size:.82rem;color:rgba(12,26,51,.62)!important}
body.hl2-B #view-home .home-cta-grid{grid-column:1!important;grid-row:2!important;grid-template-columns:repeat(6,1fr)!important;gap:8px;width:100%;max-width:1200px}
body.hl2-B #view-home .home-cta-grid .hc-card{padding:14px 12px;text-align:left;border-radius:12px}
body.hl2-B #view-home .home-cta-grid .hc-card *{text-align:left}
body.hl2-B #view-home .home-cta-grid .hc-num{font-size:.55rem;margin-bottom:4px}
body.hl2-B #view-home .home-cta-grid .hc-t{font-size:.84rem;line-height:1.1;margin:0 0 3px}
body.hl2-B #view-home .home-cta-grid .hc-d{font-size:.66rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-B #view-home .home-cta-grid .hc-arr{font-size:.95rem}

/* ============================================ */
/* C — CENTRED BAND TOP — full-width centred hero band, 2x3 cream tiles below */
body.hl2-C #view-home{background:linear-gradient(180deg,#0a1730 0%,#050b1c 100%)}
body.hl2-C #view-home .home-wrap{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:auto 1fr!important;gap:14px;padding:18px 22px}
body.hl2-C #view-home .home-hero{grid-column:1!important;grid-row:1!important;background:rgba(244,236,211,.04)!important;border:1px solid rgba(232,184,75,.30)!important;border-radius:14px;padding:22px 42px 22px;align-items:center;justify-content:center}
body.hl2-C #view-home .hh-eye{margin:0 0 4px;color:var(--gold)}
body.hl2-C #view-home .hh-title{font-size:clamp(1.5rem,2.6vw,2.1rem);line-height:1.05;margin:0 0 8px;color:#fff}
body.hl2-C #view-home .hh-title em{color:var(--gold);font-style:normal}
body.hl2-C #view-home .hh-title .hh-acr{color:rgba(255,255,255,.4)}
body.hl2-C #view-home .hh-sub{font-size:.92rem;margin:0 0 14px;line-height:1.4;max-width:780px;color:rgba(255,255,255,.78)}
body.hl2-C #view-home .hh-sub b{color:#fff}
body.hl2-C #view-home .hh-cta{width:100%;max-width:560px;margin:0 auto}
body.hl2-C #view-home .hh-cta-row{justify-content:center}
body.hl2-C #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important}
body.hl2-C #view-home .hh-pick .hp-name{color:#fff!important}
body.hl2-C #view-home .hh-hint{margin:8px 0 0;font-size:.78rem;color:rgba(255,255,255,.6)!important}
body.hl2-C #view-home .hh-hint b{color:#fff!important}
body.hl2-C #view-home .home-cta-grid{grid-column:1!important;grid-row:2!important;grid-template-columns:repeat(3,1fr)!important;grid-template-rows:repeat(2,1fr);gap:12px}
body.hl2-C #view-home .home-cta-grid .hc-card{background:#fffaef!important;border:1px solid rgba(181,132,32,.30)!important;color:#0c1a33!important;padding:18px 22px;border-radius:14px;box-shadow:0 12px 28px rgba(0,0,0,.30);align-items:flex-start}
body.hl2-C #view-home .home-cta-grid .hc-card *{text-align:left}
body.hl2-C #view-home .home-cta-grid .hc-num{color:#b58420!important;font-size:.6rem}
body.hl2-C #view-home .home-cta-grid .hc-t{color:#0c1a33!important;font-size:1.05rem;margin:0 0 4px}
body.hl2-C #view-home .home-cta-grid .hc-d{color:rgba(12,26,51,.62)!important;font-size:.78rem;line-height:1.35;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-C #view-home .home-cta-grid .hc-arr{color:#b58420!important;font-size:1.2rem}

/* ============================================ */
/* D — MAGAZINE COVER — huge centred title + picker, 6 thin row of cards below */
body.hl2-D #view-home .home-wrap{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:1fr auto!important;gap:14px;padding:18px 22px}
body.hl2-D #view-home .home-hero{grid-column:1!important;grid-row:1!important;background:#f4ecd3!important;border-radius:18px;padding:36px clamp(28px,4vw,60px);box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(181,132,32,.32);justify-content:center}
body.hl2-D #view-home .hh-eye{margin:0 0 10px;font-size:.62rem;letter-spacing:.26em}
body.hl2-D #view-home .hh-title{font-size:clamp(2.4rem,4.6vw,4rem);line-height:1.02;margin:0 0 16px;font-weight:700;letter-spacing:-.02em}
body.hl2-D #view-home .hh-sub{font-size:1.05rem;margin:0 0 26px;line-height:1.45;max-width:760px}
body.hl2-D #view-home .hh-cta{width:100%;max-width:580px;margin:0 auto}
body.hl2-D #view-home .hh-cta-row{justify-content:center}
body.hl2-D #view-home .hh-hint{margin:12px 0 0;font-size:.85rem}
body.hl2-D #view-home .home-cta-grid{grid-column:1!important;grid-row:2!important;grid-template-columns:repeat(6,1fr)!important;gap:6px;max-width:1240px;margin:0 auto;width:100%}
body.hl2-D #view-home .home-cta-grid .hc-card{padding:12px 12px;text-align:left;border-radius:10px;flex-direction:row;align-items:center;justify-content:space-between;min-height:0}
body.hl2-D #view-home .home-cta-grid .hc-num{display:none}
body.hl2-D #view-home .home-cta-grid .hc-body{flex:1;text-align:left}
body.hl2-D #view-home .home-cta-grid .hc-body *{text-align:left}
body.hl2-D #view-home .home-cta-grid .hc-t{font-size:.86rem;line-height:1.1;margin:0}
body.hl2-D #view-home .home-cta-grid .hc-d{display:none}
body.hl2-D #view-home .home-cta-grid .hc-arr{font-size:1.05rem}

/* ============================================ */
/* E — HERO TOP + BIG TILES — compact hero band on top, 2x3 big cream tiles */
body.hl2-E #view-home{background:linear-gradient(180deg,#0a1730 0%,#050b1c 100%)}
body.hl2-E #view-home .home-wrap{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:auto 1fr!important;gap:14px;padding:14px 22px 18px}
body.hl2-E #view-home .home-hero{grid-column:1!important;grid-row:1!important;background:rgba(244,236,211,.06)!important;border:1px solid rgba(232,184,75,.32)!important;border-radius:12px;padding:14px 22px;display:grid;grid-template-columns:auto 1fr auto;gap:24px;align-items:center;text-align:left}
body.hl2-E #view-home .hh-eye{display:none}
body.hl2-E #view-home .hh-title{grid-column:1;color:#fff!important;font-size:1.25rem;margin:0;line-height:1.1;text-align:left;white-space:nowrap}
body.hl2-E #view-home .hh-title em{color:var(--gold)!important;font-style:normal}
body.hl2-E #view-home .hh-title .hh-acr{color:rgba(255,255,255,.4)!important;font-size:.5em}
body.hl2-E #view-home .hh-sub{grid-column:2;color:rgba(255,255,255,.66)!important;font-size:.82rem;margin:0;line-height:1.4;max-width:none;text-align:left}
body.hl2-E #view-home .hh-sub b{color:var(--gold)!important;text-decoration:none!important}
body.hl2-E #view-home .hh-cta{grid-column:3;width:auto;max-width:none;margin:0}
body.hl2-E #view-home .hh-cta-row{justify-content:flex-end}
body.hl2-E #view-home .hh-hint{display:none}
body.hl2-E #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important;min-height:42px;padding:6px 14px}
body.hl2-E #view-home .hh-pick .hp-name{color:#fff!important}
body.hl2-E #view-home .hh-primary{min-height:42px}
body.hl2-E #view-home .home-cta-grid{grid-column:1!important;grid-row:2!important;grid-template-columns:repeat(3,1fr)!important;grid-template-rows:repeat(2,1fr);gap:12px}
body.hl2-E #view-home .home-cta-grid .hc-card{background:#fffaef!important;border:1px solid rgba(181,132,32,.30)!important;color:#0c1a33!important;padding:22px 26px;border-radius:14px;box-shadow:0 12px 30px rgba(0,0,0,.35);align-items:center;justify-content:center;text-align:center}
body.hl2-E #view-home .home-cta-grid .hc-card *{text-align:center}
body.hl2-E #view-home .home-cta-grid .hc-num{color:#b58420!important;font-size:.62rem;margin-bottom:8px}
body.hl2-E #view-home .home-cta-grid .hc-t{color:#0c1a33!important;font-size:1.2rem;margin:0 0 6px;line-height:1.1}
body.hl2-E #view-home .home-cta-grid .hc-d{color:rgba(12,26,51,.62)!important;font-size:.82rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-E #view-home .home-cta-grid .hc-arr{display:none}

/* ============================================ */
/* F — CENTRED VERTICAL COLUMN — narrow centred column, tiles in a row */
body.hl2-F #view-home .home-wrap{display:flex!important;flex-direction:column;align-items:center;justify-content:center;padding:18px 22px;gap:18px}
body.hl2-F #view-home .home-hero{background:transparent;border-radius:0;padding:0;max-width:720px;align-items:center}
body.hl2-F #view-home .hh-eye{color:var(--gold);margin:0 0 6px}
body.hl2-F #view-home .hh-title{color:#fff;font-size:clamp(2rem,3.6vw,2.8rem);line-height:1.05;margin:0 0 12px}
body.hl2-F #view-home .hh-title em{color:var(--gold);font-style:normal}
body.hl2-F #view-home .hh-title .hh-acr{color:rgba(255,255,255,.45)}
body.hl2-F #view-home .hh-sub{color:rgba(255,255,255,.78);font-size:1rem;margin:0 0 22px;line-height:1.45;max-width:600px}
body.hl2-F #view-home .hh-sub b{color:#fff}
body.hl2-F #view-home .hh-cta{width:100%;max-width:580px;margin:0 auto}
body.hl2-F #view-home .hh-cta-row{justify-content:center}
body.hl2-F #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important}
body.hl2-F #view-home .hh-pick .hp-name{color:#fff!important}
body.hl2-F #view-home .hh-hint{color:rgba(255,255,255,.62)!important;margin:10px 0 0}
body.hl2-F #view-home .hh-hint b{color:#fff!important}
body.hl2-F #view-home .home-cta-grid{grid-template-columns:repeat(6,1fr)!important;gap:8px;width:100%;max-width:1180px}
body.hl2-F #view-home .home-cta-grid .hc-card{padding:14px 12px;text-align:center;border-radius:12px}
body.hl2-F #view-home .home-cta-grid .hc-card *{text-align:center}
body.hl2-F #view-home .home-cta-grid .hc-num{font-size:.55rem;margin-bottom:6px}
body.hl2-F #view-home .home-cta-grid .hc-t{font-size:.85rem;line-height:1.1;margin:0 0 4px}
body.hl2-F #view-home .home-cta-grid .hc-d{font-size:.66rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-F #view-home .home-cta-grid .hc-arr{display:none}

/* ============================================ */
/* G — INVERTED DARK HERO + 2x3 CREAM CARDS centred grid */
body.hl2-G #view-home{background:linear-gradient(180deg,#0a1730 0%,#050b1c 100%)}
body.hl2-G #view-home .home-wrap{display:grid!important;grid-template-columns:1fr 1.2fr;gap:18px;padding:18px 22px;align-items:stretch}
body.hl2-G #view-home .home-hero{grid-column:1;background:#0c1a33!important;border:1px solid rgba(232,184,75,.30)!important;border-radius:18px;padding:36px clamp(24px,3vw,48px);align-items:center;justify-content:center}
body.hl2-G #view-home .hh-eye{color:var(--gold);margin:0 0 8px}
body.hl2-G #view-home .hh-title{color:#fff;font-size:clamp(1.7rem,2.9vw,2.5rem);line-height:1.05;margin:0 0 12px}
body.hl2-G #view-home .hh-title em{color:var(--gold);font-style:normal}
body.hl2-G #view-home .hh-title .hh-acr{color:rgba(255,255,255,.45)}
body.hl2-G #view-home .hh-sub{color:rgba(255,255,255,.78);font-size:.95rem;margin:0 0 22px;line-height:1.45;max-width:480px}
body.hl2-G #view-home .hh-sub b{color:#fff}
body.hl2-G #view-home .hh-cta{width:100%;max-width:520px;margin:0 auto}
body.hl2-G #view-home .hh-cta-row{justify-content:center}
body.hl2-G #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important}
body.hl2-G #view-home .hh-pick .hp-name{color:#fff!important}
body.hl2-G #view-home .hh-hint{color:rgba(255,255,255,.62)!important;margin:10px 0 0}
body.hl2-G #view-home .hh-hint b{color:#fff!important}
body.hl2-G #view-home .home-cta-grid{grid-column:2;grid-template-columns:repeat(2,1fr)!important;grid-template-rows:repeat(3,1fr);gap:10px}
body.hl2-G #view-home .home-cta-grid .hc-card{background:#fffaef!important;border:1px solid rgba(181,132,32,.30)!important;color:#0c1a33!important;padding:16px 18px;border-radius:12px;box-shadow:0 10px 24px rgba(0,0,0,.30);align-items:center;justify-content:center;text-align:center}
body.hl2-G #view-home .home-cta-grid .hc-card *{text-align:center}
body.hl2-G #view-home .home-cta-grid .hc-num{color:#b58420!important;font-size:.55rem;margin-bottom:5px}
body.hl2-G #view-home .home-cta-grid .hc-t{color:#0c1a33!important;font-size:1rem;margin:0 0 4px;line-height:1.1}
body.hl2-G #view-home .home-cta-grid .hc-d{color:rgba(12,26,51,.62)!important;font-size:.74rem;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-G #view-home .home-cta-grid .hc-arr{display:none}

/* ============================================ */
/* H — ASYMMETRIC 40/60 CENTRED — small cream card left + 2x3 big navy cards right */
body.hl2-H #view-home .home-wrap{display:grid!important;grid-template-columns:1fr 1.5fr;gap:18px;padding:18px 22px;align-items:stretch}
body.hl2-H #view-home .home-hero{grid-column:1;background:#f4ecd3;border-radius:18px;padding:32px 28px;box-shadow:0 30px 80px rgba(0,0,0,.40),inset 0 0 0 1px rgba(181,132,32,.32);justify-content:center;align-items:center}
body.hl2-H #view-home .hh-eye{margin:0 0 6px}
body.hl2-H #view-home .hh-title{font-size:clamp(1.4rem,2.4vw,2rem);line-height:1.05;margin:0 0 10px}
body.hl2-H #view-home .hh-sub{font-size:.84rem;margin:0 0 20px;line-height:1.4}
body.hl2-H #view-home .hh-cta{width:100%}
body.hl2-H #view-home .hh-cta-row{justify-content:center;flex-direction:column;gap:8px}
body.hl2-H #view-home .hh-pick,body.hl2-H #view-home .hh-primary{flex:1 1 100%;width:100%}
body.hl2-H #view-home .hh-primary{justify-content:center}
body.hl2-H #view-home .hh-hint{margin:10px 0 0;font-size:.74rem}
body.hl2-H #view-home .home-cta-grid{grid-column:2;grid-template-columns:repeat(2,1fr)!important;grid-template-rows:repeat(3,1fr);gap:10px}
body.hl2-H #view-home .home-cta-grid .hc-card{padding:18px 22px;border-radius:12px;align-items:flex-start;justify-content:space-between}
body.hl2-H #view-home .home-cta-grid .hc-card *{text-align:left}
body.hl2-H #view-home .home-cta-grid .hc-num{font-size:.6rem;margin-bottom:6px}
body.hl2-H #view-home .home-cta-grid .hc-t{font-size:1.1rem;margin:0 0 5px}
body.hl2-H #view-home .home-cta-grid .hc-d{font-size:.8rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-H #view-home .home-cta-grid .hc-arr{font-size:1.2rem}

/* ============================================ */
/* I — STACKED COMPACT — centred title + centred picker + 1x6 row of cards */
body.hl2-I #view-home .home-wrap{display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:22px;padding:24px 22px;background:radial-gradient(80% 80% at 50% 40%,rgba(232,184,75,.06) 0%,transparent 60%)}
body.hl2-I #view-home .home-hero{background:transparent;padding:0;max-width:880px;align-items:center}
body.hl2-I #view-home .hh-eye{color:var(--gold);margin:0 0 6px;font-size:.65rem;letter-spacing:.22em}
body.hl2-I #view-home .hh-title{color:#fff;font-size:clamp(2.2rem,4vw,3.2rem);line-height:1.02;margin:0 0 14px;font-weight:300;letter-spacing:-.02em}
body.hl2-I #view-home .hh-title em{color:var(--gold);font-weight:400;font-style:italic}
body.hl2-I #view-home .hh-title .hh-acr{color:rgba(255,255,255,.45)}
body.hl2-I #view-home .hh-sub{color:rgba(255,255,255,.78);font-size:1rem;margin:0 0 20px;line-height:1.45;max-width:640px}
body.hl2-I #view-home .hh-sub b{color:#fff}
body.hl2-I #view-home .hh-cta{width:100%;max-width:580px;margin:0 auto}
body.hl2-I #view-home .hh-cta-row{justify-content:center}
body.hl2-I #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important}
body.hl2-I #view-home .hh-pick .hp-name{color:#fff!important}
body.hl2-I #view-home .hh-hint{display:none}
body.hl2-I #view-home .home-cta-grid{grid-template-columns:repeat(6,1fr)!important;gap:8px;width:100%;max-width:1180px}
body.hl2-I #view-home .home-cta-grid .hc-card{padding:14px 12px 14px;border:1px solid rgba(232,184,75,.30)!important;background:rgba(244,236,211,.04)!important;border-radius:12px;text-align:center;align-items:center;transition:all .15s}
body.hl2-I #view-home .home-cta-grid .hc-card:hover{background:rgba(232,184,75,.10)!important;border-color:rgba(232,184,75,.55)!important;transform:translateY(-2px)}
body.hl2-I #view-home .home-cta-grid .hc-card *{text-align:center}
body.hl2-I #view-home .home-cta-grid .hc-num{font-size:.55rem;color:var(--gold);margin-bottom:6px}
body.hl2-I #view-home .home-cta-grid .hc-t{font-size:.88rem;line-height:1.1;margin:0 0 4px;color:#fff}
body.hl2-I #view-home .home-cta-grid .hc-d{font-size:.66rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;color:rgba(255,255,255,.62)}
body.hl2-I #view-home .home-cta-grid .hc-arr{display:none}

/* ============================================ */
/* J — HERO + WRAP — cream centred hero in middle, 3 cards left + 3 cards right */
body.hl2-J #view-home .home-wrap{display:grid!important;grid-template-columns:1fr 1.6fr 1fr;gap:14px;padding:18px 22px;align-items:stretch}
body.hl2-J #view-home .home-hero{grid-column:2;background:#f4ecd3;border-radius:18px;padding:34px clamp(28px,4vw,52px);box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(181,132,32,.32);justify-content:center}
body.hl2-J #view-home .hh-eye{margin:0 0 6px}
body.hl2-J #view-home .hh-title{font-size:clamp(1.8rem,3vw,2.5rem);line-height:1.05;margin:0 0 10px}
body.hl2-J #view-home .hh-sub{font-size:.95rem;margin:0 0 22px;line-height:1.45;max-width:560px}
body.hl2-J #view-home .hh-cta{width:100%;max-width:520px;margin:0 auto}
body.hl2-J #view-home .hh-cta-row{justify-content:center}
body.hl2-J #view-home .hh-hint{margin:10px 0 0;font-size:.8rem;color:rgba(12,26,51,.62)!important}
body.hl2-J #view-home .home-cta-grid{display:contents!important}
body.hl2-J #view-home .home-cta-grid .hc-card{padding:14px 16px;border-radius:12px;align-items:flex-start;justify-content:space-between}
body.hl2-J #view-home .home-cta-grid .hc-card *{text-align:left}
body.hl2-J #view-home .home-cta-grid .hc-num{font-size:.55rem;margin-bottom:5px}
body.hl2-J #view-home .home-cta-grid .hc-t{font-size:.95rem;margin:0 0 4px}
body.hl2-J #view-home .home-cta-grid .hc-d{font-size:.7rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl2-J #view-home .home-cta-grid .hc-arr{font-size:1rem}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(1){grid-column:1;grid-row:1}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(2){grid-column:1;grid-row:2}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(3){grid-column:1;grid-row:3}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(4){grid-column:3;grid-row:1}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(5){grid-column:3;grid-row:2}
body.hl2-J #view-home .home-cta-grid .hc-card:nth-child(6){grid-column:3;grid-row:3}
body.hl2-J #view-home .home-wrap{grid-template-rows:repeat(3,1fr)}
body.hl2-J #view-home .home-hero{grid-row:1 / span 3}

/* ===== picker ===== */
#hlp2{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:99999;display:flex;flex-wrap:wrap;justify-content:center;gap:4px;max-width:96vw;padding:6px 8px;background:rgba(15,28,56,.97);border:1px solid rgba(232,184,75,.55);border-radius:10px;box-shadow:0 12px 32px rgba(0,0,0,.5)}
#hlp2 button{font-family:'JetBrains Mono',monospace;font-size:.55rem;letter-spacing:.04em;text-transform:uppercase;font-weight:700;padding:6px 8px;border-radius:5px;border:1px solid rgba(255,255,255,.16);background:transparent;color:rgba(255,255,255,.72);cursor:pointer;white-space:nowrap}
#hlp2 button.on{background:#f4ecd3;color:#0c1a33;border-color:rgba(181,132,32,.65)}
"""

PICKER = r"""
<div id="hlp2" aria-label="Home layout options 2">
  <button data-h="cur">Current (live)</button>
  <button data-h="A">A &middot; Centred 60/40</button>
  <button data-h="B">B &middot; Centred stack</button>
  <button data-h="C">C &middot; Hero band + 3x2</button>
  <button data-h="D">D &middot; Magazine cover</button>
  <button data-h="E">E &middot; Top bar + tiles</button>
  <button data-h="F">F &middot; Centred column</button>
  <button data-h="G">G &middot; Navy hero + 2x3</button>
  <button data-h="H">H &middot; Asym 40/60</button>
  <button data-h="I">I &middot; Stacked compact</button>
  <button data-h="J">J &middot; Hero + side cards</button>
</div>
<script>
(function(){
  var btns=document.querySelectorAll('#hlp2 button');
  function apply(v){
    document.body.classList.remove('hl2-A','hl2-B','hl2-C','hl2-D','hl2-E','hl2-F','hl2-G','hl2-H','hl2-I','hl2-J');
    void document.body.offsetWidth;
    if(v!=='cur') document.body.classList.add('hl2-'+v);
    btns.forEach(b=>b.classList.toggle('on', b.dataset.h===v));
    try{localStorage.setItem('dhi_hl2', v);}catch(e){}
  }
  btns.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.h)));
  var init='A'; try{ init=localStorage.getItem('dhi_hl2')||init; }catch(e){}
  setTimeout(function(){
    if(typeof show==='function') show('home');
    apply(init);
  }, 300);
})();
</script>
"""

assert '</style>' in h
h = h.replace('</style>', CSS + '</style>', 1)
assert '</body>' in h
h = h.replace('</body>', PICKER + '</body>', 1)
open(DST, 'w').write(h)
print('built ' + DST + ' (' + str(round(len(h)/1024/1024, 2)) + ' MB) — 10 home layout options')
