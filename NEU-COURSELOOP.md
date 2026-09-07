# Continuous NEU course films

`./neu-courseloop.sh` runs continuously, with a fresh Claude Code session per
film. `--dry` prints the entire inventory without changing state or calling AI;
`--once` attempts one eligible film; `--status` reports the current worker;
`--retry-failed` reopens failed jobs (does not rebuild completed ones).

| Source | Format | Persona |
| --- | --- | --- |
| Numbered narrative chapter | deep-explainer | Liam, in for Bear |
| Current graded Assignment brief | ai-explainer | Liam, in for Bear |
| Each numbered lesson Assessment | cli-explainer, Claude skin | Liam, in for Bear |

All narration uses local Kokoro `am_onyx`. These are instructor films, not a new
student video requirement. The five-stage teaching spine remains Predict →
Build It → Use It → Ship It → Verify. Assessment films teach using examples,
not fabricated student work. Historical exercises and student submissions are
not part of the current NEU Assessment queue. Quizzes remain self-checks.

The chapter queue includes numbered chapter files, including introductions,
appendices and separately named draft variants; front/back matter are excluded.
Draft conflicts must be disclosed, not silently reconciled. INFO 6205 uses each
top-level section of its single book Markdown file, excluding code-fence comments.
`neu-courseloop.json` defines the course-specific source locations.

## State and output

`youtube/claude-liam-neu-<job>-v-<source-hash>/` holds each new version. Existing
films are never replaced. `.neu-courseloop/records.json`, `status.json`, and job
logs preserve progress. Rescans detect source/prompt/course-map changes. Completed
fingerprints are skipped. A finished process alone is not success: the supervisor
requires a matching receipt, provenance/check reports, current MP4, audio/video
streams and audible narration. These automated checks do not replace the worker's
frame-level visual review or the instructor's review. “review-ready” may be an
honestly labeled slate review, not a fully sourced final film.

All six workers share `../.neu-courseloop/render.lock`: only one course film
build runs at a time. This lock does not coordinate older bookloops/filmloops.
Each course also has a non-deleting advisory lock to prevent duplicate workers.
Jobs time out after 90 minutes; failures retry at most twice per fingerprint.
Any failure or account limit triggers a shared 30-minute cooldown. Low disk
space pauses production below 20 GiB free. Nothing is deleted to make space.
The machine currently needs to stay awake and logged in to produce continuously;
launch agents resume after login, not while the computer is powered off/asleep.

Prerequisites: authenticated subscription-backed `claude`, `python3`, `ffmpeg`,
`ffprobe`, and an installed sibling `brutalist-art` toolkit with its render/audio
dependencies. No toolkit is vendored here. Override `BRUTALIST_ART`, `NEU_PYTHON`,
`NEU_SHARED_STATE`, `NEU_JOB_TIMEOUT`, or `NEU_MIN_FREE_GB` if needed.

The supervisor strips inherited API/provider keys from its child environment and
disables MCP servers. It uses Claude Code's configured subscription and consumes
that account's usage allowance; it does not buy credits. No paid media generation,
publishing, git pushes, package installation, or human-signature fabrication is
authorized. Claude tools are limited to file and shell work with the production
scope in NEU-COURSELOOP-PROMPT.md; this is not an OS-level security sandbox.

## macOS service

When installed, the service label is `co.neu.courseloop.<repository-folder>`.
The LaunchAgent lives in `~/Library/LaunchAgents/<label>.plist`, uses KeepAlive,
and logs to `.neu-courseloop/service.log` and `service-error.log`.

Stop a service with `launchctl bootout gui/$(id -u)/<label>`. Start it again with
`launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist`.
Do not run a second manual worker while the service holds the course lock.

### Installation status — 2026-09-06

The six LaunchAgents were installed and tested, but macOS denied their access to
Documents (`Operation not permitted`, exit 126). They were booted out and disabled
to prevent repeated failed launches. No course production job started. This is a
macOS privacy authorization issue, not a course validator failure. After the
background runner has authorized Documents access, enable its exact label with
`launchctl enable gui/$(id -u)/<label>`, then bootstrap the plist as above and
inspect `--status` plus `service-error.log`. Do not bypass OS privacy controls.
