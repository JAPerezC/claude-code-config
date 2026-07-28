# Librerías de visualización: mapa por caso de uso

Destilado de `reports/investigacion-web-dashboards.md` §3.3 (y §2, §4).
Versiones, licencias y tamaños verificados contra fuentes primarias el
28-jul-2026. Tamaños min+gzip según Bundlephobia, kB decimales.

**Nota previa:** esta guía elige la **librería**. La forma del gráfico y el
color se deciden aparte (ver `direcciones-esteticas.md` y `tokens.md`, y el
`visual-vocabulary` del FT como catálogo de formas).

---

## Decisión rápida

| Necesidad | Librería |
|---|---|
| Gráfico a medida, pieza editorial, Svelte | **LayerCake 10 / LayerChart 2 + D3 7** |
| Dashboard denso, muchas series, tematizable | **ECharts 6** |
| Prototipo desde Python / puente Altair | **Vega-Lite 6 (Altair 6.x)** |
| Geoespacial masivo, GPU | **deck.gl 9.3** |
| Exploración rápida, EDA | **Observable Plot** |
| Gráficos a medida en React | visx 4 |
| — | **Nunca Recharts** |

---

## LayerCake / LayerChart + D3 — a medida, Svelte

- **Cuándo:** cuando el gráfico es la pieza y debe verse como de nadie más:
  scrollytelling, portadas, formas no estándar. Es la vía natural al sistema de
  diseño propio porque **no imponen estética**.
- **D3 7.9.0** (ISC): sin releases desde mar-2024 — el informe lo lee como
  **feature-complete**, con 15,4-16,6 M de descargas semanales. Snyk lo marca
  "Sustainable" aunque añade que "podría considerarse un proyecto
  descontinuado". **92 kB** min+gzip (importar solo los submódulos usados).
- **LayerCake 10** (MIT, Svelte 5): headless, resuelve escalas y layout, no
  dibuja estética. **LayerChart 2** es la capa de componentes sobre esa idea.
- **Esfuerzo de theming:** ninguno, porque no hay tema que quitar — el coste
  está en construir cada marca desde cero.
- **Rendimiento:** SVG por defecto (cómodo para leer/animar/estilar con CSS);
  para volúmenes altos hay que pasar a canvas a mano. El informe **no da un
  umbral numérico de puntos para D3/LayerCake**.
- **Alternativa React:** **visx 4.0.0** (MIT, React 18/19), unstyled por diseño;
  mantenimiento real pero lento, **riesgo medio**.

## ECharts 6 — dashboards densos tematizables

- **Cuándo:** dashboards con muchas series, interacción de serie y necesidad de
  cambiar de tema en vivo. El informe lo señala como **el único con design
  tokens de serie y cambio claro/oscuro sin reinicializar**.
- **ECharts 6.1.0** (Apache-2.0). Trae de serie **brush, dataZoom y visualMap**
  (selección, zoom, escalas visuales) sin implementarlos a mano.
- **Estética por defecto:** rehicieron el tema por defecto con design tokens
  precisamente porque **>70 % de los usuarios no lo cambiaba**. Ese default es
  hoy una huella: cámbialo siempre por los tokens del proyecto.
- **Esfuerzo de theming:** bajo — es su punto fuerte.
- **Rendimiento:** **Canvas**, apto para datos masivos (millones de puntos).
- **Bundle: 368 kB** min+gzip, pero **tree-shakeable**: importa solo las series
  y componentes usados.

## Vega-Lite / Altair — prototipos desde Python

- **Cuándo:** el análisis ya existe en Python y quieres publicarlo rápido, o
  necesitas **crossfilter y overview+detail declarativos** sin escribir lógica
  de interacción.
- **Vega-Lite 6.4.3** (BSD-3), **puente 1:1 desde Python vía Altair 6.x**.
- **Rendimiento:** el informe la describe como **cómoda por debajo de ~100k
  puntos**. Por encima, cambia de librería.
- **Bundle: 87 kB** min+gzip **más el runtime de Vega aparte** (no incluido en
  esa cifra).
- **Estética por defecto:** el informe **no la evalúa**. Trátala como
  prototipo: para la pieza final, o la tematizas a fondo o migras.

## deck.gl — geoespacial masivo

- **Cuándo:** millones de entidades sobre mapa; es **la referencia GPU
  geoespacial**. `DataFilterExtension` da crossfilter masivo.
- **deck.gl 9.3.7** (MIT). **@deck.gl/core: 177,8 kB** min+gzip.
- **WebGPU:** su propia guía (commits del 27-28 jul-2026) declara que **no está
  listo para producción** y que las extensiones siguen siendo **WebGL-only**,
  aunque hay porting activo de capas. Planifica sobre WebGL.

## Observable Plot — exploración rápida

- **Cuándo:** EDA, iteración rápida, gráficos correctos con muy poco código
  ("máxima concisión").
- **Observable Plot 0.6.17** (ISC). **128 kB** min+gzip.
- **Theming:** su CSS tiene **especificidad 0**, así que se sobrescribe con
  facilidad desde los tokens del proyecto. Esfuerzo bajo.
- **Riesgo:** **~17 meses sin release**. El informe es explícito: "sin plan B no
  es apuesta a largo plazo". Úsala para explorar, no como cimiento.

---

## Evitar

- **Recharts 3.10.1** (MIT, muy activo): es el **motor de los charts de
  shadcn/ui** ("We use Recharts under the hood" en su documentación oficial) y
  el **epicentro del look genérico**. 147,5 kB. Nota: el sitio `shadcn.io` con
  53 componentes **es de terceros**, no oficial.
- **Plotly.js 3.7.0** (MIT): potente en científico y 3D, pero **1,4 MB gzip** el
  bundle completo (366,4 kB el `basic`) y **estética muy reconocible**. Solo si
  necesitas específicamente su catálogo científico/3D.

---

## Tamaños min+gzip (referencia rápida)

| Paquete | kB |
|---|---|
| vega-lite | 87 (+ runtime Vega aparte) |
| d3 | 92 |
| Observable Plot | 128 |
| Recharts | 147,5 |
| @deck.gl/core | 177,8 |
| ECharts | 368 (tree-shakeable) |
| plotly.js completo | 1.400 (basic: 366,4) |

---

## Combinación recomendada por el informe

D3/LayerCake + Svelte + Scrollama para piezas distintivas; ECharts 6 para
dashboards tematizables; Vega-Lite como puente Altair/Python; deck.gl para lo
masivo. Todo publicado como **islas Astro** (`client:visible`) o como
componentes SvelteKit — una isla de Astro es un componente Svelte.

Datos: **build-time con Python** (pandas/DuckDB genera Parquet/JSON) +
**interactividad en cliente** (DuckDB-WASM) + **deploy estático**. Es el patrón
ganador del informe para este perfil.

## Huecos declarados

- El informe **no da umbrales de puntos** para SVG vs canvas en D3/LayerCake
  (solo el ~100k de Vega-Lite y "millones" para ECharts Canvas y deck.gl GPU).
- **No evalúa la estética por defecto** de Vega-Lite, LayerChart ni visx.
- **No documenta accesibilidad** (roles ARIA, navegación por teclado, tablas
  alternativas) de ninguna de estas librerías: verifícalo por pieza con el gate
  de axe-core.
- El skill `dataviz` incluido con Claude Code (2.1.220) es la referencia
  metodológica para color y forma, pero **no tiene URL pública** (inspección
  local).
