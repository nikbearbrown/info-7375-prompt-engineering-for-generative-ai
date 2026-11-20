# Job-Search Agent 3 — the filter, the tool, and the score

**Author:** Prasad Shinde · **Course:** INFO 7375 · **Written:** 2026-11-20
**Started from:** my JS2, js2-loop-tools-diff/ at 64e00c7, copied in unchanged (JS3-CP4a; CONTRACT.md v0.9). The Reallocation Engine was not used; Lectern was reference only (SOURCES.md).

JS3 decides which collected postings reach the fictional persona, Alex Rivera, an aspiring APM in New York. It has a filter written down before it was built (FILTER.md), an audit of what that filter rejects (AUDIT.md), a source-grounded shortlist (SHORTLIST.md), the filter offered to Claude as an MCP tool written from scratch (TOOLSERVER.md), and a record of what moves the score, measured one change at a time on labels sealed before any change existed (SEAL.md, MEASURE.md).

## Where each part of the brief is

| Brief | Where |
|---|---|
| FILTER.md: the filter, evidence rules, expected sources, wrong versions | FILTER.md §1–§4 (v1 written first, JS3-CP1; v2 and v2.1 after measuring, §6) |
| The filter and the reject audit: 30+ random rejects, closest calls, kept sample, error count and what a sample this size can say, a false friend, every rule added, cut or rejected | AUDIT.md §2, §5, §7, §8; FILTER.md §6 |
| The source-grounded shortlist, claim labels, relevance vs entailment, abstention rule and a counterexample | SHORTLIST.md; shortlist/claim_labels.tsv |
| The agent as a tool, the real transcript, both evaluations | TOOLSERVER.md; tools/mcp_server.py; transcripts/ |
| Where every number came from; one change at a time on held-out labels; persistence is not proof | MEASURE.md |
| Sign-off and driver's seat | this file, below |
| SOURCES.md, FRICTIONAL.md | those files |

## Language and toolchain
- Python 3.11 or newer, standard library only; tests with unittest. On my machine: Python 3.13.17, run as `python3.13`. No pip install is needed.
- Git.
- Node 20 and npm 10, only to probe the third-party MCP server (TOOLSERVER.md §3); nothing in JS3 needs them.

## Commands
Run every command from this folder, fall-2026/prasad-s/js3-filter-tool-score/. The tests need nothing else. Every other command reads the frozen corpus where it lives, in the sibling folders js1-contract-and-watch/ and js2-loop-tools-diff/, so run those from a clone of the course repository, not from the zip.

**All tests (no network):** `python3.13 -m unittest discover -s tests -v`. Last result, 2026-11-20: 392 tests, OK.

**The filter over the frozen corpus:** `python3.13 tools/filter_run.py` (v1) and `python3.13 tools/filter_run.py --filter v2`. Each writes a new output/filter_v*_<UTC>/ folder.

**The seal:** `python3.13 tools/seal_draw.py counts` reprints the counts. `draw` and `replace-js3` refuse to run again, because their files exist; that refusal is intended (SEAL.md §7).

**The labeling viewer, for JS3's held-out set:** `python3.13 tools/label_view.py list`, `show N`, `template`, `check PATH`.

**The audit:** `python3.13 tools/audit.py compare audit/hand_verdicts_r5.tsv` re-runs the final comparison into a new folder; `python3.13 tools/audit.py context N` shows matched terms in place.

**The measurements:** `python3.13 tools/measure.py --hand audit/hand_verdicts_r5.tsv` (development), and `python3.13 tools/measure.py --heldout vault/js3_heldout_labels.tsv --heldout vault/js3_heldout_labels_r2.tsv` (held-out; the labels are in vault/ since the reveal).

**The MCP tool server, through the scripted client:**
`python3.13 tools/mcp_client.py --out transcripts/<a new name>.jsonl --call score_posting --args '{"board_key":"greenhouse:stripe","posting_id":"7737124"}' -- python3.13 tools/mcp_server.py`

**JS2's loop, live:** `python3.13 -m agent`. It writes state/, evidence/ and output/ in the folder it runs in, so run it in a throwaway copy (git archive), as JS3-SNAP did.

## What ran

| Run | Checkpoint | Output |
|---|---|---|
| JS2's agent, live, as itself, in a throwaway copy | JS3-SNAP | snapshots/ (run report and SHA-256s; bodies kept outside the repo, for JS4) |
| Seal: counts, draw, replacement draw | JS3-CP2c, CP2d, CP3e | vault/ |
| FILTER v1 over 1,298 postings, 50 sealed withheld | JS3-CP5d | output/filter_v1_2026-11-17T210612Z/ (1,248 judged, 0 kept) |
| Audit draw and five comparison passes | JS3-CP6c, CP6e, CP6g, CP6j, CP7f, CP11d | audit/ |
| Measurement of 9 variants on the development set | JS3-CP7d, CP7h, CP11d | output/measure_2026-11-1*/, output/measure_2026-11-20T205049Z/ |
| FILTER v2 over the corpus | JS3-CP8c | output/filter_v2_2026-11-19T201210Z/ (2 kept) |
| The MCP server with Claude Code, and the scripted probes | JS3-CP10c, CP10d | transcripts/ |
| The held-out measurement | JS3-CP11f | output/measure_heldout_2026-11-20T205452Z/ |

## Where everything is
FILTER.md, SEAL.md, AUDIT.md, SHORTLIST.md, TOOLSERVER.md, MEASURE.md, CONTRACT.md (v0.9–v0.12 for JS3), GATE.md (JS2's, unchanged); agent/ (JS2's agent, plus agent/filter.py); tools/ (seal_draw, label_view, filter_run, audit, measure, mcp_server, mcp_client, and JS2's helpers); tests/; vault/ (the sealed sets, hashes and, since the reveal, the held-out labels); audit/; shortlist/; output/; transcripts/; snapshots/.

## Sign-off — Job-Search Agent 3

**Checked:**
- FILTER v1 is JS2's rule exactly: the rule.py cross-check agreed on all 1,248 judged postings (output/filter_v1_2026-11-17T210612Z/summary.txt).
- The wrong versions W6–W8 are caught: tests/test_filter_wrong_versions.py, on the constructed postings FILTER.md §4 fixed on 2026-11-15, before the build.
- No sealed posting reached any output: my grep after every run (JS3-CP5d, CP7d, CP7h, CP8c, CP11d, CP11f).
- The seal held: both draws recomputed by me with the shell (counts, overlaps, the seen list, one rank each; SEAL.md §6, §8), and the held-out labels matched their committed SHA-256 at the reveal (SEAL.md §10).
- The audit: 94 postings labeled by me, blind, committed before any comparison (JS3-CP6d); every later pass committed with its reasons (audit/recheck_notes.txt). Group (A): 0 wrong rejects of 30, 95% interval 0% to 11.6%.
- The shortlist's 8 claims, labeled by me under FILTER.md §2 (shortlist/claim_labels.tsv).
- The MCP server: a real Claude Code session in both directions, and a sealed id refused through the scripted client (transcripts/).

**How:**
- By hand: every hand verdict (audit, held-out, claims), every hash check, every sealed-id grep, every search for years.
- By a test I wrote before reading Claude's code: W6–W8's postings and their right and wrong answers are mine, in FILTER.md §4 before the build; Claude Code typed the test code.
- By recomputation: one rank per draw with shasum; the interval's upper bound, 1 − 0.025^(1/30) = 11.6%.
- With Claude's help: Claude Code wrote all the code and tests to my prompts, asked when they were unclear, and planted bugs to show the tests fail. Claude.ai reviewed my decisions, wrote the shell checks I ran, and typed most of these documents at my request from the committed files.

**Not checked:**
- I did not read every line of Claude Code's code. I reviewed each tool's core logic before committing it and relied on the tests for the rest; the planted-bug checks were Claude Code's, not mine.
- F10's years pattern on phrasings outside its test list, such as years in words or company history, across the real corpus.
- The held-out set's not_worth labels: the re-check read only worth rows, so it could move labels only one way (SEAL.md §10).
- The filesystem server's write tools and symlink handling; the 2026-07-28 protocol, which my server does not implement.
- A second labeler: every hand verdict is mine, and the audit shows my own error rate (the Staff misread, the missed years).

**Not claiming:**
- That FILTER v2 finds the jobs worth Alex's time: on the held-out set it kept none and missed the one worth posting (MEASURE.md §2).
- Any accuracy rate for the corpus: only group (A) is random, and it gives an interval, not a rate. Groups (B) and (C) and the held-out set were chosen (SEAL.md §3).
- That anything learned: every change of behavior is a committed change to code or documents (MEASURE.md §3).
- That the MCP server keeps sealed postings safe from a determined user of the same machine, or works with clients other than the ones I observed.
- That any posting is worth applying to; that judgment stays mine.

**Signed or withheld:** Prasad Shinde, 2026-11-20

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine |
|---|---|---|---|
| The filter's rules (FILTER.md) | Propose structure and options, with reasons; flag gaps | Decide every rule, and write the hand standard (§5) myself | A rule Claude wrote, obeyed by code Claude wrote, would prove nothing |
| The seal | Design the mechanics; build the tools; never see the sealed labels | Fix the rules first, run the draws, keep the labels sealed | A seal only protects against my own tuning if I commit before I tune |
| Hand verdicts and claim labels | Show me the posting's own text and nothing else | Label every posting and every claim | What a posting is worth depends on what Alex wants from a job; Claude never labeled a posting |
| The build | Claude Code builds to my prompts, and stops and asks when they are unclear | Answer each question, review the core logic, run the tests, commit | The code is the labor; the acceptance is the accountability |
| The measurement | Build the measuring tools | Choose v2 on the development set before the held-out scoring, and keep it after | Choosing after seeing the held-out set would fake the measurement |
| Trusting a tool server | Probe it and report what it declares and does | Make the trust decision | Trust means accepting a risk on my machine |
| This sign-off | Draft it from the committed record | Check every line, and sign or withhold | I am the one who signs for it |

**Why the judgment that a posting is worth my time stays mine.** Twice in JS3 the standard itself needed a decision no rule or model could make. One was whether "Staff Product Manager" is a role for someone with three years: I misread it, and caught that only by re-reading under my own written standard. The other was whether a posting that prefers 5+ years still invites someone with fewer: I decided it does. Claude could build a filter that agrees with my verdicts, but not decide what my verdicts should be. On the held-out set, the filter I chose missed the one posting I would have wanted. That is the measurement, not a reason to hand the judgment over.