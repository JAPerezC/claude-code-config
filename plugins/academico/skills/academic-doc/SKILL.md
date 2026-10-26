---
name: academic-doc
description: Crear documentos académicos (DOCX, PDF) con Pandoc. Formato APA, citas bibliográficas, reportes. Triggers en "crear documento", "generar reporte", "formato APA", "escribir paper".
allowed-tools: Read, Write, Edit, Bash, Glob, WebSearch
---

# Crear Documento Académico

## Flujo

### 1. Definir el documento
Preguntar al usuario:
- ¿Qué tipo? (reporte, paper, ensayo, tarea, tesis)
- ¿Formato requerido? (APA 7, IEEE, libre)
- ¿Formato de salida? (DOCX, PDF, o ambos)
- ¿Tiene bibliografía? (archivo .bib, Zotero, o manual)

### 2. Crear estructura en Markdown
Escribir `documento.md` con YAML frontmatter:

```yaml
---
title: "Título del Documento"
author: "Jorge Alejandro Pérez"
date: "2026-03-27"
bibliography: referencias.bib
csl: apa.csl
lang: es-MX
---
```

### 3. Gestionar citas
Si el usuario necesita citas:
- Crear `referencias.bib` con entradas BibTeX
- Usar sintaxis Pandoc: `[@autor2024]` (paréntesis) o `@autor2024` (narrativa)
- Descargar `apa.csl` si no existe:
  ```bash
  curl -L -o apa.csl https://raw.githubusercontent.com/citation-style-language/styles/master/apa.csl
  ```

### 4. Generar documento

**DOCX:**
```bash
pandoc documento.md -o documento.docx --citeproc --bibliography=referencias.bib --csl=apa.csl --reference-doc=template.dotm
```

**PDF (requiere LaTeX o Typst):**
```bash
pandoc documento.md -o documento.pdf --citeproc --bibliography=referencias.bib --csl=apa.csl --pdf-engine=xelatex
```

**Ambos:**
```bash
pandoc documento.md -o documento.docx --citeproc --bibliography=referencias.bib --csl=apa.csl
pandoc documento.md -o documento.pdf --citeproc --bibliography=referencias.bib --csl=apa.csl --pdf-engine=xelatex
```

### 5. Estructura APA 7 estándar
Si el documento es formato APA:

1. Página de título (título, autor, afiliación, nota del autor)
2. Abstract (150-250 palabras)
3. Introducción
4. Método (participantes, instrumentos, procedimiento)
5. Resultados
6. Discusión
7. Referencias
8. Apéndices (si aplica)

## Reglas
- Usar ortografía correcta en español (acentos, ñ, ¿?, ¡!)
- Verificar que las citas en el texto coincidan con las referencias
- Doble espacio, Times New Roman 12pt (para APA)
- Márgenes de 1 pulgada (2.54 cm)
- Números de página en esquina superior derecha
