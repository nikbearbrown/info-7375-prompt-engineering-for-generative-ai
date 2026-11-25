"""assemble.py - build the toolkit reel inputs for the Early Bird walkthrough film.

Step 1 (done earlier, through the toolkit): generate_audio_kokoro.py produced one narration mp3 per sentence
in ../early-bird-walkthrough/mp3 (am_onyx, free, local). Those measured durations are the clock.
Step 2 (this script): lay the sentences out on one timeline with designed pauses and result-holds, cut it into
7 beats (one per section), write mp3/beat-B0x.mp3 (sentences placed with silence between), timeline.json
(absolute start of every sentence, used by the Remotion scene) and beat_sheet.json (the toolkit's input).

Usage:  python assemble.py
"""
import json, math, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "early-bird-walkthrough"
FPS = 30
GAP = 0.35
PAUSE_BEFORE = {"S01": 0.5, "I01": 0.5, "M01": 0.5, "U01": 0.4, "E01": 0.5, "O01": 0.6}
EXTRA_AFTER = {"S09": 1.2, "M10": 0.8, "U05": 1.6, "E10": 1.0}
TAIL_END = 1.6
BEATS = [("B00", "T", "OPEN"), ("B01", "S", "IDEA"), ("B02", "I", "LANDSCAPE"), ("B03", "M", "BUILD"), ("B04", "U", "SETUP"), ("B05", "E", "TEST"), ("B06", "O", "CLOSE")]

cues = json.loads((SRC / "cues.json").read_text(encoding="utf-8"))
tm = json.loads((SRC / "mp3" / "timings.json").read_text(encoding="utf-8"))
T, DUR, acc = {}, {}, 0.6
for c in cues:
    acc += PAUSE_BEFORE.get(c["id"], 0)
    T[c["id"]] = acc
    DUR[c["id"]] = round(tm[c["id"]], 2)
    acc += DUR[c["id"]] + GAP + EXTRA_AFTER.get(c["id"], 0)
END = T["O03"] + DUR["O03"] + TAIL_END

groups = {b: [c for c in cues if c["id"][0] == p] for b, p, _ in BEATS}
bs = {}
for i, (b, p, _) in enumerate(BEATS):
    first = groups[b][0]["id"]
    bs[b] = 0.0 if i == 0 else T[first] - PAUSE_BEFORE.get(first, 0)
order = [b for b, _, _ in BEATS]
length = {b: (bs[order[i + 1]] if i + 1 < len(order) else END) - bs[b] for i, b in enumerate(order)}
# whole frames, so picture and audio share exact boundaries
length = {b: math.ceil(l * FPS - 1e-6) / FPS for b, l in length.items()}

(HERE / "mp3").mkdir(exist_ok=True)
timings = {}
for b, _, _ in BEATS:
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for c in groups[b]:
        cmd += ["-i", str(SRC / "mp3" / f"beat-{c['id']}.mp3")]
    fl = []
    for n, c in enumerate(groups[b]):
        ms = int(round((T[c["id"]] - bs[b]) * 1000))
        fl.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{n}]")
    n = len(groups[b])
    fl.append("".join(f"[v{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=0:{length[b]:.3f}[a]")
    cmd += ["-filter_complex", ";".join(fl), "-map", "[a]", "-ar", "48000", "-ac", "2", "-c:a", "libmp3lame", "-q:a", "2", str(HERE / "mp3" / f"beat-{b}.mp3")]
    subprocess.run(cmd, check=True)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(HERE / "mp3" / f"beat-{b}.mp3")], capture_output=True, text=True, check=True)
    timings[b] = round(float(r.stdout.strip()), 3)
(HERE / "mp3" / "timings.json").write_text(json.dumps(timings, indent=1), encoding="utf-8")

timeline = {"T": {k: round(v, 3) for k, v in T.items()}, "DUR": DUR, "END": round(END, 3), "beats": {b: {"bs": round(bs[b], 3), "len": length[b]} for b in order}}
(HERE / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")

VOICE = "am_onyx"
beats = []
for b, p, role in BEATS:
    text = " ".join(c["text"] for c in groups[b])
    beats.append({
        "beat_id": b, "act": role, "role_note": f"Software Walkthrough scene, section {role}", "narration_text": text,
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": length[b], "actual_duration_s": timings[b], "audio_file": f"mp3/beat-{b}.mp3",
        "shot": {"type": "REMOTION", "motion": "show-block", "show": [{"at": 0.0, "event": f"app walkthrough, section {role}"}],
                 "remotion": {"pattern": "EbwScene", "props": {"durationSeconds": length[b], "t0": round(bs[b], 3), "timeline": {"T": timeline["T"], "DUR": DUR, "END": timeline["END"]}}}},
    })
sheet = {"metadata": {
    "slug": "early-bird-final-film", "title": "Early Bird: final project film",
    "topic": "INFO 7375 - Final Project Film", "concept": "Early Bird, a job-search agent that reports only new SWE and AI postings",
    "student": "Vrajesh Nasit", "course": "INFO 7375", "engine": "kokoro", "voice_kokoro": VOICE, "clock": "narration",
    "palette": "software-walkthrough", "aspect_ratio": "16:9", "fps": FPS,
    "total_estimated_duration_seconds": round(sum(length.values()), 3),
    "honesty": {"built": False,
                "real": "Commure counts (80 then 81 postings, 12 new), the greenhouse-watch run, the probe match and the 2+ years finding come from the author's earlier graded work",
                "mockups": "company names, the flag quote and the repo match are labelled SAMPLE on screen",
                "narration": "synthetic Kokoro am_onyx voice reading a script drafted with Claude from the author's decisions; disclosed in the last beat"}},
    "beats": beats}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("beats:", {b: (round(bs[b], 2), length[b]) for b in order}, "END", round(END, 2))
