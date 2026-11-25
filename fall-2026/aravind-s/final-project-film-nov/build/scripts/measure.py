"""Boxes (CSS px, page coordinates) of the parts of the panel's pages the film crops and highlights, measured on the
live panel (scratch copy of fef450b on 127.0.0.1:8091) at the capture's viewport (1440 CSS px wide). Writes
build/capture/boxes.json. Run with $PW_PY (a Python with Playwright and its Chromium)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "capture" / "boxes.json"
RUN = "http://127.0.0.1:8091/run/2026-11-17T042300Z_gated-run_duplicate-delivery"
EVAL = "http://127.0.0.1:8091/evaluation?from=week5&graders=shown"
JS_RUN = """() => {
 const R = e => { if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height}; };
 const card = t => [...document.querySelectorAll('section.card')].find(e => e.textContent.includes(t));
 const sig = card('Signals at the alert'), ver = card('Verdict:'), appr = document.querySelector('section.card.appr'),
       steps = card('Stopped: diagnosed'), diag = card('Diagnosis');
 const out = {signals: R(sig), bad_tile: R(sig.querySelector('.tile.bad')), tiles: R(sig.querySelector('.tiles'))};
 const ps = [...sig.querySelectorAll('p')]; out.signals_sentence = R(ps.find(p => p.textContent.includes('ahead of')));
 out.verification = R(ver); out.ver_li = [...ver.querySelectorAll('li')].slice(0, 3).map(R);
 const vt = ver.querySelector('table'); out.money_table = R(vt); out.money_th = [...vt.querySelectorAll('th')].map(R);
 out.money_wrap = R(vt.parentElement);
 const lbls = [...ver.querySelectorAll('*')].filter(e => e.children.length === 0 && /Deploys during the run/i.test(e.textContent));
 out.deploys_label = R(lbls[0]);
 out.deploys_block = R(lbls[0] && lbls[0].nextElementSibling);
 out.deploys_after = lbls[0] ? [...lbls[0].parentElement.children].slice([...lbls[0].parentElement.children].indexOf(lbls[0])).map(R) : [];
 out.approval = R(appr); out.appr_trail = R(appr.querySelector('.trail')); out.appr_trail_li = [...appr.querySelectorAll('.trail li')].map(R);
 out.appr_kv = [...appr.querySelectorAll('.kv, .kv > *')].slice(0, 12).map(R);
 out.steps = R(steps); out.evidence = R(diag.querySelector('.evidence')); out.evidence_li = [...diag.querySelectorAll('.evidence > li')].map(R);
 out.cid = [...diag.querySelectorAll('.evidence .cid')].map(R);
 out.page = {w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight};
 return out; }"""
JS_EVAL = """() => {
 const R = e => { if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height}; };
 const tables = [...document.querySelectorAll('table')].filter(t => t.querySelector('th') && t.querySelector('th').textContent.trim() === 'Case');
 const out = {n_tables: tables.length};
 tables.slice(0, 2).forEach((t, i) => { const k = i === 0 ? 'opus' : 'sonnet';
   out[k] = R(t); out[k + '_wrap'] = R(t.parentElement); out[k + '_th'] = [...t.querySelectorAll('thead th, tr:first-child th')].map(e => ({...R(e), text: e.textContent.trim()}));
   out[k + '_rows'] = [...t.querySelectorAll('tbody tr')].map(e => ({...R(e), case: e.querySelector('td') && e.querySelector('td').textContent.trim()})); });
 const h = [...document.querySelectorAll('h3')]; out.opus_h = R(h.find(e => e.textContent.includes('claude-opus-5-5')));
 out.sonnet_h = R(h.find(e => e.textContent.includes('claude-sonnet-5-5')));
 out.opus_total = R([...document.querySelectorAll('p')].find(p => p.textContent.includes('191 model calls')));
 out.page = {w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight};
 return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="chromium", headless=True)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2, color_scheme="dark")
    pg.goto(RUN, wait_until="networkidle"); run = pg.evaluate(JS_RUN)
    pg.goto(EVAL, wait_until="networkidle"); ev = pg.evaluate(JS_EVAL)
    b.close()
OUT.write_text(json.dumps({"run": run, "eval": ev}, indent=1))
r = lambda d: d and {k: round(v) for k, v in d.items() if isinstance(v, (int, float))}
print("signals_sentence", r(run["signals_sentence"]), "ver_li", [r(x) for x in run["ver_li"]])
print("money_th", [(r(x)["x"], r(x)["w"]) for x in run["money_th"]], "wrap", r(run["money_wrap"]))
print("deploys_label", r(run["deploys_label"]), "after", [r(x) for x in run["deploys_after"]][:4])
print("appr_trail_li", [r(x) for x in run["appr_trail_li"]])
print("cid", [r(x) for x in run["cid"]], "evidence", r(run["evidence"]), "steps", r(run["steps"]))
print("eval tables", ev["n_tables"], "opus", r(ev["opus"]), "opus_wrap", r(ev["opus_wrap"]))
print("opus_th", [(x["text"][:14], round(x["x"]), round(x["w"])) for x in ev["opus_th"]])
print("opus_rows", [(x["case"], round(x["y"]), round(x["h"])) for x in ev["opus_rows"]])
print("sonnet_rows", [(x["case"], round(x["y"]), round(x["h"])) for x in ev["sonnet_rows"]][-3:], "sonnet_th y", round(ev["sonnet_th"][0]["y"]))
