package trace

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// encode writes tr as JSON without validating it.
func encode(t *testing.T, tr *Trace) []byte {
	t.Helper()
	if tr.Steps == nil {
		tr.Steps = []Step{}
	}
	if tr.CheckRuns == nil {
		tr.CheckRuns = []CheckRun{}
	}
	b, err := json.Marshal(tr)
	if err != nil {
		t.Fatal(err)
	}
	return b
}

func TestDecodeAcceptsGoodTrace(t *testing.T) {
	if _, err := Decode(bytes.NewReader(encode(t, good()))); err != nil {
		t.Fatal(err)
	}
}

// Decode is strict: unknown keys, missing required keys, and values that
// break the rules are all rejected.
func TestDecodeRejects(t *testing.T) {
	g := string(encode(t, good()))
	tests := []struct {
		name, json, want string
	}{
		{"unknown top-level key", strings.Replace(g, `"pod":`, `"total_input_tokens": 5, "pod":`, 1), "unknown field"},
		{"unknown command key", strings.Replace(g, `"actor":`, `"who": "x", "actor":`, 1), "unknown field"},
		{"missing check_runs", strings.Replace(g, `,"check_runs":[]`, ``, 1), `missing required key "check_runs"`},
		{"missing command actor", strings.Replace(g, `"actor":"harness",`, ``, 1), `missing required key "actor"`},
		{"agent actor on a check command", strings.Replace(g, `"actor":"harness"`, `"actor":"agent"`, 1), "actor"},
		{"v0 trace", strings.Replace(g, `"schema_version":1`, `"schema_version":0`, 1), "schema_version"},
		{"PASS with a failing check", strings.Replace(g, `"verdict":"FAIL"`, `"verdict":"PASS"`, 1), "verdict"},
		{"two traces", g + g, "extra data"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if tc.json == g {
				t.Fatal("test setup: the replacement did not change the trace")
			}
			_, err := Decode(strings.NewReader(tc.json))
			if err == nil || !strings.Contains(err.Error(), tc.want) {
				t.Errorf("err = %v, want it to mention %q", err, tc.want)
			}
		})
	}
}

// Every v1 trace in evidence/ decodes strictly. v0 traces (before T2.5)
// are left as they were and only counted.
func TestEvidenceTraces(t *testing.T) {
	paths, err := filepath.Glob(filepath.Join("..", "..", "evidence", "traces", "*.json"))
	if err != nil || len(paths) == 0 {
		t.Fatalf("no evidence traces: %v", err)
	}
	v0, v1 := 0, 0
	for _, p := range paths {
		b, err := os.ReadFile(p)
		if err != nil {
			t.Fatal(err)
		}
		var head struct {
			SchemaVersion int `json:"schema_version"`
		}
		if err := json.Unmarshal(b, &head); err != nil {
			t.Fatalf("%s: %v", p, err)
		}
		switch head.SchemaVersion {
		case 0:
			v0++
		case 1:
			v1++
			if _, err := Decode(bytes.NewReader(b)); err != nil {
				t.Errorf("%s: %v", filepath.Base(p), err)
			}
		default:
			t.Errorf("%s: schema_version %d", filepath.Base(p), head.SchemaVersion)
		}
	}
	t.Logf("evidence traces: %d v1 (decoded strictly), %d v0 (predate v1, not checked)", v1, v0)
}
