"""Write reports/shortlist.json: the shortlist with every claim and its span.

    python3 tools/make_shortlist.py

Every claim is labelled by `jobfilter.evidence` (E-v1), which abstains unless
a rule in FILTER.md §2 decides it. The prose walk-through is
`reports/shortlist.md`; this file is the machine-readable half, and the two are
generated from the same run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod, evidence, pipeline  # noqa: E402


def main() -> int:
    postings = corpus_mod.load()
    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    decisions = pipeline.run(postings, persona)
    short = [d for d in decisions if d.bucket == pipeline.SHORTLISTED]

    rows = []
    for d in sorted(short, key=lambda x: (-x.score.total, x.posting.identity)):
        claims = evidence.claims_for(d)
        rows.append({
            "identity": d.posting.identity, "board": d.posting.board,
            "title": d.posting.title, "location": d.posting.location,
            "job_family": d.posting.job_family, "url": d.posting.url,
            "score": d.score.total, "per_signal": d.score.per_signal,
            "claims": [c.as_dict() for c in claims],
            "claim_counts": evidence.summarise(claims),
        })

    agg = {k: sum(r["claim_counts"][k] for r in rows)
           for k in ("supported", "contradicted", "insufficient")}
    out = {
        "filter_version": pipeline.FILTER_VERSION,
        "scorer_version": __import__("jobfilter.score", fromlist=["x"]).SCORER_VERSION,
        "evidence_version": evidence.EVIDENCE_VERSION,
        "threshold": __import__("jobfilter.score", fromlist=["x"]).THRESHOLD,
        "generated_from": "../js2-loop-tools-diff/evidence/raw (2026-11-11T00:18Z capture)",
        "claim_totals": agg,
        "shortlist": rows,
    }
    path = ROOT / "reports" / "shortlist.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path}: {len(rows)} entries, claims {agg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
