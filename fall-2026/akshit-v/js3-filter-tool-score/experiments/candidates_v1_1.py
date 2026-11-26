"""Candidate rule changes for FILTER.md v1.1, each one change to v1.0, measured on the 50 AUDIT labels only.

    python -B experiments/candidates_v1_1.py
The 30 held-out labels are not read. For each candidate: agreement with my labels on the audit set,
which audit postings flip and whether toward my label, and how many of all 714 postings change verdict.
Writes out/experiments/candidates_v1_1.json and .md.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import corpus, filter as flt, policy  # noqa: E402
from agent3.stats import fmt_rate  # noqa: E402

V = flt.V1_0
T5_DATA = ["streaming data", "data streaming", "streaming pipeline", "streaming pipelines", "streaming ingestion",
           "batch and streaming", "streaming architecture", "streaming architectures", "streaming infrastructure",
           "streaming workloads", "streaming systems", "stream processing", "real-time streaming"]
T4_DATA = ["orchestration tool", "orchestration tools", "workflow orchestration", "data orchestration",
           "pipeline orchestration", "orchestration framework", "orchestration frameworks"]
CANDIDATES = {
    "C1 cut title-level disqualifiers": (
        "Cut Staff, Principal, Director, Manager, Head of from F2 (keep Intern, PhD, Contract, Temporary).",
        "My 2026-11-25 definition: title level doesn't count against a posting.",
        {**V, "disqualify_title": ["Intern", "PhD", "Contract", "Temporary"]}),
    "C2 punctuation inside phrases": (
        "Let any punctuation sit between a phrase's words ('data-quality', 'Data & Integration').",
        "The gap found by the second-method recompute on 2026-11-24.",
        {**V, "phrase_gap": "punctuation"}),
    "C3 streaming means data streaming": (
        "T5 counts only data-streaming phrases (" + ", ".join(T5_DATA[:4]) + ", ...), not bare 'streaming'.",
        "False friend: 9 of 10 Spotify 'streaming' matches are music/audio streaming.",
        {**V, "topic_groups": {**V["topic_groups"], "T5 streaming": T5_DATA}}),
    "C4 orchestration means workflow orchestration": (
        "T4 counts only " + ", ".join(T4_DATA[:5]) + ", ..., not bare 'orchestration'.",
        "False friend: 'program orchestration', 'resource orchestration', 'compute orchestration'.",
        {**V, "topic_groups": {**V["topic_groups"], "T4 orchestration": T4_DATA}}),
}
AUDIT = ("audit_reject_random", "audit_close", "audit_kept_random")


def agree(ids, labels, ps, cfg):
    return sum((flt.apply(ps[i], cfg)["verdict"] == "keep") == (labels[i] == "relevant") for i in ids)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sample = json.loads((policy.OUT / "audit" / "sample_v1.0.json").read_text(encoding="utf-8"))
    with (ROOT / "labels" / "hand_labels.csv").open(encoding="utf-8", newline="") as f:
        labels = {r["id"]: r["hand_label"] for r in csv.DictReader(f)}
    ids = [i for s in AUDIT for i in sample["sets"][s]]
    ps = corpus.load()["postings"]
    base = agree(ids, labels, ps, V)
    base_all = {i: flt.apply(p, V)["verdict"] for i, p in ps.items()}
    lines = ["# Candidate rules for v1.1, measured on the 50 audit labels (held-out not read)", "",
             f"v1.0 agrees with my labels on {fmt_rate(base, len(ids))}.", ""]
    rec = {"v1.0_agree": base, "n": len(ids), "candidates": {}}
    for name, (what, why, cfg) in CANDIDATES.items():
        a = agree(ids, labels, ps, {**cfg, "version": name})
        flips = []
        for i in ids:
            v0, v1 = flt.apply(ps[i], V)["verdict"], flt.apply(ps[i], cfg)["verdict"]
            if v0 != v1:
                toward = (v1 == "keep") == (labels[i] == "relevant")
                flips.append({"id": i, "title": ps[i]["title"], "from": v0, "to": v1, "my_label": labels[i],
                              "toward_my_label": toward})
        all_changed = sum(flt.apply(p, cfg)["verdict"] != base_all[i] for i, p in ps.items())
        kept_all = sum(flt.apply(p, cfg)["verdict"] == "keep" for p in ps.values())
        rec["candidates"][name] = {"what": what, "why": why, "agree": a, "flips": flips,
                                   "corpus_changed": all_changed, "corpus_kept": kept_all}
        lines += [f"## {name}", f"- change: {what}", f"- why: {why}",
                  f"- audit agreement: {base} → **{a}** of {len(ids)} ({a - base:+d})",
                  f"- audit flips: {len(flips)} ({sum(f['toward_my_label'] for f in flips)} toward my label)",
                  f"- whole corpus: {all_changed} of {len(ps)} postings change verdict; kept would be {kept_all} (v1.0: 25)"]
        for f_ in flips:
            lines.append(f"  - {'toward' if f_['toward_my_label'] else 'AWAY from'} my label: {f_['title']} "
                         f"({f_['from']} → {f_['to']}; my label {f_['my_label']})")
        lines.append("")
    policy.write_bytes(policy.OUT / "experiments" / "candidates_v1_1.json", (json.dumps(rec, indent=1) + "\n").encode())
    policy.write_bytes(policy.OUT / "experiments" / "candidates_v1_1.md", ("\n".join(lines) + "\n").encode("utf-8"))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
