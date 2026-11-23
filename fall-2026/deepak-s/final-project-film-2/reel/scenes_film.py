"""
scenes_film.py: CueGate film 2 (the project film), Manim code. Deepak Kumaran T S, INFO 7375, 2026-11-23.

Written for this film only; it contains no toolkit code. It is not runnable by itself: build_scenes.py
puts the Brutalist show-tell kit's primitives and pacing helpers in front of it (from the pinned
brutalist.art checkout, at build time) and writes scenes.py, the single file the toolkit's runner and
Gate A read. Names used here and defined by the kit: T, paper, check, cursor, ease_in, finish, _elapsed,
_TARGET, _SHEET, and the palette constants (STAGE, INK, TERRA, DIM, GHOST, CARD, BOX_*, DARK_*, BAR1-3, C30).

Two speakers: every scene carries a speaker tag (DEEPAK or SKEPTIC) top left. The first SKEPTIC line
(B02) carries the full label "SKEPTIC · a voice I wrote to ask the hard questions". Every picture of
something not built yet carries CONSTRUCTED top right. No person is drawn anywhere.
"""

try:
    _SHEET_BEAT = {b["beat_id"]: b for b in _SHEET["beats"]}
except Exception:
    _SHEET_BEAT = {}


# ═════════════════════════════ helpers ═════════════════════════════
MID_MARGIN = 0.25        # keep every animation this far off the clip midpoint (GATE T and Gate V sample there)
EDGE = "#9C8462"         # deep kraft for connectors (ink connectors fuse objects into one "text" blob)


def _bid(self):
    return type(self).__name__.split("_")[0]


def gp(self, *anims, rt=0.5):
    """play(), but never across the clip midpoint: if the animation would overlap the guard window, wait it out."""
    target = _TARGET.get(_bid(self), 0)
    now = _elapsed(self)
    if target:
        lo, hi = target / 2 - MID_MARGIN, target / 2 + MID_MARGIN
        if now < hi and now + rt > lo:
            self.wait(hi - now)
    self.play(*anims, run_time=rt)


def say(self, phrase, lead=0.25):
    """Wait until `phrase` is spoken: the kit's until() rule (character share x the voice's length),
    shifted by any silence pad_audio.py put before the voice."""
    b = _SHEET_BEAT.get(_bid(self), {})
    n, target = b.get("narration_text", ""), _TARGET.get(_bid(self), 0)
    if not n or not target or phrase not in n:
        return
    pl, pt = float(b.get("pad_lead_s", 0) or 0), float(b.get("pad_tail_s", 0) or 0)
    speech = float(b.get("speech_s") or (target - pl - pt))
    gap = pl + speech * n.index(phrase) / len(n) - lead - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def L(s, x, y, size=36, color=INK, bold=False):
    return T(s, size, color, bold).move_to([x, y, 0])


def Lleft(s, x, y, size=34, bold=False):
    return T(s, size, INK, bold).move_to([x, y, 0], aligned_edge=LEFT)


def Lright(s, x, y, size=34, bold=False):
    return T(s, size, INK, bold).move_to([x, y, 0], aligned_edge=RIGHT)


def speaker(self, who, first=False):
    """The speaker tag, top left, on screen from the first frame."""
    s = "SKEPTIC · a voice I wrote to ask the hard questions" if first else who
    tag = Lleft(s, -6.0, 3.0, 32, bold=True)
    self.add(tag)
    return tag


def constructed(self, extra=""):
    tag = Lright("CONSTRUCTED" + extra, 6.0, 3.0, 32, bold=True)
    self.add(tag)
    return tag


def block(cx, cy, w, h, d=0.32, top=BOX_TOP, front=BOX_L, side=BOX_R, sw=4):
    """A 2.5-D block: front face centred on (cx, cy), with a top and a right side receding up-right."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    dx, dy = d * C30, d * 0.5
    f = Polygon([x0, y0, 0], [x1, y0, 0], [x1, y1, 0], [x0, y1, 0], fill_color=front, fill_opacity=1, stroke_color=INK, stroke_width=sw)
    t = Polygon([x0, y1, 0], [x1, y1, 0], [x1 + dx, y1 + dy, 0], [x0 + dx, y1 + dy, 0], fill_color=top, fill_opacity=1, stroke_color=INK, stroke_width=sw)
    s = Polygon([x1, y0, 0], [x1 + dx, y0 + dy, 0], [x1 + dx, y1 + dy, 0], [x1, y1, 0], fill_color=side, fill_opacity=1, stroke_color=INK, stroke_width=sw)
    return VGroup(f, t, s)


def dark_block(cx, cy, w, h, d=0.32):
    return block(cx, cy, w, h, d, DARK_TOP, DARK_L, DARK_R)


def cue_page(x, y, w=1.7, h=2.2, rows=4):
    """A subtitle file: a white sheet with grey cue rows (a short timecode bar and a longer text bar per cue)."""
    pg = paper(x, y, w, h)
    bars = VGroup()
    top = y + h / 2 - 0.42
    step = (h - 0.7) / max(1, rows - 1) if rows > 1 else 0
    for i in range(rows):
        yy = top - i * step
        bars.add(Rectangle(width=w * 0.22, height=0.14, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([x - w * 0.29, yy, 0]))
        bars.add(Rectangle(width=w * 0.5, height=0.14, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([x + w * 0.1, yy, 0]))
    return VGroup(pg, bars)


def film_frame(x, y, w=2.2, h=1.4):
    """A film frame: a DIM picture area in an ink frame, with a pale subtitle bar (grey outline) near its foot."""
    pic = Rectangle(width=w, height=h, fill_color=DIM, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    bar = Rectangle(width=w * 0.62, height=h * 0.16, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=2).move_to([x, y - h * 0.28, 0])
    return VGroup(pic, bar)


def gate(cx, cy, s=1.0):
    """The CueGate gate: two kraft posts and a lintel with one terracotta light on its top face."""
    pw, ph, span = 0.42 * s, 2.5 * s, 1.9 * s
    left = block(cx - span / 2, cy, pw, ph, 0.28 * s)
    right = block(cx + span / 2, cy, pw, ph, 0.28 * s)
    lintel = block(cx + 0.0, cy + ph / 2 + 0.18 * s, span + pw, 0.36 * s, 0.28 * s)
    light = Dot([cx + 0.12 * s, cy + ph / 2 + 0.43 * s, 0], radius=0.07 * s, color=TERRA)
    g = VGroup(left, right, lintel, light)
    g.light = light
    return g


def bars3(x, y, hs=(0.5, 0.8, 0.35), w=0.28, gap=0.12):
    cols = (BAR1, BAR2, BAR3)
    g = VGroup()
    for i, (h, c) in enumerate(zip(hs, cols)):
        g.add(Rectangle(width=w, height=h, fill_color=c, fill_opacity=1, stroke_width=0).move_to([x + i * (w + gap), y + h / 2, 0]))
    return g


def ghost_rect(x, y, w, h, color=DIM):
    return Rectangle(width=w, height=h, fill_opacity=0, stroke_color=color, stroke_width=3).move_to([x, y, 0])


def floor_line():
    return Line([-6.0, -3.05, 0], [6.0, -3.05, 0], color=GHOST, stroke_width=4)


def arrow(a, b, color=EDGE, w=6):
    """A straight connector with a small filled head, in deep kraft."""
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = b - a
    u = d / max(1e-6, float(np.linalg.norm(d)))
    n = np.array([-u[1], u[0], 0.0])
    tip = b
    base = b - u * 0.22
    head = Polygon(tip, base + n * 0.12, base - n * 0.12, fill_color=color, fill_opacity=1, stroke_width=0)
    return VGroup(Line(a, base, color=color, stroke_width=w), head)


def act_card(self, num, title):
    """Act card: the act number and title in ink, a rule that grows under them, one terracotta dot."""
    n = L(num, -5.0, 0.35, 110, bold=True)
    t = Lleft(title, -4.2, 0.35, 54, bold=True)
    self.add(n, t)
    rule = Line([-5.4, -0.75, 0], [4.6, -0.75, 0], color=INK, stroke_width=6)
    gp(self, Create(rule), rt=0.6)
    dot = Dot([4.95, -0.75, 0], radius=0.11, color=TERRA)
    gp(self, GrowFromCenter(dot), rt=0.3)
    return VGroup(n, t, rule, dot)


# ---- the 2x2 map (B10, B11) ----
MAP_O = (0.6, -0.25)


def map_parts():
    ox, oy = MAP_O
    ax = VGroup(Line([-3.4, oy, 0], [4.6, oy, 0], color=INK, stroke_width=5),
                Line([ox, -2.6, 0], [ox, 2.2, 0], color=INK, stroke_width=5))
    labs = VGroup(Lleft("one line at a time", -3.4, oy + 0.4, 32), Lright("whole file", 4.6, oy + 0.4, 32),
                  Lleft("meaning measured", ox + 0.25, 2.2, 32), Lleft("meaning assumed", ox + 0.25, -2.6, 32))
    tools = VGroup()
    for i, name in enumerate(("Subtitle Edit", "Editsub", "EZTitles")):
        y = -1.1 - 0.5 * i
        tools.add(Dot([-2.1, y, 0], radius=0.11, color=INK), Lright(name, -2.4, y, 32))
    corner = Lleft("my reading", -6.0, 2.3, 32, bold=True)
    return ax, labs, tools, corner


# ---- the pipeline (B14) and its zoomed pair (B15, B16) ----
PIPE = [("Read", None), ("Frames", None), ("Check rules", None), ("Fix timing", None),
        ("Break lines", None), ("Ask local model", "(budget, must-keep)"), ("Check again", None), ("Ship", None)]
PIPE_X = (-4.6, -1.55, 1.5, 4.55)
PIPE_Y = (1.35, -1.15)


def pipe_box(i):
    x, y = PIPE_X[i % 4], PIPE_Y[i // 4]
    return block(x, y, 1.3, 0.75, 0.26)


def pipe_label(i):
    x, y = PIPE_X[i % 4], PIPE_Y[i // 4]
    name, sub = PIPE[i]
    g = VGroup(L(name, x, y - 0.75, 32))
    if sub:
        g.add(L(sub, x, y - 1.15, 32))
    return g


def pipe_light(i):
    x, y = PIPE_X[i % 4], PIPE_Y[i // 4]
    return Dot([x + 0.12, y + 0.5, 0], radius=0.09, color=TERRA)


PAIR = {"ask": (-2.6, 0.9), "check": (2.4, 0.9)}


def pair_parts():
    (ax, ay), (cx, cy) = PAIR["ask"], PAIR["check"]
    ask, chk = block(ax, ay, 2.2, 1.2, 0.34), block(cx, cy, 2.2, 1.2, 0.34)
    la = VGroup(L("Ask local model", ax, ay - 1.0, 34), L("(budget, must-keep)", ax, ay - 1.45, 32))
    lc = L("Check again", cx, cy - 1.0, 34)
    link = arrow([ax + 1.25, ay, 0], [cx - 1.25, cy, 0])
    return ask, chk, la, lc, link


# ═════════════════════════════ scenes ═════════════════════════════

class B02_Shift(Scene):
    """E2a. The source line and the real reply side by side; hedged opinion vs flat refusal."""
    def construct(self):
        speaker(self, "SKEPTIC", first=True)
        self.add(floor_line())
        h1, h2 = L("asked", -3.3, 2.2, 36, bold=True), L("got back", 3.3, 2.2, 36, bold=True)
        src = VGroup(T("I really don't think we", 34), T("should go in there tonight,", 34), T("not after what happened.", 34)).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([-3.3, 0.7, 0])
        rep = VGroup(T("Not in there tonight,", 34), T("not after that.", 34)).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([3.3, 0.95, 0])
        div = Line([0.0, -0.9, 0], [0.0, 2.3, 0], color=GHOST, stroke_width=4)
        self.add(h1, h2, src, rep)
        gp(self, Create(div), rt=0.3)
        hedge = Rectangle(width=5.0, height=0.16, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-3.3, -0.95, 0])
        flat = Rectangle(width=3.2, height=0.16, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([3.1, -0.6, 0])
        gp(self, GrowFromEdge(hedge, LEFT), GrowFromEdge(flat, LEFT), rt=0.35)
        l1, l2 = L("hedged opinion", -3.3, -1.6, 34), L("flat refusal", 3.1, -1.25, 34)
        gp(self, FadeIn(l1), FadeIn(l2), rt=0.25)
        finish(self)


class B03_Clock(Scene):
    """E2b. A stopwatch over a subtitle bar; a subtitle file bounces back off a QC wall; a cursor on one line."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        fr = film_frame(-3.4, -1.0, 4.0, 2.3)
        gp(self, FadeIn(fr), rt=0.4)
        say(self, "Streaming platforms")
        face = Circle(radius=1.0, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=6).move_to([-3.4, 1.3, 0])
        crown = Rectangle(width=0.3, height=0.22, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([-3.4, 2.41, 0])
        hand = Line([-3.4, 1.3, 0], [-3.4, 2.05, 0], color=INK, stroke_width=7)
        gp(self, FadeIn(face), FadeIn(crown), Create(hand), rt=0.4)
        gp(self, Rotate(hand, angle=-2.2, about_point=np.array([-3.4, 1.3, 0])), rt=1.0)
        say(self, "delivery guides")
        wall = dark_block(4.6, -0.3, 0.6, 4.2, 0.3)
        lw = L("QC", 4.6, 2.35, 40, bold=True)
        gp(self, FadeIn(wall, shift=UP * 0.15), FadeIn(lw), rt=0.4)
        pg = cue_page(0.6, -0.4, 1.3, 1.7, 3)
        gp(self, FadeIn(pg, shift=RIGHT * 0.2), rt=0.3)
        gp(self, pg.animate.move_to([3.4, -0.4, 0]), rt=0.6)
        gp(self, pg.animate.move_to([0.9, -0.9, 0]), rt=0.6)
        back = L("sent back", 0.9, -2.4, 34)
        gp(self, FadeIn(back), rt=0.3)
        say(self, "a person does")
        cur = cursor(-1.6, -2.0)
        gp(self, FadeIn(cur), rt=0.3)
        gp(self, cur.animate.move_to([-3.2, -1.6, 0]), rt=0.6)
        finish(self)


class B04_Gate(Scene):
    """E3. Subtitle file and film in; the gate; a clean file out; one line goes to the side door, back to a person."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        pg = cue_page(-5.0, 0.7, 1.4, 1.8, 3)
        fr = film_frame(-5.0, -1.25, 1.6, 1.0)
        gp(self, FadeIn(pg, shift=RIGHT * 0.2), FadeIn(fr, shift=RIGHT * 0.2), rt=0.5)
        say(self, "You give it")
        lin = L("subtitles + film", -4.7, -2.3, 32)
        gp(self, FadeIn(lin), rt=0.3)
        g = gate(-0.3, 0.1, 1.0)
        lg = L("CueGate", -0.3, 2.55, 40, bold=True)
        gp(self, FadeIn(g, shift=UP * 0.2), FadeIn(lg), rt=0.5)
        say(self, "It will hand back")
        out = cue_page(-2.8, 0.4, 1.3, 1.7, 3)
        gp(self, FadeIn(out), rt=0.3)
        gp(self, out.animate.move_to([3.6, 0.6, 0]), rt=1.0)
        ok = check(4.75, 1.85, 0.24)
        lo = L("fits the rules", 3.6, -0.75, 32)
        gp(self, Create(ok), FadeIn(lo), rt=0.4)
        say(self, "anything it can't fix")
        door = block(1.2, -2.35, 1.5, 0.55)
        ld = Lleft("back to a person", 2.4, -2.35, 32)
        gp(self, FadeIn(door, shift=UP * 0.15), FadeIn(ld), rt=0.4)
        stray = Rectangle(width=0.8, height=0.14, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-1.6, -0.6, 0])
        gp(self, FadeIn(stray), rt=0.2)
        gp(self, stray.animate.move_to([1.1, -1.95, 0]), rt=0.7)
        finish(self)


class B05_Button(Scene):
    """E4a. The gate, with a small AI button floating beside it."""
    def construct(self):
        speaker(self, "SKEPTIC")
        constructed(self)
        self.add(floor_line())
        g = gate(-1.4, 0.0, 1.0)
        lg = L("CueGate", -1.4, 2.45, 40, bold=True)
        self.add(g, lg)
        btn = block(2.8, 0.5, 1.6, 0.6, 0.26)
        lb = L("AI button", 2.9, -0.4, 34)
        gp(self, FadeIn(btn, shift=UP * 0.3), FadeIn(lb), rt=0.5)
        cur = cursor(4.4, -0.2)
        gp(self, FadeIn(cur), rt=0.3)
        finish(self)


class B06_Card(Scene):
    """E4b. A blank report card: meaning changed __ of 100; it goes up on a board."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        card = paper(-2.2, 0.1, 3.4, 4.0)
        gp(self, FadeIn(card, shift=DOWN * 0.3), rt=0.5)
        rows = VGroup(*[Rectangle(width=w, height=0.16, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([-2.2 - (2.4 - w) / 2, 1.4 - 0.5 * i, 0])
                        for i, w in enumerate((2.4, 1.9, 2.2))])
        gp(self, FadeIn(rows), rt=0.3)
        say(self, "measure how often")
        box = Rectangle(width=1.0, height=0.7, fill_opacity=0, stroke_color=INK, stroke_width=5).move_to([-2.2, -0.9, 0])
        gp(self, Create(box), rt=0.4)
        l1 = Lleft("meaning changed:", 0.1, -0.55, 36)
        l2 = Lleft("__ of 100", 0.1, -1.2, 36, bold=True)
        gp(self, FadeIn(l1), FadeIn(l2), rt=0.4)
        say(self, "publish that number")
        pin = Dot([-2.2, 2.0, 0], radius=0.11, color=TERRA)
        gp(self, GrowFromCenter(pin), rt=0.3)
        finish(self)


class B07_Act2(Scene):
    """I1. Act card 2 · WHAT ALREADY EXISTS."""
    def construct(self):
        speaker(self, "SKEPTIC")
        act_card(self, "2", "WHAT ALREADY EXISTS")
        finish(self)


class B08_Tools(Scene):
    """I2. Three plain cards with tool names in text; a cursor on one line in each."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        xs = (-4.0, 0.0, 4.0)
        names = ("Subtitle Edit", "Editsub", "EZTitles")
        cards, hl = [], []
        for x in xs:
            pg = paper(x, 0.6, 2.8, 3.0)
            ls = VGroup(*[Rectangle(width=2.0, height=0.16, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([x, 1.5 - 0.55 * k, 0]) for k in (0, 2, 3)])
            h = Rectangle(width=2.2, height=0.36, fill_color=CARD, fill_opacity=1, stroke_color=BAR1, stroke_width=3).move_to([x, 1.5 - 0.55, 0])
            cards.append(VGroup(pg, ls))
            hl.append(h)
        say(self, "Subtitle Edit")
        gp(self, FadeIn(cards[0], shift=DOWN * 0.2), FadeIn(L(names[0], xs[0], -1.4, 36)),
           FadeIn(cards[1], shift=DOWN * 0.2), FadeIn(L(names[1], xs[1], -1.4, 36)), rt=0.5)
        say(self, "EZTitles")
        gp(self, FadeIn(cards[2], shift=DOWN * 0.2), FadeIn(L(names[2], xs[2], -1.4, 36)), rt=0.5)
        say(self, "a person picks")
        gp(self, *[FadeIn(h) for h in hl], rt=0.3)
        curs = VGroup(*[cursor(x + 0.9, 0.85) for x in xs])
        gp(self, LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in curs], lag_ratio=0.3), rt=0.6)
        finish(self)


class B09_Papers(Scene):
    """I3. Two paper cards: IWSLT 2019 (length control) and IWSLT 2020 (is 42 the answer); a speech-rhythm strip."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        say(self, "In 2019")
        p1 = cue_page(-5.0, 1.25, 1.1, 1.4, 3)
        t1 = VGroup(Lleft("Controlling the Output Length", -4.0, 1.75, 34),
                    Lleft("of Neural Machine Translation", -4.0, 1.25, 34),
                    Lleft("IWSLT 2019", -4.0, 0.7, 34, bold=True))
        gp(self, FadeIn(p1, shift=DOWN * 0.2), FadeIn(t1), rt=0.5)
        say(self, "In 2020")
        p2 = cue_page(-5.0, -1.45, 1.1, 1.4, 3)
        t2 = VGroup(Lleft("Is 42 the Answer to Everything in", -4.0, -0.95, 34),
                    Lleft("Subtitling-oriented Speech Translation?", -4.0, -1.45, 34),
                    Lleft("IWSLT 2020", -4.0, -2.0, 34, bold=True))
        gp(self, FadeIn(p2, shift=DOWN * 0.2), FadeIn(t2), rt=0.5)
        say(self, "Timing and the rhythm")
        hs = (0.3, 0.7, 0.5, 0.2, 0.9, 0.4, 0.6)
        wave = VGroup(*[Rectangle(width=0.14, height=h, fill_color=(BAR1, BAR2)[k % 2], fill_opacity=1, stroke_width=0).move_to([3.6 + 0.3 * k, -2.5 + h / 2, 0])
                        for k, h in enumerate(hs)])
        gp(self, LaggedStart(*[GrowFromEdge(w, DOWN) for w in wave], lag_ratio=0.15), rt=0.6)
        finish(self)


class B10_Map(Scene):
    """I4a. The 2x2 map: one line at a time to whole file, meaning assumed to measured; three tools on the left."""
    def construct(self):
        speaker(self, "SKEPTIC")
        self.add(floor_line())
        ax, labs, tools, corner = map_parts()
        self.add(labs, corner)
        gp(self, Create(ax), rt=0.4)
        gp(self, FadeIn(tools), rt=0.3)
        finish(self)


class B11_Gap(Scene):
    """I4b. The same map; a hollow dot appears top right: CueGate (will)."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        ax, labs, tools, corner = map_parts()
        self.add(ax, labs, tools, corner)
        say(self, "how often")
        q = Lleft("published?", 0.85, 1.65, 32)
        gp(self, FadeIn(q), rt=0.3)
        say(self, "That's the gap")
        ring = Circle(radius=0.22, fill_opacity=0, stroke_color=INK, stroke_width=6).move_to([3.2, 1.6, 0])
        lab = L("CueGate (will)", 3.2, 1.05, 34, bold=True)
        gp(self, GrowFromCenter(ring), FadeIn(lab), rt=0.5)
        finish(self)


class B12_Act3(Scene):
    """M1. Act card 3 · HOW."""
    def construct(self):
        speaker(self, "SKEPTIC")
        act_card(self, "3", "HOW")
        finish(self)


class B13_Funnel(Scene):
    """M2. Two inputs into a funnel; a vice squeezes a timeline; out comes a test set with the originals known."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        fun = Polygon([-1.7, 1.7, 0], [-1.7, -1.7, 0], [-0.2, -0.35, 0], [-0.2, 0.35, 0],
                      fill_color=BOX_L, fill_opacity=1, stroke_color=INK, stroke_width=4)
        gp(self, FadeIn(fun), rt=0.4)
        say(self, "Tears of Steel")
        pa = cue_page(-5.2, 1.5, 0.9, 1.1, 2)
        la = VGroup(Lleft("Tears of Steel subtitles", -5.95, 0.6, 32), Lleft("(licence to confirm)", -5.95, 0.2, 32))
        gp(self, FadeIn(pa, shift=DOWN * 0.2), FadeIn(la), rt=0.4)
        say(self, "my own dialogue")
        pb = cue_page(-5.2, -0.95, 0.9, 1.1, 2)
        lb = VGroup(Lleft("my own lines", -5.95, -1.85, 32), Lleft("(synthetic)", -5.95, -2.25, 32))
        gp(self, FadeIn(pb, shift=DOWN * 0.2), FadeIn(lb), rt=0.4)
        say(self, "squeeze")
        tl = VGroup(*[Rectangle(width=0.36, height=0.3, fill_color=(BAR1, BAR2)[k % 2], fill_opacity=1, stroke_width=0).move_to([1.05 + 0.44 * k, 0.0, 0]) for k in range(5)])
        jl, jr = block(0.3, 0.0, 0.4, 1.1, 0.2), block(3.7, 0.0, 0.4, 1.1, 0.2)
        lv = L("timing squeezed", 1.95, -1.6, 32)
        gp(self, FadeIn(tl), FadeIn(jl), FadeIn(jr), FadeIn(lv), rt=0.4)
        gp(self, jl.animate.shift(RIGHT * 0.35), jr.animate.shift(LEFT * 0.35), tl.animate.scale(0.82), rt=0.6)
        say(self, "That gives me")
        stack = VGroup(*[cue_page(5.0 + 0.1 * k, 0.7 + 0.1 * k, 1.1, 1.4, 3) for k in range(3)])
        lo = VGroup(L("test set,", 5.0, -0.45, 32), Lright("originals known", 6.1, -0.9, 32))
        gp(self, LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in stack], lag_ratio=0.25), FadeIn(lo), rt=0.6)
        finish(self)


class B14_Pipeline(Scene):
    """M3. The hero diagram: eight boxes left to right in two rows; each lights up as it is named."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        boxes = [pipe_box(i) for i in range(8)]
        labels = [pipe_label(i) for i in range(8)]
        links = VGroup(*[arrow([PIPE_X[k] + 0.75, PIPE_Y[r], 0], [PIPE_X[k + 1] - 0.72, PIPE_Y[r], 0]) for r in (0, 1) for k in range(3)])
        turn = VGroup(Line([5.45, 1.35, 0], [5.75, 1.35, 0], color=EDGE, stroke_width=6),
                      Line([5.75, 1.35, 0], [5.75, 0.05, 0], color=EDGE, stroke_width=6),
                      Line([5.75, 0.05, 0], [-5.75, 0.05, 0], color=EDGE, stroke_width=6),
                      Line([-5.75, 0.05, 0], [-5.75, -1.15, 0], color=EDGE, stroke_width=6),
                      arrow([-5.75, -1.15, 0], [-5.3, -1.15, 0]))
        gp(self, LaggedStart(*[FadeIn(VGroup(b, l)) for b, l in zip(boxes, labels)], lag_ratio=0.12), rt=1.0)
        gp(self, Create(links), Create(turn), rt=0.5)
        cues = ("Read the file", "exact frames", "Check every rule", "Fix timing first", "changes no words",
                "go to a small open model", "comes back through", None)
        for i, phrase in enumerate(cues):
            if phrase:
                say(self, phrase)
            gp(self, GrowFromCenter(pipe_light(i)), rt=0.3)
        finish(self)


class B15_Fail(Scene):
    """M4a. Ask local model and Check again; the check fails: a cross, and the light flashes."""
    def construct(self):
        speaker(self, "SKEPTIC")
        constructed(self)
        self.add(floor_line())
        ask, chk, la, lc, link = pair_parts()
        self.add(ask, chk, la, lc, link)
        cx, cy = PAIR["check"]
        x = Cross(stroke_color=INK, stroke_width=8).scale(0.3).move_to([cx + 1.7, cy + 0.9, 0])
        light = Dot([cx + 0.15, cy + 0.78, 0], radius=0.12, color=TERRA)
        gp(self, Create(x), GrowFromCenter(light), rt=0.4)
        finish(self)


class B16_Loop(Scene):
    """M4b. A loop arrow back to Ask local model, three ticks for three tries; then a branch down to back to a person."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        ask, chk, la, lc, link = pair_parts()
        self.add(ask, chk, la, lc, link)
        (ax, ay), (cx, cy) = PAIR["ask"], PAIR["check"]
        loop = ArcBetweenPoints(np.array([cx, cy + 0.95, 0]), np.array([ax + 0.3, ay + 0.95, 0]), angle=1.0, color=INK, stroke_width=6)
        tip = Polygon([ax + 0.3, ay + 0.9, 0], [ax + 0.05, ay + 1.25, 0], [ax + 0.6, ay + 1.25, 0], fill_color=INK, fill_opacity=1, stroke_width=0)
        gp(self, Create(loop), FadeIn(tip), rt=0.6)
        ticks = VGroup(*[Dot([-0.6 + 0.6 * k, 0.4, 0], radius=0.1, color=TERRA) for k in range(3)])
        lt = L("three tries", 0.0, 1.4, 34)
        gp(self, LaggedStart(*[GrowFromCenter(t) for t in ticks], lag_ratio=0.3), FadeIn(lt), rt=0.6)
        say(self, "After that")
        branch = arrow([cx, cy - 1.3, 0], [cx, -1.9, 0])
        door = block(cx, -2.35, 1.5, 0.55)
        ld = Lright("back to a person", cx - 1.0, -2.35, 34)
        gp(self, Create(branch), FadeIn(door, shift=UP * 0.15), FadeIn(ld), rt=0.5)
        say(self, "fails closed")
        line = Rectangle(width=0.8, height=0.14, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([cx + 1.6, -1.0, 0])
        gp(self, FadeIn(line), rt=0.2)
        gp(self, line.animate.move_to([cx, -1.95, 0]), rt=0.5)
        finish(self)


CHECK_ROWS = ("model access", "compute", "data", "accounts")
CHECK_Y = (1.6, 0.5, -0.6, -1.7)


def check_rows():
    boxes = VGroup(*[Square(side_length=0.55, fill_color=CARD, fill_opacity=1, stroke_color=INK, stroke_width=5).move_to([-5.3, y, 0]) for y in CHECK_Y])
    labs = VGroup(*[Lleft(w, -4.75, y, 36) for w, y in zip(CHECK_ROWS, CHECK_Y)])
    return boxes, labs


class B17_List(Scene):
    """M5a. A checklist with four rows: model access, compute, data, accounts."""
    def construct(self):
        speaker(self, "SKEPTIC")
        self.add(floor_line())
        boxes, labs = check_rows()
        self.add(labs)
        gp(self, LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.2), rt=0.6)
        finish(self)


class B18_Have(Scene):
    """M5b. The same checklist, each row ticked or left open as RESOURCES.md says."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        boxes, labs = check_rows()
        self.add(boxes, labs)
        notes = ("no API key needed; model not chosen", "MacBook Pro, M3 Pro, 36 GB, no cloud",
                 "licence not confirmed; synthetic fallback", "GitHub; no other account needed")
        ticked = (False, True, False, True)
        cues = ("No API key", "Compute is", "The subtitle licence", "public models that download")
        for i in range(4):
            say(self, cues[i])
            y = CHECK_Y[i]
            n = Lleft(notes[i], -1.2, y, 34)
            mark = check(-5.32, y + 0.02, 0.2) if ticked[i] else Line([-5.5, y, 0], [-5.1, y, 0], color=BAR1, stroke_width=6)
            gp(self, Create(mark), FadeIn(n), rt=0.4)
        say(self, "freeing disk space")
        disk = Lleft("free disk space first", -1.2, -2.6, 32)
        gp(self, FadeIn(disk), rt=0.3)
        finish(self)


class B19_Act4(Scene):
    """V1. Act card 4 · DID IT WORK?"""
    def construct(self):
        speaker(self, "SKEPTIC")
        act_card(self, "4", "DID IT WORK?")
        finish(self)


class B20_Board(Scene):
    """V2. A scoreboard: four versions by two measures. Every cell empty; no results yet."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self, " · no results yet")
        self.add(floor_line())
        cx = (0.9, 4.1)
        heads = VGroup(L("rule breaks", cx[0], 2.3, 34, bold=True), L("shipped", cx[0], 1.85, 34, bold=True),
                       L("meaning changed", cx[1], 2.3, 34, bold=True), L("of 100", cx[1], 1.85, 34, bold=True))
        gp(self, FadeIn(heads), rt=0.4)
        rows = ("cut at budget", "one model call", "CueGate, no meaning check", "full CueGate")
        cues = ("A dumb cut", "A single", "CueGate without", "And full CueGate")
        ys = (1.0, 0.0, -1.0, -2.0)
        for r, (name, cue, y) in enumerate(zip(rows, cues, ys)):
            say(self, cue)
            gp(self, FadeIn(Lright(name, -0.6, y, 34)), Create(ghost_rect(cx[0], y, 2.4, 0.7, INK)), rt=0.35)
        say(self, "label a hundred")
        gp(self, LaggedStart(*[Create(ghost_rect(cx[1], y, 2.4, 0.7, INK)) for y in ys], lag_ratio=0.2), rt=0.7)
        finish(self)


class B21_Verdict(Scene):
    """V3. WORKED IF (zero rule breaks; less meaning change than one model call) and FAILED IF (same meaning change; most lines sent back)."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        div = Line([0.0, -2.7, 0], [0.0, 2.4, 0], color=GHOST, stroke_width=5)
        h1, h2 = L("WORKED IF", -3.1, 2.2, 44, bold=True), L("FAILED IF", 3.1, 2.2, 44, bold=True)
        self.add(h1, h2)
        gp(self, Create(div), rt=0.4)
        items = [("zero rule breaks", None, True, -3.1, 0.9, "zero rule breaks"),
                 ("less meaning change than", "one model call", True, -3.1, -0.5, "changes meaning less often"),
                 ("same meaning change", None, False, 3.1, 0.9, "just as often"),
                 ("most lines sent back", None, False, 3.1, -0.5, "sends most lines back")]
        for a, b, ok, x, y, cue in items:
            say(self, cue)
            mark = check(x - 2.55, y + 0.05, 0.2) if ok else Cross(stroke_color=INK, stroke_width=7).scale(0.2).move_to([x - 2.5, y, 0])
            txt = VGroup(Lleft(a, x - 2.1, y, 34))
            if b:
                txt.add(Lleft(b, x - 2.1, y - 0.45, 34))
            gp(self, Create(mark), FadeIn(txt), rt=0.4)
        finish(self)


class B22_Lens(Scene):
    """V4a. Who checks the checker: a magnifying glass slides over the meaning check box."""
    def construct(self):
        speaker(self, "SKEPTIC")
        constructed(self)
        self.add(floor_line())
        box = block(-0.6, -0.2, 2.4, 1.3, 0.34)
        lb = L("meaning check", -0.6, -1.4, 36)
        self.add(box, lb)
        ring = Circle(radius=1.1, fill_opacity=0, stroke_color=INK, stroke_width=9).move_to([3.3, 1.2, 0])
        handle = Line([4.1, 0.4, 0], [5.0, -0.5, 0], color=INK, stroke_width=16)
        gp(self, FadeIn(VGroup(ring, handle)), rt=0.3)
        gp(self, VGroup(ring, handle).animate.shift(LEFT * 3.2 + DOWN * 1.0), rt=0.6)
        spark = Dot([-0.45, 0.62, 0], radius=0.1, color=TERRA)
        gp(self, GrowFromCenter(spark), rt=0.3)
        finish(self)


class B23_Tally(Scene):
    """V4b. A tally sheet with one empty total; it goes into the report."""
    def construct(self):
        speaker(self, "DEEPAK")
        constructed(self)
        self.add(floor_line())
        sheet = paper(-2.6, 0.2, 3.4, 4.2)
        gp(self, FadeIn(sheet, shift=DOWN * 0.3), rt=0.4)
        lab = Lleft("waved through", -0.6, 1.5, 36)
        gp(self, FadeIn(lab), rt=0.3)
        rows = VGroup(*[Rectangle(width=2.4, height=0.14, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([-2.6, 1.5 - 0.5 * k, 0]) for k in range(4)])
        gp(self, LaggedStart(*[GrowFromEdge(r, LEFT) for r in rows], lag_ratio=0.2), rt=0.6)
        say(self, "That number")
        tot = Rectangle(width=1.1, height=0.7, fill_opacity=0, stroke_color=INK, stroke_width=5).move_to([-2.6, -1.2, 0])
        lt = Lleft("total: __", -0.6, -1.2, 36, bold=True)
        gp(self, Create(tot), FadeIn(lt), rt=0.4)
        say(self, "in the report")
        rep = cue_page(4.6, 0.2, 1.5, 2.0, 4)
        lr = L("report", 4.6, -1.3, 34)
        gp(self, FadeIn(rep, shift=LEFT * 0.3), FadeIn(lr), rt=0.4)
        finish(self)


class B24_Columns(Scene):
    """V5a. Two columns: EXISTS and WILL."""
    def construct(self):
        speaker(self, "SKEPTIC")
        self.add(floor_line())
        h1, h2 = L("EXISTS", -3.1, 2.2, 44, bold=True), L("WILL", 3.1, 2.2, 44, bold=True)
        self.add(h1, h2)
        div = Line([0.0, -2.7, 0], [0.0, 2.4, 0], color=GHOST, stroke_width=5)
        gp(self, Create(div), rt=0.4)
        finish(self)


EXISTS_ROWS = (("the plan", "14 Oct 2026"), ("the research", "14 Oct 2026"), ("the Claude reply", "14 Oct 2026"))
WILL_ROWS = ("rule checker", "timing fixer", "local model step", "meaning check", "evaluation")


class B25_Lists(Scene):
    """V5b. EXISTS: the three dated items. No CueGate code runs. WILL: the parts, as ghost outlines."""
    def construct(self):
        speaker(self, "DEEPAK")
        self.add(floor_line())
        h1, h2 = L("EXISTS", -3.1, 2.2, 44, bold=True), L("WILL", 3.1, 2.2, 44, bold=True)
        div = Line([0.0, -2.7, 0], [0.0, 2.4, 0], color=GHOST, stroke_width=5)
        self.add(h1, h2, div)
        say(self, "Today there's")
        for i, (what, when) in enumerate(EXISTS_ROWS):
            y = 1.3 - 1.05 * i
            gp(self, FadeIn(cue_page(-5.2, y, 0.5, 0.65, 2)), FadeIn(Lleft(what, -4.7, y + 0.15, 34)),
               FadeIn(Lleft(when, -4.7, y - 0.25, 32)), rt=0.3)
        say(self, "No CueGate code runs")
        nc = Lleft("no CueGate code runs", -5.45, -2.1, 34, bold=True)
        gp(self, FadeIn(nc), rt=0.3)
        say(self, "Everything else")
        ghosts = VGroup(*[ghost_rect(1.1, 1.2 - 0.85 * k, 0.55, 0.55) for k in range(5)])
        wl = VGroup(*[Lleft(w, 1.65, 1.2 - 0.85 * k, 34) for k, w in enumerate(WILL_ROWS)])
        gp(self, LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.15), FadeIn(wl), rt=0.6)
        finish(self)
