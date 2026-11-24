

# ═════════════════════════════ cite-the-line-project-film — scenes ═════════════════════════════
# Build:  cat <toolkit>/skills/make/show-tell/templates/iso_kit.py scenes_body.py > scenes.py
# (show-tell: paste the kit at the top of scenes.py; never import it.)
#
# Timing rule used in every scene (GATE T and Gate V sample each clip at its MIDPOINT):
#   phase A — every arrival, label and move finishes by 36% of the beat;
#   hold    — nothing moves between 36% and 62%;
#   phase B — from 62%, one more NEW shape lands (Gate A needs a new shape after frame 1).
# Every body beat carries the on-screen "constructed sketch" tag: nothing shown is built yet.

A_END, B_START = 0.36, 0.62


def dur(self):
    """Measured audio for this beat; 6 s when the sheet isn't beside scenes.py (Gate A's sandbox)."""
    return _TARGET.get(type(self).__name__.split("_")[0], 0) or 6.0


def at(self, frac):
    gap = frac * dur(self) - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def tag():
    return T("constructed sketch", 32).move_to([4.6, -2.95, 0])


def lab(s, x, y, size=36):
    return T(s, size).move_to([x, y, 0])


def logpage(x, y, w=2.4, h=3.0, rows=6, lengths=(0.85, 0.6, 0.95, 0.7, 0.9, 0.5)):
    """A page of log lines: white sheet, kraft shadow, grey line bars. `.rowy` = each bar's y."""
    pg = paper(x, y, w, h)
    bars, rowy = VGroup(), []
    for i in range(rows):
        yy = y + h / 2 - 0.45 - i * (h - 0.8) / max(1, rows - 1)
        x0 = x - w / 2 + 0.45
        bars.add(Line([x0, yy, 0], [x0 + (w - 0.8) * lengths[i % len(lengths)], yy, 0], color=GHOST, stroke_width=9))
        rowy.append(yy)
    g = VGroup(pg, bars)
    g.rowy, g.x0 = rowy, x - w / 2
    return g


def slip(x, y, w=1.7, h=1.0, dots=2):
    """The result slip: card, one grey cause pill, terracotta line-number dots."""
    card = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    bar = RoundedRectangle(width=w * 0.55, height=0.22, corner_radius=0.11, fill_color=BAR2, fill_opacity=1,
                           stroke_width=0).move_to([x - w * 0.12, y + h * 0.17, 0])
    ds = VGroup(*[Dot([x - w * 0.32 + i * 0.32, y - h * 0.22, 0], radius=0.07, color=TERRA) for i in range(dots)])
    return VGroup(card, bar, ds)


def cross(x, y, s=0.32, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def lens(x, y, r=0.55):
    ring = Circle(radius=r, stroke_color=INK, stroke_width=8, fill_opacity=0).move_to([x, y, 0])
    handle = Line([x + r * 0.7, y - r * 0.7, 0], [x + r * 1.5, y - r * 1.5, 0], color=INK, stroke_width=10)
    return VGroup(ring, handle)


def cylinder(x, y, w=1.6, h=1.4, top=BOX_TOP, body=BOX_R):
    e = 0.36
    bottom = Ellipse(width=w, height=e, fill_color=body, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y - h / 2, 0])
    side = Rectangle(width=w, height=h, fill_color=body, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    edges = VGroup(Line([x - w / 2, y - h / 2, 0], [x - w / 2, y + h / 2, 0], color=INK, stroke_width=4),
                   Line([x + w / 2, y - h / 2, 0], [x + w / 2, y + h / 2, 0], color=INK, stroke_width=4))
    lid = Ellipse(width=w, height=e, fill_color=top, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + h / 2, 0])
    return VGroup(bottom, side, edges, lid)


def floor_shadow(x, y, w=2.6):
    return Ellipse(width=w, height=0.32, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


def dashed_rect(x, y, w, h, n=6, color=DIM, sw=5):
    """A dashed outline from short lines (no DashedVMobject, to stay inside Gate A's stub)."""
    g = VGroup()
    corners = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
    for k in range(4):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % 4]
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            g.add(Line([ax + (bx - ax) * t0, ay + (by - ay) * t0, 0], [ax + (bx - ax) * t1, ay + (by - ay) * t1, 0],
                       color=color, stroke_width=sw))
    return g



KRAFT = "#9C8462"   # connectors: deep kraft, never ink (ink connectors fuse objects into one "text" blob)


def connector(a, b, sw=6):
    return Line([a[0], a[1], 0], [b[0], b[1], 0], color=KRAFT, stroke_width=sw)


def padlock(x, y, s=0.5):
    body = RoundedRectangle(width=s * 1.5, height=s * 1.15, corner_radius=0.08, fill_color=DARK_TOP, fill_opacity=1,
                            stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    shackle = Arc(radius=s * 0.48, start_angle=0, angle=PI, color=INK, stroke_width=9).move_arc_center_to([x, y + s * 0.57, 0])
    return VGroup(shackle, body)


def scorecard(x, y, w=1.9, h=1.5):
    card = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    head = Rectangle(width=w, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x, y + h / 2 - 0.15, 0])
    rows = VGroup(*[RoundedRectangle(width=w * (0.7 - 0.15 * i), height=0.18, corner_radius=0.09, fill_color=BAR2,
                                     fill_opacity=1, stroke_width=0).move_to([x - w * 0.12 + 0.0, y + 0.15 - i * 0.38, 0])
                    for i in range(3)])
    return VGroup(card, head, rows)


def octagon(x, y, r=1.0):
    pts = [[x + r * np.cos(PI / 8 + k * PI / 4), y + r * np.sin(PI / 8 + k * PI / 4), 0] for k in range(8)]
    return Polygon(*pts, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=7)


def restart_button(x, y, r=0.9):
    btn = Circle(radius=r, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([x, y, 0])
    arc = Arc(radius=r * 0.55, start_angle=PI * 0.6, angle=PI * 1.6, color=INK, stroke_width=9).move_arc_center_to([x, y, 0])
    t = np.array([x + r * 0.55 * np.cos(PI * 0.6), y + r * 0.55 * np.sin(PI * 0.6), 0])
    tip = Polygon(t + [0.0, 0.2, 0], t + [0.0, -0.2, 0], t + [-0.28, 0.0, 0], fill_color=INK, fill_opacity=1, stroke_width=0)
    return VGroup(btn, arc, tip)


def tray(cx, cy, w=1.8, d=1.8, h=0.7):
    iso = Iso(cx, cy, 1.0)
    back, front = iso.open_box(0, 0, 0, w, d, h)
    return iso, back, front


# ═══ 1. EXECUTIVE SUMMARY ═══════════════════════════════════════════════════

class B00_PasteHabit(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pg = logpage(-4.2, 0.4, w=1.9, h=2.4, rows=4)
        self.play(FadeIn(pg, shift=DOWN * 0.4), run_time=0.08 * d)
        bubble = RoundedRectangle(width=2.4, height=1.5, corner_radius=0.3, fill_color=CARD, fill_opacity=1,
                                  stroke_color=INK, stroke_width=5).move_to([0, 0.7, 0])
        rows = VGroup(*[RoundedRectangle(width=w, height=0.18, corner_radius=0.09, fill_color=BAR2, fill_opacity=1,
                                         stroke_width=0).move_to([-0.15, 1.0 - i * 0.4, 0]) for i, w in enumerate((1.6, 1.2, 1.4))])
        self.play(Create(connector((-3.1, 0.5), (-1.35, 0.6))), FadeIn(bubble), FadeIn(rows),
                  FadeIn(lab("chatbot", 0, -0.55)), run_time=0.12 * d)
        fix = slip(4.2, 0.5)
        self.play(Create(connector((1.35, 0.6), (3.25, 0.5))), FadeIn(fix, shift=RIGHT * 0.3), run_time=0.1 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(4.25, -0.2, w=2.0)), run_time=0.12 * d)
        finish(self)


class B01_LensCites(Scene):
    def construct(self):
        d = dur(self)
        pg = logpage(-2.6, 0.3)
        self.add(tag(), pg)
        ln = lens(-4.9, 1.9)
        self.play(FadeIn(ln), run_time=0.06 * d)
        self.play(ln.animate.move_to([-2.2, pg.rowy[2] - 0.15, 0]), run_time=0.1 * d)
        hits = VGroup(*[Dot([pg.x0 + 0.22, pg.rowy[i], 0], radius=0.08, color=TERRA) for i in (2, 4)])
        self.play(LaggedStart(*[GrowFromCenter(h) for h in hits], lag_ratio=0.4), run_time=0.07 * d)
        s = slip(2.7, 0.5)
        self.play(FadeIn(s, shift=LEFT * 0.4), FadeIn(lab("cause", 2.7, -0.55)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(check(4.1, 0.55)), run_time=0.12 * d)
        finish(self)


class B02_HandOff(Scene):
    def construct(self):
        d = dur(self)
        pg = logpage(-3.6, 0.3, rows=3, lengths=(0.4, 0.3, 0.35))
        self.add(tag(), pg)
        ln = lens(-3.3, 1.3)
        self.play(FadeIn(ln), run_time=0.05 * d)
        self.play(ln.animate.move_to([-3.3, -0.3, 0]), run_time=0.1 * d)
        empty = Rectangle(width=1.6, height=1.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([0.4, 0.6, 0])
        self.play(FadeIn(empty, shift=LEFT * 0.3), FadeIn(lab("not enough", 0.4, -0.45)), run_time=0.08 * d)
        iso, back, front = tray(3.9, -1.2)
        self.play(Create(connector((1.25, 0.6), (2.75, 0.5))), FadeIn(back), FadeIn(front),
                  FadeIn(lab("engineer", 3.9, -1.9)), run_time=0.1 * d)
        at(self, B_START)
        note = iso.page(0.45, 0.45, 0.05, w=0.9, d=1.0)
        note.set_z_index(1)
        self.play(FadeIn(note, shift=DOWN * 0.2), run_time=0.12 * d)
        finish(self)


class B03_CheckedVsNot(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        lone = slip(-3.8, 0.9)
        self.play(FadeIn(lone), FadeIn(lab("unchecked", -3.8, -1.3)), run_time=0.08 * d)
        self.play(Create(cross(-3.8, -0.35, s=0.3)), run_time=0.06 * d)
        pg = logpage(1.6, 0.3, w=2.0, h=2.6, rows=4)
        hits = VGroup(*[Dot([pg.x0 + 0.22, pg.rowy[i], 0], radius=0.08, color=TERRA) for i in (1, 3)])
        self.play(FadeIn(pg), GrowFromCenter(hits[0]), GrowFromCenter(hits[1]), run_time=0.08 * d)
        s = slip(4.6, 0.9, w=1.4, h=0.8)
        links = VGroup(*[connector((3.85, 0.9), (2.75, pg.rowy[i])) for i in (1, 3)])
        self.play(FadeIn(s), Create(links), FadeIn(lab("checked", 3.2, -1.6)), run_time=0.08 * d)
        self.play(Create(check(4.6, -0.1)), run_time=0.04 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.75, 0.25, w=1.9)), run_time=0.12 * d)
        finish(self)


# ═══ 2. INTRODUCTION ════════════════════════════════════════════════════════

class B04_Rcacopilot(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.4, -1.0, 1.0)
        box = iso.box(0, 0, 0, 1.7, 1.7, 1.2)
        self.play(FadeIn(box, shift=DOWN * 0.3), run_time=0.08 * d)
        lp = iso.p(0, 0.85, 0.6)
        self.play(FadeIn(padlock(lp[0], lp[1] - 0.05, s=0.42)), run_time=0.06 * d)
        self.play(FadeIn(T("up to 77%", 96).move_to([2.2, 0.6, 0])), run_time=0.1 * d)
        self.play(FadeIn(lab("per Microsoft Research", 2.2, -0.5, size=32)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.4, -1.15, w=3.2)), run_time=0.12 * d)
        finish(self)


class B05_Datadog(Scene):
    def construct(self):
        d = dur(self)
        iso = Iso(-0.6, -1.5, 1.0)
        plinth = iso.box(-0.2, -0.2, -0.3, 2.9, 2.9, 0.3, DARK_TOP, DARK_L, DARK_R)
        box = iso.box(0, 0, 0, 2.5, 2.5, 1.6)
        self.add(tag())
        self.play(FadeIn(plinth), FadeIn(box), FadeIn(lab("vendor platform", -0.6, -2.45)), run_time=0.09 * d)
        pg = logpage(-5.0, 0.6, w=1.2, h=1.5, rows=3)
        self.play(FadeIn(pg), run_time=0.05 * d)
        self.play(pg.animate.move_to([-3.6, 0.4, 0]), run_time=0.07 * d)
        self.play(FadeOut(pg), run_time=0.04 * d)
        self.play(FadeIn(scorecard(3.6, 0.6, w=1.7, h=1.3), shift=RIGHT * 0.4), run_time=0.08 * d)
        at(self, B_START)
        self.play(GrowFromCenter(Dot(iso.p(0.0, 1.25, 0.8), radius=0.1, color=TERRA)), run_time=0.12 * d)
        finish(self)


class B06_LockedVsOpen(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.8, -1.6, 1.0)
        locked = iso.box(0, 0, 0, 1.1, 1.1, 0.8)
        lp = iso.p(0, 0.55, 0.4)
        self.play(FadeIn(scorecard(-3.8, 1.25, w=1.8, h=1.3)), FadeIn(locked),
                  FadeIn(padlock(lp[0], lp[1], s=0.3)), FadeIn(lab("can't re-check", -3.8, -2.3)), run_time=0.12 * d)
        right = scorecard(2.6, 1.25, w=1.8, h=1.3)
        pages = VGroup(*[logpage(x, -0.9, w=0.9, h=1.1, rows=2) for x in (1.5, 2.6, 3.7)])
        links = VGroup(*[connector((2.6, 0.55), (x, -0.27)) for x in (1.5, 2.6, 3.7)])
        self.play(FadeIn(right), run_time=0.06 * d)
        self.play(Create(links), LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in pages], lag_ratio=0.25),
                  FadeIn(lab("anyone can re-check", 2.6, -2.1)), run_time=0.12 * d)
        at(self, B_START)
        self.play(Create(check(4.3, 1.25)), run_time=0.12 * d)
        finish(self)


# ═══ 3. METHODS ═════════════════════════════════════════════════════════════

class B07_Service(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        iso = Iso(-3.0, -1.2, 1.0)
        stack, lights = iso.server(0, 0, 0, w=1.6, d=1.6, slab=0.5, n=3)
        self.play(FadeIn(stack), FadeIn(lights), FadeIn(lab("FastAPI", -3.0, -1.9)), run_time=0.1 * d)
        db = cylinder(2.8, 0.2, w=1.9, h=1.7)
        self.play(Create(connector((-1.4, 0.3), (1.75, 0.3))), FadeIn(db), FadeIn(lab("Postgres", 2.8, -1.6)),
                  run_time=0.12 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.0, -1.35, w=3.0)), FadeIn(floor_shadow(2.85, -1.0, w=2.3)), run_time=0.12 * d)
        finish(self)


class B08_BreakService(Scene):
    def construct(self):
        d = dur(self)
        iso = Iso(-3.0, -1.3, 1.0)
        stack, lights = iso.server(0, 0, 0, w=1.6, d=1.6, slab=0.5, n=3)
        self.add(tag())
        self.play(FadeIn(stack), FadeIn(lights), FadeIn(lab("service", -3.0, -2.0)), run_time=0.08 * d)
        xs = (0.4, 2.2, 4.0)
        for i in range(3):
            page = logpage(xs[i], 0.4, w=1.3, h=1.7, rows=3)
            cause = Dot([xs[i] + 0.45, -0.25, 0], radius=0.08, color=TERRA)
            self.play(lights[i].animate.set_color(TERRA), FadeIn(page, shift=DOWN * 0.4), run_time=0.07 * d)
            self.play(GrowFromCenter(cause), run_time=0.02 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(-3.0, -1.45, w=3.0)), run_time=0.12 * d)
        finish(self)


class B09_Loop(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        ring = Circle(radius=1.9, stroke_color=KRAFT, stroke_width=6).move_to([-0.6, 0.1, 0])
        self.play(Create(ring), run_time=0.06 * d)
        top = logpage(-0.6, 2.05, w=1.0, h=1.2, rows=2)
        brain = Iso(1.3, -0.35, 1.0).box(0, 0, 0, 0.6, 0.6, 0.5)
        chk = slip(-0.6, -1.8, w=1.1, h=0.7, dots=0)
        rec = slip(-2.5, 0.1, w=1.0, h=0.65)
        self.play(FadeIn(top), FadeIn(brain), FadeIn(chk), FadeIn(rec),
                  FadeIn(lab("Claude Code", 3.4, 0.2)), FadeIn(lab("checker", -0.6, -2.6)), run_time=0.1 * d)
        dot = Dot(ring.point_from_proportion(0.25), radius=0.11, color=TERRA)
        self.play(FadeIn(dot), run_time=0.02 * d)
        self.play(MoveAlongPath(dot, ring), run_time=0.16 * d, rate_func=linear)
        at(self, B_START)
        self.play(FadeIn(slip(-3.75, 0.1, w=1.0, h=0.65), shift=LEFT * 0.2), run_time=0.12 * d)
        finish(self)


class B10_ReadOnly(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pg = logpage(-3.2, 0.4, w=2.2, h=2.6, rows=4)
        self.play(FadeIn(pg), FadeIn(lab("read", -3.2, -1.5)), run_time=0.08 * d)
        self.play(FadeIn(lens(-2.9, 0.6)), run_time=0.06 * d)
        self.play(FadeIn(restart_button(2.8, 0.5)), FadeIn(lab("restart", 2.8, -0.9)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(cross(2.8, 0.5, s=0.75, w=12)), run_time=0.12 * d)
        finish(self)


class B11_StopRules(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        runs = VGroup(*[slip(x, 0.9, w=1.4, h=0.8) for x in (-4.4, -2.6, -0.8)])
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in runs], lag_ratio=0.3),
                  FadeIn(lab("3 runs", -2.6, -0.2)), run_time=0.14 * d)
        self.play(FadeIn(octagon(3.0, 0.7)), FadeIn(lab("stop", 3.0, -0.8)), run_time=0.1 * d)
        at(self, B_START)
        self.play(GrowFromCenter(Dot([3.0, 0.7, 0], radius=0.13, color=TERRA)), run_time=0.12 * d)
        finish(self)


class B12_HumanGate(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        empty = Rectangle(width=1.5, height=0.9, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-4.0, 1.2, 0])
        bad = VGroup(slip(-4.0, -0.4, w=1.5, h=0.9), cross(-2.85, -0.4, s=0.22))
        self.play(FadeIn(empty), FadeIn(bad), run_time=0.08 * d)
        iso, back, front = tray(2.6, -1.1, w=2.0, d=2.0, h=0.8)
        self.play(FadeIn(back), FadeIn(front), FadeIn(lab("engineer", 2.6, -1.8)), run_time=0.08 * d)
        empty.set_z_index(1); bad.set_z_index(1)
        self.play(empty.animate.scale(0.45).move_to(iso.p(1.4, 0.6, 0.3)), run_time=0.08 * d)
        self.play(bad.animate.scale(0.45).move_to(iso.p(0.6, 1.4, 0.3)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(2.6, -1.25, w=3.6)), run_time=0.12 * d)
        finish(self)


class B13_Resources(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        screen = Rectangle(width=2.6, height=1.6, fill_color=BAR1, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-2.8, 0.8, 0])
        base = Polygon([-4.3, -0.05, 0], [-1.3, -0.05, 0], [-1.0, -0.4, 0], [-4.6, -0.4, 0],
                       fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4)
        self.play(FadeIn(screen), FadeIn(base), FadeIn(lab("laptop", -2.8, -1.0)), run_time=0.12 * d)
        card = RoundedRectangle(width=2.6, height=1.6, corner_radius=0.15, fill_color=CARD, fill_opacity=1,
                                stroke_color=INK, stroke_width=5).move_to([2.6, 0.6, 0])
        stripe = Rectangle(width=2.2, height=0.3, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([2.6, 0.95, 0])
        spark = Dot([1.7, 0.2, 0], radius=0.09, color=TERRA)
        self.play(FadeIn(card), FadeIn(stripe), FadeIn(spark), FadeIn(lab("Claude Code seat", 2.6, -0.65)), run_time=0.12 * d)
        at(self, B_START)
        self.play(Create(check(-1.0, 1.9)), Create(check(4.3, 1.7)), run_time=0.12 * d)
        finish(self)


# ═══ 4. EVALUATION ══════════════════════════════════════════════════════════

class B14_TenIncidents(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        pages = VGroup()
        for y in (1.4, -0.3):
            for x in (-4.2, -2.1, 0.0, 2.1, 4.2):
                pg = logpage(x, y, w=1.0, h=1.2, rows=2)
                pages.add(VGroup(pg, Dot([x + 0.3, y - 0.35, 0], radius=0.07, color=TERRA)))
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in pages], lag_ratio=0.12), run_time=0.22 * d)
        self.play(FadeIn(lab("known causes", 0, -1.6)), run_time=0.08 * d)
        at(self, B_START)
        self.play(FadeIn(floor_shadow(0, -1.05, w=10.0)), run_time=0.12 * d)
        finish(self)


class B15_ThreeChecks(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        cols = VGroup(slip(-3.8, 1.0, w=1.6, h=0.95), slip(0.0, 1.0, w=1.6, h=0.95, dots=0),
                      Rectangle(width=1.6, height=0.95, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                stroke_width=4).move_to([3.8, 1.0, 0]))
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cols], lag_ratio=0.3), run_time=0.14 * d)
        self.play(FadeIn(lab("lines exist", -3.8, -1.0)), FadeIn(lab("cause matches", 0.0, -1.0)), run_time=0.1 * d)
        at(self, B_START)
        self.play(LaggedStart(*[Create(check(x - 0.1, -0.15)) for x in (-3.8, 0.0, 3.8)], lag_ratio=0.3), run_time=0.14 * d)
        finish(self)


class B16_Baseline(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        frames = VGroup(*[Rectangle(width=1.5, height=2.6, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                    stroke_width=5).move_to([x, 0.6, 0]) for x in (-1.8, 1.8)])
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.2) for f in frames], lag_ratio=0.3), run_time=0.12 * d)
        self.play(FadeIn(lab("keyword script", -1.8, -1.35)), FadeIn(lab("Claude", 1.8, -1.35)), run_time=0.1 * d)
        at(self, B_START)
        self.play(Create(Line([-3.3, -0.82, 0], [3.3, -0.82, 0], color=GHOST, stroke_width=6)), run_time=0.12 * d)
        finish(self)


class B17_ExistsVsWill(Scene):
    def construct(self):
        d = dur(self)
        self.add(tag())
        small = Iso(-3.8, -0.9, 1.0).box(0, 0, 0, 0.7, 0.7, 0.5, DARK_TOP, DARK_L, DARK_R)
        self.play(FadeIn(small, shift=DOWN * 0.3), FadeIn(lab("exists", -3.8, -1.6)), run_time=0.12 * d)
        big = Iso(1.6, -1.7, 1.0)
        outline = VGroup(*[big.box(x, y, 0, 1.0, 1.0, 0.8, STAGE, STAGE, STAGE) for x, y in ((1.05, 1.05), (1.05, 0), (0, 1.05), (0, 0))])
        self.play(LaggedStart(*[Create(g) for g in outline], lag_ratio=0.2), FadeIn(lab("will exist", 1.6, -2.5)), run_time=0.16 * d)
        at(self, B_START)
        self.play(Create(big.box(0.5, 0.5, 0.85, 1.0, 1.0, 0.8, STAGE, STAGE, STAGE)), run_time=0.12 * d)
        finish(self)
