# agent-swarms

Tres agentes se pasan un microcurso. El enjambre corta por traspasos, por iteraciones y por tiempo.

Código: [`src/multi-agent/agent-swarms/app.py`](../src/multi-agent/agent-swarms/app.py).

## Descripción

`instructional_designer` arma la estructura del curso. `content_creator` redacta los módulos. `html_developer` lo convierte en un HTML y lo guarda con `file_editor` en `curso.html`. El caso es un microcurso de 15 minutos sobre CSS Grid, en español. El punto de entrada es el diseñador. Cada prompt le dice al agente a quién transferir cuando termina su parte.

## Temas

- `Swarm`: una lista de nodos, un `entry_point` y topes de traspaso y de iteración.
- Traspaso por el propio agente: el framework le da la tool de handoff; el system prompt dice cuándo usarla.
- Timeouts: 300 segundos para el enjambre y 120 por nodo.
- Una sola tool de dominio: `file_editor` en el desarrollador HTML. Los otros dos agentes no tienen tools.

## Pieza de código

Los tres agentes comparten `llama3.1`. El tercero es el único que escribe archivos. Su prompt le pide un HTML completo y cerrar guardándolo en `curso.html`.

Los topes van en el constructor. La llamada siguiente es el encargo del curso:

```78:99:01/src/multi-agent/agent-swarms/app.py
course_swarm = Swarm(
    nodes=[designer, creator, developer],
    entry_point=designer,
    max_handoffs=5,
    max_iterations=6,
    execution_timeout=300.0,
    node_timeout=120.0
)

result = course_swarm(
    """
    Crea un microcurso sobre fundamentos de CSS Grid.
    ...
    """
)

print(result)
```

`result = course_swarm(...)` está en el cuerpo del módulo. Importar este archivo también lanza el enjambre.

## Qué usa

- Modelo `llama3.1` en Ollama.
- Tool `file_editor` del SDK, para escribir `curso.html` en el directorio de trabajo del contenedor (`/app`).
- No abre el puerto 8000. No usa Tavily ni `web_fetch`.

## Activar

Desde la raíz de `ejercicios`, con el contenedor ya construido:

```powershell
docker compose up --build app
docker compose exec -it app python -u src/multi-agent/agent-swarms/app.py
```

## Qué esperar

El log muestra el traspaso `instructional_designer` → `content_creator` → `html_developer`. Al terminar, `print(result)` escribe el resultado del enjambre y el proceso acaba. `curso.html` queda en `/app`. No hay un volumen montado para la app, así que el archivo desaparece al recrear el contenedor. Si un nodo se pasa de 120 segundos, o el enjambre de 300, o hay más de 5 traspasos o 6 iteraciones, la ejecución se corta por ese tope.
