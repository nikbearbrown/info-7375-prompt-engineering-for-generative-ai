package sandbox

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os/exec"
	"strings"
	"time"
)

// Kind is a Sandbox backed by one pod in a local kind cluster.
// It drives the cluster with the kubectl CLI through os/exec.
//
// Known limit: when a context expires, the kubectl process on the host is
// killed, but the command inside the pod may keep running until Stop
// deletes the pod.
type Kind struct {
	Context   string // kubectl context; always passed, so no other cluster is ever used
	Namespace string
	Image     string
	CPU       string // limit and request, e.g. "500m"
	Memory    string // limit and request, e.g. "256Mi"

	pod string // pod name, unique per run

	// skipEgressPolicy leaves out the deny-egress NetworkPolicy. It is
	// lowercase (unexported), so only code in this package can set it; the
	// egress test uses it for a control pod that is supposed to reach the
	// internet.
	skipEgressPolicy bool
}

// This line does not run anything: it makes the compiler check that *Kind
// has every method of Sandbox. The blank identifier _ discards the value.
var _ Sandbox = (*Kind)(nil)

// NewKind returns a Kind with the project defaults and a fresh pod name.
func NewKind() (*Kind, error) {
	b := make([]byte, 4)
	if _, err := rand.Read(b); err != nil {
		return nil, fmt.Errorf("pod name: %w", err)
	}
	return &Kind{
		Context:   "kind-kind",
		Namespace: "apg-sandbox",
		Image:     "apg-sandbox:dev",
		CPU:       "500m",
		Memory:    "256Mi",
		pod:       "apg-" + hex.EncodeToString(b), // e.g. apg-1a2b3c4d
	}, nil
}

// PodName returns the name of the pod this sandbox uses.
func (k *Kind) PodName() string { return k.pod }

// Start applies the namespace, the NetworkPolicy, and the pod, waits for
// the pod to be Ready, then waits until egress is actually blocked. If any
// step after apply fails, it deletes the pod.
func (k *Kind) Start(ctx context.Context) ([]Result, error) {
	m, err := json.Marshal(k.manifest())
	if err != nil {
		return nil, fmt.Errorf("manifest: %w", err)
	}
	var results []Result

	// fail deletes the pod (best effort) and returns err. It is a closure:
	// a function value that can read and change results and k from Start.
	fail := func(err error) ([]Result, error) {
		// WithoutCancel keeps ctx's values but drops its deadline (it may
		// already have expired), and WithTimeout gives cleanup its own 30s.
		cctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), 30*time.Second)
		defer cancel() // defer runs cancel when fail returns, freeing the timer
		dr, _ := k.Stop(cctx)
		return append(results, dr), err
	}

	// "-f -" means read the manifest from stdin. kubectl accepts JSON as
	// well as YAML, so the encoding/json output can be piped straight in.
	r, err := k.run(ctx, bytes.NewReader(m), "apply", "-f", "-")
	results = append(results, r)
	if err := check(r, err); err != nil {
		return fail(fmt.Errorf("apply: %w", err))
	}

	r, err = k.run(ctx, nil, "wait", "--for=condition=Ready", "pod/"+k.pod, "--timeout=120s")
	results = append(results, r)
	if err := check(r, err); err != nil {
		return fail(fmt.Errorf("wait for pod: %w", err))
	}

	if !k.skipEgressPolicy {
		probes, err := k.waitEgressBlocked(ctx, 30*time.Second)
		results = append(results, probes...) // probes... spreads the slice
		if err != nil {
			return fail(err)
		}
	}
	return results, nil
}

// egressProbe prints "blocked" if a TCP connection from the pod to
// 1.1.1.1:443 fails, and "open" if it succeeds. The text between backticks
// is a Go raw string: newlines and quotes are kept exactly as written.
var egressProbe = []string{"timeout", "5", "python", "-I", "-c", `import socket
try:
    socket.create_connection(("1.1.1.1", 443), timeout=2).close()
    print("open")
except OSError:
    print("blocked")`}

// waitEgressBlocked runs egressProbe until it reports "blocked".
//
// Why: kindnet enforces the NetworkPolicy, but it programs the rules for a
// new pod about 1-2 seconds after the pod is Ready (measured Nov 11, 2026).
// Without this wait, the agent's first command could run with egress open.
func (k *Kind) waitEgressBlocked(ctx context.Context, limit time.Duration) ([]Result, error) {
	var results []Result
	deadline := time.Now().Add(limit)
	for {
		r, err := k.Exec(ctx, egressProbe...)
		results = append(results, r)
		if err != nil {
			return results, fmt.Errorf("egress probe: %w", err)
		}
		switch strings.TrimSpace(r.Stdout) {
		case "blocked":
			return results, nil
		case "open":
			// Still open; try again below.
		default:
			return results, fmt.Errorf("egress probe: unexpected result (exit %d): %q %q", r.ExitCode, r.Stdout, r.Stderr)
		}
		if time.Now().After(deadline) {
			return results, fmt.Errorf("egress still open after %s: NetworkPolicy not enforced", limit)
		}
		// select waits for whichever happens first: ctx ending or 500ms passing.
		select {
		case <-ctx.Done():
			return results, ctx.Err()
		case <-time.After(500 * time.Millisecond):
		}
	}
}

// Exec runs cmd in the pod. There is no shell on the host side: cmd goes
// to kubectl as separate arguments after "--". Wrap it in "sh", "-c" if a
// shell inside the pod is wanted.
func (k *Kind) Exec(ctx context.Context, cmd ...string) (Result, error) {
	if len(cmd) == 0 {
		return Result{}, errors.New("exec: empty command")
	}
	// append(a, b...) spreads the slice b into separate arguments.
	args := append([]string{"exec", k.pod, "--"}, cmd...)
	return k.run(ctx, nil, args...)
}

// CopyIn copies a host file or directory into the pod with kubectl cp
// (which uses tar inside the pod). Like cp -r, copying dir to an existing
// directory creates dir inside it; pass "dir/." to copy only its contents.
func (k *Kind) CopyIn(ctx context.Context, hostPath, sandboxPath string) (Result, error) {
	r, err := k.run(ctx, nil, "cp", hostPath, k.pod+":"+sandboxPath)
	return r, check(r, err)
}

// CopyOut copies a file or directory from the pod to the host. The content
// comes from the agent's environment, so treat it as untrusted; kubectl cp
// refuses archive paths that would land outside hostPath.
func (k *Kind) CopyOut(ctx context.Context, sandboxPath, hostPath string) (Result, error) {
	r, err := k.run(ctx, nil, "cp", k.pod+":"+sandboxPath, hostPath)
	return r, check(r, err)
}

// Stop deletes the pod and waits until it is gone. --now skips the usual
// 30-second grace period. The namespace and NetworkPolicy are shared by all
// runs, so they stay.
func (k *Kind) Stop(ctx context.Context) (Result, error) {
	r, err := k.run(ctx, nil, "delete", "pod", k.pod, "--ignore-not-found", "--wait", "--now")
	return r, check(r, err)
}

// run executes one kubectl command and records it. stdin may be nil.
// The returned error is non-nil only if kubectl could not run or ctx
// expired; a non-zero exit is reported in Result.ExitCode.
func (k *Kind) run(ctx context.Context, stdin io.Reader, args ...string) (Result, error) {
	full := append([]string{"kubectl", "--context", k.Context, "-n", k.Namespace}, args...)
	r := Result{Args: full}

	// CommandContext kills kubectl if ctx is cancelled or times out.
	// full[0] is the program, full[1:] are its arguments (no shell).
	cmd := exec.CommandContext(ctx, full[0], full[1:]...)
	var stdout, stderr bytes.Buffer
	cmd.Stdin = stdin
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	r.Stdout = stdout.String()
	r.Stderr = stderr.String()

	if ctxErr := ctx.Err(); ctxErr != nil {
		r.ExitCode = -1
		return r, fmt.Errorf("%s: %w", strings.Join(args, " "), ctxErr)
	}
	// errors.As checks whether err is (or wraps) an *exec.ExitError, which
	// means kubectl ran and exited non-zero. If so, copy the code into r.
	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		r.ExitCode = exitErr.ExitCode()
		return r, nil
	}
	if err != nil { // e.g. kubectl not installed
		r.ExitCode = -1
		return r, err
	}
	return r, nil
}

// check turns a non-zero exit into an error, for harness steps that must
// succeed.
func check(r Result, err error) error {
	if err != nil {
		return err
	}
	if r.ExitCode != 0 {
		return fmt.Errorf("exit %d: %s", r.ExitCode, strings.TrimSpace(r.Stderr))
	}
	return nil
}

// obj is shorthand for a JSON object; any means "value of any type".
type obj = map[string]any

// manifest returns a Kubernetes List holding the namespace, the
// deny-egress NetworkPolicy (unless skipEgressPolicy), and the pod.
func (k *Kind) manifest() obj {
	items := []any{
		obj{
			"apiVersion": "v1",
			"kind":       "Namespace",
			"metadata":   obj{"name": k.Namespace},
		},
	}
	if !k.skipEgressPolicy {
		items = append(items, obj{
			"apiVersion": "networking.k8s.io/v1",
			"kind":       "NetworkPolicy",
			"metadata":   obj{"name": "deny-all-egress", "namespace": k.Namespace},
			"spec": obj{
				// An empty podSelector selects every pod in the namespace.
				"podSelector": obj{},
				// Listing Egress with no egress rules means no egress is
				// allowed, DNS included.
				"policyTypes": []string{"Egress"},
			},
		})
	}
	resources := obj{"cpu": k.CPU, "memory": k.Memory}
	items = append(items, obj{
		"apiVersion": "v1",
		"kind":       "Pod",
		"metadata": obj{
			"name":      k.pod,
			"namespace": k.Namespace,
			"labels":    obj{"app": "apg-sandbox"},
		},
		"spec": obj{
			"automountServiceAccountToken": false, // no API token in the pod
			"enableServiceLinks":           false, // no service env vars in the pod
			"restartPolicy":                "Never",
			"activeDeadlineSeconds":        3600, // pod ends itself if Stop never runs
			"securityContext": obj{
				"runAsNonRoot":   true,
				"runAsUser":      1000,
				"runAsGroup":     1000,
				"seccompProfile": obj{"type": "RuntimeDefault"},
			},
			"containers": []any{obj{
				"name":            "sandbox",
				"image":           k.Image,
				"imagePullPolicy": "Never", // image comes from kind load, never a registry
				// The working directory of every kubectl exec. kubectl exec
				// has no option for it, so it is set here rather than left to
				// the image's WORKDIR: the policy resolves relative paths
				// against /workspace, so commands must run there.
				"workingDir": "/workspace",
				"securityContext": obj{
					"allowPrivilegeEscalation": false,
					"capabilities":             obj{"drop": []string{"ALL"}},
				},
				// requests == limits: the pod gets exactly this much.
				"resources": obj{"limits": resources, "requests": resources},
			}},
		},
	})
	return obj{"apiVersion": "v1", "kind": "List", "items": items}
}
