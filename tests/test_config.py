"""
Tests para el módulo de configuración
"""

import os
import pytest
from unittest.mock import patch
from src.config import Config

class TestConfig:
    """Tests para la clase Config"""
    
    def test_config_initialization(self):
        """Test de inicialización de configuración"""
        config = Config()
        assert hasattr(config, 'aws_access_key_id')
        assert hasattr(config, 'aws_secret_access_key')
        assert hasattr(config, 'aws_default_region')
    
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