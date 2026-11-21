# SOURCES

## The project's own records (Klaxon, public `main` at `fef450b`, 2026-11-17)

- `README.md`, `docs/STATUS.md`, `docs/PLAN.md`, `docs/DECISIONS.md`, `docs/RESEARCH.md` (the 10/9 research).
- `evidence/week5/report.md`: the first evaluation, 48 runs (worked out offline from the saved runs, 2026-11-08).
- `evidence/week7/2026-11-17T042300Z_gated-run_duplicate-delivery/` and its `_panel/` screenshots: the gated live
  run with the web panel open (fault 1, Opus 5.5, approved by Aravind at his terminal).
- GitHub Actions run 44037113149 (week 7's review branch, all 12 jobs passed) and run 44188797067 (`main`).
- The week 8 plan, commit `9cfc249` on the branch `claude/week-8-plan` (a plan only, not merged on 2026-11-20).

## Prior work (each read by Claude Code on 2026-11-20)

- TechCrunch, 2026-02-04, "AI SRE Resolve AI confirms $125M raise, unicorn valuation":
  https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/
- Goodwin, 2026-11-04, "Goodwin Advises Traversal on $120 Million Series B":
  https://www.goodwinlaw.com/en/news-and-events/news/2026/11/announcements-technology-goodwin-advises-traversal-120-million-series-b
- Dealroom, 2026-11-03, "Traversal raises $120M at $1B valuation to automate incident response":
  https://dealroom.co/news/169321-traversal-raises-120m-at-1b-valuation-to-automate-incident-response/
- Traversal, launch post ("the AI SRE for the Enterprise"): https://traversal.com/blog/launch-announcement
- Datadog, 2025-12-02, "Datadog Launches Bits AI SRE Agent to Resolve Incidents Faster":
  https://www.datadoghq.com/about/latest-news/press-releases/datadog-launches-bits-ai-sre-agent-to-resolve-incidents-faster/
- AWS, 2026-03-31, "AWS DevOps Agent is now generally available":
  https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/
- Microsoft Tech Community, 2026-03-10, "Announcing general availability for the Azure SRE Agent":
  https://techcommunity.microsoft.com/blog/appsonazureblog/announcing-general-availability-for-the-azure-sre-agent/4500682
- Jha et al., "ITBench: Evaluating AI Agents across Diverse Real-World IT Automation Tasks", ICML 2025, PMLR 267:
  https://proceedings.mlr.press/v267/jha25a.html
- CNCF blog, 2026-01-07, "HolmesGPT: Agentic troubleshooting built for the cloud native era":
  https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/
- HolmesGPT docs, deployment verification: https://holmesgpt.dev/latest/operator/deployment-verification/
  (Aravind read HolmesGPT's README and this page on 2026-10-09; Claude Code read the page again on 2026-11-20.)

## Tools for the film

- Voice: Kokoro (`kokoro_onnx`), voice `am_onyx`, from the course toolkit's environment; disclosed in the first line.
- Footage: Klaxon's web panel and its saved screenshots; headless Chrome; public GitHub pages.
- Assembly: ffmpeg, with captions as a soft track.

## AI use

I chose the film's form: real footage of my project, Professor Bear's four parts in his order, and a synthetic voice
that the first line discloses. Claude Code researched the prior work, drafted the script from my project's records,
checked every claim against them (FACTCHECK.md), and built the film from my choices; I reviewed the
cut and approved it. Claude Code also wrote Klaxon's code under my direction.
