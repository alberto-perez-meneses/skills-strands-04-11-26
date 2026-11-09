
from strands import Agent
from strands.multiagent import Swarm
from strands.vended_tools import file_editor

from strands.models.ollama import OllamaModel
import os

model = OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",)

# Agente 1: Diseño instruccional
designer = Agent(
    model=model,
    name="instructional_designer",
    system_prompt="""
    Eres un diseñador instruccional.
    Recibes un tema y diseñas un microcurso.

    Define:
    - Público objetivo
    - Objetivos de aprendizaje
    - Tres módulos
    - Actividades por módulo
    - Evaluación final

    Cuando tengas la estructura lista,
    transfiere el trabajo al content_creator.
    """
)

# Agente 2: Creación de contenido
creator = Agent(
    model=model,
    name="content_creator",
    system_prompt="""
    Eres un especialista en creación de contenido educativo.

    Desarrolla los módulos definidos por el diseñador.

    Incluye:
    - Explicaciones sencillas
    - Ejemplos prácticos
    - Fragmentos de código cuando corresponda
    - Una actividad por módulo

    Cuando termines, transfiere el trabajo
    al html_developer.
    """
)

# Agente 3: Generador HTML
developer = Agent(
    model=model,
    name="html_developer",
    tools=[file_editor],
    system_prompt="""
    Eres un desarrollador frontend especializado
    en plataformas educativas.

    Convierte el contenido recibido en un curso HTML.

    Requisitos:
    - HTML5
    - CSS integrado
    - Diseño responsive
    - Navegación por módulos
    - Preguntas interactivas con JavaScript
    - Retroalimentación al estudiante
    - No utilizar frameworks externos

    Genera un documento HTML completo.

    Cuando termines, entrega el resultado final y guárdalo en un archivo llamado "curso.html".
    """
)

# Crear el Swarm
course_swarm = Swarm(
    nodes=[designer, creator, developer],
    entry_point=designer,
    max_handoffs=5,
    max_iterations=6,
    execution_timeout=300.0,
    node_timeout=120.0
)

# Solicitar un curso
result = course_swarm(
    """
    Crea un microcurso sobre fundamentos de CSS Grid.

    Público: estudiantes principiantes.
    Duración: 15 minutos.
    Formato: HTML interactivo.
    Idioma: español.
    """
)

print(result)
