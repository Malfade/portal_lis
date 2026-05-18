import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "security" / "license-remote-check.sh"


def test_remote_check_script_fails_on_unreachable_port():
    env = os.environ.copy()
    env["LICENSE_API_BASE_URL"] = "http://127.0.0.1"
    env["LICENSE_API_TOKEN"] = "aksec_test"
    env["INSTANCE_ID_OVERRIDE"] = "abc"
    # Port 9 is discard / typically closed; curl should fail quickly
    env["LICENSE_API_BASE_URL"] = "http://127.0.0.1:9"
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode != 0
