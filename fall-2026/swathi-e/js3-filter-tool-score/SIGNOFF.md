# Sign-off — Job-Search Agent 3

Swathi Baba Eswarappa, 2026-11-20.
Claude Code compiled the Checked, Not checked and Not claiming lists below
from the committed records; I reviewed every row. The driver's seat is my
text, written with ChatGPT reference drafts that I revised, reviewed and
approved (see `SOURCES.md`). My decision is my own.

"How" uses three kinds of check:
- **By me:** my own observation or judgment (Swathi).
- **AI-assisted:** a check where an AI tool did part of the work, named.
- **Automated:** a test or script whose result anyone can rerun.

## Checked (which property, by which test)

| Property | Test / evidence | How |
|---|---|---|
| The filter applies FILTER.md's rules R1–R7, the score numbers and the evidence rules | `tests/test_job_filter.py`: R1a–R1b, R2a–R2e, R3a–R3b, R4a–R4c, R5a–R5l, R6a–R6e, R7a–R7b, SC1–SC7, E1–E5, D1–D6, U1–U2, O1. Tests and predictions `5024095`, before the filter code `6e6b4bf` | Automated. Claude Code wrote the tests from my FILTER.md and recorded predictions before the code |
| My six "wrong versions" are caught | W1 (false friend "training"), R6b (export-control paragraph), W3 (title-only rule on 8 real Plaid postings), R5c ("0-2 years"), E4 (missing description is "I cannot tell"), E3 (no sponsorship sentence is "insufficient") | Automated |
| The v1.1 rule changes do what the change log says, and nothing else broke | R5f–R5l, R6d, R6e, U1, U2 (tests `bb08b32`, `bf291f2`, before the code `2c3ef12`); all 113 tests pass, W3 unchanged | Automated; rule decisions by me, discussed with Claude Chat and Claude Code |
| Reject audit: 30 random rejects, close calls and every kept posting judged by hand | `audit/HUMAN_AUDIT.csv` (`fed055f`), 48 rows against `AUDIT-RULE.md`; sample drawn by `make_audit_sample.py` (seed 20261117) | By me. Rows 1–4 before seeing a ChatGPT-assisted draft; rows 5–48 after seeing it. Not blind |
| What the 0/30 result can and cannot show | `audit/AUDIT-REPORT.md` §A: rule-of-three bound 3/30 = 10% (Clopper–Pearson 9.5%), for the rejected pool only | Automated recomputation by Claude Code from the committed files |
| Every shortlist claim is labeled against the posting text | `shortlist/CLAIMS.csv` (`f4dadb2`): 21 claims, 17 supported, 4 insufficient, 0 contradicted | By me, with Claude Chat and ChatGPT feedback on R6 and R3. Claude Code checked values, exact quotes and unchanged columns, and changed nothing |
| One change at a time, on held-out labels | Threshold 5 → 6; 20 labels committed before any filter run (`b09f9ce`); `measure_heldout.py` (`698efbb`) | By me (labels; row 1 after consulting ChatGPT, rows 2–20 independent). Automated measurement |
| The saved results can be recomputed | On 2026-11-20, `run_filter.py` and `measure_heldout.py` in a scratch copy reproduced every verdict and score; only the recorded FILTER.md hash differed (FILTER.md gained a change-log line in `e8299de`) | Automated, run by Claude Code |
| The tool server does what its contract declares | `tool/tests/test_server.py`, 42 tests: P1–P11, N1–N5 (all 1,832 postings), E1–E9, A1–A5, X1–X3, R1–R3, B1–B6. Written before the server (`ae93c19`, `bdaf8ac`); before 40 FAIL / 2 ERROR, after 42 OK (`de027ed`) | Automated. Claude Code wrote the tests from the contract I decided |
| Observed file access matched the declared boundaries during the tested adversarial session | B2: Python audit hook over an adversarial session (one read of the results file, one new transcript, no network, process, remove or rename events) | Automated (it observes, it does not confine) |
| A real client can use it, and a path trick fails at the server | `tool/transcripts/2026-11-20T18-21-07-980276Z-9425.jsonl` (`4fd59d6`): `server/discover` → -32601 → `initialize` 2025-11-25; lines 10–11, `../../etc/passwd` rejected by the server | By me (I ran the Claude Code session and approved the second call in manual mode). AI-assisted: Claude Code inspected the transcript |
| No blocking privacy findings in the three protocol transcripts | `tool/privacy_scan.py` (`c4be37b`): 0 blocking hits on all three transcripts | Automated, run by Claude Code before each commit |
| The Filesystem server 2.4.0 package is the published one, and contains the GHSA-7m4x-rv66-mxhh fix | SHA-512 equal to the registry's `dist.integrity`; `dist/pinned-directory.js:338–442` (`tool/EVALUATION.md` §2) | Automated (hash). AI-assisted: code reading by Claude Code. Not run |

## Not checked

- **Labels that are not blind.** Rows 5–48 of the audit were reviewed after
  seeing a ChatGPT-assisted draft, Row 35 was adjudicated after seeing the
  filter's prediction, and held-out row 1 was labeled after consulting
  ChatGPT. Where a draft and the filter share a mistake, the audit may not
  detect it (`audit/AUDIT-REPORT.md` §F).
- **The threshold trade-off.** The held-out sample had no relevant posting
  and no scored posting, so whether threshold 6 would miss relevant postings
  was not measured (`heldout/EXPERIMENT-REPORT.md`, Limitations).
- **Requirements outside R1–R7.** No rule reads a graduation window, a degree
  deadline or a start-by date. Both Databricks shortlisted postings ask for
  graduation in fall 2026 or spring 2027, which Priya's December 2025 degree
  falls outside (`shortlist/SHORTLIST.md`).
- **Known rule gaps left open.** City-only US locations ("SEA", "Chicago"),
  a "preferred" inside a parenthesis, the "University Recruiter" title,
  degree ladders and "2-3 full year experience" (`audit/AUDIT-REPORT.md` §G).
- **The corpus-scan counts** in the audit report were pattern matching, not
  hand-verified posting by posting.
- **Tool server gaps.** No test forces an internal error (-32603); the
  rate-limit counting details are not tested; one Claude Code version on
  one day; no OS sandbox (`tool/EVALUATION.md` §1.4).
- **The Filesystem server was never run.** Its dependencies were not
  audited, its provenance attestation was not verified, and no race was
  tested (`tool/EVALUATION.md` §2.5).
- **Permission prompts are not recorded.** The auto-mode and manual-mode
  behavior of Claude Code is my testimony only; the MCP transcript has no
  record of it.

## Not claiming

- I am not claiming the agent finds jobs that fit Priya. All four
  shortlisted postings are "needs human check", and none establishes visa
  sponsorship or F-1 OPT eligibility.
- I am not claiming the shortlisted roles match Priya's primary targets; R1
  is broader than her targets file.
- I am not claiming an error rate for all 1,832 postings. 0 of 30 random
  rejects is a sample result for the rejected pool only.
- I am not claiming v1.1 is better than v1 on new postings. v1.1 was built
  from the same batch and audit it was compared on.
- I am not claiming threshold 5 is the right threshold, only that the
  held-out sample could not tell 5 and 6 apart.
- I am not claiming my labels are independent or blind where AI feedback
  was involved.
- I am not claiming anything was trained. The behavior persists because of
  files (FILTER.md, code, tests, saved runs), not model learning.
- I am not claiming my tool server is secure beyond its tests, or that it is
  sandboxed.
- I am not claiming the Filesystem server is safe. Its evaluation was code
  reading only.

## Driver's seat

| Task | What Claude should do | What I should do | Why that part stays mine (my words) | Evidence |
|---|---|---|---|---|
| The filter and its rules | Help me turn the candidate requirements into filter rules, spot tricky edge cases, write the implementation and tests, and measure how changes affect the results. | Decide which rules actually reflect Priya’s requirements, approve or reject proposed edits, and judge whether there’s enough evidence to justify a rule change. | Claude can propose logic and run metrics, but I’m the one deciding what truly counts as a relevant job for the persona—and I’m responsible if a bad rule drops good roles or lets irrelevant ones slip through. | FILTER.md `0f689b8` and change log `4a6dcfb` |
| Judging whether a posting is worth my time | Pull out key details from job descriptions, highlight requirements, surface exact quotes, and flag anything missing or ambiguous. | Read the actual posting, weigh whether it fits Priya’s profile, verify the quoted evidence, and make the final call without assuming silence means eligibility. | A posting can hit all the right keywords and still be a bad fit once you look closely at experience, graduation dates, or sponsorship rules. Deciding whether a role is worth applying to takes human judgment, so I shouldn't hand that off to Claude. | `audit/HUMAN_AUDIT.csv`, `heldout/HELDOUT.csv`, `shortlist/CLAIMS.csv` |
| The tool server and trusting a server | Help build the server, write and run tests, check protocol transcripts, surface security issues, evaluate whether what the server declares matches its observed behavior, and identify anything that remains unverified. | Decide what tools and capabilities the server can expose, approve its access boundaries, review the audit findings, and choose how much trust to give it. | Passing tests or following the MCP spec doesn’t automatically make a server safe to trust. Before letting a tool interact with my files or environment, I need to know what it can reach, what’s been verified, and what hasn’t been tested yet. | `tool/TOOL-SERVER.md`, `tool/EVALUATION.md` §1.5, §2.6 |

## Signed

Signed: Swathi Baba Eswarappa, 2026-11-20.
