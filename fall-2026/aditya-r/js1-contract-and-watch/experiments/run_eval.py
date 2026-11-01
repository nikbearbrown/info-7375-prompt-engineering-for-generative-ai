"""Run Claude evaluations for the Chapter 1 sampling report and the Chapter 2 prompt experiment.

    python experiments/run_eval.py sampling                      # 5 dev postings x 4 fresh calls, prompt v1
    python experiments/run_eval.py prompt --prompt v1 --split dev
    python experiments/run_eval.py prompt --prompt v2 --split heldout   # refused until prompts are frozen

Every call is a fresh, isolated CLI session (agent/judge.py). Each response is saved with its
validation result. These calls are independent of the watch-run judgments. Transport failures
(CLI error, rate limit, timeout) are retried and recorded; an answer that fails validation is a
result and is never retried. Resumable: postings with a saved transport-ok response are skipped.
"""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import judge  # noqa: E402
from agent.resume import load_resume  # noqa: E402
from agent.validate import validate_judgment  # noqa: E402

SAMPLE = ROOT / "experiments/sample"
FROZEN = ROOT / "prompts/FROZEN.json"
TRANSPORT_RETRIES = 4


def postings(split):
    return {p["id"]: p for p in json.loads((SAMPLE / f"{split}_postings.json").read_text())}


def check_frozen(version):
    if not FROZEN.exists():
        sys.exit("REFUSED: held-out evaluation requires prompts/FROZEN.json (freeze both prompts first)")
    frozen = json.loads(FROZEN.read_text())
    _, sha = judge.load_prompt(version)
    if frozen["prompts"].get(version) != sha:
        sys.exit(f"REFUSED: prompts/judge_{version}.md does not match its frozen hash")


def one(posting, resume, version, out_path, extra):
    if out_path.exists() and json.loads(out_path.read_text()).get("transport_ok"):
        return "skip"
    system, sha = judge.load_prompt(version)
    user = judge.build_user_message(posting, resume)
    tries = []
    for t in range(TRANSPORT_RETRIES + 1):
        rec = judge.call_claude(system, user)
        if rec["transport_ok"]:
            break
        tries.append({k: rec.get(k) for k in ("invoked_at_utc", "returncode", "transport_error", "stderr_tail")}
                     | {"result": (rec.get("cli_json") or {}).get("result")})
        time.sleep(15 * (t + 1))
    ok, errors, parsed = (False, ["transport: no response"], None)
    if rec["transport_ok"]:
        ok, errors, parsed = validate_judgment(rec["response_text"], posting, resume)
    rec.update({"prompt_version": version, "prompt_sha256": sha, "posting_id": posting["id"],
                "valid": ok, "validation_errors": errors,
                "verdict": parsed.get("verdict") if ok else None,
                "transport_failures_before_success": tries, **extra})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    return "ok" if rec["transport_ok"] else "transport-failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sampling", "prompt"])
    ap.add_argument("--prompt", default="v1")
    ap.add_argument("--split", default="dev", choices=["dev", "heldout"])
    ap.add_argument("--repeats", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    resume = load_resume(ROOT / "resume/priya-nair.resume.example.json")
    jobs = []
    if a.mode == "sampling":
        manifest = json.loads((SAMPLE / "manifest.json").read_text())
        dev = postings("dev")
        out = ROOT / "experiments/sampling/raw"
        for pid in manifest["sampling_ids"]:
            for r in range(1, a.repeats + 1):
                jobs.append((dev[pid], "v1", out / f"{pid}_rep{r}.json", {"experiment": "sampling", "repeat": r}))
    else:
        if a.split == "heldout":
            check_frozen(a.prompt)
        out = ROOT / f"experiments/prompt_experiment/raw/{a.prompt}_{a.split}"
        for pid, p in postings(a.split).items():
            jobs.append((p, a.prompt, out / f"{pid}.json", {"experiment": "prompt", "split": a.split}))
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        results = list(pool.map(lambda j: one(j[0], resume, j[1], j[2], j[3]), jobs))
    print({r: results.count(r) for r in set(results)}, "->", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
