#!/usr/bin/env python3
"""make_srt.py -- captions from the beat sheet + Kokoro ground-truth timings.

Week 1 wrote one cue per beat (a whole paragraph on screen). Captions here are
kept short: each beat is split at sentence/clause breaks into cues of at most
two 42-character lines, timed by word position inside the beat, the same
interpolation scene.py uses for its visual cues.
"""
import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAP = 0.30
LINE, MAXW = 42, 14            # chars per line, words per cue
OUT = "BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm.srt"
sheet = json.loads((ROOT / "beat_sheet.json").read_text())
t = json.loads((ROOT / "mp3/timings.json").read_text())

# narration spells acronyms and numbers for the voice ("H one B", "thirty");
# captions show the written form from NARRATION.md. Longest forms first.
CAPTION_FORMS = [(re.compile(r"\b%s\b" % re.escape(v)), w) for v, w in [
    ("one thousand eight hundred thirty-two", "1,832"),
    ("two thousand nine", "2009"),
    ("Version one point one", "Version 1.1"),
    ("Version one", "Version 1"),
    ("Agents one to three", "Agents 1 to 3"),
    ("November seventeenth", "November 17"),
    ("shortlisted four", "shortlisted 4"),
    ("stayed at four", "stayed at 4"),
    ("reviewed thirty", "reviewed 30"),
    ("changing seven", "changing 7"),
    ("label sixty", "label 60"),
    ("twenty for", "20 for"),
    ("forty locked", "40 locked"),
    ("H one B Grader", "H1BGrader"),
    ("H one B one", "H-1B1"),
    ("H one B", "H-1B"),
    ("E three", "E-3"),
    ("U S C I S", "USCIS"),
    ("O P T", "OPT"),
    ("My Visa Jobs", "MyVisaJobs"),
]]


def caption_text(s):
    for pat, form in CAPTION_FORMS:
        s = pat.sub(form, s)
    return s


# captions must read exactly as the approved readable text in NARRATION.md
READABLE = dict(re.findall(r"\*\*(B\d\d)\*\* \([^)]*\)\. (.+)",
                           (ROOT / "NARRATION.md").read_text()))
for b in sheet["beats"]:
    got = caption_text(b["narration_text"])
    if got != READABLE[b["beat_id"]].strip():
        raise SystemExit("caption text for %s differs from NARRATION.md:\n  %s\n  %s"
                         % (b["beat_id"], got, READABLE[b["beat_id"]]))


def ts(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:
        sec, ms = sec + 1, 0
    return "%02d:%02d:%02d,%03d" % (h, m, int(sec), ms)


def chunks(text):
    """Sentence/clause pieces, re-split until each fits two caption lines."""
    out = []
    for piece in re.split(r"(?<=[.?!:,])\s+", text):
        words = piece.split()
        while words:
            take = len(words)
            while take > 1 and (take > MAXW or
                                len(textwrap.wrap(" ".join(words[:take]), LINE)) > 2):
                take -= 1
            out.append(words[:take])
            words = words[take:]
    # fold tiny fragments ("Same tool,") into the next cue when they fit
    merged = []
    for c in out:
        if merged and len(merged[-1]) <= 3 and \
                len(textwrap.wrap(" ".join(merged[-1] + c), LINE)) <= 2:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    return merged


cues, clock = [], 0.0
for b in sheet["beats"]:
    d = t[b["beat_id"]]
    pieces = chunks(caption_text(b["narration_text"]))
    total = sum(len(p) for p in pieces)
    done = 0
    for p in pieces:
        start = clock + d * done / total
        done += len(p)
        end = clock + d * done / total
        cues.append((start, end, "\n".join(textwrap.wrap(" ".join(p), LINE))))
    clock += d + GAP

body = "\n".join("%d\n%s --> %s\n%s\n" % (n, ts(a), ts(z), txt)
                 for n, (a, z, txt) in enumerate(cues, 1))
(ROOT / OUT).write_text(body)
print("wrote %s  (%d cues, ends %s)" % (OUT, len(cues), ts(clock - GAP)))
