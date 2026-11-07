# Avance — módulos 5 y 6

Estado de la práctica en `01/src` frente al material del curso. El despliegue no está empezado: todo corre en local con Docker Compose. El compose descarga `llama3.1` y `d1-omni:latest`.

Leyenda: **hecho** es código que ya se puede ejecutar; **parcial** cubre una parte del ejercicio; **pendiente** no tiene código en esta carpeta.

## Módulo 5 — agentes, tools y sesiones

| Ejercicio | Tema | Estado | Pieza de código |
|-----------|------|--------|----------------|
| 5.1 Primer agente con una tool | El bucle del agente elige tools y responde sin un orquestador aparte. | Hecho como práctica | [`wordcount`](wordcount.md): `Agent(model, tools=[letter_counter, file_editor, shell])` y la llamada `agent(prompt)`. |
| 5.2 Tool con validación y errores | Una tool rechaza entradas inválidas y el agente sigue pudiendo responder. | Parcial | [`hooks`](hooks.md): `list_files`, `read_file` y `delete_file` devuelven un texto si la ruta no existe. `letter_counter` en [`wordcount`](wordcount.md) lanza `ValueError` si `letter` no es un carácter. Siguen sin tests y sin una tool de búsqueda. |
| 5.3 Cambiar de proveedor | El mismo agente corre con otro modelo cambiando solo la configuración. | Pendiente | El chat usa `OllamaModel(..., model_id="llama3.1")` en cada `app.py`, también en `src/memory/app.py`. No hay una segunda configuración del mismo agente ni una tabla de latencia o coste. |
| 5.4 Salida estructurada | La respuesta se valida contra un esquema antes de usarla desde código. | Pendiente | Las rutas devuelven texto (`stream_async` / `str`). No hay modelo Pydantic de salida ni `structured_output`. |
| 5.5 Sesiones y contexto | Controlar qué recuerda el agente entre turnos. | Hecho como práctica | [`sessions`](sessions.md): `get_session_manager` (`SnapshotSessionManager` + `LocalFileStorage`) pasado como `session_manager` al `Agent`. |
| 5.6 Límites y coste | Cortar el agente por iteraciones, tiempo o tokens, y dejar el corte registrado. | Pendiente | [`context`](context.md) imprime `total_cycles` y `totalTokens`. No hay tope ni corte. |
| Streaming por HTTP | Entregar la respuesta token a token y observar las tools en la consola. | Hecho (extra del material) | [`stream`](stream.md): `stream_response` recorre `agent.stream_async` y `custom_callback_handler` imprime `data` y `current_tool_use`. |
| Tools MCP | Usar tools definidas en otro proceso, por stdio o por SSE. | Hecho (extra del material) | [`mcp`](mcp.md): `mcp_client` (stdio + `uvx`) y `playwright_mcp_client` (SSE), pasados en `tools` del `Agent`. |
| Memoria y clasificador | Guardar un documento que el agente busca, y clasificar el mensaje antes de responder. | Hecho como práctica | [`memory`](memory.md): `FileMemoryStore` + `MemoryManager` en `app.py`; `classify_refund` llama a `/v1/systemone` y el resultado entra en el prompt. |
| Skills | Cargar guías en markdown y dejar que el agente las active junto con tools de dominio. | Hecho como práctica | [`skills`](skills.md): `AgentSkills(skills=["./skills"])` y las tools `lookup_customer`, `get_order_history` y `process_refund`. |
| Hooks | Pedir confirmación antes de una tool concreta y reanudar con la respuesta. | Hecho como práctica | [`hooks`](hooks.md): `DeleteApprovalHook.check_delete` en `BeforeToolCallEvent` y el bucle de `interruptResponse`. |
| Steering | Obligar el orden de un reembolso y revisar el tono de la respuesta sin dejarlo solo al prompt. | Hecho como práctica | [`steering`](steering.md): `RefundWorkflowHandler` (`Guide` / `Proceed` antes de `process_refund`) y `ToneGuardrailHandler.steer_after_model`. |
| Contexto inyectado | Añadir datos al contexto en cada llamada y leer el historial y las métricas al terminar. | Hecho como práctica | [`context`](context.md): `ContextInjector` con la hora UTC, y el recorrido de `agent.messages` más `result.metrics`. |

Checklist del módulo 5:

- [x] Un agente corre con tools y modelo local.
- [ ] Las tools cubren el caso de listar, leer y buscar en un workspace, con tests.
- [ ] Cambiar de modelo se hace solo por configuración y queda comparado.
- [ ] La salida estructurada se valida antes de aceptarla.
- [x] Una sesión recuerda el turno anterior y otra sesión no.
- [ ] El agente tiene presupuesto y límite de iteraciones.
- [ ] Despliegue.

## Módulo 6 — Graph, Swarm, Workflow y A2A

Hay un patrón de agente como tool en [`as-tool`](as-tool.md). `src/multi-agent/agent-swarms` y `src/multi-agent/graph-workflow` están vacías. No hay un grafo, un enjambre, un workflow ni un servidor A2A. El ejemplo [`mcp`](mcp.md) conecta tools externas al mismo agente; el ejercicio 6.4 pide exponer un agente como servicio con contrato.

| Ejercicio | Tema | Estado | Pieza de código |
|-----------|------|--------|----------------|
| 6.1 Graph | Orden fijo entre pasos, con una arista que vuelve atrás si la validación falla, y un máximo de ejecuciones. | Pendiente | La carpeta `src/multi-agent/graph-workflow` está vacía. |
| 6.2 Swarm | Varios agentes se pasan el control, con un tope de traspasos. | Pendiente | La carpeta `src/multi-agent/agent-swarms` está vacía. |
| Agente como tool | Un agente especialista entra en `tools` de otro y este lo invoca por nombre. | Hecho como práctica | [`as-tool`](as-tool.md): `researcher` con `web_fetch` y `writer` con `tools=[researcher]`. |
| 6.3 Workflow | Cada paso tiene estado (`pendiente`, `en_curso`, `hecho`, `fallido`) y se puede reanudar desde el que falló. | Pendiente | Sin código en `01/src`. |
| 6.4 A2A | Un agente se expone como servicio con contrato; una petición fuera de contrato se rechaza. | Pendiente | Sin código en `01/src`. [`mcp`](mcp.md) conecta tools externas al mismo agente; no publica un agente por A2A. |
| 6.5 Mismo caso, dos herramientas | El triaje también en LangGraph, comparado con líneas de código, control del flujo y medidas de latencia o coste. | Pendiente | Sin código en `01/src`. |

Checklist del módulo 6:

- [ ] Graph, Swarm y Workflow están implementados sobre el mismo caso.
- [ ] Cada patrón tiene un límite de pasos o de traspasos.
- [ ] Un workflow se reanuda desde el paso fallido.
- [ ] Un servicio A2A rechaza una entrada fuera de contrato.
- [ ] La comparación con LangGraph usa medidas, no solo impresión.
- [ ] Despliegue.
