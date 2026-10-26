#!/usr/bin/env python3
"""Status line para Claude Code.

Muestra: modelo · contexto (barra + tokens) · margen hasta la autocompactación ·
proyecto [rama] · líneas · duración · límites del plan (5 h / 7 días) o costo.

Usa los campos que Claude Code ya calcula (context_window.used_percentage,
rate_limits.*) y cae a cálculos propios si faltan (versiones antiguas).
"""

import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[97m"


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print("Claude Code")
        return

    model_id = _get(data, "model.id", "")
    model_display = _get(data, "model.display_name", "Claude")
    context_size = int(_get(data, "context_window.context_window_size", 200_000) or 200_000)
    current_tokens = _current_tokens(_get(data, "context_window.current_usage"))
    used_pct = _get(data, "context_window.used_percentage")
    if used_pct is None:
        used_pct = current_tokens * 100 / context_size if context_size else 0
    used_pct = int(round(float(used_pct)))

    # Margen hasta la autocompactación: con autoCompactWindow (o la variable
    # equivalente) la compactación ocurre mucho antes del 100 % de la ventana.
    compact_at = _compact_threshold(context_size)
    tokens_left = max(0, compact_at - current_tokens)

    current_dir = _get(data, "workspace.current_dir") or _get(data, "cwd") or os.getcwd()
    project_dir = _get(data, "workspace.project_dir") or current_dir
    project_name = os.path.basename(project_dir.rstrip("/")) or "~"

    m = re.search(r"(\d+)-(\d+)", model_id)
    version = f"{m.group(1)}.{m.group(2)}" if m else ""
    model_label = model_display if not version or version in model_display else f"{model_display} {version}"

    parts = [f"{BOLD}{CYAN}{model_label}{RESET}"]
    parts.append(f"{_color(used_pct, 50, 75)}{_bar(used_pct)} {used_pct}%{RESET}")
    left_pct = tokens_left * 100 // compact_at if compact_at else 0
    parts.append(f"{_color(100 - left_pct, 70, 90)}{_fmt_tokens(tokens_left)} hasta compactar{RESET}")

    git = _git_info(current_dir)
    parts.append(f"{BLUE}{project_name}{RESET}" + (f" {MAGENTA}[{git}]{RESET}" if git else ""))

    added = int(_get(data, "cost.total_lines_added", 0) or 0)
    removed = int(_get(data, "cost.total_lines_removed", 0) or 0)
    parts.append(f"{GREEN}+{added}{RESET}/{RED}-{removed}{RESET}")
    parts.append(f"{DIM}{_fmt_duration(int(_get(data, 'cost.total_duration_ms', 0) or 0))}{RESET}")

    # Suscripción: rate_limits existe → mostrar uso del plan. API: costo.
    five_h = _get(data, "rate_limits.five_hour.used_percentage")
    seven_d = _get(data, "rate_limits.seven_day.used_percentage")
    if five_h is not None or seven_d is not None:
        seg = []
        if five_h is not None:
            seg.append(f"{_color(float(five_h), 60, 85)}5h {int(float(five_h))}%{RESET}")
        if seven_d is not None:
            seg.append(f"{_color(float(seven_d), 60, 85)}7d {int(float(seven_d))}%{RESET}")
        parts.append(" ".join(seg))
    else:
        cost = _get(data, "cost.total_cost_usd")
        try:
            parts.append(f"{BOLD}{WHITE}${float(cost):.2f}{RESET}")
        except (TypeError, ValueError):
            pass

    print(f" {DIM}|{RESET} ".join(parts))


def _current_tokens(usage):
    if not isinstance(usage, dict):
        return 0
    return sum(
        int(usage.get(k, 0) or 0)
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )


def _compact_threshold(context_size):
    """Tokens a los que se autocompacta: autoCompactWindow > env > ventana."""
    window = os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if not window:
        window = _settings_value("autoCompactWindow")
    try:
        threshold = min(int(window), context_size)
    except (TypeError, ValueError):
        threshold = context_size
    pct = os.environ.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")
    if pct and pct.isdigit():
        threshold = min(threshold, context_size * int(pct) // 100)
    return threshold


def _settings_value(key):
    path = os.path.join(
        os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude")), "settings.json"
    )
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh).get(key)
    except (OSError, ValueError):
        return None


def _color(pct, warn, crit):
    return GREEN if pct < warn else YELLOW if pct < crit else RED


def _bar(pct, width=10):
    filled = max(0, min(width, int(pct) * width // 100))
    return "█" * filled + "░" * (width - filled)


def _fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n // 1000}k"
    return str(n)


def _fmt_duration(ms):
    s = ms // 1000
    m, h = s // 60, s // 3600
    if h:
        return f"{h}h{m % 60}m"
    if m:
        return f"{m}m{s % 60}s"
    return f"{s}s"


def _get(d, path, default=None):
    """Navegar dict anidado con path separado por puntos."""
    current = d
    for k in path.split("."):
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current if current is not None else default


def _git_info(cwd):
    """Rama + '*' si hay cambios, en el directorio de la sesión (no el del proceso)."""
    try:
        branch = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
        )
        name = branch.stdout.strip()
        if branch.returncode != 0 or not name:
            return ""
        dirty = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain", "-uno"],
            capture_output=True, text=True, timeout=2,
        )
        return f"{name}*" if dirty.stdout.strip() else name
    except Exception:
        return ""


if __name__ == "__main__":
    main()
