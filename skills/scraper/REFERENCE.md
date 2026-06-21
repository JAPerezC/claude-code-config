# Referencia y recetas — skill `scraper`

Recetas avanzadas y solución de problemas. El uso básico está en `README.md`.

## 1. Buscar noticias con Google News RSS y extraer el texto

Google News expone un RSS por consulta. Se obtienen los enlaces y luego se pasan al scraper
en modo `article`:

```python
import feedparser  # pip install feedparser
q = "inteligencia artificial"
feed = feedparser.parse(f"https://news.google.com/rss/search?q={q}&hl=es-419&gl=MX&ceid=MX:es")
urls = [e.link for e in feed.entries]
open("urls.txt", "w", encoding="utf-8").write("\n".join(urls))
```
```bash
python scripts/scrape.py --urls-file urls.txt --mode article --out data/processed/noticias.jsonl
```
Recuerda: Google News limita ~300 requests; si te bloquea, espera ~60 min.

## 2. Paginación

Genera las URLs de las páginas y pásalas como lote:

```python
base = "https://ejemplo.com/blog?page={}"
urls = [base.format(p) for p in range(1, 21)]
open("urls.txt", "w", encoding="utf-8").write("\n".join(urls))
```

## 3. Descubrir todo un sitio por sitemap

```bash
python scripts/scrape.py --sitemap https://ejemplo.com/sitemap.xml --mode article --out data/processed/site.jsonl
```
Si el sitemap es un *índice* (apunta a otros sitemaps), los `<loc>` serán sub-sitemaps:
extrae primero esos y vuelve a llamar con cada uno.

## 4. Convertir la salida JSONL a CSV o Parquet

```python
import pandas as pd
df = pd.read_json("data/processed/out.jsonl", lines=True)
df = df[df["ok"]]                                  # quedarse con los exitosos
df.to_csv("data/processed/out.csv", index=False, encoding="utf-8")
df.to_parquet("data/processed/out.parquet")        # requiere pyarrow
```

## 5. Scraping asíncrono masivo (extensión con httpx)

El script base es síncrono (suficiente y robusto para la mayoría). Para miles de URLs en
paralelo, `httpx` + `asyncio` es más rápido. Patrón mínimo (no incluido en el script para
mantenerlo simple y auditable):

```python
import asyncio, httpx, json

async def fetch_one(client, url, sem):
    async with sem:
        try:
            r = await client.get(url, timeout=30)
            r.raise_for_status()
            return {"url": url, "ok": True, "html_len": len(r.text)}
        except Exception as e:
            return {"url": url, "ok": False, "error": str(e)}

async def main(urls):
    sem = asyncio.Semaphore(10)  # máx. 10 concurrentes (cortesía)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        return await asyncio.gather(*(fetch_one(client, u, sem) for u in urls))
```

## 6. Selectores CSS (modo soup)

| Quieres | Selector |
|---|---|
| Un id | `#contenido` |
| Una clase | `.precio` |
| Etiqueta dentro de clase | `.card h2` |
| Atributo | `a[href^="https"]` |
| Varios a la vez | `h1, .precio, .stock` |

Inspecciona el HTML con las DevTools del navegador (clic derecho → Inspeccionar) para hallar
el selector correcto.

## 7. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `403 Forbidden` o bloqueo | Anti-bot / requiere navegador | `--proxy --render` (ScraperAPI) o cambia `--user-agent` |
| `429 Too Many Requests` | Rate limit | El backoff ya espera; sube `--delay`/`--jitter` y baja el ritmo |
| Página vacía / sin texto | Contenido cargado por JS | `--proxy --render` para renderizar JS |
| `bloqueado por robots.txt` | El sitio lo prohíbe | Solo con permiso: `--ignore-robots` |
| trafilatura no extrae nada | No es un artículo (es listado/app) | Usa `--mode soup` con un selector |
| Caracteres raros | Encoding mal detectado | El script ya usa `apparent_encoding`; revisa la fuente |

## 8. Buenas prácticas (ética y legalidad)

- Respeta `robots.txt` (activo por defecto) y los Términos de Servicio del sitio.
- Identifícate con un `--user-agent` honesto si el sitio lo pide.
- Usa `--delay` para no saturar el servidor.
- No scrapees datos personales sin base legal; cuida la privacidad.
