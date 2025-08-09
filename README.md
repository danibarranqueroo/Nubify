# Nubify

Nubify es una plataforma desarrollada en Python que simplifica la gestión de servicios cloud, ahora mismo cuenta únicamente con uso por CLI pero en un futuro se planea la creación de una interfaz web accesible y la incorporación de un chatbot técnico inteligente.

## Descripción

Nubify está diseñado para usuarios que quieren comenzar en AWS pero encuentran muy complicada su UI y tienen miedo de crear algo mal configurado que incurra en altos costes.

## Fases de Desarrollo

### Fase 1: Funcionamiento por CLI ✅ COMPLETADA
- ✅ Inicio de sesión con variables de entorno
- ✅ Mostrar recursos disponibles en AWS
- ✅ Comandos con --help para recursos a desplegar
- ✅ **Estimación de costes realista con AWS Pricing API**
- ✅ Despliegue y eliminación de stacks
- ✅ Gestión de plantillas CloudFormation

### Fase 2: Interfaz Web (Pendiente)
- Aplicación web en localhost
- Funcionamiento tanto CLI como web
- Despliegue con Docker

### Fase 3: Chatbot Inteligente ✅ COMPLETADA
- ✅ Chatbot que recomiende servicios
- ✅ Explicación de la estimación de costes
- ✅ Explicación y recomendación de servicios
- ✅ Creación de plantillas personalizadas
- ✅ Asistencia interactiva con IA (Gemini)

## Características Principales

### 🎯 **Estimación de Costes Inteligente**
- **AWS Pricing API integrada** - Precios reales y actualizados
- **Estimaciones por servicio** - EC2, S3, Lambda con precios específicos
- **Parámetros personalizables** - InstanceType, MemorySize, etc.
- **Fallback robusto** - Estimaciones estáticas si API no está disponible
- **Unidades correctas** - /mes para servicios, /GB-mes para S3

### 🚀 **Gestión de Stacks**
- **Despliegue simplificado** - Un comando para crear recursos
- **Eliminación segura** - Confirmación antes de eliminar
- **Monitoreo en tiempo real** - Estado de despliegue con progress bars
- **Manejo de errores** - Timeouts y fallbacks automáticos

### 📋 **Plantillas Predefinidas**
- **Configuración segura** - Sin misconfiguraciones
- **Parámetros validados** - Verificación antes del despliegue
- **Documentación integrada** - Descripción y detalles de cada plantilla

## Instalación

### 🚀 **Instalación Rápida (Recomendada)**

```bash
# Instalar nubify globalmente desde GitHub
pipx install git+https://github.com/danibarranqueroo/nubify.git

# Configurar variables de entorno
export AWS_ACCESS_KEY_ID=tu_access_key
export AWS_SECRET_ACCESS_KEY=tu_secret_key
export AWS_DEFAULT_REGION=us-east-1
export GEMINI_API_KEY=tu_gemini_api_key

# ¡Listo! Ya puedes usar nubify
nubify --help
```

### 🔧 **Instalación para Desarrollo**

#### Prerrequisitos
- Python 3.9 o superior
- Poetry
- Credenciales de AWS configuradas

#### Instalación con Poetry

```bash
# Clonar el repositorio
git clone <repository-url>
cd nubify

# Instalar Poetry si no está instalado
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias y configurar el entorno
poetry install

# Activar el entorno virtual
poetry env activate
source $(poetry env info --path)/bin/activate

# Crear archivo de configuración
cp env.example .env
# Editar .env con tus credenciales de AWS
```

## Configuración

1. Crear archivo `.env` con tus credenciales AWS:
```bash
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
```

2. Asegúrate de tener permisos adecuados en AWS para los servicios que vas a usar.

## Uso

### Comandos básicos

```bash
# Ver ayuda general
nubify --help

# Probar conexión con AWS
nubify test

# Listar recursos disponibles en AWS
nubify list-resources

# Ver plantillas disponibles
nubify list-templates

# Ver detalles de una plantilla
nubify template-details s3-bucket

# Estimación de costes con precios reales
nubify estimate-costs ec2-basic-no-key -p InstanceType=t3.micro

# Desplegar un recurso
nubify deploy s3-bucket my-stack -p BucketName=mi-bucket-unico

# Listar stacks desplegados
nubify list-stacks

# Ver recursos de un stack
nubify stack-resources my-stack

# Eliminar un stack
nubify delete-stack my-stack

# Iniciar chatbot interactivo
nubify chat
```

### Ejemplos de uso con estimación de costes

```bash
# Estimación de costes para EC2
nubify estimate-costs ec2-basic-no-key -p InstanceType=t3.small

# Estimación de costes para S3
nubify estimate-costs s3-bucket -p Versioning=Suspended

# Estimación de costes para Lambda
nubify estimate-costs lambda-function -p MemorySize=512

# Estimación de costes para RDS
nubify estimate-costs rds-basic -p DBInstanceClass=db.t3.small

# Desplegar con confirmación de costes
nubify deploy s3-bucket my-s3-stack -p BucketName=mi-bucket-unico

# Chatbot para asistencia inteligente
nubify chat
```

### 🤖 **Chatbot Inteligente**

Nubify incluye un chatbot interactivo que utiliza IA (Gemini) para ayudarte con:

- **Explicación de servicios AWS** - Qué es cada servicio y para qué sirve
- **Creación de plantillas** - Genera plantillas CloudFormation personalizadas
- **Ayuda con comandos** - Explica cómo usar nubify correctamente
- **Resolución de problemas** - Ayuda con errores comunes
- **Recomendaciones** - Sugiere servicios según tus necesidades

#### Configuración del Chatbot

1. Obtén una API key de Gemini en [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Añade la variable de entorno:
```bash
GEMINI_API_KEY=tu_gemini_api_key
```

#### Uso del Chatbot

```bash
# Iniciar chat interactivo
nubify chat

# Ejemplos de preguntas que puedes hacer:
# - "¿Qué es EC2 y para qué sirve?"
# - "Crea una plantilla para un bucket S3 con versionado"
# - "¿Cómo uso el comando deploy?"
# - "Tengo un error al desplegar, ¿qué hago?"
# - "¿Qué servicios AWS me recomiendas para una aplicación web?"
```
```

## Desarrollo

### Configuración del entorno de desarrollo

```bash
# Instalar dependencias de desarrollo
poetry install --with dev

# Activar el entorno virtual
poetry env activate
source $(poetry env info --path)/bin/activate

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
```

### Estructura del Proyecto

```
nubify/
├── src/                    # Código fuente
│   ├── __init__.py
│   ├── main.py            # CLI principal
│   ├── config.py          # Configuración AWS
│   ├── aws_client.py      # Cliente AWS
│   ├── templates.py       # Gestión de plantillas y Pricing API
│   ├── deployer.py        # Despliegue con waiters mejorados
│   └── chat.py            # Chatbot inteligente con IA
├── templates/              # Plantillas de CloudFormation
│   ├── ec2-basic-no-key.yaml
│   ├── s3-bucket.yaml
│   └── lambda-function.yaml
├── tests/                  # Tests unitarios
├── pyproject.toml         # Configuración Poetry
├── env.example            # Variables de entorno de ejemplo
└── README.md              # Este archivo
```

## Tecnologías Utilizadas

- **Python 3.8.1+**: Lenguaje principal
- **Poetry**: Gestión de dependencias y empaquetado
- **boto3**: SDK de AWS para Python
- **AWS Pricing API**: Estimación de costes reales
- **Click**: Framework para CLI
- **Rich**: Librería para interfaces de terminal bonitas
- **CloudFormation**: Para plantillas de infraestructura
- **Google Generative AI**: Chatbot inteligente con Gemini
- **pytest**: Framework de testing
- **Black**: Formateador de código
- **mypy**: Verificación de tipos

## Plantillas Disponibles

### EC2 Básica (`ec2-basic-no-key.yaml`)
- Instancia EC2 con configuración segura
- Security Group con puertos 22, 80, 443 abiertos
- **Sin requerimiento de KeyPair** - Más fácil de usar
- Parámetros: InstanceType

### S3 Bucket (`s3-bucket.yaml`)
- Bucket S3 con configuración segura
- Encriptación AES256 habilitada
- Bloqueo de acceso público
- **Sin BucketPolicy problemática** - Despliegue confiable
- Parámetros: BucketName, Versioning

### Lambda Function (`lambda-function.yaml`)
- Función Lambda con configuración básica
- IAM Role con permisos mínimos
- CloudWatch Logs configurado
- Parámetros: FunctionName, Runtime, MemorySize, Timeout

### RDS MySQL (`rds-basic.yaml`)
- Instancia RDS MySQL con configuración segura
- Security Group con puerto 3306 abierto
- Encriptación habilitada y backups automáticos
- Parámetros: DBInstanceClass, DBName, DBUsername, DBPassword, AllocatedStorage

## Estimación de Costes

### 🎯 **Características de la Estimación**

- **Precios reales de AWS** - Obtenidos via Pricing API
- **Estimaciones por parámetro** - Basadas en InstanceType, MemorySize, etc.
- **Unidades correctas** - /mes para servicios, /GB-mes para S3
- **Fallback automático** - Estimaciones estáticas si API no está disponible
- **Debug transparente** - Muestra qué productos se obtienen de la API

### 📊 **Ejemplo de Salida**

```bash
$ nubify estimate-costs ec2-basic-no-key -p InstanceType=t3.micro

🔍 Consultando AWS Pricing API para AmazonEC2...
✅ Respuesta recibida de Pricing API (1 productos)
💰 Precio EC2 (t3.micro): $0.010900/hora

Coste Total Estimado: $7.85/mes
```

## Contribución

Este es un proyecto de Trabajo Fin de Grado. Para contribuir, por favor contacta con el autor.

## Licencia

Este proyecto está bajo la licencia MIT.

## 🔄 **Gestión de Versiones**

### Actualizar nubify
```bash
pipx upgrade git+https://github.com/danibarranqueroo/nubify.git
```

### Desinstalar nubify
```bash
pipx uninstall nubify
```

### Ver versión instalada
```bash
nubify --version
```

## Roadmap

En caso de continuar con el desarrollo de este proyecto a futuro, se planea lo siguiente:

- Mejora de la inteligencia artifical del chatbot
- Posibilidad de uso desde telegram
- Añadir  más servicios de AWS
- Añadir más plantillas de CloudFormation
- Añadir integración con trivy para escaneo de vulnerabilidades en las plantillas
- Añadir integración con prowler para escaneo de vulnerabilidades en la infraestructura desplegada
- Estudiar la viabilidad de hacer la herramienta multicloud
