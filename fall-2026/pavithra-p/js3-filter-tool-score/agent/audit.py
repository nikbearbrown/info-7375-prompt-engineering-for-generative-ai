"""The reject audit (FILTER.md; JS3 brief, Step 2): draw the sample, build the blind labelling page, score my labels.

The sample is drawn with a fixed seed from one filter run, before any label exists, and saved. The labelling page shows
no verdict, score or set name, so my labels are blind to the filter. The held-out set is used only in SCORE-REPORT.md.
"""
import csv
import html
import io
import json
import math
import random
import re

from . import filter as filt
from . import rule

SEED = 20261125
N_RANDOM_REJECTS = 30
N_GATE_CLOSE = 6
N_HELD_OUT = 20


def key(d):
    return f"{d['board']}:{d['job_id']}"


def failed_gates(d):
    return [n for n, g in d["gates"].items() if not g["passed"]]


def draw_sample(decisions, threshold, seed=SEED):
    """decisions: dicts from decisions.jsonl. Returns {set name: [keys]} plus the order of the labelling sheet."""
    rng = random.Random(seed)
    by_key = {key(d): d for d in decisions}
    ordered = sorted(by_key)  # a fixed order before sampling, so the same seed always gives the same sample
    kept = [k for k in ordered if by_key[k]["verdict"] == filt.KEEP]
    close = [k for k in ordered if by_key[k]["close_call"]]
    gate_close = [k for k in ordered if by_key[k]["verdict"] == filt.REJECT and len(failed_gates(by_key[k])) == 1
                  and by_key[k]["score"] >= threshold]
    rejects = [k for k in ordered if by_key[k]["verdict"] == filt.REJECT and k not in close]
    sets = {"random_rejects": rng.sample(rejects, N_RANDOM_REJECTS)}
    sets["close_calls"] = close
    sets["kept"] = kept
    taken = set(sets["random_rejects"]) | set(close) | set(kept)
    sets["gate_close_calls"] = rng.sample([k for k in gate_close if k not in taken], N_GATE_CLOSE)
    taken |= set(sets["gate_close_calls"])
    pool = [k for k in ordered if k not in taken and by_key[k]["gates"] and by_key[k]["gates"]["G1 location"]["passed"]
            and rule.find_words(by_key[k]["title"], ("Engineer", "Developer"))]
    sets["held_out"] = rng.sample(pool, N_HELD_OUT)
    sheet = list(dict.fromkeys(k for name in sets for k in sets[name]))
    rng.shuffle(sheet)
    return {"seed": seed, "sizes": {n: len(v) for n, v in sets.items()}, "held_out_pool": len(pool),
            "sets": sets, "sheet_order": sheet}


def plain(job):
    return re.sub(r"\s+", " ", rule.description_text(job)).strip()


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JS3 hand labels</title><style>
:root{--bg:#fafaf7;--fg:#1d1d1b;--mut:#6b6b66;--line:#ddd;--yes:#1f7a4d;--no:#a33;--ct:#555}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,sans-serif;margin:0 auto;max-width:900px;padding:16px}
.card{border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:12px 0;background:#fff}
.card.done{opacity:.55}.y{font-size:13px;margin-top:4px;background:#f3f1ea;border-radius:6px;padding:4px 8px}.t{font-weight:600;font-size:16px}.m{color:var(--mut);font-size:13px}
details{margin:6px 0}summary{cursor:pointer;color:var(--mut)}.d{white-space:pre-wrap;font-size:13px;max-height:340px;overflow:auto;border-top:1px solid var(--line);padding-top:6px}
.btns button{margin-right:6px;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer;font-size:14px}
.btns button.on[data-v=yes]{background:var(--yes);color:#fff}.btns button.on[data-v=no]{background:var(--no);color:#fff}
.btns button.on[data-v="cannot tell"]{background:var(--ct);color:#fff}
input.note{width:100%;box-sizing:border-box;margin-top:6px;padding:5px;border:1px solid var(--line);border-radius:6px}
#bar{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:2}
#bar button{padding:7px 14px;font-size:14px}
</style></head><body>
<div id="bar"><b>JS3 hand labels</b> · <span id="n"></span> · <button id="dl">Download hand-labels.csv</button></div>
<p>Candidate (fictional): Rohan Mehta. MS in Information Systems, Northeastern, 2026. About two years as a software
engineer (Java services for a bank) plus a five-month co-op (TypeScript, MSSQL, Redis, an AI workflow over logs).
Skills: TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm,
Fluent Bit, Jenkins. Lives in Boston, looking for backend, platform or full-stack software roles in the US.</p>
<p>For each posting: <b>yes</b> = worth Rohan's time to apply · <b>no</b> = not worth it · <b>cannot tell</b> = the posting
does not say enough to decide. Add a short note when it was a hard call. Your choices are kept in this browser if you
reload; press Download when you finish.</p>
<div id="rows"></div>
<script>
const ROWS=__ROWS__;const KEY="js3-hand-labels-v1";let L={};try{L=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(L))}catch(e){}count()}
function count(){const n=ROWS.filter(r=>L[r.key]&&L[r.key].label).length;document.getElementById("n").textContent=n+" of "+ROWS.length+" labelled"}
const box=document.getElementById("rows");
ROWS.forEach((r,i)=>{const c=document.createElement("div");c.className="card";
c.innerHTML=`<div class="t">${i+1}. ${r.title}</div><div class="m">${r.board} · ${r.location} · <a href="${r.url}" target="_blank" rel="noopener">posting</a></div>
<div class="y"></div>
<details><summary>Description (${r.words} words)</summary><div class="d"></div></details>
<div class="btns"><button data-v="yes">yes</button><button data-v="no">no</button><button data-v="cannot tell">cannot tell</button></div>
<input class="note" placeholder="note (optional)">`;
c.querySelector(".d").textContent=r.text;
const y=c.querySelector(".y");y.textContent=r.years.length?"Years in the posting: "+r.years.map(t=>"\u201c"+t+"\u201d").join("  "):"Years in the posting: none stated";const note=c.querySelector(".note");
const cur=L[r.key]||{};note.value=cur.note||"";
function paint(){c.querySelectorAll("button").forEach(b=>b.classList.toggle("on",(L[r.key]||{}).label===b.dataset.v));c.classList.toggle("done",!!(L[r.key]||{}).label)}
c.querySelectorAll("button").forEach(b=>b.onclick=()=>{L[r.key]=Object.assign(L[r.key]||{}, {label:b.dataset.v,at:new Date().toISOString()});save();paint()});
note.oninput=()=>{L[r.key]=Object.assign(L[r.key]||{}, {note:note.value});save()};paint();box.appendChild(c)});
count();
document.getElementById("dl").onclick=()=>{const q=s=>'"'+String(s||"").replace(/"/g,'""')+'"';
const lines=["row,key,title,label,note,labelled_at"].concat(ROWS.map((r,i)=>[i+1,q(r.key),q(r.title),q((L[r.key]||{}).label),q((L[r.key]||{}).note),q((L[r.key]||{}).at)].join(",")));
const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([lines.join("\\n")+"\\n"],{type:"text/csv"}));a.download="hand-labels.csv";a.click()};
</script></body></html>
"""


YEARS_ASKED = re.compile(r"\b\d+(?:\.\d+)?\s*(?:\+|-|–|—|to)?\s*(?:\d+\s*)?\+?\s*years?\b", re.IGNORECASE)


def year_sentences(text, limit=3, before=110, after=70):
    """The posting's own words around each "N years", word for word (a reading aid, not a verdict)."""
    out = []
    for m in YEARS_ASKED.finditer(text):
        start, end = max(0, m.start() - before), min(len(text), m.end() + after)
        start = text.rfind(" ", 0, start) + 1 if start else 0
        end = text.find(" ", end) if text.find(" ", end) != -1 else len(text)
        snippet = ("..." if start else "") + text[start:end].strip() + ("..." if end < len(text) else "")
        if not any(m.group(0) in o and o[-40:] == snippet[-40:] for o in out):
            out.append(snippet)
        if len(out) == limit:
            break
    return out


def label_page(sample, jobs_by_key, decisions_by_key):
    rows = []
    for k in sample["sheet_order"]:
        job, d = jobs_by_key[k], decisions_by_key[k]
        text = plain(job)
        rows.append({"key": k, "title": html.escape(d["title"].strip()), "board": d["board"],
                     "location": html.escape(d["location"]), "url": html.escape(d["url"]), "text": text,
                     "words": len(text.split()), "years": year_sentences(text)})
    return PAGE.replace("__ROWS__", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/"))


def read_labels(text):
    """hand-labels.csv from the page: {key: (label, note)}. A row with no label is left out, not guessed."""
    out = {}
    for row in csv.DictReader(io.StringIO(text)):
        label = (row.get("label") or "").strip()
        if label:
            if label not in ("yes", "no", "cannot tell"):
                raise ValueError(f"row {row['row']}: unknown label {label!r}")
            out[row["key"]] = (label, (row.get("note") or "").strip())
    return out


def wilson(k, n, z=1.96):
    """95% Wilson interval for k errors in n judged postings; for k = 0 it agrees closely with the rule of three."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def is_error(verdict, label):
    """A filter mistake by my hand label: a reject (or cannot tell) I said yes to, or a keep I said no to."""
    return (label == "yes" and verdict != filt.KEEP) or (label == "no" and verdict == filt.KEEP)


def pct(lo_hi):
    return f"{lo_hi[0] * 100:.0f}% to {lo_hi[1] * 100:.0f}%"


def audit_report(sample, by_key, labels):
    """Tables for AUDIT.md from the tuning sets only. The held-out set is never read here."""
    lines = []
    for name in ("random_rejects", "close_calls", "kept", "gate_close_calls"):
        keys = sample["sets"][name]
        rows = [(k, by_key[k], labels.get(k)) for k in keys]
        judged = [(k, d, lab) for k, d, lab in rows if lab and lab[0] != "cannot tell"]
        errors = [(k, d, lab) for k, d, lab in judged if is_error(d["verdict"], lab[0])]
        unlabelled = [k for k, _, lab in rows if not lab]
        cannot = [k for k, _, lab in rows if lab and lab[0] == "cannot tell"]
        lines += [f"## {name.replace('_', ' ')}", "",
                  f"{len(keys)} postings · labelled {len(keys) - len(unlabelled)} · my 'cannot tell' {len(cannot)} · "
                  f"filter wrong by my label: {len(errors)} of {len(judged)}"
                  + (f" (95% Wilson interval {pct(wilson(len(errors), len(judged)))})" if judged else ""), "",
                  "| # | Board | Title | Filter | Score | My label | Note | Filter's reason |", "|---|---|---|---|---|---|---|---|"]
        for i, (k, d, lab) in enumerate(rows, 1):
            mark = " (wrong)" if lab and is_error(d["verdict"], lab[0]) else ""
            lines.append(f"| {i} | {d['board']} | {d['title'].strip()} | {d['verdict']}{mark} | {d['score']} | "
                         f"{lab[0] if lab else '(none)'} | {(lab[1] if lab else '').replace('|', '/')} | "
                         f"{d['reason'].replace('|', '/')} |")
        lines.append("")
    return "\n".join(lines)


def measure(specs, keys, jobs, persona, labels, decide=filt.decide):
    """One row per filter file on the held-out keys: agreement with my labels, false keeps, false rejects."""
    rows = []
    judged = [k for k in keys if labels.get(k) and labels[k][0] != "cannot tell"]
    for path, spec in specs:
        verdicts = {k: decide(jobs[k][1], jobs[k][0], persona, spec).verdict for k in keys}
        fk = [k for k in judged if labels[k][0] == "no" and verdicts[k] == filt.KEEP]
        fr = [k for k in judged if labels[k][0] == "yes" and verdicts[k] != filt.KEEP]
        agree = len(judged) - len(fk) - len(fr)
        rows.append({"filter": path, "version": spec["version"], "judged": len(judged), "agree": agree,
                     "false_keeps": fk, "false_rejects": fr, "kept": sum(v == filt.KEEP for v in verdicts.values()),
                     "interval": wilson(agree, len(judged))})
    return rows
