"""Run the frozen question set through an answerer and the checker; write a dated eval report.

  python -m claimcheck.eval                              # offline baseline (default)
  python -m claimcheck.eval --answerer claude            # live Claude run (needs ANTHROPIC_API_KEY)
  python -m claimcheck.eval --answerer recorded --responses runs/<run>/responses.jsonl
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from . import answerers
from .checker import CHECKER_VERSION, check
from .contract import ContractError, parse
from .grading import GRADE_ORDER, grade, shown

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
QUESTIONS = DATA / "questions.jsonl"
FROZEN = DATA / "FROZEN.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_sha() -> str:
    for line in FROZEN.read_text().splitlines():
        if line.startswith("sha256:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("data/FROZEN.md has no sha256 line")


def load_docs() -> dict[str, str]:
    return {p.name: p.read_text() for p in sorted(DATA.glob("policy_*.md"))}


def load_questions() -> list[dict]:
    return [json.loads(l) for l in QUESTIONS.read_text().splitlines() if l.strip()]


def run(answerer, docs, questions):
    rows = []
    for q in questions:
        if isinstance(answerer, answerers.RecordedAnswerer):
            reply = answerer.answer_for(q["id"])
        else:
            reply = answerer.answer(q["question"], docs)
        try:
            ans, contract_error = parse(reply["raw"]), None
        except ContractError as exc:
            ans, contract_error = None, str(exc)
        result = check(ans, docs) if ans else None
        shown_as = shown(ans, result)
        rows.append({
            "q": q, "reply": reply, "answer": ans, "shown": shown_as,
            "grade": grade(q, ans, shown_as),
            "reason": contract_error and f"contract: {contract_error}" or "; ".join(result.reasons),
        })
    return rows


def _cell(text, limit=110):
    text = " ".join(str(text).split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(rows, answerer, run_at, command) -> str:
    counts = {g: sum(r["grade"] == g for r in rows) for g in GRADE_ORDER}
    served = sorted({r["reply"].get("served_by", "?") for r in rows})
    replay = isinstance(answerer, answerers.RecordedAnswerer)
    lines = [
        f"# ClaimCheck eval report: {run_at:%Y-%m-%d} ({answerer.name})",
        "",
        "## Executive summary",
        "",
        f"The frozen set of {len(rows)} questions about one synthetic homeowner policy was run through the "
        f"**{answerer.name}** answerer and the citation checker. "
        f"{counts['CORRECT']} correct, {counts['CAUGHT']} caught by the checker, {counts['MISSED']} missed, "
        f"**{counts['WRONG']} wrong answers reached the reader**. Failures are listed first.",
    ]
    if answerer.name == "baseline":
        lines += ["", "This run uses the no-model baseline, not Claude. It shows what the checker does with "
                  "a crude answerer; it says nothing about Claude's accuracy."]
    if replay:
        lines += ["", "This is a replay of saved Claude replies, not a new API call."]
    lines += [
        "", "## Run record", "",
        "| | |", "|---|---|",
        f"| Run at | {run_at:%Y-%m-%d %H:%M %Z} |",
        f"| Command | `{command}` |",
        f"| Answerer | {answerer.name} |",
        f"| Model / served by | {', '.join(served)} |",
        f"| Prompt version | {answerers.PROMPT_VERSION if answerer.name != 'baseline' else 'n/a'} |",
        f"| Checker version | {CHECKER_VERSION} |",
        f"| Question set | `data/questions.jsonl`, sha256 `{sha256(QUESTIONS)[:16]}…` (frozen, see `data/FROZEN.md`) |",
    ]
    for doc in sorted(DATA.glob("policy_*.md")):
        lines.append(f"| Document | `data/{doc.name}`, sha256 `{sha256(doc)[:16]}…` |")
    lines += [
        "", "## Results (failures first)", "",
        "| Q | kind | shown to reader | grade | checker / contract | quote |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda r: (GRADE_ORDER[r["grade"]], r["q"]["id"])):
        quote = r["answer"].quote if r["answer"] else ""
        lines.append(f"| {r['q']['id']} | {r['q']['kind']} | {r['shown']} | **{r['grade']}** | "
                     f"{_cell(r['reason'], 80)} | {_cell(quote)} |")
    lines += [
        "", "## Limits of this run", "",
        "- One synthetic policy and 10 questions: a smoke test of the pipeline, not evidence about real claims.",
        "- The checker proves the quote exists in the document. Its \"quote contains the answer\" test is a "
        "proxy (numbers must match, half the answer's content words must appear in the quote), so a real "
        "quote from the wrong clause can still pass. Grading against the frozen gold text is what catches that.",
        "- The gold answers and the questions were written by the same person who wrote the checker.",
        "", "Generated by `claimcheck/eval.py`. Not edited by hand.", "",
    ]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--answerer", choices=["baseline", "claude", "recorded"], default="baseline")
    p.add_argument("--responses", type=Path, help="responses.jsonl to replay (with --answerer recorded)")
    p.add_argument("--reports", type=Path, default=ROOT / "reports")
    args = p.parse_args(argv)

    if sha256(QUESTIONS) != frozen_sha():
        raise SystemExit("data/questions.jsonl changed after it was frozen. See data/FROZEN.md.")
    if args.answerer == "recorded":
        if not args.responses:
            raise SystemExit("--answerer recorded needs --responses PATH")
        answerer = answerers.RecordedAnswerer(args.responses)
    elif args.answerer == "claude":
        answerer = answerers.ClaudeAnswerer()
    else:
        answerer = answerers.BaselineAnswerer()

    run_at = datetime.now().astimezone()
    command = "python -m claimcheck.eval " + " ".join(argv if argv is not None else sys.argv[1:])
    rows = run(answerer, load_docs(), load_questions())

    args.reports.mkdir(parents=True, exist_ok=True)
    report = args.reports / f"eval_report-{run_at:%Y-%m-%d}-{answerer.name}.md"
    report.write_text(render(rows, answerer, run_at, command.strip()))
    if answerer.name == "claude":
        run_dir = ROOT / "runs" / f"{run_at:%Y-%m-%d-%H%M}-claude"
        run_dir.mkdir(parents=True, exist_ok=True)
        with (run_dir / "responses.jsonl").open("w") as fh:
            for r in rows:
                fh.write(json.dumps({"id": r["q"]["id"], "run_at": f"{run_at:%Y-%m-%d %H:%M %Z}", **r["reply"]}) + "\n")
        print(f"raw replies saved: {run_dir / 'responses.jsonl'}")

    counts = {g: sum(r["grade"] == g for r in rows) for g in GRADE_ORDER}
    print(f"{answerer.name}: " + "  ".join(f"{g} {n}" for g, n in counts.items()))
    print(f"report: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
