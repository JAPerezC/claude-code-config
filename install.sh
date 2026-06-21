#!/usr/bin/env bash
# Instala esta configuración en ~/.claude, respaldando lo existente.
# Uso:  bash install.sh [destino]   (destino por defecto: ~/.claude)
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$HOME/.claude}"
TS="$(date +%Y%m%d-%H%M%S)"

echo "Instalando config de Claude Code en: $DEST"
mkdir -p "$DEST"

ITEMS="statusline.py hooks commands agents skills skills-archive templates scripts"
for item in $ITEMS; do
  [ -e "$SRC/$item" ] || continue
  if [ -e "$DEST/$item" ]; then
    cp -r "$DEST/$item" "$DEST/$item.bak-$TS"
    echo "  backup: $item -> $item.bak-$TS"
  fi
  cp -r "$SRC/$item" "$DEST/"
  echo "  instalado: $item"
done

echo "Listo. Revisa $DEST/settings.json y reinicia Claude Code."
echo "Nota: las skills que traen scripts ejecutan código; revísalas antes de confiar."
