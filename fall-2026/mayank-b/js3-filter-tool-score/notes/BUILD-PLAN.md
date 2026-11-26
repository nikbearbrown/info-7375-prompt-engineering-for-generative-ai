# JS3 build plan (a plan, not code)

Written by Claude Code on 2026-11-23. Nothing in this plan has run yet. It assumes the ★ answers in `FILTER-QUESTIONS.md`, and any answer you change changes the plan. **No code is written before CP1.**

## Commit order (JS3-CPn, the same as JS2)

| CP | What goes in | Why at this point |
|---|---|---|
| **CP1** | `FILTER.md` v0.1 (filter + reasons, evidence rules, expected sources + your dated count predictions, wrong versions WF1–WF6), `notes/filter-answers-<date>.md` (verbatim), `notes/FILTER-QUESTIONS.md`, `notes/BUILD-PLAN.md` | the gate comes before code (10 pts) |
| **CP2** | `config/filter.json` (the machine copy of FILTER.md v0.1), the seeds for every draw, the predicted results for the tool-server transition table (Ch 8 rows 1–10 + your cases), **the held-out draw design** | predictions and seeds are fixed before any output exists |
| **CP3** | the **one new fetch**: `runs/<id>-content/` (JS2 loop, `?content=true`, 3 requests, trace + raw + SHA-256) + a FILTER.md decisions-log line | the corpus is frozen before the filter sees it |
| **CP4** | `labels/heldout-sheet.md` (blind: no verdict or score columns), drawn by seed. **You label it, then commit it sealed.** | held-out labels exist before any rule is tuned |
| **CP5** | code + tests: `src/jsa3/filter.py`, `audit.py`, `shortlist.py`, `mcp_server.py`, the tests, and `scripts/wrong_versions.py` (WF1–WF6 each caught) | |
| **CP6** | the v0.1 run on the whole corpus: `runs/<id>-filter-v0.1/` (every record with matched words, and kept / rejected / cannot-tell) + `audit/reject-audit-v0.1.md` (blank verdicts) | |
| **CP7** | **your hand verdicts** in the audit sheet, the false friend named, and the error count with the honest sentence | your judgment is committed before any rule changes |
| **CP8** | FILTER.md v0.2: every rule added, cut or rejected **after measuring**, each with counts (Lectern's `removed_after_measurement` / `measured_before_adding`) | |
| **CP9** | the shortlist + Claude justifications (if Q13 = A: real responses, dated, model label) + `shortlist/claims.md` with **your** S/C/I labels | |
| **CP10** | tool-server transcripts (`transcripts/*.jsonl`, both directions, raw lines) + `EVAL-OWN-SERVER.md` + `EVAL-OTHER-SERVER.md` | |
| **CP11** | `SCORE.md`: where every number came from, the one change (v0.1 → v0.2 filter file) measured **once** on the sealed held-out, and the persistence statement | |
| **CP12** | README (commands, toolchain, what ran), SOURCES, FRICTIONAL, sign-off + driver's seat (with commit and transcript pointers), `review/run-review-commands.sh` + the output of **your** run | |

## Module layout (reuse JS2; nothing in JS2 changes)

```text
js3-filter-tool-score/
  FILTER.md  README.md  SOURCES.md  FRICTIONAL.md  SCORE.md  EVAL-OWN-SERVER.md  EVAL-OTHER-SERVER.md
  config/filter.json            # machine copy of FILTER.md; a test fails if the two disagree (JS2 test_gate_config pattern)
  config/boards.json budgets.json  # copied from JS2, + content=true
  persona/priya-nair.resume.json   # fictional, copied from JS2
  src/jsa/                      # JS2's policy.py, net.py, boards.py, loop.py (copied; boards.parse gains a `text` field)
  src/jsa3/filter.py            # pure: (posting, filter.json, persona) -> record {verdict, score, matched[], gates[], cannot_tell[]}
  src/jsa3/audit.py             # seeded draws -> Markdown sheets with blank verdict columns (Lectern audit_rejects.py shape)
  src/jsa3/shortlist.py         # claims C1–C5 per kept posting; optional Claude call (allow-list adds api.anthropic.com for this script only)
  src/jsa3/mcp_server.py        # stdio JSON-RPC: initialize, notifications/initialized, tools/list, tools/call(score_posting)
  scripts/mcp_record.py         # drives the server, writes every line in and out to transcripts/
  scripts/wrong_versions.py     # plants WF1–WF6
  tests/                        # test_filter, test_audit, test_mcp (lifecycle table), test_policy (from JS2), test_config_matches_filter_md
  runs/  audit/  labels/  shortlist/  transcripts/  review/  notes/
```

- **Permission policy:** JS2's `policy.py` is unchanged. Reads stay where they were. Writes go only to `runs/<id>/`, and nothing else is writable without approval.
- **The MCP server imports `filter.py` only.** It never imports `net.py`, and a test asserts that, so the server can't reach the network.

## Audit sheet format (`audit/reject-audit-v0.1.md`; a CSV twin is optional)

Header: filter version, corpus run id + SHA-256, seed, population sizes (rejects N, close calls N, kept N), draw rule.

| # | part | board | id | title | location | score | matched (where) | text snippet (≤ 240 chars around the first match) | **your verdict** (keep / reject / cannot tell) | **why** (1 line) | filter wrong? |
|---|---|---|---|---|---|---|---|---|---|---|---|

- Part 1 is the uniform random rejects (n = 30). Part 2 is the close calls (score T−1). Part 3 is the kept sample (n = 10).
- The last three columns are **blank**. Claude never fills them.
- The held-out sheet uses the same columns **without** the score, matched or verdict columns (blind).
- Summary block, filled in after your verdicts: k wrong per part, the honest sentence (Q10b), the false friend with its count across the corpus.

## Tool-server transcript plan

1. **Transcript A** (`scripts/mcp_record.py`, scripted client). This is the full lifecycle:
   - `tools/list` sent before initialize, which should get `-32000`;
   - `initialize`, then `tools/list` without the notification, which should still get `-32000` (WF6);
   - `notifications/initialized` (no response);
   - `tools/list`;
   - `tools/call` on a real kept id;
   - `tools/call` on an unknown id, which should return a result with `isError: true`;
   - `tools/call` with a bad argument, which should get `-32602`;
   - an unknown method, which should get `-32601`;
   - the text `{`, which should get `-32700`.

   Every line in and out is saved raw with a timestamp.
2. **Transcript B: a real client.** Claude Code connected via a project-local `claude mcp add`. You ask it to score one posting, and the server logs the raw stdio both ways. The host configuration is recorded: command, cwd and enabled tools, with no secrets.
3. **Evaluations.** Each one has the four ledgers, declared vs actual, what a compatible client is not entitled to infer (that "read-only" in the description is the server's testimony, and that a result isn't a fact about the world), the decision, and a re-review trigger. The other server is Chapter 8's `lessons/08-mcp-from-scratch/code/main.py` at a pinned commit, run with your recorded messages.

## Held-out split

- **Labels.** Held-out H is 30 postings, stratified 10 / 10 / 10 by v0.1 fate, drawn by a committed seed. Development D is the reject-audit items. H and D don't overlap, and the draw excludes D's ids.
- **Order.** You label H blind at CP4, before CP6 shows any filter output. H is used **once**, at CP11, for the v0.1 vs v0.2 comparison. Any second use is recorded as "H is now development data".
- **Report.** Agreement on H, false keeps, false rejects, before and after. The claim is limited to "these 30 postings in this snapshot".

## Timeline

**Track W (due Wednesday 11/25)**
- **Mon 11/23 evening:** you answer the sheet (30 min) → CP1. Claude writes CP2. Fetch → CP3.
- **Tue 11/24:** you label H (40 min) → CP4. Claude builds and tests → CP5. v0.1 run → CP6. You do the reject audit (60 min) → CP7. CP8.
- **Wed 11/25 day:** shortlist and your claim labels (45 min) → CP9. Transcripts and evaluations → CP10. CP11. Docs, review commands, sign-off → CP12. Push, zip, Canvas, all before 23:59.

**Track T (due tonight, if Q0 = B)** Everything happens tonight, about 7.5 h of wall clock from 16:15 ET.
- Keep: CP1, CP3, the v0.1 filter, the audit with 30 rejects + close calls + 10 kept, the shortlist with ~10 postings, Transcript A + the teaching-server evaluation, and the one change measured on H = 20.
- Drop: Transcript B (the real client) and the second Claude re-run, recorded as "Not checked".
- Your hand work is still about 3 h, and that's the critical path.

**Zip:** `Bhadrasen_Mayank_INFO7375_JS3.zip`, a `git archive` of the final commit's folder, as in JS2.
