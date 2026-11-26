# FILTER — what reaches Mira, and why

## Executive summary

This is the gate for Job-Search Agent 3, written before the filter code. It says:
- which postings count as relevant for the fictional persona (`persona/resume.json`: a new-graduate data or business analyst in the US who needs visa sponsorship);
- when a claim about a posting counts as supported;
- what the agent must say when it cannot tell.

The machine-readable version is `filter/filter-<version>.json`, and the code reads only that file. Every change to the filter is a new version, recorded below with the measurement that justified it.

## 1. The filter, v1 (2026-11-25; see §5 for v2–v4)

Every rule reads only the posting's own `title`, `location` and description text.

| # | Rule | Points (v1) | Why |
|---|---|---|---|
| F1 | **Role word in the title**, whole words, any case: `Data Analyst`, `Business Intelligence`, `Analytics`, `Business Analyst`, `Product Analyst` | +4 | These are the persona's target roles, the same list as JS1 contract R1. The title is where an employer names the job; words in the description name tools and teams, not the role. |
| F2 | **Topic words in the description**, whole words: `SQL`, `Python`, `Tableau`, `Looker`, `Power BI`, `Excel`, `dashboard(s)`, `A/B test(ing)`, `statistics`, `statistical`, `data visualization` | +1 each distinct word, at most +4 | These are the persona's skills. The cap stops a long description that lists every tool from outranking a real role match (wrong version W2). |
| F3 | **Senior word in the title**: `Senior`, `Sr.`, `Staff`, `Principal`, `Lead`, `Director`, `Head`, `Manager`, `III` | −3 | A 0-year candidate is not senior (JS1 R2). |
| F4 | **Stated minimum of 3 or more years** in the description | −3 | Same reason (JS1 R4; the same phrase patterns). |
| F5 | **Location not in the US** (JS1 R3, with the JS2 full-state-name fix) | −5 | The persona can work only in the US. |
| F6 | **Citizenship, clearance or no-sponsorship phrase** (JS1 R5, R6) | −5 | The persona is not a citizen and needs sponsorship. |

**Keep** a posting when its score is **≥ 5**. With these points, nothing reaches 5 without F1: topic words alone give at most 4.

**Where the numbers come from:** every weight and the threshold are **hand-set** in v1. They are ordinal choices (a hard requirement outweighs any number of topic words), not fitted, and §6 measures them.

**Rejected before measuring:** the topic word `R`. A one-letter word matches initials and list markers.

## 2. Evidence rules

The shortlist explains each kept posting as a list of claims, such as "the title names a target role", "the job is in the US", "the posting asks for SQL" or "the posting does not rule out sponsorship". Each claim is labelled against **the posting's own text**, never against the company's reputation or another page:

| Label | When |
|---|---|
| **supported** | the text contains the evidence, quoted in the label (e.g. the location string, the matched word, the sentence) |
| **contradicted** | the text contains something that says the opposite (e.g. "must be a U.S. citizen" against "does not require citizenship") |
| **insufficient** | the text says neither |

**Abstention ("I cannot tell").** The agent must say "I cannot tell" instead of keep or reject when any of these is true:
- the description is shorter than 200 characters;
- the location is empty;
- the posting would be kept (score ≥ threshold) but mentions none of `sponsor`, `visa` or `work authorization`. Then the sponsorship claim is **insufficient**, and the row says "sponsorship: I cannot tell", not "sponsorship: OK". A posting already below the threshold is rejected on its other rules; its silence about sponsorship does not change that.

Rule F6 passing means only "no excluding phrase found". It does not mean "sponsors".

## 3. Expected sources

| Source | Fields the agent must see | If missing |
|---|---|---|
| Greenhouse `pinterest`, `databricks` | `title`, `location.name`, `content` | missing `content`: abstain (§2); missing board: the JS2 run is `incomplete` |
| Ashby `ramp` | `title`, `location` / `address`, `descriptionHtml` | same |
| Lever `palantir` | `text`, `categories.location`, `description` + `lists` | same |

The data for this assignment is the union of JS2's two real runs (2026-11-09 and 2026-11-10): 1,595 distinct postings in `data/postings.jsonl`. The later snapshot wins when a posting appears in both.

## 4. Wrong versions my tests must catch

| | Plausible but wrong | Why it is wrong | Test |
|---|---|---|---|
| W1 | **Substring matching**: `Excel` matches "excellent", `Analytics` matches "Analyticsplatform" | inflates topic scores with words that are not there | `test_w1_whole_words_only` |
| W2 | **Rank by topic-word count, no cap**: a description listing 8 tools beats a "Data Analyst" title | rewards long boilerplate over the role | `test_w2_topic_words_cannot_beat_role` |
| W3 | **A missing location counts as US** | silently keeps jobs the persona may not be able to take | `test_w3_missing_location_abstains` |
| W4 | **"No no-sponsorship phrase" reported as "sponsors"** | turns silence into a claim | `test_w4_silence_is_insufficient_not_supported` |

## 5. Version history

| Version | Date | Change | Measured on | Result |
|---|---|---|---|---|
| v1 | 2026-11-25 | first version, written before code | 61 hand labels | 0 of 5 held-out Y found; 1 of 1,595 reaches Mira |
| v2 | 2026-11-25 | threshold 5 → 0; + clearance phrases; + four no-sponsorship phrases; + PhD in title → −5. Rejected: dropping the 3+ years penalty | 45 dev + 16 held-out labels | 5 of 5 held-out Y found, 1 of 11 held-out N shown; 193 reach Mira |
| v3 | 2026-11-25 | `Excel` matched only when capitalised; senior −3 → −5, + `Sr` | not measurable on the labels (no labelled row changes) | 138 reach Mira |
| v4 | 2026-11-25 | evidence fix for §2: sponsorship is **supported** only by a sentence with a sponsor word and a visa word and no negation; a 1–2 year minimum **contradicts** "fits a new graduate" (score unchanged) | same labels: no change | 138 reach Mira, all "cannot tell" |

**Current version: v4** (`filter/filter-v4.json`). Every step, with its numbers, is in `SCORE-CHANGES.md`; the audit that motivated v2 is in `AUDIT.md`.

**Changed my mind about the relevance rule.** v1 kept only postings with one of the persona's five target role words. My hand labels (AUDIT.md §2) show that I would send Mira to any entry-level US job she can apply to. v2 therefore makes the role word a bonus (+4) instead of a gate.

## 6. What moves the score

See `SCORE-CHANGES.md`: each number's origin, and one change at a time, measured on held-out labels.
