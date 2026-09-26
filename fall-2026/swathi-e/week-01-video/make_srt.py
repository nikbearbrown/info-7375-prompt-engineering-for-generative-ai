#!/usr/bin/env python3
"""make_srt.py -- captions from the beat sheet + Kokoro ground-truth timings."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAP = 0.30
sheet = json.loads((ROOT / "beat_sheet.json").read_text())
t = json.loads((ROOT / "mp3/timings.json").read_text())


def ts(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return "%02d:%02d:%06.3f" % (h, m, sec).replace(".", ",") if False else \
        "%02d:%02d:%02d,%03d" % (h, m, int(sec), round((sec - int(sec)) * 1000))


out, clock = [], 0.0
for n, b in enumerate(sheet["beats"], 1):
    d = t[b["beat_id"]]
    out.append("%d\n%s --> %s\n%s\n" % (n, ts(clock), ts(clock + d),
                                        b["narration_text"]))
    clock += d + GAP

(ROOT / "token-not-word.srt").write_text("\n".join(out))
print("wrote token-not-word.srt  (%d cues, ends %s)" % (len(out), ts(clock - GAP)))
