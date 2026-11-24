

# ═════════════════════════════ job-search-agent-film — body scenes ═════════════════════════════
# Cast kept across the film: job-board boxes, posting CARDS, a verdict SHEET with TAGS, open TRAYS.

def card(x, y, w=0.62, h=0.44, blank=False):
    """A job-posting card: white slab, ink outline; a full card carries ghost lines + a terracotta dot."""
    r = Rectangle(width=w, height=h, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    if blank:
        return VGroup(r)
    l1 = Line([x - w * 0.32, y + h * 0.12, 0], [x + w * 0.2, y + h * 0.12, 0], color=BAR2, stroke_width=4)
    l2 = Line([x - w * 0.32, y - h * 0.14, 0], [x + w * 0.05, y - h * 0.14, 0], color=BAR2, stroke_width=4)
    d = Dot([x + w * 0.3, y - h * 0.14, 0], radius=0.05, color=TERRA)
    return VGroup(r, l1, l2, d)


def tray(ox, oy, s=0.55, w=1.8, h=0.7):
    iso = Iso(ox, oy, s)
    back, front = iso.open_box(0, 0, 0, w, w, h)
    return iso, back, front


def tag(x, y, filled=True):
    return RoundedRectangle(width=0.62, height=0.3, corner_radius=0.15, fill_color=BAR2 if filled else CARD,
                            fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([x, y, 0])


def dashed_box(x, y, w, h):
    return DashedVMobject(Rectangle(width=w, height=h, stroke_color=INK, stroke_width=4), num_dashes=22).move_to([x, y, 0])


def cross(x, y, s=0.18, color=INK, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def arrow(a, b, color=INK, w=5):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0], 0.0])
    head = Polygon(b, b - d * 0.28 + n * 0.14, b - d * 0.28 - n * 0.14, fill_color=color, fill_opacity=1, stroke_color=color, stroke_width=2)
    return VGroup(Line(a, b - d * 0.2, color=color, stroke_width=w), head)


def lines_on(x, y, w, n, gap=0.4, color=BAR2, sw=5):
    """n ghost text lines, left-aligned, starting at (x, y) going down."""
    return VGroup(*[Line([x, y - i * gap, 0], [x + w * (0.92 if i % 3 else 0.7), y - i * gap, 0], color=color, stroke_width=sw) for i in range(n)])


class B01_Agent(Scene):
    def construct(self):
        boards = VGroup()
        for i in range(3):
            iso = Iso(-5.2, 1.2 - i * 1.5, 0.55)
            boards.add(iso.box(0, 0, 0, 1.3, 1.3, 0.8))
        bl = T("job boards", 34).move_to([-4.6, 2.75, 0])
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boards], lag_ratio=0.25), FadeIn(bl), run_time=1.0)
        sheet = paper(2.6, -0.2, w=3.6, h=4.4)
        self.play(FadeIn(sheet), run_time=0.5)
        until(self, "finds the postings")
        nl = T("new postings", 34).move_to([-1.0, 2.75, 0])
        self.play(FadeIn(nl), run_time=0.3)
        ys = [1.2, 0.2, -0.8, -1.8]
        cards = []
        for i, yy in enumerate(ys):
            c = card(-4.4, 1.5 - (i % 3) * 1.5)
            self.play(FadeIn(c), run_time=0.15)
            self.play(c.animate.move_to([1.7, yy, 0]), run_time=0.45)
            cards.append(c)
        until(self, "tells me which")
        tags = VGroup(*[tag(3.6, yy, filled=(i in (1, 3))) for i, yy in enumerate(ys)])
        fl = T("fits?", 34).move_to([3.6, 2.45, 0])
        self.play(LaggedStart(*[GrowFromCenter(t) for t in tags], lag_ratio=0.2), FadeIn(fl), run_time=0.9)
        until(self, "the exact rule")
        lead = Line([4.0, 0.2, 0], [4.55, 0.2, 0], color=INK, stroke_width=4)
        rl = T("rule R3", 34).next_to(lead, RIGHT, buff=0.3)
        dot = Dot([3.6, 0.2, 0], radius=0.07, color=TERRA)
        self.play(Create(lead), FadeIn(rl), GrowFromCenter(dot), run_time=0.6)
        finish(self)


class B02_Silent(Scene):
    def construct(self):
        iso = Iso(-4.6, -2.4, 0.8)
        slabs = VGroup(*[iso.box(0, 0, k * 0.12, 1.6, 1.6, 0.09, PAGE_TOP, PAGE_L, PAGE_R, sw=2) for k in range(22)])
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in slabs], lag_ratio=0.15), run_time=1.6)
        hl = T("hundreds a day", 34).move_to([-4.6, 2.6, 0])
        self.play(FadeIn(hl), run_time=0.3)
        until(self, "says apply")
        stamp = RoundedRectangle(width=1.5, height=0.8, corner_radius=0.12, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-1.3, 1.4, 0])
        al = T("apply ?", 36).next_to(stamp, UP, buff=0.3)
        self.play(GrowFromCenter(stamp), FadeIn(al), run_time=0.6)
        until(self, "silently misses")
        i1, b1, f1 = tray(0.9, -2.0)
        i2, b2, f2 = tray(3.6, -2.0)
        q1 = T("quiet day", 34).next_to(f1, DOWN, buff=0.25)
        q2 = T("quiet day", 34).next_to(f2, DOWN, buff=0.25)
        self.play(FadeIn(b1), FadeIn(f1), FadeIn(b2), FadeIn(f2), FadeIn(q1), FadeIn(q2), run_time=0.8)
        until(self, "looks exactly like")
        miss = dashed_box(4.45, 1.6, 1.4, 1.0)
        link = DashedLine([4.45, 1.05, 0], [4.45, -1.0, 0], color=DIM, stroke_width=4)
        ml = T("missed board", 34).next_to(miss, UP, buff=0.3)
        self.play(Create(miss), Create(link), FadeIn(ml), run_time=0.8)
        until(self, "both mistakes")
        dot = Dot([4.45, 1.6, 0], radius=0.08, color=TERRA)
        self.play(GrowFromCenter(dot), run_time=0.4)
        finish(self)


class B03_Alerts(Scene):
    def construct(self):
        bar = RoundedRectangle(width=3.4, height=0.7, corner_radius=0.35, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.6, 2.2, 0])
        lens = VGroup(Circle(radius=0.16, stroke_color=INK, stroke_width=4).move_to([-4.9, 2.24, 0]),
                      Line([-4.79, 2.12, 0], [-4.62, 1.96, 0], color=INK, stroke_width=4))
        sl = T("saved search", 34).next_to(bar, UP, buff=0.3)
        self.play(FadeIn(bar), Create(lens), FadeIn(sl), run_time=0.7)
        until(self, "send new postings")
        iso, back, front = tray(-4.6, -2.6, s=0.7, w=1.9, h=0.75)
        self.play(FadeIn(back), FadeIn(front), run_time=0.4)
        dl = T("daily · weekly", 34).move_to([-0.6, -2.9, 0])
        self.play(FadeIn(dl), run_time=0.3)
        for k in range(3):
            c = card(-3.6, 1.2)
            self.play(FadeIn(c), run_time=0.15)
            self.play(c.animate.move_to(iso.p(0.95, 0.95, 0.45 + k * 0.12)), run_time=0.45, rate_func=ease_in)
            self.bring_to_front(front)
        until(self, "do not explain")
        res = paper(3.6, 0.0, w=2.4, h=3.0)
        rl_ = lines_on(2.75, 0.9, 1.6, 5)
        rlab = T("résumé", 34).next_to(res, UP, buff=0.3)
        self.play(FadeIn(res), Create(rl_), FadeIn(rlab), run_time=0.6)
        link = DashedLine([2.2, -0.6, 0], [-1.5, -1.4, 0], color=DIM, stroke_width=4)
        x = cross(0.35, -1.0)
        self.play(Create(link), run_time=0.5)
        self.play(Create(x), run_time=0.3)
        finish(self)


class B04_Score(Scene):
    def construct(self):
        res = paper(-5.0, 1.3, w=1.8, h=2.2)
        job = card(-5.0, -1.4, w=1.6, h=1.1)
        self.play(FadeIn(res), FadeIn(job), Create(lines_on(-5.6, 1.9, 1.2, 4)), run_time=0.7)
        until(self, "reports skills")
        piv = Polygon([1.0, -2.2, 0], [0.55, -3.0, 0], [1.45, -3.0, 0], fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
        beam = Rectangle(width=7.4, height=0.18, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([1.0, -2.1, 0])
        self.play(FadeIn(piv), GrowFromCenter(beam), run_time=0.6)
        names = ["skills", "seniority", "keywords"]
        xs = [-1.6, 1.0, 3.6]
        ws = VGroup()
        for n, xx in zip(names, xs):
            iso = Iso(xx - 0.5, -2.0, 0.5)
            w = iso.box(0, 0, 0, 1.2, 1.2, 0.9)
            lab = T(n, 34).move_to([xx, -0.1 + 0.0, 0]).shift(UP * 0.0)
            lab.move_to([xx, 0.35, 0])
            self.play(FadeIn(w, shift=DOWN * 0.6), FadeIn(lab), run_time=0.45)
            ws.add(w)
        until(self, "How it weighs")
        qs = VGroup(*[T("?", 44).move_to([xx, 1.15, 0]) for xx in xs])
        self.play(LaggedStart(*[FadeIn(q) for q in qs], lag_ratio=0.3), run_time=0.8)
        until(self, "decision aid")
        da = T("decision aid", 36).move_to([1.0, 2.6, 0])
        ul = Line([-0.3, 2.15, 0], [2.3, 2.15, 0], color=TERRA, stroke_width=6)
        self.play(FadeIn(da), Create(ul), run_time=0.6)
        finish(self)


class B05_Gap(Scene):
    def construct(self):
        iso = Iso(-5.2, -2.2, 0.75)
        led = VGroup(*[iso.box(0, 0, k * 0.34, 1.7, 1.7, 0.3, BOX_TOP, BOX_L, BOX_R, sw=3) for k in range(6)])
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in led], lag_ratio=0.2), run_time=1.0)
        pl = T("past filings", 34).move_to([-4.6, 2.6, 0])
        self.play(FadeIn(pl), run_time=0.3)
        until(self, "not what is open")
        post = paper(0.4, -0.1, w=3.0, h=3.8)
        tl = T("today's posting", 34).next_to(post, UP, buff=0.3)
        ls = lines_on(-0.8, 1.1, 2.3, 6)
        self.play(FadeIn(post), FadeIn(tl), Create(ls), run_time=0.8)
        until(self, "names the phrase")
        hi = Rectangle(width=2.3, height=0.3, fill_color=GHOST, fill_opacity=1, stroke_color=INK, stroke_width=2).move_to([0.35, 1.1 - 3 * 0.4, 0])
        self.add(hi)
        self.bring_to_front(ls)
        self.play(GrowFromEdge(hi, LEFT), run_time=0.7)
        until(self, "checkability")
        ck = check(4.3, 0.3, s=0.35, color=TERRA, w=9)
        rl = T("recompute by hand", 34).move_to([4.3, -0.6, 0]).shift(RIGHT * 0.0)
        self.play(Create(ck), FadeIn(rl), run_time=0.7)
        until(self, "never reported as zero")
        zb = dashed_box(4.3, -1.9, 1.2, 0.7)
        z = T("never shown as 0", 34).move_to([4.3, -2.75, 0])
        self.play(Create(zb), FadeIn(z), run_time=0.6)
        finish(self)


class B06_Sources(Scene):
    def construct(self):
        names = ["Greenhouse", "Ashby", "Lever"]
        xs = [-5.0, -2.2, 0.6]
        stacks = []
        for n, xx in zip(names, xs):
            iso = Iso(xx, -0.4, 0.55)
            st, lights = iso.server(-0.7, -0.7, 0, w=1.4, d=1.4)
            lab = T(n, 34).move_to([xx, -1.5, 0])
            self.play(FadeIn(st, shift=UP * 0.2), FadeIn(lights), FadeIn(lab), run_time=0.45)
            stacks.append(lights)
        until(self, "No login")
        self.play(*[l.animate.set_color(TERRA) for l in stacks], run_time=0.5)
        until(self, "My runs used")
        comp = [("Pinterest", -5.0, -2.2), ("Databricks", -5.0, -2.8), ("Ramp", -2.2, -2.2), ("Palantir", 0.6, -2.2)]
        for n, xx, yy in comp:
            self.play(FadeIn(T(n, 32).move_to([xx, yy, 0]), shift=UP * 0.15), run_time=0.3)
        until(self, "fictional persona")
        per = paper(4.4, 0.4, w=2.4, h=3.0)
        pl = lines_on(3.5, 1.3, 1.7, 5)
        lab = T("fictional persona", 34).move_to([4.4, -1.6, 0])
        self.play(FadeIn(per, shift=LEFT * 0.4), Create(pl), FadeIn(lab), run_time=0.7)
        until(self, "stays on my laptop")
        lap = Iso(3.5, -3.0, 0.45).box(0, 0, 0, 2.2, 1.4, 0.15, DARK_TOP, DARK_L, DARK_R)
        self.play(FadeIn(lap), run_time=0.5)
        finish(self)


class B07_Contract(Scene):
    def construct(self):
        con = paper(-4.7, -0.1, w=2.6, h=4.6)
        cl = T("9 checks", 34).next_to(con, UP, buff=0.25)
        self.play(FadeIn(con), FadeIn(cl), run_time=0.6)
        rows = VGroup(*[Line([-5.6, 1.6 - i * 0.43, 0], [-4.0, 1.6 - i * 0.43, 0], color=BAR1, stroke_width=6) for i in range(9)])
        self.play(LaggedStart(*[Create(r) for r in rows], lag_ratio=0.25), run_time=2.4)
        until(self, "Every answer is labelled")
        t1, t2 = tag(-2.3, 0.7, True), tag(-2.3, -0.5, False)
        l1 = T("record", 34).next_to(t1, RIGHT, buff=0.3)
        l2 = T("model judgment", 34).next_to(t2, RIGHT, buff=0.3)
        self.play(GrowFromCenter(t1), FadeIn(l1), run_time=0.4)
        until(self, "model judgment")
        self.play(GrowFromCenter(t2), FadeIn(l2), run_time=0.4)
        until(self, "Step two")
        self.play(FadeOut(VGroup(t1, t2, l1, l2)), run_time=0.4)
        loop = Arc(radius=1.2, start_angle=PI / 2 + 0.35, angle=2 * PI - 0.7, color=INK, stroke_width=6).move_arc_center_to([-0.8, 0.3, 0])
        tip = loop.get_end()
        head = Polygon(tip + np.array([0.0, 0.0, 0]), tip + np.array([-0.3, 0.17, 0]), tip + np.array([-0.3, -0.17, 0]),
                       fill_color=INK, fill_opacity=1, stroke_color=INK, stroke_width=2)
        dot = Dot([-0.8, 0.3, 0], radius=0.1, color=TERRA)
        self.play(Create(loop), FadeIn(head), GrowFromCenter(dot), run_time=1.0)
        until(self, "six boards")
        for i, s in enumerate(["6 boards", "12 requests", "2 min"]):
            bar = Rectangle(width=0.5, height=0.4, fill_color=[BAR1, BAR2, BAR3][i], fill_opacity=1, stroke_color=INK, stroke_width=3).move_to([1.4, 1.2 - i * 0.9, 0])
            self.play(FadeIn(bar), FadeIn(T(s, 34).next_to(bar, RIGHT, buff=0.3)), run_time=0.4)
        until(self, "reads only public")
        fence = dashed_box(1.4, -0.2, 7.4, 3.8)
        self.play(Create(fence), run_time=0.8)
        until(self, "never applies")
        nl = T("never applies, emails or logs in", 34).move_to([1.4, -2.75, 0])
        self.play(FadeIn(nl), run_time=0.5)
        finish(self)


class B08_Plan(Scene):
    def construct(self):
        base = Line([-5.8, -1.8, 0], [5.8, -1.8, 0], color=INK, stroke_width=5)
        self.play(Create(base), run_time=0.7)
        dates = [("Nov 25", -4.4, "filter, score"), ("Dec 1", -1.5, "plan, memory"), ("Dec 13", 1.4, "supervised run"), ("Dec 20", 4.3, "final project")]
        phrases = ["a filter and a score", "a plan, evidence", "a supervised run", "My final project"]
        for i, ((d, x, what), ph) in enumerate(zip(dates, phrases)):
            until(self, ph)
            tick = Line([x, -1.95, 0], [x, -1.65, 0], color=INK, stroke_width=5)
            dl = T(d, 34).move_to([x, -2.5, 0])
            iso = Iso(x - 0.0, -1.75, 0.45)
            stack = VGroup(*[iso.box(-0.8, -0.8, k * 0.5, 1.6, 1.6, 0.45, *(([BOX_TOP, BOX_L, BOX_R]) if k < i else [PAGE_TOP, PAGE_L, PAGE_R])) for k in range(i + 1)])
            wl = T(what, 32).move_to([x, 0.3 if i % 2 == 0 else 1.3, 0])
            self.play(Create(tick), FadeIn(dl), FadeIn(stack, shift=DOWN * 0.3), FadeIn(wl), run_time=0.7)
            if i == 3:
                tp = iso.tape(-0.8, -0.8, 4 * 0.5 - 0.05, 1.6, 1.6)
                self.play(FadeIn(tp), run_time=0.4)
        until(self, "What I need")
        ck = check(5.6, 3.0, s=0.25, color=TERRA)
        self.play(Create(ck), run_time=0.4)
        finish(self)


class B09_Tests(Scene):
    def construct(self):
        sh = paper(-3.8, -0.2, w=3.6, h=4.2)
        self.play(FadeIn(sh), run_time=0.4)
        until(self, "tests written")
        cks = VGroup(*[check(-5.0 + c * 0.75, 1.4 - r * 0.7, s=0.14, w=5) for r in range(5) for c in range(4)])
        self.play(LaggedStart(*[Create(c) for c in cks], lag_ratio=0.08), run_time=1.6)
        pl = T("87 pass", 36).next_to(sh, UP, buff=0.25)
        self.play(FadeIn(pl), run_time=0.3)
        until(self, "does not exist")
        iso = Iso(1.6, 0.6, 0.6)
        bx = iso.box(0, 0, 0, 1.4, 1.4, 0.9)
        b404 = T("404", 40).move_to([3.9, 1.3, 0])
        self.play(FadeIn(bx), run_time=0.4)
        until(self, "returned not found")
        self.play(FadeIn(b404), run_time=0.3)
        until(self, "the run ended")
        a = arrow([1.6, -0.2, 0], [1.6, -1.4, 0])
        inc = T("incomplete", 40).move_to([1.6, -2.0, 0])
        self.play(Create(a), FadeIn(inc), run_time=0.6)
        until(self, "not zero new")
        zn = T("not 0 new", 36).move_to([4.7, -2.0, 0])
        zb = dashed_box(4.7, -0.9, 1.2, 0.6)
        self.play(FadeIn(zn), Create(zb), run_time=0.5)
        finish(self)


class B10_Cross(Scene):
    def construct(self):
        fin = T("agent: finished, 1 job", 36).move_to([-2.6, 2.7, 0])
        ck = check(1.2, 2.7, s=0.2)
        self.play(FadeIn(fin), Create(ck), run_time=0.6)
        base = Line([-5.6, -2.3, 0], [4.6, -2.3, 0], color=INK, stroke_width=4)
        self.play(Create(base), run_time=0.4)
        until(self, "looked across")
        H = 4.0
        bars = [("Greenhouse 1", -3.8, H * 1 / 176, BAR1), ("Ashby 176", -0.4, H, BAR2)]
        for lab, x, h, col in bars:
            b = Rectangle(width=1.5, height=max(0.06, h), fill_color=col, fill_opacity=1, stroke_color=INK, stroke_width=4)
            b.move_to([x, -2.3 + max(0.06, h) / 2, 0])
            self.play(GrowFromEdge(b, DOWN), FadeIn(T(lab, 34).move_to([x, -2.85, 0])), run_time=0.7)
        lv = dashed_box(3.0, -1.9, 1.5, 0.8)
        self.play(Create(lv), FadeIn(T("Lever 404", 34).move_to([3.0, -2.85, 0])), run_time=0.6)
        until(self, "flagged it")
        pole = Line([-3.8, -2.2, 0], [-3.8, 0.4, 0], color=INK, stroke_width=5)
        flag = Polygon([-3.8, 0.4, 0], [-2.9, 0.15, 0], [-3.8, -0.1, 0], fill_color=TERRA, fill_opacity=1, stroke_color=INK, stroke_width=3)
        fl = T("flagged", 36).move_to([-3.6, 1.0, 0])
        self.play(Create(pole), FadeIn(flag), FadeIn(fl), run_time=0.7)
        until(self, "does not mean right")
        x = cross(1.2, 2.7, s=0.25)
        self.play(FadeOut(ck), Create(x), run_time=0.5)
        finish(self)


class B11_Fix(Scene):
    def construct(self):
        W = 10.4
        x0 = -5.2
        seg = W * 364 / 1561
        rest = Rectangle(width=W - seg - 0.1, height=0.9, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x0 + seg + 0.1 + (W - seg - 0.1) / 2, 0.6, 0])
        bad = Rectangle(width=seg, height=0.9, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x0 + seg / 2, 0.6, 0])
        tl = T("1,561 postings", 36).move_to([0.0, 1.8, 0])
        self.play(GrowFromEdge(rest, LEFT), FadeIn(tl), run_time=0.8)
        until(self, "three hundred sixty-four")
        self.play(GrowFromEdge(bad, LEFT), run_time=0.5)
        xs = VGroup(*[cross(x0 + 0.35 + i * (seg - 0.7) / 3, 0.6, s=0.15) for i in range(4)])
        self.play(LaggedStart(*[Create(c) for c in xs], lag_ratio=0.2), run_time=0.7)
        until(self, "spelled in full")
        ex = T("San Francisco, California", 34).move_to([-2.6, -0.9, 0])
        lead = Line([-4.0, -0.5, 0], [-4.0, 0.05, 0], color=INK, stroke_width=4)
        self.play(FadeIn(ex), Create(lead), run_time=0.5)
        until(self, "I predicted")
        pg = paper(3.6, -1.9, w=1.6, h=1.6)
        self.play(FadeIn(pg), Create(lines_on(3.0, -1.5, 1.1, 3)), run_time=0.5)
        until(self, "All three hundred")
        cks = VGroup(*[check(x0 + 0.35 + i * (seg - 0.7) / 3, 0.6, s=0.15, color=INK) for i in range(4)])
        self.play(FadeOut(xs), bad.animate.set_fill(BAR1), run_time=0.4)
        self.play(LaggedStart(*[Create(c) for c in cks], lag_ratio=0.2), run_time=0.6)
        f1 = T("364 fixed", 36).move_to([-3.0, -2.6, 0])
        f2 = T("0 broken", 36).move_to([0.6, -2.6, 0])
        self.play(FadeIn(f1), run_time=0.3)
        until(self, "none broke")
        self.play(FadeIn(f2), run_time=0.3)
        finish(self)


class B12_Criteria(Scene):
    def construct(self):
        p1 = paper(-3.0, 0.5, w=4.2, h=3.2)
        p2 = paper(3.0, 0.5, w=4.2, h=3.2)
        h1 = T("worked", 36).next_to(p1, UP, buff=0.25)
        self.play(FadeIn(p1), FadeIn(h1), run_time=0.5)
        for i in range(3):
            y = 1.5 - i * 0.95
            self.play(Create(check(-4.4, y, s=0.17)), Create(Line([-3.8, y, 0], [-1.4, y, 0], color=BAR2, stroke_width=6)), run_time=0.45)
            if i < 2:
                until(self, ["no posting I labelled", "it beats a lazy rule"][i])
        until(self, "It did not work")
        h2 = T("did not work", 36).next_to(p2, UP, buff=0.25)
        self.play(FadeIn(p2), FadeIn(h2), run_time=0.5)
        for i in range(2):
            y = 1.5 - i * 0.95
            self.play(Create(cross(1.6, y)), Create(Line([2.2, y, 0], [4.6, y, 0], color=BAR2, stroke_width=6)), run_time=0.45)
            if i == 0:
                until(self, "if a relevant job")
        until(self, "a lazy rule would")
        self.play(Create(cross(1.6, -0.4)), Create(Line([2.2, -0.4, 0], [4.6, -0.4, 0], color=BAR2, stroke_width=6)), run_time=0.45)
        until(self, "marking everything")
        s1 = dashed_box(-2.0, -2.45, 1.1, 0.6)
        l1 = T("all relevant", 34).next_to(s1, RIGHT, buff=0.3)
        self.play(Create(s1), FadeIn(l1), run_time=0.5)
        until(self, "or marking nothing")
        s2 = dashed_box(2.6, -2.45, 1.1, 0.6)
        l2 = T("none relevant", 34).next_to(s2, RIGHT, buff=0.3)
        self.play(Create(s2), FadeIn(l2), run_time=0.5)
        finish(self)


class B13_Day2(Scene):
    def construct(self):
        nl = T("34 new", 36).move_to([-4.4, 2.6, 0])
        src = card(-4.4, 1.7, w=0.9, h=0.62)
        self.play(FadeIn(nl), FadeIn(src), run_time=0.5)
        i1, b1, f1 = tray(-3.2, -2.2, s=0.65)
        i2, b2, f2 = tray(2.2, -2.2, s=0.65)
        l1 = T("not relevant", 34).next_to(f1, DOWN, buff=0.25)
        l2 = T("relevant", 34).next_to(f2, DOWN, buff=0.25)
        self.play(FadeIn(b1), FadeIn(f1), FadeIn(l1), FadeIn(b2), FadeIn(f2), FadeIn(l2), run_time=0.6)
        until(self, "None fit")
        for k in range(6):
            c = card(-4.4, 1.7)
            self.add(c)
            self.play(c.animate.move_to(i1.p(0.9 + (k % 3) * 0.2, 0.9, 0.35 + k * 0.08)), run_time=0.35, rate_func=ease_in)
            self.bring_to_front(f1)
        until(self, "only run in tests")
        dl = dashed_box(3.4, 1.2, 1.6, 0.9)
        tl = T("tests only", 34).next_to(dl, UP, buff=0.3)
        self.play(Create(dl), FadeIn(tl), run_time=0.6)
        until(self, "check next")
        dot = Dot([3.4, 1.2, 0], radius=0.09, color=TERRA)
        self.play(GrowFromCenter(dot), run_time=0.4)
        finish(self)
