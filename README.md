# claude-code-config

Mi configuración de **Claude Code** (hooks, skills, comandos, agentes, scripts) para
reproducir mi setup en cualquier máquina.

> ⚠️ Repo **curado**: NO contiene credenciales, historial, transcripts ni datos privados.
> Un hook `pre-commit` + `scripts/scan-secrets.py` bloquean cualquier secreto antes de subirlo.

## Estructura

```
~/.claude/                     (este repo se instala aquí con install.sh)
- hooks/          seguridad y formato automático (PreToolUse / PostToolUse)
- commands/       slash commands de flujo de sesión
- agents/         subagentes especializados
- skills/         25 skills activas (catálogo abajo)
- skills-archive/ 24 skills archivadas fuera de rotación
- scripts/        utilidades (convos.py, scan-secrets.py)
- templates/      plantillas de proyecto (gitignore, pre-commit, licencias)
- statusline.py   statusline personalizada
```

Se **excluyen a propósito** por privacidad: `settings.json`, el `CLAUDE.md` global,
`memory/`, y los **brand packs institucionales** de las skills de diseño
(logos y sistemas de marca reales — cada carpeta `brands/` documenta el formato
para que construyas los tuyos).

## Hooks

| Evento | Script | Qué hace |
|---|---|---|
| PreToolUse | `hooks/security-gate.py` | Bloquea comandos destructivos (`rm -rf`, `chmod 777`, push forzado, lectura de `.env`/llaves) |
| PostToolUse | `hooks/auto-format.py` | Formatea con `ruff` cada `.py` editado |

En `settings.json` (no publicado) se registran además: banner de inicio de sesión,
hora local en cada prompt, recordatorio post-compactación y beep al terminar.

## Comandos de sesión

| Comando | Qué hace |
|---|---|
| `/session-start` | Inicia sesión: archiva conversaciones, carga historial/TODO, propone enfoque |
| `/session-summary` | Genera el resumen de la sesión en curso (solo texto, no persiste) |
| `/handoff` | Cierra sesión: snapshot completo + resumen persistido en `docs/*.org` |

## Agentes

| Agente | Rol |
|---|---|
| `code-reviewer` | Revisa código Python (calidad, seguridad, bugs) sin modificar archivos |
| `data-validator` | Valida datasets: schemas, tipos, nulos, duplicados, anomalías |
| `investigador` | Investiga temas técnicos en web/documentación y devuelve resumen con fuentes |
| `pipeline-runner` | Ejecuta pipelines de datos multi-paso con manejo de errores |
| `test-runner` | Corre pytest, analiza fallos y escribe tests nuevos |

## Catálogo de skills (25 activas)

### Diseño web y presentaciones

| Skill | Qué hace |
|---|---|
| `estudio-web` | Páginas y dashboards NO genéricos: Astro 7 + Tailwind 4 / SvelteKit 2, sistema de tokens por proyecto, validadores de paleta (WCAG+CVD) y lint anti-slop, scaffolds y brand packs |
| `slides-html` | Presentaciones HTML animadas autocontenidas (motor de frontend-slides, MIT) con modo institucional por brand pack y modo personal con estilos curados |
| `marp-deck` | Decks rápidos Markdown→PDF/PPTX con Marp |
| `canvas-design` | Arte visual en PNG/PDF con filosofía de diseño |
| `theme-factory` | Temas (colores/fuentes) aplicables a cualquier artefacto |
| `manim-skill` | Animaciones matemáticas/técnicas con ManimCE |

### Datos y análisis

| Skill | Qué hace |
|---|---|
| `data-analysis` | Análisis con pandas + validación de schema (CSV/Parquet/Excel), econometría |
| `explore-data` | EDA rápido: schema, nulos, estadísticas, correlaciones, limpieza |
| `statistical-analysis` | Selección de tests, supuestos, potencia, resultados APA |
| `sql-analysis` | DDL/DML/queries y migraciones (PostgreSQL, SQLite, DuckDB) |
| `scraper` | Scraping ético y robusto (retry, robots.txt, sitemap, JSONL) con script fijo y tests |
| `cv-project` | Computer vision deportiva: YOLO, OpenCV, supervision, ByteTrack |

### Documentos académicos y ofimática

| Skill | Qué hace |
|---|---|
| `academic-doc` | Documentos académicos (DOCX/PDF) con Pandoc y formato APA |
| `citas` | Búsqueda de papers, BibTeX validado, formato APA |
| `docx` / `pdf` / `pptx` / `xlsx` | Manipulación completa de Office/PDF (skills de Anthropic) |
| `doc-coauthoring` | Flujo estructurado de co-escritura de documentación |

### Flujo de trabajo

| Skill | Qué hace |
|---|---|
| `git-pr` | PR completo: conventional commit, push y descripción (slash command) |
| `init-proyecto` | Estructura estándar de proyecto nuevo (slash command) |
| `session-closer` | Cierre de sesión con snapshot (se invoca vía `/handoff`) |
| `debug` | Diagnóstico sistemático: reproducir, causa raíz, fix |
| `skill-creator` | Crear, mejorar y evaluar skills |
| `mcp-builder` | Construir servidores MCP de calidad (Python/TypeScript) |

## Patrones de diseño de skills

Lecciones aplicadas en `estudio-web` y `slides-html` (ver sus SKILL.md):

- **Lo computable se ejecuta como script; lo creativo lo decide el modelo** con los
  defaults prohibidos nombrados explícitamente (lista negra anti-slop verificable).
- **El gusto vive en artefactos curados** (design systems como datos, dos niveles:
  ficha de preselección + sistema completo), no en la improvisación del modelo.
- **Previews reales antes de generar** ("mostrar, no preguntar") y un `DESIGN.md`
  aprobado por el humano antes de codificar.
- **Validadores binarios** antes de la UI: contraste WCAG AA + daltonismo computados,
  no estimados.
- **Marcas institucionales como brand packs intercambiables**, separadas del motor y
  excluidas del repo público.

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

MIT (ver cada skill de terceros para su propia licencia; los archivos del motor de
`slides-html` provienen de [frontend-slides](https://github.com/zarazhangrui/frontend-slides),
MIT, ver `skills/slides-html/ATTRIBUTION.md`).
