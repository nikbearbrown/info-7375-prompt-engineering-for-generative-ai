# Action-surface comparison (Chapter 3)

Same task each time: "Is this Klaviyo posting relevant for the persona, and why?"

| | 1. Paste one posting into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| Can read | Only the text I paste | Only the file I hand it (posting + résumé JSON) | The board API (any posting on the allow-listed host), `state/seen.json`, the persona |
| Can write | Nothing (a chat reply) | Nothing, unless I let it edit files | `runs/*-raw.json`, `runs/*-report.json`, `state/seen.json` |
| Can send | Nothing | Nothing | HTTP GET to `boards-api.greenhouse.io` only |
| Authority it needs | None | Read access to one file | Network access (one host), write access to two folders, the ability to run `claude -p` |
| What could go wrong | I paste the wrong posting; no memory of what is new | It reads a stale file; still no "new since last run" | Fetches a host it shouldn't, corrupts state (re-reports old postings or drops new ones), leaks a real résumé if one were loaded |

## What happened when I ran all three (2026-10-31, ~6:12 pm EDT)
Same posting each time: *Senior CS Compensation Analyst* (id 7989990003). Same question. Files are in `reports/action-surfaces/`.
- **1. Chat (pasted):** `way1-prompt.txt` holds the posting text and the persona pasted into one fresh `claude -p` conversation. Reply in `way1-chat-reply.txt`: "Partially relevant, but probably a weak fit". It cited the "3–5 years" and the comp-ops domain. It was prose, not my JSON format, so nothing could validate it, and nothing remembered that the posting had been seen.
- **2. File:** `way2-prompt.txt` gave `claude -p` the Read tool only, plus `posting.txt` and `resume.json`. Reply in `way2-file-reply.txt`: "only partly relevant, probably a stretch". It gave the same reasons with more detail. It still had no state, so it couldn't tell new postings from old ones, and its output still couldn't be checked.
- **3. Agent:** `agent.py run`. It fetched the board itself, saved the raw response, and wrote `state/seen.json`. Both judges ran under the contract, and the validator checked Claude's JSON (see `runs/`).

What the comparison showed: ways 1 and 2 gave a reasonable answer about **one** posting, but a hedged one ("partly relevant"). That answer can't be validated and isn't the yes/no my contract asks for. Neither way can do "new since last run". Only way 3 can, and it needs the most authority.

**My choice: 3, but fenced.** The assignment's job is "new postings since last run", which needs state and a fetch, so 1 and 2 cannot do it. I give the agent the least autonomy that still does that: one allow-listed host, GET only, writes only inside `runs/` and `state/`, a fictional persona only, and Claude itself has no tools — it only receives text and returns JSON that my validator checks. The agent never applies, messages, or logs in.

**Way 1 again, by me (2026-10-31, ~6:55 pm):** I pasted `way1-prompt.txt` into a new claude.ai chat myself. Claude said "Mostly not relevant", a weak match, with the same reasons (3–5 years, comp operations). Screenshot: `reports/action-surfaces/way1-ANISHA-screenshot.png`. It was again prose and a hedged verdict, with nothing to validate and no state.
