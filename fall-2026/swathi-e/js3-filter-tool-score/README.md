# Job-Search Agent 3 — The Filter, the Tool, and the Score

Drafted by Claude Code from the committed records; reviewed and approved by
Swathi, 2026-11-20.

Built on my JS2 agent. The starting point (`97407ff`) copies the JS2 core
unchanged from JS2 commit `91224bc`. JS2 itself was built on my JS1 agent.

Labels used below:
- **record**: recomputable from the committed files and code.
- **my input**: run, judged or decided by me (Swathi).
- **SIM**: test data built inside a test, never fetched.
- **not run**: an instruction for future use, not something that ran for this
  submission.

## What the agent does

For **Priya Nair, a fictional persona**, the agent:

1. **Collects** postings from three public job boards (Databricks and Stripe on
   Greenhouse, Plaid on Ashby) plus one deliberately nonexistent board, through
   the JS2 loop and its permission policy. Greenhouse postings now include
   their descriptions.
2. **Filters** every posting with the rules in `FILTER.md` (R1–R7, a
   hand-set score and threshold). Each verdict is one of `shortlisted`,
   `not shortlisted`, `rejected` or `I cannot tell`, with exact quotes from the
   posting for every rule result and evidence claim.
3. **Offers one capability to Claude as a tool**: `score_posting(board,
   posting_id)`, a read-only lookup of the saved filter v1.1 record for one
   posting, served by a small MCP server written from scratch.

It never applies, emails, messages or logs in anywhere. No real résumé is
used.

## The persona and the roles the filter accepts

Each file is quoted as it states it.

- **`persona/priya-nair.targets.json`** (copied unchanged from JS1 and JS2):
  - `target_role.primary`: "AI Engineer / ML Engineer"
  - `target_role.secondary`: "Data Engineer"
  - `target_role.description`: "LLM-platform and ML-infrastructure roles;
    Databricks/LangGraph stack."
  - `target_role.excluded`: "roles requiring active security clearance"
  - `geography`: `current_location` "Boston, MA", `open_to_remote` true
  - `visa`: type "F-1", current status "F-1 OPT (post-completion, year 1)"
- **`FILTER.md`** (my filter document) describes the persona as "AI/ML
  engineering first, data engineering second; Boston, MA or remote in the
  US; F-1 OPT; 0-1 years of experience."
- **`FILTER.md` R1** accepts a title that "names AI, ML, Machine Learning,
  GenAI, Data Engineer/Engineering, Data Scientist/Science or Analytics, or
  says Software Engineer together with New Grad, Early Career, Entry or
  University". R2 lets an "Analyst" title count for R1 only when the job's
  responsibilities or required skills name data, analytics, SQL, machine
  learning or AI.

The difference: Priya's targets are AI/ML Engineer (primary) and Data
Engineer (secondary), while FILTER.md R1 also accepts Software Engineer
titles with New Grad, Early Career, Entry or University, and all four
shortlisted postings are Software Engineer new-grad or early-career roles
(`shortlist/SHORTLIST.md`).

## Language and toolchain

- **Python, standard library only.** Nothing to install and no API key. The
  Python code never calls the Claude API: the filter is deterministic rules,
  and the tool server only answers MCP requests. The tests ran with Python
  3.12.2 (Anaconda) on macOS on 2026-11-20.
- **Allow-listed hosts** (inherited from JS2; exact match, https only):
  `boards-api.greenhouse.io` and `api.ashbyhq.com`.
- **MCP client used:** Claude Code v2.1.308, connected to my server as an
  actual MCP client in my session on 2026-11-20. Claude's side of that
  session ran inside Claude Code, not through any API call in this code.
- **External server evaluated:** `@modelcontextprotocol/server-filesystem`
  2.4.0, by **code reading only** (never installed or run; see
  `tool/EVALUATION.md` §2).
- **Validator:** `python3 scripts/validate_course.py` from the course
  repository root.

## Where to find each required part

| Required part | Where |
|---|---|
| The filter as a versioned document, written before the build | `FILTER.md`: v1 `0f689b8`; revisions before any filter code `3234f79`, `ef8ea9e`, `8c7c9b8`, `aa1049c`, `8c51e77`; filter code `6e6b4bf` |
| Evidence rules, expected sources, wrong versions | `FILTER.md` sections "The evidence rules", "Expected sources", "Wrong versions my tests must catch" |
| Rules added, cut or rejected after measuring | `FILTER.md` change log (`4a6dcfb`), addendum (`c0790a4`), threshold rejection line (`e8299de`) |
| Reject audit: 30+ random rejects judged by hand, close calls, kept postings | `audit/HUMAN_AUDIT.csv` (my 48 judgments, `fed055f`); blind sheet `audit/AUDIT.csv` and `audit/read/` (`161ebae`); `audit/selection.json`; `make_audit_sample.py`; my judgment rule `AUDIT-RULE.md` (`a285233`) |
| What the sample can honestly show; the false friends | `audit/AUDIT-REPORT.md` (`815064e`), sections A and G |
| Row 35 adjudication | `audit/ADJUDICATION.md` (`40f130e`) |
| Source-grounded shortlist and its labels | `shortlist/SHORTLIST.md` (`bf15eaf`); `shortlist/CLAIMS.csv` (claims `1442650`, my labels `f4dadb2`); plan `shortlist/SHORTLIST-PLAN.md` (`534c517`) |
| Relevance versus entailment; abstention rule and counterexample | `shortlist/SHORTLIST.md`, "Relevance versus entailment" and "Abstention rule and a counterexample" |
| Tool server (MCP, from scratch) | `tool/server.py` (`61b314c`); contract `tool/TOOL-SERVER.md` (`f1c24dd`, amendment `ff32302`, confirmation `9973987`) |
| Tool server tests, written before the server | `tool/tests/test_server.py` (`ae93c19`, `bdaf8ac`); predictions `tool/TEST-PREDICTIONS.md`; runs `tool/test-runs/` |
| Real transcripts, both directions | `tool/transcripts/` (scripted client `7f1e66c`; Claude Code `4fd59d6`), written by the server itself and committed unchanged |
| Both evaluations and my trust decisions | `tool/EVALUATION.md`: §1 my server (`96bc368`), §2 the Filesystem server, code reading only (`b3eb3dd`) |
| Origin of every number; one change at a time; held-out measurement | `heldout/EXPERIMENT-REPORT.md` (`e8299de`); plan `HELDOUT-PLAN.md` (`4cbb88c`); labels `heldout/HELDOUT.csv` (`b09f9ce`); measurement `runs/heldout-v1.1-threshold-2026-11-19T17-31-47-142253-0500/` (`698efbb`) |
| Persistence is not training | `heldout/EXPERIMENT-REPORT.md`, "Why the behavior persists" |
| Sign-off and driver's seat | `SIGNOFF.md` |
| Sources and AI contributions | `SOURCES.md` |
| Friction log | `FRICTIONAL.md` |
| Code and tests | `job_filter.py`, `descriptions.py`, `run_filter.py`, `collect.py`, `measure_heldout.py`, `make_heldout_sample.py`, `make_audit_sample.py`; `tests/`; `tool/` |

## Commands

Run every command from this folder (`fall-2026/swathi-e/js3-filter-tool-score/`).

### Offline: tests (ran 2026-11-20)

Filter and inherited JS2 tests. Result on 2026-11-20: `Ran 113 tests … OK`.

```bash
python3 -m unittest discover -s tests
```

Tool server tests. Result on 2026-11-20: `Ran 42 tests … OK` (about 10 s).
The launcher keeps file paths relative, so the output contains no
home-directory path. The tests delete only the transcripts they create.

```bash
python3 -c "import runpy, sys; sys.argv = ['tool/tests/test_server.py', '-v']; runpy.run_path(sys.argv[0], run_name='__main__')"
```

### Offline: reproduce the saved results

These scripts write their output once and never overwrite it, so in this
folder they refuse to run while the committed output exists. To recompute,
use a scratch copy of the folder and delete the output folder there first.

On 2026-11-20 Claude Code did this in a scratch copy of commit `b3eb3dd`, for
the two commands below. Both recomputed outputs matched the committed files
in every verdict, score and record. The only difference was the recorded
SHA-256 of `FILTER.md`, because one change-log line was added to `FILTER.md`
afterwards (`e8299de`).

Filter v1.1 on the saved 2026-11-17 collection (writes
`runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json`):

```bash
python3 run_filter.py runs/2026-11-17T21-47-06-167440-0500
```

The held-out threshold measurement (writes
`runs/heldout-v1.1-threshold-2026-11-19T17-31-47-142253-0500/measurement.json`):

```bash
python3 measure_heldout.py
```

The audit and held-out samples (fixed seeds). These ran once, at `161ebae`
and `cc74a29`; they were not rerun on 2026-11-20:

```bash
python3 make_audit_sample.py
```

```bash
python3 make_heldout_sample.py
```

### Network: collect fresh postings (not run for this README)

This makes one request to each board, writes a new `runs/<time>/` folder and
updates `state/seen_ids.json`. The deliberate bad board returns a 404, so it
always ends `incomplete`, with exit code 1.

```bash
python3 collect.py
```

**Inherited behavior to know before running it.** `collect.py` calls the JS2
loop, which applies my old JS1 title rule to every posting not in
`state/seen_ids.json`, prints that verdict and saves it in the trace. For the
held-out collection (2026-11-19) the state file was moved out of the
repository first, so every board was a baseline and no verdicts were
produced (`HELDOUT-PLAN.md`). New postings would then still need
`run_filter.py` on the new run folder.

### The tool server

The server speaks newline-delimited JSON-RPC (MCP revision 2025-11-25) on
stdin and stdout. Run by itself, it waits for input; each session writes one
new transcript to `tool/transcripts/`.

```bash
python3 tool/server.py
```

The scripted client starts the server twice (a normal and an adversarial
session) and checks every response. It ran once, on 2026-11-20 (`7f1e66c`).
Running it again writes two **new** transcripts; the committed ones are never
overwritten.

```bash
python3 tool/client.py
```

Privacy scan before committing any transcript or run output. It exits 1 on
any blocking hit; identity terms are read at run time and never printed.

```bash
python3 tool/privacy_scan.py tool/transcripts/*.jsonl
```

With an extra identity term to search for. **Placeholder:** replace
`<extra word>` with the word, without the angle brackets; `--term` may be
repeated:

```bash
python3 tool/privacy_scan.py --term <extra word> tool/transcripts/*.jsonl
```

Registering the server with Claude Code at local scope (not project scope,
so no configuration file is added to the repository). I ran these on
2026-11-20 for the Claude Code session, then removed the registration.
**Placeholder:** replace `<absolute path to this folder>` with this folder's
absolute path, without the angle brackets. Run the `add` command from this folder,
because local scope applies to the directory it is run from:

```bash
claude mcp add --scope local js3-score-posting -- python3 <absolute path to this folder>/tool/server.py
```

```bash
claude mcp remove --scope local js3-score-posting
```

### Getting only this folder from GitHub (not run)

```bash
git clone --depth 1 --filter=blob:none --sparse -b js3-filter-tool-score-swathi-e https://github.com/BESWATHI/info-7375-prompt-engineering-for-generative-ai.git js3
```

```bash
cd js3
```

```bash
git sparse-checkout set fall-2026/swathi-e/js3-filter-tool-score
```

```bash
cd fall-2026/swathi-e/js3-filter-tool-score
```

## What ran

| What | When (ET) | Commit | Label |
|---|---|---|---|
| Live collection with descriptions: Databricks 901, Stripe 789, Plaid 142; bad board 404; exit `incomplete` | 2026-11-17 21:47 | `d4a3b94` | record |
| Filter v1 on that run: 4 shortlisted, 2 not shortlisted, 1,800 rejected, 26 "I cannot tell" | 2026-11-17 | `beb8a26` | record |
| Audit sample (48 postings, seed 20261117) | 2026-11-17 | `161ebae` | record |
| My 48 audit judgments | 2026-11-18 | `fed055f` | my input (rows 5–48 after a ChatGPT-assisted draft) |
| Filter v1.1 on the same run: 4 shortlisted, 2 not shortlisted, 1,805 rejected, 21 "I cannot tell" | 2026-11-19 | `7672a21` | record |
| Held-out live collection, baseline (no verdicts): Databricks 900, Stripe 770, Plaid 141 | 2026-11-19 17:31 | `831d6af` | record |
| My 20 held-out labels, before any filter run | 2026-11-20 | `b09f9ce` | my input (row 1 after consulting ChatGPT) |
| Held-out threshold measurement, 5 vs 6 | 2026-11-20 | `698efbb` | record |
| My shortlist claim labels (21 claims) | 2026-11-20 | `f4dadb2` | my input (R6 and R3 changes after AI feedback) |
| Tool server tests before the server: 40 FAIL, 2 ERROR | 2026-11-20 | `bdaf8ac` | record |
| Tool server tests after the server: 42 OK | 2026-11-20 | `de027ed` | record |
| Scripted client, two sessions | 2026-11-20 | `7f1e66c` | record |
| Claude Code v2.1.308 as MCP client: one normal and one adversarial call | 2026-11-20 | `4fd59d6` | my input (the session) + record (the transcript) |
| Filesystem server 2.4.0: download, SHA-512 check, code reading | 2026-11-20 | `b3eb3dd` | record (code reading, not execution) |
| Both test suites and the recomputation check above | 2026-11-20 | — | record |

## Results in brief

- **Reject audit (sample, not a rate):** 0 of 30 random rejects were relevant
  by my judgment. The approximate 95% upper bound is 3/30 = 10%
  (`audit/AUDIT-REPORT.md` §A).
- **False friends:** "university" in description text (fixed in v1.1),
  "Spark" (unchanged), "AI" and "machine learning" (`audit/AUDIT-REPORT.md`
  §G).
- **Shortlist:** 21 claims, 17 supported, 4 insufficient (all R6), 0
  contradicted. All four shortlisted postings are "needs human check".
- **Threshold 5 → 6 on 20 held-out postings:** no verdict changed, because
  the filter rejected all 20 before scoring and I judged all 20 not relevant.
  Threshold 5 kept (`heldout/EXPERIMENT-REPORT.md`).
- **Tool server:** 42/42 tests; Claude Code first probed with
  `server/discover` (2026-07-28), got -32601 and fell back to `initialize`
  with 2025-11-25. The adversarial `../../etc/passwd` request reached the
  server and the server rejected it.

## Privacy notes

- **Recruiter names in a public raw response.** The Databricks raw file of
  the 2026-11-17 run (`runs/2026-11-17T21-47-06-167440-0500/001-databricks-request.json`)
  contains two recruiter names, published by Databricks on its public job
  board, with no contact details. The file is committed unchanged; nothing
  was redacted (commit message of `d4a3b94`). The 2026-11-19 run added no
  new emails, phone numbers, LinkedIn profiles or named recruiters
  (`831d6af`).
- **Home-directory paths in one early test run.**
  `tool/test-runs/before-implementation.txt` (`ae93c19`) contains absolute
  home-directory paths in its tracebacks. It stays as committed, with no
  history rewrite, as disclosed in the `tool/TOOL-SERVER.md` amendment. Later
  run outputs and all transcripts were checked before committing.

## Known limits

See "Not checked" and "Not claiming" in `SIGNOFF.md`, the limits in
`tool/EVALUATION.md` §1.4 and §2.5, and `audit/AUDIT-REPORT.md` §F–G.
