#!/usr/bin/env python3
"""
run_evidence.py — every number shown in the video comes from here.

It imports the UNMODIFIED course reference implementation
(lessons/01-randomness-and-first-prompts/code/main.py) and writes
evidence.json. scenes.py reads that file; no figure in the reel is typed
by hand. Re-run it and the numbers either reproduce or the build is wrong.

It also cross-checks the result under a SECOND interpreter (--compare),
because the float64 boundary this reel names turns out to depend on which
CPython you run: sum() switched to compensated (Neumaier) summation in 3.12,
which moves the naive path by one unit in the last place.

Usage:
    python3 evidence/run_evidence.py \
        --course /path/to/info-7375-prompt-engineering-for-generative-ai \
        --compare /path/to/another/python3
"""
import argparse
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOGITS = [1, 2, 3]
SEED = 7
COUNT = 1000


def load_main(course_root: Path):
    code_dir = course_root / "lessons" / "01-randomness-and-first-prompts" / "code"
    if not (code_dir / "main.py").is_file():
        sys.exit(f"main.py not found under {code_dir}")
    sys.path.insert(0, str(code_dir))
    import main  # noqa: E402  (the course reference implementation, unmodified)
    return main, code_dir


def git_commit(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def neumaier_probe() -> dict:
    """Behavioural test for compensated summation in sum(). 2.0 => compensated."""
    value = sum([1e100, 1.0, -1e100, 1.0])
    return {"expression": "sum([1e100, 1.0, -1e100, 1.0])",
            "value": value,
            "compensated": value == 2.0}


def run_under(exe: Path, course: Path) -> dict:
    """Re-run THIS script under another interpreter and read back its JSON."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "cross.json"
        proc = subprocess.run(
            [str(exe), str(Path(__file__).resolve()),
             "--course", str(course), "--out", str(out)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            return {"error": proc.stderr.strip()[-400:]}
        data = json.loads(out.read_text())
    return {
        "python": data["provenance"]["python"],
        "naive_sum": data["naive"]["sum"],
        "naive_probs": data["naive"]["probs"],
        "shifted_probs": data["shifted"]["probs"],
        "identical_bitwise": data["identical_bitwise"],
        "ulp_difference": data["ulp_difference"],
        "prob_sums": data["prob_sums"],
        "neumaier_probe": data["neumaier_probe"],
    }


def main_():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", required=True, type=Path,
                    help="clone root of info-7375-prompt-engineering-for-generative-ai")
    ap.add_argument("--compare", type=Path, default=None,
                    help="a second python3 to cross-check the float64 boundary against")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).with_name("evidence.json"))
    args = ap.parse_args()

    course_root = args.course.expanduser().resolve()
    main, code_dir = load_main(course_root)

    # ---- the reference result (what main.py prints) -----------------------
    demo = main.demo()

    # ---- the two paths, computed side by side -----------------------------
    peak = max(LOGITS)

    naive_weights = [math.exp(x) for x in LOGITS]
    naive_sum = sum(naive_weights)
    naive_probs = [w / naive_sum for w in naive_weights]

    shifted_weights = [math.exp(x - peak) for x in LOGITS]
    shifted_sum = sum(shifted_weights)
    shifted_probs = [w / shifted_sum for w in shifted_weights]

    # main.py's own output must equal the shifted path exactly
    ref_probs = main.probabilities(LOGITS)
    assert ref_probs == shifted_probs, "shifted path does not match main.py"

    ratios = [n / s for n, s in zip(naive_weights, shifted_weights)]

    # ---- the float64 boundary: are the two paths bit-identical? -----------
    ulps = []
    for a, b in zip(naive_probs, shifted_probs):
        ulps.append(0 if a == b else round((b - a) / math.ulp(a)))

    # ---- the overflow the shift prevents ----------------------------------
    try:
        math.exp(1000)
        overflow = {"raised": False, "error": None}
    except OverflowError as exc:
        overflow = {"raised": True, "error": f"OverflowError: {exc}"}

    # ---- expected vs observed counts --------------------------------------
    counts = {int(k): v for k, v in demo["counts"].items()}
    expected = [p * COUNT for p in shifted_probs]

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "provenance": {
            "course_repo": "https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai",
            "course_commit": git_commit(course_root),
            "source_file": str(
                (code_dir / "main.py").relative_to(course_root)),
            "source_modified": False,
            "python": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}",
        },
        "inputs": {"logits": LOGITS, "temperature": 1.0,
                   "seed": SEED, "count": COUNT, "peak": peak},
        "naive": {
            "weights": naive_weights,
            "sum": naive_sum,
            "probs": naive_probs,
        },
        "shifted": {
            "weights": shifted_weights,
            "sum": shifted_sum,
            "probs": shifted_probs,
        },
        "ratios": ratios,
        "e_to_the_peak": math.exp(peak),
        "identical_bitwise": naive_probs == shifted_probs,
        "ulp_difference": ulps,
        "prob_sums": {"naive": sum(naive_probs), "shifted": sum(shifted_probs)},
        "overflow_demo": {
            "naive_exp_1000": overflow,
            "shifted_probabilities_1000_1000": main.probabilities([1000, 1000]),
        },
        "sampling": {
            "counts": counts,
            "expected": expected,
        },
        "reference_demo_output": demo,
        "neumaier_probe": neumaier_probe(),
    }

    if args.compare:
        payload["crosscheck"] = run_under(args.compare.expanduser().resolve(),
                                          course_root)

    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {args.out}")
    print(f"  course commit : {payload['provenance']['course_commit']}")
    print(f"  bit-identical : {payload['identical_bitwise']}")
    print(f"  ULP diff      : {ulps}")
    print(f"  prob sums     : {payload['prob_sums']}")
    print(f"  sum() compensated: {payload['neumaier_probe']['compensated']}")
    if "crosscheck" in payload:
        c = payload["crosscheck"]
        print(f"  crosscheck    : python {c.get('python')} "
              f"ULP {c.get('ulp_difference')} "
              f"compensated={c.get('neumaier_probe', {}).get('compensated')}")


if __name__ == "__main__":
    main_()
