"""What moves the score: one change to one object at a time, measured on the 30 held-out labels.

    python -B experiments/one_change.py filter  --a v1.0 --b v1.1      # the filter file
    python -B experiments/one_change.py setting                          # threshold: hand-set 6 vs fitted on audit labels
    python -B experiments/one_change.py claude --cond baseline           # judge_v1, no extra context, no tools
    python -B experiments/one_change.py claude --cond baseline_repeat    # A-A control: the same, asked again
    python -B experiments/one_change.py claude --cond prompt_v2          # the prompt:  judge_v2_abstain.md
    python -B experiments/one_change.py claude --cond context_score      # the context: + the filter's score line
    python -B experiments/one_change.py claude --cond tools_score        # the tool list: + score_posting (MCP)
    python -B experiments/one_change.py report

The held-out set (out/audit/sample_v1.0.json: heldout_reject + heldout_kept_or_close) was sealed
before any change was designed; no rule or prompt was tuned on it. A Claude condition that already
has a result is not rerun unless --rerun is given, and a rerun is saved beside the first, not over it.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import corpus, filter as flt, judge, policy  # noqa: E402
from agent3.resume import load_resume  # noqa: E402
from agent3.stats import fmt_rate  # noqa: E402

OUT = policy.OUT / "experiments"
CONDS = {
    "baseline":        {"template": "judge_v1.md", "context": False, "tools": False, "object": "(none: reference)"},
    "baseline_repeat": {"template": "judge_v1.md", "context": False, "tools": False, "object": "(none: A-A control)"},
    "prompt_v2":       {"template": "judge_v2_abstain.md", "context": False, "tools": False, "object": "the prompt"},
    "context_score":   {"template": "judge_v1.md", "context": True, "tools": False, "object": "the context"},
    "tools_score":     {"template": "judge_v1.md", "context": False, "tools": True, "object": "the tool list"},
}


def load(sets):
    sample = json.loads((policy.OUT / "audit" / "sample_v1.0.json").read_text(encoding="utf-8"))
    with (ROOT / "labels" / "hand_labels.csv").open(encoding="utf-8", newline="") as f:
        labels = {r["id"]: r["hand_label"] for r in csv.DictReader(f)}
    ids = [pid for s in sets for pid in sample["sets"][s]]
    missing = [pid for pid in ids if pid not in labels]
    if missing:
        raise SystemExit(f"{len(missing)} of these postings have no hand label yet")
    return ids, labels


HELDOUT = ("heldout_reject", "heldout_kept_or_close")
AUDIT = ("audit_reject_random", "audit_close", "audit_kept_random")


def score_filter(ids, labels, postings, cfg) -> dict:
    tp = fp = fn = tn = ct = 0
    for pid in ids:
        v = flt.apply(postings[pid], cfg)["verdict"]
        rel = labels[pid] == "relevant"
        if v == "cannot_tell":
            ct += 1
        elif v == "keep":
            tp += rel
            fp += not rel
        else:
            fn += rel
            tn += not rel
    n = tp + fp + fn + tn
    return {"version": cfg["version"], "threshold": cfg["threshold"], "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "cannot_tell": ct, "agree": tp + tn, "n": n}


def describe(m) -> str:
    return (f"{m['version']} (threshold {m['threshold']}): agrees with my labels on {fmt_rate(m['agree'], m['n'])}; "
            f"kept {m['tp'] + m['fp']} (relevant {m['tp']}), missed relevant {m['fn']}")


def run_filter(args):
    ids, labels = load(HELDOUT)
    ps = corpus.load()["postings"]
    a, b = (score_filter(ids, labels, ps, flt.VERSIONS[v]) for v in (args.a, args.b))
    flips = [pid for pid in ids if flt.apply(ps[pid], flt.VERSIONS[args.a])["verdict"]
             != flt.apply(ps[pid], flt.VERSIONS[args.b])["verdict"]]
    rec = {"object": "the filter file", "a": a, "b": b, "flipped_ids": flips,
           "flips_toward_my_label": sum((flt.apply(ps[p], flt.VERSIONS[args.b])["verdict"] == "keep")
                                        == (labels[p] == "relevant") for p in flips)}
    save(f"filter_{args.a}_vs_{args.b}", rec)
    print(describe(a), "\n" + describe(b), f"\nflipped {len(flips)} held-out postings, "
          f"{rec['flips_toward_my_label']} toward my label")


def run_setting(args):
    audit_ids, labels = load(AUDIT)
    held_ids, _ = load(HELDOUT)
    ps = corpus.load()["postings"]
    base = flt.VERSIONS[args.version]
    fits = {t: score_filter(audit_ids, labels, ps, {**base, "threshold": t})["agree"] for t in range(2, 13)}
    best = max(fits.values())
    t_fit = min((t for t, v in fits.items() if v == best), key=lambda t: (abs(t - base["threshold"]), t))
    a = score_filter(held_ids, labels, ps, base)
    b = score_filter(held_ids, labels, ps, {**base, "version": f"{base['version']}+t{t_fit}", "threshold": t_fit})
    rec = {"object": "a setting (threshold)", "fit_on": "audit labels (50)", "audit_agreement_by_threshold": fits,
           "t_fit": t_fit, "a": a, "b": b}
    save(f"setting_threshold_{base['version']}", rec)
    print("agreement on the 50 audit labels by threshold:", fits)
    print(f"fitted threshold: {t_fit} (ties broken toward the hand-set {base['threshold']})")
    print("held-out:", describe(a), "\n          " + describe(b))


def run_claude(args):
    spec = CONDS[args.cond]
    path = OUT / f"claude_{args.cond}.json"
    if path.exists() and not args.rerun:
        raise SystemExit(f"{path.name} exists; the held-out set is run once per condition (use --rerun to add a run)")
    ids, labels = load(HELDOUT)
    c = corpus.load()["postings"]
    resume = load_resume(policy.check_read(ROOT / "data" / "resume_jack_spencer.json"))
    template = (ROOT / "prompts" / spec["template"]).read_text(encoding="utf-8")
    ps = [c[pid] for pid in ids]
    kw = {}
    if spec["tools"]:
        kw = {"mcp_servers": judge.js3_tool_server(), "allowed_tools": ("mcp__js3-filter__score_posting",)}
    contexts = {}
    if spec["context"]:
        for p in ps:   # one context string per posting: the filter's own record for it
            r = flt.apply(p, flt.V1_0)
            contexts[p["id"]] = (f"FILTER RESULT (keyword filter, FILTER.md {r['filter_version']}; a keyword count, "
                                 f"not a judgment): {r['verdict']}, score {r['score']} (keep at >= "
                                 f"{flt.V1_0['threshold']}): {r['because']}")
    replies = judge.judge_all(ps, resume, template, contexts=contexts, **kw)
    rec = {"cond": args.cond, **spec, "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "replies": replies}
    if path.exists():
        path = OUT / f"claude_{args.cond}_rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    policy.write_bytes(path, (json.dumps(rec, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    valid = sum(r["valid"] for r in replies.values())
    print(f"{args.cond}: {valid}/{len(replies)} valid -> {path.relative_to(ROOT)}")


def claude_metrics(rec, labels) -> dict:
    v = {pid: r["verdict"] for pid, r in rec["replies"].items()}
    answered = [pid for pid in v if v[pid] in ("relevant", "not_relevant")]
    agree = sum(v[pid] == labels[pid] for pid in answered)
    return {"n": len(v), "invalid": sum(not r["valid"] for r in rec["replies"].values()),
            "cannot_tell": sum(x == "cannot_tell" for x in v.values()), "answered": len(answered), "agree": agree,
            "tool_calls": sum(len(r.get("tool_calls") or []) for r in rec["replies"].values()), "verdicts": v}


def report(args):
    _, labels = load(HELDOUT)
    lines = ["# One change at a time: results on the 30 held-out labels", ""]
    for name in ("filter", "setting"):
        for p in sorted(OUT.glob(f"{name}_*.json")):
            r = json.loads(p.read_text(encoding="utf-8"))
            lines += [f"## {r['object']} ({p.name})", f"- A: {describe(r['a'])}", f"- B: {describe(r['b'])}", ""]
    base_path = OUT / "claude_baseline.json"
    if base_path.exists():
        base = claude_metrics(json.loads(base_path.read_text(encoding="utf-8")), labels)
        lines += ["## Claude judge conditions", "",
                  "| condition | object changed | valid | answered | agrees with my label | cannot_tell | "
                  "tool calls | verdicts that differ from baseline |", "|---|---|---:|---:|---:|---:|---:|---:|"]
        for cond in CONDS:
            p = OUT / f"claude_{cond}.json"
            if not p.exists():
                continue
            rec = json.loads(p.read_text(encoding="utf-8"))
            m = claude_metrics(rec, labels)
            diff = sum(m["verdicts"][pid] != base["verdicts"].get(pid) for pid in m["verdicts"])
            lines.append(f"| {cond} | {rec['object']} | {m['n'] - m['invalid']}/{m['n']} | {m['answered']} | "
                         f"{fmt_rate(m['agree'], m['answered'])} | {m['cannot_tell']} | {m['tool_calls']} | "
                         f"{'-' if cond == 'baseline' else diff} |")
    text = "\n".join(lines) + "\n"
    policy.write_bytes(OUT / "REPORT.md", text.encode("utf-8"))
    print(text)


def save(name, rec):
    policy.write_bytes(OUT / f"{name}.json", (json.dumps(rec, indent=1) + "\n").encode("utf-8"))


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="what", required=True)
    f = sub.add_parser("filter")
    f.add_argument("--a", default="v1.0")
    f.add_argument("--b", required=True)
    s = sub.add_parser("setting")
    s.add_argument("--version", default="v1.0")
    c = sub.add_parser("claude")
    c.add_argument("--cond", required=True, choices=sorted(CONDS))
    c.add_argument("--rerun", action="store_true")
    sub.add_parser("report")
    args = ap.parse_args(argv)
    {"filter": run_filter, "setting": run_setting, "claude": run_claude, "report": report}[args.what](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
