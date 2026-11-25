# Job-Search Agent 3: The Filter, the Tool, and the Score

**Student:** Shreyash Yadav (`shreyash-y`) · INFO 7375 Prompt Engineering & Agentic AI, Fall 2026 · Professor Nik Bear Brown
**Assignment:** JS3, Chapters 7–9. Due 2026-11-23; built and submitted 2026-11-25.

**Starting point:** my own JS2 agent (`fall-2026/shreyash-y/js2-loop-tools-diff`, submitted commit
`177d5a8`). Its collector, rule v2 rev 3, persona, GATE.md and 121 tests were copied unchanged in
`07075a6d`. The reject audit follows the two-part design of the instructor's Lectern
(`fall-2026/nik-bear-brown/lectern/audit_rejects.py`: a uniform sample of rejects for the rate, plus the
closest calls). It was read, and no code was copied. The Reallocation Engine was not used.

*Who wrote what:*

- **Shreyash's own words:** the summary, FILTER.md, the 70 hand verdicts, every decision, both trust
  decisions, the driver's seat paragraph, Part 1 of FRICTIONAL.md and the signature.
- **Drafted by Claude Code and checked against the files:** everything else (SOURCES.md has the full
  list).

## For the grader: where each rubric item is, and one command to check it

Run every command from this folder.

| Rubric item | Where | Check it |
|---|---|---|
| The filter as a versioned document with reasons, written before the build | [FILTER.md](FILTER.md); how it became code in [FILTER-NOTES.md](FILTER-NOTES.md) | `git log --reverse --format='%h %ad %s' --date=iso -- FILTER.md js3/` shows FILTER.md first (`5e6a7703`, `3163fdb5`) and v1.1 decisions (`61e0d4c0`) before v1.1 code |
| Reject audit: ≥30 random rejects judged by hand, what the sample can show, a false friend, the rule log | [AUDIT.md](AUDIT.md), `results/audit-v1.md`, `labels/` | `shasum -a 256 -c labels/hand-verdicts.sha256 && python3 -m js3 audit` |
| Source-grounded shortlist: every claim labeled, relevance vs entailment, the abstention rule and a counterexample | [SHORTLIST.md](SHORTLIST.md), `results/shortlist-v1*.md` | `python3 -m js3 shortlist && python3 -m js3 shortlist --filter filter-v1.1.json` |
| Tool server from scratch, real transcripts, declared vs actual, two trust decisions | [TOOLSERVER.md](TOOLSERVER.md), `transcripts/` | `python3 -m unittest tests.test_js3_mcp_server -v` |
| What moves the score: origin of every number, one change at a time, held-out measurement | [SCORE.md](SCORE.md), `results/score-v1.json`, `results/judge/` | `python3 -m js3.score` |
| Sign-off and driver's seat | the end of this file | — |
| All tests; JS2's frozen tests unchanged | `tests/` | `python3 -m unittest discover -s tests -t . && shasum -a 256 -c tests.frozen.sha256` |

## Summary, in my own words

*Shreyash's words, typed into the session on 2026-11-25. Claude Code did not change them.*

I built this agent using my JS2 agent and added a tool called `score_posting` to filter jobs based on Alex's requirements. I used the reject-audit method to compare the filter results with job labels. The audit showed that exact word matching can miss good jobs and that matching skills alone can also allow unsuitable jobs. For example, the filter missed a Product Engineer role and accepted an Android role even though Android was not one of Alex's skills. I would add Product Engineer and count SQL databases as SQL, but keep the minimum of two skills. I would also keep the final decision with a human instead of fully trusting the agent.

## Language and toolchain

- **Language:** Python 3, standard library only, with nothing to install. Tested on Python 3.14.6
  (macOS). The code uses 3.9+ syntax.
- **Tests:** `unittest`. 218 tests, with 1 expected failure (JS2's Physician Reviewer test of the
  inherited rule).
- **Claude runs:** the Claude Code CLI, `claude` 2.1.331, with `--model opus` (claude-opus-5-5) and
  once `haiku` (claude-haiku-5-5). It is logged in with Shreyash's subscription, and no API key is
  used. Each call runs from an empty temporary folder with `--setting-sources ""`, so no plugin, hook,
  CLAUDE.md or memory reaches it.
- **The other tool server:** `chrome-devtools-mcp` 1.10.1, already in the local npx cache, run with
  Node 24.22.2 and Google Chrome 157.
- **Network:**
  - The live collection run reached only the three board hosts in GATE.md (`python3 -m jsagent run`).
  - The Claude CLI reached Anthropic.
  - The chrome-devtools-mcp check loaded one public posting page, which contacted 51 hosts
    (TOOLSERVER.md).
  - Nothing else uses the network.

## Commands, from a fresh clone

```bash
git clone -b shreyash-y/js3-filter-tool-score https://github.com/shreyashyadav1/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/shreyash-y/js3-filter-tool-score
```

These run offline and are deterministic. They rewrite the files under `data/` and `results/` with
the same content.

```bash
python3 -m unittest discover -s tests -t . -v
```

```bash
python3 -m js3 corpus && python3 -m js3 filter && python3 -m js3 filter --filter filter-v1.1.json
```

```bash
python3 -m js3 audit && python3 -m js3.score && python3 -m js3.whatif
```

```bash
python3 -m js3 shortlist && python3 -m js3 shortlist --filter filter-v1.1.json
```

A scripted MCP session against the tool server, with the transcript written to a file you name:

```bash
python3 -m js3.mcp_client --out /tmp/js3-session.jsonl --call score_posting '{"posting_key": "klaviyo:7792539003"}' -- python3 -m js3 serve
```

These need the network or the logged-in `claude` CLI. Each one writes new files:

```bash
python3 -m jsagent run
```

```bash
python3 -m js3.offer my-session "Use the score_posting tool on the saved posting klaviyo:7792539003 and say whether it should reach Alex."
```

The next command reruns a Claude condition, such as `B`. It is resumable and repeats no saved call;
the saved conditions cost $4.63 in all.

```bash
python3 -m js3.experiments B
```

To label: `python3 -m js3 label` (append-only). `python3 -m js3 label --print 1 10` shows the same
postings, shortened.

## What ran (2026-11-25, EST)

| When | What | Result | Evidence |
|---|---|---|---|
| 16:58, 17:05 | **FILTER.md v1** written by Shreyash, before any code | commits `5e6a7703`, `3163fdb5` | FILTER.md |
| 17:06 | **Live collection run** of the six GATE.md boards | `incomplete`, as designed: the deliberate 404 board failed and whoop was empty; 637 postings; JS2's check found nothing | `runs/20261125T220655Z/` |
| 17:14 | Filter tests written from FILTER.md, before the filter | 2 test modules fail to import | `evidence/tests-before-filter-code-2026-11-25.txt` |
| 17:20 | **Filter v1** on all 789 collected postings | 5 kept, 0 cannot tell, 44 closest calls, 0 quotes not found; the same verdicts as JS2's rule | `results/filter-v1/` |
| 17:20 | Audit and held-out draw, before any label | 70 to label, seed 7375 | `labels/SAMPLE-PLAN.md` |
| 17:23–17:25 | **The tool server**, offered to Claude three times and run once by my own client | Claude used it, reported "I cannot tell" correctly, and refused to apply | `transcripts/server/`, `transcripts/claude/` |
| 17:26 | **chrome-devtools-mcp**: declared tools, and one public posting page | 30 tools; the page contacted 51 hosts and showed the application form | `transcripts/other-server/` |
| 17:28–17:39 | **168 Claude judge calls**: B, B2, P, C, S, T and B3 on the 24 held-out postings, before any label | no condition moved a verdict; C changed the reasons on 12; T called the tool 0 times | `results/judge/` |
| 17:31–17:34 | Claude's independent claim labels for the 5 kept postings, run twice | run 2: 42 of 45 agree with the code | `results/claims-claude*/` |
| 17:53–18:04 | **Shreyash's 70 hand verdicts**, frozen by sha256 | audit: 0/30 random misses, 2/15 closest-call misses, 1/2 false positive; held-out 24/24 | `labels/`, AUDIT.md |
| 17:57 | A bug found by Shreyash's note on posting 8 (curly apostrophe), fixed test-first | 0 filter results changed | `evidence/apostrophe-*` |
| 18:07 | **Shreyash's v1.1 decisions** after measuring | adopt A1, A2, A4, B4; reject A3, A5 | FILTER.md "Version 1.1" |
| 18:09–18:12 | v1.1 tests, code, and two test-first fixes for A4 | 2 verdicts change (the two misses); audit 45/46; held-out 24/24 | `evidence/v11-*`, `evidence/state-codes-*`, `evidence/reside-colon-*` |
| by 18:28, and 18:30 | **Shreyash ran the tests and the label-hash check himself.** The first command (Claude Code's) hid the result line; the corrected one showed it | 218 tests OK (1 expected failure); `labels/hand-verdicts.jsonl: OK` | `evidence/commands-run-by-shreyash-2026-11-25.txt` |

## Folder map

- **The documents:**
  - `FILTER.md` (Shreyash's) and `FILTER-NOTES.md`;
  - `filter-v1.json` and `filter-v1.1.json` (the filter files the code reads);
  - `AUDIT.md`, `SHORTLIST.md`, `TOOLSERVER.md`, `SCORE.md`, `SOURCES.md`, `FRICTIONAL.md`.
- **`js3/`:**
  - `corpus.py`: everything collected, as one list.
  - `sections.py`: where each part of an ad sits.
  - `filtering.py`: FILTER.md as code.
  - `claims.py`: the labeled justification.
  - `audit.py`, `label.py`, `audit_report.py`: the draw, the blind labeling tool, the report.
  - `mcp_server.py`, `mcp_client.py`, `offer.py`: the tool server, the client, the offer to Claude.
  - `judge.py`, `experiments.py`, `score.py`, `whatif.py`: Chapter 9.
  - `claim_judge.py`, `shortlist.py`.
- **`jsagent/`, `tests/` (JS2's tests and `test_js3_*`), `demo/`, `persona/`, `boards.json`,
  `budgets.json`, `GATE.md`, `GATE-NOTES.md`:** inherited from JS2, unchanged.
- **`data/`:**
  - `corpus.jsonl`: 789 postings.
  - `inherited/js2-postings.json`: the raw JS2 job objects of the 152 postings that closed, with their
    runs and sha256.
- **`runs/`:** today's live run.
- **`labels/`:** the draw, its plan, and the hand verdicts with their hash.
- **`results/`:** every generated report.
- **`transcripts/`:** the MCP transcripts.
- **`prompts/`:** JS1's two prompts, byte for byte, and the FILTER.md-context prompt.
- **`evidence/`:** test runs before and after each fix.

## Known limitations

- **Filter v1.1 still keeps the Android/Kotlin job, which Shreyash's own label rejects.** The change
  that would remove it (A3) also removes two jobs he wants. It is recorded as a known false positive.
- **The audit bounds the miss rate below 9.5% at best,** for these boards and these dates. The held-out
  set separated only one change (A3), because its 24 postings do not sit where most changes act.
- **The filter reads words, not meaning.** "react quickly" counted as React, and "open to picking up
  Python" counted as Python. The verb case moved no verdict; the Android case is the false positive
  above.
- **The tool server scores with v1**, the version it was evaluated and transcribed with, not v1.1.
- **Only one held-out label set exists, and only one person labeled.** Claude's labels are a second
  opinion, not a second rater of the same kind.

## Sign-off — Job-Search Agent 3

*Drafted by Claude Code from the files. Shreyash signed it in the session on 2026-11-25 at 18:21 EST,
typing "sign shreyash yadav 26th november 2026", and corrected the date at 18:28 EST ("sorry its 25th
november"). He did not change the text and did not add a sentence on what he checked himself, so the
How line states only what the files show. After signing, at 18:30 EST, he ran the full test suite himself
(218, OK) and the hand-verdict hash check (`evidence/commands-run-by-shreyash-2026-11-25.txt`); the signed
text was not changed for that.*

```text
Checked:      - FILTER.md v1 and v1.1 as code: tests/test_js3_filter.py, test_js3_filter_doc.py and
                test_js3_boards.py (57), written from FILTER.md before js3/filtering.py existed
                (evidence/tests-before-filter-code-2026-11-25.txt); tests/test_js3_filter_v11.py (16),
                written before the v1.1 code (evidence/v11-tests-before-code-2026-11-25.txt). My five
                wrong versions are tests in them: WV1 remote not from Massachusetts, WV2 skills in
                benefits, WV3 more than 3 years, WV4 a made-up quote, WV5 a failed board as zero jobs.
              - The filter against my own judgment: my 70 hand verdicts, frozen by sha256 before any
                comparison: 0 misses in 30 random rejects, 2 misses in 15 closest calls, 1 false
                positive in 2 kept postings, 24 of 24 on the held-out set (results/audit-v1.md).
              - No made-up quotes: every quote the filter and the shortlist use is checked against the
                posting (0 not found in 789 postings), and so is every quote in Claude's claim labels.
              - The tool server: tests/test_js3_mcp_server.py (15, written after the server code) and
                the real transcripts of three claude -p sessions and one scripted session.
              - One change at a time: 168 Claude calls and six filter-file changes, scored against my
                held-out labels (results/score-v1.json); A3 and A5 rejected after measuring.
How:          The code and tests were written by Claude Code; the tests named above were committed
              before the code they test, except the server's. The hand verdicts, the v1.1 decisions,
              the claim labels in SHORTLIST.md section 4 and both trust decisions are mine, typed into
              the session. The rates and counts are recomputations by the scripts (js3 audit, js3.score,
              js3.whatif).
Not checked:  - The miss rate among all 763 rejects: 0 of 30 random rejects bounds it only below 9.5%
                (up to about 73 postings), and only for these six boards on these dates.
              - The 18 Palantir closest calls that were counted, not labeled.
              - chrome-devtools-mcp's telemetry and update traffic: read in its source and turned off,
                not observed on the network; its bundled DevTools code (about 200,000 lines) was not
                audited.
              - The tool server with any client other than Claude Code 2.1.331 and my own client, with
                very long input, or with two clients.
              - Whether a skill is central to a job or only mentioned: the Android job is a known false
                positive in v1.1, and the server still scores with v1.
Not claiming: That the agent finds good jobs; that the 5 open postings v1.1 keeps are all worth Alex's
              time (by my own label the Android one is not); that Claude agreeing with the filter on
              24 of 24 held-out postings makes either of them right in general; or that anything was
              trained: behavior that changed across sessions changed because its context changed.
Signed: Shreyash Yadav, 25th November 2026
```

## Driver's seat

| Part | Claude should | Shreyash should | Where the split shows |
|---|---|---|---|
| The filter's words and numbers | turn FILTER.md into code and tests; measure every proposed change on the corpus and on the labels before anyone decides | write FILTER.md; decide each change after seeing what it measures | FILTER.md (`5e6a7703`, `3163fdb5`, `61e0d4c0`) and its version log; A3 rejected after the held-out set caught it |
| The audit | draw the sample with a seed, hide the filter's verdict, compute the rate and what it cannot rule out | read and judge every sampled posting | `labels/hand-verdicts.jsonl`, frozen before comparing |
| The shortlist's claims | label every claim with an exact quote, check every quote, show where the code and Claude disagree | settle the disagreements | SHORTLIST.md section 4 ("technical leader" is a responsibility, not a Lead title) |
| The tools | write the server, run it with Claude, keep the transcripts, audit the other server's code | decide whether to trust each server, and for what | TOOLSERVER.md, both trust decisions |
| Whether a posting is worth Alex's time | rank it, explain it with quotes, say "I cannot tell" | decide | the Android job: every rule passed, Shreyash said no |

**Why that judgment stays mine** (*Shreyash's words, typed into the session on 2026-11-25*):

The agent follows the rules I give it, but those rules cannot cover every situation. A job can pass all the rules and still not be a good match, like the Android role. A job can also fail a rule and still be worth looking at, like the Product Engineer role. That is why the final decision should stay with me, and the agent should only help me make that decision.
