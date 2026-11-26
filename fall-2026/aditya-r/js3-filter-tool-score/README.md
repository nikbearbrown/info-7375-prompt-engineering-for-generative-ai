# Job-Search Agent 3: the Filter, the Tool, and the Score

**Student:** Aditya Raj (`aditya-r`) · **Course:** INFO 7375 · **Assignment:** JS3 (Chapters 7–9)
**Folder:** `fall-2026/aditya-r/js3-filter-tool-score/` · **Persona:** Priya Nair. She is **fictional**. No real résumé is used.

This layer decides which of the postings my agent collected reach Priya, and why. It has three parts:
- a **filter written as a document** (`FILTER.md`), with every number recomputable by hand;
- a **from-scratch MCP tool server** that lets Claude score one saved posting;
- an account of **what moves the score**, measured one change at a time on labels held out from development.

**The agent never applies, emails, messages or logs in. JS3 makes no network request:** it reads only the captures that JS1 and JS2 already made.

_Technical documentation drafted by Claude Code. The labels, the freeze decisions and the sign-off are Aditya's, and the attributions below say which is which._

## Start here: reproduce one posting's score

```bash
.venv/bin/python -m js3.explain 6233043004 --filter v1.1 --text   # every term, its field and the exact quote, then the full text
```

[`WHAT_MOVES_THE_SCORE.md` §2](WHAT_MOVES_THE_SCORE.md) works through the same posting by hand (S43: v1.0 gives 5 → reject; v1.1 gives 7 → keep; only Y moved). Its row in [`shortlist/SHORTLIST.md`](shortlist/SHORTLIST.md) shows every claim with its quote. Aditya's blind label is in [`labels/dev_labels.csv`](labels/dev_labels.csv) (S43: yes).

## Starting point: my own JS1 and JS2

The starting point is **not** the Reallocation Engine and **not** Lectern. Details and hashes are in [`SOURCES.md`](SOURCES.md).

**Inherited unchanged:**
- the JS1 normalization and matching (`inherited/rules.py`);
- the JS2 Greenhouse/Ashby parsers;
- the persona;
- **every board response the collector captured.** These are the JS1 LIVE run of 2026-10-30 (Databricks) and the JS2 LIVE run of 2026-11-10 (Databricks, Figma, Notion, and one deliberate 404). Their body hashes, recorded at capture time, are re-verified on every build.

**Not used:** the JS1/JS2 per-posting judge, and the JS2 loop.

## Language, toolchain, commands

- **Python 3.12.8** (standard library) and **pytest 8.3.3**.
- **Claude Code CLI 2.1.310**, model `claude-opus-5-5`, used only for the MCP client run and the context experiment.
- **Node v22.14.0 / npm 10**, used only to evaluate the other server.
- macOS (arm64), git.

```bash
git clone --filter=blob:none --sparse https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai
git sparse-checkout set fall-2026/aditya-r/js3-filter-tool-score
cd fall-2026/aditya-r/js3-filter-tool-score
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python -m pytest -q                       # filter, corpus/splits and tool-server tests
.venv/bin/python tests/mutation_check.py            # plants wrong versions W1–W6; each must be CAUGHT
sh scripts/clean_clone_check.sh                     # all of it in a fresh extraction, plus a byte-for-byte replay check

# replay (offline, deterministic)
.venv/bin/python -m js3.corpus                      # 1,294 postings, corpus/PROVENANCE.json
.venv/bin/python -m js3.run --filter v1.0           # also: --filter v1.1, or --threshold 5 (a setting change)
.venv/bin/python -m js3.audit                       # reject audit and single-change comparisons on dev labels
.venv/bin/python -m js3.reader_labels && .venv/bin/python -m js3.shortlist --filter v1.1
.venv/bin/python -m js3.experiment --labels labels/heldout2_labels.csv   # held-out comparisons (after the freeze)

# the tool server (stdio); see transcripts/ for a real Claude Code session
.venv/bin/python js3/mcp_server.py --filter v1.1
```

## What actually ran

| What | When (2026-11-25 unless noted) | Label | Evidence |
|---|---|---|---|
| Board captures | 2026-10-30 and 2026-11-10 | **LIVE** (by JS1/JS2) | `raw/`, `raw/CAPTURES.json` |
| Filter v1.0 on all 1,294 postings | | REPLAY of the saved captures | `runs/v1.0/` (11 keep, 1,282 reject, 1 cannot_tell) |
| Labels on 63 postings | Aditya, blind | human | `labels/dev_labels.csv`, `labels/TRANSCRIPTION.md` |
| Reject audit and candidate rules | | REPLAY + labels | `audit/AUDIT.md`, `audit/audit_results.json` |
| Filter v1.1 (Aditya's choice) | | REPLAY | `runs/v1.1/` (15 keep) |
| Claude Code as MCP client | 21:26 UTC | **LIVE Claude** | `transcripts/claude_code_2026-11-25_run1.*` |
| Other server, 4 sessions | | LIVE local process; **js3 test client, not Claude** | `transcripts/fs_*`, `evaluations/` |
| Claude context experiment: 6 format-check calls (dev) and 48 calls on H2 | 23:09–23:10 UTC for H2 | **LIVE Claude**, before any H2 label existed | `experiments/claude_context/raw/` |
| Fresh blind audit A4 of v1.1 (37 postings) | Aditya, entered in the sheet; sealed `d6cf5cc` | human | `labels/audit_a4_labels.csv`, `audit/audit_a4_results.json` |
| Labels on 24 H2 postings | Aditya, blind, edited in the sheet; sealed `94c0c89` after the freeze `9cde2b9` | human | `labels/heldout2_labels.csv`, `labels/SEAL_H2.json` |
| Pre-registered comparisons on H2 | after the seal | REPLAY + labels + the saved Claude responses | `experiments/RESULTS_H2.json`, [`WHAT_MOVES_THE_SCORE.md` §3](WHAT_MOVES_THE_SCORE.md) |
| Clean-extraction check | | fresh venv | `scripts/clean_clone_check.sh` |

## Rubric → strongest evidence

| Rubric item | Evidence |
|---|---|
| **Filter as a versioned document, written first (10)** | [`FILTER.md`](FILTER.md). v1.0 was committed alone as `80427cc`, before any code. Tests `5de50f2` came before the scorer `b33fca0`. The change log records A1–A3, C1–C3, v1.1 and the findings after the freeze. |
| **Reject audit (12)** | [`audit/AUDIT.md`](audit/AUDIT.md), **two blind audits by Aditya:** v1.0 (30 uniform random rejects, 0/27 decided were misses, 95 % CI 0–12.8 %) and a **fresh audit of the frozen v1.1 on unseen postings** (A4: 1/30 random rejects missed, CI 0.1–17.2 %; 2 of 4 decided just-below calls missed; second false friend `architect`). Both include closest calls on both sides, keeps, and what the sample can and cannot show. False friend: "agent(s)" and "unity catalog" from employer boilerplate (§3). Every rule added, cut or rejected is in §4. |
| **Source-grounded shortlist (12)** | [`shortlist/`](shortlist/README.md): 15 postings and 123 claims, each with a label, field and verbatim quote; relevance ≠ entailment (`6865704002`); abstentions; the negation counterexample (`8546367002`). |
| **Tool server and two evaluations (12)** | `js3/mcp_server.py`; [`transcripts/`](transcripts/) (a real Claude Code session, both directions); [`evaluations/EVALUATIONS.md`](evaluations/EVALUATIONS.md): declared vs observed, what compatibility does not entitle a client to assume, and trust decisions for our server and for `server-filesystem` 2.3.0 |
| **What moves the score (8)** | [`WHAT_MOVES_THE_SCORE.md`](WHAT_MOVES_THE_SCORE.md): the origin of every number, a score worked by hand, single changes on held-out H2 (pre-registered in `FREEZE.json`), and why persistence is not training. **H2 result:** v1.1 changed nothing (a null result); C-b alone and threshold 5 made false keeps; every filter missed the one yes (H10), which Claude with the rules in context caught. |
| **Sign-off and driver's seat (6)** | below |
| Frictional · Sources | [`FRICTIONAL.md`](FRICTIONAL.md) · [`SOURCES.md`](SOURCES.md) |

## Held-out status

- **The first held-out set is no longer held out.** Aditya's first 63 labels reached Claude as screenshots, so Claude read the 23 rows originally drawn as held-out. **Aditya decided** to redraw.
  - Under amendment A3, those 23 became dev evidence.
  - A **fresh held-out set H2** (24 postings, cluster-disjoint) was drawn.
- **The freeze came first.** `FREEZE.json` was committed (`9cde2b9`) while the H2 sheet was still blank. Its hash is in the freeze, and Aditya filled the sheet in directly afterwards.
- **H2 has no v1.0 keep.** Every keep cluster was already on the first sheet, so H2 tests recall near the threshold, and precision only on postings that a change newly keeps.

## Driver's seat

_The "why" column was drafted by Claude Code for Aditya to edit or replace._

| Part | Claude did | Aditya did | Why that judgment stays Aditya's |
|---|---|---|---|
| The filter | Drafted FILTER.md v1.0, the amendments and the candidates; measured each candidate | Labeled the postings that measured it; **chose v1.1** among the measured candidates; decided to redraw the held-out set | The rules encode what Priya's time is worth. Measurements can rank rules, but only the person whose time it is can decide which errors are acceptable. |
| Labels (is this posting worth her time?) | Built the blind sheets; transcribed the first batch from screenshots | Labeled 63 + 24 postings without seeing scores | **This is the judgment the whole agent is measured against.** If Claude supplied it, the audit would be measuring Claude against itself. |
| Shortlist claims | Labeled the DUTY claims and the LEVEL reader checks with verbatim quotes. Flagged that the New Grad roles' graduation windows exclude a Dec-2025 graduate. | Labeled several of those New Grad roles `yes`, to "check the graduation window" | **A claim can be contradicted by the posting and the posting can still be worth reading.** Whether to pursue a role despite an eligibility line is a personal decision, not an evidence question. |
| Tool trust | Built and exercised both servers; proposed the trust decisions | Confirms or changes the decisions (sign-off) | Attaching a tool decides what an agent may touch on his machine, so it is authorized by the person who bears the risk. |
| Sign-off | Drafted the evidence pointers and the candidate "Not checked" items | Runs `scripts/personal_checks.sh`, chooses the items, signs or withholds | A signature vouches for claims, so each one must rest on something he ran or read himself. |

## Sign-off — Job-Search Agent 3

_**Pending Aditya.** The items below are blanks or candidates for him to keep, edit or delete. No first-person verification claim is made on his behalf._

- **Checked:** _(Aditya: which properties, by which of your own tests. Run `sh scripts/personal_checks.sh | tee evidence/aditya_personal_checks.txt` and name what you checked.)_
- **How:** _(by hand / by a test I wrote before reading Claude's code / by recomputation / with Claude's help: say which parts)_
- **Not checked** (candidates, at least three to keep):
  1. The transcription of the first 63 labels beyond the title cross-check. The source CSV was deleted, and only the screenshots remain.
  2. Claude's DUTY and LEVEL reader labels on the shortlist, other than those he re-read himself.
  3. `server-filesystem` on its supported Node (≥ 24), its 2026-07-28 protocol era, and its `move_file`/`edit_file` tools.
  4. Whether any posting is still open: the captures are from 2026-10-30 and 2026-11-10.
  5. The v1.1 negation false friend (`8546367002`): found after the freeze, not fixed.
  6. The precision of v1.1's keeps on unseen postings: the A4 kept sample was 2 postings, both `unsure`.
- **Not claiming:**
  - that the filter finds every posting worth Priya's time;
  - any population error rate (all rates are sample intervals or describe stratified samples);
  - that Claude's judgments are correct;
  - that anything was trained.
- **Signed or withheld:** ______________________ (name, date)

## Privacy

- **Not published:** the persona is fictional. The private Claude chat, the label screenshots, the npm install of the evaluated server and the caches stay local, outside this folder.
- **Checked before publishing:** the published transcripts were checked for home paths, usernames and email addresses. The only redaction is one sandbox path, which is declared in each transcript header.
- **The ZIP** is built from one commit by `scripts/package.sh`, and its file list is compared with that commit's tree.
