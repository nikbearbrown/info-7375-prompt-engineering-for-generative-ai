"""Render the explanation prompt for one shortlist entry.

    python3 tools/explain_shortlist.py P-v1 ashby:34413f8d-...
    python3 tools/explain_shortlist.py P-v2 --first

**This program does not call a model.** It prints a prompt. Nothing in this
repository has an API key, makes a network request, or calls Claude -- see
FILTER.md §5 and `tests/test_no_model_and_no_network.py`, which read the source
to check that rather than taking this docstring's word for it.

The prompt is an *object* in the Chapter 9 sense: a thing with content I chose,
which changes the system's behaviour when I change it, and which was not
trained. `reports/what-moves-the-score.md` changes it one object at a time and records
every real response with the date it was obtained. Three variants exist for
that reason: P-v1 (loose rules, full body), P-v2 (strict rules, scored spans
only) and P-v3 (strict rules, full body). P-v1 -> P-v2 changes the prompt
*and* the context at once, which is the mistake the chapter is about; P-v3 is
what isolates them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod, pipeline  # noqa: E402


def render(version: str, decision) -> str:
    template = (ROOT / "prompts" / f"explain-{version}.txt").read_text(encoding="utf-8")
    spans = "\n".join(
        f'- [{h.signal} {h.points:+d}] "{h.sentence}"' for h in decision.score.hits
    )
    return template.format(
        title=decision.posting.title,
        board=decision.posting.board,
        score=decision.score.total,
        body=decision.posting.body,
        spans=spans,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", choices=["P-v1", "P-v2", "P-v3"])
    ap.add_argument("identity", nargs="?")
    ap.add_argument("--first", action="store_true", help="the top-scoring entry")
    args = ap.parse_args(argv)

    postings = corpus_mod.load()
    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    short = [
        d for d in pipeline.run(postings, persona) if d.bucket == pipeline.SHORTLISTED
    ]
    short.sort(key=lambda d: (-d.score.total, d.posting.identity))

    if args.first or not args.identity:
        chosen = short[0]
    else:
        chosen = next(d for d in short if d.posting.identity == args.identity)

    print(render(args.version, chosen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
