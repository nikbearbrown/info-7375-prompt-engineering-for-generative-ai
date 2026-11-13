package sandbox

import (
	"encoding/json"
	"testing"
)

// The pod spec sets the container's working directory explicitly, so every
// kubectl exec (which has no working-directory option) starts in
// /workspace whatever the image's WORKDIR says. The policy resolves
// relative paths against /workspace and relies on this (T2.1).
func TestManifestWorkingDir(t *testing.T) {
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
				Containers []struct {
					WorkingDir string `json:"workingDir"`
				} `json:"containers"`
			} `json:"spec"`
		} `json:"items"`
	}
	if err := json.Unmarshal(b, &list); err != nil {
		t.Fatal(err)
	}
	pods := 0
	for _, it := range list.Items {
		if it.Kind != "Pod" {
			continue
		}
		pods++
		if len(it.Spec.Containers) != 1 || it.Spec.Containers[0].WorkingDir != "/workspace" {
			t.Errorf("containers = %+v, want one with workingDir /workspace", it.Spec.Containers)
		}
	}
	if pods != 1 {
		t.Errorf("found %d pods in the manifest, want 1", pods)
	}
}
