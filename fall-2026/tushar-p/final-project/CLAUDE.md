# Agent Proving Ground — instructions for Claude Code

Read `PLAN.md` before any work. Work only on the task ID named in the prompt.

## Build and test
- Build: `go build ./...`
- Vet: `go vet ./...`
- Test: `go test ./...`
- Before finishing a task, run the narrowest test that covers the change, then `go test ./...`.

## Rules
- Investigate before fixing. Show the cause before changing code.
- Never write, read out, or commit secrets. `ANTHROPIC_API_KEY` comes from the environment only.
- Do not edit `tasks/*/check.sh`, `tasks/*/contract.json`, `tasks/split.json`, or any `*_test.go` file Tushar wrote, unless the prompt says so.
- Do not write or edit `FRICTIONAL.md`.
- Prefer the Go standard library. Ask before adding any dependency.
- Approved dependency: `github.com/anthropics/anthropic-sdk-go`.
- Sandbox access goes through `internal/sandbox`. kubectl (and docker for image builds) are called through `os/exec`.
- In docs, past tense only for things that ran; label mock-ups and seeded runs; no invented results.
- Commit messages start with the task ID, e.g. `T1.2: kind sandbox via os/exec`.
- Explain non-obvious Go in short comments; Tushar is learning Go and must be able to explain every line.
