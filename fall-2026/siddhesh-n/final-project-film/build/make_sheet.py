#!/usr/bin/env python3
"""make_sheet.py — writes beat_sheet.json for checkedsql-pitch.

Final Project Pitch Film, INFO 7375, Fall 2026 — Siddhesh Nikam.
Built with the brutalist.art show-tell skill, adapted for a student pitch:
  * narrated in my own name (no instructor name, persona, or credit line);
  * the outro is my own Manim title card, not ClaudeTitleOutro (that component
    hard-codes the instructor's handle on screen);
  * no Your Turn beat (bookend_exempt) — this is a pitch, not a tutorial.
Run: python3 make_sheet.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "checkedsql-pitch"
TITLE = "CheckedSQL: A Pitch"
HANDLE = "@nikam0420"
VOICE = "am_onyx"   # free local Kokoro voice; disclosed as synthetic in SOURCES.md

SPARSE = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, the voice "
          "carrying the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and "
          "contrast still apply.")


def beat(bid, narration, cls, image, show):
    return {"beat_id": bid, "act": "pitch", "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration,
            "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
            "voice": VOICE, "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image},
            "qc": {"sparse_by_design": True, "sparse_reason": SPARSE}}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration,
         "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


OPEN = [
    remotion(
        "BIDEA", "the question",
        "Namaste. I'm Siddhesh Nikam, and this is the pitch for my final project. Lots of tools will answer "
        "a data question. My question is different. Can I prove the answer is right?",
        "BrutalistHesitantWriter",
        {"text": "Can Claude answer\nmy campaign questions?", "triggerWords": "answer",
         "replacementWords": "prove its answers to",
         "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2,
         "jitter": 20, "seed": SLUG, "banner": ""},
        [{"at": 0.0, "event": "types the naive question"},
         {"at": 0.6, "event": "'answer' is corrected to 'prove its answers to'"}],
        lead_silence_s=0.8,
        motion_claim="The writer types 'can Claude answer my campaign questions' and corrects it to proving the answers.",
        qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
    remotion(
        "BDEFS", "terms",
        "Three terms. ROAS, return on ad spend: revenue divided by what the ads cost. A prompt contract: the "
        "fixed rules I give Claude about what it may write, and in what form. And a test set: questions whose "
        "right answers I work out by hand, before Claude sees them.",
        "ClaudeDefinitions",
        {"title": "Terms In This Film",
         "terms": [{"term": "ROAS", "meaning": "Return On Ad Spend: sales divided by the ad budget"},
                   {"term": "prompt contract", "meaning": "fixed rules that limit what Claude will write"},
                   {"term": "test set", "meaning": "questions I solve by hand first: the key"}],
         "folderLabel": HANDLE},
        [{"at": 0.12, "event": "'ROAS' lands"}, {"at": 0.45, "event": "'prompt contract' lands"},
         {"at": 0.75, "event": "'test set' lands"}], gate="CARD",
        qc={"sparse_by_design": True, "sparse_reason": "TERMS card: three prerequisites, one line each."}),
]

B = [
    beat("B00",
         "Here is the project in one sentence. CheckedSQL will let a marketing analyst ask a question in plain "
         "English, have Claude write the S Q L, run it on a campaign database, and show the answer with the "
         "query and a check.",
         "B00_OneSentence",
         "A question page slides into a dark database stack; its lights come on; a query page comes out the other side and an ink check lands beside it.",
         [{"at": 0.15, "event": "question page slides in"}, {"at": 0.4, "event": "database lights"},
          {"at": 0.7, "event": "query page out, check"}]),
    beat("B01",
         "When it's done, it will be a GitHub repository with four things. A synthetic campaign dataset. The "
         "question tool, written in Python. A test set of about thirty questions. And an evaluation log that "
         "records every pass and every miss.",
         "B01_Repo",
         "An open kraft box (the repo) sits on stage; a dark data block, a tool page, a stack of test pages and a log page drop into it one by one.",
         [{"at": 0.1, "event": "open box"}, {"at": 0.3, "event": "dataset block"},
          {"at": 0.5, "event": "tool page"}, {"at": 0.65, "event": "test stack"}, {"at": 0.85, "event": "log page"}]),
    beat("B02",
         "I looked at two real alternatives. The first is one I built: a Tableau dashboard for my marketing "
         "campaign project. It answers the questions I planned in advance. A new question means building a "
         "new view.",
         "B02_Dashboard",
         "A dashboard panel with grey bars grows; a new question page slides toward it and bounces back.",
         [{"at": 0.25, "event": "dashboard bars grow"}, {"at": 0.75, "event": "new question bounces off"}]),
    beat("B03",
         "The second is pasting a question into a general chat assistant. It writes a query, and some can run "
         "code on an uploaded file, but there's no fixed test set, so no record of how often it's right on my "
         "questions. CheckedSQL's difference: every answer is run, shown with its query, and scored against "
         "answers I checked by hand.",
         "B03_Scored",
         "A chat window passes a query page out; then the page rides through a gate made of a stack of test pages, and a check lands.",
         [{"at": 0.2, "event": "chat window, query out"}, {"at": 0.7, "event": "page through the test gate"},
          {"at": 0.85, "event": "check"}]),
    beat("B04",
         "The target role is data analyst, and the first reader is a hiring manager. In the first sixty seconds, "
         "they'll open the README, see the score table from the test set, and run one command that prints the "
         "query, the answer, and whether it matched.",
         "B04_SixtySeconds",
         "A README window opens with a grey score table; a dark terminal strip slides under it and a check appears; a large '60 s' sits beside it.",
         [{"at": 0.2, "event": "60 s"}, {"at": 0.45, "event": "README window"},
          {"at": 0.75, "event": "terminal strip, check"}]),
    beat("B05",
         "What will it prove? That I write S Q L and define marketing metrics correctly, which I already do. And "
         "that I can use what this course teaches: a prompt contract, verification against known answers, and a "
         "repeatable evaluation. The evidence: the test set, the log, and a write-up of every failure.",
         "B05_Proves",
         "Three pages stand in a row: contract, verification, evaluation; a terracotta dot lands on each as it is named, then the log page slides under them.",
         [{"at": 0.4, "event": "contract"}, {"at": 0.55, "event": "verification"},
          {"at": 0.7, "event": "evaluation"}, {"at": 0.85, "event": "log page"}]),
    beat("B06",
         "What's out. It will not change the database. It will only run read-only queries, on this one campaign "
         "schema. No dashboards, and no real company data.",
         "B06_ReadOnly",
         "The dark database stack; an arrow out of it gets a check (read); an arrow into it is crossed out (write).",
         [{"at": 0.25, "event": "read arrow + check"}, {"at": 0.6, "event": "write arrow crossed"}]),
    beat("B07",
         "What comes first: the test set and the checker, before any Claude call. I'll write ten questions, work "
         "out their answers by hand, and run my own queries through the checker as a baseline. You'll know it ran "
         "when one command prints a score table. Then Claude gets the same ten.",
         "B07_Baseline",
         "Ten small question pages in a row pass through a grey gate one after another; ink checks appear above them.",
         [{"at": 0.2, "event": "ten pages"}, {"at": 0.6, "event": "through the gate"}, {"at": 0.85, "event": "checks"}]),
    beat("B08",
         "What could sink it: an answer that looks right but isn't. ROAS is a ratio. Average it row by row, and "
         "you get a different number than total revenue over total spend, and both look plausible. My fix: put "
         "the metric definitions in the prompt contract, and add ratio questions to the test set, so this mistake "
         "gets caught and logged.",
         "B08_Ratio",
         "Two grey bars of different heights labelled 'row average' and 'total ÷ total'; a check lands on the total bar and a test page slides in.",
         [{"at": 0.3, "event": "two bars grow"}, {"at": 0.7, "event": "check on total"}, {"at": 0.85, "event": "test page"}]),
    beat("B09",
         "Why this project? It's a mix. S Q L, PostgreSQL and pandas, I already have. My marketing campaign "
         "analytics repository on GitHub computes click-through rate and return on ad spend with them. New to me "
         "are calling Claude from Python, writing prompt contracts, and building an evaluation harness. That's the "
         "part I'm here to learn.",
         "B09_HaveNew",
         "Left: a closed taped box (have). Right: an open box that pages drop into (new).",
         [{"at": 0.2, "event": "have box"}, {"at": 0.6, "event": "new box fills"}]),
    beat("B10",
         "What exists today: my two earlier GitHub repositories, and this pitch. Nothing of CheckedSQL is built "
         "yet. The dataset, the tool, the test set and the log will exist. What I don't know yet is whether "
         "thirty questions is enough. I'll find out by watching whether new questions keep finding new kinds of "
         "failure.",
         "B10_TodayWill",
         "Left: two solid boxes (today). Right: four ghost-outlined boxes (will), drawn one by one.",
         [{"at": 0.15, "event": "today boxes"}, {"at": 0.45, "event": "will boxes draw"}]),
]

BOUT = {"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW",
        "narration_text": f"{TITLE}. By Siddhesh Nikam.",
        "estimated_duration_s": 4.0, "voice": VOICE, "engine": "kokoro",
        "shot": {"type": "GRAPHIC", "source": "own",
                 "visual_intent": "My own title card: the film title, my name and GitHub handle, and the sealed repo box.",
                 "show": [{"at": 0.0, "event": "title, name, handle"}],
                 "manim": {"class": "BOUT_Title"},
                 # props are read by bookend_check.py (title + handle); no Remotion pattern, so nothing renders from them
                 "remotion": {"props": {"title": TITLE, "slug": SLUG, "handle": HANDLE, "subline": ""}}},
        "kind": "outro_voice", "tail_silence_s": 1.0,
        "qc": {"sparse_by_design": True, "sparse_reason": "Outro title card: title, name and one object."}}

beats = OPEN + B + [BOUT]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT PITCH", "skill": "show-tell",
    "style_preset": "show-tell", "channel": "student", "channel_title": HANDLE,
    "persona": "Siddhesh Nikam (narrating as himself, synthetic Kokoro voice)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "clock": "narration", "palette": "claude",
    "register": "Plain", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none", "greeting_language": "Hindi (Namaste)",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Student pitch film on the show-tell skill: opens on the hesitant writer and terms card; "
                              "no verdict card; no Your Turn (a pitch, not a tutorial). The outro is the student's "
                              "own Manim title card because ClaudeTitleOutro hard-codes the instructor's handle, "
                              "which the assignment forbids."),
    "audience": "INFO 7375 instructor and TAs; a data-analyst hiring manager",
    "source_doc": "PROJECT-BRIEF.md (Siddhesh Nikam, 2026-10-14); public repos github.com/nikam0420",
    "tags": ["data analyst", "SQL", "Claude", "evaluation", "prompt contract", "INFO 7375"]},
    "beats": beats}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in beats)
print(len(beats), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in beats)), "s")
