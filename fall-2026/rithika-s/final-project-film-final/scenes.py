"""
scenes.py — agentic-retrieval-lab-final ("Agentic Retrieval Lab", final film), show-tell.

One drawn Manim scene per beat, paced by the measured af_bella narration (beat_sheet.json +
word_times.json, via at()/until()/done()). The drawing kit and cartoon cast are pasted below
verbatim from the October reel (see cast_october.py), as the skill requires (Gate A copies
only this file). Rules for this film: real readable text only (scribble()/iso.page are not
used), key terms labelled when spoken, characters exit when their line ends, numbers on
screen exactly as in FILM-BRIEF.md. No instructor portrait, likeness or name.
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


# ═════════════════════════════ WRITING KIT (quill, ink, paper, scribble) ═════════════════════════════
# Added 2026-10-07 from the toolkit author's two reference drawings: a quill drawing a branching outline on a
# scroll, and three scattered pages of scribbled handwriting with a quill. Use when a beat is
# about writing, drafting, authorship, notes, a manuscript, a log, a letter, a signature.
# Terracotta here is only the ink drop and the outline's nodes (dots) — never the lines.


def quill(x, y, s=1.0, angle=0.0, color=INK, fill=BOX_TOP):
    """A drawn quill with its NIB at (x, y); the feather points up-right. `g.nib` is the nib point.
    Kraft-filled feather, ink outline, a shaft line and one barb. Rotate with `angle` (radians)."""
    o = np.array([x, y, 0.0])
    def P(u, v):  # icon units (0..1) → scene, nib at origin, tip at (1, 1.1)·s
        return o + np.array([u * s, v * s, 0.0])
    body = VMobject(fill_color=fill, fill_opacity=1, stroke_color=color, stroke_width=4)
    body.set_points_smoothly([P(0.00, 0.00), P(0.12, 0.62), P(0.55, 1.02), P(1.00, 1.10),
                              P(0.95, 0.68), P(0.62, 0.22), P(0.00, 0.00)])
    shaft = Line(P(0.02, 0.02), P(0.98, 1.06), color=color, stroke_width=3)
    barb = Line(P(0.46, 0.50), P(0.40, 0.72), color=color, stroke_width=2.5)
    g = VGroup(body, shaft, barb)
    if angle:
        g.rotate(angle, about_point=o)
    g.nib = o.copy()
    return g


def inkwell(iso, x0=0.0, y0=0.0, z0=0.0, s=0.7):
    """A dark ink bottle (iso box + narrow neck) with one terracotta ink dot on the lid."""
    body = iso.box(x0, y0, z0, s, s, s * 0.9, DARK_TOP, DARK_L, DARK_R)
    neck = iso.box(x0 + s * 0.3, y0 + s * 0.3, z0 + s * 0.9, s * 0.4, s * 0.4, s * 0.25, DARK_TOP, DARK_L, DARK_R)
    drop = Dot(iso.p(x0 + s * 0.5, y0 + s * 0.5, z0 + s * 1.15), radius=0.07, color=TERRA)
    return VGroup(body, neck, drop)


def paper(x, y, w=2.4, h=3.0, tilt=0.0, fill=PAGE_TOP):
    """A flat 2-D sheet (the scattered-pages drawing): white page, ink outline, kraft drop shadow.
    `tilt` in radians. Returns a VGroup; `.sheet` is the page rectangle for placing lines on it."""
    shadow = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
    sheet = Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    g = VGroup(shadow, sheet)
    if tilt:
        g.rotate(tilt, about_point=[x, y, 0])
    g.sheet = sheet
    g.cx, g.cy, g.w, g.h, g.tilt = float(x), float(y), float(w), float(h), float(tilt)   # read these; never ask the stub for vertices
    return g


def scribble(x, y, w, amp=0.07, waves=None, color=INK, sw=4):
    """One wavy handwriting line from (x, y) rightwards for `w` units. Reads as script, never as type."""
    n = waves or max(3, int(round(w * 3)))
    pts = []
    for i in range(n * 4 + 1):
        t = i / (n * 4)
        pts.append([x + w * t, y + amp * np.sin(t * n * 2 * np.pi) * (0.6 + 0.4 * np.cos(t * 5.3)), 0])
    m = VMobject(stroke_color=color, stroke_width=sw)
    m.set_points_smoothly(pts)
    return m


def scribble_block(x, y, w, n=3, gap=0.34, last=0.62, color=INK, sw=4):
    """`n` scribble lines stacked downward from (x, y); the last one is `last`× as long (a paragraph end)."""
    return VGroup(*[scribble(x, y - i * gap, w * (last if i == n - 1 else 1.0), color=color, sw=sw) for i in range(n)])


def scribbles_on(page, n=3, inset=0.3, gap=0.34, color=INK, sw=4):
    """Scribble lines laid on a `paper()` group, following its tilt (uses the page's stored geometry)."""
    w = page.w - 2 * inset
    g = scribble_block(page.cx - w / 2, page.cy + page.h / 2 - inset - 0.1, w, n=n, gap=gap, color=color, sw=sw)
    if abs(page.tilt) > 1e-3:
        g.rotate(page.tilt, about_point=[page.cx, page.cy, 0])
    return g


def outline_tree(x, y, h=1.6, levels=2, spread=0.55, color=INK, node=TERRA):
    """A branching outline (the scroll drawing): a trunk rising from (x, y), forking `levels` times,
    a terracotta dot at every tip. Returns VGroup(lines, dots) — draw lines first, dots last."""
    lines, dots = VGroup(), VGroup()
    def grow(px, py, length, lvl, dx):
        qx, qy = px + dx, py + length
        lines.add(Line([px, py, 0], [qx, qy, 0], color=color, stroke_width=4))
        if lvl == 0:
            dots.add(Dot([qx, qy, 0], radius=0.075, color=node))
            return
        for d in (-spread, spread):
            grow(qx, qy, length * 0.62, lvl - 1, d * (0.75 ** (levels - lvl)))
    grow(x, y, h * 0.42, levels, 0.0)
    g = VGroup(lines, dots)
    g.lines, g.dots = lines, dots
    return g


def write_lines(self, q, lines, speed=1.6, hop=0.22, dip=0.06):
    """Animate the quill `q` WRITING each line in `lines`: the nib hops to the line's start, then the
    line draws while the nib rides its tip (the writing motion). `speed` is scene units per second.
    Call between `until()` phrases so each line lands on its words. Works with the midpoint guard."""
    for ln in lines:
        start = np.array(ln.get_start(), dtype=float)
        self.play(q.animate.shift(start - q.nib), run_time=hop, rate_func=smooth)
        q.nib = start.copy()
        off = np.array(q.get_center(), dtype=float) - q.nib
        def ride(m, a, ln=ln, off=off):
            m.move_to(np.array(ln.point_from_proportion(min(1.0, a)), dtype=float) + off)
        try:
            length = float(ln.get_arc_length())
        except Exception:          # Gate A's stub has no arc length; any positive number keeps the check moving
            length = 2.0
        rt = max(0.35, length / speed)
        self.play(Create(ln), UpdateFromAlphaFunc(q, ride), run_time=rt, rate_func=linear)
        q.nib = np.array(ln.get_end(), dtype=float)
        # the small lift between lines keeps the quill from fusing with the ink at GATE T's midpoint
        q.shift([0, dip, 0]); q.nib = q.nib + np.array([0, dip, 0])


def grow_tree(self, q, tree, per=0.45):
    """Animate the quill drawing an `outline_tree`: each segment draws as the nib rides it; dots land last."""
    for ln in tree.lines:
        start = np.array(ln.get_start(), dtype=float)
        self.play(q.animate.shift(start - q.nib), run_time=0.18, rate_func=smooth)
        q.nib = start.copy()
        off = np.array(q.get_center(), dtype=float) - q.nib
        def ride(m, a, ln=ln, off=off):
            m.move_to(np.array(ln.point_from_proportion(min(1.0, a)), dtype=float) + off)
        self.play(Create(ln), UpdateFromAlphaFunc(q, ride), run_time=per, rate_func=linear)
        q.nib = np.array(ln.get_end(), dtype=float)
    self.play(LaggedStart(*[GrowFromCenter(d) for d in tree.dots], lag_ratio=0.15), run_time=0.6)

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


# ═════════════════════════════ FILM CAST (Agentic Retrieval Lab) — redesign v2 ═════════════════════════════
# One cast for the whole film (show-tell law 4):
#   the LIBRARY (bookcases) · KEYWORD LIBRARIAN = BM25 (cart + magnifying glass)
#   MEANING LIBRARIAN = embedding (cart + lightbulb) · the ROBOT (the AI agent)
#   the ANSWER KEY (clipboard) · DECOY BOOKS (grey) · THE PILE (top 100)
#   the RIGHT BOOK is always white with one terracotta dot.
# v2 rules (Rithika, 2026-10-11): real words only (no squiggles), phone-readable ink labels
# (key terms larger), drawings fill title-safe, key terms pop in on the whisper word timestamps
# (word_times.json), every icon labelled, CONSTRUCTED on invented examples, source tags on real data.
# Cartoon people (Rithika's authorisation, 2026-10-11): see CARTOON CAST below.
import random as _rnd

SPINES = [BOX_TOP, PAGE_TOP, BOX_L, GHOST, BOX_R, PAGE_L]
DECOY_TOP, DECOY_L, DECOY_R = "#C9C6C0", "#A9A6A0", "#8F8C86"
KRAFT_DEEP = "#9C8462"
KEY, SEC, TAG = 50, 40, 32          # key-term labels, secondary labels, source tags (type floor is 32)

try:
    _WT = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "word_times.json")))["words"]
except Exception:
    _WT = {}


def bid_of(self):
    return type(self).__name__.split("_")[0]


def _norm(w):
    return "".join(ch for ch in str(w).lower() if ch.isalnum() or ch == "%")


def word_t(bid, phrase, nth=1):
    """Start time (s) of `phrase` in the beat's whisper word timestamps, or None."""
    toks = [t for t in (_norm(x) for x in phrase.split()) if t]
    ws = _WT.get(bid, [])
    seq = [_norm(w[0]) for w in ws]
    hits = 0
    for i in range(len(seq) - len(toks) + 1):
        if seq[i:i + len(toks)] == toks:
            hits += 1
            if hits == nth:
                return float(ws[i][1])
    return None


def at(self, phrase, lead=0.12, nth=1):
    """Wait until `phrase` is spoken (whisper word time). Falls back to until() — the Gate A
    sandbox has only scenes.py, so word_times.json is absent there."""
    t = word_t(bid_of(self), phrase, nth)
    if t is None:
        until(self, phrase)
        return
    gap = t - lead - _elapsed(self)
    if gap > 0.04:
        self.wait(gap)


def P(self, *anims, rt=0.5, **kw):
    """play() with the MIDPOINT GUARD: nothing moves within ±0.25 s of the clip midpoint (GATE T and
    Gate V sample there). An animation that would cross it waits; the delay is logged as [guard]."""
    tgt = _TARGET.get(bid_of(self), 0)
    s = _elapsed(self)
    if tgt:
        m = tgt / 2
        if s < m + 0.25 and s + rt > m - 0.25:
            print(f"[guard] {bid_of(self)} cue at {s:.2f}s held {m + 0.25 - s:.2f}s past the midpoint")
            self.wait(m + 0.25 - s)
    self.play(*anims, run_time=rt, rate_func=kw.pop("rate_func", smooth), **kw)


def pop(self, *mobs, rt=0.45):
    """KEYWORD POP-IN: a gentle scale-in (same easing everywhere)."""
    P(self, *[FadeIn(m, scale=0.7) for m in mobs], rt=rt)


def _fam(mob):
    return list(mob.get_family())


def fade_to(mob, a):
    """Animate a whole group's opacity to `a` × its original (1 = restore). Keeps zero-fill strokes at zero fill."""
    try:
        orig = getattr(mob, "_op0", None)
        if orig is None:
            orig = [(m, float(m.get_fill_opacity()), float(m.get_stroke_opacity())) for m in _fam(mob)]
            mob._op0 = orig
        cur = [(float(m.get_fill_opacity()), float(m.get_stroke_opacity())) for m, _, _ in orig]

        def upd(_, t):
            for (m, f0, s0), (fc, sc) in zip(orig, cur):
                m.set_fill(opacity=fc + (f0 * a - fc) * t, family=False)
                m.set_stroke(opacity=sc + (s0 * a - sc) * t, family=False)
        return UpdateFromAlphaFunc(mob, upd)
    except Exception:                       # Gate A's stub has no opacity model
        return mob.animate.set_opacity(a)


def dim(mob):
    return fade_to(mob, 0.35)


def undim(mob):
    return fade_to(mob, 1.0)


def slide_in(mob, side=LEFT, d=1.0):
    """Characters and big props enter by sliding (never popping)."""
    return FadeIn(mob, shift=-side * d)


def slide_out(mob, side=LEFT, d=1.0):
    return FadeOut(mob, shift=side * d)


def done(self):
    """Hold to the end of the beat's audio, never past it."""
    tgt = _TARGET.get(bid_of(self), 0)
    rem = tgt - _elapsed(self) - 0.06
    if not tgt:
        self.wait(1.0)
    elif rem > 0.05:
        self.wait(rem)


def key(s, x, y, size=KEY):
    return T(s, size, INK, bold=True).move_to([x, y, 0])


def lab(s, x, y, size=SEC, bold=False):
    return T(s, size, INK, bold=bold).move_to([x, y, 0])


TAG_INK = "#5E594E"     # source tags: a lighter ink that still clears 4.5:1 contrast on the stage


def tag(s, x, y, color=TAG_INK):
    return T(s, TAG, color).move_to([x, y, 0])


ROBOT_S = 1.1           # the robot is the same size in every beat


def tag_constructed(x=4.9, y=3.15):
    return T("CONSTRUCTED", TAG, bold=True).move_to([x, y, 0])


def chip(s, x, y, size=44, bold=True):
    """A title chip: ink words on a white pill with a kraft edge."""
    t = T(s, size, INK, bold=bold)
    r = RoundedRectangle(width=t.width + 0.55, height=t.height + 0.36, corner_radius=0.2, fill_color=PAGE_TOP, fill_opacity=1,
                         stroke_color=KRAFT_DEEP, stroke_width=3)
    g = VGroup(r, t).move_to([x, y, 0])
    return g


def card(s, x, y, size=36, w=None, bold=False):
    """A paper card carrying real words."""
    t = T(s, size, INK, bold=bold)
    r = RoundedRectangle(width=(w or t.width + 0.5), height=t.height + 0.34, corner_radius=0.1, fill_color=PAGE_TOP, fill_opacity=1,
                         stroke_color=BAR1, stroke_width=3)
    return VGroup(r, t).move_to([x, y, 0])


def say(left_x, y, s, size=36):
    """A speech bubble with real words, left edge at left_x, tail pointing left (to the speaker)."""
    t = T(s, size, INK)
    w, h = t.width + 0.6, t.height + 0.42
    body = RoundedRectangle(width=w, height=h, corner_radius=0.22, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4)
    body.move_to([left_x + w / 2, y, 0])
    t.move_to(body.get_center())
    tail = Polygon([left_x + 0.06, y + 0.14, 0], [left_x + 0.06, y - 0.14, 0], [left_x - 0.32, y - 0.06, 0],
                   fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(tail, body, t)


def xmark(x, y, s=0.28, w=9):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def bookcase(iso, x0, y0, w=2.6, d=0.8, h=2.7, shelves=3, seed=0, glow=None):
    r = _rnd.Random(seed)
    case = iso.box(x0, y0, 0, w, d, h)
    planks, books = VGroup(), VGroup()
    g = VGroup(case, planks, books)
    g.glow = None
    step = (h - 0.25) / shelves
    for k in range(shelves):
        z0 = 0.12 + k * step
        planks.add(Line(iso.p(x0, y0, z0), iso.p(x0 + w, y0, z0), color=INK, stroke_width=3))
        a, slot = x0 + 0.14, 0
        while a < x0 + w - 0.3:
            bw = r.uniform(0.16, 0.26)
            bh = r.uniform(0.62, 0.92) * (step - 0.12)
            is_glow = glow is not None and glow == (k, slot)
            fill = PAGE_TOP if is_glow else r.choice(SPINES)
            bk = iso.quad([(a, y0, z0), (a + bw, y0, z0), (a + bw, y0, z0 + bh), (a, y0, z0 + bh)], fill, sw=2)
            books.add(bk)
            if is_glow:
                dot = Dot(iso.p(a + bw / 2, y0, z0 + bh * 0.78), radius=0.07, color=TERRA)
                books.add(dot)
                g.glow = VGroup(bk, dot)
            a += bw + 0.07
            slot += 1
    return g


def library(ox, oy, s=0.6, n=3, seed=1, glow=None, gap=1.5):
    iso = Iso(ox, oy, s)
    cases = [bookcase(iso, 0, i * gap, seed=seed + i, glow=glow if i == 0 else None) for i in range(n)]
    g = VGroup(*reversed(cases))
    g.cases = cases
    g.glow = cases[0].glow
    return g


def cart(ox, oy, s=1.0, tool=None, books=True):
    """A LIBRARIAN: kraft book cart on dark wheels; tool = 'glass' (BM25) or 'bulb' (embedding)."""
    iso = Iso(ox, oy, s)
    wheels = VGroup(*[Circle(radius=0.17 * s, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3)
                      .move_to(iso.p(fx, 0, 0.17)) for fx in (0.35, 1.45)])
    body = iso.box(0, 0, 0.3, 1.8, 1.0, 0.75)
    g = VGroup(wheels, body)
    if books:
        for i, (fill, hgt) in enumerate([(BOX_TOP, 0.55), (PAGE_TOP, 0.48), (BOX_TOP, 0.42)]):
            g.add(iso.box(0.18 + i * 0.4, 0.3, 1.05, 0.26, 0.5, hgt, fill, PAGE_L if fill == PAGE_TOP else BOX_L, BOX_R, sw=2))
    base = iso.p(1.6, 0.55, 1.05)
    tip = base + UP * 1.25 * s
    g.tool = None
    if tool:
        g.add(Line(base, tip, color=INK, stroke_width=5))
    if tool == "glass":
        lens = Circle(radius=0.36 * s, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=7).move_to(tip + UP * 0.34 * s)
        g.tool = VGroup(lens)
        g.add(g.tool)
    elif tool == "bulb":
        sock = Rectangle(width=0.3 * s, height=0.2 * s, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(tip + UP * 0.1 * s)
        glass = Circle(radius=0.34 * s, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to(tip + UP * 0.5 * s)
        g.tool = VGroup(sock, glass)
        g.add(g.tool)
    g.tool_center = tip + UP * (0.34 if tool == "glass" else 0.5) * s
    g.top = iso.p(0.9, 0.5, 1.6)
    return g


def light_bulb(c, s=1.0):
    return VGroup(Circle(radius=0.62 * s, stroke_color=GHOST, stroke_width=12).move_to(c), Dot(c, radius=0.09 * s, color=TERRA))


def robot(x, y, s=1.0):
    """The ROBOT (the AI agent)."""
    iso = Iso(x, y, s)
    wheels = VGroup(*[Circle(radius=0.15 * s, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3)
                      .move_to(iso.p(fx, -0.4, 0.15)) for fx in (-0.3, 0.35)])
    body = iso.box(-0.5, -0.4, 0.25, 1.0, 0.8, 0.85)
    head = iso.box(-0.42, -0.32, 1.15, 0.84, 0.64, 0.55, DARK_TOP, DARK_L, DARK_R)
    eyes = VGroup(Dot(iso.p(-0.15, -0.32, 1.45), radius=0.07 * s, color=TERRA), Dot(iso.p(0.22, -0.32, 1.45), radius=0.07 * s, color=TERRA))
    ant = VGroup(Line(iso.p(0, 0, 1.7), iso.p(0, 0, 2.05), color=INK, stroke_width=4), Dot(iso.p(0, 0, 2.08), radius=0.07 * s, color=INK))
    g = VGroup(wheels, body, head, eyes, ant)
    g.hand = iso.p(0.5, -0.4, 0.75)
    return g


def pile(iso, x0, y0, z0, n=8):
    cols = [(BOX_TOP, BOX_L, BOX_R), (PAGE_TOP, PAGE_L, PAGE_R), (DECOY_TOP, DECOY_L, DECOY_R), (BOX_TOP, BOX_L, BOX_R)]
    return VGroup(*[iso.box(x0 + ((i % 3) - 1) * 0.07, y0 + (i % 2) * 0.06, z0 + i * 0.17, 1.3, 0.85, 0.15, *cols[i % 4], sw=2)
                    for i in range(n)])


def flat_book(x, y, w=0.55, h=0.75, right=False, decoy=False):
    """A 2-D book face: white (right book has a terracotta dot), kraft, or grey decoy."""
    fill = DECOY_L if decoy else (PAGE_TOP if right else BOX_TOP)
    body = RoundedRectangle(width=w, height=h, corner_radius=0.05, fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    spine = Line([x - w / 2 + 0.1, y - h / 2 + 0.04, 0], [x - w / 2 + 0.1, y + h / 2 - 0.04, 0], color=INK, stroke_width=3)
    g = VGroup(body, spine)
    if right:
        g.add(Dot([x + 0.05, y + h / 2 - 0.16, 0], radius=0.07, color=TERRA))
    return g


def file_icon(x, y, w=1.0, h=1.25):
    body = Polygon([x - w / 2, y - h / 2, 0], [x + w / 2, y - h / 2, 0], [x + w / 2, y + h / 2 - 0.3, 0], [x + w / 2 - 0.3, y + h / 2, 0], [x - w / 2, y + h / 2, 0],
                   fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    fold = Polygon([x + w / 2 - 0.3, y + h / 2, 0], [x + w / 2 - 0.3, y + h / 2 - 0.3, 0], [x + w / 2, y + h / 2 - 0.3, 0],
                   fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=3)
    braces = T("{ }", 40, INK, bold=True).move_to([x, y - 0.1, 0])
    return VGroup(body, fold, braces)


def folder(x, y, w=2.2, h=1.5):
    tab = RoundedRectangle(width=w * 0.42, height=0.4, corner_radius=0.08, fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x - w * 0.27, y + h / 2 + 0.1, 0])
    body = RoundedRectangle(width=w, height=h, corner_radius=0.1, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    return VGroup(tab, body, Dot([x + w / 2 - 0.3, y + h / 2 - 0.28, 0], radius=0.08, color=TERRA))


def laptop(x, y, s=1.0):
    iso = Iso(x, y, s)
    base = iso.box(-1.3, -0.9, 0, 2.6, 1.8, 0.12)
    screen = iso.quad([(-1.3, 0.9, 0.12), (1.3, 0.9, 0.12), (1.3, 0.9, 1.9), (-1.3, 0.9, 1.9)], DARK_L)
    pane = iso.quad([(-1.15, 0.9, 0.27), (1.15, 0.9, 0.27), (1.15, 0.9, 1.75), (-1.15, 0.9, 1.75)], CARD, sw=2)
    g = VGroup(base, screen, pane)
    g.iso = iso
    return g


def bm25_chart():
    """B06A's finished chart (B06B opens on it, so the '?' can land on the 42% bar)."""
    vals = [(64, "human"), (60, "main rewrite"), (42, "support")]
    xs = [-4.0, -0.2, 3.6]
    floor = RoundedRectangle(width=11.6, height=0.32, corner_radius=0.06, fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-0.2, -1.45, 0])
    bars, nums, caps = [], [], []
    for (v, nm), x in zip(vals, xs):
        iso = Iso(x, -1.35, 1.25)
        h = v / 100 * 3.0
        bars.append(iso.box(-0.45, -0.45, 0, 0.9, 0.9, h, BAR3, BAR2, BAR1))
        nums.append(T(f"{v}%", 60, INK, bold=True).move_to([x, -1.35 + 0.56 + 1.25 * h + 0.6, 0]))
        caps.append(lab(nm, x, -2.35, size=44))
    title = key("BM25: right passage in top 100", 0, -3.1, size=42)
    src = tag("source: results/foundation/2026-10-08_bm25/pool_stats.json", 0, 3.05)
    return floor, bars, nums, caps, title, src




# ═════════════════════════════ CARTOON CAST (Rithika, 2026-10-11) ═════════════════════════════
# Rithika authorised generic cartoon people for this film; the toolkit's portrait house rule does not
# apply and no instructor portrait, likeness or name is used. Flat figures from Manim shapes, 4 px ink
# outlines, palette colours only (skin = kraft BOX_L for everyone). Each character is one builder, so it
# looks identical in every beat. Builders return a VGroup with .hand_r / .hand_l / .head_c and, for the
# librarians, .tool and .tool_center (the magnifier or bulb, animatable on its own).
SKIN = BOX_L


def _arm(shoulder, length, w, deg, fill):
    a = np.radians(deg)
    d = np.array([np.sin(a), -np.cos(a), 0.0])
    arm = RoundedRectangle(width=w, height=length, corner_radius=w / 2, fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=4)
    arm.move_to(np.array(shoulder) + d * length / 2).rotate(a, about_point=np.array(shoulder) + d * length / 2)
    hand = np.array(shoulder) + d * length
    return arm, hand


def _cap(c, r, color, a0=10, a1=170, brow=0.3):
    pts = [np.array(c) + r * 1.04 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]) for a in np.linspace(a0, a1, 14)]
    pts += [np.array(c) + np.array([-r * 0.92, r * brow, 0]), np.array(c) + np.array([r * 0.92, r * brow, 0])]
    return Polygon(*pts, fill_color=color, fill_opacity=1, stroke_color=INK, stroke_width=4)


def person(x, y0, h, top, bottom, hair="short", hair_color=DARK_L, wf=1.0, arm_r=0, arm_l=0, eyes="open",
           glasses=False, bowtie=False, beard=False, buttons=False, mouth=True):
    u = h / 6.0
    g = VGroup()
    for sx in (-1, 1):                                                         # legs + shoes
        g.add(RoundedRectangle(width=0.55 * u, height=2.2 * u, corner_radius=0.12 * u, fill_color=bottom, fill_opacity=1,
                               stroke_color=INK, stroke_width=4).move_to([x + sx * 0.33 * u * wf, y0 + 1.15 * u, 0]))
        g.add(RoundedRectangle(width=0.78 * u, height=0.48 * u, corner_radius=0.16 * u, fill_color=DARK_L, fill_opacity=1,
                               stroke_color=INK, stroke_width=3).move_to([x + sx * 0.4 * u * wf, y0 + 0.24 * u, 0]))   # tall enough that GATE T never reads a (dimmed) shoe as sub-floor text
    head_c = np.array([x, y0 + 5.1 * u, 0])
    r = 0.72 * u
    if hair == "long":                                                         # long hair falls behind the shoulders
        g.add(RoundedRectangle(width=3.0 * r, height=4.2 * r, corner_radius=1.0 * r, fill_color=hair_color, fill_opacity=1,
                               stroke_color=INK, stroke_width=4).move_to(head_c + DOWN * 1.15 * r))
    torso = RoundedRectangle(width=1.7 * u * wf, height=2.4 * u, corner_radius=0.35 * u, fill_color=top, fill_opacity=1,
                             stroke_color=INK, stroke_width=4).move_to([x, y0 + 3.3 * u, 0])
    sh_r = np.array([x + 0.72 * u * wf, y0 + 4.2 * u, 0])
    sh_l = np.array([x - 0.72 * u * wf, y0 + 4.2 * u, 0])
    ar, hand_r = _arm(sh_r, 2.0 * u, 0.48 * u, arm_r, top)
    al, hand_l = _arm(sh_l, 2.0 * u, 0.48 * u, -arm_l, top)
    g.add(al, torso, ar)
    if buttons:
        g.add(Line([x, y0 + 4.4 * u, 0], [x, y0 + 2.2 * u, 0], color=INK, stroke_width=3),
              *[Dot([x + 0.18 * u, y0 + (3.9 - k * 0.6) * u, 0], radius=0.06 * u + 0.01, color=INK) for k in range(3)])
    g.add(*[Circle(radius=0.2 * u, fill_color=SKIN, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(p) for p in (hand_r, hand_l)])
    g.add(Rectangle(width=0.4 * u, height=0.3 * u, fill_color=SKIN, fill_opacity=1, stroke_width=0).move_to([x, y0 + 4.5 * u, 0]))  # neck
    if hair == "long":                                                         # front locks fall over the shoulders
        g.add(*[RoundedRectangle(width=0.5 * r, height=2.3 * r, corner_radius=0.24 * r, fill_color=hair_color, fill_opacity=1,
                                 stroke_color=INK, stroke_width=4).move_to(head_c + np.array([sx * 0.88 * r, -1.0 * r, 0])) for sx in (-1, 1)])
    g.add(Circle(radius=r, fill_color=SKIN, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to(head_c))
    if hair in ("long", "short"):
        g.add(_cap(head_c, r, hair_color, brow=0.35 if hair == "long" else 0.45))
    elif hair == "sides":                                                      # bald on top, grey tufts at the sides
        g.add(*[Ellipse(width=0.42 * r, height=0.7 * r, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=3)
                .move_to(head_c + np.array([sx * 0.98 * r, 0.15 * r, 0])) for sx in (-1, 1)])
    elif hair == "white":
        g.add(_cap(head_c, r, PAGE_TOP, brow=0.5))
    elif hair == "messy":
        pts = [head_c + r * 1.05 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]) * (1.18 if i % 2 else 1.0) for i, a in enumerate(np.linspace(5, 175, 11))]
        pts += [head_c + np.array([-r * 0.95, r * 0.35, 0]), head_c + np.array([r * 0.95, r * 0.35, 0])]
        g.add(Polygon(*pts, fill_color=hair_color, fill_opacity=1, stroke_color=INK, stroke_width=4))
    ey = head_c[1] + 0.02 * r
    for sx in (-1, 1):
        ex = head_c[0] + sx * 0.36 * r
        if eyes == "sleepy":
            g.add(Line([ex - 0.16 * r, ey, 0], [ex + 0.16 * r, ey, 0], color=INK, stroke_width=4))
        else:
            g.add(Dot([ex, ey, 0], radius=0.09 * r + 0.012, color=INK))
        if glasses:
            g.add(Circle(radius=0.24 * r, stroke_color=INK, stroke_width=3).move_to([ex, ey, 0]))
    if glasses:
        g.add(Line([head_c[0] - 0.12 * r, ey, 0], [head_c[0] + 0.12 * r, ey, 0], color=INK, stroke_width=3))
    if beard:
        bp = [head_c + r * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]) for a in np.linspace(195, 345, 10)]
        bp += [head_c + np.array([0.45 * r, -1.35 * r, 0]), head_c + np.array([0, -1.6 * r, 0]), head_c + np.array([-0.45 * r, -1.35 * r, 0])]
        g.add(Polygon(*bp, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4))
    elif mouth:
        g.add(Arc(radius=0.3 * r, start_angle=PI * 1.2, angle=PI * 0.6, color=INK, stroke_width=4).move_to(head_c + DOWN * 0.42 * r))
    if bowtie:
        bc = np.array([x, y0 + 4.42 * u, 0])
        g.add(Polygon(bc, bc + np.array([-0.32 * u, 0.15 * u, 0]), bc + np.array([-0.32 * u, -0.15 * u, 0]), fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3),
              Polygon(bc, bc + np.array([0.32 * u, 0.15 * u, 0]), bc + np.array([0.32 * u, -0.15 * u, 0]), fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3))
    g.hand_r, g.hand_l, g.head_c, g.u = hand_r, hand_l, head_c, u
    return g


def me(x, y0, h=2.7):
    """ME (Rithika): long dark hair, waving."""
    return person(x, y0, h, top=PAGE_TOP, bottom=DARK_L, hair="long", hair_color=DARK_TOP, wf=0.95, arm_r=150, arm_l=10)


def keyword_librarian(x, y0, h=3.0):
    """KEYWORD LIBRARIAN (BM25): tall thin old man, round glasses, bow tie, magnifying glass."""
    g = person(x, y0, h, top=BAR1, bottom=DARK_L, hair="sides", wf=0.78, arm_r=110, arm_l=8, glasses=True, bowtie=True)
    c = g.hand_r + np.array([0.25, 0.42, 0]) * (h / 3.0)
    lens = VGroup(Line(g.hand_r, c + np.array([-0.17, -0.2, 0]) * (h / 3.0), color=INK, stroke_width=7),
                  Circle(radius=0.32 * h / 3.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=7).move_to(c))
    g.tool, g.tool_center = lens, c
    g.add(lens)
    return g


def meaning_librarian(x, y0, h=2.6):
    """MEANING LIBRARIAN (embedding): shorter old man, white beard, cardigan, lightbulb held up."""
    g = person(x, y0, h, top=BOX_R, bottom=BAR1, hair="white", wf=1.15, arm_r=125, arm_l=10, beard=True, buttons=True)
    k = h / 2.6
    sock = Rectangle(width=0.26 * k, height=0.2 * k, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(g.hand_r + UP * 0.2 * k)
    glass = Circle(radius=0.3 * k, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to(g.hand_r + UP * 0.58 * k)
    g.tool, g.tool_center = VGroup(sock, glass), g.hand_r + UP * 0.58 * k
    g.add(g.tool)
    return g


def lazy_librarian(x, y0, h=2.6):
    """LAZY LIBRARIAN: sleepy young assistant, half-closed eyes, arm out for thin books."""
    return person(x, y0, h, top=BAR2, bottom=BOX_R, hair="messy", hair_color=DARK_L, arm_r=55, arm_l=12, eyes="sleepy")


def searcher(x, y0, h=2.6):
    """SEARCHER: generic person typing on a phone."""
    g = person(x, y0, h, top=BOX_L, bottom=DARK_L, hair="short", hair_color=DARK_L, arm_r=-42, arm_l=-42)
    k = h / 2.6
    c = (g.hand_r + g.hand_l) / 2 + UP * 0.22 * k
    ph = VGroup(RoundedRectangle(width=0.42 * k, height=0.66 * k, corner_radius=0.06 * k, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to(c),
                RoundedRectangle(width=0.3 * k, height=0.46 * k, corner_radius=0.03 * k, fill_color=CARD, fill_opacity=1, stroke_width=0).move_to(c + UP * 0.03 * k))
    g.add(ph)
    g.phone = ph
    g.phone_top = c + UP * 0.33 * k
    return g


def reviewer(x, y0, h=2.2):
    """REVIEWER: generic person holding a coffee cup."""
    g = person(x, y0, h, top=BAR2, bottom=DARK_L, hair="short", hair_color=BOX_R, arm_r=-25, arm_l=10)
    k = h / 2.2
    cup = VGroup(Arc(radius=0.1 * k, start_angle=-PI / 2, angle=PI, color=INK, stroke_width=4).move_to(g.hand_r + np.array([0.2 * k, 0.12 * k, 0])),
                 RoundedRectangle(width=0.3 * k, height=0.36 * k, corner_radius=0.05, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to(g.hand_r + UP * 0.12 * k))
    g.add(cup)
    return g


def say_down(cx, y, s, size=40):
    """A speech bubble centred at (cx, y) with its tail pointing down-left (to a speaker below)."""
    t = T(s, size, INK)
    w, h = t.width + 0.6, t.height + 0.42
    body = RoundedRectangle(width=w, height=h, corner_radius=0.22, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([cx, y, 0])
    t.move_to(body.get_center())
    bx = cx - w * 0.2
    tail = Polygon([bx - 0.16, y - h / 2 + 0.06, 0], [bx + 0.16, y - h / 2 + 0.06, 0], [bx - 0.3, y - h / 2 - 0.36, 0],
                   fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(tail, body, t)


def say_r(right_x, y, s, size=36):
    """A speech bubble with real words, right edge at right_x, tail pointing right (to the speaker)."""
    t = T(s, size, INK)
    w, h = t.width + 0.6, t.height + 0.42
    body = RoundedRectangle(width=w, height=h, corner_radius=0.22, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4)
    body.move_to([right_x - w / 2, y, 0])
    t.move_to(body.get_center())
    tail = Polygon([right_x - 0.06, y + 0.14, 0], [right_x - 0.06, y - 0.14, 0], [right_x + 0.32, y - 0.06, 0],
                   fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(tail, body, t)




# ═════════════════════════════ FINAL-FILM HELPERS (2026-11-23) ═════════════════════════════
# Rules (Rithika): real readable text only (no scribble()/iso.page ghost lines), every key term
# labelled when spoken (at() on the whisper word times), characters exit when their line ends,
# numbers on screen exactly as in FILM-BRIEF.md.
PARTS_T = {1: "1 · Executive summary", 2: "2 · What others have done", 3: "3 · Methods", 4: "4 · Evaluation"}
PART_OF = {**{f"B{n:02d}": 1 for n in range(1, 6)}, **{f"B{n:02d}": 2 for n in range(6, 10)},
           **{f"B{n:02d}": 3 for n in range(10, 18)}, **{f"B{n:02d}": 4 for n in range(18, 23)}, "BOUT": 4}


def header(part):
    t = T(PARTS_T[part], TAG, TAG_INK)
    t.move_to([0, 3.12, 0]).align_to(np.array([-6.1, 0, 0]), LEFT)
    return t


def opener(self):
    """Part title card over the 1.2 s lead silence, then it shrinks to the top-left header."""
    part = PART_OF[bid_of(self)]
    big = T(PARTS_T[part], 84, INK, bold=True).move_to([0, 0.25, 0])
    rule = Line([-3.0, -0.75, 0], [3.0, -0.75, 0], color=INK, stroke_width=5)
    self.add(big, rule)
    self.wait(0.85)
    hdr = header(part)
    self.play(Transform(big, hdr), FadeOut(rule), run_time=0.3)
    return big


def plain(self):
    self.add(header(PART_OF[bid_of(self)]))


def blank_card(x, y, w=1.6, h=0.5, fill=PAGE_TOP):
    return RoundedRectangle(width=w, height=h, corner_radius=0.08, fill_color=fill, fill_opacity=1, stroke_color=BAR1, stroke_width=3).move_to([x, y, 0])


def balance(x, y, w=3.0, s=1.0, lfill=PAGE_TOP, rfill=DECOY_L, blocks=True):
    """A balance scale (deep-kraft outlines: GATE T reads ink-edged connectors as fused text). Left pan = human (white block), right pan = agent (grey block). .arm rotates about .pivot."""
    post = Rectangle(width=0.16 * s, height=1.6 * s, fill_color=BOX_R, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=3).move_to([x, y - 0.8 * s, 0])
    foot = RoundedRectangle(width=1.2 * s, height=0.24 * s, corner_radius=0.06, fill_color=BOX_L, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=3).move_to([x, y - 1.66 * s, 0])
    beam = RoundedRectangle(width=w, height=0.16 * s, corner_radius=0.05, fill_color=BOX_L, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=3).move_to([x, y, 0])
    pans, blks = VGroup(), VGroup()
    px_ = []
    for sx, fill in ((-1, lfill), (1, rfill)):
        px = x + sx * (w / 2 - 0.12 * s)
        px_.append(px)
        strings = VGroup(Line([px, y, 0], [px - 0.4 * s, y - 0.62 * s, 0], color=KRAFT_DEEP, stroke_width=3),
                         Line([px, y, 0], [px + 0.4 * s, y - 0.62 * s, 0], color=KRAFT_DEEP, stroke_width=3))
        dish = Polygon([px - 0.55 * s, y - 0.62 * s, 0], [px + 0.55 * s, y - 0.62 * s, 0], [px + 0.38 * s, y - 0.8 * s, 0], [px - 0.38 * s, y - 0.8 * s, 0],
                       fill_color=BOX_TOP, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=3)
        pans.add(VGroup(strings, dish))
        if blocks:
            blks.add(Rectangle(width=0.56 * s, height=0.4 * s, fill_color=fill, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=3).move_to([px, y - 0.42 * s, 0]))
    arm = VGroup(beam, pans, blks)
    g = VGroup(foot, post, arm)
    g.arm, g.pivot, g.pan_x, g.blocks = arm, np.array([x, y, 0]), px_, blks
    return g


def tip(g, ang=0.16):
    """+ang tips the LEFT (human) pan down."""
    return Rotate(g.arm, angle=ang, about_point=g.pivot)


def crate(ox, oy, s=1.0, w=3.4, d=1.6, h=1.5):
    iso = Iso(ox, oy, s)
    back, front = iso.open_box(0, 0, 0, w, d, h)
    return iso, back, front


def corpus_stack(ox, oy, s=1.0, w=3.4, d=1.6):
    """The test corpus as a stack whose three layers show on its faces: thin white (correct), thick grey (BM25 near-misses), kraft (random)."""
    iso = Iso(ox, oy, s)
    l1 = iso.box(0, 0, 0, w, d, 0.22, PAGE_TOP, PAGE_L, PAGE_R, sw=3)
    l2 = iso.box(0, 0, 0.22, w, d, 0.75, DECOY_TOP, DECOY_L, DECOY_R, sw=3)
    l3 = iso.box(0, 0, 0.97, w, d, 0.65, BOX_TOP, BOX_L, BOX_R, sw=3)
    return iso, l1, l2, l3


def layer(iso, z0, hh, w=3.4, d=1.6, kind="random"):
    cols = {"correct": (PAGE_TOP, PAGE_L, PAGE_R), "near": (DECOY_TOP, DECOY_L, DECOY_R), "random": (BOX_TOP, BOX_L, BOX_R)}[kind]
    g = iso.box(0.08, 0.08, z0, w - 0.16, d - 0.16, hh, *cols, sw=3)
    g.set_z_index(1)
    return g


def dashed_tile(x, y, w=2.6, h=2.0):
    return DashedVMobject(RoundedRectangle(width=w, height=h, corner_radius=0.15).move_to([x, y, 0]).set_stroke(INK, 4), num_dashes=28)


def solid_tile(x, y, w=2.6, h=2.0):
    return RoundedRectangle(width=w, height=h, corner_radius=0.15, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])


def timer_icon(x, y, r=0.36):
    face = Circle(radius=r, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    knob = Rectangle(width=0.16, height=0.12, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=2).move_to([x, y + r + 0.07, 0])
    hand = Line([x, y, 0], [x, y + r * 0.75, 0], color=INK, stroke_width=5)
    g = VGroup(face, knob, hand)
    g.hand = hand
    return g


def coins(x, y):
    return VGroup(*[Ellipse(width=0.8, height=0.3, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y + k * 0.16, 0]) for k in range(4)])


def badge(x, y, r=0.34):
    return VGroup(Circle(radius=r, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0]), check(x - 0.03, y + 0.02, s=0.15, color=INK, w=6))


def mini_laptop(x, y):
    base = RoundedRectangle(width=0.95, height=0.12, corner_radius=0.04, fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y - 0.3, 0])
    scr = RoundedRectangle(width=0.75, height=0.5, corner_radius=0.04, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y + 0.03, 0])
    return VGroup(base, scr)


def arrow(a, b):
    return Arrow(np.array(a, dtype=float), np.array(b, dtype=float), buff=0.12, color=INK, stroke_width=5, max_tip_length_to_length_ratio=0.12)


# ── the checklist (part 4) ──
RULES = ["1 Trust", "2 Length", "3 Dense vs BM25", "4 Human vs agent"]
VERDICTS = ["Met", "Provisional", "Provisional-flattered", "Human ahead"]
ROW_Y = [2.27, 1.72, 1.17, 0.62]


def checklist(n_done=0):
    board = RoundedRectangle(width=12.1, height=2.55, corner_radius=0.15, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=3).move_to([0, 1.44, 0])
    rows, slots, verdicts = VGroup(), VGroup(), VGroup()
    for k in range(4):
        rows.add(T(RULES[k], 36, INK, bold=True).move_to([0, ROW_Y[k], 0]).align_to(np.array([-5.75, 0, 0]), LEFT))
        slots.add(DashedVMobject(RoundedRectangle(width=1.1, height=0.42, corner_radius=0.1).move_to([1.15, ROW_Y[k], 0]).set_stroke(BAR1, 3), num_dashes=14))
        verdicts.add(verdict_chip(k))
    g = VGroup(board, rows, slots)
    for k in range(n_done):
        slots[k].set_opacity(0)
        g.add(verdicts[k])
    g.board, g.rows, g.slots, g.verdicts = board, rows, slots, verdicts
    return g


def verdict_chip(k):
    c = chip(VERDICTS[k], 0, ROW_Y[k], size=32)
    c.align_to(np.array([0.6, 0, 0]), LEFT)
    return c


def row_ring(k):
    """Current-row marker: a terracotta dot left of the rule's name."""
    return Dot([-5.93, ROW_Y[k], 0], radius=0.09, color=TERRA)


def stamp(self, cl, k):
    """The verdict lands in row k."""
    P(self, FadeOut(cl.slots[k]), FadeIn(cl.verdicts[k], scale=1.3), rt=0.4)
    cl.add(cl.verdicts[k])


# ═════════════════════════════ SCENES — final film (2026-11-23) ═════════════════════════════

# ── PART 1 · Executive summary (no BM25 / embedding / recall / corpus / MS MARCO on screen) ──
class B01_AgentsWrite(Scene):
    def construct(self):
        opener(self)
        box = RoundedRectangle(width=7.2, height=0.95, corner_radius=0.47, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=KRAFT_DEEP, stroke_width=5).move_to([0.9, 1.35, 0])
        lens = VGroup(Circle(radius=0.2, stroke_color=INK, stroke_width=5).move_to([4.0, 1.4, 0]), Line([4.14, 1.26, 0], [4.32, 1.08, 0], color=INK, stroke_width=5))
        who = searcher(-4.9, -3.4, h=3.3)
        mine = card("what is the shingles jab?", -3.0, 0.35, size=34)
        self.add(who, mine)
        at(self, "rag systems")
        P(self, FadeIn(VGroup(box, lens), shift=UP * 0.2), FadeIn(key("RAG: search, then answer", 0.9, 2.35, size=46), scale=0.7), rt=0.4)
        at(self, "ai agents")
        bot = robot(4.6, -2.6, s=ROBOT_S)
        P(self, slide_in(bot, RIGHT, 1.2), FadeIn(lab("AI agent", 4.9, 0.25, size=40, bold=True), scale=0.7), rt=0.4)
        at(self, "write the search")
        q = T("what is the shingles vaccine", 38, INK).move_to([0.55, 1.35, 0])
        P(self, Write(q), FadeIn(lab("writes the search query", 1.0, -0.7, size=38), scale=0.7), rt=0.55)
        at(self, "not people")
        P(self, slide_out(VGroup(who, mine), LEFT, 1.2), rt=0.4)
        done(self)


class B02_WrongPassage(Scene):
    def construct(self):
        plain(self)
        bot = robot(-5.0, -2.6, s=ROBOT_S)
        q = card("what is the shingles vaccine", -3.0, 2.2, size=34)
        lib = library(-1.6, -3.2, s=0.55, n=2, seed=7)
        self.add(bot, q, lib)
        page = flat_book(0.6, -0.9, w=0.7, h=0.95, decoy=True)
        at(self, "finds the wrong")
        P(self, FadeIn(page, shift=UP * 0.3), rt=0.3)
        P(self, page.animate.move_to([4.2, 0.0, 0]), rt=0.5)
        wl = lab("wrong passage", 4.2, -0.95, size=38, bold=True)
        pop(self, wl, rt=0.35)
        at(self, "the answer built")
        ans = card("answer", 4.2, 1.15, size=38, bold=True)
        P(self, FadeIn(ans, shift=DOWN * 0.3), FadeIn(xmark(5.95, 2.15, s=0.17)), FadeIn(lab("answer: wrong", 4.2, 2.15, size=38, bold=True), scale=0.7), rt=0.4)
        at(self, "nobody sees")
        curtain = Rectangle(width=2.9, height=2.2, fill_color=BAR2, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([4.2, 0.6, 0])
        P(self, FadeIn(curtain, shift=DOWN * 0.6), FadeIn(lab("why? hidden", 4.2, -1.7, size=40, bold=True), scale=0.7), rt=0.4)
        P(self, slide_out(bot, LEFT, 1.0), rt=0.35)
        done(self)


class B03_TheLab(Scene):
    def construct(self):
        plain(self)
        rith = me(-5.3, -3.4, h=3.0)
        at(self, "built")
        P(self, slide_in(rith, LEFT, 1.0), rt=0.45)
        at(self, "retrieval lab")
        sc = balance(-1.0, 0.8, w=4.0, s=1.0)
        P(self, FadeIn(key("Agentic Retrieval Lab", 0.3, 2.35, size=56), scale=0.8), FadeIn(sc, shift=UP * 0.2), rt=0.5)
        at(self, "public data")
        pop(self, chip("public data", 4.6, 1.45, size=38))
        at(self, "queries find")
        ag = lab("agent-written query", sc.pan_x[1], 1.5, size=34, bold=True)
        P(self, FadeIn(ag, shift=DOWN * 0.3), rt=0.4)
        at(self, "the right passage")
        rp = VGroup(flat_book(4.6, 0.55, w=0.6, h=0.8, right=True), lab("right passage?", 4.6, -0.25, size=36, bold=True))
        pop(self, rp)
        at(self, "original human question")
        hu = lab("human question", sc.pan_x[0], 1.5, size=34, bold=True)
        P(self, FadeIn(hu, shift=DOWN * 0.3), rt=0.4)
        at(self, "which search method")
        c1 = cart(2.3, -3.3, s=0.45, tool="glass", books=False)
        c2 = cart(4.1, -3.3, s=0.45, tool="bulb", books=False)
        P(self, FadeIn(VGroup(c1, c2), shift=LEFT * 0.6), FadeIn(lab("which search method?", 4.1, -1.15, size=34, bold=True), scale=0.7), rt=0.45)
        at(self, "handles them best")
        self.wait(0.6)
        P(self, slide_out(rith, LEFT, 1.0), rt=0.4)
        done(self)


class B04_SoFar(Scene):
    def construct(self):
        plain(self)
        xs = [-4.6, -1.55, 1.55, 4.6]
        scales = [balance(x, -0.3, w=2.0, s=0.8) for x in xs]
        legend = VGroup(Rectangle(width=0.42, height=0.3, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-4.3, 1.6, 0]),
                        T("human question", 42, INK).move_to([0, 1.6, 0]).align_to(np.array([-3.9, 0, 0]), LEFT),
                        Rectangle(width=0.42, height=0.3, fill_color=DECOY_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([0.6, 1.6, 0]),
                        T("agent rewrite", 42, INK).move_to([0, 1.6, 0]).align_to(np.array([1.0, 0, 0]), LEFT))
        at(self, "so far")
        P(self, LaggedStart(*[FadeIn(s_, shift=UP * 0.3) for s_ in scales], lag_ratio=0.2), FadeIn(legend), FadeIn(lab("so far", -5.2, 2.45, size=44, bold=True)), rt=0.6)
        at(self, "didnt beat")
        P(self, LaggedStart(*[tip(s_) for s_ in scales], lag_ratio=0.25), rt=0.9)
        at(self, "any search method")
        P(self, FadeIn(lab("every search method", 0, -2.85, size=40, bold=True), scale=0.7),
          FadeIn(key("human question ahead", 1.3, 2.45, size=44), scale=0.7), Create(check(4.6, 2.45, s=0.22, color=TERRA, w=8)), rt=0.45)
        done(self)


class B05_WhyItMatters(Scene):
    def construct(self):
        plain(self)
        bot = robot(-5.0, -2.6, s=ROBOT_S)
        c1 = cart(-3.6, -3.2, s=0.5, tool="glass", books=False)
        c2 = cart(-1.9, -3.2, s=0.5, tool="bulb", books=False)
        self.add(bot)
        at(self, "choosing a search")
        P(self, FadeIn(VGroup(c1, c2), shift=UP * 0.3), FadeIn(lab("choosing a search method", -3.4, 0.55, size=38, bold=True), scale=0.7), rt=0.45)
        at(self, "for an ai agent", lead=-0.6)
        P(self, slide_out(bot, LEFT, 1.0), dim(VGroup(c1, c2)), rt=0.4)
        at(self, "cheap")
        pop(self, chip("cheap", 1.4, 2.3, size=44))
        at(self, "repeatable")
        loop = Arc(radius=0.36, start_angle=0.3, angle=TAU * 0.82, color=INK, stroke_width=6).move_to([3.4, 2.3, 0])
        loop.add_tip(tip_length=0.18)
        P(self, Create(loop), FadeIn(lab("repeatable", 4.9, 2.3, size=40, bold=True), scale=0.7), rt=0.45)
        at(self, "every number")
        lap = laptop(1.4, -2.9, s=0.8)
        num = T("+0.32", 40, INK, bold=True).move_to(lap[2].get_center())
        P(self, FadeIn(lap, shift=UP * 0.3), rt=0.4)
        pop(self, num)
        at(self, "traces back")
        fi = file_icon(5.0, -0.9, w=1.1, h=1.35)
        P(self, FadeIn(fi, shift=LEFT * 0.3), FadeIn(lab("results file", 5.0, -2.05, size=36, bold=True)), rt=0.4)
        P(self, GrowArrow(arrow(lap[2].get_right(), fi.get_left())), FadeIn(key("traces back to a file", 2.6, 0.95, size=42), scale=0.7), rt=0.45)
        done(self)


# ── PART 2 · What others have done ──
class B06_Q2DWeb(Scene):
    def construct(self):
        opener(self)
        iso = Iso(-4.4, -3.1, 0.85)
        vault = iso.box(0, 0, 0, 2.4, 2.0, 2.4, BAR3, BAR2, BAR1)
        door = Circle(radius=0.62, fill_color=BAR2, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to(iso.p(1.2, 0, 1.2)).stretch(0.8, 0)
        hub = Circle(radius=0.18, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(door.get_center())
        at(self, "q2d web")
        P(self, FadeIn(VGroup(vault, door, hub), shift=UP * 0.3), FadeIn(key("Q2D-Web", -4.1, 2.3, size=56), scale=0.7), rt=0.45)
        at(self, "from perplexity")
        pop(self, lab("Perplexity", -4.1, 1.55, size=40))
        at(self, "queries over", lead=0.9)
        cards = VGroup(*[blank_card(2.0 + k * 0.5, -0.2 + k * 0.35, w=1.2, h=0.42) for k in range(3)])
        P(self, FadeIn(cards, shift=LEFT * 0.4), FadeIn(lab("agent-written queries", 0.9, 2.3, size=38, bold=True), scale=0.7), rt=0.4)
        P(self, cards.animate.move_to(door.get_center()).scale(0.4), rt=0.5)
        P(self, FadeOut(cards), rt=0.25)
        at(self, "190 million")
        pop(self, lab("190 million web documents", 0.9, 1.55, size=40, bold=True))
        at(self, "keeps its corpus")
        drawers = VGroup(*[chip(t, -0.3, y, size=34, bold=False) for t, y in (("corpus", 0.55), ("queries", -0.25), ("judgments", -1.05))])
        P(self, LaggedStart(*[FadeIn(d_, shift=LEFT * 0.3) for d_ in drawers], lag_ratio=0.3), rt=0.6)
        at(self, "private")
        bar = Rectangle(width=0.32, height=2.5, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([1.35, -0.25, 0])
        P(self, FadeIn(bar, shift=UP * 0.4), rt=0.35)
        P(self, FadeIn(Dot([1.35, -0.25, 0], radius=0.1, color=TERRA)), FadeIn(key("private", -0.3, -2.0, size=46), scale=0.7), rt=0.35)
        at(self, "leaderboard")
        board = VGroup(RoundedRectangle(width=1.8, height=1.3, corner_radius=0.1, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([4.3, -0.2, 0]))
        for k, hh in enumerate([0.8, 0.6, 0.4]):
            board.add(Rectangle(width=0.32, height=hh, fill_color=[BAR1, BAR2, BAR1][k], fill_opacity=1, stroke_width=0).move_to([3.8 + k * 0.5, -0.75 + hh / 2, 0]))
        post = Rectangle(width=0.14, height=1.3, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([4.3, -1.5, 0])
        P(self, FadeIn(VGroup(post, board), shift=UP * 0.3), FadeIn(lab("public leaderboard", 4.3, -2.5, size=38, bold=True), scale=0.7), rt=0.45)
        at(self, "not the data")
        pop(self, lab("not the data", 4.3, -3.05, size=38, bold=True))
        done(self)


class B07_MSMARCO(Scene):
    def construct(self):
        plain(self)
        jso = Iso(-4.3, -3.35, 0.85)
        back, front = jso.open_box(0, 0, 0, 2.6, 1.5, 0.9)
        at(self, "marko")
        P(self, FadeIn(VGroup(back, front), shift=UP * 0.3), FadeIn(key("MS MARCO", -2.6, 2.3, size=56), scale=0.7), rt=0.45)
        at(self, "from microsoft")
        pop(self, lab("Microsoft", -2.6, 1.65, size=40))
        at(self, "standard public")
        pop(self, chip("public", 0.6, 2.3, size=40))
        at(self, "real search questions")
        qs = VGroup(card("when is ski season over", -2.5, 0.35, size=34), card("what is the shingles jab?", -2.5, -0.45, size=34))
        P(self, LaggedStart(*[FadeIn(c, shift=UP * 0.5) for c in qs], lag_ratio=0.3), rt=0.6)
        at(self, "marked correct")
        pg = flat_book(3.3, 0.2, w=1.0, h=1.3, right=True)
        P(self, FadeIn(pg, shift=DOWN * 0.3), rt=0.35)
        P(self, Create(check(4.4, 0.25, s=0.26, color=TERRA, w=9)), FadeIn(lab("marked correct passage", 3.3, -1.0, size=38, bold=True), scale=0.7), rt=0.4)
        at(self, "human only")
        pop(self, key("human only", -2.5, 1.05, size=44))
        done(self)


class B08_Librarians(Scene):
    def construct(self):
        plain(self)
        kc = keyword_librarian(-4.7, -3.4, h=3.0)
        mc = meaning_librarian(4.6, -3.4, h=2.6)
        kc.tool._qc_intentional = True     # the magnifier reading the card IS the claim (as in October B03)
        self.add(tag_constructed(0, -2.45))
        qc = card("query: car repair cost", 0, -1.45, size=36, bold=True)
        at(self, "bm25")
        P(self, slide_in(kc, LEFT, 1.2), FadeIn(qc, scale=0.9), FadeIn(chip("BM25: keyword search", -3.0, 2.3, size=38), scale=0.7), rt=0.45)
        at(self, "keyword search")
        ba = card("car repair cost", -2.7, 0.75, size=36)
        P(self, FadeIn(ba, shift=DOWN * 0.3), rt=0.35)
        P(self, kc.tool.animate.move_to(ba.get_center()), rt=0.45)
        P(self, FadeIn(lab("same words", -2.7, -0.1, size=40, bold=True), scale=0.7), rt=0.35)
        left = VGroup(kc, ba)
        at(self, "bge and e5")
        P(self, dim(left), slide_in(mc, RIGHT, 1.2), FadeIn(chip("bge · e5: embedding models", 2.7, 2.3, size=36), scale=0.7), rt=0.45)
        at(self, "search by meaning")
        bb = card("fixing an automobile price", 2.2, 0.75, size=34)
        P(self, FadeIn(bb, shift=DOWN * 0.3), FadeIn(lab("search by meaning", 2.7, 1.55, size=38, bold=True), scale=0.7), rt=0.4)
        glow = light_bulb(mc.tool_center, s=0.8)
        P(self, FadeIn(glow), FadeIn(lab("same meaning", 2.2, -0.1, size=40, bold=True), scale=0.7), rt=0.4)
        P(self, slide_out(kc, LEFT, 1.2), slide_out(VGroup(mc, glow), RIGHT, 1.2), rt=0.4)
        done(self)


class B09_TheGap(Scene):
    def construct(self):
        plain(self)
        xs = [-4.65, -1.55, 1.55, 4.65]
        tiles = VGroup(*[solid_tile(x, 0.95) for x in xs[:3]])
        icons = VGroup(
            Iso(-5.2, 0.2, 0.42).box(0, 0, 0, 2.2, 1.8, 2.0, BAR3, BAR2, BAR1),
            VGroup(*Iso(-2.25, 0.25, 0.5).open_box(0, 0, 0, 2.4, 1.4, 0.8)),
            VGroup(Circle(radius=0.36, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([0.95, 0.95, 0]),
                   Circle(radius=0.36, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([2.15, 0.95, 0]),
                   Dot([2.15, 0.95, 0], radius=0.09, color=TERRA)))
        names = VGroup(lab("Q2D-Web\nprivate", xs[0], -0.6, size=32, bold=True), lab("MS MARCO\nhuman only", xs[1], -0.6, size=32, bold=True),
                       lab("BM25 · bge · e5", xs[2], -0.45, size=32, bold=True))
        empty = dashed_tile(xs[3], 0.95)
        self.add(tiles, icons, names)
        at(self, "the gap")
        P(self, Create(empty), FadeIn(key("the gap", xs[3], 2.45, size=46), scale=0.7), rt=0.45)
        items = [("small open", "small · open"), ("compares human", "human vs agent"), ("these search methods", "across search methods"), ("rerun on a laptop", "rerun on a laptop")]
        for k, (cue, txt) in enumerate(items):
            at(self, cue)
            t = T(txt, 38, INK, bold=True).move_to([0, -1.45 - k * 0.5, 0]).align_to(np.array([-5.8, 0, 0]), LEFT)
            P(self, FadeIn(t, shift=RIGHT * 0.3), rt=0.35)
        lap = mini_laptop(xs[3], 1.0).scale(1.5)
        P(self, FadeIn(lap, shift=LEFT * 0.6), rt=0.4)
        at(self, "thats what")
        rith = me(2.4, -3.4, h=2.2)
        P(self, FadeOut(empty), FadeIn(solid_tile(xs[3], 0.95).set_z_index(-1)), FadeIn(lab("this project", xs[3], -0.45, size=36, bold=True), scale=0.7),
          slide_in(rith, DOWN, 0.6), rt=0.45)
        self.wait(0.6)
        P(self, slide_out(rith, DOWN, 0.6), rt=0.35)
        done(self)


# ── PART 3 · Methods ──
class B10_Data(Scene):
    def construct(self):
        opener(self)
        stack = VGroup(*[blank_card(-4.2 + k * 0.08, -0.1 + k * 0.12, w=2.2, h=0.62) for k in range(6)])
        at(self, "data")
        P(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.4) for c in stack], lag_ratio=0.15), FadeIn(key("300 questions", -4.0, 1.95, size=48), scale=0.7),
          FadeIn(lab("MS MARCO", -4.0, -1.0, size=38, bold=True)), rt=0.7)
        at(self, "fixed seed")
        pop(self, tag("seed 42", -4.0, 1.25))
        at(self, "claude haiku")
        bot = robot(-0.6, -2.6, s=ROBOT_S)
        P(self, slide_in(bot, DOWN, 0.6), FadeIn(lab("Claude Haiku 4.5", -0.6, 0.35, size=38, bold=True), scale=0.7), rt=0.45)
        at(self, "rewrote each")
        one = blank_card(-3.75, 0.5, w=2.2, h=0.62)
        P(self, one.animate.move_to([1.6, 1.0, 0]), rt=0.5)
        at(self, "one main")
        main = blank_card(4.0, 1.75, w=2.6, h=0.55)
        sup = VGroup(*[blank_card(4.0, 0.95 - k * 0.62, w=2.6, h=0.5, fill=BOX_TOP) for k in range(3)])
        P(self, ReplacementTransform(one, main), FadeIn(lab("1 main", 4.0, 2.45, size=38, bold=True), scale=0.7), rt=0.4)
        at(self, "three supporting")
        P(self, LaggedStart(*[FadeIn(s_, shift=RIGHT * 0.3) for s_ in sup], lag_ratio=0.25), FadeIn(lab("3 supporting", 4.0, -1.0, size=38, bold=True), scale=0.7), rt=0.6)
        at(self, "in total", lead=0.8)
        pop(self, key("1,200 agent queries", 3.3, -2.0, size=50))
        done(self)


class B11_LeakCheck(Scene):
    def construct(self):
        plain(self)
        bot = robot(-0.6, -2.6, s=ROBOT_S)
        grid = VGroup(*[blank_card(-5.0 + (k % 2) * 2.0, 1.8 - (k // 2) * 0.7, w=1.7, h=0.48) for k in range(6)])
        self.add(bot, grid, key("leak check", -4.0, -0.9, size=46))
        scan = Line([-6.0, 2.25, 0], [-3.0, 2.25, 0], color=TERRA, stroke_width=5)
        self.add(scan)
        self.play(scan.animate.move_to([-4.5, 0.15, 0]), run_time=0.55)
        self.play(FadeOut(scan), run_time=0.1)
        flag = card("lincoln kentucky hodgenville childhood", 2.0, 1.6, size=32, bold=True)
        P(self, ReplacementTransform(grid[3].copy(), flag), rt=0.5)
        P(self, FadeIn(lab("answer: Hodgenville, Kentucky", 2.0, 0.75, size=36), scale=0.7), FadeIn(key("gave away the answer", 2.6, -0.1, size=42), scale=0.7), rt=0.3)
        P(self, slide_out(bot, DOWN, 0.6), rt=0.3)
        done(self)


class B12_TestCorpus(Scene):
    def construct(self):
        plain(self)
        iso, l1, l2, l3 = corpus_stack(-2.6, -3.0, s=1.0)
        floor = Line([-5.6, -3.05, 0], [1.0, -3.05, 0], color=KRAFT_DEEP, stroke_width=4)
        at(self, "test corpus")
        P(self, Create(floor), FadeIn(key("test corpus", -1.5, 2.35, size=50), scale=0.7), rt=0.45)
        at(self, "passages made", lead=0.9)
        pop(self, key("200,000 passages", 3.4, 2.35, size=46))
        at(self, "every correct passage")
        P(self, FadeIn(l1, shift=DOWN * 0.5), FadeIn(lab("every correct passage", 3.5, 1.2, size=36, bold=True), scale=0.7), rt=0.4)
        at(self, "top 100 near")
        kc = cart(3.4, -3.3, s=0.6, tool="glass", books=True)
        P(self, FadeIn(kc, shift=LEFT * 0.8), rt=0.35)
        P(self, FadeIn(l2, shift=DOWN * 0.5), FadeIn(lab("BM25's top-100 near-misses", 3.5, 0.45, size=36, bold=True), scale=0.7), rt=0.4)
        P(self, FadeOut(kc, shift=RIGHT * 0.8), rt=0.35)
        at(self, "random fill")
        P(self, FadeIn(l3, shift=DOWN * 0.5), FadeIn(lab("random fill", 3.5, -0.3, size=36, bold=True), scale=0.7), rt=0.4)
        done(self)


class B13_FourRetrievers(Scene):
    def construct(self):
        plain(self)
        line = Line([-6.0, -2.4, 0], [6.0, -2.4, 0], color=INK, stroke_width=4)
        at(self, "four retrievers")
        P(self, Create(line), FadeIn(key("four retrievers", 0, 2.35, size=50), scale=0.7), rt=0.4)
        xs = [-5.3, -2.4, 0.5, 3.4]
        names = ["BM25", "bge-small", "e5-small", "BM25+bge hybrid"]
        tools = ["glass", "bulb", "bulb", "glass"]
        cues = [("bm25", 1), ("bge small", 1), ("e5 small", 1), ("hybrid", 1)]
        for k in range(4):
            at(self, cues[k][0], nth=cues[k][1])
            c = cart(xs[k], -2.3, s=0.75, tool=tools[k], books=True)
            anims = [FadeIn(c, shift=UP * 0.4), FadeIn(lab(names[k], xs[k] + (0.8 if k == 3 else 0.6), -2.95, size=36, bold=True), scale=0.7)]
            if k == 3:
                anims.append(FadeIn(Circle(radius=0.3, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to(c.tool_center + RIGHT * 0.75)))
            P(self, *anims, rt=0.35)
        done(self)


class B14_Measures(Scene):
    def construct(self):
        plain(self)
        hu = card("human: what is the shingles jab?", -2.9, 1.5, size=34, bold=True)
        ag = card("agent: what is the shingles vaccine", -2.9, -0.9, size=34, bold=True)
        at(self, "measures")
        P(self, FadeIn(hu, shift=RIGHT * 0.3), FadeIn(ag, shift=RIGHT * 0.3), FadeIn(key("BM25 · top 100", 1.9, 2.55, size=40), scale=0.7), rt=0.4)
        at(self, "top 100")
        piles = VGroup()
        for y in (1.5, -0.9):
            frame = RoundedRectangle(width=2.5, height=1.15, corner_radius=0.12, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=3).move_to([1.9, y, 0])
            pages = VGroup(*[flat_book(1.05 + k * 0.42, y, w=0.32, h=0.6, decoy=True) for k in range(4)])
            piles.add(VGroup(frame, pages))
        r_in = flat_book(2.75, 1.5, w=0.4, h=0.6, right=True)
        r_out = flat_book(3.75, -0.9, w=0.4, h=0.6, right=True)
        P(self, FadeIn(piles), FadeIn(r_in), FadeIn(r_out), rt=0.4)
        P(self, Create(check(3.75, 1.55, s=0.22, color=TERRA, w=8)), FadeIn(xmark(4.45, -0.9, s=0.22)),
          FadeIn(lab("in the top 100", 1.9, 0.6, size=34, bold=True)), FadeIn(lab("not in the top 100", 2.3, -1.8, size=34, bold=True)), rt=0.4)
        at(self, "how high")
        ruler = Line([-0.6, -2.75, 0], [5.4, -2.75, 0], color=INK, stroke_width=4)
        ticks = VGroup(lab("1", -0.6, -3.15, size=32), lab("100", 5.4, -3.15, size=32))
        mover = flat_book(4.6, -2.45, w=0.34, h=0.5, right=True)
        P(self, Create(ruler), FadeIn(ticks), FadeIn(mover), FadeIn(lab("how high it ranks", -3.6, -2.75, size=38, bold=True), scale=0.7), rt=0.4)
        P(self, mover.animate.move_to([0.2, -2.45, 0]), rt=0.6)
        done(self)


class B15_Bootstrap(Scene):
    def construct(self):
        plain(self)
        at(self, "query by query")
        pairs = VGroup(*[VGroup(blank_card(-5.4 + k * 1.0, 1.25, w=0.75, h=0.42), blank_card(-5.4 + k * 1.0, 0.65, w=0.75, h=0.42, fill=DECOY_L)) for k in range(6)])
        P(self, FadeIn(key("query by query", -2.9, 2.35, size=46), scale=0.7), LaggedStart(*[FadeIn(p_, shift=DOWN * 0.3) for p_ in pairs], lag_ratio=0.15), rt=0.8)
        at(self, "bootstrap")
        axis = Line([-1.5, -1.7, 0], [5.6, -1.7, 0], color=INK, stroke_width=4)
        zero = VGroup(Line([-0.6, -1.9, 0], [-0.6, -1.5, 0], color=INK, stroke_width=4), lab("0", -0.6, -2.3, size=36, bold=True))
        whisk = VGroup(Line([2.4, -1.25, 0], [4.2, -1.25, 0], color=INK, stroke_width=6),
                       Line([2.4, -1.45, 0], [2.4, -1.05, 0], color=INK, stroke_width=6), Line([4.2, -1.45, 0], [4.2, -1.05, 0], color=INK, stroke_width=6),
                       Dot([3.3, -1.25, 0], radius=0.13, color=TERRA))
        P(self, Create(axis), FadeIn(zero), rt=0.35)
        P(self, FadeIn(whisk, scale=0.8), FadeIn(lab("95% bootstrap interval", 2.0, -0.35, size=40, bold=True), scale=0.7), rt=0.4)
        done(self)


class B16_Resources(Scene):
    def construct(self):
        plain(self)
        ys = [2.2, 1.15, 0.1, -0.95, -2.0]
        self.add(key("all in hand", 3.8, 2.3, size=48))
        at(self, "m5 laptop")
        r1 = VGroup(mini_laptop(-5.4, ys[0]), T("M5 laptop · 16 GB", 40, INK, bold=True).move_to([0, ys[0], 0]).align_to(np.array([-4.6, 0, 0]), LEFT))
        P(self, FadeIn(r1, shift=RIGHT * 0.3), rt=0.4)
        at(self, "eight minutes", lead=0.9)
        tm = timer_icon(-5.4, ys[1])
        r2 = VGroup(tm, T("about 8 minutes per embedding model", 40, INK, bold=True).move_to([0, ys[1], 0]).align_to(np.array([-4.6, 0, 0]), LEFT))
        P(self, FadeIn(r2, shift=RIGHT * 0.3), rt=0.4)
        P(self, Rotate(tm.hand, angle=-TAU * 0.6, about_point=np.array([-5.4, ys[1], 0])), rt=0.6)
        at(self, "anthropic api")
        r3 = VGroup(coins(-5.4, ys[2] - 0.2), T("Anthropic API credits", 40, INK, bold=True).move_to([0, ys[2], 0]).align_to(np.array([-4.6, 0, 0]), LEFT))
        P(self, FadeIn(r3, shift=RIGHT * 0.3), rt=0.4)
        at(self, "63 cents", lead=0.5)
        pop(self, chip("$0.63 · all LLM calls", 3.6, ys[2], size=36))
        at(self, "hugging face")
        r4 = VGroup(badge(-5.4, ys[3]), T("free Hugging Face account", 40, INK, bold=True).move_to([0, ys[3], 0]).align_to(np.array([-4.6, 0, 0]), LEFT))
        P(self, FadeIn(r4, shift=RIGHT * 0.3), rt=0.4)
        at(self, "135 automated")
        r5 = VGroup(check(-5.4, ys[4], s=0.26, color=TERRA, w=9), T("135 automated tests", 44, INK, bold=True).move_to([0, ys[4], 0]).align_to(np.array([-4.6, 0, 0]), LEFT))
        P(self, FadeIn(r5, shift=RIGHT * 0.3), rt=0.4)
        done(self)


class B17_Next(Scene):
    def construct(self):
        plain(self)
        pos = [(-3.1, 1.45), (3.1, 1.45), (-3.1, -1.25), (3.1, -1.25)]
        tiles = VGroup(*[dashed_tile(x, y, w=2.2, h=1.25) for x, y in pos])
        names = ["length-matched control corpus", "harder distractors (dense-picked)", "two larger embedding models", "LLM relevance judge"]
        cues = ["length matched", "harder distractors", "two larger", "relevance judge"]
        at(self, "next")
        P(self, Create(tiles), FadeIn(key("next", 0, 2.4, size=50), scale=0.7), rt=0.5)
        mc = meaning_librarian(0.0, -3.45, h=1.8)
        for k in range(4):
            at(self, cues[k])
            x, y = pos[k]
            icon = robot(x, y - 0.55, s=0.45) if k == 3 else Iso(x - 0.15, y - 0.5, 0.42).box(0, 0, 0, 1.8, 1.2, 1.0)
            anims = [Create(solid_tile(x, y, w=2.2, h=1.25).set_fill(opacity=0)), FadeIn(icon, shift=DOWN * 0.3),
                     FadeIn(lab(names[k], x, y - 0.95, size=34, bold=True), scale=0.7)]
            if k == 1:
                anims.append(slide_in(mc, DOWN, 0.6))
            if k == 2:
                anims.append(slide_out(mc, DOWN, 0.6))
            P(self, *anims, rt=0.4)
        done(self)


# ── PART 4 · Evaluation (the checklist) ──
class B18_Rules(Scene):
    def construct(self):
        opener(self)
        cl = checklist(0)
        clip = RoundedRectangle(width=1.4, height=0.34, corner_radius=0.08, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([0, 2.72, 0])
        at(self, "rules before", lead=0.9)
        P(self, FadeIn(VGroup(cl, clip), shift=DOWN * 0.4), FadeIn(key("pass/fail rules", -3.2, -0.55, size=48), scale=0.7), rt=0.55)
        at(self, "milestone two")
        pop(self, lab("before Milestone 2", -3.2, -1.4, size=40, bold=True))
        at(self, "drafted with")
        rith = me(4.6, -3.4, h=2.4)
        P(self, FadeIn(lab("drafted with Claude · adopted by me", -1.4, -2.3, size=38), scale=0.7), slide_in(rith, RIGHT, 1.0), rt=0.45)
        self.wait(0.7)
        P(self, slide_out(rith, RIGHT, 1.0), rt=0.35)
        done(self)


def board_with_clip(n_done):
    cl = checklist(n_done)
    clip = RoundedRectangle(width=1.4, height=0.34, corner_radius=0.08, fill_color=DARK_L, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([0, 2.72, 0])
    return cl, clip


class B19_Trust(Scene):
    def construct(self):
        plain(self)
        cl, clip = board_with_clip(0)
        ring = row_ring(0)
        self.add(cl, clip, ring)
        at(self, "every test passes")
        P(self, FadeIn(key("135 tests", -3.6, -1.3, size=50), scale=0.7), Create(check(-1.5, -1.3, s=0.26, color=TERRA, w=9)), rt=0.4)
        at(self, "dated results")
        num = T("+0.32", 46, INK, bold=True).move_to([0.9, -1.3, 0])
        fo = folder(4.2, -1.3, w=1.9, h=1.3)
        P(self, FadeIn(num, scale=0.7), FadeIn(fo, shift=LEFT * 0.3), rt=0.35)
        P(self, GrowArrow(arrow([1.75, -1.3, 0], [3.2, -1.3, 0])), FadeIn(lab("dated results folder", 3.4, -2.55, size=38, bold=True), scale=0.7), rt=0.35)
        at(self, "met", lead=0.5)
        stamp(self, cl, 0)
        done(self)


class B20_Length(Scene):
    def construct(self):
        plain(self)
        cl, clip = board_with_clip(1)
        ring = row_ring(1)
        self.add(cl, clip, ring)
        hs = [0.9, 0.5, 1.3, 0.7, 1.1, 0.4]
        pages = VGroup(*[Rectangle(width=0.42, height=h, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-5.4 + k * 0.6, -2.4 + h / 2, 0]) for k, h in enumerate(hs)])
        at(self, "shortest passages")
        P(self, FadeIn(pages, shift=UP * 0.3), rt=0.35)
        order = sorted(range(6), key=lambda k: hs[k])
        P(self, *[pages[k].animate.move_to([-5.4 + i * 0.6, -2.4 + hs[k] / 2, 0]) for i, k in enumerate(order)], rt=0.6)
        P(self, FadeIn(lab("shortest first", -3.9, -0.55, size=36, bold=True), scale=0.7), rt=0.3)
        floor = Line([0.6, -2.4, 0], [5.6, -2.4, 0], color=INK, stroke_width=4)
        b1 = Rectangle(width=1.2, height=1.55, fill_color=BAR2, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([1.9, -2.4 + 0.775, 0])
        b2 = Rectangle(width=1.2, height=1.25, fill_color=BAR3, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([4.3, -2.4 + 0.625, 0])
        at(self, "beats random")
        P(self, Create(floor), GrowFromEdge(b1, DOWN), GrowFromEdge(b2, DOWN), FadeIn(lab("shortest first", 1.9, -2.85, size=32, bold=True)), FadeIn(lab("random", 4.3, -2.85, size=32, bold=True)), rt=0.45)
        at(self, "small margin")
        br = VGroup(DashedLine([3.5, -0.85, 0], [5.3, -0.85, 0], color=INK, stroke_width=4, dash_length=0.12),
                    Line([5.1, -1.15, 0], [5.1, -0.85, 0], color=INK, stroke_width=4))
        P(self, Create(br), FadeIn(lab("small margin", 4.3, -0.4, size=36, bold=True), scale=0.7), rt=0.35)
        at(self, "they are provisional")
        stamp(self, cl, 1)
        done(self)


class B21_DenseVsBM25(Scene):
    def construct(self):
        plain(self)
        cl, clip = board_with_clip(2)
        ring = row_ring(2)
        self.add(cl, clip, ring)
        at(self, "interval is above")
        axis = Line([-5.8, -0.95, 0], [1.2, -0.95, 0], color=INK, stroke_width=4)
        zero = VGroup(Line([-4.9, -1.15, 0], [-4.9, -0.75, 0], color=INK, stroke_width=4), lab("0", -4.9, -1.5, size=36, bold=True))
        P(self, Create(axis), FadeIn(zero), FadeIn(lab("95% interval", -2.6, -1.5, size=38, bold=True), scale=0.7), rt=0.4)
        at(self, "recall but", lead=1.4)
        whisk = VGroup(Line([-1.4, -0.55, 0], [0.4, -0.55, 0], color=INK, stroke_width=6),
                       Line([-1.4, -0.75, 0], [-1.4, -0.35, 0], color=INK, stroke_width=6), Line([0.4, -0.75, 0], [0.4, -0.35, 0], color=INK, stroke_width=6),
                       Dot([-0.5, -0.55, 0], radius=0.13, color=TERRA))
        P(self, FadeIn(whisk, scale=0.8), FadeIn(key("+0.32 recall", -3.2, -0.35, size=44), scale=0.7), rt=0.4)
        mc = meaning_librarian(4.9, -3.4, h=2.3)
        P(self, slide_in(mc, RIGHT, 1.0), rt=0.4)
        at(self, "near misses")
        iso, l1, l2, l3 = corpus_stack(-4.9, -3.35, s=0.42)
        P(self, FadeIn(VGroup(l1, l2, l3), shift=UP * 0.3), FadeIn(lab("BM25's near-misses", -1.1, -2.75, size=36, bold=True), scale=0.7), rt=0.45)
        at(self, "flatters")
        cone = Polygon([3.3, 0.0, 0], [4.2, -3.4, 0], [5.7, -3.4, 0], fill_color=GHOST, fill_opacity=0.6, stroke_width=0).set_z_index(-1)
        P(self, FadeIn(cone), FadeIn(lab("flatters dense models", 1.5, -1.75, size=36, bold=True), scale=0.7), rt=0.4)
        stamp(self, cl, 2)
        P(self, slide_out(mc, RIGHT, 1.0), FadeOut(cone), rt=0.35)
        done(self)


class B22_HumanVsAgent(Scene):
    def construct(self):
        plain(self)
        cl, clip = board_with_clip(3)
        ring = row_ring(3)
        self.add(cl, clip, ring)
        xs = [-4.6, -1.55, 1.55, 4.6]
        names = ["BM25", "bge-small", "e5-small", "hybrid"]
        scales = [balance(x, -0.95, w=1.9, s=0.7) for x in xs]
        nm = VGroup(*[lab(n, x, -2.45, size=32, bold=True) for n, x in zip(names, xs)])
        self.add(*scales, nm)
        at(self, "came out ahead")
        P(self, LaggedStart(*[tip(s_, 0.2) for s_ in scales], lag_ratio=0.2), rt=0.8)
        at(self, "five points")
        b5 = lab("5 points · keyword search", -3.3, -0.2, size=34, bold=True)
        P(self, FadeIn(b5, scale=0.7), FadeIn(Dot([xs[0], -0.55, 0], radius=0.08, color=TERRA)), rt=0.45)
        at(self, "about one point")
        b1 = lab("about 1 point · meaning-based", 3.0, -0.2, size=34, bold=True)
        P(self, FadeIn(b1, scale=0.7), FadeIn(Dot([1.55, -0.55, 0], radius=0.08, color=TERRA)), rt=0.45)
        at(self, "too small")
        qm = T("?", 56, INK, bold=True).move_to([3.05, -1.3, 0])
        P(self, FadeIn(qm, scale=0.6), FadeIn(lab("too small to call for e5", 1.55, -3.0, size=32, bold=True), scale=0.7), rt=0.4)
        stamp(self, cl, 3)
        done(self)


class BOUT_Close(Scene):
    def construct(self):
        plain(self)
        cl, clip = board_with_clip(4)
        allv = VGroup(cl, clip)
        self.add(allv)
        chips = VGroup(*[chip(v, 0, 2.3, size=32) for v in VERDICTS]).arrange(RIGHT, buff=0.3).move_to([0, 2.3, 0])
        at(self, "it worked if")
        P(self, FadeOut(allv, shift=UP * 0.3), FadeIn(chips, shift=UP * 0.3), rt=0.45)
        P(self, FadeIn(key("worked if", -4.1, 1.3, size=46), scale=0.7), rt=0.3)
        at(self, "numbers reproduce")
        r1 = VGroup(check(-5.9, 0.6, s=0.17, color=INK, w=7), T("numbers reproduce", 36, INK, bold=True).move_to([0, 0.6, 0]).align_to(np.array([-5.55, 0, 0]), LEFT))
        P(self, FadeIn(r1, shift=RIGHT * 0.3), rt=0.35)
        at(self, "limits are stated")
        r2 = VGroup(check(-5.9, 0.0, s=0.17, color=INK, w=7), T("limits stated", 36, INK, bold=True).move_to([0, 0.0, 0]).align_to(np.array([-5.55, 0, 0]), LEFT))
        P(self, FadeIn(r2, shift=RIGHT * 0.3), rt=0.35)
        at(self, "it failed if")
        P(self, FadeIn(key("failed if", 0.7, 1.3, size=46), scale=0.7), rt=0.35)
        at(self, "fixed corpus erases")
        P(self, FadeIn(lab("fixed corpus erases\nthe dense advantage", 0.7, 0.3, size=34, bold=True), scale=0.7), rt=0.4)
        at(self, "next ill build")
        iso = Iso(4.05, -0.35, 0.42)
        dashed = VGroup(*[DashedVMobject(f.copy().set_fill(opacity=0), num_dashes=14) for f in iso.box(0, 0, 0, 2.0, 1.4, 1.1)])
        P(self, FadeIn(key("next", 4.5, 1.3, size=46), scale=0.7), Create(dashed), FadeIn(lab("fixed corpus", 4.5, -0.75, size=36, bold=True), scale=0.7), rt=0.4)
        P(self, FadeIn(iso.box(0, 0, 0, 2.0, 1.4, 1.1)), FadeOut(dashed), rt=0.35)
        title = key("Agentic Retrieval Lab", 0, -1.75, size=60)
        rule = Line([-1.5, -2.3, 0], [1.5, -2.3, 0], color=INK, stroke_width=4)
        name = lab("Rithika Sankar Rajeswari · github.com/rithika-sr", 0.4, -2.8, size=36)
        P(self, FadeIn(title, scale=0.85), FadeIn(rule), FadeIn(name), slide_in(me(-5.6, -3.4, h=1.5), LEFT, 0.8), rt=0.5)
        done(self)
