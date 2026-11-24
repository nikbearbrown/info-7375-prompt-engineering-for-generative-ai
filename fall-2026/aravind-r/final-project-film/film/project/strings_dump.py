"""strings_dump.py — every visible on-screen string of a scene, with the first and last time it is on screen.

Used by positioning_check.py (the positioning audit gate). Same harness as overlap_check.py: the scene runs through
Manim and, on every rendered frame (24 fps), each visible Text object's original string is recorded.
Output: _qc/positioning/strings_<SceneClass>.json

Usage (from film/project/):
  manim -r 384,216 --fps 24 --disable_caching --media_dir <scratch> strings_dump.py <SceneClass>
"""
import json
import os

from manim import Scene, Text

VIS = 0.08           # opacity below this is treated as invisible
_HERE = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_HERE, "_qc", "positioning")
os.makedirs(_OUT, exist_ok=True)
_orig_update = Scene.update_to_time


def _visible_strings(scene):
    out = set()
    for top in scene.mobjects:
        for m in top.get_family():
            if isinstance(m, Text):
                fam = m.get_family()
                op = max((float(g.get_fill_opacity()) for g in fam[1:] or fam), default=0.0)
                if op >= VIS and len(m.get_all_points()):
                    out.add(getattr(m, "original_text", None) or m.text)
    return out


def update_to_time(self, t):
    _orig_update(self, t)
    if not hasattr(self, "_seen"):
        self._seen = {}
    now = round(float(getattr(self.renderer, "time", 0.0)) + float(t), 3)
    for s in _visible_strings(self):
        first, _last = self._seen.get(s, (now, now))
        self._seen[s] = (first, now)


def tear_down(self):
    name = type(self).__name__
    rows = [{"text": s, "first": a, "last": b} for s, (a, b) in sorted(getattr(self, "_seen", {}).items(), key=lambda kv: kv[1][0])]
    json.dump(rows, open(os.path.join(_OUT, f"strings_{name}.json"), "w"), indent=1, ensure_ascii=False)
    print(f"[strings] {name}: {len(rows)} distinct strings")


Scene.update_to_time = update_to_time
Scene.tear_down = tear_down

import scenes as _scenes  # noqa: E402
for _n in [n for n in dir(_scenes) if n[:1] == "B" and n[1:3].isdigit() and "_" in n]:
    globals()[_n] = type(_n, (getattr(_scenes, _n),), {"__module__": __name__})
