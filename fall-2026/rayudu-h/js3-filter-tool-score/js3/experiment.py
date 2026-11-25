"""What moves the score (Chapter 9): one change to one object at a time, measured on the HELD-OUT labels.

Claude-judge experiments (each one call per held-out posting, a fresh `claude -p` each time):
    E0a, E0b  baseline twice: prompt v2 (JS1), context = titles + skills (JS1), model sonnet  -> the noise floor
    E2        the prompt:   v2 -> v3 (the rule paragraph replaced by the labeling question)
    E3        the context:  titles + skills -> plus education, target roles, location, remote, sponsorship
    E4        a setting:    model sonnet -> haiku
    E5        the context again, but under prompt v3 (one change from E2, added after the first round)
Filter-file experiments (deterministic, no Claude):
    E1a       FILTER.md v1.0 -> v1.1 (the accepted X1)
    E1b       v1.1 with the threshold fitted on the AUDIT labels (never the held-out ones)

    python -m js3 experiment run E0a      # writes experiments/E0a.jsonl (refuses to overwrite)
    python -m js3 experiment report       # writes experiments/report.md
"""
from __future__ import annotations

import copy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

from jsagent import claude_judge, resume as resume_mod

from . import ROOT, audit, corpus, filterdoc, labeling, sample, score, stats

EXP_DIR = ROOT / "experiments"
CONFIGS = {
    "E0a": {"prompt": "v2", "context": "titles+skills", "model": "sonnet", "what": "baseline (run 1)"},
    "E0b": {"prompt": "v2", "context": "titles+skills", "model": "sonnet", "what": "baseline (run 2): same everything"},
    "E2": {"prompt": "v3", "context": "titles+skills", "model": "sonnet", "what": "the prompt: v2 -> v3"},
    "E3": {"prompt": "v2", "context": "profile", "model": "sonnet", "what": "the context: + profile fields"},
    "E4": {"prompt": "v2", "context": "titles+skills", "model": "haiku", "what": "a setting: model sonnet -> haiku"},
    # added after the first round (Nov 22): context under the open prompt; ONE change from E2, not from E0a
    "E5": {"prompt": "v3", "context": "profile", "model": "sonnet", "what": "the context, under prompt v3: + profile fields",
           "base": "E2"},
}
# From persona/priya-nair.resume.json and persona/priya-nair.profile.yml (fictional). No contact fields.
PROFILE_EXTRA = {
    "education": "MS, Information Systems, completed 2025-12",
    "experience_months": 8,
    "target_roles": {"primary": "AI Engineer / ML Engineer", "secondary": "Data Engineer"},
    "location": "Boston, MA",
    "open_to_remote": True,
    "needs_visa_sponsorship": True,
}


def heldout(label_set: str = "first"):
    s = json.loads((ROOT / "audit" / "samples.json").read_text())
    labels = labeling.read_labels(ROOT / "audit" / "labels.csv")
    if label_set == "corrected":
        from . import relabel
        labels = {k: v for k, v in relabel.corrected_labels().items() if k in labels}
    return s["heldout"], {k: labels[k] for k in s["heldout"]}


def resume_view(resume: dict, context: str) -> dict:
    view = resume_mod.judge_view(resume)
    if context == "profile":
        view = {**view, **PROFILE_EXTRA}
    return view


def build_prompt(version: str, context: str, posting: dict, resume: dict) -> str:
    template = claude_judge.load_prompt(version)
    return (template.replace("{{RESUME_JSON}}", json.dumps(resume_view(resume, context), indent=2))
                    .replace("{{POSTING_JSON}}", json.dumps(claude_judge.posting_view(posting), indent=2)))


def run(exp: str, caller=claude_judge.call_claude, workers: int = 4) -> list:
    cfg = CONFIGS[exp]
    keys, labels = heldout()
    c = corpus.load()
    resume = resume_mod.load(ROOT / "persona" / "priya-nair.resume.json")
    out = EXP_DIR / f"{exp}.jsonl"
    EXP_DIR.mkdir(exist_ok=True)

    def one(k):
        p = c["postings"][k]
        prompt = build_prompt(cfg["prompt"], cfg["context"], p, resume)
        call = caller(prompt, cfg["model"])
        parsed, errors = claude_judge.validate(call["result"]) if not call["is_error"] else (None, ["claude call failed"])
        return {"exp": exp, **cfg, "key": k, "item": labels[k]["item"], "title": p["title"],
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), **call,
                "valid": parsed is not None, "errors": errors,
                "verdict": parsed["verdict"] if parsed else None,
                "confidence": parsed["confidence"] if parsed else None,
                "justification": parsed["justification"] if parsed else None}

    with ThreadPoolExecutor(max_workers=workers) as pool, open(out, "x") as f:   # never overwrite a run
        recs = list(pool.map(one, keys))
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return recs


def load_run(exp: str) -> dict:
    with open(EXP_DIR / f"{exp}.jsonl") as f:
        return {r["key"]: r for r in map(json.loads, f)}


def agreement(pred: dict, labels: dict) -> dict:
    """pred: key -> 'relevant' | 'not relevant' | 'cannot judge' | None (invalid). Positive = relevant."""
    m = {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "abstain": 0, "invalid": 0}
    for k, lab in labels.items():
        v, h = pred.get(k), lab["verdict"]
        if v is None:
            m["invalid"] += 1
        elif v not in ("relevant", "not relevant"):
            m["abstain"] += 1
        else:
            m[{(True, True): "TP", (True, False): "FP", (False, True): "FN", (False, False): "TN"}[
                (v == "relevant", h == "relevant")]] += 1
    m["n"] = len(labels)
    m["agree"] = m["TP"] + m["TN"]
    lo, hi = stats.wilson(m["agree"], m["n"])
    m["agree_ci"] = (round(lo, 3), round(hi, 3))
    return m


def filter_predictions(flt: dict, keys, c) -> dict:
    return {k: ("relevant" if score.score(c["postings"][k], flt)["decision"] == "kept" else "not relevant") for k in keys}


def report(label_set: str = "first") -> str:
    keys, labels = heldout(label_set)
    pos = sum(1 for v in labels.values() if v["verdict"] == "relevant")
    c = corpus.load()
    vs = audit.versions()
    v10, v11, v12 = vs["1.0"], vs["1.1"], vs["1.2"]
    # E1b: fit the threshold on the AUDIT labels only (sample.fit_threshold refuses held-out ids)
    s, audit_labels, held, audit_keys = audit.load_inputs(label_set)
    res11 = {k: score.score(p, v11) for k, p in c["postings"].items()}
    fit = sample.fit_threshold({k: audit_labels[k]["verdict"] for k in audit_keys}, res11, heldout=held,
                               current=v11["threshold"])
    v11_fit = copy.deepcopy(v11)
    v11_fit["filter_version"] = "1.1 (fitted threshold)"
    v11_fit["threshold"] = fit["threshold"]

    L = [f"# Experiments report (generated by `python -m js3 experiment report{' --labels corrected' if label_set == 'corrected' else ''}`)", "",
         f"**Labels: {'CORRECTED: second-pass verdicts (experience shown) where they exist, else first-pass' if label_set == 'corrected' else 'first pass, as committed Nov 22 (before any experiment)'}.**", "",
         f"Held-out set: {len(keys)} postings (20 drawn from kept, 20 from rejected by v1.0; stratified, so these "
         f"numbers describe these 40, not the corpus). Hemanth marked {pos} relevant and {len(keys) - pos} not relevant.",
         "", "## Filter-file changes (deterministic)", "",
         "| exp | change | agree / 40 | Wilson 95% | TP | FP | FN | TN |", "|---|---|---:|---|---:|---:|---:|---:|"]
    rows = [("E1 base", "FILTER.md v1.0", filter_predictions(v10, keys, c)),
            ("E1a", "v1.0 -> v1.1 (X1: 'Technical Staff' is not seniority)", filter_predictions(v11, keys, c)),
            ("E1b", f"v1.1, threshold {v11['threshold']} -> {fit['threshold']} (fitted on the 55 audit labels: "
                    f"{fit['correct']}/{fit['n']} in-sample)", filter_predictions(v11_fit, keys, c)),
            ("E1c", "v1.1 -> v1.2 (R17: reject when the text asks for 5+ years; cut-off fitted on corrected tuning "
                    "labels, never on these 40)", filter_predictions(v12, keys, c))]
    for name, what, pred in rows:
        m = agreement(pred, labels)
        L.append(f"| {name} | {what} | {m['agree']} | {m['agree_ci'][0]:.0%}–{m['agree_ci'][1]:.0%} | "
                 f"{m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} |")
    L += ["", "Threshold fit table (audit labels, threshold-decided postings only):", "",
          "| threshold | correct / n |", "|---:|---:|"]
    L += [f"| {r['threshold']} | {r['correct']} / {r['n']} |" for r in fit["table"]]

    L += ["", "## Claude-judge changes (one object at a time; each run is 40 fresh `claude -p` calls)", "",
          "| exp | change | model used | agree / 40 | Wilson 95% | TP | FP | FN | TN | abstain | invalid | "
          "flips vs its baseline |", "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    runs = {e: load_run(e) for e in CONFIGS if (EXP_DIR / f"{e}.jsonl").exists()}
    for e, recs in runs.items():
        base_name = CONFIGS[e].get("base", "E0a")
        base = {k: r["verdict"] for k, r in runs.get(base_name, {}).items()}
        pred = {k: r["verdict"] for k, r in recs.items()}
        m = agreement(pred, labels)
        flips = f"{sum(1 for k in keys if base and pred.get(k) != base.get(k))} (vs {base_name})"
        used = sorted({u for r in recs.values() for u in r["models_used"]})
        L.append(f"| {e} | {CONFIGS[e]['what']} | {', '.join(used)} | {m['agree']} | "
                 f"{m['agree_ci'][0]:.0%}–{m['agree_ci'][1]:.0%} | {m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} | "
                 f"{m['abstain']} | {m['invalid']} | {flips if e != 'E0a' else '—'} |")
    if runs:
        first = min(r["started_at"] for recs in runs.values() for r in recs.values())
        last = max(r["started_at"] for recs in runs.values() for r in recs.values())
        L += ["", f"Calls made from {first} to {last}."]
    return "\n".join(L) + "\n"
