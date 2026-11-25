#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for the DryRun Final Project Film (four parts, 2026-11-23).

The professor's brief asks for four parts, in this order: (1) executive summary, what and why, with no "how";
(2) introduction, what others have done and what they got, then why mine matters; (3) methods, how I will
build it, where the data comes from, step by step, and whether I have the credits, accounts, access and
compute; (4) evaluation, what I will measure and what result means it worked or didn't.

Built from my October pitch film (v5). Lines that fit a part are kept word for word: the problem, the real
Claude reply, my test, the fixed format, the locked container, the decision, the trap folders, the
measurement, "one step further", "today" and the close. The rest is new. Pitch-only lines (target role,
course skills, scope, risks, why this project) moved to APPENDIX.md.

Narrated in the first person from Pavithra Prasad's script with a synthetic Kokoro voice (af_heart, 0.95).
No house intro or outro cards: I narrate as myself.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "dryrun-project-film"
TITLE = "DryRun: Final Project Film"
VOICE = "af_heart"
SPARSE = ("Week 1-style phrase layout on a cream stage: short phrases timed to the narration, one drawing only "
          "where it explains the mechanism. Only underfill and clustered are waived; edge-bleed, empty-frame "
          "and contrast still apply.")

# (class name, part, narration, what the picture does) in film order; ids are assigned B00.. below.
SPEC = [
 # Part 1: executive summary (what and why, no how)
 ("Part1", 1, "Part one: what I'm building, and why it matters.",
  "Part title; a four-part strip with part 1 filled."),
 ("Intro", 1, "Hi, I'm Pavithra Prasad. My project is Dry Run. It will tell you what an AI's terminal command will really do to your files, before you run it, and warn you when that isn't what you asked for.",
  "My name; what DryRun is; a command passes a checkpoint before it reaches your files; a WARN chip."),
 ("Problem", 1, "AI assistants now suggest terminal commands, and coding agents run them. One wrong character can delete files, and reading a command is not the same as knowing what it will do.",
  "Four phrases build the problem; beside them the AI's workstation hands a command to your folder, and the files leave it."),
 ("RealReply", 1, "On October eleventh, I asked Claude for a command to delete log files older than seven days. It gave me this, and told me to preview it first.",
  "REAL SCREENSHOT chip; the real screenshot, cropped: my request, then Claude's command outlined and its preview advice underlined as they are spoken."),
 ("Tested", 1, "I tested the preview on a test folder on my Mac. A file seven and a half days old wasn't matched, even though it's older than seven days.",
  "MY TERMINAL chip; my own Terminal lines from 13 Oct, copied exactly; three file rows by age; the 7.5-day row is marked as missed."),
 ("WhyMatters", 1, "That matters to anyone who lets an AI suggest or run commands. A delete command has no undo step, so the check has to come before the command runs.",
  "Who it matters to; a file leaves the folder and there is no undo step; the gate closes in front of the command."),
 # Part 2: introduction (what others have done, what they got, why mine)
 ("Part2", 2, "Part two: what other people have done.",
  "Part title; the strip with part 2 filled."),
 ("Prior", 2, "Coding agents like Claude Code can ask you to approve a command before it runs, but they show you the command, not what it will change. A tool called try runs a command in a sandbox on Linux, then asks whether to keep its changes. You still judge them yourself.",
  "Two existing approaches, one prop each: an approval stamp for the agent's 'allow this command?' question; a checkpoint scanner for try."),
 ("Research", 2, "Researchers have scored AI-written Bash commands. InterCode found that letting the AI see the result of running its code helps it fix mistakes. NL2SH checked six hundred commands by hand, and its methods raised accuracy by up to thirty-two percent.",
  "Two research papers and what they got: a test bench for InterCode's run-and-fix loop; an evidence binder for NL2SH's 600 hand-checked commands and +32%."),
 ("Different", 2, "Dry Run will go one step further. It will compare the changes with your request and the AI's own prediction, and flag mismatches before you press Enter.",
  "The whole planned workflow in one picture: your folder, throwaway copy, compare, you decide."),
 # Part 3: methods (how, data, step by step, resources)
 ("Part3", 3, "Part three: how I'm going to build it.",
  "Part title; the strip with part 3 filled."),
 ("Today", 3, "Today, none of Dry Run exists yet. Everything in this film is what I will build, in four phases.",
  "No DryRun code yet; a sealed parcel; the four phases."),
 ("Contract", 3, "The AI will have to answer in a fixed format: the command, plus its own prediction of what that command will change.",
  "Example step 1: command card and predicted-changes card (constructed example)."),
 ("Simulate", 3, "Dry Run will run the command on the copy, inside a locked container with no network. Then it will compare every file before and after: what was created, changed, or deleted.",
  "Example step 2 (constructed simulation): planned locked container; before/after file list; the 8.5-day file struck out."),
 ("Gate", 3, "It will check the real changes against the AI's prediction and the task's rules. Then it will allow, warn, or block. When it can't tell, it will say so.",
  "Example step 3: predicted 2 vs simulated 1; the task rule; drawing: the gate with ALLOW / WARN / BLOCK, WARN chosen."),
 ("Human", 3, "When it warns, a person decides: they see the exact file changes, then approve or refuse.",
  "The change report is handed across a counter to a person; APPROVE and REFUSE."),
 ("Traps", 3, "To catch mistakes like that on purpose, I'll build trap folders: names with spaces, names that look like options, hidden files, files right at a time limit, and links that point outside.",
  "Trap-folder file chips appear as each is named."),
 ("Data", 3, "The data, I'll make myself: trap folders built by a script, and file tasks with known correct results. No personal files and no real users. The only outside data will be the AI's replies, saved with their dates.",
  "A conveyor makes trap folders; a task list with known answers; an inbox where each AI reply is filed with its date; no personal files, no real users."),
 ("Steps", 3, "Step by step. By November thirtieth: the copy, the run, and the file differences, with a self-test. By December sixth: the AI's fixed format, the decision, and up to three retries. By December thirteenth: the trap folders, the tasks, and the human approval. By December twentieth: the evaluation and the report.",
  "A timeline with four dated steps; the parcel is packed at December 20."),
 ("Resources", 3, "Do I have what I need? Yes. Token credits: none to buy, because Claude comes through my Northeastern Claude Code account. Accounts and access: that account, and GitHub for the code. Compute: my own laptop, an M3 with eight gigabytes of memory, which already runs Docker and a small local model in Ollama, both free. I'll keep the task set small, to stay inside my usage limits. The full plan is in my appendix.",
  "A checklist with one prop per need: token slots, a plug in its socket, a small server; then the usage-limit note and APPENDIX.md."),
 # Part 4: evaluation
 ("Part4", 4, "Part four: how I'll know it worked.",
  "Part title; the strip with part 4 filled."),
 ("Measure", 4, "Then I'll measure it: tasks with known correct results, across every trap folder, comparing Claude with a free local model, and counting how often a command did too much or too little.",
  "Evaluation plan; a queue of tasks with known answers; empty counters marked NOT MEASURED YET."),
 ("Heldout", 4, "Before I tune anything, I'll set some tasks aside as a held-out set, and plant at least five commands I know are wrong.",
  "A vault locks the held-out tasks away; five planted wrong commands go onto the test bench."),
 ("Worked", 4, "It worked if the self-test finds every planted change, every planted wrong command is flagged, and at most one correct command in ten is wrongly blocked. It didn't work if it misses a planted mistake, or blocks so many good commands that nobody would use it.",
  "Two columns: IT WORKED IF and IT DIDN'T WORK IF, each line as it is spoken; TARGETS, NOT MEASURED YET."),
 ("Limits", 4, "Even then, it won't prove commands are safe. It will only show how often this check catches the mistakes I tested.",
  "An inspection lamp over the evidence: what is not claimed, and what the evaluation can show."),
 ("Close", 4, "Dry Run. See what an AI's command will do, before it touches your files.",
  "Title and name footer."),
]

B = []
for i, (name, part, narration, image) in enumerate(SPEC):
    bid = f"B{i:02d}"
    B.append({"beat_id": bid, "act": f"part-{part}", "lane": "manim", "proof_gate": "SHOW",
              "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.6, 1),
              "voice": VOICE, "engine": "kokoro",
              "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image,
                       "manim": {"class": f"{bid}_{name}"}, "motion_claim": image},
              "qc": {"sparse_by_design": True, "sparse_reason": SPARSE}})

# The real Claude screenshot is a dark-mode capture. GATE T's whole-frame contrast reads its dark-grey interface
# shapes as dark text on dark; the toolkit's documented fix for real captured images is named text regions.
real = next(b for b in B if b["shot"]["manim"]["class"].endswith("_RealReply"))
real["qc"]["contrast_regions"] = [
    {"label": "kicker and REAL SCREENSHOT chip", "box": [0.05, 0.06, 0.85, 0.255]},
    {"label": "the real claude.ai screenshot", "box": [0.095, 0.28, 0.905, 0.735]},
    {"label": "source footer", "box": [0.17, 0.84, 0.95, 0.915]}]
real["qc"]["contrast_reason"] = ("Real dark-mode claude.ai screenshot (evidence/claude-reply-2026-10-11.png), shown unaltered. Its "
                                 "dark-grey bubble on a near-black page is interface, not text. Each region that holds text is "
                                 "checked on its own; every region must pass and all other checks still run.")

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT FILM · DRYRUN", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "pavithra-prasad", "channel_title": "Pavithra Prasad",
    "persona": "Pavithra Prasad, first person (synthetic Kokoro voice af_heart reading my script)",
    "voice": VOICE, "voice_kokoro": VOICE, "voice_speed": 0.95, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "plain", "fps": 24, "aspect_ratio": "16:9",
    "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("INFO 7375 Final Project Film: I narrate as myself, so the house bookends are left out; "
                              "the first beat is my own part title and the last my own close."),
    "audience": "INFO 7375 reviewers; hiring managers and engineers for backend and platform roles",
    "source_doc": "APPENDIX.md and PROJECT-BRIEF.md (this folder)",
    "honesty": ("A plan, not a build: no DryRun code exists yet. Real: the Claude screenshot (claude.ai, 2026-10-11), "
                "my own Terminal lines from the 13 Oct preview test, and the facts about try, InterCode and NL2SH "
                "(read 2026-11-23). Constructed and labelled on screen: the AI's prediction, the simulated deletion, "
                "the WARN decision, the change report and the person's choice. Planned and labelled: every target in "
                "part 4 (NOT MEASURED YET)."),
    "tags": ["DryRun", "AI safety", "shell commands", "sandbox", "evaluation", "INFO 7375"]},
    "beats": B}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in B)
print(len(B), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in B)), "s")
