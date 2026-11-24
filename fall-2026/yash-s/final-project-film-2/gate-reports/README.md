# Gate reports — job-search-agent (Final Project Film)

Brutalist's own quality gates, run 2026-11-23 on the free local pipeline. The final master
(`job-search-agent.mp4`, 322.96 s) was cut only after every gate passed. Paths in the logs are
shortened to `<course>/`.

| Gate | What it checks | Result | Report |
|---|---|---|---|
| F | paperwork before rendering (FACTCHECK, SHOTLIST, PROMPTS) | PASS | `art-run-*.log` |
| L | beat mix lint | PASS | `art-run-*.log` |
| A | static pre-flight on every scene | **FAIL, then PASS** (24/24 clean) | `art-run-1.log` |
| W | contrast, margins, text-on-text before render | PASS, 23/23 | `art-run-2.log` |
| B | layout audit of every rendered scene | **FAIL on several scenes, then PASS** (every scene CLEAN) | `art-run-2.log` … `art-run-12.log`, `GATE-B-layout-audit-last-scene.md` |
| V | frame-level visual QC of the compiled film | **FAIL once, then PASS**: 50 frames, 0 blocker, 0 major | `art-run-7.log`, `GATE-V-REPORT.md`, `GATE-V-contact-sheet.png` |
| T | type lock: size, contrast, overlap | **FAIL twice, then PASS** | `art-final-1.log`, `art-final-4.log` (fails), `art-final-5.log`, `GATE-T-TYPECHECK.md` |
| Bookend | opening and closing structure | PASS | `BOOKEND-CHECK.txt` |

## What failed and how it was fixed

- **Narration audio, first run:** `ffmpeg` was not on the shell's PATH; re-run with
  `/opt/homebrew/bin` added (`audio-gen.log` is the second run).
- **Gate A:** B12's row labels started outside the frame; B16–B18 (terminal) showed only text
  appearing, which the static check reads as "shapes never change"; B22's net arc was centred off
  the frame. Fixed with fixed label positions, a moving cursor and a drawn marker beside each
  narrated terminal line, and a straight net line.
- **Gate B:** strike-through lines drawn across the words "apply", "email", "log in" (B03) counted
  as labels on a line, so they became crosses beside the words. Other labels a little past the
  ±6.3 safe area (B08, B12), a "recorded output" tag touching the terminal window, and over-wide
  terminal lines (B16) were moved in or scaled to fit; the B19 label touched a page corner.
- **Gate V:** the terminal window was wider than the title-safe area (B16–B18) and the LinkedIn
  result rows were too pale (B06). Narrower window; darker rows.
- **GATE T:** two small pages with an ink outline around handwriting lines (B07, B19) read as two
  stacked labels (§8.6b), the same failure my pitch film had. Fixed with a grey edge.
- **After all gates passed**, the contact sheet showed B19's timeline labels running into each
  other; smaller labels, then Gate V and GATE T were run again (both PASS).
- **Then I watched the film** and saw the "approve" and "refuse" pills overlapping in B03 (the same
  in B07 for "Python" and "MLflow"): the gates check text against lines, not pill against pill.
  The pills are now placed from their measured widths. GATE T then read B03's wider window as one
  fused text blob (§8.6b, `art-final-4.log`); a grey window edge fixed it, and every gate passed
  again (`art-run-12.log`, `art-final-5.log`).

Superseded clips are kept outside the repository in the build folder's `_superseded/`.

## Advisory lines that remain, on purpose

`art final` prints two SKIN LINT notes: the opening is the hesitant writer rather than the
Claude.ai composer, and the outro is my own, not the house `ClaudeTitleOutro` card. Both are
deliberate, as in my pitch film: the course says to narrate as yourself and never use the
instructor's name, persona or credit line, and the house outro has the instructor's handle.
