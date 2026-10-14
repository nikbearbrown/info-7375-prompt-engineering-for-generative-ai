# Gate table — submitted film `aravind-r-readback-pitch.mp4` (v2 visuals)

- **Built with:** the toolkit's own commands, run from `final-project-film/` (`./art run <reel> --height 1080`, then `./art final <reel> --height 1080 --out <reel>/exports/landscape`), brutalist.art @ `cd4bf20` plus my outro patch.
- **Verified:** the build is byte-identical to the gated v2 candidate (same SHA-256, all 4,378 decoded frames identical).
- **Strict mode** (`ART_STRICT` unset): no `ART_STRICT=0` overrides anywhere.

| Gate | What it checks | Result (final build) | Report |
|---|---|---|---|
| F | paperwork present; factcheck content | PASS: 37 rows, every row resolved | `gates/v2/factcheck_check.txt` |
| L | beat-mix lint | clean | `gates/v2/art-run-toplevel.log` |
| A | static pre-flight, all 9 Manim scenes | 9/9 clean | `gates/v2/art-run-*.log` |
| W | WCAG contrast, margins, text overlap | 9/9 clean | `gates/v2/art-run-*.log` |
| B | layout audit (strict, curve-strict) | 0 errors, 0 warnings; every clip slotted | `gates/v2/gate-b-layout_audit-last.md` |
| V | frame-level visual QC, 20 frames | 0 BLOCKER, 0 MAJOR | `gates/v2/gate-v-REPORT.md` |
| T | type lock (midpoint frames) | PASS | `gates/v2/TYPECHECK.md` |
| Bookend | structural bookends | PASS | `gates/v2/bookend_check.txt` |
| Render integrity | `verified.json` | status "ready", SHA-256 `4334b59eae58cd946716cc924da4fb47a28ffae236c19605a01cad89568278eb`, 182.458 s | `gates/v2/master.verified.json` |

## My own checks (not toolkit gates)

| Check | v1 (commit `31005a1`) | v2 (submitted) |
|---|---|---|
| `freezedetect n=0.003 d=3`: holds ≥3 s | 23 holds, 163.7 s (89.7 %), longest 15.1 s | 8 holds, 26.3 s (14.4 %), longest 3.9 s, plus the static outro card (exempt) |
| Static hold > 4 s (outro excepted) | 20 holds | none |
| Runtime | 182.458 s | 182.458 s (Δ 0.000 s) |
| Narration audio (decoded PCM SHA-256) | `215332921a8d6b4c…` | `215332921a8d6b4c…` (identical) |
| Contact sheet, 1 frame / 2 s | `gates/v2/v1-contact-1frame-per-2s.png` | `gates/v2/v2-contact-1frame-per-2s.png` |
| Full-res frame per beat | `gates/frames/` | `gates/v2/frames/` (checked: labels legible, no logos, every number sourced) |
| Honesty audit | `gates/honesty-audit.md` | `gates/v2/honesty-audit-v2.md` (3 low flags) |
| Text overlaps, every frame (`overlap_check.py`, 24 fps, all 9 Manim scenes) | not run | **0 overlaps** (`gates/v2/overlap-check.txt`) |
| Master has no slate or review overlays | yes (`art final` export) | yes (`art final` export, not the `-slate` copy) |

*The 9.4 % measured on the first v2 candidate rose to 14.4 % after the overlap fixes. Exits now finish before entrances, and no slide passes through text, which removed some motion. That is still under the 25 % target, with no hold over 4 s.*
