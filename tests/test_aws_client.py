"""
Tests para el módulo AWSClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, NoCredentialsError
from rich.console import Console

from src.aws_client import AWSClient


class TestAWSClient:
    """Tests para la clase AWSClient"""
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_initialization_success(self, mock_session, mock_config):
        """Test de inicialización exitosa"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Crear instancia
        aws_client = AWSClient()
        
        # Verificar que se inicializó correctamente
        assert aws_client.session is not None
        assert 'ec2' in aws_client.clients
        assert 's3' in aws_client.clients
        assert 'lambda' in aws_client.clients
        assert 'rds' in aws_client.clients
        assert 'cloudformation' in aws_client.clients
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.console.print')
    def test_initialization_no_credentials(self, mock_print, mock_config):
        """Test de inicialización sin credenciales"""
        mock_config.validate_aws_credentials.return_value = False
        
        with pytest.raises(NoCredentialsError):
            AWSClient()
        
        # Verificar mensaje de error
        mock_print.assert_called()
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    @patch('src.aws_client.console.print')
    def test_initialization_exception(self, mock_print, mock_session, mock_config):
        """Test de inicialización con excepción"""
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            AWSClient()
        
        # Verificar mensaje de error
        mock_print.assert_called()
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_test_connection_success(self, mock_session, mock_config):
        """Test de conexión exitosa"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes para la inicialización
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        # Mock de STS para test_connection
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {'Account': '123456789012'}
        
        # Configurar el mock para que cuando se llame a client('sts') devuelva mock_sts
        # y para otros servicios use la lista de clientes configurada
        client_list = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        def client_side_effect(service_name):
            if service_name == 'sts':
                return mock_sts
            # Para otros servicios, usar la lista de clientes configurada
            return client_list.pop(0) if client_list else Mock()
        
        mock_session_instance.client.side_effect = client_side_effect
        
        aws_client = AWSClient()
        
        # Test de conexión
        result = aws_client.test_connection()
        assert result is True
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    @patch('src.aws_client.console.print')
    def test_test_connection_failure(self, mock_print, mock_session, mock_config):
        """Test de conexión fallida"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes para la inicialización
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        # Mock de STS para test_connection con error
        mock_sts = Mock()
        mock_sts.get_caller_identity.side_effect = Exception("Connection failed")
        
        # Configurar el mock para que cuando se llame a client('sts') devuelva mock_sts
        # y para otros servicios use la lista de clientes configurada
        client_list = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        def client_side_effect(service_name):
            if service_name == 'sts':
                return mock_sts
            # Para otros servicios, usar la lista de clientes configurada
            return client_list.pop(0) if client_list else Mock()
        
        mock_session_instance.client.side_effect = client_side_effect
        
        aws_client = AWSClient()
        
        # Test de conexión
        result = aws_client.test_connection()
        assert result is False
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_list_ec2_instances_success(self, mock_session, mock_config):
        """Test de listado de instancias EC2 exitoso"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuesta EC2
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'InstanceType': 't3.micro',
                            'State': {'Name': 'running'},
                            'LaunchTime': '2024-01-01T00:00:00Z',
                            'PublicIpAddress': '192.168.1.1',
                            'PrivateIpAddress': '10.0.0.1'
                        }
                    ]
                }
            ]
        }
        
        aws_client = AWSClient()
        
        # Test de listado
        instances = aws_client.list_ec2_instances()
        
        assert len(instances) == 1
        assert instances[0]['id'] == 'i-1234567890abcdef0'
        assert instances[0]['type'] == 't3.micro'
        assert instances[0]['state'] == 'running'
        assert instances[0]['public_ip'] == '192.168.1.1'
        assert instances[0]['private_ip'] == '10.0.0.1'
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    @patch('src.aws_client.console.print')
    def test_list_ec2_instances_client_error(self, mock_print, mock_session, mock_config):
        """Test de listado de instancias EC2 con error de cliente"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de error de cliente
        mock_ec2.describe_instances.side_effect = ClientError(
            {'Error': {'Code': 'UnauthorizedOperation', 'Message': 'Not authorized'}},
            'DescribeInstances'
        )
        
        aws_client = AWSClient()
        
        # Test de listado con error
        instances = aws_client.list_ec2_instances()
        
        assert instances == []
        mock_print.assert_called()
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_list_s3_buckets_success(self, mock_session, mock_config):
        """Test de listado de buckets S3 exitoso"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuesta S3
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {
                    'Name': 'test-bucket-1',
                    'CreationDate': '2024-01-01T00:00:00Z'
                },
                {
                    'Name': 'test-bucket-2',
                    'CreationDate': '2024-01-02T00:00:00Z'
                }
            ]
        }
        
        aws_client = AWSClient()
        
        # Test de listado
        buckets = aws_client.list_s3_buckets()
        
        assert len(buckets) == 2
        assert buckets[0]['name'] == 'test-bucket-1'
        assert buckets[1]['name'] == 'test-bucket-2'
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_list_lambda_functions_success(self, mock_session, mock_config):
        """Test de listado de funciones Lambda exitoso"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuesta Lambda
        mock_lambda.list_functions.return_value = {
            'Functions': [
                {
                    'FunctionName': 'test-function-1',
                    'Runtime': 'python3.9',
                    'MemorySize': 128,
                    'Timeout': 3,
                    'LastModified': '2024-01-01T00:00:00Z'
                }
            ]
        }
        
        aws_client = AWSClient()
        
        # Test de listado
        functions = aws_client.list_lambda_functions()
        
        assert len(functions) == 1
        assert functions[0]['name'] == 'test-function-1'
        assert functions[0]['runtime'] == 'python3.9'
        assert functions[0]['memory_size'] == 128
        assert functions[0]['timeout'] == 3
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_list_rds_instances_success(self, mock_session, mock_config):
        """Test de listado de instancias RDS exitoso"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuesta RDS
        mock_rds.describe_db_instances.return_value = {
            'DBInstances': [
                {
                    'DBInstanceIdentifier': 'test-db-1',
                    'Engine': 'mysql',
                    'DBInstanceStatus': 'available',
                    'DBInstanceClass': 'db.t3.micro',
                    'AllocatedStorage': 20
                }
            ]
        }
        
        aws_client = AWSClient()
        
        # Test de listado
        instances = aws_client.list_rds_instances()
        
        assert len(instances) == 1
        assert instances[0]['identifier'] == 'test-db-1'
        assert instances[0]['engine'] == 'mysql'
        assert instances[0]['status'] == 'available'
        assert instances[0]['instance_class'] == 'db.t3.micro'
        assert instances[0]['allocated_storage'] == 20
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    @patch('src.aws_client.console.print')
    def test_display_resources_no_resources(self, mock_print, mock_session, mock_config):
        """Test de display de recursos sin recursos"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuestas vacías
        mock_ec2.describe_instances.return_value = {'Reservations': []}
        mock_s3.list_buckets.return_value = {'Buckets': []}
        mock_lambda.list_functions.return_value = {'Functions': []}
        mock_rds.describe_db_instances.return_value = {'DBInstances': []}
        
        aws_client = AWSClient()
        
        # Test de display
        aws_client.display_resources()
        
        # Verificar mensajes de "no hay recursos"
        mock_print.assert_called()
    
    @patch('src.aws_client.config')
    @patch('src.aws_client.boto3.Session')
    def test_display_resources_with_resources(self, mock_session, mock_config):
        """Test de display de recursos con recursos"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_config.aws_access_key_id = 'test_key'
        mock_config.aws_secret_access_key = 'test_secret'
        mock_config.aws_default_region = 'us-east-1'
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        
        # Mock de clientes
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_lambda = Mock()
        mock_rds = Mock()
        mock_cloudformation = Mock()
        
        mock_session_instance.client.side_effect = [mock_ec2, mock_s3, mock_lambda, mock_rds, mock_cloudformation]
        
        # Mock de respuestas con recursos
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'InstanceType': 't3.micro',
                            'State': {'Name': 'running'},
                            'LaunchTime': '2024-01-01T00:00:00Z',
                            'PublicIpAddress': '192.168.1.1',
                            'PrivateIpAddress': '10.0.0.1'
                        }
                    ]
                }
            ]
        }
        
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {
                    'Name': 'test-bucket',
                    'CreationDate': '2024-01-01T00:00:00Z'
                }
            ]
        }
        
        mock_lambda.list_functions.return_value = {
            'Functions': [
                {
                    'FunctionName': 'test-function',
                    'Runtime': 'python3.9',
                    'MemorySize': 128,
                    'Timeout': 3,
                    'LastModified': '2024-01-01T00:00:00Z'
                }
            ]
        }
        
        mock_rds.describe_db_instances.return_value = {
            'DBInstances': [
                {
                    'DBInstanceIdentifier': 'test-db',
                    'Engine': 'mysql',
                    'DBInstanceStatus': 'available',
                    'DBInstanceClass': 'db.t3.micro',
                    'AllocatedStorage': 20
                }
            ]
        }
        
        aws_client = AWSClient()
        
        # Test de display
        aws_client.display_resources()
        
        # No debería haber errores
        assert True
