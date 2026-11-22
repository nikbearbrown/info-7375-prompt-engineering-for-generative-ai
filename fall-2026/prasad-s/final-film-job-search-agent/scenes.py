# scenes.py — WorthLoop final project film (job-search-agent-film): 17 drawn Manim beats, B1-B17.
#
# What each beat shows follows SHOTLIST.md. The show-tell drawing kit (brutalist.art
# skills/make/show-tell/templates/iso_kit.py, toolkit revision 22264a3) is pasted below unchanged,
# as the skill says: Gate A copies only scenes.py, so the kit cannot be imported. Then this
# film's helpers (go/at/hold and friends from the pitch film's scenes.py), then one Scene per beat.
#
# Class names start with the beat id (B1_…, …, B17_…): run.sh slots each clip by the text
# before the first underscore, and the kit's pacing reads the beat's narration and measured
# audio (beat_sheet.json) by the same id. Every scene is built to its beat's actual_duration_s.
# Text sits at fixed coordinates (left-aligned with aligned_edge=LEFT), never placed from a
# measured text width: Gate A's stand-in for Manim overestimates widths.

"""
iso_kit.py — the show-tell drawing kit. PASTE this block at the top of a reel's scenes.py;
do not import it (Gate A copies only scenes.py into its sandbox).

Drawn isometric objects in the Claude palette: cardboard boxes (closed, open, taped), dark
MCP blocks with ports, flat skill pages, server stacks with lights, checks, a cursor, pills.
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


# ═════════════════════════════ WorthLoop helpers ═════════════════════════════
# Gate V samples each beat at 50% and 85%; GATE T samples at 50%. go() keeps every animation
# off those instants (it finishes before the window or starts after it), and hold() fills to
# the measured audio without running past it. go/at/hold are the pitch film's helpers.
import hashlib as _hashlib
import random as _random

DEEP_KRAFT = "#9C8462"   # cables and tracks (ink-edged connectors fuse into "text" under GATE T)
DIMTXT = "#6E6A60"       # dimmed but readable text, about 4.6:1 on the stage


def _bid(self):
    return type(self).__name__.split("_")[0]


def go(self, phrase, *anims, rt=0.6, lead=0.25):
    if phrase:
        until(self, phrase, lead)
    total = _TARGET.get(_bid(self), 0)
    if total:
        for frac, pad in ((0.5, 0.4), (0.85, 0.3)):
            t = _elapsed(self)
            lo, hi = total * frac - pad, total * frac + pad
            if t < hi and t + rt > lo:
                if lo - t >= 0.3:
                    rt = lo - t - 0.02        # fits before the window
                else:
                    self.wait(max(0.05, hi - t))  # start after it
        rt = max(0.2, min(rt, total - 0.1 - _elapsed(self)))
    self.play(*anims, run_time=rt)


def at(self, frac):
    """Wait until `frac` of the beat's measured audio (narration-independent timing)."""
    total = _TARGET.get(_bid(self), 0)
    if total:
        gap = total * frac - _elapsed(self)
        if gap > 0.05:
            self.wait(gap)


def hold(self):
    total = _TARGET.get(_bid(self), 0)
    rest = (total - _elapsed(self) - 0.06) if total else 1.5
    if rest > 0.05:
        self.wait(rest)


def tag(s):
    """The beat's label from SHOTLIST.md (ILLUSTRATION, CONSTRUCTED, PLANNED, FICTIONAL): top right, whole beat."""
    return T(s, 32, bold=True).move_to([6.0, 3.05, 0], aligned_edge=RIGHT)


PARTS = {**{b: "1 · What and why" for b in ("B2", "B3")},
         **{b: "2 · What others have done" for b in ("B4", "B5", "B6", "B7")},
         **{b: "3 · How I'm building it" for b in ("B8", "B9", "B10", "B11", "B12")},
         **{b: "4 · How I'll know it worked" for b in ("B13", "B14", "B15", "B16")}}


def part(self):
    """The small part label from SHOTLIST.md: top left, whole beat (every beat but B1 and B17)."""
    return T(PARTS[_bid(self)], 32).move_to([-6.0, 3.05, 0], aligned_edge=LEFT)


def lab(s, x, y, size=38, color=INK):
    return T(s, size, color).move_to([x, y, 0])


def lab_l(s, x, y, size=38, color=INK, bold=False):
    """Text whose left edge sits at x."""
    return T(s, size, color, bold).move_to([x, y, 0], aligned_edge=LEFT)


def src(s, x, y, left=False):
    """The small source line SHOTLIST.md asks for under a claim from a source."""
    return lab_l(s, x, y, 32) if left else lab(s, x, y, 32)


def cross(x, y, s=0.35, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def arrow(a, b, w=8, tip=0.12):
    return Arrow(a, b, buff=0, color=INK, stroke_width=w, max_tip_length_to_length_ratio=tip,
                 max_stroke_width_to_length_ratio=10)


def baseline(t, y, i=0):
    """Sit glyph i of t (one without a descender) on the line y, so words in one row share a baseline."""
    t.shift([0, y - t[i].get_bottom()[1], 0])
    return t


def on_base(iso, x0, y0, z0, w, d, h, pad=0.2, base_h=0.25):
    """A kraft box on a dark base (the base carries Gate V contrast)."""
    base = iso.box(x0 - pad, y0 - pad, z0, w + 2 * pad, d + 2 * pad, base_h, DARK_TOP, DARK_L, DARK_R)
    box = iso.box(x0, y0, z0 + base_h, w, d, h)
    return base, box


def slab(iso, x0, y0, z0, w, d, h, top=PAGE_TOP, left=PAGE_L, right=PAGE_R, stroke=BAR1, sw=1.5):
    """Iso.box with a chosen outline colour: thin grey for stacked paper."""
    x1, y1, z1 = x0 + w, y0 + d, z0 + h
    return VGroup(
        iso.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], left, stroke=stroke, sw=sw),
        iso.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], right, stroke=stroke, sw=sw),
        iso.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, stroke=stroke, sw=sw))


def card(w, h, x, y):
    """A pale card with a grey outline. Text may sit inside it; an ink outline around text reads as overlap."""
    return RoundedRectangle(width=w, height=h, corner_radius=0.15, fill_color=CARD, fill_opacity=1,
                            stroke_color=BAR1, stroke_width=3).move_to([x, y, 0])


def button(x, y, w=2.8, h=0.8):
    """The Approve button: a white pill with a grey outline. (A pale filled pill counts as low-contrast ink in Gate V.)"""
    return RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color="#FFFFFF", fill_opacity=1,
                            stroke_color=BAR1, stroke_width=3).move_to([x, y, 0])


def tray(iso, x0, y0, w=2.4, d=2.0, h=0.55):
    """The packet: a shallow kraft tray on a dark base. Returns (back, front); pages go between them."""
    base = iso.box(x0 - 0.25, y0 - 0.25, 0, w + 0.5, d + 0.5, 0.25, DARK_TOP, DARK_L, DARK_R)
    back, front = iso.open_box(x0, y0, 0.25, w, d, h)
    return VGroup(base, back), front


def laptop(x, y, s=1.0):
    """The film's laptop: a dark base and a dark screen with a pale face."""
    L = Iso(x, y, s)
    base = L.box(0, 0, 0, 2.0, 1.4, 0.12, DARK_TOP, DARK_L, DARK_R)
    screen = L.quad([(0, 1.4, 0.12), (2.0, 1.4, 0.12), (2.0, 1.4, 1.35), (0, 1.4, 1.35)], DARK_TOP)
    face = L.quad([(0.12, 1.4, 0.24), (1.88, 1.4, 0.24), (1.88, 1.4, 1.23), (0.12, 1.4, 1.23)], GHOST,
                  stroke=GHOST, sw=1)
    return VGroup(base, screen, face)


# B11's example packet (constructed). Its two fingerprints are the real SHA-256 of the packet's
# three lines joined with newlines, before and after one word changes, trimmed to 12 hex
# characters. They are computed here, never typed in.
PACKET_LINES = ("Posting: Product Analyst, New York",
                "Answer: I run A/B testing in SQL.",      # A/B testing, SQL and Python are all in Alex's profile
                "Evidence: title, level, place, years")
PACKET_A = "\n".join(PACKET_LINES)
PACKET_B = PACKET_A.replace("testing in SQL.", "testing in Python.")
FP_A = _hashlib.sha256(PACKET_A.encode("utf-8")).hexdigest()[:12]
FP_B = _hashlib.sha256(PACKET_B.encode("utf-8")).hexdigest()[:12]
_rng = _random.Random(7375)
SCRAMBLE = ["".join(_rng.choice("0123456789abcdef") for _ in range(12)) for _ in range(3)]   # the in-between frames only

# B15's traps and right answers, condensed from OUTLINE.md Part 4.
TRAPS = ("Staff PM posting → not a fit: over the level ceiling",
         "“prefers 5+ years”, fits otherwise → kept: “prefers” still invites fewer",
         "Engineering posting that only mentions PMs → not a fit",
         "Instructions hidden in a posting → ignored: verdict from facts only",
         "Empty board → reported as empty, never “no new jobs”")


# ═════════════════════════════ WorthLoop scenes, B1-B17 ═════════════════════════════
class B1_OpeningCard(Scene):
    def construct(self):
        # The opening card is B1's whole picture: title, tagline and the disclosure footer, from the first frame.
        title = T("WorthLoop", 120).move_to([0, 1.0, 0])
        tagline = T("Worth your time, or it doesn't make the loop.", 44).move_to([0, -0.85, 0])
        footer = T("Voice: synthetic (Kokoro) · Script: Prasad Shinde", 32).move_to([0, -2.9, 0])
        rule = Line([-3.6, -0.15, 0], [3.6, -0.15, 0], color=INK, stroke_width=5)
        spark = Dot([3.6, -0.15, 0], radius=0.1, color=TERRA)
        self.add(title, tagline, footer)
        go(self, None, Create(rule), rt=0.6)
        go(self, None, FadeIn(spark), rt=0.3)
        hold(self)


class B2_Packet(Scene):
    def construct(self):
        self.add(part(self), tag("ILLUSTRATION"))
        P = Iso(-4.7, -0.3, 1.0)
        plinth = P.box(-0.2, -0.2, -0.25, 1.6, 1.9, 0.25, DARK_TOP, DARK_L, DARK_R)
        posting = P.page(0, 0, 0, 1.2, 1.5)
        posting.set_z_index(1)
        posting_lab = lab("posting", -4.75, -1.2, 36)
        Bx = Iso(0.4, -2.3, 1.0)
        tray_back, tray_front = tray(Bx, 0, 0)
        answers = Bx.page(0.55, 0.35, 0.37, 1.2, 1.0)
        why = Bx.page(0.95, 0.6, 0.43, 1.2, 1.0)
        for pg in (answers, why):
            pg.set_z_index(1)
        names = [lab_l(s, 3.3, y, 36) for s, y in (("posting", 0.35), ("answers", -0.35), ("why it fits", -1.05))]
        path = ArcBetweenPoints(np.array(posting.get_center()), np.array(Bx.p(1.0, 0.95, 0.31)), angle=-PI / 3)
        btn = button(-4.5, 0.2)
        approve = lab("Approve", -4.5, 0.2, 40)
        approved = lab("Approved", -4.5, 0.2, 40)
        tap = cursor(-3.55, -0.05, 0.5)
        stamp = T("Never submits", 44, bold=True).move_to([-4.5, -1.6, 0])
        rules = VGroup(Line([-6.2, -1.15, 0], [-2.8, -1.15, 0], color=INK, stroke_width=6),
                       Line([-6.2, -2.05, 0], [-2.8, -2.05, 0], color=INK, stroke_width=6))

        go(self, None, FadeIn(plinth), FadeIn(posting), FadeIn(posting_lab), rt=0.5)
        go(self, "drafts a packet", FadeIn(VGroup(tray_back, tray_front), shift=UP * 0.2), rt=0.5)
        go(self, "the posting", MoveAlongPath(posting, path), FadeOut(posting_lab), FadeOut(plinth),
           FadeIn(names[0]), rt=0.7)
        go(self, "the answers", FadeIn(answers, shift=DOWN * 0.8), FadeIn(names[1]), rt=0.45)
        go(self, "why it fits", FadeIn(why, shift=DOWN * 0.8), FadeIn(names[2]), rt=0.45)
        go(self, "The person approves", FadeIn(btn), FadeIn(approve), rt=0.4)
        go(self, None, FadeIn(tap, shift=LEFT * 0.4), rt=0.35)
        go(self, None, VGroup(btn, approve).animate.scale(0.9), rt=0.15)                 # the click presses it in
        go(self, None, btn.animate.scale(1 / 0.9).set_fill(TERRA, 1).set_stroke(TERRA), ReplacementTransform(approve, approved),
           rt=0.3)                                                                         # accent fill, "Approved"
        go(self, "WorthLoop never", Create(rules), FadeIn(stamp), rt=0.5, lead=0.4)
        hold(self)


class B3_Flood(Scene):
    def construct(self):
        J = Iso(-4.7, -0.5, 0.9)
        ad = VGroup(J.box(-0.2, -0.2, -0.25, 1.5, 1.8, 0.25, DARK_TOP, DARK_L, DARK_R), J.page(0, 0, 0, 1.1, 1.4))
        Pl = Iso(-1.3, -2.5, 0.9)
        plinth = Pl.box(-0.2, -0.2, -0.25, 1.9, 1.6, 0.25, DARK_TOP, DARK_L, DARK_R)
        rng = _random.Random(254)
        pages = [slab(Pl, rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0.08 * i, 1.5, 1.2, 0.05)
                 for i in range(16)]
        source = src("Greenhouse, via Fortune, Jul 2026", 3.35, -1.3)
        label = lab("applicants per job ad", 3.35, -0.4, 40)
        values = (12, 40, 75, 110, 150, 190, 222, 245, 254)
        nums = [lab(f"≈{v}", 3.35, 0.75, 120) for v in values]
        title = lab("Why it matters", 0, 2.45, 48)

        self.add(part(self), title)
        go(self, None, FadeIn(ad), rt=0.5)
        go(self, "Hiring is flooded", FadeIn(plinth), *[FadeIn(p, shift=DOWN * 0.4) for p in pages[:2]], rt=0.5)
        go(self, "In July 2026", FadeIn(source), rt=0.4)
        go(self, "about 254", FadeIn(nums[0]), FadeIn(label), FadeIn(pages[2], shift=DOWN * 0.4), rt=0.2)
        for i in range(1, len(values)):
            go(self, None, ReplacementTransform(nums[i - 1], nums[i]), FadeIn(pages[2 + i], shift=DOWN * 0.4), rt=0.15)
        go(self, "employers drown", LaggedStart(*[FadeIn(p, shift=DOWN * 0.5) for p in pages[11:]], lag_ratio=0.25), rt=0.8)
        hold(self)


class B4_ApplyTools(Scene):
    def construct(self):
        head = lab_l("Group 1 · Tools that apply for you", -6.0, 2.35, 44)
        form = card(5.6, 3.9, -3.0, -0.35)
        ys = (0.85, -0.25, -1.35)
        names = VGroup(*[lab_l(s, -5.45, y, 36) for s, y in zip(("name", "email", "experience"), ys)])
        slots = VGroup(*[Rectangle(width=2.3, height=0.55, fill_color="#FFFFFF", fill_opacity=1, stroke_color=BAR1,
                                   stroke_width=3).move_to([-1.55, y, 0]) for y in ys])
        vals = [Rectangle(width=w, height=0.2, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-2.55 + w / 2, y, 0])
                for w, y in zip((1.9, 0.7, 1.4), ys)]
        marks = [cross(0.25, y, s=0.17, w=7) for y in ys]
        info = lab_l("wrong info", 1.2, 0.85, 40)
        fields = lab_l("wrong fields", 1.2, -0.25, 40)
        quote = lab_l("“snake oil”", 1.2, -1.15, 56)
        gloss = [lab_l("snake oil: a product sold on", 1.2, -1.85, 32), lab_l("promises it can't keep", 1.2, -2.3, 32)]
        source = src("Washington Post, Mar 2026", 1.2, -2.95, left=True)

        self.add(part(self), tag("ILLUSTRATION"), head)       # the form is made up
        go(self, "Employers say", FadeIn(form), FadeIn(names), FadeIn(slots), rt=0.5)
        go(self, "wrong information", *[FadeIn(v, shift=DOWN * 0.5) for v in vals], FadeIn(info), rt=0.5)
        go(self, "wrong fields", *[Create(m) for m in marks], FadeIn(fields), rt=0.5)
        go(self, "One company", FadeIn(quote), *[FadeIn(g) for g in gloss], FadeIn(source), rt=0.5)
        hold(self)


class B5_Funnel(Scene):
    def construct(self):
        head = lab_l("Group 2 · Open-source agents", -6.0, 2.35, 44)
        ys = (1.4, 0.4, -0.6, -1.6)
        bars = [Rectangle(width=w, height=0.62, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-1.6, y, 0])
                for w, y in zip((7.0, 4.6, 2.6, 1.0), ys)]                      # not to scale: a funnel
        names = [lab_l(s, 2.5, y, 36) for s, y in zip(("740 listings", "68 applications", "12 interviews", "1 offer"), ys)]
        source = src("career-ops README", 2.5, -2.6, left=True)
        note = lab("bars not to scale", -1.6, -2.6, 32)

        self.add(part(self), head)
        go(self, "One checked", GrowFromCenter(bars[0]), FadeIn(names[0]), FadeIn(source), FadeIn(note), rt=0.5)
        go(self, "68", ReplacementTransform(bars[0].copy(), bars[1]), FadeIn(names[1]), rt=0.5)
        # "1 offer" comes in with "12 interviews" so it stays readable; both land before Gate V's 85% sample.
        until(self, "12 interviews", 0.3)
        self.play(ReplacementTransform(bars[1].copy(), bars[2]), FadeIn(names[2]), run_time=0.25)
        self.play(ReplacementTransform(bars[2].copy(), bars[3]), FadeIn(names[3]), run_time=0.2)
        hold(self)


class B6_PaymentChecks(Scene):
    def construct(self):
        head = lab_l("Group 3 · Approval checks from AI payments", -6.0, 2.35, 44)
        # AP2's rule, paraphrased: no quote marks (decided 2026-11-22).
        rule1 = lab_l("AP2 (v0.2): the approval screen must be non-agentic —", -5.6, 1.55, 36)
        rule2 = baseline(lab_l("plain code, not AI", -5.6, 0.85, 36), 0.85, 1)
        source = baseline(src("AP2 specification v0.2", 1.6, 0.85, left=True), 0.85)
        A1, A2 = Iso(-4.6, -1.25, 0.6), Iso(-1.4, -1.25, 0.6)
        asked = VGroup(*on_base(A1, 0, 0, 0, 1.1, 1.1, 1.0, pad=0.15, base_h=0.2))
        shield = VGroup(*on_base(A2, 0, 0, 0, 1.1, 1.1, 1.0, pad=0.15, base_h=0.2))
        n1, n2 = lab("AsAsked", -4.6, -1.8, 36), lab("Mandate Shield", -1.4, -1.8, 36)
        pitch = lab_l("Oct: payments pitch", -5.55, -2.85, 38)
        link = arrow([-1.3, -2.85, 0], [0.1, -2.85, 0])
        jobs = lab_l("job applications", 0.35, -2.85, 38)

        self.add(part(self), head)
        go(self, "One standard", FadeIn(rule1), FadeIn(rule2), FadeIn(source), rt=0.5)
        go(self, "In October", FadeIn(pitch), rt=0.4)
        go(self, "others built", FadeIn(asked, shift=DOWN * 0.3), FadeIn(n1), FadeIn(shield, shift=DOWN * 0.3),
           FadeIn(n2), rt=0.6)
        go(self, "so I carried", GrowArrow(link), FadeIn(jobs), rt=0.5)
        hold(self)


class B7_NotFound(Scene):
    def construct(self):
        ys = (2.35, 1.7)
        misses = [lab_l(s, -5.55, y, 38) for s, y in zip(("Not found: a test locked before tuning",
                                                           "Not found: approval tied to the exact packet"), ys)]
        marks = [cross(-6.0, y, s=0.16, w=6) for y in ys]
        track = Line([-5.6, -1.1, 0], [5.6, -1.1, 0], color=DEEP_KRAFT, stroke_width=6)
        F = Iso(-0.35, -0.9, 0.85)
        fbase, fbox = on_base(F, 0, 0, 0, 1.2, 1.2, 1.0, pad=0.15, base_h=0.2)
        light = Dot(F.p(0.3, 0, 0.75), radius=0.09, color=GHOST)            # stays unlit: nothing kept
        filt = lab_l("filter", 0.95, 0.2, 36)
        posting = Iso(-4.9, -1.6, 0.8).page(0, 0, 0, 1.0, 1.2)             # the worth-it posting
        posting.set_z_index(3)
        line_a = lab("My last test: missed the one worth-it posting —", 0, -2.05, 36)
        line_b = lab("read ‘prefers 5+ years’ as a rule", 0, -2.6, 36)
        source = src("JS3 held-out test · MEASURE.md", 0, -3.12)

        self.add(part(self))
        go(self, "a test locked", Create(marks[0]), FadeIn(misses[0]), rt=0.4)
        go(self, "or approval tied", Create(marks[1]), FadeIn(misses[1]), rt=0.4)
        go(self, "My last test", Create(track), FadeIn(VGroup(fbase, fbox, light)), FadeIn(filt), FadeIn(posting),
           FadeIn(line_a), FadeIn(source), rt=0.5)
        go(self, "missed the one", posting.animate.shift(RIGHT * 9.4), rt=1.0)
        go(self, "reading", FadeIn(line_b), rt=0.4)
        hold(self)


class B8_Alex(Scene):
    def construct(self):
        self.add(part(self), tag("FICTIONAL"))
        person = card(4.2, 4.4, -3.6, -0.3)
        head = Circle(radius=0.5, fill_color=BAR2, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.6, 0.85, 0])
        body = RoundedRectangle(width=2.0, height=1.0, corner_radius=0.45, fill_color=BAR2, fill_opacity=1,
                                stroke_color=INK, stroke_width=4).move_to([-3.6, -0.3, 0])
        name = lab("Alex Rivera", -3.6, -1.45, 44)
        rows = (("Stripe", 0.95), ("Robinhood", 0.2), ("Duolingo", -0.55), ("Notion", -2.05))
        gh = lab_l("Greenhouse", 0.4, 1.75, 38, bold=True)
        ab = lab_l("Ashby", 0.4, -1.3, 38, bold=True)
        blocks = [Iso(1.15, y - 0.25, 0.42).box(0, 0, 0, 0.8, 0.8, 0.55) for _, y in rows]
        boards = [lab_l(s, 2.0, y, 36) for s, y in rows]

        go(self, "Alex Rivera", FadeIn(person), FadeIn(head), FadeIn(body), FadeIn(name), rt=0.5)
        go(self, "It reads", FadeIn(gh), FadeIn(ab), LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in blocks], lag_ratio=0.2),
           *[FadeIn(t) for t in boards], rt=0.6)
        hold(self)


class B9_Evidence(Scene):
    def construct(self):
        self.add(part(self), tag("CONSTRUCTED"))
        ev = card(6.4, 4.4, -2.6, -0.25)
        title = lab_l("Evidence", -5.4, 1.4, 40, bold=True)
        # Laid out by condition, with no condition ids on screen: Title, Place, then Level with Years beneath it.
        rows = {"title": lab_l("Title", -5.4, 0.6), "place": lab_l("Place", -5.4, -0.15),
                "level": lab_l("Level", -5.4, -0.9), "years": lab_l("Years", -4.8, -1.65)}
        ticks = {k: check(-0.35, y, s=0.22, color=INK, w=8)
                 for k, y in (("title", 0.6), ("place", -0.15), ("level", -0.9), ("years", -1.65))}
        Pk = Iso(2.6, -1.55, 0.8)
        pk_back, pk_front = tray(Pk, 0, 0, w=2.2, d=1.8, h=0.5)
        pages = [Pk.page(0.3 + 0.3 * i, 0.25 + 0.2 * i, 0.31 + 0.06 * i, 1.1, 0.9) for i in range(3)]
        for pg in pages:
            pg.set_z_index(1)
        link = arrow([0.85, 0.85, 0], [1.75, 0.5, 0], tip=0.3)
        pk_lab = lab("packet (planned)", 2.75, -2.35, 38)

        go(self, None, FadeIn(ev), FadeIn(title), rt=0.5)
        go(self, "title fits", FadeIn(rows["title"]), Create(ticks["title"]), rt=0.4)
        go(self, "level fits", FadeIn(rows["level"]), Create(ticks["level"]), rt=0.4)
        go(self, "place fits", FadeIn(rows["place"]), Create(ticks["place"]), rt=0.4)
        go(self, "years fit", FadeIn(rows["years"]), Create(ticks["years"]), rt=0.4)
        go(self, "It will become", GrowArrow(link), FadeIn(VGroup(pk_back, pk_front)), FadeIn(pk_lab), rt=0.5)
        go(self, "the posting, draft", FadeIn(pages[0], shift=DOWN * 0.6), rt=0.35)
        go(self, "draft answers", FadeIn(pages[1], shift=DOWN * 0.6), rt=0.35)
        go(self, "and the evidence", FadeIn(pages[2], shift=DOWN * 0.6), rt=0.35)
        hold(self)


class B10_Plug(Scene):
    def construct(self):
        C, S = Iso(-5.0, -0.75, 0.7), Iso(3.4, -0.8, 0.7)
        claude = VGroup(*on_base(C, 0, 0, 0, 1.4, 1.4, 1.2, pad=0.15, base_h=0.2))
        scorer = VGroup(*on_base(S, 0, 0, 0, 1.5, 1.5, 1.2, pad=0.15, base_h=0.2))
        socket = Rectangle(width=0.3, height=0.7, fill_color=DARK_R, fill_opacity=1, stroke_width=0).move_to([2.05, 0.1, 0])
        lamp = Dot(S.p(0.35, 0, 1.0), radius=0.09, color=TERRA)              # lights when the plug connects
        c_lab, s_lab = lab("Claude", -5.0, -1.6, 40), lab("scorer", 3.4, -1.65, 40)
        body = RoundedRectangle(width=1.3, height=0.8, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1,
                                stroke_width=0).move_to([-0.95, 0.1, 0])
        prongs = VGroup(*[Rectangle(width=0.42, height=0.12, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0)
                          .move_to([-0.09, 0.1 + dy, 0]) for dy in (0.18, -0.18)])
        plug = VGroup(body, prongs)
        cable = Line([-3.95, 0.1, 0], [-1.7, 0.1, 0], color=DEEP_KRAFT, stroke_width=8)
        cable_end = Line([-3.95, 0.1, 0], [0.05, 0.1, 0], color=DEEP_KRAFT, stroke_width=8)
        p_lab = lab("plug (MCP)", -0.2, -0.85, 38)
        rules = Iso(-1.2, 1.25, 0.7).page(0, 0, 0, 1.1, 1.4)
        r_lab = lab_l("rules in code", -0.2, 1.75, 38)
        chips = [VGroup(pill(-1.4, -2.6, 3.0, fill=BAR3), lab("10 requests", -1.4, -2.6, 38)),
                 VGroup(pill(1.7, -2.6, 1.6, fill=BAR3), lab("60 s", 1.7, -2.6, 38))]

        self.add(part(self))
        go(self, None, FadeIn(claude), FadeIn(c_lab), rt=0.5)
        go(self, "the scorer", FadeIn(scorer), FadeIn(socket), FadeIn(s_lab), rt=0.4)
        go(self, "through a standard plug", FadeIn(plug), Create(cable), FadeIn(p_lab), rt=0.35)
        go(self, None, plug.animate.shift(RIGHT * 1.75), Transform(cable, cable_end), rt=0.5)
        go(self, None, FadeIn(lamp, scale=0.5), rt=0.25)
        go(self, "Rules in the code", FadeIn(rules), FadeIn(r_lab), rt=0.4)
        go(self, "ten requests", FadeIn(chips[0]), rt=0.35)
        go(self, "sixty seconds", FadeIn(chips[1]), rt=0.35)
        hold(self)


class B11_Fingerprint(Scene):
    def construct(self):
        self.add(part(self), tag("PLANNED"))
        btn = button(-3.9, -1.25)
        approve = lab("Approve", -3.9, -1.25, 40)
        caption = lab("Approve = plain code; the AI can't press it.", -1.6, -2.4, 36)
        pk = card(7.3, 2.45, -2.5, 1.35)
        lines = [lab_l(s, -5.85, y, 34) for s, y in zip(PACKET_LINES, (2.0, 1.35, 0.7))]
        changed = lab_l(PACKET_B.split("\n")[1], -5.85, 1.35, 34)
        changed.shift(np.array(lines[1][0].get_center()) - np.array(changed[0].get_center()))   # same baseline
        for m in (*lines, changed):
            m.set_z_index(2)
        old_word, new_word = VGroup(*lines[1][-4:]), VGroup(*changed[-7:])      # "SQL." -> "Python."
        mark = SurroundingRectangle(old_word, buff=0.07, fill_color=BAR3, fill_opacity=1, stroke_width=0,
                                    stroke_opacity=0).set_z_index(1)
        mark_new = SurroundingRectangle(new_word, buff=0.07, fill_color=BAR3, fill_opacity=1, stroke_width=0,
                                        stroke_opacity=0).set_z_index(1)
        link = arrow([1.35, 1.35, 0], [2.1, 1.35, 0], tip=0.35)
        fp_box = card(3.9, 0.95, 4.15, 1.35)
        fp_lab = lab("fingerprint", 4.15, 2.25, 38)
        prints = [Text(s, font="Menlo", color=INK, font_size=36).move_to([4.15, 1.35, 0]).set_z_index(2)
                  for s in (FP_A, *SCRAMBLE, FP_B)]

        go(self, None, FadeIn(btn), FadeIn(approve), rt=0.5)
        go(self, "plain code", FadeIn(caption), rt=0.4)
        go(self, "The approval will be tied", FadeIn(pk), *[FadeIn(m) for m in lines], rt=0.5)
        go(self, "fingerprint of the packet", GrowArrow(link), FadeIn(fp_box), FadeIn(fp_lab), FadeIn(prints[0]), rt=0.5)
        go(self, "change one word", FadeIn(mark), rt=0.3)
        go(self, None, FadeOut(old_word), FadeIn(new_word), Transform(mark, mark_new), rt=0.4)
        go(self, "and the fingerprint changes", ReplacementTransform(prints[0], prints[1]), rt=0.15)
        for i in range(2, len(prints)):
            go(self, None, ReplacementTransform(prints[i - 1], prints[i]), rt=0.15)
        hold(self)


class B12_Laptop(Scene):
    def construct(self):
        lap = laptop(-0.95, 0.45, 0.85)
        y = -0.4                                                     # the row's baseline
        words = {"laptop": baseline(lab_l("Laptop", -5.61, y, 36), y), "free": baseline(lab_l("free tools", -3.67, y, 36), y),
                 "credits": baseline(lab_l("no paid credits", -1.43, y, 36), y),
                 "claude": baseline(lab_l("Claude via university", 1.81, y, 36), y)}
        dots = [Dot([x, y + 0.11, 0], radius=0.05, color=INK) for x in (-3.95, -1.71, 1.53)]
        built = lab_l("Built", -5.4, -1.2, 40, bold=True)
        b_items = [(lab_l(s, -4.7, yy, 38), check(-5.15, yy, s=0.2, color=INK, w=7))
                   for s, yy in (("watcher", -1.85), ("filter", -2.45), ("scorer", -3.05))]
        nxt = lab_l("Next", 1.0, -1.2, 40, bold=True)
        n_items = [(lab_l(s, 1.7, yy, 38), Square(side_length=0.36, fill_opacity=0, stroke_color=INK, stroke_width=4)
                    .move_to([1.3, yy, 0])) for s, yy in (("packet", -1.85), ("gate", -2.45))]

        self.add(part(self))
        go(self, "my laptop", FadeIn(lap), FadeIn(words["laptop"]), rt=0.4)
        go(self, "free tools", FadeIn(dots[0]), FadeIn(words["free"]), rt=0.3)
        go(self, "no paid credits", FadeIn(dots[1]), FadeIn(words["credits"]), rt=0.3)
        go(self, "Claude comes", FadeIn(dots[2]), FadeIn(words["claude"]), rt=0.35)
        go(self, "Built so far", FadeIn(built), rt=0.3)
        for (text, tick), cue in zip(b_items, ("the watcher", "the filter", "the scorer")):
            go(self, cue, FadeIn(text), Create(tick), rt=0.3)
        # "Next: packet, gate" comes in right after "the scorer", so it stays on screen for at least 1.5 s.
        go(self, None, FadeIn(nxt), *[FadeIn(m) for pair in n_items for m in pair], rt=0.35)
        hold(self)


class B13_Locked(Scene):
    def construct(self):
        S = Iso(-4.3, -1.6, 1.0)
        base, box = on_base(S, 0, 0, 0, 1.8, 1.6, 1.5)
        seal = S.tape(0, 0, 1.75, 1.8, 1.6, drop=0.35)
        lock = RoundedRectangle(width=0.95, height=0.8, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1,
                                stroke_color=INK, stroke_width=4).move_to([-3.45, -0.75, 0])
        keyhole = Dot([-3.45, -0.72, 0], radius=0.09, color=GHOST)
        shackle_open = Arc(radius=0.3, start_angle=0, angle=PI, color=INK, stroke_width=12).move_to([-3.45, 0.05, 0])
        shackle_shut = Arc(radius=0.3, start_angle=0, angle=PI, color=INK, stroke_width=12).move_to([-3.45, -0.2, 0])
        l1 = lab_l("20 postings, sealed Nov 15", -1.4, 1.1, 40)
        l2 = lab_l("≈1 in 30 worth it", -1.4, -0.1, 40)
        l3 = lab_l("likely 0 or 1; exact count reported", -1.4, -1.3, 40)

        self.add(part(self))
        go(self, None, FadeIn(base), FadeIn(box), FadeIn(lock), FadeIn(keyhole), FadeIn(shackle_open), FadeIn(l1), rt=0.4)
        go(self, "locked", FadeOut(shackle_open), FadeIn(shackle_shut, shift=DOWN * 0.25), FadeIn(seal), rt=0.4)
        go(self, "about one in thirty", FadeIn(l2), rt=0.4)
        go(self, "none, or one", FadeIn(l3), rt=0.4)
        hold(self)


class B14_Checks(Scene):
    def construct(self):
        items = (("misses none", "misses none"), ("keeps at most two of the rest", "keeps at most two"),
                 ("every claim matches Alex's profile", "every claim"), ("every fingerprint matches", "every fingerprint"),
                 ("all five traps handled", "all five traps"))
        self.add(part(self))
        for (text, cue), y in zip(items, (2.3, 1.4, 0.5, -0.4, -1.3)):
            box = Square(side_length=0.5, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-5.3, y, 0])
            go(self, cue, FadeIn(box), FadeIn(lab_l(text, -4.75, y, 40)), Create(check(-5.33, y, s=0.2, color=INK, w=7)), rt=0.45)
        verdict = lab("any one fails → it didn't work", 0, -2.6, 44)
        go(self, "One failure", FadeIn(verdict), rt=0.4)
        hold(self)


class B15_Traps(Scene):
    def construct(self):
        ys = (2.0, 1.0, 0.0, -1.0, -2.0)
        rows = [lab_l(s, -5.75, y, 32) for s, y in zip(TRAPS, ys)]
        marks = [Dot([-6.05, y, 0], radius=0.1, color=TERRA) for y in ys[:2]]       # the two spoken traps

        self.add(part(self))
        go(self, None, LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.15), rt=0.9)
        go(self, "Two:", *[r.animate.set_color(DIMTXT) for r in rows[2:]], rt=0.5)
        go(self, "a Staff title", FadeIn(marks[0], scale=0.5), rt=0.3)
        go(self, 'And "prefers', FadeIn(marks[1], scale=0.5), rt=0.3)
        hold(self)


class B16_Controlled(Scene):
    def construct(self):
        self.add(part(self), tag("PLANNED"))
        xs = (-5.0, -2.5, 0.0, 2.5, 5.0)
        names = ("predict", "change packet", "caught", "refused", "re-approve")
        cues = ("I write the expected", "Then I change", "A separate check", "refuse it", "make me approve")
        nodes = [Circle(radius=0.38, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, 1.1, 0])
                 for x in xs]
        lights = [Dot([x, 1.1, 0], radius=0.24, color=TERRA) for x in xs]
        labels = [baseline(lab(s, x, 0.2, 36, DIMTXT), 0.07, 1 if s == "predict" else 0) for s, x in zip(names, xs)]
        links = [arrow([xs[i] + 0.55, 1.1, 0], [xs[i + 1] - 0.55, 1.1, 0], w=6) for i in range(4)]
        lap = laptop(-5.6, -2.55, 0.55)
        stranger = lab_l("Stranger run: clean machine", -3.6, -1.95, 40)

        self.add(*nodes, *labels)
        for i, cue in enumerate(cues):
            anims = [FadeIn(lights[i], scale=0.5), labels[i].animate.set_color(INK)]
            if i:
                anims.append(GrowArrow(links[i - 1]))
            go(self, cue, *anims, rt=0.45)
        go(self, "Last, someone", FadeIn(lap), FadeIn(stranger), rt=0.5)
        hold(self)


class B17_End(Scene):
    def construct(self):
        end = lab("WorthLoop · INFO 7375 Final Project Film · Nov 2026", 0, 0.35, 40)
        rule = Line([-3.6, -0.45, 0], [3.6, -0.45, 0], color=INK, stroke_width=5)
        spark = Dot([3.6, -0.45, 0], radius=0.1, color=TERRA)
        black = Rectangle(width=15.0, height=8.6, fill_color="#000000", fill_opacity=1, stroke_width=0,
                          stroke_opacity=0).move_to([0, 0, 0])
        black.set_z_index(10)

        self.add(end)
        go(self, None, Create(rule), rt=0.6)
        go(self, None, FadeIn(spark), rt=0.3)
        total = _TARGET.get(_bid(self), 0)
        if total:
            at(self, (total - 1.65) / total)          # a slow fade over about the last 1.6 s
            rt = max(0.5, total - 0.06 - _elapsed(self))
        else:
            rt = 1.6
        self.play(FadeIn(black), run_time=rt)
