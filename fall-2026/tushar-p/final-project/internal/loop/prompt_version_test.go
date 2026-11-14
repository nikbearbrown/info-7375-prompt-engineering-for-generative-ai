package loop

import (
	"regexp"
	"testing"

	"github.com/anthropics/anthropic-sdk-go/v2"
)

// PromptVersion is a stable SHA-256, and it changes when any one part of
// what the harness sends changes.
func TestPromptVersion(t *testing.T) {
	v := PromptVersion()
	if !regexp.MustCompile(`^[0-9a-f]{64}$`).MatchString(v) || v != PromptVersion() {
		t.Fatalf("PromptVersion = %q, want a stable hex SHA-256", v)
	}
	tools := []anthropic.ToolParam{toolDefs["read_file"], toolDefs["run_command"], toolDefs["write_file"]}
	if got := promptVersion(systemPrompt, taskMessage, NotCompleteNote, tools); got != v {
		t.Errorf("tools in name order should give PromptVersion: %s vs %s", got, v)
	}
	changed := toolDefs["run_command"]
	changed.Description = anthropic.String("something else")
	for name, other := range map[string]string{
		"system prompt": promptVersion(systemPrompt+" ", taskMessage, NotCompleteNote, tools),
		"task message":  promptVersion(systemPrompt, taskMessage+" ", NotCompleteNote, tools),
		"note":          promptVersion(systemPrompt, taskMessage, NotCompleteNote+" ", tools),
		"a tool description": promptVersion(systemPrompt, taskMessage, NotCompleteNote,
			[]anthropic.ToolParam{toolDefs["read_file"], changed, toolDefs["write_file"]}),
		"tool order": promptVersion(systemPrompt, taskMessage, NotCompleteNote,
			[]anthropic.ToolParam{toolDefs["write_file"], toolDefs["run_command"], toolDefs["read_file"]}),
	} {
		if other == v {
			t.Errorf("changing the %s did not change the prompt version", name)
		}
	}
}
