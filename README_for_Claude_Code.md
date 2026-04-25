# Demographic Health Index (DHI) — Project Handover

## Project Overview
A full-stack demographic analytics tool covering 236 countries, 1965–2050.
Built with Python data pipeline → JSON data files → self-contained HTML tools.

## File Structure

### HTML Files (the product)
- `dhi_combined.html`     — Full tool (9MB, all three views in one file)
- `dhi_world_map.html`    — D3 choropleth map, standalone (4.8MB, fully self-contained)
- `dhi_dashboard.html`    — Index & Rankings dashboard, standalone (2MB)
- `dhi_landing.html`      — About & Methodology page, standalone (34KB)

### Key Data Files
- `scores_unified.pkl`    — THE master scored dataset. Single source of truth.
                            14,922 rows × 236 countries × 1965–2050.
                            Use this for everything. Never overwrite without backup.
- `DHI_updated.xlsx`      — Source Excel model with scoring weights and raw data

### Pipeline Pickles (rebuild chain)
wpp_gen_hist.pkl → raw_indicators_hist.pkl → scores_hist_final.pkl ↘
scores_df.pkl (from Excel) ──────────────────────────────────────────→ scores_unified.pkl
                                                                              ↓
                                              map_data_unified.json + dash_data_unified.json
                                                              ↓
                                              embedded in HTML files

## Index Structure & Weights
| Category | Code | Weight |
|----------|------|--------|
| Total Fertility Score     | TFS      | 32% |
| Momentum Score            | Momentum | 21% |
| Workforce Sustainability  | WSS      | 22% |
| Fertility Quality Score   | FQS      |  8% |
| Migration Independence    | MDS      | 17% |

## Classification System
| Classification          | Score Range | Colour     |
|-------------------------|-------------|------------|
| Demographically Healthy | 80–100      | Green      |
| Under Pressure          | 65–79       | Amber      |
| Serious Decline         | 50–64       | Orange     |
| Critical                | 35–49       | Red        |
| Complete Crisis         | 0–34        | Dark red   |

## Known Issues (as of handover)
1. World map sometimes blank — D3 scripts and topology are inlined. If blank,
   check browser console for errors in the IIFE near the topology data.
2. Methodology page scroll — fixed with overflow-y:auto on html/body, but
   verify by opening dhi_landing.html directly (not inside combined).
3. Autoplay — fixed, uses setYearFromSelect() for history years (1965–2015)
   and .click() for recent/projection year buttons.

## Score Validation (2024)
- Ukraine:    22.1  (rank 236/236) — Complete Crisis
- Uzbekistan: 90.9  (rank   1/236) — Demographically Healthy  
- Global avg: 61.6

## Data Sources
- UN WPP 2024: TFR, NRR, MAC, NatChange, Pop, NetMig (1950–2100)
- WPP 5yr age groups: WRR, OADR, Labour Force Growth (1950–2100)  
- ILO LFPR: 1990–2025 (held at 1990 for prior years)
- Bilateral migration stock: 1960–2000 (decadal, interpolated)
- UNDESA immigrant stock: 1999–2050

## Python Environment
- pandas, numpy, openpyxl, json, pickle
- No special packages needed beyond standard data science stack
