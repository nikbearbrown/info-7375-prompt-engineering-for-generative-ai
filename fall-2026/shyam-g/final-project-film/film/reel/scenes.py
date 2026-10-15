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


# ═════════════════════════════ STOPLINE PITCH SCENES ═════════════════════════════
# Written for the StopLine pitch (INFO 7375). Everything above this line is the
# toolkit's iso_kit.py, pasted verbatim as the show-tell skill requires.
# Cast, kept the whole film: the kraft crate (a lot), white record pages
# (evidence), a dark terminal block (the tool), three lanes (the outcomes).
# Timing: at(self, f) waits until fraction f of the measured beat audio.
# Every animation is kept out of the 0.40-0.60 window GATE T and Gate V sample,
# labels land before 0.40, and each scene adds a new shape after 0.60.


def at(self, frac):
    target = _TARGET.get(type(self).__name__.split("_")[0], 0)
    if not target:
        self.wait(0.6)
        return
    gap = target * frac - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def crate(iso, x0, y0, w=1.6, d=1.6, h=1.2):
    """The lot: a closed kraft box with terracotta tape."""
    return VGroup(iso.box(x0, y0, 0, w, d, h), iso.tape(x0, y0, h, w, d))


def record(x, y, w=1.5, h=1.9, n=3):
    """An evidence record: a flat page with scribbled lines. The scribbles are taller
    than the kit default (amp 0.11, not 0.07): GATE T reads them as text runs, and at
    the default height they measured 40-41 px against its 41 px floor."""
    pg = paper(x, y, w, h)
    lw, top = w - 0.5, y + h / 2 - 0.42
    lines = VGroup(*[scribble(x - lw / 2, top - i * 0.42, lw * (0.62 if i == n - 1 else 1.0), amp=0.11)
                     for i in range(n)])
    return VGroup(pg, lines)


def terminal(x, y, w=2.6, h=1.7):
    """The tool: a dark panel with a prompt chevron and a ghost light."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    chev = VGroup(Line([x - w / 2 + 0.3, y + 0.35, 0], [x - w / 2 + 0.5, y + 0.2, 0], color=CARD, stroke_width=6),
                  Line([x - w / 2 + 0.5, y + 0.2, 0], [x - w / 2 + 0.3, y + 0.05, 0], color=CARD, stroke_width=6))
    light = Dot([x + w / 2 - 0.3, y + h / 2 - 0.28, 0], radius=0.08, color=GHOST)
    g = VGroup(body, chev, light)
    g.light = light
    return g


def lane(x, y, w=6.0, h=0.9):
    return RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=CARD, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])


def badge(x, y, r=0.6, lit=True):
    ring = Circle(radius=r, fill_color=BOX_TOP if lit else STAGE, fill_opacity=1,
                  stroke_color=INK if lit else GHOST, stroke_width=4).move_to([x, y, 0])
    return ring


class B00_Crate(Scene):
    def construct(self):
        iso = Iso(-3.6, -2.2, 1.0)
        box = crate(iso, 0, 0)
        shadow = Ellipse(width=3.0, height=0.6, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-3.6, -2.25, 0])
        box.shift(UP * 3)
        self.add(shadow)
        self.play(box.animate.shift(DOWN * 3), run_time=0.8, rate_func=ease_in)
        lot = T("lot", 42).move_to([-3.6, -3.0, 0])
        self.play(FadeIn(lot), run_time=0.4)
        at(self, 0.22)
        sheet = record(0.2, 0.4, 1.7, 2.1)
        recs = VGroup(record(3.6, 1.3, 1.5, 1.7, n=2), record(3.9, -1.0, 1.5, 1.7, n=2))
        self.play(FadeIn(sheet, shift=UP * 0.3), run_time=0.6)
        self.play(FadeIn(recs, shift=UP * 0.3), run_time=0.6)
        lab1 = T("proposed action", 42).move_to([0.2, -1.2, 0])
        lab2 = T("evidence", 42).move_to([3.75, -2.5, 0])
        self.play(FadeIn(lab1), FadeIn(lab2), run_time=0.4)
        at(self, 0.62)
        arrow = Arrow([1.15, 0.4, 0], [2.75, 0.4, 0], color=INK, stroke_width=6, buff=0, max_tip_length_to_length_ratio=0.2)
        self.play(GrowArrow(arrow), run_time=0.7)
        finish(self)


class B01_Parts(Scene):
    def construct(self):
        term = terminal(-4.0, 0.3)
        self.play(FadeIn(term, shift=UP * 0.4), run_time=0.6)
        l1 = T("CLI", 36).move_to([-4.0, -1.2, 0])
        self.play(FadeIn(l1), run_time=0.3)
        at(self, 0.22)
        pages = VGroup(*[record(0.0 + i * 0.18, 0.3 - i * 0.18, 1.6, 2.0, n=2) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.3), run_time=0.9)
        l2 = T("tests", 36).move_to([0.2, -1.6, 0])
        self.play(FadeIn(l2), run_time=0.3)
        at(self, 0.62)
        rep = paper(4.2, 0.3, 1.9, 2.4)
        bars = VGroup(*[Rectangle(width=0.32, height=hgt, fill_color=c, fill_opacity=1, stroke_width=0)
                        .move_to([3.6 + i * 0.45, -0.6 + hgt / 2, 0])
                        for i, (hgt, c) in enumerate([(0.9, BAR1), (1.4, BAR2), (0.6, BAR1)])])
        l3 = T("report", 36).move_to([4.2, -1.6, 0])
        self.play(FadeIn(rep), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), FadeIn(l3), run_time=0.7)
        finish(self)


class B02_Lanes(Scene):
    def construct(self):
        ys = [1.6, 0.0, -1.6]
        names = ["human review", "more evidence", "accept for review"]
        lanes = VGroup(*[lane(0.6, y) for y in ys])
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3) for l in lanes], lag_ratio=0.2), run_time=0.9)
        labs = VGroup(*[T(n, 34).move_to([-4.6, y, 0]) for n, y in zip(names, ys)])
        self.play(FadeIn(labs), run_time=0.4)
        marker = Square(side_length=0.5, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([0.6, -1.6, 0])
        self.play(FadeIn(marker), run_time=0.3)
        at(self, 0.62)
        self.play(marker.animate.move_to([0.6, 0.0, 0]), run_time=0.4)
        self.play(marker.animate.move_to([0.6, 1.6, 0]), run_time=0.4)
        dot = Dot([3.2, 1.6, 0], radius=0.14, color=TERRA)
        self.play(GrowFromCenter(dot), run_time=0.4)
        finish(self)


class B03_Run(Scene):
    def construct(self):
        panel = RoundedRectangle(width=9.6, height=4.0, corner_radius=0.15, fill_color=DARK_TOP, fill_opacity=1,
                                 stroke_color=INK, stroke_width=4).move_to([0, 0.5, 0])
        self.play(FadeIn(panel), run_time=0.6)
        cap = T("real run · synthetic data", 34).move_to([0, -2.3, 0])
        self.play(FadeIn(cap), run_time=0.3)
        at(self, 0.2)
        # Three lines copied from reports/cli_output.txt and reports/test_run.txt (run 2026-10-14).
        lines = ["INC-001  ACCEPT FOR REVIEW", "INC-003  HUMAN REVIEW REQUIRED", "Ran 12 tests   OK"]
        txt = VGroup(*[Text(s, font="DejaVu Sans Mono", color=CARD, font_size=36) for s in lines]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        if txt.width > 7.4:
            txt.scale_to_fit_width(7.4)
        txt.move_to([-0.5, 0.5, 0])
        self.play(LaggedStart(*[FadeIn(t) for t in txt], lag_ratio=0.35), run_time=1.0)
        at(self, 0.62)
        ok = check(3.9, -0.55, s=0.28, color=TERRA, w=9)
        self.play(Create(ok), run_time=0.5)
        finish(self)


class B04_SAP(Scene):
    def construct(self):
        cols = [-1.8, 2.2]
        heads = VGroup(T("SAP QM", 36).move_to([cols[0], 2.4, 0]), T("StopLine", 36).move_to([cols[1], 2.4, 0]))
        rows = [1.3, 0.3, -0.7, -1.7]
        cells = VGroup(*[RoundedRectangle(width=1.6, height=0.75, corner_radius=0.1, fill_color=CARD, fill_opacity=1,
                                          stroke_color=INK, stroke_width=3).move_to([c, r, 0]) for r in rows for c in cols])
        self.play(FadeIn(heads), FadeIn(cells), run_time=0.8)
        tag = T("sketch", 32).move_to([-5.0, -2.8, 0])
        self.play(FadeIn(tag), run_time=0.3)
        at(self, 0.2)
        ticks = VGroup(*[check(c - 0.1, r, s=0.18) for r in rows[:3] for c in cols])
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), run_time=1.2)
        at(self, 0.62)
        ring = VGroup(*[Circle(radius=0.22, stroke_color=DIM, stroke_width=4).move_to([c, rows[3], 0]) for c in cols])
        self.play(Create(ring), run_time=0.6)
        finish(self)


class B05_Hold(Scene):
    def construct(self):
        iso = Iso(-4.0, -1.6, 0.9)
        box = crate(iso, 0, 0)
        self.play(FadeIn(box, shift=DOWN * 0.3), run_time=0.6)
        bar = Rectangle(width=3.4, height=0.28, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-4.0, 1.4, 0])
        self.play(FadeIn(bar), run_time=0.4)
        l1 = T("on hold", 36).move_to([-4.0, -2.8, 0])
        self.play(FadeIn(l1), run_time=0.3)
        at(self, 0.22)
        term = terminal(0.6, 0.6, 2.8, 1.8)
        self.play(FadeIn(term, shift=UP * 0.3), run_time=0.6)
        at(self, 0.62)
        rep = record(4.3, 0.4, 1.8, 2.3, n=3)
        l2 = T("report", 36).move_to([4.3, -1.3, 0])
        self.play(FadeIn(rep, shift=LEFT * 0.4), FadeIn(l2), run_time=0.7)
        self.play(term.light.animate.set_color(TERRA), run_time=0.3)
        finish(self)


class B06_Badges(Scene):
    def construct(self):
        xs = [-4.6, -2.3, 0.0, 2.3, 4.6]
        rings = VGroup(*[badge(x, 0.6, lit=i < 3) for i, x in enumerate(xs)])
        self.play(LaggedStart(*[FadeIn(r) for r in rings], lag_ratio=0.15), run_time=0.9)
        labs = VGroup(*[T(n, 34).move_to([x, -0.6, 0]) for n, x in zip(["verify", "evaluate", "escalate"], xs)])
        self.play(FadeIn(labs), run_time=0.4)
        at(self, 0.2)
        dots = VGroup(*[Dot([x, 0.6, 0], radius=0.14, color=TERRA) for x in xs[:3]])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.25), run_time=0.8)
        at(self, 0.62)
        slashes = VGroup(*[Line([x - 0.45, 0.15, 0], [x + 0.45, 1.05, 0], color=DIM, stroke_width=6) for x in xs[3:]])
        self.play(Create(slashes), run_time=0.6)
        finish(self)


class B07_Fence(Scene):
    def construct(self):
        posts = VGroup(*[Rectangle(width=0.16, height=1.2, fill_color=BAR1, fill_opacity=1, stroke_width=0)
                         .move_to([0.0, y, 0]) for y in (-2.2, -0.9, 0.4, 1.7)])
        rail = Line([0, -2.6, 0], [0, 2.4, 0], color=BAR1, stroke_width=6)
        self.play(Create(rail), FadeIn(posts), run_time=0.7)
        l1 = T("out of scope", 34).move_to([-3.3, -2.8, 0])
        l2 = T("first piece", 34).move_to([3.3, -2.8, 0])
        self.play(FadeIn(l1), FadeIn(l2), run_time=0.3)
        at(self, 0.2)
        iso = Iso(-4.6, -0.9, 0.8)
        box = crate(iso, 0, 0)
        model = Iso(-2.0, -0.4, 0.8).mcp(0, 0, 0)
        self.play(FadeIn(box, shift=DOWN * 0.2), FadeIn(model, shift=DOWN * 0.2), run_time=0.7)
        term = terminal(3.3, 0.2)
        self.play(FadeIn(term), run_time=0.5)
        at(self, 0.62)
        glow = Circle(radius=0.22, stroke_color=TERRA, stroke_width=5).move_to(term.light.get_center())
        self.play(term.light.animate.set_color(TERRA), Create(glow), run_time=0.5)
        finish(self)


class B08_Gate(Scene):
    def construct(self):
        # Twelve small crates in two rows (the lot of 1,200); a rope round the first four (400 contained).
        crates = VGroup(*[crate(Iso(0.6 + col * 1.0, -0.4 - row * 1.3, 0.34), 0, 0, 1.5, 1.5, 1.1)
                          for row in range(2) for col in range(6)])
        self.play(LaggedStart(*[FadeIn(c) for c in crates], lag_ratio=0.05), run_time=1.0)
        rope = RoundedRectangle(width=2.2, height=2.7, corner_radius=0.2, stroke_color=TERRA, stroke_width=5,
                                fill_opacity=0).move_to([1.1, -0.85, 0])
        l1 = T("1,200 in lot", 34).move_to([4.3, -2.8, 0])
        self.play(Create(rope), FadeIn(l1), run_time=0.7)
        at(self, 0.2)
        posts = VGroup(*[Rectangle(width=0.22, height=2.2, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0)
                         .move_to([x, 0.1, 0]) for x in (-3.4, -1.6)])
        arm = Rectangle(width=0.18, height=1.8, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-3.4, 2.1, 0])
        ticket = Rectangle(width=1.2, height=0.7, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                           stroke_width=3).move_to([-5.3, 0.1, 0])
        l2 = T("400 contained", 34).move_to([1.1, -2.8, 0])
        self.play(FadeIn(posts), FadeIn(arm), FadeIn(ticket), FadeIn(l2), run_time=0.7)
        at(self, 0.62)
        self.play(ticket.animate.move_to([-0.8, 0.1, 0]), run_time=0.9)
        ok = check(-0.85, 0.9, s=0.2)
        self.play(Create(ok), run_time=0.4)
        finish(self)


class B09_Columns(Scene):
    def construct(self):
        h1 = T("already have", 42).move_to([-3.0, 2.6, 0])
        h2 = T("new to me", 42).move_to([3.0, 2.6, 0])
        base = VGroup(Line([-5.2, -2.6, 0], [-0.8, -2.6, 0], color=INK, stroke_width=4),
                      Line([0.8, -2.6, 0], [5.2, -2.6, 0], color=INK, stroke_width=4))
        self.play(FadeIn(h1), FadeIn(h2), Create(base), run_time=0.7)
        at(self, 0.2)
        left = VGroup(*[record(-3.0 + (i - 0.5) * 1.9, 0.0, 1.5, 1.8, n=2) for i in range(2)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in left], lag_ratio=0.3), run_time=0.8)
        at(self, 0.62)
        right = VGroup(*[record(3.0 + (i - 1) * 1.6, 0.0, 1.3, 1.8, n=2) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in right], lag_ratio=0.3), run_time=0.9)
        finish(self)


class B10_Split(Scene):
    def construct(self):
        divider = Line([0, -2.8, 0], [0, 2.8, 0], color=GHOST, stroke_width=4)
        iso = Iso(-5.4, -1.0, 0.55)
        solid = VGroup(*[crate(iso, i * 2.2, 0, 1.6, 1.6, 1.2) for i in range(4)])
        l1 = T("exists", 36).move_to([-3.0, -2.6, 0])
        self.play(Create(divider), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in solid], lag_ratio=0.2),
                  FadeIn(l1), run_time=1.0)
        l2 = T("will exist", 36).move_to([3.0, -2.6, 0])
        self.play(FadeIn(l2), run_time=0.3)
        at(self, 0.62)
        iso2 = Iso(1.4, -1.0, 0.55)
        ghosts = VGroup(*[iso2.box(i * 2.2, 0, 0, 1.6, 1.6, 1.2, STAGE, STAGE, STAGE, sw=4).set_stroke(DIM)
                          for i in range(3)])
        self.play(LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.25), run_time=0.9)
        finish(self)
