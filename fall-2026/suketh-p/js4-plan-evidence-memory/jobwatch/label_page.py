"""An offline page for the student's hand labels. It shows each posting's saved title, location and
text, and never its score, fate or sample group. Labels stay in the browser until the student
downloads them as JSON."""

import html
import json

from jobwatch.normalize import plain_text

COMPANY = {"greenhouse/anthropic": "Anthropic", "greenhouse/databricks": "Databricks", "ashby/linear": "Linear"}

_STYLE = """
:root { --bg:#fbfaf7; --fg:#1d1d1b; --muted:#5d5b55; --card:#ffffff; --line:#d9d5cc; --accent:#1f5fbf; --done:#e9f3e6; }
@media (prefers-color-scheme: dark) { :root { --bg:#161614; --fg:#ecebe6; --muted:#a9a69d; --card:#20201d;
  --line:#3a3833; --accent:#7fb0ff; --done:#1f2b1c; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 -apple-system, "Segoe UI", sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 16px; }
header { position: sticky; top: 0; background: var(--bg); border-bottom: 1px solid var(--line); padding: 10px 16px; z-index: 2; }
header .row { max-width: 860px; margin: 0 auto; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
button { font: inherit; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--card); color: var(--fg); cursor: pointer; }
button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; margin: 14px 0; }
.card.done { background: var(--done); }
.id { font-weight: 700; color: var(--muted); }
h2 { font-size: 1.1rem; margin: 4px 0; }
.meta { color: var(--muted); font-size: 0.92rem; }
.text { white-space: pre-wrap; font-size: 0.92rem; max-height: 14em; overflow: hidden; border-left: 3px solid var(--line); padding-left: 10px; margin: 10px 0; }
.text.open { max-height: none; }
.choices { display:flex; gap: 16px; flex-wrap: wrap; margin: 8px 0; }
.choices label { cursor: pointer; }
input[type=text] { width: 100%; font: inherit; padding: 6px 8px; border-radius: 6px; border: 1px solid var(--line); background: var(--bg); color: var(--fg); }
a { color: var(--accent); }
textarea { width: 100%; height: 10em; font: 13px monospace; }
"""

_SCRIPT = """
const STORE = "js3-labels-" + SAMPLE_SHA.slice(0, 12);
let labels = {};
try { labels = JSON.parse(localStorage.getItem(STORE) || "{}"); } catch (e) { labels = {}; }
function save() { try { localStorage.setItem(STORE, JSON.stringify(labels)); } catch (e) {} progress(); }
function progress() {
  const n = POSTINGS.filter(p => labels[p.id] && labels[p.id].label).length;
  document.getElementById("progress").textContent = n + " of " + POSTINGS.length + " labelled";
  for (const p of POSTINGS) {
    const card = document.getElementById("card-" + p.id);
    card.classList.toggle("done", !!(labels[p.id] && labels[p.id].label));
    if (document.getElementById("only-open").checked) card.hidden = !!(labels[p.id] && labels[p.id].label);
    else card.hidden = false;
  }
}
function setLabel(id, field, value) {
  labels[id] = labels[id] || {};
  labels[id][field] = value;
  labels[id].changed_at = new Date().toISOString();
  save();
}
function payload() {
  return JSON.stringify({ page: "labels/LABEL-POSTINGS.html", sample_sha256: SAMPLE_SHA,
    downloaded_at: new Date().toISOString(), labels: labels }, null, 1);
}
function download() {
  const blob = new Blob([payload()], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "js3-labels.json";
  document.body.appendChild(a); a.click(); a.remove();
}
function showText() { const t = document.getElementById("as-text"); t.hidden = false; t.value = payload(); t.select(); }
function render() {
  const list = document.getElementById("list");
  for (const p of POSTINGS) {
    const card = document.createElement("section");
    card.className = "card"; card.id = "card-" + p.id;
    const current = labels[p.id] || {};
    const name = "label-" + p.id;
    card.innerHTML =
      '<div class="id">' + p.id + ' · ' + p.company + '</div>' +
      '<h2></h2><div class="meta"></div>' +
      '<div class="text"></div>' +
      '<button type="button" class="more">Show the full text</button> ' +
      '<a target="_blank" rel="noopener noreferrer">open the live posting</a>' +
      '<div class="choices">' +
      ['yes', 'no', 'cannot tell'].map(v => '<label><input type="radio" name="' + name + '" value="' + v + '"> ' +
        ({ 'yes': 'Yes, it should reach Alex', 'no': 'No', 'cannot tell': "Can't tell" })[v] + '</label>').join('') +
      '</div>' +
      '<input type="text" placeholder="One line: what decides it">';
    card.querySelector("h2").textContent = p.title;
    card.querySelector(".meta").textContent = "Location: " + (p.location || "(blank)");
    card.querySelector(".text").textContent = p.text;
    card.querySelector("a").href = p.url;
    card.querySelector(".more").onclick = (e) => {
      const t = card.querySelector(".text"); t.classList.toggle("open");
      e.target.textContent = t.classList.contains("open") ? "Show less" : "Show the full text";
    };
    for (const r of card.querySelectorAll('input[type=radio]')) {
      if (current.label === r.value) r.checked = true;
      r.onchange = () => setLabel(p.id, "label", r.value);
    }
    const reason = card.querySelector('input[type=text]');
    reason.value = current.reason || "";
    reason.oninput = () => setLabel(p.id, "reason", reason.value);
    list.appendChild(card);
  }
  progress();
}
document.getElementById("only-open").onchange = progress;
render();
"""


_CLAIMS_SCRIPT = """
const STORE = "js3-claim-labels-" + CLAIMS_SHA.slice(0, 12);
let labels = {};
try { labels = JSON.parse(localStorage.getItem(STORE) || "{}"); } catch (e) { labels = {}; }
const ALL = POSTINGS.flatMap(p => p.claims.map(c => c.id));
function save() { try { localStorage.setItem(STORE, JSON.stringify(labels)); } catch (e) {} progress(); }
function progress() {
  const n = ALL.filter(id => labels[id] && labels[id].label).length;
  document.getElementById("progress").textContent = n + " of " + ALL.length + " claims labelled";
  for (const id of ALL) document.getElementById("row-" + id).classList.toggle("done", !!(labels[id] && labels[id].label));
}
function setLabel(id, field, value) { labels[id] = labels[id] || {}; labels[id][field] = value;
  labels[id].changed_at = new Date().toISOString(); save(); }
function payload() { return JSON.stringify({ page: "shortlist/v0.1/LABEL-CLAIMS.html", claims_sha256: CLAIMS_SHA,
  downloaded_at: new Date().toISOString(), labels: labels }, null, 1); }
function download() { const blob = new Blob([payload()], { type: "application/json" }); const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "js3-claim-labels.json"; document.body.appendChild(a); a.click(); a.remove(); }
function showText() { const t = document.getElementById("as-text"); t.hidden = false; t.value = payload(); t.select(); }
function render() {
  const list = document.getElementById("list");
  for (const p of POSTINGS) {
    const card = document.createElement("section"); card.className = "card";
    card.innerHTML = '<div class="id">Shortlist rank ' + p.rank + ' · ' + p.company + '</div><h2></h2><div class="meta"></div>' +
      '<div class="text"></div><button type="button" class="more">Show the full text</button> ' +
      '<a target="_blank" rel="noopener noreferrer">open the live posting</a><div class="claims"></div>';
    card.querySelector("h2").textContent = p.title;
    card.querySelector(".meta").textContent = "Location field: " + (p.location || "(blank)");
    card.querySelector(".text").textContent = p.text;
    card.querySelector("a").href = p.url;
    card.querySelector(".more").onclick = (e) => { const t = card.querySelector(".text"); t.classList.toggle("open");
      e.target.textContent = t.classList.contains("open") ? "Show less" : "Show the full text"; };
    const box = card.querySelector(".claims");
    for (const c of p.claims) {
      const row = document.createElement("div"); row.className = "claim"; row.id = "row-" + c.id;
      const current = labels[c.id] || {};
      row.innerHTML = '<div class="id"></div><div class="claimtext"></div><div class="quote"></div>' +
        '<div class="choices">' + ["supported", "contradicted", "insufficient"].map(v =>
          '<label><input type="radio" name="c-' + c.id + '" value="' + v + '"> ' + v + '</label>').join("") + '</div>' +
        '<input type="text" placeholder="For contradicted or insufficient: the sentence that decides it, or what is missing">';
      row.querySelector(".id").textContent = c.id + " · " + c.kind;
      row.querySelector(".claimtext").textContent = "Claim: " + c.claim;
      row.querySelector(".quote").textContent = c.quote ? "Quote (" + c.source_field + ", " + c.quote_check + "): “" + c.quote + "”" : "No quote given.";
      for (const r of row.querySelectorAll("input[type=radio]")) { if (current.label === r.value) r.checked = true;
        r.onchange = () => setLabel(c.id, "label", r.value); }
      const note = row.querySelector("input[type=text]"); note.value = current.note || "";
      note.oninput = () => setLabel(c.id, "note", note.value);
      box.appendChild(row);
    }
    list.appendChild(card);
  }
  progress();
}
render();
"""

_CLAIMS_STYLE = _STYLE + """
.claim { border-top: 1px solid var(--line); padding: 10px 0; }
.claim.done { background: var(--done); }
.claimtext { font-weight: 600; }
.quote { font-size: 0.92rem; color: var(--muted); }
"""


def build_claims(postings, claims_sha):
    """postings: [{rank, company, title, location, text, url, claims: [{id, kind, claim, quote, source_field, quote_check}]}]"""
    data = json.dumps(postings, ensure_ascii=False).replace("</", "<\\/")
    total = sum(len(p["claims"]) for p in postings)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>JS3 claim labels</title><style>{_CLAIMS_STYLE}</style></head>
<body>
<header><div class="row"><strong id="progress"></strong>
<button class="primary" onclick="download()">Download my claim labels</button>
<button onclick="showText()">Show labels as text</button></div></header>
<main>
<h1>JS3 shortlist claims: {total} claims on {len(postings)} postings</h1>
<p>These are the 8 postings your FILTER.md v0.1 ranks highest. Claude (claude-opus-5-5, through your Claude Code login,
2026-11-24) wrote each claim and chose its quote. The code checked only that each quote appears word for word. Whether
the quote <em>supports</em> the claim is your call. Read the passage in the full text, not only the quote.</p>
<p>Your FILTER.md labels: <strong>supported</strong>: "The passage states the claim for this role and preserves any
conditions, exceptions, or alternatives." <strong>contradicted</strong>: "The passage directly conflicts with the
claim." <strong>insufficient</strong>: "The text leaves the claim unresolved. Record what is missing and say 'I cannot
tell.'" For contradicted or insufficient, write the deciding sentence or what's missing in the box.</p>
<p>Claude has not proposed any labels. After you label, Claude will be asked to find the sentence that would change each
of your labels, and you decide whether it does. When you're done, click <strong>Download my claim labels</strong>
(it saves <code>js3-claim-labels.json</code>) and tell Claude Code "claims done".</p>
<textarea id="as-text" hidden></textarea>
<div id="list"></div>
</main>
<script>const CLAIMS_SHA = {json.dumps(claims_sha)};
const POSTINGS = {data};
{_CLAIMS_SCRIPT}</script>
</body></html>
"""


def build(members, items, urls, sample_sha):
    """members: the drawn sample (label ids); items: {(board, key): Item}; urls: {(board, key): link}."""
    postings = []
    for member in members:
        item = items[(member["board"], member["key"])]
        postings.append({"id": member["label_id"], "company": COMPANY.get(item.board, item.board),
                         "title": item.title, "location": item.location,
                         "text": plain_text(item.description), "url": urls.get((item.board, item.key), "")})
    data = json.dumps(postings, ensure_ascii=False).replace("</", "<\\/")
    count = len(postings)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>JS3 hand labels</title><style>{_STYLE}</style></head>
<body>
<header><div class="row"><strong id="progress"></strong>
<label><input type="checkbox" id="only-open"> show only unlabelled</label>
<button class="primary" onclick="download()">Download my labels</button>
<button onclick="showText()">Show labels as text</button></div></header>
<main>
<h1>JS3 hand labels: {count} postings</h1>
<p><strong>The question, for each posting:</strong> should this posting reach Alex Morgan? In your FILTER.md: “my fictional
applicant targeting early-career ML, AI systems, and data infrastructure roles”, and “An explicit U.S. work location fits
the search.” Choose <em>Yes</em>, <em>No</em> or <em>Can't tell</em>, and write one line on what decides it.</p>
<p>The text shown is the posting as saved on 2026-11-24 (run <code>2026-11-24-js3-corpus</code>). The live link may
have changed since. This page does not show what the filter decided or which group a posting was drawn from. Please
don't open <code>labels/v0.1-sample.json</code> or the <code>audit/</code> folder until you've downloaded your labels.</p>
<p>The brief says “judge each yourself”. SOURCES.md will record any help you used, so tell Claude Code if you had any.
Your labels save in this browser as you go. When you're done, click <strong>Download my labels</strong>. It saves
<code>js3-labels.json</code>, usually to Downloads. Then tell Claude Code “labels done”.</p>
<textarea id="as-text" hidden></textarea>
<div id="list"></div>
</main>
<script>const SAMPLE_SHA = {json.dumps(sample_sha)};
const POSTINGS = {data};
{_SCRIPT}</script>
</body></html>
"""
