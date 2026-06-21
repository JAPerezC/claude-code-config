#!/usr/bin/env python3
"""Status line para Claude Code — modelo, contexto, tokens, git, líneas, duración, costo."""

import json
import os
import re
import subprocess
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        print("Claude Code")
        return

    # --- ANSI codes ---
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

    # --- Parse fields ---
    model_id = _get(data, "model.id", "unknown")
    model_display = _get(data, "model.display_name", "Claude")
    context_size = int(_get(data, "context_window.context_window_size", 200000))
    usage = _get(data, "context_window.current_usage", None)
    total_duration_ms = int(_get(data, "cost.total_duration_ms", 0))
    lines_added = int(_get(data, "cost.total_lines_added", 0))
    lines_removed = int(_get(data, "cost.total_lines_removed", 0))
    total_cost = _get(data, "cost.total_cost_usd", None)

    # Project name
    project_dir = _get(data, "workspace.project_dir", os.getcwd())
    project_name = os.path.basename(project_dir) if project_dir else "~"

    # Model version from id
    model_version = ""
    m = re.search(r"(\d+)-(\d+)", model_id)
    if m:
        model_version = f"{m.group(1)}.{m.group(2)}"

    # Max plan detection
    is_max_plan = context_size >= 1_000_000

    # Auto-compact threshold
    compact_threshold = int(os.environ.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "65"))

    # --- Context usage ---
    if usage and isinstance(usage, dict):
        input_tokens = int(usage.get("input_tokens", 0))
        cache_creation = int(usage.get("cache_creation_input_tokens", 0))
        cache_read = int(usage.get("cache_read_input_tokens", 0))
        current_tokens = input_tokens + cache_creation + cache_read
        context_percent = current_tokens * 100 // context_size if context_size else 0
        until_compact = max(0, compact_threshold - context_percent)
    else:
        current_tokens = 0
        context_percent = 0
        until_compact = compact_threshold

    # --- Helpers ---
    def fmt_tokens(n):
        if n >= 1_000_000:
            return f"{n // 1_000_000}M"
        if n >= 1000:
            return f"{n // 1000}k"
        return str(n)

    def fmt_duration(ms):
        s = ms // 1000
        m = s // 60
        h = m // 60
        if h > 0:
            return f"{h}h{m % 60}m"
        if m > 0:
            return f"{m}m{s % 60}s"
        return f"{s}s"

    def progress_bar(pct, width=10):
        filled = pct * width // 100
        return "\u2588" * filled + "\u2591" * (width - filled)

    # Context color
    if context_percent < 50:
        ctx_color = GREEN
    elif context_percent < 75:
        ctx_color = YELLOW
    else:
        ctx_color = RED

    # Until-compact color
    if until_compact > 20:
        compact_color = GREEN
    elif until_compact > 5:
        compact_color = YELLOW
    else:
        compact_color = RED

    # --- Model label ---
    if model_version and model_version not in model_display:
        model_label = f"{model_display} {model_version}"
    else:
        model_label = model_display

    # --- Build segments ---
    parts = []
    parts.append(f"{BOLD}{CYAN}{model_label}{RESET}")
    parts.append(
        f"{ctx_color}{progress_bar(context_percent)} {context_percent}%{RESET}"
    )
    parts.append(f"{compact_color}{until_compact}% left{RESET}")
    parts.append(f"{DIM}{fmt_tokens(current_tokens)}/{fmt_tokens(context_size)}{RESET}")

    # Project + git branch
    git_info = _git_info()
    if git_info:
        parts.append(f"{BLUE}{project_name}{RESET} {MAGENTA}[{git_info}]{RESET}")
    else:
        parts.append(f"{BLUE}{project_name}{RESET}")

    # Lines
    parts.append(f"{GREEN}+{lines_added}{RESET}/{RED}-{lines_removed}{RESET}")

    # Duration
    parts.append(f"{DIM}{fmt_duration(total_duration_ms)}{RESET}")

    # Cost or Max
    if is_max_plan:
        parts.append(f"{BOLD}{MAGENTA}Max{RESET}")
    elif total_cost is not None:
        try:
            cost_val = float(total_cost)
            parts.append(f"{BOLD}{WHITE}${cost_val:.2f}{RESET}")
        except (ValueError, TypeError):
            pass

    sep = f" {DIM}|{RESET} "
    print(sep.join(parts))


def _get(d, path, default=None):
    """Navegar dict anidado con path separado por puntos."""
    keys = path.split(".")
    current = d
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current if current is not None else default


def _git_info():
    """Obtener branch + indicador de cambios pendientes."""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if branch.returncode != 0 or not branch.stdout.strip():
            return ""
        name = branch.stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if dirty.stdout.strip():
            return f"{name}*"
        return name
    except Exception:
        return ""


if __name__ == "__main__":
    main()
