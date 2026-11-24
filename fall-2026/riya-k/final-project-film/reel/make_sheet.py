#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for riya-k-ground-truth-sql-v4 (INFO 7375 final project film, four-part cut).

v4 (2026-11-22) re-cuts the v3 pitch film into the four parts the final brief requires, in order:
executive summary (B01-B05), introduction (B06-B08), methods (B09-B15), evaluation (B16-B20).
The first beat of parts 1-4 opens on a "Part N" card. Script approved by Riya 2026-11-22 (SCRIPT-v4-four-parts.md).


v2 answers the instructor's feedback on v1 (2026-10-19): the problem was not shown clearly, the
animations were weak, and there were no examples. So every beat is an animated Manim scene built
around one real example from Chinook, and the narration is plain everyday language (SQL is
explained once). Narrated in the first person as Riya with Kokoro af_bella (American female,
synthetic). Captions are burned in after the master (see burn_captions.py).

Every number spoken comes from evidence/run_slice.py output or a read-only query on Chinook,
re-run 2026-10-19, or from evidence/score_claude_runs.py and evidence/vanna_check.py, run 2026-10-21
(see FACTCHECK.md). The wrong queries were drafted with Claude and checked by Riya to copy common
text-to-SQL mistakes, and the film says so (B03). The only model output shown is the 2026-10-21 Claude run (B10).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "riya-k-ground-truth-sql-v4"
TITLE = "Ground Truth SQL"
HANDLE = "Riya Kapadnis"
VOICE = "af_bella"
SPARSE = ("Builds in step with the narration: each scene adds its parts on the spoken word and is full by the "
          "end, so the 50% sample shows a partly built picture. Only underfill and clustered are waived; "
          "edge-bleed, empty-frame and contrast still apply.")


def beat(bid, cls, narration, motion, show, lead=0.0):
    b = {"beat_id": bid, "act": "pitch", "lane": "manim", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.7, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": motion, "show": show,
                  "manim": {"class": cls}, "motion_claim": motion},
         "motion_claim": motion}
    if lead:
        b["lead_silence_s"] = lead
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE}
    return b


ACT = {}
for _b in ("B01", "B02", "B03", "B04", "B05"): ACT[_b] = "1-executive-summary"
for _b in ("B06", "B07", "B08"): ACT[_b] = "2-introduction"
for _b in ("B09", "B10", "B11", "B12", "B13", "B14", "B15"): ACT[_b] = "3-methods"
for _b in ("B16", "B17", "B18", "B19", "B20"): ACT[_b] = "4-evaluation"

B = [
 # ───────────── Part 1 · Executive summary: what and why, no "how" ─────────────
 beat("B01", "B01_Title",
    "Ground Truth SQL. I'm Riya Kapadnis, and this is my final project film. "
    "The problem: AI can write database code that runs with no errors, but gives the wrong answer.",
    "Title card: the project name writes on, Riya Kapadnis and the course fade in under it, then the one-line "
    "problem appears with a terracotta underline.",
    [{"at": 0.0, "event": "title"}, {"at": 0.25, "event": "name + course"}, {"at": 0.6, "event": "the problem line"}],
    lead=0.8),
 beat("B02", "B02_Problem",
    "Picture an analyst asking an AI: what is our revenue by country? The AI writes SQL, the language for asking a "
    "database questions. It runs. No errors. It says the USA made four thousand six hundred sixty seven dollars. "
    "The real answer is five hundred twenty three.",
    "A 'Part 1 · Executive summary' card, then a chat box: the question types in; an SQL panel types itself out; a "
    "'ran · 0 errors' pill ticks; the result table shows USA 4,667.06; a terracotta cross lands and 523.06 drops in.",
    [{"at": 0.0, "event": "part card"}, {"at": 0.3, "event": "SQL types out"}, {"at": 0.5, "event": "0 errors"},
     {"at": 0.65, "event": "USA $4,667"}, {"at": 0.9, "event": "real answer $523"}]),
 beat("B03", "B03_Matters",
    "Why does this matter? People ask data questions in plain English, so most never see the SQL. The AI doesn't "
    "know your data. And wrong SQL doesn't crash. It just gives a number people trust, and that number ends up in "
    "reports and decisions.",
    "Three reasons build left to right: a person who only sees the answer (SQL greyed out behind it); the AI at a "
    "database with question marks over its tables; a confident number landing on a meeting screen.",
    [{"at": 0.2, "event": "can't see the SQL"}, {"at": 0.45, "event": "doesn't know your data"},
     {"at": 0.75, "event": "a number people trust"}]),
 beat("B04", "B04_WhatItIs",
    "So I'm building Ground Truth SQL: a test for AI data assistants. Give it your own data and questions, and it "
    "tells you which answers the AI got wrong, and why.",
    "Your data (a server) and your questions feed a 'Ground Truth SQL' box; a report card fills: two rows crossed "
    "with their reason underneath, one row ticked.",
    [{"at": 0.1, "event": "Ground Truth SQL"}, {"at": 0.4, "event": "your data + questions"},
     {"at": 0.7, "event": "which answers were wrong"}, {"at": 0.92, "event": "why"}]),
 beat("B05", "B05_WhereUsed",
    "Where will it be used? Anywhere people ask data questions in plain English: store sales, finance, hospitals, "
    "marketing, and AI data assistants. Analysts learn what to double check. Teams test a tool "
    "before buying. Engineers see what to fix.",
    "The report card sits in the middle; five places light up around it one by one (store, finance, hospital, "
    "marketing, AI assistant); then three people step in, each with a two-word takeaway.",
    [{"at": 0.12, "event": "store"}, {"at": 0.2, "event": "finance"}, {"at": 0.26, "event": "hospital"},
     {"at": 0.32, "event": "marketing"}, {"at": 0.4, "event": "AI assistant"}, {"at": 0.6, "event": "analysts"},
     {"at": 0.75, "event": "teams"}, {"at": 0.9, "event": "engineers"}]),

 # ───────────── Part 2 · Introduction: what others have done ─────────────
 beat("B06", "B06_Bird",
    "Others have tested AI on SQL. BIRD is a public benchmark: twelve thousand seven hundred fifty one questions "
    "over ninety five databases, scored by checking results. People score about ninety three percent, and the best "
    "AI still scores lower. But BIRD tests AI only on its own databases, not yours.",
    "A 'Part 2 · Introduction' card; BIRD's shelf of its own databases; three counts tick in (12,751 questions, 95 "
    "databases, checked by results); two bars grow (people 93%, best AI shorter); a 'your data' pill outside the "
    "shelf gets a cross.",
    [{"at": 0.0, "event": "part card"}, {"at": 0.2, "event": "BIRD shelf"}, {"at": 0.35, "event": "12,751 / 95"},
     {"at": 0.6, "event": "people 93%"}, {"at": 0.75, "event": "best AI lower"}, {"at": 0.9, "event": "not your data"}]),
 beat("B07", "B07_Vanna",
    "Tools like Vanna write SQL on your own data, and come with a built-in answer test. But that test looks for "
    "words, not right numbers. On my data, it passed the answer that was nine times too high.",
    "Riya's real Vanna 2.0.2 run (screenshot, evidence/vanna_check.py, 2026-10-21) on the left; on the right "
    "'works on your data' ticks and 'checks words, not numbers' gets a cross; a 'USA 4,667 · passed' pill lands.",
    [{"at": 0.1, "event": "Vanna run"}, {"at": 0.35, "event": "your data"}, {"at": 0.6, "event": "words, not numbers"},
     {"at": 0.85, "event": "passed 4,667"}]),
 beat("B08", "B08_Gap",
    "So there's a gap. Benchmarks check numbers, but not on your data. Tools work on your data, but don't check the "
    "numbers. Ground Truth SQL does both, so you find the wrong answers before anyone trusts them.",
    "A small grid fills row by row: columns 'checks the numbers' and 'on your data'; BIRD gets a tick and a cross, "
    "Vanna a cross and a tick, Ground Truth SQL two ticks and a terracotta outline.",
    [{"at": 0.1, "event": "grid"}, {"at": 0.25, "event": "benchmarks"}, {"at": 0.5, "event": "tools"},
     {"at": 0.75, "event": "Ground Truth SQL"}]),

 # ───────────── Part 3 · Methods: how I'll build it ─────────────
 beat("B09", "B09_Data",
    "The data: Chinook, a free sample music store database. Eleven tables, fifty nine customers, and four hundred "
    "twelve orders from two thousand nine to twenty thirteen.",
    "A 'Part 3 · Methods' card; the Chinook database (server) with its label; three counts tick in (11 tables, 59 "
    "customers, 412 orders); a timeline 2009 to 2013 draws under them.",
    [{"at": 0.0, "event": "part card"}, {"at": 0.3, "event": "Chinook"}, {"at": 0.55, "event": "11 / 59 / 412"},
     {"at": 0.85, "event": "2009 to 2013"}]),
 beat("B10", "B10_AnswerKey",
    "Step one: write about fifty questions, each with a checked answer. I check every answer a second way, in plain "
    "Python, straight from the raw tables.",
    "A stack of question cards ('about 50'); one card opens: question, checked SQL, answer 523.06; a second path "
    "(plain Python from the raw tables) arrives at the same 523.06; an '=' and a tick: 'today 8 of 8 agree'.",
    [{"at": 0.1, "event": "stack of ~50"}, {"at": 0.35, "event": "checked answer"}, {"at": 0.6, "event": "second way"},
     {"at": 0.9, "event": "agree"}]),
 beat("B11", "B11_ClaudeAnswers",
    "Step two: Claude answers each question three times. It sees only the table layout and the question, and may "
    "run one read-only query. It can never change the data.",
    "Two input cards (table layout, the question) feed Claude's workstation; three run chips appear; an arrow to the "
    "database with a 'read-only · 1 query' pill; 'the data never changes' lands below.",
    [{"at": 0.1, "event": "Claude"}, {"at": 0.25, "event": "3 runs"}, {"at": 0.45, "event": "inputs"},
     {"at": 0.75, "event": "read-only"}, {"at": 0.9, "event": "never changes"}]),
 beat("B12", "B12_Judge",
    "Step three: judge by results, not wording, since one answer can be written many ways. These two queries look "
    "different, but both give five hundred twenty three.",
    "Two different SQL panels side by side; both run into the same result 523.06; an '=' appears and a line reads "
    "'compare results, not wording'.",
    [{"at": 0.2, "event": "two SQLs"}, {"at": 0.75, "event": "both 523.06"}, {"at": 0.9, "event": "results, not wording"}]),
 beat("B13", "B13_Causes",
    "Step four: a report card that sorts every miss by its cause: counting an order once per song, mixing up "
    "milliseconds and seconds, counting purchases instead of people, or linking the wrong columns.",
    "Four cause cards flip in one by one, each with the wrong number (crossed) and the right one: revenue 4,667 vs "
    "523, long songs 3,503 vs 1,069, rock buyers 835 vs 59, busiest rep (empty) vs Jane Peacock, 21.",
    [{"at": 0.3, "event": "once per song"}, {"at": 0.5, "event": "ms vs s"}, {"at": 0.7, "event": "purchases vs people"},
     {"at": 0.88, "event": "wrong columns"}]),
 beat("B14", "B14_Needs",
    "What I need: a laptop, Python, and the free database. No cloud servers, and no extra token credits: Claude "
    "answers through my Claude Code plan, the same way it did in my first runs.",
    "Two columns fill: 'what I have' (laptop, Python, free database, Claude via my Claude Code plan) with ticks, and "
    "'what I don't need' (cloud servers, extra token credits) with crosses.",
    [{"at": 0.1, "event": "laptop"}, {"at": 0.2, "event": "Python"}, {"at": 0.3, "event": "database"},
     {"at": 0.45, "event": "no cloud"}, {"at": 0.55, "event": "no credits"}, {"at": 0.7, "event": "Claude Code plan"}]),
 beat("B15", "B15_Scope",
    "The finished project will have one sample database, about fifty test questions, and Claude as the AI it "
    "tests. It won't be a chat app, and it never changes the data.",
    "Two columns fill: 'the finished project will have' (1 sample database · Chinook, ~50 test questions, Claude as "
    "the AI being tested) and 'it will not' (be a chat app, change any data · read-only).",
    [{"at": 0.15, "event": "will have"}, {"at": 0.65, "event": "will not"}]),

 # ───────────── Part 4 · Evaluation: how I'll know it worked ─────────────
 beat("B16", "B16_CheckerTest",
    "First, does the checker judge correctly? On nine test queries that I labeled by hand, comparing wording judged "
    "six right. Comparing results: all nine.",
    "A 'Part 4 · Evaluation' card; the question as a heading; nine labeled test queries (3 correct rewrites, 6 with a "
    "mistake); two bars grow: compare wording 6 of 9, compare results 9 of 9.",
    [{"at": 0.0, "event": "part card"}, {"at": 0.4, "event": "9 test queries"}, {"at": 0.7, "event": "6/9"},
     {"at": 0.9, "event": "9/9"}]),
 beat("B17", "B17_Runs",
    "Then I had Claude answer my eight questions, three times. The checker passed twenty two of twenty four. The two "
    "fails were a tie my question never settled. Claude wasn't wrong; my question was.",
    "A terminal window types the real score_claude_runs.py result (three blind Claude runs, 2026-10-21), shortened; "
    "the 22 / 24 line is underlined; the two Q02 fails light up; a card shows France 5 and Brazil 5: a tie.",
    [{"at": 0.1, "event": "command"}, {"at": 0.45, "event": "22 / 24"}, {"at": 0.65, "event": "two fails"},
     {"at": 0.85, "event": "a tie"}]),
 beat("B18", "B18_CaughtMe",
    "It also caught a mistake in my answer key. One question asked about twenty twenty three, but the data ends in twenty "
    "thirteen. The right answer was empty, so broken SQL returning nothing looked correct. Now the tool rejects empty "
    "answers.",
    "A timeline 2009-2013; a '2023' marker slides past the end; two empty result boxes show '=' ; a terracotta cross "
    "lands on the '='; a new rule card stamps on: 'empty right answer -> rejected'.",
    [{"at": 0.2, "event": "timeline"}, {"at": 0.45, "event": "empty = empty"}, {"at": 0.85, "event": "rule"}]),
 beat("B19", "B19_PassBar",
    "It worked if the checker agrees with my hand labels every time, every answer key passes the second check, and "
    "every miss on the report card has a named cause. It didn't work if Claude gets everything right, because that "
    "means my questions are too easy. Today it nearly does, so the next fifty questions must be harder.",
    "'It worked if' fills with three ticked lines; 'it didn't work if' adds one crossed line; a bar shows today's "
    "22 of 24 nearly full, and a note 'next: 50 harder questions'.",
    [{"at": 0.05, "event": "worked if"}, {"at": 0.2, "event": "hand labels"}, {"at": 0.33, "event": "second check"},
     {"at": 0.45, "event": "named cause"}, {"at": 0.62, "event": "didn't work if"}, {"at": 0.85, "event": "today"}]),
 beat("B20", "B20_Conclusion",
    "In conclusion: AI can give wrong answers that look right. Ground Truth SQL tests the AI on your own data and "
    "shows what's wrong, and why. Today the checker works. Next: fifty harder questions. "
    "So the takeaway is this: running SQL is easy. Being right is the test.",
    "An 'in conclusion' tag; four recap rows build (problem / solution / today / next); then they clear, a 'the takeaway' "
    "label appears and the closing two lines write on under it.",
    [{"at": 0.1, "event": "problem"}, {"at": 0.3, "event": "solution"}, {"at": 0.5, "event": "today"},
     {"at": 0.65, "event": "next"}, {"at": 0.8, "event": "closing line"}]),
]
for _b in B:
    _b["act"] = ACT[_b["beat_id"]]

# Keep measured audio durations across regenerations of the sheet.
old = {}
if (HERE / "beat_sheet.json").exists():
    for b in json.loads((HERE / "beat_sheet.json").read_text())["beats"]:
        old[b["beat_id"]] = b
for b in B:
    o = old.get(b["beat_id"])
    if o and o.get("narration_text") == b["narration_text"]:
        for k in ("actual_duration_s", "audio_file", "render_duration_s"):
            if k in o:
                b[k] = o[k]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "riya-kapadnis", "channel_title": HANDLE, "persona": "Riya Kapadnis (synthetic voice, Kokoro af_bella)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "burned-in after master (burn_captions.py), from narration_text with word timings",
    "bookend_exempt": ["cold-open", "bidea", "bdefs", "bvdt", "bhtf", "bout"],
    "bookend_exempt_reason": ("Course pitch redo, not a channel explainer. The instructor's feedback asked for the problem to be "
                              "shown first, so B01 is a narrated title card (project title + Riya's name + the problem) and "
                              "B02 shows the problem with a real example, replacing the hesitant writer and the terms card "
                              "(SQL is defined in the narration where it is first used). No Your Turn (a pitch has no viewer "
                              "task). No ClaudeTitleOutro: it hardcodes the instructor's handle, which the assignment forbids; "
                              "the film ends on its spoken conclusion B20."),
    "audience": "INFO 7375 instructor and TAs; a hiring manager screening AI Engineer candidates; anyone who uses AI to ask a database questions",
    "source_doc": "PROJECT-BRIEF.md; evidence/run_slice.py output and read-only Chinook queries (re-run 2026-10-19); "
                  "bird-bench.github.io (read 2026-10-09; human 92.96 and leaderboard re-read 2026-11-22); Vanna 2.0.2 run on Chinook (evidence/vanna_check.py, 2026-10-21); "
                  "three blind Claude runs (evidence/claude_runs/2026-10-21)",
    "tags": ["text-to-SQL", "evaluation", "Claude", "INFO 7375"]},
    "beats": B}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(B), "beats; est", round(sum(b["estimated_duration_s"] for b in B)), "s;",
      sum(len(b["narration_text"].split()) for b in B), "words")
