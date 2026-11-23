"""Chapter 9 experiment harness: dataset, dev/held-out split, label access.

    python3 -m js3.experiment split          # compute + write logs/experiment/split.json
    python3 -m js3.experiment measure dev    # rule 4 on the dev split
    JS3_FINAL_HELDOUT=1 python3 -m js3.experiment measure heldout   # ONCE, after the rule is locked

Split rule: EXPERIMENT.md section 2. Held-out labels are returned only when
JS3_FINAL_HELDOUT=1, and every such read is appended to
logs/experiment/heldout_access.log.
"""
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from js3 import filter as flt
from js3.postings import load_run

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "logs" / "run_20261121T132140Z.json"
AUDIT = ROOT / "logs" / "reject_audit"
OUT = ROOT / "logs" / "experiment"
SPLIT_SEED = 7375
DEV_FRACTION = 0.6
DRAFTS = ("A_random_rejected_draft.md", "B_near_threshold_draft.md", "C_relevant_draft.md")
_LABEL_RE = re.compile(r"^\*\*([ABC]\d+): (relevant|not relevant)\*\*\s*[—-]\s*(.*)$", re.M)


def _key(board, pid):
    return (str(board), str(pid))


def dataset():
    """The 88 distinct hand-judged postings, with the filter v1.0.0 result,
    WITHOUT labels. Returns {key: {"board","id","title","audit_labels",
    "filter_bucket","posting"}}."""
    _, postings, _ = load_run(RUN, ROOT)
    by_key = {_key(p["board"], p["id"]): p for p in postings}
    manifest = json.loads((AUDIT / "draw_manifest.json").read_text())
    items = {}
    for group in manifest["groups"].values():
        for e in group:
            k = _key(e["board"], e["id"])
            it = items.setdefault(k, {"board": e["board"], "id": e["id"], "title": e["title"],
                                      "audit_labels": [], "posting": by_key[k]})
            it["audit_labels"].append(e["label"])
    for it in items.values():
        it["filter_bucket"] = flt.classify(it["posting"])["bucket"]
    return items


def split(items):
    strata = {}
    for k, it in items.items():
        strata.setdefault(it["filter_bucket"], []).append(k)
    dev, heldout = [], []
    for bucket in sorted(strata):
        keys = sorted(strata[bucket])
        random.Random(SPLIT_SEED).shuffle(keys)
        n_dev = round(DEV_FRACTION * len(keys))
        dev += keys[:n_dev]
        heldout += keys[n_dev:]
    return dev, heldout


def load_split():
    s = json.loads((OUT / "split.json").read_text())
    return ([_key(x["board"], x["id"]) for x in s["dev"]], [_key(x["board"], x["id"]) for x in s["heldout"]])


def _all_labels():
    manifest = json.loads((AUDIT / "draw_manifest.json").read_text())
    lab2key = {e["label"]: _key(e["board"], e["id"]) for g in manifest["groups"].values() for e in g}
    out = {}
    for f in DRAFTS:
        for lab, verdict, reason in _LABEL_RE.findall((AUDIT / f).read_text()):
            k = lab2key[lab]
            if k in out and out[k]["label"] != verdict:
                raise ValueError(f"conflicting labels for {k}: {out[k]} vs {lab} {verdict}")
            out.setdefault(k, {"label": verdict, "reason": reason, "audit_label": lab})
    return out


def labels(which):
    """Hand labels for one split. 'heldout' requires JS3_FINAL_HELDOUT=1 and
    is logged."""
    dev, heldout = load_split()
    if which == "dev":
        keys = dev
    elif which == "heldout":
        if os.environ.get("JS3_FINAL_HELDOUT") != "1":
            raise PermissionError("held-out labels are locked until the final measurement (JS3_FINAL_HELDOUT=1)")
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "heldout_access.log", "a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} held-out labels read "
                    f"by pid {os.getpid()} argv={sys.argv}\n")
        keys = heldout
    else:
        raise ValueError(which)
    allv = _all_labels()
    return {k: allv[k] for k in keys}


def precision(rows, bucket_key):
    kept = [r for r in rows if r[bucket_key] == "relevant"]
    good = sum(r["hand"] == "relevant" for r in kept)
    return {"kept": len(kept), "hand_relevant_among_kept": good,
            "precision": (good / len(kept)) if kept else None}


def measure(which):
    """Same code for dev and held-out. Requires the split's labels (the
    held-out guard applies)."""
    from js3 import filter_v110, rule4
    items = dataset()
    lab = labels(which)
    rows = []
    for k in sorted(lab, key=lambda k: items[k]["audit_labels"][0]):
        it, p = items[k], items[k]["posting"]
        alone = rule4.check(p)
        v110 = filter_v110.classify(p)
        # Full-text diagnostic (EXPERIMENT.md section 4): Palantir only, rule 4
        # alone on descriptionPlain + Lever lists/additionalPlain. Diagnostic,
        # never a bucket. "Vacuous": full text finds a reason or flag that the
        # as-specified run (descriptionPlain only) could not see.
        full = None
        if it["board"] == "palantir":
            fc = rule4.check(dict(p, content=(p["content"] or "") + "\n" + (p.get("lever_extra") or "")))
            seen = set(alone["reasons"]) | {(f["kind"], f["quote"]) for f in alone["eligibility_flags"]}
            extra = [x for x in fc["reasons"] if x not in seen] + \
                    [f for f in fc["eligibility_flags"] if (f["kind"], f["quote"]) not in seen]
            full = {"fires": fc["fires"], "reasons": fc["reasons"], "eligibility_flags": fc["eligibility_flags"],
                    "as_specified_vacuous": bool(extra)}
        rows.append({"audit_labels": it["audit_labels"], "board": it["board"], "id": it["id"],
                     "title": it["title"].strip(), "hand": lab[k]["label"],
                     "v1.0.0": it["filter_bucket"], "v1.1.0-candidate": v110["bucket"],
                     "rule4_alone_fires": alone["fires"], "rule4_reasons": alone["reasons"],
                     "eligibility_flags": alone["eligibility_flags"], "fulltext_palantir": full})
    fired = sum(r["rule4_alone_fires"] for r in rows)
    fired_full = sum((r["fulltext_palantir"] or {"fires": r["rule4_alone_fires"]})["fires"] for r in rows)
    res = {"split": which, "n": len(rows), "rule4_version": filter_v110.VERSION,
           "rule4_alone_fire_rate": {"fired": fired, "of": len(rows)},
           "rule4_alone_fire_rate_fulltext_palantir": {"fired": fired_full, "of": len(rows)},
           "rule4_fires_on_hand_relevant": {
               "as_specified": [r["audit_labels"] for r in rows if r["hand"] == "relevant" and r["rule4_alone_fires"]],
               "fulltext_palantir": [r["audit_labels"] for r in rows if r["hand"] == "relevant"
                                     and (r["fulltext_palantir"] or {"fires": r["rule4_alone_fires"]})["fires"]]},
           "precision_on_relevant": {"v1.0.0": precision(rows, "v1.0.0"),
                                     "v1.1.0-candidate": precision(rows, "v1.1.0-candidate")},
           "hand_relevant": [r for r in rows if r["hand"] == "relevant"],
           "flipped_relevant_to_rejected": [r for r in rows if r["v1.0.0"] == "relevant"
                                            and r["v1.1.0-candidate"] == "rejected"],
           "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{which}_measurement.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    return res


def _fmt_p(x):
    return f"{x['hand_relevant_among_kept']}/{x['kept']}" + ("" if x["precision"] is None else f" = {x['precision']:.3f}") \
        + (" (undefined: nothing kept)" if x["precision"] is None else "")


def print_measurement(res):
    print(f"{res['split'].upper()} ({res['n']} postings), {res['rule4_version']}")
    f = res["rule4_alone_fire_rate"]
    print(f"  rule 4 ALONE (ignoring rules 1-2): fires on {f['fired']} of {f['of']} "
          f"({f['fired'] / f['of']:.1%}) - descriptive, not a precision claim")
    g = res["rule4_alone_fire_rate_fulltext_palantir"]
    print(f"  rule 4 ALONE, full-text diagnostic (Palantir + lists): fires on {g['fired']} of {g['of']} ({g['fired'] / g['of']:.1%})")
    h = res["rule4_fires_on_hand_relevant"]
    print(f"  rule 4 fires on a HAND-RELEVANT posting (false-negative risk): as-specified {h['as_specified'] or 'none'}; "
          f"full-text {h['fulltext_palantir'] or 'none'}")
    print(f"  precision on relevant  v1.0.0: {_fmt_p(res['precision_on_relevant']['v1.0.0'])}   "
          f"v1.1.0-candidate: {_fmt_p(res['precision_on_relevant']['v1.1.0-candidate'])}")
    print("  filter-relevant postings (v1.0.0) and what rule 4 does:")
    for r in res["rows"]:
        if r["v1.0.0"] == "relevant":
            print(f"    {'/'.join(r['audit_labels']):<6} hand={r['hand']:<13} v1.1.0={r['v1.1.0-candidate']:<9} "
                  f"{r['title'][:48]:<48} {'; '.join(x.removeprefix('rule 4: ') for x in r['rule4_reasons']) or '-'}")
    print("  hand-relevant postings, rule 4 alone:")
    for r in res["hand_relevant"]:
        fl = "; ".join(f"{x['kind']}: {x['quote']!r}" for x in r["eligibility_flags"]) or "none"
        vac = r["fulltext_palantir"] and r["fulltext_palantir"]["as_specified_vacuous"]
        print(f"    {'/'.join(r['audit_labels']):<6} v1.0.0={r['v1.0.0']:<9} AS-SPECIFIED rule4 fires={r['rule4_alone_fires']}  "
              f"reasons={r['rule4_reasons'] or '-'}  flags: {fl}" + ("   [VACUOUS: requirement text out of view]" if vac else ""))
        if r["fulltext_palantir"]:
            ft = r["fulltext_palantir"]
            ffl = "; ".join(f"{x['kind']}: {x['quote']!r}" for x in ft["eligibility_flags"]) or "none"
            print(f"    {'':<6} {'':<16} FULL-TEXT    rule4 fires={ft['fires']}  reasons={ft['reasons'] or '-'}  flags: {ffl}")
    print("  rule 4 alone fired on (all rows):")
    for r in res["rows"]:
        if r["rule4_alone_fires"]:
            print(f"    {'/'.join(r['audit_labels']):<9} hand={r['hand']:<13} {r['title'][:55]:<55} "
                  f"{'; '.join(x.removeprefix('rule 4: ') for x in r['rule4_reasons'])}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["measure"] and len(argv) == 2:
        print_measurement(measure(argv[1]))
        return
    if argv != ["split"]:
        raise SystemExit(__doc__)
    items = dataset()
    dev, heldout = split(items)
    OUT.mkdir(parents=True, exist_ok=True)
    row = lambda k: {"board": items[k]["board"], "id": items[k]["id"], "title": items[k]["title"],
                     "audit_labels": items[k]["audit_labels"], "filter_v1.0.0_bucket": items[k]["filter_bucket"]}
    rec = {"rule": "EXPERIMENT.md section 2", "seed": SPLIT_SEED, "dev_fraction": DEV_FRACTION,
           "stratified_by": "filter v1.0.0 bucket (not hand labels)", "distinct_postings": len(items),
           "dev": [row(k) for k in dev], "heldout": [row(k) for k in heldout],
           "note": "membership only - no hand labels in this file"}
    (OUT / "split.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    for name, keys in (("DEV", dev), ("HELD-OUT", heldout)):
        rel = sum(items[k]["filter_bucket"] == "relevant" for k in keys)
        print(f"{name}: {len(keys)} postings (filter-relevant {rel}, filter-rejected {len(keys) - rel})")
        for k in sorted(keys, key=lambda k: items[k]["audit_labels"][0]):
            it = items[k]
            print(f"  {'/'.join(it['audit_labels']):<10} {it['filter_bucket']:<9} [{it['board']}] {it['title'].strip()}")
    print(f"wrote {(OUT / 'split.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
