"""A fresh held-out set (JS3 step 5) from one filter run, made BEFORE any change to the filter is measured.

The rule, with a recorded seed (default 2026112103, a new one: the audit used 20261121 and 20261122, the claims kit
2026112102):
  1. The pools: the run's kept postings and its rejected postings. A posting the filter could not judge at all ("I
     cannot tell") is in neither.
  2. Left out of both pools: every posting on the same run's audit cards (js3/audit/<run id>/sealed/answers.json, of
     which only the board and posting id are read), every posting on the run's shortlist (labeled claim by claim in
     js3/claims/<run id>/), and every other posting with the same board and normalized title (FILTER.md Section 6,
     item 7) as one of those: a copy of the same job in another place, which the audit or the claims kit has shown.
  3. Each pool is sorted by board and posting id, and a uniform random sample is drawn from it with
     random.Random(seed): 15 kept postings, then 15 rejected postings. A pool smaller than its sample is refused.
  4. The 30 cards are shuffled with random.Random(seed + 1), so a card's number says nothing about its pool.

Each card is tools/audit_kit.py's blind fact card: the posting's facts, never the filter's fate, rule or score. The
answers (card -> pool, fate, deciding rule, failed rules, score) go to sealed/answers.json, whose SHA-256 is written in
README.md, so the agreement can be computed after the verdicts and the file checked untouched. Chapter 9: a held-out set
is touched once. Aravind's verdicts in VERDICTS.md are committed before any change is measured on this set; the audit's
verdicts are development data and never go into it.

Usage (from the repo root):
  python3 tools/heldout_kit.py js3/filter-run/<run id> [--audit js3/audit/<run id>/sealed/answers.json]
                               [--seed N] [--out js3/heldout]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(TOOLS))

import audit_kit  # noqa: E402
from claims_kit import earliest_start  # noqa: E402
from job_agent import filter as flt  # noqa: E402

DEFAULT_SEED = 2026112103
N_KEPT = 15
N_REJECTED = 15
POOLS = ("kept", "rejected")


def left_out(records: list, keys: set) -> set:
    """The (board, id) of the given postings and of every posting with the same board and normalized title."""
    titles = {(r["board"], flt.normalized_title(r["title"])) for r in records if (r["board"], r["id"]) in keys}
    return {(r["board"], r["id"]) for r in records
            if (r["board"], r["id"]) in keys or (r["board"], flt.normalized_title(r["title"])) in titles}


def draw(records: list, excluded: set, seed: int, n_kept: int = N_KEPT, n_rejected: int = N_REJECTED) -> list:
    """[(pool, record)] by the written rule above: kept first, then rejected. Deterministic for a seed and records."""
    rng = random.Random(seed)
    order = sorted(records, key=lambda r: (r["board"], str(r["id"])))
    out = []
    for pool, n in zip(POOLS, (n_kept, n_rejected)):
        candidates = [r for r in order if r["fate"] == pool and (r["board"], r["id"]) not in excluded]
        if len(candidates) < n:
            raise SystemExit(f"only {len(candidates)} {pool} postings are left to draw from, fewer than {n}")
        out += [(f"random {pool}", r) for r in rng.sample(candidates, n)]
    return out


def build(run_dir: Path, out_root: Path, audit: Path = None, seed: int = DEFAULT_SEED, n_kept: int = N_KEPT,
          n_rejected: int = N_REJECTED) -> Path:
    run_dir = Path(run_dir)
    data = json.loads((run_dir / "verdicts.json").read_text(encoding="utf-8"))
    run_id = data["meta"]["run_id"]
    audit = Path(audit) if audit else REPO / "js3" / "audit" / run_id / "sealed" / "answers.json"
    if not audit.exists():
        raise SystemExit(f"{audit} not found: a held-out set must leave out the audit's postings")
    audit_keys = {(a["board"], a["id"]) for a in json.loads(audit.read_text(encoding="utf-8"))["answers"]}
    short_keys = {(k["board"], k["id"]) for k in data["shortlist"]}
    records = data["records"]
    excluded = left_out(records, audit_keys | short_keys)
    drawn = draw(records, excluded, seed, n_kept, n_rejected)
    random.Random(seed + 1).shuffle(drawn)
    out = Path(out_root) / run_id
    if out.exists():
        raise SystemExit(f"{out} already exists; a held-out set is made once, before any verdict")
    postings = {key: posting for key, (posting, _) in audit_kit.saved_postings(data).items()}
    rules = flt.load_rules(version=data["meta"].get("filter_version", "1.0"))  # the run's own version
    cards, answers = [], []
    for n, (pool, r) in enumerate(drawn, 1):
        cards.append(audit_kit.card(n, postings[(r["board"], r["id"])], r["board"], rules))
        answers.append({"card": n, "board": r["board"], "id": r["id"], "title": r["title"], "pool": pool,
                        "fate": r["fate"], "deciding_rule": r["deciding_rule"], "failed_rules": r["failed_rules"],
                        "score": r["score"]})
    sealed = json.dumps({"kit": "held-out", "filter_run": run_id, "seed": seed, "answers": answers}, indent=1,
                        ensure_ascii=False) + "\n"
    (out / "sealed").mkdir(parents=True)
    (out / "sealed" / "answers.json").write_text(sealed, encoding="utf-8")
    digest = hashlib.sha256(sealed.encode("utf-8")).hexdigest()
    (out / "CARDS.md").write_text(f"# Held-out cards, filter run {run_id}\n\n{len(cards)} cards. Each shows the "
                                  "posting's facts only; nothing on a card says what the filter decided.\n\n"
                                  + "\n".join(cards), encoding="utf-8")
    sheet = ["# My verdicts, held-out set", "", "One row per card in CARDS.md. Verdict: **Keep** (worth Jane's time), "
             "**Reject** (not for Jane), or **?** (the card does not give enough to decide). The note is one short "
             "line: why.", "", "| Card | Keep / Reject / ? | Note |", "|---|---|---|"]
    sheet += [f"| {n:02} | | |" for n in range(1, len(cards) + 1)]
    (out / "VERDICTS.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    counts = {}
    for pool in POOLS:
        everyone = [r for r in records if r["fate"] == pool]
        named = sum(1 for r in everyone if (r["board"], r["id"]) in audit_keys | short_keys)
        copies = sum(1 for r in everyone if (r["board"], r["id"]) in excluded) - named
        counts[pool] = (len(everyone), named, copies, len(everyone) - named - copies)
    facts = {"run_id": run_id, "seed": seed, "digest": digest, "audit": _shown(audit), "n_audit": len(audit_keys),
             "n_short": len(short_keys), "n_cannot": sum(1 for r in records if r["fate"] == "cannot_tell"),
             "drawn": {"kept": n_kept, "rejected": n_rejected}, "counts": counts}
    (out / "README.md").write_text(readme(facts), encoding="utf-8")
    (out / "INSTRUCTIONS.md").write_text(instructions(flt.load_profile(), len(cards)), encoding="utf-8")
    return out


def readme(f: dict) -> str:
    rows = [f"| {pool} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | {f['drawn'][pool]} |" for pool, c in f["counts"].items()]
    total = sum(f["drawn"].values())
    return "\n".join([
        f"# A fresh held-out set, filter run {f['run_id']}", "",
        f"Made by `tools/heldout_kit.py` (Claude Code, at Aravind's request) from `js3/filter-run/{f['run_id']}/`, "
        "before any change to the filter was measured. It is for JS3's one-change experiments: each change to one "
        f"object is measured on these {total} postings against Aravind's verdicts.", "",
        "## The rule this set keeps (the book, chapter 9)", "",
        "A held-out set is touched once. Once it guides a choice (a word list, a weight, the cutoff, a decision to "
        "keep going), it has become development data, and its next use is no longer independent.", "",
        "- The verdicts in VERDICTS.md are committed before any change is measured on this set.",
        f"- The audit's verdicts (`js3/audit/{f['run_id']}/`) are development data: they will be used to change the "
        f"filter. They never go into this set, and none of the audit's {f['n_audit']} postings is in it, nor any copy "
        "of one.",
        "- If a result on this set leads to a change of the filter, this set becomes development data from then on. "
        "That is written here with the date, and a later claim about a change needs a new held-out set.", "",
        "## How it was drawn", "",
        f"Seed **{f['seed']}**, a new one (the audit used 20261121 and 20261122), and the card order shuffled with "
        f"seed {f['seed'] + 1}. The rule is in the tool's docstring:", "",
        f"1. The pools: the run's kept postings and its rejected postings (its {f['n_cannot']} \"I cannot tell\" "
        "posting is in neither).",
        f"2. Left out: the {f['n_audit']} audit postings (only their board and posting id were read from "
        f"`{f['audit']}`), the {f['n_short']} shortlisted postings, and every other posting with the same board and "
        "normalized title as one of those (a copy of the same job in another place).",
        f"3. From what is left, sorted by board and posting id, a uniform random sample: {f['drawn']['kept']} kept "
        f"postings, then {f['drawn']['rejected']} rejected postings.", "",
        "| Pool | In the run | Audit or shortlist | Same-title copies | Left to draw from | Drawn |",
        "|---|---:|---:|---:|---:|---:|"] + rows + ["",
        "Which card came from which pool, and what the filter decided, is in `sealed/answers.json` (SHA-256 "
        f"`{f['digest']}`). It is opened only after VERDICTS.md is committed; the hash shows it was not changed.", "",
        "## What this set may claim", "",
        f"Two separate random samples from one day's saved answers of three boards: {f['drawn']['kept']} of "
        f"{f['counts']['kept'][3]} kept postings and {f['drawn']['rejected']} of {f['counts']['rejected'][3]} "
        "rejected postings. Agreement is stated for each pool on its own, with its bound. The pools are drawn "
        f"equally, not in proportion to the run ({f['counts']['kept'][0]} kept, {f['counts']['rejected'][0]} "
        "rejected), so one rate over all postings would have to weight them, and the postings left out (the audit's, "
        "the shortlist's and their copies) are not covered.", ""])


def instructions(profile: dict, n_cards: int) -> str:
    prefs = profile["preferences"]
    areas = ", ".join(prefs["regions"] + prefs["cities"])
    remote = ", ".join(f'"{r}"' for r in prefs["remote_locations"])
    earliest = earliest_start(profile)
    return "\n".join([
        "# How to judge the held-out cards", "",
        "1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of "
        "whether the posting is worth Jane's time, not by FILTER.md's rules (this set measures changes to those "
        "rules, so it cannot use them as its answer key).",
        f"2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in {earliest} and will "
        f"need H-1B sponsorship later; she has {profile['experience']['full_time_years']} years of full-time "
        f"experience; she wants full-time backend or software engineering work in {areas}, or US remote ({remote}).",
        "3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted "
        "on its own, never as a mistake.",
        "4. Do not open `sealed/answers.json` until your verdicts are committed, and commit them before any change to "
        "the filter is measured on this set (chapter 9: a held-out set is touched once). After that, each one-change "
        f"experiment runs the changed filter on these {n_cards} postings and compares its keeps and rejects with your "
        "verdicts.", ""])


def _shown(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make a fresh held-out set from one filter run.")
    parser.add_argument("run", type=Path, help="a filter run folder (js3/filter-run/<run id>)")
    parser.add_argument("--audit", type=Path, default=None,
                        help="the same run's audit answers (default js3/audit/<run id>/sealed/answers.json)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=REPO / "js3" / "heldout")
    args = parser.parse_args(argv)
    out = build(args.run, args.out, args.audit, args.seed)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
