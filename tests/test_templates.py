"""
Tests para el módulo templates.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.templates import TemplateManager


class TestTemplateManager:
    """Tests para la clase TemplateManager"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.template_manager = TemplateManager("test_templates")
    
    @patch('src.templates.boto3.client')
    def test_initialization(self, mock_boto3_client):
        """Test de inicialización de TemplateManager"""
        # Configurar mock para boto3.client
        mock_pricing_client = Mock()
        mock_boto3_client.return_value = mock_pricing_client
        
        # Crear instancia
        tm = TemplateManager("custom_templates")
        
        # Verificar atributos
        assert tm.templates_dir == Path("custom_templates")
        assert isinstance(tm.templates, dict)
        assert tm.pricing_client == mock_pricing_client
    
    @patch('src.templates.boto3.client')
    def test_initialization_pricing_api_failure(self, mock_boto3_client):
        """Test de inicialización cuando falla la Pricing API"""
        # Configurar mock para que falle
        mock_boto3_client.side_effect = Exception("Connection error")
        
        # Crear instancia (no debe fallar)
        tm = TemplateManager()
        
        # Verificar que se inicializa sin pricing client
        assert tm.pricing_client is None
        assert isinstance(tm.templates, dict)
    
    def test_get_pricing_api_status_available(self):
        """Test del estado de Pricing API cuando está disponible"""
        # Configurar mock del pricing client
        mock_response = {'Services': ['EC2', 'S3', 'RDS']}
        self.template_manager.pricing_client = Mock()
        self.template_manager.pricing_client.get_services.return_value = mock_response
        
        # Obtener estado
        status = self.template_manager.get_pricing_api_status()
        
        # Verificar resultado
        assert status['available'] is True
        assert status['region'] == 'us-east-1'
        assert status['services_count'] == 3
        assert status['error'] is None
    
    def test_get_pricing_api_status_unavailable(self):
        """Test del estado de Pricing API cuando no está disponible"""
        # Configurar mock del pricing client para que falle
        self.template_manager.pricing_client = Mock()
        self.template_manager.pricing_client.get_services.side_effect = Exception("API error")
        
        # Obtener estado
        status = self.template_manager.get_pricing_api_status()
        
        # Verificar resultado
        assert status['available'] is False
        assert status['region'] == 'us-east-1'
        assert 'API error' in status['error']
    
    def test_get_pricing_api_status_no_client(self):
        """Test del estado de Pricing API cuando no hay cliente"""
        # Sin pricing client
        self.template_manager.pricing_client = None
        
        # Obtener estado
        status = self.template_manager.get_pricing_api_status()
        
        # Verificar resultado
        assert status['available'] is False
        assert status['region'] == 'us-east-1'
        assert status['error'] == 'Cliente no inicializado'
    
    @patch('src.templates.console.print')
    def test_display_pricing_api_status_available(self, mock_console_print):
        """Test de mostrar estado de Pricing API cuando está disponible"""
        # Configurar mock del pricing client
        mock_response = {'Services': ['EC2', 'S3']}
        self.template_manager.pricing_client = Mock()
        self.template_manager.pricing_client.get_services.return_value = mock_response
        
        # Mostrar estado
        self.template_manager.display_pricing_api_status()
        
        # Verificar que se llamó a console.print
        assert mock_console_print.call_count >= 3  # Título, región, estado
    
    @patch('src.templates.console.print')
    def test_display_pricing_api_status_unavailable(self, mock_console_print):
        """Test de mostrar estado de Pricing API cuando no está disponible"""
        # Configurar mock del pricing client para que falle
        self.template_manager.pricing_client = Mock()
        self.template_manager.pricing_client.get_services.side_effect = Exception("API error")
        
        # Mostrar estado
        self.template_manager.display_pricing_api_status()
        
        # Verificar que se llamó a console.print
        assert mock_console_print.call_count >= 4  # Título, región, estado, error
    
    @patch('builtins.open')
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.exists')
    def test_load_templates(self, mock_exists, mock_glob, mock_open):
        """Test de carga de plantillas"""
        # Configurar mocks
        mock_exists.return_value = True  # El directorio existe
        
        mock_template_files = [
            Mock(name='ec2-basic.yaml'),
            Mock(name='s3-bucket.yaml')
        ]
        mock_glob.return_value = mock_template_files
        
        # Mock del contenido de archivos
        mock_file = Mock()
        mock_file.read.side_effect = [
            'Resources:\n  EC2Instance:\n    Type: AWS::EC2::Instance',
            'Resources:\n  S3Bucket:\n    Type: AWS::S3::Bucket'
        ]
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Crear nueva instancia para probar _load_templates
        with patch('src.templates.TemplateManager._load_templates') as mock_load:
            mock_load.return_value = {
                'ec2-basic': {'name': 'ec2-basic', 'resources': {'EC2Instance': {'Type': 'AWS::EC2::Instance'}}},
                's3-bucket': {'name': 's3-bucket', 'resources': {'S3Bucket': {'Type': 'AWS::S3::Bucket'}}}
            }
            
            tm = TemplateManager("test_templates")
            
            # Verificar que se cargaron las plantillas
            assert len(tm.templates) == 2
            assert 'ec2-basic' in tm.templates
            assert 's3-bucket' in tm.templates
    
    def test_list_templates(self):
        """Test de listado de plantillas"""
        # Configurar templates de prueba
        self.template_manager.templates = {
            'ec2-basic': {},
            's3-bucket': {},
            'rds-basic': {}
        }
        
        # Obtener lista
        templates = self.template_manager.list_templates()
        
        # Verificar resultado
        assert len(templates) == 3
        assert 'ec2-basic' in templates
        assert 's3-bucket' in templates
        assert 'rds-basic' in templates
    
    def test_get_template_existing(self):
        """Test de obtención de plantilla existente"""
        # Configurar template de prueba
        test_template = {'name': 'test', 'resources': {'EC2': {'Type': 'AWS::EC2::Instance'}}}
        self.template_manager.templates = {'test-template': test_template}
        
        # Obtener template
        template = self.template_manager.get_template('test-template')
        
        # Verificar resultado
        assert template == test_template
    
    def test_get_template_not_existing(self):
        """Test de obtención de plantilla inexistente"""
        # Configurar templates vacíos
        self.template_manager.templates = {}
        
        # Obtener template inexistente
        template = self.template_manager.get_template('non-existent')
        
        # Verificar resultado
        assert template == {}
    
    @patch('src.templates.console.print')
    def test_display_templates_empty(self, mock_console_print):
        """Test de mostrar plantillas cuando no hay ninguna"""
        # Configurar templates vacíos
        self.template_manager.templates = {}
        
        # Mostrar templates
        self.template_manager.display_templates()
        
        # Verificar mensaje
        mock_console_print.assert_called_with("[yellow]No hay plantillas disponibles[/yellow]")
    
    @patch('src.templates.console.print')
    @patch('src.templates.Table')
    def test_display_templates_with_data(self, mock_table_class, mock_console_print):
        """Test de mostrar plantillas con datos"""
        # Configurar mock de Table
        mock_table = Mock()
        mock_table_class.return_value = mock_table
        
        # Configurar templates de prueba
        self.template_manager.templates = {
            'ec2-basic': {
                'description': 'EC2 básico',
                'resources': {'EC2Instance': {}},
                'parameters': {'InstanceType': {}},
                'parsed': True
            }
        }
        
        # Mostrar templates
        self.template_manager.display_templates()
        
        # Verificar que se creó la tabla
        mock_table_class.assert_called_once()
        mock_table.add_column.assert_called()
        mock_table.add_row.assert_called()
        mock_console_print.assert_called_with(mock_table)
    
    @patch('src.templates.console.print')
    def test_display_template_details_not_found(self, mock_console_print):
        """Test de mostrar detalles de plantilla inexistente"""
        # Configurar templates vacíos
        self.template_manager.templates = {}
        
        # Mostrar detalles
        self.template_manager.display_template_details('non-existent')
        
        # Verificar mensaje de error
        mock_console_print.assert_called_with("[red]Plantilla 'non-existent' no encontrada[/red]")
    
    @patch('src.templates.console.print')
    @patch('src.templates.Table')
    def test_display_template_details_with_data(self, mock_table_class, mock_console_print):
        """Test de mostrar detalles de plantilla con datos"""
        # Configurar mock de Table
        mock_table = Mock()
        mock_table_class.return_value = mock_table
        
        # Configurar template de prueba
        test_template = {
            'description': 'EC2 básico',
            'raw_content': 'test content',  # Indica parseo con regex
            'resources': {
                'EC2Instance': {'Type': 'AWS::EC2::Instance'}
            },
            'parameters': {
                'InstanceType': {
                    'Type': 'String',
                    'Description': 'Tipo de instancia',
                    'Required': True
                }
            }
        }
        self.template_manager.templates = {'test-template': test_template}
        
        # Mostrar detalles
        self.template_manager.display_template_details('test-template')
        
        # Verificar que se mostraron los detalles
        assert mock_console_print.call_count >= 3  # Título, descripción, estado
    
    def test_estimate_costs_template_not_found(self):
        """Test de estimación de costes para plantilla inexistente"""
        # Configurar templates vacíos
        self.template_manager.templates = {}
        
        # Estimar costes
        result = self.template_manager.estimate_costs('non-existent')
        
        # Verificar resultado
        assert 'error' in result
        assert 'no encontrada' in result['error']
    
    @patch('src.templates.console.print')
    def test_display_cost_estimate(self, mock_console_print):
        """Test de mostrar estimación de costes"""
        # Configurar template de prueba
        test_template = {
            'resources': {
                'EC2Instance': {'Type': 'AWS::EC2::Instance'}
            }
        }
        self.template_manager.templates = {'test-template': test_template}
        
        # Mostrar estimación
        self.template_manager.display_cost_estimate('test-template')
        
        # Verificar que se llamó a console.print
        assert mock_console_print.call_count >= 1
    
    def test_quick_cost_estimate(self):
        """Test de estimación rápida de costes"""
        # Configurar template de prueba
        test_template = {
            'resources': {
                'EC2Instance': {'Type': 'AWS::EC2::Instance'}
            }
        }
        self.template_manager.templates = {'test-template': test_template}
        
        # Estimar costes rápidos
        result = self.template_manager.quick_cost_estimate('test-template')
        
        # Verificar resultado
        assert isinstance(result, dict)
    
    def test_detailed_cost_estimate(self):
        """Test de estimación detallada de costes"""
        # Configurar template de prueba
        test_template = {
            'resources': {
                'EC2Instance': {'Type': 'AWS::EC2::Instance'}
            }
        }
        self.template_manager.templates = {'test-template': test_template}
        
        # Estimar costes detallados
        result = self.template_manager.detailed_cost_estimate('test-template')
        
        # Verificar resultado
        assert isinstance(result, dict)
    
    @patch('src.templates.console.print')
    def test_show_usage_help(self, mock_console_print):
        """Test de mostrar ayuda de uso"""
        # Mostrar ayuda
        self.template_manager.show_usage_help()
        
        # Verificar que se llamó a console.print
        assert mock_console_print.call_count >= 1
