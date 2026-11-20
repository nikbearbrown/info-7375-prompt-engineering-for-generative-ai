"""Reproduce the React/Go defect on saved Lever postings.

    python3 -m agent.reproduce_skills evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json

For every posting where React or Go matched, prints the posting title and the
40 characters around each match, so a person can judge whether it is a skill.
"""

import json
import sys

from agent.skills import _word, lever_text, match_skills

WATCH = ["React", "Go"]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    raw = json.loads(open(argv[0], encoding="utf-8").read())
    postings = json.loads(raw["body"])
    persona = json.loads(open("examples/persona.example.json", encoding="utf-8").read())
    print(f"source: {argv[0]} ({len(postings)} postings)")
    print(f"persona skills: {persona['skills']}\n")
    for p in postings:
        text = " ".join(lever_text(p).split())
        matched = match_skills(text, persona["skills"])
        hits = [s for s in WATCH if s in matched]
        if not hits:
            continue
        print(f"{p['text']}  [{p['id']}]")
        print(f"  matched skills: {matched}")
        for skill in hits:
            for m in _word(skill).finditer(text):
                ctx = text[max(0, m.start() - 40):m.end() + 40]
                print(f"  {skill:<5} ... {ctx} ...")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
