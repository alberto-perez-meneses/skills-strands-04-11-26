# graph-workflow

Un grafo de cuatro agentes. La investigación se abre en dos ramas y el informe espera a las dos.

Código: [`src/multi-agent/graph-workflow/app.py`](../src/multi-agent/graph-workflow/app.py) y [`src/multi-agent/graph-workflow/web_search.py`](../src/multi-agent/graph-workflow/web_search.py).

## Descripción

`researcher` consulta la web. Desde ese nodo salen dos aristas, hacia `analyst` y hacia `summarizer`, así que esas dos ramas corren en paralelo. `report_writer` tiene una arista desde cada rama y redacta el informe cuando ambas han terminado. El caso es el impacto de la IA en la salud. El script lanza el grafo una vez y termina.

## Temas

- `GraphBuilder`: nodos con nombre, aristas fijas y un timeout de ejecución.
- Fan-out y join: dos aristas salen de `research` y dos llegan a `report`.
- Tools solo en el primer nodo: `web_fetch` y `web_search`. Los otros tres agentes no tienen tools.
- Búsqueda con Tavily: `web_search` llama a `TavilyClient.search` y devuelve el JSON.

No hay una arista que vuelva atrás si un paso falla, ni un tope de ejecuciones del grafo. El único corte es `set_execution_timeout(600)`.

## Pieza de código

Los cuatro agentes comparten el mismo `OllamaModel`. Solo el investigador recibe tools:

```12:35:01/src/multi-agent/graph-workflow/app.py
researcher = Agent(
    model=model,
    name="researcher",
    system_prompt="Gather comprehensive information from the web.",
    tools=[web_fetch, web_search],
)

analyst = Agent(
    model=model,
    name="analyst",
    system_prompt="Identify patterns, trends, and key insights from research.",
)

summarizer = Agent(
    model=model,
    name="summarizer",
    system_prompt="Condense raw research into concise key points.",
)

report_writer = Agent(
    model=model,
    name="report_writer",
    system_prompt="Synthesize analysis and summaries into a final report.",
)
```

El grafo fija el orden y el tiempo máximo. La llamada de la última línea arranca el caso:

```37:51:01/src/multi-agent/graph-workflow/app.py
builder = GraphBuilder()
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(summarizer, "summarize")
builder.add_node(report_writer, "report")

builder.add_edge("research", "analysis")
builder.add_edge("research", "summarize")   # analyst + summarizer run in parallel
builder.add_edge("analysis", "report")
builder.add_edge("summarize", "report")      # report waits for both

builder.set_execution_timeout(600)
graph = builder.build()

result = graph("Research the impact of AI on healthcare")
```

`web_search` declara `max_results` y `topic`. La llamada a Tavily no usa esos argumentos: siempre pide `search_depth="advanced"`, `time_range="month"` e `include_raw_content="markdown"`.

```23:28:01/src/multi-agent/graph-workflow/web_search.py
    response = client.search(
        query=query,
        search_depth="advanced",
        time_range="month",
        include_raw_content="markdown"
        )
```

El cliente de Tavily se crea al importar el módulo, con el valor de `TAVILY_API_KEY` en ese momento. El mensaje de configuración solo se devuelve si la tool llega a ejecutarse sin la variable.

## Qué usa

- Modelo `llama3.1` en Ollama.
- `TAVILY_API_KEY`, pasada al servicio `app` desde el entorno de Compose. El ejemplo está en [`.env.example`](../../.env.example).
- Salida a internet: `web_fetch` y la API de Tavily.
- No abre el puerto 8000. La llamada a `graph(...)` está en el cuerpo del módulo, así que importar `app.py` también lanza la investigación.

## Activar

La imagen tiene que incluir `tavily-python` y `strands-agents[web-fetch]` de [`requirements.txt`](../requirements.txt). Desde la raíz de `ejercicios`, con la clave en el entorno:

```powershell
docker compose up --build app
docker compose exec -it app python -u src/multi-agent/graph-workflow/app.py
```

Python añade el directorio del script a `sys.path`, y así `from web_search import web_search` resuelve el archivo vecino.

## Qué esperar

En los logs aparece primero el nodo `research` y, dentro, llamadas a `web_search` o `web_fetch`. Después corren `analysis` y `summarize`, y al final `report`. Si falta la clave, la tool de búsqueda devuelve el texto de configuración cuando llega a ejecutarse, o el proceso falla al construir `TavilyClient` durante el import. Si el grafo supera 600 segundos, la ejecución se corta por el timeout.
