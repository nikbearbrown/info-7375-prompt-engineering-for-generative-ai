package trace

// Tests for the optional truncation section (D26).

import (
	"bytes"
	"strings"
	"testing"
)

// withTruncation is good() with a truncation section, as JSON.
func withTruncation(t *testing.T, limit, head, tail int) string {
	g := good()
	g.Truncation = &Truncation{LimitBytes: limit, HeadBytes: head, TailBytes: tail}
	return string(encode(t, g))
}

func TestDecodeTruncation(t *testing.T) {
	// Present and consistent: accepted.
	if _, err := Decode(strings.NewReader(withTruncation(t, 8192, 4096, 4096))); err != nil {
		t.Fatalf("good truncation rejected: %v", err)
	}
	// Absent (every trace before D26): still accepted.
	if _, err := Decode(bytes.NewReader(encode(t, good()))); err != nil {
		t.Fatalf("trace without truncation rejected: %v", err)
	}
	base := withTruncation(t, 8192, 4096, 4096)
	tests := []struct{ name, json, want string }{
		{"head + tail != limit", withTruncation(t, 8192, 4096, 1000), "truncation"},
		{"zero tail", withTruncation(t, 4096, 4096, 0), "truncation"},
		{"missing head_bytes", strings.Replace(base, `"head_bytes":4096,`, ``, 1), `missing required key "head_bytes"`},
		{"unknown key", strings.Replace(base, `"head_bytes":`, `"mode":"head","head_bytes":`, 1), "unknown field"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if tc.json == base {
				t.Fatal("test setup: the replacement did not change the trace")
			}
			_, err := Decode(strings.NewReader(tc.json))
			if err == nil || !strings.Contains(err.Error(), tc.want) {
				t.Errorf("err = %v, want it to mention %q", err, tc.want)
			}
		})
	}
}
