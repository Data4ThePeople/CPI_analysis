# Status

Project: CPI_analysis
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: what-is-driving-cpi
Step: 2g (not started; resume October 15, 2026 at publish)
Since: 2026-10-14

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-10-14 | Sep 2026 balloon, charts 01-04, what-if; monthly animated balloon Oct 2016-Sep 2026 |
| 2a | Draft with brackets resolved | 2026-10-14 | Brackets resolved, closing in; 8 charts incl. tie-out and headline/core waterfalls |
| 2b | Eric's edit, Claude's look-over | 2026-10-14 | 8 findings: 6 applied, title and subtitle set, publish date Oct 15 kept |
| 2c | Slice markup | 2026-10-14 | 38 slices: 1 drop cap, 15 text, 14 spacers, 5 images, 1 carousel (3), 1 embed, 1 divider |
| 2d | Hero 1680x1080 + alt text | 2026-10-14 | Re-confirmed: data balloon over Eric's Gemini dawn-town backdrop, composited by build.py; alt 411 chars |
| 2e | SEO | 2026-10-14 | Meta 54/152 chars, 8 keywords, Dataset + WebApplication + 10 FAQ; slug what-is-driving-cpi |
| 2f | Pushed to Prismic (draft) | 2026-10-14 | Draft as_QxRcAADIAEZ_y, Migration Release, 56 slices, 9 images |
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
- 2026-10-14 Step 2a opened. Slug cpi-september-2026. Created posts/cpi-september-2026/
  with POST.md from the template; charts 01-04 moved from charts/ to
  posts/cpi-september-2026/images/ (re-rendered, unchanged; tie-out 40 of 40).
- 2026-10-14 2a draft in POST.md: Eric's text verbatim, brackets resolved. New
  charts 01 tie-out, 02 waterfall, 03 fastest-rising; old 01-04 renumbered
  04-07. README.md added (the post links to it). Tie-out 43 of 43.
- 2026-10-14 Step 2a confirmed by Eric. Core waterfall added (chart 03, later
  charts 04-08); health insurance method notes replaced by a link to
  cpi-merry-go-round, method-mix caveat kept in limits; closing in.
- 2026-10-14 Step 2b confirmed by Eric. Viz retitled "The CPI Hot Air Balloon";
  post title the same; subtitle set. Publishes October 15, 2026.
- 2026-10-14 Step 2c confirmed by Eric. Publication time set to 6:30 a.m. EDT,
  October 15, 2026.
- 2026-10-14 Step 2d confirmed by Eric. Hero is the September 2026 balloon,
  rendered by build.py from dist/index.html#hero&theme=dark.
- 2026-10-14 Step 2d reopened by Eric during 2e: hero redone as the balloon alone
  (no axis), 3.74% beside the basket, title and text at left. No later step
  had been confirmed, so nothing is stale. 2e front matter (meta, keywords,
  dataset schema) is drafted in POST.md and resumes after 2d.
- 2026-10-14 Step 2d re-confirmed by Eric (photo backdrop, top 82% crop,
  balloon 650px). Back to 2e.
- 2026-10-14 Slug changed in 2e from cpi-september-2026 to what-is-driving-cpi
  (the page will be updated monthly). Folder and image names follow; entries
  above keep the old name.
- 2026-10-14 Step 2e confirmed by Eric.
- 2026-10-14 Pushed to Prismic as draft as_QxRcAADIAEZ_y in the Migration
  Release: 56 slices, 9 images, tags and author empty.
- 2026-10-14 Step 2f confirmed by Eric. Paused; 2g (Mailchimp teaser) picks up
  October 15, 2026 when Eric publishes.
- 2026-10-14 Phone fix on the embed (GitHub Pages only; Prismic draft
  unchanged): one-sentence description under 620px, shorter callouts on
  narrow screens. Balloon about 15% larger on phones.
- 2026-10-14 Embed restyled at Eric's request: sky-blue gradient background
  and five soft clouds fixed in the sky (light theme; faint versions in
  dark). Hero unchanged. Prismic draft unchanged (embed loads from Pages).
- 2026-10-14 Post: target-line sentence now says the 2% goal is for PCE (Eric
  accepted). Prismic draft as_QxRcAADIAEZ_y updated in place. Embed: one-line
  short description on phones ("Prices up 3.74% in 12 months to Sep 2026"),
  tooltip closes on a tap off the boxes.
