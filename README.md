# claude-code-config

Mi configuración de **Claude Code**, empaquetada como **marketplace de plugins**
(`jorge-skills`) más unos dotfiles personales (settings, CLAUDE.md global, hooks y
statusline) que instala `install.sh`.

> ⚠️ Repo **curado**: NO contiene credenciales, historial, transcripts ni datos privados.
> Un hook `pre-commit` + `scripts/scan-secrets.py` bloquean cualquier secreto antes de subirlo.

## Instalar

```bash
git clone https://github.com/JAPerezC/claude-code-config.git
cd claude-code-config
bash install.sh --dry-run   # ver qué cambiaría
bash install.sh             # instalar (respalda lo existente)
git config core.hooksPath .githooks   # solo si vas a contribuir: activa el escáner
```

`install.sh` copia los dotfiles a `~/.claude`, **fusiona** `dotfiles/settings.template.json`
con tu `settings.json` (lo local gana; hooks y reglas `deny` se suman), registra el
marketplace e instala los plugins. Requiere `jq`, `python3` y `claude`.
Con `--local` registra el marketplace desde la carpeta clonada (para probar cambios sin push).

Solo los plugins, sin dotfiles:

```bash
claude plugin marketplace add JAPerezC/claude-code-config
claude plugin install datos@jorge-skills
```

## Estructura

```
.claude-plugin/marketplace.json   marketplace "jorge-skills"
plugins/
  sesion/     /session-start, /handoff (PROGRESS.md + resumen de sesión)
  datos/      explore-data, data-analysis, statistical-analysis, sql-analysis, cv-project
              + agentes data-validator, pipeline-runner, test-runner
  academico/  academic-doc, citas, doc-coauthoring, marp-deck + agente investigador
  diseno/     estudio-web, slides-html, canvas-design, theme-factory
  dev/        /git-pr, /init-proyecto (+ templates/), mcp-builder + agente code-reviewer
  scraper/    scraping ético con script fijo y tests
dotfiles/
  settings.template.json   eficiencia, permisos, hooks y statusline
  CLAUDE.md                instrucciones globales (corto a propósito)
  statusline.py            modelo · contexto · margen hasta compactar · git · límites del plan
  convos.py                listar/archivar conversaciones
  hooks/                   security-gate, auto-format, reinject-context, stop-verify (opcional)
skills-archive/            skills fuera de rotación (no se instalan)
scripts/scan-secrets.py    escáner de secretos (pre-commit y CI)
tests/                     pytest de hooks y escáner
```

Las skills de Office (docx, pdf, pptx, xlsx) y skill-creator **ya no se incluyen**: llegan
sincronizadas desde claude.ai y duplicarlas ocupa contexto en cada sesión.

## Qué configura `settings.template.json` y por qué

| Ajuste | Valor | Motivo |
|---|---|---|
| `autoCompactWindow` | 300 000 | Con 1M de contexto la autocompactación llega a ~967K; la calidad cae mucho antes (*context rot*). |
| `BASH_MAX_OUTPUT_LENGTH` | 15 000 | Salidas largas de comandos llenan el contexto sin aportar. |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | 15 000 | Obliga a leer archivos grandes por partes. |
| `permissions.deny` | `.env`, `*.pem`, `*.key` | Secretos fuera del alcance de Read. |
| `statusLine` | `statusline.py` | Contexto usado, tokens hasta compactar y uso del plan (5 h / 7 d). |
| `extraKnownMarketplaces` | jorge-skills | El marketplace queda declarado en cualquier máquina. |

No fija `effortLevel`: el valor por defecto de Opus 5.5 es `medium`; súbelo por sesión con
`/effort` o por skill/agente con `effort:` en el frontmatter (estudio-web y slides-html usan `high`).

## Hooks

| Evento | Script | Qué hace |
|---|---|---|
| PreToolUse (Bash, Read, Edit, Write) | `security-gate.py` | **deny** para lo destructivo (`rm -rf /`, `curl \| sh`, `mkfs`) y lectura de secretos; **ask** para `sudo`, push forzado (incl. `--force-with-lease` y `+ref`), `reset --hard`, `rm -rf`. |
| PostToolUse (Edit, Write) | `auto-format.py` | `ruff format` + `ruff check --fix` (sin borrar imports) y avisa a Claude si cambió el archivo. |
| SessionStart (`compact`) | `reinject-context.sh` | Tras compactar, reinyecta `PROGRESS.md`, la rama, los últimos commits y los archivos con cambios. |
| Stop (opcional, por proyecto) | `stop-verify.sh` | No deja terminar si hay cambios y los tests fallan; respeta `stop_hook_active`. |

## Contra el *context rot*

1. `autoCompactWindow` bajo + `# Compact instructions` en el CLAUDE.md global.
2. `PROGRESS.md` que se actualiza al cerrar cada hito (lo pide el CLAUDE.md y `/handoff`)
   y que el hook `compact` vuelve a inyectar.
3. `/clear` al cambiar de tarea o tras dos correcciones fallidas; `/session-start` para retomar.
4. Subagentes (`investigador`, `data-validator`…) para explorar y devolver solo un resumen.
5. Medir: `/context`, `/usage`, `/skill-doctor` y `claude plugin details <plugin>`.

## Plugins externos recomendados

`install.sh` instala a nivel usuario **context7** (documentación actualizada) y
**pyright-lsp** (tipos y "go to definition"; necesita `uv tool install pyright`).
Por proyecto, según el caso: `playwright` (mejor la CLI `npx playwright`), `firecrawl`,
`frontend-design` o Impeccable para diseño (elige uno principal), `superpowers` solo para
features grandes. Revisa su coste con `claude plugin details` antes de dejarlos activos.

`manim-skill` (awesome-skills/manim-skill, MIT) se instala aparte, fijada por commit:
`INSTALL_MANIM=1 bash install.sh`.

## Patrones de diseño de skills

Lecciones aplicadas en `estudio-web` y `slides-html`:

- **Lo computable se ejecuta como script; lo creativo lo decide el modelo** con los
  defaults prohibidos nombrados explícitamente (lista negra anti-slop verificable, incluido
  el "nuevo slop" de 2026: crema+terracota, verde ácido sobre casi-negro, kit de tarjetas SaaS).
- **El gusto vive en artefactos curados** (design systems como datos), no en la improvisación.
- **Previews reales antes de generar** ("mostrar, no preguntar") y un `DESIGN.md`
  aprobado por el humano antes de codificar.
- **Validadores binarios** (contraste WCAG AA, daltonismo) y **bucle de capturas** con
  Playwright en escritorio y móvil antes de entregar.
- **Marcas institucionales como brand packs intercambiables**, excluidas del repo público.

## Seguridad

- **`.gitignore` blindado** y **escáner de secretos** (`python3 scripts/scan-secrets.py`),
  que revisa el contenido en *staging*, no la copia de trabajo.
- CI (`.github/workflows/ci.yml`): tests, escáner y validación de JSON.
- Las skills con scripts **ejecutan código**, y los plugins pueden traer hooks: revísalos
  antes de instalarlos y fija por commit los de terceros.

## Licencia

MIT (cada skill de terceros conserva la suya; el motor de `slides-html` proviene de
[frontend-slides](https://github.com/zarazhangrui/frontend-slides), MIT, ver
`plugins/diseno/skills/slides-html/ATTRIBUTION.md`).
