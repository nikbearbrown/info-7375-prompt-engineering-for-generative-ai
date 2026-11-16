"""
Manim scenes for show-tell-five-true-or-false (show-tell skill). Film 2 of "How to take Professor Bear's exams":
the multiple-answer question, five true-or-false statements in one.

SHOW-TELL: every beat is ONE drawn isometric illustration in the Claude palette, at most a few words of label,
and Liam's narration does the explaining. The ISO KIT block below is the skill's shared drawing kit
(brutalist.art/skills/make/show-tell/templates/iso_kit.py), pasted, not imported, because Gate A copies only scenes.py.
The midpoint guard (ST / guard, _END = 0.15) comes from the sibling show-tell films. No person is drawn anywhere.
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
# Added 2026-10-07 from Bear's two reference drawings: a quill drawing a branching outline on a
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


# ═════════════════════════════ PROFESSOR BEAR (a person is never an icon) ═════════════════════════════
# PROFESSOR BEAR LAW (Bear, 2026-10-07): when a beat needs an icon of a person, or Professor Bear himself,
# do not draw a person token and do not pull a person icon. Show one of the Professor Bear portraits in
# brutalist.art/professor-bear/, chosen at random among those of the right aspect ratio (1x1 · 2x3 · 16x9).
# `./art bear <ratio> --seed <beat>` picks the same way from the shell.
def _pb_dir():
    env = _os.environ.get("ART_HOME")
    cands = [env and _os.path.join(env, "professor-bear")]
    here = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(8):
        cands.append(_os.path.join(here, "brutalist.art", "professor-bear"))
        cands.append(_os.path.join(here, "professor-bear"))
        here = _os.path.dirname(here)
    cands.append("/Users/bear/Documents/CoWork/bear-textbooks/books/brutalist.art/professor-bear")
    for c in cands:
        if c and _os.path.isdir(c):
            return c
    return cands[-1]


_PB_RATIOS = {"1x1": (1.0, 287), "2x3": (2 / 3, 46), "16x9": (16 / 9, 13)}


def _pb_circle(path):
    """A circular cut (alpha outside the circle), cached beside the set in _crops/. Cropping is fine (Bear, 2026-10-07)."""
    from PIL import Image as _Im, ImageDraw as _Dr
    out_dir = _os.path.join(_os.path.dirname(path), "_crops"); _os.makedirs(out_dir, exist_ok=True)
    out = _os.path.join(out_dir, _os.path.splitext(_os.path.basename(path))[0] + "-circle.png")
    if not _os.path.exists(out):
        im = _Im.open(path).convert("RGBA"); w, h = im.size; s = min(w, h); top = max(0, (h - s) // 3)
        im = im.crop(((w - s) // 2, top, (w - s) // 2 + s, top + s))
        mask = _Im.new("L", (s, s), 0); _Dr.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
        im.putalpha(mask); im.save(out)
    return out


def professor_bear(ratio="2x3", height=3.0, seed=None, x=0.0, y=0.0, frame=True, shape="rect"):
    """A Professor Bear portrait (random within `ratio`; `seed` = the beat id for a stable pick across re-renders).
    Returns a Group: kraft drop shadow, the photo, an ink frame. Place with `x, y`; size with `height`.
    `shape="circle"` gives a round cut (use a 1x1 portrait). Cropping is fine: circle, rounded square, tight head shot."""
    import random as _random
    ar, n = _PB_RATIOS[ratio]
    k = _random.Random(str(seed) if seed is not None else None).randint(1, n)
    path = _os.path.join(_pb_dir(), f"professor-bear-{ratio}-{k:02d}.png")
    circle = shape == "circle"
    if circle:
        ar = 1.0
    w = height * ar
    if circle:
        shadow = Circle(radius=height / 2, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
        border = Circle(radius=height / 2, stroke_color=INK, stroke_width=4, fill_opacity=0).move_to([x, y, 0])
    else:
        shadow = Rectangle(width=w, height=height, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
        border = Rectangle(width=w, height=height, stroke_color=INK, stroke_width=4, fill_opacity=0).move_to([x, y, 0])
    try:
        img = ImageMobject(_pb_circle(path) if circle else path)
        img.height = height
        img.move_to([x, y, 0])
    except Exception:
        img = Rectangle(width=w, height=height, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    g = Group(shadow, img, border) if frame else Group(img)
    g.path = path
    return g


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



# ─────────────── midpoint guard: GATE T and Gate V sample each clip at its midpoint ───────────────
class ST:
    """No animation straddles the clip midpoint: one that would cross it is shortened to land before
    it, or starts just after it, so the midpoint frame is always a still. Attached to every beat class
    at the bottom of this file (run.sh finds scenes only by the literal `(Scene)`)."""
    def play(self, *anims, **kw):
        if not all(isinstance(a, Wait) for a in anims):
            kw["run_time"] = guard(self, float(kw.get("run_time", 1.0)))
        return Scene.play(self, *anims, **kw)


def guard(self, rt):
    """If an animation of length rt starting now would straddle the midpoint, shorten it to land before
    the midpoint or wait until just after it. Returns the run time to use."""
    tgt = _TARGET.get(type(self).__name__.split("_")[0], 0)
    if not tgt:
        return rt
    mid, t0 = tgt / 2.0, _elapsed(self)
    M = 0.22                                     # margin: frame rounding drifts the real clip clock
    if t0 < mid + M and t0 + rt > mid - M:
        room = mid - M - t0
        if room >= 0.6 * rt and room > 0.25:
            return room
        Scene.wait(self, max(0.02, mid + M - t0))
    return rt


_SLACK = {}     # per-beat extra end slack, if a 4K clip still runs past its audio (BUILD-LOG)
_END = 0.15      # base end slack: every guarded wait/play rounds UP to whole frames at 24 fps (sibling film, BUILD-LOG)


def done(self):
    """finish() plus a pacing report (a clip must not outrun its audio: compile centre-cuts it)."""
    bid = type(self).__name__.split("_")[0]
    t = _elapsed(self)
    tgt = _TARGET.get(bid, 0)
    print(f"[pace] {bid} content={t:.2f}s target={tgt:.2f}s" + ("  OVER" if t > tgt - 0.1 else ""))
    if tgt:
        self.wait(max(0.05, tgt - t - _END - _SLACK.get(bid, 0.0)))     # end ~0.15 s under the audio (24 fps frame rounding)
    else:
        self.wait(2.0)



# ═════════════════════════════ the film: five true-or-false statements in one ═════════════════════════════
# CAST (kept for the whole film): the QUESTION CARD (a paper with five rows A to E, each a letter, a box and a scribbled line that
# stands for the statement), the COIN (one point, kraft disc with one terracotta dot), the TRAY (an open kraft box: the score),
# the word SLAB (a term or a word of a sentence), the dark TOOL BLOCK (an AI tool), the INK check and cross.
# No person is drawn anywhere. The statements are read aloud; on screen they are only scribbled lines (labels only).
DEV_EDGE = "#917A55"      # dark kraft outline, SMALL objects only (GATE T counts grey < 120 as text)
DEEP = "#9C8462"          # deep kraft: cables
AG_TOP, AG_L, AG_R = "#2E2A26", "#1B1815", "#141210"   # tool block, darker than DARK_*
GHOST_FILL, GHOST_OUT = "#E4E1D8", "#B4AFA6"


def lbl(s, x, y, size=40):
    return T(s, size).move_to([x, y, 0])


def lbl_l(s, xl, y, size=40):
    """A label whose LEFT edge sits at x = xl."""
    t = T(s, size)
    return t.move_to([xl + t.width / 2.0, y, 0])


def lbl_r(s, xr, y, size=40):
    t = T(s, size)
    return t.move_to([xr - t.width / 2.0, y, 0])


def cross(x, y, s=0.24, w=9):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def rig_at(cx, cy, s, w, d):
    return Iso(cx - (w - d) * C30 * s / 2.0, cy - (w + d) * 0.5 * s / 2.0, s)


def coin(x, y, k=1.0):
    b = Ellipse(width=0.62 * k, height=0.36 * k, fill_color=BOX_L, fill_opacity=1, stroke_color=DEV_EDGE, stroke_width=3).move_to([x, y - 0.09 * k, 0])
    t = Ellipse(width=0.62 * k, height=0.36 * k, fill_color=BOX_TOP, fill_opacity=1, stroke_color=DEV_EDGE, stroke_width=3).move_to([x, y, 0])
    d = Dot([x, y, 0], radius=0.07 * k, color=TERRA)
    g = VGroup(b, t, d)
    g.set_z_index(2)
    return g


def tray(cx, cy, s=0.8, w=2.6, d=1.6, h=0.9):
    i = rig_at(cx, cy, s, w, d)
    back, front = i.open_box(0, 0, 0, w, d, h)
    back.set_z_index(0)
    front.set_z_index(3)
    land = i.p(w / 2.0, d / 2.0, 0.3)
    return back, front, np.array([land[0], land[1], 0.0])


TRAY_OFFS = [(-0.5, 0.0), (0.0, 0.12), (0.5, 0.0), (-0.22, -0.16), (0.28, -0.16)]


class QC:
    """The question card: a paper, and per row a letter, a box and a scribbled line (the statement)."""
    def __init__(self, cx=-2.5, cy=0.1, w=6.4, h=5.0, rows=5, gap=0.92, lens=None):
        self.cx, self.cy, self.w, self.h = cx, cy, w, h
        self.pg = paper(cx, cy, w, h)
        top = cy + gap * (rows - 1) / 2.0
        self.ys = [top - gap * i for i in range(rows)]
        self.bx = cx - w / 2.0 + 1.25
        self.lx = cx - w / 2.0 + 0.65
        base = w - 2.9
        lens = lens or [1.0, 0.88, 1.0, 0.8, 0.92]
        self.letters, self.boxes, self.lines, self.rows = [], [], [], []
        for i, y in enumerate(self.ys):
            lt = T("ABCDE"[i], 40).move_to([self.lx, y, 0])
            bx = Square(0.5, fill_color="#FFFFFF", fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([self.bx, y, 0])
            ln = scribble(self.bx + 0.6, y, base * lens[i])
            g = VGroup(lt, bx, ln)
            g.set_z_index(1)
            self.letters.append(lt); self.boxes.append(bx); self.lines.append(ln); self.rows.append(g)
        self.line_end = self.bx + 0.6 + base

    def mark(self, i, s=0.16, w=7):
        return check(self.bx, self.ys[i], s, INK, w).set_z_index(2)

    def cross_at(self, i, x=None, s=0.2, w=8):
        return cross(self.cx + self.w / 2.0 - 0.5 if x is None else x, self.ys[i], s, w).set_z_index(2)

    def coin_at(self, i, x):
        return coin(x, self.ys[i])

    def add_all(self, scene, marks=()):
        scene.add(self.pg, *self.rows)
        ms = []
        for i in marks:
            m = self.mark(i)
            scene.add(m)
            ms.append(m)
        return ms


# ═════════════════════════════ B00: five statements ═════════════════════════════
class B00_FiveStatements(Scene):
    def construct(self):
        q = QC()
        self.play(FadeIn(q.pg, shift=DOWN * 0.3), run_time=0.6, rate_func=ease_in)
        until(self, "lettered A to E", lead=0.4)
        for r in q.rows:
            self.play(FadeIn(r, shift=RIGHT * 0.25), run_time=0.3)
        until(self, "Each statement is true", lead=0.2)
        self.play(FadeIn(lbl_l("statement", 1.25, q.ys[1])), run_time=0.4)
        until(self, "You check the ones", lead=0.2)
        for i in (0, 2, 3):
            self.play(Create(q.mark(i)), run_time=0.3)
        self.play(FadeIn(lbl_l("checked", 1.25, q.ys[2])), run_time=0.4)
        done(self)



# ═════════════════════════════ B00A: the exam is on paper ═════════════════════════════
def pen_obj(x, y, length=2.4, tilt=0.0):
    """A pen lying on the desk: an ink barrel with a kraft cap end. Returns a VGroup; `.tip` is the nib end."""
    a = np.array([x - length / 2.0, y, 0.0]); b = np.array([x + length / 2.0, y, 0.0])
    barrel = Line(a, b, color=INK, stroke_width=26)
    cap = Line(a, a + np.array([0.7, 0.0, 0.0]), color=BOX_L, stroke_width=26)
    g = VGroup(barrel, cap)
    g.tip = b
    g.set_z_index(3)
    return g


def pencil_obj(x, y, length=2.4):
    a = np.array([x - length / 2.0, y, 0.0]); b = np.array([x + length / 2.0, y, 0.0])
    body = Line(a, b - np.array([0.35, 0.0, 0.0]), color=BOX_R, stroke_width=26)
    tip = Polygon(b - np.array([0.35, 0.18, 0.0]), b, b - np.array([0.35, -0.18, 0.0]), fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=3)
    g = VGroup(body, tip)
    g.set_z_index(3)
    return g




# ═════════════════════════════ B01: one point each ═════════════════════════════
class B01_OnePointEach(Scene):
    def construct(self):
        q = QC()
        q.add_all(self)
        bk, fr, land = tray(4.6, -1.5)
        until(self, "worth one point", lead=1.1)
        cs = [q.coin_at(i, 1.45) for i in range(5)]
        for c in cs:
            self.play(FadeIn(c, shift=UP * 0.2), run_time=0.15)
        self.play(FadeIn(lbl_l("1 point", 2.1, q.ys[0])), FadeIn(bk), FadeIn(fr), run_time=0.4)
        until(self, "So the whole question", lead=0.4)
        for k, c in enumerate(cs):
            tgt = np.array([land[0] + TRAY_OFFS[k][0], land[1] + TRAY_OFFS[k][1], 0.0])
            self.play(c.animate.move_to(tgt), run_time=0.2)
        self.play(FadeIn(T("5", 150, INK, True).move_to([4.6, 1.5, 0])), run_time=0.3)
        done(self)


# ═════════════════════════════ B02: the two ways to score ═════════════════════════════
GX, GY, GS = (-0.5, 1.9), (0.75, -1.35), 1.9


def cell(x, y):
    return Square(GS, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])


class B02_TwoCases(Scene):
    def construct(self):
        cells = [[cell(GX[c], GY[r]) for c in range(2)] for r in range(2)]
        for r in range(2):
            for c in range(2):
                self.add(cells[r][c])
        self.play(FadeIn(lbl("checked", GX[0], 2.35)), FadeIn(lbl("unchecked", GX[1], 2.35)),
                  FadeIn(lbl_r("true", -1.75, GY[0])), FadeIn(lbl_r("false", -1.75, GY[1])), run_time=0.6)
        until(self, "You checked it", lead=0.2)
        c1 = coin(GX[0], GY[0], 1.8)
        self.play(FadeIn(c1, shift=DOWN * 0.3), run_time=0.5, rate_func=ease_in)
        until(self, "Or you left it unchecked", lead=0.2)
        c2 = coin(GX[1], GY[1], 1.8)
        self.play(FadeIn(c2, shift=DOWN * 0.3), run_time=0.5, rate_func=ease_in)
        until(self, "In every other case", lead=0.2)
        self.play(Create(cross(GX[1], GY[0], 0.4, 9)), Create(cross(GX[0], GY[1], 0.4, 9)), run_time=0.6)
        done(self)


# ═════════════════════════════ B03: five small decisions ═════════════════════════════
class B03_FiveDecisions(Scene):
    def construct(self):
        xs = [-5.0, -3.8, -2.6, -1.4, -0.2]
        cs = [coin(x, 0.9, 1.5) for x in xs]
        for c in cs:
            self.add(c)
        bk, fr, land = tray(3.8, -1.2)
        self.play(FadeIn(bk), FadeIn(fr), FadeIn(lbl("5 coins", -2.6, 2.2)), run_time=0.5)
        until(self, "Get one statement wrong", lead=0.1)
        self.play(Create(cross(xs[2], 0.9, 0.42, 10).set_z_index(5)), run_time=0.5)
        self.play(cs[2].animate.set_opacity(0.25), FadeIn(lbl("missed", xs[2], -0.3)), run_time=0.4)
        until(self, "still keep the other four", lead=0.2)
        k = 0
        for j in (0, 1, 3, 4):
            tgt = np.array([land[0] + TRAY_OFFS[k][0], land[1] + TRAY_OFFS[k][1], 0.0])
            self.play(cs[j].animate.move_to(tgt), run_time=0.3)
            k += 1
        self.play(FadeIn(T("4", 150, INK, True).move_to([3.8, 1.9, 0])), run_time=0.4)
        done(self)


# ═════════════════════════════ B04: an example, A to C ═════════════════════════════


# ═════════════════════════════ B05: the two false ones, and the score ═════════════════════════════


# ═════════════════════════════ B06: a vocabulary test ═════════════════════════════


# ═════════════════════════════ B07: the wrong word in a prompt ═════════════════════════════
def slip(x, y, n=2):
    r = RoundedRectangle(width=1.5, height=0.9, corner_radius=0.08, fill_color=BOX_TOP, fill_opacity=1, stroke_color=DEV_EDGE, stroke_width=3).move_to([x, y, 0])
    ls = VGroup(*[scribble(x - 0.5, y + 0.12 - 0.28 * j, 1.0 - 0.3 * j) for j in range(n)])
    g = VGroup(r, ls)
    g.set_z_index(2)
    return g


def tool_block(cx, cy, s=0.9):
    i = rig_at(cx, cy, s, 1.4, 1.4)
    b = i.box(0, 0, 0, 1.4, 1.4, 0.8, AG_TOP, AG_L, AG_R)
    lamp = Dot(i.p(0.7, 0.7, 0.8), radius=0.08, color=GHOST).set_z_index(3)
    return VGroup(b), lamp


def mini_page(x, y, w=1.1, h=1.4, tilt=0.0, n=3, lens=(1.0, 0.8, 0.6)):
    pg = paper(x, y, w, h, tilt)
    ls = scribble_block(x - w / 2 + 0.2, y + h / 2 - 0.33, w - 0.4, n=n, gap=0.3, last=0.6)
    if abs(tilt) > 1e-3:
        ls.rotate(tilt, about_point=[x, y, 0])
    g = VGroup(pg, ls)
    g.set_z_index(2)
    return g




# ═════════════════════════════ B08: sharp words, direct and check ═════════════════════════════


# ═════════════════════════════ B09: no pattern in how many are true ═════════════════════════════
def mini_card(x, y, marks):
    pg = paper(x, y, 2.0, 3.0)
    bs = VGroup(*[Square(0.34, fill_color="#FFFFFF", fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y + 1.0 - 0.5 * j, 0]) for j in range(5)])
    ms = VGroup(*[check(x, y + 1.0 - 0.5 * j, 0.1, INK, 5) for j in marks])
    g = VGroup(pg, bs, ms)
    g.set_z_index(1)
    return g


class B09_NoPattern(Scene):
    def construct(self):
        xs = [-4.8, -1.6, 1.6, 4.8]
        pats = [[], [0], [0, 2, 4], [0, 1, 2, 3, 4]]
        until(self, "Do not hunt", lead=0.4)
        cards = [mini_card(x, 0.3, p) for x, p in zip(xs, pats)]
        for c in cards:
            self.play(FadeIn(c, shift=DOWN * 0.4), run_time=0.35, rate_func=ease_in)
        for n, x in enumerate(xs):
            self.add(lbl(str(len(pats[n])), x, -1.7, 48))
        self.play(FadeIn(lbl("no pattern", 0.0, 2.7, 64)), run_time=0.5)
        done(self)


# ═════════════════════════════ B10: the one word ═════════════════════════════
def sentence(y, widths, odd=None, x0=-3.9, fill=BOX_TOP, odd_fill=BAR2, gap=0.24, h=0.6):
    xs, x = [], x0
    slabs = []
    for k, w in enumerate(widths):
        f = odd_fill if (odd is not None and k == odd) else fill
        r = RoundedRectangle(width=w, height=h, corner_radius=0.06, fill_color=f, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x + w / 2.0, y, 0])
        slabs.append(r)
        xs.append(x + w / 2.0)
        x += w + gap
    g = VGroup(*slabs)
    g.set_z_index(1)
    return g, xs


W10 = [1.1, 0.8, 1.5, 0.9, 1.3]


class B10_OneWord(Scene):
    def construct(self):
        l1, xs = sentence(1.0, W10)
        l2, _ = sentence(-0.8, W10, odd=2)
        self.play(FadeIn(l1, shift=DOWN * 0.3), run_time=0.5)
        until(self, "wrong statements are plausible", lead=0.2)
        self.play(FadeIn(l2, shift=DOWN * 0.3), run_time=0.5)
        until(self, "one word that changes", lead=0.4)
        ring = Ellipse(width=2.0, height=1.0, color=INK, stroke_width=6).move_to([xs[2], -0.8, 0]).set_z_index(5)
        self.play(Create(ring), run_time=0.5)
        self.play(FadeIn(lbl("one word", xs[2], -1.8)), Create(check(5.0, 1.0, 0.26, INK, 9)), Create(cross(5.0, -0.8, 0.26, 9)), run_time=0.5)
        done(self)


# ═════════════════════════════ B11: always and never are not clues ═════════════════════════════
class B11_SignalWords(Scene):
    def construct(self):
        sa = RoundedRectangle(width=2.0, height=0.8, corner_radius=0.08, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-2.4, 1.6, 0])
        sn = RoundedRectangle(width=2.0, height=0.8, corner_radius=0.08, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([2.4, 1.6, 0])
        self.add(sa, sn)
        self.play(FadeIn(lbl("always", -2.4, 0.75)), FadeIn(lbl("never", 2.4, 0.75)), run_time=0.5)
        until(self, "not a reliable sign", lead=0.8)
        self.play(Create(cross(-2.4, 1.6, 0.55, 10).set_z_index(5)), Create(cross(2.4, 1.6, 0.55, 10).set_z_index(5)), run_time=0.6)
        until(self, "Judge the claim", lead=0.2)
        ln, xs = sentence(-1.0, W10, x0=-3.9)
        self.play(FadeIn(ln, shift=DOWN * 0.3), run_time=0.4)
        ring = RoundedRectangle(width=7.3, height=1.1, corner_radius=0.2, color=INK, stroke_width=6).move_to([-0.4, -1.0, 0]).set_z_index(5)
        self.play(Create(ring), run_time=0.5)
        self.play(Create(check(4.9, -1.0, 0.28, INK, 9)), FadeIn(lbl("claim", -0.4, -2.0)), run_time=0.4)
        done(self)


# ═════════════════════════════ B12: the glossary ═════════════════════════════


# ═════════════════════════════ B13: cold ═════════════════════════════
class B13_Cold(Scene):
    def construct(self):
        q = QC(cx=-2.8, cy=0.3)
        q.add_all(self)
        stack = VGroup(paper(4.6, 0.3, 2.0, 2.6, 0.08), paper(4.5, 0.4, 2.0, 2.6, -0.05), paper(4.6, 0.5, 2.0, 2.6, 0.03), scribble_block(3.85, 1.55, 1.5, n=4, gap=0.4, last=0.6, color=BAR1, sw=5))
        stack.set_z_index(2)
        self.play(FadeIn(stack, shift=DOWN * 0.3), FadeIn(lbl("cold", -2.8, -2.85, 48)), run_time=0.5)
        pc = pencil_obj(1.7, -1.2, 1.8)
        until(self, "mark it by hand", lead=0.3)
        self.play(FadeIn(pc, shift=LEFT * 0.3), run_time=0.3)
        for i in (0, 1, 2, 3):
            self.play(Create(q.mark(i)), run_time=0.2)
        until(self, "before you look", lead=0.1)
        self.play(Create(cross(4.6, 0.5, 0.6, 11).set_z_index(6)), FadeIn(lbl("notes", 4.6, -1.7, 48)), run_time=0.5)
        done(self)


# ═════════════════════════════ B14: the key and the reasons ═════════════════════════════
class B14_KeyAndReasons(Scene):
    def construct(self):
        q = QC(cx=-3.7, cy=0.0, w=4.6, h=4.8, gap=0.9)
        q.add_all(self, marks=(0, 1, 4))
        ks = paper(3.2, 0.0, 5.2, 4.8)
        ks.set_z_index(0)
        ys = q.ys
        keymarks = [check(1.35, ys[0], 0.16, INK, 7), check(1.35, ys[1], 0.16, INK, 7), check(1.35, ys[2], 0.16, INK, 7),
                    cross(1.35, ys[3], 0.16, 7), cross(1.35, ys[4], 0.16, 7)]
        reasons = [scribble(1.8, y, 3.3 - 0.25 * (n % 3)) for n, y in enumerate(ys)]
        for r in reasons:
            r.set_z_index(2)
        until(self, "Then submit your attempt", lead=0.1)
        self.play(FadeIn(ks, shift=LEFT * 0.5), FadeIn(lbl("feedback", 3.2, 2.9)), run_time=0.6)
        for m in keymarks:
            m.set_z_index(2)
        self.play(*[Create(m) for m in keymarks], run_time=0.5)
        until(self, "feedback for every statement", lead=0.1)
        for r in reasons:
            self.play(Create(r), run_time=0.25)
        self.play(FadeIn(lbl("reason", 3.2, -2.9)), run_time=0.4)
        until(self, "Especially the ones you got wrong", lead=0.2)
        for i in (2, 4):
            self.play(Create(RoundedRectangle(width=4.6, height=0.74, corner_radius=0.15, color=INK, stroke_width=5).move_to([3.2, ys[i], 0]).set_z_index(5)), run_time=0.4)
        done(self)


# ═════════════════════════════ B15: learn look-alikes in pairs ═════════════════════════════


# ═════════════════════════════ B16: reading it the way you hope ═════════════════════════════
class B16_Hoped(Scene):
    def construct(self):
        real, xs = sentence(-0.9, W10, odd=2)
        self.add(real)
        self.play(FadeIn(lbl("written", 5.0, -0.9)), run_time=0.4)
        until(self, "the way you hope it is", lead=0.3)
        ghost, _ = sentence(1.4, W10, fill=GHOST_FILL)
        for g in ghost:
            g.set_stroke(GHOST_OUT, 3)
        self.play(FadeIn(ghost, shift=DOWN * 0.4), FadeIn(lbl("hoped", 5.0, 1.4)), run_time=0.6)
        until(self, "not the way it is written", lead=0.3)
        self.play(ghost.animate.shift(UP * 0.5).set_opacity(0.0), run_time=0.5)
        ring = Ellipse(width=2.0, height=1.0, color=INK, stroke_width=6).move_to([xs[2], -0.9, 0]).set_z_index(5)
        self.play(Create(ring), run_time=0.5)
        done(self)


# ═════════════════════════════ B17: skipping what looks familiar ═════════════════════════════
class B17_Skipped(Scene):
    def construct(self):
        q = QC()
        q.add_all(self, marks=(0, 1, 3, 4))
        until(self, "skipping a statement", lead=0.1)
        arc = ArcBetweenPoints(np.array([1.5, q.ys[1], 0.0]), np.array([1.5, q.ys[3], 0.0]), angle=-PI * 0.9, color=BAR1, stroke_width=6)
        self.play(Create(arc), FadeIn(lbl_l("skipped", 2.5, q.ys[2])), run_time=0.7)
        until(self, "A familiar word", lead=0.1)
        self.play(Create(q.mark(2)), run_time=0.3)
        ring = RoundedRectangle(width=5.3, height=0.78, corner_radius=0.15, color=INK, stroke_width=5).move_to([q.cx - 0.2, q.ys[2], 0]).set_z_index(5)
        self.play(Create(ring), run_time=0.4)
        self.play(Create(q.cross_at(2)), run_time=0.4)
        done(self)


# ═════════════════════════════ B18: half true is not true ═════════════════════════════
class B18_HalfTrue(Scene):
    def construct(self):
        y = 0.4
        bx = Square(0.6, fill_color="#FFFFFF", fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.6, y, 0])
        left, xs = sentence(y, [1.1, 0.8, 1.5], x0=-2.7)
        right, _ = sentence(y, [0.9, 1.3], x0=1.75, fill=GHOST_FILL)
        for r in right:
            r.set_stroke(GHOST_OUT, 3)
        self.add(bx, left)
        self.play(FadeIn(right, shift=DOWN * 0.3), FadeIn(lbl("half true", 0.3, -1.1)), run_time=0.5)
        until(self, "true only if all", lead=0.9)
        self.play(Create(cross(2.97, y, 0.55, 10).set_z_index(5)), run_time=0.5)
        gc = check(-3.6, y, 0.2, GHOST_OUT, 7).set_z_index(5)
        self.play(Create(gc), run_time=0.3)
        self.play(FadeOut(gc), run_time=0.3)
        done(self)


# ═════════════════════════════ B19: recap ═════════════════════════════


# attach the midpoint guard (see ST); the classes stay literal `(Scene)` for run.sh's scene discovery
for _cls in [v for k, v in list(globals().items()) if isinstance(v, type) and k[:1] == "B" and k[1:3].isdigit() and issubclass(v, Scene)]:
    _cls.play = ST.play
