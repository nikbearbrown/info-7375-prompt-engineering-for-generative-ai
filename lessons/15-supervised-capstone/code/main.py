# INFO 7375: Supervised agentic capstone
# Companion: lessons/15-supervised-capstone/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
from pathlib import Path

ARTIFACTS = ("brief","data-boundary","action-surface-map","plan","gates",
             "pre-mortem","evidence","artifact","audit-note","transfer-reflection")

def validate_packet(folder):
    root = Path(folder).resolve()
    issues = []
    for name in ARTIFACTS:
        path = root / (name + ".md")
        if not path.resolve().is_relative_to(root):
            issues.append(name + ": outside packet")
        elif not path.is_file():
            issues.append(name + ": missing")
        elif len(path.read_text(encoding="utf-8").strip()) < 40:
            issues.append(name + ": insufficient content")
    return {"structurally_complete":not issues,"issues":issues,
            "human_review":"Evidence, authority, and understanding must still be assessed"}

def demo():
    return {"required_artifacts":list(ARTIFACTS),"note":"Use validate_packet on your own submission"}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
