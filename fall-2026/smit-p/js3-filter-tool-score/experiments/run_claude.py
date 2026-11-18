"""What moves the score: Claude as a judge, one change to one object at a time, on held-out labels.

    python3 experiments/run_claude.py --config baseline            # 33 calls
    python3 experiments/run_claude.py --score                      # writes experiments/results/SCORES.md

Configs (each differs from "baseline" in exactly one object):
  baseline         prompt judge-baseline.md, context = full posting, model sonnet
  baseline-repeat  identical to baseline, a second session (for the persistence point)
  prompt           prompt judge-cannot-tell.md (one added sentence)
  context          context = the score_posting tool's output instead of the posting text
  setting          model haiku instead of sonnet

Each call is a fresh, isolated `claude -p` session: empty temp directory, no tools, no settings,
no MCP servers, no session saved. A reply that is not exactly one JSON object with the right
posting id, a valid verdict, and evidence quoted verbatim from the context given is REJECTED,
never repaired. Every reply is saved with its timestamp in experiments/results/<config>.jsonl.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import filter as flt  # noqa: E402
from postings import load_run  # noqa: E402
from run_filter import load_skills  # noqa: E402

RUN_ID = "live-20261114"
CONFIGS = {
    "baseline": {"prompt": "judge-baseline.md", "context": "posting", "model": "sonnet"},
    "baseline-repeat": {"prompt": "judge-baseline.md", "context": "posting", "model": "sonnet"},
    "prompt": {"prompt": "judge-cannot-tell.md", "context": "posting", "model": "sonnet"},
    "context": {"prompt": "judge-baseline.md", "context": "tool_output", "model": "sonnet"},
    "setting": {"prompt": "judge-baseline.md", "context": "posting", "model": "haiku"},
}
VERDICTS = {"keep", "reject", "cannot_tell"}


def context_for(p, kind, skills):
    if kind == "posting":
        return (f"posting_id: {p['id']}\ntitle: {p['title']}\nlocation: {p['location']}\n"
                f"country: {p['country'] or ''}\n\n{p['text']}")
    v = flt.judge(p, skills)  # exactly what the score_posting tool returns, minus transport
    return json.dumps({"posting_id": p["id"], "title": p["title"], "location": p["location"],
                       "verdict": v["verdict"], "rule": v["rule"], "reason": v["reason"],
                       "evidence": v["evidence"]}, ensure_ascii=False, indent=1)


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def validate(text, pid, context):
    try:
        obj = json.loads(text.strip())
    except ValueError:
        return None, "not a single JSON object"
    if not isinstance(obj, dict) or set(obj) != {"posting_id", "verdict", "reason", "evidence"}:
        return None, "wrong keys"
    if str(obj["posting_id"]) != pid:
        return None, "posting_id does not match"
    if obj["verdict"] not in VERDICTS:
        return None, "verdict not in enum"
    ev = obj["evidence"]
    if not isinstance(ev, list) or not ev or not all(isinstance(e, str) and e.strip() for e in ev):
        return None, "evidence missing"
    for e in ev:
        if norm(e) not in norm(context):
            return None, f"evidence not found in the context: {e[:80]!r}"
    return obj, None


def call(p, cfg, skills):
    context = context_for(p, cfg["context"], skills)
    with open(os.path.join(ROOT, "prompts", cfg["prompt"]), encoding="utf-8") as f:
        system = f.read()
    asked = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["claude", "-p", context, "--model", cfg["model"], "--tools", "",
                            "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
                            "--system-prompt", system, "--output-format", "json"],
                           cwd=tmp, capture_output=True, text=True, timeout=300)
    rec = {"board": p["board"], "posting_id": p["id"], "title": p["title"], "asked_at": asked,
           "config": cfg, "exit": r.returncode}
    try:
        cli = json.loads(r.stdout)
    except ValueError:
        return {**rec, "status": "CALL_FAILED", "stderr": r.stderr[-500:]}
    reply = cli.get("result", "")
    rec.update(reply=reply, models_used=sorted(cli.get("modelUsage", {})), cost_usd=cli.get("total_cost_usd"))
    obj, why = validate(reply, p["id"], context)
    return {**rec, "status": "ACCEPTED", "verdict": obj["verdict"]} if obj else {**rec, "status": "REJECTED", "why": why}


def held_out_postings():
    with open(os.path.join(ROOT, "audit", "sample.json"), encoding="utf-8") as f:
        keys = [(i["board"], i["id"]) for i in json.load(f)["items"] if i["split"] == "held_out"]
    postings, _, _ = load_run(RUN_ID)
    by_key = {(p["board"], p["id"]): p for p in postings}
    return [by_key[k] for k in keys]


def run(name):
    out = os.path.join(HERE, "results", f"{name}.jsonl")
    if os.path.exists(out):
        sys.exit(f"{out} exists; results are not overwritten")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    skills, cfg = load_skills(), CONFIGS[name]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(lambda p: call(p, cfg, skills), held_out_postings()))
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(name, {s: sum(r["status"] == s for r in results) for s in ("ACCEPTED", "REJECTED", "CALL_FAILED")})


def score():
    with open(os.path.join(ROOT, "audit", "hand-verdicts.json"), encoding="utf-8") as f:
        hand = {(v["board"], v["id"]): v["hand_verdict"] for v in json.load(f)["verdicts"]}
    rows, per = [], {}
    for name in CONFIGS:
        path = os.path.join(HERE, "results", f"{name}.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            res = [json.loads(line) for line in f]
        c = {"n": len(res), "wrong_keep": 0, "wrong_reject": 0, "right": 0, "cannot_tell": 0, "rejected_reply": 0}
        for r in res:
            h = hand[(r["board"], r["posting_id"])]
            if r["status"] != "ACCEPTED":
                c["rejected_reply"] += 1
            elif r["verdict"] == "cannot_tell":
                c["cannot_tell"] += 1
            elif (r["verdict"] == "keep") == (h == "relevant"):
                c["right"] += 1
            else:
                c["wrong_keep" if r["verdict"] == "keep" else "wrong_reject"] += 1
        per[name] = {(r["board"], r["posting_id"]): r.get("verdict", r["status"]) for r in res}
        models = sorted({m for r in res for m in r.get("models_used", [])})
        rows.append(f"| {name} | {c['n']} | {c['right']} | {c['wrong_keep']} | {c['wrong_reject']} | "
                    f"{c['cannot_tell']} | {c['rejected_reply']} | {', '.join(models)} |")
    lines = ["# Claude judge on the 33 held-out postings", "",
             "Generated by `experiments/run_claude.py --score` from `experiments/results/*.jsonl`. "
             "Hand verdicts: `audit/hand-verdicts.json` (Smit). keep = relevant, reject = not relevant.", "",
             "| config | n | right | wrong keep | wrong reject | cannot_tell | reply rejected | models recorded |",
             "|---|---|---|---|---|---|---|---|", *rows]
    if "baseline" in per and "baseline-repeat" in per:
        diff = [k for k in per["baseline"] if per["baseline"][k] != per["baseline-repeat"].get(k)]
        lines += ["", f"baseline vs baseline-repeat (identical config, two sessions): {len(diff)} of "
                  f"{len(per['baseline'])} postings got a different answer: " + "; ".join(f"{b}:{i}" for b, i in diff)]
    with open(os.path.join(HERE, "results", "SCORES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=list(CONFIGS))
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.score:
        score()
    elif a.config:
        run(a.config)
    else:
        ap.error("--config or --score")


if __name__ == "__main__":
    main()
