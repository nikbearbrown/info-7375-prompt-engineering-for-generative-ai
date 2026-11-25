#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the INFO 7375 Final Project Film (v2 of the pitch film).

Structure (the assignment, in this order): 1 executive summary · 2 introduction · 3 methods · 4 evaluation.
Style: brutalist.art show-tell, as in the pitch film (one drawing per beat, short labels, the voice explains).
Every body beat carries a corner tag (constructed drawing + ran <date> / proposed) and a part chip (top right).

Sources for every claim: FACTCHECK.md. New numbers come from board-resolver/runs/live-2026-11-23/
(summary.json, log.jsonl, proposals.json, decisions.json, coverage.json) and board-resolver tests.

Run: python make_sheet.py   (writes beat_sheet.json next to this file)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "sponsorscout-final-project-film"
TITLE = "SponsorScout"
AUTHOR = "Akshit Verma"
VOICE = "am_michael"          # Kokoro v1.0, free and local (Akshit's choice for the pitch film, 2026-10-14)
WPS = 2.6                     # measured for am_michael on 2026-10-14; the audio sets the real length

PARTS = {1: "1 · executive summary", 2: "2 · introduction", 3: "3 · methods", 4: "4 · evaluation"}


def est(text):
    return round(len(text.split()) / WPS, 1)


def beat(bid, part, answers, tag, narration, cls, image, labels):
    return {
        "beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
        "answers": answers, "part": PARTS[part] if part else "", "honesty_tag": tag,
        "narration_text": narration, "estimated_duration_s": est(narration),
        "voice": VOICE, "engine": "kokoro",
        "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "motion_claim": image,
                 "labels": labels, "show": [{"at": 0.02, "event": f"corner tag: '{tag}'"}],
                 "manim": {"class": cls}},
    }


RAN_OCT = "constructed drawing · ran 2026-10-03"
RAN_NOV = "constructed drawing · ran 2026-11-23"
PROPOSED = "constructed drawing · proposed"

B = [
    beat("BOPEN", None, "title", "",
         "SponsorScout. A final project film by Akshit Verma, in four parts.",
         "BOPEN_Title",
         "SponsorScout writes on beside its mark (a crate under a scout's lens); the byline; the four parts appear "
         "in a two-by-two grid on 'in four parts'.",
         ["SponsorScout", "a final project film by Akshit Verma", "1 · executive summary", "2 · introduction",
          "3 · methods", "4 · evaluation"]),

    # ── 1 · executive summary: what, and why anyone should care (no "how") ──
    beat("P1A", 1, "the problem", "constructed drawing",
         "International students looking for data jobs have a short clock, and only some employers sponsor visas. "
         "So we apply to sponsors. But many of them have no entry-level data job open today, and those applications go nowhere.",
         "P1A_Problem",
         "A clock face (a short clock); three sponsor crates; a stack of applications with an arrow to them; grey "
         "lamps above the crates (nothing open today); a cross on the arrow (go nowhere).",
         ["a short clock", "sponsors", "applications", "nothing open today", "go nowhere"]),
    beat("P1B", 1, "what it is", RAN_OCT,
         "SponsorScout tells the student, for each sponsor, whether to apply, network, check by hand, or skip, "
         "with the public record behind every answer. A strong sponsor with nothing open isn't dropped. "
         "It goes on a networking list.",
         "P1B_Verdicts",
         "A company crate -> the SponsorScout block -> four trays on their words (apply, network, check by hand, skip); "
         "a record sheet; a small crate drops into 'network' and a terracotta ring marks it.",
         ["a sponsor", "SponsorScout", "apply", "network", "check by hand", "skip", "record"]),
    beat("P1C", 1, "limits + why it matters to me", "constructed drawing",
         "It never applies, emails, or contacts anyone. The person decides. "
         "I'm building it because I'm job hunting too, and I wanted a smarter strategy than a hundred-plus applications a day.",
         "P1C_Why",
         "Application, email and message icons slide to a dark wall and are crossed out; a list 'you decide'. Then a pile "
         "of applications ('100+ a day') gives way to one short list.",
         ["apply", "email", "contact", "you decide", "100+ applications a day", "a short list"]),

    # ── 2 · introduction: what others have done ──
    beat("P2A", 2, "prior work", "constructed drawing · no logos or screenshots",
         "What already exists? My Visa Jobs lists sponsors and their past job counts; I looked at it in October. "
         "H one B Grader grades employers on past approvals and denials. "
         "Interstride, which universities provide, shows sponsorship history and filters jobs by visa.",
         "P2A_Others",
         "Three plain panels, names in text only: MyVisaJobs (rows of past-count bars), H1BGrader (a letter grade), "
         "Interstride (a history bar row and filter chips).",
         ["MyVisaJobs", "past job counts", "H1BGrader", "grades past approvals", "Interstride", "history · visa filter"]),
    beat("P2B", 2, "prior work 2 + the gap", "constructed drawing · scorer ran 2026-10-03",
         "The Reallocation Engine's own scorer, which I had Claude Code run in October, gives a sponsor with no open job "
         "a zero, and skips it. These tools show who sponsored before, or what's open now. "
         "None that I found turns a proven sponsor with nothing open into a networking target. That's the gap.",
         "P2B_Gap",
         "A sponsor crate with a dark lamp. Top path, grey and dashed: engine scorer -> 0 -> skip. Bottom path, solid: "
         "SponsorScout -> network list; the crate travels into it; 'the gap' lands beside it.",
         ["no open job", "engine scorer", "0", "skip", "SponsorScout", "network list", "the gap"]),

    # ── 3 · methods: how, data, resources ──
    beat("P3A", 3, "data sources", "constructed drawing · all public data",
         "The data is public. Sponsorship records from the Eighty Days to Stay file. Recent funding from S E C Form D filings. "
         "Open jobs from the public Greenhouse, Lever, and Ashby job boards. The job seeker is fictional.",
         "P3A_Data",
         "Three sources rise on their words: a records sheet (H-1B sponsorship · 80 Days to Stay), a filings sheet "
         "(Form D · SEC), three small board pages (Greenhouse · Lever · Ashby); 'job seeker: fictional'.",
         ["H-1B sponsorship", "80 Days to Stay", "Form D", "SEC filings", "Greenhouse", "Lever", "Ashby", "job seeker: fictional"]),
    beat("P3B", 3, "the three checks", RAN_OCT,
         "Each sponsor gets three checks: has it sponsored data roles, has it raised money recently, "
         "and is an entry-level data job open today? The answers set the verdict. "
         "The prototype ran on October third, on one hundred twenty-three sponsors.",
         "P3B_Checks",
         "A moving conveyor through three depth-correct gates; each lamp pulses on its question; '123 sponsors · Oct 3'.",
         ["sponsored? (H-1B)", "funded? (Form D)", "open today? (job board)", "123 sponsors · Oct 3"]),
    beat("P3C", 3, "the board resolver loop", RAN_NOV,
         "But only sixteen of them had a known job board, so most answers were check by hand. "
         "So, with Claude Code, I built a board resolver. It tries names built from each company's name, one request at a time, "
         "saves every raw response with a fingerprint, and stops when it's done, out of budget, or hitting errors.",
         "P3C_Resolver",
         "'16 / 123 known boards'; the resolver block; a three-step loop (try a name -> one request -> save + fingerprint) "
         "with a return arrow; a stop panel: done · budget · errors.",
         ["16 / 123", "known boards", "board resolver", "try a name", "one request", "save + fingerprint",
          "stops: done · budget · errors"]),
    beat("P3D", 3, "the human gate + permissions", RAN_NOV,
         "It only proposes. I approve or refuse each board, and my decision is tied to the fingerprint of the response I saw. "
         "It can only read from those three sites, and it has no way to send anything.",
         "P3D_Gate",
         "A proposal sheet with a real fingerprint (c50b5646d54e, Anaplan) -> a dark gate square 'my decision' -> "
         "approve / refuse trays; 'reads 3 sites only · no way to send'.",
         ["proposal", "c50b5646d54e", "my decision", "approve", "refuse", "reads 3 sites only · no way to send"]),
    beat("P3E", 3, "resources + next steps", "constructed drawing · next steps proposed",
         "I have what I need: Claude Code, free public job boards, no keys, and no paid compute. "
         "Next, I'll re-run the verdicts on the new boards, then evaluate them.",
         "P3E_Resources",
         "A checklist ticks on its words (Claude Code, free public job boards, no API keys, $0 compute); two dashed "
         "next-step boxes (re-run verdicts -> evaluate).",
         ["Claude Code", "free public job boards", "no API keys", "$0 compute", "re-run verdicts", "evaluate"]),

    # ── 4 · evaluation: what is measured, what would say it worked or didn't ──
    beat("P4A", 4, "coverage result", "real numbers · live run 2026-11-23",
         "How will I know it worked? First, coverage. On November twenty-third, the resolver made six hundred twenty-nine requests, "
         "all to the three allowed sites, and found candidate boards for thirty-nine companies. "
         "After my review, coverage went from sixteen to fifty, of one hundred twenty-three.",
         "P4A_Coverage",
         "'629 requests · 3 sites only'; '39 candidates'; the coverage bar fills from 16/123 to 50/123 (real, after G1); "
         "the number changes 16 -> 50.",
         ["629 requests · 3 sites only", "39 candidates", "16", "50 / 123", "boards confirmed at my gate"]),
    beat("P4B", 4, "failures it made", "real cases · live run 2026-11-23",
         "It also got things wrong, in ways I could check. Five boards belonged to other companies, like a childcare center. "
         "Claude flagged them, and I refused all five. The name check called Weight Watchers a mismatch, though it's the right company. "
         "Five approved boards are empty, and sixty-seven companies showed no board under the names it tried.",
         "P4B_Failures",
         "Two board sheets with their real names (Slice Talent Community; The Village Learning Center), crossed; "
         "'5 refused'. Then: 'Weight Watchers' marked mismatch but right; an empty tray '5 empty'; '67 no board found'.",
         ["talent -> Slice Talent Community", "village -> a childcare center", "5 refused",
          "Weight Watchers: called a mismatch, but right", "5 empty boards", "67 no board found"]),
    beat("P4C", 4, "the bug no test caught", "constructed drawing · found 2026-11-23",
         "One bug got past every test. On a Windows console, the command saved my approval, then crashed. "
         "A test now reproduces it, and all twenty-eight tests pass.",
         "P4C_Bug",
         "A terminal; a decision sheet with a check 'saved'; a cross on the terminal 'then crashed'; a test pill; "
         "'28 / 28 tests pass'.",
         ["saved", "then crashed", "regression test", "28 / 28 tests pass"]),
    beat("P4D", 4, "how the verdicts will be judged", PROPOSED,
         "Next, the verdicts. Before tuning anything, I'll set aside a hand-checked set of sponsors. "
         "If fewer than nine in ten apply verdicts are right on that set, it didn't work. "
         "And after fourteen days, I'll re-check the networking targets for new postings. "
         "This sample can show what it gets wrong. It can't show that anyone gets hired.",
         "P4D_Plan",
         "A sealed dashed box 'held-out set · set aside first'; a bar with a threshold tick at 9/10 'apply verdicts right'; "
         "a 14-day grid; 'can show: what it gets wrong' / 'can't show: hires'.",
         ["held-out set", "set aside first", "pass: 9 in 10 apply verdicts right", "14 days",
          "can show: what it gets wrong", "can't show: hires"]),
]

OUTRO = {
    "beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW", "answers": "outro",
    "narration_text": f"{TITLE}. A film by {AUTHOR}.",
    "estimated_duration_s": 5.0, "voice": VOICE, "engine": "kokoro",
    "shot": {"type": "REMOTION", "source": "own",
             "show": [{"at": 0.0, "event": "title restates; author credit; no instructor handle"}],
             "remotion": {"pattern": "PitchOutro",
                          "props": {"title": TITLE, "handle": AUTHOR, "author": AUTHOR,
                                    "course": "INFO 7375 · Final Project Film", "byline": "a film by"}}},
    "kind": "outro_voice", "tail_silence_s": 1.0,
}

for b in B:
    b["qc"] = {"sparse_by_design": True,
               "sparse_reason": ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, the voice "
                                 "carries the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and "
                                 "contrast still apply.")}
BEATS = B + [OUTRO]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT FILM",
    "skill": "show-tell", "style_preset": "show-tell", "kind": "pitch",
    "author": AUTHOR, "channel": AUTHOR, "channel_title": AUTHOR,
    "persona": f"{AUTHOR}'s script, read by a synthetic voice (Kokoro {VOICE}); 'a film BY {AUTHOR}', never 'I am'; disclosed in README.md and SOURCES.md",
    "presenter": f"synthetic voice (Kokoro {VOICE}), narrating {AUTHOR}'s script — not the instructor's persona",
    "in_for_bear": False, "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Teardown",
    "fps": 24, "aspect_ratio": "16:9", "width": 1920, "height": 1080, "captions": True,
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Project film in the assignment's four parts: opens on its own title beat (BOPEN, Manim); no verdict "
                              "card; no Your Turn (no viewer task). The outro stays, credited to the author."),
    "audience": "INFO 7375 graders; a hiring manager for Data Analyst / Data Engineer roles",
    "source_doc": "Assignment 1 run outputs (the-reallocation-engine @ a1d321f); board-resolver/runs/live-2026-11-23; "
                  "board-resolver tests; MyVisaJobs (Akshit, 2026-10-07); H1BGrader and Interstride (web search by Claude, 2026-11-23)",
    "honesty_rule": "Past tense only for what exists and can be shown; every drawn beat tagged on screen.",
    "playlist": "INFO 7375", "cut": "review",
    "tags": ["INFO 7375", "final project", "H-1B", "board resolver", "data analyst", "data engineer"]},
    "beats": BEATS}

CARRY = ("audio_file", "actual_duration_s", "render_duration_s", "build")
old_path = HERE / "beat_sheet.json"
if old_path.exists():
    old = {b["beat_id"]: b for b in json.loads(old_path.read_text(encoding="utf-8")).get("beats", [])}
    for b in BEATS:
        o = old.get(b["beat_id"])
        if o and o.get("narration_text") == b["narration_text"]:
            for k in CARRY:
                if k in o:
                    b[k] = o[k]
            cues = (((o.get("shot") or {}).get("remotion") or {}).get("props") or {}).get("cues")
            if cues and b["shot"].get("remotion"):
                b["shot"]["remotion"]["props"]["cues"] = cues
            if b.get("actual_duration_s") and b["shot"].get("remotion"):
                b["shot"]["remotion"]["props"]["durationSeconds"] = b["actual_duration_s"]

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

total = sum(b.get("actual_duration_s") or b["estimated_duration_s"] for b in BEATS)
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(f"{len(BEATS)} beats · {words} words · {total:.0f}s ({total/60:.1f} min)")
for b in BEATS:
    print(f"  {b['beat_id']:6} {(b.get('actual_duration_s') or b['estimated_duration_s']):5.1f}s  {b.get('part','')}  {b.get('answers','')}")
if not 150 <= total <= 270:
    print(f"\nWARNING: {total:.0f}s is outside 2.5-4.5 min.", file=sys.stderr)
