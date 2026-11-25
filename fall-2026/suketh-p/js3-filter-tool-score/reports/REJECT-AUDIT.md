# The reject audit (Chapter 7): FILTER.md v0.1 against the student's hand verdicts

Claude Code drafted this report on 2026-11-24 from the committed records. The verdicts and their reasons are the student's: 80 postings, judged by the student outside the labelling page and pasted in chat at about 19:13 EST. They are kept as pasted in [`labels/hand-labels-as-pasted.tsv`](../labels/hand-labels-as-pasted.tsv) (commit `1589c6ee`). Asked who chose them, the student picked "All mine". The option, as Claude Code worded it: "I read each posting and chose every verdict and wrote every reason myself, outside the page." The page's own download at 18:51 held no labels.

## What was audited

- **The filter.** FILTER.md v0.1 ran on all 1,551 postings collected on 2026-11-24 at 22:36Z ([`audit/v0.1/`](../audit/v0.1/SUMMARY.md)). It kept 41, held 1 for review and rejected 1,509. That record was committed (`ee7cf9e9`, 17:51) before any posting was labelled.
- **The sample.** 80 postings were drawn once, with seed 20261124, from that record ([`labels/v0.1-sample.json`](../labels/v0.1-sample.json), `5de6a6bf`, 17:54). The page showed each posting without its score, fate or group. Claude Code did not show any fate in chat before the labels came in. Whether the student opened the committed audit view while labelling was not recorded.
- **The labels.** The student's legend: "Yes means the posting is worth showing Alex for review. Can’t tell means the work fits and the posting leaves early-career fit unresolved." The count was 5 Yes, 62 No and 13 Can’t tell.
- **Which rows.** This report uses the **50 development rows** ([`audit/v0.1/DEV-COMPARISON.md`](../audit/v0.1/DEV-COMPARISON.md)). The 30 held-out rows were compared with the filter once, after the student had chosen the change ([`ONE-CHANGE.md`](ONE-CHANGE.md)). When the student pasted the table, Claude Code saw all 80 reasons, and the paste did not say which rows were held out. Every proposal below cites development rows only.

**Outcomes.**
- Agree: Yes when the filter kept the posting or held it for review, or No when it rejected it.
- False inclusion: No, but the filter kept the posting or held it for review.
- False exclusion: Yes, but the filter rejected it.
- Can’t tell rows are never scored.

## The 30 random rejects

| | |
| --- | ---: |
| Drawn at random from | 1,494 rejects (all 1,509 minus the 15 held out) |
| The student said No | 30 |
| The student said Yes, so the filter was wrong | **0** |
| Can’t tell | 0 |

**How many were wrong: 0 of 30.**

**What that number can honestly say:**
- **It is a sample, not a rate for all rejects.** With 0 of 30, the exact 95% interval (Clopper–Pearson, `jobwatch/measure.py`) runs from **0% to 11.6%**. That interval covers the share of the 1,494 rejects the student would have wanted to see. As many as about 173 of them could be wrong, and a random 30 could still turn up none.
- **The held-out rejects agree, but only as a later check.** The 15 held-out rejects were also drawn at random and labelled in the same sitting, and all 15 were No. Seen only after the one held-out run, the 45 together give 0 of 45, an interval of 0% to 7.9% (up to about 119 of 1,509). No rule was changed because of this.
- **The 30 are mostly the easy part of the filter.** 19 of them have no engineer or developer in the title. The other 11 all have a level word such as senior or staff in the title. So the sample checks the role and level rules. It says little about the score boundary, which is what the close calls are for.
- **Everything here rests on one person's labels.** They were made once, in one sitting, with no second labeller, about one snapshot of three boards on one day.

## The closest calls

The close calls are 5 postings one point under the cutoff and 5 at it. The one-under pool was the 56 rejects that pass role and level, score 1, and are not outside the U.S. The at-cutoff pool was the 14 kept postings with score exactly 2.

| ID | Where | Title | Fate (score) | Label | Outcome | The student's reason |
| --- | --- | --- | --- | --- | --- | --- |
| P29 | one under | Software Engineer, Business Technology | rejected (1) | No | agree | The role supports business technology and lists 6+ years building production software. |
| P30 | one under | Associate Forward Deployed Engineer | rejected (1) | Yes | **false exclusion** | The role explicitly says early-career and involves production AI and data work in the U.S. It lists 2+ years and points recent graduates to internship openings. |
| P48 | one under | AV Engineer, Builds and Design | rejected (1) | No | agree | The work focuses on enterprise audiovisual systems and lists 8+ years in that discipline. |
| P54 | one under | Developer Relations, Platform | rejected (1) | No | agree | The role centers on developer relations and helping developers adopt the platform. |
| P78 | one under | Research Engineer, Chip Design RL | rejected (1) | Can’t tell | — | The role applies RL research to chip design and asks for prior ASIC or FPGA design and chip tapeout experience. The hiring level is unspecified. |
| P16 | at the cutoff | Research Engineer / Research Scientist, Tokens | kept (2) | Can’t tell | — | Large-scale ML systems fit the search. “Significant software engineering experience” leaves the level unclear. |
| P22 | at the cutoff | Research Engineer, Finetuning | kept (2) | Yes | agree | The U.S. role centers on model fine-tuning and evaluation. Its minimums focus on demonstrated ML and software engineering work. |
| P37 | at the cutoff | Software Engineer, Model-to-Product Behavior Engineering | kept (2) | Can’t tell | — | LLM evaluation fits. The minimum calls for end-to-end production ownership, and the posting lists 5+ years as preferred. |
| P57 | at the cutoff | Research Engineer / Scientist, Alignment | kept (2) | Can’t tell | — | The work centers on ML research. “Significant” engineering experience leaves the hiring level unclear. |
| P72 | at the cutoff | Research Engineer, RL Engineering | kept (2) | Can’t tell | — | The role builds RL training systems. Its minimums call for large-scale training or supporting infrastructure experience, with the hiring level unspecified. |

**What the close calls show:**
- **The student is unsure exactly where the cutoff falls.** Half of the close calls (5 of 10) are Can’t tell.
- **Of the 5 the student decided, 4 agree with the filter.** The one error is P30, the posting the student called Yes because it "explicitly says early-career".
- **Why v0.1 missed P30.** Its title has no topic word. Its description talks about "Data & AI solutions", but FILTER.md's description topics have no phrase for that, and a lone mention of AI earns nothing on purpose (wrong version 3).

## The kept sample

The kept sample is 10 postings drawn at random from the 22 kept or review postings left after the held-out and cutoff draws.

| ID | Title | Score | Label | Outcome | The student's reason |
| --- | --- | ---: | --- | --- | --- |
| P03 | Security Data Engineer | 3 | Can’t tell | — | The role builds data pipelines for data center security. It asks for prior production ownership and leaves the hiring level open. |
| P20 | Applied AI Engineer, Beneficial Deployments, Life Sciences (Molecular Design) | 3 | Can’t tell | — | The role applies AI to life sciences and seeks hands-on drug development experience. The posting leaves the hiring level open. |
| P25 | Software Engineer, Research Tools | 2 | No | **false inclusion** | The research tooling fits the topic, and the posting describes a full-stack engineer with 5+ years of experience. |
| P44 | Applied AI Engineer, Commercial | 3 | No | **false inclusion** | The commercial advisory role asks for 4+ years of technical experience and production LLM application work. |
| P46 | Applied AI, Research Engineer | 3 | No | **false inclusion** | The Applied AI Research Engineer role describes a candidate with 6+ years in technical roles. |
| P49 | AI Engineer – Forward Deployed Engineering (AI FDE) | 3 | No | **false inclusion** | The posting explicitly places new graduates and entry-level applicants outside its intended audience. |
| P56 | Applied AI Engineer, Public Sector | 3 | No | **false inclusion** | The minimums include 4+ years, active TS/SCI clearance with polygraph, and prior intelligence-community work. |
| P64 | Performance Engineer, Inference Systems | 3 | Can’t tell | — | Inference systems fit the search. The posting asks for hands-on performance work on complex production systems and leaves the level open. |
| P71 | Applied AI Engineer, Startups (Physical AI) | 3 | No | **false inclusion** | The posting asks for 4+ years of technical experience and deep hardware engineering experience. |
| P77 | Software Engineer, Research Productivity | 2 | Can’t tell | — | Research infrastructure fits. The posting asks for independent delivery of complex production projects and leaves the level open. |

**What was wrong:**
- **None of the 10 got a Yes.** 6 got No and 4 got Can’t tell. For 0 Yes out of 10, the exact 95% interval for the share of Yes among those 22 postings runs from 0% to 30.8%.
- **Five of the six No reasons name a minimum stated in the description.** P25 asks for 5+ years, P44 for 4+, P46 for 6+, P56 for 4+ plus a clearance, and P71 for 4+.
- **The sixth, P49, rules out new graduates.** Its posting says the role "is not intended for internship, new graduate, or entry-level applicants".
- **v0.1 never reads experience in a description.** Its level rule reads titles only, by the student's design: "a senior colleague mentioned in the description has no effect." That is the gap v0.2 addresses.

## Two false friends (the student named both)

### 1. "machine learning" in a description

FILTER.md gives a generic title one point for a description topic, and `machine learning` is one of the phrases. That point decided 7 of the development postings: P16, P22, P25, P37, P57, P72 and P77, each kept at exactly 2 (role 1 + description 1). In 6 of the 7, the phrase appears only in what a candidate should bring: requirements, preferred qualifications or interests. In one, P57 ("You want to build and run elegant and thorough machine learning experiments"), it describes the work.

- **P25, Software Engineer, Research Tools.** The only match is "Background in machine learning, AI research, or working closely with ML researchers", under the heading "Strong candidates may also have". The student: "the posting describes a full-stack engineer with 5+ years of experience." A nice-to-have background matched as if it were the job. P25 is a false inclusion.
- **P16, Research Engineer / Research Scientist, Tokens.** The match is "Want to learn more about machine learning research", under "You may be a good fit if you". An interest matched as if it were the work. The student labelled P16 Can’t tell ("Large-scale ML systems fit the search"), so the topic may still be right. The match was right for the wrong reason.

### 2. "ai" in an Applied AI title

`ai` is a title topic worth 2 points, inherited from JS1's focus terms. In the corpus, 62 titles contain "Applied AI", and v0.1 kept 7 of them.

- **In the kept sample, four Applied AI titles got No.** These are P44, P46, P56 and P71. P20 got Can’t tell.
- **Claude Code's reading: in these titles "Applied AI" names the team, not the topic of the work.** The student's P44 reason calls it "The commercial advisory role". Two Applied AI Architect titles came up among the random rejects. The student wrote that P23 "seeks technical customer-facing candidates with 10+ years" and called P47 "a technical sales management role". The word matched as if the posting were AI engineering work.
- **Caveat: the word did not decide those No labels.** The student's reasons for P46, P56 and P71 name years of experience, not the customer-facing work; the stated minimums decided them. v0.2 rejects all four for those minimums, and keeps 1 of the 62 Applied AI titles.

## Every rule added, cut or rejected after measuring

The measurements come from the 50 development rows. The student chose; Claude Code worded the options (FILTER.md, "After the reject audit, before any held-out label was scored"). "Wrong keeps" means false inclusions, "wrong rejects" means false exclusions, and "reaching" counts kept plus review across all 1,551 postings.

| Rule | Development effect (v0.1 → with the change) | Decision |
| --- | --- | --- |
| **Add:** reject a description that sets a minimum of 3+ years not marked preferred | Wrong keeps 6 → 1 (P25, P44, P46, P56 and P71 now rejected); no Yes lost; reaching 42 → 28 | **Added** as v0.2, the one change |
| Cut `ai` from the title topics | Wrong keeps 6 → 3 (P44, P46, P71); P20 (Can’t tell) moves to rejected; reaching 42 → 36 | Offered; the student did not choose it |
| Add early career, new grad, new graduate, recent graduate to the description topics | Wrong rejects 1 → 0 (P30); reaching 42 → 44 | Offered; the student did not choose it |
| No change | — | Offered; the student did not choose it |
| Cut `machine learning` from the description topics | Wrong keeps 6 → 5 (P25); 5 Can’t tell postings move to rejected; reaching 42 → 26 | Measured by Claude Code, not offered: it rejects more postings that the student said fit the work than the errors it fixes |
| Reject a description that says it is "not intended for … new graduate … applicants" | Wrong keeps 6 → 5 (P49); reaching 42 → 41 | Measured by Claude Code, not offered: it fixes one posting |

- **How the options were counted.** For the experience rule, the counts the student saw came from a quick regular-expression count before any code. After the rule was coded test-first (`d9f5a96e`), the same five development rows changed and no other row did ([`audit/v0.2/DEV-COMPARISON.md`](../audit/v0.2/DEV-COMPARISON.md)). The rows for the experience rule, cutting `ai`, the early-career phrases and cutting `machine learning` are reproduced from committed variant files by `python3 -m jobwatch.js3 dev-effect runs/2026-11-24-js3-corpus --sample labels/v0.1-sample.json --labels labels/hand-labels.json variants/v0.2-experience-minimum.json variants/candidates/*.json` ([`evidence/terminal/2026-11-24-dev-effect.txt`](../evidence/terminal/2026-11-24-dev-effect.txt)). The "not intended for new graduates" row was a regular-expression count in Claude Code's session, which no committed command reproduces.
- **Nothing was cut from v0.1, and nothing changed after the held-out run.**

## What this audit does not show

- **Whether the student's labels are right.** There is one labeller and no second opinion. The reasons above are the record.
- **A rate for other days, other boards or the whole corpus.** Every interval above is about one pool on 2026-11-24.
- **Whether Can’t tell postings should reach Alex.** They are left out of every score here, as the student chose for the held-out score.
- **Anything about the shortlist's claims.** Those are labelled separately (`shortlist/v0.1/`).
