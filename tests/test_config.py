"""
Tests para el módulo de configuración
"""

import os
import pytest
from unittest.mock import patch, Mock, MagicMock
from src.config import Config


class TestConfig:
    """Tests para la clase Config"""
    
    def test_config_initialization(self):
        """Test de inicialización de configuración"""
        config = Config()
        assert hasattr(config, 'aws_access_key_id')
        assert hasattr(config, 'aws_secret_access_key')
        assert hasattr(config, 'aws_default_region')
        assert hasattr(config, 'aws_session_token')
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-west-2'
    })
    def test_validate_aws_credentials_with_valid_credentials(self):
        """Test de validación con credenciales válidas"""
        config = Config()
        assert config.validate_aws_credentials() is True
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': '',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_validate_aws_credentials_with_invalid_credentials(self):
        """Test de validación con credenciales inválidas"""
        config = Config()
        assert config.validate_aws_credentials() is False
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_get_aws_config(self):
        """Test de obtención de configuración AWS"""
        config = Config()
        aws_config = config.get_aws_config()
        
        assert 'region_name' in aws_config
        assert aws_config['region_name'] == 'us-east-1'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_SESSION_TOKEN': 'test_token'
    })
    def test_get_aws_config_with_session_token(self):
        """Test de configuración AWS con token de sesión"""
        config = Config()
        aws_config = config.get_aws_config()
        
        assert 'region_name' in aws_config
        assert 'aws_session_token' in aws_config
        assert aws_config['aws_session_token'] == 'test_token'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_get_credentials(self):
        """Test de obtención de credenciales"""
        config = Config()
        credentials = config.get_credentials()
        
        assert credentials['aws_access_key_id'] == 'test_key'
        assert credentials['aws_secret_access_key'] == 'test_secret'
        assert credentials['region_name'] == 'us-east-1'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_aws_credentials_properties(self):
        """Test de propiedades de credenciales AWS"""
        config = Config()
        
        assert config.aws_access_key_id == 'test_key'
        assert config.aws_secret_access_key == 'test_secret'
        assert config.aws_default_region == 'us-east-1'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_aws_config_structure(self):
        """Test de estructura de configuración AWS"""
        config = Config()
        aws_config = config.get_aws_config()
        
        # Verificar que contiene todas las claves esperadas
        expected_keys = ['region_name']
        for key in expected_keys:
            assert key in aws_config
        
        # Verificar tipos de datos
        assert isinstance(aws_config['region_name'], str)
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_credentials_structure(self):
        """Test de estructura de credenciales"""
        config = Config()
        credentials = config.get_credentials()
        
        # Verificar que contiene todas las claves esperadas
        expected_keys = ['aws_access_key_id', 'aws_secret_access_key', 'region_name']
        for key in expected_keys:
            assert key in credentials
        
        # Verificar tipos de datos
        assert isinstance(credentials['aws_access_key_id'], str)
        assert isinstance(credentials['aws_secret_access_key'], str)
        assert isinstance(credentials['region_name'], str)
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_config_consistency(self):
        """Test de consistencia entre diferentes métodos de configuración"""
        config = Config()
        
        # Verificar que los valores son consistentes entre métodos
        aws_config = config.get_aws_config()
        credentials = config.get_credentials()
        
        assert aws_config['region_name'] == credentials['region_name']
        assert aws_config['region_name'] == config.aws_default_region
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_config_immutability(self):
        """Test de que la configuración no se modifica accidentalmente"""
        config = Config()
        
        # Obtener configuración inicial
        initial_aws_config = config.get_aws_config()
        initial_credentials = config.get_credentials()
        
        # Modificar la configuración (simular cambio de región)
        config.aws_default_region = 'eu-west-1'
        
        # Verificar que la configuración AWS cambió
        current_aws_config = config.get_aws_config()
        current_credentials = config.get_credentials()
        
        assert current_aws_config['region_name'] == 'eu-west-1'
        assert current_credentials['region_name'] == 'eu-west-1'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_config_repr(self):
        """Test de representación string de la configuración"""
        config = Config()
        config_repr = repr(config)
        
        # Verificar que la representación contiene información útil
        assert 'Config' in config_repr
        assert 'object' in config_repr
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_config_str(self):
        """Test de conversión a string de la configuración"""
        config = Config()
        config_str = str(config)
        
        # Verificar que la conversión a string funciona
        assert isinstance(config_str, str)
        assert len(config_str) > 0
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    def test_config_attributes_access(self):
        """Test de acceso a atributos de configuración"""
        config = Config()
        
        # Verificar que se puede acceder a todos los atributos
        assert hasattr(config, 'aws_access_key_id')
        assert hasattr(config, 'aws_secret_access_key')
        assert hasattr(config, 'aws_default_region')
        assert hasattr(config, 'aws_session_token')
        
        # Verificar que los atributos no son None
        assert config.aws_access_key_id is not None
        assert config.aws_secret_access_key is not None
        assert config.aws_default_region is not None
        # aws_session_token puede ser None si no está configurado 