"""Persistence is not training: send JS1's exact prompts again, weeks later, and compare.

JS1 (../js1-contract-and-watch, submitted at 72141da) saved, for every Claude call on Oct 31, the
prompt's SHA-256. This script rebuilds those prompts with JS1's own unchanged code (run with JS1's
own virtualenv, reading only), checks each rebuilt prompt hashes to the recorded value, and sends
the prompt-v2 ones again through the same `claude -p` call (jsagent.claude_judge.call_claude is
identical in JS1 and here). Output: experiments/P-rerun.jsonl. Nothing in the JS1 folder is written.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS1 = ROOT.parent / "js1-contract-and-watch"
sys.path.insert(0, str(ROOT))
from jsagent import claude_judge  # noqa: E402

DUMP = r"""
import json, sys, gzip, hashlib
sys.path.insert(0, '.')
from jsagent import claude_judge, resume as R
jobs = {j['id']: j for j in json.loads(gzip.decompress(open('runs/2026-10-31T144337/raw.json.gz', 'rb').read()))['jobs']}
res = R.load('persona/priya-nair.resume.json')
out = []
for f in ('experiment/results_dev.jsonl', 'experiment/results_heldout.jsonl'):
    for line in open(f):
        r = json.loads(line)
        if r['prompt_version'] != 'v2':
            continue
        p = claude_judge.build_prompt('v2', jobs[r['posting_id']], res)
        out.append({'posting_id': r['posting_id'], 'set': f.split('_')[1].split('.')[0], 'prompt': p,
                    'sha_rebuilt': hashlib.sha256(p.encode()).hexdigest(), 'sha_oct31': r['prompt_sha256'],
                    'oct31_started_at': r['started_at'], 'oct31_models_used': r['models_used'],
                    'oct31_verdict': (r.get('judgment') or {}).get('verdict')})
print(json.dumps(out))
"""


def main() -> int:
    dumped = json.loads(subprocess.run([str(JS1 / ".venv" / "bin" / "python"), "-c", DUMP], cwd=JS1,
                                       capture_output=True, text=True, check=True).stdout)
    mismatched = [d["posting_id"] for d in dumped if d["sha_rebuilt"] != d["sha_oct31"]]
    if mismatched:
        raise SystemExit(f"rebuilt prompts differ from Oct 31 for {mismatched}; not a like-for-like rerun")

    def one(d):
        call = claude_judge.call_claude(d["prompt"], claude_judge.MODEL)
        parsed, errors = claude_judge.validate(call["result"]) if not call["is_error"] else (None, ["call failed"])
        rec = {k: v for k, v in d.items() if k != "prompt"}
        rec.update(today_started_at=call["started_at"], today_models_used=call["models_used"],
                   today_valid=parsed is not None, today_errors=errors,
                   today_verdict=parsed["verdict"] if parsed else None,
                   today_confidence=parsed["confidence"] if parsed else None)
        return rec

    with ThreadPoolExecutor(max_workers=4) as pool, open(ROOT / "experiments" / "P-rerun.jsonl", "x") as f:
        recs = list(pool.map(one, dumped))
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    same = sum(1 for r in recs if r["today_verdict"] == r["oct31_verdict"])
    print(f"{len(recs)} identical prompts (sha256 match); same verdict as Oct 31: {same}/{len(recs)}")
    for r in recs:
        if r["today_verdict"] != r["oct31_verdict"]:
            print("  changed:", r["posting_id"], r["oct31_verdict"], "->", r["today_verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
