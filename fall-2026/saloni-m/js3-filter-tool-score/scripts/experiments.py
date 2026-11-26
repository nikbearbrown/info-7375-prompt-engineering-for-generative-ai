"""What moves the score (Chapter 9): one change to one object at a time, on the 30 held-out postings.

    python3 scripts/experiments.py run [--variants J0,J1,J2,J3] [--workers 4]   # real Claude calls
    python3 scripts/experiments.py measure                                      # needs labels/heldout_sheet.csv labelled

Claude variants (each differs from J0 in exactly one object):
  J0  baseline: prompts/judge_v1.md, full posting context, no tools
  J1  PROMPT:   prompts/judge_v2_criteria.md (adds the three labeling criteria), else as J0
  J2  CONTEXT:  posting title only, else as J0
  J3  TOOLS:    my MCP server's tools are available (score_posting, search_postings), else as J0
Filter variants (no model; the scorer itself):
  F0  FILTER.md v1.0 as written
  F1  SETTING:  threshold 3 -> 4, else v1.0
  F2+ FILTER FILE: any JSON filter in config/filter_variants/*.json (written after the dev audit)

Each Claude reply is saved raw, with its UTC start time, in out/experiments/<variant>.jsonl.
"""
import argparse
import concurrent.futures as cf
import copy
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from js3 import claude  # noqa: E402
from js3.collect import latest_snapshot, load_postings  # noqa: E402
from js3.filter import load_filter, score  # noqa: E402
from js3.stats import clopper_pearson  # noqa: E402

OUT = os.path.join(HERE, "out", "experiments")
CLAUDE_VARIANTS = {
    "J0": {"prompt": "prompts/judge_v1.md", "context": "full", "tools": False, "changed": "baseline"},
    "J1": {"prompt": "prompts/judge_v2_criteria.md", "context": "full", "tools": False, "changed": "prompt"},
    "J2": {"prompt": "prompts/judge_v1.md", "context": "title_only", "tools": False, "changed": "context"},
    "J3": {"prompt": "prompts/judge_v1.md", "context": "full", "tools": True, "changed": "tool list"},
}
VERDICTS = {"worth_time", "not_worth_time", "cannot_tell"}


def heldout_uids():
    with open(os.path.join(HERE, "labels", "heldout_sheet.csv"), newline="", encoding="utf-8") as f:
        return [r["uid"] for r in csv.DictReader(f)]


def judge(variant, p):
    v = CLAUDE_VARIANTS[variant]
    prompt = claude.fill(v["prompt"], p, v["context"])
    if v["tools"]:
        reply = claude.call(prompt, mcp=claude.own_server_mcp(),
                            allowed_tools=["mcp__js3__score_posting", "mcp__js3__search_postings"])
    else:
        reply = claude.call(prompt)
    try:
        obj = claude.parse_json_reply(reply["raw"])
        verdict = obj.get("verdict") if obj.get("verdict") in VERDICTS else None
        reply["verdict"], reply["reason"] = verdict, obj.get("reason")
        reply["parse"] = "ok" if verdict else "rejected: bad verdict"
    except Exception as e:  # noqa: BLE001
        reply["verdict"], reply["parse"] = None, f"rejected: {e}"
    return {"variant": variant, "uid": p["uid"], **v, **reply}


def run(variants, workers):
    os.makedirs(OUT, exist_ok=True)
    posts = {p["uid"]: p for p in load_postings(latest_snapshot())}
    uids = heldout_uids()
    for var in variants:
        path = os.path.join(OUT, f"{var}.jsonl")
        done = set()
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                done = {json.loads(line)["uid"] for line in f if line.strip()}
        todo = [u for u in uids if u not in done]
        print(f"{var}: {len(todo)} calls ({len(done)} already saved)", flush=True)
        with cf.ThreadPoolExecutor(workers) as ex, open(path, "a", encoding="utf-8") as f:
            for rec in ex.map(lambda u: judge(var, posts[u]), todo):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                print(f"  {var} {rec['verdict']!s:<15} {rec['uid']}", flush=True)


def filter_variants():
    base = load_filter()
    f1 = copy.deepcopy(base)
    f1["threshold"] = 4
    f1["filter_version"] = "1.0+threshold4"
    out = {"F0": ("baseline (FILTER.md v1.0)", base), "F1": ("setting: threshold 3 -> 4", f1)}
    for i, path in enumerate(sorted(glob.glob(os.path.join(HERE, "config", "filter_variants", "*.json"))), 2):
        with open(path, encoding="utf-8") as f:
            flt = json.load(f)
        out[f"F{i}"] = (f"filter file: {os.path.basename(path)} ({flt.get('_change', '')})", flt)
    return out


def tally(pred, hand):
    """pred/hand: dict uid -> verdict. Positive class = worth_time."""
    c = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "pred_cannot_tell": 0, "hand_cannot_tell": 0, "no_answer": 0}
    for u, h in hand.items():
        p = pred.get(u)
        if h == "cannot_tell":
            c["hand_cannot_tell"] += 1
            continue
        if p is None:
            c["no_answer"] += 1
        elif p == "cannot_tell":
            c["pred_cannot_tell"] += 1
        elif p == "worth_time":
            c["tp" if h == "worth_time" else "fp"] += 1
        else:
            c["fn" if h == "worth_time" else "tn"] += 1
    judged = c["tp"] + c["fp"] + c["fn"] + c["tn"]
    agree = c["tp"] + c["tn"]
    lo, hi = clopper_pearson(agree, judged)
    c["agreement"] = f"{agree}/{judged}"
    c["agreement_95ci"] = [round(lo, 2), round(hi, 2)]
    return c


def measure():
    with open(os.path.join(HERE, "labels", "heldout_sheet.csv"), newline="", encoding="utf-8") as f:
        hand = {r["uid"]: r["hand_label"] for r in csv.DictReader(f)}
    if not all(hand.values()):
        sys.exit("labels/heldout_sheet.csv is not fully labelled; run scripts/label.py labels/heldout_sheet.csv")
    posts = {p["uid"]: p for p in load_postings(latest_snapshot())}
    rows = []
    for name, (desc, flt) in filter_variants().items():
        pred = {u: ("worth_time" if score(posts[u], flt)["decision"] == "keep" else "not_worth_time") for u in hand}
        rows.append({"variant": name, "changed": desc, **tally(pred, hand)})
    for var, v in CLAUDE_VARIANTS.items():
        path = os.path.join(OUT, f"{var}.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            recs = [json.loads(line) for line in f]
        pred = {r["uid"]: r["verdict"] for r in recs}
        dates = sorted(r["started_utc"] for r in recs)
        rows.append({"variant": var, "changed": v["changed"], "claude_calls": len(recs),
                     "ran_utc": f"{dates[0]} .. {dates[-1]}", **tally(pred, hand)})
    print(json.dumps(rows, indent=2))
    with open(os.path.join(OUT, "measure.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "measure"])
    ap.add_argument("--variants", default="J0,J1,J2,J3")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.variants.split(","), a.workers)
    else:
        measure()


if __name__ == "__main__":
    main()
