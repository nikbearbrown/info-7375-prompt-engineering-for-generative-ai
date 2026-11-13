#!/usr/bin/env python3
"""Build beat_sheet.json for the Early Bird pitch film, then sync it to the measured audio.

Source script: SCRIPT.md (v1.0, 2026-10-24). Narration below is that script, respelled
only where Kokoro would misread it ("Info seventy-three seventy-five" for INFO 7375,
"Kuh-mure" for Commure, "I Ds" for IDs, "S Q L" for SQL, "Screener" for Screenr,
"Fast A P I" for FastAPI, "Lang Graph" for LangGraph). Every on-screen figure is listed
in FACTCHECK.md with its source; Early Bird is not built, so the only measured figures
come from saved board files and the runs listed there.

Two steps, either side of the audio:

    python build_beats.py            # 1. write beat_sheet.json from the spec below
    # 2. narrate:  python <toolkit>/runtime/scripts/generate_audio_kokoro.py .
    # 3. align:    python <toolkit>/runtime/scripts/align.py .   (writes mp3/words.json)
    python build_beats.py --sync     # 4. durationSeconds = measured audio,
                                     #    cues = the second each cue word is spoken

--sync never invents a time: a cue word that is not in words.json is a hard error,
so a reveal can only land on a word the narrator actually says.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEET = HERE / "beat_sheet.json"
WORDS = HERE / "mp3" / "words.json"

SLUG = "early-bird-pitch"
TITLE = "Early Bird: a job-search agent for SWE and AI roles"
VOICE = "am_onyx"            # Kokoro, local, free


def beat(bid, act, role, narration, est, pattern, props, show, cue_words=None, lane=None, qc=None, **extra):
    shot = {"type": "REMOTION", "motion": "show-block", "show": show,
            "remotion": {"pattern": pattern, "props": props}}
    if lane:
        shot["lane"] = lane
    b = {"beat_id": bid, "act": act, "role_note": role, "narration_text": narration,
         "voice": VOICE, "engine": "kokoro", "estimated_duration_s": est, "shot": shot}
    if cue_words:
        b["cue_words"] = {k: list(v) for k, v in cue_words.items()}
    if qc:
        b["qc"] = qc
    b.update(extra)
    return b


BEATS = [
    beat("B00", "OPEN", "Cold open: who is speaking, how the script was made, the synthetic voice, the need.",
         "Hi, I'm Vrajesh, and this is my final project pitch for Info seventy-three seventy-five. I drafted this "
         "script with Claude from my own decisions, and a synthetic voice reads it. I graduate in December, and I'm "
         "job hunting right now. In this market, I don't want to skip a single software job. I want to see every new "
         "one, early.",
         20, "EfOpen", {},
         [{"at": 0.0, "event": "title 'Early Bird.' over a rising sun"},
          {"at": "synthetic", "event": "disclosure pill: script drafted with Claude, synthetic voice"},
          {"at": "December", "event": "pill: Dec 2026 grad"},
          {"at": "skip", "event": "a row of software job cards, all kept"},
          {"at": "early", "event": "the newest card lifts: new"}],
         cue_words={"name": ("vrajesh", 1), "voice": ("synthetic", 1), "december": ("december", 1),
                    "skip": ("skip", 1), "early": ("early", 1)},
         lane="bookend"),

    beat("B01", "WHAT", "Q1. One sentence, then the artifact and its form. PLANNED.",
         "My project is Early Bird, a small Python agent I will build. Each time I run it, it will check the public "
         "job boards of the twenty-five to thirty companies on my list, and report only the software, full-stack and "
         "AI postings that are new since the last run. The finished artifact will be a public GitHub repository: a "
         "command-line tool, its tests, the saved board responses, and one report per run.",
         24, "EfWhat", {},
         [{"at": "agent", "event": "run station appears"},
          {"at": "boards", "event": "my-list station: Greenhouse, Lever, Ashby"},
          {"at": "new", "event": "report station: only new software / full-stack / AI"},
          {"at": "artifact", "event": "artifact pills"}],
         cue_words={"agent": ("agent", 1), "boards": ("boards", 1), "new": ("new", 1),
                    "artifact": ("artifact", 1), "report": ("report", 2)}),

    beat("B02", "EXISTS", "Exists today, REAL: two saved Commure snapshots (2026-10-14, 2026-10-23) and the ID diff "
         "I ran on 2026-10-24.",
         "The agent doesn't exist yet. What exists is real data. I saved Kuh-mure's public job board twice: on "
         "October fourteenth, and again on October twenty-third. Eighty postings, then eighty-one. I compared the "
         "posting I Ds: twelve were new, and eleven were gone. Five of the twelve new ones were software engineering "
         "roles. Seven were not software: sales, marketing, design, and one partnerships role.",
         24, "EfExists", {},
         [{"at": "fourteenth", "event": "dot grid, Oct 14: 80 postings"},
          {"at": "twenty-third", "event": "dot grid, Oct 23: 81 postings"},
          {"at": "twelve", "event": "12 new dots light"},
          {"at": "eleven", "event": "11 gone dots hollow on the left"},
          {"at": "Five", "event": "5 software / 7 other"}],
         cue_words={"data": ("data", 1), "fourteenth": ("fourteenth", 1), "twentythird": ("twenty-third", 1),
                    "eighty": ("eighty", 1), "twelve": ("twelve", 1), "eleven": ("eleven", 1),
                    "five": ("five", 1), "seven": ("seven", 1)}),

    beat("B03", "WHY", "Q2. REAL: greenhouse-watch run by me on the same two snapshots (2026-10-24, course sample "
         "resume). LinkedIn Job Match from launch coverage. PLANNED: Early Bird's difference.",
         "The closest alternative is the course's own greenhouse-watch. I ran it myself on the same two snapshots, "
         "with the course's sample resume. It found the same twelve new postings, and kept all five software roles. "
         "But it also kept Head of Performance Creative, a marketing job, because the posting mentions Python and "
         "S Q L. It watches one board per run, and keeps what passes a resume-word score. LinkedIn's Job Match only "
         "covers LinkedIn jobs, and I can't re-run how it decided. Early Bird will watch my whole list in one run, "
         "decide what counts as a software job from the role itself, not resume overlap, and keep every one, "
         "flagging only hard blockers, quoting the line from the posting.",
         46, "EfAlternative", {},
         [{"at": "ran", "event": "the 12 new titles list in"},
          {"at": "kept", "event": "greenhouse-watch column: 6 checks, 6 dashes"},
          {"at": "marketing", "event": "MARKETING stamp on Head of Performance Creative; matched words"},
          {"at": "one", "event": "cut to three option cards"},
          {"at": "whole", "event": "Early Bird card (planned)"},
          {"at": "quoting", "event": "example quoted blocker"}],
         cue_words={"ran": ("ran", 1), "same": ("same", 1), "kept": ("kept", 1), "marketing": ("marketing", 1),
                    "one": ("one", 1), "linkedin": ("linkedin's", 1), "whole": ("whole", 1),
                    "quoting": ("quoting", 1)}),

    beat("B04", "WHO", "Q3. The reader and their first sixty seconds. CONSTRUCTED (nothing is built).",
         "Who will open it? A hiring manager for a full-stack or AI engineering role. In the first sixty seconds, "
         "they will run one command on labeled sample data, and open the report: new postings, quoted blockers, and "
         "the tests that passed. The other user will be me, before every application session.",
         20, "EfWho", {},
         [{"at": "hiring", "event": "reader pill"},
          {"at": "sixty", "event": "60 s ring starts to sweep"},
          {"at": "command", "event": "step 1: the command"},
          {"at": "report", "event": "step 2: open the report"},
          {"at": "blockers", "event": "step 3: what is in it"},
          {"at": "me", "event": "second user: me"}],
         cue_words={"hiring": ("hiring", 1), "sixty": ("sixty", 1), "command": ("command", 1),
                    "report": ("report", 1), "blockers": ("blockers", 1), "me": ("me", 1)}),

    beat("B05", "PROVES", "Q4. Course topics tied to the evidence I will produce. PLANNED.",
         "What will it prove about me? Prompt contracts: Claude will have to answer in a fixed format, and a "
         "validator will reject anything else. Verification: a rule anyone can recompute, next to a labeled Claude "
         "judgment. Agent loops, with budgets and honest exit statuses. And evaluation: twenty postings I will label "
         "by hand, with ten held back for the final test.",
         22, "EfProves", {},
         [{"at": "contracts", "event": "ledger row 1"}, {"at": "verification", "event": "row 2"},
          {"at": "loops", "event": "row 3"}, {"at": "evaluation", "event": "row 4"}],
         cue_words={"contracts": ("contracts", 1), "verification": ("verification", 1), "loops": ("loops", 1),
                    "evaluation": ("evaluation", 1)}),

    beat("B06", "SCOPE", "Q5. Exclusions, the first piece that runs, and how to verify it: the REAL answer key "
         "(12 new IDs) the PLANNED watcher must reproduce.",
         "What's out, on purpose: auto-applying, logging in, messaging anyone, and scraping LinkedIn. Companies on "
         "their own hiring systems, like Google, will be marked unsupported. The first piece I'll make run is the "
         "watcher on Kuh-mure, and its check already has an answer key: the twelve new I Ds from my two saved files. "
         "The watcher will have to report exactly those twelve, and my greenhouse-watch run is a second, independent "
         "list.",
         34, "EfScope", {},
         [{"at": "out", "event": "four exclusions struck through"},
          {"at": "unsupported", "event": "Google greys to unsupported"},
          {"at": "first", "event": "answer-key card"},
          {"at": "key", "event": "12 real ID prefixes pop in"},
          {"at": "twelve", "event": "watcher must report exactly these 12 (planned)"},
          {"at": "independent", "event": "greenhouse-watch also found 12 (real)"}],
         cue_words={"out": ("out", 1), "unsupported": ("unsupported", 1), "first": ("first", 1),
                    "key": ("key", 1), "twelve": ("twelve", 2), "recompute": ("exactly", 1),
                    "independent": ("independent", 1)}),

    beat("B07", "RISK", "Q6. The risk: deciding what counts as a software job. Three REAL titles (Commure 2026-10-23, "
         "my greenhouse-watch run, Stripe from the 2026-10-14 probe) and the mitigation.",
         "What could break it? Deciding what counts as a software job. Words mislead both ways. Sales Strategy and "
         "Operations, Agents, is a sales job. greenhouse-watch kept a marketing role because the posting said Python. "
         "And across five boards, my probe's keyword rule matched seven hundred eighty-nine titles, including Account "
         "Executive, AI Sales, at Stripe. So I'll write the rule before the code, hand-label real postings, audit "
         "thirty random rejects, and only accept a Claude verdict that quotes the posting.",
         32, "EfRisk", {},
         [{"at": "Agents", "event": "case 1 + SALES stamp"},
          {"at": "Python", "event": "case 2 + MARKETING stamp"},
          {"at": "Account", "event": "case 3 + SALES stamp"},
          {"at": "matched", "event": "counter 789 of 2,156"},
          {"at": "rule", "event": "four mitigation pills"}],
         cue_words={"deciding": ("deciding", 1), "agents": ("agents", 1), "python": ("python", 1),
                    "account": ("account", 1), "matched": ("matched", 1), "rule": ("rule", 2),
                    "hand": ("hand-label", 1), "audit": ("audit", 1), "quotes": ("quotes", 1)}),

    beat("B08", "WHYME", "Q7. Existing skills with real evidence (public repos, resume); new skills named honestly.",
         "Why this project? Some skills I already have. I've built Python and Fast A P I services, at Duma Info "
         "Services and in my public Market Data Service repo. I built Screener, a Chrome extension that filters "
         "reposted job listings. And as a software engineer intern at Wave Life Sciences, I built an AI assistant "
         "with Lang Graph, and testing agents in Claude Code. What's new for me is the discipline: contracts and "
         "tests before code, held-out evaluation, permissions enforced in code, and a human approval gate before "
         "anything moves.",
         34, "EfWhyMe", {},
         [{"at": "Python", "event": "row: Python + FastAPI | repo, Duma"},
          {"at": "Chrome", "event": "row: Screenr"},
          {"at": "intern", "event": "row: LangGraph assistant"},
          {"at": "Claude", "event": "row: Claude Code test agents"},
          {"at": "contracts", "event": "New to me: four pills"}],
         cue_words={"python": ("python", 1), "screenr": ("chrome", 1), "wave": ("intern", 1),
                    "claude": ("claude", 1), "contracts": ("contracts", 1), "evaluation": ("evaluation", 1),
                    "permissions": ("permissions", 1), "gate": ("gate", 1)}),

    beat("B09", "OUTRO", "Outro: title restated, authorship and voice disclosed again.",
         "Early Bird won't apply for me. It will make sure I see every new software job, early, with the evidence "
         "in front of me. Then I apply. This was Vrajesh. The script was drafted with Claude from my decisions, and "
         "read by a synthetic voice.",
         14, "EfOutro", {},
         [{"at": 0.0, "event": "title returns with the sun"},
          {"at": "see", "event": "verb pills"},
          {"at": "Vrajesh", "event": "author and colophon"}],
         cue_words={"see": ("see", 1), "evidence": ("evidence", 1), "apply": ("apply", 2), "name": ("vrajesh", 1)},
         lane="bookend", tail_silence_s=1.0),
]

METADATA = {
    "slug": SLUG,
    "title": TITLE,
    "topic": "INFO 7375 - Final Project Pitch Film",
    "concept": "Early Bird: watch my target companies' public boards, report every new SWE/AI posting, quote real blockers",
    "student": "Vrajesh Nasit",
    "course": "INFO 7375",
    "source_script": "SCRIPT.md (v1.0, 2026-10-24)",
    "engine": "kokoro",
    "voice_kokoro": VOICE,
    "clock": "narration",
    "palette": "claude",
    "aspect_ratio": "16:9",
    "fps": 30,
    "honesty": {
        "built": False,
        "real": "B02/B03/B06/B07: Commure snapshots saved 2026-10-14 and 2026-10-23, the ID diff and the "
                "greenhouse-watch run the author ran on 2026-10-24, and the 2026-10-14 probe; labelled REAL",
        "mockups": "every product visual is labelled PLANNED or CONSTRUCTED",
        "companies": "the probe boards are example companies, not the author's private list",
        "narration": "script drafted with Claude from the author's decisions; synthetic Kokoro am_onyx voice; "
                     "disclosed in B00 and B09",
    },
}


def norm(tok: str) -> str:
    tok = unicodedata.normalize("NFKD", tok)
    tok = "".join(c for c in tok if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", tok.lower())


def anchors(b: dict) -> dict:
    return {k: tuple(v) for k, v in (b.get("cue_words") or {}).items()}


def check_cue_words(beats: list[dict]) -> None:
    """Every cue word must occur in the narration often enough, before any audio exists."""
    for b in beats:
        words = [norm(w) for w in b["narration_text"].split()]
        for key, (word, occ) in anchors(b).items():
            if words.count(norm(word)) < occ:
                sys.exit(f"FATAL {b['beat_id']}: cue '{key}' wants occurrence {occ} of '{word}', "
                         f"narration has {words.count(norm(word))}")


AUDIO_FIELDS = ("actual_duration_s", "audio_file")


def write_spec() -> None:
    check_cue_words(BEATS)
    sheet = {"metadata": dict(METADATA), "beats": json.loads(json.dumps(BEATS))}
    # keep measured audio (and its synced props) for any beat whose narration did not change
    if SHEET.is_file():
        old = {b["beat_id"]: b for b in json.loads(SHEET.read_text(encoding="utf-8"))["beats"]}
        for b in sheet["beats"]:
            prev = old.get(b["beat_id"])
            if prev and prev.get("narration_text") == b["narration_text"]:
                for f in AUDIO_FIELDS:
                    if f in prev:
                        b[f] = prev[f]
                for k in ("durationSeconds", "cues"):
                    if k in prev["shot"]["remotion"]["props"]:
                        b["shot"]["remotion"]["props"][k] = prev["shot"]["remotion"]["props"][k]
    est = sum(b["estimated_duration_s"] for b in BEATS)
    sheet["metadata"]["total_estimated_duration_seconds"] = est
    SHEET.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    words = sum(len(b["narration_text"].split()) for b in BEATS)
    print(f"wrote {SHEET}\n  beats: {len(BEATS)}  narration words: {words}  estimated: {est}s")


def sync() -> None:
    sheet = json.loads(SHEET.read_text(encoding="utf-8"))
    if not WORDS.is_file():
        sys.exit(f"FATAL: {WORDS} missing. Run generate_audio_kokoro.py, then align.py, first.")
    doc = json.loads(WORDS.read_text(encoding="utf-8"))
    fps = float(doc.get("fps") or 30)
    for b in sheet["beats"]:
        bid = b["beat_id"]
        dur = b.get("actual_duration_s")
        if not dur:
            sys.exit(f"FATAL {bid}: no actual_duration_s. Generate audio first.")
        props = b["shot"]["remotion"]["props"]
        props["durationSeconds"] = float(dur)
        keyed = anchors(b)
        if not keyed:
            print(f"  {bid}  {dur:6.2f}s  (no word cues)")
            continue
        timed = doc["beats"].get(bid)
        if not timed:
            sys.exit(f"FATAL {bid}: no word timings in {WORDS.name}")
        times = {}
        for key, (word, occ) in keyed.items():
            hits = [w for w in timed if norm(w["text"]) == norm(word)]
            if len(hits) < occ:
                sys.exit(f"FATAL {bid}: cue '{key}' word '{word}' (occurrence {occ}) not in words.json")
            times[key] = round(hits[occ - 1]["startFrame"] / fps, 3)
        props["cues"] = times
        order = sorted(times.items(), key=lambda kv: kv[1])
        print(f"  {bid}  {dur:6.2f}s  " + "  ".join(f"{k}@{v:.2f}" for k, v in order))
    total = sum(b["actual_duration_s"] for b in sheet["beats"])
    sheet["metadata"]["total_actual_duration_seconds"] = round(total, 2)
    SHEET.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"synced {SHEET.name}: {total:.2f}s ({int(total // 60)}:{total % 60:05.2f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sync", action="store_true", help="stamp measured durations and word cues into props")
    a = ap.parse_args()
    sync() if a.sync else write_spec()
