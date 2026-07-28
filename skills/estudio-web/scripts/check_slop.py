"""Lint anti-slop: detecta patrones de diseño genérico de IA en el proyecto.

Uso: python check_slop.py <directorio del proyecto>
Revisa .css, .astro, .svelte, .html, .jsx, .tsx (ignora node_modules, dist,
.svelte-kit y los propios tokens). Exit 0 = limpio; exit 1 = hallazgos.

Reglas (ver references/anti-slop.md):
  1. Fuentes prohibidas en font-family (Inter, Roboto, Arial, system-ui...)
  2. Gradientes púrpura/violeta (el cliché púrpura-cian)
  3. Hex sueltos fuera de tokens.css / DESIGN.md
  4. Easing con rebote (bounce / overshoot)
"""

import logging
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

EXTENSIONES = {".css", ".astro", ".svelte", ".html", ".jsx", ".tsx", ".vue"}
IGNORAR_DIRS = {"node_modules", "dist", ".svelte-kit", ".astro", "build", ".git"}
IGNORAR_ARCHIVOS = {"tokens.css", "DESIGN.md"}

FUENTES_PROHIBIDAS = re.compile(
    r"font-family[^;{}]*\b(Inter|Roboto(?!\s*Slab)|Arial|Helvetica(?:\s*Neue)?|system-ui|Segoe UI)\b",
    re.IGNORECASE,
)
# Púrpuras típicos de Tailwind/IA (violet/purple 400-600) en gradientes
PURPURA = re.compile(
    r"gradient[^;{}]*(#(?:8b5cf6|a855f7|7c3aed|9333ea|6d28d9|c084fc|a78bfa)|(?:\b(?:purple|violet)\b))",
    re.IGNORECASE,
)
HEX_SUELTO = re.compile(r"(?<![\w-])#[0-9a-fA-F]{3,8}\b")
BOUNCE = re.compile(
    r"(cubic-bezier\(\s*[\d.]+\s*,\s*-|cubic-bezier\([^)]*,\s*[\d.]+\s*,\s*1\.[5-9]|\bbounce\b|elastic)",
    re.IGNORECASE,
)


def revisar(path: Path) -> list[str]:
    hallazgos = []
    texto = path.read_text(encoding="utf-8", errors="ignore")
    for n, linea in enumerate(texto.splitlines(), 1):
        if FUENTES_PROHIBIDAS.search(linea):
            hallazgos.append(
                f"{path}:{n}: fuente prohibida en titular/cuerpo → usar las del DESIGN.md"
            )
        if PURPURA.search(linea):
            hallazgos.append(
                f"{path}:{n}: gradiente púrpura/violeta (cliché IA) → usar tokens de acento"
            )
        if BOUNCE.search(linea):
            hallazgos.append(
                f"{path}:{n}: easing con rebote → usar ease-out expo sobrio"
            )
        if path.name not in IGNORAR_ARCHIVOS and path.suffix != ".md":
            for m in HEX_SUELTO.finditer(linea):
                if "url(" in linea or "data:image" in linea:
                    continue
                hallazgos.append(
                    f"{path}:{n}: hex suelto {m.group(0)} → mover a tokens.css"
                )
    return hallazgos


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raiz = Path(sys.argv[1])
    if not raiz.is_dir():
        sys.exit(f"ERROR: {raiz} no es un directorio.")
    hallazgos = []
    for p in raiz.rglob("*"):
        if p.suffix not in EXTENSIONES or p.name in IGNORAR_ARCHIVOS:
            continue
        if any(parte in IGNORAR_DIRS for parte in p.parts):
            continue
        hallazgos.extend(revisar(p))
    if hallazgos:
        log.error("ANTI-SLOP: %d hallazgos", len(hallazgos))
        for h in hallazgos:
            log.error("  %s", h)
        sys.exit(1)
    log.info("ANTI-SLOP: limpio. Sin patrones genéricos detectados.")


if __name__ == "__main__":
    main()
