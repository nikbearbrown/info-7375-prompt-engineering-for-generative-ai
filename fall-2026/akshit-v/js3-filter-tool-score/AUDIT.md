# The reject audit (Chapter 7)

> Claude Code drafted this file from the committed reports it cites. The hand verdicts are mine. The lines marked **My view** are left for my own words.

## What was audited, and how

- **Corpus:** every posting my agent collected. That is the JS2 saved responses of 2026-11-10 plus a new live run on 2026-11-24, merged by id: **714 postings** (figma 163, spotify 110, snowflake 441). The 404 board is reported as "no data: I cannot tell" in both runs. Source: `out/corpus/manifest.json`, with sha256 values for every raw response.
- **Filter:** FILTER.md **v1.0**, written and committed before any JS3 code (`0e4173c`). It kept **25 of 714** and rejected 689. A second method that imports nothing from `agent3` recomputed every score and verdict and agreed on 714 of 714 (`out/recompute/`).
- **Sample:** drawn by script with seed `20261124` from the v1.0 verdicts, and committed before any label (`d6225f6`, `out/audit/sample_v1.0.json`).
  - 30 random rejects;
  - 10 closest calls (scores 5–7: 4 below the threshold, 4 above, 2 more);
  - 10 random kept postings;
  - a sealed held-out set of 15 rejects + 15 kept or close calls.
- **Hand verdicts:** I labeled all 80 on a blind sheet (`scripts/label_server.py`) that showed no score, verdict, set, or Claude output. Labeled 2026-11-25, 03:04–03:46 UTC, and committed before any computation (`30eddc9`).
- **The answer key changed after labeling. Read this before any number below.** Claude Code flagged that 44 of my 48 `relevant` labels conflict with the labeling rule I had adopted from JS1 (`labels/label_flags.md`): sales and pre-sales roles, Staff/Manager/Principal titles, 8+ years, and notes like "partial match". Of three options, I chose to **change the definition to fit the labels**. Claude drafted the wording from my notes and I accepted it (`labels/LABELING_RULE.md`, dated entry; `48fc3f9`). In short: relevant means the posting's technical skills overlap Jack's skills, fully or in part, whatever the job family or title level. Not relevant: non-technical work, internships, not full-time, or clearly more experience than 5 years.
  - **No label was changed.**
  - By Claude's reading, the new definition still contradicts **15 of the 80 labels** (19%, listed in `labels/label_noise.md`). That noise is inside every number below.
  - Consequence: the filter's F2 disqualifiers and F4 role words encode a stricter standard than my labels. Many "errors" below are postings the filter rejects *because* of rules written for the stricter standard.

## Results (v1.0, my labels as labeled): `out/audit/report_v1.0_audit.md`

| Set | Wrong | Rate (95% exact interval) |
|---|---:|---|
| 30 random rejects (labeled relevant, filter rejected) | **12** | 40% (23%–59%) |
| 10 closest calls | 5 | 50% (19%–81%) |
| 10 random kept (labeled not relevant, filter kept) | **0** | 0% (0%–31%) |

### What a sample of 30 rejects can honestly say

- **The error rate among rejects is somewhere between about 23% and 59%.** 12 of 30 is the point estimate. Scaled to all 689 rejects, between roughly **156 and 409** postings I would label relevant are among them. Thirty draws cannot narrow that further.
- **The rate is only as good as the labels.** 15 of the 80 labels contradict the definition they're scored against. **6 of the 12 reject errors are in the noise list**: #12, #32 and #78 (8+ years), and #35, #54 and #60 (selling, partner development, product management). So the error rate under a consistently applied definition is **not established** by this audit. It could be much lower.
- **0 of 10 kept were wrong.** That's still consistent with up to 31% of kept postings being wrong. Ten draws can't rule that out.
- **A random sample misses rare kinds of error.** A kind of reject that makes up 3% of rejects has a 40% chance (0.97³⁰) of not appearing in 30 draws at all.
- **What it does show:** the 12 reject errors are not near-misses. **11 of them score 0–3** (the threshold was 6; the twelfth scores 5), so no small change to the rules reaches them. They differ from the filter on *what counts as relevant*, not on borderline keyword counts.

> **My view:** ____________

## False friends: words that matched for the wrong reason

Every match below was read in its own context (`out/audit/report_v1.0_audit.md` gives 70 characters each side; the corpus-wide scan is in the commands in README).

| Word | Rule | What it matched | Evidence |
|---|---|---|---|
| **`Snowflake`** | F6 (skill) | The **employer's name**, not the skill, on Snowflake's own board | It appears in 382 of 603 postings collected on Nov 10. The JS1 rule kept 45 Snowflake postings because of it, mostly Solution Engineer, Support, and Auditor roles. Measured *before* v1.0, guarded by F6, and caught by wrong version WV1. |
| **`streaming`** | F5 T5 (topic) | **Music and audio streaming** at Spotify | **9 of the 10** Spotify postings where T5 counted. Three of them are the same boilerplate sentence: "the world's most popular audio **streaming** subscription service". Others: "the digital music landscape and **streaming** platforms", "programming music for **streaming**, TV, radio". Flagged as a watch item in v1.0. |
| **`orchestration`** | F5 T4 (topic) | Coordinating people or programs, or compute control planes, not data workflows | "thrive on **program orchestration**" (Product Marketing Manager), "ensure seamless **resource orchestration**" (Activation Solution Engineer), "compute **orchestration**/control plane" (Engineering Manager) |
| **`data warehousing`** | F5 T2 (topic) | The **product being sold**, not the work | 6 labeled postings matched it, only **1** of them labeled relevant. Example: "sales strategies … within one of the following spaces **Data Warehousing**, Business Intelligence" (Account Executive) |

**What changed because of them:**
- `Snowflake` is guarded (F6).
- `streaming` (C3) and `orchestration` (C4) guards were measured and **rejected**: neither changed a single verdict among 714 postings, nor agreement on the 50 audit labels. Both remain **unguarded false friends in v1.2**. They inflate the reasons the score gives, not its verdicts, and the shortlist's claims are built on those reasons.
- `data warehousing` was found while writing this file and was **not measured as a rule**.

A false friend in my own tooling: `scripts/label_flags.py` first flagged #49 for people management because it matched "direct reports" in "**no** direct reports". Fixed before the flags were committed.

> **My view on the false friends:** ____________

## Every rule added, cut, or rejected after measuring

Each was measured alone against v1.0 on the **50 audit labels** (`out/experiments/candidates_v1_1.md`). The held-out set was not read for these.

| Rule | Decision | Audit agreement (v1.0: 33/50) | Corpus effect |
|---|---|---|---|
| **C2** punctuation may sit between a phrase's words ("data-quality", "Data & Integration"). Found by the second-method recompute. | **added → v1.1** | 34 (+1) | 1 of 714 verdicts changes |
| **C1** cut Staff/Principal/Director/Manager/Head of from F2 | **rejected** | 33 (+0) | kept 25 → 32, adding postings no label checked |
| **C3** `streaming` only as data streaming | **rejected** | 33 (+0) | 0 change |
| **C4** `orchestration` only as workflow orchestration | **rejected** | 33 (+0) | 0 change |
| **Threshold 6 → 5** (a setting; fitted on the audit labels: 3 and 5 tied at 37/50, and the tie was broken toward the hand-set 6 by a rule written before the fit) | **adopted → v1.2** | 37 (in-sample) | kept 26 → 61 |

**After the changes (v1.2):**
- On the audit labels, which v1.2 was fitted on, so these numbers are optimistic: random rejects 11/30 wrong, close calls 2/10, kept 0/10.
- **On the held-out 30, never used for designing a rule:** v1.0 14/30 → v1.1 14/30 → **v1.2 21/30** (95% interval 51%–85%). See WHAT_MOVES_THE_SCORE.md.
