# Scaffold: dashboard con SvelteKit 2 + LayerChart/ECharts + DuckDB-WASM

Para tableros interactivos con filtros cruzados servidos como sitio estático.
Los datos los precalcula Python (`data_build.py`); el navegador filtra.

## Comandos

```bash
npx sv create <slug> --template minimal --no-add-ons --install npm
cd <slug>
npx sv add tailwindcss --install npm       # Tailwind 4
npm install layerchart layercake d3        # gráficas a medida
npm install echarts                        # solo si el tablero es denso
npm install @duckdb/duckdb-wasm@1.33.0     # solo si hay filtros sobre Parquet.
                                           # FIJAR versión exacta: el tag `latest`
                                           # de npm apunta a builds -dev (informe
                                           # §3.2). Binarios .wasm pesan 35-41 MB:
                                           # cargar con import dinámico tras el
                                           # primer render, nunca en el bundle.
npm install --save-dev @sveltejs/adapter-static
```

En `svelte.config.js`: `adapter-static` con `fallback: undefined` (SSG puro)
y `export const prerender = true` en `src/routes/+layout.js`.

## Conexión de tokens

Igual que astro-site: `make_tokens.py DESIGN.md src/` y en `src/app.css`:

```css
@import 'tailwindcss';
@import './tokens.css';
```

## Patrón de datos

1. `python <skill>/scripts/data_build.py datos.csv static/data/ --sql "..."`
2. Gráficas pequeñas: `fetch('/data/x.json')` en `+page.js` (load).
3. Filtros cruzados sobre datos grandes: DuckDB-WASM lee
   `/data/x.parquet` y las gráficas se derivan con runes
   (`$state` para filtros, `$derived` para los datos filtrados) — la
   reactividad de Svelte 5 hace el crossfiltering sin librería extra.

## Reglas de composición

- Serie de color de gráficas = tokens (`accent`, `accent-2` y derivados
  aprobados por `validate_palette.py`). Nunca la paleta default de ECharts.
- En ECharts, registrar un theme JSON construido desde tokens.json.
- KPIs, tablas y tarjetas consumen utilidades de tokens; layout con CSS grid.
- Estados: loading skeleton, vacío y error SIEMPRE diseñados.
- `prefers-reduced-motion`: sin transiciones de entrada en gráficas.

## Verificación y deploy

- `npm run build && npm run preview`; capturar desktop y móvil.
- GitHub Pages/Netlify/Vercel igual que astro-site (output `build/`).
  Confirmar con el usuario antes de publicar.
