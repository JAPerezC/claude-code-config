#!/usr/bin/env bash
# SessionStart (matcher "compact"): tras compactar, vuelve a inyectar el estado
# que el resumen suele perder. Lo que se imprime en stdout entra como contexto.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
cd "$dir" 2>/dev/null || exit 0

if [ -f PROGRESS.md ]; then
  echo "## PROGRESS.md (estado guardado antes de compactar)"
  head -n 60 PROGRESS.md
  echo
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "## Git: $(git branch --show-current 2>/dev/null)"
  git log --oneline -5 2>/dev/null
  changed=$(git status --porcelain 2>/dev/null | head -n 30)
  if [ -n "$changed" ]; then
    echo "Archivos con cambios sin commitear:"
    echo "$changed"
  fi
fi
exit 0
