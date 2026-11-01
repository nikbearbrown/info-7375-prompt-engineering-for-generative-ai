#!/usr/bin/env python3
"""JS1 job-search agent: watch one Greenhouse board, report new postings, judge each two ways.
Python 3.10+, standard library only. Claude calls go through Claude Code: `claude -p` (one fresh conversation per call).
"""
from __future__ import annotations
import argparse, csv, datetime as dt, html, json, os, random, re, shlex, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOWED_HOSTS = {"boards-api.greenhouse.io"}
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
TITLE_RE = re.compile(r"\b(analyst|analytics|business intelligence)\b", re.I)
YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|–|to)?\s*(\d{1,2})?\s*\+?\s*years?", re.I)
VERDICTS = {"relevant", "not_relevant"}
KEYS = {"verdict", "resume_fields", "posting_quotes", "reason"}
RESUME_FIELDS = {"skills.core", "target_titles", "max_years_experience", "education", "experience"}

# ---------- fetch (allow-listed) ----------
def check_host(url: str) -> None:
    host = urllib.parse.urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise PermissionError(f"refused: host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")

def fetch(slug: str) -> dict:
    if not SLUG_RE.match(slug):
        raise ValueError(f"refused: bad board slug {slug!r}")
    url = BOARD_URL.format(slug=slug); check_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": "info7375-js1/0.1 (course project; public board API)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def text_of(job: dict) -> str:
    t = html.unescape(job.get("content") or "")
    t = re.sub(r"<(?:br|/p|/li|/h\d|/ul)[^>]*>", "\n", t); t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\n\s*\n+", "\n", t).strip()

def posting(job: dict) -> dict:
    return {"id": str(job["id"]), "title": job.get("title", ""), "location": (job.get("location") or {}).get("name", ""),
            "url": job.get("absolute_url", ""), "text": text_of(job)}

# ---------- watch: new since last run, by id ----------
def watch(raw: dict, state_path: Path, label: str) -> tuple[list[dict], bool]:
    jobs = [posting(j) for j in raw.get("jobs", [])]
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    baseline = state is None
    seen = set() if baseline else set(state["seen_ids"])
    new = [] if baseline else [p for p in jobs if p["id"] not in seen]
    state_path.write_text(json.dumps({"seen_ids": sorted(seen | {p["id"] for p in jobs}), "last_run": label}, indent=1))
    return new, baseline

# ---------- judge 1: the written rule (a RECORD anyone can recompute) ----------
def max_years(text: str) -> int | None:
    nums = [int(b or a) for a, b in YEARS_RE.findall(text)]
    nums = [n for n in nums if n <= 20]
    return max(nums) if nums else None

def skill_hits(resume: dict, text: str) -> list[str]:
    return [s for s in resume["skills"]["core"] if re.search(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])", text, re.I)]

def rule_judge(resume: dict, p: dict) -> dict:
    title_ok = bool(TITLE_RE.search(p["title"]))
    hits = skill_hits(resume, p["title"] + "\n" + p["text"])
    yrs = max_years(p["text"]); limit = resume["max_years_experience"]
    years_ok = yrs is None or yrs <= limit
    verdict = "relevant" if (title_ok and len(hits) >= 2 and years_ok) else "not_relevant"
    why = [f"posting.title={p['title']!r} {'matches' if title_ok else 'does not match'} an analyst/analytics/BI title (resume.target_titles)",
           f"posting.text names {len(hits)} of resume.skills.core: {hits}",
           f"posting.text max years asked = {yrs if yrs is not None else 'not stated'} vs resume.max_years_experience={limit}"]
    return {"kind": "RECORD (rule)", "verdict": verdict, "resume_fields": ["target_titles", "skills.core", "max_years_experience"],
            "posting_fields": ["title", "text"], "justification": why}

# ---------- judge 2: Claude under a prompt contract (a JUDGMENT) ----------
def build_prompt(template: str, resume: dict, p: dict) -> str:
    post = f"TITLE: {p['title']}\nLOCATION: {p['location']}\n{p['text'][:6000]}"
    return template.replace("{resume}", json.dumps(resume)).replace("{posting}", post)

def validate(reply: str, p: dict) -> dict:
    """Reject anything that is not exactly the contract's format."""
    s = reply.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    try: d = json.loads(s)
    except json.JSONDecodeError as e: raise ValueError(f"not JSON: {e}")
    if not isinstance(d, dict) or set(d) != KEYS: raise ValueError(f"keys must be exactly {sorted(KEYS)}")
    if d["verdict"] not in VERDICTS: raise ValueError(f"bad verdict {d['verdict']!r}")
    if not d["resume_fields"] or any(f not in RESUME_FIELDS for f in d["resume_fields"]): raise ValueError("resume_fields empty or unknown")
    if not d["posting_quotes"]: raise ValueError("cites no posting text")
    body = p["title"] + "\n" + p["text"]
    norm = lambda x: re.sub(r"\s+", " ", x).strip().lower()
    for q in d["posting_quotes"]:
        if norm(q) not in norm(body): raise ValueError(f"quote not in posting: {q!r}")
    if not isinstance(d["reason"], str) or not d["reason"].strip(): raise ValueError("empty reason")
    d["kind"] = "JUDGMENT (Claude)"; return d

def ask_claude(prompt: str) -> str:
    cmd = shlex.split(os.environ.get("CLAUDE_CMD", "claude -p"))
    return subprocess.run(cmd + [prompt], capture_output=True, text=True, timeout=180).stdout

def claude_judge(template: str, resume: dict, p: dict) -> dict:
    raw = ask_claude(build_prompt(template, resume, p))
    try: return validate(raw, p) | {"raw": raw}
    except ValueError as e: return {"kind": "JUDGMENT (Claude)", "verdict": "INVALID", "error": str(e), "raw": raw}

# ---------- commands ----------
def load_resume(path=None):
    """Contract 'Refuses': only a fictional persona is ever loaded."""
    r = json.loads(Path(path or ROOT / "persona/resume.json").read_text())
    for k in ("personal", "target_titles", "max_years_experience", "skills"):
        if k not in r: raise ValueError(f"resume missing '{k}'")
    if not r["skills"].get("core"): raise ValueError("resume skills.core is empty")
    em, ph = r["personal"].get("email", ""), r["personal"].get("phone", "")
    if not em.endswith("@example.com") or "555" not in ph:
        raise PermissionError("refusing a resume that is not a fictional persona (@example.com email and 555 phone required)")
    return r
def stamp(): return dt.datetime.now().strftime("%Y-%m-%dT%H%M%S")
def all_postings(raw_path): return [posting(j) for j in json.loads(Path(raw_path).read_text()).get("jobs", [])]

def cmd_run(a):
    if a.from_file:
        raw = json.loads(Path(a.from_file).read_text())
        label = stamp() + ("-SEEDED" if "_SEEDED" in raw else "-from-saved")
    else: label = stamp() + "-live"
    if a.from_file: pass
    else:
        raw = fetch(a.board); (ROOT / f"runs/{label}-raw.json").write_text(json.dumps(raw))
    new, baseline = watch(raw, ROOT / "state/seen.json", label)
    resume = load_resume(); tpl = (ROOT / "prompts/revised.txt").read_text()
    out = {"run": label, "board": a.board, "baseline": baseline, "postings_on_board": len(raw.get("jobs", [])), "new": []}
    for p in new:
        out["new"].append({"id": p["id"], "title": p["title"], "url": p["url"], "rule": rule_judge(resume, p),
                           "claude": claude_judge(tpl, resume, p) if not a.no_claude else "skipped"})
    (ROOT / f"runs/{label}-report.json").write_text(json.dumps(out, indent=1))
    print(f"{label}: {out['postings_on_board']} on board, baseline={baseline}, new={len(new)} -> runs/{label}-report.json")
    for n in out["new"]: print(f"  NEW {n['id']} {n['title']!r}: rule={n['rule']['verdict']} claude={n['claude'] if isinstance(n['claude'], str) else n['claude']['verdict']}")

def cmd_seed(a):
    """Make a SEEDED earlier response: the real saved response minus its N highest ids (clearly labelled)."""
    raw = json.loads(Path(a.raw).read_text()); jobs = sorted(raw["jobs"], key=lambda j: j["id"])
    seeded = {"_SEEDED": f"constructed from {a.raw} by removing the {a.drop} highest ids", "jobs": jobs[:-a.drop]}
    Path(a.out).write_text(json.dumps(seeded)); print(f"wrote {a.out} ({len(seeded['jobs'])} jobs, {a.drop} removed)")

def cmd_labels(a):
    allp = all_postings(a.raw); rng = random.Random(7375)
    ana = [p for p in allp if TITLE_RE.search(p["title"])]; rest = [p for p in allp if not TITLE_RE.search(p["title"])]
    rng.shuffle(rest); ps = (ana + rest)[:20] if a.analytics_only else rest[:20]
    rng.shuffle(ps)   # all analyst postings + random others, then mixed so dev and held-out both get some
    with open(ROOT / "labels/labels.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "split", "title", "url", "my_label (relevant/not_relevant)", "my_reason"])
        for i, p in enumerate(ps): w.writerow([p["id"], "dev" if i < 10 else "heldout", p["title"], p["url"], "", ""])
    print(f"labels/labels.csv: {len(ps)} postings (10 dev, 10 held-out). Fill my_label BY HAND using LABELING-RULE in CONTRACT.md.")

def read_labels(split=None):
    rows = list(csv.DictReader(open(ROOT / "labels/labels.csv")))
    col = [k for k in rows[0] if k.startswith("my_label")][0]
    if any(r[col].strip() not in VERDICTS for r in rows): sys.exit("labels/labels.csv: every my_label must be relevant or not_relevant (label by hand first)")
    return [(r["id"], r[col].strip()) for r in rows if split in (None, r["split"])]

def cmd_experiment(a):
    resume = load_resume(); ps = {p["id"]: p for p in all_postings(a.raw)}; res = []
    for name in ("baseline", "revised"):
        tpl = (ROOT / f"prompts/{name}.txt").read_text()
        for pid, label in read_labels(a.split):
            j = claude_judge(tpl, resume, ps[pid])
            res.append({"prompt": name, "split": a.split, "id": pid, "title": ps[pid]["title"], "hand": label, "claude": j["verdict"], "at": dt.datetime.now().isoformat(timespec="seconds"), "raw_reply": j.get("raw", ""),
                        "rule": rule_judge(resume, ps[pid])["verdict"], "error": j.get("error", "")})
            print(name, pid, label, j["verdict"], j.get("error", ""))
    (ROOT / f"reports/experiment-{a.split}.json").write_text(json.dumps(res, indent=1))
    lines = [f"# Prompt experiment — {a.split} set ({stamp()})", "", "| prompt | n | valid | agrees with my hand label |", "|---|---|---|---|"]
    for name in ("baseline", "revised"):
        r = [x for x in res if x["prompt"] == name]
        lines.append(f"| {name} | {len(r)} | {sum(x['claude'] != 'INVALID' for x in r)} | {sum(x['claude'] == x['hand'] for x in r)}/{len(r)} |")
    r0 = [x for x in res if x["prompt"] == "baseline"]
    lines += [f"| written rule (no Claude) | {len(r0)} | — | {sum(x['rule'] == x['hand'] for x in r0)}/{len(r0)} |", "",
              "| id | title | hand | baseline | revised | rule |", "|---|---|---|---|---|---|"]
    for x in r0:
        rv = next(y for y in res if y["prompt"] == "revised" and y["id"] == x["id"])
        lines.append(f"| {x['id']} | {x['title']} | {x['hand']} | {x['claude']} | {rv['claude']} | {x['rule']} |")
    (ROOT / f"reports/EXPERIMENT-{a.split}.md").write_text("\n".join(lines) + "\n"); print("\n".join(lines[:8]))

def cmd_sample(a):
    resume = load_resume(); ps = {p["id"]: p for p in all_postings(a.raw)}; tpl = (ROOT / "prompts/revised.txt").read_text()
    labels = dict(read_labels())
    seen_t, ids = set(), []
    for pid in sorted(labels, key=lambda i: (labels[i] != "relevant", not TITLE_RE.search(ps[i]["title"]))):
        if ps[pid]["title"] not in seen_t: seen_t.add(ps[pid]["title"]); ids.append(pid)
    ids = ids[:5]; res = []
    for pid in ids:
        for k in range(a.n):
            j = claude_judge(tpl, resume, ps[pid]); res.append({"id": pid, "try": k + 1, "verdict": j["verdict"], "error": j.get("error", ""), "at": dt.datetime.now().isoformat(timespec="seconds"), "raw_reply": j.get("raw", "")})
            print(pid, k + 1, j["verdict"])
    (ROOT / "reports/sampling.json").write_text(json.dumps(res, indent=1))
    lines = [f"# Sampling report ({stamp()}) — revised prompt, {a.n} fresh `claude -p` conversations per posting", "",
             "| id | title | verdicts | agreement | my hand label | majority matches me? |", "|---|---|---|---|---|---|"]
    for pid in ids:
        v = [x["verdict"] for x in res if x["id"] == pid]; top = max(set(v), key=v.count)
        lines.append(f"| {pid} | {ps[pid]['title']} | {', '.join(v)} | {v.count(top)}/{len(v)} | {labels[pid]} | {'yes' if top == labels[pid] else 'NO'} |")
    (ROOT / "reports/SAMPLING.md").write_text("\n".join(lines) + "\n"); print("\n".join(lines))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("--board", default="klaviyo"); r.add_argument("--from-file"); r.add_argument("--no-claude", action="store_true"); r.set_defaults(f=cmd_run)
    s = sp.add_parser("seed"); s.add_argument("raw"); s.add_argument("--drop", type=int, default=3); s.add_argument("--out", required=True); s.set_defaults(f=cmd_seed)
    l = sp.add_parser("labels"); l.add_argument("raw"); l.add_argument("--analytics-only", action="store_true"); l.set_defaults(f=cmd_labels)
    e = sp.add_parser("experiment"); e.add_argument("raw"); e.add_argument("--split", choices=["dev", "heldout"], required=True); e.set_defaults(f=cmd_experiment)
    m = sp.add_parser("sample"); m.add_argument("raw"); m.add_argument("--n", type=int, default=4); m.set_defaults(f=cmd_sample)
    a = ap.parse_args(); a.f(a)
