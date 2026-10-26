# Contrato de design tokens

Destilado de `reports/investigacion-web-dashboards.md` §3.1, §3.4 y §5.
**Aviso de cobertura:** el informe no incluye ejemplos de código de `@theme`,
ni el listado completo del set semántico de shadcn, ni el número exacto de
`--chart-*`, ni un esquema DTCG concreto. Los snippets de abajo están marcados
*[derivado]* y deben verificarse contra la documentación oficial antes de
fijarlos en un scaffold.

---

## Los cinco principios (no negociables)

1. **Los tokens se generan PRIMERO**, antes de escribir una línea de UI. El
   informe lo clasifica como artefacto determinista nº 1 de la skill.
2. **Nunca hex sueltos**: ni en el código, ni en los prompts. Todo color se
   referencia por token. Es la regla que hace verificable el anti-slop.
3. **Tokens semánticos, no literales.** `--color-surface`, no `--gris-100`;
   `--color-accent`, no `--violeta`. El nombre describe la función, así el
   cambio de tema no rompe el significado.
4. **Variantes clara y oscura obligatorias**, ambas validadas. No es opcional
   ni un extra al final.
5. **La paleta se valida con script antes de la UI** (`validate_palette.py`:
   CVD, contraste, modo oscuro). Doctrina del skill dataviz que el informe cita:
   *"the color part is computable, so compute it"*.

Tamaño del contrato: la guía de estilo debe caber en **<5.000 tokens de
contexto** (dato del informe, Developers Digest) y referenciarse desde
`CLAUDE.md`, con las dos variantes incluidas.

---

## Set semántico base

El informe documenta el contrato de tokens de Tailwind 4 + shadcn como "la base
natural del sistema de diseño pedido", citando estos nombres:

- `--background`
- `--primary`
- `--chart-*` (serie de colores de gráfico)
- `.dark` como selector de la variante oscura

**Hueco declarado:** el informe **no enumera el resto del set** (foreground,
muted, border, ring, destructive...) ni **cuántos `--chart-*` hay**. Consulta
`ui.shadcn.com/docs/theming` antes de fijar la lista; no la inventes.

Advertencia del propio informe: shadcn "usado sin personalizar produce
exactamente el look genérico que se quiere evitar". El contrato de nombres se
adopta; los **valores** se sustituyen íntegros.

---

## Expresión en Tailwind 4 (`@theme`)

Tailwind CSS **4.3.3** (MIT, 16-jul-2026) es configuración **CSS-first**: el
bloque `@theme` es el almacén nativo de design tokens (colores OKLCH, fuentes,
radios, sombras) y genera custom properties de CSS más las utilidades
correspondientes. Ya no hay `tailwind.config.js` como fuente de verdad.

*[derivado — verificar sintaxis en tailwindcss.com/blog/tailwindcss-v4]*:

```css
/* tokens.css — única fuente de verdad de color en el proyecto */
@import "tailwindcss";

@theme {
  --color-surface:  oklch(98% 0.005 95);
  --color-ink:      oklch(22% 0.02 95);
  --color-accent:   oklch(62% 0.16 35);
  --color-chart-1:  oklch(58% 0.14 250);

  --font-display: "Fraunces", serif;
  --font-body:    "IBM Plex Sans", sans-serif;
  --font-mono:    "JetBrains Mono", monospace;

  --radius-card: 0.25rem;
}
```

**Color en OKLCH**, no hex ni HSL: es lo que el informe documenta como práctica
de Tailwind 4 y de DTCG 2025.10 (P3/OKLCH), y lo que permite variar luminosidad
sin desplazar el tono percibido.

### Variante oscura

El informe exige ambas variantes y usa `.dark` como selector del contrato
shadcn. Redefine los **mismos nombres semánticos** en el bloque oscuro; nunca
introduzcas tokens nuevos solo para oscuro (rompe el significado).

Dato relevante para gráficos: **ECharts 6 cambia de tema sin reinicializar** el
gráfico — es el único de su categoría que lo hace con claridad según el informe.
Por eso los `--color-chart-*` deben existir en las dos variantes desde el
principio, no añadirse después.

---

## Cuándo escalar a DTCG + Style Dictionary

Criterio literal del informe: **"Para un solo stack web basta `@theme`; DTCG +
Style Dictionary cuando el tema deba compilarse a varios destinos (web +
matplotlib/plotly + PDF)"**.

Es decir: si el tema **sale de la web**, escala. Si no, no añadas la capa.

| Situación | Herramienta |
|---|---|
| Solo web (Astro / SvelteKit) | `@theme` en `tokens.css` |
| Web + matplotlib/plotly + PDF | DTCG 2025.10 + Style Dictionary v5 |
| Igual, con cadena más ligera | Terrazzo (MIT, ex-Cobalt), DTCG-first |

Datos verificados del informe:

- **DTCG 2025.10** (28-oct-2025) es la primera versión estable de la
  especificación. **No es un estándar W3C formal**: es un Final Community Group
  Report bajo el W3C Community Final Specification Agreement. Theming vía el
  módulo **Resolver**; colores P3/OKLCH.
- **Style Dictionary v5** (Apache-2.0, última v5.5.0 del 21-jun-2026) soporta
  DTCG: transforms `color/oklch`, `oklab`, `p3` y `lch` desde **v5.3.0**
  (feb-2026); dimensión DTCG desde **v5.4.0** (mar-2026).
- El `the-pudding/svelte-starter` incluye Style Dictionary ^5.4.1 — señal de que
  el patrón es real en redacciones.

**Hueco declarado:** el informe no incluye un ejemplo de archivo DTCG ni de
config de Style Dictionary. Consulta `designtokens.org/tr/2025.10/format/` y
`styledictionary.com/versions/v5/` al implementar `make_tokens.py`.

---

## Flujo dentro de la skill

1. `DESIGN.md` aprobado por el humano (color, tipo, layout, elemento único).
2. `make_tokens.py`: `DESIGN.md` -> `tokens.css` + `tokens.json`.
3. `validate_palette.py`: CVD + contraste + modo oscuro. Resultado **binario**;
   si falla, no se escribe UI.
4. La UI consume tokens. `check_slop.mjs` bloquea hex sueltos fuera de
   `tokens.css` y fuentes prohibidas.

## Checklist

- [ ] `tokens.css` es el único archivo con valores de color del repositorio.
- [ ] Todos los nombres son semánticos (función), ninguno literal (color).
- [ ] Claro y oscuro definen el **mismo** conjunto de nombres.
- [ ] `--color-chart-*` existen en ambas variantes.
- [ ] Paleta validada antes de la primera pantalla.
- [ ] La guía cabe en <5.000 tokens y está enlazada desde `CLAUDE.md`.
