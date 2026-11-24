"""
iso_kit.py — the show-tell drawing kit. PASTE this block at the top of a reel's scenes.py;
do not import it (Gate A copies only scenes.py into its sandbox).

Drawn isometric objects in the Claude palette: cardboard boxes (closed, open, taped), dark
MCP blocks with ports, flat skill pages, server stacks with lights, checks, a cursor, pills,
and a WRITING KIT (quill, inkwell, paper, scribble lines, branching outline + the write_lines /
grow_tree animations that make the quill write). A PERSON IS NEVER AN ICON: `professor_bear(ratio, …)`
places a random Professor Bear portrait of the right aspect ratio (PROFESSOR BEAR LAW).
Pacing helpers read the reel's beat_sheet.json so scenes wait for their spoken phrase.

Every rule in ../SKILL.md "DRAWING LAWS" is already obeyed by these primitives; keep it that
way when you add one (label beside, never inside; terracotta never under text; dim greys
with gaps for chart blocks; type floor 32).
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


_PB_RATIOS = {"1x1": (1.0, 229), "2x3": (2 / 3, 28), "16x9": (16 / 9, 13)}


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


# ═════════════════════════════ ORIGINAL PROPS (subset of iso_originals_25.py, verbatim data) ═════════════════════════════
_ST_ORIGINALS_25 = {'review-desk': {'parts': {'legs': [{'kind': 'polygon',
                                     'pts': [[0.0, 0.0],
                                             [-0.13856406460551018, -0.08],
                                             [-0.13856406460551018, -1.28],
                                             [0.0, -1.2]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.0, 0.0],
                                             [0.13856406460551018, -0.08],
                                             [0.13856406460551018, -1.28],
                                             [0.0, -1.2]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.0, -1.2],
                                             [0.13856406460551018, -1.28],
                                             [0.0, -1.3599999999999999],
                                             [-0.13856406460551018, -1.28]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -1.25],
                                             [2.026499444855586, -1.33],
                                             [2.026499444855586, -2.5300000000000002],
                                             [2.1650635094610964, -2.45]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -1.25],
                                             [2.303627574066607, -1.33],
                                             [2.303627574066607, -2.5300000000000002],
                                             [2.1650635094610964, -2.45]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -2.45],
                                             [2.303627574066607, -2.5300000000000002],
                                             [2.1650635094610964, -2.6100000000000003],
                                             [2.026499444855586, -2.5300000000000002]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -0.825],
                                             [-1.5675059808498337, -0.9049999999999999],
                                             [-1.5675059808498337, -2.105],
                                             [-1.4289419162443235, -2.025]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -0.825],
                                             [-1.2903778516388136, -0.9049999999999999],
                                             [-1.2903778516388136, -2.105],
                                             [-1.4289419162443235, -2.025]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -2.025],
                                             [-1.2903778516388136, -2.105],
                                             [-1.4289419162443235, -2.1849999999999996],
                                             [-1.5675059808498337, -2.105]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -2.075],
                                             [0.5975575286112628, -2.155],
                                             [0.5975575286112628, -3.3549999999999995],
                                             [0.7361215932167728, -3.2750000000000004]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -2.075],
                                             [0.8746856578222831, -2.1550000000000002],
                                             [0.8746856578222831, -3.3550000000000004],
                                             [0.7361215932167728, -3.2750000000000004]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -3.2750000000000004],
                                             [0.8746856578222831, -3.3550000000000004],
                                             [0.7361215932167731, -3.4349999999999996],
                                             [0.5975575286112628, -3.3549999999999995]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035}],
                           'desktop': [{'kind': 'polygon',
                                        'pts': [[0.0, -1.0999999999999999],
                                                [-1.7320508075688772, -2.0999999999999996],
                                                [-1.7320508075688772, -2.26],
                                                [0.0, -1.2599999999999998]],
                                        'fill': '#DCC9AA',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.0, -1.0999999999999999],
                                                [2.5114736709748717, -2.55],
                                                [2.5114736709748717, -2.71],
                                                [0.0, -1.2599999999999998]],
                                        'fill': '#C7AE86',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.0, -1.2599999999999998],
                                                [2.5114736709748717, -2.71],
                                                [0.7794228634059946, -3.7099999999999995],
                                                [-1.7320508075688772, -2.26]],
                                        'fill': '#F3E9D8',
                                        'stroke': '#3D3929',
                                        'width': 0.035}],
                           'evidence': [{'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.7249999999999999],
                                                 [-0.9093266739736605, -2.475],
                                                 [-0.9093266739736605, -2.545],
                                                 [0.38971143170299744, -1.795]],
                                         'fill': '#ECE7DF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.7249999999999999],
                                                 [1.688749537379655, -2.4749999999999996],
                                                 [1.688749537379655, -2.545],
                                                 [0.38971143170299744, -1.795]],
                                         'fill': '#E2DCD2',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.795],
                                                 [1.688749537379655, -2.545],
                                                 [0.38971143170299716, -3.295],
                                                 [-0.9093266739736605, -2.545]],
                                         'fill': '#FFFFFF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polyline',
                                         'pts': [[0.2598076211353316, -2.0749999999999997],
                                                 [1.212435565298214, -2.625]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[0.0, -2.2249999999999996],
                                                 [0.9526279441628823, -2.7749999999999995]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.2598076211353316, -2.375], [0.6928203230275507, -2.925]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'circle',
                                         'cx': -0.4763139720814413,
                                         'cy': -2.535,
                                         'r': 0.055,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}]},
                 'moves': {'evidence': [1.12583302491977, 0.19999999999999998]}},
 'permission-gate': {'parts': {'base': [{'kind': 'polygon',
                                         'pts': [[0.0, 0.1],
                                                 [-1.299038105676658, -0.6499999999999999],
                                                 [-1.299038105676658, -0.7799999999999999],
                                                 [0.0, -0.03]],
                                         'fill': '#B4AFA6',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, 0.1],
                                                 [2.68467875173176, -1.45],
                                                 [2.68467875173176, -1.58],
                                                 [0.0, -0.03]],
                                         'fill': '#8B8F96',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.03],
                                                 [2.68467875173176, -1.58],
                                                 [1.3856406460551018, -2.33],
                                                 [-1.299038105676658, -0.7799999999999999]],
                                         'fill': '#D9D4C7',
                                         'stroke': '#3D3929',
                                         'width': 0.035}],
                               'posts': [{'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -0.43],
                                                  [-0.8227241335952167, -0.605],
                                                  [-0.8227241335952167, -2.305],
                                                  [-0.5196152422706631, -2.13]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -0.43],
                                                  [-0.2771281292110203, -0.5700000000000001],
                                                  [-0.2771281292110203, -2.27],
                                                  [-0.5196152422706631, -2.13]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -2.13],
                                                  [-0.2771281292110203, -2.27],
                                                  [-0.5802370205355738, -2.4450000000000003],
                                                  [-0.8227241335952167, -2.305]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -1.6800000000000002],
                                                  [1.34233937586588, -1.855],
                                                  [1.34233937586588, -3.555],
                                                  [1.6454482671904334, -3.38]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -1.6800000000000002],
                                                  [1.8879353802500762, -1.8200000000000003],
                                                  [1.8879353802500762, -3.5200000000000005],
                                                  [1.6454482671904334, -3.38]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -3.38],
                                                  [1.8879353802500762, -3.5200000000000005],
                                                  [1.5848264889255228, -3.6950000000000003],
                                                  [1.34233937586588, -3.555]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'circle',
                                          'cx': -0.38105117766515295,
                                          'cy': -1.96,
                                          'r': 0.07,
                                          'fill': '#D97757',
                                          'stroke': 'none',
                                          'width': 0}],
                               'barrier': [{'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.3399999999999999],
                                                    [-0.381051177665153, -1.42],
                                                    [-0.381051177665153, -1.69],
                                                    [-0.2424871130596428, -1.6099999999999999]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.3399999999999999],
                                                    [1.749371315644566, -2.49],
                                                    [1.749371315644566, -2.76],
                                                    [-0.2424871130596428, -1.6099999999999999]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.6099999999999999],
                                                    [1.749371315644566, -2.76],
                                                    [1.6108072510390556, -2.84],
                                                    [-0.381051177665153, -1.69]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035}]},
                     'moves': {'barrier': [0.0, -0.95]}},
 'memory-drawers': {'parts': {'cabinet': [{'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [-1.3856406460551018, -0.8],
                                                   [-1.3856406460551018, -2.8],
                                                   [0.0, -2.0]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [1.7320508075688772, -1.0],
                                                   [1.7320508075688772, -3.0],
                                                   [0.0, -2.0]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -2.0],
                                                   [1.7320508075688772, -3.0],
                                                   [0.34641016151377535, -3.8],
                                                   [-1.3856406460551018, -2.8]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                              'fixed-drawer-0': [{'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.16499999999999998],
                                                          [-0.9266471820493491, -0.8150000000000001],
                                                          [-0.9266471820493491, -1.275],
                                                          [0.19918584287042088, -0.625]],
                                                  'fill': '#B4AFA6',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.16499999999999998],
                                                          [1.7060700454553441, -1.035],
                                                          [1.7060700454553441, -1.495],
                                                          [0.19918584287042088, -0.625]],
                                                  'fill': '#8B8F96',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.625],
                                                          [1.7060700454553441, -1.495],
                                                          [0.580237020535574, -2.145],
                                                          [-0.9266471820493491, -1.275]],
                                                  'fill': '#D9D4C7',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.515],
                                                          [0.6408587988004846, -0.5900000000000001],
                                                          [0.6408587988004846, -0.68],
                                                          [0.7707626093681503, -0.605]],
                                                  'fill': '#26221F',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.515],
                                                          [1.3336791218280355, -0.8400000000000001],
                                                          [1.3336791218280355, -0.93],
                                                          [0.7707626093681503, -0.605]],
                                                  'fill': '#1E1B18',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.605],
                                                          [1.3336791218280355, -0.93],
                                                          [1.2037753112603697, -1.005],
                                                          [0.6408587988004846, -0.68]],
                                                  'fill': '#3A3530',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                              'drawer': [{'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -0.765],
                                                  [-0.9266471820493491, -1.415],
                                                  [-0.9266471820493491, -1.875],
                                                  [0.19918584287042088, -1.2249999999999999]],
                                          'fill': '#B4AFA6',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -0.765],
                                                  [1.7060700454553441, -1.635],
                                                  [1.7060700454553441, -2.0949999999999998],
                                                  [0.19918584287042088, -1.2249999999999999]],
                                          'fill': '#8B8F96',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -1.2249999999999999],
                                                  [1.7060700454553441, -2.0949999999999998],
                                                  [0.580237020535574, -2.745],
                                                  [-0.9266471820493491, -1.875]],
                                          'fill': '#D9D4C7',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.115],
                                                  [0.6408587988004846, -1.19],
                                                  [0.6408587988004846, -1.2799999999999998],
                                                  [0.7707626093681503, -1.2049999999999998]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.115],
                                                  [1.3336791218280355, -1.44],
                                                  [1.3336791218280355, -1.5299999999999998],
                                                  [0.7707626093681503, -1.2049999999999998]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.2049999999999998],
                                                  [1.3336791218280355, -1.5299999999999998],
                                                  [1.2037753112603697, -1.605],
                                                  [0.6408587988004846, -1.2799999999999998]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                              'fixed-drawer-2': [{'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.3649999999999998],
                                                          [-0.9266471820493491, -2.0149999999999997],
                                                          [-0.9266471820493491, -2.4749999999999996],
                                                          [0.19918584287042088, -1.8249999999999997]],
                                                  'fill': '#B4AFA6',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.3649999999999998],
                                                          [1.7060700454553441, -2.235],
                                                          [1.7060700454553441, -2.695],
                                                          [0.19918584287042088, -1.8249999999999997]],
                                                  'fill': '#8B8F96',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.8249999999999997],
                                                          [1.7060700454553441, -2.695],
                                                          [0.580237020535574, -3.3449999999999998],
                                                          [-0.9266471820493491, -2.4749999999999996]],
                                                  'fill': '#D9D4C7',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.715],
                                                          [0.6408587988004846, -1.79],
                                                          [0.6408587988004846, -1.8800000000000001],
                                                          [0.7707626093681503, -1.8050000000000002]],
                                                  'fill': '#26221F',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.715],
                                                          [1.3336791218280355, -2.04],
                                                          [1.3336791218280355, -2.13],
                                                          [0.7707626093681503, -1.8050000000000002]],
                                                  'fill': '#1E1B18',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.8050000000000002],
                                                          [1.3336791218280355, -2.13],
                                                          [1.2037753112603697, -2.205],
                                                          [0.6408587988004846, -1.8800000000000001]],
                                                  'fill': '#3A3530',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                              'cabinet-top': [{'kind': 'polygon',
                                               'pts': [[0.0, -1.96],
                                                       [-1.3856406460551018, -2.76],
                                                       [-1.3856406460551018, -2.88],
                                                       [0.0, -2.08]],
                                               'fill': '#DCC9AA',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -1.96],
                                                       [1.7320508075688772, -2.96],
                                                       [1.7320508075688772, -3.08],
                                                       [0.0, -2.08]],
                                               'fill': '#C7AE86',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -2.08],
                                                       [1.7320508075688772, -3.08],
                                                       [0.34641016151377535, -3.88],
                                                       [-1.3856406460551018, -2.88]],
                                               'fill': '#F3E9D8',
                                               'stroke': '#3D3929',
                                               'width': 0.035}]},
                    'moves': {'drawer': [0.7794228634059948, 0.45]}},
 'task-queue': {'parts': {'rail': [{'kind': 'polygon',
                                    'pts': [[0.0, 0.0],
                                            [-1.299038105676658, -0.75],
                                            [-1.299038105676658, -0.9],
                                            [0.0, -0.15]],
                                    'fill': '#B4AFA6',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, 0.0],
                                            [3.117691453623979, -1.8],
                                            [3.117691453623979, -1.95],
                                            [0.0, -0.15]],
                                    'fill': '#8B8F96',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, -0.15],
                                            [3.117691453623979, -1.95],
                                            [1.818653347947321, -2.6999999999999997],
                                            [-1.299038105676658, -0.9]],
                                    'fill': '#D9D4C7',
                                    'stroke': '#3D3929',
                                    'width': 0.035}],
                          'next-task': [{'kind': 'polygon',
                                         'pts': [[0.0, -0.4],
                                                 [-0.9093266739736605, -0.925],
                                                 [-0.9093266739736605, -1.8250000000000002],
                                                 [0.0, -1.3]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.4],
                                                 [0.7361215932167728, -0.825],
                                                 [0.7361215932167728, -1.725],
                                                 [0.0, -1.3]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.3],
                                                 [0.7361215932167728, -1.725],
                                                 [-0.17320508075688767, -2.25],
                                                 [-0.9093266739736605, -1.8250000000000002]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4100000000000001],
                                                 [-0.7101408311032397, -1.8000000000000003],
                                                 [-0.7101408311032397, -1.87],
                                                 [-0.034641016151377525, -1.4800000000000002]],
                                         'fill': '#ECE7DF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4100000000000001],
                                                 [0.536935750346352, -1.7400000000000002],
                                                 [0.536935750346352, -1.81],
                                                 [-0.034641016151377525, -1.4800000000000002]],
                                         'fill': '#E2DCD2',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4800000000000002],
                                                 [0.536935750346352, -1.81],
                                                 [-0.1385640646055102, -2.2],
                                                 [-0.7101408311032397, -1.87]],
                                         'fill': '#FFFFFF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polyline',
                                         'pts': [[-0.16454482671904325, -1.76],
                                                 [0.060621778264910754, -1.8900000000000001]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.42435244785437487, -1.9100000000000001],
                                                 [-0.19918584287042085, -2.04]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.6841600689897065, -2.06], [-0.45899346400575247, -2.19]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'circle',
                                         'cx': -0.2771281292110204,
                                         'cy': -1.8600000000000003,
                                         'r': 0.055,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}],
                          'waiting-tasks': [{'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -0.96],
                                                     [0.060621778264910754, -1.485],
                                                     [0.060621778264910754, -2.3850000000000002],
                                                     [0.9699484522385713, -1.86]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -0.96],
                                                     [1.706070045455344, -1.385],
                                                     [1.706070045455344, -2.285],
                                                     [0.9699484522385713, -1.86]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -1.86],
                                                     [1.706070045455344, -2.285],
                                                     [0.7967433714816834, -2.81],
                                                     [0.060621778264910754, -2.3850000000000002]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -1.9700000000000002],
                                                     [0.2598076211353316, -2.3600000000000003],
                                                     [0.2598076211353316, -2.43],
                                                     [0.9353074360871938, -2.04]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -1.9700000000000002],
                                                     [1.5068842025849232, -2.3],
                                                     [1.5068842025849232, -2.37],
                                                     [0.9353074360871938, -2.04]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -2.04],
                                                     [1.5068842025849232, -2.37],
                                                     [0.831384387633061, -2.7600000000000002],
                                                     [0.2598076211353316, -2.43]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[0.805403625519528, -2.3200000000000003],
                                                     [1.030570230503482, -2.45]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.5455960043841964, -2.47], [0.7707626093681504, -2.6]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.2857883832488648, -2.62],
                                                     [0.5109549882328188, -2.75]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': 0.6928203230275509,
                                             'cy': -2.42,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -1.5200000000000002],
                                                     [1.0305702305034823, -2.0450000000000004],
                                                     [1.0305702305034823, -2.9450000000000003],
                                                     [1.9398969044771426, -2.4200000000000004]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -1.5200000000000002],
                                                     [2.6760184976939154, -1.9450000000000003],
                                                     [2.6760184976939154, -2.8450000000000006],
                                                     [1.9398969044771426, -2.4200000000000004]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -2.4200000000000004],
                                                     [2.6760184976939154, -2.8450000000000006],
                                                     [1.7666918237202551, -3.3700000000000006],
                                                     [1.0305702305034823, -2.9450000000000003]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.5300000000000002],
                                                     [1.229756073373903, -2.9200000000000004],
                                                     [1.229756073373903, -2.99],
                                                     [1.9052558883257655, -2.6000000000000005]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.5300000000000002],
                                                     [2.476832654823495, -2.8600000000000003],
                                                     [2.476832654823495, -2.9300000000000006],
                                                     [1.9052558883257655, -2.6000000000000005]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.6000000000000005],
                                                     [2.476832654823495, -2.9300000000000006],
                                                     [1.8013328398716326, -3.3200000000000007],
                                                     [1.229756073373903, -2.99]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[1.7753520777580998, -2.8800000000000003],
                                                     [2.0005186827420536, -3.0100000000000002]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[1.515544456622768, -3.0300000000000002],
                                                     [1.740711061606722, -3.16]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[1.2557368354874365, -3.1800000000000006],
                                                     [1.4809034404713903, -3.31]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': 1.6627687752661224,
                                             'cy': -2.9800000000000004,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}]},
                'moves': {'next-task': [-0.1299038105676658, 0.32500000000000007]}},
 'agent-workstation': {'parts': {'foot': [{'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.5],
                                                   [-1.1258330249197703, -1.05],
                                                   [-1.1258330249197703, -1.2],
                                                   [-0.17320508075688767, -0.65]],
                                           'fill': '#B4AFA6',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.5],
                                                   [1.4722431864335455, -1.45],
                                                   [1.4722431864335455, -1.5999999999999999],
                                                   [-0.17320508075688767, -0.65]],
                                           'fill': '#8B8F96',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.65],
                                                   [1.4722431864335455, -1.5999999999999999],
                                                   [0.5196152422706628, -2.15],
                                                   [-1.1258330249197703, -1.2]],
                                           'fill': '#D9D4C7',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                                 'stand': [{'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.21],
                                                    [-0.17320508075688767, -1.36],
                                                    [-0.17320508075688767, -1.9600000000000002],
                                                    [0.08660254037844393, -1.81]],
                                            'fill': '#26221F',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.21],
                                                    [0.34641016151377557, -1.36],
                                                    [0.34641016151377557, -1.9600000000000002],
                                                    [0.08660254037844393, -1.81]],
                                            'fill': '#1E1B18',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.81],
                                                    [0.34641016151377557, -1.9600000000000002],
                                                    [0.08660254037844393, -2.1100000000000003],
                                                    [-0.17320508075688767, -1.9600000000000002]],
                                            'fill': '#3A3530',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                                 'screen': [{'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -1.26],
                                                     [-1.0392304845413263, -1.3599999999999999],
                                                     [-1.0392304845413263, -3.0100000000000002],
                                                     [-0.8660254037844386, -2.91]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -1.26],
                                                     [1.4722431864335457, -2.6100000000000003],
                                                     [1.4722431864335457, -4.26],
                                                     [-0.8660254037844386, -2.91]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -2.91],
                                                     [1.4722431864335457, -4.26],
                                                     [1.299038105676658, -4.36],
                                                     [-1.0392304845413263, -3.0100000000000002]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.7361215932167728, -1.505],
                                                     [1.3596598839415686, -2.715],
                                                     [1.3596598839415686, -4.025],
                                                     [-0.7361215932167728, -2.815]],
                                             'fill': '#FAF9F5',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -1.885],
                                                     [0.7188010851410841, -2.585]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -2.185],
                                                     [0.7188010851410841, -2.885]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -2.4850000000000003],
                                                     [0.7188010851410841, -3.185]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06}],
                                 'tool': [{'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.2000000000000002],
                                                   [1.905255888325765, -1.6],
                                                   [1.905255888325765, -2.1500000000000004],
                                                   [2.598076211353316, -1.7500000000000002]],
                                           'fill': '#26221F',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.2000000000000002],
                                                   [3.334197804570089, -1.6250000000000002],
                                                   [3.334197804570089, -2.1750000000000003],
                                                   [2.598076211353316, -1.7500000000000002]],
                                           'fill': '#1E1B18',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.7500000000000002],
                                                   [3.334197804570089, -2.1750000000000003],
                                                   [2.641377481542538, -2.575],
                                                   [1.905255888325765, -2.1500000000000004]],
                                           'fill': '#3A3530',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'circle',
                                           'cx': 2.9618068809427798,
                                           'cy': -1.6700000000000002,
                                           'r': 0.07,
                                           'fill': '#D97757',
                                           'stroke': 'none',
                                           'width': 0}]},
                       'moves': {'tool': [-0.4763139720814413, 0.575]}},
 'evidence-binder': {'parts': {'back-cover': [{'kind': 'polygon',
                                               'pts': [[0.0, 0.0],
                                                       [-2.424871130596428, -1.4],
                                                       [-2.424871130596428, -1.52],
                                                       [0.0, -0.12]],
                                               'fill': '#26221F',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, 0.0],
                                                       [2.0784609690826525, -1.2],
                                                       [2.0784609690826525, -1.3199999999999998],
                                                       [0.0, -0.12]],
                                               'fill': '#1E1B18',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -0.12],
                                                       [2.0784609690826525, -1.3199999999999998],
                                                       [-0.34641016151377535, -2.7199999999999998],
                                                       [-2.424871130596428, -1.52]],
                                               'fill': '#3A3530',
                                               'stroke': '#3D3929',
                                               'width': 0.035}],
                               'records': [{'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.34],
                                                    [-2.035159698893431, -1.565],
                                                    [-2.035159698893431, -1.635],
                                                    [0.08660254037844387, -0.41000000000000003]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.34],
                                                    [1.7753520777580993, -1.315],
                                                    [1.7753520777580993, -1.385],
                                                    [0.08660254037844387, -0.41000000000000003]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.41000000000000003],
                                                    [1.7753520777580993, -1.385],
                                                    [-0.34641016151377535, -2.6100000000000003],
                                                    [-2.035159698893431, -1.635]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.69],
                                                    [1.299038105676658, -1.465]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -0.8400000000000001],
                                                    [1.0392304845413263, -1.615]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -0.99],
                                                    [0.7794228634059949, -1.765]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.625,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.46],
                                                    [-2.035159698893431, -1.685],
                                                    [-2.035159698893431, -1.7550000000000001],
                                                    [0.08660254037844387, -0.53]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.46],
                                                    [1.7753520777580993, -1.435],
                                                    [1.7753520777580993, -1.5050000000000001],
                                                    [0.08660254037844387, -0.53]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.53],
                                                    [1.7753520777580993, -1.5050000000000001],
                                                    [-0.34641016151377535, -2.7300000000000004],
                                                    [-2.035159698893431, -1.7550000000000001]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.81],
                                                    [1.299038105676658, -1.585]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -0.96],
                                                    [1.0392304845413263, -1.7349999999999999]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -1.1099999999999999],
                                                    [0.7794228634059949, -1.8849999999999998]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.745,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.5800000000000001],
                                                    [-2.035159698893431, -1.8050000000000002],
                                                    [-2.035159698893431, -1.875],
                                                    [0.08660254037844387, -0.65]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.5800000000000001],
                                                    [1.7753520777580993, -1.5550000000000002],
                                                    [1.7753520777580993, -1.625],
                                                    [0.08660254037844387, -0.65]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.65],
                                                    [1.7753520777580993, -1.625],
                                                    [-0.34641016151377535, -2.8500000000000005],
                                                    [-2.035159698893431, -1.875]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.9299999999999999],
                                                    [1.299038105676658, -1.705]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -1.08],
                                                    [1.0392304845413263, -1.855]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -1.23],
                                                    [0.7794228634059949, -2.005]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.865,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0}],
                               'spine': [{'kind': 'polygon',
                                          'pts': [[0.0, -0.12],
                                                  [-2.424871130596428, -1.52],
                                                  [-2.424871130596428, -2.17],
                                                  [0.0, -0.77]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.12],
                                                  [0.15588457268119893, -0.21],
                                                  [0.15588457268119893, -0.86],
                                                  [0.0, -0.77]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.77],
                                                  [0.15588457268119893, -0.86],
                                                  [-2.2689865579152286, -2.26],
                                                  [-2.424871130596428, -2.17]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                               'cover': [{'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.6749999999999999],
                                                  [-2.2603263038773846, -2.0749999999999997],
                                                  [-2.2603263038773846, -2.195],
                                                  [0.16454482671904333, -0.7949999999999999]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.6749999999999999],
                                                  [2.0698007150448086, -1.775],
                                                  [2.0698007150448086, -1.895],
                                                  [0.16454482671904333, -0.7949999999999999]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.7949999999999999],
                                                  [2.0698007150448086, -1.895],
                                                  [-0.35507041555161956, -3.295],
                                                  [-2.2603263038773846, -2.195]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035}]},
                     'moves': {'cover': [0.0, -0.9]}},
 'approval-stamp': {'parts': {'document': [{'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [-2.1650635094610964, -1.25],
                                                    [-2.1650635094610964, -1.32],
                                                    [0.0, -0.07]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [1.9918584287042087, -1.15],
                                                    [1.9918584287042087, -1.22],
                                                    [0.0, -0.07]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.07],
                                                    [1.9918584287042087, -1.22],
                                                    [-0.17320508075688787, -2.4699999999999998],
                                                    [-2.1650635094610964, -1.32]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.12990381056766576, -0.35000000000000003],
                                                    [1.5155444566227672, -1.2999999999999998]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.3897114317029974, -0.5],
                                                    [1.2557368354874356, -1.4499999999999997]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.649519052838329, -0.6499999999999999],
                                                    [0.9959292143521041, -1.5999999999999999]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.7320508075688772,
                                            'cy': -1.31,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0}],
                              'stamp': [{'kind': 'polygon',
                                         'pts': [[0.0, -1.25],
                                                 [-0.9526279441628825, -1.7999999999999998],
                                                 [-0.9526279441628825, -2.0],
                                                 [0.0, -1.4500000000000002]],
                                         'fill': '#26221F',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.25],
                                                 [0.9526279441628825, -1.7999999999999998],
                                                 [0.9526279441628825, -2.0],
                                                 [0.0, -1.4500000000000002]],
                                         'fill': '#1E1B18',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.4500000000000002],
                                                 [0.9526279441628825, -2.0],
                                                 [0.0, -2.55],
                                                 [-0.9526279441628825, -2.0]],
                                         'fill': '#3A3530',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.85],
                                                 [-0.2598076211353316, -2.0],
                                                 [-0.2598076211353316, -2.6],
                                                 [0.0, -2.45]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.85],
                                                 [0.2598076211353316, -2.0],
                                                 [0.2598076211353316, -2.6],
                                                 [0.0, -2.45]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.45],
                                                 [0.2598076211353316, -2.6],
                                                 [0.0, -2.75],
                                                 [-0.2598076211353316, -2.6]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.15],
                                                 [-0.7794228634059946, -2.5999999999999996],
                                                 [-0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -2.32]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.15],
                                                 [0.7794228634059946, -2.5999999999999996],
                                                 [0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -2.32]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.32],
                                                 [0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -3.2199999999999998],
                                                 [-0.7794228634059946, -2.7699999999999996]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035}]},
                    'moves': {'stamp': [0.0, 0.5]}},
 'budget-slots': {'parts': {'tray': [{'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [-1.5588457268119895, -0.9],
                                              [-1.5588457268119895, -1.2],
                                              [0.0, -0.3]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [3.117691453623979, -1.8],
                                              [3.117691453623979, -2.1],
                                              [0.0, -0.3]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.3],
                                              [3.117691453623979, -2.1],
                                              [1.5588457268119895, -3.0],
                                              [-1.5588457268119895, -1.2]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'available-tokens': [{'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.52],
                                                          [-1.1864548031846809, -1.145],
                                                          [-1.1864548031846809, -1.395],
                                                          [-0.10392304845413265, -0.77]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.52],
                                                          [0.45899346400575247, -0.845],
                                                          [0.45899346400575247, -1.0950000000000002],
                                                          [-0.10392304845413265, -0.77]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.77],
                                                          [0.45899346400575247, -1.0950000000000002],
                                                          [-0.6235382907247957, -1.7200000000000002],
                                                          [-1.1864548031846809, -1.395]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -0.9450000000000001],
                                                          [-0.4503332099679081, -1.57],
                                                          [-0.4503332099679081, -1.82],
                                                          [0.6321985447626401, -1.195]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -0.9450000000000001],
                                                          [1.195115057222525, -1.27],
                                                          [1.195115057222525, -1.52],
                                                          [0.6321985447626401, -1.195]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -1.195],
                                                          [1.195115057222525, -1.52],
                                                          [0.11258330249197693, -2.145],
                                                          [-0.4503332099679081, -1.82]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.37],
                                                          [0.28578838324886463, -1.995],
                                                          [0.28578838324886463, -2.245],
                                                          [1.3683201379794128, -1.62]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.37],
                                                          [1.9312366504392982, -1.695],
                                                          [1.9312366504392982, -1.945],
                                                          [1.3683201379794128, -1.62]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.62],
                                                          [1.9312366504392982, -1.945],
                                                          [0.8487048957087499, -2.57],
                                                          [0.28578838324886463, -2.245]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                            'allocated-token': [{'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -1.795],
                                                         [1.0219099764656372, -2.42],
                                                         [1.0219099764656372, -2.67],
                                                         [2.1044417311961854, -2.045]],
                                                 'fill': '#DCC9AA',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -1.795],
                                                         [2.6673582436560705, -2.1199999999999997],
                                                         [2.6673582436560705, -2.37],
                                                         [2.1044417311961854, -2.045]],
                                                 'fill': '#C7AE86',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -2.045],
                                                         [2.6673582436560705, -2.37],
                                                         [1.5848264889255224, -2.9949999999999997],
                                                         [1.0219099764656372, -2.67]],
                                                 'fill': '#F3E9D8',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035}]},
                  'moves': {'allocated-token': [0.25980762113533157, -1.0]}},
 'comparison-trays': {'parts': {'trays': [{'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [-1.6454482671904334, -0.95],
                                                   [-1.6454482671904334, -1.08],
                                                   [0.0, -0.13]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [1.5588457268119895, -0.9],
                                                   [1.5588457268119895, -1.03],
                                                   [0.0, -0.13]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -0.13],
                                                   [1.5588457268119895, -1.03],
                                                   [-0.08660254037844374, -1.98],
                                                   [-1.6454482671904334, -1.08]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -0.8400000000000001],
                                                   [-0.19052558883257628, -1.79],
                                                   [-0.19052558883257628, -2.14],
                                                   [1.454922678357857, -1.19]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -0.8400000000000001],
                                                   [1.5588457268119897, -0.9000000000000001],
                                                   [1.5588457268119897, -1.25],
                                                   [1.454922678357857, -1.19]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -1.19],
                                                   [1.5588457268119897, -1.25],
                                                   [-0.08660254037844355, -2.2],
                                                   [-0.19052558883257628, -2.14]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -0.8899999999999999],
                                                   [-1.6454482671904334, -0.95],
                                                   [-1.6454482671904334, -1.2999999999999998],
                                                   [-1.5415252187363004, -1.2399999999999998]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -0.8899999999999999],
                                                   [0.01732050807568898, -1.79],
                                                   [0.01732050807568898, -2.14],
                                                   [-1.5415252187363004, -1.2399999999999998]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -1.2399999999999998],
                                                   [0.01732050807568898, -2.14],
                                                   [-0.08660254037844374, -2.2],
                                                   [-1.6454482671904334, -1.2999999999999998]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.05],
                                                   [0.17320508075688787, -2.0],
                                                   [0.17320508075688787, -2.13],
                                                   [1.818653347947321, -1.1800000000000002]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.05],
                                                   [3.377499074759311, -1.9500000000000002],
                                                   [3.377499074759311, -2.08],
                                                   [1.818653347947321, -1.1800000000000002]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.1800000000000002],
                                                   [3.377499074759311, -2.08],
                                                   [1.7320508075688776, -3.0300000000000002],
                                                   [0.17320508075688787, -2.13]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -1.8900000000000001],
                                                   [1.628127759114745, -2.84],
                                                   [1.628127759114745, -3.19],
                                                   [3.2735760263051783, -2.24]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -1.8900000000000001],
                                                   [3.377499074759311, -1.9500000000000002],
                                                   [3.377499074759311, -2.3000000000000003],
                                                   [3.2735760263051783, -2.24]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -2.24],
                                                   [3.377499074759311, -2.3000000000000003],
                                                   [1.7320508075688776, -3.2500000000000004],
                                                   [1.628127759114745, -3.19]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -1.94],
                                                   [0.17320508075688787, -2.0],
                                                   [0.17320508075688787, -2.35],
                                                   [0.2771281292110206, -2.29]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -1.94],
                                                   [1.8359738560230103, -2.84],
                                                   [1.8359738560230103, -3.19],
                                                   [0.2771281292110206, -2.29]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -2.29],
                                                   [1.8359738560230103, -3.19],
                                                   [1.7320508075688776, -3.2500000000000004],
                                                   [0.17320508075688787, -2.35]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                                'sample-a': [{'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -0.625],
                                                      [-0.8227241335952167, -1.075],
                                                      [-0.8227241335952167, -1.675],
                                                      [-0.04330127018922192, -1.225]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -0.625],
                                                      [0.7361215932167728, -1.075],
                                                      [0.7361215932167728, -1.675],
                                                      [-0.04330127018922192, -1.225]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -1.225],
                                                      [0.7361215932167728, -1.675],
                                                      [-0.04330127018922197, -2.125],
                                                      [-0.8227241335952167, -1.675]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035}],
                                'rims': [{'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-1.6454482671904334, -0.95],
                                                  [-1.6454482671904334, -1.2999999999999998],
                                                  [0.0, -0.35]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [0.10392304845413262, -0.06],
                                                  [0.10392304845413262, -0.41],
                                                  [0.0, -0.35]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.35],
                                                  [0.10392304845413262, -0.41],
                                                  [-1.5415252187363004, -1.3599999999999999],
                                                  [-1.6454482671904334, -1.2999999999999998]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-0.10392304845413262, -0.06],
                                                  [-0.10392304845413262, -0.41],
                                                  [0.0, -0.35]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [1.5588457268119895, -0.9],
                                                  [1.5588457268119895, -1.25],
                                                  [0.0, -0.35]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.35],
                                                  [1.5588457268119895, -1.25],
                                                  [1.454922678357857, -1.31],
                                                  [-0.10392304845413262, -0.41]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [0.17320508075688787, -2.0],
                                                  [0.17320508075688787, -2.35],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [1.922576396401454, -1.11],
                                                  [1.922576396401454, -1.46],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.4],
                                                  [1.922576396401454, -1.46],
                                                  [0.2771281292110206, -2.41],
                                                  [0.17320508075688787, -2.35]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [1.7147302994931883, -1.11],
                                                  [1.7147302994931883, -1.46],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [3.377499074759311, -1.9500000000000002],
                                                  [3.377499074759311, -2.3000000000000003],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.4],
                                                  [3.377499074759311, -2.3000000000000003],
                                                  [3.2735760263051783, -2.3600000000000003],
                                                  [1.7147302994931883, -1.46]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                                'sample-b': [{'kind': 'polygon',
                                              'pts': [[1.775352077758099, -1.675],
                                                      [0.9959292143521044, -2.125],
                                                      [0.9959292143521044, -2.725],
                                                      [1.775352077758099, -2.2750000000000004]],
                                              'fill': '#26221F',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.775352077758099, -1.675],
                                                      [2.5547749411640934, -2.125],
                                                      [2.5547749411640934, -2.725],
                                                      [1.775352077758099, -2.2750000000000004]],
                                              'fill': '#1E1B18',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.775352077758099, -2.2750000000000004],
                                                      [2.5547749411640934, -2.725],
                                                      [1.775352077758099, -3.175],
                                                      [0.9959292143521044, -2.725]],
                                              'fill': '#3A3530',
                                              'stroke': '#3D3929',
                                              'width': 0.035}]},
                      'moves': {'sample-b': [0.0, -0.9]}},
 'secure-vault': {'parts': {'body': [{'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [-1.5588457268119895, -0.9],
                                              [-1.5588457268119895, -2.9],
                                              [0.0, -2.0]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [1.9918584287042087, -1.15],
                                              [1.9918584287042087, -3.15],
                                              [0.0, -2.0]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -2.0],
                                              [1.9918584287042087, -3.15],
                                              [0.43301270189221913, -4.05],
                                              [-1.5588457268119895, -2.9]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'door': [{'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -0.20500000000000002],
                                              [0.12124355652982141, -0.28],
                                              [0.12124355652982141, -1.92],
                                              [0.25114736709748725, -1.8449999999999998]],
                                      'fill': '#B4AFA6',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -0.20500000000000002],
                                              [1.9485571585149868, -1.1849999999999998],
                                              [1.9485571585149868, -2.8249999999999997],
                                              [0.25114736709748725, -1.8449999999999998]],
                                      'fill': '#8B8F96',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -1.8449999999999998],
                                              [1.9485571585149868, -2.8249999999999997],
                                              [1.818653347947321, -2.8999999999999995],
                                              [0.12124355652982141, -1.92]],
                                      'fill': '#D9D4C7',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'lock-bar': [{'kind': 'polygon',
                                          'pts': [[0.562916512459885, -0.925],
                                                  [0.4070319397786861, -1.0150000000000001],
                                                  [0.4070319397786861, -1.195],
                                                  [0.562916512459885, -1.105]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.562916512459885, -0.925],
                                                  [1.9485571585149868, -1.725],
                                                  [1.9485571585149868, -1.9050000000000002],
                                                  [0.562916512459885, -1.105]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.562916512459885, -1.105],
                                                  [1.9485571585149868, -1.9050000000000002],
                                                  [1.7926725858337882, -1.995],
                                                  [0.4070319397786861, -1.195]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.24],
                                                  [1.3683201379794128, -1.33],
                                                  [1.3683201379794128, -1.88],
                                                  [1.5242047106606118, -1.79]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.24],
                                                  [1.6974097914174997, -1.3399999999999999],
                                                  [1.6974097914174997, -1.89],
                                                  [1.5242047106606118, -1.79]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.79],
                                                  [1.6974097914174997, -1.89],
                                                  [1.5415252187363004, -1.98],
                                                  [1.3683201379794128, -1.88]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}]},
                  'moves': {'lock-bar': [0.562916512459885, -0.325]}},
 'context-crate': {'parts': {'crate-back': [{'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [-2.0784609690826525, -1.2],
                                                     [-2.0784609690826525, -1.33],
                                                     [0.0, -0.13]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [2.25166604983954, -1.3],
                                                     [2.25166604983954, -1.4300000000000002],
                                                     [0.0, -0.13]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, -0.13],
                                                     [2.25166604983954, -1.4300000000000002],
                                                     [0.17320508075688787, -2.63],
                                                     [-2.0784609690826525, -1.33]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -1.24],
                                                     [0.06928203230275515, -2.44],
                                                     [0.06928203230275515, -3.54],
                                                     [2.1477430013854075, -2.34]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -1.24],
                                                     [2.25166604983954, -1.3],
                                                     [2.25166604983954, -2.4000000000000004],
                                                     [2.1477430013854075, -2.34]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -2.34],
                                                     [2.25166604983954, -2.4000000000000004],
                                                     [0.17320508075688787, -3.6],
                                                     [0.06928203230275515, -3.54]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -1.14],
                                                     [-2.0784609690826525, -1.2],
                                                     [-2.0784609690826525, -2.3],
                                                     [-1.9745379206285198, -2.24]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -1.14],
                                                     [0.2771281292110206, -2.44],
                                                     [0.2771281292110206, -3.54],
                                                     [-1.9745379206285198, -2.24]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -2.24],
                                                     [0.2771281292110206, -3.54],
                                                     [0.17320508075688787, -3.6],
                                                     [-2.0784609690826525, -2.3]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                             'context': [{'kind': 'polygon',
                                          'pts': [[0.0, -0.6000000000000001],
                                                  [-1.299038105676658, -1.3499999999999999],
                                                  [-1.299038105676658, -1.42],
                                                  [0.0, -0.67]],
                                          'fill': '#ECE7DF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.6000000000000001],
                                                  [1.4722431864335457, -1.45],
                                                  [1.4722431864335457, -1.52],
                                                  [0.0, -0.67]],
                                          'fill': '#E2DCD2',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.67],
                                                  [1.4722431864335457, -1.52],
                                                  [0.17320508075688787, -2.27],
                                                  [-1.299038105676658, -1.42]],
                                          'fill': '#FFFFFF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polyline',
                                          'pts': [[-0.1299038105676657, -0.9500000000000001],
                                                  [0.9959292143521045, -1.6]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.3897114317029973, -1.1], [0.7361215932167728, -1.75]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.649519052838329, -1.25], [0.4763139720814413, -1.9]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'circle',
                                          'cx': -0.8660254037844385,
                                          'cy': -1.41,
                                          'r': 0.055,
                                          'fill': '#D97757',
                                          'stroke': 'none',
                                          'width': 0}],
                             'crate-front': [{'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [-2.0784609690826525, -1.2],
                                                      [-2.0784609690826525, -2.3],
                                                      [0.0, -1.1]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [0.10392304845413262, -0.06],
                                                      [0.10392304845413262, -1.1600000000000001],
                                                      [0.0, -1.1]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -1.1],
                                                      [0.10392304845413262, -1.1600000000000001],
                                                      [-1.9745379206285198, -2.3600000000000003],
                                                      [-2.0784609690826525, -2.3]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [-0.10392304845413262, -0.06],
                                                      [-0.10392304845413262, -1.1600000000000001],
                                                      [0.0, -1.1]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [2.25166604983954, -1.3],
                                                      [2.25166604983954, -2.4000000000000004],
                                                      [0.0, -1.1]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -1.1],
                                                      [2.25166604983954, -2.4000000000000004],
                                                      [2.1477430013854075, -2.46],
                                                      [-0.10392304845413262, -1.1600000000000001]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035}],
                             'lid': [{'kind': 'polygon',
                                      'pts': [[0.0, -1.0999999999999999],
                                              [-2.1823840175367852, -2.36],
                                              [-2.1823840175367852, -2.54],
                                              [0.0, -1.2799999999999998]],
                                      'fill': '#DCC9AA',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.0999999999999999],
                                              [2.3555890982936734, -2.46],
                                              [2.3555890982936734, -2.6399999999999997],
                                              [0.0, -1.2799999999999998]],
                                      'fill': '#C7AE86',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.2799999999999998],
                                              [2.3555890982936734, -2.6399999999999997],
                                              [0.17320508075688787, -3.9],
                                              [-2.1823840175367852, -2.54]],
                                      'fill': '#F3E9D8',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polyline',
                                      'pts': [[1.12583302491977, -2.0], [-0.9526279441628823, -3.2]],
                                      'fill': 'none',
                                      'stroke': '#8B8F96',
                                      'width': 0.18}]},
                   'moves': {'lid': [0.0, -1.0]}}}

def make_original(prop_id, height=3.2, x=0.0, y=0.0):
    """Return native VGroup with .parts and scale-correct .action_vectors."""
    from manim import VGroup, Polygon, VMobject, Circle
    import numpy as np
    if not np.isfinite(height) or height <= 0:
        raise ValueError('height must be positive and finite')
    p = _ST_ORIGINALS_25[prop_id]
    pts = []
    for name, shapes in p['parts'].items():
        dx, dy = p['moves'].get(name, (0, 0))
        for s in shapes:
            q = s.get('pts') or [(s['cx']-s['r'],s['cy']-s['r']), (s['cx']+s['r'],s['cy']+s['r'])]
            pts.extend(q)
            pts.extend((a+dx, b+dy) for a,b in q)
    x0,y0 = min(a for a,b in pts), min(b for a,b in pts)
    x1,y1 = max(a for a,b in pts), max(b for a,b in pts)
    scale = min(height/(y1-y0), 4.8/(x1-x0))
    cx,cy = (x0+x1)/2, (y0+y1)/2
    def point(a,b): return np.array([(a-cx)*scale+x, -(b-cy)*scale+y, 0])
    rig = VGroup()
    rig.parts, rig.action_vectors = {}, {}
    for name, shapes in p['parts'].items():
        part = VGroup()
        for s in shapes:
            if s['kind'] == 'circle':
                mob = Circle(radius=s['r']*scale).move_to(point(s['cx'],s['cy']))
            elif s['kind'] == 'polygon':
                mob = Polygon(*[point(a,b) for a,b in s['pts']])
            else:
                mob = VMobject().set_points_as_corners([point(a,b) for a,b in s['pts']])
            mob.set_fill(s['fill'] if s['fill']!='none' else '#FFFFFF', opacity=0 if s['fill']=='none' else 1)
            mob.set_stroke(s['stroke'] if s['stroke']!='none' else '#FFFFFF', width=s['width']*100, opacity=0 if s['stroke']=='none' else 1)
            part.add(mob)
        rig.parts[name] = part
        rig.add(part)
        if name in p['moves']:
            dx,dy = p['moves'][name]
            rig.action_vectors[name] = np.array([dx*scale, -dy*scale, 0])
    return rig


# ═════════════════════════════ DAYTHREAD FINAL PROJECT FILM — scene body (2026-11-23) ═════════════════════════════
# Helpers and the cast are copied from the October pitch film's scenes_body.py. Every [C] beat illustrates a
# CONSTRUCTED, PROPOSED workflow — nothing here was observed from a running system (no DayThread prototype,
# contract, checker or evaluation exists). The only observed result shown is the 2026-10-25 replay (B02, B03). Cast reused across beats: the check-in page (raw transcript), the
# summary page, the separate check (terracotta scan line), the memory drawers, the coordinator's review page /
# desk, and the permission gate (closed, stop light lit, until a coordinator approves).
# Timing: the measured Kokoro narration is the clock (no padding except BOUT's 1.0 s tail). Motions cue on
# faster-whisper word starts stored per beat in beat_sheet.json (`words`, written by audio_post.py).

MID_GUARD = 0.22          # GATE T and Gate V sample the clip midpoint: keep motion out of [mid-0.22, mid+0.22]
SCRIB_AMP = 0.085         # GATE T measures handwriting scribbles as text runs; 0.085 keeps short ones >= 41 px
CAP_SIZE = 34
try:
    _WORDS = {b["beat_id"]: b.get("words", []) for b in _SHEET["beats"]}
except Exception:
    _WORDS = {}


def _bid(self):
    return type(self).__name__.split("_")[0]


def _target(self):
    return _TARGET.get(_bid(self), 0.0)


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def at(self, t):
    gap = t - _elapsed(self)
    if gap > 0.02:
        self.wait(gap)


def at_word(self, word, nth=1, early=0.12):
    """Wait until the nth spoken occurrence of `word` (prefix match on the whisper word list)."""
    want, seen = _norm(word), 0
    for w, t in _WORDS.get(_bid(self), []):
        if _norm(w).startswith(want):
            seen += 1
            if seen == nth:
                at(self, t - early)
                return


def done(self):
    """Hold to the end of the beat's audio, never past it (the kit's finish() waits >= 0.3 s even when late)."""
    target = _target(self)
    if not target:
        self.wait(1.0)
        return
    gap = target - _elapsed(self) - 0.06
    if gap > 0.02:
        self.wait(gap)


def span(self, *anims, rt=0.5, **kw):
    """play() that never crosses the midpoint window and never runs past the beat's audio."""
    target = _target(self)
    if target:
        mid, now = target / 2, _elapsed(self)
        if now < mid + MID_GUARD and now + rt > mid - MID_GUARD:
            at(self, mid + MID_GUARD)
        now = _elapsed(self)
        if now + rt > target - 0.15:
            rt = max(0.12, target - 0.15 - now)
    self.play(*anims, run_time=rt, **kw)


# ── captions: italic, in their own bands, never mixed with scene headings (headings stay inside y <= 2.3) ──
def CAP(s):
    return Text(s, font=SERIF, color=INK, font_size=CAP_SIZE, slant="ITALIC")   # string form: Gate A's stub has no ITALIC constant


PARTS = {1: "1 · Executive summary", 2: "2 · Introduction", 3: "3 · Methods", 4: "4 · Evaluation"}


def captions(kind=None, part=None):
    g = VGroup(CAP("Synthesized voice reading Aditya’s script").move_to([-6.1, 3.1, 0], aligned_edge=LEFT))
    if part:
        g.add(CAP(PARTS[part]).move_to([6.1, 3.1, 0], aligned_edge=RIGHT))
    if kind == "C":
        g.add(CAP("Constructed — proposed workflow").move_to([0, -3.1, 0]))
    elif kind == "D":
        g.add(CAP("From each company’s own documentation, read 2026-10-14").move_to([0, -3.1, 0]))
    elif kind == "R":
        g.add(CAP("Replay run 2026-10-25 · synthetic data · fictional client").move_to([0, -3.1, 0]))
    return g


def L(s, x, y, size=40):
    return T(s, size).move_to([x, y, 0])


# ── the cast ──
def checkin_page(x, y, w=2.8, h=3.3, n=5, dot=2, short_last=True):
    """A check-in page: paper + n handwriting lines; a terracotta dot marks line `dot` (None = no dot)."""
    pg = paper(x, y, w, h)
    my, mx, mr = min(0.55, 0.18 * h + 0.1), min(0.55, 0.2 * w + 0.1), min(0.4, 0.15 * w + 0.1)
    step = (h - 2 * my) / (n - 1)
    x0, lw = x - w / 2 + mx, w - mx - mr
    ys = [y + h / 2 - my - i * step for i in range(n)]
    lines = VGroup(*[scribble(x0, yy, lw * (0.6 if (short_last and i == n - 1) else 1.0), amp=SCRIB_AMP)
                     for i, yy in enumerate(ys)])
    g = VGroup(pg, lines)
    g.pg, g.lines, g.ys, g.x0, g.lw = pg, lines, ys, x0, lw
    g.dot = None
    if dot is not None:
        g.dot = Dot([x0 - min(0.24, mx - 0.1), ys[dot], 0], radius=0.09 if w > 1.5 else 0.07, color=TERRA)
    return g


def summary_page(x, y, w=2.3, h=2.6, gap_row=2):
    """Shorter page with a dashed empty row where the tumble line should have been."""
    pg = paper(x, y, w, h)
    x0, lw = x - w / 2 + 0.38, w - 0.76
    my = min(0.5, 0.17 * h + 0.06)
    step = (h - 2 * my) / 3
    ys = [y + h / 2 - my - i * step for i in range(4)]
    lines = VGroup(*[scribble(x0, yy, lw * (0.55 if i == 3 else 1.0), amp=SCRIB_AMP)
                     for i, yy in enumerate(ys) if i != gap_row])
    gap = DashedLine([x0, ys[gap_row], 0], [x0 + lw, ys[gap_row], 0], color=DIM, stroke_width=4, dash_length=0.16)
    g = VGroup(pg, lines, gap)
    g.gap = gap
    return g


def slip(x, y, w=1.6, h=0.72):
    s = paper(x, y, w, h)
    d = Dot([x - w / 2 + 0.28, y, 0], radius=0.08, color=TERRA)
    ln = scribble(x - w / 2 + 0.5, y, w - 0.8, amp=SCRIB_AMP)
    return VGroup(s, d, ln)


def envelope(x, y, w=0.95, h=0.62):
    body = Rectangle(width=w, height=h, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    flap = VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners(
        [[-w / 2, h / 2, 0], [0, -h * 0.05, 0], [w / 2, h / 2, 0]])
    return VGroup(body, flap).move_to([x, y, 0])


def gate(x, y, h=2.4):
    """The permission-gate prop with its own barrier replaced by a horizontal boom arm that visibly blocks the
    lane (closed) and swings up only after approval (`open_gate`), plus a terracotta stop light on the left post."""
    g = make_original("permission-gate", height=h, x=x, y=y)
    g.remove(g.parts["barrier"])
    pivot = np.array([x - 0.30 * h, y + 0.05 * h, 0])
    boom = Rectangle(width=0.72 * h, height=0.085 * h, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK,
                     stroke_width=4).move_to(pivot + np.array([0.36 * h, 0, 0]))
    g.add(boom)
    g.boom, g.pivot = boom, pivot
    g.light = Dot([x - 0.30 * h, y + 0.22 * h, 0], radius=0.11 if h > 1.5 else 0.08, color=TERRA)
    return g


def open_gate(g):
    return Rotate(g.boom, angle=PI * 0.42, about_point=g.pivot)


def plinth(cx, cy, w=3.4, d=1.3, hgt=0.3):
    """A flat shelf/plinth seen from the front: kraft top face + front face, ink outlines. `d` is unused
    (kept for call compatibility); the top face recedes by a fixed 0.35."""
    front = Rectangle(width=w, height=hgt, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([cx, cy, 0])
    top = Polygon([cx - w / 2, cy + hgt / 2, 0], [cx + w / 2, cy + hgt / 2, 0], [cx + w / 2 + 0.3, cy + hgt / 2 + 0.32, 0],
                  [cx - w / 2 + 0.3, cy + hgt / 2 + 0.32, 0], fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(top, front)


def arrow(x0, y0, x1, y1):
    return Arrow([x0, y0, 0], [x1, y1, 0], buff=0, color=INK, stroke_width=5, max_tip_length_to_length_ratio=0.25)


# ═════════════════════════════ scenes ═════════════════════════════


# ═════════════════════════════ scenes ═════════════════════════════

class BIDEA_Title(Scene):
    def construct(self):
        self.add(captions())
        name = L("Aditya Raj", 0, 0.05, 48)
        title = T("DayThread", 120).move_to([0, 1.3, 0])
        sub = L("final project · the plan", 0, -0.7, 44)
        span(self, FadeIn(name, shift=UP * 0.15), rt=0.45)
        at_word(self, "This")
        span(self, FadeIn(title, shift=UP * 0.2), rt=0.55)
        at_word(self, "final")
        span(self, FadeIn(sub, shift=UP * 0.15), rt=0.45)
        thread = Line([-4.2, -1.55, 0], [4.2, -1.55, 0], color=INK, stroke_width=5)
        span(self, Create(thread), rt=0.6)
        pages = VGroup(*[paper(x, -1.97, 0.6, 0.78) for x in (-2.6, 0.0, 2.6)])
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.25), rt=0.8)
        done(self)


# ── Part 1 · Executive summary ──

class B01_WhatItIs(Scene):
    def construct(self):
        self.add(captions("C", 1))
        ty = -0.75
        t1 = Line([-5.7, ty, 0], [-0.4, ty, 0], color=INK, stroke_width=5)
        t2 = Line([-0.4, ty, 0], [2.6, ty, 0], color=INK, stroke_width=5)
        span(self, Create(t1), rt=0.6)
        d1 = checkin_page(-4.3, 0.75, 2.0, 2.4, n=4, dot=None)
        d2 = checkin_page(-1.6, 0.75, 2.0, 2.4, n=4, dot=1)
        l1, l2 = L("Day 1", -4.3, -1.25), L("Day 2", -1.6, -1.25)
        at_word(self, "remember")
        span(self, FadeIn(d1, shift=DOWN * 0.3), FadeIn(l1), rt=0.5)
        at_word(self, "next")
        span(self, FadeIn(d2, shift=DOWN * 0.3), FadeIn(l2), rt=0.5)
        at_word(self, "concerning")
        span(self, GrowFromCenter(d2.dot), rt=0.35)
        desk = make_original("review-desk", height=2.2, x=4.2, y=-0.35)
        desk.remove(desk.parts["evidence"])
        lc = L("coordinator", 4.2, -1.95)
        at_word(self, "exact")
        span(self, Create(t2), FadeIn(desk, shift=UP * 0.2), FadeIn(lc), rt=0.6)
        ev = slip(-1.6, -0.2, 1.3, 0.6)
        at_word(self, "coordinator")
        span(self, FadeIn(ev, scale=1.1), rt=0.3)
        span(self, MoveAlongPath(ev, ArcBetweenPoints(np.array([-1.6, -0.2, 0]), np.array([4.15, 0.25, 0]), angle=-PI / 4)),
             rt=0.9, rate_func=smooth)
        done(self)


class B02_Why(Scene):
    """The one observed result: the 2026-10-25 replay (replay/RESULTS.md, Aditya's review)."""
    def construct(self):
        self.add(captions("R", 1))
        cp = checkin_page(-4.7, 0.1, 2.2, 2.7, n=4, dot=1)
        lc = L("check-in", -4.7, 1.85)
        at_word(self, "reread")
        span(self, FadeIn(cp, shift=UP * 0.2), FadeIn(cp.dot), FadeIn(lc), rt=0.5)
        a = arrow(-3.35, 0.1, -2.55, 0.1)
        sp = checkin_page(-1.2, 0.1, 2.0, 2.4, n=3, dot=0)
        ls = L("summary", -1.2, 1.85)
        at_word(self, "summary")
        span(self, GrowArrow(a), FadeIn(sp, shift=LEFT * 0.3), FadeIn(sp.dot), FadeIn(ls), rt=0.55)
        k1 = T("kept the fall: 10 of 10", 38).move_to([0.4, 0.7, 0], aligned_edge=LEFT)
        k2 = T("meaning changed: 9 of 10", 38).move_to([0.4, -0.4, 0], aligned_edge=LEFT)
        at_word(self, "kept")
        span(self, FadeIn(k1, shift=LEFT * 0.15), rt=0.4)
        at_word(self, "changed")
        span(self, FadeIn(k2, shift=LEFT * 0.15), rt=0.4)
        bar = Line([0.4, -0.85, 0], [5.4, -0.85, 0], color=TERRA, stroke_width=8)
        span(self, Create(bar), rt=0.4)
        done(self)


class B03_Exists(Scene):
    def construct(self):
        self.add(captions(None, 1))
        p1, p2 = plinth(-3.3, -1.1, w=4.2), plinth(3.1, -1.1, w=5.4)
        l1, l2 = L("ran", -3.3, 1.85), L("planned", 3.1, 1.85)
        at_word(self, "test")
        pg = checkin_page(-3.3, 0.25, 1.2, 1.6, n=3, dot=1)
        lr = L("replay · 2026-10-25", -3.3, -1.85, 36)
        span(self, FadeIn(p1), FadeIn(l1), FadeIn(pg, shift=DOWN * 0.2), FadeIn(pg.dot), FadeIn(lr), rt=0.55)
        ghosts = VGroup(*[DashedVMobject(Rectangle(width=0.82, height=1.15, color=INK, stroke_width=4), num_dashes=14)
                          .move_to([1.1 + i * 1.0, 0.2, 0]) for i in range(5)])
        at_word(self, "Everything")
        span(self, FadeIn(p2), FadeIn(l2), rt=0.4)
        span(self, LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.2), rt=0.9)
        done(self)


# ── Part 2 · Introduction ──

def lifeline_group(cx):
    pl = plinth(cx, -1.15)
    cord = VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners([[cx - 1.45, 1.05, 0], [cx - 0.95, 0.25, 0], [cx - 0.45, 1.05, 0]])
    pend = Circle(radius=0.34, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([cx - 0.95, -0.05, 0])
    tower, lights = Iso(cx + 0.9, -0.95, 1.0).server(-0.35, -0.35, 0, 0.7, 0.7, slab=0.38, n=3)
    head = L("Lifeline", cx, 1.75)
    return pl, VGroup(cord, pend), tower, lights, head


def dailycall_group(cx):
    pl = plinth(cx, -1.15)
    phone = VGroup(RoundedRectangle(width=0.95, height=1.7, corner_radius=0.14, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4),
                   Rectangle(width=0.72, height=1.25, fill_color=CARD, fill_opacity=1, stroke_width=0)).move_to([cx - 0.85, 0.3, 0])
    sm = paper(cx + 0.75, 0.3, 1.3, 1.6)
    smlines = VGroup(*[Line([cx + 0.3, 0.7 - i * 0.38, 0], [cx + 1.2, 0.7 - i * 0.38, 0], color=GHOST, stroke_width=6) for i in range(3)])
    head = L("DailyCall", cx, 1.75)
    return pl, phone, VGroup(sm, smlines), head


class B04_Others(Scene):
    def construct(self):
        self.add(captions("D", 2))
        lx, dx = -2.9, 2.9
        pl1, pend, tower, lights, h1 = lifeline_group(lx)
        pl2, phone, sm, h2 = dailycall_group(dx)
        span(self, FadeIn(pl1), FadeIn(pl2), rt=0.45)
        at_word(self, "Lifeline")
        span(self, FadeIn(pend, shift=DOWN * 0.2), FadeIn(tower), FadeIn(lights), FadeIn(h1), rt=0.5)
        arcs = VGroup(*[Arc(radius=r, start_angle=-PI / 5, angle=2 * PI / 5, color=INK, stroke_width=4).move_arc_center_to([lx - 0.95, -0.05, 0])
                        for r in (0.6, 0.85)])
        at_word(self, "detect", nth=2) if sum(_norm(w).startswith("detect") for w, _ in _WORDS.get("B04", [])) >= 2 else at_word(self, "detect")
        span(self, LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), rt=0.5)
        span(self, lights.animate.set_color(TERRA), rt=0.3)
        at_word(self, "DailyCall") if any(_norm(w).startswith("dailycall") for w, _ in _WORDS.get("B04", [])) else at_word(self, "Daily")
        span(self, FadeIn(phone, shift=DOWN * 0.2), FadeIn(h2), rt=0.45)
        at_word(self, "summaries")
        span(self, FadeIn(sm, shift=LEFT * 0.2), rt=0.45)
        done(self)


class B05_Focus(Scene):
    def construct(self):
        self.add(captions("C", 2))
        lx, dx = -2.9, 2.9
        pl1, pend, tower, lights, h1 = lifeline_group(lx)
        pl2, phone, sm, h2 = dailycall_group(dx)
        lights.set_color(TERRA)
        arcs = VGroup(*[Arc(radius=r, start_angle=-PI / 5, angle=2 * PI / 5, color=INK, stroke_width=4).move_arc_center_to([lx - 0.95, -0.05, 0])
                        for r in (0.6, 0.85)])
        left = VGroup(pl1, pend, tower, lights, arcs)
        mid = VGroup(pl2, phone, sm)
        self.add(left, mid, h1, h2)
        span(self, left.animate.scale(0.72).move_to([-4.65, -0.25, 0]), mid.animate.scale(0.72).move_to([-1.0, -0.25, 0]),
             h1.animate.move_to([-4.65, 1.2, 0]), h2.animate.move_to([-1.0, 1.2, 0]), rt=0.6)
        cx = 3.6
        pl3 = plinth(cx, -1.15, w=3.6)
        h3 = L("DayThread · planned", cx, 1.75)
        at_word(self, "narrower")
        span(self, FadeIn(pl3, shift=LEFT * 0.4), FadeIn(h3), rt=0.5)
        pgs = VGroup(*[paper(cx - 1.25 + i * 0.85, 0.55, 0.62, 0.8) for i in range(3)])
        dots = VGroup(*[Dot([cx - 1.25 + i * 0.85, 0.55, 0], radius=0.07, color=TERRA) for i in range(3)])
        at_word(self, "linked")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in pgs], lag_ratio=0.25), FadeIn(dots), rt=0.55)
        sl = Line([cx - 1.65, 0.95, 0], [cx - 1.65, 0.15, 0], color=TERRA, stroke_width=8)
        at_word(self, "separate")
        span(self, Create(sl), rt=0.25)
        span(self, sl.animate.shift(RIGHT * 2.3), rt=0.8, rate_func=linear)
        span(self, FadeOut(sl), rt=0.25)
        mg = gate(cx + 1.2, -0.55, 1.15)
        concern = slip(cx - 0.55, -0.45, 1.0, 0.5)
        thr = VGroup(*[Line([cx - 1.25 + i * 0.85, 0.15, 0], [cx - 0.55, -0.2, 0], color=INK, stroke_width=4) for i in range(3)])
        at_word(self, "person")
        span(self, FadeIn(mg), FadeIn(mg.light), rt=0.4)
        at_word(self, "leaves")
        span(self, LaggedStart(*[Create(t) for t in thr], lag_ratio=0.2), FadeIn(concern, scale=1.1), rt=0.7)
        done(self)


# ── Part 3 · Methods ──

class B06_Contract(Scene):
    def construct(self):
        self.add(captions("C", 3))
        cp = checkin_page(-5.0, 0.2, 2.0, 2.5, n=4, dot=None)
        seal = Dot([-4.45, -0.7, 0], radius=0.13, color=TERRA)
        lc = L("contract", -5.0, 1.85)
        at_word(self, "delegation")
        span(self, FadeIn(cp, shift=UP * 0.2), FadeIn(lc), rt=0.45)
        span(self, GrowFromCenter(seal), rt=0.3)
        xs = (-1.9, 0.9, 3.7)
        steps = VGroup(*[VGroup(paper(x, 0.2, 1.5, 1.1), scribble(x - 0.5, 0.2, 1.0, amp=SCRIB_AMP)) for x in xs])
        arrs = VGroup(arrow(-1.05, 0.2, 0.05, 0.2), arrow(1.75, 0.2, 2.85, 0.2))
        lh = L("handoffs", 0.9, -1.1)
        at_word(self, "step")
        span(self, LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in steps], lag_ratio=0.25), rt=0.6)
        span(self, LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.3), FadeIn(lh), rt=0.5)
        cks = VGroup(check(-0.5, 0.75, s=0.17), check(2.3, 0.75, s=0.17))
        at_word(self, "check")
        span(self, LaggedStart(*[Create(c) for c in cks], lag_ratio=0.3), rt=0.5)
        stop = Line([2.3, -0.3, 0], [2.3, 0.7, 0], color=INK, stroke_width=10)
        ls = L("stop", 2.3, 1.25)
        at_word(self, "fails")
        span(self, FadeOut(cks[1]), rt=0.25)
        at_word(self, "stops")
        span(self, Create(stop), FadeIn(ls), rt=0.4)
        tests = VGroup(*[check(-5.75 + i * 0.55, -1.6, s=0.14) for i in range(3)])
        lt = L("tests first", -4.4, -2.2, 36)
        at_word(self, "tests")
        span(self, LaggedStart(*[Create(t) for t in tests], lag_ratio=0.25), FadeIn(lt), rt=0.6)
        done(self)


class B07_Handoffs(Scene):
    def construct(self):
        self.add(captions("C", 3))
        bx = -4.5
        bnd = make_original("evidence-binder", height=1.9, x=bx, y=-0.25)
        la = L("append only", bx, -1.85)
        at_word(self, "saved")
        span(self, FadeIn(bnd, shift=UP * 0.2), FadeIn(la), rt=0.5)
        ow = paper(bx - 1.3, 1.45, 1.0, 0.65)
        xx = VGroup(Line([bx - 1.6, 1.2, 0], [bx - 1.0, 1.7, 0], color=INK, stroke_width=6),
                    Line([bx - 1.6, 1.7, 0], [bx - 1.0, 1.2, 0], color=INK, stroke_width=6))
        at_word(self, "edited")
        span(self, FadeIn(ow, shift=RIGHT * 0.3), rt=0.3)
        span(self, ow.animate.shift(RIGHT * 0.7), rt=0.3)
        span(self, ow.animate.shift(LEFT * 0.7), Create(xx), rt=0.35)
        pg = checkin_page(-1.0, 0.3, 1.3, 1.7, n=3, dot=1)
        dr = make_original("memory-drawers", height=1.8, x=1.05, y=-0.2)
        lq = L("quoted", 0.0, -1.85)
        at_word(self, "claim")
        span(self, FadeIn(pg, shift=UP * 0.2), FadeIn(pg.dot), FadeIn(dr, shift=UP * 0.2), FadeIn(lq), rt=0.5)
        q = ArcBetweenPoints(np.array([-0.3, 0.3, 0]), np.array([0.6, 0.55, 0]), angle=-PI / 3)
        q.set_stroke(INK, 5)
        at_word(self, "quote")
        span(self, Create(q), rt=0.5)
        g = gate(4.4, -0.25, 2.0)
        lg = L("bound to what was seen", 3.95, -1.85, 34)
        at_word(self, "approval")
        span(self, FadeIn(g), FadeIn(g.light), FadeIn(lg), rt=0.5)
        lock = VGroup(Rectangle(width=0.5, height=0.38, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([5.25, 0.85, 0]),
                      Arc(radius=0.17, start_angle=0, angle=PI, color=INK, stroke_width=6).move_to([5.25, 1.14, 0]))
        at_word(self, "changed")
        span(self, FadeIn(lock, shift=DOWN * 0.15), rt=0.4)
        done(self)


class B08_Loop(Scene):
    def construct(self):
        self.add(captions("C", 3))
        rc = np.array([-2.3, 0.3, 0])
        ring = Circle(radius=1.1, color=INK, stroke_width=6).move_to(rc)
        runner = Dot(rc + np.array([0, 1.1, 0]), radius=0.13, color=TERRA)
        ll = L("loop", -2.3, 1.95)
        at_word(self, "loop")
        span(self, Create(ring), FadeIn(runner), FadeIn(ll), rt=0.55)
        bs = make_original("budget-slots", height=1.7, x=2.6, y=0.35)
        lb = L("turn budget", 2.6, -1.0)
        at_word(self, "budget")
        span(self, FadeIn(bs, shift=UP * 0.2), FadeIn(lb), rt=0.5)
        at_word(self, "conversation")
        span(self, MoveAlongPath(runner, ring.copy().rotate(PI / 2, about_point=rc)),
             bs.parts["allocated-token"].animate.shift(bs.action_vectors["allocated-token"]), rt=1.0, rate_func=linear)
        bar = Line([-3.4, -1.25, 0], [-1.2, -1.25, 0], color=INK, stroke_width=8)
        ls = L("stop", -2.3, -1.8)
        at_word(self, "never")
        span(self, Create(bar), FadeIn(ls), rt=0.4)
        done(self)


class B09_Checker(Scene):
    def construct(self):
        self.add(captions("C", 3))
        base = Iso(-5.0, -0.1, 1.2).box(-0.4, -0.4, 0, 0.8, 0.8, 0.55)
        lh = L("Hugging Face", -5.0, 1.3, 36)
        lbm = L("base model", -5.0, -1.2, 36)
        at_word(self, "small")
        span(self, FadeIn(base, shift=DOWN * 0.2), FadeIn(lh), FadeIn(lbm), rt=0.5)
        a = arrow(-4.05, 0.05, -3.15, 0.05)
        ft = Iso(-2.2, -0.1, 1.2).box(-0.4, -0.4, 0, 0.8, 0.8, 0.55, DARK_TOP, DARK_L, DARK_R)
        lft = L("fine-tuned", -2.2, -1.2, 36)
        at_word(self, "fine")
        span(self, GrowArrow(a), FadeIn(ft, shift=DOWN * 0.2), FadeIn(lft), rt=0.5)
        rp = checkin_page(1.2, 0.25, 2.0, 2.5, n=4, dot=1)
        lr = L("raw transcript", 1.2, -1.55, 36)
        at_word(self, "raw")
        span(self, FadeIn(rp, shift=UP * 0.2), FadeIn(rp.dot), FadeIn(lr), rt=0.45)
        sl = Line([rp.x0 - 0.15, rp.ys[0] + 0.25, 0], [rp.x0 + rp.lw + 0.1, rp.ys[0] + 0.25, 0], color=TERRA, stroke_width=8)
        span(self, Create(sl), rt=0.25)
        span(self, sl.animate.move_to([float(np.array(sl.get_center())[0]), rp.ys[1] - 0.13, 0]), rt=0.7, rate_func=smooth)
        sp = checkin_page(4.6, 0.25, 1.7, 2.1, n=3, dot=None)
        xx = VGroup(Line([3.95, -0.5, 0], [5.25, 1.0, 0], color=INK, stroke_width=7),
                    Line([3.95, 1.0, 0], [5.25, -0.5, 0], color=INK, stroke_width=7))
        ln = L("not the summary", 4.6, -1.55, 36)
        at_word(self, "never")
        span(self, FadeIn(sp, shift=LEFT * 0.2), FadeIn(ln), rt=0.4)
        span(self, Create(xx), rt=0.35)
        done(self)


class B10_Data(Scene):
    def construct(self):
        self.add(captions("C", 3))
        top = L("synthetic data · fictional clients", 0, 1.95)
        at_word(self, "synthetic")
        span(self, FadeIn(top), rt=0.4)
        stack = VGroup(*[checkin_page(-4.3 + i * 0.18, 0.15 - i * 0.18, 1.8, 2.2, n=3, dot=None) for i in range(3)])
        lt = L("training · by Claude", -4.0, -1.65, 36)
        at_word(self, "training")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in stack], lag_ratio=0.25), FadeIn(lt), rt=0.6)
        ck = check(-2.85, -0.15, s=0.2)
        at_word(self, "spot")
        span(self, Create(ck), rt=0.35)
        v = make_original("secure-vault", height=2.0, x=3.7, y=0.15)
        lv = L("held-out · by me", 3.7, -1.65, 36)
        at_word(self, "held")
        span(self, FadeIn(v, shift=UP * 0.2), FadeIn(lv), rt=0.5)
        hp = VGroup(*[paper(0.4 + i * 0.5, 0.3, 0.7, 0.9) for i in range(2)])
        at_word(self, "myself")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in hp], lag_ratio=0.3), rt=0.4)
        span(self, hp.animate.scale(0.5).move_to([3.4, 0.2, 0]), rt=0.6, rate_func=ease_in)
        span(self, FadeOut(hp), rt=0.2)
        at_word(self, "lock")
        span(self, v.parts["lock-bar"].animate.shift(v.action_vectors["lock-bar"]), rt=0.4)
        done(self)


def laptop(x, y, w=1.7):
    scr = Rectangle(width=w, height=w * 0.62, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + 0.35, 0])
    inner = Rectangle(width=w * 0.82, height=w * 0.45, fill_color=CARD, fill_opacity=1, stroke_width=0).move_to([x, y + 0.37, 0])
    base = Polygon([x - w * 0.62, y - 0.25, 0], [x + w * 0.62, y - 0.25, 0], [x + w * 0.5, y - 0.03, 0], [x - w * 0.5, y - 0.03, 0],
                   fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(scr, inner, base)


class B11_Resources(Scene):
    def construct(self):
        self.add(captions("C", 3))
        xs = (-4.4, 0.0, 4.4)
        pls = VGroup(*[plinth(x, -1.0, w=3.0) for x in xs])
        span(self, FadeIn(pls), rt=0.4)
        ws = make_original("agent-workstation", height=1.6, x=xs[0], y=0.1)
        l1 = L("existing account", xs[0], -1.75, 36)
        at_word(self, "existing")
        span(self, FadeIn(ws, shift=DOWN * 0.2), FadeIn(l1), rt=0.45)
        c1 = check(xs[0] + 1.2, 1.15, s=0.18)
        at_word(self, "credits")
        span(self, Create(c1), rt=0.3)
        bx = Iso(xs[1], -0.55, 1.0).box(-0.4, -0.4, 0, 0.8, 0.8, 0.5)
        dn = arrow(xs[1], 1.4, xs[1], 0.45)
        l2 = L("free download", xs[1], -1.75, 36)
        at_word(self, "base")
        span(self, FadeIn(bx, shift=DOWN * 0.2), GrowArrow(dn), FadeIn(l2), rt=0.5)
        c2 = check(xs[1] + 1.2, 1.15, s=0.18)
        at_word(self, "account", nth=2)
        span(self, Create(c2), rt=0.3)
        lp = laptop(xs[2], 0.0)
        l3 = L("my laptop", xs[2], -1.75, 36)
        c3 = check(xs[2] + 1.2, 1.15, s=0.18)
        at_word(self, "laptop")
        span(self, FadeIn(lp, shift=DOWN * 0.2), FadeIn(l3), Create(c3), rt=0.5)
        st = L("Python · PyTorch · SQLite", 0, 2.0)
        at_word(self, "Python")
        span(self, FadeIn(st), rt=0.4)
        done(self)


class B12_Steps(Scene):
    def construct(self):
        self.add(captions("C", 3))
        ty = -0.2
        thread = Line([-5.4, ty, 0], [4.3, ty, 0], color=INK, stroke_width=5)
        span(self, Create(thread), rt=0.6)
        xs = (-4.6, -2.7, -0.8, 1.1, 3.0)
        labels = ("contract + tests", "test set", "training data", "checker", "loop + memory")
        cues = (("contract", 1), ("test", 2), ("training", 1), ("checker", 1), ("loop", 1))
        for i, (x, lab, (w, n)) in enumerate(zip(xs, labels, cues)):
            d = Dot([x, ty, 0], radius=0.14, color=TERRA if i == 0 else INK)
            num = L(str(i + 1), x, ty + 0.5, 40) if i % 2 else L(str(i + 1), x, ty - 0.5, 40)
            lb = L(lab, x, ty + 1.15, 36) if i % 2 == 0 else L(lab, x, ty - 1.15, 36)
            at_word(self, w, nth=n)
            span(self, GrowFromCenter(d), FadeIn(num), FadeIn(lb), rt=0.35)
        v = make_original("secure-vault", height=1.6, x=5.3, y=0.15)
        lv = L("held-out run · Dec 20", 4.0, -1.95, 36)
        at_word(self, "held")
        span(self, FadeIn(v, shift=UP * 0.2), FadeIn(lv), rt=0.5)
        done(self)


# ── Part 4 · Evaluation ──

class B13_EvalChecker(Scene):
    def construct(self):
        self.add(captions("C", 4))
        xs = (-5.0, -2.6, -0.2)
        names = ("keywords", "untrained", "fine-tuned")
        bars = VGroup(*[DashedVMobject(Rectangle(width=1.0, height=2.2, color=INK, stroke_width=4), num_dashes=22).move_to([x, 0.3, 0]) for x in xs])
        qs = VGroup(*[T("?", 64).move_to([x, 0.3, 0]) for x in xs])
        lbs = VGroup(*[L(n, x, -1.2, 36) for n, x in zip(names, xs)])
        at_word(self, "compare")
        span(self, LaggedStart(*[Create(b) for b in bars], lag_ratio=0.25), FadeIn(lbs), rt=0.7)
        span(self, FadeIn(qs), rt=0.3)
        env = envelope(3.6, 0.45, w=1.6, h=1.05)
        le = L("pass mark, sealed first", 3.6, -1.2, 36)
        at_word(self, "pass")
        span(self, FadeIn(env, shift=DOWN * 0.2), FadeIn(le), rt=0.45)
        thr = DashedLine([-5.8, 0.75, 0], [0.6, 0.75, 0], color=TERRA, stroke_width=6, dash_length=0.2)
        at_word(self, "beat")
        span(self, Create(thr), rt=0.5)
        done(self)


class B14_Failures(Scene):
    def construct(self):
        self.add(captions("C", 4))
        xs = (-5.0, -2.5, 0.0, 2.5, 5.0)
        lf = L("5 failure cases, on purpose", 0, 1.95)
        at_word(self, "five")
        span(self, FadeIn(lf), rt=0.4)
        for x, w in zip(xs, ("spill", "legs", "didn", "neighb", "asleep")):
            c = checkin_page(x, 0.0, 1.7, 2.0, n=3, dot=1)
            at_word(self, w)
            span(self, FadeIn(c, shift=DOWN * 0.25), FadeIn(c.dot), rt=0.3)
        done(self)


OP_X, OP_Y, OP_W, OP_H = -3.7, -0.1, 3.0, 3.4
SP_X, SP_Y = 0.75, 0.15


class B15_Controlled(Scene):
    def construct(self):
        self.add(captions("C", 4))
        p = checkin_page(OP_X, OP_Y, OP_W, OP_H, n=5, dot=2)
        head = L("check-in", OP_X, OP_Y + OP_H / 2 + 0.42)
        at_word(self, "controlled")
        span(self, FadeIn(p, shift=UP * 0.2), FadeIn(p.dot), FadeIn(head), rt=0.5)
        s = summary_page(SP_X, SP_Y)
        sh, sm = L("summary", SP_X, SP_Y + 1.72), L("forced to drop it", SP_X, SP_Y - 1.75, 36)
        at_word(self, "force")
        span(self, FadeIn(s, shift=LEFT * 0.4), FadeIn(sh), FadeIn(sm), rt=0.55)
        at_word(self, "drops")
        span(self, Indicate(s.gap, color=INK, scale_factor=1.0), rt=0.4)
        sl = Line([p.x0 - 0.15, p.ys[0] + 0.3, 0], [p.x0 + p.lw + 0.1, p.ys[0] + 0.3, 0], color=TERRA, stroke_width=8)
        at_word(self, "separate")
        span(self, Create(sl), rt=0.3)
        span(self, sl.animate.move_to([float(np.array(sl.get_center())[0]), p.ys[2] - 0.13, 0]), rt=0.8, rate_func=smooth)
        q = make_original("task-queue", height=2.0, x=4.7, y=-0.25)
        lq = L("review", 4.7, -1.85)
        at_word(self, "coordinator")
        span(self, FadeIn(q, shift=UP * 0.2), FadeIn(lq), rt=0.45)
        ri = slip(OP_X + 0.3, p.ys[2], 1.5, 0.7)
        span(self, FadeIn(ri, scale=1.1), rt=0.25)
        span(self, MoveAlongPath(ri, ArcBetweenPoints(np.array([OP_X + 0.3, p.ys[2], 0]), np.array([4.15, 0.45, 0]), angle=-PI / 3.5)),
             rt=0.9, rate_func=smooth)
        done(self)


class B16_Limits(Scene):
    def construct(self):
        self.add(captions("C", 4))
        fence = DashedLine([-5.8, -1.5, 0], [5.8, -1.5, 0], color=INK, stroke_width=4, dash_length=0.3)
        lf = L("synthetic only · not real care", 0, -2.05, 36)
        at_word(self, "real")
        span(self, Create(fence), FadeIn(lf), rt=0.5)
        op = checkin_page(-2.8, 0.35, 2.2, 2.6, n=4, dot=1)
        lo = L("original words", -2.8, 2.0)
        cl = slip(2.6, op.ys[1], 2.4, 0.85)
        lc = L("claim", 2.6, 2.0)
        at_word(self, "meaning")
        span(self, FadeIn(op, shift=UP * 0.2), FadeIn(op.dot), FadeIn(lo), rt=0.45)
        # GATE T reads a lined slip as stacked labels at the clip midpoint (as in the October B03): bring the
        # claim slip in only after the midpoint window
        link = Line([op.x0 + op.lw + 0.35, op.ys[1], 0], [1.3, op.ys[1], 0], color=INK, stroke_width=5)
        at_word(self, "next")
        at(self, max(_elapsed(self), _target(self) / 2 + MID_GUARD + 0.05))
        span(self, FadeIn(cl, shift=LEFT * 0.2), FadeIn(lc), rt=0.4)
        span(self, Create(link), rt=0.45)
        done(self)


class BOUT_Outro(Scene):
    def construct(self):
        self.add(captions())
        title = T("DayThread", 110).move_to([0, 1.0, 0])
        name = L("Aditya Raj", 0, -0.2, 52)
        gh = L("github.com/aditya-raj-sde", 0, -1.0, 40)
        span(self, FadeIn(title, shift=UP * 0.2), rt=0.45)
        at_word(self, "Aditya") if any(_norm(w).startswith("aditya") for w, _ in _WORDS.get("BOUT", [])) else at(self, 1.6)
        span(self, FadeIn(name, shift=UP * 0.15), FadeIn(gh, shift=UP * 0.15), rt=0.45)
        th = Line([-3.0, -1.75, 0], [3.0, -1.75, 0], color=INK, stroke_width=5)
        span(self, Create(th), rt=0.5)
        span(self, GrowFromCenter(Dot([3.0, -1.75, 0], radius=0.1, color=TERRA)), rt=0.3)
        done(self)
