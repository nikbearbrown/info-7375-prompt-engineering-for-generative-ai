package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"time"
)

// taskDirs returns every tasks/NNN-* directory.
func taskDirs(t *testing.T) []string {
	t.Helper()
	dirs, err := filepath.Glob(filepath.Join("..", "..", "tasks", "[0-9][0-9][0-9]-*"))
	if err != nil || len(dirs) < 15 {
		t.Fatalf("want at least 15 tasks, found %d (%v)", len(dirs), err)
	}
	return dirs
}

// protected reads the contract's required_output.unchanged_files.
func protected(t *testing.T, dir string) []string {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(dir, "contract.json"))
	if err != nil {
		t.Fatal(err)
	}
	var c struct {
		RequiredOutput struct {
			UnchangedFiles []string `json:"unchanged_files"`
		} `json:"required_output"`
	}
	if err := json.Unmarshal(b, &c); err != nil {
		t.Fatal(err)
	}
	if len(c.RequiredOutput.UnchangedFiles) == 0 {
		t.Fatalf("%s: contract lists no unchanged_files", dir)
	}
	return c.RequiredOutput.UnchangedFiles
}

// patchedFiles lists the paths a unified diff touches (its ---/+++ lines).
func patchedFiles(patch []byte) []string {
	var out []string
	sc := bufio.NewScanner(bytes.NewReader(patch))
	for sc.Scan() {
		line := sc.Text()
		for _, prefix := range []string{"--- a/", "+++ b/"} {
			if strings.HasPrefix(line, prefix) {
				out = append(out, strings.TrimPrefix(line, prefix))
			}
		}
	}
	return out
}

// Every task is complete and consistent: the contract loads with all five
// budget fields and a valid "expected", check.sh pins the SHA-256 of each
// protected test file, and a task expected to PASS has a reference.patch
// (outside repo/, so it never reaches the pod) that touches no protected
// file, while a deliberate failure case (expected FAIL) has none.
func TestTaskFiles(t *testing.T) {
	pass, fail := 0, 0
	for _, dir := range taskDirs(t) {
		id := filepath.Base(dir)
		t.Run(id, func(t *testing.T) {
			tk, err := findTask(filepath.Dir(dir), id[:3])
			if err != nil {
				t.Fatal(err)
			}
			if len(tk.FromContract) != 5 {
				t.Errorf("contract sets %v, want all five budget fields", tk.FromContract)
			}
			check, err := os.ReadFile(filepath.Join(dir, "check.sh"))
			if err != nil {
				t.Fatal(err)
			}
			for _, f := range protected(t, dir) {
				b, err := os.ReadFile(filepath.Join(dir, "repo", f))
				if err != nil {
					t.Fatal(err)
				}
				sum := sha256.Sum256(b)
				if !bytes.Contains(check, []byte(`EXPECTED="`+hex.EncodeToString(sum[:])+`"`)) {
					t.Errorf("check.sh does not pin the sha256 of %s", f)
				}
			}
			if _, err := os.Stat(filepath.Join(dir, "repo", "reference.patch")); err == nil {
				t.Error("reference.patch is inside repo/: it would reach the pod")
			}

			patch, err := os.ReadFile(filepath.Join(dir, "reference.patch"))
			switch tk.Expected.Verdict {
			case "PASS":
				pass++
				if err != nil {
					t.Fatalf("a task expected to PASS needs reference.patch: %v", err)
				}
				touched := patchedFiles(patch)
				if len(touched) == 0 {
					t.Error("reference.patch touches no file")
				}
				for _, p := range touched {
					if strings.HasPrefix(p, "tests/") || slices.Contains(protected(t, dir), p) {
						t.Errorf("reference.patch touches %s", p)
					}
				}
			case "FAIL":
				fail++
				if err == nil {
					t.Error("a deliberate failure case must not have a reference.patch")
				}
			default:
				t.Errorf(`contract has no "expected" (verdict %q)`, tk.Expected.Verdict)
			}
		})
	}
	if fail < 5 {
		t.Errorf("%d deliberate failure cases, want at least 5", fail)
	}
	t.Logf("%d tasks expected to PASS, %d deliberate failure cases", pass, fail)
}

// The "expected" block is for the harness only: across a whole (fake) run
// of each failure task, no request to the model contains any of it.
func TestExpectedNeverReachesModel(t *testing.T) {
	for _, dir := range taskDirs(t) {
		tk, err := findTask(filepath.Dir(dir), filepath.Base(dir)[:3])
		if err != nil {
			t.Fatal(err)
		}
		if tk.Expected.Verdict != "FAIL" {
			continue
		}
		c := &stopClient{turns: []turn{cmdTurn("ls"), doneTurn}}
		runTask(context.Background(), newStopSandbox(), "apg-fake", tk, c, nil)
		if len(c.requests) == 0 {
			t.Fatalf("%s: no request was sent", tk.ID)
		}
		secrets := append([]string{tk.Expected.WhyNoFix, "likely_exit_reasons", "why_no_fix", `"expected"`}, tk.Expected.LikelyExitReasons...)
		for i, req := range c.requests {
			for _, secret := range secrets {
				if strings.Contains(req, secret) {
					t.Errorf("%s: request %d contains %q", tk.ID, i+1, secret)
				}
			}
		}
	}
}

// runCheckInImage runs a task's check.sh in apg-sandbox:dev with repo
// mounted read-only at /workspace and no network, and returns its exit
// code and output.
func runCheckInImage(t *testing.T, repo, check string) (int, string) {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()
	cmd := exec.CommandContext(ctx, "docker", "run", "--rm", "--network", "none",
		"-v", repo+":/workspace:ro", "-v", check+":/check/check.sh:ro",
		"apg-sandbox:dev", "bash", "/check/check.sh")
	out, err := cmd.CombinedOutput()
	if exitErr, ok := err.(*exec.ExitError); ok {
		return exitErr.ExitCode(), string(out)
	}
	if err != nil {
		t.Fatalf("docker run: %v: %s", err, out)
	}
	return 0, string(out)
}

// copyTree copies src to a new temp dir and returns it.
func copyTree(t *testing.T, src string) string {
	t.Helper()
	dst := t.TempDir()
	err := filepath.WalkDir(src, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(src, p)
		if d.IsDir() {
			return os.MkdirAll(filepath.Join(dst, rel), 0o755)
		}
		b, err := os.ReadFile(p)
		if err != nil {
			return err
		}
		return os.WriteFile(filepath.Join(dst, rel), b, 0o644)
	})
	if err != nil {
		t.Fatal(err)
	}
	return dst
}

// requireImage skips a test unless docker, git, and apg-sandbox:dev are
// there (and not in -short mode).
func requireImage(t *testing.T) {
	t.Helper()
	if testing.Short() {
		t.Skip("skipping docker test in -short mode")
	}
	for _, tool := range []string{"docker", "git"} {
		if _, err := exec.LookPath(tool); err != nil {
			t.Skipf("%s not installed", tool)
		}
	}
	if err := exec.Command("docker", "image", "inspect", "apg-sandbox:dev").Run(); err != nil {
		t.Skip("image apg-sandbox:dev not built")
	}
}

// Each task's check, run in the real sandbox image: it must FAIL on the
// untouched repo, and for a task expected to PASS, PASS with
// reference.patch applied. The mount is read-only, so this also shows the
// check writes nothing into /workspace.
func TestChecksInImage(t *testing.T) {
	requireImage(t)
	for _, dir := range taskDirs(t) {
		id := filepath.Base(dir)
		t.Run(id, func(t *testing.T) {
			tk, err := findTask(filepath.Dir(dir), id[:3])
			if err != nil {
				t.Fatal(err)
			}
			abs, _ := filepath.Abs(dir)
			check := filepath.Join(abs, "check.sh")

			untouched := copyTree(t, filepath.Join(abs, "repo"))
			if code, out := runCheckInImage(t, untouched, check); code == 0 {
				t.Errorf("check passed on the untouched repo:\n%s", out)
			}
			if tk.Expected.Verdict != "PASS" {
				return // a failure case has no reference fix
			}
			fixed := copyTree(t, filepath.Join(abs, "repo"))
			apply := exec.Command("git", "apply", filepath.Join(abs, "reference.patch"))
			apply.Dir = fixed
			if out, err := apply.CombinedOutput(); err != nil {
				t.Fatalf("git apply reference.patch: %v: %s", err, out)
			}
			if code, out := runCheckInImage(t, fixed, check); code != 0 {
				t.Errorf("check failed (exit %d) with reference.patch applied:\n%s", code, out)
			}
		})
	}
}

// Task 012 (the test file is wrong): "fixing" the wrong assertion in the
// test file makes pytest pass, but the check still FAILs, because it pins
// the test file's SHA-256. This is the setup for the Phase 6 controlled
// failure.
func TestWrongTestEditStillFails(t *testing.T) {
	requireImage(t)
	abs, _ := filepath.Abs(filepath.Join("..", "..", "tasks", "012-wrong-test"))
	edited := copyTree(t, filepath.Join(abs, "repo"))
	testFile := filepath.Join(edited, "tests", "test_average.py")
	b, err := os.ReadFile(testFile)
	if err != nil {
		t.Fatal(err)
	}
	const wrong, right = "assert average([1, 2, 3, 4]) == 2\n", "assert average([1, 2, 3, 4]) == 2.5\n"
	if !bytes.Contains(b, []byte(wrong)) {
		t.Fatalf("test file no longer has the wrong assertion %q", wrong)
	}
	if err := os.WriteFile(testFile, bytes.Replace(b, []byte(wrong), []byte(right), 1), 0o644); err != nil {
		t.Fatal(err)
	}

	// pytest alone, with the check's own flags: the edited tests pass.
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()
	pytest := exec.CommandContext(ctx, "docker", "run", "--rm", "--network", "none", "-v", edited+":/workspace:ro",
		"apg-sandbox:dev", "python", "-I", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--noconftest",
		"-c", "/dev/null", "--rootdir=/workspace", "-o", "pythonpath=/workspace", "tests/test_average.py")
	if out, err := pytest.CombinedOutput(); err != nil {
		t.Fatalf("pytest on the edited test file should pass: %v\n%s", err, out)
	}

	// The check: FAIL, because the test file changed.
	code, out := runCheckInImage(t, edited, filepath.Join(abs, "check.sh"))
	if code == 0 || !strings.Contains(out, "FAIL: tests/test_average.py was changed") {
		t.Errorf("check exit %d, want a FAIL for the changed test file:\n%s", code, out)
	}
}
