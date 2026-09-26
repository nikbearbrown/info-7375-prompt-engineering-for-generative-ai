"""
Manim scenes for why-subtract-the-max (INFO 7375, Week 1).

BINTRO_Title   — 3 s silent title card (no narration; audio_policy = silence)
B00_Hook       — the real source line + the question
B01_Setup      — three scores -> softmax -> three probabilities
B02_Shift      — RAW -> -MAX -> EXP -> /TOTAL, the four-stage chain
B03_Identity   — shifted vs direct at full precision (agreement, NOT identity)
B04_WhyBother  — [1000,1000]: 0.5/0.5 vs OverflowError
B05_Boundary   — the mandatory on-screen boundary statement
B06_Close      — one-sentence recap

PROVENANCE OF EVERY NUMBER BELOW
--------------------------------
Source: lessons/01-randomness-and-first-prompts/code/main.py (repo HEAD 8f590fa),
executed on this machine with Python 3.13.5.

  PRINTED by `python3 main.py`:
      PROBS (the "probabilities" array)

  DERIVED by importing main.py and calling its own probabilities(), with each
  recomputed stage checked against that function's return value (max abs
  difference 0.0):
      PEAK, SHIFTED, EXP_SHIFTED, TOTAL_SHIFTED,
      EXP_DIRECT, TOTAL_DIRECT, PROBS_DIRECT, DIFFS, MAX_DIFF,
      BIG_PROBS, and the OverflowError message.

Nothing here is transcribed from the chapter text or from memory.
"""
from manim import *

# ── palette (house: claude skin) ──────────────────────────────────────────────
BG     = ManimColor("#FAF9F5")   # cream page
INK    = ManimColor("#3D3929")   # warm near-black — all body text
ACCENT = ManimColor("#D97757")   # terracotta — ONE accent per scene
SOFT   = ManimColor("#6E6A57")   # secondary / muted
RULE   = ManimColor("#C9C2B4")   # hairlines

# ── the real numbers ─────────────────────────────────────────────────────────
LOGITS        = [1, 2, 3]
PEAK          = 3
SHIFTED       = [-2, -1, 0]
EXP_SHIFTED   = [0.1353352832366127, 0.36787944117144233, 1.0]
TOTAL_SHIFTED = 1.5032147244080551
PROBS         = [0.09003057317038046, 0.24472847105479764, 0.6652409557748218]

EXP_DIRECT    = [2.718281828459045, 7.38905609893065, 20.085536923187668]
TOTAL_DIRECT  = 30.192874850577365
PROBS_DIRECT  = [0.09003057317038045, 0.24472847105479764, 0.6652409557748219]

DIFFS         = ["1.3877787807814457e-17", "0.0", "1.1102230246251565e-16"]
# Same values at 3 s.f., for the narrow per-row column in B03. The full-
# precision figure is on screen in the same frame (the verdict line uses
# MAX_DIFF) and in FACTCHECK.md; at full width the column reached x=6.47 and
# Gate B rejected it against the +/-6.3 safe extent.
DIFFS_SHORT   = ["1.39e-17", "0.0", "1.11e-16"]
MAX_DIFF      = "1.1102230246251565e-16"

BIG_LOGITS    = [1000, 1000]
BIG_PROBS     = [0.5, 0.5]
FLOAT_MAX     = "1.7976931348623157e+308"
OVERFLOW_MSG  = "OverflowError: math range error"

# ── safe-area helpers ────────────────────────────────────────────────────────
# Gate V (runtime/qc/final_frame_check.py) fails any frame with ink outside the
# 5% title-safe inset, and flags < 55% coverage of that area as underfill. In
# Manim units the 1920x1080 frame is 14.22 x 8, so title-safe is x +/-6.4,
# y +/-3.6. FIT_W/FIT_H leave a little margin inside that.
# Measured against the audit's own report, not assumed: manim_layout_audit.py
# prints "safe area (half-extents): ±6.3 x / ±3.4 y", so the usable box is
# 12.6 x 6.8. These leave a margin inside that.
FIT_W, FIT_H = 12.2, 6.5


def fit(m, w=FIT_W, h=FIT_H):
    """Shrink a mobject until it sits inside the title-safe box."""
    if m.width > w:
        m.scale_to_fit_width(w)
    if m.height > h:
        m.scale_to_fit_height(h)
    return m


def fill_safe(m, w=11.8, h=6.2):
    """Scale a group UP (or down) until it occupies most of the safe area.

    fit() only shrinks, which is the wrong half of the problem: Gate V fails a
    frame whose content covers < 55% of the safe area as `underfill`. A small
    block floating in the middle of the page is a defect, not a neutral
    choice. This is the Manim counterpart of fitToSafe() in the Remotion
    tokens/layout.ts.
    """
    if m.width <= 0 or m.height <= 0:
        return m
    m.scale(min(w / m.width, h / m.height))
    return m


def label(text, size=30, color=INK, weight="NORMAL"):
    """Weights are STRINGS on purpose.

    Gate A (runtime/qc/static_scene_check.py) executes construct() against a
    stub `manim` module that defines the geometry and animation names but not
    the text-weight constants, so `weight=NORMAL` raises
    NameError: name 'NORMAL' is not defined and the gate fails the scene even
    though it renders fine. Real manim accepts the string form.
    """
    return Text(text, font_size=size, color=color, weight=weight)


def kicker(text):
    # buff 0.55 put the kicker's top edge at y=3.45 on a half-height-4.0 frame,
    # 0.05 outside the audit's ±3.4 safe extent — Gate B failed it. 0.72 lands
    # the top at 3.28.
    return label(text, size=22, color=SOFT).to_edge(UP, buff=0.72)


def rule_line(width=12.2, color=RULE):
    return Line(LEFT * width / 2, RIGHT * width / 2, stroke_width=2, color=color)


def page(scene):
    """Paint the cream page.

    NOTE: run.sh finds scenes with the regex

        class ([A-Z][A-Za-z0-9]*_\\w+)\\(Scene\\)

    so every scene class below MUST inherit Scene *directly*. Factoring the
    background onto a shared base class made the whole reel invisible to the
    renderer — it reported "nothing to render" and compiled seven slates.
    Hence a plain function instead of a base class.
    """
    scene.camera.background_color = BG


# ── BINTRO ───────────────────────────────────────────────────────────────────
class BINTRO_Title(Scene):
    """3-second silent title card.

    Added as a NEW FIRST BEAT rather than by renumbering: compile.py iterates
    `beats` in array order, never by sorted id, so inserting at index 0 with a
    non-colliding id leaves every existing beat, clip and mp3 untouched.
    `run.sh` derives the beat id from the class name up to the first underscore
    (BINTRO_Title -> BINTRO).

    Carries no narration — the beat sets "silent": true, and compile.py
    substitutes anullsrc for its audio slot.
    """

    def construct(self):
        page(self)
        head = kicker("INFO 7375  ·  PROMPT ENGINEERING FOR GENERATIVE AI")

        title = VGroup(
            label("Why subtracting the maximum", size=52, color=INK),
            label("changes the intermediates", size=52, color=INK),
            label("but not the distribution", size=52, color=ACCENT, weight="BOLD"),
        ).arrange(DOWN, buff=0.34)

        bar = Line(LEFT * 3.4, RIGHT * 3.4, stroke_width=3, color=RULE)
        sub = label("Week 1  ·  softmax and temperature sampling",
                    size=28, color=SOFT)

        block = VGroup(title, bar, sub).arrange(DOWN, buff=0.52)
        fill_safe(block, w=11.4, h=5.2)
        fit(block)
        block.move_to(DOWN * 0.15)

        # travels the rule in the final second — Gate A fails a scene whose
        # shape-state never changes, and 3 s leaves little room to establish
        # movement any other way
        marker = Rectangle(width=0.13, height=0.30, stroke_width=0,
                           fill_color=ACCENT, fill_opacity=1.0)
        marker.move_to(bar.get_left())

        self.play(FadeIn(head, shift=DOWN * 0.15), run_time=0.30)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.12) for t in title],
                              lag_ratio=0.18), run_time=1.00)
        self.play(Create(bar), run_time=0.40)
        self.play(FadeIn(marker), FadeIn(sub, shift=UP * 0.10), run_time=0.35)
        self.play(marker.animate.move_to(bar.get_right()), run_time=0.60)
        self.wait(0.35)


# ── B00 ──────────────────────────────────────────────────────────────────────
class B00_Hook(Scene):
    def construct(self):
        page(self)
        # Gate W (W7, SLATE-RUNNER recap law) bans chapter numbers on screen —
        # CHAP_RE matches /\bchapter\b|\bch\.\s*\d/i over every string constant
        # in the class. Name the TOPIC instead. The narration may still say
        # "Chapter One"; the law governs the frame, not the voice.
        head = kicker("INFO 7375  ·  RANDOMNESS AND FIRST PROMPTS")

        # the actual lines from main.py, verbatim
        code = VGroup(
            label("peak = max(logits)", size=40, color=INK),
            label("weights = [math.exp((x - peak) / temperature)", size=40, color=INK),
            label("           for x in logits]", size=40, color=INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        fit(code, w=11.6)

        box = SurroundingRectangle(code, color=RULE, stroke_width=2,
                                   buff=0.55, corner_radius=0.12)
        src = label("main.py  ·  lines 14-15", size=20, color=SOFT)
        src.next_to(box, DOWN, buff=0.28).align_to(box, RIGHT)

        block = VGroup(box, code, src).move_to(UP * 0.85)

        q = label("Why subtract first?", size=64, color=ACCENT, weight="BOLD")
        q.next_to(block, DOWN, buff=0.75)
        sub = label("Nothing in the math asks for it.", size=30, color=SOFT)
        sub.next_to(q, DOWN, buff=0.30)

        whole = VGroup(block, q, sub)
        fit(whole)
        whole.move_to(DOWN * 0.25)

        ul = Line(q.get_corner(DL) + DOWN * 0.18, q.get_corner(DR) + DOWN * 0.18,
                  stroke_width=4, color=ACCENT)

        # A caret that walks the two source lines and then drops to the
        # question. Gate A scores shape MOVEMENT, not shape presence: a scene
        # whose shapes are created and then sit still reports "1 distinct
        # shape-state across N frames" and fails, which is strictly worse than
        # having no shapes at all (that is only a warning).
        caret = Rectangle(width=0.10, height=0.36, stroke_width=0,
                          fill_color=ACCENT, fill_opacity=1.0)
        caret.next_to(code[0], LEFT, buff=0.22)

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.7)
        self.play(Create(box), Write(code), run_time=1.8)
        self.play(FadeIn(caret), run_time=0.25)
        self.play(caret.animate.next_to(code[1], LEFT, buff=0.22), run_time=0.45)
        self.play(FadeIn(src), run_time=0.4)
        # Holds are sized to the MEASURED narration (13.63 s here). A scene
        # much shorter than its beat gets stretched by compile.py to fill the
        # audio — B03 was slowed 3.6x, which the compiler itself flagged as
        # "extreme slow-mo". Length the scene honestly instead.
        self.wait(2.2)
        self.play(Write(q), run_time=1.1)
        self.play(caret.animate.next_to(q, LEFT, buff=0.28), Create(ul), run_time=0.6)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.7)
        self.wait(3.9)


# ── B01 ──────────────────────────────────────────────────────────────────────
class B01_Setup(Scene):
    def construct(self):
        page(self)
        head = kicker("WHAT SOFTMAX DOES")

        chips = VGroup(*[
            VGroup(
                RoundedRectangle(width=1.7, height=1.15, corner_radius=0.14,
                                 stroke_color=RULE, stroke_width=2,
                                 fill_color=WHITE, fill_opacity=1.0),
                label(str(v), size=52, color=INK),
            )
            for v in LOGITS
        ]).arrange(DOWN, buff=0.45)
        chips.move_to(LEFT * 5.4)
        in_lab = label("scores", size=24, color=SOFT).next_to(chips, UP, buff=0.35)

        engine = VGroup(
            RoundedRectangle(width=2.8, height=1.9, corner_radius=0.16,
                             stroke_color=INK, stroke_width=3,
                             fill_color=WHITE, fill_opacity=1.0),
            label("softmax", size=34, color=INK),
        ).move_to(LEFT * 1.7)
        engine_note = label("exponentiate, then normalise", size=21, color=SOFT)
        engine_note.next_to(engine, DOWN, buff=0.32)

        a1 = Arrow(chips.get_right(), engine.get_left(), buff=0.30,
                   stroke_width=3, color=SOFT, max_tip_length_to_length_ratio=0.16)

        # probability bars — real values
        # max_w 4.6 with bars centred at x=3.4 pushed the group's left edge to
        # x=0.6, all but touching the softmax box's right edge — the second
        # arrow rendered as an unreadable stub. Narrower bars, moved right.
        bars = VGroup()
        max_w = 3.8
        for v in PROBS:
            row = VGroup()
            bar = Rectangle(width=max(max_w * v, 0.08), height=0.82,
                            stroke_width=0, fill_color=ACCENT, fill_opacity=1.0)
            row.add(bar)
            row.add(label(f"{v:.4f}", size=26, color=INK).next_to(bar, RIGHT, buff=0.25))
            bars.add(row)
        for row in bars:
            row.align_to(bars[0], LEFT)
        bars.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        bars.move_to(RIGHT * 3.2)
        out_lab = label("probabilities", size=24, color=SOFT).next_to(bars, UP, buff=0.35)

        a2 = Arrow(engine.get_right(), bars.get_left(), buff=0.30,
                   stroke_width=3, color=SOFT, max_tip_length_to_length_ratio=0.16)

        foot = label("they are all positive, and they sum to 1",
                     size=26, color=SOFT).to_edge(DOWN, buff=0.75)

        body = VGroup(chips, in_lab, engine, engine_note, a1, a2, bars, out_lab)
        fit(body, h=5.6)

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeIn(in_lab), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in chips],
                                              lag_ratio=0.18), run_time=1.3)
        self.wait(2.0)                      # "give it three numbers…"
        self.play(GrowArrow(a1), run_time=0.5)
        self.play(FadeIn(engine), Write(engine_note), run_time=1.0)
        self.wait(2.5)                      # "…two moves: exponentiate, then divide"
        self.play(GrowArrow(a2), run_time=0.5)
        self.play(FadeIn(out_lab), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(r[0], LEFT) for r in bars], lag_ratio=0.2),
                  run_time=1.4)
        self.wait(3.0)                      # "bigger scores get more probability"
        self.play(LaggedStart(*[FadeIn(r[1]) for r in bars], lag_ratio=0.2), run_time=0.9)
        self.wait(2.5)                      # the three real values land
        self.play(FadeIn(foot, shift=UP * 0.15), run_time=0.7)
        self.wait(5.8)


# ── B02 ──────────────────────────────────────────────────────────────────────
class B02_Shift(Scene):
    """The four-stage chain. Every value is real."""

    def construct(self):
        page(self)
        head = kicker("EVERY INTERMEDIATE MOVES")

        col_x = [-5.15, -1.85, 1.55, 5.15]
        headers = ["raw", f"− max ({PEAK})", "exp( · )", f"÷ {TOTAL_SHIFTED:.4f}"]
        cols = [
            [str(v) for v in LOGITS],
            [str(v) for v in SHIFTED],
            [f"{v:.4f}" for v in EXP_SHIFTED],
            [f"{v:.4f}" for v in PROBS],
        ]
        row_y = [1.30, 0.35, -0.60]

        head_row = VGroup()
        for x, h in zip(col_x, headers):
            t = label(h, size=27, color=SOFT).move_to([x, 2.25, 0])
            head_row.add(t)

        hr = rule_line(12.0).move_to([0, 1.82, 0])

        cells = VGroup()
        col_groups = []
        for ci, (x, vals) in enumerate(zip(col_x, cols)):
            g = VGroup()
            for y, v in zip(row_y, vals):
                col = ACCENT if ci == 3 else INK
                g.add(label(v, size=32, color=col).move_to([x, y, 0]))
            col_groups.append(g)
            cells.add(g)

        arrows = VGroup()
        for i in range(3):
            mid = (col_x[i] + col_x[i + 1]) / 2
            arrows.add(Arrow([mid - 0.42, 0.35, 0], [mid + 0.42, 0.35, 0],
                             buff=0, stroke_width=3, color=RULE,
                             max_tip_length_to_length_ratio=0.35))

        # Bottom band: the final distribution as bars.
        #
        # Placed by EXPLICIT coordinates. The first version built each row with
        # next_to(), then VGroup.arrange(DOWN) — which re-centres rows of
        # differing width — then shifted each row to re-align the bars. The
        # result put a value label on top of a bar (Gate B "label on a
        # curve/line") and pushed the band to y=-4.12, off-frame. Arithmetic on
        # known extents is easier to keep inside +/-3.4 than layout helpers.
        band = VGroup()
        bar_x0, max_w = -1.60, 6.40
        row_y = [-1.72, -2.42, -3.10]
        for i, v in enumerate(PROBS):
            y = row_y[i]
            bar = Rectangle(width=max(max_w * v, 0.08), height=0.44,
                            stroke_width=0, fill_color=ACCENT, fill_opacity=1.0)
            bar.move_to([bar_x0 + bar.width / 2, y, 0])
            name = label(f"score {LOGITS[i]}", size=21, color=SOFT)
            name.move_to([bar_x0 - 0.32 - name.width / 2, y, 0])
            val = label(f"{v:.4f}", size=23, color=INK)
            val.move_to([bar_x0 + bar.width + 0.32 + val.width / 2, y, 0])
            band.add(VGroup(name, bar, val))

        # sum sits ABOVE the band, between grid and bars — below it there is no
        # room left inside the safe area
        sums = label(f"sum = {sum(PROBS):.16f}", size=20, color=SOFT)
        sums.move_to([3.30, -1.12, 0])

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.play(Create(hr), run_time=0.5)

        # Establish the whole grid frame FIRST — all four headers and the row
        # names. Revealing headers one at a time left the content bounding box
        # narrow for the first half of the beat; Gate V samples at 50% and
        # measured 53% coverage against its 55% underfill floor.
        self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.15) for h in head_row],
                              lag_ratio=0.12), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(r[0]) for r in band], lag_ratio=0.12), run_time=0.7)

        # One hold per stage, so the viewer can read each column while the
        # narration walks it. 40.23 s of audio — an earlier cut ran 13.9 s
        # and was stretched 2.9x.
        for i in range(4):
            self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in col_groups[i]],
                                  lag_ratio=0.15), run_time=0.95)
            self.wait(4.3)
            if i < 3:
                self.play(GrowArrow(arrows[i]), run_time=0.35)

        self.wait(0.6)
        self.play(LaggedStart(*[GrowFromEdge(r[1], LEFT) for r in band], lag_ratio=0.2),
                  run_time=1.3)
        self.play(LaggedStart(*[FadeIn(r[2]) for r in band], lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(sums), run_time=0.5)
        self.wait(3.0)
        self.wait(3.0)


# ── B03 ──────────────────────────────────────────────────────────────────────
class B03_Identity(Scene):
    """Agreement to 1.1e-16 — explicitly NOT bit-identity."""

    def construct(self):
        page(self)
        head = kicker("SAME INPUT, TWO ROUTES")

        cx = [-5.55, -2.45, 1.45, 4.85]
        heads = ["", "shifted", "direct", "|difference|"]
        head_row = VGroup()
        for x, h in zip(cx, heads):
            if h:
                head_row.add(label(h, size=25, color=SOFT).move_to([x, 2.45, 0]))
        hr = rule_line(12.0).move_to([0, 2.05, 0])

        rows = VGroup()
        ys = [1.35, 0.35, -0.65]
        for i, y in enumerate(ys):
            rows.add(label(f"score {LOGITS[i]}", size=23, color=SOFT).move_to([cx[0], y, 0]))
            rows.add(label(f"{PROBS[i]!r}", size=24, color=INK).move_to([cx[1], y, 0]))
            rows.add(label(f"{PROBS_DIRECT[i]!r}", size=24, color=INK).move_to([cx[2], y, 0]))
            col = SOFT if DIFFS_SHORT[i] == "0.0" else ACCENT
            rows.add(label(DIFFS_SHORT[i], size=23, color=col).move_to([cx[3], y, 0]))

        hr2 = rule_line(12.0).move_to([0, -1.25, 0])

        verdict = label(f"max |difference| = {MAX_DIFF}", size=30, color=ACCENT)
        verdict.move_to([0, -1.85, 0])
        claim = label("agreement, not identity", size=40, color=INK, weight="BOLD")
        claim.move_to([0, -2.60, 0])
        note = label("two of three components differ in the final digit",
                     size=22, color=SOFT).move_to([0, -3.20, 0])

        whole = VGroup(head_row, hr, rows, hr2, verdict, claim, note)
        fit(whole, h=6.6)

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeIn(head_row), Create(hr), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.12) for r in rows],
                              lag_ratio=0.06), run_time=2.0)
        # 31.84 s of audio. This was the worst offender at 3.6x slow-mo.
        self.wait(6.0)                      # the two columns are read aloud
        self.play(Create(hr2), run_time=0.4)
        self.play(Write(verdict), run_time=1.2)
        self.wait(5.0)                      # "…the same to sixteen decimal places"
        self.play(FadeIn(claim, shift=UP * 0.2), run_time=0.8)
        self.wait(4.0)                      # "agreement, not identity"
        self.play(FadeIn(note), run_time=0.5)
        self.wait(8.0)


# ── B04 ──────────────────────────────────────────────────────────────────────
class B04_WhyBother(Scene):
    def construct(self):
        page(self)
        head = kicker(f"EQUAL LARGE SCORES  ·  {BIG_LOGITS}")

        divider = Line(UP * 2.35, DOWN * 3.05, stroke_width=2, color=RULE)

        # LEFT — the shifted path succeeds
        lt = label("with the shift", size=30, color=INK).move_to([-3.6, 2.05, 0])
        chain = VGroup(
            label(f"{BIG_LOGITS}", size=27, color=INK),
            label(f"− max  →  {SHIFTED[2]}, {SHIFTED[2]}", size=27, color=SOFT),
            label("exp    →  1.0, 1.0", size=27, color=SOFT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34).move_to([-3.6, 0.95, 0])

        lbars = VGroup()
        for v in BIG_PROBS:
            bar = Rectangle(width=3.0 * v, height=0.62, stroke_width=0,
                            fill_color=ACCENT, fill_opacity=1.0)
            lbars.add(VGroup(bar, label(f"{v}", size=26, color=INK)
                             .next_to(bar, RIGHT, buff=0.22)))
        for r in lbars:
            r[0].align_to(lbars[0][0], LEFT)
        lbars.arrange(DOWN, buff=0.36, aligned_edge=LEFT).move_to([-3.9, -1.30, 0])
        lok = label("exactly 0.5 and 0.5", size=26, color=INK).move_to([-3.6, -2.55, 0])

        # RIGHT — the direct path fails
        rt = label("without the shift", size=30, color=INK).move_to([3.6, 2.05, 0])
        rchain = VGroup(
            label("exp(1000)", size=27, color=INK),
            label(f"largest float = {FLOAT_MAX}", size=20, color=SOFT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34).move_to([3.6, 1.05, 0])

        # size 27 centred at x=3.6 put this line's right edge at 6.37, past the
        # +/-6.3 safe extent — it is the longest string in the reel
        err = label(OVERFLOW_MSG, size=23, color=ACCENT)
        errbox = SurroundingRectangle(err, color=ACCENT, stroke_width=2.5,
                                      buff=0.32, corner_radius=0.10)
        errg = VGroup(errbox, err).move_to([3.30, -0.55, 0])
        rnote = label("not a worse answer —\nno answer at all", size=26,
                      color=INK).move_to([3.6, -2.30, 0])

        whole = VGroup(lt, chain, lbars, lok, rt, rchain, errg, rnote, divider)
        fit(whole, h=6.4)

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.play(Create(divider), run_time=0.5)
        self.play(FadeIn(lt), FadeIn(rt), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.15) for c in chain],
                              lag_ratio=0.2), run_time=1.3)
        self.play(LaggedStart(*[GrowFromEdge(r[0], LEFT) for r in lbars], lag_ratio=0.2),
                  run_time=0.9)
        self.play(*[FadeIn(r[1]) for r in lbars], FadeIn(lok), run_time=0.6)
        # 24.94 s of audio
        self.wait(4.0)                      # "…exactly one half and one half"
        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.15) for c in rchain],
                              lag_ratio=0.2), run_time=1.1)
        self.wait(3.0)                      # "…larger than the biggest float"
        self.play(Create(errbox), Write(err), run_time=1.2)
        self.wait(3.0)                      # the real exception lands
        self.play(FadeIn(rnote, shift=UP * 0.15), run_time=0.7)
        self.wait(3.6)


# ── B05 ──────────────────────────────────────────────────────────────────────
class B05_Boundary(Scene):
    """The mandatory boundary statement. Verbatim — do not trim."""

    def construct(self):
        page(self)
        head = kicker("WHAT THIS DOES NOT SHOW")

        l1 = label("This shows the shifted and direct calculations", size=40, color=INK)
        l2 = label("agree on this input.", size=40, color=INK)
        l3 = label("It does not prove the implementation handles", size=40, color=ACCENT)
        l4 = label("every possible numeric input safely —", size=40, color=ACCENT)
        l5 = label("floating-point arithmetic has its own limits,", size=40, color=ACCENT)
        l6 = label("and passing this test is a narrower claim", size=40, color=ACCENT)
        l7 = label("than “numerically stable” in general.", size=40, color=ACCENT)

        body = VGroup(l1, l2, l3, l4, l5, l6, l7).arrange(
            DOWN, aligned_edge=LEFT, buff=0.30)
        # h=5.9 centred at UP*0.30 put the first line's top at y=3.25, above the
        # kicker's bottom edge (~3.17) — "WHAT THIS DOES NOT SHOW" printed on
        # top of "This shows the shifted and direct calculations". No gate
        # caught it; found by looking at the rendered frame.
        fit(body, h=5.4)
        body.move_to(DOWN * 0.10)

        bar = Line(body.get_corner(UL) + LEFT * 0.45 + UP * 0.10,
                   body.get_corner(DL) + LEFT * 0.45 + DOWN * 0.10,
                   stroke_width=5, color=RULE)

        # A marker that steps down the margin as each line lands.
        # Gate A fails a scene whose shape-state never changes ("repeated
        # animation") — a static rule beside static text counts as one state
        # across every sampled frame. The marker is also doing real work: it
        # tracks how far through the qualification the viewer is.
        marker = Rectangle(width=0.14, height=0.40, stroke_width=0,
                           fill_color=ACCENT, fill_opacity=1.0)
        marker.move_to(bar.get_start() + DOWN * 0.22 + RIGHT * 0.0)

        foot = label("one example is evidence — it is not a proof",
                     size=26, color=SOFT).to_edge(DOWN, buff=0.75)

        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.play(Create(bar), run_time=0.5)
        self.play(FadeIn(marker), run_time=0.3)
        # one line per ~1 s, matched to the 22.19 s read of the statement
        for line in body:
            self.play(
                marker.animate.move_to([bar.get_start()[0], line.get_center()[1], 0]),
                FadeIn(line, shift=RIGHT * 0.18),
                run_time=1.0,
            )
        self.wait(3.0)                      # the whole statement sits complete
        self.play(FadeIn(foot, shift=UP * 0.15), run_time=0.8)
        self.wait(8.0)


# ── B06 ──────────────────────────────────────────────────────────────────────
class B06_Close(Scene):
    def construct(self):
        page(self)
        a = label("The intermediates change.", size=58, color=SOFT)
        b = label("The distribution does not.", size=58, color=INK, weight="BOLD")
        body = VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.45)

        foot = label("subtract the max: nothing lost, an overflow avoided",
                     size=30, color=ACCENT)
        foot.next_to(body, DOWN, buff=0.85).align_to(body, LEFT)

        src = label("INFO 7375  ·  lessons/01-randomness-and-first-prompts",
                    size=21, color=SOFT)
        src.next_to(foot, DOWN, buff=0.70).align_to(body, LEFT)

        # grow to fill: at its natural size this recap covered 49% of the safe
        # area and Gate V called underfill on both sampled frames
        whole = VGroup(body, foot, src)
        fill_safe(whole)
        fit(whole)
        whole.move_to(ORIGIN)

        sep = Line(body.get_left() + DOWN * 0.02, body.get_right() + DOWN * 0.02,
                   stroke_width=3, color=RULE)
        sep.move_to([body.get_center()[0], (a.get_bottom()[1] + b.get_top()[1]) / 2, 0])

        # moving marker — see the note in B00_Hook: shapes must CHANGE between
        # sampled frames or Gate A reports a repeated animation
        marker = Rectangle(width=0.12, height=0.42, stroke_width=0,
                           fill_color=ACCENT, fill_opacity=1.0)
        marker.next_to(a, LEFT, buff=0.30)

        self.play(FadeIn(a, shift=UP * 0.2), FadeIn(marker), run_time=1.0)
        self.play(Create(sep), run_time=0.5)
        self.play(marker.animate.next_to(b, LEFT, buff=0.30),
                  FadeIn(b, shift=UP * 0.2), run_time=1.0)
        self.play(Write(foot), run_time=1.3)
        self.play(FadeIn(src), run_time=0.6)
        self.wait(5.4)                      # 10.41 s of audio
