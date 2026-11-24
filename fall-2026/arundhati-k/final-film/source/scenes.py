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


# ═════════════════════════════ coop-sponsor-check-final (Arundhati Kandelkar) ═════════════════════════════
# Every animation lands by ~0.40 of the beat or starts after ~0.60 (GATE T / Gate V sample the midpoint).
# Each body beat carries an honesty tag: EXISTS (with its evidence) or PLANNED / CONSTRUCTED.
KRAFT_EDGE = "#9C8462"


def _T(self):
    return _TARGET.get(type(self).__name__.split("_")[0]) or 8.0


def to(self, frac):
    gap = _T(self) * frac - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def rt(self, frac):
    return max(0.3, _T(self) * frac)


def tag(s):
    t = T(s, 42)
    t.move_to([-6.0 + t.width / 2, 2.95, 0])
    return t


def fit(m, maxw):
    if m.width > maxw:
        m.scale_to_fit_width(maxw)
    return m


def cross(x, y, s=0.25, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def label(s, x, y, size=38):
    return T(s, size).move_to([x, y, 0])


def kbox(ox, oy, s=1.0, w=1.6, d=1.6, h=1.2, taped=True):
    iso = Iso(ox, oy, s)
    g = iso.box(0, 0, 0, w, d, h)
    if taped:
        g.add(iso.tape(0, 0, h, w, d))
    return g


def gapped_page():
    pg = paper(-1.0, 0.6, w=5.0, h=3.0)
    lines = VGroup(*[Line([-3.1, y, 0], [-1.5, y, 0], color=GHOST, stroke_width=6) for y in (1.5, 1.0, 0.5, 0.0, -0.5)])
    hole = Rectangle(width=1.7, height=1.3, fill_color=STAGE, fill_opacity=1, stroke_color=DIM, stroke_width=3).move_to([0.4, 0.5, 0])
    return pg, lines, hole


class B00_Arrives(Scene):
    def construct(self):
        box = kbox(-1.4, -1.5, 1.0)
        pg = paper(2.8, -0.1, w=2.2, h=2.6)
        sc = scribbles_on(pg, n=4)
        l1, l2 = label("company", -1.4, -2.15), label("sponsor data", 2.8, -1.85)
        tg = tag("EXISTS · commit 03784b0")
        self.play(FadeIn(box, shift=DOWN * 0.8), FadeIn(pg), run_time=rt(self, 0.12))
        self.play(Create(sc), FadeIn(l1), FadeIn(l2), run_time=rt(self, 0.12))
        self.play(FadeIn(tg), run_time=rt(self, 0.06))
        to(self, 0.62)
        self.play(Create(check(-6.0 + tg.width + 0.45, 2.95, s=0.18)), run_time=rt(self, 0.08))
        finish(self)


class B01_Three(Scene):
    def construct(self):
        iso = Iso(-4.3, -1.6, 0.9)
        back, front = iso.open_box(0, 0, 0, 1.6, 1.6, 1.1)
        self.add(back, front)
        pg = paper(-0.9, 0.5, w=1.5, h=1.9)
        # ruled ghost lines, not scribbles: GATE T read the scribble block as a 40px text run
        sc = VGroup(*[Line([-1.4, y, 0], [-0.4, y, 0], color=GHOST, stroke_width=6) for y in (1.0, 0.6, 0.2)])
        cal = Rectangle(width=1.7, height=1.7, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([1.7, 0.5, 0])
        band = Rectangle(width=1.7, height=0.35, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.7, 1.175, 0])
        cells = VGroup(*[Square(0.3, fill_color=(TERRA if (i, j) == (1, 2) else GHOST), fill_opacity=1, stroke_width=0)
                         .move_to([1.25 + 0.45 * j, 0.6 - 0.45 * i, 0]) for i in range(3) for j in range(3)])
        live = Circle(radius=0.8, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([4.4, 0.5, 0])
        lc = check(4.35, 0.45, s=0.3)
        ls = VGroup(label("record", -0.9, -1.0, 46), label("dates", 1.7, -1.0, 46), label("live", 4.4, -1.0, 46))
        tg = tag("EXISTS")
        self.play(FadeIn(VGroup(pg, sc), shift=UP * 0.6), run_time=rt(self, 0.08))
        self.play(FadeIn(VGroup(cal, band, cells), shift=UP * 0.6), run_time=rt(self, 0.08))
        self.play(FadeIn(live, shift=UP * 0.6), Create(lc), run_time=rt(self, 0.08))
        self.play(FadeIn(ls), FadeIn(tg), run_time=rt(self, 0.08))
        to(self, 0.62)
        self.play(LaggedStart(*[GrowFromCenter(Dot([x, -1.55, 0], radius=0.08, color=TERRA)) for x in (-0.9, 1.7, 4.4)],
                              lag_ratio=0.2), run_time=rt(self, 0.1))
        finish(self)


class B02_Unknown(Scene):
    def construct(self):
        posts = VGroup(Rectangle(width=0.5, height=3.0, fill_color=DIM, fill_opacity=1, stroke_width=0).move_to([1.0, -0.4, 0]),
                       Rectangle(width=0.5, height=3.0, fill_color=DIM, fill_opacity=1, stroke_width=0).move_to([3.4, -0.4, 0]),
                       Rectangle(width=2.9, height=0.5, fill_color=DIM, fill_opacity=1, stroke_width=0).move_to([2.2, 1.35, 0]))
        q = T("?", 120, bold=True).move_to([2.2, -0.3, 0])
        box = kbox(-5.0, -1.9, 0.8, w=1.4, d=1.4, h=1.0)
        l1 = label("not in data", 2.2, 2.1)
        tg = tag("EXISTS")
        self.add(box)
        self.play(FadeIn(posts), FadeIn(l1), FadeIn(tg), run_time=rt(self, 0.1))
        self.play(box.animate.shift(RIGHT * 3.4), run_time=rt(self, 0.14))
        self.play(FadeIn(q), run_time=rt(self, 0.08))
        to(self, 0.62)
        bub = Ellipse(width=1.9, height=1.1, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([4.9, 0.6, 0])
        tail = Polygon([4.45, 0.17, 0], [4.8, 0.08, 0], [4.25, -0.3, 0], fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5)
        l2 = label("ask a person", 4.9, 1.65, 36)
        self.play(FadeIn(tail), GrowFromCenter(bub), FadeIn(l2), run_time=rt(self, 0.12))
        finish(self)


class B03_Gap(Scene):
    def construct(self):
        pg, lines, hole = gapped_page()
        l1 = label("SEC startup list", 3.65, 1.6)
        tg = tag("EXISTS · found 2026-10-02")
        banks = VGroup(*[kbox(x, 1.7, 0.42, w=1.0, d=1.0, h=0.8, taped=False) for x in (-0.3, 0.4, 1.1)])
        self.play(FadeIn(pg), FadeIn(lines), FadeIn(hole), FadeIn(l1), FadeIn(tg), run_time=rt(self, 0.08))
        self.play(FadeIn(banks), run_time=rt(self, 0.05))
        self.play(LaggedStart(*[b.animate.shift(DOWN * 4.0) for b in banks], lag_ratio=0.25), run_time=rt(self, 0.14))
        l2 = label("big banks", 3.2, -2.2)
        self.play(FadeIn(l2), run_time=rt(self, 0.05))
        to(self, 0.62)
        shadows = VGroup(*[Ellipse(width=0.8, height=0.2, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([x, -2.4, 0])
                           for x in (-0.3, 0.4, 1.1)])
        shadows.set_z_index(-1)
        self.play(FadeIn(shadows), run_time=rt(self, 0.06))
        finish(self)


class B04_Tests(Scene):
    def construct(self):
        tray = Rectangle(width=6.9, height=2.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-2.55, 0.2, 0])
        sq = VGroup(*[Square(0.5, fill_color=BAR1, fill_opacity=1, stroke_color=BAR2, stroke_width=2)
                      .move_to([-5.4 + 0.68 * (i % 9), 0.6 - 0.8 * (i // 9), 0]) for i in range(18)])
        hero = T("18 / 18", 110, bold=True).move_to([3.6, 0.6, 0])
        l1 = label("tests pass", 3.6, -0.75, 40)
        tg = tag("EXISTS · 18 / 18 · 2026-10-24")
        self.play(FadeIn(tray), FadeIn(tg), run_time=rt(self, 0.06))
        self.play(LaggedStart(*[FadeIn(s) for s in sq], lag_ratio=0.12), run_time=rt(self, 0.16))
        self.play(FadeIn(hero), FadeIn(l1), run_time=rt(self, 0.08))
        to(self, 0.62)
        self.play(Create(check(3.4, -1.85, s=0.32, w=9)), run_time=rt(self, 0.08))
        finish(self)


class B06_Second(Scene):
    def construct(self):
        pg, lines, hole = gapped_page()
        self.add(pg, lines, hole)
        pg2 = paper(4.2, -0.6, w=5.0, h=3.0)
        pg2.set_z_index(-1)
        l1 = label("second source", 2.9, -2.6)
        tg = tag("PLANNED")
        self.play(FadeIn(tg), FadeIn(pg2), run_time=rt(self, 0.08))
        self.play(pg2.animate.shift(LEFT * 3.4), run_time=rt(self, 0.16))
        self.play(FadeIn(l1), run_time=rt(self, 0.06))
        to(self, 0.62)
        fill = Rectangle(width=1.7, height=1.3, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=DIM, stroke_width=3).move_to([0.4, 0.5, 0])
        sc = scribble_block(-0.25, 0.8, 1.3, n=3, gap=0.3)
        self.play(FadeIn(fill), Create(sc), run_time=rt(self, 0.12))
        finish(self)


class B07_Eval(Scene):
    def construct(self):
        grid = VGroup(*[Square(0.5, fill_color=BOX_TOP, fill_opacity=1, stroke_color="#917A55", stroke_width=3)
                        .move_to([-4.5 + 0.66 * (i % 5), 1.5 - 0.66 * (i // 5), 0]) for i in range(25)])
        l1 = label("25 companies", -3.18, -2.2)
        tbl = Rectangle(width=4.4, height=3.2, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=4).move_to([2.8, 0.2, 0])
        head = Rectangle(width=4.4, height=0.5, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([2.8, 1.55, 0])
        rows = VGroup(*[Rectangle(width=3.6, height=0.18, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([2.8, 1.0 - 0.36 * k, 0]) for k in range(6)])
        l2 = label("2 of 25 found", 2.8, -1.95)
        tg = tag("25 RAN · 2026-10-12 / 10-25")
        self.play(FadeIn(tg), LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.04), FadeIn(l1), run_time=rt(self, 0.12))
        self.play(FadeIn(tbl), FadeIn(head), FadeIn(l2), *[s.animate.set_fill(BAR1) for s in grid], run_time=rt(self, 0.08))
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.2), run_time=rt(self, 0.12))
        to(self, 0.62)
        hits = VGroup(*[Dot(grid[k].get_center(), radius=0.12, color=TERRA) for k in (16, 19)])
        self.play(LaggedStart(*[GrowFromCenter(h) for h in hits], lag_ratio=0.3), run_time=rt(self, 0.08))
        finish(self)


class B07A_Bug(Scene):
    def construct(self):
        a = T("GOLDMAN SACHS AND CO LLC", 48)
        a.move_to([-5.6 + a.width / 2, 1.2, 0])
        la = label("hub name", -5.6 + 1.0, 2.0, 40)
        arr = Arrow([-3.6, 0.55, 0], [-3.6, -0.45, 0], color=INK, stroke_width=8, buff=0, max_tip_length_to_length_ratio=0.35)
        b = T("GOLDMAN SACHS", 48)
        b.move_to([-5.6 + b.width / 2, -1.1, 0])
        lb = label("my matcher, fixed", -5.6 + 1.7, -1.95, 40)
        tg = tag("FIXED · 2026-10-24 · test 18 / 18")
        self.play(FadeIn(tg), FadeIn(a), FadeIn(la), run_time=rt(self, 0.1))
        self.play(GrowArrow(arr), FadeIn(b), FadeIn(lb), run_time=rt(self, 0.12))
        to(self, 0.62)
        self.play(Create(check(1.9, -1.1, s=0.35, w=10)), run_time=rt(self, 0.08))
        finish(self)


class B08_Names(Scene):
    def construct(self):
        box = kbox(0.0, -1.6, 1.0)
        n1 = label("BNY Mellon", -4.2, 1.6)
        n2 = label("Bank of New York Mellon", 3.5, 1.6)
        s1 = Line([-3.6, 1.15, 0], [-1.2, 0.5, 0], color=KRAFT_EDGE, stroke_width=5)
        s2 = Line([2.6, 1.15, 0], [1.2, 0.5, 0], color=KRAFT_EDGE, stroke_width=5)
        tg = tag("PLANNED")
        self.play(FadeIn(box), FadeIn(tg), run_time=rt(self, 0.06))
        self.play(FadeIn(n1), Create(s1), run_time=rt(self, 0.08))
        self.play(FadeIn(n2), Create(s2), run_time=rt(self, 0.08))
        to(self, 0.62)
        hc = Square(0.7, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([-0.5, 2.55, 0])
        l3 = T("human check", 36)
        l3.move_to([0.25 + l3.width / 2, 2.55, 0])
        self.play(GrowFromCenter(hc), FadeIn(l3), run_time=rt(self, 0.06))
        self.play(Create(check(-0.52, 2.5, s=0.2)), run_time=rt(self, 0.05))
        finish(self)


class B09_Out(Scene):
    def construct(self):
        stop = RegularPolygon(8, radius=1.15, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.8, 0.3, 0])
        stop.rotate(PI / 8)
        bar = Rectangle(width=1.3, height=0.32, fill_color=PAGE_TOP, fill_opacity=1, stroke_width=0).move_to([-3.8, 0.3, 0])
        l1 = label("no legal advice", -3.8, -1.45)
        box = kbox(1.4, -1.4, 1.0)
        l2 = label("labelled answers", 1.6, -2.1)
        tg = tag("PLANNED")
        self.play(FadeIn(tg), FadeIn(box), run_time=rt(self, 0.08))
        self.play(GrowFromCenter(stop), FadeIn(bar), run_time=rt(self, 0.1))
        self.play(FadeIn(l1), FadeIn(l2), run_time=rt(self, 0.08))
        to(self, 0.62)
        tags = VGroup()
        for y, c in ((0.9, BAR1), (0.25, BAR2), (-0.4, BAR3)):
            tags.add(Line([3.0, y + 0.1, 0], [3.5, y, 0], color=KRAFT_EDGE, stroke_width=4),
                     Rectangle(width=0.7, height=0.42, fill_color=c, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([3.95, y, 0]))
        self.play(LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.1), run_time=rt(self, 0.12))
        finish(self)


class B10_Reader(Scene):
    def construct(self):
        win = Rectangle(width=6.8, height=4.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-1.9, -0.3, 0])
        band = Rectangle(width=6.8, height=0.42, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-1.9, 1.49, 0])
        rows = VGroup(*[Rectangle(width=w, height=0.3, fill_color=BAR3 if i else BAR1, fill_opacity=1, stroke_width=0)
                        .move_to([-4.8 + w / 2, 0.75 - 0.6 * i, 0]) for i, w in enumerate((2.0, 4.4, 4.4, 4.4, 4.4))])
        q = T("?", 56, bold=True).move_to([0.3, -0.45, 0])
        tg = tag("CONSTRUCTED · not built yet")
        l1 = label("one command", -3.8, -2.75)
        self.play(FadeIn(tg), FadeIn(win), FadeIn(band), run_time=rt(self, 0.08))
        self.play(FadeIn(rows[0]), FadeIn(l1), run_time=rt(self, 0.06))
        self.play(LaggedStart(*[FadeIn(r) for r in rows[1:]], lag_ratio=0.2), FadeIn(q), run_time=rt(self, 0.12))
        to(self, 0.62)
        tbl = VGroup(Rectangle(width=2.6, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=4).move_to([4.5, -0.3, 0]),
                     Line([4.5, 0.85, 0], [4.5, -1.45, 0], color=GHOST, stroke_width=4))
        marks = VGroup(check(3.85, 0.4, s=0.2), check(3.85, -0.5, s=0.2),
                       VGroup(Line([5.0, 0.6, 0], [5.4, 0.2, 0], color=INK, stroke_width=7), Line([5.0, 0.2, 0], [5.4, 0.6, 0], color=INK, stroke_width=7)))
        l2 = label("right / wrong", 4.5, -2.1, 36)
        self.play(FadeIn(tbl), FadeIn(l2), run_time=rt(self, 0.06))
        self.play(Create(marks), run_time=rt(self, 0.06))
        finish(self)


class B05_Hub(Scene):
    def construct(self):
        win = Rectangle(width=6.8, height=3.6, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-2.3, 0.1, 0])
        band = Rectangle(width=6.8, height=0.42, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-2.3, 1.69, 0])
        query = Rectangle(width=5.6, height=0.6, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-2.3, 0.95, 0])
        q = T("Capital One", 36).move_to([-2.3, 0.95, 0])
        r1 = fit(T("CAPITAL ONE NATIONAL ASSOCIATION", 34), 5.6).move_to([-2.3, 0.05, 0])
        r2 = fit(T("CAPITAL ONE SERVICES LLC", 34), 5.6)
        r2.move_to([r1.get_left()[0] + r2.width / 2, -0.65, 0])
        r1.move_to([r1.get_left()[0] + r1.width / 2, 0.05, 0])
        l1 = label("one employer at a time", -2.3, -2.3)
        pillr = Rectangle(width=2.6, height=0.8, fill_color=GHOST, fill_opacity=1, stroke_color=BAR1, stroke_width=4).move_to([4.2, 0.3, 0])
        l2 = label("job title", 4.2, -0.6)
        tg = tag("MY SEARCH · uscis.gov · 2026-10-25")
        self.play(FadeIn(tg), FadeIn(win), FadeIn(band), FadeIn(query), FadeIn(q), run_time=rt(self, 0.08))
        self.play(FadeIn(r1), FadeIn(r2), FadeIn(l1), run_time=rt(self, 0.1))
        self.play(FadeIn(pillr), FadeIn(l2), run_time=rt(self, 0.08))
        to(self, 0.62)
        x = VGroup(Line([3.0, -0.15, 0], [5.4, 0.75, 0], color=INK, stroke_width=9),
                   Line([3.0, 0.75, 0], [5.4, -0.15, 0], color=INK, stroke_width=9))
        self.play(Create(x), run_time=rt(self, 0.08))
        finish(self)


class B05A_Mellon(Scene):
    def construct(self):
        names = ["BNY Mellon Government Securities Services Corp", "BNY Mellon Investment Adviser Inc",
                 "Carnegie Mellon University", "The Bank of New York Mellon"]
        rows = VGroup()
        for k, n in enumerate(names):
            t = T(n, 40)
            t.move_to([-4.6 + t.width / 2, 1.0 - 0.95 * k, 0])
            rows.add(t)
        head = T("search: Mellon", 40)
        head.move_to([-4.6 + head.width / 2, 1.95, 0])
        tg = tag("SEARCHED · uscis.gov · 2026-10-12")
        self.play(FadeIn(tg), FadeIn(head), run_time=rt(self, 0.06))
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.25), run_time=rt(self, 0.16))
        to(self, 0.62)
        marks = VGroup()
        for k in (0, 1, 3):
            marks.add(Square(0.42, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-5.2, 1.0 - 0.95 * k, 0]))
        cy = 1.0 - 0.95 * 2
        marks.add(VGroup(Line([-5.4, cy - 0.2, 0], [-5.0, cy + 0.2, 0], color=INK, stroke_width=8),
                         Line([-5.4, cy + 0.2, 0], [-5.0, cy - 0.2, 0], color=INK, stroke_width=8)))
        self.play(LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.15), run_time=rt(self, 0.1))
        finish(self)


class B11_Why(Scene):
    def construct(self):
        box = kbox(-2.2, -1.8, 1.0)
        cal = Rectangle(width=1.9, height=1.9, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([2.6, -0.5, 0])
        band = Rectangle(width=1.9, height=0.4, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([2.6, 0.25, 0])
        cells = VGroup(*[Square(0.34, fill_color=(TERRA if (i, j) == (2, 0) else GHOST), fill_opacity=1, stroke_width=0)
                         .move_to([2.1 + 0.5 * j, -0.35 - 0.5 * i, 0]) for i in range(3) for j in range(3)])
        l1 = label("my own question", -2.2, -2.55, 42)
        l2 = label("co-op dates", 2.6, -2.2, 42)
        tg = tag("WHY THIS PROJECT")
        self.play(FadeIn(tg), FadeIn(box, shift=DOWN * 0.6), run_time=rt(self, 0.1))
        self.play(FadeIn(VGroup(cal, band, cells)), FadeIn(l1), FadeIn(l2), run_time=rt(self, 0.1))
        q = T("?", 120, bold=True).move_to([-0.1, 1.3, 0])
        self.play(FadeIn(q), run_time=rt(self, 0.08))
        to(self, 0.62)
        self.play(GrowFromCenter(Dot([-0.1, 0.35, 0], radius=0.1, color=TERRA)), run_time=rt(self, 0.08))
        finish(self)


class B11A_Skills(Scene):
    def construct(self):
        t1 = Rectangle(width=5.0, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.1, 0.2, 0])
        blocks = VGroup(*[Square(0.7, fill_color=BAR3, fill_opacity=1, stroke_color=BAR2, stroke_width=2)
                          .move_to([-4.6 + 1.0 * (i % 4), 0.7 - 1.0 * (i // 4), 0]) for i in range(6)])
        l1 = label("already have", -3.1, 1.95, 42)
        l2 = label("Giesecke+Devrient", -3.1, -1.6, 42)
        t2 = Rectangle(width=4.2, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([3.4, 0.2, 0])
        l3 = label("new", 3.4, 1.95, 42)
        l4 = label("second source", 3.4, -1.6, 42)
        tg = tag("WHY THIS PROJECT")
        self.play(FadeIn(tg), FadeIn(t1), FadeIn(l1), run_time=rt(self, 0.08))
        self.play(LaggedStart(*[FadeIn(b) for b in blocks], lag_ratio=0.15), FadeIn(l2), run_time=rt(self, 0.12))
        self.play(FadeIn(t2), FadeIn(l3), FadeIn(l4), run_time=rt(self, 0.08))
        to(self, 0.62)
        pg = Rectangle(width=1.5, height=1.8, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([3.4, 0.2, 0])
        lines = VGroup(*[Line([2.9, y, 0], [3.9, y, 0], color=GHOST, stroke_width=6) for y in (0.7, 0.3, -0.1)])
        self.play(FadeIn(pg, shift=DOWN * 0.5), Create(lines), run_time=rt(self, 0.1))
        finish(self)


class BWHAT_Repo(Scene):
    def construct(self):
        tray = Rectangle(width=9.6, height=3.4, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([0.0, -0.3, 0])
        tab = Rectangle(width=2.6, height=0.5, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-3.4, 1.65, 0])
        box = kbox(-3.4, -1.3, 0.8)
        grid = VGroup(*[Square(0.36, fill_color=BOX_TOP, fill_opacity=1, stroke_color="#917A55", stroke_width=3)
                        .move_to([-0.72 + 0.48 * (i % 4), 0.55 - 0.48 * (i // 4), 0]) for i in range(16)])
        pg = Rectangle(width=1.5, height=1.9, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=BAR1, stroke_width=4).move_to([3.4, -0.1, 0])
        lines = VGroup(*[Line([2.9, y, 0], [3.9, y, 0], color=GHOST, stroke_width=6) for y in (0.45, 0.05, -0.35)])
        ls = VGroup(label("tool", -3.4, -2.55, 42), label("evaluation set", 0.0, -2.55, 42), label("failure log", 3.4, -2.55, 42))
        lr = label("GitHub repository", 2.4, 1.85, 42)
        tg = tag("PLANNED · finished form")
        self.play(FadeIn(tg), FadeIn(tray), FadeIn(lr), run_time=rt(self, 0.08))
        self.play(FadeIn(box, shift=DOWN * 0.5), FadeIn(grid, shift=DOWN * 0.5), FadeIn(VGroup(pg, lines), shift=DOWN * 0.5), FadeIn(ls), run_time=rt(self, 0.14))
        to(self, 0.62)
        self.play(FadeIn(tab), run_time=rt(self, 0.06))
        finish(self)


class B09P_Proves(Scene):
    def construct(self):
        xs = (-4.0, 0.0, 4.0)
        trays = VGroup(*[Rectangle(width=3.4, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, 0.2, 0]) for x in xs])
        tags3 = VGroup(*[Rectangle(width=0.8, height=0.4, fill_color=c, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-4.0, 0.9 - 0.6 * k, 0])
                         for k, c in enumerate((BAR1, BAR2, BAR3))])
        rows = VGroup(*[Rectangle(width=2.4, height=0.16, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([0.0, 1.0 - 0.3 * k, 0]) for k in range(6)])
        pg = Rectangle(width=1.3, height=1.8, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=BAR1, stroke_width=4).move_to([3.6, 0.2, 0])
        plines = VGroup(*[Line([3.15, y, 0], [4.05, y, 0], color=GHOST, stroke_width=6) for y in (0.75, 0.4, 0.05, -0.3)])
        ptr = Arrow([5.2, 0.05, 0], [4.25, 0.05, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.35)
        ls = VGroup(label("verification", -4.0, -1.55, 42), label("evaluation", 0.0, -1.55, 42), label("source grounding", 4.0, -1.55, 42))
        tg = tag("WHAT IT PROVES")
        self.play(FadeIn(tg), FadeIn(trays), FadeIn(ls), run_time=rt(self, 0.08))
        self.play(FadeIn(tags3), FadeIn(rows), FadeIn(VGroup(pg, plines)), GrowArrow(ptr), run_time=rt(self, 0.12))
        to(self, 0.62)
        self.play(LaggedStart(*[GrowFromCenter(Dot([x, -2.2, 0], radius=0.1, color=TERRA)) for x in xs], lag_ratio=0.25), run_time=rt(self, 0.1))
        finish(self)


class B07B_Brand(Scene):
    def construct(self):
        typed = T("Robinhood", 54)
        typed.move_to([-5.4 + typed.width / 2, 1.2, 0])
        lt = label("typed", -5.4 + 0.6, 2.0, 40)
        x0 = -5.4 + typed.width + 0.4
        arr = Arrow([x0, 1.2, 0], [x0 + 1.4, 1.2, 0], color=INK, stroke_width=8, buff=0, max_tip_length_to_length_ratio=0.3)
        q = T("?", 110, bold=True).move_to([x0 + 2.1, 1.2, 0])
        row = T("ROBINHOOD MARKETS INC · 824", 44)
        row.move_to([-5.4 + row.width / 2, -1.2, 0])
        lr = label("in my data, missed", -5.4 + 1.85, -2.05, 40)
        tg = tag("FOUND · 2026-10-25")
        self.play(FadeIn(tg), FadeIn(typed), FadeIn(lt), run_time=rt(self, 0.08))
        self.play(GrowArrow(arr), FadeIn(q), run_time=rt(self, 0.08))
        self.play(FadeIn(row), FadeIn(lr), run_time=rt(self, 0.08))
        to(self, 0.62)
        self.play(GrowFromCenter(Dot([-5.75, -1.2, 0], radius=0.12, color=TERRA)), run_time=rt(self, 0.08))
        finish(self)



# ═════════════════════════════ Final Project Film beats (2026-11-23) ═════════════════════════════

class BOS_OpenSanctions(Scene):
    def construct(self):
        win = Rectangle(width=5.4, height=4.4, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-2.9, -0.25, 0])
        query = Rectangle(width=4.4, height=0.6, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-2.9, 1.6, 0])
        q = T("Chime", 36).move_to([-2.9, 1.6, 0])
        rows = VGroup()
        for k in range(11):
            y = 0.95 - 0.3 * k
            person = k not in (2, 7)
            rows.add(Circle(0.1, fill_color=BAR1 if person else INK, fill_opacity=1, stroke_width=0).move_to([-5.0, y, 0]))
            rows.add(Rectangle(width=3.4 if person else 2.6, height=0.14, fill_color=BAR2 if person else INK, fill_opacity=1,
                               stroke_width=0).move_to([-3.0 if person else -3.4, y, 0]))
        l1 = label("11 results, mostly people", -2.9, -2.95)
        miss = T("Chime Financial Inc", 44).move_to([3.6, 0.3, 0])
        l2 = label("not in the ones I reviewed", 3.4, -0.55)
        tg = tag("MY SEARCH · opensanctions.org")
        self.play(FadeIn(tg), FadeIn(win), FadeIn(query), FadeIn(q), run_time=rt(self, 0.08))
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.05), FadeIn(l1), run_time=rt(self, 0.14))
        self.play(FadeIn(miss), run_time=rt(self, 0.06))
        to(self, 0.62)
        mark = cross(miss.get_left()[0] - 0.55, 0.3, s=0.22, w=8)
        self.play(Create(mark), FadeIn(l2), run_time=rt(self, 0.08))
        finish(self)


class BGL_Gleif(Scene):
    def construct(self):
        b1 = T("Robinhood", 48).move_to([-4.6, 1.3, 0])
        b2 = T("SoFi", 48).move_to([-4.6, -0.9, 0])
        lb = label("brand", -4.6, 2.3, 36)
        n1 = fit(T("ROBINHOOD MARKETS, INC.", 42), 6.4)
        n1.move_to([-0.6 + n1.width / 2, 1.3, 0])
        n2 = fit(T("SOCIAL FINANCE, LLC", 42), 6.4)
        n2.move_to([-0.6 + n2.width / 2, -0.9, 0])
        prev = T("previously SOCIAL FINANCE, INC.", 32, color=DIM)
        prev.move_to([-0.6 + prev.width / 2, -1.7, 0])
        ln = label("legal name", -0.6 + 1.1, 2.3, 36)
        a1 = Arrow([-3.0, 1.3, 0], [-0.8, 1.3, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.2)
        a2 = Arrow([-3.0, -0.9, 0], [-0.8, -0.9, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.2)
        tg = tag("MY SEARCH · gleif.org")
        self.play(FadeIn(tg), FadeIn(lb), FadeIn(ln), FadeIn(b1), run_time=rt(self, 0.08))
        self.play(GrowArrow(a1), FadeIn(n1), run_time=rt(self, 0.1))
        self.play(FadeIn(b2), GrowArrow(a2), FadeIn(n2), run_time=rt(self, 0.12))
        to(self, 0.62)
        self.play(FadeIn(prev), run_time=rt(self, 0.08))
        finish(self)


class BCARE_Why(Scene):
    def construct(self):
        br = T("Chime", 52).move_to([-4.4, 0.2, 0])
        lb = label("what you type", -4.4, -0.7, 36)
        n1 = T("CHIME FINANCIAL INC", 40)
        n1.move_to([-0.4 + n1.width / 2, 1.3, 0])
        n2 = T("CHIME INC", 40)
        n2.move_to([-0.4 + n2.width / 2, -0.9, 0])
        s1 = Line([-3.2, 0.4, 0], [-0.6, 1.3, 0], color=KRAFT_EDGE, stroke_width=5)
        s2 = Line([-3.2, 0.0, 0], [-0.6, -0.9, 0], color=KRAFT_EDGE, stroke_width=5)
        self.play(FadeIn(br), FadeIn(lb), run_time=rt(self, 0.06))
        self.play(Create(s1), FadeIn(n1), Create(s2), FadeIn(n2), run_time=rt(self, 0.14))
        to(self, 0.62)
        hc = Square(0.7, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([1.0, -2.5, 0])
        l3 = T("you verify", 40)
        l3.move_to([1.6 + l3.width / 2, -2.5, 0])
        self.play(GrowFromCenter(hc), FadeIn(l3), run_time=rt(self, 0.06))
        self.play(Create(check(0.98, -2.55, s=0.2)), run_time=rt(self, 0.05))
        finish(self)


class BFIX_Brand(Scene):
    def construct(self):
        c = T("Chime", 46).move_to([-5.0, 1.5, 0])
        c1 = T("CHIME FINANCIAL INC", 36)
        c1.move_to([-2.6 + c1.width / 2, 2.0, 0])
        c2 = T("CHIME INC", 36)
        c2.move_to([-2.6 + c2.width / 2, 1.0, 0])
        lc = T("first word", 32, color=DIM)
        lc.move_to([3.6 + lc.width / 2, 1.5, 0])
        ca = VGroup(Line([-4.1, 1.6, 0], [-2.8, 2.0, 0], color=KRAFT_EDGE, stroke_width=5),
                    Line([-4.1, 1.4, 0], [-2.8, 1.0, 0], color=KRAFT_EDGE, stroke_width=5))
        f = T("SoFi", 46).move_to([-5.0, -0.8, 0])
        al = Arrow([-4.2, -0.8, 0], [-2.8, -0.8, 0], color=INK, stroke_width=7, buff=0, max_tip_length_to_length_ratio=0.25)
        f1 = T("SOCIAL FINANCE INC", 36)
        f1.move_to([-2.6 + f1.width / 2, -0.8, 0])
        lf = T("alias I wrote", 32, color=DIM)
        lf.move_to([3.6 + lf.width / 2, -0.8, 0])
        tg = tag("BUILT · 2026-11-23 · 26 tests pass")
        self.play(FadeIn(tg), FadeIn(c), run_time=rt(self, 0.06))
        self.play(Create(ca), FadeIn(c1), FadeIn(c2), FadeIn(lc), run_time=rt(self, 0.12))
        self.play(FadeIn(f), GrowArrow(al), FadeIn(f1), FadeIn(lf), run_time=rt(self, 0.14))
        to(self, 0.62)
        hc = Square(0.7, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([-2.2, -2.6, 0])
        l3 = T("a person picks", 40)
        l3.move_to([-1.6 + l3.width / 2, -2.6, 0])
        self.play(GrowFromCenter(hc), FadeIn(l3), run_time=rt(self, 0.06))
        self.play(Create(check(-2.22, -2.65, s=0.2)), run_time=rt(self, 0.05))
        finish(self)


class BRES_Need(Scene):
    def construct(self):
        lap = VGroup(Rectangle(width=2.0, height=1.3, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-5.0, 0.6, 0]),
                     Polygon([-6.0, -0.15, 0], [-4.0, -0.15, 0], [-3.75, -0.45, 0], [-6.25, -0.45, 0],
                             fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4))
        py = paper(-1.7, 0.4, w=1.6, h=2.0)
        pys = VGroup(*[Line([-2.2 + 0.25 * (k % 2), 1.0 - 0.38 * k, 0], [-1.2 - 0.3 * (k == 2), 1.0 - 0.38 * k, 0], color=INK, stroke_width=7) for k in range(4)])
        tray = kbox(1.4, -0.6, 0.7, taped=False)
        data = paper(4.9, 0.4, w=1.6, h=2.0)
        ds = VGroup(*[Line([4.3, 1.0 - 0.35 * k, 0], [5.5, 1.0 - 0.35 * k, 0], color=BAR1, stroke_width=6) for k in range(4)])
        labs = VGroup(label("laptop", -5.0, -1.3, 42), label("Python", -1.7, -1.3, 42),
                      label("GitHub", 1.4, -1.3, 42), label("public data", 4.9, -1.3, 42))
        tg = tag("I HAVE WHAT I NEED")
        self.play(FadeIn(tg), FadeIn(lap), FadeIn(py), Create(pys), run_time=rt(self, 0.1))
        self.play(FadeIn(tray), FadeIn(data), Create(ds), FadeIn(labs), run_time=rt(self, 0.12))
        to(self, 0.62)
        pl = pill(0.0, -2.6, 10.6, h=0.8, fill=CARD)
        pl.set_stroke(INK, 4)
        pt = T("no AI model at run time · no paid credits", 40).move_to([0.0, -2.6, 0])
        self.play(FadeIn(pl), FadeIn(pt), run_time=rt(self, 0.08))
        finish(self)


class BAFTER_Result(Scene):
    def construct(self):
        rows = [("strong sponsor missed", "3", "0"), ("wrong automatic answer", "1", "0"), ("sent to a person", "0", "6")]
        hb = T("October", 38, color=DIM).move_to([2.4, 1.7, 0])
        ha = T("now", 38, bold=True).move_to([4.6, 1.7, 0])
        rule = Line([-6.0, 1.25, 0], [5.6, 1.25, 0], color=BAR1, stroke_width=4)
        names, befores, afters = VGroup(), VGroup(), VGroup()
        for k, (n, b, a) in enumerate(rows):
            y = 0.55 - 1.0 * k
            t = T(n, 40)
            t.move_to([-5.8 + t.width / 2, y, 0])
            names.add(t)
            befores.add(T(b, 56, color=DIM).move_to([2.4, y, 0]))
            afters.add(T(a, 56, bold=True).move_to([4.6, y, 0]))
        tg = tag("MEASURED · 2026-11-23 · same 25 companies")
        self.play(FadeIn(tg), FadeIn(hb), Create(rule), FadeIn(names), run_time=rt(self, 0.1))
        self.play(LaggedStart(*[FadeIn(b) for b in befores], lag_ratio=0.3), run_time=rt(self, 0.12))
        to(self, 0.62)
        arrows = VGroup(*[Arrow([2.95, 0.55 - 1.0 * k, 0], [4.05, 0.55 - 1.0 * k, 0], color=BAR1, stroke_width=6, buff=0,
                                max_tip_length_to_length_ratio=0.3) for k in range(3)])
        self.play(FadeIn(ha), LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), run_time=rt(self, 0.08))
        self.play(LaggedStart(*[FadeIn(a) for a in afters], lag_ratio=0.3), run_time=rt(self, 0.1))
        finish(self)


class BBAR_PassFail(Scene):
    def construct(self):
        hp = T("PASS", 48, bold=True)
        hp.move_to([-5.9 + hp.width / 2, 2.05, 0])
        P = ["at least 20 of 25 verified", "0 wrong automatic answers", "uncertain → unknown or a person"]
        F = ["confirms a wrong company", "no better coverage"]
        pl = VGroup()
        for k, t in enumerate(P):
            y = 1.35 - 0.68 * k
            a = T(t, 44)
            a.move_to([-5.0 + a.width / 2, y, 0])
            pl.add(VGroup(a, check(-5.5, y, s=0.17)))
        rule = Line([-5.9, -0.95, 0], [5.9, -0.95, 0], color=BAR2, stroke_width=4)
        hf = T("FAIL", 48, bold=True)
        hf.move_to([-5.9 + hf.width / 2, -1.55, 0])
        fl = VGroup()
        for k, t in enumerate(F):
            y = -2.25 - 0.68 * k
            b = T(t, 44)
            b.move_to([-5.0 + b.width / 2, y, 0])
            fl.add(VGroup(b, cross(-5.5, y, s=0.17, w=6)))
        tg = tag("MY TARGET · after the hub is added")
        self.play(FadeIn(tg), FadeIn(hp), run_time=rt(self, 0.06))
        self.play(LaggedStart(*[FadeIn(x) for x in pl], lag_ratio=0.25), run_time=rt(self, 0.18))
        to(self, 0.62)
        self.play(Create(rule), FadeIn(hf), run_time=rt(self, 0.06))
        self.play(LaggedStart(*[FadeIn(x) for x in fl], lag_ratio=0.25), run_time=rt(self, 0.12))
        finish(self)
