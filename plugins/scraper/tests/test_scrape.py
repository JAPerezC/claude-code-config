"""Tests offline de la skill `scraper` (no requieren red).

Ejecutar:  pytest tests/ -q
Si faltan dependencias (requests/bs4/lxml), los tests afectados se saltan, no fallan.
"""

import sys
from pathlib import Path

import pytest

# Las dependencias core deben estar para importar el modulo; si no, saltar todo.
pytest.importorskip("requests")
pytest.importorskip("urllib3")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "scraper" / "scripts"))
import scrape  # noqa: E402


class _Args:
    """Stub minimo de argparse.Namespace para read_urls."""

    def __init__(self, url=None, urls=None, urls_file=None):
        self.url = url
        self.urls = urls
        self.urls_file = urls_file


def test_dedup_preserva_orden():
    assert scrape.dedup(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_valid_urls_filtra_no_http():
    entrada = [
        "https://ok.com/p",
        "http://ok2.com",
        "ftp://no.com",
        "file:///etc/passwd",
        "sin-esquema.com",
        "",
    ]
    assert scrape.valid_urls(entrada) == ["https://ok.com/p", "http://ok2.com"]


def test_classify_content():
    assert scrape.classify_content("application/pdf", "https://x/a") == "pdf"
    assert scrape.classify_content("", "https://x/file.PDF") == "pdf"
    assert scrape.classify_content("", "https://x/p", b"%PDF-1.7") == "pdf"
    assert scrape.classify_content("text/html", "https://x") == "html"
    assert scrape.classify_content("text/xml", "https://x") == "html"
    assert scrape.classify_content("", "https://x/p") == "html"
    assert scrape.classify_content("application/json", "https://x") == "json"
    assert scrape.classify_content("image/png", "https://x") == "image"
    assert scrape.classify_content("application/octet-stream", "https://x") == "other"


def test_build_session_contact_header():
    s = scrape.build_session(contact="datos@ejemplo.com")
    assert s.headers.get("From") == "datos@ejemplo.com"
    assert "From" not in scrape.build_session().headers


def test_build_session_insecure():
    assert scrape.build_session(insecure=True).verify is False
    assert scrape.build_session().verify is True


def test_read_urls_archivo_ignora_comentarios_y_vacios(tmp_path):
    f = tmp_path / "urls.txt"
    f.write_text(
        "https://a.com\n# comentario\n\nhttps://b.com\nhttps://a.com\n",
        encoding="utf-8",
    )
    args = _Args(urls_file=str(f))
    # read_urls no deduplica (eso lo hace dedup en scrape); aqui valida el parseo
    assert scrape.read_urls(args) == ["https://a.com", "https://b.com", "https://a.com"]


def test_read_urls_combina_fuentes():
    args = _Args(url="https://a.com", urls="https://b.com, https://c.com")
    assert scrape.read_urls(args) == ["https://a.com", "https://b.com", "https://c.com"]


def test_load_done_solo_marca_exitos(tmp_path):
    out = tmp_path / "out.jsonl"
    out.write_text(
        '{"url": "https://ok.com", "ok": true}\n'
        '{"json roto"\n'
        '{"url": "https://fail.com", "ok": false}\n'
        '{"url": "https://sinok.com"}\n',
        encoding="utf-8",
    )
    # Por defecto: solo ok:true cuenta como hecho (los fallos se reintentan)
    assert scrape.load_done(out) == {"https://ok.com"}
    # Con skip_failed=True: tambien se saltan fallos y registros sin ok
    assert scrape.load_done(out, skip_failed=True) == {
        "https://ok.com",
        "https://fail.com",
        "https://sinok.com",
    }


def test_repair_trailing_partial_trunca_linea_incompleta(tmp_path):
    out = tmp_path / "out.jsonl"
    out.write_text(
        '{"url": "https://a.com", "ok": true}\n'
        '{"url": "https://b.com", "ok": true}\n'
        '{"url": "https://c.com", "ok',  # linea parcial sin \n (simula crash)
        encoding="utf-8",
    )
    scrape.repair_trailing_partial(out)
    assert out.read_text(encoding="utf-8").splitlines() == [
        '{"url": "https://a.com", "ok": true}',
        '{"url": "https://b.com", "ok": true}',
    ]
    # Un archivo ya sano no se modifica
    antes = out.read_bytes()
    scrape.repair_trailing_partial(out)
    assert out.read_bytes() == antes


def test_scraperapi_params(monkeypatch):
    monkeypatch.delenv("SCRAPERAPI_KEY", raising=False)
    assert scrape._scraperapi_params("https://x.com", False) is None

    monkeypatch.setenv("SCRAPERAPI_KEY", "demo-key")
    endpoint, params = scrape._scraperapi_params("https://x.com", True)
    assert endpoint == scrape.SCRAPERAPI_ENDPOINT
    assert params["api_key"] == "demo-key"
    assert params["url"] == "https://x.com"
    assert params["render"] == "true"


def test_robots_gate_desactivado_permite_todo():
    gate = scrape.RobotsGate(session=None, user_agent="x", enabled=False)
    assert gate.allowed("https://cualquier-sitio.com/pagina") is True


def test_extract_soup_con_selector():
    pytest.importorskip("bs4")
    pytest.importorskip("lxml")
    html = (
        "<html><head><title>Titulo</title></head>"
        "<body><h1>Hola</h1><p class='x'>Mundo</p></body></html>"
    )
    r = scrape.extract_soup(html, "h1, .x", url="https://x.com")
    assert r["ok"] is True
    assert r["matches"] == ["Hola", "Mundo"]
    assert r["title"] == "Titulo"


def test_suggest_mode():
    assert (
        "render" in scrape._suggest_mode({"text_chars": 10, "links": 2}, True).lower()
    )
    assert (
        "article"
        in scrape._suggest_mode({"text_chars": 5000, "links": 5}, False).lower()
    )
    assert (
        "soup" in scrape._suggest_mode({"text_chars": 300, "links": 200}, False).lower()
    )


def test_extract_api_candidates():
    js = (
        'fetch("/api/v1/modulos?cp=06000");'
        ' var u = "https://geo.ine.mx/rest/buscar.json";'
        ' img = "/static/logo.png";'
    )
    cands = scrape._extract_api_candidates(js, "https://ubicatumodulo.ine.mx/")
    assert "https://ubicatumodulo.ine.mx/api/v1/modulos?cp=06000" in cands
    assert "https://geo.ine.mx/rest/buscar.json" in cands
    assert not any("logo.png" in c for c in cands)


def test_robots_crawl_delay():
    from urllib.robotparser import RobotFileParser

    gate = scrape.RobotsGate(session=None, user_agent="*", enabled=True)
    rp = RobotFileParser()
    rp.parse(["User-agent: *", "Crawl-delay: 7"])
    gate._cache["https://x.com"] = rp
    assert gate.crawl_delay("https://x.com/p") == 7
