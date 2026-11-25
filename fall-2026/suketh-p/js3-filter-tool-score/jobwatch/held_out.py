"""The one held-out comparison (Chapter 9), scored the way the student chose before it ran.

FILTER.md, "After the reject audit, before any held-out label was scored":
  * Can't tell rows are left out. The filter passes the first part of the bar when at least 90%
    of the held-out rows labeled Yes or No match its decision ("Leave out, scale to 90%").
  * It fails if it rejects more than one held-out posting labeled Yes.
  * It fails if it clears even one unmet requirement. For the filter, Claude Code's mechanical
    reading, fixed before the run: a row the filter keeps or holds for review, labeled No, whose
    reason states a number of years without "preferred", or names a minimum, a requirement, a
    clearance, new graduates or entry-level applicants.
  * "My checks catch every deliberate failure" is the test suite
    (tests/test_js3_wrong_versions_caught.py); this module does not score it.

claim_the_single_run() refuses a second run into a folder that already holds results: the
held-out set is measured once."""

import re
from pathlib import Path

from jobwatch import measure, sample

PASS = (9, 10)                 # at least 9/10 of the decided rows
MAX_FALSE_EXCLUSIONS = 1
RESULTS = "held-out.jsonl"
_YEARS = re.compile(r"\b(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
                    r"\s*\+?\s*(?:-\s*)?(?:or more\s+)?years?\b", re.I)
_REQUIREMENT_WORDS = ("minimum", "require", "clearance", "new graduate", "entry-level", "entry level")
CHECKS = ("at least 90% of the Yes and No rows match", "no more than one Yes rejected", "no unmet requirement cleared")


class AlreadyMeasured(Exception):
    pass


def names_an_unmet_requirement(reason):
    text = reason.lower()
    if _YEARS.search(text) and "preferred" not in text:
        return True
    return any(word in text for word in _REQUIREMENT_WORDS)


def rows(members, labels, records):
    """measure.compare rows for the two held-out groups only, with label ID, group and reason."""
    out = []
    for m in sample.held_out(members):
        key = (m["board"], m["key"])
        row = measure.compare({key: labels[m["label_id"]]["label"]}, {key: records[key]})[0]
        out.append({"label_id": m["label_id"], "stratum": m["stratum"], **row, "reason": labels[m["label_id"]]["reason"]})
    return out


def score(rows):
    decided = [r for r in rows if r["label"] in ("yes", "no")]
    matches = [r for r in decided if (r["label"] == "yes") == (r["decision"] == "reaches")]
    false_exclusions = [r for r in decided if r["label"] == "yes" and r["decision"] == "rejected"]
    false_inclusions = [r for r in decided if r["label"] == "no" and r["decision"] == "reaches"]
    cleared = [r for r in false_inclusions if names_an_unmet_requirement(r["reason"])]
    checks = dict(zip(CHECKS, (bool(decided) and PASS[1] * len(matches) >= PASS[0] * len(decided),
                               len(false_exclusions) <= MAX_FALSE_EXCLUSIONS,
                               not cleared)))
    return {"labelled": len(rows), "cannot_tell": len(rows) - len(decided), "decided": len(decided),
            "matches": len(matches), "false_exclusions": false_exclusions, "false_inclusions": false_inclusions,
            "unmet_requirements_cleared": cleared, "checks": checks, "passed": all(checks.values())}


def claim_the_single_run(out_dir):
    out = Path(out_dir)
    if (out / RESULTS).exists():
        raise AlreadyMeasured(f"{out / RESULTS} exists: the held-out set is measured once")
    out.mkdir(parents=True, exist_ok=True)
    return out
