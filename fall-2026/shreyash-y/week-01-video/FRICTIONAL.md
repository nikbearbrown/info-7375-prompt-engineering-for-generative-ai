# FRICTIONAL.md — Week 1 explainer video

Shreyash Yadav · INFO 7375 · two sessions: 2026-09-21 (build) and 2026-09-27 (submission check)

Format follows `prerequisites/frictional.md` in the course repo. Every entry
below is contemporaneous with the work; nothing here is a reconstructed
timestamp. Where I am writing something up after the fact I say so.

Sections 1-12 are from the build session on **2026-09-21**. Section 13 is from
**2026-09-27**, when I re-read the Canvas page against what I had built.

---

## 1 — Picking the concept

**Working on:** choosing one idea from Chapter 1 small enough to finish.

**I tried / expected:** I ran `main.py` first and read the printed numbers
before choosing, on the theory that I should pick whatever concept I could
actually put real numbers behind. I expected to pick the sampling one
(expected 665.24 vs observed 630) because the gap is vivid.

**What happened:** I also computed the naive and max-shifted softmax paths
side by side to see what the shift was doing, and found that they are **not**
bit-identical in float64 — `[1, 0, -1]` units in the last place, and the
shifted probabilities sum to `0.9999999999999999` rather than `1.0`.

**What I did:** switched concepts. "Subtracting the max changes the
intermediates but not the distribution" now had a mechanism I could animate,
a crash I could demonstrate (`exp(1000)`), *and* a precise boundary I had
measured myself rather than one I'd read somewhere.

**Understand now:** the shift is an exact algebraic identity — every weight is
scaled by the same `e^max`, which cancels in the normalisation. The stability
is a consequence of the identity, not the reason it's valid. I had those
backwards when I started.

**Evidence:** `evidence/evidence.json`, `FACTCHECK.md` rows 3–16.

---

## 2 — The finding that changed the video

**Working on:** double-checking the ±1 ULP claim before putting it on screen.

**I tried / expected:** I re-ran the same script under a second interpreter
(the Python 3.11 venv I'd built for the toolkit) expecting identical output —
it is the same machine, the same libm, the same code.

**What happened:** the ULP vector changed. Python 3.14.6 → `[1, 0, -1]`;
Python 3.11.15 → `[0, -1, -1]`. The *shifted* path matched exactly; only the
**naive** path moved.

**What I did:** I did not want to narrate a cause I hadn't checked, so instead
of asserting "3.12 changed `sum()`" I probed for it behaviourally:
`sum([1e100, 1.0, -1e100, 1.0])` returns `2.0` on 3.14.6 and `1.0` on both
3.11.15 and 3.9.6 — i.e. compensated summation is present in the newer one
and absent in the older. I also confirmed `math.exp(1/2/3)` is bit-identical
across all three, so the difference is the summation, not the exponential.
Then I built the cross-run **into** `run_evidence.py` (`--compare`) so the
comparison is part of the artifact and not a thing I once did in a terminal.

**Human vs AI:** Claude proposed the Neumaier/compensated-summation
explanation as soon as I showed it the two vectors. I did not take it — a
plausible cause for a floating-point discrepancy is exactly the kind of
fluent-but-unverified claim this chapter is about. I made it run the probe.
The probe is what's in the video; the explanation is only the caption on it.

**Understand now:** "reproducible" has a scope. The gap between the two paths
is reproducible. *Where* the gap lands is a property of the interpreter's
summation order, not of the mathematics. That became beat B07 and it is the
honest version of "name one thing your explanation does not establish."

**Still don't fully understand:** whether the specific positions `[1,0,-1]`
vs `[0,-1,-1]` would be stable across a different libm (a Linux box, an x86
Mac). I only have arm64 macOS here. That is my next check, and I say so in the
video's own terms rather than implying I've tested more than I have.

**Evidence:** `evidence.json → crosscheck`, `neumaier_probe`; `FACTCHECK.md`
rows 17–19.

---

## 3 — Toolkit install

**I tried / expected:** `./setup --install` in a clone of `brutalist.art`,
expecting it to just work.

**What happened / what I did, in order:**

- Machine default `python3` is 3.14.6. I built a **3.11 venv** before
  installing, on the assumption that `manim` and `kokoro-onnx` wheels lag new
  CPython releases. *Honest note:* I never tested whether 3.14 would have
  worked — I pre-empted a problem I did not confirm. (This later turned out to
  matter for a completely different reason: it gave me the second interpreter
  for entry 2.)
- Python deps then failed for real on **`pycairo`**: `Dependency lookup for
  cairo with method 'pkg-config' failed`. `cairo` and `pango` were installed
  via brew, but `pkg-config` was not. `brew install pkgconf` fixed it; the
  install then completed.
- **No LaTeX** on this machine (`pdflatex` absent), so Manim equation beats
  are unavailable. I did not install MacTeX — I wrote every scene with Manim
  `Text` only and built the algebraic fraction in B04 out of geometry (two
  stacked `VGroup`s and a `Line`). Cheaper than a 4GB TeX install and it
  renders identically.

---

## 4 — Two upstream bugs in the toolkit (worked around, not patched)

Both reproduce on a clean clone of `nikbearbrown/brutalist.art` at commit
`6a8380a`. I did not modify the toolkit for either.

**a. `./setup` never prints its readiness table.** It exits 1 at an
"ElevenLabs guard" that greps the repo for functional ElevenLabs references.
The pattern matches the toolkit's **own shipped example reels**, which
document the guard and therefore quote its pattern — e.g.
`youtube/brutalist/claude-liam-brutalist-command-setup/beat_sheet.json`
contains `"elevenlabs_guard_lines": "setup:102-115"`. So the guard always
self-matches and the readiness check is unreachable on a fresh clone.

*What I did:* ran each of the doctor's checks by hand instead of trusting the
exit code — imported every dep, ran ffmpeg/ffprobe, and synthesised one real
Kokoro phrase via `runtime/scripts/setup_smoke_kokoro.py` (passed at
−21.8 dB). Everything green except LaTeX.

**b. `./art smoke` fails on the toolkit's own fixture.** `generate_audio_kokoro.py`
refuses with `metadata.slug must be a filename, not a path`. The fixture's slug
is `_smoke`, and `validate_project()` in `runtime/scripts/build_safety.py`
requires `[A-Za-z0-9][A-Za-z0-9._-]*` — a leading underscore is rejected. The
shipped fixture cannot satisfy the shipped validator.

*What I did:* copied the fixture to a scratch dir, changed the slug to
`smoke`, and ran the same pipeline. It passed end to end — a 13.9 s mp4 with a
real audio track. So the **pipeline** is healthy; only the fixture's name is
wrong. I needed to know that before blaming my own reel for anything.

---

## 5 — Getting my own reel through the gates

Four things broke. All mine, not the toolkit's.

- **GATE F** refused to render without `FACTCHECK.md`, `SHOTLIST.md`,
  `PROMPTS.md`. Fair — I wrote them. `FACTCHECK.md` turned out to be the most
  useful document in the folder, because it forced me to attach a source to
  every single sentence in the narration, and that is where I noticed I'd been
  about to say "numerically stable" without defining which failure mode.
- **"nothing to render."** The toolkit collects scenes with the regex
  `class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)` (`runtime/scripts/run.sh`). My
  scenes inherited a shared `_Base`, so the regex saw none of them and the
  Manim stage silently did nothing. Fixed by declaring every scene
  `(Scene)` literally and attaching the shared behaviour with a `@paced`
  decorator.
- **GATE A** copies `scenes.py` **alone** into a temp dir and executes
  `construct()` there. My scenes read `evidence/evidence.json` relative to
  `__file__`, which doesn't exist in that temp dir. Rather than inline the
  numbers (which would have defeated the point of generating them), I gave the
  loader a lookup chain: `$WEEK01_EVIDENCE`, then next to `scenes.py`, then
  walking up. `build.sh` exports the variable.
- **GATE A, again:** `'B03_TwoColumns' object has no attribute '_held'`. The
  gate calls `construct()` without Manim's `setup()`, so nothing may assume
  `setup()` ran. Made initialisation idempotent and had `@paced` wrap
  `construct` so it self-initialises however it is invoked.

---

## 6 — Where the visuals were wrong, and how I knew

I rendered every scene at low quality and **looked at the frames** rather than
trusting that correct code means a correct picture.

- **B04:** I first drew the two `exp(-m)` strike-throughs at hard-coded x
  offsets. On the frame they were struck through `— m)` on the left-hand
  fraction and half of the wrong term on the right. Rebuilt the fractions as
  addressable `VGroup` parts and struck the actual mobjects. This is the one I
  would have shipped broken if I had not pulled a frame.
- **B05:** `OverflowError: math range error` at 22 pt overflowed its own box
  and ran off the canvas edge. Dropped to 19 pt and widened the box.
- **B06/B07:** GATE A rejected both — "shapes never change ... repeated
  animation". My reveals were all `FadeIn`, which changes opacity, not
  geometry. Instead of gaming the gate I rebuilt the beats so the motion
  *carries the idea*: B05 is now an exponent bar growing across a marked
  float64 ceiling at `e^709.78` and then being dragged back to zero by the
  shift; B07 animates the two disagreeing entries **moving** to different
  positions when the interpreter changes. Both are better beats than what I
  had. The gate was right.

---

## 7 — Timing

**I tried / expected:** write narration, render scenes, assemble.

**What happened:** my Manim scenes were ~11 s; the narration for those beats
was ~20 s. `compile.py` does not freeze a short clip — it *slows* it
(`setpts`), so every mechanism beat would have played at roughly half speed.

**What I did:** took the toolkit's audio-first doctrine literally. Generated
the Kokoro narration first, measured the real mp3 durations, then computed a
per-scene hold multiplier into `evidence/pacing.json` and re-rendered. Every
scene now lands within **0.6%** of its narration, so the compiler retimes
instead of slowing. Table in `SHOTLIST.md`.

---

## 8 — Human and AI contributions

- **Mine:** the concept choice; the decision to switch after seeing the ULP
  result; the insistence on probing the `sum()` cause rather than narrating
  it; the script; reading frames to catch the B04 strike-through and the B05
  overflow; the call to rebuild B05/B07 rather than suppress the gate.
- **Claude's:** most of the Python and Manim *typing*; the
  compensated-summation hypothesis (which I then made it verify); the toolkit
  spelunking to find why GATE A and the scene-collector were failing; drafting
  these documents from my notes and the actual command outputs.
- **Rejected:** Claude's first B04 used hard-coded strike-through coordinates —
  wrong on the frame. It also initially wrote the narration with the Brutalist
  house persona ("Liam, in for Bear", `@NikBearBrown` chip). I took that out:
  this is coursework and the explanation is mine, so branding it as someone
  else's channel would be a small lie in the one assignment that is about not
  telling those. See `SOURCES.md`.
- **Not done:** no Claude chat transcript appears in the video, because I
  didn't need one as evidence and I wasn't going to manufacture one for
  texture.

---

## 9 — Open

- Does the ULP position hold on x86 / glibc? Untested; I only have arm64 macOS.
- The reel does not test **underflow** — the shift fixes the top end only.
  Claiming "numerically stable" full stop would overstate what I showed, so
  the video says "representable", and `FACTCHECK.md` lists this under claims
  not made.

---

## 10 — The two gates that were actually right

Late in the build, `./art final` ran **GATE T** (typography) for the first time
— it runs on the master export, not on `./art run` — and produced two FAILs I
was glad to get.

**a. My accent colour is not accessible.** Terracotta `#D97757` on the cream
ground measures **2.74:1**, against a 4.5:1 WCAG floor. I had used it for text
in five beats. The brand documentation calls terracotta "THE one accent", so I
had treated it as a settled decision and never checked it.

*What I did:* computed the ratio for every colour in the palette rather than
guessing a replacement. `#A44A32` — already the palette's "warn" terracotta —
measures 5.11:1, so accent **text** moved to it while terracotta kept every
non-text mark (arrows, rules, the dots in B07), which is where the accent law
is really about. The same check caught `GOOD #4A7C59` at 4.26:1, which had
**not** been flagged yet but fails the same floor; darkened it to `#3C6647`
(5.78:1) before it could.

*Understand now:* a brand constant is not exempt from a contrast floor, and
"the gate didn't flag it" is not evidence that something passes — B04–B07 used
the same failing colour and only B03 tripped the check.

**b. I got the second one wrong, twice over.** GATE T also failed B02 for
"text blob touches card right boundary — text is clipped inside the card".

*First instinct:* my code line is too long. I nearly shortened a verbatim source
line to satisfy it. Pulling the frame showed the code nowhere near the edge —
so that was wrong, and reading the frame saved the `FACTCHECK.md` claim I most
wanted to keep.

*Second instinct, also wrong:* I read the component source, found that
`ClaudeCodeBeat` lays its language badge out with `marginLeft: 'auto'` — always
flush to the card's inner edge — confirmed `language` feeds nothing but that
badge, and set `language: ""`. This was a reasonable inference from real source
evidence. It was still wrong. The re-render failed **at the identical column,
3567**, and that identical number is what gave it away: a genuine fix moves the
number.

*What actually worked:* I stopped reading source and replicated §8.13's own
pixel logic against the rendered frame. It reproduced `card_right = 3567`
exactly, and put the offending blob at rows 1977–2014 — *below the card*.
Cropping those pixels showed `INFO 7375`: my own `brandLabel`. §8.13 finds the
card's columns and then scans every row in them, so any footer text
right-aligned to the card's margin trips it. Removed the `brandLabel` from that
beat; restored `language: "python"`, which had never been at fault.

*Understand now:* the check's name ("card-clip") described neither the cause nor
the location, and I twice let a plausible mechanism substitute for a
measurement. The component-chrome theory was better evidenced than the
long-line theory and was equally wrong. The tell was quantitative — an
unchanged column number after a change that should have moved it — not
conceptual.

## 11 — The place I nearly stopped too early

I wrote a justification for leaving GATE V's `underfill` finding on B01
unfixed, and I was wrong to.

The argument felt strong: B01 is the typing-animation BLUF the skill mandates,
the gate samples it mid-animation, so it cannot fill the frame at those points.
I had five measured configurations behind that claim (19/29, 17/26, 36/47,
29/40, 35/45 percent) — it was an evidenced conclusion, not a shrug.

Two things broke it.

**The exception was not actually available.** `compile.py` calls GATE V without
`--lenient` and ignores `ART_STRICT`, so `./art final` refuses while any MAJOR
exists. `ART_STRICT=0` only relaxes `./art run`. The review cut has burned-in
beat labels, so it is not submittable. My fallback did not exist, which is
worth noting: I had written "accepted, with justification" without checking
that accepting it left me with a usable deliverable.

**I had not read the component's whole prop surface.** `BrutalistHesitantWriter`
has a `contextTitle` prop that renders a persistent heading from frame 0. With
it, the content bounding box is large from the first frame regardless of how
much body text has been typed. That plus 120 pt cleared the floor at both
sample points — with the mandated component kept.

I also had a mechanism wrong on the way: I lowered `charMs` to 20 expecting the
writing to finish early and hold, and the 50% frame still showed 3 of 5 lines.
The component distributes its timeline across the beat whatever `charMs` says.

**What I actually learned.** My instinct when a check kept failing was to
decide the check was unreasonable, and I could argue it well. The honest
version is that "this gate is wrong" and "I have not finished reading the
tool" look identical from the inside, and I reached for the first one three
times in this build — the long code line, the language badge, and this. Each
time the resolution came from measuring something specific rather than from a
better argument. That is the chapter's own lesson arriving at my expense.

Cost of being wrong here: several 4K renders, each about ten minutes. Cost of
the fix once I found it: one prop.

## 12 — Open

Unresolved and worth returning to: whether `[+1, 0, −1]` vs `[0, −1, −1]` holds
on a different libm (Linux/x86). Everything here is arm64 macOS.

---

# 2026-09-27 — checking the submission against the assignment

## 13 — Two things I had wrong, found by re-reading the spec

I had the package built, gated and committed, and I thought I was done. Then I
put the Canvas assignment page side by side with the folder and read it line by
line instead of from memory. Two real defects.

**a. The GitHub path was wrong.** I had built
`fall-2025/shreyash-y/week-01-video/`. Canvas says **`fall-2026/`**. The brief I
had been working from said 2025 and I never re-checked it against the live page.

Worth recording because the course's own documents disagree:
`prerequisites/github-submission.md` says `fall-2025/first-name-last-initial/assignment-XX/`,
while the Canvas assignment says `fall-2026/first-name-last-initial/week-01-video/`
— different in **both** the year and the folder name. The assignment states
Canvas is the authority, so I followed Canvas. Flagged for a TA rather than
silently picked.

**b. I was showing a Claude interface that could be read as a transcript.**
This is the one that mattered. The toolkit's cold-open chassis renders the
Claude composer, and with its default props it showed a model chip reading
"Fable 5" and lines under the card that read like a Claude reply — for a
conversation that **never happened**. Meanwhile my own `FACTCHECK.md` asserted
"no Claude transcript on screen."

Against the assignment's rule — *if you show a Claude response it must be a real
one you actually got, with the date* — that was at best a risky reading, and
having the paperwork contradict the video was worse than either alone. The
assignment is explicit that a fabricated transcript fails on its own terms.

*What I did:* blanked the model and effort chips so no model is implied,
labelled both composer beats **RECONSTRUCTED INTERFACE** in the eyebrow, and
rewrote the lines beneath the card to say on screen that they are quoted from
`main.py`, **not a model reply**. Then updated `FACTCHECK.md` and `SOURCES.md`
to describe what is actually shown rather than claim an absence.

*Understand now:* "I didn't fabricate anything" and "nothing on screen can be
read as fabricated" are different standards, and this assignment grades the
second. I had been thinking about the rule as *don't invent a transcript* when
it also means *don't render a UI that implies one*. A component's defaults are
still my claims once I ship them.

## 14 — What the cross-check confirmed

Re-ran the evidence generator from the **pushed public repo**, on a fresh clone,
against a fresh course checkout. Every value matched the shipped
`evidence.json` — weights, sums, ratios, `identical_bitwise`, the ULP vectors on
both interpreters, the overflow demo, the Neumaier probe, and the course commit
`a0d8a1e`. Then pulled B06 and B07 out of the **shipped mp4** and read the
digits off the frames: they match `evidence.json` exactly.

That is the check I actually wanted — not "my script is deterministic" but "a
stranger with this repo gets my numbers."

## 15 — Still open

- The libm question from §2 is unchanged and untested: whether the ULP
  *positions* hold on Linux/x86. Everything here is arm64 macOS.
- `ShreyashY` does not match `github-submission.md`'s documented lowercase
  kebab-case convention (`shreyash-y`). Submitted as instructed; noted here.
- The repo is public, so the reviewer-access requirement is met without
  collaborator setup.
