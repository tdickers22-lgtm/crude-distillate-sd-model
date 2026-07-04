# US Crude Oil & Distillate — S/D Balance Model

One Jupyter notebook (`crude_distillate_sd_model.ipynb`) that pulls weekly EIA data,
builds a supply/demand balance sheet for US crude and distillate, measures inventories
against the 5-year seasonal norm, projects 12 weeks forward, runs what-if scenarios,
**backtests the deviation signal against 10 years of prices, tracks the PADD 1 / PADD 3
regional story, draws a PADD choropleth map,** and writes a one-page market-view PDF.

## Quick start

1. Install dependencies: `pip install pandas numpy matplotlib requests reportlab pillow plotly jupyter`
   (optional, for embedding the PADD map PNG in the PDF: a compatible `plotly` + `kaleido` pair)
2. Get a free EIA API key (instant): https://www.eia.gov/opendata
3. Open the notebook, paste the key into `EIA_API_KEY` in the config cell
   (or put `EIA_API_KEY=...` in a gitignored `.env`), and **Run All**.
4. First live run: `python3 test_eia_key.py` checks all **18 series IDs** and names
   any that fail — the 7 extension IDs (PADD stocks + prices) are best guesses
   until verified (see the **VERIFY LOCALLY** block in the notebook and `DECISIONS.md` #13).

Without a key the notebook still runs end-to-end on a bundled synthetic sample dataset
(calibrated to realistic market levels, including the late-June-2026 prints). Every
chart, the banner, the backtest summary and the PDF are stamped "sample data" so nothing
synthetic can be mistaken for real.

## Data modes

| Mode   | When                                                | Marker                        |
|--------|-----------------------------------------------------|-------------------------------|
| LIVE   | key set and API reachable                           | none                          |
| CACHED | key previously used; `data/eia_live_cache.csv` exists | banner note                 |
| SAMPLE | no key                                              | banner + stamp on every output |

A failing **core** series on a live pull trips the tier fallback; a failing
**extension** series (regional / price) prints the exact `PET.*.W` identifier and is
skipped — the dependent sections switch off gracefully instead of crashing. Old
11-series caches are detected and reported the same way.

## What's inside

- **Phase 1** — 18-series framework table, data QA (incl. PADD-additivity check), inventory/supply charts with 5-yr average + range overlay
- **Phase 2** — the balance sheet: implied vs actual weekly stock change, adjustment (reconciliation) tracking
- **Phase 3** — surplus/deficit vs the 5-yr seasonal norm + snapshot table (the core signal)
- **Phase 4** — 12-week baseline projection + `run_scenario()` what-if tool
- **Phase 5** — written market view + auto-generated `weekly_market_view.pdf`
- **Extensions**
  - **Regional layer** — PADD 1 & PADD 3 distillate vs their own 5-yr bands (same seasonal
    functions as the national series), P1−P3 relative tightness (Colonial-arb proxy),
    one regional sentence in the market view + PDF
  - **Signal backtest** — WTI + NYH ULSD prices, diesel crack (= ULSD × 42 − WTI, $/bbl),
    deviation-% → forward price/crack changes at 4- and 8-week horizons with an explicit
    one-week WPSR publication lag, scatters + tercile tables, full-sample and ex-COVID
    cuts, a rolling-correlation stability chart, and an honest auto-written summary
    (also appended to `DECISIONS.md`) — a clean negative result is a valid outcome
  - **PADD map** — plotly choropleth of distillate deviation by PADD (red = tight),
    with a bar-chart fallback so Run All can never break on the map

## Series (18)

| Group | Bare code | Full v1 id used by the API layer | Unit | Role |
|---|---|---|---|---|
| Crude | `WCRFPUS2` | `PET.WCRFPUS2.W` | Mb/d | supply |
| Crude | `WCEIMUS2` | `PET.WCEIMUS2.W` | Mb/d | supply |
| Crude | `WCREXUS2` | `PET.WCREXUS2.W` | Mb/d | demand |
| Crude | `WCRRIUS2` | `PET.WCRRIUS2.W` | Mb/d | demand |
| Crude | `WCESTUS1` | `PET.WCESTUS1.W` | Mb | level (ex-SPR) |
| Crude | `W_EPC0_SAX_YCUOK_MBBL` | `PET.W_EPC0_SAX_YCUOK_MBBL.W` | Mb | level (Cushing sub-component) |
| Distillate | `WDIRPUS2` | `PET.WDIRPUS2.W` | Mb/d | supply |
| Distillate | `WDIIMUS2` | `PET.WDIIMUS2.W` | Mb/d | supply |
| Distillate | `WDIEXUS2` | `PET.WDIEXUS2.W` | Mb/d | demand |
| Distillate | `WDIUPUS2` | `PET.WDIUPUS2.W` | Mb/d | demand (proxy) |
| Distillate | `WDISTUS1` | `PET.WDISTUS1.W` | Mb | level |
| Regional* | `WDISTP11` | `PET.WDISTP11.W` | Mb | PADD 1 distillate (view layer) |
| Regional* | `WDISTP21` | `PET.WDISTP21.W` | Mb | PADD 2 distillate (view layer) |
| Regional* | `WDISTP31` | `PET.WDISTP31.W` | Mb | PADD 3 distillate (view layer) |
| Regional* | `WDISTP41` | `PET.WDISTP41.W` | Mb | PADD 4 distillate (view layer) |
| Regional* | `WDISTP51` | `PET.WDISTP51.W` | Mb | PADD 5 distillate (view layer) |
| Price* | `RWTC` | `PET.RWTC.W` | $/bbl | WTI Cushing spot |
| Price* | `EER_EPD2DXL0_PF4_Y35NY_DPG` | `PET.EER_EPD2DXL0_PF4_Y35NY_DPG.W` | $/gal | NYH ULSD spot |

\* extension series — **VERIFY LOCALLY** (built without API access; IDs are best
guesses; failures degrade gracefully). PADD stocks are components of `WDISTUS1`
and are never added to the balance. Prices are never volumes: the ×7 Mb/d→Mb
conversion must never touch them; the crack's gal→bbl factor is ×42.

**Units:** `Mb` = **million** barrels and `Mb/d` = million barrels/day
throughout. EIA's API delivers these series in *thousand* barrels (`MBBL`), so
the fetch layer normalizes ÷1000 on the way in (`DECISIONS.md` #24); prices
are never scaled.

## Weekly workflow

EIA releases Wednesdays 10:30am ET → *Run All* → read the QA block → check the deviation
chart + snapshot table → check PADD 1 vs PADD 3 → skim the adjustment line → send the
fresh one-pager. The backtest and its DECISIONS.md block refresh automatically.

**Full 10-year backtest sample:** the 5-yr seasonal warm-up consumes the first five
years of history, so with the default `START_DATE = 2015` deviations begin in 2020.
Set `START_DATE = "2009-01-01"` before a live pull to give the backtest its full
10-year window.

## Files

```
crude_distillate_sd_model.ipynb   the model (self-contained; sample generator embedded)
weekly_market_view.pdf            one-page view from the latest run
data/sample_weekly_data.csv       bundled sample data (regenerated if deleted or outdated)
charts/*.png                      every chart from the latest run
test_eia_key.py                   standalone check of the key + all 18 series IDs
DECISIONS.md                      log of judgment calls + auto-updated backtest result block
```
