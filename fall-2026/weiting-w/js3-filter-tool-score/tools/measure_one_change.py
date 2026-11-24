"""Measure each one-object change against the held-out hand labels.

    python3 tools/measure_one_change.py

`reports/one-change-measurements.txt` reports what each change does to the
bucket counts. That is a description of the filter, not a measurement of
whether the change is an improvement -- for that the change has to be scored
against labels it did not see.

So: the same train/held-out split as the threshold refit (seed 20261123,
`tools/analyse_audit.py`), and for each change, agreement with my labels on
the **held-out** half only. The training half is reported too, and only so
that the gap between the two is visible.

The split is small. 48 labels, 42 decided, and the held-out half is what is
left after halving. Every number here is an agreement count on that half and
nothing else -- see FILTER.md §6.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod, pipeline, score as scorer, sections  # noqa: E402
from jobfilter.corpus import Posting  # noqa: E402

SPLIT_SEED = 20261123


def labelled_split():
    labels = json.loads(
        (ROOT / "audit" / "labels-weiting.json").read_text(encoding="utf-8")
    )["labels"]
    decided = {k: v == "yes" for k, v in labels.items() if v in ("yes", "no")}
    ids = sorted(decided)
    rng = random.Random(SPLIT_SEED)
    rng.shuffle(ids)
    half = len(ids) // 2
    return decided, set(ids[:half]), set(ids[half:])


def agreement(decisions, decided, subset):
    hit = total = 0
    for d in decisions:
        i = d.posting.identity
        if i not in subset or i not in decided:
            continue
        total += 1
        hit += int((d.bucket == pipeline.SHORTLISTED) == decided[i])
    return hit, total


def run(postings, persona):
    return pipeline.run(postings, persona)


def main() -> int:
    postings = corpus_mod.load()
    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    decided, train, held = labelled_split()

    rows = []

    def record(name, decisions, note=""):
        th, tt = agreement(decisions, decided, train)
        hh, ht = agreement(decisions, decided, held)
        rows.append((name, f"{th}/{tt}", f"{hh}/{ht}", note))

    record("baseline  F-v2 / S-v5 / T=6", run(postings, persona))

    # The two trivial filters. Without these the baseline's score is
    # meaningless: a corpus where almost everything is a `no` rewards a filter
    # that keeps almost nothing, whatever it knows.
    def trivial(keep_everything: bool):
        base = run(postings, persona)
        for d in base:
            d.bucket = pipeline.SHORTLISTED if keep_everything else pipeline.GATED
        return base

    record("trivial: reject everything", trivial(False))
    record("trivial: keep everything", trivial(True))

    # 1. the filter file: take `infrastructure` back out (undo A5)
    orig = scorer.SIGNALS["S1_core"]
    scorer.SIGNALS["S1_core"] = (
        tuple(w for w in orig[0] if w != "infrastructure"), orig[1], orig[2])
    scorer._COMPILED["S1_core"] = [
        (w, scorer._pattern(w)) for w in scorer.SIGNALS["S1_core"][0]]
    record("filter file: drop `infrastructure` (undo A5)", run(postings, persona))
    scorer.SIGNALS["S1_core"] = orig
    scorer._COMPILED["S1_core"] = [(w, scorer._pattern(w)) for w in orig[0]]

    # 2. the section weights: optional counts in full (undo A4)
    saved = dict(scorer.SECTION_WEIGHT)
    scorer.SECTION_WEIGHT[sections.OPTIONAL] = 1.0
    record("section weights: optional x1 (undo A4)", run(postings, persona))
    scorer.SECTION_WEIGHT.update(saved)

    # 3. a setting: score the whole record (wrong version W3)
    alt = [
        Posting(**{**p.__dict__,
                   "body": json.dumps(p.raw, ensure_ascii=False) if p.raw else p.body,
                   "body_fields": ("<whole record>",)})
        for p in postings
    ]
    record("setting: score the whole JSON record (W3)", run(alt, persona))

    # 4. a setting: drop Lever's `lists`
    alt = [
        Posting(**{**p.__dict__, "body": p.body.split("\n\n")[0],
                   "body_fields": ("descriptionPlain",)})
        if p.provider == "lever" and p.body else p
        for p in postings
    ]
    record("setting: drop Lever's `lists` from the body", run(alt, persona))

    # 5. the threshold
    for t in (4, 5, 7, 8):
        saved_t = scorer.THRESHOLD
        scorer.THRESHOLD = t
        record(f"threshold: T={t}", run(postings, persona))
        scorer.THRESHOLD = saved_t

    width = max(len(r[0]) for r in rows)
    out = [
        "One object at a time, measured against the held-out hand labels.",
        "",
        f"Split seed {SPLIT_SEED}, the same one tools/analyse_audit.py uses.",
        f"{len(decided)} decided labels: {len(train)} train, {len(held)} held out.",
        "Agreement = the filter's keep/drop matching my yes/no on that posting.",
        "",
        f"{'change':{width}}   train    held out",
        f"{'-' * width}   -----    --------",
    ]
    for name, tr, ho, _ in rows:
        out.append(f"{name:{width}}   {tr:>6}   {ho:>8}")
    yes_n = sum(1 for i in held if decided.get(i))
    out += [
        "",
        f"Of the {len(held)} held-out postings I labelled, {yes_n} are `yes` and "
        f"{len(held) - yes_n} are `no`.",
        "That is why the two trivial rows are in the table: on a corpus this",
        "lopsided, 'reject everything' is a strong-looking filter that knows",
        "nothing, and any score has to be read against it rather than against 0.",
        "",
        "Read the held-out column only. The training column is here so the gap",
        "between the two is visible, not because it means anything: every change",
        "below was chosen by me after looking at the corpus, so the training",
        "half is the half that cannot surprise me.",
        "",
        "A held-out half this size cannot separate changes that differ by one or",
        "two postings. Nothing here is a rate; each entry is a count out of the",
        "held-out half (FILTER.md §6).",
    ]
    text = "\n".join(out) + "\n"
    (ROOT / "reports" / "one-change-heldout.txt").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
