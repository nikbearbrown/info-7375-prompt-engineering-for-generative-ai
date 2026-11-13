// Package policy decides, before anything runs, whether one tool call from
// the agent is allowed. Every tool call goes through Check. A denied call is
// never executed: the loop records it in the trace with the rule and reason
// and tells the model why.
//
// The rules (PLAN.md T2.1):
//
//  1. tool:       only tools listed in the task's contract.
//  2. path:       file paths must resolve inside /workspace. ".." and
//     absolute paths elsewhere are denied by looking at the text; symlinks
//     are caught by asking the sandbox for the real path (Resolver).
//  3. check_file: check files are never readable or writable by the agent.
//  4. program:    run_command runs an argv list with no shell, and argv[0]
//     must be on the allowlist (Programs). Every path argument must pass
//     rule 2.
//  5. flag:       options that let an allowed program run another program,
//     delete files, write or read files outside what the policy can check,
//     or follow symlinks are denied.
//
// What this policy cannot do: python and pytest are on the allowlist, and
// both run arbitrary code (python -c, a test file, a conftest.py, an
// imported module). That code runs as the pod's user and can read outside
// /workspace, create symlinks, delete files, or start other programs; the
// policy only sees the command line, not what the code does. So the policy
// makes the allowlist meaningful for the other nine programs and for the
// file tools, and it records every decision, but it is not the security
// boundary. The pod is: non-root, no capabilities, no service-account
// token, CPU and memory limits, and no network (internal/sandbox). Rule 3
// holds today mainly because the hidden check is copied into the pod only
// after the agent's last step, so there is nothing to read during the run.
package policy

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	// Imported under another name: the tests in this package have a
	// helper called path, and a package-level name may not equal an import.
	posixpath "path"
	"strings"
)

// Workspace is the only directory the agent's tools may touch.
const Workspace = "/workspace"

// CheckDirPrefix starts the name of the directory the harness copies the
// hidden check into (a random suffix follows). The harness builds the
// directory name from this constant, so rule 3 and the harness agree.
const CheckDirPrefix = "/tmp/apg-check-"

// checkMarker is the part of CheckDirPrefix that rule 3 looks for in any
// path or argument.
const checkMarker = "apg-check-"

// Programs is the run_command allowlist (sorted). argv[0] must be exactly
// one of these: no paths like /bin/ls, no python3.
var Programs = []string{"cat", "diff", "find", "grep", "head", "ls", "pytest", "python", "sed", "tail", "wc"}

// Rules, used in Decision.Rule and written into the trace.
const (
	RuleTool      = "tool"
	RuleInput     = "input" // the tool input did not parse
	RulePath      = "path"
	RuleCheckFile = "check_file"
	RuleProgram   = "program"
	RuleFlag      = "flag"
)

// Policy holds the rules for one task.
type Policy struct {
	tools map[string]bool // the contract's allowed_tools, as a set
}

// New returns the policy for a task whose contract allows these tools.
func New(allowedTools []string) *Policy {
	p := &Policy{tools: map[string]bool{}}
	for _, t := range allowedTools {
		p.tools[t] = true
	}
	return p
}

// Decision is the policy's answer for one tool call.
type Decision struct {
	Allowed bool
	Rule    string // which rule denied the call; empty when allowed
	Reason  string // why, in words the model can act on; empty when allowed

	// Only set when Allowed: what the loop should run.
	Path string   // read_file / write_file: clean absolute path
	Argv []string // run_command: the argv to run
}

// Resolver returns the real path of each path inside the sandbox, with
// symlinks followed (the loop runs "realpath -m" in the pod). It returns an
// error only when the harness failed; if the sandbox cannot answer, it
// returns fewer paths and the call is denied.
type Resolver func(ctx context.Context, paths []string) ([]string, error)

// deny builds a denied Decision. "args ...any" collects the remaining
// arguments, as fmt.Sprintf takes them.
func deny(rule, format string, args ...any) Decision {
	return Decision{Rule: rule, Reason: fmt.Sprintf(format, args...)}
}

// Check decides one tool call. It applies every rule it can by looking at
// the input first; only if all of those pass does it call resolve, then it
// applies rules 2 and 3 again to the real paths. So a call denied by its
// text never runs anything in the sandbox, not even realpath.
//
// The error is only for harness failures from resolve; a denial is a
// Decision, not an error.
func (p *Policy) Check(ctx context.Context, tool string, input json.RawMessage, resolve Resolver) (Decision, error) {
	if !p.tools[tool] {
		return deny(RuleTool, "tool %q is not allowed for this task", tool), nil
	}

	var d Decision
	var paths []string // clean absolute paths to resolve in the sandbox
	switch tool {
	case "read_file", "write_file":
		d, paths = checkFileTool(tool, input)
	case "run_command":
		d, paths = checkCommand(input)
	default:
		// A tool in the contract that this policy does not know is denied,
		// so a new tool cannot skip the policy by accident.
		return deny(RuleTool, "tool %q has no policy rules", tool), nil
	}
	if !d.Allowed || len(paths) == 0 {
		return d, nil
	}

	real, err := resolve(ctx, paths)
	if err != nil {
		return Decision{}, fmt.Errorf("resolve paths: %w", err)
	}
	if len(real) != len(paths) {
		return deny(RulePath, "could not resolve paths %q in the sandbox", paths), nil
	}
	for i, r := range real {
		switch {
		case strings.Contains(r, checkMarker):
			return deny(RuleCheckFile, "path %s resolves to %s, which is a check file; check files are never readable or writable", paths[i], r), nil
		case !insideWorkspace(r):
			return deny(RulePath, "path %s resolves to %s, which is outside %s", paths[i], r, Workspace), nil
		}
	}
	return d, nil
}

// decodeStrict parses JSON into v and rejects unknown fields, so an input
// in the wrong shape (for example the old {"command": "..."}) is denied
// instead of half-read.
func decodeStrict(raw json.RawMessage, v any) error {
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.DisallowUnknownFields()
	if err := dec.Decode(v); err != nil {
		return err
	}
	if dec.More() {
		return errors.New("extra data after the JSON object")
	}
	return nil
}

// checkFileTool applies rules 2 and 3 to read_file and write_file.
func checkFileTool(tool string, raw json.RawMessage) (Decision, []string) {
	var in struct {
		Path    string  `json:"path"`
		Content *string `json:"content"` // pointer: nil when absent
	}
	if err := decodeStrict(raw, &in); err != nil {
		return deny(RuleInput, "invalid input: %v", err), nil
	}
	if tool == "read_file" && in.Content != nil {
		return deny(RuleInput, "invalid input: read_file takes no content"), nil
	}
	if strings.TrimSpace(in.Path) == "" {
		return deny(RuleInput, "empty path"), nil
	}
	abs, bad := lexicalPath(in.Path)
	if bad.Rule != "" {
		return bad, nil
	}
	if tool == "write_file" && abs == Workspace {
		return deny(RulePath, "path is the workspace directory itself, not a file"), nil
	}
	return Decision{Allowed: true, Path: abs}, []string{abs}
}

// lexicalPath resolves p against /workspace by text alone and applies
// rules 3 and 2. It uses package path (as posixpath; always "/"), not path/filepath,
// because these are paths inside the Linux pod, not on the host. On a
// denial, the returned Decision has its Rule set.
func lexicalPath(p string) (string, Decision) {
	for _, r := range p {
		if r < 0x20 || r == 0x7f {
			return "", deny(RulePath, "path %q contains a control character", p)
		}
	}
	if !posixpath.IsAbs(p) {
		p = posixpath.Join(Workspace, p)
	}
	p = posixpath.Clean(p) // resolves ".." in the text: /workspace/../etc becomes /etc
	if strings.Contains(p, checkMarker) {
		return "", deny(RuleCheckFile, "path %s is a check file; check files are never readable or writable", p)
	}
	if !insideWorkspace(p) {
		return "", deny(RulePath, "path %s is outside %s", p, Workspace)
	}
	return p, Decision{}
}

// insideWorkspace reports whether a clean absolute path is /workspace or
// under it. The "/" matters: /workspacex is not inside.
func insideWorkspace(p string) bool {
	return p == Workspace || strings.HasPrefix(p, Workspace+"/")
}

// checkCommand applies rules 3, 4, 5 and 2 to run_command.
func checkCommand(raw json.RawMessage) (Decision, []string) {
	var in struct {
		Argv []string `json:"argv"`
	}
	if err := decodeStrict(raw, &in); err != nil {
		return deny(RuleInput, "invalid input: %v", err), nil
	}
	if len(in.Argv) == 0 {
		return deny(RuleInput, "argv is empty"), nil
	}
	for _, a := range in.Argv {
		if strings.ContainsRune(a, 0) {
			return deny(RuleInput, "argument %q contains a NUL byte", a), nil
		}
	}

	// Rule 4: the program. There is no shell, so this is the program that
	// actually runs (the loop adds only "timeout 60" in front).
	prog := in.Argv[0]
	if !isProgram(prog) {
		return deny(RuleProgram, "program %q is not on the allowlist (%s); run_command runs one program with no shell, so pipes, &&, cd, redirection, and globs do not work",
			prog, strings.Join(Programs, ", ")), nil
	}

	// Rule 3: no argument may name the check directory, in any position,
	// including patterns and python code (which python could still build
	// at run time; see the package comment).
	for _, a := range in.Argv[1:] {
		if strings.Contains(a, checkMarker) {
			return deny(RuleCheckFile, "argument %q names the check directory; check files are never readable or writable", a), nil
		}
	}

	// Rules 5 and 2: classify the arguments of this program.
	c := &collector{}
	switch prog {
	case "find":
		c.find(in.Argv[1:])
	case "grep":
		c.grep(in.Argv[1:])
	case "sed":
		c.sed(in.Argv[1:])
	case "python":
		c.python(in.Argv[1:])
	default: // cat diff head ls pytest tail wc: every argument may be a path
		for _, a := range in.Argv[1:] {
			c.generic(a)
		}
	}
	if c.denied.Rule != "" {
		return c.denied, nil
	}

	var abs []string
	seen := map[string]bool{}
	for _, p := range c.paths {
		a, bad := lexicalPath(p)
		if bad.Rule != "" {
			return bad, nil
		}
		if !seen[a] {
			seen[a] = true
			abs = append(abs, a)
		}
	}

	argv := append([]string(nil), in.Argv...) // a copy, so the caller's slice is not shared
	if prog == "sed" {
		// GNU sed's --sandbox makes sed itself refuse e, r, and w. The
		// script check below already denies them; this is a second layer
		// in case the check and sed ever read a script differently.
		argv = append([]string{"sed", "--sandbox"}, argv[1:]...)
	}
	return Decision{Allowed: true, Argv: argv}, abs
}

func isProgram(s string) bool {
	for _, p := range Programs {
		if s == p {
			return true
		}
	}
	return false
}

// collector gathers the strings in one argv that must pass rule 2, and the
// first rule-5 denial, if any.
//
// The idea: every argument is treated as a possible path unless the
// program's parser knows it is something else (grep's pattern, sed's
// script, python's -c code, find's -name value). Treating a non-path as a
// path is safe: a word like "5" or "add or divide" resolves inside
// /workspace and passes. So mistakes in the parsers below can only deny
// too much, except where an argument is skipped on purpose.
type collector struct {
	paths  []string
	denied Decision
}

func (c *collector) path(s string) {
	if s != "" {
		c.paths = append(c.paths, s)
	}
}

func (c *collector) deny(format string, args ...any) {
	if c.denied.Rule == "" { // keep the first denial
		c.denied = deny(RuleFlag, format, args...)
	}
}

// generic adds the possible paths inside one argument:
//   - an operand ("calc/ops.py") is a path;
//   - an option's value can be attached: "--file=/etc/x" (after "="), or
//     "-f/etc/x" (a short option cluster). For a cluster, everything from
//     the first character that is not a letter or digit is checked; that
//     covers any attached value that could leave /workspace, which needs
//     a "/" or "..";
//   - any "=" inside an argument starts a possible path, as in
//     pytest -o cache_dir=/tmp/x.
func (c *collector) generic(a string) {
	if strings.HasPrefix(a, "-") && a != "-" {
		body := strings.TrimLeft(a, "-")
		if !strings.HasPrefix(a, "--") {
			if i := strings.IndexFunc(body, func(r rune) bool { return !isAlnum(r) }); i >= 0 {
				c.path(body[i:])
			}
		}
	} else {
		c.path(a)
	}
	for i := 0; i < len(a); i++ {
		if a[i] == '=' {
			c.path(a[i+1:])
		}
	}
}

func isAlnum(r rune) bool {
	return r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r >= '0' && r <= '9'
}

// isLongPrefix reports whether the long option name given on the command
// line (without "--") could mean opt. GNU tools accept any unambiguous
// prefix ("--fi" for "--file"), so a deny list must match prefixes too.
func isLongPrefix(given, opt string) bool {
	return given != "" && strings.HasPrefix(opt, given)
}

// splitLong splits "--name=value" into name, value, and whether "=" was there.
func splitLong(a string) (name, value string, hasValue bool) {
	name = strings.TrimPrefix(a, "--")
	if i := strings.IndexByte(name, '='); i >= 0 {
		return name[:i], name[i+1:], true
	}
	return name, "", false
}

// findDenied are find's options for running programs, deleting files,
// writing files, and following symlinks.
var findDenied = map[string]string{
	"-exec":    "runs another program",
	"-execdir": "runs another program",
	"-ok":      "runs another program",
	"-okdir":   "runs another program",
	"-delete":  "deletes files",
	"-fprint":  "writes a file (use write_file)",
	"-fprint0": "writes a file (use write_file)",
	"-fprintf": "writes a file (use write_file)",
	"-fls":     "writes a file (use write_file)",
	"-L":       "follows symlinks",
	"-H":       "follows symlinks",
	"-follow":  "follows symlinks",
}

// findPatterns take a pattern or format, not a path, as the next argument.
var findPatterns = map[string]bool{
	"-name": true, "-iname": true, "-path": true, "-ipath": true,
	"-wholename": true, "-iwholename": true, "-regex": true, "-iregex": true,
	"-lname": true, "-ilname": true, "-printf": true, "-perm": true,
}

func (c *collector) find(args []string) {
	for i := 0; i < len(args); i++ {
		a := args[i]
		if why, ok := findDenied[a]; ok {
			c.deny("find %s %s", a, why)
			return
		}
		if findPatterns[a] {
			i++ // skip the pattern: "-name -exec" names files called "-exec"
			continue
		}
		c.generic(a) // start points, -newer FILE, -samefile FILE, ...
	}
}

// grep: short options that take a value, and long ones.
const grepValueShort = "efmABCdD"

var grepValueLong = []string{"regexp", "file", "max-count", "after-context", "before-context",
	"context", "directories", "devices", "label", "include", "exclude", "exclude-dir",
	"exclude-from", "binary-files", "group-separator"}

// grep classifies grep's arguments. GNU grep permutes arguments (options
// may come after operands), so the walk collects operands first and
// decides at the end: the first operand is the pattern only if no -e or -f
// appeared anywhere. Otherwise every operand is a file.
func (c *collector) grep(args []string) {
	var operands []string
	patternByOption := false
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch {
		case a == "--":
			operands = append(operands, args[i+1:]...)
			i = len(args)
		case strings.HasPrefix(a, "--"):
			name, val, hasVal := splitLong(a)
			if isLongPrefix(name, "dereference-recursive") {
				c.deny("grep --dereference-recursive follows symlinks")
				return
			}
			if isLongPrefix(name, "regexp") || isLongPrefix(name, "file") {
				patternByOption = true
			}
			takesValue := false
			for _, o := range grepValueLong {
				takesValue = takesValue || isLongPrefix(name, o)
			}
			if !hasVal && takesValue && i+1 < len(args) {
				i++
				val, hasVal = args[i], true
			}
			// Only the exact --regexp value is a pattern; everything else,
			// abbreviations included, is checked as a possible path.
			if hasVal && name != "regexp" {
				c.generic(val)
			}
		case strings.HasPrefix(a, "-") && a != "-":
			i = c.shortCluster(args, i, shortSpec{value: grepValueShort, report: "R"}, func(letter byte, val string) {
				switch letter {
				case 'R':
					c.deny("grep -R follows symlinks (use -r)")
				case 'e':
					patternByOption = true // val is a pattern: not a path
				case 'f':
					patternByOption = true
					c.generic(val)
				default:
					c.generic(val)
				}
			})
			if c.denied.Rule != "" {
				return
			}
		default:
			operands = append(operands, a)
		}
	}
	if !patternByOption && len(operands) > 0 {
		operands = operands[1:] // the pattern
	}
	for _, o := range operands {
		c.path(o)
	}
}

// shortSpec says how a program reads its short options.
type shortSpec struct {
	value    string // letters that take a value: the rest of the cluster, or the next argument
	optional string // letters whose value can only be attached (sed -i.bak), never the next argument
	report   string // letters with no value that the caller still wants to see (grep -R)
}

// shortCluster walks one short-option cluster like "-inA3" at args[i].
// on is called for each letter in spec.value or spec.optional (with its
// value) and for each letter in spec.report (with ""). A value ends the
// cluster. A character that is not a letter or digit starts an attached
// value of an option this parser does not know, so it is checked as a
// possible path. shortCluster returns the index of the last argument it
// used (i, or i+1 if a value was the next argument).
func (c *collector) shortCluster(args []string, i int, spec shortSpec, on func(letter byte, val string)) int {
	a := args[i]
	for j := 1; j < len(a); j++ {
		letter := a[j]
		switch {
		case strings.IndexByte(spec.value, letter) >= 0:
			val := a[j+1:]
			if val == "" && i+1 < len(args) {
				i++
				val = args[i]
			}
			on(letter, val)
			return i
		case strings.IndexByte(spec.optional, letter) >= 0:
			on(letter, a[j+1:])
			return i
		case strings.IndexByte(spec.report, letter) >= 0:
			on(letter, "")
		case !isAlnum(rune(letter)):
			c.path(a[j:])
			return i
		}
	}
	return i
}

// sed classifies sed's arguments. Scripts (from -e, --expression, or the
// first operand when there is no -e) are checked by checkSedScript;
// script files (-f, --file) are denied because the policy cannot read
// them. Like grep, GNU sed permutes arguments.
func (c *collector) sed(args []string) {
	var scripts, operands []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch {
		case a == "--":
			operands = append(operands, args[i+1:]...)
			i = len(args)
		case strings.HasPrefix(a, "--"):
			name, val, hasVal := splitLong(a)
			switch {
			case isLongPrefix(name, "file"):
				c.deny("sed --file reads a script the policy cannot check (put the script in the argument)")
				return
			case len(name) >= 2 && isLongPrefix(name, "follow-symlinks"):
				c.deny("sed --follow-symlinks follows symlinks")
				return
			case isLongPrefix(name, "expression"):
				if !hasVal && i+1 < len(args) {
					i++
					val = args[i]
				}
				scripts = append(scripts, val)
			case isLongPrefix(name, "line-length") && !hasVal && i+1 < len(args):
				i++
				c.generic(args[i])
			default:
				c.generic(a) // --in-place=SUFFIX and others
			}
		case strings.HasPrefix(a, "-") && a != "-":
			i = c.shortCluster(args, i, shortSpec{value: "efl", optional: "i"}, func(letter byte, val string) {
				switch letter {
				case 'f':
					c.deny("sed -f reads a script the policy cannot check (put the script in the argument)")
				case 'e':
					scripts = append(scripts, val)
				case 'i':
					// -i takes an optional backup suffix, attached ("-i.bak").
					// A suffix with "/" puts the backup in another directory.
					c.path(val)
				default: // -l N
					c.generic(val)
				}
			})
			if c.denied.Rule != "" {
				return
			}
		default:
			operands = append(operands, a)
		}
	}
	if len(scripts) == 0 && len(operands) > 0 {
		scripts, operands = operands[:1], operands[1:]
	}
	for _, s := range scripts {
		if why := checkSedScript(s); why != "" {
			c.deny("sed script %q: %s", s, why)
			return
		}
	}
	for _, o := range operands {
		c.path(o)
	}
}

// python classifies python's arguments. The code after -c is not a path
// and is not checked (python can run anything; see the package comment).
// Everything else is checked as a possible path, including the script and
// its arguments.
func (c *collector) python(args []string) {
	for i := 0; i < len(args); i++ {
		a := args[i]
		if !strings.HasPrefix(a, "-") || a == "-" || a == "--" {
			// A script, stdin, or the end of options: python reads no more
			// options of its own, and the rest are the script's arguments.
			for _, rest := range args[i:] {
				c.generic(rest)
			}
			return
		}
		if strings.HasPrefix(a, "--") { // --version, --help, ...
			c.generic(a)
			continue
		}
		// A short cluster such as "-I", "-Ic", "-cprint(1)", "-mpytest".
		stop := false
		i = c.shortCluster(args, i, shortSpec{value: "cmWX"}, func(letter byte, val string) {
			if letter != 'c' { // -c's value is code: skipped on purpose
				c.generic(val)
			}
			stop = letter == 'c' || letter == 'm' // the rest are the program's arguments
		})
		if stop {
			for _, rest := range args[i+1:] {
				c.generic(rest)
			}
			return
		}
	}
}
