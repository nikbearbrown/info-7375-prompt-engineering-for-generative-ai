"""Assemble the film: one H.264 segment per beat (stills at their cue times, or an eased pan), the narration with
its pads, soft captions (mov_text) from the caption text, loudness normalized. 1080p, 30 fps.
Run with $TTS_PY (a Python with numpy) after tts.py and stage.py; needs ffmpeg on the PATH. Writes build/out/."""
import json, re, subprocess, wave
from pathlib import Path
import numpy as np

B = Path(__file__).resolve().parents[1]; FILM = B.parent
OUT, SEG = B / "out", B / "segments"
SEG.mkdir(exist_ok=True)
plan = json.loads((OUT / "plan.json").read_text())
beats = {b["id"]: b for b in json.load(open(FILM / "beats.json"))}
dur = json.loads((B / "audio" / "durations.json").read_text())
LEAD, FPS, SR = 0.30, 30, 24000
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), "-video_track_timescale", "15360"]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2500:])

order = list(plan)
timeline, t0 = [], 0
for bid in order:
    p = plan[bid]; n = p["frames"]
    seg = SEG / f"{bid}.mp4"
    if p["kind"] == "steps":
        starts = [0] + [round((LEAD + st["frac"] * dur[bid]) * FPS) for st in p["steps"][1:]]
        lines = []
        for k, st in enumerate(p["steps"]):
            end = starts[k + 1] if k + 1 < len(starts) else n
            lines += [f"file '{(B / st['png']).as_posix()}'", f"duration {(end - starts[k]) / FPS:.6f}"]
        lines.append(f"file '{(B / p['steps'][-1]['png']).as_posix()}'")
        lst = SEG / f"{bid}.txt"; lst.write_text("\n".join(lines) + "\n")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"fps={FPS},format=yuv420p",
             "-frames:v", str(n), *ENC, str(seg)])
        p["step_frames"] = starts
    else:
        x, y, w, h = p["window"]; D = n / FPS; y0, y1 = p["y0"], p["y1"]
        ease = f"({y0}+({y1}-{y0})*(1-cos(PI*min(t/{D:.4f},1)))/2)"
        fc = (f"[1:v]crop={w}:{h}:0:'{ease}'[pan];[0:v][pan]overlay={x}:{y}[b];[b][2:v]overlay=0:0,format=yuv420p")
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x0A0E13:s=1920x1080:r={FPS}:d={D:.4f}",
             "-loop", "1", "-framerate", str(FPS), "-i", str(B / p["src"]), "-loop", "1", "-framerate", str(FPS), "-i", str(B / p["overlay"]),
             "-filter_complex", fc, "-frames:v", str(n), *ENC, str(seg)])
    timeline.append({"id": bid, "start_frame": t0, "frames": n})
    t0 += n
    print("segment", bid, n, "frames", flush=True)

(SEG / "all.txt").write_text("".join(f"file '{(SEG / (b['id'] + '.mp4')).as_posix()}'\n" for b in timeline))
video = OUT / "video_only.mp4"
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(SEG / "all.txt"), "-c", "copy", str(video)])

# Narration: each beat's WAV after its lead, then silence to the beat's exact length.
total = t0 / FPS
audio = np.zeros(int(round(total * SR)), dtype=np.int16)
for b in timeline:
    if b["id"] not in dur:
        continue
    with wave.open(str(B / "audio" / f"{b['id']}.wav")) as wv:
        assert wv.getframerate() == SR
        pcm = np.frombuffer(wv.readframes(wv.getnframes()), dtype=np.int16)
    s0 = int(round((b["start_frame"] / FPS + LEAD) * SR))
    audio[s0:s0 + len(pcm)] = pcm[: len(audio) - s0]
with wave.open(str(OUT / "narration.wav"), "wb") as wv:
    wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(audio.tobytes())

# Soft captions: each beat's caption in chunks of at most 84 characters, timed by their share of the text.
def chunks(text, maxlen=84):
    """Sentences, and long ones split into balanced parts (at a comma or colon near the middle, else a space)."""
    out = []
    for rest in re.split(r"(?<=[.?!])\s+", text.strip()):
        while len(rest) > maxlen:
            k = -(-len(rest) // maxlen); target = len(rest) / k
            cands = [m.end() for m in re.finditer(r"[,:;] ", rest) if abs(m.end() - target) <= 18 and m.end() <= maxlen]
            if not cands:
                cands = [m.start() for m in re.finditer(" ", rest) if m.start() <= maxlen]
            c = min(cands, key=lambda c_: abs(c_ - target))
            out.append(rest[:c].strip()); rest = rest[c:].strip()
        if rest:
            out.append(rest)
    return out
def ts(sec):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
srt, k = [], 1
for b in timeline:
    cap = beats[b["id"]]["caption"]
    if not cap:
        continue
    cs = chunks(cap); tot = sum(len(c) for c in cs); start = b["start_frame"] / FPS + LEAD; a = dur[b["id"]]
    acc = 0
    for i, c in enumerate(cs):
        s = start + a * acc / tot; acc += len(c); e = start + a * acc / tot + (0.25 if i == len(cs) - 1 else 0)
        line = c if len(c) <= 42 else c[: c.rfind(" ", 0, max(42, len(c) // 2 + 1))] + "\n" + c[c.rfind(" ", 0, max(42, len(c) // 2 + 1)) + 1:]
        srt.append(f"{k}\n{ts(s)} --> {ts(e)}\n{line}\n"); k += 1
(OUT / "captions.srt").write_text("\n".join(srt))
assert "\u2014" not in (OUT / "captions.srt").read_text()

final = OUT / "klaxon-final-project-film.mp4"
run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(OUT / "narration.wav"), "-i", str(OUT / "captions.srt"),
     "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000",
     "-c:a", "aac", "-b:a", "160k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
     "-metadata", "title=Klaxon: Final Project Film", "-movflags", "+faststart", str(final)])

# Timings against SCRIPT.md's estimates.
parts = {}
rows = ["| Beat | Part | Script estimate s | Narration s | Beat s | Starts at |", "|---|---|---|---|---|---|"]
for b in timeline:
    bt = b["frames"] / FPS; part = beats[b["id"]]["part"]
    parts[part] = parts.get(part, 0) + bt
    st = b["start_frame"] / FPS
    rows.append(f"| {b['id']} | {part.split('.')[0] if part[0].isdigit() else part} | {beats[b['id']]['seconds']} | {dur.get(b['id'], 0):.2f} | {bt:.2f} | {int(st // 60)}:{st % 60:05.2f} |")
est = sum(x["seconds"] for x in beats.values())
md = ["# Film timings", "", f"Cut: `build/out/{final.name}` (1920x1080, 30 fps, H.264 + AAC, soft English captions).",
      f"Total: **{int(total // 60)}:{total % 60:05.2f}** ({t0} frames). SCRIPT.md's estimate: {int(est // 60)}:{est % 60:04.1f}.", "",
      "| Part | Seconds |", "|---|---|"] + [f"| {k_} | {v:.2f} |" for k_, v in parts.items()] + ["", *rows, "",
      "Each beat = 0.30 s lead + its narration + 0.45 s tail, rounded to whole frames; B21 is a silent 4 s card."]
(OUT / "TIMINGS.md").write_text("\n".join(md) + "\n")
(OUT / "timeline.json").write_text(json.dumps({"timeline": timeline, "plan": plan}, indent=1))
print("\n".join(md[:12]))
