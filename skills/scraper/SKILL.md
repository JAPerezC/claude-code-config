---
name: scraper
description: Web scraping ético y robusto con Python (requests, BeautifulSoup, trafilatura, ScraperAPI). Úsala cuando el usuario quiera extraer o 'scrapear' contenido de una o varias URLs o páginas web; por ejemplo, descargar el texto de artículos o noticias, recolectar datos estructurados (precios, tablas, enlaces), procesar un sitemap, o inspeccionar y diagnosticar una página antes de extraer. Trae scripts/scrape.py (retry, robots.txt, identificación de contenido, JSONL).
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch
---

Eres un experto en web scraping etico y robusto con Python.

## Regla principal: usa el script incluido, no reescribas la logica

Esta skill incluye `scripts/scrape.py`, que YA implementa retry con backoff, respeto de
`Retry-After` y de robots.txt, descubrimiento por sitemap, guardado incremental, reanudacion
y proxy opcional. **Prefierelo siempre** en vez de escribir scraping a mano. Solo escribe
codigo nuevo si el caso no encaja (p.ej. scraping asincrono masivo, ver REFERENCE.md).

Ejecutar (la ruta de la skill esta en `${CLAUDE_SKILL_DIR}`):

```bash
# Articulo / noticia: extrae texto + metadatos con trafilatura
python "${CLAUDE_SKILL_DIR}/scripts/scrape.py" --url https://ejemplo.com/articulo --mode article --out data/processed/out.jsonl

# Lote desde archivo (una URL por linea), reanudable
python "${CLAUDE_SKILL_DIR}/scripts/scrape.py" --urls-file urls.txt --mode article --out data/processed/noticias.jsonl

# Descubrir URLs por sitemap
python "${CLAUDE_SKILL_DIR}/scripts/scrape.py" --sitemap https://ejemplo.com/sitemap.xml --mode article --out data/processed/site.jsonl

# Datos estructurados con selector CSS (modo soup)
python "${CLAUDE_SKILL_DIR}/scripts/scrape.py" --urls-file urls.txt --mode soup --selector "h1, .precio" --out data/processed/precios.jsonl

# Sitios que bloquean: proxy ScraperAPI (requiere SCRAPERAPI_KEY en .env) y render JS
python "${CLAUDE_SKILL_DIR}/scripts/scrape.py" --url https://ejemplo.com --proxy --render --out data/processed/out.jsonl
```

Salida: JSONL (un objeto por linea), apto para `pandas.read_json(path, lines=True)`.
Flags clave: `--timeout` (30s), `--retries` (5), `--backoff` (2.0), `--delay`/`--jitter`
(cortesia), `--user-agent`, `--contact` (header From), `--insecure`, `--ignore-robots`,
`--allow-non-html`, `--inspect`, `--detect-api`, `--skip-failed`, `--no-resume`, `--log-every`.

Antes del primer uso: instalar dependencias en venv -> `pip install -r "${CLAUDE_SKILL_DIR}/requirements.txt"`.

## Documentacion de la skill

- `README.md` — portada para compartir (caracteristicas, instalacion, CLI, salida).
- `REFERENCE.md` — recetas (Google News RSS, paginacion, sitemap, async httpx, JSONL->CSV/Parquet, selectores) y solucion de problemas.
- `tests/test_scrape.py` — tests offline (`pytest tests/ -q`).

## Cuando elegir cada modo

- `--mode article` (trafilatura): quieres el TEXTO de un articulo/noticia/blog limpio
  (sin menus ni anuncios) + metadatos (titulo, autor, fecha). Ideal para corpus/NLP.
- `--mode soup` (BeautifulSoup + selector CSS): quieres datos ESTRUCTURADOS concretos
  (precios, atributos, campos de tabla). Requiere conocer el selector del sitio.

## Identificación de contenido

Antes de extraer, el script identifica el tipo de recurso (Content-Type + extensión + primeros bytes):
- **HTML** -> se extrae normal.
- **PDF** -> se omite con `ok:false` y la pista de usar la skill `pdf` (es el tool correcto para PDFs).
- **JSON / imagen / otro** -> se omite con aviso (usa `--allow-non-html` para procesarlo igual).

Además avisa si una página tiene muy poca textualidad (posible contenido renderizado por JS -> prueba `--proxy --render`).

Para una **revisión previa** sin extraer, usa `--inspect`: devuelve un perfil con el tipo de página, si `robots.txt` lo permite, la estructura (h1/h2/enlaces/tablas/texto) y un diagnóstico con el modo recomendado.

Y con `--detect-api` descubres los **endpoints de API** que usa la página (clave en apps JS/SPA): rastrea el JSON embebido y los bundles JS en busca de URLs tipo `/api/`, `.json` o `graphql`. Útil para saltar el render y pedir los datos directo a la API.

## Stack y herramientas (que se usa exactamente)

- Herramientas de Claude Code permitidas: las del frontmatter `allowed-tools` (no usa otras).
- Librerias Python: las fijadas en `requirements.txt` e importadas por `scripts/scrape.py`
  (`requests`, `urllib3`, `beautifulsoup4`+`lxml`, `trafilatura`, `python-dotenv` opcional).
  robots.txt y sitemap usan la libreria estandar. No improvises otras librerias.
- `httpx` solo si se necesita scraping asincrono masivo (ver REFERENCE.md).
- Google News RSS como fuente de busqueda de noticias.

## Reglas

- SIEMPRE timeout explicito (default 30s) y retry con backoff exponencial (429, 500, 502, 503, 504).
- Respetar `Retry-After` y robots.txt (ambos por defecto; el script ya lo hace).
- Logs de progreso cada N requests; guardar resultados incrementalmente (no perder progreso en crashes).
- `encoding="utf-8"` en toda lectura/escritura; rutas con `pathlib`.
- API keys y tokens SOLO via `os.getenv()` / `.env` (python-dotenv). NUNCA hardcodear.
- `data/raw/` y `triage/` son SOLO LECTURA: escribir salidas en `data/processed/` o `reports/`.
- Si Google News da rate limit (~300 requests), esperar ~60 min.
- Scraping etico: respetar robots.txt y los terminos del sitio; usar `--delay` para no saturar.
