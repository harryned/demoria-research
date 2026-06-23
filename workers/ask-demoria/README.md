# Ask Demoria — Cloudflare Worker

A grounded Q&A endpoint for the Demoria dataset. The model answers in prose, but
every figure comes from a tool call against the bundled data (`data.json`),
stamped with its source tier (NSO / DRE / WPP). It never invents a number.

`data.json` is a compact bundle (236 countries, the cliffs, the policy library),
regenerated from the repo data — see the builder snippet in the project notes.

## Run locally
```bash
cd workers/ask-demoria
npm install -g wrangler            # if needed
echo "ANTHROPIC_API_KEY=sk-ant-..." > .dev.vars   # local secret (gitignored)
wrangler dev                       # then open http://localhost:8787
```
The GET page is a tiny demo box. POST `{"question": "..."}` returns `{"answer": "..."}`.

## Deploy
```bash
wrangler secret put ANTHROPIC_API_KEY   # paste your key (stored encrypted)
wrangler deploy                         # -> https://ask-demoria.<subdomain>.workers.dev
```

## Embed the box on demoriaresearch.com
Drop this anywhere on the site, pointing at your deployed Worker URL:
```html
<input id="askd" placeholder="Ask Demoria about any country…" style="width:100%;padding:14px;border-radius:10px">
<div id="askdA" style="white-space:pre-wrap;margin-top:12px"></div>
<script>
const W="https://ask-demoria.<your-subdomain>.workers.dev";
askd.addEventListener("keydown",async e=>{ if(e.key!=="Enter")return; askdA.textContent="Thinking…";
  const r=await fetch(W,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({question:askd.value})});
  const d=await r.json(); askdA.textContent=d.answer||("Error: "+d.error); });
</script>
```
CORS is open (`*`); tighten `Access-Control-Allow-Origin` in `src/index.js` to your domain for production.

## Regenerate data.json
When the dataset changes, rebuild the bundle from `_data_export.json` + `public/cliffs_data.json`
+ the policy library (the builder lives in the project's AI notes), then `wrangler deploy`.

Model defaults to `claude-opus-4-8`; edit `MODEL` in `src/index.js` to use `claude-sonnet-4-6` for volume.
