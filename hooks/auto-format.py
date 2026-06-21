#!/usr/bin/env python3
"""
Hook PostToolUse: auto-formatea archivos Python despues de cada edicion.
Usa ruff si esta disponible, si no, no hace nada (fail-safe).
"""
import json
import shutil
import subprocess
import sys

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # Obtener ruta del archivo editado
    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    # Solo formatear si ruff esta disponible
    ruff_path = shutil.which("ruff")
    if not ruff_path:
        sys.exit(0)

    # Formatear con ruff
    try:
        subprocess.run(
            [ruff_path, "format", file_path],
            capture_output=True, timeout=10
        )
        subprocess.run(
            [ruff_path, "check", "--fix", file_path],
            capture_output=True, timeout=10
        )
    except Exception:
        pass  # No bloquear si falla

    sys.exit(0)

if __name__ == "__main__":
    main()
