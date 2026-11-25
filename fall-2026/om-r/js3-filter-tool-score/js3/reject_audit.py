"""Reject audit (Chapter 7): seeded draw + BLANK hand-judgment worksheets.

    python3 -m js3.reject_audit                      # latest logs/run_*.json
    python3 -m js3.reject_audit logs/run_<stamp>.json

Groups (definitions fixed by Om before the draw):

  A. random_rejected  N_RANDOM postings, random.Random(SEED).sample over the
                      reject sampling pool (filter.reject_sampling_pool - every
                      "rejected" posting, never insufficient_data), sorted by
                      (board, str(id)) first so the draw is reproducible. A
                      simple random sample over all boards pooled, not
                      stratified.
  B. near_threshold   "Closest calls" for a discrete-rule filter. Population:
                      rejected postings that matched exactly 1 of the 6 skill
                      words (one short of rule 1), OR passed rule 1 and were
                      excluded only by rule 2. Group B = every rule-2-only
                      posting (forced include, not sampled) + N_NEAR_SAMPLE
                      drawn by random.Random(SEED).sample over the exactly-1-word
                      postings sorted by (board, str(id)). Not mixed into A.
                      (Reduced from the full population for time - FRICTIONAL.md
                      entry 4. B is a sample of a sample.)
  C. relevant         ALL postings the filter kept (a census, for comparison).

A posting can be in both A and B. It is written out in full once (in A) and
cross-referenced in B, so it is judged once and the judgment counts for both.

The worksheets contain the posting text and the mechanical facts of which
rules fired. They contain NO verdict, score, suggestion or reasoning.
"""
import html
import json
import random
import re
import sys
from pathlib import Path

from js3 import filter as flt
from js3.postings import load_run

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261121
N_RANDOM = 30
N_NEAR_SAMPLE = 38  # + the forced rule-2-only includes (2 in the real run) = 40
OUT_DIR = ROOT / "logs" / "reject_audit"


def _key(r):
    return (str(r["board"]), str(r["id"]))


def is_rule2_only(r):
    return r["bucket"] == "rejected" and all(x.startswith("rule 2") for x in r["reasons"])


def is_near_threshold(r):
    return r["bucket"] == "rejected" and (len(r["matched_skills"]) == 1 or is_rule2_only(r))


def draw(filter_output, n_near=N_NEAR_SAMPLE):
    pool = sorted(flt.reject_sampling_pool(filter_output), key=_key)
    random_rejected = random.Random(SEED).sample(pool, N_RANDOM)
    population = [r for r in pool if is_near_threshold(r)]
    forced = [r for r in population if is_rule2_only(r)]
    exactly1 = [r for r in population if not is_rule2_only(r)]
    near = forced + random.Random(SEED).sample(exactly1, n_near)
    relevant = sorted(filter_output["relevant"], key=_key)
    return {"seed": SEED, "n_random": N_RANDOM, "n_near": n_near, "pool_size": len(pool),
            "random_rejected": random_rejected, "near_threshold_population": population,
            "near_threshold_forced": forced, "near_threshold_exactly1_pool": exactly1,
            "near_threshold": near, "relevant": relevant}


# ---------- worksheet rendering ----------

def render_text(raw):
    """Readable text, kept verbatim apart from markup: Greenhouse HTML is
    unescaped, block tags become line breaks, list items get '- '."""
    t = html.unescape(raw or "")
    t = re.sub(r"(?i)<li[^>]*>", "\n- ", t)
    t = re.sub(r"(?i)<br\s*/?>|</?(p|div|h[1-6]|ul|ol|li|tr)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in t.splitlines()]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def rule_facts(r):
    matched = {m["skill"]: m for m in r["matched_skills"]}
    n = len(matched)
    lines = ["**Rule 3 (content present):** yes - content is not empty, so rules 1 and 2 were applied",
             f"**Rule 1 (>= 2 of 6 skill words):** {n} of 6 matched - rule 1 "
             f"{'passed' if n >= flt.SKILL_THRESHOLD else 'not passed'}"]
    for s in flt.ROLE_SKILLS:
        if s in matched:
            m = matched[s]
            lines.append(f"  - {s}: matched in {m['field']} - \"{m['quote']}\"")
        else:
            lines.append(f"  - {s}: not found")
    if r["sales_title_word"]:
        phrase = r["ai_building_phrase"]
        lines.append(f"**Rule 2 (sales/GTM title word):** title contains \"{r['sales_title_word']}\"; "
                     f"AI-systems-building phrase in content: "
                     f"{chr(34) + phrase + chr(34) if phrase else 'none found'} - rule 2 "
                     f"{'exception applied (did not exclude)' if phrase else 'fired (excludes)'}")
    else:
        lines.append("**Rule 2 (sales/GTM title word):** no listed word in title - rule 2 did not fire")
    return lines


def entry(label, r, p):
    out = [f"## {label}. [{r['board']}] id {r['id']}", "",
           f"**Title:** {r['title']}", f"**Board:** {r['board']}", f"**URL:** {r['url']}", ""]
    out += rule_facts(r) + [""]
    if r["board"] == "palantir":
        out += ["**Content (Lever `descriptionPlain` - the only text the filter saw, per FILTER.md):**", "",
                render_text(p["content"]), "",
                "**Lever `lists` + `additionalPlain` (NOT seen by the filter - FRICTIONAL.md entry 1):**", "",
                render_text(p.get("lever_extra")) or "(none)", ""]
    else:
        out += ["**Content:**", "", render_text(p["content"]), ""]
    out += ["**Hand label (relevant / not relevant):** ________",
            "**Reason (fields relied on):** ________", "", "---", ""]
    return out


def header(title, src, selection, n):
    return [f"# Reject audit: hand-judgment worksheet (BLANK) - {title}", "",
            f"Source: `{src}` (filter v{flt.VERSION}), raw evidence committed in `evidence/`.",
            f"Selection: {selection}",
            "Generated by `js3/reject_audit.py`. No hand label, verdict, score or suggestion was",
            "computed for these postings. The rule facts below are the filter's mechanical",
            "output only.", f"Postings in this file: {n}.", "",
            "Persona: Priya Nair (`resume.json`, fictional) - target roles AI Engineer, ML Engineer,",
            "LLM Platform Engineer.", "",
            "Content is the posting's text with markup removed (text kept verbatim).", "",
            "Labeling rule used (write before labeling): ________________________________", "", "---", ""]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    run_path = (Path(argv[0]) if argv else max((ROOT / "logs").glob("run_*.json"))).resolve()
    stamp = run_path.stem.removeprefix("run_")
    _, postings, _ = load_run(run_path, ROOT)
    out = flt.run_filter(postings)
    committed = json.loads((ROOT / "logs" / f"filter_run_{stamp}.json").read_text())["summary"]
    assert flt.summary(out) == committed, (flt.summary(out), committed)
    by_id = {(p["board"], p["id"]): p for p in postings}
    d = draw(out)
    src = f"logs/filter_run_{stamp}.json"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    a_label = {}
    lines = header("A. random sample of rejected", src,
                   f"`random.Random({SEED}).sample(pool, {N_RANDOM})` over the {d['pool_size']} postings in the "
                   f"reject sampling pool (bucket \"rejected\"; insufficient_data excluded), sorted by "
                   f"(board, id) before drawing. Simple random over all three boards pooled, not stratified.",
                   N_RANDOM)
    for i, r in enumerate(d["random_rejected"], 1):
        a_label[_key(r)] = f"A{i:02d}"
        lines += entry(f"A{i:02d}", r, by_id[(r["board"], r["id"])])
    (OUT_DIR / "A_random_rejected_BLANK.md").write_text("\n".join(lines))

    overlap = [r for r in d["near_threshold"] if _key(r) in a_label]
    nf, n1 = len(d["near_threshold_forced"]), len(d["near_threshold_exactly1_pool"])
    lines = header(f"B. near-threshold rejects ({nf} forced + {d['n_near']} sampled)", src,
                   f"the {nf} postings that passed rule 1 but were excluded only by rule 2 (forced includes, "
                   f"not sampled, listed first), then `random.Random({SEED}).sample(pool, {d['n_near']})` over "
                   f"the {n1} rejected postings matching exactly 1 of the 6 skill words, sorted by (board, id) "
                   f"before drawing, in draw order. {len(overlap)} of these were also drawn into file A; they "
                   "appear here as a cross-reference only (judge once, in A - the label counts for both groups).\n\n"
                   f"**Limitation (stated, not hidden):** B is a {d['n_near']}-of-{n1} random subsample of the "
                   "near-threshold population, reduced for time (FRICTIONAL.md entry 4). The near-threshold audit "
                   "is therefore a sample of a sample: any rate estimated from B carries sampling error on top of "
                   "the hand-judging itself, and near-threshold postings not drawn here were never hand-judged.",
                   len(d["near_threshold"]))
    for i, r in enumerate(d["near_threshold"], 1):
        if _key(r) in a_label:
            lines += [f"## B{i:03d}. [{r['board']}] id {r['id']} - see {a_label[_key(r)]} in "
                      f"`A_random_rejected_BLANK.md`", "", f"**Title:** {r['title']}", "",
                      f"(Also drawn into the random sample; judge it there. Label counts for both groups.)",
                      "", "---", ""]
        else:
            lines += entry(f"B{i:03d}", r, by_id[(r["board"], r["id"])])
    (OUT_DIR / "B_near_threshold_BLANK.md").write_text("\n".join(lines))

    lines = header("C. relevant (all, for comparison)", src,
                   f"ALL {len(d['relevant'])} postings in the \"relevant\" bucket (a census, not a sample), "
                   "ordered by (board, id).", len(d["relevant"]))
    for i, r in enumerate(d["relevant"], 1):
        lines += entry(f"C{i:02d}", r, by_id[(r["board"], r["id"])])
    (OUT_DIR / "C_relevant_BLANK.md").write_text("\n".join(lines))

    manifest = {"source_filter_run": src, "filter_version": flt.VERSION, "seed": SEED, "n_random": N_RANDOM,
                "reject_pool_size": d["pool_size"],
                "near_threshold_definition": "rejected AND (exactly 1 of 6 skill words OR excluded only by rule 2)",
                "near_threshold_selection": {
                    "population_size": len(d["near_threshold_population"]),
                    "forced_includes": {"rule": "passed rule 1, excluded only by rule 2 - not subject to the sample",
                                        "count": len(d["near_threshold_forced"])},
                    "sampled": {"call": f"random.Random({SEED}).sample(exactly1_pool, {d['n_near']})",
                                "exactly1_pool_size": len(d["near_threshold_exactly1_pool"]),
                                "pool_order": "sorted by (board, str(id))", "count": d["n_near"]},
                    "group_size": len(d["near_threshold"]),
                    "reduced_from_full_population": True,
                    "why": ("time constraint: hand-judging all 156 near-threshold postings (202 distinct postings "
                            "across A+B+C) was more than Om could do in the time available; B was cut to 40 before "
                            "any posting was judged"),
                    "limitation": ("the near-threshold audit is a sample of a sample: B covers "
                                   f"{d['n_near']} of {len(d['near_threshold_exactly1_pool'])} exactly-1-word postings, "
                                   "so any near-threshold miss rate is an estimate with sampling error, and the "
                                   "undrawn postings were never hand-judged. Must be stated in the reject-audit write-up."),
                    "seed_note": ("same seed as group A, by Om's choice. Both draws start from the same random "
                                  "stream over (board, id)-sorted pools, so they are not statistically independent "
                                  "of each other; each is individually a uniform random sample of its own pool."),
                    "population": [{"board": r["board"], "id": r["id"], "title": r["title"]}
                                   for r in d["near_threshold_population"]]},
                "groups": {g: [{"label": lab, "board": r["board"], "id": r["id"], "title": r["title"]}
                               for lab, r in zip(labels, d[g])]
                           for g, labels in (
                               ("random_rejected", [f"A{i:02d}" for i in range(1, N_RANDOM + 1)]),
                               ("near_threshold", [f"B{i:03d}" for i in range(1, len(d["near_threshold"]) + 1)]),
                               ("relevant", [f"C{i:02d}" for i in range(1, len(d["relevant"]) + 1)]))},
                "overlap_A_and_B": [{"A": a_label[_key(r)], "board": r["board"], "id": r["id"]} for r in overlap]}
    (OUT_DIR / "draw_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    near_r2 = sum(is_rule2_only(r) for r in d["near_threshold"])
    print(f"reject audit draw over {src}  seed {SEED}")
    print(f"  A random_rejected : {N_RANDOM} of {d['pool_size']}  boards "
          + ", ".join(f"{b} {sum(r['board'] == b for r in d['random_rejected'])}" for b in ("gitlab", "stripe", "palantir")))
    print(f"  B near_threshold  : {len(d['near_threshold'])} = {near_r2} forced rule-2-only + {d['n_near']} sampled "
          f"of {len(d['near_threshold_exactly1_pool'])} exactly-1-word (population {len(d['near_threshold_population'])}); "
          f"overlap with A: {len(overlap)} "
          + str([f"{a_label[_key(r)]}={r['board']}:{r['id']}" for r in overlap]))
    print(f"  C relevant        : {len(d['relevant'])} (all)")
    print(f"  to hand-judge     : {N_RANDOM + len(d['near_threshold']) - len(overlap) + len(d['relevant'])} distinct postings")
    for f in sorted(OUT_DIR.iterdir()):
        print(f"  wrote {f.relative_to(ROOT)}  ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
