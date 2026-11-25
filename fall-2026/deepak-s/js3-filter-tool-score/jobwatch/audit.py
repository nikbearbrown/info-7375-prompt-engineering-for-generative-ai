"""Phase 3b: the reject-audit samples (FILTER.md section 2 close calls; brief Step 2 audit).

    python -m jobwatch audit-sheet --dataset data/postings-<run-id>.jsonl --filter data/filter-v1.jsonl
                                   --seed N --heldout-seed-a A --heldout-seed-b B

Groups, drawn in this order, each excluding postings already drawn and every held-out posting:
  close_call_reject  the 10 scored rejects whose scores are nearest T
  close_call_keep    the 5 kept postings whose scores are nearest T
  random_reject      30 random rejects
  random_keep        10 random kept postings (all, if fewer)
Gate-rejected and abstained postings have null scores and are not close-call eligible. Ties at
the close-call cutoff, and every random draw, are broken by sorting the candidates in the
section 2 tie order and drawing with random.Random(seed).sample (a fresh Random(seed) per draw).
If a group has fewer candidates than its size, all are taken and the shortfall is recorded.

The held-out keys are recomputed from the dataset with the held-out seeds (jobwatch/heldout.py's
draw is deterministic), so labels/heldout.csv is never opened here.

The sheet audit/audit-<version>.csv has posting_key, group, title, location, url, text_path and
empty verdict and override_reason columns. It has no score and no matched rule.
"""
import random

from jobwatch import heldout, sheets
from jobwatch.filter import T_DEFAULT, tie_key

SIZES = {"close_call_reject": 10, "close_call_keep": 5, "random_reject": 30, "random_keep": 10}
COLUMNS = ("posting_key", "group", "title", "location", "url", "text_path", "verdict", "override_reason")


def _sample(cands, k, seed):
    cands = sorted(cands, key=tie_key)
    if len(cands) <= k:
        return cands
    return random.Random(seed).sample(cands, k)


def nearest(cands, k, seed, threshold):
    """The k candidates nearest T; ties at the cutoff distance drawn at random with the seed."""
    by_dist = {}
    for o in cands:
        by_dist.setdefault(abs(o["score"] - threshold), []).append(o)
    out = []
    for d in sorted(by_dist):
        group = by_dist[d]
        if len(out) + len(group) <= k:
            out += sorted(group, key=tie_key)
        else:
            out += _sample(group, k - len(out), seed)
        if len(out) >= k:
            break
    return out


def draw(outputs, heldout_keys, seed, threshold=T_DEFAULT):
    posts = [o for o in outputs if o.get("scope") != "board" and o["key"] not in heldout_keys]
    taken = set()
    groups, pools = {}, {}

    def avail(pred):
        return [o for o in posts if o["key"] not in taken and pred(o)]

    order = [
        ("close_call_reject", lambda o: o["decision"] == "reject" and o["score"] is not None, True),
        ("close_call_keep", lambda o: o["decision"] == "keep", True),
        ("random_reject", lambda o: o["decision"] == "reject", False),
        ("random_keep", lambda o: o["decision"] == "keep", False),
    ]
    for name, pred, is_close in order:
        cands = avail(pred)
        pools[name] = len(cands)
        picked = nearest(cands, SIZES[name], seed, threshold) if is_close else _sample(cands, SIZES[name], seed)
        groups[name] = picked
        taken |= {o["key"] for o in picked}
    return groups, pools


def heldout_keys(lines, seed_a, seed_b):
    _, chosen = heldout.draw(list(lines), {"A": seed_a, "B": seed_b})
    return {x["key"] for s in chosen.values() for x in s}


def write_sheet(tools, lines, outputs, run_id, version, seed, hk, path=None):
    path = path or f"audit/audit-{version}.csv"
    if sheets.exists(tools, path):
        raise FileExistsError(f"{path} exists; an audit sheet is drawn once")
    groups, pools = draw(outputs, hk, seed)
    by_key = {ln["key"]: ln for ln in lines}
    picked = [by_key[o["key"]] for g in SIZES for o in groups[g]]
    paths = sheets.write_texts(tools, picked, run_id)
    rows = []
    for g in SIZES:
        for o in groups[g]:
            ln = by_key[o["key"]]
            rows.append({"posting_key": ln["key"], "group": g, "title": ln["title"],
                         "location": ln["location"] if ln["location"] is not None else "", "url": ln["url"] or "",
                         "text_path": paths[ln["key"]], "verdict": "", "override_reason": ""})
    comments = [f"Reject audit of filter {version} on run {run_id}. Audit seed {seed}; held-out postings excluded "
                f"({len(hk)} keys, recomputed from the held-out seeds; labels/heldout.csv not opened)."]
    for g in SIZES:
        short = max(0, SIZES[g] - len(groups[g]))
        comments.append(f"{g}: {len(groups[g])} drawn of {SIZES[g]} asked; pool {pools[g]}"
                        + (f"; shortfall {short}" if short else ""))
    comments.append("verdict: relevant or not_relevant (FILTER.md section 0). override_reason: only for an OVERRIDE.")
    sheets.write_sheet(tools, path, comments, COLUMNS, rows)
    return groups, pools, path


# --- near-decision group (FILTER.md section 2, added after measuring v1) ---------------------------
NEAR = "near_decision"


def near_decision(outputs, heldout_keys, already):
    """Every rejected posting with a role word (R01-R10) in its title, minus the held-out set and
    anything already drawn; all of them, in the section 2 tie order. No sampling."""
    picked = [o for o in outputs if o.get("scope") != "board" and o["decision"] == "reject"
              and any(m["rule"].startswith("R") and m["field"] == "title" for m in o["matched"])
              and o["key"] not in heldout_keys and o["key"] not in already]
    return sorted(picked, key=tie_key)


def append_near_decision(tools, lines, outputs, run_id, hk, path):
    """Append the near-decision rows after the existing groups. Existing rows, columns and seeds
    are unchanged; one comment line is added. Refuses if the group is already in the sheet."""
    comments, columns, rows = sheets.read_sheet(tools, path)
    if tuple(columns) != COLUMNS:
        raise ValueError(f"{path}: unexpected columns {columns}")
    if any(r["group"] == NEAR for r in rows):
        raise FileExistsError(f"{path} already has the {NEAR} group")
    picked = near_decision(outputs, hk, {r["posting_key"] for r in rows})
    by_key = {ln["key"]: ln for ln in lines}
    paths = sheets.write_texts(tools, [by_key[o["key"]] for o in picked], run_id)
    new = [{"posting_key": o["key"], "group": NEAR, "title": by_key[o["key"]]["title"],
            "location": by_key[o["key"]]["location"] if by_key[o["key"]]["location"] is not None else "",
            "url": by_key[o["key"]]["url"] or "", "text_path": paths[o["key"]], "verdict": "", "override_reason": ""}
           for o in picked]
    insert_at = len(comments) - 1 if comments and comments[-1].startswith("verdict:") else len(comments)
    comments = comments[:insert_at] + [
        f"{NEAR}: {len(new)} drawn, all of the pool (no sampling); added after measuring v1 (FILTER.md section 2), "
        f"appended after the groups above; their rows and the audit seed are unchanged."] + comments[insert_at:]
    sheets.write_sheet(tools, path, comments, COLUMNS, rows + new)
    return new
