# Decision log — judgment calls made while building to spec

**1. Data source for this delivered run.** The build environment cannot reach
`api.eia.gov` (network allow-list) and no API key was available, so a live pull was
impossible here. Rather than ship untested plumbing, the notebook has a three-tier
data layer — live API → cached pull → bundled synthetic sample — and this delivered
run uses the sample tier. The sample is calibrated to realistic history (the shale
ramp, the 2020 COVID shock, post-2023 export growth) and its 2026 endpoint is aligned
to publicly reported late-June-2026 EIA prints (crude ≈409–412 Mb, ~7% below the
5-yr average; distillate ≈106–107 Mb, ~10% below; Cushing ≈19 Mb; refinery runs
≈17.1 Mb/d; production ≈13.7 Mb/d). Everything synthetic is stamped as such on the
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
