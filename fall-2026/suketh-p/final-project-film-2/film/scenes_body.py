
# ═════════════════════ FINE PRINT (final project film) — scene body (Claude Code, 2026-11-21) ═════════════════════
# Pasted after iso_kit.py, iso_originals_25.py and scene_data.py by build_scenes.py (Gate A copies only scenes.py).
# One drawing per beat, adapted from the October pitch film (Assignment 4/final-project-film/scenes_body.py): the
# same helpers (gplay, at, label, stamp), the toolkit's approved props, cream / ink / terracotta.
# Every beat shows its honesty stamp (top left) and its part tag (top right), both read from beat_sheet.json through
# ON_SCREEN in scene_data.py. The terminal replays (B08, B09, B10) draw only the rows in TERM, which
# make_scene_data.py builds from the saved logs in ../evidence/terminal/; nothing is typed here.
# Fill-only shapes carry stroke_opacity=0, so Gate B never reads an invisible edge as a line through a label.


def _bid(self):
    return type(self).__name__.split("_")[0]


def gplay(self, *anims, run_time=0.8):
    """self.play, held off the clip midpoint (GATE T and Gate V sample it) by a 0.3 s guard."""
    mid = _TARGET.get(_bid(self), 10.0) / 2.0
    now = _elapsed(self)
    if now < mid + 0.3 and now + run_time > mid - 0.3:
        self.wait(max(0.02, mid + 0.32 - now))
    self.play(*anims, run_time=run_time)


def at(self, phrase, lead=0.25):
    """Wait for a spoken phrase. A phrase missing from the narration stops the render (no silent drift)."""
    n = _NARR.get(_bid(self))
    if n is not None and phrase not in n:
        raise ValueError(f"{_bid(self)}: cue {phrase!r} is not in the narration")
    until(self, phrase, lead)


def label(s, x, y, size=44):
    t = T(s, size)
    t.move_to([x, y, 0])
    return t


def label_left(s, x0, y, size=44):
    t = T(s, size)
    t.move_to([x0, y, 0])
    t.align_to(np.array([x0, 0.0, 0.0]), LEFT)
    return t


def stamp(text):
    """The honesty stamp, top left: an ink dot for what ran or was checked, a terracotta dot for the plan."""
    dot = Dot([-5.95, 3.0, 0], radius=0.09, color=INK if text.startswith("real") else TERRA)
    return VGroup(dot, label_left(text, -5.72, 3.0, 36))


def part_tag(text):
    """The part tag, top right: which of the brief's four parts this beat belongs to."""
    t = T(text, 36)
    t.move_to([5.98, 3.0, 0])
    t.align_to(np.array([5.98, 0.0, 0.0]), RIGHT)
    return t


def chrome(self):
    st, part = ON_SCREEN.get(_bid(self), ("", ""))
    g = VGroup(*([stamp(st)] if st else []), *([part_tag(part)] if part else []))
    self.add(g)
    return g


def rect(x, y, w, h, fill, stroke=None, sw=3):
    """A plain rectangle; with no stroke colour it is fill-only (and its edge is invisible to Gate B too)."""
    if stroke is None:
        return Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_width=0,
                         stroke_opacity=0).move_to([x, y, 0])
    return Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_color=stroke,
                     stroke_width=sw).move_to([x, y, 0])


def floor_(x, y, w=3.6):
    """A soft landing shadow under a prop (a new non-text shape for Gate A)."""
    e = Ellipse(width=w, height=0.42, fill_color=GHOST, fill_opacity=1, stroke_width=0,
                stroke_opacity=0).move_to([x, y, 0])
    e.set_z_index(-1)
    return e


def page(x, y, w=1.05, h=1.35):
    """A posting page: the kit's paper() with its kraft shadow made edge-free."""
    pg = paper(x, y, w, h)
    pg[0].set_stroke(opacity=0)
    return pg


def rules_on(x, y, w, n=3, gap=0.3, color=GHOST, sw=6):
    """Grey text rules on a page (never type): n lines from y downward, the last one shorter."""
    return VGroup(*[Line([x - w / 2, y - i * gap, 0], [x + w / 2 - (0.18 if i == n - 1 else 0), y - i * gap, 0],
                         color=color, stroke_width=sw) for i in range(n)])


def cross(x, y, s=0.22, color=INK, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def slip(x, y, w=1.3, h=0.5, edge=INK):
    """A quote slip: a small white card with a kraft shadow and one grey rule (never type). B16 draws its slips
    with a grey edge, so the ink crack inside is not read by GATE T as a label printed inside another label."""
    sh = rect(x + 0.07, y - 0.07, w, h, BOX_L)
    card = rect(x, y, w, h, PAGE_TOP, edge, 3)
    rule = Line([x - w / 2 + 0.2, y, 0], [x + w / 2 - 0.2, y, 0], color=GHOST, stroke_width=5)
    return VGroup(sh, card, rule)


def tag(text, x0, y, size=36):
    """A status tag: a small grey square and its words beside it (never inside it)."""
    return VGroup(rect(x0 + 0.15, y, 0.3, 0.3, BAR1), label_left(text, x0 + 0.45, y, size))


def open_crate(h, x, y):
    """The kit's context crate with its lid off; whatever is set at z 1 sits inside it."""
    c = make_original("context-crate", height=h, x=x, y=y)
    c.remove(c.parts["lid"])
    c.parts["crate-front"].set_z_index(2)
    return c


def lens(x, y, r=0.46):
    """A reading lens: an ink ring with a handle, built from kit primitives."""
    ring = Circle(radius=r, stroke_color=INK, stroke_width=7, fill_color=PAGE_TOP, fill_opacity=0.2).move_to([x, y, 0])
    handle = Line([x + r * 0.72, y - r * 0.72, 0], [x + r * 1.6, y - r * 1.6, 0], color=INK, stroke_width=12)
    return VGroup(ring, handle)


# ── terminal replay: a light terminal window and rows of Menlo, sized from scene_data.py ──────────────────────────
TERM_PITCH = 0.38      # row pitch (units)
TERM_TOPBAR = 0.26     # title-bar height
TERM_PAD = 0.15


def term_window(cx, top, nrows):
    """White body with an ink outline, a white title bar ruled off in ink, three grey dots. Returns (group, first row y).

    Changed 2026-11-21 by Claude Code (main session): the grey title bar and kraft shadow were light "ink" to Gate V and
    pulled B08's ink/background separation to 0.23 (floor 0.30). Nothing shown in the window changed."""
    w = TERM_COLS * TERM_ADV + 0.30
    h = TERM_TOPBAR + 2 * TERM_PAD + nrows * TERM_PITCH
    cy = top - h / 2
    body = rect(cx, cy, w, h, PAGE_TOP, INK, 4)
    rule_y = top - TERM_TOPBAR - 0.02
    rule = Line([cx - w / 2, rule_y, 0], [cx + w / 2, rule_y, 0], color=INK, stroke_width=3)
    dots = VGroup(*[Dot([cx - w / 2 + 0.2 + i * 0.16, top - TERM_TOPBAR / 2 - 0.02, 0], radius=0.045, color=BAR2)
                    for i in range(3)])
    return VGroup(body, rule, dots), top - TERM_TOPBAR - TERM_PAD - TERM_PITCH / 2


def term_row(text, cx, y):
    """One terminal row. The row is set between two full-height bars so every row has the same box (equal
    baselines, columns on one grid); the bars are removed before the row is shown."""
    t = Text("│" + text.ljust(TERM_COLS) + "│", font=TERM_FONT, font_size=TERM_FS, color=INK)
    t.scale(TERM_K)
    t.move_to([cx, y, 0])
    t.remove(t[0], t[-1])
    return t


def term_height(bid, k):
    n = sum(len(l["rows"]) for l in TERM[bid][k]["lines"])
    return TERM_TOPBAR + 2 * TERM_PAD + n * TERM_PITCH


def term_block(bid, k, cx, top):
    """Window k of beat bid's replay: (window, one VGroup of rows per saved line)."""
    spec = TERM[bid][k]
    n = sum(len(l["rows"]) for l in spec["lines"])
    win, y0 = term_window(cx, top, n)
    groups, i = [], 0
    for l in spec["lines"]:
        g = VGroup()
        for r in l["rows"]:
            if r.strip():
                g.add(term_row(r, cx, y0 - i * TERM_PITCH))
            i += 1
        groups.append(g)
    return win, groups


# ──────────────────────────────────────────── B01 ────────────────────────────────────────────
class B01_EightPostings(Scene):
    def construct(self):
        chrome(self)
        xs = [-5.25 + 1.5 * i for i in range(8)]
        y = 0.55
        pages, rules, titles = VGroup(), [], VGroup()
        for x in xs:
            pg = page(x, y, 1.1, 1.4)
            ru = rules_on(x, y - 0.02, 0.72)
            pages.add(VGroup(pg, ru))
            rules.append(ru)
            titles.add(Line([x - 0.36, y + 0.4, 0], [x + 0.18, y + 0.4, 0], color=INK, stroke_width=10))
        self.add(pages)
        gplay(self, FadeIn(floor_(0.0, -0.4, 12.0)), run_time=0.4)
        at(self, "screened eight")
        gplay(self, FadeIn(label("8 real postings", 0.0, 1.85, 48)), run_time=0.5)
        at(self, "by title", lead=0.9)
        gplay(self, Create(titles), run_time=0.6)
        at(self, "When an AI reviewer")
        ln = lens(xs[0], y)
        gplay(self, FadeIn(ln), run_time=0.3)
        gplay(self, ln.animate.shift(RIGHT * (xs[-1] - xs[0])), run_time=1.6)
        gplay(self, FadeOut(ln), run_time=0.3)
        crossed = [0, 1, 2, 4, 5, 7]          # six of the eight; which six is not the claim
        at(self, "six asked")
        gplay(self, *[rules[i][1].animate.set_color(BAR1) for i in crossed],
              Create(VGroup(*[cross(xs[i], y - 0.32, s=0.24) for i in crossed])), run_time=0.5)
        at(self, "two to twelve-plus")
        gplay(self, FadeIn(label("6 of 8", -2.3, -1.6, 110)),
              FadeIn(label("2–12+ yrs or no new grads", 3.1, -1.6, 40)), run_time=0.6)
        finish(self)


# ──────────────────────────────────────────── B02 ────────────────────────────────────────────
class B02_FinePrint(Scene):
    def construct(self):
        chrome(self)
        lamp = make_original("inspection-lamp", height=3.0, x=-3.9, y=-0.55)
        self.add(lamp, label("Fine Print", -3.9, 1.6, 60))
        gplay(self, FadeIn(floor_(-3.7, -2.05, 3.4)), run_time=0.4)
        at(self, "read each new posting")
        gplay(self, lamp.parts["lamp-head"].animate.shift(lamp.action_vectors["lamp-head"]), run_time=0.9)
        at(self, "show me the exact sentence")
        gplay(self, FadeIn(slip(0.15, 0.3, w=2.3, h=0.62), shift=RIGHT * 0.6),
              FadeIn(label("exact sentence", 0.15, -0.5, 44)), run_time=0.8)
        at(self, "wait for my approval")
        st = make_original("approval-stamp", height=2.4, x=4.1, y=-0.75)
        gplay(self, FadeIn(st), FadeIn(floor_(4.1, -2.0, 3.2)), FadeIn(label("my approval", 4.1, 1.15, 44)),
              run_time=0.6)
        gplay(self, st.parts["stamp"].animate.shift(-st.action_vectors["stamp"] * 0.35), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B03 ────────────────────────────────────────────
class B03_NewPostings(Scene):
    def construct(self):
        chrome(self)
        xs = (-4.9, -3.1, -1.3)
        crates = [open_crate(1.3, x, -1.0) for x in xs]
        self.add(*crates)
        gplay(self, FadeIn(floor_(-3.1, -1.75, 5.6)), run_time=0.4)
        at(self, "In under two weeks")
        stacks = []
        for x, n in zip(xs, (5, 5, 1)):           # the counts: 83 and 88 are tall stacks, 1 is one sheet
            s = VGroup(*[page(x - 0.1 + 0.05 * k, -0.4 + 0.16 * k, 0.62, 0.78) for k in range(n)])
            s.set_z_index(1)
            stacks.append(s)
        gplay(self, LaggedStart(*[FadeIn(s, shift=UP * 0.4) for s in stacks], lag_ratio=0.3), run_time=1.2)
        gplay(self, *[FadeIn(label(t, x, -2.3, 44)) for t, x in zip(("83", "88", "1"), xs)], run_time=0.4)
        at(self, "one hundred seventy-two")
        gplay(self, FadeIn(label("172", -3.1, 1.9, 96)), FadeIn(label("not seen on Nov 8", -3.1, 1.15, 40)), run_time=0.6)
        at(self, "One piece of Fine Print")
        gplay(self, FadeIn(label("watcher: runs", -3.1, -2.95, 40)), run_time=0.5)
        lamp = make_original("inspection-lamp", height=2.4, x=3.6, y=-0.8)
        lamp.set_opacity(0.4)                     # the reader is drawn faint: it is next, not built
        gplay(self, FadeIn(lamp), FadeIn(floor_(3.75, -2.0, 2.8)), FadeIn(label("reader: next", 3.6, 0.85, 40)),
              run_time=0.7)
        finish(self)


# ──────────────────────────────────────────── B04 ────────────────────────────────────────────
class B04_Exists(Scene):
    def construct(self):
        chrome(self)
        binder = make_original("evidence-binder", height=2.0, x=-4.45, y=-0.75)
        self.add(binder, label("A3 recipe", -4.45, 0.85, 44))
        gplay(self, FadeIn(floor_(-4.45, -1.85, 3.2)), run_time=0.4)
        at(self, "couldn't tell fit")
        gplay(self, FadeIn(label("?", -2.6, -0.45, 110)), run_time=0.5)
        at(self, "On LinkedIn")
        px = (0.1, 2.05)
        gplay(self, FadeIn(VGroup(*[page(x, -0.5, 1.6, 2.4) for x in px]), shift=LEFT * 0.4), run_time=0.7)
        at(self, "Qualcomm and TikTok")
        gplay(self, FadeIn(label("Qualcomm · TikTok", 1.07, 1.3, 44)), run_time=0.5)
        rows = (0.3, -0.45, -1.2)
        at(self, "Both separated")
        blocks = VGroup(*[rect(x, rows[0], 1.2, 0.42, BAR2) for x in px], *[rect(x, rows[1], 1.2, 0.42, BAR3) for x in px])
        gplay(self, FadeIn(blocks), FadeIn(label_left("minimum", 3.25, rows[0], 40)),
              FadeIn(label_left("preferred", 3.25, rows[1], 40)), run_time=0.8)
        at(self, "Neither stated", lead=1.1)
        slots = VGroup(*[rect(x, rows[2], 1.2, 0.4, PAGE_TOP, BAR1, 3) for x in px])
        gplay(self, FadeIn(slots), FadeIn(label_left("sponsorship", 3.25, rows[2], 40)), run_time=0.4)
        finish(self)


# ──────────────────────────────────────────── B05 ────────────────────────────────────────────
def _h1b(x, y):          # approvals (dark) and denials (light) per employer: three pairs of bars
    g = VGroup()
    for i, (a, d) in enumerate(((0.55, 0.15), (0.72, 0.26), (0.4, 0.1))):
        bx = x - 0.36 + 0.36 * i
        g.add(rect(bx - 0.07, y - 0.4 + a / 2, 0.12, a, BAR1), rect(bx + 0.07, y - 0.4 + d / 2, 0.12, d, BAR2))
    return g


def _score(x, y):        # a score meter, and keyword chips with one missing
    g = VGroup(*[rect(x - 0.4 + 0.2 * i, y + 0.18, 0.16, 0.2, BAR1 if i < 3 else PAGE_TOP, None if i < 3 else BAR1, 2)
                 for i in range(5)])
    g.add(*[RoundedRectangle(width=0.3, height=0.15, corner_radius=0.07,
                             fill_color=GHOST if i < 2 else PAGE_TOP, fill_opacity=1,
                             stroke_color=BAR1 if i == 2 else GHOST, stroke_width=2).move_to([x - 0.34 + 0.34 * i, y - 0.22, 0])
            for i in range(3)])
    return g


def _reqpref(x, y):      # the two kinds kept apart
    return VGroup(rect(x, y + 0.2, 0.9, 0.28, BAR2), rect(x, y - 0.2, 0.9, 0.28, BAR3))


def _wording(x, y):      # skill found (check), exact wording missed (cross)
    return VGroup(Line([x - 0.45, y + 0.22, 0], [x + 0.12, y + 0.22, 0], color=GHOST, stroke_width=6),
                  check(x + 0.3, y + 0.22, s=0.13),
                  rect(x - 0.15, y - 0.24, 0.6, 0.17, PAGE_TOP, BAR1, 2),
                  cross(x + 0.35, y - 0.24, s=0.1, w=6))


class B05_Others(Scene):
    def construct(self):
        chrome(self)
        cells = [(-5.35, 1.0), (0.85, 1.0), (-5.35, -1.7), (0.85, -1.7)]
        words = [("H-1B approvals ·", "denials · per employer"), ("match score ·", "missing keywords"),
                 ("experience, education:", "required or preferred?"), ("skill found ·", "exact wording missed")]
        cues = ["Government H-1B", "Jobscan scores", "One paper flags", "And a 2024 study"]
        for (x, y), (l1, l2), cue, build in zip(cells, words, cues, (_h1b, _score, _reqpref, _wording)):
            at(self, cue)
            card = VGroup(page(x, y, 1.3, 1.15), build(x, y))
            gplay(self, FadeIn(card, shift=UP * 0.2),
                  FadeIn(VGroup(label_left(l1, x + 0.95, y + 0.27, 34), label_left(l2, x + 0.95, y - 0.27, 34))),
                  run_time=0.6)
        finish(self)


# ──────────────────────────────────────────── B06 ────────────────────────────────────────────
class B06_Adds(Scene):
    def construct(self):
        chrome(self)
        scan = make_original("checkpoint-scanner", height=2.3, x=-4.3, y=-0.95)
        st = make_original("approval-stamp", height=2.2, x=4.45, y=-0.9)
        self.add(scan, st, label("my approval", 4.45, 0.75, 40))
        gplay(self, FadeIn(floor_(-4.2, -2.15, 3.0)), FadeIn(floor_(4.45, -2.05, 3.0)), run_time=0.4)
        at(self, "Each requirement")
        gplay(self, FadeIn(slip(-4.3, 1.15, w=1.8, h=0.5), shift=DOWN * 0.3), run_time=0.6)
        at(self, "checked word for word", lead=1.0)
        gplay(self, scan.parts["parcel"].animate.shift(scan.action_vectors["parcel"]), run_time=0.9)
        gplay(self, Create(check(-2.85, 1.15, s=0.22)), run_time=0.4)
        at(self, "Required will stay")
        trays = make_original("comparison-trays", height=1.8, x=0.1, y=-1.0)
        gplay(self, FadeIn(trays), FadeIn(floor_(0.1, -1.95, 3.0)), FadeIn(label("required", -0.95, 0.45, 40)),
              FadeIn(label("preferred", 1.3, 0.45, 40)), run_time=0.7)
        at(self, "silence on sponsorship")
        gplay(self, FadeIn(tag("sponsorship: unknown", -1.75, 1.5, 40)), run_time=0.5)
        at(self, "nothing will reach")
        gplay(self, st.parts["stamp"].animate.shift(-st.action_vectors["stamp"] * 0.3), run_time=0.6)
        finish(self)


# ──────────────────────────────────────────── B07 ────────────────────────────────────────────
class B07_Data(Scene):
    def construct(self):
        chrome(self)
        xs = (-5.3, -4.4, -3.5)
        crates = [open_crate(0.95, x, -1.55) for x in xs]
        lamp = make_original("inspection-lamp", height=1.9, x=-4.4, y=1.15)      # October's plan: the reader alone
        lamp.set_opacity(0.4)                                                      # not built: drawn faint, tagged "plan"
        gate = make_original("permission-gate", height=2.0, x=0.0, y=-1.1)
        parcel = make_original("release-parcel", height=1.8, x=3.9, y=-1.15)
        parcel.parts["lid"].shift(parcel.action_vectors["lid"])                    # open, waiting for a response
        self.add(*crates, lamp, gate, parcel)
        gplay(self, FadeIn(floor_(-4.4, -2.2, 3.4)), FadeIn(floor_(0.0, -2.2, 2.6)), FadeIn(floor_(3.9, -2.2, 2.8)),
              run_time=0.4)
        at(self, "on top of jobwatch")
        gplay(self, lamp.animate.move_to([-4.4, -0.3, 0]), run_time=0.9)         # built on top of the watcher
        gplay(self, FadeIn(label("jobwatch", -4.4, -2.75, 40)), FadeIn(tag("plan", -5.0, 0.95, 34)), run_time=0.4)
        at(self, "three job boards")
        gplay(self, *[FadeIn(Dot([x, -1.82, 0], radius=0.07, color=TERRA)) for x in xs], run_time=0.4)
        at(self, "read only from an allow-list")
        feeds = [slip(-2.3, 0.05 - 0.42 * i, w=0.8, h=0.3) for i in range(4)]
        gplay(self, FadeIn(VGroup(*feeds)), FadeIn(label("allow-list", 0.0, 0.6, 40)),
              gate.parts["barrier"].animate.shift(gate.action_vectors["barrier"]), run_time=0.6)
        gplay(self, *[f.animate.move_to([2.6, -0.35 - 0.15 * i, 0]) for i, f in enumerate(feeds[:3])], run_time=0.9)
        gplay(self, Create(cross(-1.55, 0.05 - 0.42 * 3, s=0.14)), run_time=0.3)
        at(self, "with a fingerprint")
        gplay(self, parcel.parts["lid"].animate.shift(-parcel.action_vectors["lid"]),
              *[FadeOut(f) for f in feeds[:3]], run_time=0.6)
        gplay(self, FadeIn(Dot([3.9, -0.62, 0], radius=0.1, color=TERRA)), FadeIn(label("fingerprint", 3.9, 0.6, 40)),
              run_time=0.4)
        at(self, "The applicant is fictional", lead=1.5)
        card = VGroup(page(-1.9, 1.6, 0.8, 0.95), rules_on(-1.9, 1.72, 0.5, n=3, gap=0.22))
        gplay(self, FadeIn(card), FadeIn(label_left("fictional applicant", -1.3, 1.6, 40)), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B08 ────────────────────────────────────────────
class B08_LiveRun(Scene):
    def construct(self):
        chrome(self)
        w1, tests = term_block("B08", 0, 0.0, 2.62)
        w2, run = term_block("B08", 1, 0.0, 0.27)
        gplay(self, FadeIn(w1), run_time=0.35)
        at(self, "Claude Code ran it")
        gplay(self, FadeIn(tests[0]), run_time=0.3)                       # js2-loop-tools-diff % python3 -m unittest
        at(self, "All one hundred")
        gplay(self, *[FadeIn(g) for g in tests[1:] if len(g)], run_time=0.4)   # Ran 164 tests in 4.180s · OK
        at(self, "Then a live run")
        gplay(self, FadeIn(w2), FadeIn(run[0]), run_time=0.5)            # python3 -m jobwatch run --run-id ...
        for g, cue in zip(run[1:], ("Anthropic", "Databricks", "Linear")):
            at(self, cue)
            gplay(self, FadeIn(g), run_time=0.25)                         # jobs=635 new=83 · 895/88 · 32/1
        at(self, "and found")
        gplay(self, FadeIn(label("172 not seen on Nov 8", 1.75, -2.8, 48)), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B09 ────────────────────────────────────────────
class B09_RuleRejects(Scene):
    def construct(self):
        chrome(self)
        w, rows = term_block("B09", 0, 0.0, 2.62)
        crate = open_crate(1.7, -3.2, -1.55)
        tray = make_original("context-inbox", height=1.25, x=0.9, y=-1.75)
        tray.remove(tray.parts["records"], tray.parts["new-page"])            # kept: empty
        gplay(self, FadeIn(w), FadeIn(rows[0]), run_time=0.4)                 # grep -c not_relevant ...
        gplay(self, FadeIn(crate), FadeIn(floor_(-3.2, -2.45, 2.8)), run_time=0.4)
        at(self, "rejected all")
        gplay(self, FadeIn(rows[1]), run_time=0.3)                            # 172
        sheets = [page(-5.6, -0.35 + 0.05 * k, 0.62, 0.78).set_z_index(1) for k in range(5)]
        gplay(self, FadeIn(VGroup(*sheets)), FadeIn(label("rejected", -3.2, -2.9, 40)), run_time=0.4)
        gplay(self, LaggedStart(*[s.animate.move_to([-3.3 + 0.08 * k, -1.45, 0]) for k, s in enumerate(sheets)],
                                lag_ratio=0.2), run_time=1.0)
        at(self, "for the fictional")
        gplay(self, FadeIn(tray), FadeIn(label("kept", 0.9, -2.9, 40)), run_time=0.5)
        at(self, "Were those")
        gplay(self, FadeIn(label("?", -3.2, 0.25, 110)), run_time=0.5)
        at(self, "That's the gap", lead=0.6)
        lamp = make_original("inspection-lamp", height=2.3, x=4.3, y=-1.3)
        lamp.set_opacity(0.4)                                                      # not built: drawn faint, tagged "plan"
        gplay(self, FadeIn(lamp, shift=LEFT * 0.6), FadeIn(floor_(4.45, -2.4, 2.6)), FadeIn(tag("plan", 3.75, 0.2, 34)),
              run_time=0.6)
        finish(self)


# ──────────────────────────────────────────── B10 ────────────────────────────────────────────
class B10_Approval(Scene):
    def construct(self):
        chrome(self)
        w1, nov21 = term_block("B10", 0, 0.0, 2.62)
        w2, nov8 = term_block("B10", 1, 0.0, 2.62 - term_height("B10", 0) - 0.24)
        gplay(self, FadeIn(w1), FadeIn(nov21[0]), run_time=0.4)        # the Nov 21 command, no approval given
        at(self, "refused to save")
        gplay(self, FadeIn(nov21[1]), run_time=0.4)                    # incomplete — the state was not saved ...
        at(self, "it ended incomplete")
        gplay(self, FadeIn(nov21[2]), run_time=0.4)                    # state advanced: False
        at(self, "On November eighth")
        gplay(self, FadeIn(w2), FadeIn(nov8[0]), run_time=0.5)          # the Nov 8 command with --approve-state
        at(self, "and only then", lead=0.9)
        gplay(self, FadeIn(nov8[1]), FadeIn(nov8[2]), run_time=0.4)    # finished · state advanced: True
        finish(self)


# ──────────────────────────────────────────── B11 ────────────────────────────────────────────
class B11_RulesFirst(Scene):
    def construct(self):
        chrome(self)
        pg = page(-4.6, -0.5, 1.7, 2.1)
        q = quill(-5.2, 0.2, s=0.6)
        self.add(pg, q)
        gplay(self, FadeIn(floor_(-4.5, -1.85, 2.8)), run_time=0.4)
        at(self, "I wrote the rules first")
        gplay(self, FadeIn(label("rules first", -4.6, 1.5, 44)), run_time=0.4)
        write_lines(self, q, scribble_block(-5.2, 0.2, 1.1, n=2, gap=0.42, color=BAR1, sw=5), speed=2.0)
        at(self, "Claude Code wrote the code")
        ws = make_original("agent-workstation", height=2.0, x=-1.5, y=-0.6)
        gplay(self, FadeIn(ws), FadeIn(floor_(-1.5, -1.7, 2.8)), FadeIn(label("Claude Code", -1.5, 1.5, 44)),
              run_time=0.6)
        at(self, "all but five")
        gplay(self, ws.parts["tool"].animate.shift(ws.action_vectors["tool"]), run_time=0.5)
        at(self, "I ran my own checks")
        st = make_original("approval-stamp", height=1.8, x=1.45, y=-0.6)
        sheets = [page(3.2, y, 0.5, 0.64) for y in (0.5, -0.8)]          # one sign-off sheet per agent: JS1, JS2
        gplay(self, FadeIn(st), FadeIn(floor_(1.45, -1.6, 2.6)), FadeIn(VGroup(*sheets)), run_time=0.4)
        at(self, "twice I withheld", lead=0.6)
        for sh_y, agent in ((0.5, "JS1"), (-0.8, "JS2")):
            gplay(self, st.parts["stamp"].animate.shift(st.action_vectors["stamp"]), run_time=0.2)
            gplay(self, st.parts["stamp"].animate.shift(-st.action_vectors["stamp"]),
                  FadeIn(VGroup(rect(3.2, sh_y + 0.08, 0.26, 0.2, BAR1), label_left(agent + ": withheld", 3.65, sh_y + 0.2, 34))),
                  run_time=0.25)
        at(self, "until the record was right", lead=0.9)
        gplay(self, *[FadeIn(VGroup(check(3.14, y - 0.17, s=0.1), label_left("→ signed", 3.65, y - 0.25, 34)))
                      for y in (0.5, -0.8)], run_time=0.3)
        finish(self)


# ──────────────────────────────────────────── B12 ────────────────────────────────────────────
class B12_Steps(Scene):
    def construct(self):
        chrome(self)
        xs = (-4.65, -1.55, 1.55, 4.65)
        self.add(*[label(d, x, 1.75, 48) for d, x in zip(("Nov 25", "Dec 1", "Dec 13", "Dec 20"), xs)])
        rail = Line([-6.0, -1.95, 0], [6.0, -1.95, 0], color=GHOST, stroke_width=12)
        gplay(self, Create(rail), run_time=0.5)
        steps = [("inspection-lamp", 2.1, "By November twenty-fifth", 0.25),
                 ("checkpoint-scanner", 1.9, "By December first", 0.25),
                 ("approval-stamp", 1.7, "By December thirteenth", 0.25),
                 ("experiment-bench", 1.75, "December twentieth", 1.4)]
        prev = -6.0
        for x, (pid, h, cue, ld) in zip(xs, steps):
            at(self, cue, lead=ld)
            obj = make_original(pid, height=h, x=x, y=-0.35)
            gplay(self, FadeIn(obj, shift=UP * 0.3), Create(Line([prev, -1.95, 0], [x, -1.95, 0], color=INK, stroke_width=6)),
                  FadeIn(Dot([x, -1.95, 0], radius=0.11, color=TERRA)), run_time=0.7)
            prev = x
        finish(self)


# ──────────────────────────────────────────── B13 ────────────────────────────────────────────
class B13_Resources(Scene):
    def construct(self):
        chrome(self)
        xs = (-4.45, -1.45, 1.55, 4.6)
        ya, yb = 1.3, 0.8                                         # two label rows above the objects
        plug = make_original("connector-pair", height=1.5, x=xs[0], y=-0.9)
        self.add(plug)
        gplay(self, FadeIn(floor_(xs[0], -1.8, 2.4)), run_time=0.4)
        at(self, "No API credits")
        gplay(self, FadeIn(tag("no API credits", -6.05, ya, 34)), run_time=0.5)
        at(self, "my Claude Code login")
        gplay(self, plug.parts["plug"].animate.shift(plug.action_vectors["plug"]),
              FadeIn(label("Claude Code login", xs[0], yb, 34)), run_time=0.7)
        at(self, "twenty-seven postings")
        stack = make_original("skill-stack", height=1.3, x=xs[1], y=-0.95)
        gplay(self, FadeIn(stack, shift=UP * 0.2), FadeIn(floor_(xs[1], -1.75, 2.2)),
              FadeIn(label("27 judged", xs[1], ya, 34)), FadeIn(label("Oct 31", xs[1], yb, 34)), run_time=0.6)
        gplay(self, Create(check(xs[1] + 0.95, -0.35, s=0.2)), run_time=0.3)
        at(self, "Public boards")
        ws = make_original("agent-workstation", height=1.7, x=xs[2], y=-0.95)
        gplay(self, FadeIn(ws), FadeIn(floor_(xs[2], -1.9, 2.4)), FadeIn(label("no accounts", xs[2], ya, 34)),
              FadeIn(label("laptop", xs[2], yb, 34)), run_time=0.6)
        at(self, "The limits")
        slots = make_original("budget-slots", height=1.3, x=xs[3], y=-1.1)
        gplay(self, FadeIn(slots), FadeIn(floor_(xs[3], -1.85, 2.6)), FadeIn(label("daily budget", xs[3], ya, 34)),
              FadeIn(tag("plan", xs[3] - 0.55, yb, 34)), run_time=0.6)
        tok = slots.parts["allocated-token"]
        lift = slots.action_vectors["allocated-token"] * 0.55
        cap_y = float(np.array(tok.get_top())[1] + lift[1]) + 0.06
        cap_x = float(np.array(tok.get_center())[0] + lift[0])
        gplay(self, tok.animate.shift(lift), run_time=0.6)            # a reading budget is used up ...
        gplay(self, Create(Line([cap_x - 0.75, cap_y, 0], [cap_x + 0.75, cap_y, 0], color=INK, stroke_width=6)),
              run_time=0.3)                                            # ... and stops at the cap
        finish(self)


# ──────────────────────────────────────────── B14 ────────────────────────────────────────────
class B14_TestSet(Scene):
    def construct(self):
        chrome(self)
        crate = open_crate(1.7, -4.6, -1.3)
        inside = [page(-4.75 + 0.18 * k, -0.95, 0.62, 0.78).set_z_index(1) for k in range(3)]
        vault = make_original("secure-vault", height=2.0, x=4.8, y=-1.0)
        vault.parts["lock-bar"].shift(vault.action_vectors["lock-bar"])          # starts released (open)
        tray = make_original("context-inbox", height=1.2, x=1.4, y=-1.65)
        tray.remove(tray.parts["records"], tray.parts["new-page"])
        self.add(crate, *inside, vault, tray, label("rejected", -4.6, -2.75, 40), label("development", 1.4, -2.75, 40),
                 label("held out", 4.8, -2.75, 40))
        gplay(self, FadeIn(floor_(-4.6, -2.15, 2.8)), FadeIn(floor_(4.8, -2.05, 2.8)), run_time=0.4)
        at(self, "label real public postings")
        sheets = [page(x, 0.75, 0.78, 0.98) for x in (-2.4, -1.35, -0.3)]
        gplay(self, FadeIn(VGroup(*sheets), shift=UP * 0.2), run_time=0.4)
        q = quill(-2.7, 0.95, s=0.6)
        gplay(self, FadeIn(q), run_time=0.2)
        marks = [scribble(x - 0.28, 0.95, 0.5, color=BAR1, sw=5) for x in (-2.4, -1.35, -0.3)]
        write_lines(self, q, marks, speed=1.6)
        for sh, mk in zip(sheets, marks):                     # the hand label travels with its sheet
            self.remove(mk)
            sh.add(mk)
        gplay(self, FadeOut(q), run_time=0.2)
        at(self, "a random sample")
        gplay(self, inside[1].animate.move_to([0.75, 0.75, 0]), inside[2].animate.move_to([1.8, 0.75, 0]), run_time=0.5)
        at(self, "lock a held-out group")
        gplay(self, sheets[2].animate.move_to([4.75, -0.6, 0]).scale(0.6),
              inside[2].animate.move_to([4.85, -0.7, 0]).scale(0.6), run_time=0.5)
        gplay(self, FadeOut(sheets[2]), FadeOut(inside[2]),
              vault.parts["lock-bar"].animate.shift(-vault.action_vectors["lock-bar"]), run_time=0.4)
        gplay(self, *[s.animate.move_to([1.4 + 0.1 * k, -1.35, 0]).scale(0.7) for k, s in
                      enumerate((sheets[0], sheets[1], inside[1]))], run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B15 ────────────────────────────────────────────
class B15_Measures(Scene):
    def construct(self):
        chrome(self)
        xs = (-4.7, -1.6, 1.5, 4.7)
        bench = Line([-6.0, -1.75, 0], [6.0, -1.75, 0], color=GHOST, stroke_width=12)   # the evaluation bench line
        gplay(self, Create(bench), run_time=0.4)
        at(self, "whether every quote")
        scan = make_original("checkpoint-scanner", height=1.7, x=xs[0], y=-0.75)
        gplay(self, FadeIn(scan), FadeIn(label("quote found", xs[0], 1.0, 40)), run_time=0.5)
        gplay(self, Create(check(xs[0] + 1.0, 0.25, s=0.2)), run_time=0.3)
        at(self, "misreads")
        card = VGroup(page(xs[1], -0.6, 1.4, 1.5), rect(xs[1], -0.3, 1.0, 0.32, BAR2), rect(xs[1], -0.85, 1.0, 0.32, BAR3))
        gplay(self, FadeIn(card), FadeIn(label("misreads", xs[1], 1.0, 40)), run_time=0.5)
        gplay(self, Create(cross(xs[1] + 0.95, -0.55, s=0.16)), run_time=0.3)
        at(self, "two errors kept apart")
        c1, c2 = (make_original("context-crate", height=1.15, x=xs[2] + dx, y=-0.75) for dx in (-0.95, 0.95))
        gplay(self, FadeIn(c1), FadeIn(c2), FadeIn(label("two errors", xs[2], 1.0, 40)), run_time=0.6)
        at(self, "clearing the applicant")
        gplay(self, FadeIn(VGroup(label("unsupported", xs[2] - 0.95, -2.15, 34), label("clearance", xs[2] - 0.95, -2.6, 34))),
              run_time=0.4)
        at(self, "ruling out a posting")
        gplay(self, FadeIn(VGroup(label("false", xs[2] + 0.95, -2.15, 34), label("exclusion", xs[2] + 0.95, -2.6, 34))),
              run_time=0.4)
        at(self, "how often it says", lead=1.2)
        gplay(self, FadeIn(label("?", xs[3], -0.6, 110)), FadeIn(label("I cannot tell", xs[3], 1.0, 40)), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B16 ────────────────────────────────────────────
class B16_Failures(Scene):
    def construct(self):
        chrome(self)
        ys = (1.55, 0.85, 0.15, -0.55, -1.25)
        slips = [slip(-4.2, y, w=2.5, h=0.48, edge=BAR1) for y in ys]
        gplay(self, FadeIn(VGroup(*slips)), FadeIn(label("at least 5", -4.2, 2.3, 44)), run_time=0.5)
        cues = ("a quote with one word changed", "an either-or rule", "a posting silent", "a board that refuses")
        for k, cue in enumerate(cues):
            at(self, cue)
            gplay(self, Create(crack(-4.2, ys[k])), run_time=0.3)
        gplay(self, Create(crack(-4.2, ys[4])), run_time=0.3)
        at(self, "And the failure")
        pred = slip(1.0, 0.9, w=2.0, h=0.5, edge=BAR1)
        gplay(self, FadeIn(pred, shift=DOWN * 0.3), FadeIn(label("predicted", 1.0, 1.65, 40)),
              FadeIn(label_left("'5 years preferred'", 2.25, 1.05, 40)),
              FadeIn(label_left("→ read as required", 2.25, 0.5, 40)), run_time=0.6)
        at(self, "'five years preferred'")
        card = page(1.0, -0.95, 1.3, 0.85)                                   # the student's own label for that posting
        q = quill(0.55, -0.85, s=0.5)
        gplay(self, FadeIn(card), FadeIn(q), FadeIn(label_left("my label: preferred", 1.9, -0.95, 40)), run_time=0.4)
        write_lines(self, q, [scribble(0.55, -0.85, 0.85, color=BAR1, sw=5)], speed=2.0)
        at(self, "caught by a separate check", lead=1.2)
        gplay(self, FadeOut(q), Create(cross(1.0, 0.9, s=0.17)), FadeIn(Dot([1.0, -1.2, 0], radius=0.09, color=TERRA)),
              run_time=0.3)
        finish(self)


def crack(x, y, w=1.5):
    """A deliberate break across a slip: an ink zigzag that stays inside the slip's outline."""
    pts = [[x - w / 2 + w * i / 6, y + (0.1 if i % 2 else -0.1), 0] for i in range(7)]
    return VMobject(stroke_color=INK, stroke_width=6).set_points_as_corners(pts)


# ──────────────────────────────────────────── B18 ────────────────────────────────────────────
class B18_Limits(Scene):
    def construct(self):
        chrome(self)
        si, ti = Iso(-4.0, -2.15, 1.0), Iso(2.0, -2.15, 1.0)
        small = VGroup(*[si.box(0, 0, 0.1 * k, 1.1, 0.9, 0.06, PAGE_TOP, PAGE_L, PAGE_R, sw=2) for k in range(5)])
        self.add(small)
        gplay(self, FadeIn(floor_(-3.95, -1.75, 2.6)), run_time=0.3)
        at(self, "a set this small")
        gplay(self, FadeIn(label_left("my set", -2.6, -1.3, 44)), run_time=0.4)
        at(self, "It can't prove")
        tall = [ti.box(0, 0, 0.1 * k, 1.1, 0.9, 0.06, PAGE_TOP, PAGE_L, PAGE_R, sw=2) for k in range(32)]
        gplay(self, FadeIn(floor_(2.05, -1.75, 2.6)),
              LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in tall], lag_ratio=0.08), run_time=1.0)
        gplay(self, FadeIn(label_left("every posting", 3.25, 0.6, 40)), run_time=0.3)
        finish(self)


# ──────────────────────────────────────────── BOUT ────────────────────────────────────────────
class BOUT_Outro(Scene):
    """Our own outro: the title and the student's name. (The toolkit's ClaudeTitleOutro hard-codes a handle.)"""
    def construct(self):
        lamp = make_original("inspection-lamp", height=2.5, x=-4.3, y=-0.25)
        self.add(lamp, label("Fine Print", 1.4, 0.95, 100))
        gplay(self, FadeIn(floor_(-4.1, -1.6, 3.0)), run_time=0.35)
        gplay(self, FadeIn(label("Suketh Reddy Produtoor", 1.4, -0.3, 50)),
              Create(Line([-1.3, 0.3, 0], [4.1, 0.3, 0], color=INK, stroke_width=4)), run_time=0.45)
        first, rest = CREDIT.split(" · ", 1)                       # the exact line from the sheet, on two rows
        gplay(self, FadeIn(VGroup(label(first + " ·", 0.0, -2.15, 32), label(rest, 0.0, -2.69, 32))), run_time=0.4)
        finish(self)
