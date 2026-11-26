"""Explain one posting's score term by term, with the exact quote behind every point.

  .venv/bin/python -m js3.explain <posting key or bare id> [--filter v1.0] [--text]

--text also prints the full readable description, so every quote can be found with Ctrl-F.
"""
import argparse
import sys

from inherited.rules import normalize

from .corpus import load_corpus
from .filter import load_filter, score_posting
from .text import readable


def resolve(corpus, pid):
    if pid in corpus:
        return pid
    hits = [k for k, p in corpus.items() if str(p["id"]) == pid]
    if len(hits) != 1:
        raise SystemExit(f"I cannot tell: {pid!r} {'matches several postings' if hits else 'is not in the corpus'}")
    return hits[0]


def explain(key, cfg, corpus):
    p = corpus[key]
    r = score_posting(p, cfg)
    out = [f"{key} — {p['title']!r}", f"board {p['provider']}:{p['board']} · location {p['location']!r} · "
           f"captured {p['last_seen']} · filter {cfg['version']} · threshold {cfg['threshold']}", ""]
    if r["parts"] is None:
        return "\n".join(out + [f"verdict cannot_tell: {r['reason']}"])
    P = r["parts"]
    m = P["R"]["match"]
    out.append(f"R = {P['R']['points']:+d}  " + (f"{P['R']['tier']}: '{m['phrase']}' in {m['field']}: \"{m['quote']}\""
                                               if m else "no role phrase in posting.title"))
    m = P["S"]["match"]
    out.append(f"S = {P['S']['points']:+d}  " + (f"level word '{m['phrase']}' in {m['field']}: \"{m['quote']}\""
                                               if m else "no level word in posting.title"))
    out.append(f"T = {P['T']['points']:+d}  ({P['T']['uncapped']} distinct group(s), cap {P['T']['cap']})")
    for g in P["T"]["groups"]:
        out.append(f"      {g['group']}: '{g['phrase']}' in {g['field']}: \"{g['quote']}\"")
    if p["board"] in " ".join(sum(cfg["topic"]["groups"].values(), [])).split():
        out.append(f"      (the word '{p['board']}' is ignored on its own board, FILTER.md T7)")
    m = P["E"]["match"]
    out.append(f"E = {P['E']['points']:+d}  " + (f"'{m['phrase']}' in {m['field']}: \"{m['quote']}\""
                                               if m else "no early-career phrase"))
    out.append(f"Y = {P['Y']['points']:+d}  N = {P['Y']['N']}" + ("" if P["Y"]["matches"] else "  (no 'N years' phrase)"))
    for y in P["Y"]["matches"]:
        out.append(f"      '{y['normalized']}': \"{y['quote']}\"")
    out += ["", f"{r['arithmetic']}  ->  {r['verdict']}" + (f"  (missing: {r['missing']})" if r["missing"] else "")]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("posting")
    ap.add_argument("--filter", default="v1.0")
    ap.add_argument("--text", action="store_true")
    a = ap.parse_args(argv)
    corpus = load_corpus()
    key = resolve(corpus, a.posting)
    print(explain(key, load_filter(a.filter), corpus))
    if a.text:
        print("\n--- posting.title ---\n" + corpus[key]["title"])
        print("--- posting.description (readable; normalized form is what the rules match) ---\n"
              + readable(corpus[key]["text"]))


if __name__ == "__main__":
    sys.exit(main())
