---
name: init-proyecto
description: Inicializar un nuevo proyecto con la estructura estandar, .gitignore, .env.example, .envrc y README
argument-hint: nombre-del-proyecto
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob
---

Crear un nuevo proyecto con nombre `$ARGUMENTS` siguiendo la estructura estandar.

1. Crear la estructura de directorios:
   ```
   $ARGUMENTS/
   ├── .claude/rules/
   ├── docs/
   ├── infra/
   ├── notebooks/
   ├── pipelines/
   ├── reports/
   ├── sql/
   ├── src/
   ├── triage/
   ├── data/raw/
   └── data/processed/
   ```

2. Crear archivos base usando los templates en @~/.claude/templates/gitignore-template.md y @~/.claude/templates/project-base-files.md

3. Crear `.gitignore` robusto con el template

4. Crear `.env.example`, `.envrc`, `README.md`, `requirements.txt` vacios

5. Crear `CLAUDE.md` de proyecto con seccion de arquitectura vacia para llenar

6. Inicializar git: `git init`

7. Poner `.gitkeep` en carpetas vacias para preservar estructura

8. Mostrar resumen de lo creado
