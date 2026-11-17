package main

import (
	"context"
	"testing"

	"github.com/tushar-patel28/agent-proving-ground/internal/trace"
)

// An agent run records the truncation settings in its trace (D26), and
// the trace still validates.
func TestTraceRecordsTruncation(t *testing.T) {
	client := &exitClient{replies: []reply{done}, counts: []int64{100}}
	tr := runTask(context.Background(), &exitSandbox{}, "apg-fake", exitTask(roomy), client, nil)
	want := trace.Truncation{LimitBytes: 8192, HeadBytes: 4096, TailBytes: 4096}
	if tr.Truncation == nil || *tr.Truncation != want {
		t.Fatalf("truncation = %+v, want %+v", tr.Truncation, want)
	}
	if _, err := trace.Write(t.TempDir(), tr); err != nil {
		t.Errorf("trace does not write: %v", err)
	}
}
