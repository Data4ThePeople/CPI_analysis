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

**Coverage.** January 2014 to September 2026. Each index is a direct BLS
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
of the federal funding lapse. Nothing used here depends on it: the months
needed are December 2024, September 2025, December 2025 and September 2026,
plus the Septembers from 2015 to 2025 for the 10-year average.

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
`https://www.bls.gov/cpi/tables/relative-importance/{2024,2025}.xlsx`, saved
as `data/raw/relative_importance_{year}.xlsx`. The weights are not in the API
or in the `download.bls.gov/pub/time.series/cu/` flat files.

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
Two leaves use their own index for the 12-month change but a parent's for one
of the other jobs: gardening and lawncare services (no December 2024 or
December 2025 value) and motor vehicle body work (no December 2025 value).
Both are counted as published items.

**Items without a published index.** 29 leaves (4.2% of September 2025 weight)
have no index with September 2025 and September 2026 values. They are the 25
leaves without an item code, plus household operations items (domestic
services, repair of household items; household operations was last published
October 2024), legal services, and services by other medical professionals
(published every other month). For each nearest published parent, deepest
first:
1. The parent's own September 2025 weight is its December 2024 weight
   rolled forward with its own index.
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
reading materials have a relative importance of 0.000 in both years. Their
contribution is set to 0, and they are left out of the viz and the charts.

**Reconciliation.** Items sum to 3.7380% against the published 3.7377%, and
to 2.5644% against 2.5644% for core. The independent tie-out of October 14,
2026 reproduced every item to within 0.00005 points.

**Coverage.** The expenditure tree: 293 nodes under "All items = 100", with 204
leaves that do not overlap and sum to 100. The "Special aggregate indexes"
block below it (core, energy and others) overlaps the tree and is not used,
except to check our core weight.

**Changes over time.** The 2024 and 2025 files have the same 204 leaves with
the same names.

**Suppressed, censored or masked values.** Two leaves round to 0.000
(unsampled photography, unsampled recreational reading materials).

**Missing data.** None.

**Revisions.** Not revised.

**Units and rounding.** Percent of all items, three decimals. Leaves sum to
100 within 0.05.

**Known quirks.**
- **Two rows are published at the wrong indent level in both files.**
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
