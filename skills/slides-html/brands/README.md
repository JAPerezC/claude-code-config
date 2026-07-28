# Brand packs (excluidos del repo público)

Esta carpeta contiene los sistemas de marca que la skill aplica en modo
institucional. Los packs reales (logos, paletas y reglas de una institución)
son material privado y **no se publican** en este repo — igual que
`settings.json` o `memory/`.

## Cómo crear un brand pack

Cada marca vive en `brands/<slug>/` con tres piezas:

```
brands/<slug>/
  design.md    # sistema completo: frontmatter YAML con colors/typography/
               # layout/logos/componentes/motion + guía de aplicación en prosa
  preview.md   # ficha ligera de preselección: slug, mood, formalidad,
               # cuándo usarla y cuándo NO
  logos/       # PNG/SVG de la marca (variantes para fondo claro/oscuro)
```

El formato de `design.md` sigue el patrón de los `design.md` del
bold-template-pack de frontend-slides (tokens YAML + prosa): así el modelo
aplica la marca en vez de improvisarla. Reglas que conviene incluir siempre:

- Qué variante de logo va sobre qué fondo, y sus posiciones exactas.
- Paleta cerrada ("la variedad sale del layout, no del color").
- Perfil de motion permitido (sobrio para marcas institucionales).
- Una sección "anti-derrape" con lo que NUNCA se hace con esa marca.

Después, en `SKILL.md`, se añade el gatillo del modo institucional
correspondiente en la Fase 0.
