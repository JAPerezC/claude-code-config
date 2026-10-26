#!/usr/bin/env python3
"""
Hook de seguridad PreToolUse para Claude Code.

Solo actúa ante lo verdaderamente peligroso: destrucción de datos y exposición
de secretos. Responde con JSON (hookSpecificOutput.permissionDecision):
  - "deny": se bloquea y Claude recibe el motivo.
  - "ask":  se pide confirmación al usuario (operaciones legítimas pero
            irreversibles, como sudo o un push forzado).
Sin salida = no opina; decide el sistema de permisos normal.

Matcher recomendado: "Bash|Read|Edit|Write|MultiEdit".
"""

import json
import re
import sys

# --- Bash: (patrón, decisión, motivo) ---------------------------------------
BASH_RULES = [
    # Destrucción sin vuelta atrás de la raíz, el home o el disco.
    (r"\brm\s+-[a-zA-Z]*[rR][a-zA-Z]*\s+(-\S+\s+)*(/|~|\$HOME)/?(\s|$)", "deny",
     "rm recursivo sobre /, ~ o $HOME"),
    (r"\bmkfs(\.\w+)?\s", "deny", "mkfs formatea un disco"),
    (r"\bdd\s+[^|;&]*\bof=/dev/", "deny", "dd escribiendo a un dispositivo"),
    (r"(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(ba|z)?sh\b", "deny",
     "descargar y ejecutar en shell (curl|sh)"),
    (r"\bchmod\s+(-R\s+)?777\b", "deny", "chmod 777: permisos inseguros"),
    # Irreversibles pero a veces legítimos: preguntar.
    (r"\brm\s+-[a-zA-Z]*([rR][a-zA-Z]*f|f[a-zA-Z]*[rR])", "ask",
     "rm -rf: confirma la ruta"),
    (r"\bgit\s+push\b[^;&|]*(\s--force(-with-lease)?\b|\s-f\b|\s\+\S)", "ask",
     "push forzado: puede reescribir historial remoto"),
    (r"\bgit\s+reset\s+--hard\b", "ask", "git reset --hard descarta cambios"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "ask", "git clean borra archivos sin rastrear"),
    (r"(^|[;&|]\s*)sudo\s", "ask", "sudo requiere confirmación"),
]

# Archivos con secretos (para Bash y para Read/Edit/Write).
SECRET_FILE = re.compile(
    r"(^|[/\s'\"=])("
    r"\.env(\.(?!example\b)[\w.-]+)?"  # .env, .env.local (no .env.example)
    r"|[\w.-]+\.(pem|key|p12|pfx)"
    r"|id_(rsa|ed25519|ecdsa)(?!\.pub)\b"
    r"|\.ssh/[\w.-]+"
    r"|\.credentials\.json|credentials(\.json)?"
    r"|\.secrets?(/|\b)"
    r"|\.netrc|\.pgpass"
    r")(?=$|[\s'\";|&)])"
)
# Comandos que vuelcan contenido de un archivo.
DUMPERS = re.compile(
    r"\b(cat|less|more|head|tail|bat|grep|rg|awk|sed|strings|xxd|od|base64|"
    r"cp|scp|curl|python3?|node|source)\b"
)
SECRET_ENV = [
    (r"\becho\s+[^|;&]*\$\{?[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)",
     "imprime una variable con un secreto"),
    (r"(^|[;&]\s*)(printenv|env|export\s+-p)\s*($|[;&])",
     "vuelca todas las variables de entorno"),
]


def decide(decision, reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"security-gate: {reason}",
        }
    }))
    sys.exit(0)


def check_bash(cmd):
    for pattern, decision, reason in BASH_RULES:
        if re.search(pattern, cmd):
            decide(decision, reason)
    if DUMPERS.search(cmd) and SECRET_FILE.search(cmd):
        decide("deny", "lectura de un archivo de secretos vía Bash; usa python-dotenv o pide el valor al usuario")
    for pattern, reason in SECRET_ENV:
        if re.search(pattern, cmd):
            decide("deny", reason)


def check_file(path):
    if SECRET_FILE.search(" " + path):
        decide("deny", f"acceso a archivo de secretos: {path}")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    if tool == "Bash":
        check_bash(tool_input.get("command", ""))
    elif tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        check_file(tool_input.get("file_path", "") or tool_input.get("notebook_path", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
