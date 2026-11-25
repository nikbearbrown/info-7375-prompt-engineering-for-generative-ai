# Job-Search Agent 3: the filter, the tool, and the score

**Hemanth Rayudu, INFO 7375, Fall 2026.** My agent collects from three job boards. This layer decides what reaches the fictional persona **Priya Nair**, and why:
- **a filter you can read:** `FILTER.md` *is* the filter's configuration;
- **an audit of what it throws away;**
- **a shortlist** where every claim is checked against the posting's own words;
- **the agent offered to Claude as a tool,** through an MCP server written from scratch;
- **a score** whose every number has a stated origin, changed one object at a time and measured on held-out labels.

**The central finding:**
- My first 115 hand verdicts were made with a view that **never showed the experience requirement** (0 of 90 postings that state one).
- Shown it, I changed **39 of 90** verdicts.
- That reversed the audit: the filter's problem was precision, not recall.
- One rule fixed most of it (v1.2: reject when the text asks for 5+ years).

See `AUDIT.md` section 8 and `SCORE.md` section 2c.

**Started from:**
- my own **JS2** (`../js2-loop-tools-diff/`, commit `9061037`), copied unchanged as commit `cf6b64d`;
- the **Reallocation Engine**'s greenhouse-watch scorer, whose numbers are inherited (ported to Python, credited);
- the instructor's **Lectern**, for the format of the filter log and the reject audit.

Details are in `SOURCES.md`.

| File | What it is |
|---|---|
| [`FILTER.md`](FILTER.md) | **The gate.** The filter as a document: rules with reasons and origins, the evidence rules, the expected sources, the wrong versions, the changelog. v1.0 was committed before any code (`12c826a`); v1.1 came after the audit; **v1.2** after the second labeling pass |
| [`AUDIT.md`](AUDIT.md) | The reject audit: 30 random rejects and more, judged blind by hand; what the sample can say; the false friends; the rules added, cut or rejected; **section 8: the second labeling pass and the corrected labels** |
| [`SHORTLIST.md`](SHORTLIST.md) | The source-grounded shortlist: every claim labeled supported / contradicted / insufficient; relevance vs entailment; the abstention rule and its counterexample |
| [`EVAL-OWN-SERVER.md`](EVAL-OWN-SERVER.md), [`EVAL-OTHER-SERVER.md`](EVAL-OTHER-SERVER.md) | The tool server and the two evaluations: declared vs actual, what a client isn't entitled to, the trust decisions |
| [`SCORE.md`](SCORE.md) | What moves the score: the origin of every number, one change at a time on held-out labels, and what persistence doesn't prove |
| `js3/` | the code (standard library only): `score.py`, `corpus.py`, `filterdoc.py`, `sample.py`, `audit.py`, `claims.py`, `shortlist.py`, `mcp_server.py`, `experiment.py`, `x1test.py`, `relabel.py`, `labeling.py`, `cli.py` |
| `jsagent/` | JS2's agent, unchanged (the loop, the policy, the providers, the Claude judge) |
| `tests/` | 107 tests: JS2's 52, plus the wrong versions (written before the code), the corpus counts, v1.1 and v1.2 rules, the shortlist checks, the tool server and the experiment harness |
| `audit/`, `shortlist/`, `experiments/`, `evals/`, `transcripts/` | the evidence: samples and seed, hand verdicts, Claude's raw replies, transcripts in both directions, the probe results |
| `runs/`, `CORPUS.sha256` | everything collected: three live snapshots, frozen by hash |
| [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) | what I used and what Claude contributed; my log |

## Language, toolchain, exact commands

- **Language:** Python, standard library only, plus pytest 8.3.3 for the tests. Developed on Python 3.12.9. A fresh copy of the final committed folder was also tested on **Python 3.9.6** (macOS's `/usr/bin/python3`): see "What ran".
- **Claude Code 2.1.330 (`claude -p`):** needed only for the commands marked **[Claude]**. No API key.
- **Node 23.11.0 / npx 10.9.2:** needed only for the command marked **[Node]**.
- **Tested on:** macOS.

```bash
cd fall-2026/rayudu-h/js3-filter-tool-score
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                          # 107 tests; no network, no Claude

# Recompute every published number from committed files (no network, no Claude)
.venv/bin/python -m js3 filter                         # FILTER.md (v1.2) on all 1,176 postings -> filter-runs/v1.2/
.venv/bin/python -m js3 audit                          # first-pass labels -> audit/audit-results.md
.venv/bin/python -m js3 audit --labels corrected       # corrected labels  -> audit/audit-results-corrected.md
.venv/bin/python -m js3 relabel report                 # first vs second pass -> audit/relabel-results.md
.venv/bin/python -m js3 x1test report                  # add --labels corrected for the corrected version
.venv/bin/python -m js3 experiment report              # add --labels corrected -> experiments/report-corrected.md
.venv/bin/python -m js3 shortlist-final                # Claude's saved labels + hand check -> shortlist/

# The tool server: a scripted session through the logging tap (no Claude)
.venv/bin/python scripts/mcp_smoke.py                  # -> transcripts/smoke-<time>.jsonl

# [Claude] Claude Code as the MCP client: copy mcp.example.json, fill in the absolute paths, then
claude -p "Which job postings are new since the Nov 7 snapshot (2026-11-07T184247-live) and kept by the filter?" \
  --model sonnet --mcp-config my-mcp.json --strict-mcp-config --tools "" \
  --allowedTools mcp__jsagent__search_new_postings --setting-sources "" --no-session-persistence \
  --output-format stream-json --verbose < /dev/null

# [Claude] Re-run the Claude parts (each refuses to overwrite a saved record; move the old one first)
.venv/bin/python -m js3 shortlist                      # 10 calls: label every claim
.venv/bin/python -m js3 experiment run E0a E0b E2 E3 E4 E5   # 240 calls
.venv/bin/python scripts/injection_test.py             # SEEDED: one Claude Code session
.venv/bin/python scripts/persistence_rerun.py          # 20 calls; needs ../js1-contract-and-watch with its .venv

# [Node] The other server's evaluation (downloads @modelcontextprotocol/server-filesystem@2.2.0)
.venv/bin/python scripts/probe_other_server.py declare   # then: probe, roots
```

## What ran (Nov 20–24, 2026, EST)

| What | Result |
|---|---|
| Collection, Nov 20, 9:30 PM (the JS2 loop, unchanged, `--no-claude`) | 131 new postings; the two deliberate failures again had no result; the corpus is **1,176 unique postings** |
| The filter, v1.0 → v1.1 → v1.2 | kept 194 → 212 → **105**; v1.2's new rule R17 rejected 107 postings that v1.1 kept; cannot tell 0 |
| Blind hand verdicts, 2:23–3:24 PM | **95**: 55 audit + 40 held out, committed before any analysis |
| **The reject audit** | **11 of 30** random rejects wanted (22%–54%, about 210–524 postings; an estimate). Exclusions were right 14 of 14. **False friend: "Staff"** in Perplexity's "Member of Technical Staff". X1 accepted; X2, X3 and X4 measured and rejected |
| **The shortlist** (10 postings, 69 claims) | 69 of 69 quotes grounded; 69 of 69 agreed by hand; **3 rule breaks found afterwards** and corrected. Answers: 4 worth reading, 5 not for Priya, 1 I cannot tell |
| **The tool server** | Claude Code 2.1.330 used it; a gap it exposed ("can't say whether Notion postings were covered") was fixed and re-run |
| **The other server** (filesystem 2.2.0) | containment held for `..`, the prefix trick and symlinks; **a client's roots silently replaced the sandbox** |
| **The held-out experiments** (200 calls) | noise floor 0 flips; **the prompt flipped 21 of 40**; the context and the model flipped 0; the fitted threshold = the inherited 3.0 |
| **Persistence** | JS1's exact Oct 31 prompts (hashes verified) gave **20 of 20** identical verdicts on Nov 22, which is not evidence of memory or training |
| **Second labeling pass** (Nov 23–24) | the first view had shown the experience requirement in **0 of 90** postings that state one. Re-shown with it visible, **39 of 90** verdicts changed (35 relevant → not relevant). Corrected audit: misses **3/30** (not 11/30); kept but unwanted **7/15** (not 2/15). The problem was precision |
| **v1.2** (Nov 24; decisions delegated: "Do whatever you recommend…") | R17 accepted: reject at 5+ years (cut-off fitted, ranges by lower bound). Y1, Y2, Y3, Y5 rejected. Corrected tuning labels: 57 → **70/75**, precision 56% → 87%. **Held-out (corrected): false keeps 18 → 7, relevant kept 2 → 2.** Keeping nothing would still score higher on accuracy (35/40, since only 5 of the 40 are relevant), so accuracy isn't the measure here |
| **Follow-ups after "Are you sure we are doing it right?"** (Nov 22–23) | **X1 out of sample:** on 10 never-labeled postings X1 changes, v1.1 was right 7/10 and v1.0 3/10 (`audit/x1-results.md`). **E5**, context under prompt v3: 0 verdict flips, but confidence rose. **SEEDED injection** through my server: Claude didn't follow the planted instruction, and warned Priya not to email contact details (`EVAL-OWN-SERVER.md` section 6) |

## Sign-off: Job-Search Agent 3

```text
Sign-off — Job-Search Agent 3
Checked:      (1) the six wrong versions W1-W6, by tests committed before any filter code
                  (tests/test_js3_wrong_versions.py, 47d33ef); they failed then only because
                  js3 did not exist yet, and all pass now; R17 by tests/test_js3_v12.py
              (2) the filter against my own blind verdicts: 115 first-pass (55 audit, 40 held out
                  and committed before any experiment, 20 for the X1 test) and 90 second-pass
                  verdicts with the experience requirement visible (audit/labels-v2.csv)
              (3) all 69 shortlist claim labels, by hand, in two passes (shortlist/hand-check.csv)
              (4) what my tool server declares against what it does
                  (tests/test_js3_mcp_server.py; Claude Code transcripts; one SEEDED injection run)
How:          by hand: 115 + 90 verdicts and 69 claim checks;
              by a test written before the code: W1-W6 (Claude wrote them from the list I accepted);
              by recomputation: js3 audit / relabel report / x1test report / experiment report /
                  shortlist-final regenerate every published number, for both label sets;
              with Claude's help: all code, the first-pass claim labels, the rule re-check that
                  found 3 labels I had passed, the labeling views (and the defect fixed in view v2
                  before I saw it), both server evaluations, every experiment, and the v1.2
                  decisions, which I delegated on Nov 24
Not checked:  v1.2 on postings labeled after it existed (the held-out set has only 5 relevant);
              the 4 postings new to the v1.2 shortlist (no claim labels, no hand check);
              the 25 labeled postings that state no years were not shown again, and other facts
                  a view can hide (domain, visa) were not tested;
              prompt injection beyond one crafted note with a fake link;
              the filesystem server on its supported runtime (Node >= 24), and its resources capability;
              how often Claude's claim labels change between runs (each posting was labeled once);
              a second labeler: my second pass came one day after my first, on familiar titles
Not claiming: that 3/30 (3-26%) or 11/30 is a measured miss rate for the corpus;
              that v1.2 is better by accuracy: on the held-out set keeping nothing scores higher;
                  the gain shown is fewer false keeps (18 -> 7) with no relevant posting lost;
              that the filter or Claude knows what is worth Priya's time;
              that any sameness or change across sessions reflects training;
              that the snapshots are complete or current after Nov 20
Signed or withheld: ____________ (Hemanth to sign or withhold)
```

## Driver's seat

| Part | What Claude should do | What I should do | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter | propose wording, defaults and wrong versions; measure every word on the corpus before I decide | choose the role words, exclusions, seniority rule and threshold; accept or reject each measured change | the filter encodes what *I* think is worth Priya's time; a word list is a judgment about her career | FILTER.md section 7 (my replies, verbatim); changelog X1–X4 |
| The audit | draw the samples from a committed seed, show me postings blind, compute the intervals | give every verdict myself, without seeing the score | the audit measures the filter **against my judgment**. If Claude labeled, it would measure Claude against Claude | `audit/labels.csv` (timestamps); AUDIT.md section 1 |
| **The labeling view** | choose what each item shows by one fixed rule; measure what the view hides | judge with the deciding facts in front of me, and say when I couldn't see them | the view Claude picked hid the experience line in 90 of 90 postings that have one, and 39 of my verdicts changed once I saw it. My judgment is only as good as what I'm shown, and only I could notice what was missing | AUDIT.md section 8; `audit/labels-v2.csv` |
| The shortlist | label every claim with a verbatim quote; re-check the labels against the written rule | check that each quote says what its label claims; decide on corrections | grounded quotes passed 69 of 69, and so did I, yet 3 labels broke the rule. Neither check alone is enough | SHORTLIST.md section 5; `shortlist/hand-check.csv` |
| The tool server | write it, test what it declares, record both directions, probe the other server against predictions | decide whether to trust each server, and on what conditions | trusting a tool means accepting what it can do with my files and my client; that's my risk | EVAL-OWN-SERVER.md section 5; EVAL-OTHER-SERVER.md section 6 |
| The score | run one change at a time on labels it never tuned on; report the noise floor | decide what agreement with my labels means | a higher agreement score only means closer to my judgment, not more correct | SCORE.md section 2 |
| **"Worth Priya's time"** | **give an opinion, with quotes** | **decide** | When Claude was asked **my exact question** (prompt v3), it said "not relevant" to all 40 held-out postings. On my corrected labels it agrees with all 35 negatives, but it finds **none** of the 5 postings I do want. The shortlist's claims all passed for a security role I had marked not relevant (#1). The claims can't capture what I weigh, and Claude's answer to my question isn't mine | SCORE.md sections 2b and 2c; SHORTLIST.md section 5 |
