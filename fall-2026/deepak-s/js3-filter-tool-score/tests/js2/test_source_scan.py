"""Source scans: GATE.md section 5 ("Never" table) and section 7 (verify independence), and the
Phase 2c rule that only jobwatch/tools.py touches the network or writes to disk.

Written by Claude Code (Claude Opus 5.5), 2026-11-10. AST-based. Scope as GATE.md states it:
"the package" means every .py file under jobwatch/; "the loop path" means loop, tools, policy,
providers, verify, loop_replay, persona and cli.

GATE.md Amendments A-1: the modules in LEGACY, imported unchanged from JS1 b91c877, are named as
legacy. They are not scanned for forbidden calls; every other module is scanned in full.
test_legacy_modules_are_byte_identical_to_b91c877 checks each is unchanged, and
test_loop_closure_excludes_legacy_modules checks none is reachable from the loop path.
"""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[2] / "jobwatch"
# GATE.md Amendments A-1, exactly as listed there.
LEGACY = ("fetch.py", "judge_cli.py", "experiment.py", "evidence.py", "labels.py", "inputs.py", "judge.py",
          "prompt.py", "replay.py", "run.py", "saved_run.py", "state.py")
# sha256 of each legacy module at b91c877, from `git show b91c877:<js1>/jobwatch/<m>` on 2026-11-10.
LEGACY_SHA256_B91C877 = {
    "fetch.py": "6854acc34ee5ff9eaeccd78556c9f8593656261148cd86a2f5022c894fff678b",
    "judge_cli.py": "2a138c6e083aa51d1bc5eaf20f7c6fa7cc71e97d49b0e7fe492d4cde3c1f643b",
    "experiment.py": "5d325469e6a9ed6301d40061e65e9989b96136a6d1dee1b95947c99c878d12dd",
    "evidence.py": "7e2ec454ba5bc865619102c3640abd38a157b01e472c0f356eba28c6841569ea",
    "labels.py": "7af4c09bffedc99bba5b19c585d19dfbb46c27886a469e18d63ebdac4ef96253",
    "inputs.py": "63207f33e617e966ec430f06bd4256d9f9d8f042e3daa453c89a35f780d0daf1",
    "judge.py": "5e296f6685427d9f578e1603ccf45b8e6eb3deed89715b8a14e02a24e91cc2f6",
    "prompt.py": "87e7adef6de88f955a34592047c4cb08c2993c9a7cde152ebe2ed3baea04ca34",
    "replay.py": "a3b676c858003269d826b60366d75c1b9b164155e43fd76f4a4141c1517f4335",
    "run.py": "0be5eda8bdb174d20b8999328f1145e27da2788535eb8bdf67e6c3d826b38429",
    "saved_run.py": "6f8ff89eb4e8fb9a79f3321711da82f0a24a69f8583963f05066c990a915fc9a",
    "state.py": "745f617f5289edfadd0a1fe91633453daad359dddc042302bfa118813d5d606d",
}
ALL = sorted(p for p in PKG.rglob("*.py"))
SCANNED = [p for p in ALL if not (p.parent == PKG and p.name in LEGACY)]
LOOP_ROOTS = ("jobwatch.loop", "jobwatch.tools", "jobwatch.policy", "jobwatch.providers", "jobwatch.providers.greenhouse",
              "jobwatch.providers.lever", "jobwatch.providers.ashby", "jobwatch.verify", "jobwatch.loop_replay")
LOOP_PATH = sorted([PKG / n for n in ("loop.py", "tools.py", "policy.py", "verify.py", "loop_replay.py", "persona.py",
                                      "cli.py")] + list((PKG / "providers").glob("*.py")))
JS1_JUDGE_MODULES = ("jobwatch.judge", "jobwatch.judge_cli", "jobwatch.backends", "jobwatch.prompt",
                     "jobwatch.sample", "jobwatch.experiment", "jobwatch.run", "jobwatch.replay")

NETWORK_MODULES = {"urllib.request", "http.client", "socket", "ssl", "requests", "urllib3", "httpx",
                   "smtplib", "ftplib", "telnetlib", "poplib", "imaplib", "subprocess"}
# Qualified calls (module.function) and Path-style methods (any receiver).
WRITE_QUALIFIED = {"os": {"replace", "rename", "renames", "makedirs", "mkdir", "symlink", "link", "fdopen", "truncate"},
                   "shutil": {"copy", "copy2", "copyfile", "copytree", "move"},
                   "tempfile": {"mkstemp", "mkdtemp", "NamedTemporaryFile", "TemporaryFile"}}
WRITE_METHODS = {"write_bytes", "write_text", "mkdir", "touch", "symlink_to", "hardlink_to", "rename", "mkstemp",
                 "fdopen", "atomic_write"}
DELETE_QUALIFIED = {"os": {"remove", "unlink", "rmdir", "removedirs"}, "shutil": {"rmtree"}}
DELETE_METHODS = {"unlink", "rmdir", "rmtree"}
READ_CALLS = {"read_bytes", "read_text"}


def rel(p):
    return p.relative_to(PKG.parent).as_posix()


def _calls(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
            yield node, name


def _receiver(node):
    f = node.func
    return f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None


def _matches(node, name, qualified, methods):
    recv = _receiver(node)
    if recv in qualified:
        return name in qualified[recv]
    return isinstance(node.func, ast.Attribute) and name in methods


def _imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module
            for a in node.names:
                yield f"{node.module}.{a.name}"


def _open_mode(node):
    mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
    return mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else None


def findings(path, kind):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    if kind == "network":
        out += [f"import {m}" for m in _imports(tree) if m in NETWORK_MODULES]
        out += [f"{n}()" for _, n in _calls(tree) if n in ("urlopen", "build_opener", "HTTPSConnection", "HTTPConnection")]
    elif kind == "write":
        for node, n in _calls(tree):
            if _matches(node, n, WRITE_QUALIFIED, WRITE_METHODS):
                out.append(f"{n}() line {node.lineno}")
            if n == "open" and isinstance(node.func, ast.Name):
                mode = _open_mode(node)
                if mode is None or set(mode) & set("wax+"):
                    out.append(f"open(..., {mode!r}) line {node.lineno}")
    elif kind == "delete":
        out += [f"{n}() line {node.lineno}" for node, n in _calls(tree) if _matches(node, n, DELETE_QUALIFIED, DELETE_METHODS)]
    elif kind == "read":
        for node, n in _calls(tree):
            if n in READ_CALLS or (n == "open" and isinstance(node.func, ast.Name)):
                out.append(f"{n}() line {node.lineno}")
    elif kind == "non_get":
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "method" and isinstance(node.value, ast.Constant) \
                    and str(node.value.value).upper() != "GET":
                out.append(f"method={node.value.value!r} line {node.value.lineno}")
        out += [f"import {m}" for m in _imports(tree) if m == "smtplib"]
    elif kind == "env":
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in ("environ", "getenv", "environb"):
                out.append(f"os.{node.attr} line {node.lineno}")
    return out


OUTSIDE_TOOLS = [p for p in SCANNED if p.name != "tools.py" or p.parent != PKG]


@pytest.mark.parametrize("path", OUTSIDE_TOOLS, ids=rel)
def test_no_network_call_outside_tools(path):
    assert findings(path, "network") == []


@pytest.mark.parametrize("path", OUTSIDE_TOOLS, ids=rel)
def test_no_file_write_call_outside_tools(path):
    assert findings(path, "write") == []


@pytest.mark.parametrize("path", SCANNED, ids=rel)
def test_no_delete_call_in_package(path):
    assert findings(path, "delete") == []


@pytest.mark.parametrize("path", [p for p in OUTSIDE_TOOLS if p.name != "verify.py"], ids=rel)
def test_no_file_read_outside_tools_and_verify(path):
    assert findings(path, "read") == []


def test_verify_reads_only_with_open_rb():
    tree = ast.parse((PKG / "verify.py").read_text(encoding="utf-8"))
    modes = [_open_mode(n) for n, name in _calls(tree) if name == "open" and isinstance(n.func, ast.Name)]
    assert modes == ["rb"]
    assert findings(PKG / "verify.py", "write") == [] and findings(PKG / "verify.py", "network") == []


@pytest.mark.parametrize("path", SCANNED, ids=rel)
def test_no_non_get_method_or_smtplib_in_package(path):
    assert findings(path, "non_get") == []


@pytest.mark.parametrize("path", LOOP_PATH, ids=rel)
def test_no_environment_read_in_loop_path(path):
    assert findings(path, "env") == []


def test_verify_imports_only_the_standard_library():
    tree = ast.parse((PKG / "verify.py").read_text(encoding="utf-8"))
    tops = {m.split(".")[0] for m in _imports(tree)}
    rel_imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level > 0]
    assert rel_imports == [] and "jobwatch" not in tops
    assert tops <= set(sys.stdlib_module_names), tops - set(sys.stdlib_module_names)


def test_loop_and_verify_never_import_the_judge():
    code = ("import sys, jobwatch.cli as c\n"
            "c._main_js2(['verify', 'runs/none'], None, None, None, None, None)\n"
            "import jobwatch.loop, jobwatch.loop_replay\n"
            f"bad = [m for m in {JS1_JUDGE_MODULES!r} if m in sys.modules]\n"
            "print(bad); sys.exit(1 if bad else 0)\n")
    r = subprocess.run([sys.executable, "-c", code], cwd=PKG.parent, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# --- GATE.md Amendments A-1 ----------------------------------------------------------------
def _module_file(name):
    p = PKG.parent / (name.replace(".", "/") + ".py")
    return p if p.exists() else PKG.parent / name.replace(".", "/") / "__init__.py"


def _jobwatch_imports(tree):
    for name in _imports(tree):
        if name.startswith("jobwatch"):
            yield name if _module_file(name).exists() else name.rsplit(".", 1)[0]


def static_loop_closure():
    """jobwatch modules reachable by import from the loop roots, plus the CLI's top-level imports and
    the imports inside its loop/verify/replay handler (cli._main_js2)."""
    cli = ast.parse((PKG / "cli.py").read_text(encoding="utf-8"))
    top = ast.Module(body=[n for n in cli.body if isinstance(n, (ast.Import, ast.ImportFrom))], type_ignores=[])
    handler = next(n for n in ast.walk(cli) if isinstance(n, ast.FunctionDef) and n.name == "_main_js2")
    todo = list(LOOP_ROOTS) + list(_jobwatch_imports(top)) + list(_jobwatch_imports(handler))
    seen = set()
    while todo:
        m = todo.pop()
        if m in seen or not _module_file(m).exists():
            continue
        seen.add(m)
        todo += list(_jobwatch_imports(ast.parse(_module_file(m).read_text(encoding="utf-8"))))
    return seen | {"jobwatch.cli"}


def test_loop_closure_excludes_legacy_modules():
    legacy = {f"jobwatch.{n[:-3]}" for n in LEGACY}
    static = static_loop_closure()
    assert "jobwatch.loop" in static and "jobwatch.persona" in static
    assert static & legacy == set(), sorted(static & legacy)
    code = ("import sys, jobwatch.cli as c\n"
            "c._main_js2(['verify', 'runs/none'], None, None, None, None, None)\n"
            f"import {', '.join(LOOP_ROOTS)}\n"
            f"bad = sorted(m for m in {sorted(legacy)!r} if m in sys.modules)\n"
            "print(bad); sys.exit(1 if bad else 0)\n")
    r = subprocess.run([sys.executable, "-c", code], cwd=PKG.parent, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_legacy_modules_are_byte_identical_to_b91c877():
    """Against the recorded b91c877 hashes; and, when this clone holds commit b91c877 (the personal
    repo does; a git archive or the class repo does not), against `git show b91c877:<path>` too."""
    import hashlib

    assert sorted(LEGACY_SHA256_B91C877) == sorted(LEGACY)
    for name in LEGACY:
        assert hashlib.sha256((PKG / name).read_bytes()).hexdigest() == LEGACY_SHA256_B91C877[name], name
    has_commit = subprocess.run(["git", "cat-file", "-e", "b91c877^{commit}"], cwd=PKG.parent,
                                capture_output=True).returncode == 0
    if has_commit:
        for name in LEGACY:
            js1 = subprocess.run(["git", "show", f"b91c877:fall2026/deepak-kumaran-ts/js1-contract-and-watch/jobwatch/{name}"],
                                 cwd=PKG.parent, capture_output=True)
            assert js1.returncode == 0 and js1.stdout == (PKG / name).read_bytes(), name
