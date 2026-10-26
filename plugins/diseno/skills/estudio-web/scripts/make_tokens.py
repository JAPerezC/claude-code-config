"""Genera tokens.css (Tailwind 4 @theme) y tokens.json desde un DESIGN.md.

Uso: python make_tokens.py DESIGN.md <dir de salida>
El DESIGN.md debe tener frontmatter YAML con colors (incluida variante dark),
fonts y radius — ver el contrato en references/tokens.md.
"""

import json
import logging
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

SEMANTICOS = ["bg", "surface", "text", "text-muted", "accent", "accent-2", "line"]


def parse_frontmatter(md: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", md, re.DOTALL)
    if not m:
        sys.exit("ERROR: el DESIGN.md no tiene frontmatter YAML (--- ... ---).")
    try:
        import yaml

        return yaml.safe_load(m.group(1))
    except ImportError:
        sys.exit("ERROR: falta PyYAML (pip install pyyaml).")


def validar(meta: dict) -> None:
    colors = meta.get("colors") or {}
    faltan = [k for k in SEMANTICOS if k not in colors]
    if faltan:
        sys.exit(f"ERROR: faltan tokens de color: {faltan}")
    dark = colors.get("dark") or {}
    faltan_dark = [k for k in SEMANTICOS if k not in dark]
    if faltan_dark:
        sys.exit(f"ERROR: faltan tokens en la variante dark: {faltan_dark}")
    fonts = meta.get("fonts") or {}
    for k in ["display", "body", "import"]:
        if k not in fonts:
            sys.exit(f"ERROR: falta fonts.{k} en DESIGN.md")


def css_tokens(meta: dict) -> str:
    c, f = meta["colors"], meta["fonts"]
    radius = meta.get("radius", "12px")
    lineas_luz = "\n".join(f"  --color-{k}: {c[k]};" for k in SEMANTICOS)
    lineas_dark = "\n".join(f"  --color-{k}: {c['dark'][k]};" for k in SEMANTICOS)
    return f"""/* Generado por make_tokens.py — NO editar a mano; editar DESIGN.md. */
@import url('{f["import"]}');

@theme {{
{lineas_luz}
  --font-display: '{f["display"]}', serif;
  --font-body: '{f["body"]}', sans-serif;
  --font-mono: '{f.get("mono", "monospace")}', monospace;
  --radius-base: {radius};
}}

/* Variante oscura: <html data-theme="dark"> */
[data-theme='dark'] {{
{lineas_dark}
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme='light']) {{
{lineas_dark}
  }}
}}
"""


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    design = Path(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    meta = parse_frontmatter(design.read_text(encoding="utf-8"))
    validar(meta)
    (outdir / "tokens.css").write_text(css_tokens(meta), encoding="utf-8")
    (outdir / "tokens.json").write_text(
        json.dumps(
            {
                "colors": meta["colors"],
                "fonts": meta["fonts"],
                "radius": meta.get("radius", "12px"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    log.info("Tokens escritos en %s (tokens.css + tokens.json)", outdir)


if __name__ == "__main__":
    main()
