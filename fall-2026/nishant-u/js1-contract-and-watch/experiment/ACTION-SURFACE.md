# Action-surface comparison (Chapter 3)

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

The pasted originals, `chat-reply.txt` and `file-reply.txt`, stay on my machine, untracked. The `reply`
field of each committed `.json` is byte for byte the same as its `.txt` (550 and 244 bytes, compared
2026-10-29); the `.json` adds only the surface, posting_id and saved_at.

**What these two results can't tell us:** I saw the replies after claude.ai rendered them and I copied
them. Whether the empty fence and the curly quotes were in the model's output, or were added by
rendering, copying or an editor, isn't observable from what was saved. Either way, the copy-paste
path is part of these surfaces, and `claude -p` (JSON on stdout, read by code) has no such step.

## Agent surface (Claude Code) — run on 2026-10-30 as the second watch run

- **What it was:** Claude Code running `python -m agent.run --claude` in this folder.
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
- **Evidence:** the run folder `runs/2026-10-30-1/`, the diff of `state/seen_ids.json`, and
  `git status` before and after.

### Results, 2026-10-30

- **Live second run (`e4d3cae`):** `runs/2026-10-30-1/`. 67 postings, 0 new, 1 removed since the
  baseline (8580854002). It fetched only `boards-api.greenhouse.io` (`meta.json`). The Claude judge
  wasn't called, because nothing was new. `state/seen_ids.json` changed only in `last_run`; it still
  holds 68 ids.
- **Seeded runs, labeled seeded (`14cf874` with the baseline prompt; `2eb62a9` with revision-1):** a
  replay of the same `raw.json` against a copy of the state with 3 ids removed (seed 20261030; postings
  outside my 20 labeled ones; 1 rule-relevant, 2 not). All 3 were detected as new. The rule and Claude
  verdicts matched 3/3 in both runs. With revision-1, Claude's failed_check matched the rule's 3/3
  (R4, null, R1). Every reply was valid and every citation was supported. The first seeded run used the
  baseline prompt because the agent's default hadn't been switched to the frozen revision-1; its replies
  have no failed_check at all. The real `state/seen_ids.json` was untouched by both (sha256
  `1dab9c29…` before and after).
- **What the operator (Claude Code) did, from its own session log:**
  - Commands: `date`; `git status`, `log`, `show`, `diff --stat`, `add`, `commit` and `stash list`;
    `ls`, `cat`, `head`, `sed -n`, `grep`, `wc`, `find`, `sha256sum`, `cp`; `python -m agent.run`
    (once live, twice seeded); `seeded/select_ids.py`; `python -m unittest`;
    `scripts/validate_course.py`.
  - Files written: the run folders and state above (by `agent.run`); `seeded/` (README,
    `select_ids.py`, state copies); the fixes in `agent/run.py` and `agent/watch.py`;
    `tests/test_agent_fixes.py`; `FRICTIONAL.md`; and, for the final docs, `README.md`, `SOURCES.md`
    and this file. A pre-run copy of the first seeded state went to its temporary scratch folder.
  - No push. No edits outside this folder. Hosts: `boards-api.greenhouse.io` (from `agent/watch.py`)
    and the `claude` CLI's own connection. This comes from the code and the run records; network
    traffic wasn't monitored independently.
- **Operator failures:**
  - It put `git stash -u` into a command, which would have stashed my two untracked files. The
    auto-mode classifier blocked it; the files were unchanged.
  - It reported `scripts/validate_course.py` as exit 0, when the 0 was `tail`'s exit code. The real exit
    code was 1, from failures outside this folder; it had already committed by then.
  - It read a missing `failed_check` as null (`.get()` returns None) and reported Claude's answers as
    wrong, when the baseline prompt never asked for the field.

## Comparison

| | Chat | File | Agent (2026-10-30) |
|---|---|---|---|
| Sees | pasted prompt | uploaded posting and résumé, plus the rule | board, state, repo |
| Decides | verdict text | verdict text | verdict via `claude -p` with no tools |
| Does (state change) | none | uploads stored by claude.ai | writes state and the run folder; network GETs |
| Authority | claude.ai login | login plus upload | shell, files, network |
| Valid | no (fence; bracket path), 2026-10-29 | no (curly quotes), 2026-10-29 | yes, 3/3 in each seeded run |
| Verdict / failed_check (diagnostic) | relevant / null | relevant / null | 3/3 verdicts match the rule; failed_check 3/3 with revision-1 |

## The autonomy choice

**What the surfaces showed.** On the same posting and the same frozen prompt, both claude.ai surfaces gave the right verdict (relevant, failed_check null), but neither reply passed the validator. The chat reply had an empty code fence before the JSON and, even with the fence removed, cited a résumé field in bracket notation (experience[0].title); the file reply used curly quotes. The claude -p judge, which reads raw output with no copy-paste step, never failed the validator in 60 calls. I can't tell whether the fence and the curly quotes came from the model or from the browser, copying, or an editor; either way, every manual step between the model and my code is another place things can break. The bracket-notation field is different: it's inside the JSON, so it's the model's own error, and the validator caught it.

**Least autonomy that suffices.** The task needs a board fetched, state remembered and a verdict judged. Only the fetching and state need authority, and tested code does those: an allow-listed host, refused redirects and an atomic state write, each with a test. Claude needs only to read text and return JSON, so the judge runs with --tools "" in an empty folder, the same capability set as the chat surface but without the copy-paste step. The file surface adds nothing the judge needs. The agent surface adds a shell, file writes and network access that the judge must not have, so it's used only to operate the watch, not to judge.

**Agent surface:** The agent surface needed shell, file and network authority to operate the watch, and it made mistakes a code-only path doesn't: an unsafe git command (blocked), a wrong exit code, a misread field. This supports keeping the judge at the chat-level capability set and having tested code, not an agent, do the fetching and state.

Each safety claim above has a test (no real network, no real `claude` call):

| Claim | Test |
|---|---|
| Only `boards-api.greenhouse.io` is fetched | `tests/test_watch.py` `HostAllowList.test_other_hosts_are_refused_before_any_network_call` |
| A redirect to another host is refused before any request to it | `tests/test_safety.py` `RedirectRefusal.test_redirect_to_another_host_is_refused_before_any_request_to_it` (and `test_redirect_within_the_allow_list_is_followed`) |
| A failed state write leaves the old `seen_ids.json` unchanged, with no partial file | `tests/test_safety.py` `AtomicStateWrite.test_failure_after_temp_written_before_replace_leaves_old_state`, `test_failure_partway_through_writing_leaves_old_state` |
| The judge always runs with `--tools ""` | `tests/test_safety.py` `JudgeHasNoTools.test_command_always_has_tools_set_to_none` |
| The judge runs in an empty folder | `tests/test_safety.py` `JudgeHasNoTools.test_judge_runs_in_an_empty_folder` |

The `test_safety.py` tests were added 2026-10-29, after the implementation. Each failed against a
deliberately broken version before passing against the real code:
- the redirect check removed, or the opener built without it;
- the state written in place;
- `--tools` dropped;
- the judge run in the repository folder.

The tests cover these mechanisms. They don't show what Claude Code, as the operator of the agent
surface, will or won't do with its own shell.

Conclusion drafted with Claude (claude.ai), reviewed and approved by Nishant, 2026-10-29.
