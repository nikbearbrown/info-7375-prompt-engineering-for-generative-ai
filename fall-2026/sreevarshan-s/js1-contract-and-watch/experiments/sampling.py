"""Sampling check, run by hand in the Claude app: build the prompts here, validate the saved replies here.

    python3 -m experiments.sampling build
    python3 -m experiments.sampling check experiments/sampling/replies/8546367002-1.txt

No Claude call and no network. `build` uses js1.claude_judge.build_prompt with prompts/baseline.txt,
exactly as the judge would. `check` uses js1.claude_judge.validate, the judge's own JSON validator.
A reply file's name starts with its posting id (for example 8546367002-1.txt), unless --posting-id is given.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from js1 import claude_judge
from js1.persona import PersonaRefused, load_persona

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "evidence" / "raw" / "2026-10-30T23-59-22Z.json"
SAMPLING_DIR = ROOT / "experiments" / "sampling"
POSTING_IDS = (8546367002, 8921476002, 8401114002, 8648494002, 8847738002)
PROMPT_NAME = "baseline"

EXIT_OK = 0
EXIT_PERSONA = 1
EXIT_INVALID = 4


def build(resume, profile, raw=RAW, out_dir=SAMPLING_DIR / "prompts", ids=POSTING_IDS,
          prompts_dir=claude_judge.PROMPTS_DIR):
    jobs = {j["id"]: j for j in json.loads(Path(raw).read_text(encoding="utf-8"))["jobs"]}
    missing = [i for i in ids if i not in jobs]
    if missing:
        raise ValueError(f"postings missing from {raw}: {missing}")
    prompt_text = (Path(prompts_dir) / f"{PROMPT_NAME}.txt").read_text(encoding="utf-8")
    candidate = claude_judge.candidate_fields(resume, profile)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for pid in ids:
        path = out_dir / f"{pid}.txt"
        path.write_text(claude_judge.build_prompt(prompt_text, jobs[pid], candidate), encoding="utf-8")
        written.append(path)
    return written


def check(reply_path, resume, profile, posting_id=None):
    """Return (status, verdict_or_error) for one saved reply, using the judge's validator."""
    reply_path = Path(reply_path)
    if posting_id is None:
        m = re.match(r"(\d+)", reply_path.name)
        if not m:
            raise ValueError(f"cannot read a posting id from {reply_path.name}; pass --posting-id")
        posting_id = int(m.group(1))
    allowed = claude_judge.citable_fields(claude_judge.candidate_fields(resume, profile))
    try:
        parsed = claude_judge.validate(reply_path.read_text(encoding="utf-8"), posting_id, allowed)
    except claude_judge.InvalidReply as exc:
        return "invalid", str(exc)
    return "valid", parsed["verdict"]


def main(argv=None):
    parser = argparse.ArgumentParser(prog="experiments.sampling")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="write experiments/sampling/prompts/<posting_id>.txt")
    p_check = sub.add_parser("check", help="validate saved reply files")
    p_check.add_argument("replies", nargs="+")
    p_check.add_argument("--posting-id", type=int)
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(claude_judge.RESUME, claude_judge.PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return EXIT_PERSONA
    if args.cmd == "build":
        for path in build(resume, profile):
            print(path.relative_to(ROOT))
        return EXIT_OK
    code = EXIT_OK
    for reply in args.replies:
        status, detail = check(reply, resume, profile, args.posting_id)
        if status == "valid":
            print(f"{reply}: valid, verdict: {detail}")
        else:
            print(f"{reply}: invalid ({detail})")
            code = EXIT_INVALID
    return code


if __name__ == "__main__":
    sys.exit(main())
