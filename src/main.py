#!/usr/bin/env python3
"""
Nubify CLI - Interfaz de línea de comandos para gestionar recursos AWS
"""

import click
import sys
from rich.console import Console
from rich.panel import Panel

from .config import config
from .aws_client import AWSClient
from .templates import TemplateManager
from .deployer import Deployer
from .chat import NubifyChatbot

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="Nubify")
def cli():
    """
    Nubify - Plataforma para simplificar la gestión de servicios cloud
    
    Una herramienta que permite gestionar recursos AWS de forma sencilla
    y segura, con estimación de costes y plantillas predefinidas.
    """
    pass

@cli.command()
def test():
    """Prueba la conexión con AWS"""
    console.print(Panel.fit(
        "[bold blue]Nubify[/bold blue]\n"
        "Probando conexión con AWS...",
        title="Test de Conexión"
    ))
    
    try:
        aws_client = AWSClient()
        if aws_client.test_connection():
            console.print("[green]✓ Conexión exitosa con AWS[/green]")
        else:
            console.print("[red]✗ Error al conectar con AWS[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def list_resources():
    """Lista todos los recursos AWS disponibles"""
    console.print(Panel.fit(
        "[bold blue]Nubify[/bold blue]\n"
        "Listando recursos AWS...",
        title="Recursos AWS"
    ))
    
    try:
        aws_client = AWSClient()
        aws_client.display_resources()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def list_templates():
    """Lista las plantillas disponibles para desplegar"""
    console.print(Panel.fit(
        "[bold blue]Nubify[/bold blue]\n"
        "Listando plantillas disponibles...",
        title="Plantillas"
    ))
    
    try:
        template_manager = TemplateManager()
        template_manager.display_templates()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('template_name')
def template_details(template_name):
    """Muestra detalles de una plantilla específica"""
    console.print(Panel.fit(
        f"[bold blue]Nubify[/bold blue]\n"
        f"Mostrando detalles de: {template_name}",
        title="Detalles de Plantilla"
    ))
    
    try:
        template_manager = TemplateManager()
        template_manager.display_template_details(template_name)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('template_name')
@click.option('--parameters', '-p', multiple=True, help='Parámetros en formato KEY=VALUE para estimación más precisa')
@click.option('--verbose', '-v', is_flag=True, help='Mostrar información detallada de la estimación')
def estimate_costs(template_name, parameters, verbose):
    """Estima los costes de una plantilla"""
    console.print(Panel.fit(
        f"[bold blue]Nubify[/bold blue]\n"
        f"Estimando costes de: {template_name}",
        title="Estimación de Costes"
    ))
    
    try:
        # Convertir parámetros
        params_dict = {}
        for param in parameters:
            if '=' in param:
                key, value = param.split('=', 1)
                params_dict[key] = value
        
        template_manager = TemplateManager()
        template_manager.display_cost_estimate(template_name, params_dict, verbose)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('template_name')
@click.argument('stack_name')
@click.option('--parameters', '-p', multiple=True, help='Parámetros en formato KEY=VALUE')
@click.option('--yes', '-y', is_flag=True, help='Confirmar despliegue sin preguntar')
@click.option('--verbose', '-v', is_flag=True, help='Mostrar información detallada de la estimación de costes')
def deploy(template_name, stack_name, parameters, yes, verbose):
    """Despliega una plantilla de CloudFormation"""
    
    # Validar credenciales
    if not config.validate_aws_credentials():
        console.print("[red]Error: Credenciales de AWS no configuradas[/red]")
        console.print("Por favor, configura las variables de entorno:")
        console.print("AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
        sys.exit(1)
    
    # Mostrar información del despliegue
    console.print(Panel.fit(
        f"[bold blue]Nubify[/bold blue]\n"
        f"Plantilla: {template_name}\n"
        f"Stack: {stack_name}\n"
        f"Parámetros: {len(parameters)}",
        title="Despliegue"
    ))
    
    try:
        # Obtener estimación de costes
        template_manager = TemplateManager()
        
        # Convertir parámetros
        params_dict = {}
        for param in parameters:
            if '=' in param:
                key, value = param.split('=', 1)
                params_dict[key] = value
        
        cost_estimate = template_manager.estimate_costs(template_name, params_dict, verbose)
        
        if 'error' not in cost_estimate:
            console.print(f"\n[bold]Coste Estimado: ${cost_estimate['estimated_monthly_cost']:.2f}/mes[/bold]")
        
        # Confirmar despliegue
        if not yes:
            if not click.confirm("¿Deseas continuar con el despliegue?"):
                console.print("[yellow]Despliegue cancelado[/yellow]")
                return
        
        # Realizar despliegue
        deployer = Deployer()
        success = deployer.deploy_template(template_name, stack_name, params_dict)
        
        if success:
            console.print("[green]✓ Despliegue completado exitosamente[/green]")
        else:
            console.print("[red]✗ Error en el despliegue[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def list_stacks():
    """Lista los stacks de CloudFormation desplegados"""
    console.print(Panel.fit(
        "[bold blue]Nubify[/bold blue]\n"
        "Listando stacks de CloudFormation...",
        title="Stacks"
    ))
    
    try:
        deployer = Deployer()
        deployer.display_stacks()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('stack_name')
def stack_resources(stack_name):
    """Muestra los recursos de un stack específico"""
    console.print(Panel.fit(
        f"[bold blue]Nubify[/bold blue]\n"
        f"Mostrando recursos del stack: {stack_name}",
        title="Recursos del Stack"
    ))
    
    try:
        deployer = Deployer()
        deployer.display_stack_resources(stack_name)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('stack_name')
@click.option('--yes', '-y', is_flag=True, help='Confirmar eliminación sin preguntar')
def delete_stack(stack_name, yes):
    """Elimina un stack de CloudFormation"""
    
    console.print(Panel.fit(
        f"[bold blue]Nubify[/bold blue]\n"
        f"Eliminando stack: {stack_name}",
        title="Eliminación de Stack"
    ))
    
    # Confirmar eliminación
    if not yes:
        if not click.confirm(f"¿Estás seguro de que quieres eliminar el stack '{stack_name}'?"):
            console.print("[yellow]Eliminación cancelada[/yellow]")
            return
    
    try:
        deployer = Deployer()
        success = deployer.delete_stack(stack_name)
        
        if success:
            console.print("[green]✓ Stack eliminado exitosamente[/green]")
        else:
            console.print("[red]✗ Error al eliminar el stack[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def chat():
    """Inicia el chatbot interactivo de nubify"""
    console.print(Panel.fit(
        "[bold blue]Nubify[/bold blue]\n"
        "Iniciando chatbot interactivo...",
        title="Chat"
    ))
    
    try:
        chatbot = NubifyChatbot()
        chatbot.start_chat()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

@cli.command()
def help():
    """Muestra ayuda detallada sobre los comandos disponibles"""
    
    help_text = """
[bold blue]Nubify - Comandos Disponibles[/bold blue]

[bold]Comandos Básicos:[/bold]
  test                    Prueba la conexión con AWS
  list-resources          Lista todos los recursos AWS disponibles
  list-templates          Lista las plantillas disponibles
  list-stacks             Lista los stacks de CloudFormation
  chat                    Inicia el chatbot interactivo

[bold]Plantillas:[/bold]
  template-details TEMPLATE    Muestra detalles de una plantilla
  estimate-costs TEMPLATE      Estima los costes de una plantilla
  estimate-costs TEMPLATE -v   Estima costes con información detallada

[bold]Despliegue:[/bold]
  deploy TEMPLATE STACK        Despliega una plantilla
  deploy TEMPLATE STACK -v     Despliega con estimación detallada de costes
  stack-resources STACK        Muestra recursos de un stack
  delete-stack STACK           Elimina un stack

[bold]Ejemplos de Uso:[/bold]
  nubify test
  nubify list-resources
  nubify list-templates
  nubify chat
  nubify template-details ec2-basic
  nubify estimate-costs ec2-basic
  nubify estimate-costs ec2-basic -v
  nubify deploy ec2-basic my-stack
  nubify deploy ec2-basic my-stack -p InstanceType=t3.micro
  nubify deploy ec2-basic my-stack -v
  nubify list-stacks
  nubify stack-resources my-stack
  nubify delete-stack my-stack

[bold]Opciones Disponibles:[/bold]
  -p, --parameters KEY=VALUE  Parámetros para plantillas
  -y, --yes                   Confirmar sin preguntar
  -v, --verbose               Modo detallado para estimación de costes

[bold]Configuración:[/bold]
  Configura las variables de entorno:
  AWS_ACCESS_KEY_ID=tu_access_key
  AWS_SECRET_ACCESS_KEY=tu_secret_key
  AWS_DEFAULT_REGION=us-east-1
  GEMINI_API_KEY=tu_gemini_api_key
    """
    
    console.print(Panel(help_text, title="Ayuda de Nubify"))

if __name__ == '__main__':
    cli() 