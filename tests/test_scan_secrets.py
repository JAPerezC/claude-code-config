"""Tests de scripts/scan-secrets.py."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scan-secrets.py"
spec = importlib.util.spec_from_file_location("scan_secrets", SCRIPT)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


@pytest.mark.parametrize(
    "path,forbidden",
    [
        ("projects/-home-u/abc.jsonl", True),  # ruta relativa en la raíz (bug corregido)
        ("sessions/x.json", True),
        ("sub/dir/file-history/a", True),
        (".env", True),
        ("config/.env.local", True),
        (".env.example", False),
        ("certs/server.pem", True),
        ("history.jsonl", True),
        ("plugins/datos/skills/explore-data/SKILL.md", False),
        ("skills-archive/polars/SKILL.md", False),
    ],
)
def test_is_forbidden(path, forbidden):
    assert scan.is_forbidden(Path(path)) is forbidden


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def test_staged_content_is_scanned(tmp_path):
    """Escanea lo que está en staging, no la copia de trabajo."""
    _git(tmp_path, "init", "-q")
    f = tmp_path / "config.py"
    f.write_text('API_KEY = "sk-' + "a" * 30 + '"\n')
    _git(tmp_path, "add", "config.py")
    f.write_text("API_KEY = None\n")  # el árbol de trabajo ya está limpio
    out = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True
    )
    assert out.returncode == 1
    assert "config.py" in out.stdout


def test_clean_stage_passes(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "ok.py").write_text("print('hola')\n")
    _git(tmp_path, "add", "ok.py")
    out = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True
    )
    assert out.returncode == 0
