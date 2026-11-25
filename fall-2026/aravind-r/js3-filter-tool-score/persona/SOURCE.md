# Persona source

`maya-sehgal.resume.json` is a byte-for-byte copy of `search/examples/maya-sehgal/resume.example.json` from The Reallocation Engine (commit `d08afdd`), a fictional example persona shipped for coursework. It is not edited here.

SHA-256: `617c124745dfc2bf709db5f3b962956ba83e9075796ecbc793d3e14baece8edb`

`persona-prefs.json` holds the fields the filter reads: `preferred_max_years`, `stretch_max_years`, `locations`, `needs_sponsorship`, `domains`. They are preferences added for this assignment (CONTRACT.md, 2026-10-31), not facts from the résumé.

**Correction, 2026-11-25, made after the v1.0.0 audit results were seen.** The file inherited from JS2 had `years_pm: 2`, which the filter turned into a ceiling of 3 years. That did not match the acceptance policy the persona stands in for: apply mostly to roles requiring at most 4 years, sometimes 5+ or 6+, never 7+. `years_pm` is replaced by `preferred_max_years: 4` and `stretch_max_years: 6`. Filter v1.0.0 ran with the earlier file (commit `a68340ec`). The persona is still fictional.
