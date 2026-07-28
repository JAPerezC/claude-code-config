# Scrollytelling

Destilado de `reports/investigacion-web-dashboards.md` §2 y §3.5. Versiones
verificadas contra fuentes primarias el 28-jul-2026.

---

## El patrón: pasos + gráfico sticky

Patrón dominante, **codificado por The Pudding**: columna de pasos de texto +
gráfico con `position: sticky`, y detección de qué paso está activo con
**IntersectionObserver**.

Estructura mínima:

```
<section class="scrolly">
  <figure class="sticky">   <!-- el gráfico, se queda fijo -->
  <div class="steps">       <!-- pasos; cada uno emite un índice al entrar -->
</section>
```

El componente de referencia es `Scrolly.svelte` del
**`the-pudding/svelte-starter`** (MIT, push 2-jul-2026), cuyo `package.json`
declara: Svelte ^5.55.9, SvelteKit ^2.60.1, d3 ^7.9.0, Style Dictionary ^5.4.1,
`adapter-static`, ArchieML (CMS sobre Google Docs). Otra implementación abierta
citada: `ONSvisual/svelte-scrolly`.

Stack recomendado por el informe: **SvelteKit 2 + Svelte 5 + `adapter-static`**,
LayerCake 10 o D3 7 para el gráfico, tokens compartidos con el resto del sitio.

---

## Qué mecanismo usar

### 1. IntersectionObserver / Scrollama — pasos discretos (defecto)

- **Cuándo:** el gráfico cambia de **estado** en cada paso (nueva serie, nuevo
  filtro, resaltado). Es el 90 % de los casos.
- **Scrollama 3.2.0** (MIT): última publicación en npm el **17-jun-2022**, pero
  el repo tiene pushes hasta **nov-2025** y 5.989 estrellas. El informe lo
  califica de **mantenimiento mínimo, no abandono**: estable y suficiente. Para
  React, `react-scrollama` 2.4.2.
- En Svelte suele bastar el `Scrolly.svelte` del starter (IntersectionObserver a
  pelo), sin dependencia extra.

### 2. GSAP ScrollTrigger — cuando la animación *es* la historia

- **Cuándo:** pin + scrub, es decir, la animación avanza **proporcionalmente al
  scroll** en vez de saltar entre estados. Piezas cinematográficas.
- **GSAP 3.15.0**: **100 % gratuito con todos los plugins** (ScrollTrigger,
  SplitText, MorphSVG) desde 3.13 (anuncio oficial 29-abr-2025; adquisición por
  Webflow en oct-2024).
- **Licencia:** "Standard no-charge", **propietaria, no OSI**. Gratuita incluso
  para uso comercial; irrelevante para sitios propios, pero decláralo si el
  cliente audita licencias.

### 3. CSS scroll-driven animations — solo mejora progresiva

- **Estado a jul-2026:** Chrome/Edge 115+, Safari 26+. **Firefox estable (153)
  todavía las tiene tras el flag** `layout.css.scroll-driven-animations.enabled`;
  caniuse las lista desde Firefox 155 (previsto 1-sep-2026). Soporte global
  **83,66 %**. Prioridad Interop 2026.
- **Regla:** úsalas **solo dentro de `@supports`**, como mejora sobre una
  experiencia que ya funciona sin ellas. Nunca como mecanismo principal.

```css
@supports (animation-timeline: view()) {
  .reveal { animation: fade linear both; animation-timeline: view(); }
}
```

Dato relacionado: **View Transitions same-document** están en Baseline desde el
14-oct-2025; las cross-document **no tienen Firefox**.

---

## Reglas móvil (doctrina The Pudding)

- **Mantén el scrolly solo si las transiciones son significativas.** Si el
  gráfico apenas cambia entre pasos, **apila los pasos** y sirve un gráfico
  estático por paso.
- **Evita unidades `vh`**: las barras del navegador móvil cambian de alto y
  provocan saltos. Usa alturas de contenido, o unidades de viewport dinámicas
  verificadas antes de adoptarlas (el informe no las nombra).
- Un solo gráfico visible por pantalla; el texto no debe competir con él.

## prefers-reduced-motion

Requisito explícito del starter de The Pudding y del informe.

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

Con reduced-motion activo: el scrolly debe seguir **contando la historia**, no
solo dejar de moverse. Entrega el estado final de cada paso directamente. El
scaffold `scrolly-story` incluye además un `MotionToggle` explícito.

---

## Vía rápida 100 % Python (prototipos)

**Quarto + Closeread** (v1.0.1, 11-nov-2024): secciones, stickies y triggers con
highlight/zoom/pan, celdas Python, **sin escribir JavaScript**. Posit recibió 40
propuestas al Closeread Prize y premió 17 (1 Grand Prize, 5 Special Prizes, 11
Honorable Mentions, feb-2025).

Advertencias del informe: **no es el vehículo del diseño distintivo final**, y
la **licencia del repo no fue verificada** en la investigación. Otra vía:
Observable Framework tiene un ejemplo oficial de scrollytelling con
IntersectionObserver y data loaders en Python.

---

## Errores comunes

Los dos primeros están documentados en el informe; el resto son *[derivados]* de
sus datos, no una lista del informe.

1. **Usar `vh` en móvil** -> saltos por las barras del navegador. (informe)
2. **Mantener el scrolly cuando las transiciones no son significativas** ->
   scroll largo que no aporta; apilar. (informe)
3. *[derivado]* Depender de CSS scroll-driven animations sin `@supports` ->
   roto para el ~16 % de usuarios y para Firefox estable.
4. *[derivado]* Asumir que Scrollama está abandonado por la fecha de npm
   (2022): el repo sigue con pushes hasta nov-2025.
5. *[derivado]* No entregar contenido con `prefers-reduced-motion: reduce`:
   desactivar la animación no puede equivaler a perder la información.
6. *[derivado]* Usar GSAP para pasos discretos: ScrollTrigger es para pin+scrub;
   para cambios de estado sobra con IntersectionObserver.
7. *[derivado]* Recalcular el gráfico entero en cada paso en vez de transicionar
   entre estados; en Svelte, aprovechar las transiciones del lenguaje.

## Checklist antes de publicar

- [ ] Funciona con JavaScript lento: el primer paso se ve sin esperar.
- [ ] Cada paso tiene un cambio visible y significativo en el gráfico.
- [ ] Móvil probado: sin `vh`, o pasos apilados si las transiciones no valen.
- [ ] `prefers-reduced-motion` entrega la historia completa.
- [ ] El gráfico consume los mismos tokens que el resto del sitio.
- [ ] Deploy estático con `adapter-static` (y `paths.base` si es GitHub Pages).
