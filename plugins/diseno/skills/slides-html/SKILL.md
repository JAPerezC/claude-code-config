---
name: slides-html
description: >
  Crear presentaciones HTML animadas y autocontenidas (un solo archivo, sin
  dependencias) con dos modos: INSTITUCIONAL con la marca CCD/EGTP/Tec de
  Monterrey (logos y colores oficiales), o PERSONAL con estilos curados no
  genéricos. Triggers: "presentación dinámica", "presentación HTML",
  "presentación animada", "deck interactivo", "presentación institucional",
  "presentación del CCD/Tec/EGTP", "slides para el trabajo". Para decks
  rápidos Markdown→PDF/PPTX usar marp-deck en su lugar.
when_to_use: Cuando se pide una presentación que se proyecta o comparte como HTML (animada, interactiva o con marca). No para .pptx editables (usar la skill pptx).
allowed-tools: Read, Write, Edit, Bash, Glob
effort: high
---

# Slides HTML — presentaciones animadas con y sin marca institucional

Crea presentaciones HTML sin dependencias: un solo archivo con CSS/JS inline
que corre por completo en el navegador. Motor basado en frontend-slides
(MIT, ver ATTRIBUTION.md) con brand packs propios.

Todo el contenido generado va en español con ortografía correcta (acentos,
¿?, ¡!) salvo que el usuario pida otro idioma.

## Principios (heredados del motor, NO negociables)

1. **Cero dependencias** — un solo archivo HTML autocontenido.
2. **Stage fijo 16:9** — lienzo de 1920×1080 escalado uniforme al viewport;
   nunca reflow por dispositivo. Incluir `viewport-base.css` COMPLETO en cada
   deck. Visibilidad de slides solo con `.active`/`.visible` (visibility +
   opacity + pointer-events), jamás `display: none`.
3. **Mostrar, no preguntar** — previews visuales reales, no opciones abstractas.
4. **Nada de diseño genérico** — cada deck debe sentirse hecho a medida.
5. **Revelación progresiva** — leer solo los archivos de la fase en curso.
6. `prefers-reduced-motion` siempre; nunca negar funciones CSS directamente
   (usar `calc(-1 * clamp(...))`).

---

## Fase 0: Detectar modo

**Modo I — Institucional (CCD/EGTP/Tec).** Gatillos: el usuario menciona
"institucional", "CCD", "EGTP", "Tec", "Escuela de Gobierno", "para el
trabajo", una contraparte institucional , o el deck es claramente
laboral. → Flujo institucional (abajo).

**Modo P — Personal.** Todo lo demás: charlas propias, side projects, clases
propias, portafolio. → Flujo personal.

**Variantes por tipo de contenido** (se combinan con el modo I o P):
- **Técnica con código en vivo** (charla de programación, demo de API): si
  hacen falta resaltado con transiciones de código, Monaco o v-click, usar
  Slidev en lugar de este motor (skill oficial:
  `npx skills add https://github.com/slidevjs/slidev --skill slidev`).
  Avisar al usuario del cambio de stack en una frase.
- **Historia de datos** (resultados de un análisis): 5-7 *beats*, uno por
  hallazgo, cada uno con su gráfico; los gráficos heredan las variables
  `:root` del deck (mismos colores y fuentes). El scroll/animación solo si
  reduce el esfuerzo de leer el dato; si no, una slide estática por beat.
  Si el usuario quiere scrollytelling web en vez de deck → skill `estudio-web`
  (scaffold scrolly).

**Conversión/mejora.** Si el usuario trae un HTML existente para mejorar:
leerlo, identificar su modo por los colores/logos, y aplicar las reglas de
modificación: contar elementos contra los límites de densidad ANTES de agregar
contenido; si algo excede, dividir la slide; tras CUALQUIER edición verificar
overflow, solapes y 16:9 con captura de pantalla.

En ambos modos, preguntar juntas (en un solo mensaje o con la UI de preguntas
estructuradas si está disponible):
1. **Propósito** — ¿pitch, clase, conferencia, reporte interno?
2. **Extensión** — ¿5-10, 10-20, 20+ slides?
3. **Contenido** — ¿listo, notas sueltas, solo el tema?
4. **Densidad** — ¿deck para hablar (pocas palabras, 1-3 bullets) o para leer
   (autocontenido, 4-8 bullets o 4-6 cards)?

Si hay imágenes: inspeccionarlas, evaluar cuáles son usables y co-diseñar el
guion con ellas desde el inicio (no "planear y luego pegar imágenes").

---

## Fase 1-I: Flujo INSTITUCIONAL

1. Leer `brands/ccd/design.md` — es la receta completa y OBLIGATORIA: paleta
   fija, Open Sans + Roboto Slab, componentes (cards, KPIs, badges, quote,
   tabla, tags), logos en esquinas y motion sobrio.
2. La marca NO se negocia: nada de cambiar colores o tipografías. La variedad
   sale del layout y del ritmo, no del color.
3. Generar **2 previews de una slide** (no 3): ambos dentro de la marca —
   - **Clásico**: réplica fiel del estilo de los decks Marp existentes
     (portada navy + slide de cards).
   - **Dinámico**: misma marca, pero con motion escalonado, KPIs con count-up
     y transiciones entre slides más cinemáticas (dentro del perfil sobrio).
   Guardarlos en `.slides-html/previews/` y abrirlos en el navegador.
4. Logos: incrustar en base64 (instrucciones en design.md). Variantes _white
   sobre navy, _navy sobre claro. Nunca omitirlos salvo petición explícita.
5. Tras la elección, generar el deck completo (Fase 2).

## Fase 1-P: Flujo PERSONAL

1. Leer `STYLE_PRESETS.md` (12 presets curados). Si existe
   `~/.claude/skills/frontend-slides/bold-template-pack/selection-index.json`
   (paquete original instalado), leer también ese índice y usar sus
   `preview.md` para candidatos audaces — sin leer ningún `design.md` todavía.
2. Generar **3 previews de una slide**: 1 preset seguro + 1 audaz (del pack si
   está instalado, si no un segundo preset con tratamiento valiente) + 1
   comodín diseñado a medida para el contexto.
3. Reglas anti-genérico para el comodín: tipografía con carácter (Fontshare/
   Google Fonts — nunca Inter/Roboto/Arial/system), paleta comprometida con
   acentos duros, una tesis visual reconocible, motion de alto impacto en un
   momento (carga con reveals escalonados). Prohibido: gradiente morado sobre
   blanco, glassmorphism genérico, layouts de plantilla.
4. Autenticidad de previews: deben verse como la primera slide REAL del deck
   del usuario — jamás renderizar "Opción A", nombres de template, rutas o
   notas de requisitos sobre la slide.
5. Tras la elección, generar el deck completo (Fase 2).

---

## Fase 2: Generar el deck

Antes de generar, leer: `html-template.md` (arquitectura y JS),
`viewport-base.css` (copiar ÍNTEGRO al `<style>`) y `animation-patterns.md`
(elegir el perfil de motion según el modo: institucional →
Professional/Corporate; personal → el que pida la estética elegida).

- Un solo archivo HTML autocontenido, comentado por secciones
  (`/* === NOMBRE === */`).
- Aplicar la densidad elegida en TODO el deck; si una slide se desborda,
  dividirla — nunca encoger la tipografía hasta lo ilegible.
- Navegación: flechas, espacio, swipe; edición inline (tecla E, Ctrl+S) salvo
  que pidan archivo bloqueado.
- Estructura institucional canónica: portada `.lead` → contenido → cierre
  `.closing` (ver anatomía en design.md).

**Verificación obligatoria** tras generar: capturar las slides más densas con
la CLI de Playwright (`npx -y playwright screenshot --viewport-size=1920,1080
"file://$PWD/<archivo.html>?static#<n>" slide-<n>.png`) o, si no hay Node,
Chromium headless (`chromium --headless=new --disable-gpu --window-size=1920,1080
--screenshot=slide-<n>.png "file://$PWD/<archivo.html>?static#<n>"`), y
revisar las capturas con Read: sin overflow, sin solapes de paneles, sin texto fuera de
su card. `scrollHeight` no basta: los paneles de un grid pueden taparse
visualmente entre sí. Lecciones incorporadas al motor:
- Incluir SIEMPRE el modo `?static` (clase `static` en `<html>` que fuerza los
  `.reveal` a opacidad 1 sin transición y los contadores a su valor final) —
  sin él, la captura headless sale a mitad de la animación.
- Los `.deck-controls` van en la esquina inferior DERECHA (`left: auto;
  right: 22px; transform: none;`), nunca centrados: centrados tapan la línea
  de fuente `.src` en slides con notas largas.
- La navegación soporta `#<índice>` en la URL para abrir una slide concreta
  (necesario para capturar slides individuales).

## Fase 3: Entrega

1. Borrar `.slides-html/previews/` si existe.
2. Abrir el HTML final en el navegador (`xdg-open archivo.html` en Linux, `open` en macOS).
3. Resumir: ubicación, estilo, número de slides, navegación, cómo personalizar
   (variables `:root`, link de fuentes, clase `.reveal`).
4. **PDF**: el deck imprime una slide por página gracias al bloque
   `@media print` de viewport-base.css — Ctrl+P → "Guardar como PDF" en el
   navegador, o sin interfaz:
   `chromium --headless=new --no-pdf-header-footer --print-to-pdf=deck.pdf "file://$PWD/<archivo.html>?static"`.
   El PDF pierde las animaciones; avisarlo si el deck depende de ellas.

---

## Archivos de soporte

| Archivo | Cuándo leerlo |
|---|---|
| `brands/ccd/design.md` | Fase 1-I (receta institucional completa) |
| `brands/ccd/preview.md` | Solo para preselección/diagnóstico |
| `brands/ccd/logos/*.png` | Fase 2 (incrustar en base64) |
| `STYLE_PRESETS.md` | Fase 1-P |
| `viewport-base.css` | Fase 2 (copiar íntegro) |
| `html-template.md` | Fase 2 |
| `animation-patterns.md` | Fase 2 |
| `ATTRIBUTION.md` | Créditos y cómo instalar el pack original de 34 templates |

Para agregar OTRA marca institucional en el futuro: crear
`brands/<slug>/design.md` + `preview.md` + `logos/` siguiendo el formato de
`brands/ccd/` y añadir su gatillo en la Fase 0.
