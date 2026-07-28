# Direcciones estéticas

Destilado de `reports/investigacion-web-dashboards.md` §3.5 y §3.6.

**Aviso de cobertura, importante:** el informe cita `awesome-claude-design` como
banco de referencias con **"9 familias y huellas por defecto"** pero **no las
enumera**. Tampoco documenta las familias "suizo/internacional", "brutalist" ni
"técnico/IDE": esos nombres vienen del encargo, no del informe. Aquí se separan
las familias **ancladas en evidencia del informe** de las **propuestas sin
respaldo**, y se da un procedimiento para derivar una dirección en vez de
inventar catálogo.

---

## Principio operativo: "defaults rather than choices"

Del skill `frontend-design` (55 líneas, >370.000 instalaciones a mar-2026), que
el informe pone como modelo: **nombra defaults de IA concretos** y **obliga a un
plan de diseño revisable antes de codificar**. Lo que hace no genérica a una
pieza no es elegir una familia estética, es:

1. **Anclar la dirección al sujeto real del proyecto.** ¿De qué van los datos?
   ¿Quién los publica? ¿Qué material de referencia existe (informes impresos,
   señalética, prensa del sector)? La familia se elige contra eso, no contra el
   gusto general.
2. **Nombrar explícitamente los defaults prohibidos de esa familia** en
   `DESIGN.md`. Sin la lista de prohibiciones, el modelo re-converge (cookbook
   de Anthropic: Claude "defaults to safe choices unless explicitly encouraged
   otherwise" y repite las mismas segundas opciones).
3. **Declarar el elemento único de la pieza**: una decisión que no aparecería en
   ningún otro proyecto (una escala, un tipo de gráfico, un recurso de portada).

`DESIGN.md` es artefacto intermedio obligatorio y revisable por el humano
ANTES de codificar: color, tipografía, layout y elemento único.

---

## Defaults prohibidos, transversales a toda familia

Documentados por el informe como fuentes del look genérico:

- Paleta **indigo de Tailwind** y grises de **shadcn/ui** sin personalizar.
- **Recharts** como librería de gráficos (motor del look shadcn).
- Tema **por defecto de ECharts** (lo rehicieron porque >70 % no lo cambiaba).
- Estética **muy reconocible de Plotly**.
- **Chrome de Streamlit** ("una app Streamlit se reconoce siempre") y de marimo
  (solo 3 variables CSS garantizadas).
- Titulares en **Inter / Geist / Space Grotesk**.

Ver `anti-slop.md` para la lista con patrones de detección.

---

## Familias ANCLADAS en el informe

### A. Editorial de datos / prensa (FT, The Pudding, NYT)

- **Anclas reales:** The Pudding publica `the-pudding/svelte-starter` (MIT, push
  2-jul-2026). El FT publica `visual-vocabulary` (también en
  `Financial-Times/chart-doctor`) y `@financial-times/g-components` v15.0.5
  (dic-2025); `story-playbook` está **archivado desde 2019** y **no existe
  starter-kit público** del FT. Svelte nació del trabajo de Rich Harris en
  Guardian/NYT, y las ofertas vivas de Graphics del NYT piden Svelte y D3.
- **El valor está en el método, no en el CSS:** sistema de diseño editorial
  repartido en **librerías pequeñas y específicas** (`g-axis`, `g-chartcolour`),
  y un catálogo de formas de gráfico (`visual-vocabulary`) que decide la forma
  antes que el color.
- **Cuándo usarla:** ensayos de datos, longform, scrollytelling, cualquier pieza
  donde la historia manda sobre el filtrado.
- **Stack:** SvelteKit 2 + Svelte 5 + `adapter-static`, D3 7 / LayerCake 10,
  componente Scrolly, Style Dictionary para tokens, ArchieML si el texto lo
  escribe alguien más.
- **Tipografía y paleta concretas de FT/Pudding: NO documentadas en el informe.**
  No afirmes que el FT usa tal fuente o tal fondo salmón sin verificarlo aparte.

### B. Dashboard denso tematizable

- **Cuándo:** muchas series, filtros cruzados, KPIs, datos que el usuario
  explora. No hay narrativa lineal.
- **Stack:** SvelteKit 2 (runes para estado y filtros cruzados) + **ECharts 6**
  (design tokens de serie, cambio claro/oscuro sin reinicializar, Canvas para
  millones de puntos) y LayerChart 2 / D3 para las piezas a medida. Datos en
  build con Python/DuckDB a Parquet, DuckDB-WASM en cliente.
- **Prohibido:** el tema por defecto de ECharts, Recharts, y el layout en tres
  columnas iguales.

### C. Reporte reproducible / científico

- **Stack:** Quarto CLI 1.10.18 (SCSS sobre Bootstrap 5, +1.400 variables Sass,
  25 temas Bootswatch). Interactividad sin servidor vía Observable JS o Jupyter
  Widgets.
- **Cuándo:** informes del flujo Jupyter/Posit donde importa la reproducibilidad
  más que la identidad visual. El informe lo clasifica explícitamente como
  **"marca corporativa, sin diseño editorial"**: no es el vehículo de una pieza
  distintiva.

### D. BI SQL-first corporativo

- **Stack:** Evidence 40.1.8 (SQL+Markdown, tokens en `evidence.config.yaml`,
  layout reemplazable con `+layout.svelte`).
- **Cuándo:** reporting BI estático con marca corporativa razonable. Sin
  pretensión de diseño editorial ni scrollytelling. Nota de riesgo: el
  desarrollo activo se desplazó al comercial Evidence Studio.

### E. Editorial rápido con pipeline resuelto

- **Stack:** Observable Framework 1.13.4 (ISC): **13 temas** y opción `style`
  para sustituir el stylesheet completo, data loaders en Python.
- **Riesgo a declarar al usuario:** solo parches desde nov-2024, `deploy`
  deprecado, pivote de Observable a Notebook Kit. Sin deprecación oficial.

---

## Familias PEDIDAS pero SIN RESPALDO en el informe

Suizo/internacional, brutalist y técnico/IDE **no aparecen** en el informe: ni
sus fuentes típicas, ni sus paletas, ni marcas ancla. Si las usas, decláralo en
`DESIGN.md` como criterio propio y **no las presentes como hallazgo de la
investigación**. Antes de convertirlas en presets de la skill, verifica sus
referencias con una búsqueda propia (y añade las fuentes a `refs.bib`).

Lo mismo para las 9 familias de `awesome-claude-design`: el repo existe
(`github.com/rohitg00/awesome-claude-design`) y el informe confirma que aporta
familias **y sus huellas por defecto**, pero hay que abrirlo para conocerlas.

---

## Procedimiento para derivar una dirección (en vez de elegir de catálogo)

1. Describe el sujeto en una frase y lista 3 materiales de referencia del mundo
   real de ese sujeto.
2. Elige la familia por **función** (¿narra o explora?), no por gusto: narra ->
   A; explora -> B; documenta -> C/D.
3. Escribe en `DESIGN.md`: paleta (con roles 60/30/10), pairing display+body,
   rejilla, y **el elemento único**.
4. Escribe la lista de prohibiciones específicas de esta pieza.
5. Genera tokens y valida la paleta **antes** de componer nada.

Nota: si el proyecto es institucional, los tokens salen de la marca oficial y
esta guía solo aplica a layout y forma de los gráficos. El informe no documenta
ninguna marca institucional concreta.
