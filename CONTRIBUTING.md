# Guía de Contribución

¡Gracias por tu interés en contribuir a Nubify! Este documento te ayudará a configurar el entorno de desarrollo y contribuir al proyecto.

## Configuración del Entorno de Desarrollo

### Prerrequisitos

- Python 3.8 o superior
- Poetry (recomendado) o pip
- Git

### Instalación

1. **Fork y clona el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/nubify.git
   cd nubify
   ```

2. **Instala Poetry** (si no está instalado)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Instala las dependencias**
   ```bash
   poetry install --with dev
   ```

4. **Activa el entorno virtual**
   ```bash
   poetry env activate
   source $(poetry env info --path)/bin/activate
   ```

5. **Configura las variables de entorno**
   ```bash
   cp env.example .env
   # Edita .env con tus credenciales de AWS
   ```

## Estructura del Proyecto

```
nubify/
├── src/                    # Código fuente principal
│   ├── main.py            # CLI principal
│   ├── config.py          # Configuración
│   ├── aws_client.py      # Cliente AWS
│   ├── templates.py       # Gestión de plantillas
│   └── deployer.py        # Despliegue
├── templates/              # Plantillas CloudFormation
├── tests/                  # Tests unitarios
├── docs/                   # Documentación
└── pyproject.toml         # Configuración Poetry
```

## Desarrollo

### Comandos útiles

```bash
# Ejecutar tests
poetry run pytest

# Ejecutar tests con cobertura
poetry run pytest --cov=src

# Formatear código
poetry run black src/
poetry run isort src/

# Verificar tipos
poetry run mypy src/

# Linting
poetry run flake8 src/

# Ejecutar todos los checks
poetry run black src/ && poetry run isort src/ && poetry run mypy src/ && poetry run flake8 src/
```

### Flujo de trabajo

1. **Crea una nueva rama**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Desarrolla tu funcionalidad**
   - Escribe código siguiendo las convenciones
   - Añade tests para nueva funcionalidad
   - Actualiza documentación si es necesario

3. **Ejecuta los tests**
   ```bash
   poetry run pytest
   ```

4. **Formatea el código**
   ```bash
   poetry run black src/
   poetry run isort src/
   ```

5. **Verifica tipos y linting**
   ```bash
   poetry run mypy src/
   poetry run flake8 src/
   ```

6. **Commit y push**
   ```bash
   git add .
   git commit -m "feat: añadir nueva funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

7. **Crea un Pull Request**

## Convenciones de Código

### Estilo de código

- Usamos **Black** para formateo automático
- **isort** para ordenar imports
- **mypy** para verificación de tipos
- **flake8** para linting

### Convenciones de commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests
- `chore:` Cambios en build, config, etc.

### Estructura de tests

```python
# tests/test_module.py
import pytest
from src.module import function

class TestModule:
    def test_function_should_work(self):
        """Test que verifica que la función funciona correctamente"""
        result = function()
        assert result is not None
```

## Plantillas CloudFormation

### Añadir nuevas plantillas

1. Crea un archivo YAML en `templates/`
2. Usa el formato CloudFormation estándar
3. Incluye descripción y parámetros bien documentados
4. Añade tests para la plantilla

### Ejemplo de plantilla

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Descripción de la plantilla'

Parameters:
  ParameterName:
    Type: String
    Description: Descripción del parámetro

Resources:
  ResourceName:
    Type: AWS::Service::Resource
    Properties:
      PropertyName: value

Outputs:
  OutputName:
    Description: Descripción del output
    Value: !Ref ResourceName
```

## Reportar Bugs

1. Usa el template de issue de GitHub
2. Incluye información del sistema
3. Describe los pasos para reproducir
4. Incluye logs de error si es posible

## Solicitar Funcionalidades

1. Abre un issue con la etiqueta `enhancement`
2. Describe la funcionalidad deseada
3. Explica el caso de uso
4. Discute la implementación si es necesario

## Preguntas

Si tienes preguntas sobre el desarrollo:

1. Revisa la documentación
2. Busca en issues existentes
3. Abre un issue con la etiqueta `question`

## Licencia

Al contribuir, aceptas que tu código será licenciado bajo la licencia MIT del proyecto.

¡Gracias por contribuir a Nubify! 🚀 