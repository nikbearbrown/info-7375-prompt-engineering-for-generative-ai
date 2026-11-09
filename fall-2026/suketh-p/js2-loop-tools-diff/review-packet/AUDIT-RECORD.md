# Pre-run audit — patch `4e39762`

**Date and time** — 2026-11-09 00:36:08 EST

**Verdict** — Proceed to verification. The diff adds two lines in `classify_response` in `jobwatch/loop.py`, the only function and file allowed by my review gate.

**Target** — Check that an empty HTTP 200 from Greenhouse or Ashby is recorded as `unverified` with the raw body saved and counts unknown. With one empty board, the run should end `incomplete` and show the other results as provisional. The first-run case should create no state file, and the later-run case should leave state byte-for-byte identical. When all three boards are empty, expect `error` and no state file. Replay three nonempty boards with zero new postings and matching approval to check that the run still finishes.

**Mechanism** — The new branch checks the parsed postings before the loop compares them with saved history. It returns `unverified` and no postings, so the existing loop skips that board when it computes new keys. The loop already saves the raw response before classification and exits before writing state when the run is incomplete or ends in error.

**What would change my view** — I’d ask for a revision if either provider still reports an empty board as usable, if state gets written in an empty-board run, or if the nonempty replay stops finishing. I’d reopen the scope check if the commit includes changes outside `classify_response`.
