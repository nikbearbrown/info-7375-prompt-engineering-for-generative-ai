"""Mutation check: put each CONTRACT.md wrong version into the code, one at a time, and confirm that its own test fails.
A wrong version whose test still passes is reported MISSED. Run: python tests/mutants.py"""
from __future__ import annotations

import contextlib
import json
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_wrong_versions as t  # noqa: E402
from harness import CFG  # noqa: E402

from agent import claude_judge, fetch, labels, lines, persona, rule, state, textprep  # noqa: E402
from experiments import runner  # noqa: E402


@contextlib.contextmanager
def patched(*triples):
    saved = [(obj, name, getattr(obj, name)) for obj, name, _ in triples]
    for obj, name, value in triples:
        setattr(obj, name, value)
    try:
        yield
    finally:
        for obj, name, value in saved:
            setattr(obj, name, value)


@contextlib.contextmanager
def vocab_with(**extra):
    CFG.vocab.update(extra)
    try:
        yield
    finally:
        for k in extra:
            CFG.vocab.pop(k)


def wrap(obj, name, fn):
    real = getattr(obj, name)
    return obj, name, (lambda *a, **k: fn(real, *a, **k))


def _no_seniority(real, title, sentences, persona_):
    return {**real(title, sentences, persona_), "passed": True, "seniority_token": None}


def _whole_title(real, title, persona_):
    kw = next((k for k in persona_["target_title_keywords"] if title.lower() == k), None)
    return {"passed": kw is not None, "matched_keyword": kw, "exclusion_hit": None}


def _no_exclusions(real, title, persona_):
    out = real(title, persona_)
    return {**out, "passed": out["matched_keyword"] is not None, "exclusion_hit": None}


def _exact_city(real, location, persona_):
    seg = location.lower()
    return {"passed": seg in persona_["preferred_cities"], "matched": seg if seg in persona_["preferred_cities"] else None}


def _bare_us(real, location, persona_):
    out = real(location, persona_)
    return out if out["passed"] else ({"passed": True, "matched": "united states"}
                                      if "united states" in location.lower() else out)


def _matched_all(real, sentences, persona_, vocab):
    out = real(sentences, persona_, vocab)
    return {**out, "matched": out["posting_skills"], "matched_count": len(out["posting_skills"])}


def _any_check(real, posting, sentences, persona_, vocab):
    out = real(posting, sentences, persona_, vocab)
    out["rule_verdict"] = "relevant" if any(c["passed"] for c in out["rule_checks"].values()) else "not_relevant"
    return out


def _off_by_one():
    prev = {"title": None}

    def build(real, run, cfg, posting, rule_out, claude_out):
        line = real(run, cfg, posting, rule_out, claude_out)
        line["posting_title"], prev["title"] = prev["title"] or posting["title"], posting["title"]
        return line
    return build


def _lax_validator(real, stdout):
    try:
        obj = json.loads(json.loads(stdout.decode("utf-8"))["result"])
        return (obj, None) if isinstance(obj, dict) and "verdict" in obj else (None, "x")
    except Exception:
        return None, "x"


def _repairing_validator(real, stdout):
    try:
        env = json.loads(stdout.decode("utf-8"))
        text = env["result"]
        text = text[text.index("{"):text.rindex("}") + 1]
        obj = json.loads(text)
        obj = {k: obj[k] for k in claude_judge.KEYS}
        obj["verdict"] = obj["verdict"].lower()
        env["result"] = json.dumps(obj)
        return real(json.dumps(env).encode())
    except Exception:
        return real(stdout)


def _fill_in(real, *a, **k):
    out, failure = real(*a, **k)
    if failure:
        out.update(claude_status="ok", claude_verdict="not_relevant", claude_justification="filled in",
                   claude_cited_resume_fields=["skills"], claude_cited_posting_fields=["content"])
    return out, None


def _claude_overwrites(real, run, cfg, posting, rule_out, claude_out):
    line = real(run, cfg, posting, rule_out, claude_out)
    if line["claude_verdict"]:
        line["rule_verdict"] = line["claude_verdict"]
    return line


def _repo_cwd_run(real, argv, prompt, timeout=300.0):
    import shutil
    import subprocess
    proc = subprocess.run([shutil.which(argv[0]), *argv[1:]], input=prompt.encode("utf-8"), capture_output=True,
                          cwd=Path(__file__).resolve().parent.parent)
    return proc.stdout, None


def _cp1252_run(real, argv, prompt, timeout=300.0):
    import shutil
    import subprocess
    with __import__("tempfile").TemporaryDirectory() as tmp:
        proc = subprocess.run([shutil.which(argv[0]), *argv[1:]], input=prompt.encode("cp1252", "replace"),
                              capture_output=True, cwd=tmp)
    return proc.stdout, None


def _forget_new_ids():
    first = {}

    def save(real, path, st):
        if st.get("baseline_run_id") and path not in first and all(r.get("completed_at") for r in st["runs"]):
            first[path] = list(st["seen_ids"])
        if path in first:
            st = {**st, "seen_ids": first[path]}
        return real(path, st)
    return save


def _drop_errors(*phrases):
    def check(real, *a, **k):
        return [e for e in real(*a, **k) if not any(p in e for p in phrases)]
    return check


def _never_empty(real, *a, **k):
    return real(*a, **k) or ["(empty)"]


def _drop_persona(*phrases):
    def problems(real, *a, **k):
        return [e for e in real(*a, **k) if not any(p in e for p in phrases)]
    return problems


def _reads_state(real, root):
    (root / "state" / "sentinel.json").read_text()
    return real(root)


class _Unseeded(random.Random):
    def __init__(self, seed=None):
        super().__init__(os.urandom(16))


MUTANTS = {
    1: lambda: patched(wrap(rule, "seniority_check", _no_seniority)),
    2: lambda: patched((rule, "SENIORITY_RE", re.compile(r"\b(senior|sr|staff|principal|lead|manager|director|head|vp)\s"))),
    3: lambda: patched((rule, "whole_word", lambda term: re.compile(re.escape(term)))),
    4: lambda: patched(wrap(rule, "title_check", _whole_title)),
    5: lambda: patched(wrap(rule, "title_check", _no_exclusions)),
    6: lambda: patched(wrap(rule, "location_check", _exact_city)),
    7: lambda: patched((rule, "REMOTE_REGION_RE", re.compile(r"us|usa|united states|north america"))),
    8: lambda: patched(wrap(rule, "location_check", _bare_us)),
    9: [lambda: patched((rule, "EXPERIENCE_RE", re.compile(""))),
        lambda: patched((rule, "YEARS_RE", re.compile(
            r"(?<!\d)(?:\d{1,2}\s*(?:-|–|to)\s*)?(\d{1,2})\+?\s*years?(?![a-z0-9])")))],
    10: lambda: patched((rule, "YEARS_RE", re.compile(r"(\d{1,2})\s*(?:\+|(?:-|–|to)\s*\d{1,2}\+?)?\s*years?(?![a-z0-9])"))),
    11: lambda: patched((rule, "DEGREE_RE", re.compile(r"(?!x)x"))),
    12: lambda: patched((textprep, "normalize_quotes", lambda s: s)),
    13: lambda: patched((textprep, "BLOCK_TAGS", textprep.BLOCK_TAGS - {"li"})),
    14: lambda: patched((textprep, "TRAILING", "")),
    15: lambda: patched(wrap(textprep, "requirements_sentences", lambda real, c, cut, drop: real(c, cut, ()))),
    16: lambda: vocab_with(r=["r"], databricks=["databricks"]),
    17: lambda: patched(wrap(rule, "skill_check", _matched_all)),
    18: lambda: patched(wrap(rule, "judge", _any_check)),
    19: lambda: patched(wrap(lines, "build", _off_by_one())),
    20: lambda: patched(wrap(claude_judge, "validate_output", _lax_validator)),
    21: lambda: patched(wrap(claude_judge, "validate_output", _repairing_validator)),
    22: lambda: patched(wrap(claude_judge, "judge", _fill_in)),
    23: lambda: patched(wrap(lines, "build", _claude_overwrites)),
    24: lambda: patched(wrap(claude_judge, "run_claude", _repo_cwd_run)),
    25: lambda: patched(wrap(claude_judge, "run_claude", _cp1252_run)),
    26: lambda: patched((state, "is_baseline", lambda st: False)),
    27: lambda: patched(wrap(state, "save", _forget_new_ids())),
    28: lambda: patched((lines, "completed_by_mode", lambda root: {"live": _AllRuns(), "seeded": _AllRuns()})),
    29: lambda: patched((state, "path_for", lambda root, mode: root / "state" / "state.json")),
    30: lambda: patched(wrap(lines, "check", _drop_errors("claude_raw_paths", "byte-for-byte"))),
    31: lambda: patched((fetch, "check_allowed", lambda url: None),
                        (fetch, "_NoRedirect", type("Follow", (fetch.urllib.request.HTTPRedirectHandler,), {}))),
    32: lambda: patched(wrap(textprep, "requirements_sentences", _never_empty)),
    33: lambda: patched(wrap(persona, "problems", _drop_persona("email", "phone"))),
    34: lambda: patched(wrap(persona, "problems", _drop_persona("skill not in", "missing field", "extra field"))),
    35: lambda: patched((labels.random, "Random", _Unseeded)),
    36: lambda: patched(wrap(runner, "load_board", _reads_state)),
}


class _AllRuns(set):
    def __contains__(self, item):
        return True


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    missed, total = [], 0
    for n, mutants in MUTANTS.items():
        test = getattr(t, f"test_wv_{n:02d}")
        for k, mutant in enumerate(mutants if isinstance(mutants, list) else [mutants]):
            total += 1
            tag = f"wv{n:02d}{'abc'[k] if isinstance(mutants, list) else ''}"
            try:
                with mutant():
                    test()
                missed.append(tag)
                print(f"MISSED {tag}: the test still passed with the wrong version in place")
            except Exception as e:
                print(f"caught {tag}: {type(e).__name__}: {str(e).splitlines()[0][:90] if str(e) else ''}")
    print(f"{total - len(missed)}/{total} wrong-version mutants caught by their own test")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
