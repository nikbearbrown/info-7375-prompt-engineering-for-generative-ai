# Sign-off and driver's seat: Job-Search Agent 3

_Claude Code drafted options for these lines at my request; I chose one for each and edited it (SOURCES.md)._

## Sign-off

**Checked**
- Whole-word title matching, distinct-word scoring and "no text means cannot tell", by `tests/test_filter.py`. Each planted wrong version WF1–WF4 fails at least one test (`scripts/wrong_versions.py`), and so does the tool server's WF6. All 950 saved v0.1 records equal a recomputation from the raw files at their logged SHA-256 (`review/run-by-mayank.txt`, run by me).


**How**
- By hand: the 30 held-out labels (blind), the reject-audit verdicts and every shortlist claim label. By recomputation: `review/run-review-commands.sh`, run in my own terminal. With Claude's help: Claude Code wrote the code, the tests and the drafts (SOURCES.md), and Claude Haiku 5.5 wrote the shortlist justifications.


**Not checked**
- whether the `?content=true` text is exactly what a person sees on the posting page;
- any day except 2026-11-25: one snapshot, not a stream;
- prompt injection through posting text into Claude's justifications or into the tool server's client;
- the rejects outside my audit sample, except as the bound says;


**Not claiming**
- No rate for "the filter misses X % of jobs": the bound covers only this snapshot's reject pool. No claim that the tool server is safe for any client except the one I ran. No claim that any posting is right for a real person; Priya is fictional.


**Signed or withheld:** Mayank Bhadrasen, Nov 25, 2026 (name, date)

## Driver's seat

| Task | Claude should | I should |
|---|---|---|
| The filter | draft code, tests, planted wrong versions | choose the words, write or choose the reasons, approve each change |
| The reject audit | draw the seeded sample, show each posting's evidence, compute the bound | judge every row from the original posting; name the false friend |
| The shortlist | write one justification per posting, quote its passage, flag a quote it cannot find | label every claim supported / contradicted / insufficient |
| The tool server | write it, record transcripts, list declared vs actual | decide allow / deny / pending for both servers |
| Whether a posting is worth Priya's time | never decide it | decide it |

**Why the judgment stays mine**
- A filter can only find the words I gave it. Whether a job is worth someone's time depends on things no posting states: what they want next, what they'll trade off, who they know there. The audit showed me what the words miss.
