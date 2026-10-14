# What moved inflation: the CPI hot air balloon

Data 4 The People. Each detailed item in the Consumer Price Index (CPI-U, U.S.
city average, not seasonally adjusted), sized by how much it added to or took
away from the 12-month inflation rate, month by month from October 2016 to
September 2026.

- Animated balloon, October 2016 to September 2026:
  https://data4thepeople.github.io/CPI_analysis/dist/over-time.html
- September 2026 only:
  https://data4thepeople.github.io/CPI_analysis/dist/index.html

## Where to look

| File | What it holds |
|---|---|
| `DATASETS.md` | Every data source, where it comes from, its limits and quirks, and the method in full |
| `TIEOUT.md` | Every check we run, with our number, the reference number and the result |
| `data/processed/monthly_summary.csv` | One row per month: the published 12-month change, what our items add up to, and the gap |
| `data/processed/monthly_items.csv` | One row per month and item: weight, 12-month change and contribution |

## Method in brief

Each item's contribution is its weight times its price change, with the weights
chained across BLS's January weight update so the items add up to the
published headline and core rates. In September 2026, 29 of the 204 items
(4.2% of the weight) had no published index of their own; their change is
filled from their parent category. `DATASETS.md` has the details.

## Rebuild

Python 3 with `matplotlib` and `pypdf`. The fetch step needs a free BLS API
key, `BLS_API_KEY`; `scripts/common.py` shows how it is loaded.

```
cd scripts
python fetch.py          # indexes from the BLS API, weights from bls.gov
python contrib.py        # September 2026 contributions and the what-if
python monthly.py        # every month, October 2016 to September 2026
python weights_check.py  # weight roll-forward vs printed December weights
python charts.py         # static charts
python build.py          # the two HTML pages
python tieout.py         # writes TIEOUT.md
```

Source: U.S. Bureau of Labor Statistics. Public domain.
