"""What moves the score (FILTER.md section 5): one change to one object at a time, measured on the held-out labels.

    python3 -m js3.measure ask        # ask Claude about the 16 held-out postings in 3 set-ups, saving every reply
    python3 -m js3.measure score      # compare every set-up with my held-out labels (audit/labels.csv)

Set-ups (each differs from the baseline in exactly one object):
  A  baseline: prompt baseline-v1, the whole posting
  B  M3, the prompt: revision-v1 (must-haves only), the whole posting
  C  M4, the context: baseline-v1, the title, location and requirement lines only
The filter's own changes (M1 the filter file, M2 the keep threshold) need no Claude and are scored here too.
"""

import csv
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from js3 import claude_judge
from js3.filter import evaluate, text_of
from js3.load import FOLDER, load, load_persona

OUT = FOLDER / "measure"
SETUPS = {
    "A-baseline": {"prompt": "baseline-v1.txt", "context": "whole"},
    "B-M3-prompt-revision-v1": {"prompt": "revision-v1.txt", "context": "whole"},
    "C-M4-context-requirements-only": {"prompt": "baseline-v1.txt", "context": "requirements"},
}
REQUIREMENT = re.compile(r"(?i)(\d+\s*\+?\s*(?:-|–|to)?\s*\d*\s*years|years of|require|must|clearance|degree|"
                         r"bachelor|master|phd|new grad|graduat|intern|senior|proficien|experience|you have|"
                         r"you(?:'|’)ll need|qualifications|knowledge of|familiar|strong)")


def requirement_lines(posting):
    markup = html.unescape(posting.get("content") or "")
    lines = [text_of(part) for part in re.split(r"(?i)</li>|</p>|<br\s*/?>|</h[1-6]>|\n", markup)]
    return [line for line in lines if line and REQUIREMENT.search(line)]


def with_context(posting, context):
    if context == "whole":
        return posting
    return dict(posting, content=html.escape(" ".join("<p>%s</p>" % html.escape(line)
                                                       for line in requirement_lines(posting))))


def held_out():
    items = json.loads((FOLDER / "audit" / "sample.json").read_text())["items"]
    return [i for i in items if i["set"] == "held_out"]


def ask(workers=4):
    postings = {p["key"]: p for p in load()[0]}
    resume = load_persona()
    jobs = [(name, setup, item) for name, setup in SETUPS.items() for item in held_out()]

    def one(job):
        name, setup, item = job
        path = OUT / "replies" / name / ("item-%02d.json" % item["item"])
        if path.exists():
            return path, "kept"
        posting = with_context(postings[item["key"]], setup["context"])
        record = claude_judge.judgment(posting, resume, claude_judge.ask_claude_cli,
                                       FOLDER / "prompts" / setup["prompt"])
        record.update(setup=name, item=item["item"], key=item["key"], context=setup["context"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return path, record["status"]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for path, status in pool.map(one, jobs):
            print(status, path.relative_to(FOLDER))
    return 0


def my_labels():
    with open(FOLDER / "audit" / "labels.csv", newline="", encoding="utf-8") as handle:
        return {int(r["item"]): r["label"].strip().upper() for r in csv.DictReader(handle) if r["label"].strip()}


def agreement(predicted, truth):
    """Counts against my labels: Y = fit. Returns hits, false keeps, misses and agreement."""
    pairs = [(predicted[i], truth[i]) for i in truth if i in predicted]
    tp = sum(p == "Y" and t == "Y" for p, t in pairs)
    fp = sum(p == "Y" and t == "N" for p, t in pairs)
    fn = sum(p == "N" and t == "Y" for p, t in pairs)
    agree = sum(p == t for p, t in pairs)
    return {"n": len(pairs), "agree": agree, "fit_found": tp, "kept_not_fit": fp, "fit_missed": fn}


def score():
    labels = my_labels()
    items = held_out()
    truth = {i["item"]: labels[i["item"]] for i in items if i["item"] in labels}
    postings = {p["key"]: p for p in load()[0]}
    resume = load_persona()
    rows = {}
    variants = {"v1 (keep at 5, all years)": {"version": "v1"},
                "M1 filter file: must-have years only (on v1)": {"version": "v1", "must_haves_only": True},
                "M2 setting: keep at 4 (on v1)": {"version": "v1", "keep_at": 4},
                "v1.1 (A: D.C.; B: graduation date)": {"version": "v1.1"}}
    for name, options in variants.items():
        rows[name] = agreement({i["item"]: "Y" if evaluate(postings[i["key"]], resume, **options)["outcome"] == "keep"
                                else "N" for i in items}, truth)
    for name in SETUPS:
        predicted, rejected = {}, 0
        for i in items:
            path = OUT / "replies" / name / ("item-%02d.json" % i["item"])
            if not path.exists():
                continue
            record = json.loads(path.read_text())
            if record["status"] == "accepted":
                predicted[i["item"]] = "Y" if record["verdict"] == "MATCH" else "N"
            else:
                rejected += 1
        rows["Claude " + name] = dict(agreement(predicted, truth), rejected_replies=rejected)
    result = {"scored_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "held_out_labels": len(truth),
              "labels_fit": sum(v == "Y" for v in truth.values()), "rows": rows}
    OUT.mkdir(exist_ok=True)
    (OUT / "scores.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit({"ask": ask, "score": score}[sys.argv[1]]())
