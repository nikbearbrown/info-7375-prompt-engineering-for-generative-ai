#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for cite-the-line-project-film.

INFO7375 project film by Pavan Jayant Majji, in the four parts the assignment asks for:
  1. Executive summary (what and why, no "how")   B00–B03
  2. Introduction (what others have done)          B04–B06
  3. Methods (how, step by step, resources)        B07–B13
  4. Evaluation (how I'll know it worked)          B14–B17
Built with the Brutalist show-tell skill: one drawn isometric illustration per body beat.

Same persona rules as the pitch film: first-person narration read by the free Kokoro
am_onyx voice; no instructor name, handle, greeting or credit; outro shows my own handle
(needs the local ClaudeTitleOutro patch, outro-handle.patch). Your Turn and verdict card exempt.

Honesty: nothing in the project is built yet. Every body drawing carries a
"constructed sketch" tag; no result numbers appear except Microsoft's published figure,
which is attributed on screen.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "cite-the-line-project-film"
TITLE = "Cite-the-Line"
HANDLE = "Pavan Majji"
VOICE = "am_onyx"
TAG = "a small 'constructed sketch' tag in the lower-right corner"


def beat(bid, part, narration, cls, image, show):
    return {"beat_id": bid, "act": part, "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration,
            "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
            "voice": VOICE, "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image}}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration,
         "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


S, I, M, E = "1-executive-summary", "2-introduction", "3-methods", "4-evaluation"

B = [
 # ── 1. Executive summary ──────────────────────────────────────────────────
 beat("B00", S,
      "When a backend service fails, engineers often paste the error into a chatbot and act on the answer, without checking it against the logs.",
      "B00_PasteHabit",
      f"A log page, a chat bubble labelled 'chatbot', and a fix slip, joined left to right by kraft connectors; {TAG}.",
      [{"at": 0.1, "event": "log page"}, {"at": 0.2, "event": "chat bubble"}, {"at": 0.3, "event": "fix slip"}]),
 beat("B01", S,
      "Cite the Line will read the logs from a failing service, name the likely cause, and point to the exact lines that prove it.",
      "B01_LensCites",
      f"A lens slides over a log page; two lines get terracotta dots; a slip labelled 'cause' lands beside it; {TAG}.",
      [{"at": 0.1, "event": "lens"}, {"at": 0.2, "event": "two lines marked"}, {"at": 0.3, "event": "cause slip"}]),
 beat("B02", S,
      "When the logs don't show enough, it will say so and hand the decision to a person, instead of guessing.",
      "B02_HandOff",
      f"The lens finds nothing on a sparse page; an empty slip labelled 'not enough' is passed by a connector into a tray labelled 'engineer'; {TAG}.",
      [{"at": 0.1, "event": "lens sweeps"}, {"at": 0.25, "event": "not-enough slip"}, {"at": 0.33, "event": "tray"}]),
 beat("B03", S,
      "Why it matters: a wrong root cause sends a team to fix the wrong thing. An answer you can check against the log is one you can trust, or reject.",
      "B03_CheckedVsNot",
      f"Left: a lone slip with a cross, labelled 'unchecked'. Right: a slip linked by connectors to two marked log lines, with a check, labelled 'checked'; {TAG}.",
      [{"at": 0.1, "event": "unchecked slip, cross"}, {"at": 0.25, "event": "checked slip linked to lines"}]),
 # ── 2. Introduction ───────────────────────────────────────────────────────
 beat("B04", I,
      "Others have tried this. Microsoft researchers built R C A Copilot, which predicts the root cause category of cloud incidents. On a year of Microsoft's own incidents, they report accuracy up to about seventy-seven percent.",
      "B04_Rcacopilot",
      f"A kraft data box with a padlock on its face; beside it the hero figure 'up to 77%' with the caption 'per Microsoft Research'; {TAG}.",
      [{"at": 0.1, "event": "locked data box"}, {"at": 0.25, "event": "hero figure + attribution"}]),
 beat("B05", I,
      "Datadog's Bits A I S R E investigates alerts inside Datadog's paid platform, and Datadog reports its own results.",
      "B05_Datadog",
      f"A closed box on a dark plinth labelled 'vendor platform'; a log page goes in, a score card comes out; the box never opens; {TAG}. No logos.",
      [{"at": 0.1, "event": "closed box"}, {"at": 0.25, "event": "page in, score card out"}]),
 beat("B06", I,
      "Both scores come from data an outsider can't see or re-run. Mine will publish the incidents, the known answers, and every mistake, so anyone can check the score themselves.",
      "B06_LockedVsOpen",
      f"Side by side: a score card wired to a locked box ('can't re-check'), and a score card wired to a row of open log pages ('anyone can re-check'); {TAG}.",
      [{"at": 0.1, "event": "left: card + locked box"}, {"at": 0.25, "event": "right: card + open pages"}]),
 # ── 3. Methods ────────────────────────────────────────────────────────────
 beat("B07", M,
      "Step one, the data. I'll build a small FastAPI service with a Postgres database, running in Docker.",
      "B07_Service",
      f"A server stack labelled 'FastAPI' joined by a connector to a database cylinder labelled 'Postgres'; {TAG}.",
      [{"at": 0.1, "event": "server"}, {"at": 0.25, "event": "database + connector"}]),
 beat("B08", M,
      "Then I'll break it on purpose: a slowed database, a bad config, a failing dependency. Each break produces real logs with a known cause, so no private data is needed.",
      "B08_BreakService",
      f"The server's three lights turn terracotta one by one; under each a log page drops out with a known-cause dot; {TAG}.",
      [{"at": 0.1, "event": "server"}, {"at": 0.2, "event": "lights fail, pages drop"}]),
 beat("B09", M,
      "Step two, the agent loop. For each incident, it reads the logs, asks Claude Code for a diagnosis in a fixed format, checks it, records it, and moves on.",
      "B09_Loop",
      f"A kraft ring with four stations: log page, 'Claude Code' box, checker slip with a check, and a record stack; a terracotta dot travels the ring once; {TAG}.",
      [{"at": 0.1, "event": "ring + stations"}, {"at": 0.25, "event": "dot travels the loop"}]),
 beat("B10", M,
      "Its tools are limited. It can read log files, and nothing else. It never restarts, rolls back, or changes anything.",
      "B10_ReadOnly",
      f"Left: a log page under a lens, labelled 'read'. Right: a restart button, labelled 'restart', which gets crossed out; {TAG}.",
      [{"at": 0.1, "event": "read"}, {"at": 0.25, "event": "restart button"}, {"at": 0.65, "event": "crossed out"}]),
 beat("B11", M,
      "It stops on rules, not on the model's say-so: three runs per incident, and at most one retry when an answer breaks the format.",
      "B11_StopRules",
      f"Three slips in a row labelled '3 runs', then an octagonal stop sign labelled 'stop'; {TAG}.",
      [{"at": 0.1, "event": "three runs"}, {"at": 0.25, "event": "stop sign"}]),
 beat("B12", M,
      "And there's a human gate. Any diagnosis marked not enough evidence, or rejected by the checker, goes to an engineer, who makes the call.",
      "B12_HumanGate",
      f"An empty slip and a slip with a cross slide into a tray labelled 'engineer'; {TAG}. No person icon.",
      [{"at": 0.1, "event": "two slips"}, {"at": 0.25, "event": "into the engineer tray"}]),
 beat("B13", M,
      "Do I have what I need? Claude Code through my university seat, so no paid credits. My laptop for compute. Docker and Python, which I already use. No new accounts.",
      "B13_Resources",
      f"A laptop labelled 'laptop' and a seat card labelled 'Claude Code seat'; each gets a check; {TAG}.",
      [{"at": 0.1, "event": "laptop"}, {"at": 0.2, "event": "seat card"}, {"at": 0.65, "event": "checks"}]),
 # ── 4. Evaluation ─────────────────────────────────────────────────────────
 beat("B14", E,
      "To test it, I'll create about ten incidents with known causes, including hard ones, where the loudest error isn't the real cause, and ones with no clear answer.",
      "B14_TenIncidents",
      f"Ten small log pages in two rows, each with a known-cause dot, labelled 'known causes'; {TAG}.",
      [{"at": 0.1, "event": "pages arrive"}, {"at": 0.3, "event": "label"}]),
 beat("B15", E,
      "Three checks. Every cited line must exist in the log; one invented line counts as a failure. The cause must match the known answer. And on the no-answer cases, it must decline instead of guessing.",
      "B15_ThreeChecks",
      f"Three columns: a slip with line dots ('lines exist'), a slip with a cause pill ('cause matches'), and an empty slip; each gets a check; {TAG}.",
      [{"at": 0.1, "event": "three slips"}, {"at": 0.25, "event": "checks"}]),
 beat("B16", E,
      "The baseline: a simple keyword script, scored on the same incidents. If Claude can't beat it, the tool didn't work, or my test was too easy. Either way, I'll publish the result.",
      "B16_Baseline",
      f"Two empty bar frames labelled 'keyword script' and 'Claude', with no values drawn: there are no results yet; {TAG}.",
      [{"at": 0.1, "event": "two empty frames"}, {"at": 0.65, "event": "base line"}]),
 beat("B17", E,
      "Today, what exists is this plan. Everything else in this film is what I will build. The details are in the appendix.",
      "B17_ExistsVsWill",
      f"A tiny solid dark box labelled 'exists' beside a large pile of ink-outlined boxes labelled 'will exist'; {TAG}.",
      [{"at": 0.1, "event": "exists"}, {"at": 0.25, "event": "will exist"}]),
]

OPEN = [
 remotion("BIDEA", "the question",
    "Hi, I'm Pavan Majji, a backend software engineer. This is my final project, Cite the Line. When something breaks, the better question isn't how to fix it, but which log lines prove the cause.",
    "BrutalistHesitantWriter",
    {"text": "What caused this error,\nand how do I fix it?",
     "triggerWords": "how do I fix it", "replacementWords": "which log lines prove it",
     "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2,
     "jitter": 20, "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types the fix-it question"},
     {"at": 0.6, "event": "corrects 'how do I fix it' → 'which log lines prove it'"}],
    lead_silence_s=0.8,
    motion_claim="The writer corrects the naive fix-it question into the real one.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
 remotion("BDEFS", "terms",
    "Three terms. Root cause: the failure that started the problem. Source grounding: every claim points to the exact text it came from. A human gate: a point where the system hands a decision to a person.",
    "ClaudeDefinitions",
    {"title": "Terms In This Film",
     "terms": [{"term": "root cause", "meaning": "the failure that started the problem"},
               {"term": "source grounding", "meaning": "every claim points to the exact text it came from"},
               {"term": "human gate", "meaning": "where the system hands a decision to a person"}],
     "folderLabel": HANDLE},
    [{"at": 0.12, "event": "'root cause'"}, {"at": 0.45, "event": "'source grounding'"},
     {"at": 0.75, "event": "'human gate'"}],
    gate="CARD",
    qc={"sparse_by_design": True, "sparse_reason": "TERMS card: three prerequisites, one line each."}),
]

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, "
                 "with the voice carrying the explanation. The negative space is the style, so only underfill "
                 "and clustered are waived; edge-bleed, empty-frame and contrast still apply.")
for b in B:
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}

B = OPEN + B
B.append({"beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW",
          "narration_text": "Cite the Line. I'm Pavan Majji.",
          "estimated_duration_s": 4.0, "voice": VOICE, "engine": "kokoro",
          "shot": {"type": "REMOTION", "source": "own",
                   "show": [{"at": 0.0, "event": "title restates; handle"}],
                   "remotion": {"pattern": "ClaudeTitleOutro",
                                "props": {"title": TITLE, "slug": SLUG, "handle": HANDLE, "subline": "",
                                          "hideMascot": True}}},
          "kind": "outro_voice", "tail_silence_s": 1.0})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO7375 · FINAL PROJECT FILM",
    "skill": "show-tell", "style_preset": "show-tell",
    "channel": "pavan-majji", "channel_title": HANDLE,
    "persona": "Pavan Majji (first person; synthetic Kokoro am_onyx voice reading his script)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Teardown",
    "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none", "greeting_language": "English (Hi)",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("show-tell opens on the hesitant writer + terms card, so no composer cold open; "
                              "no verdict card; no Your Turn (a project film, not a tutorial). Outro kept, "
                              "with the author's own handle (assignment: no instructor name, persona, or credit)."),
    "structure": ["executive summary B00–B03", "introduction B04–B06", "methods B07–B13", "evaluation B14–B17"],
    "audience": "hiring managers and senior engineers for backend software engineering roles",
    "source_doc": "PROJECT-BRIEF.md; APPENDIX.md; Chen et al., arXiv:2305.15778; Datadog Bits AI SRE documentation",
    "playlist": "INFO7375 Final Project", "chapter_number": 0,
    "tags": ["INFO7375", "final project", "log triage", "root cause analysis", "agentic AI",
             "human gate", "LLM evaluation", "Claude Code", "FastAPI", "Postgres"]},
    "beats": B}

# Carry measured audio forward from an existing sheet, so re-running never wipes durations.
prev_path = HERE / "beat_sheet.json"
if prev_path.exists():
    prev = {b["beat_id"]: b for b in json.loads(prev_path.read_text()).get("beats", [])}
    for b in sheet["beats"]:
        old = prev.get(b["beat_id"])
        if old and old.get("narration_text") == b["narration_text"]:
            for k in ("actual_duration_s", "audio_file"):
                if k in old:
                    b[k] = old[k]
        elif old and "actual_duration_s" in old:
            print(f"{b['beat_id']}: narration changed; re-voice with --only {b['beat_id']}")

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(B), "beats; est", round(sum(b["estimated_duration_s"] for b in B)), "s")
