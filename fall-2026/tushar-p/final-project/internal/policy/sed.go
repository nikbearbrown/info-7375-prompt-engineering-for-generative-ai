package policy

import "fmt"

// checkSedScript returns "" if a sed script uses only allowed commands, or
// why it is denied.
//
// It is an allowlist: the script is parsed command by command (GNU sed
// syntax), and anything it does not recognise is denied, so a parsing gap
// denies too much rather than too little. Denied: e (runs a shell command),
// w and W (write a file), r and R (read a file the policy cannot check),
// and the e and w flags of s. sed also runs with --sandbox (see
// checkCommand), so GNU sed itself refuses e, r, and w as well.
func checkSedScript(script string) string {
	p := &sedParser{s: script}
	return p.run()
}

// sedParser walks a script one byte at a time. i is the next byte to read.
type sedParser struct {
	s string
	i int
}

func (p *sedParser) eof() bool  { return p.i >= len(p.s) }
func (p *sedParser) peek() byte { return p.s[p.i] }

// skip moves past any of the bytes in set.
func (p *sedParser) skip(set string) {
	for !p.eof() && containsByte(set, p.peek()) {
		p.i++
	}
}

func containsByte(set string, b byte) bool {
	for i := 0; i < len(set); i++ {
		if set[i] == b {
			return true
		}
	}
	return false
}

func (p *sedParser) run() string {
	for {
		p.skip(" \t\n;")
		if p.eof() {
			return ""
		}
		if p.peek() == '#' { // comment to end of line
			p.toEndOfLine()
			continue
		}
		if why := p.addresses(); why != "" {
			return why
		}
		p.skip(" \t")
		for !p.eof() && p.peek() == '!' { // "!" negates the address
			p.i++
			p.skip(" \t")
		}
		if p.eof() {
			return "missing command after address"
		}
		cmd := p.s[p.i]
		p.i++
		if why := p.command(cmd); why != "" {
			return why
		}
	}
}

// command parses what follows one command letter.
func (p *sedParser) command(cmd byte) string {
	switch cmd {
	case '{', '}': // blocks: the commands inside are parsed like any other
		return ""
	case '=', 'd', 'D', 'g', 'G', 'h', 'H', 'n', 'N', 'p', 'P', 'x', 'z', 'F':
		return p.endOfCommand()
	case 'q', 'Q', 'l', 'L': // optional number
		p.skip(" \t")
		p.skip("0123456789")
		return p.endOfCommand()
	case 'b', 't', 'T', ':': // label, up to ";" or the end of the line
		for !p.eof() && p.peek() != ';' && p.peek() != '\n' {
			p.i++
		}
		return ""
	case 'a', 'i', 'c': // text to the end of the line; "\" + newline continues it
		for !p.eof() && p.peek() != '\n' {
			if p.peek() == '\\' {
				p.i++
			}
			p.i++
		}
		return ""
	case 's':
		return p.substitute()
	case 'y':
		if why := p.delimited(2); why != "" {
			return why
		}
		return p.endOfCommand()
	case 'e':
		return `sed command "e" runs a shell command`
	case 'w', 'W':
		return fmt.Sprintf("sed command %q writes a file (use write_file)", string(cmd))
	case 'r', 'R':
		return fmt.Sprintf("sed command %q reads a file the policy cannot check", string(cmd))
	}
	return fmt.Sprintf("sed command %q is not on the allowed list", string(cmd))
}

// substitute parses s/regex/replacement/flags.
func (p *sedParser) substitute() string {
	if why := p.delimited(2); why != "" {
		return why
	}
	for !p.eof() {
		switch b := p.peek(); {
		case containsByte("gpiImM0123456789", b):
			p.i++
		case b == 'e':
			return `sed s command flag "e" runs the result as a shell command`
		case b == 'w':
			return `sed s command flag "w" writes a file (use write_file)`
		default:
			return p.endOfCommand()
		}
	}
	return ""
}

// delimited reads a delimiter byte and then n parts, each ending with that
// delimiter (s/a/b/ has n = 2 after the first "/"). As in GNU sed, only a
// backslash escapes the delimiter.
func (p *sedParser) delimited(n int) string {
	if p.eof() || p.peek() == '\n' || p.peek() == '\\' {
		return "unterminated command: missing delimiter"
	}
	delim := p.s[p.i]
	p.i++
	for part := 0; part < n; part++ {
		if why := p.until(delim); why != "" {
			return why
		}
	}
	return ""
}

// until moves past the next unescaped delim.
func (p *sedParser) until(delim byte) string {
	for !p.eof() {
		b := p.s[p.i]
		p.i++
		switch {
		case b == '\\':
			p.i++ // the escaped byte, whatever it is
		case b == delim:
			return ""
		case b == '\n':
			return "unterminated command: newline before the closing delimiter"
		}
	}
	return "unterminated command: missing closing delimiter"
}

// addresses parses zero, one, or two addresses ("3", "$", "/re/",
// "\%re%", "1,5", "/a/,+2", "0~4").
func (p *sedParser) addresses() string {
	if why := p.address(); why != "" {
		return why
	}
	p.skip(" \t")
	if !p.eof() && p.peek() == ',' {
		p.i++
		p.skip(" \t")
		if !p.eof() && (p.peek() == '+' || p.peek() == '~') {
			p.i++
			p.skip("0123456789")
			return ""
		}
		return p.address()
	}
	return ""
}

func (p *sedParser) address() string {
	if p.eof() {
		return ""
	}
	switch b := p.peek(); {
	case b >= '0' && b <= '9':
		p.skip("0123456789")
		if !p.eof() && p.peek() == '~' {
			p.i++
			p.skip("0123456789")
		}
	case b == '$':
		p.i++
	case b == '/':
		p.i++
		if why := p.until('/'); why != "" {
			return why
		}
		p.skip("IM") // regex address flags
	case b == '\\': // \%regex% with any delimiter
		p.i++
		if p.eof() {
			return "unterminated address"
		}
		delim := p.s[p.i]
		p.i++
		if why := p.until(delim); why != "" {
			return why
		}
		p.skip("IM")
	}
	return ""
}

// endOfCommand checks that a command is followed by ";", a newline, "}",
// "#", or the end of the script, as GNU sed requires.
func (p *sedParser) endOfCommand() string {
	p.skip(" \t")
	if p.eof() || containsByte(";\n}#", p.peek()) {
		return ""
	}
	return fmt.Sprintf("unexpected %q after a command", string(p.peek()))
}

func (p *sedParser) toEndOfLine() {
	for !p.eof() && p.peek() != '\n' {
		p.i++
	}
}
