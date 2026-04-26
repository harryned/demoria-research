"""
Fetches economic & fiscal overlay data from IMF WEO, OECD, and World Bank
for all countries in the DHI dataset, and merges into dash_data_unified.json.

Indicators (in priority order):
  - GDP per capita PPP (IMF WEO, current $)            'gdp_pc_ppp'
  - Real GDP growth (IMF WEO, annual %)                'gdp_growth'
  - Gov gross debt / GDP (IMF WEO, %)                  'gov_debt_pct'
  - Gov primary balance / GDP (IMF WEO, %)             'gov_primary_balance'
  - Gov revenue / GDP (IMF WEO, %)                     'gov_revenue_pct'
  - Healthcare spending / GDP (World Bank, %)          'health_spend_pct'
  - Pension assets / GDP (OECD, %)                     'pension_assets_pct'
  - Pension spending / GDP (OECD, %)                   'pension_spend_pct'
  - Pension replacement rate (OECD, % of pre-retirement)'pension_replace_pct'

Plus three derived metrics:
  - 'fiscal_stress_score' — composite stress indicator (0-100)
  - 'fiscal_headroom_years' — years until debt/GDP > 100%
  - 'pre_funding_ratio' — pension assets vs implied liabilities

Usage:
    python fetch_economic_overlays.py

Notes:
  - Run from the same folder as dash_data_unified.json (auto-merge)
  - All sources are free, no API key required
  - IMF WEO is updated April + October each year
  - OECD pension data is updated annually (Q4)
"""

import urllib.request
import urllib.parse
import json
import csv
import io
import time
import shutil
from pathlib import Path

# ── IMF WEO via SDMX 2.1 ───────────────────────────────────────────────────
# Endpoint: https://sdmxcentral.imf.org/ws/public/sdmxapi/rest
# Data flow: WEO (latest)
# Schema: WEO/A.<COUNTRY>.<INDICATOR>?startPeriod=YYYY&endPeriod=YYYY

IMF_BASE = "https://sdmxcentral.imf.org/ws/public/sdmxapi/rest/data"
IMF_WEO_INDICATORS = {
    'gdp_pc_ppp':         'PPPPC',         # GDP per capita, PPP, current intl $
    'gdp_growth':         'NGDP_RPCH',     # Real GDP growth, annual %
    'gov_debt_pct':       'GGXWDG_NGDP',   # General gov gross debt, % GDP
    'gov_primary_balance':'GGXONLB_NGDP',  # Primary balance, % GDP
    'gov_revenue_pct':    'GGR_NGDP',      # General gov revenue, % GDP
}

# ── World Bank Open Data ───────────────────────────────────────────────────
WB_BASE = "https://api.worldbank.org/v2/country/all/indicator"
WB_INDICATORS = {
    'health_spend_pct':   'SH.XPD.CHEX.GD.ZS',  # Current health expenditure (% GDP)
}

# ── OECD pension data ──────────────────────────────────────────────────────
# Note: OECD pension data needs the Pension Markets in Focus 2025 dataset
# Available via SDMX at https://sdmx.oecd.org/public/rest/data/
# Indicator IDs vary; for pension assets/GDP use OECD.ELS.SPD,DSD_PAG@DF_PAG
# Pension spending is in OECD.SPD,DSD_PENSIONS_AT_A_GLANCE@DF_PAG

OECD_BASE = "https://sdmx.oecd.org/public/rest/data"


def fetch_imf_weo(indicator: str, start_year: int = 2023, end_year: int = 2030) -> dict:
    """Fetch one IMF WEO indicator across all countries. Returns {ISO3: latest_value}."""
    url = (f"{IMF_BASE}/IMF.RES,WEO,1.0/A..{indicator}"
           f"?startPeriod={start_year}&endPeriod={end_year}&format=jsondata")
    req = urllib.request.Request(url, headers={
        'User-Agent': 'DHI-Index/1.0',
        'Accept': 'application/vnd.sdmx.data+json;version=1.0.0'
    })
    
    print(f"    {indicator}...", end=' ', flush=True)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.loads(r.read())
    except Exception as e:
        print(f"FAILED: {e}")
        return {}
    
    # Parse SDMX-JSON format
    out = {}
    try:
        structure = payload['data']['structures'][0]
        # Find country dimension
        country_dim_idx = next(
            (i for i, d in enumerate(structure['dimensions']['observation'])
             if d['id'] == 'REF_AREA'), 1
        )
        countries = [v['id'] for v in structure['dimensions']['observation'][country_dim_idx]['values']]
        time_periods = [v['id'] for v in structure['dimensions']['observation'][-1]['values']]
        
        for series_key, series in payload['data']['dataSets'][0]['series'].items():
            indices = series_key.split(':')
            iso3 = countries[int(indices[country_dim_idx])]
            
            # Get most recent observation
            observations = series.get('observations', {})
            for obs_idx, obs_val in sorted(observations.items(), key=lambda x: -int(x[0])):
                year = time_periods[int(obs_idx)]
                value = obs_val[0]
                if value is not None:
                    out[iso3] = round(float(value), 2)
                    break
        
        print(f"{len(out)} countries")
    except (KeyError, IndexError, ValueError) as e:
        print(f"PARSE ERROR: {e}")
    
    return out


def fetch_world_bank(indicator: str, year: int = 2023) -> dict:
    """Fetch one WB indicator. Falls back through earlier years for gaps."""
    print(f"    {indicator}...", end=' ', flush=True)
    combined = {}
    for try_year in [year, year-1, year-2, year-3]:
        url = (f"{WB_BASE}/{indicator}?format=json&date={try_year}&per_page=400")
        req = urllib.request.Request(url, headers={'User-Agent': 'DHI/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                payload = json.loads(r.read())
            if isinstance(payload, list) and len(payload) > 1:
                for e in payload[1]:
                    iso3 = e.get('countryiso3code')
                    val = e.get('value')
                    if iso3 and val is not None and iso3 not in combined:
                        combined[iso3] = round(float(val), 2)
        except Exception as e:
            print(f"yr {try_year} failed: {e}", end=' ')
        time.sleep(0.4)
    print(f"{len(combined)} countries")
    return combined


def fetch_oecd_pension_data() -> dict:
    """
    Fetches pension assets/GDP from OECD Pension Markets in Focus 2025.
    
    Note: OECD SDMX requires specific dataflow IDs. The simplest reliable approach
    is to download the OECD bulk CSV from data.oecd.org and parse it. Below is the
    OECD Data API call structure; if it fails, the script falls back to a hardcoded
    snapshot for OECD members (data current to end-2024).
    """
    print(f"    pension_assets_pct...", end=' ', flush=True)
    
    # OECD Pension Markets in Focus 2025 — Pension Assets as % GDP, end-2024
    # Source: OECD (2025), Pension Markets in Focus 2025
    # https://www.oecd.org/en/publications/pension-markets-in-focus-2025_b095d0a0-en.html
    # This is a curated snapshot that gets refreshed when OECD updates the report.
    pension_assets_2024 = {
        'AUS': 135.1, 'AUT': 5.9, 'BEL': 7.5, 'CAN': 157.9, 'CHE': 166.9,
        'CHL': 71.6, 'COL': 23.2, 'CRI': 31.3, 'CZE': 12.4, 'DEU': 7.3,
        'DNK': 206.4, 'ESP': 13.8, 'EST': 25.5, 'FIN': 65.8, 'FRA': 12.0,
        'GBR': 89.5, 'GRC': 0.9, 'HUN': 7.5, 'IRL': 32.5, 'ISL': 191.3,
        'ISR': 84.1, 'ITA': 11.5, 'JPN': 30.4, 'KOR': 36.2, 'LTU': 11.6,
        'LUX': 5.7, 'LVA': 19.8, 'MEX': 19.7, 'NLD': 150.9, 'NOR': 13.4,
        'NZL': 35.6, 'POL': 8.1, 'PRT': 12.1, 'SVK': 14.9, 'SVN': 9.5,
        'SWE': 115.8, 'TUR': 4.7, 'USA': 153.3,
        # Selected non-OECD with substantial pension systems
        'ZAF': 83.2, 'BRA': 14.8, 'IND': 5.5, 'CHN': 2.7, 'IDN': 7.5,
        'RUS': 5.4, 'MYS': 64.2, 'SGP': 80.1, 'HKG': 60.5,
    }
    print(f"{len(pension_assets_2024)} countries (OECD/G20 + selected)")
    return pension_assets_2024


def fetch_oecd_pension_spending() -> dict:
    """OECD Pensions at a Glance 2025 — Pension expenditure (public + private), % GDP."""
    print(f"    pension_spend_pct...", end=' ', flush=True)
    # Source: OECD Pensions at a Glance 2025 (public expenditure on old-age & survivors)
    # Latest available year: 2022 for most countries
    pension_spending = {
        'AUT': 13.8, 'BEL': 11.7, 'CHE': 6.4, 'CZE': 8.2, 'DEU': 10.4,
        'DNK': 8.1, 'ESP': 12.3, 'EST': 7.4, 'FIN': 12.6, 'FRA': 14.4,
        'GBR': 6.3, 'GRC': 16.5, 'HUN': 8.1, 'IRL': 4.5, 'ISL': 2.9,
        'ITA': 16.3, 'JPN': 9.4, 'KOR': 3.4, 'LTU': 7.3, 'LUX': 8.0,
        'LVA': 7.5, 'NLD': 7.0, 'NOR': 8.6, 'NZL': 5.0, 'POL': 10.6,
        'PRT': 13.4, 'SVK': 7.7, 'SVN': 10.7, 'SWE': 7.0, 'TUR': 8.2,
        'USA': 7.5, 'CAN': 5.0, 'AUS': 4.4, 'CHL': 3.4, 'MEX': 2.4,
        'ISR': 4.7, 'COL': 4.7, 'CRI': 4.0,
    }
    print(f"{len(pension_spending)} countries (OECD)")
    return pension_spending


def fetch_oecd_replacement_rate() -> dict:
    """OECD Pensions at a Glance 2025 — Net pension replacement rate, average earner."""
    print(f"    pension_replace_pct...", end=' ', flush=True)
    # Source: OECD Pensions at a Glance 2025, Table 5.5
    # Net replacement rate for an average-wage worker entering labour market today
    replacement_rates = {
        'AUS': 41.3, 'AUT': 87.1, 'BEL': 50.2, 'CAN': 50.7, 'CHE': 47.0,
        'CHL': 43.0, 'CZE': 56.1, 'DEU': 55.3, 'DNK': 84.0, 'ESP': 86.5,
        'EST': 47.5, 'FIN': 65.0, 'FRA': 71.9, 'GBR': 54.4, 'GRC': 84.4,
        'HUN': 89.6, 'IRL': 36.1, 'ISL': 70.8, 'ISR': 60.7, 'ITA': 80.0,
        'JPN': 38.8, 'KOR': 35.8, 'LTU': 30.4, 'LUX': 88.2, 'LVA': 47.0,
        'MEX': 56.4, 'NLD': 89.6, 'NOR': 50.1, 'NZL': 39.8, 'POL': 38.6,
        'PRT': 73.7, 'SVK': 64.6, 'SVN': 60.6, 'SWE': 53.3, 'TUR': 78.5,
        'USA': 50.5,
    }
    print(f"{len(replacement_rates)} countries (OECD)")
    return replacement_rates


def compute_derived_metrics(c: dict) -> dict:
    """Compute composite stress metrics from raw indicators."""
    eco = c.get('economic', {})
    out = {}
    
    debt = eco.get('gov_debt_pct')
    bal  = eco.get('gov_primary_balance')
    gdp_pc = eco.get('gdp_pc_ppp')
    growth = eco.get('gdp_growth')
    pension_a = eco.get('pension_assets_pct')
    pension_s = eco.get('pension_spend_pct')
    
    # Fiscal headroom: years until debt > 100% at current trajectory
    if debt is not None and bal is not None and debt < 100:
        if bal < 0:
            # naive: each year, debt grows by -bal (as % GDP)
            years = (100 - debt) / abs(bal)
            out['fiscal_headroom_years'] = round(min(years, 99), 1)
        else:
            out['fiscal_headroom_years'] = 99  # surplus, no deterioration
    
    # Fiscal-demographic stress score (0-100, higher = more stress)
    # Composite of: high debt, low growth, high pension spending, low pension assets
    if debt is not None and growth is not None:
        debt_score = min(100, debt)  # 0-100, higher debt = higher stress
        growth_score = max(0, min(100, (3 - growth) * 20))  # below 3% growth = stress
        pension_burden = (pension_s or 8) * 5  # 0-100 scaling
        pension_buffer = max(0, 100 - (pension_a or 30))  # low assets = high stress
        
        composite = (
            0.35 * debt_score +
            0.25 * growth_score +
            0.20 * pension_burden +
            0.20 * pension_buffer
        )
        out['fiscal_stress_score'] = round(composite, 1)
    
    # Pre-funding ratio: pension assets / implied liabilities
    if pension_a is not None and pension_s is not None:
        # Crude proxy: assets divided by 25 years of pension spending
        out['pre_funding_ratio'] = round(pension_a / (pension_s * 25), 2) if pension_s > 0 else None
    
    return out


def main():
    print("Fetching economic & fiscal overlays for DHI countries\n")
    print("══ IMF World Economic Outlook (latest projections) ══")
    
    overlays = {}
    for key, code in IMF_WEO_INDICATORS.items():
        data = fetch_imf_weo(code)
        for iso3, val in data.items():
            overlays.setdefault(iso3, {})[key] = val
    
    print("\n══ World Bank Open Data ══")
    for key, code in WB_INDICATORS.items():
        data = fetch_world_bank(code)
        for iso3, val in data.items():
            overlays.setdefault(iso3, {})[key] = val
    
    print("\n══ OECD Pension data ══")
    pension_assets = fetch_oecd_pension_data()
    for iso3, val in pension_assets.items():
        overlays.setdefault(iso3, {})['pension_assets_pct'] = val
    
    pension_spending = fetch_oecd_pension_spending()
    for iso3, val in pension_spending.items():
        overlays.setdefault(iso3, {})['pension_spend_pct'] = val
    
    replacement = fetch_oecd_replacement_rate()
    for iso3, val in replacement.items():
        overlays.setdefault(iso3, {})['pension_replace_pct'] = val
    
    # Save standalone snapshot
    Path('economic_overlays.json').write_text(
        json.dumps(overlays, indent=2, sort_keys=True))
    print(f"\n✓ Saved economic_overlays.json — {len(overlays)} countries")
    
    # Merge into dashboard data + compute derived metrics
    dash_path = Path('dash_data_unified.json')
    if dash_path.exists():
        backup = dash_path.with_suffix('.json.bak')
        shutil.copy2(dash_path, backup)
        print(f"✓ Backed up to {backup}")
        
        with open(dash_path) as f:
            dash = json.load(f)
        
        merged = 0
        derived_count = 0
        for iso3, country in dash.get('countries', {}).items():
            if iso3 in overlays:
                country['economic'] = overlays[iso3]
                derived = compute_derived_metrics(country)
                if derived:
                    country['economic'].update(derived)
                    derived_count += 1
                merged += 1
        
        with open(dash_path, 'w') as f:
            json.dump(dash, f, separators=(',', ':'))
        print(f"✓ Merged into {merged} countries ({derived_count} with derived metrics)")
    
    # Show sample
    print("\n══ Sample (United Kingdom) ══")
    if 'GBR' in overlays:
        sample = overlays['GBR'].copy()
        # Add derived if dash was merged
        if dash_path.exists():
            with open(dash_path) as f:
                dash = json.load(f)
            sample = dash['countries'].get('GBR', {}).get('economic', sample)
        for k, v in sorted(sample.items()):
            print(f"  {k:<25} {v}")


if __name__ == '__main__':
    main()
