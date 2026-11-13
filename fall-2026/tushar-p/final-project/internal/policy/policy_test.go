package policy

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"
)

// fakeResolver stands in for running realpath in the pod. links maps a
// sandbox path to where it points: a path equal to a key, or under it, has
// that prefix replaced (like a symlinked directory). calls counts how often
// it ran, and got keeps the last paths it was asked about.
type fakeResolver struct {
	links map[string]string
	calls int
	got   []string
}

func (f *fakeResolver) resolve(_ context.Context, paths []string) ([]string, error) {
	f.calls++
	f.got = append([]string(nil), paths...)
	out := make([]string, len(paths))
	for i, p := range paths {
		out[i] = p
		for from, to := range f.links {
			if p == from {
				out[i] = to
			} else if strings.HasPrefix(p, from+"/") {
				out[i] = to + strings.TrimPrefix(p, from)
			}
		}
	}
	return out, nil
}

// argv builds a run_command input from its arguments.
func argv(args ...string) string {
	b, _ := json.Marshal(map[string]any{"argv": args})
	return string(b)
}

// path builds a read_file input.
func path(p string) string {
	b, _ := json.Marshal(map[string]string{"path": p})
	return string(b)
}

// write builds a write_file input.
func write(p string) string {
	b, _ := json.Marshal(map[string]string{"path": p, "content": "x\n"})
	return string(b)
}

// t14Pipeline is the shell command the agent ran in T1.4
// (evidence/traces/20261112T053055Z-92239eb0.json, step 2).
const t14Pipeline = `cd /workspace && sed -i 's|    return a // b|    return a / b|' calc/ops.py && grep -n "return a" calc/ops.py && python -m pytest -q tests/test_ops.py 2>&1 | tail -5`

// t14Sed is the sed script from that pipeline, as one argv argument.
const t14Sed = `s|    return a // b|    return a / b|`

var allTools = []string{"read_file", "write_file", "run_command"}

type tc struct {
	name   string
	tools  []string          // contract tools; nil means allTools
	tool   string            // tool name the model called
	input  string            // raw JSON input
	links  map[string]string // symlinks for the fake resolver
	allow  bool
	rule   string // wanted Rule when denied
	reason string // substring wanted in Reason when denied
}

func run(t *testing.T, cases []tc) {
	t.Helper()
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			tools := c.tools
			if tools == nil {
				tools = allTools
			}
			r := &fakeResolver{links: c.links}
			d, err := New(tools).Check(context.Background(), c.tool, json.RawMessage(c.input), r.resolve)
			if err != nil {
				t.Fatalf("Check error: %v", err)
			}
			if d.Allowed != c.allow {
				t.Fatalf("Allowed = %v, want %v (rule %q, reason %q)", d.Allowed, c.allow, d.Rule, d.Reason)
			}
			if c.allow {
				if d.Rule != "" || d.Reason != "" {
					t.Errorf("allowed call has rule %q reason %q", d.Rule, d.Reason)
				}
				return
			}
			if d.Rule != c.rule {
				t.Errorf("Rule = %q, want %q (reason %q)", d.Rule, c.rule, d.Reason)
			}
			if !strings.Contains(d.Reason, c.reason) {
				t.Errorf("Reason = %q, want it to contain %q", d.Reason, c.reason)
			}
			if d.Path != "" || d.Argv != nil {
				t.Errorf("denied call still carries something to run: path %q argv %q", d.Path, d.Argv)
			}
		})
	}
}

// Rule 1: only tools listed in the task's contract.
func TestRuleToolInContract(t *testing.T) {
	run(t, []tc{
		{name: "listed tool", tools: []string{"read_file"}, tool: "read_file", input: path("calc/ops.py"), allow: true},
		{name: "real tool not in contract", tools: []string{"read_file"}, tool: "write_file", input: write("a.py"), rule: RuleTool, reason: "not allowed for this task"},
		{name: "run_command not in contract", tools: []string{"read_file"}, tool: "run_command", input: argv("ls"), rule: RuleTool, reason: "not allowed for this task"},
		{name: "unknown tool", tool: "delete_file", input: path("a"), rule: RuleTool, reason: "not allowed for this task"},
		{name: "empty tool name", tool: "", input: path("a"), rule: RuleTool, reason: "not allowed for this task"},
	})
}

// Bad input is denied before any rule looks at it.
func TestInputMustParse(t *testing.T) {
	run(t, []tc{
		{name: "path not a string", tool: "read_file", input: `{"path": 1}`, rule: RuleInput},
		{name: "not JSON", tool: "read_file", input: `{`, rule: RuleInput},
		{name: "empty path", tool: "read_file", input: path(""), rule: RuleInput, reason: "empty path"},
		{name: "old run_command shape", tool: "run_command", input: `{"command": "ls"}`, rule: RuleInput},
		{name: "empty argv", tool: "run_command", input: argv(), rule: RuleInput, reason: "empty"},
		{name: "NUL in argument", tool: "run_command", input: argv("cat", "a\x00b"), rule: RuleInput},
	})
}

// Rule 2 for the file tools: paths must resolve inside /workspace.
func TestRulePathFileTools(t *testing.T) {
	run(t, []tc{
		{name: "relative", tool: "read_file", input: path("calc/ops.py"), allow: true},
		{name: "absolute inside", tool: "read_file", input: path("/workspace/calc/ops.py"), allow: true},
		{name: "dot dot that stays inside", tool: "read_file", input: path("calc/../tests/test_ops.py"), allow: true},
		{name: "write inside", tool: "write_file", input: write("calc/ops.py"), allow: true},
		{name: "symlink to inside", tool: "read_file", input: path("alias.py"),
			links: map[string]string{"/workspace/alias.py": "/workspace/calc/ops.py"}, allow: true},

		{name: "parent escape", tool: "read_file", input: path("../etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "dot dot in absolute", tool: "read_file", input: path("/workspace/../etc/shadow"), rule: RulePath, reason: "outside /workspace"},
		{name: "absolute elsewhere", tool: "read_file", input: path("/etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "prefix trick", tool: "read_file", input: path("/workspacex/a"), rule: RulePath, reason: "outside /workspace"},
		{name: "write outside", tool: "write_file", input: write("/tmp/x"), rule: RulePath, reason: "outside /workspace"},
		{name: "write the workspace dir", tool: "write_file", input: write("/workspace"), rule: RulePath, reason: "workspace directory itself"},
		{name: "newline in path", tool: "read_file", input: path("calc/ops.py\n/etc/passwd"), rule: RulePath, reason: "control character"},

		// Symlink tricks: lexically fine, but the real path is elsewhere.
		{name: "symlinked dir read", tool: "read_file", input: path("etc-link/passwd"),
			links: map[string]string{"/workspace/etc-link": "/etc"}, rule: RulePath, reason: "resolves to /etc/passwd"},
		{name: "symlinked file read", tool: "read_file", input: path("notes.txt"),
			links: map[string]string{"/workspace/notes.txt": "/etc/shadow"}, rule: RulePath, reason: "resolves to /etc/shadow"},
		{name: "symlinked parent write", tool: "write_file", input: write("calc/ops.py"),
			links: map[string]string{"/workspace/calc": "/tmp/evil"}, rule: RulePath, reason: "resolves to /tmp/evil/ops.py"},
	})
}

// Rule 3: check files are never readable or writable by the agent.
func TestRuleCheckFiles(t *testing.T) {
	run(t, []tc{
		{name: "read check", tool: "read_file", input: path("/tmp/apg-check-0123abcd/check.sh"), rule: RuleCheckFile, reason: "check"},
		{name: "write check", tool: "write_file", input: write("/tmp/apg-check-0123abcd/check.sh"), rule: RuleCheckFile, reason: "check"},
		{name: "escape to check", tool: "read_file", input: path("../tmp/apg-check-0123abcd/check.sh"), rule: RuleCheckFile, reason: "check"},
		{name: "symlink to check", tool: "read_file", input: path("c.sh"),
			links: map[string]string{"/workspace/c.sh": "/tmp/apg-check-0123abcd/check.sh"}, rule: RuleCheckFile, reason: "check"},
		{name: "cat check", tool: "run_command", input: argv("cat", "/tmp/apg-check-0123abcd/check.sh"), rule: RuleCheckFile, reason: "check"},
		{name: "symlinked cat", tool: "run_command", input: argv("cat", "c.sh"),
			links: map[string]string{"/workspace/c.sh": "/tmp/apg-check-0123abcd/check.sh"}, rule: RuleCheckFile, reason: "check"},
		// Named in a slot that is not path-checked: still denied.
		{name: "grep pattern names check dir", tool: "run_command", input: argv("grep", "-r", "apg-check-", "."), rule: RuleCheckFile, reason: "check"},
		{name: "python code names check dir", tool: "run_command", input: argv("python", "-c", "print(open('/tmp/apg-check-0123abcd/check.sh').read())"), rule: RuleCheckFile, reason: "check"},
	})
}

// Rule 4: argv only, program on the allowlist, every path argument passes rule 2.
func TestRuleProgramAllowlist(t *testing.T) {
	cases := []tc{
		// The T1.4 call as it was sent (a shell pipeline) is denied ...
		{name: "T1.4 pipeline via sh -c", tool: "run_command", input: argv("sh", "-c", t14Pipeline), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "T1.4 pipeline as one argv[0]", tool: "run_command", input: argv(t14Pipeline), rule: RuleProgram, reason: "not on the allowlist"},
		// ... and each of its parts is allowed as its own argv call.
		{name: "T1.4 sed", tool: "run_command", input: argv("sed", "-i", t14Sed, "calc/ops.py"), allow: true},
		{name: "T1.4 grep", tool: "run_command", input: argv("grep", "-n", "return a", "calc/ops.py"), allow: true},
		{name: "T1.4 pytest", tool: "run_command", input: argv("python", "-m", "pytest", "-q", "tests/test_ops.py"), allow: true},
		{name: "T1.4 cat", tool: "run_command", input: argv("cat", "tests/test_ops.py"), allow: true},
		{name: "T1.4 find", tool: "run_command", input: argv("find", ".", "-type", "f", "-not", "-path", "./.git/*"), allow: true},
		{name: "T1.4 head", tool: "run_command", input: argv("head", "-100", "calc/ops.py"), allow: true},

		{name: "bash", tool: "run_command", input: argv("bash", "-c", "ls"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "cd", tool: "run_command", input: argv("cd", "/workspace"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "full path to allowed program", tool: "run_command", input: argv("/bin/ls"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "env runs another program", tool: "run_command", input: argv("env", "ls"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "xargs", tool: "run_command", input: argv("xargs", "rm"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "timeout", tool: "run_command", input: argv("timeout", "1", "ls"), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "rm", tool: "run_command", input: argv("rm", "-rf", "."), rule: RuleProgram, reason: "not on the allowlist"},
		{name: "python3 is not python", tool: "run_command", input: argv("python3", "-V"), rule: RuleProgram, reason: "not on the allowlist"},

		// Allowed programs with ordinary arguments.
		{name: "ls", tool: "run_command", input: argv("ls", "-la"), allow: true},
		{name: "ls workspace", tool: "run_command", input: argv("ls", "/workspace"), allow: true},
		{name: "pytest", tool: "run_command", input: argv("pytest", "-q", "-k", "add or divide"), allow: true},
		{name: "pytest node id", tool: "run_command", input: argv("pytest", "tests/test_ops.py::test_divide"), allow: true},
		{name: "wc", tool: "run_command", input: argv("wc", "-l", "calc/ops.py"), allow: true},
		{name: "diff", tool: "run_command", input: argv("diff", "-u", "calc/ops.py", "calc/__init__.py"), allow: true},
		{name: "tail", tool: "run_command", input: argv("tail", "-n", "5", "calc/ops.py"), allow: true},
		{name: "grep pattern that looks like a path", tool: "run_command", input: argv("grep", "-rn", "/usr/bin", "."), allow: true},
		{name: "grep -e pattern with dot dot", tool: "run_command", input: argv("grep", "-e", "../x", "calc"), allow: true},
		{name: "grep attached -e", tool: "run_command", input: argv("grep", "-e/^x/", "calc/ops.py"), allow: true},
		{name: "sed regex address", tool: "run_command", input: argv("sed", "-n", "/^def/p", "calc/ops.py"), allow: true},
		{name: "find -path value", tool: "run_command", input: argv("find", ".", "-path", "/workspace/calc/*"), allow: true},
		// python code is not path-checked: it can do anything anyway (see policy.go).
		{name: "python -c reads outside (known limit)", tool: "run_command", input: argv("python", "-c", "print(open('/etc/hostname').read())"), allow: true},

		// Path arguments must pass rule 2.
		{name: "cat absolute elsewhere", tool: "run_command", input: argv("cat", "/etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "cat dot dot", tool: "run_command", input: argv("cat", "../../etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "ls root", tool: "run_command", input: argv("ls", "/"), rule: RulePath, reason: "outside /workspace"},
		{name: "head option then path", tool: "run_command", input: argv("head", "-n", "5", "/etc/hosts"), rule: RulePath, reason: "outside /workspace"},
		{name: "diff second file", tool: "run_command", input: argv("diff", "calc/ops.py", "/etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "find start point", tool: "run_command", input: argv("find", "/", "-name", "x"), rule: RulePath, reason: "outside /workspace"},
		{name: "find -newer file", tool: "run_command", input: argv("find", ".", "-newer", "/etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "grep -f file", tool: "run_command", input: argv("grep", "-f", "/etc/shadow", "calc/ops.py"), rule: RulePath, reason: "outside /workspace"},
		{name: "grep --file=", tool: "run_command", input: argv("grep", "--file=/etc/shadow", "calc/ops.py"), rule: RulePath, reason: "outside /workspace"},
		{name: "grep attached -f", tool: "run_command", input: argv("grep", "-f/etc/shadow", "calc/ops.py"), rule: RulePath, reason: "outside /workspace"},
		// GNU grep permutes arguments: with -e later, the first operand is a file.
		{name: "grep file before -e", tool: "run_command", input: argv("grep", "/etc/passwd", "-e", "root"), rule: RulePath, reason: "outside /workspace"},
		{name: "wc --files0-from=", tool: "run_command", input: argv("wc", "--files0-from=/etc/x"), rule: RulePath, reason: "outside /workspace"},
		{name: "pytest --basetemp=", tool: "run_command", input: argv("pytest", "--basetemp=/tmp/x"), rule: RulePath, reason: "outside /workspace"},
		{name: "pytest -o key=value", tool: "run_command", input: argv("pytest", "-o", "cache_dir=/tmp/c"), rule: RulePath, reason: "outside /workspace"},
		{name: "python script elsewhere", tool: "run_command", input: argv("python", "/etc/x.py"), rule: RulePath, reason: "outside /workspace"},
		{name: "sed -i backup suffix elsewhere", tool: "run_command", input: argv("sed", "-i/tmp/*", "s/a/b/", "calc/ops.py"), rule: RulePath, reason: "outside /workspace"},
		{name: "tail attached value dot dot", tool: "run_command", input: argv("tail", "-n5", "../x"), rule: RulePath, reason: "outside /workspace"},
		{name: "unknown option with attached path", tool: "run_command", input: argv("cat", "-A../../etc/passwd"), rule: RulePath, reason: "outside /workspace"},
		{name: "newline in path argument", tool: "run_command", input: argv("cat", "a\nb"), rule: RulePath, reason: "control character"},
		{name: "symlinked operand", tool: "run_command", input: argv("cat", "etc-link/passwd"),
			links: map[string]string{"/workspace/etc-link": "/etc"}, rule: RulePath, reason: "resolves to /etc/passwd"},
		{name: "symlinked ls", tool: "run_command", input: argv("ls", "up"),
			links: map[string]string{"/workspace/up": "/"}, rule: RulePath, reason: "resolves to /"},
	}
	for _, prog := range Programs {
		cases = append(cases, tc{name: "bare " + prog, tool: "run_command", input: argv(prog), allow: true})
	}
	run(t, cases)
}

// Rule 5: flags that run another program, delete files, write or read
// files the policy cannot see, or follow symlinks.
func TestRuleDeniedFlags(t *testing.T) {
	cases := []tc{}
	for _, f := range []string{"-exec", "-execdir", "-ok", "-okdir"} {
		cases = append(cases, tc{name: "find " + f, tool: "run_command", input: argv("find", ".", "-name", "*.py", f, "rm", "{}", ";"), rule: RuleFlag, reason: f})
	}
	for _, f := range []string{"-delete", "-follow"} {
		cases = append(cases, tc{name: "find " + f, tool: "run_command", input: argv("find", ".", f), rule: RuleFlag, reason: f})
	}
	for _, f := range []string{"-fprint", "-fprint0", "-fls"} {
		cases = append(cases, tc{name: "find " + f, tool: "run_command", input: argv("find", ".", f, "out.txt"), rule: RuleFlag, reason: f})
	}
	cases = append(cases,
		tc{name: "find -fprintf", tool: "run_command", input: argv("find", ".", "-fprintf", "out.txt", "%p"), rule: RuleFlag, reason: "-fprintf"},
		tc{name: "find -L", tool: "run_command", input: argv("find", "-L", "."), rule: RuleFlag, reason: "-L"},
		tc{name: "find -H", tool: "run_command", input: argv("find", "-H", "."), rule: RuleFlag, reason: "-H"},

		tc{name: "grep -R", tool: "run_command", input: argv("grep", "-R", "x", "."), rule: RuleFlag, reason: "-R"},
		tc{name: "grep -R in a cluster", tool: "run_command", input: argv("grep", "-nR", "x", "."), rule: RuleFlag, reason: "-R"},
		tc{name: "grep --dereference-recursive", tool: "run_command", input: argv("grep", "--dereference-recursive", "x", "."), rule: RuleFlag, reason: "--dereference-recursive"},

		tc{name: "sed e command", tool: "run_command", input: argv("sed", "-n", "1e id", "calc/ops.py"), rule: RuleFlag, reason: `"e"`},
		tc{name: "sed e after other command", tool: "run_command", input: argv("sed", "s/a/b/;e id", "calc/ops.py"), rule: RuleFlag, reason: `"e"`},
		tc{name: "sed e in a block", tool: "run_command", input: argv("sed", "-n", "1{p;e id\n}", "calc/ops.py"), rule: RuleFlag, reason: `"e"`},
		tc{name: "sed e in second -e", tool: "run_command", input: argv("sed", "-e", "p", "-e", "1e id", "calc/ops.py"), rule: RuleFlag, reason: `"e"`},
		tc{name: "sed s///e flag", tool: "run_command", input: argv("sed", "s/a/b/e", "calc/ops.py"), rule: RuleFlag, reason: `"e"`},
		tc{name: "sed s///w flag", tool: "run_command", input: argv("sed", "s/a/b/w /tmp/x", "calc/ops.py"), rule: RuleFlag, reason: `"w"`},
		tc{name: "sed s,,,gw other delimiter", tool: "run_command", input: argv("sed", "s,a,b,gw out", "calc/ops.py"), rule: RuleFlag, reason: `"w"`},
		tc{name: "sed w command", tool: "run_command", input: argv("sed", "w out.txt", "calc/ops.py"), rule: RuleFlag, reason: `"w"`},
		tc{name: "sed W command", tool: "run_command", input: argv("sed", "W out.txt", "calc/ops.py"), rule: RuleFlag, reason: `"W"`},
		tc{name: "sed r command", tool: "run_command", input: argv("sed", "r /etc/passwd", "calc/ops.py"), rule: RuleFlag, reason: `"r"`},
		tc{name: "sed R command", tool: "run_command", input: argv("sed", "1R notes", "calc/ops.py"), rule: RuleFlag, reason: `"R"`},
		tc{name: "sed w after y", tool: "run_command", input: argv("sed", "y/abc/xyz/;w x", "calc/ops.py"), rule: RuleFlag, reason: `"w"`},
		tc{name: "sed -f script file", tool: "run_command", input: argv("sed", "-f", "script.sed", "calc/ops.py"), rule: RuleFlag, reason: "-f"},
		tc{name: "sed --file=", tool: "run_command", input: argv("sed", "--file=script.sed", "calc/ops.py"), rule: RuleFlag, reason: "--file"},
		tc{name: "sed unknown command", tool: "run_command", input: argv("sed", "v", "calc/ops.py"), rule: RuleFlag, reason: `"v"`},
		tc{name: "sed unterminated s", tool: "run_command", input: argv("sed", "s/a/b", "calc/ops.py"), rule: RuleFlag, reason: "unterminated"},

		// sed scripts that only look dangerous.
		tc{name: "sed w and e inside s", tool: "run_command", input: argv("sed", "s/w/e/g", "calc/ops.py"), allow: true},
		tc{name: "sed escaped delimiter", tool: "run_command", input: argv("sed", `s/a\/w/b/`, "calc/ops.py"), allow: true},
		tc{name: "sed append text with w", tool: "run_command", input: argv("sed", "3a we write here", "calc/ops.py"), allow: true},
		tc{name: "sed ranges and delete", tool: "run_command", input: argv("sed", "/^def/,/^$/d;$d", "calc/ops.py"), allow: true},
		tc{name: "sed numbered s and flags", tool: "run_command", input: argv("sed", "-E", "s/(a)/\\1/2;s/x/y/gI", "calc/ops.py"), allow: true},
		tc{name: "sed print range", tool: "run_command", input: argv("sed", "-n", "1,20p", "calc/ops.py"), allow: true},
		tc{name: "find -name value that looks like -exec", tool: "run_command", input: argv("find", ".", "-name", "-exec"), allow: true},
	)
	run(t, cases)
}

// sed always runs with --sandbox, so GNU sed itself also refuses e/r/w.
func TestSedRunsInSandboxMode(t *testing.T) {
	r := &fakeResolver{}
	d, err := New(allTools).Check(context.Background(), "run_command", json.RawMessage(argv("sed", "-i", t14Sed, "calc/ops.py")), r.resolve)
	if err != nil || !d.Allowed {
		t.Fatalf("allowed=%v err=%v reason=%q", d.Allowed, err, d.Reason)
	}
	want := []string{"sed", "--sandbox", "-i", t14Sed, "calc/ops.py"}
	if strings.Join(d.Argv, "\x00") != strings.Join(want, "\x00") {
		t.Errorf("Argv = %q, want %q", d.Argv, want)
	}
}

// Other programs run exactly as sent.
func TestArgvUnchanged(t *testing.T) {
	r := &fakeResolver{}
	in := []string{"grep", "-n", "return a", "calc/ops.py"}
	d, err := New(allTools).Check(context.Background(), "run_command", json.RawMessage(argv(in...)), r.resolve)
	if err != nil || !d.Allowed {
		t.Fatalf("allowed=%v err=%v reason=%q", d.Allowed, err, d.Reason)
	}
	if strings.Join(d.Argv, "\x00") != strings.Join(in, "\x00") {
		t.Errorf("Argv = %q, want %q", d.Argv, in)
	}
}

// Relative paths are resolved against /workspace: the resolver (realpath in
// the pod) is asked about /workspace/calc/ops.py, and the file tools get
// that absolute path.
func TestRelativePathsResolveUnderWorkspace(t *testing.T) {
	r := &fakeResolver{}
	p := New(allTools)
	d, err := p.Check(context.Background(), "read_file", json.RawMessage(path("calc/ops.py")), r.resolve)
	if err != nil || !d.Allowed || d.Path != "/workspace/calc/ops.py" {
		t.Fatalf("read_file: allowed=%v path=%q err=%v", d.Allowed, d.Path, err)
	}
	if strings.Join(r.got, " ") != "/workspace/calc/ops.py" {
		t.Errorf("read_file resolved %q", r.got)
	}

	d, err = p.Check(context.Background(), "run_command", json.RawMessage(argv("cat", "calc/ops.py")), r.resolve)
	if err != nil || !d.Allowed {
		t.Fatalf("run_command: allowed=%v err=%v", d.Allowed, err)
	}
	found := false
	for _, g := range r.got {
		found = found || g == "/workspace/calc/ops.py"
	}
	if !found {
		t.Errorf("run_command resolved %q, want /workspace/calc/ops.py among them", r.got)
	}
}

// A call denied by a lexical rule never reaches the sandbox, not even for
// realpath.
func TestLexicalDenialsDoNotResolve(t *testing.T) {
	inputs := []struct{ tool, input string }{
		{"delete_file", path("a")},
		{"read_file", path("../etc/passwd")},
		{"read_file", path("/tmp/apg-check-1/check.sh")},
		{"run_command", argv("sh", "-c", t14Pipeline)},
		{"run_command", argv("cat", "/etc/passwd")},
		{"run_command", argv("find", ".", "-delete")},
		{"run_command", argv("sed", "1e id", "calc/ops.py")},
	}
	for _, in := range inputs {
		r := &fakeResolver{}
		d, err := New(allTools).Check(context.Background(), in.tool, json.RawMessage(in.input), r.resolve)
		if err != nil || d.Allowed {
			t.Errorf("%s %s: allowed=%v err=%v", in.tool, in.input, d.Allowed, err)
		}
		if r.calls != 0 {
			t.Errorf("%s %s: resolver ran %d times for a lexical denial", in.tool, in.input, r.calls)
		}
	}
}

// A resolver failure is a harness error, not a decision.
func TestResolverErrorIsReturned(t *testing.T) {
	fail := func(context.Context, []string) ([]string, error) { return nil, errors.New("kubectl gone") }
	_, err := New(allTools).Check(context.Background(), "read_file", json.RawMessage(path("calc/ops.py")), fail)
	if err == nil || !strings.Contains(err.Error(), "kubectl gone") {
		t.Errorf("err = %v", err)
	}
}

// If the resolver cannot answer for every path (realpath failed in the
// pod), the call is denied rather than run unchecked.
func TestUnresolvedPathsAreDenied(t *testing.T) {
	short := func(context.Context, []string) ([]string, error) { return nil, nil }
	d, err := New(allTools).Check(context.Background(), "read_file", json.RawMessage(path("calc/ops.py")), short)
	if err != nil || d.Allowed || d.Rule != RulePath || !strings.Contains(d.Reason, "could not resolve") {
		t.Errorf("allowed=%v rule=%q reason=%q err=%v", d.Allowed, d.Rule, d.Reason, err)
	}
}

// The allowlist is exactly the one in PLAN/T2.1.
func TestProgramsList(t *testing.T) {
	want := "cat diff find grep head ls pytest python sed tail wc"
	if got := strings.Join(Programs, " "); got != want {
		t.Errorf("Programs = %q, want %q", got, want)
	}
}
