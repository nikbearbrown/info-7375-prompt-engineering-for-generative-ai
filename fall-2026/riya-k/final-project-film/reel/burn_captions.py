#!/usr/bin/env python3
"""burn_captions.py — burn captions into the v4 master (and write an .srt beside it).

Caption TEXT is the script (beat_sheet.json narration), shown with numerals for readability
(DISPLAY below). Caption TIMING comes from faster-whisper word timestamps of each beat's
narration mp3 (word_timings.json), matched word-by-word to the script with difflib; words the
recogniser misheard (e.g. "Rhea Capadnes") are still shown as the script spells them.

    python3 burn_captions.py <master.mp4> <out.mp4>

Beat start times in the master are the running sum of the clip durations in clips/concat.txt.
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = Path.home() / "Documents/INFO7375/brutalist.art/runtime/fonts/Inter/static/Inter_28pt-Medium.ttf"
W, H, FPS = 3840, 2160, 24
SIZE, PADX, PADY, BOTTOM = 104, 48, 26, 56
INK, CARD = (61, 57, 41, 232), (250, 249, 245, 255)
MAXCH = 48

# Script text with numerals, so a viewer reads "$4,667", not "four thousand six hundred ...".
DISPLAY = {
    "B02": "Picture an analyst asking an AI: what is our revenue by country? The AI writes SQL, the language for asking a database questions. It runs. No errors. It says the USA made $4,667. The real answer is $523.",
    "B06": "Others have tested AI on SQL. BIRD is a public benchmark: 12,751 questions over 95 databases, scored by checking results. People score about 93%, and the best AI still scores lower. But BIRD tests AI only on its own databases, not yours.",
    "B09": "The data: Chinook, a free sample music store database. 11 tables, 59 customers, and 412 orders from 2009 to 2013.",
    "B10": "Step one: write about 50 questions, each with a checked answer. I check every answer a second way, in plain Python, straight from the raw tables.",
    "B12": "Step three: judge by results, not wording, since one answer can be written many ways. These two queries look different, but both give 523.",
    "B15": "The finished project will have one sample database, about 50 test questions, and Claude as the AI it tests. It won't be a chat app, and it never changes the data.",
    "B16": "First, does the checker judge correctly? On 9 test queries that I labeled by hand, comparing wording judged 6 right. Comparing results: all 9.",
    "B17": "Then I had Claude answer my 8 questions, three times. The checker passed 22 of 24. The two fails were a tie my question never settled. Claude wasn't wrong; my question was.",
    "B18": "It also caught a mistake in my answer key. One question asked about 2023, but the data ends in 2013. The right answer was empty, so broken SQL returning nothing looked correct. Now the tool rejects empty answers.",
    "B19": "It worked if the checker agrees with my hand labels every time, every answer key passes the second check, and every miss on the report card has a named cause. It didn't work if Claude gets everything right, because that means my questions are too easy. Today it nearly does, so the next 50 questions must be harder.",
    "B20": "In conclusion: AI can give wrong answers that look right. Ground Truth SQL tests the AI on your own data and shows what's wrong, and why. Today the checker works. Next: 50 harder questions. So the takeaway is this: running SQL is easy. Being right is the test.",
}


def norm(w):
    w = w.lower().replace("$", "").replace(",", "")
    return re.sub(r"[^a-z0-9.']", "", w).strip(".")


def time_words(display_words, heard):
    """Start/end time for every display word, from the matched recogniser words."""
    a = [norm(w) for w in display_words]
    b = [norm(h["w"]) for h in heard]
    t = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            t[blk.a + k] = (h["s"], h["e"])
    known = [i for i, x in enumerate(t) if x]
    if not known:
        raise SystemExit("no words matched")
    for i in range(len(t)):            # interpolate any unmatched word between its matched neighbours
        if t[i] is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            s0 = t[lo][1] if lo is not None else heard[0]["s"]
            s1 = t[hi][0] if hi is not None else heard[-1]["e"]
            span = (hi if hi is not None else len(t)) - (lo if lo is not None else -1)
            pos = i - (lo if lo is not None else -1)
            s = s0 + (s1 - s0) * (pos - 0.5) / span
            t[i] = (s, s + 0.2)
    return t, sum(1 for x in t if x) and len(known) / len(a)


def chunks(words):
    """Split at sentence ends, then at commas/colons, so no caption exceeds MAXCH characters."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        text = " ".join(words[j] for j in cur)
        end = w.endswith((".", "?", "!"))
        soft = w.endswith((",", ":")) and len(text) > 26
        nxt = len(text) + 1 + len(words[i + 1]) if i + 1 < len(words) else 0
        if end or soft or nxt > MAXCH:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def render(text, path, font):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    tw, th = x1 - x0, y1 - y0
    bx0 = (W - tw) // 2 - PADX
    by1 = H - BOTTOM
    by0 = by1 - th - 2 * PADY
    d.rounded_rectangle([bx0, by0, bx0 + tw + 2 * PADX, by1], radius=18, fill=INK)
    d.text(((W - tw) // 2 - x0, by0 + PADY - y0), text, font=font, fill=CARD)
    img.save(path)


def srt_time(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    master, out = Path(sys.argv[1]), Path(sys.argv[2])
    sheet = json.loads((HERE / "beat_sheet.json").read_text())
    heard = json.loads((HERE / "word_timings.json").read_text())
    starts = beat_starts()
    font = ImageFont.truetype(str(FONT), SIZE)
    work = HERE / "captions"
    work.mkdir(exist_ok=True)
    cues = []
    report = []
    for b in sheet["beats"]:
        bid = b["beat_id"]
        disp = DISPLAY.get(bid, b["narration_text"]).split()
        t, matched = time_words(disp, heard[bid])
        off = starts[bid]          # the narration starts at 0 s in each clip (checked with silencedetect)
        report.append(f"{bid}: {matched:.0%} of words matched to the recogniser")
        for c in chunks(disp):
            cues.append([max(0.0, off + t[c[0]][0] - 0.05), off + t[c[-1]][1] + 0.25, " ".join(disp[j] for j in c)])
    for i in range(len(cues) - 1):     # no overlaps: a caption ends when the next one starts
        cues[i][1] = min(cues[i][1], cues[i + 1][0])
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                           "-of", "csv=p=0", str(master)]))
    blank = work / "blank.png"
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    lines, srt, t_now = [], [], 0.0
    for i, (s, e, text) in enumerate(cues, 1):
        p = work / f"c{i:03d}.png"
        render(text, p, font)
        if s > t_now:
            lines += [f"file '{blank}'", f"duration {s - t_now:.3f}"]
        lines += [f"file '{p}'", f"duration {e - s:.3f}"]
        t_now = e
        srt.append(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{text}\n")
    lines += [f"file '{blank}'", f"duration {max(0.1, total - t_now):.3f}", f"file '{blank}'"]
    (work / "list.txt").write_text("\n".join(lines) + "\n")
    out.with_suffix(".srt").write_text("\n".join(srt))
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(master), "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"),
           "-filter_complex", f"[1:v]fps={FPS},format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass:format=auto[v]",
           "-map", "[v]", "-map", "0:a", "-c:a", "copy", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print("\n".join(report))
    print(f"{len(cues)} captions → {out} (+ {out.with_suffix('.srt').name})")


def beat_starts():
    """Start time of each beat in the master: the clips are concatenated in clips/concat.txt order."""
    starts, t = {}, 0.0
    for line in (HERE / "clips" / "concat.txt").read_text().splitlines():
        if not line.startswith("file "):
            continue
        clip = Path(line.split("'")[1])
        starts[clip.stem] = t
        t += float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                            "-of", "csv=p=0", str(clip)]))
    return starts


if __name__ == "__main__":
    main()
