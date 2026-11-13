package main

import (
	"bytes"
	"context"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	"github.com/tushar-patel28/agent-proving-ground/internal/sandbox"
	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// TestTimeoutDeletesPodOnKind is a seeded run on a real kind pod: the
// scripted agent runs a command that sleeps 30 seconds, the agent's
// timeout is 3 seconds. The run must end with exit reason timeout, the
// check must still run, and afterwards the pod must be gone (Stop uses a
// fresh context, not the timed-out one).
//
// Set APG_SEEDED_TRACES=<dir> to keep the trace.
func TestTimeoutDeletesPodOnKind(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping kind test in -short mode")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	if err := exec.CommandContext(ctx, "kubectl", "--context", "kind-kind", "get", "--raw", "/readyz").Run(); err != nil {
		t.Skipf("no kind cluster (context kind-kind): %v", err)
	}

	tk, err := findTask("../../tasks", "001")
	if err != nil {
		t.Fatal(err)
	}
	tk.Limits.Timeout = 3 * time.Second
	sb, err := sandbox.NewKind()
	if err != nil {
		t.Fatal(err)
	}
	client := &scriptedClient{calls: []string{
		`run_command {"argv":["python","-c","import time; time.sleep(30)"]}`,
	}}
	began := time.Now()
	tr := runTask(ctx, sb, sb.PodName(), tk, client, nil)
	tr.Model = "scripted (no model)"
	t.Logf("run took %s", time.Since(began).Round(time.Millisecond))

	dir := os.Getenv("APG_SEEDED_TRACES")
	if dir == "" {
		dir = t.TempDir()
	}
	path, err := trace.Write(dir, tr)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("trace: %s", path)

	if tr.ExitReason != trace.ReasonTimeout {
		t.Fatalf("exit reason %s (error %q), want timeout", tr.ExitReason, tr.Error)
	}
	// The bug is not fixed, so the check ran and failed.
	if !tr.Check.Ran || tr.Check.ExitCode == nil || *tr.Check.ExitCode == 0 || tr.Verdict != trace.VerdictFail {
		t.Errorf("check = %+v verdict %s, want ran, non-zero, FAIL", tr.Check, tr.Verdict)
	}
	if s := tr.Budget.Used.AgentSeconds; s < 3 || s > 10 {
		t.Errorf("agent ran %.1fs, want about 3s", s)
	}

	// The pod is gone: kubectl get reports NotFound.
	var stderr bytes.Buffer
	get := exec.CommandContext(ctx, "kubectl", "--context", "kind-kind", "-n", "apg-sandbox", "get", "pod", sb.PodName())
	get.Stderr = &stderr
	if err := get.Run(); err == nil || !strings.Contains(stderr.String(), "NotFound") {
		t.Errorf("pod %s still there after the run (err %v, stderr %q)", sb.PodName(), err, stderr.String())
	} else {
		t.Logf("kubectl get pod %s: %s", sb.PodName(), strings.TrimSpace(stderr.String()))
	}
}
