# SOURCES: what was used, and who made what

| Item | Source | Who |
|---|---|---|
| Assignment text | `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` (course repo) | Instructor |
| Starting point | My JS1, `../js1-contract-and-watch/` (commit `97732e4`) | Omkar (decisions) + Claude Code (code), per JS1's SOURCES |
| `agent/rule.py`, `agent/persona.py` | Copied **byte-identical** from JS1 `jsagent/` (sha256 `18079b26…`, `73ca1945…`) | JS1 |
| `persona/aarav-patel.example.json` | Copied unchanged from JS1, which copied it from the Reallocation Engine examples. **Fictional**: `@example.com`, 555 numbers | Course repo |
| ATS endpoints; the `hubspotjobs` slug trap; Webflow listed as Greenhouse with 27 postings (2026-09-26) | Instructor's Lectern, `fall-2026/nik-bear-brown/lectern/ATS.md`. **Read only; no code copied** | Instructor |
| Lever endpoint shape (`api.lever.co/v0/postings/{slug}?mode=json`) | Lectern ATS.md "Systems Lectern can read" table, then confirmed with `curl` on 2026-11-09 | Instructor / Claude Code |
| Job postings | Public endpoints of Klaviyo, HubSpot, Webflow (Greenhouse), Linear, Webflow (Ashby), Spotify (Lever). Read-only GET, no login, a small number of requests per run. The raw bodies are saved in `runs/*/raw/` as evidence | Those companies |
| TA feedback used | Earlier TA comments on my Week 1, Recipe and Pitch Film work (read from Canvas 2026-10-21): "your log mostly records Claude's work"; do the "yourself" items yourself. **Canvas was signed out on 2026-11-09, so no JS1 comments were read for this assignment** | TAs |
| GATE.md (all six sections) | Drafted from the assignment text before any code, 2026-11-09 08:01 UTC | **Claude Code** proposed; **[Omkar] to confirm** (GATE.md "Omkar's decisions") |
| POLICY.md boundary cases and predictions | Written 08:01 UTC, before `policy.py` | **Claude Code** |
| `agent/policy.py`, `transport.py`, `store.py`, `ats.py`, `loop.py` | Written 2026-11-09 08:02–08:09 UTC | **Claude Code** (Opus 5.5, in the Claude desktop app) |
| `verify/independent_check.py` | Written 2026-11-09 | **Claude Code** |
| All tests, constructed fixtures, mutants, `run_mutants.py` | Written 2026-11-09 | **Claude Code** |
| The review-packet change (choice, test, patch v1, revision v2) | REVIEW-PACKET.md | **Claude Code**. Decision **Omkar** (2026-11-10) |
| The drop rule (second review) | GATE.md change log 2026-11-10; REVIEW-PACKET.md "Second review" | Rule decided by **Omkar** (Claude Code asked the questions and offered options); test, code and mutants W11–W13 by **Claude Code**; Omkar ran the checks and made the decision |
| TRACE.md, WRONG-ANSWER.md, README, FRICTIONAL Part 2 | Written from the run files | **Claude Code** |
| Sign-off "Not checked" | README | **Omkar**, in his own words (2026-11-10), replacing Claude Code's draft |
| Sign-off "Not claiming" | README | **Claude Code** drafted; **Omkar** kept it |
| Sign-off "Checked/How", signature, driver's-seat "why", FRICTIONAL Part 1, GATE confirmation, review decision | — | **Omkar** (2026-11-10) |

**Claude responses shown:** none. This agent never calls Claude, and no model output appears anywhere in JS2. Every number in these files comes from a program run whose output is saved.
