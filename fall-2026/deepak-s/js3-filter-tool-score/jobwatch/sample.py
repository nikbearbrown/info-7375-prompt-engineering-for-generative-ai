"""`sample`: the same prompt on the same postings, n separate calls each (CONTRACT.md Interfaces, A7, A8, A13, A14).

Every call is its own request with no prior messages. Postings come from the saved raw response
of --run; nothing is fetched. A claude-cli failure stops the command: results.json is written with
"complete": false and the exit code is 1.
"""
import sys
from collections import Counter

from jobwatch.backends import make_judge
from jobwatch.errors import OK, OTHER, REFUSED, Stop
from jobwatch.evidence import SAMPLING_DIR, OutDir, new_stamp_dir, sha256_hex, utc_iso
from jobwatch.inputs import load_resume
from jobwatch.labels import SETS, load_split
from jobwatch.postings import posting_document
from jobwatch.prompt import load_prompt
from jobwatch.saved_run import load_saved_run, postings_for


def sample(args, *, client=None, clock):
    if args.n < 1:
        raise Stop(REFUSED, "--n must be at least 1")
    ids = args.posting_ids
    if len(set(ids)) != len(ids):
        raise Stop(REFUSED, "--posting-id repeats an id")
    resume, resume_raw = load_resume(args.resume)
    prompt = load_prompt(args.prompt)
    saved = load_saved_run(args.run)
    jobs = postings_for(saved, ids)
    split = load_split(required=False)
    if split is not None:
        held = [p for p in ids if p in set(split[SETS["held-out"]])]
        if held:
            raise Stop(REFUSED, f"held-out posting(s) refused before the final held-out run: {', '.join(held)}")
    judge = make_judge(args.judge, client)
    if not judge.available():
        raise Stop(REFUSED, f"sample calls the judge and --judge {judge.name} is not available "
                            f"({judge.unavailable_reason})")

    started = clock()
    created_at = utc_iso(started)
    out = OutDir(new_stamp_dir(SAMPLING_DIR, started))
    calls = []
    for pid in ids:
        doc = posting_document(jobs[pid])
        for k in range(1, args.n + 1):
            if judge.stopped:
                break
            stem = f"{pid}.{k}"
            judgment = judge.call(prompt, args.model, resume, pid, doc, out, clock, stem=stem)
            out.write_json(f"claude/{stem}.validation.json", judgment)
            calls.append({"posting_id": pid, "k": k, **judgment})

    per_posting = {}
    for pid in ids:
        mine = [c for c in calls if c["posting_id"] == pid]
        per_posting[pid] = {
            "status": dict(Counter(c["status"] for c in mine)),
            "verdict": dict(Counter(c["verdict"] for c in mine if c["status"] == "accepted")),
        }
    results = {
        "kind": "sample",
        "created_at": created_at,
        "run_dir": saved.run_dir,
        "run_id": saved.run_id,
        "raw_path": saved.raw_path,
        "raw_sha256": saved.raw_sha256,
        "resume_path": args.resume,
        "resume_sha256": sha256_hex(resume_raw),
        "prompt_path": prompt.path,
        "prompt_sha256": prompt.sha256,
        "model": args.model,
        "judge_backend": judge.name,
        "n": args.n,
        "complete": judge.stopped is None,
        "stopped": judge.stopped,
        "posting_ids": ids,
        "per_posting": per_posting,
        "calls": calls,
    }
    out.write_json("results.json", results)
    print(f"sample: {len(calls)} of {len(ids) * args.n} calls ({len(ids)} postings x {args.n}) "
          f"written to {out.path.as_posix()}/")
    for pid in ids:
        status = per_posting[pid]["status"]
        print(f"  {pid}: " + ", ".join(f"{s} {status.get(s, 0)}" for s in ("accepted", "rejected", "error")))
    if judge.stopped:
        print(f"jobwatch: judge stopped: {judge.stopped['reason']} on posting {judge.stopped['posting_id']}; "
              "no further calls; results.json is incomplete", file=sys.stderr)
        return OTHER
    return OK
