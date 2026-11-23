#!/usr/bin/env python3
"""make_sheet.py — writes beat_sheet.json for Varnika M's Final Project Film (four-part version).

Project: the job-search agent built across JS1 and JS2 and continued in JS3–JS5.
Structure (Professor Bear's film guidance): 1 executive summary, 2 what others have done,
3 methods, 4 evaluation. Every scene shows its part label at the top.

Show-tell style (brutalist.art skills/make/show-tell): one drawn picture per beat, few labels,
the voice explains. First person, as Varnika, in the Kokoro computer voice she chose
(am_onyx, the same voice as her Week 01 and October films). Script drafted by Claude Code
from her JS1/JS2 records and her answers on 2026-11-23; she reviews and approves it.

Re-running this file DROPS measured durations; run it only before (re)voicing.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "varnika-final-project-film"
TITLE = "A Job-Search Agent You Can Check"
HANDLE = "Varnika M"
VOICE = "am_onyx"
JS1 = "JS1 · Anthropic board · live run 2026-10-31"
JS2 = "JS2 · live run 2026-11-10"
SPARSE = ("show-tell: one drawn object or scene on a cream stage, minimal labels, the voice "
          "carries the explanation; only underfill and clustered are waived.")


def beat(bid, part, question, narration, cls, visual, labels, constructed, **extra):
    b = {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
         "part": part, "question": question, "narration_text": narration,
         "narration_status": "DRAFT (Claude Code) · awaiting Varnika's review",
         "estimated_duration_s": round(len(narration.split()) / 3.3, 1),
         "voice": VOICE, "engine": "kokoro",
         "qc": {"sparse_by_design": True, "sparse_reason": SPARSE},
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": visual, "motion_claim": visual,
                  "show": [{"at": 0.1, "event": visual}], "manim": {"class": cls},
                  "labels": labels, "constructed": constructed}}
    for k in ("source_tag", "evidence"):
        if k in extra:
            b["shot"][k] = extra.pop(k)
    b.update(extra)
    return b


P1, P2, P3, P4 = "1 · What and why", "2 · What others have done", "3 · How I'll build it", "4 · How I'll know it worked"

B = [
 # ── Part 1: executive summary (no "how") ──────────────────────────────────────────────
 beat("B01", P1, "What is it",
      "I'm Varnika. I'm searching for a job myself, and reading hundreds of job postings by hand takes hours. "
      "So my final project is an agent that does the reading. It watches job boards, picks out the few postings "
      "that fit one person, and shows why each one made the list.",
      "B01_Funnel", "A tall stack of posting cards pours into a funnel; three cards come out, each with a 'why' tag.",
      ["job boards", "shortlist", "why"], "drawing; the shortlist with reasons is planned"),
 beat("B02", P1, "Why it matters: most postings don't fit",
      "Most postings don't fit. On October thirty-first, my written rules checked all six hundred and seventy-five "
      "postings on Anthropic's job board against a made-up candidate. Only one matched.",
      "B02_OneOf675", "A grid of 675 small dots fills in; one dot turns terracotta and is circled.",
      ["675 postings", "1 match"], False, source_tag=JS1,
      evidence="../../js1-contract-and-watch/README.md (run table; 1 match of 675)", tail_silence_s=1.0),
 beat("B03", P1, "A person decides",
      "And it never acts on its own. It won't apply for jobs or send anything. It will hand a person the shortlist, "
      "and only that person can say yes, no, or not yet.",
      "B03_PersonDecides", "The shortlist card slides to a simple person figure; three buttons appear: yes, no, not yet.",
      ["yes", "no", "not yet"], "drawing; the approval step is planned (JS5)"),
 beat("B04", P1, "Why anyone should care",
      "That matters because a tool that picks jobs for you should show its reasons, so you can check it, "
      "instead of just trusting it.",
      "B04_Reasons", "A magnifying glass moves over a 'why' tag on a posting card; a check lands.",
      ["check it", "not trust it"], True),

 # ── Part 2: what others have done (filled from dated public pages) ────────────────────
 beat("B05", P2, "Job alerts",
      "What have other people done? The simplest tools are job alerts. LinkedIn and Indeed save your search, and "
      "send you new postings daily or weekly. But their help pages don't explain why a job matched.",
      "B05_Alerts", "A saved-search card sends envelopes to an inbox; a '?' hangs over the last envelope.",
      ["saved search", "daily or weekly", "why?"], "drawing of real features",
      source_tag="LinkedIn and Indeed help pages · checked 2026-11-23",
      evidence="evidence/others-2026-11-23/li_alerts.html; indeed.html"),
 beat("B06", P2, "AI matching and auto-apply",
      "Newer tools go further. LinkedIn's Skills Match compares your profile with the job description. Jobright "
      "says its agent matches roles and applies for you. LazyApply says its agent handles the entire application. "
      "Simplify's Autopilot submits with no review step, though its Copilot mode leaves the final click to you.",
      "B06_AutoApply", "A match dial on a posting card; then a stamp marks a pile of cards 'applied'; one card keeps a "
      "'you click submit' tag.",
      ["Skills Match", "Jobright", "LazyApply", "Simplify"], "drawing of claims on the companies' own pages",
      source_tag="company pages · checked 2026-11-23",
      evidence="evidence/others-2026-11-23/li_skills.html; jr_agent.html; lazy.html; simp_auto.html; simp_copilot.html"),
 beat("B07", P2, "Why mine still matters",
      "So finding jobs is automated, and so is applying. None of these pages mentions rules you can recheck, a "
      "separate program that checks each run, or a person approving the shortlist. That's what mine adds.",
      "B07_Different", "Three tags line up next to a shortlist: 'rules you can recheck', 'run checker', 'person approves'.",
      ["rules you can recheck", "run checker", "person approves"], True),

 # ── Part 3: methods ──────────────────────────────────────────────────────────────────
 beat("B08", P3, "Where the data comes from",
      "Here's how I'm building it. The data comes from public job board feeds that need no login: Anthropic on "
      "Greenhouse, Palantir on Lever, and Linear on Ashby. The candidate is made up, Aarav Patel, so no real "
      "person's data is used.",
      "B08_Data", "Three kraft boxes (Greenhouse, Lever, Ashby) feed a pipe; a profile card marked 'fictional' sits beside it.",
      ["Greenhouse", "Lever", "Ashby", "fictional"], False,
      evidence="../../js2-loop-tools-diff/config/boards.json; ../../js2-loop-tools-diff/persona/"),
 beat("B09", P3, "Built so far: JS1",
      "Two parts already work. In my first assignment, the agent watched one board, reported only new postings, "
      "and judged each one with five written rules: title, seniority, location, experience, and skills.",
      "B09_FiveRules", "Five small rule cards fall into a row under one board box; a 'new' tag lights on one posting.",
      ["title", "seniority", "location", "experience", "skills"], False, source_tag="JS1 · 73 tests",
      evidence="../../js1-contract-and-watch/CONTRACT.md (Rules 1–5)"),
 beat("B10", P3, "Built so far: JS2",
      "In the second, it became a loop over four boards on three systems, with a budget, and a permission policy "
      "in code that blocks any site not on its list. One run read one thousand and fourteen postings. It has a "
      "hundred and twenty-two tests, and a separate checker caught a real bug in one of my own runs.",
      "B10_Loop", "A loop arrow circles four board boxes (one marked 'fails on purpose'); a lock blocks an off-list site; "
      "a counter reads 1,014; a checker stamps 'caught'.",
      ["loop", "policy", "1,014", "122 tests"], False,
      source_tag=JS2 + " · 677 + 304 + 33 postings",
      evidence="../../js2-loop-tools-diff/README.md (live runs table; REVIEW-FINDINGS row 7b)"),
 beat("B11", P3, "Next steps",
      "Next, step by step. First, a filter I can read, with an audit of what it throws away, and the agent offered "
      "to Claude as a tool. Then a written plan before every run, a check on every claim, and memory across days. "
      "Last, the approval step, tied to the exact shortlist the person saw.",
      "B11_Steps", "Three steps rise left to right, labelled as each is named; an outline person stands on the last.",
      ["filter · tool", "plan · checks · memory", "approval"], "planned (JS3, JS4, JS5)"),
 beat("B12", P3, "Do I have what I need",
      "Do I have what I need? Yes. Python, with nothing to install. Claude Code, through my university. Free public "
      "job boards, and my laptop. No paid API credits are needed.",
      "B12_Have", "Four items land on a shelf with a check each: Python, Claude Code, public boards, laptop; a '$0 API credits' slip.",
      ["Python", "Claude Code", "public boards", "laptop"], False),

 # ── Part 4: evaluation ───────────────────────────────────────────────────────────────
 beat("B13", P4, "Check 1: rejected postings",
      "How will I know it worked? Four checks. One: I'll pull thirty postings the filter rejected, at random, and "
      "check each one by hand. If more than one of them fits the candidate, the filter failed.",
      "B13_Rejects", "A grid of thirty rejected cards; a magnifier steps across them; the pass line reads 'at most 1 of 30'.",
      ["30 rejected", "at most 1 of 30"], "planned check"),
 beat("B14", P4, "Check 2: must-skip list",
      "Two: a test list of postings it must skip, like a closed posting, the wrong location, or one that only "
      "matches keywords. If even one gets through, that's a fail. And a healthy run should skip at least half of "
      "what it sees.",
      "B14_MustSkip", "Three trap cards (closed, wrong location, keywords only) drop into a skip bin; a meter shows 'skip at least 50%'.",
      ["closed", "wrong location", "keywords only", "0 let through", "skip ≥ 50%"], "planned check"),
 beat("B15", P4, "Check 3: break it on purpose",
      "Three: I'll break it on purpose, and the separate checker has to catch every planted failure. "
      "In my second assignment, it already caught one.",
      "B15_Planted", "A wrench cracks a run card; the checker stamps 'NOT SUPPORTED' on it.",
      ["planted failure", "NOT SUPPORTED"], "drawing; the JS2 catch is real (seeded demonstration)",
      source_tag="JS2 · finished-wrong demonstration (seeded)",
      evidence="../../js2-loop-tools-diff/FINISHED-WRONG.md"),
 beat("B16", P4, "Check 4: approval",
      "Four: if the shortlist changes after a person approves it, the old yes must stop counting.",
      "B16_Fingerprint", "An approved shortlist with a fingerprint tag; one line changes; the 'approved' stamp turns grey: 'no longer counts'.",
      ["approved", "changed", "no longer counts"], "planned check (JS5)"),
 beat("B17", P4, "Worked or not",
      "If all four checks pass, it worked. If even one check fails, it didn't, and my final report will say which one.",
      "B17_Verdict", "Four check boxes tick one by one, then the word 'worked'; one box flips to an X and the word becomes 'didn't'.",
      ["worked", "didn't"], True),
]
B.append(beat("BOUT", "", "Outro", f"{TITLE}. {HANDLE}.", "BOUT_Title",
              "Title and name on the cream stage, beside a small shortlist card with a check.",
              [TITLE, HANDLE], False, tail_silence_s=1.0))
B[-1]["shot"]["remotion"] = {"props": {"title": TITLE, "handle": HANDLE, "subline": ""}}
B[-1]["shot"]["outro_note"] = ("Drawn in Manim (BOUT_Title), not the ClaudeTitleOutro component, which hard-codes the "
                               "instructor's handle. These props record exactly the title and name the scene shows.")

missing = [b["beat_id"] for b in B if b["narration_text"].startswith("PART2_")]
if missing:
    raise SystemExit(f"Part 2 narration not written yet: {missing}")

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT FILM",
    "skill": "show-tell", "style_preset": "show-tell",
    "channel": "varnika-m", "channel_title": HANDLE, "author": "Varnika M", "course": "INFO 7375",
    "persona": "Varnika M (first person)", "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "voice_reason": ("Varnika chose the animated film with a computer voice on 2026-11-23, the same Kokoro am_onyx "
                     "voice as her Week 01 and October films. Stock voice only: no instructor name, greeting or outro."),
    "clock": "narration", "palette": "claude", "register": "Plain",
    "fps": 24, "aspect_ratio": "16:9", "width": 1920, "height": 1080, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("The hesitant writer, terms card and Your Turn composer carry the instructor's narrator and "
                              "channel identity, which a student film may not show. B01 is the hook. BOUT is drawn in "
                              "Manim with the film title and Varnika's name."),
    "structure": ("Professor Bear's four parts, in order: 1 executive summary (B01–B04, no 'how'), 2 what others have "
                  "done (B05–B07), 3 methods (B08–B12), 4 evaluation (B13–B17)."),
    "constructed_rule": ("Drawings of anything not built yet carry a 'planned' label. Real numbers carry a source tag "
                         "naming the run they come from."),
    "claude_output_rule": "No Claude reply is shown in this film.",
    "audience": "Professor Bear and the INFO 7375 graders; a hiring manager reviewing Varnika's GitHub",
    "source_doc": "../../js1-contract-and-watch/, ../../js2-loop-tools-diff/, FACTCHECK.md",
    "tags": ["job-search agent", "agentic loop", "permission policy", "human approval", "Claude", "Python"]},
    "beats": B}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in B)
for p in (P1, P2, P3, P4):
    w = sum(len(b["narration_text"].split()) for b in B if b["part"] == p)
    print(f"{p}: {w} words, est {round(w / 201 * 60)} s")
print(len(B), "beats;", words, "words; est", round(words / 201 * 60), "s at the am_onyx rate")
