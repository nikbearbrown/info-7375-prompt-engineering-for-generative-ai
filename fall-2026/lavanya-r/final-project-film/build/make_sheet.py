#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the README Checker pitch film (Lavanya R, INFO 7375).

Cut 4 (2026-11-23): re-ordered into the professor's four parts, in order:
  1. Executive summary  (BHELLO–B01T): what I'm building and why it matters, inside the first minute,
                                        with no "how" (the terms card is gone; the container comes later).
  2. Introduction       (B02T–B06C):   what already exists (by hand, CI, Runme, Doc Detective, two
                                        published AI setup agents), then why mine is still worth building.
  3. Methods            (B03–B11):     the plan, the data, step-by-step build order, the resources I have.
  4. Evaluation         (B08–B08A):   what I'll measure and the result that counts as working or not.
Cut from cut 3 (detail now lives in PROJECT-BRIEF.md / APPENDIX.md): BDEFS, B02, B07, B09, B10, B12, B13.

Format: Brutalist show-tell (one drawn picture per beat, the voice explains), a part header on every
beat, readable README steps, my real terminal output, and one key sentence per beat.

Changes from the show-tell defaults, made because the assignment says "narrate as yourself;
do not use the instructor's name, persona, or credit line":
  - first-person narration as me; no "Liam, in for Bear" greeting
  - the locked ClaudeTitleOutro card is NOT used (it hard-codes @NikBearBrown); B14 is my own outro
Pronunciation: my first name is spelled "Luh-vun-ya" in narration_text only, so Kokoro says it the
way I say it (picked from six samples, 2026-10-13). On screen it is spelled "Lavanya".
Honesty rule: past tense only for the two real README runs (2026-10-13), the webapp repo, and the
published prior work (B06A/B06B, sources in SOURCES.md). Everything about the tool is "will".
B05's report is labelled "constructed mock-up" on screen. B08A's thresholds are targets, not results.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "readme-checker-film"
TITLE = "README Checker: Does the README Actually Work?"
VOICE = "af_bella"
NAME = "Lavanya R"
SAY = "Luh-vun-ya"   # how Kokoro should say my first name

SPARSE_REASON = ("show-tell style: one drawn picture per beat on a cream stage; the voice carries the "
                 "explanation. Only underfill and clustered are waived.")


def est(text):
    return round(len(text.split()) / 2.6, 1)


def beat(bid, cls, narration, image, show, sparse=True):
    b = {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": est(narration),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                  "manim": {"class": cls}, "motion_claim": image}}
    if sparse:
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}
    return b


HELLO = beat("BHELLO", "BHELLO_Intro",
             f"Hi, I'm {SAY}. My final project is the README Checker. Nothing is built yet.",
             "Title picture: the README Checker name, 'final project pitch · Lavanya', and 'nothing is built yet', "
             "beside a README page and an open box.",
             [{"at": 0.1, "event": "title"}, {"at": 0.7, "event": "'nothing is built yet'"}])

IDEA = {"beat_id": "BIDEA", "act": "the question", "lane": "bookend", "proof_gate": "SHOW",
        "narration_text": "The question isn't how to fix a broken README. It's how to find out if it works.",
        "voice": VOICE, "engine": "kokoro",
        "shot": {"type": "REMOTION", "source": "own",
                 "show": [{"at": 0.0, "event": "types 'How do I fix a broken README'"},
                          {"at": 0.5, "event": "corrects 'fix' to 'find' as the voice says it"}],
                 "remotion": {"pattern": "BrutalistHesitantWriter",
                              "props": {"text": "How do I fix a broken README", "triggerWords": "fix",
                                        "replacementWords": "find", "fontSize": 110, "charMs": 60,
                                        "hesitateBetween": 4, "hesitateWithin": 1, "mistakeRate": 0,
                                        "jitter": 10, "seed": SLUG, "banner": ""}}},
        "motion_claim": "The writer types the naive question (fix) and corrects it to the real one (find).",
        "qc": {"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}}
IDEA["estimated_duration_s"] = est(IDEA["narration_text"])

# ── Part 1 · Executive summary: what and why (no "how") ──
PART1 = [
    beat("B00", "B00_Problem",
         "A new engineer opens a README and follows the setup steps. A step fails, and they can't tell if the "
         "problem is them, or the instructions.",
         "A README page (grey lines); a cursor walks down and an X lands. Key line: 'Is it me, or the instructions?'",
         [{"at": 0.1, "event": "README page"}, {"at": 0.4, "event": "cursor walks"}, {"at": 0.7, "event": "X lands"}]),
    beat("B00A", "B00A_WhatItIs",
         "The README Checker will follow a project's setup instructions exactly as written, and tell you which "
         "step is broken, and why. It only reports. It won't fix anything.",
         "A README page on the left, an arrow, and a report on the right whose rows get a check, a warning and an X. "
         "Key line: 'Which step is broken, and why.' Small 'reports only · won't fix'.",
         [{"at": 0.15, "event": "README → report"}, {"at": 0.6, "event": "marks, 'won't fix'"}]),
    beat("B01", "B01_MyRun",
         "On October thirteenth, I followed my own web app's README in a fresh copy. The clone link was a "
         "placeholder, a config file was missing, and the health check returned five oh three.",
         "My webapp README as a grey-line page with seven rows; a mark lands beside each: placeholder warning, "
         "pass, fail, skipped, placeholder warning, fail, fail.",
         [{"at": 0.15, "event": "seven steps"}, {"at": 0.6, "event": "marks land"}]),
    beat("B01T", "B01T_Terminal",
         "I wrote that README, and I couldn't see what was wrong with it. Every engineer who joins a project pays "
         "for that, in lost time.",
         "A terminal panel with my real output from 2026-10-13: the migrate error and the 503 response. "
         "Key line: 'The writer can't see it. The next engineer pays for it.'",
         [{"at": 0.2, "event": "migrate error"}, {"at": 0.55, "event": "503"}]),
]

# ── Part 2 · Introduction: what others have done, then why mine ──
PART2 = [
    beat("B02T", "B02T_Terminal",
         "What exists already? Doing it by hand. Heroku's starter app worked for me, but its README asked for "
         "a tool I didn't need, and skipped the npm version it wanted. By hand, you only find what you happen "
         "to hit.",
         "A terminal panel with my real Heroku output: the npm engine warning and 200 OK.",
         [{"at": 0.25, "event": "warning"}, {"at": 0.6, "event": "200 OK"}]),
    beat("B06", "B06_NotCI",
         "Second, CI. My project's CI installs Node and the database with its own steps, separate from the README. "
         "It tests the code, not the instructions a person reads.",
         "My CI panel on one side, the README page on the other; the CI checks pass, the README is never touched.",
         [{"at": 0.2, "event": "CI steps"}, {"at": 0.6, "event": "CI passes, README untouched"}]),
    beat("B06A", "B06A_DocTools",
         "Doc tools. Runme runs a README's code blocks, but you judge the output. Doc Detective checks docs "
         "against the product, using tests you write first.",
         "Two labelled cards: Runme (runs a README's code blocks · you judge the output) and Doc Detective "
         "(tests docs against the product · you write the tests first).",
         [{"at": 0.15, "event": "Runme"}, {"at": 0.55, "event": "Doc Detective"}]),
    beat("B06B", "B06B_Agents",
         "And research. ExecutionAgent, published in 2025, set up and tested thirty three of fifty open source "
         "projects. Installamatic installed twenty one of forty Python projects. Both aim to get a project "
         "running, not to say which README line is wrong.",
         "Two result cards with their published numbers: ExecutionAgent 33 / 50, Installamatic 21 / 40, each "
         "labelled with its venue. Key line: 'Built to get it running, not to judge the README.'",
         [{"at": 0.15, "event": "ExecutionAgent 33/50"}, {"at": 0.45, "event": "Installamatic 21/40"},
          {"at": 0.75, "event": "key line"}]),
    beat("B06C", "B06C_Gap",
         "So CI skips the README, doc tools leave the judging to you, and AI agents work around it. The README "
         "Checker will run it as written, and say which line broke. That's why it's worth building.",
         "A comparison table: by hand, CI, Runme, Doc Detective, AI setup agents, README Checker (planned) × "
         "'runs the README itself' and 'says which line broke, on any README'. Rows land as named.",
         [{"at": 0.1, "event": "table"}, {"at": 0.7, "event": "README Checker row"}]),
]

# ── Part 3 · Methods: the plan, the data, the steps, the resources ──
PART3 = [
    beat("B03", "B03_WhatItIs",
         "Now the method. A command line tool, in a public GitHub repo, that will run every README step inside "
         "a throwaway container, deleted after each run.",
         "Open box (the container); the README drops in. Key line: 'Runs every README step in a throwaway container.'",
         [{"at": 0.2, "event": "box"}, {"at": 0.6, "event": "README drops in"}]),
    beat("B04", "B04_Loop",
         "It will run one step, read the real output, and decide: continue, stop, or mark it unclear. The AI "
         "picks the move, but every result comes from a command that ran.",
         "Run → read → decide loop; a dot travels the loop.",
         [{"at": 0.15, "event": "loop"}, {"at": 0.6, "event": "dot travels"}]),
    beat("B05", "B05_Report",
         "Then it will write a report: pass, warning, or fail for each step, with the README line and the real "
         "error. This one is a mock up. It isn't built yet.",
         "A readable report mock-up for my webapp README with README line numbers, stamped 'constructed mock-up'.",
         [{"at": 0.2, "event": "report"}, {"at": 0.6, "event": "rows"}]),
    beat("B05A", "B05A_Samples",
         "The data: about ten small sample projects I'll make myself. Half get one planted problem, like a "
         "missing file. Half work. So I know the right answer before the tool runs.",
         "Ten sample boxes; five get a terracotta dot (a planted problem); an answer-key page appears beside them.",
         [{"at": 0.15, "event": "ten boxes"}, {"at": 0.4, "event": "five dots"}, {"at": 0.75, "event": "answer key"}]),
    beat("B05B", "B05B_Plan",
         "Step by step. One: run one sample README in a container, and write report dot md with real exit "
         "codes. Two: add the agent loop, and a prompt contract my code checks. Three: build the samples and "
         "the answer key. Four: run the evaluation.",
         "Four numbered rows landing in order, the first marked 'first milestone'.",
         [{"at": 0.05, "event": "1"}, {"at": 0.4, "event": "2"}, {"at": 0.62, "event": "3"}, {"at": 0.78, "event": "4"}]),
    beat("B05C", "B05C_Resources",
         "Do I have what I need? Docker is on my laptop, the code goes on my GitHub, and the model calls go "
         "through Claude Code on my university login, which I've already used for a course agent. It's about "
         "one call per step, so my laptop is enough.",
         "A four-row checklist: Docker, GitHub account, Claude access, compute; a check lands on each as it is named.",
         [{"at": 0.15, "event": "Docker"}, {"at": 0.3, "event": "GitHub"}, {"at": 0.45, "event": "Claude"},
          {"at": 0.8, "event": "compute"}]),
    beat("B11", "B11_Risk",
         "The risk: a README can contain any command. So the container gets no secrets, and no access to my "
         "files. Vague steps get marked unclear, not guessed.",
         "A locked box swapped for a fresh one; a vague step marked 'unclear'.",
         [{"at": 0.2, "event": "lock"}, {"at": 0.6, "event": "fresh box, unclear"}]),
]

# ── Part 4 · Evaluation: what I'll measure, and what counts as working ──
PART4 = [
    beat("B08", "B08_Eval",
         "How will I know it worked? I'll run it on all ten samples, and compare each report to my answer key. "
         "Two numbers: planted problems caught at the right line, and false alarms on the projects that work.",
         "Answer key and the tool's report side by side with a comparison mark; two empty score slots: "
         "caught ? / 5 and false alarms ? / 5. Small 'these numbers don't exist yet'.",
         [{"at": 0.2, "event": "key vs report"}, {"at": 0.6, "event": "score slots"}]),
    beat("B08A", "B08A_Threshold",
         "It worked if it catches at least four of the five planted problems at the right line, with at most "
         "one false alarm, and every verdict comes from a command that ran. Three or fewer, or two false "
         "alarms, and it didn't. Either way, I'll write up where Claude was wrong.",
         "Two columns: 'It worked if' (≥ 4 / 5 caught at the right line · ≤ 1 false alarm · every verdict backed by a "
         "real exit code) and 'It didn't if' (≤ 3 / 5 · ≥ 2 false alarms).",
         [{"at": 0.1, "event": "worked if"}, {"at": 0.6, "event": "didn't if"}]),
]

OUTRO = beat("B14", "B14_Outro",
             "README Checker. Does the README actually work?",
             "Own outro: box and title. Replaces the locked @NikBearBrown card.",
             [{"at": 0.2, "event": "title"}, {"at": 0.6, "event": "name"}])
OUTRO["tail_silence_s"] = 1.0

BEATS = [HELLO, IDEA] + PART1 + PART2 + PART3 + PART4 + [OUTRO]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "README CHECKER · PITCH", "skill": "show-tell",
    "style_preset": "show-tell", "channel": "lavanya-r", "channel_title": NAME,
    "persona": NAME, "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9",
    "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Opens on my own intro, then the hesitant writer; no terms card (cut 4 keeps the how out of the "
                              "executive summary); no verdict card or Your Turn (cut for the 2-4 minute limit). The locked "
                              "ClaudeTitleOutro is replaced by an own drawn outro (B14) because it hard-codes "
                              "@NikBearBrown, and the assignment forbids the instructor's credit line."),
    "audience": "hiring managers and engineers reviewing a Software Engineer candidate",
    "source_doc": ("PROJECT-BRIEF.md; APPENDIX.md; two manual README runs on 2026-10-13 "
                   "(github.com/LavanyaRajesh24/webapp, github.com/heroku/node-js-getting-started); "
                   "prior work in SOURCES.md (ExecutionAgent, Installamatic, Runme, Doc Detective)"),
    "playlist": "INFO 7375 Final Project Pitch", "chapter_number": 0,
    "tags": ["README", "developer tools", "agent loop", "evaluation", "Docker", "INFO 7375"]},
    "beats": BEATS}

if __name__ == "__main__":
    (HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
    words = sum(len(b["narration_text"].split()) for b in BEATS)
    print(len(BEATS), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")
