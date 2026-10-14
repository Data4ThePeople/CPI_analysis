# Status

Project: CPI_analysis
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 2a (not started; needs a slug)
Since: 2026-10-14

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-10-14 | Sep 2026 balloon, charts 01-04, what-if; monthly animated balloon Oct 2016-Sep 2026 |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-14 Step 1 opened. Topic: September 2026 CPI item-level contributions
  to 12-month inflation. Hot-air-balloon treemap of the most detailed published
  items (box size = weighted contribution, color = unweighted 12-month change),
  top positive and negative drivers, and a what-if recalculation of headline
  and core with health insurance and prescription drugs at their 10-year
  average (September-to-September changes, 2015-16 through 2024-25).
  Interactive HTML plus static dark PNGs.
- 2026-10-14 Still in Step 1. Eric asked for the balloon animated over time,
  up to 10 years, only for months that tie out with high confidence. Built
  October 2016 to September 2026 (119 months; October 2025 was never
  published) as dist/over-time.html. All months pass the per-month tie-out.
  A second independent tie-out reproduced the output; method text in
  DATASETS.md corrected to match the code where it differed.
- 2026-10-14 Step 1 confirmed by Eric. The animated balloon keeps one shared
  altitude scale across all months so it visibly rises and falls; the scale
  must not change per month.
