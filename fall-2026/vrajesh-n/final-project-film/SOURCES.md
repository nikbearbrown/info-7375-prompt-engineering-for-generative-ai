# SOURCES — Early Bird pitch film (v1.0, rebuilt 2026-10-24)

## External sources (alternatives and facts)
| Source | Accessed | Used for |
|---|---|---|
| the-reallocation-engine, `.claude/skills/greenhouse-watch/` (`scripts/greenhouse_watch.py`, SKILL.md), local clone | read 2026-10-14; **run by me 2026-10-24** | B03/B06: the comparison run on my two Commure snapshots (`evidence/gw/`) |
| the-reallocation-engine `search/examples/aarav-patel/resume.example.json` | 2026-10-24 | the fictional sample resume greenhouse-watch scored against (my real resume was not used) |
| Social Media Today, "LinkedIn AI tools for job seekers…" https://www.socialmediatoday.com/news/linkedin-ai-tools-job-seekers-recruiters-smbs/737481/ | 2026-10-14 | LinkedIn Job Match compares a profile with a posting's qualifications |
| Public job-board endpoints: `api.ashbyhq.com/posting-api/job-board/commure`, `boards-api.greenhouse.io/v1/boards/{stripe,figma,databricks}/jobs`, `api.lever.co/v0/postings/palantir` | 2026-10-14, 2026-10-23 | the saved board responses in `evidence/` (public posting data only) |
| Greenhouse public Job Board API write-up https://dev.to/zsevic/integration-with-greenhouse-public-jobs-api-1lj3 | 2026-10-14 | confirms the board API is public, read-only, unauthenticated |

Examined and not used on screen: the course `greenhouse-watch-demo` README (its Figma "0 kept" figure was used in the v0.2 film; v1.0 uses my own run instead), Jobright reviews, Simplify autofill help.

## Self-created material (mine)
- The project and its shape: keep every software job, a referral + dream-company list, the order referral → freshness → fit, the private LinkedIn-connections idea (decided 2026-10-14).
- **Runs I did myself:** the 2026-10-23 probe run that saved the second Commure snapshot (`python -I probe.py` in `js1-contract-and-watch/data/raw/`); the new-ID diff (2026-10-24, output in `evidence/commure-new-ids-2026-10-14_to_2026-10-23.txt`); both greenhouse-watch runs (2026-10-24, `evidence/gw/`). Claude wrote the two commands; I ran them on my machine and the outputs are unedited.
- Choices for v1.0: rebuild the whole film from scratch; keep the Kokoro voice; approve script v1.0.
- My work history and repositories cited in B08 (resume kept private; public repos linked in FACTCHECK.md).
- `FRICTIONAL.md` dated entries in my own words.

## Claude contributions (Claude Code, model Claude Opus 5.5)
- **Drafted the narration script** (SCRIPT.md) and `PROJECT-BRIEF.md` from my decisions and my run outputs; I approved v1.0. After approval Claude shortened B03, B06 and B07 to keep the film under four minutes, and corrected one B02 line after a department check (FACTCHECK #8). The film says this in B00 and B09: "drafted with Claude from my own decisions".
- Wrote `evidence/probe.py` (2026-10-14) and the diff and greenhouse-watch commands I ran (2026-10-24).
- Wrote `build_beats.py`, the ten new Remotion scenes (`EarlyBirdFilm.tsx`, copy in `toolkit/`), ran narration, alignment, the transcription check, previews, the render and the gates, and wrote FACTCHECK, SHOTLIST, PROMPTS, BUILD-PROMPT and this file.
- No Claude model response is shown in the film. No on-screen figure comes from a model; every figure traces to FACTCHECK.md.

## Third-party tools and assets
| Item | License / terms |
|---|---|
| brutalist.art toolkit (github.com/nikbearbrown/brutalist.art, commit `519fcbb` + local changes in BUILD-PROMPT.md) | course-provided; no license file in the repo |
| greenhouse-watch (the-reallocation-engine) | course-provided |
| Kokoro-82M ONNX voice model, voice `am_onyx` | Apache-2.0 |
| faster-whisper `base` (alignment and the pronunciation check) | MIT |
| Remotion 4.0.486 | Remotion license (free for individuals) |
| PT Mono font (bundled with the toolkit) | SIL Open Font License |
| ffmpeg 9.0.2 | LGPL/GPL |
