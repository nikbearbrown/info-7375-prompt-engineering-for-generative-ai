"""Compare Weiting's blind hand labels against the filter, and refit T.

    python3 tools/analyse_audit.py audit/labels-weiting.json

Written **before the labels existed**, so the analysis could not be shaped by
the numbers it would produce. The method it implements is the one FILTER.md §6
committed to and `reports/what-moves-the-score.md` §4 restates:

1. count disagreements on the sample, broken down by stratum;
2. say what a sample of this size can and cannot show — a count, never a rate
   for the corpus;
3. split the labelled postings into a training half and a held-out half with a
   recorded seed, pick the threshold that best matches the labels **on the
   training half only**, and report its agreement **on the held-out half**
   against the baseline T = 6.

The labels are blind: `audit/audit-form.html` showed no score, no bucket and
no gate, and shuffled the order. The filter's own decisions were written to
`audit/audit-answer-key.json` at the same time and are only read here.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod, pipeline, score as scorer  # noqa: E402

SPLIT_SEED = 20261123


def wanted(label: str) -> bool | None:
    """Her verdict as a boolean, or None for 'unsure'."""
    return {"yes": True, "no": False}.get(label)


def filter_kept(decision) -> bool:
    return decision.bucket == pipeline.SHORTLISTED


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("labels", help="the JSON the form downloaded")
    ap.add_argument("--out", default=str(ROOT / "audit" / "audit-analysis.json"))
    args = ap.parse_args(argv)

    labels_doc = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    labels = labels_doc["labels"]
    key = json.loads(
        (ROOT / "audit" / "audit-answer-key.json").read_text(encoding="utf-8")
    )["decisions"]

    postings = corpus_mod.load()
    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    decisions = {d.posting.identity: d for d in pipeline.run(postings, persona)}

    rows = []
    for identity, verdict in labels.items():
        if identity not in decisions:
            print(f"  skipping {identity}: not in the corpus", file=sys.stderr)
            continue
        d = decisions[identity]
        rows.append({
            "identity": identity,
            "title": d.posting.title,
            "board": d.posting.board,
            "strata": key.get(identity, {}).get("strata", []),
            "her": verdict,
            "her_bool": wanted(verdict),
            "bucket": d.bucket,
            "gate_failed": d.gate_failed,
            "score": None if d.score is None else d.score.total,
            "filter_kept": filter_kept(d),
        })

    decided = [r for r in rows if r["her_bool"] is not None]
    unsure = [r for r in rows if r["her_bool"] is None]

    agree = [r for r in decided if r["her_bool"] == r["filter_kept"]]
    disagree = [r for r in decided if r["her_bool"] != r["filter_kept"]]
    false_neg = [r for r in disagree if r["her_bool"] and not r["filter_kept"]]
    false_pos = [r for r in disagree if not r["her_bool"] and r["filter_kept"]]

    # --- the threshold refit, on the scoreable subset only -------------------
    scoreable = [r for r in decided if r["score"] is not None]
    rng = random.Random(SPLIT_SEED)
    shuffled = sorted(scoreable, key=lambda r: r["identity"])
    rng.shuffle(shuffled)
    half = len(shuffled) // 2
    train, held = shuffled[:half], shuffled[half:]

    def agreement(rows_, t):
        return sum(1 for r in rows_ if (r["score"] >= t) == r["her_bool"])

    candidates = list(range(-6, 11))
    best_t, best_train = None, -1
    for t in candidates:
        a = agreement(train, t)
        if a > best_train:
            best_t, best_train = t, a

    report = {
        "labels_from": labels_doc.get("labelled_by"),
        "labelled_on": labels_doc.get("labelled_on"),
        "blind": labels_doc.get("blind"),
        "form_seed": labels_doc.get("seed"),
        "split_seed": SPLIT_SEED,
        "filter_version": pipeline.FILTER_VERSION,
        "scorer_version": scorer.SCORER_VERSION,
        "baseline_threshold": scorer.THRESHOLD,
        "counts": {
            "labelled": len(rows),
            "decided": len(decided),
            "unsure": len(unsure),
            "agree": len(agree),
            "disagree": len(disagree),
            "filter_missed_something_she_wanted": len(false_neg),
            "filter_kept_something_she_did_not": len(false_pos),
        },
        "by_stratum": {
            s: Counter(
                "agree" if r["her_bool"] == r["filter_kept"] else "disagree"
                for r in decided if s in r["strata"]
            )
            for s in ("random_reject", "near_threshold", "kept")
        },
        "her_labels": Counter(r["her"] for r in rows),
        "unsure_rows": [
            {k: r[k] for k in ("identity", "title", "board", "bucket", "score")}
            for r in unsure
        ],
        "disagreements": disagree,
        "threshold_refit": {
            "scoreable_and_decided": len(scoreable),
            "train_n": len(train),
            "held_out_n": len(held),
            "best_t_on_train": best_t,
            "agreement_on_train": f"{best_train}/{len(train)}",
            "held_out_at_best_t": f"{agreement(held, best_t)}/{len(held)}",
            "held_out_at_baseline_6": f"{agreement(held, 6)}/{len(held)}",
            "all_candidates_on_train": {
                t: f"{agreement(train, t)}/{len(train)}" for t in candidates
            },
        },
    }
    report["by_stratum"] = {k: dict(v) for k, v in report["by_stratum"].items()}
    report["her_labels"] = dict(report["her_labels"])

    Path(args.out).write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    c = report["counts"]
    print(f"labels: {c['labelled']}  decided: {c['decided']}  unsure: {c['unsure']}")
    print(f"agree: {c['agree']}   disagree: {c['disagree']}")
    print(f"  she wanted it, the filter did not keep it: "
          f"{c['filter_missed_something_she_wanted']}")
    print(f"  the filter kept it, she did not want it:   "
          f"{c['filter_kept_something_she_did_not']}")
    print(f"by stratum: {report['by_stratum']}")
    tr = report["threshold_refit"]
    print(f"\nthreshold refit (split seed {SPLIT_SEED}):")
    print(f"  scoreable+decided {tr['scoreable_and_decided']}  "
          f"train {tr['train_n']}  held out {tr['held_out_n']}")
    print(f"  best T on train:  {tr['best_t_on_train']}  ({tr['agreement_on_train']})")
    print(f"  held out at that T: {tr['held_out_at_best_t']}")
    print(f"  held out at T=6:    {tr['held_out_at_baseline_6']}")
    print(f"\nwrote {args.out}")
    print("\nA count, not a rate. See FILTER.md §6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
