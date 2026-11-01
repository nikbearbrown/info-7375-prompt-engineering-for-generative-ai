# Action-surface comparison (Chapter 3)

**Task, held fixed:** judge one real posting, Samsara `8141959` "Data Engineer" (Remote - US, asks for "4+ years
experience in a data engineering-focused role"), for the fictional persona Evan Gordon under the same prompt
contract (`prompts/judge_v1_baseline.txt`). Only the action surface changes.

**What ran:** `python3 experiments/action_surface/run_surfaces.py`, 2026-10-31 18:47 ET (persona v2.5) (start times are in each
`out/*.json`), model `claude-sonnet-5-5` via headless Claude Code (`claude -p`). Every raw result is in `out/*.json`:
returned text, cost, turn count, permission denials, and the files present in each working directory afterward.
(The same comparison ran earlier on the v1 software persona and on the v2.0–v2.4 personas, with the same pattern of results. Those
outputs were removed before submission.)

## What happened

| Surface | Tools granted | Turns | Cost (USD) | Files after | Verdict | Validator |
|---|---|---|---|---|---|---|
| **a. Paste** posting + résumé into the message | none (`--tools ""`) | 1 | 0.028 | none | relevant | VALID |
| **b. File**: Claude reads `posting.json` + `resume.json` | `Read` only | 3 | 0.032 | posting.json, resume.json (unchanged) | relevant | VALID |
| **c. Agent** fetches the posting itself and writes `state.json` | `Read`, `Write`, `WebFetch(domain:boards-api.greenhouse.io)` | 4 | 0.030 | resume.json, **state.json (written by Claude)** | relevant | VALID |
| **c-probe**: same agent asked to fetch `api.lever.co` | `WebFetch(domain:boards-api.greenhouse.io)` | 2 | 0.010 | none | (n/a) | the fetch was **denied** by the permission layer (`permission_denials` in `out/c_agent_probe_offlist.json`) |

All three gave the same verdict as the rule judge (relevant), and all three reasons cited the "4+ years" requirement
against the 5-year cap. One trial per surface: this shows the surfaces *can* agree, not that they always do.

## Read / write / send / authority / what could go wrong

| | a. Paste | b. File | c. Agent |
|---|---|---|---|
| **Can read** | only the text in the message | any file `Read` can reach from the working dir (not just the two files I named) | the files, plus anything on the allow-listed host |
| **Can write** | nothing | nothing | any path `Write` allows: the state file, and anything else in reach |
| **Can send** | nothing beyond the model call | nothing beyond the model call | HTTP requests to the allowed host (WebFetch). The probe shows other hosts are refused |
| **Authority needed** | none: the code decides what it sees | file-system read in that directory | network + file-system write. It owns the state that decides what counts as "new" |
| **What could go wrong** | the code sends the wrong posting, or a truncated one. **This happened in the v2.0 Run 2:** the judge got only the first 6,000 characters and missed a "10+ years" requirement. It can't touch anything | reads a file it wasn't meant to (e.g. a real `resume.json` sitting nearby) | writes a wrong or malformed state file, so postings are silently skipped or re-reported. Posting text could carry instructions (prompt injection) that it acts on with write access. WebFetch passes the page through a model `prompt` before Claude sees it (the probe's `tool_input` has a `prompt` field), so what it "saw" is not the raw bytes. A looser permission (any domain, or Bash) turns a judge into something that can send requests anywhere |

## Choice: the least autonomy that suffices

Why I chose surface (a)

My agent only uses the model one way: I paste the posting into a Claude call with no tools. Anything with side effects stays in plain Python.

Fetching stays in my code. jsagent/fetch.py enforces the allow-list, blocks redirects to other hosts, and saves the raw bytes before anything else runs. Those raw files are my evidence. In surface (c), WebFetch runs the page through another model first (the probe’s tool call had a prompt field), so Claude never saw the actual posting.

The state file stays in my code. Anyone should be able to recompute which jobs are “new” from the saved files. In surface (c), Claude wrote its own state.json. It worked once, but a bad write could quietly skip or repeat jobs, and a posting could slip in instructions while the model has write access.

Claude just reads text and returns JSON. It sees one posting and my persona’s résumé (no contact details), has no tools, and a validator accepts or rejects its answer. Worst case, I get a wrong judgment, which is always labeled as one and never overrides the rule.

The tradeoff

All three surfaces gave the same verdict on the test posting, so (b) and (c) added nothing my code doesn’t already do, just extra access and an injection risk. Surface (a) has its own weak spot: Claude only knows what I hand it. I saw this when the judge was cutting postings at 6,000 characters and Claude missed a “10+ years” requirement. I only caught it because I had the raw response and the rule’s record to compare.

More autonomy would only make sense for something my code can’t do, like following a link to a full job description on another site. That would mean changing the allow-list, which is a contract change, not a prompt change.

The agent uses **surface (a) for the model** and keeps everything with side effects in deterministic Python:

- **Fetching** is done by `jsagent/fetch.py`. It enforces the allow-list in code, refuses redirects off-list, and saves the
  **raw bytes**. That is the evidence. A WebFetch summary is not evidence.
- **State** (`state/seen_ids.json`) is written only by `jsagent/state.py`, after the audit passes. Whether a posting
  counts as "new" is a record anyone can recompute. It must never depend on a model's write.
- **Claude** gets one posting and a redacted résumé as text, with **no tools**, and returns JSON that a validator accepts
  or rejects. Its worst case is a wrong or rejected judgment, which is labeled as a judgment.

Surface (c) worked in this trial and was cheap. But it bought nothing the code doesn't already do, and it added
write access, network access, and an injection path. Surface (b) adds read access that isn't needed, because the code
already has the text in memory. The truncation bug shows that surface (a) has its own failure mode: the model only knows
what the code hands it. That failure was caught because the rule judge's record and the saved raw bytes were there to
compare against. **Autonomy would only be worth it** for a task the code can't do, such as following links to a full
description on another host. That would mean changing the allow-list, which is a contract change, not a prompt change.
