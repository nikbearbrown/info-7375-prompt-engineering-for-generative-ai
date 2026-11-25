"""Pick the 20 postings for the hand labels, by the seeded rule in LABELING-RULE.md, and write the sheet.

From the baseline response, take the postings with "Engineer" in the title; split them by the rule
judge's verdict; draw 10 from each side with random.Random(7375), each side sorted by id first; the
first 5 of each side go to the development set and the next 5 to the held-out set; each set is then
shuffled with the same generator. The rule's verdict is used only for this balance and is written to
labels/selection.json, never to labels/SHEET.md.

Usage (from the repo root):  python3 tools/select_postings.py            write both files
                             python3 tools/select_postings.py --check    exit 1 unless they match
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import rule  # noqa: E402
from job_agent import resume as resume_mod  # noqa: E402

BASELINE = "runs/2026-10-30T093102Z/response.json"
PERSONA = "persona/jane-doe.json"
SEED = 7375
SHOWN_BELOW_BOILERPLATE = rule.US_PERSON_PHRASES + rule.SPONSORSHIP_PHRASES + rule.START_PHRASES + ("export control",)


def select():
    raw = (REPO / BASELINE).read_bytes()
    jobs = json.loads(raw.decode("utf-8"))["jobs"]
    jane = resume_mod.load(REPO / PERSONA)
    pool = [j for j in jobs if "engineer" in j["title"].lower()]
    verdict = {j["id"]: rule.judge(j, jane, contract="0.1")["verdict"] for j in pool}  # JS1's selection used v0.1
    relevant = sorted((j for j in pool if verdict[j["id"]] == "relevant"), key=lambda j: j["id"])
    other = sorted((j for j in pool if verdict[j["id"]] != "relevant"), key=lambda j: j["id"])
    rng = random.Random(SEED)
    picked_relevant, picked_other = rng.sample(relevant, 10), rng.sample(other, 10)
    dev, held_out = picked_relevant[:5] + picked_other[:5], picked_relevant[5:] + picked_other[5:]
    rng.shuffle(dev)
    rng.shuffle(held_out)

    def entry(j):
        return {"id": j["id"], "title": j["title"], "rule_verdict": verdict[j["id"]]}

    selection = {
        "what": "The 20 postings for the hand labels, picked by the seeded rule in LABELING-RULE.md",
        "baseline_response": BASELINE,
        "baseline_sha256": hashlib.sha256(raw).hexdigest(),
        "seed": SEED,
        "pool": "postings with 'Engineer' in the title",
        "pool_size": len(pool),
        "pool_relevant_by_rule": len(relevant),
        "pool_not_relevant_by_rule": len(other),
        "development": [entry(j) for j in dev],
        "held_out": [entry(j) for j in held_out],
    }
    by_id = {j["id"]: j for j in jobs}
    return selection, sheet(selection, by_id)


def own_text(description: str) -> str:
    """The posting's text down to "About OpenAI", blank lines dropped, plus any status, start or export line below."""
    lines = [line.rstrip() for line in description.splitlines()]
    cut = next((i for i, line in enumerate(lines) if line.strip().lower() == "about openai"), len(lines))
    kept = [line.strip() for line in lines[:cut] if line.strip()]
    flagged = [line.strip() for line in lines[cut:]
               if any(p.lower() in re.sub(r"\s+", " ", line).lower() for p in SHOWN_BELOW_BOILERPLATE)]
    if flagged:
        kept += ["(below \"About OpenAI\":)"] + flagged
    return "\n".join(kept)


def sheet(selection: dict, by_id: dict) -> str:
    out = ["# Labeling sheet: 20 postings for the hand labels", "",
           f"From the baseline response {selection['baseline_response']} (SHA-256 {selection['baseline_sha256']}).",
           "Label each one with LABELING-RULE.md: relevant, or not_relevant with its reason.",
           "The rule judge's verdict is deliberately not shown here.", ""]
    number = 0
    for name, key in (("Development set", "development"), ("Held-out set", "held_out")):
        out += [f"## {name}", ""]
        for item in selection[key]:
            number += 1
            j = by_id[item["id"]]
            places = [j.get("location") or ""] + [s.get("location") or "" for s in j.get("secondaryLocations") or []]
            out += [f"### {number}. {j['title']}", "",
                    f"- id: `{j['id']}`",
                    f"- Locations: {'; '.join(p for p in places if p)}",
                    f"- Employment type: {j.get('employmentType')}; workplace: {j.get('workplaceType')}",
                    f"- Link: {j.get('jobUrl')}",
                    "", "```text", own_text(j.get("descriptionPlain") or ""), "```", ""]
    return "\n".join(out)


def main(argv) -> int:
    selection, text = select()
    selection_path, sheet_path = REPO / "labels" / "selection.json", REPO / "labels" / "SHEET.md"
    rendered = json.dumps(selection, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv:
        same = (selection_path.read_text(encoding="utf-8") == rendered and sheet_path.read_text(encoding="utf-8") == text)
        print("selection and sheet match the seeded rule" if same else "MISMATCH: the files differ from the seeded rule")
        return 0 if same else 1
    selection_path.parent.mkdir(exist_ok=True)
    selection_path.write_text(rendered, encoding="utf-8")
    sheet_path.write_text(text, encoding="utf-8")
    print(f"wrote {selection_path.relative_to(REPO)} and {sheet_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
