"""
Módulo para manejar la conexión y operaciones con AWS
"""

import boto3
from typing import List, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from rich.console import Console
from rich.table import Table

from .config import config

console = Console()

class AWSClient:
    """Clase para manejar operaciones con AWS"""
    
    def __init__(self):
        self.session = None
        self.clients = {}
        self._initialize_session()
    
    def _initialize_session(self):
        """Inicializa la sesión de AWS"""
        try:
            if not config.validate_aws_credentials():
                raise NoCredentialsError()
            
            self.session = boto3.Session(
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name=config.aws_default_region
            )
            
            # Inicializar clientes principales
            self.clients['ec2'] = self.session.client('ec2')
            self.clients['s3'] = self.session.client('s3')
            self.clients['lambda'] = self.session.client('lambda')
            self.clients['rds'] = self.session.client('rds')
            self.clients['cloudformation'] = self.session.client('cloudformation')
            
        except NoCredentialsError:
            console.print("[red]Error: Credenciales de AWS no configuradas[/red]")
            console.print("Por favor, configura las variables de entorno:")
            console.print("AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
            raise
        except Exception as e:
            console.print(f"[red]Error al inicializar sesión de AWS: {e}[/red]")
            raise
    
    def test_connection(self) -> bool:
        """Prueba la conexión con AWS"""
        try:
            # Intentar listar regiones para verificar credenciales
            sts_client = self.session.client('sts')
            sts_client.get_caller_identity()
            console.print("[green]✓ Conexión con AWS establecida correctamente[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Error al conectar con AWS: {e}[/red]")
            return False
    
    def list_ec2_instances(self) -> List[Dict[str, Any]]:
        """Lista las instancias EC2"""
        try:
            response = self.clients['ec2'].describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'],
                        'public_ip': instance.get('PublicIpAddress', 'N/A'),
                        'private_ip': instance.get('PrivateIpAddress', 'N/A')
                    })
            
            return instances
        except ClientError as e:
            console.print(f"[red]Error al listar instancias EC2: {e}[/red]")
            return []
    
    def list_s3_buckets(self) -> List[Dict[str, Any]]:
        """Lista los buckets S3"""
        try:
            response = self.clients['s3'].list_buckets()
            buckets = []
            
            for bucket in response['Buckets']:
                buckets.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate']
                })
            
            return buckets
        except ClientError as e:
            console.print(f"[red]Error al listar buckets S3: {e}[/red]")
            return []
    
    def list_lambda_functions(self) -> List[Dict[str, Any]]:
        """Lista las funciones Lambda"""
        try:
            response = self.clients['lambda'].list_functions()
            functions = []
            
            for function in response['Functions']:
                functions.append({
                    'name': function['FunctionName'],
                    'runtime': function['Runtime'],
                    'memory_size': function['MemorySize'],
                    'timeout': function['Timeout'],
                    'last_modified': function['LastModified']
                })
            
            return functions
        except ClientError as e:
            console.print(f"[red]Error al listar funciones Lambda: {e}[/red]")
            return []
    
    def list_rds_instances(self) -> List[Dict[str, Any]]:
        """Lista las instancias RDS"""
        try:
            response = self.clients['rds'].describe_db_instances()
            instances = []
            
            for instance in response['DBInstances']:
                instances.append({
                    'identifier': instance['DBInstanceIdentifier'],
                    'engine': instance['Engine'],
                    'status': instance['DBInstanceStatus'],
                    'instance_class': instance['DBInstanceClass'],
                    'allocated_storage': instance['AllocatedStorage']
                })
            
            return instances
        except ClientError as e:
            console.print(f"[red]Error al listar instancias RDS: {e}[/red]")
            return []
    
    def display_resources(self):
        """Muestra todos los recursos disponibles en una tabla formateada"""
        console.print("\n[bold blue]Recursos AWS Disponibles[/bold blue]\n")
        
        # EC2 Instances
        ec2_instances = self.list_ec2_instances()
        if ec2_instances:
            table = Table(title="Instancias EC2")
            table.add_column("ID", style="cyan")
            table.add_column("Tipo", style="magenta")
            table.add_column("Estado", style="green")
            table.add_column("IP Pública", style="yellow")
            table.add_column("IP Privada", style="yellow")
            
            for instance in ec2_instances:
                table.add_row(
                    instance['id'],
                    instance['type'],
                    instance['state'],
                    instance['public_ip'],
                    instance['private_ip']
                )
            console.print(table)
        else:
            console.print("[yellow]No hay instancias EC2[/yellow]")
        
        # S3 Buckets
        s3_buckets = self.list_s3_buckets()
        if s3_buckets:
            table = Table(title="Buckets S3")
            table.add_column("Nombre", style="cyan")
            table.add_column("Fecha Creación", style="magenta")
            
            for bucket in s3_buckets:
                table.add_row(
                    bucket['name'],
                    str(bucket['creation_date'])
                )
            console.print(table)
        else:
            console.print("[yellow]No hay buckets S3[/yellow]")
        
        # Lambda Functions
        lambda_functions = self.list_lambda_functions()
        if lambda_functions:
            table = Table(title="Funciones Lambda")
            table.add_column("Nombre", style="cyan")
            table.add_column("Runtime", style="magenta")
            table.add_column("Memoria (MB)", style="green")
            table.add_column("Timeout (s)", style="yellow")
            
            for function in lambda_functions:
                table.add_row(
                    function['name'],
                    function['runtime'],
                    str(function['memory_size']),
                    str(function['timeout'])
                )
            console.print(table)
        else:
            console.print("[yellow]No hay funciones Lambda[/yellow]")
        
        # RDS Instances
        rds_instances = self.list_rds_instances()
        if rds_instances:
            table = Table(title="Instancias RDS")
            table.add_column("Identificador", style="cyan")
            table.add_column("Motor", style="magenta")
            table.add_column("Estado", style="green")
            table.add_column("Clase", style="yellow")
            table.add_column("Almacenamiento (GB)", style="blue")
            
            for instance in rds_instances:
                table.add_row(
                    instance['identifier'],
                    instance['engine'],
                    instance['status'],
                    instance['instance_class'],
                    str(instance['allocated_storage'])
                )
            console.print(table)
        else:
            console.print("[yellow]No hay instancias RDS[/yellow]") 