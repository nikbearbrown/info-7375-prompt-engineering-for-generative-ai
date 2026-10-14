# AMI sample — 10 whole scenario meetings

**Source:** AMI Meeting Corpus, manual annotations (`ami_public_manual_1.6.2.zip`), from https://groups.inf.ed.ac.uk/ami/download/.
**Downloaded:** 2026-10-14, 13:52 EDT (17:52 UTC). SHA-256 of the zip: `b56e5babb2496b8795deeeda7e71178d7fbc9963f94276cf2a3f4b56ebbc9f9d`.
**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. The corpus licence page and the zip's `LICENCE.txt` both state that "the AMI corpus and its annotations" are released under CC BY 4.0. The abstractive summaries are among those annotations.
**Attribution:** AMI Meeting Corpus, AMI Consortium, distributed by the University of Edinburgh (https://groups.inf.ed.ac.uk/ami/), CC BY 4.0. See Carletta, J. (2006), "Announcing the AMI Meeting Corpus", *The ELRA Newsletter* 11(1), pp. 3–5.

**Changes made:** these files were converted from the corpus's NXT XML to plain text by `../../scripts/select_ami_sample.py`. Words were joined into dialogue-act utterances and sorted by start time. Each line is labelled with the speaker's channel letter and scenario role:
- PM: project manager
- ID: industrial designer
- UI: user interface designer
- ME: marketing expert

Utterances are not trimmed or reworded. Non-word tokens (vocal sounds, disfluency markers) are dropped. The scenario meetings are role-played product design teams.

## Selection rule

1. Scenario meetings only (ES, IS and TS series), using `corpusResources/meetings.xml`.
2. Duration under 35 minutes, using the meeting's `duration` attribute.
3. The human abstractive summary has a non-empty DECISIONS section.
4. At most one meeting per team (e.g. ES2002). Within a team, keep the meeting with the most DECISIONS sentences; break ties by the shorter meeting, then the lower ID.
5. Rank those team picks by DECISIONS count, highest first, with ties going to the lower ID. Take the top 10.

There were 73 eligible meetings across 35 teams. `selection.csv` lists every scenario meeting that has a summary, with its duration, DECISIONS and ACTIONS counts, eligibility and whether it was selected.

Whole meetings are used, not cut segments, because the AMI abstractive summaries are written per meeting. A cut segment wouldn't match its reference summary.

| Meeting | Duration | DECISIONS | ACTIONS |
|---|---|---|---|
| IS1004d | 32.6 min | 12 | 1 |
| ES2006d | 33.2 min | 10 | 1 |
| IS1009d | 32.1 min | 9 | 1 |
| ES2008c | 35.0 min (2098 s) | 8 | 4 |
| ES2010b | 29.4 min | 8 | 3 |
| ES2011b | 26.4 min | 8 | 2 |
| ES2013d | 31.6 min | 8 | 3 |
| IS1003c | 31.2 min | 8 | 3 |
| IS1005c | 34.4 min | 8 | 4 |
| ES2007a | 20.4 min | 7 | 1 |

## Files

- `<meeting>/transcript.txt`: the speaker-labelled transcript, one utterance per line as `[hh:mm:ss] <channel> (<role>): <text>`.
- `<meeting>/summary.txt`: the human-written abstractive summary, with sections ABSTRACT, DECISIONS, PROBLEMS/ISSUES and ACTIONS.
- `selection.csv`: the full candidate list behind the selection.

## Rebuild

From `final-project-film/`, after unzipping the download into `case-study/data/raw/extracted/`:

    python3 -I case-study/scripts/select_ami_sample.py case-study/data/raw/extracted case-study/data/sample 10
