"""RECORD (rule) vs JUDGMENT (Claude), side by side, for chosen postings.

Default set: the seeded new posting from the seeded run, plus the 6 real
postings the rule marked relevant in the baseline snapshot.

    python3 -m agent.compare
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import judge, rule

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "evidence" / "gitlab_jobs_20261030T201528Z.json"
SEEDED = ROOT / "evidence" / "gitlab_jobs_SEEDED_20261030T201528Z_plus-one-fake-posting.json"
SEEDED_ID = 9999999002


def default_postings(resume):
    seeded = next(j for j in json.loads(SEEDED.read_bytes())["jobs"] if j["id"] == SEEDED_ID)
    real = json.loads(BASELINE.read_bytes())["jobs"]
    relevant = [j for j, r in zip(real, rule.evaluate(real, resume)) if r["verdict"] == "relevant"]
    return [("SEEDED", seeded)] + [("real", j) for j in relevant]


def main():
    try:
        client = judge.get_client()  # before anything else: no key, no run
    except judge.MissingAPIKey as e:
        print(f"STOPPED: {e}", file=sys.stderr)
        return 2

    resume = json.loads((ROOT / "resume.json").read_text())
    now = datetime.now(timezone.utc)
    rows = []
    for source, p in default_postings(resume):
        record = rule.evaluate([p], resume)[0]
        judgment = judge.judge(p, resume, client)
        jv = judgment["verdict"]
        agree = "n/a (judgment unavailable)" if jv is None else ("AGREE" if jv == record["verdict"] else "DISAGREE")
        rows.append({"source": source, "id": p["id"], "title": p["title"].strip(),
                     "record": record, "judgment": judgment, "agreement": agree})
        print(f"\n[{source}] id {p['id']}: {p['title'].strip()}")
        print(f"  RECORD   (rule, recomputable):  {record['verdict']}")
        print(f"           {record['justification']}")
        if jv is None:
            print(f"  JUDGMENT (Claude, opinion):     UNAVAILABLE - {judgment['status']}: {judgment['error']}")
        else:
            print(f"  JUDGMENT (Claude {judgment['served_model']}, opinion):  {jv}")
            print(f"           {judgment['justification']}")
        print(f"  -> {agree}")

    out = ROOT / "logs" / f"compare_{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps({"at": now.isoformat(timespec="seconds"),
                               "prompt_version": judge.PROMPT_VERSION, "rows": rows}, indent=2) + "\n")
    print(f"\nsaved: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
