# Scaffold: scrollytelling con SvelteKit 2 + Scrolly + LayerCake

Para narrativas visuales tipo The Pudding/FT: pasos de texto que avanzan
sobre un gráfico fijo (sticky) que transiciona.

## Comandos

Base idéntica a `sveltekit-dashboard.md` (sv create + tailwind + adapter-static
+ layercake/d3). Extra:

```bash
npm install gsap            # SOLO para piezas cinematográficas (ScrollTrigger)
```

## El patrón steps + sticky

Componente `Scrolly.svelte` (patrón de The Pudding, ~30 líneas con
IntersectionObserver): expone `value` = índice del paso visible.

```svelte
<section class="scrolly">
  <div class="sticky">           <!-- position: sticky; top: 0; height: 100svh -->
    <Grafica paso={value} />     <!-- transiciona según el paso -->
  </div>
  <div class="steps">
    {#each pasos as paso, i}
      <div class="step" class:activo={value === i}>{paso.texto}</div>
    {/each}
  </div>
</section>
```

- Cada `.step` ocupa `min-height: 90svh` para dar aire al scroll.
- La gráfica reacciona a `paso` con transiciones de Svelte (`tweened`,
  `crossfade`) o actualizando escalas de LayerCake.

## CSS scroll-driven vs GSAP

- Efectos decorativos ligados al progreso (parallax suave, reveals):
  CSS `animation-timeline: view()` — sin JS; verificar soporte y dar
  fallback estático.
- Coreografía compleja (pin, scrub, timelines encadenados): GSAP
  ScrollTrigger.
- El estado narrativo (qué paso está activo) SIEMPRE con el patrón Scrolly,
  no con GSAP: mantiene la lógica en Svelte y es testeable.

## Reglas no negociables

- Móvil primero: los steps pasan a superponerse sobre el gráfico con fondo
  semitransparente legible; probar en 390px de ancho.
- `prefers-reduced-motion`: las transiciones se vuelven cortes; la historia
  debe funcionar completa sin animación.
- Texto de los pasos legible SIEMPRE (contraste sobre lo que tenga detrás —
  validar en las capturas).
- Sin autoplay de scroll ni secuestro de la rueda (scroll-jacking prohibido).
