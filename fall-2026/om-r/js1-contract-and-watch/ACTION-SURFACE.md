# ACTION-SURFACE.md: Action-Surface Comparison (Chapter 3)

> **Status: complete (2026-10-30).** All three surfaces were run once on
> the same posting. One open item: the paste reply's model name and UTC
> time were not recorded (see Surface 1).

## The task, held constant

One question, one posting, three surfaces.

- **Posting:** 8730125002, Senior Release Engineer. It requires daily
  Claude use for CI/CD work. Hand label: **not relevant**
  (`logs/experiment_dev_labels.md`). Both experiment prompts also said not
  relevant on dev.
- **Question:** the `judge-dev-v0` prompt contract: is this posting
  AI-systems work, as one strict JSON object.
- **Input text:** identical on every surface. It is the exact user message
  the agent builds (`judge.build_user_message`): the fictional
  `resume.json` plus the posting's id, title, and content. Files:
  `action_surface/posting_8730125002.txt` (input only) and
  `action_surface/paste_into_chat.txt` (prompt + input, ready to paste).
  The posting's content in the live fetch (22:31:55Z) was identical to the
  baseline copy (20:15:28Z), so all three surfaces judged the same text.

The surfaces cannot be made perfectly identical, and the differences are
part of the comparison:

| | Paste | File-read | Agent-fetch |
|---|---|---|---|
| Where the instructions go | pasted as chat text | the subagent's task brief | the API `system` field |
| Model | what claude.ai served (**not recorded**) | inherited from this Claude Code session; the exact string is not exposed | `claude-opus-5-5`, pinned and checked on the response |
| Posting source | text copied from a file | a file Claude Code wrote | fetched live by the agent |
| Validator applied | afterward, by hand | afterward, by hand | automatically, in-line |

## Surface 1: PASTE-INTO-CHAT (run 2026-10-30)

**How:** Om pasted `action_surface/paste_into_chat.txt` into a fresh
claude.ai chat with no prior context, and saved the reply to
`logs/action_surface/paste_reply.txt` (file written 22:31:31Z).

**Result:** **not relevant**. The JSON object in the reply was run through
the project's validator (`judge.validate`) and **passed**. Both quoted
phrases are exact substrings of the posting:

> {"verdict": "not relevant", "justification": "posting.content: The responsibilities center on release engineering and CI/CD, e.g. \"Design, build, and maintain GitLab CI/CD or comparable CI/CD pipelines for enterprise applications, including validation, testing, packaging, deployment, promotion, rollback, and post-release verification.\" The AI mentions are about using AI tools as a user, not building, integrating, or operating AI systems: \"Use approved AI-assisted engineering tools such as Claude or similar tools every day to accelerate pipeline development, scripting, test creation, troubleshooting, documentation, release analysis, and operational automation.\" No training, fine-tuning, RAG, agent, or LLM application development is listed."}

**Model: unknown. Date/time (UTC): unknown.** The reply file's `Model:` and
`Date/time (UTC):` lines still hold template placeholders. They are left
unfilled on purpose rather than backfilled with a plausible value. So this
surface's verdict cannot be attributed to `claude-opus-5-5` or to a time.
(The file's own write time, 22:31:31Z, shows when the reply was saved, not
when the chat answered.) This is itself evidence for the comparison: a
chat paste leaves no automatic record of which model answered or when,
unlike agent-fetch, which captures both in its own saved JSON record.

| | Paste-into-chat |
|---|---|
| **Can read** | Only what is pasted into that one chat. Product features such as memory or project knowledge would add more, which is why a fresh, bare chat was used. |
| **Can write** | Nothing on this machine. The conversation is stored in the chat service's history. |
| **Can send** | Nothing beyond the chat itself. The pasted text goes to the chat service. |
| **Authority needed** | A logged-in chat account. No API key, no filesystem, no network access granted to anything. |
| **What could go wrong** | Pasting a real résumé instead of the fictional one, which then sits in chat history. Pasting a stale or edited posting, with nothing recording what was pasted. An unknown model: shown here, where the model went unrecorded. No validator unless a human applies one. Copying the reply back by hand, with metadata left blank. |
| **Human in the loop** | At every step: find, copy, paste, read, record. |

## Surface 2: FILE-READ (run 2026-10-30)

**How:** a fresh Claude Code subagent with no context from this project.
It was given only the `judge-dev-v0` task text and the path
`action_surface/posting_8730125002.txt`, and told to read that one file
and nothing else. It was not told the hand label or any earlier result.
Its output was checked with `judge.validate`. Record:
`logs/action_surface/file_read_20261030T220252Z.json`.

**Result:** **not relevant**. The output **passed** the validator as-is,
and all 3 quoted phrases are exact substrings of the posting:

> {"verdict": "not relevant", "justification": "In posting.content, the listed responsibilities are release and CI/CD engineering, not building, integrating, or operating AI systems: \"Design, build, and maintain GitLab CI/CD or comparable CI/CD pipelines for enterprise applications, including validation, testing, packaging, deployment, promotion, rollback, and post-release verification.\" The only AI duties cover using AI tools as an aid to productivity: \"Use approved AI-assisted engineering tools such as Claude or similar tools every day to accelerate pipeline development, scripting, test creation, troubleshooting, documentation, release analysis, and operational automation.\" Nothing in the posting involves training or fine-tuning models, building RAG pipelines, building agents, or developing LLM applications. The company-wide line \"we embrace AI as a core productivity multiplier\" is a general statement and does not count."}

**What it actually touched:** by its own report, one tool call, a `Read`
of that one file. The harness counted 2 tool uses for the subagent: that
Read plus its report hand-back. **The tool list is self-reported.** The
individual calls were not independently visible.

| | File-read (as run: Claude Code subagent) |
|---|---|
| **Can read** | Any file this Claude Code session is permitted to read: this whole project and beyond. It was limited to one file **by instruction only, not by a sandbox.** |
| **Can write** | The subagent had write, edit, and shell tools available. By its report it used none. (A read-only file surface, such as attaching a file in a chat, would write nothing.) |
| **Can send** | Its model traffic. With shell access it could also have made network calls; by its report it made none. |
| **Authority needed** | This session's filesystem permissions and permission mode. No API key of Om's. |
| **What could go wrong** | **It could read other files**, and here that is concrete: this same project holds Om's hand label for this very posting (`logs/experiment_dev_labels.md`) and earlier Claude judgments of it (`logs/experiment_raw/...`). One unscoped read would turn an independent judgment into a copied one. A real résumé, if one were on disk, would be equally readable. The scope rests on instructions and a self-report, not enforcement. |
| **Human in the loop** | A human chooses and writes the file, and checks the output. |

## Surface 3: AGENT-FETCH (run 2026-10-30T22:31:55Z)

**How:** `python3 scripts/agent_fetch_one.py`, run by Om with his API key.
This is the built agent's own code path, with no human between fetch and
verdict:

1. `watch.run`: live fetch, raw response saved, its own state file written.
2. Posting 8730125002 is taken from that live response. **This is the one
   deviation:** the agent normally judges only new postings; here one id
   is selected so all three surfaces judge the same posting.
3. The rule RECORD and a `judge-dev-v0` JUDGMENT, validated in-line.

Record: `logs/action_surface/agent_fetch_20261030T223155Z.json`.

**Result:** JUDGMENT **not relevant**: valid, served by `claude-opus-5-5`,
`stop_reason: end_turn`, with all 5 quoted phrases exact in the live
posting. The RECORD (rule) was also **not relevant**: it matched 1 of 6
skills ("Python"), and the threshold is 2.

> {"verdict": "not relevant", "justification": "posting.content lists release engineering responsibilities such as \"Design, build, and maintain GitLab CI/CD or comparable CI/CD pipelines for enterprise applications\" and \"Define and implement CI/CD patterns for platforms such as Salesforce, Zuora, and other Business Systems.\" Its AI references only require using AI tools as a productivity aid, not building, integrating, or operating AI systems: \"Use approved AI-assisted engineering tools such as Claude or similar tools every day to accelerate pipeline development, scripting, test creation, troubleshooting, documentation\" and \"Mandatory hands-on experience using AI-assisted development and automation tools such as Claude or comparable enterprise-approved tools as part of day-to-day DevOps and release engineering work.\" No duty involves training or fine-tuning models, RAG pipelines, building AI agents, or developing LLM applications. The company statement \"we embrace AI as a core productivity multiplier\" is general and does not count."}

**What the run touched, checked on disk:**

- **Host:** the run recorded its URL as
  `https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true`,
  which is on the allow-list, so `check_url` let it through and no refusal
  was needed. This shows the permitted path was used. **It does not
  exercise the refusal itself.** That is shown by the `AllowList` unit
  tests, not by this run.
- **Evidence:** the raw response was saved as
  `evidence/gitlab_jobs_20261030T223155Z.json` (237 postings).
- **Its own state file:** `state/action_surface_seen.json` was created
  (22:31:56Z, 1 run, 237 ids, `baseline: true`, `new_ids: []`). This was
  its first run, so it recorded every id as seen and reported none as new.
- **The real watch baseline was untouched:** `state/gitlab_seen.json`
  still has its last-modified time of 20:15:30Z and the same SHA-1
  (`91258bbb...`) recorded when the seeded state was copied from it.

**Observed board drift (real, not seeded).** Between the baseline fetch
(20:15:28Z, 238 postings) and this fetch (22:31:55Z, 237), the board
changed. A comparison of the two evidence files shows **one posting
removed and none added**: **8565469002, Senior AI Engineer**. It is one of
the 6 rule-relevant postings used in the Step 3 compare. Two things
follow:

- This is the kind of change the watch exists to track, and the saved
  evidence made it checkable after the fact.
- **The watch did not detect it.** The drift was found by comparing the
  two evidence files by hand. The watch reports only ids it has not seen
  before; it has no code path for ids that disappear. Run against the
  live state now, it would report 0 new postings and say nothing about a
  relevant posting closing. For a job seeker, that is a real gap: closed
  postings are invisible to the agent.

| | Agent-fetch (the built agent) |
|---|---|
| **Can read** | The live board over HTTPS, from `boards-api.greenhouse.io` only. Locally: `resume.json` and its state file. **Claude itself reads only the text of one request and has no tools.** |
| **Can write** | A timestamped evidence file per run (~3.7 MB), the state file (atomic replace), and logs (`logs/judgment_events.jsonl`, run output). All inside this project. |
| **Can send** | HTTPS GET to `boards-api.greenhouse.io`. HTTPS POST to `api.anthropic.com` with the fictional résumé and the posting text. Nothing else: it never applies, emails, messages, or logs in anywhere. |
| **Authority needed** | Om's real API key (billed to him), outbound network, and write access to this project directory. |
| **What could go wrong** | A broken allow-list could fetch an unintended host. The state file could be corrupted: a partial write is prevented by the atomic replace, but **two concurrent runs could race (no lock; the last writer wins)**. A run between the baseline and the real second run consumes the "new" postings. **Removed postings go unreported**, as the 238 → 237 drift showed. Posting text is untrusted input to Claude: a hostile posting could try to steer the verdict, but Claude has no tools to act on, and the validator rejects anything off-format. **The Claude endpoint is not on the allow-list:** the SDK honors `ANTHROPIC_BASE_URL`, so a set environment variable would send the key, résumé, and posting to another host. And a wrong verdict arrives with no human in the loop, which is why it is labeled JUDGMENT, not fact. |
| **Human in the loop** | Only at the edges: starting the run and reading the report. |

## Side by side

| | 1. Paste | 2. File-read | 3. Agent-fetch |
|---|---|---|---|
| **Reads** | what's pasted | any permitted file (scoped by instruction) | one allow-listed host + local state |
| **Writes** | nothing locally | could write; reported none | evidence, state, logs |
| **Sends** | chat text | model traffic; could do more | 2 hosts, both named |
| **Authority** | chat login | session file permissions | API key + network + project write |
| **Main risk** | wrong thing pasted (a real résumé) | reads beyond scope: label leakage | unintended host; state race; removals unseen |
| **Model** | not recorded | inherited, not exposed | `claude-opus-5-5` (verified) |
| **Verdict on 8730125002** | **not relevant** (valid) | **not relevant** (valid) | **not relevant** (valid); rule record: not relevant |
| **Hand label** | not relevant | not relevant | not relevant |
| **Can it watch?** | no | no | yes: fetches and remembers ids; does not detect removals |

## What the three results show

**All three surfaces reached the same verdict on this one posting, not
relevant, and all three passed the same validator.** Their justifications
drew the same distinction, quoting the same "Use approved AI-assisted
engineering tools such as Claude…" line as tool use rather than
AI-systems work. So for this posting, **the judgment itself needed no
more autonomy than a bare chat paste provides.** The extra access the agent
has adds nothing to the quality of the verdict.

Limits on that: it is one posting, one call per surface, and the paste
surface's model is unknown. Agreement here does not show the surfaces
agree in general.

## The choice: agent-fetch, and why it is the least that suffices

The watch agent runs at the **agent-fetch** level. That is not because it
is the most convenient. It is the least autonomy that can do the task.

The task is not "judge a posting". It is **"watch a board and report only
what is new since the last run."** That requires three things:

1. **Fetching** a live board on its own, which needs network access.
2. **Remembering** which ids were already seen, across runs, which needs a
   state file it can write.
3. **Saving evidence** of each fetch, which needs to write files. The saved
   evidence is what made the 238 → 237 drift checkable at all.

Paste and file-read can judge just as well, as shown above, but neither can
watch. With either one, a human has to fetch the board, diff the ids
against last time, and hand over each new posting. At that point the human
*is* the agent. If the task were only "judge this one posting", paste would
suffice, and choosing agent-fetch would be over-granting.

Agent-fetch is kept as narrow as the task allows:

- **The autonomy lives in deterministic, tested Python, not in the model.**
  At the agent-fetch level, Claude's own surface is the same as paste: text
  in, one JSON object out, no tools, no file access, no network. That is
  why the verdicts match. The code around it does the fetching and writing,
  and code can be tested and audited.
- **One board host**, refused otherwise.
- **Writes only inside this project:** evidence, state, logs.
- **Never applies, emails, messages, or logs in** (assignment privacy
  rules; there is no code path for any of it).
- **Only the fictional résumé:** `watch.validate_resume` refuses a résumé
  without `"fictional": true`, an `@example.com` email, and a 555 phone.

## The real control: the allow-list

What makes agent-fetch safe enough to grant is the allow-list refusal
logic built and tested in Step 2 (`agent/fetch.py`):

- `ALLOWED_HOSTS = {"boards-api.greenhouse.io"}`. `check_url` refuses any
  URL that is not HTTPS to exactly that host. It runs before the request
  and again on the final URL after redirects.
- `_AllowListRedirects` refuses a redirect to any other host. Without it,
  `urllib` would follow such a redirect silently.
- The board token must match `[A-Za-z0-9_-]+`, so it cannot inject a path.
- Tested in `tests/test_watch.py` (`AllowList`): other hosts, plain HTTP, a
  look-alike host (`boards-api.greenhouse.io.evil.example`), an off-list
  redirect, and path injection are all refused.
- Audited: `agent/fetch.py` is the only module in the project that imports
  any network library, and it holds the only URL the agent fetches.
- In the live run, the one board request went to the allow-listed host
  (the permitted path). The refusal path is shown by the tests above, not
  by that run.

Supporting controls: the atomic state write (`os.replace`); `--from-file`
replays require an explicit `--state`, so a replay cannot touch the live
state; the pinned model plus the strict output validator; and the
fictional-résumé validator.

**Gaps this comparison surfaced (not fixed):**

- **Removals are invisible.** The watch reports new ids only, so a
  posting that closes (8565469002 did) goes unreported.
- **No lock** against concurrent runs on the same state file.
- **The allow-list governs board fetches only.** The Claude API host is
  whatever the SDK resolves, and `ANTHROPIC_BASE_URL` can change it.
- **In the file-read surface, scope was enforced by instruction, not
  sandbox,** in a project that contains the answer key.
- **The paste surface leaves no record** of which model answered, or
  when, unless a human writes it down. Here neither was written down.
