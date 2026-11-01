"""Score saved evaluations against Aditya's hand labels.

    python experiments/score.py sampling
    python experiments/score.py prompt

Recomputes everything from the saved raw files and labeling/*_labels.csv. Held-out labels are
read only once prompts/FROZEN.json exists. An invalid response counts as WRONG in the strict
agreement rate; it is never converted into a verdict.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.resume import load_resume  # noqa: E402
from agent.rules import evaluate  # noqa: E402

VERDICTS = ("relevant", "not_relevant")


def labels(split):
    if split == "heldout" and not (ROOT / "prompts/FROZEN.json").exists():
        sys.exit("REFUSED: held-out labels are sealed until prompts/FROZEN.json exists")
    rows = list(csv.DictReader(open(ROOT / f"labeling/{split}_labels.csv", newline="")))
    out = {int(r["posting_id"]): r["label"].strip().lower() for r in rows}
    bad = {k: v for k, v in out.items() if v not in VERDICTS}
    if bad:
        sys.exit(f"labels missing or invalid in labeling/{split}_labels.csv for ids {sorted(bad)}")
    return out


def postings(split):
    return {p["id"]: p for p in json.loads((ROOT / f"experiments/sample/{split}_postings.json").read_text())}


def short(v):
    return {"relevant": "R", "not_relevant": "N", None: "INVALID"}[v]


def sampling():
    resume = load_resume(ROOT / "resume/priya-nair.resume.example.json")
    manifest = json.loads((ROOT / "experiments/sample/manifest.json").read_text())
    lab, dev = labels("dev"), postings("dev")
    rows, summary = [], {"posting_count": 0, "calls": 0, "valid": 0, "unanimous": 0, "match_label_all": 0}
    for pid in manifest["sampling_ids"]:
        reps = sorted((ROOT / "experiments/sampling/raw").glob(f"{pid}_rep*.json"))
        recs = [json.loads(p.read_text()) for p in reps]
        verdicts = [r["verdict"] if r["valid"] else None for r in recs]
        skill_sets = [tuple(sorted(s["skill"] for s in json.loads(r["response_text"])["shared_skills"]["skills"]))
                      if r["valid"] else None for r in recs]
        record = evaluate(dev[pid], resume)["verdict"]
        row = {
            "posting_id": pid, "title": dev[pid]["title"], "hand_label": lab[pid], "RECORD": record,
            "verdicts": verdicts, "valid": sum(v is not None for v in verdicts), "n": len(recs),
            "distinct_verdicts": sorted({v for v in verdicts if v}),
            "agree_with_hand_label": sum(v == lab[pid] for v in verdicts),
            "distinct_cited_skill_sets": len({s for s in skill_sets if s is not None}),
            "distinct_raw_texts": len({r["response_text"] for r in recs}),
            "models_used": sorted({m for r in recs for m in r["models_used"]}),
            "invoked_at_utc": [r["invoked_at_utc"] for r in recs],
            "session_ids_distinct": len({r["session_id"] for r in recs}),
            "validation_errors": [r["validation_errors"] for r in recs if not r["valid"]],
        }
        rows.append(row)
        summary["posting_count"] += 1
        summary["calls"] += row["n"]
        summary["valid"] += row["valid"]
        summary["unanimous"] += int(len(set(verdicts)) == 1)
        summary["match_label_all"] += int(row["agree_with_hand_label"] == row["n"])
    out = {"summary": summary, "postings": rows}
    (ROOT / "experiments/sampling/results.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    md = ["| posting id | title | hand label | RECORD | 4 Claude verdicts | valid | agree w/ hand | distinct cited-skill sets | distinct raw texts |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {r['RECORD']} | "
                  f"{' '.join(short(v) for v in r['verdicts'])} | {r['valid']}/{r['n']} | {r['agree_with_hand_label']}/{r['n']} | "
                  f"{r['distinct_cited_skill_sets']} | {r['distinct_raw_texts']} |")
    (ROOT / "experiments/sampling/results_table.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(summary)


def score_split(version, split, lab, resume, jobs):
    d = ROOT / f"experiments/prompt_experiment/raw/{version}_{split}"
    if not d.exists():
        return None
    recs = {int(p.stem): json.loads(p.read_text()) for p in d.glob("*.json")}
    conf = Counter()
    per = {}
    for pid, gold in lab.items():
        r = recs.get(pid)
        pred = r["verdict"] if r and r["valid"] else None
        conf[(gold, short(pred))] += 1
        per[pid] = {"pred": pred, "errors": None if not r or r["valid"] else r["validation_errors"]}
    n = len(lab)
    fmt = sum(1 for p in per.values() if p["pred"] is not None)
    correct = sum(1 for pid, p in per.items() if p["pred"] == lab[pid])
    return {
        "prompt": version, "split": split, "n": n, "responses_saved": len(recs),
        "format_contract_pass": fmt, "agree_strict": correct,
        "agree_among_valid": f"{correct}/{fmt}",
        "confusion": {f"label={g} pred={p}": c for (g, p), c in sorted(conf.items())},
        "per_posting": per,
    }


def prompt():
    resume = load_resume(ROOT / "resume/priya-nair.resume.example.json")
    results = {}
    splits = ["dev"] + (["heldout"] if (ROOT / "prompts/FROZEN.json").exists() else [])
    md = []
    for split in splits:
        lab, jobs = labels(split), postings(split)
        record = {pid: evaluate(jobs[pid], resume)["verdict"] for pid in lab}
        base = {
            "always_not_relevant_baseline": sum(v == "not_relevant" for v in lab.values()),
            "RECORD_vs_hand_label": sum(record[pid] == lab[pid] for pid in lab),
            "n": len(lab), "hand_label_counts": dict(Counter(lab.values())),
        }
        results[split] = {"baselines": base}
        md += [f"## {split} (n = {len(lab)})", "",
               f"- Hand labels: {base['hand_label_counts']}",
               f"- 'Always not_relevant' baseline: {base['always_not_relevant_baseline']}/{len(lab)}",
               f"- Deterministic RECORD vs hand label: {base['RECORD_vs_hand_label']}/{len(lab)}", "",
               "| prompt | format/contract pass | agreement (invalid = wrong) | agreement among valid | confusion (label → pred) |",
               "|---|---|---|---|---|"]
        cols = []
        for v in ("v1", "v2"):
            s = score_split(v, split, lab, resume, jobs)
            if s:
                results[split][v] = s
                cols.append(v)
                conf = "; ".join(f"{k.replace('label=', '').replace(' pred=', '→')}: {c}" for k, c in s["confusion"].items())
                md.append(f"| {v} | {s['format_contract_pass']}/{s['n']} | {s['agree_strict']}/{s['n']} | {s['agree_among_valid']} | {conf} |")
        md += ["", "| posting id | title | hand label | RECORD | " + " | ".join(cols) + " |",
               "|---|---|---|---|" + "---|" * len(cols)]
        for pid in lab:
            preds = [short(results[split][v]["per_posting"][pid]["pred"]) for v in cols]
            md.append(f"| {pid} | {jobs[pid]['title']} | {short(lab[pid])} | {short(record[pid])} | " + " | ".join(preds) + " |")
        md.append("")
    (ROOT / "experiments/prompt_experiment/results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    (ROOT / "experiments/prompt_experiment/results_tables.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    {"sampling": sampling, "prompt": prompt}[sys.argv[1]]()
