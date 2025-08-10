"""
Módulo para manejar el despliegue de recursos usando CloudFormation
"""

import boto3
from typing import Dict, Optional
from botocore.exceptions import ClientError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import config
from .templates import TemplateManager

console = Console()

class Deployer:
    """Clase para manejar despliegues de CloudFormation"""
    
    def __init__(self):
        self.cloudformation = boto3.client(
            'cloudformation',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_default_region
        )
        self.template_manager = TemplateManager()
    
    def deploy_template(self, template_name: str, stack_name: str, parameters: Optional[Dict[str, str]] = None) -> bool:
        """Despliega una plantilla de CloudFormation"""
        
        # Obtener la plantilla
        template = self.template_manager.get_template(template_name)
        if not template:
            console.print(f"[red]Plantilla '{template_name}' no encontrada[/red]")
            return False
        
        # Leer el archivo de plantilla
        try:
            with open(template['file_path'], 'r') as f:
                template_body = f.read()
        except Exception as e:
            console.print(f"[red]Error al leer plantilla: {e}[/red]")
            return False
        
        # Preparar parámetros
        cf_parameters = []
        if parameters:
            for key, value in parameters.items():
                cf_parameters.append({
                    'ParameterKey': key,
                    'ParameterValue': value
                })
        
        # Crear stack
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Desplegando stack...", total=None)
                
                response = self.cloudformation.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=cf_parameters,
                    Capabilities=['CAPABILITY_IAM']  # Para recursos que requieren IAM
                )
                
                progress.update(task, description="Stack creado, esperando completar...")
                
                # Esperar a que el stack se complete con timeout
                try:
                    waiter = self.cloudformation.get_waiter('stack_create_complete')
                    waiter.wait(
                        StackName=stack_name,
                        WaiterConfig={'Delay': 5, 'MaxAttempts': 60}  # 5 minutos máximo
                    )
                    progress.update(task, description="¡Despliegue completado!")
                except Exception as waiter_error:
                    # Si el waiter falla, verificar el estado del stack
                    try:
                        stack_status = self.cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
                        if stack_status == 'CREATE_COMPLETE':
                            progress.update(task, description="¡Despliegue completado!")
                        elif stack_status == 'CREATE_IN_PROGRESS':
                            progress.update(task, description="Stack en progreso, verificando recursos...")
                            # Verificar si los recursos principales están completos
                            resources = self.cloudformation.list_stack_resources(StackName=stack_name)
                            main_resources_complete = all(
                                resource['ResourceStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']
                                for resource in resources['StackResourceSummaries']
                                if resource['ResourceType'] not in ['AWS::CloudFormation::WaitCondition']
                            )
                            if main_resources_complete:
                                progress.update(task, description="¡Recursos principales completados!")
                            else:
                                progress.update(task, description="Stack en progreso, algunos recursos pendientes...")
                        else:
                            raise waiter_error
                    except Exception:
                        raise waiter_error
            
            console.print(f"[green]✓ Stack '{stack_name}' desplegado correctamente[/green]")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'AlreadyExistsException':
                console.print(f"[yellow]El stack '{stack_name}' ya existe[/yellow]")
            else:
                console.print(f"[red]Error al desplegar stack: {error_message}[/red]")
            
            return False
        except Exception as e:
            console.print(f"[red]Error inesperado: {e}[/red]")
            return False
    
    def list_stacks(self) -> list:
        """Lista los stacks de CloudFormation"""
        try:
            # Mostrar TODOS los stacks sin filtrar por estado
            response = self.cloudformation.list_stacks()
            stacks = []
            
            for stack in response['StackSummaries']:
                stacks.append({
                    'name': stack['StackName'],
                    'status': stack['StackStatus'],
                    'creation_time': stack['CreationTime']
                })
            
            return stacks
        except ClientError as e:
            console.print(f"[red]Error al listar stacks: {e}[/red]")
            return []
    
    def delete_stack(self, stack_name: str) -> bool:
        """Elimina un stack de CloudFormation"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Eliminando stack...", total=None)
                
                self.cloudformation.delete_stack(StackName=stack_name)
                
                progress.update(task, description="Stack eliminado, esperando completar...")
                
                # Esperar a que el stack se elimine
                waiter = self.cloudformation.get_waiter('stack_delete_complete')
                waiter.wait(StackName=stack_name)
                
                progress.update(task, description="¡Eliminación completada!")
            
            console.print(f"[green]✓ Stack '{stack_name}' eliminado correctamente[/green]")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ValidationError':
                console.print(f"[yellow]El stack '{stack_name}' no existe[/yellow]")
            else:
                console.print(f"[red]Error al eliminar stack: {error_message}[/red]")
            
            return False
        except Exception as e:
            console.print(f"[red]Error inesperado: {e}[/red]")
            return False
    
    def get_stack_resources(self, stack_name: str) -> list:
        """Obtiene los recursos de un stack específico"""
        try:
            response = self.cloudformation.list_stack_resources(StackName=stack_name)
            resources = []
            
            for resource in response['StackResourceSummaries']:
                resources.append({
                    'logical_id': resource['LogicalResourceId'],
                    'physical_id': resource.get('PhysicalResourceId', 'N/A'),
                    'type': resource['ResourceType'],
                    'status': resource['ResourceStatus'],
                    'last_updated': resource['LastUpdatedTimestamp']
                })
            
            return resources
        except ClientError as e:
            console.print(f"[red]Error al obtener recursos del stack: {e}[/red]")
            return []
    
    def display_stacks(self):
        """Muestra los stacks disponibles en dos tablas separadas: activos y borrados"""
        from rich.table import Table
        
        stacks = self.list_stacks()
        
        if not stacks:
            console.print("[yellow]No hay stacks de CloudFormation[/yellow]")
            return
        
        # Separar stacks en activos y borrados
        active_stacks = []
        deleted_stacks = []
        
        for stack in stacks:
            if stack['status'] == 'DELETE_COMPLETE':
                deleted_stacks.append(stack)
            else:
                active_stacks.append(stack)
        
        # Tabla 1: Stacks Activos
        if active_stacks:
            console.print("\n[bold blue]Stacks Activos[/bold blue]")
            active_table = Table(title="Stacks Activos de CloudFormation")
            active_table.add_column("Nombre", style="cyan")
            active_table.add_column("Estado", style="magenta")
            active_table.add_column("Fecha Creación", style="green")
            
            for stack in active_stacks:
                # Colorear el estado según su tipo
                status = stack['status']
                if 'COMPLETE' in status and 'ROLLBACK' not in status:
                    status_style = "green"
                elif 'IN_PROGRESS' in status:
                    status_style = "yellow"
                elif 'FAILED' in status or 'ROLLBACK' in status:
                    status_style = "red"
                else:
                    status_style = "white"
                
                active_table.add_row(
                    stack['name'],
                    f"[{status_style}]{status}[/{status_style}]",
                    stack['creation_time'].strftime('%Y-%m-%d %H:%M:%S')
                )
            
            console.print(active_table)
        else:
            console.print("\n[yellow]No hay stacks activos[/yellow]")
        
        # Tabla 2: Stacks Borrados
        if deleted_stacks:
            console.print("\n[bold blue]Stacks Borrados[/bold blue]")
            deleted_table = Table(title="Stacks Borrados de CloudFormation")
            deleted_table.add_column("Nombre", style="cyan")
            deleted_table.add_column("Estado", style="red")
            deleted_table.add_column("Fecha Creación", style="green")
            
            for stack in deleted_stacks:
                deleted_table.add_row(
                    stack['name'],
                    "[red]DELETE_COMPLETE[/red]",
                    stack['creation_time'].strftime('%Y-%m-%d %H:%M:%S')
                )
            
            console.print(deleted_table)
        else:
            console.print("\n[yellow]No hay stacks borrados[/yellow]")
    
    def display_stack_resources(self, stack_name: str):
        """Muestra los recursos de un stack específico"""
        from rich.table import Table
        
        resources = self.get_stack_resources(stack_name)
        
        if not resources:
            console.print(f"[yellow]No se encontraron recursos para el stack '{stack_name}'[/yellow]")
            return
        
        table = Table(title=f"Recursos del Stack: {stack_name}")
        table.add_column("ID Lógico", style="cyan")
        table.add_column("ID Físico", style="magenta")
        table.add_column("Tipo", style="green")
        table.add_column("Estado", style="yellow")
        table.add_column("Última Actualización", style="blue")
        
        for resource in resources:
            table.add_row(
                resource['logical_id'],
                resource['physical_id'],
                resource['type'],
                resource['status'],
                str(resource['last_updated'])
            )
        
        console.print(table) 