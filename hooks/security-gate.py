#!/usr/bin/env python3
"""
Hook de seguridad PreToolUse para Claude Code.
Solo bloquea lo verdaderamente peligroso: destruccion de datos y exposicion de secretos.
Exit 0 = permitir, Exit 2 = bloquear.
"""

import json
import re
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    # Solo comandos verdaderamente destructivos o irreversibles
    dangerous_patterns = [
        (
            r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f",
            "rm -rf detectado — usa rm sin -rf o consulta al usuario",
        ),
        (r"rm\s+-[a-zA-Z]*f[a-zA-Z]*r", "rm -fr detectado"),
        (r"git\s+reset\s+--hard", "git reset --hard — operacion irreversible"),
        (
            r"git\s+push\s+(--force|-f)\b",
            "git push --force — puede destruir historial remoto",
        ),
        (r"git\s+clean\s+-fd", "git clean -fd — elimina archivos sin rastrear"),
        (r"^(?!wsl\b).*sudo\s+", "sudo no permitido (permitido dentro de wsl)"),
        (r"mkfs\s+", "mkfs detectado"),
        (r"dd\s+if=", "dd detectado"),
        (r"chmod\s+777", "chmod 777 — permisos inseguros"),
        (r"curl\s+.*\|\s*(ba)?sh", "pipe a shell detectado"),
        (r"wget\s+.*\|\s*(ba)?sh", "pipe a shell detectado"),
    ]

    # Acceso directo a secretos via Bash (lo que las deny rules no cubren)
    secret_patterns = [
        (
            r"(cat|less|more|head|tail|type)\s+.*\.env\b",
            "lectura de .env via Bash — usa python-dotenv",
        ),
        (r"(cat|less|more|head|tail|type)\s+.*\.pem\b", "lectura de .pem via Bash"),
        (r"(cat|less|more|head|tail|type)\s+.*\.key\b", "lectura de .key via Bash"),
        (
            r"(cat|less|more|head|tail|type)\s+.*\.secrets",
            "lectura de .secrets via Bash",
        ),
        (
            r"(cat|less|more|head|tail|type)\s+.*credentials",
            "lectura de credentials via Bash",
        ),
        (r"(cat|less|more|head|tail|type)\s+.*\.ssh/", "lectura de .ssh via Bash"),
        (
            r"echo\s+\$[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)",
            "exposicion de variable sensible",
        ),
        (r"^\s*printenv\s*$", "printenv detectado"),
        (r"^\s*env\s*$", "comando env detectado"),
    ]

    for pattern, description in dangerous_patterns:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(f"BLOQUEADO: {description}", file=sys.stderr)
            sys.exit(2)

    for pattern, description in secret_patterns:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(f"BLOQUEADO: {description}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
