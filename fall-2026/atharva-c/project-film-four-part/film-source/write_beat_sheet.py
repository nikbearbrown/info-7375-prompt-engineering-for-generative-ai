#!/usr/bin/env python3
"""Writes ../beat_sheet.json (narration + visual plan) from the locked script, SCRIPT-DRAFT.md v2 (2026-11-22)."""
import json
from pathlib import Path
B = [
 ("E1","executive summary","Hi, I'm Atharva. My final project is Seeded Faults: a tool that checks whether the data-quality tests on a table would actually catch bad data, or just pass.","A table with a row of checkmarks; one turns into a question mark",None,None),
 ("E2","executive summary","That matters because a test that has never failed hasn't proven anything. And now that AI can write tests in seconds, it's easy to ship tests that look complete and that nobody has checked.","An all-passed badge with a crack running through it",None,None),
 ("E3","executive summary","Seeded Faults will score a test suite: from a fixed list of problems, what it caught and what it missed. It'll be a public repository anyone can rerun with one command. It isn't built yet. This film is the plan.","Scoreboard with fault rows and caught / missed columns, rows empty","CONSTRUCTED — planned, no results",None),
 ("I1","introduction","First, what already exists. In October I tried Great Expectations and dbt. I planted fifty missing values in real New York taxi data, and a hand-written check caught all fifty. But neither tool told me what my checks would miss.","Two tool boxes, Great Expectations and dbt, each with a hand-written checklist; 50 / 50 beneath",None,"evidence: ../final-project-film/evidence/2026-10-09-first-planted-fault/ (GX unexpected_count=50; dbt FAIL 50)"),
 ("I2","introduction","Some tools draft the checks for you: Amazon's Deequ, older versions of Great Expectations, and pandera. Pandera's schema inference, run on my data, caught the same fifty. But on five fresh, clean samples from the same month, it flagged thirteen to twenty-five rows every time. I haven't checked yet whether those rows are really bad.","Three boxes that draft checks: Deequ, older Great Expectations, pandera; pandera opens to real holdout output",None,"evidence: evidence/2026-11-22-pandera-infer-schema/output_holdout.txt (14, 17, 16, 13, 25 rows flagged)"),
 ("I3","introduction","Planting bugs on purpose is an old idea: mutation testing goes back to 1978. And a 2025 IBM Research paper already has AI write data checks, then measures how many injected errors those checks catch. So my part is narrower: the dbt tests data teams actually ship, faults specific to one real table, and false alarms counted alongside catches. That matters because those tests guard real pipelines, and a score tells you which to trust.","Code file with bug marks, a data table with the same marks, my narrower part, and why it matters",None,"DeMillo, Lipton, Sayward 1978; arXiv 2509.10572"),
 ("M1","methods","Here's the plan. The data is public: New York's yellow taxi trips for January 2024. Everything runs locally on my laptop, with DuckDB and dbt.","Taxi trips table labelled public, Jan 2024, beside a laptop",None,None),
 ("M2A","methods","Step one was deciding what clean means. When I profiled the month, about three million trips, some of my faults were already there: over one percent of fares are negative, and two percent of trips have zero distance. So I filtered those out first, leaving about two point seven million clean rows.","A bar of 2.96 M trips with slivers for negative fares and zero distance, filtered to 2.7 M clean",None,"evidence: evidence/2026-11-22-data-profile/output.txt; evidence/2026-11-22-baseline-check/output.txt"),
 ("M2B","methods","Step two: lock the faults. I wrote eighteen fault types, with my pass-fail line, and committed them on November twenty-second, before any test was written, so anyone can check the list came first.","The fault catalogue page with its commit hash and date, and a padlock",None,"git commit e5aac1c, 2026-11-22"),
 ("M3","methods","Next, I'll build a script that plants each fault, fifty rows at a time, into its own copy of a ten-thousand-row holdout. I'll write my own dbt tests first. Then Claude Code writes its tests from a separate sample, so it never sees the holdout. Then every suite runs against every copy, and gets scored.","Eighteen copies of a holdout table; three test suites aimed at them","CONSTRUCTED — planned",None),
 ("M4","methods","The data's free, the tools are free, and Claude Code runs on my Claude Pro plan with Opus 5.5, capped at three prompts so I can't keep tuning it. No other accounts or paid compute are needed.","Checklist: public data, DuckDB and dbt free, Claude Pro with Opus 5.5, max 3 prompts, no other accounts or paid compute",None,"FAULT-CATALOGUE.md section 3"),
 ("V1","evaluation","How will I know it worked? First, I'll check the tool itself: every faulted copy must have exactly fifty bad rows, and a test written for each fault must catch it. Then two numbers. Catch rate: how many of the eighteen faults a suite flags. And false alarms: how many of its tests fail on clean data.","First a check on the tool itself, then a balance: faults caught against false alarms",None,None),
 ("V2","evaluation","I set the line before building. Claude's tests pass if they catch at least fifteen of the eighteen, at least as many as mine, and no more than five percent of them fail on clean data. If they fall short, that isn't the project failing. That's the finding.","Three pass conditions under a line marked set before building",None,"FAULT-CATALOGUE.md section 3 (commit e5aac1c)"),
 ("V3","close","So that's Seeded Faults: tests for your data, tested. Next up: the fault-injection script.","The cracked badge beside the empty scoreboard; next: fault-injection script",None,None),
]
beats = []
for bid, act, n, vis, label, ev in B:
    b = {"beat_id": bid, "act": act, "narration_text": n, "estimated_duration_s": round(len(n.split()) / 2.4, 1),
         "new_visual_element": vis, "shot": {"type": "GRAPHIC", "source": "own", "motion": "drawon"}}
    if label: b["on_screen_label"] = label
    if ev: b["evidence"] = ev
    beats.append(b)
sheet = {"metadata": {"title": "Seeded Faults — Project Film", "slug": "seeded-faults-project", "author": "Atharva C",
    "drafted": "2026-11-22", "engine": "kokoro", "voice_kokoro": "am_michael", "aspect": "16:9", "clock": "narration",
    "structure": "Executive summary, Introduction (prior work), Methods, Evaluation",
    "purpose": "INFO 7375 project film. The project is not built; the fault catalogue is locked (commit e5aac1c).",
    "format_note": "show-tell: one drawn picture per beat, minimal on-screen text, narration carries the idea. Constructed pictures are labelled on screen."},
    "beats": beats}
out = Path(__file__).resolve().parent.parent / "beat_sheet.json"
out.write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n")
w = sum(len(b["narration_text"].split()) for b in beats)
print(len(beats), "beats,", w, "words, est", round(w / 2.4), "s")
