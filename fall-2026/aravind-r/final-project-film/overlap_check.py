"""overlap_check.py — frame-by-frame text-overlap check for the v2 scenes (my own check, not a toolkit gate).

Runs a scene from scenes.py through Manim and, on EVERY rendered frame (24 fps), inspects the live geometry:
  1. text vs text: two visible Text objects whose bounding boxes intersect;
  2. shape vs text: any visible line, outline or shape boundary that passes through a visible Text's box.
Text sitting inside a container whose edge stays clear of the text is not a violation.

Usage (from v2/):
  manim -r 384,216 --fps 24 --disable_caching --media_dir <scratch> overlap_check.py <SceneClass>
Writes overlap_<SceneClass>.json next to this file and prints a summary line.
"""
import json
import os
import numpy as np
from manim import Scene, Text, VMobject

from scenes import *  # noqa: F401,F403  (the scenes under test)

EPS = 0.015          # shrink text boxes slightly so touching edges don't count
VIS = 0.08           # opacity below this is treated as invisible
_HERE = os.path.dirname(os.path.abspath(__file__))
_orig_update = Scene.update_to_time


def _opacity(m):
    try:
        return max(float(m.get_fill_opacity()), float(m.get_stroke_opacity()) if m.get_stroke_width() > 0 else 0.0)
    except Exception:
        return 1.0


def _text_boxes(scene):
    boxes, text_ids = [], set()
    for top in scene.mobjects:
        for m in top.get_family():
            if isinstance(m, Text):
                fam = m.get_family()
                text_ids.update(id(x) for x in fam)
                op = max((float(g.get_fill_opacity()) for g in fam[1:] or fam), default=0.0)
                if op < VIS or len(m.get_all_points()) == 0:
                    continue
                l, r = m.get_left()[0], m.get_right()[0]
                b, t = m.get_bottom()[1], m.get_top()[1]
                boxes.append((m.text if hasattr(m, "text") else "?", l + EPS, r - EPS, b + EPS, t - EPS))
    return boxes, text_ids


def _samples(m):
    pts = m.points
    if pts is None or len(pts) < 4:
        return np.zeros((0, 3))
    n = (len(pts) // 4) * 4
    c = pts[:n].reshape(-1, 4, 3)
    ts = np.linspace(0, 1, 14)[:, None]
    out = []
    for p0, p1, p2, p3 in c:
        out.append(((1 - ts) ** 3) * p0 + 3 * ((1 - ts) ** 2) * ts * p1 + 3 * (1 - ts) * ts ** 2 * p2 + ts ** 3 * p3)
    return np.vstack(out)


def _check(scene, t):
    boxes, text_ids = _text_boxes(scene)
    found = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]:
                found.append(("text/text", a[0], b[0]))
    for top in scene.mobjects:
        for m in top.get_family():
            if id(m) in text_ids or not isinstance(m, VMobject) or len(m.points) == 0:
                continue
            if _opacity(m) < VIS:
                continue
            if m.get_stroke_width() <= 0 and float(m.get_fill_opacity()) < VIS:
                continue
            s = _samples(m)
            if not len(s):
                continue
            for name, l, r, b, tt in boxes:
                inside = (s[:, 0] > l) & (s[:, 0] < r) & (s[:, 1] > b) & (s[:, 1] < tt)
                if inside.any():
                    found.append(("shape/text", type(m).__name__, name))
    for f in found:
        scene._ov.setdefault(f, []).append(round(t, 3))


def update_to_time(self, t):
    _orig_update(self, t)
    if not hasattr(self, "_ov"):
        self._ov = {}
    _check(self, float(getattr(self.renderer, "time", 0.0)) + float(t))


def tear_down(self):
    res = [{"kind": k[0], "a": k[1], "b": k[2], "first": v[0], "last": v[-1], "frames": len(v)}
           for k, v in sorted(getattr(self, "_ov", {}).items(), key=lambda kv: kv[1][0])]
    name = type(self).__name__
    json.dump(res, open(os.path.join(_HERE, f"overlap_{name}.json"), "w"), indent=1, ensure_ascii=False)
    print(f"[overlap] {name}: {len(res)} distinct overlap(s), {sum(r['frames'] for r in res)} frame-hits")
    for r in res:
        print(f"[overlap]   {r['kind']:10s} {r['first']:6.2f}-{r['last']:6.2f}s ({r['frames']} fr)  {r['a']!r} x {r['b']!r}")


Scene.update_to_time = update_to_time
Scene.tear_down = tear_down

# Manim only discovers scenes defined in this module: re-declare each scene under its own name.
import scenes as _scenes
for _n in ["BIDEA_Hook", "B01_WhatItIs", "B02_Difference", "B03_FirstMinute", "B04_Proves", "B05_InOutFirst",
           "B06_Risk", "B07_WhyMe", "B08_ExistsWill"]:
    globals()[_n] = type(_n, (getattr(_scenes, _n),), {"__module__": __name__})
