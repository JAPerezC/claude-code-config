---
description: Cerrar sesión con snapshot completo del estado del proyecto y handoff de continuidad
---

Ejecutar el skill session-closer para crear un handoff completo de sesión.

## Contexto Disponible

Estás ejecutándote en el contexto de la conversación PRINCIPAL. Tienes acceso a:
- Todo lo discutido esta sesión
- Todas las decisiones tomadas y su justificación
- Todos los archivos creados o modificados
- Todos los problemas resueltos y enfoques probados
- Los objetivos del usuario y próximos pasos

## Proceso

Sigue las instrucciones del skill session-closer para:

### 1. Pre-flight
- Verificar permisos de escritura
- Detectar nombre del proyecto
- Escaneo de seguridad para secretos

### 2. Recopilar Contenido de la Sesión (desde TU memoria de la conversación)

Poblar estas secciones basándote en lo que observaste:

**Delta de Visión del Arquitecto**:
- ¿Qué insights emergieron esta sesión?
- ¿Algún pivot o cambio de alcance?

**Problemas Resueltos**:
- Listar cada par problema → solución de esta sesión

**Decisiones Tomadas**:
- Documentar decisiones A vs B con justificación

**Ideas Exploradas/Rechazadas**:
- ¿Qué se intentó pero no funcionó?

**Checklist Próxima Sesión**:
- ¿Con qué debería empezar la próxima sesión?

### 3. Escribir Archivos
Ejecutar todas las operaciones de archivos autónomamente:
- `docs/[PROYECTO]-session-summary.org` — prepend nueva sesión
- `TODO.org` — actualizar tareas
- `GIT_REMOTE` — capturar estado de git
- `.gitignore` — asegurar que archivos de handoff estén excluidos

**NO escribir historial de sesión en CLAUDE.md.** El historial vive exclusivamente
en `docs/[PROYECTO]-session-summary.org`. CLAUDE.md contiene solo instrucciones
del proyecto y arquitectura — nunca logs de sesión.

### 4. Validar y Reportar
- Verificar que todos los archivos se escribieron
- Verificar límites de tamaño
- Presentar resumen con commit propuesto

## Modo de Ejecución

- **Autónomo**: Sin prompts de permisos, ejecutar completamente
- **Idempotente**: Seguro ejecutar múltiples veces
- **Sin git push**: Solo operaciones locales

## Notas del Usuario

Si el usuario proporcionó notas específicas sobre esta sesión:

$ARGUMENTS
