import subprocess

from release import commit


def test_commit_matches_git():
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    assert len(head) == 40
    assert commit() == head
