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


# ═════════════════════════════ cite-the-line-project-film — scenes ═════════════════════════════
# Build:  cat <toolkit>/skills/make/show-tell/templates/iso_kit.py scenes_body.py > scenes.py
# (show-tell: paste the kit at the top of scenes.py; never import it.)
#
# Timing rule used in every scene (GATE T and Gate V sample each clip at its MIDPOINT):
#   phase A — every arrival, label and move finishes by 36% of the beat;
#   hold    — nothing moves between 36% and 62%;
#   phase B — from 62%, one more NEW shape lands (Gate A needs a new shape after frame 1).
# Every body beat carries the on-screen "constructed sketch" tag: nothing shown is built yet.

A_END, B_START = 0.36, 0.62


def dur(self):
    """Measured audio for this beat; 6 s when the sheet isn't beside scenes.py (Gate A's sandbox)."""
    return _TARGET.get(type(self).__name__.split("_")[0], 0) or 6.0


def at(self, frac):
    gap = frac * dur(self) - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def tag():
    return T("constructed sketch", 32).move_to([4.6, -2.95, 0])


def lab(s, x, y, size=36):
    return T(s, size).move_to([x, y, 0])


def logpage(x, y, w=2.4, h=3.0, rows=6, lengths=(0.85, 0.6, 0.95, 0.7, 0.9, 0.5)):
    """A page of log lines: white sheet, kraft shadow, grey line bars. `.rowy` = each bar's y."""
    pg = paper(x, y, w, h)
    bars, rowy = VGroup(), []
    for i in range(rows):
        yy = y + h / 2 - 0.45 - i * (h - 0.8) / max(1, rows - 1)
        x0 = x - w / 2 + 0.45
        bars.add(Line([x0, yy, 0], [x0 + (w - 0.8) * lengths[i % len(lengths)], yy, 0], color=GHOST, stroke_width=9))
        rowy.append(yy)
    g = VGroup(pg, bars)
    g.rowy, g.x0 = rowy, x - w / 2
    return g


def slip(x, y, w=1.7, h=1.0, dots=2):
    """The result slip: card, one grey cause pill, terracotta line-number dots."""
    card = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    bar = RoundedRectangle(width=w * 0.55, height=0.22, corner_radius=0.11, fill_color=BAR2, fill_opacity=1,
                           stroke_width=0).move_to([x - w * 0.12, y + h * 0.17, 0])
    ds = VGroup(*[Dot([x - w * 0.32 + i * 0.32, y - h * 0.22, 0], radius=0.07, color=TERRA) for i in range(dots)])
    return VGroup(card, bar, ds)


def cross(x, y, s=0.32, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def lens(x, y, r=0.55):
    ring = Circle(radius=r, stroke_color=INK, stroke_width=8, fill_opacity=0).move_to([x, y, 0])
    handle = Line([x + r * 0.7, y - r * 0.7, 0], [x + r * 1.5, y - r * 1.5, 0], color=INK, stroke_width=10)
    return VGroup(ring, handle)


def cylinder(x, y, w=1.6, h=1.4, top=BOX_TOP, body=BOX_R):
    e = 0.36
    bottom = Ellipse(width=w, height=e, fill_color=body, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y - h / 2, 0])
    side = Rectangle(width=w, height=h, fill_color=body, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    edges = VGroup(Line([x - w / 2, y - h / 2, 0], [x - w / 2, y + h / 2, 0], color=INK, stroke_width=4),
                   Line([x + w / 2, y - h / 2, 0], [x + w / 2, y + h / 2, 0], color=INK, stroke_width=4))
    lid = Ellipse(width=w, height=e, fill_color=top, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + h / 2, 0])
    return VGroup(bottom, side, edges, lid)


def floor_shadow(x, y, w=2.6):
    return Ellipse(width=w, height=0.32, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


def dashed_rect(x, y, w, h, n=6, color=DIM, sw=5):
    """A dashed outline from short lines (no DashedVMobject, to stay inside Gate A's stub)."""
    g = VGroup()
    corners = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
    for k in range(4):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % 4]
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            g.add(Line([ax + (bx - ax) * t0, ay + (by - ay) * t0, 0], [ax + (bx - ax) * t1, ay + (by - ay) * t1, 0],
                       color=color, stroke_width=sw))
    return g



KRAFT = "#9C8462"   # connectors: deep kraft, never ink (ink connectors fuse objects into one "text" blob)


def connector(a, b, sw=6):
    return Line([a[0], a[1], 0], [b[0], b[1], 0], color=KRAFT, stroke_width=sw)


def padlock(x, y, s=0.5):
    body = RoundedRectangle(width=s * 1.5, height=s * 1.15, corner_radius=0.08, fill_color=DARK_TOP, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    shackle = Arc(radius=s * 0.48, start_angle=0, angle=PI, color=INK, stroke_width=9).move_arc_center_to([x, y + s * 0.57, 0])
    return VGroup(shackle, body)


def scorecard(x, y, w=1.9, h=1.5):
    card = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    head = Rectangle(width=w, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x, y + h / 2 - 0.15, 0])
    rows = VGroup(*[RoundedRectangle(width=w * (0.7 - 0.15 * i), height=0.18, corner_radius=0.09, fill_color=BAR2,
                                     fill_opacity=1, stroke_width=0).move_to([x - w * 0.12 + 0.0, y + 0.15 - i * 0.38, 0])
                    for i in range(3)])
    return VGroup(card, head, rows)


def octagon(x, y, r=1.0):
    pts = [[x + r * np.cos(PI / 8 + k * PI / 4), y + r * np.sin(PI / 8 + k * PI / 4), 0] for k in range(8)]
    return Polygon(*pts, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=7)


def restart_button(x, y, r=0.9):
    btn = Circle(radius=r, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([x, y, 0])
    arc = Arc(radius=r * 0.55, start_angle=PI * 0.6, angle=PI * 1.6, color=INK, stroke_width=9).move_arc_center_to([x, y, 0])
    t = np.array([x + r * 0.55 * np.cos(PI * 0.6), y + r * 0.55 * np.sin(PI * 0.6), 0])
    tip = Polygon(t + [0.0, 0.2, 0], t + [0.0, -0.2, 0], t + [-0.28, 0.0, 0], fill_color=INK, fill_opacity=1, stroke_width=0)
    return VGroup(btn, arc, tip)


def tray(cx, cy, w=1.8, d=1.8, h=0.7):
    iso = Iso(cx, cy, 1.0)
    back, front = iso.open_box(0, 0, 0, w, d, h)
    return iso, back, front


# ═══ 1. EXECUTIVE SUMMARY ═══════════════════════════════════════════════════

class B00_PasteHabit(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pg = logpage(-4.2, 0.4, w=1.9, h=2.4, rows=4)
        self.play(FadeIn(pg, shift=DOWN * 0.4), run_time=0.08 * d)
        bubble = RoundedRectangle(width=2.4, height=1.5, corner_radius=0.3, fill_color=CARD, fill_opacity=1,
                                  stroke_color=INK, stroke_width=5).move_to([0, 0.7, 0])
        rows = VGroup(*[RoundedRectangle(width=w, height=0.18, corner_radius=0.09, fill_color=BAR2, fill_opacity=1,
                                         stroke_width=0).move_to([-0.15, 1.0 - i * 0.4, 0]) for i, w in enumerate((1.6, 1.2, 1.4))])
        self.play(Create(connector((-3.1, 0.5), (-1.35, 0.6))), FadeIn(bubble), FadeIn(rows),
                  FadeIn(lab("chatbot", 0, -0.55)), run_time=0.12 * d)
        fix = slip(4.2, 0.5)
        self.play(Create(connector((1.35, 0.6), (3.25, 0.5))), FadeIn(fix, shift=RIGHT * 0.3), run_time=0.1 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(4.25, -0.2, w=2.0)), run_time=0.12 * d)
        finish(self)


class B01_LensCites(Scene):
    def construct(self):
        d = dur(self)
        pg = logpage(-2.6, 0.3)
        self.add(tag(), pg)
        ln = lens(-4.9, 1.9)
        self.play(FadeIn(ln), run_time=0.06 * d)
        self.play(ln.animate.move_to([-2.2, pg.rowy[2] - 0.15, 0]), run_time=0.1 * d)
        hits = VGroup(*[Dot([pg.x0 + 0.22, pg.rowy[i], 0], radius=0.08, color=TERRA) for i in (2, 4)])
        self.play(LaggedStart(*[GrowFromCenter(h) for h in hits], lag_ratio=0.4), run_time=0.07 * d)
        s = slip(2.7, 0.5)
        self.play(FadeIn(s, shift=LEFT * 0.4), FadeIn(lab("cause", 2.7, -0.55)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(check(4.1, 0.55)), run_time=0.12 * d)
        finish(self)


class B02_HandOff(Scene):
    def construct(self):
        d = dur(self)
        pg = logpage(-3.6, 0.3, rows=3, lengths=(0.4, 0.3, 0.35))
        self.add(tag(), pg)
        ln = lens(-3.3, 1.3)
        self.play(FadeIn(ln), run_time=0.05 * d)
        self.play(ln.animate.move_to([-3.3, -0.3, 0]), run_time=0.1 * d)
        empty = Rectangle(width=1.6, height=1.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([0.4, 0.6, 0])
        self.play(FadeIn(empty, shift=LEFT * 0.3), FadeIn(lab("not enough", 0.4, -0.45)), run_time=0.08 * d)
        iso, back, front = tray(3.9, -1.2)
        self.play(Create(connector((1.25, 0.6), (2.75, 0.5))), FadeIn(back), FadeIn(front),
                  FadeIn(lab("engineer", 3.9, -1.9)), run_time=0.1 * d)
        at(self, B_START)
        note = iso.page(0.45, 0.45, 0.05, w=0.9, d=1.0)
        note.set_z_index(1)
        self.play(FadeIn(note, shift=DOWN * 0.2), run_time=0.12 * d)
        finish(self)


class B03_CheckedVsNot(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        lone = slip(-3.8, 0.9)
        self.play(FadeIn(lone), FadeIn(lab("unchecked", -3.8, -1.3)), run_time=0.08 * d)
        self.play(Create(cross(-3.8, -0.35, s=0.3)), run_time=0.06 * d)
        pg = logpage(1.6, 0.3, w=2.0, h=2.6, rows=4)
        hits = VGroup(*[Dot([pg.x0 + 0.22, pg.rowy[i], 0], radius=0.08, color=TERRA) for i in (1, 3)])
        self.play(FadeIn(pg), GrowFromCenter(hits[0]), GrowFromCenter(hits[1]), run_time=0.08 * d)
        s = slip(4.6, 0.9, w=1.4, h=0.8)
        links = VGroup(*[connector((3.85, 0.9), (2.75, pg.rowy[i])) for i in (1, 3)])
        self.play(FadeIn(s), Create(links), FadeIn(lab("checked", 3.2, -1.6)), run_time=0.08 * d)
        self.play(Create(check(4.6, -0.1)), run_time=0.04 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.75, 0.25, w=1.9)), run_time=0.12 * d)
        finish(self)


# ═══ 2. INTRODUCTION ════════════════════════════════════════════════════════

class B04_Rcacopilot(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.4, -1.0, 1.0)
        box = iso.box(0, 0, 0, 1.7, 1.7, 1.2)
        self.play(FadeIn(box, shift=DOWN * 0.3), run_time=0.08 * d)
        lp = iso.p(0, 0.85, 0.6)
        self.play(FadeIn(padlock(lp[0], lp[1] - 0.05, s=0.42)), run_time=0.06 * d)
        self.play(FadeIn(T("up to 77%", 96).move_to([2.2, 0.6, 0])), run_time=0.1 * d)
        self.play(FadeIn(lab("per Microsoft Research", 2.2, -0.5, size=32)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.4, -1.15, w=3.2)), run_time=0.12 * d)
        finish(self)


class B05_Datadog(Scene):
    def construct(self):
        d = dur(self)
        iso = Iso(-0.6, -1.5, 1.0)
        plinth = iso.box(-0.2, -0.2, -0.3, 2.9, 2.9, 0.3, DARK_TOP, DARK_L, DARK_R)
        box = iso.box(0, 0, 0, 2.5, 2.5, 1.6)
        self.add(tag())
        self.play(FadeIn(plinth), FadeIn(box), FadeIn(lab("vendor platform", -0.6, -2.45)), run_time=0.09 * d)
        pg = logpage(-5.0, 0.6, w=1.2, h=1.5, rows=3)
        self.play(FadeIn(pg), run_time=0.05 * d)
        self.play(pg.animate.move_to([-3.6, 0.4, 0]), run_time=0.07 * d)
        self.play(FadeOut(pg), run_time=0.04 * d)
        self.play(FadeIn(scorecard(3.6, 0.6, w=1.7, h=1.3), shift=RIGHT * 0.4), run_time=0.08 * d)
        at(self, B_START)
        self.play(GrowFromCenter(Dot(iso.p(0.0, 1.25, 0.8), radius=0.1, color=TERRA)), run_time=0.12 * d)
        finish(self)


class B06_LockedVsOpen(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.8, -1.6, 1.0)
        locked = iso.box(0, 0, 0, 1.1, 1.1, 0.8)
        lp = iso.p(0, 0.55, 0.4)
        self.play(FadeIn(scorecard(-3.8, 1.25, w=1.8, h=1.3)), FadeIn(locked),
                  FadeIn(padlock(lp[0], lp[1], s=0.3)), FadeIn(lab("can't re-check", -3.8, -2.3)), run_time=0.12 * d)
        right = scorecard(2.6, 1.25, w=1.8, h=1.3)
        pages = VGroup(*[logpage(x, -0.9, w=0.9, h=1.1, rows=2) for x in (1.5, 2.6, 3.7)])
        links = VGroup(*[connector((2.6, 0.55), (x, -0.27)) for x in (1.5, 2.6, 3.7)])
        self.play(FadeIn(right), run_time=0.06 * d)
        self.play(Create(links), LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in pages], lag_ratio=0.25),
                  FadeIn(lab("anyone can re-check", 2.6, -2.1)), run_time=0.12 * d)
        at(self, B_START)
        self.play(Create(check(4.3, 1.25)), run_time=0.12 * d)
        finish(self)


# ═══ 3. METHODS ═════════════════════════════════════════════════════════════

class B07_Service(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.0, -1.2, 1.0)
        stack, lights = iso.server(0, 0, 0, w=1.6, d=1.6, slab=0.5, n=3)
        self.play(FadeIn(stack), FadeIn(lights), FadeIn(lab("FastAPI", -3.0, -1.9)), run_time=0.1 * d)
        db = cylinder(2.8, 0.2, w=1.9, h=1.7)
        self.play(Create(connector((-1.4, 0.3), (1.75, 0.3))), FadeIn(db), FadeIn(lab("Postgres", 2.8, -1.6)),
                  run_time=0.12 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.0, -1.35, w=3.0)), FadeIn(floor_shadow(2.85, -1.0, w=2.3)), run_time=0.12 * d)
        finish(self)


class B08_BreakService(Scene):
    def construct(self):
        d = dur(self)
        iso = Iso(-3.0, -1.3, 1.0)
        stack, lights = iso.server(0, 0, 0, w=1.6, d=1.6, slab=0.5, n=3)
        self.add(tag())
        self.play(FadeIn(stack), FadeIn(lights), FadeIn(lab("service", -3.0, -2.0)), run_time=0.08 * d)
        xs = (0.4, 2.2, 4.0)
        for i in range(3):
            page = logpage(xs[i], 0.4, w=1.3, h=1.7, rows=3)
            cause = Dot([xs[i] + 0.45, -0.25, 0], radius=0.08, color=TERRA)
            self.play(lights[i].animate.set_color(TERRA), FadeIn(page, shift=DOWN * 0.4), run_time=0.07 * d)
            self.play(GrowFromCenter(cause), run_time=0.02 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.0, -1.45, w=3.0)), run_time=0.12 * d)
        finish(self)


class B09_Loop(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        ring = Circle(radius=1.9, stroke_color=KRAFT, stroke_width=6).move_to([-0.6, 0.1, 0])
        self.play(Create(ring), run_time=0.06 * d)
        top = logpage(-0.6, 2.05, w=1.0, h=1.2, rows=2)
        brain = Iso(1.3, -0.35, 1.0).box(0, 0, 0, 0.6, 0.6, 0.5)
        chk = slip(-0.6, -1.8, w=1.1, h=0.7, dots=0)
        rec = slip(-2.5, 0.1, w=1.0, h=0.65)
        self.play(FadeIn(top), FadeIn(brain), FadeIn(chk), FadeIn(rec),
                  FadeIn(lab("Claude Code", 3.4, 0.2)), FadeIn(lab("checker", -0.6, -2.6)), run_time=0.1 * d)
        dot = Dot(ring.point_from_proportion(0.25), radius=0.11, color=TERRA)
        self.play(FadeIn(dot), run_time=0.02 * d)
        self.play(MoveAlongPath(dot, ring), run_time=0.16 * d, rate_func=linear)
        at(self, B_START)
        self.play(FadeIn(slip(-3.75, 0.1, w=1.0, h=0.65), shift=LEFT * 0.2), run_time=0.12 * d)
        finish(self)


class B10_ReadOnly(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pg = logpage(-3.2, 0.4, w=2.2, h=2.6, rows=4)
        self.play(FadeIn(pg), FadeIn(lab("read", -3.2, -1.5)), run_time=0.08 * d)
        self.play(FadeIn(lens(-2.9, 0.6)), run_time=0.06 * d)
        self.play(FadeIn(restart_button(2.8, 0.5)), FadeIn(lab("restart", 2.8, -0.9)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(cross(2.8, 0.5, s=0.75, w=12)), run_time=0.12 * d)
        finish(self)


class B11_StopRules(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        runs = VGroup(*[slip(x, 0.9, w=1.4, h=0.8) for x in (-4.4, -2.6, -0.8)])
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in runs], lag_ratio=0.3),
                  FadeIn(lab("3 runs", -2.6, -0.2)), run_time=0.14 * d)
        self.play(FadeIn(octagon(3.0, 0.7)), FadeIn(lab("stop", 3.0, -0.8)), run_time=0.1 * d)
        at(self, B_START)
        self.play(GrowFromCenter(Dot([3.0, 0.7, 0], radius=0.13, color=TERRA)), run_time=0.12 * d)
        finish(self)


class B12_HumanGate(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        empty = Rectangle(width=1.5, height=0.9, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-4.0, 1.2, 0])
        bad = VGroup(slip(-4.0, -0.4, w=1.5, h=0.9), cross(-2.85, -0.4, s=0.22))
        self.play(FadeIn(empty), FadeIn(bad), run_time=0.08 * d)
        iso, back, front = tray(2.6, -1.1, w=2.0, d=2.0, h=0.8)
        self.play(FadeIn(back), FadeIn(front), FadeIn(lab("engineer", 2.6, -1.8)), run_time=0.08 * d)
        empty.set_z_index(1); bad.set_z_index(1)
        self.play(empty.animate.scale(0.45).move_to(iso.p(1.4, 0.6, 0.3)), run_time=0.08 * d)
        self.play(bad.animate.scale(0.45).move_to(iso.p(0.6, 1.4, 0.3)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(2.6, -1.25, w=3.6)), run_time=0.12 * d)
        finish(self)


class B13_Resources(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        screen = Rectangle(width=2.6, height=1.6, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-2.8, 0.8, 0])
        base = Polygon([-4.3, -0.05, 0], [-1.3, -0.05, 0], [-1.0, -0.4, 0], [-4.6, -0.4, 0],
                       fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4)
        self.play(FadeIn(screen), FadeIn(base), FadeIn(lab("laptop", -2.8, -1.0)), run_time=0.12 * d)
        card = RoundedRectangle(width=2.6, height=1.6, corner_radius=0.15, fill_color=CARD, fill_opacity=1,
                                stroke_color=INK, stroke_width=5).move_to([2.6, 0.6, 0])
        stripe = Rectangle(width=2.2, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([2.6, 0.95, 0])
        spark = Dot([1.7, 0.2, 0], radius=0.09, color=TERRA)
        self.play(FadeIn(card), FadeIn(stripe), FadeIn(spark), FadeIn(lab("Claude Code seat", 2.6, -0.65)), run_time=0.12 * d)
        at(self, B_START)
        self.play(Create(check(-1.0, 1.9)), Create(check(4.3, 1.7)), run_time=0.12 * d)
        finish(self)


# ═══ 4. EVALUATION ══════════════════════════════════════════════════════════

class B14_TenIncidents(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pages = VGroup()
        for y in (1.4, -0.3):
            for x in (-4.2, -2.1, 0.0, 2.1, 4.2):
                pg = logpage(x, y, w=1.0, h=1.2, rows=2)
                pages.add(VGroup(pg, Dot([x + 0.3, y - 0.35, 0], radius=0.07, color=TERRA)))
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in pages], lag_ratio=0.12), run_time=0.22 * d)
        self.play(FadeIn(lab("known causes", 0, -1.6)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(0, -1.05, w=10.0)), run_time=0.12 * d)
        finish(self)


class B15_ThreeChecks(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        cols = VGroup(slip(-3.8, 1.0, w=1.6, h=0.95), slip(0.0, 1.0, w=1.6, h=0.95, dots=0),
                      Rectangle(width=1.6, height=0.95, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                stroke_width=4).move_to([3.8, 1.0, 0]))
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cols], lag_ratio=0.3), run_time=0.14 * d)
        self.play(FadeIn(lab("lines exist", -3.8, -1.0)), FadeIn(lab("cause matches", 0.0, -1.0)), run_time=0.1 * d)
        at(self, B_START)
        self.play(LaggedStart(*[Create(check(x - 0.1, -0.15)) for x in (-3.8, 0.0, 3.8)], lag_ratio=0.3), run_time=0.14 * d)
        finish(self)


class B16_Baseline(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        frames = VGroup(*[Rectangle(width=1.5, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                    stroke_width=5).move_to([x, 0.6, 0]) for x in (-1.8, 1.8)])
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.2) for f in frames], lag_ratio=0.3), run_time=0.12 * d)
        self.play(FadeIn(lab("keyword script", -1.8, -1.35)), FadeIn(lab("Claude", 1.8, -1.35)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(Line([-3.3, -0.82, 0], [3.3, -0.82, 0], color=GHOST, stroke_width=6)), run_time=0.12 * d)
        finish(self)


class B17_ExistsVsWill(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        small = Iso(-3.8, -0.9, 1.0).box(0, 0, 0, 0.7, 0.7, 0.5, DARK_TOP, DARK_L, DARK_R)
        self.play(FadeIn(small, shift=DOWN * 0.3), FadeIn(lab("exists", -3.8, -1.6)), run_time=0.12 * d)
        big = Iso(1.6, -1.7, 1.0)
        outline = VGroup(*[big.box(x, y, 0, 1.0, 1.0, 0.8, STAGE, STAGE, STAGE) for x, y in ((1.05, 1.05), (1.05, 0), (0, 1.05), (0, 0))])
        self.play(LaggedStart(*[Create(g) for g in outline], lag_ratio=0.2), FadeIn(lab("will exist", 1.6, -2.5)), run_time=0.16 * d)
        at(self, B_START)
        self.play(Create(big.box(0.5, 0.5, 0.85, 1.0, 1.0, 0.8, STAGE, STAGE, STAGE)), run_time=0.12 * d)
        finish(self)
