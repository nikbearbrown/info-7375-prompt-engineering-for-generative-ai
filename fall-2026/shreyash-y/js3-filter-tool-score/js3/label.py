"""Blind hand labeling: one posting at a time, in the shuffled order of labels/sample.json. It never
shows the filter's verdict, its reasons, or which set (audit or held-out) a posting is in.

Every answer is appended to labels/hand-verdicts.jsonl the moment it is typed, with the time, so you
can stop with q and carry on later; the last answer for a posting is the one that counts, and earlier
ones stay in the file. Run from this folder:  python3 -m js3 label      (progress: --status)"""
import datetime
import json
import pathlib
import shutil
import sys
import textwrap

from js3 import corpus

HERE = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = HERE / "labels" / "sample.json"
OUT = HERE / "labels" / "hand-verdicts.jsonl"

ALEX = ("Alex: lives in Boston, MA; remote is fine if it can be done from Massachusetts; 3 years of experience; "
        "wants Software / Backend / Full Stack / AI / ML / LLM Engineer roles; skills Python, Java, TypeScript, "
        "FastAPI, React, LangGraph, RAG, PyTorch, SQL, Docker; no Director/Staff/Principal/Manager/Lead roles; "
        "no internships, part-time, temporary, contract-only or unpaid jobs; will not relocate.")
QUESTION = "Should this job reach Alex?  y = yes   n = no   ? = I cannot tell from the posting"
KEYS = "f = full text   b = go back one   q = stop (answers are saved)"


def answers():
    out = {}
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            if line.strip():
                a = json.loads(line)
                out[a["key"]] = a
    return out


def wrap(text, width):
    return "\n".join(textwrap.fill(par, width) for par in text.split("\n") if par.strip())


def view(p, n, total, full=False):
    width = min(110, shutil.get_terminal_size((100, 30)).columns - 2)
    content = p["content"]
    req = " ".join(content[s:e] for s, e, k, h in p["blocks"] if k in ("req", "pref") and not h)
    lines = [
        "", "=" * width, f"  {n} of {total}    {p['board']} ({p['ats']})  id {p['id']}", "=" * width,
        f"Title:       {p['title']}",
        f"Location:    {p['location'] or '(not given)'}",
        f"Offices:     {', '.join(p['offices']) or '(not given)'}",
        f"Department:  {', '.join(p['departments']) or '(not given)'}",
        f"Employment:  {p.get('employment_type') or '(not given)'}      Workplace: {p.get('workplace_type') or '(not given)'}",
        f"Open today:  {'yes' if p['open_in_latest_run'] else 'no, closed since ' + str(p['last_seen']) + ' (judge it as if it were open)'}",
        f"URL:         {p.get('url')}",
    ]
    if full:
        lines += ["", "--- Full description ---", wrap(content, width)]
    else:
        lines += ["", "--- Description, first 700 characters (f shows all of it) ---", wrap(content[:700], width)]
        if req:
            lines += ["", "--- What the ad lists under its requirements / preferred headings (first 900) ---",
                      wrap(req[:900], width)]
    lines += ["", wrap(ALEX, width), "", QUESTION, KEYS]
    return "\n".join(lines)


def save(key, n, verdict, note):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rec = {"item": n, "key": key, "verdict": verdict, "note": note,
           "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "by": "Shreyash, typed in python3 -m js3 label"}
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def compact(p, n, total):
    """The same facts as view(), shorter, for answering in the chat instead of this tool."""
    content = p["content"]
    req = " ".join(content[s:e] for s, e, k, h in p["blocks"] if k in ("req", "pref") and not h)
    lines = [f"**{n}.** {p['title']}  ({p['board']})",
             f"   Location: {p['location'] or '(not given)'} | Offices: {', '.join(p['offices']) or '(not given)'} | "
             f"Department: {', '.join(p['departments']) or '(not given)'} | Employment: {p.get('employment_type') or '(not given)'}"
             + ("" if p["open_in_latest_run"] else " | closed since " + str(p["last_seen"])),
             f"   Ad opens: {content[:260].strip()}…"]
    if req:
        lines.append(f"   Under its requirements headings: {req[:380].strip()}…")
    return "\n".join(lines)


def main(argv):
    sample = json.loads(SAMPLE.read_text())
    order = sample["label_order"]
    done = answers()
    if argv and argv[0] == "--print":
        by_key = {p["key"]: p for p in corpus.load()}
        a, b = int(argv[1]), int(argv[2])
        print("\n\n".join(compact(by_key[order[i - 1]], i, len(order)) for i in range(a, b + 1)))
        return 0
    if argv and argv[0] == "--status":
        print(f"{sum(k in done for k in order)} of {len(order)} labeled ({OUT.relative_to(HERE)})")
        return 0
    by_key = {p["key"]: p for p in corpus.load()}
    i = 0
    while i < len(order) and order[i] in done:
        i += 1
    print(f"{len(order)} postings in a shuffled order; {i} already answered. Answers go to {OUT.relative_to(HERE)}.")
    while i < len(order):
        key = order[i]
        print(view(by_key[key], i + 1, len(order)))
        while True:
            try:
                a = input("> ").strip().lower()
            except EOFError:
                return 0
            if a == "f":
                print(view(by_key[key], i + 1, len(order), full=True))
                continue
            if a == "q":
                print(f"Stopped at {i + 1} of {len(order)}. Run it again to carry on.")
                return 0
            if a == "b":
                i = max(0, i - 1)
                break
            if a in ("y", "n", "?"):
                note = input("Note (optional, Enter to skip): ").strip()
                save(key, i + 1, {"y": "yes", "n": "no", "?": "cannot tell"}[a], note)
                i += 1
                break
            print("Type y, n, ?, f, b or q.")
    print(f"All {len(order)} answered. Tell Claude Code you are done; nothing else to do here.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
