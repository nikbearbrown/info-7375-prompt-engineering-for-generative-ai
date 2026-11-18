package contracts

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"testing"
)

// The embedded strings are the files' exact bytes, and the files are the
// frozen ones (D30): a changed byte, an added trailing newline, or a
// straight quote in place of a curly one fails here.
func TestFrozenSystemPrompts(t *testing.T) {
	for _, tc := range []struct {
		name   string
		bytes  int
		sha256 string
	}{
		{"A", 623, "217dbb8f78d6c56bb6b40d3c2442746d6c924af60ec70b312102b27d9cd23701"},
		{"B", 2695, "5bd2572217f96e5b5c97a6ce63555ae22a5fbc9ad64902e31d6f2942ba9000c4"},
	} {
		c := MustGet(tc.name)
		file, err := os.ReadFile(tc.name + "-system.txt")
		if err != nil {
			t.Fatal(err)
		}
		if c.System != string(file) {
			t.Errorf("%s: embedded prompt differs from %s-system.txt", tc.name, tc.name)
		}
		sum := sha256.Sum256([]byte(c.System))
		if len(c.System) != tc.bytes || hex.EncodeToString(sum[:]) != tc.sha256 {
			t.Errorf("%s: %d bytes, sha256 %x; want %d bytes, %s", tc.name, len(c.System), sum, tc.bytes, tc.sha256)
		}
	}
}

func TestGet(t *testing.T) {
	if got := Names(); len(got) != 2 || got[0] != "A" || got[1] != "B" {
		t.Errorf("Names = %v", got)
	}
	if c, err := Get(Default); err != nil || c.Name != "A" {
		t.Errorf("Get(Default) = %+v, %v", c, err)
	}
	for _, bad := range []string{"", "a", "C", "A "} {
		if _, err := Get(bad); err == nil {
			t.Errorf("Get(%q) should fail", bad)
		}
	}
}
