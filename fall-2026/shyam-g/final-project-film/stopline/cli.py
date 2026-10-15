"""python -m stopline data/incidents.json [--evidence PATH] [--audit-out PATH]

Prints one outcome line and one audit record (JSON) per incident.
"""
import argparse
import json
import sys
from pathlib import Path

from .engine import evaluate_all


def load_json_list(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON list")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stopline", description=__doc__.splitlines()[0])
    parser.add_argument("incidents", help="JSON list of incidents")
    parser.add_argument("--evidence", help="JSON list of evidence records (default: evidence.json beside incidents)")
    parser.add_argument("--audit-out", help="also write audit records as JSON Lines to this path")
    args = parser.parse_args(argv)

    incidents_path = Path(args.incidents)
    evidence_path = Path(args.evidence) if args.evidence else incidents_path.with_name("evidence.json")
    records, evidence_errors = evaluate_all(load_json_list(incidents_path), load_json_list(evidence_path))

    for err in evidence_errors:
        print(f"WARNING evidence ignored: {err}", file=sys.stderr)
    for record in records:
        print(f"{record['incident_id']}  {record['outcome']}  (decided by: {', '.join(record['decided_by']) or 'all checks passed'})")
        print(json.dumps(record, sort_keys=True))
    if args.audit_out:
        with open(args.audit_out, "w", encoding="utf-8", newline="\n") as fh:
            for record in records:
                fh.write(json.dumps(record, sort_keys=True) + "\n")
    return 0
