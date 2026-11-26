# Job-Search Agent 3: the filter, the tool, and the score

**Status: in progress (2026-11-25).** This README is completed in Phase 6. It currently records the run commands and one deviation.

Started from my JS2 (`fall-2026/aravind-r/js2-loop-tools-diff/`, branch `js2-loop-tools-diff-aravind-r`). The data is a frozen copy of one JS2 live run from **2026-11-10**. **Nothing was fetched for JS3** (`data/MANIFEST.json`).

## Toolchain
- JavaScript (ES modules)
- Node.js v20.20.2, no dependencies
- Tests: `node --test`

Every command below runs from this folder:

```bash
~/.nvm/versions/node/v20.20.2/bin/node --test
```

The same thing with nvm:

```bash
nvm use 20 && node --test
```

## Deviation: Claude calls went through claude.ai by hand, not `claude -p`
The intended path was one tool-less `claude -p` call per shortlisted posting (`src/judge.mjs`). All 7 calls failed on 2026-11-26 at 00:03 UTC (2026-11-25, 19:03 ET) with "You've hit your individual spend limit". No reply came back (`runs/claude/justify.v1-v1.1.0-e/failed/`, commit `3caf2978`).

The fallback (FILTER.md §4):
1. The exact prompts are written to `runs/claude/justify.v1-v1.1.0-e/manual/prompts/`.
2. They are pasted into claude.ai (web, incognito chat). The raw replies are saved to `manual/responses/`.
3. The replies are imported with `tools/import-manual.mjs`, through the same validator, and each record is marked `manual_paste: true`.

Phase 5 prompt changes use the same route.

```bash
~/.nvm/versions/node/v20.20.2/bin/node tools/justify-shortlist.mjs --render
```

```bash
~/.nvm/versions/node/v20.20.2/bin/node tools/import-manual.mjs --model "<model as shown in claude.ai>" --date 2026-11-25
```

```bash
~/.nvm/versions/node/v20.20.2/bin/node tools/justify-shortlist.mjs --no-call
```
