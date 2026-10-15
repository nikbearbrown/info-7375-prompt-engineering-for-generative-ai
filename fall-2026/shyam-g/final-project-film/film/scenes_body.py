
# ═════════════════════════════ STOPLINE PITCH SCENES ═════════════════════════════
# Written for the StopLine pitch (INFO 7375). Everything above this line is the
# toolkit's iso_kit.py, pasted verbatim as the show-tell skill requires.
# Cast, kept the whole film: the kraft crate (a lot), white record pages
# (evidence), a dark terminal block (the tool), three lanes (the outcomes).
# Timing: at(self, f) waits until fraction f of the measured beat audio.
# Every animation is kept out of the 0.40-0.60 window GATE T and Gate V sample,
# labels land before 0.40, and each scene adds a new shape after 0.60.


def at(self, frac):
    target = _TARGET.get(type(self).__name__.split("_")[0], 0)
    if not target:
        self.wait(0.6)
        return
    gap = target * frac - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def crate(iso, x0, y0, w=1.6, d=1.6, h=1.2):
    """The lot: a closed kraft box with terracotta tape."""
    return VGroup(iso.box(x0, y0, 0, w, d, h), iso.tape(x0, y0, h, w, d))


def record(x, y, w=1.5, h=1.9, n=3):
    """An evidence record: a flat page with scribbled lines. The scribbles are taller
    than the kit default (amp 0.11, not 0.07): GATE T reads them as text runs, and at
    the default height they measured 40-41 px against its 41 px floor."""
    pg = paper(x, y, w, h)
    lw, top = w - 0.5, y + h / 2 - 0.42
    lines = VGroup(*[scribble(x - lw / 2, top - i * 0.42, lw * (0.62 if i == n - 1 else 1.0), amp=0.11)
                     for i in range(n)])
    return VGroup(pg, lines)


def terminal(x, y, w=2.6, h=1.7):
    """The tool: a dark panel with a prompt chevron and a ghost light."""
    body = RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    chev = VGroup(Line([x - w / 2 + 0.3, y + 0.35, 0], [x - w / 2 + 0.5, y + 0.2, 0], color=CARD, stroke_width=6),
                  Line([x - w / 2 + 0.5, y + 0.2, 0], [x - w / 2 + 0.3, y + 0.05, 0], color=CARD, stroke_width=6))
    light = Dot([x + w / 2 - 0.3, y + h / 2 - 0.28, 0], radius=0.08, color=GHOST)
    g = VGroup(body, chev, light)
    g.light = light
    return g


def lane(x, y, w=6.0, h=0.9):
    return RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=CARD, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])


def badge(x, y, r=0.6, lit=True):
    ring = Circle(radius=r, fill_color=BOX_TOP if lit else STAGE, fill_opacity=1,
                  stroke_color=INK if lit else GHOST, stroke_width=4).move_to([x, y, 0])
    return ring


class B00_Crate(Scene):
    def construct(self):
        iso = Iso(-3.6, -2.2, 1.0)
        box = crate(iso, 0, 0)
        shadow = Ellipse(width=3.0, height=0.6, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-3.6, -2.25, 0])
        box.shift(UP * 3)
        self.add(shadow)
        self.play(box.animate.shift(DOWN * 3), run_time=0.8, rate_func=ease_in)
        lot = T("lot", 42).move_to([-3.6, -3.0, 0])
        self.play(FadeIn(lot), run_time=0.4)
        at(self, 0.22)
        sheet = record(0.2, 0.4, 1.7, 2.1)
        recs = VGroup(record(3.6, 1.3, 1.5, 1.7, n=2), record(3.9, -1.0, 1.5, 1.7, n=2))
        self.play(FadeIn(sheet, shift=UP * 0.3), run_time=0.6)
        self.play(FadeIn(recs, shift=UP * 0.3), run_time=0.6)
        lab1 = T("proposed action", 42).move_to([0.2, -1.2, 0])
        lab2 = T("evidence", 42).move_to([3.75, -2.5, 0])
        self.play(FadeIn(lab1), FadeIn(lab2), run_time=0.4)
        at(self, 0.62)
        arrow = Arrow([1.15, 0.4, 0], [2.75, 0.4, 0], color=INK, stroke_width=6, buff=0, max_tip_length_to_length_ratio=0.2)
        self.play(GrowArrow(arrow), run_time=0.7)
        finish(self)


class B01_Parts(Scene):
    def construct(self):
        term = terminal(-4.0, 0.3)
        self.play(FadeIn(term, shift=UP * 0.4), run_time=0.6)
        l1 = T("CLI", 36).move_to([-4.0, -1.2, 0])
        self.play(FadeIn(l1), run_time=0.3)
        at(self, 0.22)
        pages = VGroup(*[record(0.0 + i * 0.18, 0.3 - i * 0.18, 1.6, 2.0, n=2) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.3), run_time=0.9)
        l2 = T("tests", 36).move_to([0.2, -1.6, 0])
        self.play(FadeIn(l2), run_time=0.3)
        at(self, 0.62)
        rep = paper(4.2, 0.3, 1.9, 2.4)
        bars = VGroup(*[Rectangle(width=0.32, height=hgt, fill_color=c, fill_opacity=1, stroke_width=0)
                        .move_to([3.6 + i * 0.45, -0.6 + hgt / 2, 0])
                        for i, (hgt, c) in enumerate([(0.9, BAR1), (1.4, BAR2), (0.6, BAR1)])])
        l3 = T("report", 36).move_to([4.2, -1.6, 0])
        self.play(FadeIn(rep), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), FadeIn(l3), run_time=0.7)
        finish(self)


class B02_Lanes(Scene):
    def construct(self):
        ys = [1.6, 0.0, -1.6]
        names = ["human review", "more evidence", "accept for review"]
        lanes = VGroup(*[lane(0.6, y) for y in ys])
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3) for l in lanes], lag_ratio=0.2), run_time=0.9)
        labs = VGroup(*[T(n, 34).move_to([-4.6, y, 0]) for n, y in zip(names, ys)])
        self.play(FadeIn(labs), run_time=0.4)
        marker = Square(side_length=0.5, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([0.6, -1.6, 0])
        self.play(FadeIn(marker), run_time=0.3)
        at(self, 0.62)
        self.play(marker.animate.move_to([0.6, 0.0, 0]), run_time=0.4)
        self.play(marker.animate.move_to([0.6, 1.6, 0]), run_time=0.4)
        dot = Dot([3.2, 1.6, 0], radius=0.14, color=TERRA)
        self.play(GrowFromCenter(dot), run_time=0.4)
        finish(self)


class B03_Run(Scene):
    def construct(self):
        panel = RoundedRectangle(width=9.6, height=4.0, corner_radius=0.15, fill_color=DARK_TOP, fill_opacity=1,
                                 stroke_color=INK, stroke_width=4).move_to([0, 0.5, 0])
        self.play(FadeIn(panel), run_time=0.6)
        cap = T("real run · synthetic data", 34).move_to([0, -2.3, 0])
        self.play(FadeIn(cap), run_time=0.3)
        at(self, 0.2)
        # Three lines copied from reports/cli_output.txt and reports/test_run.txt (run 2026-10-14).
        lines = ["INC-001  ACCEPT FOR REVIEW", "INC-003  HUMAN REVIEW REQUIRED", "Ran 12 tests   OK"]
        txt = VGroup(*[Text(s, font="DejaVu Sans Mono", color=CARD, font_size=36) for s in lines]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        if txt.width > 7.4:
            txt.scale_to_fit_width(7.4)
        txt.move_to([-0.5, 0.5, 0])
        self.play(LaggedStart(*[FadeIn(t) for t in txt], lag_ratio=0.35), run_time=1.0)
        at(self, 0.62)
        ok = check(3.9, -0.55, s=0.28, color=TERRA, w=9)
        self.play(Create(ok), run_time=0.5)
        finish(self)


class B04_SAP(Scene):
    def construct(self):
        cols = [-1.8, 2.2]
        heads = VGroup(T("SAP QM", 36).move_to([cols[0], 2.4, 0]), T("StopLine", 36).move_to([cols[1], 2.4, 0]))
        rows = [1.3, 0.3, -0.7, -1.7]
        cells = VGroup(*[RoundedRectangle(width=1.6, height=0.75, corner_radius=0.1, fill_color=CARD, fill_opacity=1,
                                          stroke_color=INK, stroke_width=3).move_to([c, r, 0]) for r in rows for c in cols])
        self.play(FadeIn(heads), FadeIn(cells), run_time=0.8)
        tag = T("sketch", 32).move_to([-5.0, -2.8, 0])
        self.play(FadeIn(tag), run_time=0.3)
        at(self, 0.2)
        ticks = VGroup(*[check(c - 0.1, r, s=0.18) for r in rows[:3] for c in cols])
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), run_time=1.2)
        at(self, 0.62)
        ring = VGroup(*[Circle(radius=0.22, stroke_color=DIM, stroke_width=4).move_to([c, rows[3], 0]) for c in cols])
        self.play(Create(ring), run_time=0.6)
        finish(self)


class B05_Hold(Scene):
    def construct(self):
        iso = Iso(-4.0, -1.6, 0.9)
        box = crate(iso, 0, 0)
        self.play(FadeIn(box, shift=DOWN * 0.3), run_time=0.6)
        bar = Rectangle(width=3.4, height=0.28, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([-4.0, 1.4, 0])
        self.play(FadeIn(bar), run_time=0.4)
        l1 = T("on hold", 36).move_to([-4.0, -2.8, 0])
        self.play(FadeIn(l1), run_time=0.3)
        at(self, 0.22)
        term = terminal(0.6, 0.6, 2.8, 1.8)
        self.play(FadeIn(term, shift=UP * 0.3), run_time=0.6)
        at(self, 0.62)
        rep = record(4.3, 0.4, 1.8, 2.3, n=3)
        l2 = T("report", 36).move_to([4.3, -1.3, 0])
        self.play(FadeIn(rep, shift=LEFT * 0.4), FadeIn(l2), run_time=0.7)
        self.play(term.light.animate.set_color(TERRA), run_time=0.3)
        finish(self)


class B06_Badges(Scene):
    def construct(self):
        xs = [-4.6, -2.3, 0.0, 2.3, 4.6]
        rings = VGroup(*[badge(x, 0.6, lit=i < 3) for i, x in enumerate(xs)])
        self.play(LaggedStart(*[FadeIn(r) for r in rings], lag_ratio=0.15), run_time=0.9)
        labs = VGroup(*[T(n, 34).move_to([x, -0.6, 0]) for n, x in zip(["verify", "evaluate", "escalate"], xs)])
        self.play(FadeIn(labs), run_time=0.4)
        at(self, 0.2)
        dots = VGroup(*[Dot([x, 0.6, 0], radius=0.14, color=TERRA) for x in xs[:3]])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.25), run_time=0.8)
        at(self, 0.62)
        slashes = VGroup(*[Line([x - 0.45, 0.15, 0], [x + 0.45, 1.05, 0], color=DIM, stroke_width=6) for x in xs[3:]])
        self.play(Create(slashes), run_time=0.6)
        finish(self)


class B07_Fence(Scene):
    def construct(self):
        posts = VGroup(*[Rectangle(width=0.16, height=1.2, fill_color=BAR1, fill_opacity=1, stroke_width=0)
                         .move_to([0.0, y, 0]) for y in (-2.2, -0.9, 0.4, 1.7)])
        rail = Line([0, -2.6, 0], [0, 2.4, 0], color=BAR1, stroke_width=6)
        self.play(Create(rail), FadeIn(posts), run_time=0.7)
        l1 = T("out of scope", 34).move_to([-3.3, -2.8, 0])
        l2 = T("first piece", 34).move_to([3.3, -2.8, 0])
        self.play(FadeIn(l1), FadeIn(l2), run_time=0.3)
        at(self, 0.2)
        iso = Iso(-4.6, -0.9, 0.8)
        box = crate(iso, 0, 0)
        model = Iso(-2.0, -0.4, 0.8).mcp(0, 0, 0)
        self.play(FadeIn(box, shift=DOWN * 0.2), FadeIn(model, shift=DOWN * 0.2), run_time=0.7)
        term = terminal(3.3, 0.2)
        self.play(FadeIn(term), run_time=0.5)
        at(self, 0.62)
        glow = Circle(radius=0.22, stroke_color=TERRA, stroke_width=5).move_to(term.light.get_center())
        self.play(term.light.animate.set_color(TERRA), Create(glow), run_time=0.5)
        finish(self)


class B08_Gate(Scene):
    def construct(self):
        # Twelve small crates in two rows (the lot of 1,200); a rope round the first four (400 contained).
        crates = VGroup(*[crate(Iso(0.6 + col * 1.0, -0.4 - row * 1.3, 0.34), 0, 0, 1.5, 1.5, 1.1)
                          for row in range(2) for col in range(6)])
        self.play(LaggedStart(*[FadeIn(c) for c in crates], lag_ratio=0.05), run_time=1.0)
        rope = RoundedRectangle(width=2.2, height=2.7, corner_radius=0.2, stroke_color=TERRA, stroke_width=5,
                                fill_opacity=0).move_to([1.1, -0.85, 0])
        l1 = T("1,200 in lot", 34).move_to([4.3, -2.8, 0])
        self.play(Create(rope), FadeIn(l1), run_time=0.7)
        at(self, 0.2)
        posts = VGroup(*[Rectangle(width=0.22, height=2.2, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0)
                         .move_to([x, 0.1, 0]) for x in (-3.4, -1.6)])
        arm = Rectangle(width=0.18, height=1.8, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-3.4, 2.1, 0])
        ticket = Rectangle(width=1.2, height=0.7, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                           stroke_width=3).move_to([-5.3, 0.1, 0])
        l2 = T("400 contained", 34).move_to([1.1, -2.8, 0])
        self.play(FadeIn(posts), FadeIn(arm), FadeIn(ticket), FadeIn(l2), run_time=0.7)
        at(self, 0.62)
        self.play(ticket.animate.move_to([-0.8, 0.1, 0]), run_time=0.9)
        ok = check(-0.85, 0.9, s=0.2)
        self.play(Create(ok), run_time=0.4)
        finish(self)


class B09_Columns(Scene):
    def construct(self):
        h1 = T("already have", 42).move_to([-3.0, 2.6, 0])
        h2 = T("new to me", 42).move_to([3.0, 2.6, 0])
        base = VGroup(Line([-5.2, -2.6, 0], [-0.8, -2.6, 0], color=INK, stroke_width=4),
                      Line([0.8, -2.6, 0], [5.2, -2.6, 0], color=INK, stroke_width=4))
        self.play(FadeIn(h1), FadeIn(h2), Create(base), run_time=0.7)
        at(self, 0.2)
        left = VGroup(*[record(-3.0 + (i - 0.5) * 1.9, 0.0, 1.5, 1.8, n=2) for i in range(2)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in left], lag_ratio=0.3), run_time=0.8)
        at(self, 0.62)
        right = VGroup(*[record(3.0 + (i - 1) * 1.6, 0.0, 1.3, 1.8, n=2) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in right], lag_ratio=0.3), run_time=0.9)
        finish(self)


class B10_Split(Scene):
    def construct(self):
        divider = Line([0, -2.8, 0], [0, 2.8, 0], color=GHOST, stroke_width=4)
        iso = Iso(-5.4, -1.0, 0.55)
        solid = VGroup(*[crate(iso, i * 2.2, 0, 1.6, 1.6, 1.2) for i in range(4)])
        l1 = T("exists", 36).move_to([-3.0, -2.6, 0])
        self.play(Create(divider), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in solid], lag_ratio=0.2),
                  FadeIn(l1), run_time=1.0)
        l2 = T("will exist", 36).move_to([3.0, -2.6, 0])
        self.play(FadeIn(l2), run_time=0.3)
        at(self, 0.62)
        iso2 = Iso(1.4, -1.0, 0.55)
        ghosts = VGroup(*[iso2.box(i * 2.2, 0, 0, 1.6, 1.6, 1.2, STAGE, STAGE, STAGE, sw=4).set_stroke(DIM)
                          for i in range(3)])
        self.play(LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.25), run_time=0.9)
        finish(self)
