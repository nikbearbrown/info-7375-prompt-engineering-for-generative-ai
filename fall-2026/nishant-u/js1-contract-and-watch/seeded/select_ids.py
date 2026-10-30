"""Pick the 3 IDs removed from the seeded state copy; offline, standard library only.

    python3 seeded/select_ids.py [out.json]     # default: seeded/state/seen_ids.json

Candidates are the postings in runs/2026-10-30-1/raw.json that are not among the 20 labeled
ones (experiment/dev_ids.json + experiment/heldout_ids.json). With random.Random(SEED), one is
drawn from those the rule judges relevant and two from the rest, so both verdicts appear.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent import ROOT, rules, watch  # noqa: E402
from agent.resume import load_resume  # noqa: E402

SEED = 20261030
RAW = ROOT / "runs" / "2026-10-30-1" / "raw.json"
OUT = ROOT / "seeded" / "state" / "seen_ids.json"


def main(out=OUT):
    jobs = sorted(watch.parse_jobs(RAW.read_bytes()), key=lambda j: j["id"])
    labeled = set()
    for name in ("dev_ids.json", "heldout_ids.json"):
        labeled |= set(json.loads((ROOT / "experiment" / name).read_text(encoding="utf-8")))
    resume = load_resume(ROOT / "data" / "resume.example.json")
    requirements = json.loads((ROOT / "data" / "requirements.json").read_text(encoding="utf-8"))
    candidates = [j for j in jobs if j["id"] not in labeled]
    verdicts = {j["id"]: rules.evaluate(j, resume, requirements)["verdict"] for j in candidates}
    relevant = [j["id"] for j in candidates if verdicts[j["id"]] == "relevant"]
    other = [j["id"] for j in candidates if verdicts[j["id"]] != "relevant"]
    rng = random.Random(SEED)
    removed = sorted(rng.sample(relevant, 1) + rng.sample(other, 2))
    kept = sorted(j["id"] for j in jobs if j["id"] not in set(removed))
    state = {
        "seeded": True,
        "note": (f"SEEDED copy of the state, not a live change. Built from the {len(jobs)} ids in "
                 f"runs/2026-10-30-1/raw.json minus {removed}, chosen by seeded/select_ids.py with "
                 f"random.Random({SEED}) from postings outside the 20 labeled ones (1 rule-relevant, "
                 "2 not), so that the next replay detects 3 new postings and both judges run."),
        "last_run": "2026-10-30-1",
        "seen_ids": kept,
    }
    watch.write_json_atomic(out, state)
    print(f"seed {SEED}; candidates {len(candidates)} ({len(relevant)} relevant, {len(other)} not); "
          f"removed {removed}; kept {len(kept)}; wrote {Path(out).as_posix()}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
