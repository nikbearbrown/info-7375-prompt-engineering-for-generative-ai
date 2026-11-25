# FACTCHECK — SponsorScout, Final Project Film (v2)

Every claim spoken or shown, checked against a file or a source. `A1/` = Assignment 1 repository
`the-reallocation-engine` at `a1d321f`. `SUB/` = `A1/course/2026fa/submissions/AkshitVerma-AV/`.
`BR/` = `../board-resolver/`. `LIVE/` = `BR/runs/live-2026-11-23/`.
Checked by Claude Code on 2026-11-23.

Status: claims checked by Claude Code 2026-11-23. **Signed off by Akshit Verma, 2026-11-23**: "Sign off the fact check", after watching the film (his FRICTIONAL Entry 4: "I also checked the film…"). Recorded by Claude at his instruction. Row 29's 9-in-10 threshold approved by Akshit Verma, 2026-11-23: "approve the 9 in 10 threshold".

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | BOPEN | "SponsorScout. A final project film by Akshit Verma, in four parts." | PASS | Author; the four parts are the assignment's own structure. "By", never "I am": the voice is synthetic (Kokoro `am_michael`), disclosed in README/SOURCES | — |
| 2 | P1A | Many sponsors have no entry-level data job open today | PASS | run-2 (`SUB/runs/run-2/network-targets.md`): of the 16 sponsors with a board, 13 SKIP + 1 NETWORK had no live entry-level data posting; only 2 APPLY | — |
| 3 | P1A | "only some employers sponsor visas"; "a short clock" | EXEMPT | General context, not a measured claim (OPT time limit; sponsorship is the employer's choice) | — |
| 4 | P1B | Verdicts apply / network / check by hand / skip, with the public record behind every answer | PASS | run-2 report: four buckets; every value labelled `[record]` / `[your-input]` | — |
| 5 | P1B | "A strong sponsor with nothing open … goes on a networking list" | PASS | run-2: NETWORK 1 (Outset Medical: proven sponsor, scorer 0, recent Form D) | — |
| 6 | P1C | "It never applies, emails, or contacts anyone. The person decides." | PASS | Prototype has no send path (A1); resolver: GET only, three hosts (`BR/resolver.py` `check_policy`) | — |
| 7 | P1C | "I'm job hunting too … smarter strategy than a hundred-plus applications a day" | PASS | Akshit's own reason, given 2026-10-14 (pitch film FACTCHECK row 25) | — |
| 8 | P2A | "My Visa Jobs lists sponsors and their past job counts; I looked at it in October" | PASS | Akshit looked on 2026-10-07 (pitch film FACTCHECK row 8) | — |
| 9 | P2A | "H one B Grader grades employers on past approvals and denials" | PASS | Web search by Claude, 2026-11-23: h1bgrader.com employer pages ("evaluates and grades every company based on … USCIS approvals, denials"). Not looked at by Akshit, so the narration doesn't say "I looked" | — |
| 10 | P2A | "Interstride, which universities provide, shows sponsorship history and filters jobs by visa" | PASS | Web search by Claude, 2026-11-23: university career-centre pages (e.g. career.cornell.edu, 2025-02-06: Visa Insights, H-1B sponsorship history, filter by visa type) | — |
| 11 | P2B | Engine scorer "which I had Claude Code run in October" gives a sponsor with no open job a zero and skips it | PASS | `SUB/runs/engine-baseline/role-scores.md` (2026-10-03): composite 0.000, Skip | — |
| 12 | P2B | "None that I found turns a proven sponsor with nothing open into a networking target" | PASS | Scoped to what was found: MyVisaJobs (Akshit, 2026-10-07), engine scorer (run), H1BGrader and Interstride descriptions (rows 9–10). Not a claim that no such tool exists | Worded "that I found" |
| 13 | P3A | Data: sponsorship records from the 80 Days to Stay file; SEC Form D; Greenhouse, Lever, Ashby public job boards; job seeker fictional | PASS | A1 prototype README and run-2 "Data used"; persona Jack Spencer (`@example.com`) | — |
| 14 | P3B | Three checks (sponsored data roles, recent funding, entry-level data job open today) set the verdict | PASS | `A1/.../network_targets.py`; run-2 | — |
| 15 | P3B | "The prototype ran on October third, on one hundred twenty-three sponsors" | PASS | run-2 executive summary: 123 candidates, 2026-10-03 | — |
| 16 | P3C | "only sixteen of them had a known job board, so most answers were check by hand" | PASS | run-2: 16 confirmed boards; MANUAL-CHECK 107 | — |
| 17 | P3C | "with Claude Code, I built a board resolver" | PASS | `BR/` (2026-11-23): Claude Code wrote CONTRACT, tests and code at Akshit's direction (`../FRICTIONAL.md` Entry 2) | Says "with Claude Code" |
| 18 | P3C | Tries name-derived slugs, one request at a time, saves every raw response with a fingerprint, stops on done / budget / errors | PASS | `BR/resolver.py` (`slug_candidates`, `HttpTool`, `Run.probe_one`, stop reasons); `LIVE/raw/`, `LIVE/log.jsonl` | — |
| 19 | P3D | "It only proposes. I approve or refuse each board … tied to the fingerprint of the response I saw" | PASS | `BR/resolver.py` `cmd_decide` (hash check, exit 7); `LIVE/decisions.json`: 44 decisions signed "Akshit Verma" (13 typed by Akshit; 31 typed by Claude at his instruction, each noted) | — |
| 20 | P3D | "It can only read from those three sites, and it has no way to send anything" | PASS | `check_policy`: GET, https, three hosts; `LIVE/log.jsonl`: 629 GETs, all to those hosts | — |
| 21 | P3D | On-screen fingerprint `c50b5646d54e` | PASS | `LIVE/decisions.json`: ANAPLAN INC, greenhouse/anaplan, seen_sha256 starts `c50b5646d54e` | — |
| 22 | P3E | "Claude Code, free public job boards, no keys, and no paid compute" | PASS | Resolver and prototype: standard-library Python; public APIs without keys; local Kokoro/Manim; $0.00 | — |
| 23 | P4A | 2026-11-23: 629 requests, all to the three allowed sites; candidate boards for 39 companies | PASS | `LIVE/summary.json` (requests_used 629, stop done); `LIVE/log.jsonl` hosts; `LIVE/proposals.json`: 38 proposed + 1 mismatch-only = 39 | — |
| 24 | P4A | "After my review, coverage went from sixteen to fifty, of one hundred twenty-three" | PASS | `LIVE/coverage.json`: covered 50, total 123 (16 + 34 approved; 5 refused) | — |
| 25 | P4B | Five boards belonged to other companies (e.g. a childcare centre); Claude flagged them; all five refused | PASS | `LIVE/raw/greenhouse/talent.json` ("Slice Talent Community"), `village.json` ("The Village Learning Center … shape little minds"), `lever/plume.json`, `ashby/sail.json`, `lever/sila.json`; `LIVE/decisions.json`: last decision refuse ×5 | Akshit first approved them, then refused them (`../FRICTIONAL.md`); the film states the final decision |
| 26 | P4B | Name check called Weight Watchers a mismatch, though it's the right company | PASS | `LIVE/proposals.json`: WW INTERNATIONAL INC → greenhouse/ww, outcome name-mismatch, board "Weight Watchers"; raw content "Weight Watchers is a global digital health company"; approved at G1 | — |
| 27 | P4B | "Five approved boards are empty, and sixty-seven companies showed no board under the names it tried" | PASS | `LIVE/proposals.json`: exists-empty for Affinity, DocuSign, Freshworks, Lua, Zanbato (all approved); status not-found 67 | — |
| 28 | P4C | On a Windows console the command saved the approval, then crashed; a test reproduces it; all 28 tests pass | PASS | `../FRICTIONAL.md` Entry 2; `BR/test_resolver.py` `TestConsoleEncoding` (failed before the fix); `python -m unittest test_resolver` → 28 OK (re-run 2026-11-23) | — |
| 29 | P4D | Held-out set set aside before tuning; pass if ≥ 9 in 10 apply verdicts right; 14-day re-check; can't show anyone gets hired | EXEMPT | Proposed plan (tag "proposed"), not a result. The 9-in-10 threshold was drafted by Claude and **approved by Akshit, 2026-11-23** | — |
| 30 | all | Corner tags and part chips | EXEMPT | Disclosure and structure labels; every drawing is constructed in `scenes.py` | — |
