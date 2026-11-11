"""Record what JS1's R-v2 decided, so JS2's R-v2a can be held to it.

Run once, on a machine that has the JS1 folder as a sibling. It imports JS1's
own `jobagent.rule` — the committed R-v2 — judges the 163 real Greenhouse
postings JS1 captured live on 2026-10-31, and writes the verdicts to
`evidence/fixtures/js1-rv2-verdicts.json`.

Why a fixture and not an import at test time: the JS2 folder has to run from a
fresh clone of itself, with no sibling. The fixture is the baseline, its
provenance is this file, and `tests/test_rule_carried_over.py` is what holds
R-v2a to it.

    python3 tools/make_rv2_baseline.py ../js1-contract-and-watch
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evidence" / "fixtures" / "js1-greenhouse-reddit-20261031.json"
OUT = ROOT / "evidence" / "fixtures" / "js1-rv2-verdicts.json"


def main(argv) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    js1 = Path(argv[1]).resolve()
    sys.path.insert(0, str(js1))
    from jobagent import resume as js1_resume  # noqa: E402
    from jobagent import rule as js1_rule  # noqa: E402

    resume = js1_resume.load(js1 / "data" / "resume.persona.json")
    raw = FIXTURE.read_bytes()
    jobs = json.loads(raw)["jobs"]

    verdicts = {}
    for job in jobs:
        v = js1_rule.judge(job, resume)
        verdicts[str(job["id"])] = {
            "title": job.get("title"),
            "verdict": v["verdict"],
            "gate_failed": v["gate_failed"],
        }

    OUT.write_text(
        json.dumps(
            {
                "provenance": {
                    "produced_by": "tools/make_rv2_baseline.py",
                    "js1_rule_version": js1_rule.RULE_VERSION,
                    "js1_path": str(js1),
                    "source_response": FIXTURE.name,
                    "source_sha256": hashlib.sha256(raw).hexdigest(),
                    "postings": len(jobs),
                    "note": "The verdicts JS1's committed R-v2 produced for the "
                            "163 postings of its 2026-10-31 live capture. JS2's "
                            "R-v2a must reproduce every one of them.",
                },
                "verdicts": verdicts,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    counts: dict[str, int] = {}
    for v in verdicts.values():
        key = v["gate_failed"] or "relevant"
        counts[key] = counts.get(key, 0) + 1
    print(f"wrote {OUT}: {len(verdicts)} verdicts from {js1_rule.RULE_VERSION}")
    print(f"  {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
