# Tipografía

Destilado de `reports/investigacion-web-dashboards.md` §3.4. **Aviso de
cobertura:** el informe nombra una lista de fuentes y el método Utopia, pero
**no incluye pairings concretos, ni ejes variables por fuente, ni valores
numéricos de escala, ni verificación de licencia fuente por fuente**. Todo lo
marcado como *[derivado]* es criterio de esta skill, no dato verificado.

---

## Fuentes con carácter que el informe respalda

Única lista verificada (§3.4, "fuentes open source con carácter"):

| Fuente | Rol natural | Licencia |
|---|---|---|
| Bricolage Grotesque | display / titulares | no verificada en el informe |
| Fraunces | display serif / titulares | no verificada en el informe |
| Instrument Serif | display serif alto contraste | no verificada en el informe |
| Space Grotesk | display — **ver aviso** | no verificada en el informe |
| IBM Plex (familia) | body sans / serif / mono | no verificada en el informe |
| JetBrains Mono | mono / datos / código | no verificada en el informe |

**Licencias:** el informe cita `v-fonts.com/licenses/open-source` como fuente
general de fuentes variables libres, pero **no verifica la licencia de cada
familia**. Antes de empaquetar cualquiera en `assets/fonts/`, confirma la
licencia (se espera OFL) en el repositorio oficial de la fuente.

**Variabilidad:** el informe habla de "variable fonts" como categoría pero **no
documenta qué ejes expone cada familia**. Verifica los ejes reales
(`wght`, `opsz`, `SOFT`, `WONK`...) antes de escribir `font-variation-settings`.

### Aviso sobre Space Grotesk (contradicción real del informe)

Aparece en dos listas opuestas: como fuente "con carácter" (§3.4) y como huella
de slop en impeccable.style, además de ser la **segunda opción a la que Claude
re-converge** según el cookbook de Anthropic (§3.6). Resolución de esta skill
*[derivado]*: prohibida como elección automática; admisible solo si `DESIGN.md`
la justifica contra el sujeto del proyecto y no fue la primera idea.

---

## Fuentes PROHIBIDAS en titulares

- **Inter** — huella verificada (impeccable.style; typewolf.com/inter citado).
- **Geist** — huella verificada.
- **Space Grotesk** — huella verificada como segunda opción de los LLM.

*[derivado, sin respaldo en el informe]*: Roboto, Arial y `system-ui` tampoco
deberían aparecer en titulares, por falta de carácter — pero el informe no los
documenta como señal de IA. No los presentes como dato verificado.

En **body y UI densa** una sans neutra sigue siendo legítima; la prohibición
aplica a titulares y a la identidad de la pieza.

---

## Regla de pairing: display + body real

El informe exige "pairing display+body real": dos familias con función
distinta, no dos pesos de la misma. Mínimo operativo *[derivado]*:

1. **Display** (H1-H2): la que carga la personalidad. Cambio de eje óptico o de
   contraste respecto al body; se usa en tamaños grandes y poco texto.
2. **Body** (párrafos, UI): legibilidad a 16-18 px, familia distinta de la
   display.
3. **Mono** (cifras, código, ejes de gráfico): JetBrains Mono o IBM Plex Mono.
   Recomendable con `font-variant-numeric: tabular-nums` en tablas y KPIs.

Máximo **3 familias** por proyecto. Cada una declarada como token
(`--font-display`, `--font-body`, `--font-mono`), nunca como literal en un
componente (ver `tokens.md`).

### Cuándo serif / sans / mono *[derivado — el informe no da esta regla]*

- **Serif display** (Fraunces, Instrument Serif): piezas editoriales, ensayos
  de datos, longform, cualquier cosa anclada en prensa (FT / The Pudding / NYT).
- **Sans display** (Bricolage Grotesque): producto, dashboards, landings
  técnicas; también cuando hay mucha UI y poco texto corrido.
- **Sans body** (IBM Plex Sans): defecto seguro para cuerpo y UI.
- **Serif body**: solo con medida de línea controlada (60-75 caracteres) y
  bloques de texto largos; mala idea en celdas de tabla.
- **Mono**: cifras alineadas, ejes, tooltips, etiquetas de datos, timestamps.
  Nunca para párrafos.

---

## Escala fluida con clamp() (método Utopia)

El informe recomienda "escala fluida tipo Utopia con `clamp()`" y cita
`utopia.fyi`, pero **no incluye la tabla de valores**. Genera los valores en
utopia.fyi con estos parámetros y pégalos en `tokens.css`; no los inventes.

Parámetros a fijar en `DESIGN.md` antes de generar:

- Viewport mínimo y máximo (p. ej. 320 y 1240 px).
- Tamaño base en cada extremo (p. ej. 16 y 18 px).
- **Razón de escala >= 1,25x** en ambos extremos (umbral vibecodekit del
  informe; ver `anti-slop.md`).
- Número de pasos hacia arriba (5-6) y hacia abajo (1-2).

Forma del token resultante:

```css
/* valores de ejemplo: sustituir por la salida real de utopia.fyi */
--step-0: clamp(1rem, 0.91rem + 0.43vw, 1.13rem);
--step-3: clamp(1.95rem, 1.51rem + 2.2vw, 3.05rem);
```

*[derivado]* La interpolación de `clamp()` es `clamp(min, preferido, max)` donde
el término preferido combina `rem` (pendiente cero, respeta el zoom) y `vw`.
Nunca uses `vw` puro como término preferido: rompe el zoom del navegador.

Aplica el mismo método a espaciado, para que tipografía y rejilla de 8 px
escalen juntas.

---

## Checklist de titulares

- [ ] Ninguna de las 3 fuentes prohibidas en `--font-display`.
- [ ] Display y body son familias **distintas**, no dos pesos.
- [ ] <= 3 familias en todo el proyecto, todas como token.
- [ ] Fuentes empaquetadas en `assets/fonts/` (el informe lo exige para no
      depender del sistema ni de los defaults) con licencia verificada.
- [ ] Escala generada con Utopia, razón >= 1,25x, sin `vw` puro.
- [ ] `tabular-nums` activo en tablas, KPIs y ejes.
