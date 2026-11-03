import json

import pytest

from agent import resume as resume_mod
from conftest import PERSONA_PATH


def test_17_real_looking_email_is_refused(resume, tmp_path):
    resume["personal"]["email"] = "arjun.mehta@gmail.com"
    path = tmp_path / "persona_gmail.json"
    path.write_text(json.dumps(resume))
    with pytest.raises(ValueError):
        resume_mod.load_resume(path)


def test_17b_fictional_persona_loads(resume):
    assert resume_mod.load_resume(PERSONA_PATH) == resume
