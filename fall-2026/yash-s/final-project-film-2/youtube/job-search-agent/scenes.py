"""scenes.py — job-search-agent (INFO 7375 Final Project Film). The show-tell iso_kit is pasted below
(copied from my October pitch film), then the film's own cast and one Scene per beat."""
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


# ═════════════════════════════ job-search-agent: shared cast ═════════════════════════════
# The cast, kept for the whole film: company job boards (kraft boxes with terracotta tape),
# posting cards (kraft, grey edge, handwriting lines), rule pages (white paper), checks and
# crosses in ink, terracotta only for "new" and "relevant" dots, the scan line and REFUSED.
# Every body beat carries an on-screen tag: constructed sketch, drawn from my screenshots,
# or recorded output (a reconstruction of evidence/terminal-2026-11-23.txt).

SKETCH = "constructed sketch"
SHOTS = "drawn from my 2026-11-23 screenshots"
REC = "recorded output, 2026-11-23 · a reconstruction"
PLAN = "constructed sketch · plan, not built yet"
MONO = "Menlo"


def _tgt(self):
    return _TARGET.get(type(self).__name__.split("_")[0], 0)


def P(self, *anims, rt=0.6, rf=smooth, add=()):
    """self.play, held off the clip midpoint (GATE T and Gate V sample there)."""
    tgt = _tgt(self)
    if tgt:
        a, b = tgt / 2 - 0.3, tgt / 2 + 0.3
        now = _elapsed(self)
        if now < b and now + rt > a:
            self.wait(b - now + 0.02)
    if add:
        self.add(*add)
    self.play(*anims, run_time=rt, rate_func=rf)


def tag(text):
    t = T(text, 32)
    t.move_to([-6.1 + t.width / 2, -3.05, 0])
    return t


def L(text, x, y, size=40, color=INK):
    return T(text, size, color).move_to([x, y, 0])


def M(text, size=26, color=INK):
    return Text(text, font=MONO, color=color, font_size=size)


def cross(x, y, s=0.3, w=8, color=INK):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def arrow(x0, y0, x1, y1, color=INK, w=6, head=0.22):
    """A straight arrow: a line plus a filled triangle head (no Arrow class: Gate A's stub)."""
    d = np.array([x1 - x0, y1 - y0, 0.0]); n = d / (np.linalg.norm(d) or 1.0); q = np.array([-n[1], n[0], 0.0])
    tip = np.array([x1, y1, 0.0]); base = tip - n * head
    return VGroup(Line([x0, y0, 0], base, color=color, stroke_width=w),
                  Polygon(tip, base + q * head * 0.6, base - q * head * 0.6, fill_color=color, fill_opacity=1, stroke_width=0))


def window(x, y, w, h):
    """A pale app window: card face, ink outline, grey title band."""
    shadow = RoundedRectangle(width=w, height=h, corner_radius=0.14, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
    body = RoundedRectangle(width=w, height=h, corner_radius=0.14, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    band = Rectangle(width=w - 0.1, height=0.42, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x, y + h / 2 - 0.27, 0])
    return VGroup(shadow, body, band)


def row(x, y, w, h=0.34, fill=BAR3):
    return Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


def lbar(x0, y, w, h=0.42, fill=BAR1):
    """A bar anchored at its left edge x0."""
    return Rectangle(width=max(w, 0.02), height=h, fill_color=fill, fill_opacity=1, stroke_width=0).move_to([x0 + max(w, 0.02) / 2, y, 0])


def chip(x, y, text, size=32, fill=CARD, w=None):
    t = T(text, size)
    p = pill(x, y, w or (t.width + 0.6), h=0.62, fill=fill)
    p.set_stroke(color=DIM, width=3)
    t.move_to([x, y, 0])
    return VGroup(p, t)


def chip_row(texts, cx, y, size=32, gap=0.35):
    """Pills placed side by side from their measured widths, centred on cx, never overlapping."""
    chips = [chip(0, y, t, size) for t in texts]
    total = sum(c.width for c in chips) + gap * (len(chips) - 1)
    x = cx - total / 2
    for c in chips:
        c.move_to([x + c.width / 2, y, 0]); x += c.width + gap
    return chips


def card(x, y, w=1.8, h=1.1, tilt=0.0):
    """A posting card: kraft paper, grey edge, two handwriting lines (grey edge, per GATE T §8.6b)."""
    pg = paper(x, y, w, h, tilt, fill=BOX_TOP)
    pg.sheet.set_stroke(color=DIM, width=4)
    return VGroup(pg, scribbles_on(pg, n=2, inset=0.28, gap=0.34))


def outline_box(iso, x0, y0, z0, w, d, h):
    """An outline-only box: planned or in progress, not finished (stage fill, grey edges)."""
    x1, y1, z1 = x0 + w, y0 + d, z0 + h
    return VGroup(
        iso.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], STAGE, stroke=DIM, sw=4),
        iso.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], STAGE, stroke=DIM, sw=4),
        iso.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], STAGE, stroke=DIM, sw=4))


def board(cx, base_y, s=0.8):
    """A company job board: a sealed kraft box with terracotta tape, its front corner at (cx, base_y)."""
    iso = Iso(cx, base_y, s)
    return VGroup(iso.box(0, 0, 0, 1.4, 1.4, 0.9), iso.tape(0, 0, 0.9, 1.4, 1.4, drop=0.25, t=0.16))


def terminal(lines_spec, x0=-5.4, y_top=2.05, gap=0.5):
    """Recorded-output lines, left-aligned from x0. lines_spec: [(text, color)]. Returns a list of Text."""
    out = []
    for i, (s, c) in enumerate(lines_spec):
        t = M(s, 22, c)
        if t.width > 10.7:          # keep every recorded line inside the window and the title-safe area
            t.scale_to_fit_width(10.7)
        t.move_to([x0 + t.width / 2, y_top - i * gap, 0])
        out.append(t)
    return out


def ring(x, y, r, frac, color=TERRA, w=14):
    track = Circle(radius=r, stroke_color=GHOST, stroke_width=w).move_to([x, y, 0])
    arc = Arc(radius=r, start_angle=PI / 2, angle=-TAU * frac, stroke_color=color, stroke_width=w, arc_center=[x, y, 0])
    return track, arc


# ═════════════════════════════ scenes ═════════════════════════════

# ── Part 1: executive summary ──

class B01_Watch(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        xs = [-4.2, 0.0, 4.2]
        boxes = [board(x, -1.55) for x in xs]
        names = [L(n, x, -2.25, 36) for n, x in zip(["Databricks", "Anthropic", "OpenAI"], xs)]
        until(self, "watches company job boards")
        P(self, LaggedStart(*[FadeIn(b, shift=DOWN * 0.6) for b in boxes], lag_ratio=0.2), rt=0.9)
        P(self, LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.2), rt=0.5)
        until(self, "only tells you")
        scan = Line([-5.9, -1.2, 0], [-5.9, 2.6, 0], color=TERRA, stroke_width=8)
        P(self, FadeIn(scan), rt=0.2)
        P(self, scan.animate.shift(RIGHT * 11.8), rt=1.4)
        P(self, FadeOut(scan), rt=0.2)
        cards = []
        for x in xs:
            for dx in (-0.6, 0.6):
                cards.append(card(x + dx, 1.55, 1.05, 0.85))
        P(self, LaggedStart(*[FadeIn(c, shift=UP * 0.5) for c in cards], lag_ratio=0.12), rt=1.0)
        until(self, "new since")
        dots = VGroup(*[Dot([c.get_center()[0] + 0.34, c.get_center()[1] + 0.3, 0], radius=0.09, color=TERRA)
                        for i, c in enumerate(cards) if i in (1, 2, 5)])
        P(self, LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.25), rt=0.7)
        P(self, FadeIn(L("new", 4.8, 2.55, 36, TERRA)), rt=0.3)
        finish(self)


class B02_Rules(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        c = card(-5.3, 0.9, 1.8, 1.1)
        self.add(c)
        page = paper(-0.9, 0.35, 4.0, 4.2)
        rules = ["role", "location", "experience", "skills"]
        labels = [L(r, -2.0, 1.75 - i * 0.85, 38) for i, r in enumerate(rules)]
        labels = [l.move_to([-2.4 + l.width / 2, l.get_center()[1], 0]) for l in labels]
        until(self, "says why")
        P(self, FadeIn(page), *[FadeIn(l) for l in labels], rt=0.6)
        P(self, c.animate.move_to([-3.85, 2.55, 0]).scale(0.7), rt=0.6)
        until(self, "fits the candidate")
        marks = [check(0.35, 1.8, s=0.22, w=8), check(0.35, 0.95, s=0.22, w=8), cross(0.45, 0.1, s=0.22), check(0.35, -0.75, s=0.22, w=8)]
        for m in marks:
            P(self, Create(m), rt=0.35)
        trays = VGroup(RoundedRectangle(width=3.0, height=1.5, corner_radius=0.12, stroke_color=DIM, stroke_width=4, fill_opacity=0).move_to([4.6, 1.3, 0]),
                       RoundedRectangle(width=3.0, height=1.5, corner_radius=0.12, stroke_color=DIM, stroke_width=4, fill_opacity=0).move_to([4.6, -1.1, 0]))
        tl = VGroup(L("keep", 4.6, 2.35, 36), L("reject", 4.6, -0.05, 36))
        until(self, "or why it does not")
        P(self, FadeIn(trays), FadeIn(tl), rt=0.5)
        P(self, c.animate.move_to([4.6, -1.1, 0]), rt=0.7)
        until(self, "written rules")
        reason = chip(1.95, -2.3, "experience above 2 years", 30)
        P(self, FadeIn(reason, shift=UP * 0.3), rt=0.5)
        finish(self)


class B03_Person(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        sl = paper(-4.4, 1.0, 2.2, 2.7)
        lines = scribbles_on(sl, n=4, inset=0.3, gap=0.42)
        self.add(sl, lines, L("shortlist", -4.4, -0.65, 36))
        until(self, "it stops")
        arr = arrow(-3.0, 1.0, -0.4, 1.0)
        P(self, Create(arr), rt=0.5)
        gate = window(2.9, 1.0, 6.0, 2.7)
        gate[1].set_stroke(color=DIM, width=4)   # grey edge: an ink frame round labels fuses into one 'text' blob (GATE T §8.6b)
        opts = VGroup(*chip_row(["approve", "refuse", "defer"], 2.9, 0.65, 30))
        until(self, "a person makes the decision")
        P(self, FadeIn(gate), rt=0.4)
        P(self, FadeIn(L("a person decides", 2.9, 1.6, 36)), LaggedStart(*[FadeIn(o) for o in opts], lag_ratio=0.2), rt=0.7)
        acts = [chip(x, -1.75, t, 34) for x, t in zip([-3.6, 0.0, 3.6], ["apply", "email", "log in"])]
        P(self, LaggedStart(*[FadeIn(a, shift=UP * 0.3) for a in acts], lag_ratio=0.15), rt=0.6)
        for phrase, a in zip(["never applies", "never sends an email", "never logs in"], acts):
            until(self, phrase)
            cx, cy = a.get_center()[0], a.get_center()[1]
            P(self, Create(cross(cx + a.width / 2 + 0.45, cy, s=0.22, w=8)), rt=0.35)
        finish(self)


class B04_WhyCare(Scene):
    def construct(self):
        self.add(tag("numbers from my JS2 run, 2026-11-10"))
        self.add(L("Databricks: postings seen", -3.6, 2.4, 36))
        n = L("924", -3.6, 1.0, 110)
        dates = L("Oct 31", -3.6, -0.4, 36)
        self.add(n, dates)
        until(self, "change all the time")
        for v, d in [("950", "Nov 3"), ("980", "Nov 7"), ("1,004", "Nov 10")]:
            nn = L(v, -3.6, 1.0, 110); dd = L(d, -3.6, -0.4, 36)
            P(self, FadeOut(n), FadeIn(nn), FadeOut(dates), FadeIn(dd), rt=0.35)
            n, dates = nn, dd
        until(self, "eighty new postings")
        pile = VGroup(*[card(2.2 + (i % 4) * 0.55, -1.7 + (i // 4) * 0.42, 1.25, 0.8, tilt=0.06 * ((i * 7) % 5 - 2)) for i in range(12)])
        P(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.4) for c in pile], lag_ratio=0.08), rt=1.2)
        P(self, FadeIn(L("80 new", 3.0, 2.55, 48, TERRA)), rt=0.35)
        until(self, "by hand")
        lens = VGroup(Circle(radius=0.55, stroke_color=INK, stroke_width=7).move_to([0.6, 0.4, 0]),
                      Line([1.0, 0.0, 0], [1.5, -0.5, 0], color=INK, stroke_width=9))
        P(self, FadeIn(lens), rt=0.3)
        P(self, lens.animate.shift(RIGHT * 2.6 + DOWN * 0.6), rt=1.2)
        until(self, "easy to miss")
        P(self, FadeIn(L("?", 5.3, 0.9, 72)), FadeIn(L("?", 5.3, -1.7, 56)), rt=0.4)
        finish(self)


class B05_Persona(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        pg = paper(0.0, 0.3, 3.4, 4.2)
        name = L("Priya Nair", 0.0, 1.9, 48)
        body = scribble_block(-1.3, 1.05, 2.6, n=4, gap=0.45)
        until(self, "the candidate")
        P(self, FadeIn(VGroup(pg, name, body), shift=DOWN * 0.8), rt=0.7, rf=ease_in)
        stamp = VGroup(RoundedRectangle(width=3.9, height=1.2, corner_radius=0.1, stroke_color=TERRA, stroke_width=8, fill_opacity=0),
                       T("FICTIONAL", 54, TERRA)).move_to([4.0, -0.4, 0]).rotate(-0.18)
        until(self, "a fictional person")
        P(self, GrowFromCenter(stamp), rt=0.35)
        until(self, "real résumé")
        P(self, FadeIn(L("no real résumé is used", -3.9, -2.2, 36)), rt=0.4)
        finish(self)


# ── Part 2: introduction — what others have done ──

class B06_LinkedIn(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        win = window(0.4, 0.0, 10.4, 5.1)
        self.add(win, L("LinkedIn · ML engineer · Databricks · US", 0.4, 3.0, 34))
        ys = [1.35, 0.55, -0.25, -1.05, -1.85]
        until(self, "I searched")
        rows = [row(-0.3, y, 6.6, 0.42, BAR2) for y in ys]
        P(self, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.4) for r in rows], lag_ratio=0.15), rt=0.9)
        until(self, "more than ninety-nine")
        P(self, FadeIn(L("99+ results", 4.25, 1.35, 44)), rt=0.4)
        until(self, "staff-level")
        tags = [chip(3.95, y, "Staff", 30, fill=GHOST) for y in (0.55, -1.05, -1.85)]
        P(self, LaggedStart(*[FadeIn(t, shift=LEFT * 0.3) for t in tags], lag_ratio=0.2), rt=0.7)
        finish(self)


class B07_LinkedInMatch(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        track = RoundedRectangle(width=4.6, height=0.36, corner_radius=0.18, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-3.4, 1.6, 0])
        knob = Circle(radius=0.26, fill_color=INK, fill_opacity=1, stroke_width=0).move_to([-5.7, 1.6, 0])
        until(self, "medium match")
        P(self, FadeIn(track), FadeIn(knob), FadeIn(L("match", -3.4, 2.45, 36)), rt=0.4)
        P(self, knob.animate.move_to([-3.4, 1.6, 0]), rt=0.6)
        P(self, FadeIn(L("medium", -3.4, 0.95, 38)), rt=0.3)
        until(self, "my own profile")
        prof = paper(-3.4, -1.0, 2.4, 1.5)
        prof.sheet.set_stroke(color=DIM, width=4)   # grey edge: an ink frame round ink scribbles reads as stacked labels (GATE T §8.6b)
        P(self, FadeIn(prof, shift=UP * 0.4), FadeIn(scribbles_on(prof, n=2, inset=0.3, gap=0.4)), rt=0.5)
        P(self, FadeIn(L("my profile, not Priya's", -3.4, -2.2, 34)), rt=0.35)
        pc = card(3.3, 0.6, 4.4, 3.0)
        until(self, "first posting")
        P(self, FadeIn(pc, shift=LEFT * 0.5), rt=0.5)
        chips = chip_row(["Python", "MLflow"], 3.3, 0.15, 30)
        until(self, "like Python")
        P(self, LaggedStart(*[GrowFromCenter(c) for c in chips], lag_ratio=0.3), rt=0.6)
        until(self, "senior role")
        sen = VGroup(Rectangle(width=4.4, height=0.62, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0), T("senior role", 34, CARD)).move_to([3.3, -1.45, 0])
        P(self, FadeIn(sen, shift=DOWN * 0.3), rt=0.4)
        finish(self)


class B08_Jobright(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        self.add(L("Jobright · AI Engineer, Databricks", 0.0, 2.95, 36))
        track, arc = ring(-3.6, 0.1, 1.55, 0.57)
        until(self, "fifty-seven percent")
        P(self, Create(track), rt=0.3)
        P(self, Create(arc), rt=1.0)
        P(self, FadeIn(L("57%", -3.6, 0.25, 72)), FadeIn(L("fair match", -3.6, -0.55, 32)), rt=0.35)
        items = [("experience", 0.30, 1.0), ("skills", 0.40, 0.0), ("industry", 0.41, -1.0)]
        until(self, "split into experience")
        for name, f, y in items:
            P(self, FadeIn(L(name, 0.75, y, 34)), FadeIn(lbar(1.85, y, 3.1, 0.34, GHOST)), rt=0.25)
            P(self, GrowFromEdge(lbar(1.85, y, 3.1 * f, 0.34, BAR1), LEFT), FadeIn(L(f"{int(round(f * 100))}%", 5.55, y, 32)), rt=0.4)
        until(self, "how the fifty-seven")
        P(self, FadeIn(L("?", -1.05, 1.5, 96)), rt=0.4)
        finish(self)


class B09_JobrightSkills(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        chips = [chip(-4.3, 1.3, "PyTorch", 36), chip(-4.3, 0.1, "Scikit-learn", 36)]
        until(self, "marked PyTorch")
        P(self, LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in chips], lag_ratio=0.3), rt=0.6)
        ticks = [check(-2.25, 1.35, s=0.2, w=8), check(-1.85, 0.15, s=0.2, w=8)]
        P(self, LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), rt=0.5)
        P(self, FadeIn(L("“skills you have”", -4.3, 2.3, 32)), rt=0.3)
        res = paper(3.2, 0.7, 3.2, 3.4)
        until(self, "neither one")
        P(self, FadeIn(res), FadeIn(scribbles_on(res, n=5, inset=0.35, gap=0.5)), FadeIn(L("Priya's résumé", 3.2, 2.75, 34)), rt=0.5)
        P(self, Create(Line([-1.4, 0.7, 0], [1.4, 0.7, 0], color=DIM, stroke_width=4)), rt=0.4)
        P(self, FadeOut(ticks[0]), FadeOut(ticks[1]), Create(cross(-2.2, 1.3, s=0.2)), Create(cross(-1.8, 0.1, s=0.2)), rt=0.4)
        until(self, "experienced engineers")
        bar = VGroup(Rectangle(width=6.6, height=0.62, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0),
                     T("posting: for experienced engineers", 32, CARD)).move_to([-0.3, -1.6, 0])
        P(self, FadeIn(bar, shift=DOWN * 0.3), rt=0.4)
        until(self, "not relevant")
        P(self, FadeIn(L("my label: not relevant", -0.3, -2.45, 34)), rt=0.35)
        finish(self)


class B10_Claude(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        win = window(-2.4, 0.1, 7.6, 4.8)
        self.add(win, L("Claude · Sonnet 5.5", -2.4, 2.95, 34))
        slot = RoundedRectangle(width=5.6, height=1.3, corner_radius=0.12, stroke_color=DIM, stroke_width=4, fill_opacity=0).move_to([-2.4, 0.9, 0])
        until(self, "did not invent a list")
        P(self, Create(slot), rt=0.5)
        P(self, FadeIn(L("no verified list", -2.4, 0.9, 38)), rt=0.35)
        c = card(-2.4, -1.05, 3.0, 1.2)
        until(self, "rejected the same")
        P(self, FadeIn(c, shift=UP * 0.3), FadeIn(L("AI Engineer, FDE", -2.4, -2.0, 32)), rt=0.45)
        P(self, Create(cross(-2.4, -1.05, s=0.35)), rt=0.35)
        track, arc = ring(4.7, -0.6, 0.85, 0.57, w=10)
        until(self, "Jobright scored")
        P(self, FadeIn(track), FadeIn(arc), FadeIn(L("57%", 4.7, -0.55, 44)), rt=0.4)
        P(self, Create(Line([-0.8, -1.05, 0], [3.8, -0.75, 0], color=TERRA, stroke_width=5)), rt=0.5)
        finish(self)


class B11_ClaudeLimits(Scene):
    def construct(self):
        self.add(tag(SHOTS))
        c = card(-3.8, 0.0, 2.6, 1.6)
        self.add(c)
        lamp = Circle(radius=0.42, fill_color=GHOST, fill_opacity=1, stroke_color=DIM, stroke_width=4).move_to([-3.8, 1.75, 0])
        until(self, "could not confirm")
        P(self, FadeIn(lamp), FadeIn(L("still open?", -3.8, 2.6, 34)), rt=0.4)
        P(self, Indicate(lamp, color=GHOST, scale_factor=1.15), rt=0.5)
        gb = board(3.3, -1.0)
        until(self, "live Greenhouse job board")
        P(self, FadeIn(gb, shift=DOWN * 0.5), FadeIn(L("Greenhouse board", 3.3, -1.75, 34)), rt=0.5)
        P(self, Create(arrow(-2.3, 0.0, 1.9, 0.0)), rt=0.5)
        until(self, "read its own memory")
        bub = VGroup(Circle(radius=0.9, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([1.4, 2.2, 0]),
                     Circle(radius=0.16, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([0.3, 1.2, 0]))
        P(self, GrowFromCenter(bub), FadeIn(L("memory", 1.4, 2.2, 28)), rt=0.4)
        until(self, "not fully clean")
        P(self, FadeIn(L("test not fully isolated", 4.2, 2.2, 32, DIM)), rt=0.35)
        finish(self)


class B12_WhyMine(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        cols = [(-1.2, "LinkedIn"), (0.9, "Jobright"), (2.9, "Claude"), (5.0, "my agent")]
        rows_ = [(1.3, "reads the board directly"), (0.2, "saves the raw data"), (-0.9, "a written rule per decision")]
        hdr = [L(n, x, 2.4, 34) for x, n in cols]
        rl = [L(t, -4.15, y, 30) for y, t in rows_]
        until(self, "not meant to replace")
        P(self, LaggedStart(*[FadeIn(h) for h in hdr], lag_ratio=0.15), rt=0.6)
        P(self, LaggedStart(*[FadeIn(r) for r in rl], lag_ratio=0.15), rt=0.6)
        dashes = VGroup(*[L("–", x, y, 40, DIM) for x, _ in cols[:3] for y, _ in rows_])
        P(self, FadeIn(dashes), rt=0.3)
        for (y, _), phrase in zip(rows_, ["reads the company's job board", "saves the raw data", "written rule"]):
            until(self, phrase)
            P(self, Create(check(4.95, y + 0.05, s=0.24, w=9)), rt=0.35)
        P(self, FadeIn(L("– = not seen in my test", 2.9, -2.0, 30, DIM)), rt=0.3)
        finish(self)


class B13_Change(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        iso = Iso(-4.6, -0.6, 0.7)
        stack = VGroup(*[iso.page(0, 0, i * 0.14, w=2.0, d=2.4) for i in range(3)])
        until(self, "In October")
        P(self, FadeIn(stack, shift=DOWN * 0.5), FadeIn(L("October pitch:", -4.2, -1.55, 34)), FadeIn(L("docs Q&A tool", -4.2, -2.15, 34)), rt=0.6)
        until(self, "that tool was not")
        P(self, Create(cross(-4.2, 0.9, s=0.6, w=10)), FadeIn(L("not agentic", -4.2, 2.55, 36)), rt=0.45)
        xs = [1.9, 3.6, 5.3]
        bxs = [board(x, -0.6, s=0.6) for x in xs]
        until(self, "changed my project")
        P(self, LaggedStart(*[FadeIn(b, shift=DOWN * 0.4) for b in bxs], lag_ratio=0.2), rt=0.7)
        loop = Arc(radius=2.2, start_angle=PI * 0.95, angle=-PI * 1.9, stroke_color=TERRA, stroke_width=8, arc_center=[3.6, 0.4, 0])
        P(self, Create(loop), rt=0.8)
        P(self, FadeIn(L("job-search agent", 3.6, -2.15, 36)), rt=0.35)
        finish(self)


# ── Part 3: methods ──

class B14_Built(Scene):
    def construct(self):
        self.add(tag("constructed sketch · the tests are real"))
        j1 = Iso(-4.4, -1.0, 0.8).box(0, 0, 0, 1.4, 1.4, 0.9)
        j2 = Iso(-0.4, -1.0, 0.8).box(0, 0, 0, 1.4, 1.4, 1.5)
        j3 = outline_box(Iso(3.8, -1.0, 0.8), 0, 0, 0, 1.4, 1.4, 1.2)
        until(self, "In JS1")
        P(self, FadeIn(j1, shift=DOWN * 0.5), FadeIn(L("JS1 · one board", -4.4, -1.7, 34)), FadeIn(L("77 tests", -4.4, -2.3, 32)), rt=0.6)
        until(self, "In JS2")
        P(self, FadeIn(j2, shift=DOWN * 0.5), FadeIn(L("JS2 · one loop, four boards", -0.4, -1.7, 34)), FadeIn(L("65 tests", -0.4, -2.3, 32)), rt=0.6)
        until(self, "permission policy")
        posts = VGroup(*[Line([x, 2.0, 0], [x, 2.9, 0], color=INK, stroke_width=8) for x in (-1.3, 0.5)])
        rope = Line([-1.3, 2.75, 0], [0.5, 2.75, 0], color=TERRA, stroke_width=6)
        P(self, FadeIn(posts), Create(rope), rt=0.5)
        P(self, FadeIn(L("two hosts only", 2.0, 2.45, 32)), rt=0.3)
        until(self, "is in progress")
        P(self, Create(j3), FadeIn(L("JS3 · filter, in progress", 3.8, -1.7, 34)), FadeIn(L("63 tests", 3.8, -2.3, 32)), rt=0.7)
        finish(self)


class B15_Filter(Scene):
    def construct(self):
        self.add(tag("numbers from my JS3 run, 2026-11-18"))
        x0, W = -5.6, 11.2
        full = lbar(x0, 1.2, W, 0.7, BAR3)
        until(self, "two thousand four hundred eighteen")
        P(self, GrowFromEdge(full, LEFT), rt=0.7)
        P(self, FadeIn(L("2,418 saved postings", 0.0, 2.1, 38)), rt=0.3)
        rej_w = W * 2355 / 2418
        rej = lbar(x0, 1.2, rej_w, 0.7, BAR1)
        rev = lbar(x0 + rej_w, 1.2, W - rej_w, 0.7, TERRA)
        until(self, "It rejected")
        P(self, GrowFromEdge(rej, LEFT), rt=0.7)
        P(self, FadeIn(L("2,355 rejected", -2.4, 0.4, 36)), rt=0.3)
        until(self, "sixty-three in a review queue")
        P(self, FadeIn(rev), FadeIn(L("63 to review", 4.2, 0.4, 36, TERRA)), rt=0.4)
        until(self, "Most were rejected")
        strips = [chip(-2.2, -0.75, "experience above 2 years · 1,482", 30),
                  chip(-2.2, -1.55, "senior word in the title · 1,297", 30),
                  chip(-2.2, -2.35, "outside the US · 756", 30)]
        P(self, LaggedStart(*[FadeIn(s, shift=DOWN * 0.3) for s in strips], lag_ratio=0.25), rt=0.8)
        P(self, FadeIn(L("one posting can have several reasons", 3.3, -1.55, 28, DIM)), rt=0.3)
        finish(self)


def _term_scene(self, spec, cues, title):
    """Type the recorded lines `spec` [(text, color)] into a terminal window; `cues` maps a line index
    to the narration phrase it waits for."""
    self.add(tag(REC))
    win = window(0.0, 0.0, 12.2, 5.2)
    self.add(win, L(title, 0.0, 3.0, 30))
    lines = terminal(spec, y_top=1.75)
    cur = Rectangle(width=0.16, height=0.36, fill_color=TERRA, fill_opacity=1, stroke_width=0).move_to([-5.45, 1.75, 0])
    self.add(cur)
    for i, t in enumerate(lines):
        if i in cues:
            until(self, cues[i])
        c = t.get_center()
        right = min(c[0] + t.width / 2, 5.5)
        P(self, FadeIn(t, shift=RIGHT * 0.15), cur.animate.move_to([min(right + 0.2, 5.6), c[1], 0]), rt=0.3)
        if i in cues:   # underline the line the narration is about (a drawn shape, not just text)
            ul = Line([-5.6, c[1] - 0.16, 0], [-5.6, c[1] + 0.16, 0], color=TERRA, stroke_width=8)
            P(self, Create(ul), rt=0.3)
    nxt = lines[-1].get_center()
    P(self, cur.animate.move_to([-5.45, nxt[1] - 0.5, 0]), rt=0.3)
    finish(self)


class B16_Tests(Scene):
    def construct(self):
        spec = [("$ python3 -m unittest discover -s tests", DIM),
                ("Ran 65 tests in 0.197s", INK),
                ("OK", INK),
                ("$ python3 wrong_versions.py", DIM),
                ("  WV1 failed board reported as zero new: CAUGHT by 7 failing test(s)", INK),
                ("  WV2 string-prefix folder check: CAUGHT by 1 failing test(s)", INK),
                ("  WV3 retries not counted: CAUGHT by 2 failing test(s)", INK),
                ("RESULT: every wrong version was caught", TERRA)]
        _term_scene(self, spec, {0: "recorded today", 1: "sixty-five tests pass", 3: "plant three bugs", 7: "catch every one"},
                    "js2-loop-tools-diff · Python 3.9.6")


class B17_Check(Scene):
    def construct(self):
        spec = [("$ python3 independent_check.py runs/run-2026-11-10T025118Z", DIM),
                ("board                status    now   result", DIM),
                ("Databricks           ok        915   consistent", INK),
                ("Anthropic            ok        675   consistent", INK),
                ("OpenAI               ok        825   consistent", INK),
                ("Deliberate failure   failed    -     not checked here", INK),
                ("Nothing flagged.", TERRA)]
        _term_scene(self, spec, {0: "A separate checker", 2: "Databricks", 3: "Anthropic", 4: "OpenAI", 6: "Nothing flagged"},
                    "js2-loop-tools-diff · columns trimmed")


class B18_Gate(Scene):
    def construct(self):
        spec = [("$ python3 agent.py --reset-state greenhouse-anthropic \\", DIM),
                ("      --state-dir \"$T/state\"", DIM),
                ("REFUSED: refusing to reset $T/state/greenhouse-anthropic.state.json:", TERRA),
                ("         needs explicit approval (--approve-reset)", TERRA),
                ("$ python3 agent.py --reset-state greenhouse-anthropic \\", DIM),
                ("      --state-dir \"$T/state\" --approve-reset", DIM),
                ("reset: $T/state/greenhouse-anthropic.state.json", INK)]
        _term_scene(self, spec, {0: "human gate", 2: "is refused", 4: "With my approval", 6: "it is allowed"},
                    "js2-loop-tools-diff · $T is a temporary folder")


class B19_Plan(Scene):
    def construct(self):
        self.add(tag(PLAN))
        xs = [-5.1, -3.08, -1.06, 0.96, 2.98, 5.0]
        names = [("JS1", "watch"), ("JS2", "loop"), ("JS3", "filter"), ("JS4 · Dec 1", "plan + memory"), ("JS5 · Dec 13", "approval"), ("Dec 20", "final test")]
        line = Line([xs[0], 1.6, 0], [xs[-1], 1.6, 0], color=GHOST, stroke_width=6)
        nodes = []
        for i, x in enumerate(xs):
            if i < 2:
                nodes.append(Circle(radius=0.32, fill_color=INK, fill_opacity=1, stroke_width=0).move_to([x, 1.6, 0]))
            elif i == 2:
                nodes.append(Circle(radius=0.32, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([x, 1.6, 0]))
            else:
                nodes.append(Circle(radius=0.32, fill_color=STAGE, fill_opacity=1, stroke_color=DIM, stroke_width=5).move_to([x, 1.6, 0]))
        until(self, "Here is the plan")
        P(self, Create(line), rt=0.4)
        P(self, LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.12), rt=0.8)
        P(self, LaggedStart(*[FadeIn(VGroup(L(a, x, 0.9, 26), L(b, x, 0.4, 24, DIM))) for x, (a, b) in zip(xs, names)], lag_ratio=0.1), rt=0.8)
        until(self, "In JS4")
        P(self, Indicate(nodes[3], color=TERRA), rt=0.5)
        sl = paper(-2.6, -1.55, 2.0, 1.3)
        sl.sheet.set_stroke(color=DIM, width=4)     # grey edge (GATE T §8.6b), as in my pitch film
        appr = chip(1.6, -1.55, "approved", 32)
        until(self, "approval gate")
        P(self, Indicate(nodes[4], color=TERRA), rt=0.4)
        P(self, FadeIn(sl), FadeIn(scribbles_on(sl, n=2, inset=0.28, gap=0.36)), FadeIn(appr), rt=0.4)
        link = Line([-1.55, -1.55, 0], [0.6, -1.55, 0], color=INK, stroke_width=6)
        P(self, Create(link), FadeIn(L("tied to this exact list", 0.55, -2.45, 30)), rt=0.4)
        until(self, "if one posting changes")
        P(self, Create(scribble(-3.3, -1.3, 1.4, color=TERRA, sw=6)), rt=0.35)
        P(self, FadeOut(link), Create(cross(-0.45, -1.55, s=0.25)), rt=0.35)
        until(self, "for the final project")
        P(self, Indicate(nodes[5], color=TERRA), rt=0.5)
        finish(self)


class B20_Resources(Scene):
    def construct(self):
        self.add(tag(SKETCH))
        bxs = [board(-5.4, y, s=0.5) for y in (1.0, -0.3, -1.6)]
        until(self, "public job-board APIs")
        P(self, LaggedStart(*[FadeIn(b, shift=RIGHT * 0.3) for b in bxs], lag_ratio=0.2), rt=0.6)
        P(self, FadeIn(L("public job-board APIs", -4.2, 2.55, 32)), rt=0.3)
        lap = VGroup(RoundedRectangle(width=6.0, height=2.6, corner_radius=0.12, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([1.0, 0.8, 0]),
                     Polygon([-2.0, -0.7, 0], [4.0, -0.7, 0], [4.5, -1.1, 0], [-2.5, -1.1, 0], fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4))
        feeds = VGroup(*[Line([-4.5, y + 0.4, 0], [-2.0, 0.8, 0], color=DIM, stroke_width=4) for y in (1.0, -0.3, -1.6)])
        P(self, FadeIn(lap), Create(feeds), rt=0.6)
        until(self, "no paid API")
        coin = Circle(radius=0.6, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([5.5, 1.9, 0])
        P(self, FadeIn(coin, shift=LEFT * 0.4), FadeIn(L("paid API", 5.5, 0.95, 30)), rt=0.4)
        P(self, Create(cross(5.5, 1.9, s=0.45, w=9)), rt=0.35)
        until(self, "plain Python")
        P(self, FadeIn(L("Python, standard library", 1.0, 1.35, 32)), rt=0.35)
        until(self, "Claude Code")
        P(self, FadeIn(L("Claude Code, from my university", 1.0, 0.4, 30)), rt=0.35)
        until(self, "that I review")
        P(self, FadeIn(L("I review every change", 1.0, -1.8, 32)), rt=0.35)
        finish(self)


# ── Part 4: evaluation ──

class B21_HeldOut(Scene):
    def construct(self):
        self.add(tag(PLAN))
        deck = VGroup(*[card(0.0 + i * 0.06, 2.2 - i * 0.06, 1.6, 0.95) for i in range(6)])
        self.add(deck)
        dev = RoundedRectangle(width=4.4, height=2.0, corner_radius=0.12, stroke_color=DIM, stroke_width=4, fill_opacity=0).move_to([-3.6, -0.9, 0])
        held = Iso(2.4, -1.9, 0.75).box(0, 0, 0, 2.0, 2.0, 0.9)
        until(self, "set aside")
        P(self, FadeIn(dev), FadeIn(L("development", -3.6, 0.45, 34)), FadeIn(held), FadeIn(L("held-out", 3.9, 0.8, 34)), rt=0.5)
        targets = [(-4.8, -0.9), (-3.6, -0.9), (-2.4, -0.9), (-4.2, -1.3), (3.2, -1.0), (4.0, -0.9)]
        P(self, LaggedStart(*[deck[i].animate.move_to([x, y, 0]).scale(0.7) for i, (x, y) in enumerate(targets)], lag_ratio=0.1), rt=1.0)
        until(self, "label them myself")
        tape = Iso(2.4, -1.9, 0.75).tape(0, 0, 0.9, 2.0, 2.0, drop=0.3, t=0.18)
        P(self, FadeIn(tape), rt=0.3)
        until(self, "relevant")
        rel = VGroup(*[Dot([deck[i].get_center()[0] + 0.35, deck[i].get_center()[1] + 0.22, 0], radius=0.09, color=TERRA) for i in (1, 5)])
        P(self, LaggedStart(*[GrowFromCenter(d) for d in rel], lag_ratio=0.3), rt=0.5)
        until(self, "In JS1")
        note = chip(0.0, -2.4, "JS1: 25 of 25 labels were “not relevant”", 30, fill=GHOST)
        P(self, FadeIn(note, shift=UP * 0.3), rt=0.4)
        finish(self)


class B22_Failures(Scene):
    def construct(self):
        self.add(tag(PLAN))
        gx = [-4.3, 0.0, 4.3]
        gnames = ["relevant jobs missed", "wrong jobs kept", "decisions with a reason"]
        until(self, "I will measure")
        for x, n in zip(gx, gnames):
            tr = Arc(radius=0.9, start_angle=PI, angle=-PI, stroke_color=GHOST, stroke_width=12, arc_center=[x, 1.5, 0])
            P(self, Create(tr), FadeIn(L(n, x, 2.75, 30)), rt=0.3)
        until(self, "five failures on purpose")
        fx = [-5.2, -2.6, 0.0, 2.6, 5.2]
        fnames = ["no such board", "removed posting", "outside the US", "too much experience", "keywords only"]
        net = Line([-5.6, -2.6, 0], [5.6, -2.6, 0], color=DIM, stroke_width=5)
        P(self, Create(net), rt=0.4)
        pos = [(-4.3, -1.0), (0.0, -1.0), (4.3, -1.0), (-2.15, -2.05), (2.15, -2.05)]
        cards = [chip(x, y, n, 28) for (x, y), n in zip(pos, fnames)]
        for c, ph in zip(cards, ["a board that does not exist", "a removed posting", "outside the US", "too much experience", "only matches keywords"]):
            until(self, ph)
            P(self, FadeIn(c, shift=DOWN * 0.5), rt=0.3)
        P(self, LaggedStart(*[Create(check(c.get_center()[0] + c.width / 2 + 0.35, c.get_center()[1], s=0.18, w=7)) for c in cards], lag_ratio=0.12), rt=0.6)
        finish(self)


class B23_PassFail(Scene):
    def construct(self):
        self.add(tag(PLAN))
        good = ["no relevant job silently rejected", "every decision has a reason", "the recount agrees", "nothing shortlisted without my approval"]
        bad = ["a relevant job rejected", "without a reason", "an old approval accepted", "for a changed shortlist"]
        self.add(L("it worked if", -3.4, 2.55, 40), L("it did not work if", 3.6, 2.55, 40))
        cues = ["no relevant job", "every decision has a reason", "the recount agrees", "nothing reaches the shortlist"]
        for i, (g, ph) in enumerate(zip(good, cues)):
            until(self, ph)
            y = 1.55 - i * 0.95
            t = L(g, 0, y, 30); t.move_to([-5.35 + t.width / 2, y, 0])
            P(self, FadeIn(t), Create(check(-5.8, y + 0.05, s=0.18, w=7)), rt=0.35)
        until(self, "It did not work if")
        for i, ph in enumerate(["rejected without a reason", "an old approval"]):
            if i:
                until(self, ph)
            y = 1.55 - i * 1.6
            t1 = L(bad[2 * i], 0, y, 30); t1.move_to([1.2 + t1.width / 2, y, 0])
            t2 = L(bad[2 * i + 1], 0, y - 0.55, 30); t2.move_to([1.2 + t2.width / 2, y - 0.55, 0])
            P(self, FadeIn(t1), FadeIn(t2), Create(cross(0.75, y - 0.25, s=0.18, w=7)), rt=0.35)
        finish(self)


class BOUT_Outro(Scene):
    def construct(self):
        bxs = VGroup(*[board(x, 0.9, s=0.5) for x in (-1.6, 0.0, 1.6)])
        bxs.shift(UP * 3.0)
        self.add(bxs)
        P(self, bxs.animate.shift(DOWN * 3.0), rt=0.7, rf=ease_in)
        P(self, FadeIn(T("A Job-Search Agent You Can Check", 64).move_to([0, -0.5, 0])), rt=0.45)
        P(self, FadeIn(T("Final Project Film", 42).move_to([0, -1.35, 0])), rt=0.35)
        P(self, FadeIn(T("Yash Saraf", 40).move_to([0, -2.05, 0])), rt=0.35)
        until(self, "by Yash Saraf")
        P(self, GrowFromCenter(Dot([0, -2.7, 0], radius=0.1, color=TERRA)), rt=0.3)
        finish(self)
