"""scenes.py — checkedsql-pitch (Siddhesh Nikam, INFO 7375). iso_kit.py pasted verbatim, then this film's scenes."""
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


# ═════════════════════════════ checkedsql-pitch — Siddhesh Nikam, INFO 7375 ═════════════════════════════
# Every body drawing is a sketch of something that WILL exist, so each carries the on-screen tag
# "sketch · planned" (assignment honesty rule: mock-ups labelled as constructed).

def _target_and_text(self):
    bid = type(self).__name__.split("_")[0]
    return _NARR.get(bid, ""), _TARGET.get(bid, 0)


def cue(self, phrase, dur, lead=0.25, margin=0.24):
    """Wait for `phrase`, then make sure an animation of `dur` seconds stays off the clip MIDPOINT
    (GATE T and Gate V sample there). If it would overlap, start it just after the midpoint."""
    n, target = _target_and_text(self)
    now = _elapsed(self)
    t = now
    if n and target and phrase and phrase in n:
        t = max(now, target * n.index(phrase) / len(n) - lead)
    if target:
        lo, hi = target / 2 - margin, target / 2 + margin
        if t < hi and t + dur > lo:
            t = max(t, hi)
    if t - now > 0.02:
        self.wait(t - now)


def go(self, phrase, dur, *anims, **kw):
    cue(self, phrase, dur)
    self.play(*anims, run_time=dur, **kw)


def planned_tag():
    return T("sketch · planned", 32).move_to([-4.3, 3.0, 0])


def sheet(x, y, w=1.2, h=1.5, n=3):
    """A flat white page with ghost text lines (a question, a query, a log)."""
    pg = paper(x, y, w, h)
    lines = VGroup(*[Line([x - w / 2 + 0.2, y + h / 2 - 0.35 - i * 0.3, 0], [x + w / 2 - 0.2, y + h / 2 - 0.35 - i * 0.3, 0],
                          color=GHOST, stroke_width=5) for i in range(n)])
    return VGroup(pg, lines)


def panel(x, y, w, h):
    """A pale UI window: card face, ink outline, grey title band (never a dark band inside an ink card)."""
    face = RoundedRectangle(width=w, height=h, corner_radius=0.14, fill_color=CARD, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    band = Rectangle(width=w - 0.3, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x, y + h / 2 - 0.3, 0])
    return VGroup(face, band)


DB = Iso(0.0, -1.9, 0.8)


def database(iso=DB):
    stack, lights = iso.server(-0.7, -0.7, 0, w=1.4, d=1.4, slab=0.5, n=3)
    return stack, lights


class B00_OneSentence(Scene):
    def construct(self):
        self.add(planned_tag())
        stack, lights = database()
        self.add(stack, lights)
        q = sheet(-5.0, 0.3)
        self.play(q.animate.move_to([-2.6, 0.3, 0]), run_time=0.9, rate_func=smooth)
        self.play(FadeIn(T("question", 40).move_to([-2.6, -1.0, 0])), run_time=0.4)
        go(self, "run it on", 0.6, *[l.animate.set_color(TERRA) for l in lights])
        out = sheet(0.0, 0.3)
        out.set_z_index(-1)
        self.add(out)
        go(self, "show the answer", 0.8, out.animate.move_to([2.6, 0.3, 0]))
        ck = check(4.0, 0.9, s=0.3)
        self.play(Create(ck), FadeIn(T("checked", 40).move_to([2.6, -1.0, 0])), run_time=0.5)
        finish(self)


REPO = Iso(0.0, -2.4, 0.75)


def drop(self, mob, dur=0.7):
    mob.shift(UP * 4.5)
    self.add(mob)
    self.play(mob.animate.shift(DOWN * 4.5), run_time=dur, rate_func=ease_in)


class B01_Repo(Scene):
    def construct(self):
        self.add(planned_tag())
        back, front = REPO.open_box(0, 0, 0, 3.2, 3.2, 1.5)
        self.add(back, front)
        self.add(T("repo", 40).move_to([-3.6, -2.4, 0]))
        data = REPO.box(0.3, 1.8, 0.05, 1.1, 1.1, 0.7, DARK_TOP, DARK_L, DARK_R); data.set_z_index(1)
        tool = REPO.page(1.8, 1.8, 0.05); tool.set_z_index(1)
        tests = VGroup(*[REPO.page(1.8, 0.3, 0.05 + 0.12 * i) for i in range(3)]); tests.set_z_index(1)
        log = REPO.page(0.3, 0.3, 0.05); log.set_z_index(1)
        cue(self, "A synthetic", 1.1); drop(self, data)
        self.play(FadeIn(T("dataset", 40).move_to([3.9, 0.9, 0])), run_time=0.4)
        cue(self, "The question tool", 0.7); drop(self, tool)
        cue(self, "A test set", 1.1); drop(self, tests)
        self.play(FadeIn(T("test set", 40).move_to([3.9, -0.6, 0])), run_time=0.4)
        cue(self, "And an evaluation log", 0.7); drop(self, log)
        finish(self)


class B02_Dashboard(Scene):
    def construct(self):
        self.add(planned_tag())
        dash = panel(2.0, 0.5, 5.4, 3.6)
        self.add(dash)
        heights = [1.0, 1.7, 1.3, 2.3]
        bars = VGroup(*[Rectangle(width=0.7, height=h, fill_color=[BAR1, BAR2][i % 2], fill_opacity=1, stroke_width=0)
                        .move_to([0.35 + i * 1.1, -1.0 + h / 2, 0]) for i, h in enumerate(heights)])
        go(self, "Tableau dashboard", 1.0, LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2))
        self.play(FadeIn(T("dashboard", 40).move_to([2.0, -1.8, 0])), run_time=0.4)
        q = sheet(-5.6, 0.5)
        self.add(q)
        go(self, "A new question", 0.6, q.animate.move_to([-1.6, 0.5, 0]))
        self.play(q.animate.move_to([-3.9, 0.5, 0]), run_time=0.5, rate_func=rate_functions.ease_out_bounce)
        self.play(FadeIn(T("new question", 40).move_to([-3.9, -0.9, 0])), run_time=0.4)
        finish(self)


class B03_Scored(Scene):
    def construct(self):
        self.add(planned_tag())
        chat = panel(-3.8, 0.6, 3.6, 2.6)
        p1 = pill(-4.4, 0.6, 2.0, 0.4, fill=BAR3)
        p2 = pill(-3.2, -0.1, 2.0, 0.4, fill=BAR2)
        self.add(chat, p1, p2, T("chat", 40).move_to([-3.8, -1.3, 0]))
        q = sheet(-3.8, 0.4, 1.0, 1.3)
        q.set_z_index(-1)
        self.add(q)
        go(self, "It writes a query", 0.8, q.animate.move_to([-0.6, 0.4, 0]))
        posts = VGroup(Rectangle(width=0.35, height=2.6, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.4, 0.4, 0]),
                       Rectangle(width=0.35, height=2.6, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([3.0, 0.4, 0]),
                       Rectangle(width=1.95, height=0.35, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([2.2, 1.85, 0]))
        go(self, "no fixed test set", 0.6, FadeIn(posts))
        self.play(FadeIn(T("test set", 40).move_to([2.2, -1.4, 0])), run_time=0.4)
        go(self, "every answer is run", 1.0, q.animate.move_to([4.7, 0.4, 0]))
        self.play(Create(check(4.8, 1.8, s=0.3)), run_time=0.5)
        finish(self)


class B04_SixtySeconds(Scene):
    def construct(self):
        self.add(planned_tag())
        win = panel(2.4, 0.9, 5.4, 2.8)
        rows = VGroup(*[Rectangle(width=4.4, height=0.32, fill_color=[BAR2, BAR3][i % 2], fill_opacity=1, stroke_width=0)
                        .move_to([2.4, 0.9 - i * 0.5, 0]) for i in range(4)])
        go(self, "first sixty seconds", 0.6, FadeIn(T("60 s", 120).move_to([-3.6, 0.6, 0]), shift=UP * 0.2))
        go(self, "open the README", 0.6, FadeIn(win), FadeIn(rows))
        self.play(FadeIn(T("README", 40).move_to([2.4, 2.75, 0])), run_time=0.4)
        strip = Rectangle(width=5.4, height=0.8, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([2.4, -1.6, 0])
        prompt = Line([0.0, -1.6, 0], [2.0, -1.6, 0], color=GHOST, stroke_width=6)
        go(self, "run one command", 0.6, FadeIn(strip, shift=UP * 0.3), Create(prompt))
        self.play(Create(check(5.75, -1.4, s=0.28)), run_time=0.5)
        finish(self)


class B05_Proves(Scene):
    def construct(self):
        self.add(planned_tag())
        xs = [-3.8, 0.0, 3.8]
        cards = VGroup(*[sheet(x, 0.9, 2.0, 2.4, n=4) for x in xs])
        names = ["contract", "verification", "evaluation"]
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cards], lag_ratio=0.2), run_time=1.0)
        self.play(*[FadeIn(T(nm, 36).move_to([x, -0.75, 0])) for nm, x in zip(names, xs)], run_time=0.5)
        for phrase, x in zip(["a prompt contract", "verification against", "a repeatable evaluation"], xs):
            go(self, phrase, 0.4, GrowFromCenter(Dot([x + 0.7, 1.85, 0], radius=0.11, color=TERRA)))
        logp = sheet(0.0, -2.2, 4.0, 0.9, n=1)
        go(self, "The evidence", 0.7, FadeIn(logp, shift=UP * 0.4))
        finish(self)


class B06_ReadOnly(Scene):
    def construct(self):
        self.add(planned_tag())
        stack, lights = database(Iso(0.0, -1.4, 0.8))
        self.add(stack, lights)
        w_arrow = Arrow([-4.6, 0.3, 0], [-1.6, 0.3, 0], color=INK, stroke_width=8, buff=0)
        go(self, "It will not change", 0.6, GrowArrow(w_arrow))
        cross = VGroup(Line([-3.4, -0.1, 0], [-2.6, 0.7, 0], color=INK, stroke_width=9),
                       Line([-3.4, 0.7, 0], [-2.6, -0.1, 0], color=INK, stroke_width=9))
        self.play(Create(cross), FadeIn(T("write", 40).move_to([-3.1, -0.75, 0])), run_time=0.5)
        r_arrow = Arrow([1.6, 0.3, 0], [4.6, 0.3, 0], color=INK, stroke_width=8, buff=0)
        go(self, "read-only queries", 0.6, GrowArrow(r_arrow))
        self.play(Create(check(5.3, 0.4, s=0.3)), FadeIn(T("read", 40).move_to([3.1, -0.75, 0])), run_time=0.5)
        go(self, "no real company data", 0.5, *[l.animate.set_color(TERRA) for l in lights])
        finish(self)


class B07_Baseline(Scene):
    def construct(self):
        self.add(planned_tag())
        xs = [-5.4 + 1.2 * i for i in range(10)]
        pages = VGroup(*[sheet(x, 0.2, 0.8, 1.0, n=2) for x in xs])
        go(self, "ten questions", 1.0, LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.08))
        self.play(FadeIn(T("ten questions", 40).move_to([0.0, -1.2, 0])), run_time=0.4)
        scan = Line([-6.0, -0.5, 0], [-6.0, 0.9, 0], color=TERRA, stroke_width=8)
        self.add(scan)
        go(self, "through the checker", 1.4, scan.animate.move_to([6.0, 0.2, 0]), rate_func=linear)
        self.remove(scan)
        go(self, "prints a score table", 1.0,
           LaggedStart(*[Create(check(x, 1.35, s=0.24)) for x in xs], lag_ratio=0.08))
        self.play(FadeIn(T("baseline", 40).move_to([0.0, -2.1, 0])), run_time=0.4)
        finish(self)


class B08_Ratio(Scene):
    def construct(self):
        self.add(planned_tag())
        left = Rectangle(width=1.4, height=2.2, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([-1.8, -1.6 + 1.1, 0])
        right = Rectangle(width=1.4, height=3.2, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.4, -1.6 + 1.6, 0])
        go(self, "ROAS is a ratio", 0.9, GrowFromEdge(left, DOWN), GrowFromEdge(right, DOWN))
        self.play(FadeIn(T("row average", 40).move_to([-1.8, -2.25, 0])),
                  FadeIn(T("total ÷ total", 40).move_to([1.4, -2.25, 0])), run_time=0.5)
        go(self, "My fix", 0.5, Create(check(1.4, 2.25, s=0.32)))
        tp = sheet(4.6, 0.3, 1.2, 1.5)
        go(self, "add ratio questions", 0.7, FadeIn(tp, shift=LEFT * 0.8))
        finish(self)


class B09_HaveNew(Scene):
    def construct(self):
        self.add(planned_tag())
        L = Iso(-3.6, -1.9, 0.7)
        have = VGroup(L.box(0, 0, 0, 2.6, 2.6, 1.6), L.tape(0, 0, 1.6, 2.6, 2.6))
        go(self, "I already have", 0.8, FadeIn(have, shift=DOWN * 0.4))
        self.play(FadeIn(T("have", 40).move_to([-3.6, -2.6, 0])), run_time=0.4)
        R = Iso(3.0, -1.9, 0.7)
        back, front = R.open_box(0, 0, 0, 2.6, 2.6, 1.4)
        go(self, "New to me", 0.5, FadeIn(back), FadeIn(front))
        self.play(FadeIn(T("new", 40).move_to([3.0, -2.6, 0])), run_time=0.4)
        for i, phrase in enumerate(["calling Claude", "writing prompt contracts", "evaluation harness"]):
            pg = R.page(0.4 + 0.5 * i, 0.5 + 0.4 * i, 0.05 + 0.1 * i)
            pg.set_z_index(1)
            cue(self, phrase, 0.6)
            drop(self, pg, 0.6)
        finish(self)


class B10_TodayWill(Scene):
    def construct(self):
        self.add(planned_tag())
        L = Iso(-4.0, -1.5, 0.6)
        today = VGroup(L.box(0, 0, 0, 1.6, 1.6, 1.2), L.box(2.0, -0.4, 0, 1.6, 1.6, 1.2))
        go(self, "What exists today", 0.8, FadeIn(today, shift=DOWN * 0.3))
        self.play(FadeIn(T("today", 40).move_to([-3.6, -2.5, 0])), run_time=0.4)
        R = Iso(2.0, -1.8, 0.5)
        will = VGroup(*[R.box(x, y, 0, 1.6, 1.6, 1.2, top=STAGE, left=STAGE, right=STAGE, sw=3).set_stroke(DIM)
                        for x, y in [(0, 0), (2.2, 0), (0, 2.2), (2.2, 2.2)]])
        go(self, "will exist", 1.2, LaggedStart(*[Create(b) for b in will], lag_ratio=0.25))
        self.play(FadeIn(T("will exist", 40).move_to([3.4, -2.5, 0])), run_time=0.4)
        finish(self)


class BOUT_Title(Scene):
    def construct(self):
        title = T("CheckedSQL: A Pitch", 72).move_to([0, 1.3, 0])
        name = T("Siddhesh Nikam · @nikam0420", 40).move_to([0, 0.1, 0])
        self.add(title, name)
        S = Iso(0.0, -2.6, 0.5)
        box = VGroup(S.box(-0.9, -0.9, 0, 1.8, 1.8, 1.1), S.tape(-0.9, -0.9, 1.1, 1.8, 1.8, drop=0.25))
        box.shift(UP * 3.0); self.add(box)
        self.play(box.animate.shift(DOWN * 3.0), run_time=0.8, rate_func=rate_functions.ease_out_bounce)
        finish(self)
