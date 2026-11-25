"""The sampling report and the prompt experiment (the brief's Step 4, parts 1 and 2).

  python3 tools/experiment.py sample [--times 5]        repeated calls, baseline prompt, the 5 development
                                                         postings the rule passes (the other 5 fail on location
                                                         or title, which leaves Claude nothing to weigh)
  python3 tools/experiment.py run PROMPT development     one call per development posting
  python3 tools/experiment.py run PROMPT held_out        only once both development runs exist, and only once
  python3 tools/experiment.py report                     rebuild experiment/SAMPLING.md and EXPERIMENT.md
                                                         from the saved calls alone (offline, no Claude)

Every call is a fresh conversation (a new CLI process, no saved session) and is saved before it is counted.
An answer the validator rejects counts as a miss. Labels come from labels/labels.json, paired by posting id.
"""

from __future__ import annotations

import difflib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import claude_judge, rule  # noqa: E402
from job_agent import resume as resume_mod  # noqa: E402

EXPERIMENT = REPO / "experiment"
BASELINE_RESPONSE = REPO / "runs" / "2026-10-30T093102Z" / "response.json"
SETS = ("development", "held_out")
Z = 1.96  # 95% Wilson interval

# The written conclusions and notes. Drafted by Claude Code from the saved calls on 2026-10-30; the calls are never
# asked again (the tool refuses to re-run a set), so the numbers they cite stay true.
SAMPLING_CONCLUSIONS = (
    "Repeating a verdict shows repeatability, not correctness. Posting 4 got \"relevant\" on all five tries, and my "
    "label says \"not_relevant\" (a required specialty Jane lacks); posting 1 got \"relevant\" on all five tries "
    "too, though four of those five replies break the contract's three-sentence limit. The prompt applies its seven "
    "checks the same way every time, and those checks say nothing about specialties. Postings 7 and 8 got my "
    "label's verdict on every valid try.\n\n"
    "The verdict did vary on one posting, inside broken replies. Three replies on posting 5 held two answers: a first "
    "JSON object saying \"not_relevant\" with a confused justification, then a line beginning \"Correction\", then "
    "a second object saying \"relevant\". The validator rejected all three as not one JSON object, so they count as "
    "no valid judgment; a looser parser would have kept one of the two answers without saying so. Both valid replies "
    "on posting 5 matched my label.\n\n"
    "The format rules matter as much as the verdicts: under the contract's validator 8 of the 25 replies are rejected "
    "(3 for two answers in one reply, 5 for four-sentence justifications) and 2 of the 5 postings got one verdict on "
    "every try; under the validator as it first ran, 3 were rejected and 4 of 5 postings were unanimous.\n\n"
    "What these 25 calls cannot show: five tries per posting cannot pin down a rate (3 of 5 has a 95% Wilson interval "
    "of 23% to 88%); the five postings come from one board on one day, chosen because the rule passes them, not at "
    "random; and another model, prompt or day could behave differently. Agreement with my label is agreement with "
    "one person's reading."
)
EXPERIMENT_CONCLUSIONS = (
    "On the development set the revision scored 10 of 10 and the baseline 8 of 10. That gain was expected: the one "
    "change was chosen after seeing the baseline's two development misses (postings 1 and 4, both labeled as a "
    "missing specialty), so the development set is no longer a fair test of it.\n\n"
    "On the held-out set, run once per prompt after both development runs, the scores depend on two things settled "
    "after the runs. With the contract's validator and my current labels, the baseline scored 8 of 10 and the "
    "revision 9 of 10; with my first labels it is 8 to 8; with the validator as it first ran it was 10 to 9 for the "
    "baseline (first labels) or 9 to 10 (current labels). The revision's one-posting edge comes from posting 11, "
    "which I relabeled after seeing the revision call it not relevant, so it is not an independent test.\n\n"
    "What the specialty point did is clear even so. In the replies as received it changed exactly three verdicts, all "
    "from relevant to not relevant (postings 1, 4 and 11), and no other. On the ten postings that need judgment (the "
    "rule passes them), the revision matched my labels on 5 of 5 and 4 of 5, and the baseline and the rule on 3 of 5 "
    "each.\n\n"
    "The rule (a record) scored 8 of 10 on both sets. Its held-out misses are posting 11 and posting 19, whose "
    "requirement \"5+ years in one or more of: ML systems, performance engineering, distributed systems, or HPC.\" "
    "never says \"experience\", so check 7 as written skips it; one other rule-relevant posting on the board "
    "(Software Engineer, Data Infrastructure) has the same gap. Both prompts called posting 19 not relevant. The "
    "majority class scored 7 of 10 on both sets.\n\n"
    "How little ten cases show: one posting moves a pass rate by 10 points, every interval overlaps the others, and "
    "each prompt answered each posting once, while the sampling report shows a reply can break the format. This "
    "experiment cannot say that either prompt is better."
)
EVIDENCE_NOTES = (
    "- The validator as first written did not check the contract's limit of three sentences per justification. An "
    "independent review found the gap on 2026-10-30; the validator now enforces it, and every saved reply was "
    "re-checked, not asked again. Nine replies have four sentences: four in this experiment, five in the sampling.\n"
    "- I relabeled posting 11 (Systems Software Engineer, Silicon Bringup) from relevant to not relevant on 2026-10-30, "
    "after the Claude calls, when the review pointed out that its required lines are the same kind of specialty I "
    "used for postings 1 and 4. The first label is kept in labels/labels.json and in commit 882909e.\n"
    "- For the ten postings the rule rejects, I confirmed my labels in one answer, against the rule's record.\n"
    "- Claude Code read the held-out postings' text and my held-out labels while preparing my labeling questions, "
    "before any Claude judge call, and then proposed the three candidate changes; I chose one from the development "
    "results. The held-out set ran once per prompt, after both development runs, as tools/experiment.py enforces.\n"
    "- Before publishing, the command field of the saved calls was edited to write this Mac's home folder as ~, in "
    "every commit, so no account name is public. Nothing else in any record changed."
)

def load():
    jobs = {j["id"]: j for j in json.loads(BASELINE_RESPONSE.read_bytes())["jobs"]}
    labels = json.loads((REPO / "labels" / "labels.json").read_text(encoding="utf-8"))["labels"]
    jane = resume_mod.load(REPO / "persona" / "jane-doe.json")
    return jobs, labels, jane


def sampling_postings(jobs, labels, jane):
    return [l for l in labels if l["set"] == "development" and rule.judge(jobs[l["id"]], jane)["verdict"] == "relevant"]


def call(posting, jane, prompt: Path, folder: Path, label: str, model: str):
    verdict = claude_judge.judge(posting, jane, prompt_path=prompt, record_dir=folder, model=model, label=label)
    print(f"  {label}: {verdict['verdict'] or 'no valid judgment'}"
          + ("" if verdict["valid"] else f" ({verdict.get('reason', '')[:120]})"))
    return verdict


def sample(times: int, model: str) -> int:
    jobs, labels, jane = load()
    folder = EXPERIMENT / "sampling"
    if folder.exists():
        print(f"refused: experiment/{folder.name} exists; saved calls are never replaced")
        return 3
    for item in sampling_postings(jobs, labels, jane):
        print(f"posting {item['n']}: {item['title']}")
        for attempt in range(1, times + 1):
            call(jobs[item["id"]], jane, REPO / "prompts" / "baseline.txt", folder, f"n{item['n']:02d}-try{attempt}", model)
    return 0


def run(prompt: Path, part: str, model: str) -> int:
    if part not in SETS:
        print(f"the set must be one of {SETS}")
        return 2
    prompt = prompt if prompt.is_absolute() else (REPO / prompt)
    folder = EXPERIMENT / f"{prompt.stem}-{part}"
    if folder.exists():
        print(f"refused: experiment/{folder.name} exists; each prompt runs on each set once")
        return 3
    if part == "held_out":
        developed = sorted(p.name[: -len("-development")] for p in EXPERIMENT.glob("*-development"))
        if "baseline" not in developed or len(developed) != 2 or prompt.stem not in developed:
            print("refused: the held-out set runs only after the baseline and exactly one revision ran on the "
                  f"development set, and only for those two prompts (found: {developed})")
            return 3
    jobs, labels, jane = load()
    print(f"{prompt.name} on the {part} set:")
    for item in (l for l in labels if l["set"] == part):
        call(jobs[item["id"]], jane, prompt, folder, f"n{item['n']:02d}", model)
    return 0


# Reports, from the saved calls only.

def wilson(k: int, n: int):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denominator = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denominator
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


def records(folder: Path):
    """Each saved call, scored two ways: by the validation it got when it ran, and by today's validator, which also
    enforces the contract's limit of three sentences per justification (the first validator did not check it)."""
    found = []
    for path in sorted(folder.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        text = data.get("answer_text") or ""
        as_run = bool(data.get("validation", {}).get("valid"))
        answer = json.loads(text) if as_run else None
        if text:
            now, problems_now = claude_judge.validate(text, data["sent"]["data"])
        else:
            now, problems_now = None, data.get("validation", {}).get("problems", [])
        valid_now = bool(text) and not problems_now
        found.append({"file": f"{folder.name}/{path.name}", "label": data.get("label", ""), "id": data["posting_id"],
                      "answer_text": text, "valid": as_run, "verdict": (answer or {}).get("verdict"),
                      "valid_now": valid_now, "verdict_now": now["verdict"] if valid_now else None,
                      "problems_now": problems_now, "justification": (answer or {}).get("justification"),
                      "model": data.get("model"), "date": (data.get("started_at") or "")[:10],
                      "problems": data.get("validation", {}).get("problems", []),
                      "prompt_sha256": data.get("prompt", {}).get("sha256")})
    return found


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"


def interval(k, n):
    low, high = wilson(k, n)
    return f"{100 * low:.0f}% to {100 * high:.0f}%"


def cell(text) -> str:
    return str(text).replace("|", "\\|").strip()


def label_of(item, first=False):
    return item.get("first_label", item["label"]) if first else item["label"]


def said(c, strict=True):
    verdict = c["verdict_now"] if strict else c["verdict"]
    return verdict or "invalid"


def sampling_report(jobs, labels, jane) -> str:
    folder = EXPERIMENT / "sampling"
    calls = records(folder) if folder.exists() else []
    by_id = {l["id"]: l for l in labels}
    postings = sampling_postings(jobs, labels, jane)
    out = ["# Sampling report", "",
           "Generated by `python3 tools/experiment.py report` from the saved calls in `experiment/sampling/`.", "",
           "The baseline prompt contract (`prompts/baseline.txt`), asked about the same posting in fresh "
           "conversations: each call is a new Claude Code process with no saved session. The postings are the five "
           "development postings the rule passes; the other five fail on location or title, which leaves Claude "
           "nothing to weigh. Every verdict is Claude's judgment, compared with my hand label.", "",
           "Each reply is scored two ways: by the validator as it ran on 2026-10-30, and by the validator as the "
           "contract is written, which also rejects a justification of more than three sentences. The first validator "
           "did not check that limit; an independent review found the gap, and the saved replies were re-checked, "
           "not asked again.", "",
           "| # | Posting | My label | Verdicts, contract's validator | Verdicts, validator as run |",
           "|---|---|---|---|---|"]
    totals = {True: [0, 0, 0, 0], False: [0, 0, 0, 0]}  # calls, same as label, unanimous postings, invalid
    for item in postings:
        mine = [c for c in calls if c["id"] == item["id"]]
        row = [str(item["n"]), cell(item["title"]), item["label"]]
        for strict in (True, False):
            verdicts = [said(c, strict) for c in mine]
            totals[strict][0] += len(verdicts)
            totals[strict][1] += sum(v == item["label"] for v in verdicts)
            totals[strict][2] += len(set(verdicts)) == 1
            totals[strict][3] += verdicts.count("invalid")
            row.append(", ".join(verdicts))
        out.append("| " + " | ".join(row) + " |")
    models = sorted({c["model"] for c in calls if c["model"]})
    dates = sorted({c["date"] for c in calls})
    out += ["", f"Calls: {len(calls)} ({', '.join(models) or 'no model'}; {', '.join(dates) or 'no date'})."]
    for strict, name in ((True, "With the contract's validator"), (False, "With the validator as run")):
        n, same, unanimous, invalid = totals[strict]
        out.append(f"{name}: {invalid} invalid; same as my label {pct(same, n)}; postings with one verdict on every "
                   f"try {unanimous} of {len(postings)}.")
    out += ["", "## Each reply, as received", ""]
    for c in calls:
        item = by_id[c["id"]]
        if c["justification"]:
            note = c["justification"]
            if not c["valid_now"]:
                note += " (Rejected by the contract's validator: " + "; ".join(c["problems_now"]) + ".)"
        else:
            note = ("; ".join(c["problems"]) + ". The reply, as received, begins: " + json.dumps(c["answer_text"][:160])
                    + " and later says: " + json.dumps(_correction(c["answer_text"])))
        out.append(f"- `{c['label']}` (posting {item['n']}, {c['date']}): **{c['verdict'] or 'no valid judgment'}**. {note}")
    out += ["", "## What this shows, and what it cannot", "", SAMPLING_CONCLUSIONS, ""]
    return "\n".join(out)


def _correction(text: str) -> str:
    at = text.find("Correction")
    return text[at: at + 120] if at >= 0 else "(no correction line)"


def experiment_report(jobs, labels, jane) -> str:
    runs = {}
    for part in SETS:
        for folder in sorted(EXPERIMENT.glob(f"*-{part}")):
            runs[(folder.name[: -len(f"-{part}")], part)] = records(folder)
    prompts = sorted({stem for stem, _ in runs}, key=lambda s: (s != "baseline", s))
    verdict_of = {l["id"]: rule.judge(jobs[l["id"]], jane)["verdict"] for l in labels}

    def score(stem, part, strict, first, only=None):
        mine = [l for l in labels if l["set"] == part and (only is None or l["id"] in only)]
        calls = runs.get((stem, part))
        if calls is None:
            return None, len(mine)
        by_id = {c["id"]: c for c in calls}
        return sum(1 for l in mine if l["id"] in by_id and said(by_id[l["id"]], strict) == label_of(l, first)), len(mine)

    out = ["# Prompt experiment", "",
           "Generated by `python3 tools/experiment.py report` from the saved calls in `experiment/<prompt>-<set>/`.", "",
           "My 20 hand labels (`labels/labels.json`) are the answer key. Each prompt was asked once per posting; a "
           "pass is a valid answer equal to my label, and an answer the validator rejects counts as a miss. The "
           "majority class answers `not_relevant` every time. The rule's record is computed from the same postings.", "",
           "The main tables use the contract as written (its validator, including the limit of three sentences per "
           "justification, applied to the saved replies) and my labels as they now stand (posting 11 relabeled, see "
           "the notes). \"How the numbers move\" shows the other scorings.", ""]
    for part in SETS:
        mine = [l for l in labels if l["set"] == part]
        n = len(mine)
        majority = sum(1 for l in mine if l["label"] == "not_relevant")
        rule_ok = sum(1 for l in mine if verdict_of[l["id"]] == l["label"])
        out += [f"## {'Development' if part == 'development' else 'Held-out'} set ({n} postings: "
                f"{n - majority} relevant, {majority} not relevant by my labels)", "",
                "| Judge | Pass rate | 95% Wilson interval |", "|---|---|---|",
                f"| Majority class (always not_relevant) | {pct(majority, n)} | {interval(majority, n)} |",
                f"| Rule (record) | {pct(rule_ok, n)} | {interval(rule_ok, n)} |"]
        for stem in prompts:
            ok, total = score(stem, part, True, False)
            if ok is None:
                out.append(f"| Claude, {stem} prompt | not run | |")
                continue
            invalid = sum(1 for c in runs[(stem, part)] if not c["valid_now"])
            out.append(f"| Claude, {stem} prompt | {pct(ok, total)}{f', {invalid} invalid' if invalid else ''} | "
                       f"{interval(ok, total)} |")
        out += ["", "| # | Posting | My label | Rule | " + " | ".join(f"Claude, {s}" for s in prompts) + " |",
                "|---|---|---|---|" + "---|" * len(prompts)]
        for l in mine:
            shown_label = l["label"] + (f" (first: {l['first_label']})" if "first_label" in l else "")
            row = [str(l["n"]), cell(l["title"]), shown_label, verdict_of[l["id"]]]
            for stem in prompts:
                c = next((c for c in runs.get((stem, part)) or [] if c["id"] == l["id"]), None)
                if c is None:
                    row.append("not run")
                else:
                    text = said(c, True)
                    if said(c, False) != text:
                        text += f" (as run: {said(c, False)})"
                    row.append(text)
            out.append("| " + " | ".join(row) + " |")
        out.append("")
    out += ["## How the numbers move", "",
            "| Set | Judge | As run, first labels | As run, current labels | Contract's validator, first labels | "
            "Contract's validator, current labels |", "|---|---|---|---|---|---|"]
    for part in SETS:
        mine = [l for l in labels if l["set"] == part]
        name = "Development" if part == "development" else "Held-out"
        majority = [sum(1 for l in mine if label_of(l, first) == "not_relevant") for first in (True, False)]
        rule_ok = [sum(1 for l in mine if verdict_of[l["id"]] == label_of(l, first)) for first in (True, False)]
        out.append(f"| {name} | Majority class | {majority[0]}/10 | {majority[1]}/10 | {majority[0]}/10 | {majority[1]}/10 |")
        out.append(f"| {name} | Rule (record) | {rule_ok[0]}/10 | {rule_ok[1]}/10 | {rule_ok[0]}/10 | {rule_ok[1]}/10 |")
        for stem in prompts:
            cells = []
            for strict, first in ((False, True), (False, False), (True, True), (True, False)):
                ok, total = score(stem, part, strict, first)
                cells.append("not run" if ok is None else f"{ok}/{total}")
            out.append(f"| {name} | Claude, {stem} | " + " | ".join(cells) + " |")
    passed = {l["id"] for l in labels if verdict_of[l["id"]] == "relevant"}
    out += ["", "## The ten postings that need judgment", "",
            "The rule passes ten of the twenty postings. The other ten fail it on location or title, and part 1 of my "
            "labeling rule makes them not relevant, so every judge agrees with those by construction: I confirmed "
            "all ten in one answer, against the rule's record. On the ten that need judgment (contract's validator, "
            "current labels):", "",
            "| Set | Rule (record) | " + " | ".join(f"Claude, {s}" for s in prompts) + " |",
            "|---|---|" + "---|" * len(prompts)]
    for part in SETS:
        mine = [l for l in labels if l["set"] == part and l["id"] in passed]
        rule_ok = sum(1 for l in mine if verdict_of[l["id"]] == l["label"])
        cells = []
        for stem in prompts:
            ok, total = score(stem, part, True, False, only=passed)
            cells.append("not run" if ok is None else f"{ok}/{total}")
        out.append(f"| {'Development' if part == 'development' else 'Held-out'} | {rule_ok}/{len(mine)} | "
                   + " | ".join(cells) + " |")
    out.append("")
    revisions = [s for s in prompts if s != "baseline"]
    if revisions:
        diff = difflib.unified_diff((REPO / "prompts" / "baseline.txt").read_text(encoding="utf-8").splitlines(),
                                    (REPO / "prompts" / f"{revisions[0]}.txt").read_text(encoding="utf-8").splitlines(),
                                    "prompts/baseline.txt", f"prompts/{revisions[0]}.txt", lineterm="", n=0)
        out += ["## The one change", "", "```diff", *diff, "```", ""]
    out += ["## What this shows, and what it cannot", "", EXPERIMENT_CONCLUSIONS, "",
            "## Notes on the evidence", "", EVIDENCE_NOTES, ""]
    return "\n".join(out)


def report() -> int:
    jobs, labels, jane = load()
    (EXPERIMENT / "SAMPLING.md").write_text(sampling_report(jobs, labels, jane), encoding="utf-8")
    (EXPERIMENT / "EXPERIMENT.md").write_text(experiment_report(jobs, labels, jane), encoding="utf-8")
    print("wrote experiment/SAMPLING.md and experiment/EXPERIMENT.md")
    return 0


def main(argv) -> int:
    model = argv[argv.index("--model") + 1] if "--model" in argv else claude_judge.DEFAULT_MODEL
    if argv[:1] == ["sample"]:
        return sample(int(argv[argv.index("--times") + 1]) if "--times" in argv else 5, model)
    if argv[:1] == ["run"] and len(argv) >= 3:
        return run(Path(argv[1]), argv[2], model)
    if argv[:1] == ["report"]:
        return report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
