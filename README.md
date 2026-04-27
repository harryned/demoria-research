# Demoria Research

Static site for [demoriaresearch.com](https://demoriaresearch.com), home of the Demographic Health Index (DHI).

## Layout

```
.                       # source files (HTML pages, JSON data, Python build scripts)
├── public/             # what Cloudflare Pages serves
│   ├── index.html      # landing page
│   └── dhi/index.html  # Demographic Health Index (self-contained)
└── ...
```

The DHI app at `/dhi/` is a single self-contained HTML file: all sub-views (world map, dashboard, fiscal page, methodology, reading mode) and their data are embedded as base64-encoded blobs inside `dhi_combined.html`.

## Deploying to Cloudflare Pages

```
wrangler pages project create demoria-research --production-branch=main
wrangler pages deploy public --project-name=demoria-research
```

Custom domain `demoriaresearch.com` is added via the Pages dashboard or:

```
wrangler pages domain add demoriaresearch.com --project-name=demoria-research
```

## Rebuilding

The page sources at the repo root (`dhi_dashboard.html`, `dhi_world_map.html`, `dhi_fiscal.html`, `dhi_methodology.html`, `dhi_reading.html`, `dhi_sowhat.html`, `dhi_landing.html`, `dhi_splash.html`) are the editable originals. After modifying any of them, re-embed into `dhi_combined.html` and copy to `public/dhi/index.html`:

```
python3 -c "
import base64, re
with open('dhi_combined.html') as f: s = f.read()
for ta_id, src in [('d-dash','dhi_dashboard.html'), ('d-fiscal','dhi_fiscal.html'), ('d-map','dhi_world_map.html')]:
    with open(src,'rb') as fh: b64 = base64.b64encode(fh.read()).decode()
    s = re.sub(r'(<textarea id=\"'+ta_id+r'\"[^>]*>)[^<]*(</textarea>)', lambda m: m.group(1)+b64+m.group(2), s)
with open('dhi_combined.html','w') as f: f.write(s)
"
cp dhi_combined.html public/dhi/index.html
```
