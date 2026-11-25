"""Render every beat's frames (1920x1080) from HTML: title and text cards, crops of the real footage with one highlight
at a time, and, for the three pans, a transparent overlay plus the tall source the pan moves over.
Writes build/stills/*.png and build/out/plan.json. Run with $PW_PY (a Python with Playwright and its Chromium)."""
import html, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

B = Path(__file__).resolve().parents[1]
FILM = B.parent
CAP, CARDS, STILLS, OUT = B / "capture", B / "cards", B / "stills", B / "out"
for d in (CARDS, STILLS, OUT):
    d.mkdir(exist_ok=True)
BOX = json.loads((CAP / "boxes.json").read_text())
RUNB, EVB = BOX["run"], BOX["eval"]
BEATS = {b["id"]: b for b in json.load(open(FILM / "beats.json"))}
DUR = json.loads((B / "audio" / "durations.json").read_text())
LEAD, TAIL, FPS = 0.30, 0.45, 30
E = html.escape
X0, Y0, W0, H0 = 96, 128, 1728, 776          # the content box; y 904 to 1080 stays free for the soft captions
IMG = {"run_2x": (2880, 2), "eval_2x": (2880, 2), "gh_ci": (1920, 4 / 3), "gh_commits": (1920, 4 / 3),
       "runs_1.2x": (1728, 1.2), "eval_1.2x": (1728, 1.2), "wait": (1440, 1)}
SRC = {"run_2x": CAP / "run_2x.png", "eval_2x": CAP / "eval_2x.png", "gh_ci": CAP / "gh_ci.png",
       "gh_commits": CAP / "gh_commits.png", "runs_1.2x": CAP / "runs_1.2x.png", "eval_1.2x": CAP / "eval_1.2x.png",
       "wait": CAP / "saved" / "2-waiting-for-approval.png"}
PARTS = {"1": "Part 1 · Executive summary", "2": "Part 2 · What others have done", "3": "Part 3 · Methods",
         "4": "Part 4 · Evaluation", "A": "Appendix"}

CSS = """
:root{--bg:#0A0E13;--bar:#0D131A;--panel:#10171F;--panel2:#0C1218;--line:#1E2A38;--line2:#2A3A4E;--text:#E6EDF3;
--soft:#C3D0DE;--muted:#8B9BB0;--dim:#5F7084;--green:#3FB950;--red:#F85149;--amber:#E3B341;--blue:#58A6FF;--violet:#B392F0}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;background:var(--bg);color:var(--text);overflow:hidden;
font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
body.clear{background:transparent}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace}
.top{position:absolute;left:0;top:0;width:1920px;height:64px;background:var(--bar);border-bottom:1px solid var(--line);z-index:5}
.brand{position:absolute;left:96px;top:0;line-height:64px;font-size:24px;font-weight:650;letter-spacing:.01em}
.brand i{display:inline-block;width:12px;height:12px;border-radius:50%;background:#F0883E;margin-right:12px;vertical-align:1px}
.part{position:absolute;right:96px;top:0;line-height:64px;font-size:20px;color:var(--muted)}
.tag{position:absolute;left:96px;top:86px;font-size:15px;line-height:24px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);z-index:5}
.frame{position:absolute;overflow:hidden;border:1px solid var(--line2);border-radius:10px;background:var(--panel2);
box-shadow:0 10px 40px rgba(0,0,0,.35)}
.frame img{position:absolute;max-width:none}
.frame.bare{border:0;border-radius:0;box-shadow:none;background:transparent}
svg text{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif}
.hl{position:absolute;border:3px solid var(--amber);border-radius:8px;box-shadow:0 0 0 5px rgba(227,179,65,.16);z-index:3}
.hl.green{border-color:var(--green);box-shadow:0 0 0 5px rgba(63,185,80,.16)}
.hl.red{border-color:var(--red);box-shadow:0 0 0 5px rgba(248,81,73,.16)}
.hl.blue{border-color:var(--blue);box-shadow:0 0 0 5px rgba(88,166,255,.16)}
.abs{position:absolute}
.h1{font-size:56px;font-weight:700;letter-spacing:-.01em;line-height:1.1}
.h2{font-size:40px;font-weight:650;line-height:1.15}
.sub{font-size:28px;color:var(--soft);line-height:1.35}
.lbl{font-size:16px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.src{font-size:19px;color:var(--dim);font-family:ui-monospace,"SF Mono",Menlo,monospace}
.dot{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:16px;vertical-align:2px}
.chip{position:absolute;display:flex;align-items:center;padding:0 24px;height:64px;border:1px solid var(--line2);
border-radius:12px;background:var(--panel);font-size:28px}
"""

def page(body, part=None, tag=None, clear=False):
    top = "" if part is None else f'<div class="top"><div class="brand"><i></i>Klaxon</div><div class="part">{E(PARTS[part])}</div></div>'
    tg = "" if not tag else f'<div class="tag">{E(tag)}</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            + (f'<style>html,body{{background:transparent!important}}</style>' if clear else '')
            + f'<body class="{"clear" if clear else ""}">{top}{tg}{body}</body></html>')

def crop(key, css, dst, hls=(), pad=6, align="center", bare=False):
    """A crop of a captured image. css = (x, y, w, h) in the page's CSS px; dst = (x, y, w, h) on stage; the crop is
    scaled to fit dst (never above 1.0 of its pixels) and centered (or left/top aligned). hls = [(css box, colour)]."""
    w_img, dpr = IMG[key]
    sx, sy, sw, sh = [v * dpr for v in css]
    s = min(dst[2] / sw, dst[3] / sh, 1.0)
    shw, shh = sw * s, sh * s
    ox = dst[0] + (0 if "left" in align else (dst[2] - shw) / 2)
    oy = dst[1] + (0 if "top" in align else (dst[3] - shh) / 2)
    cls = "frame bare" if bare else "frame"   # outside the f-string, so the file also parses on Python 3.11
    out = [f'<div class="{cls}" style="left:{ox:.1f}px;top:{oy:.1f}px;width:{shw:.1f}px;height:{shh:.1f}px">'
           f'<img src="{SRC[key].as_uri()}" style="left:{-sx * s:.1f}px;top:{-sy * s:.1f}px;width:{w_img * s:.1f}px"></div>']
    for (hx, hy, hw, hh), col in hls:
        x = ox + (hx * dpr - sx) * s - pad; y = oy + (hy * dpr - sy) * s - pad
        out.append(f'<div class="hl {col}" style="left:{x:.1f}px;top:{y:.1f}px;width:{hw * dpr * s + 2 * pad:.1f}px;'
                   f'height:{hh * dpr * s + 2 * pad:.1f}px"></div>')
    return "".join(out), (ox, oy, shw, shh)

def bx(d, pad=0):
    return (d["x"] - pad, d["y"] - pad, d["w"] + 2 * pad, d["h"] + 2 * pad)

def union(*ds):
    x0 = min(d["x"] for d in ds); y0 = min(d["y"] for d in ds)
    x1 = max(d["x"] + d["w"] for d in ds); y1 = max(d["y"] + d["h"] for d in ds)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}

def cue(beat, phrase):
    """Fraction of the beat's spoken text before the phrase (where the step starts)."""
    sp = BEATS[beat]["spoken"]; i = sp.find(phrase)
    assert i >= 0, (beat, phrase)
    return i / len(sp)

PLAN = {}
def steps(beat, items):
    """items = [(phrase or None, html)]: the steps of a static beat, each starting at its phrase."""
    PLAN[beat] = {"kind": "steps", "steps": []}
    for k, (phrase, doc) in enumerate(items):
        f = 0.0 if phrase is None else cue(beat, phrase)
        name = f"{beat}_{k + 1}"
        (CARDS / f"{name}.html").write_text(doc)
        PLAN[beat]["steps"].append({"png": f"stills/{name}.png", "frac": f})

def pan(beat, src_doc, src_size, overlay_doc, window, y0, y1):
    """A pan: the tall source (rendered from src_doc) moves under a window of the overlay, from y0 to y1 (source px)."""
    (CARDS / f"{beat}_src.html").write_text(src_doc)
    (CARDS / f"{beat}_overlay.html").write_text(overlay_doc)
    PLAN[beat] = {"kind": "pan", "src": f"stills/{beat}_src.png", "src_size": src_size,
                  "overlay": f"stills/{beat}_overlay.png", "window": window, "y0": y0, "y1": y1}

def hole(x, y, w, h):
    """The pan's window: everything outside it is the background; soft 28 px fades at its top and bottom edges."""
    fade = lambda top, d: (f'<div class="abs" style="left:{x}px;top:{top}px;width:{w}px;height:28px;'
                           f'background:linear-gradient({d}, #0A0E13, rgba(10,14,19,0))"></div>')
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:10px;'
            f'border:1px solid var(--line2);box-shadow:0 0 0 2400px var(--bg)"></div>' + fade(y, "to bottom") + fade(y + h - 28, "to top"))

# B01: title card (L1)
steps("B01", [(None, page(
    '<div class="abs" style="left:0;top:330px;width:1920px;text-align:center">'
    '<div style="font-size:132px;font-weight:750;letter-spacing:-.02em;line-height:1">'
    '<span style="display:inline-block;width:30px;height:30px;border-radius:50%;background:#F0883E;margin-right:30px;vertical-align:22px"></span>Klaxon</div>'
    '<div class="sub" style="font-size:40px;margin-top:34px">An AI on-call engineer for a payments system</div>'
    '<div style="font-size:24px;color:var(--muted);margin-top:26px">INFO 7375 · Final Project Film · Aravind Sundaravadivelu</div></div>'
    '<div class="abs src" style="left:0;top:820px;width:1920px;text-align:center;font-size:19px">'
    'Narration: a synthetic voice (Kokoro, am_onyx). All data in this film is synthetic.</div>'))])

# B02: the panel's saved runs, a slow scroll (L2, pan)
wx, ww, wh = X0, W0, H0
pan("B02", page(f'<img src="{SRC["runs_1.2x"].as_uri()}" style="position:absolute;left:0;top:0;width:1728px">', clear=True)
    .replace("width:1920px;height:1080px", "width:1728px;height:9197px"), (1728, 9197),
    page(hole(wx, Y0, ww, wh), part="1", tag="Klaxon's web panel · every saved run (it only reads them)", clear=True),
    (wx, Y0, ww, wh), 0, 560)

# B03: the signals at the alert (L3)
sig = RUNB["signals"]
def b03(hls):
    body, _ = crop("run_2x", bx(sig), (X0, Y0, W0, H0), hls)
    return page(body, part="1", tag="Klaxon's web panel · the week 7 live run, recorded · signals at the alert")
steps("B03", [(None, b03([])), ("Only the money check failed", b03([(bx(RUNB["bad_tile"]), "red")])),
              ("our books were", b03([(bx(RUNB["signals_sentence"]), "amber")]))])

# B04: looks healthy, books wrong (L4 split)
ver = RUNB["verification"]; li = RUNB["ver_li"]
vcrop = (ver["x"], ver["y"], ver["w"], li[2]["y"] + li[2]["h"] + 14 - ver["y"])
def b04(hls, line):
    body, _ = crop("run_2x", vcrop, (X0, Y0, 1000, H0), hls)
    right = ('<div class="abs" style="left:1176px;top:300px;width:640px">'
             '<div class="lbl">Verification, by code, after the approved rollback</div>'
             f'<div class="h2" style="margin-top:22px;font-size:50px;line-height:1.2;opacity:{1 if line else 0}">'
             "A fix isn't done until the money is checked.</div></div>")
    return page(body + right, part="1", tag="Klaxon's web panel · the week 7 live run, recorded · verification")
steps("B04", [(None, b04([], False)), ("everything looks healthy", b04([(bx(li[0]), "green")], False)),
              ("while the books", b04([(bx(li[2]), "red")], False)), ("With Klaxon", b04([(bx(li[2]), "red")], True))])

# B05: who else builds this (L5 list)
ROWS5 = [("Resolve AI", "$125M Series A at a $1B valuation", "TechCrunch · Feb 4, 2026"),
         ("Traversal", "$120M Series B", "Goodwin · Nov 4, 2026"),
         ("Datadog · AWS · Microsoft", "Bits AI SRE · DevOps Agent · Azure SRE Agent", "Dec 2, 2025 · Mar 31, 2026 · Mar 10, 2026")]
def b05(n):
    rows = []
    for i, (a, b, c) in enumerate(ROWS5):
        y = 420 + i * 150
        op = 1 if i < n else 0
        rows.append(f'<div class="abs" style="left:{X0}px;top:{y}px;width:{W0}px;height:118px;border-top:1px solid var(--line);opacity:{op}">'
                    f'<div class="abs" style="left:0;top:34px;font-size:32px;font-weight:650">{E(a)}</div>'
                    f'<div class="abs" style="left:560px;top:34px;font-size:32px;color:var(--soft)">{E(b)}</div>'
                    f'<div class="abs src" style="left:560px;top:84px">{E(c)}</div></div>')
    head = (f'<div class="abs" style="left:{X0}px;top:150px"><div class="h1">What others have done</div>'
            '<div class="sub" style="margin-top:18px">The industry calls it an AI SRE: an AI site reliability engineer.</div></div>')
    return page(head + "".join(rows), part="2")
steps("B05", [(None, b05(0)), ("Resolve", b05(1)), ("Traversal", b05(2)), ("Datadog", b05(3))])

# B06: what they got (L6 two numbers)
def b06(n):
    col = lambda x, big, a, c, op: (f'<div class="abs" style="left:{x}px;top:330px;width:760px;opacity:{op}">'
                                    f'<div style="font-size:124px;font-weight:750;letter-spacing:-.02em;line-height:1">{E(big)}</div>'
                                    f'<div class="sub" style="margin-top:28px;font-size:30px">{E(a)}</div>'
                                    f'<div class="src" style="margin-top:18px">{E(c)}</div></div>')
    return page(f'<div class="abs h2" style="left:{X0}px;top:160px">What did they get?</div>'
                + col(X0, "35,000+", "incidents mitigated in Microsoft's own services, by its own count", "Microsoft Tech Community · Mar 10, 2026", 1)
                + f'<div class="abs" style="left:960px;top:330px;width:1px;height:330px;background:var(--line2);opacity:{1 if n > 1 else 0}"></div>'
                + col(1040, "11.4%", "of SRE scenarios resolved by agents on state-of-the-art models", "ITBench · ICML 2025 (PMLR 267)", 1 if n > 1 else 0),
                part="2")
steps("B06", [(None, b06(1)), ("But on", b06(2))])

# B07: HolmesGPT (L7 quote)
def b07(n):
    q = ('<div class="abs mono" style="left:96px;top:380px;width:1728px;padding:40px 48px;border:1px solid var(--line2);'
         'border-radius:12px;background:var(--panel2);font-size:30px;line-height:1.5;color:var(--soft)">'
         '<div style="color:var(--dim)">query:</div>'
         '<div>"... <span style="color:var(--text);border-bottom:3px solid var(--amber)">Compare error rates, latency, restarts, and logs</span></div>'
         '<div>before vs after the rollout ..."</div></div>')
    line = (f'<div class="abs sub" style="left:96px;top:660px;width:1728px;font-size:34px;color:var(--text);opacity:{1 if n > 1 else 0}">'
            "In its docs, I didn't find a built-in check that the money is right.</div>")
    return page(f'<div class="abs" style="left:96px;top:150px"><div class="h1">HolmesGPT</div>'
                '<div class="sub" style="margin-top:18px">Open source · a CNCF Sandbox project since October 2025</div></div>'
                + q + line + '<div class="abs src" style="left:96px;top:850px">holmesgpt.dev/latest/operator/deployment-verification'
                ' · an example query from its docs · read 2026-11-20</div>', part="2")
steps("B07", [(None, b07(1)), ("In its docs", b07(2))])

# B08: their signals, our money check (L4 split)
th = RUNB["money_th"]; mt = RUNB["money_table"]
mcrop = (th[0]["x"] - 4, mt["y"] - 4, th[2]["x"] + th[2]["w"] - th[0]["x"] + 12, mt["h"] + 8)
def b08(n):
    chips = "".join(f'<div class="chip" style="left:{X0}px;top:{300 + i * 92}px;width:560px"><span class="dot" style="background:var(--green)"></span>{E(t)}</div>'
                    for i, t in enumerate(("error rates", "latency", "restarts", "logs")))
    left = f'<div class="abs lbl" style="left:{X0}px;top:236px">What its docs compare after a deploy</div>' + chips
    right = ""
    if n > 1:
        body, (ox, oy, w, h) = crop("run_2x", mcrop, (900, 300, 924, 360), [((th[1]["x"] - 2, th[1]["y"], th[1]["w"] + 4, mt["y"] + mt["h"] - th[1]["y"]), "red")], align="left top")
        right = (f'<div class="abs lbl" style="left:900px;top:236px">What Klaxon\'s code checks after a fix: the money</div>' + body)
        if n > 2:
            right += (f'<div class="chip" style="left:900px;top:{oy + h + 40:.0f}px;width:{w:.0f}px;font-size:26px">'
                      '<span class="dot" style="background:var(--amber)"></span>Klaxon changes nothing until a person approves it</div>')
    return page(left + right, part="2", tag="Their deploy check · Klaxon's money check, the week 7 live run")
steps("B08", [(None, b08(1)), ("with the check", b08(2)), ("changes nothing", b08(3))])

# B09: how it works (L8 flat diagram)
def b09(n):
    labels = [("Simulated", "customers"), ("Payments", "API"), ("Fake payment", "provider"), ("Webhook", "receiver"),
              ("Kafka", ""), ("Double-entry", "ledger")]
    arrows = ["pay", "charge", "signed webhook", "event", "book"]
    bw, gap, top, bh = 220, 58, 440, 150
    x = X0 + (W0 - (6 * bw + 5 * gap)) / 2
    svg = [f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">',
           '<defs><marker id="a" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#8B9BB0"/></marker></defs>',
           f'<rect x="{X0}" y="360" width="{W0}" height="330" rx="16" fill="none" stroke="#2A3A4E" stroke-dasharray="8 8"/>',
           f'<text x="{X0 + 28}" y="400" fill="#8B9BB0" font-size="18" letter-spacing="2">DOCKER, ON MY MAC · SYNTHETIC DATA</text>']
    for i, (a, b) in enumerate(labels):
        bx_ = x + i * (bw + gap)
        dash = ' stroke-dasharray="7 6"' if i in (0, 2) else ""
        svg.append(f'<rect x="{bx_:.0f}" y="{top}" width="{bw}" height="{bh}" rx="14" fill="#10171F" stroke="#2A3A4E" stroke-width="2"{dash}/>')
        ty = top + (64 if b else 85)
        svg.append(f'<text x="{bx_ + bw / 2:.0f}" y="{ty}" text-anchor="middle" fill="#E6EDF3" font-size="29" font-weight="600">{E(a)}</text>')
        if b:
            svg.append(f'<text x="{bx_ + bw / 2:.0f}" y="{ty + 38}" text-anchor="middle" fill="#E6EDF3" font-size="29" font-weight="600">{E(b)}</text>')
        if i < 5:
            ax0, ax1, ay = bx_ + bw + 8, bx_ + bw + gap - 10, top + bh / 2
            svg.append(f'<line x1="{ax0:.0f}" y1="{ay:.0f}" x2="{ax1:.0f}" y2="{ay:.0f}" stroke="#8B9BB0" stroke-width="2.5" marker-end="url(#a)"/>')
            svg.append(f'<text x="{(ax0 + ax1) / 2:.0f}" y="{top + bh + 40}" text-anchor="middle" fill="#8B9BB0" font-size="22">{E(arrows[i])}</text>')
    svg.append("</svg>")
    note = ('<div class="abs src" style="left:96px;top:712px">Dashed: simulated (the customers and the provider). '
            'From the README\'s architecture, simplified.</div>')
    faults = (f'<div class="chip" style="left:{X0}px;top:776px;width:860px;opacity:{1 if n > 1 else 0}"><span class="dot" style="background:var(--amber)"></span>'
              'Six faults with known causes, injected on purpose</div>')
    head = (f'<div class="abs" style="left:{X0}px;top:150px"><div class="h1">How it works</div>'
            '<div class="sub" style="margin-top:18px">A small payments system, the patient Klaxon looks after</div></div>')
    return page(head + "".join(svg) + note + faults, part="3")
steps("B09", [(None, b09(1)), ("six faults", b09(2))])

# B10: one step at a time, cited (L2 zoom)
def b10(n):
    if n == 1:
        body, _ = crop("run_2x", bx(RUNB["steps"], 4), (X0, Y0, W0, H0))
        return page(body, part="3", tag="Klaxon's web panel · the week 7 live run · its steps, one tool call at a time")
    ev = RUNB["evidence"]
    body, _ = crop("run_2x", bx(ev, 6), (X0, Y0, W0, H0), [(bx(union(*RUNB["cid"])), "amber")])
    return page(body, part="3", tag="Klaxon's web panel · the week 7 live run · its evidence, each cited by its tool call")
steps("B10", [(None, b10(1)), ("or give a diagnosis", b10(2))])

# B11: the request waiting for him (L3 pan over the screenshot the panel saved during the run)
WS = 1.2
hl_wait = [((911, 853, 438, 41), "amber"), ((913, 929, 350, 23), "amber")]
src11 = ('<img src="%s" style="position:absolute;left:0;top:0;width:1728px">' % SRC["wait"].as_uri()
         + "".join(f'<div class="hl {c}" style="left:{(x - 4) * WS:.0f}px;top:{(y - 3) * WS:.0f}px;width:{(w + 8) * WS:.0f}px;height:{(h + 6) * WS:.0f}px"></div>' for (x, y, w, h), c in hl_wait))
pan("B11", page(src11, clear=True).replace("width:1920px;height:1080px", "width:1728px;height:2880px"), (1728, 2880),
    page(hole(X0, Y0, W0, H0), part="3", tag="Saved by the panel during the run · 2026-11-17, 04:25 UTC · waiting for approval", clear=True),
    (X0, Y0, W0, H0), 0, 880)

# B12: his approval, the rollback, the verification (L4 split)
tl = RUNB["appr_trail_li"]; ap = RUNB["approval"]
acrop = (ap["x"], 1179, ap["w"], tl[-1]["y"] + tl[-1]["h"] + 14 - 1177)
dl = RUNB["deploys_after"]
dcrop = (dl[0]["x"] - 6, dl[0]["y"] - 8, dl[0]["w"] + 12, dl[1]["y"] + dl[1]["h"] + 10 - dl[0]["y"])
def b12(n):
    left, _ = crop("run_2x", acrop, (X0, Y0 + 40, 1000, H0 - 40), [(bx(tl[1]), "amber")])
    right = ""
    if n > 1:
        body, (ox, oy, w, h) = crop("run_2x", dcrop, (1150, Y0 + 40, 674, 300), [], align="left top")
        chips = "".join(f'<div class="chip" style="left:1150px;top:{oy + h + 36 + i * 84:.0f}px;width:674px;font-size:27px">'
                        f'<span class="dot" style="background:var(--{c})"></span>{E(t)}</div>'
                        for i, (t, c) in enumerate((("Healthy: yes", "green"), ("Cause removed: yes", "green"), ("Money right: no", "red"))))
        right = f'<div class="abs lbl" style="left:1150px;top:{Y0 + 4}px">The deploy log, then the check by code</div>' + body + chips
    return page(f'<div class="abs lbl" style="left:{X0}px;top:{Y0 + 4}px">The approval gate\'s trail</div>' + left + right,
                part="3", tag="Klaxon's web panel · the week 7 live run, recorded · approval and verification")
steps("B12", [(None, b12(1)), ("Code then checked", b12(2))])

# B13: CI on GitHub, and what comes next (L9)
def ghcrop(key, hls, extra="", top=110):
    body, _ = crop(key, (0, top * 3 / 4, 1440, 862 * 3 / 4), (X0, Y0, W0, H0), hls)
    return body + extra
def b13(n):
    strip = ""
    if n > 1:
        strip = ('<div class="abs" style="left:96px;top:716px;width:1728px;height:188px;background:rgba(12,18,24,.96);'
                 'border-top:1px solid var(--line2);border-radius:0 0 10px 10px;padding:30px 40px;font-size:27px;line-height:1.6">'
                 '<div><span class="dot" style="background:var(--green)"></span>Built and public: weeks 1 to 7, including a LangGraph loop, Kubernetes, a web panel and CI</div>'
                 '<div><span class="dot" style="background:var(--blue)"></span>Planned by Dec 4: a multi-agent version, the webhook receiver in Go, a 72-run comparison, a safety pass</div></div>')
    return page(ghcrop("gh_ci", [((1150 * 3 / 4, 392 * 3 / 4, 320 * 3 / 4, 66 * 3 / 4), "green")], strip), part="3",
                tag="github.com/AravindKumar2504/klaxon · CI on week 7's review branch, every job passed")
steps("B13", [(None, b13(1)), ("Planned by December", b13(2))])

# B14: do I have what I need (L5 two columns)
HAVE = ["Claude through my university seat, with Claude Code in headless mode", "Docker Desktop and kind (Kubernetes) on my Mac",
        "GitHub Actions, free for public repositories"]
LIMITS = ["No API key and no token credits", "Seat usage limits: big batches run overnight",
          "Dollar figures: Claude Code's estimates at API prices, not money spent"]
def b14(nl, nr):
    col = lambda x, title, color, items, k: (f'<div class="abs" style="left:{x}px;top:300px;width:780px">'
                                             f'<div class="lbl" style="color:var(--{color})">{E(title)}</div>'
                                             + "".join(f'<div style="margin-top:26px;font-size:30px;line-height:1.35;opacity:{1 if i < k else 0}">{E(t)}</div>' for i, t in enumerate(items))
                                             + "</div>")
    return page(f'<div class="abs h1" style="left:{X0}px;top:150px">Do I have what I need?</div>'
                + col(X0, "What I have", "green", HAVE, nl) + f'<div class="abs" style="left:960px;top:300px;width:1px;height:440px;background:var(--line2)"></div>'
                + col(1040, "Its limits", "amber", LIMITS, nr), part="3")
steps("B14", [(None, b14(1, 1)), ("It isn't billed", b14(1, 2)), ("Dollar figures", b14(1, 3)), ("Compute is", b14(3, 3))])

# B15: his part, from the public commits (L9)
def b15(k):
    hl = [((184 * 3 / 4, 462 * 3 / 4, 440 * 3 / 4, 44 * 3 / 4), "amber")] if k == 1 else [((184 * 3 / 4, 924 * 3 / 4, 766 * 3 / 4, 42 * 3 / 4), "amber")]
    return page(ghcrop("gh_commits", hl, top=250), part="3", tag="github.com/AravindKumar2504/klaxon · the public commit history")
steps("B15", [(None, b15(1)), ("typed every approval", b15(2))])

# B16: the eight cases (L10 terminal card)
lines = (CAP / "eval-cases-card.txt").read_text().rstrip("\n").split("\n")
def b16(n):
    shown = lines[:n]
    rows = []
    for t in shown:
        if t.startswith("  action that fits:"):
            rows.append(f'<div style="color:var(--muted);padding-left:2ch">action that fits: <span style="color:var(--soft)">{E(t.split(":", 1)[1].strip())}</span></div>')
        else:
            name, rest = t.split(" ", 1)
            rows.append(f'<div><span style="color:var(--blue);font-weight:600">{E(name)}</span> <span style="color:var(--text)">{E(rest)}</span></div>')
    term = (f'<div class="abs" style="left:{X0}px;top:236px;width:{W0}px;height:668px;border:1px solid var(--line2);border-radius:12px;background:#07090C;overflow:hidden">'
            '<div style="height:44px;border-bottom:1px solid var(--line);background:#0D131A;position:relative">'
            + "".join(f'<span style="position:absolute;top:15px;left:{18 + i * 22}px;width:13px;height:13px;border-radius:50%;background:{c}"></span>' for i, c in enumerate(("#F85149", "#E3B341", "#3FB950")))
            + '<span class="mono" style="position:absolute;left:0;width:100%;text-align:center;top:11px;font-size:16px;color:var(--dim)">Terminal · a copy of Klaxon at fef450b · calls nothing</span></div>'
            '<div class="mono" style="padding:22px 30px;font-size:21px;line-height:1.5">'
            '<div><span style="color:var(--green)">$</span> make eval-cases | grep -E \'^[a-z]|action that fits\'</div>'
            + "".join(rows) + "</div></div>")
    return page(f'<div class="abs h2" style="left:{X0}px;top:148px">Eight test cases, each with its right answer written before any run</div>' + term,
                part="4")
steps("B16", [(None, b16(4)), ("the six faults", b16(12)), ("a false alarm", b16(16))])

# B17: the evaluation report, a slow scroll (L2, pan)
oth = EVB["opus_th"]
hx0, hx1 = oth[4]["x"], oth[9]["x"] + oth[9]["w"]
src17_w = int(1366 * 1.2)
src17 = (f'<img src="{SRC["eval_1.2x"].as_uri()}" style="position:absolute;left:0;top:0;width:1728px">'
         f'<div class="hl" style="left:{hx0 * 1.2 - 6:.0f}px;top:{oth[4]["y"] * 1.2 - 6:.0f}px;width:{(hx1 - hx0) * 1.2 + 12:.0f}px;height:{oth[4]["h"] * 1.2 + 12:.0f}px"></div>')
EVX = X0 + (W0 - src17_w) // 2
pan("B17", page(src17, clear=True).replace("width:1920px;height:1080px", f"width:{src17_w}px;height:6485px"), (src17_w, 6485),
    page(hole(EVX, Y0, src17_w, H0), part="4", tag="Klaxon's web panel · the evaluation report, week 5 · graders shown", clear=True),
    (EVX, Y0, src17_w, H0), 650, 900)

# B18: the fault rows (L3 zoom)
orow = EVB["opus_rows"]
tcrop = (oth[0]["x"] - 4, oth[0]["y"] - 4, oth[9]["x"] + oth[9]["w"] - oth[0]["x"] + 8, orow[5]["y"] + orow[5]["h"] - oth[0]["y"] + 6)
def b18(k):
    if k == 1:
        hl = {"x": oth[4]["x"], "y": orow[0]["y"], "w": oth[5]["x"] + oth[5]["w"] - oth[4]["x"], "h": orow[5]["y"] + orow[5]["h"] - orow[0]["y"]}
    else:
        hl = {"x": oth[9]["x"], "y": orow[0]["y"], "w": oth[9]["w"], "h": orow[5]["y"] + orow[5]["h"] - orow[0]["y"]}
    body, _ = crop("eval_2x", tcrop, (X0, Y0, W0, H0), [(bx(hl), "amber")])
    return page(body, part="4", tag="The evaluation report, week 5 · claude-opus-5-5 · the six faults")
steps("B18", [(None, b18(1)), ("No run named", b18(2))])

# B19: the false alarm (L4 split)
srow = EVB["sonnet_rows"]; sth = EVB["sonnet_th"]
fa_o = [r for r in orow if r["case"] == "false-alarm"][0]; fa_s = [r for r in srow if r["case"] == "false-alarm"][0]
cx0, cx1 = oth[0]["x"] - 4, oth[8]["x"] + oth[8]["w"] + 4
COLS19 = [(oth[0]["x"], oth[0]["x"] + oth[0]["w"]), (oth[4]["x"], oth[5]["x"] + oth[5]["w"]), (oth[8]["x"], oth[8]["x"] + oth[8]["w"])]
def strip3(label, th0, row, y, hl_idx, color):
    sc, gap = 2.0, 20
    x = X0 + 24; hh, rh = th0["h"] * sc, row["h"] * sc
    parts, hls = [], ""
    for i, (c0, c1) in enumerate(COLS19):
        w = (c1 - c0) * sc
        h1, _ = crop("eval_2x", (c0, th0["y"], c1 - c0, th0["h"]), (x, y + 56, w, hh), [], align="left top", bare=True)
        h2, _ = crop("eval_2x", (c0, row["y"], c1 - c0, row["h"]), (x, y + 56 + hh, w, rh), [], align="left top", bare=True)
        parts.append(h1 + h2)
        if i == hl_idx:
            hls = f'<div class="hl {color}" style="left:{x - 6:.1f}px;top:{y + 56 + hh - 4:.1f}px;width:{w + 12:.1f}px;height:{rh + 8:.1f}px"></div>'
        if i < len(COLS19) - 1:
            parts.append(f'<div class="abs" style="left:{x + w + gap / 2:.1f}px;top:{y + 56:.1f}px;width:1px;height:{hh + rh:.1f}px;background:var(--line2)"></div>')
        x += w + gap
    box = (f'<div class="abs" style="left:{X0}px;top:{y + 40}px;width:{x - X0 + 4:.0f}px;height:{hh + rh + 32:.0f}px;border:1px solid var(--line2);'
           'border-radius:10px;background:var(--panel)"></div>')
    return f'<div class="abs lbl" style="left:{X0}px;top:{y}px">{E(label)}</div>' + box + "".join(parts) + hls
def strip(label, th0, row, y, col):
    hdr, (ox, oy, w, h) = crop("eval_2x", (cx0, th0["y"] - 2, cx1 - cx0, th0["h"] + 4), (X0, y + 40, 1180, 60), [], align="left top")
    s = w / ((cx1 - cx0) * 2)
    rowh = (row["h"] + 4) * 2 * s
    body, _ = crop("eval_2x", (cx0, row["y"] - 2, cx1 - cx0, row["h"] + 4), (X0, oy + h - 1, 1180, rowh), [], align="left top")
    hls = ""
    if col:
        for c0, c1, color in col:
            x = X0 + (c0 - cx0) * 2 * s - 5; ww_ = (c1 - c0) * 2 * s + 10
            hls += f'<div class="hl {color}" style="left:{x:.1f}px;top:{oy + h - 6:.1f}px;width:{ww_:.1f}px;height:{rowh + 10:.1f}px"></div>'
    return f'<div class="abs lbl" style="left:{X0}px;top:{y}px">{E(label)}</div>' + hdr + body + hls
def b19(k):
    if k == 1:
        cols = [(oth[8]["x"], oth[8]["x"] + oth[8]["w"], "green")]
    else:
        cols = [(oth[4]["x"], oth[5]["x"] + oth[5]["w"], "amber")]
    idx, color = (2, "green") if k == 1 else (1, "amber")
    left = (strip3("claude-opus-5-5 · false alarm · three of the report's columns", oth[0], fa_o, Y0 + 6, idx, color)
            + strip3("claude-sonnet-5-5 · false alarm · three of the report's columns", sth[0], fa_s, Y0 + 380, idx, color))
    notes = [("green", "No action named", "on any of the six false-alarm runs"),
             ("amber", "1 run in 6", "said plainly that nothing was wrong, by each grader"),
             ("dim", "Every fault was known", "while Klaxon was built: not yet a test on unseen faults")]
    right = "".join(f'<div class="abs" style="left:1340px;top:{Y0 + 20 + i * 200}px;width:484px;opacity:{1 if i < k else 0}">'
                    f'<div style="font-size:30px;font-weight:650"><span class="dot" style="background:var(--{c})"></span>{E(a)}</div>'
                    f'<div class="sub" style="font-size:25px;margin-top:10px;padding-left:30px">{E(b)}</div></div>' for i, (c, a, b) in enumerate(notes))
    return page(left + right, part="4", tag="The evaluation report, week 5 · the false alarm on both models")
steps("B19", [(None, b19(1)), ("but each grader", b19(2)), ("And every fault", b19(3))])

# B20: works if / fails if, and the end (L11)
def b20(n):
    works = ["The 72 comparison runs keep naming the causes, with no wrong actions", "The false alarm gets called false",
             "Code keeps catching every fix that leaves the money wrong"]
    fails = ["A confident wrong cause", "An action where none fits"]
    col = lambda x, title, color, items, op: (f'<div class="abs" style="left:{x}px;top:200px;width:780px;opacity:{op}">'
                                              f'<div class="lbl" style="color:var(--{color})">{E(title)}</div>'
                                              + "".join(f'<div style="margin-top:24px;font-size:31px;line-height:1.35">{E(t)}</div>' for t in items) + "</div>")
    end = (f'<div class="abs" style="left:{X0}px;top:690px;width:{W0}px;border-top:1px solid var(--line2);padding-top:40px;opacity:{1 if n > 2 else 0}">'
           '<span style="font-size:44px;font-weight:700">Klaxon</span><span style="font-size:30px;color:var(--soft);margin-left:24px">Aravind Sundaravadivelu</span>'
           '<span class="src" style="float:right;margin-top:14px;font-size:20px">github.com/AravindKumar2504/klaxon</span></div>')
    return page(col(X0, "It works if", "green", works, 1) + f'<div class="abs" style="left:960px;top:200px;width:1px;height:400px;background:var(--line2)"></div>'
                + col(1040, "It fails if", "red", fails, 1 if n > 1 else 0) + end, part="4")
steps("B20", [(None, b20(1)), ("It fails on", b20(2)), ("Klaxon, by", b20(3))])

# B21: the appendix, silent (L12)
SOURCES = [("Klaxon's records", "github.com/AravindKumar2504/klaxon at fef450b: README, docs/STATUS.md, evidence/week5/report.md, the week 7 live run"),
           ("Resolve AI", "TechCrunch, Feb 4, 2026"), ("Traversal", "Goodwin, Nov 4, 2026"),
           ("Datadog, AWS, Microsoft", "their announcements of Dec 2, 2025; Mar 31, 2026; Mar 10, 2026"),
           ("ITBench", "Jha et al., ICML 2025, PMLR 267"),
           ("HolmesGPT", "CNCF blog, Jan 7, 2026; holmesgpt.dev, deployment verification (read Nov 20, 2026)"),
           ("AI use", "Claude Code drafted the script from the project's records, checked every claim and built this film; the voice is Kokoro (am_onyx)")]
steps("B21", [(None, page(f'<div class="abs h2" style="left:{X0}px;top:140px">Appendix: sources</div>'
                          + "".join(f'<div class="abs" style="left:{X0}px;top:{240 + i * 84}px;width:{W0}px;font-size:24px;line-height:1.4">'
                                    f'<span style="font-weight:650">{E(a)}</span><span style="color:var(--soft)"> · {E(b)}</span></div>' for i, (a, b) in enumerate(SOURCES)),
                          part="A"))])

def check_text(doc):
    assert "\u2014" not in doc, "em dash on screen"

with sync_playwright() as p:
    br = p.chromium.launch(channel="chromium", headless=True)
    for beat, plan in PLAN.items():
        if plan["kind"] == "steps":
            pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
            for st in plan["steps"]:
                name = Path(st["png"]).stem
                check_text((CARDS / f"{name}.html").read_text())
                pg.goto((CARDS / f"{name}.html").as_uri(), wait_until="load"); pg.wait_for_timeout(150)
                pg.screenshot(path=str(B / st["png"]))
            pg.close()
        else:
            w, h = plan["src_size"]
            pg = br.new_page(viewport={"width": w, "height": 1080}, device_scale_factor=1)
            pg.goto((CARDS / f"{beat}_src.html").as_uri(), wait_until="load"); pg.wait_for_timeout(200)
            pg.screenshot(path=str(B / plan["src"]), full_page=True, omit_background=True)
            pg.close()
            pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
            check_text((CARDS / f"{beat}_overlay.html").read_text())
            pg.goto((CARDS / f"{beat}_overlay.html").as_uri(), wait_until="load"); pg.wait_for_timeout(150)
            pg.screenshot(path=str(B / plan["overlay"]), omit_background=True)
            pg.close()
        print("rendered", beat, plan["kind"], flush=True)
    br.close()

for beat, plan in PLAN.items():
    plan["audio"] = DUR.get(beat, 0.0)
    plan["frames"] = round(((LEAD + DUR[beat] + TAIL) if beat in DUR else 4.0) * FPS)
(OUT / "plan.json").write_text(json.dumps(PLAN, indent=1))
print("plan written:", len(PLAN), "beats")
