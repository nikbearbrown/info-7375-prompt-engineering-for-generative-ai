#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for the Readback pitch film (show-tell format; v2 visuals).

Toolkit: brutalist.art @ cd4bf20, skill show-tell. Every body beat is one drawn
isometric scene (Manim) with a few labels; the narration carries the idea.

Deviations from the stock show-tell spine (the assignment governs):
- No instructor persona, greeting or credit: narration is first person as me,
  disclosed as a synthetic voice; the outro handle is mine (Week 1 patch).
- Bookends: the hesitant-writer open is kept as the hook; the terms card, the
  verdict card and the Claude.ai composer "Your turn" are dropped
  (metadata.bookend_exempt), so no Claude interface appears in the film.

Extra per-beat fields (the schema allows additional properties):
  question_ids, claim_status (exists / will / constructed), evidence, on_screen_label.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "aravind-r-readback-pitch"
TITLE = "Readback"
HANDLE = "Aravind Ravi · INFO 7375"
VOICE = "am_onyx"  # TODO (Aravind, Phase 3): pick the Kokoro voice

RUN = "case-study/outputs/feature-run/ (Claude Opus 5.5, claude-opus-5-5, 2026-10-14)"
SAMPLE = "case-study/data/sample/ (AMI Meeting Corpus, CC BY 4.0, downloaded 2026-10-14)"
RUBRIC = "case-study/constructed/rubric-v0.md (CONSTRUCTED, 2026-10-14)"
BRIEF = "PROJECT-BRIEF.md (2026-10-14)"
ALTS = "FRICTIONAL.md, alternative checks dated 2026-10-14"


def est(text):
    return round(len(text.split()) / 2.5, 1)


def manim(bid, cls, narration, image, show, *, q, status, evidence, label):
    return {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration, "estimated_duration_s": est(narration),
            "voice": VOICE, "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image},
            "question_ids": q, "claim_status": status, "evidence": evidence,
            "on_screen_label": label}


HOOK = {
    "beat_id": "BIDEA", "act": "hook", "lane": "bookend", "proof_gate": "SHOW",
    "narration_text": "Hi, I'm Aravind Ravi, and this pitch is read by a synthetic voice. When you own an AI feature, a judge model scores it against your rubric. So the question isn't only whether my feature passes. It's whether the judge reads my rubric the way I meant it.",
    "voice": VOICE, "engine": "kokoro", "lead_silence_s": 0.8,
    "shot": {"type": "REMOTION", "source": "own",
             "show": [{"at": 0.0, "event": "types 'Does the judge score'"},
                      {"at": 0.4, "event": "backspaces 'score' → 'misread', then 'my rubric'"}],
             "remotion": {"pattern": "BrutalistHesitantWriter",
                          "props": {"text": "Does the judge score my rubric", "triggerWords": "score",
                                    "replacementWords": "misread", "fontSize": 70, "charMs": 22,
                                    "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
                                    "seed": SLUG, "banner": ""}}},
    "motion_claim": "The writer types the naive question and corrects it to the real one: does the judge read the rubric as meant.",
    "qc": {"sparse_by_design": True, "sparse_reason": "Hesitant-writer hook: the correction is the motion."},
    "question_ids": [], "claim_status": "constructed", "evidence": None,
    "on_screen_label": "none (typed question only)",
}

B = [
 manim("B01", "B01_WhatItIs",
       "It's called Readback. It will show a product manager which clause of their eval rubric an AI judge reads differently than they meant. When it's done, it will be a Python repository with a command-line tool, a case study on public meeting data, and a log of judge agreement before and after a revision.",
       "A rubric page with five clause lines stands on the stage; a judge figure reads it; one clause line lifts out "
       "and gets a terracotta tape marker; a small repository box with a terminal prompt drops in beside it.",
       [{"at": 0.1, "event": "rubric page"}, {"at": 0.35, "event": "judge reads"},
        {"at": 0.55, "event": "one clause lifts, tape marker"}, {"at": 0.8, "event": "repo box + terminal"}],
       q=["Q1"], status="will", evidence=[BRIEF], label="CONSTRUCTED — illustration"),
 manim("B02", "B02_Difference",
       'Why care? If the judge misreads a clause, the scores look fine and the ship decision is wrong. I looked at two tools. Maxim AI measures how well several judges agree with humans. Ork dot AI compares an evaluator with human labels, then rewrites its prompt. As far as I could find in their docs on October fourteenth, neither says which clause caused the disagreement. Readback will, and it will ask the P M about that clause instead of rewriting it.',
       "Two plain grey boxes labelled 'Maxim AI' and 'orq.ai' (text only, no logos) each output a single score dial; "
       "a third box, 'Readback', outputs the rubric page with one clause taped and a question mark card beside it.",
       [{"at": 0.15, "event": "score looks fine"}, {"at": 0.35, "event": "Maxim AI box, dial"},
        {"at": 0.55, "event": "orq.ai box, rewritten page"}, {"at": 0.8, "event": "Readback: taped clause + question card"}],
       q=["Q2"], status="will", evidence=[ALTS, BRIEF],
       label="'As far as I could find in their docs, 14 Oct 2026' · names only, no logos"),
 manim("B03", "B03_FirstMinute",
       "The reader is a hiring manager for AI product roles. In the first minute, they'll open the README and see one table: per-clause agreement with my labels, the clause that disagreed most, the question Readback will ask, my revision, and held-out agreement before and after. The end user is a P M with their own rubric.",
       "A README page opens; a five-row table draws itself with EMPTY value cells (no numbers); one row lifts with a "
       "question card; a sixty-second dial sweeps beside it.",
       [{"at": 0.15, "event": "README opens"}, {"at": 0.4, "event": "table draws, cells empty"},
        {"at": 0.65, "event": "one row lifts, question card"}, {"at": 0.85, "event": "60 s dial completes"}],
       q=["Q3"], status="will", evidence=[BRIEF],
       label="CONSTRUCTED mock-up — values will be measured"),
 manim("B04", "B04_Proves",
       "What does it prove? That I treat a rubric as a prompt contract, and verify instead of trust: my labels will be committed before any judge runs, so the git history proves the order. That I'll evaluate per clause on held-out data, and ground claims in transcript lines. A reviewer could conclude I understand why judges need a human anchor. Not that it works for every feature. I'll test one.",
       "A git timeline: a 'labels' commit dot lands first, then a 'judges' commit dot after it; an anchor drops from "
       "the labels dot; a single feature box sits under a '1 feature' label.",
       [{"at": 0.2, "event": "labels commit"}, {"at": 0.4, "event": "judges commit after"},
        {"at": 0.65, "event": "anchor drops"}, {"at": 0.85, "event": "one feature only"}],
       q=["Q4"], status="will", evidence=[BRIEF], label="CONSTRUCTED — planned commit order"),
 manim("B05", "B05_InOutFirst",
       "In: the rubric module, and a case study on ten public AMI meetings, where teams role-play product design. Out: Readback will never rewrite a rubric itself. It asks, and the P M decides. First: one rubric, three judges, and my labels, producing an agreement table. You'll know it ran because its commit comes after my labels' commit.",
       "Ten transcript pages fan out on the stage (real sample); a pencil with a 'no' strike stays away from the rubric "
       "page; three judge figures line up in front of one rubric; an empty table appears after a labels commit dot.",
       [{"at": 0.15, "event": "ten AMI pages"}, {"at": 0.45, "event": "no-rewrite pencil"},
        {"at": 0.7, "event": "three judges, one rubric"}, {"at": 0.88, "event": "table after labels commit"}],
       q=["Q5"], status="exists", evidence=[SAMPLE, RUBRIC],
       label="Real data — AMI Meeting Corpus, CC BY 4.0, downloaded 14 Oct 2026 · rubric CONSTRUCTED"),
 manim("B06", "B06_Risk",
       "What could sink it? Overfitting: revising the rubric until the judges agree on the examples I tuned it on. So I'll freeze a held-out set first, and report only held-out numbers. And because judges can share blind spots, I'll compare same-model and cross-model judges, and report it either way.",
       "A stack of example cards splits in two; the smaller stack goes into a box that locks with a padlock labelled "
       "'held-out'; two judge figures with identical blinkers sit side by side, then a third different one joins.",
       [{"at": 0.2, "event": "cards split"}, {"at": 0.45, "event": "held-out box locks"},
        {"at": 0.75, "event": "same-model pair, then a cross-model judge"}],
       q=["Q6"], status="will", evidence=[BRIEF], label="CONSTRUCTED — planned method"),
 manim("B07", "B07_WhyMe",
       "Why this project? It's a mix. New to me: eval design, judge and human agreement, and multi-model judging. Already mine: writing product requirements, as a P M at L G Energy Solution Vertech, Tech for Dev and Koine Arth, though those documents are internal. From this course: my week one film verified every on-screen number, and I held my week two recipe at draft while to-do items were open. I think e-vals are becoming core to AI PM work, and I don't have an eval project yet.",
       "Two shelves: 'new' holds three empty jars; 'mine' holds a sealed folder (internal, closed) and two open "
       "folders tagged 'PR #8 · open' and 'PR #23 · open, not merged'.",
       [{"at": 0.2, "event": "new shelf"}, {"at": 0.45, "event": "sealed internal folder"},
        {"at": 0.7, "event": "PR #8 tag"}, {"at": 0.85, "event": "PR #23 tag"}],
       q=["Q7"], status="exists",
       evidence=["Week 1: github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/pull/8 (open)",
                 "Week 2: github.com/nikbearbrown/the-reallocation-engine/pull/23 (open, not merged, DRAFT)"],
       label="PR #8 · open · PR #23 · open, not merged — status as of 14 Oct 2026"),
 manim("B08", "B08_ExistsWill",
       "What exists today, October fourteenth: ten AMI meetings, a constructed five-clause rubric, and the recap feature, my prompt, run once on each meeting with Claude Opus five point five. Ten real outputs. What will exist: my labels, the judges, and the agreement table. Those numbers don't exist yet. They will be measured.",
       "Left shelf 'exists': ten pages, the rubric page, and ten recap cards (one shows a real excerpt from a recap). "
       "Right shelf 'will': empty outlines of a label sheet, three judges and a table, drawn in ghost grey.",
       [{"at": 0.15, "event": "exists shelf fills"}, {"at": 0.45, "event": "real recap excerpt card"},
        {"at": 0.75, "event": "will shelf: ghost outlines"}],
       q=["Q5"], status="exists", evidence=[SAMPLE, RUBRIC, RUN],
       label="Real output — Claude Opus 5.5 (claude-opus-5-5), 14 Oct 2026 · rubric CONSTRUCTED · ghost = will"),
]

SPARSE_REASON = ("show-tell style: one drawn scene on a cream stage per beat, minimal labels, the voice carries "
                 "the explanation; only underfill and clustered are waived.")
for b in B:
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}

OUTRO = {"beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW",
         "narration_text": f"{TITLE}. A pitch by Aravind Ravi.", "estimated_duration_s": 4.0,
         "voice": VOICE, "engine": "kokoro", "kind": "outro_voice", "tail_silence_s": 1.0,
         "shot": {"type": "REMOTION", "source": "own", "show": [{"at": 0.0, "event": "title restates; my handle"}],
                  "remotion": {"pattern": "ClaudeTitleOutro",
                               "props": {"title": TITLE, "slug": SLUG, "handle": HANDLE, "subline": "",
                                         "hideMascot": True}}},
         "question_ids": [], "claim_status": "exists", "evidence": None, "on_screen_label": HANDLE}

BEATS = [HOOK] + B + [OUTRO]

# ── v2 visuals (2026-10-14): the hook becomes a drawn Manim scene; every beat names its v2 class and label.
#    Narration and durations are unchanged from v1.
V2_CLASS = {"BIDEA": "BIDEA_Hook", "B01": "B01_WhatItIs", "B02": "B02_Difference", "B03": "B03_FirstMinute",
            "B04": "B04_Proves", "B05": "B05_InOutFirst", "B06": "B06_Risk", "B07": "B07_WhyMe", "B08": "B08_ExistsWill"}
V2_LABEL = {"BIDEA": "CONSTRUCTED — no judges have run yet",
            "B01": "CONSTRUCTED · grey = planned",
            "B02": "per their public docs, as of 14 Oct 2026 · names only (no logos)",
            "B03": "CONSTRUCTED mock-up — values will be measured",
            "B04": "CONSTRUCTED · grey = planned · real pair: AMI ES2007a [00:17:52] + recap (Claude Opus 5.5, 14 Oct 2026)",
            "B05": "AMI sample · CC BY 4.0 · downloaded 14 Oct 2026 · rubric CONSTRUCTED · first run planned",
            "B06": "CONSTRUCTED — planned method",
            "B07": "PR status as of 14 Oct 2026 · roles internal, not shown",
            "B08": "real output · Claude Opus 5.5 · 14 Oct 2026 · grey = will"}
HOOK_V2 = ("The rubric page draws clause by clause; a recap card slides in; three judge tokens stamp pass, pass, fail; "
           "C4 marks red; the line 'Does the judge misread my rubric?' types in.")
for b in BEATS:
    bid = b["beat_id"]
    if bid not in V2_CLASS:
        continue
    if bid == "BIDEA":
        b["lane"] = "manim"
        b["shot"] = {"type": "GRAPHIC", "source": "own", "manim": {"class": "BIDEA_Hook"}, "visual_intent": HOOK_V2,
                     "show": [{"at": 0.02, "event": "rubric C1–C5 draw"}, {"at": 0.32, "event": "recap card"},
                              {"at": 0.4, "event": "3 judges"}, {"at": 0.45, "event": "pass, pass, fail"},
                              {"at": 0.56, "event": "C4 red"}, {"at": 0.73, "event": "typed question"}]}
        b["motion_claim"] = HOOK_V2
    else:
        b["shot"]["manim"] = {"class": V2_CLASS[bid]}
    b["on_screen_label"] = V2_LABEL[bid]
# Silent hold after each beat (add_holds.py pads the measured audio), so the last reveal can be read.
HOLDS = {"BIDEA": 1.0, "B08": 1.5, "BOUT": 1.0}
for b in BEATS:
    b["hold_after_s"] = HOLDS.get(b["beat_id"], 1.0)
sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT PITCH", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "aravind-r", "channel_title": HANDLE, "persona": "Aravind Ravi (synthetic voice)",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "clock": "narration", "palette": "claude",
    "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Assignment pitch film: first person as the student, no instructor persona; the "
                              "hesitant-writer hook replaces the composer cold open; no verdict card and no Claude.ai "
                              "composer Your Turn, so no Claude interface is shown. The outro stays (never exempt)."),
    "audience": "an AI product manager hiring manager",
    "visual_version": "v2 (see ../gates/v2-visual-plan.md)",
    "source_doc": "PROJECT-BRIEF.md (final, 2026-10-14)",
    "tags": ["Readback", "LLM-as-a-judge", "eval rubric", "AI product management", "INFO 7375"]},
    "beats": BEATS}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(len(BEATS), "beats;", words, "words; est",
      round(sum(b.get("estimated_duration_s", est(b["narration_text"])) for b in BEATS)), "s")
