"""The rest of the js3 command line (see js3/__main__.py)."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent


def dispatch(cmd, rest):
    if cmd == "draw":
        from js3 import audit
        records = audit.load_records()
        sample = audit.draw(records)
        sample["drawn_from"] = {"file": "results/filter-v1/records.jsonl",
                                "sha256": audit.file_sha256(HERE / "results" / "filter-v1" / "records.jsonl")}
        out = HERE / "labels" / "sample.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(sample, indent=1) + "\n")
        print(f"wrote {out.relative_to(HERE)}: {sample['items']} postings to label, seed {sample['seed']}")
        print(json.dumps({"held_out": {k: len(v) for k, v in sample["held_out"].items()},
                          "audit": {k: len(v) for k, v in sample["audit"].items()},
                          "closest_calls_not_labeled": len(sample["closest_calls_not_labeled"])}))
        return 0
    if cmd == "label":
        from js3 import label
        return label.main(rest)
    if cmd == "audit":
        from js3 import audit_report
        return audit_report.main(rest)
    if cmd == "shortlist":
        from js3 import shortlist
        return shortlist.main(rest)
    if cmd == "serve":
        from js3 import mcp_server
        return mcp_server.main(rest)
    raise SystemExit(f"unknown command {cmd}")
