# Avance — módulos 5 y 6

Actualizado el 9 de noviembre de 2026.

La práctica de Strands vive en `01/src`. El curso usa estos ejemplos, y cada uno tiene código que se puede ejecutar en local con Docker Compose. El compose descarga `llama3.1` y `d1-omni:latest`. El servicio `app` recibe `TAVILY_API_KEY` para el grafo. El entrypoint activo es `src/sessions/app.py`.

## Módulo 5 — agentes, tools y sesiones

| Ejemplo | Qué hace el código | Estado | Dónde |
|---------|--------------------|--------|-------|
| wordcount | Un agente cuenta una letra, escribe el resultado y lo muestra con `shell`. `letter_counter` rechaza una letra que no sea un carácter. | Hecho | [`wordcount`](wordcount.md): `src/wordcount/app/app.py` |
| wordcount evals | La evaluación pide el conteo de erres en `strawberry`, comprueba el orden `letter_counter` → `file_editor` → `shell` y que la salida contenga `3`. | Hecho | `src/wordcount/evals/test.py` |
| stream | La respuesta sale token a token por HTTP y el callback imprime tokens y tools. | Hecho | [`stream`](stream.md): `src/stream/app.py` |
| sessions | La conversación se guarda entre peticiones con `SnapshotSessionManager` y `LocalFileStorage`. | Hecho | [`sessions`](sessions.md): `src/sessions/app.py` |
| mcp | El mismo agente usa tools de otro proceso, por stdio (`uvx`) y por SSE (Playwright). | Hecho | [`mcp`](mcp.md): `src/mcp/app.py` |
| memory | Un documento queda en `FileMemoryStore` y el agente lo busca. `classify_refund` clasifica el mensaje antes de responder. | Hecho | [`memory`](memory.md): `src/memory/` |
| skills | El agente carga guías en markdown y las usa junto con `lookup_customer`, `get_order_history` y `process_refund`. | Hecho | [`skills`](skills.md): `src/skills/` |
| hooks | Antes de borrar un archivo el hook pide confirmación y el bucle reanuda con `interruptResponse`. | Hecho | [`hooks`](hooks.md): `src/hooks/app.py` |
| steering | El reembolso sigue un orden fijo (`Guide` / `Proceed`) y otro handler revisa el tono de la respuesta. | Hecho | [`steering`](steering.md): `src/steering/` |
| context | Cada llamada recibe la hora UTC. Al terminar se imprimen `agent.messages` y `result.metrics`. | Hecho | [`context`](context.md): `src/context/app.py` |

## Módulo 6 — coordinación entre agentes

| Ejemplo | Qué hace el código | Estado | Dónde |
|---------|--------------------|--------|-------|
| as-tool | `writer` llama a `researcher` como tool. El investigador usa `web_fetch`. | Hecho | [`as-tool`](as-tool.md): `src/multi-agent/as-tool/app.py` |
| graph | Cuatro nodos con orden fijo. `research` se abre en paralelo hacia `analysis` y `summarize`, y `report` espera a las dos. Timeout de 600 segundos. La búsqueda usa Tavily. | Hecho | [`graph-workflow`](graph-workflow.md): `src/multi-agent/graph-workflow/` |
| swarm | `instructional_designer`, `content_creator` y `html_developer` se pasan un microcurso. Topes: 5 traspasos, 6 iteraciones, 300 segundos el enjambre y 120 por nodo. | Hecho | [`agent-swarms`](agent-swarms.md): `src/multi-agent/agent-swarms/app.py` |

## Cómo se abre cada ejemplo

`stream`, `sessions`, `mcp` y `memory` dejan un servidor en el puerto 8000. El resto corre un caso y el proceso termina, o lee la consola (`skills`, `hooks`, `steering`). La ficha de cada ejemplo tiene el comando. Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
docker compose exec -it app python -u src/multi-agent/graph-workflow/app.py
```
