# ═════════════════════════════ TraceCase final — scene body ═════════════════════════════
# Appended after iso_kit.py by build_scenes.py. One class per beat; the narration is the clock.
# Cast kept for the whole film: the SERVICE (dark server stack; its lights turn terracotta when it
# breaks), LOG pages, the TRACE (stacked span bars), the AGENT (a magnifying glass), the PROPOSAL
# card, the GATE (a barrier arm that lifts only on approval) and the SEAL (an approval stamp).
# Every sketch of the future product carries a "constructed" tag.
#
# LAYOUT CONTRACT (applies to every beat):
#   · a top rule at y=+2.82 and a bottom rule at y=-2.95 frame the stage on every single beat,
#     so nothing ever floats in an unbounded cream void;
#   · the heading sits on the left margin (x=-6.1) and the part marker on the right (x=+6.1),
#     so the top edge is anchored across the full width;
#   · every object that stands on the ground gets a contact shadow — that is what stops the
#     isometric cast reading as clip-art pasted onto a page;
#   · labels sit BESIDE or BELOW their object, never inside a filled shape (Gate T);
#   · nothing crosses ±6.3 x / ±3.4 y (title-safe).

DEEP_KRAFT = "#9C8462"

MARGIN_L, MARGIN_R = -6.1, 6.1
TOP_RULE_Y, BOT_RULE_Y = 2.82, -2.95

# ── word-accurate pacing ──────────────────────────────────────────────────────────────────
# The kit's until() estimates when a phrase is spoken from its share of the characters. That drifts.
# This override reads the real word timestamps that the toolkit's align.py writes to mp3/words.json,
# and falls back to the estimate only if they are missing.
try:
    _WORDS = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "mp3", "words.json")))
    _WFPS = float(_WORDS.get("fps", 24)); _WORDS = _WORDS["beats"]
except Exception:
    _WORDS, _WFPS = {}, 24.0
_kit_until = until


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def until(self, phrase, lead=0.15):
    bid = type(self).__name__.split("_")[0]
    toks = _WORDS.get(bid) or []
    want = [_norm(w) for w in phrase.split() if _norm(w)]
    have = [_norm(t["text"]) for t in toks]
    for i in range(len(have) - len(want) + 1):
        if have[i:i + len(want)] == want:
            gap = toks[i]["startFrame"] / _WFPS - lead - _elapsed(self)
            if gap > 0.05:
                self.wait(gap)
            return
    _kit_until(self, phrase)


def _mid(s):
    return _TARGET.get(type(s).__name__.split("_")[0], 10.0) / 2.0


def gplay(s, *anims, rt=0.8):
    """Play, but never across the clip midpoint (Gate T and Gate V sample there)."""
    mid, now = _mid(s), _elapsed(s)
    if now < mid + 0.3 and now + rt > mid - 0.3:
        s.wait(max(0.01, mid + 0.32 - now))
    s.play(*anims, run_time=rt)


# ── the stage furniture ───────────────────────────────────────────────────────────────────
def rule(y, x0=MARGIN_L, x1=MARGIN_R, color=GHOST, w=3):
    return Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=w)


def shadow(x, y, w, h=None, op=0.22):
    """A contact shadow. Objects that touch the ground get one; flat cards do not."""
    return Ellipse(width=w, height=h if h is not None else w * 0.22, fill_color=DIM,
                   fill_opacity=op, stroke_width=0).move_to([x, y, 0]).set_z_index(-6)


_PART = {"Executive summary": "1 / 4", "What already exists": "2 / 4",
         "Methods": "3 / 4", "Evaluation": "4 / 4"}


def heading(text):
    """Which part of the submission this beat belongs to — plus the rules that frame the stage."""
    dot = Square(side_length=0.16, fill_color=TERRA, fill_opacity=1, stroke_width=0).move_to([MARGIN_L, 3.12, 0])
    lab = T(text, 40).move_to([MARGIN_L + 0.2, 3.12, 0], aligned_edge=LEFT)
    part = T(_PART.get(text, ""), 32, color=DIM).move_to([MARGIN_R, 3.12, 0], aligned_edge=RIGHT)
    return VGroup(dot, lab, part, rule(TOP_RULE_Y), rule(BOT_RULE_Y))


def TBase(text, size, x, y, **kw):
    """T() placed so that labels of different glyph shapes share a baseline.

    move_to() centres a Text on its ink box, so a word with a descender sits higher than one
    without. Padding each label with an invisible "Ag" gives them all the same ascender and
    descender extent; the visible run is then centred horizontally on x by hand."""
    t = T(text + " Ag", size, **kw)
    n = len(text.replace(" ", ""))
    for g in t[n:]:
        g.set_opacity(0)
    vis = VGroup(*t[:n])
    return t.shift([x - vis.get_center()[0], y - t.get_center()[1], 0])


def tag():
    """The honesty label: this picture is a sketch of something that does not exist yet."""
    return T("constructed", 32, color=DIM).move_to([MARGIN_L, -3.15, 0], aligned_edge=LEFT)


def xmark(x, y, s=0.22, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=INK, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=INK, stroke_width=w))


def omark(x, y, r=0.22, w=6):
    return Circle(radius=r, stroke_color=INK, stroke_width=w, fill_opacity=0).move_to([x, y, 0])


# ── the cast ─────────────────────────────────────────────────────────────────────────────
def service(ox, oy, s=0.8, n=3):
    """The demo service: a server stack whose base centre sits at (ox, oy). Returns (stack, lights)."""
    return Iso(ox, oy + 0.65 * s, s).server(-0.65, -0.65, 0, 1.3, 1.3, 0.4, n)


def magnifier(x, y, r=0.45):
    glass = Circle(radius=r, stroke_color=INK, stroke_width=8, fill_color=CARD, fill_opacity=0.85).move_to([x, y, 0])
    handle = Line([x + r * 0.72, y - r * 0.72, 0], [x + r * 1.7, y - r * 1.7, 0], color=INK, stroke_width=14)
    return VGroup(handle, glass)


def trace(x, y, w=2.6, n=4, gap=0.34):
    """A trace waterfall: a root span and child spans, left edge at x, top row at y."""
    spec = [(0.0, 1.0), (0.08, 0.45), (0.5, 0.42), (0.58, 0.3)][:n]
    return VGroup(*[Rectangle(width=w * f, height=0.2, fill_color=BAR1 if i % 2 == 0 else BAR2, fill_opacity=1,
                              stroke_width=0).move_to([x + w * o + w * f / 2, y - i * gap, 0])
                    for i, (o, f) in enumerate(spec)])


def log_page(x, y, w=1.5, h=1.8, n=3):
    pg = paper(x, y, w, h)
    return VGroup(pg, scribble_block(x - w / 2 + 0.25, y + h / 2 - 0.45, w - 0.5, n=n, gap=0.4))


def log_sheet(x, y, w=2.6, h=3.2, n=7, mark=None):
    """A log file that reads as one: a gutter of line dots, ruled entries, one line flagged."""
    g = VGroup(paper(x, y, w, h))
    gx = x - w / 2 + 0.44
    g.add(Line([gx, y + h / 2 - 0.16, 0], [gx, y - h / 2 + 0.16, 0], color=GHOST, stroke_width=3))
    top, step = y + h / 2 - 0.46, (h - 0.92) / max(1, n - 1)
    for i in range(n):
        yy = top - i * step
        g.add(Dot([x - w / 2 + 0.24, yy, 0], radius=0.045, color=DIM))
        g.add(scribble(gx + 0.16, yy, (w - 0.78) * (0.95, 0.68, 0.86, 0.6, 0.92, 0.74, 0.8)[i % 7],
                       amp=0.09, sw=4))
        if mark is not None and i == mark:
            g.add(Dot([x + w / 2 - 0.2, yy, 0], radius=0.09, color=TERRA))
    return g


def timeline(x, y, w=2.4):
    ln = Line([x, y, 0], [x + w, y, 0], color=INK, stroke_width=5)
    dots = VGroup(*[Dot([x + w * f, y, 0], radius=0.09, color=INK) for f in (0.15, 0.5)],
                  Dot([x + w * 0.85, y, 0], radius=0.11, color=TERRA))
    return VGroup(ln, dots)


def gate(x, y, L=1.9):
    """A barrier: post at x, arm pointing right. Returns (post, arm, pivot)."""
    post = Rectangle(width=0.3, height=1.3, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([x, y + 0.65, 0])
    pivot = np.array([x, y + 1.1, 0])
    arm = VGroup(Line(pivot, pivot + np.array([L, 0, 0]), color=INK, stroke_width=16),
                 *[Line(pivot + np.array([L * f, 0, 0]), pivot + np.array([L * f + 0.18, 0, 0]), color=CARD, stroke_width=10)
                   for f in (0.3, 0.6, 0.85)])
    return post, arm, pivot


def seal(x, y, r=0.32):
    return VGroup(Circle(radius=r, fill_color=TERRA, fill_opacity=1, stroke_width=0).move_to([x, y, 0]),
                  check(x - 0.03, y + 0.03, r * 0.45, color=CARD, w=6))


def card(x, y, w=2.2, h=1.4, rows=2):
    box = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    lines = VGroup(*[scribble(x - w / 2 + 0.25, y + h / 2 - 0.4 - i * 0.38, w - 0.5 - (0.4 if i == rows - 1 else 0))
                     for i in range(rows)])
    return VGroup(box, lines)


def letter_card(x, y, ch, w=1.5, h=1.8):
    box = Rectangle(width=w, height=h, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    return VGroup(box, T(ch, 80, bold=True).move_to([x, y, 0]))


def switch(x, y):
    """A breaker switch. Returns (base, lever, pivot); flip the lever with Rotate about pivot."""
    base = RoundedRectangle(corner_radius=0.12, width=1.0, height=0.5, fill_color=DARK_TOP, fill_opacity=1,
                            stroke_width=0).move_to([x, y, 0])
    pivot = np.array([x, y + 0.2, 0])
    lever = VGroup(Line(pivot, pivot + np.array([-0.35, 0.5, 0]), color=INK, stroke_width=9),
                   Dot(pivot + np.array([-0.35, 0.5, 0]), radius=0.11, color=TERRA))
    return base, lever, pivot


def cylinder(x, y, w=1.3, h=1.3):
    """A database: centre (x, y)."""
    body = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    bottom = Ellipse(width=w, height=0.42, fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y - h / 2, 0])
    sides = VGroup(Line([x - w / 2, y - h / 2, 0], [x - w / 2, y + h / 2, 0], color=INK, stroke_width=4),
                   Line([x + w / 2, y - h / 2, 0], [x + w / 2, y + h / 2, 0], color=INK, stroke_width=4))
    top = Ellipse(width=w, height=0.42, fill_color=BOX_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y + h / 2, 0])
    rib = VGroup(*[Ellipse(width=w * 0.82, height=0.3, stroke_color=GHOST, stroke_width=3,
                           fill_opacity=0).move_to([x, y + h / 2 - 0.3 - i * 0.34, 0]) for i in range(2)])
    return VGroup(bottom, body, sides, rib, top)


def shell(x, y, w=1.4, h=0.9):
    box = RoundedRectangle(corner_radius=0.1, width=w, height=h, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    return VGroup(box, T(">_", 48, color=CARD, bold=True).move_to([x - 0.15, y, 0]))


def laptop(x, y, s=1.0):
    screen = Polygon([x - 1.15 * s, y, 0], [x + 1.15 * s, y, 0], [x + 1.05 * s, y + 1.5 * s, 0], [x - 1.05 * s, y + 1.5 * s, 0],
                     fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK, stroke_width=4)
    glow = Polygon([x - 0.95 * s, y + 0.18 * s, 0], [x + 0.95 * s, y + 0.18 * s, 0],
                   [x + 0.88 * s, y + 1.3 * s, 0], [x - 0.88 * s, y + 1.3 * s, 0],
                   fill_color="#2B2825", fill_opacity=1, stroke_width=0)
    base = Polygon([x - 1.35 * s, y, 0], [x + 1.35 * s, y, 0], [x + 1.6 * s, y - 0.35 * s, 0], [x - 1.6 * s, y - 0.35 * s, 0],
                   fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4)
    return VGroup(screen, glow, base)


def lock(x, y, s=0.5):
    body = Rectangle(width=s, height=s * 0.8, fill_color=DARK_TOP, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    shackle = Arc(radius=s * 0.3, start_angle=0, angle=PI, arc_center=[x, y + s * 0.4, 0], color=INK, stroke_width=7)
    return VGroup(shackle, body)


def pointer(x, y, s=0.6):
    """A mouse pointer whose tip is at (x, y): white body, ink outline."""
    pts = [(0, 0), (0, -1.0), (0.26, -0.76), (0.46, -1.18), (0.62, -1.1), (0.43, -0.69), (0.76, -0.69)]
    return Polygon(*[[x + u * s, y + v * s, 0] for u, v in pts], fill_color=CARD, fill_opacity=1,
                   stroke_color=INK, stroke_width=4).set_z_index(5)


def flow(a, b, color=INK):
    """A plain flow arrow from a to b."""
    return Arrow(np.array([a[0], a[1], 0]), np.array([b[0], b[1], 0]), buff=0, color=color, stroke_width=6,
                 tip_length=0.24, max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=20)


def wire(a, b, color=GHOST, w=5):
    """A structural connection — drawn, not animated; it says two things are wired together."""
    return Line([a[0], a[1], 0], [b[0], b[1], 0], color=color, stroke_width=w)


def arrow_tip(cx, cy, r, a, cw=True, s=0.16, color=INK):
    """A head sitting on the circle (cx, cy, r) at angle `a`, pointing ALONG the path."""
    return Triangle(fill_color=color, fill_opacity=1, stroke_width=0).scale(s)\
        .rotate(a - PI if cw else a).move_to([cx + r * np.cos(a), cy + r * np.sin(a), 0])


def plinth(x, y=-1.3, s=1.0):
    return Iso(x, y, s).box(-0.6, -0.6, 0, 1.2, 1.2, 0.3)


# ══════════════════ PART 1 — EXECUTIVE SUMMARY ══════════════════
EXEC = "Executive summary"


class B00_Hook(Scene):
    def construct(self):
        self.add(heading(EXEC))
        # A real monitor standing on the stage: bezel, recessed screen, neck, foot, contact shadow.
        px, py = -2.7, 0.75
        sh = shadow(px, -1.78, 3.6)
        foot = Rectangle(width=2.6, height=0.2, fill_color=DARK_TOP, fill_opacity=1,
                         stroke_color=INK, stroke_width=3).move_to([px, -1.62, 0])
        neck = Rectangle(width=0.52, height=0.68, fill_color=DARK_TOP, fill_opacity=1,
                         stroke_width=0).move_to([px, -1.18, 0])
        bez = Rectangle(width=6.5, height=3.3, fill_color=DARK_TOP, fill_opacity=1,
                        stroke_color=INK, stroke_width=4).move_to([px, py, 0])
        scr = Rectangle(width=6.1, height=2.9, fill_color="#2B2825", fill_opacity=1,
                        stroke_width=0).move_to([px, py, 0])
        # three dim metric bars, lower half of the screen
        rows = VGroup(*[Rectangle(width=4.6 * f, height=0.2, fill_color=DIM, fill_opacity=1,
                                  stroke_width=0).move_to([px - 2.5 + 2.3 * f, 0.18 - i * 0.52, 0])
                        for i, f in enumerate((0.9, 0.58, 0.74))])
        # a throughput sparkline across the top half that falls off a cliff
        pts = [(-2.5, 1.5), (-1.9, 1.72), (-1.35, 1.44), (-0.75, 1.78), (-0.2, 1.52), (0.35, 1.68)]
        line = VMobject(stroke_color=GHOST, stroke_width=6)
        line.set_points_as_corners([[px + u, v, 0] for u, v in pts] + [[px + 0.9, 1.62, 0], [px + 1.5, 0.72, 0],
                                                                      [px + 2.5, 0.68, 0]])
        axis = Line([px - 2.7, 0.62, 0], [px + 2.7, 0.62, 0], color="#3F3A35", stroke_width=3)
        light = Dot([px + 1.5, 0.72, 0], radius=0.17, color=TERRA)
        until(self, "a service broke", lead=0.9)
        self.play(FadeIn(sh), FadeIn(bez), FadeIn(scr), FadeIn(foot), FadeIn(neck), run_time=0.5)
        self.play(Create(axis), Create(line), FadeIn(rows), run_time=0.6)
        self.play(FadeIn(light, scale=0.5), run_time=0.3)
        until(self, "doesn't tell you why")
        q = T("?", 200, bold=True).move_to([3.9, 0.95, 0])
        gplay(self, FadeIn(q, shift=UP * 0.4), rt=0.6)
        blank = DashedVMobject(Rectangle(width=3.4, height=1.7, stroke_color=DIM, stroke_width=5)
                               .move_to([3.9, -1.45, 0]), num_dashes=30)
        self.play(Create(blank), run_time=0.5)
        finish(self)


class B01_WhatItIs(Scene):
    def construct(self):
        self.add(heading(EXEC))
        self.add(tag())
        rail = rule(-2.42, -5.9, 5.9)
        self.add(rail)
        until(self, "reads a broken", lead=1.1)
        stack, lights = service(-5.05, -2.3, 0.95, 3)
        sh = shadow(-5.05, -2.44, 2.5)
        self.play(FadeIn(sh), FadeIn(stack, shift=UP * 0.2), FadeIn(lights), run_time=0.6)
        lp = log_sheet(-2.25, 0.85, 1.9, 2.4, 5, mark=2)
        tr = trace(-0.95, 1.5, 2.9, 4, 0.4)
        tl = timeline(-0.95, -1.35, 2.9)
        self.play(LaggedStart(FadeIn(lp, shift=DOWN * 0.2), FadeIn(tr, shift=DOWN * 0.2),
                              FadeIn(tl, shift=DOWN * 0.2), lag_ratio=0.3), run_time=0.9)
        until(self, "works out why")
        mg = magnifier(-2.4, 0.8, 0.5)
        self.play(FadeIn(mg), run_time=0.3)
        self.play(mg.animate.move_to([1.0, 0.8, 0]), run_time=0.8)
        until(self, "proposes one fix")
        cd = card(3.95, 0.75, 2.8, 2.0, 3)
        gplay(self, FadeIn(cd, shift=RIGHT * 0.3), rt=0.5)
        until(self, "must approve")
        post, arm, _ = gate(3.0, -2.4, 1.6)
        shp = shadow(3.05, -2.46, 1.1)
        self.play(FadeIn(shp), FadeIn(post), FadeIn(arm), run_time=0.4)
        finish(self)


class B02_Artifact(Scene):
    def construct(self):
        self.add(heading(EXEC))
        self.add(tag())
        until(self, "one public repository")
        bk, fr = Iso(-4.35, -1.35, 1.05).open_box(-0.75, -0.75, 0, 1.5, 1.5, 0.9)
        shb = shadow(-4.35, -1.5, 3.1)
        self.play(FadeIn(shb), FadeIn(bk, shift=UP * 0.2), FadeIn(fr, shift=UP * 0.2), run_time=0.6)
        # four deliverables on a clean 2×2 grid, each labelled underneath on a shared baseline
        cells = [(0.9, 1.05, 0.38, "demo service"), (4.25, 1.05, 0.38, "the agent"),
                 (0.9, -1.35, -2.02, "approval screen"), (4.25, -1.35, -2.02, "evaluation report")]
        pages = [Iso(x, y, 1.1).page(-0.45, -0.45, 0.30, 0.9, 1.1) for x, y, _, _ in cells]
        labels = [T(n, 30).move_to([x, ly, 0]) for x, _, ly, n in cells]
        until(self, "demo service")
        gplay(self, FadeIn(pages[0], shift=UP * 0.3), FadeIn(labels[0]), rt=0.45)
        self.play(FadeIn(pages[1], shift=UP * 0.3), FadeIn(labels[1]), run_time=0.45)
        until(self, "approval screen")
        self.play(FadeIn(pages[2], shift=UP * 0.3), FadeIn(labels[2]), run_time=0.45)
        until(self, "evaluation report")
        self.play(FadeIn(pages[3], shift=UP * 0.3), FadeIn(labels[3]), run_time=0.45)
        finish(self)


class B03_WhyCare(Scene):
    def construct(self):
        self.add(heading(EXEC))
        self.add(plinth(-5.0, -1.9, 1.15), shadow(-5.0, -2.0, 2.6))
        until(self, "is the service healthy")
        ck = check(-5.0, -0.75, 0.52, color=INK, w=10)
        self.play(Create(ck), run_time=0.5)
        until(self, "the answer is no")
        xm = xmark(-5.0, -0.75, 0.42, 10).set_color(TERRA)
        gplay(self, FadeOut(ck), Create(xm), rt=0.5)
        until(self, "reads logs by hand")
        wall = VGroup(*[log_sheet(-2.45 + (i % 4) * 1.95, 1.3 - (i // 4) * 2.5, 1.6, 2.1, 5,
                                  mark=(1 if i == 5 else None))
                        for i in range(8)])
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in wall], lag_ratio=0.07), run_time=1.0)
        ptr = pointer(-2.4, 2.0, 0.6)
        self.play(FadeIn(ptr), run_time=0.25)
        self.play(ptr.animate.move_to([2.3, -1.45, 0]), run_time=0.9)
        until(self, "where time goes")
        cl = Circle(radius=0.68, stroke_color=INK, stroke_width=8, fill_color=CARD,
                    fill_opacity=1).move_to([5.1, -1.6, 0])
        ticks = VGroup(*[Line([5.1 + 0.52 * np.cos(a), -1.6 + 0.52 * np.sin(a), 0],
                              [5.1 + 0.64 * np.cos(a), -1.6 + 0.64 * np.sin(a), 0],
                              color=DIM, stroke_width=4) for a in np.arange(0, TAU, TAU / 12)])
        hand = Line([5.1, -1.6, 0], [5.1, -1.02, 0], color=TERRA, stroke_width=9)
        gplay(self, FadeIn(cl), FadeIn(ticks), Create(hand), rt=0.4)
        self.play(Rotate(hand, -TAU * 0.75, about_point=[5.1, -1.6, 0]), run_time=0.8)
        finish(self)


class B04_CheckNotTrust(Scene):
    def construct(self):
        self.add(heading(EXEC))
        self.add(tag())
        # Executive summary: what you get, not how it is enforced. The citation checker is B16's
        # job; this beat stays on the benefit, because the brief asks part 1 to keep "how" out.
        until(self, "check it instead", lead=0.7)
        lp = log_sheet(-4.9, 1.15, 2.2, 2.3, 6, mark=3)
        tr = trace(-6.0, -1.25, 2.2, n=3)
        self.play(FadeIn(lp, shift=DOWN * 0.2), FadeIn(tr), run_time=0.5)
        until(self, "does the digging")
        mg = magnifier(-4.2, 0.35, 0.5)
        ar = flow((-3.3, 0.85), (-1.6, 0.85))
        dg = card(0.1, 0.85, 2.8, 1.7, rows=3)
        dgl = T("diagnosis", 30).move_to([0.1, -0.45, 0])
        gplay(self, FadeIn(mg, scale=0.7), Create(ar), FadeIn(dg), FadeIn(dgl), rt=0.6)
        until(self, "you decide")
        post, arm, pv = gate(4.3, -0.75, 1.5)
        pt = pointer(4.5, 1.5, 0.55)
        ar2 = flow((1.6, 0.85), (3.3, 0.85))
        self.play(Create(ar2), FadeIn(post), FadeIn(arm), FadeIn(pt), run_time=0.55)
        until(self, "any fix runs")
        self.play(Rotate(arm, angle=PI / 2.6, about_point=pv), run_time=0.5)
        finish(self)

# ══════════════════ PART 2 — INTRODUCTION / PRIOR WORK ══════════════════
PRIOR = "What already exists"


class B05_Holmes(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        until(self, "This isn't new")
        pls = VGroup(plinth(-3.7, -1.75, 1.1), plinth(3.7, -1.75, 1.1))
        shs = VGroup(shadow(-3.7, -2.45, 2.5), shadow(3.7, -2.45, 2.5))
        self.play(FadeIn(shs), *[FadeIn(p, shift=UP * 0.15) for p in pls], run_time=0.5)
        until(self, "HolmesGPT")
        lab = T("HolmesGPT", 40).move_to([-3.7, -2.78, 0])
        mg = magnifier(-3.7, 0.25, 0.6)
        self.play(FadeIn(lab), FadeIn(mg, shift=DOWN * 0.25), run_time=0.55)
        until(self, "agentic loop")
        ring = VGroup(*[Rectangle(width=0.52, height=0.52, fill_color=DARK_TOP, fill_opacity=1,
                                  stroke_width=0)
                        .move_to([-3.7 + 1.9 * np.cos(a), 0.25 + 1.5 * np.sin(a), 0])
                        for a in np.arange(0, TAU, TAU / 6)])
        orb = Ellipse(width=3.8, height=3.0, stroke_color=DIM, stroke_width=4,
                      fill_opacity=0).move_to([-3.7, 0.25, 0])
        gplay(self, Create(orb), LaggedStart(*[FadeIn(b, scale=0.6) for b in ring],
                                             lag_ratio=0.1), rt=0.8)
        stars = T("4k stars", 36, color=DIM).move_to([0.6, 1.5, 0])
        srule = Line([-0.15, 1.1, 0], [1.35, 1.1, 0], color=GHOST, stroke_width=4)
        self.play(FadeIn(stars), Create(srule), run_time=0.3)
        until(self, "read-only by design")
        lk = lock(0.6, 0.15, 0.72)
        ro = T("read-only", 32).move_to([0.6, -0.7, 0])
        gplay(self, FadeIn(lk, shift=UP * 0.2), FadeIn(ro), rt=0.4)
        finish(self)


class B06_HolmesGap(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        self.add(plinth(-3.7, -1.75, 1.1), shadow(-3.7, -2.45, 2.5),
                 T("HolmesGPT", 40).move_to([-3.7, -2.78, 0]))
        until(self, "the mature option")
        badge = VGroup(RoundedRectangle(corner_radius=0.18, width=2.7, height=0.85,
                                        fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                        stroke_width=4).move_to([-3.7, -0.6, 0]),
                       T("mature", 38).move_to([-3.7, -0.6, 0]))
        self.play(FadeIn(badge, shift=DOWN * 0.2), run_time=0.5)
        until(self, "independent evaluation")
        frame = DashedVMobject(Rectangle(width=4.6, height=3.0, stroke_color=DIM,
                                         stroke_width=6).move_to([3.1, 0.35, 0]),
                               num_dashes=34)
        flab = T("independent evaluation", 34, color=DIM).move_to([3.1, -1.65, 0])
        gplay(self, Create(frame), FadeIn(flab), rt=0.7)
        until(self, "describing itself")
        loop = Arc(radius=1.15, start_angle=-PI / 2, angle=1.65 * PI, arc_center=[-3.7, 1.6, 0],
                   color=INK, stroke_width=8)
        tip = arrow_tip(-3.7, 1.6, 1.15, -PI / 2 + 1.65 * PI, cw=False, s=0.18)
        gplay(self, Create(loop), FadeIn(tip), rt=0.6)
        finish(self)


class B07_AIOpsLab(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        self.add(plinth(3.7, -1.75, 1.1), shadow(3.7, -2.45, 2.5),
                 T("AIOpsLab", 40).move_to([3.7, -2.78, 0]))
        until(self, "a benchmark, not a product")
        tiles = [Rectangle(width=0.44, height=0.44, fill_color=PAGE_TOP, fill_opacity=1,
                           stroke_color=INK, stroke_width=2.5)
                 .move_to([0.6 + (i % 8) * 0.56, 2.2 - (i // 8) * 0.56, 0]) for i in range(48)]
        until(self, "Forty-eight problems")
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in tiles], lag_ratio=0.012),
                  run_time=1.1)
        n48 = T("48", 62, bold=True).move_to([-0.75, 1.65, 0])
        nl = T("problems", 30, color=DIM).move_to([-0.75, 1.0, 0])
        self.play(FadeIn(n48), FadeIn(nl), run_time=0.3)
        apps = VGroup(*[service(-4.9 + i * 1.75, -1.0, 0.6, 2)[0] for i in range(3)])
        ash = VGroup(*[shadow(-4.9 + i * 1.75, -1.12, 1.6) for i in range(3)])
        gplay(self, FadeIn(ash), FadeIn(apps, shift=UP * 0.2), rt=0.5)
        until(self, "faults injected")
        bolt = Polygon(*[[-3.15 + u * 1.7, 0.95 + v * 1.7, 0] for u, v in
                         [(0.12, 0.6), (-0.16, 0.08), (0.04, 0.08), (-0.1, -0.5),
                          (0.24, 0.02), (0.03, 0.02)]],
                       fill_color=TERRA, fill_opacity=1, stroke_width=0)
        gplay(self, FadeIn(bolt, shift=DOWN * 0.5), rt=0.45)
        finish(self)


class B08_Numbers(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        # The spoken numbers are RANGES across agents, so the chart draws ranges, not single
        # bars. Every value is arXiv:2501.06706v1 Table 4, floor and ceiling across the three
        # LLM agents the narration spans (GPT-4-w-Shell, ReAct, Flash) — named on screen, so
        # the excluded fourth agent (GPT-3.5-w-Shell, weaker on every task) is not hidden.
        base, SCALE = -1.9, 3.3          # 100% of a task = 3.3 scene units
        X0, X1 = -5.0, 5.9               # the plot box; tick labels live to the left of X0
        xs = [-3.0, 0.5, 4.0]
        names = ["detection", "root cause", "mitigation"]
        rng = [(0.6923, 1.0), (0.3636, 0.4545), (0.2727, 0.5455)]
        until(self, "published numbers")
        hero = T("59%", 165, bold=True).move_to([0.0, 1.2, 0])
        self.play(FadeIn(hero, shift=UP * 0.3), run_time=0.6)
        until(self, "fifty-nine percent")
        self.play(hero.animate.scale(0.40).move_to([-5.2, 2.28, 0]), run_time=0.5)
        # a real chart floor: who was measured, a baseline, a 100% ceiling, and the source
        who = T("GPT-4 / ReAct / Flash", 30, color=DIM).move_to([MARGIN_R, 2.28, 0], aligned_edge=RIGHT)
        src = T("arXiv:2501.06706v1, Table 4", 30, color=DIM).move_to([MARGIN_R, -3.15, 0],
                                                                      aligned_edge=RIGHT)
        axis = Line([X0, base, 0], [X1, base, 0], color=INK, stroke_width=5)
        ceil_ = rule(base + SCALE, X0, X1)
        t100 = T("100%", 30, color=DIM).move_to([X0 - 0.15, base + SCALE, 0], aligned_edge=RIGHT)
        hcap = T("best agent, overall", 30, color=DIM).move_to([-4.0, 2.28, 0], aligned_edge=LEFT)
        self.play(Create(axis), FadeIn(ceil_), FadeIn(t100), FadeIn(hcap), FadeIn(who),
                  FadeIn(src), run_time=0.45)
        bands, labs = VGroup(), VGroup()
        for x, nm, (lo, hi) in zip(xs, names, rng):
            bands.add(Rectangle(width=2.5, height=(hi - lo) * SCALE, fill_color=BAR2,
                                fill_opacity=1, stroke_color=INK, stroke_width=3)
                      .move_to([x, base + (lo + hi) / 2 * SCALE, 0]))
            labs.add(TBase(nm, 32, x, base - 0.45))
        until(self, "detection, sixty-nine")
        gplay(self, FadeIn(bands[0], shift=UP * 0.2), FadeIn(labs[0]), rt=0.5)
        until(self, "root cause")
        self.play(FadeIn(bands[1], shift=UP * 0.2), FadeIn(labs[1]), run_time=0.5)
        until(self, "mitigation")
        self.play(FadeIn(bands[2], shift=UP * 0.2), FadeIn(labs[2]), run_time=0.5)
        until(self, "consistently achieve")
        half = base + SCALE * 0.5
        ruleline = DashedLine([X0, half, 0], [X1, half, 0], color=TERRA,
                              stroke_width=7, dash_length=0.24)
        t50 = T("50%", 30, color=TERRA).move_to([X0 - 0.15, half, 0], aligned_edge=RIGHT)
        self.play(Create(ruleline), FadeIn(t50), run_time=0.5)
        finish(self)


class B09_Cluster(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        until(self, "needs Kubernetes")
        blocks = VGroup(*[service(0.1 + (i % 7) * 0.9, 1.5 - (i // 7) * 1.05, 0.36, 1)[0]
                          for i in range(28)])
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in blocks], lag_ratio=0.02),
                  run_time=1.2)
        until(self, "twenty-eight microservices")
        pen = DashedVMobject(RoundedRectangle(corner_radius=0.2, width=6.9, height=4.4,
                                              stroke_color=DIM, stroke_width=5)
                             .move_to([2.8, 0.05, 0]), num_dashes=52)
        n = T("28 services", 36, color=DIM).move_to([2.8, -2.52, 0])
        gplay(self, Create(pen), FadeIn(n), rt=0.5)
        until(self, "on a laptop")
        lt = laptop(-3.9, -1.25, 0.95)
        shl = shadow(-3.9, -1.68, 3.3)
        sw = Circle(radius=0.5, stroke_color=INK, stroke_width=7, fill_color=CARD,
                    fill_opacity=1).move_to([-3.9, 1.25, 0])
        swh = Line([-3.9, 1.25, 0], [-3.9, 1.67, 0], color=DIM, stroke_width=7)
        cap = T("one laptop", 32).move_to([-3.9, -2.25, 0])
        gplay(self, FadeIn(shl), FadeIn(lt, shift=UP * 0.2), FadeIn(sw), Create(swh),
              FadeIn(cap), rt=0.6)
        finish(self)


class B10_Gap(Scene):
    def construct(self):
        self.add(heading(PRIOR))
        self.add(tag())
        self.add(plinth(-5.1, -1.8, 1.05), shadow(-5.1, -2.45, 2.4),
                 plinth(5.1, -1.8, 1.05), shadow(5.1, -2.45, 2.4),
                 T("HolmesGPT", 34).move_to([-5.1, -2.78, 0]),
                 T("AIOpsLab", 34).move_to([5.1, -2.78, 0]))
        until(self, "thin public evidence")
        d1 = DashedVMobject(Rectangle(width=1.9, height=1.3, stroke_color=DIM,
                                      stroke_width=5).move_to([-5.1, -0.25, 0]), num_dashes=18)
        self.play(Create(d1), run_time=0.45)
        until(self, "needs a cluster")
        cl = VGroup(*[service(5.1 + dx, -0.78 + dy, 0.34, 1)[0] for dx, dy in
                      [(-0.62, 0), (0.0, 0.0), (0.62, 0), (-0.31, 0.62), (0.31, 0.62)]])
        gplay(self, FadeIn(cl, shift=UP * 0.2), rt=0.5)
        until(self, "goes between them")
        span = VGroup(Line([-3.6, 2.1, 0], [3.6, 2.1, 0], color=GHOST, stroke_width=4),
                      Line([-3.6, 2.1, 0], [-3.6, 1.8, 0], color=GHOST, stroke_width=4),
                      Line([3.6, 2.1, 0], [3.6, 1.8, 0], color=GHOST, stroke_width=4))
        mid = Iso(0.0, -1.75, 1.0).box(-0.75, -0.75, 0, 1.5, 1.5, 0.35)
        self.play(FadeIn(span), FadeIn(shadow(0.0, -2.5, 2.8)),
                  FadeIn(mid, shift=UP * 0.3), run_time=0.5)
        lt = laptop(0.0, -0.3, 0.85)
        self.play(FadeIn(lt, shift=UP * 0.2), run_time=0.5)
        until(self, "shipping the broken service")
        svc = service(-0.65, 1.15, 0.4, 2)[0]
        mg = magnifier(0.9, 1.75, 0.38)
        gplay(self, FadeIn(svc), FadeIn(mg), rt=0.5)
        self.play(FadeIn(T("TraceCase", 40).move_to([0.0, -2.78, 0])), run_time=0.3)
        finish(self)


# ══════════════════ PART 3 — METHODS ══════════════════
METH = "Methods"


class B11_SystemUnderTest(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        until(self, "the thing that breaks")
        api = service(-4.3, 1.15, 0.72, 2)[0]
        sh1 = shadow(-4.3, 1.03, 1.9)
        self.play(FadeIn(sh1), FadeIn(api, shift=UP * 0.2), run_time=0.5)
        until(self, "API and worker")
        wk = service(-1.5, 1.15, 0.72, 2)[0]
        sh2 = shadow(-1.5, 1.03, 1.9)
        la = T("API", 32).move_to([-4.3, 0.25, 0])
        lw = T("worker", 32).move_to([-1.5, 0.25, 0])
        w1 = wire((-3.55, 1.68), (-2.25, 1.68))
        self.play(FadeIn(sh2), FadeIn(wk, shift=UP * 0.2), FadeIn(w1), FadeIn(la), FadeIn(lw), run_time=0.5)
        until(self, "Postgres, and Redis")
        pg = cylinder(1.4, 1.68, 1.25, 1.3)
        rd = cylinder(4.0, 1.68, 1.25, 1.3)
        sh3, sh4 = shadow(1.4, 0.95, 1.5), shadow(4.0, 0.95, 1.5)
        lp = T("Postgres", 32).move_to([1.4, 0.25, 0])
        lr = T("Redis", 32).move_to([4.0, 0.25, 0])
        w2 = VGroup(wire((-0.75, 1.68), (0.72, 1.68)), wire((2.08, 1.68), (3.33, 1.68)))
        gplay(self, FadeIn(sh3), FadeIn(sh4), FadeIn(pg, shift=UP * 0.2), FadeIn(rd, shift=UP * 0.2),
              FadeIn(w2), FadeIn(lp), FadeIn(lr), rt=0.6)
        box = DashedVMobject(RoundedRectangle(corner_radius=0.22, width=11.2, height=3.0,
                                              stroke_color=DIM, stroke_width=5)
                             .move_to([-0.15, 1.15, 0]), num_dashes=56)
        self.play(Create(box), run_time=0.6)
        until(self, "writes traces and logs")
        f1 = log_sheet(-3.6, -1.7, 1.9, 2.0, 5)
        f2 = log_sheet(3.3, -1.7, 1.9, 2.0, 5)
        a1 = flow((-2.2, -0.45), (-3.3, -0.78))
        a2 = flow((2.0, -0.45), (3.0, -0.78))
        gplay(self, Create(a1), Create(a2), FadeIn(f1), FadeIn(f2), rt=0.7)
        finish(self)


class B12_FaultCatalogue(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        xs = [-4.85, -2.42, 0.0, 2.42, 4.85]
        names = ["stale cache", "slow query", "pool", "bad deploy", "queue"]
        until(self, "fixed catalogue", lead=0.7)
        cards = [card(x, 1.25, 2.25, 1.9, 3) for x in xs]
        nums = [T(str(i + 1), 26, color=DIM).move_to([x - 0.9, 2.35, 0]) for i, x in enumerate(xs)]
        labs = [T(n, 30).move_to([x, 0.0, 0]) for n, x in zip(names, xs)]
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.25) for c in cards], lag_ratio=0.12),
                  run_time=1.0)
        self.play(LaggedStart(*[FadeIn(l) for l in labs], lag_ratio=0.08),
                  FadeIn(VGroup(*nums)), run_time=0.5)
        until(self, "one command")
        base, lever, pv = switch(-4.85, -1.45)
        gplay(self, FadeIn(base), FadeIn(lever), rt=0.4)
        self.play(Rotate(lever, -1.0, about_point=pv), run_time=0.4)
        until(self, "Stale cache")
        lit = Rectangle(width=2.45, height=2.1, fill_opacity=0,
                        stroke_color=TERRA, stroke_width=7).move_to([-4.85, 1.25, 0])
        self.play(Create(lit), run_time=0.35)
        until(self, "written down first")
        env = VGroup(Rectangle(width=3.4, height=1.5, fill_color=CARD, fill_opacity=1,
                               stroke_color=INK, stroke_width=4).move_to([2.6, -1.6, 0]),
                     Polygon([0.9, -0.85, 0], [4.3, -0.85, 0], [2.6, -1.72, 0],
                             fill_color=PAGE_L, fill_opacity=1, stroke_color=INK, stroke_width=4))
        sl = seal(4.0, -2.15, 0.3)
        el = T("ground truth", 30).move_to([2.6, -2.72, 0])
        gplay(self, FadeIn(env), FadeIn(sl), FadeIn(el), rt=0.6)
        finish(self)


class B13_DataSource(Scene):
    def construct(self):
        self.add(heading(METH))
        until(self, "That's my data")
        svc = service(-3.9, -1.2, 0.85, 2)[0]
        shs = shadow(-3.9, -1.32, 2.3)
        self.play(FadeIn(shs), FadeIn(svc, shift=UP * 0.2), run_time=0.5)
        # an open collection tray with a lip, not a kraft slab
        tray = VGroup(Rectangle(width=3.6, height=1.3, fill_color=BOX_L, fill_opacity=1,
                                stroke_color=INK, stroke_width=4).move_to([3.3, -1.5, 0]),
                      Line([1.5, -0.95, 0], [5.1, -0.95, 0], color=INK, stroke_width=5),
                      Line([1.78, -1.95, 0], [4.82, -1.95, 0], color=DEEP_KRAFT, stroke_width=4),
                      T("logs + traces", 30).move_to([3.3, -2.45, 0]))
        pgs = VGroup(*[Iso(1.85 + i * 1.1, -0.25, 0.66).page(-0.3, -0.3, 0.22, 0.6, 1.0)
                       for i in range(3)])
        self.play(FadeIn(tray), LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pgs],
                                            lag_ratio=0.15), run_time=0.9)
        until(self, "No customer logs")
        # three doors that are shut to me: frame, panel, handle, struck through
        doors = VGroup()
        for x in (-5.3, 0.0, 5.3):
            doors.add(VGroup(
                Rectangle(width=1.4, height=1.7, fill_color=DIM, fill_opacity=0.3,
                          stroke_color=INK, stroke_width=4).move_to([x, 1.85, 0]),
                Rectangle(width=0.9, height=1.1, fill_opacity=0, stroke_color=INK,
                          stroke_width=3).move_to([x, 1.95, 0]),
                Dot([x + 0.5, 1.75, 0], radius=0.08, color=INK)))
        xs_ = VGroup(*[xmark(x, 1.85, 0.34, 9) for x in (-5.3, 0.0, 5.3)])
        gplay(self, FadeIn(doors), Create(xs_), rt=0.6)
        until(self, "break my own service")
        loop = VGroup(flow((-2.4, -0.55), (1.15, -0.1)), flow((1.5, -2.35), (-3.1, -2.0)))
        self.play(Create(loop), run_time=0.7)
        until(self, "because I caused it")
        sl = seal(-3.9, 0.55, 0.42)
        gplay(self, FadeIn(sl, scale=0.6), rt=0.4)
        finish(self)


class B14_AgentLoop(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        cx, cy, r = -2.3, -0.1, 1.8
        names = ["observe", "pick a tool", "record", "update"]
        angs = [PI / 2, 0.0, -PI / 2, PI]
        until(self, "Step three")
        ring = Circle(radius=r, stroke_color=DIM, stroke_width=5,
                      fill_opacity=0).move_to([cx, cy, 0])
        # arrowheads on the ring: this is a loop, and it turns one way
        heads = VGroup(*[arrow_tip(cx, cy, r, a, cw=True, s=0.15, color=DIM)
                         for a in (PI / 4, 3 * PI / 4, 5 * PI / 4, 7 * PI / 4)])
        self.play(Create(ring), FadeIn(heads), run_time=0.5)
        until(self, "Observe, pick a tool")
        nodes, labs = VGroup(), VGroup()
        for i, (nm, a) in enumerate(zip(names, angs)):
            px, py = cx + r * np.cos(a), cy + r * np.sin(a)
            nodes.add(VGroup(Circle(radius=0.34, fill_color=CARD, fill_opacity=1, stroke_color=INK,
                                    stroke_width=5).move_to([px, py, 0]),
                             T(str(i + 1), 28).move_to([px, py, 0])))
            labs.add(T(nm, 30).move_to([px + (1.45 if abs(np.cos(a)) > 0.5 else 0) * np.sign(np.cos(a) or 1),
                                        py + (0.72 if np.sin(a) > 0.5 else (-0.72 if np.sin(a) < -0.5 else 0)), 0]))
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in nodes], lag_ratio=0.12),
                  FadeIn(labs), run_time=0.9)
        dot = Dot([cx, cy + r, 0], radius=0.18, color=TERRA)
        self.play(FadeIn(dot), run_time=0.25)
        self.play(MoveAlongPath(dot, Arc(radius=r, start_angle=PI / 2, angle=-TAU * 0.875,
                                         arc_center=[cx, cy, 0])), run_time=1.1)
        until(self, "stops when every claim")
        sl = seal(3.9, 1.45, 0.42)
        ev = T("supported", 30).move_to([3.9, 0.65, 0])
        a1 = flow((cx + r * 0.72, cy + 0.95), (3.3, 1.4))
        gplay(self, Create(a1), FadeIn(sl), FadeIn(ev), rt=0.55)
        until(self, "step budget")
        a2 = DashedLine([cx + r * 0.72, cy - 1.05, 0], [3.3, -1.3, 0], color=DIM,
                        stroke_width=6, dash_length=0.18)
        bl = T("step budget", 30).move_to([4.2, -1.5, 0])
        ticks = VGroup(*[Rectangle(width=0.2, height=0.34, fill_color=BAR2 if k < 3 else GHOST,
                                   fill_opacity=1, stroke_color=INK, stroke_width=2)
                         .move_to([3.25 + k * 0.33, -2.15, 0]) for k in range(6)])
        self.play(Create(a2), FadeIn(bl), FadeIn(ticks), run_time=0.5)
        finish(self)


class B15_AllowList(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        until(self, "allow-list in code", lead=0.9)
        bound = DashedVMobject(RoundedRectangle(corner_radius=0.24, width=7.4, height=4.3,
                                                stroke_color=INK, stroke_width=6,
                                                fill_opacity=0).move_to([-2.3, 0.15, 0]),
                               num_dashes=52)
        self.play(Create(bound), run_time=0.6)
        names = ["read logs", "query traces", "read deploys"]
        rows = VGroup()
        for i, n in enumerate(names):
            yy = 1.45 - i * 1.3
            icon = Iso(-4.75, yy - 0.45, 0.52).page(-0.3, -0.3, 0.2, 0.6, 1.0)
            rows.add(VGroup(icon, T(n, 34).move_to([-3.6, yy, 0], aligned_edge=LEFT),
                            Line([-4.0, yy - 0.62, 0], [-0.1, yy - 0.62, 0], color=GHOST, stroke_width=3)))
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in rows], lag_ratio=0.14),
                  run_time=0.9)
        until(self, "Not a shell")
        sh = shell(4.3, 0.75, 2.1, 1.3)
        gplay(self, FadeIn(sh, shift=LEFT * 0.3), rt=0.5)
        until(self, "deliberately not")
        post, arm, _ = gate(2.0, -2.3, 1.6)
        self.play(FadeIn(shadow(2.05, -2.36, 1.1)), FadeIn(post), FadeIn(arm), run_time=0.45)
        self.play(FadeIn(xmark(4.3, -0.75, 0.38, 9).set_color(TERRA)), run_time=0.3)
        finish(self)


class B16_Checker(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        until(self, "must cite")
        cd = Rectangle(width=2.7, height=1.5, fill_color=CARD, fill_opacity=1,
                       stroke_color=INK, stroke_width=4).move_to([-4.6, 1.5, 0])
        cdl = T("claim", 30).move_to([-4.6, 0.4, 0])
        self.play(FadeIn(cd, shift=DOWN * 0.2), FadeIn(cdl), run_time=0.45)
        chk = VGroup(RoundedRectangle(corner_radius=0.16, width=2.2, height=1.4,
                                      fill_color=DARK_TOP, fill_opacity=1,
                                      stroke_width=0).move_to([-0.8, 1.5, 0]),
                     T("checker", 30, color=CARD).move_to([-0.8, 1.5, 0]))
        a1 = flow((-3.2, 1.5), (-1.95, 1.5))
        self.play(Create(a1), FadeIn(chk), run_time=0.5)
        until(self, "reopens the file")
        lp = log_sheet(3.8, 1.2, 2.8, 3.2, 7, mark=2)
        hit = Rectangle(width=2.45, height=0.36, fill_opacity=0,
                        stroke_color=INK, stroke_width=6).move_to([3.88, 1.72, 0])
        a2 = flow((0.35, 1.5), (2.2, 1.55))
        gplay(self, Create(a2), FadeIn(lp), FadeIn(hit), rt=0.6)
        st = seal(-4.6, 1.5, 0.34)
        self.play(FadeIn(st, scale=0.6), run_time=0.35)
        until(self, "isn't there")
        cd2 = Rectangle(width=2.7, height=1.5, fill_color=CARD, fill_opacity=1,
                        stroke_color=INK, stroke_width=4).move_to([-4.6, -1.5, 0])
        a3 = DashedLine([-3.2, -1.5, 0], [-1.95, -1.5, 0], color=DIM, stroke_width=6,
                        dash_length=0.16)
        self.play(FadeIn(cd2), Create(a3), run_time=0.45)
        until(self, "the claim is rejected")
        tray = VGroup(Rectangle(width=2.8, height=1.0, fill_opacity=0,
                                stroke_color=INK, stroke_width=4).move_to([-0.8, -1.5, 0]),
                      T("rejected", 30).move_to([-0.8, -2.45, 0]))
        gplay(self, FadeIn(tray), FadeIn(xmark(-0.8, -1.5, 0.34, 9).set_color(TERRA)), rt=0.5)
        finish(self)


class B17_HumanGate(Scene):
    def construct(self):
        self.add(heading(METH))
        self.add(tag())
        until(self, "a short menu", lead=0.6)
        opts = VGroup(*[T(n, 32).move_to([-4.6, 1.75 - i * 1.1, 0])
                        for i, n in enumerate(["flush cache", "roll back", "restart worker"])])
        seps = VGroup(*[Line([-6.0, 1.2 - i * 1.1, 0], [-3.2, 1.2 - i * 1.1, 0], color=GHOST,
                             stroke_width=3) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(o, shift=RIGHT * 0.2) for o in opts], lag_ratio=0.13),
                  FadeIn(seps), run_time=0.85)
        until(self, "binds three things")
        pick = VGroup(Line([-6.0, 1.3, 0], [-3.2, 1.3, 0], color=INK, stroke_width=8),
                      Dot([-6.25, 1.75, 0], radius=0.14, color=TERRA))
        tgt = VGroup(Rectangle(width=2.0, height=1.3, fill_color=DARK_TOP, fill_opacity=1,
                               stroke_width=0).move_to([0.5, 1.5, 0]),
                     T("target", 32, color=CARD).move_to([0.5, 1.5, 0]))
        ev = log_sheet(4.3, 1.3, 2.2, 2.6, 6, mark=2)
        sl = seal(2.1, -0.95, 0.42)
        sll = T("one approval", 36).move_to([2.1, -1.9, 0])
        tri = VGroup(flow((-2.95, 1.6), (-0.6, 1.52)), flow((1.6, 1.42), (3.1, 1.35)),
                     flow((2.1, -0.2), (2.1, 0.55)))
        gplay(self, FadeIn(pick), FadeIn(tgt), FadeIn(ev), FadeIn(sl), FadeIn(sll),
              Create(tri), rt=0.9)
        until(self, "Change one and it refuses")
        crack = VGroup(Line([1.85, -1.3, 0], [2.18, -0.85, 0], color=CARD, stroke_width=6),
                       Line([2.18, -0.85, 0], [1.98, -0.55, 0], color=CARD, stroke_width=6))
        post, arm, pv = gate(-1.4, -2.5, 1.5)
        self.play(FadeIn(shadow(-1.35, -2.56, 1.1)), Create(crack),
                  FadeIn(post), FadeIn(arm), run_time=0.7)
        finish(self)


class B18_Resources(Scene):
    def construct(self):
        self.add(heading(METH))
        # a bench the kit stands on, so the left half reads as a desk and not two floating icons
        bench = Line([-6.0, -2.32, 0], [0.3, -2.32, 0], color=GHOST, stroke_width=5)
        self.add(bench)
        until(self, "a laptop and Docker", lead=0.7)
        lt = laptop(-4.6, -1.95, 1.05)
        bx = Iso(-1.4, -1.78, 0.95).box(-0.65, -0.65, 0, 1.3, 1.3, 0.55)
        lb = T("Docker", 30).move_to([-1.4, -2.78, 0])
        self.play(FadeIn(shadow(-4.6, -2.37, 3.6)), FadeIn(shadow(-1.4, -2.42, 2.1)),
                  FadeIn(lt, shift=UP * 0.2), FadeIn(bx, shift=UP * 0.2), FadeIn(lb),
                  run_time=0.7)
        until(self, "No cluster")
        hdr = VGroup(T("not needed", 30, color=DIM).move_to([4.3, 1.55, 0]),
                     Line([2.6, 1.2, 0], [6.0, 1.2, 0], color=GHOST, stroke_width=4))
        dim = VGroup(*[VGroup(T(n, 30, color=DIM).move_to([3.0, y, 0], aligned_edge=LEFT),
                              Line([2.6, y - 0.45, 0], [6.0, y - 0.45, 0], color=GHOST, stroke_width=3))
                       for n, y in [("cluster", 0.65), ("GPU", -0.25)]])
        crosses = VGroup(*[xmark(5.6, y, 0.26, 6).set_color(DIM) for y in (0.65, -0.25)])
        gplay(self, FadeIn(hdr), FadeIn(dim), Create(crosses), rt=0.7)
        until(self, "the open question")
        sock = DashedVMobject(RoundedRectangle(corner_radius=0.16, width=2.2, height=1.2,
                                               stroke_color=INK, stroke_width=6)
                              .move_to([-2.9, 2.05, 0]), num_dashes=24)
        q = T("?", 76, bold=True).move_to([-2.9, 2.05, 0])
        self.play(Create(sock), FadeIn(q), run_time=0.6)
        until(self, "a model interface")
        plugs = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.3, width=2.9, height=0.76,
                                                 fill_opacity=0,
                                                 stroke_color=INK, stroke_width=4)
                                .move_to([-2.9, 0.15 + i * 0.95, 0]),
                                T(n, 30).move_to([-2.9, 0.15 + i * 0.95, 0]))
                         for i, n in enumerate(["local model", "API key"])])
        gplay(self, LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in plugs], lag_ratio=0.15),
              rt=0.7)
        finish(self)


# ══════════════════ PART 4 — EVALUATION ══════════════════
EVAL = "Evaluation"


class B19_EvalSet(Scene):
    def construct(self):
        self.add(heading(EVAL))
        self.add(tag())
        tiles = [Rectangle(width=0.62, height=0.62, fill_color=PAGE_TOP, fill_opacity=1,
                           stroke_color=INK, stroke_width=3)
                 .move_to([-5.6 + (i % 6) * 0.88, 2.0 - (i // 6) * 0.88, 0]) for i in range(30)]
        until(self, "thirty scenarios")
        lab = T("30 scenarios", 38).move_to([-3.4, -2.35, 0])
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in tiles], lag_ratio=0.03),
                  FadeIn(lab), run_time=1.2)
        until(self, "Ten locked away")
        # a safe, not a grey slab: door, frame, hinges, dial
        door = Rectangle(width=3.5, height=3.0, fill_color=DARK_TOP, fill_opacity=1,
                         stroke_color=INK, stroke_width=4).move_to([3.4, 0.35, 0])
        inset = Rectangle(width=3.0, height=2.5, fill_opacity=0, stroke_color="#56504A",
                          stroke_width=4).move_to([3.4, 0.35, 0])
        hinges = VGroup(*[Rectangle(width=0.22, height=0.46, fill_color="#56504A", fill_opacity=1,
                                    stroke_width=0).move_to([1.78, 0.35 + s, 0]) for s in (0.95, -0.95)])
        dial = VGroup(Circle(radius=0.34, stroke_color=CARD, stroke_width=6, fill_opacity=0)
                      .move_to([4.55, 0.35, 0]),
                      Line([4.55, 0.35, 0], [4.55, 0.63, 0], color=CARD, stroke_width=6))
        lk = lock(3.4, 2.25, 0.6)
        vl = T("held out", 36).move_to([3.4, -1.6, 0])
        gplay(self, FadeIn(door), FadeIn(inset), FadeIn(hinges), FadeIn(dial),
              FadeIn(lk), FadeIn(vl), rt=0.55)
        held = tiles[20:]
        self.bring_to_front(*held)
        self.play(*[t.animate.move_to([2.15 + (k % 5) * 0.44, 0.72 - (k // 5) * 0.5, 0]).scale(0.6)
                    for k, t in enumerate(held)], run_time=0.9)
        finish(self)


class B20_Baseline(Scene):
    def construct(self):
        self.add(heading(EVAL))
        until(self, "The baseline")
        # the baseline gets the same evidence as the agent: logs, traces and deploys.
        lp = log_sheet(-4.7, 1.55, 2.2, 2.0, 5)
        tr = trace(-5.8, -0.1, 2.1, n=3)
        self.play(FadeIn(lp, shift=DOWN * 0.2), FadeIn(tr), run_time=0.5)
        until(self, "the same logs")
        mp = VGroup(RoundedRectangle(corner_radius=0.32, width=3.2, height=1.5,
                                     fill_color=DARK_TOP, fill_opacity=1,
                                     stroke_width=0).move_to([-0.3, 0.85, 0]),
                    T("model", 36, color=CARD).move_to([-0.3, 0.85, 0]))
        a1 = flow((-3.1, 0.85), (-1.95, 0.85))
        gplay(self, Create(a1), FadeIn(mp), rt=0.55)
        ans = VGroup(Rectangle(width=2.9, height=1.6, fill_color=CARD, fill_opacity=1,
                               stroke_color=INK, stroke_width=4).move_to([4.0, 0.85, 0]),
                     T("one answer", 30).move_to([4.0, -0.3, 0]))
        a2 = flow((1.35, 0.85), (2.5, 0.85))
        self.play(Create(a2), FadeIn(ans), run_time=0.5)
        until(self, "No loop, no tools")
        dims = VGroup(*[VGroup(Circle(radius=0.5, stroke_color=DIM, stroke_width=5,
                                      fill_opacity=0).move_to([x, -1.65, 0]),
                               Line([x - 0.36, -1.29, 0], [x + 0.36, -2.01, 0], color=DIM, stroke_width=5),
                               T(n, 28, color=DIM).move_to([x, -2.6, 0]))
                        for n, x in [("loop", -3.0), ("tools", 0.0), ("checker", 3.0)]])
        gplay(self, FadeIn(dims), rt=0.5)
        finish(self)


class B21_FourNumbers(Scene):
    def construct(self):
        self.add(heading(EVAL))
        self.add(tag())
        xs = [-4.8, -1.6, 1.6, 4.8]
        until(self, "Four measurements")
        boxes = VGroup(*[Rectangle(width=2.75, height=2.3, fill_color=CARD, fill_opacity=1,
                                   stroke_color=INK, stroke_width=4).move_to([x, 0.55, 0])
                         for x in xs])
        caps = VGroup(*[Line([x - 1.375, 1.25, 0], [x + 1.375, 1.25, 0], color=GHOST,
                             stroke_width=4) for x in xs])
        nums = VGroup(*[T(str(i + 1), 26, color=DIM).move_to([x - 1.1, 1.52, 0])
                        for i, x in enumerate(xs)])
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in boxes], lag_ratio=0.1),
                  FadeIn(caps), FadeIn(nums), run_time=0.8)
        until(self, "the right cause")
        l1 = T("right cause", 30).move_to([-4.8, -0.95, 0])
        self.play(FadeIn(l1), FadeIn(check(-4.8, 0.35, 0.52, color=INK, w=9)), run_time=0.5)
        until(self, "I don't know")
        l2 = T("honest “I don’t know”", 28).move_to([-1.6, -0.95, 0])
        gplay(self, FadeIn(l2), FadeIn(check(-1.6, 0.35, 0.52, color=INK, w=9)), rt=0.55)
        until(self, "unsupported claims")
        l3 = T("unsupported", 30).move_to([1.6, -0.95, 0])
        z = T("0", 86, bold=True, color=TERRA).move_to([1.6, 0.4, 0])
        self.play(FadeIn(l3), FadeIn(z), run_time=0.55)
        until(self, "steps it burned")
        l4 = T("steps used", 30).move_to([4.8, -0.95, 0])
        bars = VGroup(*[Rectangle(width=0.3, height=0.35 + i * 0.32, fill_color=BAR2,
                                  fill_opacity=1, stroke_color=INK, stroke_width=2)
                        .move_to([4.05 + i * 0.5, -0.38 + (0.35 + i * 0.32) / 2, 0]) for i in range(4)])
        ax = Line([3.75, -0.38, 0], [5.85, -0.38, 0], color=INK, stroke_width=4)
        self.play(FadeIn(l4), FadeIn(bars), Create(ax), run_time=0.5)
        finish(self)


class B22_WhatCountsAsWorked(Scene):
    def construct(self):
        self.add(heading(EVAL))
        self.add(tag())
        base = -2.35
        until(self, "more correct causes")
        axis = Line([-5.3, base, 0], [5.3, base, 0], color=INK, stroke_width=5)
        vault = T("correct causes, held-out 10", 30).move_to([0.0, -2.72, 0])
        b1 = Rectangle(width=2.1, height=3.6, fill_color=BAR1, fill_opacity=1,
                       stroke_color=INK, stroke_width=4).move_to([-1.9, base + 1.8, 0])
        b2 = Rectangle(width=2.1, height=1.9, fill_color=BAR3, fill_opacity=1,
                       stroke_color=INK, stroke_width=4).move_to([1.9, base + 0.95, 0])
        n1 = T("TraceCase", 30).move_to([-1.9, 1.7, 0])
        n2 = T("baseline", 30).move_to([1.9, -0.1, 0])
        self.play(Create(axis), FadeIn(vault), run_time=0.4)
        self.play(FadeIn(b1, shift=UP * 0.3), FadeIn(b2, shift=UP * 0.3), FadeIn(n1), FadeIn(n2),
                  run_time=0.7)
        until(self, "no unsupported claim")
        ruleline = DashedLine([-5.3, 0.55, 0], [5.3, 0.55, 0], color=TERRA, stroke_width=7,
                              dash_length=0.22)
        gplay(self, Create(ruleline), rt=0.45)
        until(self, "guessing more often")
        ar = flow((4.5, -1.6), (4.5, 1.1), color=DIM)
        gl = T("guess more", 28, color=DIM).move_to([4.9, 1.6, 0])
        self.play(Create(ar), FadeIn(gl), run_time=0.45)
        self.play(Create(xmark(4.5, -0.3, 0.4, 9).set_color(TERRA)), run_time=0.35)
        finish(self)


class B23_SafetyTest(Scene):
    def construct(self):
        self.add(heading(EVAL))
        self.add(tag())
        until(self, "pass or fail", lead=0.9)
        post, arm, pv = gate(0.9, -2.4, 2.6)
        self.play(FadeIn(shadow(0.95, -2.46, 1.2)), FadeIn(post), FadeIn(arm), run_time=0.45)
        until(self, "Approve fix A")
        ca = letter_card(-3.5, 0.55, "A", 2.2, 2.7)
        sl = seal(-1.3, 1.9, 0.42)
        sa = flow((-1.55, 1.55), (-2.1, 1.1))
        self.play(FadeIn(ca, shift=UP * 0.2), FadeIn(sl, scale=0.6), Create(sa), run_time=0.6)
        until(self, "swap in fix B")
        cb = letter_card(-3.5, 0.55, "B", 2.2, 2.7)
        gplay(self, FadeOut(ca, shift=LEFT * 0.6), FadeIn(cb, shift=RIGHT * 0.6), rt=0.55)
        crack = VGroup(Line([-1.55, 1.58, 0], [-1.18, 2.05, 0], color=CARD, stroke_width=6),
                       Line([-1.18, 2.05, 0], [-1.4, 2.3, 0], color=CARD, stroke_width=6))
        self.play(Create(crack), run_time=0.3)
        until(self, "must refuse")
        xm = xmark(3.9, 0.75, 0.56, 12).set_color(TERRA)
        rl = T("refused", 32).move_to([3.9, -0.35, 0])
        self.play(Create(xm), FadeIn(rl), run_time=0.45)
        finish(self)


class B24_Status(Scene):
    def construct(self):
        self.add(heading(EVAL))
        sh1 = Line([-5.9, -1.75, 0], [5.9, -1.75, 0], color=DIM, stroke_width=8)
        sh2 = Line([-5.9, 1.05, 0], [5.9, 1.05, 0], color=DIM, stroke_width=8)
        self.add(sh1, sh2)
        until(self, "Where it stands")
        e1 = Iso(-3.4, -1.62, 1.0).page(-0.45, -0.45, 0.3, 0.9, 1.1)
        e2 = VGroup(Circle(radius=0.62, stroke_color=INK, stroke_width=7, fill_color=CARD,
                           fill_opacity=1).move_to([-0.5, -1.05, 0]),
                    Circle(radius=0.3, fill_color=INK, fill_opacity=1,
                           stroke_width=0).move_to([-0.5, -1.05, 0]))
        e3 = Iso(2.6, -1.55, 0.95).page(-0.45, -0.45, 0.3, 0.9, 1.1)
        el = T("exists", 34).move_to([-5.1, -2.35, 0])
        # Name the three objects. The disc is this film, and nothing else on screen says so: it is the
        # one object in the whole reel that appears once and belongs to no recurring cast.
        enames = VGroup(T("brief", 30, color=DIM).move_to([-3.4, -2.35, 0]),
                        T("film", 30, color=DIM).move_to([-0.5, -2.35, 0]),
                        T("plan", 30, color=DIM).move_to([2.6, -2.35, 0]))
        self.play(FadeIn(e1, shift=UP * 0.2), FadeIn(e2, shift=UP * 0.2),
                  FadeIn(e3, shift=UP * 0.2), FadeIn(el), FadeIn(enames), run_time=0.7)
        until(self, "No TraceCase code")
        gl = T("will exist", 34, color=DIM).move_to([-5.1, 0.45, 0])
        ghosts = VGroup(*[DashedVMobject(Rectangle(width=1.9, height=1.3, stroke_color=DIM,
                                                   stroke_width=4).move_to([x, 1.95, 0]),
                                         num_dashes=18) for x in (-2.4, -0.1, 2.2, 4.5)])
        gnames = VGroup(*[T(n, 32, color=DIM).move_to([x, 1.95, 0]) for n, x in
                          [("service", -2.4), ("agent", -0.1), ("gate", 2.2), ("report", 4.5)]])
        gplay(self, FadeIn(gl), LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.1),
              FadeIn(gnames), rt=1.0)
        until(self, "going to build")
        # The wordmark sits in the empty band between the two shelves. On the "exists" shelf it read as
        # a label for the row — saying TraceCase exists, in the beat that says it does not.
        self.play(FadeIn(T("TraceCase", 40).move_to([0.0, 0.25, 0])), run_time=0.4)
        finish(self)
