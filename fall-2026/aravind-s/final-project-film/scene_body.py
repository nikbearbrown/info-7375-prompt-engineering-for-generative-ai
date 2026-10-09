# ═════════════════════════════ Klaxon pitch film: the scenes ═════════════════════════════
# One drawn picture per beat. The cast stays the same across the film:
#   server tower = the payments system   conveyor parcels = webhooks
#   agent workstation = Klaxon            checkpoint scanner = the money check
#   approval stamp / permission gate = a person's approval   evidence binder = records
# Honesty tags: drawn sketches of the future product say "constructed"; the
# beat drawn from the real 2026-10-09 run says "real run".

try:
    _WORDS = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "mp3", "words.json")))["beats"]
except (OSError, KeyError, ValueError):
    _WORDS = {}

KRAFT_DEEP = "#9C8462"  # connectors: ink-edged cables would fuse into "text" under GATE T
GUARD = 0.25  # keep every animation this far from the clip midpoint (GATE T and Gate V sample there)


def _bid(scene):
    return type(scene).__name__.split("_")[0]


def _dur(scene):
    return _TARGET.get(_bid(scene), 10.0)


def _at(scene, word, nth=1):
    """Seconds into the beat at which `word` (its nth occurrence) starts, or None."""
    seen = 0
    for tok in _WORDS.get(_bid(scene), []):
        if tok["text"].strip(".,:;!?\"'").lower() == word.lower():
            seen += 1
            if seen == nth:
                return tok["startFrame"] / 24.0
    return None


def _cue(scene, word, nth=1, lead=0.1):
    t = _at(scene, word, nth)
    if t is not None:
        target = t - lead
        mid = _dur(scene) / 2
        if mid - GUARD <= target <= mid + GUARD:
            target = mid + GUARD + 0.03  # one wait across the midpoint, not two (no file seam there)
        gap = target - _elapsed(scene)
        if gap > 0.02:
            scene.wait(gap)


def _play(scene, *anims, run_time=0.6):
    mid = _dur(scene) / 2
    now = _elapsed(scene)
    if now < mid + GUARD and now + run_time > mid - GUARD:
        scene.wait(max(0.02, mid + GUARD + 0.03 - now))
    scene.play(*anims, run_time=run_time)


def _done(scene):
    gap = _dur(scene) - _elapsed(scene) - 0.08
    if gap > 0.02:
        scene.wait(gap)


def _label(text, x, y, size=44):
    return T(text, size).move_to([x, y, 0])


def _tag(text="constructed", x=-5.15):
    return T(text, 32).move_to([x, 3.0, 0])


def _slip(x=0.0, y=0.0, s=1.0):
    """A recurring paper slip (a record, a page of evidence); grey line, no ink inside."""
    i = Iso(0, 0, s)
    g = i.box(-.48, -.43, 0, .96, .86, .08, sw=3)
    g.add(Line(i.p(-.27, -.1, .085), i.p(.27, -.1, .085), color=DIM, stroke_width=5))
    return g.move_to([x, y, 0])


def _crate(x=0.0, y=0.0, s=1.0, w=.8, d=.8, h=.55):
    """A small kraft box: a webhook, an incident, a fix, a skill."""
    return Iso(0, 0, s).box(-w / 2, -d / 2, 0, w, d, h).move_to([x, y, 0])


def _dashboard(x, y, w=2.3, h=1.7):
    """HTTP monitoring: a grey panel whose three bars are all full."""
    panel = RoundedRectangle(width=w, height=h, corner_radius=0.14, fill_color=BAR1, fill_opacity=1,
                             stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    bars = VGroup(*[Rectangle(width=0.34, height=h * 0.62, fill_color=CARD, fill_opacity=1, stroke_width=0)
                    .move_to([x + dx, y - h * 0.04, 0]) for dx in (-0.6, 0.0, 0.6)])
    return VGroup(panel, bars)


def _ghost(rig):
    """A prop that does not exist yet: outline only, in dim grey."""
    for part in rig.parts.values():
        for mob in part:
            mob.set_fill(opacity=0)
            mob.set_stroke(DIM, width=3, opacity=1)
    return rig


def _move(rig, part, k=1.0):
    return rig.parts[part].animate.shift(rig.action_vectors[part] * k)


class B00_WhatItIs(Scene):
    def construct(self):
        tower = make_original("server-tower", height=3.0, x=-3.6, y=0.2)
        desk = make_original("agent-workstation", height=2.5, x=3.3, y=-0.1)
        self.add(tower, desk, _label("payments", -3.6, -1.9), _label("Klaxon", 3.3, -1.95), _tag())
        _cue(self, "alert")
        _play(self, FadeIn(Dot([-3.6, 1.62, 0], radius=0.13, color=TERRA)), run_time=0.4)
        _cue(self, "investigate")
        _play(self, Create(Line([1.65, 0.35, 0], [-2.2, 0.35, 0], color=KRAFT_DEEP, stroke_width=6)), run_time=0.7)
        _cue(self, "evidence")
        _play(self, FadeIn(_slip(-0.3, -0.75), shift=UP * 0.2), run_time=0.5)
        _cue(self, "approve")
        _play(self, Create(check(0.65, -0.55, s=0.22)), run_time=0.4)
        _cue(self, "healthy")
        _play(self, Create(check(-1.95, 1.35, s=0.2)), run_time=0.35)
        _cue(self, "money")
        _play(self, Create(check(-1.25, 1.35, s=0.2)), run_time=0.35)
        _done(self)


class B01_Repo(Scene):
    def construct(self):
        parcel = make_original("release-parcel", height=2.8, x=-3.4, y=-0.3)
        parts = [make_original("server-tower", height=1.9, x=0.9, y=1.15),
                 make_original("experiment-bench", height=1.6, x=4.1, y=1.1),
                 make_original("agent-workstation", height=1.6, x=0.9, y=-1.35),
                 make_original("evidence-binder", height=1.5, x=4.1, y=-1.3)]
        self.add(parcel, _label("GitHub repo", -3.4, -2.25), _tag())
        _cue(self, "repo")
        _play(self, _move(parcel, "lid"), run_time=0.6)
        for word, part, rt in (("payments", parts[0], 0.45), ("incidents", parts[1], 0.25),
                               ("agent", parts[2], 0.45), ("report", parts[3], 0.45)):
            _cue(self, word)
            _play(self, FadeIn(part, shift=UP * 0.3), run_time=rt)
        _done(self)


class B02_QuietIncident(Scene):
    def construct(self):
        belt = make_original("conveyor", height=2.3, x=-3.6, y=-0.5)
        tower = make_original("server-tower", height=2.6, x=0.45, y=-0.1)
        dash = _dashboard(4.3, 0.0)
        self.add(belt, tower, dash, _label("webhook", -3.6, -2.2), _label("dashboard", 4.3, -1.4), _tag())
        twin = belt.parts["parcel"].copy()
        _cue(self, "webhooks")
        _play(self, _move(belt, "parcel"), run_time=0.8)
        _cue(self, "twice")
        _play(self, FadeIn(twin), run_time=0.3)
        _play(self, twin.animate.shift(belt.action_vectors["parcel"] * 0.72), run_time=0.7)
        _cue(self, "books")
        _play(self, FadeIn(Dot([0.45, 1.6, 0], radius=0.13, color=TERRA)), run_time=0.4)
        _cue(self, "succeeded")
        _play(self, Create(check(4.3, 1.3, s=0.22)), run_time=0.45)
        _done(self)


class B03_Alternatives(Scene):
    def construct(self):
        holmes = make_original("tool-block", height=2.4, x=-3.4, y=0.2)
        lamp = make_original("inspection-lamp", height=2.8, x=2.6, y=0.1)
        self.add(holmes, lamp, _label("HolmesGPT", -3.4, -1.45), _label("manual", 2.6, -1.85), _tag())
        _cue(self, "Holmes")
        _play(self, _move(holmes, "tool"), run_time=0.6)
        _cue(self, "logs")
        _play(self, FadeIn(_slip(-0.6, 1.55, s=0.7), shift=DOWN * 0.2), run_time=0.4)
        _cue(self, "manual")
        _play(self, _move(lamp, "lamp-head"), run_time=0.6)
        _cue(self, "runbook")
        _play(self, FadeIn(_slip(5.0, -0.8, s=0.8), shift=UP * 0.2), run_time=0.4)
        _done(self)


class B04_TheirCheck(Scene):
    def construct(self):
        holmes = make_original("tool-block", height=2.2, x=-4.3, y=0.15)
        dash = _dashboard(-0.6, 0.0)
        ghost = _ghost(make_original("checkpoint-scanner", height=2.6, x=3.9, y=-0.1))
        self.add(holmes, dash, _label("HolmesGPT", -4.3, -1.45), _label("dashboard", -0.6, -1.4), _tag())
        _cue(self, "comparing")
        _play(self, _move(holmes, "tool"), run_time=0.5)
        _cue(self, "latency")
        _play(self, Create(check(-0.6, 1.3, s=0.22)), run_time=0.35)
        _cue(self, "didn't")
        _play(self, Create(ghost), FadeIn(_label("money check?", 3.9, -1.8)), run_time=0.7)
        _done(self)


class B05_MoneyCheck(Scene):
    def construct(self):
        scan = make_original("checkpoint-scanner", height=3.0, x=-3.2, y=-0.1)
        stamp = make_original("approval-stamp", height=2.6, x=3.0, y=-0.2)
        self.add(scan, stamp, _label("money check", -3.2, -2.15), _label("approve", 3.0, -2.05), _tag())
        _cue(self, "save")
        _play(self, _move(scan, "parcel"), run_time=0.7)
        _cue(self, "approving")
        _play(self, _move(stamp, "stamp", 0.6), run_time=0.5)
        flag_at = np.array(scan.parts["parcel"].get_center()) + np.array([0.24, 0.23, 0.0])  # on the top face, clear of the post
        _cue(self, "green")
        _play(self, FadeIn(Dot(flag_at, radius=0.13, color=TERRA)), run_time=0.3)
        _cue(self, "wrong")
        _play(self, _move(stamp, "stamp", -0.6), run_time=0.45)
        _done(self)


class B06_Reader(Scene):
    def construct(self):
        desk = make_original("review-desk", height=2.8, x=-3.0, y=-0.2)
        scan = make_original("checkpoint-scanner", height=2.4, x=3.5, y=-0.2)
        key = Iso(0, 0, 1).box(-.35, -.35, 0, .7, .7, .3, DARK_TOP, DARK_L, DARK_R).move_to([0.35, -1.05, 0])
        self.add(desk, scan, key, _label("README", -3.0, -2.15), _label("make demo", 0.35, -1.85), _tag())
        _cue(self, "minute")
        _play(self, _move(desk, "evidence"), run_time=0.6)
        _cue(self, "command")
        pointer = cursor(0.75, -0.25)
        _play(self, FadeIn(pointer, shift=DOWN * 0.2), run_time=0.3)
        _play(self, key.animate.shift(DOWN * 0.08), run_time=0.15)
        _cue(self, "replay")
        _play(self, _move(scan, "parcel"), run_time=0.6)
        _play(self, Create(check(3.5, 1.4, s=0.22)), run_time=0.3)
        _done(self)


class B07_Contract(Scene):
    def construct(self):
        stack = make_original("skill-stack", height=2.6, x=-3.6, y=0.0)
        self.add(stack, _label("diagnosis", -3.6, -1.85), _label("evidence", 4.9, 0.0), _tag())
        _cue(self, "contract")
        _play(self, _move(stack, "selected-page"), run_time=0.6)
        _cue(self, "format")
        _play(self, Create(check(-1.5, 1.3, s=0.22)), run_time=0.35)
        bars = VGroup(*[Rectangle(width=0.28, height=hgt, fill_color=c, fill_opacity=1, stroke_width=0)
                        .move_to([2.2 + 0.4 * n, 0.95 + hgt / 2, 0])
                        for n, (hgt, c) in enumerate(((0.7, BAR1), (1.1, BAR2), (0.9, BAR1)))])
        log = _slip(2.6, -0.05, s=1.0)
        pts = ([1.95, -1.75, 0], [2.6, -1.1, 0], [3.25, -1.5, 0])
        trace = VGroup(Line(pts[0], pts[1], color=KRAFT_DEEP, stroke_width=6), Line(pts[1], pts[2], color=KRAFT_DEEP, stroke_width=6),
                       *[Dot(p, radius=0.12, color=INK) for p in pts])
        for word, source, a, b in (("metric", bars, [-2.0, 0.65, 0], [1.85, 1.45, 0]),
                                   ("log", log, [-2.0, 0.35, 0], [1.6, 0.0, 0]),
                                   ("trace", trace, [-2.0, 0.05, 0], [1.65, -1.55, 0])):
            _cue(self, word)
            _play(self, FadeIn(source), Create(Line(a, b, color=KRAFT_DEEP, stroke_width=5)), run_time=0.4)
        _done(self)


class B08_LoopEval(Scene):
    def construct(self):
        queue = make_original("task-queue", height=2.4, x=-4.0, y=-0.3)
        gate = make_original("permission-gate", height=2.6, x=0.0, y=-0.1)
        budget = make_original("budget-slots", height=2.0, x=4.0, y=0.6)
        self.add(queue, gate, budget, _label("incidents", -4.0, -2.05), _label("approval gate", 0.0, -1.95),
                 _label("budget", 4.0, -0.95), _tag())
        _cue(self, "loop")
        _play(self, _move(queue, "next-task"), run_time=0.45)
        _cue(self, "budgets")
        _play(self, _move(budget, "allocated-token"), run_time=0.45)
        _cue(self, "gate")
        _play(self, _move(gate, "barrier"), run_time=0.55)
        _play(self, Create(check(1.75, 1.15, s=0.22)), run_time=0.35)
        _cue(self, "incidents")
        _play(self, FadeIn(_crate(-5.55, 1.15, s=0.8), shift=DOWN * 0.3), run_time=0.4)
        _done(self)


class B09_Reviewer(Scene):
    def construct(self):
        binder = make_original("evidence-binder", height=2.6, x=-3.4, y=-0.1)
        ghost = _ghost(make_original("server-tower", height=2.4, x=4.9, y=0.0))
        self.add(binder, _label("evidence", -3.4, -1.95), _tag())
        _cue(self, "build")
        _play(self, _move(binder, "cover"), run_time=0.6)
        for word, x in (("tests", -0.2), ("traces", 1.45), ("evaluation", 3.1)):
            _cue(self, word)
            _play(self, FadeIn(_slip(x, -0.35), shift=UP * 0.2), run_time=0.3)
        _cue(self, "Not")
        _play(self, Create(ghost), FadeIn(_label("not claimed", 4.9, -1.85)), run_time=0.7)
        _done(self)


class B10_InOut(Scene):
    def construct(self):
        ours = make_original("server-tower", height=2.6, x=-4.6, y=-0.1)
        gate = make_original("permission-gate", height=2.4, x=-1.2, y=-0.2)
        theirs = _ghost(make_original("server-tower", height=2.6, x=4.6, y=-0.1))
        fix = _crate(0.95, -0.75, s=0.9)
        self.add(ours, gate, theirs, fix, _label("mine", -4.6, -1.95), _label("not mine", 4.6, -1.95), _tag())
        _cue(self, "approved")
        _play(self, _move(gate, "barrier"), run_time=0.6)
        _cue(self, "rollback")
        _play(self, fix.animate.move_to([-3.05, -0.95, 0]), run_time=0.8)
        _cue(self, "out")
        _play(self, Create(Line([2.45, -1.65, 0], [2.45, 1.65, 0], color=DIM, stroke_width=6)), run_time=0.6)
        _cue(self, "never")
        _play(self, _move(gate, "barrier", -1.0), run_time=0.5)
        _done(self)


class B11_FirstRun(Scene):
    def construct(self):
        belt = make_original("conveyor", height=2.2, x=-3.9, y=-0.6)
        dash = _dashboard(0.6, -0.1)
        binder = make_original("evidence-binder", height=2.2, x=4.2, y=-0.3)
        self.add(belt, dash, binder, _label("7 requests", -3.9, -2.25), _label("0 errors", 0.6, -1.5),
                 _label("balanced", 4.2, -1.95), _tag("real run, Oct 9, 2026", x=-4.3))
        twin = belt.parts["parcel"].copy()
        _cue(self, "ran")
        _play(self, _move(belt, "parcel"), run_time=0.7)
        _cue(self, "twice")
        _play(self, FadeIn(twin), run_time=0.3)
        _play(self, twin.animate.shift(belt.action_vectors["parcel"] * 0.72), run_time=0.6)
        _cue(self, "errors")
        _play(self, Create(check(0.6, 1.3, s=0.22)), run_time=0.35)
        _cue(self, "balanced")
        _play(self, _move(binder, "cover"), run_time=0.5)
        _done(self)


class B13_Risk(Scene):
    def construct(self):
        bench = make_original("experiment-bench", height=2.6, x=-3.0, y=-0.3)
        desk = make_original("agent-workstation", height=2.2, x=2.8, y=-0.2)
        self.add(bench, desk, _label("incidents", -3.0, -2.15), _label("agent", 2.8, -1.85), _tag())
        pointer = cursor(-2.55, 1.55)
        _cue(self, "build")
        _play(self, FadeIn(pointer, shift=DOWN * 0.2), run_time=0.3)
        _play(self, _move(bench, "sample"), run_time=0.35)
        _cue(self, "agent")
        _play(self, MoveAlongPath(pointer, ArcBetweenPoints(np.array([-2.55, 1.55, 0]), np.array([3.0, 1.55, 0]), angle=-PI / 4)),
              run_time=0.7)
        _cue(self, "easy")
        _play(self, Create(ArcBetweenPoints(np.array([1.3, -1.45, 0]), np.array([-1.3, -1.45, 0]), angle=-PI / 3,
                                            color=KRAFT_DEEP, stroke_width=6)), run_time=0.6)
        _done(self)


class B14_HeldOut(Scene):
    def construct(self):
        shelves = make_original("version-shelves", height=2.8, x=-3.4, y=-0.1)
        vault = make_original("secure-vault", height=2.8, x=2.6, y=-0.1)
        vault.parts["lock-bar"].shift(vault.action_vectors["lock-bar"])  # starts unlocked
        box = _crate(-0.25, -0.85, s=0.8)
        self.add(shelves, vault, box, _label("answers first", -3.4, -2.05), _label("held out", 2.6, -2.05), _tag())
        _cue(self, "answers")
        _play(self, _move(shelves, "selected-version"), run_time=0.5)
        _cue(self, "held-out")
        _play(self, box.animate.move_to([1.25, -0.95, 0]), run_time=0.5)
        _play(self, _move(vault, "lock-bar", -1.0), run_time=0.35)
        _cue(self, "failures")
        _play(self, FadeIn(_slip(5.3, -0.4), shift=UP * 0.2), run_time=0.4)
        _done(self)


class B15_Why(Scene):
    def construct(self):
        trays = make_original("comparison-trays", height=3.0, x=0.0, y=-0.4)
        trays.parts["sample-b"].shift(trays.action_vectors["sample-b"])  # the new skill is not in its tray yet
        self.add(trays, _label("show off", -3.4, -0.95), _label("learn", 3.2, -0.95), _tag())
        _cue(self, "small")
        _play(self, FadeIn(_crate(-4.6, 1.3, s=0.8), shift=DOWN * 0.3), run_time=0.45)
        _cue(self, "jobs")
        _play(self, FadeIn(_slip(-2.9, 1.45, s=0.7), shift=DOWN * 0.2), run_time=0.35)
        _cue(self, "courses")
        _play(self, FadeIn(_slip(3.2, 1.45, s=0.7), shift=DOWN * 0.2), FadeIn(_slip(4.6, 1.45, s=0.7), shift=DOWN * 0.2),
              run_time=0.4)
        _cue(self, "learning")
        _play(self, _move(trays, "sample-b", -1.0), run_time=0.6)
        _done(self)


class B16_Record(Scene):
    def construct(self):
        binder = make_original("evidence-binder", height=2.6, x=-4.0, y=0.5)
        repo = make_original("release-parcel", height=1.9, x=4.9, y=-1.15)
        self.add(binder, _label("co-op record", -4.0, -1.25), _tag())
        _cue(self, "co-op")
        _play(self, _move(binder, "cover"), run_time=0.6)
        for word, x in (("data-loss", -1.0), ("H", 0.8), ("money-unit", 2.6)):
            _cue(self, word)
            _play(self, FadeIn(_slip(x, 0.55), shift=UP * 0.2), run_time=0.3)
            _play(self, Create(check(x, 1.5, s=0.2)), run_time=0.25)
        _cue(self, "private")
        _play(self, FadeIn(_label("private code", 0.8, -0.45)), run_time=0.4)
        _cue(self, "EventEase")
        _play(self, FadeIn(repo, shift=UP * 0.3), FadeIn(_label("EventEase", 4.9, -2.6)), run_time=0.5)
        _done(self)


class B17_New(Scene):
    def construct(self):
        desk = make_original("agent-workstation", height=2.6, x=-3.8, y=-0.2)
        self.add(desk, _label("new to me", -3.8, -2.05), _tag())
        spots = [(-0.6, 0.75), (1.2, 0.75), (3.0, 0.75), (4.8, 0.75), (0.3, -1.05), (2.1, -1.05), (3.9, -1.05)]
        words = ["Kafka", "Kubernetes", "Telemetry", "loop", "server", "Lang", "evaluation"]
        for word, (x, y) in zip(words, spots):
            _cue(self, word)
            _play(self, FadeIn(_crate(x, y, s=0.75), shift=DOWN * 0.35), run_time=0.2 if word == "Kafka" else 0.3)
        _done(self)


class B18_ExistsWill(Scene):
    def construct(self):
        binder = make_original("evidence-binder", height=2.0, x=-3.8, y=-0.2)
        ghosts = VGroup(_ghost(make_original("server-tower", height=2.2, x=0.6, y=-0.1)),
                        _ghost(make_original("agent-workstation", height=1.9, x=2.75, y=-0.2)),
                        _ghost(make_original("experiment-bench", height=1.5, x=5.0, y=-0.3)))
        self.add(binder, check(-3.8, 1.25, s=0.22), _label("exists", -3.8, -1.75), _label("will exist", 2.75, -1.75), _tag())
        _cue(self, "else")
        _play(self, Create(ghosts[0]), run_time=0.5)
        _cue(self, "exist", nth=2)
        _play(self, Create(ghosts[1]), Create(ghosts[2]), run_time=0.5)
        _done(self)


class BOUT_Title(Scene):
    def construct(self):
        tower = make_original("server-tower", height=2.8, x=-3.7, y=0.0)
        self.add(tower, T("Klaxon", 110).move_to([1.7, 0.5, 0]), T("Aravind Sundaravadivelu", 44).move_to([1.7, -0.8, 0]))
        _cue(self, "Aravind")
        _play(self, Create(check(-1.95, 1.35, s=0.24)), run_time=0.35)
        _cue(self, "Sundaravadivelu")
        _play(self, FadeIn(Dot([-3.7, 1.75, 0], radius=0.13, color=TERRA)), run_time=0.3)
        _done(self)
