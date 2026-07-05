# Decision log — judgment calls made while building to spec

**1. Data source for this delivered run.** The build environment cannot reach
`api.eia.gov` (network allow-list) and no API key was available, so a live pull was
impossible here. Rather than ship untested plumbing, the notebook has a three-tier
data layer — live API → cached pull → bundled synthetic sample — and this delivered
run uses the sample tier. The sample is calibrated to realistic history (the shale
ramp, the 2020 COVID shock, post-2023 export growth) and its 2026 endpoint is aligned
to publicly reported late-June-2026 EIA prints (crude ≈409–412 Mb, ~7% below the
5-yr average; distillate ≈106–108 Mb, ~9–10% below; Cushing ≈19 Mb; refinery runs
≈16.6–17.1 Mb/d; production ≈13.7 Mb/d). Everything synthetic is stamped as such on the
banner, every chart, and the PDF. Paste a key and Run All to flip to live data —
the analytics are unchanged.

**2. Series ID selection.** The spec names series descriptively; the concrete EIA IDs
chosen are listed in the notebook's framework table and the README. Notably, crude
stocks = `WCESTUS1` (commercial, excluding SPR) per the SPR data-trap, and imports and
exports are kept gross on opposite sides of the balance rather than using net imports.

**3. "Demand" definitions.** Crude demand = refinery net crude inputs + exports.
Distillate demand = product supplied + exports, with product supplied explicitly
treated as a demand *proxy* (primary-storage disappearance, not metered consumption).

**4. History depth.** Spec says "10+ years": start = 2015-01-01, a single configurable
constant (`START_DATE`).

**5. Five-year average convention.** Trailing five calendar (ISO) years *excluding*
the current year, matched on ISO week, with week 53 folded into week 52 — matching
EIA's own five-year-average convention.

**6. Sample stocks construction.** Synthetic stock levels are anchored to a realistic
path, with weekly texture derived from the generated flows; the residual becomes a
slowly varying "adjustment" line (crude's persistently positive, ~+0.4 Mb/d recently,
as in real data) so the Phase-2 reconciliation check behaves like the real dataset
instead of being trivially zero.

**7. Projection method.** The spec says "using current trends." Implemented as: each
flow follows its 5-yr seasonal path plus the current 4-week deviation decaying at
0.85/week; the recent 8-week average adjustment is carried; the ~80% band grows with
√h using historical weekly stock-change surprise dispersion. Chosen over anything
fancier for transparency — every assumption is visible and defensible in an interview.

**8. Scenario tool form.** A plain function (`run_scenario`) rather than ipywidgets
sliders: it survives Run All, exports, and GitHub rendering, and it is scriptable.
Refinery-run shocks automatically propagate to distillate output through the observed
distillate yield (~30% of runs).

**9. Cushing's role.** Tracked as a level indicator only — it is a sub-component of
total commercial crude stocks, so adding it as a separate balance line would double
count. It gets its own chart and snapshot row because it is the WTI delivery point.

**10. Tight/loose thresholds.** ±4% versus the 5-yr average classifies
TIGHT / BALANCED / LOOSE. A stated heuristic, one line to change in `classify()`.

**11. Self-containment.** The entire model lives in one .ipynb (the sample generator
is embedded, not imported), so the single file travels; the CSV is a convenience
cache, not a dependency. The one-pager is generated *by the notebook itself*, so the
Phase-5 artifact refreshes automatically on every weekly run.

**12. Delivery format.** The spec's deliverable is a notebook plus a 1-page summary:
delivered as an *executed* .ipynb (all outputs visible without running anything), the
PDF one-pager, standalone PNGs of every chart, and this log — bundled in a zip.

---

## Extension build — regional layer, signal backtest, PADD map

**13. New series IDs — VERIFY LOCALLY.** The build environment could not reach
`api.eia.gov`, so all seven new IDs are best guesses pending a live check:
prices `PET.RWTC.W` ($/bbl) and `PET.EER_EPD2DXL0_PF4_Y35NY_DPG.W` ($/gal);
PADD distillate stocks `PET.WDISTP11.W` / `WDISTP21` / `WDISTP31` / `WDISTP41`
/ `WDISTP51` (Mb). The fetch layer distinguishes core vs extension series: a
failing CORE series still trips the tier fallback (the balance sheet is
meaningless without it), while a failing EXTENSION series prints the exact full
v1 identifier and is skipped — dependent sections switch off gracefully rather
than crash.

**14. ULSD history fallback.** NY Harbor ULSD spot starts around mid-2006 — long
enough for a 10-year sample — but if the live pull disagrees, the documented
fallback is the NY Harbor No. 2 heating oil spot (`PET.EER_EPD2F_PF4_Y35NY_DPG.W`),
the pre-ULSD-era continuation of the same marker. Swap the ID in the catalog and
note the splice date here.

**15. Backtest signal in % of norm, not Mb.** The deviation is computed both
ways, but the backtest runs on **% of the 5-yr norm**: a 10 Mb distillate
deficit was a different animal in 2016 (≈150 Mb base) than in 2026 (≈105 Mb).
Percent is scale-free across the decade; Mb is kept for the tables and prose.

**16. One-week publication lag.** WPSR data for the week ending Friday *t* is
published the following Wednesday. The backtest pairs the week-*t* deviation
with the price change from *t+1* to *t+1+h* (`shift(-(1+h)) − shift(-1)`),
enforced by an assertion. Skipping the lag would assume trades placed two
business days before the number existed. Residual caveat the assertion cannot
catch: the price series are weekly *averages*, so the week-(t+1) entry leg
partially predates the Wednesday release — a pro-thesis bias. The auto-summary
therefore also reports a conservative t+2-entry variant (the first fully
post-release weekly average).

**17. Ex-COVID robustness cut.** Mar 2020–Feb 2021 is reported separately and
excluded in a robustness pass: the demand collapse and whipsaw produced
deviation and price moves an order of magnitude outside the rest of the sample,
enough for a single year to dominate a decade of correlation. The exclusion is
**window-overlap aware and horizon-dependent**: a row is dropped when its
forward window [t+1, t+1+h] touches the COVID period, not merely when its
signal date does — filtering on signal date alone would leave Jan/Feb-2020
signals whose forward returns contain the March crash inside the "ex-COVID"
sample. Ex-COVID sign agreement is reported per study (one study flipping sign
is exactly the robustness fact that must not be averaged away). Both cuts are
shown; neither is hidden.

**18. Crack formula and its unit trap.** Diesel crack ($/bbl) = ULSD ($/gal)
× 42 − WTI ($/bbl). The gallons→barrels ×42 is the same class of trap as
Mb vs Mb/d; it is commented at the construction site. Prices never meet the
×7 flow-to-stock conversion.

**19. PADD non-additivity to the balance.** PADD stocks are *components* of the
national total (they sum to `WDISTUS1`; QA checks this) and enter the model as
a **view layer only** — never as extra balance rows, which would double-count.
Their seasonal norms reuse the existing `seasonal_series()` / `deviation()`
functions: one seasonal implementation, no fork.

**20. Map implementation and fallback.** Plotly Express choropleth with
`locationmode="USA-states"` (built-in geometry, no shapefile/geojson downloads —
sandbox-safe), the standard EIA state→PADD dict embedded in the notebook,
diverging RdBu scale centered at 0 (red = tight). Any failure falls back to a
matplotlib bar chart of the five deviations, so Run All can never break on the
map. The interactive figure uses the lightweight `plotly_mimetype` renderer
(no embedded plotly.js bundle). The PNG is embedded in the PDF only if the
local kaleido/plotly pairing supports `write_image`; when it does not (as in
the sandbox), a static bar-chart companion is rendered anyway so GitHub's
static viewer and `charts/` still carry the regional picture.

**21. Synthetic prices embed a lagged response — by design, and stamped.** The
sample generator gives WTI and the crack a mild inventory→price response
(deviation vs a trailing 52-wk mean, shifted +6 weeks, buried under dominant
AR(1) noise and realistic price-level swings). Purpose: the backtest section
must demonstrably *work* end-to-end without credentials. The response is weak
by design, so sample-run verdicts can legitimately come out MIXED or negative —
which exercises the honest-negative reporting path. Synthetic backtest numbers
validate the pipeline, never the thesis; the notebook and the auto-block below
say so explicitly whenever DATA_MODE is SAMPLE.

**22. Backtest sample depth vs START_DATE.** With `START_DATE = 2015-01-01`,
the 5-yr seasonal warm-up means deviations begin in 2020, so the "last 10
years" evaluation effectively starts there (~6.5y). For the full 10-year
window on live data, set `START_DATE = "2009-01-01"` before pulling (weekly
PADD stocks and both price series reach back far enough). Documented in the
run-locally checklist rather than silently changing the existing model's
default history depth.

**23. Tercile hit-rate definition.** Buckets are signal terciles within each
evaluation sample ("tight" = tightest third of the period — relative, robust to
level shifts). Hit rate is sign agreement: tight → forward move > 0, loose →
forward move < 0; undefined for the neutral bucket, shown as NaN. Overlapping
forward windows mean the effective sample is roughly n/h — stated wherever the
tables appear.

<!-- BACKTEST:BEGIN -->
**B. Backtest result (auto-written by the notebook; LIVE (EIA API) mode, run 2026-07-04).** Signals 2016-07-01 -> 2026-06-26, of which 517 have a complete 4-wk forward window (last usable: 2026-05-22); signal lagged 1 wk for WPSR publication: study (a) distillate %-deviation vs forward diesel crack shows r = +0.02 (4w) / +0.01 (8w); the tightest tercile of weeks preceded avg +0.25 $/bbl 4-wk crack moves with a 52% hit rate, vs +0.55 $/bbl for the loosest tercile -- NOT SUPPORTED (2/6 directional checks). Study (b) crude %-deviation vs forward WTI shows r = +0.06 (4w) / +0.07 (8w) -- NOT SUPPORTED (0/6). Ex-COVID (windows overlapping Mar-20..Feb-21 removed, per horizon): study (a) same direction; study (b) same direction. Conservative t+2-entry check (4w): r = +0.02 (a) / +0.06 (b). Caveats: overlapping windows mean the effective sample is ~n/h (517//4 = 129 independent 4-wk moves), so treat correlations as descriptive, not as t-stats; the rolling-correlation chart shows the relationship is regime-dependent; and deviations only begin 5 yrs after START_DATE (set START_DATE=2009 locally for the full 10-yr window).
<!-- BACKTEST:END -->

**24. Mb means MILLION barrels; live volumes are normalized ÷1000.** The
project's original gloss ("Mb = thousand barrels" — repeated in the extension
spec) contradicted its own data: every value in the model, the sample
calibration, the sanity ranges and the PDF (crude ≈409, distillate ≈107,
production ≈13.7/d) is in *million* barrels, while EIA's API serves these
series in *thousand* barrels (units `MBBL` / `MBBL/D`, e.g. crude stocks
≈409,000). The symbol `Mb` is kept but defined correctly as million barrels
everywhere, and the fetch layer normalizes volume series ÷1000 on the way in —
primary check the API's own units string, fallback an unmistakable magnitude
test (million-scale stocks < ~700 vs thousand-scale > ~3,000). Price series
are never scaled. VERIFY LOCALLY on the first live pull: the fetcher prints
one "normalized" line per volume series; if none appear, the API convention
changed and this decision needs revisiting.

**25. QA warnings are scoped to the trailing 3 years.** The live API returns
history to 1982 regardless of the `start` parameter (the seriesid compat route
ignores it — observed on the first live pull). Four decades of history means
1982-83 publication gaps, series that begin later (Cushing 2004, ULSD 2006,
PADD stocks 1990s, crude exports 2016), and pre-shale levels outside modern
sanity bounds — all historical facts, not data problems. Continuity / missing /
range checks therefore run on the trailing 156 weeks so a warning always means
"something is wrong NOW"; older-history NaN counts print as one info line.
Full history is retained for the seasonal frames and the backtest.

**26. Predictive Lab and the futures layer.** The level-signal backtest (block
B) came back negative, as efficient-market logic predicts for public data. The
lab therefore moves the search to where an edge is structurally possible:
expectation-relative signals (4-wk deviation change, days-of-supply deviation,
below-range and Cushing tail dummies), term-structure targets (theory of
storage ties inventories to the CURVE, not flat price), an analog-week kNN
playbook, a walk-forward validation of the inventory projection itself, and
one ex-ante composite rule. Four futures series added — `PET.RCLC1.W`,
`PET.RCLC2.W` ($/bbl) and `PET.EER_EPD2F_PE1_Y35NY_DPG.W` / `PE2` ($/gal,
×42 to $/bbl for spreads) — best guesses, VERIFY LOCALLY like the rest.

**27. Lab methodology guardrails.** Everything honors the one-week publication
lag. Walk-forward pieces never touch post-origin data: the projection
validation slices the frame to each origin and REBUILDS the balance there
(using the notebook's global balance frames would leak); analog pools end 52
weeks before each test origin; composite-rule z-scores are expanding with a
156-week minimum; strategy P&L uses weekly marks (no overlapping-window
inflation) and is labeled costless/descriptive. Dummies with <15 active weeks
are blanked in the matrix.

**28. Synthetic futures couple to the deviation proxies.** Sample-tier M1−M2
spreads respond to the lagged inventory-deviation proxies (theory-of-storage
texture) plus dominant noise — so lab machinery demonstrably works without
credentials, and, as with #21, synthetic lab numbers validate the pipeline
only. The auto-block below is stamped with the data mode.

<!-- LAB:BEGIN -->
**C. Predictive-lab result (auto-written; LIVE (EIA API) mode, run 2026-07-04).** PREDICTIVE LAB VERDICT (LIVE data, 522 wks): (1) Signal-target map -- strongest links: Cushing tail -> WTI M1-M2 4w r=-0.19; crude chg 4w -> WTI M1-M2 8w r=+0.18; Cushing tail -> WTI M1-M2 8w r=-0.18. (2) Curve vs fundamentals (as of 2024-04-05 [HISTORICAL -- futures feed ends there]): HO structure was 0.7 sd RICHER than distillate tightness implied. (3) Analog skill check (5y walk-forward, n=103): sign hit rate 43% vs 55% always-majority baseline -- no edge over base rate. (4) Flow-integration projection vs anchored-seasonal baseline (4w): crude -27%, distillate -25% (walk-forward, n=151) -- the anchored seasonal path is the better point forecaster; the flow engine's value is scenario DELTAS (shared errors cancel between scenario and baseline). (5) Tight+tightening rule on HO M1-M2 spread: total -26.9 $/bbl over 404 wks (127 in market, 43% win rate, max drawdown 32.0 $/bbl). Read (1) with the usual overlap caveat (effective n ~ n/h); the projection skill in (4) is the model's cleanest demonstrated forecasting value.
<!-- LAB:END -->

**29. Projection validation verdict — flow integration is a scenario engine,
not a point forecaster; and the futures feed is discontinued.** The lab's
walk-forward test (151 origins, 6 yrs, h = 4/8/12) shows the Phase-4
flow-integration path is beaten by the trivial "anchored seasonal" ruler
(current level + 5-yr-avg seasonal delta) at every horizon: skill −25% to
−88%. A recalibration grid — momentum decay 0.6–0.85, adjustment carry 0/0.5/1,
flow/seasonal blends w = 0.15/0.3/0.5 — found nothing that beats the anchor
(best: w = 0.15 at +0.1%, i.e. noise). Interpretation: flow-forecast errors
compound ×7×h into stock space, while stock levels are well anchored by
seasonality. Decision: the projection chart now draws the anchored path as the
validated baseline; the flow engine is retained as the **scenario** machinery,
where shocked-vs-baseline *deltas* cancel the shared error. Separately, EIA
discontinued republishing NYMEX futures (weekly AND daily end 2024-04-05,
licensing), so M1−M2 spread studies are an 18-year historical evaluation, not
a live gauge; QA reports those NaNs as an upstream fact, and a live curve
requires an external (CME) feed — a documented integration point, not a bug.
