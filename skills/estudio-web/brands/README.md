# Brand packs (excluidos del repo público)

En la versión local, esta carpeta contiene `<slug>.md` por cada marca
institucional que la skill puede aplicar en la Fase 0 (decisión A). Son
material privado (paletas, logos y reglas de instituciones reales) y **no se
publican** en este repo.

## Formato de un brand pack web

`brands/<slug>.md` contiene:

1. **Ámbito**: en qué proyectos aplica la marca y en cuáles está PROHIBIDA
   (los proyectos personales usan dirección de arte propia, nunca la marca
   por defecto).
2. **DESIGN.md institucional listo para usar**: el bloque YAML completo de
   colores semánticos (con variante dark derivada y validada con
   `scripts/validate_palette.py`), fuentes e import.
3. **Logos**: rutas de los archivos, variante por fondo, posición en header/
   footer, y la regla de copiarlos a `public/`/`static/` del proyecto.
4. **Reglas de aplicación**: componentes heredados de la marca, perfil de
   motion, y las excepciones explícitas al anti-slop (p. ej. si la marca
   OBLIGA una tipografía que normalmente estaría prohibida).
