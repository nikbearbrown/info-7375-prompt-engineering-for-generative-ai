"""What moves the score: one change at a time, each against the same baseline, read on the held-out labels.

    python3 measure_changes.py        print every comparison; write state/measure/changes.json

Filter changes (deterministic; each one replaces one v1.0 setting, everything else unchanged):
  F1 a filter word: R4 also matches "does not provide sponsorship"
  F2 the threshold: 4 -> 5
  F3 a rule boundary: R2 rejects when the lowest stated years is 2 or more (v1.0: 3 or more)
  F4 a rule reading: R2 takes the HIGHEST of the stated requirements' lower bounds (v1.0 code takes the lowest
     across all of them, so "6+ years ... 2+ years" counts as 2; every requirement must hold, so it is 6)
Claude changes (claims.py; the filter stays v1.0, so the kept set is the same 12 postings):
  C1 prompt wording: the "copy the quote exactly" sentence removed      (variant loose-quote)
  C2 context: title and locations only, no description                  (variant title-only)
  C3 prompt wording: "never include the field names in a quote" added   (variant no-field-names)
  A1 the abstention rule: abstain on role or location only, not seniority (base claims)
  C0' no change: the base prompt run again. Claude is not deterministic, so a change whose effect is no
      bigger than the difference between C0 and C0' is not shown to do anything.

The held-out labels are the decision set. Tuning numbers are printed too, marked, and never used to choose.
Nothing here trains anything: saving labels, verdicts, and claims to disk changes no model. Any difference
below comes from a rule, a number, or a prompt I changed.
"""
import json
import re
import sys
from unittest import mock

import claims as C
import corpus
import filter as F
import measure as M
from policy import Policy
from tools import Tools

FILTER_CHANGES = {
    "F0 v1.0 baseline": {},
    "F1 R4 word + 'does not provide sponsorship'": {
        "NO_SPONSOR": re.compile(F.NO_SPONSOR.pattern + r"|does not provide sponsorship", re.I)},
    "F2 threshold 4 -> 5": {"THRESHOLD": 5},
    "F3 R2 rejects at 2+ years": {"R2_MIN": 2},
    "F4 R2 reads the highest requirement": {"lowest_years": lambda text: max(
        [(int(m.group(1)), m.group(0).strip()) for m in F.YEARS.finditer(text) if int(m.group(1)) <= F.YEARS_MAX],
        default=(None, None))},
}


def evaluate_with(change):
    def evaluate(p):
        patches = {k: v for k, v in change.items() if k != "R2_MIN"}
        if patches:
            with mock.patch.multiple(F, **patches):
                v = F.evaluate(p)
        else:
            v = F.evaluate(p)
        if "R2_MIN" in change and p.get("text"):
            low, words = F.lowest_years(p["text"])
            if low is not None and low >= change["R2_MIN"] and "R2" not in v["rejected_by"]:
                v = dict(v, verdict="reject", rejected_by=dict(v["rejected_by"], R2=words))
        return v
    return evaluate


def claim_answers(tools, variant, abstain_on=C.ABSTAIN_ON):
    rows = list(__import__("csv").DictReader(tools.read_text(f"state/claims/{variant}_checked.csv").splitlines()))
    labels = {}
    for r in rows:
        labels.setdefault(r["key"], {})[r["property"]] = r["checker_label"]
    return {k: ("I cannot tell" if any(v[p] == "insufficient" for p in abstain_on) else "keep")
            for k, v in labels.items()}


def score_answers(answers, labels, side):
    """coverage (answered / kept) and accuracy on the answered, for kept postings with a label on this side."""
    keys = [k for k in answers if k in labels and labels[k]["side"] == side]
    answered = [k for k in keys if answers[k] != "I cannot tell"]
    right = [k for k in answered if labels[k]["label"] == "yes"]
    abstained_yes = [k for k in keys if answers[k] == "I cannot tell" and labels[k]["label"] == "yes"]
    return {"labeled kept": len(keys), "coverage": M.ratio(len(answered), len(keys)),
            "accuracy on answered": M.ratio(len(right), len(answered)), "abstained on a yes": len(abstained_yes)}


def main(argv):
    tools = Tools(Policy())
    _, postings = corpus.load(tools)
    labels = M.load_labels(tools)
    out = {"filter": {}, "claude": {}}
    base = {p["key"]: F.evaluate(p)["verdict"] for p in postings}
    print("FILTER CHANGES (precision / recall of keep; held-out decides)")
    for name, change in FILTER_CHANGES.items():
        ev = evaluate_with(change)
        results, errors = M.measure(ev, postings, labels)
        flips = sum(ev(p)["verdict"] != base[p["key"]] for p in postings)
        row = {r["set"]: r for r in results if r["set"].endswith("/ both")}
        out["filter"][name] = {"held-out": row["held-out / both"], "tuning": row["tuning / both"],
                               "verdicts changed in the whole corpus": flips}
        h, t = row["held-out / both"], row["tuning / both"]
        print(f"  {name:44} held-out P {h['precision']:16} R {h['recall']:16} | tuning P {t['precision']:12} "
              f"| corpus flips {flips}")
    print("\nCLAUDE CHANGES (kept postings only; coverage and accuracy on answered)")
    variants = {"C0 base prompt": ("base", C.ABSTAIN_ON), "C0' base prompt, second run": ("base-rerun", C.ABSTAIN_ON),
                "C1 loose-quote wording": ("loose-quote", C.ABSTAIN_ON),
                "C2 title-only context": ("title-only", C.ABSTAIN_ON),
                "C3 no-field-names wording": ("no-field-names", C.ABSTAIN_ON),
                "A1 abstain on role/location only": ("base", ("role", "location"))}
    for name, (variant, abstain_on) in variants.items():
        answers = claim_answers(tools, variant, abstain_on)
        checked = list(__import__("csv").DictReader(
            tools.read_text(f"state/claims/{variant}_checked.csv").splitlines()))
        quoted = [r for r in checked if r["claude_status"] in ("supported", "contradicted")]
        found = sum(r["quote_found"] == "yes" for r in quoted)
        out["claude"][name] = {"held-out": score_answers(answers, labels, "held-out"),
                               "tuning": score_answers(answers, labels, "tuning"),
                               "quotes found": M.ratio(found, len(quoted)),
                               "answered, all 12 kept": sum(a != "I cannot tell" for a in answers.values())}
        h, t = out["claude"][name]["held-out"], out["claude"][name]["tuning"]
        print(f"  {name:34} held-out coverage {h['coverage']:16} acc {h['accuracy on answered']:16} | "
              f"tuning coverage {t['coverage']:16} acc {t['accuracy on answered']:16} | quotes found "
              f"{out['claude'][name]['quotes found']}")
    tools.write_text("state/measure/changes.json", json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
