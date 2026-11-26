# Sign-off — Job-Search Agent 3

**Checked:** which properties, by which of my own tests

| Property | Test(s) or evidence |
|---|---|
| Role needs a whole phrase, not one word | `test_W1_role_needs_whole_phrase` |
| Topic words are case-sensitive and whole-word ("Scalable" is not Scala, "GitHub" is not Git) | `test_W2_topic_words_case_sensitive_whole_word` |
| Repeats count once | `test_W3_repeats_count_once` |
| A missing description is "cannot tell", never a reject | `test_W4_missing_description_is_cannot_tell` |
| Years come from the first experience phrase | `test_W5_years_from_first_experience_phrase` |
| "Python a plus" does not support "requires Python" | `test_W6_a_mention_is_not_support` |
| A bare "Remote" is "cannot tell" | `test_W7_bare_remote_is_cannot_tell` |
| The held-out labels never choose a change; one look each; tampered labels refused | `test_W8_*` (`tests/test_js3_measure.py`), `labels/HELDOUT_LOCK.json` |
| "Unable to sponsor" earns no visa points; one location bonus only; maximum 100 | `test_W9_*`, `test_W10_*`, `test_max_score_is_100` |
| Each wrong version is actually caught | `scripts/js3_sabotage_check.py`: 9 of 9 red |
| The server speaks the protocol and refuses bad calls | `tests/test_js3_mcp.py` (11 tests); `evidence/mcp/transcript.jsonl` |
| The server makes no network requests and writes no files | `test_no_network_during_a_call`, `test_no_file_writes_during_a_call`; audit trace `evidence/mcp/server_audit.txt` |
| The snapshot is what was downloaded | `jsagent/snapshot.py` checks every file's sha256 against `manifest.json` on load |
| The logged held-out results reproduce | Recomputed after v1.3: baseline, A and D all match `HELDOUT_LOG.jsonl` |

**How:**
- **By hand:**
  - my 72 labels, in two passes, blind to the filter
  - my 36 audit verdicts
  - the decisions to adopt A and "internship" and to reject B–E
  - both trust decisions
  - on 2026-11-25, in my own terminal, I reran and read:
    - `python3 -m unittest discover -s tests`: 157 OK. The "usage: … --replay needs --seeded" lines are an inherited JS2
      test passing: the loop refuses an unlabeled replay
    - `python3 scripts/js3_sabotage_check.py`: 9 of 9 wrong versions caught
    - `git show --stat 148f405`: I checked the v1.3 commit's scope myself
- **By a test written before Claude's code:** the filter and claim tests (`35915cd`) and the server tests (`59f714c`) were committed
  before the code they test. The measurement tests (W8) were **not**: they came in the same commit as `measure.py` (`426f0f5`).
  *Claude wrote all of these tests too. What makes the first two sets "before" is the commit order.*
- **By recomputation:** the held-out results reproduced from the code after v1.3; the snapshot hashes on every load.
- **With Claude's help:**
  - all the code
  - the drafts of every document
  - running the snapshot, the filter and the transcripts
  - reading the `fetch` source
  - checking the 46 v1.2 claim labels, which found 10 wrong

**Not checked:**
1. **The 39 new claim labels in the v1.3 shortlist.** Not checked one by one. The first new posting already shows the
   "list of alternatives" error.
2. **The "internship" fix in F2.** It was found on held-out data, so it has no honest measurement.
3. **The `fetch` server was never run.** It needs Python ≥ 3.11.5. My evaluation is from its source at one commit, so its runtime
   behavior (the npm install, the robots.txt checks) is what the code says, not what I observed.
4. **Any client other than my own transcript script.** No real MCP client, such as Claude Code or the Inspector, has connected to
   my server.
5. **Postings on other days.** Everything is one snapshot from 2026-11-25. The held-out set has only 7 relevant postings.
6. **Whether a random reject is wrong at a low rate.** 0 of 30 bounds the error rate only to about 9.5%.

**Not claiming:**
- that the filter finds every relevant job, or that a kept job is worth applying to
- that the score ranks jobs well: the AUC differences were noise at this sample size
- that the claim labels are right; 22% of the checked ones were wrong
- that the server is safe for any client, or that annotations prove anything
- that anything was trained; every change was a file edit

**Signed or withheld:** Signed, Ethan Gomes, 25 November 2026

---

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine |
|---|---|---|---|
| **The filter rules** | Draft FILTER.md from my JS1 contract and persona; flag placeholders and conflicts; write the tests and code from it | Choose every rule and number (score out of 100, visa points, BI titles, years ≤ 3, whole-phrase "Data Engineering") | The rules say what I want; Claude can only guess at that |
| **Labels and the audit** | Build tools that show the posting, never the filter's answer; point out where my labels break my own rule | Label and judge every posting myself; decide which answer stands when they conflict | The labels are the ground truth every number is measured against. When I saw the filter's verdict first, I agreed with it on a posting I had rejected blind |
| **Claims and evidence** | Label claims against quoted spans; check its own labels and report the errors | Decide how much to trust the labels | A label that says "supported" can be wrong 1 time in 5 |
| **Tools and servers** | Write the server, record the transcripts, trace what it touches, read other servers' source | Make the trust decision for each server | A server's description is a claim made by whoever wrote it, and I live with what it can reach |
| **What changes the score** | Propose single changes, measure them on tuning, protect the held-out labels in code | Choose what goes to held-out, and adopt or reject each change | One look at held-out cannot be undone |

**Why the judgment that a posting is worth my time stays mine:** the filter can say a posting mentions Python, is in New York, and
asks for 4+ years. It cannot say whether I want that team, that commute or that company, and its labels were wrong 22% of the time on
what the posting actually requires. The score ranks what the text matches. Whether a job is worth an application is about my life, and
the filter cannot see that.
