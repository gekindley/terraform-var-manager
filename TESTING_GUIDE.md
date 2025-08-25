# 🧪 Guía Completa de Testing en terraform-var-manager

## 📋 Tabla de Contenidos

1. [Arquitectura de Testing](#arquitectura-de-testing)
2. [Framework y Herramientas](#framework-y-herramientas)
3. [Tests Existentes Explicados](#tests-existentes-explicados)
4. [Estructura de Testing](#estructura-de-testing)
5. [Ejecutar Tests](#ejecutar-tests)
6. [Cobertura de Código](#cobertura-de-código)
7. [Mejores Prácticas Implementadas](#mejores-prácticas-implementadas)
8. [Agregar Nuevos Tests](#agregar-nuevos-tests)
9. [Testing de Integración](#testing-de-integración)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura de Testing

### Filosofía de Testing:
- **Unit Tests**: Probar funciones individuales aisladamente
- **Test-Driven Development**: Tests como documentación viviente
- **Cobertura Incremental**: Empezar con funciones críticas
- **Mantenibilidad**: Tests fáciles de leer y mantener

### Estructura Implementada:
```
terraform-var-manager/
├── tests/
│   ├── __init__.py              # Configuración de tests
│   ├── test_utils.py            # Tests de utilidades ✅
│   ├── test_api_client.py       # Tests del cliente API (pendiente)
│   ├── test_variable_manager.py # Tests del manager (pendiente)
│   ├── test_main.py            # Tests del CLI (pendiente)
│   └── fixtures/               # Datos de prueba (pendiente)
│       ├── sample_variables.json
│       └── test_responses.json
└── src/terraform_var_manager/
    ├── utils.py                 # ✅ 100% testeado
    ├── api_client.py           # ⚠️ Pendiente
    ├── variable_manager.py     # ⚠️ Pendiente
    └── main.py                 # ⚠️ Pendiente
```

---

## 🛠️ Framework y Herramientas

### Herramientas Utilizadas:

#### **pytest** - Framework de Testing:
```toml
# En pyproject.toml
[dependency-groups]
dev = [
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
]
```

#### **pytest-cov** - Cobertura de Código:
- Genera reportes de cobertura
- Identifica código no testeado
- Integración con pytest

#### **Configuración en pyproject.toml**:
```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/terraform_var_manager"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
]
```

---

## 🔍 Tests Existentes Explicados

### 📄 `test_utils.py` - Tests de Funciones Utilitarias

#### **1. `test_extract_group()`**

**Propósito**: Verificar que la función `extract_group()` extrae correctamente los nombres de grupos de las descripciones.

```python
def test_extract_group():
    """Test group extraction from descriptions."""
    assert extract_group("[api_gateway], sensitive") == "api_gateway"
    assert extract_group("keep_in_all_workspaces, [database]") == "database"
    assert extract_group("sensitive") == "default"
    assert extract_group("") == "default"
    assert extract_group(None) == "default"
```

**¿Qué está probando?**

| Test Case | Input | Expected Output | Razón |
|-----------|-------|-----------------|-------|
| `"[api_gateway], sensitive"` | `"api_gateway"` | Extrae grupo entre corchetes |
| `"keep_in_all_workspaces, [database]"` | `"database"` | Encuentra grupo sin importar posición |
| `"sensitive"` | `"default"` | Sin corchetes = grupo por defecto |
| `""` | `"default"` | String vacío = grupo por defecto |
| `None` | `"default"` | Valor nulo = grupo por defecto |

**Casos Edge probados**:
- ✅ Múltiples etiquetas con grupo
- ✅ Orden diferente de etiquetas
- ✅ Sin grupo especificado
- ✅ Input vacío o nulo

---

#### **2. `test_format_var_line()`**

**Propósito**: Verificar que la función `format_var_line()` genera líneas de variables con el formato correcto para archivos `.tfvars`.

```python
def test_format_var_line():
    """Test variable line formatting."""
    # Basic variable
    result = format_var_line("var1", "value1", "default")
    assert result == 'var1 = "value1" # [default]'
    
    # Sensitive variable
    result = format_var_line("var2", "secret", "api", sensitive=True)
    assert result == 'var2 = "secret" # [api], sensitive'
    
    # HCL variable
    result = format_var_line("var3", '["a", "b"]', "list", hcl=True)
    assert result == 'var3 = ["a", "b"] # [list], hcl'
    
    # Keep in all workspaces
    result = format_var_line("var4", "value4", "config", keep=True)
    assert result == 'var4 = "value4" # [config], keep_in_all_workspaces'
```

**¿Qué está probando?**

| Caso de Prueba | Parámetros | Output Esperado | Funcionalidad |
|----------------|------------|-----------------|---------------|
| **Variable básica** | `key="var1", value="value1", group="default"` | `'var1 = "value1" # [default]'` | Formato estándar |
| **Variable sensible** | `sensitive=True` | `'var2 = "secret" # [api], sensitive'` | Tag de sensibilidad |
| **Variable HCL** | `hcl=True` | `'var3 = ["a", "b"] # [list], hcl'` | Sin comillas para HCL |
| **Keep tag** | `keep=True` | `'var4 = "value4" # [config], keep_in_all_workspaces'` | Tag especial |

**Aspectos críticos testeados**:
- ✅ Formato de comillas para strings vs HCL
- ✅ Orden y formato de tags
- ✅ Combinación de múltiples flags
- ✅ Sintaxis correcta de .tfvars

---

#### **3. `test_group_and_format_vars_for_tfvars()`**

**Propósito**: Verificar que la función `group_and_format_vars_for_tfvars()` agrupa variables por categorías y genera el formato final de archivo .tfvars.

```python
def test_group_and_format_vars_for_tfvars():
    """Test grouping and formatting variables."""
    variables_dict = {
        "api_var": {
            "attributes": {
                "key": "api_var",
                "value": "api_value",
                "description": "[api_gateway], keep_in_all_workspaces",
                "sensitive": False,
                "hcl": False,
            }
        },
        "db_var": {
            "attributes": {
                "key": "db_var",
                "value": "db_value",
                "description": "[database], sensitive",
                "sensitive": True,
                "hcl": False,
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    # Check that it contains expected groups
    assert "api_gateway" in result
    assert "database" in result
    assert "api_var" in result
    assert "db_var" in result
    assert "_SECRET" in result  # sensitive variable should be masked
```

**¿Qué está probando?**

| Verificación | Descripción | Importancia |
|--------------|-------------|-------------|
| **Presencia de grupos** | `"api_gateway" in result` | Verifica agrupación correcta |
| **Variables incluidas** | `"api_var" in result` | Todas las variables están presentes |
| **Enmascaramiento sensible** | `"_SECRET" in result` | Variables sensibles se ocultan |
| **Formato de salida** | String con formato .tfvars | Output usable |

**Input de prueba explicado**:
```python
# Variable 1: api_var
{
    "key": "api_var",                                    # Nombre de variable
    "value": "api_value",                               # Valor real
    "description": "[api_gateway], keep_in_all_workspaces", # Grupo + tag especial
    "sensitive": False,                                 # No sensible
    "hcl": False                                       # String normal
}

# Variable 2: db_var
{
    "key": "db_var",                                   # Nombre de variable
    "value": "db_value",                              # Valor real (será enmascarado)
    "description": "[database], sensitive",           # Grupo diferente + sensible
    "sensitive": True,                                # ¡Sensible!
    "hcl": False                                     # String normal
}
```

**Output esperado**:
```hcl
# ========== api_gateway ==========
api_var = "api_value" # [api_gateway], keep_in_all_workspaces

# ========== database ==========
db_var = "_SECRET" # [database], sensitive
```

---

## 🚀 Ejecutar Tests

### Comandos Disponibles:

#### **1. Usando el script de desarrollo:**
```bash
cd terraform-var-manager/

# Ejecutar todos los tests con cobertura
./dev.sh test

# Output típico:
=== Running Tests ===
============== test session starts ==============
tests/test_utils.py ...                    [100%]
============== tests coverage ==============
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/terraform_var_manager/__init__.py        7      0   100%
src/terraform_var_manager/utils.py          42      0   100%
src/terraform_var_manager/api_client.py     52     38    27%   22-24, 31-37, ...
-----------------------------------------------------------------------
TOTAL                                       324    247    24%
============== 3 passed in 0.22s ==============
✓ Tests completed
```

#### **2. Usando UV directamente:**
```bash
# Tests básicos
uv run pytest

# Tests con verbose
uv run pytest -v

# Tests con cobertura
uv run pytest --cov=src/terraform_var_manager

# Tests con cobertura y reporte detallado
uv run pytest --cov=src/terraform_var_manager --cov-report=html
```

#### **3. Tests específicos:**
```bash
# Solo tests de utils
uv run pytest tests/test_utils.py

# Solo una función específica
uv run pytest tests/test_utils.py::test_extract_group

# Con output detallado
uv run pytest tests/test_utils.py::test_extract_group -v -s
```

---

## 📊 Cobertura de Código

### Estado Actual de Cobertura:

| Módulo | Statements | Missing | Coverage | Estado |
|--------|------------|---------|----------|--------|
| `__init__.py` | 7 | 0 | 100% | ✅ Completo |
| `utils.py` | 42 | 0 | 100% | ✅ Completo |
| `api_client.py` | 52 | 38 | 27% | ⚠️ Pendiente |
| `variable_manager.py` | 160 | 146 | 9% | ⚠️ Pendiente |
| `main.py` | 63 | 63 | 0% | ⚠️ Pendiente |

### Generar Reporte HTML:
```bash
# Generar reporte HTML detallado
uv run pytest --cov=src/terraform_var_manager --cov-report=html

# Abrir reporte
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Interpretar Cobertura:
- **Verde**: Líneas ejecutadas durante tests ✅
- **Rojo**: Líneas no ejecutadas durante tests ❌
- **Excluido**: Líneas marcadas como `# pragma: no cover`

---

## ✅ Mejores Prácticas Implementadas

### 1. **Naming Conventions**:
```python
# ✅ Nombres descriptivos
def test_extract_group():           # Función que se está probando
def test_format_var_line():        # Comportamiento específico
def test_group_and_format_vars_for_tfvars():  # Función completa
```

### 2. **Docstrings Informativos**:
```python
def test_extract_group():
    """Test group extraction from descriptions."""  # ✅ Propósito claro
```

### 3. **Casos Edge Incluidos**:
```python
# ✅ Probando casos límite
assert extract_group("") == "default"        # String vacío
assert extract_group(None) == "default"      # Valor nulo
```

### 4. **Assertions Claras**:
```python
# ✅ Verificaciones específicas
assert "api_gateway" in result               # Contenido esperado
assert "_SECRET" in result                   # Comportamiento de seguridad
```

### 5. **Test Data Realista**:
```python
# ✅ Datos que reflejan uso real
"description": "[api_gateway], keep_in_all_workspaces"
```

---

## 🆕 Agregar Nuevos Tests

### Template para Nuevos Tests:

#### **1. Test de Función Simple:**
```python
def test_nueva_funcion():
    """Test description of what this function does."""
    # Arrange (preparar datos)
    input_data = "test_input"
    expected = "expected_output"
    
    # Act (ejecutar función)
    result = nueva_funcion(input_data)
    
    # Assert (verificar resultado)
    assert result == expected
```

#### **2. Test con Múltiples Casos:**
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("case1", "result1"),
    ("case2", "result2"),
    ("edge_case", "edge_result"),
])
def test_multiple_cases(input, expected):
    """Test function with multiple input cases."""
    assert function_to_test(input) == expected
```

#### **3. Test con Excepciones:**
```python
def test_function_raises_exception():
    """Test that function raises appropriate exception."""
    with pytest.raises(ValueError, match="Expected error message"):
        function_that_should_fail("invalid_input")
```

### Próximos Tests Recomendados:

#### **`test_api_client.py`:**
```python
import pytest
from unittest.mock import Mock, patch
from terraform_var_manager.api_client import TerraformCloudClient

def test_get_variables_success():
    """Test successful variable retrieval."""
    # Mock HTTP response
    # Test client behavior
    pass

def test_get_variables_api_error():
    """Test handling of API errors."""
    # Mock failed response
    # Verify exception handling
    pass
```

#### **`test_variable_manager.py`:**
```python
def test_download_variables():
    """Test downloading variables to file."""
    # Mock API client
    # Test file generation
    pass

def test_upload_variables():
    """Test uploading variables from file."""
    # Mock file reading
    # Test API calls
    pass
```

#### **`test_main.py`:**
```python
def test_cli_help():
    """Test CLI help output."""
    # Test argument parser
    pass

def test_cli_download_command():
    """Test download command execution."""
    # Mock VariableManager
    # Test CLI integration
    pass
```

---

## 🔗 Testing de Integración

### Tipos de Tests Pendientes:

#### **1. Integration Tests:**
```python
# test_integration.py
def test_end_to_end_download():
    """Test complete download workflow."""
    # Use real API (or comprehensive mock)
    # Verify file output format
    # Check all components working together
```

#### **2. Fixture Tests:**
```python
# test_fixtures.py
def test_with_sample_terraform_data():
    """Test with realistic Terraform variable data."""
    # Load fixture data
    # Process through complete pipeline
    # Verify output matches expectations
```

#### **3. CLI Integration:**
```python
# test_cli_integration.py
def test_cli_commands_integration():
    """Test CLI commands end-to-end."""
    # Use subprocess to call CLI
    # Verify exit codes
    # Check output files
```

---

## 🚨 Troubleshooting

### Problemas Comunes:

#### **1. Import Errors:**
```bash
# Error: ModuleNotFoundError: No module named 'terraform_var_manager'
# Solución:
cd terraform-var-manager/
uv run pytest  # UV maneja el path automáticamente
```

#### **2. Test Discovery Issues:**
```bash
# Error: No tests found
# Verificar estructura:
tests/
├── __init__.py  # ✅ Debe existir
└── test_*.py    # ✅ Nombres deben empezar con 'test_'
```

#### **3. Coverage Issues:**
```bash
# Error: Coverage no incluye todos los archivos
# Verificar configuración en pyproject.toml:
[tool.coverage.run]
source = ["src/terraform_var_manager"]  # ✅ Path correcto
```

#### **4. Assertion Errors:**
```python
# Error en test - debugging:
def test_debug_example():
    result = function_to_test("input")
    print(f"Result: {result}")  # ✅ Agregar prints temporales
    print(f"Type: {type(result)}")
    assert result == expected
```

### Comandos de Debug:

```bash
# Ejecutar con output detallado
uv run pytest -v -s

# Ejecutar solo tests que fallan
uv run pytest --lf

# Parar en primer fallo
uv run pytest -x

# Mostrar variables locales en fallos
uv run pytest --tb=long
```
