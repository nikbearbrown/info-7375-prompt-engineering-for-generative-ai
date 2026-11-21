"""Capture the film's real footage with headless Chromium (Playwright): Klaxon's panel served from a scratch copy of
fef450b on 127.0.0.1:8091 (it only reads evidence/), and two public GitHub pages, signed out.
Writes PNGs and element boxes (CSS px) to build/capture/. Run with $PW_PY (a Python with Playwright and its Chromium)."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "capture"
OUT.mkdir(exist_ok=True)
PANEL = "http://127.0.0.1:8091"
RUN = "2026-11-17T042300Z_gated-run_duplicate-delivery"

BOXES_JS = """(sels) => { const out = {};
  for (const [name, sel, text] of sels) {
    let els = [...document.querySelectorAll(sel)];
    if (text) els = els.filter(e => e.textContent.includes(text));
    const e = els[0]; if (!e) { out[name] = null; continue; }
    const r = e.getBoundingClientRect();
    out[name] = {x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height}; }
  out._page = {w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight};
  return out; }"""

def shoot(page, url, name, sels=(), full=True):
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(600)
    boxes = page.evaluate(BOXES_JS, [list(s) for s in sels])
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
    (OUT / f"{name}.json").write_text(json.dumps(boxes, indent=1))
    print(name, boxes.get("_page"), {k: (v and round(v["y"])) for k, v in boxes.items() if k != "_page"})

with sync_playwright() as p:
    b = p.chromium.launch(channel="chromium", headless=True)
    # Full-frame footage: 1440 CSS px wide at 1.2 = 1728 px, the frame's footage window.
    ctx = b.new_context(viewport={"width": 1440, "height": 650}, device_scale_factor=1.2, color_scheme="dark")
    pg = ctx.new_page()
    shoot(pg, f"{PANEL}/runs", "runs_1.2x", [("table", "table", None), ("first_row", "tbody tr", None)])
    shoot(pg, f"{PANEL}/evaluation?from=week5&graders=shown", "eval_1.2x",
          [("opus_h", "h3", "claude-opus-5-5"), ("opus_table", "table", "duplicate-delivery")])
    ctx.close()
    # Crops: the same pages at device scale 2, with the boxes of the parts the film zooms into.
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, color_scheme="dark")
    pg = ctx.new_page()
    shoot(pg, f"{PANEL}/run/{RUN}", "run_2x", [
        ("alert", "section.card.ihead", None), ("signals", "section.card", "Signals at the alert"),
        ("bad_tile", ".tile.bad", None), ("alert_sentence", "div.card.ihead p", "ahead of"),
        ("diagnosis", "section.card", "Diagnosis"), ("steps", "section.card", "Stopped: diagnosed"),
        ("evidence", ".evidence", None), ("approval", "section.card.appr", None), ("trail", ".trail", None),
        ("verification", "section.card", "Verdict:"), ("money_table", "section.card table", "at the alert"),
        ("not_right", "section.card li", "The money is not right")])
    shoot(pg, f"{PANEL}/evaluation?from=week5&graders=shown", "eval_2x", [
        ("opus_table", "table", "duplicate-delivery"), ("opus_total", "p", "191 model calls"),
        ("sonnet_h", "h3", "claude-sonnet-5-5"), ("fa_opus", "tr", "false-alarm")])
    ctx.close()
    # GitHub, signed out: 1440 CSS px at 4/3 = a 1920 px frame.
    ctx = b.new_context(viewport={"width": 1440, "height": 810}, device_scale_factor=4 / 3, color_scheme="dark")
    pg = ctx.new_page()
    shoot(pg, "https://github.com/AravindKumar2504/klaxon/actions/runs/44037113149", "gh_ci", full=False)
    shoot(pg, "https://github.com/AravindKumar2504/klaxon/commits/main", "gh_commits", full=True)
    shoot(pg, "https://github.com/AravindKumar2504/klaxon", "gh_repo", full=False)
    ctx.close(); b.close()
