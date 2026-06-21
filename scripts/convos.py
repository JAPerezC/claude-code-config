#!/usr/bin/env python3
"""
Gestor de conversaciones de Claude Code.
Uso: python convos.py [list|archive|clean]
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_conversations(base_dir):
    """Encuentra todas las conversaciones en projects/."""
    convos = []
    projects_dir = Path(base_dir) / "projects"
    if not projects_dir.exists():
        return convos

    for proj in projects_dir.iterdir():
        if not proj.is_dir():
            continue
        for f in proj.glob("*.jsonl"):
            size_kb = f.stat().st_size / 1024
            mtime = f.stat().st_mtime
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

            first_msg = ""
            msg_count = 0
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        entry = json.loads(line.strip())
                        if not isinstance(entry, dict):
                            continue
                        if entry.get("type") in ("user", "assistant"):
                            msg_count += 1
                        if entry.get("type") == "user" and not first_msg:
                            msg = entry.get("message", {})
                            if isinstance(msg, dict):
                                content = msg.get("content", "")
                                if (
                                    isinstance(content, str)
                                    and len(content.strip()) > 10
                                ):
                                    first_msg = content.strip()[:70]
                                elif isinstance(content, list):
                                    for part in content:
                                        if (
                                            isinstance(part, dict)
                                            and part.get("type") == "text"
                                        ):
                                            t = part.get("text", "").strip()
                                            if len(t) > 10:
                                                first_msg = t[:70]
                                                break
                    except Exception:
                        continue

            proj_name = proj.name.replace("C--Users-jorge-", "").replace(
                "C--Users-jorge", "HOME"
            )
            convos.append(
                {
                    "path": f,
                    "project": proj_name[:20],
                    "date": date_str,
                    "mtime": mtime,
                    "msgs": msg_count,
                    "size_kb": size_kb,
                    "first_msg": first_msg or "(sin texto)",
                }
            )

    convos.sort(key=lambda x: x["mtime"], reverse=True)
    return convos


def list_convos(base_dir):
    convos = get_conversations(base_dir)
    if not convos:
        print("No hay conversaciones.")
        return

    print(
        f"\n{'#':>3} | {'Fecha':17s} | {'Proyecto':20s} | {'Msgs':>5s} | {'Tam':>8s} | Tema"
    )
    print("-" * 110)
    for i, c in enumerate(convos, 1):
        print(
            f"{i:3d} | {c['date']:17s} | {c['project']:20s} | {c['msgs']:5d} | {c['size_kb']:6.0f} KB | {c['first_msg']}"
        )

    # Archived count
    archive_dir = Path(base_dir) / "archive"
    if archive_dir.exists():
        archived = len(list(archive_dir.glob("*.jsonl")))
        print(f"\n  ({archived} conversaciones archivadas en ~/.claude/archive/)")


def archive_convos(base_dir, indices):
    convos = get_conversations(base_dir)
    archive_dir = Path(base_dir) / "archive"
    archive_dir.mkdir(exist_ok=True)

    for idx in indices:
        if idx < 1 or idx > len(convos):
            print(f"  Indice {idx} fuera de rango")
            continue
        c = convos[idx - 1]
        src = c["path"]
        dst = archive_dir / src.name
        shutil.move(str(src), str(dst))
        # Move subagents dir if exists
        sub = src.parent / src.stem
        if sub.is_dir():
            shutil.move(str(sub), str(archive_dir / src.stem))
        print(f"  Archivada #{idx}: {c['first_msg'][:50]}")


def clean_archive(base_dir):
    archive_dir = Path(base_dir) / "archive"
    if not archive_dir.exists():
        print("No hay archivo.")
        return
    files = list(archive_dir.glob("*.jsonl"))
    total_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
    print(f"\n  {len(files)} conversaciones archivadas ({total_mb:.1f} MB)")
    resp = input("  Borrar TODAS las archivadas? (s/N): ")
    if resp.lower() == "s":
        shutil.rmtree(str(archive_dir))
        archive_dir.mkdir()
        print("  Archivo limpiado.")
    else:
        print("  Cancelado.")


def archive_project(base_dir, project_dir, current_session_id=None):
    """Archiva todas las conversaciones de un proyecto excepto la sesion actual."""
    projects_dir = Path(base_dir) / "projects"
    archive_dir = Path(base_dir) / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Convertir CWD a nombre de directorio Claude
    # C:\Users\jorge\work\projects\mundial-2026 -> C--Users-jorge-work-projects-mundial-2026
    # Claude Code también convierte _ a - en los nombres
    project_path = Path(project_dir).resolve()
    path_str = str(project_path)
    path_str = path_str.replace("\\", "/").rstrip("/")
    encoded = path_str.replace(":/", "--").replace("/", "-")

    target_dir = projects_dir / encoded
    if not target_dir.exists():
        # Intentar con underscores convertidos a guiones (Claude Code lo hace)
        encoded_alt = encoded.replace("_", "-")
        target_alt = projects_dir / encoded_alt
        if target_alt.exists():
            target_dir = target_alt
        else:
            print(f"  No existe directorio de proyecto: {encoded}")
            if encoded != encoded_alt:
                print(f"  Tampoco con guiones: {encoded_alt}")
            return 0

    archived = 0
    for f in target_dir.glob("*.jsonl"):
        sid = f.stem
        if current_session_id and sid == current_session_id:
            continue  # No archivar la sesion actual
        dst = archive_dir / f.name
        shutil.move(str(f), str(dst))
        # Mover subdirectorio asociado si existe
        sub = target_dir / sid
        if sub.is_dir():
            shutil.move(str(sub), str(archive_dir / sid))
        archived += 1
        print(f"  Archivada: {sid[:12]}...")

    if archived == 0:
        print("  No habia conversaciones anteriores para archivar.")
    else:
        print(f"  Total archivadas: {archived}")
    return archived


def main():
    base_dir = Path.home() / ".claude"
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        list_convos(base_dir)
    elif sys.argv[1] == "archive":
        if len(sys.argv) < 3:
            print("Uso: convos archive 4 7 8  (numeros de conversacion)")
            return
        indices = [int(x) for x in sys.argv[2:]]
        archive_convos(base_dir, indices)
    elif sys.argv[1] == "archive-project":
        # Uso: convos archive-project <CWD> [session-id-actual]
        if len(sys.argv) < 3:
            print("Uso: convos archive-project <directorio> [session-id-a-excluir]")
            return
        project_dir = sys.argv[2]
        current_sid = sys.argv[3] if len(sys.argv) > 3 else None
        archive_project(base_dir, project_dir, current_sid)
    elif sys.argv[1] == "clean":
        clean_archive(base_dir)
    else:
        print("Uso: convos [list|archive N...|archive-project DIR [SID]|clean]")


if __name__ == "__main__":
    main()
