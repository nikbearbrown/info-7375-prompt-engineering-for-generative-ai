#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for job-search-agent (INFO 7375 Final Project Film, 2026-11-23).

SHOW-TELL style: one drawn picture per beat, minimal labels, the narration explains. Four parts,
in the professor's order: executive summary, introduction, methods, evaluation.
Narrated in the first person as Yash Saraf (Kokoro am_onyx voice reading Yash's script, as in his
pitch film); no instructor persona, name, or credit line.

Honesty rule: past tense only for what ran. JS1 and JS2 are built and tested; JS3 is in progress;
JS4, JS5 and the final evaluation are plans. Beats drawn from the 2026-11-23 screenshots say so on
screen; terminal beats show recorded output (evidence/terminal-2026-11-23.txt) as a labelled
reconstruction, not a live screen recording. The candidate is Priya Nair, a fictional persona.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
SLUG = "job-search-agent"
TITLE = "A Job-Search Agent You Can Check — Final Project Film"


def beat(bid, narration, cls, image, show):
    return {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
            "voice": "am_onyx", "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show, "manim": {"class": cls},
                     "motion_claim": image}}


B = [
 # ── Part 1: executive summary ──────────────────────────────────────────────────────────────
 beat("B01", "My final project is a job-search agent that you can check. It watches company job boards, and it only tells you about the jobs that are new since the last time it looked.",
      "B01_Watch", "Three kraft board boxes sit in a row; a terracotta scan line sweeps across them; posting cards pop up out of each box and a few of them get a terracotta 'new' dot.",
      [{"at": 0.2, "event": "boards"}, {"at": 0.5, "event": "scan sweeps"}, {"at": 0.8, "event": "new cards marked"}]),
 beat("B02", "For every new job, it says why the job fits the candidate, or why it does not, using written rules that anyone can check again.",
      "B02_Rules", "A posting card slides onto a rule page; four rule lines get a check or a cross one by one; the card drops into a 'keep' or 'reject' tray with a reason strip attached.",
      [{"at": 0.2, "event": "card onto rule page"}, {"at": 0.45, "event": "rule lines checked"}, {"at": 0.8, "event": "card filed with a reason"}]),
 beat("B03", "Then it stops, and a person makes the decision. It never applies for a job, never sends an email, and never logs in anywhere.",
      "B03_Person", "A short shortlist page slides up to a gate post where a person waits; then three actions, apply, email and log in, slide in and are each struck through.",
      [{"at": 0.2, "event": "shortlist reaches the person"}, {"at": 0.55, "event": "apply crossed"}, {"at": 0.75, "event": "email crossed"}, {"at": 0.9, "event": "log in crossed"}]),
 beat("B04", "Why does this matter? Job boards change all the time. When I ran my agent, one company, Databricks, had eighty new postings in about ten days. Checking that by hand is slow, and it is easy to miss things.",
      "B04_WhyCare", "A counter of seen postings runs from 924 to 1,004 while new cards pile up beside it; a 'by hand' magnifier scans the pile and misses cards.",
      [{"at": 0.3, "event": "counter runs 924 to 1,004"}, {"at": 0.55, "event": "cards pile up: 80 new"}, {"at": 0.85, "event": "magnifier misses cards"}]),
 beat("B05", "The candidate in this project is Priya Nair, a fictional person. I never use my real résumé.",
      "B05_Persona", "A résumé page drops in with the name Priya Nair; a terracotta 'fictional' stamp presses onto it.",
      [{"at": 0.2, "event": "résumé page"}, {"at": 0.6, "event": "fictional stamp"}]),
 # ── Part 2: introduction — what others have done ───────────────────────────────────────────
 beat("B06", "So what already exists? First, I tried LinkedIn. I searched for machine learning engineer jobs at Databricks in the United States, and it showed more than ninety-nine results. Many of them were staff-level roles.",
      "B06_LinkedIn", "A LinkedIn window fills with result rows and '99+ results'; several rows get a grey 'staff' tag.",
      [{"at": 0.35, "event": "result rows fill"}, {"at": 0.6, "event": "99+"}, {"at": 0.85, "event": "staff tags"}]),
 beat("B07", "LinkedIn gave a medium match, but that match was based on my own profile, not on Priya's résumé, so I could not compare it with my agent. Its first posting uses skills Priya has, like Python and MLflow, but it is a senior role. Matching skills alone is not enough.",
      "B07_LinkedInMatch", "A 'medium' match meter slides in, then a profile card labelled 'my profile, not Priya's' attaches to it; two skill chips light up on a posting card, then a 'senior' bar drops across the card.",
      [{"at": 0.15, "event": "medium meter"}, {"at": 0.35, "event": "my profile, not Priya's"}, {"at": 0.65, "event": "skills light up"}, {"at": 0.85, "event": "senior bar"}]),
 beat("B08", "Next, Jobright. I uploaded Priya's fictional résumé. For an AI Engineer role at Databricks, it gave a fifty-seven percent fair match, split into experience, skills, and industry. That is more explanation than I expected. But I could not see how the fifty-seven was calculated.",
      "B08_Jobright", "A ring fills to 57 percent; three bars fill to 30, 40 and 41 percent beside it; a question mark lands between the bars and the ring.",
      [{"at": 0.35, "event": "ring fills to 57"}, {"at": 0.6, "event": "three bars fill"}, {"at": 0.9, "event": "question mark"}]),
 beat("B09", "It also marked PyTorch and Scikit-learn as Priya's skills, and neither one is in her résumé. The posting itself says it is for experienced engineers, and Priya has eight months of experience, so I would label it not relevant.",
      "B09_JobrightSkills", "Two skill chips, PyTorch and Scikit-learn, get green ticks, then are checked against the résumé page and get crosses; a 'for experienced engineers' bar lands on the posting.",
      [{"at": 0.2, "event": "two chips ticked"}, {"at": 0.45, "event": "résumé check: crosses"}, {"at": 0.8, "event": "experienced-only bar"}]),
 beat("B10", "Third, I asked Claude, Sonnet five point five, to find early-career jobs at Databricks for Priya. It did better than I expected. It did not invent a list, it explained why roles did not fit, and it rejected the same AI Engineer role that Jobright scored fifty-seven percent.",
      "B10_Claude", "A Claude window shows an empty list slot labelled 'no verified list'; the AI Engineer card slides in and gets a cross; a thin line links it to the 57 ring from Jobright.",
      [{"at": 0.4, "event": "no verified list"}, {"at": 0.75, "event": "same role crossed"}, {"at": 0.9, "event": "link to the 57"}]),
 beat("B11", "But it could not confirm that any posting was still open, and it told me to use the live Greenhouse job board instead. And it read its own memory during my test, so the test was not fully clean.",
      "B11_ClaudeLimits", "An 'open?' lamp stays unlit over a posting; an arrow draws toward a Greenhouse board box; a small memory bubble pops beside the window with a grey 'not isolated' note.",
      [{"at": 0.25, "event": "lamp unlit"}, {"at": 0.55, "event": "arrow to the board"}, {"at": 0.85, "event": "memory bubble"}]),
 beat("B12", "These tools are good at finding jobs, and my agent is not meant to replace them. What I want is different: a decision I can check. My agent reads the company's job board directly, it saves the raw data, and every keep or reject comes from a written rule.",
      "B12_WhyMine", "A grid with four columns, LinkedIn, Jobright, Claude and my agent, and three rows; checks fill the my-agent column one row at a time while the other cells stay as grey dashes.",
      [{"at": 0.45, "event": "reads the board directly"}, {"at": 0.65, "event": "raw data saved"}, {"at": 0.85, "event": "written rule"}]),
 beat("B13", "One more thing. In October, I pitched a question-answering tool for the GitHub Actions docs. The final project has to be agentic, and that tool was not, so I changed my project to this agent, which I have already been building.",
      "B13_Change", "An October pitch card (a docs stack) slides in and is set aside with a cross; a loop arrow draws around the job-search agent's three boards in its place.",
      [{"at": 0.3, "event": "pitch card"}, {"at": 0.6, "event": "crossed: not agentic"}, {"at": 0.85, "event": "agent loop draws"}]),
 # ── Part 3: methods — how I am going to do it ─────────────────────────────────────────────
 beat("B14", "Here is what I have already built. In JS1, the agent watched one job board and found only the new postings. In JS2, it became one loop over four boards, with limits on time and requests, and a permission policy in the code, so it can only read from two job-board websites. JS3, a filter with written rules, is in progress.",
      "B14_Built", "Three layers stack up: JS1 and JS2 as solid kraft blocks with their test counts, JS3 as a grey outline marked 'in progress'; a fence draws around two host posts beside JS2.",
      [{"at": 0.25, "event": "JS1 block"}, {"at": 0.5, "event": "JS2 block + two-host fence"}, {"at": 0.85, "event": "JS3 outline"}]),
 beat("B15", "In its first run, the filter looked at two thousand four hundred eighteen saved postings. It rejected two thousand three hundred fifty-five, and it put sixty-three in a review queue, each with a reason. Most were rejected for asking more than two years of experience.",
      "B15_Filter", "A tall bar of 2,418 postings splits into a long 'rejected' bar and a short 'review' bar; reason strips peel off the rejected bar, the top one reading 'experience above 2 years'.",
      [{"at": 0.3, "event": "2,418 bar"}, {"at": 0.6, "event": "splits 2,355 / 63"}, {"at": 0.9, "event": "reason strips"}]),
 beat("B16", "Here is the agent's own output, recorded today. All sixty-five tests pass, offline. Then I plant three bugs on purpose, in a copy of the code, and the tests catch every one. I will rerun this after every change.",
      "B16_Tests", "A terminal window types the recorded commands and output line by line: 'Ran 65 tests', 'OK', three 'CAUGHT' lines, then 'every wrong version was caught'.",
      [{"at": 0.25, "event": "65 tests OK"}, {"at": 0.6, "event": "three bugs CAUGHT"}, {"at": 0.85, "event": "RESULT line"}]),
 beat("B17", "A separate checker recounts every board from the saved raw data, without using the agent's code. Databricks nine hundred fifteen, Anthropic six hundred seventy-five, OpenAI eight hundred twenty-five. Nothing flagged.",
      "B17_Check", "The terminal types the independent check: one row per board with its recount and 'consistent', then 'Nothing flagged.'",
      [{"at": 0.4, "event": "board rows"}, {"at": 0.9, "event": "Nothing flagged"}]),
 beat("B18", "And this is a human gate. Resetting what the agent remembers is refused, unless a person approves it. With my approval, it is allowed.",
      "B18_Gate", "The terminal types the reset command and a terracotta 'REFUSED … needs explicit approval' line; then the approved command and its 'reset' line.",
      [{"at": 0.4, "event": "REFUSED"}, {"at": 0.85, "event": "approved: reset"}]),
 beat("B19", "Here is the plan. In JS4, the agent will write a plan before each run, check what it claims, and remember across days. In JS5, I will add an approval gate tied to the exact shortlist I saw, so if one posting changes, the old approval no longer counts. Then, for the final project, I will evaluate it on data I set aside, break it on purpose, and ask someone else to run it from my README.",
      "B19_Plan", "A six-step track: steps one and two solid with checks, step three half filled, steps four to six grey outlines with their dates; a fingerprint mark joins a shortlist to an approval and breaks when one line changes.",
      [{"at": 0.2, "event": "track"}, {"at": 0.45, "event": "JS4 step"}, {"at": 0.65, "event": "fingerprint breaks on a change"}, {"at": 0.9, "event": "final step"}]),
 beat("B20", "The data comes from the public job-board APIs of Databricks, Anthropic, and OpenAI, with a fictional candidate. I need no paid API and no token credits. It is plain Python, with nothing to install, and I use Claude Code, which my university provides, to help me write code that I review.",
      "B20_Resources", "Three board boxes feed one line into a laptop; a Python file and a university Claude Code card land on the laptop; a coin labelled 'paid API' slides in and is crossed.",
      [{"at": 0.25, "event": "boards feed the laptop"}, {"at": 0.55, "event": "paid API crossed"}, {"at": 0.8, "event": "Python + Claude Code"}]),
 # ── Part 4: evaluation — how I will know it worked ────────────────────────────────────────
 beat("B21", "How will I know it did a good job? Before I tune anything, I will set aside a held-out set of postings and label them myself, including jobs I think are relevant. In JS1, all twenty-five of my labels were not relevant, so I could not count missed jobs. My reviewer pointed that out, and I will fix it.",
      "B21_HeldOut", "A deck of posting cards splits: most go to a 'development' tray, some are sealed in a 'held-out' box; a few cards get a terracotta 'relevant' dot; a grey card reads 'JS1: 25 of 25 not relevant'.",
      [{"at": 0.3, "event": "deck splits"}, {"at": 0.55, "event": "held-out sealed"}, {"at": 0.75, "event": "relevant dots"}, {"at": 0.9, "event": "JS1 note"}]),
 beat("B22", "I will measure how many relevant jobs it misses, how many wrong jobs it keeps, and whether every decision has a reason. And I will test at least five failures on purpose: a board that does not exist, a removed posting, a job outside the US, too much experience required, and a job that only matches keywords.",
      "B22_Failures", "Three measure gauges appear; then five failure cards drop one by one into a net, and each is caught with a check.",
      [{"at": 0.25, "event": "three gauges"}, {"at": 0.5, "event": "failure cards drop"}, {"at": 0.9, "event": "all five caught"}]),
 beat("B23", "It worked if no relevant job is silently rejected, every decision has a reason, the recount agrees, and nothing reaches the shortlist without my approval. It did not work if a relevant job is rejected without a reason, or if an old approval is accepted for a changed shortlist.",
      "B23_PassFail", "Two columns: under 'worked if' four checks land in turn; under 'did not work if' two crosses land.",
      [{"at": 0.2, "event": "worked-if checks"}, {"at": 0.75, "event": "did-not-work crosses"}]),
]

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, with the voice "
                 "carrying the explanation. The negative space is the style, so only underfill and clustered are waived; "
                 "edge-bleed, empty-frame and contrast still apply.")
for b in B:
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
         "voice": "am_onyx", "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show, "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


OPEN = [
 remotion("BIDEA", "the question",
    "Hi, I'm Yash Saraf. This is my final project film. My first question was whether an AI tool can find me the right jobs. The better question is whether it can show me why it picked them.",
    "BrutalistHesitantWriter",
    {"text": "Can AI find me the right jobs", "triggerWords": "find me the right jobs",
     "replacementWords": "show me why it picked them",
     "fontSize": 104, "charMs": 30, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
     "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types the naive question"}, {"at": 0.65, "event": "replaces it with: show me why it picked them"}],
    lead_silence_s=0.8,
    motion_claim="The writer types 'Can AI find me the right jobs' and corrects it to 'Can AI show me why it picked them'.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
]

OUTRO = {"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW",
         "narration_text": "A job-search agent you can check. A final project film, by Yash Saraf.",
         "estimated_duration_s": 5.0, "voice": "am_onyx", "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "manim": {"class": "BOUT_Outro"},
                  "remotion": {"props": {"title": TITLE, "handle": "Yash Saraf", "subline": ""}},
                  "visual_intent": "The three board boxes settle small above the title; the title and 'Yash Saraf' sit under them; one terracotta dot lands.",
                  "show": [{"at": 0.1, "event": "boards"}, {"at": 0.2, "event": "title + name"}, {"at": 0.7, "event": "dot"}],
                  "motion_claim": "Own outro: title and the student's name; no instructor handle or mascot."},
         "tail_silence_s": 1.0,
         "qc": {"sparse_by_design": True, "sparse_reason": "Outro card: title and name only."}}

B = OPEN + B + [OUTRO]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "yash-saraf", "channel_title": "Yash Saraf",
    "persona": "Yash Saraf, first person (synthetic Kokoro am_onyx voice reading Yash's own script)",
    "voice": "am_onyx", "voice_kokoro": "am_onyx", "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("INFO 7375 assignment rules: narrate as yourself and never use the instructor's name, persona or "
                              "credit line. So: no 'Liam, in for Bear' greeting, no Claude.ai Your Turn composer, no verdict card, "
                              "and an own outro instead of ClaudeTitleOutro, whose handle is hard-coded to @NikBearBrown. "
                              "Same choice as Yash's October pitch film."),
    "audience": "INFO 7375 instructor and TAs",
    "source_doc": "../../SCRIPT.md (2026-11-23); evidence/terminal-2026-11-23.txt; the 2026-11-23 screenshots; JS1-JS3 READMEs and run files",
    "playlist": "INFO 7375 Final Project", "chapter_number": 0,
    "tags": ["job-search agent", "agentic AI", "human gate", "evaluation", "INFO 7375"]},
    "beats": B}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(B), "beats; est", round(sum(b["estimated_duration_s"] for b in B)), "s;",
      sum(len(b["narration_text"].split()) for b in B), "words")
