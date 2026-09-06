# INFO 7375: Evaluation and human approval gates
# Companion: lessons/13-evaluation-and-approval-gates/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import hashlib
import json

FIELDS = ("action","target","reason","effects","evidence","rollback")

def fingerprint(proposal):
    if not isinstance(proposal, dict) or any(not proposal.get(k) for k in FIELDS):
        raise ValueError("Six meaningful gate fields required")
    return hashlib.sha256(json.dumps(proposal, sort_keys=True, separators=(",",":")).encode()).hexdigest()

def approved(proposal, decision):
    return (isinstance(decision, dict) and decision.get("approved") is True
            and isinstance(decision.get("approver"), str) and bool(decision["approver"].strip())
            and decision.get("fingerprint") == fingerprint(proposal))

def demo():
    proposal = dict(zip(FIELDS, ["write","report.md","deliver draft","one local file",
                                "source checks passed","restore previous file"]))
    return {"proposal":proposal,"fingerprint":fingerprint(proposal),
            "status":"awaiting human decision"}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
