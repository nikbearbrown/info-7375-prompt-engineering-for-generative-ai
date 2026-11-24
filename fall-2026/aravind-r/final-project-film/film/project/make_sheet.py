#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the Readback PROJECT film (four-part brief).

This is a new film, not a re-cut of the pitch film. It follows the four-part brief, in order:
  1. executive summary;
  2. introduction (what others have done);
  3. methods;
  4. evaluation.
It reuses the toolkit (brutalist.art @ cd4bf20 plus my outro patch), the same Kokoro voice, the v2 visual system and the
real evidence in ../../case-study/. Every narration sentence and on-screen number maps to a row in CLAIMS.md.

Pacing is measured, not guessed: the pitch film's Kokoro clips ran 554 words over 169.0 s of speech, which is
3.278 words/s (197 wpm). Runtime cap: 4:00. Planned: about 3:55 (revision of 2026-11-23: application-agnostic summary,
the AMI test bench introduced as a test bench, a closing beat, tighter gaps).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "aravind-r-readback-project-film"
TITLE = "Readback"
SAY_TITLE = "Reed-back"         # Kokoro input: phonetic spelling, so it is said "reed-back" (on screen: Readback)
HANDLE = "Aravind Ravi · INFO 7375"      # end-card handle; compile.py also shows it over the first beat
CREDIT = "read by a synthetic voice"     # end card only (outro patch `credit`), so it is not on the opening frames
TAGLINE = "Check that AI judges read your acceptance criteria\nthe way you meant them."   # end card value line (outro patch)
VOICE = "am_onyx"                 # same Kokoro voice and settings as the pitch film
WPS = 554 / 169.0                 # measured from ../../mp3/ (pitch-film clips)
HOLDS = {"B01": 0.35, "B02": 0.3, "B03": 0.5, "B04": 0.35, "B05": 0.3, "B06": 0.4, "B07": 0.3, "B08": 0.5,
         "B09": 0.35, "B10": 0.4, "B11": 0.3, "B12": 0.45, "B13": 0.3, "B14": 0.35, "B15": 0.5,
         "B16": 0.4, "B17": 0.3, "B18": 0.35, "B19": 0.4, "B20": 0.5}
# silence between beats = this hold + the 0.05 s left at each trimmed clip edge: 0.35–0.55 s, varied, longest before a
# chapter card; well under the 1.2 s dead-air gate

PARTS = {"summary": "1 · Executive summary", "introduction": "2 · Introduction",
         "methods": "3 · Methods", "evaluation": "4 · Evaluation"}

# (beat_id, part, class, unused, narration); claim ids are assigned from the sentence split below
BEATS = [
    # ── 1 · Executive summary: application-agnostic, consequence first; no meeting recap anywhere ──────
    ("B01", "summary", "B01_Hook", [],
     "Every AI feature ships against acceptance criteria a PM wrote. Those criteria become a rubric: the checklist "
     "an AI judge grades the output against. When a judge reads a criterion differently than the PM meant it, the "
     "eval passes, and the wrong behaviour ships."),
    ("B02", "summary", "B02_Stakes", [],
     "Then teams act on wrong output, users lose trust, and the feature quietly dies. And because evals are becoming "
     "the launch gate for AI features, a misread criterion ships wrong behaviour at scale, with a passing score attached."),
    ("B03", "summary", "B03_Readback", [],
     "Reed-back will find the criterion the judges read differently, and ask the PM what they meant, before anyone "
     "trusts the score. It's module one of a bigger vision: a copilot for what PMs write for AI. Reed-back is "
     "planned; nothing has run yet."),
    # ── 2 · Introduction: what others have done, then why it matters on any feature ───────────────────
    ("B04", "introduction", "B04_Maxim", [],
     "What have others done? Some tools already work on making AI judges more reliable. "
     "Maxim AI runs several models as judges, compares their verdicts, and measures how often they agree "
     "with human labels."),
    ("B05", "introduction", "B05_Orq", [],
     "Ork dot AI compares an evaluator with human labels, checks whether it answers the same way twice, "
     "and then proposes a rewritten evaluator prompt."),
    ("B06", "introduction", "B06_SpecKit", [],
     "For specs rather than rubrics, GitHub's Spec Kit has an optional clarify step that resolves ambiguity "
     "before planning starts."),
    ("B07", "introduction", "B07_Gap", [],
     "So the tools I checked give you an agreement score, a rewritten prompt, or a clearer spec. "
     "What I couldn't find in their documentation, read on October fourteenth, is any of them naming "
     "the rubric clause behind a judge disagreement."),
    ("B08", "introduction", "B08_WhyMine", [],
     "That gap is why Reed-back matters on any AI feature. A score tells you something is wrong. The criterion "
     "tells you what to fix. And a question, instead of a rewrite, keeps the fix a product decision."),
    # ── 3 · Methods: the test bench first, then the plan in the order it runs ─────────────────────────
    ("B09", "methods", "B09_TestBench", [],
     "To test Reed-back, I need one real AI feature with public data and human ground truth. I chose a "
     "meeting-recap feature on the AMI Meeting Corpus, because AMI ships human-written decision lists. It's my "
     "test case, not the product. I use ten of its meetings, which hold eighty-six decisions."),
    ("B10", "methods", "B10_Feature", [],
     "The feature under test is a meeting recap: my own prompt, running on Claude. I ran it on every meeting "
     "on October fourteenth, so ten real recaps already exist."),
    ("B11", "methods", "B11_Rubric", [],
     "Next, a constructed rubric with five clauses, like 'every decision appears' and 'don't report open "
     "questions as decisions'. The decisions clause is anchored to AMI's list, so there's a right answer to check "
     "against."),
    ("B12", "methods", "B12_Labels", [],
     "Before any judge runs, I'll mark which of AMI's decisions each recap covers. Those are the human labels, "
     "and I'll commit them first, so the history proves the order."),
    ("B13", "methods", "B13_Judges", [],
     "Then three judges score every recap: Claude, a second provider's model, and a local open-weight model. "
     "I'll measure how often they agree with each other, and with my human labels on the decisions clause."),
    ("B14", "methods", "B14_Trace", [],
     "Where the judges split, Reed-back will trace the split to its clause and ask the PM. In one real recap, "
     "two quick yeses became a decision. Does a quick yes count? The PM answers, and revises the clause."),
    ("B15", "methods", "B15_Have", [],
     "Do I have what I need? The data and the ten recaps are in my repository, and Claude runs here on my "
     "subscription. My API credits and a second provider account aren't wired in yet. Still to come: the local "
     "model, and my human labels."),
    # ── 4 · Evaluation: three checks on the test case, each with a pass and a fail; then the close ─────
    ("B16", "evaluation", "B16_Planted", [],
     "Three checks on the test case, each with a pass and a fail. First, a planted ambiguity: I'll make one "
     "clause deliberately vague, so I know the right answer in advance. It passes if Reed-back blames the clause "
     "I planted. It fails if it blames another clause, or noise."),
    ("B17", "evaluation", "B17_Kappa", [],
     "Second, agreement on the decisions clause: each judge against my human labels on all eighty-six "
     "decisions, measured with Cohen's kappa. It passes at point six or higher, a bar I'll fix before any run. "
     "Below that, it fails."),
    ("B18", "evaluation", "B18_BeforeAfter", [],
     "Third, before and after. The PM revises the flagged clause, and I re-measure judge agreement on meetings "
     "held out from the revision. If agreement doesn't rise, Reed-back didn't help, and I'll say so."),
    ("B19", "evaluation", "B19_Scorecard", [],
     "None of these checks has run yet, so every result is blank, and a failed check goes on the scorecard too."),
    ("B20", "evaluation", "B20_Close", [],
     "If these checks pass, a PM could trust a passing score to mean what they meant. That's the goal for any AI "
     "feature. And Reed-back is module one of a copilot for what PMs write for AI."),
]


def est(text):
    return round(len(text.split()) / WPS, 2)


import re
_SENT = re.compile(r'(?<=[.?!])\s+(?=[A-Z"\'])')
_n = 0


def claim_ids(text):
    """One CLAIMS.md row per narration sentence, numbered N01… in film order (the ledger uses the same split)."""
    global _n
    ids = []
    for _ in _SENT.split(text.strip()):
        _n += 1
        ids.append(f"N{_n:02d}")
    return ids


beats = []
for bid, part, cls, _claims, narration in BEATS:
    claims = claim_ids(narration)
    beats.append({
        "beat_id": bid, "act": part, "part_label": PARTS[part], "lane": "manim", "proof_gate": "SHOW",
        "narration_text": narration, "estimated_duration_s": est(narration), "hold_after_s": HOLDS[bid],
        "voice": VOICE, "engine": "kokoro", "audio_file": f"mp3/beat-{bid}.mp3",
        "shot": {"type": "GRAPHIC", "source": "own", "manim": {"class": cls},
                 "visual_intent": f"see SHOTLIST.md ({bid}) and DESIGN.md"},
        "claim_ids": claims,
        "qc": {"sparse_by_design": False},
    })
beats.append({
    "beat_id": "BOUT", "act": "outro", "part_label": "outro", "lane": "bookend", "proof_gate": "SHOW",
    "narration_text": f"{SAY_TITLE}. A project film by Aravind Ravi, read by a synthetic voice.", "estimated_duration_s": 5.0,
    "voice": VOICE, "engine": "kokoro", "audio_file": "mp3/beat-BOUT.mp3", "kind": "outro_voice", "tail_silence_s": 1.0, "hold_after_s": 1.0,
    "shot": {"type": "REMOTION", "source": "own", "show": [{"at": 0.0, "event": "title restates; my handle"}],
             "remotion": {"pattern": "ClaudeTitleOutro",
                          "props": {"title": TITLE, "slug": SLUG, "handle": HANDLE, "subline": "", "tagline": TAGLINE, "credit": CREDIT, "hideMascot": True,
                                    # pinned light card on the film's stage colour, so every cut has the same ground
                                    "polarity": "light", "background": "#F2F0E9"}}},
    "claim_ids": claim_ids(f"{SAY_TITLE}. A project film by Aravind Ravi, read by a synthetic voice."),
})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "aravind-r", "channel_title": HANDLE, "persona": "Aravind Ravi (synthetic voice)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "clock": "narration", "palette": "claude",
    "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Four-part project film: it opens on the problem with no title card (brief), so no composer "
                              "cold open, no verdict card, no Claude.ai composer Your Turn. The outro stays (never exempt)."),
    "pronunciation": "Readback is spelled Reed-back in narration_text (the Kokoro input) so it is said reed-back; on screen and in the paperwork it is Readback",
    "structure": "four-part brief: executive summary, introduction, methods, evaluation (in that order), each opened by a chapter card",
    "positioning": "Readback is application-agnostic: for any PM who writes acceptance criteria an AI judge grades a feature against. The AMI meeting-recap feature is only the test bench (Methods, Evaluation).",
    "pacing_words_per_s": round(WPS, 3), "runtime_cap_s": 240,
    "claims_ledger": "CLAIMS.md", "evaluation_plan": "EVAL-PLAN.md",
    "tags": ["Readback", "LLM-as-a-judge", "eval rubric", "AI product management", "INFO 7375"]},
    "beats": beats}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")

# ── report: words, estimated seconds per part ──
tot_w = tot_s = 0.0
for part, label in PARTS.items():
    bs = [b for b in beats if b["act"] == part]
    w = sum(len(b["narration_text"].split()) for b in bs)
    s = sum(b["estimated_duration_s"] + b["hold_after_s"] for b in bs)
    tot_w += w; tot_s += s
    print(f"{label:24s} {len(bs):2d} beats  {w:4d} words  ~{s:5.1f} s")
out = beats[-1]
tot_s += out["estimated_duration_s"]
print(f"{'outro':24s}  1 beat   {len(out['narration_text'].split()):4d} words  ~{out['estimated_duration_s']:5.1f} s")
print(f"TOTAL {int(tot_w)} body words  ~{tot_s:.1f} s  ({int(tot_s // 60)}:{int(tot_s % 60):02d})  cap 4:00")
