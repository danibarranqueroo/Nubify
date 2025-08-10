# Guía de Contribución

¡Gracias por tu interés en contribuir a Nubify! Este documento te ayudará a configurar el entorno de desarrollo y contribuir al proyecto.

## Configuración del Entorno de Desarrollo

### Prerrequisitos

- Python 3.9 o superior
- Poetry
- Git
- Credenciales de AWS configuradas
- API Key de Gemini (opcional, para funcionalidad del chatbot)

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
   # Edita .env con tus credenciales de AWS y Gemini
   ```

## Estructura del Proyecto

```
nubify/
├── src/                    # Código fuente principal
│   ├── main.py            # CLI principal con Click
│   ├── config.py          # Configuración y variables de entorno
│   ├── aws_client.py      # Cliente AWS y operaciones con servicios
│   ├── templates.py       # Gestión de plantillas y AWS Pricing API
│   ├── deployer.py        # Despliegue de stacks con CloudFormation
│   └── chat.py            # Chatbot inteligente con Gemini AI
├── templates/              # Plantillas CloudFormation predefinidas
│   ├── ec2-basic.yaml
│   ├── ec2-basic-no-key.yaml
│   ├── s3-bucket.yaml
│   ├── lambda-function.yaml
│   └── rds-basic.yaml
├── tests/                  # Tests unitarios
│   ├── __init__.py
│   ├── test_main.py       # Tests para CLI principal
│   ├── test_config.py     # Tests para configuración
│   ├── test_aws_client.py # Tests para cliente AWS
│   ├── test_templates.py  # Tests para gestión de plantillas
│   ├── test_deployer.py   # Tests para despliegue
│   └── test_chat.py       # Tests para chatbot
├── pyproject.toml         # Configuración Poetry y dependencias
└── env.example            # Variables de entorno de ejemplo
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

### Funcionalidades Principales

#### CLI con Click
- **main.py**: Interfaz de línea de comandos principal
- Comandos: `test`, `list-resources`, `list-templates`, `deploy`, `estimate-costs`, `chat`, `help`
- Soporte para flags: `--verbose` (`-v`), `--parameters` (`-p`), `--yes` (`-y`)

#### Gestión de Plantillas
- **templates.py**: Manejo de plantillas CloudFormation y estimación de costes
- Integración con AWS Pricing API para precios reales
- Fallback a estimaciones estáticas si la API no está disponible
- Soporte para parámetros personalizables

#### Despliegue con CloudFormation
- **deployer.py**: Gestión de stacks con waiters mejorados
- Progress bars y monitoreo en tiempo real
- Manejo de errores y timeouts automáticos

#### Chatbot Inteligente
- **chat.py**: Asistente con IA usando Google Gemini
- Explicación de servicios AWS
- Creación de plantillas personalizadas
- Ayuda interactiva con comandos

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
5. Actualiza la estimación de costes en `templates.py` si es necesario

### Plantillas actuales

- **ec2-basic.yaml**: Instancia EC2 con KeyPair
- **ec2-basic-no-key.yaml**: Instancia EC2 sin KeyPair (recomendada)
- **s3-bucket.yaml**: Bucket S3 seguro
- **lambda-function.yaml**: Función Lambda básica
- **rds-basic.yaml**: Instancia RDS MySQL

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

## Integración con AWS

### Servicios soportados

- **EC2**: Instancias de computación
- **S3**: Almacenamiento de objetos
- **Lambda**: Funciones serverless
- **RDS**: Bases de datos relacionales
- **CloudFormation**: Orquestación de infraestructura

### Credenciales requeridas

```bash
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Permisos mínimos

- `ec2:*`
- `s3:*`
- `lambda:*`
- `rds:*`
- `cloudformation:*`
- `pricing:*` (para estimación de costes)

## Integración con Gemini AI

### Configuración

```bash
GEMINI_API_KEY=tu_gemini_api_key
```

### Funcionalidades del chatbot

- Explicación de servicios AWS
- Creación de plantillas personalizadas
- Ayuda con comandos de nubify
- Resolución de problemas
- Recomendaciones de servicios

### Dependencias

- `google-generativeai`: Cliente oficial de Google
- Modelo: `gemini-1.5-flash`

## Reportar Bugs

1. Usa el template de issue de GitHub
2. Incluye información del sistema
3. Describe los pasos para reproducir
4. Incluye logs de error si es posible
5. Especifica la versión de Python y dependencias

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