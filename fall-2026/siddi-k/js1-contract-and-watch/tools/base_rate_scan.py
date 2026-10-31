"""One-off: the contract's base-rate check (seed-42 selection, count only) on other public Greenhouse boards.
Uses the agent's own rule/textprep/labels code; boilerplate is generic (cut at 'benefits' only), so counts are rough.
Written by Claude and run once on 2026-10-31 (~06:47 ET) to choose the v2 slug; output is in
evidence/base-rate-databricks/README.md. Boards change, so a rerun will print different numbers.

    python tools/base_rate_scan.py . stripe,samsara,scaleai
"""
import json, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
sys.path.insert(0, sys.argv[1])
from agent import config, labels, persona as pm, rule  # noqa: E402

cfg = config.load()
cfg = replace(cfg, cut_headings=("benefits",), drop_phrases=())
persona = pm.load(config.ROOT / "data" / "persona_resume.json", cfg.vocab)
BOARDS = sys.argv[2].split(",")


def scan(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            board = json.load(r)
    except Exception as e:
        return slug, f"error {type(e).__name__}"
    jobs = board.get("jobs") or []
    if len(jobs) < 20:
        return slug, f"only {len(jobs)} postings"
    sel = labels.select(board, persona, cfg)
    loc_ok = sum(1 for j in jobs if rule.location_check((j.get("location") or {}).get("name", ""), persona)["passed"])
    return slug, (f"postings {len(jobs):4}  title+seniority {sel['candidates']:3}  location-ok {loc_ok:4}  "
                  f"base-rate (rule-relevant of the 20) {sel['rule_relevant_count']}")


with ThreadPoolExecutor(8) as ex:
    for slug, msg in ex.map(scan, BOARDS):
        print(f"{slug:16} {msg}")
