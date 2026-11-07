# context

Un agente de un solo turno que recibe la hora UTC en cada llamada y, al terminar, imprime el historial, los ciclos y los tokens.

Código: [`src/context/app.py`](../src/context/app.py).

## Descripción

No hay servidor ni bucle de consola. El script arma el agente, le manda un mensaje fijo de un cliente y muestra qué quedó en `agent.messages` y en las métricas del resultado.

## Temas

- `ContextInjector`: un plugin que añade texto al contexto en cada invocación. Aquí es la hora UTC dentro de `<now>`.
- Historial en memoria: después de la llamada, `agent.messages` tiene el turno de usuario y el de asistente.
- Métricas: `result.metrics` expone ciclos y tokens. Este script los imprime; no corta la ejecución por un tope.

El agente no tiene tools de pedidos. El mensaje nombra al cliente `C-1001`, y el modelo solo puede responder con lo que trae el prompt y la hora inyectada.

## Pieza de código

El plugin es una lambda. Cada vez que el agente corre, esa función devuelve la marca de tiempo:

```8:17:01/src/context/app.py
agent = Agent(
    model=OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",),
    plugins=[
        ContextInjector(
            lambda context: f"<now>{datetime.now(timezone.utc).isoformat()}</now>"
        ),
    ],
)

result = agent("Hi, I'm customer C-1001. Can you check on my recent orders?")
```

Al volver, el script recorre los mensajes e imprime ciclos y tokens:

```19:31:01/src/context/app.py
print(f"Total messages: {len(agent.messages)}")

for msg in agent.messages:
    role = msg["role"]
    for block in msg.get("content", []):
        if "text" in block:
            print(f"{role}: {block['text'][:100]}")
        elif "toolUse" in block:
            tu = block["toolUse"]
            print(f"tool call: {tu['name']}({json.dumps(tu.get('input', {}))})")

print(f"Cycles: {result.metrics.get_summary()['total_cycles']}")
print(f"Tokens: {result.metrics.accumulated_usage['totalTokens']}")
```

## Qué usa

- Modelo `llama3.1` en Ollama (`OLLAMA_HOST`).
- Un prompt fijo. No abre el puerto 8000.
- El proceso termina cuando imprime las métricas.

## Activar

El entrypoint sigue en sesiones. Desde la raíz de `ejercicios`, con la app ya en marcha:

```powershell
docker compose exec -it app python -u src/context/app.py
```

## Probar

Una corrida en el contenedor imprimió `Total messages: 2`, `Cycles: 1` y `Tokens: 98`. El asistente pidió datos de la cuenta: no hay una tool que consulte pedidos. Si aparece una llamada a tool, el bucle la imprime como `tool call:`.
