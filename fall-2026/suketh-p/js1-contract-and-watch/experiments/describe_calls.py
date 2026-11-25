"""Describe saved calls beyond the verdict: which fields each reply cited, how long the
justification was, and what the call cost. No Claude calls; reads calls.jsonl files.

    python3 experiments/describe_calls.py experiments/sampling/calls.jsonl
"""

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONDITION_WORDS = {
    "engineering_role": ("engineer", "focus"),
    "title_seniority": ("senior", "excluded", "seniority", "staff", "manager", "director", "lead"),
    "location": ("location",),
    "skills": ("python", "skill"),
}


def describe(path):
    calls = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    by_posting = defaultdict(list)
    for c in calls:
        by_posting[c["posting_id"]].append(c)
    out = {"file": str(path), "calls": len(calls), "per_posting": {}}
    for posting_id, group in sorted(by_posting.items()):
        valid = [c for c in group if c["valid"]]
        fields = [tuple(sorted({e["field"] for e in c["resume_evidence"] + c["posting_evidence"]})) for c in valid]
        quotes = [tuple(sorted(e["quote"] for e in c["posting_evidence"])) for c in valid]
        words = [len(c["justification"].split()) for c in valid]
        out_tokens = [((c.get("call") or {}).get("usage") or {}).get("output_tokens") for c in group]
        cost = [(c.get("call") or {}).get("total_cost_usd") for c in group]
        mentions = Counter(name for c in valid for name, cues in CONDITION_WORDS.items()
                           if any(cue in c["justification"].lower() for cue in cues))
        out["per_posting"][posting_id] = {
            "title": group[0].get("title"),
            "verdicts": Counter(c["verdict"] if c["valid"] else "rejected" for c in group),
            "distinct_cited_field_sets": len(set(fields)),
            "distinct_posting_quote_sets": len(set(quotes)),
            "evidence_items": [len(c["resume_evidence"]) + len(c["posting_evidence"]) for c in valid],
            "justification_words": words,
            "output_tokens": out_tokens,
            "cost_usd": [round(x, 4) for x in cost if x is not None],
            "replies_naming_each_condition": dict(mentions),
        }
    all_cost = [(c.get("call") or {}).get("total_cost_usd") or 0 for c in calls]
    out["total_cost_usd"] = round(sum(all_cost), 3)
    out["median_output_tokens"] = statistics.median(
        [((c.get("call") or {}).get("usage") or {}).get("output_tokens") or 0 for c in calls])
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(json.dumps(describe(arg), indent=1, default=dict))
