"""Evidence for the review decision: run the OLD validator (JS1 folder,
unchanged) and the NEW one (this folder, patched) on every saved real Claude
reply, and list every reply whose result changed.

    python3 -B review/revalidate.py
"""
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
JS1 = HERE.parent / "js1-contract-and-watch"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(path.parent.parent))
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod


old = load(JS1 / "agent/claude_judge.py", "old_judge")
new = load(HERE / "agent/claude_judge.py", "new_judge")
resume = json.loads((HERE / "persona/priya-nair.resume.json").read_text())


def numeric_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).isdigit():
                yield f"{path}.{k}"
            yield from numeric_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from numeric_keys(v, f"{path}[{i}]")


print("Résumé dict keys made only of digits (patch 7044eaf would misread them as indexes):",
      list(numeric_keys(resume)) or "none")

files = sorted((JS1 / "evidence").rglob("*.json"))
replies, changed = 0, []
for f in files:
    try:
        rec = json.loads(f.read_text())
    except ValueError:
        continue
    recs = rec if isinstance(rec, list) else [rec]
    for r in recs:
        if not isinstance(r, dict):
            continue
        text = r.get("raw_reply", r.get("raw_reply_as_pasted"))
        if not isinstance(text, str):
            continue
        pid = r.get("posting_id")
        if pid is None:
            # action-surface files: no saved id, so take the reply's own id.
            # This makes the id check pass trivially; only field paths are tested.
            try:
                pid = json.loads(text.strip()).get("posting_id")
            except (ValueError, AttributeError):
                continue
        replies += 1
        a, ea = old.validate(text, pid, resume)
        b, eb = new.validate(text, pid, resume)
        if (a is None) != (b is None) or ea != eb:
            changed.append((f.relative_to(JS1), pid,
                            "VALID" if a else "INVALID",
                            "VALID" if b else "INVALID", ea, eb))

print(f"Saved real Claude replies checked: {replies} (from {JS1.name}/evidence)")
print(f"Replies whose result changed: {len(changed)}")
for c in changed:
    print(f"  {c[0]}  posting {c[1]}: {c[2]} -> {c[3]}")
    print(f"      old errors: {c[4]}")
    print(f"      new errors: {c[5]}")
