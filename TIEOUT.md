# Tie-out

Run by `scripts/tieout.py` on the October 14, 2026 pull. Release month 2026-09.

| Check | Ours | Reference | Tolerance | Result |
|---|---|---|---|---|
| Headline 12-month change (SA0) | 3.7377 | 3.7377 | 0.0001 | pass |
| Core 12-month change (SA0L1E) | 2.5644 | 2.5644 | 0.0001 | pass |
| Headline rounds to 3.7 | 3.7000 | 3.7000 | 1e-09 | pass |
| Core rounds to 2.6 | 2.6000 | 2.6000 | 1e-09 | pass |
| Headline: sum of item contributions | 3.7372 | 3.7377 | 0.005 | pass |
| Core: sum of item contributions | 2.5633 | 2.5644 | 0.005 | pass |
| Dec 2024 leaf weights sum to 100 | 100.0010 | 100.0000 | 0.05 | pass |
| Dec 2025 leaf weights sum to 100 | 100.0010 | 100.0000 | 0.05 | pass |
| Sep 2025 rolled weights sum to 100 | 99.9997 | 100.0000 | 0.01 | pass |
| Aug 2025 rolled weights vs printed: mean abs diff | 0.0006 | 0.0000 | 0.002 | pass |
| Own-index items: 12-month change matches raw (count of mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page headline: items matching contrib.json (mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page headline: published rate | 3.7377 | 3.7377 | 1e-09 | pass |
| Page headline: items add up to | 3.7372 | 3.7372 | 0.001 | pass |
| Page core: items matching contrib.json (mismatches) | 0.0000 | 0.0000 | 0 | pass |
| Page core: published rate | 2.5644 | 2.5644 | 1e-09 | pass |
| Page core: items add up to | 2.5633 | 2.5633 | 0.001 | pass |
| Chart 01: items and values match contrib.json | 1.0000 | 1.0000 | 0 | pass |
| Chart 02: items and values match contrib.json | 1.0000 | 1.0000 | 0 | pass |
| Health insurance: 10-year average Sep-Sep change | 3.5500 | 3.5500 | 0.001 | pass |
| Health insurance: 12-month change | -8.9881 | -8.9881 | 0.001 | pass |
| Health insurance: headline effect of swap | 0.1090 | 0.1090 | 0.0001 | pass |
| Health insurance: core effect of swap | 0.1365 | 0.1365 | 0.0001 | pass |
| Prescription drugs: 10-year average Sep-Sep change | 1.7131 | 1.7131 | 0.001 | pass |
| Prescription drugs: 12-month change | -4.4794 | -4.4794 | 0.001 | pass |
| Prescription drugs: headline effect of swap | 0.0601 | 0.0601 | 0.0001 | pass |
| Prescription drugs: core effect of swap | 0.0754 | 0.0754 | 0.0001 | pass |
| What-if headline | 3.9068 | 3.9068 | 0.001 | pass |
| What-if core | 2.7762 | 2.7762 | 0.001 | pass |
| Chart 04: headline what-if value | 3.9068 | 3.9068 | 1e-09 | pass |
| Chart 04: core what-if value | 2.7762 | 2.7762 | 1e-09 | pass |
| Chart 03: SEME last value is 2026-09 | 1.0000 | 1.0000 | 0 | pass |
| Chart 03: SEME last value | -8.9881 | -8.9881 | 0.001 | pass |
| Chart 03: SEMF01 last value is 2026-09 | 1.0000 | 1.0000 | 0 | pass |
| Chart 03: SEMF01 last value | -4.4794 | -4.4794 | 0.001 | pass |

## Source coverage

- 175 of 204 items have their own published index for the months used.
- 29 items (4.165% of the CPI's weight) do not. Their change is filled from the part of their parent's published change that the parent's published items do not explain.
- Those filled items contribute +0.1613 points of the headline and +0.2020 points of core (5.21% of core's weight).
- BLS's own uncertainty (standard errors, https://www.bls.gov/cpi/tables/variance-estimates/) has not been pulled yet. Single items are less precise than the total.

### Filled items by parent

| Parent (published index) | Items filled | Weight | Contribution | Implied change |
|---|---|---|---|---|
| Information technology, hardware and services | Unsampled information and information processing | 0.009 | -0.0001 | -0.9% |
| Furniture and bedding | Unsampled furniture | 0.009 | -0.0001 | -1.6% |
| Owners' equivalent rent of residences | Unsampled owners' equivalent rent of secondary residences | 1.195 | +0.0373 | +3.1% |
| Hospital and related services | Care of invalids and elderly at home | 0.158 | +0.0071 | +4.5% |
| Lodging away from home | Housing at school, excluding board | 0.252 | +0.0071 | +2.8% |
| Appliances | Unsampled appliances | 0.003 | -0.0001 | -4.4% |
| Professional services | Services by other medical professionals | 0.594 | +0.0237 | +4.0% |
| Tuition, other school fees, and childcare | Technical and business school tuition and fees, Unsampled tuition, other school fees, and childcare | 0.105 | +0.0030 | +2.9% |
| Miscellaneous personal services | Legal services, Unsampled items | 0.408 | +0.0252 | +6.2% |
| Motor vehicle maintenance and repair | Unsampled service policies | 0.064 | +0.0032 | +5.0% |
| Women's apparel | Unsampled women's apparel | 0.011 | +0.0008 | +7.1% |
| Personal care products | Unsampled personal care products | 0.009 | +0.0003 | +3.0% |
| Tools, hardware, outdoor equipment and supplies | Unsampled tools, hardware, outdoor equipment and supplies | 0.238 | +0.0043 | +1.8% |
| New and used motor vehicles | Unsampled new and used motor vehicles | 0.134 | -0.0007 | -0.5% |
| Motor vehicle fees | Unsampled motor vehicle fees | 0.013 | +0.0002 | +1.8% |
| Men's apparel | Unsampled men's apparel | 0.015 | -0.0005 | -3.4% |
| Household furnishings and operations | Domestic services, Repair of household items, Unsampled household operations | 0.575 | +0.0413 | +7.2% |
| Sporting goods | Unsampled sporting goods | 0.016 | +0.0006 | +4.1% |
| Other recreation services | Unsampled recreation services | 0.326 | +0.0062 | +1.9% |
| Recreational reading materials | Unsampled recreational reading materials | 0.000 | -0.0000 | n/a (weight about 0) |
| Tobacco and smoking products | Unsampled tobacco and smoking products | 0.006 | +0.0003 | +5.2% |
| Video and audio | Unsampled video and audio | 0.005 | +0.0001 | +1.5% |
| Public transportation | Unsampled public transportation | 0.004 | +0.0008 | +20.5% |
| Photography | Unsampled photography | 0.000 | +0.0000 | n/a (weight about 0) |
| Other recreational goods | Unsampled recreation commodities | 0.014 | +0.0014 | +10.2% |
