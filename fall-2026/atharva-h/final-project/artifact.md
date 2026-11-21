# Artifact: the working system and exactly how to run it

Packet document 8 of 10. Previous: [evidence.md](evidence.md) · Next: [audit-note.md](audit-note.md)

The system is the Python package [`sponsorsql/`](sponsorsql/) plus its tests in [`tests/`](tests/). Python standard library and SQLite only. Nothing is installed.

## Toolchain

| Tool | Version checked | Needed for |
|---|---|---|
| Python | 3.9.6 (macOS `/usr/bin/python3`) and 3.14.7 (Homebrew), 2026-11-21 | everything |
| SQLite (bundled with Python) | 3.53.4 | queries, authorizer |
| `curl`, `shasum` | macOS built-ins | downloading and checking the public workbook |
| Claude Code CLI (`claude`) | 2.1.330, bundled with the Claude desktop app | **optional**, only for live model calls (`--adapter claude-cli`). It reported "Not logged in" on 2026-11-21. |

No third-party Python packages. No API key. No network access, except the one-time workbook download and the optional live adapter.

## Where each agentic part lives

| Part | File | What to look for |
|---|---|---|
| Loop (observe, decide, act, record, stop) | `sponsorsql/agent.py` | `run()`: the proposal loop with `budget.max_proposals`, the stop calls |
| Budget | `sponsorsql/config.py` (`Budget`) | 2 proposals, 2 denials, 10 s per statement, 60 s per question, row caps |
| Tools | `sponsorsql/policy.py` (`execute`, `count_rows`), `sponsorsql/gate.py` (`export_report`) | Read-only SQL; one local write behind the gate |
| Permission policy, in code | `sponsorsql/policy.py` | `check_text()`, `authorizer()`, `open_readonly()` |
| State | `sponsorsql/state.py` | `RunState.save()` writes `state/runs/<id>.json` and `state/ledger.jsonl` |
| Stop condition | `sponsorsql/state.py` (`STOP_REASONS`) | Nine reasons; none is "the model said it was done" |
| Human gate | `sponsorsql/gate.py` | `build_view()`, `view_hash()`, `decide()`, `export_report()` |

## Run it from a fresh clone

```bash
# 1. Get the code (only this folder is needed)
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai
git checkout atharva-h/final-project
cd fall-2026/atharva-h/final-project

# 2. Tests: no data needed (a synthetic database is built inside the tests)
python3 -m unittest discover -s tests -t .

# 3. Get and load the public data (252 MB download, about 70 s to load)
curl -L -o data/LCA_Disclosure_Data_FY2026_Q3.xlsx "https://www.dol.gov//media/LCA_Disclosure_Data_FY2026_Q3.xlsx"
shasum -a 256 data/LCA_Disclosure_Data_FY2026_Q3.xlsx    # must be f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3
python3 -m sponsorsql load data/LCA_Disclosure_Data_FY2026_Q3.xlsx data/fy2026q3.sqlite

# 4. Reproduce the evaluation from the saved Claude replies
python3 -m sponsorsql evaluate --db data/fy2026q3.sqlite --set evals/dev-questions.json \
  --responses evals/proposals/round2-dev-responses.json --contract evals/PROMPT-CONTRACT-v2.md \
  --out /tmp/dev-round2.json
python3 -m sponsorsql evaluate --db data/fy2026q3.sqlite --set evals/heldout-questions.json \
  --responses evals/proposals/heldout-responses.json --contract evals/PROMPT-CONTRACT-v2.md \
  --out /tmp/heldout.json

# 5. Deliberate failure cases and the controlled failure
python3 -m sponsorsql failures --db data/fy2026q3.sqlite --out /tmp/failures.json

# 6. One question through the human gate (you approve, refuse or defer)
python3 -m sponsorsql ask --db data/fy2026q3.sqlite --qid D2 \
  --question "How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?" \
  --responses evals/proposals/round2-dev-responses.json --gate interactive
```

If the branch has been merged or renamed, the folder is `fall-2026/atharva-h/final-project/` on `main`.

## Live model calls (optional)

A recorded reply can only answer the questions it was recorded for. To ask a new question with a live model, log in to the Claude Code CLI once (`claude`, then `/login`), then run:

```bash
SPONSORSQL_CLAUDE_BIN="$(which claude)" python3 -m sponsorsql ask --db data/fy2026q3.sqlite \
  --adapter claude-cli --question "Which ten cities have the most certified H-1B Business Analyst cases?"
```

On macOS with the desktop app, the bundled binary is under `~/Library/Application Support/Claude/claude-code/<version>/.../claude.app/Contents/MacOS/claude`.

**Not run for this submission:** the CLI was not logged in on 2026-11-21. The adapter is tested against a stand-in script only (`tests/test_agent.py::ClaudeCLIAdapterTests`).
