# Setup

**All exercises assume Claude Code access.** INFO 7375 students receive it through Northeastern; public readers need their own Claude Code-enabled account. Begin at [the NEU Claude portal](https://claude.northeastern.edu/) and read the [university access summary](neu-claude-access.md). Use your NEU-provisioned account for the course. Consult university IT for account or entitlement problems.

Open Claude Code in your local course repository. Ask it to read CLAUDE.md and the current week's lesson, then guide you through prediction, your Python implementation, test execution, and artifact review. Make your prediction before asking it to run the code. Keep your work in learning-artifacts/. See [Claude Code's official quickstart](https://code.claude.com/docs/en/quickstart) for installation and account sign-in instructions.

Claude Code interaction uses your account's allowance. The offline Python reference functions do not make model requests. The separate --live API examples below are explicit optional exercises; do not assume NEU account access supplies API credits.

Python 3.11+ is sufficient for every core lab. There are no required third-party packages. Run from the repository root:

```bash
python3 scripts/course.py list
python3 scripts/course.py run 1
python3 scripts/course.py test 1
python3 scripts/validate_course.py
python3 -m coursekit.claude
```

The final command prints an offline prompt preview and makes no request. Reference scripts are finite demos. Week 8's --stdio option intentionally runs until the client closes its input; it is not used by the default demo.

## Learning workspace

Keep your attempts under learning-artifacts/, which is ignored by Git. Do not replace reference solutions with student submissions. Use sanitized or public fixtures. Claude Code is assumed throughout. Where a lesson compares chat or Cowork, you can perform the source-grounded file task in Claude Code and explain interface differences from the instructor demonstration; a separate Cowork entitlement is not a prerequisite. Do not invent interaction transcripts.

## NEU-only video preparation

For enrolled INFO 7375 students, [course prerequisites](../prerequisites/README.md) include the AI policy and an optional Brutalist workflow for recorded submissions. Students may choose another suitable media tool; quality is assessed, not tool choice. Independent readers can skip it. It is not needed to run the Python lessons. Film projects belong in [youtube/](../youtube/README.md); no upload is required by the setup instructions.

## Optional live Claude API

Provision an Anthropic API key using your account's secure workflow and configure ANTHROPIC_API_KEY in the local environment. Choose a currently available Claude model and set CLAUDE_MODEL to its exact ID. Never paste credentials into source, screenshots, course submissions, or chat. .env.example documents names only; this repository does not automatically load .env files.

After explicitly choosing to make a billable request:

```bash
python3 -m coursekit.claude --live --prompt "Explain the difference between evidence and confidence."
python3 lessons/11-tool-use-and-verification/code/main.py --live
```

The first command makes one request. The second permits at most four requests and exposes Claude tool calls through a single read-only arithmetic function. Both default to a 256-token output budget per request; this is not a dollar cap. There are no automatic retries. Account/model availability and billing are separate from a chat subscription; consult the official platform documentation for your setup.

The client sets system instructions at the top level and uses Messages API user/assistant content. Its bounded example has no streaming or automated rate-limit recovery. Live calls have not been exercised by the offline validation suite; transport tests use controlled mock responses. Do not treat those tests as evidence of account access or model performance.

## MCP teaching subset

```bash
python3 lessons/08-mcp-from-scratch/code/main.py
python3 lessons/08-mcp-from-scratch/code/main.py --stdio
```

The first command prints an offline tools/list demonstration. The second provides a newline-delimited JSON-RPC stdio server with one public fixture lookup. Use an absolute script path when configuring a client. It supports the documented 2025-11-25 teaching subset and omits production auth, HTTP transports, cancellation, and full conformance. Evaluate any external server separately before connecting it.
