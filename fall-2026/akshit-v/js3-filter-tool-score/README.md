# Job-Search Agent 3: The Filter, the Tool, and the Score

My agent collects postings from three applicant-tracking systems for a fictional persona, **Jack Spencer** (a data engineer with 5 years of experience). This layer decides what reaches him and why:
- **a filter you can read**: FILTER.md, versioned, with a reason for every rule, written and committed before any JS3 code;
- **an audit** of what it rejected, judged by hand;
- **a shortlist** whose every claim is checked against the posting's own text;
- **the agent offered to Claude as a tool**, through an MCP server I wrote from scratch;
- **a measurement of what actually moves the score**, one change at a time, on held-out labels.

**Started from:** my own Job-Search Agent 1 rule, persona, and Claude judge, and my Job-Search Agent 2 loop, providers, permission policy, and tests. All were carried into `agent3/` (the JS2 tests run unchanged against it). I did not use the Reallocation Engine or Lectern.

## Language and toolchain
- **Python 3.12.10**, standard library only. Nothing to `pip install`. Tests use `unittest`.
- **Claude Code CLI 2.1.316** (`claude -p`, logged in with my account), model `claude-opus-5-5`, for the judge, the shortlist justifications and checker, and as a real MCP client. Everything else runs without it.
- **Node.js 24.19.0 / npm 11.17.0**, only to run the *other* MCP server I evaluated (`@modelcontextprotocol/server-filesystem@2.2.0`). It was installed outside this folder with `--ignore-scripts`.
- **Network:** read-only GETs to `boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com` (the JS2 allow-list, enforced in `agent3/policy.py`).
- Developed on Windows 11. Commands work from this folder in PowerShell or Git Bash.
- **Dates:** commit times are ET. Label and run times are given in UTC; "2026-11-25" entries were written in the evening of 11-24 ET.

## Exact commands

```bash
# Tests (no network, no Claude): 69 tests
python -B -m unittest discover -s tests -t . -v

# 1. Collect (live; compares against out/state/seen_ids.json from JS2's Nov 10 run)
python -B -m agent3.run --resume data/resume_jack_spencer.json
python -B -m agent3.corpus                               # merge every saved run by id -> 714 postings

# 2. Filter, and recompute it by a second method that imports nothing from agent3
python -B -m agent3.run_filter --version v1.2            # also v1.0, v1.1
python -I -B scripts/recompute_filter.py                 # literal reading = v1.0
python -I -B scripts/recompute_filter.py --loose         # loose reading = v1.1/v1.2 phrase rule

# 3. Audit: the sample, the blind labeling page, the reports
python -B scripts/draw_sample.py                         # seed 20261124 (already drawn and committed)
python -B scripts/label_server.py                        # http://127.0.0.1:8765, writes labels/hand_labels.csv
python -B scripts/audit_report.py --version v1.0 --sets audit
python -B scripts/label_flags.py
python -B experiments/candidates_v1_1.py

# 4. Shortlist: justify, verbatim check, meaning check, answer; then the blind claim check
python -B -m agent3.shortlist --version v1.0             # 20 Claude sessions
python -B scripts/claim_server.py --version v1.0         # http://127.0.0.1:8766
python -B scripts/shortlist_report.py --version v1.0

# 5. The tool server and its evaluation
python -B -m agent3.mcp_server                           # stdio MCP server (a client starts it)
python -B scripts/mcp_probe.py mcp/probes/js3_filter_probe.json mcp/transcripts/x.jsonl -- python -B -m agent3.mcp_server
python -B scripts/claude_as_client.py --name demo --prompt "Score posting greenhouse:figma:6201407004 with score_posting."
python -B scripts/fs_eval_setup.py <sandbox dir outside this folder>
python -B scripts/mcp_probe.py mcp/probes/fs_default.json mcp/transcripts/fs_default.jsonl -- node <pkg>/dist/index.js <sandbox>/allowed

# 6. What moves the score (held-out; each Claude condition refuses to run twice)
python -B experiments/one_change.py filter --a v1.0 --b v1.1
python -B experiments/one_change.py setting --version v1.1
python -B experiments/one_change.py claude --cond baseline        # also baseline_repeat, prompt_v2,
python -B experiments/one_change.py report                        #   prompt_v3_definition, context_score, tools_score
python -B experiments/persistence.py
```

## What ran

| When (ET) | What | Result | Evidence |
|---|---|---|---|
| 11-24 21:33 | **FILTER.md v1.0 committed alone, before any code** | my decisions on Claude's numbered proposals | `0e4173c` |
| 11-24 21:33 | **Live run** (4 boards) | `incomplete`: figma 146, spotify 92, snowflake 371; the deliberate 404 not retried. **Real new postings since Nov 10: 19 / 24 / 68.** | `out/runs/20261125T023341Z.txt` |
| 11-24 | Corpus | **714** distinct postings; v1.0 kept 25 | `out/corpus/manifest.json`, `out/filter/v1.0/` |
| 11-24 | Second-method recompute | 714/714 agree (literal). The first run used the loose reading by accident: 5 disagreements, all punctuation inside a phrase. | `out/recompute/` |
| 11-24 21:40 | 80-posting sample drawn, **before any label** | seed 20261124 | `d6225f6` |
| 11-24 | MCP server probed and used by Claude Code; filesystem server probed (5 setups + 2 Claude Code runs) | see `mcp/EVALUATION.md` | `4c1ec0b`, `530de6a` |
| 11-24 | Persistence demonstration (6 sessions) | not_relevant ×2 → relevant ×2 with a notes file → not_relevant ×2 | `out/experiments/persistence.json` |
| 11-24 21:59 | Shortlist v1.0: 10 postings, 69 claims, before my claim check | checker: 46 supported, 22 insufficient, 1 contradicted | `e5a2c47` |
| 11-25 03:04–03:46 UTC | **My 80 blind labels** | 48 relevant, 32 not | `30eddc9` |
| 11-24 23:00 | **Definition of "relevant" changed after labeling** (my choice) | labels unchanged; ≥ 18/80 contradict the new definition | `48fc3f9`, `labels/label_noise.md` |
| 11-24 23:18 | v1.1 (C2 added; C1, C3, C4 rejected) and **v1.2 (threshold 5, fitted)** | held-out 14 → 14 → **21** of 30 | `b5859ce` |
| 11-24 23:23–23:32 | 180 Claude sessions on the held-out 30 | 0 flips for prompt / context / tool list / A–A; **14 flips for the definition** | `39052f4`, `5daf151` |
| 11-26 00:15–00:25 UTC | **My blind check of the 69 claims** | all 69 "supported"; E4 applied as I decided | `cab4c42` |

## Where each deliverable is

| The assignment asks for | File |
|---|---|
| The filter as a versioned document, written first | **FILTER.md** (v1.0 at `0e4173c`; version log in section 7) |
| The reject audit, hand verdicts, false friends, rules added / cut / rejected | **AUDIT.md**, `labels/hand_labels.csv`, `out/audit/`, `out/experiments/candidates_v1_1.md` |
| The source-grounded shortlist and its labels | **SHORTLIST.md**, `out/shortlist/v1.0/claims_table.md`, `labels/claim_checks_v1.0.csv` |
| The tool server, transcripts, both evaluations | `agent3/mcp_server.py`, `mcp/transcripts/`, `out/mcp/transcripts/`, **mcp/EVALUATION.md** |
| The one-change-at-a-time report | **WHAT_MOVES_THE_SCORE.md**, `out/experiments/REPORT.md` |
| Sign-off and driver's seat | below |
| SOURCES, FRICTIONAL | **SOURCES.md**, **FRICTIONAL.md** |

## Results in brief

- **Audit (v1.0, my labels as labeled):**
  - 12 of 30 random rejects were postings I labeled relevant: 40%, 95% CI 23–59%, or roughly 156–409 of the 689 rejects.
  - 0 of 10 kept were wrong (still compatible with up to 31%).
  - 11 of the 12 reject errors score 0–3, so they are differences of *definition*, not near-misses. 6 of the 12 are labels my own definition contradicts.
- **False friends:**
  - `Snowflake` (the employer's name), guarded since v1.0;
  - `streaming` (9 of 10 Spotify matches are music streaming);
  - `orchestration` ("program / resource orchestration");
  - `data warehousing` (the thing being sold, in sales roles).
  - The streaming and orchestration guards were measured, changed no verdict, and were rejected. Both words stay unguarded.
- **Shortlist:** two real relevance-is-not-entailment cases.
  - A verbatim quote that stops just before "or equivalent practical experience".
  - Spark, Kafka, and Airflow matched in a line headed "We'd love to hear from you if you have".
  - The abstention rule abstains on silence, and it answers whenever *any* core claim is supported, even one saying the work is pre-sales.
- **Tool server:** my 1.0.0 answered tool calls before `initialize` (fixed in 1.0.1), and its description over-claims offsets for role words (not fixed). The filesystem server writes by default, accepts undeclared arguments, and lets a 2025-era client's Roots replace the operator's directory unless started with `--confine-roots`; on Claude Code's 2026-07-28 connection it did not.
- **What moved the score:** only the objects that hold the **criterion**. The definition paragraph moved agreement 12 → 20 of 30 (14 flips, against 0 from re-asking). The fitted threshold moved the filter 14 → 21. The abstain instruction, the score in context, and the offered tool moved nothing.

## Sign-off: Job-Search Agent 3

> Claude Code drafted these words at my request from the record and the files cited. The signature line is mine, and I sign only after reading every line.

**Checked:**
- **The filter computes what FILTER.md says.**
  - `tests/test_filter.py`, rule by rule, F2–F9 and v1.1's C2.
  - A second method that imports nothing from `agent3` (`scripts/recompute_filter.py`) agreed on 714 of 714 for v1.0 and for v1.1.
- **All four wrong versions are caught**, in `tests/test_wrong_versions.py`:
  - WV1, employer name as skill;
  - WV2, keyword present = supported;
  - WV3, missing data = not relevant;
  - WV4, threshold off by one.
- **The evidence-rule pipeline does what E1–E4 and A1–A3 say**, in `tests/test_shortlist.py`:
  - a fabricated quote never reaches the checker;
  - the checker never sees the résumé or score;
  - a contradicted level gives not_relevant;
  - an unsupported core claim gives cannot_tell;
  - malformed replies are rejected, never repaired.
- **My MCP server enforces what it declares** (`tests/test_mcp_server.py`; probe transcripts before and after the 1.0.1 fix):
  - its schema;
  - an unknown posting is an error, not a "no";
  - a failed board gives cannot_tell;
  - tools are refused before `initialize`.
- **The JS2 loop and permission policy, unchanged**, in `tests/test_loop.py`, `tests/test_policy_boundaries.py`, `tests/test_review_time_budget.py`.
- **The sample and the labels were fixed in git before anything was computed on them** (`d6225f6`, `30eddc9`, `cab4c42`). The Claude prompt for each held-out condition was committed before its run.

**How:**
- **By hand:** all 80 posting labels and all 69 claim labels. Every decision in FILTER.md, the change of definition, which candidate rules to add or reject, adopting the threshold, applying E4, and running the definition-prompt experiment.
- **By a test I wrote before reading Claude's code:** none.
- **By recomputation:** `scripts/recompute_filter.py`, written by Claude, run on every version.
- **With Claude's help:** all code, tests, prompts, probes, and the drafts of every document, including this one.

**Not checked:**
- **The shortlist claims against their quotes, by me.** My hand check marked all 69 supported, including two claims with no quote, which E3 says are insufficient by definition. My notes judged the job ("job role is relevant"), not the claim. I chose to let E4 apply anyway, so the claim labels in force were not tested claim by claim. The only claim-by-claim judgments are the checker's, and 20 of its 22 "insufficient" labels lean on a résumé it was never given.
- **Whether my labels follow one definition.** At least 18 of 80 contradict the definition I adopted after labeling (`labels/label_noise.md`), and I did not re-read them. Every agreement number carries that noise.
- **The abstention rule A1 on real data.** No posting in the corpus is under 300 characters.
- **A2 checks that a core claim is supported, not what it says.** A supported "the main work is pre-sales" counts as data-engineering work. Found while writing SHORTLIST.md, not fixed.
- **My MCP server's promise of an offset for every matched word.** Role words have none. Found by Claude Code as a client, not fixed.
- **The filesystem server beyond read, list, and write.** Not checked: `move_file`, `copy_file`, `edit_file`, its Windows race, a POSIX symlink, any of its dependencies, or 2,700+ lines of its source.
- **Any Claude result beyond 30 held-out postings, one model, and CLI defaults.** No temperature control; A–A showed 0 verdict flips, but that is one repeat.
- **Whether the held-out set is still clean.** It was used to decide on the threshold, and the definition-prompt run was chosen after seeing the other conditions.
- **Whether `judge_v3_definition.md` should replace the agent's judge.** The agent still uses `judge_v1.md`.
- **My own run of the test suite**, unless recorded in `review/`.

**Not claiming:**
- That the filter, or Claude, finds jobs worth Jack's time. Every number here measures agreement with my labels, which use a loose "skills overlap" definition that I adopted after labeling and that at least 18 of my own labels contradict.
- That a supported claim makes a posting a good fit. Counterexample 2 in SHORTLIST.md shows support without fit.
- That "0 flips" means prompts, context, or tools never matter. It means they didn't cross a verdict on these 30 under a prompt whose criterion already settled them.
- That anything was trained. The persistence demonstration shows a behavior that lived in a file.
- That the filesystem server is safe or unsafe in general. My findings are for 2.2.0, these flags, and these two clients.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Where it shows |
|---|---|---|---|---|
| The filter (FILTER.md) | measured the JS1 rule on the Nov 10 postings; proposed every rule as a numbered option | approved F1–F9, E1–E5, A1–A3; chose all four wrong versions and the sample sizes | The filter is the standard the agent is judged by. If Claude set it, Claude would be grading itself. | `0e4173c` |
| Hand labels | built the blind sheet and page; afterwards flagged 44 labels that conflicted with my rule; never suggested a label | labeled all 80; chose to change the definition rather than the labels | The labels are the answer key. They cannot come from the thing being graded. | `30eddc9`, `48fc3f9` |
| Rule changes | measured each candidate on the audit labels only | added C2, rejected C1, C3, C4, adopted the fitted threshold | A rule change is a claim that the filter got better; I'm the one who has to stand behind it. | FILTER.md section 7 |
| Shortlist claims | wrote and checked them with two separate sessions; showed me #16/#64 and the 23 disagreements | checked all 69 blind; decided E4 applies | E4 says my label stands. The cost of that is mine, and it is recorded. | `cab4c42`, SHORTLIST.md |
| Tool servers | wrote mine; probed both; drafted declared vs. actual | the trust decision for each | Trusting a tool means accepting what it can do with my files and my agent. | mcp/EVALUATION.md |
| **Is a posting worth my time?** | gives a labeled judgment; on 30 held-out postings it moved 14 verdicts when only the definition changed | the final call | A posting's worth depends on a definition, and this project showed how far a definition moves every number. Whoever spends the day applying bears the cost of a wrong yes, so the definition and the final yes or no stay mine. | WHAT_MOVES_THE_SCORE.md |
| Sign-off | drafted the words | sign or withhold | Only I can be held to what I say I checked. | this section |

> The "why" column was drafted by Claude Code at my request.
