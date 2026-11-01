"""Offline re-check of the saved evidence. Needs no network and no Claude calls.

    .venv/bin/python scripts/verify_evidence.py

Recomputes the new-id set, every RECORD, and re-validates every saved Claude response against
the posting it was requested for. Prints PASS/FAIL per check; exits nonzero on any FAIL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.board import decode_body, parse_jobs  # noqa: E402
from agent.judge import load_prompt  # noqa: E402
from agent.resume import load_resume  # noqa: E402
from agent.rules import evaluate  # noqa: E402
from agent.validate import validate_judgment  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        failures.append(name)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    resume = load_resume(ROOT / "resume/priya-nair.resume.example.json")
    snaps = ROOT / "evidence/snapshots"
    for meta_path in sorted(snaps.glob("*.meta.json")):
        meta = json.loads(meta_path.read_text())
        data = next(p for p in snaps.glob(meta_path.name.replace(".meta.json", ".json*")) if not p.name.endswith(".headers.txt"))
        want = meta.get("sha256") or meta.get("sha256_of_saved_gzip_bytes")
        check(f"snapshot hash {data.name}", sha(data) == want)

    runs = sorted(p for p in (ROOT / "evidence/runs").iterdir() if p.is_dir())
    base_dir = next(p for p in runs if "seeded-baseline" in p.name)
    live_dir = next(p for p in runs if p.name.endswith("_live"))
    base_raw = next(base_dir.glob("raw_response.json*"))
    archive = snaps / "databricks_20260922T181913Z_wayback.json.gz"
    check("baseline raw response is byte-identical to the archived capture", sha(base_raw) == sha(archive))
    base_ids = {j["id"] for j in parse_jobs(decode_body(base_raw.read_bytes()))}
    base_state = json.loads((base_dir / "state_after_run.json").read_text())
    check("baseline state records exactly the archived ids, all 'baseline'",
          set(map(int, base_state["ids"])) == base_ids and set(base_state["ids"].values()) == {"baseline"},
          f"{len(base_ids)} ids")
    base_rep = json.loads((base_dir / "report.json").read_text())
    check("baseline reported zero new postings", base_rep["new_postings"] == [] and base_rep["run"]["new"] == 0)

    live_meta = json.loads((live_dir / "raw_response.meta.json").read_text())
    live_raw = live_dir / "raw_response.json"
    check("live raw response hash matches its metadata", sha(live_raw) == live_meta["sha256"])
    check("live response came from the allow-listed host",
          live_meta["final_url"].startswith("https://boards-api.greenhouse.io/"))
    live_jobs = {j["id"]: j for j in parse_jobs(decode_body(live_raw.read_bytes()))}
    expected_new = set(live_jobs) - base_ids
    rep = json.loads((live_dir / "report.json").read_text())
    reported = {o["posting_id"] for o in rep["new_postings"]}
    check("run 2 reported exactly the ids absent from the baseline", reported == expected_new,
          f"{len(expected_new)} new")
    check("no posting reported twice", len(reported) == len(rep["new_postings"]))

    rec_ok = judg_ok = 0
    for o in rep["new_postings"]:
        posting = live_jobs[o["posting_id"]]
        rec_ok += evaluate(posting, resume)["verdict"] == o["RECORD"]["verdict"]
        attempt = live_dir / "judgments" / o["JUDGMENT"]["attempt_files"][-1]
        a = json.loads(attempt.read_text())
        ok, _, parsed = validate_judgment(a["response_text"], posting, resume)
        judg_ok += ok and parsed["verdict"] == o["JUDGMENT"]["verdict"] and a["posting_id_requested"] == o["posting_id"]
    n = len(rep["new_postings"])
    check("every RECORD recomputes identically", rec_ok == n, f"{rec_ok}/{n}")
    check("every reported JUDGMENT re-validates against its own posting", judg_ok == n, f"{judg_ok}/{n}")
    state = json.loads((ROOT / "state/seen.json").read_text())
    check("final state: baseline ids + completed new ids, nothing pending",
          {int(k) for k, v in state["ids"].items() if v == "completed"} == expected_new
          and "pending" not in state["ids"].values())

    frozen = json.loads((ROOT / "prompts/FROZEN.json").read_text())
    for v in ("v1", "v2"):
        check(f"prompt {v} unchanged since freeze", load_prompt(v)[1] == frozen["prompts"][v])
    for raw_dir in sorted((ROOT / "experiments").glob("**/raw")):
        files = list(raw_dir.rglob("*.json"))
        good = 0
        for f in files:
            x = json.loads(f.read_text())
            split = "heldout" if "heldout" in f.parent.name else "dev"
            posting = {p["id"]: p for p in json.loads((ROOT / f"experiments/sample/{split}_postings.json").read_text())}[x["posting_id"]]
            ok, _, _ = validate_judgment(x["response_text"] or "", posting, resume)
            good += ok == x["valid"] and x["prompt_sha256"] == frozen["prompts"][x["prompt_version"]]
        check(f"experiment records re-validate with the recorded outcome and frozen prompt hash: {raw_dir.relative_to(ROOT)}",
              good == len(files), f"{good}/{len(files)}")

    print("\nALL CHECKS PASSED" if not failures else f"\n{len(failures)} CHECK(S) FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
