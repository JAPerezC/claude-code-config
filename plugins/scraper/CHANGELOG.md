# Changelog

## 1.3.0 - 2026-06-19

### Añadido
- **Modo `--detect-api`**: detección estática de endpoints de API que usa una página
  (JSON embebido, *bundles* JS y URLs con pinta de API tipo `/api/`, `.json`, `graphql`).
  Ideal para apps JavaScript/SPA. Flags `--max-js` y `--no-fetch-js`. Es heurístico
  (no ejecuta JS).

## 1.2.0 - 2026-06-19

### Añadido
- **Modo `--inspect`**: perfila una URL sin extraer (tipo de contenido, si robots la permite,
  estructura: h1/h2/h3/enlaces/tablas/formularios/texto, y un diagnóstico con el modo recomendado).
- **Respeto del `Crawl-delay`** de robots.txt (se usa como piso del `--delay`).

## 1.1.0 - 2026-06-19

### Añadido
- **Identificación del tipo de contenido** (HTML / PDF / JSON / imagen): el contenido
  no-HTML se omite con un aviso claro; para PDFs sugiere usar la skill `pdf`.
  `--allow-non-html` lo procesa de todas formas.
- **Self-identificación** ante el sitio con `--contact` (header `From`).
- **`--skip-failed`**: al reanudar, no reintentar las URLs que fallaron antes.
- **Validación de URLs** de entrada (solo http/https; se descartan y registran las demás).
- **Pista de JS**: avisa cuando una página tiene poca textualidad (posible render JS).
- **Detección de respuesta vacía / anti-bot**: si el cuerpo viene vacío o insuficiente
  (p. ej. HTTP 202 sin contenido, como ESPN), lo reporta con el status y sugiere `--proxy --render`.
- **`--insecure`**: omitir la verificación TLS (opt-in, con aviso) para entornos con proxy
  corporativo o certificados rotos.
- Empaquetado para compartir: `LICENSE` (MIT), `.gitignore`, `.claude-plugin/marketplace.json`.

### Corregido
- **Reanudación**: ahora reintenta los fallos por defecto (antes los saltaba en silencio).
- **Conteo ok/fail**: una extracción vacía ya no se cuenta como éxito.
- **Integridad del JSONL**: se trunca la línea parcial tras un crash y se registran
  las líneas corruptas con su número; el archivo de salida se abre una sola vez.
- `extract_soup` usa `get_text()` para el título (antes podía ser `None`).
- `--render` ahora exige `--proxy` (antes se ignoraba en silencio).
- `verify=True` explícito en la sesión HTTP.

## 1.0.0

- Versión inicial: modos article/soup, retry+backoff, robots.txt, sitemap,
  guardado incremental, reanudación y tests offline.
