#!/usr/bin/env python3
"""
scene.py -- INFO 7375 Final Project Pitch Film
Swathi Baba Eswarappa

Visual engine for "Cite or Refuse", a pitch for a source-grounded tax helper
for international students. Nothing in the pitched project exists yet.

Thirteen Manim scenes, one per beat in beat_sheet.json. Each scene reads its
own runtime from mp3/timings.json (Kokoro durations = ground truth) and pads
itself to match, so picture and narration stay locked without manual nudging.

EVIDENCE RULE
  Every number drawn on screen is read at import time out of data/facts.json.
  Nothing numeric is typed into an animation; check_facts.py fails the build
  if a string literal in this file contains a digit.

LABEL RULE
  Planned-system pictures carry a PROPOSED badge. B08's terminal carries
  CONSTRUCTED MOCK-UP for the whole beat, with dashes where numbers would be.

Render:  manim -qh scene.py B01_TwoAnswers ... (see build.sh)
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
GRID = FACTS["test_grid"]
TIMINGS = json.loads((ROOT / "mp3/timings.json").read_text())
SHEET = json.loads((ROOT / "beat_sheet.json").read_text())
NARRATION = {b["beat_id"]: b["narration_text"] for b in SHEET["beats"]}

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
    kicker = ""
    source = ""

    def chrome(self):
        rule_t = Line(LEFT * RULE_X, RIGHT * RULE_X, stroke_width=2,
                      color=DIM).shift(UP * RULE_Y)
        rule_b = Line(LEFT * RULE_X, RIGHT * RULE_X, stroke_width=2,
                      color=DIM).shift(DOWN * RULE_Y)
        tag = Text(self.beat_id, font=MONO, font_size=17, color=DIM)
        tag.next_to(rule_t, UP, buff=0.12).align_to(rule_t, LEFT)
        kick = Text(self.kicker, font=MONO, font_size=17, color=DIM)
        kick.next_to(rule_t, UP, buff=0.12).align_to(rule_t, RIGHT)
        foot = Text("%s · S. BABA ESWARAPPA" % N["course"], font=MONO,
                    font_size=15, color=DIM)
        foot.next_to(rule_b, DOWN, buff=0.12).align_to(rule_b, LEFT)
        # provenance: say on screen where this beat's content came from
        src = Text(self.source, font=MONO, font_size=15, color=DIM)
        src.next_to(rule_b, DOWN, buff=0.12).align_to(rule_b, RIGHT)
        self.add(rule_t, rule_b, tag, kick, foot, src)
        # content must live BETWEEN the rules, not merely inside the frame
        self.chrome_mobs = VGroup(rule_t, rule_b, tag, kick, foot, src)
        self.safe_top = rule_t.get_bottom()[1]
        self.safe_bottom = rule_b.get_top()[1]

    def play(self, *a, **k):
        if getattr(self, "_first_cue", None) is None:
            self._first_cue = self.renderer.time
        # midpoint guard: an animation that would straddle the clip midpoint
        # waits until just after it, so GATE T reads a settled frame there
        # (a half-drawn strike line in B10 read as a 9 px label). wait() is
        # itself play(Wait(...)), so pure waits pass straight through.
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
        # Week 1 only checked the settled end frame, so a label that collided
        # mid-beat and was later cleared could pass. Check after every cue.
        self.assert_in_safe_area()
        self.assert_no_text_overlap()
        return out

    def hold_until(self, t):
        """Wait until scene-time `t`, so a cue can be pinned to the narration."""
        self.wait(max(t - self.renderer.time, 0.04))

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
    """Monospace label, shrunk to max_w if it would not fit."""
    t = Text(s, font=MONO, font_size=fs, color=color)
    if max_w and t.width > max_w:
        t.scale(max_w / t.width)
    return t


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


def doc_icon(w, h, color=FG, lines=5, fold=0.45):
    """A page with a folded corner and a few grey text rules."""
    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
    page = Polygon([x0, y1, 0], [x1 - fold, y1, 0], [x1, y1 - fold, 0],
                   [x1, y0, 0], [x0, y0, 0], stroke_color=color,
                   stroke_width=3, fill_color=BG, fill_opacity=1)
    ear = VMobject(stroke_color=color, stroke_width=2).set_points_as_corners(
        [[x1 - fold, y1, 0], [x1 - fold, y1 - fold, 0], [x1, y1 - fold, 0]])
    rules = VGroup(*[Line([x0 + 0.3, 0, 0], [x1 - 0.3 - (0.6 if k % 3 == 2 else 0), 0, 0],
                          stroke_width=2, color=DIM) for k in range(lines)])
    rules.arrange(DOWN, buff=0.28).move_to([0, -h * 0.12, 0])
    return VGroup(page, ear, rules)


def tick(color=GREEN, s=0.5):
    return VMobject(stroke_color=color, stroke_width=7).set_points_as_corners(
        [[-s * 0.5, 0, 0], [-s * 0.15, -s * 0.38, 0], [s * 0.55, s * 0.45, 0]])


def cross(color=RED, s=0.45):
    return VGroup(Line([-s / 2, -s / 2, 0], [s / 2, s / 2, 0], color=color, stroke_width=7),
                  Line([-s / 2, s / 2, 0], [s / 2, -s / 2, 0], color=color, stroke_width=7))


def arrow(a, b, color=DIM, sw=3):
    return Arrow(a, b, buff=0.1, stroke_width=sw, color=color,
                 max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=8)


def badge(text, color, fs=20):
    t = T(text, fs, color)
    return VGroup(SurroundingRectangle(t, color=color, stroke_width=2, buff=0.12), t)


def proposed_badge():
    """Pinned top-right inside the content area for the whole beat."""
    b = badge("PROPOSED · NOT BUILT", AMBER)
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


# ==================================================================== B01
class B01_TwoAnswers(Beat):
    beat_id, kicker = "B01", "TWO RUNS, TWO NUMBERS"
    source = "source: TEST-NOTES.md"

    def answer_card(self, run, amount):
        box = RoundedRectangle(corner_radius=0.12, width=4.9, height=3.3,
                               stroke_width=3, stroke_color=FG)
        head = T("ChatGPT, %s" % N["test_date"], 22, FG, max_w=4.4)
        sub = T(run, 20, DIM)
        num = T(amount, 72, AMBER, max_w=4.3)
        head.move_to(box.get_top() + DOWN * 0.45)
        sub.next_to(head, DOWN, buff=0.16)
        num.move_to(box.get_center() + DOWN * 0.55)
        return VGroup(box, head, sub), num

    def construct(self):
        self.chrome()
        q = T("one question, asked twice", 30, DIM).shift(UP * 2.35)
        self.play(AddTextLetterByLetter(q, run_time=1.6))

        card_a, num_a = self.answer_card("run A", N["amount_run_a"])
        card_b, num_b = self.answer_card("run B", N["amount_run_b"])
        card_a.shift(LEFT * 3.0 + DOWN * 0.25)
        card_b.shift(RIGHT * 3.0 + DOWN * 0.25)
        num_a.shift(LEFT * 3.0 + DOWN * 0.25)
        num_b.shift(RIGHT * 3.0 + DOWN * 0.25)

        self.pin("Same tool")
        self.play(Create(card_a[0]), Create(card_b[0]),
                  FadeIn(card_a[1:]), FadeIn(card_b[1:]), run_time=1.2)

        self.pin("fifteen thousand seven hundred")
        self.play(FadeIn(num_a, scale=1.2), run_time=0.7)
        self.pin("The other said")
        self.play(FadeIn(num_b, scale=1.2), run_time=0.7)

        neq = T("≠", 80, RED).move_to(DOWN * 0.8)
        cap = T("both sounded confident", 24, DIM).shift(DOWN * 2.6)
        self.pin("Both sounded")
        self.play(FadeIn(neq, scale=1.4), Write(cap), run_time=0.9)
        self.lock()


# ==================================================================== B02
class B02_OfficialCheck(Beat):
    beat_id, kicker = "B02", "THE OFFICIAL CHECK"
    source = "source: IRS %s Instructions for Form %s, %s" % (
        N["tax_year"], N["form_1040nr"], N["irs_page"])

    def construct(self):
        self.chrome()
        doc = doc_icon(3.8, 4.9, FG, lines=6).shift(LEFT * 3.5 + DOWN * 0.15)
        t1 = T("%s Instructions" % N["tax_year"], 22, FG, max_w=2.8)
        t2 = T("Form %s" % N["form_1040nr"], 22, FG, max_w=2.8)
        title = VGroup(t1, t2).arrange(DOWN, buff=0.1)
        title.move_to(doc[0].get_top() + DOWN * 0.75 + LEFT * 0.25)
        # the rules sit low in the page; keep them clear of the title
        doc[2].next_to(title, DOWN, buff=0.35)
        self.play(Create(doc[0]), Create(doc[1]), FadeIn(doc[2]), Write(title),
                  run_time=1.4)

        cards = VGroup()
        for run, amt in (("run A", N["amount_run_a"]), ("run B", N["amount_run_b"])):
            box = RoundedRectangle(corner_radius=0.1, width=4.2, height=1.35,
                                   stroke_width=3, stroke_color=FG)
            lab = T(run, 20, DIM).move_to(box.get_left() + RIGHT * 0.6)
            num = T(amt, 40, FG).move_to(box.get_center() + RIGHT * 0.55)
            cards.add(VGroup(box, lab, num))
        cards.arrange(DOWN, buff=0.9).shift(RIGHT * 3.0 + UP * 0.05)
        self.add(cards)

        tab = badge(N["irs_page"], AMBER, fs=26)
        tab.next_to(doc[0], UP, buff=0.08).align_to(doc[0], RIGHT)
        self.pin("Page seven")
        self.play(FadeIn(tab, shift=DOWN * 0.2), run_time=0.6)

        hl_row = doc[2][3]
        hl = Rectangle(width=3.3, height=0.55, stroke_width=0, fill_color=AMBER,
                       fill_opacity=0.22).move_to(hl_row)
        amount = T(N["amount_run_a"], 30, AMBER).move_to(hl)
        self.pin("lists fifteen thousand")
        self.play(FadeOut(hl_row), FadeIn(hl), Write(amount), run_time=0.9)

        a_box, b_box = cards[0][0], cards[1][0]
        link = DashedLine(hl.get_right(), a_box.get_left(), color=GREEN,
                          stroke_width=3, dash_length=0.12)
        ok = tick().next_to(a_box, RIGHT, buff=0.15)
        self.pin("One run's number matched")
        self.play(Create(link), a_box.animate.set_stroke(GREEN, width=5),
                  Create(ok), run_time=0.9)
        no = cross().next_to(b_box, RIGHT, buff=0.2)
        self.pin("The other did not")
        self.play(b_box.animate.set_stroke(RED, width=5), Create(no), run_time=0.7)

        cap = T("neither said which to trust", 24, DIM)
        cap.next_to(cards, DOWN, buff=0.45)
        self.pin("Neither answer")
        self.play(Write(cap), run_time=1.0)
        self.lock()


# ==================================================================== B03
class B03_Problem(Beat):
    beat_id, kicker = "B03", "THE PROBLEM"
    source = "source: PROJECT-BRIEF.md"

    def construct(self):
        self.chrome()
        who = person(FG, 1.15).shift(LEFT * 4.4 + UP * 0.25)
        self.play(Create(who), run_time=1.2)

        years = N["publication_years"]          # oldest .. newest
        w, h, off = 3.4, 3.7, np.array([0.55, 0.5, 0])
        front_c = np.array([0.6, -0.75, 0])
        docs, tabs = [], []
        for k, yr in enumerate(reversed(years)):  # k=0 is the front (newest)
            d = doc_icon(w, h, FG if k == 0 else DIM, lines=2 if k == 0 else 4)
            d.move_to(front_c + off * k)
            d.set_z_index(-k)
            lab = T(yr, 20, AMBER).set_z_index(-k + 0.5)
            lab.move_to(d[0].get_corner(UR) + LEFT * 1.0 + DOWN * 0.25)
            docs.append(d)
            tabs.append(lab)

        form = T("Form %s" % N["form_8843"], 30, FG).move_to(docs[0][0].get_center() + UP * 0.35)
        form.set_z_index(1)
        docs[0][2].next_to(form, DOWN, buff=0.35).set_z_index(1)
        self.pin("Form eighty eight")
        self.play(FadeIn(docs[0], shift=UP * 0.2), Write(form), run_time=0.9)

        treaty = T("treaty applies?", 22, AMBER).set_z_index(1)
        treaty.next_to(docs[0][2], DOWN, buff=0.25)
        self.pin("whether a tax treaty")
        self.play(Write(treaty), run_time=0.8)

        self.pin("The rules live in long")
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.15) for d in docs[1:]],
                              lag_ratio=0.35), run_time=1.1)
        self.pin("change every year")
        self.play(LaggedStart(*[FadeIn(t) for t in reversed(tabs)], lag_ratio=0.3),
                  run_time=1.0)

        warn = Triangle(color=RED, stroke_width=5).scale(0.62)
        bang = T("!", 40, RED).move_to(warn.get_center() + DOWN * 0.08)
        alert = VGroup(warn, bang).move_to([5.2, -1.3, 0])
        self.pin("a wrong answer")
        self.play(FadeIn(alert, scale=1.3), docs[0][0].animate.set_stroke(RED),
                  run_time=0.8)
        self.lock()


# ==================================================================== B04
class B04_What(Beat):
    beat_id, kicker = "B04", "WHAT I WILL BUILD"
    source = "plan only · nothing built yet"

    def construct(self):
        self.chrome()
        pb = proposed_badge()
        self.add(pb)

        lead = T("what I will build", 24, DIM).move_to(UP * 2.55 + LEFT * 2.6)
        self.play(Write(lead), run_time=0.8)

        title = T("CITE OR REFUSE", 60, FG).shift(UP * 1.6)
        self.pin("Cite or Refuse")
        self.play(AddTextLetterByLetter(title, run_time=1.0))

        q = label_box(["a tax question"], 3.6, 0.85, FG, 24).shift(UP * 0.15)
        self.pin("a tax helper")
        self.play(Create(q[0]), Write(q[1]), run_time=0.8)

        ans = label_box(["answer", "+ exact passage + tax year"], 4.8, 1.35,
                        GREEN, 26, sub_color=GREEN).shift(LEFT * 3.2 + DOWN * 1.55)
        ref = label_box(["refuse", "not covered by the sources"], 4.8, 1.35,
                        AMBER, 26, sub_color=AMBER).shift(RIGHT * 3.2 + DOWN * 1.55)
        # tips stop clear of the boxes; touching, GATE T read arrow + label as one blob
        a1 = arrow(q[0].get_bottom() + LEFT * 0.6,
                   ans[0].get_top() + RIGHT * 0.6 + UP * 0.18, GREEN)
        a2 = arrow(q[0].get_bottom() + RIGHT * 0.6,
                   ref[0].get_top() + LEFT * 0.6 + UP * 0.18, AMBER)
        self.pin("shows the exact passage")
        self.play(GrowArrow(a1), FadeIn(ans, shift=DOWN * 0.15), run_time=0.9)
        self.pin("refuses when")
        self.play(GrowArrow(a2), FadeIn(ref, shift=DOWN * 0.15), run_time=0.9)

        repo = T("→ a GitHub repository", 22, DIM).shift(DOWN * 2.7)
        self.pin("It will be a GitHub")
        self.play(Write(repo), run_time=0.8)
        self.pin("None of it exists yet")
        self.play(Indicate(pb, color=AMBER, scale_factor=1.12), run_time=0.9)
        self.lock()


# ==================================================================== B05
class B05_Alternatives(Beat):
    beat_id, kicker = "B05", "ALTERNATIVES I TESTED"
    source = "source: TEST-NOTES.md · informal test"

    def construct(self):
        self.chrome()
        # these are real chatbot results, so the date they were obtained is shown
        head = T("MY TEST, %s · %s TOOLS × %s QUESTIONS · ONE RUN EACH"
                 % (N["test_date"].upper(), N["tools_tested"], N["questions_tested"]),
                 24, DIM, max_w=12.2).shift(UP * 2.5)
        self.play(Write(head), run_time=0.8)

        col_x = [-1.05, 1.85, 4.75]
        row_y = [0.55, -0.45, -1.45]
        label_x, cw, ch = -4.25, 2.8, 0.9
        colour = {"YES": GREEN, "NO": RED, "PARTLY": AMBER, "No / No / Partly": AMBER}

        heads = VGroup()
        for x, c in zip(col_x, GRID["columns"]):
            g = VGroup(*[T(s, 20, FG) for s in c["label"]]).arrange(DOWN, buff=0.08)
            heads.add(g.move_to([x, 1.55, 0]))
        self.add(heads)

        rows, cells = [], {}
        for y, r in zip(row_y, GRID["rows"]):
            lab_box = Rectangle(width=2.6, height=ch, stroke_width=2, stroke_color=DIM)
            lab = T(r["tool"], 26, FG)
            rg = VGroup(lab_box, lab.move_to(lab_box)).move_to([label_x, y, 0])
            boxes = VGroup()
            for x, c in zip(col_x, GRID["columns"]):
                b = Rectangle(width=cw, height=ch, stroke_width=2,
                              stroke_color=DIM).move_to([x, y, 0])
                boxes.add(b)
                v = r[c["key"]]
                cells[(r["tool"], c["key"])] = (b, T(v, 26, colour[v], max_w=cw - 0.3).move_to(b))
            rows.append(VGroup(rg, boxes))

        for r, row in zip(GRID["rows"], rows):
            self.pin(r["cue"])
            self.play(FadeIn(row, shift=RIGHT * 0.25), run_time=0.45)

        foot = T("small informal test, not a benchmark", 18, DIM).shift(DOWN * 2.7)
        self.pin("A small test")
        self.play(FadeIn(foot), run_time=0.6)

        def fill(key):
            return [FadeIn(cells[(r["tool"], key)][1], scale=1.15) for r in GRID["rows"]]

        self.pin(GRID["columns"][0]["cue"])
        self.play(LaggedStart(*fill("exact_passage"), lag_ratio=0.25), run_time=0.9)
        self.pin(GRID["columns"][1]["cue"])
        self.play(LaggedStart(*fill("tax_year"), lag_ratio=0.25), run_time=0.9)

        note = T("Gemini: third-party sites only", 20, AMBER).shift(DOWN * 2.2)
        gem = SurroundingRectangle(cells[("Gemini", "exact_passage")][0],
                                   color=AMBER, stroke_width=4, buff=0.0)
        self.pin("Gemini cited only")
        self.play(Create(gem), FadeIn(note), run_time=0.8)

        self.pin(GRID["columns"][2]["cue"])
        self.play(LaggedStart(*fill("declined"), lag_ratio=0.25), run_time=0.9)
        col = VGroup(*[cells[(r["tool"], "declined")][0] for r in GRID["rows"]])
        self.pin("none cleanly declined")
        self.play(Create(SurroundingRectangle(col, color=RED, stroke_width=4, buff=0.06)),
                  run_time=0.6)
        self.lock()


# ==================================================================== B06
class B06_Plan(Beat):
    beat_id, kicker = "B06", "HOW · PLANNED PIPELINE"
    source = "plan only · nothing built yet"

    def construct(self):
        self.chrome()
        self.add(proposed_badge())

        pubs = label_box(["IRS", "publications", "several years"], 2.4, 1.7,
                         FG, 24, dashed=True).shift(LEFT * 4.95)
        pg = label_box(["Postgres", "treaty tables"], 2.7, 1.25, BLUE, 24,
                       dashed=True).shift(LEFT * 1.65 + UP * 1.05)
        rt = label_box(["retrieval", "finds the passage"], 2.7, 1.25, BLUE, 24,
                       dashed=True).shift(LEFT * 1.65 + DOWN * 1.15)
        ag = label_box(["agent", "MCP server", "in Claude Code"], 2.6, 1.7,
                       AMBER, 24, dashed=True).shift(RIGHT * 1.6)
        out = label_box(["cite", "or refuse"], 2.3, 1.7, GREEN, 28,
                        dashed=True, sub_color=GREEN).shift(RIGHT * 4.95)

        self.pin("A pipeline will ingest")
        self.play(FadeIn(pubs, shift=RIGHT * 0.2), run_time=0.8)

        a_pg = arrow(pubs[0].get_right() + UP * 0.35, pg[0].get_left())
        self.pin("Treaty tables")
        self.play(GrowArrow(a_pg), FadeIn(pg, shift=RIGHT * 0.2), run_time=0.8)
        look = T("numbers looked up, not generated", 18, BLUE)
        look.next_to(pg, UP, buff=0.22)
        self.pin("so numbers are looked up")
        self.play(Write(look), run_time=0.9)

        a_rt = arrow(pubs[0].get_right() + DOWN * 0.35, rt[0].get_left())
        self.pin("Retrieval finds")
        self.play(GrowArrow(a_rt), FadeIn(rt, shift=RIGHT * 0.2), run_time=0.8)

        a_ag1 = arrow(pg[0].get_right(), ag[0].get_left() + UP * 0.4)
        a_ag2 = arrow(rt[0].get_right(), ag[0].get_left() + DOWN * 0.4)
        self.pin("and an agent")
        self.play(GrowArrow(a_ag1), GrowArrow(a_ag2),
                  FadeIn(ag, shift=RIGHT * 0.2), run_time=0.9)

        a_out = arrow(ag[0].get_right(), out[0].get_left(), GREEN)
        self.pin("answers only with")
        self.play(GrowArrow(a_out), FadeIn(out, shift=RIGHT * 0.2), run_time=0.8)
        self.lock()


# ==================================================================== B07
class B07_Versions(Beat):
    beat_id, kicker = "B07", "VERSIONED SOURCES"
    source = "clarifications: noted in TEST-NOTES.md"

    def construct(self):
        self.chrome()
        self.add(proposed_badge())

        def doc(lines, color, x, y, h=2.5):
            d = doc_icon(2.5, h, color, lines=3).move_to([x, y, 0])
            t = VGroup(*[T(s, 20, color, max_w=2.1) for s in lines]).arrange(DOWN, buff=0.08)
            t.move_to(d[0].get_top() + DOWN * 0.55 + LEFT * 0.15)
            d[2].next_to(t, DOWN, buff=0.25)
            return VGroup(d, t)

        orig = doc([N["tax_year"], "instructions"], FG, -4.6, 0.95)
        self.play(FadeIn(orig, shift=UP * 0.2), run_time=0.8)

        clar = doc([N["tax_year"], "clarified"], VIOLET, -1.0, 0.95)
        a1 = arrow(orig[0][0].get_right(), clar[0][0].get_left())
        stamp = badge("CLARIFIED", VIOLET, fs=18).rotate(12 * DEGREES)
        stamp.move_to(clar[0][0].get_center() + DOWN * 0.55)
        self.pin("published clarifications")
        self.play(GrowArrow(a1), FadeIn(clar, shift=RIGHT * 0.2), run_time=0.9)
        self.play(FadeIn(stamp, scale=1.4), run_time=0.4)

        chip = label_box(["answer", "tax year %s" % N["tax_year"]], 3.3, 1.3,
                         GREEN, 26, sub_color=GREEN).move_to([3.6, 0.95, 0])
        a2 = arrow(clar[0][0].get_right(), chip[0].get_left(), GREEN)
        self.pin("every answer will carry")
        self.play(GrowArrow(a2), FadeIn(chip), run_time=0.8)

        new = doc(["next year's", "documents"], DIM, -4.6, -1.75, h=1.9)
        self.pin("a new year's documents")
        self.play(FadeIn(new, shift=UP * 0.2), run_time=0.7)

        posts = VGroup(Line(UP * 0.6, DOWN * 0.6, stroke_width=6, color=FG).shift(LEFT * 0.45),
                       Line(UP * 0.6, DOWN * 0.6, stroke_width=6, color=FG).shift(RIGHT * 0.45),
                       Line(LEFT * 0.45, RIGHT * 0.45, stroke_width=6, color=AMBER).shift(UP * 0.15))
        gate = posts.move_to([-1.0, -1.6, 0])
        glab = T("human approves", 20, AMBER).next_to(gate, DOWN, buff=0.2)
        b1 = arrow(new[0][0].get_right(), gate.get_left())
        self.pin("only after a human")
        self.play(GrowArrow(b1), Create(gate), Write(glab), run_time=0.9)

        live = label_box(["LIVE"], 2.2, 1.0, GREEN, 30).move_to([3.6, -1.6, 0])
        b2 = arrow(gate.get_right(), live[0].get_left(), GREEN)
        self.pin("approves the update")
        self.play(GrowArrow(b2), FadeIn(live, scale=1.1), run_time=0.7)
        self.lock()


# ==================================================================== B08
class B08_FirstMinute(Beat):
    beat_id, kicker = "B08", "THE FIRST MINUTE"
    source = "constructed mock-up · no real output"

    def construct(self):
        self.chrome()
        mock = badge("CONSTRUCTED MOCK-UP", RED, fs=28).move_to(UP * 2.5)
        self.add(mock)      # on screen for the whole beat

        term = RoundedRectangle(corner_radius=0.12, width=11.2, height=4.15,
                                stroke_width=3, stroke_color=DIM).move_to(DOWN * 0.8)
        bar = Line(term.get_corner(UL) + DOWN * 0.45, term.get_corner(UR) + DOWN * 0.45,
                   stroke_width=2, color=DIM)
        dots = VGroup(*[Dot(radius=0.07, color=c) for c in (RED, AMBER, GREEN)])
        dots.arrange(RIGHT, buff=0.14).move_to(term.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.23)
        who = T("reviewer: hiring manager, AI / data engineering", 20, DIM)
        who.next_to(term, UP, buff=0.2).align_to(term, LEFT)
        self.pin("A hiring manager")
        self.play(Create(term), Create(bar), FadeIn(dots), FadeIn(who), run_time=0.9)

        x0 = term.get_left()[0] + 0.4
        spec = [
            ("$ ./demo", FG, "they will run one command", 0),
            ("> ask: <a tax question>", FG, "ask a question", 0),
            ("answer · [IRS passage] · [tax year]", GREEN, "see a cited answer", 1),
            ("> ask: <an out-of-scope question>", FG, "ask something out of scope", 0),
            ("REFUSED: not covered by IRS publications", AMBER, "see a refusal", 1),
            ("SCOREBOARD   correct —   wrong —   refused —", FG, "then check the evaluation", 0),
        ]
        y = bar.get_center()[1] - 0.45
        for k, (s, col, cue, indent) in enumerate(spec):
            line = T(s, 22, col)
            if k == len(spec) - 1:
                y -= 0.2            # set the scoreboard apart from the session
            # indent by offset: Pango drops leading spaces from the width
            line.move_to([x0 + 0.5 * indent + line.width / 2, y, 0])
            y -= 0.55
            self.pin(cue, lead=0.25)
            self.play(AddTextLetterByLetter(line, run_time=min(0.9, 0.03 * len(s))))
        self.lock()


# ==================================================================== B09
class B09_Proves(Beat):
    beat_id, kicker = "B09", "WHAT IT WILL PROVE"
    source = "plan only · evidence will exist"

    def construct(self):
        self.chrome()
        head = T("an AI system whose output can be checked", 28, FG).shift(UP * 2.45)
        self.play(Write(head), run_time=1.2)

        skills = [("prompt contracts", "prompt contracts"),
                  ("source grounding", "source grounding"),
                  ("bounded agent loop", "a bounded agent loop"),
                  ("small trained classifier", "a small trained classifier"),
                  ("held-out evaluation", "held out evaluation")]
        chips = VGroup()
        for i, (s, _) in enumerate(skills):
            chips.add(label_box([s], 4.6, 0.62, BLUE, 22))
        chips.arrange(DOWN, buff=0.18).move_to([-3.3, -0.35, 0])
        for chip, (_, cue) in zip(chips, skills):
            self.pin(cue)
            self.play(FadeIn(chip, shift=RIGHT * 0.25), run_time=0.45)

        will = T("will exist", 20, DIM).move_to([3.6, 1.45, 0])
        ev = VGroup(*[label_box([s], 3.4, 0.8, AMBER, 26, dashed=True)
                      for s in ("tests", "scoreboard", "error log")])
        ev.arrange(DOWN, buff=0.35).move_to([3.6, -0.35, 0])
        src = chips.get_right() + RIGHT * 0.15
        arrows = [arrow(src, e[0].get_left(), AMBER) for e in ev]
        for k, cue in enumerate(["The evidence will be the tests", "the scoreboard",
                                 "a log of where"]):
            self.pin(cue)
            anims = [GrowArrow(arrows[k]), FadeIn(ev[k], shift=LEFT * 0.2)]
            if k == 0:
                anims.append(FadeIn(will))
            self.play(*anims, run_time=0.6)
        self.lock()


# ==================================================================== B10
class B10_Scope(Beat):
    beat_id, kicker = "B10", "SCOPE"
    source = "source: PROJECT-BRIEF.md"

    def construct(self):
        self.chrome()
        div = Line(UP * 2.4, DOWN * 2.6, stroke_width=2, color=DIM)
        out_h = T("OUT", 36, RED).move_to([-3.3, 2.0, 0])
        self.play(Create(div), Write(out_h), run_time=0.7)

        def struck(s, y, cue):
            t = T(s, 24, FG, max_w=5.4).move_to([-3.3, y, 0])
            ln = Line(t.get_left() + LEFT * 0.15, t.get_right() + RIGHT * 0.15,
                      color=RED, stroke_width=5)
            self.pin(cue)
            self.play(Write(t), run_time=0.6)
            self.play(Create(ln), run_time=0.35)

        struck("personal tax advice", 0.9, "give personal tax advice")
        struck("preparing or filing a return", -0.1, "or prepare or file")

        first_h = T("FIRST", 36, GREEN).move_to([3.3, 2.0, 0])
        self.pin("What comes first")
        self.play(Write(first_h), run_time=0.6)

        f1 = T("%s tax year · %s publication" % (N["first_tax_years"], N["first_publications"]),
               24, FG, max_w=5.4).move_to([3.3, 0.9, 0])
        f2 = T("%s held-out questions" % N["first_heldout_questions"], 24, FG,
               max_w=5.4).move_to([3.3, -0.1, 0])
        self.pin("one tax year")
        self.play(Write(f1), run_time=0.7)
        self.pin("ten held out")
        self.play(Write(f2), run_time=0.7)

        box = frame_box(5.6, 1.0, GREEN, dashed=True).move_to([3.3, -1.45, 0])
        ok = tick(GREEN, 0.42).move_to(box.get_left() + RIGHT * 0.38)
        pas = T("tests pass on a fresh clone", 22, GREEN, max_w=4.4)
        pas.next_to(ok, RIGHT, buff=0.18)
        # the overlap check only compares text with text; keep this label
        # inside its own box explicitly
        if REAL_MANIM and pas.get_right()[0] > box.get_right()[0] - 0.2:
            raise RuntimeError("%s: pass label overflows its box" % self.beat_id)
        will = T("will run", 18, DIM).next_to(box, DOWN, buff=0.18)
        self.pin("You will know it ran")
        self.play(Create(box), FadeIn(will), run_time=0.7)
        self.pin("the tests pass")
        self.play(Write(pas), run_time=0.8)
        self.pin("fresh clone")
        self.play(Create(ok), run_time=0.5)
        self.lock()


# ==================================================================== B11
class B11_Risk(Beat):
    beat_id, kicker = "B11", "RISK: EXTRACTION ERRORS"
    source = "plan only · nothing built yet"

    def construct(self):
        self.chrome()
        self.add(proposed_badge())

        page = doc_icon(2.9, 3.8, FG, lines=6).move_to([-4.3, 0.1, 0])
        self.play(Create(page[0]), Create(page[1]), FadeIn(page[2]), run_time=0.9)

        rows, cols, cw, ch = 4, 3, 1.25, 0.62
        cells = VGroup()
        for r in range(rows):
            for c in range(cols):
                b = Rectangle(width=cw, height=ch, stroke_width=2, stroke_color=FG)
                bar = Rectangle(width=cw * (0.45 if (r + c) % 2 else 0.6), height=0.12,
                                stroke_width=0, fill_color=DIM, fill_opacity=1)
                cells.add(VGroup(b, bar.move_to(b)))
        cells.arrange_in_grid(rows, cols, buff=0).move_to([1.6, 0.1, 0])
        ex = arrow(page[0].get_right(), cells.get_left(), FG)
        exl = T("extract", 20, DIM).next_to(ex, UP, buff=0.12)
        self.pin("Extracting tables")
        self.play(GrowArrow(ex), FadeIn(exl), LaggedStart(
            *[FadeIn(c) for c in cells], lag_ratio=0.04), run_time=1.2)

        bad = cells[4]
        self.pin("a bad extraction")
        # the cell's value bar turns light with it: grey on red is 2.8:1 (GATE T)
        self.play(bad[0].animate.set_fill(RED, opacity=0.45).set_stroke(RED, width=4),
                  bad[1].animate.set_fill(FG), run_time=0.6)

        one = T("start: %s publication" % N["first_publications"], 22, DIM)
        one.next_to(page, DOWN, buff=0.25)
        self.pin("start with one publication")
        self.play(FadeIn(one), run_time=0.6)

        glass = VGroup(Circle(radius=0.42, color=AMBER, stroke_width=5),
                       Line(ORIGIN, DR * 0.5, color=AMBER, stroke_width=7)
                       .shift(DR * 0.3)).move_to(page[0].get_center())
        self.pin("check extracted values")
        self.play(FadeIn(glass), run_time=0.3)
        self.play(glass.animate.move_to(bad.get_center() + DR * 0.1), run_time=1.1)
        ok = tick(GREEN, 0.38).move_to(bad)
        self.pin("by hand", lead=0.1)
        self.play(FadeOut(glass), bad[0].animate.set_fill(GREEN, opacity=0.25)
                  .set_stroke(GREEN, width=4), FadeOut(bad[1]), Create(ok), run_time=0.6)

        rest = [c for k, c in enumerate(cells) if k != 4]
        tag = T("unchecked = UNVERIFIED", 22, AMBER).next_to(cells, DOWN, buff=0.35)
        self.pin("mark anything unchecked")
        self.play(*[c[0].animate.set_stroke(AMBER, width=2) for c in rest],
                  Write(tag), run_time=0.9)
        self.lock()


# ==================================================================== B12
class B12_Why(Beat):
    beat_id, kicker = "B12", "WHY THIS PROJECT"
    source = "source: PROJECT-BRIEF.md"

    def construct(self):
        self.chrome()
        div = Line(UP * 2.5, DOWN * 2.6, stroke_width=2, color=DIM)
        have = T("ALREADY HAVE", 30, GREEN).move_to([-3.3, 2.15, 0])
        new = T("NEW TO ME", 30, VIOLET).move_to([3.3, 2.15, 0])
        self.play(Create(div), Write(have), Write(new), run_time=1.0)

        left = [("Python", "Python,"), ("data cleaning", "data cleaning"),
                ("testing", "and testing")]
        for k, (s, cue) in enumerate(left):
            t = T(s, 26, FG).move_to([-3.3, 1.2 - 0.68 * k, 0])
            self.pin(cue)
            self.play(FadeIn(t, shift=RIGHT * 0.2), run_time=0.4)

        pr = label_box(["Reallocation Engine", "pull request %s" % N["pr_number"]],
                       4.4, 1.15, GREEN, 22).move_to([-3.3, -1.55, 0])
        self.pin("my Reallocation Engine")
        self.play(FadeIn(pr, shift=UP * 0.15), run_time=0.6)

        right = [("MCP servers", "M C P servers"),
                 ("retrieval evaluation", "retrieval evaluation"),
                 ("rules engines", "rules engines"),
                 ("a classifier from scratch", "training a classifier")]
        for k, (s, cue) in enumerate(right):
            t = T(s, 26, FG, max_w=5.6).move_to([3.3, 1.2 - 0.68 * k, 0])
            self.pin(cue)
            self.play(FadeIn(t, shift=LEFT * 0.2), run_time=0.4)
        self.pin("are new to me")
        self.play(Indicate(new, color=VIOLET, scale_factor=1.1), run_time=0.8)
        self.lock()


# ==================================================================== B13
class B13_Close(Beat):
    beat_id, kicker = "B13", "EXISTS TODAY · WILL EXIST"
    source = "Kokoro · Manim CE · FFmpeg · Brutalist"

    def construct(self):
        self.chrome()
        div = Line(UP * 2.5, DOWN * 2.6, stroke_width=2, color=DIM)
        ex_h = T("EXISTS TODAY", 30, GREEN).move_to([-3.3, 2.15, 0])
        will_h = T("WILL EXIST", 30, AMBER).move_to([3.3, 2.15, 0])
        self.play(Create(div), Write(ex_h), run_time=0.7)

        exists = [("this plan", "this plan"), ("my test notes", "my test notes"),
                  ("one IRS document check", "and one check")]
        # done = solid tick; not built = dashed hollow marker
        left = VGroup()
        for k, (s, cue) in enumerate(exists):
            t = T(s, 26, FG).move_to([-2.95, 1.15 - 0.8 * k, 0])
            ok = tick(GREEN, 0.34).next_to(t, LEFT, buff=0.3)
            left.add(VGroup(ok, t))
            self.pin(cue)
            self.play(Create(ok), FadeIn(t, shift=RIGHT * 0.2), run_time=0.45)

        later = ["ingestion pipeline", "Postgres treaty tables", "retrieval",
                 "agent + MCP server", "out-of-scope classifier", "held-out evaluation"]
        right = VGroup()
        for s in later:
            mark = DashedVMobject(Square(0.3, stroke_width=3, color=AMBER), num_dashes=8)
            right.add(VGroup(mark, T(s, 22, AMBER, max_w=4.6)).arrange(RIGHT, buff=0.3))
        right.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([3.3, -0.2, 0])
        self.pin("Everything else is will")
        self.play(Write(will_h), LaggedStart(*[Create(r[0]) for r in right],
                                             lag_ratio=0.1),
                  LaggedStart(*[FadeIn(r[1]) for r in right], lag_ratio=0.12),
                  run_time=1.1)

        self.pin("Cite or Refuse.", lead=0.5)
        self.play(FadeOut(VGroup(div, ex_h, will_h, left, right)), run_time=0.45)
        name = T("CITE OR REFUSE", 56, FG).shift(UP * 0.9)
        who = T("Swathi Baba Eswarappa", 32, FG).shift(DOWN * 0.2)
        crs = T("%s · Final Project Pitch" % N["course"], 22, DIM).shift(DOWN * 0.9)
        self.play(FadeIn(name, shift=UP * 0.2), run_time=0.5)
        self.pin("Swathi Baba", lead=0.2)
        self.play(FadeIn(who), run_time=0.5)
        self.pin("INFO seven", lead=0.2)
        self.play(FadeIn(crs), run_time=0.5)
        self.lock()


SCENES = [b["graphic"]["manim"] for b in SHEET["beats"]]
