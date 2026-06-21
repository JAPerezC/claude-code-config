# claude-code-config

Mi configuración de **Claude Code** (hooks, skills, comandos, agentes, settings) para
reproducir mi setup en cualquier máquina.

> ⚠️ Repo **curado**: NO contiene credenciales, historial, transcripts ni datos privados.
> Un hook `pre-commit` + `scripts/scan-secrets.py` bloquean cualquier secreto antes de subirlo.

## Contenido

| Carpeta / archivo | Qué es |
|---|---|
| `hooks/` | `security-gate.py` (PreToolUse) y `auto-format.py` (ruff) |
| `commands/` | Slash commands (handoff, session-start, session-summary) |
| `agents/` | Subagentes (code-reviewer, data-validator, investigador, ...) |
| `skills/` | 23 skills activas |
| `skills-archive/` | 24 skills archivadas |
| `statusline.py` | Statusline personalizada |
| `templates/` | Plantillas de proyecto |
| `scripts/convos.py` | Gestor de conversaciones |
| `scripts/scan-secrets.py` | Escáner de secretos (pre-commit) |

> Nota: `settings.json`, el `CLAUDE.md` global y `memory/` se **excluyen a propósito** por privacidad — configura los tuyos.

## Instalar en otra máquina

```bash
git clone https://github.com/JAPerezC/claude-code-config.git
cd claude-code-config
bash install.sh          # copia a ~/.claude (respalda lo existente)
git config core.hooksPath .githooks   # activa el escáner de secretos
```

## Seguridad

- **`.gitignore` blindado**: ignora `.credentials.json`, `.env*`, `history*`, `projects/`,
  transcripts, claves `*.pem`/`*.key`, caches, etc.
- **Escáner de secretos**: `python scripts/scan-secrets.py` (lo ejecuta el `pre-commit`).
  Detecta tokens de GitHub/AWS/Google/Slack, claves `sk-...`, bloques de clave privada,
  asignaciones `password=/api_key=` y archivos privados prohibidos.
- Las skills con scripts **ejecutan código**: revísalas antes de instalarlas.

## Licencia

MIT (ver cada skill de terceros para su propia licencia).
