# Action-surface comparison (Chapter 3)

## The task, held constant

Judge one posting against the baseline prompt contract.
- **Posting:** **8041054003**, Software Engineer, Conversational Products & Agent Workflows, Boston. My reviewed label: `relevant`.
- **Résumé:** the same fictional résumé subset in every surface.
- **Answer:** a validated `relevant` / `not_relevant` verdict with cited evidence.

Every surface uses the same fictional résumé subset and posting JSON, packaged differently:
- [`action_surface/8041054003_input.json`](action_surface/8041054003_input.json) is the exact user message the agent sends: the eight allowed résumé paths plus the posting, with no name, email, or phone.
- [`action_surface/8041054003_chat_paste.txt`](action_surface/8041054003_chat_paste.txt) is `prompts/baseline.txt`, a `---` separator, then that same message, ready to paste.

## Surface 1: paste one posting into a chat

**Steps:**
1. Open a **new** conversation on claude.ai.
2. Paste the whole of `8041054003_chat_paste.txt` and send it.
3. Copy the reply with claude.ai's Copy button and save it with `pbpaste > experiment/action_surface/surface1_response.txt`.
4. Check it against the contract:

```bash
.venv/bin/python -I -c "import json,sys; sys.path.insert(0,'.'); from jsagent.validator import validate_claude_output as v; r=json.load(open('resumes/aarav-patel.json')); p={j['id']:j for j in json.load(open('evidence/klaviyo_2026-10-31_preimplementation_live.json'))['jobs']}[8041054003]; print(v(open(sys.argv[1]).read(), r, p))" experiment/action_surface/surface1_response.txt
```

**Result.** Revan ran it on claude.ai with Opus 5.5 on 2026-10-31; the reply was saved at 14:36 ET as [`surface1_response.txt`](action_surface/surface1_response.txt).
- **Verdict:** `relevant`, matching my reviewed label.
- **Contract:** the output **passed** the validator: one bare JSON object, seven justification entries, every résumé value and posting phrase found where it was cited.
- **Evidence it chose:** title, location, Python, Kafka, AWS, Kubernetes, and the "3+ years" requirement against `years_experience` 2.

**A first attempt that does not count.** Before this run, the paste went by mistake into the Claude Code session building this project, and that session's reply was saved as the result. It was discarded: that session already knew my hand label and the agent's verdict for this posting, so it was not a fresh chat. The two replies differ (eight entries against seven, different quoted phrases), which is how the mix-up was confirmed. See FRICTIONAL.md §7.

## Surface 2: give Claude a file to read

**Steps:**
1. Open a **new** conversation on claude.ai and attach `8041054003_input.json`.
2. Paste the text of `prompts/baseline.txt` as the message, saying the input is in the attached file.
3. Save the reply as `action_surface/surface2_response.txt`, then run the same validator command with that file name.

**Result.** Revan ran it twice on claude.ai with Opus 5.5 on 2026-10-31, each time with the baseline prompt pasted and the input file attached. Both replies were prose, and both **failed** the validator: `output is not a single bare JSON object (prose or code fence present)`. Both read as `relevant` ("Good stretch match. Apply." / "Good fit, worth applying"), matching my hand label, but no program can read either reply that way.

**First run: it used information that was not in the input.** ([`surface2_first_attempt_redacted.txt`](action_surface/surface2_first_attempt_redacted.txt))
- **What it did:** it named two of *my real* projects, described one, and advised adding them to "your resume". It also offered to write résumé bullets.
- **Why that matters:** neither project appears in the prompt or the attached file, which hold only the fictional Aarav Patel's résumé subset and the posting. The chat treated the fictional candidate as me and filled in from something the account already held.
- **What is committed:** the reply with the four mentions of those projects redacted. The unredacted reply stays on my machine (`private/`, git-ignored).

**Second run, after I removed claude.ai memory:** ([`surface2_response.txt`](action_surface/surface2_response.txt))
- **No outside information.** Everything it cited is in the attached file: target titles, location, exclusions, skills, `years_experience` 2 against "3+ years", and the missing generative-AI and FastAPI/Django experience.
- **Still not in the contract's format.** It again gave a prose recommendation with advice ("add it to your resume before applying"), not the JSON object the prompt asked for.

**What the two runs suggest, and how far that goes.**
- **Memory is the likely source of the outside information.** The project names were gone once memory was removed. That is one run before and one after, so it is consistent with memory as the source, not proof of it; I did not check past-chat search or Projects separately.
- **The observed answer form differed.** With the same prompt text, the paste (surface 1) returned valid JSON and both file runs returned prose. One paste run and two file runs cannot separate the cause from chance.

## Surface 3: an agent fetches and keeps its own state

**What ran.** `python -m jsagent run` (CONTRACT.md):
- It fetched the board over GET from the allow-listed host only.
- It saved the raw response to `evidence/`.
- It diffed the response against `state/seen_ids.json`.
- It judged the new postings with the rule and with Claude.
- It wrote `runs/` and then the state file.

**Result.** Live run 2 judged 8041054003 at 05:51:09 UTC on 2026-10-31 (`runs/2026-10-31T05-51-09Z_live.json`, commit `5fc0b68`). The rule said `relevant`, and Claude said `relevant`; the output passed the validator.

**Who held what.** In this design the **model is not the agent**. The Python program holds every power: network access, file writes, and the API key. Claude receives one text message and returns one JSON object. It has no tools, so it cannot fetch, write, or send anything.

**A second agent surface also ran here: Claude Code itself.** It built this project with shell and file access, and its record shows what that broader authority did:
- **It fetched more than the agent's allow-list permits.** During contract review it ran `curl` against `boards-api.greenhouse.io` for 13 board slugs (`greenhouse`, `hubspot`, `toast`, `klaviyo`, and others). The finished agent refuses every slug but `klaviyo`, and these fetches came before that allow-list existed. They stayed on one public host and were read-only.
- **It changed a file more than intended.** Its first edit of `experiment/labels.csv` rewrote all 21 lines, because it switched Windows-style line endings to Unix ones. `git diff --stat` caught it, the file was restored, and the fix was redone as a one-line change (`335d280`).
- **It wrote and committed directly.** It committed throughout, and it ran `git stash` and `git checkout --` to test old code. Each of those actions was visible in the transcript, but none needed a separate approval from me.

## Comparison

| | 1. Chat paste | 2. File to read | 3a. This agent (code holds power) | 3b. Claude Code as the agent |
|---|---|---|---|---|
| **Can read** | What I paste, plus whatever the claude.ai account holds about me (memory, past chats) | The file I attach, plus whatever the account holds about me: with memory on, it used my real projects, which were not in the file | The allow-listed board endpoint; the résumé and state files on disk | Anything its permissions allow: the repo, the shell, the network |
| **Can write** | Nothing; I copy the answer out | Nothing; I copy the answer out | `evidence/`, `runs/`, `state/` only, through fixed code paths | Any permitted file, including labels, state, and git history |
| **Can send** | My pasted text to claude.ai | The file's contents to Claude | A GET to `boards-api.greenhouse.io`; the résumé subset and posting to the Claude API | Whatever its shell can reach |
| **Authority needed** | A claude.ai account | A claude.ai account plus a file upload | Network to one host, writes to three folders, an API key in the environment | Shell, filesystem, and network permissions, plus git |
| **What could go wrong** | Wrong posting pasted, so verdicts get paired with the wrong job (wrong version 1, by hand); pasted into the wrong conversation (it happened here: see Surface 1); a real résumé pasted; no record unless saved | The judgment mixes in the account's knowledge of me (it happened: real projects, with memory on); the format is ignored (it happened in both runs); the file holds more than intended; text inside the posting tries to instruct the model | State corruption (baseline leak, state advanced on failure), a host outside the allow-list, spend on every new posting, key leakage; posting text can change a verdict, but it cannot cause a fetch or a write because the model has no tools | Fetching outside any allow-list, unintended edits to labels or state, history rewrites, injected instructions in posting text that it then acts on with tools |
| **Repeatable?** | Only by repeating it by hand | Only by repeating it by hand | Yes: one command, logged, with tests | Depends on the session |

## The choice: the least autonomy that suffices

**For judging one posting, surface 1 suffices.** A paste needs no authority, and in this run it returned a valid, checkable answer. For future spot checks, I would use a fresh chat with memory off.

**Surface 2 did worse at the same task here.** Neither file run kept the format, and the first mixed in my real projects. A chat on my own account cannot be relied on to judge the *fictional* candidate in front of it: it may judge me instead.

**For the actual job, it does not.** The job is noticing *new* postings over days, and that needs a fetch, a memory of seen ids, and a saved record. A chat or a file read cannot remember state between runs without me doing it by hand, which brings back the copy-paste errors the contract's wrong versions describe.

**So the job needs surface 3, but with power held by code, not by the model (3a, not 3b):**
- **Fetching and state stay deterministic.** They are allow-listed and tested: every wrong version in CONTRACT.md has a test, and the mutation check shows each test catches its wrong version.
- **The model gets the narrowest role that still needs judgment:** text in, JSON out, checked by a validator. Its output can never become a rule verdict or a state change.
- **The API call sees only what the code sends.** It has no account memory, so the surface 2 leak of my real projects cannot happen there: Claude receives the eight résumé paths and the posting, nothing else.
- **Injected text in a posting has a hard ceiling.** At most it can corrupt one labeled judgment. It cannot trigger a request or a write.
- **Claude Code's broader autonomy was useful for *building* the agent, under my review.** I would not give that autonomy to the *running* watch. The fetches and the line-ending edit above show what it does with authority the task never needed.

## Not shown by this comparison

- **Repeatability of surfaces 1 and 2.** Surface 1 ran once and surface 2 twice, on one posting. Whether a paste always keeps the format, or a file upload always breaks it, is not shown.
- **Which account setting supplied my real projects.** Removing memory made them disappear in one rerun; past-chat search and Projects were not checked separately.
- **Prompt-injection resistance.** No posting with injected instructions was tested on any surface.
- **Behavior over many days.** The agent ran twice, and the second run's change was seeded.
