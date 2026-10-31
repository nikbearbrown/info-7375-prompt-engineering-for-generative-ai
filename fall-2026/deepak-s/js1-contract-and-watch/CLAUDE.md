# Working rules for Claude Code in this folder

CONTRACT.md is the spec. If code and contract disagree, the contract wins. If the contract is
ambiguous or silent, stop and ask me. Do not pick an interpretation yourself.

Do not edit: CONTRACT.md, tests/acceptance/, tests/conftest.py, labels/, prompts/*.md once I say "frozen",
FRICTIONAL.md, the sign-off and driver's-seat sections of README.md, examples/persona_resume.json.
If you think one of these is wrong, tell me and explain why.

Do not: make network requests, run the live fetch, call the Anthropic API, or read anything
outside this folder. I run those myself.

Stack: Python 3.11+, stdlib urllib for HTTP, dependencies pinned in requirements.txt
(anthropic, jsonschema, pytest only, unless I approve more). One entry point: `python -m jobwatch`.

No TODO, FIXME, stub, `pass` placeholder, or "not implemented" path in delivered code. If you
didn't finish something, say so plainly in your reply.

After every change, list the files you touched and the CONTRACT.md clause each change serves.
