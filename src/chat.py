#!/usr/bin/env python3
"""
Nubify Chat - Chatbot inteligente para asistir con nubify
"""

import os
import json
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from typing import Dict, List, Optional, Any
import yaml

from .config import config
from .templates import TemplateManager
from .aws_client import AWSClient
from .commands import get_command_info, get_all_commands, is_service_supported, get_supported_services, get_available_templates

console = Console()

class NubifyChatbot:
    """Chatbot inteligente para asistir con nubify"""
    
    def __init__(self):
        self.model = None
        self.template_manager = TemplateManager()
        self.aws_client = AWSClient()
        self.conversation_history = []
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa el modelo de Gemini"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            console.print("[red]Error: GEMINI_API_KEY no configurada[/red]")
            console.print("Por favor, configura la variable de entorno GEMINI_API_KEY")
            return False
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            return True
        except Exception as e:
            console.print(f"[red]Error al inicializar Gemini: {e}[/red]")
            return False
    
    def _get_system_prompt(self) -> str:
        """Obtiene el prompt del sistema con contexto de nubify"""
        commands_info = get_all_commands()
        commands_text = "\n".join([
            f"- {cmd}: {info['description']}"
            for cmd, info in commands_info.items()
        ])
        
        supported_services = get_supported_services()
        services_text = ", ".join([s.upper() for s in supported_services])
        
        available_templates = get_available_templates()
        templates_text = ", ".join(available_templates)
        
        return f"""
Eres NubifyBot, un asistente especializado en ayudar con la plataforma Nubify para gestión de servicios AWS.

CONTEXTO DE NUBIFY:
- Nubify es una herramienta CLI para simplificar la gestión de recursos AWS
- Permite desplegar plantillas de CloudFormation de forma sencilla
- Incluye estimación de costes y plantillas predefinidas

COMANDOS DISPONIBLES EN NUBIFY:
{commands_text}

SERVICIOS SOPORTADOS POR NUBIFY PARA CREAR PLANTILLAS:
- {services_text}

CAPACIDADES:
1. Explicar servicios AWS (puedes explicar cualquier servicio, pero solo crear plantillas para los soportados)
2. Crear plantillas de CloudFormation SOLO para {services_text}
3. Explicar comandos de nubify y su uso
4. Resolver dudas sobre configuración y despliegue
5. Recomendar servicios según necesidades específicas
6. Ayudar con errores comunes

PLANTILLAS DISPONIBLES:
- {templates_text}

IMPORTANTE:
- Solo puedes crear plantillas para {services_text}
- Para otros servicios, explica qué son pero indica que no están soportados en nubify
- Cuando crees una plantilla, automáticamente la guardarás en la carpeta templates
- Para estimación de costes, usa el comando: nubify estimate-costs <nombre-plantilla>
- SOLO sugiere comandos que realmente existen en nubify

RESPONDE DE FORMA:
- Clara y concisa
- Con ejemplos prácticos cuando sea útil
- En español
- Con comandos específicos de nubify cuando sea apropiado
"""
    
    def _get_templates_context(self) -> str:
        """Obtiene el contexto de las plantillas disponibles"""
        try:
            templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
            templates_info = []
            
            for filename in os.listdir(templates_dir):
                if filename.endswith('.yaml'):
                    template_path = os.path.join(templates_dir, filename)
                    with open(template_path, 'r') as f:
                        content = f.read()
                        templates_info.append(f"Plantilla: {filename}\nContenido:\n{content}\n")
            
            return "\n".join(templates_info)
        except Exception as e:
            return f"Error al leer plantillas: {e}"
    
    def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analiza la intención del usuario"""
        user_input_lower = user_input.lower()
        
        # Detección directa basada en palabras clave
        if any(word in user_input_lower for word in ['crear', 'crea', 'genera', 'haz', 'hacer', 'nuevo', 'nueva', 'plantilla', 'template']):
            # Verificar si menciona algún servicio AWS
            supported_services = get_supported_services()
            service_found = None
            for service in supported_services:
                if service in user_input_lower:
                    service_found = service
                    break
            
            if service_found:
                return {
                    "intent": "CREATE_TEMPLATE",
                    "confidence": 0.9,
                    "extracted_info": {"service": service_found}
                }
        
        # Detección de explicación de servicios
        if any(word in user_input_lower for word in ['explica', 'qué es', 'que es', 'describe', 'información', 'info']):
            supported_services = get_supported_services()
            for service in supported_services:
                if service in user_input_lower:
                    return {
                        "intent": "EXPLAIN_SERVICE",
                        "confidence": 0.9,
                        "extracted_info": {"service": service}
                    }
        
        # Detección de ayuda con comandos
        if any(word in user_input_lower for word in ['ayuda', 'help', 'comando', 'command', 'cómo', 'como', 'uso']):
            return {
                "intent": "HELP_COMMAND",
                "confidence": 0.8,
                "extracted_info": {}
            }
        
        # Detección de estimación de costes
        if any(word in user_input_lower for word in ['costo', 'coste', 'precio', 'gasto', 'estimate', 'cost']):
            return {
                "intent": "COST_ESTIMATION",
                "confidence": 0.8,
                "extracted_info": {}
            }
        
        # Detección de recomendaciones
        if any(word in user_input_lower for word in ['recomienda', 'recomendación', 'sugiere', 'sugerencia']):
            return {
                "intent": "RECOMMEND",
                "confidence": 0.8,
                "extracted_info": {}
            }
        
        # Detección de problemas
        if any(word in user_input_lower for word in ['error', 'problema', 'fallo', 'no funciona', 'bug']):
            return {
                "intent": "TROUBLESHOOT",
                "confidence": 0.8,
                "extracted_info": {"error": user_input}
            }
        
        # Por defecto, pregunta general
        return {
            "intent": "GENERAL_QUESTION",
            "confidence": 0.5,
            "extracted_info": {}
        }
    
    def _handle_explain_service(self, service: str) -> str:
        """Maneja solicitudes de explicación de servicios"""
        prompt = f"""
Explica el servicio AWS "{service}" de forma clara y concisa. Incluye:
- Qué es y para qué sirve
- Casos de uso principales
- Ventajas y consideraciones
- Cómo se relaciona con nubify
- Ejemplo de plantilla si es relevante

Responde en español de forma amigable.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al explicar el servicio {service}: {e}"
    
    def _handle_create_template(self, user_request: str) -> str:
        """Maneja solicitudes de creación de plantillas"""
        # Verificar si el servicio está soportado
        supported_services = get_supported_services()
        user_request_lower = user_request.lower()
        
        service_requested = None
        for service in supported_services:
            if service in user_request_lower:
                service_requested = service
                break
        
        if not service_requested:
            services_text = ", ".join([s.upper() for s in supported_services])
            return f"""
Lo siento, pero nubify actualmente solo soporta la creación de plantillas para estos servicios:
- {services_text}

Puedo explicarte otros servicios AWS, pero no puedo crear plantillas para ellos. ¿Te gustaría que te explique algún servicio específico o prefieres crear una plantilla para uno de los servicios soportados?
"""
        
        prompt = f"""
El usuario quiere crear una nueva plantilla de CloudFormation para {service_requested.upper()}. Su solicitud es:
"{user_request}"

Genera una plantilla YAML de CloudFormation que cumpla con los requisitos.
La plantilla debe ser:
- Funcional y válida
- Bien documentada con comentarios
- Segura (usar mejores prácticas)
- Optimizada en costes
- Compatible con nubify

IMPORTANTE: Responde SOLO con el contenido YAML de la plantilla, sin explicaciones adicionales.
El YAML debe estar completo y listo para usar.
"""
        
        try:
            response = self.model.generate_content(prompt)
            yaml_content = response.text.strip()
            
            # Extraer solo el YAML si hay markdown
            if yaml_content.startswith('```yaml'):
                yaml_content = yaml_content.split('```yaml')[1].split('```')[0].strip()
            elif yaml_content.startswith('```'):
                yaml_content = yaml_content.split('```')[1].split('```')[0].strip()
            
            # Generar nombre de archivo
            template_name = self._generate_template_name(service_requested, user_request)
            
            # Guardar la plantilla
            success = self._save_template(template_name, yaml_content)
            
            if success:
                return f"""
✅ **Plantilla creada exitosamente: {template_name}**

La plantilla se ha guardado automáticamente en la carpeta `templates/`.

**Para usar la plantilla:**

1. **Ver detalles:**
   ```bash
   nubify template-details {template_name}
   ```

2. **Estimar costes:**
   ```bash
   nubify estimate-costs {template_name}
   ```

3. **Desplegar:**
   ```bash
   nubify deploy {template_name} mi-stack
   ```

**Contenido de la plantilla:**
```yaml
{yaml_content}
```
"""
            else:
                return f"Error al guardar la plantilla. Aquí está el contenido YAML para que lo guardes manualmente:\n\n```yaml\n{yaml_content}\n```"
                
        except Exception as e:
            return f"Error al crear la plantilla: {e}"
    
    def _generate_template_name(self, service: str, user_request: str) -> str:
        """Genera un nombre único para la plantilla"""
        # Extraer palabras clave del request
        keywords = []
        if 'basic' in user_request.lower():
            keywords.append('basic')
        if 'advanced' in user_request.lower():
            keywords.append('advanced')
        if 'secure' in user_request.lower():
            keywords.append('secure')
        if 'high-availability' in user_request.lower() or 'ha' in user_request.lower():
            keywords.append('ha')
        
        # Generar nombre
        if keywords:
            return f"{service}-{'-'.join(keywords)}.yaml"
        else:
            return f"{service}-custom.yaml"
    
    def _save_template(self, template_name: str, yaml_content: str) -> bool:
        """Guarda la plantilla en la carpeta templates"""
        try:
            # Obtener la ruta absoluta del directorio templates de forma más robusta
            # Buscar el directorio templates desde la ubicación actual del script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Intentar diferentes rutas posibles, priorizando el directorio templates de nubify
            possible_paths = [
                os.path.join(current_dir, '..', 'templates'),  # src/../templates (nubify/templates)
                os.path.join(os.getcwd(), 'templates'),  # directorio actual/templates
                os.path.join(current_dir, '..', '..', 'templates'),  # src/../../templates
                os.path.join(os.path.dirname(os.getcwd()), 'templates')  # directorio padre/templates
            ]
            
            # Buscar primero el directorio templates que esté dentro de nubify
            templates_dir = None
            for path in possible_paths:
                # Verificar si el directorio existe
                if os.path.exists(path) or os.path.exists(os.path.dirname(path)):
                    # Preferir la ruta que esté DENTRO del directorio nubify (no que solo contenga la palabra)
                    # La ruta ideal es: /path/to/nubify/templates
                    path_normalized = os.path.normpath(path)
                    dir_normalized = os.path.normpath(os.path.dirname(path))
                    
                    # Verificar si la ruta está dentro de nubify (no en el directorio padre)
                    if ('nubify' in path_normalized and 
                        not path_normalized.endswith('/nubify/../templates') and
                        not path_normalized.endswith('/nubify/../../templates')):
                        templates_dir = path
                        break
                    elif templates_dir is None:
                        templates_dir = path  # Guardar como respaldo
            
            # Si no encontramos una ruta válida, usar la primera opción
            if not templates_dir:
                templates_dir = possible_paths[0]
            
            # Crear directorio si no existe
            os.makedirs(templates_dir, exist_ok=True)
            
            template_path = os.path.join(templates_dir, template_name)
            
            # Guardar la plantilla
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Verificar que se guardó correctamente
            if os.path.exists(template_path):
                print(f"✅ Plantilla guardada exitosamente en: {template_path}")
                return True
            else:
                print(f"❌ Error: La plantilla no se guardó en: {template_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error al guardar plantilla: {e}")
            print(f"Directorio templates: {templates_dir}")
            print(f"Nombre de plantilla: {template_name}")
            return False
    
    def _handle_help_command(self, command: str) -> str:
        """Maneja solicitudes de ayuda con comandos"""
        commands_help = get_all_commands()
        
        if command in commands_help:
            cmd_info = commands_help[command]
            return f"""
[bold]Comando: {command}[/bold]
{cmd_info['description']}

[bold]Uso:[/bold]
{cmd_info['usage']}

[bold]Ejemplo:[/bold]
{cmd_info['example']}
"""
        else:
            commands_list = "\n".join([
                f"- {cmd}: {info['description']}" 
                for cmd, info in commands_help.items()
            ])
            
            return f"""
No encontré información específica para el comando "{command}".

[bold]Comandos disponibles en nubify:[/bold]
{commands_list}

¿Te refieres a alguno de estos comandos?
"""
    
    def _handle_troubleshoot(self, error: str) -> str:
        """Maneja solicitudes de resolución de problemas"""
        prompt = f"""
El usuario tiene un problema o error:
"{error}"

Ayúdale a resolverlo proporcionando:
1. Posibles causas del problema
2. Soluciones paso a paso
3. Comandos de nubify que pueden ayudar
4. Prevención para el futuro

Responde de forma clara y práctica en español.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al analizar el problema: {e}"
    
    def _handle_cost_estimation(self, user_request: str) -> str:
        """Maneja solicitudes de estimación de costes"""
        available_templates = get_available_templates()
        templates_text = ", ".join(available_templates)
        
        # Verificar si menciona una plantilla específica
        if 'plantilla' in user_request.lower() or 'template' in user_request.lower():
            return f"""
Para estimar los costes de una plantilla específica, usa el comando:

```bash
nubify estimate-costs <nombre-plantilla>
```

**Ejemplos:**
```bash
nubify estimate-costs ec2-basic
nubify estimate-costs s3-bucket
nubify estimate-costs lambda-function
```

**Con parámetros personalizados:**
```bash
nubify estimate-costs ec2-basic -p InstanceType=t3.small
nubify estimate-costs lambda-function -p MemorySize=512
```

**Plantillas disponibles:**
- {templates_text}

Si quieres crear una nueva plantilla para estimar sus costes, primero créala conmigo y luego usa el comando estimate-costs.
"""
        else:
            return f"""
Para obtener estimaciones de costes en nubify, puedes usar:

**1. Plantillas predefinidas:**
```bash
nubify estimate-costs ec2-basic
nubify estimate-costs s3-bucket
nubify estimate-costs lambda-function
```

**2. Con parámetros personalizados:**
```bash
nubify estimate-costs ec2-basic -p InstanceType=t3.small
nubify estimate-costs lambda-function -p MemorySize=512
```

**3. Ver todas las plantillas disponibles:**
```bash
nubify list-templates
```

**4. Ver detalles de una plantilla:**
```bash
nubify template-details <nombre-plantilla>
```

**Plantillas disponibles:**
- {templates_text}

¿Qué tipo de recurso te gustaría estimar? Puedo ayudarte a crear una plantilla personalizada si necesitas algo específico.
"""
    
    def _handle_recommend(self, user_request: str) -> str:
        """Maneja solicitudes de recomendaciones"""
        supported_services = get_supported_services()
        services_text = ", ".join([s.upper() for s in supported_services])
        
        prompt = f"""
El usuario quiere recomendaciones de servicios AWS. Su solicitud es:
"{user_request}"

IMPORTANTE: Nubify actualmente solo soporta estos servicios para crear plantillas:
- {services_text}

Proporciona recomendaciones basadas en:
- Casos de uso comunes
- Mejores prácticas
- Costes y escalabilidad
- Integración con nubify

Incluye:
1. Servicios recomendados con justificación (puedes recomendar cualquier servicio AWS)
2. Plantillas de nubify relevantes (solo para {services_text})
3. Consideraciones de costes
4. Pasos para implementar

Si recomiendas servicios no soportados por nubify, explica qué son pero indica que no puedes crear plantillas para ellos.

Responde de forma estructurada y práctica en español.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al generar recomendaciones: {e}"
    
    def _generate_response(self, user_input: str) -> str:
        """Genera una respuesta basada en la entrada del usuario"""
        # Analizar intención
        intent_analysis = self._analyze_intent(user_input)
        intent = intent_analysis.get("intent", "GENERAL_QUESTION")
        extracted_info = intent_analysis.get("extracted_info", {})
        
        # Manejar según la intención
        if intent == "EXPLAIN_SERVICE":
            service = extracted_info.get("service", "")
            if service:
                return self._handle_explain_service(service)
            else:
                # Extraer servicio del texto del usuario
                prompt = f"Extrae el nombre del servicio AWS de: '{user_input}'"
                try:
                    response = self.model.generate_content(prompt)
                    service = response.text.strip()
                    return self._handle_explain_service(service)
                except:
                    return "¿Qué servicio AWS te gustaría que te explique?"
        
        elif intent == "CREATE_TEMPLATE":
            return self._handle_create_template(user_input)
        
        elif intent == "HELP_COMMAND":
            command = extracted_info.get("command", "")
            if command:
                return self._handle_help_command(command)
            else:
                return self._handle_help_command("")
        
        elif intent == "TROUBLESHOOT":
            error = extracted_info.get("error", user_input)
            return self._handle_troubleshoot(error)
        
        elif intent == "RECOMMEND":
            return self._handle_recommend(user_input)
        
        elif intent == "COST_ESTIMATION":
            return self._handle_cost_estimation(user_input)
        
        else:
            # Pregunta general
            system_prompt = self._get_system_prompt()
            templates_context = self._get_templates_context()
            
            full_prompt = f"""
{system_prompt}

CONTEXTO DE PLANTILLAS:
{templates_context}

HISTORIAL DE CONVERSACIÓN:
{chr(10).join([f"Usuario: {msg['user']}\nBot: {msg['bot']}" for msg in self.conversation_history[-5:]])}

Usuario: {user_input}

Responde de forma útil y específica para nubify.
"""
            
            try:
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                return f"Error al generar respuesta: {e}"
    
    def start_chat(self):
        """Inicia la sesión de chat interactiva"""
        if not self.model:
            console.print("[red]No se pudo inicializar el chatbot[/red]")
            return
        
        supported_services = get_supported_services()
        services_text = ", ".join([s.upper() for s in supported_services])
        
        console.print(Panel.fit(
            f"[bold blue]NubifyBot[/bold blue]\n"
            f"¡Hola! Soy tu asistente para nubify. Puedo ayudarte con:\n"
            f"• Explicar servicios AWS\n"
            f"• Crear plantillas de CloudFormation para {services_text}\n"
            f"• Ayudar con comandos de nubify\n"
            f"• Resolver problemas\n"
            f"• Recomendar servicios\n"
            f"• Estimación de costes\n\n"
            f"Escribe 'salir' para terminar la conversación.",
            title="Chat Iniciado"
        ))
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]Tú[/bold cyan]")
                
                if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
                    console.print("[yellow]¡Hasta luego![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Generar respuesta
                console.print("\n[bold green]NubifyBot[/bold green]")
                response = self._generate_response(user_input)
                
                # Mostrar respuesta
                try:
                    # Intentar renderizar como markdown
                    md = Markdown(response)
                    console.print(md)
                except:
                    # Si falla, mostrar como texto plano
                    console.print(response)
                
                # Guardar en historial
                self.conversation_history.append({
                    "user": user_input,
                    "bot": response
                })
                
                # Limitar historial
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
            except KeyboardInterrupt:
                console.print("\n[yellow]¡Hasta luego![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue
