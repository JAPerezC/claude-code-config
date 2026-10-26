#!/usr/bin/env python3
"""Scraper robusto y reutilizable para la skill `scraper`.

Implementa de una vez la lógica que el SKILL.md solo describía:
- Sesión HTTP con timeout explícito y retry con backoff exponencial (429/5xx).
- Respeto del header `Retry-After` y del `Crawl-delay` de robots.txt.
- Modo `--inspect`: perfil de la página (tipo, robots, estructura, diagnóstico) sin extraer.
- Modo `--detect-api`: detecta endpoints de API (JSON embebido, bundles JS, URLs tipo API).
- Respeto de robots.txt por host (configurable con --ignore-robots).
- Identificación del tipo de contenido (HTML/PDF/JSON/imagen): omite lo no-HTML
  con un aviso claro (p.ej. sugiere la skill `pdf` para PDFs); --allow-non-html lo fuerza.
- Self-identificación opcional ante el sitio con el header `From` (--contact).
- Descubrimiento de URLs por sitemap.xml (--sitemap).
- Guardado incremental en JSONL (no se pierde progreso si crashea).
- Reanudación: salta URLs ya extraídas con éxito; los fallos se reintentan
  (usa --skip-failed para saltarlos también).
- Integridad del JSONL: trunca una línea parcial al final (crash previo) y
  registra líneas corruptas con su número.
- Validación de URLs de entrada (solo http/https).
- Proxy opcional vía ScraperAPI (clave en `.env`, nunca hardcodeada).
- Dos modos de extracción: `article` (trafilatura) y `soup` (selector CSS).
- Logging a nivel INFO, encoding utf-8 y rutas con pathlib (Windows-friendly).

Uso típico:
    python scrape.py --urls-file urls.txt --out data/processed/out.jsonl --mode article
    python scrape.py --url https://ejemplo.com/articulo --mode article
    python scrape.py --sitemap https://ejemplo.com/sitemap.xml --mode article
    python scrape.py --urls-file urls.txt --mode soup --selector "h1, .precio"

Las dependencias están fijadas en ../requirements.txt (instalar en venv).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scraper")

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
SCRAPERAPI_ENDPOINT = "https://api.scraperapi.com/"


def load_env() -> None:
    """Carga variables de `.env` si python-dotenv está disponible (opcional)."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        log.debug("python-dotenv no instalado; se usan variables de entorno del SO.")


def build_session(
    user_agent: str = DEFAULT_UA,
    total_retries: int = 5,
    backoff_factor: float = 2.0,
    contact: str | None = None,
    insecure: bool = False,
) -> requests.Session:
    """Crea una sesión con retry+backoff que respeta `Retry-After`.

    backoff_factor=2 -> esperas de 0, 2, 4, 8, 16 s entre reintentos.
    `contact` (email/URL) se envía en el header `From` para identificarte ante el sitio.
    """
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.verify = not insecure  # verificación TLS (desactivable con --insecure)
    if insecure:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": user_agent})
    if contact:
        session.headers["From"] = contact
    return session


def dedup(urls: list[str]) -> list[str]:
    """Elimina duplicados preservando el orden de aparición."""
    seen: set[str] = set()
    return [u for u in urls if not (u in seen or seen.add(u))]


def valid_urls(urls: list[str]) -> list[str]:
    """Filtra URLs: solo http/https con host. Las descartadas se registran."""
    out: list[str] = []
    for u in urls:
        parsed = urlparse(u)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            out.append(u)
        else:
            log.warning("URL ignorada (no http/https o sin host): %r", u)
    return out


def classify_content(content_type: str, url: str, head: bytes = b"") -> str:
    """Identifica el tipo de recurso: 'html' | 'pdf' | 'json' | 'image' | 'other'.

    Usa el Content-Type, la extensión de la URL y (si se pasa) los primeros bytes.
    Un Content-Type vacío se asume HTML (mejor esfuerzo).
    """
    ct = (content_type or "").lower()
    u = (url or "").lower()
    if "pdf" in ct or u.endswith(".pdf") or head.startswith(b"%PDF"):
        return "pdf"
    if not ct:
        return "html"
    if "html" in ct or "xml" in ct:
        return "html"
    if "json" in ct:
        return "json"
    if ct.startswith("image/"):
        return "image"
    return "other"


class RobotsGate:
    """Comprueba robots.txt por host, con cache. Fail-open: si robots.txt no es
    accesible, se asume permitido (comportamiento convencional) y se registra."""

    def __init__(
        self, session: requests.Session, user_agent: str, enabled: bool = True
    ):
        self.session = session
        self.ua = user_agent
        self.enabled = enabled
        self._cache: dict[str, RobotFileParser] = {}

    def allowed(self, url: str) -> bool:
        if not self.enabled:
            return True
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._cache.get(base)
        if rp is None:
            rp = self._load(base)
            self._cache[base] = rp
        return rp.can_fetch(self.ua, url)

    def _load(self, base: str) -> RobotFileParser:
        rp = RobotFileParser()
        robots_url = urljoin(base, "/robots.txt")
        try:
            resp = self.session.get(robots_url, timeout=10)
            rp.parse([] if resp.status_code >= 400 else resp.text.splitlines())
        except requests.RequestException as exc:
            log.warning("No se pudo leer %s (%s); se asume permitido.", robots_url, exc)
            rp.parse([])
        return rp

    def crawl_delay(self, url: str) -> float | None:
        """Crawl-delay declarado en robots.txt para nuestro UA (o None)."""
        if not self.enabled:
            return None
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._cache.get(base)
        if rp is None:
            rp = self._load(base)
            self._cache[base] = rp
        try:
            return rp.crawl_delay(self.ua)
        except Exception:  # noqa: BLE001
            return None


def read_sitemap(
    session: requests.Session, sitemap_url: str, timeout: int = 30
) -> list[str]:
    """Extrae las URLs (<loc>) de un sitemap.xml (o índice de sitemaps)."""
    from bs4 import BeautifulSoup

    resp = session.get(sitemap_url, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "xml")
    return [loc.get_text(strip=True) for loc in soup.find_all("loc")]


def _scraperapi_params(url: str, render: bool) -> tuple[str, dict] | None:
    """Devuelve (endpoint, params) para enrutar por ScraperAPI, o None si no aplica."""
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key:
        return None
    params = {"api_key": api_key, "url": url}
    if render:
        params["render"] = "true"
    return SCRAPERAPI_ENDPOINT, params


def fetch(
    session: requests.Session,
    url: str,
    timeout: int = 30,
    use_scraperapi: bool = False,
    render: bool = False,
) -> requests.Response:
    """Descarga `url` y devuelve la Response (con encoding corregido).

    Lanza requests.HTTPError en 4xx/5xx finales.
    """
    if use_scraperapi:
        routed = _scraperapi_params(url, render)
        if routed is None:
            raise RuntimeError(
                "Se pidió --proxy pero no hay SCRAPERAPI_KEY en el entorno/.env"
            )
        endpoint, params = routed
        resp = session.get(endpoint, params=params, timeout=timeout)
    else:
        resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp


def extract_article(html: str, url: str | None = None) -> dict:
    """Extrae el contenido principal y metadatos con trafilatura (import perezoso)."""
    import trafilatura

    raw = trafilatura.extract(
        html,
        output_format="json",
        with_metadata=True,
        include_comments=False,
        include_tables=True,
        url=url,
    )
    if not raw:
        return {"url": url, "ok": False, "error": "trafilatura no extrajo contenido"}
    data = json.loads(raw)
    data["url"] = url or data.get("source") or data.get("url")
    data["ok"] = True
    return data


def extract_soup(html: str, selector: str, url: str | None = None) -> dict:
    """Extrae texto de los elementos que coincidan con `selector` (CSS) vía BeautifulSoup."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    matches = [el.get_text(strip=True) for el in soup.select(selector)]
    return {
        "url": url,
        "ok": bool(matches),
        "selector": selector,
        "matches": matches,
        "title": soup.title.get_text(strip=True) if soup.title else None,
    }


def repair_trailing_partial(out_path: Path) -> None:
    """Trunca una línea JSONL parcial al final del archivo (crash previo).

    Como `write_record` siempre termina cada registro con '\\n', un archivo sano
    termina en '\\n'. Si no, hay una línea incompleta: se trunca hasta el último '\\n'.
    """
    if not out_path.exists() or out_path.stat().st_size == 0:
        return
    with out_path.open("rb") as fh:
        fh.seek(-1, os.SEEK_END)
        if fh.read(1) == b"\n":
            return  # termina correctamente
    data = out_path.read_bytes()
    idx = data.rfind(b"\n")
    new_len = idx + 1 if idx >= 0 else 0
    with out_path.open("rb+") as fh:
        fh.truncate(new_len)
    log.warning(
        "Se truncó una línea JSONL parcial al final de %s (crash previo).", out_path
    )


def load_done(out_path: Path, skip_failed: bool = False) -> set[str]:
    """URLs ya procesadas en el JSONL de salida (para reanudar).

    Por defecto solo cuenta como "hecha" una URL con `ok: true`, de modo que los
    fallos previos se reintentan. Con `skip_failed=True` se saltan también los fallos.
    Las líneas corruptas se registran (con su número) y se ignoran.
    """
    done: set[str] = set()
    if not out_path.exists():
        return done
    with out_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                log.warning("Línea JSONL corrupta ignorada (%s:%d).", out_path, lineno)
                continue
            url = rec.get("url")
            if url and (skip_failed or rec.get("ok") is True):
                done.add(url)
    return done


def write_record(fh, record: dict) -> None:
    """Escribe un registro como una línea JSON y hace flush (guardado incremental)."""
    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    fh.flush()


def read_urls(args: argparse.Namespace) -> list[str]:
    """Reúne las URLs desde --url, --urls (coma) o --urls-file (una por línea, # = comentario)."""
    urls: list[str] = []
    if args.url:
        urls.append(args.url)
    if args.urls:
        urls.extend(u.strip() for u in args.urls.split(",") if u.strip())
    if args.urls_file:
        path = Path(args.urls_file)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def _suggest_mode(structure: dict, js_likely: bool) -> str:
    """Heurística: sugiere cómo scrapear según la estructura detectada."""
    if js_likely:
        return "Poco contenido estático -> probablemente JS; usa --proxy --render."
    text_chars = structure.get("text_chars", 0)
    links = structure.get("links", 0)
    if text_chars and links > 50 and text_chars / max(links, 1) < 40:
        return "Parece un listado -> usa --mode soup con un selector de los items."
    return "Parece contenido de artículo -> usa --mode article."


def inspect_url(args, session, url, robots_allowed: bool) -> dict:
    """Perfila una URL sin extraer: tipo, robots, estructura y diagnóstico."""
    profile = {"url": url, "inspect": True, "robots_allowed": robots_allowed}
    if not robots_allowed and args.respect_robots:
        profile["ok"] = False
        profile["note"] = (
            "robots.txt no permite esta URL (usa --ignore-robots para inspeccionar)."
        )
        return profile
    try:
        resp = fetch(
            session,
            url,
            timeout=args.timeout,
            use_scraperapi=args.proxy,
            render=args.render,
        )
    except Exception as exc:  # noqa: BLE001
        profile["ok"] = False
        profile["error"] = f"{type(exc).__name__}: {exc}"
        return profile

    ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    kind = classify_content(ctype, str(resp.url), resp.content[:8])
    profile.update(
        {
            "ok": True,
            "status": resp.status_code,
            "content_type": ctype,
            "kind": kind,
            "final_url": str(resp.url),
        }
    )
    if kind != "html":
        profile["diagnostico"] = {
            "pdf": "Es un PDF; usa la skill 'pdf' para extraer texto/tablas.",
            "json": "Es JSON; parséalo directamente (no necesita scraping HTML).",
            "image": "Es una imagen.",
        }.get(kind, "Contenido no-HTML.")
        return profile

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(" ", strip=True)
    structure = {
        "h1": len(soup.find_all("h1")),
        "h2": len(soup.find_all("h2")),
        "h3": len(soup.find_all("h3")),
        "links": len(soup.find_all("a")),
        "tables": len(soup.find_all("table")),
        "forms": len(soup.find_all("form")),
        "images": len(soup.find_all("img")),
        "text_chars": len(text),
    }
    js_likely = len(text.strip()) < 500 or resp.status_code in (202, 204)
    profile["title"] = soup.title.get_text(strip=True) if soup.title else None
    profile["structure"] = structure
    profile["js_likely"] = js_likely
    profile["diagnostico"] = _suggest_mode(structure, js_likely)
    return profile


API_HINT = re.compile(r"(api|graphql|\.json|/v\d+/|/rest/|/service|/data/)", re.I)
_ABS_URL = re.compile(r"https?://[^\s\"'`)<>]+")
_REL_URL = re.compile(r"""["'](/[A-Za-z0-9_\-./][A-Za-z0-9_\-./?=&%]*)["']""")


def _extract_api_candidates(text: str, base_url: str) -> set:
    """Extrae URLs/paths con pinta de API desde HTML o JS (heurístico)."""
    cands: set[str] = set()
    for m in _ABS_URL.findall(text):
        m = m.rstrip(",;\\")
        if API_HINT.search(m):
            cands.add(m)
    for m in _REL_URL.findall(text):
        if API_HINT.search(m):
            cands.add(urljoin(base_url, m))
    return cands


def detect_api(args, session, url, robots_allowed) -> dict:
    """Detecta (estáticamente) endpoints de API que usa la página: JSON embebido,
    bundles JS y URLs con pinta de API. No ejecuta JS; es heurístico."""
    result = {"url": url, "detect_api": True, "robots_allowed": robots_allowed}
    if not robots_allowed and args.respect_robots:
        result["ok"] = False
        result["note"] = "robots.txt no permite esta URL (usa --ignore-robots)."
        return result
    try:
        resp = fetch(
            session,
            url,
            timeout=args.timeout,
            use_scraperapi=args.proxy,
            render=args.render,
        )
    except Exception as exc:  # noqa: BLE001
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text, "lxml")
    base = str(resp.url)
    candidates = _extract_api_candidates(resp.text, base)

    embedded = []
    for s in soup.find_all("script"):
        stype = (s.get("type") or "").lower()
        if stype in ("application/json", "application/ld+json"):
            txt = s.string or s.get_text()
            if txt and txt.strip():
                embedded.append({"type": stype, "id": s.get("id"), "chars": len(txt)})

    bundles = [urljoin(base, s["src"]) for s in soup.find_all("script", src=True)]
    if not args.no_fetch_js:
        for b in bundles[: args.max_js]:
            try:
                jr = session.get(b, timeout=args.timeout)
                if jr.ok and len(jr.content) < 3_000_000:
                    candidates |= _extract_api_candidates(jr.text, base)
            except requests.RequestException:
                continue

    result.update(
        {
            "ok": bool(candidates) or bool(embedded),
            "status": resp.status_code,
            "api_candidates": sorted(candidates)[:50],
            "embedded_json": embedded,
            "js_bundles_revisados": bundles[: args.max_js]
            if not args.no_fetch_js
            else [],
            "note": "Detección estática/heurística (no ejecuta JS). Para exactitud total, captura el tráfico XHR con un navegador headless o las DevTools.",
        }
    )
    return result


def _process_url(args, session, url) -> dict:
    """Descarga, identifica el contenido y extrae. Devuelve el registro (dict con 'ok')."""
    resp = fetch(
        session,
        url,
        timeout=args.timeout,
        use_scraperapi=args.proxy,
        render=args.render,
    )
    ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    kind = classify_content(ctype, str(resp.url), resp.content[:8])

    if kind != "html" and not args.allow_non_html:
        record = {
            "url": url,
            "ok": False,
            "error": f"contenido no-HTML ({kind})",
            "content_type": ctype,
            "final_url": str(resp.url),
        }
        if kind == "pdf":
            record["hint"] = "Es un PDF; usa la skill 'pdf' para extraer texto/tablas."
        else:
            record["hint"] = "Usa --allow-non-html para procesarlo de todas formas."
        return record

    html = resp.text
    if len(html.strip()) < 100:
        return {
            "url": url,
            "ok": False,
            "error": f"respuesta vacía o insuficiente (HTTP {resp.status_code})",
            "content_type": ctype,
            "status": resp.status_code,
            "final_url": str(resp.url),
            "hint": "Posible anti-bot o contenido por JS; prueba --proxy --render.",
        }
    if args.mode == "article":
        record = extract_article(html, url=url)
    else:
        record = extract_soup(html, args.selector, url=url)
    record.setdefault("content_type", ctype)
    if str(resp.url) != url:
        record["final_url"] = str(resp.url)

    # Pista: poca textualidad suele indicar contenido renderizado por JS.
    if record.get("ok"):
        if args.mode == "article":
            text_len = len(record.get("text") or "")
        else:
            text_len = sum(len(m) for m in record.get("matches", []))
        if text_len < 200:
            log.info(
                "Poca textualidad en %s (%d chars); quizá requiera --proxy --render (JS).",
                url,
                text_len,
            )
    return record


def scrape(args: argparse.Namespace) -> int:
    if args.render and not args.proxy:
        log.error("--render requiere --proxy (ScraperAPI). Abortando.")
        return 2

    load_env()
    if args.insecure:
        log.warning(
            "--insecure activo: NO se verifica el certificado TLS (riesgo de MITM)."
        )
    ua = args.user_agent or DEFAULT_UA
    session = build_session(
        user_agent=ua,
        total_retries=args.retries,
        backoff_factor=args.backoff,
        contact=args.contact,
        insecure=args.insecure,
    )

    urls = read_urls(args)
    if args.sitemap:
        try:
            found = read_sitemap(session, args.sitemap, timeout=args.timeout)
            log.info("Sitemap %s -> %d URLs", args.sitemap, len(found))
            urls += found
        except Exception as exc:  # noqa: BLE001
            log.warning("No se pudo leer el sitemap %s: %s", args.sitemap, exc)
    urls = dedup(valid_urls(urls))
    if not urls:
        log.error("No hay URLs válidas (--url/--urls/--urls-file/--sitemap).")
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    repair_trailing_partial(out_path)

    done = load_done(out_path, skip_failed=args.skip_failed) if args.resume else set()
    pending = [u for u in urls if u not in done]
    robots = RobotsGate(session, ua, enabled=args.respect_robots)
    log.info(
        "Total %d | hechas %d | pendientes %d | modo=%s | robots=%s | proxy=%s -> %s",
        len(urls),
        len(done),
        len(pending),
        args.mode,
        args.respect_robots,
        args.proxy,
        out_path,
    )

    ok = fail = skipped = 0
    with out_path.open("a", encoding="utf-8") as fh:
        for i, url in enumerate(pending, start=1):
            allowed = robots.allowed(url)
            if args.inspect:
                record = inspect_url(args, session, url, allowed)
                write_record(fh, record)
                if record.get("ok"):
                    ok += 1
                else:
                    fail += 1
                if i % args.log_every == 0:
                    log.info("Inspección %d/%d", i, len(pending))
                if i < len(pending):
                    time.sleep(args.delay + random.uniform(0, args.jitter))
                continue
            if args.detect_api:
                record = detect_api(args, session, url, allowed)
                write_record(fh, record)
                if record.get("ok"):
                    ok += 1
                else:
                    fail += 1
                if i < len(pending):
                    time.sleep(args.delay + random.uniform(0, args.jitter))
                continue
            if not allowed:
                write_record(
                    fh, {"url": url, "ok": False, "error": "bloqueado por robots.txt"}
                )
                skipped += 1
                log.info("ROBOTS bloquea %s (usa --ignore-robots para forzar)", url)
                continue
            try:
                record = _process_url(args, session, url)
            except Exception as exc:  # noqa: BLE001 - registramos y seguimos, no abortamos el lote
                record = {
                    "url": url,
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
                log.warning("FALLO %s -> %s", url, exc)

            write_record(fh, record)
            if record.get("ok"):
                ok += 1
            else:
                fail += 1

            if i % args.log_every == 0:
                log.info(
                    "Progreso %d/%d (ok=%d, fail=%d, robots=%d)",
                    i,
                    len(pending),
                    ok,
                    fail,
                    skipped,
                )

            if i < len(pending):  # cortesía entre requests con jitter (+ Crawl-delay)
                base_delay = args.delay
                if args.respect_robots:
                    cd = robots.crawl_delay(url)
                    if cd:
                        base_delay = max(base_delay, float(cd))
                time.sleep(base_delay + random.uniform(0, args.jitter))

    log.info(
        "Listo. ok=%d, fail=%d, robots-skip=%d, salida=%s", ok, fail, skipped, out_path
    )
    return 0 if fail == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scraper robusto (skill scraper).")
    src = p.add_argument_group("fuente de URLs")
    src.add_argument("--url", help="Una sola URL.")
    src.add_argument("--urls", help="URLs separadas por coma.")
    src.add_argument(
        "--urls-file", help="Archivo con una URL por línea (# = comentario)."
    )
    src.add_argument("--sitemap", help="URL de un sitemap.xml para descubrir URLs.")

    p.add_argument(
        "--out", default="scrape_output.jsonl", help="JSONL de salida (incremental)."
    )
    p.add_argument(
        "--mode",
        choices=("article", "soup"),
        default="article",
        help="article=trafilatura (texto+metadatos); soup=selector CSS.",
    )
    p.add_argument("--selector", default="body", help="Selector CSS para modo soup.")
    p.add_argument(
        "--allow-non-html",
        action="store_true",
        help="Procesar también contenido no-HTML (por defecto se omite con aviso).",
    )
    p.add_argument(
        "--inspect",
        action="store_true",
        help="No extrae: devuelve un perfil (tipo, robots, estructura, diagnóstico) por URL.",
    )
    p.add_argument(
        "--detect-api",
        action="store_true",
        help="Detecta endpoints de API que usa la página (JSON embebido, bundles JS, URLs tipo API).",
    )

    net = p.add_argument_group("red")
    net.add_argument("--timeout", type=int, default=30, help="Timeout por request (s).")
    net.add_argument("--retries", type=int, default=5, help="Reintentos por request.")
    net.add_argument(
        "--backoff", type=float, default=2.0, help="backoff_factor del retry."
    )
    net.add_argument(
        "--delay", type=float, default=1.0, help="Pausa base entre requests (s)."
    )
    net.add_argument(
        "--jitter", type=float, default=0.5, help="Jitter aleatorio extra (s)."
    )
    net.add_argument("--user-agent", default=None, help="User-Agent personalizado.")
    net.add_argument(
        "--contact",
        default=None,
        help="Email/URL de contacto (header From) para identificarte ante el sitio.",
    )
    net.add_argument(
        "--insecure",
        action="store_true",
        help="No verificar el certificado TLS (úsalo solo si confías en el destino).",
    )
    net.add_argument(
        "--max-js",
        type=int,
        default=5,
        help="Máximo de bundles JS a descargar para --detect-api.",
    )
    net.add_argument(
        "--no-fetch-js",
        action="store_true",
        help="En --detect-api, no descargar los bundles JS (solo analiza el HTML).",
    )
    net.add_argument(
        "--proxy",
        action="store_true",
        help="Enrutar por ScraperAPI (SCRAPERAPI_KEY en .env).",
    )
    net.add_argument(
        "--render",
        action="store_true",
        help="Renderizar JS vía ScraperAPI (requiere --proxy).",
    )

    pol = p.add_argument_group("cortesía / política")
    pol.add_argument(
        "--respect-robots",
        action="store_true",
        default=True,
        help="Respetar robots.txt (por defecto activo).",
    )
    pol.add_argument(
        "--ignore-robots",
        dest="respect_robots",
        action="store_false",
        help="Ignorar robots.txt (úsalo solo si tienes permiso).",
    )

    res = p.add_argument_group("reanudación")
    res.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Saltar URLs ya extraídas con éxito (por defecto activo).",
    )
    res.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="No reanudar; reprocesa todas las URLs.",
    )
    res.add_argument(
        "--skip-failed",
        action="store_true",
        help="Al reanudar, NO reintentar las URLs que fallaron antes (por defecto SÍ se reintentan).",
    )
    p.add_argument(
        "--log-every", type=int, default=10, help="Cada cuántas URLs loguear progreso."
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return scrape(args)


if __name__ == "__main__":
    sys.exit(main())
