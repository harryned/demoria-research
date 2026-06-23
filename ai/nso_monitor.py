"""
NSO births monitor — the hard, manual part of the Birth & Fertility Tracker,
automated to a first-pass-with-human-check.

For each configured national statistical office release page, it fetches the
page, has Claude extract the latest published monthly (or cumulative) birth
figure and the prior-year comparison as STRUCTURED output, flags anomalies, and
drafts a "recent updates" feed entry in the tracker's own shape. A human still
signs off before anything goes live — extraction from messy, multilingual gov
pages is good but not infallible.

Usage:
  export ANTHROPIC_API_KEY=...
  python3 nso_monitor.py --url "https://kostat.go.kr/..." --country "South Korea"
  python3 nso_monitor.py                 # sweep the SOURCES list below
  python3 nso_monitor.py --json out.json # also write structured results

The SOURCES URLs are examples and MUST be verified/maintained — statistical
offices move their release pages often. The value here is the pipeline.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import httpx
import anthropic
from pydantic import BaseModel, Field

import demoria_data as D

MODEL = "claude-opus-4-8"
ROOT = Path(__file__).resolve().parent.parent

# iso, country, release-page URL. Verified June 2026 (re-check periodically;
# statistical offices move their release pages). Fetchability noted: many gov
# sites are JS-rendered or bot-blocked, in which case a plain GET will fail and
# you pair this with a headless browser or a manual paste. The extraction step
# is the same either way. Ordered best-monthly-granularity first.
SOURCES = [
    ("KOR", "South Korea", "https://mods.go.kr/board.es?mid=a20108100000&bid=11773"),         # KOSTAT, monthly
    ("NLD", "Netherlands", "https://www.cbs.nl/en-gb/figures/detail/83474ENG"),                # CBS, monthly live births
    ("FRA", "France", "https://www.insee.fr/fr/statistiques/7944361"),                         # INSEE, monthly (French)
    ("SWE", "Sweden", "https://www.scb.se/en/finding-statistics/statistics-by-subject-area/population-and-living-conditions/population-composition-and-development/population-statistics/"),  # SCB, monthly
    ("GBR", "England & Wales", "https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths"),  # ONS, quarterly
    ("USA", "United States", "https://www.cdc.gov/nchs/nvss/vsrr/natality-dashboard.htm"),     # CDC NCHS (dashboard is JS; PDFs fetch)
    ("NOR", "Norway", "https://www.ssb.no/en/befolkning/fodte-og-dode/statistikk/fodte"),      # SSB
    ("DEU", "Germany", "https://www.destatis.de/EN/Themes/Society-Environment/Population/Births/_node.html"),  # Destatis
    ("CZE", "Czechia", "https://csu.gov.cz/births"),                                           # CZSO
    ("ITA", "Italy", "https://www.istat.it/en/statistical-themes/population/population-and-households/"),  # ISTAT
    ("ESP", "Spain", "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177007&menu=ultiDatos&idp=1254735573002"),  # INE
    ("POL", "Poland", "https://stat.gov.pl/en/topics/population/population/"),                  # GUS
    ("AUS", "Australia", "https://www.abs.gov.au/statistics/people/population/national-state-and-territory-population/latest-release"),  # ABS, quarterly
    ("JPN", "Japan", "https://www.e-stat.go.jp/en/statistics/00450011"),                        # e-Stat (JS-heavy hub)
    ("TWN", "Taiwan", "https://statis.moi.gov.tw/micst/webMain.aspx?k=menume"),                 # MOI (JS-heavy)
    ("SGP", "Singapore", "https://www.singstat.gov.sg/find-data/search-by-theme/population/births-and-fertility/latest-data"),  # SingStat (bot-blocked)
]

ANOMALY_PCT = 8.0  # |YoY %| at or above this is flagged for attention


class BirthsReading(BaseModel):
    found: bool = Field(description="True only if a concrete current-year birth count is on the page.")
    country: str = Field(description="Country the figure is for.")
    period_label: str = Field(description="Human label for the latest period, e.g. 'February 2026' or 'Jan-Feb 2026'.")
    figure_basis: str = Field(description="'single_month', 'cumulative', or 'annual'.")
    months_covered: int = Field(description="How many months the latest figure covers (1 for a single month, N for year-to-date, 12 for full year).")
    latest_year: int = Field(description="Calendar year of the latest period.")
    latest_births: int = Field(description="Births in the latest period (absolute count).")
    prior_year_same_period_births: int | None = Field(description="Births in the SAME period one year earlier, if the page gives it; else null.")
    yoy_pct: float | None = Field(description="Year-on-year percent change vs the same period last year, if computable; else null.")
    release_date: str = Field(description="The page's publication/update date if shown, else 'unknown'.")
    source_quote: str = Field(description="A short verbatim quote from the page that contains the figure.")
    confidence: str = Field(description="'high', 'medium', or 'low' — your confidence in the extraction.")
    notes: str = Field(description="Anything notable: a record high/low, a revision, sparse data, or why nothing was found.")


def fetch_text(url: str, timeout: float = 25.0) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (DemoriaResearch NSO monitor; +https://demoriaresearch.com)"}
    r = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    html = r.text
    html = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:30000]


def extract(country: str, url: str, page_text: str) -> BirthsReading:
    client = anthropic.Anthropic()
    prompt = (
        f"This is the text of a national statistics page for {country} ({url}).\n"
        "Find the MOST RECENT published current-year birth figure (a monthly count, a "
        "year-to-date cumulative count, or a full-year count), and the same-period figure "
        "one year earlier if the page provides it. Compute the year-on-year percent change "
        "only if you have both figures from the page. Do not infer or invent numbers that "
        "are not on the page; if there is no concrete current-year birth count, set found=false.\n\n"
        f"PAGE TEXT:\n{page_text}"
    )
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        output_format=BirthsReading,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.parsed_output


def to_feed_entry(iso: str, r: BirthsReading) -> dict:
    """Shape an entry like births_data.json's 'recent' feed."""
    kind = "annual" if r.figure_basis == "annual" else "monthly"
    return {
        "iso": iso,
        "name": D.country_name(iso) if D.DATA.get(iso) else r.country,
        "kind": kind,
        "chg": round(r.yoy_pct, 1) if r.yoy_pct is not None else None,
        "mon": r.months_covered if kind == "monthly" else None,
        "year": r.latest_year,
        "period": r.period_label,
        "source": url_of(iso),
    }


def url_of(iso: str) -> str:
    for s in SOURCES:
        if s[0] == iso:
            return s[2]
    return ""


def is_anomaly(r: BirthsReading) -> bool:
    if r.yoy_pct is not None and abs(r.yoy_pct) >= ANOMALY_PCT:
        return True
    return bool(re.search(r"record|highest|lowest|sharpest|biggest", (r.notes or ""), re.I))


def run_one(iso: str, country: str, url: str) -> dict:
    out = {"iso": iso, "country": country, "url": url}
    try:
        text = fetch_text(url)
    except Exception as e:
        out["status"] = "fetch_failed"
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    try:
        r = extract(country, url, text)
    except Exception as e:
        out["status"] = "extract_failed"
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    out["status"] = "ok"
    out["reading"] = r.model_dump()
    out["anomaly"] = is_anomaly(r)
    if r.found:
        out["feed_entry"] = to_feed_entry(iso, r)
    return out


def digest_line(res: dict) -> str:
    if res["status"] != "ok":
        return f"  ✗ {res['country']:<14} {res['status']}: {res.get('error','')[:60]}"
    r = res["reading"]
    if not r["found"]:
        return f"  · {res['country']:<14} no current-year figure found ({r['notes'][:50]})"
    flag = "  ⚑" if res["anomaly"] else "   "
    yoy = f"{r['yoy_pct']:+.1f}%" if r["yoy_pct"] is not None else "  n/a"
    return (f"{flag} {res['country']:<14} {r['period_label']:<14} "
            f"{r['latest_births']:>9,} births  {yoy} YoY  [{r['confidence']}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--country")
    ap.add_argument("--iso", default="")
    ap.add_argument("--json", help="write structured results to this path")
    args = ap.parse_args()

    if args.url:
        iso = args.iso or (D.resolve_country(args.country) if args.country else "") or "???"
        jobs = [(iso, args.country or iso, args.url)]
    else:
        jobs = SOURCES

    results = []
    print("Demoria NSO births monitor\n" + "=" * 60, file=sys.stderr)
    for iso, country, url in jobs:
        res = run_one(iso, country, url)
        results.append(res)
        print(digest_line(res), file=sys.stderr)

    anomalies = [r for r in results if r.get("anomaly")]
    feed = [r["feed_entry"] for r in results if r.get("feed_entry")]
    print("\n" + "=" * 60, file=sys.stderr)
    print(f"{len(feed)} figures extracted, {len(anomalies)} flagged for attention.", file=sys.stderr)
    if feed:
        print("\nDraft 'recent updates' feed (review before publishing):", file=sys.stderr)
        print(json.dumps(feed, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2))
        print(f"\nWrote {args.json}", file=sys.stderr)


if __name__ == "__main__":
    main()
