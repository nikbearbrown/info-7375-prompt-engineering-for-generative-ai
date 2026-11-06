"""Compare the rule verdict and Claude's judgment in a run report, side by side.

One line per record (posting_id, rule verdict, judgment (Claude), and the
rejection reasons when Claude's reply was rejected), then totals. The two
verdicts are never merged into one score (CONTRACT.md §6). Read-only.

Usage:
    python3.13 tools/compare_verdicts.py <run_report.json>
"""

import argparse
import json
import sys

CLAUDE_LABEL = "judgment (Claude)"


def compare(report):
    """(output lines, totals dict) for a run report's new_postings."""
    records = report.get("new_postings") if isinstance(report, dict) else None
    if not isinstance(records, list):
        raise ValueError("not a run report: no 'new_postings' list")
    totals = {"agree": 0, "disagree": 0, "rejected": 0}
    lines = []
    for record in records:
        rule, claude = record["rule_verdict"], record["claude_verdict"]
        line = f"{record['posting_id']}  rule: {rule}  {CLAUDE_LABEL}: {claude}"
        if claude == "rejected":
            totals["rejected"] += 1
            lines.append(line)
            reasons = (record.get("claude_justification") or {}).get("reasons") or ["(no reasons recorded)"]
            lines.extend(f"    - {reason}" for reason in reasons)
        elif claude == rule:
            totals["agree"] += 1
            lines.append(f"{line}  agree")
        else:
            totals["disagree"] += 1
            lines.append(f"{line}  DISAGREE")
    lines.append(f"records: {len(records)}  agree: {totals['agree']}  "
                 f"disagree: {totals['disagree']}  rejected: {totals['rejected']}")
    return lines, totals


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 tools/compare_verdicts.py",
                                     description="Rule verdict vs judgment (Claude), one line per record.")
    parser.add_argument("report")
    args = parser.parse_args(argv)
    try:
        with open(args.report, encoding="utf-8") as fh:
            lines, _ = compare(json.load(fh))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: cannot compare {args.report}: {exc}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
