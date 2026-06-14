"""
Scrape Wikipedia vital-statistics tables for live births and deaths for the
22 user-flagged countries. Same source as the TFR scrape — these tables
typically have columns:
  Year | Population | Live births | Deaths | Natural increase | CBR | CDR | TFR | ...
We pull Births and Deaths in absolute numbers (NSO-style), then convert to
per-1000 rates using WPP population to keep the denominator consistent.
"""
import sys, json, time, re
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from bs4 import BeautifulSoup
from _country_meta import SLUG_OVERRIDE
from _wiki_tfr_scrape import (
    fetch as scrape_fetch, extract_refs, cell_text,
    parse_year_cell,
)

ISOS = ["ALB", "ARG", "ARM", "AUS", "AUT", "AZE", "BEL", "BGR", "BIH", "BLR", "BMU", "BRN", "CAN", "CHE", "CHL", "CHN", "COL", "CYP", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "GEO", "GRC", "GRL", "HKG", "HRV", "HUN", "IRL", "ISL", "ISR", "ITA", "JPN", "KAZ", "KGZ", "KOR", "LIE", "LTU", "LUX", "LVA", "MAC", "MCO", "MDA", "MKD", "MLT", "MNE", "MNG", "MYS", "NLD", "NOR", "NZL", "PHL", "POL", "PRT", "ROU", "RUS", "SGP", "SRB", "SVK", "SVN", "SWE", "THA", "TUR", "TWN", "UKR", "URY", "USA", "UZB", "VNM", "XKX"]
# (ARE, BIH, SUR are KEEP WPP — no need to scrape)

YEARS = set(range(2005, 2026))
country_list = json.loads(Path("_country_list.json").read_text())

def slug_for(iso, name):
    if iso in SLUG_OVERRIDE: return SLUG_OVERRIDE[iso]
    return f"Demographics_of_{name.replace(' ', '_').replace(',', '')}"

# Header-name heuristics — birth/death columns can be labelled various ways
def looks_like_births_header(h):
    h = (h or "").lower()
    return ("live birth" in h or h.strip() == "births" or "live births" in h
            or "no. births" in h or "no. of births" in h)
def looks_like_deaths_header(h):
    h = (h or "").lower()
    return (h.strip() == "deaths" or "no. deaths" in h or "no. of deaths" in h
            or "total deaths" in h)

NUM_RE = re.compile(r'[\d,]+\.?\d*')

def parse_count(cell_str):
    """Parse a count cell like '54,621' or '54621.0'."""
    if not cell_str: return None
    s = cell_str.replace(",","").replace(" ","").strip()
    m = NUM_RE.search(s)
    if not m: return None
    try:
        v = float(m.group(0).replace(",",""))
        return v
    except:
        return None

results = {}
for iso in ISOS:
    name = country_list.get(iso, iso)
    slug = slug_for(iso, name)
    html = scrape_fetch(slug)
    if not html:
        results[iso] = {"status":"fetch_failed", "rows":[]}
        continue
    soup = BeautifulSoup(html, "html.parser")
    # Find tables with both 'Live births' and 'Deaths' columns
    candidates = []
    for t_i, table in enumerate(soup.find_all("table")):
        rows = table.find_all("tr")
        if not rows: continue
        headers = [cell_text(th) for th in rows[0].find_all(["th","td"])]
        b_idx = d_idx = None
        for i, h in enumerate(headers):
            if b_idx is None and looks_like_births_header(h): b_idx = i
            if d_idx is None and looks_like_deaths_header(h): d_idx = i
        if b_idx is None or d_idx is None: continue
        these = []
        for tr in rows[1:]:
            cells = tr.find_all(["td","th"])
            if len(cells) != len(headers): continue
            yr = parse_year_cell(cell_text(cells[0]))
            if yr is None or yr not in YEARS: continue
            bv = parse_count(cell_text(cells[b_idx]))
            dv = parse_count(cell_text(cells[d_idx]))
            if bv is None and dv is None: continue
            these.append((yr, bv, dv))
        if these:
            candidates.append((len(these), t_i, these, headers))
    if not candidates:
        results[iso] = {"status":"no_births_deaths_table", "slug": slug, "rows":[]}
        print(f"  {iso} {name[:28]:<28} no table found")
        time.sleep(0.3); continue
    candidates.sort(key=lambda x: (-x[0], x[1]))
    n, t_i, rows_ext, headers = candidates[0]
    # Dedupe by year (take first occurrence — best table)
    seen = set(); kept = []
    for yr, bv, dv in sorted(rows_ext):
        if yr in seen: continue
        seen.add(yr); kept.append([yr, bv, dv])
    results[iso] = {"status":"ok","slug":slug,"rows":kept,"headers":headers}
    print(f"  {iso} {name[:28]:<28} {len(kept):2} rows  e.g. {kept[0]}")
    time.sleep(0.3)

Path("_nso_births_deaths.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"\nWrote _nso_births_deaths.json")
