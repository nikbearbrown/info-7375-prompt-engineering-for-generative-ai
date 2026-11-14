import importlib.util
import sysconfig


def test_pyyaml_is_installed():
    # The real PyYAML, installed in site-packages, not a yaml.py next to the code.
    spec = importlib.util.find_spec("yaml")
    assert spec is not None and spec.origin is not None
    assert spec.origin.startswith(sysconfig.get_paths()["purelib"] + "/")


def test_load():
    from settings import load
    assert load("name: demo\nport: 8080\ntags: [a, b]\n") == {"name": "demo", "port": 8080, "tags": ["a", "b"]}
