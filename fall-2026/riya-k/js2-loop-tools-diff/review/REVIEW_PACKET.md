# Review packet: the Intern exclusion (Chapter 6)

**The change I asked Claude Code to make:** exclude internship postings from the relevance rule.
**Why this change:** my JS1 hand check on Databricks posting 6866538002 showed the rule rates an internship
as relevant, and the TA's JS1 feedback (2026-11-09) asked me to add an Intern exclusion.
**My rule decision (2026-11-09, in chat):** whole-word `Intern` and `Internship` only. Co-op and Apprentice are
left out on purpose (see "What the test still misses").

## Order of events (each step is a commit, so the order can be checked)

| Step | Commit | What |
|---|---|---|
| 1. Defect seen on a real posting | `2b7c83d` (raw response) | live run day 1, 2026-11-09 20:32 UTC; `runs/raw/greenhouse-databricks-20261109T203203Z-live-day1-a1.json` contains 6866538002 |
| 2. Test written **before** the patch | `fdae00e` | `tests/test_intern.py`, `tests/fixtures/databricks-6866538002.json` (the real posting, copied unchanged), `review/reproduce.py` |
| 3. Exact prompt committed **before** running it | `6e69b42` | `review/patch_prompt.md` |
| 4. I ran the reproduce + red test | (no file change) | output below |
| 5. Claude Code patched it (separate headless session) | this commit | `review/claude_patch_response.json` (raw response), `review/patch.diff`, `review/patch_session_tool_calls.md` |
| 6. I ran the tests myself and decided | this commit | output and decision below |

## 1. The defect, reproduced (command I ran, 2026-11-09, before the patch)

```text
$ python3 review/reproduce.py && python3 -m unittest tests.test_intern -v
6866538002  'Data Science Intern (2027 Start)'  ->  relevant
justification: title 'Data Science Intern (2027 Start)' has title word(s) ['Data Science']; 2 of résumé skills ...
test_intern_any_case_and_punctuation ... FAIL
test_internship_is_excluded ... FAIL
test_real_posting_6866538002_data_science_intern_is_not_relevant ... FAIL
test_control_same_posting_without_intern_is_relevant ... ok
test_internal_international_internals_stay_relevant ... ok
FAILED (failures=3)
```

The two tests that pass before the patch are there on purpose: they fail a **plausible-but-wrong** fix,
`"intern" in title.lower()`, which would also exclude real jobs whose titles contain "Internal", "International" or
"Internals". On 2026-11-09 the live boards had such titles: OpenAI "Internal Communications, Enterprise & Growth",
Anthropic "Finance Systems Lead, International", Databricks "Software Engineer - Database Engine Internals".

## 2. The diff, read as a change in behavior (`review/patch.diff`)

| Hunk | Behavior before → after |
|---|---|
| `INTERN_WORDS = ["Intern", "Internship"]` | new constant; no other list changed |
| `intern_hits = [w for w in INTERN_WORDS if find_word(w, title)]` | checks the **title only**, with the existing whole-word, case-insensitive matcher |
| `... and not senior_hits and not intern_hits` | an intern title now forces `not_relevant`, the same way a seniority word does; the title, skill and location parts are unchanged |
| `reasons.append(f"title has intern word(s) {intern_hits}")` | the record now says **why**, so the verdict stays recomputable by hand |

The change does **not** alter: skill counting, the location test, `resume_fields`/`posting_fields`, or any posting
that has no intern word (the 45 earlier tests and the mutation check still pass).

## 3. Did it stay in scope?

- **Edits: yes.** The only file Claude edited was `jsagent/rules.py` (4 Edit calls, `patch_session_tool_calls.md` rows 4–7).
  `git diff --stat` also showed `runs/state/greenhouse-databricks.json`. That change is from **my** live run at
  20:32 UTC (it contains `run_id 20261109T203203Z-live-day1`); Claude's session started at 20:41:49 and never touched it.
- **Tools: no, and this is the finding.** I started the session with `--allowedTools "Read,Edit"`, expecting Read and
  Edit only. Claude used **Bash** three times (rows 2, 3, 8). A read-only `grep "intern" tests/ *.md` **ran**, so Claude read
  my test file before writing the fix. Its code comment "Amendment 3" was copied from my test's docstring. It also tried to
  write `rules.py` through a Bash python script and to run the tests. Both were refused, and the raw response lists them
  under `permission_denials`. They were refused because a headless run cannot grant approval, **not** because of my
  flag. `--allowedTools` is a list of tools that get auto-approved, not a fence. To actually fence it, the flag would be
  `--disallowedTools Bash` (not tested yet).
- **What that means for test-first:** the test was committed (`fdae00e`) before the patch ran, so it was not written to
  fit the patch. But the patch was written by a model that had seen the test, so passing the test is weaker evidence than
  it would be for a blind patch. That is why the look-alike cases and the mutation check matter.
- **Claude's own report:** it said "I haven't run the tests" (true; both attempts were refused) and claimed
  6866538002 would now show `['Intern']`. I did not take that claim on trust; I checked it (section 4).

## 4. Commands I ran myself after the patch (2026-11-09)

```text
$ python3 review/reproduce.py && python3 -m unittest discover -s tests && python3 tools/check_wrong_versions.py
6866538002  'Data Science Intern (2027 Start)'  ->  not_relevant
justification: ... ; title has intern word(s) ['Intern']
Ran 50 tests in 0.133s
OK
[OK] clean copy: tests pass
[OK] 1 empty board reported as success ... [OK] 8 symlink escape ...   (all 10 wrong versions still caught)
```

## 5. My decision

> **Accept.** "I accept that the intern test first went red before and then green after whrn i ran it, and the changed rule stayed in rules.py"
> (Riya Kapadnis, 2026-11-09, in chat, quoted as typed)

## 6. What the test would still miss

Checked after the patch with `rules.find_word` on each title:

- **An internship whose title does not say "Intern".** For example, `"Data Scientist (Summer 2027)"` with "12-week internship"
  only in the description is still rated `relevant`. The rule looks at the title only, and no test has intern wording
  only in the content.
- **The plural `"Interns"`** (e.g. "Data Science Interns") is not matched, because whole-word matching treats "Interns" as
  a different word.
- **`"Co-op"`** is not matched by this change. It is handled by the next amendment (full-time only).
