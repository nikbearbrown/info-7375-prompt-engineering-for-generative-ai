#!/usr/bin/env python3
"""make_sheet.py — builds beat_sheet.json for agent-proving-ground-progress.

Narration is BEAT-PLAN.md (approved by Tushar, Nov 23, 2026) word for word,
except B04, which was changed to the October PROJECT-BRIEF.md wording (step 4
[VERIFY]; Tushar chose "brief only" on Nov 23, 2026). Beat ids are the plan's
B1..B13 written B01..B13 (the toolkit wants [A-Z][A-Z0-9_]*, and two digits
keep them in order).

Run once before audio. Re-running it wipes measured durations and sentence
times, so re-run sentence_audio.py after it.
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parent

B04_APPROVED = ("Pieces of this already exist. E2B and Runtime give agents sandboxes. Langfuse and "
                "Raindrop trace and evaluate model calls. oh-my-pi is a harness for coding agents. "
                "And a Drupal project, AI Proving Ground, grades what an agent actually saved instead "
                "of what it reports, but only for Drupal sites.")

BEATS = [
    ("B01", "B01_Hello", "CONSTRUCTED",
     "I'm Tushar Patel, a software engineering student at Northeastern. This is my final project, Agent Proving Ground.",
     "Title card: 'Tushar Patel', then the title 'Agent Proving Ground' and the subtitle 'progress film, through M5'."),
    ("B02", "B02_Done", "CONSTRUCTED",
     "When an AI coding agent says \"done,\" that isn't the same as the job being done. The agent might have fixed the bug, or quietly changed the test, or just stopped.",
     "A speech bubble 'Done!' beside a red failing test; then three small outcomes: fixed the bug, changed the test, just stopped."),
    ("B03", "B03_Loop", "CONSTRUCTED",
     "Agent Proving Ground runs a coding agent on small tasks inside a locked sandbox. It records every step the agent takes, and it decides pass or fail with its own tests, never with the agent's word. Anyone who relies on a coding agent needs exactly this: a cheap, local way to see what the agent did, and whether it really worked.",
     "sandbox -> trace -> check -> PASS/FAIL, drawn left to right as the narration names each part."),
    ("B04", "B04_Others", "CONSTRUCTED",
     "Pieces of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites.",
     "One card per tool: E2B (sandboxes), Langfuse (traces and scores), AI Proving Ground for Drupal (grades what was saved; Drupal only)."),
    ("B05", "B05_WhyMine", "CONSTRUCTED",
     "What I wanted was all of it in one small loop I can run on a laptop: sandbox, trace, an independent check, and a human who approves before anything leaves, with every failure written down.",
     "The four pieces (sandbox, trace, check, human approval) joined in a loop on a laptop outline; a failure log under it."),
    ("B06", "B06_RealRun", "REAL",
     "I built it in Go. The agent is Claude Haiku, with three tools: read a file, write a file, run a command. It works inside a Kubernetes pod with no network. After every change, the harness runs a hidden check the agent never sees. Here's a real run on task one: it passed in three steps, and every step is in the trace.",
     "REAL. Terminal frame: the 'apg run 001' result line (PLAN.md:120, Nov 12) and apg show of 20261112T053055Z-92239eb0 with its 3 steps. Evidence: evidence/B6.txt."),
    ("B07", "B07_PolicyGate", "REAL",
     "Every tool call goes through a policy written in code. A denied call never runs; it's just recorded. And before any change leaves the sandbox, I see the diff and approve it myself. My approval is bound to the exact bytes I saw, so if the diff changes, my approval is void.",
     "REAL. Terminal frame 1: apg show step 4 of 20261118T034327Z-b54f5cd6 (contract B, held-out, 008), DENIED (rule: path). Frame 2: gate section of 20261113T224740Z-a9a2c258, approved, diff_sha256 = recheck_sha256. Evidence: evidence/B7.txt."),
    ("B08", "B08_Data", "REAL",
     "The data is sixteen small Python tasks I made for this project. Eleven are normal bugs. Five are built to make the system say no: a wrong test, a task that needs the network, a budget too small. I split them into development and held-out sets, and froze that split before tuning anything.",
     "REAL. Terminal frame: tasks/README.md task ids (11 normal, 5 failure), then git show --stat 26b5305. Evidence: evidence/B8.txt."),
    ("B09", "B09_Isolation", "REAL",
     "I tried to break the sandbox from inside a real pod: no network, not root, capped CPU, memory, processes and disk. Every limit held. It runs on my laptop with Docker and kind, a spend-limited API key, and Claude Code, which wrote the code while I reviewed every change.",
     "REAL. Terminal frame: highlighted lines of evidence/isolation/20261117-isolation-d29.txt (network, uid, CPU, memory, pids, disk; all PASS). Evidence: evidence/B9.txt."),
    ("B10", "B10_Predictions", "REAL",
     "Pass or fail comes only from the hidden check. I compared two system prompts: the original, and a longer one I wrote. Before running either on the held-out tasks, I wrote down and committed my predictions.",
     "REAL. Terminal frame: docs/t5-predictions.md header and git log -1 6d7bafe; prompt sizes A 623 bytes, B 2,695 bytes. Evidence: evidence/B10.txt."),
    ("B11", "B11_Results", "REAL",
     "Seventy held-out runs. Both prompts passed all twenty normal runs, and both said no on all fifteen failure runs. That's a ceiling: pass rate can't tell them apart. My longer prompt cost about forty-one percent more and did no better.",
     "REAL. Terminal frame: totals from evidence/compare/20261118-t51-a-vs-b.txt (runs 35/35, 20/20, 15/15, total cost). Costs labelled 'estimated from list prices'. Evidence: evidence/B11.txt."),
    ("B12", "B12_PassMeans", "REAL",
     "Then I read all forty passing fixes myself. No cheating, no test edits. But on one task, seven of ten fixes missed behavior the documentation asks for and the tests don't check. So a pass means the frozen checks passed, not that the spec was met.",
     "REAL. Terminal frame: FAILURES.md F2 lines (7 of 10 on 011) and the executed check add_tag('x', ['X']) -> ['X', 'x']. Evidence: evidence/B12.txt."),
    ("B13", "B13_Next", "CONSTRUCTED",
     "Next, I'll trigger a failure on purpose, an agent editing its own test, and show the check catching it. Then a stranger will run the project from the README alone. If it ever passes something it shouldn't, or a sandbox limit breaks, it didn't work. The code is public at github.com/tushar-patel28/agent-proving-ground.",
     "Checklist: M0-M5 ticked; 'controlled failure', 'stranger run', 'submit Dec 18' open. Repo URL on screen."),
]


def main():
    beats = []
    for bid, cls, kind, text, mech in BEATS:
        words = len(text.split())
        viz = {"mechanic": mech}
        if kind == "CONSTRUCTED":
            viz["label"] = "Constructed"
            viz["note"] = "constructed diagram: must show 'Constructed' on screen for the whole beat"
        else:
            viz["label"] = "Real output"
            viz["note"] = "real repo output: terminal frame shows the source path and its date"
        beats.append({
            "beat_id": bid,
            "narration_text": text,
            "engine": "kokoro",
            "voice": "am_onyx",
            "estimated_duration_s": round(words / 145 * 60, 1),
            "new_visual_element": kind.title(),
            "shot": {"type": "GRAPHIC", "source": "own"},
            "graphic": {"engine": "manim", "manim": cls, "production_viz": viz},
        })
    sheet = {
        "metadata": {
            "title": "Agent Proving Ground — progress film (through M5)",
            "slug": "agent-proving-ground-progress",
            "topic": "PROGRESS",
            "purpose": "Final Project Film, progress version: what Agent Proving Ground is and what ran through milestone M5.",
            "engine": "kokoro",
            "voice_kokoro": "am_onyx",
            "aspect": "16:9",
            "clock": "narration",
            "narrator": "Tushar Patel (own narration, Kokoro am_onyx, as in the October pitch)",
            "note": ("Narration copied verbatim from BEAT-PLAN.md (approved by Tushar, Nov 23, 2026), "
                     "except B04: changed to the October PROJECT-BRIEF.md wording (step 4 [VERIFY], "
                     "Tushar chose 'brief only', Nov 23, 2026). REAL beats show captured repo output "
                     "(evidence/<beat>.txt) with source path and date; CONSTRUCTED beats show 'Constructed'."),
            "b04_approved_text": B04_APPROVED,
            "constructed": [b[0] for b in BEATS if b[2] == "CONSTRUCTED"],
            "real": [b[0] for b in BEATS if b[2] == "REAL"],
        },
        "beats": beats,
    }
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n")
    total_words = sum(len(b[3].split()) for b in BEATS)
    print(f"wrote beat_sheet.json: {len(beats)} beats, {total_words} words")


if __name__ == "__main__":
    main()
