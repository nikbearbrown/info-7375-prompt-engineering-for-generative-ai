"""scenes.py — A Job-Search Agent You Can Check (Varnika M, INFO 7375 Final Project Film, four-part).

Show-tell style: one drawn picture per beat, few labels, the narration explains.
The kit block below is the same trimmed brutalist.art show-tell kit (b21f625) used in the October
film (../scenes.py); the scenes after it are new. Every scene shows its part label (top left).
"""
from manim import *
import numpy as np
import json as _json, os as _os

# ═════════════════════════════ ISO KIT (show-tell, trimmed) ═════════════════════════════
STAGE = "#F2F0E9"; INK = "#3D3929"; TERRA = "#D97757"; DIM = "#8B8F96"; GHOST = "#D9D4C7"; CARD = "#FAF9F5"
BOX_TOP, BOX_L, BOX_R = "#F3E9D8", "#DCC9AA", "#C7AE86"
BOX_IN1, BOX_IN2, BOX_FLOOR = "#CDB894", "#BFA67E", "#B39A72"
DARK_TOP, DARK_L, DARK_R = "#3A3530", "#26221F", "#1E1B18"
PAGE_TOP, PAGE_L, PAGE_R = "#FFFFFF", "#ECE7DF", "#E2DCD2"
BAR1, BAR2, BAR3 = "#8B8F96", "#B4AFA6", "#D9D4C7"
KRAFT_DEEP = "#9C8462"
SERIF = "EB Garamond"
C30 = 0.8660254
config.background_color = STAGE


def T(s, size=40, color=INK, bold=False):
    return Text(s, font=SERIF, color=color, font_size=size, weight="BOLD" if bold else "NORMAL")


class Iso:
    def __init__(self, ox=0.0, oy=0.0, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z=0.0):
        return np.array([self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * 0.5 * self.s + z * self.s, 0.0])

    def quad(self, pts, fill, stroke=INK, sw=4):
        return Polygon(*[self.p(*q) for q in pts], fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=sw)

    def box(self, x0, y0, z0, w, d, h, top=BOX_TOP, left=BOX_L, right=BOX_R, stroke=INK, sw=4):
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        return VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], left, stroke, sw),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], right, stroke, sw),
            self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, stroke, sw))

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


def check(x, y, s=0.2, color=INK, w=7):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))


def cursor(x, y, s=0.45):
    return Polygon([x, y, 0], [x, y - s, 0], [x + s * 0.28, y - s * 0.72, 0], [x + s * 0.62, y - s * 0.66, 0],
                   fill_color=INK, fill_opacity=1, stroke_color=CARD, stroke_width=2)


# ═════════════════════════════ pacing (narration is the clock) ═════════════════════════════
try:
    _SHEET = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "beat_sheet.json")))
    _TARGET = {b["beat_id"]: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0) for b in _SHEET["beats"]}
    _NARR = {b["beat_id"]: b["narration_text"] for b in _SHEET["beats"]}
except Exception:
    _TARGET, _NARR = {}, {}


def _bid(self):
    return type(self).__name__.split("_")[0]


def _elapsed(self):
    rt = getattr(getattr(self, "renderer", None), "time", None)
    return float(rt) if isinstance(rt, (int, float)) else 0.0


def until(self, phrase, lead=0.25):
    n, target = _NARR.get(_bid(self), ""), _TARGET.get(_bid(self), 0)
    if not n or not target or phrase not in n:
        return
    gap = target * n.index(phrase) / len(n) - lead - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def finish(self):
    target = _TARGET.get(_bid(self), 0)
    if not target:
        self.wait(2.0)
        return
    rem = target - _elapsed(self) - 0.1     # stay under the audio: compile.py centre-cuts long clips
    if rem > 0.05:
        self.wait(rem)


def G(self, *anims, rt=0.7):
    """Play, but never across the clip midpoint (GATE T and Gate V sample there)."""
    mid = _TARGET.get(_bid(self), 10) / 2
    now = _elapsed(self)
    if now < mid + 0.3 and now + rt > mid - 0.3:
        self.wait(max(0.01, mid + 0.32 - now))
    self.play(*anims, run_time=rt)


# ═════════════════════════════ this film's cast ═════════════════════════════
def ctag():
    """On-screen honesty label for drawings of things that do not exist yet."""
    return T("planned · constructed", 32).move_to([4.25, -3.05, 0])


def flat_page(x, y, w=3.0, h=3.8, n=6, inset=0.4):
    """The docs page: white sheet, ink outline, kraft shadow, ghost text lines. `.ly` holds line heights."""
    shadow = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.14, y - 0.14, 0])
    sheet = Rectangle(width=w, height=h, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    top, bot = y + h / 2 - 0.55, y - h / 2 + 0.5
    ly = [top - i * (top - bot) / max(1, n - 1) for i in range(n)]
    lines = VGroup(*[Line([x - w / 2 + inset, yy, 0], [x + w / 2 - inset - (0.5 if i % 3 == 2 else 0), yy, 0],
                          color=GHOST, stroke_width=10) for i, yy in enumerate(ly)])
    g = VGroup(shadow, sheet, lines)
    g.ly, g.x0, g.x1 = ly, x - w / 2 + inset, x + w / 2 - inset
    return g


def hl(page, i):
    """Highlight line i of a flat_page: an ink line over it and a terracotta dot at its start."""
    yy = page.ly[i]
    return (Line([page.x0, yy, 0], [page.x1, yy, 0], color=INK, stroke_width=10),
            Dot([page.x0 - 0.22, yy, 0], radius=0.09, color=TERRA))


def qcard(x, y, w=1.3, h=1.0):
    """The question card: a kraft card with two ghost lines."""
    shadow = Rectangle(width=w, height=h, fill_color=BOX_R, fill_opacity=1, stroke_width=0).move_to([x + 0.1, y - 0.1, 0])
    card = Rectangle(width=w, height=h, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    l1 = Line([x - w / 2 + 0.22, y + 0.15, 0], [x + w / 2 - 0.22, y + 0.15, 0], color=KRAFT_DEEP, stroke_width=8)
    l2 = Line([x - w / 2 + 0.22, y - 0.15, 0], [x + 0.05, y - 0.15, 0], color=KRAFT_DEEP, stroke_width=8)
    return VGroup(shadow, card, l1, l2)


def kcard(x, y, w=1.2, h=1.5, fill=BOX_TOP, stroke=INK):
    shadow = Rectangle(width=w, height=h, fill_color=BOX_R, fill_opacity=1, stroke_width=0).move_to([x + 0.1, y - 0.1, 0])
    card = Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=4).move_to([x, y, 0])
    return VGroup(shadow, card)


def outline_card(x, y, w=1.2, h=1.5):
    """A 'will exist' placeholder: empty outline in deep kraft."""
    return Rectangle(width=w, height=h, stroke_color=KRAFT_DEEP, stroke_width=5, fill_opacity=0).move_to([x, y, 0])


def shelf(x, y, w):
    return Rectangle(width=w, height=0.3, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])


def gate(x, y, h=2.0, w=1.6):
    """A conveyor gate: two kraft posts and a lintel."""
    lp = Rectangle(width=0.28, height=h, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x - w / 2, y + h / 2, 0])
    rp = Rectangle(width=0.28, height=h, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x + w / 2, y + h / 2, 0])
    top = Rectangle(width=w + 0.28, height=0.3, fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + h + 0.15, 0])
    return VGroup(lp, rp, top)


def tray(x, y, w=2.6, h=0.9):
    """A flat open tray: kraft base and a front lip."""
    base = Rectangle(width=w, height=h, fill_color=BOX_IN1, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    lip = Rectangle(width=w, height=0.35, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y - h / 2 + 0.17, 0])
    base.set_z_index(0); lip.set_z_index(3)
    return base, lip




# ═════════════════════════════ this film's cast ═════════════════════════════
RUST = "#A3472A"   # darker accent: 5.27:1 on cream (Gate T needs 4.5:1; TERRA text is 2.74:1)
P1, P2, P3, P4 = "1 · What and why", "2 · What others have done", "3 · How I'll build it", "4 · How I'll know it worked"


def part(p):
    """Part label, top left, on every scene: the four-part structure is always visible."""
    return T(p, 32, color=RUST, bold=True).align_to([-6.2, 0, 0], LEFT).align_to([0, 3.35, 0], UP)


def ctag(s="planned · drawing"):
    """On-screen honesty label for drawings of things that are not built yet."""
    return T(s, 30, color=DIM).align_to([6.2, 0, 0], RIGHT).align_to([0, -3.35, 0], DOWN)


def src(s):
    """Source tag for real numbers and real pages."""
    return T(s, 30, color=DIM).align_to([-6.2, 0, 0], LEFT).align_to([0, -3.35, 0], DOWN)


def posting(x, y, w=1.0, h=1.3, fill=CARD):
    """A job posting card: card plus three ghost lines."""
    c = kcard(x, y, w=w, h=h, fill=fill)
    lines = VGroup(*[Line([x - w / 2 + 0.18, y + h / 2 - 0.3 - i * 0.28, 0],
                          [x + w / 2 - 0.18 - (0.25 if i == 2 else 0), y + h / 2 - 0.3 - i * 0.28, 0],
                          color=GHOST, stroke_width=7) for i in range(3)])
    return VGroup(c, lines)


def tag(s, x, y, size=30, color=INK, stroke=INK):
    t = T(s, size, color=color)
    box = RoundedRectangle(width=t.width + 0.4, height=t.height + 0.3, corner_radius=0.12, fill_color=CARD,
                           fill_opacity=1, stroke_color=stroke, stroke_width=3)
    g = VGroup(box, t).move_to([x, y, 0])
    return g


def stamp(s, x, y, size=34, color=RUST):
    t = T(s, size, color=color, bold=True)
    box = Rectangle(width=t.width + 0.35, height=t.height + 0.3, stroke_color=color, stroke_width=5, fill_opacity=0)
    return VGroup(box, t).move_to([x, y, 0]).rotate(0.12)


def person(x, y, s=1.0, color=INK, fill=BOX_TOP):
    head = Circle(radius=0.32 * s, fill_color=fill, fill_opacity=1, stroke_color=color, stroke_width=4).move_to([x, y + 0.55 * s, 0])
    body = RoundedRectangle(width=1.0 * s, height=0.8 * s, corner_radius=0.35 * s, fill_color=fill, fill_opacity=1,
                            stroke_color=color, stroke_width=4).move_to([x, y - 0.25 * s, 0])
    return VGroup(body, head)


def magnifier(x, y, r=0.45):
    ring = Circle(radius=r, stroke_color=INK, stroke_width=7, fill_color=CARD, fill_opacity=0.35).move_to([x, y, 0])
    handle = Line([x + r * 0.7, y - r * 0.7, 0], [x + r * 1.7, y - r * 1.7, 0], color=INK, stroke_width=12)
    return VGroup(ring, handle)


def envelope(x, y, w=0.9, h=0.6):
    body = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y, 0])
    flap = VGroup(Line([x - w / 2, y + h / 2, 0], [x, y - 0.02, 0], color=INK, stroke_width=3),
                  Line([x, y - 0.02, 0], [x + w / 2, y + h / 2, 0], color=INK, stroke_width=3))
    return VGroup(body, flap)


def xmark(x, y, s=0.25, color=RUST, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def lock(x, y):
    body = RoundedRectangle(width=0.9, height=0.75, corner_radius=0.1, fill_color=BOX_R, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    shackle = Arc(radius=0.3, start_angle=0, angle=PI, color=INK, stroke_width=8).move_to([x, y + 0.5, 0])
    return VGroup(shackle, body)


# ═════════════════════════════ part 1 · what and why ═════════════════════════════
class B01_Funnel(Scene):
    def construct(self):
        stack = VGroup(*[posting(-4.6 + i * 0.12, 0.9 - i * 0.12) for i in range(6)])
        funnel = Polygon([-1.6, 1.6, 0], [1.0, 1.6, 0], [0.0, -0.2, 0], [-0.6, -0.2, 0], fill_color=BOX_L,
                         fill_opacity=1, stroke_color=INK, stroke_width=4)
        spout = Rectangle(width=0.6, height=0.7, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-0.3, -0.55, 0])
        self.add(part(P1), stack, T("job boards", 34).move_to([-4.3, -1.55, 0]), ctag())
        until(self, "hundreds")
        more = VGroup(*[posting(-3.9 + i * 0.12, 0.2 - i * 0.12) for i in range(4)])
        G(self, FadeIn(more, shift=DOWN * 0.4), rt=0.5)
        until(self, "does the reading")
        G(self, FadeIn(funnel), FadeIn(spout), rt=0.6)
        G(self, more.animate.move_to([-0.3, 1.2, 0]).scale(0.4).set_opacity(0.0), rt=0.9)
        until(self, "picks out")
        outs = VGroup(*[posting(2.6 + i * 1.35, -0.6) for i in range(3)])
        G(self, LaggedStart(*[FadeIn(o, shift=RIGHT * 0.5) for o in outs], lag_ratio=0.25), rt=0.9)
        G(self, FadeIn(T("shortlist", 34).move_to([3.95, -1.85, 0])), rt=0.4)
        until(self, "shows why")
        whys = VGroup(*[tag("why", 2.6 + i * 1.35, 0.55, 28, stroke=RUST) for i in range(3)])
        G(self, LaggedStart(*[FadeIn(w) for w in whys], lag_ratio=0.2), rt=0.7)
        finish(self)


class B02_OneOf675(Scene):
    def construct(self):
        cols, rows = 27, 25
        dots = VGroup(*[Dot([-5.6 + c * 0.25, 2.55 - r * 0.2, 0], radius=0.06, color=INK)
                        for r in range(rows) for c in range(cols)])
        self.add(part(P1), src("JS1 · Anthropic board · live run 2026-10-31"))
        until(self, "six hundred")
        G(self, FadeIn(dots), FadeIn(T("675 postings", 40).move_to([4.6, 1.0, 0])), rt=0.8)
        until(self, "made-up candidate")
        hit = dots[13 * cols + 17]
        ring = Circle(radius=0.22, color=RUST, stroke_width=6).move_to(hit.get_center())
        G(self, hit.animate.set_color(RUST).scale(1.8), Create(ring), FadeIn(T("1 match", 44, color=RUST, bold=True).move_to([4.6, -0.2, 0])), rt=0.7)
        finish(self)


class B03_PersonDecides(Scene):
    def construct(self):
        card = VGroup(posting(-4.4, 0.6, w=1.6, h=2.0), T("shortlist", 34).move_to([-4.4, -0.8, 0]))
        self.add(part(P1), card, ctag("planned · drawing"))
        until(self, "won't apply")
        env = envelope(-1.4, -1.6, 1.2, 0.8)
        G(self, FadeIn(env), rt=0.4)
        G(self, Create(xmark(-1.4, -1.6, 0.45)), FadeIn(T("no applying, no sending", 32).move_to([-1.4, -2.55, 0])), rt=0.5)
        until(self, "hand a person")
        who = person(3.8, 1.1, 1.3)
        G(self, FadeIn(who), card.animate.move_to([1.4, 0.6, 0]), rt=0.9)
        until(self, "only that person")
        btns = VGroup(tag("yes", 2.5, -1.4, 34), tag("no", 3.6, -1.4, 34), tag("not yet", 5.0, -1.4, 34))
        G(self, LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in btns], lag_ratio=0.3), rt=0.9)
        finish(self)


class B04_Reasons(Scene):
    def construct(self):
        card = posting(-1.0, 0.2, w=2.2, h=2.8)
        why = tag("why it fits", -1.0, -1.65, 30, stroke=RUST)
        self.add(part(P1), card)
        until(self, "show its reasons")
        G(self, FadeIn(why, shift=UP * 0.2), rt=0.5)
        mag = magnifier(-5.0, 1.0)
        G(self, FadeIn(mag), rt=0.3)
        until(self, "check it")
        G(self, mag.animate.move_to([0.75, -1.25, 0]), rt=0.8)
        G(self, Create(check(2.7, -1.55, s=0.3)), FadeIn(T("check it, don't just trust it", 34).move_to([3.4, 1.4, 0])), rt=0.6)
        finish(self)


# ═════════════════════════════ part 2 · what others have done ═════════════════════════════
class B05_Alerts(Scene):
    def construct(self):
        search = VGroup(kcard(-4.6, 0.4, w=1.8, h=1.4), magnifier(-4.75, 0.55, r=0.3))
        base, lip = tray(3.6, -0.6, w=3.0, h=1.0)
        self.add(part(P2), src("LinkedIn and Indeed help pages · checked 2026-11-23"))
        until(self, "LinkedIn and Indeed")
        G(self, FadeIn(search), FadeIn(T("saved search", 32).move_to([-4.6, -0.75, 0])),
          FadeIn(T("LinkedIn · Indeed", 34).move_to([-4.6, 1.75, 0])), rt=0.6)
        until(self, "send you")
        G(self, FadeIn(base), FadeIn(lip), FadeIn(T("inbox", 32).move_to([3.6, -1.6, 0])), rt=0.4)
        envs = [envelope(-2.6, 0.4) for _ in range(3)]
        for i, e in enumerate(envs):
            self.add(e)
            G(self, e.animate.move_to([2.7 + i * 0.9, -0.35, 0]), rt=0.55)
        G(self, FadeIn(T("daily or weekly", 32).move_to([0.2, 1.3, 0])), rt=0.4)
        until(self, "don't explain")
        G(self, FadeIn(T("why?", 48, color=RUST, bold=True).move_to([4.5, 1.1, 0])), rt=0.5)
        finish(self)


class B06_AutoApply(Scene):
    def construct(self):
        self.add(part(P2), src("company pages · checked 2026-11-23"))
        xs = [-5.0, -1.7, 1.6, 4.9]
        until(self, "Skills Match")
        c1 = posting(xs[0], 0.5, w=1.6, h=2.0)
        dial = Arc(radius=0.55, start_angle=PI, angle=-PI, color=INK, stroke_width=6).move_to([xs[0], -0.55, 0])
        needle = Line([xs[0], -0.8, 0], [xs[0] + 0.35, -0.4, 0], color=RUST, stroke_width=7)
        G(self, FadeIn(c1), Create(dial), Create(needle), FadeIn(T("Skills Match", 30).move_to([xs[0], -1.6, 0])), rt=0.7)
        until(self, "Jobright")
        pile = VGroup(*[posting(xs[1] - 0.25 + i * 0.12, 0.6 - i * 0.12, w=1.3, h=1.7) for i in range(4)])
        G(self, FadeIn(pile), FadeIn(T("Jobright", 30).move_to([xs[1], -1.6, 0])), rt=0.5)
        until(self, "LazyApply")
        G(self, FadeIn(stamp("applied", xs[1], 2.15)), FadeIn(T("LazyApply", 30).move_to([xs[1], -2.15, 0])), rt=0.5)
        until(self, "Autopilot")
        c3 = posting(xs[2], 0.5, w=1.4, h=1.8)
        G(self, FadeIn(c3), FadeIn(T("Simplify Autopilot", 30).move_to([xs[2], -1.6, 0])), rt=0.5)
        G(self, FadeIn(stamp("no review", xs[2], 2.15, 30)), rt=0.4)
        until(self, "Copilot mode")
        c4 = posting(xs[3], 0.5, w=1.4, h=1.8)
        G(self, FadeIn(c4), FadeIn(T("Simplify Copilot", 30).move_to([xs[3], -1.6, 0])),
          FadeIn(tag("you click submit", xs[3], 2.0, 28)), rt=0.6)
        finish(self)


class B07_Different(Scene):
    def construct(self):
        card = posting(-4.2, 0.2, w=1.8, h=2.4)
        self.add(part(P2), card, T("my shortlist", 34).move_to([-4.2, -1.45, 0]))
        rows = [("rules you can recheck", 1.5), ("a separate run checker", 0.2), ("a person approves", -1.1)]
        keys = ["rules you can recheck", "separate program", "person approving"]
        items = []
        for (label, y), k in zip(rows, keys):
            until(self, k)
            t = tag(label, 1.4, y, 34)
            ck = check(4.6, y, s=0.22)
            items += [t, ck]
            G(self, FadeIn(t, shift=LEFT * 0.3), Create(ck), rt=0.6)
        until(self, "what mine adds")
        box = SurroundingRectangle(VGroup(*items), color=RUST, stroke_width=5, buff=0.3)
        G(self, Create(box), rt=0.6)
        finish(self)


# ═════════════════════════════ part 3 · how I'll build it ═════════════════════════════
class B08_Data(Scene):
    def construct(self):
        self.add(part(P3))
        agent = kcard(2.3, 0.4, w=2.0, h=1.6, fill=BOX_TOP)
        self.add(agent, T("agent", 36).move_to([2.3, 0.4, 0]))
        rows = [("Anthropic on", "Greenhouse · Anthropic", 1.7), ("Palantir on", "Lever · Palantir", 0.4),
                ("Linear on", "Ashby · Linear", -0.9)]
        for k, label, y in rows:
            until(self, k)
            b = kcard(-5.2, y, w=0.9, h=0.8)
            t = T(label, 30).move_to([-3.0, y, 0]).align_to([-4.55, 0, 0], LEFT)
            a = Arrow([-0.1, y, 0], [1.25, 0.4, 0], color=DIM, stroke_width=5, buff=0.1)
            G(self, FadeIn(b), FadeIn(t), Create(a), rt=0.5)
        until(self, "made up")
        prof = VGroup(kcard(5.4, 0.4, w=1.6, h=2.0, fill=CARD), person(5.4, 0.55, 0.6))
        G(self, FadeIn(prof), FadeIn(T("Aarav Patel", 30).move_to([5.4, -1.0, 0])),
          FadeIn(T("fictional", 30, color=RUST).move_to([5.4, -1.5, 0])), rt=0.6)
        G(self, FadeIn(T("public feeds · no login", 32, color=DIM).move_to([-2.6, -2.3, 0])), rt=0.4)
        finish(self)


class B09_FiveRules(Scene):
    def construct(self):
        self.add(part(P3), src("JS1 · 73 tests"))
        until(self, "watched one board")
        board = kcard(-4.4, 1.3, w=1.3, h=1.0)
        G(self, FadeIn(board), FadeIn(T("one board", 30).move_to([-4.4, 0.45, 0])), rt=0.5)
        until(self, "new postings")
        p = posting(-2.2, 1.3, w=0.9, h=1.1)
        G(self, FadeIn(p, shift=RIGHT * 0.3), FadeIn(tag("new", -2.2, 2.35, 28, stroke=RUST)), rt=0.5)
        until(self, "judged each one")
        G(self, FadeIn(T("five written rules", 34).move_to([2.4, 1.3, 0])), rt=0.4)
        names = ["title", "seniority", "location", "experience", "skills"]
        until(self, "five written rules", lead=0.0)
        cards = [VGroup(kcard(-4.8 + i * 2.4, -0.9, w=1.0, h=1.2, fill=CARD), T(f"R{i + 1}", 30).move_to([-4.8 + i * 2.4, -0.9, 0]),
                        T(n, 30).move_to([-4.8 + i * 2.4, -1.95, 0])) for i, n in enumerate(names)]
        G(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in cards], lag_ratio=0.4), rt=2.2)
        finish(self)


class B10_Loop(Scene):
    def construct(self):
        self.add(part(P3), src("JS2 · live run 2026-11-10 · 677 + 304 + 33 postings"))
        cx, cy, r = -3.3, 0.2, 1.6
        until(self, "loop")
        th0, sweep = PI / 2 - 0.25, -1.85 * PI
        arc = Arc(radius=r, start_angle=th0, angle=sweep, arc_center=[cx, cy, 0], color=INK, stroke_width=6)
        the = th0 + sweep                                   # add_tip would reshape the arc, so draw the tip by hand
        tip = Triangle(color=INK, fill_color=INK, fill_opacity=1).scale(0.16)
        tip.rotate(np.arctan2(-np.cos(the), np.sin(the)) - PI / 2).move_to([cx + r * np.cos(the), cy + r * np.sin(the), 0])
        loop = VGroup(arc, tip)
        boxes = VGroup(*[kcard(cx + r * np.cos(a), cy + r * np.sin(a), w=0.7, h=0.55, fill=BOX_TOP)
                         for a in (PI / 2, 0, -PI / 2, PI)])
        G(self, Create(loop), FadeIn(boxes), rt=0.8)
        G(self, Create(xmark(cx - r, cy, 0.22, w=6)), FadeIn(T("X = board that fails on purpose", 28, color=DIM).move_to([cx, cy - r - 0.6, 0])), rt=0.3)
        until(self, "permission policy")
        lk = lock(0.6, 1.3)
        G(self, FadeIn(lk), FadeIn(T("policy in code", 30).move_to([0.6, 0.45, 0])), rt=0.5)
        until(self, "one thousand")
        G(self, FadeIn(T("1,014 postings", 44, bold=True).move_to([4.3, 1.5, 0])), rt=0.5)
        until(self, "hundred and twenty-two")
        G(self, FadeIn(T("122 tests", 40).move_to([4.3, 0.4, 0])), rt=0.4)
        until(self, "separate checker")
        G(self, FadeIn(stamp("bug caught", 4.3, -1.0, 36)), FadeIn(T("separate checker", 30).move_to([4.3, -2.0, 0])), rt=0.6)
        finish(self)


class B11_Steps(Scene):
    def construct(self):
        self.add(part(P3), ctag("planned"))
        specs = [("First,", "filter · tool", "JS3", -4.2, 1.0), ("Then a written plan", "plan · checks · memory", "JS4", 0.0, 1.9),
                 ("Last,", "approval", "JS5", 4.2, 2.8)]
        for k, label, js, x, h in specs:
            until(self, k)
            stepbox = Rectangle(width=3.6, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5)
            stepbox.move_to([x, -2.4 + h / 2, 0])
            G(self, FadeIn(stepbox, shift=UP * 0.3), FadeIn(T(label, 32).move_to([x, -2.4 + h + 0.45, 0])),
              FadeIn(T(js, 34, color=INK, bold=True).move_to([x, -2.4 + h / 2, 0])), rt=0.6)
        finish(self)


class B12_Have(Scene):
    def construct(self):
        self.add(part(P3), shelf(0, -0.9, 12.0))
        items = [("Python", "Python"), ("Claude Code", "Claude Code (NEU)"),
                 ("Free public", "public boards"), ("my laptop", "laptop")]
        for i, (k, label) in enumerate(items):
            until(self, k)
            x = -4.8 + i * 3.2
            G(self, FadeIn(kcard(x, 0.0, w=1.2, h=1.4, fill=CARD), shift=DOWN * 0.3), FadeIn(T(label, 30).move_to([x, -1.6, 0])),
              Create(check(x + 0.05, 0.05, s=0.25)), rt=0.45)
        until(self, "No paid")
        G(self, FadeIn(tag("$0 paid API credits", 0, 2.0, 36, stroke=RUST)), rt=0.5)
        finish(self)


# ═════════════════════════════ part 4 · how I'll know it worked ═════════════════════════════
class B13_Rejects(Scene):
    def construct(self):
        self.add(part(P4), ctag("planned check"))
        until(self, "thirty postings")
        cards = VGroup(*[posting(-5.4 + c * 0.95, 1.7 - r * 1.0, w=0.7, h=0.85) for r in range(5) for c in range(6)])
        G(self, FadeIn(cards), FadeIn(T("30 rejected, picked at random", 30).move_to([-3.0, -3.0, 0])), rt=0.7)
        until(self, "by hand")
        mag = magnifier(-5.4, 1.7, r=0.35)
        G(self, FadeIn(mag), rt=0.2)
        G(self, mag.animate.move_to([-0.65, 1.7, 0]), rt=1.2)
        until(self, "more than one")
        G(self, FadeIn(tag("pass: at most 1 of 30 fits", 3.9, 0.9, 34, stroke=RUST)),
          FadeIn(T("2 or more: the filter failed", 32).move_to([3.9, -0.3, 0])), rt=0.6)
        finish(self)


class B14_MustSkip(Scene):
    def construct(self):
        self.add(part(P4), ctag("planned check"))
        base, lip = tray(-1.2, -1.6, w=8.4, h=1.0)
        self.add(base, lip, T("skipped", 32).move_to([-1.2, -2.55, 0]))
        traps = [("closed posting", "closed", -4.4), ("wrong location", "wrong location", -1.2), ("only matches", "keywords only", 2.0)]
        for k, label, x in traps:
            until(self, k)
            c = VGroup(posting(x, 1.4, w=1.1, h=1.3), T(label, 30).move_to([x, 2.5, 0]))
            G(self, FadeIn(c), rt=0.35)
            G(self, c[0].animate.move_to([x, -1.35, 0]).scale(0.8), rt=0.5)
        until(self, "even one")
        G(self, FadeIn(tag("0 let through", 4.9, 1.6, 36, stroke=RUST)), rt=0.5)
        until(self, "at least half")
        bar = Rectangle(width=2.6, height=0.45, stroke_color=INK, stroke_width=4).move_to([4.9, 0.2, 0])
        fill = Rectangle(width=1.3, height=0.45, fill_color=RUST, fill_opacity=1, stroke_width=0).align_to(bar, LEFT).align_to(bar, UP)
        G(self, Create(bar), FadeIn(fill), FadeIn(T("skip at least 50%", 32).move_to([4.9, -0.5, 0])), rt=0.6)
        finish(self)


class B15_Planted(Scene):
    def construct(self):
        self.add(part(P4), ctag("planned check"))
        run = posting(-2.6, 0.3, w=2.2, h=2.8)
        self.add(run, T("a run", 32).move_to([-2.6, -1.5, 0]))
        until(self, "break it")
        crack = VMobject(color=RUST, stroke_width=7).set_points_as_corners(
            [[-3.4, 1.5, 0], [-2.8, 0.9, 0], [-3.1, 0.4, 0], [-2.4, -0.2, 0], [-2.7, -0.7, 0]])
        G(self, Create(crack), FadeIn(T("planted failure", 32).move_to([-2.6, 2.1, 0])), rt=0.6)
        until(self, "separate checker")
        G(self, FadeIn(stamp("NOT SUPPORTED", 1.6, 0.4, 38)), FadeIn(T("separate checker", 30).move_to([1.6, -0.6, 0])), rt=0.6)
        until(self, "In my second assignment")
        G(self, FadeIn(src("JS2 · finished-wrong demonstration (seeded) · caught")), Create(check(4.8, 0.4, s=0.3)), rt=0.5)
        finish(self)


class B16_Fingerprint(Scene):
    def construct(self):
        self.add(part(P4), ctag("planned check"))
        card = posting(-2.2, 0.3, w=2.6, h=3.0)
        fp = tag("fingerprint", -2.2, -1.75, 30)
        ok = stamp("approved", 1.6, 0.9, 40)
        self.add(card, fp, ok)
        until(self, "changes")
        ln = Line([-3.25, 1.2 - 0.28, 0], [-1.15, 1.2 - 0.28, 0], color=RUST, stroke_width=9)
        G(self, Create(ln), FadeIn(T("one posting changed", 30, color=RUST).move_to([-2.2, 2.3, 0])),
          FadeIn(tag("new fingerprint", 1.2, -1.75, 30, stroke=RUST)), rt=0.6)
        until(self, "old yes")
        G(self, ok.animate.set_color(DIM), FadeIn(tag("no longer counts", 1.9, -0.4, 36, stroke=RUST)), rt=0.6)
        finish(self)


class B17_Verdict(Scene):
    def construct(self):
        self.add(part(P4))
        xs = [-4.5, -1.5, 1.5, 4.5]
        boxes = VGroup(*[Square(side_length=1.2, stroke_color=INK, stroke_width=5, fill_color=CARD, fill_opacity=1).move_to([x, 0.8, 0]) for x in xs])
        labels = VGroup(*[T(s, 30).move_to([x, -0.25, 0]) for s, x in zip(("30 rejected", "must-skip list", "planted failure", "approval"), xs)])
        self.add(boxes, labels)
        until(self, "all four")
        cks = [check(x + 0.05, 0.8, s=0.3) for x in xs]
        G(self, LaggedStart(*[Create(c) for c in cks], lag_ratio=0.25), rt=1.0)
        until(self, "it worked")
        word = T("worked", 56, bold=True).move_to([0, -1.6, 0])
        banner = RoundedRectangle(width=3.6, height=1.1, corner_radius=0.2, stroke_color=INK, stroke_width=4,
                                  fill_color=CARD, fill_opacity=1).move_to([0, -1.6, 0])
        G(self, FadeIn(banner), FadeIn(word), rt=0.4)
        until(self, "even one check")
        fail = Square(side_length=1.2, stroke_color=RUST, stroke_width=8, fill_opacity=0).move_to([xs[2], 0.8, 0])
        G(self, FadeOut(cks[2]), Create(fail), Create(xmark(xs[2], 0.8, 0.35)), banner.animate.set_stroke(RUST),
          Transform(word, T("didn't", 56, color=RUST, bold=True).move_to([0, -1.6, 0])), rt=0.6)
        until(self, "final report")
        G(self, FadeIn(T("the final report says which one", 32, color=DIM).move_to([0, -2.6, 0])), rt=0.5)
        finish(self)


class BOUT_Title(Scene):
    def construct(self):
        card = posting(-5.3, 0.2, w=1.4, h=1.8)
        self.add(card, T("A Job-Search Agent You Can Check", 46).move_to([1.1, 0.5, 0]), T("Varnika M", 40).move_to([1.1, -0.5, 0]))
        self.wait(0.3)
        G(self, Create(check(-4.55, -1.05, s=0.24)), rt=0.5)
        finish(self)
