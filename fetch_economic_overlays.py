"""
Fetches GDP per capita (PPP), government debt/GDP, and old-age dependency ratio
from World Bank Open Data API for all countries in the DHI dataset.

Run from the same directory as your dash_data_unified.json file.

Usage:
    python fetch_economic_overlays.py

Outputs:
    economic_overlays.json          — standalone overlay data
    dash_data_unified.json          — merged in-place (backed up first)
"""

import urllib.request
import json
import time
import shutil
from pathlib import Path

# World Bank indicator codes
INDICATORS = {
    'gdp_pc_ppp':   'NY.GDP.PCAP.PP.CD',     # GDP per capita, PPP (current $)
    'gov_debt_pct': 'GC.DOD.TOTL.GD.ZS',     # Central gov debt (% GDP)
    'oadr_fiscal':  'SP.POP.DPND.OL',        # Old-age dependency ratio (%)
    'gdp_growth':   'NY.GDP.MKTP.KD.ZG',     # GDP growth (annual %)
}

LABELS = {
    'gdp_pc_ppp':   'GDP per capita (PPP, $)',
    'gov_debt_pct': 'Government debt (% GDP)',
    'oadr_fiscal':  'Old-age dependency (%)',
    'gdp_growth':   'GDP growth (annual %)',
}

TARGET_YEAR = 2023  # WB lags ~2 years; 2023 has best coverage in 2025/2026

def fetch_indicator(code: str, year: int) -> dict:
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
           f"?format=json&date={year}&per_page=400")
    req = urllib.request.Request(url, headers={'User-Agent': 'DHI/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read())
    if not isinstance(payload, list) or len(payload) < 2:
        return {}
    out = {}
    for e in payload[1]:
        iso3 = e.get('countryiso3code')
        val  = e.get('value')
        if iso3 and val is not None:
            out[iso3] = float(val)
    return out


def fetch_with_fallback(code: str) -> dict:
    """Try most recent year, fall back through earlier years for missing countries."""
    combined = {}
    for year in [TARGET_YEAR, TARGET_YEAR-1, TARGET_YEAR-2, TARGET_YEAR-3, TARGET_YEAR-4]:
        year_data = fetch_indicator(code, year)
        for iso3, val in year_data.items():
            combined.setdefault(iso3, val)
        time.sleep(0.4)
    return combined


def main():
    print(f"Fetching economic overlays (target year: {TARGET_YEAR})\n")
    
    overlays = {}
    for key, code in INDICATORS.items():
        print(f"  {LABELS[key]:<32} ({code})...", end=' ', flush=True)
        data = fetch_with_fallback(code)
        for iso3, val in data.items():
            overlays.setdefault(iso3, {})[key] = round(val, 2)
        print(f"{len(data)} countries")
    
    # Save standalone
    Path('economic_overlays.json').write_text(json.dumps(overlays, indent=2))
    print(f"\n✓ Saved economic_overlays.json ({len(overlays)} countries)")
    
    # Merge into dashboard data if present
    dash_path = Path('dash_data_unified.json')
    if dash_path.exists():
        # Backup first
        backup = dash_path.with_suffix('.json.bak')
        shutil.copy2(dash_path, backup)
        print(f"✓ Backed up to {backup}")
        
        with open(dash_path) as f:
            dash = json.load(f)
        
        merged = 0
        for iso3, country in dash.get('countries', {}).items():
            if iso3 in overlays:
                country['economic'] = overlays[iso3]
                merged += 1
        
        with open(dash_path, 'w') as f:
            json.dump(dash, f, separators=(',', ':'))
        print(f"✓ Merged into {merged} countries in dash_data_unified.json")
    else:
        print("\nNote: dash_data_unified.json not found in current directory.")
        print("Either move this script to your DHI folder, or merge manually.")
    
    # Print sample for sanity check
    print("\nSample (UK):")
    if 'GBR' in overlays:
        for k, v in overlays['GBR'].items():
            print(f"  {LABELS[k]:<32} {v}")
    print("\nSample (Japan):")
    if 'JPN' in overlays:
        for k, v in overlays['JPN'].items():
            print(f"  {LABELS[k]:<32} {v}")

if __name__ == '__main__':
    main()
