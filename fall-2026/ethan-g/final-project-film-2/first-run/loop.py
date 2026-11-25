"""The loop: Claude writes the checks, the scorer grades them, the clean-copy results go back, Claude revises.

  python loop.py                      # live: Claude Code in headless mode, on the logged-in subscription
  python loop.py --fixture DIR        # replay saved replies (round1*.md, round2*.md, ...) instead of calling Claude
  python loop.py --rounds 3 --model claude-opus-5-5 --effort high

Each round (observe, decide, act, record):
  1. act      ask Claude for one checks file (round 1: the contract in claude-checks/PROMPT-round1.md;
              later rounds: the clean-copy feedback, in the same conversation)
  2. check    the reply must hold exactly one python block, and that code must pass check_policy() before it runs
  3. act      run the scorer on the clean copy and on both plantings (seed 25, held-out seed 99)
  4. record   save the prompt, the raw reply, the code, the scores and the decision under loop-runs/<timestamp>/
  5. decide   stop on: the pass line (5 of 5 caught, 0 good rows flagged, 0 crashes, on both plantings);
              a refused or missing reply; a clean copy with nothing left to report; or the round budget

What Claude sees: the contract, then only the clean copy's results (which rules rejected good trips, which
rules crashed). It never sees the data, the plantings, the answer keys or the scores. Claude Code runs with
no tools (--tools "") in an empty folder, so it can only answer in text.
"""
import argparse, ast, datetime as dt, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = HERE / ".venv" / "bin" / "python"
SEEDS = (25, 99)
TYPES = ["negative_fare", "dropoff_before_pickup", "missing_value", "duplicate_rows", "wrong_type"]

# ───────────────────────── the pure parts (tested in tests/test_loop.py) ─────────────────────────

BLOCK = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S)


def extract_code(reply):
    """The one fenced code block in a reply, or None when there is none or more than one."""
    blocks = BLOCK.findall(reply or "")
    return blocks[0] if len(blocks) == 1 else None


ALLOWED_IMPORTS = {"pandas", "pandera", "pandera.pandas", "numpy", "re", "math", "datetime", "typing"}
FORBIDDEN_NAMES = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "globals", "locals",
                   "vars", "getattr", "setattr", "delattr", "exit", "quit"}
ALLOWED_TO = {"to_datetime", "to_numeric", "to_timedelta"}
FORBIDDEN_ATTRS = {"system", "popen", "remove", "unlink", "rmdir", "rename", "write", "writelines", "mkdir"}


def check_policy(code):
    """Violations that stop model-written code from being run ([] = allowed). The scorer imports this file,
    so anything that could read the plantings, write files, start processes or reach the network is refused."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"syntax error: {e.msg} (line {e.lineno})"]
    v = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name not in ALLOWED_IMPORTS:
                    v.append(f"import {a.name} is not allowed")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "") not in ALLOWED_IMPORTS:
                v.append(f"import {node.module} is not allowed")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            v.append(f"use of {node.id}() is not allowed")
        elif isinstance(node, ast.Attribute):
            a = node.attr
            if a.startswith("__") and a.endswith("__"):
                v.append(f"dunder attribute {a} is not allowed")
            elif a.startswith("read_") or (a.startswith("to_") and a not in ALLOWED_TO):
                v.append(f".{a}() (file input/output) is not allowed")
            elif a in FORBIDDEN_ATTRS:
                v.append(f".{a}() is not allowed")
    if not any(isinstance(n, (ast.Assign, ast.AnnAssign)) and any(isinstance(t, ast.Name) and t.id == "schema"
               for t in (n.targets if isinstance(n, ast.Assign) else [n.target])) for n in tree.body):
        v.append("no `schema` defined at the top level")
    return v


CLOSE = ("Revise your checks so they still protect against real data problems but no longer reject these normal "
         "trips. Keep the same contract as before: pandera 0.29 with `import pandera.pandas as pa`, one variable "
         "named `schema`, one-line comments above each rule, no hard-coded row numbers or dataset values, and return "
         "only the Python code in a single code block.")


def build_feedback(flags):
    """The next-round prompt, built only from the clean copy's results (explain_clean.py JSON)."""
    n, per, col = flags.get("distinct_rows", 0), flags.get("per_rule", []), flags.get("column_level", [])
    parts = []
    if n:
        parts.append(f"I ran your checks on a clean copy of the real table: 10,000 normal trips that are known to be "
                     f"good. Your checks rejected {n} of those normal trips. Here is how many normal trips each of "
                     f"your rules rejected:\n\n" +
                     "\n".join(f"- {r['check']}: {r['rows']} trip{'' if r['rows'] == 1 else 's'}" for r in per))
    if col:
        lead = ("Also, these" if n else "I ran your checks on a clean copy of the real table: 10,000 normal trips "
                "that are known to be good. These")
        parts.append(f"{lead} rules failed on the clean copy as a whole instead of returning a result:\n\n" +
                     "\n".join(f"- '{c['check']}' on {c['column']}: {c['failure']}" for c in col))
    return "\n\n".join(parts + [CLOSE]) + "\n"


def clean_ok(s):
    c = s["clean"]
    return not c["flagged_rows"] and not c["column_failures"] and not c["crashed_checks"] and not c["error"]


def passes(s25, s99):
    return all(s["types_caught"] == len(TYPES) and clean_ok(s) for s in (s25, s99))


def decide(rnd, max_rounds, s25, s99, flags):
    if passes(s25, s99):
        return True, "pass line met"
    if rnd >= max_rounds:
        return True, f"budget: {max_rounds} rounds used, pass line not met"
    if not flags.get("distinct_rows") and not flags.get("column_level"):
        return True, "clean copy passes, so clean-copy feedback has nothing left to report; pass line not met"
    return False, "continue: clean-copy feedback to give"


# ───────────────────────── the effects (model, scorer, records) ─────────────────────────

def find_claude():
    if os.environ.get("CLAUDE"):
        return os.environ["CLAUDE"]
    hit = shutil.which("claude")
    if hit:
        return hit
    exts = sorted(Path.home().glob(".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude"))
    if exts:
        return str(exts[-1])
    sys.exit("Claude Code not found: put `claude` on PATH or set CLAUDE=/path/to/claude")


def ask_claude(prompt, session, args, work):
    """One headless Claude Code call with no tools, in an empty folder. Returns (text, session_id, raw)."""
    cmd = [find_claude(), "-p", prompt, "--output-format", "json", "--model", args.model, "--effort", args.effort,
           "--tools", "", "--strict-mcp-config"]
    if session:
        cmd += ["--resume", session]
    p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=args.timeout)
    try:
        raw = json.loads(p.stdout)
    except json.JSONDecodeError:
        raw = {"is_error": True, "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:], "returncode": p.returncode}
    if raw.get("is_error") or p.returncode:
        return None, session, raw
    return raw.get("result", ""), raw.get("session_id", session), raw


def score(checks, rdir):
    """The independent check: score_checks.py on both plantings, explain_clean.py on the clean copy."""
    out = {}
    for seed, lab in zip(SEEDS, ("score", "score-heldout")):
        subprocess.run([str(PY), "score_checks.py", str(checks), lab, str(rdir), str(seed)], cwd=HERE,
                       capture_output=True, text=True, timeout=600)
        out[seed] = json.loads((rdir / f"{lab}.json").read_text())
    subprocess.run([str(PY), "explain_clean.py", str(checks), "clean", str(rdir)], cwd=HERE,
                   capture_output=True, text=True, timeout=600)
    out["flags"] = json.loads((rdir / "clean-clean-flags.json").read_text())
    return out


def line(s):
    c = s["clean"]
    clean = ("PASS" if clean_ok(s) else
             f"{c['flagged_rows']} good row{'' if c['flagged_rows'] == 1 else 's'} flagged" + (f", {len(c['crashed_checks'])} check(s) crash" if c["crashed_checks"] else ""))
    return f"clean copy: {clean} · caught {s['types_caught']} of 5 · " + \
        ", ".join(f"{t} {s['types'][t]['verdict']}" for t in TYPES if s["types"][t]["verdict"] != "CAUGHT")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per Claude call")
    ap.add_argument("--fixture", help="folder of saved replies to replay (round1*.md, round2*.md, …)")
    args = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run = HERE / "loop-runs" / (stamp + ("-fixture" if args.fixture else ""))
    work = run / "work"; work.mkdir(parents=True)          # Claude's empty working folder
    state = {"started": stamp, "mode": "fixture" if args.fixture else "live", "model": args.model,
             "effort": args.effort, "max_rounds": args.rounds, "rounds": [], "session_id": None}
    if not args.fixture:
        state["claude_cli"] = subprocess.run([find_claude(), "--version"], capture_output=True, text=True).stdout.strip()
    save = lambda: (run / "state.json").write_text(json.dumps(state, indent=1) + "\n")
    prompt = (HERE / "claude-checks" / "PROMPT-round1.md").read_text()
    fixtures = sorted(Path(args.fixture).glob("round*.md")) if args.fixture else []
    print(f"loop → {run.relative_to(HERE)}  ({state['mode']}, up to {args.rounds} rounds)")

    for rnd in range(1, args.rounds + 1):
        rdir = run / f"round{rnd}"; rdir.mkdir()
        (rdir / "prompt.md").write_text(prompt)
        t0 = time.time()
        if args.fixture:
            if rnd > len(fixtures):
                state["stop"] = f"fixture has no reply for round {rnd}"; break
            text, raw = fixtures[rnd - 1].read_text(), {"fixture": fixtures[rnd - 1].name}
        else:
            text, state["session_id"], raw = ask_claude(prompt, state["session_id"], args, work)
        (rdir / "reply.json").write_text(json.dumps(raw, indent=1) + "\n")
        rec = {"round": rnd, "seconds": round(time.time() - t0, 1)}
        state["rounds"].append(rec)
        if text is None:
            rec["outcome"] = "model call failed"; state["stop"] = "model call failed"; save(); break
        (rdir / "reply.md").write_text(text)
        code = extract_code(text)
        if code is None:
            rec["outcome"] = "refused: reply must hold exactly one python block"; state["stop"] = rec["outcome"]; save(); break
        (rdir / "checks.py").write_text(code)
        bad = check_policy(code)
        if bad:
            rec["outcome"] = "refused by policy"; rec["violations"] = bad
            state["stop"] = "policy refused the checks (not run): " + "; ".join(bad); save(); break
        s = score(rdir / "checks.py", rdir)
        stop, why = decide(rnd, args.rounds, s[25], s[99], s["flags"])
        rec.update({"seed25": line(s[25]), "seed99": line(s[99]), "passes": passes(s[25], s[99]), "decision": why})
        print(f"round {rnd}: {rec['seed25']}\n         held-out: {rec['seed99']}\n         → {why}")
        save()
        if stop:
            state["stop"] = why; break
        prompt = build_feedback(s["flags"])
    state["finished"] = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    save()
    print(f"stop: {state.get('stop')}\nsaved: {run.relative_to(HERE)}/state.json")


if __name__ == "__main__":
    main()
