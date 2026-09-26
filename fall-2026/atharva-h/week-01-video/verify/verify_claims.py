#!/usr/bin/env python3
"""
verify_claims.py — every number used in the Week 01 video, computed and checked.

WHY THIS FILE EXISTS
    The video makes numerical claims. This script is the evidence for each one.
    Nothing appears on screen that is not produced here first. Run it, read the
    log, and you can audit the video without watching it.

WHAT IS BEING VERIFIED
    The concept: the final step of a language model (the softmax) keeps only the
    GAPS between scores and discards their overall level. Consequences:
      - shifting every score by the same amount changes nothing        (C3)
      - therefore "all of these are bad" has no output shape           (argued, not computed)
      - stretching the gaps IS what temperature does                    (C12)
      - and if floating-point rounding ALTERS the gaps, the meaning
        silently changes while every test still passes            (C6-C9, C14)

PROVENANCE OF THE IMPLEMENTATION
    `probabilities` and `sample` below are reproduced verbatim from Chapter 1,
    "Randomness and first prompts", code listings at lines 170-182 and 228-241.
    The chapter states they mirror lessons/01-randomness-and-first-prompts/code/main.py
    in the course book repository. That repository was not available on this
    machine (see FRICTIONAL.md), so the chapter's printed listing is the source,
    and C1 cross-checks our output against the chapter's own recorded tables.

USAGE
    python3 verify_claims.py                 # human-readable log to stdout
    python3 verify_claims.py --json out.json # also write machine-readable record

    Stdlib only. No dependencies, no API keys, no network.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import platform
import random
import sys
from collections import Counter

# ─────────────────────────────────────────────────────────────────────────────
# The implementation under test — verbatim from Chapter 1, lines 170-182.
# ─────────────────────────────────────────────────────────────────────────────


def probabilities(logits, temperature=1.0):
    if not logits or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Need logits and a positive finite temperature")
    if not all(math.isfinite(x) for x in logits):
        raise ValueError("Logits must be finite")
    peak = max(logits)
    weights = [math.exp((x - peak) / temperature) for x in logits]
    total = sum(weights)
    return [weight / total for weight in weights]


# Chapter 1, lines 228-241.
def sample(logits, count=1000, seed=7, temperature=1.0):
    if type(count) is not int or count < 0:
        raise ValueError("Count must be nonnegative")
    rng = random.Random(seed)
    return dict(Counter(rng.choices(
        range(len(logits)),
        probabilities(logits, temperature),
        k=count,
    )))


# ─────────────────────────────────────────────────────────────────────────────
# Comparison functions — deliberately NOT softmax. Used as a negative control.
# Both return positive, normalised values. Neither is shift-invariant.
# Their job is to show that C3 is a real property, not an artefact of the demo.
# ─────────────────────────────────────────────────────────────────────────────


def square_normalise(logits):
    weights = [x * x for x in logits]
    total = sum(weights)
    return [w / total for w in weights]


def abs_normalise(logits):
    weights = [abs(x) for x in logits]
    total = sum(weights)
    return [w / total for w in weights]


# ─────────────────────────────────────────────────────────────────────────────
# Tiny check runner. Each claim records what was expected, what was observed,
# and whether they agree. A failed claim is printed, not swallowed.
# ─────────────────────────────────────────────────────────────────────────────

CLAIMS: list[dict] = []


def claim(cid: str, statement: str, passed: bool, evidence: dict) -> None:
    CLAIMS.append({
        "id": cid,
        "statement": statement,
        "passed": bool(passed),
        "evidence": evidence,
    })
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {cid}  {statement}")
    for key, value in evidence.items():
        print(f"         {key}: {value}")
    print()


def fmt(values, places: int = 10) -> list[str]:
    return [f"{v:.{places}f}" for v in values]


# Constructed input. The chapter is explicit at line 134 that these scores were
# chosen by hand: "In this example I have chosen them; no model produced them."
# They are NOT measurements from any language model.
BASE_SCORES = [1.0, 2.0, 3.0]

# The chapter's own recorded results, transcribed from its tables, used as the
# reference our run is checked against.
CHAPTER_PROBABILITIES = {
    0.5: ["0.0158762400", "0.1173104278", "0.8668133322"],   # chapter line 208
    1.0: ["0.0900305732", "0.2447284711", "0.6652409558"],   # chapter line 209
    2.0: ["0.1863237232", "0.3071958857", "0.5064803911"],   # chapter line 210
}
CHAPTER_COUNTS = {                                            # chapter lines 255-257
    0.5: [18, 133, 849],
    1.0: [102, 268, 630],
    2.0: [202, 329, 469],
}


# ─────────────────────────────────────────────────────────────────────────────


def c1_reproduce_chapter_probabilities() -> None:
    """Our run must agree with the chapter's published probability table."""
    observed = {T: fmt(probabilities(BASE_SCORES, T)) for T in (0.5, 1.0, 2.0)}
    agrees = all(observed[T] == CHAPTER_PROBABILITIES[T] for T in observed)
    claim(
        "C1",
        "Our probabilities match the chapter's recorded table to 10 decimal places",
        agrees,
        {"chapter": CHAPTER_PROBABILITIES, "observed": observed},
    )


def c2_reproduce_chapter_counts() -> None:
    """
    Sampling counts. The chapter's run used Python 3.14.6. We record ours and
    report agreement as an OBSERVATION, not an assertion -- random.choices is
    not contractually stable across interpreter versions, and pretending
    otherwise would be the exact overclaim this chapter is about.
    """
    observed = {}
    for T in (0.5, 1.0, 2.0):
        counts = sample(BASE_SCORES, count=1000, seed=7, temperature=T)
        observed[T] = [counts.get(i, 0) for i in range(3)]  # absent key -> 0
    agrees = all(observed[T] == CHAPTER_COUNTS[T] for T in observed)
    claim(
        "C2",
        "Seeded sample counts reproduce the chapter's recorded run on this interpreter",
        agrees,
        {
            "chapter_counts": CHAPTER_COUNTS,
            "observed_counts": observed,
            "chapter_interpreter": "Python 3.14.6",
            "this_interpreter": platform.python_version(),
            "note": "Disagreement here is a portability finding, not a bug in either run.",
        },
    )


def c3_shift_invariance_holds() -> None:
    """Adding the same constant to every score must not change the output."""
    truth = probabilities(BASE_SCORES)
    results = {}
    all_identical = True
    for exponent in range(0, 16):          # 1e0 .. 1e15, all below 2**53
        shift = 10.0 ** exponent
        shifted = probabilities([x + shift for x in BASE_SCORES])
        identical = shifted == truth       # exact equality, not isclose
        results[f"1e{exponent}"] = "identical" if identical else fmt(shifted)
        all_identical &= identical
    claim(
        "C3",
        "Shifting all scores by up to 1e15 leaves the output bit-for-bit identical",
        all_identical,
        {"unshifted": fmt(truth), "by_shift": results,
         "comparison": "exact list equality (==), not math.isclose"},
    )


def c4_negative_control() -> None:
    """
    The control that makes C3 meaningful. Two other ways of turning scores into
    positive normalised values, both of which DO change under an identical shift.
    If these also held steady, C3 would be telling us nothing about softmax.
    """
    evidence, all_broke = {}, True
    for name, fn in (("x_squared", square_normalise), ("abs_x", abs_normalise)):
        base = fn(BASE_SCORES)
        shifted = fn([x + 100.0 for x in BASE_SCORES])
        changed = base != shifted
        all_broke &= changed
        evidence[name] = {
            "on_[1,2,3]": fmt(base, 6),
            "on_[101,102,103]": fmt(shifted, 6),
            "changed_under_shift": changed,
        }
    evidence["softmax_for_contrast"] = {
        "on_[1,2,3]": fmt(probabilities(BASE_SCORES), 6),
        "on_[101,102,103]": fmt(probabilities([x + 100.0 for x in BASE_SCORES]), 6),
        "changed_under_shift": probabilities(BASE_SCORES) != probabilities(
            [x + 100.0 for x in BASE_SCORES]),
    }
    claim(
        "C4",
        "Negative control: x^2 and |x| normalisation are NOT shift-invariant, softmax is",
        all_broke,
        evidence,
    )


def c5_ratio_depends_only_on_difference() -> None:
    """The mechanism behind C3: exp(a)/exp(b) = exp(a-b)."""
    p = probabilities(BASE_SCORES)
    checks = {
        "p2/p1": (p[2] / p[1], math.exp(3 - 2)),
        "p2/p0": (p[2] / p[0], math.exp(3 - 1)),
        "p1/p0": (p[1] / p[0], math.exp(2 - 1)),
    }
    ok = all(math.isclose(a, b, rel_tol=1e-12) for a, b in checks.values())
    claim(
        "C5",
        "Every probability ratio equals exp(score difference) -- only gaps matter",
        ok,
        {k: {"observed": f"{a:.12f}", "exp(difference)": f"{b:.12f}"}
         for k, (a, b) in checks.items()},
    )


def c6_exact_breaking_threshold() -> None:
    """
    Where shift-invariance stops being true in floating point.
    2**53 is the largest integer for which float64 represents every integer;
    above it consecutive integers start collapsing onto the same value.
    """
    truth = probabilities(BASE_SCORES)
    p53 = 2 ** 53
    scan = {}
    for delta in range(-4, 5):
        shift = float(p53 + delta)
        shifted_scores = [x + shift for x in BASE_SCORES]
        out = probabilities(shifted_scores)
        scan[f"2**53{delta:+d}"] = {
            "gaps": [shifted_scores[1] - shifted_scores[0],
                     shifted_scores[2] - shifted_scores[1]],
            "output": fmt(out, 8),
            "matches_unshifted": out == truth,
        }
    holds_below = scan["2**53-3"]["matches_unshifted"]
    breaks_at = not scan["2**53-2"]["matches_unshifted"]
    claim(
        "C6",
        "Shift-invariance holds at 2**53-3 and breaks at 2**53-2 (float64 integer limit)",
        holds_below and breaks_at,
        {"two_to_the_53": p53, "scan": scan,
         "reason": "past 2**53, float64 can no longer represent consecutive integers, "
                   "so the gaps between scores are altered by rounding"},
    )


def c7_failure_mode_invented_confidence() -> None:
    """
    Failure A. At shift 1e16 rounding widens the gaps from 1 to 2. Doubling the
    gaps is arithmetically identical to halving the temperature -- so the broken
    output is indistinguishable from a deliberate temperature change.
    """
    broken = fmt(probabilities([x + 1e16 for x in BASE_SCORES]))
    chapter_half_temperature = CHAPTER_PROBABILITIES[0.5]
    shifted_scores = [x + 1e16 for x in BASE_SCORES]
    claim(
        "C7",
        "At shift 1e16 the output is digit-identical to the chapter's temperature 0.5 row",
        broken == chapter_half_temperature,
        {
            "shift_1e16_at_temperature_1.0": broken,
            "chapter_temperature_0.5_row": chapter_half_temperature,
            "gaps_after_rounding": [shifted_scores[1] - shifted_scores[0],
                                    shifted_scores[2] - shifted_scores[1]],
            "interpretation": "a rounding artefact is indistinguishable from turning "
                              "the confidence dial; the output alone cannot tell you which",
        },
    )


def c8_failure_mode_invented_ignorance() -> None:
    """
    Failure B. At shift 1e17 all three scores round to the same float. The gaps
    become zero and the output is perfectly uniform -- the shape this video
    identifies as 'no preference'. The bug manufactures apparent uncertainty.
    """
    shifted_scores = [x + 1e17 for x in BASE_SCORES]
    out = probabilities(shifted_scores)
    uniform = len(set(out)) == 1
    claim(
        "C8",
        "At shift 1e17 all scores collapse to one value and the output is exactly uniform",
        uniform,
        {
            "distinct_shifted_scores": sorted(set(shifted_scores)),
            "output": fmt(out),
            "interpretation": "uniform is the shape of 'no preference'; here it is "
                              "produced by rounding, not by anything the model knows",
        },
    )


def c9_the_test_still_passes() -> None:
    """
    The point of the whole exercise. Both wrong outputs satisfy the property the
    chapter's own test checks. Compare Assignment 10, chapter line 373, which
    asks the reader to CONSTRUCT a bug that survives an assertion.
    """
    evidence, all_pass = {}, True
    for label, shift in (("shift_1e16_invented_confidence", 1e16),
                         ("shift_1e17_invented_ignorance", 1e17)):
        out = probabilities([x + shift for x in BASE_SCORES])
        total = sum(out)
        passes = math.isclose(total, 1.0)
        all_pass &= passes
        evidence[label] = {
            "output": fmt(out),
            "sum": repr(total),
            "math.isclose(sum, 1.0)": passes,
        }
    claim(
        "C9",
        "Both broken outputs pass a sum-to-one check -- the green test sees nothing",
        all_pass,
        evidence | {"note": "sum-to-one tests normalisation. It cannot test whether "
                            "the gaps that went in were the gaps that were meant."},
    )


def c10_my_own_assumption_was_wrong() -> None:
    """
    Recorded because it is part of the honest log, not because it is flattering.
    Looking for the threshold, I first used a binary search, which assumes the
    predicate is monotonic -- once broken, stays broken. It is not. The region
    around 2**53 is not monotonic, so that search was invalid and its answer
    was not trustworthy. C6's scan replaced it.
    """
    truth = probabilities(BASE_SCORES)
    p53 = 2 ** 53
    states = {}
    for delta in (2, 3, 4):
        out = probabilities([x + float(p53 + delta) for x in BASE_SCORES])
        if out == truth:
            states[f"2**53+{delta}"] = "matches unshifted"
        elif len(set(out)) == 1:
            states[f"2**53+{delta}"] = "uniform"
        else:
            states[f"2**53+{delta}"] = "skewed: " + ",".join(fmt(out, 6))
    non_monotonic = len(set(states.values())) > 1
    claim(
        "C10",
        "The break is NOT monotonic, so the binary search I first used was invalid",
        non_monotonic,
        {"states": states,
         "consequence": "binary search requires a monotonic predicate; this one "
                        "alternates between uniform and skewed. Threshold in C6 "
                        "was found by an explicit scan instead."},
    )


def c12_temperature_is_gap_scaling() -> None:
    """
    The finding the video's ending rests on. Halving the temperature and
    doubling the gaps are not similar operations -- they are the same one.

    Consequence: softmax sees a list of GAPS, and there are exactly two things
    you can do to that list. Slide it (C3: nothing happens) or stretch it
    (this claim: that IS temperature). There is no third operation.

    This is what turns C7 from a coincidence into a prediction. If rounding
    widens the gaps by a factor of two, it has set the temperature to 0.5 --
    so C7's output MUST be the chapter's temperature 0.5 row, before we look.
    """
    half_temperature = probabilities([1.0, 2.0, 3.0], temperature=0.5)
    doubled_gaps = probabilities([1.0, 3.0, 5.0], temperature=1.0)

    # and the general form: scaling every gap by k == dividing temperature by k
    general = []
    for k in (2.0, 3.0, 0.5):
        scaled = [1.0 + k * (x - 1.0) for x in BASE_SCORES]   # stretch gaps by k
        general.append((k,
                        probabilities(scaled, temperature=1.0),
                        probabilities(BASE_SCORES, temperature=1.0 / k)))
    general_holds = all(a == b for _, a, b in general)

    claim(
        "C12",
        "Halving temperature IS doubling the gaps -- the same operation, bit-for-bit",
        half_temperature == doubled_gaps and general_holds,
        {
            "[1,2,3] at T=0.5": fmt(half_temperature, 12),
            "[1,3,5] at T=1.0": fmt(doubled_gaps, 12),
            "identical": half_temperature == doubled_gaps,
            "general_rule": {
                f"gaps x{k}": {"stretched_at_T=1": fmt(a, 10),
                               f"unstretched_at_T={1/k}": fmt(b, 10),
                               "identical": a == b}
                for k, a, b in general
            },
            "consequence": "C7 is not a coincidence. Rounding at 1e16 doubles the gaps, "
                           "which IS temperature 0.5, so the chapter's 0.5 row is the "
                           "predicted output -- not a surprising one.",
        },
    )


def c13_naive_version_also_underflows() -> None:
    """
    Secondary finding. Not in the video (off-concept) -- recorded for the README
    and the oral defence.

    Chapter line 164 justifies max-subtraction by avoiding "unnecessarily large
    intermediate exponentials" -- a worry about numbers getting too BIG. The
    opposite failure is not mentioned: when every score is very negative, every
    naive weight underflows to zero and the normalisation divides by zero.

    Honesty note: raw next-token logits sit around -10..+10, so this is not
    where it bites. Accumulated sequence log-probabilities of -800 are ordinary.
    The claim is "scores of this size occur in real softmax use", NOT "real
    next-token logits look like this".
    """
    scores = [-800.0, -801.0]
    naive_weights = [math.exp(x) for x in scores]        # no overflow: these underflow
    naive_total = sum(naive_weights)
    naive_fails = (naive_total == 0.0)
    ours = probabilities(scores)
    # gap of 1 between two outcomes -> logistic(1)
    expected = 1.0 / (1.0 + math.exp(-1.0))
    ours_correct = math.isclose(ours[0], expected, rel_tol=1e-12)
    claim(
        "C13",
        "Naive exp() also fails downward: at [-800,-801] every weight underflows to 0",
        naive_fails and ours_correct,
        {
            "naive_weights": naive_weights,
            "naive_total": naive_total,
            "naive_next_step": "division by zero" if naive_fails else "fine",
            "with_max_subtraction": fmt(ours, 10),
            "expected_for_a_gap_of_1": f"{expected:.10f}",
            "chapter_line_164_reason": "avoids 'unnecessarily large intermediate "
                                       "exponentials' -- overflow only; underflow unmentioned",
            "scope": "not raw next-token logits (those are ~-10..+10); this magnitude "
                     "occurs in accumulated sequence log-probabilities",
        },
    )


def c14_digits_run_out() -> None:
    """
    The on-screen demonstration in beat B06. A float64 carries about sixteen
    decimal digits. Just past 2**53 the last digit can no longer be recorded,
    so three consecutive integers cannot all be stored -- and the gaps between
    them silently double.

    This is C6 made visible with real digits, for the beat that explains WHY
    rounding changes a gap.
    """
    wanted = [9007199254740993, 9007199254740994, 9007199254740995]
    stored = [int(float(x)) for x in wanted]
    wanted_gaps = [wanted[1] - wanted[0], wanted[2] - wanted[1]]
    stored_gaps = [stored[1] - stored[0], stored[2] - stored[1]]
    claim(
        "C14",
        "Just past 2**53 the last digit is unrecordable: gaps 1,1 are stored as 2,2",
        wanted_gaps == [1, 1] and stored_gaps == [2, 2] and stored[0] != wanted[0],
        {
            "significant_decimal_digits": sys.float_info.dig,
            "digits_in_2**53": len(str(2 ** 53)),
            "wanted": wanted,
            "stored": stored,
            "wanted_gaps": wanted_gaps,
            "stored_gaps": stored_gaps,
            "note": "9007199254740993 cannot be represented and becomes ...992; "
                    "9007199254740995 becomes ...996. The middle value is exact.",
        },
    )


def c11_why_max_subtraction_exists() -> None:
    """The practical reason the shift is in the code at all: the naive form overflows."""
    evidence, behaved = {}, True
    for scores in ([1.0, 2.0, 3.0], [700.0, 701.0, 702.0], [1000.0, 1001.0, 1002.0]):
        key = str([int(s) for s in scores])
        try:
            naive_weights = [math.exp(x) for x in scores]
            naive_total = sum(naive_weights)
            naive_out = fmt([w / naive_total for w in naive_weights], 6)
        except OverflowError as exc:
            naive_out = f"OverflowError: {exc}"
        ours = fmt(probabilities(scores), 6)
        evidence[key] = {"naive_exp_without_shift": naive_out, "with_max_subtraction": ours}
    overflowed = "OverflowError" in str(evidence["[1000, 1001, 1002]"]["naive_exp_without_shift"])
    survived = evidence["[1000, 1001, 1002]"]["with_max_subtraction"] == fmt(
        probabilities(BASE_SCORES), 6)
    claim(
        "C11",
        "Without max-subtraction exp() overflows at [1000,1001,1002]; with it, the answer is fine",
        overflowed and survived and behaved,
        evidence,
    )


# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", metavar="PATH", help="also write a JSON record here")
    args = parser.parse_args()

    environment = {
        "run_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python_version": platform.python_version(),
        "python_build": " ".join(platform.python_build()),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "float_info_dig": sys.float_info.dig,
        "float_info_mant_dig": sys.float_info.mant_dig,
    }

    print("=" * 78)
    print("VERIFICATION — Week 01 video, 'the last step keeps only the gaps'")
    print("=" * 78)
    for key, value in environment.items():
        print(f"  {key}: {value}")
    print()
    print("Constructed input:", BASE_SCORES,
          "\n  (chosen by hand — chapter line 134: 'no model produced them')")
    print("=" * 78)
    print()

    for check in (
        c1_reproduce_chapter_probabilities,
        c2_reproduce_chapter_counts,
        c3_shift_invariance_holds,
        c4_negative_control,
        c5_ratio_depends_only_on_difference,
        c6_exact_breaking_threshold,
        c7_failure_mode_invented_confidence,
        c8_failure_mode_invented_ignorance,
        c9_the_test_still_passes,
        c10_my_own_assumption_was_wrong,
        c11_why_max_subtraction_exists,
        c12_temperature_is_gap_scaling,
        c13_naive_version_also_underflows,
        c14_digits_run_out,
    ):
        check()

    passed = sum(1 for c in CLAIMS if c["passed"])
    print("=" * 78)
    print(f"SUMMARY: {passed}/{len(CLAIMS)} claims verified on Python "
          f"{environment['python_version']}")
    for c in CLAIMS:
        if not c["passed"]:
            print(f"  NOT VERIFIED: {c['id']} — {c['statement']}")
    print("=" * 78)

    if args.json:
        record = {"environment": environment,
                  "constructed_input": BASE_SCORES,
                  "claims": CLAIMS}
        with open(args.json, "w") as handle:
            json.dump(record, handle, indent=2)
            handle.write("\n")
        print(f"\nJSON record written to {args.json}")

    return 0 if passed == len(CLAIMS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
