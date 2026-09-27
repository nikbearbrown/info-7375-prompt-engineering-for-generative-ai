# FRICTIONAL — Week 1 explainer video

Machine: MacBook (Apple Silicon), macOS (Darwin 25.5.0), Homebrew Python 3.13.0, Node v20.20.2.
Toolkit: brutalist.art @ `cd4bf20` (identical to the Canvas zip). Course repo @ `149c8e7`.

Claude Code ran the setup steps on my machine at my request. The errors quoted below are copied from its terminal output.

---

## 2026-09-26 — `./setup` exits before checking anything

**Tried:** `./setup` on a fresh clone of brutalist.art.
**Broke:** it exited 1 with `ElevenLabs reference found — this toolkit is Kokoro-only for narration.` The guard (`setup` lines 102–115) matches 10 files, all inside the toolkit's own archived example films under `youtube/brutalist/…`. My files had nothing to do with it. The Canvas zip and the current upstream clone fail in the same way.
**Did instead:** moved `youtube/` out of the toolkit folder (to `A01/_toolkit-youtube-parked/`) without editing any toolkit code. The guard then passed.

## 2026-09-26 — ffmpeg missing

**Broke:** `ffmpeg not found`.
**Did instead:** `brew install ffmpeg` (9.0.2).

## 2026-09-26 — `manim<0.19` cannot install on Python 3.13

**Tried:** `pip install -r requirements.txt` in a venv built on Homebrew Python 3.13.0. I used a venv instead of `./setup --install`, which runs `pip install --break-system-packages` into the global Python.
**Broke:** `Could not find a version that satisfies the requirement manim<0.19,>=0.18`. Every manim 0.18.x release declares `Requires-Python <3.13`.
**Did instead:** `brew install python@3.12` and rebuilt the venv on Python 3.12.14. I didn't upgrade manim, so the toolkit's pinned version stays as it is.

## 2026-09-26 — pycairo will not build

**Broke:** `metadata-generation-failed … pycairo`: the cairo C library wasn't installed.
**Did instead:** `brew install pkg-config cairo pango`. Then manim 0.18.1, manimpango 0.5.0 and pycairo 1.29.1 built.

## 2026-09-26 — Kokoro voice fails the setup smoke test

**Tried:** `./setup --install` (npm deps, fonts and the ~340 MB Kokoro model all installed), then `python3 runtime/scripts/setup_smoke_kokoro.py`.
**Broke:** `Error processing file '/Users/runner/work/espeakng-loader/espeakng-loader/espeak-ng/_dynamic/share/espeak-ng-data/phontab': No such file or directory.` The macOS espeak-ng library inside `espeakng-loader 0.2.4` still points at the path of the CI machine that built it.
**Also tried, did not work:** the `ESPEAK_DATA_PATH` and `PHONEMIZER_ESPEAK_DATA_PATH` env vars; `phonemizer==3.3.0` (breaks kokoro-onnx: no `set_data_path`); `espeakng-loader==0.2.3` (same error); passing the data dir's parent through `EspeakConfig`. I reverted each one.
**Did instead:** `brew install espeak-ng` (1.52.0) and `export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.1.dylib`, an override kokoro-onnx itself supports. Smoke test result: `kokoro synth OK — mean_volume -21.8 dB`. The venv and this variable are both set in `A01/brutalist-env.sh`.
**Result:** `./setup` now shows everything ready except "Manim equation beats" (LaTeX). This video doesn't need LaTeX: equations go through the toolkit's matplotlib renderer, and Manim scenes use `Text`, not `MathTex`.

## 2026-09-27 — `fill_math.py` fails: matplotlib not installed

**Tried:** `python3 fill_math.py <toolkit>` to typeset the B02/B05 equation rows.
**Broke:** `ModuleNotFoundError: No module named 'matplotlib'`. The toolkit's `runtime/scripts/typeset_math.py` imports matplotlib, but `requirements.txt` doesn't list it, and `./setup` doesn't check for it.
**Did instead:** `pip install matplotlib` in the venv, then re-ran. All 5 equation rows typeset.

## 2026-09-27 — scene code adjustments forced by the toolchain

- `DecimalNumber` in manim 0.18 renders digits through LaTeX, which isn't installed here. Running counters in `scenes.py` use `ValueTracker` plus `Text` instead.
- The toolkit's Gate A stub has no `NORMAL`/`BOLD` constants and doesn't call `Scene.setup()`. The scenes pass font weights as strings and start with an explicit `self.begin()`.
- Small EB Garamond text rendered with uneven letter spacing (a known Manim/Pango issue). Type is now set 4× large and scaled down.

## 2026-09-27 — review-cut build: what broke and what was fixed

- **Manim scenes silently skipped.** The first `./art run` printed "nothing to render". `run.sh` finds scenes with the regex `class B.._Name(Scene)`, and my scenes subclassed a helper class. Fix: scenes subclass `Scene` directly, and the timing helper became a separate `Timeline` object.
- **B06 failed to render.** `PredictCard` is named in the ai-explainer SKILL.md but isn't a registered composition (`./art scenes --check PredictCard` → NOT RENDERABLE). Switched to `MedhavyPredictCard`, which has the same props and no brand marks.
- **Gate B (layout audit) failures.** In B04, the "same" label sat on the dashed divider, and the footnote dropped below the safe area. In B07 and B08, the recorded-output cards crossed the title-safe edges, and a box drawn around "0.0" counted as a line crossing text. Fixed by breaking the divider around the labels, moving the bars up, shifting the cards inward, and switching to an underline.
- **Gate V (frame QC) BLOCKER.** The B07 error card's border crossed the left title-safe edge. Fixed by making the card text slightly smaller.
- **Footnote wrapped onto two lines in the 4K render.** The small-type fix (set 4× large, scale down) makes Pango wrap long MarkupText. The B04 footnote now uses plain Text with Unicode superscripts (10⁻¹⁶).
- **Cold-open reply lines too small** (~17 px at 1080p). Set `largeText: true` on B00 and BHTF, which gives ~25 px, the toolkit's legibility floor.
- **Runtime miscount.** I (Claude) first estimated 3:31 by adding the durations wrong. The measured audio totals 189.6 s, and the cut is 189.96 s (≈ 3:10).
- **Remaining Gate V MAJOR items, accepted with `ART_STRICT=0`:** "underfill" on B01 (the toolkit's typing-writer component, mid-sentence), BVDT (the toolkit's verdict page, 47–48% vs 55%), and B03. B03 uses only the left half on purpose: the beat sheet reserves the right half so the B04 shifted column lands beside the same numbers. Zero BLOCKERs remain.

## 2026-09-27 — my own steps (Aravind)

- **Persona:** I asked what "Liam" was, since the draft said "this is Liam, in for Bear". It's the toolkit's synthetic narrator persona standing in for the instructor. I asked for my own name instead. We settled on "Hi, this is Aravind Ravi's week one explainer, read by a synthetic voice", so the voice isn't presented as mine.
- **Running the evidence myself:** my first two attempts failed with `No such file or directory`, because my terminal was in `Assignments/A01`, not the course repo. After `cd` into the repo, both scripts ran, and the numbers matched the earlier run exactly.
- **B00 prompt:** `claude` gave `command not found` (`~/.local/bin` isn't on my PATH), so I ran `~/.local/bin/claude` instead. The fresh session (Sonnet 4.5) said the probabilities are "identical to 15 decimal places". Our draft narration said "about sixteen digits". The re-check showed 15 is right, and I chose "Agree to 15 — stay truthful".
- **What I understand now:** softmax only cares about the gaps between scores, not how big they are. Subtracting the same number from every score cancels out of the fraction, so the max-subtraction is purely a safety step to stop exp() from overflowing. The 1.1 × 10⁻¹⁶ difference we measured is floating-point rounding, not a different answer. I also learned that "equal in exact math" and "equal on the computer" are different claims: Claude's "15 decimal places" was the more precise one, and our own draft had it slightly wrong.
- **What I still don't understand / next question:** the shift fixes overflow but not underflow, so how do real libraries keep a tiny probability from becoming exactly 0.0? My guess is they work in log space (log-softmax / log-sum-exp) and never exponentiate the small value, but I haven't tested it. Next step: compute log-softmax for [0, −1000] and check that it returns about −1000 instead of −inf.
- **Change I requested after watching the review cut, and why it helps understanding:** B01's overview stopped at "It keeps the", so the one sentence that says *why* the subtraction exists never appeared. Finishing it puts the purpose (preventing overflow) on screen before any numbers, so the side-by-side columns in B03/B04 have a reason to exist.

## 2026-09-27 — changes I asked for after watching the review cut

**What I flagged (Aravind):**
- B01's typed overview stopped at "It keeps the" and never finished.
- The outro card showed @NikBearBrown, not me.
- Every frame should be readable at a natural pace and should actually explain the idea.
- There should be a synthesis of what students learn just before the end.

**Why each happened, and what changed (Claude Code diagnosed, I approved the direction):**
- **Unfinished typing:** each typed character takes at least one video frame, so the three lines needed ≈ 10–12 s. The renderer trims the clip to the beat's audio (10.5 s). Fix: slightly longer, more precise B01 narration ("changes the arithmetic, but none of the final probabilities", which also drops the "every number" overclaim) plus cleaner typing settings.
- **Outro handle:** the stock component hard-codes it. Fix: a 3-line toolkit patch (`toolkit-patches/`) adding a `handle` prop, set to "Aravind Ravi · INFO 7375".
- **Pacing:** the voice ran straight from one beat into the next, so each beat's last reveal was on screen for only about 1 s. The toolkit ignores `lead_silence_s`/`tail_silence_s`, so `add_holds.py` pads each narration file with a per-beat hold (1–3 s; 3 s on the predict card so there's time to actually predict). Runtime 3:10 → 3:32.
- **Readability:** the predict card's 22 px commit line was merged into its 38 px spark line. B02's input row got labels ("scores", "temperature") so it no longer dwarfs the formula. B08's two summary lines now land on their own spoken phrases.
- **Synthesis:** the toolkit's bookend check requires recap → Your Turn → outro, so the synthesis stays just before "Your turn". The verdict page became "What you should take away": five lines, adding the "checks nothing about truth" point that was spoken but not shown before.
- **Why this helps understanding:** the pauses give a viewer time to compare the two columns before the next beat starts. The takeaways page puts all five claims, including the limit, in one place to check against. The outro with my name makes clear this is my work, not something the instructor endorsed.

## 2026-09-27 — second round of changes after watching (title card and section markers)

- **I asked for:** a plain title card before the Claude screen that says what the topic is, and a marker on every screen saying what that part is about.
- **What changed:** a new `BTTL` title card (toolkit `FormACard`: title, subtitle, course/chapter, my name, synthetic-voice disclosure). The toolkit wants the Claude screen first, so this uses its documented `bookend_exempt: ["cold-open"]`. B00's narration was rewritten to describe the Claude check actually on screen ("the weights are different, but the final probabilities are identical to fifteen decimal places") instead of talking over it generally. `add_markers.py` burns "1 · The rule" … "7 · The limit", "Takeaways", "Your turn" into the top-right corner, the one corner that's empty in every beat.
- **Why it helps:** the viewer knows the topic and the question before seeing any tool output, and the markers show where they are in the argument (rule → direct → shifted → why → predict → why it exists → limit). The title card adds one more accepted underfill warning (37% fill), which is normal for a title card.
- Runtime is now ≈ 3:50, still inside the 2–4 minute target.

## 2026-09-27 — iteration 2: measure first, then fix, then animate

**Phase 0 (measurements on the 3:50 review cut, `_qc/PHASE0.md`).** A reviewer had flagged problems from frame grabs. Before fixing anything, we reproduced them:
- 32.4 s of silence (14% of the runtime).
- Two background colours, #FBF9F5 and #F1F0E9 (the reviewer had reported four).
- Most beats opened on a near-blank frame.
- Loudness −24.6 LUFS, which was fine.

The whisper transcript plus Kokoro's phoneme output found one real mispronunciation the reviewer couldn't hear: "INFO 7375" was read as "seven thousand three hundred seventy-five". Fixed by spelling it out ("seventy-three seventy-five") in the outro narration (GATE P).

**Problems hit while fixing and animating (all real, in order):**
- **`sci()` hit the video's own subject.** Formatting 5e-324 as "5 × 10⁻³²⁴" computed `10 ** -324`, which itself underflows to 0.0 and raised a divide-by-zero. Rewritten with string formatting.
- **The scene clock drifted.** It added up requested waits, but a 1/24 s wait rendered at 12 fps produces zero frames. BHTF came out 3.9 s short of its audio. The clock now reads Manim's real `renderer.time`.
- **Gate A's Manim stub** doesn't support `.animate(rate_func=…)`, gives placeholder text a huge width, and runs without the beat sheet. Each needed a guard. It also rejects a text-only Manim title card as "shapes never change", so the title card went back to the toolkit's `FormACard`, not a decorative shape.
- **`SVGMobject` rescales every SVG to height 2 by default.** The B05 fraction pieces lost their relative sizes (Σexp(z_j) rendered tiny). Loading at natural size (`height=None`) fixed it.
- **The toolkit's bookend check still fails the rebuilt "Your turn" beat.** Its `bookend_exempt` only applies when no BHTF beat exists at all. It isn't a build gate; logged, not worked around.
- **A stale `media/B02.mp4`** from the Remotion version would have made `run.sh` skip the new Manim B02 (it skips filled slots). Cleared all stale renders.
- **The stacked-bar separators skewed the widths.** The 2 px separator strokes biased the pixel measurement (smallest segment 0.4 points low) and erased the tiny bar's first segment. Removing them brought B03's measured shares to within 0.13 percentage points. The 36 px tiny bar can only be to scale within ±1 px at 1080p.
- **Gate T only runs at `art final`.** It blocked the first final render with four fails: text under the 20.5 px floor in B03, B08 and BVDT (from shrink-to-fit on long counter values and long takeaway lines), and terracotta strike lines over B05's glyphs (2.74:1 contrast). Fixed by larger type, three-line counters, shorter takeaway lines, and ink strikes with the terracotta boxes kept off the glyphs.

**Decisions I made (Aravind):**
- Keep the one toolkit patch (my name on the outro) even though the iteration-2 brief said "don't modify the toolkit": I asked for my name only.
- Keep the spoken synthetic-voice disclosure because the course's Brutalist guide requires it; drop the on-screen one.
- Cut the title card, then ask for it back. It's now 7.3 s and builds line by line instead of the old 18.5 s static card.
- Approved every narration change as a before/after diff (B00, BHTF, BOUT, and the title-card split).

**What I'd check next:** re-run `exp_sweep.py` myself so every evidence file is my own run. Claude Code ran that one.

## 2026-09-27 — final render: two gates that only run at `art final`

- **Gate T (type lock).** Fixing its four fails took three rounds. Its "text run" is a pixel blob measured at 4K, so EB Garamond's small x-height needed about 28–30 pt for lowercase labels. The last failure was a single "→" glyph in a takeaway line, which is only x-height tall. I reproduced each measurement by calling the checker's own functions on the exact mid-clip frame before changing anything. B05's contrast fail came from terracotta boxes the checker read as text-shaped; underlines don't trip it.
- **Gate V at final is strict** (no `ART_STRICT` override), so the four underfill warnings accepted at review time blocked the master. The toolkit's documented fix is a per-beat `qc.sparse_by_design` with a written reason. It's declared for BTTL (title card), B01 (hesitant writer, the case the checker's own docstring names), B02 (the formula held alone before the inputs arrive) and B06 (the predict card). It waives only underfill; edge-bleed and contrast still apply.
- **Final:** 203.75 s, 1920×1080, 9.6 MB, −24.5 LUFS; section markers burned in by `add_markers.py`.
