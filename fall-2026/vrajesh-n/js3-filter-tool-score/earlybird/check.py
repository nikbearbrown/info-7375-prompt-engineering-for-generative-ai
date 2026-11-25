"""Independent check of a run. It shares no code with the agent's parser or loop and does not trust its report.

1. Recount: re-open every raw file the trace says was parsed, count the items with these few lines,
   and compare with the count the trace claims.
2. Drop to zero: flag a board that now has 0 postings when an earlier run in the state file saw some.
"""
import json
from pathlib import Path


def count_items(path):
    data = json.loads(Path(path).read_bytes())
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):
        return len(data["jobs"])
    return None


def check(root, trace_path, state_path=None):
    root = Path(root).resolve()
    events = [json.loads(line) for line in Path(trace_path).read_text(encoding="utf-8").splitlines() if line]
    exit_event = next((e for e in events if e["action"] == "exit"), {})
    label = exit_event.get("label")
    state = json.loads(Path(state_path).read_text(encoding="utf-8")) if state_path and Path(state_path).exists() else {}
    problems, rows = [], []
    for e in events:
        if e["action"] != "parse" or e.get("result") != "ok":
            continue
        raw = (root / e["raw_path"]).resolve()
        if not raw.is_relative_to(root):
            problems.append(f"{e['board']}: trace points outside the project ({e['raw_path']})")
            continue
        actual = count_items(raw)
        rows.append({"board": e["board"], "claimed": e["count"], "recounted": actual, "raw_path": e["raw_path"]})
        if actual != e["count"]:
            problems.append(f"{e['board']}: trace claims {e['count']} postings, but {e['raw_path']} holds {actual}")
        earlier = [x for x in state.get("boards", {}).get(e["board"], {}).get("runs", [])
                   if x["label"] != label and x["postings"]]
        if e["count"] == 0 and earlier:
            problems.append(f"{e['board']}: 0 postings now, but run {earlier[-1]['label']} "
                            f"({earlier[-1]['date']}) saw {earlier[-1]['postings']}")
    return {"label": label, "exit_claimed": exit_event.get("status"), "boards": rows, "problems": problems,
            "verdict": "PASS" if not problems else "FAIL"}
