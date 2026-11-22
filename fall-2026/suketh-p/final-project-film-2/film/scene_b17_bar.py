
# ──────────────────────────────────────────── B17 ────────────────────────────────────────────
# The student's own "worked / didn't work" bar (Part 4, between B16 and B18). build_scenes.py pastes this section into
# scenes.py only when beat_sheet.json has a B17 beat. Every word on screen comes from the sheet: the stamp and part tag
# (ON_SCREEN) and the bar's text (BAR_LINES, copied by make_scene_data.py from the beat's `bar_lines`, the student's
# words). This file writes none, and adds no numbers. A long line is set on two rows at a word boundary; no word changes.


def _bar_rows(text, width, size=34, floor=32):
    """The line at `size`, shrunk to fit `width` but never below the 32 floor; if it still does not fit, split at the
    word boundary that balances the two halves. Never cuts or edits the words."""
    t = T(text, size)
    while t.width > width and size > floor:
        size -= 2
        t = T(text, size)
    if t.width <= width or " " not in text:
        return [t]
    words, best = text.split(" "), None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        w = max(T(a, size).width, T(b, size).width)
        if best is None or w < best[0]:
            best = (w, a, b)
    return [T(best[1], size), T(best[2], size)]


def _bar_column(title, items, x0, top, good):
    """A titled column: the title, then each item with an ink check (worked) or cross (didn't work) beside it.
    Returns (title mobject, [VGroup(mark, rows) per item])."""
    head = label_left(title, x0, top, 44)
    out, y = [], top - 0.72
    for it in items:
        rows = _bar_rows(it, 5.35)
        g = VGroup(check(x0 + 0.12, y, s=0.15) if good else cross(x0 + 0.16, y, s=0.13))
        for j, r in enumerate(rows):
            r.move_to([x0 + 0.55, y - 0.5 * j, 0])
            r.align_to(np.array([x0 + 0.55, 0.0, 0.0]), LEFT)
            g.add(r)
        out.append(g)
        y -= 0.5 * len(rows) + 0.2
    return head, out


class B17_Bar(Scene):
    def construct(self):
        chrome(self)
        bl = BAR_LINES["B17"]
        y = 1.85                                                     # the measuring bar, two zones
        ticks = VGroup(*[Line([-5.8 + 1.16 * i, y - 0.32, 0], [-5.8 + 1.16 * i, y - 0.14, 0], color=INK, stroke_width=4)
                         for i in range(11)])                         # scale marks only: no numbers are given
        rail = Line([-5.8, y, 0], [5.8, y, 0], color=GHOST, stroke_width=16)
        self.add(rail)
        gplay(self, Create(ticks), run_time=0.5)
        worked = rect(-2.95, y, 5.7, 0.2, BAR3)
        failed = rect(2.95, y, 5.7, 0.2, BAR2)
        head_w, items_w = _bar_column(bl["worked_title"], bl["worked"], -5.8, 0.95, True)
        head_f, items_f = _bar_column(bl["failed_title"], bl["failed"], 0.3, 0.95, False)
        at(self, "It worked if", lead=0.0)
        gplay(self, GrowFromEdge(worked, LEFT), FadeIn(head_w), Create(check(-0.35, y + 0.45, s=0.17)), run_time=0.5)
        for g, cue in zip(items_w, ("at least twenty-seven", "my checks catch")):
            at(self, cue)
            gplay(self, FadeIn(g), run_time=0.4)
        at(self, "It didn't work if")
        gplay(self, GrowFromEdge(failed, LEFT), FadeIn(head_f), Create(cross(5.55, y + 0.45, s=0.15)), run_time=0.5)
        for g, cue in zip(items_f, ("misquotes", "clears even one", "wrongly rules out")):
            at(self, cue)
            gplay(self, FadeIn(g), run_time=0.4)
        at(self, "I'll label about sixty")
        gplay(self, FadeIn(label(bl["footer"], 0.0, -2.75, 36)), run_time=0.5)
        finish(self)
