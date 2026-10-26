---
name: session-start
description: Inicia una sesión de trabajo cargando el contexto del proyecto (PROGRESS.md, historial de handoff, TODO.org, estado de git) y propone en qué enfocarse.
argument-hint: "[archivar]"
disable-model-invocation: true
---

Iniciar una nueva sesión de trabajo cargando el contexto existente. Sé breve: el
objetivo es orientar, no releer el proyecto entero.

## Pasos

0. **Archivar conversaciones anteriores (solo si `$ARGUMENTS` incluye `archivar`)**:
   - Ejecutar: `python3 ~/.claude/convos.py archive-project "$(pwd)" "${CLAUDE_SESSION_ID}"`
   - Mueve las conversaciones del proyecto a `~/.claude/archive/` excepto la sesión en
     curso. Las archivadas dejan de aparecer en `/resume`; avisa al usuario de ello.
   - Si falla o no hay conversaciones anteriores, continuar sin bloquear.

1. **Leer archivos de contexto** (solo los que existan; no los crees):
   - `PROGRESS.md` (estado del último hito)
   - `docs/[PROYECTO]-session-summary.org`: solo la sesión más reciente
   - `TODO.org`: tareas abiertas
   - CLAUDE.md ya está cargado; no lo releas.

2. **Estado de git**: rama, últimos 5 commits (`git log --oneline -5`), cambios sin
   commitear, merge/rebase en curso.

3. **Presentar el briefing**:

```org
* Inicio de Sesión — [FECHA]
:PROPERTIES:
:SESSION_DATE: [YYYY-MM-DD]
:PROJECT: [NOMBRE_PROYECTO]
:BRANCH: [BRANCH_ACTUAL]
:END:

** Dónde nos quedamos
[3-5 líneas desde PROGRESS.md / última sesión]

** Tareas Pendientes
- [ ] [Desde TODO.org o el checklist de la última sesión]

** Estado de git
- Working tree: [limpio/con cambios] · Último commit: [mensaje corto]

** Enfoque sugerido
1. [Tarea prioritaria]
2. [Trabajo sin terminar]
```

4. **Preguntar**: "¿En qué te gustaría enfocarte esta sesión?"
