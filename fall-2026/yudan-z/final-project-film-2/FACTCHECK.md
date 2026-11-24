# FACTCHECK — job-search-agent-film

Every spoken claim, checked against a file or a page before rendering (2026-11-23). JS1 = `fall-2026/yudan-z/js1-contract-and-watch`, JS2 = `fall-2026/yudan-z/js2-loop-tools-diff` (commit 47bab91).

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | BIDEA | Narrator is Yudan Zhou, an IS master's student; the voice is synthetic, reading her script | EXEMPT | Self-description; voice = Kokoro `af_heart`, speed 1.08 | — |
| 2 | B01 | The agent reads public job boards, finds new postings, and judges each with the rule that produced the answer | PASS | JS1 `agent/watch.py` (seen ids), JS2 `agent/loop.py`; every verdict carries per-check `reasons` with `evidence` (`runs/live/run-20261110T234346Z.json`) | — |
| 3 | B02 | "hundreds of postings a day" | PASS | Each daily run reads every listed posting: 1,566 on 2026-11-10 across four boards (`runs/live/run-20261110T234346Z.md`) | — |
| 4 | B02 | A missed board can look like a quiet day | PASS | JS2 GATE.md W1 (wrong version: failed board reported "0 new"); the agent reports it as `failed`, run `incomplete` | — |
| 5 | B03 | LinkedIn job alerts: new postings matching a saved search, daily or weekly, by email or in the app | PASS | LinkedIn Help, "Job alerts on LinkedIn" (linkedin.com/help/linkedin/answer/a511279), read 2026-11-23 | — |
| 6 | B04 | Jobright reports skills, seniority and keyword gaps; weighting not published; "a decision aid, not a guarantee" | CORRECTED | jobright.ai/tools/resume-job-matcher (report headings); jobright.ai/ai-job-match ("a decision aid—not a guarantee…"), read 2026-11-23 | Removed "a score from zero to one hundred" (no scale on Jobright's pages) and "its own guide says it is not a hiring probability" (generic blog wording, not Jobright's product page) |
| 7 | B05 | Visa filing databases show past filings, not open jobs | PASS | Pitch film `evidence/` (h1bdata.info LCA filings, 2026-10-13); USCIS H-1B Employer Data Hub is by fiscal year | A sentence naming F1 Hire was dropped: f1hire.com is a closure notice (renamed FrogHire), and its contrast described the earlier project, not this agent |
| 8 | B05 | The sponsorship check reads the posting; the verdict names the phrase it found | PASS | JS2 `agent/rule.py:154` (`no-sponsorship phrases: …`); CONTRACT.md R6 | — |
| 9 | B06 | Three public ATSs (Greenhouse, Ashby, Lever); no login; runs used Pinterest, Databricks, Ramp, Palantir; fictional persona | PASS | JS2 `config/allowlist.json`, `config/boards.json`, `persona/resume.json` (@example.com, 555) | — |
| 10 | B07 | Contract before code, nine checks incl. title (R1), work country (R3), citizenship (R5), sponsorship (R6) | PASS | JS1 CONTRACT.md (commit 077c5e0 before code); R9 added 2026-10-30 | — |
| 11 | B07 | Answers labelled record (rule) or model judgment (Claude) | PASS | JS1 README; `agent/judge.py` + validator. The JS2 loop uses the rule only | — |
| 12 | B07 | Budgets 6 boards / 12 requests / 2 minutes; permission policy in code; never applies, emails or logs in | PASS | JS2 GATE.md §3, `agent/loop.py` LIMITS, `agent/policy.py` NEVER_TOOLS, POLICY.md B01–B19 | — |
| 13 | B08 | Course layers: filter and score (Nov 25), plan, evidence and memory (Dec 1), supervised run (Dec 13), final project (Dec 20) | EXEMPT | Future work; Canvas assignment list seen 2026-11-23 | — |
| 14 | B08 | What I need, I have | PASS | Python 3.14 standard library; public APIs need no key; Claude Code CLI 2.1.314 logged in (JS1/JS2 SOURCES.md) | — |
| 15 | B09 | 87 tests pass, written before the code | PASS | JS2 README; commit order ff7a40c → 14909bd; full suite run 2026-11-10 | — |
| 16 | B09 | A board that does not exist → not found → run `incomplete` | PASS | JS2 `runs/live/terminal-run1.txt`, `terminal-run2.txt` (HTTP 404, exit code 3) | — |
| 17 | B10 | Ramp on the wrong system: finished, 1 job; independent check found 176 on Ashby and flagged it | PASS | JS2 FINISHED-WRONG.md, `runs/wrong-ats/terminal-crosscheck.txt` | — |
| 18 | B11 | More than 1,500 real postings; 364 US jobs rejected for full state names; predictions first; 364 fixed, 0 broken | PASS | JS2 `review/01-reproduce-before.txt` (1,561), `review/02` (tests before patch), `review/12-behaviour-change-after-revision.txt` | — |
| 19 | B12 | Success and failure criteria | EXEMPT | The student's own evaluation standard, chosen 2026-11-23 | Added the lazy-rule baselines after review (a criterion that cannot fail is not a criterion) |
| 20 | B13 | Second real day: 34 new postings, none fit the persona; the relevant path has run only in tests | PASS | JS2 `runs/live/run-20261110T234346Z.md` (34 `not_relevant`), README "Not checked" #2 | — |
