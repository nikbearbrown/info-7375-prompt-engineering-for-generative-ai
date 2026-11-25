#!/usr/bin/env python3
"""
scene.py -- INFO 7375 Final Project Film (plan)
Swathi Baba Eswarappa

Visual engine for "A Supervised Job-Search Agent with Sponsorship Evidence",
in the four required parts: executive summary, introduction, methods,
evaluation. B05 is completed JS1-JS3 work; everything else is planned.

Eleven Manim scenes, one per beat in beat_sheet.json. Each scene reads its
own runtime from mp3/timings.json (Kokoro durations = ground truth) and pads
itself to match, so picture and narration stay locked without manual nudging.

EVIDENCE RULE
  Every number drawn on screen is read at import time out of data/facts.json.
  Nothing numeric is typed into an animation; check_facts.py fails the build
  if a string literal in this file contains a digit.

LABEL RULE
  Each beat's label is read from beat_sheet.json and drawn top-left. Every
  string drawn is logged to build/onscreen/<beat>.json, and check_labels.py
  fails the build if one is not word for word in that beat's production_viz.
  Planned beats carry a PLANNED badge; B05 carries COMPLETED · JS3; B11's
  PROPOSED TARGETS — NOT RESULTS stays through the sign-off.

Render:  manim -qk --frame_rate 24 scene.py B01_WhatItIs ... (see build.sh)
"""
import json
from pathlib import Path

import numpy as np
import manim as _manim
from manim import *

# the toolkit's Gate A runs construct() against a stub manim with no real
# geometry; the Beat assertions below need real bounding boxes, so they only
# run under real Manim (every actual render)
REAL_MANIM = hasattr(_manim, "__version__")

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- evidence
FACTS = json.loads((ROOT / "data/facts.json").read_text())
N = {k: v["display"] for k, v in FACTS["numbers"].items()}
C = FACTS["commits"]
FOOT = FACTS["footers"]
TIMINGS = json.loads((ROOT / "mp3/timings.json").read_text())
SHEET = json.loads((ROOT / "beat_sheet.json").read_text())
NARRATION = {b["beat_id"]: b["narration_text"] for b in SHEET["beats"]}
LABEL = {b["beat_id"]: b["graphic"]["production_viz"]["label"] for b in SHEET["beats"]}

# ------------------------------------------------------------------ style
BG = "#0B0B0C"
FG = "#F5F3EF"
DIM = "#8A8A90"
AMBER = "#FFB020"
RED = "#FF4D3D"
GREEN = "#3DDC84"
BLUE = "#4FC3F7"
VIOLET = "#B388FF"
MONO = "Menlo"

# chrome sits inside the toolkit's 5% title-safe area (x 96..1824, y 54..1026
# px = +-6.4 x +-3.6 units); Week 1's rules ran to +-6.85 and would bleed
RULE_X = 6.25
RULE_Y = 3.0
# the toolkit's GATE T samples every beat clip at its midpoint; nothing may be
# mid-animation within this many seconds of it
MID_PAD = 0.2

config.background_color = BG

# every string handed to T(), in creation order, for check_labels.py
DRAWN = []


def _visible(m, thresh=0.05):
    """Effective opacity of a mobject, read from the parts actually drawn."""
    parts = m.family_members_with_points()
    if not parts:
        return False
    return max(max(p.get_fill_opacity(), p.get_stroke_opacity())
               for p in parts) >= thresh


class Beat(Scene):
    """Base: draws the persistent brutalist chrome and locks scene length."""

    beat_id = "B00"

    def chrome(self, type_label=False):
        """Rules, the beat-sheet label top-left, beat id top-right, footer.

        With type_label the label is returned unadded, for the scene to type on.
        """
        DRAWN.clear()
        rule_t = Line(LEFT * RULE_X, RIGHT * RULE_X, stroke_width=2,
                      color=DIM).shift(UP * RULE_Y)
        rule_b = Line(LEFT * RULE_X, RIGHT * RULE_X, stroke_width=2,
                      color=DIM).shift(DOWN * RULE_Y)
        lab = T(LABEL[self.beat_id], 17, FG)
        lab.next_to(rule_t, UP, buff=0.12).align_to(rule_t, LEFT)
        tag = T(self.beat_id, 17, DIM)
        tag.next_to(rule_t, UP, buff=0.12).align_to(rule_t, RIGHT)
        mobs = [rule_t, rule_b, lab, tag]
        # provenance: the beat sheet's footer, verbatim, wrapped if it is long
        src = None
        if self.beat_id in FOOT:
            src = wrap(FOOT[self.beat_id], 15, DIM, 2 * RULE_X, buff=0.06)
            src.next_to(rule_b, DOWN, buff=0.12).align_to(rule_b, LEFT)
            mobs.append(src)
        who_s = "S. BABA ESWARAPPA · %s" % N["course"]
        who = Text(who_s, font=MONO, font_size=15, color=DIM)
        if src is None or (len(src) == 1 and
                           src.width + who.width + 0.5 < 2 * RULE_X):
            who = T(who_s, 15, DIM)
            who.next_to(rule_b, DOWN, buff=0.12).align_to(rule_b, RIGHT)
            mobs.append(who)
        self.add(*[m for m in mobs if not (type_label and m is lab)])
        # content must live BETWEEN the rules, not merely inside the frame
        self.chrome_mobs = VGroup(*mobs)
        self.safe_top = rule_t.get_bottom()[1]
        self.safe_bottom = rule_b.get_top()[1]
        return lab

    def play(self, *a, **k):
        if getattr(self, "_first_cue", None) is None:
            self._first_cue = self.renderer.time
        # midpoint guard: an animation that would straddle the clip midpoint
        # waits until just after it, so GATE T reads a settled frame there.
        # wait() is itself play(Wait(...)), so pure waits pass straight through.
        if REAL_MANIM and not all(isinstance(x, Wait) for x in a):
            anims = self.compile_animations(*a, **k)
            t0, rt = self.renderer.time, self.get_run_time(anims)
            mid = TIMINGS[self.beat_id] / 2
            if t0 < mid + MID_PAD and t0 + rt > mid - MID_PAD:
                self.wait(mid + MID_PAD - t0)
            a, k = anims, {}
        out = super().play(*a, **k)
        if not REAL_MANIM:
            return out
        # check after every cue, not just the settled end frame
        self.assert_in_safe_area()
        self.assert_no_text_overlap()
        return out

    def hold_until(self, t):
        """Wait until scene-time `t`, so a cue can be pinned to the narration.

        A wait shorter than one frame writes an empty partial movie, and
        ffmpeg then refuses to combine the scene, so those are skipped.
        """
        dt = t - self.renderer.time
        # Gate A's stub manim has no frame_rate; any positive wait is fine there
        frame = 1.0 / config.frame_rate if REAL_MANIM else 0.0
        if dt > 0 and dt >= frame:
            self.wait(dt)

    def at(self, phrase):
        """Approximate time the narration reaches `phrase`.

        Kokoro gives one duration per beat, not per word, so this interpolates
        by word position. It is accurate to a few tenths of a second, which is
        all a visual cue needs -- and it re-derives itself if the script
        changes, instead of freezing hand-tuned numbers into the animation.
        """
        txt = NARRATION[self.beat_id]
        i = txt.lower().index(phrase.lower())
        return TIMINGS[self.beat_id] * len(txt[:i].split()) / len(txt.split())

    def pin(self, phrase, lead=0.35):
        """Hold until just before `phrase` is spoken, then let the cue play."""
        self.hold_until(max(self.at(phrase) - lead, 0.0))

    def assert_in_safe_area(self):
        """Content must stay between the chrome rules."""
        chrome = set(id(p) for p in self.chrome_mobs.family_members_with_points())
        worst = []
        for m in self.mobjects:
            for p in m.family_members_with_points():
                if id(p) in chrome:
                    continue
                if max(p.get_fill_opacity(), p.get_stroke_opacity()) < 0.05:
                    continue
                t, b = p.get_top()[1], p.get_bottom()[1]
                l, r = p.get_left()[0], p.get_right()[0]
                if (b < self.safe_bottom - 0.02 or t > self.safe_top + 0.02
                        or l < -RULE_X - 0.02 or r > RULE_X + 0.02):
                    worst.append("x[%.2f,%.2f] y[%.2f,%.2f]" % (l, r, b, t))
        if worst:
            raise RuntimeError(
                "%s: %d part(s) outside the safe area -> %s"
                % (self.beat_id, len(worst), sorted(set(worst))[:5]))

    def assert_no_text_overlap(self):
        """Fail if two separate Text mobjects occupy the same space."""
        def texts(m):
            if isinstance(m, Text):
                yield m
            else:
                for sub in m.submobjects:
                    yield from texts(sub)

        vis = []
        for m in self.mobjects:
            for t in texts(m):
                if not _visible(t):
                    continue
                if t.width < 1e-3 or t.height < 1e-3:
                    continue
                if t not in vis:
                    vis.append(t)

        pad = 0.04
        for i in range(len(vis)):
            for j in range(i + 1, len(vis)):
                a, b = vis[i], vis[j]
                if (a.get_left()[0] < b.get_right()[0] - pad
                        and b.get_left()[0] < a.get_right()[0] - pad
                        and a.get_bottom()[1] < b.get_top()[1] - pad
                        and b.get_bottom()[1] < a.get_top()[1] - pad):
                    raise RuntimeError(
                        "%s: text overlap %r x %r"
                        % (self.beat_id, a.text[:28], b.text[:28]))

    def assert_in_frame(self):
        """Fail the render if anything visible sits outside the frame."""
        half_w = config.frame_width / 2 - 0.05
        half_h = config.frame_height / 2 - 0.05
        bad = []
        for m in self.mobjects:
            for p in m.family_members_with_points():
                if max(p.get_fill_opacity(), p.get_stroke_opacity()) < 0.05:
                    continue
                l, r = p.get_left()[0], p.get_right()[0]
                b, t = p.get_bottom()[1], p.get_top()[1]
                if l < -half_w or r > half_w or b < -half_h or t > half_h:
                    bad.append("x[%.2f,%.2f] y[%.2f,%.2f]" % (l, r, b, t))
        if bad:
            raise RuntimeError(
                "%s: %d mobject(s) outside the frame -> %s"
                % (self.beat_id, len(bad), bad[:4]))

    def lock(self):
        """Pad (or accept overrun) so the scene equals its narration."""
        if not REAL_MANIM:
            return self.wait(1)
        self.assert_in_frame()
        self.assert_in_safe_area()
        self.assert_no_text_overlap()
        out = ROOT / "build/onscreen"
        out.mkdir(parents=True, exist_ok=True)
        (out / ("%s.json" % self.beat_id)).write_text(
            json.dumps(DRAWN, ensure_ascii=False, indent=1))
        target = TIMINGS[self.beat_id]
        remaining = target - self.renderer.time
        lead = getattr(self, "_first_cue", None)
        lead = 0.0 if lead is None else lead
        flag = "  <-- DEAD AIR" if lead > 1.2 else ""
        flag += "  <-- LONG HOLD" if remaining > 2.5 else ""
        print("[slack] %-5s lead=%5.2fs  anim_end=%6.2fs  audio=%6.2fs  "
              "trailing=%5.2fs%s"
              % (self.beat_id, lead, self.renderer.time, target, remaining, flag))
        self.wait(max(remaining, 0.08))


# ------------------------------------------------------------- components
def T(s, fs=24, color=FG, max_w=None):
    """Monospace label, shrunk to max_w if it would not fit. Logged."""
    DRAWN.append(s)
    t = Text(s, font=MONO, font_size=fs, color=color)
    if max_w and t.width > max_w:
        t.scale(max_w / t.width)
    return t


def wrap(s, fs, color, max_w, buff=0.1):
    """Left-aligned lines split at spaces, so each line is a piece of `s`."""
    lines, cur = [], []
    for w in s.split(" "):
        trial = " ".join(cur + [w])
        if cur and Text(trial, font=MONO, font_size=fs).width > max_w:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    lines.append(" ".join(cur))
    return VGroup(*[T(l, fs, color) for l in lines]).arrange(
        DOWN, buff=buff, aligned_edge=LEFT)


def frame_box(w, h, color=FG, dashed=False, sw=3):
    r = Rectangle(width=w, height=h, stroke_width=sw, stroke_color=color)
    if dashed:
        return DashedVMobject(r, num_dashes=int((w + h) * 7), dashed_ratio=0.55)
    return r


def label_box(lines, w, h, color=FG, fs=22, dashed=False, sub_color=None):
    """A box with one bold first line and optional dimmer lines under it."""
    box = frame_box(w, h, color, dashed)
    rows = VGroup(*[T(s, fs if i == 0 else fs - 4,
                      color if i == 0 else (sub_color or DIM), max_w=w - 0.3)
                    for i, s in enumerate(lines)])
    rows.arrange(DOWN, buff=0.12).move_to(box)
    return VGroup(box, rows)


def text_rules(w, n, color=DIM, buff=0.22):
    """Grey placeholder lines standing in for text that is not shown."""
    return VGroup(*[Line([0, 0, 0], [w - (0.5 if k % 3 == 2 else 0), 0, 0],
                         stroke_width=2, color=color) for k in range(n)]
                  ).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def doc_icon(w, h, color=FG, lines=5, fold=0.45):
    """A page with a folded corner and a few grey text rules."""
    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
    page = Polygon([x0, y1, 0], [x1 - fold, y1, 0], [x1, y1 - fold, 0],
                   [x1, y0, 0], [x0, y0, 0], stroke_color=color,
                   stroke_width=3, fill_color=BG, fill_opacity=1)
    ear = VMobject(stroke_color=color, stroke_width=2).set_points_as_corners(
        [[x1 - fold, y1, 0], [x1 - fold, y1 - fold, 0], [x1, y1 - fold, 0]])
    rules = VGroup(*[Line([x0 + 0.2, 0, 0], [x1 - 0.2 - (0.3 if k % 3 == 2 else 0), 0, 0],
                          stroke_width=2, color=DIM) for k in range(lines)])
    rules.arrange(DOWN, buff=0.18).move_to([0, -h * 0.12, 0])
    return VGroup(page, ear, rules)


def tick(color=GREEN, s=0.5):
    return VMobject(stroke_color=color, stroke_width=7).set_points_as_corners(
        [[-s * 0.5, 0, 0], [-s * 0.15, -s * 0.38, 0], [s * 0.55, s * 0.45, 0]])


def cross(color=RED, s=0.45):
    return VGroup(Line([-s / 2, -s / 2, 0], [s / 2, s / 2, 0], color=color, stroke_width=7),
                  Line([-s / 2, s / 2, 0], [s / 2, -s / 2, 0], color=color, stroke_width=7))


def strike(t, color=RED):
    return Line(t.get_left() + LEFT * 0.1, t.get_right() + RIGHT * 0.1,
                color=color, stroke_width=5)


def arrow(a, b, color=DIM, sw=3):
    return Arrow(a, b, buff=0.1, stroke_width=sw, color=color,
                 max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=8)


def badge(text, color, fs=20):
    t = T(text, fs, color)
    return VGroup(SurroundingRectangle(t, color=color, stroke_width=2, buff=0.12), t)


def status_badge(text, color):
    """Pinned top-right inside the content area for the whole beat."""
    b = badge(text, color)
    b.move_to([RULE_X - b.width / 2 - 0.05, RULE_Y - b.height / 2 - 0.12, 0])
    return b


def person(color=FG, s=1.0):
    head = Circle(radius=0.38 * s, color=color, stroke_width=4).shift(UP * 0.95 * s)
    body = Line(UP * 0.55 * s, DOWN * 0.55 * s, color=color, stroke_width=4)
    arms = Line(LEFT * 0.6 * s + UP * 0.2 * s, RIGHT * 0.6 * s + UP * 0.2 * s,
                color=color, stroke_width=4)
    legs = VGroup(Line(DOWN * 0.55 * s, DOWN * 1.3 * s + LEFT * 0.45 * s, color=color, stroke_width=4),
                  Line(DOWN * 0.55 * s, DOWN * 1.3 * s + RIGHT * 0.45 * s, color=color, stroke_width=4))
    return VGroup(head, body, arms, legs)


def padlock(color=VIOLET, s=1.0):
    body = Rectangle(width=0.5 * s, height=0.4 * s, stroke_width=4, stroke_color=color,
                     fill_color=color, fill_opacity=0.25)
    shackle = Arc(radius=0.17 * s, start_angle=0, angle=PI, stroke_width=4,
                  color=color).next_to(body, UP, buff=0)
    return VGroup(body, shackle)


def folder(color=FG, s=1.0):
    return Polygon([0, 0, 0], [0.5 * s, 0, 0], [0.5 * s, 0.32 * s, 0], [0.24 * s, 0.32 * s, 0],
                   [0.19 * s, 0.38 * s, 0], [0, 0.38 * s, 0], stroke_color=color, stroke_width=3)


# ==================================================================== B01
class B01_WhatItIs(Beat):
    beat_id = "B01"

    def construct(self):
        lab = self.chrome(type_label=True)
        # the part header types on top-left and stays
        self.play(AddTextLetterByLetter(lab, run_time=1.2))
        pb = status_badge("PLANNED", AMBER)
        self.play(FadeIn(pb), run_time=0.4)

        # blank job cards: no company names, no logos
        cards = VGroup(*[Rectangle(width=0.5, height=0.32, stroke_width=2, stroke_color=FG)
                         for _ in range(18)])
        cards.arrange_in_grid(2, 9, buff=0.14).move_to([-1.0, 1.95, 0])
        funnel = VGroup(Line([-4.0, 1.25, 0], [-1.6, -0.55, 0], color=BLUE, stroke_width=4),
                        Line([2.0, 1.25, 0], [-0.4, -0.55, 0], color=BLUE, stroke_width=4))
        self.pin("finds early-career jobs")
        self.play(Create(funnel), LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in cards],
                                              lag_ratio=0.05), run_time=1.4)

        keep = [cards[3], cards[8], cards[13]]
        rest = [c for c in cards if all(c is not k for k in keep)]
        self.pin("sets aside the ones")
        self.play(*[c.animate.move_to([-1.0, 0.7, 0]) for c in cards], run_time=0.8)
        # set aside: a dimmed stack at the left, three per row
        pile = [c.animate.move_to([-5.9 + 0.6 * (k % 3), 0.9 - 0.42 * (k // 3), 0])
                .set_stroke(DIM, opacity=0.5) for k, c in enumerate(rest)]
        self.play(*pile, run_time=0.9)

        outs = [-2.8, -1.0, 0.8]
        self.pin("for each job that remains")
        self.play(*[c.animate.scale(1.7).move_to([x, -1.35, 0]) for c, x in zip(keep, outs)],
                  run_time=1.0)

        tags = VGroup(*[badge("evidence", AMBER, fs=18).next_to(c, DOWN, buff=0.22)
                        for c in keep])
        self.pin("shows the evidence")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tags], lag_ratio=0.3),
                  run_time=1.0)
        self.pin("public record of sponsoring")
        self.play(*[Indicate(t, color=AMBER, scale_factor=1.1) for t in tags], run_time=0.8)
        self.lock()


# ==================================================================== B02
class B02_WhyItMatters(Beat):
    beat_id = "B02"

    def construct(self):
        self.chrome()
        win = T("job-search window", 20, DIM).move_to([-5.0, 2.5, 0], aligned_edge=LEFT)
        outline = Rectangle(width=10.0, height=0.35, stroke_width=2, stroke_color=FG).move_to([0, 2.0, 0])
        fill = Rectangle(width=10.0, height=0.35, stroke_width=0, fill_color=FG,
                         fill_opacity=0.8).move_to(outline)
        self.play(FadeIn(win), Create(outline), FadeIn(fill), run_time=0.8)
        self.pin("limited time")
        self.play(fill.animate.stretch_to_fit_width(2.4).align_to(outline, LEFT), run_time=1.6)

        pivot = np.array([0, -0.75, 0])
        fulcrum = Triangle(color=FG, stroke_width=3).scale(0.4)
        fulcrum.move_to(pivot + DOWN * fulcrum.height / 2)
        beam = Line(pivot + LEFT * 4.2, pivot + RIGHT * 4.2, color=FG, stroke_width=5)
        small = label_box(["wrong: this job fits"], 4.0, 0.75, RED, 20)
        # cards sit high enough that the tilted beam never crosses them
        small.next_to(beam.point_from_proportion(0.14), UP, buff=0.4)
        large = label_box(["wrong: they sponsor"], 4.7, 1.45, RED, 26)
        large.next_to(beam.point_from_proportion(0.86), UP, buff=0.45)
        self.play(Create(fulcrum), Create(beam), run_time=0.6)
        self.pin("this job fits")
        self.play(FadeIn(small, shift=DOWN * 0.2), run_time=0.6)
        self.pin("they sponsor")
        self.play(FadeIn(large, shift=DOWN * 0.2), run_time=0.6)

        # the heavier error tips the scale
        ang, arm = 9 * DEGREES, 3.0
        d = arm * np.tan(ang)
        self.pin("cost much more")
        self.play(Rotate(beam, -ang, about_point=pivot), small.animate.shift(UP * d),
                  large.animate.shift(DOWN * d), run_time=0.9)

        chips = VGroup(*[badge(s, GREEN, fs=18) for s in
                         ("shows evidence", "says when unsure", "no auto-apply, no auto-send")])
        chips.arrange(RIGHT, buff=0.35).move_to([0, -2.45, 0])
        for chip, cue in zip(chips, ("shows its evidence", "says when it isn't sure",
                                     "doesn't apply or send")):
            self.pin(cue)
            self.play(FadeIn(chip, shift=UP * 0.15), run_time=0.5)
        self.pin("on its own")
        self.play(Indicate(chips[2], color=GREEN, scale_factor=1.08), run_time=0.8)
        self.lock()


# ==================================================================== B03
class B03_ExistingTools(Beat):
    beat_id = "B03"

    def construct(self):
        self.chrome()
        tools = [
            ("USCIS %s Employer Data Hub:" % N["h1b"],
             "approvals/denials by employer, %s" % N["fy_start"], "U S C I S publishes"),
            ("DOL OFLC disclosure files:", "case-level, quarterly", "The Department of Labor"),
            ("%s:" % N["grader_sites"], "employer search", "Sites like"),
            ("Browser extensions (e.g. Interstride):", "mark sponsors on job sites",
             "browser extensions"),
        ]
        for k, (name, what, cue) in enumerate(tools):
            y = 2.0 - 1.22 * k
            box = frame_box(9.3, 1.02, FG).move_to([-1.55, y, 0])
            txt = VGroup(T(name, 21, FG), T(what, 19, DIM)).arrange(
                DOWN, buff=0.1, aligned_edge=LEFT)
            txt.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.3)
            ok = tick(GREEN, 0.36).move_to([3.6, y, 0])
            well = T("does this well", 18, GREEN).next_to(ok, RIGHT, buff=0.2)
            self.pin(cue)
            self.play(Create(box), FadeIn(txt, shift=RIGHT * 0.15), run_time=0.7)
            self.play(Create(ok), FadeIn(well), run_time=0.5)
        self.pin("flag sponsors")
        self.play(Indicate(well, color=GREEN, scale_factor=1.1), run_time=0.8)
        self.lock()


# ==================================================================== B04
class B04_MyQuestion(Beat):
    beat_id = "B04"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED", AMBER))

        q1 = T("Has this employer sponsored before?", 22, FG)
        q1.move_to([-6.0, 2.1, 0], aligned_edge=LEFT)
        ok = tick(GREEN, 0.34).next_to(q1, RIGHT, buff=0.3)
        ex = T("existing tools", 18, DIM).next_to(ok, RIGHT, buff=0.2)
        self.pin("has this employer sponsored")
        self.play(Write(q1), run_time=0.9)
        self.play(Create(ok), FadeIn(ex), run_time=0.5)

        q2 = T("What does this posting say, and how does it compare?", 22, AMBER)
        q2.move_to([-6.0, 1.3, 0], aligned_edge=LEFT)
        self.pin("I'm adding a narrower one")
        self.play(Write(q2), run_time=1.1)

        def panel(title, color, x):
            box = frame_box(4.6, 1.9, color).move_to([x, -0.35, 0])
            t = T(title, 20, color).move_to(box.get_top() + DOWN * 0.38)
            r = text_rules(3.6, 3).next_to(t, DOWN, buff=0.3)
            return VGroup(box, t, r)

        post = panel("POSTING SAYS (quoted)", FG, -3.6)
        hist = panel("EMPLOYER HISTORY (cited)", BLUE, 1.3)
        self.pin("My agent shows both")
        self.play(FadeIn(post, shift=RIGHT * 0.2), FadeIn(hist, shift=LEFT * 0.2), run_time=0.9)

        flag = badge("DIFFERENCE TO REVIEW", AMBER, fs=22).move_to([-1.15, -2.2, 0])
        self.pin("flags differences")
        self.play(FadeIn(flag, scale=1.15), run_time=0.6)

        who = person(FG, 0.75).move_to([5.0, -0.2, 0])
        dec = T("decides", 20, FG).next_to(who, DOWN, buff=0.25)
        self.pin("leaves the decision")
        self.play(Create(who), FadeIn(dec), run_time=0.9)
        self.lock()


# ==================================================================== B05
class B05_CompletedWork(Beat):
    beat_id = "B05"

    def construct(self):
        self.chrome()
        self.add(status_badge("COMPLETED · %s" % N["js3"], GREEN))

        steps = [
            "Rules before code (%s)" % C["rules"],
            "%s postings, %s (%s): Databricks %s · Stripe %s · Plaid %s" % (
                N["postings_total"], N["collection_date"], C["collection"],
                N["postings_databricks"], N["postings_stripe"], N["postings_plaid"]),
            "%s: %s shortlisted (%s)" % (N["v1"], N["v1_shortlisted"], C["v1"]),
            "Audit of %s: %s of %s random rejects relevant; sample only, could be up to %s (%s)" % (
                N["v1"], N["audit_relevant"], N["audit_sample"], N["audit_bound"], C["audit"]),
            "%s after audit: %s verdicts changed, shortlist still %s (%s)" % (
                N["v11"], N["v11_changed"], N["v11_shortlisted"], C["v11"]),
        ]
        cues = ["I wrote filter rules", "and collected", "Version one shortlisted",
                "I reviewed thirty", "Version one point one then"]
        xs = [-5.0, -2.5, 0.0, 2.5, 5.0]
        y0 = 0.0
        # alternate above / below the line so each block gets room
        spans = [(-6.1, 3.9, "L"), (-6.1, 5.85, "L"), (0.0, 3.9, "C"),
                 (6.1, 5.85, "R"), (6.1, 3.9, "R")]

        prev = -6.0
        for k, (s, cue, x, (edge, w, how)) in enumerate(zip(steps, cues, xs, spans)):
            blk = wrap(s, 20, FG, w)
            up = k % 2 == 0
            if up:
                blk.next_to([x, y0, 0], UP, buff=0.4)
            else:
                blk.next_to([x, y0, 0], DOWN, buff=0.4)
            if how == "L":
                blk.align_to([edge, 0, 0], LEFT)
            elif how == "R":
                blk.align_to([edge, 0, 0], RIGHT)
            else:
                blk.set_x(edge)
            seg = Line([prev, y0, 0], [x, y0, 0], color=GREEN, stroke_width=4)
            dot = Dot([x, y0, 0], radius=0.11, color=GREEN)
            stem = Line([x, y0 + (0.12 if up else -0.12), 0],
                        [x, y0 + (0.32 if up else -0.32), 0], color=GREEN, stroke_width=3)
            self.pin(cue)
            self.play(Create(seg), FadeIn(dot, scale=1.4), run_time=0.5)
            self.play(Create(stem), FadeIn(blk, shift=(DOWN if up else UP) * 0.15), run_time=0.7)
            prev = x
        self.pin("the shortlist stayed")
        self.play(Indicate(blk, color=GREEN, scale_factor=1.04), run_time=0.9)
        self.lock()


# ==================================================================== B06
class B06_DataAndLimits(Beat):
    beat_id = "B06"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED (NOT BUILT)", AMBER))

        lca = label_box(["LCA certified by DOL"], 3.9, 0.7, FG, 20).move_to([-4.25, 1.75, 0])
        pet = label_box(["%s petition to USCIS" % N["h1b"]], 4.3, 0.7, FG, 20).move_to([0.35, 1.75, 0])
        dec = label_box(["decision"], 2.0, 0.7, DIM, 20, dashed=True).move_to([4.4, 1.75, 0])
        notin = T("not in this data", 18, DIM).next_to(dec, DOWN, buff=0.18)
        a1 = arrow(lca[0].get_right(), pet[0].get_left())
        a2 = DashedLine(pet[0].get_right() + RIGHT * 0.1, dec[0].get_left() + LEFT * 0.1,
                        color=DIM, stroke_width=3)
        cap = T("historical activity ≠ approval ≠ future promise", 20, AMBER)
        cap.move_to([-1.6, 0.95, 0])

        self.pin("The new data is")
        self.play(FadeIn(lca, shift=RIGHT * 0.2), run_time=0.7)
        self.pin("before filing")
        self.play(GrowArrow(a1), FadeIn(pet, shift=RIGHT * 0.2), run_time=0.8)
        self.pin("not a visa approval")
        self.play(Create(a2), FadeIn(dec), FadeIn(notin), run_time=0.8)
        self.play(Write(cap), run_time=1.0)

        vh = T("VISA_CLASS", 20, DIM).move_to([-6.1, 0.15, 0], aligned_edge=LEFT)
        visas = VGroup(*[T(v, 22, FG) for v in (N["h1b"], N["h1b1"], N["e3"])])
        for k, v in enumerate(visas):
            v.move_to([-5.8, -0.45 - 0.6 * k, 0], aligned_edge=LEFT)
        keep = tick(GREEN, 0.32).next_to(visas[0], RIGHT, buff=0.3)
        sh = T("CASE_STATUS", 20, DIM).move_to([-2.6, 0.15, 0], aligned_edge=LEFT)
        rows = [("Certified → counted", FG),
                ("Certified-Withdrawn → listed separately, not counted", VIOLET),
                ("Denied, Withdrawn → excluded", DIM)]
        st = VGroup(*[T(s, 19, c) for s, c in rows])
        for k, r in enumerate(st):
            r.move_to([-2.6, -0.45 - 0.6 * k, 0], aligned_edge=LEFT)

        self.pin("count only certified")
        self.play(FadeIn(vh), FadeIn(visas[0]), Create(keep), FadeIn(sh), FadeIn(st[0]),
                  run_time=0.8)
        self.pin("list withdrawn certifications")
        self.play(FadeIn(st[1], shift=RIGHT * 0.15), run_time=0.6)
        self.pin("leave out")
        self.play(FadeIn(visas[1]), FadeIn(visas[2]), FadeIn(st[2]), run_time=0.5)
        self.play(Create(strike(visas[1])), Create(strike(visas[2])),
                  visas[1].animate.set_color(DIM), visas[2].animate.set_color(DIM), run_time=0.5)

        p1 = T("%s posting restriction (headline)" % N["rank_1"], 19, AMBER)
        p2 = T("%s employer history (context)" % N["rank_2"], 19, FG)
        pr = VGroup(p1, p2).arrange(RIGHT, buff=0.6)
        card = frame_box(pr.width + 0.5, 0.62, FG).move_to([0, -2.45, 0])
        pr.move_to(card)
        self.pin("If a posting says")
        self.play(Create(card), FadeIn(p1), run_time=0.7)
        self.pin("the employer's history is context")
        self.play(FadeIn(p2), run_time=0.6)
        self.lock()


# ==================================================================== B07
class B07_LoopAndPermissions(Beat):
    beat_id = "B07"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED", AMBER))

        # dashed: not built
        words = ["collect", "filter", "match", "check", "record", "stop"]
        parts, boxes = [], []
        for k, w in enumerate(words):
            t = T(w, 20, FG)
            b = DashedVMobject(SurroundingRectangle(t, color=FG, stroke_width=2, buff=0.14),
                               num_dashes=24)
            boxes.append(VGroup(b, t))
            parts.append(boxes[-1])
            if k < len(words) - 1:
                parts.append(T("->", 20, DIM))
        row = VGroup(*parts).arrange(RIGHT, buff=0.14).move_to([0, 1.8, 0])
        back = DashedVMobject(ArcBetweenPoints(boxes[4].get_bottom() + DOWN * 0.05,
                                               boxes[0].get_bottom() + DOWN * 0.05,
                                               angle=-PI / 5, color=BLUE, stroke_width=3),
                              num_dashes=40)
        self.pin("run as a loop")
        self.play(LaggedStart(*[FadeIn(p) for p in parts], lag_ratio=0.15), run_time=1.6)
        self.play(Create(back), run_time=0.6)

        ro_box = frame_box(4.0, 1.25, BLUE).move_to([-4.2, -0.1, 0])
        ro = wrap("job boards · DOL files: READ-ONLY", 18, BLUE, 3.7).move_to(ro_box)
        slot = frame_box(2.6, 0.7, DIM, dashed=True).move_to([-4.2, -1.65, 0])
        sa = T("send / apply", 20, DIM).move_to(slot)
        no = cross(RED, 0.4).move_to([-5.85, -1.65, 0])
        nst = T("no such tool", 18, RED).next_to(slot, DOWN, buff=0.2)
        self.pin("Outside sources are read-only")
        self.play(Create(ro_box), FadeIn(ro), run_time=0.7)
        self.play(Create(slot), FadeIn(sa), Create(no), FadeIn(nst), run_time=0.7)

        wa = T("writes allowed", 18, FG).move_to([-1.6, 0.3, 0], aligned_edge=LEFT)
        dirs = VGroup()
        for k, d in enumerate(("state/ (memory)", "audit/", "decisions/")):
            f = folder(BLUE, 1.0)
            t = T(d, 20, FG)
            dirs.add(VGroup(f, t).arrange(RIGHT, buff=0.2).move_to(
                [-1.6, -0.35 - 0.6 * k, 0], aligned_edge=LEFT))
        self.pin("it writes only")
        self.play(FadeIn(wa), LaggedStart(*[FadeIn(d, shift=RIGHT * 0.15) for d in dirs],
                                          lag_ratio=0.25), run_time=0.9)

        bl = T("budget", 18, DIM).move_to([2.4, 0.3, 0], aligned_edge=LEFT)
        meter = Rectangle(width=2.6, height=0.3, stroke_width=2, stroke_color=FG).move_to([4.8, 0.3, 0])
        level = Rectangle(width=2.6, height=0.3, stroke_width=0, fill_color=BLUE,
                          fill_opacity=0.8).move_to(meter)
        self.pin("fixed budget")
        self.play(FadeIn(bl), Create(meter), FadeIn(level), run_time=0.6)
        self.play(level.animate.stretch_to_fit_width(0.9).align_to(meter, LEFT), run_time=0.8)

        exits = VGroup()
        for k, e in enumerate(("queue empty", "budget spent", "error limit")):
            y = -0.35 - 0.6 * k
            a = arrow([2.3, y, 0], [2.95, y, 0], FG, sw=3)
            exits.add(VGroup(a, T(e, 20, FG).move_to([3.1, y, 0], aligned_edge=LEFT)))
        self.pin("stops when the queue")
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.1) for x in exits], lag_ratio=0.3),
                  run_time=1.0)
        msd = T("model says done", 20, DIM).move_to([3.1, -2.3, 0], aligned_edge=LEFT)
        self.pin("not because the model")
        self.play(FadeIn(msd), run_time=0.4)
        self.play(Create(strike(msd)), run_time=0.4)
        self.lock()


# ==================================================================== B08
class B08_GateAndResources(Beat):
    beat_id = "B08"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED", AMBER))

        posts = VGroup(Line(UP * 0.5, DOWN * 0.5, stroke_width=6, color=FG).shift(LEFT * 0.3),
                       Line(UP * 0.5, DOWN * 0.5, stroke_width=6, color=FG).shift(RIGHT * 0.3),
                       Line(LEFT * 0.3, RIGHT * 0.3, stroke_width=6, color=AMBER).shift(UP * 0.15))
        gate = posts.move_to([-5.75, 1.75, 0])
        btns = VGroup(badge("approve", GREEN), T("/", 20, DIM), badge("refuse", RED),
                      T("/", 20, DIM), badge("defer", AMBER))
        btns.arrange(RIGHT, buff=0.18).move_to([-2.85, 1.75, 0])
        self.pin("I'll approve")
        self.play(Create(gate), LaggedStart(*[FadeIn(b) for b in btns], lag_ratio=0.2),
                  run_time=1.0)

        card = frame_box(3.0, 1.1, FG).move_to([-2.85, 0.15, 0])
        hsh = T("#hash", 22, FG).move_to(card.get_top() + DOWN * 0.3)
        rl = text_rules(2.2, 2, buff=0.16).next_to(hsh, DOWN, buff=0.18)
        # ends stop short of the badge and card; touching, GATE T read the
        # three as one fused text blob
        a, b = np.array(btns[0].get_bottom()), np.array(card.get_top())
        u = (b - a) / (np.linalg.norm(b - a) or 1.0)
        tie = Line(a + u * 0.15, b - u * 0.15, color=GREEN, stroke_width=3)
        self.pin("tied to the exact evidence")
        self.play(Create(tie), Create(card), FadeIn(hsh), FadeIn(rl), run_time=0.8)

        stale_box = frame_box(3.0, 0.75, AMBER, dashed=True).move_to([-2.85, -1.3, 0])
        stale = T("stale: rejected", 20, AMBER).move_to(stale_box)
        link = DashedLine(card.get_bottom(), stale_box.get_top(), color=AMBER, stroke_width=3)
        self.pin("evidence I saw", lead=0.0)
        self.play(Create(link), Create(stale_box), FadeIn(stale), run_time=0.7)

        pers = badge("Priya Nair — FICTIONAL", FG, fs=20).move_to([-3.3, -2.45, 0])
        self.pin("Priya Nair")
        self.play(FadeIn(pers, shift=UP * 0.1), run_time=0.6)

        head = T("Resources", 22, FG).move_to([0.4, 1.9, 0], aligned_edge=LEFT)
        self.pin("Resources:")
        self.play(FadeIn(head), run_time=0.4)
        items = [("Claude Code via university seat (model access, usage limits apply)", "Claude Code seat"),
                 ("job-board APIs, no key", "job-board APIs"),
                 ("free government data", "government data is free"),
                 ("laptop", "my laptop")]
        y = 1.35
        for s, cue in items:
            txt = wrap(s, 19, FG, 5.0)
            ok = tick(GREEN, 0.3)
            txt.move_to([1.0, y, 0], aligned_edge=UL)
            ok.move_to([0.6, txt[0].get_center()[1], 0])
            y = txt.get_bottom()[1] - 0.3
            self.pin(cue)
            self.play(Create(ok), FadeIn(txt, shift=RIGHT * 0.15), run_time=0.5)

        det = badge("Details: PLAN-APPENDIX.md", FG, fs=20).move_to([0.4, -2.45, 0], aligned_edge=LEFT)
        self.pin("Details are in my appendix")
        self.play(FadeIn(det, shift=UP * 0.1), run_time=0.6)
        self.lock()


# ==================================================================== B09
class B09_LabelSets(Beat):
    beat_id = "B09"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED", AMBER))

        sq = VGroup(*[Square(0.26, stroke_width=2, stroke_color=FG) for _ in range(60)])
        sq.arrange_in_grid(4, 15, buff=0.08).move_to([-1.2, 1.55, 0])
        total = T(N["label_total"], 26, FG).next_to(sq, LEFT, buff=0.4)
        self.pin("hand-label sixty")
        self.play(FadeIn(total), LaggedStart(*[FadeIn(s) for s in sq], lag_ratio=0.01),
                  run_time=1.1)

        # 4 x 15 grid: the first five columns are development, the rest held-out
        dev = VGroup(*[s for i, s in enumerate(sq) if i % 15 < 5])
        held = VGroup(*[s for i, s in enumerate(sq) if i % 15 >= 5])
        dl = VGroup(T(N["label_dev"], 24, BLUE), T("development", 20, BLUE)).arrange(RIGHT, buff=0.2)
        dl.move_to([-4.6, 0.5, 0])
        self.pin("twenty for development")
        self.play(FadeOut(total), dev.animate.set_stroke(BLUE).move_to([-4.6, 1.55, 0]),
                  held.animate.set_stroke(VIOLET).move_to([0.9, 1.55, 0]), run_time=0.8)
        self.play(FadeIn(dl), run_time=0.4)

        lock_ = padlock(VIOLET).move_to([3.15, 1.55, 0])
        hl = VGroup(T(N["label_heldout"], 24, VIOLET), T("held-out", 20, VIOLET)).arrange(RIGHT, buff=0.2)
        hl.move_to([0.9, 0.5, 0])
        cbc = T("committed before code", 18, DIM).next_to(hl, DOWN, buff=0.15)
        self.pin("forty locked away")
        self.play(FadeIn(lock_, scale=1.3), FadeIn(hl), FadeIn(cbc), run_time=0.7)

        ex_box = frame_box(8.6, 0.6, FG, dashed=True).move_to([0, -2.45, 0])
        ex = T("No qualifying record found in the selected datasets", 18, FG).move_to(ex_box)
        self.pin("including employers with no")
        self.play(Create(ex_box), FadeIn(ex), run_time=0.7)

        a = label_box(["%s with qualifying records → missed-match check" % N["heldout_with_records"]],
                      8.6, 0.6, VIOLET, 19).move_to([0.9, -0.8, 0])
        b = label_box(["%s with none → false-match check" % N["heldout_none"]],
                      8.6, 0.6, VIOLET, 19).move_to([0.9, -1.55, 0])
        self.pin("Missed matches count only")
        self.play(FadeIn(a, shift=DOWN * 0.15), run_time=0.6)
        self.pin("the rest are checked")
        self.play(FadeIn(b, shift=DOWN * 0.15), run_time=0.6)
        self.pin("false matches")
        self.play(Indicate(b[1], color=VIOLET, scale_factor=1.06), run_time=0.8)
        self.lock()


# ==================================================================== B10
class B10_Checker(Beat):
    beat_id = "B10"

    def construct(self):
        self.chrome()
        self.add(status_badge("PLANNED", AMBER))

        box = frame_box(5.0, 2.5, FG).move_to([-1.8, 0.85, 0])
        head = T("CHECKER", 22, FG).move_to(box.get_top() + DOWN * 0.35)
        checks = VGroup(*[T(s, 19, FG) for s in
                          ("right employer", "right source", "record supports sentence")])
        for k, c in enumerate(checks):
            c.move_to([-3.7, 1.15 - 0.55 * k, 0], aligned_edge=LEFT)
        self.pin("A separate checker")
        self.play(Create(box), FadeIn(head), FadeIn(checks), run_time=0.9)

        claim = doc_icon(0.9, 1.1, FG, lines=3).move_to([-5.55, 0.6, 0])
        self.pin("re-verify each claim")
        self.play(FadeIn(claim, shift=RIGHT * 0.2), run_time=0.5)
        ticks = VGroup(*[tick(GREEN, 0.28).move_to([-4.0, c.get_center()[1], 0]) for c in checks])
        for t, cue in zip(ticks, ("the right employer", "the right source", "supports the sentence")):
            self.pin(cue, lead=0.2)
            self.play(Create(t), run_time=0.4)
        self.play(claim.animate.move_to([1.3, 0.6, 0]), run_time=0.6)

        seed = badge("SEEDED: wrong match", RED, fs=19).move_to([-4.35, -1.3, 0])
        self.pin("trigger one wrong match")
        self.play(FadeIn(seed, shift=RIGHT * 0.2), run_time=0.5)
        self.play(seed.animate.move_to([-1.8, -1.3, 0]), run_time=0.6)
        stop = RegularPolygon(8, color=RED, fill_color=RED, fill_opacity=0.85,
                              stroke_width=3).scale(0.32).rotate(PI / 8).move_to([0.6, -1.3, 0])
        blk = T("blocked", 19, RED).next_to(stop, DOWN, buff=0.15)
        flag = SurroundingRectangle(checks[0], color=RED, stroke_width=3, buff=0.08)
        self.pin("gets caught", lead=0.2)
        self.play(Create(flag), FadeIn(stop, scale=1.3), FadeIn(blk), run_time=0.6)

        lst = wrap("deliberate failures (%s): no filings · suffix variant · trade name · "
                   "look-alike · staffing placement · %s/%s only"
                   % (N["min_failures"], N["h1b1"], N["e3"]), 19, FG, 3.85)
        lst.move_to([2.35, 2.0, 0], aligned_edge=UL)
        self.pin("at least five")
        self.play(LaggedStart(*[FadeIn(l, shift=LEFT * 0.1) for l in lst], lag_ratio=0.3),
                  run_time=2.2)
        self.lock()


# ==================================================================== B11
class B11_Targets(Beat):
    beat_id = "B11"

    def construct(self):
        self.chrome()
        # stays for the whole beat, through the sign-off
        title = badge("PROPOSED TARGETS — NOT RESULTS", AMBER, fs=26).move_to([0, 2.4, 0])
        self.add(title)

        rows = [("wrong matches", N["target_zero"], None, "zero wrong matches"),
                ("unsupported claims", N["target_zero"], None, "zero unsupported"),
                ("unauthorized actions", N["target_zero"], None, "zero unauthorized"),
                ("planted differences flagged", "all", None, "every planted difference"),
                ("missed matches", N["target_missed"], "(of employers with records)",
                 "at most two missed")]
        table = VGroup()
        for k, (name, val, note, cue) in enumerate(rows):
            y = 1.55 - 0.55 * k
            r = VGroup(T(name, 22, FG).move_to([-5.0, y, 0], aligned_edge=LEFT),
                       T(val, 22, AMBER).move_to([0.9, y, 0], aligned_edge=LEFT))
            if note:
                r.add(T(note, 18, DIM).next_to(r[1], RIGHT, buff=0.25))
            # dashed hollow marker: a target, not a measured result (no text;
            # the PROPOSED TARGETS label already says so)
            r.add(DashedVMobject(Square(0.3, stroke_width=3, color=AMBER),
                                 num_dashes=8).move_to([-5.5, y, 0]))
            table.add(r)
            self.pin(cue)
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.5)

        proto = T("first held-out result kept; re-run after a fix = regression test", 19, FG)
        proto.move_to([0, -1.45, 0])
        self.pin("After any fix")
        self.play(Write(proto), run_time=1.0)
        lim = badge("purposive sample: tests the rules, not a real-world rate", DIM, fs=19)
        lim.move_to([0, -2.4, 0])
        self.pin("The employers are chosen")
        self.play(FadeIn(lim, shift=UP * 0.1), run_time=0.6)

        sign = T("Swathi Baba Eswarappa · %s · Final Project Film" % N["course"], 26, FG)
        sign.move_to([0, 0.1, 0])
        self.pin("These are targets")
        self.play(FadeOut(VGroup(table, proto, lim)), run_time=0.5)
        self.play(FadeIn(sign, shift=UP * 0.15), run_time=0.6)
        self.lock()


SCENES = [b["graphic"]["manim"] for b in SHEET["beats"]]
