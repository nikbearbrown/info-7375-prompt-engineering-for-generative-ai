# FRICTIONAL: Week 1 Explainer Video

This log was compiled on 2026-09-26 from the Claude Code session transcript,
terminal output, and file timestamps. The dated entries record what actually
happened, retrospectively. The last entry is a reflection Claude wrote at my
request, from the same record and what I told it.

## 2026-09-26, about 02:30 EDT: getting the course code to run

- I ran the setup steps in my own terminal. I added the Homebrew Python PATH
  line to `~/.zshrc` (02:33), forked and cloned the course repo (02:34), then
  ran `scripts/validate_course.py`.
- The first validation attempt failed with `can't open file
  '/Users/aravinds/Downloads/scripts/validate_course.py'`. My terminal was in
  `~/Downloads`, not the repo. After `cd` into the repo it passed: 15 lessons,
  90 lesson tests, and 13 integration tests.
- Friction: my terminal used Python 3.12.14, but Claude Code's shell still
  used macOS's Python 3.9.6, below the course's 3.11 minimum.

## 2026-09-26, about 21:55: the PATH fix did not reach Claude Code

- A fresh Claude Code session still reported Python 3.9.6. Claude read the
  desktop app's shell snapshot and found that it hard-codes the app's own
  PATH, so edits to `~/.zshrc` and `~/.zprofile` never reach it.
- Claude proposed a user-level SessionStart hook that appends the Homebrew
  Python path to `$CLAUDE_ENV_FILE`, the mechanism documented for this. It
  tested the hook on a scratch file first. I approved creating
  `~/.claude/settings.json` (21:59). A new session then reported 3.12.14.

## 2026-09-26, 22:03: found the assignment

- Canvas showed the Week 1 video due Sunday 2026-09-27 at 11:59 PM, about 26
  hours away. I asked Claude to build it end to end so I could study the
  result before submitting.

## 2026-09-26, 22:05-22:20: toolkit install, three blockers

1. Node and FFmpeg were missing. Homebrew installed Node 26.10.0 and FFmpeg 9.0.2.
2. `./setup --install` failed in pip: `pycairo` must be built from source and
   needs Cairo plus `pkg-config`, and then `manimpango` needed Pango. After
   installing cairo 1.18.6, pkgconf 3.0.7, and pango 1.58.2, pip succeeded:
   Manim 0.18.1, kokoro-onnx, and faster-whisper 1.2.1.
3. The toolkit's own readiness check stopped before printing its table. Its
   ElevenLabs guard matched example files inside the toolkit's own `youtube/`
   folder, so the problem is upstream, not in our files. Claude ran the same
   checks by hand, and the Kokoro smoke test synthesized audio at -21.8 dB.

## 2026-09-26, 22:16: evidence before script

- `evidence/softmax_steps.py` imports the lesson's own `probabilities()` and
  prints every number the video uses. Its outputs are saved in `evidence/`.

## 2026-09-26, 22:20-22:45: script, audio, scenes, and the QC gates

- Narration: 9 beats and 505 words, generated locally with Kokoro `am_onyx`
  (about 151 s). Word times were aligned with faster-whisper, so each value
  appears as it is spoken.
- Bug caught by the layout audit: in B00 the question text flew diagonally
  off the frame. The scene file had defined constants named `LEFT` and
  `RIGHT`, which overwrote Manim's direction vectors of the same names. They
  were renamed to `XL` and `XR`.
- Layout fixes:
  - B02's highlight box clipped the `[` next to `-0.2500`; it became an underline.
  - B03's longest code line ran past the frame; the code block now scales as one unit, so indentation stays true.
  - Two other lines touched the safe margin.
- Gate A false positives: the render-free check estimates text widths, so two
  correctly placed elements looked off-frame to it. They were repositioned
  relative to their neighbours. The real-render audit was already clean.
- Claim correction: B07 first said the transformation "guarantees positive
  numbers that sum to one". In floating point a weight can underflow to 0.0
  (`math.exp(-800)` is `0.0`). The narration now says "In exact arithmetic",
  matching the chapter, and the on-screen heading reads "Guaranteed (exact
  math)".

## 2026-09-26, about 22:45-23:00: review cut, visual QC, and the final gate

- The first review cut passed the automated frame check (Gate V: 0
  blockers, 0 major). Looking at full-size frames still found defects the
  gates did not flag:
  - "only rank three outcomes." (B01) and "Not yet." (B00) sat higher than
    the words before them, because centering text with descenders shifts it.
    Text is now aligned on its baseline.
  - `total 1.5032` and `sum = 1.0000` ran into each other in B04.
  - One header per table sat low, and B05's rows were cramped.
- The final export was then blocked by Gate T, a typography check that runs
  only at export. It reads solid terracotta (`#D97757`) bars and arrowheads
  as low-contrast "text" on cream. Accent shapes now use the darker
  `#A44A32`, the same colour the accent text already used, which passes WCAG
  at 5.5:1.

## 2026-09-26, 23:07: reflection

Claude wrote this section at my request, from our session record and what I
told it.

- **What I took from the final cut:** a list like `[1, 2, 3]` only ranks
  outcomes. The lesson's function turns it into chances by exponentiating the
  gaps and dividing by the total, so each 1-point gap multiplies the chance by
  e. The result is the chance of being *sampled* from hand-picked scores, not
  the chance of being *right*.
- **Friction I actually hit:**
  - I ran `validate_course.py` from the wrong folder.
  - I wasn't sure whether setup was finished, or which Claude session to work in.
  - At 22:03 I found that the Week 1 deliverable was this video, due in about 26
    hours, not the Assignment 1 I had been preparing for.
- **Decision:** with the deadline that close, I had Claude build the whole video
  (the course allows and expects AI use) and planned to study the result before
  submitting.
- **What I checked:** I watched the final cut at 23:07. At 23:15 I re-ran
  `lessons/01-randomness-and-first-prompts/code/main.py` myself. It printed
  0.09003, 0.24473, 0.66524, which match the video's 0.0900, 0.2447, 0.6652
  (beats B04 and B07). I did not re-run `evidence/softmax_steps.py`; Claude ran
  it and compared every other on-screen number with its saved output.
- **Next step:** learn the concept well enough to explain it to a TA without
  notes, including the questions just outside the video: why subtract the max
  first, and what temperature changes.
