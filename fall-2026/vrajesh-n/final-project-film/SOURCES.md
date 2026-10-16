# SOURCES — Early Bird pitch film

All accessed 2026-10-14 unless noted.

## External sources (alternatives and facts)
| Source | Used for |
|---|---|
| the-reallocation-engine, `.claude/skills/greenhouse-watch/` (SKILL.md, README.md, `scripts/greenhouse_watch.py`), local clone at commit `80a44c8` (2026-10-03) | what greenhouse-watch does: one board per run; Greenhouse, Ashby, SmartRecruiters hosts; résumé-keyword score threshold |
| course repo `fall-2026/nik-bear-brown/greenhouse-watch-demo/README.md` | the demo figures: 11 new Figma postings, 0 kept |
| Social Media Today, "LinkedIn AI tools for job seekers…" https://www.socialmediatoday.com/news/linkedin-ai-tools-job-seekers-recruiters-smbs/737481/ | LinkedIn Job Match compares a profile with each qualification of a posting |
| careery.pro Jobright review https://careery.pro/blog/ai-job-search/jobright-ai-review (published 2026-10-08) | examined, then **not used in the film**: its only fabrication report is one unverified Reddit account |
| scoutify.com Jobright review https://scoutify.com/blog/jobright-review | background on Jobright (not used on screen) |
| Simplify help, autofill settings https://help.simplify.jobs/articles/8686025-manage-autofill-settings-in-the-simplify-extension | background on auto-fill tools (not used on screen) |
| Greenhouse public Job Board API write-up https://dev.to/zsevic/integration-with-greenhouse-public-jobs-api-1lj3 | confirms the board API is public, read-only, unauthenticated |
| Public job-board endpoints: `api.ashbyhq.com/posting-api/job-board/commure`, `boards-api.greenhouse.io/v1/boards/{stripe,figma,databricks}/jobs`, `api.lever.co/v0/postings/palantir` | the real probe data in `evidence/2026-10-14/` (public posting data only) |

## Self-created material (mine)
- The project idea and its shape: keep every software job, a referral + dream-company list, project-proof matching, the order referral → freshness → fit, and the private LinkedIn-connections idea (all my decisions in conversation, 2026-10-14).
- Rejected directions, also mine: "skip most postings" (I rejected it: in this market I want every software job), and Meta's Muse Spark as a second judge.
- My work history and repositories cited in B08 (resume kept private; public repos linked in FACTCHECK.md).

## Claude contributions (Claude Code, model Claude Opus 5.5, session of 2026-10-14)
- Researched alternatives (web search) and read the course repos; flagged that the course's greenhouse-watch already does the core watch, and that an earlier draft line about Jobright overstated its source (removed).
- Drafted `PROJECT-BRIEF.md` and the narration script from my decisions; I reviewed and approved them.
- Wrote `evidence/probe.py` and ran it; wrote `build_beats.py`; wrote the ten Remotion scenes (`EarlyBirdPitch.tsx`, kept in the local brutalist.art clone); ran narration, alignment, the transcription pronunciation check, the preview and the render; wrote these documents.
- No Claude model response is shown in the film. No figure on screen comes from a model; every figure traces to FACTCHECK.md.

## Third-party tools and assets
| Item | License / terms |
|---|---|
| brutalist.art toolkit (github.com/nikbearbrown/brutalist.art, commit `519fcbb` + local changes listed in BUILD-PROMPT.md) | course-provided; no license file in the repo |
| Kokoro-82M ONNX voice model, voice `am_onyx` | Apache-2.0 |
| faster-whisper `base` (timing alignment and the pronunciation check) | MIT |
| Remotion 4.0.486 | Remotion license (free for individuals) |
| PT Mono font (bundled with the toolkit) | SIL Open Font License |
| ffmpeg 9.0.2 | LGPL/GPL |
