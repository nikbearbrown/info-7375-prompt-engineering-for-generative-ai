# Job-Search Agent 3: the filter, the tool, and the score

INFO 7375, Chapters 7–9. This layer decides which job postings reach the job seeker, and why:
- **a filter you can read:** `FILTER.md`, versioned, with the reason for every rule
- **a reject audit** judged by hand
- **a source-grounded shortlist,** with every claim labeled
- **a from-scratch MCP tool server,** with real client transcripts and two evaluations
- **a report on what moves the score,** with every number's origin and one change measured on
  held-out labels

The job seeker is the fictional persona **Maya Sehgal**. No real résumé is used anywhere.

**Started from:** my JS2, `fall-2026/aravind-r/js2-loop-tools-diff/` (branch
`js2-loop-tools-diff-aravind-r`, tip `066ad25f`). JS3 is its own branch,
`js3-filter-tool-score-aravind-r`, cut from `origin/main`, so the diff contains JS3 only.

**Data:** a frozen copy of one JS2 live run from **2026-11-10**, 1,064 postings:
- Greenhouse: Stripe 776, Airbnb 203
- Lever: Spotify 85
- a deliberately broken board, which is reported as unavailable

`data/MANIFEST.json` records the SHA-256 of each file. **Nothing was fetched for JS3.** The JS2
allow-list is unchanged and unused.

## Language and toolchain

| | Version |
|---|---|
| Language | JavaScript, ES modules (`.mjs`) |
| Runtime | **Node.js 20.x**: developed and tested on v20.20.2 |
| Dependencies | **none**: Node built-ins only, no `package.json` |
| Tests | `node --test` (built-in runner) |
| Claude, intended path | `claude` CLI **2.1.323**, `claude -p`, tool-less (`src/judge.mjs`). It failed on the spend limit (see Deviations). |
| Claude, used path | claude.ai web, incognito chat, model **Claude Opus 5.5** (as shown in the selector; self-reported) |
| MCP clients that connected | Claude Code 2.1.323; Claude Desktop (`claude-ai` 0.1.0, `local-agent-mode-js3-filter` 1.0.0) |
| Git | branch `js3-filter-tool-score-aravind-r` on the fork `aravindravi7/prompt-engineering-and-agentic-ai`; final-filter tag `js3-filter-final` |

## Commands

Run from this folder, `fall-2026/aravind-r/js3-filter-tool-score/`, with Node 20.x on the PATH, for
example after `nvm use 20`.

> **Note about my machine:** its default `node` is v24, so I ran every command with the full path
> `~/.nvm/versions/node/v20.20.2/bin/node` in place of `node`.

```bash
cd fall-2026/aravind-r/js3-filter-tool-score
```

The tests (no network; synthetic fixtures plus the frozen snapshot; 71 tests):

```bash
nvm use 20
```

```bash
node --test
```

Run the final filter (v1.1.0-e) over the snapshot. It writes `runs/filter/v1.1.0-e/`:

```bash
node tools/run-filter.mjs
```

Recompute the audit results from the hand verdicts. View B uses the final filter by default:

```bash
node tools/audit-results.mjs
```

Known-limit counts and the sponsor/visa grep (measurement only):

```bash
node tools/known-limits.mjs
```

```bash
node tools/grep-sponsor.mjs > audit/sponsor-visa-hits.md
```

Phase 3: render the exact prompts, import the pasted replies, build the claim table, apply the
confirmed labels:

```bash
node tools/justify-shortlist.mjs --render
```

```bash
node tools/import-manual.mjs --model "Claude Opus 5.5 (as shown in the claude.ai model selector)" --date 2026-11-25
```

```bash
node tools/justify-shortlist.mjs --no-call
```

```bash
node tools/confirm-claims.mjs
```

The MCP server, over stdio. A client starts it; for the client config, see
`mcp/client-config.example.json`:

```bash
node mcp/server.mjs
```

```bash
claude mcp add js3-filter -- "$(command -v node)" "$PWD/mcp/server.mjs"
```

Claude Desktop config (used for the 3 real `tools/call`). Add this to
`~/Library/Application Support/Claude/claude_desktop_config.json` (back the file up first), then
restart Claude Desktop:

```json
{
  "mcpServers": {
    "js3-filter": {
      "command": "<ABSOLUTE PATH TO A NODE 20.x BINARY>",
      "args": ["<ABSOLUTE PATH TO>/fall-2026/aravind-r/js3-filter-tool-score/mcp/server.mjs"]
    }
  }
}
```

The judge tool (blind; shows no score, decision, or stratum; saves after every row). Audit, the
recheck, and labels:

```bash
node tools/judge-audit.mjs
```

```bash
node tools/judge-audit.mjs --recheck plan
```

```bash
node tools/judge-audit.mjs --sheet labels/label-sheet.csv
```

Phase 5: evaluate a run against the dev labels. Held-out requires `--heldout-final --why "…"`, and
every held-out evaluation is logged:

```bash
node tools/eval-labels.mjs --run runs/filter/v1.1.0-e --set dev
```

**Not to be re-run:**
- `tools/make-samples.mjs` would redraw the audit and label sheets. It refuses to overwrite a sheet
  with any verdict in it.
- `tools/judge-audit.mjs` on a sheet that is already filled: it only offers empty rows, so re-running is harmless but pointless.

## What ran (past tense, with evidence)

| What | Result | Evidence |
|---|---|---|
| The gate | `FILTER.md` v1.0.0 and the wrong-version tests were committed **before any filter code** | `bb88c420` (no `src/` existed) |
| Filter v1.0.0 on the snapshot | keep 0, cannot_tell 3, reject 1,061 | `13b4c6c4` |
| Reject audit, v1.0.0 vs Aravind's first pass | random rejects: **2 of 30** false rejects (estimate 6.7%, exact 95% interval 0.8–22.1%, for v1.0.0's 1,061 rejects in this snapshot only); 12 of 15 closest calls disagreed | `audit/RESULTS.md`, `1c9ce17b` |
| Recheck (14 rows) and persona correction | 10 verdicts revised. Experience policy corrected **after** the audit (≤4 / 5–6 / never 7+). | `c711833a`, `f3cefa22` |
| Filter changes v1.1.0-a…e, each with its own commit and measurement | final v1.1.0-e: keep 4, cannot_tell 3, reject 1,057, vetoes 2. Final filter vs final verdicts: random rejects 0/30 (95% upper bound 11.6%), closest calls 0/15 (dev use) | `FILTER.md` §9, tag `js3-filter-final` (`70c22c16`) |
| False friend | primary: **"program manager"** in the title rule (A027, A044, A052); secondary: "training" (Airbnb pay boilerplate, not a filter word) | `audit/RESULTS.md` |
| Phase 3 Claude calls (`claude -p`) | **all 7 failed** (spend limit, no reply) | `3caf2978` |
| What did **not** run | `claude -p` for the justifications (spend limit, 0 tokens, no reply); a `tools/call` from Claude Code (same limit); any prompt or context change in Phase 5 (no held-out posting labeled relevant or cannot_tell) | `3caf2978`, `82f18acc`, `phase5/RESULTS.md` |
| Phase 3 via claude.ai (manual) | 7 valid replies, 54 claims, all quotes verbatim. Aravind confirmed 37 supported / 6 contradicted / 11 insufficient. | `shortlist/SHORTLIST.md`, `ffd5e49f` |
| MCP server, real clients | Claude Code: handshake and `tools/list` (`tools/call` blocked by the spend limit). Claude Desktop: 3 real `tools/call` (keep; veto with quote; `../../README.md` refused). | `transcripts/README.md`, `592026e1` |
| Phase 5 diff-set (post hoc, not held-out) | Of the 12 postings threshold 0.70 adds as keeps, Aravind labeled **3 relevant, 9 not** (3/12, exact 95% interval 5.5–57.2%). D09 = A065 is a false reject under the final filter (0.775). | `phase5/RESULTS.md`, `5540e14b` |
| Phase 5 | Held-out has **0 relevant** of 20. The baseline and threshold 0.70 both surfaced 0, so recall and the change could not be measured. No number was fitted on labels. | `phase5/RESULTS.md`, `phase5/ORIGINS.md` |

## Where each deliverable is

| Assignment item | File |
|---|---|
| FILTER.md (filter, evidence rules, sources, wrong versions, CHANGELOG) | `FILTER.md` |
| Code and tests | `src/`, `tools/`, `test/`, `testlib/` |
| Reject audit with hand verdicts | `audit/audit-sheet.csv`, `audit/RESULTS.md`, `audit/results.json`, `audit/known-limits.json`, `audit/sponsor-visa-hits.md` |
| Source-grounded shortlist and its labels | `shortlist/SHORTLIST.md`, `shortlist/claims-confirmed-justify.v1-v1.1.0-e.csv`, `runs/claude/justify.v1-v1.1.0-e/` |
| Tool server, transcripts, both evaluations | `mcp/server.mjs`, `transcripts/`, `evaluations/own-server.md`, `evaluations/filesystem-server.md` |
| One-change-at-a-time report | `phase5/ORIGINS.md`, `phase5/PLAN.md`, `phase5/RESULTS.md`, `phase5/heldout-log.jsonl`, `experiments/` |
| Sign-off and driver's seat | `SIGNOFF.md` |
| SOURCES / FRICTIONAL | `SOURCES.md`, `FRICTIONAL.md` |
| Labels (dev / held-out) | `labels/label-sheet.csv`, `labels/heldout.frozen.json` |

## Deviations

1. **Claude calls went through claude.ai by hand, not `claude -p`.** All 7 `claude -p` calls failed
   on 2026-11-26 at 00:03 UTC (2026-11-25, 19:03 ET) with "You've hit your individual spend limit".
   - The prompts were rendered byte-identical to the failed calls, pasted into claude.ai (web,
     incognito), and the replies imported through the same validator (`manual_paste: true`).
   - The model name is self-reported, and claude.ai's own system prompt is not controlled.
   - FILTER.md §4.
2. **Claude Code's MCP session never reached `tools/call`** (the same spend limit). The real
   `tools/call` transcript comes from Claude Desktop.
3. **The definition changed after the first audit results** (the persona's experience policy;
   `f3cefa22`). This is dated and labeled everywhere it is used.

## Privacy and boundaries

- Persona only: the résumé is the fictional example from The Reallocation Engine, and its emails
  end `@example.com`.
- No credentials or caches are committed (`.gitignore`). The local MCP config with absolute paths
  is ignored; `mcp/client-config.example.json` uses placeholders.
- The agent never applies, emails, messages, or logs in.
- The MCP server is read-only. It writes only its own transcript, inside this folder.
