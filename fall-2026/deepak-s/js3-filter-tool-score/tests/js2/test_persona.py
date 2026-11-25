"""jobwatch/persona.py (the JS2 copy used by the loop) agrees with JS1's jobwatch/inputs.py.

Written by Claude Code (Claude Opus 5.5), 2026-11-10. JS1 inputs.py at b91c877 has no check_resume;
its entry point is load_resume(path), so the comparison is persona.check_resume(raw, schema) against
inputs.load_resume(path) on the same bytes. Tests may import inputs; the loop path may not (A-1).

Cases: the JS1 persona, plus every invalid-persona case the JS1 tests use:
  tests/spec/test_privacy.py LEAKS and NOT_FICTIONAL (loaded from that file, not retyped);
  tests/unit/test_inputs_and_prompt.py lines 50-56 (the shape changes) and lines 38-47 (a leak in
  /work/1/highlights/0), retyped below because they are inline in that file;
  plus a body that is not JSON.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from jobwatch import inputs, persona
from jobwatch.errors import Stop

TESTS = Path(__file__).resolve().parents[1]
ROOT = TESTS.parent
PERSONA_RAW = (ROOT / "examples" / "persona_resume.json").read_bytes()
SCHEMA = json.loads((ROOT / "schema" / "resume.schema.json").read_text(encoding="utf-8"))


def _load_js1_privacy_cases():
    spec = importlib.util.spec_from_file_location("js1_test_privacy", TESTS / "spec" / "test_privacy.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = {f"privacy_{k}": v[0] for k, v in mod.LEAKS.items()}
    cases.update({f"privacy_{k}": v for k, v in mod.NOT_FICTIONAL.items()})
    return cases


def _leak_in_highlight(d):
    d["work"][1]["highlights"][0] = "Contact " + "real" + "@" + "gmail.com"


SHAPE = {  # tests/unit/test_inputs_and_prompt.py lines 50-56
    "shape_role_no_word_chars": lambda d: d["targets"]["roles"].append("--"),
    "shape_location_no_word_chars": lambda d: d["targets"]["locations"].append("()"),
    "shape_roles_empty": lambda d: d["targets"].update(roles=[]),
    "shape_phone_missing": lambda d: d["basics"].pop("phone"),
    "shape_skills_string": lambda d: d.update(skills="Python"),
}
CASES = {"persona_unchanged": lambda d: None, **_load_js1_privacy_cases(), **SHAPE,
         "refusal_names_path_not_value": _leak_in_highlight}


def _outcome(fn):
    try:
        return ("ok", fn())
    except Stop as e:
        return ("stop", e.code, str(e))


@pytest.mark.parametrize("name", list(CASES) + ["not_json"])
def test_persona_agrees_with_js1_inputs(name, tmp_path):
    if name == "not_json":
        raw = b"{not json"
    else:
        data = json.loads(PERSONA_RAW)
        CASES[name](data)
        raw = PERSONA_RAW if name == "persona_unchanged" else json.dumps(data).encode("utf-8")
    p = tmp_path / "r.json"
    p.write_bytes(raw)
    js1 = _outcome(lambda: inputs.load_resume(p)[0])
    js2 = _outcome(lambda: persona.check_resume(raw, SCHEMA))
    assert js2 == js1
    assert (js1[0] == "ok") == (name == "persona_unchanged")


def test_persona_module_does_no_file_io():
    import ast

    tree = ast.parse((ROOT / "jobwatch" / "persona.py").read_text(encoding="utf-8"))
    names = {n.attr if isinstance(n, ast.Attribute) else n.id
             for n in ast.walk(tree) if isinstance(n, (ast.Attribute, ast.Name))}
    assert not names & {"open", "read_bytes", "read_text", "write_bytes", "write_text", "Path", "SCHEMA_PATH"}
