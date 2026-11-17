package sandbox

// T4.4: each pod limit is not only set (TestManifest) but holds. Every test
// here tries to break a limit from inside a real kind pod and checks that
// the attempt fails. The t.Logf lines are the evidence; run with -v.
//
// The memory and fork tests can only hurt the kind node if their limit is
// missing, so each one first confirms its limit and stops (t.Fatal) before
// doing anything if the limit is not there. Each also caps itself.

import (
	"context"
	"encoding/json"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"
)

// py runs a Python script in the pod with python -I (isolated mode: no
// user site-packages, no PYTHON* variables), under coreutils timeout.
// A harness failure (kubectl could not run) ends the test.
func py(t *testing.T, ctx context.Context, k *Kind, secs int, script string) Result {
	t.Helper()
	r, err := k.Exec(ctx, "timeout", strconv.Itoa(secs), "python", "-I", "-c", script)
	if err != nil {
		t.Fatalf("exec: %v", err)
	}
	return r
}

// exec1 runs one program in the pod (argv, no shell).
func exec1(t *testing.T, ctx context.Context, k *Kind, cmd ...string) Result {
	t.Helper()
	r, err := k.Exec(ctx, cmd...)
	if err != nil {
		t.Fatalf("exec %v: %v", cmd, err)
	}
	return r
}

// logResult writes a command's output into the test log, one line each,
// dropping kubectl's own "command terminated" line.
func logResult(t *testing.T, label string, r Result) {
	t.Helper()
	t.Logf("%s: exit=%d", label, r.ExitCode)
	for _, s := range []string{r.Stdout, r.Stderr} {
		for _, line := range strings.Split(strings.TrimRight(s, "\n"), "\n") {
			if line != "" && !strings.HasPrefix(line, "command terminated") {
				t.Logf("  %s", line)
			}
		}
	}
}

// wantLines fails the test for each wanted line missing from out.
func wantLines(t *testing.T, out string, want ...string) {
	t.Helper()
	lines := strings.Split(out, "\n")
	for _, w := range want {
		found := false
		for _, l := range lines {
			if strings.TrimSpace(l) == w {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("missing line %q", w)
		}
	}
}

func TestIsolation(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	startPod(t, k)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()

	t.Run("non_root", func(t *testing.T) {
		r := exec1(t, ctx, k, "id")
		logResult(t, "id", r)
		if !strings.HasPrefix(r.Stdout, "uid=1000(apg) gid=1000(apg)") {
			t.Errorf("id = %q, want uid=1000 gid=1000", r.Stdout)
		}
		r = py(t, ctx, k, 10, `
import os
for l in open('/proc/1/status'):
    if l.startswith(('Uid:', 'Gid:')): print('pid1', ' '.join(l.split()))
try:
    os.setuid(0); print('setuid(0) SUCCEEDED')
except OSError as e:
    print('setuid(0) errno', e.errno)
`)
		logResult(t, "PID 1's ids and setuid(0)", r)
		wantLines(t, r.Stdout, "pid1 Uid: 1000 1000 1000 1000", "pid1 Gid: 1000 1000 1000 1000", "setuid(0) errno 1")
	})

	t.Run("capabilities", func(t *testing.T) {
		r := py(t, ctx, k, 10, `
import os
for l in open('/proc/self/status'):
    if l.startswith('Cap'): print(' '.join(l.split()))
open('/workspace/apg-cap-probe', 'w').close()
for name, fn in [('chown(file, 0, 0)', lambda: os.chown('/workspace/apg-cap-probe', 0, 0)),
                 ('setgroups([0])', lambda: os.setgroups([0]))]:
    try:
        fn(); print(name, 'SUCCEEDED')
    except OSError as e:
        print(name, 'errno', e.errno)
os.remove('/workspace/apg-cap-probe')
`)
		logResult(t, "capability sets and privileged calls", r)
		wantLines(t, r.Stdout,
			"CapInh: 0000000000000000", "CapPrm: 0000000000000000", "CapEff: 0000000000000000",
			"CapBnd: 0000000000000000", "CapAmb: 0000000000000000",
			"chown(file, 0, 0) errno 1", "setgroups([0]) errno 1")
	})

	t.Run("no_privilege_escalation", func(t *testing.T) {
		r := py(t, ctx, k, 10, `
import os
for l in open('/proc/self/status'):
    if l.startswith(('NoNewPrivs:', 'Seccomp:')): print(' '.join(l.split()))
try:
    os.unshare(os.CLONE_NEWUSER); print('unshare(CLONE_NEWUSER) SUCCEEDED')
except OSError as e:
    print('unshare(CLONE_NEWUSER) errno', e.errno)
`)
		logResult(t, "no_new_privs, seccomp, user namespace", r)
		// Seccomp 2 is filter mode: the RuntimeDefault profile is loaded.
		wantLines(t, r.Stdout, "NoNewPrivs: 1", "Seccomp: 2", "unshare(CLONE_NEWUSER) errno 1")

		// setuid-root programs exist in the image; with no_new_privs the
		// setuid bit does not raise privileges, so mount still fails.
		r = exec1(t, ctx, k, "find", "/", "-xdev", "-perm", "-4000", "-type", "f")
		logResult(t, "setuid programs in the image", r)
		if !strings.Contains(r.Stdout, "/mount") {
			t.Fatalf("no setuid mount in the image to try: %q", r.Stdout)
		}
		exec1(t, ctx, k, "mkdir", "-p", "/tmp/apg-mnt")
		r = exec1(t, ctx, k, "mount", "-t", "tmpfs", "none", "/tmp/apg-mnt")
		logResult(t, "mount -t tmpfs none /tmp/apg-mnt", r)
		if r.ExitCode == 0 {
			t.Error("mount succeeded")
		}
	})

	t.Run("writes_outside_workspace", func(t *testing.T) {
		r := py(t, ctx, k, 10, `
import os
for d in ['/', '/etc', '/usr', '/usr/local/lib/python3.12/site-packages', '/var', '/root', '/opt',
          '/workspace', '/tmp', '/var/tmp', '/dev/shm', '/home/apg']:
    p = os.path.join(d, 'apg-write-probe')
    try:
        with open(p, 'x') as f: f.write('x')
        os.remove(p); print('WRITABLE', d)
    except OSError as e:
        print('DENIED', d, 'errno', e.errno)
try:
    open('/etc/passwd', 'a').close(); print('WRITABLE /etc/passwd')
except OSError as e:
    print('DENIED /etc/passwd errno', e.errno)
`)
		logResult(t, "create a file in each directory", r)
		// errno 13 is EACCES: denied by file permissions (the root
		// filesystem is not read-only; that would be errno 30, EROFS).
		wantLines(t, r.Stdout,
			"DENIED / errno 13", "DENIED /etc errno 13", "DENIED /usr errno 13",
			"DENIED /usr/local/lib/python3.12/site-packages errno 13", "DENIED /var errno 13",
			"DENIED /root errno 13", "DENIED /opt errno 13", "DENIED /etc/passwd errno 13",
			"WRITABLE /workspace", "WRITABLE /tmp")
	})

	t.Run("no_service_account_token", func(t *testing.T) {
		r := py(t, ctx, k, 15, `
import os, socket
print('/var/run/secrets/kubernetes.io exists:', os.path.exists('/var/run/secrets/kubernetes.io'))
toks = []
for d in ['/var/run/secrets', '/run/secrets']:
    for root, dirs, files in os.walk(d):
        toks += [os.path.join(root, f) for f in files if 'token' in f]
print('token files:', toks)
# KUBERNETES_SERVICE_HOST/PORT name the API server's Service; 10.96.0.1:443
# is kind's default, used only if the variables are missing.
src = 'env' if 'KUBERNETES_SERVICE_HOST' in os.environ else 'default'
h = os.environ.get('KUBERNETES_SERVICE_HOST', '10.96.0.1')
p = int(os.environ.get('KUBERNETES_SERVICE_PORT', '443'))
print('api server', h, p, 'from', src)
try:
    socket.create_connection((h, p), timeout=5).close(); print('api server CONNECTED')
except OSError as e:
    print('api server blocked:', type(e).__name__)
`)
		logResult(t, "service-account token and API server", r)
		wantLines(t, r.Stdout, "/var/run/secrets/kubernetes.io exists: False", "token files: []")
		if !strings.Contains(r.Stdout, "api server blocked:") {
			t.Errorf("API server reachable from the pod: %q", r.Stdout)
		}
	})

	t.Run("cpu_limit", func(t *testing.T) {
		// Four processes spin for 3 s of wall time. Unlimited, that is up
		// to 12 CPU-seconds; with a 500m limit it must stay near 1.5.
		r := py(t, ctx, k, 20, `
import time, multiprocessing as mp
print('cpu.max', open('/sys/fs/cgroup/cpu.max').read().strip())
def stat():
    d = dict(l.split() for l in open('/sys/fs/cgroup/cpu.stat'))
    return int(d['usage_usec']), int(d['nr_throttled'])
def spin(sec):
    end = time.monotonic() + sec
    while time.monotonic() < end: pass
u0, t0 = stat(); w0 = time.monotonic()
ps = [mp.Process(target=spin, args=(3,)) for _ in range(4)]
for p in ps: p.start()
for p in ps: p.join()
u1, t1 = stat(); w1 = time.monotonic()
print('wall_seconds', round(w1 - w0, 3))
print('cpu_seconds', round((u1 - u0) / 1e6, 3))
print('cpus_used', round((u1 - u0) / 1e6 / (w1 - w0), 3))
print('throttled_periods', t1 - t0)
`)
		logResult(t, "4 busy processes for 3 s", r)
		wantLines(t, r.Stdout, "cpu.max 50000 100000")
		vals := map[string]float64{}
		for _, l := range strings.Split(r.Stdout, "\n") {
			if f := strings.Fields(l); len(f) == 2 {
				if v, err := strconv.ParseFloat(f[1], 64); err == nil {
					vals[f[0]] = v
				}
			}
		}
		// 0.65 = the 0.5 CPU limit plus 30% for scheduler slack.
		if c, ok := vals["cpus_used"]; !ok || c > 0.65 {
			t.Errorf("cpus_used = %v (ok=%v), want <= 0.65", c, ok)
		}
		if n := vals["throttled_periods"]; n <= 0 {
			t.Errorf("throttled_periods = %v, want > 0", n)
		}
	})
}

// TestIsolationMemory runs a memory hog in its own pod: the OOM kill may
// take the whole container down.
func TestIsolationMemory(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	startPod(t, k)
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
	defer cancel()

	// Safety gate: allocate nothing unless the 256Mi limit is in place and
	// the container cannot spill into swap.
	r := py(t, ctx, k, 10, `
print('memory.max', open('/sys/fs/cgroup/memory.max').read().strip())
print('memory.swap.max', open('/sys/fs/cgroup/memory.swap.max').read().strip())
`)
	logResult(t, "cgroup memory settings", r)
	if !strings.Contains(r.Stdout, "memory.max 268435456\n") {
		t.Fatalf("memory limit is not 256Mi: %q; not running the hog", r.Stdout)
	}
	if !strings.Contains(r.Stdout, "memory.swap.max 0\n") {
		t.Fatalf("swap is allowed: %q; the hog would swap instead of being killed; not running it", r.Stdout)
	}

	// The hog fills 16 MiB at a time (bytes * n writes every byte, so the
	// pages are really used) and prints the total. It stops by itself at
	// 1 GiB, so even without the limit it could not take more.
	r = py(t, ctx, k, 30, `
chunks = []
for i in range(1, 65):
    chunks.append(b'\x01' * (16 << 20))
    print(i * 16, flush=True)
print('REACHED 1024 MiB')
`)
	lines := strings.Fields(r.Stdout)
	last := ""
	if len(lines) > 0 {
		last = lines[len(lines)-1]
	}
	t.Logf("memory hog: exit=%d, last MiB printed=%s, stderr=%q", r.ExitCode, last, strings.TrimSpace(r.Stderr))
	if r.ExitCode != 137 {
		t.Errorf("exit = %d, want 137 (SIGKILL by the OOM killer)", r.ExitCode)
	}
	mib, err := strconv.Atoi(last)
	if err != nil || mib >= 256 {
		t.Errorf("last MiB printed = %q, want a number below 256", last)
	}

	// What Kubernetes recorded. The kill may have taken the container (and
	// so the pod) down with it; poll briefly for the status to settle.
	for i := 0; i < 10; i++ {
		pr, err := k.run(ctx, nil, "get", "pod", k.PodName(), "-o",
			"jsonpath={.status.phase} {.status.containerStatuses[0].state.terminated.reason}")
		if err != nil {
			t.Fatal(err)
		}
		if strings.Contains(pr.Stdout, "OOMKilled") || i == 9 {
			t.Logf("pod status (phase, terminated reason): %q exit=%d", pr.Stdout, pr.ExitCode)
			break
		}
		time.Sleep(time.Second)
	}
}

// TestIsolationPids tries to fork past the pod's process limit, in its own
// pod.
func TestIsolationPids(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
	defer cancel()

	// Safety gate: fork nothing unless the kubelet has the pids limit. The
	// limit sits on the pod's cgroup, a parent the container cannot see,
	// so it is read from the kubelet's live config (configz).
	r, err := k.run(ctx, nil, "get", "--raw", "/api/v1/nodes/kind-control-plane/proxy/configz")
	if err != nil || r.ExitCode != 0 {
		t.Fatalf("configz: %v %q", err, r.Stderr)
	}
	var cz struct {
		KubeletConfig struct {
			PodPidsLimit int `json:"podPidsLimit"`
		} `json:"kubeletconfig"`
	}
	if err := json.Unmarshal([]byte(r.Stdout), &cz); err != nil {
		t.Fatal(err)
	}
	t.Logf("kubelet configz podPidsLimit: %d", cz.KubeletConfig.PodPidsLimit)
	if cz.KubeletConfig.PodPidsLimit != 256 {
		t.Fatalf("podPidsLimit is %d, not 256; not running the fork test", cz.KubeletConfig.PodPidsLimit)
	}

	startPod(t, k)
	// Each child blocks reading a pipe. When the parent closes the write
	// end, every child reads end-of-file and exits. The loop stops at the
	// first failed fork, or after 400 forks whatever happens.
	r = py(t, ctx, k, 60, `
import os, errno
r, w = os.pipe()
kids, err = [], None
for i in range(400):
    try:
        pid = os.fork()
    except OSError as e:
        err = e
        break
    if pid == 0:
        os.close(w)
        os.read(r, 1)
        os._exit(0)
    kids.append(pid)
print('forked', len(kids))
print('fork error', 'none' if err is None else errno.errorcode.get(err.errno), flush=True)
os.close(w)
for pid in kids:
    os.waitpid(pid, 0)
print('reaped', len(kids))
`)
	logResult(t, "fork until it fails (cap 400)", r)
	if !strings.Contains(r.Stdout, "fork error EAGAIN") {
		t.Errorf("fork never failed with EAGAIN: %q", r.Stdout)
	}
	for _, l := range strings.Split(r.Stdout, "\n") {
		if f := strings.Fields(l); len(f) == 2 && f[0] == "forked" {
			if n, _ := strconv.Atoi(f[1]); n >= 256 {
				t.Errorf("forked %d children, want fewer than 256", n)
			}
		}
	}

	// The pod still works afterwards.
	r = exec1(t, ctx, k, "echo", "ok")
	logResult(t, "echo ok after the fork test", r)
	if r.Stdout != "ok\n" {
		t.Errorf("pod unusable after the fork test: %q", r.Stdout)
	}
}

// TestKindConfigPidsLimit keeps the pids limit in the cluster config (no
// cluster needed): without it, the fork test refuses to run.
func TestKindConfigPidsLimit(t *testing.T) {
	b, err := os.ReadFile("../../sandbox/kind.yaml")
	if err != nil {
		t.Fatal(err)
	}
	for _, l := range strings.Split(string(b), "\n") {
		if strings.TrimSpace(l) == "podPidsLimit: 256" {
			return
		}
	}
	t.Error("sandbox/kind.yaml has no podPidsLimit: 256 line")
}
