#!/usr/bin/env python3
"""normalize_audio.py — loudness-normalise the narration timeline before the final compile.

The brief asks for −16 LUFS integrated (±1) and a true peak of −1 dBTP or lower. The toolkit's compile doesn't
normalise, so this script:
  1. rebuilds the master narration track the way compile.py does: each beat's mp3, padded (never trimmed) to
     its frame-rounded render length, as 48 kHz stereo PCM, concatenated;
  2. runs ffmpeg loudnorm in two passes (measure, then apply) to I=-16, TP=-1.5, LRA=11;
  3. writes mp3/master-16lufs.wav, which `art final … --audio mp3/master-16lufs.wav` uses as the explicit
     master track. The verified master is then the delivered file.
Usage: python3 normalize_audio.py   (run after `art run`, which stamps render_duration_s into beat_sheet.json)
"""
import json
import math
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sheet = json.load(open(os.path.join(HERE, "beat_sheet.json")))
fps = float(sheet["metadata"].get("fps", 24))
tmp = tempfile.mkdtemp(prefix="rb-norm-")
wavs, total = [], 0.0
for b in sheet["beats"]:
    dur = b.get("render_duration_s") or math.ceil(float(b["actual_duration_s"]) * fps - 1e-8) / fps
    total += dur
    src = os.path.join(HERE, b.get("audio_file") or f"mp3/beat-{b['beat_id']}.mp3")
    wav = os.path.join(tmp, f"{b['beat_id']}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-map", "0:a:0", "-vn", "-af", "apad", "-t", f"{dur:.6f}",
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav], check=True)
    wavs.append(wav)
lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{w}'\n" for w in wavs))
raw = os.path.join(tmp, "master.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s16le", raw], check=True)

TARGET = "I=-16:TP=-1.5:LRA=11"
log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af", f"loudnorm={TARGET}:print_format=json",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(log[log.rfind("{"):log.rfind("}") + 1])
out = os.path.join(HERE, "mp3", "master-16lufs.wav")
af = (f"loudnorm={TARGET}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
log2 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "2",
                       "-c:a", "pcm_s16le", out], capture_output=True, text=True).stderr
m2 = json.loads(log2[log2.rfind("{"):log2.rfind("}") + 1])
chk = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
s = chk[chk.rfind("Summary:"):]
dur_out = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                               capture_output=True, text=True).stdout)
print(f"timeline {total:.3f} s · wrote {os.path.relpath(out, HERE)} ({dur_out:.3f} s)")
print(f"before: I {m['input_i']} LUFS · TP {m['input_tp']} dBTP · LRA {m['input_lra']}")
print(f"loudnorm mode: {m2.get('normalization_type')}")
print("after (ebur128): I", re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1), "LUFS · true peak",
      re.search(r"Peak:\s+(-?[\d.]+) dBFS", s).group(1), "dBTP")
