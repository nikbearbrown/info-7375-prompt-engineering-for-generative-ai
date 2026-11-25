
# ═════════════════════════════ DataSentry project film — scenes (Ethan Gomes, 2026-11-23) ═════════════════════════════
# scenes.py = iso_kit.py + iso_originals_25.py + recorded_block.py + this file (see build_scenes.sh). Gate A copies only scenes.py.
# One drawing per beat; labels beside objects, ink, >= 30; terracotta only for dots/lights/checks.
# Every beat in parts 1-4 carries a small tag in the top-left corner naming its part.

MID_MARGIN = 0.26


def G(self, *anims, rt=0.5, **kw):
    """Play, but never across the clip midpoint (GATE T and Gate V sample there)."""
    bid = type(self).__name__.split("_")[0]
    tgt = _TARGET.get(bid, 0)
    if tgt:
        mid, t0 = tgt / 2.0, _elapsed(self)
        if t0 < mid + MID_MARGIN and t0 + rt > mid - MID_MARGIN:
            self.wait(mid + MID_MARGIN - t0)
    self.play(*anims, run_time=rt, **kw)


def L(s, x, y, size=36, bold=False):
    return T(s, size, INK, bold).move_to([x, y, 0])


ACTS = {1: "1 · Executive summary", 2: "2 · What others have done", 3: "3 · Methods", 4: "4 · Evaluation"}


def act_tag(n):
    """The part this beat belongs to, small, top-left (the assignment's four parts, in order)."""
    t = T(ACTS[n], 30, INK, True)
    return t.move_to([-6.0 + t.width / 2, 3.08, 0])


def parcel(iso, x0, y0, z0=0.0, w=1.0, d=1.0, h=0.8, flaw=False):
    """A kraft parcel (a batch of rows). `flaw` adds one terracotta dot on its top face (a planted defect)."""
    g = VGroup(iso.box(x0, y0, z0, w, d, h))
    if flaw:
        g.add(Dot(iso.p(x0 + w * 0.5, y0 + d * 0.5, z0 + h), radius=0.09, color=TERRA))
    return g


def table_card(x, y, w=5.4, h=3.6, rows=6):
    """A flat data table: kraft-shadowed white card, a grey header band of 5 column blocks, grey row bars."""
    card = paper(x, y, w=w, h=h)
    top = y + h / 2
    cols = VGroup(*[RoundedRectangle(width=(w - 0.8) / 5 - 0.12, height=0.34, corner_radius=0.08,
                                     fill_color=BAR1, fill_opacity=1, stroke_width=0)
                    .move_to([x - w / 2 + 0.4 + (i + 0.5) * (w - 0.8) / 5, top - 0.45, 0]) for i in range(5)])
    bars = VGroup(*[RoundedRectangle(width=w - 0.8, height=0.24, corner_radius=0.06, fill_color=BAR1,
                                     fill_opacity=1, stroke_width=0)
                    .move_to([x, top - 1.0 - i * (h - 1.35) / max(1, rows - 1), 0]) for i in range(rows)])
    return card, cols, bars


def tall_scribbles(page, n=3, inset=0.25, gap=0.5, amp=0.11):
    """scribbles_on() with taller strokes: the kit's 0.07 amplitude measures ~40 px at 4K, under GATE T's 41 px floor."""
    w = page.w - 2 * inset
    x0, y0 = page.cx - w / 2, page.cy + page.h / 2 - inset - 0.15
    return VGroup(*[scribble(x0, y0 - i * gap, w * (0.62 if i == n - 1 else 1.0), amp=amp) for i in range(n)])


# The pitch's scanner variant (Ethan, 2026-10-14): the near leg's top cap is dropped so the top bar sits over it.
import copy as _copy
_SC = _copy.deepcopy(_ST_ORIGINALS_25["checkpoint-scanner"])
_SC["parts"]["near-post"] = _SC["parts"]["near-post"][:2]
_ST_ORIGINALS_25["checkpoint-scanner-under"] = _SC


def scanner(height, x, y):
    """The scanner rig with explicit layering: the moving block passes BEHIND the top bar, the near leg stays in front."""
    rig = make_original("checkpoint-scanner-under", height=height, x=x, y=y)
    arch = list(rig.parts["arch"])
    for m in arch[:3]:
        m.set_z_index(0)
    for m in arch[3:]:
        m.set_z_index(2)
    rig.parts["parcel"].set_z_index(1)
    rig.parts["near-post"].set_z_index(3)
    return rig


MONO = "Menlo"


def M(s, size=28, color=INK):
    return Text(s, font=MONO, color=color, font_size=size)


def terminal(x, y, w, h):
    """A plain terminal-style panel (typeset text, not a screen recording): card, grey title bar."""
    shadow = RoundedRectangle(width=w, height=h, corner_radius=0.18, fill_color=BOX_L, fill_opacity=1,
                              stroke_width=0).move_to([x + 0.14, y - 0.14, 0])
    win = RoundedRectangle(width=w, height=h, corner_radius=0.18, fill_color=CARD, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    bar = RoundedRectangle(width=w - 0.4, height=0.36, corner_radius=0.1, fill_color=BAR1, fill_opacity=1,
                           stroke_width=0).move_to([x, y + h / 2 - 0.36, 0])
    return VGroup(shadow, win, bar)


def tline(s, x0, y, size=24):
    return M(s, size).move_to([x0, y, 0], aligned_edge=LEFT)


CHAR_W = 0.2    # Menlo advance per character at font sizes 24-26 (measured); fixed so Gate A's stub and Manim agree


def panel(texts, cx, cy, size=24, gap=0.5, marker_room=0.9):
    """Lines of typeset text in a window sized to fit them, centred on (cx, cy). Returns (window, [lines]).
    Geometry comes from character counts (monospace), never from measured mobject widths."""
    w = max(len(t.rstrip()) for t in texts) * CHAR_W + 1.0 + marker_room
    h = 0.75 + gap * len(texts) + 0.35
    top = cy + h / 2
    x0 = cx - w / 2 + 0.5
    lines = []
    for i, t in enumerate(texts):
        y = top - 0.75 - i * gap
        lead = len(t) - len(t.lstrip())                       # leading spaces keep their columns
        ln = tline(t.strip(), x0 + lead * CHAR_W, y, size)
        ln.x_end, ln.y_mid = x0 + len(t.rstrip()) * CHAR_W, y
        lines.append(ln)
    win = terminal(cx, cy, w, h)
    return win, lines


def mark_after(line, ok=True):
    """A tick (PASS/CAUGHT) or a terracotta dot (FAIL/MISSED) just past the end of a line."""
    if ok:
        return check(line.x_end + 0.35, line.y_mid + 0.02, s=0.18)
    return Dot([line.x_end + 0.4, line.y_mid, 0], radius=0.12, color=TERRA)


def recorded_tag(x, y):
    return L("recorded output · " + RECORDED["date"], x, y, 32)


class BIDEA_Title(Scene):
    """Title card: who made it, the project name, a drawn rule with one terracotta dot, and the four parts."""
    def construct(self):
        credit = VGroup(T("Project Film created by", 48), T("Ethan Gomes", 48, bold=True)).arrange(RIGHT, buff=0.22, aligned_edge=UP).move_to([0, 2.55, 0])
        name = L("DataSentry", 0, 0.9, 120, bold=True)
        self.play(FadeIn(credit), FadeIn(name, shift=UP * 0.15), run_time=0.8)
        # short opener (about 6 s): the rule lands at once; the four parts land at "about Data Sentry" (~2.8 s) and stay
        rule = Line([-4.2, -0.3, 0], [3.9, -0.3, 0], color=BAR1, stroke_width=5)
        dot = Dot([4.25, -0.3, 0], radius=0.13, color=TERRA)
        G(self, Create(rule), rt=0.4)
        G(self, GrowFromCenter(dot), rt=0.2)
        until(self, "about Data Sentry")
        p1 = L("1  What and why  ·  2  What others have done", 0, -1.3, 36)
        p2 = L("3  How I'll do it  ·  4  How I'll know it worked", 0, -2.0, 36)
        G(self, FadeIn(p1, shift=UP * 0.1), FadeIn(p2, shift=UP * 0.1), rt=0.6)
        finish(self)


# ───────────────────────────── 1 · Executive summary ─────────────────────────────

class BSIMPLE_Spellcheck(Scene):
    """In plain words: test the rules like a spell-checker. Hide mistakes on purpose; count which are caught."""
    def construct(self):
        pg = paper(-1.6, 0.05, w=5.6, h=4.4)
        lines = tall_scribbles(pg, n=5, gap=0.72)
        self.play(FadeIn(act_tag(1)), FadeIn(pg, shift=DOWN * 0.2), run_time=0.6)
        self.play(Create(lines), run_time=0.8)
        spots = [(0, 0.55), (1, -0.4), (3, 0.3), (4, -0.9)]
        y0 = 0.05 + 4.4 / 2 - 0.25 - 0.15
        marks = [Dot([-1.6 + dx, y0 - i * 0.72, 0], radius=0.13, color=TERRA) for i, dx in spots]
        until(self, "hide mistakes")
        lh = L("hidden mistakes", 3.6, 2.4, 36)
        G(self, LaggedStart(*[GrowFromCenter(m) for m in marks], lag_ratio=0.2), FadeIn(lh), rt=0.6)
        until(self, "count which")
        lens = Circle(radius=0.55, stroke_color=INK, stroke_width=8).move_to([-4.0, 1.2, 0])
        handle = Line([-3.6, 0.8, 0], [-3.1, 0.3, 0], color=INK, stroke_width=12)
        mag = VGroup(lens, handle)
        G(self, FadeIn(mag), rt=0.2)
        G(self, mag.animate.shift([4.6, -1.6, 0]), rt=0.8, rate_func=smooth)
        until(self, "get caught")
        ticks = VGroup(*[check(float(np.array(m.get_center())[0]) + 0.05, float(np.array(m.get_center())[1]) + 0.4, s=0.15) for m in marks[:3]])
        lc = L("caught", 3.6, 1.1, 36)
        G(self, LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), FadeIn(lc), rt=0.4)
        until(self, "which slip")
        ring = Circle(radius=0.3, stroke_color=INK, stroke_width=5).move_to(np.array(marks[3].get_center()))
        ls = L("slipped through", 3.6, -1.95, 36)
        G(self, Create(ring), FadeIn(ls), rt=0.4)
        finish(self)


class B00_Scanner(Scene):
    """What it is: the scanner, the name, the table (parcel) rides under the arch and a planted bad row lights."""
    def construct(self):
        rig = scanner(4.4, -1.6, -0.1)
        vec = rig.action_vectors["parcel"]
        rig.parts["parcel"].shift(vec)
        self.play(FadeIn(act_tag(1)), FadeIn(rig, shift=DOWN * 0.25), run_time=0.8)
        until(self, "Data Sentry")
        name = VGroup(T("DataSentry", 60, INK, True), T("an AI agent", 36)).arrange(DOWN, buff=0.15).move_to([3.9, 1.1, 0])
        G(self, FadeIn(name), rt=0.4)
        until(self, "writes data checks")
        tag = L("a table", 1.3, -2.45, 36)
        G(self, FadeIn(tag), rt=0.3)
        G(self, rig.parts["parcel"].animate.shift(-vec), rt=1.2, rate_func=smooth)
        until(self, "bad rows I planted")
        dot = Dot(np.array(rig.parts["parcel"].get_center()) + np.array([0, 0.25, 0]), radius=0.1, color=TERRA).set_z_index(1.5)
        lp = L("planted bad row", 3.9, -0.3, 36)
        G(self, GrowFromCenter(dot), FadeIn(lp), rt=0.4)
        until(self, "a person approves")
        ok = check(1.95, -1.33, s=0.2)
        la = L("a person approves", 4.0, -1.3, 36)
        G(self, Create(ok), FadeIn(la), rt=0.4)
        finish(self)


class B01_Why(Scene):
    """Why it matters: bad rows that get through become wrong numbers on a dashboard; DataSentry shows which ones."""
    def construct(self):
        card, cols, bars = table_card(-4.0, 0.2, w=3.6, h=3.0, rows=5)
        self.play(FadeIn(act_tag(1)), FadeIn(VGroup(card, cols, bars), shift=DOWN * 0.2), run_time=0.6)
        until(self, "let bad rows through")
        bad = [bars[1], bars[3]]
        dots = VGroup(*[Dot(np.array(b.get_center()) + np.array([0.6, 0, 0]), radius=0.11, color=TERRA) for b in bad])
        G(self, LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.3), rt=0.5)
        until(self, "wrong numbers")
        arrow = Line([-1.9, 0.2, 0], [-0.4, 0.2, 0], color=INK, stroke_width=6)
        dash = paper(2.3, 0.2, w=4.4, h=3.0)
        hs = [1.0, 1.5, 0.7, 2.1, 1.25]
        bx = [2.3 + (i - 2) * 0.75 for i in range(len(hs))]      # bar centres, centred on the card
        base = Line([bx[0] - 0.4, -0.85, 0], [bx[-1] + 0.4, -0.85, 0], color=INK, stroke_width=4)  # 0.15 past both outer bars
        cols2 = VGroup(*[Rectangle(width=0.5, height=hh, fill_color=BAR1, fill_opacity=1, stroke_width=0)
                         .move_to([bx[i], -0.85 + hh / 2, 0]) for i, hh in enumerate(hs)])
        wrong = Dot([bx[3], -0.85 + hs[3] + 0.2, 0], radius=0.11, color=TERRA)
        lw = L("wrong numbers", 2.3, -1.95, 36)
        G(self, Create(arrow), rt=0.35)
        G(self, FadeIn(dash, shift=DOWN * 0.2), Create(base), rt=0.4)
        G(self, LaggedStart(*[GrowFromEdge(c, DOWN) for c in cols2], lag_ratio=0.12), rt=0.6)
        G(self, GrowFromCenter(wrong), FadeIn(lw), rt=0.4)
        until(self, "has to grade them")
        ok = check(-4.0, 2.4, s=0.22)
        lg = L("graded", -3.0, 2.4, 36)
        G(self, Create(ok), FadeIn(lg), rt=0.4)
        finish(self)


# ───────────────────────────── 2 · What others have done ─────────────────────────────

class B03_Gap(Scene):
    """Prior work 2, run for real: pandera, dbt and GX Core flag the 25 fares; only the answer key shows 25 time-travel trips got through."""
    def construct(self):
        d, g, sc = RECORDED["dbt"], RECORDED["gx"], RECORDED["score"]
        rows = [("tool", "clean", "broken"),
                ("pandera", "PASS" if RECORDED["clean_pass"] else "FAIL", "FAIL {}".format(RECORDED["broken_flagged"])),
                ("dbt", d["clean"]["status"], d["broken"]["status"]),
                ("GX Core", "PASS" if g["clean"]["success"] else "FAIL", "FAIL {}".format(g["broken"]["unexpected_count"]))]
        texts = ["{:<10}{:<9}{}".format(*r) for r in rows] + [
            "answer key",
            "negative fares            {}/{}  {}".format(sc["negative_fare"]["caught"], sc["negative_fare"]["planted"], sc["negative_fare"]["verdict"]),
            "drop-off before pick-up    {}/{}  {}".format(sc["dropoff_before_pickup"]["caught"], sc["dropoff_before_pickup"]["planted"], sc["dropoff_before_pickup"]["verdict"])]
        win, lines = panel(texts, 0.0, 0.2, size=24, gap=0.52)
        self.play(FadeIn(act_tag(2)), FadeIn(win, shift=DOWN * 0.2), run_time=0.6)
        until(self, "Pandera")
        G(self, FadeIn(VGroup(*lines[:4])), rt=0.5)          # the three tools, as they are named
        until(self, "all caught")
        G(self, FadeIn(lines[4]), FadeIn(lines[5]), Create(mark_after(lines[5], True)), rt=0.5)
        until(self, "none caught")
        G(self, FadeIn(lines[6]), GrowFromCenter(mark_after(lines[6], False)), rt=0.5)
        G(self, FadeIn(recorded_tag(0.0, -2.95)), rt=0.3)
        finish(self)


def info_card(x, y, head, body, w=3.6, h=3.0):
    """A white card with a bold heading and one or two short lines (published results, see SOURCES.md)."""
    card = paper(x, y, w=w, h=h)
    txt = VGroup(T(head, 34, INK, True), *[T(b, 34) for b in body]).arrange(DOWN, buff=0.22).move_to([x, y, 0])
    return card, txt


class B04_PriorAI(Scene):
    """Prior work 3: AI already writes tests. GX Cloud's ExpectAI suggests checks; Meta's TestGen-LLM (2024) and ACH (2025) report results."""
    def construct(self):
        self.play(FadeIn(act_tag(2)), run_time=0.3)
        until(self, "Expect A I")
        c1, t1 = info_card(-4.15, 0.35, "GX Cloud", ["ExpectAI:", "suggests checks"])
        G(self, FadeIn(c1, shift=DOWN * 0.2), FadeIn(t1), rt=0.5)
        until(self, "at Meta")
        c2, t2 = info_card(0.0, 0.35, "Meta · 2024", ["75% built", "57% passed"])
        G(self, FadeIn(c2, shift=DOWN * 0.2), FadeIn(t2), rt=0.5)
        until(self, "a later tool")
        c3, t3 = info_card(4.15, 0.35, "Meta · 2025", ["planted bugs", "73% accepted"])
        G(self, FadeIn(c3, shift=DOWN * 0.2), FadeIn(t3), rt=0.5)
        until(self, "percent accepted")
        G(self, FadeIn(L("published results · sources in SOURCES.md", 0, -2.1, 30)), rt=0.3)
        finish(self)


class B05_Grid(Scene):
    """The gap: a comparison grid CONSTRUCTED from the sources (labelled on screen). Only DataSentry has all three."""
    def construct(self):
        f = "{:<18}{:<8}{:<9}{}"
        texts = [f.format("", "data", "planted", "AI-written"),
                 f.format("", "tables", "defects", "checks"),
                 f.format("mutation (1978)", "no", "yes", "no"),
                 f.format("Meta ACH (2025)", "no", "yes", "yes"),
                 f.format("dbt", "yes", "no", "no"),
                 f.format("GX + ExpectAI", "yes", "no", "yes"),
                 f.format("DataSentry", "yes", "yes", "yes")]
        win, lines = panel(texts, 0.0, 0.3, size=24, gap=0.5)
        self.play(FadeIn(act_tag(2)), FadeIn(win, shift=DOWN * 0.2), run_time=0.6)
        G(self, FadeIn(lines[0]), FadeIn(lines[1]), rt=0.3)
        until(self, "Mutation testing")
        G(self, FadeIn(lines[2]), FadeIn(lines[3]), rt=0.4)
        until(self, "in what I found")
        G(self, FadeIn(lines[4]), FadeIn(lines[5]), rt=0.4)
        until(self, "That's the gap")
        G(self, FadeIn(lines[6]), Create(mark_after(lines[6], True)), rt=0.4)
        G(self, FadeIn(L("constructed from the sources · in what I found", 0.0, -2.45, 30)), rt=0.3)
        finish(self)


# ───────────────────────────── 3 · Methods ─────────────────────────────

class B06_Table(Scene):
    """The data: NYC yellow taxi, January 2025, a 10,000-row sample (as used in the recorded run)."""
    def construct(self):
        card, cols, bars = table_card(-1.3, -0.3, w=7.2, h=4.6, rows=7)
        self.play(FadeIn(act_tag(3)), FadeIn(card, shift=DOWN * 0.2), run_time=0.5)
        until(self, "The data is public")
        G(self, LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.1), rt=1.0)
        until(self, "New York City")
        l1 = L("NYC taxi · Jan 2025", -1.3, 2.6, 40)
        G(self, FadeIn(l1), LaggedStart(*[GrowFromCenter(c) for c in cols], lag_ratio=0.1), rt=0.7)
        until(self, "ten thousand rows")
        l2 = VGroup(T("{:,}".format(RECORDED["rows"]), 48, bold=True), T("rows", 36)).arrange(DOWN, buff=0.12).move_to([4.6, -0.3, 0])
        G(self, FadeIn(l2), rt=0.35)
        finish(self)


class B07_StepOne(Scene):
    """Step 1 (built): a planter breaks copies of the table, five defect types, and locks away the answer key."""
    def construct(self):
        lt = L("Step 1", -4.9, 2.4, 44, bold=True)
        c1, h1, b1 = table_card(-4.5, 0.45, w=2.9, h=2.3, rows=4)
        self.play(FadeIn(act_tag(3)), FadeIn(lt), FadeIn(VGroup(c1, h1, b1), shift=DOWN * 0.2), run_time=0.5)
        until(self, "a planter script")
        a1 = Line([-2.8, 0.45, 0], [-1.55, 0.45, 0], color=INK, stroke_width=6)
        block = Iso(-0.6, -0.35, 0.95).mcp(0, 0, 0, w=1.3, d=1.3, h=0.8)
        l2 = L("planter", -0.6, -1.2)
        G(self, Create(a1), rt=0.4)
        G(self, FadeIn(block, shift=DOWN * 0.3), FadeIn(l2), rt=0.5)
        until(self, "five different ways")
        a2 = Line([0.45, 0.45, 0], [1.7, 0.45, 0], color=INK, stroke_width=6)
        c2, h2, b2 = table_card(3.45, 0.45, w=2.9, h=2.3, rows=4)
        marks = VGroup(*[Dot(np.array(b.get_right()) + np.array([-0.3, 0, 0]), radius=0.1, color=TERRA) for b in b2[1:3]])
        G(self, Create(a2), rt=0.4)
        G(self, FadeIn(VGroup(c2, h2, b2), shift=DOWN * 0.2), rt=0.5)
        G(self, LaggedStart(*[GrowFromCenter(m) for m in marks], lag_ratio=0.3), FadeIn(L("5 defect types", 3.45, 2.0, 32)), rt=0.5)
        until(self, "answer key")
        vault = make_original("secure-vault", height=1.5, x=3.45, y=-1.95)
        l3 = L("answer key", 0.9, -2.05)
        G(self, FadeIn(vault, shift=DOWN * 0.2), FadeIn(l3), rt=0.5)
        finish(self)


class B08_StepTwo(Scene):
    """Step 2 (built, run twice by hand): Claude writes pandera checks from column names only; a scorer grades them."""
    def construct(self):
        lt = L("Step 2", -4.9, 2.4, 44, bold=True)
        ws = make_original("agent-workstation", height=2.4, x=-4.7, y=0.45)
        self.play(FadeIn(act_tag(3)), FadeIn(lt), FadeIn(ws, shift=DOWN * 0.2), run_time=0.5)
        l1 = VGroup(T("Claude", 36), T("Opus 5.5", 32)).arrange(DOWN, buff=0.06).move_to([-4.7, -1.5, 0])
        self.play(FadeIn(l1), run_time=0.3)
        until(self, "writes pandera checks")
        a1 = Line([-3.3, 0.45, 0], [-2.3, 0.45, 0], color=INK, stroke_width=6)
        pages = VGroup(*[Iso(-1.45, -0.3 + i * 0.28, 0.75).page(0, 0, 0, w=1.3, d=1.4) for i in range(3)])
        l2 = L("pandera checks", -1.45, -1.3)
        G(self, Create(a1), rt=0.35)
        G(self, LaggedStart(*[FadeIn(pg, shift=DOWN * 0.3) for pg in pages], lag_ratio=0.3), FadeIn(l2), rt=0.8)
        until(self, "A scorer grades")
        a2 = Line([-0.4, 0.45, 0], [0.6, 0.45, 0], color=INK, stroke_width=6)
        cc, hc, bc = table_card(1.75, 1.25, w=1.9, h=1.4, rows=3)
        cb, hb, bb = table_card(1.75, -0.55, w=1.9, h=1.4, rows=3)
        dot = Dot(np.array(bb[1].get_right()) + np.array([-0.2, 0, 0]), radius=0.09, color=TERRA)
        G(self, Create(a2), rt=0.35)
        G(self, FadeIn(VGroup(cc, hc, bc)), FadeIn(VGroup(cb, hb, bb)), rt=0.5)
        G(self, GrowFromCenter(dot), rt=0.3)
        until(self, "every broken copy")
        a3 = Line([2.9, 0.35, 0], [3.8, 0.35, 0], color=INK, stroke_width=6)
        binder = make_original("evidence-binder", height=1.6, x=4.95, y=0.45)
        l3 = L("scorer", 4.95, -1.3)
        G(self, Create(a3), rt=0.35)
        G(self, FadeIn(binder, shift=DOWN * 0.2), FadeIn(l3), rt=0.5)
        ok = check(4.5, -2.05, s=0.2)
        miss = Dot([5.45, -2.05, 0], radius=0.12, color=TERRA)
        G(self, Create(ok), GrowFromCenter(miss), rt=0.4)
        finish(self)


class B09_StepThree(Scene):
    """Step 3 (built and run, 2026-11-23): the loop in Claude Code — write, score, clean-copy results only, revise."""
    def construct(self):
        lt = T("Step 3 \u00b7 built and run", 44, INK, True)
        lt.move_to([-6.0 + lt.width / 2, 2.4, 0])
        self.play(FadeIn(act_tag(3)), FadeIn(lt), run_time=0.5)
        until(self, "the loop")
        ws = make_original("agent-workstation", height=1.9, x=-4.1, y=0.15)
        l1 = L("write", -4.1, -1.25)
        G(self, FadeIn(ws, shift=DOWN * 0.2), FadeIn(l1), rt=0.45)
        a1 = Line([-2.9, 0.15, 0], [-1.6, 0.15, 0], color=INK, stroke_width=6)
        binder = make_original("evidence-binder", height=1.5, x=-0.3, y=0.15)
        l2 = L("score", -0.3, -1.25)
        G(self, Create(a1), rt=0.3)
        G(self, FadeIn(binder, shift=DOWN * 0.2), FadeIn(l2), rt=0.45)
        until(self, "Only the clean")
        a2 = Line([1.0, 0.15, 0], [2.3, 0.15, 0], color=INK, stroke_width=6)
        note = paper(3.5, 0.15, w=1.6, h=1.9)
        lines = tall_scribbles(note, n=3, gap=0.5)
        l3 = L("clean-copy results only", 3.5, -1.25, 34)
        G(self, Create(a2), rt=0.3)
        G(self, FadeIn(note, shift=DOWN * 0.2), Create(lines), FadeIn(l3), rt=0.5)
        until(self, "and Claude revises")
        back = ArcBetweenPoints([3.5, -1.75, 0], [-4.1, -1.75, 0], angle=-0.6, color=INK, stroke_width=6)
        lr = L("up to 3 rounds, all logged", 0.0, -2.8, 34)
        G(self, Create(back), rt=0.6)
        G(self, FadeIn(lr), rt=0.3)
        until(self, "It's built")
        ok = check(2.55, 2.42, s=0.2)
        lg = L("ran " + RECORDED["loop"]["date"], 4.45, 2.4, 36)
        G(self, Create(ok), FadeIn(lg), rt=0.4)
        finish(self)


class B09A_Tools(Scene):
    """Tools and permissions: Claude runs fenced (no built-in tools, an empty folder, never the answer keys or held-out
    data); model-written code passes a code policy before it runs. Next (planned): a small tool menu, every call checked."""
    def construct(self):
        self.play(FadeIn(act_tag(3)), run_time=0.3)
        until(self, "fenced")
        ws = make_original("agent-workstation", height=2.0, x=-4.3, y=0.5)
        fence = DashedVMobject(RoundedRectangle(width=3.4, height=3.0, corner_radius=0.2, stroke_color=INK, stroke_width=5),
                               num_dashes=40).move_to([-4.3, 0.45, 0])
        lf = L("no tools \u00b7 empty folder", -4.3, -1.45, 32)
        G(self, FadeIn(ws, shift=DOWN * 0.2), Create(fence), FadeIn(lf), rt=0.6)
        until(self, "no answer keys")
        ln = L("no answer keys \u00b7 no held-out data", -3.3, -2.15, 32)
        G(self, FadeIn(ln), rt=0.4)
        until(self, "code policy")
        gate = make_original("permission-gate", height=2.4, x=0.2, y=0.35)
        lg = L("code policy", 0.2, -1.45, 34)
        G(self, FadeIn(gate, shift=DOWN * 0.2), FadeIn(lg), rt=0.5)
        until(self, "tool menu")
        menu = paper(4.25, 0.35, w=3.9, h=2.6)
        tools = ["profile_column", "write_checks", "run_dev_scorer", "submit_for_review"]
        rows = VGroup(*[M(t, 24) for t in tools]).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([4.25, 0.35, 0])
        lm = L("next: tool menu", 4.25, 2.15, 34, bold=True)
        G(self, FadeIn(menu, shift=DOWN * 0.2), FadeIn(lm), rt=0.4)
        G(self, LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.2), rt=0.5)
        lc = L("each call checked", 4.25, -1.45, 32)
        G(self, FadeIn(lc), rt=0.3)
        finish(self)


class B09B_Gate(Scene):
    """The human gate (planned): the person sees the scorecard, the code and its sha256, then approves, refuses or
    defers; the decision is bound to that hash, and nothing is kept without approval."""
    def construct(self):
        card = paper(-2.6, 0.2, w=5.6, h=3.6)
        lt = L("review", -2.6, 1.55, 40, bold=True)
        self.play(FadeIn(act_tag(3)), FadeIn(card, shift=DOWN * 0.2), FadeIn(lt), run_time=0.5)
        lp = L("planned", 4.6, 2.45, 32)
        self.play(FadeIn(lp), run_time=0.3)
        until(self, "the scorecard")
        rows = VGroup(T("scorecard", 36), T("code", 36), T("sha256 fingerprint", 36)).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([-2.6, -0.25, 0])
        G(self, LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.3), rt=0.7)
        until(self, "and approve")
        bx = 3.4

        def button(y, text):
            b = RoundedRectangle(width=3.0, height=0.8, corner_radius=0.15, fill_color=CARD, fill_opacity=1,
                                 stroke_color=INK, stroke_width=4).move_to([bx, y, 0])
            return VGroup(b, T(text, 36).move_to([bx + 0.2, y, 0]))
        b1, b2, b3 = button(1.2, "approve"), button(0.1, "refuse"), button(-1.0, "defer")
        m1 = check(bx - 1.05, 1.23, s=0.17)
        m2 = Dot([bx - 1.05, 0.1, 0], radius=0.11, color=TERRA)
        G(self, FadeIn(b1), Create(m1), rt=0.35)
        G(self, FadeIn(b2), GrowFromCenter(m2), rt=0.35)
        G(self, FadeIn(b3), rt=0.35)
        until(self, "Nothing is kept")
        G(self, FadeIn(L("nothing kept without approval", 0.0, -2.45, 36)), rt=0.4)
        finish(self)


class B10_Resources(Scene):
    """Resources: public data, a laptop, the existing Claude subscription; no API key, no token credits."""
    def construct(self):
        card = paper(0.0, -0.1, w=8.8, h=4.6)
        self.play(FadeIn(act_tag(3)), FadeIn(card, shift=DOWN * 0.2), run_time=0.5)
        items = [("public data", "data: public (NYC TLC)"), ("my laptop", "compute: my laptop"),
                 ("Claude subscription", "Claude: my existing subscription"), ("No API key", "API key, credits: none")]
        ys = [1.4, 0.5, -0.4, -1.3]
        for (phrase, text), y in zip(items, ys):
            until(self, phrase)
            ok = check(-3.6, y + 0.03, s=0.2)
            t = T(text, 36)
            t.move_to([-3.0 + t.width / 2, y, 0])
            G(self, Create(ok), FadeIn(t), rt=0.4)
        finish(self)


# ───────────────────────────── 4 · Evaluation ─────────────────────────────

class B11_Measures(Scene):
    """What is measured, for every set of checks: defects caught, false alarms, crashes, the held-out planting."""
    def construct(self):
        self.play(FadeIn(act_tag(4)), run_time=0.3)
        xs = [-4.6, -1.55, 1.55, 4.6]
        names = ["defects caught", "false alarms", "crashes", "held-out data"]
        for i, (phrase, x, nm) in enumerate(zip(["defect types caught", "false alarms", "crashing checks", "held-out data"], xs, names)):
            until(self, phrase)
            sh = paper(x, 0.45, w=1.9, h=2.3)
            n = L(str(i + 1), x, 0.45, 72, bold=True)
            lb = L(nm, x, -1.3, 34)
            G(self, FadeIn(sh, shift=DOWN * 0.3), FadeIn(n), FadeIn(lb), rt=0.45)
        finish(self)


class B12_PassLine(Scene):
    """The pass line, set before the next run: 5 of 5 caught, 0 good trips flagged, 0 crashes, on both plantings."""
    def construct(self):
        card = paper(0.0, 0.15, w=9.4, h=4.3)
        title = L("pass line", 0.0, 1.75, 44, bold=True)
        self.play(FadeIn(act_tag(4)), FadeIn(card, shift=DOWN * 0.2), FadeIn(title), run_time=0.6)
        items = [("all five", "5 of 5 defect types caught"), ("zero good", "0 good trips flagged"),
                 ("no crashing", "0 crashing checks")]
        ys = [0.75, -0.15, -1.05]
        for (phrase, text), y in zip(items, ys):
            until(self, phrase)
            ok = check(-3.4, y + 0.03, s=0.2)
            t = T(text, 38)
            t.move_to([-2.8 + t.width / 2, y, 0])
            G(self, Create(ok), FadeIn(t), rt=0.4)
        until(self, "both plantings")
        G(self, FadeIn(L("on both plantings · anything less fails", 0.0, -2.55, 36)), rt=0.4)
        finish(self)


class B13_SoFar(Scene):
    """Results (recorded output, the live loop run of 2026-11-23): round 1 and 2 below the pass line, round 3 meets it;
    round 3's checks on a second clean copy the loop never saw: 0 good trips flagged."""
    def construct(self):
        lp = RECORDED["loop"]
        rs = {r["round"]: r for r in lp["rounds"]}
        def cell(r):
            if r["clean_crashed"]:
                return "1 check crashes" if r["clean_crashed"] == 1 else "%d checks crash" % r["clean_crashed"]
            n = r["clean_rows"]
            return "PASS" if not n else ("1 row flagged" if n == 1 else "%d rows flagged" % n)
        f = "{:<8}{:<19}{}"
        texts = ["$ ./run_loop.sh", f.format("round", "clean copy", "caught (both plantings)")] + \
                [f.format(str(k), cell(rs[k]), "%d of 5" % min(rs[k]["caught"], rs[k]["caught99"])) for k in sorted(rs)] + \
                ["second clean copy, round %d:  %d flagged" % (max(rs), rs[max(rs)]["heldout_clean_rows"])]
        win, lines = panel(texts, 0.0, -0.2, size=24, gap=0.54)
        lh = L("the loop's results", 0.0, 2.5, 40, bold=True)
        self.play(FadeIn(act_tag(4)), FadeIn(win, shift=DOWN * 0.2), FadeIn(lh), run_time=0.6)
        G(self, FadeIn(lines[0]), FadeIn(lines[1]), rt=0.3)
        for k, phrase in zip(sorted(rs), ["round one", "round two", "round three"]):
            until(self, phrase)
            ln = lines[1 + k]
            G(self, FadeIn(ln), (Create if rs[k]["passes"] else GrowFromCenter)(mark_after(ln, rs[k]["passes"])), rt=0.4)
        until(self, "second clean copy")
        hc = rs[max(rs)]["heldout_clean_rows"] == 0
        G(self, FadeIn(lines[-1]), (Create if hc else GrowFromCenter)(mark_after(lines[-1], hc)), rt=0.4)
        G(self, FadeIn(L("Claude Opus 5.5 \u00b7 recorded output \u00b7 " + lp["date"], 0.0, -2.75, 30)), rt=0.3)
        finish(self)


class B13A_Failures(Scene):
    """Planned failure cases: at least five deliberate ones, and one controlled failure (predicted, triggered, caught by
    the held-out scorer, refused at the gate)."""
    def construct(self):
        lp = L("planned", 4.6, 2.45, 32)
        self.play(FadeIn(act_tag(4)), FadeIn(lp), run_time=0.4)
        until(self, "at least five ways")
        names = ["forbidden import", "crashing check", "hard-coded values", "empty reply", "answer-key read"]
        pos = [(-4.2, 1.35), (0.0, 1.35), (4.2, 1.35), (-2.1, 0.35), (2.1, 0.35)]
        items = []
        for nm, (x, y) in zip(names, pos):
            t = T(nm, 34).move_to([x + 0.2, y, 0])
            d = Dot([x + 0.2 - len(nm) * 0.095 - 0.4, y, 0], radius=0.11, color=TERRA)   # from the character count (Gate A's stub agrees)
            items.append(VGroup(d, t))
        G(self, LaggedStart(*[FadeIn(i) for i in items], lag_ratio=0.2), rt=1.0)
        until(self, "one controlled failure")
        lc = L("controlled failure", 0.0, -0.9, 40, bold=True)
        G(self, FadeIn(lc), rt=0.4)
        steps = ["predict", "trigger", "held-out catches it", "refused at the gate"]
        ts = VGroup(*[T(st, 32) for st in steps]).arrange(RIGHT, buff=1.0).move_to([0, -1.95, 0])
        arrows = [Line(np.array(ts[i].get_right()) + np.array([0.15, 0, 0]), np.array(ts[i + 1].get_left()) - np.array([0.15, 0, 0]),
                       color=INK, stroke_width=4) for i in range(3)]
        G(self, FadeIn(ts[0]), rt=0.3)
        for i in range(1, 4):
            G(self, Create(arrows[i - 1]), FadeIn(ts[i]), rt=0.35)
        finish(self)


class B14_Outcome(Scene):
    """What the result shows, and what it does not: claims no stronger than the evidence (text only, no card borders)."""
    def construct(self):
        divider = Line([0, 1.9, 0], [0, -2.0, 0], color=INK, stroke_width=4)
        self.play(FadeIn(act_tag(4)), Create(divider), run_time=0.5)
        until(self, "it worked")
        h1 = L("shown", -3.1, 1.4, 44, bold=True)
        ok = check(-4.55, 1.43, s=0.22)
        b1 = VGroup(T("this table,", 38), T("5 defect types,", 38), T("passed in 3 rounds", 38)).arrange(DOWN, buff=0.3).move_to([-3.1, -0.35, 0])
        G(self, FadeIn(h1), Create(ok), rt=0.4)
        G(self, FadeIn(b1, shift=DOWN * 0.15), rt=0.5)
        until(self, "Not shown yet")
        h2 = L("not shown yet", 3.1, 1.4, 44, bold=True)
        dot = Dot([0.85, 1.4, 0], radius=0.13, color=TERRA)
        b2 = VGroup(T("other tables", 38), T("real defects", 38), T("I didn't plant", 38)).arrange(DOWN, buff=0.3).move_to([3.1, -0.35, 0])
        G(self, FadeIn(h2), GrowFromCenter(dot), rt=0.4)
        G(self, FadeIn(b2, shift=DOWN * 0.15), rt=0.5)
        finish(self)


END_HOLD = 4.0   # seconds of silent tail on BEND (finish_audio.py) that hold the end screen


class BEND_Close(Scene):
    """Close: the scanner returns; the title and Ethan's name land beside it; then the end screen:
    'Thank you', the project title, 'Final Project Film', and Ethan's name."""
    def construct(self):
        rig = scanner(3.8, -3.2, -0.1)
        vec = rig.action_vectors["parcel"]
        rig.parts["parcel"].shift(vec)
        self.play(FadeIn(rig, shift=DOWN * 0.2), run_time=0.4)
        title = L("DataSentry", 2.4, 0.5, 64, bold=True)
        name = L("Ethan Gomes", 2.4, -0.55, 40)
        self.play(FadeIn(title), run_time=0.35)
        self.play(FadeIn(name), run_time=0.35)
        G(self, rig.parts["parcel"].animate.shift(-vec), rt=0.8, rate_func=smooth)
        light = Dot(np.array(rig.parts["parcel"].get_center()) + np.array([0, 0.22, 0]), radius=0.09, color=TERRA).set_z_index(1.5)
        G(self, GrowFromCenter(light), rt=0.3)
        # end screen (Ethan, 2026-11-23): after the last word, a thank-you card holds for the silent 4 s tail
        tgt = _TARGET.get("BEND", 0)
        if tgt:
            self.wait(max(0.1, tgt - END_HOLD - _elapsed(self)))
        G(self, FadeOut(VGroup(rig, title, name, light)), rt=0.5)
        thanks = L("Thank you", 0, 1.75, 80, bold=True)
        proj = L("DataSentry", 0, 0.45, 60, bold=True)
        rule = Line([-3.0, -0.4, 0], [2.8, -0.4, 0], color=BAR1, stroke_width=5)
        dot = Dot([3.1, -0.4, 0], radius=0.12, color=TERRA)
        film = L("Final Project Film", 0, -1.25, 40)
        who = L("Ethan Gomes", 0, -2.05, 44, bold=True)
        G(self, FadeIn(thanks, shift=UP * 0.1), FadeIn(proj), rt=0.6)
        G(self, Create(rule), GrowFromCenter(dot), FadeIn(film), FadeIn(who), rt=0.6)
        finish(self)
