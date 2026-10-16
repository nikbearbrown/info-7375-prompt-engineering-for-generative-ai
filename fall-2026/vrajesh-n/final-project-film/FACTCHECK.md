# FACTCHECK — every figure and claim on screen or in the narration

Status: checked 2026-10-14 by Vrajesh Nasit with Claude Code. PASS = verified against the named source; EXEMPT = planned or constructed and labelled so on screen; CORRECTED = wording changed after a check. "Real" = measured today; "planned" = future work; "constructed" = illustration.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Kind |
|---|---|---|---|---|---|
| 1 | B00 | Graduating December 2026, job hunting now | PASS | my enrolment (MSIS, Sep 2024 – Dec 2026) | real (self) |
| 2 | B01 | 25–30 companies on my list | EXEMPT | my private list; not shown, not committed | planned |
| 3 | B02 | Probe ran 2026-10-14 against Commure, Stripe, Figma, Databricks, Palantir | PASS | `evidence/probe.py`, `evidence/2026-10-14/*.json` | real |
| 4 | B02 | 80 / 725 / 144 / 895 / 312 postings; 2,156 total | PASS | `evidence/2026-10-14/summary.json` | real |
| 5 | B02 | 34 / 161 / 37 / 362 / 195 naive keyword matches | PASS | same file; rule is the `ROLE` regex in `probe.py` | real |
| 6 | B02 | 5 boards, 3 platforms (Ashby, Greenhouse, Lever) | PASS | `BOARDS` in `probe.py` | real |
| 7 | B03 | greenhouse-watch watches one board per run, keeps only postings above a résumé-keyword score | PASS | the-reallocation-engine `.claude/skills/greenhouse-watch/SKILL.md` + `scripts/greenhouse_watch.py` (commit `80a44c8`, read 2026-10-14) | real (read) |
| 8 | B03 | Its demo: 11 new Figma postings in four days, 0 kept | PASS | `fall-2026/nik-bear-brown/greenhouse-watch-demo/README.md`, "The two-day watch" table | real (read) |
| 9 | B03 | greenhouse-watch can be re-run and checked (deterministic, fixtures, saved responses) | PASS | same README, "How to reproduce it" | real (read) |
| 10 | B03 | LinkedIn Job Match compares a profile with a posting's qualifications; only LinkedIn postings | PASS | Social Media Today launch coverage (SOURCES.md) | real (secondary) |
| 11 | B03 | LinkedIn: "can't re-run how it decided" | PASS | no public method or re-run is documented in the coverage I read | my judgment |
| 12 | B03 | "5+ years required" quote check | EXEMPT | labelled `example` on screen | constructed example |
| 13 | B04 | `python -m earlybird run --fixtures` and its output | EXEMPT | labelled CONSTRUCTED · not built yet | constructed |
| 14 | B05 | 20 hand labels, 10 held out | EXEMPT | JS1 prompt-experiment requirement | planned |
| 15 | B06 | Google uses its own hiring system (unsupported) | CORRECTED | 2026-10-14 14:23 UTC: `boards-api.greenhouse.io/v1/boards/google`, `api.lever.co/v0/postings/google` and `api.ashbyhq.com/posting-api/job-board/google` all returned HTTP 404 (slug `google` only; other slugs untested) | real (checked) + planned behaviour |
| 16 | B06 | run IDs 101–105 | EXEMPT | labelled "IDs illustrative" | constructed |
| 17 | B07 | 789 of 2,156 titles matched a keyword | PASS | `summary.json` (34+161+37+362+195 = 789) | real |
| 18 | B07 | "Account Executive, AI Sales" (Stripe), "Accounting AI Solutions Lead" (Stripe) and the other four titles | PASS | `summary.json` → `sample` fields | real |
| 19 | B08 | Python + FastAPI services (Duma Info Services; Market-Data-Service repo) | PASS | my resume (kept private); public repo github.com/Vrajesh-works/Market-Data-Service | real |
| 20 | B08 | Screenr filters reposted job listings | PASS | public repo github.com/Vrajesh-works/Screenr (last commit 2026-04-02) | real |
| 21 | B08 | Wave Life Sciences intern: LangGraph assistant, Claude Code testing agents | PASS | my resume; that code is private to the employer | real (resume only) |
| 22 | B09 | Voice is synthetic | PASS | Kokoro `am_onyx`, disclosed in B00 and B09 | real |

No users, employers' metrics, testimonials or results are claimed. Resume metrics (savings, coverage percentages) were deliberately left out because the film cannot show their evidence.

## Corrections made during the check
- B06 Google: first written as "does not appear" with no check run; checked (HTTP 404 x3) and narrowed to the slug tested.
- B03 Jobright: an earlier script line ("an award the user never won") overstated an unverified Reddit report; removed from the film.
