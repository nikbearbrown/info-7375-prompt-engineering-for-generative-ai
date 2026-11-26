"""Measure the filter against Revan's hand verdicts: the reject audit, and one change at a time (Chapter 9).

  .venv/bin/python tools/js3_measure.py audit
  .venv/bin/python tools/js3_measure.py run --condition filter_v1 --set dev
  .venv/bin/python tools/js3_measure.py run --condition filter_v1 --set held_out --final

Hand verdicts come from runs/js3/filter_v1/LABEL_SHEET.csv (`hand_verdict` = relevant | not_relevant).
Splits come from runs/js3/filter_v1/audit_sample.json (FILTER.md section 6).

Conditions. Each changes exactly one object relative to its named baseline:
  filter_v1                 baseline: FILTER.md v1 as committed
  setting_threshold_5       setting:  THRESHOLD 6 -> 5                         (vs filter_v1)
  filter_no_platform        filter:   R5 topic list without "platform"         (vs filter_v1)
  claude_prompt_baseline    prompt:   JS1 prompts/baseline.txt, full posting   (Claude; needs ANTHROPIC_API_KEY)
  claude_prompt_revision1   prompt:   JS1 prompts/revision-1.txt, full posting (vs claude_prompt_baseline)
  claude_context_excerpts   context:  revision-1, but the posting content is only the filter's quoted excerpts
                                      (what score_posting returns)              (vs claude_prompt_revision1)

A held-out run needs --final, a dev run of the same condition first, and happens once per condition: a second
held-out run is refused. Results: runs/js3/experiments/<UTC>_<set>_<condition>/.
"""
import argparse
import csv
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from experiment.common import wilson  # noqa: E402
from jsfilter import filter as F  # noqa: E402

RUN = ROOT / "runs" / "js3" / "filter_v1"
EXP = ROOT / "runs" / "js3" / "experiments"
LABELS = ("relevant", "not_relevant")

CONDITIONS = {
    "filter_v1": ("baseline", None),
    "setting_threshold_5": ("setting", "filter_v1"),
    "filter_no_platform": ("filter file", "filter_v1"),
    "claude_prompt_baseline": ("prompt (Claude baseline)", None),
    "claude_prompt_revision1": ("prompt", "claude_prompt_baseline"),
    "claude_context_excerpts": ("context", "claude_prompt_revision1"),
}


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def load_labels():
    with (RUN / "LABEL_SHEET.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    sample = json.loads((RUN / "audit_sample.json").read_text())
    meta = {e["audit_id"]: e for e in sample["sheet"]}
    out = {}
    for r in rows:
        v = r["hand_verdict"].strip()
        if v and v not in LABELS:
            sys.exit(f"{r['audit_id']}: hand_verdict {v!r} must be one of {LABELS}")
        out[(r["board"], r["id"])] = {**r, "hand_verdict": v or None, **meta[r["audit_id"]]}
    return out


def filter_rows(threshold=None, topics=None):
    resume = json.loads((ROOT / "resumes" / "aarav-patel.json").read_text())
    saved = F.THRESHOLD, F.TOPIC_PHRASES
    try:
        if threshold is not None:
            F.THRESHOLD = threshold
        if topics is not None:
            F.TOPIC_PHRASES = topics
        boards = F.load_snapshot(ROOT)
        return {(r["board"], r["id"]): r for r in F.run_filter(resume, boards)["rows"]}, boards
    finally:
        F.THRESHOLD, F.TOPIC_PHRASES = saved


# ---- audit --------------------------------------------------------------------------------

def audit():
    labels = load_labels()
    rows, _ = filter_rows()
    missing = [k for k, v in labels.items() if not v["hand_verdict"]]
    if missing:
        print(f"WARNING: {len(missing)} sheet rows have no hand_verdict yet; they are excluded below.")
    report = {"generated_at": now().isoformat(timespec="seconds"), "filter_version": F.FILTER_VERSION,
              "unlabeled": [labels[k]["audit_id"] for k in missing], "strata": {}}
    for stratum in ("random_reject", "closest_call", "kept"):
        members = [(k, v) for k, v in labels.items() if stratum in v["strata"] and v["hand_verdict"]]
        wrong = []
        for k, v in members:
            filter_says = "relevant" if rows[k]["fate"] == "kept" else "not_relevant"
            if filter_says != v["hand_verdict"]:
                wrong.append({"audit_id": v["audit_id"], "board": k[0], "id": k[1], "title": rows[k]["title"],
                              "filter": filter_says, "fate": rows[k]["fate"], "failed_rules": rows[k]["failed_rules"],
                              "hand": v["hand_verdict"], "reason": v["reason"]})
        n, k_wrong = len(members), len(wrong)
        lo, hi = wilson(k_wrong, n)
        report["strata"][stratum] = {"n_labeled": n, "filter_wrong": k_wrong,
                                     "wilson_95": [round(lo, 3), round(hi, 3)], "wrong": wrong}
    rr = report["strata"]["random_reject"]
    pop = sum(r["fate"] in F.REJECT_FATES for r in rows.values())
    report["random_reject_population"] = pop
    report["what_the_sample_can_show"] = (
        f"{rr['filter_wrong']} of {rr['n_labeled']} randomly sampled rejects were judged wrongly rejected. "
        f"The 95% Wilson interval for the share of wrongly rejected postings among the {pop} rejects in this "
        f"snapshot is {rr['wilson_95'][0]:.0%}-{rr['wilson_95'][1]:.0%}, under simple random sampling and the "
        "assumption that the hand verdicts are right. It is a sample estimate for this one snapshot, not a "
        "measured rate for all postings or other dates.")
    ff = [(v["audit_id"], v["false_friend_word"]) for v in labels.values() if v["false_friend_word"].strip()]
    report["false_friends_recorded"] = ff
    EXP.mkdir(parents=True, exist_ok=True)
    (EXP / "audit_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({s: {k: v for k, v in d.items() if k != "wrong"} for s, d in report["strata"].items()}, indent=1))
    print(report["what_the_sample_can_show"])
    print(f"wrote {(EXP / 'audit_report.json').relative_to(ROOT)}")


# ---- one change at a time -----------------------------------------------------------------

def verdicts(condition, keys):
    if condition.startswith("claude_"):
        from jsagent.claude_judge import credentials_present, make_claude_judge, MISSING_CREDENTIALS
        if not credentials_present():
            sys.exit(MISSING_CREDENTIALS)
        prompt = "baseline.txt" if condition == "claude_prompt_baseline" else "revision-1.txt"
        judge = make_claude_judge(prompt_path=ROOT / "prompts" / prompt)
        resume = json.loads((ROOT / "resumes" / "aarav-patel.json").read_text())
        rows, boards = filter_rows()
        desc = {(p["board"], p["id"]): p for b in boards for p in b["postings"]}
        out = {}
        for k in keys:
            p = desc[k]
            content = (" … ".join(q for q in rows[k]["evidence"].values() if q)
                       if condition == "claude_context_excerpts" else p["description"])
            posting = {"title": p["title"], "location": {"name": p["location"]}, "content": content}
            res = judge(resume, posting)
            out[k] = {"verdict": res["claude_verdict"], "raw": res, "context_chars": len(content)}
            print(f"  {k[0]} {k[1]}: {res['claude_verdict']}", flush=True)
        return out, {"prompt": f"prompts/{prompt}", "context": "filter excerpts only"
                     if condition == "claude_context_excerpts" else "full saved posting"}
    kw = {"setting_threshold_5": {"threshold": 5},
          "filter_no_platform": {"topics": tuple(t for t in F.TOPIC_PHRASES if t != "platform")}}.get(condition, {})
    rows, _ = filter_rows(**kw)
    return ({k: {"verdict": "relevant" if rows[k]["fate"] == "kept" else "not_relevant",
                 "fate": rows[k]["fate"], "total": rows[k]["total"]} for k in keys}, {"filter_change": kw})


def run(condition, split, final):
    if condition not in CONDITIONS:
        sys.exit(f"unknown condition; choose from {sorted(CONDITIONS)}")
    if split == "held_out":
        if not final:
            sys.exit("held-out runs need --final")
        if not list(EXP.glob(f"*_dev_{condition}")):
            sys.exit(f"no dev run of {condition} yet; run --set dev first")
        if list(EXP.glob(f"*_held_out_{condition}")):
            sys.exit(f"{condition} already has a held-out run; the held-out set is used once per condition")
    labels = load_labels()
    keys = sorted(k for k, v in labels.items() if v["split"] == split)
    unlabeled = [labels[k]["audit_id"] for k in keys if not labels[k]["hand_verdict"]]
    if unlabeled:
        sys.exit(f"{split} rows without a hand verdict: {unlabeled}")
    started = now()
    results, config = verdicts(condition, keys)
    conf = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "invalid_or_unavailable": 0}
    per = []
    for k in keys:
        hand, got = labels[k]["hand_verdict"], results[k]["verdict"]
        if got not in LABELS:
            conf["invalid_or_unavailable"] += 1
        else:
            conf[("t" if got == hand else "f") + ("p" if got == "relevant" else "n")] += 1
        per.append({"audit_id": labels[k]["audit_id"], "board": k[0], "id": k[1], "hand": hand, "got": got,
                    "agree": got == hand, **{x: y for x, y in results[k].items() if x != "verdict"}})
    agree = sum(p["agree"] for p in per)
    lo, hi = wilson(agree, len(per))
    obj, base = CONDITIONS[condition]
    summary = {"condition": condition, "object_changed": obj, "compared_with": base, "set": split,
               "n": len(per), "agree": agree, "agreement": round(agree / len(per), 3) if per else None,
               "wilson_95": [round(lo, 3), round(hi, 3)], "confusion_relevant_positive": conf,
               "config": config, "started_at": started.isoformat(timespec="seconds"),
               "finished_at": now().isoformat(timespec="seconds"), "filter_version": F.FILTER_VERSION}
    out = EXP / f"{started.strftime('%Y-%m-%dT%H-%M-%SZ')}_{split}_{condition}"
    out.mkdir(parents=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "per_posting.json").write_text(json.dumps(per, indent=1, ensure_ascii=False, default=str) + "\n")
    print(json.dumps(summary, indent=1))
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit")
    r = sub.add_parser("run")
    r.add_argument("--condition", required=True)
    r.add_argument("--set", dest="split", required=True, choices=("train", "dev", "held_out"))
    r.add_argument("--final", action="store_true")
    a = ap.parse_args()
    audit() if a.cmd == "audit" else run(a.condition, a.split, a.final)


if __name__ == "__main__":
    main()
