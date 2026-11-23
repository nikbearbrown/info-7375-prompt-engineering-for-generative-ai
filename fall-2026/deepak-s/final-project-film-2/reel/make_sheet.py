#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for CueGate film 2 (the project film, show-tell, two voices).

Narration is read verbatim from NARRATION-FILM2.md (one row per beat); nothing is retyped here.
Each beat has one speaker: DEEPAK (Kokoro am_onyx) or SKEPTIC (Kokoro af_bella, a constructed voice).
The script beat ids (E1 ... V5b, OUT) are kept in each beat as "script_beat".

Run once before audio; never after `art final` (it would wipe the build stamps).
"""
import json
from pathlib import Path

from pad_audio import pads

HERE = Path(__file__).resolve().parent
NARRATION = HERE / "NARRATION-FILM2.md"
SLUG = "cuegate-film2"
TITLE = "CueGate"
HANDLE = "Deepak Kumaran T S"
VOICE = {"DEEPAK": "am_onyx", "SKEPTIC": "af_bella"}
SPARSE = ("show-tell: one drawn picture on a cream stage per beat, labels beside the objects, the voice "
          "carries the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and "
          "contrast still apply.")


def rows():
    out = {}
    for line in NARRATION.read_text().splitlines():
        if not line.startswith("| B"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            raise SystemExit(f"unexpected table row: {line[:80]}")
        bid, script, act, speaker, text = cells
        if bid == "Beat":
            continue
        if speaker not in VOICE:
            raise SystemExit(f"{bid}: unknown speaker {speaker}")
        if "{" in text or "}" in text:
            raise SystemExit(f"{bid}: unfilled field in narration")
        out[bid] = dict(script=script, act=int(act), speaker=speaker, text=text)
    return out


R = rows()


def est(bid):
    r = R[bid]
    speech = round(len(r["text"].split()) / 3.1, 2)
    lead, tail = pads(bid, r["speaker"], speech)
    return round(speech + lead + tail, 2)


def common(bid):
    r = R[bid]
    return {"beat_id": bid, "script_beat": r["script"], "act_number": r["act"], "speaker": r["speaker"],
            "narration_text": r["text"], "estimated_duration_s": est(bid),
            "voice": VOICE[r["speaker"]], "engine": "kokoro"}


def manim_beat(bid, cls, visual, show, constructed=False):
    b = common(bid)
    b.update({"act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
              "qc": {"sparse_by_design": True, "sparse_reason": SPARSE},
              "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": visual, "motion_claim": visual,
                       "show": show, "manim": {"class": cls}}})
    if constructed:
        b["shot"]["constructed_label"] = "CONSTRUCTED"
    return b


beats = []
b = common("B01")
b.update({"act": "cold open", "lane": "pantry", "proof_gate": "SHOW",
          "qc": {"sparse_by_design": True, "sparse_reason": "Real screenshot (evidence) on the cream stage with its date caption."},
          "shot": {"type": "STILL", "source": "own", "motion": "hold",
                   "visual_intent": "Deepak's real dated claude.ai screenshot (the pitch film's B00 image), with the act chip and speaker tag",
                   "still": "media/B01.png, built by make_e1.py from the pitch film's media/B00.png (sha256 1030efd2...) plus the act chip '1 · WHAT AND WHY' and the speaker tag 'DEEPAK'",
                   "exchange_date": "2026-10-14",
                   "show": [{"at": 0.0, "event": "Deepak's real Claude exchange, dated 2026-10-14"}]}})
beats.append(b)

beats += [
    manim_beat("B02", "B02_Shift", "The source line and the reply side by side; hedged opinion vs flat refusal",
               [{"at": 0.0, "event": "SKEPTIC label: a voice I wrote to ask the hard questions"},
                {"at": 0.05, "event": "asked / got back, side by side"},
                {"at": 0.3, "event": "highlights: hedged opinion, flat refusal"}]),
    manim_beat("B03", "B03_Clock", "A stopwatch over a subtitle bar; a file bounces back off a QC wall",
               [{"at": 0.05, "event": "film frame with subtitle bar; stopwatch"},
                {"at": 0.4, "event": "a subtitle file hits the QC wall and bounces back"},
                {"at": 0.8, "event": "a cursor on one line: by hand"}]),
    manim_beat("B04", "B04_Gate", "Turnstile gate: subtitle file and film in, clean file out, side door back to a person",
               [{"at": 0.05, "event": "subtitle file and film frame arrive"},
                {"at": 0.25, "event": "gate draws"},
                {"at": 0.55, "event": "clean file out, check"},
                {"at": 0.8, "event": "one line peels off to the side door: back to a person"}], constructed=True),
    manim_beat("B05", "B05_Button", "The gate, with a small AI button floating beside it",
               [{"at": 0.05, "event": "gate on stage, AI button floats in"}], constructed=True),
    manim_beat("B06", "B06_Card", "A blank report card: meaning changed __ of 100",
               [{"at": 0.05, "event": "report card drops in"},
                {"at": 0.45, "event": "empty box: meaning changed, __ of 100"},
                {"at": 0.8, "event": "the card goes up on a board: published"}], constructed=True),
    manim_beat("B07", "B07_Act2", "Act card 2: what already exists",
               [{"at": 0.0, "event": "act card 2 · WHAT ALREADY EXISTS"}]),
    manim_beat("B08", "B08_Tools", "Three plain cards, tool names in text, one cursor on one line each",
               [{"at": 0.05, "event": "Subtitle Edit and Editsub cards"},
                {"at": 0.45, "event": "EZTitles card"},
                {"at": 0.75, "event": "a cursor on one line in each"}]),
    manim_beat("B09", "B09_Papers", "Two paper cards: IWSLT 2019 and IWSLT 2020",
               [{"at": 0.05, "event": "2019 paper"},
                {"at": 0.45, "event": "2020 paper"},
                {"at": 0.85, "event": "a speech-rhythm strip beside it"}]),
    manim_beat("B10", "B10_Map", "A 2x2 map, one line at a time to whole file, meaning assumed to measured; three tools on the left; my reading",
               [{"at": 0.05, "event": "axes, labels, three tool dots on the left"}]),
    manim_beat("B11", "B11_Gap", "The same map; a hollow dot top right: CueGate (will)",
               [{"at": 0.05, "event": "the map from B10"},
                {"at": 0.6, "event": "hollow dot top right, CueGate (will)"}], constructed=True),
    manim_beat("B12", "B12_Act3", "Act card 3: how",
               [{"at": 0.0, "event": "act card 3 · HOW"}]),
    manim_beat("B13", "B13_Funnel", "A funnel: Tears of Steel subtitles (licence to confirm) and my own lines (synthetic) in; a vice squeezes a timeline; out: test set, originals known",
               [{"at": 0.05, "event": "funnel"},
                {"at": 0.15, "event": "Tears of Steel subtitles (licence to confirm)"},
                {"at": 0.45, "event": "my own lines (synthetic)"},
                {"at": 0.7, "event": "a vice squeezes the timeline"},
                {"at": 0.9, "event": "test set, originals known"}], constructed=True),
    manim_beat("B14", "B14_Pipeline", "The hero pipeline: Read, Frames, Check rules, Fix timing, Break lines, Ask local model (budget, must-keep), Check again, Ship; each box lights as it is named",
               [{"at": 0.05, "event": "eight boxes"},
                {"at": 0.15, "event": "each box lights up as it is named"}], constructed=True),
    manim_beat("B15", "B15_Fail", "Ask local model and Check again; Check again flashes",
               [{"at": 0.05, "event": "two boxes; the check fails"}], constructed=True),
    manim_beat("B16", "B16_Loop", "Loop arrow around Ask local model with three ticks, then a branch down to back to a person",
               [{"at": 0.1, "event": "loop arrow, three ticks"},
                {"at": 0.6, "event": "branch down to back to a person"}], constructed=True),
    manim_beat("B17", "B17_List", "A checklist with four rows: model access, compute, data, accounts",
               [{"at": 0.05, "event": "four empty rows"}]),
    manim_beat("B18", "B18_Have", "The same checklist, each row ticked or left open as RESOURCES.md says",
               [{"at": 0.1, "event": "model access: open (no API key needed; model not chosen)"},
                {"at": 0.3, "event": "compute: ticked"},
                {"at": 0.5, "event": "data: open (licence not confirmed)"},
                {"at": 0.7, "event": "accounts: ticked (GitHub; no other account needed)"}]),
    manim_beat("B19", "B19_Act4", "Act card 4: did it work?",
               [{"at": 0.0, "event": "act card 4 · DID IT WORK?"}]),
    manim_beat("B20", "B20_Board", "A scoreboard, four rows by two columns, every cell empty",
               [{"at": 0.05, "event": "column heads"},
                {"at": 0.2, "event": "rows land as each version is named"},
                {"at": 0.8, "event": "meaning column cells draw"}], constructed=True),
    manim_beat("B21", "B21_Verdict", "Two columns: WORKED IF and FAILED IF",
               [{"at": 0.05, "event": "WORKED IF: zero rule breaks, less meaning change than one model call"},
                {"at": 0.45, "event": "FAILED IF: same meaning change, most lines sent back"}]),
    manim_beat("B22", "B22_Lens", "A magnifying glass over the meaning check box",
               [{"at": 0.05, "event": "meaning check box; lens slides over it"}], constructed=True),
    manim_beat("B23", "B23_Tally", "A tally sheet with one empty total",
               [{"at": 0.05, "event": "tally sheet"},
                {"at": 0.55, "event": "empty total"},
                {"at": 0.8, "event": "it goes into the report"}], constructed=True),
    manim_beat("B24", "B24_Columns", "Two columns: EXISTS and WILL",
               [{"at": 0.05, "event": "EXISTS and WILL heads"}]),
    manim_beat("B25", "B25_Lists", "EXISTS lists the dated items; WILL lists the rest",
               [{"at": 0.1, "event": "EXISTS: the plan, the research, the Claude reply, each dated 14 Oct 2026"},
                {"at": 0.55, "event": "no CueGate code runs"},
                {"at": 0.7, "event": "WILL: ghost outlines of the parts"}]),
]

b = common("BOUT")
b.update({"act": "outro", "lane": "bookend", "proof_gate": "SHOW", "kind": "outro_voice", "tail_silence_s": 1.0,
          "shot": {"type": "REMOTION", "source": "own", "visual_intent": "Title card",
                   "show": [{"at": 0.0, "event": "title CueGate and the narrator's name"}],
                   "remotion": {"pattern": "ClaudeTitleOutro",
                                "props": {"title": TITLE, "slug": SLUG, "handle": HANDLE,
                                          "showMascot": False, "subline": ""}}}})
beats.append(b)

missing = set(R) - {x["beat_id"] for x in beats}
if missing:
    raise SystemExit(f"beats in NARRATION-FILM2.md with no picture: {sorted(missing)}")

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "CUEGATE · PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": SLUG, "channel_title": HANDLE,
    "persona": ("Deepak Kumaran T S (narration written by Deepak, voiced by Kokoro am_onyx); "
                "SKEPTIC: a constructed voice Deepak wrote to ask the four questions, voiced by Kokoro af_bella"),
    "voice": "am_onyx", "voice_kokoro": "am_onyx", "engine": "kokoro",
    "voices": VOICE,
    "clock": "narration", "palette": "claude", "register": "Plain",
    "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "srt sidecar written by make_captions.py, every cue tagged with its speaker",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("CueGate project film (Deepak, 2026-11-23): the film follows the professor's four-part "
                              "structure (executive summary, introduction, methods, evaluation). It opens on Deepak's "
                              "real claude.ai screenshot as a still, not the ClaudeComposerAsk mock; it has no verdict "
                              "card and no Your Turn. The spoken outro stays."),
    "audience": "INFO 7375 classmates and instructor; a subtitle QC lead",
    "source_doc": "inputs-film2/FILM2-SCRIPT.md and inputs-film2/RESOURCES.md (Deepak, 2026-11-23); evidence/day-one/FINDINGS.md (2026-10-14)",
    "audio_ready": True,
    "playlist": "INFO 7375 final project film", "chapter_number": 0,
    "tags": ["CueGate", "subtitles", "verification", "evaluation", "local models"]},
    "beats": beats}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(beats), "beats; est", round(sum(b["estimated_duration_s"] for b in beats), 1), "s")
