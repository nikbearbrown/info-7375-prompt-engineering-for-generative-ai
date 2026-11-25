"""Measure filter configs against my blind hand verdicts. No network.

    python -m agent.measure_filter --run out/runs/<run> --configs config/filter_v1_0.json ...

For each config, re-scores every posting in the run exactly as agent/run_filter.py does
(same adapters, same score_run), then compares the 48 audited postings with my hand verdicts
(audit/sample_key_DO_NOT_OPEN_UNTIL_JUDGED.json + audit/hand_verdicts.csv).
KEEP = relevant, REJECT = not_relevant, CANNOT TELL = cannot_tell.

Writes (through policy.check_write)
    out/measure/<run>/report.json
    out/measure/<run>/report.md
and prints report.md. "Changed vs v1.0" always compares with FILTER.md v1.0 (config=None),
re-scored in this same pass, whether or not filter_v1_0.json is among --configs.
Hand verdicts are my judgment, not ground truth.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from agent.filter import FILTER_VERSION, resolve_config
from agent.policy import PolicyError, _approved_dir, make_dir, write_atomic
from agent.run_filter import DECISIONS, PROJECT_ROOT, _resolve, load_filter_config, score_run

AUDIT_DIR = "audit"
KEY_FILE = "sample_key_DO_NOT_OPEN_UNTIL_JUDGED.json"
VERDICTS_FILE = "hand_verdicts.csv"
GROUPS = ("random_reject", "close_below_7", "close_above_8", "kept_sample")
VERDICT_FOR = {"KEEP": "relevant", "REJECT": "not_relevant", "CANNOT TELL": "cannot_tell"}
VERDICTS = tuple(VERDICT_FOR.values())


def _check_audit_read(path, root):
    """Reads of the audit inputs only, inside <root>/audit (not in policy.READ_DIRS)."""
    resolved = _resolve(path, root).resolve()
    if not resolved.is_relative_to(_approved_dir(AUDIT_DIR, root)):
        raise PolicyError(f"audit read outside audit/ refused: {path}")
    return resolved


def load_audit(root=PROJECT_ROOT):
    """[{audit_id, group, board, id, title, key_decision, verdict, verdict_reason}] in key order."""
    with open(_check_audit_read(Path(AUDIT_DIR) / KEY_FILE, root), encoding="utf-8") as f:
        key = json.load(f)
    with open(_check_audit_read(Path(AUDIT_DIR) / VERDICTS_FILE, root), encoding="utf-8", newline="") as f:
        verdicts = {row["audit_id"]: row for row in csv.DictReader(f)}

    rows = []
    for k in key:
        v = verdicts.get(k["audit_id"])
        if v is None:
            raise ValueError(f"{k['audit_id']}: in the sample key but not in {VERDICTS_FILE}")
        if v["my_verdict"] not in VERDICTS:
            raise ValueError(f"{k['audit_id']}: unknown verdict {v['my_verdict']!r}")
        if k["group"] not in GROUPS:
            raise ValueError(f"{k['audit_id']}: unknown audit group {k['group']!r}")
        rows.append({
            "audit_id": k["audit_id"], "group": k["group"], "board": k["board"], "id": k["id"],
            "title": k["title"], "key_decision": k["decision"],
            "verdict": v["my_verdict"], "verdict_reason": v.get("reason", ""),
        })
    extra = sorted(set(verdicts) - {k["audit_id"] for k in key})
    if extra:
        raise ValueError(f"in {VERDICTS_FILE} but not in the sample key: {', '.join(extra)}")
    return rows


def _index(records):
    """{(board, str(id)): result}; duplicates would make the join ambiguous, so they raise."""
    out = {}
    for board, p, r in records:
        k = (board, str(p.get("id")))
        if k in out:
            raise ValueError(f"duplicate posting {k} in the run; cannot join audit rows")
        out[k] = r
    return out


def _lookup(index, row):
    r = index.get((row["board"], str(row["id"])))
    if r is None:
        raise ValueError(f"{row['audit_id']} ({row['board']} {row['id']}) not found in the run")
    return r


def measure(run_dir, config_paths, root=PROJECT_ROOT):
    run_dir = _resolve(run_dir, root)
    audit = load_audit(root)

    base_records, _, _ = score_run(run_dir, root, None)
    base = _index(base_records)
    key_mismatch = [
        {"audit_id": a["audit_id"], "key_decision": a["key_decision"],
         "v1_0_now": _lookup(base, a)["decision"]}
        for a in audit if _lookup(base, a)["decision"] != a["key_decision"]
    ]

    configs = []
    for path in config_paths:
        name, overrides = load_filter_config(path, root)
        records, _, _ = score_run(run_dir, root, overrides)
        idx = _index(records)

        rows, agree = [], 0
        dis_by_group = {g: 0 for g in GROUPS}
        n_by_group = Counter(a["group"] for a in audit)
        for a in audit:
            r, old = _lookup(idx, a), _lookup(base, a)
            ok = VERDICT_FOR[r["decision"]] == a["verdict"]
            agree += ok
            if not ok:
                dis_by_group[a["group"]] += 1
            rows.append({
                "audit_id": a["audit_id"], "group": a["group"], "board": a["board"],
                "title": a["title"], "v1_0_decision": old["decision"], "decision": r["decision"],
                "score": r["score"], "verdict": a["verdict"], "agrees": ok,
                "changed_vs_v1_0": r["decision"] != old["decision"],
            })
        counts = Counter(r["decision"] for _, _, r in records)
        configs.append({
            "name": name, "file": str(path), "overrides": overrides,
            "values": resolve_config(overrides),
            "agreement": agree, "audited": len(audit),
            "disagreements_by_group": dis_by_group,
            "audited_by_group": {g: n_by_group[g] for g in GROUPS},
            "changed_vs_v1_0": [x for x in rows if x["changed_vs_v1_0"]],
            "run_decisions": {d: counts[d] for d in DECISIONS},
            "postings_scored": len(records),
            "audited_rows": rows,
        })

    return {
        "run": run_dir.name,
        "filter_version": FILTER_VERSION,
        "verdict_mapping": VERDICT_FOR,
        "audited": len(audit),
        "audit_verdicts": dict(Counter(a["verdict"] for a in audit)),
        "sample_key_vs_v1_0_rescore_mismatches": key_mismatch,
        "note": "Hand verdicts are my judgment, not ground truth. Configs are v1.0 with the "
                "named overrides, not new FILTER.md versions.",
        "configs": configs,
    }


def _md_cell(text):
    return str(text).replace("|", "\\|")


def render_md(report):
    L = [f"# Filter measurement: run {report['run']}", ""]
    L.append(f"FILTER.md v{report['filter_version']}; each config overrides only the keys it names. "
             f"{report['audited']} audited postings, compared with my blind hand verdicts "
             f"({', '.join(f'{k} {v}' for k, v in sorted(report['audit_verdicts'].items()))}). "
             "KEEP = relevant, REJECT = not_relevant, CANNOT TELL = cannot_tell. "
             "Hand verdicts are my judgment, not ground truth.")
    L.append("")
    mm = report["sample_key_vs_v1_0_rescore_mismatches"]
    L.append("Sanity check: v1.0 re-scored now vs the decisions in the sample key: "
             + ("all 48 match." if not mm else
                f"{len(mm)} differ: " + ", ".join(f"{m['audit_id']} {m['key_decision']}->{m['v1_0_now']}" for m in mm)))
    L.append("")

    L.append("## Summary")
    L.append("")
    L.append("| Config | Overrides | Agreement | " + " | ".join(GROUPS) + " | KEEP | REJECT | CANNOT TELL |")
    L.append("|---|---|---:|" + "---:|" * len(GROUPS) + "---:|---:|---:|")
    for c in report["configs"]:
        groups = " | ".join(f"{c['disagreements_by_group'][g]}/{c['audited_by_group'][g]}" for g in GROUPS)
        rd = c["run_decisions"]
        L.append(f"| {c['name']} | `{json.dumps(c['overrides'], sort_keys=True)}` | "
                 f"{c['agreement']}/{c['audited']} | {groups} | "
                 f"{rd['KEEP']} | {rd['REJECT']} | {rd['CANNOT TELL']} |")
    L.append("")
    L.append("Group columns are disagreements / audited postings in that group. "
             f"KEEP / REJECT / CANNOT TELL are over all {report['configs'][0]['postings_scored'] if report['configs'] else 0} postings in the run.")
    L.append("")

    for c in report["configs"]:
        L.append(f"## {c['name']}")
        L.append("")
        L.append(f"File `{c['file']}`; values used: `{json.dumps(c['values'])}`.")
        L.append("")
        L.append(f"Agreement with my verdicts: **{c['agreement']}/{c['audited']}**.")
        L.append("")
        ch = c["changed_vs_v1_0"]
        if not ch:
            L.append("No audited posting changes decision from v1.0.")
        else:
            L.append(f"{len(ch)} audited posting(s) change decision from v1.0:")
            L.append("")
            L.append("| Audit id | Group | Title | v1.0 | This config | My verdict | Agrees now? |")
            L.append("|---|---|---|---|---|---|---|")
            for x in ch:
                L.append(f"| {x['audit_id']} | {x['group']} | {_md_cell(x['title'])} | "
                         f"{x['v1_0_decision']} | {x['decision']} | {x['verdict']} | "
                         f"{'yes' if x['agrees'] else 'no'} |")
        L.append("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, help="out/runs/<run folder>")
    ap.add_argument("--configs", required=True, nargs="+", metavar="PATH",
                    help="config JSON files, e.g. config/filter_v1_0.json")
    args = ap.parse_args(argv)
    root = PROJECT_ROOT
    try:
        report = measure(args.run, args.configs, root)
        md = render_md(report)
        out = make_dir(Path(root) / "out" / "measure" / report["run"], root)
        write_atomic(out / "report.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n", root)
        write_atomic(out / "report.md", md + "\n", root)
    except (PolicyError, OSError, ValueError, KeyError) as e:
        print(json.dumps({"status": "error", "reason": f"{type(e).__name__}: {e}"}, indent=2))
        return 2
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
