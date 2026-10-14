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


# ═════════════════════════════ final-project-pitch-nishant-u ═════════════════════════════
# The film's own scenes, pasted after the kit. One isometric drawing per body beat; visuals,
# labels and "constructed" flags follow beat_sheet.json exactly. Labels are on stage from the
# first frame; every move is held off the clip midpoint, where GATE T and Gate V sample.

# EB Garamond is not installed system-wide here: register the toolkit's copy for this process.
try:
    import manimpango as _mp
    _ART = _os.environ.get("ART_HOME") or _os.path.join(_os.path.expanduser("~"), "brutalist.art")
    _EBG = _os.path.join(_ART, "runtime", "fonts", "EB_Garamond", "static", "EBGaramond-Regular.ttf")
    if _os.path.exists(_EBG):
        _mp.register_font(_EBG)
except Exception:
    pass

KRAFT_DEEP = "#9C8462"   # connectors and belts: never ink, or they fuse with what they join (GATE T)


def _bid(scene):
    return type(scene).__name__.split("_")[0]


def go(scene, *anims, rt=0.8):
    """play(), held clear of the clip midpoint (GATE T / Gate V sample there)."""
    mid = _TARGET.get(_bid(scene), 10) / 2
    now = _elapsed(scene)
    if now < mid + 0.3 and now + rt > mid - 0.3:
        scene.wait(max(0.01, mid + 0.35 - now))
    scene.play(*anims, run_time=rt)


def done(scene):
    gap = _TARGET.get(_bid(scene), 10) - _elapsed(scene) - 0.10
    if gap > 0:
        scene.wait(gap)


def L(s, x, y, size=52):
    return T(s, size).move_to([x, y, 0])


def stamp():
    """The on-screen 'constructed' label: none of the agent's output exists yet."""
    return T("constructed", 44).move_to([4.6, 3.0, 0])


def sheet(x, y, w, h, fill=PAGE_TOP):
    return paper(x, y, w, h, 0.0, fill)


def lines_on(x, y, w, n, gap=0.36, color=GHOST, sw=5):
    return VGroup(*[Line([x, y - i * gap, 0], [x + w, y - i * gap, 0], color=color, stroke_width=sw) for i in range(n)])


def ring(x, y, r=0.3, color=INK):
    return Circle(radius=r, color=color, stroke_width=6).move_to([x, y, 0])


def kpage(iso, x0=0.0, y0=0.0, z0=0.0, w=1.1, d=1.4):
    """A resume page: kraft slab with dim lines (the skill page, but kraft, so it reads as a different paper)."""
    slab = iso.box(x0, y0, z0, w, d, 0.06, BOX_TOP, BOX_L, BOX_R, sw=2)
    zt = z0 + 0.06
    ln = VGroup(*[Line(iso.p(x0 + 0.2, y0 + d * f, zt), iso.p(x0 + w - 0.2, y0 + d * f, zt), color=DIM, stroke_width=4)
                  for f in (0.35, 0.6)])
    return VGroup(slab, ln)


class B00_Agent(Scene):
    def construct(self):
        b1, l1 = Iso(-5.2, -0.3, 0.6).server(0, 0, 0)
        b2, l2 = Iso(-3.5, -1.9, 0.6).server(0, 0, 0)
        agent = Iso(0.2, -1.5, 0.95).mcp(0, 0, 0, 1.5, 1.5, 0.85)
        self.add(b1, l1, b2, l2, agent, L("job boards", -4.4, 1.9), L("agent", 0.2, -2.35), stamp())
        self.wait(0.2)
        belt = Line([-2.7, -1.15, 0], [-1.2, -0.75, 0], color=KRAFT_DEEP, stroke_width=8)
        go(self, Create(belt), rt=0.6)
        until(self, "watch public job boards")
        go(self, *[d.animate.set_color(TERRA) for d in list(l1) + list(l2)], rt=0.5)
        until(self, "retail")
        pg = Iso(-3.3, -1.0, 0.42).page(0, 0, 0)
        go(self, FadeIn(pg), rt=0.3)
        go(self, pg.animate.move_to([-1.3, -0.55, 0]), rt=1.0)
        self.remove(pg)
        until(self, "fictional")
        resume = kpage(Iso(2.3, 0.7, 0.6))
        go(self, FadeIn(resume, shift=DOWN * 0.4), rt=0.6)
        tray_back, tray_front = Iso(4.3, -2.2, 0.75).open_box(0, 0, 0, 1.5, 1.5, 0.4)
        until(self, "which new postings")
        go(self, FadeIn(tray_back), FadeIn(tray_front), rt=0.5)
        out = Iso(1.4, -0.9, 0.42).page(0, 0, 0)
        out.set_z_index(1)
        go(self, FadeIn(out), rt=0.3)
        go(self, out.animate.move_to([4.3, -1.55, 0]), rt=1.0)
        until(self, "worth their time")
        go(self, Create(check(4.4, -0.2, 0.28)), rt=0.5)
        done(self)


class B01_Repo(Scene):
    def construct(self):
        iso = Iso(0.0, -2.9, 1.0)
        back, front = iso.open_box(0, 0, 0, 2.4, 2.4, 1.0)
        agent = iso.mcp(0.55, 0.55, 0, 1.2, 1.2, 0.6)
        agent.set_z_index(1)
        self.add(back, agent, front, L("GitHub repo", -4.3, -2.4), L("evidence packet", 3.85, -2.55))
        self.wait(0.2)
        until(self, "cite")
        spark = Dot(iso.p(1.15, 1.15, 0.6), radius=0.09, color=TERRA).set_z_index(3)
        go(self, FadeIn(spark), rt=0.3)
        start = [0.0, 0.2, 0]
        code = VGroup(sheet(-4.6, 1.7, 1.5, 1.8), lines_on(-5.05, 2.2, 0.9, 3, color=BAR1))
        tests = VGroup(sheet(-2.2, 2.0, 1.5, 1.8), *[check(-2.3, 2.45 - i * 0.5, 0.17) for i in range(3)])
        log = VGroup(sheet(2.2, 2.0, 1.5, 1.8), lines_on(1.75, 2.5, 0.9, 4, gap=0.3, color=BAR1))
        stack = VGroup(Iso(4.4, -1.5, 0.75).box(0, 0, 0, 1.2, 1.5, 0.75, PAGE_TOP, PAGE_L, PAGE_R, sw=3),
                       *[Line(Iso(4.4, -1.5, 0.75).p(0, 0.15, 0.075 * k), Iso(4.4, -1.5, 0.75).p(0, 1.35, 0.075 * k),
                              color=BAR2, stroke_width=2) for k in range(1, 10)])
        film = VGroup(Rectangle(width=1.6, height=1.1, fill_color=DIM, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([4.6, 2.1, 0]),
                      Triangle(fill_color=TERRA, fill_opacity=1, stroke_width=0).scale(0.22).rotate(-PI / 2).move_to([4.65, 2.1, 0]))
        for part, phrase in ((code, "Python agent"), (tests, "tests"), (log, "evaluation log"),
                             (stack, "evidence packet"), (film, "five-minute")):
            until(self, phrase)
            target = np.array(part.get_center(), dtype=float)
            part.move_to(start)
            go(self, FadeIn(part), rt=0.2)
            go(self, part.animate.move_to(target), rt=0.45)
        done(self)


class B02_Alerts(Scene):
    def construct(self):
        env = VGroup(Rectangle(width=2.8, height=1.8, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-4.2, 0.4, 0]),
                     Line([-5.6, 1.3, 0], [-4.2, 0.25, 0], color=INK, stroke_width=4),
                     Line([-4.2, 0.25, 0], [-2.8, 1.3, 0], color=INK, stroke_width=4))
        self.add(env, L("LinkedIn Job Alerts", -3.3, 2.1), L("why?", 4.4, 2.35))
        self.wait(0.2)
        until(self, "emailed me postings")
        posts = []
        for i, x in enumerate((-0.9, 1.6, 4.1)):
            p = VGroup(sheet(x, -0.6, 1.6, 2.0), lines_on(x - 0.5, -0.1, 1.0, 3, color=BAR1))
            target = np.array(p.get_center(), dtype=float)
            p.move_to([-4.2, 0.4, 0])
            go(self, FadeIn(p), rt=0.2)
            go(self, p.animate.move_to(target), rt=0.55)
            posts.append(x)
        until(self, "never told me why")
        tags = [RoundedRectangle(width=0.9, height=0.45, corner_radius=0.12, fill_color=CARD, fill_opacity=1,
                                 stroke_color=INK, stroke_width=4).move_to([x + 0.35, 1.05, 0]) for x in posts]
        for t in tags:
            go(self, GrowFromCenter(t), rt=0.35)
        done(self)


class B03_Jobright(Scene):
    def construct(self):
        c = np.array([-3.6, 0.5, 0.0])
        dial = Circle(radius=1.25, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to(c)
        ticks = VGroup(*[Line(c + 1.0 * np.array([np.cos(a), np.sin(a), 0]), c + 1.2 * np.array([np.cos(a), np.sin(a), 0]),
                              color=DIM, stroke_width=5) for a in np.linspace(PI * 0.15, PI * 0.85, 5)])
        needle = Line(c, c + np.array([-0.85, 0.35, 0]), color=INK, stroke_width=8)
        hub = Dot(c, radius=0.1, color=INK)
        funnel = Polygon([0.2, 1.6, 0], [3.0, 1.6, 0], [1.95, -0.3, 0], [1.25, -0.3, 0],
                         fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4)
        spout = Rectangle(width=0.7, height=0.6, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([1.6, -0.6, 0])
        self.add(dial, ticks, needle, hub, funnel, spout, L("Jobright", -3.6, -1.35),
                 L("careery.pro review, 2026", 1.8, -2.9, 44))
        self.wait(0.2)
        until(self, "a match score")
        go(self, Rotate(needle, angle=-1.6, about_point=c), rt=0.9)
        mark = Dot(c + 1.2 * np.array([np.cos(PI * 0.32), np.sin(PI * 0.32), 0]), radius=0.1, color=TERRA)
        go(self, FadeIn(mark), rt=0.3)
        until(self, "filter")
        for k in range(2):
            card = VGroup(sheet(1.6, 2.6, 0.9, 0.7), lines_on(1.35, 2.75, 0.5, 2, gap=0.25, color=BAR1))
            go(self, FadeIn(card), rt=0.2)
            go(self, card.animate.move_to([1.6, -1.6, 0]), rt=0.7)
            self.remove(card)
        out = VGroup(sheet(1.6, -1.7, 0.9, 0.7), lines_on(1.35, -1.55, 0.5, 2, gap=0.25, color=BAR1))
        go(self, FadeIn(out), rt=0.3)
        until(self, "past sponsorship history")
        ledger = VGroup(sheet(4.9, 1.0, 1.7, 2.2), lines_on(4.3, 1.75, 1.2, 5, gap=0.32, color=BAR1))
        go(self, FadeIn(ledger, shift=LEFT * 0.4), rt=0.5)
        feed = Line([4.05, 0.6, 0], [2.75, 0.9, 0], color=KRAFT_DEEP, stroke_width=8)
        go(self, Create(feed), rt=0.5)
        done(self)


class B04_ThreeWays(Scene):
    def construct(self):
        post = sheet(-3.0, 0.0, 3.4, 4.6)
        rows = VGroup(lines_on(-4.3, 1.75, 2.6, 1, color=BAR1), lines_on(-4.3, 1.05, 2.6, 1, color=BAR1),
                      lines_on(-4.3, -1.65, 2.6, 1, color=BAR1))
        self.add(post, rows, L("supported", 1.95, 1.0), L("insufficient", 2.15, -0.45), stamp())
        self.wait(0.2)
        until(self, "by its own text")
        bracket = VGroup(Line([-4.55, 0.8, 0], [-4.55, 1.3, 0], color=INK, stroke_width=6),
                         Line([-4.55, 0.8, 0], [-4.4, 0.8, 0], color=INK, stroke_width=6),
                         Line([-4.55, 1.3, 0], [-4.4, 1.3, 0], color=INK, stroke_width=6))
        go(self, Create(bracket), rt=0.5)
        go(self, Create(check(-0.55, 1.0, 0.24)), rt=0.5)
        until(self, "silent")
        go(self, Create(ring(-0.45, -0.45)), rt=0.5)
        until(self, "never apply")
        gate = VGroup(Line([4.4, -3.0, 0], [4.4, -1.3, 0], color=INK, stroke_width=8),
                      Line([5.4, -3.0, 0], [5.4, -1.3, 0], color=INK, stroke_width=8),
                      Line([4.4, -1.6, 0], [5.4, -1.6, 0], color=INK, stroke_width=8))
        go(self, Create(gate), rt=0.5)
        go(self, GrowArrow(Arrow([0.3, -2.4, 0], [4.15, -2.4, 0], buff=0, color=INK, stroke_width=8)), rt=0.8)
        done(self)


class B05_SixtySeconds(Scene):
    def construct(self):
        screen = Rectangle(width=3.2, height=2.0, fill_color=DIM, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-4.1, 1.0, 0])
        base = Polygon([-5.8, -0.15, 0], [-2.4, -0.15, 0], [-2.0, -0.65, 0], [-6.1, -0.65, 0],
                       fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4)
        self.add(screen, base, L("shortlist", -0.9, -2.75), L("skipped", 1.9, -2.75), stamp())
        self.wait(0.2)
        until(self, "run one command")
        prompt = VGroup(Line([-5.35, 1.45, 0], [-5.15, 1.3, 0], color=CARD, stroke_width=6),
                        Line([-5.15, 1.3, 0], [-5.35, 1.15, 0], color=CARD, stroke_width=6))
        go(self, Create(prompt), rt=0.3)
        go(self, Create(Line([-4.9, 1.3, 0], [-3.0, 1.3, 0], color=CARD, stroke_width=8)), rt=1.0)
        until(self, "shortlist with citations")
        trays = []
        for x in (-0.9, 1.9, 4.7):
            bk, fr = Iso(x, -2.15, 0.6).open_box(0, 0, 0, 1.6, 1.6, 0.45)
            t = VGroup(bk, fr)
            target = np.array(t.get_center(), dtype=float)
            t.move_to([-3.0, -1.2, 0])
            go(self, FadeIn(t), rt=0.2)
            go(self, t.animate.move_to(target), rt=0.6)
            trays.append(x)
        go(self, Create(check(-0.85, -0.25, 0.26)), rt=0.4)
        go(self, GrowFromCenter(RoundedRectangle(width=0.8, height=0.4, corner_radius=0.1, fill_color=CARD, fill_opacity=1,
                                                 stroke_color=INK, stroke_width=4).move_to([1.9, -0.25, 0])), rt=0.4)
        bars = VGroup(*[Rectangle(width=0.32, height=h, fill_color=col, fill_opacity=1, stroke_width=0).move_to([4.35 + i * 0.42, -0.6 + h / 2, 0])
                        for i, (h, col) in enumerate(((0.9, BAR1), (0.6, BAR2), (1.2, BAR1)))])
        go(self, GrowFromEdge(bars, DOWN), rt=0.5)
        done(self)


class B06_Proves(Scene):
    def construct(self):
        c = np.array([-2.0, -0.5, 0.0])
        track = Ellipse(width=6.0, height=2.8, color=KRAFT_DEEP, stroke_width=10).move_to(c)
        meter = Rectangle(width=0.8, height=2.8, stroke_color=INK, stroke_width=5, fill_opacity=0).move_to([5.0, 0.0, 0])
        segs = [Rectangle(width=0.6, height=0.55, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([5.0, -1.05 + i * 0.7, 0])
                for i in range(4)]
        hinge = np.array([1.6, 0.25, 0.0])
        bar = Line(hinge, hinge + np.array([0, -1.5, 0]), color=INK, stroke_width=9)
        post = Dot(hinge, radius=0.1, color=INK)
        self.add(track, meter, *segs, bar, post, L("loop", -2.0, 1.45), L("budget", 5.0, -2.0), L("gate", 1.6, -2.45))
        self.wait(0.2)
        block = Iso(0.0, 0.0, 0.42).mcp(0, 0, 0, 1.2, 1.2, 0.7)
        block.move_to(c + np.array([3.0, 0, 0]))   # the track's right end, where MoveAlongPath starts
        until(self, "agent loop")
        go(self, FadeIn(block), rt=0.3)
        path = Ellipse(width=6.0, height=2.8).move_to(c)
        for k in range(2):
            go(self, MoveAlongPath(block, path), rt=1.6)
            self.remove(segs[-1 - k])
        until(self, "exits")
        go(self, Rotate(bar, angle=PI / 2, about_point=hinge), rt=0.5)
        go(self, block.animate.move_to([2.8, -0.5, 0]), rt=0.7)
        until(self, "Permissions in code")
        port = Iso(-5.6, 1.8, 0.55).box(0, 0, 0, 0.9, 0.9, 0.6, GHOST, BOX_IN1, BOX_IN2, sw=4)
        lock = VGroup(Rectangle(width=0.7, height=0.55, fill_color=DARK_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-4.2, 2.2, 0]),
                      Arc(radius=0.24, start_angle=0, angle=PI, color=INK, stroke_width=7).move_to([-4.2, 2.6, 0]))
        go(self, FadeIn(port), rt=0.3)
        go(self, FadeIn(lock, shift=DOWN * 0.3), rt=0.4)
        until(self, "human gate")
        go(self, Create(check(2.9, 0.75, 0.26)), rt=0.4)
        done(self)


class B07_Evidence(Scene):
    def construct(self):
        tests = sheet(-3.6, -0.1, 2.6, 3.6)
        ev = sheet(1.3, -0.1, 3.6, 3.9)
        rows = VGroup(*[VGroup(Square(side_length=0.3, stroke_color=DIM, stroke_width=4, fill_opacity=0).move_to([-0.05, 1.3 - i * 0.62, 0]),
                               Line([0.35, 1.3 - i * 0.62, 0], [2.3, 1.3 - i * 0.62, 0], color=GHOST, stroke_width=5)) for i in range(5)])
        self.add(tests, ev, rows, L("tests", -3.6, -2.45), L("held-out eval", 1.3, -2.6), stamp())
        self.wait(0.2)
        until(self, "tests")
        for i in range(4):
            go(self, Create(check(-3.6, 1.15 - i * 0.7, 0.2)), rt=0.3)
        until(self, "five deliberate failure")
        for i in range(5):
            go(self, FadeIn(Square(side_length=0.2, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-0.05, 1.3 - i * 0.62, 0])), rt=0.15)
        until(self, "predict and then trigger")
        y = 1.3 - 2 * 0.62
        go(self, Create(VGroup(Line([2.55, y - 0.2, 0], [2.95, y + 0.2, 0], color=INK, stroke_width=7),
                               Line([2.55, y + 0.2, 0], [2.95, y - 0.2, 0], color=INK, stroke_width=7))), rt=0.5)
        until(self, "stranger")
        go(self, FadeIn(cursor(4.0, 0.9, 0.5)), rt=0.3)
        done(self)


class B08_OutFirst(Scene):
    def construct(self):
        x0 = -4.6
        send = Arrow([x0 - 0.8, 1.7, 0], [x0 + 0.8, 1.7, 0], buff=0, color=INK, stroke_width=8)
        env = VGroup(Rectangle(width=1.6, height=1.0, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x0, 0.25, 0]),
                     Line([x0 - 0.8, 0.75, 0], [x0, 0.15, 0], color=INK, stroke_width=4), Line([x0, 0.15, 0], [x0 + 0.8, 0.75, 0], color=INK, stroke_width=4))
        key = VGroup(Circle(radius=0.32, stroke_color=INK, stroke_width=7).move_to([x0 - 0.5, -1.25, 0]),
                     Line([x0 - 0.18, -1.25, 0], [x0 + 0.8, -1.25, 0], color=INK, stroke_width=7),
                     Line([x0 + 0.55, -1.25, 0], [x0 + 0.55, -1.55, 0], color=INK, stroke_width=7))
        board, lights = Iso(0.9, -1.9, 0.62).server(0, 0, 0)
        self.add(send, env, key, board, lights, L("out", x0, 2.7), L("one board", 0.9, -2.75), L("state file", 4.8, -2.75))
        self.wait(0.2)
        for item, phrase in ((1.7, "never apply"), (0.25, "email"), (-1.25, "log in")):
            until(self, phrase)
            go(self, Create(Line([x0 - 1.0, item - 0.5, 0], [x0 + 1.0, item + 0.5, 0], color=INK, stroke_width=8)), rt=0.35)
        until(self, "one public board")
        go(self, *[d.animate.set_color(TERRA) for d in lights], rt=0.4)
        until(self, "fictional resume")
        go(self, FadeIn(kpage(Iso(3.0, -1.0, 0.6)), shift=DOWN * 0.3), rt=0.5)
        until(self, "raw board response")
        go(self, FadeIn(VGroup(sheet(0.9, 1.25, 1.1, 0.8), lines_on(0.55, 1.4, 0.7, 2, gap=0.28, color=BAR1)), shift=DOWN * 0.3), rt=0.4)
        until(self, "state file")
        sf = VGroup(sheet(4.8, -0.9, 1.5, 1.9), lines_on(4.35, -0.4, 0.9, 3, gap=0.4, color=BAR1),
                    Rectangle(width=0.6, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([4.35, 0.2, 0]))
        go(self, FadeIn(sf, shift=DOWN * 0.5), rt=0.5)
        done(self)


class B09_Risk(Scene):
    def construct(self):
        post = VGroup(sheet(-3.0, -0.1, 3.0, 4.0), lines_on(-4.1, 1.4, 2.2, 1, color=BAR1))
        c = np.array([3.9, -0.5, 0.0])
        # deep kraft, not ink: an ink arc swallows its ink needle as one text blob (GATE T §8.6b)
        gauge = Arc(radius=1.3, start_angle=0, angle=PI, arc_center=c, color=KRAFT_DEEP, stroke_width=9)
        needle = Line(c, c + np.array([-1.0, 0.15, 0]), color=INK, stroke_width=8)
        hub = Dot(c, radius=0.1, color=INK)
        self.add(post, gauge, needle, hub, L("insufficient", 0.9, 1.25), L("abstain", 3.9, -1.35), stamp())
        self.wait(0.2)
        until(self, "look confident")
        big = check(-3.2, 0.1, 0.75, w=12)
        go(self, Create(big), rt=0.6)
        until(self, "an insufficient label")
        self.remove(big)
        go(self, Create(ring(-3.0, 0.0, 0.6)), rt=0.5)
        until(self, "how often it abstains")
        go(self, Rotate(needle, angle=-0.9, about_point=c), rt=0.8)
        go(self, FadeIn(Dot(c + np.array([0.0, 1.3, 0]), radius=0.1, color=TERRA)), rt=0.3)
        done(self)


class B10_Skills(Scene):
    def construct(self):
        li, ri = Iso(-4.8, -1.4, 0.7), Iso(1.6, -1.4, 0.7)
        lshelf = li.box(0, 0, 0, 3.6, 1.1, 0.25, DARK_TOP, DARK_L, DARK_R)
        rshelf = ri.box(0, 0, 0, 3.6, 1.1, 0.25, DARK_TOP, DARK_L, DARK_R)
        ghosts = [ri.box(0.2 + i * 0.85, 0.2, 0.25, 0.65, 0.65, 0.65, STAGE, STAGE, STAGE, sw=4).set_stroke(DIM) for i in range(4)]
        self.add(lshelf, rshelf, *ghosts, L("I bring", -3.5, 2.3), L("new to me", 2.9, 2.3))
        self.wait(0.2)
        for i, phrase in enumerate(("Python", "SQL", "data analysis")):
            until(self, phrase)
            blk = li.box(0.25 + i * 1.15, 0.2, 0.25, 0.8, 0.7, 0.8)
            go(self, FadeIn(blk, shift=DOWN * 0.4), rt=0.4)
        for i, phrase in enumerate(("agent loops", "permissions", "MCP server", "evaluation")):
            until(self, phrase)
            go(self, FadeIn(ri.box(0.2 + i * 0.85, 0.2, 0.25, 0.65, 0.65, 0.65)), rt=0.35)
        done(self)


class B11_ExistsWill(Scene):
    def construct(self):
        boxes = [Iso(x, -1.4, 0.55).box(0, 0, 0, 1.2, 1.2, 1.0) for x in (-5.0, -3.4, -1.8)]
        self.add(*boxes, L("exists today", -3.4, 1.7), L("will exist", 3.3, 2.0))
        self.wait(0.2)
        for x, phrase in zip((-5.0, -3.4, -1.8), ("Brutalist setup", "Week 1 film", "Reallocation Engine")):
            until(self, phrase)
            go(self, Create(check(x, 0.75, 0.24)), rt=0.35)
        until(self, "Nothing of the agent")
        gi = Iso(3.3, -2.2, 0.85)
        outline = VGroup(*[DashedLine(gi.p(*a), gi.p(*b), color=DIM, stroke_width=5, dash_length=0.18)
                           for a, b in (((0, 0, 0), (2.2, 0, 0)), ((0, 0, 0), (0, 2.2, 0)), ((0, 0, 0), (0, 0, 1.0)),
                                        ((2.2, 0, 0), (2.2, 0, 1.0)), ((0, 2.2, 0), (0, 2.2, 1.0)),
                                        ((0, 0, 1.0), (2.2, 0, 1.0)), ((0, 0, 1.0), (0, 2.2, 1.0)),
                                        ((2.2, 0, 1.0), (2.2, 2.2, 1.0)), ((0, 2.2, 1.0), (2.2, 2.2, 1.0)))])
        go(self, Create(outline), rt=0.8)
        done(self)


class BEND_Close(Scene):
    def construct(self):
        gi = Iso(-2.6, -1.9, 0.9)
        edges = (((0, 0, 0), (2.2, 0, 0)), ((0, 0, 0), (0, 2.2, 0)), ((0, 0, 0), (0, 0, 1.0)),
                 ((2.2, 0, 0), (2.2, 0, 1.0)), ((0, 2.2, 0), (0, 2.2, 1.0)),
                 ((0, 0, 1.0), (2.2, 0, 1.0)), ((0, 0, 1.0), (0, 2.2, 1.0)),
                 ((2.2, 0, 1.0), (2.2, 2.2, 1.0)), ((0, 2.2, 1.0), (2.2, 2.2, 1.0)))
        ghost = VGroup(*[DashedLine(gi.p(*a), gi.p(*b), color=DIM, stroke_width=5, dash_length=0.18) for a, b in edges])
        plinth = Iso(-2.6, -2.25, 0.9).box(-0.2, -0.2, 0, 2.6, 2.6, 0.3, DARK_TOP, DARK_L, DARK_R)
        self.add(plinth)
        self.wait(0.2)
        ghost.shift(UP * 0.8)
        go(self, FadeIn(ghost), rt=0.4)
        go(self, ghost.animate.shift(DOWN * 0.8), rt=0.8)
        name, title = L("Nishant U", 3.0, 0.6, 64), L("Job-search agent", 3.0, -0.4, 52)
        go(self, FadeIn(name), FadeIn(title), rt=0.6)
        until(self, "the agent I will build")
        go(self, FadeIn(Dot(gi.p(1.1, 1.1, 1.0), radius=0.1, color=TERRA)), rt=0.3)
        done(self)
