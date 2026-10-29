"""Claude judge experiments on DEVELOPMENT postings only, with prompts/baseline.md.

    python3 experiment/claude_dev.py sampling       # 5 dev postings x 4 fresh calls -> experiment/sampling/
    python3 experiment/claude_dev.py baseline-dev   # 10 dev postings x 1 fresh call -> experiment/runs/baseline-dev/

Every call is a separate `claude -p` process (a fresh conversation) through agent.claude_judge,
which saves the prompt, the raw reply and its date, session_id and model. Any held-out id is refused.
"""
import json
import random
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parent.parent)]
from hand_labels import HERE, ROOT, hand_labels, postings, split  # noqa: E402
from agent import claude_judge, validator  # noqa: E402
from agent.resume import load_resume  # noqa: E402

SAMPLING_SEED = 20261030
SAMPLING_POSTINGS = 5
SAMPLING_CALLS = 4


def sampling_pick(dev, labels):
    """5 dev postings with a mix of my labels: up to 2 of my relevant ones, the rest not_relevant."""
    rng = random.Random(SAMPLING_SEED)
    rel = sorted(i for i in dev if labels[i]["my_label"] == "relevant")
    other = sorted(i for i in dev if labels[i]["my_label"] != "relevant")
    k_rel = max(min(len(rel), 2), SAMPLING_POSTINGS - len(other))
    return sorted(rng.sample(rel, k_rel) + rng.sample(other, SAMPLING_POSTINGS - k_rel))


def one_call(job, resume, out_dir, template):
    """One fresh judge call, then the validator and the support check, kept in separate columns."""
    outcome = claude_judge.judge(job, resume, out_dir, template=template)
    row = {"posting_id": job["id"], "status": outcome["status"], "meta": outcome.get("meta")}
    if outcome["status"] != "ran":
        row.update(valid=False, errors=[f"not run: {outcome['reason']}"], verdict=None, citations=[])
        return row
    # The posting it was given is the only id a judgment may name.
    errors = validator.validate(outcome["result"], resume, {job["id"]})
    row.update(valid=not errors, errors=errors, verdict=None, citations=[])
    try:
        parsed = json.loads(outcome["result"])
    except ValueError:
        return row
    if isinstance(parsed, dict):
        # Recorded even when invalid, so a wrong shape and an unsupported quote stay distinguishable.
        row["verdict"] = parsed.get("verdict")
        if isinstance(parsed.get("citations"), list):
            row["citations"] = [dict(c, support=validator.support_check(c, job))
                                for c in parsed["citations"] if isinstance(c, dict)]
    return row


def all_supported(row):
    return bool(row["citations"]) and all(c["support"] == "supported" for c in row["citations"])


def main(mode):
    resume = load_resume(ROOT / "data" / "resume.example.json")
    template = (ROOT / "prompts" / "baseline.md").read_text(encoding="utf-8")
    dev, heldout = split()
    labels = hand_labels()
    jobs = postings()

    if mode == "sampling":
        ids, calls, base = sampling_pick(dev, labels), SAMPLING_CALLS, HERE / "sampling"
    elif mode == "baseline-dev":
        ids, calls, base = sorted(dev), 1, HERE / "runs" / "baseline-dev"
    else:
        raise SystemExit("usage: claude_dev.py sampling | baseline-dev")
    if set(ids) & set(heldout) or not set(ids) <= set(dev):
        raise SystemExit("refused: only development postings may be sent to Claude")
    if (base / "results.json").exists():
        raise SystemExit(f"refused: {base.relative_to(ROOT)}/results.json exists; these calls already ran")

    rows = []
    for pid in ids:
        for n in range(1, calls + 1):
            out_dir = base / str(pid) / f"call-{n}" if calls > 1 else base
            row = one_call(jobs[pid], resume, out_dir, template)
            row.update(call=n, my_label=labels[pid]["my_label"], my_failed_check=labels[pid]["my_failed_check"],
                       supported=all_supported(row),
                       passed=row["valid"] and row["verdict"] == labels[pid]["my_label"])
            rows.append(row)
            print(pid, n, row["status"], row["verdict"], "valid" if row["valid"] else row["errors"], flush=True)

    result = {"mode": mode, "prompt": "prompts/baseline.md", "seed": SAMPLING_SEED if mode == "sampling" else None,
              "posting_ids": ids, "calls_per_posting": calls, "rows": rows}
    (base / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
