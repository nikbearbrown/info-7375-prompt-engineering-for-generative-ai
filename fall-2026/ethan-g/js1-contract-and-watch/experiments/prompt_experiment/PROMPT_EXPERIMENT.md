# Prompt experiment (Chapter 2)



## Set

20 real postings, all from the allow-listed host (`boards-api.greenhouse.io`), all saved on 2026-10-31 in
`experiments/source_raw/` (frozen, so the set doesn't move while the watch keeps running): Samsara plus Coinbase, Discord, Elastic, Brex, Reddit, and Twilio. **No sampling and no
hand-picking:** the pool is *every* data-titled posting on those 7 boards (title matches data engineer, analytics
engineer, data platform, data infrastructure, data & analytics, market data, or data analyst, the last added with
CONTRACT v2.1). The 6 postings the watch already ran through Claude are excluded, and repeated titles on one board are
collapsed to the lowest id (Samsara lists one role in 8 cities). That left 21. Shuffled with seed 7375, the first 20 were
split 10 dev / 10 held-out (`experiments/common.py`). **Left out by the shuffle:** Coinbase 8180833 "Senior Market Data
Engineer" (Remote - USA, asks 3+ years), a likely match. It was not swapped back in, because choosing after seeing it would be cherry-picking.

The random split is uneven. Dev has 4 Staff-titled roles, while held-out has more Remote-US roles asking 2–5 years.
There is only **one** data analyst posting in the whole set (Brex "Data Analyst II", New York, in dev).
It was left as drawn: rebalancing by hand after seeing the titles would be cherry-picking.

Labels: `labels.csv` (with a one-line reason per label). Rule: `LABELING_RULE.md` (finished 19:37, before any label). After labeling, each split had
**4 relevant and 6 not relevant**. Labeling history: a first pass, a self-check against the rule, a second pass, and Ethan's decision to follow the rule for
4 Staff/Lead titles and 1 intern. All of it happened before any judge was run against the labels (snapshots `labels_first_pass_19-45.csv` and
`labels_second_pass_19-49.csv`).

## Prompts

- **v1 baseline:** `prompts/judge_v1_baseline.txt`
- **v2 revision:** `prompts/judge_v2_revision.txt`. **The one change** (chosen by Ethan from three candidates) is one added sentence:
  > Domain experience: do not mark a posting not_relevant only because the candidate lacks industry or domain experience (e.g. ads, healthcare, fintech)
  > unless the posting lists it as a minimum requirement.

  **Why:** v1's one dev failure that conflicted with the labeling rule was 8299493002 (Discord, Senior Data Engineer, Ads). Claude rejected it partly for
  "no ad-tech background", while the labeling rule doesn't require domain experience and allows 5 years. The other candidates were a years-policy sentence
  and a quote-the-evidence sentence.

## Results

| prompt | split | n | Claude pass | rejected | rule judge (same postings) |
|---|---|---|---|---|---|
| v1 | dev | 10 | **8/10** | 0 | 8/10 |
| v2 | dev | 10 | **8/10** | 0 | 8/10 |
| v1 | held-out | 10 | **9/10** | 0 | 8/10 |
| v2 | held-out | 10 | **9/10** | 0 | 8/10 |

Raw per-posting results: `results/*.jsonl`. Held-out was unlocked once per prompt, after both were frozen: `results/HELDOUT_LOG.txt` (19:58:12 v1, 19:58:49 v2,
with prompt hashes).

**What the misses were** (each Claude reason checked against the posting text):

| Posting | Split | Hand label | Claude (v1 = v2) | Rule | Posting text | Reading |
|---|---|---|---|---|---|---|
| 8299493002 Discord Senior Data Engineer, Ads | dev | relevant | not relevant | relevant | "5+ years of hands-on experience writing production code and architecting data pipelines". Ads/MMP experience is "strongly" preferred, not required. Mentors and leads initiatives | **The only genuine Claude-vs-rule disagreement.** Claude misread the general 5+ years as "5+ years of ad-tech", and v2 didn't fix it, because Claude still treated that as a *minimum requirement* |
| 7858719 Samsara People Analytics AI Engineer | dev | relevant | not relevant | not relevant | "8+ years of relevant experience", "This Staff AI Engineer role" | **Labeling error**: the hand label conflicts with the labeling rule (more than 5 years, Staff). Claude and the rule are right by that rule |
| 7917475 Samsara Senior AI Data & Analytics Engineer II | held-out | relevant | not relevant | not relevant | "8+ years of experience in data engineering, analytics engineering…" | **Labeling error**: more than 5 years. Claude and the rule are right by the rule |

The rule judge's own misses: 7812407 (dev, it passed a "Senior Software Engineer" requiring 5+ years of backend SWE, which the labeler rejected), 8244449 (held-out,
"HR Analytics"), plus the same two labeling-error postings in the other direction. The dev labels were **not** corrected after seeing Claude's answers. Doing so
would have used model output to edit the answer key.

## What I conclude

Did my change help?

No. I added one sentence telling Claude not to reject a posting just for missing domain experience (like ads), unless the posting lists it as a minimum. v1 and v2 gave the same verdicts on all 20 postings (8/10 on dev, 9/10 on held-out). So all I can say is the change didn’t break anything.

Why it didn’t work

I wrote it for the Discord Senior Data Engineer (Ads) posting, but v2’s reasoning showed I’d aimed at the wrong problem. Claude was still reading “5+ years writing production code” as “5+ years in ad tech” and treating it as a minimum, so my exception applied anyway. It wasn’t domain bias; Claude was misreading the requirement. Next I’ll try having it quote the exact phrase from the posting.

What the misses showed me about my labels

Two of Claude’s three misses were really mine. The People Analytics AI Engineer and Senior AI Data & Analytics Engineer II postings both ask for 8+ years, and one is a Staff role, so my own rule says not relevant. Claude and the rule judge got them right. I’d labeled them relevant because my first pass went by job titles. I left those labels alone, though, since changing them after seeing Claude’s answers would mean letting the model fix my answer key.

How much ten cases can show

Not much. One posting swings the score by 10 points, the two prompts never disagreed, and it’s all one labeler, one persona, one model, one day. On this set, Claude matched my labels about as often as the rule did. Its one real miss came from misreading a requirement, which the validator can’t catch, because it only checks format, not truth.

## Honest limits

- 10 cases per split: one posting = 10 percentage points. A v1→v2 change of 1–2 postings is within what re-running
  the *same* prompt can produce (see the sampling report's flip rate).
- One labeler (me), one persona, seven boards, one day, one model.
- The dev and held-out sets are not balanced (see above), so their pass rates aren't directly comparable.
- Pass = agreement with *my* label. If my labeling rule is wrong, a high pass rate means Claude agrees with my mistake. Here the reverse showed up too:
  2 of the 3 Claude misses were my labels breaking my own rule, so the true agreement with the *rule as written* was higher than the scores show.
- v1 and v2 produced identical verdicts on all 20 postings, so this experiment can't show that the change did anything. It shows only that it didn't break anything.
