"""
Tests para el módulo NubifyChatbot
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from src.chat import NubifyChatbot


class TestNubifyChatbot:
    """Tests para la clase NubifyChatbot"""
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_initialization_success(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de inicialización exitosa del chatbot"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Verificar que se inicializa correctamente
        assert chatbot.model is not None
        assert chatbot.template_manager is not None
        assert chatbot.aws_client is not None
        assert chatbot.conversation_history == []
        
        # Verificar que se llamó a genai.configure
        mock_configure.assert_called_once_with(api_key='test_api_key')
        mock_genai_model.assert_called_once_with('gemini-1.5-flash')
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.console.print')
    def test_initialization_no_api_key(self, mock_print, mock_getenv):
        """Test de inicialización sin API key"""
        # Configurar mocks
        mock_getenv.return_value = None
        
        chatbot = NubifyChatbot()
        
        # Verificar que se muestra el error
        mock_print.assert_called()
        assert chatbot.model is None
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.console.print')
    def test_initialization_exception(self, mock_print, mock_configure, mock_getenv):
        """Test de inicialización con excepción"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_configure.side_effect = Exception("API Error")
        
        chatbot = NubifyChatbot()
        
        # Verificar que se muestra el error
        mock_print.assert_called()
        assert chatbot.model is None
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_get_system_prompt(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de obtención del prompt del sistema"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        prompt = chatbot._get_system_prompt()
        
        # Verificar que el prompt contiene información relevante
        assert 'NubifyBot' in prompt
        assert 'nubify' in prompt.lower()
        assert 'aws' in prompt.lower()
        assert 'cloudformation' in prompt.lower()
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    @patch('src.chat.os.path.dirname')
    @patch('src.chat.os.listdir')
    @patch('builtins.open')
    def test_get_templates_context(self, mock_open, mock_listdir, mock_dirname, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de obtención del contexto de plantillas"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        mock_dirname.return_value = '/test/path'
        mock_listdir.return_value = ['ec2-basic.yaml', 'lambda-function.yaml', 's3-bucket.yaml']
        
        # Mock del archivo abierto
        mock_file = Mock()
        mock_file.read.return_value = 'template content'
        mock_open.return_value.__enter__.return_value = mock_file
        
        chatbot = NubifyChatbot()
        context = chatbot._get_templates_context()
        
        # Verificar que se obtiene el contexto
        assert 'ec2-basic' in context
        assert 'lambda-function' in context
        assert 's3-bucket' in context
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_explain_service(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para explicar servicio"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser EXPLAIN_SERVICE
        intent = chatbot._analyze_intent("¿Qué es EC2?")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_create_template(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para crear plantilla"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser CREATE_TEMPLATE
        intent = chatbot._analyze_intent("Crea una plantilla para EC2")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_help_command(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para ayuda de comando"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser HELP_COMMAND
        intent = chatbot._analyze_intent("¿Cómo uso el comando deploy?")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_troubleshoot(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para resolución de problemas"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser TROUBLESHOOT
        intent = chatbot._analyze_intent("Error al desplegar stack")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_cost_estimation(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para estimación de costos"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser COST_ESTIMATION
        intent = chatbot._analyze_intent("¿Cuánto cuesta esta plantilla?")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_analyze_intent_recommend(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de análisis de intención para recomendaciones"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería ser RECOMMEND
        intent = chatbot._analyze_intent("¿Qué servicio me recomiendas para una aplicación web?")
        
        # Verificar que se analiza correctamente
        assert 'intent' in intent
        assert 'extracted_info' in intent
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_handle_explain_service(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de manejo de explicación de servicios"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="EC2 es un servicio de computación en la nube...")
        mock_genai_model.return_value = mock_model
        
        chatbot = NubifyChatbot()
        
        # Test con servicio válido
        response = chatbot._handle_explain_service("EC2")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_handle_help_command(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de manejo de ayuda de comandos"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con comando válido
        response = chatbot._handle_help_command("deploy")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_handle_troubleshoot(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de manejo de resolución de problemas"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Para resolver este error de validación...")
        mock_genai_model.return_value = mock_model
        
        chatbot = NubifyChatbot()
        
        # Test con error válido
        response = chatbot._handle_troubleshoot("Error de validación")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_handle_cost_estimation(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de manejo de estimación de costos"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Test con solicitud válida
        response = chatbot._handle_cost_estimation("¿Cuánto cuesta EC2?")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_handle_recommend(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de manejo de recomendaciones"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Para una base de datos, te recomiendo RDS...")
        mock_genai_model.return_value = mock_model
        
        chatbot = NubifyChatbot()
        
        # Test con solicitud válida
        response = chatbot._handle_recommend("Necesito una base de datos")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_generate_response_explain_service(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de generación de respuesta para explicar servicio"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Lambda es un servicio serverless...")
        mock_genai_model.return_value = mock_model
        
        chatbot = NubifyChatbot()
        
        # Test con entrada que debería generar respuesta de explicación
        response = chatbot._generate_response("¿Qué es Lambda?")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_generate_response_general_question(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de generación de respuesta para pregunta general"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Respuesta del modelo")
        mock_genai_model.return_value = mock_model
        
        chatbot = NubifyChatbot()
        
        # Test con entrada general
        response = chatbot._generate_response("¿Cómo funciona nubify?")
        
        # Verificar que se genera una respuesta
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    @patch('src.chat.console.print')
    @patch('src.chat.Prompt.ask')
    def test_start_chat_exit(self, mock_prompt, mock_print, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de inicio de chat con salida"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        mock_prompt.return_value = 'salir'
        
        chatbot = NubifyChatbot()
        
        # Test de inicio de chat
        chatbot.start_chat()
        
        # Verificar que se muestra el mensaje de bienvenida
        mock_print.assert_called()
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_conversation_history(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de historial de conversación"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        
        chatbot = NubifyChatbot()
        
        # Verificar que el historial está vacío al inicio
        assert len(chatbot.conversation_history) == 0
        
        # Simular conversación
        chatbot.conversation_history.append({
            'user': '¿Qué es EC2?',
            'bot': 'EC2 es un servicio de computación en la nube...'
        })
        
        # Verificar que se agregó al historial
        assert len(chatbot.conversation_history) == 1
        assert chatbot.conversation_history[0]['user'] == '¿Qué es EC2?'
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_template_manager_integration(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de integración con TemplateManager"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        mock_template_manager_instance = Mock()
        mock_template_manager.return_value = mock_template_manager_instance
        
        chatbot = NubifyChatbot()
        
        # Verificar que se creó el TemplateManager
        assert chatbot.template_manager is not None
        mock_template_manager.assert_called_once()
    
    @patch('src.chat.os.getenv')
    @patch('src.chat.genai.configure')
    @patch('src.chat.genai.GenerativeModel')
    @patch('src.chat.TemplateManager')
    @patch('src.chat.AWSClient')
    def test_aws_client_integration(self, mock_aws_client, mock_template_manager, mock_genai_model, mock_configure, mock_getenv):
        """Test de integración con AWSClient"""
        # Configurar mocks
        mock_getenv.return_value = 'test_api_key'
        mock_genai_model.return_value = Mock()
        mock_aws_client_instance = Mock()
        mock_aws_client.return_value = mock_aws_client_instance
        
        chatbot = NubifyChatbot()
        
        # Verificar que se creó el AWSClient
        assert chatbot.aws_client is not None
        mock_aws_client.assert_called_once()
