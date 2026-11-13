# FACTCHECK — every figure and claim on screen or in the narration (film v1.0)

Status: checked 2026-10-24 by Vrajesh Nasit with Claude Code. PASS = verified against the named source; EXEMPT = planned or constructed and labelled so on screen; CORRECTED = wording changed after a check. "Real" = measured from saved files; "planned" = future work; "constructed" = illustration.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Kind |
|---|---|---|---|---|---|
| 1 | B00 | Graduating December 2026, job hunting now | PASS | my enrolment (MSIS, Sep 2024 – Dec 2026) | real (self) |
| 2 | B00 | Script drafted with Claude from my decisions; synthetic voice | PASS | SOURCES.md "Claude contributions"; Kokoro `am_onyx` | real |
| 3 | B01 | 25–30 companies on my list; Greenhouse, Lever, Ashby | EXEMPT | my private list; not shown, not committed; labelled PLANNED | planned |
| 4 | B02 | Commure board saved 2026-10-14 and 2026-10-23 | PASS | `evidence/2026-10-14/ashby_commure.json`, `evidence/2026-10-23/ashby_commure.json` (copies of `js1-contract-and-watch/data/raw/…`; the 10-14 copies are byte-identical, MD5 `6e790dc4…`) | real |
| 5 | B02 | 80 postings, then 81 | PASS | `evidence/commure-new-ids-2026-10-14_to_2026-10-23.txt` (my run, 2026-10-24), first line `80 81` | real |
| 6 | B02 | 12 new IDs, 11 gone (69 in both) | PASS | same file, `new: 12 gone: 11`; 81 − 12 = 69 = 80 − 11 | real |
| 7 | B02 | 5 of the 12 are software engineering | PASS | all five titles "Senior Software Engineer, …", department `Engineering` (department table in the same file) | real |
| 8 | B02 | 7 are not software: sales, marketing, design, one partnerships role | CORRECTED | Sales ×2, Marketing team ×2, "Growth Marketing Lead" (G&A), Design ×1, "Manager, Strategic Partnerships" (Corporate). First draft said "sales, marketing and design"; the partnerships role fits none, so the line was changed | real |
| 9 | B03 | I ran greenhouse-watch on the same two snapshots with the course's sample resume | PASS | `evidence/gw/2026-10-14/` (baseline) and `evidence/gw/2026-10-23/` (run): run records, reports, raw copies; resume `search/examples/aarav-patel/resume.example.json` (fictional) | real (my run) |
| 10 | B03 | It found the same 12 new postings | PASS | `evidence/gw/2026-10-23/run-*.json`: `jobs_new` 12; titles match #5 | real |
| 11 | B03 | It kept 6: all 5 software + Head of Performance Creative | PASS | same run: `jobs_relevant` 6; the report lists the five SWE titles (scores 7.8–9.5) and Head of Performance Creative (3.5) | real |
| 12 | B03 | Head of Performance Creative kept because the posting mentions Python and SQL (and is remote) | PASS | report "Why it is here": Python +1.0, SQL +1.0, skill_any +0.5, remote +1.0 = 3.5 ≥ threshold 3.0 | real |
| 13 | B03 | Titles on screen shortened ("Sr.", "Rev. Ops", "Infra.", "Rep.") | EXEMPT | labelled "titles shortened" on screen; full titles in #5 | display |
| 14 | B03 | greenhouse-watch watches one board per run, keeps postings over a résumé-word score | PASS | `--board` is one required argument; `scheme default-0.1 · threshold 3.0` in the report | real (read + run) |
| 15 | B03 | LinkedIn Job Match covers LinkedIn postings; I can't re-run how it decided | PASS | Social Media Today launch coverage (SOURCES.md); no public method or re-run documented in what I read | real (secondary) + my judgment |
| 16 | B03 | Early Bird: whole list, software job decided from the role, keeps every one, quotes blockers | EXEMPT | labelled PLANNED | planned |
| 17 | B03 | "5+ years required" quoted blocker | EXEMPT | labelled `example` | constructed |
| 18 | B04 | `python -m earlybird run --sample` and the three steps | EXEMPT | labelled CONSTRUCTED · not built | constructed |
| 19 | B05 | 20 hand labels, 10 held out | EXEMPT | labelled PLANNED; JS1 prompt-experiment requirement | planned |
| 20 | B06 | Google: own hiring system → unsupported | PASS | 2026-10-14 14:23 UTC: Greenhouse, Lever and Ashby endpoints for slug `google` all HTTP 404 (other slugs untested) | real (checked) + planned behaviour |
| 21 | B06 | The 12 ID prefixes on the answer-key card | PASS | first 8 characters of the 12 new IDs (department table in the diff file) | real |
| 22 | B06 | First watcher must report exactly these 12 | EXEMPT | labelled planned | planned |
| 23 | B06 | greenhouse-watch also found 12 | PASS | #10 | real |
| 24 | B07 | "Sales Strategy & Operations, Agents" is a sales job | PASS | department `Sales` (diff file) | real |
| 25 | B07 | 789 of 2,156 titles matched the probe's keyword rule, five boards | PASS | `evidence/2026-10-14/summary.json`: 34+161+37+362+195 = 789; 80+725+144+895+312 = 2,156 | real |
| 26 | B07 | "Account Executive, AI Sales" at Stripe | PASS | `evidence/2026-10-14/summary.json` → `greenhouse:stripe.sample` | real |
| 27 | B08 | Python + FastAPI services (Duma Info Services; Market-Data-Service repo) | PASS | my resume (private); github.com/Vrajesh-works/Market-Data-Service | real |
| 28 | B08 | Screenr filters reposted job listings | PASS | github.com/Vrajesh-works/Screenr (last commit 2026-04-02) | real |
| 29 | B08 | Wave Life Sciences intern: LangGraph assistant, Claude Code testing agents | PASS | my resume; that code is private to the employer | real (resume only) |
| 30 | B09 | Script drafted with Claude; synthetic voice | PASS | as #2 | real |

No users, employers' metrics, testimonials or results are claimed. Resume metrics were left out because the film cannot show their evidence.

## Corrections made during the check
- B02: "seven were sales, marketing and design" → "seven were not software: sales, marketing, design, and one partnerships role" (department check, 2026-10-24).
- B03: the v0.2 film said greenhouse-watch "kept none" (its own Figma demo). On my Commure run it kept all five software roles, so the film now reports my run, not the demo.
