# SOURCES

Drafted by Claude (Claude Code, Opus 5.5) on 2026-10-09 from the session record and my answers that day.

## What I used

- **My project's first piece**, `klaxon` repository (local commit `801a0bf`; the code is not public yet): `src/klaxon/**` and `tests/**`. Every number in the film comes from its two evidence files of 2026-10-09, copied into `evidence/` here (`evidence/first-piece/2026-10-09T225438Z_duplicate-webhook_naive_seed7.json` and `..._idempotent_seed7.json`), produced by `python -m klaxon.demo duplicate-webhook --handler naive|idempotent` with Python 3.12.14. The data is synthetic and seeded (seed 7): a fake provider, fake payments, no real money.
- **Brutalist toolkit** `nikbearbrown/brutalist.art`, commit `22264a3`: the show-tell skill, its drawing kit (`iso_kit.py`) and its 25 approved original isometric props (`iso_originals_25.py`), the Remotion bookends (`BrutalistHesitantWriter`, `ClaudeDefinitions`) and one `ShowTellCard`, the Kokoro audio script, word alignment, the QC gates and the compiler.
- **Manim Community 0.18.1** (MIT): every drawn beat.
- **Remotion** (from the toolkit's `runtime/remotion` install): the opening writer, the terms card and the real-run card.
- **Kokoro-82M** voice model (Apache-2.0) via kokoro-onnx, voice `am_onyx`: the synthetic narration, generated locally.
- **faster-whisper** (MIT): word timings, so each motion lands on its spoken word, and a pronunciation check.
- **Fonts:** EB Garamond (SIL Open Font License, bundled with the toolkit).
- **Public sources checked for claims** (all read 2026-10-09; see FACTCHECK.md): Stripe webhooks docs (https://docs.stripe.com/webhooks); AWS SQS at-least-once delivery docs; the HolmesGPT README and its deployment-verification page (https://github.com/HolmesGPT/holmesgpt, Apache-2.0); my public EventEase repo (https://github.com/AravindKumar2504/EventEase).
- **No third-party images, footage, music, logos or sound effects.** Product names (HolmesGPT, GitHub) appear only as plain text labels.

## What was made for this film

- `make_sheet.py` and `beat_sheet.json` (the narration and visual plan, 22 beats), `scene_body.py` and the generated `scenes.py` (19 Manim scenes), `build_scenes.py`, `finish_audio.py`, `make_shotlist.py`
- `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `BUILD-PROMPT.md`, `PROJECT-BRIEF.md`, `README.md`, this file, `FRICTIONAL.md`
- The rendered film and the toolkit's gate reports

## Who did what

**Claude (Claude Code in the Claude desktop app, model Claude Opus 5.5), at my request on 2026-10-09:**
- Built the first piece in the Klaxon repo (code and 91 tests), had a separate Claude reviewer check it, fixed what it found, and ran the demo that produced the evidence files.
- Drafted the narration and the brief from my planning-session notes, wrote the beat sheet and all scenes, checked the claims against the public sources, rendered the film and ran the toolkit's gates.
- Drafted these documents.

**Me (Aravind Sundaravadivelu):**
- Chose the project and its direction in the planning session on 2026-10-09 (the pivot from code review to an AI on-call engineer, the full build, the course fit).
- Asked Claude to build the first piece and the film.
- Read the HolmesGPT README and its deployment-verification page myself (confirmed 2026-10-09), so the film can say "the alternatives I looked at".
- Confirmed my reason for the project as written in beat B15, and that the EventEase webhook signature check (commit `271ead3`, 2025-04-17, git user "AraGooner") is mine.
- Approved the first commit in the Klaxon repo (`801a0bf`, local only).
- Watched the film and approved the narration (2026-10-09). The EventEase line in beat B16 was added at my request.
- Have not yet read the first piece's code line by line or run it myself; Claude ran the tests and the demo.

## Synthetic narration

The narrator is Kokoro's synthetic `am_onyx` voice. It is not my voice or the instructor's, and it is not an endorsement. The first beat says so.

## No Claude output is shown

The film shows no Claude response. The real-run numbers come from running my own code, recorded in the evidence files. Everything about what Klaxon will do is a plan, labelled "constructed" on screen.
