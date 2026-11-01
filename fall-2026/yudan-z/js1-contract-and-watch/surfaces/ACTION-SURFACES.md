# Action-surface comparison (Chapter 3)

## Executive summary

I gave Claude the same task three ways on 2026-10-30: judge Pinterest posting 8213988 against my contract for the persona. I recorded every tool call. All three reached the same verdict (`relevant`).

- **Paste (chat):** used no tools and returned a valid answer.
- **File read:** read three files and returned an answer my validator rejects.
- **Agent:** listed the folder, fetched the board four times, wrote two files, and said itself that it never had the raw bytes, so it could not have saved the evidence my contract requires.

**I chose the least autonomy that suffices.** Plain Python fetches, stores and diffs. Claude only sees pasted text, with every tool disabled.

## How each was run

All three used the Claude Code CLI in print mode (`claude -p --output-format stream-json --verbose`). The full event logs are in `surfaces/*.stream.jsonl`; summaries are in `surfaces/*.summary.json`.

| Surface | Command shape | Inputs available |
|---|---|---|
| 1. Paste into a chat | all tools disallowed; posting text pasted in the prompt (the same prompt as `agent/judge.py`) | only the pasted text |
| 2. Give Claude a file | `--allowedTools Read`, run in `surfaces/box-file/` holding only `posting.json`, `resume.json`, `CONTRACT.md` | three local files |
| 3. Let an agent fetch and write state | `--allowedTools Read Write "WebFetch(domain:boards-api.greenhouse.io)"`, run in `surfaces/box-agent/` | network (one host) + that folder |

## What happened (recorded, not described from memory)

| | 1. Paste | 2. File | 3. Agent |
|---|---|---|---|
| **Tool calls** | none | `Read` ×3 (CONTRACT.md, posting.json, resume.json) | `Glob` (listed the folder), `ToolSearch`, `Read` ×2, `WebFetch` ×4 (board list ×2, posting ×2, all on the allowed host), `Write` ×2 |
| **Could read** | the pasted text only | any file it was allowed to read (`Read` is not limited to the folder by itself) | the folder, plus anything on `boards-api.greenhouse.io` |
| **Could write** | nothing | nothing | files in its working folder (it created `seen_ids.json` and `verdict.json`) |
| **Could send** | nothing outside the model call | nothing outside the model call | HTTP requests to the allowed host (its prompts to `WebFetch` were sent along with the URLs) |
| **Authority needed** | none beyond the model call | read access to my files | network access and write access on my machine |
| **Verdict** | relevant | relevant | relevant |
| **Passed my validator?** | **yes** | **no**: `posting_fields` contained `location.name`, not an allowed field | **no**: same `location.name` problem in `verdict.json` |
| **State it wrote** | — | — | `seen_ids.json` with 170 ids; I checked them against my agent's 2026-10-30 baseline and found 170/170 the same |
| **Evidence** | — | — | none: "my tools never had the raw bytes", so `WebFetch` returned a model-processed view of the JSON, not the response |

## What could go wrong

- **Paste:** I can paste the wrong posting or a truncated one. This happened: my 6,000-character cut hid a sponsorship sentence. The model cannot notice what it never saw.
- **File:** `Read` is a capability, not a folder boundary. In a less careful setup it could read my real résumé if the path were known. Its answer drifted from my output contract even with the contract file in front of it.
- **Agent:**
  - It chose its own requests: it read the board twice "because the response was too long" and fetched the posting twice.
  - The ids it wrote passed my check here, but I could only check them because my own deterministic watcher had the raw response. Its state file is a model's summary of a response it never held.
  - It also used tools I had not listed (`Glob`, `ToolSearch`).
  - With a broader allow-list it could fetch other hosts.

## My choice: the least autonomy that suffices

The task needs four things: fetch one host, keep the raw bytes, remember ids, and judge each new posting.

- The first three are **deterministic** and need no model at all. Python does them (`agent/watch.py`), with a hard allow-list check before any request and the raw response saved byte-for-byte.
- Only the judgment needs Claude. It gets the **paste surface**: the posting text inside the prompt, every tool disallowed, and a validator on the way out (`agent/judge.py`).
- So Claude can read only what I hand it, write nothing, and send nothing.

The agent surface gave the same verdict, but it could not satisfy my contract's evidence requirement and it needed write access and network authority to do it.

## Note on the raw logs

On 2026-10-31 I replaced my Windows user name with `<user>` in the three `*.stream.jsonl` files (2 occurrences per file, all inside local file paths), for privacy. I also removed the first line of each log, the `system init` line (local paths, session ids, my CLI's tool and connector inventory), which is not evidence for this comparison. No assistant, user or result line was changed.
