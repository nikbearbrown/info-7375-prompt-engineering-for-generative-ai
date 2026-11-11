# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Saloni M · INFO 7375 · Fall 2026 · built and run 2026-11-10 (ET), before the 11:59 pm deadline.

**Started from:** my own Job-Search Agent 1 ([`../js1-contract-and-watch/`](../js1-contract-and-watch/)):
its https/host allow-list idea, its "first run is a baseline, nothing is new" rule, and its way of
storing seen ids (bare posting ids). The board list was chosen from the slugs in the instructor's
Lectern collector (`fall-2026/nik-bear-brown/lectern/sources.json`); no Lectern or Reallocation
Engine code was copied. JS2 does not call Claude at run time: it watches boards, it does not judge.

| Read this | For |
|---|---|
| [GATE.md](GATE.md) | exits, budgets, repeat rule, error policy, permission policy, wrong versions — committed first (`5d221da6`) |
| [TRACE.md](TRACE.md) | the agent trace of one real run, including the deliberate failure |
| [FINISHED-WRONG.md](FINISHED-WRONG.md) | a run that ends "finished" and is wrong, and the independent check that catches it |
| [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md) | 21 permission cases with my predictions (committed before the run) and the observed results |
| [REVIEW-PACKET.md](REVIEW-PACKET.md) | the Claude Code change I reviewed: reproduce, test first, diff, scope, my commands, my decision |
| [SIGNOFF.md](SIGNOFF.md) | sign-off and driver's seat |
| [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) | what came from where · my honest log |

## Language and toolchain

- **Python 3.13.5**, standard library only (`urllib`, `json`, `gzip`, `hashlib`, `unittest`). No
  `pip install`, no virtualenv, no API key, no Claude call at run time.
- macOS (Darwin 25.5), zsh. Any Python ≥ 3.9 should work; only 3.13.5 was run.
- Built with Claude Code (desktop app, Claude Opus 5.5) on 2026-11-10; see SOURCES.md.

## Exact commands (from a fresh clone)

```sh
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/saloni-m/js2-loop-tools-diff

python3 -m unittest discover -s tests -t . -v      # 50 tests, offline, < 1 s

python3 -m jsagent.run                            # live run; new history -> out/state/seen_ids.pending.json
python3 -m jsagent.run --approve-state            # live run; I approve overwriting out/state/seen_ids.json

cd scripts && python3 finished_wrong_demo.py --live-check && cd ..   # SIMULATED finished-wrong demo
python3 scripts/independent_check.py out/runs/<run_id>/report.json --state-before <state.json> [--live]
```

Exit codes of `jsagent.run`: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error. Every live run
makes 4 GETs (no retries were needed on 2026-11-10) and ends `incomplete`, because the
deliberately misspelled board returns 404, as GATE.md §4 requires.

A live run from a fresh clone compares against the committed `out/state/seen_ids.json` (live run
3's history), so it reports whatever was posted after 2026-11-11 00:56 UTC.

## What ran (all on 2026-11-10 ET = 2026-11-11 UTC)

| Run | Who ran it | Code | Result | Evidence |
|---|---|---|---|---|
| Live run 1 (00:41 UTC) | Claude Code | JS2-2 | `incomplete`: anthropic 679, figma 144, openai 826 (all baseline, 0 new); `anthropic-doesnotexist` **404, not retried, no counts** | `out/runs/20261111T004140Z-live/` |
| Boundary tests | Claude Code | JS2-5 | 21/21 pass; my predictions matched 19/21 (B03, B21 differ) | `review/03-boundary-run.txt` |
| Finished-wrong demo (**SIMULATED** figma emptied, other inputs real) | Claude Code | patch v2 | wrong version 1: `FINISHED, 0 new`; independent check: **CONTRADICTED** (144 saved before; live recount 144); real loop: `incomplete` | `out/demo/finished-wrong/` |
| Review: defect reproduced | **Saloni** | JS2-6 (stashed patch) | `FAILED (failures=1)`: board b's job 1001 hidden by board a's 1001 | `review/05-saloni-before-patch.txt` |
| Live run 2 (00:50 UTC) | **Saloni** | patch v1 | `incomplete`, **0 new — but OpenAI had 1 real new job, hidden by v1's re-baseline** | `review/07-saloni-live-run2.txt` |
| Live run 3 (00:56 UTC) | **Saloni** | patch v2 | `incomplete`, **1 new**: *Account Director, Mid-Market \| Korea* (OpenAI); history approved | `review/13-saloni-live-run3.txt` |
| Live run 4 (00:56 UTC) | **Saloni** | patch v2 | `incomplete`, 0 new (nothing new twice); history to pending, not approved | `review/14-saloni-live-run4.txt` |
| All tests | **Saloni** | patch v2 | 50/50 | `review/12-saloni-all-tests-v2.txt` |

Only four live runs exist, all within 15 minutes of one another. Raw responses are saved
byte-for-byte (gzip) before parsing, with the SHA-256 of the uncompressed bytes in each trace.

## Design in one paragraph

`jsagent/run.py` refuses to start (status `error`, zero requests) if `config/run.json` disagrees
with the budgets or hosts written in GATE.md. `jsagent/loop.py` visits each planned board once,
checks the request and seconds budgets before every request, skips a repeated method+host+path,
retries once only on a timeout or 5xx, saves the raw bytes, then classifies the response as ok,
suspicious-empty or failed. A failed or empty board reports no counts and never changes saved
history. `jsagent/policy.py` is the only gate to the network and the disk: exact-match https GET
hosts, credentials refused, redirects re-checked; reads inside the project, writes inside `out/`
after resolving symlinks, and overwriting the job history needs `--approve-state`. A job is
identified as `system:board:id`.
