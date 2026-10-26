"""Valida la paleta de tokens.json: contraste WCAG AA + distinguibilidad CVD.

Uso: python validate_palette.py <tokens.json>
Salida binaria: exit 0 = paleta aprobada; exit 1 = reprobada (con reporte).
Checa ambas variantes (clara y oscura):
  - text/bg y text/surface        >= 4.5 (AA texto normal)
  - text-muted/bg                 >= 4.5
  - accent/bg                     >= 3.0 (AA componentes UI)
  - accent vs accent-2            distinguibles con protanopia y deuteranopia
"""

import json
import logging
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Matrices de simulación CVD (Viénot/Brettel simplificado, sobre RGB lineal)
PROTANOPIA = [[0.567, 0.433, 0.0], [0.558, 0.442, 0.0], [0.0, 0.242, 0.758]]
DEUTERANOPIA = [[0.625, 0.375, 0.0], [0.7, 0.3, 0.0], [0.0, 0.3, 0.7]]


def hex_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


def lineal(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(rgb: tuple) -> float:
    r, g, b = (lineal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    la, lb = luminancia(hex_rgb(a)), luminancia(hex_rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def simular(rgb: tuple, matriz: list) -> tuple:
    lin = [lineal(c) for c in rgb]
    return tuple(sum(matriz[i][j] * lin[j] for j in range(3)) for i in range(3))


def distancia_cvd(a: str, b: str, matriz: list) -> float:
    sa, sb = simular(hex_rgb(a), matriz), simular(hex_rgb(b), matriz)
    return sum((x - y) ** 2 for x, y in zip(sa, sb)) ** 0.5


def revisar_variante(nombre: str, c: dict) -> list[str]:
    errores = []
    pares_texto = [("text", "bg"), ("text", "surface"), ("text-muted", "bg")]
    for fg, bg in pares_texto:
        r = contraste(c[fg], c[bg])
        if r < 4.5:
            errores.append(f"[{nombre}] {fg}/{bg} = {r:.2f} (< 4.5 AA)")
        else:
            log.info("[%s] %s/%s = %.2f OK", nombre, fg, bg, r)
    r = contraste(c["accent"], c["bg"])
    if r < 3.0:
        errores.append(f"[{nombre}] accent/bg = {r:.2f} (< 3.0 AA UI)")
    else:
        log.info("[%s] accent/bg = %.2f OK", nombre, r)
    for etiqueta, matriz in [
        ("protanopia", PROTANOPIA),
        ("deuteranopia", DEUTERANOPIA),
    ]:
        d = distancia_cvd(c["accent"], c["accent-2"], matriz)
        if d < 0.08:
            errores.append(
                f"[{nombre}] accent vs accent-2 indistinguibles con {etiqueta} "
                f"(distancia {d:.3f} < 0.08)"
            )
        else:
            log.info("[%s] accent/accent-2 con %s: %.3f OK", nombre, etiqueta, d)
    return errores


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    tokens = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    colors = tokens["colors"]
    errores = revisar_variante("clara", colors)
    errores += revisar_variante("oscura", colors["dark"])
    if errores:
        log.error("PALETA REPROBADA (%d problemas):", len(errores))
        for e in errores:
            log.error("  - %s", e)
        log.error("Corrige DESIGN.md y regenera con make_tokens.py.")
        sys.exit(1)
    log.info("PALETA APROBADA: contraste AA y CVD en ambas variantes.")


if __name__ == "__main__":
    main()
