# Job-Search Agent 3 — The Filter, the Tool, and the Score

**Smit P. · INFO 7375 · Fall 2026 · Chapters 7–9**

## Executive summary

This layer decides which collected job postings reach the candidate, and why. The agent
collected 473 postings from four public job boards on 2026-11-14 for a fictional new-grad
software engineer, Aarav Patel. A written filter kept 6 of them. Smit judged 71 postings by
hand to check the filter. It disagreed with him on 10, and 4 of its 6 keeps were wrong, mostly
because of one false friend: "5+ years …, *including 3+ years* with Ruby" read as a 3-year
job. Three rule changes chosen after measuring (version 1.1) leave 3 keeps, all of which Smit
judged relevant.

Each keep is broken into claims and checked against the posting's own words. The
top-ranked job matched three skills only inside "for example" lists and never states a
level or a number of years. Relevance is not entailment. The scoring step is offered to
Claude through a tool server written from scratch, with real transcripts. Claude as a judge
was measured one change at a time. A prompt change traded a wrong answer for an abstention,
and two identical runs disagreed once in 33.

**What it started from:** Job-Search Agent 1 (the fictional persona, the 2-skill rule, the
labeling rule) and Job-Search Agent 2 (the same three boards: Figma, Spotify, Linear).
Airbnb is added from Agent 1. The idea of a reject audit with recorded added/cut/rejected
words follows the instructor's Lectern. No code was copied from either.

## Language, toolchain, commands

Python 3 (tested on 3.12.7, macOS), **standard library only**, no `pip install`. The Claude
parts use the Claude Code command line (`claude`, tested 2.1.323), signed in. Run everything
from this folder.

```bash
python3 -m unittest discover -s tests -v
```

That runs 43 offline tests. Next, the deliberate-bug check, which writes `tests/mutation-log.md`:

```bash
python3 tests/mutation_check.py
```

Filter every saved posting (offline). Add `--version 1.0` for the audited version:

```bash
python3 src/run_filter.py --run-id live-20261114
```

Recompute the audit, the filter changes and the shortlist (offline):

```bash
python3 src/audit.py score --run-id live-20261114
```

```bash
python3 src/measure_filter.py --run-id live-20261114
```

```bash
python3 src/shortlist.py && python3 src/shortlist.py --compare && python3 src/entailment_example.py
```

Recompute the Claude judge scores from the saved replies (offline):

```bash
python3 experiments/run_claude.py --score
```

The tool server, driven by the hand-written client (offline; use a new name each time):

```bash
python3 src/mcp_client.py stdio-session --name my-session-1
```

**Network and model commands** (not needed to check anything above):

```bash
python3 src/collect.py --run-id live-YYYYMMDD
```

```bash
python3 experiments/run_claude.py --config baseline
```

That one makes 33 Claude calls (about $0.50) and refuses to overwrite saved results.

Claude Code as a client of the tool server (replace `/ABS/PATH` with this folder):

```bash
claude -p "Use the score_posting tool to score board figma, posting_id 5691911004. Report the verdict and quote the evidence." --model sonnet --mcp-config '{"mcpServers":{"js3":{"command":"python3","args":["/ABS/PATH/src/mcp_server.py","--transcript-name","my-claude-try"]}}}' --strict-mcp-config --allowedTools mcp__js3__score_posting --setting-sources "" --no-session-persistence
```

## What ran

All on 2026-11-14 US Eastern time. Timestamps inside the files are UTC (late 11-14 to early 11-15).

| What | Kind | Result | Evidence |
|---|---|---|---|
| Collection | **live**, 4 GETs to 3 allow-listed hosts | 473 postings (Airbnb 214, Figma 139, Spotify 87, Linear 33), 0 failures | `runs/live-20261114/manifest.json`, `raw/` |
| Filter v1.0 | offline | 6 keep, 467 reject, 0 cannot_tell | `runs/live-20261114/verdicts-v1.0.json` |
| Reject audit | Smit's hand verdicts on 71 | v1.0 wrong on 10/71 (random rejects 2/30) | `AUDIT.md`, `audit/` |
| Filter v1.1 | offline | 3 keep, all judged relevant by Smit | `FILTER.md` change log, `verdicts-v1.1.json` |
| Shortlist claims | checker + Smit's labels | 18 claims; agree on 10 | `SHORTLIST.md` |
| Tool server | **real** sessions: my client; Claude Code 2.1.323 with `claude-sonnet-5-5` | all requests answered or refused as declared | `TOOL-SERVER.md`, `transcripts/` |
| Other server | **live**: Microsoft Learn MCP, my client | 3 tools; declared prompts/resources empty | `transcripts/mslearn-*.jsonl` |
| Claude judge | **live**, 5 configs × 33 held-out, 165 calls, $1.46 | see table | `WHAT-MOVES-THE-SCORE.md`, `experiments/results/` |

Nothing in this folder is a seeded or simulated run. The postings in `tests/` are
**constructed** for the tests and labeled as such.

## How to explain any verdict

Open `runs/live-20261114/verdicts-v1.1.json` or call the tool. Each verdict names the rule
that decided it and quotes the text. By hand, in order:
1. Does the title contain a role word?
2. Does it contain a level word (senior, sr, staff, principal, lead, manager, director, head, intern, internship, PhD)?
3. Is there a description?
4. Is the location in the US? Missing → cannot tell.
5. Which is the *largest* "N+ years … experience"? 4 or more → reject; a range across 4, or no number → cannot tell.
6. Is at least 1 résumé skill there as a whole word?

## Layout

```
FILTER.md                 the filter and evidence rules, v1.0 written first (c25d7660), v1.1 change log
AUDIT.md                  the reject audit       SHORTLIST.md   claims, labels, entailment, abstention
TOOL-SERVER.md            server, transcripts, two evaluations
WHAT-MOVES-THE-SCORE.md   origin of every number, one change at a time, persistence
src/                      collect, postings, filter, run_filter, audit, measure_filter, shortlist,
                          entailment_example, mcp_server, mcp_client
tests/                    test_filter.py (committed before the filter code, 5466e3c1), test_parts.py,
                          mutation_check.py -> mutation-log.md
prompts/  experiments/    Claude judge prompts, runner, saved replies, SCORES.md
runs/     audit/          raw responses and verdicts; sample, hand verdicts, numbers, claims
transcripts/              every tool-server session, both directions
persona/                  fictional résumé (Aarav Patel, @example.com, 555 phone)
```

## Sign-off — Job-Search Agent 3

> **DRAFT by Claude. Not signed.** Smit must read every line, correct anything that is not
> true for him, decide the two trust decisions, and then sign or withhold.

**Checked**

| Property | Test or check |
|---|---|
| Wrong version 1 (substring matching: Java/JavaScript, SQL/PostgreSQL, lead/leadership, US/Russia) is caught | `tests/test_filter.py` `WrongVersion1_*`; mutant W1 caught |
| Wrong version 2 (location ignored) is caught: same posting flips US / Brazil / empty | `WrongVersion2_*`; mutant W2 caught |
| Each filter rule R1–R6, v1.0 and v1.1 | `test_filter.py` (33 tests; the first 27 committed before the code) |
| Collector refuses off-list hosts and http; a failed board is not judged; raw saved byte-for-byte | `test_parts.py` `Collector` |
| Tool server offers one read-only tool and refuses paths, extra arguments, undeclared tools and methods | `test_parts.py` `ToolServer`; real transcript `client-session-20261114` |
| The tests notice deliberate bugs | `tests/mutation-log.md`: 11 of 12 caught; the survivor is explained |
| The filter against my own judgment | my 71 hand verdicts (`AUDIT.md`) |
| The shortlist claims against the posting text | my 18 claim labels (`SHORTLIST.md`) |
| Report numbers match the saved data | recomputation: `audit.py score`, `measure_filter.py`, `run_claude.py --score` |

**How:** by hand (me): the filter choices, 71 hand verdicts, 18 claim labels, the v1.1
changes. With Claude's help: Claude wrote all code, all tests, both prompts and the drafts
of every report. `tests/test_filter.py` was written by Claude from FILTER.md and committed
before the filter code existed, but it is not a test **I** wrote before reading Claude's
code. By recomputation: every number in the reports.

**Not checked**

1. Whether the 3 shortlisted jobs are worth applying to: level and years are not stated in two of them.
2. Rejects outside the 71 judged: 467 rejects, 30 sampled; the random-sample interval is 0.8%–22%.
3. Run-to-run stability of my own verdicts: each posting was judged once, by one person.
4. The filter on any board other than these four, or on a second collection day.
5. Claude's judge on the dev postings, and the tool-list change, measured on held-out.
6. What Microsoft Learn's `microsoft_docs_fetch` does with a non-Microsoft URL.

**Not claiming:** that the filter finds good jobs; that 2/30 is the miss rate for all
rejects; that the prompt revision made Claude better (it moved errors into abstentions);
that any behavior here was learned or trained; that the claim checker is right where it
disagrees with me.

**Trust decisions:** my tool server: ____________ · Microsoft Learn MCP server: ____________

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Part of the task | Claude should | I should | Why it stays mine | Evidence the split happened |
|---|---|---|---|---|
| The filter rules | offer options; write them up; define what's needed to make them testable, marked as such | choose role words, exclusions, threshold, abstention cases, score, wrong versions | the filter decides what I never see | FILTER.md provenance; `[defined by Claude]` marks |
| Hand verdicts and claim labels | show the posting's facts, never its own verdict; ask once when an answer contradicts my stated rule | judge every posting and claim | they are the yardstick; if Claude labels, it grades itself | `audit/hand-verdicts.json`, `shortlist-hand-labels.json`, the checks recorded in each |
| Changing the filter | measure each change alone, on dev and held-out | decide what goes into v1.1, and why | a rule change trades missed jobs for wasted reading, and only I can set that price | FILTER.md v1.1 table ("Missing good jobs worse") |
| Code, tests, experiments | write and run all of it, and break it on purpose | read the results and run the tests myself | I have to explain any verdict | SOURCES.md; `tests/mutation-log.md` |
| Trusting a tool server | test what it declares against what it does | decide whether to connect it | a server runs with my session's access | TOOL-SERVER.md |
| **Is a posting worth my time?** | filter, cite, rank, and say "I cannot tell" | decide | it spends my application time and my OPT clock, and a score that ranks a job first can still rest on "e.g." lists | SHORTLIST.md: the top job's claims |
