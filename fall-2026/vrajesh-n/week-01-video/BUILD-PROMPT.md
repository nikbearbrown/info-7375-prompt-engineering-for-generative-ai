# BUILD-PROMPT — "A Slogan Is a Division"

Everything needed to rebuild this film from this folder. No API keys, no accounts,
no paid services. Total cost to rebuild: **$0.00**.

---

## 0. Prerequisites

```bash
git clone https://github.com/nikbearbrown/brutalist.art
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai course
```

Then install. **Do not just run `./setup --install` and trust the result** — see
FRICTIONAL.md for five failures a fresh clone hits. The working sequence on Windows +
Python 3.13 was:

```bash
# ffmpeg (required by every compile step)
winget install --id Gyan.FFmpeg

# Python deps, MINUS manim: manim<0.19 requires Python <3.13, and because pip
# resolves before installing, including it aborts the whole requirements file.
python -m pip install "kokoro-onnx>=0.4" "mutagen>=1.47,<1.48" "Pillow>=10.2,<11" \
                      "numpy>=2.0.2" "faster-whisper>=1.0,<2"
python -m pip install matplotlib      # undeclared dep of runtime/scripts/typeset_math.py

# Remotion
cd brutalist.art/runtime/remotion && npm install && cd -

# Kokoro voice model (~340 MB, not in git)
mkdir -p brutalist.art/runtime/models/kokoro && cd brutalist.art/runtime/models/kokoro
curl -fLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -fLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd -
```

Windows only: make `python3` resolve to real Python rather than the Microsoft Store stub,
and apply the one-line npx portability patch described in step 3.

Verify honestly — a dependency list is not proof:

```bash
python3 brutalist.art/runtime/scripts/setup_smoke_kokoro.py
# expected: [smoke] kokoro synth OK - mean_volume -21.8 dB   (anything above -40 dB passes)
```

## 1. Generate the beat sheet from executed evidence

```bash
cd course/fall-2026/vrajesh-n/week-01-video
python build_beats.py --course ../../.. --toolkit /path/to/brutalist.art
```

This **executes** `course/research/llm_scale.py` and writes every figure it prints into
`beat_sheet.json`, including a verbatim copy of its output under
`metadata.evidence.recorded_output`. It also typesets the two equations to outlined SVG via
`runtime/scripts/typeset_math.py`.

The script asserts its own arithmetic before writing:

```python
assert abs(words - 225_000_000_000) < 1          # 300e9 tokens x 0.75 words/token
assert abs(rates["250"] - words / (250 * mins_per_year)) < 0.5
assert spread > 1400                              # 2851.9 - 1426.0 = 1425.9
assert 9 < ratio < 11                             # 3.15576e24 / 3.14e23 = 10.05
```

If `llm_scale.py` ever changes, this build either follows it or fails loudly. It cannot
silently disagree with its source. Expected output:

```
wrote .../beat_sheet.json
  beats: 9
  estimated runtime: 202s (3:22)
```

(The 202 s is an *estimate*. The real clock is step 2.)

## 2. Narrate — this sets the clock

```bash
python3 /path/to/brutalist.art/runtime/scripts/generate_audio_kokoro.py .
```

Writes `mp3/beat-B00.mp3` … `beat-B08.mp3` plus `mp3/timings.json`, and stamps
`actual_duration_s` back into `beat_sheet.json`. Measured result:

```
B00 11.95  B01 10.71  B02 19.84  B03 17.54  B04 25.55
B05 21.65  B06 22.63  B07 10.62  B08  6.36
total 146.85s = 2:27
```

Audio-first doctrine: these measured durations are the master clock. Timing is never
fixed by hand — you regenerate audio and recompile.

## 3. Render the scenes

```bash
python3 /path/to/brutalist.art/runtime/scripts/remotion_scenes.py .
```

**Windows patch required.** `remotion_scenes.py:90` builds `["npx", ...]`; on Windows `npx`
is `npx.CMD` and `CreateProcess` cannot launch a bare `.CMD` name from an argv list, so all
nine beats fail with `[WinError 2]`. The fix, in `brutalist.art`:

```python
# before
cmd = ["npx", "remotion", "render", ENTRY, pattern, str(candidate),
# after
npx = shutil.which("npx") or "npx"
cmd = [npx, "remotion", "render", ENTRY, pattern, str(candidate),
```

`shutil` is already imported. Renders each 1920x1080 composition at `--scale=2`, i.e. a
true 3840x2160, `--image-format=png --crf=16`.

## 4. Review cut, then master

```bash
cd /path/to/brutalist.art
./art run   "<this folder>"    # review cut with beat markers burned in
./art final "<this folder>"    # clean 4K master; refuses if any beat is still a slate
```

## 5. Verify by looking, not by probing

Per `CLAUDE-CODE-VISUAL-QC-CHECK.md`, an mp4 probe is a file check, not a pixel check.
Sample frames and read them against the 8-point rubric; results in `_qc/REPORT.md` and
`qc-sheet.png`.

---

## Prompts used with Claude Code

Paraphrased; the full session is not committed, per the GitHub posting rules on private
transcripts. What Claude actually contributed, and what I rejected, is itemised in
SOURCES.md section 3.

1. *"Read Chapter 1 and run its code — I want the real numbers, not the prose figures."*
2. *"Which Chapter 1 concepts have classmates already claimed under fall-2026?"*
   — Relative Quartile is scored against the group, so collisions matter.
3. *"Give me topic options, ranked by whether the mechanism can be shown with real moving
   numbers and whether the concept is unclaimed."*
4. *"Do #2"* — the scale slogan.
5. *"Search the component library before authoring any beat"* — GATE L; produced the
   `ExecutedData` / `TypesetMath` / `FormACard` shortlist.
6. *"Generate the beat sheet from the executed script output rather than hand-typing the
   numbers, and assert the arithmetic at build time."*
7. *"Diagnose why all nine Remotion renders failed"* — the npx `.CMD` bug.

## What was deliberately not done

- No paid API, no key, no account, no upload. The toolkit never publishes; the master stays
  in this folder.
- No Manim. Its pin is broken on Python 3.13, and this film's beats route to Remotion
  anyway. Recorded in FRICTIONAL.md rather than worked around.
- No generated imagery and no Claude transcript on screen. See PROMPTS.md and FACTCHECK.md.
