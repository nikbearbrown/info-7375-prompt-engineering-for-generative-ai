"""The reject audit (Chapter 7): draw a seeded sample, label it blind, and report what the sample can show.

    python3 -m js3.audit draw            # writes audit/sample-key.json + audit/cards.md (refuses if verdicts exist)
    python3 -m js3.audit label           # Omkar labels each card by hand, blind (no score, no filter verdict)
    python3 -m js3.audit show            # one-shot: print the next unlabelled card (or --card N)
    python3 -m js3.audit label --card N --verdict keep|reject|cannot_tell --note "why"   # one-shot: save one verdict
    python3 -m js3.audit claude-rate     # a SECOND rater: one fresh `claude -p` call per card, same rule, same card
    python3 -m js3.audit report          # writes audit/AUDIT-RESULTS.md from the verdict files

Four parts (Lectern's audit_rejects.py idea, extended):
  R  a UNIFORM random sample of 30 rejects (seed recorded): the only part that supports a rate
  C  every close call (gate-passing, score within 1.0 of the threshold), kept or rejected
  G  gate near-misses: rejects with score >= threshold that failed exactly one gate (up to 8, random)
  K  every kept posting (the shortlist is small enough to read in full)
The cards are shuffled together and never show the part, the score or the filter's verdict, so the
hand verdict cannot copy the filter. The key (audit/sample-key.json) is read only by `report`.
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import webbrowser

from . import data, scorer, store
from . import textutil as tu

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 7375003
N_RANDOM = 30
N_GATE = 8
KEY = "audit/sample-key.json"
CARDS = "audit/cards.md"
OMKAR = "audit/omkar-verdicts.csv"
CLAUDE = "audit/claude-second-rater.jsonl"
VERDICTS = ("keep", "reject", "cannot_tell")
RULE = ("Should this posting reach Aarav? KEEP if all four hold (Omkar's JS1 labeling rule, 2026-10-26): "
        "1 role: a Software Engineer role, or a close engineering role that is mostly writing software "
        "(not sales, IT, security-compliance or analyst); 2 level: the posting asks for about 3 years or fewer; "
        "3 location: any US location; 4 skills: Aarav meets most of the posting's required qualifications. "
        "Otherwise REJECT. CANNOT_TELL only if the card does not let you decide.")


def _p(path):
    return os.path.join(BASE, path)


def _card(p, rec, n):
    text = tu.clean(p.get("content"))
    cfg = scorer.load_filter()
    segs = tu.segments(p.get("html") or p.get("content") or "", cfg["requirement_headings"], cfg["end_headings"],
                       cfg.get("plural_headings", False))
    req = " ".join(t for in_req, _, t in segs if in_req)
    excerpt = (req or text)[:900]
    yrs = "; ".join(q for _, q in tu.years_statements(text, cfg.get("years_plus_alone", False))[:3]) or "(none found)"
    return {"card": n, "company": p.get("company"), "title": p.get("title"),
            "location": (p.get("location") or {}).get("name") or "(empty)", "url": p.get("absolute_url") or "",
            "years_sentences": yrs, "excerpt_kind": "requirements section" if req else "start of posting",
            "excerpt": excerpt + ("…" if len(req or text) > 900 else "")}


def draw(run_id=None):
    if os.path.exists(_p(OMKAR)) and os.path.getsize(_p(OMKAR)) > 0:
        raise SystemExit(f"{OMKAR} already has verdicts; refusing to redraw the sample over them")
    run_id, corpus = data.load_corpus(run_id)
    cfg = scorer.load_filter()
    persona = data.load_persona()
    recs = [scorer.evaluate(p, persona, cfg) for p in corpus]
    idx = list(range(len(corpus)))
    rng = random.Random(SEED)
    rejects = [i for i in idx if recs[i]["verdict"] == "reject"]
    part = {}
    for i in rng.sample(rejects, N_RANDOM):
        part.setdefault(i, []).append("R")
    for i in idx:
        if recs[i]["close_call"]:
            part.setdefault(i, []).append("C")
    gate = [i for i in rejects if recs[i]["score"] >= cfg["threshold"] and
            sum(not g["pass"] for g in recs[i]["gates"].values()) == 1]
    for i in rng.sample(gate, min(N_GATE, len(gate))):
        part.setdefault(i, []).append("G")
    for i in idx:
        if recs[i]["verdict"] == "keep":
            part.setdefault(i, []).append("K")
    order = list(part)
    rng.shuffle(order)
    key, cards = [], []
    for n, i in enumerate(order, 1):
        r = recs[i]
        key.append({"card": n, "id": r["id"], "source": r["source"], "parts": part[i], "filter_verdict": r["verdict"],
                    "score": r["score"], "reasons": r["reasons"], "close_call": r["close_call"],
                    "title": r["title"], "skills_found": r["skills_found"]})
        cards.append(_card(corpus[i], r, n))
    meta = {"corpus_run": run_id, "filter_version": cfg["version"], "seed": SEED,
            "drawn_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "population": {"postings": len(corpus), "rejects": len(rejects),
                           "kept": sum(r["verdict"] == "keep" for r in recs),
                           "close_calls": sum(r["close_call"] for r in recs), "gate_near_misses": len(gate)},
            "parts": {"R": N_RANDOM, "C": sum("C" in v for v in part.values()),
                      "G": sum("G" in v for v in part.values()), "K": sum("K" in v for v in part.values())},
            "cards": len(order)}
    store.write_text(KEY, json.dumps({"meta": meta, "key": key, "cards": cards}, indent=1, ensure_ascii=False))
    L = [f"# Audit cards (blind): {len(cards)} postings", "",
         f"Drawn {meta['drawn_utc']} from corpus {run_id} with filter v{cfg['version']}, seed {SEED}. "
         "The cards do not show the score, the filter's verdict or which part of the sample a card came from.", "",
         "**Rule for each card.** " + RULE, ""]
    for c in cards:
        L += [f"## Card {c['card']}: {c['company']} · {c['title']}", "",
              f"- Location: {c['location']}", f"- Link: {c['url'] or '(no link)'}",
              f"- Years sentences: {c['years_sentences']}", f"- Excerpt ({c['excerpt_kind']}): {c['excerpt']}", ""]
    store.write_text(CARDS, "\n".join(L))
    return meta


def _load_key():
    with open(_p(KEY), encoding="utf-8") as f:
        return json.load(f)


def _omkar():
    if not os.path.exists(_p(OMKAR)):
        return {}
    with open(_p(OMKAR), encoding="utf-8") as f:
        return {int(r["card"]): r for r in csv.DictReader(f)}


def label(inp=input, out=print):
    k = _load_key()
    done = _omkar()
    todo = [c for c in k["cards"] if c["card"] not in done]
    out(f"{len(done)} of {len(k['cards'])} cards labelled. {len(todo)} to go. q = save and quit.\n\n{RULE}\n")
    new = not os.path.exists(_p(OMKAR))
    store.check(OMKAR)
    with open(_p(OMKAR), "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["card", "verdict", "note", "labelled_utc"])
        if new:
            w.writeheader()
        for c in todo:
            out("=" * 78)
            out(f"Card {c['card']} · {c['company']} · {c['title']}\nLocation: {c['location']}\nLink: {c['url']}")
            out(f"Years sentences: {c['years_sentences']}\nExcerpt ({c['excerpt_kind']}):\n{c['excerpt']}\n")
            while True:
                a = inp("[k]eep / [r]eject / [c]annot tell / [o]pen link / [q]uit: ").strip().lower()
                if a == "o" and c["url"]:
                    webbrowser.open(c["url"])
                    continue
                if a in ("k", "r", "c", "q"):
                    break
            if a == "q":
                out("saved.")
                return
            note = inp("note in your words (why; Enter to skip): ").strip()
            w.writerow({"card": c["card"], "verdict": {"k": "keep", "r": "reject", "c": "cannot_tell"}[a],
                        "note": note, "labelled_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            f.flush()
    out("all cards labelled. Now run: python3 -m js3.audit report")


def _card_text(c):
    return (f"Card {c['card']} · {c['company']} · {c['title']}\nLocation: {c['location']}\nLink: {c['url']}\n"
            f"Years sentences: {c['years_sentences']}\nExcerpt ({c['excerpt_kind']}):\n{c['excerpt']}\n")


def show(card=None, out=print):
    """Print one card, blind. Default: the next card without a verdict."""
    k = _load_key()
    done = _omkar()
    if card is None:
        todo = [c for c in k["cards"] if c["card"] not in done]
        if not todo:
            out(f"all {len(k['cards'])} cards labelled. Now run: python3 -m js3.audit report")
            return None
        c = todo[0]
    else:
        c = next((x for x in k["cards"] if x["card"] == card), None)
        if c is None:
            raise SystemExit(f"no card {card}; cards are 1-{len(k['cards'])}")
    out(f"{len(done)} of {len(k['cards'])} cards labelled.\n\n{RULE}\n")
    out(_card_text(c))
    out(f"Answer with ONE of keep / reject / cannot_tell, and your own words after --note, e.g.:\n"
        f"  python3 -m js3.audit label --card {c['card']} --verdict reject --note <your words in quotes>")
    return c["card"]


PLACEHOLDERS = {"your reason", "your reason here", "type your own reason", "why", "reason", "note", "<your reason>"}


def label_one(card, verdict, note, out=print, replace=False):
    """Save ONE hand verdict (the one-line form of `label`). Refuses a card that already has one,
    unless replace=True: then the old row is kept in audit/omkar-verdicts-replaced.csv (nothing is lost)."""
    k = _load_key()
    if card not in {c["card"] for c in k["cards"]}:
        raise SystemExit(f"no card {card}; cards are 1-{len(k['cards'])}")
    verdict = {"k": "keep", "r": "reject", "c": "cannot_tell"}.get(verdict, verdict)
    if verdict not in VERDICTS:
        raise SystemExit(f"verdict must be one of {', '.join(VERDICTS)} (or k / r / c)")
    n = (note or "").strip().lower()
    if not n or n in PLACEHOLDERS or n.startswith(("your reason", "type your", "write why", "write your", "...")) \
            or n.strip(". ") == "":
        raise SystemExit('--note must be YOUR reason in your own words (e.g. what in the posting decided it), '
                         'not the example text. Nothing was saved.')
    done = _omkar()
    if card in done and not replace:
        raise SystemExit(f"card {card} already has a verdict ({done[card]['verdict']}); add --replace to change it")
    if card in done:
        old = done.pop(card)
        hist = "audit/omkar-verdicts-replaced.csv"
        store.check(hist)
        first = not os.path.exists(_p(hist))
        with open(_p(hist), "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["card", "verdict", "note", "labelled_utc", "replaced_utc"])
            if first:
                w.writeheader()
            w.writerow(dict(old, replaced_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
        with open(_p(OMKAR), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["card", "verdict", "note", "labelled_utc"])
            w.writeheader()
            for c in sorted(done):
                w.writerow({k_: done[c][k_] for k_ in ("card", "verdict", "note", "labelled_utc")})
    new = not os.path.exists(_p(OMKAR)) or os.path.getsize(_p(OMKAR)) == 0
    store.check(OMKAR)
    with open(_p(OMKAR), "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["card", "verdict", "note", "labelled_utc"])
        if new:
            w.writeheader()
        w.writerow({"card": card, "verdict": verdict, "note": (note or "").strip(),
                    "labelled_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    out(f"saved card {card}: {verdict}. {len(done) + 1} of {len(k['cards'])} labelled.\n")
    show(out=out)


CLAUDE_PROMPT = """You are labelling one job posting for a fictional candidate, Aarav Patel: MS Information Systems (2026-05), about 2 years full-time as a Software Engineer (Java services) plus a 2026 co-op (TypeScript, MSSQL, Redis, Elasticsearch), lives in Boston, open to any US location. Shipped skills: TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins.

{rule}

Use only the card below. Answer with one JSON object and nothing else:
{{"verdict": "keep" | "reject" | "cannot_tell", "reason": "<one sentence citing the card>"}}

CARD
Company: {company}
Title: {title}
Location: {location}
Years sentences: {years_sentences}
Excerpt ({excerpt_kind}): {excerpt}
"""


def claude_call(prompt, model="claude-sonnet-5-5", timeout=180):
    """One fresh, tool-less `claude -p` conversation in an empty temp dir (JS1's isolation)."""
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["claude", "-p", prompt, "--model", model, "--tools", "", "--setting-sources", "",
                            "--no-session-persistence", "--output-format", "json"],
                           cwd=d, capture_output=True, text=True, timeout=timeout)
    return r


def _parse_json(text):
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    s, e = t.find("{"), t.rfind("}")
    return json.loads(t[s:e + 1])


def claude_rate(model="claude-sonnet-5-5", workers=6):
    from concurrent.futures import ThreadPoolExecutor
    k = _load_key()
    have = set()
    if os.path.exists(_p(CLAUDE)):
        with open(_p(CLAUDE), encoding="utf-8") as f:
            have = {json.loads(l)["card"] for l in f if l.strip()}
    todo = [c for c in k["cards"] if c["card"] not in have]

    def one(c):
        prompt = CLAUDE_PROMPT.format(rule=RULE, **c)
        t0 = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = claude_call(prompt, model)
        row = {"card": c["card"], "asked_utc": t0, "model": model, "exit": r.returncode}
        try:
            env = json.loads(r.stdout)
            row["raw"] = env.get("result")
            row["session_id"] = env.get("session_id")
            v = _parse_json(row["raw"])
            row["verdict"], row["reason"] = v.get("verdict"), v.get("reason")
            if row["verdict"] not in VERDICTS:
                row["invalid"] = f"verdict {row['verdict']!r} not allowed"
        except Exception as e:  # keep the failure, never invent a verdict
            row["invalid"] = f"{e.__class__.__name__}: {e}"
            row["stderr"] = r.stderr[-500:]
        return row

    store.check(CLAUDE)
    with ThreadPoolExecutor(workers) as ex, open(_p(CLAUDE), "a", encoding="utf-8") as f:
        for row in ex.map(one, todo):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(row["card"], row.get("verdict"), row.get("invalid", ""))


# --- statistics ---------------------------------------------------------------------------

def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided 95% interval for a binomial proportion (bisection; stdlib only)."""
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(100):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - _binom_cdf(k - 1, n, p) >= alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: _binom_cdf(k, n, p) <= alpha / 2)
    return lower, upper


def report():
    k = _load_key()
    meta, key = k["meta"], {e["card"]: e for e in k["key"]}
    om = _omkar()
    cl = {}
    if os.path.exists(_p(CLAUDE)):
        with open(_p(CLAUDE), encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    cl[r["card"]] = r
    n_cards = len(key)
    # the filter's verdict NOW (the sample was drawn under an earlier version; rules changed since)
    cfg_now = scorer.load_filter()
    _, corpus = data.load_corpus(meta["corpus_run"])
    by = {(p["source"], p["id"]): p for p in corpus}
    persona = data.load_persona()
    now = {c: scorer.evaluate(by[(e["source"], e["id"])], persona, cfg_now)["verdict"] for c, e in key.items()}
    L = ["# Audit results (generated)", "",
         f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} by `python3 -m js3.audit report` from "
         f"`{KEY}`, `{OMKAR}` and `{CLAUDE}`. Sample drawn {meta['drawn_utc']}, corpus {meta['corpus_run']}, "
         f"filter v{meta['filter_version']}, seed {meta['seed']}.", "",
         f"Population: {meta['population']['postings']} postings, {meta['population']['rejects']} rejects, "
         f"{meta['population']['kept']} kept, {meta['population']['close_calls']} close calls, "
         f"{meta['population']['gate_near_misses']} gate near-misses. Cards: {n_cards} "
         f"(R {meta['parts']['R']}, C {meta['parts']['C']}, G {meta['parts']['G']}, K {meta['parts']['K']}; "
         "a card can be in more than one part).", ""]
    labelled = len(om)
    L.append(f"**Omkar's hand verdicts: {labelled} of {n_cards} cards.**" +
             ("" if labelled == n_cards else " **The audit is not finished: every number that needs a hand verdict says PENDING.**"))
    L.append("")
    agree_rows = []

    def part_stats(tag, wrong_if):
        cards = [c for c, e in key.items() if tag in e["parts"]]
        lab = [c for c in cards if c in om]
        wrong = [c for c in lab if wrong_if(om[c]["verdict"], key[c])]
        unsure = [c for c in lab if om[c]["verdict"] == "cannot_tell"]
        return cards, lab, wrong, unsure

    # R: random rejects
    cards, lab, wrong, unsure = part_stats("R", lambda v, e: v == "keep")
    L += ["## Part R: 30 random rejects (the only part that supports a rate)", ""]
    if len(lab) < len(cards):
        L += [f"PENDING: {len(lab)} of {len(cards)} labelled.", ""]
    else:
        lo, hi = clopper_pearson(len(wrong), len(cards))
        N = meta["population"]["rejects"]
        L += [f"**The filter was wrong on {len(wrong)} of {len(cards)} random rejects** (Omkar said keep). "
              f"{len(unsure)} more were 'cannot tell'.", "",
              f"What a sample of {len(cards)} can honestly show: the observed miss rate is {len(wrong)}/{len(cards)} = "
              f"{len(wrong) / len(cards):.1%}. The exact 95% interval (Clopper-Pearson) is **{lo:.1%} to {hi:.1%}**. "
              f"That is an **estimate** for the {N} rejects of this one corpus, not a measured rate: if the true rate "
              f"were at the top of the interval, about {round(hi * N)} of the {N} rejects would be postings Omkar wants. "
              "A sample this size cannot rule that out, and it says nothing about other boards or other weeks.", ""]
        if wrong:
            L.append("Missed postings: " + "; ".join(f"card {c} ({key[c]['title']}: {om[c]['note'] or 'no note'})" for c in wrong))
            L.append("")
    for tag, title, wrong_if, what in [
            ("C", "Part C: close calls (score within 1.0 of the threshold)", lambda v, e: v != e["filter_verdict"] and v != "cannot_tell", "disagreed with the filter"),
            ("G", "Part G: gate near-misses (score ≥ threshold, one gate failed)", lambda v, e: v == "keep", "should have been kept"),
            ("K", "Part K: every kept posting", lambda v, e: v == "reject", "should have been rejected (false positives)")]:
        cards, lab, wrong, unsure = part_stats(tag, wrong_if)
        L += [f"## {title}", ""]
        if len(lab) < len(cards):
            L.append(f"PENDING: {len(lab)} of {len(cards)} labelled.")
        else:
            L.append(f"**{len(wrong)} of {len(cards)} {what}**; {len(unsure)} 'cannot tell'. "
                     "This part was chosen on purpose, not at random, so it shows *where* the filter errs, not *how often*.")
        L.append("")
    changed_now = [c for c in key if now[c] != key[c]["filter_verdict"]]
    L += [f"## Filter v{meta['filter_version']} (when drawn) vs v{cfg_now['version']} (now)", "",
          f"{len(changed_now)} of {n_cards} cards have a different verdict now: " +
          ("; ".join(f"card {c} {key[c]['title']} ({key[c]['filter_verdict']} → {now[c]})" for c in changed_now) or "none") +
          ". Parts R/C/G/K and their numbers above use the verdict at draw time, because that is the filter the sample measured.", ""]
    L += ["## Every card", "", f"| Card | Parts | Company · title | Filter v{meta['filter_version']} (score) | Filter v{cfg_now['version']} | Omkar | Omkar's note | Claude 2nd rater |",
          "|---:|---|---|---|---|---|---|---|"]
    for c in sorted(key):
        e = key[c]
        o = om.get(c, {})
        r = cl.get(c, {})
        cv = r.get("verdict") or ("invalid" if r else "—")
        L.append(f"| {c} | {','.join(e['parts'])} | {e['title'][:70].replace('|', '/')} | {e['filter_verdict']} ({e['score']}) | {now[c]} | "
                 f"{o.get('verdict', 'PENDING')} | {(o.get('note') or '').replace('|', '/')[:90]} | {cv} |")
        if o and r.get("verdict"):
            agree_rows.append((o["verdict"], r["verdict"], e["filter_verdict"]))
    L += ["", "## Second rater (Claude) — not a hand verdict", "",
          f"{sum(1 for r in cl.values() if r.get('verdict'))} of {n_cards} cards have a valid Claude verdict "
          f"({sum(1 for r in cl.values() if r.get('invalid'))} invalid). Each is one fresh `claude -p` call with the same rule and "
          "the same card, recorded with its time in `audit/claude-second-rater.jsonl`. Claude's verdicts never change the "
          "audit's numbers above; they only show where a second reader disagrees."]
    if agree_rows:
        n = len(agree_rows)
        oc = sum(o == c for o, c, _ in agree_rows)
        of = sum(o == fv for o, _, fv in agree_rows)
        L.append("")
        L.append(f"On the {n} cards with both: Omkar and Claude agree on {oc} ({oc / n:.0%}); Omkar and the filter agree on {of} ({of / n:.0%}).")
    else:
        fc = [(r["verdict"], key[c]["filter_verdict"]) for c, r in cl.items() if r.get("verdict")]
        if fc:
            a = sum(x == y for x, y in fc)
            L.append("")
            L.append(f"Until Omkar labels: Claude agrees with the filter on {a} of {len(fc)} cards. This is not an error rate; neither is a hand verdict.")
    store.write_text("audit/AUDIT-RESULTS.md", "\n".join(L) + "\n")
    return labelled, n_cards


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["draw", "label", "show", "claude-rate", "report"])
    ap.add_argument("--run")
    ap.add_argument("--card", type=int, help="label/show: card number")
    ap.add_argument("--verdict", help="label: keep | reject | cannot_tell (or k / r / c)")
    ap.add_argument("--note", default="", help="label: your reason, in your words")
    ap.add_argument("--replace", action="store_true", help="label: change a card's verdict (the old row is kept)")
    a = ap.parse_args(argv)
    if a.cmd == "draw":
        m = draw(a.run)
        print(json.dumps(m, indent=1))
    elif a.cmd == "show":
        show(a.card)
    elif a.cmd == "label" and a.verdict is not None:
        if a.card is None:
            raise SystemExit("--verdict needs --card N (see `python3 -m js3.audit show`)")
        label_one(a.card, a.verdict, a.note, replace=a.replace)
    elif a.cmd == "label":
        label()
    elif a.cmd == "claude-rate":
        claude_rate()
    else:
        n, total = report()
        print(f"wrote audit/AUDIT-RESULTS.md ({n} of {total} cards hand-labelled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
