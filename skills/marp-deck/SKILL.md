---
name: marp-deck
description: Crear presentaciones desde Markdown con Marp. Genera HTML, PDF y PPTX. Triggers en "crear presentación", "hacer slides", "generar deck".
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Crear Presentación con Marp

## Flujo de 4 Etapas

### 1. Entrevistar
Preguntar al usuario:
- ¿Cuál es el tema/objetivo de la presentación?
- ¿Quién es la audiencia? (clase, conferencia, defensa, etc.)
- ¿Cuántas diapositivas aproximadamente?
- ¿Hay datos o gráficas que incluir?
- ¿Estilo preferido? (minimalista, académico, corporativo)

### 2. Generar Draft
Crear archivo `slides.md` con formato Marp:

```markdown
---
marp: true
theme: default
paginate: true
header: 'Título'
footer: 'Autor — Fecha'
---

# Título de la Presentación
## Subtítulo

---

## Slide 2

- Punto clave 1
- Punto clave 2

<!-- Speaker notes aquí -->
```

### 3. Iterar
El usuario revisa y pide cambios:
- "Divide la slide 3 en dos"
- "Agrega una gráfica de los resultados"
- "Cambia el tema a gaia"

### 4. Exportar
Generar los tres formatos:

```bash
marp slides.md -o presentacion.html
marp slides.md -o presentacion.pdf
marp slides.md -o presentacion.pptx
```

## Temas Disponibles
- `default` — Limpio, fondo blanco
- `gaia` — Colores vibrantes, fondos de color
- `uncover` — Minimalista con acentos

## Reglas
- Usar ortografía correcta en español (acentos, ñ, ¿?, ¡!)
- Máximo 6 bullets por slide
- Cada slide = una idea
- Títulos como conclusiones, no como temas
- Incluir notas del presentador con `<!-- ... -->`
