# Week 1 Explainer Video: Three Scores Are Not Yet Three Chances

- **Student:** Aravind Sundaravadivelu (`aravind-s`)
- **Course:** INFO 7375 Prompt Engineering for Generative AI, Fall 2026
- **Assignment:** Week 1 Explainer Video (explain one concept from Chapter 1)
- **Video:** `three-scores-not-yet-three-chances.mp4`, runtime 2:32, 1920x1080
- **Built with:** the Brutalist toolkit (`nikbearbrown/brutalist.art`, commit `cd4bf20`), Manim, and local Kokoro narration. Claude Code did most of the build at my request (details in SOURCES.md).

## The concept

From Chapter 1, Part 2: **three scores are not yet three chances.** Scores such
as `[1, 2, 3]` only rank outcomes: they sum to 6 and can be negative. The
lesson's `probabilities()` turns them into chances in three moves:

1. Subtract the largest score.
2. Exponentiate.
3. Divide by the total.

That is why a negative score still gets a positive chance, and why each
1-point gap between scores multiplies the chance by e ≈ 2.7183.

**Why this one:** it is the smallest mechanism in the chapter that can be
shown completely with the lesson's own printed numbers, and the chapter's
later ideas (temperature, sampling, seeds) all build on it.

**What the video does not establish (beat B07):** the results are chances of
being *sampled* from hand-picked scores, not chances of being *right*.

## Contents

| File | What it is |
|---|---|
| `three-scores-not-yet-three-chances.mp4` | The rendered video |
| `beat_sheet.json` | The reviewed narration and visual plan (9 beats, with measured audio durations) |
| `scenes.py` | Manim source for every beat |
| `evidence/softmax_steps.py` | Prints every number shown, using the lesson's own `probabilities()` |
| `evidence/softmax_steps_output.txt`, `evidence/main_py_output.txt` | The saved real outputs (Python 3.12.14) |
| `FACTCHECK.md` | Every claim in the video and its evidence |
| `SHOTLIST.md`, `PROMPTS.md` | The toolkit's work order and prompts, required for rendering |
| `BUILD-PROMPT.md` | The prompts and commands that rebuild the video |
| `SOURCES.md` | What was used, what was made, what Claude contributed, and licences |
| `FRICTIONAL.md` | Dated log |
| `qc/` | The toolkit's QC evidence: frame-check report (Gate V), typography check (Gate T), contact sheet, and the final export's SHA-256 receipt |

## Check every number (no toolkit needed)

From the course repository root:

```bash
python3 lessons/01-randomness-and-first-prompts/code/main.py
python3 fall-2026/aravind-s/week-01-video/evidence/softmax_steps.py
```

Compare the output with the two files in `evidence/`.

## Rebuild the video

BUILD-PROMPT.md has the full recipe. The short version (macOS with Homebrew
and Python 3.11+) copies the folder to `/tmp` so the build files do not land
in the course repo:

```bash
brew install node ffmpeg cairo pkgconf pango
git clone https://github.com/nikbearbrown/brutalist.art.git && cd brutalist.art && git checkout cd4bf20
python3.12 -m venv .venv && source .venv/bin/activate && ./setup --install
cp -R <course-repo>/fall-2026/aravind-s/week-01-video /tmp/week-01-video
python3 runtime/scripts/generate_audio_kokoro.py /tmp/week-01-video
python3 runtime/scripts/align.py /tmp/week-01-video
./art run /tmp/week-01-video --height 1080
./art final /tmp/week-01-video --height 1080 --out /tmp/week-01-video/final
```

## License

The code (`scenes.py`, `evidence/`) is MIT. The video, the narration script,
and these documents are CC BY 4.0. The lesson code shown in beat B03 comes from
the course repository (MIT).
