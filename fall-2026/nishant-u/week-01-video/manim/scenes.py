"""Manim scenes for week-01-softmax-max-subtraction.

One Scene per beat; each reads its measured narration duration from
../beat_sheet.json and times reveals to the spoken phrase (character-offset
estimate). Every displayed number comes from maxsub_runs.py stdout
(2026-09-26) or is labelled as computed / worked by hand.

Render:  manim -qh --fps 24 scenes.py <SceneClass>
"""
import json
from pathlib import Path

from manim import *
from manim.utils.color import ManimColor

HERE = Path(__file__).resolve().parent
SHEET = json.loads((HERE.parent / "beat_sheet.json").read_text(encoding="utf-8"))
BEATS = {b["beat_id"]: b for b in SHEET["beats"]}
FONTS = Path.home() / "brutalist.art" / "runtime" / "fonts"
SERIF_TTF = FONTS / "EB_Garamond" / "static" / "EBGaramond-Regular.ttf"
MONO_TTF = FONTS / "PT_Mono" / "PTMono-Regular.ttf"
SERIF, MONO = "EB Garamond", "PT Mono"

BG = ManimColor("#F2F0E9")
INK = ManimColor("#3D3929")
ACCENT = ManimColor("#D97757")      # marks only (rules, boxes, strikes)
ACCENT_TEXT = ManimColor("#A44A32")  # accent glyphs: 5.11:1 on cream (WCAG AA)
CARD = ManimColor("#FFFFFF")

SRC = SHEET["metadata"]["evidence"]["labels"]["printed"]
TOTALS = SHEET["metadata"]["evidence"]["labels"]["totals"]
HAND = SHEET["metadata"]["evidence"]["labels"]["by_hand"]
SRC2 = SHEET["metadata"]["evidence"]["labels"]["printed_0927"]
ROUND = SHEET["metadata"]["evidence"]["labels"]["rounded"]

SAFE_W = 12.8          # 14.22 frame width minus 5% insets
SAFE_BOTTOM = -3.6


def tex(s, size=60, color=INK):
    return MathTex(s, font_size=size, color=color)


def serif(s, size=40, color=INK, **kw):
    return Text(s, font=SERIF, font_size=size, color=color, **kw)


def mono(s, size=34, color=INK):
    return Text(s, font=MONO, font_size=size, color=color)


def label(s, size=24):
    return serif(s, size=size, color=INK).set_opacity(0.8)


def fit(m, width=SAFE_W):
    if m.width > width:
        m.scale_to_fit_width(width)
    return m


def split_fraction(eq):
    """Numerator / denominator glyphs of a MathTex fraction, by position."""
    parts = eq.family_members_with_points()
    bar = max(parts, key=lambda g: g.width / max(g.height, 1e-3))
    x0, x1, cy = bar.get_left()[0], bar.get_right()[0], bar.get_center()[1]
    inside = [g for g in parts if g is not bar and x0 - 0.02 <= g.get_x() <= x1 + 0.02]
    num = sorted([g for g in inside if g.get_center()[1] > cy], key=lambda g: g.get_x())
    den = sorted([g for g in inside if g.get_center()[1] < cy], key=lambda g: g.get_x())
    return num, den


class Beat(Scene):
    BID = ""

    def setup(self):
        self.camera.background_color = BG
        beat = BEATS[self.BID]
        self.dur = float(beat["actual_duration_s"])
        self.speech = self.dur - float(beat.get("gap_padded_s", 0.0))
        self.text = beat.get("narration_text") or ""
        self.clock = 0.0

    def when(self, phrase):
        if isinstance(phrase, (int, float)):
            return self.dur * phrase
        i = self.text.find(phrase)
        assert i >= 0, f"{self.BID}: phrase not in narration: {phrase!r}"
        return self.speech * i / max(len(self.text), 1)

    def at(self, phrase):
        t = self.when(phrase)
        if t > self.clock + 1e-3:
            self.wait(t - self.clock)
            self.clock = t

    def go(self, *anims, run_time=0.6):
        self.play(*anims, run_time=run_time)
        self.clock += run_time

    def finish(self):
        if self.dur - self.clock > 1e-3:
            self.wait(self.dur - self.clock)

    def construct(self):
        with register_font(str(SERIF_TTF)), register_font(str(MONO_TTF)):
            self.build()


def source_label(text=SRC):
    return label(text).to_corner(DL, buff=0.95)   # inside the 5% title-safe inset


class TitleCard(Beat):
    BID = "B00"

    def build(self):
        t1 = serif("Why subtracting the max", size=92)
        t2 = serif("changes nothing that matters", size=92)
        title = fit(VGroup(t1, t2).arrange(DOWN, buff=0.45), 12.0)
        rule = Line(LEFT * 1.6, RIGHT * 1.6, color=ACCENT, stroke_width=6)
        sub = serif("Nishant · INFO 7375 Week 1", size=54).set_opacity(0.85)
        g = VGroup(title, rule, sub).arrange(DOWN, buff=1.0).move_to(ORIGIN)
        self.add(g)
        self.finish()


class OverflowOpen(Beat):
    BID = "B01"

    def build(self):
        head = serif("Recorded output · maxsub_runs.py", size=30).set_opacity(0.8)
        l1 = mono("naive (no max-subtraction):", size=36)
        l2 = mono("OverflowError: math range error", size=40, color=ACCENT_TEXT)
        body = VGroup(l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        card = RoundedRectangle(width=max(body.width, head.width) + 1.4, height=body.height + head.height + 1.6,
                                corner_radius=0.2, fill_color=CARD, fill_opacity=1,
                                stroke_color=INK, stroke_width=1.5)
        VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(card)
        g = VGroup(card, head, body)
        fit(g, 11.5).move_to(UP * 0.6)
        fix = serif("The fix: one subtraction.", size=52).next_to(card, DOWN, buff=0.7)
        self.add(card, head, source_label())
        self.go(AddTextLetterByLetter(l1), run_time=1.0)
        self.at("and it crashes")
        self.go(AddTextLetterByLetter(l2), run_time=1.0)
        self.at("The fix is one subtraction")
        self.go(FadeIn(fix, shift=UP * 0.2))
        self.finish()


class SoftmaxDefinition(Beat):
    BID = "B02"

    def build(self):
        heading = serif("Softmax: scores to probabilities", 52).move_to(UP * 2.9)
        scores = tex(r"z = [1,\ 2,\ 3]", 80)
        cap1 = serif("one score per option", 34).set_opacity(0.8)
        VGroup(scores, cap1).arrange(DOWN, buff=0.25).move_to([-3.4, 0.9, 0])
        result = fit(tex(r"p = [0.090,\ 0.245,\ 0.665]", 64), 5.6).move_to([-3.4, -1.3, 0])
        formula = fit(tex(r"p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}", 130), 5.4).move_to([3.0, -0.3, 0])
        num, den = split_fraction(formula)
        self.add(heading)
        self.at("gives each option a score")
        self.go(Write(scores), FadeIn(cap1))
        self.at("Softmax turns scores")
        self.go(Write(formula), run_time=1.2)
        self.at("raise e")
        self.go(*[g.animate.set_color(ACCENT_TEXT) for g in num])
        self.at("then divide by the total")
        self.go(*[g.animate.set_color(INK) for g in num], *[g.animate.set_color(ACCENT_TEXT) for g in den])
        self.at("For scores one, two, three")
        self.go(*[g.animate.set_color(INK) for g in den])
        self.at("that gives")
        self.go(Write(result), FadeIn(source_label()), run_time=1.0)
        self.finish()


class RawPath(Beat):
    BID = "B03"

    def build(self):
        r1 = tex(r"e^{1},\ e^{2},\ e^{3} = 2.718,\ 7.389,\ 20.086", 64)
        r2 = tex(r"\text{total} = 30.193", 64)
        r3 = fit(tex(r"\frac{2.718}{30.193},\ \frac{7.389}{30.193},\ \frac{20.086}{30.193}"
                     r" = 0.090,\ 0.245,\ 0.665", 64))
        rows = VGroup(r1, r2, r3).arrange(DOWN, buff=1.05).move_to(UP * 0.35)
        tl = label(TOTALS, 26).next_to(r2, DOWN, buff=0.2)
        self.go(Write(r1), FadeIn(source_label()), run_time=1.0)
        self.at("Divide each by their total")
        self.go(Write(r2), FadeIn(tl))
        self.at("and you get those")
        self.go(Write(r3), run_time=1.0)
        self.finish()


class ShiftedPathSideBySide(Beat):
    BID = "B04"

    def build(self):
        shift = tex(r"[1,\ 2,\ 3] - 3 = [-2,\ -1,\ 0]", 64)
        h_raw = serif("Raw", 40)
        h_sh = serif("Shifted", 40, color=INK)
        rows = [
            (tex(r"e^{z}", 48), tex(r"2.718,\ 7.389,\ 20.086", 52), tex(r"0.135,\ 0.368,\ 1.000", 52)),
            (tex(r"\text{total}", 48), tex(r"30.193", 52), tex(r"1.503", 52)),
            (tex(r"p", 48), tex(r"0.090,\ 0.245,\ 0.665", 52), tex(r"0.090,\ 0.245,\ 0.665", 52)),
        ]
        xs = (-5.7, -2.0, 3.4)
        y0 = 0.35
        h_raw.move_to([xs[1], y0 + 1.0, 0])
        h_sh.move_to([xs[2], y0 + 1.0, 0])
        for k, row in enumerate(rows):
            for x, m in zip(xs, row):
                m.move_to([x, y0 - 1.05 * k, 0])
        shift.move_to([0, 2.75, 0])
        sep = Line([0.7, y0 + 1.4, 0], [0.7, y0 - 2.7, 0], color=INK, stroke_width=1.5).set_opacity(0.5)
        tl = label(TOTALS, 24).move_to([xs[2], y0 - 3.0, 0])
        raw_col = VGroup(h_raw, *[r[0] for r in rows], *[r[1] for r in rows])
        one = rows[0][2][0][-5:]  # "1.000"
        self.add(raw_col, source_label())
        self.at("Now subtract")
        self.go(Write(shift), run_time=1.0)
        self.at("The in-between numbers")
        self.go(FadeIn(h_sh), Create(sep), Write(rows[0][2]), Write(rows[1][2]), FadeIn(tl), run_time=1.0)
        self.at("exactly one")
        self.go(one.animate.set_color(ACCENT_TEXT))
        self.at("But the final")
        box_l = SurroundingRectangle(rows[2][1], color=ACCENT, buff=0.18)
        box_r = SurroundingRectangle(rows[2][2], color=ACCENT, buff=0.18)
        self.go(one.animate.set_color(INK), Write(rows[2][2]))
        self.go(Create(box_l), Create(box_r))
        self.finish()


class ShiftInvariance(Beat):
    BID = "B05"

    def build(self):
        row1 = MathTex(r"\frac{e^{z_i - m}}{\sum_j e^{z_j - m}}",
                       r"= \frac{e^{-m}\, e^{z_i}}{e^{-m} \sum_j e^{z_j}}",
                       font_size=84, color=INK)
        row2 = MathTex(r"= \frac{e^{z_i}}{\sum_j e^{z_j}}", font_size=84, color=INK)
        row1.move_to(UP * 1.1)
        row2.next_to(row1[1], DOWN, buff=0.8, aligned_edge=LEFT)
        note = serif("m is any constant; the code uses m = max score", 30).set_opacity(0.8)
        note.to_edge(DOWN, buff=0.6)
        num, den = split_fraction(row1[1])
        cancel = VGroup(*num[:3], *den[:3])
        strikes = VGroup(*[Line(VGroup(*grp).get_corner(DL), VGroup(*grp).get_corner(UR),
                                color=ACCENT, stroke_width=6)
                           for grp in (num[:3], den[:3])])
        self.go(Write(row1[0]), FadeIn(note), run_time=1.0)
        self.at("multiplies the top")
        self.go(Write(row1[1]), run_time=1.2)
        self.at("e to the minus m")
        self.go(*[g.animate.set_color(ACCENT_TEXT) for g in cancel])
        self.at("and it cancels")
        self.go(Create(strikes))
        self.at("Softmax only cares")
        self.go(Write(row2), run_time=1.0)
        self.finish()


class OverflowVsShifted(Beat):
    BID = "B06"

    def build(self):
        z = tex(r"z = [1000,\ 1000]", 72).move_to(UP * 2.6)
        hl = serif("Directly", 40).move_to([-3.4, 1.0, 0])
        hr = serif("Subtract the max", 40).move_to([3.4, 1.0, 0])
        sep = Line([0, 1.05, 0], [0, -3.1, 0], color=INK, stroke_width=1.5).set_opacity(0.5)
        e1000 = tex(r"e^{1000}", 80).move_to([-3.4, -0.2, 0])
        err = mono("OverflowError:", 42, color=ACCENT_TEXT)
        err2 = mono("math range error", 42, color=ACCENT_TEXT)
        errg = VGroup(err, err2).arrange(DOWN, buff=0.15).move_to([-3.4, -1.7, 0])
        errl = label(SRC, 22).next_to(errg, DOWN, buff=0.35)
        steps = tex(r"[0,\ 0] \rightarrow [1,\ 1]", 72).move_to([3.4, -0.2, 0])
        stepl = label(HAND, 22).next_to(steps, DOWN, buff=0.25)
        half = tex(r"\rightarrow [0.5,\ 0.5]", 72).move_to([3.4, -1.8, 0])
        halfl = label(SRC, 22).next_to(half, DOWN, buff=0.25)
        brace = Brace(z[0][3:12], DOWN, color=INK)
        shared = serif("shared by both", 30).next_to(brace, DOWN, buff=0.1)
        self.go(Write(z))
        self.at("Done directly")
        self.go(FadeIn(hl), FadeIn(hr), Create(sep), Write(e1000))
        self.at("overflows")
        self.go(FadeIn(errg), FadeIn(errl))
        self.at("Subtract the max")
        self.go(Write(steps), FadeIn(stepl), run_time=1.0)
        self.at("then fifty-fifty")
        self.go(Write(half), FadeIn(halfl))
        self.at("The thousand was shared")
        self.go(FadeOut(hl), FadeOut(hr), run_time=0.3)
        self.go(GrowFromCenter(brace), FadeIn(shared))
        self.finish()


class GapNotSize(Beat):
    BID = "B06B"

    def build(self):
        r2 = tex(r"[1000,\ 1001] - 1001 = [-1,\ 0]", 72).move_to(UP * 2.5)
        r2l = label(HAND, 24).next_to(r2, DOWN, buff=0.2)
        la = tex(r"[1000,\ 1001]", 68).move_to([-3.6, -0.5, 0])
        lb = tex(r"[0,\ 1]", 68).move_to([-3.6, -1.9, 0])
        qa = tex(r"\rightarrow\ p = \,?", 68)
        qb = tex(r"\rightarrow\ p = \,?", 68)
        pa = tex(r"\rightarrow\ p = [0.269,\ 0.731]", 68).move_to([1.8, -0.5, 0])
        pb = tex(r"\rightarrow\ p = [0.269,\ 0.731]", 68).move_to([1.8, -1.9, 0])
        qa.align_to(pa, LEFT).match_y(pa)
        qb.align_to(pb, LEFT).match_y(pb)
        gap = serif("gap of 1 in both", 38).next_to(VGroup(la, lb), DOWN, buff=0.45)
        pl = VGroup(label(SRC2, 24), label(ROUND, 24)).arrange(DOWN, aligned_edge=RIGHT, buff=0.12)
        pl.align_to(pa, RIGHT).match_y(gap)
        box_a = SurroundingRectangle(pa[0][3:], color=ACCENT, buff=0.15)
        box_b = SurroundingRectangle(pb[0][3:], color=ACCENT, buff=0.15)
        self.at("It isn't just ties")
        self.go(FadeIn(la), FadeIn(qa), FadeIn(lb), FadeIn(qb))
        self.at("become minus one and zero")
        self.go(Write(r2), FadeIn(r2l), run_time=1.0)
        self.at("The result matches")
        self.go(ReplacementTransform(qa, pa), run_time=0.8)
        self.go(ReplacementTransform(qb, pb), FadeIn(pl), run_time=0.8)
        self.at("Same gap")
        self.go(FadeIn(gap), Create(box_a), Create(box_b))
        self.finish()


class LastDigit(Beat):
    BID = "B07"

    def build(self):
        a = mono("0.09003057317038045", 60)
        b = mono("0.09003057317038046", 60)
        la = serif("raw", 40).set_opacity(0.85)
        lb = serif("shifted", 40).set_opacity(0.85)
        nums = VGroup(a, b).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        labs = VGroup(la, lb)
        la.next_to(a, LEFT, buff=0.6)
        lb.next_to(b, LEFT, buff=0.6)
        VGroup(nums, labs).move_to(UP * 0.3)
        self.add(nums, labs, source_label())
        self.at("differ in the last digit")
        box = SurroundingRectangle(VGroup(a[-1], b[-1]), color=ACCENT, buff=0.12)
        self.go(a[-1].animate.set_color(ACCENT_TEXT), b[-1].animate.set_color(ACCENT_TEXT), Create(box))
        self.finish()


class Limits(Beat):
    BID = "B08"

    def build(self):
        head = serif("What this does not show", 68)
        lines = [fit(serif(s, 44), 11.5) for s in (
            "One passing test covers one case.",
            "Not proof of stability for every input.",
            "Not a change in what the model prefers, or whether it's right.")]
        body = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        rule = Line(LEFT * 1.0, RIGHT * 1.0, color=ACCENT, stroke_width=5)
        g = VGroup(head, rule, body).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        rule.align_to(head, LEFT)
        body.align_to(head, LEFT)
        g.move_to(UP * 0.2)
        self.add(head, rule)
        for ln, phrase in zip(lines, ("one passing test", "stable for every input", "what the model prefers")):
            self.at(phrase)
            self.go(FadeIn(ln, shift=RIGHT * 0.2))

        # the [0, -1000] example (printed 2026-09-27)
        hl = serif("Printed", 36).set_opacity(0.85).move_to([-3.4, 1.35, 0])
        hr = serif("True value", 36).set_opacity(0.85).move_to([3.4, 1.35, 0])
        sep = Line([0, 1.6, 0], [0, -1.9, 0], color=INK, stroke_width=1.5).set_opacity(0.5)
        z = tex(r"z = [0,\ -1000]", 60).move_to([-3.4, 0.5, 0])
        ex = VGroup(mono("math.exp(-1000)", 36), tex(r"= 0.0", 60)).arrange(RIGHT, buff=0.25).move_to([-3.4, -0.35, 0])
        pr = tex(r"p = [1.0,\ 0.0]", 60).move_to([-3.4, -1.2, 0])
        prl = label(SRC2, 22).next_to(pr, DOWN, buff=0.25)
        tv = tex(r"\frac{e^{-1000}}{1 + e^{-1000}} > 0", 64).move_to([3.4, -0.35, 0])
        tvl = label("From the formula, not printed output.", 22).next_to(tv, DOWN, buff=0.3)
        punch = serif("Prevents overflow, not rounding.", 54, color=ACCENT_TEXT).move_to(DOWN * 2.75)
        self.at("For example")
        top = VGroup(head, rule)
        self.go(FadeOut(body), top.animate.scale(0.8).to_edge(UP, buff=0.55), run_time=0.6)
        self.go(FadeIn(hl), FadeIn(hr), Create(sep), Write(z), run_time=0.6)
        self.at("the smaller option")
        self.go(FadeIn(ex), run_time=0.5)
        self.at("comes out as exactly zero")
        self.go(Write(pr), FadeIn(prl), run_time=0.6)
        self.at("Its true value")
        self.go(Write(tv), FadeIn(tvl), run_time=0.8)
        self.at("The subtraction prevents")
        self.go(FadeIn(punch, shift=UP * 0.2))
        self.finish()
