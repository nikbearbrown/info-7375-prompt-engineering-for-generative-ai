#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for agent-reliability-audit-pitch.

This script writes the PRE-AUDIO beat sheet. The submitted beat_sheet.json is the
POST-BUILD version — it additionally carries measured audio durations,
render records, and the BCLOSE silent-tail fix, none of which this
script produces. Do not re-run this script before rebuilding the real
master, or those measured fields and the BCLOSE fix will be lost.

This is a PITCH film: the tool it describes does not exist yet. Every
narration line is written in present/future tense accordingly — nothing is
claimed as built or measured except the one cited external source (see
SOURCES.md) and the one real, named GitHub pull request referenced in B07.

Narrated as myself (Om Raut), first person. No instructor name or persona
("Liam", "Bear", "in for Bear") appears in any narration_text. The outro
bookend (ClaudeTitleOutro) is NOT used at all, specifically because its
Remotion component hardcodes "@NikBearBrown" and ignores its own `handle`
prop — confirmed by reading ClaudeTitleOutro.tsx directly rather than
assuming. The film ends on one more plain drawn beat instead.

bookend_check.py is not invoked by `art run` or `art final` (confirmed by
reading run.sh / compile.py), so skipping the ClaudeTitleOutro bookend
entirely does not fail any gate that actually runs in this pipeline.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "agent-reliability-audit-pitch"
TITLE = "agent-reliability-audit: pass-at-k isn't enough"


def beat(bid, narration, cls, image, show, qc_waive=True):
    b = {
        "beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
        "narration_text": narration,
        "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
        "voice": "am_onyx", "engine": "kokoro",
        "shot": {
            "type": "GRAPHIC", "source": "own",
            "visual_intent": image, "motion_claim": image, "show": show,
            "manim": {"class": cls},
        },
    }
    if qc_waive:
        b["qc"] = {
            "sparse_by_design": True,
            "sparse_reason": (
                "show-tell style: one drawn scene on the cream stage per beat, "
                "minimal labels, narration carries the explanation. Negative "
                "space is the style; only underfill/clustered are waived."
            ),
        }
    return b


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", lane="bookend", **extra):
    b = {
        "beat_id": bid, "act": act, "lane": lane, "proof_gate": gate,
        "narration_text": narration,
        "estimated_duration_s": round(len(narration.split()) / 2.5, 1),
        "voice": "am_onyx", "engine": "kokoro",
        "shot": {"type": "REMOTION", "source": "own", "show": show,
                 "remotion": {"pattern": pattern, "props": props}},
    }
    b.update(extra)
    return b


# ── Opening bookends (hesitant writer + definitions; no persona, no handle) ──

BIDEA = remotion(
    "BIDEA", "the question",
    "Here's the pitch, and I want to be upfront about this part first: "
    "nothing in this film has been built yet. It's an honest plan for a "
    "tool that checks one thing most agent demos never check.",
    "BrutalistHesitantWriter",
    {
        "text": "I'm building an agent that works.",
        "triggerWords": "that works",
        "replacementWords": "that's reliably right",
        "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1,
        "mistakeRate": 2, "jitter": 20, "seed": SLUG, "banner": "",
    },
    [
        {"at": 0.0, "event": "types 'I'm building an agent that works.'"},
        {"at": 0.6, "event": "corrects 'that works' -> 'that is reliably right, not just right once'"},
    ],
    lead_silence_s=0.8,
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."},
)

BDEFS = remotion(
    "BDEFS", "terms",
    "Three terms. Pass-at-k: did it succeed at least once across k tries. "
    "Pass-caret-k: did it succeed every single time. And a tool contract: "
    "the deal a tool makes about what it will actually return.",
    "ClaudeDefinitions",
    {
        "title": "Terms In This Film",
        "terms": [
            {"term": "pass@k", "meaning": "succeeded at least once in k tries"},
            {"term": "pass^k", "meaning": "succeeded every single time"},
            {"term": "tool contract", "meaning": "what a tool promises to return"},
        ],
        "folderLabel": "",
    },
    [
        {"at": 0.15, "event": "'pass@k' lands"},
        {"at": 0.5, "event": "'pass^k' lands"},
        {"at": 0.8, "event": "'tool contract' lands"},
    ],
    gate="CARD",
    qc={"sparse_by_design": True, "sparse_reason": "Terms card: three prerequisites, one line each."},
)

# ── Body: one consistent cast — a crate labeled AGENT, a conveyor + gate(s), ──
# ── a docs.python.org page, a dashboard with two counters, one broken gate. ──

B00 = beat(
    "B00",
    "Picture the thing I'm building as a crate. Open it up, and there's "
    "exactly one tool inside — it reaches out and fetches a real page "
    "from Python's own documentation.",
    "B00_CrateOpens",
    "A crate labeled AGENT drops onto the stage; the lid lifts; a cable "
    "draws from inside it out to a small page icon labeled docs.python.org.",
    [
        {"at": 0.1, "event": "crate drops in"},
        {"at": 0.4, "event": "lid lifts"},
        {"at": 0.7, "event": "cable draws to the docs.python.org page"},
    ],
)

B01 = beat(
    "B01",
    "I'll run the same real question through that same tool, five times "
    "in a row, and watch what comes back each time.",
    "B01_ConveyorLoop",
    "The crate rides a conveyor through one gate, five times in a loop; "
    "each pass lights the gate briefly.",
    [
        {"at": 0.15, "event": "conveyor and gate appear"},
        {"at": 0.4, "event": "first pass, gate lights"},
        {"at": 0.75, "event": "loop continues, gate lights again"},
    ],
)

B02 = beat(
    "B02",
    "This next number isn't mine. A 2026 agent-evaluation methodology "
    "piece reports a real example: an agent can look ninety-seven "
    "percent successful under pass-at-three.",
    "B02_PassAtKCounter",
    "A counter climbs to 97 percent, with a small on-screen label reading "
    "'cited, not mine'.",
    [
        {"at": 0.2, "event": "counter starts climbing"},
        {"at": 0.65, "event": "counter settles at 97%, CITED label appears"},
    ],
)

B03 = beat(
    "B03",
    "The same source reports the all-three-times number for that same "
    "agent at around thirty-four percent — a sixty-three point gap. "
    "That gap is the whole reason this tool exists.",
    "B03_PassCaretKCounter",
    "A second, smaller counter appears beside the first, falling to 34 "
    "percent, same 'cited, not mine' label carried over.",
    [
        {"at": 0.2, "event": "second counter appears"},
        {"at": 0.6, "event": "it falls to 34%"},
    ],
)

B04 = beat(
    "B04",
    "Here's the other half of the audit: what happens when the tool "
    "itself lies to the agent? I'll deliberately feed it a broken "
    "response — malformed data, a stale page, a timeout.",
    "B04_GateBreaks",
    "One gate on the conveyor cracks and turns jagged; a small warning "
    "icon appears over it.",
    [
        {"at": 0.25, "event": "gate cracks"},
        {"at": 0.6, "event": "warning icon appears"},
    ],
)

B05 = beat(
    "B05",
    "From there the crate has two paths. One: it notices and refuses to "
    "guess. Two: it quietly passes the bad data through anyway. One of "
    "those is safe. The other is the failure mode nobody shows you.",
    "B05_TwoPaths",
    "The conveyor forks past the broken gate: one path ends at a stop "
    "sign with a check; the other continues through with a faded, "
    "uncertain box.",
    [
        {"at": 0.2, "event": "fork appears"},
        {"at": 0.5, "event": "safe path: stop sign + check"},
        {"at": 0.8, "event": "unsafe path: faded box continues"},
    ],
)

B06 = beat(
    "B06",
    "I'm keeping this small on purpose: one real tool, ten real "
    "questions, one documentation source. The hard part isn't the demo "
    "— it's making the interface work with any agent, not just mine. If "
    "I run out of time, I'll say so plainly instead of pretending "
    "otherwise.",
    "B06_SmallScope",
    "The same crate sits alone on an otherwise empty stage, with a small "
    "label reading '1 tool'.",
    [{"at": 0.2, "event": "crate alone, label settles"}],
)

B07 = beat(
    "B07",
    "Most of this is new to me — I've never built a fault-injection "
    "harness before. But the instinct isn't new. In a real pull request "
    "I have open right now, I deliberately tried to break a different "
    "scoring system and found a real flaw in it. This applies that same "
    "habit to agents instead.",
    "B07_PullRequest",
    "The crate sits beside a small GitHub pull-request icon, connected "
    "by one line.",
    [{"at": 0.2, "event": "crate and PR icon, line connects them"}],
)

YT_PROMPT = (
    "Pick an agent you've built. Run its hardest task five times in a row. "
    "Tell me honestly: did it succeed every single time, or just once? "
    "If it has any tool calls, tell me what happens if one of those tools "
    "returns something malformed or wrong."
)

BHTF = remotion(
    "BHTF", "your turn",
    "If you want to try this yourself: paste this into Claude. " + YT_PROMPT +
    " Then check two things. Did it actually run five real times, not just "
    "once? And did it tell you what happens when a tool lies to it?",
    "ClaudeComposerAsk",
    {
        "greeting": "Your turn.",
        "topic": "AGENT RELIABILITY · YOUR TURN",
        "segment": "Check Your Own Agent",
        "command": YT_PROMPT,
        "runningText": "paste this into Claude…",
        "output": [
            "Check: it actually ran five times, not once.",
            "Check: it says what happens when a tool returns bad data.",
        ],
        "folderLabel": "",
        "modelLabel": "",
        "effortLabel": "",
    },
    [
        {"at": 0.0, "event": "composer opens — 'Your turn.'"},
        {"at": 0.15, "event": "the prompt types in full"},
        {"at": 0.8, "event": "two check lines land"},
    ],
)

# ── Closing beat: a plain drawn scene, NOT ClaudeTitleOutro ──
# (ClaudeTitleOutro.tsx hardcodes "@NikBearBrown" and ignores its own
# `handle` prop — confirmed by reading the component source. Ending on one
# more drawn beat avoids that entirely, and fits show-tell's own style.)

BCLOSE = beat(
    "BCLOSE",
    f"That's {TITLE.split(':')[0]} — nothing built yet, but the plan is "
    "real, and the repo link is in the description if you want to watch "
    "it get built.",
    "BCLOSE_TitleCard",
    "The crate, conveyor, and dashboard from earlier settle together one "
    "last time; the project name is drawn in simple ink lettering beside "
    "them.",
    [
        {"at": 0.2, "event": "cast settles together"},
        {"at": 0.6, "event": "project name draws in"},
    ],
    qc_waive=True,
)

BODY = [B00, B01, B02, B03, B04, B05, B06, B07]
BEATS = [BIDEA, BDEFS] + BODY + [BHTF, BCLOSE]

sheet = {
    "metadata": {
        "slug": SLUG,
        "title": TITLE,
        "topic": "AGENT EVALUATION · RELIABILITY",
        "skill": "show-tell",
        "style_preset": "show-tell",
        "channel": "",
        "persona": "Om Raut, narrated in first person (synthetic Kokoro voice — see SOURCES.md)",
        "voice": "am_onyx",
        "voice_kokoro": "am_onyx",
        "engine": "kokoro",
        "clock": "narration",
        "palette": "claude",
        "register": "plain, direct, first-person",
        "fps": 24,
        "aspect_ratio": "16:9",
        "width": 3840,
        "height": 2160,
        "caption_policy": "none",
        "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
        "bookend_exempt_reason": (
            "show-tell pitch film: opens on the hesitant writer + terms card, "
            "no verdict card. The ClaudeTitleOutro bookend is deliberately not "
            "used at all (its handle prop is hardcoded and ignored by the "
            "component — see make_sheet.py docstring), so bookend_exempt "
            "includes 'bhtf' defensively even though no automated gate in "
            "this pipeline actually calls bookend_check.py."
        ),
        "audience": "a hiring manager or engineer evaluating my work for an ML/AI engineering role",
        "source_doc": (
            "Pass@k vs pass^k framing and its illustrative figures: "
            "'Building an AI Agent Evaluation Pipeline: 2026 Methodology,' "
            "digitalapplied.com (cited, not my own result — see SOURCES.md)."
        ),
        "tags": ["agent evaluation", "reliability", "pass@k", "fault injection", "tool contracts"],
    },
    "beats": BEATS,
}

(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(BEATS), "beats; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")
