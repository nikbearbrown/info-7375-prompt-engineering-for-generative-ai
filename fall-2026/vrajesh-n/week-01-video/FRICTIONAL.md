# Frictional — Week 1 Explainer Video

Concept: a training-scale slogan restated as a division with a hidden assumption.
All three entries are from one working session on **2026-09-26**, split by episode.
Nothing here is retrospective or reconstructed from memory; the log was written
alongside the work.

---

## Entry

**Date and what I was working on:** 2026-09-26, session 1 — picking the concept, and
getting Chapter 1's numbers to reproduce on my machine before planning any video.

**I tried / expected:** Cloned `nikbearbrown/info-7375-prompt-engineering-for-generative-ai`
and ran `lessons/01-randomness-and-first-prompts/code/main.py`, then
`research/llm_scale.py`. I expected the reading-time figures to match the chapter prose
exactly, since the chapter quotes 1,711 / 2,139 / 2,852 years.

**What happened:** They matched, but the script printed a **fourth** rate the chapter prose
never quotes: 300 wpm gives 1,426.0 years. I also noticed the chapter records its own saved
run as Python 3.14.6 while I am on 3.13.3, and the chapter explicitly declines to promise
identical results across interpreter versions. My sampling counts came out identical to its
table anyway: `{0: 102, 1: 268, 2: 630}`.

Separately I checked `fall-2026/` to see which concepts classmates had already claimed,
because Relative Quartile is scored against the group. Seven were taken, including the
max-subtraction (`suketh-p`, "Shifted, Not Changed") — the concept the assignment text
hints at hardest.

**What I did:** Picked the scale slogan instead of the max-subtraction. Two reasons: it was
unclaimed, and the 300 wpm row lets me show a spread the chapter itself does not spell out.
I abandoned an earlier lean toward the 665.24-versus-630 sampling gap. It was also unclaimed
and also good, but it sits inside softmax territory where half the cohort already is, and
its visuals would have looked like everyone else's.

**What Claude or another person contributed:** Claude ran the scripts and produced the
taken/untaken survey of `fall-2026/`. I checked its claim that the 300 wpm row is absent
from the chapter prose by reading the section myself — it is absent; the prose stops at
150/200/250. I accepted the concept recommendation but not the first one it offered: its
initial pick was the sampling gap, and I overrode it on the collision argument.

**What I understand now / still do not understand:** I understand that the "thousands of
years" figure is a division with three inputs, and that only two of them (token count,
words per token) are ever stated. What I still do not know is whether **0.75 words per
token** is accurate for GPT-3's actual tokenizer or is itself a convenient round number.
If it is wrong, every year figure I show scales with it. Next question: is there a published
measurement of that ratio, or is 0.75 also a slogan?

**Evidence and next step:** `research/llm_scale.py` stdout preserved verbatim in
`beat_sheet.json` under `metadata.evidence.recorded_output`. Next: build the beat sheet so
it reads those numbers at build time instead of me copying them by hand.

---

## Entry

**Date and what I was working on:** 2026-09-26, session 2 — installing brutalist.art from a
fresh clone.

**I tried / expected:** Ran `./setup`, expecting the documented dependency table telling me
which features were READY.

**What happened:** Five separate failures, none of them caused by my machine being unusual.

1. **`./setup` exits 1 before running a single check.** Its own ElevenLabs guard
   (`setup:105`) greps the whole tree for four paid-voice fingerprints and hits the
   toolkit's *own self-documenting reel about `setup`*, which quotes those fingerprints in
   `youtube/brutalist/claude-liam-brutalist-command-setup/beat_sheet.json`. The guard's
   own comment says "prose documentation mentioning the name is allowed." The
   implementation does not implement that exception.
2. **`manim>=0.18,<0.19` cannot install on Python 3.13** — every 0.18.x requires
   `Python <3.13`. Because pip resolves before installing, this aborted the *entire*
   `requirements.txt` and left nothing installed, including the packages that were fine.
3. **ffmpeg was absent**, and every compile step needs it.
4. **`./art` calls `python3`**, which on Windows hits the Microsoft Store alias stub.
5. **`typeset_math.py` imports matplotlib**, which is not in `requirements.txt` at all.

**What I did:** Installed ffmpeg via winget. Installed the requirements *minus* manim, which
worked. Made `python3` resolve by copying `python.exe` to `python3.exe` inside the Python
install directory, which sits ahead of `WindowsApps` on PATH. Installed matplotlib
separately.

For manim I did **not** install a Python 3.12 side by side. I checked whether I needed Manim
at all first, and I did not: my concept is typography and numbers, which the `nopunt`
catalog routes to Remotion, and the equation requirement is met by `TypesetMath`, which uses
matplotlib mathtext rather than Manim or LaTeX. The Manim lane is unused in this film, so its
breakage is recorded rather than worked around.

I verified the install rather than trusting it: `setup_smoke_kokoro.py` synthesised and
decoded a real phrase at **-21.8 dB**, above the -40 dB floor.

**What Claude or another person contributed:** Claude diagnosed all five and proposed the
fixes. It initially told me the ElevenLabs guard blocked `./setup --install` entirely; I had
it check line numbers and it corrected itself — the guard is at line 105, *after* the install
block ends around line 100, so the installer does run and only the check phase is blocked.
That distinction changed what I had to do by hand.

**What I understand now / still do not understand:** I understand that a green dependency
table would not have proved much anyway — the setup file itself says readiness is decided
only by live verification, which is why the Kokoro smoke test mattered more than the table I
never got. What I still do not understand is whether the manim pin is deliberate (0.19
changed APIs the toolkit depends on) or simply stale. I did not investigate, because I routed
around it.

**Evidence and next step:** `./setup` exit code 1 with its offending-file list; the smoke test
line `[smoke] kokoro synth OK - mean_volume -21.8 dB`. Next: author the beat sheet.

---

## Entry

**Date and what I was working on:** 2026-09-26, session 3 — authoring the beat sheet and
rendering.

**I tried / expected:** Wrote `build_beats.py` to generate `beat_sheet.json` by executing
`llm_scale.py` at build time, so that no figure on screen is hand-typed. I expected my
narration estimates to be roughly right; I had budgeted 202 s.

**What happened:** Kokoro measured **146.85 s (2:27)**, about 27% shorter than I estimated.
Still inside the 2-4 minute window, so I left it alone rather than padding, which the
assignment says is visible and costs points.

Then `remotion_scenes.py` failed all nine beats at once with
`[WinError 2] The system cannot find the file specified`. The cause is
`remotion_scenes.py:90`, which calls `["npx", ...]` from an argv list; on Windows `npx` is
`npx.CMD`, and `CreateProcess` cannot launch a bare `.CMD` name.

**What I did:** Before patching, I tested three invocations in isolation — bare `npx`
(FileNotFoundError), `shutil.which("npx")` absolute path (rc=0), and `cmd /c npx` (rc=0) —
and took the `shutil.which` version as the smaller change, since `shutil` was already
imported. One line, in my own clone, recorded here.

I also rejected `BarChart` after finding it with `./art scenes`. It looked like the obvious
component for four reading rates, but it is registered at **1280x720**, and
`RENDER-TARGETS.md` requires code lanes to be born at 4K rather than upscaled.
`ExecutedData` is 1920x1080 and renders at `--scale=2` to a true 3840x2160, so I used that
and lost nothing.

**What Claude or another person contributed:** Claude wrote `build_beats.py` and the patch.
The design decision I pushed for was making the beat sheet *generated from executed output*
rather than hand-authored, so the film cannot silently disagree with the script that produced
its numbers; the build-time `assert`s in that file exist for the same reason. I have not
independently verified every one of the 648 compositions Claude searched — only the five I
used.

**What I understand now / still do not understand:** I understand why the toolkit insists
audio is measured first: my estimate was off by nearly a minute, and if I had cut visuals to
the estimate, every beat would have been wrong. I still do not know whether my `at=` reveal
times inside B04 land on the right words, because those were set against my estimate rather
than the measured audio. I need to watch the frames and check.

**Evidence and next step:** `mp3/timings.json` for the measured durations; the one-line diff
in `runtime/scripts/remotion_scenes.py`. Next step: render, then check reveal timing against
the narration by looking at sampled frames, rather than trusting the mp4 duration.

---

## Entry

**Date and what I was working on:** 2026-09-26, session 4 - getting through the two
output gates and cutting the master.

**I tried / expected:** Ran `./art final`, expecting GATE T (type-lock) and gate-v (visual)
to pass, since every beat is a registered component with no slates.

**What happened:** Four things, in order.

1. `./art run` (the review cut) **cannot run on Windows at all**. `compile.py` builds an
   ffmpeg `drawtext` filter containing the literal font path, and a Windows path's
   backslashes and the `C:` colon are filtergraph metacharacters, so ffmpeg mangles the
   path to `NEU coursePEAIbrutalist.art...` and dies with `No option name near`. This
   affects only the review burn-in, so I went to `./art final`.
2. **GATE T silently skipped itself** - `[typecheck] GATE T skipped - missing deps` because
   scipy was absent. A skipped gate is not a passed gate, so I installed scipy and re-ran.
3. With scipy present, `type_check.py` then **crashed on cp1252** writing TYPECHECK.md,
   because it uses `Path.write_text` with no encoding and the report contains a less-than-
   or-equal sign. Setting `PYTHONUTF8=1` fixed that and the same class of bug elsewhere.
4. GATE T then ran properly and **failed**, twice, on real findings: B04's note was 14 words
   against the 12-word NO-WORDY-CARD limit, and then B04's smallest text run measured 36px
   against a 41px floor.

**What I did:** Shortened the B04 note to 10 words, keeping the provenance rather than
dropping it. For the 36px finding I traced it to `ExecutedData.tsx`, whose note line is
`38 * unit` - small enough that *any* reel supplying a note fails the toolkit's own type
floor - and raised it to 46. GATE T then passed: 9 beats, 0 FAILs.

gate-v then reported 0 BLOCKER and 10 MAJOR, all one class: `underfill`, content covering
21-33% of the safe area against a 55% minimum. I raised B01's writer from 96 to 150 and
promoted the course and my name out of B08's dim colophon tier into real body lines, which
moved B01 from 13% to 32% and B08 from 19% to 21%.

Then I stopped, because I do not think the remaining findings are defects. Three rules in
this toolkit cannot all be satisfied at once:

- `type_check.py` 8.5 NO-WORDY-CARD: at most 12 words in a prose element (it blocked me).
- `final_frame_check.py` underfill: at least 55% ink coverage of the safe area.
- `DESIGN-PRINCIPLES.md`: "negative-space / frame-coverage ~15-35% validated pre-render".

You cannot hold 12 words and 55% ink coverage at once with legible serif type, and my cards
sit inside the 15-35% band the design document actually prescribes. I pulled the flagged
frames for B06 and B08 and read them: both are correctly composed, legible, inside the safe
area, with the colophon tier doing its job. So I shipped, and recorded the disagreement here
instead of inflating the type until the gate went quiet.

Separately, reading my own frames caught a real defect the gates did not: B02 and B05 were
printing caret powers as literal text, and MATH-TYPESETTING.md forbids that in an ordinary
text card. I added a `power10()` helper to `build_beats.py` that emits real Unicode
superscripts and re-rendered both. That one was mine, not the toolkit's.

**What Claude or another person contributed:** Claude diagnosed all four gate failures and
traced the 36px finding to the component rather than to my props. I made the call to ship
against gate-v rather than change its threshold - Claude offered lowering the 55% floor in
my clone as an option and I rejected it, because editing a QC threshold so my own build
passes reads badly even when it is logged, and the honest version is this entry.

**What I understand now / still do not understand:** I understand the difference between a
gate that found a defect (B04's 36px caption, which was real) and a gate whose threshold
disagrees with its own design document (underfill). I do not know which is intended to win
when they conflict - `DESIGN-PRINCIPLES.md` claims precedence over "grammar + validators",
which arguably makes the 15-35% band authoritative over gate-v's 55%, but I am not confident
enough to call gate-v simply wrong. That is a question for Bear.

**Evidence and next step:** `TYPECHECK.md` (Overall: PASS, 9 beats, 0 FAILs); `_qc/REPORT.md`
(0 BLOCKER, 10 MAJOR, all `underfill`); `_qc/QC-NOTE.md` for the adjudication; the frames I
read under `_qc/frames/`. Next step: ask whether gate-v's floor or the design document's
band is the intended rule, because every text-card reel in this toolkit will hit this.
