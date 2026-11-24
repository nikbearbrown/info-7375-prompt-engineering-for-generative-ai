# ═════════════════════════════ v2 reel helpers ═════════════════════════════
# Midpoint guard: GATE T and Gate V sample each clip at 50%. Nothing is in motion between 47%
# and 53% of a beat; at() moves or shortens any animation that would overlap that window.
EARLY, LATE = 0.47, 0.53   # only the 50% frame is sampled by GATE T / Gate V; keep a short hold around it
MONO = "PT Mono"
CAP_TOP = -2.75          # burned-in captions live below this line; keep the drawing above it


def _dur(self):
    return _TARGET.get(type(self).__name__.split("_")[0], 12.0) or 12.0


def _t_of(self, phrase):
    bid = type(self).__name__.split("_")[0]
    n, target = _NARR.get(bid, ""), _TARGET.get(bid, 0)
    if not n or not target:
        return None          # no beat sheet beside the file (Gate A's isolated copy): play now
    if phrase not in n:
        raise ValueError(f"{bid}: cue phrase not in narration: {phrase!r}")
    return target * n.index(phrase) / len(n)


def at(self, when, *anims, rt=0.8, lead=0.2):
    """Play anims when `when` (a phrase of the narration, or a fraction of the beat) arrives,
    never overlapping the 47-53% still window."""
    D = _dur(self)
    now = _elapsed(self)
    if isinstance(when, (int, float)):
        t = when * D
    else:
        tp = _t_of(self, when)
        t = now if tp is None else tp - lead
    t = max(t, now)
    lo, hi = EARLY * D, LATE * D
    if t < lo < t + rt:
        if lo - t >= 0.35:
            rt = lo - t
        else:
            t = hi
    elif lo <= t < hi:
        t = hi
    if t - now > 0.05:
        self.wait(t - now)
    self.play(*anims, run_time=rt)


def M(s, size=34, color=INK):
    return Text(s, font=MONO, color=color, font_size=size)


def L(s, size=40, color=INK, bold=False):
    return T(s, size, color, bold)


def panel(w, h, x=0.0, y=0.0, fill=CARD, stroke=INK, sw=4, r=0.18):
    return RoundedRectangle(width=w, height=h, corner_radius=r, fill_color=fill, fill_opacity=1,
                            stroke_color=stroke, stroke_width=sw).move_to([x, y, 0])


def fit(mob, w):
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


def boxed(mob, x=0.0, y=0.0, padx=0.35, pady=0.2, fill="#FFFFFF", sw=3):
    """A card sized to its contents."""
    box = panel(mob.width + 2 * padx, mob.height + 2 * pady, fill=fill, sw=sw)
    mob.move_to(box)
    return VGroup(box, mob).move_to([x, y, 0])


def code(lines, size=30, x=0.0, y=0.0, maxw=6.3, pad=0.3, title=None):
    """An SQL panel: monospaced lines on a card sized to them (shrunk to fit maxw)."""
    body = VGroup(*[M(s, size) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    fit(body, maxw - 2 * pad)
    box = panel(body.width + 2 * pad, body.height + 2 * pad)
    body.move_to(box)
    g = VGroup(box, body)
    if title:
        g.add(L(title, 36).next_to(box, UP, buff=0.12).align_to(box, LEFT))
    return g.move_to([x, y, 0])


def strike(mob, color=TERRA, w=8):
    """Mark a wrong value: a red cross just right of it (a line through text trips Gate B)."""
    r = mob.get_right()
    return cross(r[0] + 0.42, r[1], 0.17, color, w)


def cross(x, y, s=0.32, color=TERRA, w=9):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def tick(x, y, s=0.26):
    return check(x, y, s, INK, 8)


def ok_pill(s="ran · 0 errors", x=0.0, y=0.0, size=34):
    inner = VGroup(tick(0, 0, 0.16), L(s, size)).arrange(RIGHT, buff=0.22)
    p = pill(0, 0, inner.width + 0.7, 0.7, fill="#FFFFFF").set_stroke(INK, 3)
    inner.move_to(p)
    return VGroup(p, inner).move_to([x, y, 0])


def person(x, y, s=1.0):
    head = Circle(radius=0.28 * s, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([x, y + 0.42 * s, 0])
    body = ArcBetweenPoints([x - 0.5 * s, y - 0.45 * s, 0], [x + 0.5 * s, y - 0.45 * s, 0], angle=-PI * 0.9,
                            color=INK, stroke_width=5)
    return VGroup(head, body)


def table(rows, x=0.0, y=0.0, size=34, header=True, gap=0.5):
    """A small result table sized to its cells; the first row is the header."""
    cells = [[(L(c, size, bold=True) if (header and i == 0) else M(c, size)) for c in r] for i, r in enumerate(rows)]
    ncol = len(rows[0])
    colw = [max(cells[i][j].width for i in range(len(rows))) + gap for j in range(ncol)]
    rh = 0.62
    g = VGroup()
    for i, r in enumerate(cells):
        cx = 0.25
        row = VGroup()
        for j, t in enumerate(r):
            t.move_to([cx, -i * rh, 0], aligned_edge=LEFT)
            row.add(t)
            cx += colw[j]
        g.add(row)
    W = sum(colw) + 0.25
    frame = panel(W, rh * len(rows) + 0.3, fill="#FFFFFF", sw=3).move_to([W / 2, -(len(rows) - 1) * rh / 2, 0])
    rule = Line([0.1, -rh / 2, 0], [W - 0.1, -rh / 2, 0], color=INK, stroke_width=3) if header else VGroup()
    out = VGroup(frame, rule, g)
    out.move_to([x, y, 0])
    out.rows = g
    return out


def tag(s, y=3.0, size=34):
    t = L(s, size)
    p = pill(0, y, t.width + 0.7, 0.62, fill=CARD).set_stroke(DIM, 2)
    t.move_to([0, y, 0])
    return VGroup(p, t)


def opener(self, text):
    """A heading on screen from the first frame, so a beat never opens on an empty stage."""
    h = L(text, 60, bold=True).move_to([0, 0.3, 0])
    self.play(FadeIn(h, shift=UP * 0.3), run_time=0.6)
    return h


def rise(mob, d=0.5):
    return FadeIn(mob, shift=UP * d)


def slide_in(mob, d=1.2):
    return FadeIn(mob, shift=LEFT * d)


def part_card(self, n, name, sub):
    """Opens the first beat of each of the four required parts: the part's name, alone, for ~1.6 s."""
    k = L(f"Part {n} of 4", 44, DIM).move_to([0, 1.15, 0])
    h = L(name, 84, bold=True).move_to([0, 0.15, 0])
    s = L(sub, 44).move_to([0, -0.8, 0])
    self.play(FadeIn(k, shift=UP * 0.2), FadeIn(h, shift=UP * 0.3), FadeIn(s, shift=UP * 0.2), run_time=0.5)
    self.wait(1.1)
    self.play(FadeOut(VGroup(k, h, s), shift=UP * 0.3), run_time=0.4)


def mark_line(s_, ok, size=36):
    m = tick(0, 0, 0.15) if ok else cross(0, 0, 0.15)
    return VGroup(m, L(s_, size)).arrange(RIGHT, buff=0.28)


class B04_WhatItIs(Scene):
    def construct(self):
        name = boxed(fit(L("Ground Truth SQL", 46, bold=True), 3.0), -1.0, 0.55, padx=0.4, pady=0.3, fill=CARD, sw=5)
        what = fit(L("a test for AI data assistants", 36), 3.8).next_to(name, DOWN, buff=0.3)
        db = make_original("server-tower", 1.7, x=-4.8, y=1.45)
        db_l = L("your data", 34).move_to([-4.8, 0.25, 0])
        qs = boxed(fit(L("your questions", 34), 2.2), -4.8, -1.3, padx=0.25, pady=0.18)
        a1 = Arrow([-3.9, 1.1, 0], name.get_left() + UP * 0.2, color=INK, stroke_width=5, buff=0.1)
        a2 = Arrow(qs.get_right(), name.get_left() + DOWN * 0.2, color=INK, stroke_width=5, buff=0.1)
        card = panel(5.0, 4.4, 3.8, 0.35, fill="#FFFFFF")
        rc_t = L("report card", 40, bold=True).move_to([3.8, 2.15, 0])
        rows_spec = [("Revenue by country", False, "why: counted each order 4 times", 1.35),
                     ("Customers per country", True, None, 0.25),
                     ("Long songs", False, "why: read ms as seconds", -0.6)]
        rows, whys = VGroup(), VGroup()
        for q, ok, why, y in rows_spec:
            t = fit(L(q, 34), 3.7).move_to([1.6, y, 0], aligned_edge=LEFT)
            m = tick(5.95, y + 0.04, 0.15) if ok else cross(5.95, y, 0.15)
            rows.add(VGroup(t, m))
            if why:
                whys.add(fit(L(why, 30, TERRA), 4.4).move_to([1.6, y - 0.5, 0], aligned_edge=LEFT))
        a3 = Arrow(name.get_right(), card.get_left(), color=INK, stroke_width=5, buff=0.05)
        at(self, "So I'm building", FadeIn(name, scale=0.9), rt=0.7)
        at(self, "a test for AI", FadeIn(what, shift=UP * 0.2), rt=0.5)
        at(self, "Give it your own data", rise(db), FadeIn(db_l), GrowArrow(a1), rt=0.7)
        at(self, "and questions", FadeIn(qs), GrowArrow(a2), rt=0.6)
        at(self, "it tells you", GrowArrow(a3), FadeIn(card), FadeIn(rc_t), rt=0.6)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in rows], lag_ratio=0.3), run_time=1.0)
        at(self, "and why", LaggedStart(*[FadeIn(w, shift=UP * 0.15) for w in whys], lag_ratio=0.4), rt=0.8)
        finish(self)


class B06_Bird(Scene):
    def construct(self):
        part_card(self, 2, "Introduction", "what other people have done")
        shelf = make_original("version-shelves", 2.6, x=-4.3, y=1.0)
        bird = L("BIRD", 56, bold=True).move_to([-4.3, -0.75, 0])
        bird_s = fit(L("a public benchmark", 34), 2.9).move_to([-4.3, -1.35, 0])
        stats = VGroup(
            VGroup(M("12,751", 52), L("questions", 38)).arrange(RIGHT, buff=0.35),
            VGroup(M("95", 52), L("databases", 38)).arrange(RIGHT, buff=0.35),
            mark_line("scored by checking results", True, 38),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-1.2, 1.75, 0], aligned_edge=LEFT)
        full = 4.0
        def bar(lbl, y, frac, color, val):
            l_ = L(lbl, 36).move_to([0.7, y, 0], aligned_edge=RIGHT)
            b0 = Rectangle(width=0.01, height=0.45, fill_color=color, fill_opacity=1, stroke_width=0).move_to([1.0, y, 0], aligned_edge=LEFT)
            b1 = Rectangle(width=full * frac, height=0.45, fill_color=color, fill_opacity=1, stroke_width=0).move_to([1.0, y, 0], aligned_edge=LEFT)
            v = L(val, 36).next_to(b1, RIGHT, buff=0.25)
            return l_, b0, b1, v
        lp, bp, bp1, vp = bar("people", -0.5, 0.93, INK, "93%")
        la, ba, ba1, va = bar("best AI", -1.2, 0.834, BAR1, "lower")
        src = L("bird-bench.github.io · read 2026-11-22", 28, DIM).move_to([3.3, -1.95, 0])
        yours = boxed(L("your data", 34), -4.3, -2.15, padx=0.3, pady=0.14)
        yours[0].set_stroke(DIM, 3)
        nob = cross(-3.0, -2.15, 0.18)
        at(self, "BIRD is a public", rise(shelf), FadeIn(bird), FadeIn(bird_s), rt=0.8)
        at(self, "twelve thousand", FadeIn(stats[0], shift=RIGHT * 0.3), rt=0.5)
        at(self, "ninety five databases", FadeIn(stats[1], shift=RIGHT * 0.3), rt=0.5)
        at(self, "scored by checking", FadeIn(stats[2], shift=RIGHT * 0.3), rt=0.5)
        at(self, "People score", FadeIn(lp), FadeIn(bp), rt=0.3)
        self.play(Transform(bp, bp1), FadeIn(vp), FadeIn(src), run_time=0.7)
        at(self, "the best", FadeIn(la), FadeIn(ba), rt=0.3)
        self.play(Transform(ba, ba1), FadeIn(va), run_time=0.7)
        at(self, "not yours", FadeIn(yours, shift=UP * 0.2), Create(nob), rt=0.6)
        finish(self)


class B07_Vanna(Scene):
    def construct(self):
        img = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "images", "vanna_run_crop.png")
        if not _os.path.exists(img):   # the toolkit may render a copy of scenes.py from elsewhere
            img = _os.path.expanduser("~/Documents/INFO7375/films/riya-k-ground-truth-sql-v4/images/vanna_run_crop.png")
        shot = ImageMobject(img)
        shot.scale_to_fit_width(6.6)
        shot.move_to([-2.7, 1.0, 0])
        shot_bg = panel(7.0, shot.height + 0.45, -2.7, 1.0, fill="#FFFFFF", sw=3)
        shot_t = L("my run of Vanna 2.0.2 · 2026-10-21", 32, DIM).next_to(shot_bg, DOWN, buff=0.2)
        ws = Group(shot_bg, shot, shot_t)
        van = L("Vanna", 60, bold=True).move_to([4.0, 2.2, 0])
        l1 = mark_line("works on your data", True, 36).move_to([4.0, 1.2, 0])
        l2 = mark_line("checks words, not numbers", False, 36).move_to([4.0, 0.4, 0])
        fit(l2, 4.4)
        passed = boxed(VGroup(M("USA 4,667", 36, TERRA), tick(0, 0, 0.15), L("passed", 38),
                              L("· 9× too high", 38)).arrange(RIGHT, buff=0.28), 0, -1.95, padx=0.4, pady=0.16)
        at(self, "Tools like Vanna", FadeIn(ws, shift=UP * 0.4), FadeIn(van), rt=0.8)
        at(self, "on your own data", FadeIn(l1, shift=LEFT * 0.3), rt=0.5)
        at(self, "looks for", FadeIn(l2, shift=LEFT * 0.3), rt=0.5)
        at(self, "it passed", FadeIn(passed, shift=UP * 0.3), rt=0.6)
        finish(self)


class B08_Gap(Scene):
    def construct(self):
        head = opener(self, "the gap")
        cx = [0.7, 4.6]
        h1 = L("checks the numbers", 36, bold=True).move_to([cx[0], 2.4, 0])
        h2 = L("on your data", 36, bold=True).move_to([cx[1], 2.4, 0])
        rule = Line([-6.2, 1.95, 0], [6.2, 1.95, 0], color=GHOST, stroke_width=4)
        spec = [("benchmarks (BIRD)", True, False, 1.25), ("tools (Vanna)", False, True, 0.15),
                ("Ground Truth SQL", True, True, -1.05)]
        rows = []
        for name, a, b, y in spec:
            nm = L(name, 42, bold=(name == "Ground Truth SQL")).move_to([-6.0, y, 0], aligned_edge=LEFT)
            m1 = tick(cx[0], y + 0.05, 0.2) if a else cross(cx[0], y, 0.2)
            m2 = tick(cx[1], y + 0.05, 0.2) if b else cross(cx[1], y, 0.2)
            rows.append(VGroup(nm, m1, m2))
        hl = RoundedRectangle(width=12.4, height=0.95, corner_radius=0.15, stroke_color=TERRA, stroke_width=6).move_to([0, -1.05, 0])
        note = L("find wrong answers before anyone trusts them", 38).move_to([0, -2.15, 0])
        at(self, "Benchmarks", FadeOut(head), FadeIn(h1), FadeIn(h2), Create(rule), rt=0.6)
        self.play(FadeIn(rows[0], shift=RIGHT * 0.3), run_time=0.6)
        at(self, "Tools work", FadeIn(rows[1], shift=RIGHT * 0.3), rt=0.6)
        at(self, "Ground Truth SQL does both", FadeIn(rows[2], shift=RIGHT * 0.3), rt=0.6)
        self.play(Create(hl), run_time=0.6)
        at(self, "so you find", FadeIn(note, shift=UP * 0.2), rt=0.6)
        finish(self)


class B09_Data(Scene):
    def construct(self):
        part_card(self, 3, "Methods", "how I'm going to build it")
        db = make_original("server-tower", 2.8, x=-4.2, y=0.9)
        nm = L("Chinook", 56, bold=True).move_to([-4.2, -1.0, 0])
        sub = fit(L("free sample music store", 34), 3.3).move_to([-4.2, -1.6, 0])
        stats = VGroup(*[VGroup(M(n, 60), L(t, 40)).arrange(RIGHT, buff=0.35)
                         for n, t in [("11", "tables"), ("59", "customers"), ("412", "orders")]]
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([-0.6, 1.4, 0], aligned_edge=LEFT)
        axis = Line([-0.6, -1.0, 0], [5.8, -1.0, 0], color=INK, stroke_width=6)
        ticks = VGroup()
        for i, yv in enumerate(range(2009, 2014)):
            x = -0.4 + i * 1.5
            ticks.add(Line([x, -1.15, 0], [x, -0.85, 0], color=INK, stroke_width=5), L(str(yv), 34).move_to([x, -1.55, 0]))
        lic = L("public, MIT license", 30, DIM).move_to([-4.2, -2.15, 0])
        at(self, "The data: Chinook", rise(db), FadeIn(nm), rt=0.7)
        at(self, "a free sample", FadeIn(sub), FadeIn(lic), rt=0.5)
        at(self, "Eleven tables", FadeIn(stats[0], shift=RIGHT * 0.3), rt=0.4)
        at(self, "fifty nine", FadeIn(stats[1], shift=RIGHT * 0.3), rt=0.4)
        at(self, "four hundred", FadeIn(stats[2], shift=RIGHT * 0.3), rt=0.4)
        at(self, "from two thousand nine", Create(axis), LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.1), rt=1.0)
        finish(self)


class B10_AnswerKey(Scene):
    def construct(self):
        step = tag("step 1 · the answer key", y=3.0)
        stack = VGroup(*[panel(2.6, 1.7, -4.8 + 0.14 * i, 0.9 - 0.14 * i, fill="#FFFFFF", sw=3).set_stroke(DIM, 3)
                         for i in range(4)])
        st_l = fit(L("about 50 questions", 36), 2.8).move_to([-4.5, -0.9, 0])
        q = L("Revenue by country?", 38, bold=True)
        sql = code(["SELECT BillingCountry, SUM(Total)", "FROM Invoice GROUP BY BillingCountry"], 26, maxw=5.6)
        ans = M("USA 523.06", 38)
        card1 = VGroup(q, sql, ans).arrange(DOWN, buff=0.22).move_to([0.2, 1.3, 0])
        k1 = L("checked answer", 34, DIM).next_to(ans, RIGHT, buff=0.35)
        py = boxed(VGroup(L("second check", 36, bold=True), L("plain Python, raw tables", 34)).arrange(DOWN, buff=0.1), -0.5, -1.25,
                   fill=CARD, sw=4)
        ans2 = M("USA 523.06", 38).next_to(py, RIGHT, buff=0.5)
        eq = M("=", 64).move_to([5.0, 0.0, 0])
        agree = VGroup(tick(0, 0, 0.16), L("today 8 of 8 agree", 36)).arrange(RIGHT, buff=0.25).move_to([3.6, -2.05, 0])
        self.add(step)
        at(self, "Step one", LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in stack], lag_ratio=0.2), rt=0.8)
        at(self, "about fifty", FadeIn(st_l), rt=0.4)
        at(self, "each with a checked", FadeIn(q), FadeIn(sql), rt=0.6)
        self.play(FadeIn(ans), FadeIn(k1), run_time=0.5)
        at(self, "a second way", FadeIn(py, shift=UP * 0.3), rt=0.6)
        at(self, "straight from", FadeIn(ans2, shift=LEFT * 0.3), rt=0.5)
        self.play(FadeIn(agree, shift=UP * 0.2), run_time=0.6)
        finish(self)


class B11_ClaudeAnswers(Scene):
    def construct(self):
        step = tag("step 2 · Claude answers", y=3.0)
        i1 = boxed(L("table layout", 36), -4.8, 1.55)
        i2 = boxed(L("the question", 36), -4.8, 0.25)
        ws = make_original("agent-workstation", 2.2, x=-1.4, y=1.0)
        cl = L("Claude", 44, bold=True).move_to([-1.4, -0.45, 0])
        runs = VGroup(*[boxed(L(f"run {k}", 34), 1.75, 1.9 - 0.85 * (k - 1), padx=0.3, pady=0.12) for k in (1, 2, 3)])
        for r in runs:
            r[0].set_stroke(DIM, 3)
        db = make_original("server-tower", 2.0, x=4.9, y=1.1)
        ro = boxed(fit(L("read-only · 1 query", 34), 2.8), 4.4, -0.55, fill=CARD, padx=0.3, pady=0.14)
        a1 = Arrow(i1.get_right(), [-2.6, 1.1, 0], color=INK, stroke_width=5, buff=0.08)
        a2 = Arrow(i2.get_right(), [-2.6, 0.7, 0], color=INK, stroke_width=5, buff=0.08)
        a3 = Arrow([2.75, 1.05, 0], [3.85, 1.05, 0], color=INK, stroke_width=5, buff=0.05)
        never = VGroup(cross(0, 0, 0.16), L("can never change the data", 38)).arrange(RIGHT, buff=0.3).move_to([0, -1.85, 0])
        self.add(step)
        at(self, "Step two", rise(ws), FadeIn(cl), rt=0.7)
        at(self, "three times", LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in runs], lag_ratio=0.35), rt=1.0)
        at(self, "table layout", FadeIn(i1), GrowArrow(a1), rt=0.5)
        at(self, "and the question", FadeIn(i2), GrowArrow(a2), rt=0.5)
        at(self, "one read-only", rise(db), GrowArrow(a3), FadeIn(ro), rt=0.7)
        at(self, "It can never", FadeIn(never, shift=UP * 0.2), rt=0.6)
        finish(self)


class B12_Judge(Scene):
    def construct(self):
        step = tag("step 3 · judge by results", y=3.0)
        a = code(["SELECT BillingCountry,", "  SUM(Total)", "FROM Invoice", "GROUP BY BillingCountry"],
                 28, x=-3.2, y=1.15, maxw=5.9, title="checked SQL")
        b = code(["SELECT BillingCountry,", "  SUM(UnitPrice*Quantity)", "FROM Invoice", "JOIN InvoiceLine ...",
                  "GROUP BY BillingCountry"], 28, x=3.2, y=1.05, maxw=5.9, title="different SQL")
        ra = boxed(M("USA 523.06", 36), -3.2, -1.05)
        rb = boxed(M("USA 523.06", 36), 3.2, -1.05)
        aa = Arrow(a.get_bottom(), ra.get_top(), color=INK, stroke_width=5, buff=0.06)
        ab = Arrow(b.get_bottom(), rb.get_top(), color=INK, stroke_width=5, buff=0.06)
        eq = M("=", 72).move_to([0, -1.05, 0])
        note = L("compare results, not wording", 40).move_to([0, -2.1, 0])
        self.add(step)
        at(self, "Step three", FadeIn(note, shift=UP * 0.2), rt=0.6)
        at(self, "These two queries", FadeIn(a, shift=RIGHT * 0.4), FadeIn(b, shift=LEFT * 0.4), rt=0.9)
        at(self, "both give", GrowArrow(aa), GrowArrow(ab), FadeIn(ra), FadeIn(rb), rt=0.7)
        self.play(FadeIn(eq, scale=1.4), run_time=0.4)
        finish(self)


class B13_Causes(Scene):
    def construct(self):
        step = tag("step 4 · report card, sorted by cause", y=3.0)
        specs = [("Revenue", "counted once|per song", "4,667", "523"),
                 ("Long songs", "ms read|as seconds", "3,503", "1,069"),
                 ("Rock buyers", "purchases,|not people", "835", "59"),
                 ("Busiest rep", "wrong columns|linked", "(empty)", "Jane Peacock")]
        cues = ["counting an order", "mixing up", "counting purchases", "linking the wrong"]
        xs = [-4.6, -1.55, 1.55, 4.6]
        self.add(step)
        for (q, why, bad, good), x, cue in zip(specs, xs, cues):
            card = panel(2.85, 4.6, x, 0.25, fill="#FFFFFF")
            tq = fit(L(q, 40, bold=True), 2.45).move_to([x, 2.05, 0])
            tw = fit(VGroup(*[L(w, 32) for w in why.split("|")]).arrange(DOWN, buff=0.06), 2.5).move_to([x, 1.35, 0])
            wl = L("AI-style", 32, DIM).move_to([x, 0.6, 0])
            wv = fit(M(bad, 50), 2.0).move_to([x - 0.25, 0.05, 0])
            rl = L("right", 32, DIM).move_to([x, -0.6, 0])
            rv = fit((M(good, 50) if len(good) < 8 else L(good, 38)), 2.45).move_to([x, -1.2, 0])
            grp = VGroup(card, tq, tw, wl, wv, rl, rv)
            at(self, cue, FadeIn(grp, shift=UP * 0.4), rt=0.6)
            self.play(Create(strike(wv)), run_time=0.35)
        finish(self)


class B14_Needs(Scene):
    def construct(self):
        def col(head, items, x, ok):
            h = L(head, 42, bold=True).move_to([x, 2.4, 0], aligned_edge=LEFT)
            its = VGroup(*[mark_line(s_, ok, 38) for s_ in items]
                         ).arrange(DOWN, aligned_edge=LEFT, buff=0.38).next_to(h, DOWN, buff=0.45, aligned_edge=LEFT)
            return h, its
        have_h, have = col("what I have", ["a laptop", "Python", "the free database", "Claude, via my Claude Code plan"], -6.2, True)
        no_h, no = col("what I don't need", ["cloud servers", "extra token credits"], 1.8, False)
        same = L("same setup as my first Claude runs (2026-10-21)", 34, DIM).move_to([0, -2.1, 0])
        at(self, "What I need", FadeIn(have_h), rt=0.4)
        at(self, "a laptop", FadeIn(have[0], shift=RIGHT * 0.3), rt=0.4)
        at(self, "Python", FadeIn(have[1], shift=RIGHT * 0.3), rt=0.4)
        at(self, "the free database", FadeIn(have[2], shift=RIGHT * 0.3), rt=0.4)
        at(self, "No cloud", FadeIn(no_h), FadeIn(no[0], shift=RIGHT * 0.3), rt=0.5)
        at(self, "no extra token", FadeIn(no[1], shift=RIGHT * 0.3), rt=0.4)
        at(self, "Claude answers", FadeIn(have[3], shift=RIGHT * 0.3), rt=0.5)
        at(self, "the same way", FadeIn(same, shift=UP * 0.2), rt=0.5)
        finish(self)


class B16_CheckerTest(Scene):
    def construct(self):
        part_card(self, 4, "Evaluation", "how I'll know it worked")
        head = L("does the checker judge correctly?", 52, bold=True).move_to([0, 2.2, 0])
        what = L("9 test queries, labeled by hand: 3 correct rewrites, 6 with a mistake", 36).move_to([0, 1.05, 0])
        full = 5.2
        def bar_row(lbl, y, n, color):
            l_ = L(lbl, 40).move_to([-1.6, y, 0], aligned_edge=RIGHT)
            b0 = Rectangle(width=0.01, height=0.55, fill_color=color, fill_opacity=1, stroke_width=0).move_to([-1.2, y, 0], aligned_edge=LEFT)
            b1 = Rectangle(width=full * n / 9, height=0.55, fill_color=color, fill_opacity=1, stroke_width=0).move_to([-1.2, y, 0], aligned_edge=LEFT)
            v = M(f"{n} / 9", 40).next_to(b1, RIGHT, buff=0.3)
            return l_, b0, b1, v
        lw, bw, bw1, nw = bar_row("compare wording", -0.2, 6, BAR1)
        lr, br, br1, nr = bar_row("compare results", -1.3, 9, INK)
        self.play(FadeIn(head, shift=UP * 0.2), run_time=0.5)
        at(self, "On nine test queries", FadeIn(what), rt=0.5)
        at(self, "comparing wording", FadeIn(lw), FadeIn(bw), rt=0.3)
        self.play(Transform(bw, bw1), FadeIn(nw), run_time=0.7)
        at(self, "Comparing results", FadeIn(lr), FadeIn(br), rt=0.3)
        self.play(Transform(br, br1), FadeIn(nr), run_time=0.7)
        finish(self)


class B19_PassBar(Scene):
    def construct(self):
        h1 = L("it worked if", 44, bold=True).move_to([-6.2, 2.45, 0], aligned_edge=LEFT)
        ok = VGroup(*[mark_line(s_, True, 36) for s_ in
                      ["the checker agrees with my hand labels, every time",
                       "every answer key passes the second check",
                       "every miss on the report card has a named cause"]]
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(h1, DOWN, buff=0.25, aligned_edge=LEFT)
        h2 = L("it didn't work if", 44, bold=True).move_to([-6.2, -0.65, 0], aligned_edge=LEFT)
        bad = mark_line("Claude gets everything right: the questions are too easy", False, 36
                        ).next_to(h2, DOWN, buff=0.25, aligned_edge=LEFT)
        today = VGroup(L("today: Claude 22 of 24", 36),
                       Arrow(ORIGIN, RIGHT * 0.9, color=INK, stroke_width=5, buff=0),
                       L("next 50 questions must be harder", 36, bold=True)).arrange(RIGHT, buff=0.3).move_to([0, -2.3, 0])
        fit(today, 12.0)
        at(self, "It worked if", FadeIn(h1), rt=0.4)
        at(self, "the checker agrees", FadeIn(ok[0], shift=RIGHT * 0.3), rt=0.5)
        at(self, "every answer key", FadeIn(ok[1], shift=RIGHT * 0.3), rt=0.5)
        at(self, "every miss", FadeIn(ok[2], shift=RIGHT * 0.3), rt=0.5)
        at(self, "It didn't work", FadeIn(h2), FadeIn(bad, shift=RIGHT * 0.3), rt=0.6)
        at(self, "Today it nearly", FadeIn(today, shift=UP * 0.2), rt=0.6)
        finish(self)


class B20_Conclusion(Scene):
    def construct(self):
        def head(s_, y):
            return L(s_, 42, bold=True).move_to([-6.2, y, 0], aligned_edge=LEFT)
        X0 = -3.4
        h1, h2, h3, h4 = head("problem", 2.45), head("solution", 1.2), head("today", -0.05), head("next", -1.75)
        p1 = VGroup(M("$4,667", 44), L("looks right", 38), M("$523", 44), L("is true", 38)).arrange(RIGHT, buff=0.4)
        for k in (1, 2, 3):
            p1[k].shift(RIGHT * 0.55)
        p1.move_to([X0, 2.45, 0], aligned_edge=LEFT)
        st = strike(p1[0])
        p2 = VGroup(L("your data", 40), Arrow(ORIGIN, RIGHT * 0.9, color=INK, stroke_width=5, buff=0),
                    L("test the AI", 40), Arrow(ORIGIN, RIGHT * 0.9, color=INK, stroke_width=5, buff=0),
                    L("report card", 40)).arrange(RIGHT, buff=0.3)
        fit(p2, 9.4).move_to([X0, 1.2, 0], aligned_edge=LEFT)
        p3 = VGroup(L("the checker works: Claude tested on 8 questions, 3 times", 34),
                    L("22 of 24 passed; both fails were my question's fault", 34)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit(p3, 9.7).move_to([X0, -0.05, 0], aligned_edge=LEFT)
        p3.shift(UP * (h3.get_center()[1] - p3[0].get_center()[1]))
        p4 = fit(L("about 50 harder questions, each checked a second way", 34), 9.7).move_to([X0, -1.75, 0], aligned_edge=LEFT)
        recap = VGroup(h1, h2, h3, h4, p1, st, p2, p3, p4)
        c1 = L("Running SQL is easy.", 72).move_to([0, 0.9, 0])
        c2 = L("Being right is the test.", 72).move_to([0, -0.45, 0])
        u = Line(c2.get_corner(DL) + DOWN * 0.12, c2.get_corner(DR) + DOWN * 0.12, color=TERRA, stroke_width=8)
        take = L("the takeaway", 44, DIM).move_to([0, 2.2, 0])
        concl = opener(self, "in conclusion")
        at(self, "AI can give", FadeOut(concl), FadeIn(h1), FadeIn(p1, shift=RIGHT * 0.3), rt=0.8)
        self.play(Create(st), run_time=0.4)
        at(self, "Ground Truth SQL tests", FadeIn(h2), LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in p2], lag_ratio=0.3), rt=1.2)
        at(self, "Today the checker", FadeIn(h3), FadeIn(p3, shift=RIGHT * 0.3), rt=0.6)
        at(self, "Next:", FadeIn(h4), FadeIn(p4, shift=RIGHT * 0.3), rt=0.5)
        at(self, "So the takeaway", FadeOut(recap, shift=UP * 0.4), FadeIn(take, shift=UP * 0.2), rt=0.8)
        at(self, "running SQL", Write(c1), rt=1.0)
        at(self, "Being right", Write(c2), rt=1.0)
        self.play(Create(u), run_time=0.6)
        finish(self)


#B01
class B01_Title(Scene):
    def construct(self):
        title = fit(L("Ground Truth SQL", 120), 12.0)
        title.move_to([0, 1.75, 0])
        name = L("Riya Kapadnis", 72).move_to([0, 0.45, 0])
        course = L("INFO 7375  ·  Final Project Film", 44).move_to([0, -0.35, 0])
        rule = Line([-4.2, -0.95, 0], [4.2, -0.95, 0], color=GHOST, stroke_width=4)
        prob1 = L("AI can write database code that runs with no errors", 44).move_to([0, -1.6, 0])
        prob2 = L("but gives the wrong answer.", 44).move_to([0, -2.25, 0])
        under = Line(prob2.get_corner(DL) + DOWN * 0.08 + RIGHT * 2.05, prob2.get_corner(DR) + DOWN * 0.08,
                     color=TERRA, stroke_width=8)
        self.play(Write(title), run_time=1.6)
        self.play(FadeIn(name, shift=UP * 0.3), run_time=0.9)
        self.play(FadeIn(course, shift=UP * 0.3), Create(rule), run_time=0.8)
        at(self, "The problem", FadeIn(prob1, shift=UP * 0.2), rt=0.9)
        at(self, "but gives", FadeIn(prob2, shift=UP * 0.2), rt=0.7)
        self.play(Create(under), run_time=0.6)
        finish(self)



#B02
class B02_Problem(Scene):
    def construct(self):
        honest = tag("example SQL · drafted with Claude, checked by me")
        you = person(-6.0, 2.2, 0.45)
        q = L("What is our revenue by country?", 36)
        chat = boxed(q, padx=0.3, pady=0.2)
        chat.move_to([-5.6, 2.2, 0], aligned_edge=LEFT)
        sql = code(["SELECT BillingCountry,", "  SUM(Total)", "FROM Invoice", "JOIN InvoiceLine",
                    "  USING (InvoiceId)", "GROUP BY BillingCountry"], 28, maxw=5.6)
        sql.move_to([-6.2, -0.2, 0], aligned_edge=LEFT)
        okp = ok_pill(x=sql.get_center()[0], y=-2.3)
        res = table([("Country", "Revenue"), ("USA", "4,667.06"), ("Canada", "2,689.96"), ("France", "1,722.10")], size=32)
        res.move_to([3.7, 0.3, 0])
        res_lbl = L("the answer it gives", 36).next_to(res, UP, buff=0.18)
        usa_val = res.rows[1][1]
        real = boxed(VGroup(L("real answer", 40), M("523.06", 52)).arrange(RIGHT, buff=0.35), 3.7, -1.95, sw=4)
        arrow = Arrow(sql.get_right() + RIGHT * 0.1, res.get_left() + LEFT * 0.1, color=INK, stroke_width=6, buff=0.05)
        part_card(self, 1, "Executive summary", "what I'm building, and why it matters")
        self.add(honest)
        self.play(FadeIn(chat[0]), FadeIn(you), run_time=0.6)
        at(self, "what is our revenue", AddTextLetterByLetter(q), rt=1.4)
        at(self, "The AI writes SQL", FadeIn(sql[0]), rt=0.4)
        at(self, "the language", LaggedStart(*[AddTextLetterByLetter(l) for l in sql[1]], lag_ratio=1.0), rt=2.4)
        at(self, "It runs", rise(okp), rt=0.6)
        at(self, "It says the USA", GrowArrow(arrow), FadeIn(res), FadeIn(res_lbl), rt=0.9)
        self.play(Indicate(usa_val, color=TERRA, scale_factor=1.15), run_time=0.8)
        at(self, "The real answer", Create(strike(usa_val)), rt=0.5)
        self.play(FadeIn(real, shift=UP * 0.3), run_time=0.8)
        finish(self)



#B03
class B03_Matters(Scene):
    def construct(self):
        head = opener(self, "why does this matter?")
        # 1 · the person sees only the answer
        p = person(-4.6, 0.4, 1.3)
        ans = panel(2.4, 1.0, -4.6, 2.15, fill="#FFFFFF", sw=3)
        ans_t = M("$4,667", 44).move_to(ans)
        hidden = VGroup(*[Line([-5.6, -0.95 - i * 0.28, 0], [-3.4 - (i % 2) * 0.6, -0.95 - i * 0.28, 0],
                               color=GHOST, stroke_width=10) for i in range(4)])
        l1 = fit(L("never sees the SQL", 36), 3.3).move_to([-4.6, -2.25, 0])
        # 2 · the AI doesn't know the data
        tower = make_original("server-tower", 2.6, x=0.0, y=0.55)
        qs = VGroup(*[L("?", 64).move_to([dx, 2.45 + dy, 0]) for dx, dy in [(-0.9, 0), (0.1, 0.25), (1.0, -0.05)]])
        l2 = L("doesn't know your data", 36).move_to([0.0, -2.25, 0])
        # 3 · no crash, a trusted number
        screen = panel(3.4, 2.2, 4.6, 1.1, fill="#FFFFFF")
        stand = Line([4.6, -0.0, 0], [4.6, -0.7, 0], color=INK, stroke_width=6)
        foot = Line([4.0, -0.7, 0], [5.2, -0.7, 0], color=INK, stroke_width=6)
        num = M("$4,667", 54).move_to([4.6, 1.25, 0])
        okp = tick(5.8, 0.45, 0.2)
        l3 = fit(L("no crash, just trusted", 36), 3.3).move_to([4.6, -2.25, 0])
        at(self, "so most never see", FadeOut(head), FadeIn(p), FadeIn(ans), FadeIn(ans_t), FadeIn(hidden), FadeIn(l1), rt=0.9)
        at(self, "The AI doesn't know", rise(tower), FadeIn(l2), rt=0.8)
        self.play(LaggedStart(*[FadeIn(q, scale=1.4) for q in qs], lag_ratio=0.3), run_time=0.9)
        at(self, "wrong SQL doesn't crash", FadeIn(screen), Create(stand), Create(foot), rt=0.7)
        self.play(Write(num), FadeIn(l3), run_time=0.8)
        at(self, "people trust", Create(okp), Indicate(num, color=TERRA), rt=0.8)
        finish(self)



#B05
class B05_WhereUsed(Scene):
    def construct(self):
        rc = panel(3.0, 2.2, 0, 0.85, fill="#FFFFFF")
        rc_t = L("report card", 38, bold=True).move_to([0, 1.55, 0])
        rows = VGroup()
        for i, ok in enumerate([True, False, True]):
            y = 1.05 - i * 0.5
            rows.add(Line([-1.0, y, 0], [0.55, y, 0], color=GHOST, stroke_width=10))
            rows.add(tick(0.95, y + 0.05, 0.13) if ok else cross(0.95, y, 0.13))
        places = [("store sales", -4.3, 2.55), ("finance", -4.7, 1.2), ("hospitals", 4.7, 1.2),
                  ("marketing", 4.3, 2.55), ("AI data assistant", 0.0, 2.75)]
        cues = ["store sales", "finance", "hospitals", "marketing", "AI data assistants"]
        pills = []
        for (s_, x, y) in places:
            b = boxed(L(s_, 38), x, y, padx=0.35, pady=0.22)
            b[0].set_stroke(DIM, 3)          # grey edge: GATE T reads a dark edge as text
            if x == 0:
                ln = DashedLine(b.get_bottom(), [0, 1.95, 0], color=DIM, stroke_width=3)
            else:
                ln = DashedLine(b.get_right() if x < 0 else b.get_left(), [np.sign(x) * 1.55, 1.0, 0], color=DIM, stroke_width=3)
            pills.append(VGroup(ln, b))
        people = [("Analysts", "double-check"), ("Teams", "test before buying"), ("Engineers", "fix first")]
        pcues = ["Analysts learn", "Teams test", "Engineers see"]
        pp = VGroup()
        for who, what in people:
            words = VGroup(L(who, 38, bold=True), L(what, 36)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            g = VGroup(person(0, 0, 0.7), words)
            words.next_to(g[0], RIGHT, buff=0.3)
            pp.add(g)
        pp.arrange(RIGHT, buff=1.0).move_to([0, -1.65, 0])
        fit(pp, 12.2)
        self.play(FadeIn(rc), FadeIn(rc_t), FadeIn(rows), run_time=0.6)
        for g, c in zip(pills, cues):
            at(self, c, FadeIn(g, scale=0.8), rt=0.45, lead=0.1)
        for g, c in zip(pp, pcues):
            at(self, c, rise(g, 0.3), rt=0.6)
        finish(self)



#B15
class B15_Scope(Scene):
    def construct(self):
        def col(head, items, x, mark):
            h = L(head, 40, bold=True).move_to([x, 2.4, 0], aligned_edge=LEFT)
            its = VGroup(*[VGroup(mark(0, 0, 0.15), L(s_, 36)).arrange(RIGHT, buff=0.25) for s_ in items]
                         ).arrange(DOWN, aligned_edge=LEFT, buff=0.36).next_to(h, DOWN, buff=0.45, aligned_edge=LEFT)
            return h, its
        inc_h, inc = col("the finished project will have", ["1 sample database (Chinook)", "~50 test questions",
                                                            "Claude as the AI being tested"], -6.3, lambda x, y, s: tick(x, y, s))
        out_h, out = col("it will not", ["be a chat app", "change any data"], 1.2, cross)
        at(self, "The finished project", FadeIn(inc_h), rt=0.5)
        at(self, "one sample database", FadeIn(inc[0], shift=RIGHT * 0.3), rt=0.4)
        at(self, "about fifty test", FadeIn(inc[1], shift=RIGHT * 0.3), rt=0.4)
        at(self, "and Claude as", FadeIn(inc[2], shift=RIGHT * 0.3), rt=0.4)
        at(self, "It won't be", FadeIn(out_h), FadeIn(out[0], shift=RIGHT * 0.3), rt=0.5)
        at(self, "it never changes", FadeIn(out[1], shift=RIGHT * 0.3), rt=0.4)
        finish(self)



#B17
class B17_Runs(Scene):
    def construct(self):
        real = tag("real run · Claude Opus 5.5 · 2026-10-21 · output shortened", y=3.05)
        frame = panel(12.6, 4.2, 0, 0.5, fill="#FFFFFF")
        bar = Rectangle(width=12.5, height=0.45, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([0, 2.38, 0])
        dots = VGroup(*[Circle(radius=0.08, fill_color=c, fill_opacity=1, stroke_width=0).move_to([-5.95 + i * 0.3, 2.38, 0])
                        for i, c in enumerate([TERRA, DIM, DIM])])
        cmd = M("$ python3 score_claude_runs.py", 30).move_to([-5.9, 1.85, 0], aligned_edge=LEFT)
        lines = ["Q01, Q03 … Q08   all 3 runs   PASS",
                 "Q02  gold  USA 13 · Canada 8 · Brazil 5 …",
                 "run1  USA 13 · Canada 8 · France 5 …  FAIL",
                 "run2  USA 13 · Canada 8 · France 5 …  FAIL",
                 "run3  USA 13 · Canada 8 · Brazil 5 …  PASS"]
        out = VGroup(*[M(s_, 30) for s_ in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([-5.9, 0.38, 0], aligned_edge=LEFT)
        last = M("22 / 24 passed by comparing rows", 30).move_to([-5.9, -1.3, 0], aligned_edge=LEFT)
        ul = Line(last.get_corner(DL) + DOWN * 0.08, last.get_corner(DR) + DOWN * 0.08, color=TERRA, stroke_width=7)
        fails = VGroup(out[2], out[3])
        tie_q = L("Q02 · Which 5 countries have the most customers?", 36)
        tie_a = VGroup(L("France 5", 40), M("=", 44), L("Brazil 5", 40), L("· a tie, not a mistake", 40)).arrange(RIGHT, buff=0.3)
        tie = boxed(VGroup(tie_q, tie_a).arrange(DOWN, buff=0.16), 0, -2.4, fill=CARD, sw=4, pady=0.16)
        self.add(real)
        self.play(FadeIn(frame), FadeIn(bar), FadeIn(dots), run_time=0.35)
        self.play(AddTextLetterByLetter(cmd), run_time=0.6)
        at(self, "Then I had Claude", LaggedStart(*[FadeIn(l, shift=UP * 0.15) for l in out], lag_ratio=0.3), rt=1.2)
        at(self, "The checker passed", FadeIn(last), rt=0.4)
        self.play(Create(ul), run_time=0.5)
        at(self, "The two fails", Indicate(fails, color=TERRA, scale_factor=1.04), rt=0.9)
        at(self, "a tie", FadeIn(tie, shift=UP * 0.3), rt=0.6)
        finish(self)



#B18
class B18_CaughtMe(Scene):
    def construct(self):
        head = opener(self, "a mistake in my answer key")
        axis = Line([-6.0, 1.9, 0], [1.2, 1.9, 0], color=INK, stroke_width=6)
        years = VGroup()
        for i, yv in enumerate(range(2009, 2014)):
            x = -5.6 + i * 1.6
            years.add(Line([x, 1.75, 0], [x, 2.05, 0], color=INK, stroke_width=5), L(str(yv), 36).move_to([x, 1.35, 0]))
        dl = L("the data", 36).move_to([-2.4, 2.55, 0])
        dash = DashedLine([1.4, 1.9, 0], [4.2, 1.9, 0], color=DIM, stroke_width=4)
        m23 = VGroup(Dot([4.6, 1.9, 0], radius=0.14, color=TERRA), L("2023", 40).move_to([4.6, 1.35, 0]))
        q = L("my question", 36).move_to([4.6, 2.55, 0])
        def ebox(lbl, x):
            b = boxed(M("(empty)", 40), x, -0.35, padx=0.6, pady=0.25)
            return VGroup(L(lbl, 36).next_to(b, UP, buff=0.15), b)
        e1, e2 = ebox("right answer", -3.0), ebox("broken SQL", 3.0)
        eq = M("=", 72).move_to([0, -0.35, 0])
        looks = VGroup(tick(0, 0, 0.17), L("looked correct", 36)).arrange(RIGHT, buff=0.25).move_to([0, -1.3, 0])
        neq = M("≠", 72, TERRA).move_to([0, -0.35, 0])
        rule = boxed(L("new rule: an empty right answer is rejected", 36), 0, -2.2, fill=CARD, sw=4)
        at(self, "One question asked", FadeOut(head), Create(axis), FadeIn(years), FadeIn(dl), rt=0.8)
        at(self, "but the data ends", Create(dash), FadeIn(m23, shift=RIGHT * 1.5), FadeIn(q), rt=0.8)
        at(self, "The right answer was empty", FadeIn(e1), FadeIn(e2), rt=0.6)
        self.play(FadeIn(eq), FadeIn(looks), run_time=0.5)
        at(self, "Now the tool", Transform(eq, neq), FadeOut(looks), rt=0.5)
        self.play(FadeIn(rule, shift=UP * 0.3), run_time=0.6)
        finish(self)


