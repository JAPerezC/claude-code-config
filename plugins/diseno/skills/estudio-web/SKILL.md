---
name: estudio-web
description: >
  Crear páginas web y dashboards NO genéricos con stack moderno: sitios con
  Astro 7 + Tailwind 4, dashboards y scrollytelling con SvelteKit 2 + LayerChart/
  ECharts + DuckDB-WASM. Sistema de tokens propio por proyecto, validadores de
  paleta/anti-slop, y modo institucional CCD/EGTP/Tec SOLO para proyectos
  institucionales. Triggers: "crear página web", "landing", "portfolio", "sitio
  web", "micrositio", "dashboard web", "tablero interactivo", "scrollytelling",
  "reporte web interactivo", "publicar en GitHub Pages/Vercel/Netlify".
when_to_use: Cuando el entregable es una página, sitio, dashboard o historia con scroll que debe verse distinta de una plantilla.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
effort: high
---

# Estudio Web — páginas y dashboards con identidad propia

Genera artefactos web con diseño distintivo y reproducible. El principio
rector (del informe `reports/investigacion-web-dashboards.md` del proyecto
CLAUDE): **lo computable se ejecuta como script; lo creativo lo decide el
modelo con los defaults prohibidos nombrados explícitamente**.

Todo el contenido va en español con ortografía correcta (acentos, ¿?, ¡!)
salvo que el usuario pida otro idioma.

## Fase 0: Dos decisiones antes de tocar código

**A. Marca.** ¿El proyecto es institucional (CCD/EGTP/Tec, contrapartes de trabajo)? → leer `brands/<marca>.md` y usar SU sistema cerrado.
**Todo lo demás — proyectos personales y privados — usa dirección de arte
propia por proyecto** (nunca aplicar la marca Tec por defecto; en caso de
duda, preguntar).

**B. Artefacto.** Elegir scaffold:
- **Página/sitio** (landing, portfolio, reporte, micrositio) → `scaffolds/astro-site.md`
- **Dashboard** (tablero interactivo con datos) → `scaffolds/sveltekit-dashboard.md`
- **Scrollytelling** (narrativa con scroll) → `scaffolds/scrolly-story.md`

Requisito: Node 20+ y npm (`node --version`). Si no están, avisar al usuario
y detenerse (los scaffolds no funcionan sin Node).

## Flujo de 7 pasos

### 1. Brief + DESIGN.md (modelo → revisión humana)

Preguntar juntas: propósito y audiencia, contenido disponible (¿datos? ¿en
qué formato?), y referencias que le gusten (si no hay, inferir del sujeto).

Escribir `DESIGN.md` en la raíz del proyecto — artefacto intermedio
OBLIGATORIO que el usuario aprueba ANTES de codificar:

```markdown
---
proyecto: <slug>
modo: personal | institucional
artefacto: pagina | dashboard | scrolly
colors:            # SEMÁNTICOS, con variante dark obligatoria
  bg: "#..."       # fondo
  surface: "#..."  # tarjetas/paneles
  text: "#..."
  text-muted: "#..."
  accent: "#..."
  accent-2: "#..."
  line: "#..."
  dark: { bg: "#...", surface: "#...", text: "#...", text-muted: "#...",
          accent: "#...", accent-2: "#...", line: "#..." }
fonts:
  display: "<nombre>"   # NUNCA Inter/Roboto/Arial/system-ui (ver anti-slop)
  body: "<nombre>"
  mono: "<nombre>"
  import: "<URL de Google Fonts/Fontshare>"
radius: "12px"
---
## Dirección de arte
<familia estética elegida y POR QUÉ ancla con el sujeto real — ver
references/direcciones-esteticas.md>
## Elemento distintivo
<el único rasgo memorable de esta pieza: un dispositivo gráfico, no un efecto>
## Defaults prohibidos en este proyecto
<lista explícita — copiar los aplicables de references/anti-slop.md>
```

Para elegir paleta/tipografía leer: `references/direcciones-esteticas.md`,
`references/tipografia.md`, `references/anti-slop.md`.

### 2. Tokens + validación (script, bloqueante)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/make_tokens.py" DESIGN.md src/styles/
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_palette.py" src/styles/tokens.json
```

`validate_palette.py` es binario: si falla el contraste (WCAG AA) o la
distinguibilidad CVD, corregir la paleta en DESIGN.md y regenerar. NO seguir
con una paleta reprobada. Contrato de tokens: `references/tokens.md`.

### 3. Scaffold (script)

Seguir la receta del scaffold elegido (comandos exactos + archivos). El
scaffold queda conectado a `tokens.css` desde el inicio: **jamás hex sueltos
fuera de tokens.css**.

### 4. Composición (modelo, consumiendo tokens)

Construir páginas/componentes usando SOLO tokens y las fuentes del DESIGN.md.
Jerarquía, layout y ritmo son decisión creativa — con `references/anti-slop.md`
como lista negra activa. Para gráficas, elegir librería según
`references/dataviz.md`; para scrolly, `references/scrollytelling.md`.

### 5. Datos (script, si aplica)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/data_build.py" <entrada> static/data/
```

Patrón: Python/pandas/DuckDB precalcula en build → Parquet/JSON estático →
el cliente filtra (DuckDB-WASM en dashboards). Nunca cómputo pesado en el
navegador que Python pueda dejar hecho.

### 6. Gates de calidad (script, bloqueante)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check_slop.py" <dir del proyecto>
```

Detecta: fuentes prohibidas, gradientes púrpura-cian, hex fuera de tokens,
easing bounce. Si hay Node y el proyecto lo amerita, correr también axe-core
(`npx @axe-core/cli`) como gate de accesibilidad WCAG 2.2 AA.

### 7. Preview visual (modelo)

Levantar el dev server (`npm run dev`) y capturar en escritorio (1440×900) y
móvil (390×844). Preferir la CLI de Playwright, que gasta menos contexto que el
MCP de navegador:

```bash
npx -y playwright screenshot --viewport-size=1440,900 --full-page http://localhost:4321 shot-desktop.png
npx -y playwright screenshot --viewport-size=390,844  --full-page http://localhost:4321 shot-mobile.png
```

Leer las capturas con Read y MIRARLAS: overflow, jerarquía, contraste real,
estados hover/focus. El validador cubre color, no layout. Criticar contra
`references/anti-slop.md` (incluida la sección 9), ajustar y recapturar hasta
que se vea intencional. Antes de entregar, quitar un elemento decorativo.

## Archivos de soporte

| Archivo | Cuándo |
|---|---|
| `brands/<marca>.md` | Fase 0 SOLO si el proyecto es institucional |
| `references/direcciones-esteticas.md` | Paso 1 (dirección de arte) |
| `references/tipografia.md` | Paso 1 |
| `references/anti-slop.md` | Pasos 1 y 4 (lista negra activa) |
| `references/tokens.md` | Paso 2 |
| `references/dataviz.md` | Paso 4 (elección de librería de gráficas) |
| `references/scrollytelling.md` | Paso 4 (solo scaffold scrolly) |
| `scaffolds/*.md` | Paso 3 (receta del artefacto elegido) |
| `scripts/*.py` | Pasos 2, 5 y 6 |

Deploy: cada scaffold documenta su ruta (GitHub Pages con Action oficial,
Vercel/Netlify por CLI o Git). Confirmar con el usuario antes de publicar a
un servicio externo.
