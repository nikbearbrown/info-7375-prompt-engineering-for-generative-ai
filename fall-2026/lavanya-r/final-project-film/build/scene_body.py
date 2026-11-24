
# ═════════════════════════════ README CHECKER — scenes (Lavanya R) ═════════════════════════════
# Cut 4 (2026-11-23): every beat carries a part header for the professor's four parts
# (1 · What and why, 2 · What exists, 3 · Methods, 4 · Evaluation), readable README steps, my REAL
# terminal output for the two runs, and one key sentence. Pacing: each beat builds before ~42% of
# its audio, holds still through the clip midpoint (GATE T / Gate V sample there), then adds its
# payoff after ~58%. `until(self, phrase)` waits for the spoken phrase.
KRAFT_EDGE = "#9C8462"
MONO = "Menlo"


def at(self, frac):
    target = _TARGET.get(type(self).__name__.split("_")[0], 0)
    gap = target * frac - _elapsed(self)
    if target and gap > 0.05:
        self.wait(gap)


def M(s, size=30, color=INK):
    return Text(s, font=MONO, color=color, font_size=size)


def header(s):
    return T(s, size=34).move_to([-6.05, 3.0, 0], aligned_edge=LEFT)


def keyline(s, size=36):
    return T(s, size=size).move_to([0, -3.0, 0])


def xmark(x, y, s=0.15, color=INK, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def warn(x, y, s=0.2):
    return Triangle(color=INK, stroke_width=6, fill_opacity=0).scale(s).move_to([x, y, 0])


def skip(x, y, s=0.17):
    return Line([x - s, y, 0], [x + s, y, 0], color=INK, stroke_width=7)


def mark(kind, x, y):
    return {"ok": lambda: check(x - 0.05, y, s=0.17), "x": lambda: xmark(x, y),
            "warn": lambda: warn(x, y), "skip": lambda: skip(x, y)}[kind]()


def container(ox, oy, s=0.85, w=2.0, d=2.0, h=1.3):
    iso = Iso(ox, oy, s)
    back, front = iso.open_box(0, 0, 0, w, d, h)
    return iso, back, front


def floor_shadow(x, y, w=3.4):
    return Ellipse(width=w, height=0.42, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


def panel(x0, x1, y0, y1):
    """A light terminal / report window: card body, grey title band (never a dark band in an ink card)."""
    body = Rectangle(width=x1 - x0, height=y1 - y0, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                     stroke_width=4).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
    band = Rectangle(width=x1 - x0, height=0.38, fill_color=BAR1, fill_opacity=1, stroke_width=0
                     ).move_to([(x0 + x1) / 2, y1 - 0.19, 0])
    return VGroup(body, band)


def readme_page(x, y, w=2.4, h=3.0, rows=4):
    pg = paper(x, y, w, h)
    top = y + h / 2 - 0.45
    gap = (h - 0.8) / max(1, rows - 1)
    lines = VGroup(*[Line([x - w / 2 + 0.3, top - i * gap, 0], [x + w / 2 - 0.3 - (0.5 if i % 3 == 2 else 0), top - i * gap, 0],
                          color=GHOST, stroke_width=7) for i in range(rows)])
    return VGroup(pg, lines)


def page_rows(x, y, w, h, rows):
    """Row y-positions of readme_page(x, y, w, h, rows)."""
    top = y + h / 2 - 0.45
    gap = (h - 0.8) / max(1, rows - 1)
    return [top - i * gap for i in range(rows)]


def sample_boxes(x0=-5.4, y0=0.55, dx=1.45, dy=1.9, s=0.5):
    """Ten small sample-project boxes in two rows. Returns (VGroup, top points)."""
    boxes, tops = VGroup(), []
    for r in range(2):
        for c in range(5):
            iso = Iso(x0 + c * dx, y0 - r * dy, s)
            boxes.add(iso.box(0, 0, 0, 1.0, 1.0, 0.8))
            tops.append(iso.p(0.5, 0.5, 0.8))
    return boxes, tops


PLANTED = (0, 3, 4, 6, 8)   # which of the ten samples get a planted problem (drawing only)


# ═══════════════════════ PART 1 · EXECUTIVE SUMMARY: what and why (no "how") ═══════════════════════
class BHELLO_Intro(Scene):
    def construct(self):
        sh = floor_shadow(-3.6, -1.85, w=3.0)
        iso, back, front = container(-3.6, -1.7, s=0.75)
        pg = iso.page(0.45, 0.3, 2.4, w=1.1, d=1.4)
        pg.set_z_index(1)
        t1 = T("README Checker", size=60, bold=True).move_to([2.2, 1.0, 0])
        t2 = T("Final project pitch · Lavanya · INFO 7375", size=34).move_to([2.2, 0.0, 0])
        self.play(FadeIn(sh), FadeIn(back), FadeIn(front), FadeIn(pg), Write(t1), run_time=1.0)
        self.play(Write(t2), run_time=0.7)
        at(self, 0.6)
        t3 = T("Nothing is built yet.", size=40).move_to([2.2, -1.3, 0])
        self.play(Write(t3), GrowFromCenter(Dot([t3.get_left()[0] - 0.35, -1.3, 0], radius=0.09, color=TERRA)),
                  pg.animate.shift(DOWN * iso.s * 2.0), run_time=0.8)
        finish(self)


class B00_Problem(Scene):
    def construct(self):
        h = header("1 · What and why: the problem")
        pg = readme_page(-2.0, 0.0, w=4.0, h=4.2, rows=5)
        ys = page_rows(-2.0, 0.0, 4.0, 4.2, 5)
        self.play(FadeIn(h), FadeIn(pg, shift=DOWN * 0.2), run_time=0.8)
        lab = T("README", size=40).move_to([2.6, 1.3, 0])
        self.play(Write(lab), run_time=0.4)
        cur = cursor(0.3, ys[0] + 0.1)
        self.play(FadeIn(cur), run_time=0.2)
        self.play(cur.animate.move_to([0.45, ys[1] - 0.05, 0]), run_time=0.5)
        at(self, 0.58)
        self.play(cur.animate.move_to([0.45, ys[2] - 0.05, 0]), run_time=0.4)
        self.play(Create(xmark(1.15, ys[2], s=0.2)), run_time=0.4)
        k = keyline("Is it me, or the instructions?", size=40)
        self.play(Write(k), run_time=0.6)
        finish(self)


class B00A_WhatItIs(Scene):
    def construct(self):
        h = header("1 · What and why: what I'm building")
        pg = readme_page(-4.4, 0.15, w=2.8, h=3.4, rows=5)
        lab = T("README", size=36).move_to([-4.4, 2.25, 0])
        arr = Arrow([-2.75, 0.15, 0], [-1.05, 0.15, 0], color=INK, stroke_width=6, buff=0)
        self.play(FadeIn(h), FadeIn(pg, shift=DOWN * 0.2), FadeIn(lab), run_time=0.8)
        self.play(GrowArrow(arr), run_time=0.5)
        win = panel(-0.6, 6.0, -1.55, 1.9)
        title = T("report", size=34, bold=True).move_to([-0.2, 1.15, 0], aligned_edge=LEFT)
        self.play(FadeIn(win), FadeIn(title), run_time=0.6)
        rows = [("ok", "step 1  ·  pass"), ("warn", "step 2  ·  warning  ·  why"), ("x", "step 3  ·  fail  ·  why")]
        made = [(mark(k, -0.05, 0.4 - i * 0.7), T(t, size=32).move_to([0.4, 0.4 - i * 0.7, 0], aligned_edge=LEFT))
                for i, (k, t) in enumerate(rows)]
        until(self, "and tell you")
        for m, t in made:
            self.play(Create(m), FadeIn(t), run_time=0.35)
        at(self, 0.6)
        tag = T("reports only  ·  won't fix anything", size=32).move_to([2.7, -2.1, 0])
        k = keyline("Which step is broken, and why.", size=40)
        self.play(FadeIn(tag), Write(k), run_time=0.7)
        finish(self)


class B01_MyRun(Scene):
    def construct(self):
        h = header("1 · Why care? My own README failed")
        pg = readme_page(-2.6, -0.1, w=4.2, h=4.8, rows=7)
        ys = page_rows(-2.6, -0.1, 4.2, 4.8, 7)
        self.play(FadeIn(h), FadeIn(pg, shift=DOWN * 0.2), run_time=0.8)
        src = T("my webapp README · fresh clone · Oct 13, 2026", size=32).move_to([0, -3.05, 0])
        self.play(FadeIn(src), run_time=0.5)
        kinds = ["warn", "ok", "x", "skip", "warn", "x", "x"]
        marks = [mark(k, 0.0, ys[i]) for i, k in enumerate(kinds)]
        notes = {0: "placeholder", 2: "missing file", 6: "503"}
        nt = {i: T(n, size=34).move_to([0.5, ys[i], 0], aligned_edge=LEFT) for i, n in notes.items()}
        until(self, "The clone link")
        for i in range(2):
            self.play(Create(marks[i]), *([FadeIn(nt[i])] if i in nt else []), run_time=0.35)
        at(self, 0.58)
        for i in range(2, 4):
            self.play(Create(marks[i]), *([FadeIn(nt[i])] if i in nt else []), run_time=0.35)
        until(self, "the health check")
        for i in range(4, 7):
            self.play(Create(marks[i]), *([FadeIn(nt[i])] if i in nt else []), run_time=0.35)
        finish(self)


class B01T_Terminal(Scene):
    def construct(self):
        h = header("1 · Why care? My actual terminal output")
        win = panel(-6.0, 6.0, -1.3, 1.9)
        lab = T("real output · Oct 13, 2026", size=32).move_to([0, -1.95, 0])
        self.play(FadeIn(h), FadeIn(win), FadeIn(lab), run_time=0.8)
        L = [M('ERROR: Cannot find "…/config/config.json".'), M("HTTP/1.1 503 Service Unavailable")]
        L[0].move_to([-5.6, 0.85, 0], aligned_edge=LEFT)
        L[1].move_to([-5.6, -0.35, 0], aligned_edge=LEFT)
        bars = [Line([-5.75, l.get_bottom()[1] - 0.12, 0], [l.get_right()[0], l.get_bottom()[1] - 0.12, 0],
                     color=TERRA, stroke_width=5) for l in L]
        at(self, 0.1)
        self.play(FadeIn(L[0]), run_time=0.3)
        self.play(Create(bars[0]), run_time=0.35)
        self.play(FadeIn(L[1]), run_time=0.3)
        self.play(Create(bars[1]), run_time=0.35)
        until(self, "Every engineer")
        k = keyline("The writer can't see it. The next engineer pays for it.")
        self.play(Write(k), run_time=0.6)
        finish(self)


# ═══════════════════════ PART 2 · INTRODUCTION: what exists, then why mine ═══════════════════════
class B02T_Terminal(Scene):
    def construct(self):
        h = header("2 · What exists: following a README by hand")
        win = panel(-6.0, 6.0, -1.3, 1.9)
        lab = T("Heroku's Node.js starter README · real output · Oct 13, 2026", size=32).move_to([0, -1.95, 0])
        self.play(FadeIn(h), FadeIn(win), FadeIn(lab), run_time=0.8)
        L = [M("npm warn EBADENGINE …  npm: '12.x' }"), M("HTTP/1.1 200 OK")]
        L[0].move_to([-5.6, 0.85, 0], aligned_edge=LEFT)
        L[1].move_to([-5.6, -0.35, 0], aligned_edge=LEFT)
        until(self, "worked for me")
        self.play(FadeIn(L[1]), run_time=0.3)
        self.play(Create(check(L[1].get_right()[0] + 0.5, L[1].get_center()[1], s=0.17)), run_time=0.3)
        at(self, 0.38)
        self.play(FadeIn(L[0]), run_time=0.3)
        bar = Line([-5.75, L[0].get_bottom()[1] - 0.1, 0], [L[0].get_right()[0], L[0].get_bottom()[1] - 0.1, 0],
                   color=TERRA, stroke_width=5)
        self.play(Create(bar), run_time=0.4)
        until(self, "By hand, you")
        k = keyline("By hand, you only find what you happen to hit.")
        self.play(Write(k), run_time=0.6)
        finish(self)


class B06_NotCI(Scene):
    def construct(self):
        h = header("2 · What exists: CI pipelines")
        left = panel(-6.0, -0.6, -2.0, 1.75)
        lt = T("my CI pipeline", size=34).move_to([-3.3, 2.2, 0])
        lines = VGroup(*[Line([-5.5, y, 0], [-2.2, y, 0], color=GHOST, stroke_width=7) for y in (0.75, 0.0, -0.75)])
        self.play(FadeIn(h), FadeIn(left), FadeIn(lt), FadeIn(lines), run_time=0.9)
        pg = readme_page(3.1, 0.15, w=4.4, h=3.2, rows=4)
        rt = T("my README", size=34).move_to([3.1, 2.2, 0])
        self.play(FadeIn(pg), FadeIn(rt), run_time=0.8)
        at(self, 0.58)
        cks = VGroup(*[check(-1.4, y, s=0.17) for y in (0.75, 0.0, -0.75)])
        self.play(LaggedStart(*[Create(c) for c in cks], lag_ratio=0.3), run_time=0.8)
        nt = T("never run by CI", size=34).move_to([3.1, -2.05, 0])
        self.play(FadeIn(nt), run_time=0.4)
        k = keyline("CI tests the code, not the instructions a person reads.")
        self.play(Write(k), run_time=0.6)
        finish(self)


def tool_card(x0, x1, name, does, catch):
    """A named prior-work card: name, what it does, and its catch (with a warning mark)."""
    cx = (x0 + x1) / 2
    win = panel(x0, x1, -1.6, 1.9)
    nm = T(name, size=44, bold=True).move_to([cx, 0.95, 0])
    d = T(does, size=32).move_to([cx, 0.05, 0])
    c = T(catch, size=32).move_to([cx - 1.85, -0.8, 0], aligned_edge=LEFT)
    w = warn(cx - 2.2, -0.8)
    return win, nm, d, VGroup(w, c)


class B06A_DocTools(Scene):
    def construct(self):
        h = header("2 · What exists: doc-testing tools")
        a = tool_card(-6.0, -0.3, "Runme", "runs a README's code blocks", "you judge the output")
        b = tool_card(0.3, 6.0, "Doc Detective", "checks docs against the product", "you write the tests first")
        self.play(FadeIn(h), FadeIn(a[0]), Write(a[1]), run_time=0.8)
        self.play(FadeIn(a[2]), run_time=0.4)
        until(self, "but you judge")
        self.play(FadeIn(a[3]), run_time=0.4)
        at(self, 0.4)
        self.play(FadeIn(b[0]), Write(b[1]), FadeIn(b[2]), run_time=0.7)
        at(self, 0.62)
        self.play(FadeIn(b[3]), run_time=0.4)
        src = T("open-source projects on GitHub", size=32).move_to([0, -2.4, 0])
        self.play(FadeIn(src), run_time=0.4)
        finish(self)


def result_card(x0, x1, name, num, what, cite):
    cx = (x0 + x1) / 2
    win = panel(x0, x1, -1.6, 1.9)
    nm = T(name, size=40, bold=True).move_to([cx, 1.1, 0])
    n = T(num, size=72, bold=True).move_to([cx, 0.15, 0])
    w = T(what, size=32).move_to([cx, -0.65, 0])
    c = T(cite, size=32, color=INK).move_to([cx, -2.1, 0])
    return win, nm, n, w, c


class B06B_Agents(Scene):
    def construct(self):
        h = header("2 · What exists: AI agents that set up projects (research)")
        a = result_card(-6.0, -0.3, "ExecutionAgent", "33 / 50", "projects set up and tested",
                        "Bouzenia & Pradel · ISSTA 2025")
        b = result_card(0.3, 6.0, "Installamatic", "21 / 40", "Python projects installed",
                        "Milliken, Kang & Yoo · SANER 2025")
        self.play(FadeIn(h), FadeIn(a[0]), Write(a[1]), run_time=0.8)
        until(self, "thirty three")
        self.play(FadeIn(a[2], scale=1.1), FadeIn(a[3]), FadeIn(a[4]), run_time=0.6)
        until(self, "Installamatic")
        self.play(FadeIn(b[0]), Write(b[1]), FadeIn(b[2], scale=1.1), FadeIn(b[3]), FadeIn(b[4]), run_time=0.8)
        until(self, "Both aim")
        k = keyline("Built to get a project running, not to judge the README.")
        self.play(Write(k), run_time=0.6)
        finish(self)


GAP_ROWS = [("by hand", "ok", "warn", "B06C"),
            ("CI", "x", "x", "CI skips"),
            ("doc tools (Runme, Doc Detective)", "ok", "warn", "doc tools"),
            ("AI setup agents", "warn", "x", "AI agents"),
            ("README Checker (planned)", "ok", "ok", None)]


class B06C_Gap(Scene):
    def construct(self):
        h = header("2 · Why mine is still worth building")
        XA, XB = 1.6, 4.6
        ca = VGroup(T("runs the README", size=32), T("as written", size=32)).arrange(DOWN, buff=0.1).move_to([XA, 2.1, 0])
        cb = VGroup(T("says which", size=32), T("line broke", size=32)).arrange(DOWN, buff=0.1).move_to([XB, 2.1, 0])
        rule = Line([-6.0, 1.5, 0], [6.0, 1.5, 0], color=GHOST, stroke_width=4)
        self.play(FadeIn(h), FadeIn(ca), FadeIn(cb), Create(rule), run_time=0.8)
        made = []
        for i, (name, a, b, _) in enumerate(GAP_ROWS):
            y = 1.0 - i * 0.68
            last = i == len(GAP_ROWS) - 1
            t = T(name, size=34 if last else 32, bold=last).move_to([-5.7, y, 0], aligned_edge=LEFT)
            made.append(VGroup(t, mark(a, XA, y), mark(b, XB, y)))
        dot = Dot([-6.0, 1.0 - 4 * 0.68, 0], radius=0.09, color=TERRA)
        self.play(FadeIn(made[0]), run_time=0.4)
        for i in (1, 2, 3):
            until(self, GAP_ROWS[i][3])
            self.play(FadeIn(made[i]), run_time=0.4)
        at(self, 0.58)
        self.play(FadeIn(made[4]), GrowFromCenter(dot), run_time=0.5)
        until(self, "That's why")
        k = keyline("Run it as written. Say which line broke.")
        self.play(Write(k), run_time=0.6)
        finish(self)


# ═══════════════════════ PART 3 · METHODS: plan, data, steps, resources ═══════════════════════
class B03_WhatItIs(Scene):
    def construct(self):
        h = header("3 · Methods: what I'll build")
        sh = floor_shadow(-2.4, -2.05, w=3.2)
        iso, back, front = container(-2.4, -1.9)
        self.play(FadeIn(h), FadeIn(sh), FadeIn(back), FadeIn(front), run_time=0.8)
        l1 = T("README Checker", size=48, bold=True).move_to([2.8, 1.4, 0])
        l2 = T("a command-line tool", size=34).move_to([2.8, 0.55, 0])
        l3 = T("in a public GitHub repo", size=34).move_to([2.8, -0.05, 0])
        l4 = T("container", size=32).move_to([-2.4, 1.95, 0])
        self.play(Write(l1), FadeIn(l2), FadeIn(l3), FadeIn(l4), run_time=0.9)
        pg = iso.page(0.45, 0.3, 2.6, w=1.1, d=1.4)
        pg.set_z_index(1)
        self.play(FadeIn(pg), run_time=0.4)
        at(self, 0.58)
        self.play(pg.animate.shift(DOWN * iso.s * 2.3), run_time=0.8, rate_func=ease_in)
        k = keyline("Will run every README step inside a throwaway container")
        self.play(Write(k), run_time=0.6)
        finish(self)


class B04_Loop(Scene):
    def construct(self):
        h = header("3 · Methods: the agent loop")
        P = {"run": np.array([-1.6, 1.3, 0]), "read": np.array([1.8, -1.4, 0]), "decide": np.array([-4.2, -1.4, 0])}
        nodes = VGroup(*[Circle(radius=0.42, color=INK, stroke_width=5, fill_color=CARD, fill_opacity=1).move_to(p)
                         for p in P.values()])
        self.play(FadeIn(h), LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.3), run_time=1.0)
        labs = VGroup(T("run one step", size=34).next_to(nodes[0], UP, buff=0.25),
                      T("read the real output", size=34).next_to(nodes[1], RIGHT, buff=0.3),
                      T("decide", size=34).next_to(nodes[2], DOWN, buff=0.25))
        self.play(FadeIn(labs), run_time=0.6)
        order = [("run", "read"), ("read", "decide"), ("decide", "run")]
        arcs = VGroup(*[ArcBetweenPoints(P[a] + (P[b] - P[a]) / np.linalg.norm(P[b] - P[a]) * 0.5,
                                         P[b] - (P[b] - P[a]) / np.linalg.norm(P[b] - P[a]) * 0.5,
                                         angle=-PI / 4, color=KRAFT_EDGE, stroke_width=5) for a, b in order])
        self.play(Create(arcs), run_time=0.8)
        opts = T("continue  ·  stop  ·  mark unclear", size=32).move_to([3.2, 1.6, 0])
        self.play(FadeIn(opts), run_time=0.4)
        at(self, 0.58)
        dot = Dot(arcs[0].get_start(), radius=0.12, color=TERRA)
        self.play(FadeIn(dot), run_time=0.2)
        for a in arcs:
            self.play(MoveAlongPath(dot, a), run_time=0.6, rate_func=linear)
        k = keyline("The AI picks the move. Real commands decide the result.")
        self.play(Write(k), run_time=0.6)
        finish(self)


REPORT_ROWS = [("warn", "step 1  ·  warning  ·  placeholder"),
               ("x", "step 3  ·  fail  ·  missing file"),
               ("warn", "step 5  ·  warning  ·  placeholder")]


class B05_Report(Scene):
    def construct(self):
        h = header("3 · Methods: what it will produce")
        win = panel(-6.0, 6.0, -2.15, 2.25)
        title = T("report.md", size=34, bold=True).move_to([-5.5, 1.45, 0], aligned_edge=LEFT)
        stamp = T("CONSTRUCTED MOCK-UP · not built yet", size=36, bold=True).move_to([0, -2.85, 0])
        self.play(FadeIn(h), FadeIn(win), Write(title), run_time=0.9)
        self.play(FadeIn(stamp), run_time=0.5)
        rows = []
        for i, (k, s) in enumerate(REPORT_ROWS):
            y = 0.5 - i * 0.85
            rows.append((mark(k, -5.3, y), T(s, size=32).move_to([-4.8, y, 0], aligned_edge=LEFT)))
        for m, t in rows[:1]:
            self.play(Create(m), FadeIn(t), run_time=0.35)
        at(self, 0.58)
        for m, t in rows[1:]:
            self.play(Create(m), FadeIn(t), run_time=0.35)
        finish(self)


class B05A_Samples(Scene):
    def construct(self):
        h = header("3 · Methods: where the data comes from")
        boxes, tops = sample_boxes()
        l1 = T("~10 small sample projects I'll make", size=32).move_to([-2.5, 2.25, 0])
        self.play(FadeIn(h), LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in boxes], lag_ratio=0.08),
                  FadeIn(l1), run_time=1.3)
        until(self, "Half get")
        sparks = VGroup(*[Dot(tops[i], radius=0.09, color=TERRA) for i in PLANTED])
        l2 = T("dot = one problem I plant", size=32).move_to([-2.5, -2.3, 0])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in sparks], lag_ratio=0.2), FadeIn(l2), run_time=0.8)
        at(self, 0.58)
        win = panel(1.4, 6.2, -1.5, 1.7)
        kt = T("answer key", size=34, bold=True).move_to([1.75, 0.95, 0], aligned_edge=LEFT)
        k1 = T("5 broken: which line", size=32).move_to([1.75, 0.15, 0], aligned_edge=LEFT)
        k2 = T("5 working: no problem", size=32).move_to([1.75, -0.6, 0], aligned_edge=LEFT)
        self.play(FadeIn(win), FadeIn(kt), FadeIn(k1), FadeIn(k2), run_time=0.6)
        until(self, "So I know")
        k = keyline("I know the right answer before the tool runs.")
        self.play(Write(k), run_time=0.6)
        finish(self)


PLAN = [("Runner: one sample README in a container", "report.md with a real exit code per step  ·  first milestone", "One:"),
        ("Agent loop: continue, stop, or unclear", "with a prompt contract my code checks", "Two:"),
        ("Samples: ~10 projects and an answer key", "5 with a planted problem, 5 that work", "Three:"),
        ("Evaluation: score against the answer key", "the two numbers in part 4", "Four:")]


class B05B_Plan(Scene):
    def construct(self):
        h = header("3 · Methods: step by step")
        self.play(FadeIn(h), run_time=0.5)
        for i, (main, sub, cue) in enumerate(PLAN):
            y = 1.85 - i * 1.15
            c = Circle(radius=0.34, color=INK, stroke_width=5, fill_color=CARD, fill_opacity=1).move_to([-5.55, y - 0.2, 0])
            n = T(str(i + 1), size=36, bold=True).move_to(c.get_center())
            a = T(main, size=36).move_to([-4.85, y, 0], aligned_edge=LEFT)
            b = T(sub, size=32).move_to([-4.85, y - 0.5, 0], aligned_edge=LEFT)
            until(self, cue)
            self.play(GrowFromCenter(c), FadeIn(n), FadeIn(a), FadeIn(b), run_time=0.5)
        finish(self)


NEED = [("Docker", "installed on my laptop (version 29.1)", "Docker"),
        ("GitHub", "the code goes in a public repo on my account", "the code goes"),
        ("Claude", "Claude Code, university login · already used for a course agent", "the model calls"),
        ("Compute", "my laptop · about one model call per README step", "It's about one")]


class B05C_Resources(Scene):
    def construct(self):
        h = header("3 · Methods: do I have what I need?")
        self.play(FadeIn(h), run_time=0.5)
        for i, (name, detail, cue) in enumerate(NEED):
            y = 1.85 - i * 1.15
            a = T(name, size=38, bold=True).move_to([-5.0, y, 0], aligned_edge=LEFT)
            b = T(detail, size=32).move_to([-5.0, y - 0.5, 0], aligned_edge=LEFT)
            until(self, cue)
            self.play(FadeIn(a), FadeIn(b), run_time=0.4)
            self.play(Create(check(-5.6, y - 0.2, s=0.2)), run_time=0.3)
        finish(self)


class B11_Risk(Scene):
    def construct(self):
        h = header("3 · Methods: keeping it safe")
        sh = floor_shadow(-3.6, -1.95, w=3.0)
        iso = Iso(-3.6, -1.8, 0.75)
        bx = iso.box(0, 0, 0, 2.0, 2.0, 1.3)
        lc = iso.p(1.0, 0.0, 0.55)
        body = Rectangle(width=0.6, height=0.48, fill_color=DIM, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to(lc)
        shack = Arc(radius=0.21, start_angle=0, angle=PI, color=INK, stroke_width=7).move_to(lc + np.array([0, 0.36, 0]))
        self.play(FadeIn(h), FadeIn(sh), FadeIn(bx), FadeIn(body), Create(shack), run_time=0.8)
        risk = T("risk: a README can contain any command", size=32).move_to([2.2, 2.2, 0])
        f1 = T("disposable container", size=32).move_to([1.0, 1.25, 0], aligned_edge=LEFT)
        f2 = T("no secrets, no access to my files", size=32).move_to([1.0, 0.6, 0], aligned_edge=LEFT)
        f3 = T("deleted after every run", size=32).move_to([1.0, -0.05, 0], aligned_edge=LEFT)
        self.play(FadeIn(risk), run_time=0.4)
        self.play(FadeIn(f1), FadeIn(f2), FadeIn(f3), run_time=0.6)
        at(self, 0.58)
        old = VGroup(bx, body, shack)
        self.play(old.animate.shift(LEFT * 1.6).set_opacity(0), run_time=0.6)
        fresh = iso.box(0, 0, 0, 2.0, 2.0, 1.3)
        self.play(FadeIn(fresh, shift=DOWN * 0.3), run_time=0.5)
        v = T('"set up your database"  →  unclear', size=34).move_to([2.6, -1.3, 0])
        self.play(FadeIn(v), run_time=0.4)
        k = keyline("Vague steps get marked unclear, not guessed.")
        self.play(Write(k), run_time=0.5)
        finish(self)


# ═══════════════════════ PART 4 · EVALUATION: what I'll measure, what counts ═══════════════════════
class B08_Eval(Scene):
    def construct(self):
        h = header("4 · Evaluation: what I'll measure")
        pa = readme_page(-5.0, 0.35, w=2.2, h=2.8, rows=4)
        la = T("my answer key", size=32).move_to([-5.0, -1.45, 0])
        vs = T("vs", size=40).move_to([-3.3, 0.35, 0])
        pb = readme_page(-1.6, 0.35, w=2.2, h=2.8, rows=4)
        lb = T("its report.md", size=32).move_to([-1.6, -1.45, 0])
        self.play(FadeIn(h), FadeIn(pa, shift=DOWN * 0.2), FadeIn(la), run_time=0.8)
        self.play(FadeIn(vs), FadeIn(pb, shift=DOWN * 0.2), FadeIn(lb), run_time=0.7)
        lab = T("× 10 samples", size=32).move_to([-3.3, 2.2, 0])
        self.play(FadeIn(lab), run_time=0.4)
        at(self, 0.58)
        s1 = T("caught:  ? / 5", size=40).move_to([0.5, 1.0, 0], aligned_edge=LEFT)
        s1b = T("planted, at the right line", size=32).move_to([0.5, 0.4, 0], aligned_edge=LEFT)
        s2 = T("false alarms:  ?", size=40).move_to([0.5, -0.5, 0], aligned_edge=LEFT)
        s2b = T("on the 5 working samples", size=32).move_to([0.5, -1.1, 0], aligned_edge=LEFT)
        self.play(FadeIn(s1), FadeIn(s1b), run_time=0.4)
        until(self, "and false alarms")
        self.play(FadeIn(s2), FadeIn(s2b), run_time=0.4)
        k = keyline("These numbers don't exist yet.")
        self.play(Write(k), run_time=0.5)
        finish(self)


class B08A_Threshold(Scene):
    def construct(self):
        h = header("4 · Evaluation: what counts as working")
        ta = T("It worked if", size=40, bold=True).move_to([-5.55, 2.1, 0], aligned_edge=LEFT)
        ca = check(-5.95, 2.1, s=0.2)
        A = ["at least 4 of 5 planted problems caught", "each at the right README line", "at most 1 false alarm",
             "every verdict from a command that ran"]
        ya = [1.3, 0.65, 0.0, -0.65]
        ia = [T(s, size=32).move_to([-5.55, y, 0], aligned_edge=LEFT) for s, y in zip(A, ya)]
        self.play(FadeIn(h), FadeIn(ta), Create(ca), run_time=0.6)
        until(self, "at least four")
        self.play(FadeIn(ia[0]), run_time=0.35)
        until(self, "at the right line")
        self.play(FadeIn(ia[1]), run_time=0.35)
        until(self, "with at most")
        self.play(FadeIn(ia[2]), run_time=0.35)
        at(self, 0.4)
        self.play(FadeIn(ia[3]), run_time=0.35)
        div = Line([1.6, 2.3, 0], [1.6, -1.0, 0], color=GHOST, stroke_width=4)
        tb = T("It didn't if", size=40, bold=True).move_to([2.35, 2.1, 0], aligned_edge=LEFT)
        cb = xmark(2.0, 2.1, s=0.16)
        ib = [T("3 or fewer caught,", size=32).move_to([2.35, 1.3, 0], aligned_edge=LEFT),
              T("or 2+ false alarms", size=32).move_to([2.35, 0.65, 0], aligned_edge=LEFT)]
        until(self, "Three or fewer")
        self.play(Create(div), FadeIn(tb), Create(cb), FadeIn(ib[0]), run_time=0.5)
        until(self, "or two false")
        self.play(FadeIn(ib[1]), run_time=0.35)
        tag = T("targets set now, before anything is built", size=32).move_to([0, -1.75, 0])
        until(self, "Either way")
        k = keyline("Either way: a write-up of where Claude was wrong.")
        self.play(FadeIn(tag), Write(k), run_time=0.6)
        finish(self)


class B14_Outro(Scene):
    def construct(self):
        sh = floor_shadow(-3.6, -1.85, w=3.0)
        iso, back, front = container(-3.6, -1.7, s=0.75)
        pg = iso.page(0.45, 0.3, 0.9, w=1.1, d=1.4)
        pg.set_z_index(1)
        t1 = T("README Checker", size=56, bold=True).move_to([2.0, 0.6, 0])
        t2 = T("Does the README actually work?", size=36).move_to([2.0, -0.4, 0])
        self.play(FadeIn(sh), FadeIn(back), FadeIn(front), FadeIn(pg), Write(t1), Write(t2), run_time=1.4)
        at(self, 0.58)
        self.play(GrowFromCenter(Dot([2.0, -1.2, 0], radius=0.1, color=TERRA)), run_time=0.4)
        finish(self)
