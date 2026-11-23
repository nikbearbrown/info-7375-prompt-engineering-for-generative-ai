"""scenes.py — Manim scenes for agent-proving-ground-progress (progress film, through M5).

Same chassis as the October pitch (youtube/brutalist/agent-proving-ground/scenes.py):
top rail, Text built at one reference size and scaled down, white cards, audio-
clocked _hold, sentence-timed cues, and the same NEUTRAL palette. No product,
brand or channel styling, no logos, no people, no mascots. Colour carries
meaning only: red marks a failure, a denial or a limit; green appears only on PASS.

Show-tell approach: one simple picture per beat, minimal on-screen text, the
narration carries the explanation.

Two kinds of beat:
- CONSTRUCTED (B01-B05, B13): drawn diagrams; the rail carries a "Constructed"
  pill for the whole beat.
- REAL (B06-B12): terminal-style frames whose text is copied from the captures in
  evidence/<beat>.txt (taken 2026-11-23, read-only, from the APG repo). Each frame's
  title bar shows the source path and the source's own date; the rail carries a
  "Real output" pill. Long lines are cut with "…", never reworded.

Timing: _until(scene, beat, phrase) waits for the phrase (sentence onsets measured
by sentence_audio.py). _play() keeps every animation off the 50% and 85% frames
that Gate T / Gate V sample, so nothing is half-faded there.
"""
import json
from pathlib import Path

import numpy as np
from manim import *

config.disable_caching = True

BG   = ManimColor("#F5F5F3")   # neutral off-white ground
INK  = ManimColor("#1F2328")   # near-black: body text and primary strokes
SOFT = ManimColor("#59636E")   # secondary text and structure (5.6:1 on BG)
CARD = ManimColor("#FFFFFF")   # card surface
BAR  = ManimColor("#E4E6E9")   # terminal title bar / highlight band
ACC  = ManimColor("#B42318")   # red: fail / denied / limit
GOOD = ManimColor("#1A7F37")   # green: PASS only

_SHEET = Path(__file__).resolve().parent / "beat_sheet.json"
try:
    _BEATS = {b["beat_id"]: b for b in json.loads(_SHEET.read_text())["beats"]}
except (OSError, ValueError, KeyError):   # pre-audio authoring / Gate A copy
    _BEATS = {}
_DUR = {k: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0.0)
        for k, b in _BEATS.items()}
_NARR = {k: b.get("narration_text", "") for k, b in _BEATS.items()}
_SENT = {k: b.get("sentences") or [] for k, b in _BEATS.items()}


def _clock(scene):
    try:
        return float(scene.renderer.time)
    except Exception:                      # Gate A's mock has no renderer clock
        return 0.0


def _cue_time(beat_id, phrase):
    text = _NARR.get(beat_id, "")
    i = text.find(phrase)
    if i < 0:
        raise ValueError(f"{beat_id}: cue {phrase!r} is not in the narration")
    pos = 0
    for s in _SENT.get(beat_id, []):
        j = text.find(s["text"], pos)
        if j <= i < j + len(s["text"]):
            if i == j:
                return float(s["start_s"]), True
            frac = (i - j) / len(s["text"])
            return float(s["start_s"]) + frac * (float(s["end_s"]) - float(s["start_s"])), False
        pos = j + len(s["text"])
    return _DUR.get(beat_id, 0.0) * i / max(len(text), 1), False


def _until(scene, beat_id, phrase, lead=0.15):
    if not _NARR.get(beat_id):
        return
    t, exact = _cue_time(beat_id, phrase)
    target = t - (0.1 if exact else lead)
    gap = target - _clock(scene)
    if gap > 0.05:
        scene.wait(gap)
    elif gap < -0.6 and _clock(scene) > 0:
        print(f"[cue-late] {beat_id} {phrase!r} {-gap:.2f}s late", flush=True)


_GUARD = 0.25


def _play(scene, beat_id, *anims, run_time=0.5):
    """play(), but never across the 50% / 85% sample frames (+-_GUARD s)."""
    d = float(_DUR.get(beat_id) or 0.0)
    if d > 0:
        for frac in (0.5, 0.85):
            m = d * frac
            t = _clock(scene)
            if t < m + _GUARD and t + run_time > m - _GUARD:
                scene.wait(m + _GUARD - t)
    scene.play(*anims, run_time=run_time)


def _hold(scene, beat_id, minimum=0.05):
    target = float(_DUR.get(beat_id) or 0.0)
    scene.wait(max(target - _clock(scene) - 0.02, minimum))


_TEXT_REF = 96.0
MONO = "Menlo"


def _label(text, size=24, color=None, weight=None):
    kw = {"font_size": _TEXT_REF, "color": color or INK}
    if weight:
        kw["weight"] = weight
    return Text(text, **kw).scale(size / _TEXT_REF)


# Pango wraps a Text line at the render's pixel width, so long mono lines built
# at 96 pt wrap in low-resolution previews. Mono text uses a 48 pt reference.
_MONO_REF = 48.0


def _mono(text, size=22, color=None, weight=None):
    kw = {"font": MONO, "font_size": _MONO_REF, "color": color or INK}
    if weight:
        kw["weight"] = weight
    return Text(text, **kw).scale(size / _MONO_REF)


# Menlo advance per character at size 22 (60 chars measure 10.98 units).
_CW22 = 10.98 / 60


def _left(mob, x, y):
    mob.move_to([0.0, y, 0])
    mob.align_to([x, 0.0, 0], LEFT)
    return mob


def _rail(kind):
    """Top rail: project kicker left, 'Constructed' or 'Real output' pill right."""
    g = VGroup()
    k = _label("AGENT PROVING GROUND · PROGRESS", size=15, color=SOFT)
    k.to_edge(LEFT, buff=1.11).set_y(3.18)
    g.add(k)
    t = _label("Constructed" if kind == "constructed" else "Real output", size=17)
    pill = RoundedRectangle(corner_radius=0.16, width=t.width + 0.42, height=0.38,
                            color=INK, stroke_width=1.6)
    t.move_to(pill.get_center())
    tag = VGroup(pill, t)
    tag.to_edge(RIGHT, buff=1.11).set_y(3.18)
    g.add(tag)
    g.add(Line([-6.0, 2.92, 0], [6.0, 2.92, 0], color=SOFT, stroke_width=1.2))
    return g


def _card(w, h, x, y, stroke=None):
    return RoundedRectangle(corner_radius=0.12, width=w, height=h,
                            color=stroke or SOFT, fill_color=CARD, fill_opacity=1.0,
                            stroke_width=2.0).move_to([x, y, 0])


def _chip(text, size=24, color=None, mono=False):
    t = _mono(text, size=size, color=color) if mono else _label(text, size=size, color=color)
    box = RoundedRectangle(corner_radius=0.14, width=t.width + 0.5, height=t.height + 0.36,
                           color=SOFT, fill_color=CARD, fill_opacity=1.0, stroke_width=2.0)
    t.move_to(box.get_center())
    return VGroup(box, t)


def _tick(x, y, s=0.22, color=None, width=5.0):
    m = VMobject(stroke_color=color or INK, stroke_width=width)
    m.set_points_as_corners([[x - s, y, 0], [x - 0.3 * s, y - 0.65 * s, 0],
                             [x + s, y + 0.75 * s, 0]])
    return m


def _cross(x, y, s=0.2, color=None, width=5.0):
    c = color or ACC
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=c, stroke_width=width),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=c, stroke_width=width))


def _bubble(w, h, x, y):
    body = RoundedRectangle(corner_radius=0.3, width=w, height=h, color=SOFT,
                            fill_color=CARD, fill_opacity=1.0, stroke_width=2.0)
    body.move_to([x, y, 0])
    by = y - h / 2
    tail = VMobject(stroke_color=SOFT, stroke_width=2.0, fill_color=CARD, fill_opacity=1.0)
    tail.set_points_as_corners([[x - w * 0.26, by + 0.04, 0], [x - w * 0.39, by - 0.55, 0],
                                [x - w * 0.13, by + 0.04, 0]])
    return VGroup(body, tail)


# ── terminal frame ─────────────────────────────────────────────────────────────
_LINE = 0.40      # line pitch at size 22
_PAD = 0.18


def _term(path, date, lines, top, w=11.8, x=0.0, size=22):
    """A terminal-style card. `lines` is a list of (text, color) or text.
    Returns dict: frame (card+bar+dots+path+date), lines (list of Text), and
    row_y(i) for highlight placement. `top` is the card's top edge."""
    n = len(lines)
    bar_h = 0.45
    h = bar_h + 2 * _PAD + n * _LINE
    cy = top - h / 2
    card = _card(w, h, x, cy, stroke=SOFT)
    bar = Rectangle(width=w - 0.04, height=bar_h, stroke_width=0, fill_color=BAR,
                    fill_opacity=1.0).move_to([x, top - bar_h / 2 - 0.02, 0])
    dots = VGroup(*[Circle(radius=0.07, stroke_width=1.5, color=SOFT)
                    .move_to([x - w / 2 + 0.3 + i * 0.25, top - bar_h / 2, 0]) for i in range(3)])
    ptxt = _mono(path, size=18)
    dtxt = _mono(date, size=18)
    avail = w - 1.3 - dtxt.width - 0.4
    if ptxt.width > avail:
        ptxt.scale(avail / ptxt.width)
    _left(ptxt, x - w / 2 + 1.1, top - bar_h / 2)
    dtxt.move_to([0, top - bar_h / 2, 0]).align_to([x + w / 2 - 0.25, 0, 0], RIGHT)
    frame = VGroup(card, bar, dots, ptxt, dtxt)
    mobs = []
    y0 = top - bar_h - _PAD - _LINE / 2
    for i, ln in enumerate(lines):
        text, color = (ln, None) if isinstance(ln, str) else ln
        # Pango drops leading spaces (even no-break ones), so an indent is
        # rebuilt as an x offset of that many character widths.
        lead = len(text) - len(text.lstrip(" "))
        t = _mono(text[lead:] if text.strip() else " ", size=size, color=color)
        indent = lead * _CW22 * size / 22
        if t.width + indent > w - 0.6:
            k = (w - 0.6) / (t.width + indent)
            t.scale(k)
            indent *= k
        _left(t, x - w / 2 + 0.3 + indent, y0 - i * _LINE)
        mobs.append(t)
    return {"frame": frame, "lines": mobs, "row_y": lambda i: y0 - i * _LINE,
            "x": x, "w": w, "bottom": top - h}


def _band(term, i, j=None, color=None):
    """Highlight band behind rows i..j (drawn as an outline, so it never covers text)."""
    j = i if j is None else j
    ya, yb = term["row_y"](i) + _LINE / 2, term["row_y"](j) - _LINE / 2
    return Rectangle(width=term["w"] - 0.25, height=ya - yb, stroke_width=3,
                     color=color or INK).move_to([term["x"], (ya + yb) / 2, 0])


# ─────────────────────────────────────────────────────────────────────────────
#  B01 — Hello. Title card. CONSTRUCTED.
# ─────────────────────────────────────────────────────────────────────────────
class B01_Hello(Scene):

    def construct(self):
        self.camera.background_color = BG
        rail = _rail("constructed")
        name = _label("Tushar Patel", size=52, weight="BOLD").move_to([0.0, 1.55, 0])
        who = _label("software engineering student · Northeastern", size=26, color=SOFT)
        who.move_to([0.0, 0.85, 0])
        rule = Line([-4.6, 0.25, 0], [4.6, 0.25, 0], color=SOFT, stroke_width=1.5)
        title = _label("Agent Proving Ground", size=60, weight="BOLD").move_to([0.0, -0.75, 0])
        sub = _label("progress film · through M5", size=28, color=SOFT).move_to([0.0, -1.6, 0])
        row = VGroup(*[_card(1.5, 0.6, x, -2.5) for x in (-3.6, -1.2, 1.2, 3.6)])
        words = VGroup(*[_label(w, size=20, color=SOFT).move_to([x, -2.5, 0])
                         for w, x in zip(("sandbox", "trace", "check", "verdict"),
                                         (-3.6, -1.2, 1.2, 3.6))])

        self.add(rail)
        _play(self, "B01", FadeIn(name), LaggedStart(*[FadeIn(c) for c in row], lag_ratio=0.15),
              FadeIn(words), run_time=0.6)
        _until(self, "B01", "a software engineering student")
        _play(self, "B01", FadeIn(who), Create(rule), run_time=0.5)
        _until(self, "B01", "This is my final project")
        _play(self, "B01", Write(title), run_time=0.8)
        _play(self, "B01", FadeIn(sub), run_time=0.5)
        _hold(self, "B01")


# ─────────────────────────────────────────────────────────────────────────────
#  B02 — The problem. "Done!" beside a failing test; three things "done" can hide.
# ─────────────────────────────────────────────────────────────────────────────
class B02_Done(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        bubble = _bubble(4.4, 2.4, -3.2, 0.7)
        who = _label("agent", size=20, color=SOFT).move_to([-3.2, 2.3, 0])
        said = _label("Done!", size=44, weight="BOLD").move_to([-3.2, 0.7, 0])

        run = _card(4.4, 2.4, 3.2, 0.7)
        src = _label("test run", size=20, color=SOFT).move_to([3.2, 2.3, 0])
        x = _cross(0.0, 0.0, s=0.2)
        fail = _mono("1 failed", size=30, color=ACC)
        VGroup(x, fail).arrange(RIGHT, buff=0.3).move_to([3.2, 0.7, 0])
        neq = _label("≠", size=72, color=SOFT).move_to([0.0, 0.7, 0])

        xs = (-4.2, 0.0, 4.2)
        maybe = [_chip(t, size=24) for t in ("fixed the bug?", "changed the test?", "just stopped?")]
        for c, cx in zip(maybe, xs):
            c.move_to([cx, -2.2, 0])
        links = [Line([-3.2, -1.15, 0], [cx, -1.75, 0], color=SOFT, stroke_width=2) for cx in xs]

        _play(self, "B02", FadeIn(bubble), FadeIn(who), run_time=0.4)
        _until(self, "B02", "says \"done,\"")
        _play(self, "B02", Write(said), run_time=0.5)
        _until(self, "B02", "that isn't the same")
        _play(self, "B02", FadeIn(run), FadeIn(src), Create(x), FadeIn(fail), FadeIn(neq), run_time=0.6)
        for cue, link, chip in zip(("fixed the bug", "quietly changed the test", "just stopped"),
                                   links, maybe):
            _until(self, "B02", cue)
            _play(self, "B02", Create(link), FadeIn(chip), run_time=0.4)
        _hold(self, "B02")


# ─────────────────────────────────────────────────────────────────────────────
#  B03 — What it is: sandbox -> trace -> check -> PASS/FAIL.
# ─────────────────────────────────────────────────────────────────────────────
class B03_Loop(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        y = 0.3
        xs = (-4.65, -1.55, 1.55, 4.65)
        boxes = [_card(2.6, 3.0, x, y) for x in xs]
        names = [_label(n, size=28, weight="BOLD").move_to([x, y + 1.05, 0])
                 for n, x in zip(("sandbox", "trace", "check", "verdict"), xs)]
        wall = DashedVMobject(Rectangle(width=1.7, height=1.0, color=INK, stroke_width=2.5),
                              num_dashes=24).move_to([xs[0], y - 0.35, 0])
        agent = Dot([xs[0] - 0.4, y - 0.35, 0], radius=0.12, color=INK)
        steps = VGroup(*[VGroup(Dot([xs[1] - 0.7, y + dy, 0], radius=0.06, color=INK),
                                Line([xs[1] - 0.45, y + dy, 0], [xs[1] + 0.75, y + dy, 0],
                                     color=INK, stroke_width=3))
                         for dy in (0.0, -0.35, -0.7)])
        tests = _mono("tests", size=24).move_to([xs[2] - 0.25, y - 0.35, 0])
        ok = _tick(xs[2] + 0.65, y - 0.35, s=0.2, width=6)
        pas = _label("PASS", size=30, weight="BOLD", color=GOOD).move_to([xs[3], y - 0.15, 0])
        fai = _label("FAIL", size=30, weight="BOLD", color=ACC).move_to([xs[3], y - 0.7, 0])
        arrows = [Arrow([x + 1.33, y, 0], [x + 1.77, y, 0], buff=0, color=SOFT,
                        stroke_width=3, tip_length=0.14) for x in xs[:3]]

        word = _bubble(2.6, 0.8, 1.55, -2.05)
        wtxt = _label("\"done\"", size=24, color=SOFT).move_to([1.55, -2.05, 0])
        wx = _cross(3.25, -2.05, s=0.18)
        laptop = VGroup(RoundedRectangle(corner_radius=0.08, width=2.4, height=1.4, color=INK,
                                         stroke_width=2.5).move_to([-3.1, -2.05, 0]),
                        Polygon([-4.6, -2.95, 0], [-1.6, -2.95, 0], [-1.85, -2.75, 0],
                                [-4.35, -2.75, 0], color=INK, stroke_width=2.5))
        local = _label("local · cheap", size=24).move_to([-3.1, -2.05, 0])

        _play(self, "B03", FadeIn(boxes[0]), FadeIn(names[0]), FadeIn(agent), run_time=0.5)
        _until(self, "B03", "inside a locked sandbox")
        _play(self, "B03", Create(wall), agent.animate.shift(RIGHT * 0.4), run_time=0.6)
        _until(self, "B03", "It records every step")
        _play(self, "B03", GrowArrow(arrows[0]), FadeIn(boxes[1]), FadeIn(names[1]), run_time=0.5)
        _play(self, "B03", LaggedStart(*[Create(s) for s in steps], lag_ratio=0.3), run_time=0.8)
        _until(self, "B03", "it decides pass or fail")
        _play(self, "B03", GrowArrow(arrows[1]), FadeIn(boxes[2]), FadeIn(names[2]), FadeIn(tests),
              Create(ok), run_time=0.6)
        _play(self, "B03", GrowArrow(arrows[2]), FadeIn(boxes[3]), FadeIn(names[3]),
              FadeIn(pas), FadeIn(fai), run_time=0.6)
        _until(self, "B03", "never with the agent's word")
        _play(self, "B03", FadeIn(word), FadeIn(wtxt), Create(wx), run_time=0.5)
        _until(self, "B03", "a cheap, local way")
        _play(self, "B03", Create(laptop), FadeIn(local), run_time=0.6)
        _hold(self, "B03")


# ─────────────────────────────────────────────────────────────────────────────
#  B04 — Others. One card per tool, in the October PROJECT-BRIEF.md wording.
# ─────────────────────────────────────────────────────────────────────────────
class B04_Others(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        xs = (-4.15, 0.0, 4.15)
        y = 0.35
        cards = [_card(3.8, 3.9, x, y) for x in xs]
        names = [_label("E2B", size=34, weight="BOLD"),
                 _label("Langfuse", size=34, weight="BOLD"),
                 _label("AI Proving Ground", size=28, weight="BOLD")]
        for n, x in zip(names, xs):
            n.move_to([x, y + 1.45, 0])
        what = [_label("sandboxes for", size=22, color=SOFT),
                _label("traces and scores", size=22, color=SOFT),
                _label("a Drupal project", size=22, color=SOFT)]
        what2 = [_label("AI-generated code", size=22, color=SOFT), None,
                 _label("grades what was saved", size=22, color=SOFT)]
        for i, x in enumerate(xs):
            what[i].move_to([x, y - 1.05, 0])
            if what2[i] is not None:
                what2[i].move_to([x, y - 1.45, 0])
        # one small picture each: a sandbox wall, a trace, a check
        wall = VGroup(DashedVMobject(Rectangle(width=1.6, height=1.0, color=INK, stroke_width=2.5),
                                     num_dashes=22),
                      Dot(radius=0.1, color=INK)).move_to([xs[0], y + 0.25, 0])
        trace = VGroup(*[VGroup(Dot([xs[1] - 0.65, y + 0.6 - k * 0.35, 0], radius=0.06, color=INK),
                                Line([xs[1] - 0.4, y + 0.6 - k * 0.35, 0],
                                     [xs[1] + 0.75, y + 0.6 - k * 0.35, 0], color=INK, stroke_width=3))
                         for k in range(3)])
        saved = VGroup(Rectangle(width=0.9, height=1.0, color=INK, stroke_width=2.5)
                       .move_to([xs[2] - 0.45, y + 0.25, 0]),
                       _tick(xs[2] + 0.75, y + 0.25, s=0.24, width=6))
        only = _chip("Drupal sites only", size=22, color=ACC).move_to([xs[2], -2.35, 0])

        _until(self, "B04", "Pieces of this already exist")
        _play(self, "B04", LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.2), run_time=0.7)
        _until(self, "B04", "E2B provides")
        _play(self, "B04", FadeIn(names[0]), Create(wall), FadeIn(what[0]), FadeIn(what2[0]), run_time=0.6)
        _until(self, "B04", "Langfuse records")
        _play(self, "B04", FadeIn(names[1]), Create(trace), FadeIn(what[1]), run_time=0.6)
        _until(self, "B04", "And a Drupal project")
        _play(self, "B04", FadeIn(names[2]), Create(saved), FadeIn(what[2]), FadeIn(what2[2]), run_time=0.6)
        _until(self, "B04", "but only for Drupal sites")
        _play(self, "B04", FadeIn(only), run_time=0.5)
        _hold(self, "B04")


# ─────────────────────────────────────────────────────────────────────────────
#  B05 — Why mine. Four pieces in one loop, on a laptop, with a failure log.
# ─────────────────────────────────────────────────────────────────────────────
class B05_WhyMine(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        screen = RoundedRectangle(corner_radius=0.12, width=8.6, height=4.3, color=INK,
                                  stroke_width=3).move_to([-1.2, 0.45, 0])
        base = Polygon([-6.0, -1.95, 0], [3.6, -1.95, 0], [3.2, -1.65, 0], [-5.6, -1.65, 0],
                       color=INK, stroke_width=3)
        pos = {"sandbox": (-3.3, 1.45), "trace": (0.9, 1.45),
               "check": (0.9, -0.55), "you approve": (-3.3, -0.55)}
        nodes = {k: _chip(k, size=26).move_to([x, y, 0]) for k, (x, y) in pos.items()}
        order = ["sandbox", "trace", "check", "you approve"]
        arrows = []
        for a, b in zip(order, order[1:] + order[:1]):
            pa, pb = np.array([*pos[a], 0.0]), np.array([*pos[b], 0.0])
            d = pb - pa
            u = d / np.linalg.norm(d)
            off = 1.6 if abs(u[0]) > 0.5 else 0.42
            arrows.append(Arrow(pa + u * off, pb - u * off, buff=0, color=SOFT,
                                stroke_width=3, tip_length=0.18))
        log = VGroup(Rectangle(width=1.7, height=2.1, color=SOFT, stroke_width=2.5)
                     .move_to([5.0, 0.45, 0]),
                     *[Line([4.4, 1.05 - k * 0.35, 0], [5.6, 1.05 - k * 0.35, 0], color=SOFT,
                            stroke_width=2.5) for k in range(4)])
        logl = _label("failures", size=24).move_to([5.0, -1.0, 0])

        _play(self, "B05", Create(screen), Create(base), run_time=0.6)
        _until(self, "B05", "sandbox, trace")
        _play(self, "B05", FadeIn(nodes["sandbox"]), run_time=0.3)
        _play(self, "B05", GrowArrow(arrows[0]), FadeIn(nodes["trace"]), run_time=0.35)
        _until(self, "B05", "an independent check")
        _play(self, "B05", GrowArrow(arrows[1]), FadeIn(nodes["check"]), run_time=0.4)
        _until(self, "B05", "a human who approves")
        _play(self, "B05", GrowArrow(arrows[2]), FadeIn(nodes["you approve"]), run_time=0.4)
        _play(self, "B05", GrowArrow(arrows[3]), run_time=0.3)
        _until(self, "B05", "with every failure written down")
        _play(self, "B05", Create(log), FadeIn(logl), run_time=0.6)
        _hold(self, "B05")


# ─────────────────────────────────────────────────────────────────────────────
#  B06 — The loop, then a real run (task 001, Nov 12). REAL.
#  Source: evidence/B6.txt (PLAN.md:120; apg show of 20261112T053055Z-92239eb0).
# ─────────────────────────────────────────────────────────────────────────────
class B06_RealRun(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        # phase 1: the pod (drawn) with the agent's three tools and the hidden check
        pod = DashedVMobject(RoundedRectangle(corner_radius=0.2, width=7.8, height=4.0,
                                              color=INK, stroke_width=3), num_dashes=60)
        pod.move_to([-2.0, 0.45, 0])
        podl = _label("Kubernetes pod · no network", size=24).move_to([-2.1, 2.05, 0])
        go = _chip("built in Go", size=24).move_to([4.4, 2.15, 0])
        model = _mono("claude-haiku-5-5", size=24).move_to([-2.1, 1.1, 0])
        tools = VGroup(*[_chip(t, size=20, mono=True) for t in ("read_file", "write_file", "run_command")])
        tools.arrange(RIGHT, buff=0.25).move_to([-2.1, 0.0, 0])
        check = _card(2.8, 2.2, 4.4, 0.45)
        checkl = _label("hidden check", size=24).move_to([4.4, 1.05, 0])
        checkt = _tick(4.4, 0.1, s=0.3, width=6)
        arrow = Arrow([2.0, 0.45, 0], [2.9, 0.45, 0], buff=0, color=SOFT, stroke_width=3,
                      tip_length=0.18)
        phase1 = VGroup(pod, podl, go, model, tools, check, checkl, checkt, arrow)

        # phase 2: the real run (text copied from evidence/B6.txt)
        t1 = _term("PLAN.md:120  ·  traces/20261112T053055Z-92239eb0.json", "2026-11-12 05:30Z",
                   [("$ apg run 001                (result line recorded in PLAN.md)", SOFT),
                    ("001  PASS  steps=3  reason=check_passed", INK),
                    ("$ apg show evidence/traces/20261112T053055Z-92239eb0.json", SOFT),
                    "task     001-fix-function",
                    "model    claude-haiku-5-5",
                    "verdict  PASS  exit reason check_passed",
                    ("steps in the trace:", SOFT),
                    "1 run_command   2 run_command   3 end_turn"], top=2.72)

        _play(self, "B06", FadeIn(go), run_time=0.3)
        _until(self, "B06", "The agent is Claude Haiku")
        _play(self, "B06", Create(pod), FadeIn(model), run_time=0.6)
        _until(self, "B06", "read a file")
        _play(self, "B06", LaggedStart(*[FadeIn(t) for t in tools], lag_ratio=0.5), run_time=1.0)
        _until(self, "B06", "It works inside a Kubernetes pod")
        _play(self, "B06", FadeIn(podl), run_time=0.4)
        _until(self, "B06", "After every change")
        _play(self, "B06", GrowArrow(arrow), FadeIn(check), FadeIn(checkl), run_time=0.5)
        _play(self, "B06", Create(checkt), run_time=0.3)
        _until(self, "B06", "Here's a real run")
        _play(self, "B06", FadeOut(phase1), FadeIn(t1["frame"]), run_time=0.5)
        _play(self, "B06", *[FadeIn(m) for m in t1["lines"][:2]], run_time=0.4)
        _until(self, "B06", "it passed in three steps")
        _play(self, "B06", Create(_band(t1, 1, color=GOOD)), *[FadeIn(m) for m in t1["lines"][2:6]],
              run_time=0.5)
        _until(self, "B06", "and every step is in the trace")
        _play(self, "B06", *[FadeIn(m) for m in t1["lines"][6:]], Create(_band(t1, 7)), run_time=0.5)
        _hold(self, "B06")


# ─────────────────────────────────────────────────────────────────────────────
#  B07 — Policy and gate. REAL. Source: evidence/B7.txt.
#  Frame 1: apg show step 4 of 20261118T034327Z-b54f5cd6 (contract B, held-out, 008).
#  Frame 2: gate section of 20261113T224740Z-a9a2c258 (answered by Tushar).
# ─────────────────────────────────────────────────────────────────────────────
class B07_PolicyGate(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("traces/20261118T034327Z-b54f5cd6.json", "2026-11-18 03:43Z · Nov 17 ET",
                   [("apg show, step 4 · task 008-config-parser · contract B · held-out", SOFT),
                    "  asked:   write_file /tmp/unused.txt (1 line, 11 bytes)",
                    ("  policy:  DENIED (rule: path): path /tmp/unused.txt is", ACC),
                    ("           outside /workspace", ACC),
                    "  /workspace changed: no"], top=2.72)
        t2 = _term("evidence/traces/20261113T224740Z-a9a2c258.json  ·  gate",
                   "2026-11-13 22:48Z",
                   [("human-answered by Tushar in a real terminal (trace-schema.md:47)", SOFT),
                    "decision        approved",
                    "diff_sha256     cbdbe61d2d21943c…dd5492255c4ff61a162d7216ae86ae9850",
                    "recheck_sha256  cbdbe61d2d21943c…dd5492255c4ff61a162d7216ae86ae9850"],
                   top=t1["bottom"] - 0.25)

        _play(self, "B07", FadeIn(t1["frame"]), FadeIn(t2["frame"]), FadeIn(t1["lines"][0]),
              run_time=0.5)
        _until(self, "B07", "Every tool call goes through a policy")
        _play(self, "B07", FadeIn(t1["lines"][1]), run_time=0.4)
        _until(self, "B07", "A denied call never runs")
        _play(self, "B07", *[FadeIn(m) for m in t1["lines"][2:4]], Create(_band(t1, 2, 3, color=ACC)),
              run_time=0.5)
        _until(self, "B07", "it's just recorded")
        _play(self, "B07", FadeIn(t1["lines"][4]), run_time=0.4)
        _until(self, "B07", "And before any change leaves")
        _play(self, "B07", FadeIn(t2["lines"][0]), run_time=0.4)
        _until(self, "B07", "approve it myself")
        _play(self, "B07", FadeIn(t2["lines"][1]), run_time=0.4)
        _until(self, "B07", "My approval is bound")
        _play(self, "B07", *[FadeIn(m) for m in t2["lines"][2:]], run_time=0.5)
        _until(self, "B07", "so if the diff changes")
        _play(self, "B07", Create(_band(t2, 2, 3)), run_time=0.5)
        _hold(self, "B07")


# ─────────────────────────────────────────────────────────────────────────────
#  B08 — Data. REAL. Source: evidence/B8.txt (tasks/README.md; git show --stat 26b5305).
# ─────────────────────────────────────────────────────────────────────────────
class B08_Data(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("tasks/README.md  ·  16 task directories", "753612d · Nov 13, 2026",
                   [("## Normal tasks (expected: PASS)                        11", SOFT),
                    "001 002 003 004 005 006 007 008 009 010 011",
                    ("## Deliberate failure cases (expected: FAIL)             5", SOFT),
                    "012-wrong-test   013-needs-network   014-needs-git",
                    "015-tiny-budget  016-contradictory-spec"], top=2.72)
        t2 = _term("$ git show --stat 26b5305", "Fri Nov 13 19:36 2026 -0500",
                   ["commit 26b5305680e49e5fee1c955b7824fc0743d5f3a2",
                    "    T3.2: freeze dev/held-out split",
                    " tasks/split.json           |  65 +++++++++++++++",
                    " 4 files changed, 405 insertions(+)"], top=t1["bottom"] - 0.25)

        _play(self, "B08", FadeIn(t1["frame"]), FadeIn(t2["frame"]), run_time=0.5)
        _until(self, "B08", "Eleven are normal bugs")
        _play(self, "B08", *[FadeIn(m) for m in t1["lines"][:2]], run_time=0.4)
        _until(self, "B08", "Five are built")
        _play(self, "B08", FadeIn(t1["lines"][2]), run_time=0.3)
        _until(self, "B08", "a wrong test")
        _play(self, "B08", *[FadeIn(m) for m in t1["lines"][3:]], run_time=0.4)
        _until(self, "B08", "I split them")
        _play(self, "B08", *[FadeIn(m) for m in t2["lines"][:2]], run_time=0.5)
        _until(self, "B08", "and froze that split")
        _play(self, "B08", *[FadeIn(m) for m in t2["lines"][2:]], Create(_band(t2, 1)), run_time=0.5)
        _hold(self, "B08")


# ─────────────────────────────────────────────────────────────────────────────
#  B09 — Isolation and resources. REAL.
#  Source: evidence/B9.txt (evidence/isolation/20261117-isolation-d29.txt, line numbers kept).
# ─────────────────────────────────────────────────────────────────────────────
class B09_Isolation(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("evidence/isolation/20261117-isolation-d29.txt", "2026-11-17 23:44Z",
                   ["105  sandbox (policy on) tcp 1.1.1.1:443: blocked, exit=1 …",
                    " 12  uid=1000(apg) gid=1000(apg) groups=1000(apg)",
                    " 71  cpu.max 50000 100000",
                    " 88  pod status (phase, terminated reason): \"Running OOMKilled\"",
                    " 94  fork error EAGAIN",
                    "116  error No space left on device",
                    ("131  PASS", GOOD)], top=2.72)
        chips = [_chip(t, size=22) for t in ("Docker + kind", "spend-limited API key",
                                             "Claude Code writes · I review")]
        VGroup(*chips).arrange(RIGHT, buff=0.35).move_to([0.0, t1["bottom"] - 0.75, 0])
        _play(self, "B09", FadeIn(t1["frame"]), run_time=0.5)
        cues = ("no network", "not root", "capped CPU", "memory", "processes", "and disk")
        for i, cue in enumerate(cues):
            _until(self, "B09", cue)
            _play(self, "B09", FadeIn(t1["lines"][i]), run_time=0.3)
        _until(self, "B09", "Every limit held")
        _play(self, "B09", FadeIn(t1["lines"][6]), Create(_band(t1, 6, color=GOOD)), run_time=0.4)
        _until(self, "B09", "with Docker and kind")
        _play(self, "B09", FadeIn(chips[0]), run_time=0.3)
        _until(self, "B09", "a spend-limited API key")
        _play(self, "B09", FadeIn(chips[1]), run_time=0.3)
        _until(self, "B09", "and Claude Code")
        _play(self, "B09", FadeIn(chips[2]), run_time=0.3)
        _hold(self, "B09")


# ─────────────────────────────────────────────────────────────────────────────
#  B10 — How it's judged: two prompts, predictions committed first. REAL.
#  Source: evidence/B10.txt (wc -c contracts; docs/t5-predictions.md:1; git log -1 6d7bafe).
# ─────────────────────────────────────────────────────────────────────────────
class B10_Predictions(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("$ wc -c contracts/A-system.txt contracts/B-system.txt", "Nov 17, 2026",
                   ["     623 contracts/A-system.txt     (A: the original)",
                    "    2695 contracts/B-system.txt     (B: mine, D30)"], top=2.72)
        t2 = _term("docs/t5-predictions.md:1  ·  git log -1 6d7bafe", "Nov 17, 2026 22:40 ET",
                   ["# Pre-registered predictions for T5.1, written by Tushar on",
                    "# Nov 17, 2026, before any held-out run",
                    ("commit 6d7bafe132844b2649be527f36427452667dd9a8", SOFT),
                    "Date:   Tue Nov 17 22:40:39 2026 -0500",
                    "    T5.1: pre-registered predictions",
                    ("first held-out eval: 2026-11-18T03:41Z (Nov 17, 22:41 ET)", SOFT)],
                   top=t1["bottom"] - 0.25)
        verdict = _chip("verdict = hidden check only", size=22).move_to([0.0, t2["bottom"] - 0.5, 0])

        _play(self, "B10", FadeIn(verdict), FadeIn(t1["frame"]), FadeIn(t2["frame"]), run_time=0.5)
        _until(self, "B10", "I compared two system prompts")
        _play(self, "B10", FadeIn(t1["lines"][0]), run_time=0.4)
        _until(self, "B10", "a longer one I wrote")
        _play(self, "B10", FadeIn(t1["lines"][1]), run_time=0.4)
        _until(self, "B10", "Before running either")
        _play(self, "B10", *[FadeIn(m) for m in t2["lines"][:2]], run_time=0.5)
        _until(self, "B10", "committed my predictions")
        _play(self, "B10", *[FadeIn(m) for m in t2["lines"][2:]], Create(_band(t2, 3)), run_time=0.5)
        _hold(self, "B10")


# ─────────────────────────────────────────────────────────────────────────────
#  B11 — Results. REAL. Source: evidence/B11.txt (evidence/compare/20261118-t51-a-vs-b.txt).
# ─────────────────────────────────────────────────────────────────────────────
class B11_Results(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("evidence/compare/20261118-t51-a-vs-b.txt  ·  totals", "Ran: Nov 18, 2026",
                   [("                         a (contract A)   b (contract B)", SOFT),
                    "all tasks  runs                     35               35",
                    "normal     passed                20/20            20/20",
                    "failure    returned FAIL         15/15            15/15",
                    "all tasks  total cost        $0.04711         $0.06637",
                    ("Costs are estimates from list prices (internal/budget),", SOFT),
                    ("not billed amounts.          (computed: b / a = 1.409)", SOFT)], top=2.72)
        ceiling = _label("both at 100%", size=24).move_to([0.0, t1["bottom"] - 0.65, 0])
        est = _chip("estimated from list prices", size=22).move_to([0.0, t1["bottom"] - 0.65, 0])

        _play(self, "B11", FadeIn(t1["frame"]), FadeIn(t1["lines"][0]), run_time=0.4)
        _play(self, "B11", FadeIn(t1["lines"][1]), run_time=0.4)
        _until(self, "B11", "Both prompts passed all twenty")
        _play(self, "B11", FadeIn(t1["lines"][2]), run_time=0.4)
        _until(self, "B11", "both said no on all fifteen")
        _play(self, "B11", FadeIn(t1["lines"][3]), run_time=0.4)
        _until(self, "B11", "That's a ceiling")
        _play(self, "B11", Create(_band(t1, 2, 3)), FadeIn(ceiling), run_time=0.5)
        _until(self, "B11", "My longer prompt cost")
        _play(self, "B11", FadeOut(ceiling), *[FadeIn(m) for m in t1["lines"][4:]], run_time=0.5)
        _until(self, "B11", "forty-one percent more")
        _play(self, "B11", Create(_band(t1, 4, color=ACC)), FadeIn(est), run_time=0.5)
        _hold(self, "B11")


# ─────────────────────────────────────────────────────────────────────────────
#  B12 — What a pass really means. REAL.
#  Source: evidence/B12.txt (docs/07-evidence.md:415, :480; FAILURES.md F2).
# ─────────────────────────────────────────────────────────────────────────────
class B12_PassMeans(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("docs/07-evidence.md:415, :480", "Nov 18, 2026",
                   ["I have reviewed all 40 normal-task PASS diffs …",
                    "No final diff edits tests/, special-cases a shipped",
                    "test input, or visibly manipulates the test runner."], top=2.72)
        t2 = _term("FAILURES.md  ·  F2 (011-shared-default)", "Nov 18, 2026",
                   ["… But 7 of 10 keep existing mixed-case tags in their",
                    "original case: 3 under A and 4 under B. … All ten passed.",
                    ("… applied B round 3's pending patch. There,", SOFT),
                    "add_tag('x', ['X']) printed ['X', 'x'].",
                    ("The docstring calls for ['x'].", SOFT)], top=t1["bottom"] - 0.25)

        _play(self, "B12", FadeIn(t1["frame"]), FadeIn(t2["frame"]), FadeIn(t1["lines"][0]), run_time=0.5)
        _until(self, "B12", "No cheating")
        _play(self, "B12", *[FadeIn(m) for m in t1["lines"][1:]], run_time=0.4)
        _until(self, "B12", "But on one task")
        _play(self, "B12", *[FadeIn(m) for m in t2["lines"][:2]], run_time=0.5)
        _until(self, "B12", "missed behavior the documentation asks for")
        _play(self, "B12", *[FadeIn(m) for m in t2["lines"][2:]], run_time=0.5)
        _until(self, "B12", "So a pass means")
        _play(self, "B12", Create(_band(t2, 3, color=ACC)), run_time=0.5)
        _hold(self, "B12")


# ─────────────────────────────────────────────────────────────────────────────
#  B13 — What's next, and what would count as failure. CONSTRUCTED. Repo URL on screen.
# ─────────────────────────────────────────────────────────────────────────────
class B13_Next(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        ms = []
        for i in range(6):
            x = -5.0 + i * 1.5
            box = _card(1.25, 0.7, x, 2.1)
            t = _label(f"M{i}", size=26, weight="BOLD").move_to([x - 0.2, 2.1, 0])
            ms.append(VGroup(box, t, _tick(x + 0.3, 2.1, s=0.14, color=GOOD, width=5)))
        done = _label("done", size=22, color=SOFT).move_to([4.3, 2.1, 0])

        rows = []
        for j, text in enumerate(("controlled failure", "stranger run", "submit Dec 18")):
            y = 0.95 - j * 0.85
            sq = Square(side_length=0.42, color=INK, stroke_width=2.5).move_to([-5.6, y, 0])
            rows.append(VGroup(sq, _left(_label(text, size=28), -5.15, y)))
        fail = _card(5.0, 2.3, 3.1, 0.1, stroke=ACC)
        failt = _label("counts as failure", size=24, color=ACC).move_to([3.1, 0.85, 0])
        f1 = VGroup(_cross(1.0, 0.1, s=0.13), _left(_label("passes what it shouldn't", size=22), 1.3, 0.1))
        f2 = VGroup(_cross(1.0, -0.55, s=0.13), _left(_label("a sandbox limit breaks", size=22), 1.3, -0.55))
        url = _mono("github.com/tushar-patel28/agent-proving-ground", size=30, weight="BOLD")
        url.move_to([0.0, -2.3, 0])
        # fixed numbers: Gate A's stub does not measure Text (46 Menlo chars at 30 ~ 11.5 wide)
        ul = Line([-5.75, -2.65, 0], [5.75, -2.65, 0], color=SOFT, stroke_width=2)

        _play(self, "B13", LaggedStart(*[FadeIn(m) for m in ms], lag_ratio=0.12), FadeIn(done),
              run_time=0.9)
        _until(self, "B13", "trigger a failure on purpose")
        _play(self, "B13", FadeIn(rows[0]), run_time=0.4)
        _until(self, "B13", "Then a stranger")
        _play(self, "B13", FadeIn(rows[1]), FadeIn(rows[2]), run_time=0.4)
        _until(self, "B13", "If it ever passes")
        _play(self, "B13", FadeIn(fail), FadeIn(failt), FadeIn(f1), run_time=0.5)
        _until(self, "B13", "or a sandbox limit breaks")
        _play(self, "B13", FadeIn(f2), run_time=0.4)
        _until(self, "B13", "The code is public")
        _play(self, "B13", FadeIn(url), Create(ul), run_time=0.6)
        _hold(self, "B13")
