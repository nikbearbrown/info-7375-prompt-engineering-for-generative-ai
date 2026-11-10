# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Tushar Patel · INFO 7375 · Fall 2026 · Due November 10, 2026

I extended my JS1 Stripe watch in `fall-2026/tushar-p/js1-contract-and-watch/` at `cb4333e` into a bounded Python loop. It fetches public listings, validates posting IDs, and compares each board with its own saved state. The first successful fetch establishes a baseline and reports zero new IDs. The permission checks run in code before the request or file operation.

| Board | System | Role |
|---|---|---|
| Stripe | Greenhouse | Public listing |
| Notion | Ashby | Public listing |
| Linear | Ashby | Public listing |
| `info7375-tushar-js2-deliberately-invalid-20261109` | Greenhouse | Deliberate 404 |

I used Python 3.12.10 on macOS with zsh and Git. The agent uses the standard library. The tests use pytest 9.2.0, pinned in [requirements.txt](requirements.txt). I used Claude Code for implementation and patch work.

## Run from a fresh clone

From the repository root, use Python 3.12 if available. I tested with Python 3.12.10.

```bash
cd fall-2026/tushar-p/js2-loop-tools-diff
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

The tests run offline and block real sockets. The final saved run passed all 132 tests. [Test output](evidence/test-runs/full-suite-final.txt)

### Live watch

This command makes public HTTPS requests. With all three real boards reachable, I expect three successes, one deliberate 404, and exit code 3. The command prints the run's summary path. The same run folder contains the trace, raw responses, and a snapshot of the state the agent started with.

```bash
.venv/bin/python -m agent --config config/boards.json --out out
printf 'Agent exit: %s\n' "$?"
```

The CLI exits with `0` for `finished`, `2` for `error`, `3` for `incomplete`, and `4` for `budget-exhausted`. The time window can stop live work. A valid config can use at most 10 attempts, so the separate 12-attempt guard is exercised directly in tests.

To check a run independently, pass its run folder to `checks/independent_count.py`. This example uses the saved live evidence and needs no network:

```bash
.venv/bin/python checks/independent_count.py evidence/runs/live-2-after-ua-patch/
```

### Offline comparison and deliberately wrong demo

These two runs start from identical October 27 seen IDs and replay the same October 28 response. The ordinary replay reports 16 new IDs. The deliberately wrong replay substitutes an empty listing after saving the original bytes. Both agent runs exit `finished`. The checker should exit 0 for the ordinary replay and 1 for the wrong replay.

```bash
demo_root=$(mktemp -d "${TMPDIR:-/tmp}/info7375-js2-demo.XXXXXX")
for demo in fixture seeded-wrong; do
  demo_out="$demo_root/$demo"
  mkdir -p "$demo_out"
  cp fixtures/seed-state-2026-10-27.json "$demo_out/state.json"

  demo_flags=()
  if [ "$demo" = seeded-wrong ]; then
    demo_flags=(--seed-wrong-empty)
  fi

  .venv/bin/python -m agent --config config/seed-demo.json --out "$demo_out" \
    --fixture fixtures/greenhouse-stripe-2026-10-28-from-js1.json "${demo_flags[@]}"
  printf 'Agent exit: %s\n' "$?"
  .venv/bin/python checks/independent_count.py "$demo_out"/runs/*/
  printf 'Checker exit: %s\n' "$?"
done
```

The README command was verified with Bash. [Saved output](evidence/finished-wrong-answer/readme-demo-check.txt)

## What I recorded on November 9

| Run or check | Observed result | Evidence |
|---|---|---|
| P01–P20 and M1–M3 | All 20 predictions matched. P13 failed only when both containment layers were compromised. | [Permission results](evidence/PERMISSION-BOUNDARIES.md) |
| Live run 1 | Stripe succeeded. Notion and Linear returned 403. The invalid token returned 404. Exit `incomplete`. | [Summary](evidence/runs/live-1-ashby-403/summary.json) |
| User-Agent review | The focused test failed before the patch and passed after. I accepted the patch after the 124-test run and live run 2. | [Review packet](REVIEW-PACKET.md) |
| Live run 2 | Stripe, Notion, and Linear succeeded. The invalid token returned 404 in one attempt and had null counts. Exit `incomplete`. | [Summary](evidence/runs/live-2-after-ua-patch/summary.json) · [Trace](evidence/runs/live-2-after-ua-patch/trace.jsonl) · [Raw responses](evidence/runs/live-2-after-ua-patch/raw/) |
| Offline replay and wrong-answer demo | Normal replay matched at 16 new IDs. The seeded wrong replay reported 0, and the checker found 16. The checker also matched the three comparable boards from live run 2. | [Demo output](evidence/finished-wrong-answer/demo-output.txt) |

The initial gate and permission predictions were committed before implementation at `7b171a4`. The current [gate](GATE.md) records later decisions. My [sign-off and driver's seat](SIGNOFF.md), [sources](SOURCES.md), and [Frictional log](FRICTIONAL.md) document what I checked and who contributed.

The watch uses public GET endpoints on the allow-list and identifies itself as a student project. It has no persona data or credentials and never applies, emails, messages, or logs in. The protected shortlist exists as a tested permission boundary. Normal runs have no CLI path to approve or write it.
