"""Prompt Experiment (Chapter 2): one judge call per posting for a split.

    python3 scripts/run_experiment.py --set dev --prompt judge-dev-v0     # baseline
    python3 scripts/run_experiment.py --set dev --prompt judge-dev-v1     # one-sentence revision
    python3 scripts/run_experiment.py --set heldout --final --prompt ...  # only at the very end

Only the judge-dev-* prompts are allowed here. They are scoped to the
hand-label question; judge-v1 is the production judge and is not part of
this experiment.

Saves each call to logs/experiment_raw/<prompt_version>/<set>/<posting_id>.json
and never overwrites: one call per posting per prompt version. The held-out
set needs --final and its hand labels saved first.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from agent import judge  # noqa: E402
from experiment_common import LABELS, RAW_ROOT, read_labels, split_ids  # noqa: E402

BASELINE = ROOT / "evidence" / "gitlab_jobs_20261030T201528Z.json"
EXPERIMENT_PROMPTS = ["judge-dev-v0", "judge-dev-v1"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["dev", "heldout"], required=True)
    ap.add_argument("--prompt", choices=EXPERIMENT_PROMPTS, required=True)
    ap.add_argument("--final", action="store_true",
                    help="required for heldout: confirms the dev phase is finished")
    args = ap.parse_args()

    if args.set == "heldout" and not args.final:
        print("REFUSED: the held-out set runs only at the end, with --final.", file=sys.stderr)
        return 2
    if not LABELS[args.set].exists():
        print(f"REFUSED: hand labels {LABELS[args.set].relative_to(ROOT)} must be saved "
              "before this set is run.", file=sys.stderr)
        return 2
    read_labels(args.set)  # fail now, not after spending calls, if labels are malformed

    try:
        client = judge.get_client()
    except judge.MissingAPIKey as e:
        print(f"STOPPED: {e}", file=sys.stderr)
        return 2

    resume = json.loads((ROOT / "resume.json").read_text())
    jobs = {j["id"]: j for j in json.loads(BASELINE.read_bytes())["jobs"]}
    out_dir = RAW_ROOT / args.prompt / args.set
    out_dir.mkdir(parents=True, exist_ok=True)
    system_prompt = judge.PROMPTS[args.prompt]
    prompt_sha = hashlib.sha256(system_prompt.encode()).hexdigest()

    for pid in split_ids(args.set):
        path = out_dir / f"{pid}.json"
        if path.exists():
            print(f"skip (already run): {path.relative_to(ROOT)}")
            continue
        p = jobs[pid]
        r = judge.judge(p, resume, client, prompt_version=args.prompt)
        r.update(set=args.set, posting_title=p["title"].strip(),
                 system_prompt_sha256=prompt_sha, system_prompt=system_prompt,
                 user_message=judge.build_user_message(p, resume))
        path.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"{path.relative_to(ROOT)}: {r['status']} {r['verdict']}")
    print(f"\nnext: python3 scripts/score_experiment.py --set {args.set} --prompt {args.prompt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
