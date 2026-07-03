# US Crude Oil & Distillate — S/D Balance Model

One Jupyter notebook (`crude_distillate_sd_model.ipynb`) that pulls weekly EIA data,
builds a supply/demand balance sheet for US crude and distillate, measures inventories
against the 5-year seasonal norm, projects 12 weeks forward, runs what-if scenarios,
and writes a one-page market-view PDF.

## Quick start

1. Install dependencies: `pip install pandas numpy matplotlib requests reportlab pillow jupyter`
2. Get a free EIA API key (instant): https://www.eia.gov/opendata
3. Open the notebook, paste the key into `EIA_API_KEY` in the config cell
   (or `export EIA_API_KEY=...`), and **Run All**.

Without a key the notebook still runs end-to-end on a bundled synthetic sample dataset
(calibrated to realistic market levels, including the late-June-2026 prints). Every
chart, the banner, and the PDF are stamped "sample data" so nothing synthetic can be
mistaken for real.

## Data modes

| Mode   | When                                                | Marker                        |
|--------|-----------------------------------------------------|-------------------------------|
| LIVE   | key set and API reachable                           | none                          |
| CACHED | key previously used; `data/eia_live_cache.csv` exists | banner note                 |
| SAMPLE | no key                                              | banner + stamp on every output |

## What's inside (mapped to the project phases)

- **Phase 1** — 11-series framework table, data QA, four inventory/supply charts with 5-yr average + range overlay
- **Phase 2** — the balance sheet: implied vs actual weekly stock change, adjustment (reconciliation) tracking
- **Phase 3** — surplus/deficit vs the 5-yr seasonal norm + snapshot table (the core signal)
- **Phase 4** — 12-week baseline projection + `run_scenario()` what-if tool (including the spec's runs −5% × 4-week example)
- **Phase 5** — written market view + auto-generated `weekly_market_view.pdf`

## Weekly workflow

EIA releases Wednesdays 10:30am ET → *Run All* → read the QA block → check the deviation
chart + snapshot table → skim the adjustment line → send the fresh one-pager.

## Files

```
crude_distillate_sd_model.ipynb   the model (self-contained; sample generator embedded)
weekly_market_view.pdf            one-page view from the latest run
data/sample_weekly_data.csv       bundled sample data (regenerated if deleted)
charts/*.png                      every chart from the latest run
DECISIONS.md                      log of judgment calls made during the build
```

Series IDs used — crude: `WCRFPUS2`, `WCEIMUS2`, `WCREXUS2`, `WCRRIUS2`, `WCESTUS1`,
`W_EPC0_SAX_YCUOK_MBBL` · distillate: `WDIRPUS2`, `WDIIMUS2`, `WDIEXUS2`, `WDIUPUS2`,
`WDISTUS1`. The distillate production and export IDs are the corrected ones, so a live
pull replaces the two series previously flagged for re-pull.
