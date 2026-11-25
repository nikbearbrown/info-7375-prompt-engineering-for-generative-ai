"""Rebuild the audit's and the held-out set's blind cards with today's card builder, and compare them with the cards
that were committed and judged. A diagnostic, computed after the fact from committed files: it changes no rule, no
verdict and no frozen result.

The audit's cards (js3/audit/2026-11-21T044414Z/CARDS.md, committed in c19dd8e; his verdicts frozen in 45fc2c0)
were built before f629b8c (2026-11-22) changed tools/audit_kit.py's card(): since then a card keeps lines whole at
"U.S.", "e.g." and "i.e.", and shows every line R5's phrases match. The held-out cards were rebuilt with that change
before any verdict (js3/heldout/2026-11-21T044414Z/CHANGES.md), so they should rebuild byte for byte.

Each kit is rebuilt by its own build() (tools/audit_kit.py, tools/heldout_kit.py) into a temporary folder that is
deleted afterwards: the same filter run, the seed its SAMPLE.md or README.md published, FILTER.md pinned to the run's
filter_version (build() does that). Nothing is written next to the committed kits. Both kits' answers are already
open (the audit's since 79df09c, the held-out set's since cb1b50c): the rebuilt answer files are only compared byte
for byte, and the audit's opened answers give each changed card's fate.

For every card that differs: the lines each block lost and gained, the words gained, and which hard rule reads the
gained line. A rule reads a line when the line holds what the rule decides on (FILTER.md v1.0, Section 7): R1 the
employment type, R2 the locations, R3 and R4 the title; R5 a U.S.-person, clearance or sponsorship phrase; R6 a start
phrase, or "start" with a month and year or a season and year; R7 a number of years; R8 an annotation title, or a
main-responsibility phrase with a labeling task. "export control" is R5's caution: shown, never a reason to reject.

Usage (from the repo root):
  python3 tools/card_rebuild_check.py            write js3/checks/CARD-REBUILD.md
  python3 tools/card_rebuild_check.py --check    write nothing; exit 1 if the committed file is not what this rebuilds
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(TOOLS))

import audit_kit  # noqa: E402
import heldout_kit  # noqa: E402
import score_audit  # noqa: E402
from job_agent import filter as flt  # noqa: E402
from job_agent.rule import MONTHS, YEARS, _flat, _has_word, _MONTH_YEAR  # noqa: E402

RUN_ID = "2026-11-21T044414Z"
FILTER_RUN = REPO / "js3" / "filter-run" / RUN_ID
AUDIT = REPO / "js3" / "audit" / RUN_ID
HELDOUT = REPO / "js3" / "heldout" / RUN_ID
OUT = REPO / "js3" / "checks" / "CARD-REBUILD.md"
WRITTEN = "2026-11-24"
COMMAND = "python3 tools/card_rebuild_check.py"
CARD = re.compile(r"^## Card (\d\d)\n", re.M)
BLOCK = re.compile(r"^\*\*(.+):\*\*$")
LONGEST = 240
SAME_FILES = {"audit": ("sealed/answers.json", "SAMPLE.md", "INSTRUCTIONS.md"),
              "held-out": ("sealed/answers.json", "README.md", "INSTRUCTIONS.md", "CARDS.md")}


def split_cards(text: str) -> tuple:
    parts = CARD.split(text)
    return parts[0], {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def blocks(body: str) -> "collections.OrderedDict":
    """{block name: its lines} for one card: "facts" (the title and the field lines), then each bold block."""
    out = collections.OrderedDict([("facts", [])])
    current = "facts"
    for line in body.split("\n"):
        m = BLOCK.match(line)
        if m:
            current = m.group(1)
            out[current] = []
        elif line.strip() and line.strip() != "---" and line != "- none":
            out[current].append(line)
    return out


def minus(a: list, b: list) -> list:
    """The items of a that b lacks, counted, in a's order."""
    left = collections.Counter(b)
    out = []
    for item in a:
        if left[item]:
            left[item] -= 1
        else:
            out.append(item)
    return out


def text_of(line: str) -> str:
    return line[2:] if line.startswith(("- ", "> ")) else line


def readers(line: str, block: str, rules: dict) -> list:
    """[(what reads the line, the phrase it decides on)], by FILTER.md v1.0's lists."""
    if block == "facts":
        fields = (("- Employment type:", "R1"), ("- Locations:", "R2"))
        named = [(rule, line) for start, rule in fields if line.startswith(start)]
        return named or ([("R3, R4 and R8's title check", line)] if line.startswith("**") else [])
    text, out = text_of(line), []
    low = _flat(text).lower()
    out += [("R5", p) for p in rules["status_us_person_phrases"] + rules["status_sponsorship_phrases"]
            if p.lower() in low]
    out += [("R6", p) for p in rules["start_phrases"] if p.lower() in low]
    if _has_word(text, "start"):
        dated = [f"{m} {y}" for m, y in _MONTH_YEAR.findall(text) if m.lower() in MONTHS]
        seasons = [f"{w} {y}" for w, y in flt._season_mentions(text, rules)]
        out += [("R6", d) for d in dated + seasons]
    out += [("R7", m.group(0)) for m in YEARS.finditer(text)]
    duty = [p for p in rules["annotation_responsibility_phrases"] if _has_word(text, p)]
    task = [p for p in rules["annotation_task_phrases"] if _has_word(text, p)]
    if duty and task:
        out.append(("R8", f"{duty[0]} ... {task[0]}"))
    if rules["caution_phrase"] in low:
        out.append(("R5's caution, never a reason to reject", rules["caution_phrase"]))
    return out


def compare(old_text: str, new_text: str, rules: dict) -> dict:
    old_head, old_cards = split_cards(old_text)
    new_head, new_cards = split_cards(new_text)
    if sorted(old_cards) != sorted(new_cards):
        raise SystemExit("STOP: the rebuilt kit has other card numbers than the committed one")
    changed = {}
    for n in sorted(old_cards):
        if old_cards[n] == new_cards[n]:
            continue
        before, after = blocks(old_cards[n]), blocks(new_cards[n])
        old_flat = _flat(old_cards[n]).lower()
        diffs = []
        for name in list(before) + [b for b in after if b not in before]:
            lost, gained = minus(before.get(name, []), after.get(name, [])), minus(after.get(name, []),
                                                                                    before.get(name, []))
            if not lost and not gained:
                continue
            words = minus(" ".join(text_of(x) for x in gained).split(), " ".join(text_of(x) for x in lost).split())
            dropped = minus(" ".join(text_of(x) for x in lost).split(), " ".join(text_of(x) for x in gained).split())
            read = []
            for line in gained:
                for rule, phrase in readers(line, name, rules):
                    read.append({"rule": rule, "phrase": phrase, "on_old_card": phrase.lower() in old_flat})
            diffs.append({"block": name, "lost": lost, "gained": gained, "words": words, "dropped": dropped,
                          "read": read})
        changed[n] = diffs
    return {"same_head": old_head == new_head, "cards": len(old_cards), "changed": changed}


def rebuild(kind: str) -> dict:
    """Build the kit again into a temporary folder; compare it with the committed one; delete the folder."""
    committed = AUDIT if kind == "audit" else HELDOUT
    published = (committed / ("SAMPLE.md" if kind == "audit" else "README.md")).read_text(encoding="utf-8")
    seed = int(re.search(r"[Ss]eed \*\*(\d+)\*\*", published).group(1))
    digest = hashlib.sha256((committed / "sealed" / "answers.json").read_bytes()).hexdigest()
    if f"`{digest}`" not in published:
        raise SystemExit(f"STOP: the committed {kind} answers do not match the SHA-256 their kit published")
    data = json.loads((FILTER_RUN / "verdicts.json").read_text(encoding="utf-8"))
    version = data["meta"].get("filter_version", "1.0")
    with tempfile.TemporaryDirectory(prefix="card-rebuild-") as tmp:
        if kind == "audit":
            fresh = audit_kit.build(FILTER_RUN, Path(tmp), seed)
        else:
            fresh = heldout_kit.build(FILTER_RUN, Path(tmp), AUDIT / "sealed" / "answers.json", seed)
        same = {name: (fresh / name).read_bytes() == (committed / name).read_bytes() for name in SAME_FILES[kind]}
        result = compare((committed / "CARDS.md").read_text(encoding="utf-8"),
                         (fresh / "CARDS.md").read_text(encoding="utf-8"), flt.load_rules(version=version))
    result.update(seed=seed, digest=digest, version=version, same=same)
    return result


def listing(items: list) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def shown(line: str) -> str:
    text = text_of(line)
    return "\"" + (text if len(text) <= LONGEST else text[:LONGEST] + " ...") + "\""


def verdict_of(card: int, verdicts: dict, after: dict) -> str:
    his, note = verdicts[card]
    text = f"{his} (\"{note}\")"
    if card in after:
        text += f"; after the reveal: {after[card][0]} ({after[card][3]})"
    return text


def assessment(diffs: list) -> str:
    reads = [r for d in diffs for r in d["read"] if not r["rule"].startswith("R5's caution")]
    new = [r for r in reads if not r["on_old_card"]]
    words = [w for d in diffs for w in d["words"]]
    if new:
        named = ", ".join(sorted({f"{r['rule']} (\"{r['phrase']}\")" for r in new}))
        return f"Yes: the card he judged did not show a line {named} reads."
    if reads:
        how = "the same words, now on one line" if not words else ("the words \"" + " ".join(words) +
                                                                     "\" added around them")
        return (f"No: every phrase a rule reads here ({', '.join(sorted({r['phrase'] for r in reads}))}) was "
                f"already on the card he judged; the change is {how}.")
    caution = [r for d in diffs for r in d["read"] if r["rule"].startswith("R5's caution")]
    if caution:
        on_old = all(r["on_old_card"] for r in caution)
        return ("No rule (R1 to R8) reads this line to decide. It is R5's caution, which never rejects in v1.0, and "
                f"\"{caution[0]['phrase']}\" {'was already' if on_old else 'was not'} on the card he judged"
                + (f"; the change adds \"{' '.join(words)}\" in front." if words else "."))
    return "No rule (R1 to R8) reads the changed lines."


def card_section(n: int, diffs: list, answers: dict, verdicts: dict, after: dict) -> list:
    a = answers[n]
    fate = score_audit.filter_side(a)
    out = [f"### Card {n:02d}: {a['title'].strip()}", "",
           f"- His verdict: {verdict_of(n, verdicts, after)}. The filter: {fate}. Group: {a['group']}."]
    for d in diffs:
        out.append(f"- {d['block']}: lost " + ("; ".join(shown(x) for x in d["lost"]) or "nothing")
                   + "; gained " + ("; ".join(shown(x) for x in d["gained"]) or "nothing") + ".")
        out.append("- Words gained: " + ("\"" + " ".join(d["words"]) + "\"" if d["words"] else
                                         "none (the same words as before)")
                   + ("; words lost: \"" + " ".join(d["dropped"]) + "\"" if d["dropped"] else "") + ".")
        reads = "; ".join(f"{r['rule']}: \"{r['phrase']}\", {'on' if r['on_old_card'] else 'not on'} the old card"
                          for r in d["read"])
        out.append(f"- What reads the gained line: {reads or 'no rule'}.")
    out += [f"- Could it have changed his verdict? {assessment(diffs)}", ""]
    return out


def render() -> str:
    audit, held = rebuild("audit"), rebuild("held-out")
    answers = {a["card"]: a for a in json.loads((AUDIT / "sealed" / "answers.json").read_text(encoding="utf-8"))
               ["answers"]}
    verdicts = score_audit.read_verdicts(AUDIT / "VERDICTS.md")
    after = score_audit.read_after_reveal(AUDIT / "AFTER-REVEAL.md")
    changed = audit["changed"]
    disclosed = sorted(c for c in changed if c in after)
    others = sorted(c for c in changed if c not in after)
    in_blocks = collections.Counter(d["block"] for diffs in changed.values() for d in diffs)
    same_files = listing(f"`{name}`" for name, ok in audit["same"].items() if ok)
    lines = [f"Computed by Claude Code on {WRITTEN} from committed files, after the fact. Not a new measurement. "
             f"Rebuild: `{COMMAND}` from the repo root (`--check` compares without writing).", "",
             "# The blind cards rebuilt with today's card builder", "",
             "A diagnostic. It changes no rule, no verdict and no frozen result. The audit's cards were built and "
             "committed (`c19dd8e`, 2026-11-20 at 11:49 PM ET), and his verdicts frozen (`45fc2c0`, 2026-11-22 at "
             "1:44 AM ET), before `f629b8c` (2026-11-22 at 2:02 AM ET) changed `tools/audit_kit.py`'s `card()`: lines "
             "are kept "
             "whole at \"U.S.\", \"e.g.\" and \"i.e.\", and "
             "every line R5's phrases match is shown. Each kit is rebuilt here by its own `build()` into a temporary "
             "folder that is deleted afterwards, from `js3/filter-run/" + RUN_ID + "/`, with FILTER.md pinned to the "
             "run's version; nothing is written next to the committed kits. Both kits' answers were already open; "
             "the rebuilt answer files are only compared byte for byte.", "",
             "## In short", "",
             f"- **Audit:** {audit['cards'] - len(changed)} of {audit['cards']} cards rebuild byte for byte; "
             f"{len(changed)} differ: " + ", ".join("%02d" % c for c in sorted(changed)) + ". Card "
             + ", ".join("%02d" % c for c in disclosed) + " is the one `AFTER-REVEAL.md` already disclosed. Every "
             "difference is in " + ", ".join(f"the block \"{b}\" ({n} cards)" for b, n in sorted(in_blocks.items()))
             + "."]
    could = [c for c in others if assessment(changed[c]).startswith("Yes")]
    lines.append(f"- Besides card " + ", ".join("%02d" % c for c in disclosed) + ", "
                 + (f"{len(could)} of the {len(others)} changed cards gained a line a rule reads that the judged "
                    "card did not show: " + ", ".join("%02d" % c for c in could) + "." if could else
                    f"none of the {len(others)} changed cards gained a line a rule (R1 to R8) reads that the judged "
                    "card did not show, so none of these changes could have changed his verdict by a rule's line."))
    lines.append(f"- **Held-out:** {held['cards'] - len(held['changed'])} of {held['cards']} cards rebuild byte for "
                 "byte, and so do the whole files " + listing(f"`{n}`" for n in sorted(held["same"]))
                 + (", as expected: they were rebuilt with `f629b8c` before he labeled them." if not held["changed"]
                    and all(held["same"].values()) else "; SOME DIFFER (see below)."))
    lines += ["", "## The audit's cards", "",
              f"Rebuilt by `tools/audit_kit.py` with seed {audit['seed']} (published in `SAMPLE.md`) and FILTER.md "
              f"v{audit['version']}. The rebuilt {same_files} are byte for byte the committed ones: the same sample in "
              f"the same order (`sealed/answers.json`, SHA-256 `{audit['digest']}`). The text before the first card is "
              f"{'the same' if audit['same_head'] else 'DIFFERENT'}.", ""]
    for c in others:
        lines += card_section(c, changed[c], answers, verdicts, after)
    lines += ["## Card 17, already disclosed", "",
              "`AFTER-REVEAL.md` records this change and his answer to it; the rebuild shows the same line.", ""]
    for c in disclosed:
        lines += card_section(c, changed[c], answers, verdicts, after)
    lines += ["## The held-out cards", "",
              f"Rebuilt by `tools/heldout_kit.py` with seed {held['seed']} (published in its `README.md`), the audit's "
              f"answers (board and posting id only, as the kit reads them) and FILTER.md v{held['version']}. "
              + "; ".join(f"`{name}`: {'the same' if ok else 'DIFFERENT'}" for name, ok in sorted(held["same"].items()))
              + f". Cards: {held['cards'] - len(held['changed'])} of {held['cards']} the same, byte for byte.", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if the committed file differs")
    args = ap.parse_args(argv)
    text = render()
    name = OUT.relative_to(REPO).as_posix()
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print(f"{name}: {'the same as' if same else 'DIFFERENT FROM'} what the committed files rebuild")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
