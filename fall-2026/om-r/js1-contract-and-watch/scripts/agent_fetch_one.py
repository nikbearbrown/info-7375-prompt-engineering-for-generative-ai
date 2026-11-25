"""Action-Surface Comparison (Chapter 3), surface 3: AGENT-FETCH.

The built agent's own code path, for one posting, with no human in the
loop between fetch and verdict:
  1. watch.run: allow-listed live fetch of the GitLab board, raw response
     saved as evidence, its own state file written atomically.
  2. Pick posting 8730125002 out of that live response. (The agent normally
     judges only NEW postings; selecting one id is the one deviation, so
     the three surfaces judge the same posting.)
  3. rule.evaluate (RECORD) and judge.judge with judge-dev-v0 (JUDGMENT),
     the same question used for the paste and file-read surfaces.

Uses state/action_surface_seen.json, NOT the live watch state, so the
real baseline in state/gitlab_seen.json is untouched.

    python3 scripts/agent_fetch_one.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import judge, rule, watch  # noqa: E402

POSTING_ID = 8730125002
PROMPT = "judge-dev-v0"
STATE = ROOT / "state" / "action_surface_seen.json"
OUT_DIR = ROOT / "logs" / "action_surface"


def main():
    try:
        client = judge.get_client()  # no key: stop before any network call
    except judge.MissingAPIKey as e:
        print(f"STOPPED: {e}", file=sys.stderr)
        return 2

    resume = watch.validate_resume(json.loads((ROOT / "resume.json").read_text()))
    now = datetime.now(timezone.utc)
    report = watch.run("gitlab", resume, STATE, ROOT / "evidence")  # live, allow-listed
    jobs = {j["id"]: j for j in json.loads(Path(report["evidence_file"]).read_bytes())["jobs"]}

    out = {"surface": "agent-fetch", "at": now.isoformat(timespec="seconds"),
           "posting_id": POSTING_ID, "prompt_version": PROMPT,
           "evidence_file": str(Path(report["evidence_file"]).relative_to(ROOT)),
           "state_file": str(STATE.relative_to(ROOT)),
           "watch_baseline": report["baseline"],
           "postings_in_live_response": report["postings_in_response"]}
    if POSTING_ID not in jobs:
        out["result"] = f"posting {POSTING_ID} is no longer on the live board; nothing judged"
    else:
        p = jobs[POSTING_ID]
        out["record"] = rule.evaluate([p], resume)[0]
        out["judgment"] = judge.judge(p, resume, client, prompt_version=PROMPT)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"agent_fetch_{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    print(f"[{out['at']}] AGENT-FETCH, posting {POSTING_ID}, prompt {PROMPT}")
    print(f"  live fetch: {report['source']}  ({out['postings_in_live_response']} postings)")
    print(f"  evidence:   {out['evidence_file']}\n  state:      {out['state_file']}")
    if "judgment" in out:
        j = out["judgment"]
        print(f"  RECORD   (rule):    {out['record']['verdict']}")
        print(f"  JUDGMENT (Claude):  {j['verdict'] or 'UNAVAILABLE - ' + j['status']}  "
              f"({j['served_model']})\n    {j['justification'] or j['error']}")
    else:
        print(f"  {out['result']}")
    print(f"  saved: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
