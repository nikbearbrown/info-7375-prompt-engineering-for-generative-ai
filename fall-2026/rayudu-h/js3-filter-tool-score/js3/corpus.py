"""Everything the agent collected: the live snapshots under runs/*-live/, read through the JS2
policy (reads inside this folder only). Each posting is kept in its latest version, with the
snapshots it appeared in. Boards with no result in a snapshot are listed, never dropped."""
from __future__ import annotations

import gzip
import json

from jsagent.policy import Policy
from jsagent.providers import SYSTEMS

from . import ROOT


def snapshot_dirs(root=ROOT) -> list:
    return sorted(p for p in (root / "runs").glob("*-live") if (p / "run.json").exists())


def load(root=ROOT, policy: Policy = None) -> dict:
    policy = policy or Policy(root)
    snapshots, postings = [], {}
    for d in snapshot_dirs(root):
        run = json.loads(policy.check_read(d / "run.json").read_text())
        snap = {"id": d.name, "status": run.get("status"), "boards_ok": [], "boards_without_result": [], "keys": []}
        for b in run["boards"]:
            if b["status"] != "ok":
                snap["boards_without_result"].append({"board": b["board"], "status": b["status"],
                                                      "reason": b.get("reason", "")})
                continue
            system, board = b["board"].split(":", 1)
            raw = gzip.decompress(policy.check_read(root / b["raw"]["file"]).read_bytes())
            for p in SYSTEMS[system].parse(board, raw):
                prev = postings.get(p["key"])
                p["first_seen"] = prev["first_seen"] if prev else d.name
                p["last_seen"] = d.name
                p["snapshots"] = (prev["snapshots"] if prev else []) + [d.name]
                postings[p["key"]] = p                       # the latest version wins
                snap["keys"].append(p["key"])
            snap["boards_ok"].append(b["board"])
        snapshots.append(snap)
    return {"snapshots": snapshots, "postings": postings, "latest": snapshots[-1]["id"] if snapshots else None}


def latest_keys(c: dict) -> set:
    return set(c["snapshots"][-1]["keys"]) if c["snapshots"] else set()


def new_keys(c: dict, since: str, upto: str = None) -> set:
    """Keys in snapshot `upto` (default: latest) that were not in any snapshot up to and including `since`."""
    ids = [s["id"] for s in c["snapshots"]]
    upto = upto or ids[-1]
    if since not in ids or upto not in ids or ids.index(since) >= ids.index(upto):
        raise ValueError(f"unknown or out-of-order snapshots: since={since!r}, upto={upto!r}")
    seen = set()
    for s in c["snapshots"][: ids.index(since) + 1]:
        seen |= set(s["keys"])
    return set(c["snapshots"][ids.index(upto)]["keys"]) - seen
