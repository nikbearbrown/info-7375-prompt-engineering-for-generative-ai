"""The source-grounded shortlist (JS3 brief, Step 2; FILTER.md section 4).

For each kept posting, Claude writes a justification as claims with quotes (prompts/justify-v1.txt). The reply is saved
before it is parsed; a reply that is not in the fixed shape is shown as invalid, never fixed. Each claim then gets the
mechanical label from agent/evidence.py, and my hand label (audit/claim-labels.csv) is the final one.
"""
import json
import subprocess
import tempfile
from datetime import datetime, timezone

from . import evidence
from . import filter as filt
from . import rule

CLAUDE_CMD = ["claude", "-p", "--output-format", "json", "--strict-mcp-config", "--tools", ""]  # no tools: text only


class InvalidReply(Exception):
    """Claude's reply is not the fixed JSON shape. Saved and shown as invalid; never repaired."""


def build_prompt(template, job):
    description = rule.description_text(job)
    return (template.replace("{title}", (job.get("title") or "").strip())
            .replace("{location}", (job.get("location") or {}).get("name") or "")
            .replace("{description}", " ".join(description.split())))


def call_claude(prompt, timeout=240):
    """One real Claude Code call. Returns the CLI's JSON envelope as text, unchanged."""
    # Run from an empty folder so no project file (CLAUDE.md, this repo) becomes part of Claude's context.
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(CLAUDE_CMD, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=empty)
    if done.returncode != 0:
        raise RuntimeError(f"claude exited {done.returncode}: {done.stderr.strip()[:300]}")
    return done.stdout


def parse_reply(envelope_text):
    """The CLI envelope -> (claims, model text). Raises InvalidReply for anything outside the fixed shape."""
    try:
        envelope = json.loads(envelope_text)
    except ValueError as e:
        raise InvalidReply(f"the CLI output is not JSON: {e}") from e
    text = (envelope.get("result") or "").strip()
    try:
        reply = json.loads(text)
    except ValueError as e:
        raise InvalidReply(f"the reply is not JSON only: {text[:80]!r}") from e
    claims = reply.get("claims") if isinstance(reply, dict) else None
    if not isinstance(claims, list) or not 4 <= len(claims) <= 5:
        raise InvalidReply("the reply needs 4 or 5 claims")
    for c in claims:
        if not isinstance(c, dict) or set(c) != {"about", "claim", "quote"}:
            raise InvalidReply(f"a claim must have exactly about, claim and quote: {c!r}")
        if c["about"] not in evidence.ABOUT or not all(isinstance(c[k], str) for k in c):
            raise InvalidReply(f"bad claim: {c!r}")
    counts = {a: sum(c["about"] == a for c in claims) for a in evidence.ABOUT}
    if counts["role"] != 1 or counts["experience"] != 1 or counts["location"] != 1 or not 1 <= counts["skills"] <= 2:
        raise InvalidReply(f"wrong mix of claims: {counts}")
    return claims, text


SHORTLIST_SIZE = 8  # hand-set (FILTER.md section 7): about as many postings as I would read closely in one sitting


def rank(decisions, size=SHORTLIST_SIZE):
    """The shortlist: kept postings only, highest score first, ties in collection order, at most `size`.
    No gate-failing posting can be on it."""
    kept = [d for d in decisions if d["verdict"] == filt.KEEP]
    return sorted(kept, key=lambda d: -d["score"])[:size]


def build(decisions, jobs_by_key, spec, persona, template, save_raw, caller=call_claude, now=None):
    """Runs Claude once per shortlisted posting. save_raw(name, text) stores each reply before parsing."""
    skills = filt.resume_skills(persona, spec["skill_lists"])
    entries = []
    for d in rank(decisions):
        key = f"{d['board']}:{d['job_id']}"
        job = jobs_by_key[key]
        asked_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        raw = caller(build_prompt(template, job))
        save_raw(key, raw)
        entry = {"key": key, "title": d["title"].strip(), "score": d["score"], "url": d["url"], "asked_at": asked_at}
        try:
            claims, _ = parse_reply(raw)
        except InvalidReply as e:
            entries.append({**entry, "valid": False, "invalid_reason": str(e), "claims": []})
            continue
        labelled = []
        for c in claims:
            label, why, hand = evidence.label_claim(c, job, spec, skills)
            labelled.append({**c, "machine_label": label, "machine_reason": why, "needs_hand_check": hand})
        entries.append({**entry, "valid": True, "claims": labelled,
                        "machine_abstains": evidence.abstain([(c["about"], c["machine_label"]) for c in labelled])})
    return entries
