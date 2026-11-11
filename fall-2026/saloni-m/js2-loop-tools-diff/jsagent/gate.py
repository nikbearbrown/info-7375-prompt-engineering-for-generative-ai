"""Read the budgets and hosts from GATE.md so the config cannot drift from the written decision."""
import re

BUDGET_LINE = re.compile(
    r"at most (\d+) boards, (\d+) HTTP requests, (\d+) seconds in total, (\d+) seconds per request")
HOSTS_LINE = re.compile(r"^- \*\*Hosts:\*\*(.*)$", re.M)


def read_gate(text):
    m = BUDGET_LINE.search(text)
    h = HOSTS_LINE.search(text)
    if not m or not h:
        raise ValueError("GATE.md has no budget line or no Hosts line")
    b = dict(zip(["max_boards", "max_requests", "max_seconds", "request_timeout_seconds"], map(int, m.groups())))
    return {"budgets": b, "allowed_hosts": sorted(re.findall(r"`([^`]+)`", h.group(1)))}


def mismatches(cfg, gate):
    out = []
    for k, v in gate["budgets"].items():
        if cfg.get("budgets", {}).get(k) != v:
            out.append(f"budget {k}: config {cfg.get('budgets', {}).get(k)!r} != GATE.md {v!r}")
    if sorted(cfg.get("allowed_hosts", [])) != gate["allowed_hosts"]:
        out.append(f"hosts: config {sorted(cfg.get('allowed_hosts', []))} != GATE.md {gate['allowed_hosts']}")
    return out
