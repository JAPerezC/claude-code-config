# Archivos Base Obligatorios al Iniciar un Proyecto

## `.env.example` (plantilla sin valores reales)
```bash
# Base de datos
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# APIs externas
API_KEY=
API_SECRET=

# Configuracion general
ENV=development
LOG_LEVEL=INFO
```

## `.envrc` (para direnv — sin secretos)
```bash
dotenv_if_exists .env
```

## `README.md` (estructura minima)
```markdown
# Nombre del Proyecto

## Descripcion
...

## Estructura del Repositorio
...

## Setup
1. Copiar `.env.example` a `.env` y completar los valores
2. Instalar dependencias: `pip install -r requirements.txt`

## Uso
...
```
