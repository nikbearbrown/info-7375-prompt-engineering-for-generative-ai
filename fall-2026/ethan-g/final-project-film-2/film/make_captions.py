"""Word-aligned subtitles (SRT + WebVTT) for the DataSentry project film, on the real clip offsets of the master.

Text is the KNOWN narration (align.py put each word on the moment it is spoken), never a blind transcript.
Spelled-out tokens written for the voice are shown the way a reader expects ("D B T" -> "dbt").
Asserts every narrated word is kept. Run after align.py; rerun whenever any beat is re-voiced.
"""
import json, subprocess, textwrap
from pathlib import Path

R = Path(__file__).resolve().parent
OUT = R.parent / "DataSentry_ProjectFilm_EthanGomes"
sheet = json.loads((R / "beat_sheet.json").read_text())
words = json.loads((R / "mp3/words.json").read_text())
fps = words["fps"]

# spoken spelling -> on-screen spelling (token runs, matched ignoring a trailing comma/period)
DISPLAY = [(["Data", "Sentry"], "DataSentry"), (["D", "B", "T"], "dbt"), (["G", "X", "Cloud"], "GX Cloud"), (["Expect", "A", "I"], "ExpectAI"),
           (["twenty", "twenty-six"], "2026"),
           (["Dee-queue"], "Deequ"), (["nineteen", "seventy-eight"], "1978")]


def merge(ws):
    out, i = [], 0
    while i < len(ws):
        for seq, shown in DISPLAY:
            run = ws[i:i + len(seq)]
            if len(run) == len(seq) and [w["text"].rstrip(".,") for w in run] == seq:
                tail = run[-1]["text"][len(seq[-1]):]          # keep the punctuation that followed
                out.append({"text": shown + tail, "startFrame": run[0]["startFrame"], "endFrame": run[-1]["endFrame"],
                            "spoken": [w["text"] for w in run]})
                i += len(seq)
                break
        else:
            out.append(dict(ws[i], spoken=[ws[i]["text"]]))
            i += 1
    return out


offsets, t = {}, 0.0
for b in sheet["beats"]:
    offsets[b["beat_id"]] = t
    t += float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                        "-of", "default=nw=1:nk=1", str(R / "clips" / f"{b['beat_id']}.mp4")]))


def wrap(text):
    """One line up to 42 characters; otherwise two balanced lines (no orphaned last word)."""
    if len(text) <= 42:
        return text
    return textwrap.fill(text, min(42, (len(text) + 1) // 2 + 5))


def ts(s, sep=","):
    ms = round(s * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02}{sep}{ms:03}"


cues, prev, spoken = [], 0.0, []
for b in sheet["beats"]:
    ws = merge(words["beats"][b["beat_id"]])
    lead = round(float(b.get("lead_silence_s", 0)) * fps)        # the voice starts after the padded lead
    if ws and ws[0]["startFrame"] < lead:
        ws[0]["startFrame"] = lead
    j = 0
    while j < len(ws):
        group = []
        while j < len(ws) and len(group) < 9:
            group.append(ws[j]); j += 1
            text = " ".join(w["text"] for w in group)
            if len(text) >= 58 or (len(group) >= 4 and group[-1]["text"].endswith((".", "?", "!", ";", ":"))):
                break
        start = max(prev, offsets[b["beat_id"]] + group[0]["startFrame"] / fps)
        end = max(start + 0.5, offsets[b["beat_id"]] + (group[-1]["endFrame"] + 4) / fps)   # hold ~1/6 s past the word
        nxt_start = offsets[b["beat_id"]] + ws[j]["startFrame"] / fps if j < len(ws) else None
        if nxt_start is not None:
            end = min(end, nxt_start)
        prev = end
        for w in group:
            spoken.extend(w["spoken"])
        cues.append((start, end, wrap(" ".join(w["text"] for w in group))))

assert " ".join(spoken).split() == " ".join(b["narration_text"] for b in sheet["beats"]).split(), "narration dropped"
srt = "\n\n".join(f"{i}\n{ts(a)} --> {ts(z)}\n{x}" for i, (a, z, x) in enumerate(cues, 1)) + "\n"
vtt = "WEBVTT\n\n" + "\n\n".join(f"{ts(a, '.')} --> {ts(z, '.')}\n{x}" for a, z, x in cues) + "\n"
OUT.with_suffix(".srt").write_text(srt)
OUT.with_suffix(".vtt").write_text(vtt)
(R / f"{sheet['metadata']['slug']}.srt").write_text(srt)   # beside the reel, where srt_check.py looks
print(len(cues), "cues; all narration kept; timeline", round(t, 3), "s; last cue ends", round(cues[-1][1], 2), "s")
