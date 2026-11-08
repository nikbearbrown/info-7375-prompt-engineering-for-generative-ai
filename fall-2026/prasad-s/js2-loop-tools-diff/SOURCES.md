# SOURCES — Job-Search Agent 2

Written 2026-11-08 (JS2-CP10). Every source this folder used, and where its
use is recorded. Every number, time and claim below is taken from a file in
this folder or a commit message, and cited, or, where marked
"(Prasad, confirmed 2026-11-08; not in a committed file)", rests on Prasad's
confirmation. Commits are cited by checkpoint ID.

## The JS2 brief

- `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` in the
  course repository: "Job-Search Agent 2 — The Loop, the Tools, and the
  Diff". 100 points; due Tuesday, November 10, 11:59 pm ET; Chapters 4–6.
- It sets the deliverables: GATE.md, README.md, SOURCES.md, FRICTIONAL.md, the
  trace, the demo, the boundary-test table, the review packet, the sign-off
  and the driver's seat.
- It names Lectern and the Reallocation Engine as optional starting points,
  and asks the student to say what they started from.

## Job-Search Agent 1, at bff5356

- `fall-2026/prasad-s/js1-contract-and-watch/` at commit `bff5356`
  (JS1-CP18, 2026-10-31), as signed off on 2026-10-31 (GATE.md header).
- **What was copied:** agent, tests, tools, CONTRACT.md, config.json,
  resume_persona.json and .gitignore. They came in unchanged via git archive,
  with `diff -r` clean and 45/45 tests passing here (JS2-CP3).
- **Still unchanged since then** (`git diff` against JS2-CP3):
  `agent/persona.py`, `agent/replies.py`, `agent/errors.py` and
  `tests/expected/`.
- **What JS2 changed** is recorded in CONTRACT.md v0.5–v0.8.
- JS1's own sources are in `js1-contract-and-watch/SOURCES.md`.

## Lectern — reference only

The instructor's collector, at `fall-2026/nik-bear-brown/lectern/`. No
Lectern file is copied into this folder (`git ls-files`).

| Item | What it says | Where JS2 uses it |
|---|---|---|
| `collect.py:52` | The Ashby URL: `https://api.ashbyhq.com/posting-api/job-board/{quote(slug)}?includeCompensation=true` | The Ashby fetch URL form, cited in CONTRACT.md v0.5 item 1 ("pattern from Lectern, collect.py:52"); used in `agent/config.py` and `agent/policy.py` |
| `collect.py:42` | Lectern sends `User-Agent: lectern (course project)` | Precedent for JS2's honest User-Agent, cited in CONTRACT.md v0.8 item 1 ("Lectern does the same (collect.py:42)") |
| `ATS.md` slug notes | Line 11: HubSpot's board is `hubspotjobs`, not `hubspot`. Line 30: Miro's slug is `realtimeboardglobal`, and `miro` does not work. Line 92: an empty `jobs` array means a wrong slug or an empty board, not "not hiring" | Used on 2026-11-02 to choose two probe cases, `miro` and `hubspot` on Greenhouse (Prasad, confirmed 2026-11-08; not in a committed file). The probes got 404 for both (`evidence/gate_probes/probe_log.txt`): for `hubspot`, a 404, not the empty board ATS.md describes |
| `sources.json`, the Stripe note (line 133, `_comment`) | Stripe was removed from Lectern's watch list on 2026-10-18 at Professor Bear's word, for a reason about educational applicability, "Not a finding about either company" | Read on 2026-11-02 to see why Lectern dropped Stripe. The reason was not about the board itself, so Stripe stayed (Prasad, confirmed 2026-11-08; not in a committed file). GATE.md §0 keeps stripe as "JS1's board" |

## The Greenhouse and Ashby public job-board APIs

Read without credentials, by GET only, over https (GATE.md §5).

**Greenhouse:**
- URL: `https://boards-api.greenhouse.io/v1/boards/<token>/jobs?content=true`
  (CONTRACT.md v0.5 item 1).
- A missing board answers 404 with the JSON body
  `{"status":404,"error":"Job not found"}`
  (`evidence/gate_probes/gh_nosuchboard_2026-11-02T194210Z.json`).

**Ashby:**
- URL:
  `https://api.ashbyhq.com/posting-api/job-board/<name>?includeCompensation=true`
  (CONTRACT.md v0.5 item 1).
- A missing board answers 404 with the plain-text body "Not Found",
  `text/plain; charset=utf-8`
  (`evidence/ashby_js2nosuchboard_2026-11-07T000612Z_a1.json` and its
  sidecar).
- The host sits behind Cloudflare, which refused Python's default User-Agent
  with 403, error 1010 (CONTRACT.md v0.8 item 1; JS2-CP5c).
- The Ashby fields JS2 reads (id, title, location, secondaryLocations,
  descriptionPlain, jobUrl) are listed in CONTRACT.md v0.5 item 3.

**Saved responses:**
- Probes of 2026-11-02 (`evidence/gate_probes/`, JS2-CP1).
- Snapshots of 2026-11-05 (`evidence/snapshots/`, JS2-SNAP).
- Runs 1 and 2 (`evidence/*_a1.json`, JS2-CP6 and JS2-CP9).

No official Greenhouse or Ashby documentation pages were consulted; the
endpoints came from Lectern and Prasad's own probes (Prasad, confirmed
2026-11-08; not in a committed file).

## The Python standard library

- Python 3.11 or newer, standard library only, tests with `unittest`
  (CONTRACT.md header). Run on Python 3.13.17 (CONTRACT.md header).
- Modules imported by `agent/`: argparse, dataclasses, datetime, hashlib,
  html, json, os, pathlib, re, socket, sys, time, urllib.
- Modules imported by `tests/`: contextlib, copy, datetime, http, importlib,
  io, json, os, pathlib, re, shutil, socket, sys, tempfile, unittest, urllib.
- No official Python documentation pages were consulted (Prasad, confirmed
  2026-11-08; not in a committed file).

## Claude Code

What it built, per checkpoint, as each commit message says. "Run by me" in a
commit message is Prasad.

| Checkpoint | What Claude Code did, per the commit message (or the file cited) |
|---|---|
| JS2-CP1 | Not named in the message. GATE.md was "Written: 2026-11-05, before Claude Code changed any code in this folder" (GATE.md header); author Prasad Shinde. The gate probes of 2026-11-02 were run by Claude Code at Prasad's instruction; Prasad reviewed the report and committed (Prasad, confirmed 2026-11-08; not in a committed file) |
| JS2-CP2 | Not named (GATE.md v0.2: review by Claude.ai; see below) |
| JS2-SNAP | Not named in the message. The 2026-11-05 snapshots were fetched by Claude Code at Prasad's instruction; Prasad reviewed the report and committed (Prasad, confirmed 2026-11-08; not in a committed file) |
| JS2-CP3 | Not named in the message. The copy (git archive and diff -r) was run by Claude Code at Prasad's instruction; Prasad reviewed the report, ran the tests (45/45) and committed (Prasad, confirmed 2026-11-08; not in a committed file) |
| JS2-CP5a | "Built by Claude Code against GATE.md v0.2 §5 after it stopped on four rule conflicts, which I decided. Board membership added on review. Tests run by me: 64/64." It also made eleven smaller decisions, D1–D11, reviewed and accepted by Prasad (CONTRACT.md v0.6 changelog and item 4) |
| JS2-CP5b | "Built by Claude Code against GATE.md v0.2 and CONTRACT.md v0.6. It stopped on five open points, which I decided. Checked by me: 106/106 tests." It also made twenty smaller decisions, E1–E20, reviewed and accepted by Prasad (CONTRACT.md v0.7 changelog and item 7) |
| JS2-CP5c | "Test written and failing first (evidence/tests/), then the fix, by Claude Code. Tests run by me: 108/108." The defect was found by Prasad's smoke run and confirmed with curl (same message) |
| JS2-CP6 | Not named. Run 1 was "Run by me" |
| JS2-CP7 | Not named in the message. The independent check is Prasad's ("My independent check, no agent code"). The demo was run by Prasad, in a throwaway copy (/tmp/js2_demo), with the same seeds as the README's reproduction commands (Prasad, confirmed 2026-11-08; not in a committed file) |
| JS2-CP8b | "Assertions mine (GATE.md v0.3 §6 W5, committed in CP8a). Test code typed by Claude Code, with no agent code changed. Run by me" |
| JS2-CP8c | "Patch by Claude Code, scoped to GATE.md v0.3 §4: agent/run.py only, plus the one test that asserted the old row. Reviewed by me as a change in behavior; run by me … Accepted." |
| JS2-CP8e | Not named in the message. The label change was made by Claude Code at Prasad's instruction; Prasad reviewed it, ran the tests (109/109) and committed (Prasad, confirmed 2026-11-08; not in a committed file) |
| JS2-CP9, JS2-CP9b | Not named. Run 2, the recount and the boundary run were "run by me" |
| JS2-CP10 | This README.md and SOURCES.md were drafted by Claude Code from the files and commit messages, with Prasad's sections ("Boundary tests: predicted vs actual", "Review packet", "Sign-off", "Driver's seat") left for Prasad. Not yet committed |

## Claude.ai

The reviews, and the amendment text it typed, as each changelog states. In
every case below, the changelog says the decisions are Prasad's.

| Document and version | What Claude.ai did (the changelog's words, condensed) |
|---|---|
| GATE.md v0.2 (2026-11-05, JS2-CP2) | "changes from a review by Claude (Claude.ai) on 2026-11-05; the decisions are mine." Items 1–10 of the review list are applied there |
| GATE.md v0.3 (2026-11-07, JS2-CP8a) | "Reviewed by Claude (Claude.ai) on 2026-11-07, which suggested the live-path test, the concrete 59 ids, the reworded reason in the first row and the header line; the decisions and the wording are mine." |
| CONTRACT.md v0.5 (2026-11-06, JS2-CP4) | "Claude (Claude.ai) reviewed two drafts; after the second review it typed the fixes into the file at my request. I made every decision and ran the evidence checks myself" |
| CONTRACT.md v0.6 (2026-11-06, JS2-CP5a-v0.6) | "Claude (Claude.ai) typed this entry and the v0.6 section at my request; the decisions are mine." |
| CONTRACT.md v0.7 (2026-11-06, JS2-CP5b-v0.7) | "Claude (Claude.ai) typed this entry and the v0.7 section at my request; the decisions are mine." |
| CONTRACT.md v0.8 (2026-11-07, JS2-CP8d) | "Claude (Claude.ai) typed this entry and the v0.8 section at my request; the decisions are mine." |

Beyond the changelogs (Prasad, confirmed 2026-11-08; not in a committed file):
- Claude.ai planned the checkpoints, wrote the prompts Prasad gave Claude
  Code, and reviewed every commit.
- It wrote the check commands Prasad ran: the isRemote counts on 2026-11-06,
  the CP7 independent check, and the run 2 recount script. Prasad ran each on
  Prasad's own files, and the numbers come from those runs.
- It typed GATE.md v0.3's edit blocks, combining Prasad's text with its
  suggested fixes, as the v0.3 changelog lists.

Earlier, JS1-era Claude contributions (CONTRACT.md v0.2–v0.4) are recorded in
CONTRACT.md's changelog.
