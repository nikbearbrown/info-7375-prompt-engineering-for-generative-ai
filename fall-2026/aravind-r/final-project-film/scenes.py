"""scenes.py — Readback pitch film, v2 visuals (narration and durations identical to v1).

The show-tell ISO KIT (brutalist.art @ cd4bf20) is pasted below unchanged. The v2 design system follows it:
colour roles, a progress rail, the recurring rubric page, and cue timing read from mp3/words.json.
See gates/v2-visual-plan.md.
"""
from manim import *
import numpy as np
import json as _json, os as _os

# ═════════════════════════════ ISO KIT (show-tell) ═════════════════════════════
STAGE = "#F2F0E9"; INK = "#3D3929"; TERRA = "#D97757"; DIM = "#8B8F96"; GHOST = "#D9D4C7"; CARD = "#FAF9F5"
BOX_TOP, BOX_L, BOX_R = "#F3E9D8", "#DCC9AA", "#C7AE86"          # kraft cardboard: top, left face, right face (deep enough for Gate V contrast)
BOX_IN1, BOX_IN2, BOX_FLOOR = "#CDB894", "#BFA67E", "#B39A72"     # inside walls + floor
DARK_TOP, DARK_L, DARK_R = "#3A3530", "#26221F", "#1E1B18"        # MCP / server blocks
PAGE_TOP, PAGE_L, PAGE_R = "#FFFFFF", "#ECE7DF", "#E2DCD2"         # skill pages
BAR1, BAR2, BAR3 = "#8B8F96", "#B4AFA6", "#D9D4C7"                # chart segments, dim to ghost
SERIF = "EB Garamond"
C30 = 0.8660254
config.background_color = STAGE


def T(s, size=36, color=INK, bold=False):
    return Text(s, font=SERIF, color=color, font_size=size, weight="BOLD" if bold else "NORMAL")


class Iso:
    """Isometric projection: x runs right-up, y runs left-up, z runs up. (ox, oy) is where (0,0,0) lands."""
    def __init__(self, ox=0.0, oy=0.0, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z=0.0):
        return np.array([self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * 0.5 * self.s + z * self.s, 0.0])

    def v(self, dx, dy, dz=0.0):
        return self.p(dx, dy, dz) - self.p(0, 0, 0)

    def quad(self, pts, fill, stroke=INK, sw=4):
        return Polygon(*[self.p(*q) for q in pts], fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=sw)

    def box(self, x0, y0, z0, w, d, h, top=BOX_TOP, left=BOX_L, right=BOX_R, sw=4):
        """Closed box: the two front faces (x = x0 and y = y0) plus the top."""
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        return VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], left, sw=sw),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], right, sw=sw),
            self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, sw=sw))

    def open_box(self, x0, y0, z0, w, d, h):
        """(back, front): floor + inner back walls, then the front walls. Put contents between them."""
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        back = VGroup(
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], BOX_FLOOR),
            self.quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], BOX_IN1),
            self.quad([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], BOX_IN2))
        front = VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], BOX_L),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], BOX_R))
        back.set_z_index(0); front.set_z_index(2)
        return back, front

    def tape(self, x0, y0, z1, w, d, drop=0.35, t=0.22):
        """Terracotta tape across the top (along x) and down the left front face."""
        ym = y0 + d / 2
        return VGroup(
            self.quad([(x0, ym - t, z1), (x0 + w, ym - t, z1), (x0 + w, ym + t, z1), (x0, ym + t, z1)], TERRA, sw=0),
            self.quad([(x0, ym - t, z1), (x0, ym + t, z1), (x0, ym + t, z1 - drop), (x0, ym - t, z1 - drop)], TERRA, sw=0))

    def mcp(self, x0, y0, z0, w=1.3, d=1.3, h=0.7):
        """Dark MCP block with two light ports on its right front face."""
        body = self.box(x0, y0, z0, w, d, h, DARK_TOP, DARK_L, DARK_R)
        ports = VGroup(*[self.box(x0 + w * f, y0 - 0.18, z0 + h * 0.3, w * 0.16, 0.18, h * 0.3, GHOST, BOX_IN1, BOX_IN2, sw=1)
                         for f in (0.22, 0.58)])
        return VGroup(body, ports)

    def page(self, x0, y0, z0, w=1.1, d=1.4):
        """A skill page lying flat: white slab, three ghost text lines, one terracotta dot."""
        slab = self.box(x0, y0, z0, w, d, 0.06, PAGE_TOP, PAGE_L, PAGE_R, sw=1.5)
        zt = z0 + 0.06
        lines = VGroup(*[Line(self.p(x0 + 0.2, y0 + d * f, zt), self.p(x0 + w - 0.2, y0 + d * f, zt), color=GHOST, stroke_width=4)
                         for f in (0.3, 0.5, 0.7)])
        dot = Dot(self.p(x0 + 0.2, y0 + d * 0.86, zt), radius=0.06, color=TERRA)
        return VGroup(slab, lines, dot)

    def server(self, x0, y0, z0, w=1.4, d=1.4, slab=0.42, n=3):
        """A stack of dark server slabs; returns (stack, lights) — lights start ghost, turn terracotta."""
        stack = VGroup(*[self.box(x0, y0, z0 + i * (slab + 0.04), w, d, slab, DARK_TOP, DARK_L, DARK_R) for i in range(n)])
        lights = VGroup(*[Dot(self.p(x0 + 0.25, y0, z0 + i * (slab + 0.04) + slab / 2), radius=0.06, color=GHOST) for i in range(n)])
        return stack, lights


def ease_in(t):
    """Quadratic ease-in (things dropping into a box). Local: Gate A's stub has no ease_in_quad."""
    return t * t


def check(x, y, s=0.2, color=INK, w=7):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))


def cursor(x, y, s=0.45):
    return Polygon([x, y, 0], [x, y - s, 0], [x + s * 0.28, y - s * 0.72, 0], [x + s * 0.62, y - s * 0.66, 0],
                   fill_color=INK, fill_opacity=1, stroke_color=CARD, stroke_width=2)


def pill(x, y, w, h=0.62, fill="#FFFFFF"):
    return RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color=fill, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


# ═════════════════════════════ pacing (narration is the clock) ═════════════════════════════
try:
    _SHEET = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "beat_sheet.json")))
    _TARGET = {b["beat_id"]: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0) for b in _SHEET["beats"]}
    _NARR = {b["beat_id"]: b["narration_text"] for b in _SHEET["beats"]}
except Exception:
    _TARGET, _NARR = {}, {}


def _elapsed(self):
    rt = getattr(getattr(self, "renderer", None), "time", None)
    return float(rt) if isinstance(rt, (int, float)) else 0.0


def until(self, phrase, lead=0.25):
    """Wait until `phrase` is spoken (its character share of the narration × the measured audio)."""
    bid = type(self).__name__.split("_")[0]
    n, target = _NARR.get(bid, ""), _TARGET.get(bid, 0)
    if not n or not target or phrase not in n:
        return
    gap = target * n.index(phrase) / len(n) - lead - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def finish(self):
    target = _TARGET.get(type(self).__name__.split("_")[0], 0)
    self.wait(max(0.3, target - _elapsed(self)) if target else 2.0)


# ═════════════════════════════ v2 design system ═════════════════════════════
# Colour roles (defined once; text is always INK — red and grey fail the 4.5:1 type floor on cream).
KRAFT, KRAFT2 = BOX_R, BOX_L          # existing tools + existing evidence
RED = TERRA                            # disagreement / the clause in question only (shapes, never type)
PLAN = BAR1                            # planned / will exist (grey outlines only)
RAIL = ["What", "Why", "Who", "Proves", "Scope", "Risk", "Why me"]
_HERE = _os.path.dirname(_os.path.abspath(__file__))

try:
    _WORDS = _json.load(open(_os.path.join(_HERE, "mp3", "words.json")))
    _FPS = float(_WORDS.get("fps", 24))
except Exception:
    _WORDS, _FPS = {"beats": {}}, 24.0


def _bid(self):
    return type(self).__name__.split("_")[0]


def _mid(self):
    return _TARGET.get(_bid(self), 0) / 2


def word_t(self, word, nth=1):
    """Start time (s) of the nth spoken occurrence of `word` in this beat (whisper/forced-alignment clock)."""
    seen = 0
    for w in _WORDS["beats"].get(_bid(self), []):
        if w["text"].strip(".,:;?!'\"").lower() == word.lower():
            seen += 1
            if seen == nth:
                return w["startFrame"] / _FPS
    return None


def P(self, *anims, rt=0.6):
    """play() that never animates across the clip midpoint (GATE T and Gate V sample it).
    If a move would cross it, shorten the move to finish before the midpoint when there's room (>= 0.3 s);
    otherwise wait until just after the midpoint."""
    mid, t = _mid(self), _elapsed(self)
    if mid and t < mid + 0.25 and t + rt > mid - 0.25:
        room = mid - 0.25 - t
        if room >= 0.3:
            rt = room
        else:
            self.wait(max(0.05, mid + 0.27 - t))
    self.play(*anims, run_time=rt)


def on(self, word, nth=1, lead=0.1):
    """Wait until `word` is spoken (falls back to no wait in Gate A's sandbox)."""
    t = word_t(self, word, nth)
    if t is None:
        return
    gap = t - lead - _elapsed(self)
    if gap > 0.04:
        self.wait(gap)


def rail(active=None):
    """Progress rail along the top: seven marks, the current one filled."""
    g = VGroup()
    xs = [-5.45 + i * 1.72 for i in range(7)]
    for name, x in zip(RAIL, xs):
        filled = name == active
        dot = Circle(radius=0.1, stroke_color=INK, stroke_width=4,
                     fill_color=INK if filled else STAGE, fill_opacity=1).move_to([x - 0.55, 3.1, 0])
        lab = T(name, 32, bold=filled).move_to([0, 3.1, 0]).align_to([x - 0.36, 0, 0], LEFT)
        g.add(dot, lab)
    return g


def tag(s):
    return T(s, 32).move_to([0, -3.05, 0]).align_to([-6.0, 0, 0], LEFT)


def card(x, y, w, h, stroke=INK, sw=4, fill=CARD):
    return RoundedRectangle(width=w, height=h, corner_radius=0.1, fill_color=fill, fill_opacity=1,
                            stroke_color=stroke, stroke_width=sw).move_to([x, y, 0])


def plan_box(x, y, w, h, fill=False):
    """Grey dashed outline (optionally on a light grey fill): something that will exist."""
    out = DashedVMobject(RoundedRectangle(width=w, height=h, corner_radius=0.1, stroke_color=PLAN,
                                          stroke_width=5).move_to([x, y, 0]), num_dashes=28)
    if not fill:
        return out
    return VGroup(RoundedRectangle(width=w, height=h, corner_radius=0.1, stroke_width=0, fill_color=BAR2,
                                   fill_opacity=0.3).move_to([x, y, 0]), out)


class Rubric:
    """The recurring rubric page: five clause bars C1–C5 inside an ink card; clause labels sit outside it."""
    def __init__(self, x, y, w=1.7, h=2.3, labels=True, only=None):
        band = max(0.19, min(0.34, h * 0.14))   # never thinner than GATE T's 41 px type floor
        self.page = VGroup(card(x, y, w, h),
                           Rectangle(width=w - 0.08, height=band, fill_color=DARK_TOP, fill_opacity=1,
                                     stroke_width=0).move_to([x, y + h / 2 - band / 2 - 0.04, 0]))
        top, gap = y + h / 2 - 0.42 - band * 0.6, (h - 0.84 - band * 0.6) / 4
        self.bars = VGroup(*[Line([x - w / 2 + 0.28, top - i * gap, 0], [x + w / 2 - 0.28 - (0.3 if i % 2 else 0), top - i * gap, 0],
                                  color=BAR2, stroke_width=11) for i in range(5)])
        idx = range(5) if only is None else only   # small pages label only the clause in question
        self.labels = VGroup(*[T(f"C{i + 1}", 32).move_to([x - w / 2 - 0.38, top - i * gap, 0]) for i in idx]) if labels else VGroup()
        self.x, self.y, self.w = x, y, w

    def group(self):
        return VGroup(self.page, self.bars, self.labels)

    def mark(self, i=3):
        """The red accent on clause i (C4 by default): a dot at the clause's start."""
        b = self.bars[i]
        return Dot([self.x - self.w / 2 + 0.14, b.get_center()[1], 0], radius=0.09, color=RED)


def _load_sample():
    """Real numbers for B05, read from the committed files (asserted against the constants below)."""
    rows = [("IS1004d", 12, 32.6, 258), ("ES2006d", 10, 33.2, 258), ("IS1009d", 9, 32.1, 244),
            ("ES2008c", 8, 35.0, 237), ("ES2010b", 8, 29.4, 276), ("ES2011b", 8, 26.4, 250),
            ("ES2013d", 8, 31.6, 232), ("IS1003c", 8, 31.2, 244), ("IS1005c", 8, 34.4, 248),
            ("ES2007a", 7, 20.4, 224)]
    cs = _os.path.join(_HERE, "..", "case-study")
    if _os.path.exists(cs):
        import csv
        sel = {r["meeting"]: r for r in csv.DictReader(open(_os.path.join(cs, "data", "sample", "selection.csv")))
               if r["selected"] == "True"}
        assert sorted(sel) == sorted(r[0] for r in rows), "B05: selected meetings differ from selection.csv"
        for m, dec, mins, words in rows:
            assert int(sel[m]["decisions"]) == dec, f"B05: {m} DECISIONS != selection.csv"
            assert round(float(sel[m]["duration_s"]) / 60, 1) == mins, f"B05: {m} duration != selection.csv"
            rec = _json.load(open(_os.path.join(cs, "outputs", "feature-run", f"{m}.json")))["recap"]
            assert len(rec.split()) == words, f"B05: {m} recap word count != feature-run output"
    return rows


SAMPLE = _load_sample()


def judge_token(x, y, r=0.46):
    """A judge model: a kraft disc with a dark lens (existing models are kraft)."""
    return VGroup(Circle(radius=r, stroke_width=0, fill_color=KRAFT, fill_opacity=1).move_to([x, y, 0]),
                  Circle(radius=r * 0.4, stroke_width=0, fill_color=DARK_TOP, fill_opacity=1).move_to([x, y, 0]))


def stamp(x, y, ok=True, r=0.27):
    """A verdict stamp beside a judge: a filled disc (dark = pass, red = fail) with a light mark; the word sits beside it."""
    disc = Circle(radius=r, stroke_width=0, fill_color=DARK_TOP if ok else RED, fill_opacity=1).move_to([x, y, 0])
    if ok:
        mark = check(x - 0.02, y + 0.02, s=0.12, color=CARD, w=6)
    else:
        mark = VGroup(Line([x - 0.11, y - 0.11, 0], [x + 0.11, y + 0.11, 0], color=CARD, stroke_width=6),
                      Line([x - 0.11, y + 0.11, 0], [x + 0.11, y - 0.11, 0], color=CARD, stroke_width=6))
    return VGroup(disc, mark)


def folder(x, y, w=1.3, h=0.85):
    """A grey (planned) folder outline."""
    tab = Polygon([x - w / 2, y + h / 2, 0], [x - w / 2 + 0.45, y + h / 2, 0], [x - w / 2 + 0.55, y + h / 2 + 0.16, 0],
                  [x - w / 2 + 0.05, y + h / 2 + 0.16, 0], stroke_color=PLAN, stroke_width=5)
    return VGroup(plan_box(x, y, w, h, fill=True), tab)


def doc_icon(x, y, w=0.55, h=0.72, fill=CARD, stroke=INK):
    page = card(x, y, w, h, stroke=stroke, sw=3, fill=fill)
    lines = VGroup(*[Line([x - w / 2 + 0.1, y + h / 2 - 0.2 - i * 0.16, 0], [x + w / 2 - 0.1, y + h / 2 - 0.2 - i * 0.16, 0],
                          color=BAR2, stroke_width=5) for i in range(3)])
    return VGroup(page, lines)


def left(t, x):
    return t.align_to([x, 0, 0], LEFT)


def padlock(x, y):
    shackle = Arc(radius=0.28, start_angle=0, angle=PI, arc_center=[x, y + 0.36, 0], color=INK, stroke_width=9)
    body = Rectangle(width=0.95, height=0.72, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    return VGroup(shackle, body)


def anchor(x, y):
    ring = Circle(radius=0.16, color=INK, stroke_width=7).move_to([x, y + 0.75, 0])
    shank = Line([x, y + 0.59, 0], [x, y - 0.55, 0], color=INK, stroke_width=8)
    arm = Arc(radius=0.55, start_angle=PI, angle=PI, color=INK, stroke_width=8).move_to([x, y - 0.3, 0])
    return VGroup(ring, shank, arm)


EXCERPT = "Include a lock function so buttons can't be pressed by accident"
TRANSCRIPT_LINE = "it can just have a lock function,"
try:  # every real excerpt on screen must be a verbatim substring of its source file
    _cs = _os.path.join(_HERE, "..", "case-study")
    if _os.path.exists(_cs):
        _rec = _json.load(open(_os.path.join(_cs, "outputs", "feature-run", "ES2007a.json")))["recap"]
        assert EXCERPT in _rec and "[00:17:52]" in _rec, "excerpt not in the recorded ES2007a output"
        _tr = open(_os.path.join(_cs, "data", "sample", "ES2007a", "transcript.txt")).read()
        assert "[00:17:52] C (UI):" in _tr and TRANSCRIPT_LINE in _tr, "transcript line not in ES2007a transcript"
except FileNotFoundError:
    pass


# ═════════════════════════════ B05 — scope (Q5): the real-data beat ═════════════════════════════
class B05_InOutFirst(Scene):
    def construct(self):
        self.add(rail("Scope"), tag("AMI sample · CC BY 4.0 · downloaded 14 Oct 2026"))
        rb = Rubric(4.3, 1.45, w=1.5, h=2.0, only=[3])
        page = rb.group()
        self.add(page)
        cons = T("CONSTRUCTED", 32).move_to([4.3, -0.1, 0])
        P(self, Indicate(rb.page, color=INK, scale_factor=1.06), FadeIn(cons), rt=0.6)

        # 1. ten real meeting cards fan out
        on(self, "ten")
        cards = VGroup(*[card(-3.4 + (i - 4.5) * 0.32, 0.2 + abs(i - 4.5) * -0.06, 1.0, 1.35, stroke=INK, sw=3, fill=KRAFT2)
                         .rotate((i - 4.5) * 0.06) for i in range(10)])
        P(self, LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cards], lag_ratio=0.08), rt=0.9)

        # 2. cards re-flow into rows: real meeting IDs + DECISIONS bars (ValueTracker growth)
        y0, dy, x0, k = 1.95, 0.44, -4.05, 0.3
        ys = [y0 - i * dy for i in range(10)]
        stubs = VGroup(*[Rectangle(width=0.08, height=0.3, fill_color=KRAFT, fill_opacity=1, stroke_width=0)
                         .move_to([x0 + 0.04, y, 0]) for y in ys])
        P(self, *[ReplacementTransform(c, s) for c, s in zip(cards, stubs)], rt=0.7)
        ids = VGroup(*[T(m, 32).move_to([-5.0, y, 0]) for (m, *_), y in zip(SAMPLE, ys)])
        hdr = T("decisions", 34).move_to([-2.25, 2.45, 0])
        P(self, LaggedStart(*[FadeIn(t, shift=RIGHT * 0.15) for t in ids], lag_ratio=0.06), FadeIn(hdr), rt=0.8)
        grow = ValueTracker(0.0)
        bars = VGroup(*[always_redraw(lambda d=d, y=y: Rectangle(
            width=max(0.08, d * k * grow.get_value()), height=0.3, fill_color=KRAFT, fill_opacity=1, stroke_width=0)
            .move_to([x0 + max(0.08, d * k * grow.get_value()) / 2, y, 0])) for (_, d, *_), y in zip(SAMPLE, ys)])
        self.remove(stubs)
        self.add(bars)
        P(self, grow.animate.set_value(1.0), rt=1.1)
        for b in bars:
            b.clear_updaters()  # freeze the grown bars so later focus dims apply
        vals = VGroup(*[T(str(d), 32).move_to([x0 + d * k + 0.28, y, 0]) for (_, d, *_), y in zip(SAMPLE, ys)])
        P(self, LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.05), rt=0.5)

        # 3. real recap word counts against the 250-word cap; the IS1004d tension, stated as a sourced fact
        on(self, "design")
        wx0, wk = 0.35, 2.4 / 300
        whdr = T("recap words", 34).move_to([1.55, 2.45, 0])
        wgrow = ValueTracker(0.0)
        wbars = VGroup(*[always_redraw(lambda n=n, y=y: Rectangle(
            width=max(0.06, n * wk * wgrow.get_value()), height=0.22, fill_color=KRAFT2, fill_opacity=1, stroke_width=0)
            .move_to([wx0 + max(0.06, n * wk * wgrow.get_value()) / 2, y, 0])) for (*_, n), y in zip(SAMPLE, ys)])
        self.add(wbars)
        P(self, FadeIn(whdr), wgrow.animate.set_value(1.0), rt=0.8)
        for b in wbars:
            b.clear_updaters()
        capx = wx0 + 250 * wk
        cap = DashedLine([capx, 2.15, 0], [capx, -2.2, 0], color=INK, stroke_width=4, dash_length=0.12)
        capl = T("250", 32).move_to([capx, -2.55, 0])
        P(self, Create(cap), FadeIn(capl), rt=0.5)
        call = T("IS1004d: 12 decisions, 250-word cap", 32).move_to([-2.3, -2.55, 0])
        P(self, Circumscribe(VGroup(ids[0], bars[0], vals[0]), color=INK, buff=0.06), FadeIn(call), rt=0.7)
        chart = VGroup(ids, bars, vals, hdr, whdr, wbars, cap, capl, call)
        keep = VGroup(ids, bars, vals, hdr, whdr, wbars, cap, capl)
        keep.save_state()

        # 4. OUT: Readback never rewrites the rubric (focus moves to the rubric; the chart dims)
        on(self, "Out")
        out = T("OUT", 38, bold=True).move_to([5.68, 2.28, 0])
        ul = Line([5.2, 1.86, 0], [6.16, 1.86, 0], color=RED, stroke_width=8)
        nev = VGroup(T("never rewrites", 34), T("the rubric", 34)).arrange(DOWN, buff=0.08).move_to([4.6, -0.8, 0])
        P(self, chart.animate.set_opacity(0.3), FadeIn(out, shift=DOWN * 0.25), Create(ul), rt=0.6)
        P(self, FadeIn(nev, shift=UP * 0.15), rt=0.4)
        on(self, "itself")
        dot = rb.mark(3)
        P(self, FadeIn(dot), Indicate(rb.bars[3], color=RED, scale_factor=1.15), rt=0.6)
        on(self, "asks")
        q = VGroup(card(5.82, 1.45, 0.62, 0.62, fill="#FFFFFF"), T("?", 40).move_to([5.82, 1.45, 0]))
        qa = Arrow(dot.get_center() + np.array([0.0, 0.0, 0]), [5.47, 1.42, 0], color=INK, stroke_width=6, buff=0.12,
                   max_tip_length_to_length_ratio=0.15)
        P(self, GrowArrow(qa), FadeIn(q, shift=LEFT * 0.2), rt=0.5)
        on(self, "decides")
        pm = VGroup(Circle(radius=0.38, color=INK, stroke_width=5).move_to([5.84, 0.66, 0]), T("PM", 30).move_to([5.84, 0.66, 0]))
        P(self, FadeIn(pm, scale=0.6), Indicate(q, color=INK, scale_factor=1.15), rt=0.5)

        # 5. the first run, planned (grey); at "agreement table" focus leaves the rubric block
        on(self, "First")
        block = VGroup(page, cons, out, ul, nev, dot, qa, q, pm)
        block.save_state()
        fr = T("first run · planned", 34).move_to([4.5, -1.5, 0])
        P(self, FadeIn(fr, shift=UP * 0.15), rt=0.5)
        items = ["1 rubric", "3 judges", "my labels"]
        checks = VGroup()
        for i, (txt, word) in enumerate(zip(items, ["one", "three", "labels"])):
            on(self, word)
            y = -1.92 - i * 0.46
            box = plan_box(3.0, y, 0.3, 0.3)
            lab = T(txt, 32).move_to([0, y, 0]).align_to([3.27, 0, 0], LEFT)
            checks.add(box, lab)
            P(self, Create(box), FadeIn(lab, shift=RIGHT * 0.1), rt=0.4)
        on(self, "agreement")
        arr = Arrow([5.22, -2.84, 0], [5.48, -2.84, 0], color=INK, stroke_width=6, buff=0, max_tip_length_to_length_ratio=0.4)
        tbl = VGroup(RoundedRectangle(width=0.8, height=0.7, corner_radius=0.08, stroke_color=PLAN, stroke_width=6,
                                      fill_color=GHOST, fill_opacity=1).move_to([5.88, -2.4, 0]),
                     Line([5.48, -2.4, 0], [6.28, -2.4, 0], color=PLAN, stroke_width=4),
                     Line([5.88, -2.05, 0], [5.88, -2.75, 0], color=PLAN, stroke_width=4))
        P(self, block.animate.set_opacity(0.3), GrowArrow(arr), FadeIn(tbl, shift=LEFT * 0.2), rt=0.6)

        # 6. "its commit comes after my labels' commit" (planned order); the checklist dims, the cap call-out gives way
        on(self, "commit")
        plan = VGroup(fr, checks, arr, tbl)
        plan.save_state()
        d1 = Circle(radius=0.2, color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=1).move_to([-4.75, -2.55, 0])
        l1 = T("labels", 34).move_to([0, -2.55, 0]).align_to([-4.42, 0, 0], LEFT)
        P(self, FadeOut(call), rt=0.3)
        P(self, plan.animate.set_opacity(0.35), FadeIn(d1, scale=0.5), FadeIn(l1), rt=0.5)
        on(self, "after")
        ordr = Arrow([-3.2, -2.55, 0], [-2.35, -2.55, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.3)
        d2 = Circle(radius=0.2, color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=1).move_to([-2.05, -2.55, 0])
        l2 = T("report", 34).move_to([0, -2.55, 0]).align_to([-1.72, 0, 0], LEFT)
        P(self, GrowArrow(ordr), FadeIn(d2, shift=RIGHT * 0.3), FadeIn(l2), rt=0.5)

        # closing state: the whole scope at full contrast (real data, the rule, the plan)
        P(self, Restore(keep), Restore(block), Restore(plan), rt=0.7)
        finish(self)




# ═════════════════════════════ BIDEA — hook ═════════════════════════════
class BIDEA_Hook(Scene):
    def construct(self):
        self.add(rail(None), tag("CONSTRUCTED — no judges have run yet"))
        rb = Rubric(-3.9, 0.3, w=2.6, h=3.4)
        P(self, FadeIn(rb.page, shift=UP * 0.4), rt=0.3)
        who = VGroup(T("Aravind Ravi", 48, bold=True), T("read by a synthetic voice", 36)).arrange(DOWN, buff=0.12).move_to([2.2, 1.0, 0])
        for i, t in enumerate([0.4, 0.95, 1.5, 2.05, 2.6]):
            if i == 1:
                P(self, FadeIn(who[0], shift=UP * 0.3), rt=0.4)
            if i == 4:
                P(self, FadeIn(who[1], shift=UP * 0.3), rt=0.4)
            if _elapsed(self) < t:
                self.wait(t - _elapsed(self))
            P(self, Create(rb.bars[i]), FadeIn(rb.labels[i], shift=RIGHT * 0.1), rt=0.45)
        on(self, "When")
        hdr = T("my eval rubric", 44, bold=True).move_to([-3.9, -2.15, 0])
        P(self, FadeIn(hdr, shift=UP * 0.2), rt=0.5)
        on(self, "AI")
        rec = VGroup(card(0.2, 0.4, 2.3, 2.9, stroke=INK, sw=4, fill=KRAFT2),
                     *[Line([-0.65, 1.3 - i * 0.45, 0], [1.05 - (0.4 if i % 2 else 0), 1.3 - i * 0.45, 0], color=CARD, stroke_width=10)
                       for i in range(5)])
        recl = T("a recap", 40).move_to([0.2, -1.4, 0])
        P(self, FadeOut(who), rt=0.3)
        P(self, FadeIn(rec, shift=LEFT * 0.4), FadeIn(recl), rt=0.5)
        on(self, "judge")
        ys = [1.9, 0.75, -0.4]
        js = VGroup(*[judge_token(3.2, y) for y in ys])
        links = VGroup(*[Line([2.72, y, 0], [1.4, 0.4 + (y - 0.75) * 0.5, 0], color=INK, stroke_width=6) for y in ys])
        jl = T("3 judges", 40).move_to([3.2, -1.4, 0])
        P(self, LaggedStart(*[FadeIn(j, shift=LEFT * 0.4) for j in js], lag_ratio=0.2), Create(links), FadeIn(jl), rt=0.6)
        stamps = []
        for (ok, word), y, t in zip([(True, "pass"), (True, "pass"), (False, "fail")], ys, [6.5, 7.0, 7.5]):
            if _elapsed(self) < t:
                self.wait(t - _elapsed(self))
            st = VGroup(stamp(4.25, y, ok), T(word, 40, bold=True).move_to([5.15, y, 0]))
            stamps.append(st)
            P(self, FadeIn(st, scale=1.5), rt=0.35)
        on(self, "question")
        dot = rb.mark(3)
        P(self, VGroup(rec, recl, js, links, jl, *stamps[:2]).animate.set_opacity(0.3), FadeIn(dot, scale=2.5),
          Indicate(rb.bars[3], color=RED, scale_factor=1.15), rt=0.6)
        on(self, "passes")
        ray = Line([4.0, -0.4, 0], rb.bars[3].get_right() + np.array([0.15, 0, 0]), color=RED, stroke_width=7)
        P(self, Create(ray), Circumscribe(VGroup(rb.bars[3], rb.labels[3], dot), color=RED, buff=0.08), rt=0.7)
        on(self, "whether", nth=2)
        q = "Does the judge misread my rubric?"
        line = Text(q, font=SERIF, color=INK, font_size=52).move_to([0.9, -2.15, 0])
        P(self, FadeOut(hdr), FadeOut(ray), rt=0.3)
        P(self, AddTextLetterByLetter(line, time_per_char=1.9 / len(q)), rt=1.9)
        finish(self)


# ═════════════════════════════ B01 — what it is ═════════════════════════════
class B01_WhatItIs(Scene):
    def construct(self):
        self.add(rail("What"), tag("CONSTRUCTED · grey = planned"))
        rb = Rubric(-3.9, 0.3, w=2.6, h=3.4)
        ys = [1.9, 0.75, -0.4]
        js = VGroup(*[judge_token(3.2, y) for y in ys])
        self.add(rb.group(), js)
        on(self, "Readback")
        title = T("Readback", 72, bold=True).move_to([0.0, 2.3, 0])
        P(self, FadeIn(title, shift=UP * 0.2), rt=0.6)
        on(self, "clause")
        c4 = rb.bars[3].get_right() + np.array([0.12, 0, 0])
        rays = VGroup(*[Line([2.72, y, 0], c4, color=INK, stroke_width=6) for y in ys])
        P(self, LaggedStart(*[Create(r) for r in rays], lag_ratio=0.25), rt=0.8)
        on(self, "reads")
        dot = rb.mark(3)
        P(self, FadeIn(dot, scale=2.5), rays.animate.set_color(RED), Indicate(rb.bars[3], color=RED, scale_factor=1.15), rt=0.6)
        on(self, "meant")
        bub = T("Did you mean…?", 48).move_to([0.6, 0.7, 0])
        tail = Line(c4 + np.array([0.15, 0.05, 0]), [-1.8, 0.55, 0], color=INK, stroke_width=5)
        pm = VGroup(Circle(radius=0.46, color=INK, stroke_width=6).move_to([0.6, -0.3, 0]), T("PM", 36).move_to([0.6, -0.3, 0]))
        P(self, FadeOut(rays), js.animate.set_opacity(0.25), rt=0.3)
        P(self, Create(tail), FadeIn(bub, shift=RIGHT * 0.3), rt=0.5)
        P(self, FadeIn(pm, scale=0.6), rt=0.4)
        on(self, "When")
        icon = Rubric(5.75, 2.32, w=0.5, h=0.66, labels=False)
        P(self, FadeOut(VGroup(dot, tail, bub, pm, js, rb.labels)), rt=0.3)
        P(self, title.animate.scale(0.75).move_to([-4.3, 2.47, 0]), rt=0.4)
        P(self, ReplacementTransform(VGroup(rb.page, rb.bars), icon.group()), rt=0.5)
        on(self, "repository")
        repo = VGroup(folder(-3.6, 0.15, w=2.2, h=1.5), T("repo", 40).move_to([-3.6, -1.0, 0]))
        P(self, FadeIn(repo, shift=UP * 0.3), rt=0.5)
        on(self, "command-line")
        cmd = "$ readback-pm check rubric.md"
        cli = Text(cmd, font="PT Mono", color=INK, font_size=32).move_to([0, -2.25, 0])
        left(cli, -5.6)
        P(self, AddTextLetterByLetter(cli, time_per_char=1.0 / len(cmd)), rt=1.0)
        on(self, "case")
        cs = VGroup(folder(0.4, 0.15, w=2.2, h=1.5), T("case study", 40).move_to([0.4, -1.0, 0]))
        P(self, FadeIn(cs, shift=UP * 0.3), rt=0.5)
        on(self, "log")
        lg = VGroup(plan_box(3.9, 0.2, 1.4, 1.7, fill=True),
                    *[DashedLine([3.4, 0.65 - i * 0.35, 0], [4.4, 0.65 - i * 0.35, 0], color=PLAN, stroke_width=5) for i in range(4)],
                    T("eval log", 40).move_to([3.9, -0.95, 0]))
        P(self, FadeIn(lg, shift=UP * 0.3), rt=0.5)
        on(self, "revision")
        ba = VGroup(T("before", 36).move_to([3.1, -1.6, 0]),
                    Arrow([3.85, -1.6, 0], [4.55, -1.6, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.3),
                    T("after", 36).move_to([5.2, -1.6, 0]))
        P(self, FadeIn(ba, shift=LEFT * 0.3), Indicate(lg, color=INK, scale_factor=1.08), rt=0.6)
        finish(self)


# ═════════════════════════════ B02 — why anyone would care ═════════════════════════════
class B02_Difference(Scene):
    def construct(self):
        self.add(rail("Why"))
        rb = Rubric(-3.9, 0.3, w=2.6, h=3.4)
        start = Rubric(5.75, 2.32, w=0.5, h=0.66, labels=False)
        self.add(start.group())
        P(self, ReplacementTransform(start.group(), rb.group()), rt=0.7)
        on(self, "misreads")
        dot = rb.mark(3)
        P(self, FadeIn(dot, scale=2.5), Indicate(rb.bars[3], color=RED, scale_factor=1.15), rt=0.6)
        on(self, "look")
        sc = VGroup(T("score:", 52).move_to([0.6, 1.0, 0]), T("pass", 52, bold=True).move_to([2.45, 1.0, 0]), stamp(3.65, 1.02, True, r=0.34))
        P(self, FadeIn(sc, shift=UP * 0.3), rt=0.5)
        on(self, "wrong")
        wr = VGroup(T("ship decision:", 44).move_to([1.1, -0.4, 0]), T("wrong", 44, bold=True).move_to([3.4, -0.4, 0]),
                    stamp(4.55, -0.38, False, r=0.3))
        P(self, FadeIn(wr, shift=UP * 0.3), rt=0.5)

        # the comparison grid, built row by row, only from FRICTIONAL.md's logged checks (14 Oct 2026)
        on(self, "two")
        COLS = {"m": 0.05, "o": 2.3, "r": 4.55}
        ROWY = [1.55, 0.85, 0.15, -0.55, -1.25]
        ROWS = ["compares several judges", "judge–human agreement", "rewrites the judge prompt",
                "names the clause", "asks the PM"]
        icon = Rubric(5.9, 2.38, w=0.45, h=0.6, labels=False)
        heads = VGroup(T("Maxim AI", 36).move_to([COLS["m"], 2.38, 0]), T("orq.ai", 36).move_to([COLS["o"], 2.38, 0]),
                       T("Readback", 36, bold=True).move_to([COLS["r"], 2.38, 0]))
        rlabs = VGroup(*[left(T(r, 32).move_to([0, y, 0]), -6.0) for r, y in zip(ROWS, ROWY)])
        rule = Line([-6.0, 1.97, 0], [6.1, 1.97, 0], color=BAR2, stroke_width=3)
        foot = tag("per their public docs, as of 14 Oct 2026 · names only")
        colbg = VGroup(*[RoundedRectangle(width=2.0, height=3.6, corner_radius=0.12, stroke_width=0, fill_color=KRAFT2,
                                          fill_opacity=0.3).move_to([COLS[c], 0.15, 0]) for c in ("m", "o")])
        P(self, FadeOut(VGroup(sc, wr, rb.labels, dot)), rt=0.3)
        P(self, ReplacementTransform(VGroup(rb.page, rb.bars), icon.group()), rt=0.5)
        P(self, FadeIn(colbg), FadeIn(heads), Create(rule), FadeIn(foot), rt=0.5)
        P(self, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in rlabs], lag_ratio=0.12), rt=0.7)

        def yes(col, row):
            return stamp(COLS[col], ROWY[row], True, r=0.24)

        def nf(col, row):
            return T("not found", 32).move_to([COLS[col], ROWY[row], 0])

        def planned(row, word="planned"):
            x, y = COLS["r"], ROWY[row]
            t = T(word, 32).move_to([x, y, 0])
            u = DashedLine([x - 0.65, y - 0.27, 0], [x + 0.65, y - 0.27, 0], color=PLAN, stroke_width=5)
            return VGroup(t, u)

        on(self, "several")
        P(self, FadeIn(yes("m", 0), scale=0.5), Indicate(rlabs[0], color=INK, scale_factor=1.08), rt=0.4)
        on(self, "agree")
        P(self, FadeIn(yes("m", 1), scale=0.5), Indicate(rlabs[1], color=INK, scale_factor=1.08), rt=0.4)
        on(self, "humans")
        P(self, LaggedStart(*[FadeIn(nf("m", r)) for r in (2, 3, 4)], lag_ratio=0.2), rt=0.6)
        on(self, "compares")
        P(self, FadeIn(nf("o", 0)), colbg[0].animate.set_opacity(0.12), colbg[1].animate.set_opacity(0.6), rt=0.5)
        on(self, "human")
        P(self, FadeIn(yes("o", 1), scale=0.5), rt=0.35)
        on(self, "rewrites")
        P(self, FadeIn(yes("o", 2), scale=0.5), Indicate(rlabs[2], color=INK, scale_factor=1.08), rt=0.4)
        on(self, "prompt")
        P(self, LaggedStart(*[FadeIn(nf("o", r)) for r in (3, 4)], lag_ratio=0.2), rt=0.5)
        on(self, "docs")
        P(self, colbg.animate.set_opacity(0.3), Circumscribe(foot, color=INK, buff=0.08), rt=0.8)
        on(self, "clause")
        hl = RoundedRectangle(width=12.2, height=0.6, corner_radius=0.1, stroke_width=0, fill_color=KRAFT2,
                              fill_opacity=0.8).move_to([0.05, ROWY[3], 0])
        self.add(hl)
        self.bring_to_back(hl)
        P(self, FadeIn(hl), rt=0.5)
        on(self, "Readback")
        rbg = RoundedRectangle(width=2.0, height=3.6, corner_radius=0.12, stroke_color=PLAN, stroke_width=6,
                               fill_color=GHOST, fill_opacity=0.3).move_to([COLS["r"], 0.15, 0])
        self.bring_to_back(rbg)
        P(self, FadeIn(rbg), FadeOut(hl), LaggedStart(*[FadeIn(planned(r)) for r in (3, 0, 1)], lag_ratio=0.25), rt=0.7)
        on(self, "clause", nth=2)
        P(self, FadeIn(planned(4)), Indicate(icon.group(), color=INK, scale_factor=1.08), rt=0.4)
        on(self, "rewriting")
        P(self, FadeIn(planned(2, "never")), Indicate(rlabs[2], color=INK, scale_factor=1.08), rt=0.4)
        sk = VGroup(left(T("specs (later module): Spec Kit clarify", 32).move_to([0, -2.2, 0]), -6.0),
                    Line([-6.0, -1.82, 0], [6.1, -1.82, 0], color=BAR2, stroke_width=3))
        P(self, FadeIn(sk, shift=UP * 0.2), rt=0.5)
        finish(self)


# ═════════════════════════════ B03 — who opens it ═════════════════════════════
class B03_FirstMinute(Scene):
    def construct(self):
        self.add(rail("Who"), tag("CONSTRUCTED mock-up — values will be measured"))
        icon = Rubric(5.75, 2.32, w=0.5, h=0.66, labels=False)
        self.add(icon.group())
        on(self, "reader")
        head = Circle(radius=0.4, stroke_width=0, fill_color=DARK_TOP, fill_opacity=1).move_to([-4.8, 1.6, 0])
        body = Sector(radius=0.75, angle=PI, start_angle=0, stroke_width=0, fill_color=DARK_TOP, fill_opacity=1).move_to([-4.8, 0.82, 0])
        P(self, FadeIn(head, shift=UP * 0.3), FadeIn(body, shift=UP * 0.3), rt=0.6)
        hl = VGroup(T("hiring manager", 36), T("AI product roles", 32)).arrange(DOWN, buff=0.1).move_to([-4.8, -0.3, 0])
        P(self, FadeIn(hl[0], shift=UP * 0.15), rt=0.4)
        on(self, "roles")
        P(self, FadeIn(hl[1], shift=UP * 0.15), rt=0.4)
        on(self, "first")
        clock = VGroup(Circle(radius=0.42, color=INK, stroke_width=7), Line([0, 0.42, 0], [0, 0.62, 0], color=INK, stroke_width=9)).move_to([5.05, -1.92, 0])
        sl = left(T("first 60 seconds", 34).move_to([0, -2.0, 0]), 1.55)
        P(self, FadeIn(clock, scale=0.5), FadeIn(sl, shift=LEFT * 0.3), rt=0.5)
        on(self, "open")
        win = card(1.35, -0.2, 8.5, 4.7, stroke=BAR1, sw=5, fill="#FFFFFF")
        bar = Rectangle(width=8.5, height=0.42, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([1.35, 1.94, 0])
        rn = left(T("README.md", 36, bold=True).move_to([0, 2.5, 0]), -2.9)
        fill = VGroup(*[Line([-2.55, 1.35 - i * 0.38, 0], [4.9 - (1.2 if i % 3 == 1 else 0), 1.35 - i * 0.38, 0],
                             color=BAR2, stroke_width=12) for i in range(7)])
        self.bring_to_front(clock, sl)
        P(self, VGroup(head, body, hl).animate.set_opacity(0.4), FadeIn(win), FadeIn(bar), FadeIn(rn), FadeIn(fill),
          icon.group().animate.move_to([3.0, 2.55, 0]), rt=0.6)
        self.bring_to_front(clock, sl)
        on(self, "table")
        cur = cursor(4.4, 0.9, s=0.6)
        P(self, FadeIn(cur), FadeOut(fill, shift=UP * 0.3), cur.animate.shift(DOWN * 1.2 + LEFT * 0.9), rt=0.8)
        heads = ["per clause", "most disagreed", "question asked", "revision", "held-out before/after"]
        words = [("per-clause", 1), ("disagreed", 1), ("question", 1), ("revision", 1), ("held-out", 1)]
        ys = [1.25, 0.6, -0.05, -0.7, -1.35]
        grid = VGroup(*[Line([-2.65, y - 0.32, 0], [5.3, y - 0.32, 0], color=BAR2, stroke_width=3) for y in ys[:-1]])
        P(self, FadeOut(cur), Create(grid), rt=0.5)
        for h, (w, n), y in zip(heads, words, ys):
            on(self, w, n)
            lab = left(T(h, 34).move_to([0, y, 0]), -2.55)
            band = RoundedRectangle(width=7.9, height=0.66, corner_radius=0.08, stroke_width=0, fill_color=KRAFT,
                                    fill_opacity=0.85).move_to([1.33, y, 0])
            dashes = VGroup(*[T("—", 36).move_to([x, y, 0]) for x in (2.2, 3.3, 4.4)])
            self.bring_to_back(band)
            P(self, FadeIn(band), FadeIn(lab, shift=LEFT * 0.2), FadeIn(dashes), rt=0.6)
            P(self, FadeOut(band), rt=0.3)
        on(self, "end")
        pm = VGroup(Circle(radius=0.46, color=INK, stroke_width=6).move_to([-4.8, -1.45, 0]), T("PM", 36).move_to([-4.8, -1.45, 0]))
        pml = T("end user", 34).move_to([-4.8, -2.3, 0])
        P(self, FadeIn(pm, scale=0.6), FadeIn(pml), rt=0.5)
        on(self, "own")
        P(self, Indicate(VGroup(*[m for m in self.mobjects if isinstance(m, Text) and m.get_center()[1] < 1.5 and m.get_center()[0] > -2.8 and m.get_center()[1] > -1.8]),
                         color=INK, scale_factor=1.06), rt=0.5)
        cc = clock[0].get_center()
        sweep = Arc(radius=0.26, start_angle=PI / 2, angle=-2 * PI * 0.999, arc_center=[cc[0], cc[1], 0], color=INK, stroke_width=12)
        P(self, Create(sweep), rt=1.4)
        finish(self)


# ═════════════════════════════ B04 — what it proves ═════════════════════════════
class B04_Proves(Scene):
    def construct(self):
        self.add(rail("Proves"), tag("CONSTRUCTED · grey = planned · real pair: AMI ES2007a"))
        CH = [("prompt contract", 1.62, "contract"), ("verification", 1.0, "verify"), ("evaluation", 0.3, "evaluate"),
              ("source grounding", -0.6, "ground")]
        chips = {}
        for txt, y, w in CH:
            chips[w] = VGroup(left(T(txt, 36).move_to([0, y, 0]), -5.9))
        on(self, "prove")
        ttl = left(T("it will show I can:", 44, bold=True).move_to([0, 2.55, 0]), -5.9)
        P(self, FadeIn(ttl, shift=UP * 0.15), rt=0.5)
        on(self, "contract")
        pg = Rubric(-0.85, 1.97, w=0.75, h=0.95, labels=False)
        c1 = Line([-2.35, 1.62, 0], [-1.27, 1.62, 0], color=INK, stroke_width=5)   # level: a slight slant reads as sub-floor type
        P(self, FadeIn(chips["contract"], shift=RIGHT * 0.3), FadeIn(pg.group(), scale=0.6), Create(c1), rt=0.6)
        on(self, "verify")
        P(self, FadeIn(chips["verify"], shift=RIGHT * 0.3), rt=0.4)
        on(self, "labels")
        ln = DashedLine([-0.3, 1.75, 0], [5.9, 1.75, 0], color=PLAN, stroke_width=7)
        d1 = Circle(radius=0.26, color=PLAN, stroke_width=8, fill_color=GHOST, fill_opacity=1).move_to([1.0, 1.75, 0])
        l1 = T("labels", 36).move_to([1.0, 2.4, 0])
        c2 = Line([-3.25, 1.0, 0], [0.8, 1.52, 0], color=INK, stroke_width=5)
        P(self, Create(ln), FadeIn(d1, scale=0.4), FadeIn(l1), Create(c2), rt=0.6)
        on(self, "committed")
        P(self, Indicate(VGroup(d1, l1), color=INK, scale_factor=1.35), rt=0.5)
        on(self, "runs")
        d2 = Circle(radius=0.26, color=PLAN, stroke_width=8, fill_color=GHOST, fill_opacity=1).move_to([4.2, 1.75, 0])
        l2 = T("judge runs", 36).move_to([4.2, 2.4, 0])
        P(self, FadeIn(d2, scale=0.4), FadeIn(l2), rt=0.5)
        on(self, "proves")
        oa = Arrow([1.35, 1.75, 0], [3.85, 1.75, 0], color=INK, stroke_width=9, buff=0, max_tip_length_to_length_ratio=0.12)
        pl = T("planned order", 34).move_to([2.75, 1.2, 0])
        P(self, GrowArrow(oa), FadeIn(pl), rt=0.6)
        on(self, "evaluate")
        ho = VGroup(RoundedRectangle(width=1.0, height=0.6, corner_radius=0.08, stroke_color=PLAN, stroke_width=6,
                                     fill_color=GHOST, fill_opacity=1).move_to([-1.75, 0.3, 0]))
        hol = left(T("held-out", 34).move_to([0, 0.3, 0]), -1.1)
        c3 = Line([-3.7, 0.3, 0], [-2.3, 0.3, 0], color=INK, stroke_width=5)
        P(self, FadeIn(chips["evaluate"], shift=RIGHT * 0.3), FadeIn(ho, scale=0.6), FadeIn(hol), Create(c3), rt=0.6)
        on(self, "ground")
        everything = VGroup(*[chips[k] for k in ("contract", "verify", "evaluate")], pg.group(), c1, c2, c3, ln, d1, l1, d2, l2, oa, pl, ho, hol)
        everything.save_state()
        P(self, everything.animate.set_opacity(0.3), FadeIn(chips["ground"], shift=RIGHT * 0.3), rt=0.5)
        on(self, "transcript")
        tc = card(2.6, -0.6, 7.0, 1.15, stroke=BAR1, sw=4, fill=KRAFT2)
        tt = VGroup(T("AMI ES2007a  [00:17:52] UI:", 32), T("“… it can just have a lock function,”", 32)).arrange(DOWN, buff=0.08).move_to([2.6, -0.6, 0])
        c4 = Line([-2.3, -0.6, 0], [-0.95, -0.6, 0], color=INK, stroke_width=5)
        P(self, FadeIn(tc, shift=LEFT * 0.8), FadeIn(tt, shift=LEFT * 0.8), Create(c4), rt=0.6)
        on(self, "lines")
        rc = card(2.6, -2.15, 7.0, 1.15, stroke=BAR1, sw=4, fill=KRAFT2)
        rt_ = VGroup(T("recap · Claude Opus 5.5 · 14 Oct 2026", 32), T("“Include a lock function … [00:17:52]”", 32)).arrange(DOWN, buff=0.08).move_to([2.6, -2.15, 0])
        ar = Arrow([2.6, -1.18, 0], [2.6, -1.57, 0], color=INK, stroke_width=8, buff=0, max_tip_length_to_length_ratio=0.5)
        P(self, GrowArrow(ar), FadeIn(rc), FadeIn(rt_), rt=0.6)
        on(self, "reviewer")
        P(self, Restore(everything), Circumscribe(VGroup(tc, rc), color=INK, buff=0.08), rt=0.8)
        on(self, "anchor")
        an = anchor(1.0, 0.72).scale(0.6).move_to([1.0, 0.98, 0])
        P(self, FadeIn(an), Indicate(d1, color=INK, scale_factor=1.4), rt=0.6)
        on(self, "every")
        feats = VGroup(*[RoundedRectangle(width=0.55, height=0.5, corner_radius=0.08, stroke_width=0, fill_color=KRAFT,
                                          fill_opacity=1).move_to([3.95 + i * 0.65, 0.55, 0]) for i in range(4)])
        fl = T("AI features", 34).move_to([2.6, 0.55, 0])
        P(self, LaggedStart(*[FadeIn(f, scale=0.4) for f in feats], lag_ratio=0.15), FadeIn(fl), rt=0.6)
        on(self, "one")
        fl1 = T("1 feature", 34).move_to([2.6, 0.55, 0])
        P(self, *[f.animate.set_fill(GHOST, 1) for f in feats[1:]], ReplacementTransform(fl, fl1),
          Create(check(3.97, 0.58, s=0.15, color=INK, w=7)), rt=0.5)
        finish(self)


# ═════════════════════════════ B06 — what could sink it ═════════════════════════════
class B06_Risk(Scene):
    def construct(self):
        self.add(rail("Risk"), tag("CONSTRUCTED — planned method"))
        on(self, "Overfitting")
        ov = left(T("overfitting", 48, bold=True).move_to([0, 2.45, 0]), -5.9)
        deck = VGroup(*[card(-3.6 + i * 0.1, 0.8 - i * 0.08, 1.6, 1.15, stroke=BAR1, sw=3, fill=KRAFT2) for i in range(8)])
        dl = T("examples", 36).move_to([-3.25, -0.85, 0])
        P(self, FadeIn(ov, shift=UP * 0.15), LaggedStart(*[FadeIn(c, shift=UP * 0.12) for c in deck], lag_ratio=0.08), FadeIn(dl), rt=0.7)
        on(self, "revising")
        pg = Rubric(0.6, 0.95, w=1.0, h=1.35, labels=False)
        loop = CurvedArrow([0.0, 1.8, 0], [-2.55, 1.55, 0], angle=PI / 3, color=INK, stroke_width=7)
        loop2 = CurvedArrow([-2.55, 0.0, 0], [0.0, 0.1, 0], angle=PI / 3, color=INK, stroke_width=7)
        P(self, FadeIn(pg.group(), shift=LEFT * 0.4), Create(loop), rt=0.6)
        P(self, Create(loop2), rt=0.5)
        on(self, "agree")
        P(self, Indicate(VGroup(loop, loop2, pg.group()), color=INK, scale_factor=1.12), rt=0.7)
        on(self, "examples")
        P(self, *[c.animate.shift(RIGHT * (i - 3.5) * 0.14) for i, c in enumerate(deck)], rt=0.6)
        on(self, "freeze")
        dev, held = VGroup(*deck[:5]), VGroup(*deck[5:])
        P(self, FadeOut(VGroup(loop, loop2, pg.group())), held.animate.shift(RIGHT * 3.2 + DOWN * 0.15),
          dl.animate.move_to([-3.95, -0.85, 0]), rt=0.6)
        dl2 = T("dev", 36).move_to([-3.95, -1.42, 0])
        lock = padlock(0.1, 1.35).scale(1.3)
        hl = T("held-out", 36).move_to([0.25, -0.78, 0])
        P(self, FadeIn(dl2), FadeIn(lock, shift=DOWN * 0.5), FadeIn(hl), rt=0.5)
        on(self, "numbers")
        hs = VGroup(T("held-out score:", 34), T("—", 38)).arrange(RIGHT, buff=0.15).move_to([0.25, -1.35, 0])
        P(self, FadeIn(hs, shift=UP * 0.2), Indicate(lock, color=INK, scale_factor=1.3), rt=0.5)
        on(self, "blind")
        left_side = VGroup(ov, deck, dl, dl2, lock, hl, hs)
        left_side.save_state()
        P(self, left_side.animate.set_opacity(0.3), rt=0.5)
        a = Circle(radius=0.8, stroke_color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=0.35).move_to([3.0, 0.95, 0])
        b = Circle(radius=0.8, stroke_color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=0.35).move_to([3.85, 0.95, 0])
        P(self, FadeIn(a, scale=0.5), FadeIn(b, scale=0.5), rt=0.6)
        on(self, "compare")
        sm = T("same model", 36).move_to([3.42, 2.15, 0])
        ovl = Ellipse(width=0.72, height=1.3, stroke_width=0, fill_color=BAR1, fill_opacity=1).move_to([3.42, 0.95, 0])
        P(self, FadeIn(sm), FadeIn(ovl), rt=0.5)
        on(self, "cross-model")
        c = Circle(radius=0.62, stroke_color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=0.35).move_to([2.55, -1.0, 0])
        d = Circle(radius=0.62, stroke_color=PLAN, stroke_width=7, fill_color=GHOST, fill_opacity=0.35).move_to([4.45, -1.0, 0])
        cm = T("cross-model", 36).move_to([3.5, -2.05, 0])
        P(self, FadeIn(c, shift=RIGHT * 0.5), FadeIn(d, shift=LEFT * 0.5), FadeIn(cm), rt=0.6)
        on(self, "report", nth=2)
        rp = left(T("compare both, report either way", 36).move_to([0, -2.1, 0]), -5.9)
        P(self, Restore(left_side), FadeIn(rp, shift=UP * 0.2), rt=0.6)
        finish(self)


# ═════════════════════════════ B07 — why this project ═════════════════════════════
class B07_WhyMe(Scene):
    def construct(self):
        self.add(rail("Why me"), tag("PR status as of 14 Oct 2026 · roles internal, not shown"))
        on(self, "project")
        q = T("a mix", 60, bold=True).move_to([0, 0.6, 0])
        P(self, FadeIn(q, scale=0.7), rt=0.5)
        on(self, "New")
        nl = left(T("new to me:", 36, bold=True).move_to([0, 2.4, 0]), -6.0)
        P(self, FadeOut(q), FadeIn(nl, shift=RIGHT * 0.3), rt=0.4)
        brk = VGroup(Line([-5.9, 1.42, 0], [5.9, 1.42, 0], color=INK, stroke_width=10),
                     Line([-5.9, 1.42, 0], [-5.9, 1.27, 0], color=INK, stroke_width=10),
                     Line([5.9, 1.42, 0], [5.9, 1.27, 0], color=INK, stroke_width=10))
        P(self, Create(brk), rt=0.5)
        NEW = [("eval design", -4.6, "eval"), ("judge–human agreement", -0.85, "agreement"), ("multi-model judging", 3.95, "multi-model")]
        news = []
        for txt, x, w in NEW:
            on(self, w)
            t = T(txt, 36).move_to([x, 1.85, 0])
            news.append(t)
            P(self, FadeIn(t), rt=0.4)
        on(self, "Already")
        tl = Line([-5.8, -0.35, 0], [5.9, -0.35, 0], color=INK, stroke_width=8)
        am = left(T("already mine:", 36, bold=True).move_to([0, 0.95, 0]), -6.0)
        P(self, Create(tl), FadeIn(am, shift=RIGHT * 0.3), rt=0.7)
        on(self, "requirements")
        prd = doc_icon(-2.75, 1.06, w=0.55, h=0.6, fill=KRAFT2)
        P(self, FadeIn(prd, shift=UP * 0.3), rt=0.4)
        ROLES = [("LG Energy Solution Vertech", -5.0, "L"), ("Tech4Dev", -3.3, "Tech"), ("KoineArth", -1.8, "Koine")]
        rl = VGroup(T("LG Energy Solution Vertech", 32), T("·", 32), T("Tech4Dev", 32), T("·", 32), T("KoineArth", 32)).arrange(RIGHT, buff=0.15)
        rl.move_to([0, 0.42, 0]).align_to([-6.0, 0, 0], LEFT)
        parts = [VGroup(rl[0]), VGroup(rl[1], rl[2]), VGroup(rl[3], rl[4])]
        for (txt, x, w), part in zip(ROLES, parts):
            on(self, w)
            chip = RoundedRectangle(width=1.25, height=0.75, corner_radius=0.1, stroke_width=0, fill_color=KRAFT,
                                    fill_opacity=1).move_to([x, -0.35, 0])
            P(self, FadeIn(chip, scale=0.4), FadeIn(part), rt=0.4)
        on(self, "internal")
        it = left(T("internal — not shown", 34).move_to([0, -1.05, 0]), -6.0)
        P(self, FadeIn(it, shift=UP * 0.2), rl.animate.set_opacity(0.45), rt=0.5)
        on(self, "course")
        seg = Line([0.2, -0.35, 0], [3.9, -0.35, 0], color=INK, stroke_width=18)
        roles = VGroup(am, prd, rl, it)
        roles.save_state()
        P(self, Create(seg), roles.animate.set_opacity(0.35), rt=0.5)
        on(self, "film")
        f8 = card(1.0, -0.35, 1.1, 0.8, stroke=INK, sw=4, fill=KRAFT2)
        t8 = T("PR #8 · open", 34).move_to([1.0, -1.1, 0])
        P(self, FadeIn(f8, scale=0.4), FadeIn(t8), rt=0.4)
        on(self, "verified")
        P(self, Create(check(1.02, -0.32, s=0.24, w=9)), Indicate(VGroup(f8, t8), color=INK, scale_factor=1.08), rt=0.5)
        on(self, "recipe")
        f23 = card(3.2, -0.35, 1.1, 0.8, stroke=INK, sw=4, fill=KRAFT2)
        t23 = T("PR #23 · open · DRAFT", 34).move_to([3.2, -1.7, 0])
        P(self, FadeIn(f23, scale=0.4), FadeIn(t23), rt=0.4)
        on(self, "to-do")
        P(self, Indicate(VGroup(f23, t23), color=INK, scale_factor=1.08), rt=0.5)
        on(self, "think")
        rb = Rubric(5.3, -0.35, w=0.55, h=0.72, labels=False)
        rbg = RoundedRectangle(width=0.95, height=1.05, corner_radius=0.1, stroke_color=PLAN, stroke_width=6,
                               fill_color=GHOST, fill_opacity=1).move_to([5.3, -0.35, 0])
        rbl = T("Readback", 34, bold=True).move_to([5.2, -1.1, 0])
        P(self, FadeIn(rbg, scale=0.5), FadeIn(rb.group(), scale=0.5), FadeIn(rbl), rt=0.5)
        on(self, "core")
        course = VGroup(f8, t8, f23, t23, seg)
        course.save_state()
        P(self, course.animate.set_opacity(0.35), *[Indicate(t, color=INK, scale_factor=1.05) for t in news], rt=0.6)
        on(self, "eval", nth=2)
        lk = Arrow([5.9, 1.27, 0], [5.45, 0.25, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.25)
        P(self, Indicate(brk, color=INK, scale_factor=1.02), GrowArrow(lk), rt=0.7)
        P(self, Restore(roles), Restore(course), rt=0.6)
        finish(self)


# ═════════════════════════════ B08 — exists today vs will exist ═════════════════════════════
class B08_ExistsWill(Scene):
    def construct(self):
        frame = VGroup(rail(None), tag("real output · Claude Opus 5.5 · 14 Oct 2026 · grey = will"))
        self.add(frame)
        on(self, "exists")
        div = Line([0.25, 2.0, 0], [0.25, -2.6, 0], color=BAR2, stroke_width=4)
        eh = left(T("exists · 14 Oct 2026", 40, bold=True).move_to([0, 2.55, 0]), -6.0)
        exbg = RoundedRectangle(width=6.3, height=4.6, corner_radius=0.15, stroke_width=0, fill_color=KRAFT2,
                                fill_opacity=0.35).move_to([-2.9, -0.3, 0])
        P(self, FadeIn(exbg, shift=RIGHT * 1.5), Create(div), FadeIn(eh, shift=RIGHT * 1.0), rt=0.6)
        on(self, "ten")
        amis = VGroup(*[card(-5.55 + i * 0.07, 1.5 - i * 0.04, 0.6, 0.72, stroke=BAR1, sw=2, fill=KRAFT) for i in range(10)])
        al = left(T("AMI sample · 10 meetings", 32).move_to([0, 1.45, 0]), -4.45)
        P(self, LaggedStart(*[FadeIn(a, shift=RIGHT * 0.3) for a in amis], lag_ratio=0.05), FadeIn(al), rt=0.6)
        on(self, "constructed")
        rb = Rubric(-5.35, 0.42, w=0.6, h=0.72, labels=False)
        cl = left(T("constructed docs (3)", 34).move_to([0, 0.5, 0]), -4.5)
        P(self, FadeIn(rb.group(), shift=RIGHT * 0.3), FadeIn(cl), rt=0.5)
        on(self, "recap")
        ex = card(-2.95, -0.7, 6.0, 1.15, stroke=BAR1, sw=4, fill=KRAFT)
        ext = T("“Include a lock function …”", 36).move_to([-2.95, -0.47, 0])
        P(self, FadeIn(ex, shift=UP * 0.4), FadeIn(ext, shift=UP * 0.4), rt=0.6)
        on(self, "Claude")
        ml = T("ES2007a recap · Claude Opus 5.5", 32).move_to([-2.95, -1.0, 0])
        P(self, FadeIn(ml), Indicate(ex, color=INK, scale_factor=1.04), rt=0.5)
        on(self, "Ten")
        dots = VGroup(*[Dot([-5.75 + i * 0.3, -1.75, 0], radius=0.12, color=INK) for i in range(10)])
        dl = left(T("10 real outputs", 34).move_to([0, -1.75, 0]), -2.65)
        bl = left(T("brief · log", 34).move_to([0, -2.35, 0]), -5.85)
        P(self, LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.08), FadeIn(dl), FadeIn(bl), rt=0.6)
        on(self, "will")
        wh = left(T("will exist", 40, bold=True).move_to([0, 2.55, 0]), 0.7)
        wbg = RoundedRectangle(width=5.6, height=4.6, corner_radius=0.15, stroke_color=PLAN, stroke_width=6,
                               fill_color=GHOST, fill_opacity=0.5).move_to([3.3, -0.3, 0])
        P(self, FadeIn(wbg, shift=LEFT * 1.5), FadeIn(wh, shift=LEFT * 1.0), rt=0.5)
        WILL = [("my labels", 1.4, "labels"), ("judge runs", 0.55, "judges"), ("agreement table", -0.3, "agreement")]
        for txt, y, w in WILL:
            on(self, w)
            bx = plan_box(1.15, y, 0.62, 0.62, fill=True)
            lb = left(T(txt, 34).move_to([0, y, 0]), 1.65)
            P(self, Create(bx), FadeIn(lb, shift=LEFT * 0.4), rt=0.4)
        on(self, "numbers")
        hb = plan_box(1.15, -1.15, 0.62, 0.62, fill=True)
        hl = left(T("held-out result: —", 34).move_to([0, -1.15, 0]), 1.65)
        P(self, Create(hb), FadeIn(hl, shift=LEFT * 0.4), rt=0.4)
        on(self, "measured")
        cb = plan_box(1.15, -2.0, 0.62, 0.62, fill=True)
        cll = left(T("CLI · later modules", 34).move_to([0, -2.0, 0]), 1.65)
        P(self, Create(cb), FadeIn(cll, shift=LEFT * 0.4), rt=0.4)
        # match-cut to the outro: everything recedes, the rubric page comes to the centre
        keep = set(rb.group()) | {frame}
        rest = Group(*[m for m in self.mobjects if m not in keep])
        P(self, FadeOut(rest), rt=0.4)
        P(self, rb.group().animate.scale(2.4).move_to([0, 0.4, 0]), rt=0.5)
        finish(self)
