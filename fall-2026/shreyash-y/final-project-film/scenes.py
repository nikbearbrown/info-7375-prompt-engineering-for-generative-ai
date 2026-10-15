"""
Manim scenes for yadav-shreyash-final-project-pitch-film ("Quote It or Refuse.").

ClaimCheck does not exist yet. Every picture of the tool here is a sketch of the
plan and carries an on-screen CONSTRUCTED / PLANNED label. The only real output
drawn is Dovetail's pytest summary, read verbatim from
evidence/dovetail-pytest-2026-10-07.txt (a separate project, shown as evidence
of an existing skill).

Timing: each scene reads its beat's measured narration length from
beat_sheet.json and places events at fractions of it, so the audio stays the
clock. No MathTex anywhere (no LaTeX needed).
"""

import json
import os
from pathlib import Path

from manim import *

BG = "#F2F0E9"
INK = "#3D3929"
SOFT = "#6B6555"
ACCENT = "#D97757"   # marks only (strokes, rules, arrows)
WARN = "#A44A32"     # accent-coloured TEXT (contrast-safe on cream)
GOOD = "#3C6647"

SERIF = "EB Garamond"
MONO = "Menlo"
SANS = "Helvetica Neue"

FOOT = "Shreyash Yadav  ·  INFO 7375 final project pitch"


def _find(rel: str) -> Path | None:
    env = os.environ.get("CLAIMCHECK_REEL")
    bases = [Path(env)] if env else []
    here = Path(__file__).resolve().parent
    bases += [here, *here.parents]
    for b in bases:
        p = b / rel
        if p.is_file():
            return p
    return None


_bs = _find("beat_sheet.json")
DUR = {}
if _bs:
    for b in json.loads(_bs.read_text())["beats"]:
        if b.get("actual_duration_s"):
            DUR[b["beat_id"]] = float(b["actual_duration_s"])


class Clock:
    """Event timing against the beat's measured audio length."""

    def __init__(self, scene, beat_id):
        scene.camera.background_color = BG
        self.s, self.t = scene, 0.0
        self.total = DUR.get(beat_id, 16.0)

    def play(self, *anims, rt=0.6):
        self.s.play(*anims, run_time=rt)
        self.t += rt

    def until(self, frac):
        gap = frac * self.total - self.t
        if gap > 0.04:
            self.s.wait(gap)
            self.t += gap

    def finish(self):
        self.until(1.0)


def txt(s, size=30, color=INK, font=SANS, **kw):
    return Text(s, font=font, font_size=size, color=color, **kw)


def heading(s):
    return Text(s, font=SERIF, font_size=50, color=INK).to_edge(UP, buff=0.72)


def footer(stamp=None):
    parts = VGroup(txt(FOOT, 18, SOFT))
    if stamp:
        parts.add(txt(stamp, 20, WARN, weight="BOLD"))
    parts.arrange(RIGHT, buff=0.6)
    if parts.width > 12.4:
        parts.scale_to_fit_width(12.4)
    return parts.to_edge(DOWN, buff=0.72)


def box(label, w=2.6, h=1.3, color=INK, size=26, dashed=False, tcolor=None, sw=3):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.12,
                         stroke_color=color, stroke_width=sw)
    if dashed:
        r = DashedVMobject(r, num_dashes=40)
    t = txt(label, size, tcolor or INK)
    if t.width > w - 0.3:
        t.scale_to_fit_width(w - 0.3)
    return VGroup(r, t)


def arrow(a, b, color=INK, buff=0.12, sw=4, tip=0.14):
    return Arrow(a, b, buff=buff, stroke_width=sw, color=color,
                 max_tip_length_to_length_ratio=tip)


# ──────────────────────────────────────────────────────────────────────────
class B02_UncheckedCitation(Scene):
    def construct(self):
        c = Clock(self, "B02")
        page = Rectangle(width=5.8, height=6.0, stroke_color=INK, stroke_width=3,
                         fill_color=WHITE, fill_opacity=0.6).move_to([-3.4, 0.15, 0])
        ptitle = txt("HOMEOWNER POLICY  (synthetic)", 22, INK, weight="BOLD").move_to(
            page.get_top() + DOWN * 0.45)
        rows = ["1   Definitions", "2   Dwelling", "3   Personal property",
                "4   Perils insured against", "4(a)  Fire and smoke",
                "4(c)  Wind and hail", "5   Exclusions", "6   Conditions"]
        lines = VGroup(*[txt(r, 24, SOFT, font=MONO) for r in rows]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22).next_to(ptitle, DOWN, buff=0.3)
        lines.align_to(page, LEFT).shift(RIGHT * 0.4)
        lines[4].shift(RIGHT * 0.6)
        lines[5].shift(RIGHT * 0.6)
        c.play(Create(page), FadeIn(ptitle), rt=0.8)
        c.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in lines], lag_ratio=0.15), rt=1.6)

        c.until(0.22)
        endo = VGroup(
            Rectangle(width=3.4, height=1.0, stroke_color=WARN, stroke_width=2,
                      fill_color=BG, fill_opacity=1),
            txt("ENDORSEMENT E-2\nreplaces 4(a) wording", 20, WARN),
        ).next_to(lines, DOWN, buff=0.15).align_to(page, RIGHT).shift(LEFT * 0.25)
        strike = SurroundingRectangle(lines[4], buff=0.1, color=WARN, stroke_width=2.2)
        c.play(FadeIn(endo, shift=LEFT * 0.6), Create(strike), rt=0.9)

        c.until(0.45)
        bubble = VGroup(
            RoundedRectangle(width=5.2, height=1.9, corner_radius=0.3,
                             stroke_color=INK, stroke_width=3),
            Text("Yes - covered under\nSection 4(b).", font=SERIF, font_size=46,
                 color=INK, t2c={"4(b)": WARN}),
        ).move_to([3.2, 1.6, 0])
        c.play(FadeIn(bubble, shift=UP * 0.2), rt=0.8)

        c.until(0.66)
        a4, a5 = lines[4].get_center(), lines[5].get_center()
        target = [page.get_right()[0] - 0.25, (a4[1] + a5[1]) * 0.5, 0]
        seek = DashedLine(bubble.get_left() + DOWN * 0.3, target, color=WARN,
                          stroke_width=2.2, dash_length=0.18).add_tip(tip_length=0.16)
        c.play(Create(seek), rt=1.0)
        q = Text("?", font=SERIF, font_size=110, color=WARN).move_to([3.2, -1.1, 0])
        none = txt("no Section 4(b) in this policy", 30, WARN).next_to(q, DOWN, buff=0.2)
        c.play(FadeIn(q, scale=1.3), FadeIn(none), rt=0.7)
        c.play(FadeIn(footer("CONSTRUCTED EXAMPLE - synthetic text")), rt=0.4)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B03_Pipeline(Scene):
    def construct(self):
        c = Clock(self, "B03")
        title = heading("What I will build")
        c.play(FadeIn(title), rt=0.5)
        y = 0.15
        q = box("question", 2.2, 1.2).move_to([-5.2, y, 0])
        c.play(FadeIn(q), rt=0.5)
        c.until(0.06)
        form = txt("public GitHub repo  ·  Python + Claude CLI  ·  test set  ·  eval report", 28, INK)
        if form.width > 12.0:
            form.scale_to_fit_width(12.0)
        form.next_to(title, DOWN, buff=0.3)
        c.play(FadeIn(form, shift=DOWN * 0.1), rt=0.6)

        c.until(0.22)
        cl = box("Claude +\nsynthetic\nclaim file", 2.4, 1.7).move_to([-2.3, y, 0])
        c.play(GrowArrow(arrow(q.get_right(), cl.get_left())), FadeIn(cl), rt=0.7)

        c.until(0.42)
        chips = VGroup(*[box(s, 2.3, 0.62, size=24) for s in ("answer", "verbatim quote", "doc id")]
                       ).arrange(DOWN, buff=0.14).move_to([0.75, y, 0])
        c.play(GrowArrow(arrow(cl.get_right(), chips.get_left())),
               LaggedStart(*[FadeIn(ch) for ch in chips], lag_ratio=0.3), rt=1.0)

        c.until(0.46)
        chk = VGroup(RoundedRectangle(width=3.7, height=2.4, corner_radius=0.14,
                                      stroke_color=ACCENT, stroke_width=2.4),
                     txt("checker  (code, not a model)", 22, WARN, weight="BOLD")
                     ).move_to([4.5, y, 0])
        chk[1].scale_to_fit_width(3.3)
        chk[1].move_to(chk[0].get_top() + DOWN * 0.5)
        c.play(GrowArrow(arrow(chips.get_right(), chk.get_left(), ACCENT, sw=2.2, tip=0.12)), Create(chk[0]),
               FadeIn(chk[1]), rt=0.8)
        c1 = txt("[ ] quote found in doc?", 20, INK, font=MONO).move_to(chk[0].get_center() + DOWN * 0.1)
        c2 = txt("[ ] quote has answer?", 20, INK, font=MONO).next_to(c1, DOWN, buff=0.22, aligned_edge=LEFT)
        c.until(0.66)
        c.play(FadeIn(c1), rt=0.4)
        c.until(0.74)
        c.play(FadeIn(c2), rt=0.4)

        c.until(0.85)
        ok = box("PASS\nshown to reader", 3.0, 1.0, GOOD, 24, tcolor=GOOD).move_to([0.9, -2.05, 0])
        bad = box("FAIL - rejected:\n\"not in the documents\"", 3.6, 1.0, ACCENT, 24,
                  tcolor=WARN, sw=2.2).move_to([4.5, -2.05, 0])
        c.play(GrowArrow(arrow(chk.get_bottom() + LEFT * 0.8, ok.get_top(), GOOD)),
               GrowArrow(arrow(chk.get_bottom() + RIGHT * 0.5, bad.get_top(), ACCENT, sw=2.2, tip=0.12)),
               FadeIn(ok), FadeIn(bad), rt=0.8)
        c.play(FadeIn(footer("PLANNED DESIGN - not built")), rt=0.4)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B05_Alternatives(Scene):
    def construct(self):
        c = Clock(self, "B05")
        title = heading("What I tried, and the difference")
        c.play(FadeIn(title), rt=0.5)
        cols_x = [0.6, 3.0, 5.4]
        heads = ["citation\nchecked by code", "ships with\na test set", "refusal\nis a rule"]
        hy = 1.85
        hs = VGroup(*[txt(h, 24, INK, weight="BOLD").move_to([x, hy, 0]) for x, h in zip(cols_x, heads)])
        rule = Line([-6.2, hy - 0.65, 0], [6.2, hy - 0.65, 0], stroke_color=SOFT, stroke_width=2)
        c.play(LaggedStart(*[FadeIn(h) for h in hs], lag_ratio=0.2), Create(rule), rt=1.0)

        rows = [("chat assistant\n+ PDF upload", 0.08, 0.5),
                ("RAG template\n(LlamaIndex / LangChain),\nout of the box", 0.38, -0.75),
                ("ClaimCheck\n(planned)", 0.72, -1.95)]
        for i, (label, frac, y) in enumerate(rows):
            c.until(frac)
            lab = txt(label, 26, WARN if i == 2 else INK, weight="BOLD" if i == 2 else "NORMAL")
            lab.move_to([-4.1, y, 0])
            if lab.width > 4.4:
                lab.scale_to_fit_width(4.4)
            if i < 2:
                marks = VGroup(*[Line([x - 0.35, y, 0], [x + 0.35, y, 0], stroke_color=SOFT,
                                      stroke_width=6) for x in cols_x])
            else:
                marks = VGroup(*[VGroup(Circle(radius=0.32, stroke_color=ACCENT, stroke_width=5),
                                        txt("planned", 18, WARN).shift(DOWN * 0.55)).move_to([x, y - 0.12, 0])
                                 for x in cols_x])
            c.play(FadeIn(lab, shift=RIGHT * 0.3), LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.2), rt=0.9)
        c.play(FadeIn(footer("what I saw in my own tries - not a market survey")), rt=0.4)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B06_FirstMinute(Scene):
    def construct(self):
        c = Clock(self, "B06")
        who = txt("reader: hiring manager, applied-AI / LLM engineer role", 30, INK, weight="BOLD"
                  ).to_edge(UP, buff=0.72)
        c.play(FadeIn(who), rt=0.5)
        steps = [("README.md", 0.24), ("python -m claimcheck eval", 0.30), ("eval_report.md", 0.36)]
        xs = [-4.6, -0.2, 4.4]
        prev = None
        for (s, f), x in zip(steps, xs):
            c.until(f)
            b = box(s, 4.2 if "python" in s else 2.9, 0.8, size=24).move_to([x, 2.2, 0])
            anims = [FadeIn(b)]
            if prev is not None:
                anims.append(GrowArrow(arrow(prev.get_right(), b.get_left())))
            c.play(*anims, rt=0.5)
            prev = b

        rows = [("Q01", "PASS", "Section 4(a), para 2"), ("Q02", "PASS", "Endorsement E-2"),
                ("Q03", "REFUSED", "not in the documents"), ("Q04", "FAIL", "quote not found in doc"),
                ("Q05", "PASS", "Section 5, item 3"), ("Q06", "FAIL", "quote lacks the answer")]

        def row(r):
            col = WARN if r[1] == "FAIL" else (GOOD if r[1] == "PASS" else SOFT)
            return VGroup(txt(r[0], 28, INK, font=MONO), txt(r[1], 28, col, font=MONO, weight="BOLD"),
                          txt(r[2], 28, INK, font=MONO))

        hdr = VGroup(txt("Q", 30, SOFT, font=MONO), txt("result", 30, SOFT, font=MONO),
                     txt("cited clause", 30, SOFT, font=MONO))
        xcol = [-5.4, -3.7, -1.5]
        ys = [0.8 - 0.5 * i for i in range(len(rows))]

        def place(g, y):
            for m, x in zip(g, xcol):
                m.move_to([x, y, 0], aligned_edge=LEFT)
            return g

        place(hdr, 1.3)
        objs = [place(row(r), ys[i]) for i, r in enumerate(rows)]
        c.until(0.39)
        c.play(FadeIn(hdr), LaggedStart(*[FadeIn(o) for o in objs], lag_ratio=0.12), rt=1.2)

        c.until(0.58)
        order = sorted(range(len(rows)), key=lambda i: {"FAIL": 0, "REFUSED": 1, "PASS": 2}[rows[i][1]])
        anims = []
        for new_pos, i in enumerate(order):
            anims.append(objs[i].animate.move_to([objs[i].get_center()[0], ys[new_pos], 0]))
        c.play(*anims, rt=1.0)

        c.until(0.76)
        st = txt("CONSTRUCTED MOCK-UP - no results exist", 36, WARN, weight="BOLD")
        stamp = VGroup(Rectangle(width=st.width + 0.7, height=0.95, stroke_color=ACCENT, stroke_width=6,
                                 fill_color=BG, fill_opacity=1), st).move_to([0, -2.5, 0])
        c.play(FadeIn(stamp, scale=1.15), FadeIn(footer("placeholder rows - not results")), rt=0.6)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B07_SkillsToEvidence(Scene):
    def construct(self):
        c = Clock(self, "B07")
        title = heading("What a reviewer could fairly conclude")
        c.play(FadeIn(title), rt=0.5)
        skills = ["prompt contracts", "source grounding", "evaluation", "failure analysis"]
        files = ["contract + parser", "citation checker", "frozen test set\n+ prompt log", "FAILURES.md"]
        ys = [1.55, 0.5, -0.55, -1.6]
        L = [txt(s, 32, INK, weight="BOLD").move_to([-3.8, y, 0]) for s, y in zip(skills, ys)]
        c.play(LaggedStart(*[FadeIn(l) for l in L], lag_ratio=0.2), rt=1.2)
        c.until(0.30)
        for l, f, y in zip(L, files, ys):
            b = box(f, 3.6, 0.9, SOFT, 26, dashed=True).move_to([3.0, y, 0])
            c.play(GrowArrow(arrow(l.get_right(), b.get_left(), WARN, sw=2.2, tip=0.1)), FadeIn(b), rt=0.55)
        legend = txt("dashed = will exist", 22, SOFT).move_to([3.0, 2.35, 0])
        c.play(FadeIn(legend), rt=0.3)

        c.until(0.62)
        line = Line([-6.2, -2.35, 0], [6.2, -2.35, 0], stroke_color=ACCENT, stroke_width=2.4)
        nc = txt("NOT claimed: that it works on real claims", 32, WARN, weight="BOLD").next_to(line, DOWN, buff=0.18)
        c.play(Create(line), FadeIn(nc), rt=0.8)
        c.until(0.85)
        c.play(FadeIn(footer("synthetic data only")), rt=0.4)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B08_Scope(Scene):
    def construct(self):
        c = Clock(self, "B08")
        xs = [-4.4, 0.0, 4.35]
        heads = ["IN", "OUT, on purpose", "FIRST TO RUN"]
        H = [Text(h, font=SERIF, font_size=40, color=WARN if i == 1 else INK).move_to([x, 2.7, 0])
             for i, (h, x) in enumerate(zip(heads, xs))]
        rules = [Line([x - 1.75, 2.25, 0], [x + 1.75, 2.25, 0], stroke_color=SOFT, stroke_width=2) for x in xs]

        def col(items, x, color=INK):
            return VGroup(*[txt(s, 28, color) for s in items]).arrange(DOWN, buff=0.42).move_to([x, 0.5, 0])

        ins = col(["1 synthetic claim file", "30-50 questions", "at least 1/3 traps"], xs[0])
        outs = col(["deciding coverage", "approve or deny", "real claims or\ncustomer data"], xs[1])
        firsts = col(["1 policy", "10 questions", "the checker"], xs[2])

        c.play(*[FadeIn(h) for h in H], *[Create(r) for r in rules], rt=0.7)
        c.play(LaggedStart(*[FadeIn(i) for i in ins], lag_ratio=0.3), rt=1.2)
        c.until(0.28)
        c.play(LaggedStart(*[FadeIn(o) for o in outs], lag_ratio=0.3), rt=1.0)
        def cross(o):
            cx, cy = o.get_left()[0] - 0.35, o.get_center()[1]
            return VGroup(Line([cx - 0.15, cy - 0.15, 0], [cx + 0.15, cy + 0.15, 0], stroke_color=ACCENT, stroke_width=6),
                          Line([cx - 0.15, cy + 0.15, 0], [cx + 0.15, cy - 0.15, 0], stroke_color=ACCENT, stroke_width=6))
        strikes = [cross(o) for o in outs]
        c.play(*[Create(s) for s in strikes], rt=0.6)

        c.until(0.42)
        head = Circle(radius=0.22, stroke_color=INK, stroke_width=4)
        body = Arc(radius=0.42, start_angle=0, angle=PI, stroke_color=INK, stroke_width=4).next_to(head, DOWN, buff=0.05)
        person = VGroup(head, body)
        lab = txt("a person decides", 28, INK, weight="BOLD")
        who = VGroup(person, lab).arrange(RIGHT, buff=0.3).move_to([xs[1], -2.0, 0])
        c.play(FadeIn(who), rt=0.5)

        c.until(0.60)
        c.play(LaggedStart(*[FadeIn(f) for f in firsts], lag_ratio=0.3), rt=1.0)
        c.until(0.84)
        rep = box("eval_report.md\n(dated)", 3.2, 1.1, ACCENT, 26).move_to([xs[2], -2.0, 0])
        c.play(GrowArrow(arrow(firsts.get_bottom(), rep.get_top(), ACCENT)), FadeIn(rep), rt=0.6)
        c.play(FadeIn(footer("PLAN - nothing here runs yet")), rt=0.3)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B09_Risk(Scene):
    def construct(self):
        c = Clock(self, "B09")
        title = heading("What could sink it")
        c.play(FadeIn(title), rt=0.5)
        pos = {"documents": [-3.1, 1.5, 0], "questions": [-4.8, -1.4, 0], "tool": [-1.4, -1.4, 0]}
        nodes = {}
        for k, p in pos.items():
            nodes[k] = VGroup(box(k, 2.4, 0.95, INK, 30), txt("written by me", 20, SOFT)).arrange(
                DOWN, buff=0.12).move_to(p)
        c.play(LaggedStart(*[FadeIn(n) for n in nodes.values()], lag_ratio=0.35), rt=1.4)
        loop = VGroup(
            CurvedArrow(nodes["documents"][0].get_left(), nodes["questions"][0].get_top(), angle=0.6, color=SOFT),
            CurvedArrow(nodes["questions"][0].get_right(), nodes["tool"][0].get_left(), angle=0.6, color=SOFT),
            CurvedArrow(nodes["tool"][0].get_top(), nodes["documents"][0].get_right(), angle=0.6, color=SOFT),
        )
        c.play(Create(loop), rt=0.8)

        gx = 1.3
        frame = Rectangle(width=0.9, height=4.0, stroke_color=INK, stroke_width=3).move_to([gx, -0.2, 0])
        true_y = -0.6
        tline = DashedLine([gx - 0.75, true_y, 0], [gx + 0.75, true_y, 0], color=INK, stroke_width=3)
        tl = txt("true", 22, SOFT).next_to(tline, LEFT, buff=0.1)
        glab = txt("score", 24, INK).next_to(frame, UP, buff=0.15)
        base = frame.get_bottom()[1]

        def fill(top):
            return Rectangle(width=0.86, height=top - base, stroke_width=0, fill_color=ACCENT,
                             fill_opacity=0.85).move_to([gx, (top + base) / 2, 0])
        f = fill(true_y)
        c.until(0.22)
        c.play(Create(frame), FadeIn(glab), FadeIn(f), Create(tline), FadeIn(tl), rt=0.6)
        c.until(0.34)
        ans = Text("my answer", font=SERIF, font_size=44, color=WARN).move_to([4.4, 2.3, 0])
        c.play(Transform(f, fill(1.5)), FadeIn(ans), rt=1.0)

        mit = [("freeze the test set\nbefore tuning", 0.55), ("1/3 adversarial\nquestions", 0.68),
               ("log every prompt\nchange with its score", 0.80)]
        items = VGroup()
        for i, (s, fr) in enumerate(mit):
            c.until(fr)
            num = Text(str(i + 1), font=SERIF, font_size=44, color=WARN)
            t = txt(s, 24, INK)
            g = VGroup(num, t).arrange(RIGHT, buff=0.25, aligned_edge=UP).move_to([4.4, 1.2 - 1.25 * i, 0])
            g.align_to([2.5, 0, 0], LEFT)
            items.add(g)
            anims = [FadeIn(g, shift=LEFT * 0.3)]
            if i == 0:
                lock = VGroup(RoundedRectangle(width=0.5, height=0.38, corner_radius=0.06, stroke_color=ACCENT,
                                               stroke_width=4),
                              Arc(radius=0.17, start_angle=0, angle=PI, stroke_color=ACCENT, stroke_width=4)
                              .shift(UP * 0.2)).next_to(nodes["questions"], DOWN, buff=0.15)
                anims.append(FadeIn(lock))
            if i == 2:
                anims.append(Transform(f, fill(true_y + 0.15)))
            c.play(*anims, rt=0.7)
        c.play(FadeIn(footer("PLAN - mitigations not yet in place")), rt=0.3)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
class B10_HaveVsNew(Scene):
    def construct(self):
        c = Clock(self, "B10")
        ev = _find("evidence/dovetail-pytest-2026-10-07.txt")
        if ev is None:
            raise FileNotFoundError("evidence/dovetail-pytest-2026-10-07.txt not found; set CLAIMCHECK_REEL")
        raw = ev.read_text().splitlines()
        run_line = next(l for l in raw if l.startswith("# run at:"))
        dots = next(l for l in raw if l.startswith("....") or "[100%]" in l)
        summary = next(l for l in raw if "passed" in l)
        run_when = run_line.split("run at:")[1].split("host")[0].strip()

        title = heading("Why this project: a mix")
        c.play(FadeIn(title), rt=0.5)
        lx, rx = -3.3, 3.5
        lh = Text("already have", font=SERIF, font_size=44, color=INK).move_to([lx, 2.2, 0])
        rh = Text("new to me", font=SERIF, font_size=44, color=WARN).move_to([rx, 2.2, 0])
        div = Line([0.25, 2.5, 0], [0.25, -2.6, 0], stroke_color=SOFT, stroke_width=2)

        c.until(0.08)
        c.play(FadeIn(lh), Create(div), rt=0.5)
        item = txt("LLM + deterministic checker", 30, INK, weight="BOLD").move_to([lx, 1.35, 0])
        c.play(FadeIn(item), rt=0.4)

        c.until(0.30)
        evbox = Rectangle(width=6.2, height=2.6, stroke_color=INK, stroke_width=2,
                          fill_color=WHITE, fill_opacity=0.7).move_to([lx, -0.35, 0])
        d = txt(dots.strip(), 20, GOOD, font=MONO)
        d.scale_to_fit_width(5.7)
        s = txt(summary.strip(), 34, GOOD, font=MONO, weight="BOLD")
        w = txt(f"Dovetail repo  ·  pytest -q  ·  run {run_when}", 20, SOFT, font=MONO)
        if w.width > 5.8:
            w.scale_to_fit_width(5.8)
        VGroup(d, s, w).arrange(DOWN, buff=0.3).move_to(evbox)
        cap = txt("separate project - evidence of a skill, not part of ClaimCheck", 20, SOFT).next_to(evbox, DOWN, buff=0.15)
        if cap.width > 5.8:
            cap.scale_to_fit_width(5.8)
        c.play(Create(evbox), rt=0.4)
        c.play(FadeIn(d), rt=0.4)
        c.play(FadeIn(s), FadeIn(w), FadeIn(cap), rt=0.6)

        c.until(0.62)
        c.play(FadeIn(rh), rt=0.4)
        news = ["Claude API", "prompt contracts", "source-grounded\ntest set"]
        bs = VGroup(*[box(n, 4.2, 1.0, ACCENT, 30, dashed=True) for n in news]).arrange(DOWN, buff=0.3
                                                                                     ).move_to([rx, -0.2, 0])
        c.play(LaggedStart(*[FadeIn(b) for b in bs], lag_ratio=0.3), rt=1.0)
        c.until(0.88)
        c.play(FadeIn(footer("target domain: insurance / health tech")), rt=0.4)
        c.finish()


# ──────────────────────────────────────────────────────────────────────────
# The toolkit's ClaudeTitleOutro hard-codes the instructor's channel handle
# (OUTRO-LOCK.md); the assignment forbids his name or credit line, so the
# outro is drawn here instead.
class BOUT_Title(Scene):
    def construct(self):
        c = Clock(self, "BOUT")
        title = Text("Quote It or Refuse", font=SERIF, font_size=120, color=INK)
        dot = Text(".", font=SERIF, font_size=120, color=WARN)
        t = VGroup(title, dot).arrange(RIGHT, buff=0.04, aligned_edge=DOWN).move_to([0, 1.25, 0])
        rule = Line([-5.6, 0.05, 0], [5.6, 0.05, 0], stroke_color=ACCENT, stroke_width=2.4)
        who = Text("Shreyash Yadav", font=SERIF, font_size=58, color=INK).move_to([0, -0.85, 0])
        course = txt("INFO 7375  ·  Final project pitch  ·  Fall 2026",
                     28, SOFT).move_to([0, -1.75, 0])
        work = txt("ClaimCheck (working title) - nothing built yet", 28, WARN, weight="BOLD").move_to([0, -2.5, 0])
        c.play(FadeIn(t, shift=UP * 0.2), rt=0.7)
        c.play(Create(rule), rt=0.4)
        c.until(0.25)
        tick = Line([-1.0, -1.3, 0], [1.0, -1.3, 0], stroke_color=INK, stroke_width=3)
        c.play(FadeIn(who, shift=UP * 0.15), Create(tick), rt=0.5)
        c.until(0.45)
        frame = SurroundingRectangle(work, buff=0.14, color=WARN, stroke_width=2)
        c.play(FadeIn(course), FadeIn(work), Create(frame), rt=0.6)
        c.finish()
