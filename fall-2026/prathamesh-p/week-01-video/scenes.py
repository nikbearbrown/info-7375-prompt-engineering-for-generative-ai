"""Manim scenes for week-01-expected-vs-observed (INFO 7375 Week 1 explainer).

One Scene per Manim beat; class name prefix = beat id (run.sh contract).
Every beat ends exactly on its measured narration duration (actual_duration_s
in beat_sheet.json), so compile.py never has to slow or center-cut a clip.

Numbers on screen come from, and only from:
  * main_output_2026-09-27.txt           -- main.py output (probabilities, counts)
  * evidence/seed7_sequence.json         -- the real seed-7 draw sequence
                                            (counts verified == main.py)
  * evidence/main_output_rerun_2026-09-27.txt -- the real B06 re-run
  * arithmetic on those values (1000 x p, gaps), labelled "computed" on screen
Constructed elements are labelled "constructed" on screen.
No Claude interface, no persona, no channel chip. Counters only, no MathTex.
"""
import hashlib
import json
import os
from pathlib import Path

import manimpango
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedVMobject,
                   FadeIn, FadeOut, Indicate, Line, MarkupText, Rectangle,
                   RoundedRectangle, Scene, SurroundingRectangle, Text,
                   ValueTracker, VGroup, always_redraw, linear)

# All paths are relative to the reel folder (the folder holding this file and
# beat_sheet.json). The toolkit checkout is expected beside it
# (…/week-01-video and …/brutalist.art in the same parent folder).
# run.sh's GATE A executes an isolated copy of scenes.py in a temp folder; only
# there is the reel located via the WEEK01_REEL_DIR environment variable.
HERE = Path(__file__).resolve().parent
if not (HERE / "beat_sheet.json").exists():
    if not os.environ.get("WEEK01_REEL_DIR"):
        raise FileNotFoundError("scenes.py is outside its reel folder; set WEEK01_REEL_DIR to the reel folder")
    HERE = Path(os.environ["WEEK01_REEL_DIR"]).resolve()
FONTS = HERE.parent / "brutalist.art" / "runtime" / "fonts"

# Register the toolkit's bundled fonts by file so Pango never depends on what
# happens to be installed (PT Mono is not installed system-wide on Windows).
# Fail loudly: a silent fallback font would change the rendered video.
for _f in (FONTS / "EB_Garamond" / "static" / "EBGaramond-Regular.ttf",
           FONTS / "PT_Mono" / "PTMono-Regular.ttf"):
    if not _f.exists():
        raise FileNotFoundError(f"bundled font missing: {_f} (is brutalist.art beside this folder?)")
    manimpango.register_font(str(_f))

SERIF, MONO = "EB Garamond", "PT Mono"

# Claude palette (runtime/remotion/src/tokens/claude.ts). SPARK is for shapes
# only (about 2.9:1 on PAGE, too low for text); ACCENT_TEXT is the text accent.
PAGE, INK, SOFT = "#FAF9F5", "#3D3929", "#73705F"
SPARK, ACCENT_TEXT, HAIR, MUTED_FILL = "#D97757", "#A44A32", "#E5E2D9", "#CFCABB"

TIMES, MINUS, DOT, DASH, ELLIPSIS = "\u00d7", "\u2212", "\u00b7", "\u2014", "\u2026"
DISCLOSURE = "Narration: synthetic voice (Kokoro af_bella), not the author"


# ------------------------------------------------------------------ evidence

def _find(rel):
    p = HERE / rel
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def _json(rel):
    return json.loads(_find(rel).read_text(encoding="utf-8"))


def duration(bid):
    for b in _json("beat_sheet.json")["beats"]:
        if b["beat_id"] == bid:
            return float(b.get("actual_duration_s") or b["estimated_duration_s"])
    raise KeyError(bid)


MAIN = _json("main_output_2026-09-27.txt")            # main.py stdout (JSON)
PROBS = MAIN["probabilities"]                         # [p0, p1, p2]
COUNTS = [MAIN["counts"][str(k)] for k in range(3)]   # outcome order: 102, 268, 630
DRAWS = 1000
EXPECTED = [DRAWS * p for p in PROBS]                 # computed: 90.03, 244.73, 665.24
GAPS = [c - e for c, e in zip(COUNTS, EXPECTED)]      # computed: +11.97, +23.27, -35.24


def signed(x):
    return ("+" if x >= 0 else MINUS) + f"{abs(x):.2f}"


# ------------------------------------------------------------------ helpers

def T(s, size=36, color=INK):
    return Text(s, font=SERIF, font_size=size, color=color)


def M(s, size=22, color=INK):
    return Text(s, font=MONO, font_size=size, color=color)


def fit(mob, max_w):
    if mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    return mob


def code_block(lines, size=22, max_w=None, pitch=0.42):
    """Monospace lines with real indentation (leading spaces become x offsets)."""
    cw = M("M" * 20, size).width / 20
    rows = VGroup()
    top = (len(lines) - 1) / 2 * pitch                    # lay out centred: every coord stays in frame
    for i, line in enumerate(lines):
        body = line.lstrip(" ")
        y = top - i * pitch
        if not body:                                      # blank line keeps its slot
            rows.add(M(".", size).set_opacity(0).move_to([0, y, 0]).align_to([0, 0, 0], LEFT))
            continue
        row = M(body, size)
        row.move_to([0, y, 0]).align_to([0, 0, 0], LEFT)
        row.shift(RIGHT * cw * (len(line) - len(body)))
        rows.add(row)
    if max_w and rows.width > max_w:
        rows.scale(max_w / rows.width)
    return rows


# Beat clock. run.sh discovers scenes by regex, and only matches classes that
# subclass Scene directly, so each beat does and @beat attaches these helpers.
def _begin(self, footer=True):
    self.camera.background_color = PAGE
    self.dur = duration(self.BID)
    self.t = 0.0
    if footer:
        self.add(T(DISCLOSURE, 20, SOFT).move_to([-6.2, -3.2, 0], aligned_edge=LEFT))


def _go(self, *anims, rt=0.6, **kw):
    self.play(*anims, run_time=rt, **kw)
    self.t += rt


def _at(self, frac):
    """Wait until frac x the beat's measured audio duration."""
    target = frac * self.dur
    if target - self.t > 0.04:
        self.wait(target - self.t)
        self.t = target


def _finish(self):
    _at(self, 1.0)


def beat(bid):
    def attach(cls):
        cls.BID = bid
        cls.begin, cls.go, cls.at, cls.finish = _begin, _go, _at, _finish
        return cls
    return attach


# ------------------------------------------------------------------ beats

@beat("B00")
class B00_TwoNumbers(Scene):

    def construct(self):
        self.begin()
        kicker = T(f"Same program {DOT} same token {DOT} same run", 34, SOFT).move_to([0, 2.7, 0])
        left = VGroup(fit(T(f"{EXPECTED[2]:.2f}", 150), 5.2),
                      T("expected count", 34),
                      T(f"computed: {DRAWS} {TIMES} p(token 2), main.py", 24, SOFT)
                      ).arrange(DOWN, buff=0.3).move_to([-3.3, 0.3, 0])
        right = VGroup(fit(T(str(COUNTS[2]), 150), 5.2),
                       T("observed count", 34),
                       T("main.py output, seed 7", 24, SOFT)
                       ).arrange(DOWN, buff=0.3).move_to([3.3, 0.3, 0])
        q_left = T("What chance was assigned?", 30, ACCENT_TEXT).move_to([-3.3, -2.2, 0])
        q_right = T("What happened in this run?", 30, ACCENT_TEXT).move_to([3.3, -2.2, 0])

        self.go(FadeIn(kicker), rt=0.8)
        self.at(0.30)
        self.go(FadeIn(left, shift=UP * 0.3), rt=0.7)
        self.at(0.58)
        self.go(FadeIn(right, shift=UP * 0.3), rt=0.7)
        self.at(0.80)
        self.go(FadeIn(q_left), FadeIn(q_right), rt=0.7)
        self.finish()


@beat("B02")
class B02_Mechanism(Scene):
    # main.py lines 9, 14-17, 19, 22-24 verbatim (input checks, lines 10-13 and 20-21, omitted)
    CODE = [
        "def probabilities(logits, temperature=1.0):",
        "    peak = max(logits)",
        "    weights = [math.exp((x - peak) / temperature) for x in logits]",
        "    total = sum(weights)",
        "    return [weight / total for weight in weights]",
        "",
        "def sample(logits, count=1000, seed=7, temperature=1.0):",
        "    rng = random.Random(seed)",
        "    return dict(Counter(rng.choices(range(len(logits)),",
        "                                   probabilities(logits, temperature), k=count)))",
    ]

    def construct(self):
        self.begin()
        header = T(f"main.py {DASH} lines 9{chr(0x2013)}24, input checks omitted", 24, SOFT)
        header.move_to([-6.2, 2.75, 0], aligned_edge=LEFT)
        # code gets most of the frame (readable at 1080p); bars take a compact right column
        code = code_block(self.CODE, 24, max_w=9.0, pitch=0.52)
        code.move_to([-6.2, 0.0, 0], aligned_edge=LEFT)

        xs, base, k = [3.75, 4.75, 5.75], -1.8, 4.5         # 1.0 apart so "token i" labels never touch
        title = M("probabilities([1, 2, 3])", 20).move_to([6.2, 2.75, 0], aligned_edge=RIGHT)
        bars, vals, labels = VGroup(), VGroup(), VGroup()
        for i, (x, p) in enumerate(zip(xs, PROBS)):
            bar = Rectangle(width=0.5, height=p * k, stroke_width=0,
                            fill_color=SPARK if i == 2 else MUTED_FILL, fill_opacity=1)
            bar.move_to([x, base + p * k / 2, 0])
            bars.add(bar)
            vals.add(T(f"{p:.4f}", 22, ACCENT_TEXT if i == 2 else INK).next_to(bar, UP, buff=0.15))
            labels.add(VGroup(T(f"token {i}", 20), T(f"score {i + 1}", 20, SOFT))
                       .arrange(DOWN, buff=0.08).move_to([x, base - 0.45, 0]))
        axis = Line([3.35, base, 0], [6.2, base, 0], color=SOFT, stroke_width=2)

        self.go(FadeIn(header), FadeIn(code, lag_ratio=0.08), rt=1.6)
        self.at(0.30)
        self.go(FadeIn(title), Create(axis), FadeIn(labels), rt=0.6)
        for bar, val in zip(bars, vals):
            self.go(FadeIn(bar, shift=UP * 0.2), FadeIn(val), rt=0.45)
        self.at(0.52)
        self.go(Indicate(bars[2], color=SPARK, scale_factor=1.06), rt=0.8)
        self.at(0.74)
        hl = SurroundingRectangle(VGroup(code[7], code[9]), color=SPARK, buff=0.1, stroke_width=3)
        self.go(Create(hl), rt=0.7)
        self.finish()


@beat("B03")
class B03_ExpectedCount(Scene):

    def construct(self):
        self.begin()
        expr = T(f"{PROBS[2]!r} {TIMES} {DRAWS}", 44).move_to([0, 2.7, 0])
        v = ValueTracker(0.0)
        counter = always_redraw(lambda: T(f"{v.get_value():.2f}", 160).move_to([0, 0.75, 0]))
        row = VGroup(*[T(f"token {i}: {e:.2f}", 34, ACCENT_TEXT if i == 2 else INK)
                       for i, e in enumerate(EXPECTED)]).arrange(RIGHT, buff=1.0).move_to([0, -1.25, 0])
        row_label = T(f"expected counts {DASH} {DRAWS} {TIMES} probability, computed from main.py output",
                      24, SOFT).move_to([0, -1.95, 0])

        self.go(FadeIn(expr), rt=0.6)
        self.add(counter)
        self.go(v.animate.set_value(EXPECTED[2]), rt=2.2)
        final = T(f"{EXPECTED[2]:.2f}", 160).move_to(counter.get_center())
        self.remove(counter)
        self.add(final)
        self.at(0.36)
        self.go(FadeIn(row, lag_ratio=0.3), FadeIn(row_label), rt=1.2)
        self.at(0.64)
        # mark ".24" by colour, not a box: a box edge would cut through the number
        note = T("not an integer", 30, ACCENT_TEXT).next_to(final[3:], UP, buff=0.2)
        self.go(final[3:].animate.set_color(ACCENT_TEXT), FadeIn(note), rt=0.7)
        self.finish()


@beat("B04")
class B04_DrawByDraw(Scene):

    def construct(self):
        self.begin()
        ev = _json("evidence/seed7_sequence.json")
        seq = ev["sequence"]
        assert len(seq) == DRAWS and [seq.count(k) for k in range(3)] == COUNTS
        cum, c = [(0, 0, 0)], [0, 0, 0]
        for s in seq:
            c[s] += 1
            cum.append(tuple(c))

        call = fit(M("random.Random(7).choices(range(3), probabilities([1, 2, 3], 1.0), k=1000)", 20), 12.2)
        call.move_to([0, 3.0, 0])
        call_note = T(f"real sequence {DASH} same call as sample(); counts match main.py", 22, SOFT)
        call_note.move_to([0, 2.5, 0])

        xs, base, top = [-3.5, 0.0, 3.5], -2.2, 3.0
        fps = 24

        def state(i):
            """Bars, count labels and draw counter after exactly i real draws."""
            bars, labels = VGroup(), VGroup()
            for k in range(3):
                h = max(0.002, cum[i][k] / COUNTS[2] * top)
                bars.add(Rectangle(width=1.6, height=h, stroke_width=0, fill_opacity=1,
                                   fill_color=SPARK if k == 2 else MUTED_FILL).move_to([xs[k], base + h / 2, 0]))
                labels.add(T(str(cum[i][k]), 36, ACCENT_TEXT if k == 2 else INK)
                           .move_to([xs[k], base + h + 0.32, 0]))
            drawn = T(f"draw {i} of {DRAWS}", 30, SOFT).move_to([0, 1.9, 0])
            return VGroup(bars, labels, drawn)

        axis = Line([-5.0, base, 0], [5.0, base, 0], color=SOFT, stroke_width=2)
        names = VGroup(*[T(f"token {k}", 26).move_to([xs[k], base - 0.4, 0]) for k in range(3)])
        self.cur = state(0)

        def show(i):
            new = state(i)
            self.remove(self.cur)
            self.add(new)
            self.cur = new

        self.add(axis, names, self.cur)
        self.go(FadeIn(call), FadeIn(call_note), rt=0.6)
        for draw_no, frac in ((1, 0.14), (2, 0.26), (3, 0.40)):
            self.at(frac)
            show(draw_no)
            self.go(Indicate(names[seq[draw_no - 1]], color=SPARK, scale_factor=1.15), rt=0.5)
        first2 = T("draw 3: first token 2", 26, ACCENT_TEXT).move_to([3.5, -0.9, 0])
        self.go(FadeIn(first2), rt=0.4)
        self.at(0.48)
        self.go(FadeOut(first2), rt=0.3)
        # Stream the remaining real draws: one exact cumulative state per frame.
        frames = max(1, round(0.24 * self.dur * fps))
        for j in range(1, frames + 1):
            show(3 + round((DRAWS - 3) * j / frames))
            self.wait(1 / fps)
            self.t += 1 / fps

        labels = self.cur[1]
        for k, frac in enumerate((0.74, 0.82, 0.90)):
            self.at(frac)
            self.go(Indicate(labels[k], color=SPARK if k == 2 else INK, scale_factor=1.2), rt=0.6)
        self.finish()


@beat("B05")
class B05_SideBySide(Scene):

    def construct(self):
        self.begin()
        # GATE T min-size: no standalone "=" runs, and big enough that fit() never shrinks it
        legend = fit(T(f"outline: expected (computed)   {DOT}   filled: observed (main.py, seed 7)",
                       32, SOFT), 12.2).move_to([0, 3.05, 0])
        xs, base, k = [-4.2, 0.0, 4.2], -1.9, 3.0 / EXPECTED[2]
        pairs, gap_labels = [], []
        for i, x in enumerate(xs):
            he, ho = EXPECTED[i] * k, COUNTS[i] * k
            exp_bar = Rectangle(width=0.95, height=he, stroke_color=INK, stroke_width=3, fill_opacity=0)
            exp_bar.move_to([x - 0.55, base + he / 2, 0])
            obs_bar = Rectangle(width=0.95, height=ho, stroke_width=0, fill_opacity=1,
                                fill_color=SPARK if i == 2 else MUTED_FILL)
            obs_bar.move_to([x + 0.55, base + ho / 2, 0])
            ev = T(f"{EXPECTED[i]:.2f}", 24).next_to(exp_bar, UP, buff=0.12)
            ov = T(str(COUNTS[i]), 24).next_to(obs_bar, UP, buff=0.12)
            name = T(f"token {i}", 26).move_to([x, base - 0.35, 0])
            gap = T(f"gap {signed(GAPS[i])}", 30, ACCENT_TEXT if i == 2 else INK).move_to([x, base - 0.85, 0])
            pairs.append(VGroup(exp_bar, obs_bar, ev, ov, name))
            gap_labels.append(gap)
        axis = Line([-5.8, base, 0], [5.8, base, 0], color=SOFT, stroke_width=2)
        total = fit(T(f"{signed(GAPS[0])} + {GAPS[1]:.2f} {MINUS} {abs(GAPS[2]):.2f} = {abs(sum(GAPS)):.2f}"
                      f"   (both rows total {DRAWS})", 30), 12.2).move_to([0, 2.35, 0])
        share = fit(T(f"token 2:  assigned p = {PROBS[2]:.4f}   {DOT}   observed share "
                      f"{COUNTS[2]} / {DRAWS} = {COUNTS[2] / DRAWS:.3f}", 30, ACCENT_TEXT), 12.2).move_to([0, 1.8, 0])

        self.add(axis)
        self.go(FadeIn(legend), rt=0.5)
        for i, frac in enumerate((0.04, 0.20, 0.34)):
            self.at(frac)
            self.go(FadeIn(pairs[i], shift=UP * 0.2), FadeIn(gap_labels[i]), rt=0.6)
        self.at(0.50)
        self.go(FadeIn(total), rt=0.7)
        self.at(0.74)
        self.go(FadeIn(share), rt=0.7)
        self.finish()


@beat("B06")
class B06_Rerun(Scene):

    def construct(self):
        self.begin()
        files = [("run 1", "main_output_2026-09-27.txt"),
                 ("run 2", "evidence/main_output_rerun_2026-09-27.txt")]
        panels, shas, hits = [], [], []
        for (name, rel), x in zip(files, (-3.1, 3.1)):             # panels span +/-0.3..5.9, inside title-safe
            raw = _find(rel).read_bytes()
            lines = raw.decode("utf-8").splitlines()
            body = code_block(lines, 20, max_w=5.0, pitch=0.31)
            body.move_to([x, 0.35, 0])
            frame = RoundedRectangle(corner_radius=0.12, width=5.6, height=body.height + 0.5,
                                     stroke_color=HAIR, stroke_width=2).move_to(body.get_center())
            head = T(f"{name} {DASH} {Path(rel).name}", 22, SOFT).next_to(frame, UP, buff=0.12)
            digest = hashlib.sha256(raw).hexdigest().upper()
            sha = M(f"SHA-256 {digest[:8]}{ELLIPSIS}{digest[-6:]}", 20).next_to(frame, DOWN, buff=0.15)
            row630 = next(i for i, ln in enumerate(lines) if f'"2": {COUNTS[2]}' in ln)
            panels.append(VGroup(frame, head, body))
            shas.append(sha)
            hits.append(body[row630])
        verdict = T(f"byte-identical {DOT} same SHA-256 {DOT} re-run 2026-09-27 on this machine",
                    26, ACCENT_TEXT).move_to([0, -2.6, 0])

        self.go(FadeIn(panels[0]), rt=0.6)
        self.at(0.14)
        self.go(FadeIn(panels[1]), rt=0.6)
        self.at(0.30)
        self.go(FadeIn(shas[0]), FadeIn(shas[1]), rt=0.5)
        self.go(FadeIn(verdict), rt=0.5)
        self.at(0.58)
        boxes = [SurroundingRectangle(h, color=SPARK, buff=0.03, stroke_width=3) for h in hits]
        self.go(*[Create(b) for b in boxes], rt=0.7)
        self.finish()


@beat("B07")
class B07_Boundary(Scene):

    def construct(self):
        self.begin()
        heading = T("What this does not establish", 48).move_to([0, 2.85, 0])
        y, half, span = 0.1, 5.5, 60.0                       # constructed axis: +/-60 draws
        to_x = lambda g: g / span * half
        axis = Line([-half, y, 0], [half, y, 0], color=SOFT, stroke_width=3)
        zero = VGroup(Line([0, y - 0.15, 0], [0, y + 0.15, 0], color=SOFT, stroke_width=3),
                      T("0", 24, SOFT).move_to([0, y - 0.45, 0]))
        axis_name = T(f"token-2 gap: observed {MINUS} expected", 26, SOFT).move_to([5.9, y - 0.45, 0],
                                                                                  aligned_edge=RIGHT)
        dot = Circle(radius=0.14, color=SPARK, fill_color=SPARK, fill_opacity=1).move_to([to_x(GAPS[2]), y, 0])
        dot_label = T(f"{signed(GAPS[2])}  (seed 7, the one real run)", 28, ACCENT_TEXT).move_to(
            [to_x(GAPS[2]) + 0.4, y + 0.6, 0])
        slots = VGroup(*[DashedVMobject(Circle(radius=0.14, color=SOFT, stroke_width=2), num_dashes=10)
                         for _ in range(9)]).arrange(RIGHT, buff=0.35).move_to([0, 1.55, 0])
        slots_label = T("other runs: not measured", 26, SOFT).move_to([0, 2.1, 0])
        crit = DashedVMobject(Rectangle(width=6.6, height=0.9, color=INK, stroke_width=2), num_dashes=40)
        crit.move_to([0, -1.6, 0])
        crit_text = T("acceptance criterion:  ________", 30).move_to(crit.get_center())
        decide = T("decide before you look", 30, ACCENT_TEXT).move_to([0, -2.45, 0])
        constructed = T("axis and slots constructed; one point real", 22, SOFT).move_to([6.2, -3.2, 0],
                                                                                      aligned_edge=RIGHT)

        self.go(FadeIn(heading), rt=0.6)
        self.at(0.10)
        self.go(Create(axis), FadeIn(zero), FadeIn(axis_name), FadeIn(constructed), rt=0.8)
        self.at(0.40)
        self.go(FadeIn(dot, scale=0.5), FadeIn(dot_label), rt=0.6)
        self.at(0.52)
        self.go(FadeIn(slots, lag_ratio=0.15), FadeIn(slots_label), rt=1.0)
        self.at(0.72)
        self.go(Create(crit), FadeIn(crit_text), rt=0.8)
        self.at(0.90)
        self.go(FadeIn(decide), rt=0.5)
        self.finish()


@beat("B08")
class B08_YourTurn(Scene):
    SNIPPET = "evidence/b08_your_turn_snippet.py"    # the exact file that was run and checked

    def construct(self):
        self.begin()
        heading = T("Your turn", 56).move_to([0, 2.85, 0])
        rule = fit(T("Before you run anything, write down how far from 665 is too far.", 34), 12.2)
        rule.move_to([0, 1.95, 0])
        my_rule = T("my rule:", 28, SOFT).move_to([-3.6, 1.15, 0])
        blank = Line([-2.8, 1.05, 0], [3.8, 1.05, 0], color=INK, stroke_width=2)
        where = M("run from: lessons/01-randomness-and-first-prompts/code", 22, SOFT).move_to([0, 0.2, 0])
        lines = _find(self.SNIPPET).read_text(encoding="utf-8").splitlines()
        code = code_block(lines, 26, max_w=9.0, pitch=0.5)
        code.move_to([0, -1.05, 0])
        panel = RoundedRectangle(corner_radius=0.12, width=code.width + 0.8, height=code.height + 0.6,
                                 stroke_color=HAIR, stroke_width=2).move_to(code.get_center())
        note = T(f"suggestion {DASH} results not shown", 30, SOFT).move_to([0, -2.4, 0])

        self.go(FadeIn(heading), rt=0.6)
        self.at(0.08)
        self.go(FadeIn(rule), rt=0.8)
        self.go(FadeIn(my_rule), Create(blank), rt=0.6)
        self.at(0.42)
        self.go(FadeIn(where), FadeIn(panel), FadeIn(code, lag_ratio=0.2), FadeIn(note), rt=1.0)
        self.at(0.84)
        self.go(Indicate(blank, color=SPARK, scale_factor=1.05), rt=0.8)
        self.finish()


@beat("B09")
class B09_Outro(Scene):

    def construct(self):
        self.begin(footer=False)
        title = MarkupText(f'Expected {EXPECTED[2]:.2f}, Observed {COUNTS[2]}'
                           f'<span foreground="{ACCENT_TEXT}">.</span>',
                           font=SERIF, font_size=76, color=INK)
        fit(title, 12.2).move_to([0, 2.1, 0])
        who = T(f"Prathamesh P {DOT} INFO 7375, Week 1", 34).move_to([0, 0.4, 0])
        prov = T("Numbers: main.py, course repo b293224, run 2026-09-27", 26, SOFT).move_to([0, -1.5, 0])
        voice = T(DISCLOSURE, 26, SOFT).move_to([0, -2.2, 0])

        self.go(FadeIn(title, shift=UP * 0.2), rt=0.8)
        self.at(0.45)
        self.go(FadeIn(who), FadeIn(prov), FadeIn(voice), rt=0.8)
        self.finish()
