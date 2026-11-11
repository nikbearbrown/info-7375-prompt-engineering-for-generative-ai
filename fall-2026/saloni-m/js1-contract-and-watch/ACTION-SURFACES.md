# Action-surface comparison (Chapter 3)

**Task, the same on all three surfaces:** judge posting 5432575008 ("Applied AI Engineer,
Startups") for Priya and name the fields used. Surface 3 also had to fetch the board and write its
own state file. All three ran on 2026-11-01 with `sh scripts/action_surfaces.sh`, each in an empty
temp directory, with `claude -p` (CLI 2.0.20, `--model claude-sonnet-5-5`). Outputs are in
`results/action-surfaces/`.

| | 1. Paste into a chat | 2. Give Claude a file | 3. Agent fetches and writes state |
|---|---|---|---|
| **Can read** | only the text in the prompt | the 2 files in its temp dir (Read only) | the web, limited to `boards-api.greenhouse.io` (WebFetch), plus its dir |
| **Can write** | nothing | nothing | files in its dir (Write) |
| **Can send** | nothing | nothing | HTTP GET requests to the allowed host |
| **Authority needed** | none beyond the model call | read access to one folder | network egress plus filesystem write |
| **Turns / cost (CLI report)** | 1 / $0.026 | 6 / $0.060 | 15 / $0.165 |
| **Verdict it gave** | not_relevant | not_relevant | not_relevant |
| **What went wrong, observed** | nothing in this run | nothing in this run | its `state.json` held **84 of 674** ids, marked `"complete": false`. The fetch tool truncated the 9.8 MB response. Its message said it saved **85** ids, but the file it wrote has 84. |
| **What could go wrong** | I paste the wrong posting or a stale copy, and nothing records which posting was judged | it reads whatever is in the folder (a real résumé left there would be read) | a silently partial state file makes the next run report hundreds of "new" postings; a looser allow-list lets it fetch anything; its account of what it did differs from what it did |

All three verdicts agree with each other and with v1 in the prompt experiment. They disagree with
the hand label (relevant), for the reason given in PROMPT-EXPERIMENT.md.

## The choice: surface 2, inside code that does the fetching

**The least autonomy that suffices is 1–2: Claude reads a posting it was given, and writes
nothing.** The parts surface 3 handed to the model are exactly the parts that have to be exact:
the fetch, the raw evidence, and the id set behind "new since last run". In this run the agent got
the id set wrong (84/674) and described its own output inaccurately (85).

`agent/watch.py` does those parts in ordinary code, which can be tested:
- a hard allow-list (`test_allow_list_refuses_other_hosts`)
- the full raw response saved to disk
- id diffing (`test_baseline_then_new_since_last`)

Claude's job shrinks to the one step that actually needs judgment: one posting in, one validated
JSON verdict out, no tools (`--disallowedTools` lists every tool). That is surface 1 in mechanics
(the posting is passed in the prompt), with surface 2's discipline (fixed inputs, nothing written).
Surface 3's autonomy bought nothing for this task: it gave the same verdict at 6× the cost of
surface 1, with a broken state file.

**Not shown:** one run per surface, one posting. The 84-of-674 truncation is one observation of the
WebFetch tool on one large response. It is not a measured failure rate.
