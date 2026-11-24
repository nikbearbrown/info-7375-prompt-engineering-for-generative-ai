
# ═════════════════════════════ DAYTHREAD FINAL PROJECT FILM — scene body (2026-11-23) ═════════════════════════════
# Helpers and the cast are copied from the October pitch film's scenes_body.py. Every [C] beat illustrates a
# CONSTRUCTED, PROPOSED workflow — nothing here was observed from a running system (no DayThread prototype,
# contract, checker or evaluation exists). The only observed result shown is the 2026-10-25 replay (B02, B03). Cast reused across beats: the check-in page (raw transcript), the
# summary page, the separate check (terracotta scan line), the memory drawers, the coordinator's review page /
# desk, and the permission gate (closed, stop light lit, until a coordinator approves).
# Timing: the measured Kokoro narration is the clock (no padding except BOUT's 1.0 s tail). Motions cue on
# faster-whisper word starts stored per beat in beat_sheet.json (`words`, written by audio_post.py).

MID_GUARD = 0.22          # GATE T and Gate V sample the clip midpoint: keep motion out of [mid-0.22, mid+0.22]
SCRIB_AMP = 0.085         # GATE T measures handwriting scribbles as text runs; 0.085 keeps short ones >= 41 px
CAP_SIZE = 34
try:
    _WORDS = {b["beat_id"]: b.get("words", []) for b in _SHEET["beats"]}
except Exception:
    _WORDS = {}


def _bid(self):
    return type(self).__name__.split("_")[0]


def _target(self):
    return _TARGET.get(_bid(self), 0.0)


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def at(self, t):
    gap = t - _elapsed(self)
    if gap > 0.02:
        self.wait(gap)


def at_word(self, word, nth=1, early=0.12):
    """Wait until the nth spoken occurrence of `word` (prefix match on the whisper word list)."""
    want, seen = _norm(word), 0
    for w, t in _WORDS.get(_bid(self), []):
        if _norm(w).startswith(want):
            seen += 1
            if seen == nth:
                at(self, t - early)
                return


def done(self):
    """Hold to the end of the beat's audio, never past it (the kit's finish() waits >= 0.3 s even when late)."""
    target = _target(self)
    if not target:
        self.wait(1.0)
        return
    gap = target - _elapsed(self) - 0.06
    if gap > 0.02:
        self.wait(gap)


def span(self, *anims, rt=0.5, **kw):
    """play() that never crosses the midpoint window and never runs past the beat's audio."""
    target = _target(self)
    if target:
        mid, now = target / 2, _elapsed(self)
        if now < mid + MID_GUARD and now + rt > mid - MID_GUARD:
            at(self, mid + MID_GUARD)
        now = _elapsed(self)
        if now + rt > target - 0.15:
            rt = max(0.12, target - 0.15 - now)
    self.play(*anims, run_time=rt, **kw)


# ── captions: italic, in their own bands, never mixed with scene headings (headings stay inside y <= 2.3) ──
def CAP(s):
    return Text(s, font=SERIF, color=INK, font_size=CAP_SIZE, slant="ITALIC")   # string form: Gate A's stub has no ITALIC constant


PARTS = {1: "1 · Executive summary", 2: "2 · Introduction", 3: "3 · Methods", 4: "4 · Evaluation"}


def captions(kind=None, part=None):
    g = VGroup(CAP("Synthesized voice reading Aditya’s script").move_to([-6.1, 3.1, 0], aligned_edge=LEFT))
    if part:
        g.add(CAP(PARTS[part]).move_to([6.1, 3.1, 0], aligned_edge=RIGHT))
    if kind == "C":
        g.add(CAP("Constructed — proposed workflow").move_to([0, -3.1, 0]))
    elif kind == "D":
        g.add(CAP("From each company’s own documentation, read 2026-10-14").move_to([0, -3.1, 0]))
    elif kind == "R":
        g.add(CAP("Replay run 2026-10-25 · synthetic data · fictional client").move_to([0, -3.1, 0]))
    return g


def L(s, x, y, size=40):
    return T(s, size).move_to([x, y, 0])


# ── the cast ──
def checkin_page(x, y, w=2.8, h=3.3, n=5, dot=2, short_last=True):
    """A check-in page: paper + n handwriting lines; a terracotta dot marks line `dot` (None = no dot)."""
    pg = paper(x, y, w, h)
    my, mx, mr = min(0.55, 0.18 * h + 0.1), min(0.55, 0.2 * w + 0.1), min(0.4, 0.15 * w + 0.1)
    step = (h - 2 * my) / (n - 1)
    x0, lw = x - w / 2 + mx, w - mx - mr
    ys = [y + h / 2 - my - i * step for i in range(n)]
    lines = VGroup(*[scribble(x0, yy, lw * (0.6 if (short_last and i == n - 1) else 1.0), amp=SCRIB_AMP)
                     for i, yy in enumerate(ys)])
    g = VGroup(pg, lines)
    g.pg, g.lines, g.ys, g.x0, g.lw = pg, lines, ys, x0, lw
    g.dot = None
    if dot is not None:
        g.dot = Dot([x0 - min(0.24, mx - 0.1), ys[dot], 0], radius=0.09 if w > 1.5 else 0.07, color=TERRA)
    return g


def summary_page(x, y, w=2.3, h=2.6, gap_row=2):
    """Shorter page with a dashed empty row where the tumble line should have been."""
    pg = paper(x, y, w, h)
    x0, lw = x - w / 2 + 0.38, w - 0.76
    my = min(0.5, 0.17 * h + 0.06)
    step = (h - 2 * my) / 3
    ys = [y + h / 2 - my - i * step for i in range(4)]
    lines = VGroup(*[scribble(x0, yy, lw * (0.55 if i == 3 else 1.0), amp=SCRIB_AMP)
                     for i, yy in enumerate(ys) if i != gap_row])
    gap = DashedLine([x0, ys[gap_row], 0], [x0 + lw, ys[gap_row], 0], color=DIM, stroke_width=4, dash_length=0.16)
    g = VGroup(pg, lines, gap)
    g.gap = gap
    return g


def slip(x, y, w=1.6, h=0.72):
    s = paper(x, y, w, h)
    d = Dot([x - w / 2 + 0.28, y, 0], radius=0.08, color=TERRA)
    ln = scribble(x - w / 2 + 0.5, y, w - 0.8, amp=SCRIB_AMP)
    return VGroup(s, d, ln)


def envelope(x, y, w=0.95, h=0.62):
    body = Rectangle(width=w, height=h, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    flap = VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners(
        [[-w / 2, h / 2, 0], [0, -h * 0.05, 0], [w / 2, h / 2, 0]])
    return VGroup(body, flap).move_to([x, y, 0])


def gate(x, y, h=2.4):
    """The permission-gate prop with its own barrier replaced by a horizontal boom arm that visibly blocks the
    lane (closed) and swings up only after approval (`open_gate`), plus a terracotta stop light on the left post."""
    g = make_original("permission-gate", height=h, x=x, y=y)
    g.remove(g.parts["barrier"])
    pivot = np.array([x - 0.30 * h, y + 0.05 * h, 0])
    boom = Rectangle(width=0.72 * h, height=0.085 * h, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK,
                     stroke_width=4).move_to(pivot + np.array([0.36 * h, 0, 0]))
    g.add(boom)
    g.boom, g.pivot = boom, pivot
    g.light = Dot([x - 0.30 * h, y + 0.22 * h, 0], radius=0.11 if h > 1.5 else 0.08, color=TERRA)
    return g


def open_gate(g):
    return Rotate(g.boom, angle=PI * 0.42, about_point=g.pivot)


def plinth(cx, cy, w=3.4, d=1.3, hgt=0.3):
    """A flat shelf/plinth seen from the front: kraft top face + front face, ink outlines. `d` is unused
    (kept for call compatibility); the top face recedes by a fixed 0.35."""
    front = Rectangle(width=w, height=hgt, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([cx, cy, 0])
    top = Polygon([cx - w / 2, cy + hgt / 2, 0], [cx + w / 2, cy + hgt / 2, 0], [cx + w / 2 + 0.3, cy + hgt / 2 + 0.32, 0],
                  [cx - w / 2 + 0.3, cy + hgt / 2 + 0.32, 0], fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(top, front)


def arrow(x0, y0, x1, y1):
    return Arrow([x0, y0, 0], [x1, y1, 0], buff=0, color=INK, stroke_width=5, max_tip_length_to_length_ratio=0.25)


# ═════════════════════════════ scenes ═════════════════════════════


# ═════════════════════════════ scenes ═════════════════════════════

class BIDEA_Title(Scene):
    def construct(self):
        self.add(captions())
        name = L("Aditya Raj", 0, 0.05, 48)
        title = T("DayThread", 120).move_to([0, 1.3, 0])
        sub = L("final project · the plan", 0, -0.7, 44)
        span(self, FadeIn(name, shift=UP * 0.15), rt=0.45)
        at_word(self, "This")
        span(self, FadeIn(title, shift=UP * 0.2), rt=0.55)
        at_word(self, "final")
        span(self, FadeIn(sub, shift=UP * 0.15), rt=0.45)
        thread = Line([-4.2, -1.55, 0], [4.2, -1.55, 0], color=INK, stroke_width=5)
        span(self, Create(thread), rt=0.6)
        pages = VGroup(*[paper(x, -1.97, 0.6, 0.78) for x in (-2.6, 0.0, 2.6)])
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pages], lag_ratio=0.25), rt=0.8)
        done(self)


# ── Part 1 · Executive summary ──

class B01_WhatItIs(Scene):
    def construct(self):
        self.add(captions("C", 1))
        ty = -0.75
        t1 = Line([-5.7, ty, 0], [-0.4, ty, 0], color=INK, stroke_width=5)
        t2 = Line([-0.4, ty, 0], [2.6, ty, 0], color=INK, stroke_width=5)
        span(self, Create(t1), rt=0.6)
        d1 = checkin_page(-4.3, 0.75, 2.0, 2.4, n=4, dot=None)
        d2 = checkin_page(-1.6, 0.75, 2.0, 2.4, n=4, dot=1)
        l1, l2 = L("Day 1", -4.3, -1.25), L("Day 2", -1.6, -1.25)
        at_word(self, "remember")
        span(self, FadeIn(d1, shift=DOWN * 0.3), FadeIn(l1), rt=0.5)
        at_word(self, "next")
        span(self, FadeIn(d2, shift=DOWN * 0.3), FadeIn(l2), rt=0.5)
        at_word(self, "concerning")
        span(self, GrowFromCenter(d2.dot), rt=0.35)
        desk = make_original("review-desk", height=2.2, x=4.2, y=-0.35)
        desk.remove(desk.parts["evidence"])
        lc = L("coordinator", 4.2, -1.95)
        at_word(self, "exact")
        span(self, Create(t2), FadeIn(desk, shift=UP * 0.2), FadeIn(lc), rt=0.6)
        ev = slip(-1.6, -0.2, 1.3, 0.6)
        at_word(self, "coordinator")
        span(self, FadeIn(ev, scale=1.1), rt=0.3)
        span(self, MoveAlongPath(ev, ArcBetweenPoints(np.array([-1.6, -0.2, 0]), np.array([4.15, 0.25, 0]), angle=-PI / 4)),
             rt=0.9, rate_func=smooth)
        done(self)


class B02_Why(Scene):
    """The one observed result: the 2026-10-25 replay (replay/RESULTS.md, Aditya's review)."""
    def construct(self):
        self.add(captions("R", 1))
        cp = checkin_page(-4.7, 0.1, 2.2, 2.7, n=4, dot=1)
        lc = L("check-in", -4.7, 1.85)
        at_word(self, "reread")
        span(self, FadeIn(cp, shift=UP * 0.2), FadeIn(cp.dot), FadeIn(lc), rt=0.5)
        a = arrow(-3.35, 0.1, -2.55, 0.1)
        sp = checkin_page(-1.2, 0.1, 2.0, 2.4, n=3, dot=0)
        ls = L("summary", -1.2, 1.85)
        at_word(self, "summary")
        span(self, GrowArrow(a), FadeIn(sp, shift=LEFT * 0.3), FadeIn(sp.dot), FadeIn(ls), rt=0.55)
        k1 = T("kept the fall: 10 of 10", 38).move_to([0.4, 0.7, 0], aligned_edge=LEFT)
        k2 = T("meaning changed: 9 of 10", 38).move_to([0.4, -0.4, 0], aligned_edge=LEFT)
        at_word(self, "kept")
        span(self, FadeIn(k1, shift=LEFT * 0.15), rt=0.4)
        at_word(self, "changed")
        span(self, FadeIn(k2, shift=LEFT * 0.15), rt=0.4)
        bar = Line([0.4, -0.85, 0], [5.4, -0.85, 0], color=TERRA, stroke_width=8)
        span(self, Create(bar), rt=0.4)
        done(self)


class B03_Exists(Scene):
    def construct(self):
        self.add(captions(None, 1))
        p1, p2 = plinth(-3.3, -1.1, w=4.2), plinth(3.1, -1.1, w=5.4)
        l1, l2 = L("ran", -3.3, 1.85), L("planned", 3.1, 1.85)
        at_word(self, "test")
        pg = checkin_page(-3.3, 0.25, 1.2, 1.6, n=3, dot=1)
        lr = L("replay · 2026-10-25", -3.3, -1.85, 36)
        span(self, FadeIn(p1), FadeIn(l1), FadeIn(pg, shift=DOWN * 0.2), FadeIn(pg.dot), FadeIn(lr), rt=0.55)
        ghosts = VGroup(*[DashedVMobject(Rectangle(width=0.82, height=1.15, color=INK, stroke_width=4), num_dashes=14)
                          .move_to([1.1 + i * 1.0, 0.2, 0]) for i in range(5)])
        at_word(self, "Everything")
        span(self, FadeIn(p2), FadeIn(l2), rt=0.4)
        span(self, LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.2), rt=0.9)
        done(self)


# ── Part 2 · Introduction ──

def lifeline_group(cx):
    pl = plinth(cx, -1.15)
    cord = VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners([[cx - 1.45, 1.05, 0], [cx - 0.95, 0.25, 0], [cx - 0.45, 1.05, 0]])
    pend = Circle(radius=0.34, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([cx - 0.95, -0.05, 0])
    tower, lights = Iso(cx + 0.9, -0.95, 1.0).server(-0.35, -0.35, 0, 0.7, 0.7, slab=0.38, n=3)
    head = L("Lifeline", cx, 1.75)
    return pl, VGroup(cord, pend), tower, lights, head


def dailycall_group(cx):
    pl = plinth(cx, -1.15)
    phone = VGroup(RoundedRectangle(width=0.95, height=1.7, corner_radius=0.14, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4),
                   Rectangle(width=0.72, height=1.25, fill_color=CARD, fill_opacity=1, stroke_width=0)).move_to([cx - 0.85, 0.3, 0])
    sm = paper(cx + 0.75, 0.3, 1.3, 1.6)
    smlines = VGroup(*[Line([cx + 0.3, 0.7 - i * 0.38, 0], [cx + 1.2, 0.7 - i * 0.38, 0], color=GHOST, stroke_width=6) for i in range(3)])
    head = L("DailyCall", cx, 1.75)
    return pl, phone, VGroup(sm, smlines), head


class B04_Others(Scene):
    def construct(self):
        self.add(captions("D", 2))
        lx, dx = -2.9, 2.9
        pl1, pend, tower, lights, h1 = lifeline_group(lx)
        pl2, phone, sm, h2 = dailycall_group(dx)
        span(self, FadeIn(pl1), FadeIn(pl2), rt=0.45)
        at_word(self, "Lifeline")
        span(self, FadeIn(pend, shift=DOWN * 0.2), FadeIn(tower), FadeIn(lights), FadeIn(h1), rt=0.5)
        arcs = VGroup(*[Arc(radius=r, start_angle=-PI / 5, angle=2 * PI / 5, color=INK, stroke_width=4).move_arc_center_to([lx - 0.95, -0.05, 0])
                        for r in (0.6, 0.85)])
        at_word(self, "detect", nth=2) if sum(_norm(w).startswith("detect") for w, _ in _WORDS.get("B04", [])) >= 2 else at_word(self, "detect")
        span(self, LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), rt=0.5)
        span(self, lights.animate.set_color(TERRA), rt=0.3)
        at_word(self, "DailyCall") if any(_norm(w).startswith("dailycall") for w, _ in _WORDS.get("B04", [])) else at_word(self, "Daily")
        span(self, FadeIn(phone, shift=DOWN * 0.2), FadeIn(h2), rt=0.45)
        at_word(self, "summaries")
        span(self, FadeIn(sm, shift=LEFT * 0.2), rt=0.45)
        done(self)


class B05_Focus(Scene):
    def construct(self):
        self.add(captions("C", 2))
        lx, dx = -2.9, 2.9
        pl1, pend, tower, lights, h1 = lifeline_group(lx)
        pl2, phone, sm, h2 = dailycall_group(dx)
        lights.set_color(TERRA)
        arcs = VGroup(*[Arc(radius=r, start_angle=-PI / 5, angle=2 * PI / 5, color=INK, stroke_width=4).move_arc_center_to([lx - 0.95, -0.05, 0])
                        for r in (0.6, 0.85)])
        left = VGroup(pl1, pend, tower, lights, arcs)
        mid = VGroup(pl2, phone, sm)
        self.add(left, mid, h1, h2)
        span(self, left.animate.scale(0.72).move_to([-4.65, -0.25, 0]), mid.animate.scale(0.72).move_to([-1.0, -0.25, 0]),
             h1.animate.move_to([-4.65, 1.2, 0]), h2.animate.move_to([-1.0, 1.2, 0]), rt=0.6)
        cx = 3.6
        pl3 = plinth(cx, -1.15, w=3.6)
        h3 = L("DayThread · planned", cx, 1.75)
        at_word(self, "narrower")
        span(self, FadeIn(pl3, shift=LEFT * 0.4), FadeIn(h3), rt=0.5)
        pgs = VGroup(*[paper(cx - 1.25 + i * 0.85, 0.55, 0.62, 0.8) for i in range(3)])
        dots = VGroup(*[Dot([cx - 1.25 + i * 0.85, 0.55, 0], radius=0.07, color=TERRA) for i in range(3)])
        at_word(self, "linked")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in pgs], lag_ratio=0.25), FadeIn(dots), rt=0.55)
        sl = Line([cx - 1.65, 0.95, 0], [cx - 1.65, 0.15, 0], color=TERRA, stroke_width=8)
        at_word(self, "separate")
        span(self, Create(sl), rt=0.25)
        span(self, sl.animate.shift(RIGHT * 2.3), rt=0.8, rate_func=linear)
        span(self, FadeOut(sl), rt=0.25)
        mg = gate(cx + 1.2, -0.55, 1.15)
        concern = slip(cx - 0.55, -0.45, 1.0, 0.5)
        thr = VGroup(*[Line([cx - 1.25 + i * 0.85, 0.15, 0], [cx - 0.55, -0.2, 0], color=INK, stroke_width=4) for i in range(3)])
        at_word(self, "person")
        span(self, FadeIn(mg), FadeIn(mg.light), rt=0.4)
        at_word(self, "leaves")
        span(self, LaggedStart(*[Create(t) for t in thr], lag_ratio=0.2), FadeIn(concern, scale=1.1), rt=0.7)
        done(self)


# ── Part 3 · Methods ──

class B06_Contract(Scene):
    def construct(self):
        self.add(captions("C", 3))
        cp = checkin_page(-5.0, 0.2, 2.0, 2.5, n=4, dot=None)
        seal = Dot([-4.45, -0.7, 0], radius=0.13, color=TERRA)
        lc = L("contract", -5.0, 1.85)
        at_word(self, "delegation")
        span(self, FadeIn(cp, shift=UP * 0.2), FadeIn(lc), rt=0.45)
        span(self, GrowFromCenter(seal), rt=0.3)
        xs = (-1.9, 0.9, 3.7)
        steps = VGroup(*[VGroup(paper(x, 0.2, 1.5, 1.1), scribble(x - 0.5, 0.2, 1.0, amp=SCRIB_AMP)) for x in xs])
        arrs = VGroup(arrow(-1.05, 0.2, 0.05, 0.2), arrow(1.75, 0.2, 2.85, 0.2))
        lh = L("handoffs", 0.9, -1.1)
        at_word(self, "step")
        span(self, LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in steps], lag_ratio=0.25), rt=0.6)
        span(self, LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.3), FadeIn(lh), rt=0.5)
        cks = VGroup(check(-0.5, 0.75, s=0.17), check(2.3, 0.75, s=0.17))
        at_word(self, "check")
        span(self, LaggedStart(*[Create(c) for c in cks], lag_ratio=0.3), rt=0.5)
        stop = Line([2.3, -0.3, 0], [2.3, 0.7, 0], color=INK, stroke_width=10)
        ls = L("stop", 2.3, 1.25)
        at_word(self, "fails")
        span(self, FadeOut(cks[1]), rt=0.25)
        at_word(self, "stops")
        span(self, Create(stop), FadeIn(ls), rt=0.4)
        tests = VGroup(*[check(-5.75 + i * 0.55, -1.6, s=0.14) for i in range(3)])
        lt = L("tests first", -4.4, -2.2, 36)
        at_word(self, "tests")
        span(self, LaggedStart(*[Create(t) for t in tests], lag_ratio=0.25), FadeIn(lt), rt=0.6)
        done(self)


class B07_Handoffs(Scene):
    def construct(self):
        self.add(captions("C", 3))
        bx = -4.5
        bnd = make_original("evidence-binder", height=1.9, x=bx, y=-0.25)
        la = L("append only", bx, -1.85)
        at_word(self, "saved")
        span(self, FadeIn(bnd, shift=UP * 0.2), FadeIn(la), rt=0.5)
        ow = paper(bx - 1.3, 1.45, 1.0, 0.65)
        xx = VGroup(Line([bx - 1.6, 1.2, 0], [bx - 1.0, 1.7, 0], color=INK, stroke_width=6),
                    Line([bx - 1.6, 1.7, 0], [bx - 1.0, 1.2, 0], color=INK, stroke_width=6))
        at_word(self, "edited")
        span(self, FadeIn(ow, shift=RIGHT * 0.3), rt=0.3)
        span(self, ow.animate.shift(RIGHT * 0.7), rt=0.3)
        span(self, ow.animate.shift(LEFT * 0.7), Create(xx), rt=0.35)
        pg = checkin_page(-1.0, 0.3, 1.3, 1.7, n=3, dot=1)
        dr = make_original("memory-drawers", height=1.8, x=1.05, y=-0.2)
        lq = L("quoted", 0.0, -1.85)
        at_word(self, "claim")
        span(self, FadeIn(pg, shift=UP * 0.2), FadeIn(pg.dot), FadeIn(dr, shift=UP * 0.2), FadeIn(lq), rt=0.5)
        q = ArcBetweenPoints(np.array([-0.3, 0.3, 0]), np.array([0.6, 0.55, 0]), angle=-PI / 3)
        q.set_stroke(INK, 5)
        at_word(self, "quote")
        span(self, Create(q), rt=0.5)
        g = gate(4.4, -0.25, 2.0)
        lg = L("bound to what was seen", 3.95, -1.85, 34)
        at_word(self, "approval")
        span(self, FadeIn(g), FadeIn(g.light), FadeIn(lg), rt=0.5)
        lock = VGroup(Rectangle(width=0.5, height=0.38, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([5.25, 0.85, 0]),
                      Arc(radius=0.17, start_angle=0, angle=PI, color=INK, stroke_width=6).move_to([5.25, 1.14, 0]))
        at_word(self, "changed")
        span(self, FadeIn(lock, shift=DOWN * 0.15), rt=0.4)
        done(self)


class B08_Loop(Scene):
    def construct(self):
        self.add(captions("C", 3))
        rc = np.array([-2.3, 0.3, 0])
        ring = Circle(radius=1.1, color=INK, stroke_width=6).move_to(rc)
        runner = Dot(rc + np.array([0, 1.1, 0]), radius=0.13, color=TERRA)
        ll = L("loop", -2.3, 1.95)
        at_word(self, "loop")
        span(self, Create(ring), FadeIn(runner), FadeIn(ll), rt=0.55)
        bs = make_original("budget-slots", height=1.7, x=2.6, y=0.35)
        lb = L("turn budget", 2.6, -1.0)
        at_word(self, "budget")
        span(self, FadeIn(bs, shift=UP * 0.2), FadeIn(lb), rt=0.5)
        at_word(self, "conversation")
        span(self, MoveAlongPath(runner, ring.copy().rotate(PI / 2, about_point=rc)),
             bs.parts["allocated-token"].animate.shift(bs.action_vectors["allocated-token"]), rt=1.0, rate_func=linear)
        bar = Line([-3.4, -1.25, 0], [-1.2, -1.25, 0], color=INK, stroke_width=8)
        ls = L("stop", -2.3, -1.8)
        at_word(self, "never")
        span(self, Create(bar), FadeIn(ls), rt=0.4)
        done(self)


class B09_Checker(Scene):
    def construct(self):
        self.add(captions("C", 3))
        base = Iso(-5.0, -0.1, 1.2).box(-0.4, -0.4, 0, 0.8, 0.8, 0.55)
        lh = L("Hugging Face", -5.0, 1.3, 36)
        lbm = L("base model", -5.0, -1.2, 36)
        at_word(self, "small")
        span(self, FadeIn(base, shift=DOWN * 0.2), FadeIn(lh), FadeIn(lbm), rt=0.5)
        a = arrow(-4.05, 0.05, -3.15, 0.05)
        ft = Iso(-2.2, -0.1, 1.2).box(-0.4, -0.4, 0, 0.8, 0.8, 0.55, DARK_TOP, DARK_L, DARK_R)
        lft = L("fine-tuned", -2.2, -1.2, 36)
        at_word(self, "fine")
        span(self, GrowArrow(a), FadeIn(ft, shift=DOWN * 0.2), FadeIn(lft), rt=0.5)
        rp = checkin_page(1.2, 0.25, 2.0, 2.5, n=4, dot=1)
        lr = L("raw transcript", 1.2, -1.55, 36)
        at_word(self, "raw")
        span(self, FadeIn(rp, shift=UP * 0.2), FadeIn(rp.dot), FadeIn(lr), rt=0.45)
        sl = Line([rp.x0 - 0.15, rp.ys[0] + 0.25, 0], [rp.x0 + rp.lw + 0.1, rp.ys[0] + 0.25, 0], color=TERRA, stroke_width=8)
        span(self, Create(sl), rt=0.25)
        span(self, sl.animate.move_to([float(np.array(sl.get_center())[0]), rp.ys[1] - 0.13, 0]), rt=0.7, rate_func=smooth)
        sp = checkin_page(4.6, 0.25, 1.7, 2.1, n=3, dot=None)
        xx = VGroup(Line([3.95, -0.5, 0], [5.25, 1.0, 0], color=INK, stroke_width=7),
                    Line([3.95, 1.0, 0], [5.25, -0.5, 0], color=INK, stroke_width=7))
        ln = L("not the summary", 4.6, -1.55, 36)
        at_word(self, "never")
        span(self, FadeIn(sp, shift=LEFT * 0.2), FadeIn(ln), rt=0.4)
        span(self, Create(xx), rt=0.35)
        done(self)


class B10_Data(Scene):
    def construct(self):
        self.add(captions("C", 3))
        top = L("synthetic data · fictional clients", 0, 1.95)
        at_word(self, "synthetic")
        span(self, FadeIn(top), rt=0.4)
        stack = VGroup(*[checkin_page(-4.3 + i * 0.18, 0.15 - i * 0.18, 1.8, 2.2, n=3, dot=None) for i in range(3)])
        lt = L("training · by Claude", -4.0, -1.65, 36)
        at_word(self, "training")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in stack], lag_ratio=0.25), FadeIn(lt), rt=0.6)
        ck = check(-2.85, -0.15, s=0.2)
        at_word(self, "spot")
        span(self, Create(ck), rt=0.35)
        v = make_original("secure-vault", height=2.0, x=3.7, y=0.15)
        lv = L("held-out · by me", 3.7, -1.65, 36)
        at_word(self, "held")
        span(self, FadeIn(v, shift=UP * 0.2), FadeIn(lv), rt=0.5)
        hp = VGroup(*[paper(0.4 + i * 0.5, 0.3, 0.7, 0.9) for i in range(2)])
        at_word(self, "myself")
        span(self, LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in hp], lag_ratio=0.3), rt=0.4)
        span(self, hp.animate.scale(0.5).move_to([3.4, 0.2, 0]), rt=0.6, rate_func=ease_in)
        span(self, FadeOut(hp), rt=0.2)
        at_word(self, "lock")
        span(self, v.parts["lock-bar"].animate.shift(v.action_vectors["lock-bar"]), rt=0.4)
        done(self)


def laptop(x, y, w=1.7):
    scr = Rectangle(width=w, height=w * 0.62, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + 0.35, 0])
    inner = Rectangle(width=w * 0.82, height=w * 0.45, fill_color=CARD, fill_opacity=1, stroke_width=0).move_to([x, y + 0.37, 0])
    base = Polygon([x - w * 0.62, y - 0.25, 0], [x + w * 0.62, y - 0.25, 0], [x + w * 0.5, y - 0.03, 0], [x - w * 0.5, y - 0.03, 0],
                   fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(scr, inner, base)


class B11_Resources(Scene):
    def construct(self):
        self.add(captions("C", 3))
        xs = (-4.4, 0.0, 4.4)
        pls = VGroup(*[plinth(x, -1.0, w=3.0) for x in xs])
        span(self, FadeIn(pls), rt=0.4)
        ws = make_original("agent-workstation", height=1.6, x=xs[0], y=0.1)
        l1 = L("existing account", xs[0], -1.75, 36)
        at_word(self, "existing")
        span(self, FadeIn(ws, shift=DOWN * 0.2), FadeIn(l1), rt=0.45)
        c1 = check(xs[0] + 1.2, 1.15, s=0.18)
        at_word(self, "credits")
        span(self, Create(c1), rt=0.3)
        bx = Iso(xs[1], -0.55, 1.0).box(-0.4, -0.4, 0, 0.8, 0.8, 0.5)
        dn = arrow(xs[1], 1.4, xs[1], 0.45)
        l2 = L("free download", xs[1], -1.75, 36)
        at_word(self, "base")
        span(self, FadeIn(bx, shift=DOWN * 0.2), GrowArrow(dn), FadeIn(l2), rt=0.5)
        c2 = check(xs[1] + 1.2, 1.15, s=0.18)
        at_word(self, "account", nth=2)
        span(self, Create(c2), rt=0.3)
        lp = laptop(xs[2], 0.0)
        l3 = L("my laptop", xs[2], -1.75, 36)
        c3 = check(xs[2] + 1.2, 1.15, s=0.18)
        at_word(self, "laptop")
        span(self, FadeIn(lp, shift=DOWN * 0.2), FadeIn(l3), Create(c3), rt=0.5)
        st = L("Python · PyTorch · SQLite", 0, 2.0)
        at_word(self, "Python")
        span(self, FadeIn(st), rt=0.4)
        done(self)


class B12_Steps(Scene):
    def construct(self):
        self.add(captions("C", 3))
        ty = -0.2
        thread = Line([-5.4, ty, 0], [4.3, ty, 0], color=INK, stroke_width=5)
        span(self, Create(thread), rt=0.6)
        xs = (-4.6, -2.7, -0.8, 1.1, 3.0)
        labels = ("contract + tests", "test set", "training data", "checker", "loop + memory")
        cues = (("contract", 1), ("test", 2), ("training", 1), ("checker", 1), ("loop", 1))
        for i, (x, lab, (w, n)) in enumerate(zip(xs, labels, cues)):
            d = Dot([x, ty, 0], radius=0.14, color=TERRA if i == 0 else INK)
            num = L(str(i + 1), x, ty + 0.5, 40) if i % 2 else L(str(i + 1), x, ty - 0.5, 40)
            lb = L(lab, x, ty + 1.15, 36) if i % 2 == 0 else L(lab, x, ty - 1.15, 36)
            at_word(self, w, nth=n)
            span(self, GrowFromCenter(d), FadeIn(num), FadeIn(lb), rt=0.35)
        v = make_original("secure-vault", height=1.6, x=5.3, y=0.15)
        lv = L("held-out run · Dec 20", 4.0, -1.95, 36)
        at_word(self, "held")
        span(self, FadeIn(v, shift=UP * 0.2), FadeIn(lv), rt=0.5)
        done(self)


# ── Part 4 · Evaluation ──

class B13_EvalChecker(Scene):
    def construct(self):
        self.add(captions("C", 4))
        xs = (-5.0, -2.6, -0.2)
        names = ("keywords", "untrained", "fine-tuned")
        bars = VGroup(*[DashedVMobject(Rectangle(width=1.0, height=2.2, color=INK, stroke_width=4), num_dashes=22).move_to([x, 0.3, 0]) for x in xs])
        qs = VGroup(*[T("?", 64).move_to([x, 0.3, 0]) for x in xs])
        lbs = VGroup(*[L(n, x, -1.2, 36) for n, x in zip(names, xs)])
        at_word(self, "compare")
        span(self, LaggedStart(*[Create(b) for b in bars], lag_ratio=0.25), FadeIn(lbs), rt=0.7)
        span(self, FadeIn(qs), rt=0.3)
        env = envelope(3.6, 0.45, w=1.6, h=1.05)
        le = L("pass mark, sealed first", 3.6, -1.2, 36)
        at_word(self, "pass")
        span(self, FadeIn(env, shift=DOWN * 0.2), FadeIn(le), rt=0.45)
        thr = DashedLine([-5.8, 0.75, 0], [0.6, 0.75, 0], color=TERRA, stroke_width=6, dash_length=0.2)
        at_word(self, "beat")
        span(self, Create(thr), rt=0.5)
        done(self)


class B14_Failures(Scene):
    def construct(self):
        self.add(captions("C", 4))
        xs = (-5.0, -2.5, 0.0, 2.5, 5.0)
        lf = L("5 failure cases, on purpose", 0, 1.95)
        at_word(self, "five")
        span(self, FadeIn(lf), rt=0.4)
        for x, w in zip(xs, ("spill", "legs", "didn", "neighb", "asleep")):
            c = checkin_page(x, 0.0, 1.7, 2.0, n=3, dot=1)
            at_word(self, w)
            span(self, FadeIn(c, shift=DOWN * 0.25), FadeIn(c.dot), rt=0.3)
        done(self)


OP_X, OP_Y, OP_W, OP_H = -3.7, -0.1, 3.0, 3.4
SP_X, SP_Y = 0.75, 0.15


class B15_Controlled(Scene):
    def construct(self):
        self.add(captions("C", 4))
        p = checkin_page(OP_X, OP_Y, OP_W, OP_H, n=5, dot=2)
        head = L("check-in", OP_X, OP_Y + OP_H / 2 + 0.42)
        at_word(self, "controlled")
        span(self, FadeIn(p, shift=UP * 0.2), FadeIn(p.dot), FadeIn(head), rt=0.5)
        s = summary_page(SP_X, SP_Y)
        sh, sm = L("summary", SP_X, SP_Y + 1.72), L("forced to drop it", SP_X, SP_Y - 1.75, 36)
        at_word(self, "force")
        span(self, FadeIn(s, shift=LEFT * 0.4), FadeIn(sh), FadeIn(sm), rt=0.55)
        at_word(self, "drops")
        span(self, Indicate(s.gap, color=INK, scale_factor=1.0), rt=0.4)
        sl = Line([p.x0 - 0.15, p.ys[0] + 0.3, 0], [p.x0 + p.lw + 0.1, p.ys[0] + 0.3, 0], color=TERRA, stroke_width=8)
        at_word(self, "separate")
        span(self, Create(sl), rt=0.3)
        span(self, sl.animate.move_to([float(np.array(sl.get_center())[0]), p.ys[2] - 0.13, 0]), rt=0.8, rate_func=smooth)
        q = make_original("task-queue", height=2.0, x=4.7, y=-0.25)
        lq = L("review", 4.7, -1.85)
        at_word(self, "coordinator")
        span(self, FadeIn(q, shift=UP * 0.2), FadeIn(lq), rt=0.45)
        ri = slip(OP_X + 0.3, p.ys[2], 1.5, 0.7)
        span(self, FadeIn(ri, scale=1.1), rt=0.25)
        span(self, MoveAlongPath(ri, ArcBetweenPoints(np.array([OP_X + 0.3, p.ys[2], 0]), np.array([4.15, 0.45, 0]), angle=-PI / 3.5)),
             rt=0.9, rate_func=smooth)
        done(self)


class B16_Limits(Scene):
    def construct(self):
        self.add(captions("C", 4))
        fence = DashedLine([-5.8, -1.5, 0], [5.8, -1.5, 0], color=INK, stroke_width=4, dash_length=0.3)
        lf = L("synthetic only · not real care", 0, -2.05, 36)
        at_word(self, "real")
        span(self, Create(fence), FadeIn(lf), rt=0.5)
        op = checkin_page(-2.8, 0.35, 2.2, 2.6, n=4, dot=1)
        lo = L("original words", -2.8, 2.0)
        cl = slip(2.6, op.ys[1], 2.4, 0.85)
        lc = L("claim", 2.6, 2.0)
        at_word(self, "meaning")
        span(self, FadeIn(op, shift=UP * 0.2), FadeIn(op.dot), FadeIn(lo), rt=0.45)
        # GATE T reads a lined slip as stacked labels at the clip midpoint (as in the October B03): bring the
        # claim slip in only after the midpoint window
        link = Line([op.x0 + op.lw + 0.35, op.ys[1], 0], [1.3, op.ys[1], 0], color=INK, stroke_width=5)
        at_word(self, "next")
        at(self, max(_elapsed(self), _target(self) / 2 + MID_GUARD + 0.05))
        span(self, FadeIn(cl, shift=LEFT * 0.2), FadeIn(lc), rt=0.4)
        span(self, Create(link), rt=0.45)
        done(self)


class BOUT_Outro(Scene):
    def construct(self):
        self.add(captions())
        title = T("DayThread", 110).move_to([0, 1.0, 0])
        name = L("Aditya Raj", 0, -0.2, 52)
        gh = L("github.com/aditya-raj-sde", 0, -1.0, 40)
        span(self, FadeIn(title, shift=UP * 0.2), rt=0.45)
        at_word(self, "Aditya") if any(_norm(w).startswith("aditya") for w, _ in _WORDS.get("BOUT", [])) else at(self, 1.6)
        span(self, FadeIn(name, shift=UP * 0.15), FadeIn(gh, shift=UP * 0.15), rt=0.45)
        th = Line([-3.0, -1.75, 0], [3.0, -1.75, 0], color=INK, stroke_width=5)
        span(self, Create(th), rt=0.5)
        span(self, GrowFromCenter(Dot([3.0, -1.75, 0], radius=0.1, color=TERRA)), rt=0.3)
        done(self)
