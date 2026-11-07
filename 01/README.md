# Módulo 01 — práctica de Strands (módulos 5 y 6)

Esta carpeta es la práctica local de los módulos 5 (agentes, tools y sesiones) y 6 (patrones multiagente). El código vive en `src/`. El avance frente al material del curso está en [`docs/progreso.md`](docs/progreso.md).

El contenedor ejecuta una sola línea de [`entrypoint.sh`](entrypoint.sh). Hoy es:

```sh
exec python -u src/sessions/app.py
```

## Activar un ejemplo

1. Deja una sola de estas líneas en `entrypoint.sh`:

```sh
exec python -u src/wordcount/app.py
exec python -u src/stream/app.py
exec python -u src/sessions/app.py
exec python -u src/mcp/app.py
exec python -u src/memory/app.py
```

2. Desde la raíz de `ejercicios`, reconstruye la app. El Dockerfile copia `entrypoint.sh` en la imagen, así que hace falta `--build`:

```powershell
docker compose up --build app
```

`wordcount`, `context` y `multi-agent/as-tool` corren un prompt y el proceso termina. `stream`, `sessions`, `mcp` y `memory` dejan un servidor en el puerto 8000. `skills`, `hooks` y `steering` son bucles de consola. El entrypoint sigue con sesiones; el resto se abre con `docker compose exec -it`. `skills` hay que arrancarlo desde `src/skills`, y `steering` desde `src/steering`, porque `AgentSkills` busca `./skills`. `as-tool` necesita la imagen reconstruida con el extra `web-fetch`. Los pasos están en las fichas de [docs/](docs/).

## Ejemplos

| Ejemplo | Módulo | Tema | Pieza de código |
|---------|--------|------|----------------|
| [wordcount](docs/wordcount.md) | 5 | Agente, tool declarativa y tools de archivo y shell | `letter_counter`, `Agent(...)` y `agent(prompt)` en `src/wordcount/app.py` |
| [stream](docs/stream.md) | 5 | Streaming HTTP y callback de tokens y tools | `stream_response` y `custom_callback_handler` en `src/stream/app.py` |
| [sessions](docs/sessions.md) | 5 | Memoria de la conversación entre peticiones | `get_session_manager` y `session_manager=` en `src/sessions/app.py` |
| [mcp](docs/mcp.md) | 5 | Tools externas por MCP (stdio y SSE) | `mcp_client`, `playwright_mcp_client` y `tools=[...]` en `src/mcp/app.py` |
| [memory](docs/memory.md) | 5 | Memoria de largo plazo y clasificador de reembolso | `FileMemoryStore`, `MemoryManager` y `classify_refund` en `src/memory/` |
| [skills](docs/skills.md) | 5 | Skills en markdown y tools de atención al cliente | `AgentSkills`, `process_refund` y el bucle `input` en `src/skills/app.py` |
| [hooks](docs/hooks.md) | 5 | Aprobación antes de borrar un archivo | `DeleteApprovalHook.check_delete` y el bucle de `interruptResponse` en `src/hooks/app.py` |
| [steering](docs/steering.md) | 5 | Orden obligatorio del reembolso y revisión del tono | `RefundWorkflowHandler.steer_before_tool` y `ToneGuardrailHandler.steer_after_model` en `src/steering/` |
| [context](docs/context.md) | 5 | Hora inyectada en el contexto, historial y métricas | `ContextInjector` y `result.metrics` en `src/context/app.py` |
| [as-tool](docs/as-tool.md) | 6 | Un agente usa a otro como tool | `writer` con `tools=[researcher]` en `src/multi-agent/as-tool/app.py` |

`src/multi-agent/agent-swarms` y `src/multi-agent/graph-workflow` existen y no tienen archivos. Graph, Swarm, Workflow y A2A siguen sin código. El despliegue tampoco está empezado. El detalle está en [`docs/progreso.md`](docs/progreso.md).
