# Action-surface comparison (2026-10-31)

One posting, 8546367002: "AI Engineer – Forward Deployed Engineering (AI FDE)", location "United States". The content and title are the same in every method. The agent fetch returned the same fields and values as the saved copy in `evidence/raw/2026-10-30T23-59-22Z.json`. The only difference is JSON formatting: 10,598 bytes compact versus the saved copy pretty-printed. My hand label is "not relevant".

## Verdicts side by side

| method | evidence | verdict | skills cited |
|---|---|---|---|
| 1. Chat paste, run 1 | `sampling/replies/8546367002-1.txt` | not relevant | none |
| 1. Chat paste, run 2 | `sampling/replies/8546367002-2.txt` | not relevant | Databricks, AWS, Python |
| 1. Chat paste, run 3 | `sampling/replies/8546367002-3.txt` | not relevant | Databricks, AWS, Python |
| 1. Chat paste, run 4 | `sampling/replies/8546367002-4.txt` | not relevant | Databricks, AWS, Python |
| 2. File read | `action_surface/file_read.json` | not relevant | Databricks, AWS |
| 3. Agent fetch | `action_surface/agent_fetch.json` | not relevant | Databricks, AWS |

- **All six verdicts pass the judge's validator** (`python3 -m experiments.sampling check … --posting-id 8546367002`).
- **Skills cited:** chat runs 2–4 cite Python, but the word "Python" does not appear in this posting. Methods 2 and 3 cite only skills the description names: AWS, and the Databricks platform as preferred.
- **Reasons given:** every reply rejects the posting for experience, citing the description's "not intended for internship, new graduate, or entry-level applicants" and "extensive years". Chat runs 1–3 also raise the export-control note as a sponsorship risk. Run 4 and methods 2 and 3 do not.

## What happened in each method

**1. Chat paste**
- **Where:** the Claude app, incognito chat, Sonnet 4.6, web search off.
- **What was sent:** you pasted the full baseline prompt from `experiments/sampling/prompts/8546367002.txt` into 4 fresh chats.
- **Problem during the run:** 3 of the first saves for this posting were spoiled by clipboard mistakes and redone. They are kept in `sampling/spoiled/`.

**2. File read**
- **Directory:** `/tmp/js1-surface-file/` held exactly two files:
  - `posting_8546367002.json`: the posting object copied from the saved live response. 9,380 bytes, sha256 `dcbbf35d…a6c9`.
  - `candidate_fields.json`: the output of `js1.claude_judge.candidate_fields()`, the same object the judge puts in its input. 914 bytes, sha256 `709b34dc…95c9`.
- **What was read:** this Claude Code session ran `cd /tmp/js1-surface-file && ls`, then read both files in full with its Read tool. It read nothing else in that directory.
- **What was written:** the verdict, by hand, to `experiments/action_surface/file_read.json`.

**3. Agent fetch**
- **Directory:** `/tmp/js1-surface-fetch/`, with its own empty state, `state/seen_ids.json` = `{"seen_ids": [], "last_fetched_ids": [], "last_run": null}`. That state was not read or changed afterward.
- **The fetch:** one GET to `https://boards-api.greenhouse.io/v1/boards/databricks/jobs/8546367002`.
  - It went through the project's `check_url` allow-list and redirect handler, with user agent `INFO7375-JS1-student-agent`.
  - Response: HTTP 200, `application/json`, no redirect, 10,598 bytes, sha256 `317c52fb…1516`, at 2026-10-31T15-52-28Z.
- **What was saved:** the raw response (`raw_8546367002.json`) and a fetch log (`fetch_log.json`) in that directory. The response is copied byte for byte to `experiments/action_surface/agent_fetch_raw.json`.
- **How it was judged:** the session read the raw response in full with its Read tool. It used Priya's candidate fields already in its context from method 2; they were not re-read from a file in this directory.
- **Live files untouched:** `state/` and `evidence/raw/` were not touched. `git status` showed no change in either.

## Action surface

| method | what Claude reads | what Claude writes | what Claude sends | authority | failure modes seen in this run |
|---|---|---|---|---|---|
| 1. Chat paste | Only the pasted prompt: the posting's title, location and description text plus Priya's candidate fields | Nothing. It returns text, and I saved the reply by hand | Nothing beyond its reply in the chat | None: no files, no fetching, web search off | 3 saves spoiled by my clipboard (shell text instead of a reply), redone. Runs 2–4 cite Python, which the posting does not name. Run 1 cites no skills while its explanation says skills align |
| 2. File read | The two files in `/tmp/js1-surface-file/`. The session could also read any other file it can reach, including the whole project | `experiments/action_surface/file_read.json`, written by this session | No network call | Claude Code session tools: read and write files, run shell commands | None in the run. The judge had the project open (see the note below) |
| 3. Agent fetch | The Greenhouse response it fetched, plus candidate fields already in its context | Raw response, fetch log and empty state in `/tmp/js1-surface-fetch/`; `agent_fetch.json` and `agent_fetch_raw.json` in the project | One HTTPS GET to boards-api.greenhouse.io, with the project's user agent | Same session tools plus network access. The host was limited only by the allow-list check it chose to run | None in the run. The single-job endpoint is not the board endpoint the watch uses. Same project-context note as method 2 |

**Note on methods 2 and 3:** in both, the judge was this Claude Code session, which has the project open. It had seen CONTRACT.md, my hand labels and the earlier replies. That project context may have influenced its verdicts and citations. The isolated CLI judge is different: it runs from an empty temporary directory, with tools disabled, and gets only the prompt.

## My answers

BEGIN
**18. Single posting.** I'll use one real Databricks posting from the selected development cases for all three methods. I'll record its posting ID and use exactly the same posting content in each comparison.

**19. Agent-fetch version.** I'll actually run the agent-fetch method in a separate test directory with isolated state. I'll save the results as evidence without modifying the live baseline history.

**20. Least autonomy.** For evaluating a single posting, manually pasting it into a chat requires the least autonomy. For the ongoing job watch, I'll use a Python script that fetches public postings from the approved Greenhouse endpoint and manages the local state. Claude won't have browsing, fetching, or file-writing tools. It will only evaluate the information passed to it.

**21. Worst-case risk.** The biggest risks are exposing private information, accessing an unauthorized website, or corrupting the saved posting history. That's why I want a strict host allow-list, fictional persona data, and separate test state.

**22. Read, write, and send permissions.** The Python script handles fetching job postings, reading Priya's fictional résumé and profile, and saving raw responses, state files, verdicts, and reports. Claude receives only one public posting and Priya's relevant skills and eligibility requirements through the CLI. Claude has no tools or independent access to files, websites, or accounts. The script saves Claude's validated response.
END
