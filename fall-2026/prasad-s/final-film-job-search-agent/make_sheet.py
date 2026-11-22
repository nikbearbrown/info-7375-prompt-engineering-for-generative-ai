#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for job-search-agent-film (WorthLoop, the final project film).

It builds the 17 narration beats, B1-B17, from NARRATION.md in this folder, and gives each
one the scene fields the toolkit needs to render it as a drawn Manim beat (act, lane,
proof_gate, shot, qc), modeled on the pitch film's make_sheet.py (final-project-film/). What
each beat shows follows SHOTLIST.md; the scenes are in scenes.py, one class per beat, named
<beat id>_<Name>. Voice: Kokoro am_onyx (metadata.voice_kokoro); engine "kokoro" on every
beat.

Each narration_text is exactly that beat's line in NARRATION.md, without the "B# — " label.
The opening card and the "On screen:" line are on-screen text, not narration: neither
becomes a beat or part of one. The opening card will be B1's picture.

Refuses to write if any narration_text contains "Shinde", or if NARRATION.md does not hold
exactly 17 beats, B1 to B17, in order.

Re-run after audio generation: it keeps each beat's measured actual_duration_s and
audio_file, and B1's tts_phoneme_overrides (written by the Assignment 1 override), but only
while that beat's narration_text is unchanged. A beat whose text changed loses them and
needs new audio. It never writes or changes a narration or audio field itself.

Do NOT re-run it after `art final`: it rewrites the sheet and drops the build stamps.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "job-search-agent-film"
TITLE = "WorthLoop"
VOICE = "am_onyx"
N_BEATS = 17
LABEL = re.compile(r"^(B\d+) — (.+)$")
KEEP = ("actual_duration_s", "audio_file", "tts_phoneme_overrides")

old = {}
if (HERE / "beat_sheet.json").exists() and (HERE / "beat_sheet.json").stat().st_size:
    old = {b["beat_id"]: b for b in json.loads((HERE / "beat_sheet.json").read_text(encoding="utf-8"))["beats"]}


def carry(b):
    """Keep measured audio from a previous run, only if the narration is unchanged."""
    o = old.get(b["beat_id"], {})
    if o.get("narration_text") == b["narration_text"]:
        for k in KEEP:
            if k in o:
                b[k] = o[k]
    elif any(k in o for k in KEEP):
        print(f"{b['beat_id']}: narration changed; its old audio is not carried over, so it needs new audio")
    return b


def words(text):
    return sum(1 for t in text.split() if re.search(r"[A-Za-z0-9]", t))


def est(text):
    return round(words(text) / 2.5, 1)


def refuse(msg):
    sys.exit(f"make_sheet.py: REFUSED, nothing written: {msg}")


beats = []
for line in (HERE / "NARRATION.md").read_text(encoding="utf-8").splitlines():
    m = LABEL.match(line)
    if m:
        bid, text = m.group(1), m.group(2).strip()
        beats.append(carry({"beat_id": bid, "narration_text": text,
                            "estimated_duration_s": est(text), "engine": "kokoro"}))

ids = [b["beat_id"] for b in beats]
if ids != [f"B{i}" for i in range(1, N_BEATS + 1)]:
    refuse(f"expected exactly {N_BEATS} beats, B1 to B{N_BEATS} in order; found {len(ids)}: {ids}")
for b in beats:
    if "shinde" in b["narration_text"].lower():
        refuse(f'{b["beat_id"]}: narration_text contains "Shinde"')

# Scene fields. One drawn Manim scene per beat. The class name starts with the beat id:
# run.sh slots each clip by the text before the first underscore, and the pacing helpers in
# scenes.py find the beat's narration and measured audio the same way. "label" is the
# provenance label SHOTLIST.md gives the beat, shown top left for the whole beat ("" = none).
# "show" lists what appears, each with the spoken phrase it waits for (None = no phrase).
SPARSE = ("show-tell style: one drawn picture per beat on a cream stage, with labels; the voice "
          "carries the explanation. Only underfill and clustered are waived; edge-bleed, "
          "empty-frame and contrast still apply.")
SCENES = {
    "B1": ("B1_OpeningCard", "",
           "Opening card for the whole beat: 'WorthLoop · Prasad Shinde' / 'Narration: synthetic "
           "voice (Kokoro am_onyx). Words: Prasad Shinde.'",
           [(None, "both card lines, from the first frame"), (None, "an ink rule and a dot draw in")]),
    "B2": ("B2_Packet", "ILLUSTRATION",
           "A posting becomes a packet (posting, answers, why it fits); an Approve button; a "
           "'Never submits' stamp.",
           [(None, "a posting on a dark plinth"), ("drafts a packet", "a shallow packet tray"),
            ("the posting", "the posting moves into the tray"), ("the answers", "an answers page drops in"),
            ("why it fits", "a why-it-fits page drops in"), ("The person approves", "Approve button, cursor"),
            ("WorthLoop never", "'Never submits' stamp")]),
    "B3": ("B3_Flood", "",
           "'≈254 applicants per job ad', source line 'Greenhouse, via Fortune, Jul 2026'; "
           "applications pile up while the number counts up to 254.",
           [(None, "a job ad"), ("hiring is flooded", "an application pile starts"),
            ("In July 2026", "source line"), ("about 254", "the number counts up to ≈254 as pages pile up"),
            ("employers drown", "more applications pile on")]),
    "B4": ("B4_ApplyTools", "",
           "Group 1, 'Tools that apply for you': wrong info, wrong fields; 'snake oil', source "
           "line 'Washington Post, Mar 2026'.",
           [(None, "group header"), ("Employers say", "an application form"),
            ("wrong information", "values drop into the fields; 'wrong info'"),
            ("wrong fields", "a cross beside each field; 'wrong fields'"),
            ("One company", "'snake oil' and its source line")]),
    "B5": ("B5_Funnel", "",
           "Group 2, 'Open-source agents': the career-ops funnel 740 → 68 → 12 → 1, each bar "
           "shrinking as its number is spoken; source line 'career-ops README'. Bar widths "
           "are not to scale; each bar is labeled with its number.",
           [(None, "group header"), ("One checked", "740 listings bar; source line"), ("68", "bar shrinks: 68 applications"),
            ("12 interviews", "bar shrinks: 12 interviews"), ("one offer", "bar shrinks: 1 offer")]),
    "B6": ("B6_PaymentChecks", "",
           "Group 3, 'Approval checks from AI payments': AP2's rule, quoted as AP2's; AsAsked and "
           "Mandate Shield named; 'Oct: payments pitch → job applications'.",
           [(None, "group header"), ("One standard", "AP2's rule, quoted, with its source line"),
            ("In October", "'Oct: payments pitch'"), ("others built", "AsAsked and Mandate Shield"),
            ("so I carried", "arrow to 'job applications'")]),
    "B7": ("B7_NotFound", "",
           "The two 'not found' lines; then 'My last test: missed the one worth-it posting — read "
           "'prefers 5+ years' as a rule', the posting sliding past the filter as it's spoken; "
           "source line 'JS3 held-out test · MEASURE.md'.",
           [("a test locked", "Not found: a test locked before tuning"),
            ("or approval tied", "Not found: approval tied to the exact packet"),
            ("My last test", "track, filter, the worth-it posting, first test line, source line"),
            ("missed the one", "the posting slides past the filter"), ("reading", "second test line")]),
    "B8": ("B8_Alex", "FICTIONAL",
           "Alex Rivera card, labeled FICTIONAL; the four boards: Stripe, Robinhood, Duolingo "
           "(Greenhouse), Notion (Ashby).",
           [("Alex Rivera", "Alex Rivera card"), ("It reads", "the four boards under Greenhouse and Ashby")]),
    "B9": ("B9_Evidence", "CONSTRUCTED",
           "An evidence card laid out by condition: Title (C1), Place (C2), then C4 with Level and "
           "Years beneath it. Its lines are revealed in spoken order: Title ✓, Level ✓, Place ✓, "
           "Years ✓. Then '→ packet (planned)'.",
           [("Here is one", "the evidence card"), ("title fits", "Title (C1) ✓"), ("level fits", "C4, Level ✓"),
            ("place fits", "Place (C2) ✓"), ("years fit", "Years ✓"), ("It will become", "→ packet (planned)"),
            ("the posting, draft", "a page drops into the packet"), ("draft answers", "a page drops in"),
            ("and the evidence", "a page drops in")]),
    "B10": ("B10_Plug", "",
            "Claude → plug (MCP) → scorer, the plug connecting as it's named; 'rules in code'; "
            "'10 requests' and '60 s' as two limit chips.",
            [(None, "Claude"), ("the scorer", "the scorer and its socket"),
             ("through a standard plug", "the plug (MCP) appears and connects; a light turns on"),
             ("Rules in the code", "rules in code"), ("ten requests", "chip: 10 requests"),
             ("sixty seconds", "chip: 60 s")]),
    "B11": ("B11_Fingerprint", "PLANNED",
            "Packet → fingerprint. One word in the packet is highlighted and changed, and the "
            "fingerprint scrambles into a different one. The two fingerprints are the real SHA-256 "
            "of the two example packet texts, trimmed to 12 characters (computed in scenes.py). "
            "'Approve = plain code; the AI can't press it.'",
            [(None, "Approve button"), ("plain code", "'Approve = plain code; the AI can't press it.'"),
             ("The approval will be tied", "the example packet"),
             ("fingerprint of the packet", "→ fingerprint"), ("change one word", "one word highlighted, then changed"),
             ("and the fingerprint changes", "the fingerprint scrambles into the new one")]),
    "B12": ("B12_Laptop", "",
            "'Laptop · free tools · no paid credits · Claude via university'; Built ✓ watcher, "
            "filter, scorer; Next: packet, gate.",
            [("my laptop", "laptop; 'Laptop'"), ("free tools", "'free tools'"), ("no paid credits", "'no paid credits'"),
             ("Claude comes", "'Claude via university'"), ("Built so far", "Built"), ("the watcher", "✓ watcher"),
             ("the filter", "✓ filter"), ("the scorer", "✓ scorer"), ("Next", "Next"), ("the packet", "packet"),
             ("the gate", "gate")]),
    "B13": ("B13_Locked", "",
            "A locked box: '20 postings, sealed Nov 15'; '≈1 in 30 worth it'; 'likely 0 or 1; "
            "exact count reported'.",
            [(None, "the box, open lock, '20 postings, sealed Nov 15'"), ("locked", "the lock closes; tape seals it"),
             ("about one in thirty", "'≈1 in 30 worth it'"), ("none, or one", "'likely 0 or 1; exact count reported'")]),
    "B14": ("B14_Checks", "",
            "The five pass checks, ticking in as the narration lists them; closing line 'any one "
            "fails → it didn't work'.",
            [("misses none", "✓ misses none"), ("keeps at most two", "✓ keeps at most two of the rest"),
             ("every claim", "✓ every claim matches Alex's profile"), ("every fingerprint", "✓ every fingerprint matches"),
             ("all five traps", "✓ all five traps handled"), ("One failure", "any one fails → it didn't work")]),
    "B15": ("B15_Traps", "",
            "All five traps with their right answers, as in OUTLINE.md Part 4; the two spoken ones "
            "(Staff, 'prefers 5+ years') highlighted, the other three dimmed but readable.",
            [(None, "the five traps and their answers"), ("Two:", "the three unspoken traps dim"),
             ("a Staff title", "the Staff trap is marked"), ('And "prefers', "the 'prefers 5+ years' trap is marked")]),
    "B16": ("B16_Controlled", "PLANNED",
            "Five steps light up in order: predict → change packet → caught → refused → re-approve; "
            "then 'Stranger run: clean machine'.",
            [(None, "five unlit steps"), ("I write the expected", "predict"), ("Then I change", "change packet"),
             ("A separate check", "caught"), ("refuse it", "refused"), ("make me approve", "re-approve"),
             ("Last, someone", "laptop; 'Stranger run: clean machine'")]),
    "B17": ("B17_End", "",
            "End card: 'WorthLoop · INFO 7375 Final Project Film · Nov 2026', fading slowly to black "
            "as the line ends.",
            [(None, "the end card, from the first frame"), (None, "an ink rule and a dot draw in"),
             (None, "a slow fade to black over about the last 1.6 s")]),
}
if sorted(SCENES) != sorted(ids):
    refuse(f"SCENES covers {sorted(SCENES)}, but the beats are {ids}")
for b in beats:
    cls, label, intent, show = SCENES[b["beat_id"]]
    b.update({
        "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
        "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": intent,
                 "show": [{"cue": cue, "event": event} for cue, event in show],
                 "manim": {"class": cls, "tag": label}, "motion_claim": intent},
        "qc": {"sparse_by_design": True, "sparse_reason": SPARSE}})

sheet = {"metadata": {
    "slug": SLUG,
    "title": TITLE,
    "topic": "WORTHLOOP · FINAL PROJECT FILM",
    "skill": "show-tell",
    "style_preset": "show-tell",
    "channel": "worthloop",
    "voice_kokoro": VOICE,
    "engine": "kokoro",
    "clock": "narration",
    "fps": 24,
    "aspect_ratio": "16:9",
    "width": 3840,
    "height": 2160,
    "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Course final project film, not a channel episode: it opens on its own "
                              "opening card (B1) instead of a composer cold open, has no verdict card "
                              "and no Your Turn composer, and carries no channel handle or persona. It "
                              "ends on its own end card (B17), not a BOUT outro, which bookend_check.py "
                              "cannot exempt; that script is not called by art run or art final."),
    "audience": "INFO 7375 reviewers of the final project",
    "source_doc": "NARRATION.md (this folder)",
}, "beats": beats}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
total_words = sum(words(b["narration_text"]) for b in beats)
measured = [b["actual_duration_s"] for b in beats if "actual_duration_s" in b]
print(f"{len(beats)} beats; {total_words} words; est {round(sum(b['estimated_duration_s'] for b in beats))} s "
      f"at 2.5 words/s; measured audio kept for {len(measured)} beat(s)")
