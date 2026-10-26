---
name: handoff
description: Cierre de sesión con snapshot de estado y handoff de continuidad (docs/*-session-summary.org, TODO.org, PROGRESS.md). Con el argumento "resumen" solo imprime el resumen sin escribir archivos.
when_to_use: Cuando el usuario dice "cerrar sesión", "handoff", "resume la sesión" o va a hacer /clear tras un hito.
argument-hint: "[resumen] [notas para el resumen]"
disable-model-invocation: true
---

# Handoff de sesión

Se ejecuta en la conversación principal (no en un subagente): el contenido sale de
lo que se habló en esta sesión — decisiones y su porqué, archivos tocados,
problemas resueltos, caminos descartados y siguientes pasos.

**Modo resumen** — si `$ARGUMENTS` empieza por `resumen`, genera solo el bloque
org de la sección 4 y muéstralo; no escribas ningún archivo.

Notas del usuario para esta sesión (si las hay): $ARGUMENTS

Cierre meticuloso de sesión para mantener continuidad de proyecto entre sesiones de trabajo. Funciona de forma determinística e idempotente.

## Reglas Base

- **Zona horaria**: la del sistema (`date +%Z`; fechas ISO: YYYY-MM-DD, horas: YYYY-MM-DDTHH:mm)
- **Seguridad**: Nunca commitear secretos, archivos .env, ni blobs binarios. Abortar si se detectan.
- **Idempotencia**: Ejecutar dos veces produce el mismo estado (sin duplicados, sin drift)
- **Sin mutaciones de red**: Nunca modificar git remotes ni push automático
- **Texto mínimo**: Crear diffs, no muros de prosa
- **Ortografía**: Usar acentos, ñ, ¿?, ¡! en todo el texto generado

## Estructura de Archivos

```
raíz-proyecto/
├── .project                          # PROJECT_NAME (solo local)
├── .gitignore                        # Actualizado con entradas de handoff
├── docs/
│   └── [PROYECTO]-session-summary.org # Historial de sesiones (solo local)
├── working-outline.md                # Esquema del proyecto (solo local)
├── TODO.org                          # Tareas org-mode (solo local)
├── CLAUDE.md                         # Contexto AI - fuente de verdad (solo local)
├── GIT_REMOTE                        # Cache de metadata git (solo local)
├── handoff-trace.log                 # Log de operaciones (solo local)
└── README.org                        # Página del proyecto (MERGE, no sobrescribir)
```

## Workflow

### 1. Verificaciones Pre-flight

```bash
# Verificaciones críticas (abortar si fallan)
- Permisos de escritura en directorio actual
- No hay merge/rebase en progreso
- No hay cambios staged en archivos de contexto (CLAUDE.md, etc.)

# Verificaciones de advertencia (loguear pero continuar)
- Working tree dirty → listar en Bloqueadores
- HEAD desacoplado → notar en resumen
- Sin remote configurado → notar en GIT_REMOTE
```

### 2. Resolver Nombre de PROYECTO

Orden de prioridad:
1. Archivo `.project` (si existe)
2. Marcadores padre: pyproject.toml > _quarto.yml > package.json > Cargo.toml > go.mod
3. Basename de git toplevel
4. Fallback: `unnamed-project-YYYYMMDD`

Sanitizar: reemplazar `/` y espacios con `-`
Persistir en `.project`

### 3. Escaneo de Seguridad

**ABORTAR si se detecta**:
- Patrones: `password|secret|api_key|token` con valores
- Archivos: `.env*`, `secrets.*`, `*.pem`, `id_rsa`

### 4. Actualizar .gitignore

Agregar si faltan:
```gitignore
docs/
working-outline.md
TODO.org
GIT_REMOTE
.project
handoff-trace.log
COMPACT.md
COMPACT-archive-*.md
```

### 5. Resumen de Sesión

**Archivo**: `docs/[PROYECTO]-session-summary.org`

**Template**:
```org
#+TITLE: [PROYECTO] — Historial de Sesiones
#+STARTUP: showall

# SESSIONS_START

* Sesión YYYY-MM-DD
:PROPERTIES:
:SESSION_DATE: YYYY-MM-DD
:SESSION_TIME: HH:MM
:TIMEZONE: [salida de date +%Z]
:PROJECT: [proyecto]
:BRANCH: [branch]
:END:

** Visión del Arquitecto (Delta desde la Última)

*Visión Central*: [¿Qué intenta lograr este proyecto?]

*Aprendizajes e Insights*:
- [Insight clave de ESTA sesión]

*Ajustes a Objetivos*:
- [Pivots o cambios de alcance]

** Esta Sesión

*Decisiones Estructurales*:
- [Decisiones arquitectónicas tomadas]

*Problemas Resueltos*:
1. [Problema] → [Solución]

*Decisiones Tomadas*:
- [Opción A vs B: elegí A porque...]

*Ideas Exploradas/Rechazadas*:
- [Idea]: [Por qué no funcionó]

** Checklist Próxima Sesión

- [ ] [Tarea de alta prioridad]
- [ ] [Investigación necesaria]

** Bloqueadores

[Bloqueadores o Ninguno]
```

**Lógica de inserción**: Prepend después del marcador `# SESSIONS_START`

### 5b. PROGRESS.md

Reescribir (no acumular) `PROGRESS.md` en la raíz, de 60 líneas como máximo: objetivo
actual, qué está hecho, qué falta, archivos tocados y comandos para verificar. Es lo
que el hook `SessionStart` (matcher `compact`) vuelve a inyectar tras compactar, y lo
que conviene leer al abrir una sesión nueva después de `/clear`.

### 6. CLAUDE.md

**NO escribir historial de sesión en CLAUDE.md.** El historial vive exclusivamente
en `docs/[PROYECTO]-session-summary.org`.

CLAUDE.md es para instrucciones del proyecto, notas de arquitectura y decisiones
clave solamente. Si el proyecto tiene CLAUDE.md, dejarlo sin cambios durante
el handoff. Si el proyecto no tiene uno, no crearlo — es decisión del usuario.

### 7. Metadata Git Remote

**Archivo**: `GIT_REMOTE`
```
REMOTE_URL=[url]
DEFAULT_BRANCH=[branch]
CURRENT_BRANCH=[branch]
LAST_COMMIT=[hash]
REPOSITORY_STATUS=[clean|dirty]
GIT_AVAILABLE=[true|false]
GENERATED_AT=[timestamp]
```

### 8. Compactación de Contexto

**Trigger**: CLAUDE.md > 160 KB

**Preservar** (nunca compactar):
- Overview del Proyecto
- Checklist de Fases
- Decisiones Clave (todas)
- Instrucciones de Trabajo
- Últimas 5 entradas de sesión

**Archivar a COMPACT.md**:
- Entradas de sesión más antiguas
- Logs detallados de problema/solución

### 9. Validación Post-flight

```bash
[ -f .project ]
[ -f "docs/${PROJECT_NAME}-session-summary.org" ]
```

## Output

### Mensaje de Commit Propuesto

```
chore(handoff): [PROYECTO] sesión YYYY-MM-DD

Decisiones:
- [Decisión clave]

Logros:
- [Qué se completó]

Siguiente: [Primera tarea]
```

### Resumen de Archivos

```
Handoff de Sesión Completo

CREADOS/ACTUALIZADOS:
  docs/[proyecto]-session-summary.org
  TODO.org
  GIT_REMOTE

SOLO LOCAL (en .gitignore):
  Todos los archivos de handoff excluidos de git

COMMIT OPCIONAL:
  git add .gitignore
  git commit -m "chore(handoff): ..."
```

## Recordatorio Crítico

**Este skill requiere contexto de conversación PRINCIPAL** para saber:
- Qué se logró esta sesión
- Qué decisiones se tomaron
- Qué problemas se resolvieron

NO ejecutar como subagente. Usar comando `/handoff`.
