"""
Módulo de configuración para Nubify
Maneja variables de entorno y configuración de AWS
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Clase para manejar la configuración de la aplicación"""
    
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_default_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        
    def validate_aws_credentials(self) -> bool:
        """Valida que las credenciales de AWS estén configuradas"""
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            return False
        return True
    
    def get_aws_config(self) -> dict:
        """Retorna la configuración de AWS para boto3"""
        config = {
            'region_name': self.aws_default_region
        }
        
        if self.aws_session_token:
            config['aws_session_token'] = self.aws_session_token
            
        return config
    
    def get_credentials(self) -> dict:
        """Retorna las credenciales de AWS"""
        return {
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key,
            'region_name': self.aws_default_region
        }

# Instancia global de configuración
config = Config() 