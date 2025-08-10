"""
Módulo para manejar plantillas de CloudFormation
"""

import os
import re
import yaml
import boto3
import json
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
from botocore.exceptions import ClientError

console = Console()

class TemplateManager:
    """Gestor de plantillas de CloudFormation"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
        self.pricing_client = None
        self._init_pricing_client()
    
    def _init_pricing_client(self):
        """Inicializa el cliente de AWS Pricing API"""
        try:
            self.pricing_client = boto3.client('pricing', region_name='us-east-1')
        except Exception as e:
            console.print(f"[yellow]Advertencia: No se pudo inicializar Pricing API: {e}[/yellow]")
            console.print("[yellow]Usando estimaciones estáticas como fallback[/yellow]")
    
    def get_pricing_api_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la Pricing API"""
        status = {
            'available': False,
            'region': 'us-east-1',
            'error': None
        }
        
        if self.pricing_client:
            try:
                # Intentar una consulta simple para verificar conectividad
                response = self.pricing_client.get_services()
                status['available'] = True
                status['services_count'] = len(response.get('Services', []))
            except Exception as e:
                status['error'] = str(e)
        else:
            status['error'] = 'Cliente no inicializado'
        
        return status
    
    def display_pricing_api_status(self):
        """Muestra el estado de la Pricing API"""
        status = self.get_pricing_api_status()
        
        console.print(f"\n[bold blue]Estado de AWS Pricing API[/bold blue]")
        console.print(f"Región: {status['region']}")
        
        if status['available']:
            console.print(f"[green]✅ Disponible - {status.get('services_count', 'N/A')} servicios[/green]")
        else:
            console.print(f"[red]❌ No disponible[/red]")
            if status['error']:
                console.print(f"Error: {status['error']}")
        
        console.print()
    
    def _get_aws_pricing(self, service_code: str, filters: List[Dict], verbose: bool = False) -> Optional[float]:
        """Obtiene precios reales de AWS Pricing API"""
        if not self.pricing_client:
            return None
        
        try:
            if verbose:
                console.print(f"[blue]🔍 Consultando AWS Pricing API para {service_code}...[/blue]")
            
            # Para S3 y RDS, obtener más resultados para encontrar el correcto
            max_results = 10 if service_code in ['AmazonS3', 'AmazonRDS'] else 1
            
            response = self.pricing_client.get_products(
                ServiceCode=service_code,
                Filters=filters,
                MaxResults=max_results
            )
            
            if response['PriceList']:
                if verbose:
                    console.print(f"[green]✅ Respuesta recibida de Pricing API ({len(response['PriceList'])} productos)[/green]")
                
                # Para S3, buscar el producto correcto
                if service_code == 'AmazonS3':
                    if verbose:
                        console.print(f"[blue]🔍 Buscando precio de S3 Standard Storage...[/blue]")
                    
                    for i, price_item in enumerate(response['PriceList']):
                        price_data = json.loads(price_item)
                        
                        # Mostrar información del producto
                        if verbose and 'product' in price_data:
                            product = price_data['product']
                            if 'attributes' in product:
                                attrs = product['attributes']
                                console.print(f"[blue]Producto {i+1}:[/blue]")
                                for key, value in attrs.items():
                                    console.print(f"  {key}: {value}")
                                
                                # Buscar S3 Standard Storage
                                if 'storageClass' in attrs and 'Standard' in attrs['storageClass']:
                                    console.print(f"[green]✅ Encontrado S3 Standard Storage![/green]")
                                    price = self._extract_price_from_response(price_data, service_code, verbose)
                                    if price is not None:
                                        return price
                    
                    # Si no se encontró S3 Standard Storage, continuar con el primer resultado
                    if verbose:
                        console.print(f"[yellow]⚠️ No se encontró S3 Standard Storage, usando primer resultado disponible[/yellow]")
                
                # Para RDS, buscar el producto correcto
                elif service_code == 'AmazonRDS':
                    if verbose:
                        console.print(f"[blue]🔍 Buscando precio de RDS MySQL...[/blue]")
                    
                    for i, price_item in enumerate(response['PriceList']):
                        price_data = json.loads(price_item)
                        
                        # Mostrar información del producto
                        if verbose and 'product' in price_data:
                            product = price_data['product']
                            if 'attributes' in product:
                                attrs = product['attributes']
                                console.print(f"[blue]Producto RDS {i+1}:[/blue]")
                                for key, value in attrs.items():
                                    console.print(f"  {key}: {value}")
                                
                                # Buscar RDS MySQL
                                if 'databaseEngine' in attrs and 'MySQL' in attrs['databaseEngine']:
                                    console.print(f"[green]✅ Encontrado RDS MySQL![/green]")
                                    price = self._extract_price_from_response(price_data, service_code, verbose)
                                    if price is not None:
                                        return price
                    
                    # Si no se encontró RDS MySQL, continuar con el primer resultado
                    if verbose:
                        console.print(f"[yellow]⚠️ No se encontró RDS MySQL, usando primer resultado disponible[/yellow]")
                
                # Para otros servicios, usar el primer resultado
                price_data = json.loads(response['PriceList'][0])
                
                # Debug: mostrar campos disponibles para S3
                if verbose and service_code == 'AmazonS3':
                    console.print(f"[blue]🔍 Campos disponibles en respuesta S3:[/blue]")
                    if 'product' in price_data:
                        product = price_data['product']
                        if 'attributes' in product:
                            attrs = product['attributes']
                            for key, value in attrs.items():
                                console.print(f"  {key}: {value}")
                
                # Debug: mostrar campos disponibles para EC2
                elif verbose and service_code == 'AmazonEC2':
                    console.print(f"[blue]🔍 Campos disponibles en respuesta EC2:[/blue]")
                    if 'product' in price_data:
                        product = price_data['product']
                        if 'attributes' in product:
                            attrs = product['attributes']
                            for key, value in attrs.items():
                                console.print(f"  {key}: {value}")
                
                # Debug: mostrar campos disponibles para Lambda
                elif verbose and service_code == 'AWSLambda':
                    console.print(f"[blue]🔍 Campos disponibles en respuesta Lambda:[/blue]")
                    if 'product' in price_data:
                        product = price_data['product']
                        if 'attributes' in product:
                            attrs = product['attributes']
                            for key, value in attrs.items():
                                console.print(f"  {key}: {value}")
                
                # Extraer precio
                price = self._extract_price_from_response(price_data, service_code, verbose)
                if price is not None:
                    if verbose:
                        if service_code == 'AmazonS3':
                            console.print(f"[green]✅ Precio extraído: ${price:.6f}/GB-mes[/green]")
                        else:
                            console.print(f"[green]✅ Precio extraído: ${price:.6f}/hora[/green]")
                    return price
                else:
                    if verbose:
                        console.print(f"[yellow]⚠️ No se pudo extraer precio de la respuesta[/yellow]")
            else:
                if verbose:
                    console.print(f"[yellow]⚠️ No se encontraron productos para {service_code}[/yellow]")
            
        except ClientError as e:
            if verbose:
                console.print(f"[yellow]Error al obtener precios de AWS: {e}[/yellow]")
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Error inesperado en Pricing API: {e}[/yellow]")
        
        return None
    
    def _extract_price_from_response(self, price_data: Dict, service_code: str = None, verbose: bool = False) -> Optional[float]:
        """Extrae el precio de la respuesta de Pricing API"""
        try:
            # Debug: mostrar estructura de la respuesta
            if verbose:
                console.print(f"[blue]🔍 Estructura de respuesta para {service_code}:[/blue]")
                console.print(f"  Claves principales: {list(price_data.keys())}")
            
            if 'terms' in price_data:
                if verbose:
                    console.print(f"  Términos disponibles: {list(price_data['terms'].keys())}")
                
                # Buscar precio en términos OnDemand
                ondemand = price_data['terms'].get('OnDemand', {})
                if ondemand:
                    if verbose:
                        console.print(f"  Términos OnDemand: {list(ondemand.keys())}")
                    
                    for term_id, term_data in ondemand.items():
                        if verbose:
                            console.print(f"  Analizando término: {term_id}")
                        
                        if 'priceDimensions' in term_data:
                            price_dimensions = term_data.get('priceDimensions', {})
                            if verbose:
                                console.print(f"    Dimensiones de precio: {list(price_dimensions.keys())}")
                            
                            for dim_id, dim_data in price_dimensions.items():
                                if verbose:
                                    console.print(f"    Analizando dimensión: {dim_id}")
                                    console.print(f"      Campos: {list(dim_data.keys())}")
                                
                                if 'pricePerUnit' in dim_data:
                                    price_per_unit = dim_data.get('pricePerUnit', {})
                                    if verbose:
                                        console.print(f"      Precio por unidad: {price_per_unit}")
                                    
                                    if 'USD' in price_per_unit:
                                        price = float(price_per_unit['USD'])
                                        if verbose:
                                            console.print(f"[green]✅ Precio extraído: ${price}[/green]")
                                        return price
                                    elif 'CNY' in price_per_unit:
                                        # Convertir CNY a USD (aproximadamente 1 CNY = 0.14 USD)
                                        cny_price = float(price_per_unit['CNY'])
                                        usd_price = cny_price * 0.14
                                        if verbose:
                                            console.print(f"[green]✅ Precio extraído: {cny_price} CNY = ${usd_price:.6f} USD[/green]")
                                        return usd_price
                
                # Si no hay OnDemand, buscar en otros tipos de términos
                for term_type, terms in price_data['terms'].items():
                    if term_type != 'OnDemand':
                        if verbose:
                            console.print(f"  Revisando términos {term_type}: {list(terms.keys())}")
                        
                        for term_id, term_data in terms.items():
                            if 'priceDimensions' in term_data:
                                price_dimensions = term_data.get('priceDimensions', {})
                                for dim_id, dim_data in price_dimensions.items():
                                    if 'pricePerUnit' in dim_data:
                                        price_per_unit = dim_data.get('pricePerUnit', {})
                                        if 'USD' in price_per_unit:
                                            price = float(price_per_unit['USD'])
                                            if verbose:
                                                console.print(f"[green]✅ Precio extraído de {term_type}: ${price}[/green]")
                                            return price
                                        elif 'CNY' in price_per_unit:
                                            # Convertir CNY a USD (aproximadamente 1 CNY = 0.14 USD)
                                            cny_price = float(price_per_unit['CNY'])
                                            usd_price = cny_price * 0.14
                                            if verbose:
                                                console.print(f"[green]✅ Precio extraído de {term_type}: {cny_price} CNY = ${usd_price:.6f} USD[/green]")
                                            return usd_price
            
            # Si no se encontró en términos, buscar en otros lugares
            if verbose:
                console.print(f"[yellow]⚠️ No se encontró precio en términos, buscando en otros campos...[/yellow]")
            
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Error extrayendo precio: {e}[/yellow]")
                console.print(f"[yellow]Traceback completo:[/yellow]")
                import traceback
                console.print(traceback.format_exc())
        
        return None
    
    def _extract_template_info(self, content: str) -> Dict[str, Any]:
        """Extrae información básica de una plantilla CloudFormation usando regex"""
        info = {
            'description': 'Sin descripción',
            'parameters': {},
            'resources': {}
        }
        
        # Extraer descripción
        desc_match = re.search(r'Description:\s*[\'"]([^\'"]*)[\'"]', content)
        if desc_match:
            info['description'] = desc_match.group(1)
        
        # Extraer parámetros
        params_section = re.search(r'Parameters:(.*?)(?=\n\s*Resources:|$)', content, re.DOTALL)
        if params_section:
            params_content = params_section.group(1)
            # Buscar parámetros individuales
            param_blocks = re.findall(r'(\w+):\s*\n\s+Type:\s*([^\n]+)', params_content)
            for param_name, param_type in param_blocks:
                info['parameters'][param_name] = {
                    'Type': param_type.strip(),
                    'Description': 'Sin descripción'
                }
        
        # Extraer recursos
        resources_section = re.search(r'Resources:(.*?)(?=\n\s*Outputs:|$)', content, re.DOTALL)
        if resources_section:
            resources_content = resources_section.group(1)
            # Buscar recursos individuales
            resource_blocks = re.findall(r'(\w+):\s*\n\s+Type:\s*([^\n]+)', resources_content)
            for resource_name, resource_type in resource_blocks:
                info['resources'][resource_name] = {'Type': resource_type.strip()}
        
        return info
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carga las plantillas disponibles"""
        templates = {}
        
        if not self.templates_dir.exists():
            console.print(f"[yellow]Directorio de plantillas no encontrado: {self.templates_dir}[/yellow]")
            return templates
        
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                # Intentar cargar con PyYAML primero
                with open(template_file, 'r') as f:
                    template_data = yaml.safe_load(f)
                
                template_name = template_file.stem
                templates[template_name] = {
                    'name': template_name,
                    'description': template_data.get('Description', 'Sin descripción'),
                    'parameters': template_data.get('Parameters', {}),
                    'resources': template_data.get('Resources', {}),
                    'file_path': str(template_file),
                    'parsed': True
                }
                
            except Exception as e:
                # Si falla PyYAML, usar regex para extraer información básica
                try:
                    with open(template_file, 'r') as f:
                        content = f.read()
                    
                    template_name = template_file.stem
                    info = self._extract_template_info(content)
                    
                    templates[template_name] = {
                        'name': template_name,
                        'description': info['description'],
                        'parameters': info['parameters'],
                        'resources': info['resources'],
                        'file_path': str(template_file),
                        'parsed': True,  # Cambiado a True porque el regex funciona correctamente
                        'raw_content': content
                    }
                    
                except Exception as e2:
                    console.print(f"[red]Error crítico al cargar {template_file}: {e2}[/red]")
        
        return templates
    
    def list_templates(self) -> List[str]:
        """Lista las plantillas disponibles"""
        return list(self.templates.keys())
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Obtiene una plantilla específica"""
        return self.templates.get(template_name, {})
    
    def display_templates(self):
        """Muestra las plantillas disponibles en una tabla formateada"""
        if not self.templates:
            console.print("[yellow]No hay plantillas disponibles[/yellow]")
            return
        
        table = Table(title="Plantillas Disponibles")
        table.add_column("Nombre", style="cyan")
        table.add_column("Descripción", style="magenta")
        table.add_column("Recursos", style="green")
        table.add_column("Parámetros", style="yellow")
        table.add_column("Estado", style="blue")
        
        for template_name, template_data in self.templates.items():
            resources_count = len(template_data.get('resources', {}))
            parameters_count = len(template_data.get('parameters', {}))
            status = "✅ OK" if template_data.get('parsed', False) else "⚠️ Regex Parse"
            description = template_data.get('description', 'Sin descripción')
            
            table.add_row(
                template_name,
                description,
                str(resources_count),
                str(parameters_count),
                status
            )
        
        console.print(table)
    
    def display_template_details(self, template_name: str):
        """Muestra detalles de una plantilla específica"""
        template = self.get_template(template_name)
        
        if not template:
            console.print(f"[red]Plantilla '{template_name}' no encontrada[/red]")
            return
        
        console.print(f"\n[bold blue]Detalles de la plantilla: {template_name}[/bold blue]\n")
        
        # Descripción
        console.print(f"[bold]Descripción:[/bold] {template.get('description', 'Sin descripción')}")
        
        # Estado
        if 'raw_content' in template:
            console.print("[green]✅ Plantilla parseada correctamente con regex[/green]")
        
        # Recursos
        resources = template.get('resources', {})
        if resources:
            table = Table(title="Recursos")
            table.add_column("Tipo", style="cyan")
            table.add_column("Nombre", style="magenta")
            
            for resource_name, resource_data in resources.items():
                resource_type = resource_data.get('Type', 'Desconocido')
                table.add_row(resource_type, resource_name)
            
            console.print(table)
        
        # Parámetros
        parameters = template.get('parameters', {})
        if parameters:
            table = Table(title="Parámetros")
            table.add_column("Nombre", style="cyan")
            table.add_column("Tipo", style="magenta")
            table.add_column("Descripción", style="green")
            table.add_column("Requerido", style="yellow")
            
            for param_name, param_data in parameters.items():
                param_type = param_data.get('Type', 'String')
                description = param_data.get('Description', 'Sin descripción')
                required = 'Sí' if param_data.get('Required', False) else 'No'
                
                table.add_row(param_name, param_type, description, required)
            
            console.print(table)
    
    def estimate_costs(self, template_name: str, parameters: Optional[Dict[str, str]] = None, verbose: bool = False) -> Dict[str, Any]:
        """Estima los costes de una plantilla con estimaciones más realistas"""
        template = self.get_template(template_name)
        
        if not template:
            return {'error': f'Plantilla {template_name} no encontrada'}
        
        # Estimación mejorada de costes
        cost_estimate = {
            'template_name': template_name,
            'estimated_monthly_cost': 0.0,
            'services': [],
            'assumptions': [],
            'pricing_api_used': False  # Rastrear si se usó realmente Pricing API
        }
        
        resources = template.get('resources', {})
        
        for resource_name, resource_data in resources.items():
            resource_type = resource_data.get('Type', '')
            
            # Estimaciones mejoradas por tipo de recurso
            if 'AWS::EC2::Instance' in resource_type:
                instance_type = parameters.get('InstanceType', 't3.micro') if parameters else 't3.micro'
                cost, used_pricing_api = self._estimate_ec2_cost(instance_type, verbose)
                cost_estimate['pricing_api_used'] = cost_estimate['pricing_api_used'] or used_pricing_api
                cost_estimate['services'].append({
                    'service': 'EC2',
                    'description': f'Instancia EC2 ({instance_type}): {resource_name}',
                    'estimated_cost': cost,
                    'details': f'Instance Type: {instance_type}'
                })
                cost_estimate['estimated_monthly_cost'] += cost
                cost_estimate['assumptions'].append(f'EC2: Estimación basada en {instance_type} (us-east-1)')
            
            elif 'AWS::S3::Bucket' in resource_type:
                bucket_name = parameters.get('BucketName', 'default-bucket') if parameters else 'default-bucket'
                versioning = parameters.get('Versioning', 'Enabled') if parameters else 'Enabled'
                cost, used_pricing_api = self._estimate_s3_cost(versioning, verbose)
                cost_estimate['pricing_api_used'] = cost_estimate['pricing_api_used'] or used_pricing_api
                cost_estimate['services'].append({
                    'service': 'S3',
                    'description': f'Bucket S3: {bucket_name}',
                    'estimated_cost': cost,
                    'details': f'Versioning: {versioning}'
                })
                cost_estimate['estimated_monthly_cost'] += cost
                cost_estimate['assumptions'].append('S3: Estimación incluye storage básico y requests')
            
            elif 'AWS::Lambda::Function' in resource_type:
                function_name = parameters.get('FunctionName', 'default-function') if parameters else 'default-function'
                memory_size = parameters.get('MemorySize', '128') if parameters else '128'
                cost, used_pricing_api = self._estimate_lambda_cost(int(memory_size), verbose)
                cost_estimate['pricing_api_used'] = cost_estimate['pricing_api_used'] or used_pricing_api
                cost_estimate['services'].append({
                    'service': 'Lambda',
                    'description': f'Función Lambda: {function_name}',
                    'estimated_cost': cost,
                    'details': f'Memory: {memory_size}MB'
                })
                cost_estimate['estimated_monthly_cost'] += cost
                cost_estimate['assumptions'].append(f'Lambda: Estimación basada en {memory_size}MB y uso moderado')
            
            elif 'AWS::RDS::DBInstance' in resource_type:
                instance_type = parameters.get('DBInstanceClass', 'db.t3.micro') if parameters else 'db.t3.micro'
                cost, used_pricing_api = self._estimate_rds_cost(instance_type, verbose)
                cost_estimate['pricing_api_used'] = cost_estimate['pricing_api_used'] or used_pricing_api
                cost_estimate['services'].append({
                    'service': 'RDS',
                    'description': f'Instancia RDS: {resource_name}',
                    'estimated_cost': cost,
                    'details': f'Instance Class: {instance_type}'
                })
                cost_estimate['estimated_monthly_cost'] += cost
                cost_estimate['assumptions'].append(f'RDS: Estimación basada en {instance_type} (us-east-1)')
        
        return cost_estimate
    
    def quick_cost_estimate(self, template_name: str, parameters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Estimación rápida de costes sin información detallada (equivalente a verbose=False)"""
        return self.estimate_costs(template_name, parameters, verbose=False)
    
    def detailed_cost_estimate(self, template_name: str, parameters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Estimación detallada de costes con toda la información de debug (equivalente a verbose=True)"""
        return self.estimate_costs(template_name, parameters, verbose=True)
    
    def _estimate_ec2_cost(self, instance_type: str, verbose: bool = False) -> tuple[float, bool]:
        """Estima el coste de EC2 usando Pricing API o estimaciones estáticas"""
        
        # Intentar obtener precio real de AWS Pricing API
        if self.pricing_client:
            # Filtros específicos para EC2
            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
            ]
            
            real_price = self._get_aws_pricing('AmazonEC2', filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio EC2 ({instance_type}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Si no funciona con filtros específicos, probar con filtros más simples
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros más simples para EC2...[/yellow]")
            simple_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            ]
            
            real_price = self._get_aws_pricing('AmazonEC2', simple_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio EC2 ({instance_type}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Si aún no funciona, probar con filtros básicos
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros básicos para EC2...[/yellow]")
            basic_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            ]
            
            real_price = self._get_aws_pricing('AmazonEC2', basic_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio EC2 ({instance_type}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
        
        # Fallback a estimaciones estáticas
        pricing = {
            't3.micro': 0.0104,    # $0.0104/hora
            't3.small': 0.0208,    # $0.0208/hora
            't3.medium': 0.0416,   # $0.0416/hora
            't3.large': 0.0832,    # $0.0832/hora
            'm5.large': 0.096,     # $0.096/hora
            'c5.large': 0.085,     # $0.085/hora
        }
        
        hourly_cost = pricing.get(instance_type, 0.0104)  # Default a t3.micro
        monthly_cost = hourly_cost * 24 * 30  # 24 horas * 30 días
        
        if verbose:
            console.print(f"[yellow]⚠️ No se pudo obtener precio de Pricing API, usando estimación estática para EC2 ({instance_type})[/yellow]")
            console.print(f"[green]✅ Precio estimado: ${monthly_cost:.2f}/mes[/green]")
        return round(monthly_cost, 2), False
    
    def _estimate_s3_cost(self, versioning: str, verbose: bool = False) -> tuple[float, bool]:
        """Estima el coste de S3 usando Pricing API o estimaciones estáticas"""
        
        # Intentar obtener precio real de AWS Pricing API
        if self.pricing_client:
            # Filtros específicos para S3 Standard Storage
            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'volumeType', 'Value': 'Amazon S3'},
                {'Type': 'TERM_MATCH', 'Field': 'storageClass', 'Value': 'General Purpose'},
            ]
            
            real_price = self._get_aws_pricing('AmazonS3', filters, verbose)
            if real_price is not None:
                # S3 pricing es por GB-mes, no por hora
                storage_cost_per_gb_month = real_price  # Ya es por GB-mes
                estimated_storage_gb = 1.0
                
                # Requests (estimación)
                get_requests = 1000
                put_requests = 100
                get_cost = (get_requests / 1000) * 0.0004
                put_cost = (put_requests / 1000) * 0.0005
                
                base_cost = (estimated_storage_gb * storage_cost_per_gb_month) + get_cost + put_cost
                
                # Versioning puede aumentar costes
                if versioning == 'Enabled':
                    base_cost *= 1.1  # 10% adicional por versioning
                
                if verbose:
                    console.print(f"[blue]💰 Precio S3 (Standard Storage): ${real_price:.6f}/GB-mes[/blue]")
                return round(base_cost, 2), True
            
            # Si no funciona con filtros específicos, probar con filtros más simples
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros más simples para S3...[/yellow]")
            simple_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'usagetype', 'Value': 'TimedStorage-ByteHrs'},
            ]
            
            real_price = self._get_aws_pricing('AmazonS3', simple_filters, verbose)
            if real_price is not None:
                # S3 pricing es por GB-mes, no por hora
                storage_cost_per_gb_month = real_price  # Ya es por GB-mes
                estimated_storage_gb = 1.0
                
                # Requests (estimación)
                get_requests = 1000
                put_requests = 100
                get_cost = (get_requests / 1000) * 0.0004
                put_cost = (put_requests / 1000) * 0.0005
                
                base_cost = (estimated_storage_gb * storage_cost_per_gb_month) + get_cost + put_cost
                
                # Versioning puede aumentar costes
                if versioning == 'Enabled':
                    base_cost *= 1.1  # 10% adicional por versioning
                
                if verbose:
                    console.print(f"[blue]💰 Precio S3 (Standard Storage): ${real_price:.6f}/GB-mes[/blue]")
                return round(base_cost, 2), True
            
            # Si aún no funciona, probar con filtros aún más básicos
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros básicos para S3...[/yellow]")
            basic_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AmazonS3', basic_filters, verbose)
            if real_price is not None:
                # S3 pricing es por GB-mes, no por hora
                storage_cost_per_gb_month = real_price  # Ya es por GB-mes
                estimated_storage_gb = 1.0
                
                # Requests (estimación)
                get_requests = 1000
                put_requests = 100
                get_cost = (get_requests / 1000) * 0.0004
                put_cost = (put_requests / 1000) * 0.0005
                
                base_cost = (estimated_storage_gb * storage_cost_per_gb_month) + get_cost + put_cost
                
                # Versioning puede aumentar costes
                if versioning == 'Enabled':
                    base_cost *= 1.1  # 10% adicional por versioning
                
                if verbose:
                    console.print(f"[blue]💰 Precio S3 (Standard Storage): ${real_price:.6f}/GB-mes[/blue]")
                return round(base_cost, 2), True
        
        # Fallback a estimaciones estáticas
        storage_cost_per_gb = 0.023  # $0.023 por GB por mes
        estimated_storage_gb = 1.0    # Estimación de 1GB
        
        # Requests
        get_requests = 1000  # Estimación de requests
        put_requests = 100
        get_cost = (get_requests / 1000) * 0.0004  # $0.0004 por 1000 requests
        put_cost = (put_requests / 1000) * 0.0005  # $0.0005 por 1000 requests
        
        base_cost = (estimated_storage_gb * storage_cost_per_gb) + get_cost + put_cost
        
        # Versioning puede aumentar costes
        if versioning == 'Enabled':
            base_cost *= 1.1  # 10% adicional por versioning
        
        if verbose:
            console.print(f"[yellow]⚠️ No se pudo obtener precio de Pricing API, usando estimación estática para S3[/yellow]")
            console.print(f"[green]✅ Precio estimado: ${base_cost:.2f}/mes[/green]")
        return round(base_cost, 2), False
    
    def _estimate_lambda_cost(self, memory_mb: int, verbose: bool = False) -> tuple[float, bool]:
        """Estima el coste de Lambda usando Pricing API o estimaciones estáticas"""
        
        # Intentar obtener precio real de AWS Pricing API
        if self.pricing_client:
            # Filtros específicos para Lambda
            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'usagetype', 'Value': 'Lambda-GB-Second'},
            ]
            
            real_price = self._get_aws_pricing('AWSLambda', filters, verbose)
            if real_price is not None:
                # Lambda pricing es por GB-segundo
                requests_per_month = 1000000  # 1M requests
                duration_ms = 100  # 100ms promedio
                
                # Cálculo de GB-segundos
                gb_seconds = (memory_mb / 1024) * (duration_ms / 1000) * requests_per_month
                
                # Costes usando precio real
                request_cost = (requests_per_month / 1000000) * 0.20  # $0.20 por 1M requests
                compute_cost = (gb_seconds / 1000000) * real_price  # Precio real por GB-segundo
                
                total_cost = request_cost + compute_cost
                if verbose:
                    console.print(f"[blue]💰 Precio Lambda ({memory_mb}MB): ${real_price:.6f}/GB-segundo[/blue]")
                return round(total_cost, 2), True
            
            # Si no funciona con filtros específicos, probar con filtros más simples
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros más simples para Lambda...[/yellow]")
            simple_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AWSLambda', simple_filters, verbose)
            if real_price is not None:
                # Lambda pricing es por GB-segundo
                requests_per_month = 1000000  # 1M requests
                duration_ms = 100  # 100ms promedio
                
                # Cálculo de GB-segundos
                gb_seconds = (memory_mb / 1024) * (duration_ms / 1000) * requests_per_month
                
                # Costes usando precio real
                request_cost = (requests_per_month / 1000000) * 0.20  # $0.20 por 1M requests
                compute_cost = (gb_seconds / 1000000) * real_price  # Precio real por GB-segundo
                
                total_cost = request_cost + compute_cost
                if verbose:
                    console.print(f"[blue]💰 Precio Lambda ({memory_mb}MB): ${real_price:.6f}/GB-segundo[/blue]")
                return round(total_cost, 2), True
        
        # Fallback a estimaciones estáticas
        requests_per_month = 1000000  # 1M requests
        duration_ms = 100  # 100ms promedio
        
        # Cálculo de GB-segundos
        gb_seconds = (memory_mb / 1024) * (duration_ms / 1000) * requests_per_month
        
        # Costes
        request_cost = (requests_per_month / 1000000) * 0.20  # $0.20 por 1M requests
        compute_cost = (gb_seconds / 1000000) * 0.0000166667  # $0.0000166667 por GB-segundo
        
        total_cost = request_cost + compute_cost
        if verbose:
            console.print(f"[yellow]⚠️ No se pudo obtener precio de Pricing API, usando estimación estática para Lambda[/yellow]")
            console.print(f"[green]✅ Precio estimado: ${total_cost:.2f}/mes[/green]")
        return round(total_cost, 2), False
    
    def _estimate_rds_cost(self, instance_class: str, verbose: bool = False) -> tuple[float, bool]:
        """Estima el coste de RDS usando Pricing API o estimaciones estáticas"""
        
        # Intentar obtener precio real de AWS Pricing API
        if self.pricing_client:
            # Filtros específicos para RDS
            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': 'MySQL'},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEdition', 'Value': 'Standard'},
                {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AmazonRDS', filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio RDS ({instance_class}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Si no funciona con filtros específicos, probar con filtros más simples
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros más simples para RDS...[/yellow]")
            simple_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': 'MySQL'},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AmazonRDS', simple_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio RDS ({instance_class}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Si aún no funciona, probar con filtros básicos
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros básicos para RDS...[/yellow]")
            basic_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AmazonRDS', basic_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio RDS ({instance_class}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Si aún no funciona, probar con filtros de uso específico
            if verbose:
                console.print(f"[yellow]⚠️ Intentando con filtros de uso específico para RDS...[/yellow]")
            usage_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'usagetype', 'Value': 'RDS:GP2:Piops'},
            ]
            
            real_price = self._get_aws_pricing('AmazonRDS', usage_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio RDS ({instance_class}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
            
            # Último intento: buscar solo por tipo de instancia y región
            if verbose:
                console.print(f"[yellow]⚠️ Último intento: filtros mínimos para RDS...[/yellow]")
            minimal_filters = [
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            ]
            
            real_price = self._get_aws_pricing('AmazonRDS', minimal_filters, verbose)
            if real_price is not None:
                monthly_cost = real_price * 24 * 30  # 24 horas * 30 días
                if verbose:
                    console.print(f"[blue]💰 Precio RDS ({instance_class}): ${real_price:.6f}/hora[/blue]")
                return round(monthly_cost, 2), True
        
        # Fallback a estimaciones estáticas
        pricing = {
            'db.t3.micro': 0.017,     # $0.017/hora
            'db.t3.small': 0.034,     # $0.034/hora
            'db.t3.medium': 0.068,    # $0.068/hora
            'db.t3.large': 0.136,     # $0.136/hora
            'db.t2.micro': 0.017,     # $0.017/hora
            'db.t2.small': 0.034,     # $0.034/hora
            'db.r5.large': 0.291,     # $0.291/hora
        }
        
        hourly_cost = pricing.get(instance_class, 0.017)  # Default a db.t3.micro
        monthly_cost = hourly_cost * 24 * 30  # 24 horas * 30 días
        
        if verbose:
            console.print(f"[yellow]⚠️ No se pudo obtener precio de Pricing API, usando estimación estática para RDS[/yellow]")
            console.print(f"[green]✅ Precio estimado: ${monthly_cost:.2f}/mes[/green]")
        return round(monthly_cost, 2), False
    
    def display_cost_estimate(self, template_name: str, parameters: Optional[Dict[str, str]] = None, verbose: bool = False):
        """Muestra la estimación de costes de una plantilla"""
        cost_estimate = self.estimate_costs(template_name, parameters, verbose)
        
        if 'error' in cost_estimate:
            console.print(f"[red]{cost_estimate['error']}[/red]")
            return
        
        console.print(f"\n[bold blue]Estimación de Costes: {template_name}[/bold blue]\n")
        
        # Indicar modo de ejecución
        if verbose:
            console.print("[blue]🔍 Modo verbose activado - Mostrando información detallada[/blue]\n")
        
        # Indicar si se usó Pricing API y si devolvió datos
        if self.pricing_client:
            # Verificar si realmente se obtuvieron datos de Pricing API
            pricing_api_used = cost_estimate.get('pricing_api_used', False)
            if pricing_api_used:
                console.print("[green]✅ Usando AWS Pricing API para estimaciones reales[/green]")
            else:
                console.print("[yellow]⚠️ AWS Pricing API no devolvió datos, usando estimaciones estáticas[/yellow]")
        else:
            console.print("[yellow]⚠️ Usando estimaciones estáticas (Pricing API no disponible)[/yellow]")
        
        # Servicios
        if cost_estimate['services']:
            table = Table(title="Servicios")
            table.add_column("Servicio", style="cyan")
            table.add_column("Descripción", style="magenta")
            table.add_column("Detalles", style="yellow")
            table.add_column("Coste Estimado ($/mes)", style="green")
            
            for service in cost_estimate['services']:
                table.add_row(
                    service['service'],
                    service['description'],
                    service.get('details', ''),
                    f"${service['estimated_cost']:.2f}"
                )
            
            console.print(table)
            
            # En modo no-verbose, mostrar resumen rápido
            if not verbose:
                console.print(f"\n[blue]💡 Para ver información detallada, usa el modo verbose[/blue]")
        
        # Coste total con unidad correcta
        total_cost = cost_estimate['estimated_monthly_cost']
        
        # Determinar si es principalmente S3 (para mostrar unidad correcta)
        is_s3_template = any('S3' in service['service'] for service in cost_estimate.get('services', []))
        
        if is_s3_template and len(cost_estimate.get('services', [])) == 1:
            # Si es solo S3, mostrar por GB-mes
            console.print(f"\n[bold]Coste Total Estimado: ${total_cost:.2f}/GB-mes[/bold]")
            console.print(f"[blue]Nota: Para 1GB de almacenamiento estimado[/blue]")
        else:
            # Para otros servicios, mostrar por mes
            console.print(f"\n[bold]Coste Total Estimado: ${total_cost:.2f}/mes[/bold]")
        
        # Asunciones (solo en modo verbose)
        if verbose and cost_estimate.get('assumptions'):
            console.print(f"\n[bold]Asunciones:[/bold]")
            for assumption in cost_estimate['assumptions']:
                console.print(f"• {assumption}")
        
        # Nota final (siempre visible)
        console.print(f"\n[yellow]Nota: Esta es una estimación basada en precios de us-east-1. Los costes reales pueden variar según región, uso y configuración.[/yellow]")
    
    def display_quick_cost_estimate(self, template_name: str, parameters: Optional[Dict[str, str]] = None):
        """Muestra una estimación rápida de costes sin información detallada"""
        self.display_cost_estimate(template_name, parameters, verbose=False)
    
    def display_detailed_cost_estimate(self, template_name: str, parameters: Optional[Dict[str, str]] = None):
        """Muestra una estimación detallada de costes con toda la información de debug"""
        self.display_cost_estimate(template_name, parameters, verbose=True)
    
    def show_usage_help(self):
        """Muestra ayuda sobre cómo usar los diferentes modos de estimación"""
        console.print(f"\n[bold blue]Guía de Uso - Estimación de Costes[/bold blue]\n")
        
        console.print("[bold]Modos de Estimación:[/bold]")
        console.print("• [cyan]Rápida (por defecto):[/cyan] Solo información esencial")
        console.print("• [cyan]Detallada (verbose):[/cyan] Información completa con debug\n")
        
        console.print("[bold]Métodos Disponibles:[/bold]")
        console.print("• [green]estimate_costs(template, params, verbose=False)[/green] - Estimación básica")
        console.print("• [green]quick_cost_estimate(template, params)[/green] - Estimación rápida")
        console.print("• [green]detailed_cost_estimate(template, params)[/green] - Estimación detallada")
        console.print("• [green]display_cost_estimate(template, params, verbose=False)[/green] - Mostrar estimación")
        console.print("• [green]display_quick_cost_estimate(template, params)[/green] - Mostrar rápida")
        console.print("• [green]display_detailed_cost_estimate(template, params)[/green] - Mostrar detallada\n")
        
        console.print("[bold]Ejemplos:[/bold]")
        console.print("• [yellow]template_manager.display_quick_cost_estimate('ec2-basic')[/yellow]")
        console.print("• [yellow]template_manager.display_detailed_cost_estimate('ec2-basic')[/yellow]")
        console.print("• [yellow]template_manager.display_cost_estimate('ec2-basic', verbose=True)[/yellow]")
        
        console.print() 