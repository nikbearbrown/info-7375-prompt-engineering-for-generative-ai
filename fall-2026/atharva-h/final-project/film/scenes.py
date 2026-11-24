"""scenes.py — Manim scenes for atharva-sponsorsql-final (INFO 7375 final project demo).

Every number and output line shown comes from saved output of the real system
(fall-2026/atharva-h/final-project: evidence/ and evals/results/), re-typeset for
legibility and labelled as such on screen. Scripted test inputs are labelled.

Pacing: scenes read their measured narration length and text from beat_sheet.json
and land events on spoken phrases. No LaTeX. One terracotta accent per scene.
"""
import json
import os

import numpy as np
from manim import *

# ── Palette ──────────────────────────────────────────────────────────────────
BG    = ManimColor("#FAF9F5")
INK   = ManimColor("#3D3929")
ACC   = ManimColor("#D97757")
SOFT  = ManimColor("#6B6858")
GHOST = ManimColor("#C9C4B4")
CARD  = ManimColor("#FFFFFF")
KRAFT = ManimColor("#F3E9D8")

# ── Pacing from the beat sheet ───────────────────────────────────────────────
_SHEET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beat_sheet.json")
_FALLBACK = {"B00": 15.0, "B02": 20.25, "B03": 20.76, "B04": 16.19, "B05": 16.04, "B06": 16.04, "B07": 14.63, "B08": 13.89, "B09": 16.11, "B10": 15.57, "B11": 19.03, "B12": 8.94}


def _beat(bid):
    try:
        with open(_SHEET) as f:
            for b in json.load(f)["beats"]:
                if b["beat_id"] == bid:
                    return b
    except Exception:
        pass
    return None


class Pacer:
    """Tracks elapsed time; waits until a spoken phrase, then pads to the audio length."""

    def __init__(self, scene, bid):
        scene.camera.background_color = BG
        self.s, self.bid = scene, bid
        b = _beat(bid)
        self.D = float((b or {}).get("actual_duration_s") or _FALLBACK[bid])
        self.text = (b or {}).get("narration_text", "")
        self.t = 0.0

    def until(self, phrase, fallback):
        i = self.text.find(phrase) if self.text else -1
        f = i / len(self.text) if i >= 0 else fallback
        target = min(f * self.D, self.D - 1.4)
        if target > self.t + 0.05:
            self.s.wait(target - self.t)
            self.t = target

    def play(self, *anims, run_time=0.8):
        self.s.play(*anims, run_time=run_time)
        self.t += run_time

    def finish(self):
        rest = self.D - self.t
        if rest > 0.05:
            self.s.wait(rest)
            self.t = self.D


# ── Drawing helpers ──────────────────────────────────────────────────────────
def T(text, size=32, color=None, weight=None):
    # Render at 4x and scale down: Pango drops word spaces at small font sizes.
    kw = {"font_size": size * 4, "color": color or INK}
    if weight:
        kw["weight"] = weight
    return Text(text, **kw).scale(0.25)


def M(text, size=24, color=None):
    return Text(text, font_size=size, color=color or INK, font="Menlo")


def keep_in(mob, xr=6.0, yr=3.15):
    """Shift a mobject so its whole box sits inside the safe area."""
    dx = min(0, xr - mob.get_right()[0]) + max(0, -xr - mob.get_left()[0])
    dy = min(0, yr - mob.get_top()[1]) + max(0, -yr - mob.get_bottom()[1])
    mob.shift(RIGHT * dx + UP * dy)
    return mob


def fit(mob, w):
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


def box(w, h, label=None, size=32, fill=CARD):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.14, color=INK,
                         stroke_width=4, fill_color=fill, fill_opacity=1)
    if label is None:
        return VGroup(r)
    return VGroup(r, fit(T(label, size), w - 0.3).move_to(r))


def page(w=1.3, h=1.6, lines=4, fill=CARD):
    r = Rectangle(width=w, height=h, color=INK, stroke_width=4, fill_color=fill, fill_opacity=1)
    ls = VGroup(*[Line(LEFT * (w / 2 - 0.2), RIGHT * (w / 2 - 0.2 - (0.25 if i % 2 else 0)),
                       color=GHOST, stroke_width=5).shift(UP * (h / 2 - 0.35 - i * 0.3))
                  for i in range(lines)])
    ls.move_to(r).align_to(r, UP).shift(DOWN * 0.3)
    return VGroup(r, ls)


def check_mark(c, s=0.35, color=ACC):
    return VMobject(color=color, stroke_width=9).set_points_as_corners(
        [c + np.array([-s, 0, 0]), c + np.array([-s * 0.3, -s * 0.7, 0]), c + np.array([s, s * 0.8, 0])])


def tag(text, size=28):
    t = T(text, size, weight="BOLD")
    p = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.35, corner_radius=0.2,
                         color=INK, stroke_width=3, fill_color=KRAFT, fill_opacity=1)
    return VGroup(p, t.move_to(p))


def constructed(text="CONSTRUCTED", note="mock-up · nothing here is real data"):
    g = VGroup(T(text, 26, SOFT, weight="BOLD"), T(note, 22, SOFT)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
    return keep_in(g.to_corner(DL, buff=1.0))


# ── Helpers for this film ───────────────────────────────────────────────────
def part_tag(n, name):
    t = tag(f"{n} · {name}", 24)
    t.to_corner(UL, buff=0.75)
    return keep_in(t)


def caption(text, size=22):
    c = fit(T(text, size, SOFT), 11.6).move_to([0, -3.0, 0])
    return keep_in(c)


def label_tr(text, size=20):
    c = T(text, size, SOFT)
    c.to_corner(UR, buff=0.75)
    return keep_in(c)


def terminal(lines, width, size=22, pad=0.35):
    texts = VGroup(*[M(line.rstrip(), size, CARD) for line in lines]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    for line, mob in zip(lines, texts):
        indent = len(line) - len(line.lstrip(" "))
        if indent:
            mob.shift(RIGHT * 0.14 * indent)
    fit(texts, width - 2 * pad)
    panel = RoundedRectangle(width=width, height=texts.height + 2 * pad, corner_radius=0.12,
                             color=INK, stroke_width=4, fill_color=INK, fill_opacity=1)
    texts.move_to(panel).align_to(panel, LEFT).shift(RIGHT * pad)
    return VGroup(panel, texts)


def card(lines, w, h, title_size=30, body_size=22):
    title = fit(T(lines[0], title_size, weight="BOLD"), w - 0.4)
    body = [fit(T(x, body_size), w - 0.4) for x in lines[1:]]
    content = VGroup(title, *body).arrange(DOWN, buff=0.1)
    r = RoundedRectangle(width=w, height=h, corner_radius=0.14, color=INK, stroke_width=4,
                         fill_color=BG, fill_opacity=1)
    return VGroup(r, content.move_to(r))


# ═════════════════════════════════════════════════════════════════════════════
class B00_Intro(Scene):
    def construct(self):
        p = Pacer(self, "B00")
        pt = part_tag(1, "Executive summary")
        cap = caption("H-1B: the main U.S. work visa for skilled jobs")
        p.play(FadeIn(pt), FadeIn(cap), run_time=0.8)

        p.until("International students", 0.25)
        q = card(["A student asks:", "Which employers file H-1Bs", "for Data Analyst jobs?"], 5.0, 2.3, 30, 30)
        q.move_to([3.4, 0.9, 0])
        p.play(FadeIn(q, shift=LEFT * 0.3), run_time=0.8)

        p.until("public", 0.62)
        frame = Rectangle(width=5.4, height=4.0, color=INK, stroke_width=4, fill_color=CARD, fill_opacity=1)
        frame.move_to([-3.3, -0.1, 0])
        rows = VGroup(*[Line(frame.get_left() + RIGHT * 0.0, frame.get_right(), color=INK, stroke_width=2)
                        .shift(UP * (frame.height / 2 - 0.5 - k * 0.44)) for k in range(8)])
        cols = VGroup(*[Line(frame.get_top(), frame.get_bottom(), color=INK, stroke_width=2)
                        .shift(RIGHT * (-frame.width / 2 + 1.1 * (k + 1))) for k in range(4)])
        rows.move_to(frame).shift(DOWN * 0.0)
        lab = T("Labor Department file: 437,496 filings", 26, weight="BOLD").next_to(frame, UP, buff=0.2)
        fit(lab, 5.6)
        p.play(Create(frame), Create(rows), Create(cols), FadeIn(lab), run_time=1.4)

        p.until("can't search", 0.88)
        mark = T("?", 110, ACC, weight="BOLD").move_to([3.4, -1.45, 0])
        p.play(FadeIn(mark, scale=0.6), run_time=0.6)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B02_Existing(Scene):
    def construct(self):
        p = Pacer(self, "B02")
        pt = part_tag(2, "Introduction")
        cap = caption("Sites reviewed online 2026-11-21 · ChatGPT reply saved word for word (2026-10-24)")
        a = card(["MyVisaJobs", "search by company,", "title, city, state"], 3.8, 2.1).move_to([-4.3, 1.1, 0])
        b = card(["H-1B salary explorer", "filter by employer,", "title, year, status"], 3.8, 2.1).move_to([0, 1.1, 0])
        p.play(FadeIn(pt), FadeIn(cap), FadeIn(a, shift=DOWN * 0.2), FadeIn(b, shift=DOWN * 0.2), run_time=1.0)

        p.until("chatbot", 0.35)
        c = card(["ChatGPT (my test)", "wrote a query, said 40,", "nothing checked it"], 3.8, 2.1).move_to([4.3, 1.1, 0])
        p.play(FadeIn(c, shift=DOWN * 0.2), run_time=0.7)

        p.until("adds two things", 0.72)
        s = card(["SponsorSQL adds", "the query and matching rows are shown  ·  its error rate is published"],
                 10.0, 1.5, 30, 24).move_to([-0.3, -1.45, 0])
        cm = check_mark(np.array([5.35, -1.45, 0]), 0.3)
        p.play(FadeIn(s, shift=UP * 0.2), run_time=0.7)
        p.play(Create(cm), run_time=0.5)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B03_Data(Scene):
    def construct(self):
        p = Pacer(self, "B03")
        pt = part_tag(3, "Methods")
        cap = caption("LCA: the form an employer files with the Labor Department before hiring on an H-1B", 22)
        doc = page(1.4, 1.8, 4).move_to([-4.9, 1.0, 0])
        doc_lab = VGroup(T("FY2026 Q3 file", 24, weight="BOLD"), T("252 MB workbook", 22)).arrange(DOWN, buff=0.06)
        doc_lab.next_to(doc, DOWN, buff=0.2)
        p.play(FadeIn(pt), FadeIn(cap), FadeIn(doc), FadeIn(doc_lab), run_time=0.9)

        p.until("fingerprint", 0.3)
        sha = tag("SHA-256 f8ca8448… matches", 22).move_to([-4.9, -1.75, 0])
        keep_in(sha)
        p.play(FadeIn(sha), run_time=0.6)

        p.until("blank rows", 0.45)
        r1 = card(["1,032,735 sheet rows"], 4.0, 0.9, 28).move_to([-0.3, 1.6, 0])
        r2 = card(["437,496 filings kept", "595,239 blank rows dropped"], 4.0, 1.3, 28, 22).move_to([-0.3, -0.55, 0])
        a1 = Arrow(r1.get_bottom(), r2.get_top(), buff=0.1, color=INK, stroke_width=5)
        p.play(FadeIn(r1), GrowArrow(a1), FadeIn(r2), run_time=1.0)

        p.until("eighteen", 0.66)
        c1 = card(["98 columns"], 3.4, 0.9, 28).move_to([4.3, 1.6, 0])
        c2 = card(["18 public columns", "kept"], 3.4, 1.3, 28, 22).move_to([4.3, -0.55, 0])
        a2 = Arrow(c1.get_bottom(), c2.get_top(), buff=0.1, color=INK, stroke_width=5)
        p.play(FadeIn(c1), GrowArrow(a2), FadeIn(c2), run_time=0.9)

        p.until("Contact names", 0.85)
        x = VGroup(Line(UL * 0.16, DR * 0.16, color=ACC, stroke_width=7), Line(DL * 0.16, UR * 0.16, color=ACC, stroke_width=7))
        nl = T("contact names and emails: never loaded", 24)
        never = VGroup(x, nl).arrange(RIGHT, buff=0.25).move_to([2.1, -1.9, 0])
        keep_in(never)
        p.play(FadeIn(never), run_time=0.6)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B04_Loop(Scene):
    def construct(self):
        p = Pacer(self, "B04")
        pt = part_tag(3, "Methods")
        cap = caption("Agent: software that repeats look, decide, act, record, and stops by itself", 22)
        center = np.array([0, 0.45, 0])
        names = ["observe", "decide", "act", "record", "stop"]
        angles = [90, 18, -54, -126, 162]
        boxes = []
        for n, ang in zip(names, angles):
            pos = center + np.array([3.6 * np.cos(np.radians(ang)), 1.75 * np.sin(np.radians(ang)), 0])
            boxes.append(box(2.4, 0.85, n, 30).move_to(pos))
        mid = T("agent loop", 34, weight="BOLD").move_to(center)
        p.play(FadeIn(pt), FadeIn(cap), FadeIn(mid), run_time=0.8)
        def edge(b, toward):
            c = np.array(b.get_center(), dtype=float)
            d = np.array(toward, dtype=float) - c
            hw, hh = b.width / 2, b.height / 2
            t = min(hw / abs(d[0]) if d[0] else 1e9, hh / abs(d[1]) if d[1] else 1e9)
            return c + d * t
        arrows = []
        for i in range(4):
            a_, b_ = boxes[i], boxes[i + 1]
            arrows.append(Arrow(edge(a_, b_.get_center()), edge(b_, a_.get_center()), buff=0.12, color=INK,
                                stroke_width=4, max_tip_length_to_length_ratio=0.2))
        cues = [("Observe", 0.15), ("Decide", 0.25), ("Act:", 0.42), ("Record", 0.5)]
        for i, (phrase, fb) in enumerate(cues):
            p.until(phrase, fb)
            anims = [FadeIn(boxes[i], scale=0.9)]
            if i > 0:
                anims.append(GrowArrow(arrows[i - 1]))
            p.play(*anims, run_time=0.5)

        p.until("And stop", 0.58)
        dot = Dot(radius=0.11, color=ACC).next_to(boxes[4], UP, buff=0.12)
        p.play(GrowArrow(arrows[3]), FadeIn(boxes[4], scale=0.9), FadeIn(dot, scale=0.4), run_time=0.6)
        chips = VGroup(tag("2 tries per question", 24), tag("10 s per query", 24)).arrange(RIGHT, buff=0.4)
        chips.move_to([-1.8, -2.25, 0])
        p.play(FadeIn(chips), run_time=0.5)

        p.until("Never", 0.85)
        never = tag("not when the model says it's done", 24).next_to(chips, RIGHT, buff=0.4)
        row = VGroup(chips, never)
        fit(row, 11.6)
        row.move_to([0, -2.25, 0])
        p.play(FadeIn(never), run_time=0.5)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B05_Policy(Scene):
    def construct(self):
        p = Pacer(self, "B05")
        pt = part_tag(3, "Methods")
        cap = caption("SQL query: instructions that pick and count rows in a database")
        p.play(FadeIn(pt), FadeIn(cap), run_time=0.7)

        p.until("permission policy", 0.12)
        pol = card(["Permission policy", "a short list, written in code, of what the tool is allowed to do",
                    "anything else is blocked before it runs"], 10.4, 1.9, 32, 26).move_to([0, -0.45, 0])
        p.play(FadeIn(pol, shift=UP * 0.2), run_time=0.6)

        p.until("only reading", 0.3)
        rule = box(6.4, 0.95, "SQLite rule: read one table (lca), nothing else", 26).move_to([2.6, 1.85, 0])
        keep_in(rule)
        p.play(FadeIn(rule), run_time=0.6)

        p.until("read-only", 0.38)
        db = box(3.6, 0.95, "database: read-only", 28).move_to([-3.4, 1.85, 0])
        p.play(FadeIn(db), run_time=0.6)

        p.until("real output", 0.6)
        lines = ["$ python3 -m sponsorsql failures --db data/fy2026q3.sqlite",
                 "  F1  as predicted  stop=stopped_policy_denials",
                 "      caught by policy.check_text (text layer)",
                 "  F2  as predicted  stop=stopped_policy_denials",
                 "      caught by policy.check_text (text layer)",
                 "  F3  as predicted  stop=stopped_policy_denials",
                 "      caught by policy.authorizer (SQLite layer)",
                 "  rows before 437,496  ·  rows after 437,496"]
        term = terminal(lines, 11.6, 22).move_to([0, -0.55, 0])
        note = T("real output, 2026-11-21 · re-typeset · F1 = DELETE, F2 = hidden 2nd statement, F3 = other table", 18, SOFT)
        fit(note, 11.4)
        note.next_to(term, DOWN, buff=0.12)
        p.play(FadeOut(pol), FadeIn(term[0]), FadeIn(note), run_time=0.4)
        p.play(LaggedStart(*[FadeIn(t) for t in term[1][:-1]], lag_ratio=0.3), run_time=2.0)

        p.until("every row", 0.88)
        p.play(FadeIn(term[1][-1]), run_time=0.5)
        ul = Line(term[1][-1].get_corner(DL) + DOWN * 0.06, term[1][-1].get_corner(DR) + DOWN * 0.06,
                  color=ACC, stroke_width=5)
        p.play(Create(ul), run_time=0.4)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B06_RealRun(Scene):
    def construct(self):
        p = Pacer(self, "B06")
        pt = part_tag(3, "Methods")
        lab = label_tr("real output, 2026-11-23 run · recorded Claude reply · re-typeset")
        cap = caption("Human gate: nothing is saved until a person approves this exact screen")
        lines = ["Question: How many certified H-1B Data Analyst cases have a",
                 "          recorded worksite in Boston, MA?",
                 "Answer:   40",
                 "SQL:      SELECT COUNT(*) AS cases FROM lca",
                 "          WHERE CASE_STATUS = 'Certified' AND VISA_CLASS = 'H-1B' AND ...",
                 "Matching rows: 40, for example",
                 "  8272   Gupta Media Holdings LLC       Marketing Data Analyst II",
                 "  24187  CarGurus, Inc.                 Senior Product Data Analyst",
                 "  43289  Brigham and Women's Hospital   Data Analyst I",
                 "View SHA-256: 713713b8dbd41703 ... 9632c47e3"]
        term = terminal(lines, 11.8, 21).move_to([0, 0.55, 0])
        keep_in(term)
        p.play(FadeIn(pt), FadeIn(lab), FadeIn(cap), FadeIn(term[0]), run_time=0.8)
        t = term[1]
        p.until("The question", 0.12)
        p.play(FadeIn(t[0]), FadeIn(t[1]), run_time=0.5)
        p.until("The answer", 0.3)
        p.play(FadeIn(t[2]), FadeIn(t[3]), FadeIn(t[4]), run_time=0.6)
        p.until("matching rows", 0.45)
        p.play(LaggedStart(*[FadeIn(x) for x in t[5:9]], lag_ratio=0.25), run_time=1.0)

        p.until("human gate", 0.62)
        gate = terminal(["Approve, refuse, or defer this answer? [a/r/d]:"], 8.6, 24).next_to(term, DOWN, buff=0.22)
        gl = T("gate prompt (interactive mode)", 20, SOFT).next_to(gate, RIGHT, buff=0.25)
        grp = VGroup(gate, gl)
        keep_in(grp)
        p.play(FadeIn(gate), FadeIn(gl), run_time=0.6)

        p.until("fingerprint", 0.85)
        p.play(FadeIn(t[9]), run_time=0.4)
        ul = Line(t[9].get_corner(DL) + DOWN * 0.06, t[9].get_corner(DR) + DOWN * 0.06, color=ACC, stroke_width=5)
        p.play(Create(ul), run_time=0.4)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B07_Resources(Scene):
    def construct(self):
        p = Pacer(self, "B07")
        pt = part_tag(3, "Methods")
        cap = caption("Claude Code: Anthropic's AI coding assistant, used through my account")
        p.play(FadeIn(pt), FadeIn(cap), run_time=0.7)

        p.until("Python", 0.1)
        a = card(["Python + SQLite", "standard library only,", "nothing installed"], 3.8, 2.0).move_to([-4.3, 1.0, 0])
        b = card(["Claude Code", "my account; no API key,", "no paid credits"], 3.8, 2.0).move_to([0, 1.0, 0])
        c = card(["This Mac", "data loads in about", "70 seconds"], 3.8, 2.0).move_to([4.3, 1.0, 0])
        p.play(LaggedStart(FadeIn(a), FadeIn(b), FadeIn(c), lag_ratio=0.3), run_time=1.2)

        p.until("wasn't logged in", 0.55)
        note = card(["Claude command line: \"Not logged in\"",
                     "so the tested queries came from separate Claude sessions, saved word for word and replayed"],
                    11.2, 1.5, 28, 22).move_to([0, -1.45, 0])
        dot = Dot(radius=0.11, color=ACC).next_to(note[1][0], LEFT, buff=0.2)
        p.play(FadeIn(note, shift=UP * 0.2), FadeIn(dot, scale=0.4), run_time=0.7)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B08_EvalSetup(Scene):
    def construct(self):
        p = Pacer(self, "B08")
        pt = part_tag(4, "Evaluation")
        cap = caption("Answer key: the right answers, counted by code that never sees the model's query", 21)
        p.play(FadeIn(pt), FadeIn(cap), run_time=0.7)

        p.until("development set", 0.1)
        d = card(["10 development questions", "used while building,", "to find and fix mistakes"], 5.2, 1.75, 28, 22).move_to([-3.0, 0.9, 0])
        p.play(FadeIn(d, shift=DOWN * 0.2), run_time=0.7)

        p.until("held-out set", 0.25)
        h = card(["5 held-out questions", "kept aside until the end,", "to test the fixes on new ones"], 5.2, 1.75, 28, 22).move_to([3.0, 0.9, 0])
        p.play(FadeIn(h, shift=DOWN * 0.2), run_time=0.7)

        p.until("answer key", 0.6)
        k1 = card(["answer key", "counted by separate code"], 5.2, 1.0, 26, 20).move_to([-3.0, -0.75, 0])
        k2 = card(["answer key", "counted by separate code"], 5.2, 1.0, 26, 20).move_to([3.0, -0.75, 0])
        p.play(FadeIn(k1), FadeIn(k2), run_time=0.7)

        p.until("locked", 0.72)
        frz = tag("locked before any test", 24).move_to([0, 2.3, 0])
        p.play(FadeIn(frz), run_time=0.5)

        p.until("To pass", 0.85)
        bar = VGroup(tag("at least 8/10", 28), tag("at least 4/5", 28), tag("0 unsafe queries", 28)).arrange(RIGHT, buff=0.5)
        bar.move_to([0, -2.2, 0])
        dot = Dot(radius=0.11, color=ACC).next_to(bar, LEFT, buff=0.25)
        p.play(FadeIn(bar), FadeIn(dot, scale=0.4), run_time=0.7)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B09_Results(Scene):
    def construct(self):
        p = Pacer(self, "B09")
        pt = part_tag(4, "Evaluation")
        cap = caption("Development: 10 questions used while building · Held-out: 5 new questions, run once at the end")
        base_y = -1.45
        base = Line([-6.0, base_y, 0], [6.0, base_y, 0], color=INK, stroke_width=4)
        p.play(FadeIn(pt), FadeIn(cap), Create(base), run_time=0.8)
        specs = [("four out of ten", 0.12, -4.0, 0.4, "4/10", "development · 1st try", "'Metadata Analyst' counted"),
                 ("nine out of ten", 0.55, 0.0, 0.9, "9/10", "development · title rule", "miss: invisible tabs"),
                 ("the held-out set", 0.86, 4.0, 1.0, "5/5", "held-out · run once", "")]
        full = 3.0
        for phrase, fb, x, frac, score, name, note in specs:
            p.until(phrase, fb)
            bar = Rectangle(width=2.2, height=full * frac, stroke_width=0, fill_color=INK, fill_opacity=1)
            bar.move_to([x, base_y + full * frac / 2, 0])
            s = T(score, 40, weight="BOLD").next_to(bar, UP, buff=0.15)
            n = fit(T(name, 22), 3.8).move_to([x, base_y - 0.35, 0])
            parts = [GrowFromEdge(bar, DOWN), FadeIn(s), FadeIn(n)]
            if note:
                nt = fit(T(note, 20, SOFT), 3.8).move_to([x, base_y - 0.8, 0])
                parts.append(FadeIn(nt))
            if score == "5/5":
                cm = check_mark(s.get_right() + np.array([0.5, 0.05, 0]), 0.25)
                parts.append(Create(cm))
            p.play(*parts, run_time=0.8)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B10_BreakIt(Scene):
    def construct(self):
        p = Pacer(self, "B10")
        pt = part_tag(4, "Evaluation")
        lab = label_tr("scripted test inputs, not model output · 2026-11-21")
        cap = caption("Deliberate failure: a test built to make the system fail on purpose")
        p.play(FadeIn(pt), FadeIn(lab), FadeIn(cap), run_time=0.7)
        names = ["delete", "2nd statement", "other table", "runaway query", "contact details",
                 "visa prediction", "broken replies", "clarification", "stale approval", "answer ≠ rows"]
        tiles = VGroup()
        for i, n in enumerate(names):
            col, row = i % 5, i // 5
            t = card([f"F{i + 1}  ✓", n], 2.25, 1.05, 26, 20).move_to([-4.6 + 2.3 * col, 1.55 - 1.2 * row, 0])
            tiles.add(t)
        p.until("Ten deliberate", 0.2)
        p.play(LaggedStart(*[FadeIn(t, scale=0.9) for t in tiles], lag_ratio=0.15), run_time=2.2)

        p.until("title bug", 0.75)
        wide = card(["C1  title bug triggered on purpose  →  caught by the answer key"], 10.4, 0.95, 26).move_to([-0.45, -1.3, 0])
        cm = check_mark(wide.get_right() + np.array([0.5, 0, 0]), 0.24)
        p.play(FadeIn(wide, shift=UP * 0.2), run_time=0.6)
        p.play(Create(cm), run_time=0.4)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B11_Limits(Scene):
    def construct(self):
        p = Pacer(self, "B11")
        pt = part_tag(4, "Evaluation")
        head = fit(T("Independent review: 18 findings · code fixed where it could be", 30, weight="BOLD"), 11.4)
        head.move_to([0, 2.15, 0])
        cap = caption("Full review saved word for word in the project: evidence/independent-review-2026-11-21.md", 20)
        p.play(FadeIn(pt), FadeIn(head), FadeIn(cap), run_time=0.8)
        rows = ["Claude's final instructions were tested before I reviewed them (reviewed since)",
                "The answer keys share their rules with the system",
                "The model's replies were replayed, not live"]
        cues = [("The final version", 0.3), ("The answer keys", 0.42), ("replayed", 0.52)]
        objs = []
        for i, (text, (phrase, fb)) in enumerate(zip(rows, cues)):
            p.until(phrase, fb)
            r = card([text], 10.6, 0.75, 26).move_to([0.3, 1.2 - 0.9 * i, 0])
            bang = VGroup(Circle(radius=0.22, color=INK, stroke_width=4), T("!", 26, weight="BOLD"))
            bang.next_to(r, LEFT, buff=0.2)
            grp = VGroup(bang, r)
            keep_in(grp)
            p.play(FadeIn(grp, shift=RIGHT * 0.2), run_time=0.5)
            objs.append(grp)

        p.until("narrow", 0.7)
        claim = card(["Honest claim: narrow · one public file · answers you can check"], 11.2, 0.85, 28).move_to([0, -1.55, 0])
        p.play(FadeIn(claim, shift=UP * 0.2), run_time=0.6)

        p.until("sign-off", 0.9)
        dec = tag("Ship, narrow or defer: my sign-off, still open", 24).move_to([0, -2.42, 0])
        dot = Dot(radius=0.11, color=ACC).next_to(dec, LEFT, buff=0.25)
        p.play(FadeIn(dec), FadeIn(dot, scale=0.4), run_time=0.5)
        p.finish()


# ═════════════════════════════════════════════════════════════════════════════
class B12_Outro(Scene):
    def construct(self):
        p = Pacer(self, "B12")
        name = T("SponsorSQL", 132, weight="BOLD")
        dot = Dot(radius=0.17, color=ACC).next_to(name, RIGHT, buff=0.1).align_to(name, DOWN).shift(UP * 0.07)
        title = VGroup(name, dot).move_to([0, 2.0, 0])
        sub = fit(T("Plain-English questions, answers you can check", 48), 11.5).next_to(title, DOWN, buff=0.45)
        p.play(FadeIn(name, shift=UP * 0.2), run_time=0.7)
        p.play(FadeIn(dot, scale=0.3), FadeIn(sub), run_time=0.5)
        rule = Line(LEFT * 5.6, RIGHT * 5.6, color=INK, stroke_width=3).next_to(sub, DOWN, buff=0.55)
        cred = fit(T("Atharva Hambir · INFO 7375 · Final project", 42), 11.5).next_to(rule, DOWN, buff=0.85)
        p.until("answers you can check", 0.25)
        p.play(Create(rule), FadeIn(cred), run_time=0.7)
        p.finish()
