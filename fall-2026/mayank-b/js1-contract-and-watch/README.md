# Job-Search Agent 1: The Contract and the Watch

Mayank Bhadrasen · INFO 7375 · Fall 2026

One board (Anthropic on Greenhouse), one fictional persona résumé (Priya Nair), new postings only, and two labeled verdicts per new posting: a **record** from my written rule, which anyone can recompute, and a **judgment** from Claude under a fixed output format and a validator. The contract came first: [CONTRACT.md](CONTRACT.md), commit `e936060`, before any code existed.

## Toolchain

| | |
|---|---|
| Language | JavaScript (ES modules) on Node.js 22 or later; built and tested on Node 24.8.0, npm 11.6.0, macOS |
| Dependency | `@anthropic-ai/sdk` 1.3.0 (the only one) |
| Tests | Node's built-in test runner (`node:test`), no test framework |
| Claude model | `claude-haiku-5-5`, effort `low`, one fresh API call per verdict |
| Board | `GET https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` (public, no login) |

## Setup and commands (from a fresh clone)

```bash
cd fall-2026/mayank-b/js1-contract-and-watch
npm install
cp .env.example .env            # then put your own ANTHROPIC_API_KEY in .env (git-ignored)

npm test                        # 21 tests; no network, no API key needed
node scripts/wrong-versions.js  # plants W1, W2, W5 into a temp copy and shows the tests catch each one
npm run check-persona           # validates the persona résumé
npm run watch                   # one run of the watch: live fetch, raw response saved, new postings judged
node src/cli.js rule <posting_id> --raw runs/<run>/raw-response.json   # recompute one rule verdict
```

The baseline run needs no API key (it reports nothing as new, so nothing is judged). Without a key, later runs still give the rule's verdict and record Claude's as `no_verdict`.

Seeded run, only if a live second run shows no change: `npm run watch -- --seeded-from runs/<earlier-run>/raw-response.json`. Its folder and report are labeled `seeded`.

Step 4 scripts (each Claude call is fresh; they read saved raw responses and never fetch the board):

```bash
npm run sample -- --raw runs/<run>/raw-response.json --ids <5 ids, comma-separated> --n 4
npm run experiment -- --prompt prompts/judge-v1.md --set dev
npm run experiment -- --prompt prompts/judge-v2.md --set heldout --final   # only at the very end
```

## Layout

| Path | What it is |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, wrong versions, the dated failure sentence |
| `notes/contract-questions-with-my-answers.md` | Claude's guided questions with my original answers (evidence for how the contract was written) |
| `persona/priya-nair.resume.json` | fictional persona with my `search` block (the rule's control panel) |
| `src/allowlist.js` | every request passes the host allow-list check first |
| `src/persona.js` | persona validator (`@example.com`, `555`), runs before any fetch |
| `src/rule.js` | the rule (record) |
| `src/claude.js`, `prompts/judge-v1.md` | the Claude judge (judgment), its prompt contract and validator |
| `src/watch.js`, `src/cli.js` | the watch: fetch, save raw, new-by-id, dedupe, state |
| `tests/` | the tests, including W1, W2, W5 and the failure sentence; `tests/fixtures/` holds constructed (not real) postings |
| `scripts/wrong-versions.js` | proves each wrong version is caught |
| `scripts/sample.js`, `scripts/experiment.js` | sampling report and prompt experiment |
| `state/seen-ids.json` | every posting id seen so far |
| `runs/run-NN-YYYY-MM-DD/` | `raw-response.json` (exactly as received) and `report.json` for each run |
| `labels/` | my hand labels (`labels.example.json` is the template) |
| `reports/` | sampling and experiment results |

## What ran

Past tense only for what ran and can be shown.

- 2026-10-28, during the build (run by Claude Code): `npm test` passed 21 of 21; `node scripts/wrong-versions.js` caught W1, W2 and W5; one live Claude call on posting 5448481008 ("Data Engineer, Product") returned a reply the validator accepted (verdict `relevant`, 2.5 s). That call was a development check and is not part of any report.
- I re-ran the tests myself: _pending_
- Run 1 (baseline): _pending_
- Run 2 (second calendar day): _pending_

## Sampling report (Chapter 1)

_pending_

## Prompt experiment (Chapter 2)

_pending_

## Action-surface comparison (Chapter 3)

_pending_

## Sign-off: Job-Search Agent 1

_pending: written by me_

## Driver's seat

_pending: written by me_
