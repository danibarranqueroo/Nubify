#!/usr/bin/env python3
"""
Configuración centralizada de comandos de Nubify
"""

import os

# Comandos disponibles en nubify
AVAILABLE_COMMANDS = {
    "test": {
        "description": "Prueba la conexión con AWS",
        "usage": "nubify test",
        "example": "nubify test"
    },
    "list-resources": {
        "description": "Lista todos los recursos AWS disponibles",
        "usage": "nubify list-resources",
        "example": "nubify list-resources"
    },
    "list-templates": {
        "description": "Lista las plantillas disponibles para desplegar",
        "usage": "nubify list-templates",
        "example": "nubify list-templates"
    },
    "template-details": {
        "description": "Muestra detalles de una plantilla específica",
        "usage": "nubify template-details <nombre>",
        "example": "nubify template-details ec2-basic"
    },
    "estimate-costs": {
        "description": "Estima los costes de una plantilla",
        "usage": "nubify estimate-costs <plantilla> [--parameters KEY=VALUE]",
        "example": "nubify estimate-costs ec2-basic -p InstanceType=t3.micro"
    },
    "deploy": {
        "description": "Despliega una plantilla de CloudFormation",
        "usage": "nubify deploy <plantilla> <stack-name> [--parameters KEY=VALUE]",
        "example": "nubify deploy ec2-basic my-stack -p InstanceType=t3.micro"
    },
    "list-stacks": {
        "description": "Lista los stacks de CloudFormation desplegados",
        "usage": "nubify list-stacks",
        "example": "nubify list-stacks"
    },
    "stack-resources": {
        "description": "Muestra los recursos de un stack específico",
        "usage": "nubify stack-resources <stack-name>",
        "example": "nubify stack-resources my-stack"
    },
    "delete-stack": {
        "description": "Elimina un stack de CloudFormation",
        "usage": "nubify delete-stack <stack-name>",
        "example": "nubify delete-stack my-stack"
    },
    "chat": {
        "description": "Inicia el chatbot interactivo",
        "usage": "nubify chat",
        "example": "nubify chat"
    },
    "help": {
        "description": "Muestra ayuda general",
        "usage": "nubify help",
        "example": "nubify help"
    }
}

# Servicios soportados para crear plantillas
SUPPORTED_SERVICES = ['ec2', 'lambda', 's3', 'rds']

# Plantillas disponibles
AVAILABLE_TEMPLATES = [
    'ec2-basic',
    'ec2-basic-no-key', 
    'lambda-function',
    's3-bucket'
]

def get_command_info(command_name: str) -> dict:
    """Obtiene información de un comando específico"""
    return AVAILABLE_COMMANDS.get(command_name, {})

def get_all_commands() -> dict:
    """Obtiene todos los comandos disponibles"""
    return AVAILABLE_COMMANDS

def is_command_available(command_name: str) -> bool:
    """Verifica si un comando está disponible"""
    return command_name in AVAILABLE_COMMANDS

def is_service_supported(service_name: str) -> bool:
    """Verifica si un servicio está soportado para crear plantillas"""
    return service_name.lower() in SUPPORTED_SERVICES

def get_supported_services() -> list:
    """Obtiene la lista de servicios soportados"""
    return SUPPORTED_SERVICES

def get_available_templates() -> list:
    """Obtiene la lista de plantillas disponibles"""
    try:
        # Obtener la ruta del directorio templates
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, '..', 'templates')
        
        # Verificar si el directorio existe
        if not os.path.exists(templates_dir):
            return AVAILABLE_TEMPLATES
        
        # Obtener todas las plantillas del directorio
        templates = []
        for filename in os.listdir(templates_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                templates.append(filename)
        
        # Si no hay plantillas en el directorio, usar las predefinidas
        if not templates:
            return AVAILABLE_TEMPLATES
        
        return sorted(templates)
        
    except Exception as e:
        print(f"Error al obtener plantillas del directorio: {e}")
        return AVAILABLE_TEMPLATES
