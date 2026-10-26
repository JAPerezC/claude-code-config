#!/usr/bin/env bash
# Stop hook OPCIONAL, por proyecto: no deja terminar a Claude si hay cambios y
# los tests fallan. Copiar a <proyecto>/.claude/hooks/ y registrar en
# <proyecto>/.claude/settings.json:
#   "hooks": {"Stop": [{"hooks": [{"type": "command",
#     "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop-verify.sh"}]}]}
# Ajusta TEST_CMD al proyecto (por defecto pytest vía uv).
TEST_CMD="${TEST_CMD:-uv run pytest -q -x}"

input=$(cat)
# Evita bucles: si ya estamos continuando por este hook, dejar terminar.
[ "$(jq -r '.stop_hook_active // false' <<<"$input")" = "true" ] && exit 0
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
# Sin cambios en el árbol de trabajo no hay nada que verificar.
git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null && exit 0

if ! out=$($TEST_CMD 2>&1); then
  printf 'Los tests fallan; arregla la causa raíz (sin editar los tests) antes de terminar:\n%s\n' \
    "$(tail -n 40 <<<"$out")" >&2
  exit 2
fi
exit 0
