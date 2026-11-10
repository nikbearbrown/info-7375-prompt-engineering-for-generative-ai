# SOURCES — Job-Search Agent 1 (nishant-u)

## Sources used

- **Greenhouse Job Board API.** Endpoint used, GET only, no login:
  `https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true`. Documentation:
  <https://docs.greenhouse.io/job-board.html>, opened by Claude Code during setup on 2026-10-29. It says
  authentication isn't required for GET endpoints (`FRICTIONAL.md`).
- **Faire's board** on Greenhouse (board token `faire`): 68 postings in the baseline response of
  2026-10-29, saved verbatim as `runs/2026-10-29-1/raw.json` (sha256
  `3c10b536e3805bb5a4fca46800ac5caf4c521fa84c9beec30a8ab0beb995c2b7`). I haven't read Faire's own
  careers-site terms (`FRICTIONAL.md`). The raw.json files are Faire's public board responses saved verbatim; they include contact details Faire itself published in its postings (e.g. an accommodations contact). They are kept unedited so their recorded sha256 hashes stay valid.
- **The Reallocation Engine** (<https://github.com/nikbearbrown/the-reallocation-engine>), for the
  fictional persona Priya Nair: `search/examples/priya-nair/resume.example.json`, repo commit
  `d08afddc` (2026-08-17), copied unchanged to `data/resume.example.json`, sha256
  `a4fdbc960457ba911b9d3b8593400d17ea77f35a33ce2a508128c1694c4493c1`. Her `profile.yml` was read for
  her target roles.
- **Course chapters** in this repository:
  - Chapter 1, `chapters/01-next-token-prediction-and-sampling.md`: the sampling report and the
    sign-off template.
  - Chapter 2, `chapters/02-prompt-contracts-and-evaluation.md`: the contract, the validator, the
    dev / held-out split and the one-change prompt experiment.
  - Chapter 3, `chapters/03-chat-assistant-agent.md`: the action-surface comparison.
- **The JS1 brief**, `assignments/assignment-js1-the-contract-and-the-watch.md`.
- **The course AI policy:** `prerequisites/ai-policy.md`
  (<https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/ai-policy.md>)
  and the video [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz).

## What I wrote or decided

- **The contract** (`CONTRACT.md`, commit `3deb719`) and its rule choices: the title terms and
  exclusions, R3's US-location test, counting only Priya's shipped skill lists for R4, allowing Senior
  and Staff titles, the three wrong versions, and the failure statement. I approved the amendments: the
  empty-quote fix and revision-1's `failed_check`.
- **The board choice:** Faire, with Instacart as the backup (`FRICTIONAL.md`).
- **The labeling rule** (`LABELING-RULE.md`, commit `dd83c2e`), written before any posting was chosen.
- **All 20 hand labels** (`experiment/labeling/labels.csv`, commit `8e2fa73`), labeled by hand in Excel
  before any Claude judge call.
- **The one prompt change:** adding `failed_check` in revision 1, and why (`PROMPT-EXPERIMENT.md`).
- **The freeze** (commit `37fd62f`) before the held-out evaluation, which ran once (commit `8a53c80`).
- **The gate decisions:** the declared pass rule (valid AND verdict equals my hand label), declaring
  failed_check agreement as a second measure before the revision ran, and when to move from dev to
  freeze to held-out.
- **Accepting or rejecting Claude Code's suggestions:** for example, keeping the 50-state R3 list without
  `, DC`, keeping `resume_field: null` for R1–R3, fixing empty quotes through a contract amendment, and
  having the safety tests added. Two choices are still undecided: absence citations, and the judge's
  empty folder (`FRICTIONAL.md`, "My decisions").
- **The sign-off and the driver's seat** (`README.md`): approved and signed by me, 2026-10-30.
- **The limits on the agent surface** (no push, no seeded run without asking), and catching that the
  agent still used the baseline prompt and that a missing `failed_check` was misread as null
  (`FRICTIONAL.md`, 2026-10-30).

## What Claude contributed

### claude.ai (chat), 2026-10-29

- Drafted the contract text with me; I reviewed and approved it (`CONTRACT.md`, first line).
- Drafted the prompts with me (`prompts/baseline.md`, `prompts/revision-1.md`).
- Explained how the rule's wording reads while I labeled, for example that "AI/ML" contains ML and
  that "Leader" isn't "lead". I shared the 20 titles and locations, including the held-out ones. It
  didn't label any posting (`FRICTIONAL.md`, `experiment/SPLIT.md` exposure log).
- The two action-surface replies (chat and file surfaces) in `experiment/action-surface/` are claude.ai
  output, saved byte for byte, observed 2026-10-29.

### claude.ai (chat), 2026-10-30

- Drafted the sign-off and the driver's seat in `README.md` with me; I approved them.

### Claude Code, 2026-10-29

- **Code:** `agent/`, written against my contract.
- **Tests:** `tests/`, including the constructed fixtures and the three mutants in `tests/mutants.py`,
  and the safety tests added after the implementation (commit `3d397ae`).
- **Scripts:** `experiment/make_split.py`, `claude_dev.py`, `report_dev.py`, `rule_vs_hand.py`,
  `hand_labels.py`, and `action-surface/check_surface_replies.py`.
- **Report drafts:** `SAMPLING-REPORT.md`, `BASELINE-DEV.md`, `PROMPT-EXPERIMENT.md`,
  `ACTION-SURFACE.md`, the `FRICTIONAL.md` entries, and this file and `README.md`.
- **Bugs it found:**
  - The empty-quote hole: an empty quote passed the validator and counted as supported. Found during
    implementation; fixed by the contract amendment.
  - The `skills.agent_note` letter split, a bug Claude Code both made and caught. On 2026-10-29, before
    the contract was written, its read-only skills check read the string letter by letter, so single
    letters counted as skills. I didn't write that code. I then made it wrong version 3 in my contract.
  - The safety claims in the `ACTION-SURFACE.md` draft were broader than the tests.
- **The fresh-clone check** in `README.md` (2026-10-29).

### Claude Code, 2026-10-30 (the agent surface)

- **Operated the watch** as the agent surface (`experiment/ACTION-SURFACE.md`, "Results, 2026-10-30"):
  the live second run (`e4d3cae`) and, with my permission, the seeded runs (`14cf874`, `2eb62a9`),
  including `seeded/select_ids.py`.
- **Fixed the agent** after I pointed out the baseline-prompt default (`2eb62a9`): revision-1 as the
  default, seeded labels kept, the printed path, the null rendering, and `tests/test_agent_fixes.py`.
- **Its own mistakes** in that session, logged in `ACTION-SURFACE.md` and `FRICTIONAL.md`: a
  `git stash -u` blocked by the auto-mode classifier, a wrong exit code reported for
  `scripts/validate_course.py`, and a missing `failed_check` read as null.
- **Drafted** the 2026-10-30 updates to `ACTION-SURFACE.md`, `README.md`, this file and `FRICTIONAL.md`.

### `claude -p` (the judge), 2026-10-29

- Every Claude verdict in this folder: the sampling calls, both dev runs and the held-out evaluation.
  Each was a separate `claude -p --output-format json --tools ""` call on my Claude Code login (CLI
  2.1.312, model `claude-opus-5-5`, no API key). Each saved prompt, raw reply, date and session_id is
  under `experiment/sampling/` and `experiment/runs/`.
- 2026-10-30: the six judge calls in the seeded runs (`seeded/runs/` and `seeded/rev1/runs/`, three
  each), the same command run in an empty temporary folder, model `claude-opus-5-5`. Each prompt, raw
  reply and meta (date, session_id) is saved under that run's `claude/` folder. The live second run
  made no judge call.
