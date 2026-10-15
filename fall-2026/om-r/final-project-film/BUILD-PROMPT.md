# BUILD-PROMPT.md — rebuilding agent-reliability-audit-pitch

This is the real sequence that produced the submitted master
(SHA-256 4a78550dbe0e64567e9f05cb7d251f6f3d3ca2619ed8457be14993e51feb136b),
written after the build — every fix below was actually needed, not
hypothetical. Full narrative detail is in `FRICTIONAL.md`; this file is
the sequence to follow, that one is the why.

## 1. Get Brutalist and confirm the show-tell skill

```bash
git clone https://github.com/nikbearbrown/brutalist.art
cd brutalist.art
python3.11 -m ensurepip --upgrade   # if pip is missing
brew install ffmpeg                 # if ffmpeg is missing
./setup --install
./art --list   # confirm "show-tell" is listed
cat skills/make/show-tell/SKILL.md   # read before writing anything
```

## 2. Place the reel and generate the pre-audio beat sheet

```bash
mkdir -p youtube/agent-reliability-audit-pitch
# copy in make_sheet.py, scenes.py, FACTCHECK.md, SHOTLIST.md, PROMPTS.md
cd youtube/agent-reliability-audit-pitch
python3 make_sheet.py
```

**This writes the PRE-AUDIO sheet only** — no measured durations, no
BCLOSE silent-tail fix (see step 6). The submitted `beat_sheet.json` is
the version after steps 3–6 below, not this script's raw output.

## 3. Branding check before writing any scene

show-tell's default bookends are scripted for a specific instructor
persona: the cold-open narration says "This is Liam, in for Bear," and the
`ClaudeTitleOutro` Remotion component hardcodes `@NikBearBrown` with no
`handle` prop to override it (confirmed by reading `ClaudeTitleOutro.tsx`
directly). Since this film is narrated as myself, neither default is used:

- every `narration_text` is rewritten in first person, no instructor name
- the outro bookend is replaced entirely with a plain drawn closing beat
  (`BCLOSE_TitleCard`), not `ClaudeTitleOutro`
- `bookend_check.py` (which would otherwise flag this) is confirmed, by
  reading `run.sh`/`compile.py` directly, to never be called by `./art run`
  or `./art final` — so this substitution fails no gate the pipeline
  actually runs

## 4. Generate audio (the real timing clock)

```bash
cd ../..
python3 runtime/scripts/generate_audio_kokoro.py youtube/agent-reliability-audit-pitch
```

## 5. Compile the review cut — expect real gate failures, here's what they were

```bash
./art run youtube/agent-reliability-audit-pitch --height 2160
```

This build hit four distinct, real failures before passing clean. Fix each
by reading the actual error, not by guessing:

- **Gate A, repeated-animation error**: a scene created two shapes in one
  `play()` call before Gate A's first snapshot, so they looked identical
  forever. Fix: split into two separate `play()` calls so a real second
  state forms.
- **Terracotta text / undersized captions**: show-tell forbids terracotta
  as a text color and requires labels at Manim font size ≥32 (Manim
  font-size units, not pixels; Gate T's actual measured floor is 41px at
  4K render resolution). Fix: ink text, captions at Manim font size 36,
  with a small non-text ink/terracotta curve as the drawn accent
  instead (matching the toolkit's own precedent of "a hero number plus a
  drawn curve beside it").
  
  *A later Gate T pass flagged two of these curves themselves as
  "terracotta accent text" (a pixel-level text-shape false positive on
  short, thin, slightly curved strokes) — recolored to ink rather than
  editing the gate's own exemption list, which would affect every reel.*
- **Detached floor shadow**: a shadow built as a separate object from a
  crate that later moved stayed behind when only the crate animated — this
  also caused a "label landing on a line" layout-audit error. Fix: group
  shadow + object + label as ONE unit before any move/scale.
- **Object too wide for its gap**: an animated object was wider than the
  gap it needed to visually pass through. Fix: increase the travel/gap
  distance — then re-check the new position is still inside the ±6.3×±3.4
  safe area (an earlier fix moved an object just outside this bound,
  caught by Gate V's edge-bleed check).

## 6. The silent tail — a known fragile manual fix

The first `./art final` passed every gate but had no true silent tail at
the end (the toolkit's 1.0s standard, normally supplied by
`ClaudeTitleOutro`, which step 3 deliberately doesn't use). Fixed by
appending 1.0s of digital silence directly to the closing beat's generated
mp3, and setting its `actual_duration_s` to match in `beat_sheet.json`.

**This fix is fragile**: re-running `generate_audio_kokoro.py` for this
reel will silently regenerate the closing beat's audio at its natural
(shorter) length and lose the padded silence, since the pipeline has no
explicit `tail_silence_s` field. If you regenerate audio, redo this step
before the final render.

## 7. Final render

```bash
./art final youtube/agent-reliability-audit-pitch --height 2160
```

Confirms Gate T (type/contrast check, which only runs here, not in
`./art run`). Save `TYPECHECK.md` — it's a required submission item.

## Before submitting

Cross-check every on-screen claim in the final master against
`FACTCHECK.md`. If anything doesn't trace back to something either real or
explicitly labeled as proposed/constructed, fix the film, not the write-up.
