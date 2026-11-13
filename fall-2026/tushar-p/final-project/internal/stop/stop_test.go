package stop

import (
	"context"
	"slices"
	"strings"
	"testing"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
)

// Moved here from cmd/apg/main_test.go with RemoteExit (T2.3).
func TestRemoteExit(t *testing.T) {
	ok := []sandbox.Result{
		{ExitCode: 0},
		{ExitCode: 1, Stderr: "command terminated with exit code 1\n"},
	}
	for _, r := range ok {
		if err := RemoteExit(r); err != nil {
			t.Errorf("%+v: unexpected error %v", r, err)
		}
	}
	gone := sandbox.Result{ExitCode: 1, Stderr: `Error from server (NotFound): pods "apg-x" not found`}
	if err := RemoteExit(gone); err == nil {
		t.Error("a kubectl failure must not count as the check's exit code")
	}
}

// fakePod answers the fingerprint and kill commands with fixed output.
type fakePod struct {
	sandbox.Sandbox // embedded nil interface: only Exec is used here
	fingerprint     string
	kill            string
}

func (f *fakePod) Exec(_ context.Context, cmd ...string) (sandbox.Result, error) {
	switch {
	case slices.Equal(cmd, FingerprintCmd):
		return sandbox.Result{Stdout: f.fingerprint}, nil
	case slices.Equal(cmd, KillCmd):
		return sandbox.Result{Stdout: f.kill}, nil
	}
	return sandbox.Result{}, nil
}

func noRec(string, ...sandbox.Result) {}

// The same files listed in another order give the same fingerprint; a
// changed hash gives a different one.
func TestFingerprintIgnoresOrder(t *testing.T) {
	pod := &fakePod{fingerprint: "aaa  /workspace/a\nbbb  /workspace/b\n"}
	c := New(pod, "check.sh", noRec)
	first, err := c.fingerprint(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	pod.fingerprint = "bbb  /workspace/b\naaa  /workspace/a\n"
	second, _ := c.fingerprint(context.Background())
	pod.fingerprint = "bbb  /workspace/b\naab  /workspace/a\n"
	third, _ := c.fingerprint(context.Background())
	if first != second || first == third {
		t.Errorf("fingerprints: %s %s %s; want first == second != third", first, second, third)
	}
}

// AfterStep runs no check when nothing changed.
func TestAfterStepUnchanged(t *testing.T) {
	pod := &fakePod{fingerprint: "aaa  /workspace/a\n"}
	c := New(pod, "check.sh", noRec)
	if err := c.Baseline(context.Background()); err != nil {
		t.Fatal(err)
	}
	r, err := c.AfterStep(context.Background(), 1)
	if err != nil || r.Changed || r.Ran || len(c.Runs) != 0 {
		t.Errorf("result %+v err %v runs %d, want nothing", r, err, len(c.Runs))
	}
}

// A process that survives every kill pass, or output that is not the
// script's JSON, is a harness error: the check must not run.
func TestKillFailures(t *testing.T) {
	for _, out := range []string{`{"killed": [{"pid": 7, "cmd": "x"}], "left": 1}`, "Traceback (most recent call last):"} {
		c := New(&fakePod{kill: out}, "check.sh", noRec)
		if _, err := c.Run(context.Background(), "final", 0); err == nil || !strings.Contains(err.Error(), "kill processes") {
			t.Errorf("kill output %q: err = %v, want a kill error", out, err)
		}
	}
	n, err := New(&fakePod{kill: `{"killed": [{"pid": 7, "cmd": "sleep 300"}, {"pid": 9, "cmd": "y"}], "left": 0}`}, "c", noRec).Kill(context.Background(), "check")
	if err != nil || n != 2 {
		t.Errorf("kill = %d, %v; want 2, nil", n, err)
	}
}
