"""The reject audit's kit (JS3 step 2), made from one filter run BEFORE any hand verdict exists.

The sample, by a written rule and a recorded seed:
  1. RANDOM REJECTS: a uniform random sample of rejected postings (default 30), the only part that supports a rate.
  2. CLOSE CALLS (default 15): kept postings scoring one topic group either side of the cutoff (55 or 60), drawn at
     random (default 8); then rejected postings that failed exactly one hard rule: one drawn at random for each rule
     that has such postings, then more drawn at random from all of them, up to the rest (default 7).
  3. KEPT SAMPLE: a uniform random sample of kept postings not already drawn (default 10).
No posting is drawn twice. The cards are shuffled with the same seed, so a card's number says nothing about its group.

Each card shows the posting's facts and never the filter's fate, rule or score: id, board, title, link, locations,
employment type, date, every sentence with a number of years, every start sentence, every status sentence, every
sentence with a topic word and an action word (computed for every card, so their presence reveals nothing), and the
first words of the description. The answers (card -> group, fate, deciding rule, score) go to sealed/answers.json,
whose SHA-256 is written in SAMPLE.md, so the agreement can be computed after the verdicts and checked untouched.

Usage (from the repo root):
  python3 tools/audit_kit.py js3/filter-run/<run id> [--seed N] [--out js3/audit]
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import filter as flt  # noqa: E402
from job_agent import providers  # noqa: E402
from job_agent.rule import YEARS, _flat, _has_word  # noqa: E402

DEFAULT_SEED = 20261121
STATUS_WORDS = ("citizen", "U.S. person", "US person", "clearance", "green card", "permanent resident", "sponsor",
                "sponsorship", "visa", "export control", "authorized to work", "work authorization", "ITAR")
FIRST_WORDS = 150
# The filter's sentence splitter ends a sentence after these (a known v1.1 item). On 2026-11-22 that hid
# "U.S. Person Required" from audit card 17, a line R5 had read, so cards keep these whole: cards show facts.
ABBREVIATIONS = ("U.S.", "e.g.", "i.e.")


def card_sentences(text: str) -> list:
    """The description split for a card: the filter's own splitter, but never inside U.S., e.g. or i.e."""
    guarded = text or ""
    for i, abbr in enumerate(ABBREVIATIONS):
        guarded = guarded.replace(abbr, f"\x00{i}\x00")
    sentences, _ = flt.split_sentences(guarded)
    out = []
    for s in sentences:
        for i, abbr in enumerate(ABBREVIATIONS):
            s = s.replace(f"\x00{i}\x00", abbr)
        out.append(s)
    return out


def draw(records: list, seed: int, n_random: int = 30, n_close_kept: int = 8, n_close_rejected: int = 7,
         n_kept: int = 10) -> list:
    """[(group, record)] by the written rule above. Deterministic for a given seed and records."""
    rng = random.Random(seed)
    order = sorted(records, key=lambda r: (r["board"], str(r["id"])))
    rejected = [r for r in order if r["fate"] == "rejected"]
    kept = [r for r in order if r["fate"] == "kept"]
    taken, out = set(), []

    def take(group, pool, n):
        pool = [r for r in pool if (r["board"], r["id"]) not in taken]
        for r in rng.sample(pool, min(n, len(pool))):
            taken.add((r["board"], r["id"]))
            out.append((group, r))

    take("random reject", rejected, n_random)
    take("close call: kept near the cutoff", [r for r in kept if r["score"] in (55, 60)], n_close_kept)
    one_rule = [r for r in rejected if len(r["failed_rules"]) == 1]
    before = len(out)
    for rule in flt.HARD_RULES:
        take("close call: failed one rule", [r for r in one_rule if r["failed_rules"] == [rule]], 1)
    take("close call: failed one rule", one_rule, max(0, n_close_rejected - (len(out) - before)))
    take("kept sample", kept, n_kept)
    return out


def card(number: int, posting: dict, board: str, rules: dict) -> str:
    sentences, _ = flt.split_sentences(posting.get("descriptionPlain") or "")  # the filter's own split: topics
    shown = card_sentences(posting.get("descriptionPlain") or "")  # whole lines for the facts a person reads
    flat = [re.sub(r"^[-•*–]\s+", "", _flat(s).strip()) for s in shown]  # the posting's own bullets go
    years = [s for s in flat if YEARS.search(s)]
    start = [s for s in flat if _has_word(s, "start") or any(p.lower() in s.lower() for p in rules["start_phrases"])]
    # Every line R5's own phrases match (as R5 reads them: lower case, anywhere), so a card never hides what R5 read.
    r5 = [p.lower() for key in ("status_us_person_phrases", "status_sponsorship_phrases") for p in rules.get(key, [])]
    status = [s for s in flat if any(_has_word(s, w) for w in STATUS_WORDS) or any(p in s.lower() for p in r5)]
    topics = flt.topic_groups(sentences, rules)
    words = (posting.get("descriptionPlain") or "").split()
    places = [t for t, _ in flt._places(posting) if isinstance(t, str) and t.strip()]

    def block(title, items):
        return [f"**{title}:**", ""] + ([f"- {i}" for i in items] if items else ["- none"]) + [""]

    lines = [f"## Card {number:02}", "", f"**{posting.get('title') or '(no title)'}**", "",
             f"- Board: {board}", f"- Posting id: `{posting.get('id')}`", f"- Link: {posting.get('jobUrl')}",
             f"- Locations: {'; '.join(places) or 'none listed'}",
             f"- Employment type: {posting.get('employmentType') or 'not stated'}",
             f"- Posted: {posting.get('publishedAt') or 'no date'}", ""]
    lines += block("Sentences with a number of years", years)
    lines += block("Start sentences", start)
    lines += block("Sentences about status, sponsorship or clearance", status)
    lines += block("Sentences with a topic word and an action word",
                   [f"({g}) {t['sentence']}" for g, t in topics.items()])
    lines += [f"**The first {min(FIRST_WORDS, len(words))} words of the description:**", "",
              "> " + " ".join(words[:FIRST_WORDS]) + (" ..." if len(words) > FIRST_WORDS else ""), "", "---", ""]
    return "\n".join(lines)


def saved_postings(data: dict) -> dict:
    """{(board, posting id): (the posting in the filter's fields, the board's own job as saved)} for one filter run.

    Read from each board's saved answer, which must still match the SHA-256 the filter run recorded. Also used by
    tools/claims_kit.py (which quotes the board's own fields) and tools/heldout_kit.py.
    """
    out = {}
    for source in data["meta"]["sources"]:
        if not source.get("run"):
            continue
        path = REPO / source["file"] if not Path(source["file"]).is_absolute() else Path(source["file"])
        body = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
        if hashlib.sha256(body).hexdigest() != source["sha256"]:
            raise SystemExit(f"{path} no longer matches the SHA-256 the filter run recorded")
        raw_jobs = providers._jobs(source["system"], json.loads(body.decode("utf-8")))
        for posting, raw in zip(providers.read(source["system"], 200, body), raw_jobs):
            out[(source["key"], posting["id"])] = (posting, raw)
    return out


def build(run_dir: Path, out_root: Path, seed: int = DEFAULT_SEED, **sizes) -> Path:
    run_dir = Path(run_dir)
    data = json.loads((run_dir / "verdicts.json").read_text(encoding="utf-8"))
    rules = flt.load_rules(version=data["meta"].get("filter_version", "1.0"))  # the run's own version
    postings = {key: posting for key, (posting, _) in saved_postings(data).items()}
    drawn = draw(data["records"], seed, **sizes)
    random.Random(seed + 1).shuffle(drawn)
    out = Path(out_root) / data["meta"]["run_id"]
    if out.exists():
        raise SystemExit(f"{out} already exists; the kit is made once, before any verdict")
    (out / "sealed").mkdir(parents=True)
    cards, answers = [], []
    for n, (group, r) in enumerate(drawn, 1):
        cards.append(card(n, postings[(r["board"], r["id"])], r["board"], rules))
        answers.append({"card": n, "board": r["board"], "id": r["id"], "title": r["title"], "group": group,
                        "fate": r["fate"], "deciding_rule": r["deciding_rule"], "failed_rules": r["failed_rules"],
                        "score": r["score"]})
    sealed = json.dumps({"filter_run": data["meta"]["run_id"], "seed": seed, "answers": answers}, indent=1,
                        ensure_ascii=False) + "\n"
    (out / "sealed" / "answers.json").write_text(sealed, encoding="utf-8")
    digest = hashlib.sha256(sealed.encode("utf-8")).hexdigest()
    counts = {}
    for group, _ in drawn:
        counts[group] = counts.get(group, 0) + 1
    (out / "CARDS.md").write_text(f"# Audit cards, filter run {data['meta']['run_id']}\n\n{len(cards)} cards. Each "
                                  "shows the posting's facts only; nothing on a card says what the filter decided.\n\n"
                                  + "\n".join(cards), encoding="utf-8")
    sheet = ["# My verdicts", "", "One row per card in CARDS.md. Verdict: **Keep** (worth Jane's time), **Reject** "
             "(not for Jane), or **?** (the card does not give enough to decide). The note is one short line: why.", "",
             "| Card | Keep / Reject / ? | Note |", "|---|---|---|"]
    sheet += [f"| {n:02} | | |" for n in range(1, len(cards) + 1)]
    (out / "VERDICTS.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    (out / "SAMPLE.md").write_text("\n".join([
        f"# The audit sample, filter run {data['meta']['run_id']}", "",
        f"Drawn by `tools/audit_kit.py` with seed **{seed}** (card order shuffled with seed {seed + 1}), before any "
        "verdict existed. The rule is in the tool's docstring:", "",
        "1. Random rejects: a uniform random sample of the rejected postings (the only part that supports a rate).",
        "2. Close calls: kept postings scoring 55 or 60 (one topic group either side of the 60 cutoff), drawn at random; "
        "then rejected postings that failed exactly one hard rule, one at random for each rule that has such postings, "
        "then more at random from all of them.", "3. Kept sample: a uniform random sample of the other kept postings.",
        "", "| Group | Cards |", "|---|---:|"] + [f"| {g} | {c} |" for g, c in counts.items()] + [
        f"| total | {len(drawn)} |", "",
        f"Which card belongs to which group, and what the filter decided, is in `sealed/answers.json` (SHA-256 "
        f"`{digest}`). It is opened only after the verdicts in VERDICTS.md are committed; the hash shows it was not "
        "changed.", ""]), encoding="utf-8")
    (out / "INSTRUCTIONS.md").write_text("\n".join([
        "# How to judge the cards", "",
        "1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of "
        "whether the posting is worth Jane's time, not by FILTER.md's rules (the audit checks those rules, so it "
        "cannot use them as the answer key).",
        "2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in May 2027 and will need "
        "H-1B sponsorship later; she has 3 years of full-time experience; she wants full-time backend or software "
        "engineering work in California, Austin, Boston or Cambridge, New York, Seattle, Bellevue or Redmond, or US "
        "remote.",
        "3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted "
        "on its own, never as a mistake.",
        "4. Do not open `sealed/answers.json` until your verdicts are committed. After that, Claude Code computes the "
        "agreement: a miss is a posting the filter rejected that you marked Keep; a wrong keep is one it kept that you "
        "marked Reject. The random rejects give the miss count with its exact bound; the close calls and the kept "
        "sample show where the boundary is and what got through.", ""]), encoding="utf-8")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make the reject audit's kit from one filter run.")
    parser.add_argument("run", type=Path, help="a filter run folder (js3/filter-run/<run id>)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=REPO / "js3" / "audit")
    args = parser.parse_args(argv)
    out = build(args.run, args.out, args.seed)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
