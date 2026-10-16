#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for the INFO 7375 final project pitch film (Klaxon).

Format: the brutalist.art show-tell skill (one drawn isometric picture per beat,
minimal labels, the voice explains). The assignment overrides the skill's
bookends: first person as Aravind, no instructor name, persona or credit line,
so there is no "Liam, in for Bear" greeting, no Your Turn composer and no
ClaudeTitleOutro card (it hard-codes the instructor's handle). The film ends on
its own drawn title beat (BOUT, Manim).

Honesty rule: past tense only for what exists (the first piece, run on
2026-10-09). Everything else is "will". Drawn beats that sketch the future
product carry an on-screen "constructed" tag; the beats that show the real run
carry "real run, Oct 9".

Narration drafted by Claude (Claude Code, Opus 5.5) on 2026-10-09 for Aravind
to review and change; nothing here is final until he approves it.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "klaxon-pitch"
TITLE = "Klaxon: An AI On-Call Engineer That Checks the Money"
AUTHOR = "Aravind Sundaravadivelu"

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, "
                 "with the voice carrying the explanation. The negative space is the style, so only underfill "
                 "and clustered are waived; edge-bleed, empty-frame and contrast still apply.")


def beat(bid, act, narration, cls, image, show, tag):
    """A drawn Manim body beat. tag is the on-screen honesty label: 'constructed' or 'real run'."""
    return {"beat_id": bid, "act": act, "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.9, 1),
            "voice": "am_onyx", "engine": "kokoro", "honesty_tag": tag,
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image},
            "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.9, 1),
         "voice": "am_onyx", "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show, "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


OPEN = [
    remotion("BIDEA", "the question",
             "Hi, I'm Aravind, and this is a synthetic voice reading my pitch. My final project will be an AI "
             "on-call engineer that doesn't stop at fixing the alert. It will prove the fix worked.",
             "BrutalistHesitantWriter",
             {"text": "An AI on-call engineer\nthat fixes the alert", "triggerWords": "fixes the alert",
              "replacementWords": "proves the fix worked", "fontSize": 78, "charMs": 30, "hesitateBetween": 8,
              "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20, "seed": SLUG, "banner": ""},
             [{"at": 0.0, "event": "types 'An AI on-call engineer / that fixes the alert'"},
              {"at": 0.5, "event": "reconsiders 'fixes the alert' and replaces it with 'proves the fix worked'"}],
             lead_silence_s=0.8,
             motion_claim="The writer types the naive goal (fix the alert) and corrects it to the real one (prove the fix worked).",
             qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer opener: the correction is the motion."}),
    remotion("BDEFS", "terms",
             "Two terms. A webhook: a message a payment provider sends my server when money moves. And idempotent: "
             "safe to repeat, so a second copy changes nothing.",
             "ClaudeDefinitions",
             {"title": "Terms In This Film",
              "terms": [{"term": "webhook", "meaning": "a message a payment provider sends my server"},
                        {"term": "idempotent", "meaning": "safe to repeat: a second copy changes nothing"}],
              "folderLabel": AUTHOR},
             [{"at": 0.15, "event": "'webhook' lands"}, {"at": 0.55, "event": "'idempotent' lands"}], gate="CARD",
             qc={"sparse_by_design": True, "sparse_reason": "TERMS card: two prerequisites, one line each."}),
]

BODY = [
    beat("B00", "what it is",
         "Klaxon will be an AI on-call engineer for a payments system. When an alert fires, it will investigate, "
         "propose a fix with evidence, wait for a person to approve it, and then check that the system is healthy "
         "and the money is right.",
         "B00_WhatItIs",
         "The payments server tower and the Klaxon workstation sit on stage. The tower's alarm light turns terracotta, "
         "a cable draws from the workstation to the tower, a diagnosis slip appears and gets an ink check (approved), "
         "and two ink checks land beside the tower (healthy, money right).",
         [{"at": 0.3, "event": "alarm light"}, {"at": 0.4, "event": "cable"}, {"at": 0.65, "event": "approved"},
          {"at": 0.85, "event": "two checks"}], "constructed"),
    beat("B01", "what exists when done",
         "When it's done, it will be a public GitHub repo: a small payments system, incidents whose causes I know in "
         "advance, the Klaxon agent, and an evaluation report.",
         "B01_Repo",
         "A release parcel labelled 'GitHub repo' opens; four small parts rise out of it one by one as they are named: "
         "a server, a test bench, a workstation, a binder.",
         [{"at": 0.2, "event": "lid lifts"}, {"at": 0.35, "event": "server"}, {"at": 0.55, "event": "bench"},
          {"at": 0.7, "event": "workstation"}, {"at": 0.85, "event": "binder"}], "constructed"),
    beat("B02", "why care: the quiet incident",
         "Why would anyone care? Payment providers send webhooks at least once, so the same one can arrive twice. If "
         "my code books it twice, the money is wrong, and the dashboard still shows every request succeeded.",
         "B02_QuietIncident",
         "Parcels (webhooks) ride a conveyor into the server; one parcel arrives a second time. Beside it a dashboard's "
         "bars stay full with an ink check.",
         [{"at": 0.25, "event": "parcels ride in"}, {"at": 0.5, "event": "the same parcel again"},
          {"at": 0.8, "event": "dashboard full, check"}], "constructed"),
    beat("B03", "alternatives I looked at",
         "The real alternatives I looked at: Holmes G P T, an open-source S R E agent that investigates incidents from "
         "logs, metrics and traces. And the manual way: an engineer with a dashboard and a runbook.",
         "B03_Alternatives",
         "A dark tool block labelled HolmesGPT undocks its tool; then an inspection lamp, the manual way, lowers over a "
         "runbook page.",
         [{"at": 0.2, "event": "HolmesGPT"}, {"at": 0.75, "event": "lamp, manual"}], "constructed"),
    beat("B04", "what their verification checks",
         "Holmes G P T can even verify a deploy, by comparing error rates, latency and logs. Those are the signals that "
         "stayed green here. In its docs, I didn't find a built-in check that the money is right.",
         "B04_TheirCheck",
         "The HolmesGPT block sits beside the green dashboard and an ink check lands on the dashboard; then a ghost "
         "outline of a money-check scanner draws in, empty.",
         [{"at": 0.3, "event": "check on the dashboard"}, {"at": 0.8, "event": "ghost money check"}], "constructed"),
    beat("B05", "the value, in one line",
         "So Klaxon will save a payments on-call engineer from approving a fix that looks green while the money is "
         "still wrong.",
         "B05_MoneyCheck",
         "Klaxon's money-check scanner (solid now) passes a parcel and flags it with a terracotta dot; the approval "
         "stamp above the page lifts back instead of coming down.",
         [{"at": 0.25, "event": "scanner flags"}, {"at": 0.6, "event": "stamp down"}, {"at": 0.9, "event": "stamp lifts"}],
         "constructed"),
    beat("B06", "who opens it",
         "Who opens it? A hiring manager for new-grad backend roles. In the first minute, the read me will walk one "
         "incident to a passing money check, and one command will replay it on their machine.",
         "B06_Reader",
         "A README page on a review desk; a cursor clicks a command pill; a parcel passes the scanner and an ink check lands.",
         [{"at": 0.2, "event": "README"}, {"at": 0.6, "event": "click"}, {"at": 0.85, "event": "check"}], "constructed"),
    beat("B07", "what it proves 1",
         "What will it prove? The skills this course teaches. A prompt contract: every diagnosis has a fixed format, "
         "checked before anything runs. And source grounding: every claim cites a metric, a log line or a trace.",
         "B07_Contract",
         "A diagnosis page with three rows; a cable draws from each row to its source: a bar chart, a log page, a trace.",
         [{"at": 0.3, "event": "diagnosis page"}, {"at": 0.65, "event": "cables to sources"}], "constructed"),
    beat("B08", "what it proves 2",
         "A bounded agent loop, with budgets and an approval gate. Checks after every fix. And an evaluation of accuracy, "
         "time and cost, on incidents with known causes.",
         "B08_LoopEval",
         "Incident parcels wait in a queue; one moves through a permission gate whose barrier lifts; a budget tray loses "
         "one token for each step.",
         [{"at": 0.2, "event": "queue"}, {"at": 0.45, "event": "gate"}, {"at": 0.8, "event": "budget token"}], "constructed"),
    beat("B09", "fair conclusion",
         "A reviewer could fairly conclude that I can build a gated agent, check its claims, and measure where it fails, "
         "from the tests, traces and evaluation. Not that it could run a real company's on-call.",
         "B09_Reviewer",
         "An evidence binder opens on a review desk; its record pages fan out one at a time.",
         [{"at": 0.3, "event": "binder opens"}, {"at": 0.6, "event": "records"}], "constructed"),
    beat("B10", "in and out",
         "What's in: one demo payments system, six incident types, approved fixes with rollback, and the evaluation. "
         "What's out, on purpose: Klaxon will never act without approval, and never on anything I don't own.",
         "B10_InOut",
         "A fix parcel waits at a permission gate; a stamp comes down; the barrier lifts for our server only. A second "
         "server outside a dashed line stays behind a closed barrier.",
         [{"at": 0.3, "event": "parcel at gate"}, {"at": 0.6, "event": "approval, barrier lifts"},
          {"at": 0.85, "event": "outside server stays closed"}], "constructed"),
    beat("B11", "first piece: it ran",
         "What comes first? The money check, and it already exists. It ran on October ninth, on synthetic data. A fake "
         "provider sent one payment twice. The dashboard showed zero errors, and the ledger balanced.",
         "B11_FirstRun",
         "The real run, drawn: seven parcels ride into the server, the third one again at the end; the dashboard reads "
         "0 errors; the ledger binder shows a balance mark.",
         [{"at": 0.35, "event": "seven deliveries"}, {"at": 0.75, "event": "0 errors, balanced"}], "real run"),
    remotion("B12", "first piece: the money check failed",
             "But the money check failed. One payment was posted twice, and the books were off by sixty-nine dollars "
             "and sixty-eight cents. With the idempotent handler, the same run passed.",
             "ShowTellCard",
             {"kind": "focus", "heading": "Real run, Oct 9, synthetic data",
              "items": [{"label": "Ledger balanced", "value": "PASS", "sub": ""},
                        {"label": "Posted once", "value": "FAIL", "sub": ""},
                        {"label": "Matches provider", "value": "FAIL", "sub": ""},
                        {"label": "Off by", "value": "+$69.68", "sub": ""},
                        {"label": "Idempotent run", "value": "PASS", "sub": ""}],
              "focus": 4, "cues": [0.2, 0.31, 0.37, 0.7]},  # on "posted", "books", "off", "idempotent"; holds through 45-55%
             [{"at": 0.2, "event": "lens to 'Posted once FAIL'"}, {"at": 0.37, "event": "lens to 'Off by +$69.68'"},
              {"at": 0.7, "event": "lens to 'Idempotent run PASS'"}],
             gate="CARD", lane="card",
             motion_claim="A lens walks the real money-check rows and stops on what failed, then on the passing fixed run.",
             why_card="The idea is a set of real numbers from the 2026-10-09 run; the lens finding the failing row is the claim; a drawing would have to invent the same rows."),
    beat("B13", "what could sink it",
         "What could sink it? Klaxon grading its own homework. I build both the incidents and the agent, so the "
         "incidents could end up too easy for it.",
         "B13_Risk",
         "On one experiment bench, the same cursor places the incident sample and then the agent block; a loop arrow "
         "draws between them.",
         [{"at": 0.35, "event": "incident placed"}, {"at": 0.6, "event": "agent placed"}, {"at": 0.85, "event": "loop"}],
         "constructed"),
    beat("B14", "what I will do about it",
         "So I'll write the incidents and their answers first, keep a held-out set the agent never sees during "
         "development, and report the failures, not just the wins.",
         "B14_HeldOut",
         "Answer pages go onto a shelf first; then incident parcels slide into a vault whose locking bar closes.",
         [{"at": 0.2, "event": "answers first"}, {"at": 0.55, "event": "vault locks"}], "constructed"),
    beat("B15", "why this project",
         "Why this project? I wanted a real product idea that one person can build small, that uses the skills in "
         "the jobs I'm applying for, and that can be my final project for both of my courses. So it's a mix of "
         "showing off and learning.",
         "B15_Why",
         "Two trays side by side: the left holds tools I already have, the right fills with tools that are new to me.",
         [{"at": 0.3, "event": "one project"}, {"at": 0.8, "event": "show off / learn"}], "constructed"),
    beat("B16", "existing skills, with evidence",
         "Skills I already have: webhooks, idempotency and code review. At my co-op, I caught a webhook data-loss path, "
         "an H MAC check that crashed, and a money-unit error off by a factor of a hundred. That code is private. "
         "In public, there's the Stripe webhook signature check I wrote for EventEase, a team project.",
         "B16_Record",
         "An evidence binder opens to three record pages; an ink check lands on each as it is named. Then a small "
         "public repo parcel labelled EventEase appears.",
         [{"at": 0.3, "event": "data-loss"}, {"at": 0.4, "event": "HMAC"}, {"at": 0.55, "event": "100x"},
          {"at": 0.85, "event": "EventEase"}], "constructed"),
    beat("B17", "new skills",
         "New to me: Kafka, Kubernetes, Open Telemetry, an agent loop and an M C P server built from scratch, Lang Graph, "
         "and evaluation design.",
         "B17_New",
         "Tool blocks undock one by one onto the Klaxon workstation's bench as they are named.",
         [{"at": 0.2, "event": "first tool"}, {"at": 0.8, "event": "last tool"}], "constructed"),
    beat("B18", "exists today, will exist",
         "So today, the plan and the first piece exist. Everything else will exist by December.",
         "B18_ExistsWill",
         "Two shelves. Left, solid: a binder with a check (the first piece). Right, ghost outlines of the server, the "
         "workstation and the bench, waiting.",
         [{"at": 0.3, "event": "exists"}, {"at": 0.7, "event": "will exist"}], "constructed"),
    beat("BOUT", "outro",
         "Klaxon. By Aravind Sundaravadivelu.",
         "BOUT_Title",
         "The film's server tower with an ink check, the word Klaxon, and the author's name.",
         [{"at": 0.1, "event": "title"}, {"at": 0.5, "event": "name"}], "constructed"),
]
BODY[-1]["kind"] = "outro_voice"
BODY[-1]["tail_silence_s"] = 1.0

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT PITCH · KLAXON", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "aravind-s", "channel_title": AUTHOR, "author": AUTHOR,
    "persona": "Aravind Sundaravadivelu, first person (synthetic Kokoro am_onyx voice, disclosed in BIDEA)",
    "voice": "am_onyx", "voice_kokoro": "am_onyx", "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9",
    "width": 1920, "height": 1080, "caption_policy": "none",
    "course": "INFO 7375, Fall 2026, Final Project Pitch Film",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Assignment rules govern: narrate as myself, no instructor name, persona or credit line. "
                              "Opens on the hesitant writer and a terms card; a pitch has no viewer task, so no Your Turn; "
                              "no verdict card. The toolkit's ClaudeTitleOutro hard-codes the instructor's handle, so the "
                              "outro is a drawn Manim title beat instead (bookend_check reports it; see FRICTIONAL.md)."),
    "honesty": ("Past tense only for the first piece, which ran on 2026-10-09 (synthetic data, seeded, in-process). "
                "Everything else is will. Drawn beats are labelled constructed on screen; the real-run beats are "
                "labelled real run. No Claude response is shown."),
    "audience": "a hiring manager or senior engineer, and the INFO 7375 graders",
    "source_doc": "klaxon/docs/pitch/PROJECT-BRIEF-DRAFT.md; klaxon/evidence/first-piece/*.json (real run 2026-10-09)",
    "tags": ["Klaxon", "AI SRE", "on-call", "payments", "webhooks", "idempotency", "INFO 7375"]},
    "beats": OPEN + BODY}

# Keep measured audio (and its file paths) across re-runs of this script, so a
# narration-only edit does not wipe durations that still match.
old = HERE / "beat_sheet.json"
if old.exists():
    prev = {b["beat_id"]: b for b in json.loads(old.read_text()).get("beats", [])}
    for b in sheet["beats"]:
        p = prev.get(b["beat_id"])
        if p and p.get("narration_text") == b["narration_text"]:
            for key in ("actual_duration_s", "audio_file"):
                if key in p:
                    b[key] = p[key]

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in sheet["beats"])
print(len(sheet["beats"]), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in sheet["beats"])), "s")
