// Package stop is the stop condition (PLAN.md T2.3). After every agent
// step the harness fingerprints /workspace; if it changed, the harness runs
// the hidden check, and a pass stops the run. A failed check only tells the
// model that the task is not complete yet. When the agent ends its turn,
// that only triggers a final check: the model's word is never the verdict.
//
// Keeping the check hidden while the agent is still running: before the
// check is copied in, every process in the pod except PID 1 is killed, so
// nothing the agent left running can read or change the check; after it
// runs, processes are killed again and the check directory is deleted,
// all before the agent's next step.
//
// Known limit: the check runs the agent's own code (pytest imports the
// package under test), so that code could read the check while it runs
// and copy it into /workspace. Run records whether the check run changed
// /workspace (CheckRun.ChangedWorkspace), but nothing prevents it without
// running the check as a different user.
package stop

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/policy"
	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// FingerprintCmd lists the sha256 of every regular file in /workspace
// (argv, no shell; the policy limits only the agent, so -exec is fine
// here). Symlinks and empty directories are not part of the fingerprint,
// and neither are the tool caches __pycache__ and .pytest_cache: "-prune"
// skips those directories, and "-o" (or) sends everything else to the
// sha256sum branch.
var FingerprintCmd = []string{"find", "/workspace",
	"(", "-name", "__pycache__", "-o", "-name", ".pytest_cache", ")", "-prune",
	"-o", "-type", "f", "-exec", "sha256sum", "--", "{}", "+"}

// CleanPycacheCmd deletes Python bytecode from /workspace: every
// __pycache__ directory, and every other *.pyc (a file or a symlink). Each
// check run does this after the kill and before the check, so bytecode the
// agent planted cannot be loaded in place of the source, including a bare
// calc/ops.pyc with no ops.py, which Python imports without a source file.
// The pattern "*.pyc" reaches find as is: there is no shell to expand it.
// The "(" ... ")" group makes "-type f -o -type l" bind before -exec
// (argv, so no backslashes are needed, unlike in a shell).
var CleanPycacheCmd = []string{"find", "/workspace",
	"-name", "__pycache__", "-type", "d", "-prune", "-exec", "rm", "-rf", "--", "{}", "+",
	"-o", "-name", "*.pyc", "(", "-type", "f", "-o", "-type", "l", ")", "-exec", "rm", "-f", "--", "{}", "+"}

// killScript kills every process in the pod except PID 1 (the container's
// "sleep infinity") and itself, and prints what it killed as JSON.
//
// kill(-1, SIGKILL) sends SIGKILL to every process this user may signal;
// on Linux that excludes PID 1 and the caller. It loops because a process
// can fork while it runs. A zombie (state Z) is already dead and only
// waits for its parent to collect it, so it does not count.
//
// It runs as "python -I": isolated mode ignores the current directory,
// PYTHONPATH, and the user's site-packages, so nothing the agent planted
// in /workspace or $HOME is imported; the standard library is owned by
// root, so the agent cannot change it.
const killScript = `import json, os, signal, time
me = os.getpid()
def others():
    found = {}
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in (1, me):
            continue
        try:
            with open('/proc/%d/stat' % pid) as f:
                state = f.read().rsplit(')', 1)[1].split()[0]
            with open('/proc/%d/cmdline' % pid, 'rb') as f:
                cmd = f.read().replace(b'\0', b' ').decode(errors='replace').strip()
        except OSError:
            continue
        if state != 'Z':
            found[pid] = cmd
    return found
killed = others()
left = killed
for _ in range(20):
    if not left:
        break
    try:
        os.kill(-1, signal.SIGKILL)
    except ProcessLookupError:
        pass
    time.sleep(0.05)
    left = others()
print(json.dumps({"killed": [{"pid": p, "cmd": c[:200]} for p, c in sorted(killed.items())], "left": len(left)}))
`

// KillCmd runs killScript in the pod.
var KillCmd = []string{"python", "-I", "-c", killScript}

// StepResult is what the stop condition found after one step.
type StepResult struct {
	Changed bool // /workspace changed during the step
	Ran     bool // so the check ran
	Passed  bool // and passed: the run stops
}

// Checker runs the stop condition for one run.
type Checker struct {
	sb    sandbox.Sandbox
	check string                                   // host path of check.sh
	rec   func(phase string, rs ...sandbox.Result) // records every command in the trace
	last  string                                   // fingerprint after the last step or check

	Runs []trace.CheckRun // every check run so far, for the trace
}

// New returns a Checker. Call Baseline after setup, before the agent.
func New(sb sandbox.Sandbox, checkPath string, rec func(phase string, rs ...sandbox.Result)) *Checker {
	return &Checker{sb: sb, check: checkPath, rec: rec}
}

// Baseline records the fingerprint of the freshly copied repo.
func (c *Checker) Baseline(ctx context.Context) error {
	fp, err := c.fingerprint(ctx)
	c.last = fp
	return err
}

// AfterStep fingerprints /workspace and, if it changed since the last step
// or check, runs the check. n is the step number.
func (c *Checker) AfterStep(ctx context.Context, n int) (StepResult, error) {
	fp, err := c.fingerprint(ctx)
	if err != nil {
		return StepResult{}, err
	}
	if fp == c.last {
		return StepResult{}, nil
	}
	c.last = fp
	code, err := c.Run(ctx, trace.TriggerWorkspaceChanged, n)
	if err != nil {
		return StepResult{Changed: true}, err
	}
	return StepResult{Changed: true, Ran: true, Passed: code == 0}, nil
}

// Run runs the hidden check once and returns its exit code (0 = PASS).
// afterStep is the step that triggered it (0 for the final check). The
// error is only for harness failures.
//
// Order: kill the agent's processes, delete __pycache__, fingerprint, copy
// the check into a new directory with a random name, run it, kill again
// (nothing the check started may outlive it), delete the directory,
// fingerprint again.
func (c *Checker) Run(ctx context.Context, trigger string, afterStep int) (int, error) {
	killed, err := c.Kill(ctx, trace.PhaseCheck)
	if err != nil {
		return 0, err
	}
	r, err := c.sb.Exec(ctx, CleanPycacheCmd...)
	c.rec(trace.PhaseCheck, r)
	if err != nil || r.ExitCode != 0 {
		return 0, fmt.Errorf("delete __pycache__ (exit %d, err %v): %s", r.ExitCode, err, strings.TrimSpace(r.Stderr))
	}
	before, err := c.fingerprint(ctx)
	if err != nil {
		return 0, err
	}

	b := make([]byte, 8)
	if _, err := rand.Read(b); err != nil {
		return 0, err
	}
	// policy.CheckDirPrefix: the policy's rule 3 denies any tool call that
	// names it.
	dir := policy.CheckDirPrefix + hex.EncodeToString(b)
	r, err = c.sb.Exec(ctx, "mkdir", "-m", "700", dir)
	c.rec(trace.PhaseCheck, r)
	if err != nil || r.ExitCode != 0 {
		return 0, fmt.Errorf("mkdir %s (exit %d, err %v)", dir, r.ExitCode, err)
	}
	removed := false
	// If anything below fails, still try to delete the directory, with a
	// context of its own: ctx may be the reason it failed.
	defer func() {
		if !removed {
			cctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), 30*time.Second)
			defer cancel()
			r, _ := c.sb.Exec(cctx, "rm", "-rf", "--", dir)
			c.rec(trace.PhaseCheck, r)
		}
	}()

	r, err = c.sb.CopyIn(ctx, c.check, dir+"/check.sh")
	c.rec(trace.PhaseCheck, r)
	if err != nil {
		return 0, fmt.Errorf("copy check: %w", err)
	}
	r, err = c.sb.Exec(ctx, "bash", dir+"/check.sh")
	c.rec(trace.PhaseCheck, r)
	if err != nil {
		return 0, fmt.Errorf("run check: %w", err)
	}
	if err := RemoteExit(r); err != nil {
		return 0, fmt.Errorf("run check: %w", err)
	}
	code := r.ExitCode

	if _, err := c.Kill(ctx, trace.PhaseCheck); err != nil {
		return 0, err
	}
	r, err = c.sb.Exec(ctx, "rm", "-rf", "--", dir)
	c.rec(trace.PhaseCheck, r)
	if err != nil || r.ExitCode != 0 {
		return 0, fmt.Errorf("delete %s (exit %d, err %v)", dir, r.ExitCode, err)
	}
	removed = true

	after, err := c.fingerprint(ctx)
	if err != nil {
		return 0, err
	}
	c.last = after // what the check itself changed is not the agent's next change
	c.Runs = append(c.Runs, trace.CheckRun{
		AfterStep:        afterStep,
		Trigger:          trigger,
		ExitCode:         code,
		Passed:           code == 0,
		Killed:           killed,
		WorkspaceSHA256:  before,
		ChangedWorkspace: after != before,
	})
	return code, nil
}

// fingerprint returns one sha256 over the sorted list of file hashes.
// Sorting matters: the order find lists a directory in can change even
// when nothing in it did.
func (c *Checker) fingerprint(ctx context.Context) (string, error) {
	r, err := c.sb.Exec(ctx, FingerprintCmd...)
	c.rec(trace.PhaseFingerprint, r)
	if err != nil {
		return "", fmt.Errorf("fingerprint: %w", err)
	}
	// A non-zero exit (say, a file the agent made unreadable) still gives a
	// usable fingerprint: its error text is part of it. Only kubectl
	// failing is an error.
	if err := RemoteExit(r); err != nil {
		return "", fmt.Errorf("fingerprint: %w", err)
	}
	lines := strings.Split(strings.TrimSpace(r.Stdout), "\n")
	sort.Strings(lines)
	sum := sha256.Sum256([]byte(strings.Join(lines, "\n") + "\n--stderr--\n" + cleanKubectl(r.Stderr)))
	return hex.EncodeToString(sum[:]), nil
}

// Kill runs KillCmd and returns how many processes it found to kill. The
// command is recorded under phase (check, or gate before an export).
func (c *Checker) Kill(ctx context.Context, phase string) (int, error) {
	r, err := c.sb.Exec(ctx, KillCmd...)
	c.rec(phase, r)
	if err != nil {
		return 0, fmt.Errorf("kill processes: %w", err)
	}
	var out struct {
		Killed []struct {
			PID int    `json:"pid"`
			Cmd string `json:"cmd"`
		} `json:"killed"`
		Left int `json:"left"`
	}
	if err := json.Unmarshal([]byte(strings.TrimSpace(r.Stdout)), &out); err != nil {
		return 0, fmt.Errorf("kill processes: bad output (exit %d): %v: %q %q", r.ExitCode, err, r.Stdout, r.Stderr)
	}
	if out.Left > 0 {
		return 0, fmt.Errorf("kill processes: %d still running after 20 tries", out.Left)
	}
	return len(out.Killed), nil
}

// RemoteExit tells a non-zero exit from the command in the pod apart from
// kubectl failing (for example, the pod is gone). When the command in the
// pod exits non-zero, kubectl exec prints "command terminated with exit
// code N" on stderr; any other non-zero exit is kubectl's own failure.
func RemoteExit(r sandbox.Result) error {
	if r.ExitCode == 0 || strings.Contains(r.Stderr, "command terminated with exit code") {
		return nil
	}
	return errors.New("kubectl exec failed: " + strings.TrimSpace(r.Stderr))
}

// cleanKubectl drops kubectl's "command terminated" line, which is not
// part of what the command printed.
func cleanKubectl(s string) string {
	var keep []string
	for _, line := range strings.Split(s, "\n") {
		if !strings.HasPrefix(line, "command terminated with exit code") {
			keep = append(keep, line)
		}
	}
	return strings.Join(keep, "\n")
}
