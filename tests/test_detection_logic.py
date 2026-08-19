from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_detection_script_compiles():
    source = (ROOT / "scripts" / "detect.py").read_text()
    ast.parse(source)


def test_required_detection_names_present():
    source = (ROOT / "scripts" / "detect.py").read_text()
    for name in (
        "ssh_bruteforce",
        "windows_bruteforce",
        "web_scan",
        "application_errors",
        "failure_then_success",
    ):
        assert f"def {name}" in source
