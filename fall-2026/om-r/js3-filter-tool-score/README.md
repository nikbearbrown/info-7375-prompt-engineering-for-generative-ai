# Job-Search Agent 3 — Filter, Tool, Score

**Om Raut** · INFO 7375, Fall 2026 · Job-Search Agent 3 (Chapters 7–9) ·
GitHub folder: `fall-2026/om-r/js3-filter-tool-score/`

This agent runs on postings collected by Job-Search Agent 2's loop, which
it imports unchanged. The candidate is Priya Nair from JS1's `resume.json`,
a fictional persona. It adds four things:

- **A filter with stated rules.** Every rejection carries a reason, and
  every quote is checked against the posting text.
- **A hand-judged audit of what the filter rejected.** Om labeled 90 rows
  covering 88 distinct postings.
- **A Chapter 9 experiment with a single held-out read.** It promoted rule
  4 to FILTER.md v1.1.0.
- **Scoring with Claude.** A source-grounded shortlist, exposed as one
  MCP-shaped tool server.

The spec is `FILTER.md`, written before any code. Its v1.1.0 amendment is
dated 2026-11-22 and was written after the experiment.

## Language and toolchain

- **Python 3.11** (tested on 3.11.15).
- **Standard library everywhere except one lazy import.** I checked this
  by parsing every import in `js3/`, `tests/` and `tools/` with `ast` and
  comparing against `sys.stdlib_module_names`.
  - Standard-library modules used: `argparse`, `collections`, `datetime`,
    `hashlib`, `html`, `importlib`, `json`, `os`, `pathlib`, `random`,
    `re`, `runpy`, `subprocess`, `sys`, `tempfile`, `unittest`.
  - Other imports: the project's own packages (`js3`, `tests`); `agent`,
    which is JS2's package (imported by `js3/collect.py`) and, in a
    subprocess, JS1's (`tools/rule1_vs_js1.py`); and `anthropic`.
- **Third-party: `anthropic==0.39.0`, needed only for the [key] steps.**
  It is imported inside `js3/shortlist.py:get_client()` and nowhere else,
  so every [offline] and [live] step runs without it installed. There is
  no `requirements.txt`; install it with `pip install anthropic==0.39.0`
  before a [key] step.
- **Sibling projects this one reads:**
  - JS2, at `$JS2_ROOT` (default `~/Desktop/js2-loop-tools-diff`), for
    collection.
  - JS1, at `$JS1_ROOT` (default `~/Desktop/js1-contract-and-watch`), for
    the rule-1 cross-check and for `resume.json`.
  - Two MCP tests (`ToolsCall.test_relevant_posting_is_judged_...` and
    `test_adhoc_title_and_content`) also read JS1's `resume.json`. With
    `JS1_ROOT` pointing nowhere, the suite reports 89 OK and 2 errors.
- **Network hosts:**
  - Collection reaches `boards-api.greenhouse.io` and `api.lever.co`
    through JS2's loop, which enforces JS2's allow-list.
  - The shortlist and the MCP server reach `api.anthropic.com` through the
    SDK. JS3 itself does not enforce a host allow-list (TOOL-SERVER.md
    section 5).
- **Claude:** model `claude-opus-5-5`, effort `medium`, prompt version
  `shortlist-v1`, no fallback model.
- **Tests:** `unittest`, 91 tests:

  | File | Tests |
  |---|---|
  | `test_filter_rules` | 15 |
  | `test_wrong_versions` | 11 |
  | `test_reject_audit` | 8 |
  | `test_rule4` | 22 |
  | `test_shortlist` | 18 |
  | `test_mcp_server` | 17 |

## The evidence-commit exception

JS1 and JS2 never committed `evidence/`. A run regenerates the raw board
responses, about 15 MB of them, so committing them added size and nothing
checkable.

JS3 makes **one deliberate exception**: the raw responses behind run
`20261121T132140Z` are committed (`a1988cb`, with the reason in
`.gitignore`). Every other run's evidence is still ignored.

The reason is that this run is no longer just an input that can be fetched
again. It is the ground truth that the rest of the submission is checked
against:

- **The reject audit.** Om's 90 hand labels and reasons
  (`logs/reject_audit/*_draft.md`) are judgments about specific posting
  text. Anyone checking a label, or a quote attributed to Om, needs exactly
  the text he read.
- **The Chapter 9 experiment.** The dev/held-out split and both
  measurements run over those exact 88 postings.
- **The shortlist and the MCP transcripts.** A claim is labeled
  `supported` only if its quote is an exact substring of the posting. A
  reviewer can check that label only against the same posting.

A future live fetch would not give the same text. JS2 documented the board
drift: postings are added, removed and edited between runs. The fresh-clone
check on 2026-11-23 showed it again: gitlab 245 / stripe 779 / palantir 307,
against 246 / 778 / 308 in the committed run. Committing the evidence is
what makes the audit, the experiment and the grounding checkable, rather
than just runnable again.

## Exact commands to reproduce everything, in order

These are the commands behind this submission, in the order they were first
run. The order follows the numbered `logs/` files and the git history.

Tags:
- **[offline]**: no network.
- **[live]**: fetches the real boards.
- **[key]**: calls the Claude API. It needs `ANTHROPIC_API_KEY` and is
  billed.

> **Run these in a fresh clone, not in this folder.** Several steps check
> out the commit where something was first built, or delete a module to
> show its tests failing first. Each one restores the files afterwards.
> Some steps rewrite committed outputs; in a clone, `git status` then shows
> whether they came out byte-identical.
>
> **Verification.** Every [offline] and [live] command below was run end to
> end, in this order, in a fresh clone on 2026-11-23 (UTC), and worked as
> written. The clone was made from a bundle of this repository's history.
>
> **The [key] commands were not re-run in that check.** They are the
> commands Om ran in his own terminal (logs 21, 22, 29, 30). In the clone,
> without a key, the shortlist stops with `MissingAPIKey` and writes
> nothing, and the MCP client's relevant-posting call returns `isError`.
>
> **Fresh-clone differences, all expected:**
> - Step 2 is a new live baseline. It writes a new
>   `logs/run_<stamp>.json` and new `evidence/`, with counts that drift
>   from the committed run. Every later step names the committed run,
>   `logs/run_20261121T132140Z.json`, explicitly.
> - Steps 3, 4, 5 and 6 regenerate committed files: the filter-run JSON,
>   the BLANK worksheets and draw manifest, `split.json`, and
>   `dev_measurement.json`. In the clone, all came out byte-identical
>   (`git status` clean).
> - The reject-audit draw prints `wrote ...` for **every** file in
>   `logs/reject_audit/`, Om's `*_draft.md` worksheets included. It does
>   not write those files (`js3/reject_audit.py:244`). It only lists the
>   directory, which makes the message misleading. This was found while
>   writing this README and left as is.
> - Step 7 appends a second line to the **clone's**
>   `logs/experiment/heldout_access.log`, and the step restores it
>   afterwards. Never run it in this folder: the committed log records
>   exactly one held-out read, and a second line there would make that
>   record false. `heldout_measurement.json` came out byte-identical.
> - The test counts in logs 23 and 24 are 15. Two tests were added later
>   for the schema fix (logs 27–28), so the same commands now run 17.
>
> **Reconstructions.** Four pre-fix states were never committed: in each
> case, the fix went in before the first commit of that file. Their logs
> are 05a, 16, 26a and 27. The commands for them recreate the pre-fix code
> from the change described in FRICTIONAL.md and TOOL-SERVER.md, run it,
> and restore the file. In the clone, each reproduced the failure in its
> log.

```
git clone js3-history.bundle js3 && cd js3
```

**0. The spec, written first.** `FILTER.md`, commit `9426989`. No command.

**1. Wrong-version tests: no implementation, then the deliberately wrong
stubs, then the real filter and grounding.** [offline] Logs 00–03.
```
git checkout -q 0274afb && python3 -m unittest -v tests.test_wrong_versions          # logs/00: FAILED (errors=2), no js3.filter yet
JS3_FILTER_IMPL=js3.wrong_stub_filter JS3_GROUNDING_IMPL=js3.wrong_stub_grounding python3 -m unittest -v tests.test_wrong_versions
                                                                                      # logs/01: FAILED (failures=13)
git checkout -q 9e2c27a
JS3_FILTER_IMPL=js3.wrong_stub_filter JS3_GROUNDING_IMPL=js3.wrong_stub_grounding python3 -m unittest -v tests.test_wrong_versions
                                                                                      # logs/01b: FAILED (failures=15), blank-quote test added
python3 -m unittest -v tests.test_wrong_versions                                      # logs/02: OK (11 tests)
python3 -m unittest -v                                                                # logs/03: OK (26 tests at this commit)
git checkout -q main
```

**2. Collect through JS2's loop, unchanged.** [live] Log 04. Needs JS2 at
`$JS2_ROOT`.
```
python3 -m js3.collect --approve-new-boards            # logs/04: EXIT finished, BASELINE x3, 6 requests
```

**3. Filter run over the committed run, the relative-path crash, and the
rule-1 cross-check against JS1.** [offline] Logs 05, 05a, 06. The
cross-check needs JS1 at `$JS1_ROOT`.
```
python3 -m js3.run_filter logs/run_20261121T132140Z.json
                                                       # logs/05: total 1332, relevant 20, rejected 1312, insufficient_data 0
sed -i '' 's/(Path(argv\[0\]) if argv else max((ROOT \/ "logs").glob("run_\*.json"))).resolve()/(Path(argv[0]) if argv else max((ROOT \/ "logs").glob("run_*.json")))/' js3/run_filter.py \
  && python3 -m js3.run_filter logs/run_20261121T132140Z.json; git checkout -q -- js3/run_filter.py logs/
                                                       # logs/05a (reconstruction: .resolve() removed): ValueError ... not in the subpath
python3 tools/rule1_vs_js1.py logs/run_20261121T132140Z.json
                                                       # logs/06: JS1 rule relevant 22, JS3 rule 1 pass 22; disagreements 0
```
`sed -i ''` is the macOS/BSD form; on GNU sed use `sed -i`.

**4. Reject-audit draw: tests first, the first draw (B = all 156), then
the reduction to B = 2 forced + 38 sampled.** [offline] Logs 07–12.
```
git checkout -q 340dfa9 && rm js3/reject_audit.py && python3 -m unittest -v tests.test_reject_audit; git checkout -q -- js3/reject_audit.py
                                                       # logs/07: FAILED (errors=6), module does not exist yet
python3 -m unittest -v tests.test_reject_audit         # logs/08: OK (6 tests)
python3 -m js3.reject_audit logs/run_20261121T132140Z.json
                                                       # logs/09: seed 20261121, A 30, B 156, C 20; 202 to hand-judge
git clean -fdq -- logs/reject_audit                    # remove the first draw's untracked worksheets before checkout
git checkout -q dc47bf1 && git checkout -q 340dfa9 -- js3/reject_audit.py && python3 -m unittest -v tests.test_reject_audit; git checkout -q dc47bf1 -- js3/reject_audit.py
                                                       # logs/10: FAILED (errors=8), new group-B tests vs the old module
python3 -m unittest -v tests.test_reject_audit         # logs/11: OK (8 tests)
git checkout -q main
python3 -m js3.reject_audit logs/run_20261121T132140Z.json
                                                       # logs/12: A 30, B 40 (2 forced + 38 of 154), C 20; 88 distinct
git status --short logs/reject_audit                   # empty: BLANK worksheets + draw_manifest.json byte-identical to 6af4411
```
The BLANK worksheets were committed (`6af4411`) before any judging. Om's
judged worksheets and REJECT-AUDIT.md followed in `3f25469`. That step was
hand judgment, and no command reproduces it.

**5. Chapter 9: catalog and dev/held-out split before rule 4 exists, then
dev-only evidence.** [offline] Logs 13–14.
```
python3 -m js3.experiment split                        # logs/13: seed 7375; DEV 53 (12 relevant), HELDOUT 35 (8 relevant)
git status --short logs/experiment                     # empty: split.json byte-identical to 277b7d6
python3 tools/dev_evidence.py                          # logs/14: dev split only
```

**6. Rule 4, test-first, at the commit where it was locked.** [offline]
Logs 15–17b.
```
git checkout -q 8650e84
rm js3/rule4.py js3/filter_v110.py && JS3_RULE4_IMPL=js3.wrong_stub_rule4 python3 -m unittest -v tests.test_rule4; git checkout -q -- js3/
                                                       # logs/15: FAILED (failures=19, errors=4), no-op stub, real modules absent
sed -i '' 's/at\\s+least\\s+|/at\\s+least|/' js3/rule4.py && python3 -m unittest -v tests.test_rule4; git checkout -q -- js3/rule4.py
                                                       # logs/16 (reconstruction: \s+ before the number removed): FAILED (failures=2)
python3 -m unittest -v tests.test_rule4                # logs/16b: OK (22 tests)
python3 -m js3.experiment measure dev                  # logs/17b: DEV 53; dev_measurement.json byte-identical
git checkout -q main
```
Log 17 came from the same rule before the full-text Palantir diagnostic was
added to the report. That intermediate code was never committed, so the
clone reproduces log 17b.

**7. The single held-out read.** [offline] Log 18. **Clone only**: see the
note above.
```
python3 -m js3.experiment measure heldout              # PermissionError: held-out labels are locked (the guard)
JS3_FINAL_HELDOUT=1 python3 -m js3.experiment measure heldout
                                                       # logs/18: HELDOUT 35; heldout_measurement.json byte-identical
git checkout -q -- logs/experiment/                    # drop the clone's second access-log line
```
EXPERIMENT.md sections 7–8 and the FILTER.md v1.1.0 amendment
(`9298665`) are interpretation, not commands.

**8. Source-grounded shortlist.** [offline] logs 19–20, then [key] logs
21–22.
```
rm js3/shortlist.py && python3 -m unittest -v tests.test_shortlist; git checkout -q -- js3/shortlist.py
                                                       # logs/19: FAILED (errors=18), module does not exist yet
python3 -m unittest -v tests.test_shortlist            # logs/20: OK (18 tests)
export ANTHROPIC_API_KEY=...                           # [key] in your own terminal; never commit or paste it
python3 -m js3.shortlist 2>&1 | tee logs/NN_shortlist_live_run.txt
                                                       # logs/21: five 401 JUDGMENT_ERRORs (invalid key), no model output
                                                       # logs/22: 5 candidates, 38 claims (29 supported, 5 contradicted, 4 insufficient)
```
Each [key] run writes `logs/shortlist/shortlist_<stamp>.json` and one
transcript per call, `logs/shortlist/transcripts/<board>_<id>_<n>.json`. It
never overwrites, and it is not deterministic: a re-run gives different
claims. The committed run that SHORTLIST.md analyzes is
`shortlist_20261122T234058Z.json`.

**9. MCP-shaped tool server.** [offline] logs 23–28, then [key] logs
29–30.
```
rm js3/mcp_server.py && python3 -m unittest -v tests.test_mcp_server; git checkout -q -- js3/mcp_server.py
                                                       # logs/23: FAILED (failures=1, errors=14) of 15 then; 1 + 16 of 17 now
python3 -m unittest -v tests.test_mcp_server           # logs/24: OK (15 then, 17 now)
python3 tools/mcp_client.py                            # logs/25: no key; cross-check IDENTICAL; relevant call -> isError
sed -i '' '/sys.path\[0\] = /d' tools/mcp_audit.py && python3 tools/mcp_client.py --audit; git checkout -q -- tools/mcp_audit.py
                                                       # logs/26a (reconstruction: import-path fix removed): server crashes, JSONDecodeError
python3 tools/mcp_client.py --audit                    # logs/26: audited, no key; IDENTICAL; every write INSIDE logs/mcp
python3 - <<'EOF'
import re, pathlib
p = pathlib.Path('js3/mcp_server.py'); s = p.read_text()
new = '    "oneOf": [{"required": ["board", "id"]}, {"required": ["title", "content"]}],\n}'
s2 = re.sub(r'    "oneOf": \[\n.*?\n    \],\n\}', lambda m: new, s, count=1, flags=re.S)
assert s2 != s; p.write_text(s2)
EOF
python3 -m unittest -v tests.test_mcp_server.InputSchemaModesAreExclusive; git checkout -q -- js3/mcp_server.py
                                                       # logs/27_mcp_schema_gap_test_before_fix (reconstruction: pre-fix oneOf): FAILED (failures=2, errors=2)
python3 -m unittest -v tests.test_mcp_server.InputSchemaModesAreExclusive
                                                       # logs/28: OK
export ANTHROPIC_API_KEY=...                           # [key]
python3 tools/mcp_client.py --audit 2>&1 | tee logs/NN_mcp_client_session_audited_with_key.txt
                                                       # logs/29: 401 from a corrupted key copy, handled as isError
                                                       # logs/30: scored call, verdict relevant, 1 contradiction
```
Each client session writes `logs/mcp/client_<stamp>.jsonl` and
`logs/mcp/server_<stamp>_<pid>.jsonl`, and the client checks the two
against each other. A [key] session also writes
`logs/mcp/judge_transcripts/<board>_<id>_<n>.json`. Two files are numbered
27; TOOL-SERVER.md section 4.6 explains why. Section 4.3 covers the deleted
log from the environment-leak bug.

**10. The full suite today, and the key-leak checks.** [offline]
```
python3 -m unittest                                    # Ran 91 tests, OK
git log --all -p | grep -ic 'sk-ant[-]'                # 0: no API-key prefix anywhere in history
grep -rn 'sk-ant[-]' . --exclude-dir=.git | wc -l      # 0: none in the tree
```

## What actually ran vs. what's proposed

Everything above actually ran, between 2026-11-21 and 2026-11-23 (UTC). The
[offline] and [live] steps ran again end to end in a fresh clone on
2026-11-23. The real output is in `logs/`.

Nothing here is a `[TODO]` stub. The filter, rule 4, the grounding check,
the shortlist and the MCP server are all used on real postings.

Real data: one live collection run (`20261121T132140Z`, 1,332 postings
from gitlab, stripe and palantir), and Om's 90 hand labels. Live Claude
output:
- 5 shortlist judgments (log 22).
- 4 MCP judge transcripts (`logs/mcp/judge_transcripts/*_1..4.json`).
- The failed 401 attempts (logs 21 and 29) are real API responses.

**Constructed input, each labeled in its own file:**

- **Empty-content fixtures.** In `tests/test_wrong_versions.py`, postings
  101–106 have empty, null, whitespace-only or tag-only content. Two of
  them have a title that alone would pass rule 1. Each must come out as
  `insufficient_data` and stay out of the reject audit's sampling pool.
  Posting 200 is a constructed non-matching control. All use
  `example.invalid` URLs.
- **Rule and draw fixtures.** `tests/test_filter_rules.py` and
  `tests/test_reject_audit.py` say "Constructed fixtures only" in their
  docstrings. The reject-audit fixture pool is small, so its tests draw
  `n_near=3`.
- **Graduation and clearance fixtures.** `tests/test_rule4.py`:
  - "Must be graduating in December 2026 or Spring 2027." (graduation);
  - "Security clearance or the ability to obtain a clearance."
    (clearance);
  - "Graduating in 2028. Active security clearance required." (both).

  Each must flag and never reject. Two of these sentences match real text
  in **B032**, the one held-out hand-relevant posting: "Security clearance
  or the ability to obtain a clearance." and "Graduating in 2028." Decision
  B was made with B032's text already known (EXPERIMENT.md section 3). B032
  itself is real committed evidence, not a fixture. The fact that rule 4
  did not fire on it is in log 18.
- **Fake Claude.** `FakeClient` and `FakeRaw` in `tests/test_shortlist.py`
  return canned `claims_json(...)` bodies. They are reused by
  `tests/test_mcp_server.py`. No test calls the network.
- **Ad hoc postings.** In the MCP tests, `{title, content}` postings use
  "AI Engineer" plus a real GitLab quote. Their id is a sha256 of the text,
  and `source` is `"adhoc"`.
- **Deliberately bad requests.** `tools/mcp_client.py` sends four probes:
  an unknown tool `delete_everything`, mixed `{board, id, title}`
  arguments, `{this is not json`, and a JSON-RPC batch. The tests send
  similar ones.

**Deliberately wrong, and labeled as such:**

- `js3/wrong_stub_filter.py`, `js3/wrong_stub_grounding.py` and
  `js3/wrong_stub_rule4.py` exist only so the tests can be shown failing.
  Each says so in its docstring, and nothing outside the tests imports
  them.
  - The filter stub sends empty postings to `rejected`.
  - The grounding stub labels every claim `supported` without checking it.
  - The rule-4 stub never fires.
- The four reconstructions above (05a, 16, 26a, 27) apply the pre-fix code
  to a working copy and restore the file straight after. They never
  produce a commit.

**Proposed, not built.** None of the following is enforced in the server
(TOOL-SERVER.md section 5):
- a call budget;
- a spending limit;
- an input size cap;
- a host allow-list.

A clean v1.1.0 code release is also left for later: the code's `VERSION`
remains `1.1.0-candidate`. The extensions FILTER.md's amendment lists as
"explicitly not done" are also unbuilt:
- adding "Senior";
- a lower year threshold;
- an out-of-stack detector;
- reading Lever `lists`.

## Files in this submission

| Path | What it is |
|---|---|
| `FILTER.md` | The spec, written before any code, with its dated v1.1.0 amendment (rule 4) |
| `js3/` | `filter.py` (v1.0.0 rules 1–3), `rule4.py` and `filter_v110.py` (v1.1.0), `grounding.py`, `postings.py`, `collect.py` (JS2's loop, unchanged), `run_filter.py`, `reject_audit.py`, `experiment.py` (split and guarded held-out read), `shortlist.py` (Claude judgment), `mcp_server.py` and `minischema.py`. Also the three deliberately wrong stubs |
| `tests/` | 91 `unittest` tests: wrong versions, filter rules, reject-audit draw, rule 4, shortlist, MCP server (including a real stdio subprocess session) |
| `tools/` | `rule1_vs_js1.py` (cross-check against JS1), `dev_evidence.py` (dev-only design evidence), `mcp_client.py` (minimal MCP client with a wire-log cross-check), `mcp_audit.py` (PEP 578 audit wrapper; never records child environments) |
| `evidence/` | Raw board responses for run `20261121T132140Z` only: the deliberate exception (`a1988cb`) |
| `logs/` | Every test and run output in order (`00`–`30`, with 05a, 01b, 16b, 17b, 26a, and two 27s). Also `run_*.json`, `filter_run_*.json`, `reject_audit/` (draw manifest, BLANK and judged worksheets), `experiment/` (split, measurements, `heldout_access.log`), `shortlist/` and `mcp/` (wire logs and judge transcripts) |
| `FRICTIONAL.md` | What broke or changed during the build, with corrections |
| `REJECT-AUDIT.md` | The hand audit of the filter's rejects and passes (groups A, B, C) |
| `EXPERIMENT.md` | Chapter 9: numbers catalog, split, design problems, rule 4, the held-out result and what it can't show, the promotion decision |
| `SHORTLIST.md` | Source-grounded shortlist: prompt contract, real output, relevance vs. entailment, the limits of abstention |
| `TOOL-SERVER.md` | The MCP server: wire format, real transcripts, found-then-fixed items, evaluation of my server and of the reference filesystem server |
| `SIGNOFF.md`, `SIGNOFF-DRAFT.md` | Om's sign-off, and the skeleton it was written from |
| `SOURCES.md` | What I used, what I wrote and decided, what Claude contributed, and the AI use disclosure (Claude Code and a claude.ai chat) |
| `js3-history.bundle` | The build's full git history (every commit hash cited in these files), for `git clone js3-history.bundle js3` |

# Sign-off — Job-Search Agent 3

## Checked

- **Filter and grounding.** The wrong-version tests failed against both deliberately wrong implementations -- 13 failures on the first run against the stubs, 15 after the blank-quote test was added -- and passed against the real implementation. A separate rule-1 cross-check against JS1's original rule.py ran on all 1,332 postings: both agreed on all 22 relevant matches, zero disagreements. The full suite recorded 91 passing tests. See tests/test_wrong_versions.py, logs 00-03, logs/06_rule1_vs_js1_crosscheck.txt.

- **Reject audit.** I hand-judged 90 rows across groups A, B, and C (88 distinct postings), with no AI assistance on the judgments themselves -- every label and reason is my own. Group B used 38 sampled postings plus 2 forced rule-2 rejects; the BLANK worksheets were committed before any judging. The filter passed all 20 Group C postings as relevant; under my own labeling rule, only C03 held up -- the other 19 were false positives for Priya's specific fit, several of them genuine AI/ML roles whose experience requirements she doesn't meet. See logs/reject_audit/draw_manifest.json and REJECT-AUDIT.md.

- **Rule 4.** The dev/held-out split and the design decisions were committed before rule 4 existed. The tests caught a real regex bug (fixed before any measurement), and rule 4 was locked after dev-only measurement. The held-out label set was read exactly once, logged, and the raw result was committed before any interpretation was written. See EXPERIMENT.md, logs 15-18, commits 277b7d6, 46e7782, 8650e84, ad9ff05.

- **Shortlist.** I ran the live shortlist myself with my own key. The first attempt failed with five 401 errors from an invalid key; the retry, with a working key, returned five valid responses with 38 total claims -- 29 supported, 5 contradicted, 4 insufficient. I checked and confirmed zero fabricated quotes across all five. See SHORTLIST.md and logs 21-22.

- **MCP server.** Client transcripts matched the server's wire logs exactly in every recorded session. The schema regression test failed before the oneOf fix and passed after. During a live audited session, the audit wrapper itself leaked my API key into a local log; Claude caught it before anything was staged. I made the call to delete the affected log and rotate the key, rather than redact it -- and when the replacement key's first copy also failed, I caught the cause myself (a stray bracket character) by checking the key's prefix before retrying. See TOOL-SERVER.md sections 4.1 and 4.3-4.4, logs 25-30.

## How

For the filter, the rule-1 cross-check, and the Chapter 9 experiment, I specified the two wrong versions to test, the B032 must-not-fire case, and the schema-gap cases; Claude wrote the actual test and tool code, and I verified the results against the committed test logs and output. The live runs I personally executed with my own key are logs 21, 22, 29, and 30.

For the reject audit, every one of the 90 hand labels and reasons is my own writing, with no AI drafting -- AI helped only with the labeling rule itself, not with any individual label or reason sentence. That help came from a separate claude.ai chat (as best I recall), not from this Claude Code session, which never saw the worksheets until they arrived already judged. I used Claude to parse the worksheets, check every quote it attributed to me against the committed posting text, and draft REJECT-AUDIT.md's structure. I made the call on how to handle the Group B sample reduction, and I asked specifically for the Group C count to be stated plainly rather than softened.

## Not checked

- Rule 4 against the full Palantir text (Lever's lists field, not just descriptionPlain) -- the audit found 26 affected postings where this would matter.
- Rule 4 against a genuinely fresh set of postings whose labels neither Claude nor I had already seen before designing the rule.
- Whether any of these results carry over to a different collection date, a different candidate, or a second, independent labeler.
- The tool server's behavior under a call budget, a spending limit, an input size cap, or a host allow-list -- none of these are enforced in the server itself. The origin of one MCP session (00:36Z) found in the logs is also unresolved.
- The filesystem-server evaluation is based on reading its published source, not on running it myself.

## Not claiming

Held-out precision on the filter's relevant bucket went from 0/8 to 0/3 -- fewer postings passed, but none were true positives before or after, so this isn't evidence the rule improved precision; it's a structural artifact of held-out having zero true positives to begin with. The one hand-relevant posting in held-out (B032) didn't trigger rule 4, but one data point says very little about how often the rule would wrongly reject a good match.

The 19/20 figure in Group C is exact only for this one collection run and this one persona's fit -- Groups A and B are samples with real sampling error, and A and B overlap and share a seed, so none of these numbers generalize into a miss rate for the full reject pool.

A quote taken directly from a posting can still fail to back up the verdict it's attached to. The shortlist shows this both ways: on 8704363002, a generic boilerplate sentence drove a contradiction flag that didn't reflect anything substantive; on 8175656, the verdict stayed "relevant" even though one of its own supported claims quoted a 2-year experience requirement the posting itself states as a gap.

**Signed: Om Raut, 2026-11-23**

## Driver's seat

| Task | Where I had help | What I did | Why I kept that decision | Evidence |
|---|---|---|---|---|
| Filter contract | Claude implemented the contract and drafted the v1.1.0 amendment. | I set what the amendment had to cover, including why rule 4 was promoted, its known gaps, and keeping the Palantir field issue out of scope for this change. | I wanted the rule and its exceptions written down so I could compare them against the output. | 9426989, 9298665, FRICTIONAL.md entry 1 |
| Filter and rule-1 cross-check | Claude wrote the wrong stubs, tests, filter, grounding code, and the JS1 cross-check. | I specified the wrong behaviors the tests had to catch. | Passing the final version only tells me so much if the tests also let the wrong version through. | 0274afb, 9e2c27a, 667d6dc, logs 00-06 |
| Raw evidence | Claude committed this run's raw posting evidence as an exception to the earlier ignore convention. | I used the saved run as the source for the audit. | The exact posting text matters when a label or a quote gets challenged. | a1988cb, .gitignore |
| Reject sampling | Claude generated the seeded draws and blank worksheets and redrew B on my instruction. | I chose the 2 forced + 38 sampled approach and kept the ambiguity in the write-up rather than smoothing it over. | I wanted both rule-2 cases inspected without quietly mixing them into the random draw. | 6af4411, draw manifest, FRICTIONAL.md entry 4 |
| Reject judgments and report | Claude parsed my worksheets, checked every quote attributed to me, and drafted the report structure. | Every one of the 90 labels and reasons is my own writing. I set the task and asked for the exact Group C count to be stated plainly. | I wanted the count to say whose search we were judging. Several of the rejected roles really did involve AI engineering. | logs/reject_audit/*_draft.md, REJECT-AUDIT.md, 3f25469 |
| Experiment split | Claude computed the split and built the guarded held-out reader. | I went through the prior-exposure limitation honestly and kept it in the interpretation rather than hiding it. | I'd already seen the labels, so I couldn't honestly treat the experiment as blind. | 277b7d6, EXPERIMENT.md sections 1-2 |
| Rule 4 design | Claude implemented rule 4 test-first, fixed the regex bug, and added the full-text Palantir diagnostic. | I set the design decisions and specified that B032 must not trigger rule 4. | I wanted to settle the rule before seeing what the locked version did on held-out. | 46e7782, 8650e84, logs 14-17b |
| Held-out decision | Claude ran the guarded read, committed the result, and drafted the interpretation. | I specified what the promotion and amendment had to account for, and confirmed the prior-exposure and overlapping-interval caveats stayed in. | Fewer postings passing was an observable change. Better precision was a separate claim the numbers didn't actually support. | ad9ff05, 9298665, heldout_access.log |
| Shortlist | Claude wrote the prompt contract, validator, and abstention check, and flagged where my planned example didn't match the real output. | I ran the failed attempt and the live retry myself, with my own key. | The live output showed where the model's verdict and the text it quoted could genuinely pull in different directions. | SHORTLIST.md, logs 21-22 |
| MCP server | Claude built the server, client, and audit wrapper, and found and fixed the oneOf gap. | I specified the schema test cases and ran the live sessions in logs 29 and 30 myself. | I wanted to see what actually happened in a live call, including what the audit actually recorded. | TOOL-SERVER.md, logs 27-30 |
| Key incident | Claude's own audit wrapper caused the leak, then spotted it before anything was staged, fixed the hook, and verified the fix with a fake secret. | I chose deletion over redaction, rotated the key, and caught the stray bracket in the replacement key myself before retrying. | It was my key, so the call on what to do with the affected log and credential was mine to make. | TOOL-SERVER.md sections 4.3-4.4, logs 29-30 |
| This sign-off | A claude.ai chat conversation helped draft the wording from a scaffold. It is the same conversation I used to plan and draft this submission's work throughout, separate from the Claude Code sessions that did the actual implementation. | Final review and signature are mine. | The signature is my call. | This document |
