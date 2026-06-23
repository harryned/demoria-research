# Demoria AI tools

Two prototypes that put an LLM **on top of** the Demoria dataset, never in place of it.
The governing rule: the model retrieves, reasons and writes prose; **every number comes
from the dataset, with provenance (NSO / DRE / WPP). It never invents a figure.**

Built on the Anthropic SDK. Default model: `claude-opus-4-8`.

## Setup

```bash
pip install anthropic httpx pydantic        # (anthropic pulls pydantic)
export ANTHROPIC_API_KEY=sk-ant-...
```

All three files live in `ai/` and read the repo's data files (`_data_export.json`,
`public/cliffs_data.json`, and the policy library in `_build_policies_page.py`).

## 1. `ask_demoria.py` — grounded natural-language Q&A

A question-answering layer over the whole database. The model answers in plain British
English but calls tools to fetch the actual numbers, and stamps each with its source tier.

```bash
python3 ask_demoria.py "Which countries have the lowest fertility in 2025?"
python3 ask_demoria.py "How far have Japan's annual births fallen from their peak?"
python3 ask_demoria.py "Compare Korea and Italy's working-age population in 2000 and 2050"
python3 ask_demoria.py "What has South Korea tried to lift its birth rate, and did it work?"
python3 ask_demoria.py                       # interactive REPL
python3 ask_demoria.py --model claude-sonnet-4-6 "..."   # cheaper, for high volume
```

Tools the model can call (all backed by `demoria_data.py`): resolve_country,
get_indicator_value, get_indicator_series, rank_countries, compare_countries,
get_cohort_cliff, search_pronatal_policies. Tool calls are printed to stderr so you can
see the model's working.

This is the engine to put behind an "Ask Demoria" box on the site (free public tier) and
behind a paid API. The same tool layer powers the dossier generator and policy advisor.

## 2. `nso_monitor.py` — births-tracker monitoring agent

Automates the hardest part of the Birth & Fertility Tracker: reading 200+ statistical
offices for the latest current-year births. For each configured release page it fetches
the page, has Claude extract the latest figure as **structured output** (a validated
Pydantic schema), flags anomalies, and drafts a "recent updates" feed entry in the
tracker's own shape. A human signs off before publishing.

```bash
python3 nso_monitor.py --url "https://<stat-office>/..." --country "South Korea"
python3 nso_monitor.py                        # sweep the SOURCES list
python3 nso_monitor.py --json out.json        # also write structured results
```

The `SOURCES` URLs in the file are **examples and must be maintained** — statistical
offices move their release pages, and many block automated fetches (you will see
`fetch_failed` / 403 on those). The value is the pipeline: fetch -> structured extract ->
anomaly flag -> feed entry. For blocked sources, pair this with a headless browser or a
manual paste; the extraction step is unchanged.

## 3. `demoria_data.py` — the grounded data layer

The single source of truth both tools query. Run it directly for a self-test:

```bash
python3 demoria_data.py
```

## Notes

- Numbers are only ever as good as the dataset. The tools surface provenance so a reader
  can see whether a figure is national (NSO), a Demoria correction (DRE), or the UN
  baseline (WPP).
- Cost: `ask_demoria` makes a few tool round-trips per question; `claude-opus-4-8` is the
  quality default, `claude-sonnet-4-6` is the high-volume option.
- These are backend tools, not part of the static site deploy.
