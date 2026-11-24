# SCORE REPORT — Job-Search Agent 3

Run date: 2026-11-24
Scorer: `js3/scorer.py` (`score_posting`, `score_all`)
Input: `output/filter_results.json` (47 passed postings out of 1779)

## Where every number comes from

| Component | Weight | Origin | When it applies |
|---|---|---|---|
| Title match | 60 | Hand-set | reason is `title_match` or `title_and_topic` |
| Topic bonus | 20 | Hand-set | reason is `title_and_topic` |
| Description available | 20 | Hand-set | `description_available` is True |

None of these weights was fitted on labeled data. The 0–100 range exists only because the three hand-set weights sum to 100.

## Held-out set and expected ranking (recorded before running)

The held-out set is the last 10 passed postings in `filter_results.json` order. It is a fixed set to compare the two runs on, not a set of relevance labels: nobody has labeled whether these postings suit Priya, so this report can't measure accuracy.

| # | Board | Posting ID | Title |
|---|---|---|---|
| H1 | spotify | 19c12e29-b6d4-4d97-9053-48238fb7c381 | Machine Learning Engineer - Subscriptions |
| H2 | spotify | 204f6cd7-98a3-4360-87e3-8876adf087da | Senior Data Engineer - Data Platform |
| H3 | spotify | c322d068-5b59-4658-b618-bb2a032eeb9b | Senior Machine Learning Engineer - Messaging Platform |
| H4 | spotify | 05b8d6ee-0773-4255-b8b9-ae73d74a5ee5 | Senior Machine Learning Engineer, Personalization |
| H5 | spotify | c73be71c-1a63-4906-9925-95f2115d1f1d | Senior Software Engineer - Enterprise AI |
| H6 | spotify | 47d4eabf-8d5a-4dab-ac72-de7b5b56841c | Senior Staff Machine Learning Engineer - Content Platform |
| H7 | spotify | 499543e3-78e7-473a-8a1d-a82ce9ce9030 | Senior Staff Machine Learning Engineer - Content Platform |
| H8 | spotify | 281e7db9-86ba-4a1c-8773-c23b96ed32dc | Staff Machine Learning Engineer, Home Surfaces |
| H9 | spotify | 6af8894a-752f-4485-be70-a6685e5fd696 | Staff Machine Learning Engineer, Home Surfaces |
| H10 | spotify | 9761af44-be41-43ca-8c01-79cdbb2aef93 | Staff Machine Learning Engineer, Personalization |

**Expected before running.** All 10 are Spotify (Lever) postings that passed as `title_and_topic` with a description, so I expect each to score 60 + 20 + 20 = **100**. All 10 should tie, and ties keep file order, so the expected ranking is H1 through H10 in the order above. After the one change (description weight 20 → 0), I expect all 10 to drop to **80**, still tied, in the same order.

**Limit of this held-out set.** All 10 held-out postings have descriptions, so the one change moves all of them by the same 20 points and can't change their order. The change matters for how Greenhouse postings rank *against* Spotify postings, and no Greenhouse posting is in the held-out set.

## Run A — default weights (60 / 20 / 20)

Score distribution across the 47 passed postings: **100 × 14** (all Spotify), **60 × 33** (all Databricks and Stripe). No other scores occur.

**Top 10**

| Rank | Score | Board | Posting ID | Title |
|---|---|---|---|---|
| 1 | 100 | spotify | 186b763a-2a61-4563-8813-ff6b40c9c8a7 | Backend Engineer - Data Platform |
| 2 | 100 | spotify | 926149ab-6999-4058-b35d-41e302b70e05 | Backend Engineer - Data Platform |
| 3 | 100 | spotify | b4f6cd01-1d5d-41a9-b287-6d10416da03c | Data Scientist - Business Analytics |
| 4 | 100 | spotify | 8a9cc53c-48c0-4d43-8287-d81ab09e74fa | Data Scientist, Company Planning & Execution |
| 5 | 100 | spotify | 19c12e29-b6d4-4d97-9053-48238fb7c381 | Machine Learning Engineer - Subscriptions |
| 6 | 100 | spotify | 204f6cd7-98a3-4360-87e3-8876adf087da | Senior Data Engineer - Data Platform |
| 7 | 100 | spotify | c322d068-5b59-4658-b618-bb2a032eeb9b | Senior Machine Learning Engineer - Messaging Platform |
| 8 | 100 | spotify | 05b8d6ee-0773-4255-b8b9-ae73d74a5ee5 | Senior Machine Learning Engineer, Personalization |
| 9 | 100 | spotify | c73be71c-1a63-4906-9925-95f2115d1f1d | Senior Software Engineer - Enterprise AI |
| 10 | 100 | spotify | 47d4eabf-8d5a-4dab-ac72-de7b5b56841c | Senior Staff Machine Learning Engineer - Content Platform |

**Bottom 10**

| Rank | Score | Board | Posting ID | Title |
|---|---|---|---|---|
| 38 | 60 | stripe | 7983456 | Machine Learning Engineer, Radar |
| 39 | 60 | stripe | 8333122 | Master's Machine Learning Engineer, Intern |
| 40 | 60 | stripe | 8333074 | Master's Machine Learning Engineer, Intern |
| 41 | 60 | stripe | 8194285 | PhD Data Scientist, Intern |
| 42 | 60 | stripe | 8194283 | PhD Data Scientist, Intern |
| 43 | 60 | stripe | 8328662 | PhD Machine Learning Engineer, Intern |
| 44 | 60 | stripe | 8328664 | PhD Machine Learning Engineer, Intern |
| 45 | 60 | stripe | 8148653 | Staff Machine Learning Engineer, Financial Connections |
| 46 | 60 | stripe | 8243615 | Staff Machine Learning Engineer, Radar |
| 47 | 60 | stripe | 8112043 | Staff Software Engineer, Risk Data Engineering |

Ranks inside a tie are file order, not merit. All 33 Greenhouse postings tie at 60, so "bottom 10" is just the last 10 Stripe postings in the file.

**Held-out result:** H1–H10 each scored 100 and sit at ranks 5–14 in order, as expected.

## The one change — description weight 20 → 0

Only one value changed: `weights={"description": 0}`. Title match (60) and topic bonus (20) stay the same, as do the filter results, the 47 postings, and the held-out 10.

## Run B — description weight 0 (60 / 20 / 0)

Score distribution: **80 × 14** (all Spotify), **60 × 33** (all Databricks and Stripe).

- **Top 10:** the same 10 postings in the same order as Run A, each now scoring 80 instead of 100.
- **Bottom 10:** the same 10 postings in the same order, still at 60.
- **Held-out result:** H1–H10 each scored 80 and are still at ranks 5–14 in the same order, as expected.

## What changed

- **Scores:** every Spotify posting dropped from 100 to 80, and every Greenhouse posting stayed at 60. The gap between them shrank from 40 points to 20.
- **Ranking:** nothing moved. All 47 postings keep the same rank.
- **Why the change didn't help Greenhouse:** the topic bonus can only fire when there is description text to find a topic word in, and Greenhouse postings have none. So the topic bonus is a second description penalty. Removing the description weight still leaves Greenhouse 20 points behind for the same underlying reason: missing data.
- **What the scorer can't tell apart:** within each board, every posting gets the same score. "PhD Machine Learning Engineer, Intern", "Staff Machine Learning Engineer, Radar", and "Machine Learning Engineer, Radar" all score 60. Under either set of weights, the scorer measures which board a posting came from, not how well it fits Priya.

A changed score across runs does not mean anything was trained. These are hand-set weights applied to the same labels.
