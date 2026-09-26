# FRICTIONAL.md — why-subtract-the-max

Everything that broke or needed adjusting, in the order it happened. Nothing
here is smoothed over; each entry is a real failure with the real message.

Dates are the session dates. Environment: Windows 11, Python 3.13.5,
Node 24.19.0, ffmpeg 9.0.1 (Gyan build), manim 0.19.2, MiKTeX 25.12.

---

## 2026-09-14 — toolkit would not install or run on Windows at all

These are defects in `brutalist.art` itself, found while getting `./setup`
green before any of this reel existed. All six fixes are still applied in the
toolkit working tree and are **uncommitted**.

1. **`python3` resolved to the Microsoft Store stub.** Every `pip install`
   printed "Python was not found" and installed nothing, so `./setup` reported
   all Python features missing even after installing them. Fixed by copying
   `python.exe` to `python3.exe` in `...\Programs\Python\Python313\`, which
   precedes `WindowsApps` on PATH.

2. **`manim>=0.18,<0.19` is uninstallable on Python 3.13.** Every 0.18.x
   release caps at `Requires-Python <3.13`. pip resolves before installing, so
   this one pin aborted the whole `requirements.txt` batch and nothing
   installed. Relaxed to `>=0.19,<0.20`; that pulled manimpango 0.6 and
   Pillow 12, so those ceilings moved too. Verified by rendering a real repo
   scene, not by trusting the import check.

3. **ffmpeg filtergraph destroyed the Windows font path.** `compile.py`
   interpolated a raw path into a `drawtext` filter; the parser ate the
   backslashes and split on the drive colon, failing with
   `Error parsing filterchain`. Needed a **double** backslash before the colon
   (`C\\:/path`) — a filtergraph option value is unescaped twice. Found by
   probing eight escaping forms against the actual ffmpeg build.

4. **Locale encoding broke text I/O.** `atomic_json`/`atomic_text` wrote with
   the platform codepage while `json.dump` ran `ensure_ascii=False`, so any
   em dash or arrow crashed with `'charmap' codec can't encode character`.
   Fixing only the write side made it **worse** — reads still produced mojibake
   which then got written back as UTF-8, double-encoded into bytes cp1252
   could not decode, turning a warning into a hard crash. Real scope was 59
   call sites; fixed with `PYTHONUTF8=1` in `./art` (PEP 540).

5. **`./art smoke` could not pass as shipped, on any platform.** Two causes:
   the fixture's own slug `_smoke` was rejected by `build_safety.py`'s slug
   regex (which the harness simultaneously *requires*), and Gate V blocks on
   the review timecode burned 16px from the right/top edge. It passed
   historically only on freetype-less ffmpeg builds where `has_drawtext()`
   returns False.

---

## 2026-09-22 — building this reel

6. **`main.py` does not print most of what this reel needs.** It emits only
   `probabilities([1,2,3])` and the sampler counts. The intermediates, the
   unshifted path, and the `[1000,1000]` case are never printed. Resolved by
   importing the module and calling its own `probabilities()`, checking every
   recomputed stage against that function's return (max abs difference 0.0).
   The distinction is recorded in SOURCES.md rather than hidden.

7. **The brief's "identity check" is false as specified.** It asked to show the
   two paths "produce identical final probabilities." They do not: indices 0
   and 2 differ in the last bit, max abs difference `1.1102230246251565e-16`,
   and `sum(probabilities)` is `0.9999999999999999`, not `1.0`. B03 states
   "agreement, not identity" instead. Flagged to the user before building.

8. **GATE F blocked the first render.** `FACTCHECK.md`, `SHOTLIST.md` and
   `PROMPTS.md` must exist *before* rendering, not after. Written, then re-run.

9. **All seven scenes were invisible to the renderer.** `run.sh` discovers
   scenes with `class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)` — it requires
   inheriting `Scene` **directly**. My shared `_Base` class for the cream
   background meant zero scenes matched; the run reported "nothing to render"
   and would have compiled seven slates. Replaced the base class with a
   `page(scene)` function.

10. **GATE A: `NameError: name 'NORMAL' is not defined`.** Gate A executes
    `construct()` against a *stub* `manim` module that defines geometry and
    animation names but not the text-weight constants. `weight=NORMAL` works
    in real manim and fails the gate. Switched to the string form
    `weight="NORMAL"`, which both accept.

11. **GATE A: "shapes never change" on B05, then on B00 and B06.** The gate
    scores shape *movement*, not presence. B05 (static statement + fixed rule)
    was a hard error. Adding one static shape to B00/B06 made them **worse** —
    they went from a non-blocking "no shapes recorded" warning to a blocking
    "1 distinct shape-state" error. Fixed with markers that actually move.

12. **GATE W: chapter number on screen.** `INFO 7375 · CHAPTER 1 · …` tripped
    W7 (SLATE-RUNNER recap law), which matches `/\bchapter\b|\bch\.\s*\d/i`
    over every string constant in the class. Renamed to name the topic. The
    narration still says "Chapter One" — the law governs the frame, not the
    voice.

13. **GATE B: safe area is tighter than documented.** `layout.ts` and the Gate V
    docstring describe a 5% inset (x ±6.4, y ±3.6 in Manim units), but
    `manim_layout_audit.py` reports **±6.3 x / ±3.4 y** and enforces that. My
    `kicker()` at `to_edge(UP, buff=0.55)` put text at y=3.45 — 0.05 outside —
    and my `FIT_H` of 6.9 exceeded the real 6.8 limit. Four separate rounds of
    this, one beat at a time:
    - B00: kicker 0.05 above the line.
    - B02: the bottom band ran to **y=-4.12, off-frame entirely**, and the
      `arrange`/`shift` juggling put a value label on top of a bar. Rebuilt
      with explicit coordinates.
    - B03: full-precision diff strings reached x=6.47. Column now shows 3 s.f.;
      the exact figure is on the same frame in the verdict line.
    - B04: `OverflowError: math range error` — the longest string in the reel —
      reached x=6.37.

14. **Every beat was slow-motion.** compile.py stretches a short clip to fill
    its measured audio. My first cut ran 1.7x–3.6x slow; the compiler itself
    warned `B03: clip 8.9s slowed 3.6x into 31.9s beat — extreme slow-mo`.
    Rewrote every scene with holds sized to the measured narration. Now
    1.06x–1.18x.

15. **SKIN LINT wanted Claude bookends.** `palette: claude` makes the linter
    require `ClaudeComposerAsk` as a cold open and `ClaudeTitleOutro` as an
    outro. This is a course assignment with its own beat list, so the palette
    is now `teardown` (the house default).

16. **GATE V: 14 BLOCKERs, all `edge-bleed` "right/top edge", on every frame.**
    Not my content — my scenes pass Gate B's own safe-area audit with 0 errors
    and 0 warnings. It is the review timecode burned 16px from the right/top,
    the same pre-existing conflict as item 5. Confirmed by re-running with
    `ART_NO_DRAWTEXT=1`: BLOCKER went 14 → 0, nothing else changed.
    **This means the reel is compiled with the review clock disabled.** The
    clean master has no review label anyway, so the deliverable is unaffected,
    but it is a workaround around a toolkit bug, not a fix to this reel.

17. **GATE V: `underfill` on B02 (53%) and B06 (49%)** against a 55% floor.
    B02 revealed its four column headers one at a time, so the content bounding
    box stayed narrow through the frame Gate V samples at 50%; it now
    establishes the whole grid first. B06 was simply set too small — `fit()`
    only ever shrinks, so a small block floating mid-page is never corrected.
    Added `fill_safe()`, the Manim counterpart of `fitToSafe()` in
    `tokens/layout.ts`.

18. **`./art run` exited 4 with no Gate V verdict printed.** Run standalone,
    `final_frame_check.py` on the same reel exited 2 and printed its report
    normally. Not diagnosed — the subsequent run completed cleanly, so the
    cause is unknown rather than fixed. Recorded because it is unexplained.

---

## 2026-09-26 — verification pass against the assignment rubric

Found by **looking at extracted frames**, after every gate had already
reported clean. Both are cases the automated checks do not cover.

19. **B05: the kicker printed on top of the boundary statement.**
    "WHAT THIS DOES NOT SHOW" collided with the first line, "This shows the
    shifted and direct calculations". Cause: `fit(body, h=5.9)` centred at
    `UP*0.30` put the body's top at y=3.25, above the kicker's bottom edge at
    ~3.17. Gate B's overlap check (W5 TEXT-ON-LINE) looks for text crossing
    *lines*, and Gate V measures coverage and edge-bleed — neither tests text
    against text at different z-order. On the beat that carries the whole
    boundary requirement, this was the worst place for it. Fixed:
    `h=5.4`, centred at `DOWN*0.10`.

20. **B01: the second arrow rendered as an unreadable stub.** The bars group's
    left edge sat at x=0.60 while the softmax box's right edge was at x=0.45 —
    0.15 units of gap, less than the arrow's two 0.30 buffers. `Arrow()`
    silently drew a degenerate shape instead of failing. Fixed by narrowing
    the bars (`max_w` 4.6 → 3.8) and moving the chips and box left.

Also re-verified in this pass, all unchanged: `python3 main.py` output is
byte-identical at HEAD `8f590fa`; `main.py` lines 14–15 match what B00 renders;
and an AST audit of `scenes.py` confirms every on-screen digit-bearing string
is either interpolated from a provenance constant or one of seven hard-coded
literals, each individually justified.

### Noted, not changed

B01's footer reads "they are all positive, and they sum to 1" while B02
displays `sum = 0.9999999999999999`. The reel states the mathematical property
and then shows the floating-point reality one beat later. Defensible — that gap
is arguably the subject — but it is an internal tension a grader could pick at.
Left as the author's call.

---

## Still open

- The six toolkit fixes are **uncommitted** in the local `brutalist.art` checkout.
  They are not part of this reel and belong upstream.
- Items 3, 4, 5 and 16 are upstream defects worth reporting to the maintainer.
  Item 16 in particular means `./art run` with QC strict cannot pass on any
  ffmpeg that has the `drawtext` filter.
- Item 18 is unexplained.
