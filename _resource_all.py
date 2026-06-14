#!/usr/bin/env python3
"""Re-apply the NATIONAL DATA LAYER on top of the UN-WPP baseline, in order.
Run this after any base rebuild or override cascade so the national figures
(reported births, national deaths, published NSO TFR) stay the durable basis
of BOTH the raw-data tables and the Birth Tracker.

Order matters:
  1. births  — reported national annual (sheet) where published, else WPP
  2. deaths  — national vital-registration (wiki vital-stats) + pre-2023 births
  3. deaths_extra — the 9 hand-fetched countries + France metropole scope fix
  4. tfr     — NSO published TFR (wiki vital-stats + Eurostat) -> blob + tracker
Each step recomputes single-year natural change and re-tags NSO/DRE/WPP.
Idempotent. Then rebuild the tracker page + static pages and copy to public.
"""
import subprocess, sys, shutil
def run(cmd):
    print(f"\n=== {cmd} ===")
    r=subprocess.run([sys.executable,cmd],capture_output=True,text=True)
    print((r.stdout or '').strip()[-600:])
    if r.returncode!=0:
        print((r.stderr or '')[-800:]); raise SystemExit(f"FAILED: {cmd}")

for step in ('_resource_births.py','_resource_deaths.py','_resource_deaths_extra.py','_resource_tfr.py'):
    run(step)

# propagate to the Birth Tracker page + static pages
run('_embed_births_data.py')
run('_build_static_pages.py')
shutil.copy('dhi_globe.html','public/index.html')
shutil.copy('dhi_globe.html','public/dhi/index.html')
print("\nNational data layer re-applied to raw-data tables + Birth Tracker.")
