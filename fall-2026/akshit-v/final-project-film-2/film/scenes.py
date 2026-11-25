"""
scenes.py — INFO 7375 Final Project Film, "SponsorScout" (Akshit Verma), v2 of the pitch film.

Built in the assignment's four parts (executive summary · introduction · methods · evaluation). Same
show-tell style and the same drawing kit as the pitch film (2026-10-14): the kit block below (ISO KIT,
pacing helpers, cast) is copied unchanged from that film's scenes.py, lines 19-331. New in v2: the part
chip (top right) and the P* scenes.

HONESTY: every body scene carries a corner tag ("constructed drawing" + ran <date> / proposed / real
numbers). The only numbers drawn are real ones: Assignment 1 run outputs, and
board-resolver/runs/live-2026-11-23 (FACTCHECK.md).
"""
from manim import *
import numpy as np
import json as _json, os as _os, re as _re

# ── font: EB Garamond ships with the toolkit (runtime/fonts/EB_Garamond, SIL OFL) but is not installed
#    system-wide on this machine; register the file so Pango can find it.
try:
    import manimpango as _mp
    for _base in (_os.environ.get("ART_HOME"), r"C:\Users\Akshit Verma\PromptEngr\brutalist.art"):
        _f = _base and _os.path.join(_base, "runtime", "fonts", "EB_Garamond", "static", "EBGaramond-Regular.ttf")
        if _f and _os.path.isfile(_f):
            _mp.register_font(_f)
            break
except Exception:
    pass

# ═════════════════════════════ ISO KIT (show-tell, pasted) ═════════════════════════════
STAGE = "#F2F0E9"; INK = "#3D3929"; TERRA = "#D97757"; DIM = "#8B8F96"; GHOST = "#D9D4C7"; CARD = "#FAF9F5"
BOX_TOP, BOX_L, BOX_R = "#F3E9D8", "#DCC9AA", "#C7AE86"
BOX_IN1, BOX_IN2, BOX_FLOOR = "#CDB894", "#BFA67E", "#B39A72"
DARK_TOP, DARK_L, DARK_R = "#3A3530", "#26221F", "#1E1B18"
PAGE_TOP, PAGE_L, PAGE_R = "#FFFFFF", "#ECE7DF", "#E2DCD2"
BAR1, BAR2, BAR3 = "#8B8F96", "#B4AFA6", "#D9D4C7"
DEEP_KRAFT = "#9C8462"
SERIF = "EB Garamond"
C30 = 0.8660254
config.background_color = STAGE


def T(s, size=36, color=INK):
    return Text(s, font=SERIF, color=color, font_size=size)


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
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        return VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], left, sw=sw),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], right, sw=sw),
            self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, sw=sw))

    def open_box(self, x0, y0, z0, w, d, h):
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


def ease_in(t):
    return t * t


def check(x, y, s=0.2, color=INK, w=7):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))
# ═════════════════════════════ end ISO KIT ═════════════════════════════


# ═════════════════════════════ pacing: the narration's own word clock ═════════════════════════════
_HERE = _os.path.dirname(_os.path.abspath(__file__))
try:
    _SHEET = _json.load(open(_os.path.join(_HERE, "beat_sheet.json"), encoding="utf-8"))
    _TARGET = {b["beat_id"]: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0) for b in _SHEET["beats"]}
    _NARR = {b["beat_id"]: b["narration_text"] for b in _SHEET["beats"]}
    _TAG = {b["beat_id"]: b.get("honesty_tag", "") for b in _SHEET["beats"]}
except Exception:
    _TARGET, _NARR, _TAG = {}, {}, {}
try:   # word-level timing written by align.py: {"fps": .., "beats": {BID: [{text, startFrame, endFrame}]}}
    _W = _json.load(open(_os.path.join(_HERE, "mp3", "words.json"), encoding="utf-8"))
    _WORDS = {k: [(_re.sub(r"[^a-z0-9]", "", w["text"].lower()), w["startFrame"] / _W["fps"]) for w in v]
              for k, v in _W["beats"].items()}
except Exception:
    _WORDS = {}

MID_MARGIN = 0.25   # GATE T and Gate V sample the clip midpoint: keep motion off it


def _bid(self):
    return type(self).__name__.split("_")[0]


def _elapsed(self):
    rt = getattr(getattr(self, "renderer", None), "time", None)
    return float(rt) if isinstance(rt, (int, float)) else 0.0


def at(self, phrase, lead=0.15):
    """Wait until `phrase` is spoken: its first word's start in words.json (exact), else its share of the text."""
    bid = _bid(self)
    toks = [t for t in (_re.sub(r"[^a-z0-9]", "", x.lower()) for x in phrase.split()) if t]
    words = _WORDS.get(bid)
    t0 = None
    if words and toks:
        texts = [w for w, _ in words]
        for i in range(len(texts) - len(toks) + 1):
            if texts[i:i + len(toks)] == toks:
                t0 = words[i][1]
                break
    if t0 is None:
        n, target = _NARR.get(bid, ""), _TARGET.get(bid, 0)
        if not n or not target or phrase not in n:
            return
        t0 = target * n.index(phrase) / len(n)
    gap = t0 - lead - _elapsed(self)
    if gap > 0.04:
        self.wait(gap)


def gplay(self, *anims, run_time=0.6, **kw):
    """play(), but never across the clip midpoint: wait past it first if the move would straddle it."""
    tgt = _TARGET.get(_bid(self), 0)
    if tgt:
        mid, t = tgt / 2, _elapsed(self)
        if t < mid + MID_MARGIN and t + run_time > mid - MID_MARGIN:
            self.wait(mid + MID_MARGIN - t)
    self.play(*anims, run_time=run_time, **kw)


def enter(self, *mobs, run_time=0.7):
    """The entrance build: everything rises in, staggered."""
    self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.3) for m in mobs], lag_ratio=0.12), run_time=run_time)


def finish(self, fade=0.4):
    """Hold, then fade the whole frame to the stage just before the beat ends: a dip-to-cream transition."""
    target = _TARGET.get(_bid(self), 0)
    if not target:
        self.wait(1.0)
        return
    t = _elapsed(self)
    start = target - fade - 0.12
    if start > t:
        self.wait(start - t)
    mobs = [m for m in self.mobjects]
    if mobs:
        self.play(*[FadeOut(m) for m in mobs], run_time=fade)
    rest = target - _elapsed(self) - 0.04
    if rest > 0.04:
        self.wait(rest)


def honesty_tag(self):
    """The corner tag, top-left inside SAFE, ink, size 32 (type floor). Added with the first frame."""
    s = _TAG.get(_bid(self)) or "constructed drawing"
    t = T(s, 32)
    t.move_to([-6.1 + t.width / 2, 3.25 - t.height / 2, 0])
    self.add(t)
    return t


def label(s, at_xy, size=36):
    t = T(s, size)
    t.move_to(np.array([at_xy[0], at_xy[1], 0], dtype=float))
    return t


def centre(m):
    return np.array(m.get_center(), dtype=float)


def arrow(a, b, dashed=False, color=INK, sw=5):
    a, b = np.array([a[0], a[1], 0], dtype=float), np.array([b[0], b[1], 0], dtype=float)
    if dashed:
        line = DashedLine(a, b, color=color, stroke_width=sw, dash_length=0.16)
    else:
        line = Line(a, b, color=color, stroke_width=sw)
    d = (b - a) / max(np.linalg.norm(b - a), 1e-6)
    n = np.array([-d[1], d[0], 0])
    head = Polygon(b, b - d * 0.26 + n * 0.13, b - d * 0.26 - n * 0.13, fill_color=color, fill_opacity=1, stroke_width=0)
    return VGroup(line, head)


def cross(x, y, s=0.22, color=INK, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def sheet(x, y, w=1.4, h=1.8, rows=4, fill=PAGE_TOP, line=GHOST):
    """A flat page facing the viewer: white face, ink edge, kraft offset shadow, ghost text rows."""
    sh = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.1, y - 0.1, 0])
    pg = Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    gap = h / (rows + 1)
    ln = VGroup(*[Line([x - w / 2 + 0.22, y + h / 2 - gap * (i + 1), 0], [x + w / 2 - 0.22 - (0.3 if i == rows - 1 else 0),
                       y + h / 2 - gap * (i + 1), 0], color=line, stroke_width=6) for i in range(rows)])
    g = VGroup(sh, pg, ln)
    g.rows_y = [y + h / 2 - gap * (i + 1) for i in range(rows)]
    return g


def terminal(x, y, w=1.9, h=1.3):
    """A dark terminal card: no glyphs, ghost command lines and a terracotta cursor block."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK,
                            stroke_width=4).move_to([x, y, 0])
    bar = Rectangle(width=w - 0.04, height=0.2, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x, y + h / 2 - 0.12, 0])
    l1 = Line([x - w / 2 + 0.25, y + 0.1, 0], [x + 0.3, y + 0.1, 0], color=BAR2, stroke_width=7)
    l2 = Line([x - w / 2 + 0.25, y - 0.22, 0], [x - 0.15, y - 0.22, 0], color=BAR2, stroke_width=7)
    cur = Rectangle(width=0.16, height=0.24, fill_color=TERRA, fill_opacity=1, stroke_width=0).move_to([x + 0.02, y - 0.22, 0])
    return VGroup(body, bar, l1, l2, cur)


# ── the film's cast, depth-correct ──
def crate(iso, x, y, z=0.0, w=1.2, d=1.2, h=0.9):
    """The film's company: a kraft crate, grey strap, one terracotta seal. z-index 1: between a tray's back (0)
    and front (2), and between a gate's back post (0) and front post (3)."""
    body = iso.box(x, y, z, w, d, h)
    ym = y + d / 2
    strap = iso.quad([(x, ym - 0.12, z + h), (x + w, ym - 0.12, z + h), (x + w, ym + 0.12, z + h), (x, ym + 0.12, z + h)],
                     BAR2, stroke=DEEP_KRAFT, sw=2)
    seal = Dot(iso.p(x + w / 2, ym, z + h), radius=0.08, color=TERRA)
    g = VGroup(body, strap, seal)
    g.set_z_index(1)
    return g


def iso_at(cx, cy, w, d, h, s=1.0):
    """An Iso whose box(0, 0, 0, w, d, h) is centred on screen point (cx, cy)."""
    return Iso(cx - (w - d) / 2 * C30 * s, cy - (w + d) / 2 * 0.5 * s - h / 2 * s, s)


def crate_at(cx, cy, w=1.2, h=0.9, s=1.0):
    return crate(iso_at(cx, cy, w, w, h, s), 0, 0, 0, w, w, h)


def tray_at(cx, cy, w=1.8, h=0.5, s=1.0):
    back, front = iso_at(cx, cy, w, w, h, s).open_box(0, 0, 0, w, w, h)
    return VGroup(back, front)


def dark_block(cx, cy, w=1.5, h=1.0, s=1.0):
    """A dark machine block (scorer / workflow / resolver) with one terracotta lamp."""
    iso = iso_at(cx, cy, w, w, h, s)
    g = iso.box(0, 0, 0, w, w, h, DARK_TOP, DARK_L, DARK_R)
    lamp = Dot(iso.p(w * 0.5, 0, h * 0.55), radius=0.09, color=TERRA)
    return VGroup(g, lamp)


def plinth(iso, x, y, w, d, t=0.28):
    """A dark slab under a pale object (Gate V contrast: a lone kraft object read 0.28 < 0.30)."""
    p = iso.box(x - 0.25, y - 0.25, -t, w + 0.5, d + 0.5, t, DARK_TOP, DARK_L, DARK_R)
    p.set_z_index(-1)
    return p


def gate(iso, x, y, h=1.8, span=1.75, pw=0.22):
    """A check gate across the belt, in depth order: back post z0 < (crate z1) < front post + bar z3 < lamp z4."""
    back = iso.box(x, y + span, 0, pw, pw, h, DARK_TOP, DARK_L, DARK_R); back.set_z_index(0)
    front = iso.box(x, y, 0, pw, pw, h, DARK_TOP, DARK_L, DARK_R); front.set_z_index(3)
    bar = iso.box(x, y, h, pw, span + pw, 0.2, DARK_TOP, DARK_L, DARK_R); bar.set_z_index(3)
    lamp = Circle(radius=0.15, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to(
        iso.p(x + pw / 2, y + span / 2 + pw / 2, h + 0.5))
    lamp.set_z_index(4)
    return VGroup(back, front, bar), lamp


def belt(iso, x0, y0, length, width=1.95):
    """A flat conveyor along +x: within 28 of the stage, deep-kraft edges, ghost centre dashes (which move)."""
    body = iso.quad([(x0, y0, 0), (x0 + length, y0, 0), (x0 + length, y0 + width, 0), (x0, y0 + width, 0)],
                    "#E6E1D5", stroke=DEEP_KRAFT, sw=3)
    body.set_z_index(-2)
    dashes = VGroup(*[Line(iso.p(x0 + i, y0 + width / 2, 0), iso.p(x0 + i + 0.5, y0 + width / 2, 0), color=GHOST, stroke_width=5)
                      for i in np.arange(0.3, length - 1.4, 1.0)])
    dashes.set_z_index(-1)
    return body, dashes


def ride(self, iso, crate_m, dashes, dx, run_time=0.8):
    """The crate rides the belt by dx while the belt's dashes run with it (then reset by one period, unseen)."""
    period = iso.v(1.0, 0, 0)
    gplay(self, crate_m.animate.shift(iso.v(dx, 0, 0)), dashes.animate.shift(period), run_time=run_time, rate_func=smooth)
    dashes.shift(-period)


def pulse(self, lamp, color=TERRA):
    ring = Circle(radius=0.2, stroke_color=color, stroke_width=5).move_to(centre(lamp))
    ring.set_z_index(5)
    gplay(self, lamp.animate.set_fill(color), Create(ring), run_time=0.3)
    self.play(ring.animate.scale(1.8).set_stroke(opacity=0), run_time=0.3)
    self.remove(ring)


def under(m, s, size=32, buff=0.22):
    """A label just below an object's lowest point (never overlapping it)."""
    return T(s, size).next_to(m, DOWN, buff=buff)


def beside(m, s, size=32, buff=0.25, side=RIGHT):
    return T(s, size).next_to(m, side, buff=buff)


def at_left(t, x):
    """Place a label so its left edge sits at x (keeps long labels inside SAFE)."""
    t.shift(RIGHT * (x - t.get_left()[0]))
    return t



# ═════════════════════════════ v2: the part chip (top right) ═════════════════════════════
try:
    _PART = {b["beat_id"]: b.get("part", "") for b in _SHEET["beats"]}
except Exception:
    _PART = {}


def part_chip(self):
    """Which of the assignment's four parts this beat belongs to: top right, ink, with a terracotta bar."""
    s = _PART.get(_bid(self))
    if not s:
        return None
    t = T(s, 32)
    t.move_to([6.1 - t.width / 2, 3.25 - t.height / 2, 0])
    bar = Rectangle(width=0.1, height=t.height + 0.08, fill_color=TERRA, fill_opacity=1, stroke_width=0)
    bar.next_to(t, LEFT, buff=0.15)
    self.add(t, bar)
    return VGroup(bar, t)


def pill_check(x, y, w=1.5):
    p = RoundedRectangle(width=w, height=0.6, corner_radius=0.3, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK,
                         stroke_width=4).move_to([x, y, 0])
    return VGroup(p, check(x - 0.3, y, 0.16))


# ═════════════════════════════ BOPEN — the name, and the four parts ═════════════════════════════
class BOPEN_Title(Scene):
    def construct(self):
        title = T("SponsorScout", 112).move_to([1.35, 1.35, 0])
        rule = Line([-1.6, 0.45, 0], [4.3, 0.45, 0], color=TERRA, stroke_width=6)
        c = crate_at(-5.0, 0.85, 1.05, 0.8, 1.0)
        lens = VGroup(Circle(radius=0.55, stroke_color=INK, stroke_width=8, fill_color=CARD, fill_opacity=0.35),
                      Line([0.39, -0.39, 0], [0.9, -0.9, 0], color=INK, stroke_width=12)).move_to([-4.35, 1.8, 0])
        glint = Dot([-4.6, 2.05, 0], radius=0.07, color=TERRA)
        self.play(FadeIn(c, shift=UP * 0.3), Write(title), run_time=0.9)
        self.play(FadeIn(lens, shift=DOWN * 0.3 + LEFT * 0.2), Create(rule), run_time=0.45)
        self.add(glint)
        at(self, "A final project film")
        by = T("a final project film by Akshit Verma", 44).move_to([1.35, -0.2, 0])
        gplay(self, FadeIn(by, shift=UP * 0.2), run_time=0.4)
        at(self, "in four parts", lead=0.3)
        cells = [("1 · executive summary", -1.9, -1.2), ("2 · introduction", 2.7, -1.2),
                 ("3 · methods", -1.9, -1.9), ("4 · evaluation", 2.7, -1.9)]
        labs = [at_left(T(s, 34).move_to([0, y, 0]), x) for s, x, y in cells]
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.15) for l in labs], lag_ratio=0.15), run_time=0.6)
        finish(self, fade=0.3)


# ═════════════════════════════ P1A — the problem ═════════════════════════════
class P1A_Problem(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        cx, cy = -4.9, 0.45
        face = Circle(radius=0.6, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([cx, cy, 0])
        hand = Line([cx, cy, 0], [cx, cy + 0.46, 0], color=TERRA, stroke_width=6)
        knob = Dot([cx, cy, 0], radius=0.07, color=INK)
        enter(self, VGroup(face, hand, knob), under(face, "a short clock", 32))
        self.play(Rotate(hand, -PI * 1.3, about_point=[cx, cy, 0]), run_time=1.0)
        at(self, "only some employers")
        XS = (-2.5, -0.7, 1.1)
        crates = [crate_at(x, 0.3, 0.85, 0.65, 1.0) for x in XS]
        gplay(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in crates], lag_ratio=0.15),
              FadeIn(T("sponsors", 34).move_to([-0.7, -0.95, 0])), run_time=0.6)
        at(self, "So we apply")
        pile = VGroup(*[sheet(4.9 + 0.1 * i, 0.45 - 0.08 * i, 0.95, 1.2, rows=3) for i in range(4)])   # 2026-11-23: moved right so "go nowhere" clears it
        gplay(self, FadeIn(pile, shift=LEFT * 0.3), FadeIn(T("applications", 32).move_to([5.05, -0.95, 0])),
              Create(arrow([4.2, 0.3], [2.1, 0.3])), run_time=0.6)
        at(self, "no entry-level")
        lamps = [Circle(radius=0.14, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, 1.45, 0])
                 for x in XS]
        gplay(self, *[FadeIn(l, scale=0.5) for l in lamps], FadeIn(T("nothing open today", 34).move_to([-0.7, 2.2, 0])),
              run_time=0.5)
        at(self, "and those applications")
        gplay(self, Create(cross(3.15, 0.3, 0.2)), FadeIn(T("go nowhere", 32).move_to([3.05, -0.35, 0])), run_time=0.4)
        finish(self)


# ═════════════════════════════ P1B — what SponsorScout does ═════════════════════════════
class P1B_Verdicts(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        ciso = iso_at(-4.75, 0.6, 1.0, 1.0, 0.8, 1.0)
        comp = VGroup(plinth(ciso, 0, 0, 1.0, 1.0), crate(ciso, 0, 0, 0, 1.0, 1.0, 0.8))
        enter(self, comp, under(comp, "a sponsor"))
        at(self, "SponsorScout tells")
        flow = dark_block(-1.85, 0.6, 1.2, 0.85, 1.0)
        gplay(self, FadeIn(flow, shift=UP * 0.3), FadeIn(under(flow, "SponsorScout")), Create(arrow([-3.6, 0.6], [-2.95, 0.6])),
              run_time=0.6)
        cells = [("apply", 1.95, "whether to apply"), ("network", 0.8, "network"),
                 ("check by hand", -0.35, "check by hand"), ("skip", -1.5, "or skip")]
        trays, labs = {}, {}
        for name, y, cue in cells:
            at(self, cue)
            tr = tray_at(1.35, y, 1.0, 0.4, 0.8)
            trays[name] = tr
            labs[name] = beside(tr, name, 32, buff=0.25)
            gplay(self, FadeIn(tr, shift=LEFT * 0.2), FadeIn(labs[name]),
                  Create(arrow([-0.7, 0.6], [0.45, y], sw=4)), run_time=0.35)
        at(self, "with the public record")
        # 2026-11-23 (Akshit's frame note): the arrow started at a fixed x and ran over "network";
        # it now starts just past the label's real right edge, and the record sheet moved right
        rec = sheet(5.45, 0.8, 0.7, 0.85, rows=2)
        x0 = labs["network"].get_right()[0] + 0.2
        gplay(self, FadeIn(rec, shift=LEFT * 0.3), Create(arrow([x0, 0.8], [rec.get_left()[0] - 0.15, 0.8], sw=4)), run_time=0.45)
        gplay(self, FadeIn(T("record", 32).next_to(rec, UP, buff=0.15)), run_time=0.3)
        at(self, "A strong sponsor")
        pick = crate_at(1.35, 0.98, 0.55, 0.4, 0.8)
        gplay(self, FadeIn(pick, shift=DOWN * 0.5), run_time=0.5)
        at(self, "isn't dropped")
        ring = Circle(radius=0.42, stroke_color=TERRA, stroke_width=6).move_to([1.35, 0.9, 0])
        gplay(self, Create(ring), run_time=0.4)
        finish(self)


# ═════════════════════════════ P1C — what it never does; why it matters to me ═════════════════════════════
class P1C_Why(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        wall = Rectangle(width=0.3, height=4.0, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([0.0, 0.25, 0])
        enter(self, wall)
        phase1 = VGroup(wall)
        icons = [
            ("apply", sheet(-3.0, 1.45, 0.75, 0.95, rows=2), "never applies"),
            ("email", VGroup(Rectangle(width=1.0, height=0.66, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4),
                             Line([-0.5, 0.33, 0], [0, -0.05, 0], color=INK, stroke_width=4),
                             Line([0, -0.05, 0], [0.5, 0.33, 0], color=INK, stroke_width=4)).move_to([-3.0, 0.25, 0]), "emails"),
            ("contact", VGroup(RoundedRectangle(width=1.0, height=0.66, corner_radius=0.2, fill_color=PAGE_TOP, fill_opacity=1,
                                                stroke_color=INK, stroke_width=4),
                               Polygon([-0.25, -0.33, 0], [-0.05, -0.33, 0], [-0.35, -0.55, 0], fill_color=INK, fill_opacity=1,
                                       stroke_width=0)).move_to([-3.0, -0.95, 0]), "or contacts anyone"),
        ]
        for name, m, cue in icons:
            at(self, cue)
            y = centre(m)[1]
            lb = T(name, 32).move_to([-5.2, y, 0])
            x = cross(-1.0, y, 0.18)
            gplay(self, FadeIn(m, shift=RIGHT * 1.0), FadeIn(lb), run_time=0.35)
            gplay(self, Create(x), run_time=0.2)
            phase1.add(m, lb, x)
        at(self, "The person decides")
        lst = sheet(3.4, 0.6, 1.4, 1.8, rows=4)
        lst_l = under(lst, "you decide", 34)
        gplay(self, FadeIn(lst, shift=LEFT * 0.4), FadeIn(lst_l), run_time=0.45)
        phase1.add(lst, lst_l)
        at(self, "I'm building it")
        pile = VGroup(*[sheet(-4.4 + 0.12 * i, 0.75 - 0.08 * i, 1.2, 1.5, rows=3) for i in range(8)])
        gplay(self, FadeOut(phase1, shift=UP * 0.2), FadeIn(pile, shift=UP * 0.2),
              FadeIn(T("100+ applications a day", 32).move_to([-3.95, -0.95, 0])), run_time=0.5)
        at(self, "a smarter strategy")
        short = sheet(3.2, 0.55, 1.3, 1.6, rows=3)
        gplay(self, Create(arrow([-2.4, 0.55], [2.2, 0.55])), FadeIn(short, shift=LEFT * 0.3),
              FadeIn(under(short, "a short list", 34)), run_time=0.55)
        finish(self)


# ═════════════════════════════ P2A — what already exists ═════════════════════════════
class P2A_Others(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        XS, Y, W, H = (-4.1, 0.0, 4.1), 0.3, 3.3, 2.5

        def panel(x):
            body = RoundedRectangle(width=W, height=H, corner_radius=0.18, fill_color=CARD, fill_opacity=1,
                                    stroke_color=INK, stroke_width=4).move_to([x, Y, 0])
            head = Rectangle(width=W - 0.04, height=0.36, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to(
                [x, Y + H / 2 - 0.2, 0])
            return VGroup(body, head)
        at(self, "My Visa Jobs")
        p1 = panel(XS[0])
        rows = VGroup(*[VGroup(Line([XS[0] - 1.35, Y + 0.55 - i * 0.42, 0], [XS[0] - 0.6, Y + 0.55 - i * 0.42, 0], color=BAR2, stroke_width=8),
                               Rectangle(width=wv, height=0.22, fill_color=BAR1, fill_opacity=1, stroke_width=0)
                               .move_to([XS[0] - 0.4 + wv / 2, Y + 0.55 - i * 0.42, 0]))
                        for i, wv in enumerate((1.4, 0.9, 1.7, 0.6))])
        gplay(self, FadeIn(p1, shift=UP * 0.2), FadeIn(T("MyVisaJobs", 36).next_to(p1, UP, buff=0.18)), run_time=0.4)
        gplay(self, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in rows], lag_ratio=0.15),
              FadeIn(under(p1, "past job counts", 32, buff=0.18)), run_time=0.5)
        at(self, "I looked at it")
        gplay(self, FadeIn(T("I looked · Oct 7", 28).move_to([XS[0], Y - H / 2 - 0.85, 0])), run_time=0.3)
        at(self, "H one B Grader")
        p2 = panel(XS[1])
        grade = T("A", 96).move_to([XS[1] - 0.6, Y - 0.15, 0])
        gbars = VGroup(*[Rectangle(width=wv, height=0.22, fill_color=BAR1 if i == 0 else BAR2, fill_opacity=1, stroke_width=0)
                         .move_to([XS[1] + 0.25 + wv / 2, Y + 0.3 - i * 0.42, 0]) for i, wv in enumerate((1.0, 0.7, 0.4))])
        gplay(self, FadeIn(p2, shift=UP * 0.2), FadeIn(T("H1BGrader", 36).next_to(p2, UP, buff=0.18)), run_time=0.4)
        gplay(self, FadeIn(grade, scale=1.2), FadeIn(gbars), FadeIn(under(p2, "grades past approvals", 32, buff=0.18)), run_time=0.45)
        at(self, "Interstride")
        p3 = panel(XS[2])
        hist = VGroup(*[Rectangle(width=0.26, height=hv, fill_color=BAR1, fill_opacity=1, stroke_width=0)
                        .move_to([XS[2] - 1.3 + i * 0.36, Y - 0.2 + hv / 2, 0]) for i, hv in enumerate((0.3, 0.55, 0.45, 0.8, 0.65))])
        chips = VGroup(*[RoundedRectangle(width=0.9, height=0.42, corner_radius=0.2, fill_color=PAGE_TOP, fill_opacity=1,
                                          stroke_color=INK, stroke_width=3).move_to([XS[2] + 1.0, Y + 0.5 - i * 0.6, 0]) for i in range(2)])
        gplay(self, FadeIn(p3, shift=UP * 0.2), FadeIn(T("Interstride", 36).next_to(p3, UP, buff=0.18)), run_time=0.4)
        gplay(self, LaggedStart(*[GrowFromEdge(h, DOWN) for h in hist], lag_ratio=0.12), run_time=0.5)
        at(self, "shows sponsorship history")
        gplay(self, FadeIn(chips), FadeIn(under(p3, "history · visa filter", 32, buff=0.18)), run_time=0.4)
        finish(self)


# ═════════════════════════════ P2B — the engine's scorer, and the gap ═════════════════════════════
class P2B_Gap(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        c = crate_at(-5.0, 0.1, 1.05, 0.8, 1.0)
        lamp = Circle(radius=0.15, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-5.0, 1.15, 0])
        sponsor = VGroup(c, lamp)
        enter(self, sponsor, under(c, "no open job", 32))
        at(self, "own scorer")
        eng = dark_block(-1.6, 1.45, 1.0, 0.7, 0.9)
        gplay(self, FadeIn(eng, shift=UP * 0.2), FadeIn(under(eng, "engine scorer", 30, buff=0.12)),
              Create(arrow([-4.25, 0.6], [-2.55, 1.35], dashed=True, color=BAR1)), run_time=0.5)
        at(self, "a zero")
        gplay(self, FadeIn(T("0", 72).move_to([0.25, 1.55, 0]), scale=1.4), run_time=0.35)
        at(self, "and skips it")
        skip = tray_at(3.5, 1.5, 1.3, 0.4, 0.9)
        gplay(self, Create(arrow([0.75, 1.5], [2.4, 1.5], dashed=True, color=BAR1)), FadeIn(skip, shift=LEFT * 0.2),
              FadeIn(beside(skip, "skip", 36)), run_time=0.45)
        at(self, "These tools show")
        ss = dark_block(-1.6, -0.75, 1.0, 0.7, 0.9)
        net = tray_at(3.5, -0.75, 1.5, 0.45, 0.95)
        gplay(self, FadeIn(ss, shift=UP * 0.2), FadeIn(under(ss, "SponsorScout", 30, buff=0.12)),
              Create(arrow([-4.25, -0.25], [-2.55, -0.7])), run_time=0.45)
        gplay(self, Create(arrow([-0.65, -0.75], [2.25, -0.75])), FadeIn(net, shift=LEFT * 0.2),
              FadeIn(under(net, "network list", 32, buff=0.12)), run_time=0.45)
        at(self, "None that I found")
        gplay(self, sponsor.animate.scale(0.7).move_to([3.5, -0.3, 0]), run_time=0.8)
        gplay(self, Create(check(5.35, -0.6, 0.24)), FadeIn(T("the gap", 36).move_to([5.45, 0.25, 0])), run_time=0.4)
        finish(self)


# ═════════════════════════════ P3A — the data ═════════════════════════════
class P3A_Data(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        at(self, "Sponsorship records")
        s1 = sheet(-4.4, 0.75, 1.4, 1.8, rows=4)
        l1 = under(s1, "H-1B sponsorship", 32)
        gplay(self, FadeIn(s1, shift=UP * 0.3), FadeIn(l1), FadeIn(under(l1, "80 Days to Stay", 28, buff=0.1)), run_time=0.5)
        at(self, "Recent funding")
        s2 = sheet(-0.9, 0.75, 1.4, 1.8, rows=4)
        l2 = under(s2, "Form D", 32)
        gplay(self, FadeIn(s2, shift=UP * 0.3), FadeIn(l2), FadeIn(under(l2, "SEC filings", 28, buff=0.1)), run_time=0.5)
        boards = []
        for nm, y in (("Greenhouse", 1.55), ("Lever", 0.45), ("Ashby", -0.65)):
            at(self, nm)
            pg = sheet(2.4, y, 0.8, 0.85, rows=2)
            gplay(self, FadeIn(pg, shift=LEFT * 0.2), FadeIn(beside(pg, nm, 32, buff=0.25)), run_time=0.3)
            boards.append(pg)
        gplay(self, FadeIn(T("public job boards", 30).move_to([3.3, 2.45, 0])), run_time=0.3)
        gplay(self, FadeIn(T("job seeker: fictional", 32).move_to([-2.6, -2.05, 0])), run_time=0.35)
        finish(self)


# ═════════════════════════════ P3B — three checks (ran 2026-10-03) ═════════════════════════════
class P3B_Checks(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        iso = Iso(-3.0, -2.35, 0.78)
        GX = (1.6, 4.0, 6.4)
        body, dashes = belt(iso, 0, 0, 8.4)
        gates = [gate(iso, x, -0.05) for x in GX]
        c = crate(iso, 0.15, 0.35, 0.02, 1.15, 1.15, 0.85)
        enter(self, VGroup(body, dashes), *[VGroup(g, l) for g, l in gates], c)
        names = ["sponsored? (H-1B)", "funded? (Form D)", "open today? (job board)"]
        cues = ["has it sponsored", "has it raised", "is an entry-level"]
        x_now = 0.15
        for gx, (g, lamp), name, cue in zip(GX, gates, names, cues):
            at(self, cue)
            x_to = gx - 0.05 - 0.45
            ride(self, iso, c, dashes, x_to - x_now, run_time=0.75)
            x_now = x_to
            pulse(self, lamp)
            post = iso.p(gx + 0.1, -0.05, 0)
            lb = at_left(T(name, 32).move_to([0, post[1] - 0.45, 0]), post[0] + 0.25)
            gplay(self, FadeIn(lb, shift=UP * 0.15), run_time=0.3)
        at(self, "set the verdict", lead=0.0)
        ride(self, iso, c, dashes, 1.3, run_time=0.6)
        at(self, "The prototype ran")
        gplay(self, FadeIn(at_left(T("123 sponsors · Oct 3", 36).move_to([0, 2.45, 0]), -6.05)), run_time=0.35)
        finish(self)


# ═════════════════════════════ P3C — the board resolver loop ═════════════════════════════
class P3C_Resolver(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        num = T("16 / 123", 64).move_to([-4.6, 1.85, 0])
        enter(self, num, under(num, "known boards", 32, buff=0.15))
        at(self, "I built a board resolver")
        res = dark_block(-4.2, -0.55, 1.2, 0.85, 1.0)
        gplay(self, FadeIn(res, shift=UP * 0.3), FadeIn(under(res, "board resolver", 32, buff=0.15)), run_time=0.45)
        steps = [("try a name", -1.25, 2.2, "tries names"), ("one request", 1.35, 2.2, "one request"),
                 ("save + fingerprint", 4.45, 3.0, "saves every raw")]
        Y = 0.95
        prev = None
        for s, x, w, cue in steps:
            at(self, cue)
            # Gate T 2026-11-23: an INK outline around the label read as one text blob over the label (bbox-overlap);
            # a filled kraft panel with no outline carries the same step
            box = RoundedRectangle(width=w, height=0.9, corner_radius=0.15, fill_color=BOX_TOP, fill_opacity=1,
                                   stroke_width=0).move_to([x, Y, 0])
            txt = T(s, 30).move_to([x, Y, 0])
            anims = [FadeIn(box, shift=UP * 0.2), FadeIn(txt)]
            if prev is None:
                anims.append(Create(arrow([-3.25, -0.1], [-1.9, 0.45], sw=4)))
            else:
                anims.append(Create(arrow([prev.get_right()[0] + 0.02, Y], [box.get_left()[0] - 0.02, Y], sw=4)))
            gplay(self, *anims, run_time=0.4)
            prev = box
        back = CurvedArrow([4.45, Y - 0.5, 0], [-1.25, Y - 0.5, 0], angle=-PI / 3, color=INK, stroke_width=5)
        gplay(self, Create(back), run_time=0.5)
        at(self, "and stops")
        stop = RoundedRectangle(width=6.0, height=0.8, corner_radius=0.15, fill_color=DARK_TOP, fill_opacity=1,
                                stroke_color=INK, stroke_width=3).move_to([1.6, -1.55, 0])
        stxt = T("stops: done · out of budget · errors", 30, CARD).move_to([1.6, -1.55, 0])
        gplay(self, FadeIn(stop, shift=UP * 0.2), FadeIn(stxt), run_time=0.45)
        finish(self)


# ═════════════════════════════ P3D — the human gate, bound to the fingerprint ═════════════════════════════
class P3D_Gate(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        prop = sheet(-4.6, 0.9, 1.3, 1.6, rows=3)
        pl = under(prop, "proposal", 32)
        fp = under(pl, "c50b5646d54e", 28, buff=0.12)
        enter(self, prop, pl, fp)
        at(self, "I approve or refuse")
        g = Square(side_length=0.9, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-1.3, 0.9, 0])
        gplay(self, Create(arrow([-3.8, 0.9], [-1.85, 0.9])), FadeIn(g, scale=0.6), FadeIn(under(g, "my decision", 32)), run_time=0.45)
        ap = tray_at(2.3, 1.6, 1.2, 0.4, 0.85)
        rf = tray_at(2.3, -0.3, 1.2, 0.4, 0.85)
        apl = beside(ap, "approve", 32)
        rfl = beside(rf, "refuse", 32)
        gplay(self, Create(arrow([-0.75, 1.05], [1.25, 1.5], sw=4)), Create(arrow([-0.75, 0.75], [1.25, -0.2], sw=4)),
              FadeIn(ap), FadeIn(rf), FadeIn(apl), FadeIn(rfl), run_time=0.5)
        gplay(self, Create(check(apl.get_right()[0] + 0.45, 1.6, 0.2)), Create(cross(rfl.get_right()[0] + 0.45, -0.3, 0.18)),
              run_time=0.3)
        at(self, "tied to the fingerprint")
        d1 = Dot([fp.get_left()[0] - 0.25, fp.get_center()[1], 0], radius=0.1, color=TERRA)
        d2 = Dot([-1.3, 0.9, 0], radius=0.12, color=TERRA)
        gplay(self, FadeIn(d1, scale=0.4), FadeIn(d2, scale=0.4), run_time=0.35)
        at(self, "It can only read")
        gplay(self, FadeIn(T("reads 3 sites only · no way to send", 32).move_to([0.6, -1.95, 0])), run_time=0.4)
        finish(self)


# ═════════════════════════════ P3E — resources and next steps ═════════════════════════════
class P3E_Resources(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        rows = [("Claude Code", 1.6, "Claude Code"), ("free public job boards", 0.8, "free public"),
                ("no API keys", 0.0, "no keys"), ("$0 compute", -0.8, "no paid compute")]
        boxes = [Square(side_length=0.42, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-5.6, y, 0])
                 for _, y, _ in rows]
        enter(self, *boxes)
        for (s, y, cue), b in zip(rows, boxes):
            at(self, cue)
            gplay(self, Create(check(-5.62, y, 0.15)), FadeIn(at_left(T(s, 34).move_to([0, y, 0]), -5.15)), run_time=0.3)
        at(self, "Next, I'll re-run")
        gplay(self, FadeIn(T("next (proposed)", 30).move_to([2.6, 2.0, 0])), run_time=0.3)
        b1 = DashedVMobject(RoundedRectangle(width=3.2, height=0.95, corner_radius=0.15, stroke_color=INK, stroke_width=4),
                            num_dashes=36).move_to([2.6, 1.0, 0])
        gplay(self, Create(b1), FadeIn(T("re-run verdicts", 32).move_to([2.6, 1.0, 0])), run_time=0.45)
        b2 = DashedVMobject(RoundedRectangle(width=3.2, height=0.95, corner_radius=0.15, stroke_color=INK, stroke_width=4),
                            num_dashes=36).move_to([2.6, -0.8, 0])
        gplay(self, Create(arrow([2.6, 0.45], [2.6, -0.25], sw=4)), Create(b2), FadeIn(T("evaluate", 32).move_to([2.6, -0.8, 0])),
              run_time=0.45)
        finish(self)


# ═════════════════════════════ P4A — coverage, 16 -> 50 of 123 (real) ═════════════════════════════
class P4A_Coverage(Scene):
    """Real: board-resolver/runs/live-2026-11-23 (summary.json, log.jsonl, coverage.json)."""
    def construct(self):
        honesty_tag(self); part_chip(self)
        L, W = -4.6, 10.0
        base = Rectangle(width=W, height=0.55, fill_color=BAR3, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([L + W / 2, -1.15, 0])
        enter(self, base)
        at(self, "First, coverage")
        num = T("16 / 123", 104).move_to([0.4, 0.75, 0])
        f16 = Rectangle(width=W * 16 / 123, height=0.55, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0)
        f16.move_to([L + W * 16 / 123 / 2, -1.15, 0])
        gplay(self, FadeIn(num, scale=0.85), GrowFromEdge(f16, LEFT), FadeIn(under(base, "boards confirmed at my gate", 32)),
              run_time=0.5)
        at(self, "six hundred twenty-nine")
        gplay(self, FadeIn(at_left(T("629 requests · 3 sites only", 34).move_to([0, 2.35, 0]), -6.05)), run_time=0.35)
        at(self, "thirty-nine companies")
        gplay(self, FadeIn(at_left(T("39 candidates", 34).move_to([0, 2.35, 0]), 2.3)), run_time=0.35)
        at(self, "to fifty", lead=0.3)
        f50 = Rectangle(width=W * 50 / 123, height=0.55, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0)
        f50.move_to([L + W * 50 / 123 / 2, -1.15, 0])
        num50 = T("50 / 123", 104).move_to([0.4, 0.75, 0])
        gplay(self, Transform(f16, f50), Transform(num, num50), run_time=0.8)
        gplay(self, FadeIn(T("from 16", 32).move_to([L + W * 16 / 123 / 2 + 0.1, -0.5, 0])), run_time=0.3)
        finish(self)


# ═════════════════════════════ P4B — what it got wrong (real cases) ═════════════════════════════
class P4B_Failures(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        at(self, "Five boards belonged")
        s1 = sheet(-5.0, 1.3, 0.85, 1.05, rows=2)
        s2 = sheet(-5.0, -0.45, 0.85, 1.05, rows=2)
        l1 = at_left(T("talent → Slice Talent Community", 32).move_to([0, 1.3, 0]), -4.3)
        l2 = at_left(T("village → a childcare center", 32).move_to([0, -0.45, 0]), -4.3)
        gplay(self, FadeIn(s1, shift=UP * 0.2), FadeIn(l1), FadeIn(s2, shift=UP * 0.2), FadeIn(l2), run_time=0.5)
        at(self, "Claude flagged them")
        x1, x2 = cross(-5.0, 1.3, 0.28), cross(-5.0, -0.45, 0.28)
        gplay(self, Create(x1), Create(x2), run_time=0.35)
        at(self, "I refused all five")
        ref = T("5 refused", 56).move_to([4.2, 0.55, 0])
        refl = under(ref, "at my gate", 32, buff=0.15)
        gplay(self, FadeIn(ref, scale=0.85), FadeIn(refl), run_time=0.4)
        phase1 = VGroup(s1, s2, l1, l2, x1, x2, ref, refl)
        at(self, "The name check")
        gplay(self, FadeOut(phase1, shift=UP * 0.2), run_time=0.4)
        ww = sheet(-4.9, 1.0, 0.95, 1.15, rows=2)
        wl = at_left(under(ww, "Weight Watchers", 32, buff=0.15), -6.0)   # Gate B 2026-11-23: was centred, left edge -6.35
        gplay(self, FadeIn(ww, shift=UP * 0.2), FadeIn(wl), run_time=0.4)
        at(self, "a mismatch")
        m1 = at_left(T("called a mismatch", 32).move_to([0, 1.35, 0]), -3.95)
        gplay(self, FadeIn(m1), run_time=0.3)
        at(self, "though it's the right")
        m2 = at_left(T("but it's the right company", 32).move_to([0, 0.75, 0]), -3.95)
        gplay(self, FadeIn(m2), Create(check(m2.get_right()[0] + 0.4, 0.75, 0.18)), run_time=0.35)
        at(self, "Five approved boards")
        emp = tray_at(4.1, 1.05, 1.3, 0.45, 0.9)
        gplay(self, FadeIn(emp, shift=DOWN * 0.2), FadeIn(under(emp, "5 empty boards", 32, buff=0.15)), run_time=0.4)
        at(self, "sixty-seven")
        n67 = T("67", 72).move_to([-4.9, -1.35, 0])
        gplay(self, FadeIn(n67, scale=0.85), FadeIn(at_left(T("showed no board under the names it tried", 30)
                                                            .move_to([0, -1.35, 0]), -4.1)), run_time=0.4)
        finish(self)


# ═════════════════════════════ P4C — the bug no test caught ═════════════════════════════
class P4C_Bug(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        term = terminal(-4.0, 0.6, 2.1, 1.45)
        enter(self, term, under(term, "the command", 32))
        at(self, "saved my approval")
        dec = sheet(-0.4, 0.6, 1.2, 1.5, rows=3)
        gplay(self, Create(arrow([-2.85, 0.6], [-1.15, 0.6], sw=4)), FadeIn(dec, shift=LEFT * 0.3),
              FadeIn(under(dec, "saved", 32)), Create(check(-0.45, 0.6, 0.2)), run_time=0.45)
        at(self, "then crashed")
        gplay(self, Create(cross(-4.0, 0.6, 0.35, color=TERRA, w=9)), FadeIn(T("then crashed", 32).move_to([-4.0, 1.95, 0])),
              run_time=0.35)
        at(self, "A test now")
        pill = pill_check(3.6, 1.2, 1.6)
        gplay(self, FadeIn(pill, shift=DOWN * 0.2), FadeIn(T("regression test", 32).move_to([3.6, 0.45, 0])), run_time=0.4)
        at(self, "all twenty-eight")
        gplay(self, FadeIn(T("28 / 28 tests pass", 36).move_to([3.6, -0.45, 0])), run_time=0.35)
        finish(self)


# ═════════════════════════════ P4D — how the verdicts will be judged (proposed) ═════════════════════════════
class P4D_Plan(Scene):
    def construct(self):
        honesty_tag(self); part_chip(self)
        at(self, "I'll set aside")
        box = DashedVMobject(RoundedRectangle(width=2.5, height=1.8, corner_radius=0.15, stroke_color=INK, stroke_width=4),
                             num_dashes=40).move_to([-4.4, 1.0, 0])
        inside = VGroup(*[sheet(-4.85 + 0.45 * i, 1.0, 0.55, 0.75, rows=2) for i in range(3)])
        hl = under(box, "held-out set", 32, buff=0.15)
        gplay(self, Create(box), FadeIn(inside), FadeIn(hl), FadeIn(under(hl, "set aside first", 28, buff=0.08)), run_time=0.5)
        at(self, "If fewer than nine")
        bx, bw = 1.6, 4.6
        bar = Rectangle(width=bw, height=0.45, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([bx, 1.3, 0])
        tick = Line([bx - bw / 2 + bw * 0.9, 1.0, 0], [bx - bw / 2 + bw * 0.9, 1.6, 0], color=TERRA, stroke_width=7)
        gplay(self, FadeIn(bar), Create(tick), FadeIn(T("pass: 9 in 10 apply verdicts right", 30).move_to([bx, 2.05, 0])),
              run_time=0.45)
        at(self, "it didn't work")
        gplay(self, FadeIn(T("below the line: it didn't work", 28).move_to([bx, 0.6, 0])), run_time=0.35)
        at(self, "after fourteen days")
        days = VGroup(*[Square(side_length=0.3, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=3)
                        for _ in range(14)]).arrange_in_grid(rows=2, cols=7, buff=0.1).move_to([0.6, -0.55, 0])
        gplay(self, FadeIn(days), FadeIn(at_left(T("14-day re-check", 30).move_to([0, -0.55, 0]), 2.4)), run_time=0.4)
        gplay(self, LaggedStart(*[d.animate.set_fill(BAR2) for d in days], lag_ratio=0.1), run_time=1.0)
        at(self, "This sample can show")
        gplay(self, FadeIn(at_left(T("can show: what it gets wrong", 30).move_to([0, -1.75, 0]), -6.0)), run_time=0.35)
        gplay(self, FadeIn(at_left(T("can't show: anyone hired", 30).move_to([0, -1.75, 0]), 1.0)), run_time=0.35)
        finish(self)
