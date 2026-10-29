# Action-surface comparison (Chapter 3) — draft for Nishant to edit

The same task on three surfaces: apply the frozen revision-1 rule (`prompts/revision-1.md`, sha256
`16ecb436…c453206`) to development posting **8660923002**, "Senior Applied ML/AI Scientist - Search",
New York City, NY; San Francisco, CA. My hand label and the rule judge both say **relevant**, with
failed_check **null**. The `claude -p` dev run of the same prompt is in `runs/revision1-dev/`: it was
valid, relevant, null, with 1 supported citation.

Chapter 3's terms, as used here:
- **See / decide / do:** reading input, producing a judgment, changing state.
- **Granted capabilities:** what the runtime lets the surface do, not what its name suggests.
- **Authority:** what it has been permitted to do. Capability isn't authority.
- **Proposed vs observed:** what was asked or claimed, against what the saved evidence shows.

## Chat surface (claude.ai, pasted prompt)

- **Reads:** one message: the whole revision-1 prompt with the résumé and posting pasted in
  (`action-surface/chat-prompt.md`, byte-for-byte the prompt `claude -p` was sent). It was a new chat
  in an Incognito window, outside my course Project, so no Project instructions or files were in
  context. I did not record which other claude.ai features were enabled on my account.
- **Writes:** nothing on my machine. **Sends:** nothing. It returns text, and I copy it.
- **Authority it needs:** my claude.ai login, and my decision to paste fictional data into it. No file,
  shell or network authority on my side.
- **What went wrong (observed 2026-10-29, saved 17:38 ET, approximate):**
  - The reply is **not valid JSON**. It starts with an empty code fence (`` ```json `` then `` ``` ``)
    before the object.
  - In a diagnostic that strips the fence (not a contract result), the object still fails: it cites
    `resume_field` `"experience[0].title"`. That is bracket notation, not a dotted path.
  - Its verdict (relevant) and failed_check (null) match my label and the rule judge. Its 3 quotes are
    all supported, but they don't count, because the reply is invalid.
- **Evidence:** `action-surface/chat-reply.json` (saved byte for byte from `chat-reply.txt`, CRLF
  kept) and `action-surface/check-output.txt`.

## File surface (claude.ai, two uploads plus an instruction)

- **Reads:** two uploaded files, `file-surface/8660923002.txt` (the posting with HTML removed and line
  breaks kept) and `file-surface/resume.example.json`, plus `file-prompt.md`: the instruction line and
  the revision-1 rule and schema, with nothing pasted inline. It was a new Incognito chat outside the
  Project.
- **Writes:** nothing on my machine. **Sends:** nothing. The uploads do leave my machine and are
  stored by claude.ai with the chat.
- **Authority it needs:** my claude.ai login, and my decision to upload files. It is the same as chat
  plus file upload. Here the files are fictional and already public in this repo; with a real résumé,
  this is where real personal data would leave the machine.
- **What went wrong (observed 2026-10-29, sent 17:50 ET):**
  - The reply is **not valid JSON**: every JSON quote is a curly quote (`“ ”`).
  - In a diagnostic that swaps in straight quotes (not a contract result), it is accepted: relevant,
    null, 1 citation (`content`, `skills.languages`, "Python"), supported.
  - None of the three risks predicted in the kit happened: `posting_field` used the contract's name
    `content`, `posting_id` was present and correct, and no quote spanned a line break.
- **Evidence:** `action-surface/file-reply.json` and `action-surface/check-output.txt`.

**What these two results can't tell us:** I saw the replies after claude.ai rendered them and I copied
them. Whether the empty fence and the curly quotes were in the model's output, or were added by
rendering, copying or an editor, isn't observable from what was saved. Either way, the copy-paste
path is part of these surfaces, and `claude -p` (JSON on stdout, read by code) has no such step.

## Agent surface (Claude Code) — to be run on 2026-10-30 as the second watch run

- **What it will be:** Claude Code running `python -m agent.run --claude` in this folder.
- **Reads:** the Faire board at the allow-listed host `boards-api.greenhouse.io`, `state/seen_ids.json`,
  the résumé and requirements, and the repository files Claude Code itself can open.
- **Writes:** `state/seen_ids.json` and a new run folder `runs/2026-10-30-<n>/` (`raw.json`,
  `meta.json`, `report.json`, `report.md`, and `claude/` with every prompt and raw reply).
- **Sends:** HTTP GETs to the board. For each new posting, one `claude -p --output-format json
  --tools ""` call, run in an empty temporary folder, so the judge itself has no tools and no
  repository context.
- **Authority it needs:** shell, file writes and network. This is far more than the judging task
  needs. The program needs it to fetch and to keep state; Claude Code is granted it as the operator.
- **What could go wrong:** Claude Code holds the same shell, so it *could*:
  - push to GitHub;
  - edit files other than the run folder and state, such as the prompts, labels or contract;
  - reach the network beyond the allow-list, which only constrains `agent/watch.py`, not Claude Code.

  None of these is needed. The proposed action is "run one command." The observed state changes
  should be checked afterwards with `git status` and `git diff`.
- **Evidence (after it runs):** the run folder `runs/2026-10-30-<n>/`, the diff of
  `state/seen_ids.json`, and `git status` before and after.

## Comparison

| | Chat | File | Agent (planned) |
|---|---|---|---|
| Sees | pasted prompt | uploaded posting and résumé, plus the rule | board, state, repo |
| Decides | verdict text | verdict text | verdict via `claude -p` with no tools |
| Does (state change) | none | uploads stored by claude.ai | writes state and the run folder; network GETs |
| Authority | claude.ai login | login plus upload | shell, files, network |
| Valid on 2026-10-29 | no (fence; bracket path) | no (curly quotes) | to be run |
| Verdict / failed_check (diagnostic) | relevant / null | relevant / null | to be run |

## The autonomy choice

The watch and the state are handled by Python code, not by Claude:
- **Allow-listed fetch:** `agent/watch.py` accepts only `boards-api.greenhouse.io` and re-checks the
  host on every redirect.
- **Atomic state write:** a temp file plus `os.replace`, and the state moves only after the report is
  written.
- **Claude's role:** it gets the least autonomy that suffices. Text in, JSON out, through
  `claude -p --tools ""` in an empty folder. That is the same capability set as the chat surface,
  with code instead of a person on both ends.

Why the other two add authority this task doesn't need:
- **File surface:** uploads add file reading, but the posting and résumé already fit in the prompt.
  Uploading also stores the files with a third-party chat, which costs nothing here (fictional data)
  but would expose a real résumé.
- **Agent surface:** shell, file writes and network are needed for the *watch*, and tested,
  deterministic code already does the watch. Giving them to the *judge* would add the push, edit and
  network risks listed above, and no check in the contract needs them.
- **The chat surface shows a further cost of a human in the loop.** Its copy-paste path broke the
  JSON on both claude.ai surfaces today. A program reading `claude -p` stdout doesn't have that step.

What is and isn't tested: the host allow-list has tests (`tests/test_watch.py`). The redirect
re-check, the atomic state write and the `--tools ""` argument are in the code but no test covers
them yet.
