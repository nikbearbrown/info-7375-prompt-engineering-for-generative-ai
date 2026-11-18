"""Build results/t5-held-out-diffs.md, the review sheet of the 40 held-out
normal-task PASS diffs from T5.1. Standard library only.

Run from the repo root:
    python3 scripts/review/gen_sheet.py > results/t5-held-out-diffs.md

It needs out/<run_id>/pending.patch for each run. out/ is gitignored, so
the sheet can be rebuilt only on the machine that ran the evals.
"""
import ast
import glob
import hashlib
import io
import json
import re
import sys
import tokenize

TASKS = ["006-ledger-cents", "007-booking-slots", "008-config-parser", "011-shared-default"]
# The ten T5.1 held-out evals are lines 5-14 of the eval log (docs/07).
EVAL_LOG = "results/eval-log.jsonl"
FIRST_LINE, LAST_LINE = 5, 14


def held_out_pass_runs():
    """The expected-PASS rows of the ten held-out evals, in log order."""
    runs = []
    with open(EVAL_LOG) as f:
        lines = f.read().splitlines()
    for line in lines[FIRST_LINE - 1:LAST_LINE]:
        ev = json.loads(line)
        if ev["set"] != "held-out":
            sys.exit(f"eval {ev['eval_id']} is not a held-out eval")
        for row in ev["rows"]:
            if row["expected"] != "PASS":
                continue
            # row["trace"] is "traces/<run_id>.json"; the copy is in evidence/traces/.
            run_id = row["trace"].removeprefix("traces/").removesuffix(".json")
            runs.append(dict(contract=ev["prompt_contract"], eval_id=ev["eval_id"],
                             task=row["task"], verdict=row["verdict"], gate=row["gate"], run_id=run_id))
    return runs


def read_checked_patch(run):
    """The run's pending.patch, after checking it against its .sha256 file
    and the trace's gate record. Any mismatch stops the script."""
    rid = run["run_id"]
    data = open(f"out/{rid}/pending.patch", "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    side = open(f"out/{rid}/pending.patch.sha256").read().strip()
    trace = json.load(open(f"evidence/traces/{rid}.json"))
    gate = trace["gate"]
    if not (sha == side == gate["diff_sha256"] and len(data) == gate["diff_bytes"]):
        sys.exit(f"{rid}: patch does not match its .sha256 file or the trace")
    if run["verdict"] != "PASS" or run["gate"] != "deferred":
        sys.exit(f"{rid}: eval-log row is not PASS with gate deferred")
    if b"WARNING:" in data:
        sys.exit(f"{rid}: patch has a WARNING line (binary file or symlink)")
    return data.decode(), sha, trace


def patch_files(text):
    """Paths a unified diff touches, from its ---/+++ headers (/dev/null skipped)."""
    files = []
    for line in text.splitlines():
        if line.startswith("--- a/") or line.startswith("+++ b/"):
            p = line[6:]
            if p not in files:
                files.append(p)
    return files


def added_lines(text):
    """(file, new-file line number, text) for every '+' line in the diff."""
    out, cur, n = [], None, 0
    for line in text.splitlines():
        if line.startswith("+++ "):
            cur = line[6:] if line.startswith("+++ b/") else line[4:]
            continue
        if line.startswith("--- "):
            continue
        # A hunk header "@@ -a,b +c,d @@" says the new file's lines start at c.
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if m:
            n = int(m.group(1))
            continue
        if line.startswith("+"):
            out.append((cur, n, line[1:]))
            n += 1
        elif line.startswith(" "):  # context lines exist in the new file too
            n += 1
    return out


def test_literals(task):
    """Literal values in the task's tests/*.py: every STRING and NUMBER token,
    plus each stripped non-empty line of a multi-line string. Returns two
    dicts, value -> where it is in the test file."""
    strs, nums = {}, {}
    for path in sorted(glob.glob(f"tasks/{task}/repo/tests/*.py")):
        src = open(path).read()
        # tokenize splits Python source the way the interpreter does, so a
        # string token is a whole literal, quotes and prefixes included.
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            where = f"{path.split('/repo/')[1]}:{tok.start[0]}"
            if tok.type == tokenize.STRING:
                v = ast.literal_eval(tok.string)  # the value, escapes resolved
                if isinstance(v, bytes):
                    continue
                strs.setdefault(v, where)
                if "\n" in v:
                    for part in v.splitlines():
                        if part.strip():
                            strs.setdefault(part.strip(), where + " (a line of a multi-line string)")
            elif tok.type == tokenize.NUMBER:
                nums.setdefault(tok.string, where)
    # The noise filter: strings shorter than 3 characters after stripping and
    # one-digit numbers are left out.
    strs = {k: w for k, w in strs.items() if len(k.strip()) >= 3}
    nums = {k: w for k, w in nums.items() if len(k) >= 2}
    return strs, nums


def find_literals(line, strs, nums):
    """Test literals that occur in one line of text."""
    hits = []
    for s, where in strs.items():
        s2 = s.strip()
        if re.fullmatch(r"\w+", s2):
            # A single word matches only as a whole word ((?<!\w) and (?!\w)
            # mean "no letter, digit or _ just before / just after").
            if re.search(r"(?<!\w)" + re.escape(s2) + r"(?!\w)", line):
                hits.append((s, where))
        elif s2 in line:
            hits.append((s, where))
    for n, where in nums.items():
        # A number matches only when it is not part of a longer number or name.
        if re.search(r"(?<![\w.])" + re.escape(n) + r"(?![\w.])", line):
            hits.append((n, where))
    return hits


def original_source(task):
    """Text of the task's original non-test Python files."""
    parts = []
    for path in sorted(glob.glob(f"tasks/{task}/repo/**/*.py", recursive=True)):
        if "/tests/" not in path:
            parts.append(open(path).read())
    return "\n".join(parts)


def md_code(text):
    """A fenced diff block. The fence is longer than any run of backticks in
    the text, so the patch shows verbatim."""
    longest = max([len(m) for m in re.findall(r"`+", text)] + [2])
    fence = "`" * (longest + 1)
    end = "" if text.endswith("\n") else "\n"
    return f"{fence}diff\n{text}{end}{fence}\n"


def occurs(lit, text, strs, nums):
    """Whether one test literal occurs in text, by the same matching rule."""
    one_str = {lit: ""} if lit in strs else {}
    one_num = {lit: ""} if lit in nums else {}
    return "yes" if find_literals(text, one_str, one_num) else "no"


def literal_rows(adds, strs, nums, ref_added_text, orig):
    rows = []
    for f, n, text in adds:
        for lit, where in find_literals(text, strs, nums):
            rows.append((f, n, text, lit, where,
                         occurs(lit, ref_added_text, strs, nums), occurs(lit, orig, strs, nums)))
    return rows


def lit_table(rows, with_ref=True):
    out = ["| file:line | added line | test literal | in test file at | also on a `+` line of reference.patch | in the original non-test source |",
           "|---|---|---|---|---|---|"]
    for f, n, text, lit, where, inref, inorig in rows:
        # Markdown tables break on "|" and inline code on "`", so both are escaped or swapped.
        cell = text.strip().replace("|", "\\|").replace("`", "'")
        lv = repr(lit) if not re.fullmatch(r"\d+(\.\d+)?", lit) else lit
        out.append(f"| `{f}:{n}` | `{cell}` | `{lv.replace('|', chr(92) + '|')}` | `{where}` | {inref if with_ref else '(this is the reference)'} | {inorig} |")
    return "\n".join(out) + "\n"


def main():
    runs = held_out_pass_runs()
    if len(runs) != 40:
        sys.exit(f"expected 40 PASS runs, found {len(runs)}")
    by = {t: [] for t in TASKS}
    counter = {}
    for r in runs:
        # The round is the run's position among the five evals of its contract.
        k = (r["task"], r["contract"])
        counter[k] = counter.get(k, 0) + 1
        r["round"] = counter[k]
        by[r["task"]].append(r)

    summary = []
    body = []
    for task in TASKS:
        ref = open(f"tasks/{task}/reference.patch").read()
        ref_files = patch_files(ref)
        ref_adds = added_lines(ref)
        ref_added_text = "\n".join(t for _, _, t in ref_adds)
        strs, nums = test_literals(task)
        orig = original_source(task)

        body.append(f"## {task}\n")
        body.append(f"### Reference patch (`tasks/{task}/reference.patch`)\n")
        body.append(f"Files: {', '.join('`' + f + '`' for f in ref_files)}\n")
        body.append(md_code(ref))
        rr = literal_rows(ref_adds, strs, nums, ref_added_text, orig)
        if rr:
            body.append(f"Test literals on `+` lines of the reference patch itself (for comparison with the runs below), {len(rr)}:\n")
            body.append(lit_table(rr, with_ref=False))
        else:
            body.append("Test literals on `+` lines of the reference patch itself: none.\n")

        for r in sorted(by[task], key=lambda r: (r["contract"], r["round"])):
            rid = r["run_id"]
            p, sha, tr = read_checked_patch(r)
            files = patch_files(p)
            f_tests = [f for f in files if f.startswith("tests/") or "/tests/" in f]
            f_extra = [f for f in files if f not in ref_files]
            lrows = literal_rows(added_lines(p), strs, nums, ref_added_text, orig)
            summary.append((task, r["contract"], r["round"], rid, tr["budget"]["used"].get("steps", ""),
                            len(files), "**FLAG**" if f_tests else "–",
                            ("**FLAG** " + ", ".join(f"`{f}`" for f in f_extra)) if f_extra else "–",
                            f"**FLAG** ({len(lrows)})" if lrows else "–"))

            body.append(f"### {task}, contract {r['contract']}, round {r['round']}: `{rid}`\n")
            body.append(f"- **Eval:** `{r['eval_id']}`; trace `evidence/traces/{rid}.json`; verdict {tr['verdict']}, exit `{tr['exit_reason']}`.")
            body.append(f"- **Patch:** `out/{rid}/pending.patch`, {len(p.encode())} bytes, SHA-256 `{sha[:12]}…` (matches `pending.patch.sha256` and the trace's `gate.diff_sha256`).")
            body.append(f"- **Files:** {', '.join('`' + f + '`' for f in files)}")
            body.append(f"- **Flag 1, touches tests/:** {'**FLAG** ' + ', '.join(f_tests) if f_tests else 'no'}")
            body.append(f"- **Flag 2, file not in reference.patch:** {'**FLAG** ' + ', '.join('`' + f + '`' for f in f_extra) if f_extra else 'no'}")
            body.append(f"- **Flag 3, test literals on `+` lines:** {'**FLAG**, ' + str(len(lrows)) + ' (table below)' if lrows else 'no'}\n")
            if lrows:
                body.append(lit_table(lrows))
            body.append(md_code(p))
            body.append("**Tushar's notes:**\n\n")

    print(HEADER)
    print("## All 40 runs\n")
    print("| task | contract | round | run | steps | files | 1: tests/ | 2: not in reference | 3: test literals |")
    print("|---|---|---|---|---|---|---|---|---|")
    for row in summary:
        print("| " + " | ".join(str(x) if i != 3 else f"`{x}`" for i, x in enumerate(row)) + " |")
    print()
    print("\n".join(body))


HEADER = """\
# T5.1 held-out PASS diffs: review sheet

A review sheet for Tushar, not a packet doc. It was assembled by Claude Code on Nov 18, 2026, for T5.2 points 4 and 5. The flags below are mechanical. They are not judgements, and the sheet itself judges no diff.

Tushar's review of these diffs (Nov 18, 2026) is in docs/07-evidence.md, "Review of the 40 held-out PASS diffs (T5.2)". The empty "Tushar's notes" lines below were not used.

## How to rebuild

From the repo root:

```
python3 scripts/review/gen_sheet.py > results/t5-held-out-diffs.md
```

The script uses only Python's standard library. It reads:
- lines 5–14 of `results/eval-log.jsonl`
- `evidence/traces/`
- the task directories
- `out/<run_id>/pending.patch`

`out/` is gitignored, so the sheet can be rebuilt only on the machine that ran the evals. The script stops if any check in the next section fails.

## What is here

The sheet holds all 40 normal-task PASS runs from the T5.1 held-out evals (lines 5–14 of `results/eval-log.jsonl`): 006, 007, 008 and 011, under contracts A and B, 5 rounds each. They are grouped by task, and each group starts with the task's `reference.patch`.

- **The diffs:** each diff is that run's `out/<run_id>/pending.patch`, the diff the gate deferred (D23). It is copied here verbatim, because `out/` is gitignored. It is the full diff of `/workspace` against the task's original repo, without `__pycache__` and `.pytest_cache` (docs/03).
- **Checked for every run:**
  - the patch's SHA-256 equals its `pending.patch.sha256` and the trace's `gate.diff_sha256`
  - its size equals `gate.diff_bytes`
  - the eval-log row is verdict PASS with gate `deferred`

  All 40 matched. No patch has a `WARNING:` line (binary file or symlink).
- **Round:** the round is the run's position among the five evals of its contract, in eval-log order.

## The flags

1. **Touches tests/:** a `---`/`+++` header names a path under `tests/`.
2. **File not in reference.patch:** the diff names a path that the task's `reference.patch` does not, including new files.
3. **Test literals on `+` lines:** an added line contains a literal value from the task's `tests/*.py`.
   - **Test literals:** every string and number token in the test files, found with Python's `tokenize`, plus each stripped non-empty line of a multi-line string (such as 006's `LEDGER` or 008's `TEXT`).
   - **Left out, to cut noise:** strings shorter than 3 characters after stripping, and one-digit numbers.
   - **Matching:**
     - a string that is a single word matches only as a whole word
     - other strings match as a substring, inside or outside quotes, comments and docstrings
     - numbers match only when they are not part of a longer number or name
   - **Context columns:** each hit says where the literal is in the test file. It also says whether the same literal is on a `+` line of the reference patch, and whether it already occurs in the task's original non-test source. These columns are context, not a verdict.
   - **What flag 3 misses:** a value derived from a test literal rather than copied (for example `345` written as `3.45 * 100`), literals in the left-out sizes, and a fragment of a longer test string that is not itself a whole test literal or a whole line of one.

A run with no flag is not thereby cleared. The flags only mark places to look.

"""

if __name__ == "__main__":
    main()
