#!/usr/bin/env bash
# Instala esta configuración de Claude Code (Linux/macOS).
#
#   bash install.sh            dotfiles + settings + plugins del marketplace
#   bash install.sh --local    igual, pero registra el marketplace desde esta
#                              carpeta (para probar cambios sin hacer push)
#   bash install.sh --dry-run  muestra qué haría sin tocar nada
#
# Qué hace:
#   1. Copia statusline.py, convos.py y hooks/ a ~/.claude (respalda lo existente).
#   2. Instala ~/.claude/CLAUDE.md solo si no existe (si existe, deja CLAUDE.md.repo).
#   3. Fusiona dotfiles/settings.template.json con ~/.claude/settings.json
#      (lo local gana en claves sueltas; los hooks del repo se añaden).
#   4. Registra el marketplace jorge-skills e instala sus plugins + los oficiales
#      recomendados (context7, pyright-lsp).
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TS="$(date +%Y%m%d-%H%M%S)"
LOCAL=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --local) LOCAL=1 ;;
    --dry-run) DRY=1 ;;
    *) echo "Opción desconocida: $arg" >&2; exit 1 ;;
  esac
done

PLUGINS_PROPIOS="sesion datos academico diseno dev scraper"
PLUGINS_OFICIALES="context7 pyright-lsp"

run() { if [ "$DRY" = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi; }
need() { command -v "$1" >/dev/null || { echo "Falta '$1' en el PATH." >&2; exit 1; }; }
need jq
need python3

echo "Instalando en: $DEST"
run mkdir -p "$DEST/hooks"

# --- 1. dotfiles -------------------------------------------------------------
for f in statusline.py convos.py; do
  [ -e "$DEST/$f" ] && run cp "$DEST/$f" "$DEST/$f.bak-$TS"
  run install -m 755 "$SRC/dotfiles/$f" "$DEST/$f"
done
for f in "$SRC"/dotfiles/hooks/*; do
  name="$(basename "$f")"
  [ "$name" = "stop-verify.sh" ] && continue   # plantilla por proyecto, no global
  [ -e "$DEST/hooks/$name" ] && run cp "$DEST/hooks/$name" "$DEST/hooks/$name.bak-$TS"
  run install -m 755 "$f" "$DEST/hooks/$name"
done
echo "  dotfiles: statusline.py, convos.py, hooks/"

# --- 2. CLAUDE.md global ------------------------------------------------------
if [ -e "$DEST/CLAUDE.md" ]; then
  run cp "$SRC/dotfiles/CLAUDE.md" "$DEST/CLAUDE.md.repo"
  echo "  CLAUDE.md ya existe: dejé la versión del repo en CLAUDE.md.repo para comparar."
else
  run cp "$SRC/dotfiles/CLAUDE.md" "$DEST/CLAUDE.md"
  echo "  CLAUDE.md global instalado."
fi

# --- 3. settings.json ---------------------------------------------------------
SETTINGS="$DEST/settings.json"
TEMPLATE="$SRC/dotfiles/settings.template.json"
if [ -e "$SETTINGS" ]; then CUR="$(cat "$SETTINGS")"; else CUR='{}'; fi
# Fusión: template * local (lo local gana), pero los arrays de hooks y de
# permissions.deny se unen sin duplicados en lugar de reemplazarse.
MERGED="$(jq -n --argjson t "$(cat "$TEMPLATE")" --argjson l "$CUR" '
  ($t * $l)
  | .hooks = (reduce ((($t.hooks // {}) | keys) + (($l.hooks // {}) | keys) | unique)[] as $ev
      ({}; .[$ev] = ((($t.hooks[$ev] // []) + ($l.hooks[$ev] // [])) | unique)))
  | .permissions.deny = ((($t.permissions.deny // []) + ($l.permissions.deny // [])) | unique)
')"
# Con --local el marketplace apunta a esta carpeta; no declarar a la vez el de GitHub.
[ "$LOCAL" = 1 ] && MERGED="$(jq 'del(.extraKnownMarketplaces["jorge-skills"])' <<<"$MERGED")"
if [ "$DRY" = 1 ]; then
  echo "  [dry-run] settings.json quedaría:"; echo "$MERGED" | sed 's/^/    /'
else
  [ -e "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak-$TS"
  printf '%s\n' "$MERGED" > "$SETTINGS"
  echo "  settings.json fusionado (respaldo: settings.json.bak-$TS)"
fi

# --- 4. plugins -----------------------------------------------------------------
if ! command -v claude >/dev/null; then
  echo "  'claude' no está en el PATH: omito la instalación de plugins."
else
  if [ "$LOCAL" = 1 ]; then MK_SRC="$SRC"; else MK_SRC="JAPerezC/claude-code-config"; fi
  run claude plugin marketplace add "$MK_SRC" || true
  run claude plugin marketplace update jorge-skills || true
  for p in $PLUGINS_PROPIOS; do
    run claude plugin install "$p@jorge-skills" --scope user || echo "  aviso: no se pudo instalar $p"
  done
  for p in $PLUGINS_OFICIALES; do
    run claude plugin install "$p@claude-plugins-official" --scope user || echo "  aviso: no se pudo instalar $p"
  done
  command -v pyright-langserver >/dev/null || \
    echo "  pyright-lsp necesita el binario: uv tool install pyright"
fi

# --- 5. skill externa (manim), fijada por commit ------------------------------
MANIM_SHA="e2cdc1e9f5d2f39392cdafd30b2b04b31b673d60"
if [ ! -d "$DEST/skills/manim-skill" ] && [ "${INSTALL_MANIM:-0}" = 1 ]; then
  run git clone -q https://github.com/awesome-skills/manim-skill "$DEST/skills/manim-skill"
  run git -C "$DEST/skills/manim-skill" checkout -q "$MANIM_SHA"
  echo "  manim-skill instalada en el commit ${MANIM_SHA:0:7}"
fi

echo
echo "Listo. Reinicia Claude Code y comprueba con /status, /hooks y /plugin."
echo "Las skills con scripts ejecutan código: revísalas antes de confiar en ellas."
