# Tie-out

Run by `scripts/tieout.py` on the October 14, 2026 pull. Release month 2026-09.

| Check | Ours | Reference | Tolerance | Result |
|---|---|---|---|---|
| Headline 12-month change (SA0) | 3.7377 | 3.7377 | 0.0001 | pass |
| Core 12-month change (SA0L1E) | 2.5644 | 2.5644 | 0.0001 | pass |
| Headline rounds to 3.7 | 3.7000 | 3.7000 | 1e-09 | pass |
| Core rounds to 2.6 | 2.6000 | 2.6000 | 1e-09 | pass |
| Headline: sum of item contributions | 3.7380 | 3.7377 | 0.002 | pass |
| Core: sum of item contributions | 2.5644 | 2.5644 | 0.002 | pass |
| Dec 2024 leaf weights sum to 100 | 100.0010 | 100.0000 | 0.05 | pass |
| Dec 2025 leaf weights sum to 100 | 100.0010 | 100.0000 | 0.05 | pass |
| Sep 2025 rolled weights sum to 100 | 100.0010 | 100.0000 | 0.01 | pass |
| Aug 2025 rolled weights vs printed: mean abs diff | 0.0006 | 0.0000 | 0.002 | pass |
| Own-index items: 12-month change matches raw (count of mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page headline: items matching contrib.json (mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page headline: published rate | 3.7377 | 3.7377 | 1e-09 | pass |
| Page headline: items add up to | 3.7380 | 3.7380 | 0.001 | pass |
| Page core: items matching contrib.json (mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page core: published rate | 2.5644 | 2.5644 | 1e-09 | pass |
| Page core: items add up to | 2.5644 | 2.5644 | 0.001 | pass |
| Chart 05: items and values match contrib.json | 1.0000 | 1.0000 | 0 | pass |
| Chart 06: items and values match contrib.json | 1.0000 | 1.0000 | 0 | pass |
| Chart 02: waterfall steps add to the items total | 3.7380 | 3.7380 | 0.0001 | pass |
| Chart 02: waterfall total | 3.7380 | 3.7377 | 0.002 | pass |
| Chart 03: core waterfall steps add to the core items total | 2.5644 | 2.5644 | 0.0001 | pass |
| Chart 03: core waterfall total | 2.5644 | 2.5644 | 0.002 | pass |
| Chart 04: fastest risers match raw indexes | 1.0000 | 1.0000 | 0 | pass |
| Health insurance: 10-year average Sep-Sep change | 3.5500 | 3.5500 | 0.001 | pass |
| Health insurance: 12-month change | -8.9881 | -8.9881 | 0.001 | pass |
| Health insurance: headline effect of swap | 0.1090 | 0.1090 | 0.0001 | pass |
| Health insurance: core effect of swap | 0.1364 | 0.1365 | 0.0001 | pass |
| Prescription drugs: 10-year average Sep-Sep change | 1.7131 | 1.7131 | 0.001 | pass |
| Prescription drugs: 12-month change | -4.4794 | -4.4794 | 0.001 | pass |
| Prescription drugs: headline effect of swap | 0.0601 | 0.0601 | 0.0001 | pass |
| Prescription drugs: core effect of swap | 0.0754 | 0.0754 | 0.0001 | pass |
| What-if headline | 3.9068 | 3.9068 | 0.001 | pass |
| What-if core | 2.7762 | 2.7762 | 0.001 | pass |
| Chart 08: headline what-if value | 3.9068 | 3.9068 | 1e-09 | pass |
| Chart 08: core what-if value | 2.7762 | 2.7762 | 1e-09 | pass |
| Chart 07: SEME last value is 2026-09 | 1.0000 | 1.0000 | 0 | pass |
| Chart 07: SEME last value | -8.9881 | -8.9881 | 0.001 | pass |
| Chart 07: SEMF01 last value is 2026-09 | 1.0000 | 1.0000 | 0 | pass |
| Chart 07: SEMF01 last value | -4.4794 | -4.4794 | 0.001 | pass |
| Monthly series: months passing every check (of 119) | 119.0000 | 119.0000 | 0 | pass |
| Monthly series: largest headline gap (pts) | 0.0013 | 0.0000 | 0.005 | pass |
| Monthly series: largest core gap (pts) | 0.0008 | 0.0000 | 0.005 | pass |
| Weight roll-forward vs printed December weights, 2015-2025: largest diff | 0.0010 | 0.0000 | 0.0015 | pass |
| Monthly series September 2026 equals contrib.json (headline sum) | 3.7380 | 3.7380 | 0.001 | pass |

## Source coverage

- 175 of 204 items have their own published index for the months used.
- 29 items (4.188% of the CPI's weight) do not. Their change is filled from the part of their parent's published change that the parent's published items do not explain.
- Those filled items contribute +0.1621 points of the headline and +0.2030 points of core (5.238% of core's weight).
- BLS's own uncertainty (standard errors, https://www.bls.gov/cpi/tables/variance-estimates/) has not been pulled yet. Single items are less precise than the total.

### Filled items by parent

| Parent (published index) | Items filled | Weight | Contribution | Implied change |
|---|---|---|---|---|
| Information technology, hardware and services | Unsampled information and information processing | 0.009 | -0.0001 | -0.9% |
| Lodging away from home | Housing at school, excluding board | 0.243 | +0.0077 | +3.2% |
| Owners' equivalent rent of residences | Unsampled owners' equivalent rent of secondary residences | 1.196 | +0.0373 | +3.1% |
| Furniture and bedding | Unsampled furniture | 0.009 | -0.0001 | -1.7% |
| Appliances | Unsampled appliances | 0.003 | -0.0001 | -4.4% |
| Tools, hardware, outdoor equipment and supplies | Unsampled tools, hardware, outdoor equipment and supplies | 0.238 | +0.0043 | +1.8% |
| Men's apparel | Unsampled men's apparel | 0.015 | -0.0005 | -3.4% |
| Women's apparel | Unsampled women's apparel | 0.011 | +0.0008 | +7.2% |
| New and used motor vehicles | Unsampled new and used motor vehicles | 0.121 | -0.0006 | -0.5% |
| Motor vehicle maintenance and repair | Unsampled service policies | 0.064 | +0.0032 | +5.0% |
| Motor vehicle fees | Unsampled motor vehicle fees | 0.013 | +0.0002 | +1.8% |
| Professional services | Services by other medical professionals | 0.593 | +0.0237 | +4.0% |
| Hospital and related services | Care of invalids and elderly at home | 0.166 | +0.0072 | +4.3% |
| Tuition, other school fees, and childcare | Technical and business school tuition and fees, Unsampled tuition, other school fees, and childcare | 0.105 | +0.0030 | +2.9% |
| Personal care products | Unsampled personal care products | 0.009 | +0.0003 | +3.0% |
| Miscellaneous personal services | Legal services, Unsampled items | 0.412 | +0.0253 | +6.1% |
| Household furnishings and operations | Domestic services, Repair of household items, Unsampled household operations | 0.608 | +0.0411 | +6.8% |
| Public transportation | Unsampled public transportation | 0.004 | +0.0008 | +21.0% |
| Video and audio | Unsampled video and audio | 0.005 | +0.0001 | +1.5% |
| Sporting goods | Unsampled sporting goods | 0.016 | +0.0006 | +4.0% |
| Photography | Unsampled photography | 0.000 | +0.0000 | n/a (weight about 0) |
| Other recreational goods | Unsampled recreation commodities | 0.014 | +0.0014 | +10.2% |
| Other recreation services | Unsampled recreation services | 0.326 | +0.0062 | +1.9% |
| Recreational reading materials | Unsampled recreational reading materials | 0.000 | -0.0000 | n/a (weight about 0) |
| Tobacco and smoking products | Unsampled tobacco and smoking products | 0.006 | +0.0003 | +5.1% |

## Monthly series, October 2016 to September 2026

Each month passes when: the published 12-month rate recomputed from the raw all-items and core indexes matches, rounded to one decimal, the rate BLS itself reports (API calculations); the items add up to within 0.005 points of it, for headline and for core; items without their own index carry no more than 10% of the weight; the weight years it uses pass the roll-forward check; and the page draws the same totals.

Missing: 2025-10: BLS did not publish October 2025 indexes (federal funding lapse).

### Weight roll-forward check

Each December's weights rolled forward a year, compared with what BLS printed for the next December on the same weight basis (`scripts/weights_check.py`).

| December | Compared with | Items | Mean abs diff | Max abs diff |
|---|---|---|---|---|
| 2015 | 2015 December, old-weights table | 161 | 0.00032 | 0.0010 |
| 2016 | 2016 December table (no weight update) | 179 | 0.00033 | 0.0009 |
| 2017 | 2017 December, old-weights table | 160 | 0.00034 | 0.0009 |
| 2018 | 2018 December table (no weight update) | 178 | 0.00032 | 0.0010 |
| 2019 | 2019 December, old-weights table | 153 | 0.00034 | 0.0009 |
| 2020 | 2020 December table (no weight update) | 176 | 0.00033 | 0.0010 |
| 2021 | 2021 December, old-weights table | 173 | 0.00035 | 0.0010 |
| 2022 | 2022 December, old-weights table | 174 | 0.00031 | 0.0009 |
| 2023 | 2023 December, old-weights table | 172 | 0.00033 | 0.0010 |
| 2024 | 2024 December, old-weights table | 172 | 0.00034 | 0.0009 |
| 2025 | 2025 December, old-weights table | 170 | 0.00033 | 0.0009 |

### Every month

| Month | Headline | Items add up to | Gap | Core | Items add up to | Gap | Filled weight | Matches BLS rounded | Result |
|---|---|---|---|---|---|---|---|---|---|
| 2016-10 | 1.636 | 1.636 | +0.0003 | 2.145 | 2.145 | +0.0007 | 2.80% | yes | pass |
| 2016-11 | 1.693 | 1.693 | +0.0005 | 2.111 | 2.111 | +0.0001 | 2.81% | yes | pass |
| 2016-12 | 2.075 | 2.075 | +0.0005 | 2.197 | 2.197 | +0.0002 | 2.82% | yes | pass |
| 2017-01 | 2.500 | 2.500 | +0.0005 | 2.272 | 2.272 | -0.0000 | 2.68% | yes | pass |
| 2017-02 | 2.738 | 2.738 | +0.0003 | 2.224 | 2.223 | -0.0001 | 2.96% | yes | pass |
| 2017-03 | 2.381 | 2.381 | -0.0000 | 2.002 | 2.002 | +0.0000 | 2.39% | yes | pass |
| 2017-04 | 2.200 | 2.200 | +0.0002 | 1.883 | 1.883 | +0.0001 | 2.39% | yes | pass |
| 2017-05 | 1.875 | 1.875 | -0.0001 | 1.733 | 1.733 | -0.0002 | 2.66% | yes | pass |
| 2017-06 | 1.633 | 1.633 | -0.0000 | 1.703 | 1.703 | -0.0001 | 2.66% | yes | pass |
| 2017-07 | 1.728 | 1.728 | -0.0004 | 1.692 | 1.692 | -0.0001 | 2.39% | yes | pass |
| 2017-08 | 1.939 | 1.939 | -0.0000 | 1.684 | 1.684 | -0.0004 | 2.67% | yes | pass |
| 2017-09 | 2.233 | 2.233 | -0.0001 | 1.693 | 1.692 | -0.0002 | 2.39% | yes | pass |
| 2017-10 | 2.041 | 2.041 | -0.0002 | 1.774 | 1.773 | -0.0004 | 2.39% | yes | pass |
| 2017-11 | 2.203 | 2.203 | +0.0001 | 1.711 | 1.711 | +0.0000 | 2.40% | yes | pass |
| 2017-12 | 2.109 | 2.109 | -0.0002 | 1.776 | 1.776 | +0.0001 | 2.68% | yes | pass |
| 2018-01 | 2.071 | 2.070 | -0.0005 | 1.821 | 1.821 | +0.0001 | 2.68% | yes | pass |
| 2018-02 | 2.212 | 2.212 | -0.0001 | 1.848 | 1.848 | +0.0002 | 2.96% | yes | pass |
| 2018-03 | 2.360 | 2.360 | -0.0001 | 2.117 | 2.117 | +0.0003 | 2.40% | yes | pass |
| 2018-04 | 2.463 | 2.462 | -0.0003 | 2.139 | 2.139 | +0.0001 | 2.39% | yes | pass |
| 2018-05 | 2.801 | 2.801 | +0.0003 | 2.237 | 2.238 | +0.0003 | 2.39% | yes | pass |
| 2018-06 | 2.872 | 2.872 | +0.0003 | 2.255 | 2.255 | +0.0002 | 2.67% | yes | pass |
| 2018-07 | 2.950 | 2.950 | -0.0000 | 2.354 | 2.354 | +0.0002 | 2.40% | yes | pass |
| 2018-08 | 2.699 | 2.699 | -0.0001 | 2.199 | 2.199 | +0.0003 | 2.68% | yes | pass |
| 2018-09 | 2.277 | 2.277 | -0.0001 | 2.170 | 2.170 | +0.0002 | 2.39% | yes | pass |
| 2018-10 | 2.522 | 2.522 | -0.0000 | 2.139 | 2.139 | +0.0003 | 2.39% | yes | pass |
| 2018-11 | 2.177 | 2.176 | -0.0005 | 2.214 | 2.214 | -0.0001 | 2.40% | yes | pass |
| 2018-12 | 1.910 | 1.910 | +0.0001 | 2.179 | 2.179 | +0.0004 | 2.68% | yes | pass |
| 2019-01 | 1.551 | 1.551 | +0.0002 | 2.154 | 2.154 | +0.0003 | 2.83% | yes | pass |
| 2019-02 | 1.520 | 1.520 | -0.0001 | 2.084 | 2.084 | +0.0001 | 2.83% | yes | pass |
| 2019-03 | 1.863 | 1.862 | -0.0002 | 2.037 | 2.037 | -0.0000 | 2.55% | yes | pass |
| 2019-04 | 1.996 | 1.996 | -0.0004 | 2.065 | 2.065 | +0.0001 | 2.55% | yes | pass |
| 2019-05 | 1.790 | 1.790 | -0.0005 | 1.989 | 1.989 | -0.0002 | 2.54% | yes | pass |
| 2019-06 | 1.648 | 1.648 | -0.0006 | 2.127 | 2.126 | -0.0002 | 2.54% | yes | pass |
| 2019-07 | 1.811 | 1.811 | -0.0004 | 2.210 | 2.210 | +0.0002 | 2.66% | yes | pass |
| 2019-08 | 1.750 | 1.749 | -0.0003 | 2.386 | 2.386 | +0.0001 | 2.84% | yes | pass |
| 2019-09 | 1.711 | 1.711 | -0.0000 | 2.358 | 2.358 | +0.0001 | 2.66% | yes | pass |
| 2019-10 | 1.764 | 1.764 | -0.0000 | 2.314 | 2.315 | +0.0001 | 2.56% | yes | pass |
| 2019-11 | 2.051 | 2.052 | +0.0003 | 2.317 | 2.317 | +0.0001 | 2.58% | yes | pass |
| 2019-12 | 2.285 | 2.285 | -0.0001 | 2.259 | 2.259 | +0.0001 | 2.88% | yes | pass |
| 2020-01 | 2.487 | 2.487 | +0.0002 | 2.261 | 2.261 | +0.0002 | 2.88% | yes | pass |
| 2020-02 | 2.335 | 2.335 | +0.0006 | 2.357 | 2.357 | +0.0002 | 2.87% | yes | pass |
| 2020-03 | 1.539 | 1.540 | +0.0004 | 2.091 | 2.092 | +0.0002 | 2.86% | yes | pass |
| 2020-04 | 0.329 | 0.330 | +0.0008 | 1.432 | 1.433 | +0.0004 | 3.40% | yes | pass |
| 2020-05 | 0.118 | 0.119 | +0.0007 | 1.222 | 1.223 | +0.0006 | 2.54% | yes | pass |
| 2020-06 | 0.646 | 0.646 | +0.0005 | 1.187 | 1.188 | +0.0005 | 3.18% | yes | pass |
| 2020-07 | 0.986 | 0.987 | +0.0007 | 1.570 | 1.570 | +0.0002 | 3.47% | yes | pass |
| 2020-08 | 1.310 | 1.310 | +0.0006 | 1.736 | 1.737 | +0.0003 | 2.87% | yes | pass |
| 2020-09 | 1.371 | 1.372 | +0.0005 | 1.713 | 1.714 | +0.0003 | 3.30% | yes | pass |
| 2020-10 | 1.182 | 1.182 | +0.0002 | 1.611 | 1.611 | +0.0002 | 3.60% | yes | pass |
| 2020-11 | 1.175 | 1.175 | +0.0001 | 1.646 | 1.647 | +0.0001 | 3.49% | yes | pass |
| 2020-12 | 1.362 | 1.362 | -0.0002 | 1.620 | 1.620 | -0.0001 | 3.61% | yes | pass |
| 2021-01 | 1.400 | 1.400 | -0.0002 | 1.410 | 1.410 | -0.0000 | 2.97% | yes | pass |
| 2021-02 | 1.676 | 1.675 | -0.0008 | 1.283 | 1.282 | -0.0001 | 3.61% | yes | pass |
| 2021-03 | 2.620 | 2.619 | -0.0004 | 1.646 | 1.646 | +0.0000 | 3.63% | yes | pass |
| 2021-04 | 4.160 | 4.159 | -0.0006 | 2.961 | 2.961 | -0.0003 | 3.57% | yes | pass |
| 2021-05 | 4.993 | 4.992 | -0.0009 | 3.798 | 3.797 | -0.0005 | 3.37% | yes | pass |
| 2021-06 | 5.391 | 5.391 | -0.0009 | 4.475 | 4.474 | -0.0001 | 3.45% | yes | pass |
| 2021-07 | 5.365 | 5.365 | -0.0005 | 4.275 | 4.274 | -0.0001 | 3.57% | yes | pass |
| 2021-08 | 5.251 | 5.250 | -0.0009 | 4.000 | 4.000 | -0.0004 | 3.42% | yes | pass |
| 2021-09 | 5.390 | 5.389 | -0.0012 | 4.025 | 4.025 | -0.0002 | 3.41% | yes | pass |
| 2021-10 | 6.222 | 6.221 | -0.0010 | 4.563 | 4.562 | -0.0003 | 3.73% | yes | pass |
| 2021-11 | 6.809 | 6.808 | -0.0009 | 4.929 | 4.928 | -0.0001 | 3.77% | yes | pass |
| 2021-12 | 7.036 | 7.036 | -0.0004 | 5.453 | 5.453 | -0.0003 | 3.77% | yes | pass |
| 2022-01 | 7.480 | 7.479 | -0.0007 | 6.021 | 6.021 | -0.0000 | 3.71% | yes | pass |
| 2022-02 | 7.871 | 7.870 | -0.0006 | 6.414 | 6.414 | -0.0002 | 3.69% | yes | pass |
| 2022-03 | 8.542 | 8.542 | -0.0009 | 6.474 | 6.475 | +0.0000 | 3.68% | yes | pass |
| 2022-04 | 8.259 | 8.258 | -0.0007 | 6.161 | 6.161 | +0.0002 | 3.69% | yes | pass |
| 2022-05 | 8.582 | 8.581 | -0.0009 | 6.022 | 6.022 | +0.0003 | 3.68% | yes | pass |
| 2022-06 | 9.060 | 9.059 | -0.0009 | 5.917 | 5.917 | +0.0003 | 3.93% | yes | pass |
| 2022-07 | 8.525 | 8.524 | -0.0012 | 5.911 | 5.911 | +0.0000 | 3.97% | yes | pass |
| 2022-08 | 8.263 | 8.262 | -0.0010 | 6.322 | 6.322 | +0.0003 | 3.66% | yes | pass |
| 2022-09 | 8.202 | 8.201 | -0.0011 | 6.631 | 6.631 | +0.0000 | 3.97% | yes | pass |
| 2022-10 | 7.745 | 7.744 | -0.0011 | 6.284 | 6.285 | +0.0003 | 5.84% | yes | pass |
| 2022-11 | 7.110 | 7.109 | -0.0013 | 5.958 | 5.958 | -0.0001 | 3.68% | yes | pass |
| 2022-12 | 6.454 | 6.453 | -0.0010 | 5.708 | 5.708 | +0.0002 | 3.68% | yes | pass |
| 2023-01 | 6.410 | 6.409 | -0.0007 | 5.583 | 5.583 | +0.0002 | 3.66% | yes | pass |
| 2023-02 | 6.036 | 6.035 | -0.0004 | 5.538 | 5.538 | +0.0003 | 3.63% | yes | pass |
| 2023-03 | 4.985 | 4.985 | -0.0004 | 5.590 | 5.590 | -0.0001 | 3.67% | yes | pass |
| 2023-04 | 4.930 | 4.930 | -0.0003 | 5.519 | 5.519 | -0.0002 | 3.89% | yes | pass |
| 2023-05 | 4.048 | 4.048 | +0.0001 | 5.330 | 5.330 | -0.0000 | 3.61% | yes | pass |
| 2023-06 | 2.969 | 2.969 | +0.0001 | 4.829 | 4.829 | -0.0001 | 3.15% | yes | pass |
| 2023-07 | 3.178 | 3.178 | +0.0002 | 4.653 | 4.653 | -0.0000 | 3.18% | yes | pass |
| 2023-08 | 3.665 | 3.665 | +0.0001 | 4.349 | 4.349 | +0.0002 | 3.91% | yes | pass |
| 2023-09 | 3.700 | 3.700 | +0.0003 | 4.147 | 4.147 | +0.0001 | 3.27% | yes | pass |
| 2023-10 | 3.241 | 3.241 | +0.0002 | 4.031 | 4.031 | -0.0000 | 6.10% | yes | pass |
| 2023-11 | 3.137 | 3.138 | +0.0005 | 4.007 | 4.007 | +0.0002 | 4.19% | yes | pass |
| 2023-12 | 3.352 | 3.352 | +0.0002 | 3.930 | 3.930 | +0.0001 | 4.24% | yes | pass |
| 2024-01 | 3.091 | 3.091 | +0.0000 | 3.862 | 3.862 | +0.0001 | 3.65% | yes | pass |
| 2024-02 | 3.153 | 3.153 | +0.0001 | 3.752 | 3.753 | +0.0003 | 4.25% | yes | pass |
| 2024-03 | 3.477 | 3.478 | +0.0002 | 3.801 | 3.801 | +0.0001 | 3.22% | yes | pass |
| 2024-04 | 3.357 | 3.357 | +0.0000 | 3.610 | 3.610 | +0.0002 | 3.96% | yes | pass |
| 2024-05 | 3.269 | 3.269 | -0.0002 | 3.419 | 3.419 | +0.0003 | 3.79% | yes | pass |
| 2024-06 | 2.971 | 2.972 | +0.0002 | 3.267 | 3.267 | +0.0001 | 4.62% | yes | pass |
| 2024-07 | 2.895 | 2.895 | -0.0002 | 3.171 | 3.171 | -0.0001 | 3.79% | yes | pass |
| 2024-08 | 2.531 | 2.531 | -0.0000 | 3.197 | 3.197 | -0.0001 | 6.30% | yes | pass |
| 2024-09 | 2.441 | 2.441 | +0.0002 | 3.311 | 3.311 | -0.0001 | 3.35% | yes | pass |
| 2024-10 | 2.598 | 2.598 | +0.0002 | 3.333 | 3.333 | -0.0001 | 3.99% | yes | pass |
| 2024-11 | 2.749 | 2.749 | +0.0001 | 3.319 | 3.318 | -0.0001 | 4.36% | yes | pass |
| 2024-12 | 2.888 | 2.888 | +0.0001 | 3.238 | 3.238 | -0.0003 | 4.60% | yes | pass |
| 2025-01 | 3.000 | 3.000 | -0.0001 | 3.258 | 3.258 | -0.0004 | 4.31% | yes | pass |
| 2025-02 | 2.822 | 2.822 | +0.0001 | 3.117 | 3.117 | -0.0004 | 4.32% | yes | pass |
| 2025-03 | 2.391 | 2.391 | -0.0002 | 2.789 | 2.789 | -0.0002 | 4.39% | yes | pass |
| 2025-04 | 2.311 | 2.311 | -0.0002 | 2.779 | 2.779 | -0.0003 | 4.41% | yes | pass |
| 2025-05 | 2.355 | 2.355 | +0.0000 | 2.787 | 2.787 | -0.0004 | 3.79% | yes | pass |
| 2025-06 | 2.669 | 2.669 | -0.0000 | 2.934 | 2.934 | -0.0002 | 4.39% | yes | pass |
| 2025-07 | 2.705 | 2.705 | +0.0002 | 3.059 | 3.060 | +0.0002 | 4.46% | yes | pass |
| 2025-08 | 2.916 | 2.916 | +0.0003 | 3.110 | 3.110 | -0.0003 | 7.01% | yes | pass |
| 2025-09 | 3.013 | 3.013 | +0.0001 | 3.019 | 3.019 | -0.0000 | 4.18% | yes | pass |
| 2025-11 | 2.735 | 2.735 | -0.0001 | 2.633 | 2.634 | +0.0003 | 8.26% | yes | pass |
| 2025-12 | 2.677 | 2.677 | -0.0002 | 2.639 | 2.640 | +0.0002 | 4.99% | yes | pass |
| 2026-01 | 2.386 | 2.386 | -0.0002 | 2.504 | 2.504 | -0.0000 | 4.92% | yes | pass |
| 2026-02 | 2.414 | 2.414 | -0.0000 | 2.457 | 2.457 | +0.0002 | 4.97% | yes | pass |
| 2026-03 | 3.256 | 3.257 | +0.0004 | 2.595 | 2.595 | +0.0004 | 4.98% | yes | pass |
| 2026-04 | 3.811 | 3.812 | +0.0008 | 2.750 | 2.751 | +0.0008 | 4.06% | yes | pass |
| 2026-05 | 4.249 | 4.249 | +0.0004 | 2.851 | 2.851 | +0.0003 | 4.17% | yes | pass |
| 2026-06 | 3.531 | 3.532 | +0.0009 | 2.594 | 2.595 | +0.0007 | 3.97% | yes | pass |
| 2026-07 | 3.365 | 3.365 | +0.0004 | 2.478 | 2.478 | +0.0001 | 4.17% | yes | pass |
| 2026-08 | 3.397 | 3.396 | -0.0001 | 2.446 | 2.446 | +0.0004 | 4.57% | yes | pass |
| 2026-09 | 3.738 | 3.738 | +0.0003 | 2.564 | 2.564 | +0.0000 | 4.19% | yes | pass |
