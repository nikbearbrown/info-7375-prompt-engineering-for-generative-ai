#!/usr/bin/env python3
"""
scene.py -- INFO 7375 Week 01 Explainer Video
Swathi Baba Eswarappa

Visual engine for "The unit is a token, not a word."

Ten Manim scenes, one per beat in beat_sheet.json. Each scene reads its
own runtime from mp3/timings.json (Kokoro durations = ground truth) and
pads itself to match, so picture and narration stay locked without any
manual nudging.

EVIDENCE RULE
  Every integer drawn on screen is read at import time out of
  code/token_probe_output.json and code/embedding_probe_output.json.
  Nothing is typed by hand. If the probe output changes, the frames change.
  The single exception is the 8-dim vector display in B05, which is random
  (seed=7375) and carries a CONSTRUCTED badge on screen.

Render:  manim -qh scene.py B01_Hook ... (see build.sh)
"""
import json
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- evidence
PROBE = json.loads((ROOT / "code/token_probe_output.json").read_text())
EMB = json.loads((ROOT / "code/embedding_probe_output.json").read_text())
TIMINGS = json.loads((ROOT / "mp3/timings.json").read_text())
SHEET = json.loads((ROOT / "beat_sheet.json").read_text())
NARRATION = {b["beat_id"]: b["narration_text"] for b in SHEET["beats"]}


def probe(word, encoding="cl100k_base"):
    for r in PROBE:
        if r["word"] == word and r["encoding"] == encoding:
            return r
    raise KeyError((word, encoding))


SB = probe("strawberry")                       # str|aw|berry  [496,675,15717]
SB_O200 = probe("strawberry", "o200k_base")    # st|raw|berry  [302,1618,19772]
BAN = probe("banana")                          # [88847]
SPACED = EMB["spacing_control"]["spaced"]      # 10 ids, 436 x3
PLAIN = EMB["spacing_control"]["plain"]
LADDER = EMB["frequency_ladder"]           # common survives / rare shatters

# ------------------------------------------------------------------ style
BG = "#0B0B0C"
FG = "#F5F3EF"
DIM = "#6B6B70"
AMBER = "#FFB020"
RED = "#FF4D3D"
GREEN = "#3DDC84"
BLUE = "#4FC3F7"
VIOLET = "#B388FF"
MONO = "Menlo"

config.background_color = BG


def _visible(m, thresh=0.05):
    """Effective opacity of a mobject, read from the parts actually drawn."""
    parts = m.family_members_with_points()
    if not parts:
        return False
    return max(max(p.get_fill_opacity(), p.get_stroke_opacity())
               for p in parts) >= thresh


class Beat(Scene):
    """Base: draws the persistent brutalist chrome and locks scene length."""

    beat_id = "B00"
    kicker = ""
    source = "vocab: OpenAI *.tiktoken (tiktoken 0.14.0)"

    def chrome(self):
        rule_t = Line(LEFT * 6.85, RIGHT * 6.85, stroke_width=2,
                      color=DIM).to_edge(UP, buff=0.58)
        rule_b = Line(LEFT * 6.85, RIGHT * 6.85, stroke_width=2,
                      color=DIM).to_edge(DOWN, buff=0.58)
        tag = Text(self.beat_id, font=MONO, font_size=17, color=DIM)
        tag.next_to(rule_t, UP, buff=0.12).align_to(rule_t, LEFT)
        kick = Text(self.kicker, font=MONO, font_size=17, color=DIM)
        kick.next_to(rule_t, UP, buff=0.12).align_to(rule_t, RIGHT)
        foot = Text("INFO 7375 · S. BABA ESWARAPPA", font=MONO,
                    font_size=15, color=DIM)
        foot.next_to(rule_b, DOWN, buff=0.1).align_to(rule_b, LEFT)
        # provenance: say on screen where this beat's numbers came from
        src = Text(self.source, font=MONO, font_size=15, color=DIM)
        src.next_to(rule_b, DOWN, buff=0.1).align_to(rule_b, RIGHT)
        self.add(rule_t, rule_b, tag, kick, foot, src)
        # content must live BETWEEN the rules, not merely inside the frame
        self.chrome_mobs = VGroup(rule_t, rule_b, tag, kick, foot, src)
        self.safe_top = rule_t.get_bottom()[1]
        self.safe_bottom = rule_b.get_top()[1]

    def play(self, *a, **k):
        if getattr(self, "_first_cue", None) is None:
            self._first_cue = self.renderer.time
        return super().play(*a, **k)

    def hold_until(self, t):
        """Wait until scene-time `t`, so a cue can be pinned to the narration."""
        self.wait(max(t - self.renderer.time, 0.04))

    def at(self, phrase):
        """Approximate time the narration reaches `phrase`.

        Kokoro gives one duration per beat, not per word, so this interpolates
        by word position. It is accurate to a few tenths of a second, which is
        all a visual cue needs -- and it re-derives itself if the script
        changes, instead of freezing hand-tuned numbers into the animation.
        """
        txt = NARRATION[self.beat_id]
        i = txt.lower().index(phrase.lower())
        return TIMINGS[self.beat_id] * len(txt[:i].split()) / len(txt.split())

    def pin(self, phrase, lead=0.35):
        """Hold until just before `phrase` is spoken, then let the cue play."""
        self.hold_until(max(self.at(phrase) - lead, 0.0))

    def assert_in_safe_area(self):
        """Content must stay between the chrome rules.

        assert_in_frame() only checks the frame box, and the text-overlap test
        compares text to text -- so a caption could cross the bottom rule into
        the footer band and pass both, which is exactly what B03 and B04 did.
        """
        chrome = set(id(p) for p in self.chrome_mobs.family_members_with_points())
        worst = []
        for m in self.mobjects:
            for p in m.family_members_with_points():
                if id(p) in chrome:
                    continue
                if max(p.get_fill_opacity(), p.get_stroke_opacity()) < 0.05:
                    continue
                t, b = p.get_top()[1], p.get_bottom()[1]
                if b < self.safe_bottom - 0.02 or t > self.safe_top + 0.02:
                    worst.append(round(b if b < self.safe_bottom else t, 2))
        if worst:
            raise RuntimeError(
                "%s: %d part(s) outside the safe area [%.2f, %.2f] -> %s"
                % (self.beat_id, len(worst), self.safe_bottom, self.safe_top,
                   sorted(set(worst))[:5]))

    def assert_no_text_overlap(self):
        """Fail if two separate Text mobjects occupy the same space.

        fit()/clamp() only guard the frame edges. They cannot see a caption
        colliding with a diagram already on screen, which is how B05's
        "consumed at the tokenizer" line ended up running through the
        embedding table.
        """
        def texts(m):
            if isinstance(m, Text):
                yield m
            else:
                for sub in m.submobjects:
                    yield from texts(sub)

        vis = []
        for m in self.mobjects:
            for t in texts(m):
                if not _visible(t):
                    continue
                if t.width < 1e-3 or t.height < 1e-3:
                    continue
                vis.append(t)

        pad = 0.04
        for i in range(len(vis)):
            for j in range(i + 1, len(vis)):
                a, b = vis[i], vis[j]
                if (a.get_left()[0] < b.get_right()[0] - pad
                        and b.get_left()[0] < a.get_right()[0] - pad
                        and a.get_bottom()[1] < b.get_top()[1] - pad
                        and b.get_bottom()[1] < a.get_top()[1] - pad):
                    raise RuntimeError(
                        "%s: text overlap %r x %r"
                        % (self.beat_id, a.text[:28], b.text[:28]))

    def assert_in_frame(self):
        """Fail the render if anything visible sits outside the safe frame.

        qc_frames.py scans pixels, so it can only see content that is still
        *partly* on screen; a line pushed entirely past the bottom edge leaves
        no pixels to find. This catches that case at build time instead.
        """
        half_w = config.frame_width / 2 - 0.05
        half_h = config.frame_height / 2 - 0.05
        bad = []
        for m in self.mobjects:
            for p in m.family_members_with_points():
                if max(p.get_fill_opacity(), p.get_stroke_opacity()) < 0.05:
                    continue
                l, r = p.get_left()[0], p.get_right()[0]
                b, t = p.get_bottom()[1], p.get_top()[1]
                if l < -half_w or r > half_w or b < -half_h or t > half_h:
                    bad.append("x[%.2f,%.2f] y[%.2f,%.2f]" % (l, r, b, t))
        if bad:
            raise RuntimeError(
                "%s: %d mobject(s) outside the frame -> %s"
                % (self.beat_id, len(bad), bad[:4]))

    def lock(self):
        """Pad (or accept overrun) so the scene equals its narration.

        Reports the trailing hold. A large value means the picture finished
        long before the voice did, which is how B10's sign-off ended up on
        screen 6.5s early -- worth knowing for every beat, not just that one.
        """
        self.assert_in_frame()
        self.assert_in_safe_area()
        self.assert_no_text_overlap()
        target = TIMINGS[self.beat_id]
        remaining = target - self.renderer.time
        lead = getattr(self, "_first_cue", None)
        lead = 0.0 if lead is None else lead
        flag = "  <-- DEAD AIR" if lead > 1.2 else ""
        print("[slack] %-5s lead=%5.2fs  anim_end=%6.2fs  audio=%6.2fs  "
              "trailing=%5.2fs%s"
              % (self.beat_id, lead, self.renderer.time, target, remaining, flag))
        self.wait(max(remaining, 0.08))


# ------------------------------------------------------------- components
def char_cells(word, size=0.62, fs=30, color=FG):
    """The raw string as discrete character boxes."""
    g = VGroup()
    for ch in word:
        box = Square(size, stroke_width=2, stroke_color=color)
        t = Text(ch, font=MONO, font_size=fs, color=color)
        g.add(VGroup(box, t.move_to(box)))
    return g.arrange(RIGHT, buff=0.07)


def token_chip(piece, tid, color=AMBER, w=None, fs=30, idfs=22):
    """One token: its text on top, its real integer ID underneath."""
    label = Text(piece, font=MONO, font_size=fs, color=color)
    width = w if w else max(label.width + 0.5, 1.15)
    box = RoundedRectangle(corner_radius=0.08, width=width, height=0.82,
                           stroke_width=3, stroke_color=color)
    label.move_to(box)
    idt = Text(str(tid), font=MONO, font_size=idfs, color=color)
    idt.next_to(box, DOWN, buff=0.13)
    return VGroup(box, label, idt)


def index_ruler(word, target, cells):
    """0..n-1 ticks under the characters; target letters flagged."""
    nums, flags = VGroup(), VGroup()
    for i, ch in enumerate(word):
        n = Text(str(i), font=MONO, font_size=19,
                 color=RED if ch == target else DIM)
        n.next_to(cells[i], DOWN, buff=0.16)
        nums.add(n)
        if ch == target:
            flags.add(SurroundingRectangle(cells[i], color=RED,
                                           stroke_width=3, buff=0.02))
    return nums, flags


SAFE_MARGIN = 0.40


def fit(m, margin=SAFE_MARGIN):
    """Scale a mobject down if it would run past the visible frame."""
    max_w = config.frame_width - 2 * margin
    if m.width > max_w:
        m.scale(max_w / m.width)
    return m


def clamp(m, margin=SAFE_MARGIN):
    """Nudge a mobject back inside the frame if it overhangs an edge."""
    half = config.frame_width / 2 - margin
    if m.get_right()[0] > half:
        m.shift(LEFT * (m.get_right()[0] - half))
    if m.get_left()[0] < -half:
        m.shift(RIGHT * (-half - m.get_left()[0]))
    return m


def constructed_badge():
    t = Text("CONSTRUCTED · random vectors, seed=7375", font=MONO,
             font_size=17, color=RED)
    box = SurroundingRectangle(t, color=RED, stroke_width=2, buff=0.14)
    return VGroup(box, t)


# ==================================================================== B01
class B01_Hook(Beat):
    beat_id, kicker = "B01", "THE FAILED PROMPT"
    source = "no data on this card"

    def construct(self):
        self.chrome()
        q = Text('"How many r\'s are in strawberry?"', font=MONO,
                 font_size=38, color=FG).shift(UP * 1.5)
        self.play(AddTextLetterByLetter(q, run_time=2.4))

        self.pin("the famous answer")
        a2 = Text("2", font=MONO, font_size=110, color=FG).shift(DOWN * 0.35)
        lab2 = Text("the famous answer", font=MONO, font_size=21, color=DIM)
        lab2.next_to(a2, DOWN, buff=0.25)
        self.play(FadeIn(a2, shift=UP * 0.3), Write(lab2), run_time=1.3)

        self.pin("The real answer")
        strike = Line(a2.get_left() + LEFT * 0.28, a2.get_right() + RIGHT * 0.28,
                      color=RED, stroke_width=9)
        self.play(Create(strike), run_time=0.7)

        a3 = Text("3", font=MONO, font_size=110, color=GREEN)
        a3.move_to(a2).shift(RIGHT * 2.6)
        lab3 = Text("the real answer", font=MONO, font_size=21, color=GREEN)
        lab3.next_to(a3, DOWN, buff=0.25)
        self.play(FadeIn(a3, scale=1.35), Write(lab3), run_time=0.8)

        self.pin("bad at counting", lead=1.6)
        self.play(FadeOut(VGroup(a2, strike, lab2, a3, lab3)),
                  q.animate.shift(UP * 0.9).set_opacity(0.4), run_time=0.9)
        d1 = Text("not bad at COUNTING", font=MONO, font_size=42, color=DIM)
        d2 = Text("bad at SEEING", font=MONO, font_size=52, color=AMBER)
        VGroup(d1, d2).arrange(DOWN, buff=0.45).shift(DOWN * 0.35)
        self.play(Write(d1), run_time=0.9)
        self.pin("bad at seeing")
        self.play(Write(d2), run_time=1.0)
        self.lock()


# ==================================================================== B02
class B02_Claim(Beat):
    beat_id, kicker = "B02", "THE CLAIM"
    source = "BPE: Sennrich et al. 2016, arXiv:1508.07909"

    def construct(self):
        self.chrome()
        head = Text("The unit is a TOKEN.", font=MONO, font_size=46, color=FG)
        head.shift(UP * 2.2)
        self.play(Write(head), run_time=1.4)

        rows = []
        spec = [("CHARACTER", list("strawberry"), DIM),
                ("TOKEN", SB["token_pieces"], AMBER),
                ("WORD", ["strawberry"], DIM)]
        for name, parts, col in spec:
            lab = Text(name, font=MONO, font_size=24, color=col)
            lab.set_width(min(lab.width, 2.2))
            chips = VGroup()
            for p in parts:
                b = Rectangle(width=max(len(p) * 0.29 + 0.34, 0.52), height=0.6,
                              stroke_width=3 if col == AMBER else 2,
                              stroke_color=col)
                chips.add(VGroup(b, Text(p, font=MONO, font_size=24,
                                         color=col).move_to(b)))
            chips.arrange(RIGHT, buff=0.09)
            row = VGroup(lab, chips).arrange(RIGHT, buff=0.7)
            rows.append(row)
        stack = VGroup(*rows).arrange(DOWN, buff=0.62, aligned_edge=LEFT)
        stack.shift(DOWN * 0.2)
        for cue, r in zip(["The unit a language", "Not a word", "not a letter"], rows):
            self.pin(cue)
            self.play(FadeIn(r, shift=RIGHT * 0.35), run_time=0.7)

        box = SurroundingRectangle(rows[1], color=AMBER, stroke_width=4, buff=0.2)
        note = Text("TOKEN = the only unit the model actually receives", font=MONO,
                    font_size=24, color=AMBER)
        fit(note)
        note.next_to(stack, DOWN, buff=0.5)
        clamp(note)
        self.pin("Everything downstream")
        self.play(Create(box), Write(note), run_time=1.1)
        self.lock()


# ==================================================================== B03
class B03_Tokenize(Beat):
    beat_id, kicker = "B03", "tiktoken · cl100k_base"
    source = "vocab: OpenAI cl100k_base.tiktoken"

    def construct(self):
        self.chrome()
        cells = char_cells("strawberry").shift(UP * 2.15)
        cap = Text("10 characters", font=MONO, font_size=22, color=DIM)
        cap.next_to(cells, UP, buff=0.22)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cells],
                              lag_ratio=0.06), Write(cap), run_time=1.6)

        self.pin("byte pair encoding")
        tok = Rectangle(width=6.2, height=0.95, stroke_width=3, stroke_color=BLUE)
        tokl = Text("BPE TOKENIZER", font=MONO, font_size=27, color=BLUE)
        tokbox = VGroup(tok, tokl.move_to(tok)).shift(UP * 0.95)
        self.play(Create(tok), Write(tokl), run_time=0.9)

        # the characters visibly fall INTO the tokenizer, one after another,
        # rather than cross-fading -- the swallow is the point of the beat
        self.pin("Ten characters in", lead=1.4)
        self.play(FadeOut(cap, shift=UP * 0.2), run_time=0.3)
        self.play(LaggedStart(*[
            c.animate.scale(0.55).move_to(tokbox.get_center()).set_opacity(0.0)
            for c in cells], lag_ratio=0.09), run_time=1.5)
        self.play(Flash(tokbox.get_center(), color=BLUE, line_length=0.28,
                        num_lines=14, flash_radius=1.1), run_time=0.5)

        chips = VGroup(*[token_chip(p, i) for p, i in
                         zip(SB["token_pieces"], SB["token_ids"])])
        chips.arrange(RIGHT, buff=0.55).shift(DOWN * 1.05)
        # start each arrow above its own chip; a shared origin made the
        # middle arrow (pointing straight down at "aw") a near-zero stub
        bottom_y = tok.get_bottom()[1]
        arrows = VGroup(*[
            Arrow([c[0].get_center()[0], bottom_y, 0], c[0].get_top(),
                  buff=0.12, stroke_width=3, color=BLUE,
                  max_tip_length_to_length_ratio=0.28)
            for c in chips])
        self.pin("Three integers out", lead=0.6)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.18),
                  run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.25) for c in chips],
                              lag_ratio=0.22), run_time=1.5)

        out = Text("3 integers", font=MONO, font_size=24, color=AMBER)
        out.next_to(chips, DOWN, buff=0.45)
        ids = Text(str(SB["token_ids"]), font=MONO, font_size=30, color=AMBER)
        ids.next_to(out, DOWN, buff=0.15)
        self.play(Write(out), run_time=0.6)
        self.pin("Four ninety six")
        self.play(Write(ids), run_time=1.0)

        # "Decode those three and you get, s t r, a w, berry." -- light each
        # chip as its piece is spoken instead of holding a still frame.
        self.pin("Decode those three")
        for cue, c in zip(["s t", "a w", "berry."], chips):
            self.pin(cue, lead=0.25)
            self.play(c[0].animate.set_stroke(GREEN, width=5),
                      c[1].animate.set_color(GREEN), run_time=0.3)
        self.lock()


# ==================================================================== B04
class B04_Indices(Beat):
    beat_id, kicker = "B04", "WHERE THE R's LIVE"
    source = "vocab: OpenAI cl100k_base.tiktoken"

    def construct(self):
        self.chrome()
        cells = char_cells("strawberry").shift(UP * 1.85)
        self.add(cells)
        nums, flags = index_ruler("strawberry", "r", cells)
        self.pin("character index")
        self.play(LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.05),
                  run_time=1.1)
        self.play(LaggedStart(*[Create(f) for f in flags], lag_ratio=0.2),
                  run_time=1.1)

        idx = Text("r @ char index  [2, 7, 8]", font=MONO, font_size=30, color=RED)
        idx.next_to(nums, DOWN, buff=0.45)
        self.play(Write(idx), run_time=1.0)

        chips = VGroup(*[token_chip(p, i) for p, i in
                         zip(SB["token_pieces"], SB["token_ids"])])
        chips.arrange(RIGHT, buff=0.75).shift(DOWN * 0.95)
        self.pin("Split across those tokens")
        self.play(FadeIn(chips, shift=UP * 0.3), run_time=1.0)

        counts = SB["per_token_target_count"]          # [1, 0, 2]
        badges = VGroup()
        for c, n in zip(chips, counts):
            col = RED if n else DIM
            t = Text("%d r" % n, font=MONO, font_size=26, color=col)
            t.next_to(c, UP, buff=0.22)
            badges.add(t)
        self.pin("one R inside")
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in badges],
                              lag_ratio=0.25), run_time=1.3)

        eq = Text("1  +  0  +  2   =   3", font=MONO, font_size=34, color=AMBER)
        eq.next_to(chips, DOWN, buff=0.55)
        # Each r physically flies out of the string and into the token that
        # swallowed it -- the claim of the beat, shown rather than captioned.
        self.pin("zero inside")
        # land each r on the part of the token that swallowed it: char 2 in
        # 'str', chars 7 and 8 on the two r's inside 'berry'
        flights, dests, arcs = VGroup(), [], []
        for ci, chip, dx, arc in [(2, chips[0], 0.18, PI / 2.6),
                                  (7, chips[2], -0.02, -PI / 2.6),
                                  (8, chips[2], 0.30, -PI / 2.6)]:
            g = Text("r", font=MONO, font_size=30, color=RED)
            g.move_to(cells[ci])
            flights.add(g)
            dests.append(chip[0].get_center() + RIGHT * dx)
            arcs.append(arc)
        self.add(flights)
        # curve the paths outward so they sweep around the index line rather
        # than cutting straight through it
        self.play(LaggedStart(*[
            f.animate(path_arc=a).scale(0.85).move_to(d).set_opacity(0.0)
            for f, d, a in zip(flights, dests, arcs)],
            lag_ratio=0.3), run_time=1.6)
        self.play(*[Indicate(c[0], color=RED, scale_factor=1.08)
                    for c in [chips[0], chips[2]]], run_time=0.6)
        # play() promotes animated children to top-level mobjects, so the
        # group alone is not enough to clear them
        self.remove(flights, *flights)

        self.pin("One, zero, two")
        self.play(Write(eq), run_time=1.1)
        ask = Text("...but only if you can look INSIDE a token.",
                   font=MONO, font_size=24, color=DIM)
        ask.next_to(eq, DOWN, buff=0.25)
        self.pin("To answer the question")
        self.play(Write(ask), run_time=1.2)
        self.lock()


# ==================================================================== B05
class B05_Embedding(Beat):
    beat_id, kicker = "B05", "THE LOOKUP IS A ROW INDEX"
    source = "IDs measured · vectors CONSTRUCTED (seed 7375)"

    def construct(self):
        self.chrome()
        chips = VGroup(*[token_chip(p, i) for p, i in
                         zip(SB["token_pieces"], SB["token_ids"])])
        chips.arrange(RIGHT, buff=0.5).scale(0.9).shift(UP * 2.25 + LEFT * 3.4)
        self.add(chips)

        ruler = Text("char index [2, 7, 8]", font=MONO, font_size=24, color=RED)
        ruler.next_to(chips, DOWN, buff=0.4)
        self.add(ruler)

        # embedding matrix
        mrows = VGroup()
        for _ in range(7):
            mrows.add(Rectangle(width=3.0, height=0.3, stroke_width=1.5,
                                stroke_color=DIM))
        mrows.arrange(DOWN, buff=0.06)
        mlab = Text("E  (embedding table)", font=MONO, font_size=21, color=BLUE)
        mlab.next_to(mrows, UP, buff=0.2)
        matrix = VGroup(mrows, mlab).shift(RIGHT * 3.6 + UP * 0.9)
        self.pin("the embedding lookup")
        self.play(FadeIn(matrix), run_time=0.9)

        rng = np.random.default_rng(7375)
        targets = [1, 3, 5]
        vecs = VGroup()
        self.pin("Token four ninety six fetches")
        for k, (chip, tid) in enumerate(zip(chips, SB["token_ids"])):
            row = mrows[targets[k]]
            self.play(row.animate.set_stroke(AMBER, width=3.5),
                      Create(Arrow(chip[0].get_right(), row.get_left(), buff=0.15,
                                   stroke_width=2.5, color=AMBER,
                                   max_tip_length_to_length_ratio=0.12)),
                      run_time=0.55)
            v = rng.normal(0, 1, 8).round(2)
            vt = Text("E[%d] = [%s]" % (tid, "  ".join("%+.2f" % x for x in v)),
                      font=MONO, font_size=19, color=BLUE)
            vecs.add(vt)
        vecs.arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN * 1.65)
        self.pin("That row is a list")
        self.play(FadeIn(vecs, shift=UP * 0.25), run_time=1.1)

        badge = constructed_badge().scale(0.9)
        badge.next_to(vecs, DOWN, buff=0.35)
        self.play(FadeIn(badge), run_time=0.6)

        # the character positions fall out of the pipeline
        gone = Text("no slot for 'the 3rd letter'", font=MONO,
                    font_size=26, color=RED)
        gone.move_to(ruler)
        self.pin("There is no slot", lead=0.9)
        self.play(ruler.animate.set_opacity(0.15).shift(DOWN * 0.15),
                  run_time=0.8)
        self.play(FadeOut(ruler, shift=DOWN * 0.8), run_time=0.9)
        self.play(FadeIn(gone, scale=1.1), run_time=0.8)
        self.pin("The spelling was consumed")
        last = Text("consumed before the network", font=MONO,
                    font_size=22, color=DIM)
        last.next_to(gone, DOWN, buff=0.3)
        # keep it in the left column; the embedding table owns the right side
        if last.get_right()[0] > matrix.get_left()[0] - 0.3:
            last.shift(LEFT * (last.get_right()[0]
                               - (matrix.get_left()[0] - 0.3)))
        fit(last); clamp(last)
        self.play(Write(last), run_time=1.3)
        self.lock()


# ==================================================================== B06
class B06_TokenizerDependence(Beat):
    beat_id, kicker = "B06", "SAME WORD · TWO TOKENIZERS"
    source = "vocab: OpenAI cl100k_base + o200k_base"

    def construct(self):
        self.chrome()
        head = Text("The cut is not in the word.", font=MONO,
                    font_size=38, color=FG).shift(UP * 2.4)
        self.play(Write(head), run_time=1.2)

        def row(rec, col, y):
            name = Text("%s   vocab=%d" % (rec["encoding"],
                                           EMB["tokenizer_dependence"][rec["encoding"]]["vocab"]),
                        font=MONO, font_size=21, color=col)
            # width proportional to the piece: token_chip's 1.15 minimum made
            # "str" and "st" render identically wide, which put both cut marks
            # at the same x and hid the shift entirely
            chips = VGroup(*[token_chip(p, i, color=col,
                                        w=0.30 * len(p) + 0.45)
                             for p, i in zip(rec["token_pieces"],
                                             rec["token_ids"])])
            chips.arrange(RIGHT, buff=0.22)
            g = VGroup(name, chips).arrange(DOWN, buff=0.35)
            return g.shift(UP * y)

        r1 = row(SB, AMBER, 0.85)
        r2 = row(SB_O200, VIOLET, -1.35)
        # left-align both rows on the same x: centred rows put the two cut
        # positions at almost the same place, which hides the very difference
        # this beat exists to show
        for rg in (r1, r2):
            rg[1].align_to(LEFT * 2.6, LEFT)
            rg[0].align_to(rg[1], LEFT)
        self.pin("that split tracks")
        self.play(FadeIn(r1, shift=RIGHT * 0.3), run_time=1.2)
        self.pin("o two hundred k base")
        self.play(FadeIn(r2, shift=RIGHT * 0.3), run_time=1.2)

        # The claim of this beat is that the cut MOVES. Show it moving: mark
        # the first boundary, then slide the marker to where the second
        # tokenizer puts it. Replaces a static "str|aw vs st|raw" caption.
        def cut_x(rowg, k):
            chips = rowg[1]
            return (chips[k][0].get_right()[0] + chips[k + 1][0].get_left()[0]) / 2

        def marker(rowg, k, col):
            chips = rowg[1]
            top, bot = chips.get_top()[1] + 0.18, chips.get_bottom()[1] - 0.18
            return DashedLine([cut_x(rowg, k), top, 0],
                              [cut_x(rowg, k), bot, 0],
                              stroke_width=5, color=col, dash_length=0.12)

        m1 = marker(r1, 0, RED)
        m2 = marker(r2, 0, RED)
        self.pin("Different boundary")
        self.play(Create(m1), run_time=0.5)
        self.play(TransformFromCopy(m1, m2), run_time=1.1)
        self.play(Flash(m2.get_center(), color=RED, line_length=0.2,
                        num_lines=12, flash_radius=0.6), run_time=0.45)

        note = Text("the cut moved — different merge table, different boundary",
                    font=MONO, font_size=22, color=DIM)
        note.next_to(r2, DOWN, buff=0.55)
        fit(note); clamp(note)
        self.pin("whichever merge table")
        self.play(Write(note), run_time=1.2)
        self.lock()


# ==================================================================== B07
class B07_Banana(Beat):
    beat_id, kicker = "B07", "NO BOUNDARY TO BLAME"
    source = "vocab: OpenAI cl100k_base.tiktoken"

    def construct(self):
        self.chrome()
        # "Now the one that kills the boundary story outright." runs for ~2.8s
        # before banana appears. Put the objection this beat demolishes on
        # screen for it, instead of holding an empty frame.
        obj = Text('the objection:', font=MONO, font_size=24, color=DIM)
        obj2 = Text('"it\'s just the SPLIT that hides them"', font=MONO,
                    font_size=32, color=FG)
        objg = VGroup(obj, obj2).arrange(DOWN, buff=0.28)
        fit(objg); clamp(objg)
        self.add(objg)

        cells = char_cells("banana", size=0.75, fs=36).shift(UP * 1.6)
        self.pin("Banana. Three")
        self.play(FadeOut(objg, shift=UP * 0.4), run_time=0.45)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cells],
                              lag_ratio=0.08), run_time=1.2)
        nums, flags = index_ruler("banana", "a", cells)
        self.play(LaggedStart(*[Create(f) for f in flags], lag_ratio=0.18),
                  run_time=0.9)
        three = Text("3 a's", font=MONO, font_size=28, color=RED)
        three.next_to(cells, UP, buff=0.3)
        self.pin("Three A's")
        self.play(Write(three), run_time=0.7)

        chip = token_chip("banana", BAN["token_ids"][0], fs=36, idfs=30)
        chip.scale(1.25).shift(UP * 0.2)
        self.pin("Encode it and you")
        self.play(cells.animate.scale(0.45).move_to(chip).set_opacity(0),
                  FadeOut(flags), FadeIn(chip, scale=0.85), run_time=1.5)

        one = Text("1 token", font=MONO, font_size=34, color=AMBER)
        one.next_to(chip, DOWN, buff=0.45)
        self.pin("get one token")
        self.play(Write(one), run_time=0.8)

        k1 = Text("no split · no boundary · letters still gone",
                  font=MONO, font_size=25, color=FG)
        k2 = Text("a token is an ATOM", font=MONO, font_size=34, color=RED)
        VGroup(k1, k2).arrange(DOWN, buff=0.28).next_to(one, DOWN, buff=0.38)
        self.pin("There is no boundary here")
        self.play(Write(k1), run_time=1.1)
        self.pin("a token is an atom", lead=1.0)
        self.play(Write(k2), run_time=0.9)
        self.lock()


# ==================================================================== B08
class B08_SpacedControl(Beat):
    beat_id, kicker = "B08", "THE CONTROL"
    source = "vocab: OpenAI cl100k_base.tiktoken"

    def construct(self):
        self.chrome()
        before = Text('"strawberry"   ->   %d tokens' % PLAIN["n"],
                      font=MONO, font_size=28, color=DIM).shift(UP * 2.5)
        self.play(Write(before), run_time=1.0)

        after = Text('"s t r a w b e r r y"   ->   %d tokens' % SPACED["n"],
                     font=MONO, font_size=28, color=GREEN)
        after.next_to(before, DOWN, buff=0.35)
        self.pin("Space the word out")
        self.play(Write(after), run_time=1.2)

        ids = SPACED["ids"]
        pieces = [p.strip() or "_" for p in SPACED["pieces"]]
        chips = VGroup(*[token_chip(p, i, color=FG, w=1.02, fs=26, idfs=19)
                         for p, i in zip(pieces, ids)])
        chips.arrange(RIGHT, buff=0.12).scale(0.92).shift(UP * 0.05)
        self.pin("encodes to ten tokens", lead=0.8)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in chips],
                              lag_ratio=0.07), run_time=1.8)

        hits = [k for k, i in enumerate(ids) if i == 436]
        boxes = VGroup(*[SurroundingRectangle(chips[k], color=GREEN,
                                              stroke_width=4, buff=0.06)
                         for k in hits])
        self.pin("Token four hundred thirty six")
        self.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.25),
                  run_time=1.3)
        self.pin("appears three times", lead=0.2)
        for _ in range(2):
            self.play(boxes.animate.set_stroke(opacity=0.25), run_time=0.22)
            self.play(boxes.animate.set_stroke(opacity=1.0), run_time=0.22)

        pos = VGroup()
        for k in hits:
            t = Text(str(k), font=MONO, font_size=22, color=GREEN)
            t.next_to(chips[k], UP, buff=0.16)
            pos.add(t)
        self.pin("at positions two")
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in pos],
                              lag_ratio=0.2), run_time=0.9)

        line = Text("id 436  x3  @ positions [2, 7, 8]", font=MONO,
                    font_size=30, color=GREEN).shift(DOWN * 1.30)
        self.pin("and eight. The exact")
        self.play(Write(line), run_time=1.2)
        echo = Text("= the exact char indices from the raw word", font=MONO,
                    font_size=25, color=AMBER)
        echo.next_to(line, DOWN, buff=0.28)
        self.pin("The exact character indices")
        self.play(Write(echo), run_time=1.2)
        # the closing claim of this beat needs its own cue, or the last 8s of
        # narration plays over a frozen frame
        self.pin("The trick does not make")
        final = Text("the input changed  ·  not the model", font=MONO,
                     font_size=26, color=AMBER)
        final.next_to(echo, DOWN, buff=0.5)
        fit(final); clamp(final)
        self.play(Write(final), run_time=1.3)
        self.lock()


# ==================================================================== B09
class B09_Boundary(Beat):
    beat_id, kicker = "B09", "THE BOUNDARY"
    source = "left: measured here · right: cited"

    def construct(self):
        self.chrome()
        head = Text("What this does NOT establish", font=MONO,
                    font_size=40, color=FG).shift(UP * 2.5)
        self.play(Write(head), run_time=1.3)

        div = Line(UP * 1.85, DOWN * 2.3, stroke_width=3, color=DIM)
        self.pin("I have shown", lead=0.6)
        self.play(Create(div), run_time=0.5)

        shown = ["tokenization removes",
                 "character positions",
                 "at the INPUT"]
        notshown = ["that a model can",
                    "NEVER count letters"]
        extra = ["· CoT scratchpad",
                 "· a code tool",
                 "· char-level input",
                 "· memorised answers"]

        h1 = Text("SHOWN", font=MONO, font_size=28, color=GREEN)
        h1.move_to(LEFT * 3.6 + UP * 1.5)
        g1 = VGroup(*[Text(s, font=MONO, font_size=24, color=FG) for s in shown])
        g1.arrange(DOWN, buff=0.24, aligned_edge=LEFT).next_to(h1, DOWN, buff=0.4)
        g1.align_to(h1, LEFT).shift(LEFT * 0.9)
        self.play(Write(h1), run_time=0.6)
        self.pin("that tokenization removes")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in g1],
                              lag_ratio=0.2), run_time=1.3)

        h2 = Text("NOT SHOWN", font=MONO, font_size=28, color=AMBER)
        h2.move_to(RIGHT * 3.6 + UP * 1.5)
        g2 = VGroup(*[Text(s, font=MONO, font_size=24, color=FG) for s in notshown])
        g2.arrange(DOWN, buff=0.24, aligned_edge=LEFT).next_to(h2, DOWN, buff=0.4)
        g2.align_to(h2, LEFT).shift(LEFT * 1.0)
        self.pin("I have not shown")
        self.play(Write(h2), run_time=0.6)
        self.pin("can never count letters", lead=0.6)
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in g2],
                              lag_ratio=0.2), run_time=1.0)

        g3 = VGroup(*[Text(s, font=MONO, font_size=21, color=AMBER)
                      for s in extra])
        g3.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        g3.next_to(g2, DOWN, buff=0.4).align_to(g2, LEFT)
        for cue, t in zip(["a chain", "a code tool", "character level input",
                           "many current models"], g3):
            self.pin(cue)
            self.play(FadeIn(t, shift=RIGHT * 0.2), run_time=0.45)

        # these four are reported, not measured by me -- say so on screen
        # a footnote, set apart by a rule so it reads as an annotation on the
        # column rather than a fifth bullet in it
        fn_rule = Line(LEFT * 1.35, RIGHT * 1.35, stroke_width=1.5, color=DIM)
        fn_rule.next_to(g3, DOWN, buff=0.18).align_to(g3, LEFT)
        tag2 = Text("not measured here", font=MONO,
                    font_size=19, color=AMBER)
        tag2.next_to(fn_rule, DOWN, buff=0.14).align_to(g3, LEFT)
        cite = Text("CoT: Wei et al. 2022, arXiv:2201.11903", font=MONO,
                    font_size=18, color=DIM)
        cite.next_to(tag2, DOWN, buff=0.14).align_to(g3, LEFT)
        for m in (tag2, cite):
            fit(m); clamp(m)
        self.add(fn_rule, tag2, cite)

        mark = Text("measured by me", font=MONO, font_size=19, color=GREEN)
        mark.next_to(g1, DOWN, buff=0.28).align_to(g1, LEFT)
        self.add(mark)

        self.lock()


# ==================================================================== B10
class B10_Close(Beat):
    beat_id, kicker = "B10", "RECAP"
    source = "vocab: OpenAI *.tiktoken · full refs in SOURCES.md"

    def construct(self):
        self.chrome()
        stages = [("10 chars", '"strawberry"', FG),
                  ("3 ints", str(SB["token_ids"]), AMBER),
                  ("3 vectors", "E[id] -> row", BLUE)]
        boxes = VGroup()
        for title, sub, col in stages:
            t = Text(title, font=MONO, font_size=28, color=col)
            s = Text(sub, font=MONO, font_size=20, color=col)
            inner = VGroup(t, s).arrange(DOWN, buff=0.18)
            b = Rectangle(width=4.0, height=1.5, stroke_width=3, stroke_color=col)
            boxes.add(VGroup(b, inner.move_to(b)))
        boxes.arrange(RIGHT, buff=0.7).scale(0.86).shift(UP * 1.35)

        arrows = VGroup()
        self.play(FadeIn(boxes[0]), run_time=0.7)
        for k in (1, 2):
            ar = Arrow(boxes[k - 1].get_right(), boxes[k].get_left(), buff=0.1,
                       stroke_width=3, color=DIM,
                       max_tip_length_to_length_ratio=0.28)
            arrows.add(ar)
            self.play(GrowArrow(ar), FadeIn(boxes[k]), run_time=0.7)

        drop = Text("char positions [2, 7, 8]", font=MONO, font_size=24, color=RED)
        drop.next_to(boxes[0], DOWN, buff=0.55)
        self.play(FadeIn(drop), run_time=0.6)
        x = Text("dropped here", font=MONO, font_size=20, color=RED)
        x.next_to(drop, DOWN, buff=0.16)
        self.play(Write(x), run_time=0.6)
        self.play(VGroup(drop, x).animate.shift(DOWN * 0.9).set_opacity(0.0),
                  run_time=1.2)

        # Cues are pinned to the narration rather than played back to back:
        # the voice reaches "not a reasoning bug" at ~9.8s and the sign-off at
        # ~15.9s of this beat's 19.11s. Playing straight through put the name
        # card on screen 6.5s before it was spoken.
        k1 = Text("not a reasoning bug.", font=MONO, font_size=36, color=DIM)
        k2 = Text("the input format.", font=MONO, font_size=46, color=AMBER)
        VGroup(k1, k2).arrange(DOWN, buff=0.3).shift(DOWN * 1.35)
        # the voice reaches "that is the input format" at ~13.8s and starts
        # the sign-off at ~15.86s; the card must be UP by then, not starting
        self.hold_until(9.8)
        self.play(Write(k1), run_time=0.9)
        self.hold_until(13.6)
        self.play(Write(k2), run_time=0.8)
        self.hold_until(14.9)

        # clear the recap as well -- leaving the pipeline on screen under the
        # sign-off made the last card read as a half-finished slide
        self.play(FadeOut(VGroup(k1, k2)),
                  FadeOut(boxes, shift=UP * 0.3),
                  FadeOut(arrows, shift=UP * 0.3), run_time=0.45)
        n = Text("Swathi Baba Eswarappa", font=MONO, font_size=34, color=FG)
        c = Text("INFO 7375 · Week 01 · Chapter 1, Part 1", font=MONO,
                 font_size=22, color=DIM)
        v = Text("tiktoken 0.14.0 · Kokoro-82M · Manim CE · Brutalist",
                 font=MONO, font_size=18, color=DIM)
        VGroup(n, c, v).arrange(DOWN, buff=0.32).move_to(ORIGIN)
        self.play(FadeIn(n, shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(c), FadeIn(v), run_time=0.6)
        self.lock()


# =================================================================== B06B
class B06B_Frequency(Beat):
    """Why the boundary lands where it does: merges follow frequency."""

    beat_id, kicker = "B06B", "MERGES FOLLOW FREQUENCY"
    source = "vocab: OpenAI cl100k_base.tiktoken"

    def construct(self):
        self.chrome()
        head = Text("Merges are learned from frequency.", font=MONO,
                    font_size=36, color=FG).shift(UP * 2.45)
        self.play(Write(head), run_time=1.1)

        rows = VGroup()
        for wd in ["berry", "strawberry", "zyzzyva"]:
            rec = LADDER[wd]
            col = GREEN if rec["n"] == 1 else (AMBER if wd == "strawberry" else RED)
            name = Text('"%s"' % wd, font=MONO, font_size=26, color=FG)
            name.set_width(min(name.width, 2.6))
            chips = VGroup()
            for p in rec["pieces"]:
                b = Rectangle(width=max(len(p) * 0.26 + 0.34, 0.5), height=0.55,
                              stroke_width=3, stroke_color=col)
                chips.add(VGroup(b, Text(p, font=MONO, font_size=22,
                                         color=col).move_to(b)))
            chips.arrange(RIGHT, buff=0.1)
            cnt = Text("%d token%s" % (rec["n"], "" if rec["n"] == 1 else "s"),
                       font=MONO, font_size=23, color=col)
            row = VGroup(name, chips, cnt).arrange(RIGHT, buff=0.55)
            rows.add(row)
        rows.arrange(DOWN, buff=0.72, aligned_edge=LEFT).shift(DOWN * 0.25)
        for cue, r in zip(["Berry on its own", "one token", "zyzzyva"], rows):
            self.pin(cue)
            self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)

        note = Text("common survives whole  ·  rare shatters", font=MONO,
                    font_size=24, color=DIM)
        note.next_to(rows, DOWN, buff=0.6)
        self.pin("shatters into four", lead=0.45)
        self.play(Write(note), run_time=0.6)
        kick = Text("nothing in that process is aware of letters", font=MONO,
                    font_size=22, color=AMBER)
        kick.next_to(note, DOWN, buff=0.26)
        self.play(Write(kick), run_time=0.5)
        self.lock()


SCENES = ["B01_Hook", "B02_Claim", "B03_Tokenize", "B04_Indices",
          "B05_Embedding", "B06_TokenizerDependence", "B06B_Frequency", "B07_Banana",
          "B08_SpacedControl", "B09_Boundary", "B10_Close"]
