# US Crude Oil & Distillate — S/D Balance Model

One Jupyter notebook (`crude_distillate_sd_model.ipynb`) that pulls weekly EIA data,
builds a supply/demand balance sheet for US crude and distillate, measures inventories
against the 5-year seasonal norm, projects 12 weeks forward, runs what-if scenarios,
**backtests the deviation signal against 10 years of prices, tracks the PADD 1 / PADD 3
regional story, draws a PADD choropleth map,** and writes a one-page market-view PDF.

## Quick start

1. Install dependencies: `pip install pandas numpy matplotlib requests reportlab pillow "plotly>=6.1.1" kaleido yfinance jupyter`
   (`yfinance` powers the live futures curve; `plotly>=6.1.1` paired with `kaleido` is what makes the PADD-map PNG embed in the PDF — an older plotly 5 + kaleido 1.x pair silently skips the PNG)
2. Get a free EIA API key (instant): https://www.eia.gov/opendata
3. Open the notebook, paste the key into `EIA_API_KEY` in the config cell
   (or put `EIA_API_KEY=...` in a gitignored `.env`), and **Run All**.
4. First live run: `python3 test_eia_key.py` checks all **22 series IDs** and names
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
  - **Predictive Lab** — signal×target matrix (incl. M1−M2 spread targets from the
    futures layer), curve-vs-fundamentals divergence gauge, kNN analog playbook with
    a walk-forward skill check, walk-forward validation of the inventory projection
    vs a seasonal baseline, and one ex-ante composite rule with weekly-mark P&L —
    all publication-lag- and lookahead-clean (`DECISIONS.md` #26-28)

## Series (22)

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
| Price* | `RCLC1` | `PET.RCLC1.W` | $/bbl | WTI futures M1 |
| Price* | `RCLC2` | `PET.RCLC2.W` | $/bbl | WTI futures M2 |
| Price* | `EER_EPD2F_PE1_Y35NY_DPG` | `PET.EER_EPD2F_PE1_Y35NY_DPG.W` | $/gal | NYH HO/ULSD futures M1 |
| Price* | `EER_EPD2F_PE2_Y35NY_DPG` | `PET.EER_EPD2F_PE2_Y35NY_DPG.W` | $/gal | NYH HO/ULSD futures M2 |

\* extension series — **VERIFY LOCALLY** (built without API access; IDs are best
guesses; failures degrade gracefully). PADD stocks are components of `WDISTUS1`
and are never added to the balance. Prices are never volumes: the ×7 Mb/d→Mb
conversion must never touch them; the crack's gal→bbl factor is ×42.

> **Live futures curve.** EIA discontinued the four NYMEX futures series
> (`RCLC1/2`, HO `M1/M2`) in Apr-2024, so they freeze there in a live pull. The
> data layer now refreshes them from **Yahoo Finance** (`CL=F`/`HO=F` continuous
> fronts for M1 across the whole gap, plus the current front-two contracts for the
> live M1−M2 term structure), so the structure layer, divergence gauge and market
> view stay current. It's fully optional: without `yfinance` or a network the
> columns stay as EIA left them and every dependent section degrades as before.
> The deep 2024-25 spread *history* isn't free to rebuild (the source drops expired
> contracts), so the spread backtest still runs on EIA's real pre-2024 history.

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
