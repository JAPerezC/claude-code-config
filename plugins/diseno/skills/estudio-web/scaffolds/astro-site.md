# Scaffold: sitio con Astro 7 + Tailwind 4 + tokens

Para landings, portfolios, reportes y micrositios. Cero JS por defecto;
islas interactivas solo donde hagan falta.

## Comandos (ejecutar en el directorio padre del proyecto)

```bash
npm create astro@latest <slug> -- --template minimal --no-install --git false
cd <slug>
npm install
npx astro add tailwind --yes        # instala @tailwindcss/vite (Tailwind 4)
npm install --save-dev @astrojs/svelte svelte   # solo si habrá islas
```

## Conexión de tokens (obligatoria antes de escribir componentes)

1. Generar tokens: `python <skill>/scripts/make_tokens.py DESIGN.md src/styles/`
2. **Fuentes SIEMPRE por `<link>` en el `<head>` del layout** (preconnect +
   stylesheet con la URL de `fonts.import` del DESIGN.md). El `@import` de
   fuentes que emite `tokens.css` NO basta: Vite/Tailwind lo deja a mitad del
   bundle final y el navegador ignora los `@import` que no van al inicio —
   el síntoma es la página entera en serif/sans de fallback.
3. En `src/styles/global.css` (el que crea `astro add tailwind`):

```css
@import 'tailwindcss';
@import './tokens.css';
```

3. Con Tailwind 4, cada token de `@theme` genera utilidades automáticas:
   `--color-accent` → `text-accent`, `bg-accent`; `--font-display` →
   `font-display`. Usar SIEMPRE esas utilidades — nunca hex ni fuentes
   literales en componentes.

## Estructura mínima

```
src/
  layouts/Base.astro     (head, fuentes, tema claro/oscuro, header/footer)
  pages/index.astro
  components/            (secciones; islas .svelte solo si interactivas)
  styles/global.css + tokens.css
public/                  (imágenes, logos si modo institucional)
```

- Toggle de tema: script inline en Base.astro que fija
  `document.documentElement.dataset.theme` desde localStorage.
- Islas: `<Grafica client:visible />` — la página sigue siendo estática.
- Imágenes con `astro:assets` (`<Image>`) para optimización automática.

## Verificación y deploy

- `npm run dev` para preview; `npm run build && npm run preview` antes de
  publicar.
- GitHub Pages: workflow oficial `withastro/action` + `site`/`base` en
  `astro.config.mjs`.
- Vercel/Netlify: conectar el repo; build `npm run build`, output `dist/`.
  Confirmar con el usuario antes de publicar.
