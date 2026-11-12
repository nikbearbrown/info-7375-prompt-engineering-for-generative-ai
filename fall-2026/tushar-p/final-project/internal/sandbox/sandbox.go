// Package sandbox runs task commands in an isolated environment.
//
// The harness talks only to the Sandbox interface, so the backend (kind
// today, plain Docker as the fallback) can change without touching the loop.
package sandbox

import "context"

// Result is one host command the sandbox ran, kept so it can be written
// into the trace exactly as it happened.
type Result struct {
	// Args is the exact argv run on the host, for example
	// ["kubectl", "--context", "kind-kind", "-n", "apg-sandbox", "exec", "apg-1a2b3c4d", "--", "echo", "hi"].
	Args     []string `json:"args"`
	Stdout   string   `json:"stdout"`
	Stderr   string   `json:"stderr"`
	ExitCode int      `json:"exit_code"`
}

// Sandbox is one isolated environment for one run.
//
// Every method takes a context so the caller can set a timeout
// (context.WithTimeout); when it expires, the host command is killed.
//
// Error rule: Exec returns an error only when the host command could not
// run or the context expired. A command that runs and exits non-zero is
// normal data for the agent, so it is reported in Result.ExitCode with a nil
// error. Start, CopyIn, CopyOut, and Stop return an error on any non-zero
// exit, because those are harness steps that must succeed.
type Sandbox interface {
	// Start creates the environment and waits until it is ready.
	// It can run several host commands, so it returns all of them.
	Start(ctx context.Context) ([]Result, error)
	// Exec runs cmd (argv form, no shell) inside the sandbox.
	Exec(ctx context.Context, cmd ...string) (Result, error)
	// CopyIn copies a host file or directory into the sandbox.
	CopyIn(ctx context.Context, hostPath, sandboxPath string) (Result, error)
	// CopyOut copies a sandbox file or directory to the host.
	CopyOut(ctx context.Context, sandboxPath, hostPath string) (Result, error)
	// Stop deletes the environment. Safe to call more than once.
	Stop(ctx context.Context) (Result, error)
}
