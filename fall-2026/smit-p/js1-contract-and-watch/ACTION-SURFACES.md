# Action-surface comparison (Chapter 3)

> **Authorship.** Drafted by Claude Code from runs it carried out on 2026-10-24 in Smit P.'s session. The hand labels and the decisions are Smit's (see DECISIONS.md). Every number can be recomputed with `python3 experiments/score.py`.

## Executive summary

Claude Code, in my build session, ran the same job three ways: judge one real posting
(Software Engineer, Payments, remote-US, which I labeled relevant) against the fictional
résumé. First with everything pasted into the message, then with files to read, then
letting the agent fetch the job board itself and keep its own state file. The two low-autonomy versions got the right
answer. The high-autonomy agent got it wrong. It fetched the board without the job
descriptions, had five extra commands blocked by permissions, and still returned a
confident, well-formed "not relevant" that passed my validator. More autonomy bought more
ways to fail and no better answer. The agent therefore keeps fetching and state in plain
code that I can test, and gives Claude only what it needs to judge: the posting pasted in,
no tools.

## What was run (2026-10-24, `claude-sonnet-5-5`, same system prompt `prompts/baseline.md`)

| | Surface 1: paste into chat | Surface 2: a file to read | Surface 3: agent fetches and keeps state |
|---|---|---|---|
| Command | `claude -p --tools ""` with the posting and résumé in the message. This is the CLI with no tools, standing in for "paste into a chat"; I did not use the claude.ai chat window | `claude -p --tools Read` in a directory holding `posting-8274152.json` and the résumé | `claude -p --tools Bash,Read,Write`, allowed: `Bash(curl …boards-api.greenhouse.io/*)`, Read, Write |
| Evidence | `experiments/action-surfaces/surface1-*` | `surface2-result.json` | `surface3-result.json`, `surface3-agent-workdir/` |
| Turns | 1 | 3 | 10 |
| Permission denials | 0 | 0 | **5** |
| Verdict | relevant ✓ | relevant ✓ | **not_relevant ✗** |
| Validator | ACCEPTED | ACCEPTED | **ACCEPTED** (format fine, answer wrong) |
| Cost | $0.008 | $0.042 | $0.067 |

What surface 3 actually did: it ran `curl` **without** `?content=true`, so its `raw.json`
(147 KB, vs 2.7 MB for my script's fetch) has no job descriptions. It wrote a correct
`state.json` (191 ids). The 5 denied commands (in order, from `surface3-result.json`
`permission_denials`):

1. `curl … -o raw.json; ls -la; python3 …`: chained commands
2. `python3 -I -c "…"`: not allowed
3. `jq …`: not allowed
4. `curl -s "…/jobs/8274152" | jq … | sed …`: a pipe
5. `curl -s "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs/8274152"`: a plain
   fetch of the posting on the allowed host. It was refused **because of the permission
   pattern (written by Claude Code for this run), not because of anything the agent did wrong**: the agent put the URL in
   quotes, and the rule `Bash(curl -s https://boards-api.greenhouse.io/*)` only matches
   the URL without quotes.

So the agent did try, correctly, to get the posting's content. The permission
configuration blocked it. It never saw the skills section. Its reason says it
"couldn't confirm 2 skills", yet it returned a definite `not_relevant` anyway.
Uncertainty went in as a verdict. This is itself an action-surface finding: once an
agent has authority, a too-tight permission can also produce a wrong answer, not only a
too-loose one.

## Read, write, send, authority, risk

| | Paste into chat | File to read | Agent fetches and writes state |
|---|---|---|---|
| **Can read** | only what I pasted | files in the directory it is given, or any readable path if Read is unscoped | the network (any URL `curl` reaches, unless the allow-list holds), every file it can open |
| **Can write** | nothing | nothing | files: raw response, state file, anything else Write allows |
| **Can send** | nothing beyond the model call | nothing beyond the model call | HTTP requests, so it can leak data in a URL or hit a host off the allow-list if a pattern is too loose |
| **Authority it needs** | none; I am the I/O | read permission on a folder | network + write + shell, each a permission grant |
| **What could go wrong** | I paste the wrong posting (labels on wrong postings), or paste my real résumé | it reads a file I did not mean to give it (my real résumé lives on the same machine) | wrong endpoint (happened), state written from a bad fetch (no "don't update state on failure" rule unless I write one), a corrupted seen-ids list that silently hides new jobs, off-list hosts, confident verdicts from missing data (happened) |
| **Who checks it** | me, in the message | me, plus the folder boundary | the permission system catches *actions*, nothing catches a *wrong answer from incomplete data* |

## The choice: the least autonomy that suffices

**Claude gets surface 1, the posting pasted in with no tools. The fetch, the diff, and the
state file stay in `src/watch.py`.**

- The parts that need authority (network, writing state) are exactly the parts that must
  never be wrong silently. In code, they are tested: allow-listed host, `content=true`,
  baseline reports nothing, state untouched on a failed fetch (`tests/test_contract.py`,
  class `TheWatch` and `Refuses`). In surface 3 each was a fresh improvisation, and one
  improvisation (the missing `content=true`) was wrong.
- The part that needs a model, judging relevance from text, needs no authority at all.
  Giving it a network and a shell added 9 turns, 5 blocked actions, 8× the cost, and a
  wrong answer.
- Surface 2 also worked. But reading files means pointing the model at a filesystem where
  my real résumé exists. Pasting the persona in removes that path entirely.
- The validator is not enough on its own. Surface 3's wrong answer passed it, because it
  checks that citations exist, not that the judgment is adequate. The rule verdict and my
  hand labels are what catch that.

What would change my mind: if judging needed information that is not in the posting
(for example, looking up the company's sponsorship history), that one lookup should be
another tested script feeding the paste, not a tool handed to the model.
