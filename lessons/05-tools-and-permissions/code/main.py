# INFO 7375: Tools, permissions, and boundaries
# Companion: lessons/05-tools-and-permissions/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
from pathlib import Path

def authorize(root, target, operation, approved=False):
    if operation not in {"read", "write"}:
        raise PermissionError("Operation is not allowed")
    base = Path(root).resolve()
    path = (base / target).resolve()
    if not path.is_relative_to(base):
        raise PermissionError("Path escapes the data boundary")
    if operation == "write" and approved is not True:
        raise PermissionError("Write requires human approval")
    return path

def demo():
    return {"read": str(authorize("/tmp/course", "notes.txt", "read")),
            "note": "Preflight illustration; no file is read or written"}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
