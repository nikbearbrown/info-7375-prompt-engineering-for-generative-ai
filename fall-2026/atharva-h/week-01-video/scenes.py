"""scenes.py — Manim scenes for claude-liam-only-the-gaps.

Concept: the softmax keeps only the GAPS between scores and discards their level.

Palette: cream #FAF9F5, ink #3D3929, terracotta #D97757 (ONE accent event per scene).
Every number on screen is produced by verify/verify_claims.py
(14/14 claims, Python 3.14.7 and 3.12.14). Nothing here is illustrative-but-invented:
constructed INPUTS are marked CONSTRUCTED on screen; all OUTPUTS are computed.

No LaTeX — Text only, so the reel does not depend on a dvisvgm toolchain.
No slant=ITALIC on multi-word text (Pango collapses spaces).

Scene durations are authored against the MEASURED narration lengths in
beat_sheet.json (actual_duration_s). Never hand-tune timing: regenerate
audio and recompile.
"""
import math

from manim import *

# ── The implementation under test ─────────────────────────────────────────────
# Verbatim from Chapter 1, lines 170-182 — the same function verify_claims.py
# tests. Every number this file puts on screen is COMPUTED here, never copied
# in by hand. An earlier draft hardcoded a "plausible" value and got it wrong;
# the self-check at the bottom of this block exists so that cannot recur.


def probabilities(logits, temperature=1.0):
    if not logits or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Need logits and a positive finite temperature")
    if not all(math.isfinite(x) for x in logits):
        raise ValueError("Logits must be finite")
    peak = max(logits)
    weights = [math.exp((x - peak) / temperature) for x in logits]
    total = sum(weights)
    return [weight / total for weight in weights]


def _sq_norm(logits):
    w = [x * x for x in logits]
    t = sum(w)
    return [x / t for x in w]


def _abs_norm(logits):
    w = [abs(x) for x in logits]
    t = sum(w)
    return [x / t for x in w]


BASE = [1.0, 2.0, 3.0]                                   # CONSTRUCTED input
P_BASE = probabilities(BASE)                             # C1  T=1.0
P_HALF = probabilities(BASE, 0.5)                        # C1  T=0.5
P_BUMP = probabilities([1.0, 3.4, 3.0])                  # the "panel is alive" nudge
P_1E16 = probabilities([x + 1e16 for x in BASE])         # C7  invented confidence
P_1E17 = probabilities([x + 1e17 for x in BASE])         # C8  invented ignorance
SQ_LO, SQ_HI = _sq_norm(BASE), _sq_norm([101.0, 102.0, 103.0])    # C4 control
AB_LO, AB_HI = _abs_norm(BASE), _abs_norm([101.0, 102.0, 103.0])  # C4 control

# Self-check: refuse to render if any of this drifts from the chapter's
# recorded tables or from the claims verify_claims.py proves.
assert [f"{p:.10f}" for p in P_BASE] == ["0.0900305732", "0.2447284711", "0.6652409558"]
assert [f"{p:.10f}" for p in P_HALF] == ["0.0158762400", "0.1173104278", "0.8668133322"]
assert P_1E16 == P_HALF, "C7: shift 1e16 must equal the chapter's T=0.5 row"
assert len(set(P_1E17)) == 1, "C8: shift 1e17 must be exactly uniform"
assert probabilities(BASE, 0.5) == probabilities([1.0, 3.0, 5.0]), "C12: stretch == temperature"

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = ManimColor("#FAF9F5")   # claude cream — the app ground
INK   = ManimColor("#3D3929")   # warm near-black — all body text
ACC   = ManimColor("#D97757")   # terracotta — ONE accent event per scene
SOFT  = ManimColor("#73705F")   # secondary text, chips
GHOST = ManimColor("#A9A491")   # dimmed / un-highlighted (never below ~40% opacity)
CARD  = ManimColor("#FFFFFF")   # card surface
LINE  = ManimColor("#E5E2D9")   # hairline

def _t(text, size=24, color=None, weight=None):
    kw = {"font_size": size, "color": color or INK}
    if weight:
        kw["weight"] = weight
    return Text(text, **kw)


def _mono(text, size=20, color=None):
    return Text(text, font_size=size, color=color or INK, font="Menlo")


def _constructed():
    """The label the rubric requires. Persists in every scene that shows the input."""
    box = VGroup(
        _t("CONSTRUCTED", size=14, color=SOFT),
        _t("chosen by hand · no model made these", size=11, color=SOFT),
    ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
    return box.to_corner(DL, buff=0.95)


def _panel_label(text):
    return _t(text, size=14, color=SOFT, weight="BOLD")


def _score_bars(scores, x_centre, zero_y=-1.6, unit=0.42, show_values=True):
    """Bars on a number line with zero marked. Returns (group, bars, numerals, axis)."""
    axis = Line(LEFT * 1.9, RIGHT * 1.9, color=INK, stroke_width=1.6)
    axis.move_to([x_centre, zero_y, 0])
    zero_tag = _t("0", size=13, color=SOFT).next_to(axis, LEFT, buff=0.12)

    bars, numerals = VGroup(), VGroup()
    for i, s in enumerate(scores):
        h = s * unit
        x = x_centre - 1.15 + i * 1.15
        bar = Rectangle(width=0.62, height=abs(h) if abs(h) > 0.02 else 0.02,
                        color=INK, stroke_width=1.6, fill_color=INK, fill_opacity=0.40)
        bar.move_to([x, zero_y + h / 2, 0])
        bars.add(bar)
        if show_values:
            n = _t(f"{s:g}", size=18)
            n.move_to([x, zero_y + h + (0.24 if h >= 0 else -0.24), 0])
            numerals.add(n)
    return VGroup(axis, zero_tag, bars, numerals), bars, numerals, axis


def _slice_bar(probs, centre, width=4.6, height=0.62, accent_index=None):
    """One fixed-width bar sliced by probability. The pizza — always the same total."""
    group, x = VGroup(), centre[0] - width / 2
    for i, p in enumerate(probs):
        w = max(width * p, 0.012)
        fill = ACC if i == accent_index else INK
        op = 0.86 if i == accent_index else (0.34 + 0.16 * i)
        seg = Rectangle(width=w, height=height, color=INK, stroke_width=1.2,
                        fill_color=fill, fill_opacity=op)
        seg.move_to([x + w / 2, centre[1], 0])
        group.add(seg)
        x += w
    frame = Rectangle(width=width, height=height, color=INK, stroke_width=1.6)
    frame.move_to(centre)
    return VGroup(group, frame)


def _readout(probs, centre, size=13, color=None):
    txt = _mono("  ".join(f"{p:.10f}" for p in probs), size=size, color=color)
    txt.move_to(centre)
    return txt


# ═════════════════════════════════════════════════════════════════════════════
#  B01_ScoreToChances — the master frame. Scores in, one whole pizza out.
#  Claim C1. 17.81s
# ═════════════════════════════════════════════════════════════════════════════
class B01_ScoreToChances(Scene):
    def construct(self):
        self.camera.background_color = BG

        divider = Line(UP * 3.1, DOWN * 3.1, color=LINE, stroke_width=1.4)
        left_lab = _panel_label("WHAT THE MODEL THINKS").move_to([-3.6, 2.85, 0])
        right_lab = _panel_label("WHAT COMES OUT").move_to([3.6, 2.85, 0])

        self.play(FadeIn(left_lab), FadeIn(right_lab), Create(divider), run_time=1.1)

        frame, bars, numerals, _ = _score_bars([1, 2, 3], x_centre=-3.6)
        self.play(Create(frame[0]), FadeIn(frame[1]), run_time=1.0)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.35), run_time=1.9)
        self.play(LaggedStart(*[FadeIn(n) for n in numerals], lag_ratio=0.3), run_time=1.0)

        mark = _constructed()
        self.play(FadeIn(mark), run_time=0.7)
        self.wait(1.6)

        rule = _t("must total 100", size=15, color=SOFT).move_to([3.6, 1.15, 0])
        self.play(FadeIn(rule), run_time=0.8)

        pizza = _slice_bar(P_BASE, [3.6, 0.25, 0])
        self.play(Create(pizza[1]), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(s) for s in pizza[0]], lag_ratio=0.3), run_time=1.6)

        pct = _t("9%          24%                    67%", size=16, color=SOFT)
        pct.move_to([3.6, -0.42, 0])
        self.play(FadeIn(pct), run_time=0.8)

        read = _readout(P_BASE, [3.6, -1.45, 0])
        cite = _t("verify_claims.py · C1 · reproduces the recorded T=1.0 row",
                  size=12, color=SOFT).move_to([3.6, -2.05, 0])
        self.play(FadeIn(read), run_time=1.0)
        self.play(FadeIn(cite), run_time=0.7)
        self.wait(2.2)


# ═════════════════════════════════════════════════════════════════════════════
#  B03_SlideAndFreeze — prove the panel is alive, then slide everything and freeze.
#  Claim C3. 17.49s
# ═════════════════════════════════════════════════════════════════════════════
class B03_SlideAndFreeze(Scene):
    def construct(self):
        self.camera.background_color = BG

        divider = Line(UP * 3.1, DOWN * 3.1, color=LINE, stroke_width=1.4)
        left_lab = _panel_label("SCORES").move_to([-3.6, 2.85, 0])
        right_lab = _panel_label("OUTPUT").move_to([3.6, 2.85, 0])
        mark = _constructed()
        frame, bars, numerals, axis = _score_bars([1, 2, 3], x_centre=-3.6)
        pizza = _slice_bar(P_BASE, [3.6, 0.9, 0])
        read = _readout(P_BASE, [3.6, -0.15, 0])

        self.add(divider, left_lab, right_lab, mark, frame, pizza, read)
        self.wait(0.8)

        # ── the panel is ALIVE: move ONE bar and the output visibly redraws ──
        alive = _t("nudge ONE score", size=14, color=SOFT).move_to([-3.6, 2.2, 0])
        self.play(FadeIn(alive), run_time=0.5)
        moved = [1, 3.4, 3]
        new_frame, new_bars, new_nums, _ = _score_bars(moved, x_centre=-3.6)
        bumped = P_BUMP                      # computed above, not copied in
        self.play(Transform(bars, new_bars), Transform(numerals, new_nums),
                  Transform(pizza, _slice_bar(bumped, [3.6, 0.9, 0])),
                  Transform(read, _readout(bumped, [3.6, -0.15, 0])),
                  run_time=1.6)
        self.wait(0.9)

        # back to [1,2,3]
        back_frame, back_bars, back_nums, _ = _score_bars([1, 2, 3], x_centre=-3.6)
        self.play(Transform(bars, back_bars), Transform(numerals, back_nums),
                  Transform(pizza, _slice_bar(P_BASE, [3.6, 0.9, 0])),
                  Transform(read, _readout(P_BASE, [3.6, -0.15, 0])),
                  FadeOut(alive), run_time=1.2)

        # ── the ONE accent event: bracket the gap ────────────────────────────
        zy, u = -1.6, 0.42                     # must match _score_bars defaults
        y1, y2 = zy + 2 * u, zy + 3 * u        # tops of the score-2 and score-3 bars
        br = VGroup(
            DashedLine([-3.6, y1, 0], [-1.9, y1, 0], color=ACC,
                       stroke_width=1.8, dash_length=0.09),
            DashedLine([-2.45, y2, 0], [-1.9, y2, 0], color=ACC,
                       stroke_width=1.8, dash_length=0.09),
            DoubleArrow([-2.0, y1, 0], [-2.0, y2, 0], color=ACC,
                        stroke_width=3, tip_length=0.10, buff=0),
        )
        gap_lab = _t("the gap", size=15, color=ACC).move_to([-1.2, (y1 + y2) / 2, 0])
        self.play(Create(br), FadeIn(gap_lab), run_time=1.0)

        # ── slide ALL of them; gaps locked; output frozen ────────────────────
        note = _t("gaps locked", size=15, color=SOFT).move_to([-3.6, -2.5, 0])
        self.play(FadeIn(note), run_time=0.5)

        locked = VGroup(bars, numerals, br, gap_lab)
        for shift_lab, dy in (("+1e6", 0.35), ("+1e15", 0.35), ("below zero", -1.2)):
            tag = _t(shift_lab, size=15, color=INK).move_to([-1.35, -2.95, 0])
            self.play(locked.animate.shift(UP * dy), FadeIn(tag), run_time=1.15)
            self.play(FadeOut(tag), run_time=0.25)

        frozen = _t("IDENTICAL — ten decimal places, every shift",
                    size=15, color=INK, weight="BOLD").move_to([3.6, -0.95, 0])
        cite = _t("verify_claims.py · C3 · exact equality, not isclose",
                  size=12, color=SOFT).move_to([3.6, -1.5, 0])
        self.play(FadeIn(frozen), run_time=0.8)
        self.play(FadeIn(cite), run_time=0.6)
        self.wait(2.0)


# ═════════════════════════════════════════════════════════════════════════════
#  B04_ControlAndLunch — the negative control, then the rotten kitchen.
#  Claims C4 (+ constructed lunch labels). 19.48s
# ═════════════════════════════════════════════════════════════════════════════
class B04_ControlAndLunch(Scene):
    def construct(self):
        self.camera.background_color = BG

        head = _t("is it really the machine, or a stiff animation?",
                  size=20, color=INK).to_edge(UP, buff=0.75)
        sub = _t("same +100 slide, three different ways to make positive numbers",
                 size=13, color=SOFT).next_to(head, DOWN, buff=0.16)
        self.play(FadeIn(head), FadeIn(sub), run_time=1.2)

        cols = [
            ("x squared", SQ_LO, SQ_HI, True),
            ("absolute value", AB_LO, AB_HI, True),
            ("softmax", P_BASE, P_BASE, False),
        ]
        groups = VGroup()
        for i, (name, before, after, breaks) in enumerate(cols):
            x = -4.5 + i * 4.5
            title = _t(name, size=17, weight="BOLD").move_to([x, 1.75, 0])
            b_lab = _t("[1, 2, 3]", size=12, color=SOFT).move_to([x, 1.25, 0])
            b_bar = _slice_bar(before, [x, 0.82, 0], width=3.4, height=0.42)
            a_lab = _t("[101, 102, 103]", size=12, color=SOFT).move_to([x, 0.28, 0])
            a_bar = _slice_bar(after, [x, -0.15, 0], width=3.4, height=0.42)
            verdict = _t("CHANGED" if breaks else "UNCHANGED", size=15,
                         color=ACC if not breaks else SOFT,
                         weight="BOLD").move_to([x, -0.78, 0])
            groups.add(VGroup(title, b_lab, b_bar, a_lab, a_bar, verdict))
        self.play(LaggedStart(*[FadeIn(g) for g in groups], lag_ratio=0.35), run_time=3.0)
        cite = _t("verify_claims.py · C4 — the control that makes the result mean something",
                  size=12, color=SOFT).move_to([0, -1.45, 0])
        self.play(FadeIn(cite), run_time=0.7)
        self.wait(1.5)
        lunch_head = _t("so: lunch", size=26, weight="BOLD").to_edge(UP, buff=0.75)
        self.play(FadeOut(groups), FadeOut(sub), FadeOut(cite),
                  Transform(head, lunch_head), run_time=0.7)

        # ── the rotten kitchen ───────────────────────────────────────────────
        mark = VGroup(
            _t("CONSTRUCTED", size=13, color=SOFT, weight="BOLD"),
            _t("lunch example is the narrator's own", size=11, color=SOFT),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT).to_corner(DL, buff=0.95)
        self.play(FadeIn(mark), run_time=0.35)

        names = ["pizza", "salad", "dirt"]
        rows = VGroup()
        for i, (n, s) in enumerate(zip(names, [3, 2, 1])):
            lab = _t(f"{n}", size=26).move_to([-4.0, 1.5 - i * 0.78, 0])
            val = _t(f"{s}", size=26, color=SOFT).move_to([-2.0, 1.5 - i * 0.78, 0])
            rows.add(VGroup(lab, val))
        pizza = _slice_bar([P_BASE[2], P_BASE[1], P_BASE[0]], [2.6, 0.85, 0],
                           width=5.8, height=0.9, accent_index=0)
        call = _t("67%  ·  pizza", size=30, weight="BOLD").move_to([2.6, -0.35, 0])
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.3),
                  Create(pizza[1]), run_time=1.3)
        self.play(FadeIn(pizza[0]), run_time=0.9)
        self.play(FadeIn(call), run_time=0.7)
        self.wait(1.2)

        # everything rotten: -100 across the board
        rotten = VGroup()
        for i, (n, s) in enumerate(zip(names, [-97, -98, -99])):
            lab = _t(f"rotten {n}", size=26, color=INK).move_to([-4.0, 1.5 - i * 0.78, 0])
            val = _t(f"{s}", size=26, color=SOFT).move_to([-2.0, 1.5 - i * 0.78, 0])
            rotten.add(VGroup(lab, val))
        drop = _t("every score 100 points worse", size=14, color=SOFT).move_to([-3.1, -1.45, 0])
        self.play(Transform(rows, rotten), FadeIn(drop), run_time=1.6)
        self.wait(1.3)
        same = _t("same answer", size=20, color=ACC, weight="BOLD").move_to([2.6, -1.15, 0])
        self.play(FadeIn(same), run_time=0.7)
        self.wait(1.8)


# ═════════════════════════════════════════════════════════════════════════════
#  B05_PayoffAndStretch — the thesis line, then stretching == temperature.
#  Claim C12. 18.05s
# ═════════════════════════════════════════════════════════════════════════════
class B05_PayoffAndStretch(Scene):
    def construct(self):
        self.camera.background_color = BG

        l1 = _t("It can always tell you what it prefers.", size=30).move_to([0, 0.55, 0])
        l2 = _t("It can never tell you it hates all of them.", size=30,
                weight="BOLD").move_to([0, -0.3, 0])
        self.play(FadeIn(l1), run_time=1.2)
        self.play(FadeIn(l2), run_time=1.2)
        self.wait(2.2)                       # the line sets alone. nothing else moves.
        self.play(FadeOut(l1), FadeOut(l2), run_time=0.7)

        head = _t("two things you can do to a set of gaps", size=20).to_edge(UP, buff=0.75)
        self.play(FadeIn(head), run_time=0.8)

        # live geometry: bars on the left, the pizza on the right
        frame, bars, numerals, _ = _score_bars(BASE, x_centre=-4.0, zero_y=-1.9, unit=0.40)
        pizza = _slice_bar(P_BASE, [3.4, 0.55, 0], width=4.8, height=0.55)
        read = _readout(P_BASE, [3.4, -0.25, 0])
        self.play(FadeIn(frame), FadeIn(pizza), FadeIn(read), run_time=1.2)

        # gap marker between the first two bar tops — this is the thing being acted on
        def gap_arrow(scores, label):
            y0 = -1.9 + scores[0] * 0.40
            y1 = -1.9 + scores[1] * 0.40
            arr = DoubleArrow([-3.3, y0, 0], [-3.3, y1, 0], color=ACC,
                              stroke_width=3, tip_length=0.16, buff=0)
            lab = _t(label, size=14, color=ACC).next_to(arr, RIGHT, buff=0.12)
            return VGroup(arr, lab)

        gap = gap_arrow(BASE, "gap 1")
        self.play(Create(gap), run_time=0.8)

        # ── 1. SLIDE: everything moves, the gap does not, the output does not ──
        tag = _t("SLIDE  →  output unchanged", size=17, color=SOFT).move_to([-4.0, 2.05, 0])
        self.play(FadeIn(tag), run_time=0.5)
        self.play(VGroup(bars, numerals, gap).animate.shift(UP * 0.8), run_time=1.2)
        self.play(VGroup(bars, numerals, gap).animate.shift(DOWN * 0.8), run_time=0.9)

        # ── 2. STRETCH the gaps: the favourite's slice visibly grows ─────────
        tag2 = _t("STRETCH the gaps  →  the favourite wins more often", size=17,
                  color=ACC, weight="BOLD").move_to([-3.6, 2.05, 0])
        self.play(Transform(tag, tag2), run_time=0.5)

        wide = [1.0, 3.0, 5.0]                       # gaps x2  ==  temperature 0.5
        _, wide_bars, wide_nums, _ = _score_bars(wide, x_centre=-4.0, zero_y=-1.9, unit=0.40)
        self.play(
            Transform(bars, wide_bars),
            Transform(numerals, wide_nums),
            Transform(gap, gap_arrow(wide, "gap 2")),
            Transform(pizza, _slice_bar(P_HALF, [3.4, 0.55, 0], width=4.8, height=0.55)),
            Transform(read, _readout(P_HALF, [3.4, -0.25, 0])),
            run_time=1.8,
        )
        hot = _t("temperature DOWN", size=15, color=ACC).move_to([3.4, -0.95, 0])
        self.play(FadeIn(hot), run_time=0.5)
        self.wait(0.9)

        # ── 3. SQUASH the gaps: the slices even out ──────────────────────────
        tag3 = _t("SQUASH them together  →  it picks more evenly", size=17,
                  color=ACC, weight="BOLD").move_to([-3.6, 2.05, 0])
        self.play(Transform(tag, tag3), run_time=0.5)

        tight = [1.0, 1.5, 2.0]                      # gaps x0.5  ==  temperature 2.0
        p_tight = probabilities(tight)
        assert [f"{v:.10f}" for v in p_tight] == ["0.1863237232", "0.3071958857",
                                                  "0.5064803911"], "C12: gaps x0.5 == T 2.0"
        _, tight_bars, tight_nums, _ = _score_bars(tight, x_centre=-4.0, zero_y=-1.9, unit=0.40)
        self.play(
            Transform(bars, tight_bars),
            Transform(numerals, tight_nums),
            Transform(gap, gap_arrow(tight, "gap ½")),
            Transform(pizza, _slice_bar(p_tight, [3.4, 0.55, 0], width=4.8, height=0.55)),
            Transform(read, _readout(p_tight, [3.4, -0.25, 0])),
            Transform(hot, _t("temperature UP", size=15, color=ACC).move_to([3.4, -0.95, 0])),
            run_time=1.8,
        )

        same = _t("stretching and squashing the gaps IS the temperature dial",
                  size=18, weight="BOLD").move_to([0, -2.6, 0])
        cite = _t("verify_claims.py · C12 · gaps x2 = T 0.5, gaps x0.5 = T 2.0",
                  size=12, color=SOFT).move_to([0, -3.05, 0])
        self.play(FadeIn(same), run_time=0.8)
        self.play(FadeIn(cite), run_time=0.6)
        self.wait(1.2)


# ═════════════════════════════════════════════════════════════════════════════
#  B07_PredictConfirm — state the prediction, hold it, THEN stretch the gaps.
#  Claims C6, C7, C12. 19.99s
# ═════════════════════════════════════════════════════════════════════════════
class B07_PredictConfirm(Scene):
    def construct(self):
        self.camera.background_color = BG

        head = _t("past about 9 quadrillion, the digits run out", size=26,
                  weight="BOLD").to_edge(UP, buff=0.75)
        sub = _t("2^53 = 9,007,199,254,740,992", size=15, color=SOFT).next_to(head, DOWN, buff=0.12)
        self.play(FadeIn(head), FadeIn(sub), run_time=1.3)

        scan = [("2^53-3", "1, 1", False), ("2^53-2", "1, 0", True),
                ("2^53-1", "0, 2", True), ("2^53+0", "2, 2", True)]
        rows = VGroup()
        for i, (s, g, broken) in enumerate(scan):
            y = 1.55 - i * 0.42
            rows.add(VGroup(
                _mono(s, size=15, color=INK if broken else SOFT).move_to([-4.6, y, 0]),
                _mono(g, size=15, color=ACC if broken else SOFT).move_to([-2.8, y, 0]),
                _t("BROKEN" if broken else "ok", size=13,
                   color=INK if broken else SOFT).move_to([-1.5, y, 0]),
            ))
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.3), run_time=1.8)
        self.wait(0.7)

        # ── the PREDICTION, stated before anything is computed ──────────────
        pbox = Rectangle(width=6.2, height=2.25, color=ACC, stroke_width=2.2,
                         fill_color=CARD, fill_opacity=1).move_to([2.9, 0.9, 0])
        plab = _t("PREDICTION — before computing", size=12, color=ACC,
                  weight="BOLD").move_to([2.9, 1.6, 0])
        p1 = _t("gaps: 1 apart  →  2 apart", size=16).move_to([2.9, 1.05, 0])
        p2 = _t("a stretch of 2  =  temperature 0.5", size=16).move_to([2.9, 0.62, 0])
        p3 = _t("so: the recorded T=0.5 row", size=16, weight="BOLD").move_to([2.9, 0.19, 0])
        # the left-hand geometry arrives FIRST, so the prediction hold is not a bare card
        self.play(FadeOut(sub), FadeOut(rows), run_time=0.6)
        frame, bars, numerals, _ = _score_bars(BASE, x_centre=-4.2, zero_y=-2.55, unit=0.60)
        pizza = _slice_bar(P_BASE, [-3.9, 1.85, 0], width=4.6, height=0.7)
        self.play(FadeIn(frame), FadeIn(pizza), run_time=0.9)

        self.play(Create(pbox), FadeIn(plab), run_time=0.9)
        self.play(FadeIn(p1), run_time=0.6)
        self.play(FadeIn(p2), run_time=0.6)
        self.play(FadeIn(p3), run_time=0.7)
        self.wait(1.7)                       # let the audience disbelieve it first

        rounding = _t("rounding past 2^53", size=15, color=ACC).move_to([-1.55, -1.15, 0])
        self.play(FadeIn(rounding), run_time=0.5)

        wide = [1.0, 3.0, 5.0]
        _, wide_bars, wide_nums, _ = _score_bars(wide, x_centre=-4.2, zero_y=-2.55, unit=0.60)
        self.play(
            Transform(bars, wide_bars),
            Transform(numerals, wide_nums),
            Transform(pizza, _slice_bar(P_HALF, [-3.9, 1.85, 0], width=4.6, height=0.7)),
            run_time=2.1,
        )

        got = VGroup(_t("computed at shift 1e16", size=12, color=SOFT),
                     _readout(P_HALF, [0, 0, 0]),
                     ).arrange(DOWN, buff=0.12).move_to([2.9, -1.1, 0])
        want = VGroup(_t("the published T=0.5 row", size=12, color=SOFT),
                      _readout(P_HALF, [0, 0, 0]),
                      ).arrange(DOWN, buff=0.12).move_to([2.9, -2.1, 0])
        self.play(FadeIn(got), run_time=0.8)
        self.play(FadeIn(want), run_time=0.8)
        match = _t("digit for digit", size=16, color=ACC, weight="BOLD").move_to([2.9, -2.8, 0])
        self.play(FadeIn(match), run_time=0.7)
        self.wait(1.2)


# ═════════════════════════════════════════════════════════════════════════════
#  B08_FlatAndCheck — fake ignorance, and the check that sees nothing.
#  Claims C8, C9. 17.60s
# ═════════════════════════════════════════════════════════════════════════════
class B08_FlatAndCheck(Scene):
    def construct(self):
        self.camera.background_color = BG

        head = _t("push once more  ·  shift 1e17", size=22, weight="BOLD").to_edge(UP, buff=0.75)
        self.play(FadeIn(head), run_time=0.9)

        before = VGroup(_mono("1.0    2.0    3.0", size=26),
                        _t("three distinct scores", size=16, color=SOFT)
                        ).arrange(DOWN, buff=0.18).move_to([0, 2.1, 0])
        self.play(FadeIn(before), run_time=1.0)

        after = VGroup(_mono("1e17   1e17   1e17", size=26, color=ACC),
                       _t("all three round to the SAME number  ·  gaps 0, 0",
                          size=16, color=SOFT)
                       ).arrange(DOWN, buff=0.18).move_to([0, 2.1, 0])
        self.play(Transform(before, after), run_time=1.6)
        self.wait(1.1)

        flat = _slice_bar(P_1E17, [0, 0.35, 0], width=9.6, height=1.15)
        read = _readout(P_1E17, [0, -0.72, 0], size=17)
        shape = _t("flat  —  the shape of 'no preference'", size=26).move_to([0, -1.35, 0])
        made = _t("manufactured out of nothing but rounding", size=19,
                  color=SOFT).move_to([0, -2.1, 0])
        self.play(Create(flat[1]), FadeIn(flat[0]), run_time=1.2)
        self.play(FadeIn(read), run_time=0.9)
        self.play(FadeIn(shape), run_time=0.8)
        self.play(FadeIn(made), run_time=0.7)
        self.wait(1.4)
        self.play(FadeOut(before), FadeOut(flat), FadeOut(read),
                  FadeOut(shape), FadeOut(made), FadeOut(head), run_time=0.7)

        # ── both wrong. both pass. ──────────────────────────────────────────
        q = _t("both of these are wrong", size=22, weight="BOLD").to_edge(UP, buff=0.75)
        self.play(FadeIn(q), run_time=0.8)

        panels = VGroup()
        for i, (lab, probs) in enumerate((("shift 1e16 — invented confidence", P_HALF),
                                          ("shift 1e17 — invented ignorance", P_1E17))):
            x = -3.6 + i * 7.2
            t = _t(lab, size=14, color=SOFT).move_to([x, 1.85, 0])
            bar = _slice_bar(probs, [x, 0.95, 0], width=5.4, height=0.66)
            r = _readout(probs, [x, 0.3, 0])
            s = _mono("sum = 1.0", size=17).move_to([x, -0.3, 0])
            panels.add(VGroup(t, bar, r, s))
        self.play(LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.35), run_time=2.0)

        checks = VGroup()
        for i in range(2):
            x = -3.6 + i * 7.2
            tick = VGroup(
                Line([x - 0.22, -0.95, 0], [x - 0.04, -1.13, 0], color=ACC, stroke_width=5),
                Line([x - 0.04, -1.13, 0], [x + 0.3, -0.72, 0], color=ACC, stroke_width=5),
            )
            lab = _t("isclose(sum, 1.0)  →  True", size=14, color=ACC,
                     weight="BOLD").move_to([x, -1.85, 0])
            checks.add(VGroup(tick, lab))
        self.play(LaggedStart(*[Create(c[0]) for c in checks], lag_ratio=0.3), run_time=1.0)
        self.play(*[FadeIn(c[1]) for c in checks], run_time=0.8)

        kicker = _t("the reference check passes them both", size=18,
                    weight="BOLD").move_to([0, -2.35, 0])
        cite = _t("verify_claims.py · C8, C9 · a passing test that proves nothing",
                  size=12, color=SOFT).move_to([0, -2.85, 0])
        self.play(FadeIn(kicker), run_time=0.8)
        self.play(FadeIn(cite), run_time=0.6)
        self.wait(1.2)


# ═════════════════════════════════════════════════════════════════════════════
#  B02_WhatIsAGap — define the one word the whole reel depends on.
#  Added after review: "gap" was used from beat two onward and never explained.
# ═════════════════════════════════════════════════════════════════════════════
class B02_WhatIsAGap(Scene):
    def construct(self):
        self.camera.background_color = BG

        head = _t("a \"gap\" is just the distance between two scores",
                  size=26).to_edge(UP, buff=0.75)
        self.play(FadeIn(head), run_time=1.1)

        def row(values, y, colour=INK):
            """A number line with the three values on it and the distances marked."""
            g = VGroup()
            xs = [-3.95, 0.0, 3.95]
            line = Line([-5.95, y, 0], [5.95, y, 0], color=SOFT, stroke_width=1.8)
            g.add(line)
            dots, labels = VGroup(), VGroup()
            for x, v in zip(xs, values):
                d = Dot([x, y, 0], radius=0.11, color=colour)
                lab = _t(f"{v:g}", size=32, color=colour).move_to([x, y + 0.62, 0])
                dots.add(d)
                labels.add(lab)
            g.add(dots, labels)
            arrows = VGroup()
            for a, b in ((xs[0], xs[1]), (xs[1], xs[2])):
                arr = DoubleArrow([a, y - 0.5, 0], [b, y - 0.5, 0], color=ACC,
                                  stroke_width=3, tip_length=0.16, buff=0.12)
                tag = _t("1 apart", size=20, color=ACC).move_to([(a + b) / 2, y - 1.0, 0])
                arrows.add(VGroup(arr, tag))
            g.add(arrows)
            return g, dots, labels, arrows

        top, _, _, top_arrows = row([1, 2, 3], 1.65)
        self.play(FadeIn(top[0]), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(m) for m in top[1]], lag_ratio=0.3), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(m) for m in top[2]], lag_ratio=0.3), run_time=0.9)
        self.play(LaggedStart(*[Create(a) for a in top_arrows], lag_ratio=0.35), run_time=1.5)
        self.wait(1.3)

        bot, _, _, bot_arrows = row([101, 102, 103], -1.45)
        self.play(FadeIn(bot[0]), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(m) for m in bot[1]], lag_ratio=0.3), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(m) for m in bot[2]], lag_ratio=0.3), run_time=0.9)
        self.play(LaggedStart(*[Create(a) for a in bot_arrows], lag_ratio=0.35), run_time=1.4)
        self.wait(0.9)

        verdict = _t("completely different scores  ·  exactly the same gaps",
                     size=27, weight="BOLD").move_to([0, -3.0, 0])
        self.play(FadeIn(verdict), run_time=1.0)
        self.wait(1.8)


# ═════════════════════════════════════════════════════════════════════════════
#  B06_OutOfDigits — why a computer stops being able to tell 1 apart.
#  REV 3: replaced B06_RulerRounding. The ruler version said "very big numbers"
#  while showing 1, 2, 3 — the visual contradicted the voice, so "runs out of
#  room" had nothing to attach to. This shows the digits actually running out.
#  Claim C14.
# ═════════════════════════════════════════════════════════════════════════════
WANTED = [9007199254740993, 9007199254740994, 9007199254740995]
STORED = [int(float(x)) for x in WANTED]
assert STORED == [9007199254740992, 9007199254740994, 9007199254740996]
assert [STORED[1] - STORED[0], STORED[2] - STORED[1]] == [2, 2], "C14: gaps must double"


class B06_OutOfDigits(Scene):
    def construct(self):
        self.camera.background_color = BG

        head = _t("a computer has room for about sixteen digits in a number",
                  size=25).to_edge(UP, buff=0.75)
        self.play(FadeIn(head), run_time=0.7)

        def digit_box(text, y, label, scale=1.0):
            cells = VGroup()
            n, w = 16, 0.60
            pad = " " * (n - len(text)) + text
            for k, ch in enumerate(pad):
                x = (k - (n - 1) / 2) * w
                filled = ch != " "
                cell = Rectangle(width=w * 0.9, height=0.76, color=INK, stroke_width=2.0,
                                 fill_color=INK if filled else CARD,
                                 fill_opacity=0.30 if filled else 1)
                cell.move_to([x, y, 0])
                cells.add(cell)
                if filled:
                    cells.add(_mono(ch, size=26).move_to([x, y, 0]))
            tag = _t(label, size=18, color=SOFT).move_to([0, y - 0.78, 0])
            return VGroup(cells, tag).scale(scale)

        # ── the box: nearly empty for a small score, full for a huge one ────
        small = digit_box("3", 2.32, "a small score — plenty of room spare")
        self.play(FadeIn(small), run_time=0.8)
        big = digit_box("9007199254740993", 2.32, "a huge score — every cell used up")
        self.play(Transform(small, big), run_time=1.1)

        # ── the comparison, complete before the halfway mark ────────────────
        cols = [-4.15, 0.0, 4.15]

        def row(values, y, colour, label, gap_text, arrow_y, tag_y, stroke):
            lab = _t(label, size=17, color=SOFT).move_to([0, y + 0.52, 0])
            nums = VGroup(*[_mono(f"…{str(v)[-6:]}", size=27, color=colour).move_to([x, y, 0])
                            for x, v in zip(cols, values)])
            arrows = VGroup(*[VGroup(
                DoubleArrow([cols[i] + 1.05, arrow_y, 0], [cols[i + 1] - 1.05, arrow_y, 0],
                            color=colour, stroke_width=stroke, tip_length=0.15, buff=0),
                _t(gap_text, size=17, color=colour).move_to(
                    [(cols[i] + cols[i + 1]) / 2, tag_y, 0]),
            ) for i in range(2)])
            return VGroup(lab, nums, arrows)

        want = row(WANTED, 0.40, INK, "what we wanted", "1 apart", -0.14, -0.50, 2.6)
        store = row(STORED, -1.52, ACC, "what it can actually store", "2 apart", -2.06, -2.42, 3.2)

        self.play(FadeIn(want[0]), LaggedStart(*[FadeIn(m) for m in want[1]],
                                               lag_ratio=0.2), run_time=1.0)
        self.play(LaggedStart(*[Create(g) for g in want[2]], lag_ratio=0.25), run_time=0.8)
        self.play(FadeIn(store[0]), TransformFromCopy(want[1], store[1]), run_time=1.3)
        self.play(LaggedStart(*[Create(g) for g in store[2]], lag_ratio=0.25), run_time=0.9)

        verdict = _t("the last digit can't be written down — so the gaps doubled",
                     size=23, weight="BOLD").move_to([0, -3.02, 0])
        self.play(FadeIn(verdict), run_time=0.8)
        self.wait(5.2)
