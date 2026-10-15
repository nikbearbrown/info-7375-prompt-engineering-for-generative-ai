# BUILD-PROMPT — how this film was made, and how to rebuild it

## Prompts I gave Claude (claude.ai, Claude Opus 5.5, 2026-10-14)

1. Pasted the assignment text and the toolkit link: *"this is professors brutalist link help me do my assignment give me zip file which will fullfill all requirements and tell me step by step on terminal how to push and submit the assignment i dont want to loose marks see all minor details and help to do it"*
2. Gave my name, GitHub (`github.com/nikam0420`), target role (data analyst), and machine (Mac).
3. Chose from Claude's three suggestions: project **"Verified SQL Q&A"**, voice **Kokoro, script in my name**, folder in **the professor's class repo**.

What Claude did with those: read my public repos to ground the "existing skills" answers; drafted `PROJECT-BRIEF.md`; wrote `build/make_sheet.py` (narration + visual plan) and `build/scenes.py` (Manim drawings, using the show-tell skill's `iso_kit.py`); wrote the paperwork (`FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`) and this folder's docs; ran the Manim-free gates (A, W, L, bookend) — all passed. It could not render: package downloads are blocked in its workspace, so I rendered on my Mac.

## Commands that rebuild it

```bash
# one-time setup (macOS)
brew install python ffmpeg node cairo pango pkg-config
git clone https://github.com/nikbearbrown/brutalist.art ~/brutalist.art
cd ~/brutalist.art && ./setup --install && ./setup

# rebuild (from this folder)
./build_film.sh ~/brutalist.art
```

`build_film.sh` runs, in order:

```bash
python3 make_sheet.py                                        # writes beat_sheet.json
python3 runtime/scripts/generate_audio_kokoro.py <reel>      # narration = the clock
./art run   <reel>                                           # renders scenes; gates A W L F B V
./art final <reel>                                           # gate T, then the clean master
python3 runtime/scripts/master_check.py   <reel>             # render integrity
python3 runtime/scripts/loudness_check.py <reel>
python3 runtime/scripts/bookend_check.py  <reel>
```

To change the script: edit the narration in `build/make_sheet.py`, re-run `./build_film.sh`. To re-render one scene: delete `<reel>/manim/<BEAT>.mp4` (and `<reel>/media/videos`) and re-run.

## Two fixes the script applies (found 2026-10-14)

- Before rendering it sets `meanSize` 48 -> 52 in `runtime/remotion/src/scenes/ClaudeDefinitions.tsx`. At 48 the terms card fails Gate T (40px < 41px).
- `./art final` writes the master to `brutalist.art/renders/`, so the script copies it into the reel folder before the render-integrity check.
