# GATE Addendum 1 — clarifications (2026-11-10)

- **Author of the decisions:** Aditya Raj. Sections 1–6 below are his words, given in the Claude Code session in answer to six clarification questions Claude raised after reading `GATE.md`. Claude saved them verbatim on 2026-11-10 at 16:33 EST and changed only the markdown heading levels.
- **Scope:** these clarify `GATE.md` (commit `8257ffb`). They do not change any budget, host or selected board. They were committed before any JS2 loop implementation existed.
- **Precedence:** where a section below is more specific than `GATE.md`, it applies.

---

## 1. Redirect handling

A redirect is a run-level policy error: refuse it before following it, stop further operational work, report `error`, and exit 2. Preserve diagnostic evidence and do not publish staged state.

This follows the original gate’s treatment of prohibited actions. W8 must verify that the destination receives no request, not merely that an error appears afterward.

## 2. Approval record and export timing

Use `approvals/<run-id>.json` at the JS2 root. The runtime may read this directory but must not create or modify its approval records.

Approval must bind to the proposal’s run ID, operation, exact destination, and SHA-256 of the exact export bytes. A missing or mismatched approval cannot authorize the write.

Implement `--export <run-id>` as a separate export-only invocation:
- Read the saved proposal and matching human approval.
- Validate them and create the approved export.
- Make no board requests or model calls.
- Refuse an existing destination rather than overwriting it.
- Record a separate export result without changing the original watch run’s status.

Keep this simple. Do not build a general approval framework. Give me the exact approval action to perform when we reach the demonstration; do not perform or claim that human approval yourself.

## 3. Shortlist contents

Include only postings whose deterministic RECORD is `relevant` and whose JUDGMENT has passed validation.

Show both verdicts, including disagreements. Include the provider, board, posting ID, title, job URL, source run, and evidence references. Do not imply that a validated judgment proves suitability.

Relevant postings with pending or invalid judgments are excluded from the export and counted as withheld. Clearly identify the export as a partial shortlist if the source run has unresolved work. Export approval does not turn an incomplete watch run into a finished one.

## 4. Finalization reserve

Reserve 10 seconds within the existing 180-second limit.

Before each network or model invocation, compute the remaining operational allowance as:

180 seconds − elapsed time − 10 seconds.

If this is not positive, stop productive work and finalize. Otherwise, the invocation’s timeout is the smaller of 20 seconds and that allowance.

The deadline must cover body reading and subprocess execution, not just connection setup. Retry waits also consume time. Do not claim a hard deadline is enforced if the implementation only checks it between potentially unbounded operations.

## 5. Published reconnaissance evidence

Inspect the existing reconnaissance JSON for private information. If suitable, copy it unchanged to:

`evidence/pre_gate_recon/pre_gate_recon_20261110T183146Z.json`

Record its hash and verify that the copy matches the local original. If redaction is necessary, document it and do not claim byte identity.

Add a public evidence pointer in the gate addendum explaining the relationship to the original `local/recon/` reference. Do not publish the rest of `local/`, private conversations, or the sealed observations.

## 6. Expected demonstration outcome

Yes: if the 10-call limit prevents remaining evaluations, the real demonstration should report `budget-exhausted`, exit 4, retain pending postings, and separately report the deliberate board failure.

If all evaluations fit within budget but the deliberate board fails, the result should be `incomplete`, exit 3.

Report whichever actually occurs. Do not increase the budget, remove the failing board, shrink the observed backlog, or invent judgments to obtain a cleaner result.

---

## Evidence pointer for the reconnaissance (added by Claude, factual only)

`GATE.md` cites `local/recon/pre_gate_recon_20261110T183146Z.json`. That folder is Aditya's private local workspace and is not published. Its reconnaissance file is published unchanged as [`evidence/pre_gate_recon/pre_gate_recon_20261110T183146Z.json`](evidence/pre_gate_recon/pre_gate_recon_20261110T183146Z.json).

- SHA-256 of both copies: `c1e62853c6d6183c4aa8935d864b0323f70957289a3ea34063911cd1a30849d7`. `cmp` confirmed the two are byte-identical on 2026-11-10, so no redaction was made.
- Privacy inspection: the file holds only public endpoint URLs, HTTP statuses, content types, timings, byte counts, response hashes, JSON key names and one sample public posting id per board. It contains no user name, path, email address, token or response body; the 9-byte body `Not Found` is the only exception.
- Provenance: Claude Code wrote the probe that produced it and ran it at 2026-11-10T18:31:46Z, before `GATE.md` existed. That scratch script (last modified 13:31 EST, the time of the run) is published unchanged as [`evidence/pre_gate_recon/recon_probe.py`](evidence/pre_gate_recon/recon_probe.py) (SHA-256 `cfcff50bd4c4df9e49e1675b61aa069c5ed1a9a728ef700e6497055265836d66`). It is reconnaissance only, not agent code. Nothing else from `local/` is published.
