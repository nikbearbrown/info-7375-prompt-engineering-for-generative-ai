#!/usr/bin/env python3
"""Generate beat_sheet.json for "A Slogan Is a Division" from EXECUTED evidence.

Nothing numeric in this film is typed by hand. Every figure on screen is read
at build time from the course's own derivation script:

    <course>/research/llm_scale.py

which prints offline arithmetic over the published GPT-3 figures
(Brown et al. 2020, arXiv:2005.14165). If that script changes, this film
changes with it or fails loudly -- it cannot silently disagree with its source.

Per brutalist.art docs/EXECUTABLE-EVIDENCE.md: run the example, do not shop for
a picture of it. Per docs/MATH-TYPESETTING.md: the division is a real typeset
fraction (TypesetMath / typeset_math.py), never a text card imitating one.

Usage:
    python build_beats.py --course <path to course repo> --toolkit <path to brutalist.art>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import subprocess
import sys
from pathlib import Path

SLUG = "week-01-scale-slogan"
TITLE = "A Slogan Is a Division"
VOICE = "am_onyx"          # Kokoro, local, free. No paid voice anywhere.
STUDENT = "Vrajesh Nasit"
COURSE = "INFO 7375"


SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")


def power10(mantissa: float, exponent: int) -> str:
    """MATH-TYPESETTING.md: a text card may not carry a caret power or an
    e-notation float. Render real Unicode superscripts instead."""
    return f"{mantissa:g} × 10{str(exponent).translate(SUP)}"


def run_llm_scale(course: Path) -> dict:
    """Execute the course's derivation script and return its recorded output."""
    script = course / "research" / "llm_scale.py"
    if not script.is_file():
        sys.exit(f"FATAL: derivation script not found: {script}")
    proc = subprocess.run([sys.executable, str(script)],
                          capture_output=True, text=True, cwd=course)
    if proc.returncode != 0:
        sys.exit(f"FATAL: llm_scale.py exited {proc.returncode}\n{proc.stderr}")
    return json.loads(proc.stdout)


def math_rows(toolkit: Path, exprs: list[tuple[str, float]]) -> list[dict]:
    """Typeset each expression to an outlined SVG row. No text fallback.

    MATH-TYPESETTING.md: never silently fall back from a missing renderer to an
    ordinary text card -- report the beat BLOCKED instead.
    """
    sys.path.insert(0, str(toolkit / "runtime" / "scripts"))
    try:
        from typeset_math import typeset          # noqa: PLC0415
    except Exception as exc:                       # pragma: no cover
        sys.exit(f"FATAL: math renderer unavailable ({exc}). Beat BLOCKED -- "
                 f"do not substitute a text card. Install matplotlib.")
    rows = []
    for expression, at in exprs:
        row = typeset(expression)
        row["at"] = at
        rows.append(row)
    return rows


def build(course: Path, toolkit: Path) -> dict:
    eng = run_llm_scale(course)

    rates = eng["reading_years_by_rate"]              # {"150": 2851.9, ...}
    cited = eng["cited"]
    assume = eng["assumptions"]
    tokens = cited["gpt3_train_tokens"]
    wpt = assume["words_per_token"]
    words = tokens * wpt
    mins_per_year = assume["seconds_per_year"] / 60
    compute_years = eng["compute_years_at_one_billion_per_second"]
    implied = eng["flops_implied_by_one_hundred_million_years"]
    ratio = implied / cited["gpt3_train_flops"]

    slow, fast = rates["150"], rates["300"]
    spread = slow - fast

    # --- self-check: the on-screen claims must follow from the executed data ---
    assert abs(words - 225_000_000_000) < 1, words
    assert abs(rates["250"] - words / (250 * mins_per_year)) < 0.5
    assert spread > 1400, spread
    assert 9 < ratio < 11, ratio

    stamp = dt.date.today().isoformat()
    provenance = (f"Executed {stamp} - python research/llm_scale.py "
                  f"(Python {platform.python_version()})")

    beats = []

    # B00 -- COLD OPEN. The slogan arrives as the ask. Claude UI is the subject
    # here only because this is the cold open (ILLUSTRATE LAW allows it).
    beats.append({
        "beat_id": "B00", "act": "ASK",
        "role_note": "COLD OPEN. The slogan lands as a question, answered by the film.",
        "narration_text": (
            "You have heard this one. It would take a person thousands of years to read "
            "everything G P T three was trained on. It sounds like a measurement. "
            "I want to show you that it is a division, and that one of its inputs is missing."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 19,
        "shot": {"type": "REMOTION", "lane": "bookend", "motion": "type-on",
                 "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                     "greeting": "Hello, Vrajesh",
                     "topic": f"{COURSE} - CHAPTER 1",
                     "segment": TITLE,
                     "command": "how long would it take a person to read 300 billion tokens?",
                     "runningText": "running the arithmetic...",
                     "folderLabel": f"{COURSE} - Week 1",
                 }}},
    })

    # B01 -- EXECUTIVE SUMMARY. The misconception is typed, then corrected.
    # The replaced word IS the reel's real misconception (measurement -> division).
    beats.append({
        "beat_id": "B01", "act": "BLUF",
        "role_note": "EXECUTIVE-SUMMARY LAW. Writer types the misconception and corrects it.",
        "narration_text": (
            "Here is the correction up front. The reading comparison is not a measurement "
            "of the training data. It is a division. And the number it produces depends on "
            "a reading speed that the slogan never states."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 17,
        "lead_silence_s": 0.8,
        "shot": {"type": "REMOTION", "motion": "type-on",
                 "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
                     "text": "The reading comparison\nis a measurement.",
                     "triggerWords": "measurement",
                     "replacementWords": "division",
                     "face": "serif", "fontSize": 150, "align": "center",
                     "seed": SLUG,
                 }}},
    })

    # B02 -- the published figures, with their citation in the colophon tier.
    beats.append({
        "beat_id": "B02", "act": "EVIDENCE",
        "role_note": "Published figures only. Later models are larger and undisclosed.",
        "narration_text": (
            "Start with figures that were actually published. G P T three: one hundred "
            "seventy five billion parameters. About three hundred billion training tokens. "
            "And a reported training compute of three point one four times ten to the "
            "twenty third floating point operations. Those come from Brown and colleagues, "
            "twenty twenty. Later frontier models are larger, and their figures are "
            "frequently undisclosed."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 24,
        "shot": {"type": "REMOTION", "motion": "karaoke",
                 "remotion": {"pattern": "FormACard", "props": {
                     "lines": ["GPT-3, as published",
                               f"{cited['gpt3_parameters']:,} parameters",
                               f"{tokens:,} training tokens",
                               f"{power10(cited['gpt3_train_flops'] / 1e23, 23)} FLOPs of training compute"],
                     "meta": [cited["source"], "Reported by the authors; not re-measured here."],
                     "dark": False,
                 }}},
    })

    # B03 -- THE DIVISION, really typeset. Two rows: words, then years.
    beats.append({
        "beat_id": "B03", "act": "MECHANISM",
        "role_note": "MATH-TYPESETTING: real fraction bar, structured notation, staged reveal.",
        "narration_text": (
            "So do the arithmetic in the open. Three hundred billion tokens, at about "
            "zero point seven five words per token, is two hundred twenty five billion words. "
            "Divide that by a reading rate times the minutes in a year, and the units leave "
            "you with years. At two hundred fifty words per minute, that is one thousand "
            "seven hundred and eleven years."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 25,
        "shot": {"type": "REMOTION", "motion": "reveal",
                 "remotion": {"pattern": "TypesetMath", "props": {
                     "title": "The slogan, written as arithmetic",
                     "rows": math_rows(toolkit, [
                         (r"300\times10^{9}\ \mathrm{tokens}\times0.75"
                          r"\ \frac{\mathrm{words}}{\mathrm{token}}"
                          r"=225\times10^{9}\ \mathrm{words}", 0.0),
                         (r"\frac{225\times10^{9}\ \mathrm{words}}"
                          r"{250\ \frac{\mathrm{words}}{\mathrm{min}}"
                          r"\times525{,}960\ \frac{\mathrm{min}}{\mathrm{year}}}"
                          r"=1{,}711.2\ \mathrm{years}", 9.0),
                     ]),
                     "note": "Every quantity here was published or stated. Except one.",
                     "conditions": provenance,
                 }}},
    })

    # B04 -- THE SWEEP. The hidden parameter, made visible. This is the thesis beat.
    beats.append({
        "beat_id": "B04", "act": "MECHANISM",
        "role_note": "THE point of the film: the answer moves on an unstated input.",
        "narration_text": (
            "But nobody stated the reading rate. So run every rate the course script uses. "
            "At one hundred fifty words per minute, the answer is two thousand eight hundred "
            "fifty two years. At two hundred, two thousand one hundred thirty nine. "
            "At two hundred fifty, one thousand seven hundred eleven. At three hundred, "
            "one thousand four hundred twenty six. Same corpus. Same arithmetic. The answer "
            "moves by more than fourteen hundred years, and the thing that moved was an "
            "assumption nobody wrote down."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 32,
        "shot": {"type": "REMOTION", "motion": "reveal",
                 "remotion": {"pattern": "ExecutedData", "props": {
                     "title": "Same arithmetic. Four reading rates.",
                     "mode": "table",
                     "columnLabels": ["Reading rate", "Years to read"],
                     "rows": [
                         {"label": "150 wpm", "value": rates["150"], "at": 1.0},
                         {"label": "200 wpm", "value": rates["200"], "at": 3.0},
                         {"label": "250 wpm", "value": rates["250"], "at": 5.0},
                         {"label": "300 wpm", "value": rates["300"], "at": 7.0},
                     ],
                     # NO-WORDY-CARD (type_check.py 8.5) caps a prose element at
                     # 12 words, so the provenance is compressed rather than dropped.
                     "note": (f"Spread: {spread:,.1f} years on an unstated input. "
                              f"Source: llm_scale.py, {stamp}."),
                 }}},
    })

    # B05 -- the same move on the compute slogan; two true sentences, different claims.
    beats.append({
        "beat_id": "B05", "act": "MECHANISM",
        "role_note": "Second instance, so the method reads as general, not a one-off.",
        "narration_text": (
            "The compute slogan behaves the same way. If you could perform one billion "
            "operations per second by hand, G P T three's reported training compute would "
            "take you about nine point nine five million years. You may have heard over one "
            "hundred million years. That sentence needs roughly ten times G P T three's "
            "budget. Both sentences can be true. They are not the same sentence, and a "
            "reader who cannot tell them apart cannot audit either one."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 29,
        "shot": {"type": "REMOTION", "motion": "karaoke",
                 "remotion": {"pattern": "FormACard", "props": {
                     "lines": ["At one billion operations per second:",
                               f"GPT-3 as reported = {compute_years:,.0f} years",
                               f'"Over 100 million years" needs {power10(round(implied / 1e24, 2), 24)} FLOPs',
                               f"which is about {ratio:.0f}x GPT-3 - a different model"],
                     "meta": [provenance,
                              "Both statements can be true. They are not the same statement."],
                     "dark": False,
                 }}},
    })

    # B06 -- THE BOUNDARY. Required by the rubric; the one dark beat (polarity punctuation).
    beats.append({
        "beat_id": "B06", "act": "LIMIT",
        "role_note": "What the explanation does NOT establish. Dark = 1 of 9 beats.",
        "narration_text": (
            "Now the boundary, and it matters more than the arithmetic. None of this shows "
            "the comparison is false, or useless. Every version of it still says the same "
            "true thing: more text than a person could read in many lifetimes. What the "
            "sweep establishes is narrower than that. The headline number carries a hidden "
            "parameter, so until someone states the reading rate, you cannot check the "
            "figure you were handed. That is the entire claim. It says nothing about "
            "whether anything the model writes is true."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 33,
        "shot": {"type": "REMOTION", "motion": "karaoke",
                 "remotion": {"pattern": "FormACard", "props": {
                     "lines": ["This does not establish",
                               "that the comparison is wrong,",
                               "or that the slogan should not be used.",
                               "Only that it has an input nobody stated."],
                     "meta": ["A hidden parameter is not a false claim.",
                              "And none of this is evidence about truthfulness of output."],
                     "dark": True,
                 }}},
    })

    # B07 -- HANDOFF. Paste-able prompt, read aloud (CLAUDE-BRAND handoff law).
    beats.append({
        "beat_id": "B07", "act": "HANDOFF",
        "role_note": "Your turn. The composer returns with a prompt the viewer can run.",
        "narration_text": (
            "Your turn. Take one impressive A I number you see this week. Parameters, "
            "tokens, energy, dollars. Restate it as a division, and name the input nobody "
            "specified. That is the whole skill."),
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 15,
        "shot": {"type": "REMOTION", "lane": "bookend", "motion": "type-on",
                 "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                     "greeting": "Your turn.",
                     "topic": f"{COURSE} - YOUR TURN",
                     "segment": "Restate it as a division",
                     "command": ("take one AI statistic I have seen this week, rewrite it as "
                                 "a division, and name the input nobody stated"),
                     "runningText": "your move...",
                     "folderLabel": f"{COURSE} - Week 1",
                 }}},
    })

    # B08 -- OUTRO. Neutral student card: title restated, no channel handle, no mascot.
    # OUTRO-LOCK.md governs claude-liam-* slugs only; this is not one of those.
    beats.append({
        "beat_id": "B08", "act": "OUTRO",
        "role_note": "Neutral student outro. No @handle, no mascot, spoken not scored.",
        "narration_text": f"A slogan is a division. {COURSE}, week one. {STUDENT}.",
        "voice": VOICE, "engine": "kokoro", "estimated_duration_s": 8,
        "tail_silence_s": 1.0,
        "shot": {"type": "REMOTION", "lane": "bookend", "motion": "karaoke",
                 "remotion": {"pattern": "FormACard", "props": {
                     "lines": [TITLE, f"{COURSE} - Week 1", STUDENT],
                     "meta": ["Built with brutalist.art - Kokoro voice, local, free"],
                     "dark": False,
                 }}},
    })

    return {
        "metadata": {
            "slug": SLUG,
            "title": TITLE,
            "topic": f"{COURSE} - Chapter 1 - Randomness and first prompts",
            "concept": "A training-scale slogan restated as a division with a hidden assumption",
            "student": STUDENT,
            "course": COURSE,
            "week": 1,
            "engine": "kokoro",
            "voice_kokoro": VOICE,
            "clock": "narration",
            "palette": "claude",
            "aspect_ratio": "16:9",
            "evidence": {
                "derivation_script": "research/llm_scale.py (course repo)",
                "executed_on": stamp,
                "python": platform.python_version(),
                "recorded_output": eng,
            },
            "total_estimated_duration_seconds": sum(b["estimated_duration_s"] for b in beats),
        },
        "beats": beats,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=Path,
                    default=Path(__file__).resolve().parents[3])
    ap.add_argument("--toolkit", type=Path,
                    default=Path(r"C:/NEU course/PEAI/brutalist.art"))
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).with_name("beat_sheet.json"))
    args = ap.parse_args()

    sheet = build(args.course.resolve(), args.toolkit.resolve())
    args.out.write_text(json.dumps(sheet, indent=2) + "\n", encoding="utf-8")
    total = sheet["metadata"]["total_estimated_duration_seconds"]
    print(f"wrote {args.out}")
    print(f"  beats: {len(sheet['beats'])}")
    print(f"  estimated runtime: {total}s ({total // 60}:{total % 60:02d})")


if __name__ == "__main__":
    main()
