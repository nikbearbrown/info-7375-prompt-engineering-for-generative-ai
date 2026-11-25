# Action surface: three ways to get a Claude verdict

Draft, 2026-10-31. Same task each time: judge one posting against the
persona (personal block removed).

| | Way 1: claude.ai chat paste | Way 2: `claude -p` told to read a file | Way 3: the agent (`python3 -m agent.main`) |
|---|---|---|---|
| Status | **not verified here**: `experiment/action_surface/way1_chat.txt` is not in this folder | ran once, 2026-10-31 (`way2_file.txt`) | ran 2026-10-31 as the SEEDED run (`seeded_run/`) |
| Can read | only the text I paste | the files in the folder it runs in (a fresh temp folder holding one file); Claude Code's tools, limited by my permission settings | Greenhouse (my code fetches, not Claude), `persona_arjun_mehta.json`, the seen file; Claude reads only the prompt text for one posting |
| Can write | nothing on my machine | in principle files, if my permission settings allow its write tools; in the run it took 2 turns with 0 permission denials (writing was not tested) | my code writes only `raw/`, `state/`, `results/`, `claude_responses/` (or `--out`/`--state` paths); Claude writes nothing |
| Sends | whatever I paste, to Anthropic through the browser | the file's contents and the prompt, to Anthropic | for each new posting: id, title, location, HTML-free content, and the résumé without `personal`, to Anthropic; network fetch only to `boards-api.greenhouse.io` (code-enforced, redirects refused) |
| Authority needed | my claude.ai login | my Claude Code login and local tool permissions | my Claude Code login; network access to one host |
| What could go wrong | pasting real personal data by mistake; copy errors; no saved, repeatable record | Claude uses tools beyond reading if my settings allow; my personal Claude Code settings still load; reply format drifts (**happened**: the way 2 reply was wrapped in a ```json fence) | fenced reply becomes "no Claude verdict" (**happened**: 1 of 3 in the SEEDED run); rule false positives (e.g. "Bangalore, IN" read as Indiana, not run); Greenhouse changes its format (not run) |

## Least autonomy that suffices

Way 2-style per-posting judging inside the agent: one `claude -p` call per
new posting, from a fresh empty folder, with Claude only judging the text it
is given and returning JSON that my code validates. The fetch, the seen-ids
comparison, the rule verdict, and all file writes are done by my own code,
not by Claude. Claude needs no network, file-write, or browsing authority
for this task.

Not run: restricting Claude Code's tools further with CLI flags, and
measuring whether that changes verdicts.

## Evidence
- Way 2: `experiment/action_surface/way2_run.py` (the exact call) and
  `way2_file.txt` (timestamp, the file Claude was given, raw reply).
- Way 3: `seeded_run/SEEDED.md`, `seeded_run/run_output.txt`,
  `seeded_run/claude_responses/`.
- Way 1: `experiment/action_surface/way1_chat.txt` (to be added by me).
