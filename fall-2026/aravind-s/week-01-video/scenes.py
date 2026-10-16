"""Manim scenes for "Three Scores Are Not Yet Three Chances" (INFO 7375, Week 1).

One Scene per beat, B00..B08. Every number on screen is copied from
evidence/softmax_steps_output.txt and evidence/main_py_output.txt, which were
printed by the lesson's own probabilities() (Python 3.12.14). The scores
[1, 2, 3] and [-1, 2, 3] are constructed inputs, chosen by hand.

Timing is audio-first: each scene reads its beat's measured narration length
from beat_sheet.json and word start times from mp3/words.json, so a value
appears when the narrator says it. If those files are missing (for example,
the toolkit's render-free static check copies this file alone), events fall
back to fixed fractions of the beat.
"""
import json
import re
from pathlib import Path

from manim import *

HERE = Path(__file__).resolve().parent


def _load(rel):
    try:
        return json.loads((HERE / rel).read_text())
    except Exception:
        return None


_SHEET = _load("beat_sheet.json")
_WORDS = _load("mp3/words.json")
_FALLBACK_DUR = {"B00": 13.48, "B01": 11.07, "B02": 17.09, "B03": 14.27,
                 "B04": 22.31, "B05": 20.50, "B06": 20.31, "B07": 20.20,
                 "B08": 12.59}


def dur(bid):
    for beat in (_SHEET or {}).get("beats", []):
        if beat.get("beat_id") == bid and beat.get("actual_duration_s"):
            return float(beat["actual_duration_s"])
    return _FALLBACK_DUR[bid]


def _norm(word):
    return re.sub(r"[^a-z0-9']", "", word.lower())


def at(bid, phrase, frac, nth=1):
    """Seconds into beat `bid` when `phrase` starts (word clock), else frac*dur."""
    if _WORDS:
        words = _WORDS.get("beats", {}).get(bid, [])
        fps = _WORDS.get("fps", 24)
        toks = [_norm(w["text"]) for w in words]
        target = [_norm(p) for p in phrase.split()]
        seen = 0
        for i in range(len(toks) - len(target) + 1):
            if toks[i:i + len(target)] == target:
                seen += 1
                if seen == nth:
                    return words[i]["startFrame"] / fps
    return frac * dur(bid)


class Clock:
    """Plays animations at word times and holds the last frame to the beat end."""

    def __init__(self, scene, bid):
        self.scene, self.bid, self.t = scene, bid, 0.0

    def until(self, when):
        gap = when - self.t
        if gap > 0.02:
            self.scene.wait(gap)
            self.t += gap

    def play(self, *anims, rt=0.6, when=None):
        if when is not None:
            self.until(when)
        self.scene.play(*anims, run_time=rt)
        self.t += rt

    def finish(self):
        self.until(dur(self.bid))


# ---- palette: Claude-style cream stage, warm ink, one terracotta accent ----
BG = "#FAF9F5"
INK = "#3D3929"
SOFT = "#5F5A4B"
ACC = "#A44A32"      # accent for shapes: toolkit Gate T reads solid #D97757 bars/arrowheads as low-contrast text
ACC_T = "#A44A32"    # accent for text, 5.5:1 on BG
BRAND = "#D97757"    # Claude terracotta, used only for the period on the recap title
GOOD = "#3F6E4E"
PALE = "#F1EADF"
SERIF = "EB Garamond"
MONO = "Menlo"
XL, XR = -6.1, 6.1  # safe-area x anchors (not the Manim LEFT/RIGHT vectors)


def T(s, size=40, color=INK, font=SERIF, maxw=11.9):
    t = Text(s, font=font, font_size=size, color=color)
    if t.width > maxw:
        t.scale_to_fit_width(maxw)
    return t


def M(s, size=40, color=INK, maxw=11.9):
    return T(s, size, color, MONO, maxw)


def left_at(mob, x, y):
    mob.move_to([x + mob.width / 2, y, 0])
    return mob


def right_at(mob, x, y):
    mob.move_to([x - mob.width / 2, y, 0])
    return mob


def chrome(scene, title, foot_left, foot_right):
    scene.camera.background_color = BG
    kicker = left_at(M("SOFTMAX · SCORES TO CHANCES", 22, SOFT), XL, 3.2)
    head = left_at(T(title, 50, INK), XL, 2.55)
    fl = left_at(M(foot_left, 20, SOFT, maxw=8.9), XL, -3.2)
    fr = right_at(M(foot_right, 20, SOFT, maxw=3.0), XR, -3.2)
    group = VGroup(kicker, head, fl, fr)
    scene.add(group)
    return group


def baseline(mob, y, i=0):
    """Shift `mob` so glyph i (a letter that sits on the line) rests on y."""
    return mob.shift((y - mob[i].get_bottom()[1]) * UP)


def frame(mob, buff=0.1, color=ACC, width=4):
    """A plain rectangle around `mob` (edges stay clear of the text inside)."""
    rect = Rectangle(width=mob.width + 2 * buff, height=mob.height + 2 * buff,
                     color=color, stroke_width=width)
    return rect.move_to(mob.get_center())


def bar(p, x0, y, scale, height=0.42):
    rect = Rectangle(width=max(p * scale, 0.04), height=height,
                     stroke_width=0, fill_color=ACC, fill_opacity=1)
    return left_at(rect, x0, y)


class B00_ThreeScores(Scene):
    def construct(self):
        bid = "B00"
        c = Clock(self, bid)
        chrome(self, "Three scores",
               "narration: synthetic Kokoro voice (am_onyx), not the author",
               "1 / 9")
        items = []
        for i, x in enumerate([-4.1, 0.0, 4.1]):
            card = RoundedRectangle(width=3.3, height=2.7, corner_radius=0.18,
                                    stroke_color=INK, stroke_width=3,
                                    fill_color=PALE, fill_opacity=1)
            card.move_to([x, 0.35, 0])
            num = M(str(i + 1), 110, INK).move_to([x, 0.62, 0])
            lab = T(f"outcome {i}", 34, SOFT).move_to([x, -0.55, 0])
            items.append(VGroup(card, num, lab))
        c.play(LaggedStart(*[FadeIn(g, shift=0.3 * UP) for g in items],
                           lag_ratio=0.35), rt=1.0, when=at(bid, "one", 0.06))
        tag = T("constructed input: I chose these by hand. No model produced them.",
                34, ACC_T).move_to([0, -1.85, 0])
        rule = Line([-5.75, -2.25, 0], [5.75, -2.25, 0], color=ACC, stroke_width=4)
        c.play(FadeIn(tag), Create(rule), rt=0.5, when=at(bid, "picked", 0.16))
        q = T("Are these three chances?", 52, INK)
        ny = T("Not yet.", 52, ACC_T)
        line = VGroup(q, ny).arrange(RIGHT, buff=0.5).move_to([0, -1.9, 0])
        baseline(ny, q[0].get_bottom()[1])
        c.play(FadeOut(tag), FadeOut(rule), rt=0.3, when=at(bid, "tempting", 0.74))
        c.play(FadeIn(q), rt=0.5)
        c.play(FadeIn(ny, shift=0.2 * LEFT), Create(frame(line, 0.22)), rt=0.4,
               when=at(bid, "not yet", 0.91))
        c.finish()


class B01_Overview(Scene):
    def construct(self):
        bid = "B01"
        c = Clock(self, bid)
        chrome(self, "The whole idea",
               "overview: the first framing is typed, then corrected", "2 / 9")
        a = left_at(T("Three scores", 56, INK), -6.0, 1.15)
        wrong = T("are three chances.", 56, INK)
        baseline(wrong.next_to(a, RIGHT, buff=0.3), a[0].get_bottom()[1])
        right = T("only rank three outcomes.", 56, INK)
        baseline(right.next_to(a, RIGHT, buff=0.3), a[0].get_bottom()[1])
        c.play(AddTextLetterByLetter(a), rt=0.3)
        c.play(AddTextLetterByLetter(wrong), rt=0.35)
        c.play(wrong.animate.set_color(ACC_T), rt=0.15)
        c.play(FadeOut(wrong), rt=0.2)
        c.play(AddTextLetterByLetter(right), rt=0.5)
        l2 = left_at(T("To get chances: exponentiate the gaps,", 46, INK), -6.0, -0.1)
        l3 = left_at(T("then divide by the total.", 46, INK), -6.0, -0.85)
        c.play(AddTextLetterByLetter(l2), rt=0.9, when=at(bid, "exponentiate", 0.29))
        c.play(AddTextLetterByLetter(l3), rt=0.6, when=at(bid, "then divide", 0.44))
        l4 = left_at(T("... and it has a limit.", 44, ACC_T), -6.0, -2.05)
        c.play(FadeIn(l4, shift=0.2 * UP), rt=0.5, when=at(bid, "limit", 0.86))
        c.finish()


class B02_DivideBySix(Scene):
    def construct(self):
        bid = "B02"
        c = Clock(self, bid)
        chrome(self, "Why not just divide by the sum?",
               "divide-by-sum is NOT the lesson's rule; shown for contrast only",
               "3 / 9")
        ys = [1.3, 0.05, -1.2]
        inputs = ["[1, 2, 3]", "[-1, 2, 3]", "[-1, 0, 1]"]
        ops = ["÷ 6", "÷ 4", "÷ 0"]
        rows = [VGroup(left_at(M(s, 36), -6.0, y), left_at(M(o, 36), -2.8, y))
                for s, o, y in zip(inputs, ops, ys)]
        r1 = left_at(M("[0.1667, 0.3333, 0.5000]", 36), -1.4, ys[0])
        r2 = VGroup(M("[", 36), M("-0.2500", 36), M(", 0.5000, 0.7500]", 36))
        r2.arrange(RIGHT, buff=0.04)
        left_at(r2, -1.4, ys[1])
        r3 = left_at(M("ZeroDivisionError", 36, ACC_T), -1.4, ys[2])
        s1 = left_at(T("sums to 1. Looks fine.", 30, GOOD), -1.4, ys[0] - 0.6)
        s2 = left_at(T("a chance below zero", 30, ACC_T), -1.4, ys[1] - 0.6)
        s3 = left_at(T("no answer at all", 30, ACC_T), -1.4, ys[2] - 0.6)
        def under(mob, color):
            rule = Line(ORIGIN, RIGHT, color=color, stroke_width=5)
            rule.match_width(mob)
            return rule.next_to(mob, DOWN, buff=0.1)
        need = left_at(T("We need a rule that survives any finite score.", 40, INK),
                       -6.0, -2.55)
        c.play(FadeIn(rows[0]), rt=0.5, when=at(bid, "divide by the sum", 0.06))
        c.play(FadeIn(r1, shift=0.2 * RIGHT), rt=0.5, when=at(bid, "sixth", 0.28))
        c.play(FadeIn(s1), Create(under(r1, GOOD)), rt=0.4, when=at(bid, "fine", 0.37))
        c.play(FadeIn(rows[1]), rt=0.5, when=at(bid, "minus one", 0.5))
        c.play(FadeIn(r2, shift=0.2 * RIGHT), rt=0.5, when=at(bid, "three gives", 0.56))
        c.play(Create(under(r2[1], ACC)), FadeIn(s2), rt=0.5, when=at(bid, "below zero", 0.59))
        c.play(FadeIn(rows[2]), rt=0.5, when=at(bid, "minus one", 0.66, nth=2))
        c.play(FadeIn(r3), FadeIn(s3), Create(under(r3, ACC)), rt=0.5, when=at(bid, "divides", 0.74))
        c.play(FadeIn(need, shift=0.2 * UP), rt=0.6, when=at(bid, "survive", 0.88))
        c.finish()


CODE = [
    (0, "def probabilities(logits, temperature=1.0):"),
    (4, "...  # lines 10-13: input checks (not shown)"),
    (4, "peak = max(logits)"),
    (4, "weights = [math.exp((x - peak) / temperature) for x in logits]"),
    (4, "total = sum(weights)"),
    (4, "return [weight / total for weight in weights]"),
]


class B03_RealCode(Scene):
    def construct(self):
        bid = "B03"
        c = Clock(self, bid)
        chrome(self, "The lesson's actual function",
               "lessons/01-randomness-and-first-prompts/code/main.py, lines 9-17",
               "4 / 9")
        size = 24
        cw = M("M" * 20, size, maxw=100).width / 20
        lines = VGroup()
        for k, (indent, src) in enumerate(CODE):
            color = SOFT if src.startswith("...") else INK
            line = M(src, size, color, maxw=100).align_to(ORIGIN, LEFT)
            lines.add(line.shift(indent * cw * RIGHT + k * 0.56 * DOWN))
        if lines.width > 11.2:          # one uniform scale keeps the indentation true
            lines.scale_to_fit_width(11.2)
        lines.move_to([0, 0.25, 0])
        panel = RoundedRectangle(width=lines.width + 0.6, height=lines.height + 0.5,
                                 corner_radius=0.15, stroke_color=SOFT, stroke_width=2,
                                 fill_color=PALE, fill_opacity=1)
        panel.move_to(lines.get_center())
        c.play(FadeIn(panel), FadeIn(lines), rt=0.8)
        steps = [
            (lines[2], "Find the largest", 0.21, "move 1: subtract the largest score from every score"),
            (lines[3], "Exponentiate", 0.43, "move 2: exponentiate each result (every weight > 0)"),
            (VGroup(lines[4], lines[5]), "divide every", 0.55, "move 3: divide every weight by the total"),
        ]
        box = caption = None
        for target, phrase, frac, text in steps:
            new_box = frame(target, 0.06)
            new_cap = left_at(T(text, 36, INK), -6.0, -2.05)
            when = at(bid, phrase, frac)
            if box is None:
                c.play(Create(new_box), FadeIn(new_cap), rt=0.5, when=when)
            else:
                c.play(ReplacementTransform(box, new_box), FadeOut(caption), rt=0.4, when=when)
                c.play(FadeIn(new_cap), rt=0.3)
            box, caption = new_box, new_cap
        temp = left_at(T("temperature = 1.0 in every example in this video", 30, SOFT),
                       -6.0, -2.65)
        c.play(FadeIn(temp), rt=0.5, when=at(bid, "temperature", 0.69))
        c.finish()


def column(values, x, ys, size=38, color=INK):
    return VGroup(*[M(v, size, color).move_to([x, y, 0]) for v, y in zip(values, ys)])


class B04_WorkedExample(Scene):
    def construct(self):
        bid = "B04"
        c = Clock(self, bid)
        chrome(self, "Worked example: [1, 2, 3]",
               "real output: probabilities([1, 2, 3]), Python 3.12.14, 4 places",
               "5 / 9")
        ys = [0.95, 0.2, -0.55]
        xs = [-5.2, -2.75, 0.0, 2.75]
        heads = [baseline(T(h, 32, SOFT).move_to([x, 1.75, 0]), 1.62)
                 for h, x in zip(["score", "minus peak", "weight = exp", "chance"], xs)]
        sc = column(["1", "2", "3"], xs[0], ys)
        mp = column(["-2", "-1", "0"], xs[1], ys)
        wt = column(["0.1353", "0.3679", "1.0000"], xs[2], ys)
        ch = column(["0.0900", "0.2447", "0.6652"], xs[3], ys)
        bars = [bar(p, 4.0, y, 2.2) for p, y in zip([0.0900, 0.2447, 0.6652], ys)]
        peak = M("peak = 3", 28, ACC_T).move_to([xs[0], -1.45, 0])
        c.play(FadeIn(heads[0]), rt=0.3, when=at(bid, "run it", 0.0))
        for k, word in enumerate(["one", "two", "three"]):
            c.play(FadeIn(sc[k], shift=0.15 * UP), rt=0.2, when=at(bid, word, 0.03 + 0.02 * k))
        c.play(FadeIn(heads[1]), FadeIn(peak), rt=0.4, when=at(bid, "subtract the peak", 0.07))
        for k, (phrase, nth) in enumerate([("minus two", 1), ("minus one", 1), ("and zero", 1)]):
            c.play(FadeIn(mp[k], shift=0.15 * UP), rt=0.25, when=at(bid, phrase, 0.15 + 0.04 * k, nth))
        c.play(FadeIn(heads[2]), rt=0.3, when=at(bid, "exponentiate", 0.27))
        for k, phrase in enumerate(["zero point one", "zero point three", "exactly one"]):
            c.play(FadeIn(wt[k], shift=0.15 * UP), rt=0.3, when=at(bid, phrase, 0.3 + 0.05 * k))
        pos_box = SurroundingRectangle(wt, color=ACC, buff=0.12, stroke_width=4)
        c.play(Create(pos_box), rt=0.4, when=at(bid, "every weight", 0.45))
        sum_line = Line([-1.0, -1.0, 0], [1.0, -1.0, 0], color=INK, stroke_width=3)
        total = M("total 1.5032", 34, INK).move_to([0.0, -1.45, 0])
        c.play(FadeOut(pos_box), Create(sum_line), rt=0.4, when=at(bid, "add them up", 0.52))
        c.play(FadeIn(total), rt=0.4, when=at(bid, "one point five", 0.56))
        c.play(FadeIn(heads[3]), rt=0.3, when=at(bid, "divide each weight", 0.62))
        for k, phrase in enumerate(["zero point zero nine", "zero point two four", "zero point six six"]):
            c.play(FadeIn(ch[k]), GrowFromEdge(bars[k], LEFT), rt=0.45,
                   when=at(bid, phrase, 0.72 + 0.07 * k))
        badge = M("sum = 1.0000", 32, GOOD).move_to([xs[3], -2.1, 0])
        c.play(FadeIn(badge, shift=0.15 * UP), rt=0.4, when=at(bid, "sum to one", 0.95))
        c.finish()


def hop(a, b, y, label_y, text):
    arrow = Arrow([a.get_right()[0] + 0.12, y, 0], [b.get_left()[0] - 0.12, y, 0],
                  buff=0, color=ACC, stroke_width=5, max_tip_length_to_length_ratio=0.3)
    lab = M(text, 28, ACC_T).move_to([(a.get_right()[0] + b.get_left()[0]) / 2, label_y, 0])
    return arrow, lab


class B05_GapMultiplier(Scene):
    def construct(self):
        bid = "B05"
        c = Clock(self, bid)
        chrome(self, "The gap is a multiplier",
               "real output: neighbour ratios from evidence/softmax_steps.py",
               "6 / 9")
        xs = [-2.6, 0.9, 4.4]
        ya, yb = 1.25, -0.65
        la = left_at(T("weights", 36, SOFT), -6.0, ya)
        lb = left_at(T("chances", 36, SOFT), -6.0, yb)
        wa = VGroup(*[M(v, 48).move_to([x, ya, 0]) for v, x in zip(["0.1353", "0.3679", "1.0000"], xs)])
        wb = VGroup(*[M(v, 48).move_to([x, yb, 0]) for v, x in zip(["0.0900", "0.2447", "0.6652"], xs)])
        c.play(FadeIn(la), LaggedStart(*[FadeIn(m) for m in wa], lag_ratio=0.3), rt=0.9,
               when=at(bid, "each one point step", 0.11))
        hops_a = [hop(wa[0], wa[1], ya, ya + 0.6, "× 2.7183"),
                  hop(wa[1], wa[2], ya, ya + 0.6, "× 2.7183")]
        c.play(*[GrowArrow(h[0]) for h in hops_a], rt=0.5, when=at(bid, "multiplies", 0.17))
        c.play(*[FadeIn(h[1]) for h in hops_a], rt=0.4, when=at(bid, "about two point", 0.24))
        mid = M("all three ÷ 1.5032 (the same total)", 30, INK).move_to([0.9, 0.45, 0])
        c.play(FadeIn(mid), rt=0.5, when=at(bid, "divided by the same", 0.47))
        c.play(FadeIn(lb), LaggedStart(*[FadeIn(m) for m in wb], lag_ratio=0.3), rt=0.9,
               when=at(bid, "so each chance", 0.55))
        hops_b = [hop(wb[0], wb[1], yb, yb + 0.6, "× 2.7183"),
                  hop(wb[1], wb[2], yb, yb + 0.6, "× 2.7183")]
        c.play(*[GrowArrow(h[0]) for h in hops_b], *[FadeIn(h[1]) for h in hops_b], rt=0.6,
               when=at(bid, "times the one below", 0.63))
        gaps = left_at(T("The gaps set the ratios.", 40, INK), -6.0, -1.6)
        c.play(FadeIn(gaps), rt=0.5, when=at(bid, "the gaps set", 0.7))
        contrast = left_at(M("divide by six instead: 0.3333 → 0.5000 is × 1.5000", 28, SOFT),
                           -6.0, -2.35)
        c.play(FadeIn(contrast), rt=0.5, when=at(bid, "divide by six", 0.8))
        c.finish()


class B06_NegativeScores(Scene):
    def construct(self):
        bid = "B06"
        c = Clock(self, bid)
        chrome(self, "The hard case: [-1, 2, 3]",
               "real output: probabilities([-1, 2, 3]), Python 3.12.14, 4 places",
               "7 / 9")
        ghost = left_at(M("divide-by-sum gave -0.2500 for this input: a chance below zero",
                          26, SOFT), -6.0, 1.75)
        ys = [0.35, -0.4, -1.15]
        xs = [-4.6, -1.3, 2.0]
        heads = [baseline(T(h, 32, SOFT).move_to([x, 1.05, 0]), 0.92) for h, x in zip(["score", "weight", "chance"], xs)]
        sc = column(["-1", "2", "3"], xs[0], ys)
        wt = column(["0.0183", "0.3679", "1.0000"], xs[1], ys)
        ch = column(["0.0132", "0.2654", "0.7214"], xs[2], ys)
        bars = [bar(p, 3.4, y, 2.6) for p, y in zip([0.0132, 0.2654, 0.7214], ys)]
        c.play(FadeIn(ghost), rt=0.5, when=0.1)
        c.play(FadeIn(heads[0]), LaggedStart(*[FadeIn(m) for m in sc], lag_ratio=0.3), rt=0.8,
               when=at(bid, "minus one two three", 0.07))
        c.play(FadeIn(heads[1]), LaggedStart(*[FadeIn(m) for m in wt], lag_ratio=0.3), rt=0.8,
               when=at(bid, "tiny positive", 0.27))
        c.play(FadeIn(heads[2]), rt=0.3, when=at(bid, "chances come out", 0.33))
        for k, phrase in enumerate(["zero point zero one", "zero point two six", "zero point seven two"]):
            c.play(FadeIn(ch[k]), GrowFromEdge(bars[k], LEFT), rt=0.45,
                   when=at(bid, phrase, 0.38 + 0.08 * k))
        badge = left_at(M("all positive · sum = 1.0000", 30, GOOD), -6.0, -2.0)
        c.play(FadeIn(badge), rt=0.4, when=at(bid, "all positive", 0.62))
        note = left_at(M("gap of 3 points → × 20.0855 (that is e³)", 30, ACC_T), -6.0, -2.6)
        c.play(FadeIn(note), rt=0.5, when=at(bid, "a gap of three", 0.7))
        boxes = VGroup(SurroundingRectangle(sc[2], color=ACC, buff=0.1, stroke_width=4),
                       SurroundingRectangle(ch[2], color=ACC, buff=0.1, stroke_width=4))
        c.play(Create(boxes), rt=0.5, when=at(bid, "the biggest score", 0.86))
        c.finish()


class B07_WhatItDoesNotProve(Scene):
    def construct(self):
        bid = "B07"
        c = Clock(self, bid)
        chrome(self, "What this does not establish",
               "scores were constructed by hand; the chances describe sampling only",
               "8 / 9")
        head_l = left_at(T("chance of being sampled", 36, INK), -6.0, 1.6)
        ys = [0.85, 0.1, -0.65]
        rows = VGroup()
        for i, (p, y) in enumerate(zip([0.0900, 0.2447, 0.6652], ys)):
            lab = left_at(T(f"outcome {i}", 30, SOFT), -6.0, y)
            b = bar(p, -4.3, y, 4.0)
            val = left_at(M(f"{p:.4f}", 30, INK), -4.3 + p * 4.0 + 0.15, y)
            rows.add(VGroup(lab, b, val))
        c.play(FadeIn(head_l), rt=0.3, when=at(bid, "sampled", 0.15))
        for r in rows:
            c.play(FadeIn(r[0]), FadeIn(r[2]), GrowFromEdge(r[1], LEFT), rt=0.35)
        not_right = left_at(T("is not the chance of being right", 34, ACC_T), -6.0, -1.55)
        c.play(FadeIn(not_right), rt=0.5, when=at(bid, "not chances", 0.28))
        divider = Line([0.25, 1.9, 0], [0.25, -2.5, 0], color=SOFT, stroke_width=2)
        c.play(Create(divider), rt=0.3, when=at(bid, "guarantees", 0.39) - 0.3)
        g_head = left_at(T("Guaranteed (exact math)", 36, GOOD), 0.6, 1.6)
        g_items = [baseline(left_at(T(s, 30, INK), 0.6, y), y - 0.12, 1) for s, y in
                   zip(["+ every chance is positive", "+ they sum to 1", "+ the scores' order is kept"],
                       [1.05, 0.55, 0.05])]
        c.play(FadeIn(g_head), rt=0.4, when=at(bid, "guarantees", 0.39))
        for item, phrase, frac in zip(g_items, ["positive", "sum to one", "order"], [0.41, 0.49, 0.56]):
            c.play(FadeIn(item, shift=0.1 * RIGHT), rt=0.3, when=at(bid, phrase, frac))
        n_head = left_at(T("Not established", 36, ACC_T), 0.6, -0.7)
        n_items = [baseline(left_at(T(s, 30, INK), 0.6, y), y - 0.12, 1) for s, y in
                   zip(["? that the scores were sensible", "? that outcome 2 is true",
                        "? that 0.6652 means 66.5% right"], [-1.25, -1.75, -2.25])]
        c.play(FadeIn(n_head), rt=0.4, when=at(bid, "says nothing", 0.6))
        for item, phrase, frac in zip(n_items, ["sensible", "outcome two", "confident"], [0.68, 0.73, 0.82]):
            c.play(FadeIn(item, shift=0.1 * RIGHT), rt=0.3, when=at(bid, phrase, frac))
        c.finish()


class B08_Recap(Scene):
    def construct(self):
        bid = "B08"
        c = Clock(self, bid)
        self.camera.background_color = BG
        kicker = left_at(M("SOFTMAX · SCORES TO CHANCES", 22, SOFT), XL, 3.2)
        fl = left_at(M("Aravind Sundaravadivelu · INFO 7375 · Fall 2026", 20, SOFT), XL, -3.2)
        fr = right_at(M("synthetic voice: Kokoro", 20, SOFT), XR, -3.2)
        self.add(kicker, fl, fr)
        t1 = left_at(T("Three Scores Are Not Yet", 66, INK), -6.0, 2.2)
        t2 = left_at(T("Three Chances", 66, INK), -6.0, 1.25)
        dot = Dot(radius=0.1, color=BRAND).move_to([t2.get_right()[0] + 0.2, t2.get_bottom()[1] + 0.1, 0])
        c.play(FadeIn(t1), FadeIn(t2), FadeIn(dot), rt=1.0)
        recipe = left_at(T("Exponentiate the gaps. Divide by the total.", 42, INK), -6.0, 0.15)
        c.play(FadeIn(recipe, shift=0.15 * UP), rt=0.5, when=at(bid, "exponentiate", 0.21))
        sub = left_at(T("The order and every ratio survive. Truth is not part of the deal.", 32, SOFT),
                      -6.0, -0.55)
        c.play(FadeIn(sub), rt=0.5, when=at(bid, "keeps the order", 0.47))
        card = RoundedRectangle(width=12.2, height=1.35, corner_radius=0.15, stroke_color=ACC,
                                stroke_width=3, fill_color=PALE, fill_opacity=1).move_to([0, -1.95, 0])
        task1 = left_at(T("Your turn: predict it first, then run it", 34, ACC_T), -5.7, -1.7)
        task2 = left_at(M("probabilities([1, 2, 4])", 34, INK), -5.7, -2.25)
        c.play(FadeIn(card), FadeIn(task1), FadeIn(task2), rt=0.6, when=at(bid, "your turn", 0.64))
        c.finish()
