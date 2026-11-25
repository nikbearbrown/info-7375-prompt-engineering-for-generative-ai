# Job-Search Agent 3 — The Filter, the Tool, and the Score (nishant-u)

## What this is

The layer that decides **what reaches Priya, and why**, for one fictional job seeker (Priya Nair, `data/resume.example.json`). It covers Chapters 7–9.

- **A filter you can read** (`FILTER.md`, versions 1 and 2) with four relevance rules, four evidence rules and an abstention rule. It was written before any code and changed only after a measured reject audit.
- **A source-grounded shortlist.** Every claim is labeled supported / contradicted / insufficient against the posting's own text, with the exact quote (`SHORTLIST.md`).
- **A tool server written from scratch** that offers one capability to Claude over the Model Context Protocol message shape: `score_posting(posting_id)`. It has real transcripts, and both it and the course's reference server are evaluated with Chapter 8's four ledgers (`MCP-EVALUATION.md`).
- **An account of what moves the score:** the origin of every number, and one change at a time measured on held-out labels (`SCORE.md`).

Everything runs offline over the 182 unique postings my JS2 loop saved from three boards on 2026-11-10: Greenhouse faire and instacart, and Ashby poshmark. The agent never applies, emails, messages or logs in.

## What I started from

My JS2 agent, branch `nishant-u-js2`, final commit **`f956e22`**. Its committed folder was copied unchanged into this one (commit `adfad6f`): the JS1 rule and contract, the JS2 loop, its saved raw responses and its tests. JS2's README, FRICTIONAL and sign-off are in that commit.

## Language and toolchain

- **Language:** Python 3.12 (tested on 3.12.10), standard library only. Nothing to install.
- **Tests:** `unittest`.
- **Platform:** Windows 11 with Git Bash. Some saved-response paths are long, so clone with `git clone -c core.longpaths=true …`.
- **Optional:** the Claude Code CLI (tested with 2.1.332), only to repeat the one Claude Code MCP run. Nothing else uses Claude or the network.

## Commands

Run from this folder (`fall-2026/nishant-u/js3-filter-tool-score/`).

```bash
# All tests (JS1 + JS2 + JS3): 220 tests, 1 skipped on Windows (the JS2 real-symlink case)
python -m unittest discover -s tests -t .

# The filter over the 182 saved postings (offline)
python -m agent3.run --filter-version 2                      # writes out3/filter-run-v2/ (the default)
python -m agent3.run --filter-version 1 --out /tmp/v1-check   # to reproduce v1 without touching out3/filter-run/

# The blind audit kit (deterministic for the seed). Use --out: the default writes into audit/
# and would overwrite my filled-in audit/audit.csv with the blank kit.
python -m audit.make_kit --seed 20261124 --out /tmp/audit-kit

# The scripted MCP client (each run appends to mcp_server/transcripts/)
python mcp_server/client.py --target js3          # this folder's server
python mcp_server/client.py --target reference    # the course server, lessons/08-mcp-from-scratch/code/main.py

# The one real Claude Code run (optional; needs the Claude Code CLI and an account)
claude -p "Use the score_posting tool to score the job posting greenhouse:faire:8806617002. Report its verdict and reason, then list each claim (C1 to C4) with its label and the exact quote the tool returned. Use only what the tool returned; do not add anything." \
  --mcp-config mcp_server/mcp-config.json --strict-mcp-config --tools "" \
  --allowedTools "mcp__js3-score__score_posting" --output-format stream-json --verbose
```

**Reproducing v1:** re-running v1 reproduces `out3/filter-run/results.json` byte for byte. Its `shortlist.md` now differs from the committed one by a single quote, which the quote fix in `409b995` corrected.

## What actually ran

Every JS3 commit, oldest first. Author: Nishant U. Commits marked * also carry a `Co-Authored-By: Claude` trailer.

| Commit | What it is |
| --- | --- |
| `adfad6f`* | Start from JS2 `f956e22`: an unchanged copy of the committed folder (385 files, byte-identical) |
| `5a6df3f`* | FILTER.md v1, written before any JS3 code |
| `f308043`* | AUDIT-RULE.md, written before any audit sample was drawn |
| `7a0c270`* | 44 tests written from FILTER.md, all failing (`agent3` did not exist yet) |
| `8e759bf`* | `agent3/` filter, shortlist and offline CLI; v1 run: 16 accepted, 166 rejected (F1 144, F2 9, F3 8, F4 5), 0 abstained |
| `096a74c`* | The blind audit kit, committed blank (45 postings, seed 20261124) |
| `b8b0a20` | The reject audit, 45 verdicts in `audit/audit.csv` |
| `b68e605`* | FILTER.md v2: my decisions after the audit (accept 1, 2, 7, 8; reject 4, 5, 6) |
| `79f1dcc`* | 18 tests for v2, failing before the v2 code |
| `fb071b5`* | v2 implemented; v2 run: 23 accepted, F1 144, F2 7, F3 8, F4 0. v1 is still the library default |
| `c67ba2f`* | AUDIT-REPORT.md: comparison, false friends, decisions, v1 vs v2 |
| `409b995`* | Fix: the C2 quote rested on a substring ("SQL" inside "MySQL"), plus a regression test |
| `03ad6d4`* | SHORTLIST.md: entailment cases, abstention counterexample, C3 |
| `d8d45e6`* | SCORE.md: origin of every number; one change at a time on held-out labels |
| `bcf17ad`* | SPLIT.md exposure log: 4 held-out postings were in the audit |
| `7339062`* | The v2 run also writes `shortlist.json` (for the tool server) |
| `b16b973`* | MCP tool server from scratch, with 17 tests |
| `875563e`* | Real MCP transcripts: scripted client (JS3 and reference servers), one Claude Code run |
| `d5882e2`* | MCP-EVALUATION.md draft (four ledgers, two servers) |
| `87b152a` | My trust decisions for both servers |
| `32f95f1`* | Server descriptions changed to match my trust decision |

## Where each required artifact is

| Required | Where |
| --- | --- |
| The filter, versioned, written before the build | `FILTER.md` (v1 at `5a6df3f`; v2 decisions and the Version 2 section below the unchanged v1 text) |
| The evidence rules and expected sources | `FILTER.md` |
| Code | `agent3/filter.py`, `agent3/shortlist.py`, `agent3/run.py`, `audit/make_kit.py`, `mcp_server/server.py`, `mcp_server/client.py` |
| Tests | `tests/test_js3_filter.py`, `test_js3_shortlist.py`, `test_js3_mutants.py` (+ `js3_mutants.py`), `test_js3_run.py`, `test_js3_audit_kit.py`, `test_js3_v2.py`, `test_js3_mcp.py` |
| Run outputs | `out3/filter-run/` (v1), `out3/filter-run-v2/` (v2: `results.json`, `shortlist.md`, `shortlist.json`) |
| The reject audit, with hand verdicts | `audit/audit.csv` (verdicts); the judgment rule in `AUDIT-RULE.md`; the kit in `audit/postings/` and `audit/HOW-TO.md` |
| What the audit can and can't show; false friends; rule changes | `audit/AUDIT-REPORT.md` |
| The source-grounded shortlist and its labels | `SHORTLIST.md` (links `out3/filter-run-v2/shortlist.md`) |
| The tool server and its transcripts | `mcp_server/` (`server.py`, `client.py`, `mcp-config.json`, `transcripts/`) |
| The Claude Code run, with date and session ID | `mcp_server/CLAUDE-CODE-RUN.md` |
| Both server evaluations and trust decisions | `MCP-EVALUATION.md` |
| What moves the score | `SCORE.md` |
| Sign-off and driver's seat | this README, below |
| Sources and what Claude contributed | `SOURCES.md` (written by me) |
| Honest log | `FRICTIONAL.md` |

## Sign-off

```text
Sign-off — Job-Search Agent 3
Checked:      FILTER.md written before any code (5a6df3f); F1–F4, C1–C4, abstention and missing fields
              (test_js3_filter, test_js3_shortlist); the four wrong versions are caught (test_js3_mutants);
              the v2 changes (test_js3_v2); the run is offline, deduplicated and deterministic (test_js3_run);
              the audit kit is deterministic and shows no filter reasons (test_js3_audit_kit); the MCP
              server's lifecycle, error codes, path refusal and no-network imports (test_js3_mcp); quotes
              rest on whole-word matches (regression test, 409b995); v1 reproduces byte for byte.
How:          by hand: TODO-NISHANT (write this yourself).
              Tests written before the implementation: 7a0c270 (44 tests, all failing before agent3
              existed) and 79f1dcc (v2 tests failing before the v2 code), written by Claude Code from my
              FILTER.md. By recomputation: the v1/v2 comparisons and the Clopper-Pearson intervals. With
              Claude's help: the code, the tests, the report drafts and the MCP ledgers; the rule decisions
              and both trust decisions are mine.
Not checked:  v2 on a fresh sample (the fix counts come from the same 45 that suggested the changes);
              the 136 unjudged rejects; the C1–C4 labels by hand (they are computed); boundary symlink case
              on Windows; the MCP server with other clients or the older protocol versions it claims;
              Ashby's isRemote and workplaceType fields (unused); seniority; whether the postings
              (collected 2026-11-10) are still open.
Not claiming: that the 3/30 (10%, 95% CI 2.1–26.5%) miss estimate is a measured rate, or that it
              describes v2; that v2 is better in general; that a shortlisted posting means Priya should
              apply; that "sponsors visas: insufficient" means a company doesn't sponsor; that anything
              was trained.
Signed:       Nishant U, 2026-11-25.
```

## Driver's seat

| Task | What Claude should do | What I should do | Why it stays mine | Evidence |
| --- | --- | --- | --- | --- |
| The filter rules and their reasons | Implement the rules exactly as written, point out where the text is ambiguous, write tests and wrong versions from it | Write the rules and a reason for each, before any code; settle the ambiguities | What counts as relevant for Priya is a decision about her goals, not a fact in the postings | `FILTER.md` v1 at `5a6df3f`, before code at `8e759bf`; tests failing first at `7a0c270`; interpretations listed in `agent3/filter.py` |
| The reject audit and rule changes | Build a blind, seeded kit; compute agreement, the interval and the fix/break count for each candidate change; say what the counts overstate | Fix the audit rule before sampling; judge the postings; accept or reject each change with a reason | A rule change trades one kind of error for another, and only I can price that trade | `AUDIT-RULE.md` (`f308043`), kit (`096a74c`), verdicts (`b8b0a20`), decisions in `FILTER.md` (`b68e605`), `audit/AUDIT-REPORT.md` |
| The shortlist claims | Label each claim against the posting text with an exact quote; flag where a match does not entail the claim | Read the flagged cases; decide what a label is allowed to claim | A matching word is not support; whether a sentence supports a claim is a reading judgment | `SHORTLIST.md` cases 1–3; quote fix `409b995` |
| The MCP server and trust decisions | Write the server and its tests; run real transcripts; fill the four ledgers with evidence types | Decide whether to trust each server, for what, and under which conditions | Compatibility is not authorization: someone has to own the decision to connect a tool to an assistant | `mcp_server/transcripts/`, `MCP-EVALUATION.md`, trust decisions at `87b152a` |
| The final call that a posting is worth Priya's time | Claude can label claims against the text | Decide whether to put a posting in front of her | Whether a posting is worth her time depends on things the text can't settle (seniority fit, sponsorship, her priorities), so that judgment stays mine | C3 is "insufficient" for every accepted posting; seniority is not judged (`FILTER.md`); 22 of the 23 v2-accepted titles say Senior or Staff, and the 23rd is a "Lead" |
