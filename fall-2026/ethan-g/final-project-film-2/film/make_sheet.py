#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the DataSentry project film (Ethan Gomes, 2026-11-23).

The assignment asks for four parts, in this order: 1 executive summary (what and why, no "how"),
2 introduction (what others have done, and what they got), 3 methods (the plan, the data, the steps,
the resources), 4 evaluation (what is measured, and what result means it worked). Length: 4 minutes.

show-tell format: one drawn picture per beat, a label or two, the narration explains. Every beat carries
a small tag naming its part. Narrated as Ethan (first person, a stock Kokoro voice); no instructor name,
persona, or credit line, so no house bookends (the film closes on a drawn beat, BEND).

Honesty: past tense only for what ran (first-run/results/2026-10-25/). The loop in Claude Code and the
public repo are "still to build". Prior-work numbers come from the papers listed in ../SOURCES.md.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "datasentry-project-film"
TITLE = "DataSentry: Project Film"
VOICE = "am_michael"   # the same stock Kokoro voice as the pitch (not the toolkit's Liam persona, am_onyx)
SPARSE = ("show-tell: one drawn object on a cream stage, a label or two; the voice explains. "
          "Only underfill and clustered are waived; edge-bleed, empty-frame and contrast still apply.")


def beat(bid, act, narration, cls, intent, show, sparse=True, **extra):
    b = {"beat_id": bid, "act": act, "lane": "manim", "proof_gate": "SHOW", "narration_text": narration,
         "estimated_duration_s": round(len(narration.split()) / 2.6, 1), "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": intent, "show": show,
                  "manim": {"class": cls}, "motion_claim": intent}}
    if sparse:
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE}
    b.update(extra)
    return b


BEATS = [
 beat("BIDEA", "title",
    "This is a project film by Ethan Gomes, about Data Sentry, in four parts.",
    "BIDEA_Title", "Title card: 'Project Film created by Ethan Gomes'; 'DataSentry' large; a rule with one terracotta dot; the four parts listed below it, numbered 1 to 4.",
    [{"at": 0.05, "event": "DataSentry"}, {"at": 0.3, "event": "rule + dot"}, {"at": 0.5, "event": "the four parts"}],
    lead_silence_s=0.8),

 # ── 1 · Executive summary: what and why (no "how") ──
 beat("BSIMPLE", "1 executive summary",
    "Part one, the executive summary. Companies set rules to catch bad data, like a taxi fare below zero. Data "
    "Sentry tests those rules like a spell-checker: hide mistakes on purpose, count which get caught, and which slip through.",
    "BSIMPLE_Spellcheck", "A page of writing; terracotta marks hidden in it on purpose; a magnifier passes over and ticks the ones it finds; one mark is left with no tick ('slipped through').",
    [{"at": 0.3, "event": "the page"}, {"at": 0.6, "event": "mistakes hidden"}, {"at": 0.85, "event": "caught / slipped through"}]),
 beat("B00", "1 executive summary",
    "Data Sentry is an AI agent that writes data checks for a table, tests them against bad rows I planted, and "
    "revises them, until a person approves the final set.",
    "B00_Scanner", "A checkpoint scanner arch with 'DataSentry · an AI agent' beside it; a table (parcel) slides under the arch; a terracotta dot (a planted bad row) lights on it; a tick and 'a person approves'.",
    [{"at": 0.1, "event": "scanner lands"}, {"at": 0.35, "event": "label"}, {"at": 0.6, "event": "planted bad row"}, {"at": 0.85, "event": "a person approves"}]),
 beat("B01", "1 executive summary",
    "Why it matters: when checks let bad rows through, wrong numbers reach dashboards and decisions. And as AI writes "
    "more checks, someone has to grade them.",
    "B01_Why", "A table card with terracotta bad rows; an arrow to a bar-chart dashboard card with a terracotta dot on one bar ('wrong numbers'); then a tick and 'graded'.",
    [{"at": 0.2, "event": "bad rows"}, {"at": 0.45, "event": "wrong dashboard"}, {"at": 0.85, "event": "graded"}]),

 # ── 2 · Introduction: what others have done ──
 beat("B03", "2 what others have done",
    "Part two, what others have done. Pandera, D B T and Great Expectations run rules on tables; Amazon's Dee-queue "
    "suggests them. I ran one rule, fare can't be negative, in all three: all caught the negative fares, none caught "
    "the trips that end before they start.",
    "B03_Gap", 'Recorded output (typeset) of the 2026-10-25 run: the three tools side by side (all PASS clean, FAIL 25 broken), then the answer key: negative fares 25/25 CAUGHT, drop-off before pick-up 0/25 MISSED; tagged "recorded output · <date>".',
    [{"at": 0.45, "event": "three tools"}, {"at": 0.7, "event": "caught"}, {"at": 0.85, "event": "missed"}]),
 beat("B04", "2 what others have done",
    "AI already writes tests: Great Expectations' paid Expect A I suggests data checks, and at Meta, AI-written tests "
    "built seventy-five percent of the time and passed fifty-seven; a later tool, steered by planted bugs, had "
    "seventy-three percent accepted.",
    "B04_PriorAI", "Three cards land in a row, each with one big published number: 'GX Cloud ExpectAI / suggests checks'; 'Meta TestGen-LLM 2024 / 75% built · 57% passed'; 'Meta ACH 2025 / 73% accepted'.",
    [{"at": 0.2, "event": "ExpectAI"}, {"at": 0.45, "event": "Meta 2024"}, {"at": 0.8, "event": "Meta 2025"}]),
 beat("B05", "2 what others have done",
    "Mutation testing has graded code tests with planted bugs since nineteen seventy-eight. But in what I found, "
    "nobody does that for AI-written data checks on real tables. That's the gap Data Sentry fills.",
    "B05_Grid", 'A comparison grid (constructed from the sources, labelled so): rows mutation testing (1978), Meta ACH, dbt, GX + ExpectAI, DataSentry; columns "data tables", "planted defects", "AI-written checks"; only DataSentry is yes in all three.',
    [{"at": 0.2, "event": "mutation testing row"}, {"at": 0.55, "event": "data tools"}, {"at": 0.85, "event": "DataSentry row"}]),

 # ── 3 · Methods: how ──
 beat("B06", "3 methods",
    "Part three, methods. The data is public: New York City yellow taxi trips from January twenty twenty-five, ten "
    "thousand rows.",
    "B06_Table", "A flat table card; grey rows fill in; labels 'NYC taxi · Jan 2025' and the real sample size from the first run.",
    [{"at": 0.3, "event": "table"}, {"at": 0.6, "event": "NYC taxi"}, {"at": 0.85, "event": "rows"}]),
 beat("B07", "3 methods",
    "Step one: a planter script breaks copies of the table five different ways, and locks the answer key away.",
    "B07_StepOne", "Titled 'Step 1': a table card, an arrow to a dark planter block, an arrow to a broken copy with terracotta marks ('5 defect types'), and a locked answer key; labels 'planter', 'answer key'.",
    [{"at": 0.25, "event": "planter"}, {"at": 0.55, "event": "broken copy"}, {"at": 0.8, "event": "answer key"}]),
 beat("B08", "3 methods",
    "Step two: Claude sees only the column names and types, and writes pandera checks under a contract. A scorer "
    "grades them on the clean copy and every broken copy.",
    "B08_StepTwo", "Titled 'Step 2': a workstation (Claude) writes check pages; the checks run over a clean and a broken copy; the scorer binder lands with a tick and a dot; labels 'Claude', 'pandera checks', 'scorer'.",
    [{"at": 0.2, "event": "Claude"}, {"at": 0.45, "event": "checks"}, {"at": 0.8, "event": "scorer"}]),
 beat("B09", "3 methods",
    "Step three: the loop. Only the clean copy's results go back, and Claude revises, up to three rounds, all logged. "
    "It's built, and it ran.",
    "B09_StepThree", "Titled 'Step 3 · built and run': three stations on a loop (write, score, 'clean-copy results only') joined by arrows; 'up to 3 rounds, all logged'; a tick and 'ran 2026-11-23'.",
    [{"at": 0.15, "event": "write, score"}, {"at": 0.4, "event": "feedback"}, {"at": 0.65, "event": "loop closes"}, {"at": 0.85, "event": "ran"}]),
 beat("B09A", "3 methods",
    "Its tools are fenced: no built-in tools, an empty folder, no answer keys or held-out data, and every checks file "
    "must pass a code policy before it runs. Next: a tool menu, with every call checked.",
    "B09A_Tools", "Claude's workstation inside a dashed fence ('no tools · empty folder'); 'no answer keys · no held-out data' under it; a permission gate labelled 'code policy'; a menu card 'next: tool menu' with four tool names, each checked by code.",
    [{"at": 0.15, "event": "fence"}, {"at": 0.35, "event": "no answer keys"}, {"at": 0.55, "event": "code policy"}, {"at": 0.8, "event": "tool menu"}]),
 beat("B09B", "3 methods",
    "And a person stays in charge. Before any checks are kept, I'll see the scorecard, the code and its fingerprint, "
    "and approve, refuse, or defer. Nothing is kept without that.",
    "B09B_Gate", "Planned (labelled 'planned'): a review card with three rows ('scorecard', 'code', 'sha256 fingerprint'); three buttons land: 'approve' (tick), 'refuse' (dot), 'defer'; 'nothing kept without approval'.",
    [{"at": 0.25, "event": "review card"}, {"at": 0.6, "event": "approve / refuse / defer"}, {"at": 0.85, "event": "nothing kept"}]),
 beat("B10", "3 methods",
    "Do I have what I need? Yes: public data, my laptop, and my existing Claude subscription. No API key, no credits.",
    "B10_Resources", "A checklist card; four ticks land one by one beside 'data: public (NYC TLC)', 'compute: my laptop', 'Claude: my existing subscription', 'API key, credits: none'.",
    [{"at": 0.3, "event": "data"}, {"at": 0.45, "event": "compute"}, {"at": 0.65, "event": "Claude"}, {"at": 0.85, "event": "no key"}]),

 # ── 4 · Evaluation: how I'll know it worked ──
 beat("B11", "4 evaluation",
    "Part four, evaluation. I measure defect types caught, false alarms on good trips, and crashing checks, on "
    "held-out data never used for tuning: a second planting and a second clean copy.",
    "B11_Measures", "Four record sheets land in a row, numbered 1 to 4, each labelled with one measure: 'defects caught', 'false alarms', 'crashes', 'held-out data'.",
    [{"at": 0.35, "event": "1"}, {"at": 0.5, "event": "2"}, {"at": 0.62, "event": "3"}, {"at": 0.8, "event": "4"}]),
 beat("B12", "4 evaluation",
    "It passes only with all five defect types caught, zero good trips flagged, and no crashing checks, on both "
    "plantings. Anything less fails.",
    "B12_PassLine", "The pass line as a card titled 'pass line': three conditions, each with a tick ('5 of 5 defect types caught', '0 good trips flagged', '0 crashing checks'), then 'on both plantings · anything less fails'.",
    [{"at": 0.3, "event": "five of five"}, {"at": 0.5, "event": "zero flagged"}, {"at": 0.7, "event": "no crashes"}, {"at": 0.85, "event": "both"}]),
 beat("B13", "4 evaluation",
    "By hand, nothing passed. In the loop, round one flagged ninety-four good trips, round two just one, and round "
    "three none, with all five caught: pass line met. On the second clean copy, still zero.",
    "B13_SoFar", 'Recorded output (typeset) of the live loop run (./run_loop.sh, 2026-11-23): round 1, 94 good rows flagged, 5 of 5 (dot); round 2, 1 flagged, 5 of 5 (dot); round 3, PASS, 5 of 5 on both plantings (tick); second clean copy, 0 flagged (tick); tagged "Claude Opus 5.5 · recorded output · <date>".',
    [{"at": 0.3, "event": "round 1"}, {"at": 0.45, "event": "round 2"}, {"at": 0.6, "event": "round 3"}, {"at": 0.85, "event": "second clean copy"}]),
 beat("B13A", "4 evaluation",
    "I'll also break it on purpose, at least five ways, like a forbidden import or a try at the answer key. And one "
    "controlled failure: I'll trigger the rule-dropping Claude did by hand; the held-out scorer must catch it, and "
    "I'll refuse it at the gate.",
    "B13A_Failures", "Planned (labelled 'planned'): five small labels land, each with a terracotta dot ('forbidden import', 'crashing check', 'hard-coded values', 'empty reply', 'answer-key read'); then a row 'controlled failure: predict → trigger → caught by held-out → refused at the gate'.",
    [{"at": 0.3, "event": "five failure cases"}, {"at": 0.75, "event": "controlled failure"}]),
 beat("B14", "4 evaluation",
    "So far, it worked on this table and five defect types. Not shown yet: other tables, or real defects I didn't "
    "plant.",
    "B14_Outcome", "Two columns of text: 'shown' (tick): 'this table, 5 defect types, passed in 3 rounds'; 'not shown yet' (dot): 'other tables', 'real defects I didn't plant'.",
    [{"at": 0.3, "event": "shown"}, {"at": 0.7, "event": "not shown yet"}]),
 beat("BEND", "close",
    "That's Data Sentry. I'm Ethan Gomes. Thanks for watching.",
    "BEND_Close", "The scanner returns; the title and Ethan's name land beside it; then a silent end screen: 'Thank you', 'DataSentry', 'Final Project Film', 'Ethan Gomes'.",
    [{"at": 0.2, "event": "scanner"}, {"at": 0.5, "event": "title and name"}], tail_silence_s=4.0),
]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT · PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "ethan-gomes", "channel_title": "@EthanGomes14", "persona": "Ethan Gomes (narrated in first person; synthetic Kokoro voice)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Course assignment (INFO 7375 project film): narrate as yourself, no instructor name, "
                              "persona, or credit line. No composer cold open, no verdict card, no Your Turn. The house outro "
                              "card (ClaudeTitleOutro) hard-codes the instructor's handle, so the film closes on a drawn beat (BEND) "
                              "instead; bookend_check.py is expected to report the missing ClaudeTitleOutro."),
    "audience": "INFO 7375 instructor and TAs; a data engineering hiring manager",
    "source_doc": "../APPENDIX.md and ../SOURCES.md (2026-11-23); recorded runs in ../first-run/results/2026-10-25/ and ../first-run/loop-runs/2026-11-23_182418/",
    "playlist": "", "chapter_number": 0,
    "tags": ["data engineering", "data quality", "pandera", "Claude", "evaluation", "project film"]},
    "beats": BEATS}

# carry measured audio forward when the narration is unchanged (show-tell gate trap 4)
old = {}
p = HERE / "beat_sheet.json"
if p.exists():
    for ob in json.load(open(p))["beats"]:
        old[ob["beat_id"]] = ob
for b in BEATS:
    ob = old.get(b["beat_id"])
    if ob and ob.get("narration_text") == b["narration_text"]:
        for k in ("actual_duration_s", "audio_file"):
            if k in ob:
                b[k] = ob[k]

p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(len(BEATS), "beats;", words, "words; est", round(sum(b.get("actual_duration_s") or b["estimated_duration_s"] for b in BEATS)), "s")
