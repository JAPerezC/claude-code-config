---
name: explore-data
description: Exploracion rapida de un dataset - schema, tipos, nulos, estadisticas, correlaciones, y recomendaciones de limpieza
argument-hint: ruta/al/archivo.csv
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
context: fork
---

Explorar el dataset en `$ARGUMENTS` siguiendo este flujo:

## 1. Carga y validacion
- Detectar formato (CSV, Parquet, Excel, JSON)
- Usar `encoding="utf-8"` y `pathlib.Path`
- Para Excel: usar `openpyxl`, NO convertir a CSV
- Mostrar shape, dtypes, primeras 5 filas

## 2. Calidad de datos
- Porcentaje de nulos por columna
- Duplicados
- Columnas constantes (un solo valor)
- Tipos inconsistentes (numeros guardados como string)

## 3. Estadistica descriptiva
- describe() para numericas
- value_counts() para categoricas (top 10)
- Rango de fechas si hay columnas temporales

## 4. Visualizacion rapida
- Generar script que cree PNGs (NO embeber en notebook)
- Histogramas de numericas
- Barras de categoricas
- Matriz de correlacion si hay +3 numericas
- Guardar graficos en `reports/figures/`

## 5. Recomendaciones
- Columnas candidatas a eliminar
- Transformaciones sugeridas
- Optimizacion de dtypes (category, int8, etc.)
- Estimacion de reduccion de memoria

## Reglas:
- NUNCA modificar el archivo original
- Outputs van a `data/processed/` o `reports/`
- Usar `logging`, no `print()`
