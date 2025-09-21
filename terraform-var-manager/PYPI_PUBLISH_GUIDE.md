# 📦 Guía de Publicación en PyPI

Esta guía te llevará paso a paso para publicar `terraform-var-manager` versión 1.0.0 en PyPI.

## 📋 Método Recomendado: Usando dev.sh + ~/.pypirc

El script `./dev.sh` está configurado para leer automáticamente las credenciales desde `~/.pypirc`, lo que simplifica enormemente el proceso:

```bash
# Configurar una vez
vim ~/.pypirc

# Publicar en TestPyPI
./dev.sh publish-test

# Publicar en PyPI (con confirmación)
./dev.sh publish
```

**Ventajas:**
- ✅ Credenciales seguras almacenadas localmente
- ✅ Configuración reutilizable
- ✅ Menos propenso a errores
- ✅ Integración perfecta con el workflow de desarrollo

## 🔐 Paso 1: Configurar Credenciales

### 1.1 Crear Cuentas
- **TestPyPI**: https://test.pypi.org/account/register/
- **PyPI**: https://pypi.org/account/register/

### 1.2 Generar API Tokens

#### Para TestPyPI:
1. Ve a https://test.pypi.org/manage/account/token/
2. Crea un nuevo token con scope "Entire account"
3. Copia el token (empieza con `pypi-`)

#### Para PyPI:
1. Ve a https://pypi.org/manage/account/token/
2. Crea un nuevo token con scope "Entire account"
3. Copia el token (empieza con `pypi-`)

### 1.3 Configurar ~/.pypirc (Recomendado)

El script `dev.sh` utiliza automáticamente el archivo `~/.pypirc` para leer las credenciales.

Crear o editar `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-tu-token-pypi

[testpypi]
username = __token__
password = pypi-tu-token-testpypi
```

### 1.4 Alternativa: Variables de entorno

Si prefieres no usar `~/.pypirc`, puedes usar variables de entorno:
```bash
# Para TestPyPI
UV_PUBLISH_URL="https://test.pypi.org/legacy/" \
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="pypi-tu-token-testpypi" \
uv publish

# Para PyPI
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="pypi-tu-token-pypi" \
uv publish
```

## 🔨 Paso 2: Preparar el Paquete

### 2.1 Verificar que estés en el directorio correcto
```bash
cd ${HOME}/terraform-var-manager/terraform-var-manager
pwd  # Debe mostrar la ruta del paquete
```

### 2.2 Limpiar builds anteriores
```bash
./dev.sh clean
```

### 2.3 Ejecutar tests finales
```bash
./dev.sh test
```

### 2.4 Construir el paquete
```bash
./dev.sh build
```

### 2.5 Verificar archivos generados
```bash
ls -la dist/
# Debes ver:
# terraform_var_manager-1.0.0.tar.gz
# terraform_var_manager-1.0.0-py3-none-any.whl
```

## 🧪 Paso 3: Publicar en TestPyPI (Recomendado primero)

### 3.1 Publicar en TestPyPI usando dev.sh (Recomendado)
```bash
# El script lee automáticamente desde ~/.pypirc
./dev.sh publish-test
```

**Lo que hace el script:**
- Lee automáticamente el token de TestPyPI desde `~/.pypirc`
- Configura las variables de entorno necesarias para UV
- Publica el paquete en TestPyPI
- Muestra el enlace para verificar la publicación

### 3.2 Publicar en TestPyPI manualmente
```bash
# Usando variables de entorno directamente
UV_PUBLISH_URL="https://test.pypi.org/legacy/" \
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="tu-token-testpypi" \
uv publish
```

### 3.3 Verificar la publicación
- Ve a: https://test.pypi.org/project/terraform-var-manager/
- Verifica que aparezca la versión 1.0.0
- Revisa que los metadatos sean correctos

### 3.3 Probar instalación desde TestPyPI
```bash
# En un entorno virtual nuevo
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ terraform-var-manager

# Probar que funcione
terraform-var-manager --help
```

## 🚀 Paso 4: Publicar en PyPI (Producción)

### 4.1 Publicar en PyPI usando dev.sh (Recomendado)
```bash
# El script lee automáticamente desde ~/.pypirc y pide confirmación
./dev.sh publish
```

**Lo que hace el script:**
- Lee automáticamente el token de PyPI desde `~/.pypirc`
- Solicita confirmación explícita antes de publicar
- Configura las variables de entorno necesarias para UV
- Publica el paquete en PyPI de producción
- Muestra el enlace para verificar la publicación

### 4.2 Publicar en PyPI manualmente
```bash
# Usando variables de entorno directamente
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="tu-token-pypi" \
uv publish
```

### 4.3 Verificar la publicación
- Ve a: https://pypi.org/project/terraform-var-manager/
- Verifica que aparezca la versión 1.0.0

### 4.3 Probar instalación desde PyPI
```bash
# En un entorno virtual nuevo
pip install terraform-var-manager

# Probar que funcione
terraform-var-manager --help
```

## 🔍 Paso 5: Verificaciones Post-Publicación

### 5.1 Verificar información del paquete
```bash
pip show terraform-var-manager
```

### 5.2 Verificar que los entry points funcionen
```bash
terraform-var-manager --version
tfvar-manager --version
```

### 5.3 Verificar la página de PyPI
- Descripción correcta
- Badges funcionando
- Enlaces a GitHub
- Clasificadores correctos

## 📋 Checklist de Pre-Publicación

- [ ] Tests pasando (3/3)
- [ ] Versión 1.0.0 en pyproject.toml
- [ ] Versión 1.0.0 en __init__.py
- [ ] README.md actualizado
- [ ] LICENSE incluido
- [ ] Metadatos correctos en pyproject.toml
- [ ] Archivos dist/ generados
- [ ] CLI funciona correctamente

## 🛠️ Comandos Rápidos de Referencia

```bash
# Workflow completo usando dev.sh (Lee automáticamente ~/.pypirc)
./dev.sh clean
./dev.sh test
./dev.sh build

# Publicar en TestPyPI (usa ~/.pypirc automáticamente)
./dev.sh publish-test

# Publicar en PyPI (usa ~/.pypirc automáticamente, pide confirmación)
./dev.sh publish

# Comandos manuales alternativos
# TestPyPI
UV_PUBLISH_URL="https://test.pypi.org/legacy/" \
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="TU_TOKEN_TESTPYPI" \
uv publish

# PyPI
UV_PUBLISH_USERNAME="__token__" \
UV_PUBLISH_PASSWORD="TU_TOKEN_PYPI" \
uv publish
```

## ⚠️ Solución de Problemas Comunes

### Error: "Could not find testpypi token in ~/.pypirc"
- Verifica que el archivo `~/.pypirc` existe: `ls -la ~/.pypirc`
- Asegúrate de que tenga la sección `[testpypi]` con `username` y `password`
- El password debe ser el token completo que empieza con `pypi-`

### Error: "Could not find pypi token in ~/.pypirc"
- Agrega la sección `[pypi]` a tu archivo `~/.pypirc`
- Incluye `username = __token__` y `password = pypi-tu-token`

### Error: "File already exists"
- El paquete ya fue publicado con esa versión
- Incrementa la versión en `pyproject.toml` e `__init__.py`

### Error: "Invalid credentials"
- Verifica que el token sea correcto y no haya espacios extra
- Asegúrate de usar `__token__` como username
- Regenera el token si es necesario

### Error: "Package name already taken"
- Alguien más ya usó ese nombre
- Cambia el nombre en `pyproject.toml`

### Error: "Missing required fields"
- Verifica que `pyproject.toml` tenga todos los campos requeridos
- Revisa que `README.md` y `LICENSE` existan

### Script dev.sh no encuentra ~/.pypirc
- Verifica permisos: `chmod 600 ~/.pypirc`
- Asegúrate de que el formato sea correcto (sin espacios extra)
- Prueba el comando manual como alternativa

## 🎉 ¡Éxito!

Una vez publicado, tu paquete estará disponible para instalación global:

```bash
pip install terraform-var-manager
```

Y aparecerá en:
- https://pypi.org/project/terraform-var-manager/
- Búsquedas de PyPI
- pip install commands

---

**Nota**: Una vez publicada una versión en PyPI, no se puede sobrescribir. Solo se puede publicar versiones nuevas.
