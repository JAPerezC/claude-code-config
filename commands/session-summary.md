Crear un resumen de sesión compatible con el formato del session-closer.

Genera un output que puede usarse directamente por el skill session-closer o capturarse manualmente.

## Formato de Salida

```org
* Sesión [FECHA]
:PROPERTIES:
:SESSION_DATE: [YYYY-MM-DD]
:SESSION_TIME: [HH:MM]
:TIMEZONE: America/Mexico_City
:PROJECT: [desde .project o detectado]
:BRANCH: [branch actual de git]
:END:

** Visión del Arquitecto (Delta desde la Última)

*Visión Central*: [Qué intenta lograr este proyecto]

*Aprendizajes e Insights*:
- [Insight clave de esta sesión]

*Ajustes a Objetivos*:
- [Pivots o cambios de alcance, o "Ninguno"]

** Esta Sesión

*Decisiones Estructurales*:
- [Decisiones arquitectónicas tomadas]

*Problemas Resueltos*:
1. [Problema] → [Solución]

*Decisiones Tomadas*:
- [Opción A vs B: elegí A porque...]

*Ideas Exploradas/Rechazadas*:
- [Idea]: [Por qué no funcionó]

** Cambios en Código

Archivos modificados:
- =ruta/al/archivo.py= — [descripción breve]

** Contexto Combinado

*Alineación con la Visión*: [Cómo esta sesión apoya los objetivos]

*Conflictos por Resolver*: [Tensiones o deuda técnica introducida]

*Evolución desde la Última*: [Cómo cambió el proyecto esta sesión]

** Checklist Próxima Sesión

- [ ] [Tarea de alta prioridad]
- [ ] [Investigación necesaria]
- [ ] [Seguimiento pendiente]

** Bloqueadores

[Listar bloqueadores, o "Ninguno"]
```

## Instrucciones

1. Revisar el historial de conversación de esta sesión
2. Identificar decisiones significativas, problemas resueltos, cambios de código e ideas rechazadas
3. Extraer TODOs y elementos de seguimiento
4. Formatear como org-mode válido

**NO escribir historial de sesión en CLAUDE.md.** CLAUDE.md es solo para instrucciones del proyecto. Todo el historial va a `docs/[PROYECTO]-session-summary.org`.
