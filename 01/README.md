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

`wordcount` corre un prompt y el contenedor termina. `stream`, `sessions`, `mcp` y `memory` dejan un servidor en el puerto 8000. `skills`, `hooks` y `steering` son bucles de consola: el entrypoint sigue con sesiones y esos tres se abren con `docker compose exec -it`. `skills` hay que arrancarlo desde `src/skills`, y `steering` desde `src/steering`, porque `AgentSkills` busca `./skills`. Los pasos están en [docs/skills.md](docs/skills.md), [docs/hooks.md](docs/hooks.md) y [docs/steering.md](docs/steering.md).

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

El módulo 6 (Graph, Swarm, Workflow y A2A) todavía no tiene código en `src/`. El despliegue tampoco está empezado. El detalle está en [`docs/progreso.md`](docs/progreso.md).
