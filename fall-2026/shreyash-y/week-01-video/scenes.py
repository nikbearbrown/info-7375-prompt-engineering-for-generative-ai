"""
Manim scenes for yadav-shreyash-week01-softmax-max-subtraction.

Every number drawn here is read from evidence/evidence.json, which is written
by evidence/run_evidence.py from the UNMODIFIED course reference
implementation. Nothing in this file is a typed-in figure.

  B03_TwoColumns   — the same logits weighted two ways; the shared factor e^3
  B04_Normalize    — both columns normalise to the identical distribution
  B05_Overflow     — the overflow the shift prevents
  B06_Boundary     — what this does NOT establish: not bit-identical in float64
  B07_Interpreter  — and the size of that gap is the interpreter's, not the maths'

No MathTex / Tex anywhere: this machine has no LaTeX, and the reel does not
need one. See FRICTIONAL.md.
"""

import json
import math
import os
import sys
from pathlib import Path

from manim import *

# ── the Claude fidelity palette (CLAUDE-BRAND.md) ─────────────────────────
BG = "#F2F0E9"
INK = "#3D3929"
SOFT = "#6B6555"
ACCENT = "#D97757"      # THE accent — marks only (rules, arrows, dots, strokes)
WARN = "#A44A32"        # 5.11:1 on cream
GOOD = "#3C6647"        # 5.78:1 on cream (#4A7C59 measured 4.26:1 — failed GATE T)

# GATE T §8.3 requires 4.5:1 for TEXT. Terracotta #D97757 on cream is 2.74:1, so
# accent-coloured *text* uses the darker sibling; the terracotta itself still
# carries every non-text mark, which is where the brand's accent law applies.
ACCENT_TEXT = WARN

MONO = "Menlo"
SERIF = "EB Garamond"

def _find_evidence() -> Path:
    """Locate evidence.json.

    The toolkit's GATE A copies scenes.py ALONE into a temp dir and executes
    construct() there (runtime/scripts/run.sh), so a plain relative read fails
    under the gate even though it works for a normal render. The env var is
    the gate's route in; build.sh exports it. See FRICTIONAL.md.
    """
    env = os.environ.get("WEEK01_EVIDENCE")
    if env and Path(env).is_file():
        return Path(env)
    here = Path(__file__).resolve().parent
    for base in (here, *here.parents):
        candidate = base / "evidence" / "evidence.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "evidence/evidence.json not found. Generate it first:\n"
        "  python3 evidence/run_evidence.py --course <course clone> "
        "--compare <another python3>\n"
        "or point WEEK01_EVIDENCE at it.")


E = json.loads(_find_evidence().read_text())

LOGITS = E["inputs"]["logits"]
PEAK = E["inputs"]["peak"]
XC = E["crosscheck"]

SOURCE_LINE = (
    "Source: lessons/01-randomness-and-first-prompts/code/main.py"
    f"  ·  course commit {E['provenance']['course_commit'][:7]}"
    f"  ·  run {E['generated_at_utc'][:10]}"
)


def f5(x):
    return f"{x:.5f}"


def footer(extra=None):
    """The provenance strip every figure carries."""
    text = SOURCE_LINE if extra is None else SOURCE_LINE + "  ·  " + extra
    return Text(text, font_size=15, color=SOFT).to_edge(DOWN, buff=0.68)


def heading(label):
    return Text(label, font=SERIF, font_size=36, color=INK).to_edge(UP, buff=0.78)


def mono(text, size=24, color=INK, **kw):
    return Text(text, font=MONO, font_size=size, color=color, **kw)


def ulp_str(u):
    return f"{u:+d}" if u else "0"


def tail_marked(value_repr, base, mark, size=16):
    """One monospace number with its final digit tinted (exact glyph metrics)."""
    n = len(value_repr)
    return Text(value_repr, font=MONO, font_size=size, color=base,
                t2c={f"[{n - 1}:{n}]": mark})


PACING = {}
_pacing_file = Path(__file__).parent / "evidence" / "pacing.json"
if _pacing_file.is_file():
    PACING = json.loads(_pacing_file.read_text())


# Holds are scaled so each scene lands on its narration's real duration.
# The audio is the clock (Brutalist doctrine): evidence/pacing.json carries a
# per-scene multiplier derived from the measured Kokoro mp3 lengths, so the
# compiler never has to slow a short clip to fill a long beat.
#
# These arrive by decorator rather than by a base class on purpose: the
# toolkit collects scenes with the regex  class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)
# (runtime/scripts/run.sh), so every renderable scene must say `(Scene)`
# literally. See FRICTIONAL.md.


def _ensure(self):
    """Idempotent init. The QC gate calls construct() without Manim's setup(),
    so nothing may assume setup() ran. See FRICTIONAL.md."""
    if getattr(self, "_paced_ready", False):
        return
    self.camera.background_color = BG
    self._held = 0.0
    self._pace = float(PACING.get(type(self).__name__, {}).get("pace", 1.0))
    self._paced_ready = True


def _setup(self):
    _ensure(self)


def _hold(self, seconds):
    _ensure(self)
    self._held += seconds
    self.wait(seconds * self._pace)


def _tear_down(self):
    _ensure(self)
    print(f"HOLDSUM {type(self).__name__} held={self._held:.4f} "
          f"pace={self._pace:.4f}")


def paced(cls):
    """Give a plain Scene the paced-hold contract, however it gets invoked."""
    cls.setup, cls.hold, cls.tear_down = _setup, _hold, _tear_down
    inner = cls.construct

    def construct(self):
        _ensure(self)
        inner(self)

    cls.construct = construct
    return cls


# ──────────────────────────────────────────────────────────────────────────
@paced
class B03_TwoColumns(Scene):
    """Same logits, two sets of weights. Every row scaled by the same e^3."""

    def construct(self):
        title = heading("The same logits, weighted two ways")
        setup = mono(f"logits = {LOGITS}     temperature = 1.0     max = {PEAK}",
                     24, SOFT).next_to(title, DOWN, buff=0.32)

        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)
        self.play(FadeIn(setup), run_time=0.5)

        lx, rx = -2.6, 3.3
        head_y = 1.75
        rows_y = [0.95, 0.25, -0.45]

        h_left = mono("exp(x)", 26, INK).move_to([lx, head_y, 0])
        h_right = mono(f"exp(x - {PEAK})", 26, ACCENT_TEXT).move_to([rx, head_y, 0])
        rule = Line([-6.4, head_y - 0.33, 0], [6.4, head_y - 0.33, 0],
                    stroke_width=1.2, color=SOFT)

        self.play(FadeIn(h_left), FadeIn(h_right), Create(rule), run_time=0.7)

        for i, x in enumerate(LOGITS):
            y = rows_y[i]
            self.play(
                FadeIn(mono(f"x = {x}", 24, SOFT).move_to([-5.5, y, 0])),
                FadeIn(mono(f5(E["naive"]["weights"][i]), 26).move_to([lx, y, 0])),
                FadeIn(mono(f5(E["shifted"]["weights"][i]), 26).move_to([rx, y, 0])),
                run_time=0.45,
            )

        srule = Line([-6.4, -0.95, 0], [6.4, -0.95, 0], stroke_width=1.2, color=SOFT)
        self.play(Create(srule), run_time=0.4)
        self.play(
            FadeIn(mono("sum", 24, SOFT).move_to([-5.5, -1.5, 0])),
            FadeIn(mono(f5(E["naive"]["sum"]), 26).move_to([lx, -1.5, 0])),
            FadeIn(mono(f5(E["shifted"]["sum"]), 26).move_to([rx, -1.5, 0])),
            run_time=0.6,
        )
        self.hold(2.4)

        # the point: every row differs by the SAME factor
        ratio_txt = f"x {E['ratios'][0]:.6f}"
        arrows, ratios = VGroup(), VGroup()
        for i in range(len(LOGITS)):
            y = rows_y[i]
            arrows.add(Arrow([rx - 1.55, y, 0], [lx + 1.15, y, 0],
                             buff=0.05, stroke_width=2.2, color=ACCENT,
                             max_tip_length_to_length_ratio=0.12))
            ratios.add(mono(ratio_txt, 21, ACCENT_TEXT).move_to([0.35, y + 0.3, 0]))

        self.play(*[GrowArrow(a) for a in arrows], run_time=0.7)
        self.play(*[FadeIn(r) for r in ratios], lag_ratio=0.25, run_time=1.0)
        self.hold(3.0)

        note = mono(f"the same factor every row  -  e^{PEAK} = {E['e_to_the_peak']:.6f}",
                    23, WARN).move_to([0, -2.35, 0])
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.7)
        self.play(Indicate(note, scale_factor=1.05, color=WARN), run_time=0.9)

        self.add(footer())
        self.hold(0.9)


# ──────────────────────────────────────────────────────────────────────────
@paced
class B04_Normalize(Scene):
    """Dividing by the sum cancels the shared factor. Same distribution."""

    @staticmethod
    def _fraction(num_parts, den_parts, size=28):
        """A real stacked fraction built from parts, so pieces stay addressable."""
        num = VGroup(*[mono(t, size, c) for t, c in num_parts]).arrange(RIGHT, buff=0.10)
        den = VGroup(*[mono(t, size, c) for t, c in den_parts]).arrange(RIGHT, buff=0.10)
        width = max(num.width, den.width) + 0.28
        bar = Line(LEFT * width / 2, RIGHT * width / 2, stroke_width=1.6, color=INK)
        return VGroup(num, bar, den).arrange(DOWN, buff=0.15), num, den

    def construct(self):
        title = heading("Divide by the sum and the factor cancels")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)

        lx, rx = -3.7, 3.7
        head_y = 2.30
        rows_y = [1.55, 0.82, 0.09]

        h_left = mono("exp(x) / sum", 26, SOFT).move_to([lx, head_y, 0])
        h_right = mono(f"exp(x - {PEAK}) / sum", 26, ACCENT_TEXT).move_to([rx, head_y, 0])
        self.play(FadeIn(h_left), FadeIn(h_right), run_time=0.6)

        lefts, rights = [], []
        for i in range(len(LOGITS)):
            y = rows_y[i]
            lv = mono(f"{E['naive']['probs'][i]:.5f}", 34).move_to([lx, y, 0])
            rv = mono(f"{E['shifted']['probs'][i]:.5f}", 34).move_to([rx, y, 0])
            lefts.append(lv); rights.append(rv)
            self.play(FadeIn(lv), FadeIn(rv), run_time=0.4)

        self.hold(0.9)

        merged = VGroup(*[
            mono(f"{E['shifted']['probs'][i]:.5f}", 40).move_to([0, rows_y[i], 0])
            for i in range(len(LOGITS))
        ])
        self.play(
            *[Transform(lefts[i], merged[i]) for i in range(len(LOGITS))],
            *[Transform(rights[i], merged[i]) for i in range(len(LOGITS))],
            FadeOut(h_left), FadeOut(h_right),
            run_time=1.3,
        )
        rule = Line([-1.5, rows_y[2] - 0.45, 0], [1.5, rows_y[2] - 0.45, 0],
                    stroke_width=2.6, color=ACCENT)
        self.play(Create(rule), run_time=0.6)
        self.play(FadeIn(Text("one distribution", font=SERIF, font_size=29, color=ACCENT_TEXT)
                         .move_to([0, -0.85, 0]), shift=UP * 0.12), run_time=0.7)
        self.hold(0.6)

        left_f, _, _ = self._fraction(
            [("exp(x - m)", INK)], [("SUM exp(x - m)", INK)])
        right_f, rnum, rden = self._fraction(
            [("exp(-m)", WARN), ("exp(x)", INK)],
            [("exp(-m)", WARN), ("SUM exp(x)", INK)])
        eq = mono("=", 30, INK)
        row = VGroup(left_f, eq, right_f).arrange(RIGHT, buff=0.62).move_to([0, -1.85, 0])

        bars = VGroup(left_f[1], right_f[1])
        rest = VGroup(left_f[0], left_f[2], right_f[0], right_f[2], eq)
        self.play(Create(bars), run_time=0.7)
        self.play(FadeIn(rest), run_time=0.7)
        self.hold(2.4)

        # the factor cancels, so it LEAVES: the two exp(-m) terms are marked,
        # then removed, and the remaining terms close the gap they left.
        self.play(Indicate(rnum[0], scale_factor=1.12, color=WARN),
                  Indicate(rden[0], scale_factor=1.12, color=WARN), run_time=0.9)
        self.play(FadeOut(rnum[0], shift=UP * 0.45),
                  FadeOut(rden[0], shift=DOWN * 0.45), run_time=0.9)
        self.play(rnum[1].animate.move_to(rnum.get_center()),
                  rden[1].animate.move_to(rden.get_center()), run_time=0.7)
        self.hold(2.0)

        self.play(FadeIn(Text("the shift is an exact identity, not an approximation",
                              font=SERIF, font_size=26, color=INK)
                         .move_to([0, -2.70, 0]), shift=UP * 0.1), run_time=0.8)

        self.add(footer())
        self.hold(0.9)


# ──────────────────────────────────────────────────────────────────────────
@paced
class B05_Overflow(Scene):
    """Why bother with an identity that changes nothing: the float64 ceiling."""

    # exponent axis: 0 .. 1100 mapped onto x in [-5.5, 5.5]
    X0, X1, VMAX = -5.5, 5.5, 1100.0

    def x_of(self, value):
        return self.X0 + (self.X1 - self.X0) * (value / self.VMAX)

    def construct(self):
        ceiling = math.log(sys.float_info.max)          # 709.782712893384

        title = heading("Why bother, if the answer is the same")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)
        setup = mono("logits = [1000, 1000]", 24, SOFT).move_to([-3.7, 2.35, 0])
        self.play(FadeIn(setup), run_time=0.5)

        axis_y = 0.35
        axis = Line([self.X0, axis_y, 0], [self.X1, axis_y, 0],
                    stroke_width=1.6, color=SOFT)
        axis_lab = mono("the exponent we hand to exp()", 20, SOFT) \
            .move_to([0, axis_y - 1.5, 0])
        t0 = mono("0", 19, SOFT).move_to([self.x_of(0), axis_y - 0.38, 0])
        t1000 = mono("1000", 19, SOFT).move_to([self.x_of(1000), axis_y - 0.38, 0])
        self.play(Create(axis), FadeIn(t0), FadeIn(t1000), FadeIn(axis_lab), run_time=0.8)

        cx = self.x_of(ceiling)
        ceil_line = DashedLine([cx, axis_y - 0.55, 0], [cx, axis_y + 1.35, 0],
                               stroke_width=2.2, color=WARN, dash_length=0.09)
        ceil_lab = mono(f"float64 ceiling   e^{ceiling:.2f}", 19, WARN) \
            .move_to([cx, axis_y + 1.68, 0])
        self.play(Create(ceil_line), FadeIn(ceil_lab), run_time=0.8)
        self.hold(0.6)

        # ── without the shift: the bar grows straight through the ceiling ──
        tracker = ValueTracker(0.0)
        bar = always_redraw(lambda: Rectangle(
            width=max(0.001, self.x_of(tracker.get_value()) - self.X0),
            height=0.38,
            fill_opacity=1,
            fill_color=WARN if tracker.get_value() > ceiling else INK,
            stroke_width=0,
        ).move_to([self.X0 + (self.x_of(tracker.get_value()) - self.X0) / 2,
                   axis_y + 0.42, 0]))
        readout = always_redraw(lambda: mono(
            f"exp({tracker.get_value():4.0f})", 21,
            WARN if tracker.get_value() > ceiling else INK,
        ).move_to([self.X0 + 0.95, axis_y + 1.15, 0]))

        tag = mono("without the shift", 21, SOFT).move_to([-3.6, -2.05, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.add(bar, readout)
        self.play(tracker.animate.set_value(1000.0), run_time=2.2, rate_func=linear)
        self.hold(0.5)

        err = mono(E["overflow_demo"]["naive_exp_1000"]["error"], 21, WARN) \
            .move_to([0, -2.6, 0])
        self.play(FadeIn(err, shift=UP * 0.12), run_time=0.7)
        self.play(Indicate(err, scale_factor=1.04, color=WARN), run_time=0.8)
        self.hold(0.9)

        # ── with the shift: subtracting the max drags it back to zero ──
        self.play(FadeOut(err), FadeOut(tag), run_time=0.5)
        tag2 = mono("with the shift   x - max(logits)", 21, ACCENT_TEXT).move_to([-3.0, -2.05, 0])
        self.play(FadeIn(tag2), run_time=0.4)
        self.play(tracker.animate.set_value(0.0), run_time=1.6)
        self.hold(0.5)

        self.remove(readout)
        zero_lab = mono("exp(0) = 1", 22, GOOD) \
            .move_to([self.X0 + 1.0, axis_y + 1.15, 0])
        res = mono(f"probabilities([1000, 1000]) -> "
                   f"{E['overflow_demo']['shifted_probabilities_1000_1000']}", 22, GOOD) \
            .move_to([0, -2.6, 0])
        self.play(FadeIn(zero_lab), run_time=0.5)
        self.play(FadeIn(res, shift=UP * 0.12), run_time=0.7)
        self.hold(0.9)

        self.add(footer())
        self.hold(0.9)


@paced
class B06_Boundary(Scene):
    """The named limit: exact on paper, not bit-identical in float64.

    Laid out as three stacked PAIRS rather than two long rows: the comparison
    that matters is naive-vs-shifted within one entry, so the two numbers that
    must be read against each other sit one above the other.
    """

    def construct(self):
        title = heading("What this does not establish")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)

        claim = Text("that the two paths return bit-identical floats",
                     font=SERIF, font_size=27, color=WARN).next_to(title, DOWN, buff=0.30)
        self.play(FadeIn(claim), run_time=0.7)

        naive, shifted = E["naive"]["probs"], E["shifted"]["probs"]
        ulps = E["ulp_difference"]
        ys = [1.30, 0.05, -1.20]

        uppers, lowers, tags, lowers_lab = [], [], [], []
        for i, y in enumerate(ys):
            differs = ulps[i] != 0
            lab_a = mono("exp(x)", 20, SOFT).move_to([-4.6, y + 0.27, 0])
            lab_b = mono(f"exp(x-{PEAK})", 20, ACCENT_TEXT).move_to([-4.6, y - 0.60, 0])
            up = tail_marked(repr(naive[i]), INK, WARN if differs else INK, 25) \
                .move_to([0.5, y + 0.27, 0])
            lo = tail_marked(repr(shifted[i]), INK, WARN if differs else INK, 25) \
                .move_to([0.5, y - 0.60, 0])          # arrives from below
            tag = mono(f"{ulp_str(ulps[i])} ULP" if differs else "same", 22,
                       WARN if differs else GOOD).move_to([4.9, y, 0])
            lowers_lab.append(lab_b)
            uppers.append(up); lowers.append(lo); tags.append(tag)
            self.play(FadeIn(lab_a), FadeIn(up), run_time=0.35)

        self.hold(0.5)
        self.play(*[FadeIn(m) for m in lowers + lowers_lab], lag_ratio=0.15, run_time=0.7)
        self.hold(0.6)
        # they slide up into register: you cannot compare what is not aligned
        self.play(*[m.animate.shift(UP * 0.33) for m in lowers + lowers_lab], run_time=1.0)
        self.hold(0.8)
        self.play(*[FadeIn(t) for t in tags], lag_ratio=0.2, run_time=0.8)
        self.hold(1.8)

        sums = mono(f"sum of probabilities     {E['prob_sums']['naive']!r}"
                    f"     vs     {E['prob_sums']['shifted']!r}", 21, INK) \
            .move_to([0, -2.25, 0])
        self.play(FadeIn(sums, shift=UP * 0.1), run_time=0.8)
        self.hold(0.9)
        self.play(Indicate(sums, scale_factor=1.03, color=WARN), run_time=0.8)
        self.hold(0.7)

        self.play(FadeIn(Text("exactly equal on paper; equal to one unit in the last "
                              "place on this machine",
                              font=SERIF, font_size=24, color=INK)
                         .move_to([0, -2.80, 0]), shift=UP * 0.1), run_time=0.8)

        self.add(footer(f"python {E['provenance']['python']} on {E['provenance']['platform']}"))
        self.hold(0.9)


@paced
class B07_Interpreter(Scene):
    """And the gap is not even a fixed property of the code."""

    def construct(self):
        title = heading("Same code, same machine, two interpreters")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)

        lx, rx = -3.4, 3.4
        a_py, b_py = E["provenance"]["python"], XC["python"]
        a_comp = E["neumaier_probe"]["compensated"]
        b_comp = XC["neumaier_probe"]["compensated"]

        self.play(
            FadeIn(mono(f"Python {a_py}", 25, INK).move_to([lx, 1.95, 0])),
            FadeIn(mono(f"Python {b_py}", 25, ACCENT_TEXT).move_to([rx, 1.95, 0])),
            run_time=0.6,
        )
        self.play(Create(Line([-6.3, 1.55, 0], [6.3, 1.55, 0],
                              stroke_width=1.2, color=SOFT)), run_time=0.4)

        self.play(
            FadeIn(mono("ULP difference", 21, SOFT).move_to([0, 1.0, 0])),
            run_time=0.4,
        )
        # three entry slots per side; a dot marks the entries that disagree.
        # Animating the dots across shows the gap RELOCATING, which is the point.
        def slots(centre):
            g = VGroup(*[mono(f"[{i}]", 20, SOFT) for i in range(3)]) \
                .arrange(RIGHT, buff=0.85)
            return g.move_to([centre, 0.95, 0])

        left_slots, right_slots = slots(lx), slots(rx)
        self.play(FadeIn(left_slots), FadeIn(right_slots), run_time=0.5)

        def values(ulps, group, centre):
            return VGroup(*[
                mono(ulp_str(u), 27, WARN if u else SOFT)
                   .move_to([group[i].get_center()[0], 0.35, 0])
                for i, u in enumerate(ulps)
            ])

        a_vals = values(E["ulp_difference"], left_slots, lx)
        self.play(FadeIn(a_vals), run_time=0.6)

        def dots(ulps, group):
            return VGroup(*[
                Dot(point=[group[i].get_center()[0], -0.2, 0], radius=0.075, color=WARN)
                for i, u in enumerate(ulps) if u
            ])

        a_dots = dots(E["ulp_difference"], left_slots)
        self.play(*[GrowFromCenter(d) for d in a_dots], run_time=0.5)
        self.hold(1.0)

        b_vals = values(XC["ulp_difference"], right_slots, rx)
        b_dots = dots(XC["ulp_difference"], right_slots)
        self.play(FadeIn(b_vals), run_time=0.6)
        # the same two dots travel to where THIS interpreter puts the gap
        self.play(*[Transform(a_dots[i], b_dots[i]) for i in range(len(a_dots))],
                  run_time=1.3)
        self.hold(1.2)

        self.play(
            FadeIn(mono("sum([1e100, 1.0, -1e100, 1.0])", 20, SOFT).move_to([0, -0.35, 0])),
            run_time=0.5,
        )
        self.play(
            FadeIn(mono(f"{E['neumaier_probe']['value']!r}"
                        + ("   compensated" if a_comp else "   not compensated"),
                        22, GOOD if a_comp else SOFT).move_to([lx, -0.9, 0])),
            FadeIn(mono(f"{XC['neumaier_probe']['value']!r}"
                        + ("   compensated" if b_comp else "   not compensated"),
                        22, GOOD if b_comp else SOFT).move_to([rx, -0.9, 0])),
            run_time=0.8,
        )
        self.hold(3.0)

        stable = VGroup(
            mono("stable across both interpreters", 20, SOFT),
            mono("not bit-identical", 20, INK),
            mono(f"sum of shifted probabilities  {E['prob_sums']['shifted']!r}", 20, INK),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([0, -1.9, 0])
        self.play(FadeIn(stable, shift=UP * 0.1), run_time=0.9)
        self.hold(1.8)

        self.play(FadeIn(Text("the gap is real; where it lands is your interpreter's, "
                              "not the mathematics'",
                              font=SERIF, font_size=25, color=WARN)
                         .move_to([0, -2.70, 0]), shift=UP * 0.1), run_time=0.8)

        self.add(footer("CPython 3.12+ compensates sum()"))
        self.hold(0.9)
