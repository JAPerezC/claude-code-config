# Anti-slop: lista negra verificable

Destilado de `reports/investigacion-web-dashboards.md`, áreas 3.4 y 3.6.
Catálogos que cita el informe: impeccable.style (64 patrones), vibecodekit
(señales + remedios numéricos), 925studios (estratégico, sin métricas).

Diagnóstico: el look genérico no lo causa ningún framework, lo causan **los
defaults** (paleta indigo de Tailwind, grises de shadcn/ui, chrome de
Streamlit, tema por defecto de ECharts) y la convergencia estadística de los
LLM hacia lo "on distribution", admitida por el cookbook de Anthropic: Claude
"defaults to safe choices unless explicitly encouraged otherwise" y re-converge
en las mismas segundas opciones (Space Grotesk).

---

## Regla maestra (hace innecesario memorizar hex)

Cero colores literales fuera de `tokens.css`. Todo color, sombra, radio y
familia tipográfica sale de un token semántico. Lo que no se detecte por nombre
se detecta por esta regla:

```bash
rg -n --glob '!**/tokens.css' -e '#[0-9a-fA-F]{3,8}\b' -e 'rgba?\(' -e 'hsla?\(' -e 'oklch\('
```

---

## 1. Gradiente púrpura-cian

- **Qué es:** fondo o hero con `linear-gradient` de violeta/índigo a cian.
  Huella nº 1 de v0/Lovable/Bolt; el sesgo se atribuye a Tailwind UI e
  `indigo-500` (tuit semi-apologético de Adam Wathan, ago-2025, +1M vistas).
- **Detección:**
  ```bash
  rg -n -e '(from|via|to)-(purple|violet|fuchsia|indigo)-' -e 'linear-gradient\('
  ```
- **En su lugar:** color plano de `--color-surface`, o gradiente construido con
  dos tokens ya aprobados por `validate_palette.py` dentro de la misma familia
  de tono. Nunca dos tintes fríos opuestos.
- **Evidencia:** informe §3.4 y §3.6 (impeccable.style, dev.to/alanwest).

## 2. Glassmorphism genérico

- **Qué es:** tarjetas semitransparentes blancas con `backdrop-blur` sobre un
  fondo colorido, sin motivo funcional.
- **Detección:**
  ```bash
  rg -n -e 'backdrop-blur' -e 'backdrop-filter' -e 'bg-white/(5|10|20)' -e 'rgba\(255,\s*255,\s*255'
  ```
- **En su lugar:** superficie opaca con token propio y jerarquía por
  espaciado/tipografía. El desenfoque solo si hay contenido real detrás que
  deba seguir siendo visible (overlay de mapa, modal sobre gráfico).

## 3. Grid de exactamente 3 cards con borde de acento

- **Qué es:** fila de tres tarjetas idénticas con `border-l-4`/`border-t-4` de
  color de marca. Señal documentada por vibecodekit ("exactamente 3 cards") y
  bordes de acento por impeccable.style.
- **Detección:**
  ```bash
  rg -n -e 'grid-cols-3' -e 'border-[lrtb]-(2|4|8)\b'
  ```
- **En su lugar:** que el número de elementos lo dicte el contenido real (2, 5,
  7...); diferenciar jerarquía por tamaño o posición, no por franja de color.

## 4. Fuentes por defecto en titulares

- **Qué es:** titulares en Inter, Geist o Space Grotesk. El informe nombra esas
  tres como huellas verificadas (impeccable.style + cookbook de Anthropic).
- **Detección:**
  ```bash
  rg -n -i -e 'Inter|Geist|Space Grotesk' -e 'next/font/google'
  ```
- **En su lugar:** ver `tipografia.md`. Pairing display+body real con variable
  fonts con carácter.
- **NO respaldado por el informe:** Roboto, Arial y `system-ui` no aparecen en
  ninguna fuente verificada como huella de IA. Trátalos como pobres para
  titulares por criterio propio, no como dato del informe.

## 5. Easing bounce por defecto

- **Qué es:** toda animación con rebote/overshoot sin motivo narrativo.
- **Detección:**
  ```bash
  rg -n -e 'back\.(out|in)' -e 'elastic\.' -e 'bounce' -e 'cubic-bezier\([^)]*,\s*1\.[0-9]'
  ```
- **En su lugar:** curvas de salida sobrias y duraciones cortas; el rebote solo
  cuando la animación *es* la historia (ver `scrollytelling.md`).
- **Nivel de evidencia:** aparece en el blueprint de la skill (§5 del informe)
  pero **sin fuente ni métrica que lo respalde**. Es criterio, no dato.

## 6. Hero centrado con badge + título + subtítulo + 2 botones

- **Qué es:** la plantilla de apertura de todo sitio generado por IA: píldora
  pequeña en mayúsculas, H1 centrado, párrafo gris, botón primario + secundario.
  Señal documentada por vibecodekit ("hero centrado con badge").
- **Detección:** primer `<section>` del index con `text-center` + un
  `rounded-full` con `text-xs`/`uppercase` + dos `<a>`/`<button>` consecutivos.
  ```bash
  rg -n -e 'rounded-full[^"]*text-xs' -e 'text-center' --glob '**/index.*'
  ```
- **En su lugar:** apertura asimétrica anclada al sujeto real: dato de portada,
  gráfico, imagen a sangre o titular a la izquierda con entradilla editorial.

## 7. Sombras de color (moradas) y defaults sin personalizar

- **Qué es:** `box-shadow` teñido de violeta, más el uso de shadcn/ui, Recharts
  o el tema por defecto de ECharts sin tocar. El informe es explícito: shadcn
  "sin personalizar produce exactamente el look genérico"; Recharts es "el motor
  del look shadcn genérico"; ECharts rehízo su tema por defecto justamente
  porque **>70 % de los usuarios no lo cambiaba**.
- **Detección:**
  ```bash
  rg -n -e 'shadow-(purple|violet|indigo)' -e 'box-shadow[^;]*(rgba?|oklch|#)'
  rg -n -e 'from "recharts"' -e 'components/ui/'
  ```
- **En su lugar:** sombras neutras derivadas del token de superficie; si se usa
  shadcn, reescribir el código copiado (`npx shadcn create` permite elegir
  estilo, fuentes y librería base) y sustituir Recharts por LayerChart/D3 o
  ECharts 6 tematizado.

## 8. Emojis como iconografía — SIN RESPALDO

El informe lo dice literalmente: *"La señal 'emojis como iconos' no quedó
respaldada por las fuentes verificadas"*. No lo listes como anti-patrón
verificado. Si lo evitas, di que es preferencia de la skill.

---

## Remedios numéricos (vibecodekit, únicos con métrica en el informe)

| Métrica | Umbral |
|---|---|
| Reparto de color | 60 / 30 / 10 |
| Razón de escala tipográfica | >= 1,25x |
| Rejilla base | 8 px |
| Contraste APCA | Lc >= 75 |

`DESIGN.md` por proyecto es parte del remedio, no un extra.

## Gate de validación

- **Bloqueante:** WCAG 2.2 AA con axe-core (~100 reglas). Ojo: `target-size`,
  la única regla específica de 2.2, **viene desactivada por defecto** —
  actívala.
- **Advisory:** APCA. No es normativo en WCAG 3.0 (Recommendation prevista
  hacia finales de 2029).
- **Las herramientas automáticas no bastan:** estudio GOV.UK, la mejor
  herramienta individual detectó el 41 % de 143 barreras; las 10 combinadas, el
  71 %. Revisión visual manual obligatoria al final.
