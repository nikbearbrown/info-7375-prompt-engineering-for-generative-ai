"""Cross-check two runs' new and closed postings from the saved raw responses alone.

    python3 crosscheck_days.py runs/DAY1 runs/DAY2

It uses its own id extraction, not adapters.py or loop.py. It recomputes, per board,
which ids are new and which closed between the two raw responses, then compares that
with what the day-2 run reported in its run.json. It reads only, and writes nothing.
Exit code 0 if they agree, 1 if not.
"""
import json
import os
import sys


def ids_in(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    jobs = data if isinstance(data, list) else data["jobs"]
    return {str(job["id"]) for job in jobs}


def main(day1, day2):
    with open(os.path.join(day2, "run.json"), encoding="utf-8") as f:
        reported = json.load(f)["results"]
    agree = True
    for name in sorted(os.listdir(os.path.join(day2, "raw"))):
        if not name.endswith(".json") or name.endswith("_board.json"):
            continue
        system, token = name[:-5].split("_", 1)
        key = f"{system}/{token}"
        first, second = os.path.join(day1, "raw", name), os.path.join(day2, "raw", name)
        if not os.path.exists(first) or reported.get(key, {}).get("status") != "ok":
            continue
        a, b = ids_in(first), ids_in(second)
        mine = (sorted(b - a), sorted(a - b))
        theirs = (sorted(p["id"] for p in reported[key]["new"]), sorted(reported[key]["closed"]))
        ok = mine == theirs
        agree &= ok
        print(f"{key}: day1 {len(a)}, day2 {len(b)}; recomputed new {mine[0]} closed {mine[1]}; "
              f"run.json new {theirs[0]} closed {theirs[1]} -> {'agree' if ok else 'DISAGREE'}")
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
