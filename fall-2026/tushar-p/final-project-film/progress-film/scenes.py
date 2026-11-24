"""scenes.py — Manim scenes for agent-proving-ground-progress (progress film v2, through M5).

Same chassis as the October pitch (youtube/brutalist/agent-proving-ground/scenes.py):
top rail, Text built at one reference size and scaled down, white cards, audio-
clocked _hold, sentence-timed cues, and the same NEUTRAL palette. No product,
brand or channel styling, no logos, no people, no mascots. Colour carries
meaning only: red marks a failure, a denial or a limit; green marks PASS (and,
in B08, the eleven tasks whose expected verdict is PASS).

v2 structure (Nov 23, 2026): explain the project first, keep "built so far"
short, end on what's left.

Two kinds of beat:
- CONSTRUCTED (every beat except B09 and B11): drawn diagrams and mock-ups; the
  rail carries a "Constructed" pill for the whole beat.
- REAL (B09, B11): terminal-style frames whose text is copied from the captures in
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
LINE = ManimColor("#A9B0B8")   # chip outlines: decorative, lighter than any text colour

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
                           color=LINE, fill_color=CARD, fill_opacity=1.0, stroke_width=2.0)
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



def _fade(mobs):
    return [FadeIn(m) for m in mobs]


# ═════════════════════════════════════════════════════════════════════════════
#  PART 1 — EXECUTIVE SUMMARY
# ═════════════════════════════════════════════════════════════════════════════

# B01 — Hello. Title card. CONSTRUCTED.
class B01_Hello(Scene):

    def construct(self):
        self.camera.background_color = BG
        rail = _rail("constructed")
        name = _label("Tushar Patel", size=52, weight="BOLD").move_to([0.0, 1.6, 0])
        who = _label("software engineering student · Northeastern", size=26, color=SOFT)
        who.move_to([0.0, 0.9, 0])
        rule = Line([-4.6, 0.35, 0], [4.6, 0.35, 0], color=SOFT, stroke_width=1.5)
        course = _label("INFO 7375 · final project", size=28, color=SOFT).move_to([0.0, -0.2, 0])
        title = _label("Agent Proving Ground", size=60, weight="BOLD").move_to([0.0, -1.05, 0])
        row = VGroup(*[_card(1.5, 0.6, x, -2.5) for x in (-3.6, -1.2, 1.2, 3.6)])
        words = VGroup(*[_label(w, size=24, color=SOFT).move_to([x, -2.5, 0])
                         for w, x in zip(("sandbox", "trace", "check", "verdict"),
                                         (-3.6, -1.2, 1.2, 3.6))])

        self.add(rail)
        _play(self, "B01", FadeIn(name), LaggedStart(*[FadeIn(c) for c in row], lag_ratio=0.15),
              FadeIn(words), run_time=0.6)
        _until(self, "B01", "a software engineering student")
        _play(self, "B01", FadeIn(who), Create(rule), run_time=0.5)
        _until(self, "B01", "This is my final project")
        _play(self, "B01", FadeIn(course), Write(title), run_time=0.9)
        _hold(self, "B01")


# B02 — The problem. Three panels, the same "Done!" in each. CONSTRUCTED.
class B02_Done(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        xs = (-4.15, 0.0, 4.15)
        panels = [_card(3.7, 4.9, x, -0.1) for x in xs]
        heads = [_label(t, size=28, weight="BOLD").move_to([x, 1.8, 0])
                 for t, x in zip(("fixed the bug", "edited the test", "gave up"), xs)]
        marks = [_tick(xs[0], 0.85, s=0.34, width=7),
                 _cross(xs[1], 0.85, s=0.28, width=7),
                 _cross(xs[2], 0.85, s=0.28, width=7)]
        bubbles = [_bubble(2.8, 1.1, x, -0.95) for x in xs]
        dones = [_label("Done!", size=34, weight="BOLD").move_to([x, -0.95, 0]) for x in xs]
        eqs = [_label("=", size=44, color=SOFT).move_to([x, -0.95, 0]) for x in (-2.075, 2.075)]
        claim = _chip("a claim ≠ a result", size=28).move_to([0.0, -3.05, 0])

        _play(self, "B02", LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.15), run_time=0.5)
        _play(self, "B02", *_fade(bubbles), *_fade(dones), run_time=0.5)
        _until(self, "B02", "is a claim, not a result")
        _play(self, "B02", FadeIn(claim), run_time=0.4)
        for i, cue in enumerate(("fix the bug", "quietly edit the test", "just give up")):
            _until(self, "B02", cue)
            _play(self, "B02", FadeIn(heads[i]), Create(marks[i]), run_time=0.4)
        _until(self, "B02", "its message can look the same")
        _play(self, "B02", *_fade(eqs), run_time=0.4)
        _hold(self, "B02")


# B03 — What it is: one command -> sandbox -> trace -> check -> PASS/FAIL. CONSTRUCTED.
class B03_WhatItIs(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        y = -0.2
        xs = (-4.65, -1.55, 1.55, 4.65)
        cmd = _chip("$ apg run <task>", size=24, mono=True).move_to([-4.15, 2.15, 0])
        repo = _chip("code in a public GitHub repo", size=26).move_to([3.0, 2.15, 0])
        down = Arrow([-4.65, 1.8, 0], [-4.65, 1.18, 0], buff=0, color=SOFT, stroke_width=3,
                     tip_length=0.16)
        boxes = [_card(2.6, 2.6, x, y) for x in xs]
        names = [_label(n, size=28, weight="BOLD").move_to([x, y + 0.85, 0])
                 for n, x in zip(("sandbox", "trace", "check", "verdict"), xs)]
        wall = DashedVMobject(Rectangle(width=1.7, height=0.9, color=INK, stroke_width=2.5),
                              num_dashes=24).move_to([xs[0], y - 0.45, 0])
        agent = Dot([xs[0] - 0.4, y - 0.45, 0], radius=0.12, color=INK)
        steps = VGroup(*[VGroup(Dot([xs[1] - 0.7, y + dy, 0], radius=0.06, color=INK),
                                Line([xs[1] - 0.45, y + dy, 0], [xs[1] + 0.75, y + dy, 0],
                                     color=INK, stroke_width=3))
                         for dy in (-0.15, -0.5, -0.85)])
        tests = _mono("its tests", size=22).move_to([xs[2] - 0.25, y - 0.45, 0])
        ok = _tick(xs[2] + 0.85, y - 0.45, s=0.18, width=6)
        pas = _label("PASS", size=30, weight="BOLD", color=GOOD).move_to([xs[3], y - 0.2, 0])
        fai = _label("FAIL", size=30, weight="BOLD", color=ACC).move_to([xs[3], y - 0.75, 0])
        arrows = [Arrow([x + 1.33, y, 0], [x + 1.77, y, 0], buff=0, color=SOFT,
                        stroke_width=3, tip_length=0.14) for x in xs[:3]]
        word = _bubble(3.2, 0.8, 1.55, -2.4)
        wtxt = _label("agent: \"done\"", size=24, color=SOFT).move_to([1.55, -2.4, 0])
        wx = _cross(3.6, -2.4, s=0.18)

        _until(self, "B03", "is a command-line tool")
        _play(self, "B03", FadeIn(cmd), run_time=0.4)
        _until(self, "B03", "a public GitHub repo")
        _play(self, "B03", FadeIn(repo), run_time=0.4)
        _until(self, "B03", "You give it a small coding task")
        _play(self, "B03", GrowArrow(down), FadeIn(boxes[0]), FadeIn(names[0]), FadeIn(agent),
              run_time=0.5)
        _until(self, "B03", "inside a locked sandbox")
        _play(self, "B03", Create(wall), agent.animate.shift(RIGHT * 0.4), run_time=0.6)
        _until(self, "B03", "records every step")
        _play(self, "B03", GrowArrow(arrows[0]), FadeIn(boxes[1]), FadeIn(names[1]),
              LaggedStart(*[Create(s) for s in steps], lag_ratio=0.3), run_time=0.8)
        _until(self, "B03", "decides pass or fail")
        _play(self, "B03", GrowArrow(arrows[1]), FadeIn(boxes[2]), FadeIn(names[2]), FadeIn(tests),
              Create(ok), run_time=0.6)
        _play(self, "B03", GrowArrow(arrows[2]), FadeIn(boxes[3]), FadeIn(names[3]),
              FadeIn(pas), FadeIn(fai), run_time=0.6)
        _until(self, "B03", "Never by taking")
        _play(self, "B03", FadeIn(word), FadeIn(wtxt), Create(wx), run_time=0.5)
        _hold(self, "B03")


# B04 — Who opens it, first minute. A terminal MOCK-UP (constructed, not captured).
class B04_FirstMinute(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        who = _chip("engineers deciding: trust this agent, or this change?", size=26)
        who.move_to([-1.35, 2.35, 0])
        clock = _chip("first minute", size=26).move_to([4.6, 2.35, 0])
        t = _term("mock-up of the terminal (not captured output)", "constructed",
                  [("$ apg run 001", INK),
                   ("001  PASS  steps=3  reason=check_passed", INK),
                   ("$ apg show <trace>", INK),
                   "step 1  run_command  …",
                   "step 2  run_command  …",
                   "step 3  end_turn"], top=1.85)

        _play(self, "B04", FadeIn(t["frame"]), run_time=0.5)
        _until(self, "B04", "It's for engineers")
        _play(self, "B04", FadeIn(who), run_time=0.4)
        _until(self, "B04", "In their first minute")
        _play(self, "B04", FadeIn(clock), run_time=0.4)
        _until(self, "B04", "they run one command")
        _play(self, "B04", FadeIn(t["lines"][0]), run_time=0.3)
        _until(self, "B04", "read one result line")
        _play(self, "B04", FadeIn(t["lines"][1]), Create(_band(t, 1)), run_time=0.4)
        _until(self, "B04", "and open the trace")
        _play(self, "B04", LaggedStart(*[FadeIn(m) for m in t["lines"][2:]], lag_ratio=0.25),
              run_time=1.0)
        _hold(self, "B04")


# ═════════════════════════════════════════════════════════════════════════════
#  PART 2 — INTRODUCTION
# ═════════════════════════════════════════════════════════════════════════════

# B05 — Others: E2B and Langfuse, each with what it solves and what it doesn't. CONSTRUCTED.
class B05_Others(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        xs = (-3.0, 3.0)
        cards = [_card(5.4, 4.9, x, -0.15) for x in xs]
        names = [_label(n, size=36, weight="BOLD").move_to([x, 1.8, 0])
                 for n, x in zip(("E2B", "Langfuse"), xs)]
        wall = VGroup(DashedVMobject(Rectangle(width=1.6, height=0.85, color=INK, stroke_width=2.5),
                                     num_dashes=22),
                      Dot(radius=0.1, color=INK)).move_to([xs[0], 0.9, 0])
        trace = VGroup(*[VGroup(Dot([xs[1] - 0.75, 1.2 - k * 0.3, 0], radius=0.06, color=INK),
                                Line([xs[1] - 0.5, 1.2 - k * 0.3, 0],
                                     [xs[1] + 0.85, 1.2 - k * 0.3, 0], color=INK, stroke_width=3))
                         for k in range(3)])
        solves = [("sandboxes for AI-generated code", xs[0]), ("LLM traces and scores", xs[1])]
        nots = [("whether the work is right", xs[0]), ("an agent doing what it shouldn't", xs[1])]
        s_head = [_label("solves", size=24, color=SOFT).move_to([x, 0.05, 0]) for x in xs]
        s_text = [_label(t, size=26).move_to([x, -0.4, 0]) for t, x in solves]
        n_head = [_label(h, size=24, color=ACC).move_to([x, -1.2, 0])
                  for h, x in (("doesn't tell you", xs[0]), ("doesn't stop", xs[1]))]
        n_text = [_label(t, size=26).move_to([x, -1.65, 0]) for t, x in nots]

        _until(self, "B05", "Parts of this already exist")
        _play(self, "B05", LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.2), run_time=0.6)
        _until(self, "B05", "E2B provides")
        _play(self, "B05", FadeIn(names[0]), Create(wall), run_time=0.5)
        _until(self, "B05", "Langfuse records")
        _play(self, "B05", FadeIn(names[1]), Create(trace), run_time=0.5)
        _until(self, "B05", "Each solves one piece well")
        _play(self, "B05", *_fade(s_head), *_fade(s_text), run_time=0.5)
        _until(self, "B05", "But a sandbox doesn't tell you")
        _play(self, "B05", FadeIn(n_head[0]), FadeIn(n_text[0]), run_time=0.4)
        _until(self, "B05", "and a trace doesn't stop")
        _play(self, "B05", FadeIn(n_head[1]), FadeIn(n_text[1]), run_time=0.4)
        _hold(self, "B05")


# B06 — Why mine: the four pieces in one loop on a laptop; why; what I learned. CONSTRUCTED.
class B06_WhyMine(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        screen = RoundedRectangle(corner_radius=0.12, width=7.2, height=4.3, color=INK,
                                  stroke_width=3).move_to([-2.4, 0.45, 0])
        base = Polygon([-6.2, -1.95, 0], [1.4, -1.95, 0], [1.05, -1.65, 0], [-5.85, -1.65, 0],
                       color=INK, stroke_width=3)
        pos = {"sandbox": (-4.3, 1.45), "trace": (-0.5, 1.45),
               "check": (-0.5, -0.55), "human approval": (-4.3, -0.55)}
        nodes = {k: _chip(k, size=26).move_to([x, y, 0]) for k, (x, y) in pos.items()}
        tip = dict(buff=0, color=SOFT, stroke_width=3, tip_length=0.18)
        arrows = [Arrow([-3.3, 1.45, 0], [-1.45, 1.45, 0], **tip),
                  Arrow([-0.5, 1.0, 0], [-0.5, -0.1, 0], **tip),
                  Arrow([-1.45, -0.55, 0], [-2.7, -0.55, 0], **tip),
                  Arrow([-4.3, -0.1, 0], [-4.3, 1.0, 0], **tip)]
        why = _card(3.5, 2.3, 4.25, 1.15)
        why1 = _label("more code by agents", size=24, color=SOFT).move_to([4.25, 1.75, 0])
        why2 = _label("check it,", size=30, weight="BOLD").move_to([4.25, 1.1, 0])
        why3 = _label("don't trust it", size=30, weight="BOLD").move_to([4.25, 0.55, 0])
        new = _label("new to me", size=26, color=SOFT).move_to([4.25, -0.65, 0])
        langs = VGroup(_chip("Go", size=26), _chip("Kubernetes", size=26))
        langs.arrange(RIGHT, buff=0.3).move_to([4.25, -1.3, 0])

        _play(self, "B06", Create(screen), Create(base), run_time=0.6)
        _until(self, "B06", "sandbox, trace")
        _play(self, "B06", FadeIn(nodes["sandbox"]), run_time=0.3)
        _play(self, "B06", GrowArrow(arrows[0]), FadeIn(nodes["trace"]), run_time=0.35)
        _until(self, "B06", "an independent check")
        _play(self, "B06", GrowArrow(arrows[1]), FadeIn(nodes["check"]), run_time=0.4)
        _until(self, "B06", "and a human approval")
        _play(self, "B06", GrowArrow(arrows[2]), FadeIn(nodes["human approval"]), run_time=0.4)
        _play(self, "B06", GrowArrow(arrows[3]), run_time=0.3)
        _until(self, "B06", "I built it because")
        _play(self, "B06", FadeIn(why), FadeIn(why1), run_time=0.4)
        _until(self, "B06", "someone has to check it")
        _play(self, "B06", FadeIn(why2), FadeIn(why3), run_time=0.4)
        _until(self, "B06", "Along the way")
        _play(self, "B06", FadeIn(new), run_time=0.3)
        _until(self, "B06", "Go and Kubernetes")
        _play(self, "B06", LaggedStart(*[FadeIn(c) for c in langs], lag_ratio=0.4), run_time=0.6)
        _hold(self, "B06")


# ═════════════════════════════════════════════════════════════════════════════
#  PART 3 — METHODS
# ═════════════════════════════════════════════════════════════════════════════

# B07 — One run, built step by step: pod -> agent + 3 tools -> policy -> hidden check -> trace
#        -> human gate. CONSTRUCTED.
class B07_OneRun(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        pod = DashedVMobject(RoundedRectangle(corner_radius=0.2, width=7.0, height=4.05,
                                              color=INK, stroke_width=3), num_dashes=64)
        pod.move_to([-2.5, 0.425, 0])
        podl = _left(_label("Kubernetes pod", size=24, weight="BOLD"), -5.7, 2.05)
        podc = _chip("no network · not root", size=24).move_to([-0.95, 2.05, 0])
        agent = _label("agent: Claude Haiku", size=26).move_to([-2.5, 1.2, 0])
        tools = VGroup(*[_chip(t, size=18, mono=True) for t in ("read_file", "write_file",
                                                                "run_command")])
        tools.arrange(RIGHT, buff=0.2).move_to([-2.5, 0.35, 0])
        policy = Rectangle(width=6.6, height=0.66, color=ACC, stroke_width=2.5).move_to([-2.5, -0.6, 0])
        policyl = _label("permission policy, in code: every call first", size=26).move_to([-2.5, -0.6, 0])
        tip = dict(buff=0, color=SOFT, stroke_width=3, tip_length=0.16)
        a_check = Arrow([1.1, 1.45, 0], [2.15, 1.45, 0], **tip)
        check = _card(3.6, 1.9, 4.05, 1.45)
        checkl = _label("hidden check", size=26, weight="BOLD").move_to([4.05, 1.95, 0])
        pf = VGroup(_label("PASS", size=26, weight="BOLD", color=GOOD),
                    _label("/", size=26, color=SOFT),
                    _label("FAIL", size=26, weight="BOLD", color=ACC)).arrange(RIGHT, buff=0.2)
        pf.move_to([4.05, 1.05, 0])
        a_trace = Arrow([1.1, -0.65, 0], [2.15, -0.65, 0], **tip)
        trace = _card(3.6, 1.7, 4.05, -0.65)
        tracel = _label("trace", size=26, weight="BOLD").move_to([4.05, -0.1, 0])
        tlines = VGroup(*[VGroup(Dot([3.0, -0.6 - k * 0.3, 0], radius=0.05, color=INK),
                                 Line([3.2, -0.6 - k * 0.3, 0], [5.1, -0.6 - k * 0.3, 0],
                                      color=INK, stroke_width=2.5)) for k in range(3)])
        gate = _card(11.9, 0.95, 0.0, -2.35)
        gatel = _left(_label("human gate", size=24, weight="BOLD"), -5.6, -2.35)
        gatem = _left(_label("I see the diff · I approve", size=26), -3.75, -2.35)
        gates = _left(_mono("diff_sha256 = recheck_sha256", size=20), 0.75, -2.35)

        _play(self, "B07", Create(pod), run_time=0.6)
        _until(self, "B07", "The harness starts a Kubernetes pod")
        _play(self, "B07", FadeIn(podl), run_time=0.3)
        _until(self, "B07", "with no network")
        _play(self, "B07", FadeIn(podc), run_time=0.3)
        _until(self, "B07", "The agent, Claude Haiku")
        _play(self, "B07", FadeIn(agent), run_time=0.3)
        _until(self, "B07", "read a file")
        _play(self, "B07", LaggedStart(*[FadeIn(t) for t in tools], lag_ratio=0.5), run_time=1.0)
        _until(self, "B07", "Every tool call passes")
        _play(self, "B07", Create(policy), FadeIn(policyl), run_time=0.5)
        _until(self, "B07", "After every change")
        _play(self, "B07", GrowArrow(a_check), FadeIn(check), FadeIn(checkl), run_time=0.5)
        _until(self, "B07", "Pass or fail comes only")
        _play(self, "B07", FadeIn(pf), run_time=0.4)
        _play(self, "B07", GrowArrow(a_trace), FadeIn(trace), FadeIn(tracel), Create(tlines),
              run_time=0.5)
        _until(self, "B07", "Then I see the diff")
        _play(self, "B07", FadeIn(gate), FadeIn(gatel), FadeIn(gatem), run_time=0.5)
        _until(self, "B07", "my approval is bound")
        _play(self, "B07", FadeIn(gates), run_time=0.4)
        _hold(self, "B07")


# B08 — The tasks: 16 tiles (11 expected PASS, 5 expected no), the frozen dev/held-out
#        split, and what it runs on. CONSTRUCTED. Split membership from evidence/B8.txt.
_DEV = (0, 1, 2, 3, 4, 8, 9, 12, 13)          # 001-005, 009, 010, 013, 014
_HELD = (5, 6, 7, 10, 11, 14, 15)             # 006-008, 011, 012, 015, 016


class B08_Tasks(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        tiles = []
        for i in range(16):
            x = -5.4 + 0.72 * i
            sq = Square(side_length=0.58, color=SOFT, stroke_width=2, fill_color=CARD,
                        fill_opacity=1.0).move_to([x, 1.75, 0])
            tile = VGroup(sq, _mono(f"{i + 1:03d}", size=15).move_to([x, 1.75, 0]))
            tiles.append(tile.set_z_index(2))      # above the dev / held-out cards they move into
        l_norm = _label("11 ordinary bugs", size=26).move_to([-1.8, 2.45, 0])
        l_no = _label("5: the right answer is no", size=26, color=ACC).move_to([3.96, 2.45, 0])
        dev = _card(5.6, 2.5, -3.0, -0.85)
        held = _card(5.6, 2.5, 3.0, -0.85)
        devl = _label("dev", size=24, weight="BOLD").move_to([-3.0, 0.05, 0])
        heldl = _label("held-out", size=24, weight="BOLD").move_to([3.0, 0.05, 0])
        body = Rectangle(width=0.42, height=0.34, color=INK, stroke_width=2.5, fill_color=CARD,
                         fill_opacity=1.0).move_to([0.0, 0.75, 0])
        shackle = Arc(radius=0.14, start_angle=0, angle=PI, color=INK, stroke_width=2.5)
        shackle.move_to([0.0, 0.99, 0])
        lock = VGroup(shackle, body)
        frozen = _left(_label("split frozen before tuning", size=26, color=SOFT), 0.35, 0.8)

        def slot(k, total, row1, cx):
            """Grid slot k of `total` tiles: `row1` on the first row, the rest below."""
            row, col = (0, k) if k < row1 else (1, k - row1)
            n = row1 if row == 0 else total - row1
            return [cx + 0.85 * (col - (n - 1) / 2), -0.6 - 0.8 * row, 0]

        targets = {i: slot(k, len(_DEV), 5, -3.0) for k, i in enumerate(_DEV)}
        targets.update({i: slot(k, len(_HELD), 4, 3.0) for k, i in enumerate(_HELD)})
        chips = VGroup(*[_chip(t, size=24) for t in ("Docker + kind", "spend-limited API key",
                                                     "Claude Code writes · I review")])
        chips.arrange(RIGHT, buff=0.25).move_to([0.0, -2.75, 0])

        _play(self, "B08", LaggedStart(*[FadeIn(t) for t in tiles], lag_ratio=0.05),
              FadeIn(dev), FadeIn(held), FadeIn(devl), FadeIn(heldl), run_time=0.9)
        _until(self, "B08", "Eleven are ordinary bugs")
        _play(self, "B08", *[tiles[i][0].animate.set_stroke(GOOD, width=3).set_fill(GOOD, 0.15)
                             for i in range(11)], FadeIn(l_norm), run_time=0.5)
        _until(self, "B08", "Five are designed")
        _play(self, "B08", *[tiles[i][0].animate.set_stroke(ACC, width=3).set_fill(ACC, 0.12)
                             for i in range(11, 16)], FadeIn(l_no), run_time=0.5)
        _until(self, "B08", "I froze a development")
        _play(self, "B08", *[tiles[i].animate.move_to(targets[i]) for i in range(16)], run_time=1.0)
        _play(self, "B08", FadeIn(lock), FadeIn(frozen), run_time=0.4)
        _until(self, "B08", "with Docker and kind")
        _play(self, "B08", FadeIn(chips[0]), run_time=0.3)
        _until(self, "B08", "a spend-limited API key")
        _play(self, "B08", FadeIn(chips[1]), run_time=0.3)
        _until(self, "B08", "and Claude Code")
        _play(self, "B08", FadeIn(chips[2]), run_time=0.3)
        _hold(self, "B08")


# B09 — Built so far. REAL: three quick dated frames from the captures.
#   Frame 1: evidence/B6.txt (PLAN.md:120; trace 20261112T053055Z-92239eb0).
#   Frame 2: evidence/B7.txt (apg show step 4 of 20261118T034327Z-b54f5cd6).
#   Frame 3: evidence/B9.txt (evidence/isolation/20261117-isolation-d29.txt, line numbers kept).
#   Strip: evidence/B13.txt (PLAN.md milestone table M0-M5).
class B09_BuiltSoFar(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        f1 = _term("PLAN.md:120  ·  evidence/traces/20261112T053055Z-92239eb0.json",
                   "2026-11-12 05:30Z",
                   [("$ apg run 001                (result line recorded in PLAN.md)", SOFT),
                    ("001  PASS  steps=3  reason=check_passed", INK),
                    ("steps in the trace:", SOFT),
                    "1 run_command   2 run_command   3 end_turn"], top=2.72)
        f2 = _term("traces/20261118T034327Z-b54f5cd6.json", "2026-11-18 03:43Z · Nov 17 ET",
                   [("apg show, step 4 · task 008-config-parser · contract B · held-out", SOFT),
                    "  asked:   write_file /tmp/unused.txt (1 line, 11 bytes)",
                    ("  policy:  DENIED (rule: path): path /tmp/unused.txt is", ACC),
                    ("           outside /workspace", ACC),
                    "  /workspace changed: no"], top=2.72)
        f3 = _term("evidence/isolation/20261117-isolation-d29.txt", "2026-11-17 23:44Z",
                   ["105  sandbox (policy on) tcp 1.1.1.1:443: blocked, exit=1 …",
                    " 12  uid=1000(apg) gid=1000(apg) groups=1000(apg)",
                    " 71  cpu.max 50000 100000",
                    " 88  pod status (phase, terminated reason): \"Running OOMKilled\"",
                    " 94  fork error EAGAIN",
                    "116  error No space left on device",
                    ("131  PASS", GOOD)], top=2.72)
        ms = VGroup(*[VGroup(_card(0.7, 0.45, 0.9 + 0.8 * i, -3.0),
                             _label(f"M{i}", size=18, weight="BOLD").move_to([0.9 + 0.8 * i, -3.0, 0]))
                      for i in range(6)])
        msl = _label("PLAN.md: done through", size=28, color=SOFT)
        msl.move_to([0.0, -3.0, 0]).align_to([0.35, 0, 0], RIGHT)
        mst = _tick(5.55, -3.0, s=0.16, width=5)

        _until(self, "B09", "through milestone five")
        _play(self, "B09", FadeIn(msl), LaggedStart(*[FadeIn(m) for m in ms], lag_ratio=0.12),
              Create(mst), run_time=0.8)
        _until(self, "B09", "A real run on task one")
        _play(self, "B09", FadeIn(f1["frame"]), *_fade(f1["lines"][:2]), run_time=0.4)
        b1a, b1b, b2 = _band(f1, 1, color=GOOD), _band(f1, 3), _band(f2, 2, 3, color=ACC)
        _until(self, "B09", "passed in three steps")
        _play(self, "B09", Create(b1a), run_time=0.4)
        _until(self, "B09", "with every step in the trace")
        _play(self, "B09", *_fade(f1["lines"][2:]), Create(b1b), run_time=0.4)
        _until(self, "B09", "A denied tool call")
        _play(self, "B09", FadeOut(VGroup(f1["frame"], *f1["lines"], b1a, b1b)), run_time=0.3)
        _play(self, "B09", FadeIn(f2["frame"]), *_fade(f2["lines"][:2]), run_time=0.4)
        _until(self, "B09", "was recorded and never ran")
        _play(self, "B09", *_fade(f2["lines"][2:]), Create(b2), run_time=0.4)
        _until(self, "B09", "And when I tried to break")
        _play(self, "B09", FadeOut(VGroup(f2["frame"], *f2["lines"], b2)), run_time=0.3)
        _play(self, "B09", FadeIn(f3["frame"]), LaggedStart(*_fade(f3["lines"][:6]), lag_ratio=0.3),
              run_time=1.4)
        _until(self, "B09", "every limit held")
        _play(self, "B09", FadeIn(f3["lines"][6]), Create(_band(f3, 6, color=GOOD)), run_time=0.4)
        _hold(self, "B09")


# ═════════════════════════════════════════════════════════════════════════════
#  PART 4 — EVALUATION
# ═════════════════════════════════════════════════════════════════════════════

# B10 — How it's judged: three checks. CONSTRUCTED.
class B10_Judged(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        xs = (-4.15, 0.0, 4.15)
        cards = [_card(3.8, 4.7, x, -0.15) for x in xs]
        nums = [_label(str(i + 1), size=40, weight="BOLD", color=SOFT).move_to([x, 1.65, 0])
                for i, x in enumerate(xs)]
        h = [_label(t, size=28, weight="BOLD").move_to([x, 0.8, 0])
             for t, x in zip(("normal tasks", "the five no-tasks", "compare changes"), xs)]
        r1 = _label("→ PASS", size=34, weight="BOLD", color=GOOD).move_to([xs[0], -0.2, 0])
        r2 = _label("→ must FAIL", size=34, weight="BOLD", color=ACC).move_to([xs[1], -0.2, 0])
        r2b = _label("a PASS here = it failed", size=24, color=SOFT).move_to([xs[1], -1.25, 0])
        r3 = [_label(t, size=26).move_to([xs[2], y, 0]) for t, y in
              (("prompt A vs prompt B", -0.1), ("on held-out tasks", -0.75),
               ("predictions first", -1.4))]
        m1 = _tick(xs[0], -1.3, s=0.3, color=GOOD, width=7)
        m2 = _cross(xs[1], -1.95, s=0.22, width=6)
        m3 = Line([xs[2] - 1.1, -1.75, 0], [xs[2] + 1.1, -1.75, 0], color=INK, stroke_width=3)

        _until(self, "B10", "It's judged on three things")
        _play(self, "B10", LaggedStart(*[FadeIn(VGroup(c, n)) for c, n in zip(cards, nums)],
                                       lag_ratio=0.2), run_time=0.7)
        _until(self, "B10", "On normal tasks")
        _play(self, "B10", FadeIn(h[0]), FadeIn(r1), Create(m1), run_time=0.4)
        _until(self, "B10", "On the five no-tasks")
        _play(self, "B10", FadeIn(h[1]), FadeIn(r2), run_time=0.4)
        _until(self, "B10", "A pass on one of those")
        _play(self, "B10", FadeIn(r2b), Create(m2), run_time=0.4)
        _until(self, "B10", "Third, I compare changes")
        _play(self, "B10", FadeIn(h[2]), FadeIn(r3[0]), run_time=0.4)
        _until(self, "B10", "on held-out tasks")
        _play(self, "B10", FadeIn(r3[1]), run_time=0.3)
        _until(self, "B10", "and I wrote my predictions down")
        _play(self, "B10", FadeIn(r3[2]), Create(m3), run_time=0.3)
        _hold(self, "B10")


# B11 — First results. REAL. No costs.
#   Frame 1: evidence/B11.txt (evidence/compare/20261118-t51-a-vs-b.txt totals).
#   Frame 2: evidence/B12.txt (docs/07-evidence.md:415; FAILURES.md F2).
class B11_Results(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("real"))

        t1 = _term("evidence/compare/20261118-t51-a-vs-b.txt  ·  totals", "Ran: Nov 18, 2026",
                   [("                         a (contract A)   b (contract B)", SOFT),
                    "all tasks  runs                     35               35",
                    "normal     passed                20/20            20/20",
                    "failure    returned FAIL         15/15            15/15"], top=2.72)
        t2 = _term("docs/07-evidence.md:415  ·  FAILURES.md F2 (011-shared-default)",
                   "Nov 18, 2026",
                   ["I have reviewed all 40 normal-task PASS diffs …",
                    ("FAILURES.md F2:", SOFT),
                    "… But 7 of 10 keep existing mixed-case tags in their",
                    "original case: 3 under A and 4 under B. … All ten passed.",
                    "add_tag('x', ['X']) printed ['X', 'x'].",
                    ("The docstring calls for ['x'].", SOFT)], top=t1["bottom"] - 0.25)

        _until(self, "B11", "First results")
        _play(self, "B11", FadeIn(t1["frame"]), *_fade(t1["lines"][:2]), run_time=0.5)
        _until(self, "B11", "Both prompts passed all twenty")
        _play(self, "B11", FadeIn(t1["lines"][2]), run_time=0.4)
        _until(self, "B11", "said no on all fifteen")
        _play(self, "B11", FadeIn(t1["lines"][3]), Create(_band(t1, 2, 3)), run_time=0.4)
        _until(self, "B11", "Then I read all forty")
        _play(self, "B11", FadeIn(t2["frame"]), FadeIn(t2["lines"][0]), run_time=0.5)
        _until(self, "B11", "On one task, seven of ten")
        _play(self, "B11", *_fade(t2["lines"][1:4]), run_time=0.5)
        _until(self, "B11", "So a pass means")
        _play(self, "B11", *_fade(t2["lines"][4:]), Create(_band(t2, 4, color=ACC)), run_time=0.5)
        _hold(self, "B11")


# ═════════════════════════════════════════════════════════════════════════════
#  CLOSE
# ═════════════════════════════════════════════════════════════════════════════

# B12 — What's left: three numbered cards. CONSTRUCTED.
class B12_Left(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        items = (("Controlled failure", "edit the test → check catches it → recover"),
                 ("Stranger run", "README only, clean machine"),
                 ("Harden the check", "confirm every test actually ran: a forced exit can't fake a pass"))
        ys = (1.75, 0.0, -1.75)
        cards = [_card(11.8, 1.5, 0.0, y) for y in ys]
        nums = [_label(str(i + 1), size=48, weight="BOLD", color=SOFT).move_to([-5.15, y, 0])
                for i, y in enumerate(ys)]
        titles = [_left(_label(t, size=32, weight="BOLD"), -4.4, y + 0.27)
                  for (t, _), y in zip(items, ys)]
        # cards 1-2 keep size 30; card 3's line is longer, so 26 (still above Gate T's floor)
        lines = [_left(_label(d, size=30 if i < 2 else 26, color=SOFT), -4.4, y - 0.33)
                 for i, ((_, d), y) in enumerate(zip(items, ys))]
        footer = _label("All by Dec 18", size=28, color=SOFT).move_to([0.0, -3.0, 0])
        boxes = [Square(side_length=0.5, color=INK, stroke_width=2.5).move_to([5.35, y, 0]) for y in ys]

        _until(self, "B12", "Three things are left")
        _play(self, "B12", LaggedStart(*[FadeIn(VGroup(c, n)) for c, n in zip(cards, nums)],
                                       lag_ratio=0.2), run_time=0.7)
        for i, cue in enumerate(("First, a controlled failure", "Second, a stranger",
                                 "Third, I'll harden the check")):
            _until(self, "B12", cue)
            _play(self, "B12", FadeIn(titles[i]), FadeIn(lines[i]), Create(boxes[i]), run_time=0.4)
        _play(self, "B12", FadeIn(footer), run_time=0.4)
        _hold(self, "B12")


# B13 — Risk, scope, thanks, repo URL. CONSTRUCTED.
class B13_Close(Scene):

    def construct(self):
        self.camera.background_color = BG
        self.add(_rail("constructed"))

        risk = _card(11.8, 3.4, 0.0, 0.8, stroke=ACC)
        riskh = _label("Risk", size=26, weight="BOLD", color=ACC).move_to([0.0, 2.1, 0])
        riskt = _label("a pass that isn't real", size=40, weight="BOLD").move_to([0.0, 1.45, 0])
        risks = _label("code under test can fool a check", size=26, color=SOFT).move_to([0.0, 0.85, 0])
        arrow = Arrow([0.0, 0.55, 0], [0.0, 0.05, 0], buff=0, color=SOFT, stroke_width=3,
                      tip_length=0.15)
        fixes = VGroup(_chip("diff review", size=28), _chip("documented gaps", size=28))
        fixes.arrange(RIGHT, buff=0.5).move_to([0.0, -0.35, 0])
        scope = _left(_label("not a hosted service · not a model benchmark", size=26, color=SOFT),
                      -5.6, -1.5)
        honest = _left(_label("one honest tool", size=28, weight="BOLD"), 1.85, -1.5)
        url = _mono("github.com/tushar-patel28/agent-proving-ground", size=30, weight="BOLD")
        url.move_to([0.0, -2.3, 0])
        thanks = _label("Thanks for watching.", size=30).move_to([0.0, -2.95, 0])

        _play(self, "B13", FadeIn(risk), FadeIn(riskh), FadeIn(riskt), run_time=0.5)
        _until(self, "B13", "since code under test")
        _play(self, "B13", FadeIn(risks), run_time=0.4)
        _until(self, "B13", "That's why I review diffs")
        _play(self, "B13", GrowArrow(arrow), FadeIn(fixes[0]), run_time=0.4)
        _until(self, "B13", "write down every known gap")
        _play(self, "B13", FadeIn(fixes[1]), run_time=0.4)
        _until(self, "B13", "It won't be")
        _play(self, "B13", FadeIn(scope), run_time=0.4)
        _until(self, "B13", "It's one honest tool")
        _play(self, "B13", FadeIn(honest), run_time=0.4)
        _until(self, "B13", "Thanks for watching")
        _play(self, "B13", FadeIn(thanks), run_time=0.4)
        _until(self, "B13", "The code is at")
        _play(self, "B13", FadeIn(url), run_time=0.5)
        _hold(self, "B13")
