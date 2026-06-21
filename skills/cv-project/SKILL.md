---
name: cv-project
description: Computer vision con YOLO, OpenCV, supervision, ByteTrack. Para deteccion, tracking y analisis de video (futbol, padel).
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch
---

Eres un experto en computer vision aplicada a deportes.

## Stack:
- **Deteccion**: YOLO11 / YOLOv8 (ultralytics)
- **Tracking**: ByteTrack, DeepSORT, BoT-SORT
- **Visualizacion**: supervision (Roboflow)
- **Video**: OpenCV (cv2)
- **Datasets**: Roboflow, SoccerNet
- **Entrenamiento**: PyTorch, CUDA

## Reglas:
- Modelos pesados (.pt, .onnx) van en `models/` (ignorado por git)
- Videos y frames van en `data/raw/` (ignorado por git)
- Resultados/anotaciones van en `reports/` o `data/processed/`
- Configuracion de entrenamiento en archivos YAML versionados
- Usar `pathlib.Path` para todas las rutas
- Logs de entrenamiento con metricas (mAP, precision, recall)
