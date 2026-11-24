"""scenes.py — Readback PROJECT film (four-part brief): Manim scenes B01–B20.

A new film, not a re-cut of the pitch film. One visual system, written down in DESIGN.md:
  colour roles  REAL evidence = kraft · CONSTRUCTED = white paper with a dark band · PLANNED = dashed grey, values "—"
                THE CLAUSE = terracotta, used only on the hero chip's outline, its halo and the trace line (never type)
  type          72 / 52 / 40 / 36 / 32 (32 is the floor), EB Garamond; PT Mono for meeting IDs
  grid          12 columns across ±6.2 · content y −2.7…2.6 · source label at y −3.05 · corner tag top right (y 3.12, inside the ±3.4 safe area)
  structure     a chapter card (large numeral + title) opens each part; there is no section bar on any frame
  motion        enter = fade + a 0.15 rise · exits finish before entrances · every scene opens on the previous
                scene's last frame
Positioning (revision of 23 Nov 2026): Readback is for any AI feature's acceptance criteria. The executive summary and
the introduction show only a generic "criterion" chip and constructed illustrations; the AMI meeting-recap feature
appears only from Methods on, as the test case, and there the hero chip becomes C4 from the CONSTRUCTED rubric-v0.md,
in plain English. Corner tags name what a frame shows: illustration, planned, vision, test case.
Every number on screen is read from a repo file (asserted below) or from EVAL-PLAN.md, where it is a plan setting.
Narration is the clock: cues come from mp3/words.json.
"""
from manim import *
import numpy as np
import csv as _csv
import json as _json
import os as _os

# ═════════════════════════════ colour roles (the only colours in the film) ═════════════════════════════
STAGE = "#F2F0E9"                        # the ground at every cut, the outro included (patched ClaudeTitleOutro)
INK = "#3D3929"                          # all type; neutral actors (the PM, ticks, needles)
KRAFT, KRAFT_LT = "#C7AE86", "#DCC9AA"   # REAL: AMI data, real recaps, real models, tools as their docs describe them
KRAFT_DK = "#A8916B"                     # REAL, deeper: a model drawn on a kraft card
PAPER, PAPER_LN, BAND = "#FFFFFF", "#B4AFA6", "#3A3530"   # CONSTRUCTED: white paper, light rule, dark header band
WILL, WILL_FILL = "#8B8F96", "#D9D4C7"   # PLANNED ("will"): dashed grey outline on light grey; values shown as "—"
CLAUSE = "#D97757"                       # THE CLAUSE: hero chip outline, halo, trace line. Never type, never under type.
GREY = "#8B8F96"                         # connectors; outlines of neutral containers that hold type
TAG_INK = "#6B675C"                      # corner tags: quieter than INK, still 4.9:1 on STAGE (WCAG AA)
config.background_color = STAGE

SERIF, MONO = "EB Garamond", "PT Mono"
H1, H2, H3, BODY, SMALL = 72, 52, 40, 36, 32      # the type scale; 32 is the floor (Gate T: 41 px at 2160)
LX = -6.05                                        # left text margin (grid: 12 columns across ±6.2)
PARTS4 = ["Executive summary", "Introduction", "Methods", "Evaluation"]
RAIL_X = [-6.05, -2.0, 0.85, 3.6]
TAG_ILLU = "CONSTRUCTED illustration · no judge has run yet"
TAG_DOCS = "per their public docs · checked 14 Oct 2026"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_CS = _os.path.join(_HERE, "..", "..", "case-study")

# ═════════════════════════════ pacing: narration is the clock ═════════════════════════════
try:
    _SHEET = _json.load(open(_os.path.join(_HERE, "beat_sheet.json")))
    _TARGET = {b["beat_id"]: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0) for b in _SHEET["beats"]}
except Exception:
    _TARGET = {}
try:
    _WORDS = _json.load(open(_os.path.join(_HERE, "mp3", "words.json")))
    _FPS = float(_WORDS.get("fps", 24))
except Exception:
    _WORDS, _FPS = {"beats": {}}, 24.0


def _bid(self):
    return type(self).__name__.split("_")[0]


def _elapsed(self):
    rt = getattr(getattr(self, "renderer", None), "time", None)
    return float(rt) if isinstance(rt, (int, float)) else 0.0


def _mid(self):
    return _TARGET.get(_bid(self), 0) / 2


def word_t(self, word, nth=1):
    """Start time (s) of the nth spoken occurrence of `word` in this beat (forced-alignment clock)."""
    seen = 0
    for w in _WORDS["beats"].get(_bid(self), []):
        if w["text"].strip(".,:;?!'\"").lower() == word.lower():
            seen += 1
            if seen == nth:
                return w["startFrame"] / _FPS
    return None


def on(self, word, nth=1, lead=0.1):
    """Wait until `word` is spoken (no wait in Gate A's sandbox)."""
    t = word_t(self, word, nth)
    if t is None:
        return
    gap = t - lead - _elapsed(self)
    if gap > 0.04:
        self.wait(gap)


def P(self, *anims, rt=0.6):
    """play() that never animates across the clip midpoint (Gates T and V sample it)."""
    mid, t = _mid(self), _elapsed(self)
    if mid and t < mid + 0.25 and t + rt > mid - 0.25:
        room = mid - 0.25 - t
        if room >= 0.3:
            rt = room
        else:
            self.wait(max(0.05, mid + 0.27 - t))
    self.play(*anims, run_time=rt)


def finish(self):
    target = _TARGET.get(_bid(self), 0)
    self.wait(max(0.3, target - _elapsed(self)) if target else 2.0)


# ═════════════════════════════ real evidence, read from the repo and asserted ═════════════════════════════
def _load_sel():
    """The 10 selected AMI meetings: (meeting, DECISIONS count, duration in s), from selection.csv."""
    rows = [("IS1004d", 12, 1955.0), ("ES2006d", 10, 1991.0), ("IS1009d", 9, 1929.0), ("ES2008c", 8, 2098.0),
            ("ES2010b", 8, 1764.0), ("ES2011b", 8, 1581.0), ("ES2013d", 8, 1898.0), ("IS1003c", 8, 1870.0),
            ("IS1005c", 8, 2062.0), ("ES2007a", 7, 1221.0)]
    path = _os.path.join(_CS, "data", "sample", "selection.csv")
    if _os.path.exists(path):
        got = sorted(((r["meeting"], int(r["decisions"]), float(r["duration_s"])) for r in _csv.DictReader(open(path))
                      if r["selected"] == "True"), key=lambda r: (-r[1], r[0]))
        assert got == rows, "selection.csv differs from the meetings drawn on screen"
        for m, *_ in rows:
            assert _os.path.exists(_os.path.join(_CS, "outputs", "feature-run", f"{m}.json")), f"no real recap for {m}"
    assert sum(r[1] for r in rows) == 86
    return rows


SEL = _load_sel()
TRANSCRIPT = "[00:17:52] C (UI): … it can just have a lock function,"
RECAP = ("Include a lock function so buttons can't be", "pressed by accident … [00:17:52]")
TR_HERO = ("[00:17:52] C (UI):", "… it can just have a lock function,")                        # B10, hero size
RC_HERO = ("Include a lock function", "so buttons can't be pressed", "by accident … [00:17:52]")
assert " ".join(TR_HERO) == TRANSCRIPT and " ".join(RC_HERO) == " ".join(RECAP)
DEC_ITEMS = (("The remote will have", "a lock function."), ("The remote will be", "sold internationally."))
CLAUSES = ("Every decision … appears in the recap", "Claims trace to the transcript.", "Action items have owners.",
           "Unresolved stays unresolved.", "Useful to someone who missed it.")
CLAUSE_TEXT = ("C4 · Don't report open", "questions as decisions")   # rubric-v0.md C4 in plain English (CLAIMS.md)
CHIP_W = 5.1          # two lines at the 32 floor: each measures 3.9, and the pill's flat run must cover them
try:  # every excerpt on screen is a verbatim piece of its source file
    if _os.path.exists(_CS):
        _rec = _json.load(open(_os.path.join(_CS, "outputs", "feature-run", "ES2007a.json")))
        assert "Include a lock function so buttons can't be pressed by accident" in _rec["recap"] and "[00:17:52]" in _rec["recap"]
        assert _rec["models_reported"] == ["claude-opus-5-5"] and _rec["run_started_utc"].startswith("2026-10-14")
        _tr = open(_os.path.join(_CS, "data", "sample", "ES2007a", "transcript.txt")).read()
        assert "[00:17:52] C (UI):" in _tr and "it can just have a lock function," in _tr
        _sm = open(_os.path.join(_CS, "data", "sample", "ES2007a", "summary.txt")).read()
        assert all(" ".join(p) in _sm for p in DEC_ITEMS)
        _rb = open(_os.path.join(_CS, "constructed", "rubric-v0.md")).read()
        assert "Every decision listed" in _rb and "appears in the recap" in _rb
        assert all(c in _rb for c in CLAUSES[1:])
        _r2 = _json.load(open(_os.path.join(_CS, "outputs", "feature-run", "ES2010b.json")))
        assert "## Decisions" in _r2["recap"] and "- The remote should be easy to find if lost [00:20:52]" in _r2["recap"].split("## Action")[0]
        assert _r2["models_reported"] == ["claude-opus-5-5"] and _r2["run_started_utc"].startswith("2026-10-14")
        _t2 = open(_os.path.join(_CS, "data", "sample", "ES2010b", "transcript.txt")).read()
        assert all(x in _t2 for x in ("[00:20:44] B (ID): Do we want this thing to be able to be found easily?",
                                      "[00:20:49] A (PM): I think so.", "[00:20:52] D (ME): Sure, yeah."))
        _s2 = open(_os.path.join(_CS, "data", "sample", "ES2010b", "summary.txt")).read()
        assert "will consider including speech recognition and a locator function" in _s2
except FileNotFoundError:
    pass


# ═════════════════════════════ kit: type, containers, actors ═════════════════════════════
def T(s, size=BODY, bold=False, font=SERIF):
    return Text(s, font=font, font_size=size, color=INK, weight="BOLD" if bold else "NORMAL")


def Tm(s, size=SMALL):
    return Text(s, font=MONO, font_size=size, color=INK)


def lx(m, x):
    return m.align_to([x, 0, 0], LEFT)


def rx(m, x):
    return m.align_to([x, 0, 0], RIGHT)


def rbox(x, y, w, h, fill=PAPER, stroke=GREY, sw=4, r=0.12, op=1.0):
    return RoundedRectangle(width=w, height=h, corner_radius=r, fill_color=fill, fill_opacity=op,
                            stroke_color=stroke, stroke_width=sw).move_to([x, y, 0])


def real_card(x, y, w, h):
    """REAL evidence: kraft, grey outline (ink outlines around type fail Gate T). The deeper kraft keeps Gate V's
    ink-vs-ground separation above 0.30 when the cards are large; ink on it is 5.4:1."""
    return rbox(x, y, w, h, KRAFT, GREY)


def made_card(x, y, w, h):
    """CONSTRUCTED: white paper, light rule, a dark header band that never carries type."""
    return VGroup(rbox(x, y, w, h, PAPER, PAPER_LN),
                  Rectangle(width=w - 0.12, height=0.2, fill_color=BAND, fill_opacity=1, stroke_width=0)
                  .move_to([x, y + h / 2 - 0.16, 0]))


def will_box(x, y, w, h, fill=True):
    """PLANNED: dashed grey outline on light grey."""
    out = DashedVMobject(rbox(x, y, w, h, PAPER, WILL, sw=5, op=0), num_dashes=max(10, int(5 * (w + h))))
    if not fill:
        return out
    return VGroup(rbox(x, y, w, h, WILL_FILL, WILL, sw=0), out)


def blank(x, y, w=1.1, h=0.6):
    """A planned value: '—' in a will box."""
    return VGroup(will_box(x, y, w, h), T("—", BODY).move_to([x, y, 0]))


def pill(x, y, s, fill=PAPER):
    t = T(s, SMALL)
    w = t.width + 0.5
    return VGroup(RoundedRectangle(width=w, height=0.7, corner_radius=0.35, fill_color=fill, fill_opacity=1,
                                   stroke_color=GREY, stroke_width=4).move_to([x, y, 0]), t.move_to([x, y, 0]))


def will_pill(x, y, s):
    t = T(s, SMALL)
    w = t.width + 0.6
    base = RoundedRectangle(width=w, height=0.7, corner_radius=0.35, fill_color=WILL_FILL, fill_opacity=1,
                            stroke_width=0).move_to([x, y, 0])
    out = DashedVMobject(RoundedRectangle(width=w, height=0.7, corner_radius=0.35, stroke_color=WILL,
                                          stroke_width=5).move_to([x, y, 0]), num_dashes=max(12, int(4 * w)))
    return VGroup(base, out, t.move_to([x, y, 0]))


def chip(x, y, form="full"):
    """THE HERO: one criterion as a physical chip.
    crit / crit_c = the generic criterion (executive summary, introduction: no test case on it);
    full = C4 in plain English, two lines; compact = 'C4'; mini = 'C4' in a grid header (test case only)."""
    if form == "crit":
        t, w, h = T("criterion", BODY), 2.3, 0.82
    elif form == "crit_c":
        t, w, h = T("criterion", SMALL), 2.0, 0.7
    elif form == "full":
        t, w, h = VGroup(T(CLAUSE_TEXT[0], SMALL), T(CLAUSE_TEXT[1], SMALL)).arrange(DOWN, buff=0.05), CHIP_W, 1.1
    elif form == "compact":
        t, w, h = T("C4", H3, bold=True), 1.6, 0.82
    else:
        t, w, h = T("C4", SMALL, bold=True), 1.15, 0.62
    body = RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color=PAPER, fill_opacity=1,
                            stroke_width=0).move_to([x, y, 0])
    return VGroup(body, t.move_to([x, y, 0]), pill_outline(x, y, w, h)).set_z_index(3)


def pill_outline(x, y, w, h, color=CLAUSE, sw=8, gap=0.035):
    """The chip's terracotta outline as four strokes (two flat edges, two end caps) with hairline gaps where they
    meet. Gate T reads a closed terracotta ring around type as terracotta *text*; open strokes read as structure.
    The type inside stays ink."""
    r = h / 2
    d = gap / r
    return VGroup(Line([x - w / 2 + r + gap, y + r, 0], [x + w / 2 - r - gap, y + r, 0], color=color, stroke_width=sw),
                  Line([x - w / 2 + r + gap, y - r, 0], [x + w / 2 - r - gap, y - r, 0], color=color, stroke_width=sw),
                  Arc(radius=r, start_angle=PI / 2 + d, angle=PI - 2 * d, arc_center=[x - w / 2 + r, y, 0], color=color,
                      stroke_width=sw),
                  Arc(radius=r, start_angle=-PI / 2 + d, angle=PI - 2 * d, arc_center=[x + w / 2 - r, y, 0], color=color,
                      stroke_width=sw))


def open_rect(x, y, w, h, color=CLAUSE, sw=7, gap=0.06):
    """A rectangle outline as four straight strokes with open corners (same reason as pill_outline)."""
    return VGroup(Line([x - w / 2 + gap, y + h / 2, 0], [x + w / 2 - gap, y + h / 2, 0], color=color, stroke_width=sw),
                  Line([x - w / 2 + gap, y - h / 2, 0], [x + w / 2 - gap, y - h / 2, 0], color=color, stroke_width=sw),
                  Line([x - w / 2, y - h / 2 + gap, 0], [x - w / 2, y + h / 2 - gap, 0], color=color, stroke_width=sw),
                  Line([x + w / 2, y - h / 2 + gap, 0], [x + w / 2, y + h / 2 - gap, 0], color=color, stroke_width=sw))


def halo(c, buff=0.17):
    """The lit state: a translucent terracotta ring behind the chip."""
    w, h = c.width + 2 * buff, c.height + 2 * buff
    return RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color=CLAUSE, fill_opacity=0.32,
                            stroke_width=0).move_to(c.get_center()).set_z_index(2)


def judge(x, y, r=0.4, plan=False, fill=KRAFT):
    """A judge model. Real models are kraft discs with a dark lens; planned judge runs are dashed grey."""
    if plan:
        return VGroup(Circle(radius=r, stroke_width=0, fill_color=WILL_FILL, fill_opacity=1).move_to([x, y, 0]),
                      DashedVMobject(Circle(radius=r, stroke_color=WILL, stroke_width=6).move_to([x, y, 0]), num_dashes=14),
                      Circle(radius=r * 0.4, stroke_width=0, fill_color=WILL, fill_opacity=1).move_to([x, y, 0]))
    return VGroup(Circle(radius=r, stroke_width=0, fill_color=fill, fill_opacity=1).move_to([x, y, 0]),
                  Circle(radius=r * 0.4, stroke_width=0, fill_color=BAND, fill_opacity=1).move_to([x, y, 0]))


def pm(x, y, s=1.0):
    """The product manager: a neutral ink figure."""
    return VGroup(Circle(radius=0.2 * s, stroke_width=0, fill_color=INK, fill_opacity=1).move_to([x, y + 0.33 * s, 0]),
                  RoundedRectangle(width=0.78 * s, height=0.46 * s, corner_radius=0.2 * s, stroke_width=0,
                                   fill_color=INK, fill_opacity=1).move_to([x, y - 0.17 * s, 0]))


def tick(x, y, s=0.2, color=INK, w=8):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))


def cross(x, y, s=0.17, color=INK, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def stamp(x, y, ok=True, r=0.27):
    if ok:
        return VGroup(Circle(radius=r, stroke_width=0, fill_color=INK, fill_opacity=1).move_to([x, y, 0]),
                      tick(x - 0.02, y + 0.02, s=0.12, color=PAPER, w=6))
    return VGroup(Circle(radius=r, stroke_color=GREY, stroke_width=4, fill_color=PAPER, fill_opacity=1).move_to([x, y, 0]),
                  cross(x, y, s=0.1, w=6))


def arrow(a, b, color=GREY, sw=6):
    return Arrow([a[0], a[1], 0], [b[0], b[1], 0], color=color, stroke_width=sw, buff=0,
                 max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=12)


def poly(pts, color=CLAUSE, sw=7):
    return VMobject(stroke_color=color, stroke_width=sw).set_points_as_corners([[p[0], p[1], 0] for p in pts])


def bubble(x, y, s, tail=None, size=BODY):
    """A question bubble (grey outline) with an optional tail polygon given as three points."""
    t = T(s, size)
    w = t.width + 0.6
    g = VGroup()
    if tail:
        g.add(Polygon(*[[p[0], p[1], 0] for p in tail], fill_color=PAPER, fill_opacity=1, stroke_color=GREY, stroke_width=5))
    g.add(RoundedRectangle(width=w, height=0.85, corner_radius=0.3, fill_color=PAPER, fill_opacity=1,
                           stroke_color=GREY, stroke_width=5).move_to([x, y, 0]), t.move_to([x, y, 0]))
    return g


def bubble_left(x, y, s, w, size=BODY, tip=0.2):
    """A question bubble of fixed width w (Gate A's stub over-measures text) whose tail points left."""
    xl = x - w / 2
    return VGroup(Polygon([xl + 0.02, y - 0.12, 0], [xl + 0.02, y + 0.12, 0], [xl - tip, y, 0], fill_color=PAPER, fill_opacity=1,
                          stroke_color=GREY, stroke_width=5),
                  RoundedRectangle(width=w, height=0.85, corner_radius=0.3, fill_color=PAPER, fill_opacity=1, stroke_color=GREY,
                                   stroke_width=5).move_to([x, y, 0]), T(s, size).move_to([x, y, 0]))


def doc_icon(x, y, w=0.6, h=0.78, fill=PAPER):
    return VGroup(rbox(x, y, w, h, fill, GREY, sw=3, r=0.06),
                  *[Line([x - w / 2 + 0.12, y + h / 2 - 0.2 - i * 0.17, 0], [x + w / 2 - 0.12, y + h / 2 - 0.2 - i * 0.17, 0],
                         color=PAPER_LN, stroke_width=5) for i in range(3)])


def padlock(x, y, s=1.0):
    return VGroup(Arc(radius=0.28 * s, start_angle=0, angle=PI, arc_center=[x, y + 0.36 * s, 0], color=INK, stroke_width=9 * s + 2),
                  Rectangle(width=0.95 * s, height=0.72 * s, fill_color=BAND, fill_opacity=1, stroke_color=INK,
                            stroke_width=3).move_to([x, y, 0]))


def gauge(x, y):
    return VGroup(Arc(radius=0.55, start_angle=0, angle=PI, arc_center=[x, y - 0.22, 0], color=GREY, stroke_width=8),
                  Line([x, y - 0.22, 0], [x - 0.3, y + 0.2, 0], color=INK, stroke_width=8),
                  Dot([x, y - 0.22, 0], radius=0.1, color=INK))


def rail(active):
    """The section bar is gone (revision of 23 Nov 2026): chapter cards mark the parts instead."""
    return VGroup()


def tag(s):
    return lx(T(s, SMALL).move_to([0, -3.05, 0]), LX)


def src(s):
    return rx(T(s, SMALL).move_to([0, -3.05, 0]), -LX)


def title(s, y=2.2, size=H2):
    return lx(T(s, size, bold=True).move_to([0, y, 0]), LX)


def lines2(a, b, x, y, size=SMALL):
    """Two centred lines of type around y."""
    d = 0.22 if size <= SMALL else 0.25
    return VGroup(T(a, size).move_to([x, y + d, 0]), T(b, size).move_to([x, y - d, 0]))


def fade_all(d, keep=()):
    return [FadeOut(v) for k, v in d.items() if k not in keep]


def pulse(m, s=1.08):
    """Emphasis without a colour change: grow and settle back in place."""
    return ScaleInPlace(m, s, rate_func=there_and_back)


def band(x0, x1, y0, y1):
    """An invisible panel (stage colour, no outline) behind a row or column; it only ever flashes a soft colour."""
    return Rectangle(width=x1 - x0, height=y1 - y0, fill_color=STAGE, fill_opacity=1, stroke_width=0).move_to(
        [(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(-2)


def flash(*ms, color=PAPER_LN):
    """A colour flash on large shapes (cards, bands): the change ffmpeg's freeze detector can see. Type never moves."""
    return [Indicate(m, color=color, scale_factor=1.0) for m in ms]


def ctag(*labels):
    """A small corner tag (top right) naming what kind of thing is on screen: illustration, planned, vision, test case.
    Real evidence keeps its full source and date label at the bottom instead."""
    return rx(Text(" · ".join(labels), font=SERIF, font_size=SMALL, color=TAG_INK).move_to([0, 3.12, 0]), -LX)


def chapter_card(k):
    """A part's chapter card: a large numeral and the part's title."""
    num = Text(str(k), font=SERIF, font_size=200, color=INK, weight="BOLD")
    ttl = T(PARTS4[k - 1], H1, bold=True)
    return VGroup(num, ttl).arrange(RIGHT, buff=0.6).move_to([0, 0.1, 0])


def chapter_in(self, a, k, keep=()):
    """Clear the previous part's last frame, hold chapter card k for about 1.5 s, then clear it.
    The part's narration has already started under the card, so there is no silent gap."""
    card = chapter_card(k)
    P(self, *fade_all(a, keep=keep), rt=0.35)
    P(self, FadeIn(card, shift=UP * 0.1), rt=0.3)
    self.wait(1.0)
    P(self, FadeOut(card, shift=UP * 0.1), rt=0.3)


# ═════════════════════════════ 1 · EXECUTIVE SUMMARY (any AI feature: no meeting, recap, AMI or C4 here) ═════════════════════════════
VALUE = ("Check that AI judges read your acceptance criteria", "the way you meant them.")
PG_X, PG_Y, PG_W, PG_H = -4.25, -0.35, 2.9, 3.3
BAR_Y = [0.65, -0.05, -0.75, -1.45]
J_X, F_X, ROW = 0.35, 4.55, -0.35
# three CONSTRUCTED vignettes from different kinds of AI feature: (feature, one ambiguous criterion, its output)
VIG = (("support-reply bot", "Resolve the issue", ("“See Settings", "for refunds.”")),
       ("document summariser", "Cover the key points", ("“Both sides agree", "on price.”")),
       ("search answer", "Cite a source", ("“Source:", "a forum post.”")))
VIG_X, VIG_Y, VIG_W, VIG_H = [-4.15, 0.0, 4.15], -0.15, 3.95, 4.0


def poster():
    """Frame 0: chapter card 1 and the film's poster in one."""
    head = VGroup(Text("1", font=SERIF, font_size=150, color=INK, weight="BOLD"), T(PARTS4[0], H2, bold=True)).arrange(RIGHT, buff=0.45)
    lx(head.move_to([0, 2.6, 0]), LX)
    c = chip(0, -2.15, "crit")
    return {"num": head, "title": Text("Readback", font=SERIF, font_size=130, color=INK, weight="BOLD").move_to([0, 0.8, 0]),
            "value": VGroup(T(VALUE[0], BODY).move_to([0, -0.42, 0]), T(VALUE[1], BODY).move_to([0, -0.95, 0])),
            "chip": c, "halo": halo(c), "ct": ctag("planned")}      # the name: compile.py's channel title over the first beat


def crit_pill(x, y, s):
    """A criterion as a small chip (vignettes): ink type, terracotta open outline."""
    t, w = T(s, SMALL), 3.75        # fixed width (Gate A's stub over-measures text): the widest criterion is 3.46 at 32
    return VGroup(RoundedRectangle(width=w, height=0.66, corner_radius=0.33, fill_color=PAPER, fill_opacity=1, stroke_width=0)
                  .move_to([x, y, 0]), t.move_to([x, y, 0]), pill_outline(x, y, w, 0.66, sw=6))


def L01():
    """B01's last frame: the PM's criteria became a rubric; a judge read one line its own way, passed it, and it shipped."""
    page = made_card(PG_X, PG_Y, PG_W, PG_H)
    x0, x1 = PG_X - PG_W / 2 + 0.25, PG_X + PG_W / 2 - 0.8
    bars = VGroup(*[Line([x0, y, 0], [x1 - (0.35 if i % 2 else 0), y, 0], color=PAPER_LN, stroke_width=12) for i, y in enumerate(BAR_Y)])
    boxes = VGroup(*[Square(0.3, stroke_color=GREY, stroke_width=4).move_to([PG_X + PG_W / 2 - 0.42, y, 0]) for y in BAR_Y])
    return {"ct": ctag("illustration"), "page": page, "bars": bars, "boxes": boxes,
            "ptitle": lx(T("rubric", BODY, bold=True).move_to([0, 1.75, 0]), -5.0), "who": pm(-5.55, 1.75, 0.8),
            "c3": open_rect((x0 + x1) / 2 - 0.1, BAR_Y[2], x1 - x0 + 0.3, 0.42, sw=6),
            "chip": chip(J_X, -2.35, "crit"),
            "judge": VGroup(judge(J_X, ROW, r=0.5), T("AI judge", SMALL).move_to([J_X, ROW - 0.8, 0])),
            "arrows": VGroup(arrow((PG_X + PG_W / 2 + 0.15, ROW), (J_X - 0.62, ROW)), arrow((F_X - 1.45, ROW), (J_X + 0.62, ROW))),
            "meant": rx(T("what the PM meant", BODY).move_to([0, -2.35, 0]), J_X - 1.35),
            "read": lx(T("how the judge read it", BODY).move_to([0, -2.35, 0]), J_X + 1.35),
            "pass": VGroup(stamp(J_X, 0.75), T("pass", BODY).move_to([J_X + 0.85, 0.75, 0])),
            "ships": T("ships", BODY, bold=True).move_to([F_X, ROW, 0])}


def feature_box():
    return VGroup(rbox(F_X, ROW, 2.7, 1.8, PAPER, GREY), T("AI feature", BODY).move_to([F_X, ROW + 0.45, 0]),
                  doc_icon(F_X, ROW - 0.35, 0.55, 0.62))


class B01_Hook(Scene):
    def construct(self):
        po, d = poster(), L01()
        self.add(*po.values())                                   # frame 0: the poster is chapter card 1
        self.wait(1.4)
        P(self, *[FadeOut(po[k]) for k in ("num", "title", "value", "halo")], Transform(po["ct"], d["ct"]),
          Transform(po["chip"], d["chip"]), rt=0.5)
        fb = feature_box()
        P(self, FadeIn(fb, shift=UP * 0.15), rt=0.4)
        on(self, "criteria")
        P(self, FadeIn(d["page"], shift=UP * 0.15), LaggedStart(*[Create(b) for b in d["bars"]], lag_ratio=0.15), rt=0.7)
        lab = lx(T("acceptance criteria", BODY).move_to([0, 1.75, 0]), -5.0)
        P(self, FadeIn(lab, shift=UP * 0.1), rt=0.35)
        on(self, "PM")
        P(self, FadeIn(d["who"], shift=RIGHT * 0.1), rt=0.35)
        on(self, "wrote")
        P(self, *flash(d["page"][0]), rt=0.5)
        on(self, "rubric")
        P(self, ReplacementTransform(lab, d["ptitle"]), rt=0.4)
        on(self, "checklist")
        P(self, LaggedStart(*[Create(b) for b in d["boxes"]], lag_ratio=0.15), *flash(d["page"][0]), rt=0.6)
        on(self, "judge")
        P(self, FadeIn(d["judge"], shift=UP * 0.15), rt=0.4)
        on(self, "output")
        P(self, *[GrowArrow(a) for a in d["arrows"]], *flash(fb[0]), rt=0.5)
        on(self, "criterion")
        P(self, Create(d["c3"]), pulse(po["chip"], 1.1), rt=0.6)
        on(self, "differently")
        P(self, FadeIn(d["meant"], shift=RIGHT * 0.1), FadeIn(d["read"], shift=LEFT * 0.1), rt=0.5)
        on(self, "meant")
        P(self, *flash(d["page"][0]), rt=0.5)                     # the PM's page: what was meant
        on(self, "passes")
        P(self, FadeIn(d["pass"], scale=0.8), rt=0.4)
        on(self, "and")
        P(self, *flash(fb[0]), rt=0.4)                            # the feature passes and heads out
        on(self, "ships")
        P(self, FadeOut(fb, shift=RIGHT * 1.6), rt=0.35)
        P(self, FadeIn(d["ships"]), rt=0.3)
        finish(self)


def L02():
    """B02's last frame: three constructed vignettes, each passed by its judge, stacked 'at scale' on the launch gate."""
    cards, heads, crits, outs, judges, stamps, stacks = (VGroup() for _ in range(7))
    for (head, cr, out), x in zip(VIG, VIG_X):
        cards.add(rbox(x, VIG_Y, VIG_W, VIG_H, PAPER, PAPER_LN))
        heads.add(T(head, SMALL).move_to([x, VIG_Y + 1.5, 0]))
        crits.add(crit_pill(x, VIG_Y + 0.75, cr))
        outs.add(VGroup(T(out[0], SMALL).move_to([x, VIG_Y - 0.15, 0]), T(out[1], SMALL).move_to([x, VIG_Y - 0.6, 0])))
        judges.add(judge(x - 1.05, VIG_Y - 1.5, r=0.27))
        stamps.add(VGroup(stamp(x - 0.15, VIG_Y - 1.5), T("pass", SMALL).move_to([x + 0.65, VIG_Y - 1.5, 0])))
        stacks.add(VGroup(*[rbox(x, VIG_Y - 0.12 * k, VIG_W, VIG_H, PAPER, PAPER_LN, sw=3) for k in (2, 1)]).set_z_index(-1))
    vig = VGroup(*[VGroup(cards[i], heads[i], crits[i], outs[i], judges[i], stamps[i]) for i in range(3)])
    return {"ct": ctag("illustration"), "vig": vig, "stacks": stacks,
            "gate": VGroup(Line([-6.1, -2.55, 0], [6.1, -2.55, 0], color=INK, stroke_width=8),
                           T("launch gate: the eval", SMALL).move_to([0, -2.98, 0]))}


class B02_Stakes(Scene):
    def construct(self):
        a, b = L01(), L02()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("ct",)), rt=0.4)
        for i, word in enumerate(("teams", "trust", "dies")):
            on(self, word)
            P(self, FadeIn(b["vig"][i], shift=UP * 0.15), rt=0.6)
        on(self, "gate")
        P(self, Create(b["gate"][0]), FadeIn(b["gate"][1], shift=UP * 0.1), rt=0.6)
        on(self, "criterion")
        P(self, *flash(*[v[0] for v in b["vig"]]), rt=0.6)
        on(self, "scale")
        P(self, LaggedStart(*[FadeIn(st, shift=DOWN * 0.1) for st in b["stacks"]], lag_ratio=0.2), rt=0.6)
        on(self, "passing")
        P(self, *[pulse(v[5], 1.15) for v in b["vig"]], rt=0.6)
        on(self, "attached")
        P(self, *[Indicate(v[5][1], color=INK, scale_factor=1.15) for v in b["vig"]], rt=0.5)
        finish(self)


def L03():
    """B03's last frame: Readback asks the PM about the criterion before the score is trusted; the vision; the status."""
    c = chip(1.65, 1.2, "crit")
    tiles = VGroup(VGroup(rbox(-4.0, -1.6, 3.7, 1.3, PAPER, GREY, op=0), T("criteria", BODY).move_to([-4.0, -1.38, 0]),
                          T("module 1 · Readback", SMALL).move_to([-4.0, -1.85, 0])),
                   VGroup(will_box(0.0, -1.6, 3.7, 1.3, fill=False), T("system prompts", BODY).move_to([0.0, -1.38, 0]), T("later", SMALL).move_to([0.0, -1.85, 0])),
                   VGroup(will_box(4.0, -1.6, 3.7, 1.3, fill=False), T("PRDs", BODY).move_to([4.0, -1.38, 0]), T("later", SMALL).move_to([4.0, -1.85, 0])))
    return {"ct": ctag("planned", "vision"), "title": lx(T("Readback", H1, bold=True).move_to([0, 2.45, 0]), LX),
            "who": pm(-5.6, 1.15, 0.8), "bub": bubble_left(-2.75, 1.25, "What did you mean?", 4.46, tip=0.12),   # text measures 3.86
            "chip": c, "halo": halo(c), "score": VGroup(stamp(4.35, 1.2), T("score", BODY).move_to([5.25, 1.2, 0])).set_opacity(0.4),
            "vt": T("vision: a copilot for what PMs write for AI", H3, bold=True).move_to([0, -0.3, 0]),
            "tiles": tiles, "disc": T("Readback is planned · nothing has run yet", BODY).move_to([0, -2.85, 0])}


class B03_Readback(Scene):
    def construct(self):
        a, b = L02(), L03()
        self.add(*a.values())
        ct = a["ct"]
        P(self, *fade_all(a, keep=("ct",)), Transform(ct, ctag("planned")), rt=0.4)
        P(self, FadeIn(b["title"], shift=UP * 0.15), FadeIn(b["disc"]), rt=0.4)          # the status line stays on screen
        on(self, "criterion")
        P(self, FadeIn(b["chip"], scale=0.85), FadeIn(b["halo"]), rt=0.5)
        on(self, "ask")
        P(self, FadeIn(b["who"], shift=RIGHT * 0.1), FadeIn(b["bub"], shift=UP * 0.1), rt=0.5)
        on(self, "meant")
        P(self, *flash(b["bub"][1]), pulse(b["chip"], 1.05), rt=0.5)
        on(self, "trusts")
        P(self, FadeIn(b["score"]), rt=0.4)
        row = band(-6.4, 6.4, 0.35, 2.0)
        self.add(row)
        on(self, "score")
        P(self, *flash(row, color=KRAFT_LT), rt=0.5)
        on(self, "module")
        P(self, FadeIn(b["tiles"][0], shift=UP * 0.15), Transform(ct, b["ct"]), rt=0.5)
        on(self, "vision")
        P(self, FadeIn(b["vt"], shift=UP * 0.1), rt=0.4)
        on(self, "copilot")
        P(self, LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in b["tiles"][1:]], lag_ratio=0.25), rt=0.6)
        on(self, "planned")
        P(self, Indicate(b["disc"], color=INK, scale_factor=1.06), rt=0.5)
        finish(self)


# ═════════════════════════════ 2 · INTRODUCTION ═════════════════════════════
NODE_X, NODE_Y, NODE_W, NODE_H = [-4.3, 0.0, 4.3], -0.35, 3.7, 2.8
CHIP_TOP = (5.0, 2.2)


def flow_frame():
    return (VGroup(*[real_card(x, NODE_Y, NODE_W, NODE_H) for x in NODE_X]),
            VGroup(arrow((-2.42, NODE_Y), (-1.88, NODE_Y)), arrow((1.88, NODE_Y), (2.42, NODE_Y))))


def L04():
    nodes, arrows = flow_frame()
    x1, x2, x3 = NODE_X
    return {"rail": rail(PARTS4[1]), "tag": tag(TAG_DOCS), "title": title("Maxim AI"),
            "chip": chip(*CHIP_TOP, "crit_c"), "nodes": nodes, "arrows": arrows,
            "n1": VGroup(*[judge(x1 + dx, 0.6, r=0.34, fill=KRAFT_DK) for dx in (-0.9, 0, 0.9)], lines2("several models", "as judges", x1, -0.55, BODY)),
            "n2": VGroup(stamp(x2 - 0.85, 0.6, r=0.3), stamp(x2, 0.6, ok=False, r=0.3), stamp(x2 + 0.85, 0.6, r=0.3),
                         lines2("compares", "their verdicts", x2, -0.55, BODY)),
            "n3": VGroup(lines2("agreement with", "human labels", x3, 0.35, BODY), pill(x3, -1.2, "agreement score"))}


def L05():
    d = L04()
    x1, x2, x3 = NODE_X
    d.update({"title": title("orq.ai"),
              "n1": VGroup(judge(x1 - 0.75, 0.6, r=0.34, fill=KRAFT_DK), T("vs", BODY).move_to([x1, 0.6, 0]), doc_icon(x1 + 0.75, 0.6, 0.7, 0.9, fill=STAGE),
                           lines2("an evaluator vs", "human labels", x1, -0.55, BODY)),
              "n2": VGroup(stamp(x2 - 0.5, 0.6, r=0.3), stamp(x2 + 0.5, 0.6, r=0.3), lines2("same answer", "twice?", x2, -0.55, BODY)),
              "n3": VGroup(lines2("then proposes", "a rewrite", x3, 0.35, BODY), pill(x3, -1.2, "rewritten prompt"))})
    return d


def L06():
    d = L04()
    x1, x2, x3 = NODE_X
    d.update({"title": title("GitHub Spec Kit"),
              "n1": VGroup(doc_icon(x1, 0.6, 0.7, 0.9, fill=STAGE), lines2("for specs,", "not rubrics", x1, -0.55, BODY)),
              "n2": VGroup(T("?", H2, bold=True).move_to([x2 - 0.6, 0.6, 0]), arrow((x2 - 0.28, 0.6), (x2 + 0.32, 0.6)),
                           tick(x2 + 0.66, 0.58, s=0.24), lines2("an optional", "clarify step", x2, -0.55, BODY)),
              "n3": VGroup(lines2("resolves ambiguity", "before planning", x3, 0.35, BODY), pill(x3, -1.2, "clearer spec"))})
    return d


def L07():
    cols = [("Maxim AI", "agreement score"), ("orq.ai", "rewritten prompt"), ("GitHub Spec Kit", "clearer spec")]
    c = chip(0, -1.45, "crit")
    return {"rail": rail(PARTS4[1]), "tag": tag(TAG_DOCS), "title": title("From the tools I checked"),
            "names": VGroup(*[T(n, BODY, bold=True).move_to([x, 1.45, 0]) for (n, _), x in zip(cols, NODE_X)]),
            "outs": VGroup(*[pill(x, 0.72, o, fill=KRAFT) for (_, o), x in zip(cols, NODE_X)]),
            "drops": VGroup(*[DashedLine([x, 0.35, 0], [x, 0.03, 0], color=GREY, stroke_width=4, dash_length=0.08) for x in NODE_X]),
            "xs": VGroup(*[cross(x, -0.2) for x in NODE_X]),
            "nf": VGroup(*[T("not found in docs", SMALL).move_to([x, -0.62, 0]) for x in NODE_X]),
            "chip": c, "slot": will_box(0, -1.45, 2.9, 1.0, fill=False),
            "what": T("names the criterion behind a disagreement", BODY).move_to([0, -2.4, 0])}


def L08():
    x1, x2, x3 = NODE_X
    c = chip(x2, 0.65, "crit_c")
    return {"rail": rail(PARTS4[1]), "tag": ctag("planned"),
            "title": title("Why Readback matters on any AI feature"),
            "tiles": VGroup(*[rbox(x, -0.25, 3.6, 3.3) for x in NODE_X]),
            "arrows": VGroup(arrow((-2.45, -0.25), (-1.85, -0.25)), arrow((1.85, -0.25), (2.45, -0.25))),
            "t1": VGroup(gauge(x1, 0.65), T("a score", H3, bold=True).move_to([x1, -0.3, 0]),
                         T("something is wrong", SMALL).move_to([x1, -0.95, 0])),
            "chip": c, "halo": halo(c),
            "t2": VGroup(T("the criterion", H3, bold=True).move_to([x2, -0.3, 0]), T("what to fix", SMALL).move_to([x2, -0.95, 0])),
            "t3": VGroup(pm(x3 - 0.75, 0.55, 0.8),
                         bubble(x3 + 0.5, 0.75, "?", tail=[(x3 + 0.08, 0.66), (x3 + 0.08, 0.86), (x3 - 0.2, 0.68)]),
                         T("a question", H3, bold=True).move_to([x3, -0.3, 0]), T("the PM decides", SMALL).move_to([x3, -0.95, 0])),
            "nr": T("not a rewrite", SMALL).move_to([x3, -1.5, 0])}


class B04_Maxim(Scene):
    def construct(self):
        a, b = L03(), L04()
        self.add(*a.values())
        chapter_in(self, a, 2)                                   # chapter card 2 replaces the old near-empty frame
        P(self, FadeIn(b["chip"]), FadeIn(b["tag"]), rt=0.4)
        what = title("What others have done")
        P(self, FadeIn(what, shift=UP * 0.15), rt=0.4)
        on(self, "tools")
        names = VGroup(*[VGroup(real_card(x, 0.2, 3.7, 1.1), T(n, BODY, bold=True).move_to([x, 0.2, 0]))
                         for n, x in zip(["Maxim AI", "orq.ai", "GitHub Spec Kit"], [-4.25, 0.0, 4.25])])
        P(self, LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in names], lag_ratio=0.2), rt=0.7)
        on(self, "reliable")
        P(self, LaggedStart(*[Indicate(n[1], color=INK, scale_factor=1.08) for n in names], lag_ratio=0.2), rt=0.7)
        on(self, "Maxim")
        P(self, FadeOut(what), FadeOut(names), rt=0.35)
        P(self, FadeIn(b["title"], shift=UP * 0.15), rt=0.4)
        on(self, "several")
        P(self, FadeIn(b["nodes"][0], shift=UP * 0.15), FadeIn(b["n1"], shift=UP * 0.15), rt=0.6)
        on(self, "compares")
        P(self, GrowArrow(b["arrows"][0]), FadeIn(b["nodes"][1], shift=UP * 0.15), FadeIn(b["n2"], shift=UP * 0.15), rt=0.6)
        on(self, "measures")
        P(self, GrowArrow(b["arrows"][1]), FadeIn(b["nodes"][2], shift=UP * 0.15), FadeIn(b["n3"][0], shift=UP * 0.15), rt=0.6)
        on(self, "labels")
        P(self, FadeIn(b["n3"][1], shift=UP * 0.15), rt=0.5)
        finish(self)


def _swap_tool(self, a, b, cues):
    """B05/B06: same flow frame, new tool; contents swap on their spoken words."""
    self.add(*a.values())
    # node 1 stays; nodes 2 and 3 leave with the old tool and come back with the new one, on their words
    P(self, ReplacementTransform(a["title"], b["title"]), *[FadeOut(a[k]) for k in ("n1", "n2", "n3", "arrows", "nodes")], rt=0.45)
    for key, word in cues:
        on(self, word)
        if key == "n1":
            P(self, FadeIn(b["nodes"][0], shift=UP * 0.15), FadeIn(b["n1"], shift=UP * 0.15), rt=0.5)
        elif key == "n2":
            P(self, GrowArrow(b["arrows"][0]), FadeIn(b["nodes"][1], shift=UP * 0.15), FadeIn(b["n2"], shift=UP * 0.15), rt=0.55)
        elif key == ("n3", 0):
            P(self, GrowArrow(b["arrows"][1]), FadeIn(b["nodes"][2], shift=UP * 0.15), FadeIn(b["n3"][0], shift=UP * 0.15), rt=0.55)
        elif isinstance(key, tuple):
            P(self, FadeIn(b[key[0]][key[1]], shift=UP * 0.15), rt=0.45)
        else:
            P(self, FadeIn(b[key], shift=UP * 0.15), rt=0.5)
    finish(self)


class B05_Orq(Scene):
    def construct(self):
        b = L05()
        _swap_tool(self, L04(), b, [("n1", "compares"), ("n2", "checks"), (("n3", 0), "proposes"), (("n3", 1), "prompt")])


class B06_SpecKit(Scene):
    def construct(self):
        _swap_tool(self, L05(), L06(), [("n1", "specs"), ("n2", "optional"), (("n3", 0), "resolves"), (("n3", 1), "planning")])


class B07_Gap(Scene):
    def construct(self):
        a, b = L06(), L07()
        self.add(*a.values())
        P(self, *[FadeOut(a[k]) for k in ("nodes", "arrows", "n1", "n2", "n3")], ReplacementTransform(a["title"], b["title"]), rt=0.5)
        P(self, Transform(a["chip"], b["chip"]), rt=0.6)          # the chip comes down to wait under the outputs
        for i, word in enumerate(["agreement", "rewritten", "clearer"]):
            on(self, word)
            P(self, FadeIn(b["names"][i], shift=UP * 0.15), FadeIn(b["outs"][i], shift=UP * 0.15), rt=0.45)
        on(self, "What")
        P(self, pulse(a["chip"]), *flash(*[o[0] for o in b["outs"]], color=KRAFT_DK), rt=0.6)
        on(self, "documentation")
        P(self, LaggedStart(*[Create(x) for x in b["drops"]], lag_ratio=0.15),
          LaggedStart(*[FadeIn(x, scale=0.6) for x in b["xs"]], lag_ratio=0.15), rt=0.6)
        on(self, "October")
        P(self, LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in b["nf"]], lag_ratio=0.15), rt=0.6)
        on(self, "naming")
        P(self, Create(b["slot"]), FadeIn(b["what"], shift=UP * 0.15), rt=0.6)
        on(self, "disagreement")
        P(self, pulse(a["chip"], 1.06), rt=0.6)
        finish(self)


class B08_WhyMine(Scene):
    def construct(self):
        a, b = L07(), L08()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("rail", "title", "chip")), rt=0.45)
        P(self, Transform(a["chip"], b["chip"]), rt=0.5)
        on(self, "Reed-back")
        P(self, ReplacementTransform(a["title"], b["title"]), FadeIn(b["tag"]), FadeIn(b["halo"]), rt=0.5)
        on(self, "score")
        P(self, FadeIn(b["tiles"][0], shift=UP * 0.15), FadeIn(b["t1"], shift=UP * 0.15), rt=0.5)
        on(self, "criterion")
        P(self, GrowArrow(b["arrows"][0]), FadeIn(b["tiles"][1], shift=UP * 0.15), FadeIn(b["t2"], shift=UP * 0.15), rt=0.6)
        on(self, "question")
        P(self, GrowArrow(b["arrows"][1]), FadeIn(b["tiles"][2], shift=UP * 0.15), FadeIn(b["t3"], shift=UP * 0.15), rt=0.6)
        on(self, "rewrite")
        P(self, FadeIn(b["nr"], shift=UP * 0.1), rt=0.4)
        on(self, "decision")
        P(self, Indicate(b["tiles"][2], color=PAPER_LN, scale_factor=1.0), Indicate(b["t3"][3], color=INK, scale_factor=1.1), rt=0.7)
        finish(self)


# ═════════════════════════════ 3 · METHODS (the pipeline builds itself) ═════════════════════════════
STRIP = [("AMI data", "real"), ("Recaps", "real"), ("Rubric", "made"), ("Labels", "will"), ("Judges", "will"), ("Readback", "will")]
SX, SY, SW, SH = [-5.175, -3.105, -1.035, 1.035, 3.105, 5.175], 2.3, 1.95, 0.62


def strip(k, active=None):
    """The method pipeline: nodes before k are built (in their colour role), the rest are skeletons."""
    nodes = VGroup()
    for i, (name, kind) in enumerate(STRIP):
        x = SX[i]
        if i >= k:
            nodes.add(VGroup(DashedVMobject(rbox(x, SY, SW, SH, PAPER, PAPER_LN, sw=4, op=0), num_dashes=22)))
            continue
        box = {"real": rbox(x, SY, SW, SH, KRAFT, GREY), "made": rbox(x, SY, SW, SH, PAPER, PAPER_LN)}.get(kind)
        nodes.add(VGroup(box if box is not None else will_box(x, SY, SW, SH), T(name, SMALL, bold=(i == active)).move_to([x, SY, 0])))
    links = VGroup(*[Line([SX[i] + SW / 2, SY, 0], [SX[i + 1] - SW / 2, SY, 0], color=GREY, stroke_width=4)
                     for i in range(5)])
    return VGroup(links, nodes)


def meeting_cards():
    cards, ids, durs, decs = VGroup(), VGroup(), VGroup(), VGroup()
    for i, (m, dec, dur) in enumerate(SEL):
        x, y = [-4.9, -2.45, 0.0, 2.45, 4.9][i % 5], [0.05, -1.7][i // 5]
        cards.add(real_card(x, y, 2.34, 1.55))
        ids.add(Tm(m, BODY).move_to([x, y + 0.45, 0]))
        durs.add(T(f"{int(dur // 60)} min {int(round(dur % 60))} s", SMALL).move_to([x, y, 0]))
        decs.add(T(f"{dec} decisions", SMALL).move_to([x, y - 0.45, 0]))
    return cards, ids, durs, decs


def L09():
    cards, ids, durs, decs = meeting_cards()
    return {"ct": ctag("test case"), "tag": tag("AMI corpus · CC BY 4.0"), "src": src("data: case-study/data/sample/selection.csv"),
            "strip": strip(1, 0), "title": T("86 decisions", H1, bold=True).move_to([0, 1.3, 0]),
            "cards": cards, "ids": ids, "durs": durs, "decs": decs}


def L10():
    """B10's last frame: the real transcript line, compact; the real recap output, hero size, with nine more behind it."""
    stack = VGroup(*[rbox(0.03 * k, -1.05 + 0.01 * k, 11.4 + 0.06 * k, 2.5 + 0.02 * k, KRAFT, GREY, sw=2)
                     for k in range(9, 0, -1)]).set_z_index(-1)      # the other nine peek out at the top and right
    return {"ct": ctag("test case"), "strip": strip(2, 1),
            "tl": lx(T("AMI ES2007a transcript · CC BY 4.0", SMALL).move_to([0, 1.66, 0]), LX),
            "tc": real_card(0, 0.95, 12.1, 0.85), "tt": T(TRANSCRIPT, H3).move_to([0, 0.95, 0]),
            "stack": stack, "rc": real_card(0, -1.05, 11.4, 2.5),
            "rt": VGroup(*[lx(T(t, H2).move_to([0, -0.3 - 0.74 * i, 0]), -5.3) for i, t in enumerate(RC_HERO)]),
            "rl": lx(T("10 real recaps · claude-opus-5-5 · 14 Oct 2026", SMALL).move_to([0, -2.8, 0]), LX)}


ROW_Y = [1.08, 0.58, 0.1, -0.72, -1.56]      # C4 is the two-line chip, so its row is taller


def L11():
    c = chip(0, ROW_Y[3])
    lx(c, -5.95)
    items = VGroup(*[T(s, SMALL) for s in (*DEC_ITEMS[0], *DEC_ITEMS[1])])
    for t, y in zip(items, (0.15, -0.27, -0.85, -1.27)):
        lx(t.move_to([0, y, 0]), 1.8)
    return {"ct": ctag("test case"), "strip": strip(3, 2),
            "rcard": made_card(-2.4, -0.35, 7.4, 3.9),
            "ids": VGroup(*[T(f"C{i + 1}", SMALL, bold=True).move_to([-5.8, ROW_Y[i], 0]) for i in (0, 1, 2, 4)]),
            "rows": VGroup(*[lx(T(CLAUSES[i], SMALL).move_to([0, ROW_Y[i], 0]), -5.32) for i in (0, 1, 2, 4)]),
            "chip": c, "rk": lx(T("CONSTRUCTED · rubric-v0.md", SMALL).move_to([0, -2.62, 0]), LX),
            "dcard": real_card(3.825, -0.35, 4.55, 3.9),
            "dhead": VGroup(lx(T("ES2007a · DECISIONS", SMALL, bold=True).move_to([0, 1.15, 0]), 1.8),
                            lx(T("human-written", SMALL).move_to([0, 0.7, 0]), 1.8)),
            "items": items, "more": lx(T("… 7 in this meeting", SMALL).move_to([0, -1.85, 0]), 1.8),
            "link": VGroup(Line([1.22, ROW_Y[0], 0], [1.55, ROW_Y[0], 0], color=INK, stroke_width=7),
                           Dot([1.22, ROW_Y[0], 0], radius=0.09, color=INK), Dot([1.55, ROW_Y[0], 0], radius=0.09, color=INK)),
            "ticks": VGroup(tick(5.75, -0.06), tick(5.75, -1.06)),
            "dk": rx(T("AMI ES2007a · CC BY 4.0", SMALL).move_to([0, -2.62, 0]), -LX)}


CHIP_PARK = (5.35, -2.45)


def label_grid():
    ids, rows = VGroup(), VGroup()
    for i, (m, dec, _dur) in enumerate(SEL):
        y = 1.5 - 0.42 * i
        ids.add(lx(Tm(m, SMALL).move_to([0, y, 0]), LX))
        rows.add(VGroup(*[will_box(-3.9 + 0.42 * j, y, 0.34, 0.34, fill=False) for j in range(dec)]))
    return ids, rows


def L12():
    ids, rows = label_grid()
    return {"ct": ctag("planned", "test case"), "strip": strip(4, 3),
            "chip": chip(*CHIP_PARK, "compact"), "gids": ids, "grows": rows,
            "hl": T("my human labels", H3, bold=True).move_to([3.7, 1.3, 0]),
            "hs": T("86 decisions, marked by me", SMALL).move_to([3.7, 0.78, 0]),
            "hb": VGroup(will_box(3.7, 0.15, 4.3, 0.7), T("planned · not marked yet", SMALL).move_to([3.7, 0.15, 0])),
            "d1": VGroup(judge(1.75, -0.95, r=0.2, plan=True), lx(T("labels committed", SMALL).move_to([0, -0.95, 0]), 2.1)),
            "d2": VGroup(judge(1.75, -2.05, r=0.2, plan=True), lx(T("judges run", SMALL).move_to([0, -2.05, 0]), 2.1)),
            "arr": arrow((1.75, -1.2), (1.75, -1.8)),
            "gp": lx(T("git shows the order", SMALL).move_to([0, -1.5, 0]), 2.1)}


JY, GX, GH_Y = [0.85, -0.15, -1.15], [0.75, 1.7, 2.65, 3.6, 4.55], 1.6


def L13():
    return {"ct": ctag("planned", "test case"), "strip": strip(5, 4),
            "js": VGroup(*[judge(-5.4, y, r=0.38, plan=True) for y in JY]),
            "jl": VGroup(*[lx(T(s, BODY).move_to([0, y, 0]), -4.8) for s, y in
                           zip(["Claude", "a second provider's model", "a local open-weight model"], JY)]),
            "hdr": VGroup(*[T(f"C{i + 1}", SMALL, bold=True).move_to([GX[i], GH_Y, 0]) for i in (0, 1, 2, 4)]),
            "chip": chip(GX[3], GH_Y, "mini"),
            "cells": VGroup(*[will_box(x, y, 0.75, 0.62, fill=False) for y in JY for x in GX]),
            "m1": VGroup(lx(T("agreement between judges", SMALL).move_to([0, -1.85, 0]), LX), blank(1.6, -1.85, h=0.5)),
            "m2": VGroup(lx(T("judges vs my labels, decisions clause", SMALL).move_to([0, -2.4, 0]), LX), blank(1.6, -2.4, h=0.5))}


def trace_marks():
    """B14, first half: the judges split on C4 and the split is traced up to the chip (drawn over L13's grid)."""
    J14 = [JY[0] + 0.1, JY[1], JY[2] - 0.1]
    return {"marks": VGroup(tick(GX[3], J14[0] - 0.02, s=0.16), cross(GX[3], J14[1], s=0.14), tick(GX[3], J14[2] - 0.02, s=0.16)),
            "split": rbox(GX[3], JY[1], 0.75, 0.62, stroke=CLAUSE, sw=7, op=0), "halo": halo(chip(GX[3], GH_Y, "mini"), buff=0.1),
            "up": poly([(GX[3] + 0.375, JY[1]), (GX[3] + 0.475, JY[1]), (GX[3] + 0.475, GH_Y - 0.31)], sw=6)}


# B14's real example (ES2010b): every quote is a verbatim piece of its source file (asserted at the top)
EX_Q = "[00:20:44] ID: “Do we want this thing to be able to be found easily?”"
EX_A = "PM: “I think so.”     ME: “Sure, yeah.”"
EX_R = "Decisions: “The remote should be easy to find if lost [00:20:52]”"
EX_D = "AMI's DECISIONS list: “will consider including … a locator function”"


def L14():
    """B14's last frame: a real recap line where C4 is hard to call, the PM's question, then the PM's revision."""
    bub = bubble(-1.3, -2.45, "Does a quick yes count as a decision?", tail=[(-4.99, -2.33), (-4.99, -2.57), (-5.2, -2.45)])
    return {"strip": strip(6, 5), "ct": ctag("planned", "test case"),
            "tr": VGroup(real_card(0, 1.15, 12.2, 1.35), lx(T(EX_Q, SMALL).move_to([0, 1.42, 0]), -5.85),
                         lx(T(EX_A, SMALL).move_to([0, 0.88, 0]), -5.85), rx(T("ES2010b · AMI · CC BY 4.0", SMALL).move_to([0, 0.88, 0]), 5.85)),
            "rc": VGroup(real_card(0, -0.45, 12.2, 1.35), lx(T(EX_R, SMALL).move_to([0, -0.18, 0]), -5.85),
                         rx(T("real recap · claude-opus-5-5 · 14 Oct 2026", SMALL).move_to([0, -0.72, 0]), 5.85)),
            "ami": lx(T(EX_D, SMALL).move_to([0, -1.55, 0]), -5.85),
            "who": pm(-5.6, -2.45, 0.8), "chip": chip(3.35, -2.45, "mini"),
            "ask": will_pill(-1.3, -2.45, "C4 · revised by the PM"), "_bub": bub}


HAVE = ((("have",), "tick", ((("AMI data · 10 meetings",), ("in my repository",)), (("10 real recaps",), ("in my repository",)),
                             (("Claude (claude -p)",), ("set up on this Mac", "CLI 2.1.323")), (("compute",), ("this Mac",)))),
        (("account,", "not yet wired"), "open", ((("API credits",), ()), (("a second provider",), ()))),
        (("planned",), "open", ((("local open-weight", "model"), ("Ollama not installed",)), (("my human labels",), ("I mark the 86 decisions",)))))
COL_X, SEP_X = [-6.05, -1.40, 2.10], [-1.52, 1.98]   # measured: widest lines 4.40 / 3.25 / 3.87 at 36 and 32


def L15():
    """B15's last frame: what I have, in three columns (wording as verified on this Mac, 23 Nov 2026)."""
    heads, cols = VGroup(), VGroup()
    for (hl, kind, items), x0 in zip(HAVE, COL_X):
        icon = (tick(x0 + 0.17, 2.35, s=0.17) if kind == "tick" else
                DashedVMobject(Circle(radius=0.17, stroke_color=WILL, stroke_width=6).move_to([x0 + 0.2, 2.35, 0]), num_dashes=8))
        ht = VGroup(*[lx(T(t, BODY, bold=True).move_to([0, 2.35 + 0.21 * (len(hl) - 1) - 0.42 * k, 0]), x0 + 0.55) for k, t in enumerate(hl)])
        heads.add(VGroup(icon, ht))
        col, y = VGroup(), 1.55
        for names, det in items:
            item = VGroup()
            for t in names:
                item.add(lx(T(t, BODY).move_to([0, y, 0]), x0))
                y -= 0.52
            y += 0.05
            for t in det:
                item.add(lx(T(t, SMALL).move_to([0, y, 0]), x0))
                y -= 0.42
            col.add(item)
            y -= 0.15
        cols.add(col)
    return {"ct": ctag("test case"), "tag": tag("a tick means set up on this Mac · status as of 23 Nov 2026"),
            "heads": heads, "cols": cols, "seps": VGroup(*[Line([x, 2.75, 0], [x, -2.7, 0], color=GREY, stroke_width=3) for x in SEP_X])}


REQ_X = [-4.15, 0.0, 4.15]
REQS = (("a real AI feature", ("a meeting-recap", "feature")), ("public data", ("the AMI Meeting", "Corpus · CC BY 4.0")),
        ("human ground truth", ("human-written", "decision lists")))


class B09_TestBench(Scene):
    def construct(self):
        a, b = L08(), L09()
        self.add(*a.values())
        chapter_in(self, a, 3)                                   # chapter card 3 replaces the old near-empty frame
        reqs = VGroup(*[pill(x, 1.25, r) for (r, _), x in zip(REQS, REQ_X)])
        ans = VGroup(*[VGroup(tick(x - 1.75, 0.45, s=0.16), T(l1, SMALL).move_to([x + 0.15, 0.45, 0]), T(l2, SMALL).move_to([x + 0.15, 0.02, 0]))
                       for (_, (l1, l2)), x in zip(REQS, REQ_X)])
        big = VGroup(rbox(0, -1.55, 6.5, 1.05, PAPER, GREY, sw=6), T("test case, not the product", H3, bold=True).move_to([0, -1.55, 0]))
        P(self, FadeIn(b["strip"]), rt=0.3)
        for k, word in enumerate(("feature", "public", "human")):
            on(self, word)
            P(self, FadeIn(reqs[k], shift=UP * 0.15), rt=0.4)
        rb = band(-6.4, 6.4, -0.35, 1.75)                      # behind the three requirements
        self.add(rb)
        for k, word in enumerate(("chose", "Corpus", "lists")):
            on(self, word)
            extra = flash(rb, color=KRAFT_LT) if word == "chose" else ([FadeIn(b["tag"]), FadeIn(b["src"])] if word == "Corpus" else [])
            P(self, FadeIn(ans[k], shift=UP * 0.1), *extra, rt=0.45)
            if word == "chose":
                self.remove(rb)                                  # the band is only there for its flash
            if word == "Corpus":
                on(self, "ships")
                P(self, *flash(*[r[0] for r in reqs]), rt=0.5)
        on(self, "test", 2)
        P(self, FadeIn(big, scale=0.9), rt=0.45)
        on(self, "product")
        P(self, Indicate(big[1], color=INK, scale_factor=1.06), rt=0.45)
        P(self, FadeOut(reqs), FadeOut(ans), FadeOut(big), FadeIn(b["ct"]), rt=0.4)   # the big tag becomes the corner tag
        on(self, "ten")
        P(self, LaggedStart(*[FadeIn(VGroup(c, i, du), shift=UP * 0.15) for c, i, du in zip(b["cards"], b["ids"], b["durs"])], lag_ratio=0.05), rt=0.6)
        on(self, "eighty-six")
        P(self, FadeIn(b["title"]), LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in b["decs"]], lag_ratio=0.05), rt=0.8)
        finish(self)


class B10_Feature(Scene):
    def construct(self):
        a, b = L09(), L10()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("rail", "strip", "ct")), Transform(a["strip"], b["strip"]), rt=0.5)
        hero = VGroup(real_card(0, 0.6, 12.1, 1.8), lx(T(TR_HERO[0], H2).move_to([0, 1.0, 0]), -5.85),
                      lx(T(TR_HERO[1], H2).move_to([0, 0.2, 0]), -5.85),
                      rx(T("AMI ES2007a transcript · CC BY 4.0", SMALL).move_to([0, 1.0, 0]), 5.85))
        pc = VGroup(made_card(-2.6, -1.5, 6.9, 1.05), T("CONSTRUCTED · my recap prompt", SMALL).move_to([-2.6, -1.6, 0]))
        cl = VGroup(real_card(3.9, -1.55, 4.4, 0.95), T("Claude · claude-opus-5-5", SMALL).move_to([3.9, -1.55, 0]))
        arr = arrow((0.95, -1.55), (1.6, -1.55))
        on(self, "recap")
        P(self, FadeIn(hero, shift=UP * 0.15), rt=0.5)                    # the real transcript line, hero size
        on(self, "prompt")
        P(self, FadeIn(pc, shift=UP * 0.15), rt=0.4)                      # the chain builds under it
        on(self, "Claude")
        P(self, GrowArrow(arr), FadeIn(cl, shift=RIGHT * 0.15), rt=0.45)
        on(self, "ran")
        P(self, FadeOut(VGroup(hero, pc, cl, arr)), rt=0.3)
        P(self, FadeIn(VGroup(b["tc"], b["tt"]), shift=UP * 0.1), FadeIn(b["tl"]),
          FadeIn(b["rc"], shift=UP * 0.15), FadeIn(b["rt"], shift=UP * 0.15), rt=0.5)   # the real recap output, hero size
        on(self, "fourteenth")
        rl0 = lx(T("real output · claude-opus-5-5 · 14 Oct 2026", SMALL).move_to([0, -2.8, 0]), LX)
        P(self, FadeIn(rl0, shift=UP * 0.1), rt=0.4)
        on(self, "ten")
        P(self, LaggedStart(*[FadeIn(st) for st in b["stack"]], lag_ratio=0.08), ReplacementTransform(rl0, b["rl"]), rt=0.8)
        finish(self)


class B11_Rubric(Scene):
    def construct(self):
        a, b = L10(), L11()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("rail", "strip", "ct")), Transform(a["strip"], b["strip"]), rt=0.5)
        on(self, "rubric")
        P(self, FadeIn(b["rcard"], shift=UP * 0.15), FadeIn(b["rk"]), rt=0.45)
        on(self, "five")
        rows = [VGroup(b["ids"][k], b["rows"][k]) for k in range(4)]
        P(self, LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rows], lag_ratio=0.12), rt=0.8)
        on(self, "every")
        P(self, Indicate(rows[0][1], color=INK, scale_factor=1.03), rt=0.6)
        on(self, "report")
        P(self, FadeIn(b["chip"], scale=0.85), rt=0.5)                    # C4, in plain English, is the hero chip
        on(self, "questions")
        P(self, pulse(b["chip"], 1.04), rt=0.45)
        on(self, "decisions", 2)
        P(self, Indicate(rows[0][1], color=INK, scale_factor=1.03), *flash(b["rcard"][0]), rt=0.6)
        on(self, "anchored")
        P(self, FadeIn(VGroup(b["dcard"], b["dhead"], b["items"], b["more"]), shift=LEFT * 0.2), FadeIn(b["dk"]), rt=0.6)
        on(self, "list")
        P(self, Create(b["link"]), rt=0.5)
        on(self, "answer")
        P(self, LaggedStart(*[Create(t) for t in b["ticks"]], lag_ratio=0.3), Indicate(b["dcard"], color=KRAFT_DK, scale_factor=1.0), rt=0.7)
        finish(self)


class B12_Labels(Scene):
    def construct(self):
        a, b = L11(), L12()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("rail", "strip", "chip", "ct")), Transform(a["strip"], b["strip"]), rt=0.45)
        P(self, FadeOut(a["chip"], scale=0.6), FadeIn(b["chip"], scale=0.8), Transform(a["ct"], b["ct"]), rt=0.5)
        on(self, "mark")
        P(self, LaggedStart(*[FadeIn(VGroup(i, r), shift=RIGHT * 0.1) for i, r in zip(b["gids"], b["grows"])], lag_ratio=0.1), rt=1.2)
        on(self, "covers")
        P(self, LaggedStart(*[Indicate(i, color=INK, scale_factor=1.12) for i in b["gids"]], lag_ratio=0.1), rt=1.0)
        on(self, "human")
        P(self, FadeIn(b["hl"], shift=UP * 0.15), FadeIn(b["hs"], shift=UP * 0.15), rt=0.45)
        on(self, "commit")
        P(self, FadeIn(b["hb"], shift=UP * 0.1), FadeIn(b["d1"], shift=UP * 0.1), rt=0.45)
        on(self, "first")
        P(self, GrowArrow(b["arr"]), FadeIn(b["d2"], shift=DOWN * 0.1), rt=0.5)
        on(self, "history")
        P(self, FadeIn(b["gp"], shift=RIGHT * 0.1), Indicate(b["arr"], color=INK), rt=0.6)
        finish(self)


class B13_Judges(Scene):
    def construct(self):
        a, b = L12(), L13()
        self.add(*a.values())
        P(self, *fade_all(a, keep=("rail", "strip", "chip", "ct")), Transform(a["strip"], b["strip"]), rt=0.4)
        on(self, "judges")
        P(self, LaggedStart(*[FadeIn(j, shift=UP * 0.15) for j in b["js"]], lag_ratio=0.2), rt=0.6)
        on(self, "every")
        P(self, FadeIn(b["hdr"], shift=DOWN * 0.1), Transform(a["chip"], b["chip"]), rt=0.6)
        on(self, "Claude")
        P(self, FadeIn(b["jl"][0], shift=RIGHT * 0.1), rt=0.4)
        on(self, "second")
        P(self, FadeIn(b["jl"][1], shift=RIGHT * 0.1), rt=0.4)
        on(self, "local")
        P(self, FadeIn(b["jl"][2], shift=RIGHT * 0.1), rt=0.4)
        P(self, LaggedStart(*[FadeIn(c) for c in b["cells"]], lag_ratio=0.04), rt=0.9)
        on(self, "measure")
        P(self, FadeIn(b["m1"], shift=UP * 0.15), LaggedStart(*[Indicate(t, color=INK, scale_factor=1.08) for t in b["jl"]], lag_ratio=0.2), rt=0.7)
        on(self, "human")
        P(self, FadeIn(b["m2"], shift=UP * 0.15), Indicate(b["m1"][0], color=INK, scale_factor=1.05), rt=0.5)
        on(self, "decisions")
        P(self, LaggedStart(*[pulse(m, 1.1) for m in (b["hdr"][0], *[b["cells"][5 * r] for r in range(3)])], lag_ratio=0.15),
          Indicate(b["m2"][0], color=INK, scale_factor=1.04), rt=0.6)
        finish(self)


class B14_Trace(Scene):
    def construct(self):
        a, b, g = L13(), L14(), trace_marks()
        self.add(*a.values())
        P(self, FadeOut(a["m1"]), FadeOut(a["m2"]), Transform(a["strip"], b["strip"]), rt=0.45)
        on(self, "split")
        top, bot = VGroup(a["js"][0], a["jl"][0], *a["cells"][0:5]), VGroup(a["js"][2], a["jl"][2], *a["cells"][10:15])
        P(self, top.animate.shift(UP * 0.1), bot.animate.shift(DOWN * 0.1), rt=0.4)
        P(self, LaggedStart(*[Create(m) for m in g["marks"]], lag_ratio=0.25), Create(g["split"]), rt=0.5)
        on(self, "trace")
        P(self, Create(g["up"]), rt=0.5)
        on(self, "clause")
        P(self, FadeIn(g["halo"]), pulse(a["chip"], 1.12), rt=0.5)
        on(self, "ask")
        P(self, FadeIn(b["who"], shift=RIGHT * 0.1), rt=0.35)
        on(self, "real")                                         # a real recap line where C4 is hard to call
        P(self, FadeOut(VGroup(a["js"], a["jl"], a["hdr"], a["cells"], a["chip"], *g.values())), rt=0.35)
        P(self, FadeIn(b["tr"], shift=UP * 0.15), rt=0.45)
        on(self, "yeses")
        P(self, FadeIn(b["rc"], shift=UP * 0.15), FadeIn(b["ami"], shift=UP * 0.1), rt=0.5)
        on(self, "count")
        P(self, FadeIn(b["_bub"], shift=UP * 0.1), FadeIn(b["chip"], scale=0.85), rt=0.45)
        on(self, "answers")
        P(self, Indicate(b["who"], color=INK, scale_factor=1.06), rt=0.4)
        on(self, "revises")
        P(self, FadeOut(b["_bub"]), rt=0.25)
        P(self, FadeIn(b["ask"], shift=UP * 0.1), rt=0.4)
        finish(self)


class B15_Have(Scene):
    def construct(self):
        a, b = L14(), L15()
        a.pop("_bub")
        self.add(*a.values())
        P(self, *fade_all(a, keep=("ct",)), Transform(a["ct"], b["ct"]), rt=0.45)
        P(self, FadeIn(b["tag"]), Create(b["seps"]), rt=0.35)
        col1, col2, col3 = b["cols"]
        cb = [band(-6.35, -1.52, -2.78, 2.88), band(-1.52, 1.98, -2.78, 2.88), band(1.98, 6.35, -2.78, 2.88)]
        self.add(*cb)
        steps = [("data", 0, col1[0:2]), ("Claude", None, col1[2:3]), ("credits", 1, col2[0:1]), ("provider", None, col2[1:2]),
                 ("local", 2, col3[0:1]), ("human", None, col3[1:2])]
        for word, h, items in steps:
            on(self, word)
            anims = [FadeIn(it, shift=RIGHT * 0.12) for it in items]
            if h is not None:
                anims.append(FadeIn(b["heads"][h], shift=DOWN * 0.1))
            P(self, *anims, rt=0.45)
            P(self, *[Indicate(it[0], color=INK, scale_factor=1.06) for it in items], rt=0.35)
            if word == "data":
                on(self, "repository")
                P(self, LaggedStart(*[Indicate(it[-1], color=INK, scale_factor=1.08) for it in col1[0:2]], lag_ratio=0.3),
                  *flash(cb[0], color=KRAFT_LT), rt=0.6)
            if word == "Claude":
                on(self, "here")                                 # "Claude runs here": compute, this Mac
                P(self, FadeIn(col1[3], shift=RIGHT * 0.12), rt=0.4)
                on(self, "subscription")
                P(self, *[Indicate(t, color=INK, scale_factor=1.08) for t in col1[2][1:]], *flash(cb[0], color=KRAFT_LT), rt=0.6)
                on(self, "My")
                P(self, *flash(cb[1], color=WILL_FILL), rt=0.5)
            if word == "provider":
                on(self, "wired")
                P(self, Indicate(b["heads"][1][1], color=INK, scale_factor=1.06), rt=0.5)
                on(self, "Still")                                # "Still to come": the planned column lights
                P(self, *flash(cb[2], color=WILL_FILL), rt=0.5)
        finish(self)


# ═════════════════════════════ 4 · EVALUATION (a pass/fail scorecard with empty results) ═════════════════════════════
ROWS = ((["1 · Planted ambiguity"], ["blames the", "planted clause"], ["another clause,", "or noise"]),
        (["2 · Decisions clause", "vs my human labels"], ["kappa ≥ 0.6", "for each judge"], ["kappa < 0.6"]),
        (["3 · Before and after"], ["agreement rises on", "held-out meetings"], ["stays the same,", "or drops"]))
COL_L, RES_X, VLINES = [-6.05, -2.15, 1.45], 5.4, [-2.3, 1.3, 4.6]


def _cell(lines, x, y):
    g = VGroup(*[T(s, SMALL) for s in lines])
    for k, t in enumerate(g):
        lx(t.move_to([0, y + 0.215 * (len(lines) - 1) - 0.43 * k, 0]), x)
    return g


def scorecard(expanded=False):
    """(head, lines, rows): rows[i] = VGroup(check, pass_if, fail_if, result)."""
    if expanded:
        hy, rys, hl, top = 2.05, [1.05, -0.25, -1.55], [1.7, 0.4, -0.9, -2.2], 2.4
    else:
        hy, rys, hl, top = 0.36, [-0.3775, -1.33, -2.28], [0.1, -0.855, -1.805, -2.755], 0.62
    head = VGroup(*[lx(T(s, SMALL, bold=True).move_to([0, hy, 0]), x) for s, x in zip(["Check", "Pass if", "Fail if"], COL_L)],
                  T("Result", SMALL, bold=True).move_to([RES_X, hy, 0]))
    lines = VGroup(*[Line([-6.1, y, 0], [6.1, y, 0], color=GREY, stroke_width=3) for y in hl],
                   *[Line([x, top, 0], [x, hl[-1], 0], color=GREY, stroke_width=3) for x in VLINES])
    rows = VGroup(*[VGroup(_cell(c, COL_L[0], y), _cell(p, COL_L[1], y), _cell(f, COL_L[2], y), blank(RES_X, y))
                    for (c, p, f), y in zip(ROWS, rys)])
    return head, lines, rows


DEMO_X, DEMO_Y = [-4.4, -2.2, 0.0, 2.2, 4.4], 1.85
TAG_EVAL = "PLANNED · nothing has run yet (EVAL-PLAN.md)"
TAG_EV = ("planned", "test case")


def mini_clauses():
    out = VGroup()
    for i, x in enumerate(DEMO_X):
        if i == 3:
            out.add(chip(x, DEMO_Y, "mini"))
        else:
            out.add(VGroup(RoundedRectangle(width=1.15, height=0.62, corner_radius=0.31, fill_color=PAPER, fill_opacity=1,
                                            stroke_color=GREY, stroke_width=4).move_to([x, DEMO_Y, 0]),
                           T(f"C{i + 1}", SMALL, bold=True).move_to([x, DEMO_Y, 0])))
    return out


def ring(x, sw=6, color=INK):
    return RoundedRectangle(width=1.5, height=0.95, corner_radius=0.47, stroke_color=color, stroke_width=sw,
                            fill_opacity=0).move_to([x, DEMO_Y, 0])


class B16_Planted(Scene):
    def construct(self):
        a = L15()
        self.add(*a.values())
        head, lines, rows = scorecard()
        chapter_in(self, a, 4)                                   # chapter card 4 replaces the old near-empty frame
        P(self, FadeIn(ctag(*TAG_EV)), rt=0.3)
        on(self, "Three")
        P(self, Create(lines), FadeIn(head, shift=UP * 0.1), rt=0.8)
        on(self, "pass")
        P(self, Indicate(head[1], color=INK, scale_factor=1.15), rt=0.4)
        on(self, "fail")
        P(self, LaggedStart(*[Indicate(h, color=INK, scale_factor=1.12) for h in head], lag_ratio=0.15), rt=0.5)
        on(self, "planted")
        P(self, FadeIn(rows[0][0], shift=RIGHT * 0.1), FadeIn(rows[0][3]), rt=0.45)
        on(self, "clause")
        mc = mini_clauses()
        P(self, LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in mc], lag_ratio=0.1), rt=0.6)
        on(self, "vague")
        lab = T("planted in C4 · one variant per clause, C1–C5", SMALL).move_to([0, 0.9, 0])
        pt = arrow((DEMO_X[3], 1.22), (DEMO_X[3], 1.52))
        P(self, FadeIn(lab), GrowArrow(pt), rt=0.5)
        on(self, "advance")
        P(self, pulse(mc[3], 1.15), Indicate(lab, color=INK, scale_factor=1.05), rt=0.6)
        on(self, "blames")
        r = ring(DEMO_X[3])
        ok = tick(DEMO_X[3] + 0.98, DEMO_Y + 0.45, s=0.18)
        P(self, Create(r), Create(ok), FadeIn(rows[0][1], shift=RIGHT * 0.1), rt=0.6)
        on(self, "planted", 2)
        P(self, Indicate(rows[0][1], color=INK, scale_factor=1.06), Indicate(lab, color=INK, scale_factor=1.05), rt=0.5)
        on(self, "another")
        r2, bad = ring(DEMO_X[1]), cross(DEMO_X[1] + 0.98, DEMO_Y + 0.45)
        P(self, FadeOut(r), FadeOut(ok), rt=0.25)
        P(self, Create(r2), FadeIn(bad, scale=0.6), FadeIn(rows[0][2][0], shift=RIGHT * 0.1), rt=0.45)
        on(self, "noise")
        noise = VGroup(*[ring(DEMO_X[i], sw=4, color=GREY) for i in (0, 2, 4)])
        bad2 = cross(5.48, DEMO_Y + 0.45)
        P(self, FadeOut(r2), FadeOut(bad), rt=0.25)
        P(self, LaggedStart(*[Create(n) for n in noise], lag_ratio=0.2), FadeIn(bad2, scale=0.6),
          FadeIn(rows[0][2][1], shift=RIGHT * 0.1), rt=0.5)
        finish(self)


def planted_end():
    """B16's last frame above the scorecard (B17 opens on it)."""
    return VGroup(mini_clauses(), T("planted in C4 · one variant per clause, C1–C5", SMALL).move_to([0, 0.9, 0]),
                  arrow((DEMO_X[3], 1.22), (DEMO_X[3], 1.52)), VGroup(*[ring(DEMO_X[i], sw=4, color=GREY) for i in (0, 2, 4)]),
                  cross(5.48, DEMO_Y + 0.45))


G0, G1, GY = 2.6, 5.8, 1.5
GT = G0 + 0.6 * (G1 - G0)          # the 0.6 bar on a low…high scale (a plan setting from EVAL-PLAN.md)


def k_demo():
    """B17's demo, piece by piece (B18 opens on all of it)."""
    return {"judge": VGroup(lx(T("each judge", SMALL).move_to([0, 1.62, 0]), LX), will_box(-0.55, 1.62, 4.9, 0.48)),
            "human": VGroup(lx(T("my human labels", SMALL).move_to([0, 2.3, 0]), LX), will_box(-0.55, 2.3, 4.9, 0.48)),
            "n86": VGroup(T("86 decisions, marked by me", SMALL).move_to([-0.55, 2.3, 0]), T("86 decisions", SMALL).move_to([-0.55, 1.62, 0])),
            "scale": VGroup(Line([G0, 1.22, 0], [G1, 1.22, 0], color=GREY, stroke_width=6),
                            T("low", SMALL).move_to([G0, 0.98, 0]), T("high", SMALL).move_to([G1 - 0.05, 0.98, 0]),
                            T("Cohen's kappa", BODY).move_to([4.2, 2.3, 0])),
            "pass": VGroup(rbox((GT + G1) / 2, GY, G1 - GT - 0.04, 0.46, WILL_FILL, WILL, sw=0, r=0.06),
                           T("pass", SMALL).move_to([(GT + G1) / 2, GY, 0])),
            "bar": VGroup(Line([GT, 1.16, 0], [GT, 1.84, 0], color=INK, stroke_width=7), T("0.6", SMALL).move_to([GT, 0.98, 0])),
            "lock": padlock(GT + 0.5, 0.98, s=0.38),
            "fail": VGroup(rbox((G0 + GT) / 2, GY, GT - G0 - 0.04, 0.46, WILL_FILL, WILL, sw=0, r=0.06),
                           T("fail", SMALL).move_to([(G0 + GT) / 2, GY, 0]))}


def bars_inverted(k):
    """Inverted flash of B17's two label bars: box ink, its text white."""
    out = []
    for key, t in (("human", k["n86"][0]), ("judge", k["n86"][1])):
        box = k[key][1]
        out += [Indicate(box[0], color=INK, scale_factor=1.0), Indicate(t, color=PAPER, scale_factor=1.0)]
    return out


class B17_Kappa(Scene):
    def construct(self):
        head, lines, rows = scorecard()
        tg, old, k = ctag(*TAG_EV), planted_end(), k_demo()
        r2 = band(-6.25, 6.25, -1.78, -0.88)                     # row 2 of the scorecard, between its rules
        self.add(rail(PARTS4[3]), tg, head, lines, rows[0], old, r2)
        P(self, FadeOut(old), rt=0.4)
        on(self, "decisions")
        P(self, FadeIn(rows[1][0], shift=RIGHT * 0.1), FadeIn(rows[1][3]), rt=0.45)
        on(self, "judge")
        P(self, FadeIn(k["judge"], shift=RIGHT * 0.15), rt=0.45)
        on(self, "human")
        P(self, FadeIn(k["human"], shift=RIGHT * 0.15), rt=0.45)
        on(self, "eighty-six")
        P(self, LaggedStart(*[FadeIn(t) for t in k["n86"]], lag_ratio=0.3), rt=0.5)
        on(self, "measured")
        P(self, LaggedStart(*[Indicate(t, color=INK, scale_factor=1.05) for t in (k["human"][0], k["judge"][0])], lag_ratio=0.2),
          *bars_inverted(k), rt=0.6)
        on(self, "Cohen's")
        P(self, Create(k["scale"][0]), FadeIn(k["scale"][1:]), rt=0.6)
        on(self, "point")
        P(self, FadeIn(k["pass"]), Create(k["bar"][0]), FadeIn(k["bar"][1]), FadeIn(rows[1][1], shift=RIGHT * 0.1), rt=0.6)
        on(self, "higher")
        P(self, *flash(r2, color=WILL_FILL), rt=0.5)
        on(self, "fix")
        P(self, FadeIn(k["lock"]), Indicate(k["bar"][1], color=INK, scale_factor=1.15), *bars_inverted(k), rt=0.5)
        on(self, "Below")
        P(self, FadeIn(k["fail"]), FadeIn(rows[1][2], shift=RIGHT * 0.1), rt=0.5)
        on(self, "fails")
        P(self, Indicate(k["fail"][0], color=INK, scale_factor=1.0), Indicate(k["fail"][1], color=PAPER, scale_factor=1.0),  # inverted flash
          LaggedStart(*[Indicate(t, color=INK, scale_factor=1.06) for t in rows[1][:3]], lag_ratio=0.2), rt=0.7)
        finish(self)


def ba_demo():
    """B18's demo, piece by piece (B19 opens on all of it). The held-out split's size is not shown (EVAL-PLAN.md)."""
    return {"chip": chip(-5.3, 1.9, "compact"), "arr": arrow((-4.4, 1.9), (-3.9, 1.9)),
            "rev": will_pill(-2.55, 1.9, "C4 · revised"), "why": T("PM revises the clause", SMALL).move_to([-3.6, 1.05, 0]),
            "ba": VGroup(lx(T("before", SMALL).move_to([0, 2.3, 0]), 2.6), blank(4.3, 2.3, w=1.0, h=0.5),
                         lx(T("after", SMALL).move_to([0, 1.62, 0]), 2.6), blank(4.3, 1.62, w=1.0, h=0.5)),
            "held": VGroup(*[rbox(0.7 + 0.09 * k, 1.95 + 0.07 * k, 1.5, 0.95, KRAFT, GREY, sw=2) for k in (2, 1, 0)],
                           padlock(0.7, 1.95, s=0.5), T("held-out meetings", SMALL).move_to([0.75, 1.05, 0])),
            "up": arrow((5.35, 1.45), (5.35, 2.5), color=INK, sw=8)}


class B18_BeforeAfter(Scene):
    def construct(self):
        head, lines, rows = scorecard()
        k, d = k_demo(), ba_demo()
        tg, old = ctag(*TAG_EV), VGroup(*k_demo().values())
        self.add(rail(PARTS4[3]), tg, head, lines, rows[0], rows[1], old)
        P(self, FadeOut(old), rt=0.4)
        on(self, "after")
        P(self, FadeIn(rows[2][0], shift=RIGHT * 0.1), FadeIn(rows[2][3]), rt=0.45)
        on(self, "revises")
        P(self, FadeIn(d["chip"], shift=UP * 0.15), rt=0.35)
        P(self, GrowArrow(d["arr"]), FadeIn(d["rev"], shift=RIGHT * 0.15), FadeIn(d["why"], shift=UP * 0.1), rt=0.6)
        on(self, "re-measure")
        P(self, LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in d["ba"]], lag_ratio=0.15), rt=0.6)
        on(self, "held")
        P(self, FadeIn(d["held"], shift=UP * 0.15), rt=0.5)
        on(self, "rise")
        P(self, GrowArrow(d["up"]), FadeIn(rows[2][1], shift=RIGHT * 0.1), rt=0.5)
        on(self, "help")
        P(self, FadeIn(rows[2][2], shift=RIGHT * 0.1), rt=0.45)
        on(self, "say")
        P(self, Indicate(rows[2][3][0], color=INK, scale_factor=1.0), Indicate(rows[2][3][1], color=PAPER, scale_factor=1.3), rt=0.6)
        finish(self)


class B19_Scorecard(Scene):
    def construct(self):
        head, lines, rows = scorecard()
        x, old = VGroup(head, lines, rows), VGroup(*ba_demo().values())
        tg = ctag(*TAG_EV)
        self.add(rail(PARTS4[3]), tg, x, old)
        P(self, FadeOut(old), rt=0.4)
        eh, el, er = scorecard(expanded=True)
        P(self, ReplacementTransform(x, VGroup(eh, el, er)), rt=0.8)
        on(self, "blank")
        P(self, *[Indicate(r[3][0], color=INK, scale_factor=1.0) for r in er],          # inverted flash: box ink, "—" white
          *[Indicate(r[3][1], color=PAPER, scale_factor=1.3) for r in er], rt=0.7)
        P(self, FadeIn(scorecard_note()), rt=0.45)
        on(self, "failed")
        P(self, FadeIn(failed_line()), rt=0.5)
        on(self, "scorecard")
        P(self, Indicate(eh[3], color=INK, scale_factor=1.2), rt=0.6)
        finish(self)


def scorecard_note():
    return lx(T("Result: will be measured · nothing has run as of 23 Nov 2026", SMALL).move_to([0, -2.55, 0]), LX)


def failed_line():
    return lx(T("a failed check goes on the scorecard too", SMALL).move_to([0, -3.05, 0]), LX)


# ═════════════════════════════ the close: what a pass would let a PM trust, on any AI feature; the vision ═════════════════════════════
def trust_row():
    who, meant, eq = pm(0, 0, 0.8), T("what the PM meant", BODY), T("=", H2)
    means, ps = T("what the score means", BODY), VGroup(stamp(0, 0), T("pass", BODY))
    ps[1].next_to(ps[0], RIGHT, buff=0.2)
    VGroup(who, meant, eq, means, ps).arrange(RIGHT, buff=0.38).move_to([0, 0.6, 0])
    return {"who": who, "meant": meant, "eq": eq, "means": means, "pass": ps}


def L20():
    """B20's last frame (the end card follows)."""
    return {"ct": ctag("planned", "vision"),
            "checks": VGroup(*[will_pill(x, 2.2, f"check {i + 1} · pass") for i, x in enumerate((-4.1, 0.0, 4.1))]),
            **trust_row(),
            "feat": VGroup(*[pill(x, -1.0, f) for f, x in zip(("support-reply bot", "document summariser", "search answer"), (-4.1, 0.0, 4.1))]),
            "any": T("the goal: any AI feature", H3, bold=True).move_to([0, -1.8, 0]),
            "vis": T("Readback is module 1 of a copilot for what PMs write for AI", BODY).move_to([0, -2.75, 0])}


class B20_Close(Scene):
    def construct(self):
        head, lines, rows = scorecard(expanded=True)
        tg, b = ctag(*TAG_EV), L20()
        old = VGroup(head, lines, rows, scorecard_note(), failed_line())
        self.add(tg, old)
        P(self, FadeOut(old), Transform(tg, b["ct"]), rt=0.45)
        on(self, "pass")
        P(self, LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in b["checks"]], lag_ratio=0.2), rt=0.6)
        on(self, "trust")
        P(self, FadeIn(b["who"], shift=RIGHT * 0.1), FadeIn(b["meant"], shift=RIGHT * 0.1), rt=0.5)
        on(self, "meant")
        P(self, FadeIn(b["eq"]), FadeIn(b["means"], shift=LEFT * 0.1), FadeIn(b["pass"], scale=0.8), rt=0.5)
        on(self, "goal")
        P(self, LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in b["feat"]], lag_ratio=0.2), rt=0.6)
        on(self, "feature")
        P(self, FadeIn(b["any"], shift=UP * 0.1), rt=0.4)
        on(self, "module")
        P(self, FadeIn(b["vis"], shift=UP * 0.1), rt=0.5)
        vb = band(-6.4, 6.4, -3.2, -2.3)
        self.add(vb)
        on(self, "copilot")
        P(self, *flash(vb, color=KRAFT_LT), rt=0.5)
        on(self, "AI", 2)                                        # "…write for AI": clear of Gate V's 85 % sample
        P(self, *flash(*[f[0] for f in b["feat"]]), rt=0.5)
        finish(self)
