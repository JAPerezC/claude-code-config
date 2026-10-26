#!/usr/bin/env python3
"""
Hook PostToolUse: auto-formatea archivos Python despues de cada edicion.
Usa ruff si esta disponible, si no, no hace nada (fail-safe).

Si ruff cambia el archivo, se avisa a Claude (additionalContext) para que lo
relea antes de volver a editarlo; si no, el siguiente Edit falla porque el
texto en memoria ya no coincide con el del disco.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _digest(path):
    try:
        return hashlib.sha1(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    ruff_path = shutil.which("ruff")
    if not ruff_path:
        sys.exit(0)

    before = _digest(file_path)
    try:
        subprocess.run([ruff_path, "format", file_path], capture_output=True, timeout=10)
        # F401 (imports sin usar) no se autocorrige: el modelo suele añadir el
        # import antes que el código que lo usa, y ruff lo borraría a mitad de tarea.
        subprocess.run(
            [ruff_path, "check", "--fix", "--unfixable", "F401", file_path],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        sys.exit(0)  # No bloquear si falla

    if before is not None and _digest(file_path) != before:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": (
                            f"auto-format: ruff reformateó {file_path}; "
                            "reléelo antes de volver a editarlo."
                        ),
                    }
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
