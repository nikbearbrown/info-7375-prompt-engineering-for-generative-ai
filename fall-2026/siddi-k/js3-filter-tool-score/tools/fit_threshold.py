"""Fit one number on labels (brief Step 2.4): keep_threshold, fitted on the AUDIT labels only (development data),
then tested once on the held-out set H. Rule: fewest disagreements with Siddi on audit postings that reached scoring;
ties go to the hand-set value 4, then to the higher threshold. Writes output/experiments/fitted_threshold.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_heldout  # noqa: E402
from experiments import hand_labels  # noqa: E402
from js3 import collect, policy  # noqa: E402
from js3 import filter as flt  # noqa: E402

RUN = "2026-11-26T02-59-56Z"


def errors(cfg, items, labels, t):
    c = dict(cfg, keep_threshold=t)
    wrong = []
    for p in items:
        k = f"{p['board']}:{p['id']}"
        kept = flt.evaluate(c, p)["verdict"] == "keep"
        if kept != (labels[k] == "relevant"):
            wrong.append(k)
    return wrong


def main() -> int:
    cfg = json.loads(policy.check_read("config/filter.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads(policy.check_read("labels/sheet-manifest.json").read_text(encoding="utf-8"))
    audit_keys = {it["key"] for it in manifest["items"] if not any(r.startswith("held_out") for r in it["roles"])}
    postings = {f"{p['board']}:{p['id']}": p for p in collect.load_postings(policy.ROOT / "data" / "collections" / RUN)}
    labels = {x["key"]: x["label"] for x in map(json.loads, policy.check_read("labels/hand_labels.jsonl")
                                                .read_text(encoding="utf-8").splitlines()) if x}
    audit = [postings[k] for k in sorted(audit_keys)]
    scored = [p for p in audit if flt.evaluate(cfg, p)["score"] is not None]
    table = {t: errors(cfg, scored, labels, t) for t in range(0, 10)}
    best = min(table, key=lambda t: (len(table[t]), t != 4, -t))
    H = list({f"{p['board']}:{p['id']}": p for p in build_heldout.load()}.values())
    h_labels = hand_labels()
    h_hand_set, h_fitted = errors(cfg, H, h_labels, 4), errors(cfg, H, h_labels, best)
    out = {"fitted_on": f"{len(scored)} audit postings that passed every gate (development labels)",
           "errors_by_threshold": {t: len(v) for t, v in table.items()}, "fitted": best, "hand_set": 4,
           "held_out_errors": {"hand_set_4": len(h_hand_set), f"fitted_{best}": len(h_fitted), "n": len(H)},
           "held_out_postings_reaching_scoring": sum(flt.evaluate(cfg, p)["score"] is not None for p in H)}
    policy.write_bytes("output/experiments/fitted_threshold.json", (json.dumps(out, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
