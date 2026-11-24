# AUDIT.md: the reject audit (Chapter 7)

Every row, with my verdict and reason, is in `audit/audit-table.md` (generated). This file says what was done and what
the numbers can and cannot show.

## 1. What ran

| Step | When (UTC) | What | Evidence |
|---|---|---|---|
| Filter v1 on everything collected | 2026-11-24 | 2,576 postings (JS2 day-2 corpus) → **55 kept, 2,212 rejected, 309 cannot_tell** | `out/v1/summary.json`, `out/v1/decisions.jsonl` |
| Seeded sample drawn | 2026-11-24, before I labeled | seed 7375: 32 random rejects (R), 10 closest calls (N), 10 kept (K), 6 cannot_tell (T), 20 held-out (H) | `audit/sample.json`, commit `44a80ca` |
| My blind labels | 2026-11-24 ~21:15–21:41 | 78 postings, shuffled, filter verdict hidden; "Show to Arya / Not for Arya / Can't tell" | `audit/label-sheet.html`, `audit/hand-labels.json` |
| Labels frozen | right after download | sha256 committed before any comparison | `audit/hand-labels.sha256`, commit `fe8f7e5`; `tests/test_heldout.py` |
| My reasons + corrections | 2026-11-24, in chat, **after** seeing the filter's verdicts | 33 reasons; 11 corrections (1 withdrawn) | `audit/hand-reasons.json`, `audit/hand-label-corrections.json` |

"Closest calls" = the gate-passing postings nearest the threshold: 6 rejected at score 5 and 4 abstentions at
score 6 (A3).

## 2. Results (filter v1 vs my labels)

| Stratum | n | My blind verdicts | v1 wrong (blind) | After my corrections | v1 wrong (corrected) |
|---|---|---|---|---|---|
| R random rejects | 32 | 30 not, 1 show, 1 can't tell | **1** (#32 shown, rejected) + 1 can't tell | 32 not | **0** |
| N closest calls | 10 | 7 not, 3 show | 6 | 10 not | 4 (the 4 A3 abstentions, which I'd reject) |
| K kept sample | 10 | 8 not, 2 show | **8** | 8 not, 2 show | **8** |
| T cannot_tell sample | 6 | 5 not, 1 show | 6 (every abstention I could decide) | 5 not, 1 can't tell | 5 |

### What this sample can honestly say

- **Random rejects: 0 wrong out of 32 (after my corrections), 1 out of 32 blind.** For 0/32, the 95% Wilson interval
  for the false-reject rate is **0% to 10.7%**. For 1/32 it is 0.6% to 15.7%. Applied to the 2,212 rejects, that is
  anywhere from 0 to about 240 postings I would have wanted (blind: up to about 350). **The sample cannot tell
  "the filter never drops a good job" apart from "it drops a couple of hundred".** Good jobs are rare among the rejects (blind,
  1 of 32 random rejects was a Show, and I later corrected it), so a clean random-reject sample is weak evidence. These intervals describe this sample. They are **not measured rates for all
  postings.**
- **Kept: 8 of 10 kept postings are ones I would not show.** The 95% interval for "kept but not for Arya" is 49% to 94%.
  This is the filter's real failure, and the sample is big enough to see it. My main reason was years of experience:
  7 of those 8 ask for 4–10+ years.
- **The two strata answer different questions.** R checks what the filter throws away; K checks what it lets through.
  v1 throws away almost nothing I want, and lets through mostly things I don't.

### My own errors in the audit

I wasn't a perfect judge, and the record shows it:
- **#19 and #45:** I judged against **my own** background ("i thought of my work ex after undergrasd, dashboards and
  sql but for arya it will be a no"), not the persona's. I chose to judge every label as Arya. #45 was corrected; for
  #19 I withdrew the change and kept the blind "not".
- **#32:** I said Show because the location said "London, UK; Remote". The posting's own text says "This role is based
  in our London office" and "hybrid work model of 3 days in the office per week". The word "Remote" came from my JS2
  parser, which appends it when Ashby's `isRemote` flag is true.
- **#16, #56:** I marked "Can't tell" when my own reason ("dont have any of these", "cycersec no ex in that") was a
  clear Not.
- **#37** (no change): I labeled it Show. Its text has no number, only "Extensive years of hands-on industry data
  science experience", so v1 and v1.1 say "I cannot tell" on level (C4), and Claude's baseline said Not. Its near-twin
  posting, `greenhouse:databricks 8546367002` (not in my sample), says outright "It is not intended for internship, new
  graduate, or entry-level applicants". I keep my blind verdict for #37. (Claude first told me that sentence was in #37,
  then corrected itself after checking the text.)
- **A bias I admit:** while labeling I worried that if I said Not to everything, "always not" would beat the filter
  and the work would be "of no use". Asked afterwards whether that made me pick Show where my honest answer was Not, I
  said: "yes a couple of times i did think about that". I can't say which cards. So some of my blind **Show**
  labels may be inflated. 8 of my 10 blind Shows were changed later in chat (#26, #32, #45, #48, #58, #69, #75 to
  Not; #17 to Can't tell); only #37 and #44 stayed Show. I can't tell how much of that was this worry and how much
  was Claude's questions.

The corrections were made after I had seen the filter's verdicts and Claude's questions, so they are **not blind**.
Every result in this folder is reported both ways.

## 3. False friends (words that matched for the wrong reason)

| Word | Where it matched | Why it's wrong | Size |
|---|---|---|---|
| **`agents`** (TOPIC) | Databricks company boilerplate: "rely on the Databricks Data + AI Platform to build and scale data and AI apps, analytics and **agents**" | it scores the company, not the job (#41 "Data+AI Workforce Transformation Practitioner", #49 "AI Transformation Leader") | the boilerplate sentence is in **914 of 914** Databricks postings; `agents` was counted as a TOPIC point in 878 Databricks and 149 of 155 Notion postings (Notion's source sentence not checked) |
| **`evaluation`** (TOPIC) | #2 "from discovery to initial **evaluation** through deployment"; #48 "risk reporting, independent **evaluation**, and incident reporting" | a sales stage, and AI legislation, not building evals | counted as a TOPIC point in 455 postings; not measured how many of them mean model evaluation |
| **`AI`** (ROLE) | #51 "Transformative **AI** Research Economist" (needs a PhD in Economics); #42 "Regulatory Counsel, **AI** Regulation" | the job is *about* AI, not building it | the ROLE word gives +4, so one false match nearly passes the threshold alone |
| "internship" (in my C5 evidence code) | `greenhouse:databricks 8546367002`: "not intended for **internship**, new graduate, or entry-level applicants" | my code labeled C5 "full-time" contradicted; the sentence is about level, not employment type | 1 kept posting in v1.1 |

## 4. Rules added, cut or rejected after measuring

All candidates were measured on the 58 audit labels (dev) only; I chose v1.1 from those results; v1.1 was committed
(`810ee17`) before the held-out 20 were scored. Full table: `SCORE.md` §2.

| Rule | Decision | Measured (dev, corrected labels) |
|---|---|---|
| G6: reject if smallest stated years > 3 | **added** | 41 → 47 of 58 |
| years pattern reads "8 or more years", spelled-out numbers | **changed** | 41 → 41 (no decision changes alone; needed by G6) |
| US city names count as US (G1, A2, C3) | **added** | 41 → 45; corpus cannot_tell 309 → 27 |
| TOPIC word `agents` | **cut** | 41 → 43 |
| TOPIC word `evaluation` | considered, **not adopted** (not measured as its own change) | — |

v1.1 on the whole corpus: **46 kept, 2,505 rejected, 25 cannot_tell** (`out/v1.1/summary.json`).

**Not re-audited:** I did not draw a new random-reject sample for v1.1. v1.1 rejects about 290 more postings than v1,
and nothing here checks what those are.
