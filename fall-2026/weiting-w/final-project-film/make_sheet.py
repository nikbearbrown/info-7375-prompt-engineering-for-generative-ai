#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the INFO 7375 final-project pitch film.

Built on the show-tell chassis (skills/make/show-tell/SKILL.md), copied from
reference/example-make_sheet.py. Every body beat is ONE drawn isometric Manim
illustration on the Claude cream stage, with at most a few words of label; the
narration carries the explanation.

STRUCTURE (rewritten 2026-11-22). The assignment now fixes the order of the film:

  1. EXECUTIVE SUMMARY — what I am building and why anybody would care. No "how".
  2. INTRODUCTION      — what already exists, who has tried this, what they got.
  3. METHODS           — the plan, the data, the steps, and what it needs to run.
  4. EVALUATION        — how I will know whether it worked.

The four act names are spoken and are also printed as the on-screen label of each
act's first beat (B00, B06, B11, B16), so the structure is visible without audio.
Detail that does not fit the film lives in PROJECT-BRIEF.md, which is the appendix.

FOUR DELIBERATE DEVIATIONS from show-tell doctrine, all forced by the course
assignment ("Narrate as yourself. Do not use the instructor's name, persona, or
credit line."). Each one is logged in FRICTIONAL.md:

  1. BIDEA greeting is NOT "Hallo. This is Liam, in for Bear." — it is the
     author's own first-person opening.
  2. metadata.persona / channel name the author, not "Liam (in for Bear)".
  3. folderLabel in BDEFS and BHTF, and handle + narration in BOUT, name the
     author, not @NikBearBrown. SKILL.md marks the outro "never exempt" and
     OUTRO-LOCK.md enforces it, so the bookend/outro check is expected to flag
     this film. That report ships as-is with the reason, not papered over.
  4. Voice is Kokoro af_bella rather than the default am_onyx ("Liam"). It is a
     synthetic voice reading the author's own words, and it is disclosed as such
     in BIDEA, on the BOUT end card, and in SOURCES.md — the same practice the
     author used on her week-01 film for this course. Swap to a real recording of
     her voice if one is made; then the disclosure comes out and nothing else changes.

HONESTY (assignment rule): nothing in this film exists yet except the Unity game
referenced in B09 and B16. Every drawing of the proposed tool carries a "proposed"
label on screen; the beat describing past experience carries "spring 2026". Past
tense is used only there. Every claim about another tool in act 2 is quoted from
that tool's own documentation and is listed in FACTCHECK.md with its source.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "show-tell-the-names-nothing-checks"
TITLE = "The Names Nothing Checks"
AUTHOR = "Weiting Wang"
HANDLE = "@WeitingWang0704"


def beat(bid, act, narration, cls, image, show):
    return {"beat_id": bid, "act": act, "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration,
            "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
            "voice": "af_bella", "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image,
                     "show": show, "manim": {"class": cls}, "motion_claim": image}}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration,
         "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
         "voice": "af_bella", "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


# ---------------------------------------------------------------- body (drawn)
# Cast, kept for the whole film: the project crate (left half = C# pages,
# right half = asset blocks), the string thread between them, two gates, the
# effect lamp, and the checklist slip.

EXEC, INTRO, METHOD, EVAL = "executive summary", "introduction", "methods", "evaluation"

B = [
 # ══════════════════════ 1. EXECUTIVE SUMMARY — what, and why care ═══════════
 beat("B00", EXEC,
      "I am building a checker for Unity projects. Start with the project itself. "
      "One side holds the C sharp scripts. The other holds the assets, and the assets "
      "hold the project's real names.",
      "B00_Project",
      "An open isometric crate divided in two: pale pages stack on the left, dark asset "
      "blocks rise on the right. Labels: the act title 'executive summary' top left, "
      "'scripts' and 'assets' beside each half.",
      [{"at": 0.15, "event": "crate lands with floor shadow, act title"},
       {"at": 0.45, "event": "pages stack on the left, label"},
       {"at": 0.75, "event": "asset blocks rise on the right, label"}]),

 beat("B01", EXEC,
      "The code can only reach those names as text. A string. Material dot set float, "
      "open quote, glow active, close quote. That quoted word is the whole link.",
      "B01_StringReach",
      "A single ink thread draws from a page on the left across to one asset block on the "
      "right, ending in a small terracotta dot. One label beside the thread: 'string'.",
      [{"at": 0.2, "event": "page lifts forward"},
       {"at": 0.55, "event": "thread draws across, lands before the midpoint"},
       {"at": 0.85, "event": "terracotta end dot, label"}]),

 beat("B02", EXEC,
      "Get that word wrong and nothing stops you. The compiler lets it through. "
      "The console stays quiet. The game runs. The glow simply never happens.",
      "B02_SilentPass",
      "The thread now ends in empty space. A crate rides between two open gates labelled "
      "'compiler' and 'console'; both stay open; an effect lamp at the end stays dark grey.",
      [{"at": 0.15, "event": "two gates draw, both open"},
       {"at": 0.5, "event": "crate rides through, fully opaque, lands before the midpoint"},
       {"at": 0.85, "event": "lamp stays dark; a small ring grows and fades"}]),

 beat("B03", EXEC,
      "Not everything is silent. Unity does warn about a wrong animator parameter, once "
      "that line runs. About a wrong shader property it says nothing at all.",
      "B03_WhatWarns",
      "Two terracotta runners approach the gates. The upper one is stopped by a bar that drops "
      "across it; the lower one passes straight through both and reaches the dark lamp. "
      "Labels beside: 'warns', 'silent'.",
      [{"at": 0.15, "event": "two runners line up"},
       {"at": 0.45, "event": "bar drops on the upper runner, lands before the midpoint"},
       {"at": 0.8, "event": "the lower runner reaches the lamp; labels"}]),

 beat("B04", EXEC,
      "And this is getting more common. An assistant that reads only your C sharp files "
      "cannot know the name inside the shader graph, so the name it writes is a guess.",
      "B04_HalfRead",
      "A scan line sweeps only the left half of the crate and stops at the divider; the "
      "right half sits behind a dim scrim. One ink label: 'guess'.",
      [{"at": 0.2, "event": "scrim covers the right half"},
       {"at": 0.45, "event": "scan line sweeps the left half only, finishes before the midpoint"},
       {"at": 0.8, "event": "'guess' label lands beside the thread"}]),

 beat("B05", EXEC,
      "So here is what I am building. One command, run before the game: every name your "
      "code asks for that your project does not have, in one list. That is the whole product.",
      "B05_OneList",
      "The crate on the left, and beside it a paper slip whose rows fill with ink ticks and "
      "two ink crosses — the report. Labels: 'one list', 'proposed'.",
      [{"at": 0.2, "event": "slip draws in beside the crate, labels"},
       {"at": 0.5, "event": "tick rows and two crosses land, before the midpoint"},
       {"at": 0.85, "event": "a bracket counts the two crosses"}]),

 # ══════════════════════ 2. INTRODUCTION — what already exists ═══════════════
 beat("B06", INTRO,
      "What exists already. Unity has solved this once: its Input System can generate a "
      "C sharp class from your input actions, so those names become code instead of strings. "
      "One name kind out of four.",
      "B06_TypeSafe",
      "Four dark name blocks in a row. The leftmost sits ON a white page — the generated class — "
      "while the other three sit apart on the crate side. Labels: the act title 'introduction' "
      "top left, 'input actions' under the fused one, 'the other three' under the rest.",
      [{"at": 0.15, "event": "act title and the four blocks land"},
       {"at": 0.5, "event": "the left block settles onto the page, before the midpoint"},
       {"at": 0.85, "event": "a terracotta dot marks the solved one"}]),

 beat("B07", INTRO,
      "For the other three, the analyzers look at this exact line. Rider calls the string "
      "lookup inefficient. Microsoft's Unity rules say cache the ID. Both ask whether the "
      "string is fast, not whether it is right.",
      "B07_FastNotRight",
      "Two threads leave the same page: the upper one ends at a small kraft tag — the cached ID — "
      "the lower one ends in empty space with a terracotta dot. Labels: 'faster', 'still unchecked'.",
      [{"at": 0.2, "event": "upper thread draws to the tag, label"},
       {"at": 0.5, "event": "lower thread ends in empty space, label, before the midpoint"},
       {"at": 0.85, "event": "a dim ring grows where the lower thread ends"}]),

 beat("B08", INTRO,
      "Unity's own Project Auditor, built in since six point four, reports twenty five "
      "categories of issue. Not one of them compares a name in the code with a name in the assets.",
      "B08_Auditor",
      "A five by five grid of dim squares with clear gaps — the twenty five categories — and one "
      "square in it left as an empty outline. Labels: 'twenty five', 'not this one'.",
      [{"at": 0.2, "event": "grid fills in, label"},
       {"at": 0.55, "event": "one square stays an outline, label lands, before the midpoint"},
       {"at": 0.85, "event": "a ring grows around the empty square"}]),

 beat("B09", INTRO,
      "I tried the other direction too: an AI tool writing straight into the editor. I asked "
      "it to lay out a scene. It put things in the wrong places. Not a warning. Work to undo.",
      "B09_WritesIn",
      "A mechanical arm reaches down over the crate and drops blocks at visibly wrong angles. "
      "Labels beside: 'writes', and a corner stamp 'spring 2026'.",
      [{"at": 0.2, "event": "arm reaches down, fully opaque"},
       {"at": 0.5, "event": "blocks drop crooked, settle before the midpoint"},
       {"at": 0.85, "event": "a third crooked block lands"}]),

 beat("B10", INTRO,
      "So the pieces exist. The check itself is an API call you make yourself, one object at a "
      "time. What I could not find is anything that reads a whole project and lists every name "
      "that does not resolve.",
      "B10_Gap",
      "The whole crate, both halves, under one wide ghost-outlined sweep band that nothing fills. "
      "Labels: 'whole project', 'proposed'.",
      [{"at": 0.2, "event": "crate and the outlined band draw, labels"},
       {"at": 0.5, "event": "band completes across both halves, before the midpoint"},
       {"at": 0.85, "event": "a terracotta dot lands at the far edge of the band"}]),

 # ══════════════════════ 3. METHODS — how, data, steps, resources ════════════
 beat("B11", METHOD,
      "So, how. Step one: read the assets that define names. Shader graphs, animator "
      "controllers, the tag manager, the input actions file. Write down every name that "
      "really exists.",
      "B11_Index",
      "A paper slip draws itself beside the asset half and fills with ink tick rows, one per "
      "asset block. Labels: the act title 'methods' top left, 'index', 'proposed'.",
      [{"at": 0.15, "event": "act title, slip draws in beside the asset half"},
       {"at": 0.5, "event": "tick rows fill, complete before the midpoint"},
       {"at": 0.85, "event": "'proposed' stamp lands"}]),

 beat("B12", METHOD,
      "Step two: find every quoted name in the C sharp and compare it against that list. "
      "Step three: print what is missing, with the file and the line. It never writes to "
      "your project.",
      "B12_Compare",
      "The thread from B01 re-routes from the page into the slip; one row turns to an ink cross. "
      "A large ink-outlined padlock draws over the crate. Labels beside: 'marked', 'read only'.",
      [{"at": 0.2, "event": "thread re-routes into the slip"},
       {"at": 0.45, "event": "one row turns to a cross, before the midpoint"},
       {"at": 0.8, "event": "padlock draws over the crate; labels land"}]),

 beat("B13", METHOD,
      "Version one reads only strings written out in full. A name assembled at runtime is "
      "marked cannot determine, and counted. I would rather be quiet than wrong.",
      "B13_Scope",
      "A page with two rows: the upper one a solid bar with a tick beside it, the lower one three "
      "short bars with gaps and a hollow ring beside it. Labels: 'written out', 'cannot tell'.",
      [{"at": 0.2, "event": "page and both rows draw, labels"},
       {"at": 0.5, "event": "the tick lands on the upper row, before the midpoint"},
       {"at": 0.85, "event": "a hollow ring lands beside the lower row"}]),

 beat("B14", METHOD,
      "What this needs: Python, the project's own files, and my laptop. No API key. No token "
      "credits. No cloud compute. No account. The data is the project you point it at.",
      "B14_Needs",
      "Two trays. The left one is solid and holds a page, an asset block and the glow from my own "
      "game. The right one is an empty outline holding nothing. Labels: 'have', 'not needed'.",
      [{"at": 0.15, "event": "the full tray and the outlined tray land, labels"},
       {"at": 0.5, "event": "the objects settle into the left tray, before the midpoint"},
       {"at": 0.85, "event": "the glow ring draws on the left tray's block"}]),

 beat("B15", METHOD,
      "I build it one name kind at a time. Shader properties first, because that is the silent "
      "one. Then animator parameters, tags, and input actions.",
      "B15_Order",
      "Four blocks on a rail: the first solid and dark, the other three ghost outlines. Labels: "
      "'first', 'then three'.",
      [{"at": 0.2, "event": "rail and the first solid block land, labels"},
       {"at": 0.55, "event": "three ghost outlines draw along the rail, before the midpoint"},
       {"at": 0.85, "event": "a terracotta dot lands above the first block"}]),

 # ══════════════════════ 4. EVALUATION — how I will know ═════════════════════
 beat("B16", EVAL,
      "How will I know it worked. A test project with three wrong names planted in it, and my "
      "own Unity game, the one I shipped last spring, as the second case.",
      "B16_Fixture",
      "A small crate beside the slip; three rows on the slip turn to ink crosses while the rest "
      "stay ticks, and a bracket counts the three. Labels: the act title 'evaluation' top left, "
      "'test project', 'proposed'.",
      [{"at": 0.2, "event": "act title, small crate lands with shadow"},
       {"at": 0.5, "event": "three crosses land, before the midpoint"},
       {"at": 0.85, "event": "bracket and the count land"}]),

 beat("B17", EVAL,
      "The number that decides it is false alarms. A string is not always written out in full. "
      "Flag good code once, and nobody runs the tool twice.",
      "B17_FalseAlarm",
      "A grey bar stack grows on a plinth beside a correct tick row that flips to a cross; "
      "gaps between every segment. Labels beside: 'false alarms', 'proposed'.",
      [{"at": 0.2, "event": "plinth and axis draw"},
       {"at": 0.45, "event": "bar stack grows, settles before the midpoint"},
       {"at": 0.8, "event": "a good row flips to a cross; labels land"}]),

 beat("B18", EVAL,
      "I report three numbers: how many planted names it caught, how many good lines it wrongly "
      "flagged, and how many it could not determine. All three, not just the flattering one.",
      "B18_TwoNumbers",
      "A second and third grey bar stack grow beside the first, with gaps: 'caught' and "
      "'cannot tell'. One terracotta dot tops the middle stack. Label beside: 'proposed'.",
      [{"at": 0.2, "event": "second stack grows"},
       {"at": 0.45, "event": "third stack grows, settles before the midpoint"},
       {"at": 0.8, "event": "terracotta dot lands on the middle stack; labels"}]),

 beat("B19", EVAL,
      "It has worked when it names all three planted names and raises nothing on the untouched "
      "code. One false alarm and version one has failed. That is the line.",
      "B19_PassMark",
      "Two columns on one plinth: the left one grown to a drawn ink rule above it, the right one "
      "flat at zero with a terracotta dot on the baseline. Labels: 'all three', 'none'.",
      [{"at": 0.2, "event": "plinth, axis and the pass rule draw, labels"},
       {"at": 0.5, "event": "the left column grows to the rule, before the midpoint"},
       {"at": 0.85, "event": "a terracotta dot lands at zero on the right"}]),
]

# ------------------------------------------------------------------- bookends

OPEN = [
 remotion("BIDEA", "the question",
    f"Hi. These are {AUTHOR}'s words, read by a synthetic voice. I build games in Unity. "
    "The checks I found ask whether a line of code is fast. The one I am building asks "
    "whether the name in it exists.",
    "BrutalistHesitantWriter",
    {"text": "The checks I found ask whether this code\nis fast",
     "triggerWords": "is fast", "replacementWords": "is right",
     "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1,
     "mistakeRate": 2, "jitter": 20, "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types 'The checks I found ask whether this code is fast'"},
     {"at": 0.65, "event": "backspaces 'is fast' -> 'is right' on the spoken correction"}],
    lead_silence_s=0.8,
    motion_claim="The writer types what today's checks ask and corrects it to what this project asks.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),

 remotion("BDEFS", "terms",
    "Three terms. A shader property: a name stored in a Unity asset, not in the code. "
    "A string reference: code reaching that name as quoted text. And a silent failure: "
    "wrong code that compiles, runs, and does nothing.",
    "ClaudeDefinitions",
    {"title": "Terms In This Film",
     "terms": [{"term": "shader prop", "meaning": "a name stored in a Unity asset, not in the code"},
               {"term": "string ref", "meaning": "code reaching that name as quoted text"},
               {"term": "silent fail", "meaning": "wrong code that compiles, runs, and does nothing"}],
     "folderLabel": HANDLE},
    [{"at": 0.15, "event": "'shader prop' lands"},
     {"at": 0.5, "event": "'string ref' lands"},
     {"at": 0.8, "event": "'silent fail' lands"}], gate="CARD",
    qc={"sparse_by_design": True, "sparse_reason": "TERMS card: three prerequisites, one line each."}),
]

YT_PROMPT = ("Pick a project you know well and ask your AI assistant for code that uses a name "
             "stored outside the source files: an animator parameter, a shader property, a config "
             "key. Then open the file that actually defines that name and compare. Tell me whether "
             "the assistant read it or guessed it.")

YOURTURN = remotion("BHTF", "your turn",
    "Your turn. Paste this into Claude. " + YT_PROMPT + " Then check two things yourself. Did it "
    "say out loud that it was unsure? And would anything in your build have caught it if it was wrong?",
    "ClaudeComposerAsk",
    {"greeting": "Your turn.", "topic": "CLAUDE · YOUR TURN",
     "segment": "Find One Guessed Name", "command": YT_PROMPT,
     "runningText": "paste this into Claude…",
     "output": ["Check: did it say it was unsure?",
                "Check: would anything in your build have caught it?"],
     "folderLabel": HANDLE, "modelLabel": "Opus 5", "effortLabel": "High"},
    [{"at": 0.0, "event": "Composer opens — 'Your turn.'"},
     {"at": 0.1, "event": "the prompt types in full"},
     {"at": 0.85, "event": "two check lines land"}])

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal "
                 "labels, with the voice carrying the explanation. The negative space is the style, "
                 "so only underfill and clustered are waived; edge-bleed, empty-frame and contrast "
                 "still apply.")
for b in B:
    if b["lane"] == "manim":
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}

B = OPEN + B + [YOURTURN]

B.append({"beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW",
          "narration_text": f"{TITLE}. Read by a synthetic voice, for {AUTHOR.split()[0]}.",
          "estimated_duration_s": 4.0, "voice": "af_bella", "engine": "kokoro",
          "shot": {"type": "REMOTION", "source": "own",
                   "show": [{"at": 0.0, "event": "title restates; author handle"}],
                   "remotion": {"pattern": "ClaudeTitleOutro",
                                "props": {"title": TITLE, "slug": SLUG,
                                          "handle": HANDLE, "subline": ""}}},
          "kind": "outro_voice", "tail_silence_s": 1.0})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "UNITY · VERIFICATION",
    "skill": "show-tell", "style_preset": "show-tell",
    "channel": "weiting-wang", "channel_title": HANDLE,
    "persona": ("Synthetic Kokoro af_bella voice reading Weiting Wang's own words "
                "(disclosed in the opening beat, on the end card, and in SOURCES.md)"),
    "voice": "af_bella", "voice_kokoro": "af_bella", "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "plain",
    "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none", "greeting_language": "English (Hi)",
    "structure": ["executive summary (B00-B05)", "introduction (B06-B10)",
                  "methods (B11-B15)", "evaluation (B16-B19)"],
    "bookend_exempt": ["cold-open", "bvdt"],
    "bookend_exempt_reason": (
        "show-tell style: opens on the hesitant writer plus the terms card, no verdict card; "
        "Your Turn is the Claude.ai composer. The spoken outro stays, but names the author "
        "instead of the instructor: the INFO 7375 assignment requires narrating as oneself and "
        "forbids the instructor's name, persona or credit line, so the outro handle and "
        "narration are the author's. OUTRO-LOCK is expected to flag this; see FRICTIONAL.md."),
    "audience": "Unity gameplay programmers who write code with an AI assistant, and reviewers "
                "looking at tools and AI-engineering work",
    "honesty_note": (
        "Nothing in this film exists yet except the Unity game referenced in B09 and B16. "
        "Every drawing of the proposed tool is labelled 'proposed' on screen. Past tense appears "
        "only in B09 and B16, both of which describe work actually done in spring 2026. "
        "Act 2 describes other people's tools; every claim there is quoted from that tool's own "
        "documentation and listed in FACTCHECK.md with the page it came from. "
        "CORRECTED 2026-10-13: an earlier cut claimed the console says nothing about a wrong "
        "animator parameter. Unity does warn about that one. The claim now names the shader "
        "property, which Unity's own documentation says has no effect and no message, and B03 "
        "states the difference out loud. See FACTCHECK.md rows 3 and 4."),
    "source_doc": "PROJECT-BRIEF.md (this repository, the film's appendix); "
                  "brutalist.art skills/make/show-tell/SKILL.md",
    "playlist": "INFO 7375 Fall 2026", "chapter_number": 0,
    "tags": ["Unity", "C#", "verification", "source grounding", "evaluation",
             "prompt contracts", "INFO 7375"]},
    "beats": B}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(B), "beats; est", round(sum(b["estimated_duration_s"] for b in B)), "s")
