# BUILD-LOG — Final Project Film (Claude's technical log)

## Executive summary

**What this is:** Claude Code's record of the commands, errors and fixes while building this film and the brand-name
fix. **Why read it:** to rebuild or audit the work. It is not my reflection — that is `FRICTIONAL.md`.

## 2026-11-22 / 11-23

- Folder `final-film/` created with PREDICTIONS.md (5 open questions), MY-SEARCHES.md, FRICTIONAL.md, SCRIPT-OUTLINE.md.
- Predictions pasted verbatim at 15:32 EST before any fix code. Tests written next; 9 fail (1 failure: the old
  "ACME finds nothing" test now contradicts fix A, rewritten to "candidate, never a match"; 8 errors: the alias
  argument and `load_aliases` did not exist yet).
- Fix written; 26/26 pass. Eval re-run on the same CSV (sha256 identical to 10-25): Robinhood, Chime, SoFi listed;
  Plaid, Ramp, Coinbase newly listed (all blank approvals); no other row changed.
- Film reel `youtube/coop-sponsor-check-final/` copied from the pitch reel; beat sheet rewritten into the four parts;
  8 new Manim scenes; B05 redrawn around her Capital One search (the 10-12 search shown in the pitch film was Claude's).
- Whisper transcript caught: "So Fi" heard as "Sophia" when listed second → reordered "Robinhood, Chime, and So Fi";
  outro "By <name>" mangled → "Made by <name>". Whisper still cannot spell her name: she must listen to BNAME and BOUT.
- FACTCHECK pass reworded BOS: she wrote Chime Financial was not in "the results I reviewed"; the first draft said
  flatly "not Chime Financial".
- Gate A (static check) stopped the first render: BAFTER had no changing shapes (added arrows), BRES laptop base
  outside the safe area (moved 0.25 right).
- Further gate stops, each fixed in `scenes.py` and re-rendered: Gate B layout — BOS strike line through text (→ cross
  beside it) and a label below the safe area; BGL "previously…" label 0.02 past the edge (34 → 32 pt); BCARE names past
  the edge (moved left). A one-pass bounds check of all new scenes then found nothing else. Gate V — BOS ghost rows too
  faint (darkened), P4 card mostly empty at its sample (part cards: 96 pt, faster typing, 0.3 s lead + 0.8 s padded tail).
  Gate T — BRES smallest text run 40 px < 41 px: labels 36 → 42 pt, then the wavy "Python page" scribbles (read as tiny
  text) replaced by straight code lines. Changed beats had to have their `build` stamp cleared to re-render (stale clips
  moved to the reel's `_superseded/`).
- Final master: GATE T PASS, Gate V 0/0, layout audit 0/0; 257.8 s, 3840×2160, 24 fps. Frames audited at 35 % and 92 %
  of every beat (bookends included) plus 85 % of BNAME, BFIX, BRES and the outro.
- **19:00–19:35, revision after her brief check.** She sent two lines (MY-SEARCHES 3b, 4b): she *has* the resources, and a
  numeric target (≥ 20 of 25 verified, 0 wrong automatic answers). BRES and BBAR narration rewritten from them; only those two
  beats re-voiced (all other mp3s restored from backup so timing is unchanged). GATE T flagged BBAR list text at 36 px →
  PASS/FAIL stacked vertically at 44 pt. New master 257.0 s, GATE T PASS, Gate V 0/0, sha `1fefeef648f8479ab297feee06861d346548216a9d834491dbdb019c7bbe8b4b`. Frames of both beats checked.
