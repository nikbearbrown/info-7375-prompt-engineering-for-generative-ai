# Gate reports — final build

## Executive summary

Every quality gate in the Brutalist toolkit passed on the final build (2026-10-14). That
includes frame-level visual QC (0 blockers, 0 major defects), the type lock, and the
pre-render scene checks. The master also decodes end to end with no errors. Several gates
failed on the way there; each failure and its fix is in `../FRICTIONAL.md`. No gate was
bypassed or loosened (`ART_STRICT` was never set to 0), and the toolkit was not modified.

| Gate | What it checks | Final result | Report |
|---|---|---|---|
| F | paperwork exists before rendering (FACTCHECK, SHOTLIST, PROMPTS) | PASS | `BUILD-RUN-final.log.txt` |
| F (content) | every claim has a verdict and a source | PASS: 19 rows, 14/14 beats covered | `EXTRA-CHECKS.txt` |
| L | beat-mix lint (no bare text slides) | PASS | `BUILD-RUN-final.log.txt`, `EXTRA-CHECKS.txt` |
| A | static scene pre-flight | PASS | `BUILD-RUN-final.log.txt` |
| W | WCAG contrast, margins, text overlap (pre-render) | PASS | `BUILD-RUN-final.log.txt` |
| B | post-render layout audit per Manim scene | PASS (CLEAN) | `BUILD-RUN-final.log.txt` |
| V | frame-level visual QC on the compiled cut, 28 frames | PASS: 0 BLOCKER, 0 MAJOR | `GATE-V-REPORT.md`, `gate-v-contact-sheet.png` |
| T | type lock: size, overflow, contrast, kerning, card clip | PASS | `GATE-T-TYPECHECK.md`, `ART-FINAL.log.txt` |
| CONTENT | placeholders, missing props, cross-reel contamination | PASS | `EXTRA-CHECKS.txt` |
| FRAME | analytical layout + contrast from beat-sheet props | PASS | `EXTRA-CHECKS.txt` |
| decode | full ffmpeg decode of the master; stream check | no errors; 3840×2160, 24 fps, 5119 frames, video 213.29 s / audio 213.29 s | `EXTRA-CHECKS.txt` |

Non-blocking note from `art final`: "SKIN LINT: BOUT … OUTRO LAW wants ClaudeTitleOutro".
That is expected. The toolkit's outro hard-codes the instructor's channel handle, which this
assignment forbids, so BOUT is my own Manim card.
