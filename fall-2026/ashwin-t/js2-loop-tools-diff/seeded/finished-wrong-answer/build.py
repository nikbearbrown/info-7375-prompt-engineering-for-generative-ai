"""Rebuild this SEEDED folder from the real live run of 2026-11-09 (written by Claude Code).

    python3 seeded/finished-wrong-answer/build.py      # from the js2-loop-tools-diff folder

Real slices: the first 3 klaviyo postings and first 2 supabase postings, byte-for-byte objects
from runs/2026-11-09T20-21-52Z-live/raw/ (collected 2026-11-09T20:21:52Z), re-serialized.
Hand-made: the hubspotjobs body {"jobs": [], "meta": {"total": 0}}. HubSpot's real board had
126 postings at that time; the empty body is NOT a real response.
Seeded state: those klaviyo and supabase ids, plus the first 5 real hubspotjobs ids, as if a
previous run had seen them.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent.parent / "runs" / "2026-11-09T20-21-52Z-live" / "raw"
COLLECTED = "2026-11-09T20:21:52Z"


def load(name):
    return json.loads((LIVE / name).read_text(encoding="utf-8"))


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


klaviyo = load("greenhouse__klaviyo__attempt-1.json")
supabase = load("ashby__supabase__attempt-1.json")
hubspot = load("greenhouse__hubspotjobs__attempt-1.json")

dump("greenhouse__klaviyo.json", {"jobs": klaviyo["jobs"][:3], "meta": {"total": 3}})
dump("ashby__supabase.json", {"jobs": supabase["jobs"][:2], "apiVersion": supabase.get("apiVersion")})
dump("greenhouse__hubspotjobs.json", {"jobs": [], "meta": {"total": 0}})
dump("config.json", {"schema_version": 1, "boards": [
    {"provider": "greenhouse", "board": "klaviyo", "purpose": "watch"},
    {"provider": "greenhouse", "board": "hubspotjobs", "purpose": "watch"},
    {"provider": "ashby", "board": "supabase", "purpose": "watch"}]})


def entry(ids):
    return {"seen_ids": sorted(str(i) for i in ids), "last_observed": COLLECTED}


dump("state.json", {"schema_version": 1, "last_finished_run": COLLECTED, "boards": {
    "greenhouse/klaviyo": entry(j["id"] for j in klaviyo["jobs"][:3]),
    "greenhouse/hubspotjobs": entry(j["id"] for j in hubspot["jobs"][:5]),
    "ashby/supabase": entry(j["id"] for j in supabase["jobs"][:2])}})

real = f"real slice of the live response collected {COLLECTED} (runs/2026-11-09T20-21-52Z-live)"
dump("manifest.json", {
    "label": "SEEDED REPLAY",
    "config": "config.json",
    "state": "state.json",
    "responses": {
        "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true":
            {"status": 200, "body": "greenhouse__klaviyo.json", "provenance": real},
        "https://api.ashbyhq.com/posting-api/job-board/supabase":
            {"status": 200, "body": "ashby__supabase.json", "provenance": real},
        "https://boards-api.greenhouse.io/v1/boards/hubspotjobs/jobs?content=true":
            {"status": 200, "body": "greenhouse__hubspotjobs.json",
             "provenance": "HAND-MADE empty board; the real board had 126 postings at " + COLLECTED},
    }})
print("rebuilt", sorted(p.name for p in HERE.iterdir()))
