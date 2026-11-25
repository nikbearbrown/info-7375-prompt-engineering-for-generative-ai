# Job-Search Agent 3: The Filter, the Tool, and the Score

JS2 gave me a bounded loop that saves every posting it fetches and judges it with a six-check rule. This layer does not build a new filter. It **writes that rule down as a versioned document before building anything** ([`FILTER.md`](FILTER.md)), **audits it by hand** on everything collected, **labels every claim on the shortlist** against the posting's own text, **offers one read-only capability to Claude** through a tool server written from scratch, and **measures one change at a time** on labels nobody tuned on. All judging runs on fictional persona Aarav Patel (`personas/`).

## What I started from

My own Job-Search Agent 2, as submitted: course folder `fall-2026/hsuan-t/js2-loop-tools-diff/` (course commits f81ce8f and 9ce2385). It holds the JS1 contract and watch, the JS2 loop over four boards on Greenhouse and Ashby, the permission policy, the rule judge and the Claude judge. I did not use the Reallocation Engine or Lectern code. JS2's README stays in that folder; this README covers JS3 only.

## Language and toolchain

| | Version used |
|---|---|
| Language | Python 3.11 (tested on 3.11.10, macOS) |
| Filter, audit, shortlist, tool server | Python standard library only |
| Tool server client | [Claude Code](https://claude.com/claude-code) 2.1.332 (the version in the transcript's `clientInfo`) |
| Claude judge (F5 E2 only) | Claude Code CLI `claude -p`, model `claude-sonnet-5-5` |
| Tests | `pytest==8.4.2` (`requirements-dev.txt`; also installs `anthropic==2.3.0`, used only by the JS2 `--claude-via api` path) |
| Data | Responses saved by the JS1/JS2 runs in `evidence/raw/` (5 folders, last one 2026-11-08). **JS3 fetched nothing new**: every number below comes from those saved files |

## Exact commands (fresh clone)

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/hsuan-t/js3-filter-tool-score
python3.11 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

# All tests: no network, no Claude call, no cost
.venv/bin/python -m pytest

# Judge every saved posting under FILTER v2.1 -> audit/all_verdicts.json, audit/summary.md
.venv/bin/python reports/audit_run.py

# Split each kept posting's justification into labeled claims -> shortlist/shortlist.json, SHORTLIST.md
.venv/bin/python reports/shortlist.py

# The numbers FILTER.md quotes (W1, L1; then A, B1, B2, C, L1 for v2)
.venv/bin/python reports/filter_v1_measure.py
.venv/bin/python reports/filter_v2_measure.py

# The tool server (stdio JSON-RPC); registration with Claude Code: MCP.md
.venv/bin/python -m job_agent.mcp_server

# F5: E1 (rule, no Claude), E2 (needs `claude` logged in: 20 calls per prompt)
.venv/bin/python reports/f5_experiment.py e1
.venv/bin/python reports/f5_experiment.py e2 claude_judge.v3
```

Checked on 2026-11-25 from a clean copy of the final commit (new venv): 326 passed; `audit_run.py`, `shortlist.py` and both `filter_v*_measure.py` rewrite their files **byte for byte the same** as committed. Two scripts are not in the list on purpose:
- `reports/f5_experiment.py e1` compares rule v1 with **the rule in the code today**. When I ran E1 that was v2 (13/20, `reports/f5/e1_rule.heldout.json`). The code is now v2.1, so a re-run writes 12/20, the v2.1 number the report already gives (`reports/what_moves_the_score.md` §2).
- `reports/audit_report.py` rebuilds only the k/n table of `audit/AUDIT.md` (it comes out the same) and overwrites the false-friend and rule-change sections written by hand. `reports/audit_sample.py` refuses to overwrite filled labels.

## What ran

| What | When, by whom | Result | Where |
|---|---|---|---|
| FILTER v1 written and signed, before any JS3 code | 2026-11-24, drafted by Claude, corrected and signed by me | six rules, one reason each, two wrong versions with tests | `FILTER.md`, commit d876d64 (20:10) before the first JS3 code ea263a7 (23:34) |
| Filter run on everything collected | 2026-11-24 (v1), 2026-11-25 (v2, v2.1) | 2,123 postings (stripe 843, openai 816, cloudflare 464); relevant v1 70 → v2 59 → v2.1 **67** | `audit/v1/`, `audit/all_verdicts.json`, `audit/summary.md` |
| Reject audit: 30 random rejects + 10 close calls + 10 kept, judged by me blind | 2026-11-25, me (seed 20261124) | disagreements 1/30, 3/10, 4/10 with 95% intervals; false friend S20 | `audit/hand_verdicts.csv`, `audit/AUDIT.md` |
| Shortlist: every claim labeled | 2026-11-25, code labels + my review | 67 postings, 496 claims; relevance ≠ entailment: Stripe 7235875 (AWS); abstention counterexample S16 | `shortlist/`, `shortlist/REVIEW.md` |
| Tool server in a real Claude Code session | 2026-11-25 18:02–18:04 UTC, I ran it | 11 messages both ways; one posting scored; `../../etc` refused by the server (`-32602`) | `transcripts/mcp-2026-11-25.jsonl`, `MCP.md` |
| Two server evaluations | 2026-11-25; evidence drafted by Claude, trust decisions mine | ours: trusted as is; official `fetch` (read at a pinned commit, not run): not connected | `MCP_EVAL.md` |
| One change at a time on 20 fresh held-out labels | 2026-11-25; labels mine, committed before any run | E1 filter v1 → v2: 12 → 13 (one posting already seen, so not clean); E2 prompt v2 → v3: 13 = 13 | `heldout/`, `reports/what_moves_the_score.md`, `reports/f5/` |

## Where each part of the brief is

| Brief | Where |
|---|---|
| Step 1: the filter as a document, versioned, a reason per rule | [`FILTER.md`](FILTER.md) §1, version header, §5 changelog |
| Evidence rules and "I cannot tell" | FILTER.md §2 |
| Expected sources and the answer when something is missing | FILTER.md §3 |
| ≥ 2 plausible-but-wrong versions + tests | FILTER.md §4; `tests/test_js3_wrong_w1_substring.py`, `tests/test_js3_wrong_w2_missing_field.py`; red run `evidence/js3/f1_wrong_versions_red.txt` |
| 2.1 Reject audit, honest sample statement, false friend, every rule added / cut / rejected | [`audit/AUDIT.md`](audit/AUDIT.md), `audit/hand_verdicts.csv`; FILTER.md §5 |
| 2.2 Source-grounded shortlist, relevance ≠ entailment, abstention | [`shortlist/REVIEW.md`](shortlist/REVIEW.md), `shortlist/shortlist.json`, `shortlist/review.csv` |
| 2.3 Tool server from scratch, real transcript, two evaluations | `job_agent/mcp_server.py` (no MCP SDK), [`MCP.md`](MCP.md), `transcripts/`, [`MCP_EVAL.md`](MCP_EVAL.md) |
| 2.4 Origin of every number, one change at a time, what persistence is not proof of | [`reports/what_moves_the_score.md`](reports/what_moves_the_score.md) |
| Sign-off and driver's seat | below |
| Commit history of my working repo | `evidence/git-history.txt` (this folder is one commit in the course repo; the ids cited here are from there) |

## Tests

`.venv/bin/python -m pytest` runs 326 test cases; JS3 added these files:

| What | Test |
|---|---|
| Wrong version W1: substring skill match | `tests/test_js3_wrong_w1_substring.py` (red on W1: `evidence/js3/f1_wrong_versions_red.txt`) |
| Wrong version W2: missing field = cut | `tests/test_js3_wrong_w2_missing_field.py` (same file) |
| FILTER v2 rule 4, from real audit sentences | `tests/test_js3_filter_v2.py` (7 of 9 fail on v1: `evidence/js3/v2_rule4_red_on_v1.txt`) |
| Audit run, blind sample, report (refuses blank labels) | `tests/test_js3_audit.py` |
| Every shortlist claim has one label and a verbatim quote or none | `tests/test_js3_shortlist.py` |
| Tool server: handshake, tools/list, tools/call, refusals, transcript | `tests/test_js3_mcp_server.py` (starts the server as a subprocess). The no-network import check was an agent-loop acceptance test at build time and is not in this repo (MCP_EVAL.md) |

JS1 and JS2 tests still run, including JS2's permission-policy boundary tests.

## Sign-off — Job-Search Agent 3

**Checked**
1. The filter in the code is the one FILTER.md describes, and the two wrong versions I chose are caught: `test_js3_wrong_w1_substring.py`, `test_js3_wrong_w2_missing_field.py`, `test_js3_filter_v2.py`.
2. The audit numbers come from my labels and not from a blank read as agreement: `test_js3_audit.py`; `audit/AUDIT.md` k/n recomputed from `hand_verdicts.csv`.
3. Every claim on the shortlist carries exactly one label, and every `supported` quote is word for word in the posting: `test_js3_shortlist.py`; all 323 quotes re-checked against the raw files (0 mismatches).
4. The tool server answers a real client and refuses a board outside its list: `test_js3_mcp_server.py`; the real Claude Code session in `transcripts/mcp-2026-11-25.jsonl`.
5. In F5 each run changed one object, and the held-out labels were committed before any run: `git diff` of the prompts (one line), commits d84e90a (sample) and 66d2c73 (labels) before the E1/E2 results.

**How**
1. By tests whose cases I chose (W1, W2 in FILTER.md §4; rule 4 from audit samples S01, S16, S20). Claude wrote the test code and ran each against the wrong version first (red runs in `evidence/js3/`).
2–3. By labeling 50 postings myself, blind to the filter's verdict, and by a script that recomputes the counts and re-reads the raw files (written and run by Claude, results checked by me).
4. By running the server in my own Claude Code session (2026-11-25) and reading the transcript.
5. By the commit order and the diff, shown in `reports/what_moves_the_score.md` §2.

**Not checked**
1. 495 of the 496 shortlist claims carry only the code's label; I reviewed one by hand (Stripe 7235875). The code never proposes `contradicted`, and it marks a word in the company intro as `supported` (REVIEW.md).
2. Whether the tool server opens no network connection at run time: no test in this repo checks it. The import check ran only as agent-loop's acceptance test when the server was built, and loading it in a fresh interpreter (proposal P1) was run once by hand, not kept as a test. Tested with one client, Claude Code 2.1.332.
3. A clean held-out result for FILTER v2 or v2.1: E1's only changed posting (H11) was seen while I decided B2, and v2.1 was found by reading H01. No unseen set was labeled after that.
4. Any posting newer than 2026-11-08: JS3 judged only saved files; the boards were not fetched again.
5. The `fetch` server's behavior: I evaluated it by reading its source at a pinned commit, not by running it.

**Not claiming**
- That the filter wrongly cuts about 3% of postings. 1 of 30 random rejects is a sample; a 95% interval of 0.1%–17% is all it supports, and only for these 2,123 saved postings.
- That FILTER v2 is better on unseen postings. Its 8 → 5 disagreements were measured on the same 50 samples it was built from, and on 19 unseen held-out postings v1 and v2 gave the same verdicts.
- That prompt v3 is better than v2. Both scored 13/20 and gave the same 20 verdicts; I adopted v3 so that Claude and the rule judge years the same way.
- That `readOnlyHint: true` makes a server safe, ours or anyone's (MCP_EVAL.md).
- That `relevant` means Aarav should apply. It means no rule found a reason to cut; whether a posting is worth his time is a judgment the filter doesn't make (driver's seat, last row).

**Signed:** Hsuan-Hung (Isaac) Tai, 2026-11-25

## Driver's seat

Commit ids are from my working repo (`evidence/git-history.txt`). The entry named in `FRICTIONAL.md` holds each decision with its context; quotes are from those entries. Labels like "D8" in the docs point to my private decision log; the decisions themselves are in FRICTIONAL and FILTER.md §5.

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| FILTER.md | Drafted every reason (tag `[AI]`), §2–§4, measured W1 and L1 | Read and corrected each rule; decided missing information passes and is labeled `insufficient`; chose W1 and W2; signed v1 | The filter says what reaches me; its reasons have to be mine to defend | d876d64 before ea263a7; FRICTIONAL "Missing info passes and is labeled insufficient": "Keep the current rule: not written counts as a pass. Just label the claim insufficient." |
| Build | Wrote the audit, shortlist and server code through agent-loop; found and fixed the "Node.js" split bug its own spec caused | Approved the tests before the run, merged | Code enters my agent only after I approve the tests | ea263a7, be7ab04; FRICTIONAL "Sign off FILTER.md, build the rest with agent-loop" |
| Reject audit | Drew the blind sample, computed k/n and intervals, proposed S20, measured candidates A, B1, B2, C, L1 | Judged all 50 postings with my LABELING_RULE; chose S20; adopted A and B2, rejected C, B1, L1; replaced B2's threshold with my ratio rule | The labels are the measurement; if Claude labeled them, the audit would measure Claude | 3d47dd8, 14a0b41; "Adopt A, don't adopt C, show me those 7 B2 postings." |
| Shortlist | Labeled 496 claims by code, re-checked every quote | Reviewed the Privy AWS claim as `insufficient`; kept the abstention counterexample | Whether a sentence supports a claim is a reading of meaning, which the code doesn't do | 30b4054, `shortlist/review.csv`; "knowing the skills the company uses is still a good plus" |
| Tool server | Wrote the server and MCP.md; read `fetch`'s source; drafted both evaluations | Registered it and ran the real session; made both trust decisions | Which tools may run on my machine is my call | edc5c1c, 7f08113; "Don't connect fetch… My agent may only reach the boards on its allow-list, and fetch reaches any site." |
| What moves the score | Built the origins table, drew the held-out sample, ran E1 and E2 | Labeled the 20 held-out postings before any run; adopted v3 for consistency, not score; replaced the rule-5 phrase | Choosing what to change, and accepting a lower score for a true rule, is mine | d84e90a, 66d2c73 before results; 4a62b61; "Adopt v3 for consistency, no extra run." |
| Sign-off | Drafted the wording and the candidate items | Chose what to claim and signed it | My name is on it | This section |
| **Worth my time?** | Gives `relevant` and the labeled reasons | Decides whether to apply | The filter only finds a reason to cut. It can't weigh what it can't see: S17, S24, S42 and S46 passed on one shared word while the job's core is C/C++ or low-level systems; Privy passed on the company's stack, not its requirements. Whether a job is worth an application is about my goals and my time, and nobody else, Claude included, holds those | `audit/AUDIT.md` disagreements; `shortlist/REVIEW.md` |
