# A finished wrong answer, and the check that caught it

Every run here was live, against the real Greenhouse API, on 2026-11-09. None were simulated.

## The wrong answer
- **The config:** `config/wrong_board.json` names Greenhouse board `abacus` as if it were Abacus Insights. Abacus Insights' real board is `abacusinsights`. The slug `abacus` belongs to a different employer.
- **The command:**
  ```bash
  python3 agent.py run --config config/wrong_board.json --state state/wrong_board.json --label WRONG-BOARD-demo
  ```
- **The run:** `runs/2026-11-09T205807Z_WRONG-BOARD-demo`.
  - **Exit `finished`** (code 0) after 1 request in 0.23 s.
  - **46 postings were reported** as a clean baseline, and their ids were written to `state/wrong_board.json`.
  - **Nothing in the loop's own report says anything is wrong.** By the gate's definition this is a success: every configured board was fetched, parsed, and saved, within budget.
- **Why it is wrong:**
  - The postings belong to another employer. The first one in `raw/greenhouse_abacus.json` links to `abacustechnology.com`.
  - On the same day, the real Abacus Insights board had 15 postings (`runs/2026-11-09T205756Z`).
  - A watch built on this run would report another company's jobs as Abacus Insights' new jobs from then on.

## The independent check
- **The command:**
  ```bash
  python3 check_identity.py --config config/wrong_board.json
  ```
- **The result:** `runs/2026-11-09T205808Z_identity-check`, which reported **MISMATCH**, exit 1:

  | Board | Employer in config | Board's own name | Result |
  |---|---|---|---|
  | greenhouse/abacus | Abacus Insights | ABACUS | MISMATCH |

- **Why it's independent:**
  - It never reads the loop's report, run folder, or state. It reads only the config.
  - It asks Greenhouse a different question, the board's own name (`/v1/boards/{token}`), and saves that answer in `raw/greenhouse_abacus_board.json`.
  - It compares names with its own function (`same_name`), sharing no code with the loop.
  - It goes through the same permission policy and writes only its own new folder in `runs/`.
- **Control:** on the real config, the check (`runs/2026-11-09T205810Z_identity-check`) found that Abacus Insights matched, exit 0. It reported Ashby and Lever boards as "not checkable", not as passing, because those systems have no public endpoint for a board's name.

## What happened next
- **The loop was fixed in review.** This defect became the review packet's change (`REVIEW_PACKET.md`). The review test `tests/test_review_identity.py` (drafted with Claude's help, accepted by me) was committed first (`a81c572`), then the patch (`b3f5adb`).
- **The same wrong board after the patch:** `runs/2026-11-10T170122Z_WRONG-BOARD-after-patch` exited `incomplete` after one request, with the reason `identity mismatch: the board calls itself 'ABACUS', but the config says 'Abacus Insights'`. It saved no ids (`state/wrong_board_after.json` has `"boards": {}`).
- **The check still covers Greenhouse only.** A valid Ashby or Lever board for the wrong employer would still finish cleanly, and neither the loop nor `check_identity.py` would catch it. This limit is recorded in `GATE.md`.

## Reproduce the original finished wrong answer
The current loop refuses this board, so use the code from before the patch. Run these from the repository root (they write only inside `/tmp/js2-before`):

```bash
mkdir -p /tmp/js2-before && git archive a81c572 fall-2026/atharva-h/js2-loop-tools-diff | tar -x -C /tmp/js2-before
```

```bash
cd /tmp/js2-before/fall-2026/atharva-h/js2-loop-tools-diff && python3 agent.py run --config config/wrong_board.json --state state/wrong_board_rerun.json --label WRONG-BOARD-rerun
```

```bash
cd /tmp/js2-before/fall-2026/atharva-h/js2-loop-tools-diff && python3 check_identity.py --config config/wrong_board.json
```

The board's contents change over time, so the posting count may differ from 46. The loop's `finished` and the check's MISMATCH should not.
