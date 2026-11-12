package sandbox

import (
	"context"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"time"
)

// TestManifest checks the pod and policy settings without a cluster, so it
// always runs.
func TestManifest(t *testing.T) {
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	// Round-trip through JSON so the test sees exactly what kubectl gets.
	b, err := json.Marshal(k.manifest())
	if err != nil {
		t.Fatal(err)
	}
	var list struct {
		Items []struct {
			Kind string `json:"kind"`
			Spec struct {
				// NetworkPolicy fields
				PodSelector map[string]any `json:"podSelector"`
				PolicyTypes []string       `json:"policyTypes"`
				Egress      []any          `json:"egress"`
				// Pod fields; *bool tells "missing" (nil) apart from false.
				AutomountServiceAccountToken *bool `json:"automountServiceAccountToken"`
				SecurityContext              struct {
					RunAsNonRoot bool `json:"runAsNonRoot"`
					RunAsUser    int  `json:"runAsUser"`
				} `json:"securityContext"`
				Containers []struct {
					Image           string `json:"image"`
					SecurityContext struct {
						AllowPrivilegeEscalation *bool `json:"allowPrivilegeEscalation"`
						Capabilities             struct {
							Drop []string `json:"drop"`
						} `json:"capabilities"`
					} `json:"securityContext"`
					Resources struct {
						Limits map[string]string `json:"limits"`
					} `json:"resources"`
				} `json:"containers"`
			} `json:"spec"`
		} `json:"items"`
	}
	if err := json.Unmarshal(b, &list); err != nil {
		t.Fatal(err)
	}

	var sawPolicy, sawPod bool
	for _, it := range list.Items {
		switch it.Kind {
		case "NetworkPolicy":
			sawPolicy = true
			s := it.Spec
			if len(s.PodSelector) != 0 || !slices.Equal(s.PolicyTypes, []string{"Egress"}) || len(s.Egress) != 0 {
				t.Errorf("policy must select all pods and allow no egress: %+v", s)
			}
		case "Pod":
			sawPod = true
			s := it.Spec
			if s.AutomountServiceAccountToken == nil || *s.AutomountServiceAccountToken {
				t.Error("automountServiceAccountToken must be false")
			}
			if !s.SecurityContext.RunAsNonRoot || s.SecurityContext.RunAsUser != 1000 {
				t.Errorf("must run as non-root uid 1000: %+v", s.SecurityContext)
			}
			if len(s.Containers) != 1 {
				t.Fatalf("want 1 container, got %d", len(s.Containers))
			}
			c := s.Containers[0]
			if c.Image != "apg-sandbox:dev" {
				t.Errorf("image = %q", c.Image)
			}
			if p := c.SecurityContext.AllowPrivilegeEscalation; p == nil || *p {
				t.Error("allowPrivilegeEscalation must be false")
			}
			if !slices.Equal(c.SecurityContext.Capabilities.Drop, []string{"ALL"}) {
				t.Errorf("capabilities.drop = %v, want [ALL]", c.SecurityContext.Capabilities.Drop)
			}
			if c.Resources.Limits["cpu"] == "" || c.Resources.Limits["memory"] == "" {
				t.Errorf("cpu and memory limits required: %v", c.Resources.Limits)
			}
		}
	}
	if !sawPolicy || !sawPod {
		t.Errorf("manifest missing items: policy=%v pod=%v", sawPolicy, sawPod)
	}
}

// requireKind skips the test unless a kind cluster answers.
func requireKind(t *testing.T) {
	t.Helper() // report failures at the caller's line, not here
	if testing.Short() {
		t.Skip("skipping kind test in -short mode")
	}
	if _, err := exec.LookPath("kubectl"); err != nil {
		t.Skip("kubectl not installed")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := exec.CommandContext(ctx, "kubectl", "--context", "kind-kind", "get", "--raw", "/readyz").Run(); err != nil {
		t.Skipf("no kind cluster (context kind-kind): %v", err)
	}
}

// startPod starts k and registers cleanup, so a failing test never leaves a
// pod behind. It returns the host commands Start ran.
func startPod(t *testing.T, k *Kind) []Result {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
	defer cancel()
	results, err := k.Start(ctx)
	// t.Cleanup runs after the test ends, even if it fails. Stop gets a
	// fresh context because the test's context may be gone by then.
	t.Cleanup(func() {
		cctx, ccancel := context.WithTimeout(context.Background(), time.Minute)
		defer ccancel()
		if _, err := k.Stop(cctx); err != nil {
			t.Errorf("cleanup stop: %v", err)
		}
	})
	if err != nil {
		t.Fatalf("start %s: %v (results: %+v)", k.PodName(), err, results)
	}
	return results
}

func TestKindLifecycle(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	startPod(t, k)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	// Exec returns stdout, exit code, and the exact command.
	r, err := k.Exec(ctx, "echo", "hi")
	if err != nil {
		t.Fatal(err)
	}
	if r.Stdout != "hi\n" || r.ExitCode != 0 {
		t.Errorf("echo hi: stdout=%q exit=%d stderr=%q", r.Stdout, r.ExitCode, r.Stderr)
	}
	want := []string{"kubectl", "--context", "kind-kind", "-n", "apg-sandbox", "exec", k.PodName(), "--", "echo", "hi"}
	if !slices.Equal(r.Args, want) {
		t.Errorf("Args = %q, want %q", r.Args, want)
	}
	t.Logf("ran: %s", strings.Join(r.Args, " "))

	// A failing command is data (ExitCode), not an error.
	r, err = k.Exec(ctx, "sh", "-c", "echo oops >&2; exit 3")
	if err != nil {
		t.Fatalf("non-zero exit should not be an error: %v", err)
	}
	if r.ExitCode != 3 || !strings.Contains(r.Stderr, "oops") {
		t.Errorf("exit 3: got exit=%d stderr=%q", r.ExitCode, r.Stderr)
	}

	// CopyIn, then read it back inside the pod.
	content := "copied in from the host\n"
	in := filepath.Join(t.TempDir(), "in.txt")
	if err := os.WriteFile(in, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	if r, err := k.CopyIn(ctx, in, "/workspace/in.txt"); err != nil {
		t.Fatalf("copy in: %v (%+v)", err, r)
	}
	r, err = k.Exec(ctx, "cat", "/workspace/in.txt")
	if err != nil || r.Stdout != content {
		t.Errorf("cat after CopyIn: stdout=%q err=%v", r.Stdout, err)
	}

	// CopyIn a directory with a trailing "/.": its contents land directly
	// in /workspace (without "/." kubectl cp would create /workspace/<name>).
	src := t.TempDir()
	if err := os.MkdirAll(filepath.Join(src, "a"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(src, "a", "b.txt"), []byte("nested\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if r, err := k.CopyIn(ctx, src+string(filepath.Separator)+".", "/workspace"); err != nil {
		t.Fatalf("copy in dir: %v (%+v)", err, r)
	}
	r, err = k.Exec(ctx, "cat", "/workspace/a/b.txt")
	if err != nil || r.Stdout != "nested\n" {
		t.Errorf("dir CopyIn: cat /workspace/a/b.txt stdout=%q stderr=%q err=%v", r.Stdout, r.Stderr, err)
	}

	// CopyOut a file the pod wrote, and compare on the host.
	if r, err := k.Exec(ctx, "sh", "-c", "echo made in the pod > /workspace/out.txt"); err != nil || r.ExitCode != 0 {
		t.Fatalf("write out.txt: %v (%+v)", err, r)
	}
	out := filepath.Join(t.TempDir(), "out.txt")
	if r, err := k.CopyOut(ctx, "/workspace/out.txt", out); err != nil {
		t.Fatalf("copy out: %v (%+v)", err, r)
	}
	got, err := os.ReadFile(out)
	if err != nil || string(got) != "made in the pod\n" {
		t.Errorf("CopyOut content = %q, err=%v", got, err)
	}

	// Stop deletes the pod.
	if r, err := k.Stop(ctx); err != nil {
		t.Fatalf("stop: %v (%+v)", err, r)
	}
	r, err = k.run(ctx, nil, "get", "pod", k.PodName())
	if err != nil || r.ExitCode == 0 || !strings.Contains(r.Stderr, "NotFound") {
		t.Errorf("pod should be gone: exit=%d stderr=%q err=%v", r.ExitCode, r.Stderr, err)
	}
}

// Probes run with coreutils timeout so a blocked connection fails in
// seconds instead of hanging.
var (
	tcpProbe = []string{"timeout", "10", "python", "-I", "-c",
		"import socket; socket.create_connection(('1.1.1.1', 443), timeout=5).close(); print('connected')"}
	dnsProbe = []string{"timeout", "10", "python", "-I", "-c",
		"import socket; print(socket.getaddrinfo('example.com', 443)[0][4])"}
)

func TestKindEgressBlocked(t *testing.T) {
	requireKind(t)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()

	// Control: same image and pod settings, but in a namespace with no
	// NetworkPolicy. If this cannot connect, the host has no internet, and
	// a failed connection from the sandbox would prove nothing.
	control, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	control.Namespace = "apg-control"
	control.skipEgressPolicy = true
	startPod(t, control)
	for _, probe := range [][]string{tcpProbe, dnsProbe} {
		r, err := control.Exec(ctx, probe...)
		if err != nil {
			t.Fatal(err)
		}
		if r.ExitCode != 0 {
			t.Skipf("control pod has no internet, cannot prove the block: %s %s", r.Stdout, r.Stderr)
		}
		t.Logf("control (no policy): exit=%d %s", r.ExitCode, strings.TrimSpace(r.Stdout))
	}

	// Sandbox: the deny-all-egress policy is on, so both probes must fail.
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	results := startPod(t, k)
	// Start's own egress probes: "open" ones show the gap it waited out.
	var seen []string
	for _, r := range results {
		if slices.Equal(r.Args[len(r.Args)-len(egressProbe):], egressProbe) {
			seen = append(seen, strings.TrimSpace(r.Stdout))
		}
	}
	t.Logf("Start's egress probes: %v", seen)
	for name, probe := range map[string][]string{"tcp 1.1.1.1:443": tcpProbe, "dns example.com": dnsProbe} {
		r, err := k.Exec(ctx, probe...)
		if err != nil {
			t.Fatal(err)
		}
		if r.ExitCode == 0 {
			t.Errorf("%s: sandbox reached the internet: %s", name, r.Stdout)
			continue
		}
		// Log the last line of Python's error, skipping kubectl's own
		// "command terminated with exit code N" line.
		last := ""
		for _, line := range strings.Split(strings.TrimSpace(r.Stderr), "\n") {
			if line != "" && !strings.HasPrefix(line, "command terminated") {
				last = line
			}
		}
		t.Logf("sandbox (policy on) %s: blocked, exit=%d %s", name, r.ExitCode, last)
	}
}
