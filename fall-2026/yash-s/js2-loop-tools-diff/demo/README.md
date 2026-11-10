# Finished-wrong-answer demonstration (SEEDED, with one CONSTRUCTED response)

**This is not a live run.** The agent reads saved responses from `replay/` and fetches nothing. The run is a realistic "finished" result that is wrong, and the check that catches it is a separate script, not the agent's own report (GATE.md section 4, Empty Response).

| `replay/` file | What it is |
|---|---|
| `greenhouse-databricks.json` | An exact copy of the live run's Databricks response (`runs/run-2026-11-10T025118Z/`, sha256 `4c287ecf6ec1…`) |
| `ashby-openai.json` | An exact copy of the live run's OpenAI response (same run, sha256 `faf9491cab01…`) |
| `greenhouse-anthropic.json` | **CONSTRUCTED**: a well-formed but empty job list (`{"jobs": []}`), with a `_comment` saying so. Anthropic's real board had 675 postings in the live run. |

`state/` holds copies of the three state files as they were right after the live run. The demonstration writes only to `demo/state/` and `demo/runs/`, never to the real `state/` or `runs/`.

## Commands (from the js2-loop-tools-diff folder)

```bash
python3 agent.py --config config/demo-finished-wrong.json --replay demo/replay --state-dir demo/state --runs-dir demo/runs
python3 independent_check.py demo/runs/run-<the new folder> --earlier runs
```

**What should happen:**
- **The agent** ends **finished** (exit 0): three boards ok, 0 new postings, no problems.
- **The independent check** recounts each board from the demo run's saved raw responses and compares them with the live run. It flags Anthropic, **DROP-TO-ZERO: 675 postings before, none now**, and exits 1.
