# Action-surface comparison (Chapter 3) — Job-Search Agent 1

**Task, done three ways on 2026-10-31:** decide whether posting 4720573005
(*Frontier Agents Engineer (Applied AI)*, Scale AI) is relevant for the fictional
persona Priya Nair. Runs 1 and 2 used the identical prompt contract
(`prompt_4720573005.txt`, built from `prompts/baseline.txt`). Run 3 used my
agent, whose Claude step uses the agent's own built-in prompt (`agent/claude_judge.py`).
After the post-hoc label audit, the correct answer is **not relevant**: the
posting's "Required Qualifications" say 4+ years.

## What each surface could read, write, and send

| | 1. Chat (claude.ai) | 2. File (Claude Code) | 3. Agent (my `agent.run`) |
|---|---|---|---|
| **How run** | New claude.ai web chat outside the course Project; I pasted the prompt (~1:36 PM). | Claude Code v2.1.316, Opus 5.5, Claude Enterprise, **manual mode**; asked it to read the prompt file and not create or edit files (1:38 PM). | `python3 -m agent.run ... --claude` (seeded run, report `reports/runs/20261031T173034Z.md`). |
| **Can read** | Only what I paste. | The file I named. It showed "Read 1 file" **with no permission prompt in manual mode**, so it could equally have read any file in the folder, including the persona résumé. | The allow-listed host (`boards-api.greenhouse.io`) and its own folder's résumé, target, and state files. |
| **Can write** | Nothing on my machine. | Files and shell commands, if I approve, or without asking in auto mode. Earlier today, in auto mode, it created `tools/make_seeded_earlier.py` and ran a command from my paste without asking. | `data/raw/`, its state file, and `reports/runs/`. It refuses to overwrite an existing file. |
| **Sends** | The pasted prompt to Anthropic. | The file contents to Anthropic. | Each new posting's text plus skills/target fields to Claude via `claude -p` **with no tools**; never résumé contact fields (guarded and tested). |
| **Authority it needs** | My claude.ai login. | My login, plus trust for the folder, plus a permission mode. | Network access, write access to its folder, my Claude login, and the ability to run unattended. |
| **Verdict (actual reply)** | not_relevant: cited the 4+ years requirement ✓ | not_relevant: cited the 4+ years requirement ✓ | Rule: not_relevant (title keyword missing; right outcome, wrong reason). Claude judge: **relevant** (its prompt has no experience limit) ✗ |

## What went wrong or could go wrong (observed today, unless marked)
- **Chat:** no automatic record. Twice I saved my own clipboard text instead of
  Claude's reply. I caught it by checking the file and redid the run. Could go
  wrong (not observed): pasting a partial posting, or real personal data.
- **File:** reading needed no approval, even in manual mode. Claude Code also
  asked to import an `AGENTS.md` from outside my folder (I declined) and to trust
  my whole home folder when started there (I declined). A macOS "Data Access
  Blocked" notice appeared during this run; I did not verify what triggered it.
- **Agent:** the first fetch failed on a certificate error and saved nothing
  (it failed closed). Two runs in the same second collided on the report filename;
  the agent refused to overwrite, so the state was untouched. The Claude judge
  gave a wrong verdict because its prompt lacks the persona's experience limit,
  and its validator accepted a cited field (`target.title_keywords`) that does not exist.
- **Across surfaces:** the same baseline prompt gave **relevant** in my earlier
  `claude -p` experiment run and **not_relevant** in runs 1 and 2. On this
  borderline posting, Claude's verdict was not stable across occasions.

## My choice: the least autonomy that suffices
Watching a board needs fetching, saving evidence, and remembering ids between
runs, so some program must hold network and write access. I give that authority
to **deterministic code**: an allow-listed fetch, a fixed state file, and
refuse-to-overwrite. Claude never holds it.

Claude's part, judging one posting, needs only **chat-level access**: text in,
JSON out. That is exactly how the agent calls it: `claude -p` with no tools, from
a temporary directory, receiving only the posting and skills/target fields.

I rejected letting Claude Code fetch, read the folder, and write state itself.
Today it read a file without asking even in manual mode, and in auto mode it
wrote a file and ran a command without asking. Nothing in this task needs Claude
to hold those permissions.

Deciding whether to apply stays mine. The agent never applies, emails, or logs in.

**What remains open:** the agent's Claude step is the least-privileged surface,
but its *prompt* is the weakest of the three (it gave the wrong verdict here).
The fix is to add the persona's hard constraints, distinguishing required from
preferred experience. That is not done in this layer.
