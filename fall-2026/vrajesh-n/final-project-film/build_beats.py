#!/usr/bin/env python3
"""Build beat_sheet.json for the Early Bird pitch film, then sync it to the measured audio.

Source script: SCRIPT.md (v0.2, 2026-10-14). Narration below is that script, respelled
only where Kokoro would misread it ("Info seventy-three seventy-five" for INFO 7375,
"Screener" for Screenr, "Fast A P I" for FastAPI). Every on-screen figure is listed in
FACTCHECK.md with its source; the only measured figures are from evidence/2026-10-14/,
because Early Bird is not built.

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
    beat("B00", "OPEN", "Cold open: who is speaking, the synthetic-voice disclosure, and the need in one breath.",
         "Hi, I'm Vrajesh. This is my final project pitch for Info seventy-three seventy-five, read by a "
         "synthetic voice from my own script. I graduate in December, and I'm job hunting right now. In this "
         "market, I don't want to skip a single software job. I want to see every new one, early.",
         20, "EbOpen", {},
         [{"at": 0.0, "event": "title lockup 'Early Bird.' over a rising sun line"},
          {"at": "synthetic", "event": "honesty chip: synthetic voice, my script"},
          {"at": "December", "event": "chip: graduating December 2026"},
          {"at": "skip", "event": "a row of job cards; none is crossed out"},
          {"at": "early", "event": "the newest card lifts and glows"}],
         cue_words={"name": ("vrajesh", 1), "voice": ("synthetic", 1), "december": ("december", 1),
                    "skip": ("skip", 1), "early": ("early", 1)},
         lane="bookend"),

    beat("B01", "WHAT", "Q1. One sentence, then the artifact and its form.",
         "My project is Early Bird, a small Python agent. Each time I run it, it checks the job boards of the "
         "twenty-five to thirty companies on my list, and reports only the software, full-stack and AI postings "
         "that are new since the last run. The finished artifact is a public GitHub repository: a command-line "
         "tool with its tests, the saved board responses, and one report per run.",
         24, "EbWhatItIs", {},
         [{"at": "agent", "event": "the agent box appears centre"},
          {"at": "boards", "event": "company board chips stream in from the left"},
          {"at": "new", "event": "only two cards pass through to the report"},
          {"at": "artifact", "event": "artifact pills: repo, CLI, tests, saved responses, reports"}],
         cue_words={"agent": ("agent", 1), "boards": ("boards", 1), "new": ("new", 1),
                    "artifact": ("artifact", 1), "report": ("report", 1)}),

    beat("B02", "EXISTS", "Exists today: the real probe run of 2026-10-14, numbers from evidence/2026-10-14/summary.json.",
         "The agent doesn't exist yet. What exists is one probe I ran this morning, October fourteenth, against "
         "five public job boards: Kuh-mure, Stripe, Figma, Databricks and Palantir. These are example companies, "
         "not my private list. Two thousand one hundred fifty-six postings came back, and I saved every raw response.",
         22, "EbProbe", {},
         [{"at": "probe", "event": "terminal plate, REAL RUN 2026-10-14 chip"},
          {"at": "boards", "event": "five real output rows land one by one"},
          {"at": "example", "event": "caption: example companies, not my list"},
          {"at": "thousand", "event": "hero counter climbs to 2,156"},
          {"at": "saved", "event": "raw-file chips drop into a folder"}],
         cue_words={"probe": ("probe", 1), "boards": ("boards", 1), "example": ("example", 1),
                    "total": ("thousand", 1), "saved": ("saved", 1)}),

    beat("B03", "WHY", "Q2. Two real alternatives examined (greenhouse-watch read 2026-10-14; LinkedIn Job Match "
         "from launch coverage) and the specific difference.",
         "Two things already exist. The course's own greenhouse-watch tool watches one board at a time, and keeps "
         "only postings that match my resume keywords. In its demo, Figma posted eleven new jobs in four days, and "
         "it kept none. LinkedIn's Job Match compares my profile with a posting, but only for jobs on LinkedIn, and "
         "I can't re-run how it decided. Early Bird watches my whole list in one run. It keeps every software job, "
         "instead of scoring skill gaps away. It only flags hard blockers, like five years required, and it quotes "
         "the line, and code checks that the quote is really in the posting. It never applies for me.",
         42, "EbAlternatives", {},
         [{"at": "tool", "event": "column: greenhouse-watch"},
          {"at": "none", "event": "stat pill: Figma demo, 11 new, 0 kept"},
          {"at": "compares", "event": "column: LinkedIn Job Match"},
          {"at": "whole", "event": "column: Early Bird (planned); its unique row lights"},
          {"at": "quotes", "event": "a quoted blocker line with a check mark"}],
         cue_words={"gw": ("tool", 1), "none": ("none", 1), "linkedin": ("compares", 1),
                    "eb": ("whole", 1), "keeps": ("keeps", 2), "quotes": ("quotes", 1), "never": ("never", 1)}),

    beat("B04", "WHO", "Q3. The reader, and their first sixty seconds. Output is CONSTRUCTED (nothing is built).",
         "Who opens it? A hiring manager for a full-stack or AI engineering role. In the first sixty seconds, they "
         "run one command on labeled sample data, and open the report: new postings, quoted blockers, and the tests "
         "that passed. The other user is me, before every application session.",
         20, "EbFirstMinute", {},
         [{"at": "hiring", "event": "reader pill"},
          {"at": "command", "event": "the command types into a terminal plate"},
          {"at": "report", "event": "constructed report rows appear, labelled CONSTRUCTED"},
          {"at": "me", "event": "second reader pill: me, before applying"}],
         cue_words={"hiring": ("hiring", 1), "command": ("command", 1), "report": ("report", 1),
                    "blockers": ("blockers", 1), "tests": ("tests", 1), "me": ("me", 1)}),

    beat("B05", "PROVES", "Q4. Course topics tied to the planned evidence for each.",
         "What does it prove about me? Prompt contracts: Claude must answer in a fixed format, and a validator "
         "rejects anything else. Verification: a rule anyone can recompute, next to a labeled Claude judgment. "
         "Agent loops, with budgets and honest exit statuses. And evaluation: twenty postings I label by hand, "
         "with ten held back for the final test.",
         22, "EbProves", {},
         [{"at": "contracts", "event": "tile 1: prompt contract, a JSON shape and a red reject"},
          {"at": "verification", "event": "tile 2: record beside judgment"},
          {"at": "loops", "event": "tile 3: a loop with a budget bar and exit tags"},
          {"at": "evaluation", "event": "tile 4: 20 label dots, 10 split off as held out"}],
         cue_words={"contracts": ("contracts", 1), "verification": ("verification", 1), "loops": ("loops", 1),
                    "evaluation": ("evaluation", 1), "held": ("held", 1)}),

    beat("B06", "SCOPE", "Q5. One deliberate exclusion, the first piece that runs, and how to verify it.",
         "What's out, on purpose: auto-applying, logging in, messaging anyone, and scraping LinkedIn. Companies on "
         "their own hiring systems, like Google, will be marked unsupported, not guessed at. The first piece I'll "
         "make run is the watcher on one board, Kuh-mure. Run one is a baseline and reports zero new. A later run "
         "reports only new posting IDs, and anyone can check that by comparing the two saved files. As a second, "
         "independent check, I'll run the course's greenhouse-watch on the same saved data, and compare our lists.",
         36, "EbFirstRun", {},
         [{"at": "out", "event": "four excluded actions, struck through"},
          {"at": "unsupported", "event": "Google chip greys to 'unsupported'"},
          {"at": "baseline", "event": "run 1 file card: baseline, 0 new"},
          {"at": "later", "event": "run 2 file card: only new IDs highlighted"},
          {"at": "independent", "event": "greenhouse-watch card joins with an equals sign"}],
         cue_words={"out": ("out", 1), "unsupported": ("unsupported", 1), "first": ("first", 1),
                    "baseline": ("baseline", 1), "later": ("later", 1), "comparing": ("comparing", 1),
                    "independent": ("independent", 1)}),

    beat("B07", "RISK", "Q6. One concrete, project-specific risk (real titles from evidence/2026-10-14) and the mitigation.",
         "What could break it? Keeping every software job only works if software job is decided correctly. My "
         "probe's simple keyword rule matched seven hundred eighty-nine titles, and some of them are sales jobs, "
         "like Account Executive, AI Sales, at Stripe. If the report fills with noise, I'll stop reading it. So I'll "
         "write the rule before the code, hand-label real postings, audit thirty random rejects, and only accept a "
         "Claude verdict that quotes the posting.",
         30, "EbRisk", {},
         [{"at": "matched", "event": "real titles fall through a keyword sieve; counter 789 of 2,156"},
          {"at": "sales", "event": "SALES stamp on 'Account Executive, AI Sales'"},
          {"at": "noise", "event": "the report card fogs over"},
          {"at": "rule", "event": "four mitigation pills clear the fog"}],
         cue_words={"matched": ("matched", 1), "sales": ("sales", 1), "noise": ("noise", 1),
                    "rule": ("rule", 2), "hand": ("hand-label", 1), "audit": ("audit", 1), "quotes": ("quotes", 1)}),

    beat("B08", "WHYME", "Q7. Existing skills with real evidence (public repos, resume); new skills named honestly.",
         "Why this project? Some skills I already have. I've built Python and Fast A P I services, at Duma Info "
         "Services and in my public Market Data Service repo. I built Screener, a Chrome extension that filters "
         "reposted job listings. And as a software engineer intern at Wave Life Sciences, I built an AI assistant "
         "with Lang Graph, and testing agents in Claude Code. What's new for me is the discipline: contracts and "
         "tests before code, held-out evaluation, permissions enforced in code, and a human approval gate before anything moves.",
         34, "EbWhyMe", {},
         [{"at": "Python", "event": "chip into 'Already have': Python + FastAPI"},
          {"at": "Chrome", "event": "chip: job-listing filter (Screenr)"},
          {"at": "intern", "event": "chip: LangGraph assistant"},
          {"at": "Claude", "event": "chip: Claude Code test agents"},
          {"at": "contracts", "event": "chips into 'New to me': four disciplines"}],
         cue_words={"python": ("python", 1), "screenr": ("chrome", 1), "wave": ("intern", 1),
                    "claude": ("claude", 1), "contracts": ("contracts", 1), "evaluation": ("evaluation", 1),
                    "permissions": ("permissions", 1), "gate": ("gate", 1)}),

    beat("B09", "OUTRO", "Neutral student outro: title restated, no channel handle, voice disclosed again.",
         "Early Bird won't apply for me. It makes sure I see every new job, early, with the evidence in front of me. "
         "Then I apply. This was Vrajesh, and this pitch was read by a synthetic voice.",
         12, "EbOutro", {},
         [{"at": 0.0, "event": "title 'Early Bird.' returns"},
          {"at": "see", "event": "verb chips land"},
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
    "source_script": "SCRIPT.md (v0.2)",
    "engine": "kokoro",
    "voice_kokoro": VOICE,
    "clock": "narration",
    "palette": "claude",
    "aspect_ratio": "16:9",
    "fps": 30,
    "honesty": {
        "built": False,
        "real": "B02 and B07 show real output of evidence/probe.py, run 2026-10-14, labelled REAL RUN",
        "mockups": "every product visual is labelled CONSTRUCTED or PLANNED",
        "companies": "the five probe boards are example companies, not the author's private list",
        "narration": "synthetic Kokoro am_onyx voice reading the author's script; disclosed in B00 and B09",
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
