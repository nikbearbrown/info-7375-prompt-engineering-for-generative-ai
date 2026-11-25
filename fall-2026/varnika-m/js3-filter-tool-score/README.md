# Job-Search Agent 3 — The Filter, the Tool, and the Score

Varnika M · INFO 7375, Fall 2026

My JS2 agent collected 1,014 postings from three boards. JS3 decides what reaches me and why:
- a **filter written as a document** I can read ([FILTER.md](FILTER.md), committed before any code, `48488ab3`);
- a **reject audit** judged by my own hand;
- a **shortlist** where every claim is checked against the posting's own text;
- the agent offered to Claude **as a tool** through a Model Context Protocol server I wrote from scratch;
- a record of **what moves the score**.

Who did what is in [SOURCES.md](SOURCES.md), and my log is in [FRICTIONAL.md](FRICTIONAL.md).

## What I started from

- **My JS1 and JS2 work:**
  - The rule R1–R5 (`js3/rule.py`) is JS1's, **byte-identical** (SHA-256 `2aa42900…`).
  - The readers for Greenhouse, Lever and Ashby (`js3/boards.py`) are JS2's, byte-identical.
  - The persona is the same fictional résumé, Aarav Patel (`@example.com`, 555 phone).
  - The Claude judge and both prompts come from JS1 (`js3/claude_judge.py`, `prompts/`). One import line was changed.
- **The data:** the three raw responses of my JS2 live run `2026-11-10T215306Z`, copied into `data/` and checked byte for byte against the SHA-256 hashes in JS2's run record.
- **Not used:** the Reallocation Engine's role scorer and Lectern.

## Language, toolchain, commands

| What | Version | Needed for |
|---|---|---|
| Python, standard library only | 3.9+ (tested on 3.9.6, macOS) | everything |
| Claude Code CLI (`claude`), logged in | tested with 2.1.283 | only to repeat the Claude measurements (`js3.measure ask`) or the tool-server session |
| Network | none | no command here fetches anything |

From a fresh clone:

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/varnika-m/js3-filter-tool-score

python3 -m unittest discover -s tests -t .   # 34 tests, offline
python3 -m js3.report shortlist              # filter v1.1 on all 1,014 postings -> shortlist/SHORTLIST.md
python3 -m js3.measure score                 # every change scored against my held-out labels -> measure/scores.json
python3 -m js3.mcp_server                    # the tool server on stdin/stdout (a client starts it; see mcp.json)
```

To have Claude Code use the tool server, as in the saved session (this uses my Claude Code access):

```bash
claude -p "Call score_posting for posting_id lever/palantir/ab7e3425-81d5-4705-a7b5-cd60c8a45cdb" \
  --mcp-config mcp.json --strict-mcp-config --tools "" --allowedTools "mcp__js3__score_posting"
```

`python3 -m js3.sample` re-draws the blind sample (seed `20261125`) and rewrites `audit/`. Do not run it in this folder unless you want to replace the committed sample and labels sheet.

## What ran (all on 2026-11-25)

| Step | What | Result | Where |
|---|---|---|---|
| Filter v1 | FILTER.md v1 on 1,014 postings | keep 46 (38 jobs), close call 134, reject 834, cannot tell 0, not checked: none | `cc1636a1` |
| Blind sample | 62 postings: 30 random rejects, 8 close calls, 8 kept, 16 held out | committed before any label | `audit/sample.json` |
| My labels | 62 hand verdicts (53 mine; 9 Claude-suggested from my rules and confirmed by me) | 11 Y, 51 N | `audit/labels.csv`, `audit/labels-raw.md` |
| **Reject audit** | my labels against the filter | **0 of 30 random rejects fit: my pass line (at most 1) is met.** 2 of 8 close calls fit (a "D.C." bug), 7 of 8 kept fit | [AUDIT.md](AUDIT.md) |
| Filter v1.1 | my two rule changes after the audit (A: "D.C."; B: graduation date) | keep 61 (46 jobs), close call 137, reject 816 | [FILTER.md](FILTER.md), `ac25be53` |
| **Shortlist** | every claim on all 46 jobs labeled against the posting text | 234 supported, 0 contradicted, 99 insufficient. 34 "I cannot tell", 12 "fits" | [shortlist/SHORTLIST.md](shortlist/SHORTLIST.md), [shortlist/EVIDENCE.md](shortlist/EVIDENCE.md) |
| **Tool server** | Claude Code 2.1.283 (`claude-opus-5-5` requested; its record also lists `claude-haiku-4-5`) used my server, 15:52 UTC | 9 messages logged in both directions | [TOOL-SERVER.md](TOOL-SERVER.md), `transcripts/` |
| Two evaluations | my server, and the reference `fetch` server at commit `97ed9ec` | mine: trusted for read-only scoring. `fetch`: **not** for my agent | [TOOL-SERVER.md](TOOL-SERVER.md) |
| **What moves the score** | 48 Claude replies (16 held-out × 3 set-ups, 15:53–15:54 UTC) and 4 filter variants | M2 (keep at 4) 10/16; M3 (prompt) 14/16; others 16/16 | [WHAT-MOVES-THE-SCORE.md](WHAT-MOVES-THE-SCORE.md), `measure/` |

The tool-server session ran with filter **v1** (before v1.1). The server now answers with v1.1.

## What is in this folder

| Path | What it is |
|---|---|
| `FILTER.md` | the filter as a versioned document: rules with reasons, evidence rules, sources, wrong versions, the audit plan, versions v1 and v1.1 |
| `AUDIT.md`, `audit/` | the reject audit, every hand verdict, the blind sheets, my labeling decisions, my raw label lines |
| `shortlist/` | the source-grounded shortlist and its notes |
| `TOOL-SERVER.md`, `js3/mcp_server.py`, `mcp.json`, `transcripts/` | the tool server, its real transcript, and both evaluations |
| `WHAT-MOVES-THE-SCORE.md`, `js3/measure.py`, `measure/` | the origin of every number, the one-change-at-a-time results, every Claude reply |
| `js3/` | `load.py` (data, hash-checked), `filter.py` (v1 and v1.1), `claims.py` (evidence rules), `rule.py` (JS1), `boards.py` (JS2), `sample.py`, `quickview.py`, `report.py`, `claude_judge.py` (JS1) |
| `tests/` | 34 tests, including FILTER.md's wrong versions WF1–WF6 |
| `data/`, `persona/`, `prompts/` | the saved responses, the fictional résumé, the two JS1 prompts |

Left out: caches, credentials (there are none), my real résumé, and the Claude Code conversation transcript of my own work, which stays on my machine.

## Sign-off — Job-Search Agent 3

*Claude Code's draft from the record, for me to check, change, and then sign or withhold.*

**Checked**
- **The filter's rules and wrong versions.** Tests:
  - `test_wf1_engineer_alone_is_not_a_role_word`, `test_wf2_javascript_is_not_java`, `test_wf3_ranking_counts_different_skills_not_repeats`;
  - `test_wf4_no_years_is_insufficient_and_the_answer_is_cannot_tell`, `test_wf5_the_same_job_in_three_cities_is_one_shortlist_entry`, `test_wf6_a_missing_field_is_cannot_tell_not_a_verdict`;
  - `test_a_washington_dc_with_dots_is_a_us_location`, `test_b_must_be_graduating_later_than_his_degree_fails`.
- **The data is what JS2 collected.** Tests: `test_the_saved_data_is_what_js2_recorded`, `test_changed_bytes_stop_the_run`, `test_a_missing_board_is_not_checked_not_empty`.
- **The evidence rules.** Tests: `test_relevance_is_not_entailment_a_listed_word_is_not_an_ask`, `test_a_nice_to_have_skill_is_not_supported`, `test_more_years_contradict`.
- **The tool server does only what it declares.** Tests: `test_a_tool_it_does_not_offer_is_an_error`, `test_extra_or_wrong_arguments_are_refused`, `test_the_server_writes_nothing_but_its_transcript`. Also the real Claude Code transcript.
- **The reject audit.** 0 of 30 random rejects fit, by my own labels.

**How**
- **By hand:** all 62 labels (9 of them by confirming Claude's suggestions from my rules), my labeling decisions, and the v1.1 rule decisions.
- **By recomputation:** `python3 -m js3.measure score` recomputes every agreement from the saved replies and my labels.
- **With Claude's help:** Claude Code wrote all code, tests and reports. The tests were written **after** the code this time, not before.

**Not checked**
1. Whether any of the 816 v1.1 rejects fit. 0 of 30 is consistent with up to about 9.5% of them, about 79 postings.
2. Run-to-run variation in Claude's answers. Each held-out set-up was asked once.
3. Whether Aarav is eligible for a US security clearance. 6 of my 11 Y labels depend on it.
4. The `fetch` server's six helper modules, and the server running at all: it was evaluated by reading only.
5. A tool-server session with filter v1.1. The saved session used v1.
6. Whether the postings are still open. The data is from 2026-11-10.

**Not claiming**
- That the filter finds every job that fits Aarav, or that its "fits" answers are right ("3+ years" is a known gap).
- That one prompt or setting is better in general: 16 held-out postings, 2 fits.
- That anything was learned or trained: behavior changed only through files.
- That this says anything about another candidate, board or day.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Part | What Claude should do (and did) | What I should do (and did) | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter | Draft FILTER.md from my JS1 rules; recommend decisions | Make the decisions: D1–D3 before the build; A–F after the audit | The rules decide what never reaches me. A rule I cannot defend is not mine. | `48488ab3`; FILTER.md Versions |
| The audit labels | Build a blind, shuffled sheet; point out labels that contradicted my own rules | **Judge every posting**: is it worth my time? | **Whether a posting is worth my time is the judgment the whole agent serves.** Claude labeling it would be Claude grading Claude's filter. | `audit/labels-raw.md`; AUDIT.md "Who decided each label" |
| The evidence | Label every claim with a quote; show where relevance is not entailment | Read the counterexamples, and decide what "fits" may mean (D2) | A quote can support the words and still not the conclusion ("3+ years"). Only I decide whether a job is worth applying to. | shortlist/EVIDENCE.md |
| The tool server | Write it, run Claude Code against it, evaluate both servers | Make the trust decisions | Granting a tool to an agent is a permission I give, not one the tool declares | TOOL-SERVER.md sections 3–4 |
| What moves the score | Run each change once, against my held-out labels | Decide what to adopt (v1.1 yes; M2 and M3 no) | The held-out labels are my judgment, so the measurement is only as good as they are | WHAT-MOVES-THE-SCORE.md |
