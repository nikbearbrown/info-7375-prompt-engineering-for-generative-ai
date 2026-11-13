package stop

import (
	"os/exec"
	"strings"
	"testing"
)

// CleanPycacheCmd, run exactly as written (argv, no shell) in the sandbox
// image: it deletes __pycache__ directories and every other *.pyc file or
// symlink, and leaves source files and a directory that merely ends in
// .pyc alone.
func TestCleanPycacheInImage(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping docker test in -short mode")
	}
	if _, err := exec.LookPath("docker"); err != nil {
		t.Skip("docker not installed")
	}
	if err := exec.Command("docker", "image", "inspect", "apg-sandbox:dev").Run(); err != nil {
		t.Skip("image apg-sandbox:dev not built")
	}
	// sh only builds the test tree; then "$@" runs CleanPycacheCmd as
	// separate arguments, as kubectl exec would.
	setup := `cd /workspace && mkdir -p calc/__pycache__ tests/__pycache__ dir.pyc &&
touch calc/ops.py calc/ops.pyc calc/__pycache__/ops.cpython-312.pyc tests/__pycache__/t.pyc dir.pyc/keep.txt &&
ln -s /etc/hostname link.pyc && "$@" && find /workspace | sort`
	args := append([]string{"run", "--rm", "--network", "none", "apg-sandbox:dev", "sh", "-c", setup, "sh"}, CleanPycacheCmd...)
	out, err := exec.Command("docker", args...).CombinedOutput()
	if err != nil {
		t.Fatalf("docker run: %v: %s", err, out)
	}
	got := strings.TrimSpace(string(out))
	want := strings.Join([]string{"/workspace", "/workspace/calc", "/workspace/calc/ops.py", "/workspace/dir.pyc", "/workspace/dir.pyc/keep.txt", "/workspace/tests"}, "\n")
	if got != want {
		t.Errorf("left after cleanup:\n%s\nwant:\n%s", got, want)
	}
}
