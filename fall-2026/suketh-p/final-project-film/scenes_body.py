
# ═════════════════════════════ FINE PRINT — scene body (Claude Code, 2026-10-14) ═════════════════════════════
# Pasted after iso_kit.py and iso_originals_25.py by build_scenes.py (Gate A copies only scenes.py).
# One drawing per beat. Labels sit beside objects in ink, at most three per beat counting the honesty stamp.
# The stamp says what each picture is: "real · …" for Assignment 3 evidence, "constructed · not built" for the
# proposed agent, "constructed example" for the made-up posting sentence in B04.

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
    until(self, phrase, lead)


def label(s, x, y, size=48):
    t = T(s, size)
    t.move_to([x, y, 0])
    return t


def label_left(s, x0, y, size=48):
    t = T(s, size)
    t.move_to([x0 + t.width / 2, y, 0])
    return t


def stamp(text, kind="sketch"):
    """The honesty stamp, top left: what is real and what is a sketch."""
    dot = Dot([-5.95, 3.0, 0], radius=0.09, color=TERRA if kind == "sketch" else INK)
    t = T(text, 36)
    t.move_to([-5.72 + t.width / 2, 3.0, 0])
    return VGroup(dot, t)


def cross(x, y, s=0.22, color=INK, w=7):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def slip(x, y, w=1.3, h=0.5):
    """A quote slip: a small white card with a kraft shadow and one grey rule (never type)."""
    sh = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.07, y - 0.07, 0])
    card = Rectangle(width=w, height=h, fill_color=PAGE_TOP, fill_opacity=1, stroke_color=INK,
                     stroke_width=3).move_to([x, y, 0])
    rule = Line([x - w / 2 + 0.2, y, 0], [x + w / 2 - 0.2, y, 0], color=GHOST, stroke_width=5)
    return VGroup(sh, card, rule)


def floor(x, y, w=3.6):
    """A soft landing shadow under a prop (a new non-text shape for Gate A)."""
    e = Ellipse(width=w, height=0.42, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    e.set_z_index(-1)
    return e


def sheet(x, y, w=1.05, h=1.35, lines=3):
    """A posting page: white sheet, ink outline, kraft shadow, grey scribble lines."""
    pg = paper(x, y, w, h)
    return VGroup(pg, scribbles_on(pg, n=lines, inset=0.2, gap=0.26, color=GHOST, sw=4))


# ──────────────────────────────────────────── B00 ────────────────────────────────────────────
class B00_Recipe(Scene):
    def construct(self):
        rig = make_original("evidence-binder", height=2.9, x=-2.0, y=-0.45)
        self.add(stamp("real · from my A3 work", "real"), rig, label("A3 recipe", 3.4, 1.3, 58))
        gplay(self, FadeIn(floor(-2.0, -1.95, 3.8)), run_time=0.5)
        at(self, "Claude wrote the code")
        gplay(self, rig.parts["cover"].animate.shift(rig.action_vectors["cover"]), run_time=1.0)
        at(self, "ran the checks")
        gplay(self, FadeIn(label("36 tests", 3.4, 0.0, 54)), run_time=0.5)
        gplay(self, Create(VGroup(*[check(2.7 + i * 0.72, -1.0, s=0.2) for i in range(3)])), run_time=0.8)
        finish(self)


# ──────────────────────────────────────────── B01 ────────────────────────────────────────────
class B01_EightPostings(Scene):
    def construct(self):
        xs = [-5.0, -3.65, -2.3, -0.95]
        pages = VGroup(*[sheet(x, y) for y in (0.85, -1.15) for x in xs])
        self.add(stamp("real · Sep 29 review · fictional applicant", "real"), pages)
        gplay(self, FadeIn(floor(-2.95, -2.1, 5.6)), run_time=0.4)
        at(self, "six asked")
        flagged = [0, 1, 2, 3, 4, 6]                        # six of the eight; which six is not the claim
        flags = VGroup(*[Rectangle(width=0.5, height=0.2, fill_color=INK, fill_opacity=1, stroke_width=0)
                         .move_to([xs[i % 4] + 0.2, (0.85 if i < 4 else -1.15) + 0.86, 0]) for i in flagged])
        gplay(self, FadeIn(flags), run_time=0.6)
        gplay(self, FadeIn(label("6 of 8", 3.7, 0.35, 120)), run_time=0.6)
        at(self, "An AI reviewer")
        hold = Rectangle(width=5.9, height=0.22, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([-2.95, -2.45, 0])
        gplay(self, GrowFromCenter(hold), FadeIn(label("all held", 3.7, -1.6, 52)), run_time=0.7)
        finish(self)


# ──────────────────────────────────────────── B02 ────────────────────────────────────────────
class B02_FinePrint(Scene):
    def construct(self):
        rig = make_original("inspection-lamp", height=3.3, x=-1.6, y=-0.25)
        self.add(stamp("constructed · not built"), rig, label("Fine Print", 3.5, 1.55, 64))
        gplay(self, FadeIn(floor(-1.4, -1.95, 3.6)), run_time=0.4)
        at(self, "the posting itself")
        gplay(self, rig.parts["lamp-head"].animate.shift(rig.action_vectors["lamp-head"]), run_time=1.0)
        at(self, "quote the sentence")
        slips = VGroup(*[slip(3.5, 0.35 - i * 0.75) for i in range(3)])
        gplay(self, FadeIn(slips, shift=RIGHT * 0.4), run_time=0.9)
        at(self, "stop for my approval")
        gplay(self, Create(check(4.65, -1.95, s=0.22)), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B03 ────────────────────────────────────────────
class B03_QuoteCheck(Scene):
    def construct(self):
        rig = make_original("checkpoint-scanner", height=3.1, x=-1.2, y=-0.35)
        self.add(stamp("constructed · not built"), rig, label("quote check", 3.6, 1.55, 58))
        gplay(self, FadeIn(floor(-1.1, -1.95, 3.4)), run_time=0.4)
        at(self, "Code will check")
        gplay(self, rig.parts["parcel"].animate.shift(rig.action_vectors["parcel"]), run_time=0.9)
        gplay(self, Create(check(3.0, 0.35, s=0.26)), run_time=0.4)
        at(self, "If it isn't")
        bad = slip(3.6, -0.6, w=1.2)
        gplay(self, FadeIn(bad), run_time=0.4)
        gplay(self, bad.animate.shift(DOWN * 1.1), Create(cross(4.6, -0.6)), run_time=0.7)
        finish(self)


# ──────────────────────────────────────────── B04 ────────────────────────────────────────────
class B04_Misread(Scene):
    def construct(self):
        rig = make_original("checkpoint-scanner", height=2.6, x=-2.2, y=-0.75)
        desk = make_original("review-desk", height=1.9, x=3.9, y=-1.35)
        quote = label("“5 yrs preferred”", -2.2, 1.75, 50)
        self.add(stamp("constructed example"), rig, desk, quote)
        gplay(self, FadeIn(floor(-2.1, -2.15, 3.0)), run_time=0.4)
        at(self, "the agent records required")
        gplay(self, FadeIn(label("read as: required", 3.6, 1.75, 48)), run_time=0.5)
        at(self, "The quote check would still pass")
        gplay(self, rig.parts["parcel"].animate.shift(rig.action_vectors["parcel"]), run_time=0.8)
        gplay(self, Create(check(0.35, 0.6, s=0.24)), run_time=0.4)
        at(self, "So preferred")
        gplay(self, Create(cross(3.6, 1.0, s=0.22)), run_time=0.4)
        at(self, "anything unclear")
        gplay(self, desk.parts["evidence"].animate.shift(desk.action_vectors["evidence"] * 0.6), run_time=0.8)
        finish(self)


# ──────────────────────────────────────────── B05 ────────────────────────────────────────────
class B05_Background(Scene):
    def construct(self):
        rig = make_original("comparison-trays", height=2.6, x=-0.4, y=-0.6)
        b = rig.parts["sample-b"]
        rig.remove(b)
        self.add(stamp("constructed · not built"), rig, label("requirement", -3.3, 1.45, 50))
        gplay(self, FadeIn(floor(-0.4, -1.95, 4.0)), run_time=0.4)
        at(self, "two and a half years")
        gplay(self, FadeIn(b, shift=DOWN * 0.5), FadeIn(label("fictional profile", 3.3, 1.45, 50)), run_time=0.8)
        at(self, "needs a comparison")
        gplay(self, b.animate.shift(rig.action_vectors["sample-b"] * 0.5), run_time=0.7)
        finish(self)


# ──────────────────────────────────────────── B06 ────────────────────────────────────────────
class B06_Loop(Scene):
    def construct(self):
        gate = make_original("permission-gate", height=2.9, x=-2.7, y=-0.5)
        slots = make_original("budget-slots", height=1.9, x=3.1, y=-1.0)
        self.add(stamp("constructed · not built"), gate, slots, label("read only", -2.7, 1.75, 52))
        gplay(self, FadeIn(floor(-2.7, -1.95, 3.2)), run_time=0.4)
        at(self, "fetch a public posting")
        gplay(self, gate.parts["barrier"].animate.shift(gate.action_vectors["barrier"]), run_time=0.8)
        pg = slip(-4.6, -1.35, w=1.0, h=0.42)
        gplay(self, FadeIn(pg), run_time=0.3)
        gplay(self, pg.animate.shift(RIGHT * 3.6), run_time=0.9)
        at(self, "the budget runs out")
        gplay(self, FadeIn(label("budget", 3.1, 0.6, 52)), run_time=0.4)
        gplay(self, slots.parts["allocated-token"].animate.shift(slots.action_vectors["allocated-token"]), run_time=0.8)
        finish(self)


# ──────────────────────────────────────────── B07 ────────────────────────────────────────────
class B07_Gate(Scene):
    def construct(self):
        rig = make_original("approval-stamp", height=3.0, x=-1.8, y=-0.4)
        self.add(stamp("constructed · not built"), rig)
        gplay(self, FadeIn(floor(-1.7, -1.95, 4.0)), run_time=0.4)
        at(self, "until I approve it")
        gplay(self, rig.parts["stamp"].animate.shift(rig.action_vectors["stamp"]), run_time=0.6)
        gplay(self, Create(check(-0.5, -0.95, s=0.22)), run_time=0.4)
        at(self, "A value the model proposed")
        src = VGroup(Rectangle(width=0.5, height=0.36, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.2, 0.75, 0]),
                     label("source: model", 1.65 + 3.478 / 2, 0.75, 48))      # measured width 3.478
        gplay(self, FadeIn(src), run_time=0.5)
        at(self, "my approval will be")
        rev = VGroup(Rectangle(width=0.5, height=0.36, fill_color=BAR1, fill_opacity=1, stroke_width=0).move_to([1.2, -0.25, 0]),
                     label("review: approved", 1.65 + 4.217 / 2, -0.25, 48))  # measured width 4.217
        gplay(self, FadeIn(rev), run_time=0.5)
        finish(self)


# ──────────────────────────────────────────── B08 ────────────────────────────────────────────
class B08_Alternatives(Scene):
    def construct(self):
        pages = VGroup(*[paper(x, -0.55, 1.5, 2.3) for x in (-4.9, -3.0)])
        self.add(stamp("left real · right constructed"), pages, label("LinkedIn \u00b7 2 postings", -3.55, 1.55, 44))
        gplay(self, FadeIn(floor(-3.95, -1.95, 4.4)), run_time=0.4)
        at(self, "Both separate minimum")
        blocks = VGroup(*[Rectangle(width=1.1, height=h, fill_color=c, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
                          for x in (-4.9, -3.0) for (y, h, c) in ((0.15, 0.55, BAR2), (-0.6, 0.55, BAR3))])
        gplay(self, FadeIn(blocks), run_time=0.6)
        at(self, "neither accessible description")
        slots = VGroup(*[Rectangle(width=1.1, height=0.32, fill_color=STAGE, fill_opacity=1, stroke_color=BAR1,
                                   stroke_width=3).move_to([x, -1.3, 0]) for x in (-4.9, -3.0)])
        gplay(self, FadeIn(slots), run_time=0.5)
        at(self, "Fine Print will preserve")
        report = sheet(2.4, -0.5, w=1.9, h=2.5, lines=3)
        gplay(self, FadeIn(report, shift=LEFT * 0.3), FadeIn(label("Fine Print", 3.4, 1.55, 54)), run_time=0.7)
        at(self, "attach checked source quotes")
        quotes = VGroup(*[slip(4.6, 0.35 - i * 0.75, w=1.3) for i in range(3)])
        gplay(self, FadeIn(quotes, shift=RIGHT * 0.3), run_time=0.6)
        at(self, "keep missing sponsorship")
        gplay(self, FadeIn(Dot([5.45, -1.15, 0], radius=0.1, color=TERRA)), run_time=0.4)
        finish(self)


# ──────────────────────────────────────────── B09 ────────────────────────────────────────────
class B09_FirstMinute(Scene):
    def construct(self):
        rig = make_original("release-parcel", height=2.7, x=-2.6, y=-0.6)
        self.add(stamp("constructed · not built"), rig, label("repo", -2.6, 1.7, 54))
        gplay(self, FadeIn(floor(-2.6, -2.05, 3.4)), run_time=0.4)
        at(self, "run one command")
        gplay(self, rig.parts["lid"].animate.shift(rig.action_vectors["lid"]), run_time=0.8)
        at(self, "read the report")
        rep = sheet(2.9, -0.45, w=2.4, h=2.7, lines=4)
        gplay(self, FadeIn(rep, shift=RIGHT * 0.4), FadeIn(label("report", 2.9, 1.7, 54)), run_time=0.8)
        gplay(self, Create(VGroup(*[check(4.4, 0.35 - i * 0.6, s=0.16) for i in range(3)])), run_time=0.6)
        finish(self)


# ──────────────────────────────────────────── B10 ────────────────────────────────────────────
class B10_Evaluation(Scene):
    def construct(self):
        rig = make_original("experiment-bench", height=2.7, x=-2.2, y=-0.6)
        self.add(stamp("constructed · not built"), rig, label("held out", -2.2, 1.65, 54))
        gplay(self, FadeIn(floor(-2.2, -2.05, 3.8)), run_time=0.4)
        at(self, "set a held-out group aside")
        gplay(self, rig.parts["sample"].animate.shift(rig.action_vectors["sample"]), run_time=0.8)
        at(self, "count two mistakes")
        boxes = VGroup(*[make_original("context-crate", height=1.3, x=x, y=-0.9) for x in (2.4, 4.4)])
        gplay(self, FadeIn(boxes, shift=UP * 0.3), FadeIn(label("2 error types", 3.4, 1.65, 52)), run_time=0.8)
        finish(self)


# ──────────────────────────────────────────── B11 ────────────────────────────────────────────
class B11_FirstSlice(Scene):
    def construct(self):
        rig = make_original("task-queue", height=2.6, x=-2.2, y=-0.6)
        self.add(stamp("constructed · not built"), rig, label("first slice", -2.2, 1.65, 56))
        gplay(self, FadeIn(floor(-2.2, -2.05, 4.0)), run_time=0.4)
        at(self, "one loop over one public posting")
        gplay(self, rig.parts["next-task"].animate.shift(rig.action_vectors["next-task"] * 1.5), run_time=0.8)
        at(self, "a test that fails")
        scan = make_original("checkpoint-scanner", height=2.2, x=3.6, y=-0.8)
        gplay(self, FadeIn(scan), FadeIn(label("one-word test", 3.6, 1.65, 50)), run_time=0.5)
        gplay(self, Create(cross(4.95, 0.55, s=0.22)), run_time=0.4)
        finish(self)


# ──────────────────────────────────────────── B12 ────────────────────────────────────────────
class B12_Skills(Scene):
    def construct(self):
        rig = make_original("skill-stack", height=2.4, x=-2.6, y=-0.55)
        self.add(rig, label("Amazon · Vertex · AgentOS", -2.4, 1.6, 48))
        gplay(self, FadeIn(floor(-2.6, -1.85, 3.2)), run_time=0.4)
        at(self, "AgentOS")
        gplay(self, rig.parts["selected-page"].animate.shift(rig.action_vectors["selected-page"] * 0.6), run_time=0.8)
        at(self, "New to me")
        fresh = sheet(3.4, -0.5, w=1.9, h=2.3, lines=2)
        gplay(self, FadeIn(fresh, shift=LEFT * 0.4), FadeIn(label("new", 3.4, 1.6, 56)), run_time=0.8)
        gplay(self, FadeIn(Dot([2.75, 0.4, 0], radius=0.09, color=TERRA)), run_time=0.4)
        finish(self)


# ──────────────────────────────────────────── B13 ────────────────────────────────────────────
class B13_ExistsWill(Scene):
    def construct(self):
        binder = make_original("evidence-binder", height=2.3, x=-2.9, y=-0.7)
        crate = make_original("context-crate", height=2.3, x=3.0, y=-0.7)
        self.add(binder, crate, label("exists", -2.9, 1.5, 58), label("not yet", 3.0, 1.5, 58))
        gplay(self, FadeIn(floor(-2.9, -2.05, 3.2)), FadeIn(floor(3.0, -2.05, 2.8)), run_time=0.4)
        at(self, "the recipe")
        drops = VGroup(*[slip(-2.75 + i * 0.12, 0.05 + i * 0.16, w=1.5, h=0.42) for i in range(3)])
        gplay(self, FadeIn(drops, shift=DOWN * 0.6), run_time=0.8)
        at(self, "Not yet")
        gplay(self, FadeIn(Dot([3.0, -0.05, 0], radius=0.1, color=TERRA)), run_time=0.4)
        finish(self)


# ──────────────────────────────────────────── BOUT ────────────────────────────────────────────
class BOUT_Outro(Scene):
    """Our own outro: the title and my name. (The toolkit's ClaudeTitleOutro hard-codes the instructor's handle.)"""
    def construct(self):
        rig = make_original("inspection-lamp", height=2.6, x=-3.6, y=-0.3)
        self.add(rig, label("Fine Print", 2.0, 0.55, 104))
        gplay(self, FadeIn(floor(-3.4, -1.6, 3.0)), run_time=0.35)
        gplay(self, FadeIn(label("Suketh Reddy Produtoor", 2.0, -0.75, 50)),
              Create(Line([-0.4, -0.12, 0], [4.4, -0.12, 0], color=INK, stroke_width=4)), run_time=0.45)
        finish(self)
