# Job-Search Agent 3: the filter, the tool, and the score

**Hemanth Rayudu, INFO 7375, Fall 2026.** My agent collects from three job boards. This layer decides what reaches the fictional persona **Priya Nair**, and why:
- **a filter you can read:** `FILTER.md` *is* the filter's configuration;
- **an audit of what it throws away;**
- **a shortlist** where every claim is checked against the posting's own words;
- **the agent offered to Claude as a tool,** through an MCP server written from scratch;
- **a score** whose every number has a stated origin, changed one object at a time and measured on held-out labels.

**Started from:**
- my own **JS2** (`../js2-loop-tools-diff/`, commit `9061037`), copied unchanged as commit `cf6b64d`;
- the **Reallocation Engine**'s greenhouse-watch scorer, whose numbers are inherited (ported to Python, credited);
- the instructor's **Lectern**, for the format of the filter log and the reject audit.

Details are in `SOURCES.md`.

| File | What it is |
|---|---|
| [`FILTER.md`](FILTER.md) | **The gate.** The filter as a document: rules with reasons and origins, the evidence rules, the expected sources, the wrong versions, the changelog. v1.0 was committed before any code (`12c826a`); v1.1 came after the audit |
| [`AUDIT.md`](AUDIT.md) | The reject audit: 30 random rejects and more, judged blind by hand; what the sample can say; the false friend; the rules added, cut or rejected |
| [`SHORTLIST.md`](SHORTLIST.md) | The source-grounded shortlist: every claim labeled supported / contradicted / insufficient; relevance vs entailment; the abstention rule and its counterexample |
| [`EVAL-OWN-SERVER.md`](EVAL-OWN-SERVER.md), [`EVAL-OTHER-SERVER.md`](EVAL-OTHER-SERVER.md) | The tool server and the two evaluations: declared vs actual, what a client isn't entitled to, the trust decisions |
| [`SCORE.md`](SCORE.md) | What moves the score: the origin of every number, one change at a time on held-out labels, and what persistence doesn't prove |
| `js3/` | the code (standard library only): `score.py`, `corpus.py`, `filterdoc.py`, `sample.py`, `audit.py`, `claims.py`, `shortlist.py`, `mcp_server.py`, `experiment.py`, `cli.py` |
| `jsagent/` | JS2's agent, unchanged (the loop, the policy, the providers, the Claude judge) |
| `tests/` | 102 tests: JS2's 52, plus the wrong versions (written before the code), the corpus counts, the shortlist checks, the tool server and the experiment harness |
| `audit/`, `shortlist/`, `experiments/`, `evals/`, `transcripts/` | the evidence: samples and seed, hand verdicts, Claude's raw replies, transcripts in both directions, the probe results |
| `runs/`, `CORPUS.sha256` | everything collected: three live snapshots, frozen by hash |
| [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) | what I used and what Claude contributed; my log |

## Language, toolchain, exact commands

- **Language:** Python 3.12.9, standard library only, plus pytest 8.3.3 for the tests. The code avoids anything newer than Python 3.9.
- **Claude Code 2.1.330 (`claude -p`):** needed only for the commands marked **[Claude]**. No API key.
- **Node 23.11.0 / npx 10.9.2:** needed only for the command marked **[Node]**.
- **Tested on:** macOS.

```bash
cd fall-2026/rayudu-h/js3-filter-tool-score
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                          # 102 tests; no network, no Claude

# Recompute every published number from committed files (no network, no Claude)
.venv/bin/python -m js3 filter                         # FILTER.md on all 1,176 postings -> filter-runs/v1.1/
.venv/bin/python -m js3 audit                          # -> audit/audit-results.md (the numbers in AUDIT.md)
.venv/bin/python -m js3 shortlist-final                # Claude's saved labels + hand check -> shortlist/
.venv/bin/python -m js3 experiment report              # saved experiment records -> experiments/report.md

# The tool server: a scripted session through the logging tap (no Claude)
.venv/bin/python scripts/mcp_smoke.py                  # -> transcripts/smoke-<time>.jsonl

# [Claude] Claude Code as the MCP client: copy mcp.example.json, fill in the absolute paths, then
claude -p "Which job postings are new since the Nov 7 snapshot (2026-11-07T184247-live) and kept by the filter?" \
  --model sonnet --mcp-config my-mcp.json --strict-mcp-config --tools "" \
  --allowedTools mcp__jsagent__search_new_postings --setting-sources "" --no-session-persistence \
  --output-format stream-json --verbose < /dev/null

# [Claude] Re-run the Claude parts (each refuses to overwrite a saved record; move the old one first)
.venv/bin/python -m js3 shortlist                      # 10 calls: label every claim
.venv/bin/python -m js3 experiment run E0a E0b E2 E3 E4   # 200 calls
.venv/bin/python scripts/persistence_rerun.py          # 20 calls; needs ../js1-contract-and-watch with its .venv

# [Node] The other server's evaluation (downloads @modelcontextprotocol/server-filesystem@2.2.0)
.venv/bin/python scripts/probe_other_server.py declare   # then: probe, roots
```

## What ran (Nov 20–22, 2026, EST)

| What | Result |
|---|---|
| Collection, Nov 20, 9:30 PM (the JS2 loop, unchanged, `--no-claude`) | 131 new postings; the two deliberate failures again had no result; the corpus is **1,176 unique postings** |
| The filter, v1.0 → v1.1 | kept 194 → **212**, rejected 982 → 964, cannot tell 0 |
| Blind hand verdicts, 2:23–3:24 PM | **95**: 55 audit + 40 held out, committed before any analysis |
| **The reject audit** | **11 of 30** random rejects wanted (22%–54%, about 210–524 postings; an estimate). Exclusions were right 14 of 14. **False friend: "Staff"** in Perplexity's "Member of Technical Staff". X1 accepted; X2, X3 and X4 measured and rejected |
| **The shortlist** (10 postings, 69 claims) | 69 of 69 quotes grounded; 69 of 69 agreed by hand; **3 rule breaks found afterwards** and corrected. Answers: 4 worth reading, 5 not for Priya, 1 I cannot tell |
| **The tool server** | Claude Code 2.1.330 used it; a gap it exposed ("can't say whether Notion postings were covered") was fixed and re-run |
| **The other server** (filesystem 2.2.0) | containment held for `..`, the prefix trick and symlinks; **a client's roots silently replaced the sandbox** |
| **The held-out experiments** (200 calls) | noise floor 0 flips; **the prompt flipped 21 of 40**; the context and the model flipped 0; the fitted threshold = the inherited 3.0 |
| **Persistence** | JS1's exact Oct 31 prompts (hashes verified) gave **20 of 20** identical verdicts on Nov 22, which is not evidence of memory or training |

## Sign-off: Job-Search Agent 3

```text
(draft, awaiting Hemanth's decision)
```

## Driver's seat

| Part | What Claude should do | What I should do | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter | propose wording, defaults and wrong versions; measure every word on the corpus before I decide | choose the role words, exclusions, seniority rule and threshold; accept or reject each measured change | the filter encodes what *I* think is worth Priya's time; a word list is a judgment about her career | FILTER.md section 7 (my replies, verbatim); changelog X1–X4 |
| The audit | draw the samples from a committed seed, show me postings blind, compute the intervals | give every verdict myself, without seeing the score | the audit measures the filter **against my judgment**. If Claude labeled, it would measure Claude against Claude | `audit/labels.csv` (timestamps); AUDIT.md section 1 |
| The shortlist | label every claim with a verbatim quote; re-check the labels against the written rule | check that each quote says what its label claims; decide on corrections | grounded quotes passed 69 of 69, and so did I, yet 3 labels broke the rule. Neither check alone is enough | SHORTLIST.md section 5; `shortlist/hand-check.csv` |
| The tool server | write it, test what it declares, record both directions, probe the other server against predictions | decide whether to trust each server, and on what conditions | trusting a tool means accepting what it can do with my files and my client; that's my risk | EVAL-OWN-SERVER.md section 5; EVAL-OTHER-SERVER.md section 6 |
| The score | run one change at a time on labels it never tuned on; report the noise floor | decide what agreement with my labels means | a higher agreement score only means closer to my judgment, not more correct | SCORE.md section 2 |
| **"Worth Priya's time"** | **give an opinion, with quotes** | **decide** | When Claude was asked **my exact question** (prompt v3), it said "not relevant" to all 40 held-out postings, where I said 19 were worth reading. The shortlist's claims all passed for a security role I had marked not relevant (#1). The claims can't capture what I weigh, and Claude's answer to my question isn't mine | SCORE.md section 2b (E2); SHORTLIST.md section 5 |
