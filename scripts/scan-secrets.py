#!/usr/bin/env python3
"""Escáner de secretos y archivos privados para pre-commit / auditoría.

Uso:
  python scan-secrets.py                # escanea los archivos en staging (git)
  python scan-secrets.py ruta [ruta...] # escanea archivos/carpetas dados

Sale con código 1 si encuentra un secreto o un archivo privado prohibido.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("OpenAI/Anthropic key", re.compile(r"sk-[A-Za-z0-9_\-]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{30,}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "Asignación de secreto",
        re.compile(
            r"(?i)(api[_-]?key|secret|password|passwd|client[_-]?secret|access[_-]?token)"
            r"\s*[:=]\s*['\"][^'\"]{8,}['\"]"
        ),
    ),
    ("Bearer token", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}")),
]

# Subcadenas que indican un placeholder/ejemplo (no un secreto real).
PLACEHOLDERS = (
    "your",
    "xxx",
    "...",
    "<",
    "example",
    "changeme",
    "dummy",
    "placeholder",
    "redacted",
    "sample",
    "_here",
    "list-item",
    "checkbox",
    "container",
    "todo",
    "fake",
    "demo",
    "my-key",
    "my_key",
    "tu_",
    "tu-",
    "aqui",
)


def _is_placeholder(value: str) -> bool:
    v = value.lower()
    return any(p in v for p in PLACEHOLDERS)


def is_forbidden(path: Path) -> bool:
    """Archivos/rutas que NUNCA deben commitearse (privados/credenciales)."""
    n = path.name
    # git devuelve rutas relativas ("projects/x"); se antepone "/" para que
    # los directorios en la raíz del repo también coincidan con "/projects/".
    s = "/" + str(path).replace("\\", "/").removeprefix("./")
    if n == ".env.example":
        return False
    if n == ".credentials.json" or n in (
        "history.jsonl",
        "history.jsonl.bak",
        "command-log.txt",
    ):
        return True
    if n == ".env" or n.startswith(".env."):
        return True
    if n.endswith((".pem", ".key")) or n.startswith("id_rsa"):
        return True
    for d in (
        "/projects/",
        "/projects-archive/",
        "/archive/",
        "/sessions/",
        "/shell-snapshots/",
        "/file-history/",
        "/paste-cache/",
        "/backups/",
        "/session-env/",
        "/todos/",
    ):
        if d in s:
            return True
    return False


def staged_text(path: Path) -> str | None:
    """Contenido en staging (lo que realmente se va a commitear)."""
    out = subprocess.run(
        ["git", "show", f":{path.as_posix()}"], capture_output=True
    )
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="ignore")


def files_to_check(args: list[str]) -> list[Path]:
    if not args:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
        )
        return [Path(p) for p in out.stdout.splitlines() if p.strip()]
    result: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            result += [f for f in p.rglob("*") if f.is_file()]
        else:
            result.append(p)
    return result


def main() -> int:
    staged = not sys.argv[1:]
    files = files_to_check(sys.argv[1:])
    hits = []
    for f in files:
        if is_forbidden(f):
            hits.append((str(f), "ARCHIVO PRIVADO PROHIBIDO", ""))
            continue
        if staged:
            text = staged_text(f)
            if text is None:
                continue
        else:
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
        for name, pat in PATTERNS:
            for m in pat.finditer(text):
                if _is_placeholder(m.group(0)):
                    continue
                hits.append((str(f), name, m.group(0)[:12] + "..."))
                break

    if hits:
        print("BLOQUEADO — secretos o archivos privados detectados:")
        for f, kind, sample in hits:
            print(f"  [{kind}] {f} {sample}")
        print("\nQuita el secreto, o añade el archivo a .gitignore antes de commitear.")
        return 1
    print(
        f"scan-secrets: OK — {len(files)} archivos revisados, sin secretos ni privados."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
