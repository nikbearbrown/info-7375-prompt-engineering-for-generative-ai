# Final Project Film: CueGate

| | |
| --- | --- |
| Name | Deepak Kumaran Thoppudu Sudharsanan |
| Project | CueGate: subtitles that fit the frame, or don't ship |
| Runtime | 3:55.2 (235.21 s, measured with ffprobe on cuegate-film2.mp4) |
| Film | cuegate-film2.mp4 (3840x2160, 24 fps, h264 + AAC, 15.2 MB); captions in cuegate-film2.srt, every cue tagged with its speaker |
| Toolkit | Brutalist (github.com/nikbearbrown/brutalist.art at commit 519fcbb), skill show-tell, Kokoro voices am_onyx (me) and af_bella (the SKEPTIC), free local pipeline, no API keys |

The narration text is mine. It is voiced by Kokoro because the course requires the free local pipeline. The SKEPTIC is a voice I wrote to ask the hard questions out loud. It is not a real person, a user or a reviewer, and it is labelled that way on screen at its first line.

## How the film follows the four parts

| Part | Film beats | Starts at |
| --- | --- | --- |
| 1. Executive summary: what I'm building and why it matters | B01–B06 | 0:00 |
| 2. Introduction: what others have done | B07–B11 | 0:52 |
| 3. Methods: how I'll build it, the data, and whether I have what I need | B12–B18 | 1:38 |
| 4. Evaluation: how I'll know it worked | B19–B25, then the outro | 2:54 |

## What exists and what will

Today there is the plan (appendix/CUEGATE-PLAN.md), the research (evidence/day-one/) and one dated Claude reply (evidence/claude-exchange.md and .png, 2026-10-14). No CueGate code runs. Everything else in the film is said with "will", and every picture of something not built is labelled CONSTRUCTED on screen. The record is evidence/exists_today-film2.json.

## What is in this folder

- `cuegate-film2.mp4`, `cuegate-film2.srt`: the film and its captions (every narration word; each cue starts with DEEPAK: or SKEPTIC:).
- `beat_sheet.json`: narration, speaker, voice and visual plan for all 26 beats, with the measured durations.
- `appendix/`: the detail behind the methods and evaluation. `CUEGATE-PLAN.md` is the October plan with a dated update line at the top (the shortening step will use a local open-weight model, with no API key); the rest of the file is unchanged from the copy submitted with the pitch film. `FACTCHECK.md` lists every claim, its kind, its verdict and its dated source. `MODELS.md` is the check of candidate local models that download without an account.
- `evidence/`: the Claude exchange shown in the film, the dated day-one source checks, exists_today-film2.json, and `RESOURCES.md`, my own answers about access, compute, data, accounts and code status (the only source for the resources line in M5b).
- `reel/`: code and paperwork written for this film. `NARRATION-FILM2.md` (the narration, one row per beat), `make_sheet.py` (the beat sheet), `pad_audio.py` (the fixed pauses after the SKEPTIC's lines and before the act cards), `make_e1.py` (the E1 still), `scenes_film.py` (the Manim scenes), `build_scenes.py` (assembles scenes.py at build time), `make_captions.py`, and the GATE P paperwork (FACTCHECK.md, SHOTLIST.md, PROMPTS.md, PEDAGOGY.md with my signature). `reel/media/B01.base.png` is the pitch film's B00 still (my screenshot, unaltered), and `reel/media/B01.png` is it with the act chip and speaker tag.
- `gates/`: every gate report. `gates/INDEX.md` lists each gate, its command, its result and its report.
- `FRICTIONAL.md`: my notes on what got in the way. `REVIEW.md`: my review lines, word for word. `BUILD-LOG-FILM2.md`: the tool events, in order.
- `rebuild-film2.sh`: rebuilds the film with one command (below). `patches/`: the two local toolkit patches.

`reel/make_sheet.py` reads `reel/NARRATION-FILM2.md` from its own folder. `rebuild-film2.sh` doesn't need it: it uses `beat_sheet.json`. Some documents name files by their paths in my working folder. In this folder they are: `inputs-film2/RESOURCES.md` → `evidence/RESOURCES.md`; `inputs/claude-exchange.*` → `evidence/claude-exchange.*`; `inputs/CUEGATE-README.md` → `appendix/CUEGATE-PLAN.md`; `youtube/cuegate-film2/` → `reel/`. `inputs-film2/FILM2-SCRIPT.md` and `inputs-film2/ASSIGNMENT-FILM2.md` stay in my working folder; the narration's text is in `reel/NARRATION-FILM2.md` and `beat_sheet.json`.

## Two local modifications to the toolkit

Both are in `patches/`, both are applied by `rebuild-film2.sh`, and neither is committed to the toolkit. They are the same two patches as the pitch film.

1. `patches/setup-guard.patch`: the toolkit's `setup` refuses to run because its ElevenLabs guard matches the toolkit's own `youtube/` fixture files. The patch adds `--exclude-dir=youtube` to that guard's two grep calls, so it still scans everything else.
2. `patches/outro-handle.patch`: the toolkit's outro card hard-codes the instructor's channel handle. The patch adds optional `handle` and `showMascot` props, with the defaults unchanged. This film sets the handle to my name and turns the mascot off.

## Rebuild

Prerequisites (versions this film was built with):

- Python 3.13 (3.13.2) as `python3` on PATH
- Node 24 or newer (v24.21.0) and npm (11.19.0)
- ffmpeg and ffprobe (9.0.1): `brew install ffmpeg`
- Homebrew pkgconf (3.0.8): `brew install pkgconf`. manim's pycairo needs it.
- Homebrew cairo (1.18.4): `brew install cairo`
- git and curl. A few GB of free disk; setup downloads the 340 MB Kokoro model and the Remotion packages.

`rebuild-film2.sh` checks these first and stops with a message naming anything missing.

```bash
./rebuild-film2.sh
```

It builds everything in a new `./_rebuild/` folder and writes the film to `_rebuild/out/cuegate-film2.mp4`, the captions beside it, and the gate reports to `_rebuild/gates/`. If the folder's path is long, the Python virtual environment goes in a short temporary folder instead (`/tmp/cgv.*`), because the Kokoro voices' espeak-ng library can't read its data from a path longer than about 150 characters; the script says when it does this. No keys, no paid services, nothing published.

Tested 2026-11-23 from a fresh copy of this folder: exit 0 and every gate passed. The rebuilt film was one frame longer (235.250 s) and not byte-identical, because a fresh setup installs current package versions: onnxruntime 1.32.0 and numpy 2.5.5 instead of the 1.31.0 and 2.5.4 this film was built with. That changed the voice audio of two beats slightly; every other audio file and every Manim clip came out byte-identical. Details: gates/rebuild-test/COMPARISON.txt.
