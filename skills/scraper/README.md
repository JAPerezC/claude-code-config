# Skill `scraper`

Web scraping ético y robusto con Python para Claude Code. No es solo una guía: incluye un
script de producción (`scripts/scrape.py`) con retry/backoff, respeto de robots.txt, guardado
incremental y reanudación, de modo que su comportamiento es **determinista y auditable**.

## Características

- Sesión HTTP con **retry + backoff exponencial** (429/500/502/503/504) y respeto de `Retry-After`.
- **Respeto de robots.txt** por host (desactivable con `--ignore-robots`).
- **Guardado incremental** en JSONL: si crashea, no pierdes lo ya hecho.
- **Reanudación** automática: salta las URLs ya extraídas con éxito y reintenta los fallos (`--skip-failed` para saltarlos).
- Dos modos: **`article`** (trafilatura: texto limpio + metadatos) y **`soup`** (selector CSS).
- **Identificación de contenido**: detecta HTML/PDF/JSON; omite lo no-HTML con aviso (sugiere la skill `pdf` para PDFs).
- **Self-identificación** ante el sitio con `--contact` (header `From`).
- Descubrimiento de URLs por **sitemap.xml**.
- **ScraperAPI** opcional como proxy (clave en `.env`, nunca hardcodeada) y render de JS.
- Cortesía configurable entre requests (`--delay` + `--jitter`) y logging de progreso.

## Estructura

```
scraper/
├── SKILL.md            # Manifiesto de la skill (lo que lee Claude)
├── README.md           # Este archivo
├── REFERENCE.md        # Recetas avanzadas y solución de problemas
├── requirements.txt    # Dependencias fijadas
├── scripts/
│   └── scrape.py       # Implementación reutilizable
└── tests/
    └── test_scrape.py  # Tests offline (no requieren red)
```

## Instalación

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows / Git Bash
pip install -r requirements.txt
```

## Uso rápido

```bash
# Texto limpio de un artículo
python scripts/scrape.py --url https://ejemplo.com/articulo --mode article --out data/processed/out.jsonl

# Lote reanudable desde archivo
python scripts/scrape.py --urls-file urls.txt --mode article --out data/processed/noticias.jsonl

# Descubrir por sitemap
python scripts/scrape.py --sitemap https://ejemplo.com/sitemap.xml --mode article --out data/processed/site.jsonl

# Datos estructurados con selector CSS
python scripts/scrape.py --urls-file urls.txt --mode soup --selector "h1, .precio"
```

## Salida

JSONL (un objeto por línea), listo para pandas:

```python
import pandas as pd
df = pd.read_json("data/processed/out.jsonl", lines=True)
```

## Opciones de la CLI

| Flag | Default | Para qué |
|---|---|---|
| `--url` / `--urls` / `--urls-file` / `--sitemap` | — | Fuente de URLs |
| `--mode article|soup` | `article` | trafilatura vs selector CSS |
| `--selector` | `body` | Selector CSS (modo soup) |
| `--out` | `scrape_output.jsonl` | Archivo JSONL de salida |
| `--timeout` | `30` | Timeout por request (s) |
| `--retries` / `--backoff` | `5` / `2.0` | Reintentos y backoff |
| `--delay` / `--jitter` | `1.0` / `0.5` | Cortesía entre requests (s) |
| `--user-agent` | navegador | User-Agent personalizado |
| `--proxy` / `--render` | off | ScraperAPI y render de JS |
| `--respect-robots` / `--ignore-robots` | respeta | Política de robots.txt |
| `--resume` / `--no-resume` / `--skip-failed` | resume | Reanudar; reintenta fallos salvo `--skip-failed` |
| `--allow-non-html` | off | Procesar contenido no-HTML (por defecto se omite) |
| `--inspect` | off | Perfilar la página (tipo, robots, estructura) sin extraer |
| `--detect-api` / `--max-js` / `--no-fetch-js` | off / `5` | Detectar endpoints de API (JSON embebido, bundles JS) |
| `--insecure` | off | No verificar TLS (entornos con proxy/certificado roto) |
| `--contact` | — | Header `From` para identificarte ante el sitio |
| `--log-every` | `10` | Frecuencia de log de progreso |

## Inspección previa (`--inspect`)

Antes de extraer, perfila una URL: tipo de contenido, si `robots.txt` la permite, la
estructura (encabezados, enlaces, tablas, texto) y un diagnóstico del modo recomendado.

```bash
python scripts/scrape.py --url https://ejemplo.com --inspect
```

Útil para decidir `--mode article` vs `--mode soup`, o detectar páginas con anti-bot/JS.

## Detección de API (`--detect-api`)

Para páginas que cargan datos por JavaScript (SPAs), descubre los **endpoints de API**
que usa la página: rastrea el JSON embebido y los *bundles* JS en busca de URLs tipo
`/api/`, `.json` o `graphql`.

```bash
python scripts/scrape.py --url https://ejemplo.com --detect-api
```

Ejemplo real (INE "Ubica tu módulo", una app Nuxt) — encontró sus endpoints:

```
https://ubicatumodulo.ine.mx/api/search/modulos
https://ubicatumodulo.ine.mx/api/search/municipios?e=
https://ubicatumodulo.ine.mx/api/search/moviles/?e=
```

Es heurístico (no ejecuta JS); para exactitud total, captura el XHR con un navegador headless.

## Seguridad

- No ejecuta nada por su cuenta: el código corre solo cuando lo invocas vía Bash.
- API keys vía `os.getenv()` / `.env`; nunca en el código.
- `data/raw/` y `triage/` son solo lectura; las salidas van a `data/processed/` o `reports/`.
- Respeta robots.txt por defecto y aplica cortesía entre requests.

## Tests

```bash
pytest tests/ -q
```

## Compartir como plugin

Esta carpeta ya es un plugin (`.claude-plugin/plugin.json`) y su propio marketplace
(`.claude-plugin/marketplace.json`). Para distribuirla:

1. Súbela a un repo de GitHub (p. ej. `JAPerezC/claude-scraper-skill`).
2. Quien quiera instalarla:
   ```
   /plugin marketplace add JAPerezC/claude-scraper-skill
   /plugin install scraper@jorge-skills
   ```
3. Alternativa simple: copiar la carpeta `scraper/` a `~/.claude/skills/`.
