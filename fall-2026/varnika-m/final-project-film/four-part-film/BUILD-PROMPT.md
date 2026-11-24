# Build prompt — A Job-Search Agent You Can Check

The prompts and commands that rebuild this folder and the film. Run 2026-11-23 on macOS, Apple
Silicon, with the brutalist.art virtual environment (Python 3.12, Manim 0.18.1, kokoro-onnx 0.6.1).
Cost: $0.00. No API keys, paid services or uploads.

## 1. My prompts to Claude Code (paraphrased, in order)

1. (Pasted Professor Bear's email) This is my new assignment; please explain it in easy, simple English.
2. The assignment is due today, so this is a new assignment, right?
3. (Pasted the Canvas listing: Final Project Film, due Monday by 11:30 pm, 25 points.)
4. What does the assignment say: is it to be a new one, or something different?
5. Give me project ideas that are best suited.
6. Okay, let's go with the best, which is idea 1, right?
7. Please do the complete assignment now; make sure it is correct, good, and follows all the
   assignment criteria.
8. (My answers to four questions) Animated film with a computer voice · "strict" pass line ·
   my reason: I'm job searching myself · Claude researches what others have done.

## 2. Evidence

```bash
# my earlier work, re-run 2026-11-23
(cd ../../js1-contract-and-watch && python3 -m unittest discover -s tests -t .)   # Ran 73 tests … OK
(cd ../../js2-loop-tools-diff   && python3 -m unittest discover -s tests -t .)   # Ran 122 tests … OK
# the 1,014: Anthropic 677 + Palantir 304 + Linear 33
python3 -c "import json;d=json.load(open('../../js2-loop-tools-diff/jobs/runs/2026-11-10T212848Z.json'));print([(b['key'],(b.get('counts') or {}).get('postings')) for b in d['boards']])"
# the Part 2 pages: URLs and SHA-256s in evidence/others-2026-11-23/README.md
shasum -a 256 evidence/others-2026-11-23/*.html
```

## 3. Toolkit

```bash
cd ~/Desktop/infobrutalist/brutalist.art     # at b21f625, unmodified
source .venv/bin/activate
```

## 4. Beat sheet and narration

`make_sheet.py` drops measured durations, so run it only before voicing.

```bash
python3 make_sheet.py
python3 ~/Desktop/infobrutalist/brutalist.art/runtime/scripts/generate_audio_kokoro.py "$PWD"
# pad B02 (so "1 match" stays on screen) and the outro with a 1.0 s silent tail, then write every measured length back
for B in B02 BOUT; do ffmpeg -y -i mp3/beat-$B.mp3 -af "apad=pad_dur=1.0" -c:a libmp3lame -q:a 2 /tmp/pad.mp3 && mv /tmp/pad.mp3 mp3/beat-$B.mp3; done
python3 - <<'EOF'
import json, subprocess
d = json.load(open("beat_sheet.json"))
for b in d["beats"]:
    b["actual_duration_s"] = round(float(subprocess.check_output(["ffprobe", "-v", "error",
        "-show_entries", "format=duration", "-of", "csv=p=0", b["audio_file"]]).decode()), 3)
json.dump(d, open("beat_sheet.json", "w"), indent=2, ensure_ascii=False)
EOF
```

Pronunciation was checked by transcribing each MP3 with faster-whisper `base.en`.

## 5. Render, gates, final

```bash
cd ~/Desktop/infobrutalist/brutalist.art
./art run   <this folder> --height 1080                            # Gates F, L, A, W, B, V + review cut
./art final <this folder> --height 1080 --out <this folder>/final   # Gate T + master
```

`art run` renders only scenes whose `manim/<BID>.mp4` is missing. To re-render a scene, move its
clip aside first.
