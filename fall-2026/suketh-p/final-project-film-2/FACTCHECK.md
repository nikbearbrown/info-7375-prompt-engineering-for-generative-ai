# FACTCHECK — every factual sentence in the script, and the record behind it

Drafted by Claude Code on 2026-11-21. Paths are relative to this folder. **Tense** says what the sentence claims:
*did* (it happened), *is* (true now), or *will* (the plan). A *will* sentence needs no evidence of success, only that it
is clearly marked as the plan (spoken in future tense, with a `constructed · not built` stamp).

Status: checked 2026-11-21 by Claude Code and by an independent fact-check subagent (a separate Claude Code subagent; 10 findings: 9 fixed, marked CORRECTED above, and 1 already moot). Draft film approved by the student, Suketh Reddy Produtoor, on 2026-11-21 ("Approve it"). PASS means the record supports the sentence as spoken; for *will* sentences it means the sentence is clearly a plan.

Records used:
- **A3**: `../Assignment 3/the-reallocation-engine/course/2026fa/submissions/sukethrp/POSTING-REVIEW.md`
- **A4**: October's pitch film, `../Assignment 4/final-project-film/` (`PROJECT-BRIEF.md`, `FRICTIONAL.md`,
  `evidence/linkedin-check-2026-10-14.md`) and `../Assignment 4/WORKING-NOTES.md`
- **JS1**: the fork at `99a7443`, `fall-2026/suketh-p/js1-contract-and-watch/` (`README.md`, `SOURCES.md`). Commits
  `29b3a26` (the student's `CONTRACT.md`, "before any code") and `546fd7a8` (the first agent code).
- **JS2**: the clone at `9c1db18`, `work/jobwatch/fall-2026/suketh-p/js2-loop-tools-diff/` (`README.md`, `GATE.md`).
  Commit `b55d2a5` is the student's `GATE.md`, "before any code".
- **RUN**: today's captures in `evidence/terminal/` (hashes in `SHA256SUMS`), plus the clone's
  `runs/film-normal-noapproval-2026-11-21/results.md`
- **CANVAS**: the student's screenshots of the Canvas Assignments list, shared in chat on 2026-11-21 at 18:34 EST
- **CHAT**: the student's answers in this conversation, 2026-11-21

| Beat | Claim | Verdict | Source / record | Tense |
|---|---|---|---|---|
| BIDEA | I'm an international student on F-1, looking for new-grad ML roles | PASS | The student's choices on 2026-10-13: "Say I'm on F-1", target role new-grad ML/AI (A4 `WORKING-NOTES.md`, Decisions) | is |
| BIDEA | Before I tailor an application, I need to know whether this posting rules me out | PASS | The student's own words, pitch §7: "I want to know whether a role deserves my time before I tailor an application" (A4 `PROJECT-BRIEF.md`) | is |
| B01 | A recipe Claude Code and I built screened eight real postings for a fictional new grad, by title and sponsor record. *Picture:* no sponsor ticks, because only four of the eight had a sponsor tier (AppLovin and Nextdoor Proven; Moloco and Databricks Likely; PathAI Unknown; Scale AI, Anthropic and OpenAI had no row: A3 `WORKED-RUN.md`) | CORRECTED | A3 `POSTING-REVIEW.md`. October's narration: "Claude Code and I built a recipe". The applicant is fictional (Arjun Rao, no work history) | did |
| B01 | When an AI reviewer read them in full, six asked for 2 to 12+ years of experience, or excluded new graduates. The reader was Codex, an AI reviewer; Claude re-checked the same day (A4 `WORKING-NOTES.md`, Verified facts) | CORRECTED | A3 `POSTING-REVIEW.md` (AppLovin ≥4, Nextdoor ≥5, Moloco ~5–12+, PathAI master's + 2–4 or PhD + 0–2, Anthropic ≥6, Databricks excludes new grads). Same wording as October's film. *Nuance:* PathAI's PhD path allows 0–2 years; for a master's-level new grad it asks 2–4 | did |
| B02 | Fine Print will read each new posting, show the exact sentence behind each requirement, and wait for approval | PASS | DESIGN §6; pitch §1. Nothing of it is built | will |
| B03 | In under two weeks, the three boards showed 172 postings that weren't in my November eighth snapshot | CORRECTED | RUN `film-normal-noapproval-2026-11-21.txt`: new = 83 + 88 + 1. The baseline is the Nov 8 state (`2026-11-08-normal-1`, 11:17 UTC); today's run started 2026-11-21 23:43 UTC, 13.5 days later. "Snapshot" is the saved Nov 8 state. Some of the 172 may be reposts: the fact-checker found 81 of the 171 Greenhouse ids are lower than an id already listed on Nov 8 | did |
| B03 | One piece of Fine Print already runs: the watcher | CORRECTED | RUN (tests and live run). Changed from "half" after the fact-check: none of B02's three capabilities exists yet | is |
| B04 | My first try matched on title and sponsor record and couldn't tell fit | PASS | A3; pitch §2 | did |
| B04 | LinkedIn, Qualcomm and TikTok: both separate minimum and preferred; neither stated sponsorship | PASS | The student's own check: A4 `evidence/linkedin-check-2026-10-14.md`, written by the student | did |
| B05 | Government H-1B data counts an employer's past approvals and denials, not what a posting asks for | CORRECTED | PRIOR-ART: the USCIS H-1B Employer Data Hub has "data on the first decisions USCIS makes on petitions …", queried by fiscal year, employer name, city, state, ZIP and NAICS code (the hub page; accessed 18:43 ET). Job title is not a query field. "Not what one posting asks for" describes what the data is (petition decisions per employer), not a missing feature | is |
| B05 | Jobscan scores a résumé against a posting and lists missing keywords | CORRECTED | PRIOR-ART: Jobscan's homepage and tutorial describe a match rate and missing keywords (accessed 18:44–18:45 ET) | is |
| B05 | One paper flags whether experience and education are required or preferred | CORRECTED | PRIOR-ART: Thakrar & Young, arXiv 2501.07663 (Jan 2025). The full text flags whether experience is required, and whether education is required or preferred. Confidence medium (a course practicum, scored against another LLM's output) | did |
| B05 | A 2024 study found language models find skills but miss their exact wording | CORRECTED | PRIOR-ART: Nguyen, Zhang, Montariol & Bosselut, NLP4HR 2024. The abstract says LLMs were "not on par" with supervised models. The arXiv v1 full text says the models locate skills but "fail to capture the exact sequence" | did |
| B06 | Fine Print will put those pieces together. Each requirement will carry the posting's own sentence, checked word for word by code. Required apart from preferred; sponsorship unknown when silent; nothing shortlisted before approval | CORRECTED | DESIGN §6; pitch §2, §4. **Not claimed as new:** required vs preferred (Thakrar & Young do it) and a human review step (Jobscan's Auto Apply: "You review every one before it's sent"). The claim is the combination, for one person's decision | will |
| B07 | In October I planned to build the reader first, and now I can build it on top of jobwatch, which already monitors three job boards | PASS | **The student's own words**, Frictional entry 1 (`FRICTIONAL.md`, 2026-11-21 19:04), used in the narration with the student's agreement ("Sure proceed"). Backed by A4 `FRICTIONAL.md` line 119 (the October plan) and RUN (jobwatch watches three boards) | did / is |
| B07 | Its data comes from public job-board feeds, read only from an allow-list | PASS | JS2 `README.md`: "HTTPS GET only, to the four endpoints in jobwatch/boards.py" | is |
| B07 | Every response is saved, with a fingerprint, before anything reads it | PASS | JS2 `README.md`: "It saves every raw response before reading it"; `verify` checks "the sha256 recorded at retrieval" | is |
| B07 | The applicant is fictional | PASS | JS2 `README.md`: the persona is Alex Morgan (fictional) | is |
| B08 | On Nov 21, Claude Code ran it from a fresh copy; all 164 tests passed | PASS | RUN `tests-2026-11-21.txt` ("Ran 164 tests … OK", exit 0). Clone of `js2-loop-tools-diff` at `9c1db18`. Run by Claude Code | did |
| B08 | A live run read Anthropic, Databricks and Linear and found 172 new postings | PASS | RUN `film-normal-noapproval-2026-11-21.txt` | did |
| B09 | Its word rule, from my first agent, rejected all 172 for the fictional applicant | PASS | RUN `film-rule-count-2026-11-21.txt` (`grep -c not_relevant` → 172) and `film-rule-relevant-2026-11-21.txt` (→ 0). JS2 `README.md`: "screens new postings with JS1's literal rule for a fictional persona" | did |
| B09 | A word rule can't say whether those rejections were right | PASS | An argument, not a measurement. The JS3 brief requires a hand audit of rejects for exactly this reason | is |
| B10 | The run did not save its state because no approval was given; incomplete, state unchanged | PASS | RUN `film-normal-noapproval-2026-11-21.txt` ("the state was not saved: no approval was given"; "state advanced: False"; exit 3). `cmp` of the before and after copies (`evidence/state-*.json`): identical. RUN `film-normal-noapproval-check-2026-11-21.txt`: the independent check PASS | did |
| B10 | On Nov 8, I typed that approval myself, for one run and one file, and only then did it save | PASS | RUN `2026-11-08-normal-1-run-by-student.txt` (copied unchanged from JS2; SHA-256 `63aa9b83…b32b`): "Run by the student in their own Terminal"; `--approve-state 2026-11-08-normal-1:state/state.json`; "state advanced: True" | did |
| B11 | So far, in both job-search agents, I wrote the rules first, before any code | CORRECTED | JS1 `29b3a26` "CONTRACT.md written by the student, before any code" (06:10), first code `546fd7a8` (06:26); JS2 `b55d2a5` "the student's GATE.md … before any code" | did |
| B11 | Claude Code wrote the code, all but five of the tests, and ran most checks | CORRECTED | JS1 `README.md`: all the code, 92 of 93 tests (the student wrote 1), and most runs. JS2 `README.md`: 160 of 164 tests (the student wrote 4); Claude Code wrote the independent checker | did |
| B11 | I ran my own checks, and twice I withheld my sign-off until the record was right | CORRECTED | The student's own checks: the JS1 Terminal test run at `9243e75`, and the `cmp` on JS2 failure-2. JS1: the student withheld the sign-off on 2026-10-31 over overstated drafts, then signed after corrections ("Sign now"). JS2: withheld at `dfe7203` ("the contribution record needs correction"), then signed at `d6ff91b` | did |
| B12 | Dates Nov 25, Dec 1, Dec 13, Dec 20 | PASS | CANVAS (JS3 Nov 25, JS4 Dec 1, JS5 Dec 13, Final Project Dec 20) | is |
| B12 | Reader labels claims supported / contradicted / insufficient, or "I cannot tell" | PASS | JS3 brief, Step 1 (the brief's own terms; the student's `FILTER.md` will define them) | will |
| B12 | Every quote checked against the saved posting by Dec 1 | PASS | Pitch §5 (the quote check); JS4 brief Step 2.1 (each claim gets a check that fails differently). *Mapping to JS4 is Claude's proposal* | will |
| B12 | Approval tied to the exact shortlist by Dec 13 | PASS | JS5 brief, Step 1 ("Bind the approval to a fingerprint of the exact proposal") | will |
| B13 | No API credits | PASS | CHAT: "Only Claude Code" | is |
| B13 | My first agent's judge used my Claude Code login for 27 postings in October | PASS | JS1 `README.md` "What ran", 2026-10-31 08:50: run 2, 27 new, each got a Claude judgment; default `--judge claude-code`; JS1 `SOURCES.md`: the student's NEU Claude Code login | did |
| B13 | Public boards need no accounts; a laptop runs it | PASS | JS2 `README.md` (GET to public endpoints, no login; Python 3 standard library, macOS) | is |
| B13 | Boards can refuse automated reads; usage caps mean a daily reading budget (the budget is the plan; its picture is labelled 'plan') | CORRECTED | A3: OpenAI's Ashby API returned 403 (A4 `WORKING-NOTES.md`, "Verified facts"; pitch §6) | did |
| B17 | It worked if ≥ 27 of 30 held-out decisions match my labels and the checks catch every deliberate failure; it didn't if the reader misquotes, clears one unmet requirement, or wrongly rules out more than one eligible posting; about 60 labelled by hand, including 30 random rejects, 30 set aside before tuning | PASS | **The student's own words**, chat 2026-11-21 (after approving the draft), spoken verbatim except numerals spelled out. It is the student's bar, set before any of it is built | will |
| B14, B15, B16, B18 | The evaluation plan: hand labels, a random sample of rejects, held-out set, four measures, five or more deliberate failures | CORRECTED | Final Project brief ("held-out", "at least five deliberate failure cases", "controlled failure"); JS3 brief (reject audit); pitch §4 | will |
| B16 | The predicted failure: a quote copied word for word, but "five years preferred" treated as a requirement | PASS | **The student's own words**, Frictional entry 1 ("quote a posting word for word and still get it wrong by treating 'five years preferred' as a requirement"); pitch §6 ("a true quote read the wrong way") | will |
| BOUT | Narration: my script, synthesized voice (Kokoro am_eric) | CORRECTED | `film/beat_sheet.json` (`voice`, `engine`); the student's October choice of am_eric | is |

## The independent fact-check (2026-11-21)

A fresh subagent opened each record and checked every sentence of the script. It found 5 must-fix and 5 should-fix
problems. All ten were judged genuine and fixed, except one that was already moot (B07's old wording had been replaced by
the student's own words). The fixes covered:
- B01's picture (sponsor ticks) and who read the postings;
- the outro line ("my script" became "drafted by Claude Code …, approved by me");
- "half" of Fine Print;
- B11's generalization and exact shares;
- B15's "me" (the evaluation uses a fictional applicant);
- B05's wording against its sources;
- B03's "new";
- B13's stamp coverage.

Unchanged and confirmed by the check: the hashes, the identical state copies, 164 tests, 83 + 88 + 1 = 172, 172
rejected, 13.5 days, 27 postings judged on Oct 31, the LinkedIn wording, and the Canvas dates.
