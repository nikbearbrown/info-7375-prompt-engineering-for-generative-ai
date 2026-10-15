# FACTCHECK — checkedsql-pitch

Every claim in the narration, checked against its source. "Will" claims are plans, not facts, and are marked PLAN.

| # | Beat | Claim | Verdict | Source / note |
|---|---|---|---|---|
| 1 | BIDEA | I'm Siddhesh Nikam; this is my final-project pitch | PASS | the student |
| 2 | BDEFS | ROAS = revenue divided by ad spend | PASS | standard definition; same formula as `marketing-campaign-analytics` README (ROAS metric) |
| 3 | B00 | CheckedSQL will take a plain-English question, have Claude write SQL, run it, show answer + query + check | PLAN | PROJECT-BRIEF.md §1 |
| 4 | B01 | the repo will hold a synthetic dataset, a Python tool, ~30-question test set, an evaluation log | PLAN | PROJECT-BRIEF.md §1 |
| 5 | B02 | I built a Tableau dashboard for my marketing campaign project | PASS — student to confirm | github.com/nikam0420/marketing-campaign-analytics README lists a Tableau dashboard (read 2026-10-14) |
| 6 | B02 | a dashboard answers questions planned in advance; a new question needs a new view | PASS | how a fixed dashboard works |
| 7 | B03 | a general chat assistant writes a query; some can run code on an uploaded file; no fixed test set of *my* questions | PASS | general description, no product named, no metric claimed |
| 8 | B04 | hiring manager's first 60 s: README, score table, one command | PLAN | PROJECT-BRIEF.md §3 |
| 9 | B05 | I already write SQL and define marketing metrics | PASS | `marketing-campaign-analytics`: `sql/03_create_kpi_views.sql`, `python/transform_campaign_data.py` (CTR, conversion rate, ROAS, profit) |
| 10 | B06 | read-only, one schema, no dashboards, no real company data | PLAN | PROJECT-BRIEF.md §5 |
| 11 | B07 | ten-question baseline before any Claude call | PLAN | PROJECT-BRIEF.md §5 |
| 12 | B08 | averaging ROAS row by row differs from total revenue ÷ total spend | PASS | arithmetic: mean of ratios ≠ ratio of sums unless every row has equal spend |
| 13 | B09 | my repo computes click-through rate and ROAS with SQL, PostgreSQL and pandas | PASS | `marketing-campaign-analytics` README + file list (read 2026-10-14) |
| 14 | B10 | exists today: two earlier repos + this pitch; nothing of CheckedSQL is built | PASS | github.com/nikam0420 (public repos, read 2026-10-14) |

No users, employers, metrics, testimonials or results are claimed. No Claude responses are shown on screen.
