# SOURCES

## What I started from

| Source | Used for | Date |
|---|---|---|
| **My JS1 agent**, `../js1-contract-and-watch/` (final commit `3c098e1`) | `jsagent/rules.py`, `jsagent/contract.py`, `persona/arya-sahni.json` and the rule tests (`tests/test_rules.py`), copied **unchanged** in commit `3109ccd`; the Databricks state from my JS1 runs (last 2026-11-01), carried over with ids as strings | copied 2026-11-09 |
| The instructor's **Lectern** `fall-2026/nik-bear-brown/lectern/ATS.md` | Board slugs and the two traps it documents: Greenhouse `hubspot` empty vs `hubspotjobs`, and SmartRecruiters returning 200 + `content: []` for a company it doesn't have. **No Lectern code was copied.** I re-probed both traps by hand. The Greenhouse one is out of date (see below) | read 2026-11-09 |
| TA feedback on JS1 (Aravind Balaji, Canvas, 2026-11-09) | Two JS2 asks: add the Intern exclusion, and run the watch on two real calendar days | 2026-11-09 |
| Public board APIs (no login, GET only): `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.smartrecruiters.com` | The boards | 2026-11-09 and 2026-11-10 |
| Python 3.13 standard library; `certifi` (CA bundle path only, macOS SSL fix) | Everything in `jsagent/`, `tests/`, `tools/`, `review/` | |

**Lectern correction I found:** on 2026-11-09, Greenhouse `hubspot` returned **HTTP 404**, not the empty board that ATS.md
(probed 2026-09-26) describes. The SmartRecruiters trap still worked (200 with `totalFound: 0`), so I used that for the
empty-board demo. My probes are listed in GATE.md "Board facts".

## What I did (Riya)

- **Every GATE.md decision:** the boards, the budgets (6 boards / 10 requests / 60 s, changed only by a dated amendment), the
  error policy (retry only temporary errors, once, after 2 s; never retry 4xx; flag empty boards), and which write needs my
  approval (removing seen ids). I chose these in chat on 2026-11-09. I asked whether they were best practice before
  committing. Claude wrote them up, and proposed the repeat rule, the exit wording and the list of wrong versions,
  which I agreed to. GATE.md was committed alone, before any JS2 code (`61c093d`).
- **Reviewing the 17 boundary predictions** before the policy code existed. I questioned why so many were "refuse" and kept them.
- **Rule amendment 3** (Intern, Internship only; Co-op and Apprentice left out on purpose) and **amendment 4** (full-time only:
  "i dont want to see coops and any tpye of part time jobs i just want full time jobs", plus Contract and Temporary).
- **Commands I ran myself:** live run day 1 (2026-11-09), live run day 2 (2026-11-10), the reproduce script and red test, the Claude Code patch
  command, the post-patch test and mutation run, and the finished-wrong-answer demo with its independent check.
  Their output is quoted in TRACE.md and review/REVIEW_PACKET.md as it appeared in my terminal.
- **The review decision** on Claude's patch (accept), in my own words.
- **FRICTIONAL.md entries** and **the sign-off signature**.

## What Claude contributed

**Claude Code (Claude Opus 5.5), main session, 2026-11-09 to 2026-11-10:**

- Probing the board endpoints with curl before GATE.md, which found the out-of-date Lectern note.
- **All JS2 code:** `jsagent/loop.py`, `jsagent/policy.py`, `jsagent/ats.py`, `tools/independent_check.py`,
  `tools/check_wrong_versions.py`, `review/reproduce.py`, and amendment 4 in `rules.py`, `ats.py` and `contract.py`.
- **All tests:** `tests/test_loop.py`, `tests/test_policy.py` (B1–B17), `tests/test_intern.py`, `tests/test_fulltime.py`.
  I decided what the intern and full-time tests had to check; Claude wrote them.
- **Drafts** of GATE.md (from my answers), BOUNDARY.md, RULE.md, TRACE.md, review/REVIEW_PACKET.md, README.md, this
  file and the sign-off / driver's-seat table, for me to check.
- **Runs it made itself:** the smoke test into a scratch folder (not submitted), the seeded 4-board run, all test runs while building.
- **Problems it found that I then decided on:** the stale `hubspot` note; the "Internal/International/Internals" look-alikes;
  that Notion's `employmentType` was wrong for "Outcomes Architect [Contract]" (so the title and field both count);
  that `--allowedTools` did not fence the patch session.

**Claude Code (Claude Opus 5.5), separate headless patch session, 2026-11-09 20:41 UTC** (`afb7dddc-…`):
the Intern patch to `jsagent/rules.py`, from the prompt in `review/patch_prompt.md`. Raw response:
`review/claude_patch_response.json`. Tool calls: `review/patch_session_tool_calls.md`.

No Claude output is used as a job verdict in JS2. Every verdict comes from the written rule (a record).
