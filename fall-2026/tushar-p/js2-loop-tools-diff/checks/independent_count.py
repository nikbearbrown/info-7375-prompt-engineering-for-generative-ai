"""Independent count (GATE F17, "Finished with the wrong answer", Wrong versions row 7).

    .venv/bin/python checks/independent_count.py <run_dir>

A separate, read-only program. It does not import anything from agent/; it re-derives
the new-ID sets from the run's own evidence and compares them with the agent's report:

- summary.json         the agent's report (new, new_ids, raw_paths per board)
- raw/...              each board's last saved raw response
- pre-run-state.json   the seen IDs the agent loaded before the run (or null)

For each board whose raw body is a valid listing, new = unique raw IDs minus that board's
pre-run seen IDs; a board with no pre-run entry is a baseline, so new must be zero.
Exit 0 if every comparable board matches, 1 on any mismatch, 2 if the evidence can't be read.
It never writes anything and never changes the agent's exit or state.
"""

import json
import sys
from pathlib import Path

USAGE = "usage: independent_count.py <run_dir>"


def read_json(path: Path):
    """(value, None) or (None, reason)."""
    try:
        return json.loads(path.read_bytes()), None
    except OSError as err:
        return None, f"cannot read {path}: {err}"
    except (UnicodeDecodeError, ValueError) as err:
        return None, f"{path} is not valid JSON: {err}"


def listing_ids(provider: str, data):
    """Unique IDs in response order if `data` is a valid listing, else None.

    Written independently of the agent: a JSON object with a `jobs` list whose every
    item is an object with an `id`; Greenhouse IDs are non-bool integers, Ashby IDs are
    non-empty strings.
    """
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return None
    unique, seen = [], set()
    for job in data["jobs"]:
        if not isinstance(job, dict) or "id" not in job:
            return None
        value = job["id"]
        if provider == "greenhouse":
            ok = isinstance(value, int) and not isinstance(value, bool)
        elif provider == "ashby":
            ok = isinstance(value, str) and value != ""
        else:
            ok = False
        if not ok:
            return None
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def raw_file(run_dir: Path, run_id: str, recorded: str):
    """Map a raw path recorded in the summary (relative to the output root, e.g.
    runs/<run_id>/raw/...) into this run folder, which may have been copied elsewhere."""
    parts = Path(recorded).parts
    if Path(recorded).is_absolute() or ".." in parts:
        return None
    if len(parts) > 2 and parts[0] == "runs" and parts[1] == run_id:
        parts = parts[2:]
    return run_dir.joinpath(*parts)


def show(value) -> str:
    return "null" if value is None else str(value)


def main(argv) -> int:
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    run_dir = Path(argv[1])
    summary, problem = read_json(run_dir / "summary.json")
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 2
    pre_run, problem = read_json(run_dir / "pre-run-state.json")
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 2
    if pre_run is not None and not isinstance(pre_run, dict):
        print("error: pre-run-state.json must be null or a JSON object", file=sys.stderr)
        return 2

    run_id = summary.get("run_id", "")
    print(f"run {run_id}  mode: {summary.get('mode')}  agent exit: {summary.get('exit')}")
    rows, details = [], []
    for board in summary.get("boards", []):
        key, provider = board.get("board"), board.get("provider")
        agent_new, agent_ids = board.get("new"), board.get("new_ids")
        raw_paths = board.get("raw_paths") or []
        independent, match = "n/a (no raw response)", "n/a"
        indep_fetched = None
        if raw_paths:
            path = raw_file(run_dir, run_id, raw_paths[-1])
            data, problem = (None, "unsafe raw path") if path is None else read_json(path)
            ids = None if problem else listing_ids(provider, data)
            if ids is None:
                independent = "n/a (raw is not a valid listing)"
            else:
                indep_fetched = len(ids)
                prior = (pre_run or {}).get(key)
                if prior is None:
                    expected = []
                    independent = "0 (baseline, no prior state)"
                else:
                    seen = set(prior)
                    expected = [i for i in ids if i not in seen]
                    independent = str(len(expected))
                agent_set = set(agent_ids) if isinstance(agent_ids, list) else None
                if agent_new == len(expected) and agent_set == set(expected):
                    match = "yes"
                else:
                    match = "MISMATCH"
                    missing = sorted(set(expected) - (agent_set or set()), key=str)
                    extra = sorted((agent_set or set()) - set(expected), key=str)
                    details.append(f"{key}: agent reported new={show(agent_new)}, the saved response "
                                   f"gives {len(expected)}; missing from the agent's report: "
                                   f"{missing[:20]}{' ...' if len(missing) > 20 else ''}; "
                                   f"extra in the agent's report: {extra[:20]}")
        if match == "n/a" and agent_new is not None:
            match = "MISMATCH"
            details.append(f"{key}: agent reported new={agent_new}, but there is no valid saved listing to support it")
        rows.append((key, show(agent_new), independent, match, show(board.get("fetched")), show(indep_fetched)))

    headers = ("board", "agent_new", "independent_new", "match", "agent_fetched", "independent_fetched")
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)))

    mismatches = [r for r in rows if r[3] == "MISMATCH"]
    for line in details:
        print(f"MISMATCH {line}")
    if mismatches:
        print(f"RESULT: MISMATCH on {len(mismatches)} of {len(rows)} board(s)")
        return 1
    print(f"RESULT: all comparable boards match ({sum(r[3] == 'yes' for r in rows)} compared, "
          f"{sum(r[3] == 'n/a' for r in rows)} not comparable)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
