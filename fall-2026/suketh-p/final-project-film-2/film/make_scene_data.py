#!/usr/bin/env python3
"""make_scene_data.py: writes scene_data.py, the data block that build_scenes.py pastes into scenes.py
(Gate A copies only scenes.py, so nothing on screen may live in another file at render time).

Drafted by Claude Code on 2026-11-21 for fine-print-film.

1. ON_SCREEN: each beat's honesty stamp (`on_screen_status`, top left) and part tag (`on_screen_part`, top right),
   copied from beat_sheet.json, so the screen can never drift from the sheet.

2. BAR_LINES: the text of B17, the student's "worked / didn't work" bar, from that beat's `bar_lines`, once it
   exists; CREDIT: BOUT's small line, exactly as quoted in BOUT's visual_intent.

3. TERM: the terminal replays in B08, B09 and B10. Every character comes from a saved log in ../evidence/terminal/;
   nothing is typed here. The Nov 21 logs are read from their .json captures (prompt line = "<cwd_shown> % <command>",
   exactly as the matching .txt shows it). The Nov 8 log exists only as the student's .txt (copied unchanged from JS2),
   so it is read from that file: the session after its "---" header line. Each source file is checked against
   ../evidence/terminal/SHA256SUMS first, and each .json is checked line by line against its .txt.
   The only changes made to the text:
     (a) a subset of whole lines is shown (KEEP below names them);
     (b) runs of 2+ spaces are collapsed to two spaces, to fit the width;
     (c) Nov 8 log only: cd "/Users/.../js2-loop-tools-diff" is shown as cd ~/…/js2-loop-tools-diff;
     (w) a line longer than the window (COLS characters) continues on the next row, cut at exactly COLS characters,
         the way a terminal window of that width wraps it. No character is added, removed or changed by (w).
         (w) is NOT in the brief's list (a)-(c); PRODUCTION-NOTES.md flags it for the student's decision.
   The result is scanned for private details (home-folder path, user name) and for the numbers the film quotes.

4. MONO: PT Mono (OFL, shipped with the toolkit) metrics measured with Manim (the same renderer as the film), used to size the terminal text so its
   x-height is TERM_XH_PX at 2160p (GATE T's floor is 41 px) and COLS characters fit the window.

Run: python3 make_scene_data.py   (build_scenes.py runs it first; toolkit venv active, Manim installed)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVID = HERE.parent / "evidence" / "terminal"

COLS = 63                  # window width in characters (PT Mono at a 43 px x-height: 63 fit in the safe width)
TERM_FONT = "PT Mono"      # OFL 1.1, shipped with the toolkit (runtime/fonts/PT_Mono/OFL.txt)
TERM_FS = 48               # Text() is built at this size and scaled down (Manim rounds advances at small sizes)
TERM_XH_PX = 43.0          # target x-height at 2160p; GATE T floor is 41 px (1.9 % of 2160)
PX_PER_UNIT = 3840 / (128 / 9)   # Manim frame is 128/9 units wide

# Which saved lines each window shows. "P" is the prompt line; numbers are 0-based indices into the log's output
# lines (the .json "lines" list; for the Nov 8 .txt, the lines after the prompt).
KEEP = {
    "B08": [("tests-2026-11-21", ["P", 2, 3, 4]),
            ("film-normal-noapproval-2026-11-21", ["P", 1, 2, 3])],
    "B09": [("film-rule-count-2026-11-21", ["P", 0])],
    "B10": [("film-normal-noapproval-2026-11-21", ["P", 0, 4]),
            ("2026-11-08-normal-1-run-by-student", ["P", 0, 4])],
}
MUST_SHOW = {   # the numbers the narration and FACTCHECK rely on; the build stops if a replay loses one
    "B08": ["Ran 164 tests", "OK", "jobs=635 new=83", "jobs=895 new=88", "jobs=32 new=1"],
    "B09": ["172"],
    "B10": ["state advanced: False", "state advanced: True", "--approve-state 2026-11-08-normal-1:state/state.json",
            "no approval was given for this run"],
}
PRIVATE = ["/Users", "sukethreddyprodutoor", "Desktop", "Prompt Engineering", "fork/fall-2026", "suketh-p"]


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_sums():
    sums = {}
    for ln in (EVID / "SHA256SUMS").read_text().splitlines():
        if ln.strip():
            h, name = ln.split(None, 1)
            sums[name.strip()] = h
    return sums


def load_log(name, sums):
    """Return (prompt, output_lines, source_file, sha, notes) from the saved log, verified."""
    js, txt = EVID / f"{name}.json", EVID / f"{name}.txt"
    notes = []
    if js.exists():
        assert sums.get(js.name) == sha256(js), f"{js.name}: SHA-256 does not match SHA256SUMS"
        assert sums.get(txt.name) == sha256(txt), f"{txt.name}: SHA-256 does not match SHA256SUMS"
        d = json.loads(js.read_text())
        prompt = f"{d['cwd_shown']} % {d['command']}"
        out = [l["text"] for l in d["lines"]]
        tl = txt.read_text().split("\n")
        assert tl[0] == prompt, f"{name}: .txt prompt line differs from the .json"
        assert tl[1:1 + len(out)] == out, f"{name}: .txt output differs from the .json"
        assert tl[1 + len(out)] == f"[exit {d['exit_code']}]", f"{name}: exit line differs"
        return prompt, out, js.name, sums[js.name], notes
    # Nov 8: only the student's .txt exists (copied unchanged from JS2)
    assert sums.get(txt.name) == sha256(txt), f"{txt.name}: SHA-256 does not match SHA256SUMS"
    lines = txt.read_text().split("\n")
    session = lines[lines.index("---") + 1:]
    while session and not session[-1].strip():
        session.pop()
    prompt, out = session[0], session[1:]
    pat = re.compile(r'cd "/Users/[^"]*/js2-loop-tools-diff"')
    assert len(pat.findall(prompt)) == 1, f"{name}: expected one cd \"/Users/.../js2-loop-tools-diff\""
    prompt = pat.sub("cd ~/…/js2-loop-tools-diff", prompt)
    notes.append("(c) cd \"/Users/…/js2-loop-tools-diff\" shown as cd ~/…/js2-loop-tools-diff")
    return prompt, out, txt.name, sums[txt.name], notes


def collapse(s):
    return re.sub(r" {2,}", "  ", s)


def wrap(s):
    return [s[i:i + COLS] for i in range(0, len(s), COLS)] or [""]


def measure_mono():
    from manim import Text, config
    one = Text("x", font=TERM_FONT, font_size=TERM_FS)
    many = Text("x" * 41, font=TERM_FONT, font_size=TERM_FS)
    bar1 = Text("│", font=TERM_FONT, font_size=TERM_FS)
    adv = (many.width - one.width) / 40
    k = TERM_XH_PX / (one.height * PX_PER_UNIT)
    return {"k": k, "adv": adv * k, "xh_px": one.height * k * PX_PER_UNIT, "bar_h": bar1.height * k,
            "fw": float(config.frame_width)}


def main():
    sheet = json.loads((HERE / "beat_sheet.json").read_text())
    on_screen = {b["beat_id"]: (b.get("on_screen_status", ""), b.get("on_screen_part", ""))
                 for b in sheet["beats"]}
    bar = {}
    for bt in sheet["beats"]:
        if bt["beat_id"] == "B17":                # the student's bar: their words, never written here
            bl = bt.get("bar_lines")
            ok = (isinstance(bl, dict) and all(isinstance(bl.get(k), str) and bl[k].strip()
                                               for k in ("worked_title", "failed_title", "footer"))
                  and all(isinstance(bl.get(k), list) and bl[k] and all(isinstance(x, str) and x.strip() for x in bl[k])
                          for k in ("worked", "failed")))
            assert ok, "B17 needs bar_lines {worked_title, worked[], failed_title, failed[], footer}: the student's words"
            bar["B17"] = bl
    bout = next(bt for bt in sheet["beats"] if bt["beat_id"] == "BOUT")
    m = re.search(r"one small line: '(.+)'$", bout["shot"]["visual_intent"].strip())
    assert m and " · " in m.group(1), "BOUT visual_intent must quote its small line"
    credit = m.group(1)
    sums = check_sums()
    term, record = {}, {}
    for bid, windows in KEEP.items():
        term[bid], record[bid] = [], []
        for name, keep in windows:
            prompt, out, src, sha, notes = load_log(name, sums)
            total = 1 + len(out)
            lines, dropped, collapsed, wrapped = [], [], [], []
            for ref in keep:
                raw = prompt if ref == "P" else out[ref]
                shown = collapse(raw)
                if shown != raw:
                    collapsed.append(ref)
                rows = wrap(shown)
                if len(rows) > 1:
                    wrapped.append(ref)
                lines.append({"src": ref, "rows": rows})
            kept_out = [r for r in keep if r != "P"]
            dropped = [i for i in range(len(out)) if i not in kept_out]
            term[bid].append({"log": name, "file": src, "sha256": sha, "lines": lines})
            record[bid].append({"log": src, "sha256": sha, "source_lines": total,
                                "shown": keep, "dropped_output_lines": dropped,
                                "dropped_text": [out[i] for i in dropped],
                                "collapsed": collapsed, "wrapped": wrapped, "notes": notes})
        flat = "\n".join(r for w in term[bid] for l in w["lines"] for r in l["rows"])
        joined = "\n".join("".join(l["rows"]) for w in term[bid] for l in w["lines"])
        for p in PRIVATE:
            assert p not in flat, f"{bid}: private detail {p!r} would appear on screen"
        for m in MUST_SHOW[bid]:
            assert m in joined, f"{bid}: {m!r} missing from the replay"
    mono = measure_mono()
    widest = max(len(r) for b in term.values() for w in b for l in w["lines"] for r in l["rows"])
    assert widest <= COLS
    text_w = COLS * mono["adv"]
    assert text_w / 2 < 6.15, f"terminal text {text_w:.2f} units wide: past the safe area"
    head = ("\n# ═════════════ SCENE DATA — GENERATED by make_scene_data.py: do not edit here ═════════════\n"
            "# ON_SCREEN: (stamp, part tag) per beat, from beat_sheet.json.\n"
            "# TERM: terminal replays built from ../evidence/terminal/ (see make_scene_data.py and PRODUCTION-NOTES.md).\n")
    body = (f"ON_SCREEN = {on_screen!r}\n"
            f"TERM_FONT = {TERM_FONT!r}\nTERM_FS = {TERM_FS}\nTERM_K = {mono['k']:.6f}\n"
            f"TERM_ADV = {mono['adv']:.6f}\nTERM_COLS = {COLS}\nTERM_BAR_H = {mono['bar_h']:.6f}\n"
            f"BAR_LINES = {bar!r}\nCREDIT = {credit!r}\n"
            f"TERM = {json.dumps(term, ensure_ascii=False, indent=1)}\n")
    (HERE / "scene_data.py").write_text(head + body)
    (HERE / "terminal_replay_record.json").write_text(json.dumps(
        {"generated_by": "make_scene_data.py", "cols": COLS, "x_height_px_at_2160": round(mono["xh_px"], 1),
         "advance_px_at_2160": round(mono["adv"] * PX_PER_UNIT, 1), "beats": record},
        indent=2, ensure_ascii=False) + "\n")
    print(f"scene_data.py: {len(on_screen)} beats on screen; terminal x-height {mono['xh_px']:.1f}px, "
          f"advance {mono['adv'] * PX_PER_UNIT:.1f}px, {COLS} cols = {text_w:.2f} units")
    for bid, ws in record.items():
        for w in ws:
            print(f"  {bid} {w['log']}: shown {w['shown']} dropped {w['dropped_output_lines']} "
                  f"collapsed {w['collapsed']} wrapped {w['wrapped']} {' '.join(w['notes'])}")


if __name__ == "__main__":
    sys.exit(main())
