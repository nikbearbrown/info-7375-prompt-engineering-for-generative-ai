# Sources

JS2's sources are in [js2/SOURCES.md](js2/SOURCES.md) and JS1's in [js1/SOURCES.md](js1/SOURCES.md); what they list still
applies to the code JS3 builds on.

## How the work was split

**Mine:**
- FILTER.md Section 1: the rules R1 to R8, the topic words and the ranking, in four drafts on 2026-11-20
  ([filter-drafts/](filter-drafts/)). After each draft, Claude Code checked my rules against the code and the saved
  postings and told me what was wrong or unclear, and I rewrote them.
- The decision, after my 6:39 AM run on 2026-11-20, that one posting with no title should be "I cannot tell" on its own
  instead of hiding its whole board.
- Every label: 55 audit verdicts, 30 held-out verdicts and 105 claim labels, judged blind and committed before any answer
  was opened; my answers after the reveals (card 17 and the four flip checks); my change of claim 09.6 before its freeze.
- The three calls in FILTER.md v1.1: a cutoff of 50, 10 points off for an export-control line, and no "build systems".
- My own test (`tests/test_aravind_own_rule.py`: the case and the expected result), which I ran myself, and my
  recomputation of the audit's and the claims' results.
- Both trust decisions, in my own words.
- My notes for the Frictional entries and for the sign-off and driver's seat.
- Asking Claude Code, on 2026-11-20, to decide the rest of FILTER.md itself ("decide yourself whatever is best for this
  agent").

**Claude Code's, at my request:**
- FILTER.md Sections 2 to 7 (the evidence rules, the expected sources, the wrong versions, the failure sentence and the
  shortlist's claims, the implementation choices, the machine-readable copy), drafted from my Section 1, the brief and
  chapter 7 and labeled as its own; in v1.1, the two implementation changes and the text around my calls.
- The code: the filter engine and its run (`job_agent/filter.py`, `job_agent/filter_run.py`), the reader fix for a
  posting with no title, the audit, held-out and claims kits, the card fix, the scorers, the held-out experiment tool,
  the MCP server, client and live-run script, every test except mine, and the planted mistakes.
- The reports: the filter runs' reports, the RESULTS.md files, ABSTENTION.md, ORIGINS.md, CHANGES-TO-MEASURE.md with its
  predictions, EXPERIMENTS.md, the drafts of both MCP evaluations, js3/mcp/README.md, this file and README.md.
- Running everything: the filter runs, the kits, the scoring, the held-out measurement, the live Claude Code MCP call
  (2026-11-21) and the planted mistakes.
- Showing me the cards and claims in chat, entering my verdicts and labels (my letters unchanged, my reasons tightened
  to one line, my messages kept word for word outside the repo), finding the sentence behind each claim disagreement,
  and organizing my notes into FRICTIONAL.md and js3/SIGNOFF.md, as the Frictional guide allows ("AI can organize your
  notes; you must supply the actual experience").

## What I used

- The JS3 brief, `assignments/assignment-js3-the-filter-the-tool-and-the-score.md` in the course repository, and the
  grading pages it links: the Frictional guide, GitHub posting and Relative Quartile.
- The course book: chapter 7 (relevance versus entailment, supported and insufficient, "label each row yourself first"),
  chapter 8 (MCP from scratch: the lifecycle, protocol version 2025-11-25, the four ledgers, the evidence types,
  "discovery is not consent to call") and chapter 9 (a held-out set is touched once; persistence is not proof of
  training).
- The Model Context Protocol specification, version 2025-11-25 (modelcontextprotocol.io), its lifecycle and tools pages,
  read for the server and the evaluations.
- The course's lesson 8 reference server (`lessons/08-mcp-from-scratch/code/main.py` at `5639e4c8`, MIT license), copied
  byte for byte into `js3/mcp/other-server/` to evaluate it; it was never connected to Claude.
- Contract v0.2 (CONTRACT.md, JS1): R5's status phrases are inherited from it unchanged.
- The course repository's Lectern filter, read by Claude Code for the shape of a reject audit and a rule ledger; no code
  was copied.
- Two classmates' JS3 folders on the course repository's main branch, read by Claude Code on 2026-11-20 to see what the
  brief's parts look like in practice; nothing was copied.
- The board answers that JS2's loop saved on 2026-11-20 from the public job-board endpoints of OpenAI (Ashby), Verkada
  (Greenhouse) and Palantir (Lever).
- Python's standard library, and the Claude Code CLI 2.1.326 as the MCP client in one live run.
