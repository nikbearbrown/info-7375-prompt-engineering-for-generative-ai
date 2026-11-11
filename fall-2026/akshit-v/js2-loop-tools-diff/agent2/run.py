"""One run of the multi-board watch.

Live run:
    python -m agent2.run --resume data/resume_jack_spencer.json
Replay of saved responses (the run is labeled with --label, e.g. SEEDED):
    python -m agent2.run --resume data/resume_jack_spencer.json --replay out/<dir>/manifest.json --label SEEDED --out out/<dir>
Reset the seen-id state (needs approval):
    python -m agent2.run --resume data/resume_jack_spencer.json --reset-state --approve reset-state
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent2 import loop, policy, rule
from agent2.config import BOARDS, BUDGET
from agent2.fetch import LiveTransport, ReplayTransport
from agent2.resume import ResumeRejected, load_resume


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"boards": {}}
    state = json.loads(path.read_text(encoding="utf-8"))  # ValueError -> exit error
    if not isinstance(state.get("boards"), dict):
        raise ValueError("state file has no 'boards' object")
    return state


def new_postings(state: dict, board_key: str, postings: list[dict]):
    """None means baseline (board never seen): nothing is reported as new."""
    prev = state["boards"].get(board_key)
    if prev is None:
        return None
    seen = set(prev["seen_ids"])
    return [p for p in postings if p["id"] not in seen]


def next_state(state: dict, result: loop.LoopResult, run_id: str) -> dict:
    boards = {k: dict(v) for k, v in state["boards"].items()}
    for key, postings in result.postings.items():   # only boards whose outcome was ok
        prev = boards.get(key, {"seen_ids": []})
        boards[key] = {"seen_ids": sorted(set(prev["seen_ids"]) | {p["id"] for p in postings}),
                       "last_count": len(postings), "last_ok_run": run_id}
    return {"boards": boards}


def render(record: dict) -> str:
    lines = [f"# Run {record['run_id']}  [{record['transport']}]",
             f"exit: {record['exit']}  ({record['cause']})",
             f"requests used: {record['requests_used']} / {record['budget']['max_requests']}", "", "## Trace"]
    for e in record["trace"]:
        extra = {k: v for k, v in e.items() if k not in ("seq", "t", "event")}
        lines.append(f"{e['seq']:>3}  t={e['t']:>7}s  {e['event']:<16} {json.dumps(extra, ensure_ascii=False)}")
    lines += ["", "## Boards"]
    for key, b in record["boards"].items():
        lines.append(f"- {key}: {b['outcome']} ({b['detail']})")
    if record["not_attempted"]:
        lines.append(f"- not attempted: {', '.join(record['not_attempted'])}")
    lines += ["", "## New postings (rule verdict = record, recomputable from CONTRACT rule of JS1)"]
    for key, items in record["new"].items():
        if items is None:
            lines.append(f"- {key}: BASELINE (first time this board was seen; none reported as new)")
            continue
        lines.append(f"- {key}: {len(items)} new")
        for p in items:
            lines.append(f"    {p['verdict']:<13} {p['title']}  ({p['because']})  {p['url']}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resume", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=policy.OUT, help="output folder; must be inside out/")
    ap.add_argument("--replay", type=Path, help="serve saved responses from this manifest instead of the network")
    ap.add_argument("--label", default="REPLAY", help="label for a replay run, e.g. SEEDED")
    ap.add_argument("--reset-state", action="store_true")
    ap.add_argument("--approve", action="append", default=[], help="explicit approvals, e.g. reset-state")
    args = ap.parse_args(argv)

    started = datetime.now(timezone.utc)
    run_id = f"{started:%Y%m%dT%H%M%SZ}"
    out = policy.check_write(args.out)          # the output folder itself must be inside out/
    state_path = out / "state" / "seen_ids.json"

    def fail(cause: str) -> int:
        print(f"exit: error ({cause})", file=sys.stderr)
        return 2

    try:
        resume = load_resume(policy.check_read(args.resume))
    except ResumeRejected as e:
        return fail(f"résumé failed validation: {'; '.join(e.args[0])}")
    except policy.PolicyViolation as e:
        return fail(str(e))
    if args.reset_state:
        try:
            policy.reset_state(state_path, approvals=frozenset(args.approve))
        except policy.PolicyViolation as e:
            return fail(str(e))
        print(f"state reset (approved): {state_path}")
        return 0
    try:
        state = load_state(state_path)
    except ValueError as e:
        return fail(f"state file is corrupt: {e}")

    transport = ReplayTransport(args.replay, args.label) if args.replay else LiveTransport()

    def save_raw(board_key, attempt, body):
        name = board_key.replace(":", "_") + f"_try{attempt}.json"
        p = policy.write_bytes(out / "evidence" / run_id / name, body)
        return p.relative_to(policy.ROOT).as_posix()

    last_counts = {k: v.get("last_count") for k, v in state["boards"].items()}
    result = loop.run_loop(BOARDS, transport, last_counts, BUDGET, save_raw)

    new = {}
    for key, postings in result.postings.items():
        items = new_postings(state, key, postings)
        if items is not None:
            items = [{**p, **{k: rule.judge(p, resume)[k] for k in ("verdict", "because")}} for p in items]
            items = [{k: v for k, v in p.items() if k != "content_text"} for p in items]
        new[key] = items

    record = {"run_id": run_id, "started_utc": started.isoformat(timespec="seconds"), "transport": transport.label,
              "exit": result.exit, "cause": result.cause, "budget": vars(BUDGET), "requests_used": result.requests_used,
              "boards": result.boards, "not_attempted": result.not_attempted, "new": new,
              "state_before": state, "trace": result.trace}
    policy.write_bytes(out / "runs" / f"{run_id}.json", (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode())
    text = render(record)
    policy.write_bytes(out / "runs" / f"{run_id}.txt", text.encode("utf-8"))
    print(text)

    if result.exit != "error":   # GATE: on error the state file is not changed
        policy.write_bytes(state_path, (json.dumps(next_state(state, result, run_id), indent=2) + "\n").encode())
    return {"finished": 0, "incomplete": 1, "budget_exhausted": 3, "error": 2}[result.exit]


if __name__ == "__main__":
    sys.exit(main())
