"""Writes beat_sheet.json for the A11yProof project film. Edit narration here, then re-run."""
import json, pathlib

COURSE = "INFO 7375 · Prompt Engineering & AI"   # confirmed by the student 2026-11-23
TITLE = "A11yProof: Accessibility Fixes With Proof"
CHIP = "A11yProof · Final Project"
AUTHOR = "Shubham Bagwe"   # replaces the toolkit's @NikBearBrown handle on tables and outro

def rem(bid, act, narration, pattern, props, est, **extra):
    b = {"beat_id": bid, "act": act, "narration_text": narration,
         "shot": {"type": "GRAPHIC", "source": "remotion", "motion": "illustrate",
                  "remotion": {"pattern": pattern, "props": props,
                               "rendered": {"out": f"media/{bid}.mp4", "at": ""}}},
         "estimated_duration_s": est, "audio_file": f"mp3/beat-{bid}.mp3",
         "engine": "kokoro", "voice": "am_onyx"}
    b.update(extra)
    return b

def card(kind, **p):
    return {"kind": kind, **p}

beats = [
  # ── Title card (user rule: topic, course, name, instructor) ──
  rem("B00", "TITLE",
      "A-eleven-Y Proof. A-eleven-Y is developer shorthand for accessibility. My final project film for Professor Nik Bear Brown. I'm Shubham Bagwe.",
      "LectureEvidenceTable",
      {"title": TITLE, "headers": ["Final project film", ""],
       "rows": [["Topic", "An agent that fixes web accessibility"], ["Course", COURSE],
                ["Student", "Shubham Bagwe"], ["Instructor", "Prof. Nik Bear Brown"]],
       "note": "Northeastern University · Fall 2026", "cues": [0.05, 0.12, 0.19, 0.26]}, 6),

  # ── 1. Executive summary ──
  rem("B01", "ASK",
      "Almost every website on the internet has accessibility bugs that lock disabled people out. "
      "So I asked one question. Can an A I agent fix them, prove every fix, and still leave a human in charge?",
      "ClaudeComposerAsk",
      {"greeting": "Namaste, Shubham", "topic": "FINAL PROJECT · AGENTIC AI", "segment": TITLE,
       "command": "Almost every home page fails basic accessibility checks. Can an agent fix the real code, prove every fix, and still leave a person in charge?",
       "runningText": "scoping the agent…", "folderLabel": CHIP,
       "output": ["scan → fix → re-scan → a person approves",
                  "the proof comes from a checker, not the model",
                  "nothing merges without a human"]}, 12),
  rem("B02", "BLUF",
      "A-eleven-Y Proof is an agent that fixes real website code, with proof. It finds the barriers blind and keyboard users hit, "
      "rewrites the code, re-checks it, and asks a person before anything ships.",
      "BrutalistHesitantWriter",
      {"text": "A11yProof is an AI that\nmakes any website accessible.\nA person approves every fix.",
       "contextTitle": "The project in one breath",
       "contextItems": [{"label": "Helps", "detail": "blind and keyboard users"}, {"label": "Does", "detail": "fixes the real code"}, {"label": "Decides", "detail": "a person, every time"}],
       "triggerWords": "makes any website accessible", "replacementWords": "fixes real code with proof",
       "charMs": 40, "fontSize": 88, "seed": "a11yproof-7375"}, 11, lead_silence_s=0.8),
  rem("B03", "WHY-SCALE",
      "Here's why anyone should care. Every year WebAIM tests the top one million home pages. "
      "In twenty twenty-six, ninety-five point nine percent had failures a machine can detect. About fifty-six errors per page. And it got worse, not better.",
      "ShowTellCard",
      card("masked", word="95.9%", heading="WebAIM Million 2026", sub="of top home pages fail"), 13),
  rem("B04", "WHY-STAKES",
      "That isn't only unfair, it's expensive. More than five thousand A D A lawsuits over websites and apps were filed in twenty twenty-five. "
      "And up to one in four American adults lives with a disability. These are real people being turned away.",
      "ShowTellCard",
      card("dashboard", heading="ADA digital lawsuits, 2025", word="5,114",
           sub="UsableNet year-end report"), 13),
  rem("B05", "WHAT",
      "So the project is simple to say. Find the barriers. Fix the actual code. Prove each fix worked, "
      "with a person signing off before it ships. Small sites and open-source projects get a fix, instead of a lawsuit.",
      "ShowTellCard",
      # stack order: [centre, left, right]
      card("stack", items=[{"label": "Fix", "value": "edit code", "sub": ""},
                           {"label": "Scan", "value": "find barriers", "sub": ""},
                           {"label": "Prove", "value": "re-check + OK", "sub": ""}]), 12),

  # ── 2. Introduction: what others have done ──
  rem("B06", "PRIOR-ART",
      "What have other people done? Checkers like axe, Lighthouse and WAVE find problems, but a developer still has to fix them. "
      "Overlay widgets promise one-line compliance. In twenty twenty-five the F T C ordered accessiBe to pay one million dollars over exactly that claim. "
      "Researchers have shown language models can repair violations. One system, AccessGuru, reduced violation scores by up to eighty-four percent. "
      "What none of them give a small team is the whole path: fix the source, prove it, and let a person decide.",
      "LectureEvidenceTable",
      {"title": "What already exists", "headers": ["Approach", "Example", "Gap"],
       "rows": [["Checkers", "axe · Lighthouse · WAVE", "find, don't fix"],
                ["Overlays", "accessiBe widget", "FTC: $1M order, 2025"],
                ["Research", "AccessGuru, ASSETS '25", "up to 84% — not a tool"],
                ["A11yProof", "scan → fix → re-scan", "proof + a person"]],
       "note": "Sources: FTC (Apr 2025) · arXiv 2507.19549 · WebAIM 2026",
       "cues": [0.06, 0.27, 0.55, 0.82]}, 34),
  rem("B07", "WHY-MINE",
      "That's why A-eleven-Y Proof matters. It doesn't ask you to trust the A I. It shows you the evidence, and you decide.",
      "ShowTellCard", card("masked", word="Proof", heading="evidence over trust", sub="not promises"), 7),

  # ── 3. Methods ──
  rem("B08", "LOOP",
      "Now, how I'll build it. A-eleven-Y Proof runs a loop. Observe: load the page in a real browser and run axe core. "
      "Decide: pick one violation. Act: patch the code in a sandbox. Record: write every step to a ledger. That ledger is its memory, so it never retries a fix a person already refused. "
      "And stop, when the re-scan is clean, when it hits its budget of steps and dollars, or when it refuses. Never just because the model says it's done.",
      "ShowTellCard",
      card("focus", heading="The agent loop", focus=4, cues=[0.2, 0.36, 0.5, 0.64],
           items=[{"label": "Observe", "value": "axe-core scan", "sub": ""},
                  {"label": "Decide", "value": "one violation", "sub": ""},
                  {"label": "Act", "value": "sandbox patch", "sub": ""},
                  {"label": "Record", "value": "ledger = memory", "sub": ""},
                  {"label": "Stop", "value": "clean · budget", "sub": ""}]), 26),
  rem("B09", "TOOLS",
      "Every tool has a permission policy written in code, not in the prompt. The scanner only visits allow-listed sites. "
      "The editor writes to a branch inside a sandbox, never to main. Opening a pull request needs a signed approval. "
      "And text on a web page is treated as data, never as instructions.",
      "LectureEvidenceTable",
      {"title": "Tools, and what each may do", "headers": ["Tool", "Allowed", "Enforced by"],
       "rows": [["Scanner", "read pages", "URL allow-list"],
                ["Editor", "write a branch", "sandbox, no main"],
                ["Pull request", "after approval", "signed gate token"],
                ["Page text", "data only", "never instructions"]],
       "note": "The policy lives in code, not in the prompt.",
       "cues": [0.2, 0.38, 0.6, 0.8]}, 20),
  rem("B10", "GATE",
      "The human gate. Before any pull request opens, a person sees the exact diff, before and after screenshots, and the re-scan result. "
      "They approve, refuse, or defer, and that decision is bound to a hash of what they saw. Change one line, and the approval no longer counts.",
      "ShowTellCard",
      card("search", heading="Approve fix #12?", focus=3,
           items=[{"label": "Diff a41f…e9 · what you saw", "sub": "", "value": ""},
                  {"label": "Before / after: layout same", "sub": "", "value": ""},
                  {"label": "Re-scan: 7 → 0 violations", "sub": "", "value": ""},
                  {"label": "Approve · Refuse · Defer", "sub": "", "value": ""}]), 18),
  rem("B11", "DATA",
      "Where does the data come from? Two places. Synthetic test pages where I plant known bugs, and real open-source sites whose maintainers say yes. "
      "No personal data. The tools are free and open: Playwright, axe core and a GitHub App. The model runs on Claude A P I credits, with a hard cap per run.",
      "LectureEvidenceTable",
      {"title": "Data, access and budget", "headers": ["Need", "Source", "Status"],
       "rows": [["Test pages", "synthetic, planted bugs", "I build them"],
                ["Real sites", "open-source repos", "invite only"],
                ["Tools", "Playwright · axe · GitHub", "free"],
                ["Model", "Claude API credits", "capped per run"]],
       "note": "No personal data. Real repositories only with the maintainer's permission.",
       "cues": [0.08, 0.3, 0.55, 0.75]}, 20),
  rem("B12", "PLAN",
      "The plan, step by step. First, the contract and the tests, written before any code. Then the loop and its tools. "
      "Then the gate and the GitHub App. Then the evaluation, on cases I set aside. And last, a small pilot on real repositories.",
      "ShowTellCard",
      card("focus", heading="Build plan", focus=4, cues=[0.22, 0.4, 0.58, 0.76],
           items=[{"label": "1 · Contract", "value": "tests first", "sub": ""},
                  {"label": "2 · Loop", "value": "tools + budget", "sub": ""},
                  {"label": "3 · Gate", "value": "GitHub App", "sub": ""},
                  {"label": "4 · Evaluate", "value": "held-out set", "sub": ""},
                  {"label": "5 · Pilot", "value": "real repos", "sub": ""}]), 16),

  # ── 4. Evaluation ──
  rem("B13", "MEASURE",
      "How will I know it worked? I split the test cases before tuning anything: a development set to build against, and a held-out set I don't touch until the end. "
      "On held-out pages it passes if at least eighty percent of violations are fixed, with zero new violations and zero broken layouts, checked by axe and screenshot diffs, not by the model. "
      "And on real repositories, maintainers have to accept at least seven of ten pull requests.",
      "LectureEvidenceTable",
      {"title": "How I'll know it worked", "headers": ["Measure", "Pass if", "Checked by"],
       "rows": [["Violations fixed", "≥ 80% held-out", "axe re-scan"],
                ["New violations", "zero", "axe re-scan"],
                ["Broken layouts", "zero", "screenshot diff"],
                ["PRs accepted", "≥ 7 of 10", "maintainers"]],
       "note": "Targets fixed before tuning. Held-out cases are never used to tune.",
       "cues": [0.3, 0.5, 0.62, 0.82]}, 30),
  rem("B14", "FAILURE",
      "An evaluation has to be able to say no, so I'll break it on purpose. At least five planted failure cases, like made-up alt text, a fix that breaks the layout, "
      "and a page that hides an instruction telling the agent to push straight to main. I predict the model will sometimes obey it. "
      "The permission check in code catches it, the run stops, and I review the recovery.",
      "ShowTellCard",
      card("stack", items=[{"label": "Catch", "value": "code blocks", "sub": ""},
                           {"label": "Plant", "value": "hidden order", "sub": ""},
                           {"label": "Recover", "value": "I review it", "sub": ""}]), 22),
  rem("B15", "LIMITS",
      "And the honest limits. Automated checks see only part of the problem, so a person will test the held-out pages with a screen reader. "
      "A sample of a few dozen sites can show the loop works. It can't prove it works on every website.",
      "ShowTellCard",
      card("focus", heading="What this can't show", focus=2, cues=[0.3, 0.6],
           items=[{"label": "axe coverage", "value": "only part", "sub": ""},
                  {"label": "Alt-text meaning", "value": "needs a human", "sub": ""},
                  {"label": "Sample size", "value": "a few dozen", "sub": ""}]), 14),

  # ── Close ──
  rem("B16", "VERDICT",
      "So here's the whole pitch on one page. The web is failing disabled people, and the current fixes don't hold up. "
      "A-eleven-Y Proof fixes the source code, proves each fix with tools that can say no, and keeps a person at the merge button.",
      "ClaudeVerdictArtifact",
      {"artifactTitle": "A11yProof — one page", "artifactHeading": "The pitch", "lectureLayout": True,
       "artifactLines": ["Why: 95.9% of top home pages fail automated checks; 5,114 ADA digital lawsuits in 2025.",
                         "Gap: checkers don't fix, overlays overpromise, research isn't a shipped tool.",
                         "How: scan → fix → re-scan loop, permissions in code, a human gate bound to the diff.",
                         "Proof: held-out pages, five-plus planted failures, axe and screenshots as the judges."]}, 16),
  rem("B17", "HANDOFF",
      "Your turn. Paste this into Claude: Run axe on my home page. List the three violations that would stop a blind or keyboard-only visitor, and show the exact code fix for each. "
      "Then check every fix yourself, with a keyboard and a screen reader. That last step is the whole point.",
      "ClaudeComposerAsk",
      {"greeting": "Your turn.", "topic": "YOUR TURN · ACCESSIBILITY", "segment": TITLE,
       "command": "Run axe on my home page. List the three violations that would stop a blind or keyboard-only visitor, and show the exact code fix for each.",
       "runningText": "paste this into Claude…", "output": [], "folderLabel": CHIP}, 16),
  rem("B18", "OUTRO",
      "A-eleven-Y Proof. Accessibility fixes with proof. By Shubham Bagwe.",
      "ClaudeTitleOutro", {"title": TITLE, "slug": "fixproof-pitch"}, 5),
]

for b in beats:
    r = b["shot"]["remotion"]
    if r["pattern"] in ("LectureEvidenceTable", "ClaudeTitleOutro"):
        r["props"]["handle"] = AUTHOR

sheet = {"metadata": {
    "title": TITLE, "slug": "fixproof-pitch", "topic": "FINAL PROJECT · AGENTIC AI",
    "register": "Plain", "brand": "claude-liam", "engine": "kokoro", "voice_kokoro": "am_onyx",
    "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5",
    "greeting": "Namaste, Shubham", "course": COURSE, "student": AUTHOR,
    "instructor": "Prof. Nik Bear Brown",
    "note": "Project pitch film: exec summary (B01-B05), introduction/prior art (B06-B07), methods (B08-B12), evaluation (B13-B15). Facts: FACTS.md."},
  "beats": beats}
here = pathlib.Path(__file__).parent
(here / "beat_sheet.json").write_text(json.dumps(sheet, indent=1, ensure_ascii=False))
print(len(beats), "beats;", sum(len(b["narration_text"].split()) for b in beats), "words")
