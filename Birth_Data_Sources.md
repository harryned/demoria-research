# Birth Tracker — where to get monthly births, by country

Frequency key: **M** monthly · **Q** quarterly · **A** annual (one figure/year).
Lag = roughly how long after a month/period ends before it's published.
Fill the matching cells in `Birth_Tracker_Input.xlsx`, then run `python3 _births_from_sheet.py --write`.

> Tip: for the EU/EEA, **Eurostat `demo_fmonth`** ("Live births by month") is one table for ~35 countries and the `_births_pipeline.py` script already pulls it automatically. Use the national sources below when you want the freshest figure (NSOs publish 1–2 months ahead of Eurostat) or for non-EU countries.

---

## East Asia  *(the fastest, most important reporters)*

| Country | Source | Freq | Where | Lag |
|---|---|---|---|---|
| **South Korea** | KOSIS — Statistics Korea | M | kosis.kr → table **DT_1B8000G** "Live births" (the page you sent). Free OpenAPI key at kosis.kr → OpenAPI | ~5 wk |
| **Japan** | e-Stat / MHLW Vital Statistics (monthly, 人口動態統計月報) | M | e-stat.go.jp → "Vital Statistics" → Monthly. Also mhlw.go.jp/toukei/saikin/hw/jinkou/ | ~2 mo |
| **Taiwan** | MOI Dept. of Household Registration | M | ris.gov.tw → 統計 (Statistics) → 出生 (births), monthly | ~2 wk (fastest in the world) |
| **Hong Kong** | C&SD | Q | censtatd.gov.hk → Births & deaths (quarterly) | ~1 qtr |
| **Macao** | DSEC | Q/M | dsec.gov.mo → Demographic statistics | ~1 qtr |
| **China** | NBS (National Bureau of Statistics) | A | stats.gov.cn → annual communiqué (released ~mid-Jan for prior year). Annual only | ~1 yr |
| **Mongolia** | NSO | M | 1212.mn (NSO data portal) → population/births | ~1 mo |

## Southeast Asia

| Country | Source | Freq | Where | Lag |
|---|---|---|---|---|
| **Singapore** | Dept. of Statistics / ICA | M/A | singstat.gov.sg → Births & Fertility; monthly live births in "Monthly Digest of Statistics" | ~1 mo |
| **Thailand** | DOPA, Bureau of Registration Admin. | M | stat.bora.dopa.go.th — registered births by month (very timely) | ~1 mo |
| **Malaysia** | DOSM | Q | dosm.gov.my → Vital Statistics (quarterly) | ~1 qtr |
| **Philippines** | PSA | A (M registry lag) | psa.gov.ph → Vital Statistics | slow |
| **Vietnam** | GSO | A | gso.gov.vn | ~1 yr |

## South & Central Asia

| Country | Source | Freq | Where |
|---|---|---|---|
| **India** | Civil Registration System / SRS | A | censusindia.gov.in (SRS); CRS reports — annual, slow |
| **Kazakhstan** | Bureau of National Statistics | M | stat.gov.kz → demography (monthly) |
| **Uzbekistan / Kyrgyzstan / Tajikistan** | National stat committees | M/Q | stat.uz · stat.kg · stat.tj |
| **Iran** | National Organization for Civil Registration (NOCR) | M/Q | sabteahval.ir (Persian) — registered births |
| **Sri Lanka / Bangladesh** | Dept. of Census & Statistics | A | statistics.gov.lk · bbs.gov.bd |

## Western & Northern Europe

| Country | Source | Freq | Where |
|---|---|---|---|
| **UK — England & Wales** | ONS | A (provisional Q) | ons.gov.uk → Births. Monthly *occurrences* limited; annual + quarterly provisional |
| **UK — Scotland** | National Records of Scotland | Q/M | nrscotland.gov.uk → Vital Events (quarterly + monthly) |
| **UK — N. Ireland** | NISRA | Q | nisra.gov.uk |
| **Ireland** | CSO | Q | cso.ie → Vital Statistics (quarterly) |
| **France** | INSEE | M | insee.fr → série "Naissances" mensuelles (very timely) |
| **Germany** | Destatis | M | destatis.de → Geburten (monthly, GENESIS table 12612) |
| **Italy** | ISTAT | M | istat.it / dati.istat.it → Iscritti in anagrafe per nascita (monthly) |
| **Spain** | INE | M | ine.es → Estadística de Nacimientos / Movimiento Natural (monthly) |
| **Netherlands** | CBS | M | opendata.cbs.nl → StatLine "Births; key figures" (monthly, table 37943eng) |
| **Belgium** | Statbel | A/Q | statbel.fgov.be |
| **Switzerland** | FSO (BFS) | M/Q | bfs.admin.ch → Population → Births |
| **Austria** | Statistik Austria | M | statistik.at → Geburten |
| **Portugal** | INE | M | ine.pt → Nados-vivos (monthly) |
| **Greece** | ELSTAT | M/A | statistics.gr |
| **Sweden** | SCB | M | scb.se → Befolkningsstatistik (monthly) — PxWeb API |
| **Norway** | SSB | M/Q | ssb.no → Fødte (table 01222 / quarterly) — PxWeb API |
| **Denmark** | Statistics Denmark | M/Q | dst.dk → StatBank table FOD407 / FODIE — API |
| **Finland** | Tilastokeskus | M | stat.fi / StatFin → "Births" monthly — PxWeb API |
| **Iceland** | Statistics Iceland | M/Q | statice.is |
| **Luxembourg / Cyprus / Malta** | STATEC · CYSTAT · NSO | Q/A | statistiques.lu · cystat.gov.cy · nso.gov.mt |

## Central & Eastern Europe  *(most via Eurostat demo_fmonth)*

| Country | Source | Freq | Where |
|---|---|---|---|
| **Poland** | GUS | M | stat.gov.pl → Demografia (monthly) |
| **Czechia** | CZSO | M | czso.cz → Obyvatelstvo (monthly) |
| **Hungary** | KSH | M | ksh.hu → Népmozgalom (monthly) |
| **Romania** | INSSE | M | insse.ro |
| **Bulgaria / Croatia / Serbia / Slovakia / Slovenia / Baltics** | National stat offices | M/Q | nsi.bg · dzs.hr · stat.gov.rs · statistics.sk · stat.si · stat.gov.lv etc. (all in Eurostat) |
| **Ukraine** | State Statistics Service (wartime: @_Kinez_ on X) | M | ukrstat.gov.ua (limited); cross-check @_Kinez_ |
| **Russia** | Rosstat | M | rosstat.gov.ru → ЕМИСС (monthly естественное движение) |
| **Belarus** | Belstat | Q | belstat.gov.by |

## North America

| Country | Source | Freq | Where |
|---|---|---|---|
| **United States** | CDC / NCHS | M (provisional) | cdc.gov/nchs → Vital Statistics Rapid Release (provisional monthly births); also wonder.cdc.gov |
| **Canada** | Statistics Canada | A/Q | statcan.gc.ca → table 13-10-0415 (births); Quebec ISQ publishes faster (stat.gouv.qc.ca) |

## Latin America & Caribbean

| Country | Source | Freq | Where |
|---|---|---|---|
| **Mexico** | INEGI | A (M registry) | inegi.org.mx → Natalidad |
| **Brazil** | Registro Civil / IBGE | M/Q | sidra.ibge.gov.br → Estatísticas do Registro Civil (monthly registered) |
| **Chile** | INE / Registro Civil | M | ine.gob.cl → Estadísticas Vitales |
| **Argentina** | DEIS / INDEC | A | argentina.gob.ar/salud/deis |
| **Colombia** | DANE | M/Q | dane.gov.co → Estadísticas Vitales (EEVV) |
| **Costa Rica / Peru / Ecuador** | INEC | M/A | inec.cr · inei.gob.pe · ecuadorencifras.gob.ec |
| **Puerto Rico** | Dept. of Health / CDC | M | salud.pr.gov; CDC NCHS |

## Caucasus & Türkiye

| Country | Source | Freq | Where |
|---|---|---|---|
| **Türkiye** | TÜİK | A (M registry) | tuik.gov.tr → Doğum İstatistikleri |
| **Georgia** | GeoStat | M/Q | geostat.ge |
| **Armenia** | ArmStat | M/Q | armstat.am |
| **Azerbaijan** | SSC | M/Q | stat.gov.az |

## Middle East & North Africa · Gulf

| Country | Source | Freq | Where |
|---|---|---|---|
| **Israel** | CBS | M/Q | cbs.gov.il → Live births (monthly) |
| **Saudi Arabia** | GASTAT | A | stats.gov.sa → Births & Deaths Bulletin (nationals split) |
| **UAE** | FCSC | A | fcsc.gov.ae (Emirati nationals via GLMM) |
| **Qatar / Kuwait / Bahrain / Oman** | PSA · CSB · IGA · NCSI | A/Q | psa.gov.qa · csb.gov.kw · data.gov.bh · ncsi.gov.om |
| **Egypt** | CAPMAS | A/Q | capmas.gov.eg |
| **Algeria / Tunisia / Jordan / Iraq** | ONS · INS · DOS · CSO | A | ons.dz · ins.tn · dos.gov.jo |

## Oceania

| Country | Source | Freq | Where |
|---|---|---|---|
| **Australia** | ABS | Q/A | abs.gov.au → Births, Australia (annual) + quarterly population |
| **New Zealand** | Stats NZ | Q | stats.govt.nz → Births and deaths (quarterly, very timely) |

---

### Suggested starter set (fast, reliable, biggest stories)
Taiwan · South Korea · Japan · Hong Kong · Singapore · Thailand · USA (CDC) · France · Germany · Italy · Spain · Netherlands · Sweden · Norway · Denmark · Finland · Poland · England&Wales · Scotland · New Zealand · Israel · Chile · Brazil

These 20-odd cover most of the world's population-weighted fertility news and publish within ~1–2 months. Everything else can fill in over time.
