"""A fresh blind set for FILTER.md v1.1, made on 2026-11-24 before any verdict: postings Aravind has never been shown,
most of them ones whose recommendation v1.1 changes, so his verdicts test the calls he made after the held-out results.

Why a new set: the held-out set became development data on 2026-11-22, when the cutoff of 50, the export-control
penalty and dropping "build systems" were chosen from its results (js3/heldout/2026-11-21T044414Z/CHANGES.md). A claim
that v1.1 holds needs labels that played no part in choosing it (the book, chapter 9).

The rule, with a recorded seed (default 2026112401, a new one: the audit used 20261121 and 20261122, the claims kit
2026112102 and the held-out set 2026112103):
  1. Records: the v1.1 filter run (js3/filter-run/2026-11-22T084738Z) and, for v1.0's scores, the v1.0 run of the same
     saved answers (js3/filter-run/2026-11-21T044414Z); the two must have the same postings and the same fates.
     "Recommended" means kept with a score at or above the version's cutoff (FILTER.md: v1.0 60, v1.1 50). Two
     counterfactual scores come from judging every saved posting again with v1.1 minus one of its calls: without the
     export-control penalty, and with "build systems" back in its topic group.
  2. Left out: every posting already shown to Aravind on a card, in a claim or on a shortlist: the audit's and the
     held-out set's postings (only the board and posting id are read from their sealed answers), both runs'
     shortlists, the two saved postings the MCP runs scored (tools/mcp_client.py), and every other posting with the
     same board and normalized title as one of those.
  3. Strata, from what is left, each sorted by board and posting id:
       A  "v1.1 adds": kept, recommended by v1.1, not by v1.0.                                       12 cards
       B  "the penalty holds back": kept, not recommended by v1.1, recommended without the penalty.   every one
       C  "both recommend": recommended by v1.0 and v1.1 (a control).                                 3 cards
       D  "both reject": rejected, for exactly one rule (a control near the line).                    2 cards
     One random.Random(seed) puts each stratum in a random order, A first, and the first postings are taken, skipping
     any whose board and normalized title is already on a card, so no job appears twice.
     The postings whose v1.1 recommendation changes with "build systems" back are counted; if there are none, no card
     can test that call, and the README says so.
  4. The cards are shuffled with random.Random(seed + 1), so a card's number says nothing about its stratum.

Each card is tools/audit_kit.py's blind fact card (with the card fix of 2026-11-22), built with the run's own FILTER.md
version: the posting's facts, never a fate, a rule or a score. The answers go to sealed/answers.json, whose SHA-256 is
in README.md. PREDICTIONS.md (written by this tool) says before any verdict what each outcome would mean, and
tools/score_fresh.py, committed with the kit, scores it once the verdicts are committed.

Usage (from the repo root):
  python3 tools/fresh_kit.py [--run js3/filter-run/2026-11-22T084738Z] [--v10 js3/filter-run/2026-11-21T044414Z]
                             [--seed N] [--out js3/fresh]
"""

from __future__ import annotations

import argparse
import copy
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

DEFAULT_SEED = 2026112401
V11_RUN = REPO / "js3" / "filter-run" / "2026-11-22T084738Z"
V10_RUN = REPO / "js3" / "filter-run" / "2026-11-21T044414Z"
# The two saved postings the MCP runs scored (tools/mcp_client.py, KEPT and REJECTED); Aravind has read their records.
MCP_POSTINGS = {("ashby-openai", "f3ddd41c-541f-485e-90d6-86c26e018e9f"), ("greenhouse-verkada", "5283655007")}
STRATA = ("A", "B", "C", "D")
NAMES = {"A": "v1.1 adds", "B": "the penalty holds back", "C": "both recommend", "D": "both reject"}
SIZES = {"A": 12, "B": None, "C": 3, "D": 2}  # None: every posting in the stratum

# Claude Code's predictions, fixed before any verdict; tools/score_fresh.py checks them with these same numbers.
PREDICT_A_KEEPS = 9        # Keep on at least 9 of the 12 A cards
PREDICT_B_UNSURE = 2       # "?" on at least 2 of the B cards
PREDICT_CONTROLS = "all"   # Keep on every C card and Reject on every D card


def without_penalty(rules: dict) -> dict:
    out = copy.deepcopy(rules)
    out["ranking"].pop("caution_penalty", None)
    return out


def with_build_systems(rules: dict, v10_rules: dict) -> dict:
    """v1.1 with "build systems" back where v1.0 had it; refused if the topic groups differ in anything else."""
    out = copy.deepcopy(rules)
    for group, words in v10_rules["topic_groups"].items():
        if [w for w in words if w != "build systems"] != rules["topic_groups"].get(group):
            raise SystemExit(f"topic group {group!r} differs between v1.0 and v1.1 in more than 'build systems'")
        out["topic_groups"][group] = list(words)
    return out


def recommended(fate: str, score, cutoff: int) -> bool:
    return fate == "kept" and score is not None and score >= cutoff


def left_out(records: list, keys: set) -> set:
    """The (board, id) of the given postings and of every posting with the same board and normalized title."""
    titles = {(r["board"], flt.normalized_title(r["title"])) for r in records if (r["board"], r["id"]) in keys}
    return {(r["board"], r["id"]) for r in records
            if (r["board"], r["id"]) in keys or (r["board"], flt.normalized_title(r["title"])) in titles}


def seen_keys(v11: dict, v10: dict, audit: Path, heldout: Path) -> set:
    keys = set(MCP_POSTINGS)
    for sealed in (audit, heldout):
        keys |= {(a["board"], a["id"]) for a in json.loads(Path(sealed).read_text(encoding="utf-8"))["answers"]}
    for data in (v11, v10):
        keys |= {(k["board"], k["id"]) for k in data["shortlist"]}
    return keys


def classify(v11: dict, v10: dict) -> dict:
    """{(board, id): row} for every posting: its stratum (or None) and every score the strata are read from."""
    rules = flt.load_rules(version=v11["meta"]["filter_version"])
    rules10 = flt.load_rules(version=v10["meta"].get("filter_version", "1.0"))
    if rules["version"] != "1.1":
        raise SystemExit(f"{v11['meta']['run_id']} is a FILTER.md {rules['version']} run, not v1.1")
    cut11, cut10 = rules["ranking"]["shortlist_min"], rules10["ranking"]["shortlist_min"]
    nopen, withbs = without_penalty(rules), with_build_systems(rules, rules10)
    postings = {key: p for key, (p, _) in audit_kit.saved_postings(v11).items()}
    old = {(r["board"], r["id"]): r for r in v10["records"]}
    jane = flt.load_profile()
    rows = {}
    for r in v11["records"]:
        key = (r["board"], r["id"])
        if key not in old or old[key]["fate"] != r["fate"]:
            raise SystemExit(f"{key}: the v1.0 and v1.1 runs differ in postings or fates; this rule assumes they do not")
        again = flt.judge(postings[key], jane, rules, key[0])
        if (again["fate"], again["score"]) != (r["fate"], r["score"]):
            raise SystemExit(f"{key}: judging again with v1.1 does not give the committed run's fate and score")
        s_np = flt.judge(postings[key], jane, nopen, key[0])["score"]
        s_bs = flt.judge(postings[key], jane, withbs, key[0])["score"]
        rec10 = recommended(r["fate"], old[key]["score"], cut10)
        rec11 = recommended(r["fate"], r["score"], cut11)
        rec_np = recommended(r["fate"], s_np, cut11)
        rec_bs = recommended(r["fate"], s_bs, cut11)
        if rec11 and not rec10:
            stratum = "A"
        elif r["fate"] == "kept" and not rec11 and rec_np:
            stratum = "B"
        elif rec11 and rec10:
            stratum = "C"
        elif r["fate"] == "rejected" and len(r["failed_rules"]) == 1:
            stratum = "D"
        else:
            stratum = None
        rows[key] = {"record": r, "stratum": stratum, "score_v10": old[key]["score"], "score_v11": r["score"],
                     "score_without_penalty": s_np, "score_with_build_systems": s_bs, "recommended_v10": rec10,
                     "recommended_v11": rec11, "recommended_without_penalty": rec_np,
                     "recommended_with_build_systems": rec_bs, "v11_drops": rec10 and not rec11,
                     "build_systems_moves": rec11 != rec_bs}
    return {"rows": rows, "cut10": cut10, "cut11": cut11, "rules": rules}


def draw(rows: dict, excluded: set, seed: int, sizes: dict = None) -> list:
    """[(stratum, key)] by the written rule above: A, B, C, D in turn. Deterministic for a seed and the rows."""
    sizes = dict(SIZES if sizes is None else sizes)
    rng = random.Random(seed)
    taken_titles, out = set(), []
    for s in STRATA:
        pool = sorted((k for k, v in rows.items() if v["stratum"] == s and k not in excluded),
                      key=lambda k: (k[0], str(k[1])))
        n = len(pool) if sizes[s] is None else sizes[s]
        picked = 0
        for key in rng.sample(pool, len(pool)):
            if picked == n:
                break
            title = (key[0], flt.normalized_title(rows[key]["record"]["title"]))
            if title in taken_titles:
                continue
            taken_titles.add(title)
            out.append((s, key))
            picked += 1
        if picked < n:
            raise SystemExit(f"stratum {s} has only {picked} distinct jobs left to draw from, fewer than {n}")
    return out


def build(out_root: Path, run_dir: Path = V11_RUN, v10_dir: Path = V10_RUN, seed: int = DEFAULT_SEED,
          audit: Path = None, heldout: Path = None, sizes: dict = None) -> Path:
    v11 = json.loads((Path(run_dir) / "verdicts.json").read_text(encoding="utf-8"))
    v10 = json.loads((Path(v10_dir) / "verdicts.json").read_text(encoding="utf-8"))
    run_id, run10 = v11["meta"]["run_id"], v10["meta"]["run_id"]
    audit = Path(audit) if audit else REPO / "js3" / "audit" / run10 / "sealed" / "answers.json"
    heldout = Path(heldout) if heldout else REPO / "js3" / "heldout" / run10 / "sealed" / "answers.json"
    for path in (audit, heldout):
        if not path.exists():
            raise SystemExit(f"{path} not found: a fresh set must leave out every posting already shown")
    out = Path(out_root) / run_id
    if out.exists():
        raise SystemExit(f"{out} already exists; a fresh set is made once, before any verdict")
    c = classify(v11, v10)
    rows = c["rows"]
    records = [v["record"] for v in rows.values()]
    seen = seen_keys(v11, v10, audit, heldout)
    excluded = left_out(records, seen)
    drawn = draw(rows, excluded, seed, sizes)
    random.Random(seed + 1).shuffle(drawn)
    postings = {key: p for key, (p, _) in audit_kit.saved_postings(v11).items()}
    cards, answers = [], []
    for n, (s, key) in enumerate(drawn, 1):
        v, r = rows[key], rows[key]["record"]
        cards.append(audit_kit.card(n, postings[key], key[0], c["rules"]))
        answers.append({"card": n, "board": key[0], "id": key[1], "title": r["title"], "stratum": s,
                        "stratum_name": NAMES[s], "fate": r["fate"], "deciding_rule": r["deciding_rule"],
                        "failed_rules": r["failed_rules"], "cautions": r["cautions"],
                        **{f: v[f] for f in ("score_v10", "score_v11", "score_without_penalty",
                                             "score_with_build_systems", "recommended_v10", "recommended_v11",
                                             "recommended_without_penalty")}})
    sealed = json.dumps({"kit": "fresh v1.1", "filter_run": run_id, "v10_run": run10, "seed": seed,
                         "cutoffs": {"v1.0": c["cut10"], "v1.1": c["cut11"]}, "answers": answers}, indent=1,
                        ensure_ascii=False) + "\n"
    (out / "sealed").mkdir(parents=True)
    (out / "sealed" / "answers.json").write_text(sealed, encoding="utf-8")
    digest = hashlib.sha256(sealed.encode("utf-8")).hexdigest()
    (out / "CARDS.md").write_text(f"# Fresh cards for FILTER.md v1.1, filter run {run_id}\n\n{len(cards)} cards. Each "
                                  "shows the posting's facts only; nothing on a card says what the filter decided.\n\n"
                                  + "\n".join(cards), encoding="utf-8")
    sheet = ["# My verdicts, fresh set for FILTER.md v1.1", "", "One row per card in CARDS.md. Verdict: **Keep** (worth "
             "Jane's time), **Reject** (not for Jane), or **?** (the card does not give enough to decide). The note is "
             "one short line: why.", "", "| Card | Keep / Reject / ? | Note |", "|---|---|---|"]
    sheet += [f"| {n:02} | | |" for n in range(1, len(cards) + 1)]
    (out / "VERDICTS.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    counts = {}
    for s in STRATA:
        everyone = [k for k, v in rows.items() if v["stratum"] == s]
        named = sum(1 for k in everyone if k in seen)
        copies = sum(1 for k in everyone if k in excluded) - named
        counts[s] = (len(everyone), named, copies, len(everyone) - named - copies, sum(1 for d in drawn if d[0] == s))
    facts = {"run_id": run_id, "run10": run10, "seed": seed, "digest": digest, "counts": counts, "n_cards": len(cards),
             "cut10": c["cut10"], "cut11": c["cut11"], "n_seen": len(seen),
             "v11_drops": sum(1 for v in rows.values() if v["v11_drops"]),
             "bs_moves": sum(1 for k, v in rows.items() if v["build_systems_moves"]),
             "bs_moves_left": sum(1 for k, v in rows.items() if v["build_systems_moves"] and k not in excluded)}
    (out / "README.md").write_text(readme(facts), encoding="utf-8")
    (out / "PREDICTIONS.md").write_text(predictions(facts), encoding="utf-8")
    (out / "INSTRUCTIONS.md").write_text(instructions(flt.load_profile(), len(cards)), encoding="utf-8")
    return out


def readme(f: dict) -> str:
    rows = [f"| {s}: {NAMES[s]} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} |" for s, c in f["counts"].items()]
    bs = ("No posting's v1.1 recommendation changes with \"build systems\" back (it moves only scores and ranks), so no "
          "card here can test that call." if f["bs_moves"] == 0 else
          f"{f['bs_moves']} postings' v1.1 recommendation changes with \"build systems\" back ({f['bs_moves_left']} of "
          "them never shown); they are not a stratum here, so this set does not test that call.")
    return "\n".join([
        f"# A fresh blind set for FILTER.md v1.1, filter run {f['run_id']}", "",
        "Made by `tools/fresh_kit.py` (Claude Code, at Aravind's request) on 2026-11-24, before any verdict, from "
        f"`js3/filter-run/{f['run_id']}/` (v1.1) and `js3/filter-run/{f['run10']}/` (v1.0, the same saved answers).",
        "", "## Why this set exists", "",
        "Aravind made v1.1's three calls (a cutoff of 50, 10 points off for an export-control line, no \"build "
        f"systems\") after seeing the held-out results, so the held-out set (`js3/heldout/{f['run10']}/`) became "
        "development data on 2026-11-22 and no longer tests them. This set holds postings he has never been shown, "
        "most of them ones whose recommendation v1.1 changes, so his verdicts can say whether the calls hold on new "
        "labels. The book, chapter 9: a held-out set is touched once.", "",
        "## How it was drawn", "",
        f"Seed **{f['seed']}**, a new one (the audit used 20261121 and 20261122, the claims kit 2026112102, the held-out "
        f"set 2026112103), and the card order shuffled with seed {f['seed'] + 1}. The full rule is in the tool's "
        "docstring. \"Recommended\" means kept with a score at or above the version's cutoff (v1.0: "
        f"{f['cut10']}, v1.1: {f['cut11']}).", "",
        f"Left out: the {f['n_seen']} postings already shown to Aravind (the audit's and the held-out set's cards, both "
        "runs' shortlists, which the claims kit and the reports show, and the two postings the MCP runs scored) and every "
        "other posting with the same board and normalized title as one of those.", "",
        "| Stratum | In the run | Already shown | Same-title copies | Left to draw from | Cards |",
        "|---|---:|---:|---:|---:|---:|"] + rows + ["",
        f"- A: kept, recommended by v1.1 and not by v1.0 (the cutoff moved from {f['cut10']} to {f['cut11']}).",
        "- B: kept, below v1.1's cutoff only because of the 10-point export-control penalty (recommended without it).",
        "- C and D are controls: recommended by both versions, and rejected by both for exactly one rule.",
        f"- {bs}",
        f"- Kept postings that v1.0 recommends and v1.1 does not: {f['v11_drops']}.", "",
        "Which card came from which stratum, and every score, is in `sealed/answers.json` (SHA-256 "
        f"`{f['digest']}`). It is opened only after VERDICTS.md is committed; the hash shows it was not changed. What "
        "each outcome would mean is in PREDICTIONS.md, written with the kit, and `tools/score_fresh.py` scores it.", "",
        "## What this set may claim", "",
        "Small random draws from strata of one day's saved answers of three boards, judged by one person. Each stratum "
        "is reported on its own, with its bound where it has one. It is not a rate for all postings, and it says "
        "nothing about live postings, other boards or other days. The filter runs' reports list kept postings with "
        "their scores and are public in this repo; Aravind has not studied them, but they were not hidden from him.", ""])


def predictions(f: dict) -> str:
    n = {s: f["counts"][s][4] for s in STRATA}
    return "\n".join([
        "# Predictions and how each outcome is read (written before any verdict)", "",
        "Written by Claude Code on 2026-11-24 with the kit, before Aravind judged any card. `tools/score_fresh.py` checks "
        "the predictions with the same numbers (they are constants in `tools/fresh_kit.py`). A \"?\" is counted on its "
        "own, never as a mistake, as in every other set.", "",
        f"## A, the cutoff of 50 ({n['A']} cards)", "",
        f"v1.1 recommends every A posting and v1.0 recommends none. A Keep is a card where v1.1's recommendation agrees "
        "with Aravind and v1.0's does not; a Reject is the reverse. The cutoff call holds on this set if his Keeps "
        "outnumber his Rejects. The bound reported is the exact one-sided 95% upper bound on v1.1's disagreements "
        "among the A cards he judged.", "",
        f"Prediction: Keep on at least {PREDICT_A_KEEPS} of the {n['A']} A cards (in the audit and the held-out set he "
        "kept every kept posting he judged). Held: at least that many. Partly: more Keeps than Rejects, but fewer. Not "
        "held: no more Keeps than Rejects.", "",
        f"## B, the export-control penalty ({n['B']} cards)", "",
        "v1.1 holds every B posting back from the shortlist; without the penalty they would be recommended. A Keep "
        "disagrees with the penalty. A Reject agrees with holding it back (and disagrees with the filter's keep). A ? "
        "says the card does not settle it, which is what a caution is for: the posting stays kept for a person to "
        "check, not recommended outright.", "",
        f"Prediction: ? on at least {PREDICT_B_UNSURE} of the {n['B']} B cards (he marked all three export-control "
        f"cards of the held-out set ?). Held: at least {PREDICT_B_UNSURE}. Partly: one. Not held: none.", "",
        f"## C and D, the controls ({n['C']} and {n['D']} cards)", "",
        "Both versions agree on these. A Reject on a C card or a Keep on a D card is a disagreement both versions "
        "share; it says nothing for or against v1.1's calls. Prediction: Keep on every C card and Reject on every D "
        "card. Held: all of them. Partly: all but one. Not held: more than one off.", "",
        "## \"build systems\"", "",
        "No card tests this call (README.md says why).", "",
        "## After the result", "",
        "If a result here leads to a change of FILTER.md, this set becomes development data from that date, and that "
        "is written in a CHANGES.md here. Anything Aravind says about a card after the answers are opened goes in "
        "AFTER-REVEAL.md and is reported beside the frozen result, never in place of it.", ""])


def instructions(profile: dict, n_cards: int) -> str:
    prefs = profile["preferences"]
    areas = ", ".join(prefs["regions"] + prefs["cities"])
    remote = ", ".join(f'"{r}"' for r in prefs["remote_locations"])
    return "\n".join([
        "# How to judge the fresh cards", "",
        "1. Open CARDS.md and VERDICTS.md side by side. Judge each card from the card alone, by your own sense of "
        "whether the posting is worth Jane's time, not by FILTER.md's rules (this set tests v1.1's calls, so it cannot "
        "use them as its answer key).",
        f"2. Jane (fictional) is an F-1 student, not a U.S. person, who can start full time in {earliest_start(profile)} "
        f"and will need H-1B sponsorship later; she has {profile['experience']['full_time_years']} years of full-time "
        f"experience; she wants full-time backend or software engineering work in {areas}, or US remote ({remote}).",
        "3. Write Keep, Reject or ? and one short line on why. Use ? when the card does not settle it; a ? is counted "
        "on its own, never as a mistake.",
        f"4. Do not open `sealed/answers.json` until your verdicts for all {n_cards} cards are committed. Then "
        "`python3 tools/score_fresh.py js3/fresh/<run id>` scores them once.", ""])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make the fresh blind set for FILTER.md v1.1.")
    parser.add_argument("--run", type=Path, default=V11_RUN, help="the v1.1 filter run folder")
    parser.add_argument("--v10", type=Path, default=V10_RUN, help="the v1.0 filter run of the same saved answers")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=REPO / "js3" / "fresh")
    args = parser.parse_args(argv)
    out = build(args.out, args.run, args.v10, args.seed)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
