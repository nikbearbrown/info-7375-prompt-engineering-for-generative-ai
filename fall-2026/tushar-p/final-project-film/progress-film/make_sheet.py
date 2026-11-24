#!/usr/bin/env python3
"""make_sheet.py — builds beat_sheet.json for agent-proving-ground-progress (v2).

Narration is Tushar's v2 beat plan (BEAT-PLAN.md, Nov 23, 2026) word for word.
v2 replaced v1 the same day: v1 led with implementation and ended without
explaining what's left. Beat ids are B01..B13 (the toolkit wants
[A-Z][A-Z0-9_]*, and two digits keep them in order).

Run once before audio. Re-running it wipes measured durations and sentence
times, so re-run sentence_audio.py after it.
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parent

BEATS = [
    # PART 1 — EXECUTIVE SUMMARY
    ("B01", "B01_Hello", "CONSTRUCTED",
     "Hi, I'm Tushar Patel, a software engineering student at Northeastern. This is my final project for INFO 7375: Agent Proving Ground.",
     "Title card: 'Tushar Patel', 'software engineering student · Northeastern', then 'INFO 7375 · final project' and the title 'Agent Proving Ground'."),
    ("B02", "B02_Done", "CONSTRUCTED",
     "AI coding agents are good at saying they're finished. But \"done\" is a claim, not a result. An agent can fix the bug, or quietly edit the test so it passes, or just give up, and its message can look the same each time.",
     "Three panels, each ending in the same bubble 'Done!': fixed bug (tick) / edited test (cross) / gave up (cross)."),
    ("B03", "B03_WhatItIs", "CONSTRUCTED",
     "Agent Proving Ground is a command-line tool, with its code in a public GitHub repo. You give it a small coding task. It runs an AI agent on that task inside a locked sandbox, records every step it takes, and decides pass or fail by running its own tests. Never by taking the agent's word for it.",
     "One command -> sandbox -> trace -> check -> PASS/FAIL, drawn left to right as the narration names each part."),
    ("B04", "B04_FirstMinute", "CONSTRUCTED",
     "It's for engineers deciding whether to trust a coding agent, or a change to one. In their first minute, they run one command, read one result line, and open the trace to see exactly what the agent did.",
     "A terminal mock-up: one command, one result line, then a trace opening. Labelled constructed (a mock-up, not captured output)."),
    # PART 2 — INTRODUCTION
    ("B05", "B05_Others", "CONSTRUCTED",
     "Parts of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. Each solves one piece well. But a sandbox doesn't tell you whether the work is right, and a trace doesn't stop an agent from doing what it shouldn't.",
     "Two cards (E2B, Langfuse), each with a 'solves' line and a 'doesn't' line."),
    ("B06", "B06_WhyMine", "CONSTRUCTED",
     "Mine joins the pieces in one small loop that runs on a laptop: sandbox, trace, an independent check, and a human approval before any change leaves. I built it because more and more code is written by agents, and someone has to check it rather than trust it. Along the way I learned Go and Kubernetes, which were both new to me.",
     "The four pieces joined into a loop on a laptop outline; then 'check it, don't trust it'; then 'new to me: Go · Kubernetes'."),
    # PART 3 — METHODS
    ("B07", "B07_OneRun", "CONSTRUCTED",
     "Here's one run. The harness starts a Kubernetes pod with no network, not running as root. The agent, Claude Haiku, gets three tools: read a file, write a file, run a command. Every tool call passes a permission policy written in code first. After every change, the harness runs a hidden check the agent never sees. Pass or fail comes only from that check. Then I see the diff and approve it, and my approval is bound to the exact bytes I saw.",
     "One diagram built step by step with the narration: pod -> agent + 3 tools -> policy -> hidden check -> trace -> human gate."),
    ("B08", "B08_Tasks", "CONSTRUCTED",
     "The tasks are sixteen small Python repos I made. Eleven are ordinary bugs. Five are designed so the right answer is no: a wrong test, a task that needs the network, a budget too small. I froze a development and held-out split before tuning anything. It runs on my laptop with Docker and kind, a spend-limited API key, and Claude Code, which writes the code while I review every change.",
     "16 task tiles (11 green, 5 red) splitting into 'dev' and 'held-out' with a lock; then three chips: Docker + kind, spend-limited API key, Claude Code writes · I review."),
    ("B09", "B09_BuiltSoFar", "REAL",
     "All of that is built and tested now, through milestone five. A real run on task one passed in three steps, with every step in the trace. A denied tool call was recorded and never ran. And when I tried to break the sandbox from inside a real pod, every limit held.",
     "REAL. Three quick dated terminal frames from the captures: the apg run 001 PASS line (Nov 12, evidence/B6.txt), the denied call in run 20261118T034327Z-b54f5cd6 (Nov 17 ET, evidence/B7.txt), the isolation results (Nov 17, evidence/B9.txt). A small 'M0-M5 done' strip (PLAN.md, evidence/B13.txt)."),
    # PART 4 — EVALUATION
    ("B10", "B10_Judged", "CONSTRUCTED",
     "It's judged on three things. On normal tasks, it should pass. On the five no-tasks, it must say no. A pass on one of those would mean it failed. Third, I compare changes, like two different system prompts, on held-out tasks nobody tuned on, and I wrote my predictions down before the held-out runs.",
     "Three checks: 'normal -> PASS', 'no-tasks -> must FAIL', 'compare on held-out, predictions first'."),
    ("B11", "B11_Results", "REAL",
     "First results: seventy held-out runs. Both prompts passed all twenty normal runs and said no on all fifteen no-runs. Then I read all forty passing fixes myself. On one task, seven of ten missed what the documentation asks for. So a pass means the checks passed, not that the spec was met.",
     "REAL. The apg compare totals (Nov 18, evidence/B11.txt), then FAILURES.md F2 with ['X', 'x'] (Nov 18, evidence/B12.txt). No costs."),
    # CLOSE
    ("B12", "B12_Left", "CONSTRUCTED",
     "Three things are left. First, a controlled failure: I'll make an agent edit its own test on purpose, show the check catching it, and fix it. Second, a stranger will run the project from the README on a clean machine. Third, I'll harden the check, so it confirms every test actually ran.",
     "Three numbered cards: '1 Controlled failure — edit the test -> check catches it -> recover', '2 Stranger run — README only, clean machine', '3 Harden the check — confirm every test actually ran: a forced exit can't fake a pass'; footer 'All by Dec 18'."),
    ("B13", "B13_Close", "CONSTRUCTED",
     "The biggest risk is a pass that isn't real, since code under test can fool a check. That's why I review diffs and write down every known gap. It won't be a hosted service or a model benchmark. It's one honest tool. Thanks for watching. The code is at github.com/tushar-patel28/agent-proving-ground.",
     "'Risk: a pass that isn't real -> diff review + documented gaps', then the repo URL and 'Thanks for watching.'"),
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
            viz["note"] = "real repo output: terminal frames show the source path and its date"
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
            "purpose": "Final Project Film, progress version: what Agent Proving Ground is, what is built through milestone M5, and what is left.",
            "engine": "kokoro",
            "voice_kokoro": "am_onyx",
            "aspect": "16:9",
            "clock": "narration",
            "narrator": "Tushar Patel (own narration, Kokoro am_onyx, as in the October pitch)",
            "note": ("v2 narration, copied verbatim from BEAT-PLAN.md (Tushar, Nov 23, 2026). v1 (same day) "
                     "was superseded because it led with implementation and ended without explaining "
                     "what's left. REAL beats (B09, B11) show captured repo output (evidence/<beat>.txt) "
                     "with source path and date; every other beat shows 'Constructed'."),
            "constructed": [b[0] for b in BEATS if b[2] == "CONSTRUCTED"],
            "real": [b[0] for b in BEATS if b[2] == "REAL"],
        },
        "beats": beats,
    }
    (REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n")
    total_words = sum(len(b[3].split()) for b in BEATS)
    print(f"wrote beat_sheet.json: {len(beats)} beats, {total_words} words")


if __name__ == "__main__":
    raise SystemExit(main())
