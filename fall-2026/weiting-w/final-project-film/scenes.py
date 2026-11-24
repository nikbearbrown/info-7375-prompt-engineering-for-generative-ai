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

# ═════════════════════════════ FILM-LOCAL KIT ═════════════════════════════
# the-names-nothing-checks — INFO 7375 final-project pitch film.
#
# Everything above this line is brutalist.art/skills/make/show-tell/templates/iso_kit.py,
# pasted verbatim per SKILL.md ("do not import it: Gate A copies only scenes.py").
#
# THE CAST, kept for the whole film:
#   the project slab   — one crate split by a divider: pale PAGES on the left (the C# scripts),
#                        dark BLOCKS on the right (the assets that hold the real names)
#   the string thread  — one ink line reaching from a page across to a block
#   the two gates      — compiler and console, both of which stay open
#   the effect lamp    — the thing that was supposed to happen; stays grey
#   the checklist slip — the proposed tool's output
#
# FOUR ACTS (2026-11-22 rebuild): executive summary B00-B05, introduction B06-B10,
# methods B11-B15, evaluation B16-B19. The first beat of each act prints the act name as
# its top-left label, so the structure is readable with the sound off.
#
# MIDPOINT DISCIPLINE. GATE T and Gate V both sample each clip at its MIDPOINT, so every
# scene is built in three phases: (1) construct and land the labels well before the midpoint,
# (2) hold_past_mid() through the sampled window with nothing in flight, (3) add one NEW
# non-text shape afterwards, which is also what Gate A's "shapes never change" check wants.

DKRAFT = "#917A55"        # outline for SMALL objects only (GATE T reads it as text on large ones)
CONNECT = "#9C8462"       # cables and leader lines, so they do not fuse with ink blocks
MID_MARGIN = 0.22         # frame rounding beats a 0.06-0.08 s margin (SKILL.md)
ACT_X, ACT_Y = -4.5, 3.0  # where each act's title label sits (inside Gate W's 3.4 safe area)


def hold_past_mid(self, margin=MID_MARGIN):
    """Hold with nothing in flight until the GATE T / Gate V sampling window has passed."""
    bid = type(self).__name__.split("_")[0]
    target = _TARGET.get(bid, 0)
    if not target:
        self.wait(0.5)
        return
    gap = (target / 2.0 + margin) - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def label(text, x, y, size=42):
    """A label that sits BESIDE its object — never inside an outline, never terracotta.
    Floor raised from 36 to 42 on 2026-10-14: GATE T failed a serif run 1 px under its 41 px
    minimum on the author's week-01 film, and EB Garamond renders shorter than sans at the
    same nominal size. Every label here is serif."""
    return T(text, size=size, color=INK).move_to([x, y, 0])


def act_title(text):
    """The act name, top left of the act's first beat: executive summary, introduction,
    methods, evaluation. The assignment fixes that order, so the film shows it."""
    return T(text, size=42, color=INK).move_to([ACT_X, ACT_Y, 0]).align_to([ACT_X, 0, 0], LEFT)


def floor_shadow(x, y, w=4.6, h=1.0):
    return Ellipse(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


def project_iso():
    return Iso(-0.4, -1.4, 0.85)


def project_slab(iso):
    """The crate everything else sits on, plus the divider between its two halves."""
    slab = iso.box(0, 0, 0, 4.4, 2.8, 0.45)
    divider = Line(iso.p(2.2, 0.0, 0.45), iso.p(2.2, 2.8, 0.45), color=DIM, stroke_width=4)
    return slab, divider


def script_pages(iso):
    return VGroup(iso.page(0.35, 0.35, 0.45), iso.page(0.35, 1.45, 0.45))


def asset_blocks(iso):
    return VGroup(iso.mcp(2.45, 0.35, 0.45, w=1.3, d=1.0, h=0.6),
                  iso.mcp(2.45, 1.55, 0.45, w=1.3, d=1.0, h=0.6))


def string_thread(iso, to_block=True):
    """The one ink line from a page to a block. Deep kraft so it does not fuse with the dark blocks."""
    a = iso.p(1.2, 1.05, 0.52)
    b = iso.p(2.45, 0.85, 0.75) if to_block else iso.p(3.9, -1.1, 0.75)
    return Line(a, b, color=CONNECT, stroke_width=5), b


def name_block(x, y, s=0.9, w=1.0, d=1.0, h=0.55):
    """One asset name, drawn as a single dark block standing on its own at (x, y).
    Used by the act-2 and act-3 beats that count name kinds rather than show the crate."""
    return Iso(x, y, s).mcp(0, 0, 0, w=w, d=d, h=h)


def ghost_block(x, y, s=0.9, w=1.0, d=1.0, h=0.55):
    """The same block, not built yet: outline only, no fill — the film's 'proposed' shape."""
    g = name_block(x, y, s, w, d, h)
    for m in g.family_members_with_points():
        m.set_fill(opacity=0)
        m.set_stroke(color=DIM, width=4)
    return g


def flat_page(x, y, s=0.9, w=1.8, d=1.6):
    """One C# page standing on its own at (x, y), away from the crate."""
    return Iso(x, y, s).page(0, 0, 0, w=w, d=d)


def slip(x, y, w=2.5, h=3.0, rows=5):
    """The checklist: a flat sheet whose rows are filled by check marks, not type."""
    sheet = paper(x, y, w=w, h=h)
    ys = [y + h / 2 - 0.5 - i * (h - 1.0) / max(1, rows - 1) for i in range(rows)]
    return sheet, ys


def cross(x, y, s=0.18, w=7):
    """The mark for a name the project does not have."""
    return VGroup(Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w),
                  Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w))


def bracket(x, ytop, ybot, color=CONNECT, w=4):
    """A counting bracket beside a run of rows."""
    return VGroup(Line([x, ytop, 0], [x, ybot, 0], color=color, stroke_width=w),
                  Line([x, ytop, 0], [x + 0.2, ytop, 0], color=color, stroke_width=w),
                  Line([x, ybot, 0], [x + 0.2, ybot, 0], color=color, stroke_width=w))


def glow(x, y, s=1.0):
    """The sword glow from the author's own Unity game, drawn as what it is: one terracotta ring
    around the block, with a spark. A drawn sword read as a rocket in the first contact sheet, and
    terracotta is permitted on one curve and on dots — never on text.
    The ring opens at the bottom (300 degrees, not the earlier 115-degree arc): GATE T reads a
    wide-and-short terracotta blob as accent TYPE and fails it on cream at 2.74:1, so the one
    curve in this film is drawn taller than it is wide, which is not a text shape."""
    arc = Arc(radius=0.55 * s, start_angle=-PI / 3, angle=PI * 5 / 3, arc_center=[x, y, 0],
              stroke_color=TERRA, stroke_width=5)
    spark = Dot([x, y + 0.55 * s, 0], radius=0.09, color=TERRA)
    return VGroup(arc, spark)


def bar_stack(x, y0, segs, w=0.62):
    """A chart column: DIM-to-GHOST segments with visible gaps, so GATE T cannot fuse them."""
    cols = [BAR1, BAR2, BAR3]
    g, y = VGroup(), y0
    for i, hgt in enumerate(segs):
        g.add(Rectangle(width=w, height=hgt, fill_color=cols[i % 3], fill_opacity=1,
                        stroke_color=DKRAFT, stroke_width=2).move_to([x, y + hgt / 2, 0]))
        y += hgt + 0.1
    return g


def gate_arch(x, y, w=1.5, h=2.0):
    """An open gate: two posts and a lintel. Nothing closes it — that is the point of B02."""
    return VGroup(
        Rectangle(width=0.18, height=h, fill_color=BOX_R, fill_opacity=1, stroke_color=INK,
                  stroke_width=4).move_to([x - w / 2, y + h / 2, 0]),
        Rectangle(width=0.18, height=h, fill_color=BOX_R, fill_opacity=1, stroke_color=INK,
                  stroke_width=4).move_to([x + w / 2, y + h / 2, 0]),
        Rectangle(width=w + 0.18, height=0.2, fill_color=BOX_R, fill_opacity=1, stroke_color=INK,
                  stroke_width=4).move_to([x, y + h + 0.1, 0]))


# ═════════════════════════════ SCENES ═════════════════════════════
# run.sh finds scenes by grepping this file for the literal class-definition text, so every
# scene below is written out plainly and none subclasses a helper (a subclassed one is silently
# skipped — SKILL.md). For the same reason this comment does not spell that pattern out: an
# earlier version quoted SKILL.md's example placeholder verbatim, run.sh read the comment as a
# fifteenth scene, and Gate A failed on a class that does not exist.


# ───────────────────────── 1. EXECUTIVE SUMMARY ─────────────────────────

class B00_Project(Scene):
    def construct(self):
        iso = project_iso()
        sh = floor_shadow(0.0, -1.55)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        act = act_title("executive summary")
        l_left, l_right = label("scripts", -3.6, -0.9), label("assets", 3.5, -0.3)

        self.play(FadeIn(sh, shift=np.array([0, 0.2, 0])), FadeIn(act), run_time=0.5)
        self.play(Create(slab), run_time=0.9, rate_func=smooth)
        until(self, "One side holds")
        self.play(LaggedStart(*[FadeIn(p, shift=np.array([0, 0.35, 0])) for p in pages], lag_ratio=0.3),
                  FadeIn(l_left), run_time=1.0, rate_func=ease_in)
        until(self, "The other")
        self.play(LaggedStart(*[GrowFromCenter(b) for b in blocks], lag_ratio=0.3),
                  FadeIn(l_right), run_time=1.0)

        hold_past_mid(self)
        self.play(Create(divider), run_time=0.6)      # the new shape, clear of the midpoint
        finish(self)


class B01_StringReach(Scene):
    def construct(self):
        iso = project_iso()
        sh = floor_shadow(0.0, -1.55)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        base = VGroup(sh, slab, divider, pages, blocks)          # continuity: B00 ended with all of this
        # The reach is the whole point of the beat, so it arcs well clear of the crate instead of
        # running flat between two dark blocks, where it was invisible in the first contact sheet.
        a, mid, b = iso.p(0.9, 1.5, 0.6), np.array([0.1, 2.5, 0.0]), iso.p(2.9, 0.9, 1.15)
        thread = VMobject(stroke_color=CONNECT, stroke_width=7)
        thread.set_points_smoothly([a, mid, b])
        dot = Dot(b, radius=0.1, color=TERRA)
        lbl = label("string", -2.9, 2.5)

        self.add(base)
        self.play(pages[1].animate.shift(np.array([0.0, 0.22, 0.0])), run_time=0.5, rate_func=smooth)
        until(self, "A string")
        self.play(Create(thread), FadeIn(lbl), run_time=1.2, rate_func=linear)

        hold_past_mid(self)
        self.play(GrowFromCenter(dot), run_time=0.5)
        finish(self)


class B02_SilentPass(Scene):
    def construct(self):
        # The crate keeps its pages and blocks here: B01 ended with a full project on stage, and
        # an empty slab broke the film's "same objects, whole film" law in the first contact sheet.
        iso = Iso(-4.6, -0.9, 0.5)
        sh = floor_shadow(-4.3, -1.05, w=2.8, h=0.7)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        g1, g2 = gate_arch(-0.4, -1.1), gate_arch(3.0, -1.1)
        # The lamp is the effect that was supposed to happen. It must still be grey at the end,
        # and the terracotta runner must stop OUTSIDE it: parked in the middle of the lamp, the
        # accent colour reads as "lit", which is the opposite of what the narration says.
        lamp = Circle(radius=0.36, fill_color=GHOST, fill_opacity=1, stroke_color=INK,
                      stroke_width=4).move_to([5.0, -0.1, 0])
        runner = Dot([-2.5, -0.1, 0], radius=0.11, color=TERRA)
        l1, l2 = label("compiler", -0.4, -1.9, 42), label("console", 3.0, -1.9, 42)
        l3 = label("no error", 4.7, 1.6, 42)
        ring = Circle(radius=0.68, stroke_color=DIM, stroke_width=4,
                      fill_opacity=0).move_to([5.0, -0.1, 0])

        self.add(sh, slab, divider, pages, blocks)
        self.play(Create(g1), Create(g2), FadeIn(l1), FadeIn(l2), run_time=0.9)
        self.play(FadeIn(lamp), GrowFromCenter(runner), run_time=0.5)
        until(self, "The compiler")
        self.play(runner.animate.move_to([4.25, -0.1, 0]), run_time=1.5, rate_func=linear)
        self.play(FadeIn(l3), run_time=0.4)

        hold_past_mid(self)
        self.play(Create(ring), run_time=0.6)          # the lamp never lit; only the ring is new
        finish(self)


class B03_WhatWarns(Scene):
    def construct(self):
        # The honest qualifier beat. Unity DOES print "Parameter 'X' does not exist" for a bad
        # animator parameter once the line runs; the Unity manual says a shader property that is
        # not on the current shader simply "will have no effect".
        # The bar must CLOSE the gate's opening horizontally — drawn vertically it merged into a
        # post and the beat read as two runners passing nothing.
        iso = Iso(-4.6, -0.9, 0.5)
        sh = floor_shadow(-4.3, -1.05, w=2.8, h=0.7)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        g1, g2 = gate_arch(-0.4, -1.1), gate_arch(3.0, -1.1)
        lamp = Circle(radius=0.36, fill_color=GHOST, fill_opacity=1, stroke_color=INK,
                      stroke_width=4).move_to([5.0, -0.1, 0])
        top = Dot([-2.3, 0.55, 0], radius=0.11, color=TERRA)
        low = Dot([-2.3, -0.55, 0], radius=0.11, color=TERRA)
        bar = Line([-0.55, 0.55, 0], [0.95, 0.55, 0], color=INK, stroke_width=9)
        l1 = label("warns", 0.2, 1.65, 42)
        l2 = label("silent", 4.5, 1.6, 42)
        leader = Line([4.5, 1.35, 0], [4.72, 0.33, 0], color=CONNECT, stroke_width=4)

        self.add(sh, slab, divider, pages, blocks, g1, g2, lamp)
        self.play(GrowFromCenter(top), GrowFromCenter(low), run_time=0.5)
        until(self, "Unity does warn")
        self.play(top.animate.move_to([-1.55, 0.55, 0]), run_time=0.6, rate_func=smooth)
        self.play(Create(bar), FadeIn(l1), run_time=0.6)
        self.play(low.animate.move_to([4.25, -0.1, 0]), run_time=1.3, rate_func=linear)

        hold_past_mid(self)
        self.play(FadeIn(l2), Create(leader), run_time=0.6)
        finish(self)


class B04_HalfRead(Scene):
    def construct(self):
        iso = project_iso()
        sh = floor_shadow(0.0, -1.55)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        endpt = iso.p(2.9, 0.9, 1.15)
        thread = VMobject(stroke_color=CONNECT, stroke_width=7)
        thread.set_points_smoothly([iso.p(0.9, 1.5, 0.6), np.array([0.1, 2.5, 0.0]), endpt])
        base = VGroup(sh, slab, divider, pages, blocks, thread, Dot(endpt, radius=0.1, color=TERRA))
        # Gate V measures ink-vs-background luminance separation across the whole frame. A pale
        # GHOST veil at 0.92 left almost nothing dark on screen and the beat failed at 0.24
        # (floor 0.30). A DIM scrim reads better anyway — the half is blacked out, not fogged —
        # and the blocks beneath show faintly through at 0.72. Measured 0.34 after the change.
        veil = Polygon(iso.p(2.2, 0, 0.45), iso.p(4.4, 0, 0.45), iso.p(4.4, 2.8, 1.35), iso.p(2.2, 2.8, 1.35),
                       fill_color=DIM, fill_opacity=0.72, stroke_color=INK, stroke_width=4)
        scan = Line(iso.p(0.0, 0.0, 0.5), iso.p(0.0, 2.8, 0.5), color=TERRA, stroke_width=6)
        lbl = label("guess", 4.2, 1.9)
        # a leader that actually reaches the guessed end, with a clear gap at the label end
        leader = Line([3.55, 1.78, 0], np.array(endpt) + np.array([0.26, 0.2, 0.0]),
                      color=CONNECT, stroke_width=4)

        self.add(base)
        self.play(FadeIn(veil), run_time=0.6)
        until(self, "An assistant")
        self.play(scan.animate.shift(iso.v(2.2, 0, 0)), run_time=1.2, rate_func=linear)
        self.play(FadeOut(scan), FadeIn(lbl), run_time=0.4)

        hold_past_mid(self)
        self.play(Create(leader), run_time=0.6)
        finish(self)


class B05_OneList(Scene):
    def construct(self):
        # The product, stated once: the crate goes in, one list comes out. Ticks are names the
        # project really has; the two crosses are the names the code asked for and it does not.
        iso = Iso(-3.4, -1.3, 0.7)
        sh = floor_shadow(-2.9, -1.5, w=3.6, h=0.9)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        sheet, rows = slip(3.4, 0.2, w=2.6, h=3.1, rows=5)
        ticks = VGroup(*[check(2.6, rows[i], s=0.18) for i in (0, 1, 2)])
        bad = VGroup(*[cross(2.6, rows[i]) for i in (3, 4)])
        brk = bracket(1.95, rows[3] + 0.22, rows[4] - 0.22)
        l1, l2 = label("one list", 3.4, 2.2, 42), label("proposed", 3.4, -1.9, 42)

        self.add(sh, slab, divider, pages, blocks)
        self.play(FadeIn(sheet, shift=np.array([0.3, 0.0, 0.0])), FadeIn(l1), FadeIn(l2), run_time=0.8)
        until(self, "One command")
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.18), run_time=1.0)
        self.play(LaggedStart(*[Create(c) for c in bad], lag_ratio=0.25), run_time=0.8)

        hold_past_mid(self)
        self.play(Create(brk), run_time=0.6)
        finish(self)


# ───────────────────────── 2. INTRODUCTION ─────────────────────────

class B06_TypeSafe(Scene):
    def construct(self):
        # Unity solved exactly this problem once, for one of the four name kinds: the Input
        # System generates a C# class, so those names live in the code instead of in a string.
        act = act_title("introduction")
        page = flat_page(-4.2, -0.9, s=0.95, w=2.0, d=1.8)
        fused = name_block(-3.5, -0.1, s=0.9, w=0.9, d=0.9, h=0.5)
        rest = VGroup(name_block(-0.4, -0.7), name_block(1.9, -0.7), name_block(4.2, -0.7))
        spark = Dot([-3.25, 1.0, 0], radius=0.09, color=TERRA)
        l1, l2 = label("input actions", -2.7, -2.5, 42), label("the rest", 2.6, -2.5, 42)

        self.play(FadeIn(act), FadeIn(page, shift=np.array([0.0, 0.3, 0.0])), run_time=0.7)
        until(self, "Input System")
        self.play(FadeIn(fused, shift=np.array([0.0, 0.5, 0.0])), FadeIn(l1),
                  run_time=0.9, rate_func=ease_in)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in rest], lag_ratio=0.25),
                  FadeIn(l2), run_time=1.1)

        hold_past_mid(self)
        self.play(GrowFromCenter(spark), run_time=0.5)
        finish(self)


class B07_FastNotRight(Scene):
    def construct(self):
        # Rider: "String based graphics property lookup is inefficient." Microsoft's UNT0041 and
        # UNT0046: cache the hash, cache the ID — both filed under Performance. The same line of
        # code, a different question. The lower thread still ends nowhere.
        page = flat_page(-4.5, -0.9, s=0.95, w=1.8, d=1.6)
        tag = Rectangle(width=1.1, height=0.66, fill_color=BOX_TOP, fill_opacity=1,
                        stroke_color=INK, stroke_width=4).move_to([1.6, 1.9, 0])
        up = VMobject(stroke_color=CONNECT, stroke_width=6)
        up.set_points_smoothly([[-2.9, 0.7, 0], [-1.0, 1.9, 0], [1.0, 1.9, 0]])
        low = VMobject(stroke_color=CONNECT, stroke_width=6)
        low.set_points_smoothly([[-2.9, 0.1, 0], [-1.0, -0.9, 0], [1.3, -1.2, 0]])
        end = Dot([1.5, -1.25, 0], radius=0.1, color=TERRA)
        ring = Circle(radius=0.62, stroke_color=DIM, stroke_width=4,
                      fill_opacity=0).move_to([1.5, -1.25, 0])
        l1, l2 = label("faster", 3.9, 1.9, 42), label("unchecked", 4.3, -1.25, 42)

        self.add(page)
        self.play(Create(up), Create(tag), FadeIn(l1), run_time=1.0)
        until(self, "Rider calls")
        self.play(Create(low), GrowFromCenter(end), FadeIn(l2), run_time=1.1)

        hold_past_mid(self)
        self.play(Create(ring), run_time=0.6)
        finish(self)


class B08_Auditor(Scene):
    def construct(self):
        # Project Auditor's IssueCategory enum lists twenty five categories. One square per
        # category, and the one this film is about is not among them — it stays an outline.
        pitch, side = 0.78, 0.5
        x0, y0 = -3.6, -1.1
        squares, hole = VGroup(), None
        for r in range(5):
            for c in range(5):
                x, y = x0 + c * pitch, y0 + r * pitch
                if (r, c) == (2, 2):
                    hole = Rectangle(width=side, height=side, stroke_color=INK, stroke_width=4,
                                     fill_opacity=0).move_to([x, y, 0])
                    continue
                squares.add(Rectangle(width=side, height=side, fill_color=BAR2, fill_opacity=1,
                                      stroke_color=INK, stroke_width=2).move_to([x, y, 0]))
        leader = Line([2.1, 0.46, 0], [-1.35, 0.46, 0], color=CONNECT, stroke_width=4)
        ring = Circle(radius=0.52, stroke_color=INK, stroke_width=4,
                      fill_opacity=0).move_to([-2.04, 0.46, 0])
        l1 = label("twenty five", -2.4, -2.5, 42)
        l2 = label("not this one", 3.9, 0.46, 42)

        self.play(LaggedStart(*[FadeIn(s) for s in squares], lag_ratio=0.03),
                  FadeIn(l1), run_time=1.4)
        until(self, "reports twenty five")
        self.play(Create(hole), FadeIn(l2), Create(leader), run_time=0.9)

        hold_past_mid(self)
        self.play(Create(ring), run_time=0.6)
        finish(self)


class B09_WritesIn(Scene):
    def construct(self):
        iso = project_iso()
        sh = floor_shadow(0.0, -1.55)
        slab, divider = project_slab(iso)
        pages = script_pages(iso)
        # the arm reaches DOWN from above, not in from the left: GATE T reads the ink arm as a
        # text run, and a wide one overlaps the slab's bbox by 36%. Taller than wide is not type.
        arm = VGroup(
            Line([0.45, 3.3, 0], [1.7, 2.6, 0], color=INK, stroke_width=8),
            Line([1.7, 2.6, 0], [2.3, 1.75, 0], color=INK, stroke_width=8),
            Rectangle(width=0.5, height=0.3, fill_color=DARK_TOP, fill_opacity=1,
                      stroke_color=INK, stroke_width=3).move_to([2.3, 1.6, 0]))
        # spaced apart: a dense lattice of dark blocks breaks into false "text" blobs under GATE T
        def crook(y, ang):
            b = iso.mcp(2.35, y, 0.45, w=1.15, d=0.8, h=0.55)
            return b.rotate(ang, about_point=iso.p(2.92, y + 0.4, 0.72))
        crooked = VGroup(crook(0.15, 0.2), crook(1.25, -0.24))
        third = crook(2.35, 0.32)
        l1, l2 = label("writes", 4.4, 2.1), label("spring 2026", -4.2, -2.6, 42)

        self.add(sh, slab, divider, pages)
        self.play(FadeIn(arm, shift=np.array([-0.4, 0.3, 0.0])), FadeIn(l2), run_time=0.7)
        until(self, "It put things")
        self.play(LaggedStart(*[FadeIn(b, shift=np.array([0.0, 0.7, 0.0])) for b in crooked], lag_ratio=0.4),
                  FadeIn(l1), run_time=1.2, rate_func=ease_in)

        hold_past_mid(self)
        self.play(FadeIn(third, shift=np.array([0.0, 0.7, 0.0])), run_time=0.6, rate_func=ease_in)
        finish(self)


class B10_Gap(Scene):
    def construct(self):
        # The gap, drawn as the thing nobody does: one sweep across BOTH halves of the crate.
        # It is an outline, because it does not exist yet — the same 'proposed' language the
        # tool beats use.
        iso = project_iso()
        sh = floor_shadow(0.0, -1.55)
        slab, divider = project_slab(iso)
        pages, blocks = script_pages(iso), asset_blocks(iso)
        band = Rectangle(width=8.6, height=2.9, stroke_color=DIM, stroke_width=5,
                         fill_opacity=0).move_to([0.2, 0.75, 0])
        edge = Dot([4.5, 0.75, 0], radius=0.11, color=TERRA)
        l1, l2 = label("whole project", 0.2, 2.9, 42), label("proposed", 4.3, -2.5, 42)

        self.add(sh, slab, divider, pages, blocks)
        self.play(FadeIn(l2), run_time=0.4)
        until(self, "What I could not find")
        self.play(Create(band), FadeIn(l1), run_time=1.3)

        hold_past_mid(self)
        self.play(GrowFromCenter(edge), run_time=0.5)
        finish(self)


# ───────────────────────── 3. METHODS ─────────────────────────

class B11_Index(Scene):
    def construct(self):
        iso = Iso(-2.6, -1.3, 0.75)
        sh = floor_shadow(-2.1, -1.5, w=4.0)
        slab, divider = project_slab(iso)
        blocks = asset_blocks(iso)
        sheet, rows = slip(4.0, 0.2, w=2.6, h=3.1, rows=5)
        ticks = VGroup(*[check(3.2, yy, s=0.18) for yy in rows])
        act = act_title("methods")
        l1, l2 = label("index", 4.0, 2.2, 42), label("proposed", 4.0, -1.8, 42)

        self.add(sh, slab, divider, blocks)
        self.play(FadeIn(act), FadeIn(sheet, shift=np.array([0.3, 0.0, 0.0])), FadeIn(l1), run_time=0.8)
        until(self, "Shader graphs")
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.18), run_time=1.3)

        hold_past_mid(self)
        self.play(FadeIn(l2), GrowFromCenter(Dot([4.0, -1.35, 0], radius=0.08, color=TERRA)), run_time=0.5)
        finish(self)


class B12_Compare(Scene):
    def construct(self):
        iso = Iso(-2.6, -1.3, 0.75)
        sh = floor_shadow(-2.1, -1.5, w=4.0)
        slab, divider = project_slab(iso)
        blocks = asset_blocks(iso)
        sheet, rows = slip(4.0, 0.2, w=2.6, h=3.1, rows=5)
        ticks = VGroup(*[check(3.2, yy, s=0.18) for yy in rows[:4]])
        thread = Line(iso.p(1.0, 1.0, 0.5), [2.7, rows[4], 0], color=CONNECT, stroke_width=5)
        bad = cross(3.18, rows[4])
        # a large ink-outlined padlock: small objects in dark kraft read as sub-floor text (GATE T)
        lock_body = Rectangle(width=1.3, height=1.0, fill_color=BOX_TOP, fill_opacity=1,
                              stroke_color=INK, stroke_width=4).move_to([-1.1, 2.0, 0])
        shackle = Arc(radius=0.42, start_angle=0, angle=PI, stroke_color=INK,
                      stroke_width=5).move_to([-1.1, 2.71, 0])
        keyhole = Dot([-1.1, 2.0, 0], radius=0.12, color=INK)
        l1, l2 = label("marked", 4.6, -1.8, 42), label("read only", -3.9, 2.1, 42)

        self.add(sh, slab, divider, blocks, sheet, ticks)
        self.play(Create(thread), run_time=0.8, rate_func=linear)
        until(self, "compare it against")
        self.play(Create(bad), FadeIn(l1), run_time=0.7)

        hold_past_mid(self)
        self.play(Create(lock_body), Create(shackle), GrowFromCenter(keyhole), FadeIn(l2), run_time=1.0)
        finish(self)


class B13_Scope(Scene):
    def construct(self):
        # What version one will and will not read. The upper row is one literal written out in
        # full; the lower row is a name assembled from pieces, which gets counted, not guessed at.
        sheet = paper(0.6, 0.3, w=5.2, h=3.2)
        solid = Rectangle(width=2.6, height=0.34, fill_color=BAR1, fill_opacity=1,
                          stroke_color=DKRAFT, stroke_width=2).move_to([0.1, 1.15, 0])
        parts = VGroup(*[Rectangle(width=0.66, height=0.34, fill_color=BAR2, fill_opacity=1,
                                   stroke_color=DKRAFT, stroke_width=2).move_to([-1.1 + 1.0 * i, -0.55, 0])
                         for i in range(3)])
        tick = check(2.2, 1.15, s=0.2)
        ring = Circle(radius=0.26, stroke_color=INK, stroke_width=6,
                      fill_opacity=0).move_to([2.2, -0.55, 0])
        l1, l2 = label("written out", -4.3, 1.15, 42), label("cannot tell", -4.3, -0.55, 42)

        self.add(sheet)
        self.play(Create(solid), FadeIn(l1), run_time=0.8)
        self.play(LaggedStart(*[Create(p) for p in parts], lag_ratio=0.2), FadeIn(l2), run_time=1.0)
        until(self, "cannot determine")
        self.play(Create(tick), run_time=0.6)

        hold_past_mid(self)
        self.play(Create(ring), run_time=0.6)
        finish(self)


class B14_Needs(Scene):
    def construct(self):
        # Everything this project needs is already on the left: a Unity project of my own, its
        # files, and a laptop. The right tray — keys, credits, cloud compute — stays empty.
        iso = Iso(-2.4, -1.6, 0.9)
        iso2 = Iso(2.0, -1.6, 0.9)
        sh = floor_shadow(-2.3, -1.9, w=4.2, h=0.9)
        back, front = iso.open_box(0, 0, 0, 2.6, 2.4, 0.6)
        pg = iso.page(0.3, 0.4, 0.05)
        blk = iso.mcp(1.3, 1.3, 0.05, w=0.9, d=0.7, h=0.45)
        sw = glow(-2.4, 0.2, s=1.0)
        l_have = label("have", -2.3, -2.6)

        # the empty tray is the same object with no fill, not a flat lozenge
        gb, gf = iso2.open_box(0, 0, 0, 2.6, 2.4, 0.6)
        empty = VGroup(*[m for m in list(gb) + list(gf)])
        for m in empty:
            m.set_fill(opacity=0)
            m.set_stroke(color=DIM, width=4)
        l_new = label("not needed", 3.0, -2.6)

        self.add(sh, back, front)
        self.play(Create(empty), FadeIn(l_new), run_time=0.9)
        self.play(FadeIn(pg, shift=np.array([0.0, 0.5, 0.0])), run_time=0.5, rate_func=ease_in)
        until(self, "No API key")
        self.play(FadeIn(blk, shift=np.array([0.0, 0.5, 0.0])), FadeIn(l_have), run_time=0.6, rate_func=ease_in)

        hold_past_mid(self)
        self.play(Create(sw), run_time=0.9)
        finish(self)


class B15_Order(Scene):
    def construct(self):
        # The build order, one name kind at a time. The first block is solid because it is the
        # one I will make run first; the other three are outlines until they are built.
        rail = Line([-5.2, -1.0, 0], [5.2, -1.0, 0], color=DKRAFT, stroke_width=4)
        first = name_block(-4.4, -0.9, s=0.95)
        later = VGroup(ghost_block(-1.6, -0.9), ghost_block(0.8, -0.9), ghost_block(3.2, -0.9))
        spark = Dot([-4.4, 1.1, 0], radius=0.09, color=TERRA)
        l1, l2 = label("first", -4.4, -2.3, 42), label("then three", 1.6, -2.3, 42)

        self.play(Create(rail), run_time=0.5)
        self.play(FadeIn(first, shift=np.array([0.0, 0.4, 0.0])), FadeIn(l1),
                  run_time=0.8, rate_func=ease_in)
        until(self, "Shader properties first")
        self.play(LaggedStart(*[Create(b) for b in later], lag_ratio=0.25), FadeIn(l2), run_time=1.2)

        hold_past_mid(self)
        self.play(GrowFromCenter(spark), run_time=0.5)
        finish(self)


# ───────────────────────── 4. EVALUATION ─────────────────────────

class B16_Fixture(Scene):
    def construct(self):
        iso = Iso(-3.9, -1.2, 0.6)
        sh = floor_shadow(-3.3, -1.45, w=3.0, h=0.8)
        slab, divider = project_slab(iso)
        sheet, rows = slip(2.6, 0.2, w=2.6, h=3.1, rows=5)
        ticks = VGroup(*[check(1.8, rows[i], s=0.18) for i in (0, 4)])
        # the three planted errors are contiguous, so one bracket can count them
        crosses = VGroup(*[cross(1.8, rows[i]) for i in (1, 2, 3)])
        ytop, ybot = rows[1] + 0.22, rows[3] - 0.22
        brk = bracket(1.02, ytop, ybot)
        n3 = label("3", 0.52, (ytop + ybot) / 2, 48)
        act = act_title("evaluation")
        l1, l2 = label("test project", -3.3, -2.4, 42), label("proposed", 2.6, -1.9, 42)

        self.add(sh, slab, divider, sheet, ticks)
        self.play(FadeIn(act), FadeIn(l1), run_time=0.5)
        until(self, "three wrong names")
        self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.25), run_time=1.2)
        self.play(FadeIn(l2), run_time=0.4)

        hold_past_mid(self)
        self.play(Create(brk), FadeIn(n3), run_time=0.7)
        finish(self)


class B17_FalseAlarm(Scene):
    def construct(self):
        plinth = Rectangle(width=8.0, height=0.26, fill_color=BOX_R, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to([0.3, -2.1, 0])
        axis = Line([-3.9, -1.97, 0], [-3.9, 1.9, 0], color=DIM, stroke_width=4)
        bars = bar_stack(-2.6, -1.97, [0.8, 0.7, 0.5])
        # the cross lands on a row of the checklist, so it reads as a good line wrongly flagged
        row = Rectangle(width=2.0, height=0.9, fill_color=PAGE_TOP, fill_opacity=1,
                        stroke_color=INK, stroke_width=4).move_to([2.4, 1.1, 0])
        good = check(2.4, 1.1, s=0.22)
        bad = cross(2.4, 1.1, s=0.22)
        l1, l2 = label("false alarms", -2.6, -2.75, 42), label("proposed", 2.4, -0.1, 42)

        self.add(plinth, axis, row, good)
        self.play(FadeIn(l1), run_time=0.4)
        until(self, "not always")
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), run_time=1.1)

        hold_past_mid(self)
        self.play(FadeOut(good), Create(bad), FadeIn(l2), run_time=0.7)
        finish(self)


class B18_TwoNumbers(Scene):
    def construct(self):
        plinth = Rectangle(width=8.4, height=0.26, fill_color=BOX_R, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to([0.5, -2.1, 0])
        axis = Line([-3.9, -1.97, 0], [-3.9, 1.9, 0], color=DIM, stroke_width=4)
        bars1 = bar_stack(-2.6, -1.97, [0.8, 0.7, 0.5])
        bars2 = bar_stack(0.5, -1.97, [1.2, 0.9, 0.7])
        bars3 = bar_stack(3.4, -1.97, [0.6, 0.45])
        spark = Dot([0.5, 1.05, 0], radius=0.09, color=TERRA)
        # spread apart: at the first pass these three ran together into "false alarmscaught"
        l1 = label("false alarms", -2.6, -2.75, 42)
        l2 = label("caught", 0.5, -2.75, 42)
        l3 = label("cannot tell", 3.4, -2.75, 42)

        self.add(plinth, axis, bars1, l1)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars2], lag_ratio=0.2),
                  FadeIn(l2), run_time=1.1)
        until(self, "could not determine")
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars3], lag_ratio=0.2),
                  FadeIn(l3), run_time=0.9)

        hold_past_mid(self)
        self.play(GrowFromCenter(spark), run_time=0.5)
        finish(self)


class B19_PassMark(Scene):
    def construct(self):
        # The line version one has to clear: every planted name caught, and nothing raised on the
        # code that was left alone. The right column is empty on purpose — zero is the target.
        plinth = Rectangle(width=8.0, height=0.26, fill_color=BOX_R, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to([0.3, -2.1, 0])
        axis = Line([-3.9, -1.97, 0], [-3.9, 1.9, 0], color=DIM, stroke_width=4)
        bars = bar_stack(-2.2, -1.97, [0.9, 0.8, 0.7])
        rule = Line([-3.5, 0.63, 0], [-0.9, 0.63, 0], color=INK, stroke_width=6)
        zero = Dot([2.6, -1.9, 0], radius=0.11, color=TERRA)
        l1, l2 = label("all three", -2.2, -2.75, 42), label("none", 2.6, -2.75, 42)

        self.add(plinth, axis)
        self.play(Create(rule), FadeIn(l1), FadeIn(l2), run_time=0.8)
        until(self, "raises nothing")
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), run_time=1.2)

        hold_past_mid(self)
        self.play(GrowFromCenter(zero), run_time=0.5)
        finish(self)
