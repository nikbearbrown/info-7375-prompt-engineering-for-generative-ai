"""Source-grounded claims for kept postings (FILTER.md "Evidence rules").

    python3 claims.py run VARIANT      ask `claude -p` for claims on every posting the v1.0 filter keeps
    python3 claims.py check VARIANT    check every quote against the posting; write the label sheet and answers
    python3 claims.py confirmed        the agent's answers from MY labels (my_label in base_checked.csv)

VARIANT is one of:
- base         the prompt below, with the full posting
- loose-quote  ONE wording change: the "copy the quote exactly" sentence is removed
- title-only   ONE context change: Claude sees the title and locations, not the description
- no-field-names  ONE wording change: a sentence saying quotes must not include the field names
                ("Title:", "Locations:", "Description:"), added after the base run showed Claude copying them
- base-rerun   NO change: the base prompt run a second time, to see how much a run varies on its own

Claude writes claims; it never decides keep or reject. For each of six fixed claims it gives a status and a quote.
The substring checker then labels each claim:
- the quote is found in the posting (title, locations, or description, after whitespace is collapsed):
  Claude's status stands, until I confirm it;
- the quote is not found, or is empty: the claim is "insufficient", whatever Claude said.
A found quote shows the text is there, not that it says what the claim says (relevance is not entailment).
That second question is mine: I confirm every label in the base sheet.

FILTER.md v1.2 adopts no-field-names as the claims prompt. v1.2 keeps 9 of v1.0's 12 postings, so its claims
are the no-field-names claims on those 9 (measure_changes.py, "v1.2 as adopted").

The agent's answer for a kept posting is "I cannot tell" when its role, seniority, or location claim is
insufficient, or its description is missing; otherwise "keep". Years and sponsorship never force it.
"""
import concurrent.futures
import csv
import io
import json
import os
import re
import subprocess
import sys

import corpus
import filter as F
from policy import Policy
from tools import Tools

CLAUDE = os.environ.get("CLAUDE_BIN", os.path.expanduser(
    "~/Library/Application Support/Claude/claude-code/2.1.331/5cdc5c10ac5c/claude.app/Contents/MacOS/claude"))
VARIANTS = ("base", "loose-quote", "title-only", "no-field-names", "base-rerun")
NO_FIELDS = ('Never include the field names "Title:", "Locations:", or "Description:" in a quote; they are not '
             'part of the posting. ')
CLAIMS = {
    "role": "The job is data, BI, or business analyst work.",
    "seniority": "The job is entry level or junior.",
    "years": "The job requires 2 years of experience or fewer.",
    "location": "The job can be done from the US.",
    "sponsorship": "The employer will sponsor a work visa.",
    "skills": "The job asks for SQL, Python, Tableau, or Excel.",
}
ABSTAIN_ON = ("role", "seniority", "location")
EXACT = ("The quote must be copied exactly, character for character, from the posting text below: "
         "do not paraphrase, shorten inside, or fix typos. ")

PROMPT = """You check job postings for evidence. Below is one job posting. For each of these six claims, decide:
- "supported": the posting says what the claim says;
- "contradicted": the posting says the opposite;
- "insufficient": the posting is silent or ambiguous on it.

Claims:
{claims}

For "supported" or "contradicted", give one short quote from the posting that shows it. {exact}For \
"insufficient", give an empty quote. Do not decide whether anyone should apply.

Answer with JSON only, no other text, in exactly this shape:
{{"claims": [{{"property": "role", "status": "...", "quote": "..."}}, ...]}}
with one entry for each of: role, seniority, years, location, sponsorship, skills.

POSTING
Title: {title}
Locations: {locations}
{body}"""


def prompt(p, variant):
    body = "Description: (not shown)" if variant == "title-only" else f"Description:\n{p['text'] or '(none)'}"
    return PROMPT.format(claims="\n".join(f"- {k}: {v}" for k, v in CLAIMS.items()),
                         exact={"loose-quote": "", "no-field-names": EXACT + NO_FIELDS}.get(variant, EXACT), title=p["title"],
                         locations="; ".join(dict.fromkeys(p["locations"])) or "not given", body=body)


def ask(text):
    done = subprocess.run([CLAUDE, "-p", text, "--output-format", "json", "--max-turns", "1", "--tools", ""],
                          capture_output=True, text=True, timeout=300)
    return json.loads(done.stdout)


def parse(result_text):
    m = re.search(r"\{.*\}", result_text or "", re.S)
    data = json.loads(m.group(0)) if m else {"claims": []}
    return {c.get("property"): c for c in data.get("claims", []) if isinstance(c, dict)}


def collapse(s):
    return re.sub(r"\s+", " ", s or "").strip()


def found(quote, p):
    q = collapse(quote)
    if not q:
        return False
    # Locations are joined exactly as the prompt shows them ("; "), so a quote spanning two of them is found.
    haystack = collapse(" \n ".join([p["title"] or "", "; ".join(dict.fromkeys(p["locations"] or [])),
                                      p["text"] or ""]))
    return q in haystack


def label(claim, p):
    """(checker label, quote found?) for one claim."""
    status = (claim or {}).get("status")
    hit = found((claim or {}).get("quote"), p)
    if status in ("supported", "contradicted") and hit:
        return status, True
    return "insufficient", hit


def answer(labels, p):
    if not p["text"] or any(labels[k] == "insufficient" for k in ABSTAIN_ON):
        return "I cannot tell"
    return "keep"


def safe(key):
    return key.replace("/", "__")


def confirmed(tools):
    """Answers from my_label, the labels I confirmed, instead of the checker's."""
    rows = list(csv.DictReader(tools.read_text("state/claims/base_checked.csv").splitlines()))
    if any(not r["my_label"] for r in rows):
        raise SystemExit("base_checked.csv: my_label is not filled in on every row")
    _, postings = corpus.load(tools)
    by_key = {p["key"]: p for p in postings}
    labels = {}
    for r in rows:
        labels.setdefault(r["key"], {})[r["property"]] = r["my_label"]
    return {k: {"title": by_key[k]["title"], "answer": answer(v, by_key[k]), "labels": v} for k, v in labels.items()}


def main(argv):
    if argv[1:] == ["confirmed"]:
        tools = Tools(Policy())
        answers = confirmed(tools)
        tools.write_text("state/claims/base_answers_my_labels.json", json.dumps(answers, indent=1) + "\n")
        for key, a in answers.items():
            print(f"  {a['answer']:14} {key}  {a['title']}")
        return 0
    if len(argv) != 3 or argv[1] not in ("run", "check") or argv[2] not in VARIANTS:
        print(__doc__)
        return 2
    command, variant = argv[1], argv[2]
    tools = Tools(Policy())
    _, postings = corpus.load(tools)
    kept = [p for p in postings if F.evaluate(p, "1.0")["verdict"] == "keep"]  # claims were run on v1.0's kept set
    folder = f"state/claims/{variant}"
    if command == "run":
        todo = [p for p in kept if not os.path.exists(f"{folder}/{safe(p['key'])}.json")]

        def one(p):
            text = prompt(p, variant)
            out = ask(text)
            return p, {"key": p["key"], "variant": variant, "prompt": text, "model": sorted(out.get("modelUsage", {})),
                       "is_error": out.get("is_error"), "result": out.get("result")}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for p, rec in pool.map(one, todo):
                tools.write_text(f"{folder}/{safe(p['key'])}.json", json.dumps(rec, indent=1) + "\n")
                print(f"{variant}: {p['key']} {'ERROR' if rec['is_error'] else 'ok'}")
        return 0
    rows, answers = [], {}
    for p in kept:
        rec = json.loads(tools.read_text(f"{folder}/{safe(p['key'])}.json"))
        claims = parse(rec["result"])
        labels = {}
        for prop, text in CLAIMS.items():
            c = claims.get(prop)
            labels[prop], hit = label(c, p)
            rows.append({"key": p["key"], "title": p["title"], "property": prop, "claim": text,
                         "claude_status": (c or {}).get("status", "missing"), "quote": (c or {}).get("quote", ""),
                         "quote_found": "yes" if hit else "no", "checker_label": labels[prop], "my_label": "",
                         "note": ""})
        answers[p["key"]] = {"title": p["title"], "answer": answer(labels, p), "labels": labels}
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    tools.write_text(f"state/claims/{variant}_checked.csv", out.getvalue())
    tools.write_text(f"state/claims/{variant}_answers.json", json.dumps(answers, indent=1) + "\n")
    quoted = [r for r in rows if r["claude_status"] in ("supported", "contradicted")]
    print(f"{variant}: {len(kept)} kept postings, {len(rows)} claims; Claude gave {len(quoted)} supported/contradicted, "
          f"quote found for {sum(r['quote_found'] == 'yes' for r in quoted)}")
    for key, a in answers.items():
        print(f"  {a['answer']:14} {key}  {a['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
