"""scenes.py — Manim beats for "Same Odds, Smaller Numbers" (max-subtraction in softmax).

Beats: B00_ColdOpen, B02_Rule, B03_DirectRoute, B04_ShiftedRoute, B05_Cancel, B06_Predict, B07_Overflow,
B08_Underflow, BVDT_Takeaways, BHTF_YourTurn. (BTTL, B01, BOUT are toolkit Remotion components.)

Evidence rule: every number on screen is parsed from evidence/ files (verify_numbers_output.txt,
exp_sweep_output.txt, b00_claude_reply.txt) or the input list in verify_numbers.py. Nothing numeric
is hard-coded here. Live counters only show values that are true at that frame (x beside exp(x),
with exp computed from the displayed x); sweeps step through recorded lines, never interpolate.

Motion language: nothing pops in; eased moves of ~0.4–0.6 s; the score chips travel B02 → B03 → B04;
T = 1 stays pinned top-left from B02 to B08; ONE terracotta accent per beat, on a shape, at the moment
the narration points at it (word clock). Page #FAF9F5, ink #3D3929, soft #73705F, accent #D97757.

Timing: reveals are keyed to narration phrases through mp3/words.json (runtime/scripts/align.py).
Each scene lasts exactly its beat's audio (mp3/timings.json), so compile.py never retimes it.
"""
import json
import math
import re
from pathlib import Path

from manim import *

HERE = Path(__file__).resolve().parent

# ── palette / type ─────────────────────────────────────────────────────────────
BG = ManimColor("#FAF9F5")
INK = ManimColor("#3D3929")
SOFT = ManimColor("#73705F")
GHOST = ManimColor("#A9A491")
ACC = ManimColor("#D97757")
CARD = ManimColor("#FFFFFF")
BORDER = ManimColor("#E5E2D9")
SEG_OPACITY = [0.95, 0.62, 0.34]          # the three outcomes, same shading in every stacked bar
SERIF = "EB Garamond"
MONO = "Menlo"
SANS = "SF Pro Text"
config.background_color = BG

# ── evidence ───────────────────────────────────────────────────────────────────
EV_FILE = HERE / "evidence" / "verify_numbers_output.txt"
SWEEP_FILE = HERE / "evidence" / "exp_sweep_output.txt"
B00_FILE = HERE / "evidence" / "b00_claude_reply.txt"


def _floats(s):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", s)]


def load_evidence():
    """Parse the recorded runs. In the QC gates' temp copy (no evidence folder) return None;
    in the reel folder a missing or unparsable file is a hard error."""
    if not EV_FILE.exists():
        if (HERE / "beat_sheet.json").exists():
            raise RuntimeError(f"missing {EV_FILE}")
        return None
    t = EV_FILE.read_text()

    def line(tag):
        m = re.search(r"^" + re.escape(tag) + r"\s+(.*)$", t, re.M)
        if not m:
            raise RuntimeError(f"evidence line not found: {tag!r}")
        return m.group(1)

    ev = {}
    ev["run_date"] = re.search(r"^run date: (\d{4}-\d{2}-\d{2})", t, re.M).group(1)
    ev["python"] = re.search(r"^python: ([\d.]+)", t, re.M).group(1)
    w = line("B03 direct weights")
    ev["direct_w"], ev["direct_sum"] = _floats(w.split("sum")[0]), _floats(w.split("sum")[1])[0]
    ev["probs"] = _floats(line("B03 direct probabilities"))
    ev["shifted"] = [int(x) for x in _floats(line("B04 shifted scores"))]
    w = line("B04 shifted weights")
    ev["shifted_w"], ev["shifted_sum"] = _floats(w.split("sum")[0]), _floats(w.split("sum")[1])[0]
    ev["shifted_probs"] = _floats(line("B04 shifted probabilities"))
    ev["bit_identical"] = line("B04 bit-identical?").strip()
    ev["max_diff"] = _floats(line("B04 largest difference"))[0]
    ev["overflow_msg"] = line("B07 math.exp(1000)").strip()
    ev["p1000"] = line("B07 probabilities([1000, 1000])").strip()
    ev["float_max"] = _floats(line("B07 largest float"))[0]
    ev["exp_m1000"] = line("B08 math.exp(-1000)").strip()
    ev["p_underflow"] = line("B08 probabilities([0, -1000])").strip()
    ev["float_min"] = _floats(line("B08 smallest positive float"))[0]
    ev["true_exp10"] = _floats(line("B08 true size of exp(-1000) = 10 **"))[0]
    src = (HERE / "verify_numbers.py").read_text()
    ev["scores"] = [int(x) for x in _floats(re.search(r"^z = (\[.*\])", src, re.M).group(1))]
    ev["max_score"] = max(ev["scores"])
    assert [s - ev["max_score"] for s in ev["scores"]] == ev["shifted"], "scores/shifted mismatch"
    assert ev["probs"] == ev["shifted_probs"], "printed probabilities differ at 10 places"
    head = B00_FILE.read_text()
    ev["b00_model"] = re.search(r"^# model: ([^(\n]+)", head, re.M).group(1).strip()
    ev["b00_date"] = re.search(r"^# date: (\S+)", head, re.M).group(1)
    ev["b00_text"] = head
    s = SWEEP_FILE.read_text()
    ev["sweep_date"] = re.search(r"^run date: (\d{4}-\d{2}-\d{2})", s, re.M).group(1)
    ev["sweep_python"] = re.search(r"^python: ([\d.]+)", s, re.M).group(1)
    ev["up"] = [(int(a), b.strip()) for a, b in re.findall(r"^UP (\d+) (.+)$", s, re.M)]
    ev["down"] = [(int(a), b.strip()) for a, b in re.findall(r"^DOWN (\d+) (.+)$", s, re.M)]
    assert ev["up"] and ev["down"], "sweep lines missing"
    return ev


EV = load_evidence()
if EV is None:   # QC-gate temp copy only: shapes need numbers, these are never rendered
    EV = {"run_date": "-", "python": "-", "direct_w": [1.0, 2.0, 3.0], "direct_sum": 6.0, "probs": [0.2, 0.3, 0.5],
          "shifted": [-2, -1, 0], "shifted_w": [0.2, 0.3, 0.5], "shifted_sum": 1.0, "shifted_probs": [0.2, 0.3, 0.5],
          "bit_identical": "-", "max_diff": 1.0, "overflow_msg": "-", "p1000": "-", "float_max": 1e308,
          "exp_m1000": "-", "p_underflow": "[1.0, 0.0]", "float_min": 1e-300, "true_exp10": -400.0,
          "scores": [1, 2, 3], "max_score": 3, "b00_model": "-", "b00_date": "-", "b00_text": "",
          "sweep_date": "-", "sweep_python": "-", "up": [(0, "1.0"), (10, "OverflowError: x")],
          "down": [(0, "1.0"), (10, "0.0")]}

RUN_LABEL = f"recorded output · Python {EV['python']} · {EV['run_date']}"
SWEEP_LABEL = f"recorded sweep (exp_sweep.py) · Python {EV['sweep_python']} · {EV['sweep_date']}"
_SUP = str.maketrans("0123456789-−.", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁻·")


def sci(x, digits=1):
    """1.7976931348623157e+308 → '1.8 × 10³⁰⁸' (display rounding of a recorded value).
    String-based: 10 ** -324 would itself underflow to 0.0."""
    mant, exp = f"{x:.{digits}e}".split("e")
    return f"{mant} × 10{str(int(exp)).translate(_SUP)}"


def minus(s):
    return str(s).replace("-", "−")


# ── cue clock ──────────────────────────────────────────────────────────────────
def _norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("-", " ").replace("—", " ")).split()


class Cues:
    """Beat-local seconds for narration phrases (words.json when built, else word-position estimate)."""

    def __init__(self, beat_id, fallback_duration):
        self.duration = fallback_duration
        self.words = None
        self.narration = None
        self.beat = {}
        sheet = HERE / "beat_sheet.json"
        if sheet.exists():
            for b in json.loads(sheet.read_text())["beats"]:
                if b["beat_id"] == beat_id:
                    self.beat = b
                    self.narration = _norm(b["narration_text"])
                    self.duration = b.get("actual_duration_s") or b.get("estimated_duration_s") or self.duration
        timings = HERE / "mp3" / "timings.json"
        if timings.exists():
            self.duration = json.loads(timings.read_text()).get(beat_id, self.duration)
        words = HERE / "mp3" / "words.json"
        if words.exists():
            data = json.loads(words.read_text())
            fps = data.get("fps", 24)
            rows = data.get("beats", {}).get(beat_id)
            if rows:
                self.words = [(w, r["startFrame"] / fps) for r in rows for w in _norm(r["text"])]

    @staticmethod
    def _find(seq, phrase):
        n = len(phrase)
        for i in range(len(seq) - n + 1):
            if seq[i:i + n] == phrase:
                return i
        return None

    def index(self, phrase):
        seq = [w for w, _ in self.words] if self.words else (self.narration or [])
        return self._find(seq, _norm(phrase))

    def time_at_index(self, i, fallback):
        if self.words and i is not None and i < len(self.words):
            return self.words[i][1]
        if self.narration and i is not None:
            return self.duration * i / len(self.narration)
        return fallback

    def time(self, phrase, fallback_fraction):
        return self.time_at_index(self.index(phrase), self.duration * fallback_fraction)


class Timeline:
    """Paces one scene against its narration. The clock is the renderer's real elapsed time (so
    frame rounding never drifts it); the QC stub has no renderer, so it falls back to a sum.
    (Scene classes subclass Scene directly: run.sh finds them with `class B.._Name(Scene)`.)"""

    def __init__(self, scene, beat_id, fallback_duration):
        self.scene = scene
        scene.camera.background_color = BG
        self.cues = Cues(beat_id, fallback_duration)
        self._sum = 0.0

    @property
    def clock(self):
        t = getattr(getattr(self.scene, "renderer", None), "time", None)
        return float(t) if isinstance(t, (int, float)) else self._sum

    def until(self, phrase, fraction, lead=0.15):
        self.until_t(self.cues.time(phrase, fraction) - lead)

    def until_t(self, target):
        gap = target - self.clock
        if gap > 1 / 24:
            self.scene.wait(gap)
            self._sum += gap

    def run(self, *anims, run_time=0.5, **kw):
        self.scene.play(*anims, run_time=run_time, **kw)
        self._sum += run_time

    def frame(self):
        self.scene.wait(1 / 24)
        self._sum += 1 / 24

    def hold_to_end(self):
        self.scene.wait(max(self.cues.duration - self.clock, 1 / 24))


# ── text & shape helpers (type set 4× large and scaled down: Pango spaces small glyphs unevenly) ──
_OVERSET = 4


def serif(s, size=40, color=INK, weight="NORMAL"):
    return Text(s, font=SERIF, font_size=size * _OVERSET, color=color, weight=weight).scale(1 / _OVERSET)


def mono(s, size=34, color=INK, weight="NORMAL"):
    """Monospace; one glyph per character (spaces included) so glyph ranges match string ranges."""
    return Text(s, font=MONO, font_size=size * _OVERSET, color=color, weight=weight,
                disable_ligatures=True).scale(1 / _OVERSET)


def sans(s, size=30, color=INK, weight="NORMAL"):
    return Text(s, font=SANS, font_size=size * _OVERSET, color=color, weight=weight,
                disable_ligatures=True).scale(1 / _OVERSET)


def fit(m, max_w):
    if m.width > max_w:
        m.scale_to_fit_width(max_w)
    return m


def chip(n, size=40):
    label = mono(minus(n), size)
    box = RoundedRectangle(corner_radius=0.12, width=max(0.85, label.width + 0.35), height=0.78,
                           stroke_color=INK, stroke_width=2, fill_color=CARD, fill_opacity=1)
    return VGroup(box, label.move_to(box))


def t_tag():
    """T = 1, pinned top-left from B02 to B08."""
    return serif("T = 1", 28, SOFT).move_to([-6.15, 3.2, 0], aligned_edge=LEFT)


def underline(g, color=ACC, width=6, gap=0.08):
    return Line(g.get_corner(DL) + DOWN * gap, g.get_corner(DR) + DOWN * gap, color=color, stroke_width=width)


def stack(widths, x0, y, h=0.5):
    """A stacked bar: one rectangle per outcome, left to right, shaded by outcome."""
    rects, x = VGroup(), x0
    for w, op in zip(widths, SEG_OPACITY):
        r = Rectangle(width=max(w, 1e-3), height=h, stroke_width=0, fill_color=INK, fill_opacity=op)   # no separator: widths stay exact
        r.move_to([x, y, 0], aligned_edge=LEFT)
        rects.add(r)
        x += w
    return rects


def reveal_typing(t, texts, seconds):
    """Type a VGroup of Text lines (one glyph per char) at a uniform rate: glyphs go from hidden
    to shown in order, one render frame at a time."""
    glyphs = [g for line in texts for g in line]
    for g in glyphs:
        g.set_opacity(0)
    n = max(1, int(seconds * 24))
    for f in range(1, n + 1):
        k = round(len(glyphs) * f / n)
        for g in glyphs[:k]:
            g.set_opacity(1)
        t.frame()


def math_svg(beat_id, index):
    """A typeset-math row (matplotlib mathtext SVG from fill_math.py) at its natural size,
    or a Text stand-in in the QC temp copy."""
    sheet = HERE / "beat_sheet.json"
    if sheet.exists():
        import base64
        b = next(x for x in json.loads(sheet.read_text())["beats"] if x["beat_id"] == beat_id)
        row = b["shot"]["math_rows"][index]
        path = HERE / "media" / f"_math_{beat_id}_{index}.svg"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(base64.b64decode(row["src"].split(",", 1)[1]))
        return SVGMobject(str(path), height=None).set_color(INK)   # natural size: pieces keep relative scale
    return serif("formula", 60)


def svg_row(expression_index, beat_id, height):
    return math_svg(beat_id, expression_index).scale_to_fit_height(height)


# ─────────────────────────────────────────────────────────────────────────────
#  B00 — cold open: the real Claude Code exchange (rebuilt so the reply can type in, carry its date,
#  and flag the one claim the video checks later). Words are verbatim from evidence/b00_claude_reply.txt.
# ─────────────────────────────────────────────────────────────────────────────
B00_PROMPT_LINES = [
    "Run lessons/01-randomness-and-first-prompts/code/main.py and show me what",
    "probabilities([1, 2, 3]) returns. Then compute the same distribution without subtracting",
    "the max, and print both sets of intermediate weights side by side.",
]


class B00_ColdOpen(Scene):
    BEAT, EST = "B00", 15.6

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        beat = t.cues.beat
        reply = beat.get("reply_lines") or ["(stub)", "(stub)", "(stub) identical to 15 decimal places"]   # QC stub only
        if EV["b00_text"]:
            for line in reply:
                assert line in EV["b00_text"], f"reply line not verbatim: {line!r}"
            assert " ".join(B00_PROMPT_LINES) == beat.get("prompt_text"), "prompt must match beat_sheet"
        topic = sans("INFO 7375 · SOFTMAX", 20, SOFT, weight="BOLD").move_to([-6.15, 3.15, 0], aligned_edge=LEFT)
        segment = serif("Same Odds, Smaller Numbers", 30, weight="BOLD").move_to([-6.15, 2.72, 0], aligned_edge=LEFT)
        greet = serif("Hello, Aravind", 48).move_to([0, 1.8, 0])
        card = RoundedRectangle(corner_radius=0.22, width=12.5, height=2.35, stroke_color=BORDER, stroke_width=2,
                                fill_color=CARD, fill_opacity=1).move_to([0, 0.25, 0])
        prompt = VGroup(*[sans(s, 27) for s in B00_PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        fit(prompt, card.width - 0.9).move_to(card.get_center() + UP * 0.28).align_to(card, LEFT).shift(RIGHT * 0.45)
        plus = Circle(radius=0.15, color=BORDER, stroke_width=2).move_to(card.get_corner(DL) + RIGHT * 0.5 + UP * 0.33)
        plus_t = sans("+", 20, SOFT).move_to(plus)
        model = sans(EV["b00_model"], 22, INK).move_to(card.get_corner(DR) + LEFT * 1.7 + UP * 0.33)
        send = RoundedRectangle(corner_radius=0.1, width=0.4, height=0.4, stroke_width=0, fill_color=GHOST,
                                fill_opacity=1).move_to(card.get_corner(DR) + LEFT * 0.5 + UP * 0.33)
        folder = sans("Aravind Ravi", 22, SOFT).next_to(card, DOWN, buff=0.22).align_to(card, LEFT).shift(RIGHT * 0.2)
        running = mono("running main.py…", 19, SOFT).next_to(folder, DOWN, buff=0.2).align_to(folder, LEFT)
        lines = VGroup(*[mono(s, 19) for s in reply]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fit(lines, 12.3).next_to(running, DOWN, buff=0.14).align_to(folder, LEFT)
        stamp = serif(f"Claude Code · {EV['b00_model']} · {EV['b00_date']}", 22, SOFT)
        stamp.next_to(lines, DOWN, buff=0.2).align_to(folder, LEFT)
        for g in prompt:
            g.set_opacity(0)
        for g in lines:
            g.set_opacity(0)
        self.add(topic, segment, greet, card, plus, plus_t, model, send, folder, prompt, lines)

        t.until_t(0.3)
        reveal_typing(t, prompt, 2.2)
        t.until("I asked Claude Code", 0.35)
        t.run(FadeIn(running, shift=UP * 0.08), run_time=0.4)
        t.until("Its answer", 0.5)
        reveal_typing(t, lines, 2.4)
        t.until("identical to fifteen decimal places", 0.7)
        phrase, last = "identical to 15 decimal places", reply[-1]
        tag = sans("claim — checked later", 20, SOFT).next_to(lines[-1], RIGHT, buff=0.35)
        if phrase in last:                                   # (absent only in the QC stub's placeholder)
            a = last.index(phrase)
            claim = lines[-1][a:a + len(phrase)]
            t.run(Create(underline(claim, width=5, gap=0.06)), FadeIn(tag, shift=LEFT * 0.1), run_time=0.5)
        t.until("Let's see why", 0.85)
        t.run(FadeIn(stamp), run_time=0.4)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B02 — the rule: formula (largest), the score chips drop into the z_i slot one at a time, T = 1 pins.
# ─────────────────────────────────────────────────────────────────────────────
CHIP_ROW_Y = -1.15
CHIP_XS = [-1.1, 0.0, 1.1]
ZI_GLYPHS = slice(8, 10)          # 'z' and subscript 'i' in the numerator of the typeset formula


def b02_layout():
    title = serif("Scores to probabilities", 40).move_to([0, 3.0, 0])
    formula = svg_row(0, "B02", 2.3).move_to([0, 1.15, 0])
    label = serif("scores  z =", 36).move_to([-3.1, CHIP_ROW_Y, 0])
    chips = VGroup(*[chip(s).move_to([x, CHIP_ROW_Y, 0]) for s, x in zip(EV["scores"], CHIP_XS)])
    note = serif("Constructed input: scores chosen by hand, not produced by a model.", 30).move_to([0, -2.38, 0])
    cond = serif("T > 0 in general; held at T = 1 for this whole video.", 26, SOFT).move_to([0, -3.02, 0])
    return dict(title=title, formula=formula, label=label, chips=chips, note=note, cond=cond, tag=t_tag())


class B02_Rule(Scene):
    BEAT, EST = "B02", 16.4

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        L = b02_layout()
        self.add(L["title"], L["formula"])              # opens on content, never a blank frame
        slot_src = L["formula"][ZI_GLYPHS] if len(L["formula"]) > 9 else L["formula"]
        slot = SurroundingRectangle(slot_src, color=ACC, buff=0.07, stroke_width=4, corner_radius=0.05)
        # a soft pointer follows the words: "raise e to each score" (numerator), "divide by the total" (denominator)
        if len(L["formula"]) > 23:
            numer, denom = L["formula"][4:13], L["formula"][13:24]
            ptr = SurroundingRectangle(numer, color=SOFT, buff=0.1, stroke_width=3, corner_radius=0.08)
            t.until("Raise e to each score", 0.1)
            t.run(Create(ptr), run_time=0.45)
            t.until("divide by the total", 0.2)
            t.run(ptr.animate.become(SurroundingRectangle(denom, color=SOFT, buff=0.1, stroke_width=3, corner_radius=0.08)),
                  run_time=0.5)
            t.until("they all sum to one", 0.35)
            t.run(FadeOut(ptr), run_time=0.35)
        t.until("one, two, and three", 0.4)
        t.run(FadeIn(L["label"], shift=UP * 0.12), Create(slot), run_time=0.45)
        idx = t.cues.index("one, two, and three")
        for off, c in zip([0, 1, 3], L["chips"]):        # "one", "two", "and three"
            t.until_t(t.cues.time_at_index(None if idx is None else idx + off, t.clock) - 0.12)
            dropped = c.copy().scale_to_fit_height(slot.height * 0.95).move_to(slot)
            self.add(dropped)
            t.run(FadeIn(dropped, shift=DOWN * 0.25), run_time=0.3)
            t.run(ReplacementTransform(dropped, c), run_time=0.45)
        t.run(FadeOut(slot), run_time=0.3)
        t.until("I picked those by hand", 0.6)
        t.run(FadeIn(L["note"], shift=UP * 0.1), run_time=0.45)
        t.until("Temperature stays at one", 0.8)
        temp = serif("T = 1", 36).move_to([3.3, CHIP_ROW_Y, 0])
        t.run(FadeIn(temp, shift=LEFT * 0.15), FadeIn(L["cond"]), run_time=0.45)
        t.until("only one thing moves", 0.92)
        t.run(ReplacementTransform(temp, L["tag"]), run_time=0.6)   # pinned for the rest of the video
        t.hold_to_end()


# ── B03 / B04 shared layout ─────────────────────────────────────────────────────
ROW_Y = [1.75, 1.08, 0.41]
HEAD_Y = 2.85
COL_CHIP = 0.72
LEFT_CX = -3.45
RAW_W = 5.6                                   # width for the direct weights' total (30.193); every raw stack shares it
UNIT_W = 4.4                                  # display width that stands for total probability 1
B3_X0, B3_RAW_Y, B3_UNIT_Y = 0.6, 0.95, -1.1


def raw_widths(weights):
    return [RAW_W * w / EV["direct_sum"] for w in weights]


def unit_widths():
    return [UNIT_W * p for p in EV["probs"]]


def seg_labels(bar, texts, y_offsets, size=24):
    """Labels under (negative offset) or over (positive) each segment, with a short leader."""
    out = VGroup()
    for r, s, dy in zip(bar, texts, y_offsets):
        lab = mono(s, size).move_to([r.get_center()[0], r.get_center()[1] + dy, 0])
        edge = r.get_bottom() if dy < 0 else r.get_top()
        tip = lab.get_top() if dy < 0 else lab.get_bottom()
        lead = Line(edge, [edge[0], tip[1] + (0.05 if dy < 0 else -0.05), 0], color=SOFT, stroke_width=1.5)
        out.add(VGroup(lead, lab))
    return out


class Column:
    """B03's left column: score chips → weights → sum."""

    def __init__(self):
        cx = LEFT_CX
        self.header = serif("direct:  exp(z)", 40, weight="BOLD").move_to([cx, HEAD_Y, 0])
        self.col_labels = VGroup(serif("score", 30, SOFT).move_to([cx - 1.9, 2.4, 0]),
                                 serif("weight", 30, SOFT).move_to([cx + 1.1, 2.4, 0]))
        self.scores = VGroup(*[chip(s, 34).scale(COL_CHIP).move_to([cx - 1.9, y, 0]) for s, y in zip(EV["scores"], ROW_Y)])
        self.arrows = VGroup(*[Arrow([cx - 1.3, y, 0], [cx - 0.15, y, 0], buff=0, color=SOFT, stroke_width=3,
                                     max_tip_length_to_length_ratio=0.2) for y in ROW_Y])
        self.weights = VGroup(*[mono(f"{w:.3f}", 40).move_to([cx + 1.1, y, 0]) for w, y in zip(EV["direct_w"], ROW_Y)])
        self.sum_text = mono(f"sum  {EV['direct_sum']:.3f}", 36)
        self.sum_box = SurroundingRectangle(self.sum_text, color=INK, buff=0.18, corner_radius=0.08, stroke_width=2)
        VGroup(self.sum_text, self.sum_box).move_to([cx, -0.45, 0])

    def all(self):
        return VGroup(self.header, self.col_labels, self.scores, self.arrows, self.weights, self.sum_box, self.sum_text)


def b03_right():
    raw = stack(raw_widths(EV["direct_w"]), B3_X0, B3_RAW_Y)
    raw_cap = serif("weights, drawn to scale", 30, SOFT).move_to([B3_X0, B3_RAW_Y + 1.42, 0], aligned_edge=LEFT)
    raw_lab = seg_labels(raw, [f"{w:.3f}" for w in EV["direct_w"]], [0.95, 0.55, 0.55])
    unit = stack(unit_widths(), B3_X0, B3_UNIT_Y)
    unit_cap = serif(f"÷ {EV['direct_sum']:.3f}  →  probabilities, total 1", 30, SOFT) \
        .move_to([B3_X0, B3_UNIT_Y + 0.62, 0], aligned_edge=LEFT)
    unit_lab = seg_labels(unit, [f"{p:.4f}" for p in EV["probs"]], [-0.62, -1.08, -0.62])
    return dict(raw=raw, raw_cap=raw_cap, raw_lab=raw_lab, unit=unit, unit_cap=unit_cap, unit_lab=unit_lab)


# ─────────────────────────────────────────────────────────────────────────────
#  B03 — the direct route. Opens on B02's last frame; chips travel into the column; the weights
#  become a stacked bar at their true relative widths; normalising squashes it to unit width.
# ─────────────────────────────────────────────────────────────────────────────
class B03_DirectRoute(Scene):
    BEAT, EST = "B03", 17.0

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        L = b02_layout()
        self.add(*[v for k, v in L.items()])               # B02's last frame (T = 1 already pinned)
        col, R = Column(), b03_right()
        t.run(FadeOut(VGroup(L["title"], L["formula"], L["label"], L["note"], L["cond"])),
              *[L["chips"][i].animate.move_to(col.scores[i]).scale(COL_CHIP) for i in range(3)],
              FadeIn(col.header), FadeIn(col.col_labels), run_time=0.6)

        # true climb: each arrow shows x, the cell shows exp(x) of that same displayed x
        t.until("two point seven", 0.2)
        trackers = [ValueTracker(0.0) for _ in EV["scores"]]
        cells = VGroup(*[always_redraw(lambda tr=tr, y=y: mono(f"{math.exp(round(tr.get_value(), 2)):.3f}", 40)
                                       .move_to([LEFT_CX + 1.1, y, 0])) for tr, y in zip(trackers, ROW_Y)])
        xs = VGroup(*[always_redraw(lambda tr=tr, y=y: mono(f"x = {tr.get_value():.2f}", 24, SOFT)
                                    .move_to([LEFT_CX - 0.72, y + 0.27, 0])) for tr, y in zip(trackers, ROW_Y)])
        t.run(*[GrowArrow(a) for a in col.arrows], FadeIn(cells), FadeIn(xs), run_time=0.4)
        t.run(*[tr.animate.set_value(s) for tr, s in zip(trackers, EV["scores"])], run_time=2.0)
        self.remove(cells, xs)
        self.add(col.weights)                              # the recorded values (equal to the settled counters)

        # the three weights become one stacked bar, drawn to scale
        t.until("thirty point one nine", 0.45)
        t.run(FadeIn(col.sum_text), Create(col.sum_box), FadeIn(R["raw_cap"]), run_time=0.45)
        for w_txt, seg, lab in zip(col.weights, R["raw"], R["raw_lab"]):
            flying = w_txt.copy()
            t.run(GrowFromEdge(seg, LEFT), ReplacementTransform(flying, lab[1]), Create(lab[0]), run_time=0.4)

        # normalising: divide by the sum = squash the whole stack to unit width
        t.until("divide each", 0.55)
        squash = R["raw"].copy()
        t.run(FadeIn(R["unit_cap"]), squash.animate.stretch_to_fit_width(UNIT_W).move_to(R["unit"], aligned_edge=LEFT),
              run_time=0.8)
        self.remove(squash)
        self.add(R["unit"])
        t.run(LaggedStart(*[FadeIn(g, shift=DOWN * 0.08) for g in R["unit_lab"]], lag_ratio=0.35), run_time=0.9)

        t.until("two thirds", 0.9)
        t.run(R["unit"][2].animate.set_fill(ACC, opacity=1), run_time=0.45)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B04 — the core idea. Scores on a number line: the whole line slides left by the max, the gaps stay 1
#  and 1. The shifted weights make a tiny stack (same scale); it stretches to unit width and lands exactly
#  on B03's unit bar. Footnote pays off B00's "15 decimal places".
# ─────────────────────────────────────────────────────────────────────────────
NL_Y, NL_K, NL_X0 = 2.0, 1.25, -0.6            # number line: x = NL_X0 + NL_K * value
B4_X0, B4_RAW_Y, B4_SHIFT_Y, B4_UNIT_Y = -5.9, 0.55, -0.45, -1.55


def nx(v):
    return NL_X0 + NL_K * v


class B04_ShiftedRoute(Scene):
    BEAT, EST = "B04", 19.5

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        col, R = Column(), b03_right()
        tag = t_tag()
        R["unit"][2].set_fill(ACC, opacity=1)
        self.add(tag, col.all(), *R.values())               # B03's last frame

        # the number line, with the B03 chips travelling onto it
        vals = list(range(-3, 5))
        axis = Line([nx(-3.3), NL_Y, 0], [nx(4.3), NL_Y, 0], color=SOFT, stroke_width=2)
        ticks = VGroup(*[Line([nx(v), NL_Y - 0.08, 0], [nx(v), NL_Y + 0.08, 0], color=SOFT, stroke_width=2) for v in vals])
        tick_lab = VGroup(*[serif(minus(v), 22, SOFT).move_to([nx(v), NL_Y - 0.3, 0]) for v in vals])
        chips = VGroup(*[chip(s, 34).scale(COL_CHIP).move_to([nx(s), NL_Y + 0.55, 0]) for s in EV["scores"]])
        gaps = [b - a for a, b in zip(EV["scores"], EV["scores"][1:])]
        brackets = VGroup()
        for (a, b), g in zip(zip(EV["scores"], EV["scores"][1:]), gaps):
            y = NL_Y - 0.62
            br = VGroup(Line([nx(a) + 0.08, y + 0.12, 0], [nx(a) + 0.08, y, 0]),
                        Line([nx(a) + 0.08, y, 0], [nx(b) - 0.08, y, 0]),
                        Line([nx(b) - 0.08, y, 0], [nx(b) - 0.08, y + 0.12, 0])).set_stroke(INK, width=2)
            br.add(serif(f"gap {g}", 22).move_to([(nx(a) + nx(b)) / 2, y - 0.22, 0]))
            brackets.add(br)
        # direct raw stack + unit bar move to the lower-left; the column leaves
        new_raw = stack(raw_widths(EV["direct_w"]), B4_X0, B4_RAW_Y, h=0.42)
        new_unit = stack(unit_widths(), B4_X0, B4_UNIT_Y, h=0.42)
        new_unit[2].set_fill(ACC, opacity=1)
        raw_txt = serif(f"direct weights:  {'  +  '.join(f'{w:.3f}' for w in EV['direct_w'])}  =  {EV['direct_sum']:.3f}",
                        24)
        fit(raw_txt, 5.8).move_to([0.35, B4_RAW_Y, 0], aligned_edge=LEFT)
        unit_lab = seg_labels(new_unit, [f"{p:.4f}" for p in EV["probs"]], [-0.55, -0.98, -0.55])
        unit_txt = serif("probabilities, total 1", 24, SOFT).move_to([B4_X0 + UNIT_W + 0.35, B4_UNIT_Y, 0], aligned_edge=LEFT)
        scale_note = serif("bars drawn to scale", 22, SOFT).move_to([B4_X0, B4_RAW_Y + 0.5, 0], aligned_edge=LEFT)
        t.run(FadeOut(VGroup(col.header, col.col_labels, col.arrows, col.weights, col.sum_box, col.sum_text,
                             R["raw_cap"], R["raw_lab"], R["unit_cap"], R["unit_lab"])),
              *[col.scores[i].animate.move_to(chips[i]) for i in range(3)],
              Transform(R["raw"], new_raw), Transform(R["unit"], new_unit),
              Create(axis), FadeIn(ticks), FadeIn(tick_lab), run_time=0.7)
        self.remove(*col.scores)
        self.add(chips)
        t.run(FadeIn(brackets), FadeIn(raw_txt), FadeIn(unit_lab), FadeIn(unit_txt), FadeIn(scale_note),
              R["unit"][2].animate.set_fill(INK, opacity=SEG_OPACITY[2]), run_time=0.5)

        # subtract the max: the whole line slides; the gaps never change
        t.until("Subtract the biggest score", 0.12)
        shift_lab = serif(f"− {EV['max_score']}", 30, weight="BOLD").move_to([nx(2), NL_Y + 1.15, 0])
        arrow = Arrow([nx(3.2), NL_Y + 1.15, 0], [nx(0.4), NL_Y + 1.15, 0], buff=0, color=INK, stroke_width=3,
                      max_tip_length_to_length_ratio=0.1)
        t.run(FadeIn(shift_lab), GrowArrow(arrow), run_time=0.45)
        t.run(VGroup(chips, brackets).animate.shift(LEFT * NL_K * EV["max_score"]), run_time=1.0)
        t.run(FadeOut(shift_lab), FadeOut(arrow), run_time=0.3)

        t.until("minus two, minus one, zero", 0.25)
        new_chips = VGroup(*[chip(s, 34).scale(COL_CHIP).move_to(c) for s, c in zip(EV["shifted"], chips)])
        t.run(*[Transform(c, n) for c, n in zip(chips, new_chips)], run_time=0.5)

        # every weight changes: the shifted weights, at the same scale, make a tiny stack
        t.until("every weight changes", 0.4)
        shifted = stack(raw_widths(EV["shifted_w"]), B4_X0, B4_SHIFT_Y, h=0.42)
        shift_txt = serif(f"shifted weights:  {'  +  '.join(f'{w:.3f}' for w in EV['shifted_w'])}  =  {EV['shifted_sum']:.3f}",
                          24)
        fit(shift_txt, 5.8).move_to([0.35, B4_SHIFT_Y, 0], aligned_edge=LEFT)
        t.run(*[GrowFromEdge(r, LEFT) for r in shifted], FadeIn(shift_txt, shift=LEFT * 0.1), run_time=0.6)

        # divide anyway: stretch the tiny stack to unit width; it lands exactly on B03's unit bar
        t.until("same three values", 0.72)
        landing = shifted.copy()
        t.run(landing.animate.stretch_to_fit_width(UNIT_W).move_to(R["unit"], aligned_edge=LEFT), run_time=1.0)
        frame_ = SurroundingRectangle(R["unit"], color=ACC, buff=0.08, stroke_width=5)
        same = serif("same partition", 26, weight="BOLD").next_to(frame_, UP, buff=0.12).align_to(frame_, LEFT)
        t.run(Create(frame_), FadeIn(same), run_time=0.5)

        t.until("fifteen decimal places", 0.9)
        foot = serif(f"Claude said “identical to 15 decimal places”  ·  recorded run: largest difference "
                     f"{sci(EV['max_diff'])}, bit-identical: {EV['bit_identical']}", 21, SOFT)
        fit(foot, 12.2).move_to([0, -3.05, 0])
        t.run(FadeIn(foot, shift=UP * 0.08), run_time=0.45)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B05 — why it's allowed: the factored fraction is built from separate pieces, so the shared
#  factor exp(−m) can be boxed, struck out and removed; the fraction collapses to the original.
# ─────────────────────────────────────────────────────────────────────────────
class B05_Cancel(Scene):
    BEAT, EST = "B05", 17.2

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        tag = t_tag()
        title = serif("The shared factor cancels", 40).move_to([0, 3.0, 0])
        self.add(tag, title)                                   # opens on content
        row1 = svg_row(0, "B05", 1.35).move_to([0, 1.75, 0])
        A, Bm, Cm, D = math_svg("B05", 1), math_svg("B05", 2), math_svg("B05", 2), math_svg("B05", 3)
        k = 0.52 / A.height if A.height else 1
        for m in (A, Bm, Cm, D):
            m.scale(k)
        y_num, y_den, y_bar = -0.05, -1.15, -0.55
        num = VGroup(A, Bm).arrange(RIGHT, buff=0.18).move_to([0.35, y_num, 0])
        den = VGroup(Cm, D).arrange(RIGHT, buff=0.18).move_to([0.35, y_den, 0])
        half = min(max(num.width, den.width) / 2 + 0.1, 5.0)
        bar = Line([0.35 - half, y_bar, 0], [0.35 + half, y_bar, 0], color=INK, stroke_width=3)
        eq = serif("=", 60).next_to(bar, LEFT, buff=0.4)
        m_note = serif(f"m is the largest score (here m = {EV['max_score']})", 28, SOFT).move_to([0, -2.35, 0])

        t.until("Call the biggest score m", 0.1)
        t.run(FadeIn(row1, shift=DOWN * 0.1), FadeIn(m_note), run_time=0.5)
        t.until("splits every weight", 0.3)
        t.run(FadeIn(eq), Create(bar), run_time=0.4)
        t.run(LaggedStart(FadeIn(A, shift=DOWN * 0.1), FadeIn(Bm, shift=DOWN * 0.1),
                          FadeIn(D, shift=UP * 0.1), FadeIn(Cm, shift=UP * 0.1), lag_ratio=0.3), run_time=1.1)
        t.until("same factor", 0.45)
        boxes = VGroup(underline(Bm, width=7, gap=0.12), underline(Cm, width=7, gap=0.12))   # terracotta marks, not text
        t.run(Create(boxes), run_time=0.5)
        t.until("so it cancels", 0.6)
        strikes = VGroup(*[Line(m.get_corner(DL), m.get_corner(UR), color=INK, stroke_width=5) for m in (Bm, Cm)])   # ink over text (contrast)
        t.run(Create(strikes), run_time=0.45)
        t.until("back at the original formula", 0.72)
        t.run(FadeOut(VGroup(Bm, Cm, boxes, strikes)), run_time=0.4)
        new_w = min(max(A.width, D.width) + 0.2, 8.0)
        t.run(A.animate.move_to([0.35, y_num, 0]), D.animate.move_to([0.35, y_den, 0]),
              bar.animate.put_start_and_end_on([0.35 - new_w / 2, y_bar, 0], [0.35 + new_w / 2, y_bar, 0]),
              eq.animate.move_to([0.35 - new_w / 2 - 0.55, y_bar, 0]), run_time=0.6)
        t.until("can't change their ratios", 0.9)
        ratio = serif("The shift changes the weights. It can't change their ratios.", 30).move_to([0, -2.95, 0])
        t.run(FadeIn(ratio, shift=UP * 0.08), run_time=0.45)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B06 — predict card; the pause after "commit" gets a quiet 3-2-1 ring so the silence reads as deliberate.
# ─────────────────────────────────────────────────────────────────────────────
def b06_layout():
    spark = serif("Predict first.", 36, SOFT).move_to([0, 2.55, 0])
    q = VGroup(serif("Scores [1000, 1000]: what are the probabilities,", 52, weight="BOLD"),
               serif("and what does the direct route do?", 52, weight="BOLD")).arrange(DOWN, buff=0.3)
    fit(q, 12.0).move_to([0, 0.9, 0])
    rule = Line([-1.1, -0.55, 0], [1.1, -0.55, 0], color=ACC, stroke_width=6)
    commit = serif("Commit to both answers — the answer is next.", 32, SOFT).move_to([0, -1.25, 0])
    return dict(spark=spark, q=q, rule=rule, commit=commit, tag=t_tag())


class B06_Predict(Scene):
    BEAT, EST = "B06", 13.6

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        L = b06_layout()
        self.add(L["tag"], L["spark"], L["q"])              # the question is on screen from frame 0
        t.until("Commit to both answers", 0.8)
        t.run(Create(L["rule"]), FadeIn(L["commit"], shift=UP * 0.1), run_time=0.5)
        # the pause: a ring empties and counts 3-2-1 (the question itself never moves)
        start = t.clock + 0.3
        span = max(t.cues.duration - start - 0.15, 0.9)
        t.until_t(start)
        ring_bg = Circle(radius=0.42, color=BORDER, stroke_width=5).move_to([0, -2.45, 0])
        prog = ValueTracker(1.0)
        ring = always_redraw(lambda: Arc(radius=0.42, start_angle=PI / 2, angle=max(prog.get_value(), 1e-3) * TAU,
                                         color=SOFT, stroke_width=5).move_to([0, -2.45, 0]))
        count = always_redraw(lambda: serif(str(max(1, math.ceil(prog.get_value() * 3))), 32, SOFT).move_to([0, -2.45, 0]))
        t.run(FadeIn(ring_bg), FadeIn(ring), FadeIn(count), run_time=0.15)
        t.run(prog.animate.set_value(0.0), run_time=span, rate_func=linear)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B07 — [1000, 1000]. Right: the shifted route's three steps. Left: the recorded sweep of math.exp
#  climbing a log axis to the largest float; at x = 710 it stops with the recorded OverflowError.
# ─────────────────────────────────────────────────────────────────────────────
LOG_X, UP_Y0, UP_Y1, UP_TOP = -5.3, -0.9, 1.45, 310.0      # axis: log10(value) 0..310 → y UP_Y0..UP_Y1


def up_y(log10v):
    return UP_Y0 + (UP_Y1 - UP_Y0) * log10v / UP_TOP


class B07_Overflow(Scene):
    BEAT, EST = "B07", 19.2

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        L = b06_layout()
        self.add(*L.values())                                 # B06's last frame
        title = serif("scores  [1000, 1000]", 44, weight="BOLD").move_to([0, 3.0, 0])
        lx, rx = -3.35, 3.55
        l_head = serif("direct route", 32, SOFT).move_to([lx, 2.3, 0])
        r_head = serif("shifted route", 32, SOFT).move_to([rx, 2.3, 0])
        divider = DashedLine([0, 2.55, 0], [0, -3.1, 0], color=SOFT, stroke_width=2, dash_length=0.1)
        t.run(ReplacementTransform(L["q"], title), FadeOut(VGroup(L["spark"], L["rule"], L["commit"])), run_time=0.6)
        t.run(FadeIn(l_head), FadeIn(r_head), Create(divider), run_time=0.4)

        vx = rx + 0.4
        start = mono("[1000, 1000]", 36).move_to([vx, 1.5, 0])
        t.run(FadeIn(start), run_time=0.3)
        # direct route: the log axis is set up now; the recorded sweep runs on its cue
        axis = Arrow([LOG_X, UP_Y0 - 0.1, 0], [LOG_X, UP_Y1 + 0.35, 0], buff=0, color=SOFT, stroke_width=3,
                     max_tip_length_to_length_ratio=0.05)
        ticks = VGroup()
        for p in (0, 100, 200):
            y = up_y(p)
            ticks.add(Line([LOG_X - 0.07, y, 0], [LOG_X + 0.07, y, 0], color=SOFT, stroke_width=2),
                      serif(f"10{str(p).translate(_SUP)}", 24, SOFT).move_to([LOG_X - 0.18, y, 0], aligned_edge=RIGHT))
        ceil_y = up_y(math.log10(EV["float_max"]))
        ceiling = Line([LOG_X - 0.25, ceil_y, 0], [-0.4, ceil_y, 0], color=INK, stroke_width=3)
        ceil_label = serif(f"largest float ≈ {sci(EV['float_max'])}", 24).move_to([-4.95, ceil_y + 0.28, 0], aligned_edge=LEFT)
        axis_lab = serif("log scale", 28, SOFT).move_to([LOG_X + 0.15, UP_Y0 - 0.3, 0], aligned_edge=LEFT)
        t.run(Create(axis), FadeIn(ticks), Create(ceiling), FadeIn(ceil_label), FadeIn(axis_lab), run_time=0.5)
        steps = [("− 1000", "[0, 0]", "subtract a thousand", 0.15), ("exp", "[1, 1]", "e to the zero", 0.25),
                 ("÷ 2", EV["p1000"], "one over two", 0.32)]
        prev_y = 1.5
        for op, val, cue, frac in steps:
            t.until(cue, frac)
            y = prev_y - 1.0
            arr = Arrow([vx, prev_y - 0.28, 0], [vx, y + 0.28, 0], buff=0, color=SOFT, stroke_width=3,
                        max_tip_length_to_length_ratio=0.3)
            op_t = serif(op, 30, SOFT).next_to(arr, LEFT, buff=0.25)
            val_t = mono(val, 36, weight="BOLD" if val == EV["p1000"] else "NORMAL").move_to([vx, y, 0])
            t.run(GrowArrow(arr), FadeIn(op_t), FadeIn(val_t), run_time=0.45)
            prev_y = y

        t.until("never arrives", 0.45)
        dot = Dot([LOG_X, up_y(0), 0], radius=0.09, color=INK)
        ctr_x, ctr_y = -4.95, 0.35
        counter = VGroup(mono("x = 0", 24), mono("exp(x) =", 24, SOFT), mono("1.0", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.08) \
            .move_to([ctr_x, ctr_y, 0], aligned_edge=LEFT)
        t.run(FadeIn(dot), FadeIn(counter), run_time=0.3)
        ups = EV["up"]
        end_t = t.cues.time("overflow error", 0.62) - 0.5
        per = max((end_t - t.clock) / max(len(ups), 1), 0.12)
        for x, val in ups:
            is_err = not re.match(r"^[\d.e+-]+$", val)
            new = VGroup(mono(f"x = {x}", 24), mono("exp(x) =", 24, SOFT),
                         mono(val, 24 if not is_err else 22, weight="BOLD" if is_err else "NORMAL")) \
                .arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([ctr_x, ctr_y, 0], aligned_edge=LEFT)
            y = ceil_y + 0.02 if is_err else up_y(math.log10(float(val)) if float(val) > 0 else 0)
            t.run(Transform(counter, new), dot.animate.move_to([LOG_X, y, 0]), run_time=min(per, 0.35))
            if per > 0.35:
                t.until_t(t.clock + per - 0.35)
        sweep_cap = fit(serif(SWEEP_LABEL, 26, SOFT), 6.0).move_to([-6.2, UP_Y0 - 0.62, 0], aligned_edge=LEFT)
        t.run(FadeIn(sweep_cap), run_time=0.3)

        t.until("overflow error", 0.62)
        card_lines = VGroup(mono(">>> math.exp(1000)", 21), mono(EV["overflow_msg"], 21, weight="BOLD")) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        card = SurroundingRectangle(card_lines, color=INK, fill_color=CARD, fill_opacity=1, buff=0.16,
                                    corner_radius=0.08, stroke_width=2)
        card_group = VGroup(card, card_lines).move_to([lx, -2.25, 0])
        caption = serif(RUN_LABEL, 22, SOFT).next_to(card_group, DOWN, buff=0.12)
        t.run(FadeIn(card_group, shift=UP * 0.1), FadeIn(caption), run_time=0.45)

        t.until("only the difference did", 0.88)
        diff = mono("1000 − 1000 = 0", 36, weight="BOLD").move_to([rx, -2.6, 0])
        t.run(FadeIn(diff), Create(underline(diff, width=8, gap=0.15)), run_time=0.5)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  B08 — the boundary, the mirror image: the recorded sweep of math.exp(−x) falls past the smallest
#  positive float, printing fewer digits each step, until it is 0.0.
# ─────────────────────────────────────────────────────────────────────────────
DN_X, DN_Y0, DN_Y1, DN_BOT = -5.3, 1.45, -2.55, -440.0     # axis: log10 0..−440 → y DN_Y0..DN_Y1


def dn_y(log10v):
    return DN_Y0 + (DN_Y1 - DN_Y0) * log10v / DN_BOT


class B08_Underflow(Scene):
    BEAT, EST = "B08", 19.9

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        tag = t_tag()
        header = serif("What this does not establish", 44, weight="BOLD").move_to([0, 3.0, 0])
        inp = serif("scores  [0, −1000]", 34, SOFT).move_to([0, 2.35, 0])
        self.add(tag, header, inp)                             # opens on content
        cmd1, out1 = mono(">>> math.exp(-1000)", 26), mono(EV["exp_m1000"], 26)
        cmd2, out2 = mono(">>> probabilities([0, -1000])", 26), mono(EV["p_underflow"], 30, weight="BOLD")
        lines = VGroup(cmd1, out1, cmd2, out2).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        card = SurroundingRectangle(lines, color=INK, fill_color=CARD, fill_opacity=1, buff=0.25,
                                    corner_radius=0.08, stroke_width=2)
        card_group = VGroup(card, lines).move_to([3.15, 0.7, 0])
        caption = serif(RUN_LABEL, 22, SOFT).next_to(card_group, DOWN, buff=0.15)
        axis = Arrow([DN_X, DN_Y1 - 0.15, 0], [DN_X, DN_Y0 + 0.3, 0], buff=0, color=SOFT, stroke_width=3,
                     max_tip_length_to_length_ratio=0.05)
        ticks = VGroup()
        for p in (0, -100, -200, -300, -400):
            y = dn_y(p)
            ticks.add(Line([DN_X - 0.07, y, 0], [DN_X + 0.07, y, 0], color=SOFT, stroke_width=2),
                      serif(f"10{minus(p).translate(_SUP)}", 24, SOFT).move_to([DN_X - 0.18, y, 0], aligned_edge=RIGHT))
        ax_lab = serif("size of the weight (log scale)", 30, SOFT).move_to([DN_X + 0.2, DN_Y0 + 0.28, 0], aligned_edge=LEFT)
        t.run(FadeIn(card), FadeIn(cmd1), FadeIn(cmd2), FadeIn(caption), Create(axis), FadeIn(ticks), FadeIn(ax_lab),
              run_time=0.6)

        t.until("e to the minus thousand", 0.25)
        ty = dn_y(EV["true_exp10"])
        tdot = Dot([DN_X, ty, 0], radius=0.09, color=INK)
        true_label = VGroup(serif(f"e⁻¹⁰⁰⁰: true size ≈ 10{minus(EV['true_exp10']).translate(_SUP)}", 24),
                            serif("computed as −1000 / ln 10", 28, SOFT)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to([DN_X + 0.3, ty + 0.05, 0], aligned_edge=LEFT)
        t.run(FadeIn(tdot), FadeIn(true_label), run_time=0.45)

        t.until("too small for a float", 0.4)
        floor_y = dn_y(math.log10(EV["float_min"]))
        floor = DashedLine([DN_X - 0.25, floor_y, 0], [-0.6, floor_y, 0], color=INK, stroke_width=3, dash_length=0.12)
        floor_label = serif(f"smallest float ≈ {sci(EV['float_min'], 0)}", 30).move_to([-3.3, floor_y + 0.2, 0], aligned_edge=LEFT)
        t.run(Create(floor), FadeIn(floor_label), run_time=0.4)
        dot = Dot([DN_X, dn_y(0), 0], radius=0.09, color=INK)
        ctr_x, ctr_y = -4.95, 0.7
        counter = VGroup(mono("x = 0", 24), mono("exp(−x) =", 24, SOFT), mono("1.0", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.08) \
            .move_to([ctr_x, ctr_y, 0], aligned_edge=LEFT)
        self.add(dot, counter)
        downs = EV["down"]
        end_t = t.cues.time("rounds to zero", 0.45) + 0.4
        fast = [d for d in downs if d[0] < 708]
        slow = [d for d in downs if d[0] >= 708]
        budget = max(end_t - t.clock, 2.0)
        fast_per, slow_per = 0.12, max((budget - 0.12 * len(fast)) / max(len(slow), 1), 0.3)
        for x, val in downs:
            v = float(val)
            new = VGroup(mono(f"x = {x}", 24), mono("exp(−x) =", 24, SOFT), mono(val, 24, weight="BOLD" if v == 0 else "NORMAL")) \
                .arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([ctr_x, ctr_y, 0], aligned_edge=LEFT)
            y = dn_y(math.log10(v)) if v > 0 else floor_y - 0.35
            per = fast_per if x < 708 else slow_per
            t.run(Transform(counter, new), dot.animate.move_to([DN_X, y, 0]), run_time=min(per, 0.3))
            if per > 0.3:
                t.until_t(t.clock + per - 0.3)
        stored = mono("stored: 0.0", 26, weight="BOLD").move_to([DN_X + 0.3, floor_y - 0.38, 0], aligned_edge=LEFT)
        sweep_cap = serif(SWEEP_LABEL, 26, SOFT).move_to([DN_X - 0.6, -3.12, 0], aligned_edge=LEFT)
        t.run(FadeIn(stored), FadeIn(out1), FadeIn(sweep_cap), run_time=0.4)

        t.until("exactly zero", 0.62)
        t.run(FadeIn(out2), run_time=0.35)
        t.run(Create(underline(out2[-4:-1], width=8, gap=0.12)), run_time=0.4)

        summary = VGroup(serif("prevents:  overflow", 34), serif("does not prevent:  underflow", 34, weight="BOLD")) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.15, -2.2, 0])
        t.until("the shift prevents overflow", 0.8)
        t.run(FadeIn(summary[0], shift=UP * 0.08), run_time=0.35)
        t.until("doesn't prevent underflow", 0.88)
        t.run(FadeIn(summary[1], shift=UP * 0.08), run_time=0.35)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  BVDT — takeaways, each line on its spoken phrase (rebuilt: stock card type is too small).
# ─────────────────────────────────────────────────────────────────────────────
class BVDT_Takeaways(Scene):
    BEAT, EST = "BVDT", 18.4

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        lines_txt = t.cues.beat.get("takeaways") or ["takeaway"] * 5
        card = RoundedRectangle(corner_radius=0.18, width=12.6, height=5.85, stroke_color=BORDER, stroke_width=2,
                                fill_color=CARD, fill_opacity=1).move_to([0, -0.45, 0])
        heading = serif("What you should take away", 46, weight="BOLD").move_to([0, 3.0, 0])
        self.add(card, heading)                                 # opens on content
        rows = VGroup()
        for i, item in enumerate(lines_txt):
            claim, detail = (item if isinstance(item, (list, tuple)) else (item, ""))
            head = VGroup(serif(f"{i + 1}.", 34, SOFT), serif(claim, 34, weight="BOLD")).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
            sub = serif(detail, 30, SOFT).next_to(head[1], DOWN, buff=0.1, aligned_edge=LEFT)
            rows.add(VGroup(head, sub))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        fit(rows, card.width - 1.1).move_to(card.get_center()).align_to(card, LEFT).shift(RIGHT * 0.55)
        cues = ["changes every intermediate weight", "none of the final probabilities", "large scores don't overflow",
                "doesn't stop tiny weights", "never checks whether"]
        for i, (row, cue) in enumerate(zip(rows, cues)):
            t.until(cue, 0.15 + 0.17 * i)
            t.run(FadeIn(row, shift=UP * 0.12), run_time=0.4)
            if i == 3:                                          # the one accent: the limit
                t.run(Create(underline(row[0][1], gap=0.1)), run_time=0.35)
        t.hold_to_end()


# ─────────────────────────────────────────────────────────────────────────────
#  BHTF — your turn: the prompt types word by word as it is read (rebuilt: stock composer
#  types every prompt in a fixed 1.5 s).
# ─────────────────────────────────────────────────────────────────────────────
PROMPT_LINES = [
    "Here is my softmax function: [paste your code]. Don't fix it, and don't",
    "tell me whether it's correct. Give me one finite input where subtracting",
    "the max still doesn't protect me, predict exactly what my function returns",
    "for it, and give me the one line I'd run to check.",
]
HELD_BACK = ["Don't fix it", "don't tell me whether it's correct"]   # underlined on "It holds back…"


def phrase_segments(lines, phrase):
    """(line, first glyph, end glyph) pieces of `phrase` in the joined prompt, split at line breaks."""
    joined = " ".join(lines)
    a = joined.index(phrase)
    b = a + len(phrase)
    segs, off = [], 0
    for li, line in enumerate(lines):
        lo, hi = max(a, off), min(b, off + len(line))
        if lo < hi:
            segs.append((li, lo - off, hi - off))
        off += len(line) + 1
    return segs


class BHTF_YourTurn(Scene):
    BEAT, EST = "BHTF", 20.4

    def construct(self):
        t = Timeline(self, self.BEAT, self.EST)
        expected = t.cues.beat.get("prompt_text")
        if expected:
            assert " ".join(PROMPT_LINES) == expected, "on-screen prompt must match beat_sheet prompt_text"
        topic = sans("INFO 7375 · YOUR TURN", 20, SOFT, weight="BOLD").move_to([-6.15, 3.15, 0], aligned_edge=LEFT)
        segment = serif("Same Odds, Smaller Numbers", 30, weight="BOLD").move_to([-6.15, 2.72, 0], aligned_edge=LEFT)
        greet = serif("Your turn.", 52).move_to([0, 2.05, 0])
        card = RoundedRectangle(corner_radius=0.22, width=12.5, height=3.25, stroke_color=BORDER, stroke_width=2,
                                fill_color=CARD, fill_opacity=1).move_to([0, -0.15, 0])
        texts = VGroup(*[sans(s, 29) for s in PROMPT_LINES]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        fit(texts, card.width - 0.9).move_to(card.get_center() + UP * 0.3).align_to(card, LEFT).shift(RIGHT * 0.45)
        plus = Circle(radius=0.16, color=BORDER, stroke_width=2).move_to(card.get_corner(DL) + RIGHT * 0.5 + UP * 0.38)
        plus_t = sans("+", 22, SOFT).move_to(plus)
        send = RoundedRectangle(corner_radius=0.1, width=0.42, height=0.42, stroke_width=0, fill_color=GHOST,
                                fill_opacity=1).move_to(card.get_corner(DR) + LEFT * 0.5 + UP * 0.38)
        folder = sans("Aravind Ravi", 22, SOFT).next_to(card, DOWN, buff=0.25).align_to(card, LEFT).shift(RIGHT * 0.2)
        hint = mono("paste this into Claude…", 22, SOFT).next_to(folder, DOWN, buff=0.18).align_to(folder, LEFT)
        for line in texts:
            line.set_opacity(0)
        self.add(topic, segment, greet, card, plus, plus_t, send, folder, texts)   # opens on content

        spans = [(li, m.start(), m.end()) for li, s in enumerate(PROMPT_LINES) for m in re.finditer(r"\S+", s)]
        start = t.cues.index("here is my softmax function")
        for k, (li, a, b) in enumerate(spans):
            t.until_t(t.cues.time_at_index(None if start is None else start + k, 1.0 + k * 0.28) - 0.05)
            texts[li][a:b].set_opacity(1)          # shown from the next rendered frame
        t.run(FadeIn(hint), run_time=0.3)

        t.until("It holds back the fix and the verdict", 0.7)
        marks = [underline(texts[li][a:b], width=5, gap=0.07) for ph in HELD_BACK for li, a, b in phrase_segments(PROMPT_LINES, ph)]
        t.run(*[Create(m) for m in marks], run_time=0.5)
        t.hold_to_end()
