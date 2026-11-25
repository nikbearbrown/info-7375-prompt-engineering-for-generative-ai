#!/usr/bin/env python3
"""
make_captions.py — burned-in captions for the SponsorScout pitch film (copied from my Week 01 film, unchanged logic).

Source of truth is mp3/words.json, written by runtime/scripts/align.py: the KNOWN
narration text, word by word, placed on the moment each word is spoken
(faster-whisper supplies timing only; the text is never transcribed blind).
So the captions say exactly what the narrator says, when it is said.

Beat offsets come from the conformed clips the compiler actually concatenated
(clips/<BID>.mp4, measured with ffprobe), not from estimates.

Writes, in the reel folder:
    captions.srt   sidecar (toggle-able in any player)
    captions.ass   styled for burn-in: Lato, cream on an ink box, bottom centre,
                   box bottom at y=1022 on a 1920x1080 frame (inside SAFE.b=1026);
                   scenes.py draws nothing below y=-2.5 units (~877 px), so captions never cover a drawing

Usage (run from the reel folder, AFTER compile):
    python3 tools/make_captions.py
"""
import json, re, subprocess
from pathlib import Path

REEL = Path(__file__).resolve().parent.parent
MAX_WORDS, MAX_CHARS = 7, 40

def clip_dur(bid):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(REEL / "clips" / f"{bid}.mp4")],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

def ts_srt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def ts_ass(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    W = json.loads((REEL / "mp3" / "words.json").read_text(encoding="utf-8"))
    fps = W["fps"]
    cues, offset = [], 0.0
    for beat in sheet["beats"]:
        bid = beat["beat_id"]; dur = clip_dur(bid)
        words = []
        for w in W["beats"][bid]:
            text = w["text"]
            if not re.search("[A-Za-z0-9]", text):      # a bare dash/punct token: glue to previous word
                if words: words[-1]["text"] += " " + text
                continue
            words.append({"text": text, "t0": w["startFrame"] / fps, "t1": w["endFrame"] / fps})
        chunk = []
        def flush():
            if chunk:
                cues.append({"t0": offset + chunk[0]["t0"], "t1": offset + chunk[-1]["t1"],
                             "text": " ".join(x["text"] for x in chunk), "beat_end": offset + dur})
                chunk.clear()
        for w in words:
            chunk.append(w)
            line = " ".join(x["text"] for x in chunk)
            if len(chunk) >= MAX_WORDS or len(line) >= MAX_CHARS or \
               (len(chunk) >= 3 and re.search("[.,:;?!]$", w["text"])):
                flush()
        flush()
        offset += dur
    # each cue holds until the next one starts (same beat), else a short tail
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["t0"] if i + 1 < len(cues) else c["beat_end"]
        end = min(nxt, c["t1"] + 0.45, c["beat_end"]) if nxt <= c["beat_end"] else min(c["t1"] + 0.45, c["beat_end"])
        c["t1"] = max(end, c["t0"] + 0.6)

    srt = "".join(f"{i}\n{ts_srt(c['t0'])} --> {ts_srt(c['t1'])}\n{c['text']}\n\n" for i, c in enumerate(cues, 1))
    (REEL / "captions.srt").write_text(srt, encoding="utf-8")

    # ASS colours are &HAABBGGRR. cream #FAF9F5 -> &H00F5F9FA ; ink #3D3929 at ~85% -> &H2629393D
    head = "\n".join([
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
        "MarginV, Encoding",
        "Style: Default,Lato,40,&H00F5F9FA,&H00F5F9FA,&H2629393D,&H00000000,0,0,0,0,100,100,0.3,0,3,14,0,2,360,360,72,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"])
    ev = "\n".join(f"Dialogue: 0,{ts_ass(c['t0'])},{ts_ass(c['t1'])},Default,,0,0,0,,{c['text']}" for c in cues)
    (REEL / "captions.ass").write_text(head + "\n" + ev + "\n", encoding="utf-8")
    longest = max(len(c["text"]) for c in cues)
    print(f"{len(cues)} cues over {offset:.2f}s  (longest cue {longest} chars)  -> captions.srt, captions.ass")

if __name__ == "__main__":
    main()
