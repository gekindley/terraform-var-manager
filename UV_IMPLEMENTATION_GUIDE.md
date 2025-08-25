# 🚀 Guía Completa: Aplicación de UV en terraform-var-manager

## 📋 Tabla de Contenidos

1. [¿Qué es UV?](#qué-es-uv)
2. [¿Por qué UV en lugar de pip/poetry?](#por-qué-uv-en-lugar-de-pippoetry)
3. [Instalación de UV](#instalación-de-uv)
4. [Migración del Script Original](#migración-del-script-original)
5. [Estructura del Proyecto con UV](#estructura-del-proyecto-con-uv)
6. [Configuración Detallada](#configuración-detallada)
7. [Gestión de Dependencias](#gestión-de-dependencias)
8. [Flujo de Desarrollo](#flujo-de-desarrollo)
9. [Build y Distribución](#build-y-distribución)
10. [Comandos UV Utilizados](#comandos-uv-utilizados)
11. [Mejores Prácticas](#mejores-prácticas)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 ¿Qué es UV?

**UV** es un gestor de paquetes y proyectos Python de nueva generación desarrollado por **Astral** (creadores de Ruff). Está escrito en **Rust** y es extremadamente rápido.

### Características Principales:
- ⚡ **10-100x más rápido** que pip
- 🔒 **Lock files automáticos** para reproducibilidad
- 🐍 **Gestión de versiones Python** integrada
- 📦 **Gestión completa de proyectos** (creación, build, publish)
- 🛠️ **Reemplaza múltiples herramientas**: pip, virtualenv, poetry, pipenv, pyenv

---

## 🤔 ¿Por qué UV en lugar de pip/poetry?

### Comparación con Herramientas Tradicionales:

| Característica | UV | Poetry | pip + venv | pipenv |
|----------------|----|---------|-----------| -------|
| **Velocidad** | ⚡ Muy rápida | 🐌 Lenta | 🐌 Lenta | 🐌 Lenta |
| **Lock files** | ✅ Automático | ✅ Manual | ❌ No | ✅ Manual |
| **Gestión Python** | ✅ Integrada | ❌ No | ❌ No | ❌ No |
| **Build/Publish** | ✅ Nativo | ✅ Sí | ❌ No | ❌ No |
| **Configuración** | 📄 Simple | 📄 Compleja | 📄 Manual | 📄 Media |


## 🔧 Instalación de UV

### Instalación Realizada:
```bash
# Instalación usando el script oficial
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificación
uv --version
# Output: uv 0.8.13
```

### Configuración de PATH:
```bash
# Agregar al PATH (automático en la instalación)
export PATH="$HOME/.local/bin:$PATH"
```

### Alternativas de Instalación:
```bash
# Via pip (si ya tienes Python)
pip install uv

# Via homebrew (macOS)
brew install uv

# Via cargo (si tienes Rust)
cargo install --git https://github.com/astral-sh/uv uv
```

---

## 📦 Migración del Script Original

### Estado Original:
```
terraform-var-manager/
├── script_variables.py    # Script monolítico
└── README.md
```

### Proceso de Migración:

#### 1. Inicialización del Proyecto UV:
```bash
# Crear estructura de proyecto con UV
uv init --lib terraform-var-manager

# Esto genera:
terraform-var-manager/
├── pyproject.toml
├── src/terraform_var_manager/
│   ├── __init__.py
│   └── py.typed
├── README.md
└── .python-version
```

#### 2. Refactorización del Código:
```bash
# Mover y modularizar el script original
mv script_variables.py terraform-var-manager/src/terraform_var_manager/main.py

# Crear módulos separados:
# - api_client.py: Cliente para Terraform Cloud API
# - variable_manager.py: Lógica de negocio de alto nivel
# - utils.py: Funciones utilitarias
# - main.py: CLI interface
```

#### 3. Estructura Modular Resultante:
```
src/terraform_var_manager/
├── __init__.py           # Package principal con exports
├── main.py              # CLI interface (ArgumentParser)
├── api_client.py        # TerraformCloudClient class
├── variable_manager.py  # VariableManager class
├── utils.py             # Funciones utilitarias
└── py.typed             # Typing marker
```

---

## 🏗️ Estructura del Proyecto con UV

### Estructura Final:
```
terraform-var-manager/
├── .gitignore                    # Configuración Git
└── terraform-var-manager/       # Package principal
    ├── src/terraform_var_manager/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── api_client.py
    │   ├── variable_manager.py
    │   └── utils.py
    ├── tests/
    │   ├── __init__.py
    │   └── test_utils.py
    ├── .venv/                    # Entorno virtual UV
    ├── .pytest_cache/
    ├── dist/                     # Distribuciones built
    ├── pyproject.toml            # Configuración principal
    ├── README.md                 # Documentación
    ├── LICENSE                   # Licencia MIT
    ├── dev.sh                    # Script de desarrollo
    └── uv.lock                   # Lock file
```

## ⚙️ Configuración Detallada

### pyproject.toml Configurado:

```toml
[project]
name = "terraform-var-manager"
version = "0.1.0"
description = "A tool to manage Terraform Cloud variables..."
readme = "README.md"
authors = [
    { name = "Geordy Kindley", email = "gekindley@gmail.com" }
]
requires-python = ">=3.9"
dependencies = [
    "requests>=2.28.0",
]
keywords = ["terraform", "terraform-cloud", "variables", "devops"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
    # ... más classifiers
]

[project.urls]
Homepage = "https://github.com/gekindley/terraform-var-manager"
Repository = "https://github.com/gekindley/terraform-var-manager"

[project.scripts]
terraform-var-manager = "terraform_var_manager.main:main"
tfvar-manager = "terraform_var_manager.main:main"

[build-system]
requires = ["uv_build>=0.8.13,<0.9.0"]
build-backend = "uv_build"

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]

[dependency-groups]
dev = [
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
]
```

### Explicación de Secciones:

#### `[project]`:
- **name**: Nombre en PyPI (con guiones)
- **scripts**: Entry points para CLI
- **dependencies**: Dependencias de producción
- **classifiers**: Metadatos para PyPI

#### `[build-system]`:
- **requires**: Backend de build (uv_build)
- **build-backend**: Motor de construcción

#### `[dependency-groups]`:
- **dev**: Dependencias de desarrollo
- Reemplaza `[tool.poetry.group.dev.dependencies]`

---

## 📚 Gestión de Dependencias

### Dependencias de Producción:
```bash
# Agregar dependencia de producción
uv add requests

# Especificar versión
uv add "requests>=2.28.0"

# Agregar múltiples
uv add requests click typer
```

### Dependencias de Desarrollo:
```bash
# Agregar dependencias de desarrollo
uv add --dev pytest pytest-cov

# Instalar todas las dependencias (prod + dev)
uv sync --all-extras
```

### Lock File (uv.lock):
```yaml
# Archivo generado automáticamente
# Garantiza builds reproducibles
# Similar a poetry.lock o Pipfile.lock

version = 1
requires-python = ">=3.9"

[[package]]
name = "requests"
version = "2.32.5"
source = { registry = "https://pypi.org/simple" }
# ... más detalles
```

### Comandos de Gestión:
```bash
# Instalar dependencias del proyecto
uv sync

# Actualizar dependencias
uv sync --upgrade

# Instalar en entorno específico
uv sync --python 3.11

# Solo dependencias de producción
uv sync --no-dev
```

---

## 🔄 Flujo de Desarrollo

### Script de Desarrollo (dev.sh):
```bash
#!/bin/bash
# Script personalizado para tareas comunes

case "${1:-help}" in
    install)
        uv sync --all-extras
        ;;
    test)
        uv run pytest tests/ -v --cov=src/terraform_var_manager
        ;;
    build)
        uv build
        ;;
    run)
        shift
        uv run terraform-var-manager "$@"
        ;;
esac
```

### Flujo Típico de Desarrollo:
```bash
# 1. Instalar dependencias
./dev.sh install

# 2. Ejecutar tests
./dev.sh test

# 3. Ejecutar CLI en desarrollo
./dev.sh run --help

# 4. Build para distribución
./dev.sh build

# 5. Limpiar artifacts
./dev.sh clean
```

### Comandos UV Directos:
```bash
# Ejecutar script dentro del entorno
uv run python -c "from terraform_var_manager import VariableManager; print('OK')"

# Ejecutar comando CLI
uv run terraform-var-manager --help

# Ejecutar tests
uv run pytest

# Activar shell del entorno virtual
uv shell
```

---

## 📦 Build y Distribución

### Proceso de Build:
```bash
# Build automático con UV
uv build

# Genera:
dist/
├── terraform_var_manager-0.1.0.tar.gz      # Source distribution
└── terraform_var_manager-0.1.0-py3-none-any.whl  # Wheel
```

### Verificación de Build:
```bash
# Instalar desde wheel local
uv pip install dist/terraform_var_manager-0.1.0-py3-none-any.whl

# Probar instalación
terraform-var-manager --help
```

### Publicación (cuando esté listo):
```bash
# Configurar credenciales PyPI
uv config --set pypi.token <token>

# Publicar en TestPyPI primero
uv publish --repository testpypi

# Publicar en PyPI real
uv publish
```

---

## 🛠️ Comandos UV Utilizados

### Gestión de Proyecto:
```bash
uv init --lib terraform-var-manager     # Inicializar proyecto
uv add requests                          # Agregar dependencia
uv add --dev pytest                     # Agregar dep de desarrollo
uv sync                                 # Instalar dependencias
uv sync --all-extras                    # Instalar todas las deps
```

### Ejecución:
```bash
uv run terraform-var-manager --help     # Ejecutar CLI
uv run pytest                          # Ejecutar tests
uv run python script.py                # Ejecutar Python
uv shell                               # Activar entorno
```

### Build y Distribución:
```bash
uv build                               # Construir package
uv publish                             # Publicar en PyPI
uv publish --repository testpypi       # Publicar en TestPyPI
```

### Gestión de Python:
```bash
uv python install 3.11                 # Instalar Python 3.11
uv python list                         # Listar Pythons disponibles
uv sync --python 3.11                  # Usar Python específico
```

---

## ✅ Mejores Prácticas

### 1. Estructura de Proyecto:
- ✅ Usar `src/` layout para packages
- ✅ Separar tests en directorio propio
- ✅ Incluir `py.typed` para type hints
- ✅ Usar entry points para CLI

### 2. Gestión de Dependencias:
- ✅ Especificar versiones mínimas (`>=`)
- ✅ Usar dependency groups para organizar
- ✅ Incluir `uv.lock` en control de versiones
- ✅ Mantener `pyproject.toml` limpio

### 3. Development Workflow:
- ✅ Crear script de desarrollo (`dev.sh`)
- ✅ Usar `uv run` para comandos
- ✅ Configurar tests automatizados
- ✅ Build regular para validación

### 4. Distribución:
- ✅ Probar en TestPyPI primero
- ✅ Verificar metadatos en `pyproject.toml`
- ✅ Incluir documentación completa
- ✅ Usar semantic versioning

---

## 🚨 Troubleshooting

### Problemas Comunes:

#### 1. Import Errors:
```bash
# Error: ModuleNotFoundError
# Solución: Instalar en modo editable
uv pip install -e .
```

#### 2. Lock File Conflicts:
```bash
# Error: uv.lock conflictos
# Solución: Regenerar lock
rm uv.lock
uv sync
```

#### 3. Python Version Issues:
```bash
# Error: Python version incompatible
# Solución: Especificar Python
uv sync --python 3.9
```

#### 4. Build Failures:
```bash
# Error: Build falla
# Solución: Verificar pyproject.toml
uv build --verbose
```

### Debugging:
```bash
# Verbose output
uv --verbose sync

# Ver configuración
uv config list

# Ver entorno
uv run python -c "import sys; print(sys.path)"
```

---

## 🎯 Conclusiones

### Beneficios Obtenidos:
1. **⚡ Velocidad**: Gestión de dependencias extremadamente rápida
2. **🔒 Reproducibilidad**: Lock files automáticos
3. **🎛️ Simplicidad**: Una herramienta para todo el ciclo de vida
4. **🚀 Modernidad**: Siguiendo las mejores prácticas actuales
5. **📦 Profesionalismo**: Package listo para distribución

### Lecciones Aprendidas:
- UV simplifica enormemente la gestión de proyectos Python
- La estructura modular mejora maintainability
- Los entry points hacen el CLI más profesional
- El flujo de desarrollo es más eficiente

### Recomendaciones Futuras:
- Usar UV para todos los proyectos Python nuevos
- Migrar proyectos existentes gradualmente
- Aprovechar la gestión de versiones Python integrada
- Explorar funcionalidades avanzadas como workspaces

---

## 🔄 Actualización y Rebuild del Package

### Cuando actualices el código del package, sigue este flujo:

#### 1. **Después de realizar cambios en el código:**
```bash
cd terraform-var-manager/

# Verificar que los cambios no rompan nada
./dev.sh test
```

#### 2. **Actualizar la versión (opcional pero recomendado):**
```bash
# Editar pyproject.toml y cambiar la versión
# version = "0.1.0" → version = "0.1.1"
nano pyproject.toml
```

#### 3. **Rebuild del package:**
```bash
# Limpiar builds anteriores
./dev.sh clean

# Crear nuevo build
./dev.sh build

# O usando comandos UV directos:
uv build --clean
```

#### 4. **Verificar el nuevo build:**
```bash
# Verificar que se generaron los archivos
ls -la dist/

# Probar instalación local del nuevo build
cd /tmp
uv venv test-install
source test-install/bin/activate
uv pip install /path/to/terraform-var-manager/dist/terraform_var_manager-0.1.1-py3-none-any.whl

# Probar que funciona
terraform-var-manager --help
```

#### 5. **Flujo completo automatizado:**
```bash
#!/bin/bash
# Script para actualización completa

# Ejecutar tests
echo "🧪 Ejecutando tests..."
./dev.sh test || exit 1

# Limpiar builds anteriores  
echo "🧹 Limpiando builds anteriores..."
./dev.sh clean

# Crear nuevo build
echo "📦 Creando nuevo build..."
./dev.sh build

# Verificar archivos generados
echo "✅ Archivos generados:"
ls -la dist/

echo "🎉 ¡Build completado exitosamente!"
```

#### 6. **Para publicación (después del build):**
```bash
# Solo cuando estés listo para publicar
# Primero en TestPyPI
uv publish --repository testpypi

# Después en PyPI real
uv publish
```

### 📋 **Checklist de Actualización:**

- [ ] ✅ Tests pasan (`./dev.sh test`)
- [ ] 📝 Versión actualizada en `pyproject.toml` (si aplica)
- [ ] 🧹 Build anterior limpiado (`./dev.sh clean`)
- [ ] 📦 Nuevo build creado (`./dev.sh build`)
- [ ] 🔍 Build verificado localmente
- [ ] 📚 Documentación actualizada (si aplica)
- [ ] 🏷️ Git tag creado para nueva versión (si aplica)
- [ ] 🚀 Publicado (cuando esté listo)

### ⚡ **Comando Rápido para Desarrollo:**
```bash
# Un solo comando para rebuild rápido durante desarrollo
./dev.sh test && ./dev.sh clean && ./dev.sh build
```

---

**🎉 ¡UV transformó terraform-var-manager de un script simple a un package Python profesional y distribuible!**
