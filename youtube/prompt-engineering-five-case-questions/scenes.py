"""
Manim scenes for show-tell-what-is-a-case-exam (show-tell skill). One drawn isometric illustration per beat, labels only, Liam explains.
B06 is not drawn: it plays the real public practice case on CCPlainShell (law 10). The ISO KIT and pacing helpers are pasted from
brutalist.art/skills/make/show-tell/templates/iso_kit.py (not imported: Gate A copies only scenes.py); no person icon anywhere.
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
    """No animation straddles the clip midpoint (attached to every beat class at the bottom of this file)."""
    def play(self, *anims, **kw):
        if not all(isinstance(a, Wait) for a in anims):
            kw["run_time"] = guard(self, float(kw.get("run_time", 1.0)))
        return Scene.play(self, *anims, **kw)


def guard(self, rt):
    tgt = _TARGET.get(type(self).__name__.split("_")[0], 0)
    if not tgt:
        return rt
    mid, t0 = tgt / 2.0, _elapsed(self)
    M = 0.22
    if t0 < mid + M and t0 + rt > mid - M:
        room = mid - M - t0
        if room >= 0.6 * rt and room > 0.25:
            return room
        Scene.wait(self, max(0.02, mid + M - t0))
    return rt


_SLACK = {}
_END = 0.15


def done(self):
    bid = type(self).__name__.split("_")[0]
    t = _elapsed(self)
    tgt = _TARGET.get(bid, 0)
    print(f"[pace] {bid} content={t:.2f}s target={tgt:.2f}s" + ("  OVER" if t > tgt - 0.1 else ""))
    if tgt:
        self.wait(max(0.05, tgt - t - _END - _SLACK.get(bid, 0.0)))
    else:
        self.wait(2.0)


# ═════════════════════════════ the film: what is a case exam ═════════════════════════════
# Cast, kept for the whole film: a dark AGENT block (one lamp on its top), white report SHEETS with grey lines, a kraft TRAY
# (the stakeholder), a dark LOG server, ink checks and crosses, and one terracotta RING (the scan) that marks the thing under test.
DEEP = "#9C8462"            # deep kraft (grey 129): connectors and boundaries never read as type


def P3(c):
    return np.array([c[0], c[1], 0.0])


def rig_at(cx, cy, s, w, d):
    return Iso(cx - (w - d) * C30 * s / 2.0, cy - (w + d) * 0.5 * s / 2.0, s)


def lbl(s, x, y, size=42):
    return T(s, size).move_to([x, y, 0]).set_z_index(6)


def cross(x, y, s=0.22, w=9):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w)).set_z_index(6)


def tick(x, y, s=0.22):
    return check(x, y, s).set_z_index(6)


def ring(x, y, w=2.0, h=0.5):
    return Ellipse(width=w, height=h, stroke_color=TERRA, stroke_width=6, fill_opacity=0).move_to([x, y, 0]).set_z_index(7)


def mark(sh, i):
    return Dot([sh.cx - sh.w / 2 + 0.16, sh.ys[i], 0], radius=0.13, color=TERRA).set_z_index(7)


def sheet(cx, cy, w=2.0, h=2.6, n=3):
    pg = paper(cx, cy, w, h)
    ys = [cy + h / 2 - 0.6 - i * 0.5 for i in range(n)]
    ls = VGroup(*[Line([cx - w / 2 + 0.3, y, 0], [cx + w / 2 - 0.3 - (0.6 if i == n - 1 else 0), y, 0], color=BAR2, stroke_width=5)
                  for i, y in enumerate(ys)])
    g = VGroup(pg, ls).set_z_index(2)
    g.ys, g.cx, g.cy, g.w, g.h = ys, cx, cy, w, h
    return g


def slip(cx, cy, w=1.7, h=0.75, n=2):
    return sheet(cx, cy, w, h, 0) if n == 0 else VGroup(
        paper(cx, cy, w, h),
        *[Line([cx - w / 2 + 0.25, cy + h / 2 - 0.25 - i * 0.28, 0], [cx + w / 2 - 0.25 - (0.5 if i == n - 1 else 0), cy + h / 2 - 0.25 - i * 0.28, 0],
               color=BAR2, stroke_width=4) for i in range(n)]).set_z_index(3)


def agent(cx, cy, s=0.85):
    iso = rig_at(cx, cy, s, 1.3, 1.3)
    blk = iso.mcp(0, 0, 0, 1.3, 1.3, 0.7).set_z_index(1)
    top = iso.p(0.65, 0.65, 0.7)
    lamp = Dot([top[0], top[1], 0], radius=0.09, color=GHOST).set_z_index(3)
    g = VGroup(blk, lamp)
    g.top, g.lamp, g.iso = top, lamp, iso
    return g


def lit(lamp):
    return Dot(lamp.get_center(), radius=0.09, color=TERRA).set_z_index(4)


def logsrv(cx, cy, s=0.8):
    iso = rig_at(cx, cy, s, 1.4, 1.4)
    stack, lights = iso.server(0, 0, 0, 1.4, 1.4, 0.42, 3)
    g = VGroup(stack, lights)
    g.lights, g.iso = lights, iso
    return g


def tray(cx, cy, s=0.8, w=1.8, d=1.3):
    iso = rig_at(cx, cy, s, w, d)
    back, front = iso.open_box(0, 0, 0, w, d, 0.5)
    g = VGroup(back, front)
    g.iso, g.back, g.front = iso, back, front
    return g


def wire(a, b, w=6):
    return Line(P3(a), P3(b), color=DEEP, stroke_width=w).set_z_index(0)


def fly(self, m, to, rt=0.7):
    self.play(m.animate.move_to(P3(to)), run_time=rt)


# ══════════════ B00: recall versus judge ══════════════
class B00_Judge(Scene):
    def construct(self):
        iso = rig_at(-3.7, -0.4, 0.9, 1.4, 1.8)
        stack = VGroup(*[iso.page(0, 0, 0.1 * i, 1.4, 1.8) for i in range(3)])
        t1 = lbl("recall", -3.7, -2.1)
        self.play(FadeIn(stack, shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(t1), run_time=0.4)
        until(self, "A case exam asks", lead=0.4)
        x = cross(-3.7, 0.2, 0.5, 12)
        self.play(Create(x), run_time=0.4)
        self.play(FadeOut(VGroup(stack, x), shift=LEFT * 1.5), run_time=0.6)
        until(self, "an AI agent has already", lead=0.3)
        ag = agent(2.3, -1.2)
        self.play(FadeIn(ag, shift=DOWN * 0.5), run_time=0.6)
        sh = sheet(2.3, 1.7)
        self.play(FadeIn(sh, shift=UP * 0.4), run_time=0.6)
        t2 = lbl("agent", 2.3, -2.3)
        self.play(FadeIn(t2), run_time=0.4)
        until(self, "decide whether", lead=0.2)
        self.play(Create(ring(2.3, sh.ys[1], 1.9, 0.5)), run_time=0.5)
        self.play(FadeOut(t1), FadeIn(lbl("judge", -1.6, 1.7, 56)), run_time=0.4)
        done(self)


def pencil(x, y, ang=0.6, s=1.0):
    body = Rectangle(width=1.5 * s, height=0.2 * s, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4)
    tip = Polygon([0.75 * s, 0.1 * s, 0], [0.75 * s, -0.1 * s, 0], [1.0 * s, 0, 0], fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    g = VGroup(body, tip).rotate(ang).move_to([x, y, 0]).set_z_index(6)
    return g


# ══════════════ B00P: the exam is on paper ══════════════


# ══════════════ B01: the scenario ══════════════
class B01_Scenario(Scene):
    def construct(self):
        sc = sheet(-4.2, 0.3, 2.2, 2.9, 4)
        self.play(FadeIn(sc, shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("scenario", -4.2, -1.7)), run_time=0.4)
        until(self, "stakeholder", lead=0.3)
        tr = tray(0.2, -0.1)
        self.play(FadeIn(tr, shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("stakeholder", 0.2, -1.5)), run_time=0.4)
        until(self, "a goal", lead=0.3)
        r = Circle(radius=0.8, color=INK, stroke_width=5).move_to([4.3, 0.3, 0]).set_z_index(2)
        d = Dot([4.3, 0.3, 0], radius=0.18, color=TERRA).set_z_index(3)
        self.play(Create(r), run_time=0.6)
        self.play(FadeIn(d, scale=0.3), run_time=0.4)
        self.play(FadeIn(lbl("goal", 4.3, -1.1)), run_time=0.4)
        done(self)


# ══════════════ B02: the instruction ══════════════
class B02_Instruction(Scene):
    def construct(self):
        sc = sheet(-4.3, 0.4, 2.2, 2.9, 4)
        ag = agent(3.4, -0.9)
        self.add(sc)
        self.play(FadeIn(ag, shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("agent", 3.4, -2.1)), run_time=0.4)
        until(self, "the instruction", lead=0.3)
        sl = slip(-2.4, 1.0)
        self.play(FadeIn(sl, shift=RIGHT * 0.3), run_time=0.4)
        self.play(FadeIn(lbl("instruction", 0.0, -2.3)), run_time=0.4)
        until(self, "sent to the agent", lead=0.3)
        self.play(sl.animate.move_to(P3((3.4, 0.35))), run_time=0.9)
        self.play(FadeOut(sl, scale=0.4), FadeIn(lit(ag.lamp)), run_time=0.4)
        done(self)


# ══════════════ B03: the output ══════════════
class B03_Output(Scene):
    def construct(self):
        ag = agent(-1.0, -1.2)
        self.add(ag)
        self.play(FadeIn(lbl("agent", -1.0, -2.3)), run_time=0.4)
        until(self, "agent's output", lead=0.2)
        sh = sheet(-1.0, 1.75, 2.2, 2.6, 3)
        self.play(FadeIn(sh, shift=UP * 0.5), FadeIn(lit(ag.lamp)), run_time=0.7)
        until(self, "confident", lead=0.2)
        tk = tick(sh.cx + 0.6, sh.cy - 0.95, 0.25)
        self.play(Create(tk), run_time=0.4)
        until(self, "one planted flaw", lead=0.3)
        self.play(FadeIn(mark(sh, 1), scale=0.3), run_time=0.4)
        self.play(FadeIn(lbl("planted flaw", 2.7, sh.ys[1], 48)), run_time=0.4)
        done(self)


# ══════════════ B04: four probes ══════════════
class B04_Probes(Scene):
    def construct(self):
        xs = [-4.8, -2.4, 0, 2.4, 4.8]
        words = ["defect", "term", "check", "fix", "plain"]
        keys = ["First", "Second", "Third", "Fourth", "Fifth"]
        for i in range(5):
            until(self, keys[i], lead=0.4)
            s = sheet(xs[i], 0.5, 1.7, 2.6, 3)
            self.play(FadeIn(s, shift=DOWN * 0.4), run_time=0.5)
            self.play(FadeIn(lbl(words[i], xs[i], -1.5)), run_time=0.35)
        done(self)


# ══════════════ B05: the design firm ══════════════


# ══════════════ B07: the fabricated record ══════════════


# ══════════════ B08: one check ══════════════


# ══════════════ B09: the correction ══════════════


# ══════════════ B10: two plain sentences ══════════════


# ══════════════ B11 / B12: the scoring column (ten units) ══════════════
UNIT = 0.4
GAP = 0.06
ROWS = [("defect  3", 3, BAR1), ("exact term  2", 2, BAR2), ("evidence  2", 2, BAR1), ("fix  2", 2, BAR2), ("scope  1", 1, BAR1)]


def col_iso():
    return Iso(-2.6, -3.0, 0.8)


def col_block(iso, z0, units, c):
    top = {BAR1: BAR2, BAR2: BAR3}[c]
    return iso.box(0, 0, z0, 1.6, 1.6, units * UNIT, top, c, "#7A7E85" if c == BAR1 else BAR1, sw=4)


class B11_Scored(Scene):
    def construct(self):
        iso = col_iso()
        z = 0.0
        keys = ["Finding a real defect", "exact term", "Asking for evidence", "Giving a fix", "keeping to scope"]
        self.add(Dot([0, 0, 0], radius=0.001, color=STAGE))
        for (name, u, c), k in zip(ROWS, keys):
            until(self, k, lead=0.5)
            b = col_block(iso, z, u, c)
            mid = iso.p(0.8, 0.0, z + u * UNIT / 2)
            self.play(FadeIn(b, shift=DOWN * 0.6), run_time=0.45)
            self.play(FadeIn(lbl(name, 1.6, mid[1])), run_time=0.3)
            z += u * UNIT + GAP
        done(self)


class B12_Cap(Scene):
    def construct(self):
        iso = col_iso()
        z = 0.0
        blocks = []
        for name, u, c in ROWS:
            b = col_block(iso, z, u, c)
            blocks.append((b, z, u))
            z += u * UNIT + GAP
        self.add(*[b for b, _, _ in blocks])
        self.play(FadeIn(lbl("ten points", 3.4, 1.2)), run_time=0.4)
        until(self, "If you name no real defect", lead=0.2)
        z5 = 3 * UNIT + 2 * GAP + 2 * UNIT + GAP     # top of the second row's top (3+2 = five units)
        slab = iso.box(-0.3, -0.3, z5 + 0.5, 2.2, 2.2, 0.16, BOX_TOP, BOX_L, BOX_R).set_z_index(5)
        self.play(FadeIn(slab, shift=DOWN * 1.2), run_time=0.7)
        self.play(slab.animate.shift(DOWN * iso.v(0, 0, 0.5)[1]), run_time=0.3)
        upper = VGroup(*[b for b, zz, u in blocks[2:]])
        self.play(FadeOut(upper, shift=UP * 0.3), run_time=0.5)
        self.play(FadeIn(lbl("cap  5", 3.4, iso.p(0, 0, z5)[1], 56)), run_time=0.4)
        done(self)


# ══════════════ B13: polish earns nothing ══════════════
class B13_Checklist(Scene):
    def construct(self):
        pol = paper(-4.0, 0.5, 2.4, 3.0)
        scr = scribbles_on(pol, n=5, inset=0.35, gap=0.45)
        self.play(FadeIn(VGroup(pol, scr), shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("polish", -4.0, -1.5)), run_time=0.4)
        self.play(FadeIn(lbl("0", -4.0, -2.4, 72)), run_time=0.4)
        until(self, "checklist", lead=0.5)
        ck = paper(2.8, 0.5, 3.2, 3.4)
        boxes = VGroup(*[Square(0.34, color=INK, stroke_width=4).move_to([1.7, 1.6 - i * 0.62, 0]) for i in range(5)])
        ln = VGroup(*[Line([2.2, 1.6 - i * 0.62, 0], [4.0, 1.6 - i * 0.62, 0], color=BAR2, stroke_width=5) for i in range(5)])
        self.play(FadeIn(VGroup(ck, boxes, ln), shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("checklist", 2.8, -1.9)), run_time=0.4)
        until(self, "right name", lead=1.4)
        for i in range(5):
            self.play(Create(tick(1.7, 1.6 - i * 0.62, 0.15)), run_time=0.2)
        done(self)


# ══════════════ B14: claim versus evidence ══════════════
class B14_Evidence(Scene):
    def construct(self):
        cl = sheet(-4.3, 0.4, 2.0, 2.6, 3)
        self.play(FadeIn(cl, shift=DOWN * 0.4), run_time=0.5)
        self.play(FadeIn(lbl("claim", -4.3, -1.5)), run_time=0.4)
        until(self, "what is the evidence", lead=0.4)
        self.play(FadeIn(mark(cl, 0), scale=0.3), run_time=0.4)
        self.play(FadeIn(lbl("evidence?", -4.3, 2.4)), run_time=0.4)
        until(self, "Evidence is something", lead=0.3)
        ob = sheet(-0.9, 0.4, 2.0, 2.6, 3)
        sv = logsrv(4.4, -0.8)
        self.play(FadeIn(ob, shift=DOWN * 0.4), FadeIn(sv, shift=DOWN * 0.4), run_time=0.6)
        self.play(FadeIn(lbl("observed", -0.9, -1.5)), run_time=0.4)
        self.play(Create(wire((0.2, ob.ys[1]), (3.1, -0.1))), run_time=0.7)
        for lt in sv.lights:
            self.play(FadeIn(Dot(lt.get_center(), radius=0.07, color=TERRA).set_z_index(5)), run_time=0.15)
        done(self)


# ══════════════ B15: name it with the exact term ══════════════


# ══════════════ B16: observable proof ══════════════
class B16_Proof(Scene):
    def construct(self):
        ag = agent(-3.6, -1.3)
        sh = sheet(-3.6, 1.6, 2.0, 2.3, 3)
        self.add(ag)
        self.play(FadeIn(sh, shift=UP * 0.3), run_time=0.5)
        until(self, "observable proof", lead=0.2)
        sv = logsrv(4.0, -0.9)
        self.play(FadeIn(sv, shift=DOWN * 0.4), run_time=0.5)
        self.play(FadeIn(lbl("the log", 4.0, -2.3)), run_time=0.4)
        self.play(Create(wire((-2.6, sh.ys[1]), (2.8, -0.1))), run_time=0.8)
        for lt in sv.lights:
            self.play(FadeIn(Dot(lt.get_center(), radius=0.07, color=TERRA).set_z_index(5)), run_time=0.15)
        until(self, "double-check it", lead=0.6)
        arc = ArcBetweenPoints(P3((-4.7, 0.9)), P3((-4.7, -0.7)), angle=2.4, color=INK, stroke_width=5).set_z_index(5)
        self.play(Create(arc), run_time=0.5)
        self.play(Create(cross(-5.5, 0.1, 0.28, 10)), run_time=0.3)
        self.play(FadeIn(lbl("double-check", -4.3, -2.9)), run_time=0.4)
        done(self)


# ══════════════ B17: a precise fix, inside scope ══════════════
class B17_Scope(Scene):
    def construct(self):
        ag = agent(-3.0, -1.1)
        cs = sheet(-3.0, 1.5, 2.0, 2.2, 3)
        self.add(ag)
        self.play(FadeIn(cs, shift=UP * 0.3), run_time=0.5)
        until(self, "Give a fix", lead=0.0)
        sl = slip(-5.5, -2.7, 1.5, 0.9, 3)
        self.play(FadeIn(sl, shift=UP * 0.3), run_time=0.4)
        self.play(sl.animate.move_to(P3((-3.0, -0.35))), run_time=0.8)
        self.play(FadeOut(sl, scale=0.4), FadeIn(lit(ag.lamp)), run_time=0.4)
        until(self, "keep to scope", lead=0.4)
        bd = RoundedRectangle(width=6.2, height=5.2, corner_radius=0.25, stroke_color=DEEP, stroke_width=6, fill_opacity=0).move_to([-3.0, 0.35, 0]).set_z_index(0)
        self.play(Create(bd), run_time=0.7)
        self.play(FadeIn(lbl("scope", -3.0, -2.85)), run_time=0.4)
        out = sheet(3.6, 0.5, 2.0, 2.6, 3)
        self.play(FadeIn(out, shift=DOWN * 0.3), run_time=0.5)
        self.play(Create(cross(3.6, 0.5, 0.45, 12)), run_time=0.3)
        self.play(FadeIn(lbl("not asked", 3.6, -1.6)), run_time=0.4)
        done(self)


# ══════════════ B18: do it cold, key after ══════════════


# ══════════════ B19: the glossary ══════════════


# ══════════════ B20: the one-line evidence request ══════════════


# ══════════════ B21: the exam folder ══════════════


# ══════════════ B22: fluent but wrong ══════════════


# ══════════════ B23: only trivial tests ══════════════


# ══════════════ B24: outside the request ══════════════


# ══════════════ B25: add more tests ══════════════


for _cls in (B00_Judge, B00P_Paper, B01_Scenario, B02_Instruction, B03_Output, B04_Probes, B05_Firm, B07_Fabricated, B08_Check, B09_Fix,
             B10_Plain, B11_Scored, B12_Cap, B13_Checklist, B14_Evidence, B15_Name, B16_Proof, B17_Scope, B18_Cold,
             B19_Glossary, B20_OneLine, B21_Folder, B22_Fluent, B23_Tests, B24_Outside, B25_MoreTests):
    _cls.play = ST.play
