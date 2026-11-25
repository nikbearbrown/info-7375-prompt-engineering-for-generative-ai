"""The independent check of one loop run (GATE.md, "The finished wrong answer and its independent check").

It reads only what the run saved, each board's raw answers and their meta files, and what the run
claims in report.json. It never imports the agent's code. For each board on the report it takes the
last saved answer and decides, by its own reading, whether the board could have been read: HTTP 200,
JSON, and a non-empty list of postings that each have an id and a title (a "jobs" list on Ashby and
Greenhouse, a top-level list on Lever). Then it compares:

1. the board's status in the report with that reading (a board reported "read" whose saved answer
   could not have been read is the finished wrong answer GATE.md describes);
2. the number of postings in the report with the number in the saved answer;
3. each new posting id with the saved answer (a new id must be in it) and each gone id (it must not be);
4. the exit with the per-board results: "finished" while a board could not have been read is wrong,
   and so is "incomplete" when every board could be read and no budget ran out.

Usage (from the repo root):  python3 tools/check_run.py runs/<run id>
Exit 0: the report agrees with the saved answers; 1: at least one disagreement; 2: not a loop run folder.
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path


def readable(system: str, status, body: bytes):
    """(True, ids) when the answer could have been read, else (False, why). This file's own reading."""
    if status != 200:
        return False, f"the saved answer is HTTP {status}"
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False, "the saved answer is not JSON"
    items = data if system == "lever" else (data.get("jobs") if isinstance(data, dict) else None)
    if not isinstance(items, list):
        return False, "the saved answer has no list of postings"
    if not items:
        return False, "the saved answer's list of postings is empty"
    title_key = "text" if system == "lever" else "title"
    ids = []
    for item in items:
        if not isinstance(item, dict) or item.get("id") in (None, "") or not item.get(title_key):
            return False, "a saved posting has no id or no title"
        ids.append(str(item["id"]))
    return True, ids


def last_answer(folder: Path):
    metas = sorted(folder.glob("attempt-*.meta.json"), key=lambda p: int(p.name.split("-")[1].split(".")[0]))
    if not metas:
        return None
    meta = json.loads(metas[-1].read_text(encoding="utf-8"))
    body = gzip.decompress((folder / meta["body_file"]).read_bytes())
    return meta, body


def check(run_dir: Path) -> tuple:
    """(lines to print, flags). Each flag is one disagreement between the report and the saved answers."""
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    lines, flags = [f"Independent check of {run_dir.name} (reads the saved answers and report.json only)", ""], []
    lines.append("| Board | Reported | From the saved answer | Postings reported / saved |")
    lines.append("|---|---|---|---|")
    could_not_read = []
    for board in report["boards"]:
        key, system, reported = board["key"], board["system"], board["status"]
        if reported == "not visited":
            lines.append(f"| {key} | not visited | (nothing saved, nothing to check) | |")
            continue
        saved = last_answer(run_dir / "boards" / key)
        if saved is None:
            verdict, why, ids = False, "no answer was saved", None
        else:
            meta, body = saved
            ok, detail = readable(system, meta.get("status"), body)
            verdict, why, ids = ok, ("readable" if ok else detail), (detail if ok else None)
        if not verdict:
            could_not_read.append(key)
        expected = "read" if verdict else "unverified"
        counts = f"{board.get('postings')} / {len(ids) if ids is not None else 'none'}"
        lines.append(f"| {key} | {reported} | {expected}: {why} | {counts} |")
        if reported != expected:
            flags.append(f"{key}: the report says {reported!r}, but {why}, so it should be {expected!r}")
        if verdict and board.get("postings") != len(ids):
            flags.append(f"{key}: the report counts {board.get('postings')} postings, the saved answer holds {len(ids)}")
        if verdict:
            present = set(ids)
            for item in board.get("new") or []:
                if str(item["id"]) not in present:
                    flags.append(f"{key}: new posting {item['id']} is not in the saved answer")
            for item in board.get("gone") or []:
                if str(item["id"]) in present:
                    flags.append(f"{key}: gone posting {item['id']} is still in the saved answer")
        elif board.get("gone"):
            flags.append(f"{key}: {len(board['gone'])} postings reported gone from a board whose answer could not be read")
    budget_reasons = [r for r in report.get("reasons", []) if "budget" in r]
    if could_not_read and report["exit"] == "finished":
        flags.append(f"exit: the report says finished, but {', '.join(could_not_read)} could not have been read")
    if not could_not_read and not budget_reasons and report["exit"] == "incomplete":
        flags.append("exit: the report says incomplete, but every board's saved answer is readable and no budget ran out")
    lines += ["", f"Report's exit: {report['exit']} (code {report['exit_code']})"]
    lines += ["", "Disagreements:" if flags else "No disagreement between the report and the saved answers."]
    lines += [f"- {flag}" for flag in flags]
    return lines, flags


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or not (Path(args[0]) / "report.json").exists() or not (Path(args[0]) / "boards").is_dir():
        print("usage: python3 tools/check_run.py runs/<run id>   (a loop run folder with report.json and boards/)")
        return 2
    lines, flags = check(Path(args[0]))
    print("\n".join(lines))
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
