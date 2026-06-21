---
name: citas
description: Buscar papers, generar BibTeX, validar referencias, formatear en APA.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
context: fork
---

# Gestión de Citas y Bibliografía

## Modos de Uso

### 1. Buscar y agregar una referencia
```
/citas buscar: machine learning for political violence prediction
```

**Flujo:**
1. Buscar en Semantic Scholar / CrossRef / Google Scholar
2. Obtener metadata verificada (DOI, autores, año, journal)
3. Generar entrada BibTeX válida
4. Agregar a `refs.bib` del proyecto (crear si no existe)
5. Mostrar la clave de cita para usar en el documento: `[@clave2026]`

### 2. Agregar referencia manual
```
/citas agregar: https://doi.org/10.1234/ejemplo
```

**Flujo:**
1. Resolver DOI vía CrossRef (`https://doi.org/{doi}` con header `Accept: application/x-bibtex`)
2. Validar metadata
3. Agregar a `refs.bib`

### 3. Verificar bibliografía existente
```
/citas verificar
```

**Flujo:**
1. Leer `refs.bib`
2. Para cada entrada, verificar DOI o título contra CrossRef/Semantic Scholar
3. Marcar entradas no verificables como sospechosas
4. Reportar: verificadas, sospechosas, duplicadas, incompletas

### 4. Formatear bibliografía
```
/citas formatear apa
```

**Flujo:**
1. Leer `refs.bib`
2. Generar lista formateada en APA 7ma edición
3. Mostrar en terminal o escribir a `referencias.md`

### 5. Citar fuente web
```
/citas web: https://url-del-recurso.com
```

**Flujo:**
1. Fetch de la URL
2. Extraer: título, autor, fecha de publicación, sitio
3. Generar entrada BibTeX tipo `@misc` o `@online`
4. Agregar a `refs.bib`

## Formato BibTeX Estándar

### Paper/Artículo
```bibtex
@article{apellido2026keyword,
  author    = {Apellido, Nombre and Apellido2, Nombre2},
  title     = {Título completo del artículo},
  journal   = {Nombre del Journal},
  year      = {2026},
  volume    = {10},
  number    = {3},
  pages     = {100--115},
  doi       = {10.1234/ejemplo},
  url       = {https://doi.org/10.1234/ejemplo}
}
```

### Sitio Web/Recurso Online
```bibtex
@misc{apellido2026keyword,
  author       = {Apellido, Nombre OR Nombre del Sitio},
  title        = {Título de la página},
  year         = {2026},
  url          = {https://url-completa.com},
  urldate      = {2026-03-30},
  note         = {Consultado el 30 de marzo de 2026}
}
```

### Libro
```bibtex
@book{apellido2026keyword,
  author    = {Apellido, Nombre},
  title     = {Título del Libro},
  publisher = {Editorial},
  year      = {2026},
  isbn      = {978-0-000-00000-0}
}
```

## Validación Anti-Alucinación

**OBLIGATORIO** antes de agregar cualquier referencia:
1. Si tiene DOI → resolver contra `https://api.crossref.org/works/{doi}`
2. Si no tiene DOI → buscar título exacto en Semantic Scholar
3. Si no se puede verificar → marcar como `% UNVERIFIED` en el comentario BibTeX
4. NUNCA inventar autores, títulos, journals o DOIs

## Convenciones de Claves

Formato: `apellidoAñoKeyword`
- `perez2026violencia`
- `smith2024machinelearning`
- `inegi2025censo`

Si hay conflicto (misma clave), agregar sufijo: `a`, `b`, `c`.

## Reglas
- Ortografía correcta en español (acentos, ñ, ¿?, ¡!)
- Encoding UTF-8 en `refs.bib`
- Una entrada por fuente, sin duplicados
- Verificar antes de agregar
