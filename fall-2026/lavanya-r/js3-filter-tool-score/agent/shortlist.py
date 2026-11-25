"""The source-grounded shortlist (Chapter 7).

1. Shortlist = the 10 highest-scoring postings kept by FILTER.md v1.1
   (ties broken by key), from out/filter/v1.1/decisions.jsonl.
2. Each posting's justification is turned into claims: one per thing the
   filter matched (role word, topic words, skills, US location), plus the
   two fit claims the filter only implies (experience, sponsorship).
3. Claude labels every claim supported / contradicted / insufficient with an
   exact quote (one `claude -p` call per posting; raw replies saved).
4. agent.evidence.check_label re-checks every label: a quote not found in
   the posting turns the label into "insufficient".

python3 -B -m agent.shortlist          # calls Claude for postings not yet labelled
python3 -B -m agent.shortlist --table  # prints SHORTLIST.md's tables
"""

import datetime
import json
import pathlib
import subprocess
import sys
import tempfile

from agent import corpus, evidence

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "out" / "shortlist"
N = 10
PROMPT = """You label claims about one job posting against the posting's own text.

For each numbered claim, give exactly one label:
- "supported": an exact quote from the POSTING says the claim. Containing the same word is not enough: the quote must say what the claim says.
- "contradicted": an exact quote from the POSTING says the opposite.
- "insufficient": the posting does not say it either way, or only mentions the word without making the claim.

The quote must be copied character for character from the POSTING (title, location or text), at most 30 words. Use "" for insufficient. Use nothing outside the posting.

Answer with one JSON list and nothing else:
[{"n": 1, "label": "...", "quote": "..."}, ...]
"""


def claims_for(d):
    m, cl = d["matched"], []
    if m["S1"]:
        cl.append(("role", f"The job is a {' / '.join(m['S1'])} role."))
    for w in m["S2"]:
        cl.append(("topic", f"The day-to-day work involves {w}."))
    for s in m["S3"]:
        cl.append(("skill", f"The role uses {s}, which Priya has shipped with."))
    cl.append(("location", f"The job can be done in the US ({m['R3'][0]})."))
    cl.append(("experience", "The job is open to someone with less than one "
                             "year of full-time experience."))
    cl.append(("sponsorship", "The employer will sponsor a US work visa."))
    return [{"n": i, "topic": t, "claim": c} for i, (t, c) in enumerate(cl, 1)]


def shortlist():
    recs = [json.loads(l) for l in open(HERE / "out/filter/v1.1/decisions.jsonl")]
    kept = [r for r in recs if r["verdict"] == "keep"]
    kept.sort(key=lambda r: (-r["score"], r["key"]))
    return kept[:N]


def label(p, claims, cwd):
    body = "\n".join(f"{c['n']}. {c['claim']}" for c in claims)
    prompt = (f"{PROMPT}\n## CLAIMS\n{body}\n\n## POSTING\nTitle: "
              f"{p['title'].strip()}\nLocation: {'; '.join(p['locations'])}\n\n"
              f"{p['text']}\n")
    t0 = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    r = subprocess.run(["claude", "-p", "--model", "sonnet", "--tools", "",
                        "--no-session-persistence", "--output-format", "json"],
                       input=prompt, capture_output=True, text=True, cwd=cwd,
                       timeout=300)
    return {"started": t0, "exit": r.returncode, "stdout": r.stdout,
            "stderr": r.stderr[-2000:]}


def parse(raw):
    text = json.loads(raw["stdout"])["result"]
    return json.loads(text[text.index("["): text.rindex("]") + 1])


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    posts = {p["key"]: p for p in corpus.load(HERE / "runs/2026-11-24T220432Z-live")}
    cwd = tempfile.mkdtemp(prefix="js3-shortlist-")   # outside the repo
    for d in shortlist():
        f = OUT / (d["key"].replace("/", "__") + ".json")
        if f.exists():
            continue
        claims = claims_for(d)
        raw = label(posts[d["key"]], claims, cwd)
        f.write_text(json.dumps({"key": d["key"], "claims": claims, "raw": raw},
                                ensure_ascii=False, indent=1))
        print("labelled", d["key"])


def results():
    posts = {p["key"]: p for p in corpus.load(HERE / "runs/2026-11-24T220432Z-live")}
    out = []
    for rank, d in enumerate(shortlist(), 1):
        saved = json.loads((OUT / (d["key"].replace("/", "__") + ".json")).read_text())
        by_n = {x["n"]: x for x in parse(saved["raw"])}
        checked = []
        for c in saved["claims"]:
            got = by_n.get(c["n"], {"label": "insufficient", "quote": ""})
            checked.append(evidence.check_label(
                posts[d["key"]], dict(c, label=got["label"], quote=got["quote"])))
        out.append({"rank": rank, "key": d["key"], "title": d["title"].strip(),
                    "score": d["score"], "labelled_at": saved["raw"]["started"],
                    "claims": checked,
                    "answer": evidence.answer(posts[d["key"]], checked)})
    return out


def table():
    for r in results():
        print(f"\n### {r['rank']}. {r['title']} ({r['key'].split('/')[1]}), score {r['score']}\n")
        print(f"Labelled by Claude (sonnet, `claude -p`) at {r['labelled_at']}; "
              f"re-checked by `agent/evidence.py`. Agent's answer: experience "
              f"**{r['answer'].get('experience')}**, sponsorship "
              f"**{r['answer'].get('sponsorship')}**.\n")
        print("| # | Claim | Claude's label | Quote | Final label | Check |")
        print("|---|---|---|---|---|---|")
        for c in r["claims"]:
            q = (c["quote"] or "").replace("|", "/")
            print(f"| {c['n']} | {c['claim']} | {c['label']} | {q} | "
                  f"**{c['final']}** | {c['why']} |")


if __name__ == "__main__":
    table() if "--table" in sys.argv else run()
