# Terminal evidence

These are exact captures of commands run for the film, made with `tools/capture.py`. Each `.txt` file shows the prompt
line and then the output exactly as printed. Each `.json` file adds the timing of every line, the UTC start and end, the
exit code and the Python version. The only change to the text is the home folder replaced with `~`, which is recorded in
each `.json`. `SHA256SUMS` holds every file's hash; check them with `shasum -a 256 -c SHA256SUMS`.

| File | Command | Run by | When (UTC) | Result |
|---|---|---|---|---|
| `tests-2026-11-21` | `python3 -m unittest` | Claude Code | 2026-11-21 23:43:06 | 164 tests OK, exit 0 |
| `film-normal-noapproval-2026-11-21` | `python3 -m jobwatch run --run-id film-normal-noapproval-2026-11-21` | Claude Code | 23:43:15 | `incomplete`, no approval; new 83 / 88 / 1; state unchanged; exit 3 |
| `film-normal-noapproval-check-2026-11-21` | `python3 -I checks/independent_check.py …` | Claude Code | 23:43:27 | PASS, exit 0 |
| `film-failure-2026-11-21` | `python3 -m jobwatch run --run-id film-failure-2026-11-21 --failure-control` | Claude Code | 23:43:36 | `incomplete`; the 404 board failed as expected; exit 3 |
| `film-rule-count-2026-11-21` | `grep -c not_relevant runs/film-normal-noapproval-2026-11-21/results.md` | Claude Code | 23:45:12 | 172 |
| `film-rule-relevant-2026-11-21` | `grep -c -E '\*\*relevant\*\*' …/results.md` | Claude Code | 23:45:12 | 0 (exit 1 means no match) |
| `2026-11-08-normal-1-run-by-student.txt` | the student's own approved run, `--approve-state 2026-11-08-normal-1:state/state.json` | **the student** | 2026-11-08 11:17 | `finished`, state advanced; copied unchanged from JS2's `evidence/terminal/` |

All of the Nov 21 runs used a fresh clone of the fork's `js2-loop-tools-diff` branch at `9c1db18`, in `work/jobwatch/`,
so JS2's committed evidence and state were never touched. `evidence/state-before-film-normal-noapproval.json` and
`evidence/state-after-film-normal-noapproval.json` are the state file copied just before and just after the run without
approval. `cmp` found them identical.

## How the film shows these logs (beats B08, B09, B10)

The film shows **excerpts** of these files, replayed in a drawn terminal window. The text is never retyped: the scene
data is generated from the `.json` files by `film/make_scene_data.py`, which first checks each file against
`SHA256SUMS`. The only changes are these:

- **The prompt line.** `js2-loop-tools-diff % <command>` is written by `tools/capture.py` from the run's folder name and
  command; no shell printed it. The Nov 8 log keeps its own `$`, as the student's log shows it.
- **Lines selected.** Lines are chosen, and none are edited:
  - B08 drops the 164-dot test progress line, the dashed rule, the run's status, `used …` and `evidence:` lines;
  - B10 drops the board lines, which B08 already shows, and the `evidence:` line.
- **Spaces squeezed.** In B08's three board lines, runs of spaces are collapsed to two.
- **Long lines wrapped.** Lines longer than 63 characters (the commands, and the Nov 21 status line) are wrapped at the
  window's edge, the way a 63-column terminal shows them, in PT Mono at the size GATE T requires. No character is
  added or removed.
- **The Nov 8 home path.** The `cd "/Users/…/js2-loop-tools-diff"` in the Nov 8 log is shown as
  `cd ~/…/js2-loop-tools-diff`, so no home folder or username appears on screen.

The full record of what each window kept and dropped is in `film/terminal_replay_record.json` and in §4 of
`film/PRODUCTION-NOTES.md`.
