"""`experiment`: score prompts, and the rule as a baseline, against the hand labels of one set.

CONTRACT.md Interfaces › experiment, with Amendments A7 (--run), A8 (output, held-out refusals),
A10 (--prompt-b optional on development), A11 (development reuses saved results), A12 (counts) and
A14 (judge backends; a claude-cli failure stops the command and leaves results.json with
"complete": false, which a later identical command resumes) and A15 (a held-out resume never sends
a posting that already has a saved call).
"""
import json
import math
import subprocess
import sys
from statistics import NormalDist

from jobwatch.backends import make_judge
from jobwatch.errors import BAD_RULE_VERDICT, OK, OTHER, REFUSED, Stop
from jobwatch.evidence import EXPERIMENTS_DIR, OutDir, atomic_write, json_bytes, sha256_hex, utc_iso, utc_stamp
from jobwatch.inputs import load_resume
from jobwatch.judge import _judgment
from jobwatch.labels import SETS, load_hand_labels, load_split
from jobwatch.postings import posting_document
from jobwatch.prompt import load_prompt
from jobwatch.rule import apply_rule
from jobwatch.saved_run import load_saved_run, postings_for
from jobwatch.validator import Invalid, check_verdict

OUTCOMES = ("accepted_correct", "accepted_wrong", "rejected", "error")
Z95 = NormalDist().inv_cdf(0.975)


def wilson(k, n, z=Z95):
    """The 95% Wilson score interval for k successes in n trials."""
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, centre - half), min(1.0, centre + half)]


def outcome(status, verdict, hand_label):
    if status == "accepted":
        return "accepted_correct" if verdict == hand_label else "accepted_wrong"
    return "rejected" if status == "rejected" else "error"


def score(outcomes):
    n = len(outcomes)
    counts = {o: outcomes.count(o) for o in OUTCOMES}
    return {"n": n, "counts": counts, "pass_rate": counts["accepted_correct"] / n,
            "wilson_95": wilson(counts["accepted_correct"], n)}


def _git(*argv):
    return subprocess.run(["git", *argv], capture_output=True, text=True)


def check_committed(prompt_paths):
    """held-out refuses if prompts/ or a prompt file is untracked or has uncommitted changes (A8)."""
    status = _git("status", "--porcelain", "--", "prompts/", *prompt_paths)
    if status.returncode != 0:
        raise Stop(REFUSED, "held-out refused: git status could not check prompts/ for uncommitted changes")
    if status.stdout.strip():
        raise Stop(REFUSED, "held-out refused: prompts/ or a prompt file has uncommitted changes")
    for path in prompt_paths:
        if _git("ls-files", "--error-unmatch", "--", path).returncode != 0:
            raise Stop(REFUSED, f"held-out refused: {path} is not committed")


def _provenance(saved, resume_path, resume_sha, model, ids, backend):
    return {"run_dir": saved.run_dir, "run_id": saved.run_id, "raw_path": saved.raw_path,
            "raw_sha256": saved.raw_sha256, "resume_path": resume_path, "resume_sha256": resume_sha,
            "model": model, "judge_backend": backend, "posting_ids": ids}


def _previous(target, prompt, provenance, held_out, prompt_shas):
    """The saved results.json of an existing target, if it was made from the same inputs (A11, A14)."""
    try:
        previous = json.loads((target / "results.json").read_bytes())
    except (OSError, ValueError):
        raise Stop(REFUSED, f"{target.as_posix()} exists but has no readable results.json; it cannot be "
                            "reused or resumed") from None
    same = previous.get("prompt_sha256") == prompt.sha256 and all(
        previous.get(k, "sdk" if k == "judge_backend" else None) == provenance[k]
        for k in ("raw_sha256", "resume_sha256", "model", "judge_backend", "posting_ids")
    )
    if not same:
        raise Stop(REFUSED, f"{target.as_posix()} was made from a different run, résumé, model, judge or set; "
                            "it cannot be reused")
    if held_out and previous.get("prompt_shas") != prompt_shas:
        raise Stop(REFUSED, f"held-out refused: {target.as_posix()} was run with a different pair of prompts")
    return previous


def _saved(judge, target, pid, resume, doc):
    """The saved judgment for one posting, or None if it has no saved call."""
    raw_path = (target / "claude" / f"{pid}.response.txt").as_posix()
    judgment = judge.saved(target, pid, pid, resume, doc, raw_path)
    if judgment is not None or not (target / "claude" / f"{pid}.validation.json").exists():
        return judgment
    try:
        judgment = json.loads((target / "claude" / f"{pid}.validation.json").read_bytes())
    except (OSError, ValueError):
        return None
    return judgment if isinstance(judgment, dict) and judgment.get("status") == "error" else None


def _set_aside(target, pid, stamp):
    """Before a resumed call, move the posting's earlier files to claude/previous/<stamp>/."""
    old = sorted((target / "claude").glob(f"{pid}.*"))
    if old:
        keep = target / "claude" / "previous" / stamp
        keep.mkdir(parents=True, exist_ok=True)
        for f in old:
            f.rename(keep / f.name)


def experiment(args, *, client=None, clock):
    held_out = args.set == "held-out"
    resume, resume_raw = load_resume(args.resume)
    prompts = [("A", args.prompt_a, load_prompt(args.prompt_a))]
    if args.prompt_b:
        prompts.append(("B", args.prompt_b, load_prompt(args.prompt_b)))
    elif held_out:
        raise Stop(REFUSED, "--set held-out needs both --prompt-a and --prompt-b")
    if len(prompts) == 2 and prompts[0][2].sha256 == prompts[1][2].sha256:
        raise Stop(REFUSED, "--prompt-a and --prompt-b have the same sha256; omit --prompt-b to score one prompt")
    prompt_shas = sorted(p.sha256 for _, _, p in prompts)
    judge = make_judge(args.judge, client)

    saved = load_saved_run(args.run)
    ids = load_split()[SETS[args.set]]
    if not ids:
        raise Stop(REFUSED, f"labels/split.json has no {args.set} ids")
    labels = load_hand_labels(ids)
    jobs = postings_for(saved, ids)
    docs = {pid: posting_document(jobs[pid]) for pid in ids}
    provenance = _provenance(saved, args.resume, sha256_hex(resume_raw), args.model, ids, judge.name)

    rule_rows = []
    for pid in ids:
        verdict = apply_rule(resume, jobs[pid])
        try:
            check_verdict(verdict, resume, docs[pid])
        except Invalid as e:
            raise Stop(BAD_RULE_VERDICT, f"the rule produced an invalid verdict for {pid} ({e.reason})") from None
        rule_rows.append({"posting_id": pid, "hand_label": labels[pid], "verdict": verdict["verdict"],
                          "outcome": outcome("accepted", verdict["verdict"], labels[pid])})
    baseline = {**score([r["outcome"] for r in rule_rows]), "postings": rule_rows}

    # Every refusal comes before the first call. A target is new, done (complete: re-scored from its
    # files) or partial (resumed). On development a resume calls postings with no saved call or a saved
    # error; on held-out it calls only postings with no saved call, so none is ever sent twice (A15).
    plan = []
    for name, path, prompt in prompts:
        target = EXPERIMENTS_DIR / args.set / prompt.sha256[:12]
        previous = _previous(target, prompt, provenance, held_out, prompt_shas) if target.exists() else None
        known = {}
        if previous is not None:
            for pid in ids:
                j = _saved(judge, target, pid, resume, docs[pid])
                if held_out and (target / "claude" / f"{pid}.request.json").exists():
                    known[pid] = j or _judgment("error", "no_saved_response", args.model)
                elif j is not None and (previous.get("complete", True) or j["status"] != "error"):
                    known[pid] = j
            if previous.get("complete", True) and len(known) != len(ids):
                raise Stop(REFUSED, f"{target.as_posix()}: results.json is complete but saved calls are missing")
        plan.append({"name": name, "path": path, "prompt": prompt, "target": target, "previous": previous,
                     "known": known, "todo": [pid for pid in ids if pid not in known]})
    if held_out and all(step["previous"] is not None and not step["todo"] for step in plan):
        raise Stop(REFUSED, "held-out refused: it has already run to completion; the held-out set runs once")
    if held_out:
        check_committed([step["path"] for step in plan])
    if any(step["todo"] for step in plan) and not judge.available():
        raise Stop(REFUSED, f"experiment calls the judge and --judge {judge.name} is not available "
                            f"({judge.unavailable_reason})")

    started = clock()
    print(f"experiment {args.set}: {len(ids)} postings from {saved.raw_path}; judge {judge.name}")
    for step in plan:
        target, prompt, previous, judgments = step["target"], step["prompt"], step["previous"], dict(step["known"])
        called = 0
        if step["todo"]:
            out = OutDir(target, exist_ok=previous is not None)
            for pid in step["todo"]:
                if judge.stopped:
                    break
                _set_aside(target, pid, utc_stamp(started))
                judgments[pid] = judge.call(prompt, args.model, resume, pid, docs[pid], out, clock)
                called += 1
                out.write_json(f"claude/{pid}.validation.json", judgments[pid])
        complete = len(judgments) == len(ids) and not (judge.stopped and step["todo"])
        rows = [{"posting_id": pid, "hand_label": labels[pid], **judgments[pid],
                 "outcome": outcome(judgments[pid]["status"], judgments[pid]["verdict"], labels[pid])}
                for pid in ids if pid in judgments]
        result = score([r["outcome"] for r in rows]) if complete else {
            "n": len(ids), "counts": None, "pass_rate": None, "wilson_95": None}
        results = {
            "kind": "experiment",
            "set": args.set,
            "created_at": previous["created_at"] if previous else utc_iso(started),
            **({"rescored_at": utc_iso(started)} if previous else {}),
            **provenance,
            "prompt_path": prompt.path,
            "prompt_sha256": prompt.sha256,
            "prompt_shas": prompt_shas,
            "complete": complete,
            "stopped": judge.stopped if not complete else None,
            **result,
            "postings": rows,
            "baseline_rule": baseline,
        }
        atomic_write(target / "results.json", json_bytes(results))
        if not step["todo"]:
            how = "re-scored from saved responses"
        else:
            how = f"called {called}" + (f", reused {len(step['known'])}" if step["known"] else "")
        summary = _summary(result) if complete else f"INCOMPLETE ({len(rows)} of {len(ids)} judged)"
        print(f"  {step['name']} {step['path']} (sha256 {prompt.sha256[:12]}, {how}): {summary}")
        print(f"    {(target / 'results.json').as_posix()}")
        if judge.stopped:
            break
    print(f"  rule (record, baseline): {_summary(baseline)}")
    if judge.stopped:
        print(f"jobwatch: judge stopped: {judge.stopped['reason']} on posting {judge.stopped['posting_id']}; "
              "no further calls; rerun the same command to resume", file=sys.stderr)
        return OTHER
    return OK


def _summary(result):
    c, n = result["counts"], result["n"]
    lo, hi = result["wilson_95"]
    return (", ".join(f"{o} {c[o]}" for o in OUTCOMES)
            + f"; pass rate {c['accepted_correct']}/{n} = {result['pass_rate']:.3f}, 95% Wilson [{lo:.3f}, {hi:.3f}]")
