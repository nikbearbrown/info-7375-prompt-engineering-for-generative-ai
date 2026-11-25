#!/usr/bin/env python3
"""make_captions.py: cuegate-film2.srt, the full narration with a speaker tag on every cue.

Every cue starts with its speaker, "DEEPAK:" or "SKEPTIC:", and keeps every narration word. Each cue
is at most two lines of 42 characters (Netflix's English line limit), tag included, split at sentence
and clause ends where possible. Cues are timed inside the voice's own span in each beat: after any
lead silence pad_audio.py added (pad_lead_s) and over the voice's measured length (speech_s), by each
cue's share of the characters, the same rule the scenes' say() uses. Beat offsets come from the
compiled clips (clips/<BID>.mp4) when they exist, so the captions follow the master's timeline. The
text is the source narration, not a transcription.

Usage: python3 make_captions.py            (run in the reel folder after `art final`)
"""
import json
import re
import subprocess
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_LINE, MAX_LINES = 42, 2


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", str(path)]))


def stamp(s):
    ms = round(s * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def fits(tag, text):
    return len(textwrap.wrap(f"{tag} {text}", MAX_LINE)) <= MAX_LINES


def chunks(tag, text):
    """Split narration into pieces that fit two 42-character lines with the tag in front."""
    parts = re.split(r"(?<=[.?!:;])\s+|(?<=,)\s+", text.strip())
    out, cur = [], ""
    for p in parts:
        trial = (cur + " " + p).strip()
        if fits(tag, trial):
            cur = trial
            continue
        if cur:
            out.append(cur)
        while not fits(tag, p):                                  # a single long clause: cut at word boundaries
            words, piece = p.split(), ""
            for i, w in enumerate(words):
                t2 = (piece + " " + w).strip()
                if not fits(tag, t2):
                    out.append(piece); p = " ".join(words[i:]); break
                piece = t2
        cur = p
    if cur:
        out.append(cur)
    return out


sheet = json.loads((HERE / "beat_sheet.json").read_text())
cues, t, emitted = [], 0.0, []
for b in sheet["beats"]:
    bid = b["beat_id"]
    tag = f"{b['speaker']}:"
    clip = HERE / "clips" / f"{bid}.mp4"
    window = dur(clip) if clip.exists() else float(b["actual_duration_s"])
    lead = float(b.get("pad_lead_s") or 0)
    speech = float(b.get("speech_s") or b["actual_duration_s"])
    speech = min(speech, window - lead)
    pieces = chunks(tag, b["narration_text"])
    total = sum(len(p) for p in pieces)
    at = t + lead
    for p in pieces:
        span = speech * len(p) / total
        cues.append((at, at + span - 0.04, "\n".join(textwrap.wrap(f"{tag} {p}", MAX_LINE))))
        emitted.append(p)
        at += span
    t += window

assert " ".join(emitted).split() == " ".join(b["narration_text"] for b in sheet["beats"]).split(), "a word was lost"
assert all(len(l) <= MAX_LINE for _, _, c in cues for l in c.split("\n")) and all(c.count("\n") < MAX_LINES for _, _, c in cues)
assert all(c.startswith(("DEEPAK:", "SKEPTIC:")) for _, _, c in cues), "a cue has no speaker tag"
srt = "\n\n".join(f"{i}\n{stamp(a)} --> {stamp(z)}\n{c}" for i, (a, z, c) in enumerate(cues, 1)) + "\n"
(HERE / f"{sheet['metadata']['slug']}.srt").write_text(srt)
print(len(cues), "cues; every narration word kept, every cue tagged; timeline", round(t, 3), "s")
