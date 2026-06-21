---
name: git-pr
description: Crear un Pull Request completo - commit con conventional commits, push a branch, crear PR con descripcion
argument-hint: descripcion breve del cambio
disable-model-invocation: true
allowed-tools: Read, Bash, Grep, Glob
---

Crear un PR para: `$ARGUMENTS`

## Flujo:

### 1. Revisar cambios
- `git status` y `git diff` para ver todo lo modificado
- Verificar que NO hay secretos, .env, ni archivos de sistema

### 2. Preparar commit
- Agrupar archivos relacionados
- Proponer mensaje Conventional Commits: `tipo(scope): descripcion`
- **MOSTRAR el diff y mensaje al usuario y ESPERAR aprobacion**

### 3. Crear branch (si estamos en main/master)
- Nombre: `feat/descripcion-corta` o `fix/descripcion-corta`
- **Consultar al usuario antes de crear**

### 4. Push
- `git push -u origin nombre-branch`
- **Consultar al usuario antes de push**

### 5. Crear PR
- Titulo corto (<70 chars)
- Body con: Summary (bullets), Test plan (checklist)
- Usar `gh pr create`

### 6. Reportar
- Mostrar URL del PR al usuario
