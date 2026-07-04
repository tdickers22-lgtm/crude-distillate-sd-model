# Crude & Distillate — Backtest Report (2026-07-04)

- **DATA MODE: LIVE (EIA API)   |   2283 weeks   |   1982-08-20 -> 2026-06-26**
- QA: PASS -- all checks clean
- notebook cell errors: 0
- live volume normalization: 16 series scaled thousand→million bbl ✓
- alignment check PASS  |  usable overlapping weeks (study a, h=4): 517   signals 2016-07-01 -> 2026-05-22 (each with a complete 4-wk forward window)

## Auto-written summary

Signals 2016-07-01 -> 2026-06-26, of which 517 have a complete 4-wk forward window (last usable: 2026-05-22); signal lagged 1 wk for WPSR publication: study (a) distillate %-deviation vs forward diesel crack shows r = +0.02 (4w) / +0.01 (8w); the tightest tercile of weeks preceded avg +0.25 $/bbl 4-wk crack moves with a 52% hit rate, vs +0.55 $/bbl for the loosest tercile -- NOT SUPPORTED (2/6 directional checks). Study (b) crude %-deviation vs forward WTI shows r = +0.06 (4w) / +0.07 (8w) -- NOT SUPPORTED (0/6). Ex-COVID (windows overlapping Mar-20..Feb-21 removed, per horizon): study (a) same direction; study (b) same direction. Conservative t+2-entry check (4w): r = +0.02 (a) / +0.06 (b). Caveats: overlapping windows mean the effective sample is ~n/h (517//4 = 129 independent 4-wk moves), so treat correlations as descriptive, not as t-stats; the rolling-correlation chart shows the relationship is regime-dependent; and deviations only begin 5 yrs after START_DATE (set START_DATE=2009 locally for the full 10-yr window).

## Tercile tables

```
horizon                        4w                                              8w                               
                 avg move ($/bbl) hit rate median ($/bbl)      n avg move ($/bbl) hit rate median ($/bbl)      n
sample   bucket                                                                                                 
full     tight               0.25     0.52           0.42 172.00             0.89     0.53           0.54 171.00
         neutral             0.22      NaN           0.34 172.00            -0.25      NaN          -0.23 171.00
         loose               0.55     0.43           0.51 173.00             1.56     0.40           1.00 171.00
ex-COVID tight               0.45     0.51           0.41 154.00             1.72     0.55           1.14 151.00
         neutral            -0.28      NaN           0.29 152.00            -1.09      NaN          -0.53 150.00
         loose               1.04     0.43           0.44 154.00             2.02     0.43           0.87 151.00
```

```
horizon                        4w                                              8w                               
                 avg move ($/bbl) hit rate median ($/bbl)      n avg move ($/bbl) hit rate median ($/bbl)      n
sample   bucket                                                                                                 
full     tight              -0.10     0.45          -0.95 172.00             0.07     0.41          -2.60 171.00
         neutral            -0.48      NaN           0.66 172.00            -0.85      NaN           0.79 171.00
         loose               1.54     0.34           1.59 173.00             3.08     0.29           2.66 171.00
ex-COVID tight               0.01     0.46          -0.75 153.00             0.17     0.42          -2.64 151.00
         neutral             0.32      NaN           0.72 153.00             1.23      NaN           1.35 150.00
         loose               0.45     0.40           1.28 154.00             0.79     0.39           1.27 151.00
```

## Market view

```
US CRUDE & DISTILLATE -- WEEKLY S/D VIEW   (week ending 2026-06-26)

Commercial crude stocks are 408 Mb, 29 Mb (7%) below the 5-yr seasonal average and below the bottom of its 5-yr range. The last 4 weeks drew 25 Mb. The baseline projection has the deficit at 11 Mb by 2026-09-18 (narrowing).

Cushing sits at 19.7 Mb, below the bottom of its 5-yr range (-38% vs 5-yr avg) -- the WTI delivery point is critically thin.

Distillate stocks are 109 Mb, 9 Mb (7%) below the 5-yr average, in the bottom quartile of its 5-yr range. 4-wk change: +6 Mb. Baseline projection puts the gap at -1 Mb vs norm by 2026-09-18, i.e. converging toward normal ahead of the winter heating season.

PADD 1 distillate 23.0 Mb, 6.7 Mb (23%) below its 5-yr norm -- NY Harbor tight, constructive for ULSD cracks; P1-P3 relative tightness -20.0 pts implies incentive to ship product east (Colonial-arb pull).

Prices: WTI $73.59/bbl, NYH ULSD $3.189/gal, diesel crack $60.35/bbl (+0.58 $/bbl over 4 wks).

MODEL VIEW: crude TIGHT (supportive of flat price and backwardated WTI structure); distillate TIGHT (constructive for diesel cracks and HO spreads).

Backtest (10y cap, n=517): tight-tercile distillate weeks preceded avg +0.25 $/bbl 4-wk crack moves (r = +0.02, hit 52%) -- not supported.

Generated from live EIA weekly data.
```

## Artifacts

- `weekly_market_view.pdf` — the one-pager (opened automatically)
- `charts/backtest_dist_crack.png`, `charts/backtest_crude_wti.png` — scatters
- `charts/backtest_stability.png` — 3-yr rolling correlation
- `charts/padd1_distillate.png`, `charts/padd3_distillate.png` — regional bands
- `DECISIONS.md` — the auto-updated result block sits at the bottom
