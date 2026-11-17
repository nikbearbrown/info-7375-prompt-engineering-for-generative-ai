package sandbox

// D29: the pod's disk use is capped two ways.
//   - /workspace and /tmp are 32Mi tmpfs volumes: the kernel refuses a
//     write past the size, and the pod keeps working.
//   - The rest of the writable layer has a 64Mi ephemeral-storage limit:
//     the kubelet evicts the pod some seconds after it is passed.

import (
	"context"
	"encoding/json"
	"strings"
	"testing"
	"time"
)

// TestManifestStorage checks the volumes and the limit without a cluster.
func TestManifestStorage(t *testing.T) {
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	b, err := json.Marshal(k.manifest())
	if err != nil {
		t.Fatal(err)
	}
	var list struct {
		Items []struct {
			Kind string `json:"kind"`
			Spec struct {
				Volumes []struct {
					Name     string `json:"name"`
					EmptyDir struct {
						Medium    string `json:"medium"`
						SizeLimit string `json:"sizeLimit"`
					} `json:"emptyDir"`
				} `json:"volumes"`
				Containers []struct {
					VolumeMounts []struct {
						Name      string `json:"name"`
						MountPath string `json:"mountPath"`
					} `json:"volumeMounts"`
					Resources struct {
						Limits   map[string]string `json:"limits"`
						Requests map[string]string `json:"requests"`
					} `json:"resources"`
				} `json:"containers"`
			} `json:"spec"`
		} `json:"items"`
	}
	if err := json.Unmarshal(b, &list); err != nil {
		t.Fatal(err)
	}
	for _, it := range list.Items {
		if it.Kind != "Pod" {
			continue
		}
		vols := map[string]string{} // name -> "medium sizeLimit"
		for _, v := range it.Spec.Volumes {
			vols[v.Name] = v.EmptyDir.Medium + " " + v.EmptyDir.SizeLimit
		}
		mounts := map[string]string{} // mountPath -> volume name
		for _, m := range it.Spec.Containers[0].VolumeMounts {
			mounts[m.MountPath] = m.Name
		}
		for _, p := range []struct{ path, vol string }{{"/workspace", "workspace"}, {"/tmp", "tmp"}} {
			if mounts[p.path] != p.vol || vols[p.vol] != "Memory 32Mi" {
				t.Errorf("%s: mounted volume %q (%q), want %q as Memory 32Mi", p.path, mounts[p.path], vols[p.vol], p.vol)
			}
		}
		res := it.Spec.Containers[0].Resources
		if res.Limits["ephemeral-storage"] != "64Mi" || res.Requests["ephemeral-storage"] != "64Mi" {
			t.Errorf("ephemeral-storage = limit %q request %q, want 64Mi", res.Limits["ephemeral-storage"], res.Requests["ephemeral-storage"])
		}
		return
	}
	t.Fatal("no pod in the manifest")
}

// TestIsolationScratchFull fills /workspace and /tmp past their size: the
// write fails, and the pod stays usable.
func TestIsolationScratchFull(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	startPod(t, k)
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Minute)
	defer cancel()

	// Safety gate: write nothing unless both are 32 MiB tmpfs mounts.
	// /proc/mounts lists tmpfs sizes in KiB (32Mi = 32768k).
	r := py(t, ctx, k, 10, `
for l in open('/proc/mounts'):
    f = l.split()
    if f[1] in ('/workspace', '/tmp'):
        size = [o for o in f[3].split(',') if o.startswith('size=')]
        print('mount', f[1], f[2], size[0] if size else 'size=none')
`)
	logResult(t, "mounts", r)
	wantLines(t, r.Stdout, "mount /workspace tmpfs size=32768k", "mount /tmp tmpfs size=32768k")
	if t.Failed() {
		t.Fatal("not 32 MiB tmpfs mounts; not filling them")
	}

	for _, dir := range []string{"/workspace", "/tmp"} {
		// Write 1 MiB at a time until the write fails, at most 64 MiB.
		// DIR in the script is replaced by the directory to fill.
		r = py(t, ctx, k, 30, strings.ReplaceAll(`
import os
p = 'DIR/apg-fill'
n, err = 0, None
with open(p, 'wb') as f:
    try:
        for n in range(1, 65):
            f.write(b'\x01' * (1 << 20))
            f.flush()
            os.fsync(f.fileno())
        n += 1
    except OSError as e:
        err = e
print('MiB written before the error', n - 1)
print('error', 'none' if err is None else os.strerror(err.errno))
os.remove(p)
open('DIR/after', 'w').write('ok')
print('small write after removing it:', open('DIR/after').read())
os.remove('DIR/after')
`, "DIR", dir))
		logResult(t, "fill "+dir, r)
		wantLines(t, r.Stdout, "error No space left on device", "small write after removing it: ok")
	}

	r = exec1(t, ctx, k, "echo", "ok")
	logResult(t, "echo ok after filling both", r)
	if r.Stdout != "ok\n" {
		t.Errorf("pod unusable: %q", r.Stdout)
	}
}

// TestIsolationDiskEviction writes past the ephemeral-storage limit
// outside the tmpfs volumes, in its own pod: the kubelet evicts the pod.
func TestIsolationDiskEviction(t *testing.T) {
	requireKind(t)
	k, err := NewKind()
	if err != nil {
		t.Fatal(err)
	}
	startPod(t, k)
	ctx, cancel := context.WithTimeout(context.Background(), 4*time.Minute)
	defer cancel()

	// Safety gate: the limit must be on the running pod.
	r, err := k.run(ctx, nil, "get", "pod", k.PodName(), "-o",
		"jsonpath={.spec.containers[0].resources.limits.ephemeral-storage}")
	if err != nil || strings.TrimSpace(r.Stdout) != "64Mi" {
		t.Fatalf("pod ephemeral-storage limit = %q (err %v); not writing", r.Stdout, err)
	}
	t.Logf("pod ephemeral-storage limit: %s", r.Stdout)

	// 96 MiB into /home/apg (the image's writable layer), a fixed amount.
	r = py(t, ctx, k, 60, `
with open('/home/apg/apg-fill', 'wb') as f:
    for i in range(96):
        f.write(b'\x01' * (1 << 20))
print('wrote 96 MiB to /home/apg')
`)
	logResult(t, "write past the limit", r)

	// The kubelet checks usage periodically, so wait for the eviction.
	start := time.Now()
	var status string
	for time.Since(start) < 2*time.Minute {
		pr, err := k.run(ctx, nil, "get", "pod", k.PodName(), "-o", "jsonpath={.status.phase}|{.status.reason}|{.status.message}")
		if err != nil {
			t.Fatal(err)
		}
		status = pr.Stdout
		if strings.HasPrefix(status, "Failed|") {
			break
		}
		time.Sleep(2 * time.Second)
	}
	t.Logf("pod status after %.0fs: %s", time.Since(start).Seconds(), status)
	if !strings.HasPrefix(status, "Failed|Evicted|") || !strings.Contains(status, "ephemeral local storage") {
		t.Errorf("pod not evicted for ephemeral storage: %q", status)
	}
}
