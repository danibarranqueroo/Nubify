"""
Tests para el módulo Deployer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table

from src.deployer import Deployer


class TestDeployer:
    """Tests para la clase Deployer"""
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_initialization(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de inicialización del Deployer"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Crear instancia
        deployer = Deployer()
        
        # Verificar que se creó correctamente
        assert deployer.template_manager == mock_template_manager_instance
        mock_boto3_client.assert_called_once_with(
            'cloudformation',
            aws_access_key_id='test_key',
            aws_secret_access_key='test_secret',
            region_name='us-east-1'
        )
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    @patch('builtins.open')
    def test_deploy_template_success(self, mock_open, mock_template_manager, mock_config, mock_boto3_client):
        """Test de despliegue exitoso de template"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        mock_template_manager_instance.get_template.return_value = {'file_path': '/test/template.yaml'}
        
        # Mock del archivo
        mock_file = Mock()
        mock_file.read.return_value = 'template content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock de la respuesta de create_stack
        mock_cf_client.create_stack.return_value = {
            'StackId': 'arn:aws:cloudformation:us-east-1:123456789012:stack/test-stack/12345678-1234-1234-1234-123456789012'
        }
        
        # Mock del waiter
        mock_waiter = Mock()
        mock_cf_client.get_waiter.return_value = mock_waiter
        
        deployer = Deployer()
        
        # Ejecutar despliegue
        result = deployer.deploy_template('test-template', 'test-stack', {'param': 'value'})
        
        # Verificar que se llamó correctamente
        mock_cf_client.create_stack.assert_called_once()
        assert result is True
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_deploy_template_not_found(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de despliegue con template no encontrado"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        mock_template_manager_instance.get_template.return_value = None
        
        deployer = Deployer()
        
        # Ejecutar despliegue
        result = deployer.deploy_template('nonexistent-template', 'test-stack')
        
        # Verificar que falló
        assert result is False
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_deploy_template_client_error(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de despliegue con error de cliente"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        mock_template_manager_instance.get_template.return_value = {'file_path': '/test/template.yaml'}
        
        # Mock del archivo
        mock_file = Mock()
        mock_file.read.return_value = 'template content'
        
        # Simular error en create_stack
        mock_cf_client.create_stack.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Template format error'}},
            'CreateStack'
        )
        
        with patch('builtins.open', return_value=mock_file):
            deployer = Deployer()
            
            # Ejecutar despliegue
            result = deployer.deploy_template('test-template', 'test-stack')
            
            # Verificar que falló
            assert result is False
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_list_stacks_success(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de listado exitoso de stacks"""
        from datetime import datetime
        
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Mock de la respuesta de list_stacks
        mock_cf_client.list_stacks.return_value = {
            'StackSummaries': [
                {
                    'StackName': 'test-stack-1',
                    'StackStatus': 'CREATE_COMPLETE',
                    'CreationTime': datetime(2023, 1, 1, 0, 0, 0)
                },
                {
                    'StackName': 'test-stack-2',
                    'StackStatus': 'DELETE_COMPLETE',
                    'CreationTime': datetime(2023, 1, 2, 0, 0, 0)
                }
            ]
        }
        
        deployer = Deployer()
        
        # Ejecutar listado
        result = deployer.list_stacks()
        
        # Verificar que se obtuvo la lista
        assert len(result) == 2
        assert result[0]['name'] == 'test-stack-1'
        assert result[1]['name'] == 'test-stack-2'
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_list_stacks_error(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de listado de stacks con error"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Simular error en list_stacks
        mock_cf_client.list_stacks.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'ListStacks'
        )
        
        deployer = Deployer()
        
        # Ejecutar listado
        result = deployer.list_stacks()
        
        # Verificar que se retornó lista vacía
        assert result == []
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_delete_stack_success(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de eliminación exitosa de stack"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Mock del waiter
        mock_waiter = Mock()
        mock_cf_client.get_waiter.return_value = mock_waiter
        
        deployer = Deployer()
        
        # Ejecutar eliminación
        result = deployer.delete_stack('test-stack')
        
        # Verificar que se llamó correctamente
        mock_cf_client.delete_stack.assert_called_once_with(StackName='test-stack')
        assert result is True
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_delete_stack_not_found(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de eliminación de stack no encontrado"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Simular error de validación (stack no encontrado)
        mock_cf_client.delete_stack.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Stack does not exist'}},
            'DeleteStack'
        )
        
        deployer = Deployer()
        
        # Ejecutar eliminación
        result = deployer.delete_stack('nonexistent-stack')
        
        # Verificar que falló
        assert result is False
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_get_stack_resources_success(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de obtención exitosa de recursos de stack"""
        from datetime import datetime
        
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Mock de la respuesta de list_stack_resources
        mock_cf_client.list_stack_resources.return_value = {
            'StackResourceSummaries': [
                {
                    'LogicalResourceId': 'EC2Instance',
                    'PhysicalResourceId': 'i-1234567890abcdef0',
                    'ResourceType': 'AWS::EC2::Instance',
                    'ResourceStatus': 'CREATE_COMPLETE',
                    'LastUpdatedTimestamp': datetime(2023, 1, 1, 0, 0, 0)
                }
            ]
        }
        
        deployer = Deployer()
        
        # Ejecutar obtención de recursos
        result = deployer.get_stack_resources('test-stack')
        
        # Verificar que se obtuvieron los recursos
        assert len(result) == 1
        assert result[0]['logical_id'] == 'EC2Instance'
        assert result[0]['type'] == 'AWS::EC2::Instance'
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    def test_get_stack_resources_error(self, mock_template_manager, mock_config, mock_boto3_client):
        """Test de obtención de recursos con error"""
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Simular error en list_stack_resources
        mock_cf_client.list_stack_resources.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'Stack does not exist'}},
            'ListStackResources'
        )
        
        deployer = Deployer()
        
        # Ejecutar obtención de recursos
        result = deployer.get_stack_resources('nonexistent-stack')
        
        # Verificar que se retornó lista vacía
        assert result == []
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    @patch('src.deployer.console')
    def test_display_stacks(self, mock_console, mock_template_manager, mock_config, mock_boto3_client):
        """Test de visualización de stacks"""
        from datetime import datetime
        
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Mock de la respuesta de list_stacks
        mock_cf_client.list_stacks.return_value = {
            'StackSummaries': [
                {
                    'StackName': 'test-stack',
                    'StackStatus': 'CREATE_COMPLETE',
                    'CreationTime': datetime(2023, 1, 1, 0, 0, 0)
                }
            ]
        }
        
        deployer = Deployer()
        
        # Ejecutar visualización
        deployer.display_stacks()
        
        # Verificar que se llamó a console.print
        mock_console.print.assert_called()
    
    @patch('src.deployer.boto3.client')
    @patch('src.deployer.config')
    @patch('src.deployer.TemplateManager')
    @patch('src.deployer.console')
    def test_display_stack_resources(self, mock_console, mock_template_manager, mock_config, mock_boto3_client):
        """Test de visualización de recursos de stack"""
        from datetime import datetime
        
        # Configurar mocks
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_cf_client = Mock()
        mock_boto3_client.return_value = mock_cf_client
        
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        # Mock de la respuesta de list_stack_resources
        mock_cf_client.list_stack_resources.return_value = {
            'StackResourceSummaries': [
                {
                    'LogicalResourceId': 'EC2Instance',
                    'PhysicalResourceId': 'i-1234567890abcdef0',
                    'ResourceType': 'AWS::EC2::Instance',
                    'ResourceStatus': 'CREATE_COMPLETE',
                    'LastUpdatedTimestamp': datetime(2023, 1, 1, 0, 0, 0)
                }
            ]
        }
        
        deployer = Deployer()
        
        # Ejecutar visualización
        deployer.display_stack_resources('test-stack')
        
        # Verificar que se llamó a console.print
        mock_console.print.assert_called()
