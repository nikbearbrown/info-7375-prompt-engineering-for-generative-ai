"""One-time setup: start JS2's Greenhouse/databricks memory from JS1's, so the
first JS2 run reports postings new since JS1's last run (2026-10-30).

    python3 -m agent.import_js1_state

Reads ../js1-contract-and-watch (allowed: read only); writes state/ (a NEW file,
so no approval is needed; if it already exists the policy asks).
"""
import json
import pathlib

from agent.policy import Policy, ask_on_terminal

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = "../js1-contract-and-watch/state/databricks-seen_ids.json"
DST = "state/greenhouse-databricks.json"


def main():
    policy = Policy(ROOT)
    js1 = json.loads(policy.read_bytes(SRC))
    state = {"ats": "greenhouse", "board": "databricks",
             "seen_ids": sorted(str(i) for i in js1["seen_ids"]),
             "imported_from": {"file": SRC,
                               "js1_runs": [r["stamp"] for r in js1["runs"]]},
             "runs": []}
    policy.write_bytes(DST, (json.dumps(state, indent=1) + "\n").encode(),
                       approver=ask_on_terminal)
    print(f"{DST}: {len(state['seen_ids'])} ids from JS1 runs "
          f"{state['imported_from']['js1_runs']}")


if __name__ == "__main__":
    main()
