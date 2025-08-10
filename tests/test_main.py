"""
Tests para el módulo main.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from src.main import cli


class TestMainCLI:
    """Tests para la interfaz CLI principal"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.runner = CliRunner()
    
    @patch('src.main.AWSClient')
    def test_test_command_success(self, mock_aws_client_class):
        """Test del comando test cuando la conexión es exitosa"""
        # Configurar mock
        mock_aws_client = Mock()
        mock_aws_client.test_connection.return_value = True
        mock_aws_client_class.return_value = mock_aws_client
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['test'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Conexión exitosa con AWS' in result.output
    
    @patch('src.main.AWSClient')
    def test_test_command_failure(self, mock_aws_client_class):
        """Test del comando test cuando la conexión falla"""
        # Configurar mock
        mock_aws_client = Mock()
        mock_aws_client.test_connection.return_value = False
        mock_aws_client_class.return_value = mock_aws_client
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['test'])
        
        # Verificar resultado
        assert result.exit_code == 1
        assert 'Error al conectar con AWS' in result.output
    
    @patch('src.main.AWSClient')
    def test_test_command_exception(self, mock_aws_client_class):
        """Test del comando test cuando ocurre una excepción"""
        # Configurar mock para que lance excepción
        mock_aws_client_class.side_effect = Exception("Error de conexión")
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['test'])
        
        # Verificar resultado
        assert result.exit_code == 1
        assert 'Error: Error de conexión' in result.output
    
    @patch('src.main.AWSClient')
    def test_list_resources_success(self, mock_aws_client_class):
        """Test del comando list-resources"""
        # Configurar mock
        mock_aws_client = Mock()
        mock_aws_client_class.return_value = mock_aws_client
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['list-resources'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Listando recursos AWS' in result.output
        mock_aws_client.display_resources.assert_called_once()
    
    @patch('src.main.TemplateManager')
    def test_list_templates_success(self, mock_template_manager_class):
        """Test del comando list-templates"""
        # Configurar mock
        mock_template_manager = Mock()
        mock_template_manager_class.return_value = mock_template_manager
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['list-templates'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Listando plantillas disponibles' in result.output
        mock_template_manager.display_templates.assert_called_once()
    
    @patch('src.main.TemplateManager')
    def test_template_details_success(self, mock_template_manager_class):
        """Test del comando template-details"""
        # Configurar mock
        mock_template_manager = Mock()
        mock_template_manager_class.return_value = mock_template_manager
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['template-details', 'ec2-basic'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Mostrando detalles de: ec2-basic' in result.output
        mock_template_manager.display_template_details.assert_called_once_with('ec2-basic')
    
    @patch('src.main.TemplateManager')
    def test_estimate_costs_success(self, mock_template_manager_class):
        """Test del comando estimate-costs"""
        # Configurar mock
        mock_template_manager = Mock()
        mock_template_manager.display_cost_estimate.return_value = None
        mock_template_manager_class.return_value = mock_template_manager
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['estimate-costs', 'ec2-basic'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Estimando costes de: ec2-basic' in result.output
        mock_template_manager.display_cost_estimate.assert_called_once()
    
    @patch('src.main.TemplateManager')
    @patch('src.main.Deployer')
    @patch('src.main.config')
    @patch('src.main.click.confirm')
    def test_deploy_success(self, mock_click_confirm, mock_config, mock_deployer_class, mock_template_manager_class):
        """Test del comando deploy"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = True
        mock_click_confirm.return_value = True  # Simular confirmación del usuario
        
        mock_template_manager = Mock()
        mock_template_manager.estimate_costs.return_value = {
            'estimated_monthly_cost': 50.0
        }
        mock_template_manager_class.return_value = mock_template_manager
        
        mock_deployer = Mock()
        mock_deployer.deploy_template.return_value = True
        mock_deployer_class.return_value = mock_deployer
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['deploy', 'ec2-basic', 'test-stack'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Plantilla: ec2-basic' in result.output
        mock_deployer.deploy_template.assert_called_once()
    
    @patch('src.main.TemplateManager')
    @patch('src.main.Deployer')
    @patch('src.main.config')
    def test_deploy_failure_no_credentials(self, mock_config, mock_deployer_class, mock_template_manager_class):
        """Test del comando deploy cuando fallan las credenciales"""
        # Configurar mocks
        mock_config.validate_aws_credentials.return_value = False
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['deploy', 'ec2-basic', 'test-stack'])
        
        # Verificar resultado
        assert result.exit_code == 1
        assert 'Credenciales de AWS no configuradas' in result.output
    
    @patch('src.main.Deployer')
    def test_list_stacks_success(self, mock_deployer_class):
        """Test del comando list-stacks"""
        # Configurar mock
        mock_deployer = Mock()
        mock_deployer_class.return_value = mock_deployer
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['list-stacks'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Listando stacks' in result.output
        mock_deployer.display_stacks.assert_called_once()
    
    @patch('src.main.Deployer')
    def test_stack_resources_success(self, mock_deployer_class):
        """Test del comando stack-resources"""
        # Configurar mock
        mock_deployer = Mock()
        mock_deployer_class.return_value = mock_deployer
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['stack-resources', 'test-stack'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Mostrando recursos' in result.output
        mock_deployer.display_stack_resources.assert_called_once_with('test-stack')
    
    @patch('src.main.Deployer')
    @patch('src.main.click.confirm')
    def test_delete_stack_success(self, mock_click_confirm, mock_deployer_class):
        """Test del comando delete-stack"""
        # Configurar mocks
        mock_click_confirm.return_value = True  # Simular confirmación del usuario
        
        mock_deployer = Mock()
        mock_deployer.delete_stack.return_value = True
        mock_deployer_class.return_value = mock_deployer
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['delete-stack', 'test-stack'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Eliminando stack: test-stack' in result.output
        mock_deployer.delete_stack.assert_called_once_with('test-stack')
    
    @patch('src.main.NubifyChatbot')
    def test_chat_success(self, mock_chatbot_class):
        """Test del comando chat"""
        # Configurar mock
        mock_chatbot = Mock()
        mock_chatbot_class.return_value = mock_chatbot
        
        # Ejecutar comando
        result = self.runner.invoke(cli, ['chat'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Iniciando chat' in result.output
        mock_chatbot.start_chat.assert_called_once()
    
    def test_help_command(self):
        """Test del comando help"""
        # Ejecutar comando
        result = self.runner.invoke(cli, ['help'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Ayuda de Nubify' in result.output
    
    def test_version_option(self):
        """Test de la opción de versión"""
        # Ejecutar comando
        result = self.runner.invoke(cli, ['--version'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Nubify, version 0.1.0' in result.output
    
    def test_cli_group_help(self):
        """Test de la ayuda del grupo CLI"""
        # Ejecutar comando
        result = self.runner.invoke(cli, ['--help'])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert 'Nubify - Plataforma para simplificar' in result.output
