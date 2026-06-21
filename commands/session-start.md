Iniciar una nueva sesión de trabajo cargando contexto existente.

## Pasos

0. **Archivar conversaciones anteriores del proyecto**:
   - Ejecutar: `python3 ~/.claude/scripts/convos.py archive-project "$(pwd)"`
   - Esto archiva TODAS las conversaciones del proyecto actual excepto la sesión en uso
   - Si hay errores o no hay conversaciones anteriores, continuar sin bloquear

1. **Leer archivos de contexto** (si existen):
   - `CLAUDE.md` para instrucciones del proyecto
   - `docs/[PROYECTO]-session-summary.org` para historial de sesiones recientes
   - `TODO.org` para tareas pendientes
   - `working-outline.md` para estructura del proyecto

2. **Analizar estado de git**:
   - Branch actual y commits recientes
   - Cambios sin commitear (working tree dirty)
   - Merge/rebase en progreso

3. **Presentar briefing de sesión**:

```org
* Inicio de Sesión — [FECHA]
:PROPERTIES:
:SESSION_DATE: [YYYY-MM-DD]
:SESSION_TIME: [HH:MM]
:TIMEZONE: America/Mexico_City
:PROJECT: [NOMBRE_PROYECTO]
:BRANCH: [BRANCH_ACTUAL]
:END:

** Contexto Cargado
- CLAUDE.md: [estado]
- Historial de sesiones: [N sesiones encontradas]
- TODO.org: [N tareas pendientes]

** Resumen de Sesión Anterior
[Puntos clave de la última sesión desde session-summary.org]

** Tareas Pendientes
- [ ] [Desde TODO.org]
- [ ] [Desde checklist de última sesión]

** Estado Actual
- Branch: [branch]
- Working tree: [limpio/con cambios]
- Último commit: [mensaje corto]

** Enfoque Sugerido
Basándome en el contexto, sugiero trabajar en:
1. [Tarea prioritaria]
2. [Trabajo sin terminar]
3. [Siguiente paso natural]
```

4. **Preguntar**: "¿En qué te gustaría enfocarte esta sesión?"
