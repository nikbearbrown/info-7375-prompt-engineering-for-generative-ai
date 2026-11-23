"""Build the blind labelling form for the reject audit (FILTER.md §6).

    python3 tools/make_audit_form.py

**Blind on purpose.** The form shows a posting and nothing else: no score, no
bucket, no gate, no hint of what the filter decided. The rows are shuffled with
a recorded seed so the bucket cannot be inferred from position either.

This is the direct fix for a failure in JS1: Claude told Weiting the agent's
verdicts before she labelled, so her four labels were not blind and no number
computed against them could be presented as an independent comparison. That
cost nothing to avoid and was avoided by nobody, so it is avoided mechanically
here — the decisions simply are not in the file she opens.

The sample, fixed in FILTER.md §6 before any of it was drawn:

- 30 postings drawn at random from everything the filter rejected at a gate;
- every posting the scorer put within ±2 of the threshold, which is all of the
  near-misses, because the threshold is the number most likely to be wrong;
- every posting the filter kept, so the audit can find false positives and not
  only false negatives.

Output: `audit/audit-form.html`, self-contained, opened with a browser. It
writes `audit/labels-weiting.json` when she presses Download.
"""

from __future__ import annotations

import html
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inherited import resume as resume_mod  # noqa: E402
from jobfilter import corpus as corpus_mod  # noqa: E402
from jobfilter import pipeline, score as scorer  # noqa: E402

SEED = 20261123
N_GATED = 30
BODY_CHARS = 6000


def build_sample(decisions):
    by = pipeline.buckets(decisions)
    rng = random.Random(SEED)

    gated = sorted(by[pipeline.GATED], key=lambda d: d.posting.identity)
    gated_sample = rng.sample(gated, min(N_GATED, len(gated)))

    near = [
        d for d in decisions
        if d.score is not None and abs(d.score.total - scorer.THRESHOLD) <= 2
    ]
    kept = by[pipeline.SHORTLISTED]

    # A posting can belong to more than one stratum -- 13 of the 14 kept
    # postings also sit within +/-2 of the threshold. Recording only the first
    # would under-report the kept sample, so every stratum is kept.
    chosen: dict[str, list] = {}
    order: dict[str, object] = {}
    for d, name in (
        [(d, "random_reject") for d in gated_sample]
        + [(d, "near_threshold") for d in near]
        + [(d, "kept") for d in kept]
    ):
        order[d.posting.identity] = d
        chosen.setdefault(d.posting.identity, []).append(name)

    rows = [(order[i], tuple(sorted(set(s)))) for i, s in chosen.items()]
    rng.shuffle(rows)
    return rows


def main() -> int:
    postings = corpus_mod.load()
    persona = resume_mod.load(ROOT / "data" / "resume.persona.json")
    decisions = pipeline.run(postings, persona)
    rows = build_sample(decisions)

    items = []
    for d, reason in rows:
        p = d.posting
        body = p.body or ""
        truncated = len(body) > BODY_CHARS
        items.append({
            "id": p.identity,
            "board": p.board,
            "title": p.title,
            "location": p.location,
            "family": p.job_family,
            "url": p.url,
            "body": body[:BODY_CHARS],
            "truncated": truncated,
            "no_body": not p.has_body,
            "_strata": list(reason),     # recorded, not shown
        })

    # the key the form must not contain
    answer_key = {
        d.posting.identity: {
            "bucket": d.bucket,
            "gate_failed": d.gate_failed,
            "score": None if d.score is None else d.score.total,
            "strata": list(reason),
        }
        for d, reason in rows
    }

    out_dir = ROOT / "audit"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "audit-answer-key.json").write_text(
        json.dumps(
            {
                "note": "The filter's own decisions for the sampled postings. "
                        "NOT shown in audit-form.html; written separately so the "
                        "labelling is blind. Compared against the labels only "
                        "after they come back.",
                "seed": SEED,
                "sample_size": len(rows),
                "decisions": answer_key,
            },
            indent=1, ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    shown = [{k: v for k, v in it.items() if k != "_strata"} for it in items]
    page = TEMPLATE.replace("__DATA__", json.dumps(shown, ensure_ascii=False))
    page = page.replace("__COUNT__", str(len(shown)))
    page = page.replace("__SEED__", str(SEED))
    (out_dir / "audit-form.html").write_text(page, encoding="utf-8")

    from collections import Counter
    strata = Counter(s for _, names in rows for s in names)
    print(f"wrote {out_dir / 'audit-form.html'}  ({len(rows)} postings)")
    print(f"      {out_dir / 'audit-answer-key.json'}  (not shown in the form)")
    print(f"  strata: {dict(strata)}   seed={SEED}")
    return 0


TEMPLATE = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JS3 reject audit — blind labelling</title>
<style>
  :root { --bg:#fbfbfa; --fg:#1a1a18; --mut:#6b6b66; --line:#e3e3df;
          --yes:#1a7f4b; --no:#b3341f; --unk:#7a6a1f; --card:#fff; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
          --bg:#16161a; --fg:#ececea; --mut:#9a9a94; --line:#2e2e34;
          --yes:#4ec27e; --no:#e8705a; --unk:#d4ba52; --card:#1e1e24; } }
  * { box-sizing:border-box }
  body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.55
         ui-sans-serif,-apple-system,"PingFang SC","Helvetica Neue",sans-serif; }
  header { position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line);
           padding:14px 16px; z-index:10 }
  .wrap { max-width:860px; margin:0 auto; padding:0 16px 80px }
  h1 { font-size:17px; margin:0 0 4px }
  .sub { color:var(--mut); font-size:13px }
  .bar { height:6px; background:var(--line); border-radius:3px; margin-top:10px; overflow:hidden }
  .bar > i { display:block; height:100%; background:var(--yes); width:0%; transition:width .2s }
  .card { background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:16px; margin:16px 0 }
  .card.done { opacity:.55 }
  .ttl { font-weight:600; font-size:16px; margin:0 0 6px }
  .meta { color:var(--mut); font-size:13px; margin-bottom:10px }
  .body { white-space:pre-wrap; font-size:13.5px; max-height:300px; overflow:auto;
          border:1px solid var(--line); border-radius:6px; padding:10px; background:var(--bg) }
  .nobody { color:var(--unk); font-style:italic; font-size:13.5px;
            border:1px dashed var(--line); border-radius:6px; padding:10px }
  .btns { display:flex; gap:8px; margin-top:12px; flex-wrap:wrap }
  button { font:inherit; padding:7px 14px; border-radius:7px; border:1px solid var(--line);
           background:var(--card); color:var(--fg); cursor:pointer }
  button.sel[data-v="yes"] { background:var(--yes); border-color:var(--yes); color:#fff }
  button.sel[data-v="no"]  { background:var(--no);  border-color:var(--no);  color:#fff }
  button.sel[data-v="unsure"] { background:var(--unk); border-color:var(--unk); color:#fff }
  footer { position:fixed; bottom:0; left:0; right:0; background:var(--card);
           border-top:1px solid var(--line); padding:10px 16px; text-align:center }
  .dl { background:var(--yes); color:#fff; border-color:var(--yes); padding:9px 20px }
  .note { font-size:12.5px; color:var(--mut); margin-top:8px }
  code { font-size:12.5px }
</style>
</head>
<body>
<header>
  <div class="wrap" style="padding-bottom:0">
    <h1>JS3 拒绝审计 — 盲标</h1>
    <div class="sub">
      共 __COUNT__ 条,顺序已用种子 __SEED__ 打乱。<b>这里不显示过滤器的任何判定</b>——
      分数、分桶、卡在哪一关都没有,你看到的和过滤器看到的是同一份原始内容。
    </div>
    <div class="bar"><i id="bar"></i></div>
    <div class="sub" id="count" style="margin-top:6px"></div>
  </div>
</header>
<div class="wrap" id="list"></div>
<footer>
  <button class="dl" id="dl">下载 labels-weiting.json</button>
  <div class="note">随时可以下载,不必全部标完。进度会自动存在浏览器里。</div>
</footer>
<script>
const DATA = __DATA__;
const KEY = "js3-audit-labels-v1";
let labels = {};
try { labels = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { labels = {}; }

const QUESTION = "这条职位,你希望它出现在你的候选名单里吗?";

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(labels)); } catch (e) {}
  const n = Object.keys(labels).length;
  document.getElementById("bar").style.width = (100 * n / DATA.length) + "%";
  document.getElementById("count").textContent = n + " / " + DATA.length + " 已标注";
}

function card(item, i) {
  const el = document.createElement("div");
  el.className = "card";
  const fam = item.family === null ? "(无)" : item.family;
  const bodyHtml = item.no_body
    ? '<div class="nobody">这个板块没有返回职位正文。只有标题、地点和部门可以依据——过滤器看到的也只有这些。</div>'
    : '<div class="body"></div>';
  el.innerHTML =
      '<div class="ttl"></div>'
    + '<div class="meta"></div>'
    + bodyHtml
    + '<div class="btns">'
    + '<button data-v="yes">想看 (yes)</button>'
    + '<button data-v="no">不想看 (no)</button>'
    + '<button data-v="unsure">说不准 (unsure)</button>'
    + '</div>';
  el.querySelector(".ttl").textContent = (i + 1) + ". " + item.title;
  el.querySelector(".meta").textContent =
    item.board + "  ·  " + item.location + "  ·  部门: " + fam;
  if (!item.no_body) {
    el.querySelector(".body").textContent =
      item.body + (item.truncated ? "\\n\\n[... 正文已截断 ...]" : "");
  }
  el.querySelectorAll("button").forEach(b => {
    b.onclick = () => {
      labels[item.id] = b.dataset.v;
      el.querySelectorAll("button").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel");
      el.classList.add("done");
      save();
    };
    if (labels[item.id] === b.dataset.v) { b.classList.add("sel"); el.classList.add("done"); }
  });
  return el;
}

const list = document.getElementById("list");
const q = document.createElement("div");
q.className = "sub";
q.style.margin = "16px 0 0";
q.textContent = QUESTION + "  —  按你自己的标准判断,不用猜过滤器会怎么判。";
list.appendChild(q);
DATA.forEach((item, i) => list.appendChild(card(item, i)));
save();

document.getElementById("dl").onclick = () => {
  const out = {
    labelled_by: "Weiting Wang",
    labelled_on: new Date().toISOString(),
    form: "audit/audit-form.html",
    seed: __SEED__,
    blind: "The form showed no score, no bucket and no gate. Order shuffled.",
    question: QUESTION,
    labels: labels
  };
  const blob = new Blob([JSON.stringify(out, null, 1)], {type: "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "labels-weiting.json";
  a.click();
};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
