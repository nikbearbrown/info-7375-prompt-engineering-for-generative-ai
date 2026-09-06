# INFO 7375: Claude Code and evidence-based diff review
# Companion: lessons/06-claude-code-and-diff-review/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import difflib

def diff(before, after):
    return "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                        fromfile="before.py", tofile="after.py"))

def review(changed, allowed, checks_passed, approved):
    reasons = []
    if not changed:
        reasons.append("no changes")
    if set(changed) - set(allowed):
        reasons.append("out of scope")
    if checks_passed is not True:
        reasons.append("checks failed or absent")
    if approved is not True:
        reasons.append("human review required")
    return {"merge_ready": not reasons, "reasons": reasons}

def demo():
    return {"diff": diff("return x - 1\n", "return x + 1\n"),
            "review": review(["app.py"], ["app.py"], True, False)}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
