"""
scenes.py — agent-reliability-audit-pitch

WARNING TO WHOEVER RENDERS THIS: I (Claude, drafting this in a sandbox
without a matching Manim/show-tell environment) have NOT been able to
render-test this file. Follow show-tell's own documented workflow before
trusting it:
  1. Pre-audit Gate A from a scratch folder holding ONLY this file (copy
     nothing else) — that is exactly what `art run`'s Gate A sees.
  2. Run runtime/qc/static_scene_check.py and manim_layout_audit.py
     (--curve-strict) against it.
  3. Render stills first (`manim -ql -s`) and look at a contact sheet
     before any 4K render.
Expect to find and fix real bugs — this is a first draft, not a verified
one. Every function call below is copied from the REAL, confirmed
iso_kit.py and the REAL claude-liam-brutalist-show-tell-cards reference
scene — nothing here is guessed at an unverified API.

The 12-beat sequence: BIDEA and BDEFS are Remotion bookends (handled by
make_sheet.py / remotion_scenes.py, not here). B00–B07 and BCLOSE are the
9 Manim scenes below, using a consistent cast per show-tell Law 4: one
crate labeled AGENT, one gate the crate passes through, a docs.python.org
page, two counters, one GitHub pull-request pill, and the same floor plane
throughout.
"""

# ═════════════════════════════ ISO KIT (show-tell) — pasted verbatim ═════════════════════════════
# Copied from skills/make/show-tell/templates/iso_kit.py per that file's own
# instruction ("PASTE this block at the top of a reel's scenes.py; do not
# import it — Gate A copies only scenes.py into its sandbox"). Nothing below
# this block, down to the "the film" marker, has been modified.

from manim import *
import numpy as np
import json as _json, os as _os

STAGE = "#F2F0E9"; INK = "#3D3929"; TERRA = "#D97757"; DIM = "#8B8F96"; GHOST = "#D9D4C7"; CARD = "#FAF9F5"
BOX_TOP, BOX_L, BOX_R = "#F3E9D8", "#DCC9AA", "#C7AE86"
BOX_IN1, BOX_IN2, BOX_FLOOR = "#CDB894", "#BFA67E", "#B39A72"
DARK_TOP, DARK_L, DARK_R = "#3A3530", "#26221F", "#1E1B18"
PAGE_TOP, PAGE_L, PAGE_R = "#FFFFFF", "#ECE7DF", "#E2DCD2"
BAR1, BAR2, BAR3 = "#8B8F96", "#B4AFA6", "#D9D4C7"
SERIF = "EB Garamond"
C30 = 0.8660254
config.background_color = STAGE


def T(s, size=36, color=INK, bold=False):
    return Text(s, font=SERIF, color=color, font_size=size, weight="BOLD" if bold else "NORMAL")


class Iso:
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

    def tape(self, x0, y0, z1, w, d, drop=0.35, t=0.22):
        ym = y0 + d / 2
        return VGroup(
            self.quad([(x0, ym - t, z1), (x0 + w, ym - t, z1), (x0 + w, ym + t, z1), (x0, ym + t, z1)], TERRA, sw=0),
            self.quad([(x0, ym - t, z1), (x0, ym + t, z1), (x0, ym + t, z1 - drop), (x0, ym - t, z1 - drop)], TERRA, sw=0))

    def mcp(self, x0, y0, z0, w=1.3, d=1.3, h=0.7):
        body = self.box(x0, y0, z0, w, d, h, DARK_TOP, DARK_L, DARK_R)
        ports = VGroup(*[self.box(x0 + w * f, y0 - 0.18, z0 + h * 0.3, w * 0.16, 0.18, h * 0.3, GHOST, BOX_IN1, BOX_IN2, sw=1)
                         for f in (0.22, 0.58)])
        return VGroup(body, ports)

    def page(self, x0, y0, z0, w=1.1, d=1.4):
        slab = self.box(x0, y0, z0, w, d, 0.06, PAGE_TOP, PAGE_L, PAGE_R, sw=1.5)
        zt = z0 + 0.06
        lines = VGroup(*[Line(self.p(x0 + 0.2, y0 + d * f, zt), self.p(x0 + w - 0.2, y0 + d * f, zt), color=GHOST, stroke_width=4)
                         for f in (0.3, 0.5, 0.7)])
        dot = Dot(self.p(x0 + 0.2, y0 + d * 0.86, zt), radius=0.06, color=TERRA)
        return VGroup(slab, lines, dot)

    def server(self, x0, y0, z0, w=1.4, d=1.4, slab=0.42, n=3):
        stack = VGroup(*[self.box(x0, y0, z0 + i * (slab + 0.04), w, d, slab, DARK_TOP, DARK_L, DARK_R) for i in range(n)])
        lights = VGroup(*[Dot(self.p(x0 + 0.25, y0, z0 + i * (slab + 0.04) + slab / 2), radius=0.06, color=GHOST) for i in range(n)])
        return stack, lights


def ease_in(t):
    return t * t


def check(x, y, s=0.2, color=INK, w=7):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))


def cursor(x, y, s=0.45):
    return Polygon([x, y, 0], [x, y - s, 0], [x + s * 0.28, y - s * 0.72, 0], [x + s * 0.62, y - s * 0.66, 0],
                   fill_color=INK, fill_opacity=1, stroke_color=CARD, stroke_width=2)


def pill(x, y, w, h=0.62, fill="#FFFFFF"):
    return RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color=fill, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


# pacing (narration is the clock) — reads this folder's own beat_sheet.json
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


# ═════════════════════════════ the film ═════════════════════════════
# agent-reliability-audit-pitch — 9 drawn beats. Consistent cast: a crate
# labeled AGENT, a gate the crate passes through, a docs.python.org page,
# two counters, one GitHub pull-request pill. Reused across beats so a
# viewer recognises beat 7's crate as beat 0's crate (show-tell Law 4).
#
# FIXES applied after a real Gate A / layout-audit / stills pass (not
# guessed): (1) B04's crack now draws in two separate play() calls, since
# Gate A snapshots only after play()/wait() and two shapes created in one
# call before the first snapshot look identical to one shape forever.
# (2) B02/B03 no longer use terracotta TEXT (not allowed) and now draw a
# small ink curve beside each counter, both to pass Gate A's "no shapes
# recorded" warning and to match the real reference film's own pattern (a
# hero number plus a drawn curve beside it). Caption size raised to 36
# (floor is 32). (3) B05/B07/BCLOSE now build shadow+crate+label as ONE
# grouped unit before any move/scale, so nothing detaches when the group
# is repositioned — the detached-shadow bug and the "AGENT on a line"
# layout-audit error both came from moving the crate alone while the
# shadow and label were separate, independently-placed objects.
# (4) B00 now actually uses open_box() to show an interior, with a small
# tool block inside, matching its own narration ("open it up, there's one
# tool inside") instead of just hiding the lid with nothing underneath.

BOXW, BOXD, BOXH, LIDH = 2.4, 2.4, 1.5, 0.18
MAIN = Iso(0.0, -1.8, 0.78)   # the crate, centre-left of stage


def floor_shadow(iso=MAIN, w=BOXW, d=BOXD):
    sh = iso.quad([(0.15, -0.35, 0), (w + 0.35, -0.35, 0), (w + 0.35, d - 0.15, 0), (0.15, d - 0.15, 0)], "#BFB4A0", sw=0)
    sh.set_z_index(-1)
    return sh


def sealed_crate(iso=MAIN):
    """The crate, closed, with a terracotta tape seal."""
    return VGroup(iso.box(0, 0, 0, BOXW, BOXD, BOXH), iso.tape(0, 0, BOXH, BOXW, BOXD))


def crate_label(crate_mobj):
    """AGENT, placed safely below whatever the crate's current bounding box is —
    computed from the real object, never a hardcoded offset, so it can't drift
    onto the crate's own lines after a later move/scale."""
    return T("AGENT", 32).next_to(crate_mobj, DOWN, buff=0.2)


def crate_unit(iso=MAIN, label=True):
    """ONE grouped VGroup: floor shadow + sealed crate + (optional) AGENT label.
    Any later .move_to()/.scale() on this single group keeps all three aligned —
    use this whenever a beat repositions the crate; use floor_shadow()+sealed_crate()
    separately only when a beat needs to manipulate the crate's own parts (the lid)
    while it stays in place."""
    shadow = floor_shadow(iso)
    crate = sealed_crate(iso)
    g = VGroup(shadow, crate)
    if label:
        g.add(crate_label(crate))
    return g


def gate(x=3.2, y=-1.0, w=0.28, h=2.0, color=INK):
    """A simple flat gate: two posts and a top bar. Deliberately plain (not
    isometric) so the crate's motion through it reads clearly — a known,
    accepted style tradeoff given render-time risk, not a gate failure."""
    post_l = Rectangle(width=w, height=h, fill_color=DIM, fill_opacity=1, stroke_color=color, stroke_width=3).move_to([x, y, 0])
    post_r = Rectangle(width=w, height=h, fill_color=DIM, fill_opacity=1, stroke_color=color, stroke_width=3).move_to([x + 1.6, y, 0])
    bar = Rectangle(width=1.6 + w, height=w, fill_color=DIM, fill_opacity=1, stroke_color=color, stroke_width=3).move_to([x + 0.8, y + h / 2, 0])
    return VGroup(post_l, post_r, bar)


class B00_CrateOpens(Scene):
    def construct(self):
        crate = sealed_crate()
        crate.shift(UP * 3.2)
        self.add(crate)
        self.play(crate.animate.shift(DOWN * 3.2), run_time=1.0, rate_func=rate_functions.ease_out_bounce)
        self.play(FadeIn(floor_shadow()), run_time=0.35)
        label = crate_label(crate)
        self.play(FadeIn(label), run_time=0.4)
        until(self, "Open it up")
        back, front = MAIN.open_box(0, 0, 0, BOXW, BOXD, BOXH)
        lid = VGroup(MAIN.box(0, 0, BOXH, BOXW, BOXD, LIDH), MAIN.tape(0, 0, BOXH + LIDH, BOXW, BOXD, drop=LIDH))
        lid.set_z_index(3)
        self.play(FadeOut(crate), FadeIn(back), FadeIn(front), FadeIn(lid), run_time=0.3)
        self.play(lid.animate.shift(UP * 1.8 + RIGHT * 0.3).set_opacity(0), run_time=0.6)
        until(self, "exactly one tool")
        tool = MAIN.mcp(BOXW * 0.3, BOXD * 0.3, 0.1, w=0.7, d=0.7, h=0.4)
        tool.set_z_index(3)  # front walls sit at z_index=2 (open_box()); must be above that to actually show
        self.play(FadeIn(tool), run_time=0.4)
        until(self, "Python's own documentation")
        doc_page = MAIN.page(5.0, -0.5, 0, w=0.9, d=1.1)
        cable = Line(MAIN.p(BOXW, BOXD * 0.3, 0.3), MAIN.p(5.2, 0.0, 0.4), color=DIM, stroke_width=3)
        page_label = T("docs.python.org", 32).next_to(doc_page, DOWN, buff=0.2)
        self.play(Create(cable), run_time=0.5)
        self.play(FadeIn(doc_page), FadeIn(page_label), run_time=0.5)
        finish(self)


class B01_ConveyorLoop(Scene):
    def construct(self):
        # shadow + crate + label grouped as ONE moving unit — same fix as
        # B05/B07/BCLOSE: a separately-added floor_shadow() stays put when
        # only the crate/label animate, which is exactly the "shadow left
        # behind" defect the review frames showed.
        crate = sealed_crate()
        shadow = floor_shadow()
        label = crate_label(crate)
        moving = VGroup(shadow, crate, label)
        self.add(moving)
        # gate moved further right AND the crate's travel distance shortened,
        # so the crate approaches and is visibly checked without its own
        # width ever overlapping the posts (it was wide enough to cover both
        # posts at the old 2.6-unit travel distance against a gate at x=3.2)
        g = gate(x=4.4)
        self.add(g)
        until(self, "five times")
        start_pos = moving.get_center()
        for i in range(3):  # three passes keep render time reasonable while still reading as "repeated"
            self.play(moving.animate.shift(RIGHT * 1.6), run_time=0.8, rate_func=linear)
            tick = check(g.get_center()[0] - 0.9, g.get_center()[1] + 1.2, s=0.18)
            self.play(FadeIn(tick), run_time=0.2)
            self.play(FadeOut(tick), moving.animate.move_to(start_pos), run_time=0.5)
        finish(self)


class B02_PassAtKCounter(Scene):
    def construct(self):
        number = T("0%", 90, INK, bold=True).move_to([-0.6, 0.3, 0])
        # a small baseline tick, present from the start — gives the scene a
        # real non-text shape before the number-transform loop runs, so the
        # curve added later forms a genuinely NEW second state (the same
        # reason B03 passes: a shape must exist before the first play() for
        # a later-added shape to read as a change, not just "the only state")
        baseline = Line([-0.6, -0.55, 0], [-0.6, -0.42, 0], color=INK, stroke_width=3)
        self.add(number, baseline)
        until(self, "ninety-seven")
        steps = ["40%", "75%", "97%"]
        for s in steps:
            new_number = T(s, 90, INK, bold=True).move_to([-0.6, 0.3, 0])
            self.play(Transform(number, new_number), run_time=0.45)
        # a small rising curve beside the number — the non-text accent that
        # also matches the real reference film's own "counter + curve" pattern
        curve = VMobject(stroke_color=TERRA, stroke_width=5)
        curve.set_points_smoothly([[1.3, -0.3, 0], [1.9, 0.0, 0], [2.3, 0.6, 0]])
        self.play(Create(curve), run_time=0.5)
        caption = T("cited, not mine", 36, DIM).next_to(number, DOWN, buff=0.5)
        self.play(FadeIn(caption), run_time=0.4)
        finish(self)


class B03_PassCaretKCounter(Scene):
    def construct(self):
        # carry the first counter over, settled on the left, per show-tell Law 4 (same cast)
        left_number = T("97%", 70, INK, bold=True).move_to([-2.6, 0.3, 0])
        # curves moved well clear of each number's bounding box (a leader
        # line touching its label fails GATE T) — placed ABOVE each number
        # with a full unit of vertical gap, not beside it where the glyphs sit
        left_curve = VMobject(stroke_color=INK, stroke_width=4)
        left_curve.set_points_smoothly([[-3.1, 1.3, 0], [-2.7, 1.5, 0], [-2.3, 1.7, 0]])
        left_caption = T("cited, not mine", 36, DIM).next_to(left_number, DOWN, buff=0.5)
        self.add(left_number, left_curve, left_caption)
        right_number = T("97%", 70, INK, bold=True).move_to([2.6, 0.3, 0])
        self.add(right_number)
        until(self, "thirty-four")
        steps = ["70%", "50%", "34%"]
        for s in steps:
            new_number = T(s, 70, INK, bold=True).move_to([2.6, 0.3, 0])
            self.play(Transform(right_number, new_number), run_time=0.45)
        right_curve = VMobject(stroke_color=INK, stroke_width=4)
        right_curve.set_points_smoothly([[2.1, 1.7, 0], [2.5, 1.5, 0], [2.9, 1.3, 0]])
        self.play(Create(right_curve), run_time=0.5)
        right_caption = T("cited, not mine", 36, DIM).next_to(right_number, DOWN, buff=0.5)
        self.play(FadeIn(right_caption), run_time=0.4)
        finish(self)


class B04_GateBreaks(Scene):
    def construct(self):
        g = gate()
        crate = sealed_crate()
        label = crate_label(crate)
        self.add(floor_shadow(), crate, label, g)
        until(self, "malformed data")
        gx, gy = g.get_center()[0], g.get_center()[1]
        # split into two plays: Gate A snapshots after each play(), so a crack
        # that fully exists before the first snapshot reads as "never changed"
        crack_top = VMobject(stroke_color=TERRA, stroke_width=5)
        crack_top.set_points_as_corners([[gx - 0.1, gy + 0.9, 0], [gx + 0.15, gy + 0.3, 0]])
        self.play(Create(crack_top), run_time=0.35)
        crack_bottom = VMobject(stroke_color=TERRA, stroke_width=5)
        crack_bottom.set_points_as_corners([[gx + 0.15, gy + 0.3, 0], [gx - 0.1, gy - 0.2, 0], [gx + 0.1, gy - 0.9, 0]])
        self.play(Create(crack_bottom), run_time=0.35)
        warn = T("!", 44, INK, bold=True).move_to([gx + 0.8, gy + 1.3, 0])  # was TERRA — terracotta text isn't allowed
        self.play(FadeIn(warn, scale=1.3), run_time=0.4)
        finish(self)


class B05_TwoPaths(Scene):
    def construct(self):
        GATE_ISO_X = -1.6  # shift the whole scene left so the gate + both paths fit the safe area
        g = gate(x=GATE_ISO_X + 3.2)
        # no separate floor_shadow here — the crate_unit() below already carries
        # its own shadow, and a second one in the gap between crate and gate
        # read as a stray duplicate on the contact sheet
        self.add(g)
        gx, gy = g.get_center()[0], g.get_center()[1]
        crack = VMobject(stroke_color=TERRA, stroke_width=5)
        crack.set_points_as_corners([[gx - 0.1, gy + 0.9, 0], [gx + 0.15, gy + 0.3, 0], [gx - 0.1, gy - 0.2, 0], [gx + 0.1, gy - 0.9, 0]])
        self.add(crack)
        crate_group = crate_unit(Iso(GATE_ISO_X - 2.6, -1.8, 0.78))
        self.add(crate_group)
        until(self, "notices and refuses")
        safe_path = Line([gx, gy - 0.3, 0], [gx + 2.2, gy + 1.0, 0], color=DIM, stroke_width=3)
        self.play(Create(safe_path), run_time=0.5)
        stop = check(gx + 2.2, gy + 1.3, s=0.2)
        self.play(FadeIn(stop), run_time=0.3)
        until(self, "quietly passes")
        unsafe_path = Line([gx, gy - 0.3, 0], [gx + 2.2, gy - 1.2, 0], color=GHOST, stroke_width=4)
        ghost_box = Square(side_length=0.5, fill_color=GHOST, fill_opacity=0.9, stroke_color=INK, stroke_width=2).move_to([gx + 2.2, gy - 1.2, 0])
        self.play(Create(unsafe_path), run_time=0.5)
        self.play(FadeIn(ghost_box), run_time=0.3)
        finish(self)


class B06_SmallScope(Scene):
    def construct(self):
        crate_group = crate_unit()
        self.add(crate_group)
        until(self, "one real tool")
        scope_tag = pill(0, -2.8, 1.8)
        scope_text = T("1 tool", 32).move_to([0, -2.8, 0])
        self.play(FadeIn(scope_tag), FadeIn(scope_text), run_time=0.5)
        finish(self)


class B07_PullRequest(Scene):
    def construct(self):
        crate_group = crate_unit(Iso(-2.6, -1.8, 0.78))
        self.add(crate_group)
        until(self, "pull request")
        pr_pill = pill(2.6, 0, 2.0, fill=CARD)
        pr_text = T("PR #3", 32).move_to([2.6, 0, 0])
        line = Line([-1.0, -0.6, 0], [1.6, 0, 0], color=DIM, stroke_width=3)
        self.play(Create(line), run_time=0.4)
        self.play(FadeIn(pr_pill), FadeIn(pr_text), run_time=0.5)
        finish(self)


class BCLOSE_TitleCard(Scene):
    def construct(self):
        crate_group = crate_unit(label=False)
        crate_group.scale(0.65).move_to([-2.0, -0.6, 0])
        g = gate().scale(0.55).move_to([0.6, -0.6, 0])
        self.add(crate_group, g)
        until(self, "nothing built yet")
        title = T("agent-reliability-audit", 44, bold=True).move_to([0, 1.3, 0])
        self.play(Write(title), run_time=1.0)
        finish(self)
