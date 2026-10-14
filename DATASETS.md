# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new.

## CPI-U item indexes (BLS, Public Data API v2)

**What it is.** Monthly price index levels for the Consumer Price Index for All
Urban Consumers (CPI-U), U.S. city average, not seasonally adjusted, one series
per item: `CUUR0000<item_code>`. The aggregates used for checking are `SA0` (all
items) and `SA0L1E` (all items less food and energy, called "core" here).

**Where it comes from.** `https://api.bls.gov/publicAPI/v2/timeseries/data/`,
POST, JSON, 50 series and 20 years per request, registered key
(`BLS_API_KEY`, central `.env`). Fetched by `scripts/fetch.py`, cached as
`data/raw/indexes.json`.

**Version and vintage.** Pulled October 14, 2026, the day the September 2026
CPI was released. BLS treats the not seasonally adjusted CPI-U as final when it
is issued and does not revise it, apart from rare corrections. (Seasonally
adjusted data is revised for five years each February. It is not used here.)

**Coverage.** January 2014 to September 2026, used for every month from
October 2016 to September 2026 (the animated page). Each index is a direct BLS
estimate built from sampled prices. There are two exceptions:
- **Items without a usable index.** 25 leaves (about 2.7% of December 2024
  weight) have no BLS item code at all: the "Unsampled ..." residual items,
  housing at school, care of invalids and elderly at home, and technical and
  business school tuition. Four more have a code but BLS has paused or
  stopped the index (household operations items, legal services) or
  publishes it every other month (services by other medical professionals).
  These 29 leaves (4.2% of September 2025 weight) are filled from their
  parent; see "Items without a published index" below.
- **Health insurance** is not a price that BLS collects. It is modeled; see
  Known quirks.

**Changes over time.** BLS item structure was the same in the December 2024
and December 2025 weight files: the same 204 leaves. Older history (needed
only for the 10-year average of health insurance and prescription drugs)
uses those two series as published; both existed for the whole window.

**Suppressed, censored or masked values.** None at the U.S. city average level
for the items used.

**Missing data.** October 2025 is published as "-" for every series because
of the federal funding lapse. For the September 2026 release nothing depends
on it. In the monthly series, October 2025 itself has no 12-month change and
is left out; no other month uses October 2025. BLS did not collect October
2025 prices and resumed collection on November 14, 2025 (November 2025
release, "Federal Government Shutdown" box), so November 2025 has more items
without a published index than usual (8.3% of weight, the most of any month).

Some item indexes skip months. BLS does not publish them when it has too few
prices (hospital services: October 2022 and August 2024; household operations
items, leased cars and trucks, legal services and services by other medical
professionals: many months since 2020). Those items are filled for that month
from their parent (see "Items without a published index").

**Revisions.** None expected for not seasonally adjusted data. We pin the
October 14, 2026 pull.

**Units and rounding.** Index levels to three decimals, 1982-84=100 for most
series (some later items use a December 1997 or later base, which does not
affect percent changes). BLS publishes 12-month changes rounded to one
decimal. We compute from the three-decimal index levels, so our changes can
differ from the published ones in the second decimal.

**Known quirks.**
- **Health insurance (SEME) uses the retained earnings method.** BLS does not
  track premiums. It tracks the change in insurers' retained earnings
  (premiums minus benefits paid) relative to benefits, from industry financial
  reports. That ratio lags about 10 months and is smoothed with a two-year
  moving average. It is multiplied by the price change of the other medical
  care indexes. Only the retained earnings part of premiums stays in the
  health insurance weight. The part paid out as benefits is reassigned to the
  medical care items it pays for. So the health insurance weight is much
  smaller than what households spend on premiums.
- **Method changes inside the 10-year window.** The health insurance method
  changed in October 2020 (Medicare Advantage added), April 2021 (one
  nonprofit carrier's data dropped), October 2022 (Medicare Part D added),
  October 2023 (half-year data with two-year smoothing; first half-year update
  with April 2024 data) and October 2025 (long-term care insurance removed).
  Before October 2023 the index was reset once a year, each October, which
  gave the large swings of 2019 through 2023. Since then it updates every
  April and October. So the 10-year average mixes two methods. We say that in
  the post.
- **Prescription drugs (SEMF01)** are priced at the transaction price, which
  includes the insurer's and the patient's share. Rebates paid by drug makers
  to insurers or pharmacy benefit managers after the sale are not captured.
- Source: BLS, "Measuring Price Change in the CPI: Medical care",
  https://www.bls.gov/cpi/factsheets/medical-care.htm.

**License.** U.S. government work, public domain.

## Relative importance of CPI components (BLS)

**What it is.** Each item's share of total CPI-U spending, in percent, as of
December of the named year. The December 2025 file uses 2024 spending weights.
The December 2024 file uses 2023 spending weights.

**Where it comes from.**
`https://www.bls.gov/cpi/tables/relative-importance/{2020..2025}.xlsx`, saved
as `data/raw/relative_importance_{year}.xlsx`. December 2014 to December 2019
come from BLS's archive, `ri-archive-2010-2019.zip` on the same page, as
fixed-width text tables (`{year}.txt`). The weights are not in the API or in
the `download.bls.gov/pub/time.series/cu/` flat files.

**Old-basis December tables (checks only).** In years when weights change,
BLS also prints the December weights on the outgoing basis:
`old-weights-{2021..2025}.htm` on the same page, and `old-weights-{2015,2017,
2019}.pdf` in the archive zip. They are used only to check our roll-forward.

**Version and vintage.** Published once a year. BLS updates weights every
January, so the December 2024 weights govern January to December 2025, and
the December 2025 weights govern January 2026 onward. Between Decembers each
item's weight drifts with its own price change relative to the total. We roll
the December 2024 weights forward to September 2025 that way, which is how BLS
computes the monthly relative importance it prints in the release tables.

Each monthly release prints the weights for the month before. September 2025
weights were never printed: they would have appeared in the October 2025
release, which was cancelled during the funding lapse. The September 2025
release (October 24, 2025) prints August 2025 weights. The November 2025
release (December 18, 2025) prints October 2025 weights. We check our rolled
weights against both printed columns, saved as `data/raw/release_*.htm`.

**Rolling weights forward.** BLS's formula, not rescaled:
RI(month) = RI(December) x (item index month / item index December) /
(all items index month / all items index December). The rolled leaves sum to
99.98 rather than 100 because the published all-items index is aggregated
from area-level data, not from these national item indexes. The 29 filled
leaves then take their weight from their parent's own rolled weight (see
below), which brings the total to 100.001.

**Method chosen (Eric, October 14, 2026).** Chained contribution. Each item
starts from its September 2025 relative importance for September to December
2025. It then uses BLS's December 2025 weights for January to September 2026,
scaled by the all-items change from September to December 2025:

    c = w_Sep25 x (I_Dec25/I_Sep25 - 1)
      + (All_Dec25/All_Sep25) x RI_Dec25 x (I_Sep26/I_Dec25 - 1)

The simpler "September 2025 weight x 12-month change" sums to 3.61% against a
published 3.74%. Most of the gap is gasoline: it rose 34% over the year, much
of it after its weight was reset in January. Core uses the same formula with
weights rescaled to core and the core index (SA0L1E).

**Which index each leaf uses.** Each job needs certain months, and a leaf uses
its own index for a job when that index has them, otherwise its nearest
published parent's:
- the 12-month change needs September 2025 and September 2026;
- rolling the weight needs December 2024 and September 2025;
- splitting the year at the January reweight needs September 2025 and
  December 2025;
- the August 2025 weight check needs December 2024 and August 2025.
In September 2026, three leaves use their own index for the 12-month change
but a parent's for one of the other jobs: gardening and lawncare services (no
December 2024 or December 2025 value; it uses Household furnishings and
operations, because Household operations is not published those months),
motor vehicle body work (no December 2025 value) and leased cars and trucks
(no December 2024 value). They are counted as published items. In such cases
the leaf keeps its own 12-month change, and only the weight roll or the split
at the January reset comes from the parent. Which leaves this affects varies
by month.

**Items without a published index.** 29 leaves (4.2% of September 2025 weight)
have no index with September 2025 and September 2026 values. They are the 25
leaves without an item code, plus household operations items (domestic
services, repair of household items; household operations was last published
October 2024), legal services, and services by other medical professionals
(published every other month). For each nearest published parent, deepest
first:
1. The parent's September 2025 weight is the sum of its leaves' December
   2024 weights, rolled forward with the parent's own index. (The sum of
   leaves, not the parent's printed weight: the two differ by rounding, and
   the sum keeps the leaves adding to the parent. The independent tie-out
   found the choice moves month totals by at most 0.0005 points.) Its
   December 2025 weight is likewise the sum of its leaves' December 2025
   weights.
2. Its contribution is computed with the chained formula, one term at a time
   (September to December 2025, then December 2025 to September 2026).
3. For each term, what the parent's other leaves do not explain goes to the
   filled leaves: the first term shared by their December 2024 weights, the
   second by their December 2025 weights. The filled leaves' weight is the
   parent's weight minus its other leaves' weights.
This makes every published parent reconcile. The change shown for a filled
leaf is its contribution divided by its weight, marked as filled in the viz.
Household operations comes out near 7%, against the 1.55% it would get by
borrowing its parent's change.

**Zero-weight leaves.** Unsampled photography and unsampled recreational
reading materials have a relative importance of 0.000 in some Decembers. When
a leaf is 0.000 in both Decembers a month uses (as both are for September
2026), its contribution is set to 0. In other months they get a tiny fill
(never more than 0.0002 points). They are left out of the drawing whenever
their weight is 0.001% or less.

**Changes shown for small filled items.** A filled leaf's change is its
contribution divided by its weight. When the weight is very small (under about
0.01%), rounding in the parent makes that change unstable. For example, the
tie-out got +29.7% for unsampled public transportation in April 2023 under a
different reading of the fill rule, where we get +11.1%. These boxes are too
small to see, and their contributions are under 0.001 points, but their
colors and tooltip changes should not be read as measured.

**Core weights.** "Rescaled to core" divides by the sum of the core leaves:
in the first term, their December weights rolled to the base month with the
core index (SA0L1E); in the second, their December weights. Using BLS's
printed core weight instead would move core totals by up to 0.0004 points.

**Reconciliation.** Items sum to 3.7380% against the published 3.7377%, and
to 2.5644% against 2.5644% for core. The independent tie-out of October 14,
2026 reproduced every item to within 0.00005 points.

## Monthly series, October 2016 to September 2026 (added October 14, 2026)

**Same method, any month.** `scripts/chain.py` computes any target month T.
The base B is the same month a year earlier. The weights split at the January
reset between them:

    c = w_B x (I_Dec/I_B - 1) + (All_Dec/All_B) x RI_Dec x (I_T/I_Dec - 1)

Dec is the December just before T's year. RI_Dec is that December's table,
and w_B is the December before that, rolled forward to B. When T is a
December, B is that same reset month, so the first term is zero. Core uses
core weights and the core index, as above. The September 2026 results are
identical to `contrib.py`'s.

**Two changes needed for older months, neither of which changes September
2026:**
1. A fill parent must have its own index for all four months (the December
   before B, B, the December reset, and T). When the nearest published parent
   lacks one, the fill moves up to the next parent that has them (household
   operations is published only some months).
2. The core share of a fill is computed from the headline share with the same
   fixed factors that turn any item's headline terms into core terms (core
   weight rescaling, core index for the second term). This allows a parent
   that holds both core and energy items, such as Private transportation in
   November 2025 (motor vehicle insurance missing). The energy items there
   have their own index and are subtracted out first. The filled items under
   one parent must all be core, or all not; the code stops if not.

**Drawn items.** Items with no weight, or too little weight for a 12-month
change (0.001% of the CPI or less, two "Unsampled" items in some months), are
left out of the drawing. They never add up to more than 0.0002 points.

**Per-month tie-out (in `scripts/tieout.py` and TIEOUT.md).** A month passes
when the items add up to the published headline and core within 0.005 points,
the published rate (from the raw index) rounds to the rate BLS reports,
filled items carry 10% of weight or less, and the page draws the same totals.
All 119 months pass. The largest gaps are 0.0013 points (headline) and 0.0008
(core). The largest filled share is 8.3% (November 2025).

**Weight roll-forward check (`scripts/weights_check.py`).** Each December's
weights, rolled forward a year with our indexes, are compared with the next
December BLS printed on the same basis (the regular table in 2016, 2018 and
2020, the old-basis table in other years). Every year matches within 0.001,
which is BLS's rounding, over 153 to 179 items a year. The independent
tie-out also checked parent groups: two are just over 0.001 (housing in
2015, private transportation in 2018, both 0.00101 to 0.00103), consistent
with rounding.

**Why stop at October 2016.** Eric asked for up to ten years. The method and
checks would work further back: the archive has weight tables to 2010 and the
index pull starts in 2014, so January 2016 is the earliest month without new
downloads. That is not used.

**Health insurance over time.** The health insurance item changes method
inside the window (see Known quirks above). Its swings in 2019 to 2023 come
largely from the yearly October reset of the retained earnings method.

**Coverage.** The expenditure tree: 293 nodes under "All items = 100", with 204
leaves that do not overlap and sum to 100. The "Special aggregate indexes"
block below it (core, energy and others) overlaps the tree and is not used,
except to check our core weight.

**Changes over time.** All twelve files, December 2014 to December 2025, have
the same 293 nodes in the same order and nesting, with 204 leaves. This is
asserted by `weights.canonical_tree`. Items were renamed along the
way (15 items, three of them renamed twice) and kept their BLS item code, for example "Airline fare" to "Airline
fares", "Child care and nursery school" to "Day care and preschool", "Land-line
telephone services" to "Residential telephone services". Every year's tree is
relabeled with the December 2025 names, matched by position.

Weight updates: January 2016 (2013-2014 spending), January 2018 (2015-2016),
January 2020 (2017-2018), January 2022 (2019-2020), then every January from
2023 with the spending of two years before. In other years the December table
is the previous December's weights rolled forward.

**Suppressed, censored or masked values.** Two leaves round to 0.000
(unsampled photography, unsampled recreational reading materials).

**Missing data.** None.

**Revisions.** Not revised.

**Units and rounding.** Percent of all items, three decimals. Leaves sum to
100 within 0.05.

**Text tables (2014-2019).** One leading space per indent level after the
first. Long names wrap onto one or two more lines; the last line carries the
numbers. Some full-width names have no dot leader. All three cases are
handled in `weights._txt_rows`, and every parent equals the sum of its
children after the two indent fixes.

**Known quirks.**
- **Two rows are published at the wrong indent level in every file, 2014 to
  2025.**
  "Alcoholic beverages" sits at level 3 under Food; it belongs at level 2
  beside Food. "Information technology, hardware and services" sits at level
  3 under Communication; it belongs at level 4 under Information and
  information processing. We found both by checking that every parent equals
  the sum of its children. Both are fixed in `scripts/weights.py`, carrying
  each row's whole subtree with it. The same fix was first found in the CPI
  diesel project.
- 25 leaves have no item code in `cu.item` ("Unsampled ..." items, housing
  at school, care of invalids and elderly at home, technical and business
  school tuition). Two more, the men's and women's underwear, nightwear,
  swimwear and accessories items, match only after ", and" is collapsed to
  " and"; both have published indexes.
- Food is every leaf under "Food". Energy is every leaf under "Household
  energy" or "Motor fuel". Core is every other leaf, including alcoholic
  beverages and tobacco, as in BLS's own "All items less food and energy".

**License.** U.S. government work, public domain.

## CPI item codes (BLS `cu.item`)

**What it is.** The list of CPI item codes and names, 400 items.

**Where it comes from.** `https://download.bls.gov/pub/time.series/cu/cu.item`,
tab-separated. It needs a browser-like User-Agent.

**Known quirks.** Names mostly match the relative importance file exactly.
Matching is by exact name after collapsing ", and" to " and". Every match is
checked by fetching the series.
