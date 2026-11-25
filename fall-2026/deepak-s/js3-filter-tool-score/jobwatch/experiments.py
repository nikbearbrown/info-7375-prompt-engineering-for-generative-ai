"""Phase 6: what moves the score. One change to one object at a time, on the held-out postings.

    python -m jobwatch experiment-filter --dataset <jsonl> --heldout-seed-a A --heldout-seed-b B
        E1, the filter file: v1 against the final version (no change was adopted, so final = v1),
            plus each rejected candidate C1-C5 for information (decisions were made at Gate 3b).
        E2, a setting: the location weight 2 -> 0 (FILTER.md section 2 keeps it "so that it can be
            changed as a setting in Phase 6"); T stays 8.
        Writes experiments/E1-decisions.json and E2-decisions.json (no labels read).
    python -m jobwatch experiment-judge --dataset <jsonl> --heldout-seed-a A --heldout-seed-b B --arm ARM --run N
        E3, the context given to Claude: ARM title_text (the posting title and its text) or
        title_only (the title alone); location is in neither arm. Prompt prompts/js3_relevance_v1.md,
        which quotes the FILTER.md section 0 labeling rule; JS1 claude-cli backend, model
        claude-sonnet-5-5. Writes experiments/E3/<arm>-run<N>.json and every call's files.
    python -m jobwatch experiment-report --dataset <jsonl> --heldout-seed-a A --heldout-seed-b B
        Reads labels/heldout.csv and the files above; writes experiments/results.json and .md:
        per stratum (never pooled, FILTER.md section 7), counts with denominators, agreement with
        the labels, precision and recall where the counts allow, each with its exact 95% interval;
        for E3, how many labels move between the two identical baseline runs and between the
        baseline and the change.

The held-out postings are found by redrawing with the held-out seeds (jobwatch/heldout.py), so the
first two commands never open labels/heldout.csv; the report checks the redrawn keys against it.
Abstentions are counted separately and excluded from precision and recall (FILTER.md section 7).
"""
import dataclasses
import json

from jobwatch import claude_judge, heldout, sheets
from jobwatch import filter as flt
from jobwatch.stats import clopper_pearson

FINAL = flt.V1  # no Gate 3b candidate was adopted (FILTER.md section 8)
E2_RULES = dataclasses.replace(flt.V1, version="v1, location weight 0", location_weight=0)
ARMS = ("title_text", "title_only")


def heldout_lines(lines, seed_a, seed_b):
    _, chosen = heldout.draw(list(lines), {"A": seed_a, "B": seed_b})
    return [(s, ln) for s in ("A", "B") for ln in chosen[s]]


def filter_decisions(picked, arms):
    out = {}
    for name, rules in arms:
        out[name] = {ln["key"]: {"stratum": s, **{k: v for k, v in flt.evaluate(ln, rules).items()
                                                   if k in ("decision", "score", "reasons")}} for s, ln in picked}
    return out


def e1_arms():
    return [("v1", flt.V1), ("final (= v1)", FINAL)] + [(f"v1+{c} (rejected at Gate 3b)", r) for c, (_, r) in flt.CANDIDATES.items()]


def e2_arms():
    return [("v1 (location weight 2)", flt.V1), ("v1, location weight 0", E2_RULES)]


def context(line, arm):
    if arm == "title_only":
        return f"Title: {line['title']}"
    return f"Title: {line['title']}\nText:\n{line['text']}"


def parse_label(result):
    try:
        lab = json.loads(result)["label"]
    except (TypeError, ValueError, KeyError):
        return None
    return lab if lab in ("relevant", "not_relevant") else None


def run_judge(tools, picked, arm, run_no, template, model, clock):
    out_dir = f"experiments/E3/{arm}-run{run_no}"
    labels = {}
    for s, ln in picked:
        system, user = claude_judge.fill(template, CONTEXT=context(ln, arm))
        stem = ln["key"].replace(":", "_")
        res = claude_judge.call(tools, system, user, model, stem, out_dir, clock)
        labels[ln["key"]] = {"stratum": s, "label": None if res["error"] else parse_label(res["result"]),
                             "error": res["error"], "model": res["model"], "called_at": res["called_at"]}
    return labels


# --- the report (reads the held-out labels) ----------------------------------------------------------
def interval(k, n):
    if n == 0:
        return None
    lo, hi = clopper_pearson(k, n)
    return {"k": k, "n": n, "rate": k / n, "ci95": [lo, hi]}


def filter_metrics(decisions, labels, stratum):
    keys = [k for k, d in decisions.items() if d["stratum"] == stratum]
    kept = [k for k in keys if decisions[k]["decision"] == "keep"]
    rej = [k for k in keys if decisions[k]["decision"] == "reject"]
    abst = [k for k in keys if decisions[k]["decision"] == "abstain"]
    decided = kept + rej
    agree = sum((decisions[k]["decision"] == "keep") == (labels[k] == "relevant") for k in decided)
    tp = sum(labels[k] == "relevant" for k in kept)
    relevant_decided = sum(labels[k] == "relevant" for k in decided)
    return {"n": len(keys), "kept": len(kept), "rejected": len(rej), "abstained": len(abst),
            "labeled_relevant": sum(labels[k] == "relevant" for k in keys),
            "agreement": interval(agree, len(decided)), "precision": interval(tp, len(kept)),
            "recall": interval(tp, relevant_decided)}


def judge_metrics(run, labels, stratum):
    keys = [k for k, d in run.items() if d["stratum"] == stratum]
    answered = [k for k in keys if run[k]["label"] in ("relevant", "not_relevant")]
    said_rel = [k for k in answered if run[k]["label"] == "relevant"]
    tp = sum(labels[k] == "relevant" for k in said_rel)
    agree = sum(run[k]["label"] == labels[k] for k in answered)
    return {"n": len(keys), "said_relevant": len(said_rel), "said_not_relevant": len(answered) - len(said_rel),
            "no_answer": len(keys) - len(answered), "agreement": interval(agree, len(answered)),
            "precision": interval(tp, len(said_rel)), "recall": interval(tp, sum(labels[k] == "relevant" for k in answered))}


def moved(a, b, stratum=None):
    keys = [k for k in a if (stratum is None or a[k]["stratum"] == stratum) and k in b]
    return {"moved": sum(a[k]["label"] != b[k]["label"] for k in keys), "n": len(keys)}


def report(sheet_rows, picked, e1, e2, e3):
    labels = {r["posting_key"]: r["label"] for r in sheet_rows}
    redrawn = {ln["key"] for _, ln in picked}
    if set(labels) != redrawn:
        raise ValueError("labels/heldout.csv keys differ from the held-out redraw; the seeds or the dataset differ")
    empty = [k for k, v in labels.items() if v not in ("relevant", "not_relevant")]
    if empty:
        raise ValueError(f"labels/heldout.csv: {len(empty)} rows without a relevant/not_relevant label")
    out = {"labels_relevant": {s: sum(labels[ln["key"]] == "relevant" for st, ln in picked if st == s) for s in ("A", "B")},
           "overrides": sum(bool(r["override_reason"].strip()) for r in sheet_rows), "E1": {}, "E2": {}, "E3": {}}
    for name, dec in e1.items():
        out["E1"][name] = {s: filter_metrics(dec, labels, s) for s in ("A", "B")}
    for name, dec in e2.items():
        out["E2"][name] = {s: filter_metrics(dec, labels, s) for s in ("A", "B")}
    for name, run in e3.items():
        out["E3"][name] = {s: judge_metrics(run, labels, s) for s in ("A", "B")}
    base1, base2, change = e3.get("title_text-run1"), e3.get("title_text-run2"), e3.get("title_only-run1")
    if base1 and base2 and change:
        out["E3_movement"] = {s: {"baseline_run1_vs_run2": moved(base1, base2, s), "baseline_run1_vs_title_only": moved(base1, change, s),
                                  "baseline_run2_vs_title_only": moved(base2, change, s)} for s in ("A", "B")}
    return out


def _fmt(iv):
    return "n/a (denominator 0)" if iv is None else f"{iv['k']}/{iv['n']} = {iv['rate']:.3f} [{iv['ci95'][0]:.3f}, {iv['ci95'][1]:.3f}]"


def render(res):
    L = ["# Phase 6 results on the held-out labels (generated by python -m jobwatch experiment-report)", "",
         "Per stratum, never pooled (FILTER.md section 7). Rates are k/n with the exact (Clopper-Pearson) 95% interval. "
         "Abstentions are excluded from agreement, precision and recall.", "",
         f"Held-out labels: stratum A {res['labels_relevant']['A']}/30 relevant, stratum B {res['labels_relevant']['B']}/10 relevant; "
         f"OVERRIDEs {res['overrides']}.", ""]
    for exp in ("E1", "E2"):
        L += [f"## {exp}", "", "| Arm | Stratum | n | kept | rejected | abstained | labeled relevant | agreement | precision | recall |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for arm, by in res[exp].items():
            for s, m in by.items():
                L.append(f"| {arm} | {s} | {m['n']} | {m['kept']} | {m['rejected']} | {m['abstained']} | {m['labeled_relevant']} | "
                         f"{_fmt(m['agreement'])} | {_fmt(m['precision'])} | {_fmt(m['recall'])} |")
        L.append("")
    L += ["## E3", "", "| Run | Stratum | n | said relevant | said not_relevant | no answer | agreement | precision | recall |",
          "|---|---|---|---|---|---|---|---|---|"]
    for arm, by in res["E3"].items():
        for s, m in by.items():
            L.append(f"| {arm} | {s} | {m['n']} | {m['said_relevant']} | {m['said_not_relevant']} | {m['no_answer']} | "
                     f"{_fmt(m['agreement'])} | {_fmt(m['precision'])} | {_fmt(m['recall'])} |")
    if "E3_movement" in res:
        L += ["", "Labels that moved (postings whose answer differs):", ""]
        for s, m in res["E3_movement"].items():
            b, c, d = m["baseline_run1_vs_run2"], m["baseline_run1_vs_title_only"], m["baseline_run2_vs_title_only"]
            L.append(f"- Stratum {s}: baseline run 1 vs run 2 (identical setup): {b['moved']}/{b['n']}; "
                     f"baseline run 1 vs title only: {c['moved']}/{c['n']}; baseline run 2 vs title only: {d['moved']}/{d['n']}.")
        L += ["", "Rule (CLAUDE.md): if the change moves no more labels than the two identical baseline runs move, no conclusion "
              "about the change can be drawn."]
    return "\n".join(L) + "\n"


def read_heldout(tools):
    return sheets.read_sheet(tools, heldout.SHEET)[2]
