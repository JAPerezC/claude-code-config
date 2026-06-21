# Template .gitignore Obligatorio

Al crear o modificar un `.gitignore`, asegurate de incluir como minimo:

```gitignore
# === SECRETOS Y CONFIGURACION LOCAL ===
.env
.env.*
!.env.example
*.env
.secrets/
secrets/
credentials/
config/local/
*.pem
*.key
*.p12
*.pfx
*.crt

# === DIRENV ===
.direnv/

# === PYTHON ===
__pycache__/
*.py[cod]
*.pyo
.Python
*.egg
*.egg-info/
dist/
build/
eggs/
.eggs/
*.so
.venv/
venv/
env/
ENV/
.cache/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# === JUPYTER ===
.ipynb_checkpoints/
*.ipynb_checkpoints

# === DATOS Y MODELOS (archivos pesados) ===
*.csv
*.parquet
*.feather
*.pkl
*.pickle
*.h5
*.hdf5
*.onnx
*.pt
*.pth
*.bin
data/raw/
data/processed/
models/
artifacts/

# === SISTEMA OPERATIVO ===
.DS_Store
Thumbs.db
desktop.ini

# === IDEs ===
.vscode/
.idea/
*.swp
*.swo
*~

# === LOGS Y TEMPORALES ===
*.log
logs/
tmp/
temp/
triage/local/

# === CLOUD / INFRA ===
.terraform/
*.tfstate
*.tfstate.backup
.terraformrc
terraform.rc
```
