"""Check the claude.ai replies from the action-surface comparison (Chapter 3). No Claude call.

    python3 experiment/action-surface/check_surface_replies.py save chat chat-reply.txt "2026-10-30 14:05 EDT"
    python3 experiment/action-surface/check_surface_replies.py save file file-reply.txt "2026-10-30 14:20 EDT"
    python3 experiment/action-surface/check_surface_replies.py

`save` wraps a reply pasted verbatim into a .txt file as chat-reply.json or file-reply.json, with the
date and time you give; it refuses to overwrite one. With no arguments, the script runs the revision-1
validator and the separate support check on each saved reply, and compares its verdict and
failed_check with my hand label and the rule judge.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent.parent)]
from hand_labels import ROOT, hand_labels, postings, split  # noqa: E402
from agent import rules, validator  # noqa: E402
from agent.resume import load_resume  # noqa: E402

POSTING_ID = 8660923002
SURFACES = {"chat": "chat-reply.json", "file": "file-reply.json"}


def save(surface, text_path, saved_at):
    out = HERE / SURFACES[surface]
    if out.exists():
        raise SystemExit(f"refused: {out.name} exists; replies are saved once")
    reply = Path(text_path).read_text(encoding="utf-8-sig")
    out.write_text(json.dumps({"surface": surface, "posting_id": POSTING_ID, "saved_at": saved_at,
                               "reply": reply}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"saved {out.name}: {len(reply)} characters, verbatim")


def check():
    dev, _ = split()
    if POSTING_ID not in dev:
        raise SystemExit("refused: the action-surface posting must be a development posting")
    resume = load_resume(ROOT / "data" / "resume.example.json")
    requirements = json.loads((ROOT / "data" / "requirements.json").read_text(encoding="utf-8"))
    job = postings()[POSTING_ID]
    hand = hand_labels()[POSTING_ID]
    rule = rules.evaluate(job, resume, requirements)
    print(f"posting {POSTING_ID}: my label {hand['my_label']} ({hand['my_failed_check'] or 'null'}), "
          f"rule judge {rule['verdict']} ({rule['failed_check'] or 'null'})")

    for surface, name in SURFACES.items():
        path = HERE / name
        print(f"\n[{surface}] {name}")
        if not path.exists():
            print("  not saved yet")
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        reply = saved["reply"]
        if not isinstance(reply, str):  # an object pasted straight into the file
            reply = json.dumps(reply)
        print(f"  saved_at: {saved.get('saved_at')}")
        errors = validator.validate(reply, resume, {POSTING_ID}, schema="revision-1")
        print("  valid: " + ("yes" if not errors else "no: " + "; ".join(errors)))
        try:
            parsed = json.loads(reply)
        except ValueError:
            continue
        if not isinstance(parsed, dict):
            continue
        verdict, failed = parsed.get("verdict"), parsed.get("failed_check", "(missing)")
        print(f"  verdict {verdict}, failed_check {'null' if failed is None else failed}")
        print(f"  vs my label:   verdict {'same' if verdict == hand['my_label'] else 'differs'}, "
              f"failed_check {'same' if failed == hand['my_failed_check'] else 'differs'}")
        print(f"  vs rule judge: verdict {'same' if verdict == rule['verdict'] else 'differs'}, "
              f"failed_check {'same' if failed == rule['failed_check'] else 'differs'}")
        citations = [c for c in parsed.get("citations") or [] if isinstance(c, dict)]
        for c in citations:
            print(f"  citation `{c.get('posting_field')}` / resume `{c.get('resume_field')}`: "
                  f"{c.get('quote')!r} -> {validator.support_check(c, job)}")
        if not citations:
            print("  no citations to check")


if __name__ == "__main__":
    if sys.argv[1:2] == ["save"] and len(sys.argv) == 5 and sys.argv[2] in SURFACES:
        save(*sys.argv[2:])
    elif len(sys.argv) == 1:
        check()
    else:
        raise SystemExit(__doc__)
