# as-tool

Dos agentes en un solo proceso. El que escribe recibe al que investiga como si fuera una tool.

Código: [`src/multi-agent/as-tool/app.py`](../src/multi-agent/as-tool/app.py).

## Descripción

`researcher` busca datos en la web. `writer` no busca por su cuenta: llama a `researcher` y con eso redacta un resumen de tres frases sobre el repositorio de FastAPI. El script hace una sola llamada y termina.

## Temas

- Agente como tool: pasar un `Agent` en la lista `tools` de otro agente. El escritor dispara al investigador por nombre.
- Tool de vendimia `web_fetch`: descarga una página y la convierte a texto. Entra en el extra `strands-agents[web-fetch]` de [`requirements.txt`](../requirements.txt).
- Un modelo compartido: los dos agentes usan el mismo `OllamaModel`.

Esto no es un Graph, un Swarm ni un servicio A2A. El orden lo decide el escritor al invocar la tool. Las carpetas `src/multi-agent/agent-swarms` y `src/multi-agent/graph-workflow` existen y todavía no tienen archivos.

## Pieza de código

`researcher` tiene nombre y la tool de web. `writer` recibe ese objeto en `tools`:

```6:21:01/src/multi-agent/as-tool/app.py
model = OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",)
researcher = Agent(
    model=model,
    name="researcher",
    system_prompt="You are a research specialist. Find factual information.",
    tools=[web_fetch],
)

writer = Agent(
    model=model,
    name="writer",
    system_prompt="You are a technical writer. Use the researcher to gather facts.",
    tools=[researcher],  # Pass agent directly as a tool
)

writer("Research the FastAPI GitHub repo and write a 3-sentence summary.")
```

## Qué usa

- Modelo `llama3.1` en Ollama.
- Salida a internet desde el contenedor `app`, porque `web_fetch` descarga la página.
- No abre el puerto 8000. El proceso termina al acabar el resumen.

## Activar

Hay que reconstruir la imagen después de añadir `strands-agents[web-fetch]` a `requirements.txt`. Sin ese extra, el import de `web_fetch` falla por falta de `beautifulsoup4`.

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
docker compose exec -it app python -u src/multi-agent/as-tool/app.py
```

## Probar

En una corrida el log mostró primero `Tool #1: researcher` y, dentro de esa llamada, `Tool #1: web_fetch`. Después el escritor imprimió un resumen de tres frases sobre FastAPI. Si `web_fetch` no puede salir a la red, la tool devuelve el error y el resumen no tiene datos de la página.
