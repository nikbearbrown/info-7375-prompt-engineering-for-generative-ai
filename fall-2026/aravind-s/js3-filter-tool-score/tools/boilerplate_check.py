"""Do the score's sentence-based points come from boilerplate? A diagnostic, computed after the fact from committed
files: it changes no rule, no verdict and no frozen result.

For the kept postings of each filter run (v1.0: js3/filter-run/2026-11-21T044414Z/, v1.1: 2026-11-22T084738Z/), every
point the score gives from a sentence (job_agent/filter.py score(), FILTER.md Section 1's ranking):
  - a topic group, +5: a topic word and an action word in one sentence (topic_groups(), which records the first
    sentence that earned each group);
  - a company word, -10: R7's "cannot tell" for a years sentence that names the company (Section 6, item 3);
  - (also counted, never removed) v1.1's caution, -10: a sentence with "export control".
Each is checked against the sentence that earned it. A sentence is boilerplate when the same normalized sentence
(whitespace collapsed, a leading bullet dropped, lower case) is in at least T of the same board's saved postings, at
two thresholds: 5 postings, and 20% of the board's saved postings (rounded up). The sentences are each run's own
(FILTER.md's splitter as that version runs it); the board's saved postings are every posting of its saved answer,
checked against the SHA-256 the run recorded, whatever its fate.

A point depends on boilerplate when no other sentence of the posting earns it: the topic groups are recomputed by
the filter's own topic_groups() over the posting's sentences that are not boilerplate, R7 by its own r7_years(), and
the score by its own score(). The shortlist (the run's cutoff, the duplicates, the order, the top 10) is recomputed
by its own shortlist(). The rank is the place in the shortlist's ordered list, after the cutoff and the duplicates.

Usage (from the repo root):
  python3 tools/boilerplate_check.py            write js3/checks/BOILERPLATE.md
  python3 tools/boilerplate_check.py --check    write nothing; exit 1 if the committed file is not what this rebuilds
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(TOOLS))

import audit_kit  # noqa: E402
from job_agent import filter as flt  # noqa: E402
from job_agent.rule import _flat  # noqa: E402

RUNS = ("2026-11-21T044414Z", "2026-11-22T084738Z")
OUT = REPO / "js3" / "checks" / "BOILERPLATE.md"
WRITTEN = "2026-11-24"
COMMAND = "python3 tools/boilerplate_check.py"
QUOTE = 120
BULLET = re.compile("^[-\u2022*\u2013]\\s+")  # the posting's own bullets, as audit_kit.card() drops them
THRESHOLDS = (("at least 5 postings", "5 postings", lambda board_size: 5),
              ("at least 20% of the board's saved postings", "20% of the board",
               lambda board_size: -(-board_size // 5)))


def normalized(sentence: str) -> str:
    return BULLET.sub("", _flat(sentence).strip()).lower()


def quote(sentence: str) -> str:
    text = BULLET.sub("", _flat(sentence).strip())
    return text if len(text) <= QUOTE else text[:QUOTE] + " ..."


def key(record: dict) -> tuple:
    return (record["board"], record["id"])


def index(postings: dict, rules: dict) -> tuple:
    """(each posting's sentences, {(board, normalized sentence): posting ids}, the same for titles, board sizes)."""
    sentences = {k: flt.split_sentences(p.get("descriptionPlain") or "", rules.get("splitter_keeps", ()))[0]
                 for k, p in postings.items()}
    share, titles = collections.defaultdict(set), collections.defaultdict(set)
    for k, found in sentences.items():
        for s in found:
            share[(k[0], normalized(s))].add(k[1])
            titles[(k[0], normalized(s))].add(flt.normalized_title(postings[k].get("title") or ""))
    return sentences, share, titles, collections.Counter(k[0] for k in postings)


def load_run(run_id: str, cache: dict) -> dict:
    folder = REPO / "js3" / "filter-run" / run_id
    data = json.loads((folder / "verdicts.json").read_text(encoding="utf-8"))
    rules = flt.load_rules(version=data["meta"]["filter_version"])
    sources = tuple(sorted((s["key"], s["sha256"]) for s in data["meta"]["sources"] if s.get("run")))
    if sources not in cache:  # both runs read the same saved answers; read them once
        cache[sources] = {k: p for k, (p, _) in audit_kit.saved_postings(data).items()}
    sentences, share, titles, board_size = index(cache[sources], rules)
    kept = [r for r in data["records"] if r["fate"] == "kept"]
    for r in kept:  # the records' own topics are what the filter's topic_groups() gives on these sentences
        if flt.topic_groups(sentences[key(r)], rules) != r["topics"]:
            raise SystemExit(f"STOP: {run_id}: the topics of {key(r)} do not rebuild from its saved posting")
    chosen = flt.shortlist(data["records"], rules)
    if [list(key(r)) for r in chosen["top"]] != [[k["board"], k["id"]] for k in data["shortlist"]]:
        raise SystemExit(f"STOP: {run_id}: the shortlist does not rebuild from verdicts.json")
    return {"run_id": run_id, "data": data, "rules": rules, "sentences": sentences, "share": share,
            "titles": titles, "board_size": board_size, "kept": kept, "chosen": chosen}


def ranks(chosen: dict) -> dict:
    out = {key(r): f"#{n}" for n, r in enumerate(chosen["ordered"], 1)}
    out.update({key(r): "a removed duplicate" for r in chosen["duplicates_removed"]})
    return out


def without_boilerplate(run: dict, threshold) -> dict:
    """Each kept posting's points that depend on boilerplate at this threshold, and its score without them."""
    rules, profile = run["rules"], flt.load_profile()
    out = {}
    for r in run["kept"]:
        k = key(r)
        limit = threshold(run["board_size"][r["board"]])
        boiler = {s for s in run["sentences"][k] if len(run["share"][(r["board"], normalized(s))]) >= limit}
        others = [s for s in run["sentences"][k] if s not in boiler]
        groups = flt.topic_groups(others, rules)
        recorded = [g for g, t in r["topics"].items()
                    if len(run["share"][(r["board"], normalized(t["sentence"]))]) >= limit]
        changed = copy.deepcopy(r)
        changed["topics"] = groups
        company = [f for f in r["flags"] if f["rule"] == "R7"]
        company_recorded, company_depends = [], []
        if company:
            r7 = next(c for c in r["rules"] if c["rule"] == "R7")
            if len(run["share"][(r["board"], normalized(r7["quote"] or ""))]) >= limit:
                company_recorded.append(r7["quote"])
            again = flt.r7_years(others, profile, rules, {"section6": {"company_words": []}})
            if again["result"] != "cannot_tell":
                company_depends.append(r7["quote"])
                changed["flags"] = [f for f in r["flags"] if f["rule"] != "R7"]
        score, _ = flt.score(changed, rules)
        changed["score"] = score
        out[k] = {"record": r, "changed": changed, "recorded": recorded,
                  "depends": [g for g in r["topics"] if g not in groups], "company_recorded": company_recorded,
                  "company_depends": company_depends}
    return out


def plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def analyze(run: dict) -> list:
    """For each threshold: the points that rest on boilerplate, and the shortlist without the ones that depend on it."""
    rules = run["rules"]
    before = ranks(run["chosen"])
    top = [key(r) for r in run["chosen"]["top"]]
    out = []
    for label, short, threshold in THRESHOLDS:
        result = without_boilerplate(run, threshold)
        used = collections.defaultdict(list)
        for k, v in result.items():
            for g in v["recorded"]:
                t = v["record"]["topics"][g]
                used[(k[0], normalized(t["sentence"]))].append((v["record"], g, t))
        records = [result[key(r)]["changed"] if r["fate"] == "kept" else r for r in run["data"]["records"]]
        chosen = flt.shortlist(records, rules)
        after = ranks(chosen)
        moved = [k for k, v in result.items() if v["changed"]["score"] != v["record"]["score"]]
        rank_changed = {k for k in result if before.get(k, "below the cutoff") != after.get(k, "below the cutoff")}
        hit = [k for k, v in result.items() if v["depends"] or v["company_depends"]]
        limits = {b: threshold(n) for b, n in sorted(run["board_size"].items())}
        out.append({"label": label, "short": short, "limits": limits,
                    "result": result, "used": used, "before": before, "after": after, "moved": moved,
                    "rank_changed": rank_changed, "hit": hit,
                    "recorded": sum(len(v["recorded"]) for v in result.values()),
                    "depends": sum(len(v["depends"]) for v in result.values()),
                    "company_recorded": sum(len(v["company_recorded"]) for v in result.values()),
                    "company_depends": sum(len(v["company_depends"]) for v in result.values()),
                    "same_top": [key(r) for r in chosen["top"]] == top, "in_top": [k for k in hit if k in top]})
    return out


def run_section(run: dict, analysis: list) -> list:
    rules, kept = run["rules"], run["kept"]
    cutoff = rules["ranking"]["shortlist_min"]
    points = sum(len(r["topics"]) for r in kept)
    out = [f"## FILTER.md v{rules['version']}: filter run {run['run_id']}", "",
           f"{len(kept)} kept postings; {points} topic points (one per topic group a posting earned, +5 each); the "
           f"shortlist cutoff is {cutoff}. Boards: " + ", ".join(f"{b} {n} saved postings" for b, n in
                                                                sorted(run["board_size"].items())) + ".", ""]
    flags = collections.Counter(f["rule"] for r in kept for f in r["flags"])
    out += [f"Company-word points (R7 \"cannot tell\", -10) on kept postings: {flags.get('R7', 0)}. The other "
            f"sentence-based penalty, R6's \"cannot tell\" for a season start: {flags.get('R6', 0)}."]
    cautions = [r for r in kept if r["cautions"]]
    if rules["ranking"].get("caution_penalty"):
        sentences = sorted({(r["board"], normalized(c)) for r in cautions for c in r["cautions"]})
        shared = []
        for s in sentences:
            n = len(run["share"][s])
            at = [a["short"] for a in analysis if n >= a["limits"][s[0]]]
            not_at = [a["short"] for a in analysis if n < a["limits"][s[0]]]
            shared.append(f"{n} postings of {s[0]} (" + (f"boilerplate at {' and '.join(at)}" if at else
                                                        "boilerplate at neither threshold")
                          + (f", not at {' and '.join(not_at)}" if at and not_at else "") + ")")
        out += ["", f"The caution ({rules['ranking']['caution_penalty']} for a sentence with "
                f"\"{rules['caution_phrase']}\") is on {plural(len(cautions), 'kept posting')}, through "
                f"{plural(len(sentences), 'sentence')}, shared by {'; '.join(shared)}. It is not a topic or company "
                "word, and it is a legal statement about the role, so it is counted here and never removed below."]
    out += ["", "How widely each topic point's sentence is shared:", "",
            "| Postings of the same board with the sentence | Topic points |", "|---:|---:|"]
    spread = collections.Counter(len(run["share"][(r["board"], normalized(t["sentence"]))])
                                 for r in kept for t in r["topics"].values())
    out += [f"| {n} | {c} |" for n, c in sorted(spread.items())]
    for a in analysis:
        limits = ", ".join(f"{b} {n}" for b, n in a["limits"].items())
        out += ["", f"### Boilerplate: {a['label']}", "", f"The threshold per board: {limits}.", "",
                f"- Topic points whose recorded sentence is boilerplate: {a['recorded']}.",
                f"- Topic points that depend on boilerplate (no other sentence earns the group): {a['depends']}, on "
                f"{plural(len(a['hit']), 'posting')}.",
                f"- Company-word points whose sentence is boilerplate: {a['company_recorded']}; that depend on it: "
                f"{a['company_depends']}."]
        if a["used"]:
            out += ["", "| Board | Postings with the sentence | Distinct titles among them | Points it gave | "
                    "Sentence (first 120 characters) |", "|---|---:|---:|---|---|"]
            for s, uses in sorted(a["used"].items(), key=lambda kv: (-len(run["share"][kv[0]]), kv[0])):
                gave = "; ".join(f"{g} (\"{t['term']}\") to {r['title'].strip()} `{r['id'][:8]}`" for r, g, t in uses)
                out.append(f"| {s[0]} | {len(run['share'][s])} | {len(run['titles'][s])} | {gave} | "
                           f"\"{quote(uses[0][2]['sentence'])}\" |")
        out += [""]
        if a["moved"]:
            out += ["Without the points that depend on boilerplate:", "",
                    f"| Posting | Score | Rank | Recommended (cutoff {cutoff}) |", "|---|---|---|---|"]
            for k in a["moved"]:
                r, c = a["result"][k]["record"], a["result"][k]["changed"]
                rec = lambda x: "yes" if x["score"] >= cutoff else "no"  # noqa: E731
                out.append(f"| {r['title'].strip()} ({r['board']} `{r['id'][:8]}`) | {r['score']} to {c['score']} | "
                           f"{a['before'].get(k, 'below the cutoff')} to {a['after'].get(k, 'below the cutoff')} | "
                           f"{rec(r)} to {rec(c)} |")
            own = len(a["rank_changed"] & set(a["moved"]))
            others = len(a["rank_changed"] - set(a["moved"]))
            out += ["", f"In all, {plural(len(a['rank_changed']), 'kept posting')} change rank: {own} of the postings "
                    "above" + (f", and {others} others that move up." if others else ", and no other.")]
        else:
            out += ["Without the points that depend on boilerplate, no score changes, so no rank or recommendation "
                    "changes."]
        out += [f"The top 10 {'is unchanged, in the same order' if a['same_top'] else 'CHANGES'}; "
                + (f"{len(a['in_top'])} of its postings depend on boilerplate." if a["in_top"] else
                   "none of its postings depends on boilerplate.")]
    return out + [""]


def summary(runs: list, analyses: list) -> list:
    out = ["## In short", ""]
    for run, analysis in zip(runs, analyses):
        cutoff = run["rules"]["ranking"]["shortlist_min"]
        out.append(f"- **v{run['rules']['version']}** ({sum(len(r['topics']) for r in run['kept'])} topic points on "
                   f"{len(run['kept'])} kept postings, cutoff {cutoff}):")
        for a in analysis:
            if not a["depends"] and not a["company_depends"]:
                out.append(f"  - at {a['short']}: no point depends on boilerplate.")
                continue
            jobs = collections.Counter((a["result"][k]["record"]["title"].strip(), k[0]) for k in a["hit"])
            named = "; ".join(f"{title}, {board}" + (f", {n} copies" if n > 1 else "")
                              for (title, board), n in sorted(jobs.items()))
            text = (f"  - at {a['short']}: {plural(a['depends'], 'topic point')} on "
                    f"{plural(len(a['hit']), 'posting')} ({named}) depend on boilerplate")
            if a["moved"]:
                steps = collections.Counter((a["result"][k]["record"]["score"], a["result"][k]["changed"]["score"])
                                            for k in a["moved"])
                fallen = sum(n for (old, new), n in steps.items() if old >= cutoff > new)
                text += ("; without them " + ", ".join(f"{plural(n, 'score')} {'falls' if n == 1 else 'fall'} "
                                                       f"from {old} to {new}"
                                                       for (old, new), n in sorted(steps.items(), reverse=True))
                         + (f", {fallen} of them below the cutoff" if fallen else ", none below the cutoff"))
            out.append(text + "; the top 10 " + ("stays the same." if a["same_top"] else "CHANGES."))
    widest = max((len(run["share"][(r["board"], normalized(t["sentence"]))]), r["board"], run["board_size"][r["board"]])
                 for run in runs for r in run["kept"] for t in r["topics"].values())
    out.append(f"- The most widely shared sentence that earned a topic point is in {widest[0]} of {widest[1]}'s "
               f"{widest[2]} saved postings.")
    company = sum(1 for run in runs for r in run["kept"] for f in r["flags"] if f["rule"] == "R7")
    out.append(f"- Company-word points on kept postings, in both runs: {company}"
               + (", so none can depend on boilerplate." if not company else "."))
    in_top = sum(len(a["in_top"]) for analysis in analyses for a in analysis)
    out += ["- " + ("No posting in either top 10 depends on boilerplate, at either threshold." if not in_top else
                    f"{in_top} top-10 postings depend on boilerplate (see below)."), ""]
    return out


def render() -> str:
    cache = {}
    runs = [load_run(run_id, cache) for run_id in RUNS]
    analyses = [analyze(run) for run in runs]
    lines = [f"Computed by Claude Code on {WRITTEN} from committed files, after the fact. Not a new measurement. "
             f"Rebuild: `{COMMAND}` from the repo root (`--check` compares without writing).", "",
             "# Do the score's sentence-based points come from boilerplate?", "",
             "A diagnostic. It changes no rule, no verdict and no frozen result. Read from "
             + ", ".join(f"`js3/filter-run/{r['run_id']}/verdicts.json`" for r in runs)
             + ", the saved board answers they name (checked against their SHA-256), FILTER.md Section 7 versions "
             + " and ".join(r["rules"]["version"] for r in runs) + " and `persona/jane-doe.json`.", "",
             "The score gives points from sentences in two ways (`score()` in `job_agent/filter.py`): a topic group "
             "earns +5 when one sentence has a topic word and an action word, and R7 costs -10 when a years sentence "
             "names the company (a company word). FILTER.md Section 5 names the risk this checks: a posting can rank "
             "high from topic words in an \"about us\" sentence. A sentence counts as boilerplate when the same "
             "normalized sentence (whitespace collapsed, a leading bullet dropped, lower case) is in many postings of "
             "the same board: at least 5, or at least 20% of the board's saved postings (rounded up). A point depends "
             "on boilerplate when no other sentence of the posting earns it.", ""]
    lines += summary(runs, analyses)
    for run, analysis in zip(runs, analyses):
        lines += run_section(run, analysis)
    lines += ["## What this does not change", "",
              "No rule changes. Whether a shared requirement line should earn topic points, or count once per board, "
              "is the owner's call, in a later FILTER.md version; v1.0 and v1.1 stay as they are.", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if the committed file differs")
    args = ap.parse_args(argv)
    text = render()
    shown = OUT.relative_to(REPO).as_posix()
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print(f"{shown}: {'the same as' if same else 'DIFFERENT FROM'} what the committed files rebuild")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
