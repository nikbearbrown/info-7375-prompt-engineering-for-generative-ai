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

# ── facts from the user's own test (fill from the real screenshot; never invent) ──
CHAT_TOOL = "ChatGPT"            # which assistant was used
CHAT_DATE = "October twenty-fourth"
CHAT_ANSWER = "Search"          # the channel it named, exactly as it said it
CHAT_RIGHT = True                # True / False once known

if CHAT_RIGHT is True:
    chat_line = (f"It answered {CHAT_ANSWER}, which is right. But there is no fixed test set, so no record of "
                 "how often it is right on my questions, or which ones it gets wrong.")
elif CHAT_RIGHT is False:
    chat_line = (f"It answered {CHAT_ANSWER}. The right answer is Search. It looked plausible, and nothing "
                 "told me it was wrong: there was no test set and no score.")
else:
    raise SystemExit("set CHAT_ANSWER / CHAT_RIGHT from the real screenshot first")

B = [
    beat("B00",
         "One sentence. CheckedSQL will let a marketing analyst ask a campaign question in plain English, have "
         "Claude write the S Q L, run it on the data, and show the answer beside the query, scored against an "
         "answer key.",
         "B00_OneSentence",
         "The real test question 'Which channel had the highest ROAS?' slides into a dark Claude block (planned), a SQL page comes out, runs on the campaigns table, and the answer 'Search' lands with a check.",
         [{"at": 0.15, "event": "question card"}, {"at": 0.35, "event": "Claude block"},
          {"at": 0.55, "event": "SQL page into the data"}, {"at": 0.8, "event": "answer Search + check"}]),
    beat("B01",
         "When it's done, it will be a GitHub repository, and part of it already runs. On October "
         "twenty-fourth, with Claude's help, I built the synthetic dataset, ten test questions with an answer key, and the checker. "
         "Still to come: the prompt contract, the Claude step, and the evaluation log.",
         "B01_Repo",
         "An open repo box. Three solid parts drop in, labelled with their real file names. Three ghost outlines for the parts still to build.",
         [{"at": 0.3, "event": "three real files drop in"}, {"at": 0.75, "event": "three ghost outlines draw"}]),
    beat("B02",
         "Why would anyone care? The first alternative is a fixed dashboard, like the Tableau dashboard in my "
         "marketing campaign project, which I made with AI help. It answers the questions planned in advance. "
         "A new question means building a new view.",
         "B02_Dashboard",
         "A dashboard with three coloured channel bars grows; a new question card slides toward it and bounces back.",
         [{"at": 0.4, "event": "dashboard bars"}, {"at": 0.8, "event": "new question bounces"}]),
    beat("B03",
         f"The second is a general chat assistant. On {CHAT_DATE}, I gave {CHAT_TOOL} my campaign data and asked "
         f"which channel had the highest ROAS. {chat_line} CheckedSQL runs every answer, shows its query, and scores it.",
         "B03_ChatTest",
         "My real ChatGPT answer (cropped screenshot, Oct 24) framed; an arrow to 'Search'; my answer-key card agrees with a check; then a row of ten questions with only one answered: one answer is not a record.",
         [{"at": 0.25, "event": "screenshot"}, {"at": 0.4, "event": "arrow to its answer"}, {"at": 0.5, "event": "key agrees"}, {"at": 0.75, "event": "1 of 10"}]),
    beat("B04",
         "Who opens it? A hiring manager for a data analyst role. In the first sixty seconds, they open the "
         "README, run one command, python three checker dot P Y, and see a score table. That command already works today.",
         "B04_SixtySeconds",
         "'60 s'; a README window; a dark terminal strip with the real command and the real score line '10/10'.",
         [{"at": 0.2, "event": "60 s"}, {"at": 0.45, "event": "README"}, {"at": 0.75, "event": "terminal + score"}]),
    beat("B05",
         "What will it prove? That I can get marketing metrics right and check them against an answer key. "
         "And three course skills: a prompt contract, verification against known answers, and evaluation I can repeat. "
         "Verification and evaluation now have real evidence: the checker and its score table. The contract is next.",
         "B05_Proves",
         "Three cards: contract (ghost, planned), verification and evaluation (solid, each gets a check); an evidence page slides under the two real ones.",
         [{"at": 0.35, "event": "three cards"}, {"at": 0.7, "event": "checks on the real two"}]),
    beat("B06",
         "What's out: it will never change the database. The checker already refuses anything but a single "
         "read-only SELECT. One schema, no dashboards, and no real company data: these twenty-four rows are synthetic.",
         "B06_ReadOnly",
         "The campaigns table; a write arrow is crossed out; a read arrow gets a check, labelled SELECT only; '24 rows · synthetic'.",
         [{"at": 0.25, "event": "write crossed"}, {"at": 0.5, "event": "SELECT only + check"}, {"at": 0.8, "event": "24 rows"}]),
]

BASELINE = remotion(
    "B07", "pitch",
    "What came first was the baseline, before any Claude call: ten questions, an answer key worked out from "
    "the totals, and baseline S Q L drafted with Claude. The checker printed ten out of ten. Then I added two deliberately wrong "
    "queries that average ROAS row by row. The checker failed both.",
    "ShowTellCard",
    {"kind": "focus", "heading": "Baseline run, Oct 24 (real)", "focus": 2,
     "items": [{"label": "Q03 overall ROAS", "value": "2.74 PASS"},
               {"label": "Q06 best channel", "value": "Search PASS"},
               {"label": "Q06 trap: row average", "value": "Email FAIL"},
               {"label": "Q07 Email ROAS", "value": "2.29 PASS"},
               {"label": "Score", "value": "10/10"}],
     "durationSeconds": 14.0},
    [{"at": 0.05, "event": "real score rows land"}, {"at": 0.6, "event": "lens stops on the trap row"}],
    gate="CARD", lane="card",
    cue_phrases=["ten out of ten", "two deliberately wrong"])
BASELINE["lane"] = "card"

B += [BASELINE,
    beat("B08",
         "What could sink it? An answer that looks right but isn't. These are Email's eight real rows. Four of "
         "them spend almost nothing and return fourteen to twenty times that. Average the row ratios, and Email's "
         "ROAS comes out at nine point seven five.",
         "B08_RowTrap",
         "Eight blue bars, one per Email row, height = that row's ROAS; four tower; a dashed line lands at 9.75, labelled row average.",
         [{"at": 0.4, "event": "eight row bars grow"}, {"at": 0.8, "event": "average line 9.75"}]),
    beat("B09",
         "Divide total revenue by total spend instead, and Email is two point two nine. The best channel is "
         "Search, not Email. Both numbers look plausible. My fix: the metric definition goes in the prompt "
         "contract, and the test set has ratio questions, so this mistake gets caught, as it just was.",
         "B09_TotalFix",
         "The 9.75 ghost bar is crossed out; three channel bars at their true ROAS (Email 2.29, Search 3.98, Social 1.05); a check lands on Search.",
         [{"at": 0.25, "event": "true bars"}, {"at": 0.55, "event": "check on Search"}, {"at": 0.85, "event": "test page"}]),
    beat("B10",
         "Why this project? Mostly to learn. My earlier marketing campaign repository was built with a lot of AI "
         "help, so it shows the domain I care about, metrics like click-through rate and return on ad spend, more "
         "than it proves I can code alone. New to me: writing and checking S Q L myself, calling Claude from "
         "Python, prompt contracts, and evaluation. This project is how I'll prove those.",
         "B10_HaveNew",
         "Left: a closed taped box labelled have: campaign KPIs (repo built with AI help). Right: an open box that four pages drop into, labelled new.",
         [{"at": 0.2, "event": "have box"}, {"at": 0.6, "event": "new box fills"}]),
    beat("B11",
         "So, what exists today: my two earlier repositories, this film, and the first piece of CheckedSQL: the "
         "dataset, the questions, the answer key, and the checker. What will exist: the prompt contract, the "
         "Claude step, thirty questions, and the evaluation log. What I don't know yet is whether thirty is "
         "enough. I'll find out by watching whether new questions keep finding new kinds of failure.",
         "B11_TodayWill",
         "Left: solid boxes for what exists (two repos, film, checker). Right: ghost boxes for what will exist, drawn one by one.",
         [{"at": 0.2, "event": "today boxes"}, {"at": 0.55, "event": "will boxes draw"}]),
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
