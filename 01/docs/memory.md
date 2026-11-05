# memory

Memoria de largo plazo y un clasificador de reembolsos antes de que hable el agente.

Código: [`src/memory/app.py`](../src/memory/app.py) y [`src/memory/clasify_refund.py`](../src/memory/clasify_refund.py).

## Descripción

Al arrancar se guarda un documento de preferencias. En cada `POST /stream`, otro modelo decide si el mensaje pide un reembolso y el agente de chat responde con esa decisión y con lo que encuentre en el almacén.

## Temas

- Memoria de largo plazo: `FileMemoryStore` guarda un documento y `MemoryManager` se lo da al agente. En los logs aparece la tool `search_memory`.
- Distinta de la sesión de [`sessions`](sessions.md): la sesión guarda el historial del chat; este almacén es un documento que el agente busca.
- Clasificador previo al agente: `classify_refund` no es una tool de Strands. Su resultado entra en el prompt.
- Umbral: si la probabilidad `noul` queda por debajo de 0.80, el intent es `other`. Una corrida devolvió `noul` 0.64.

## Pieza de código

Al arrancar, `add_memory` escribe un markdown en el store `agent-memory`. El log muestra la clave `travel-preferences.md`:

```19:24:01/src/memory/app.py
store = FileMemoryStore(name="agent-memory")

async def add_memory():
    key = await store.add("# Travel preferences\n- Prefers aisle seats"
    )
    print(f"Memory added with key: {key}")
```

`classify_refund` pregunta a Ollama si el mensaje es un reembolso. El modelo del clasificador es `DECIDER_MODEL` (`d1-omni:latest`) y el corte es `DECIDER_THRESHOLD` (0.80):

```47:68:01/src/memory/clasify_refund.py
    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.post(
            f"{OLLAMA_HOST}/v1/systemone",
            json=payload
        )

        response.raise_for_status()

        result = response.json()

    answer = result["answers"]["refund_request"]
    print(answer)

    probability = float(answer["noul"])

    return {
        "is_refund_request": probability >= DECIDER_THRESHOLD,
        "probability": probability,
        "threshold": DECIDER_THRESHOLD,
        "model": result.get("model", DECIDER_MODEL),
        "latency_ms": result.get("latency_ms")
    }
```

`get_decision_context` convierte esa probabilidad en `refund_request` u `other`. `stream` la pega en el prompt, con instrucciones para reconocer el reembolso y no darlo por procesado:

```52:67:01/src/memory/app.py
    enriched_prompt = f"""
    Analiza el siguiente mensaje del usuario y responde de manera
    natural, amable y profesional.

    MENSAJE DEL USUARIO:
    {request.prompt}

    RESULTADO DEL CLASIFICADOR:
    {decision}

    INSTRUCCIONES:
    - Utiliza la clasificación como contexto adicional.
    - No inventes información sobre pedidos o transacciones.
    - Si el usuario solicita un reembolso, reconoce su solicitud.
    - No confirmes que un reembolso ha sido autorizado o procesado.
    - Si la clasificación no es concluyente, solicita aclaraciones.
```

El agente de esa petición recibe el almacén:

```70:74:01/src/memory/app.py
    async def generate():
        agent =  Agent(model=model,
        memory_manager=MemoryManager(stores=[store]),
        tools=[],
        callback_handler=custom_callback_handler)
```

```87:98:01/src/memory/app.py
async def get_decision_context(message: str):
    decision = await classify_refund(message)

    return {
        "intent": (
            "refund_request"
            if decision["is_refund_request"]
            else "other"
        ),
        "confidence": decision["probability"],
        "model": decision["model"]
    }
```

El agente de chat sigue siendo `llama3.1`. La lista `tools` va vacía: la búsqueda de memoria llega por `memory_manager`.

## Qué usa

- Chat: `llama3.1` en Ollama (`OLLAMA_HOST`).
- Clasificador: `d1-omni:latest` en `POST {OLLAMA_HOST}/v1/systemone`. `ollama-pull` descarga ese modelo junto con `llama3.1`.
- `POST /stream` con cuerpo `{"prompt": "..."}`. La respuesta es `text/event-stream`.
- El callback imprime `MODEL OUTPUT` y `USING TOOL` en los logs.

El servidor escucha en `0.0.0.0:8000`. El archivo del store vive dentro del contenedor. Recrear el contenedor lo borra; al volver a arrancar, `start_server` llama otra vez a `add_memory`.

## Activar

`ollama-pull` baja `d1-omni:latest` al levantar el compose. Si el volumen de Ollama se creó antes de ese cambio, bájalo a mano desde la raíz de `ejercicios`:

```powershell
docker compose exec ollama ollama pull d1-omni
```

En [`entrypoint.sh`](../entrypoint.sh):

```sh
python src/memory/app.py
```

```powershell
docker compose up --build app
```

## Probar

Cuando el log muestre `Memory added with key: travel-preferences.md` y que Uvicorn escucha:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Quiero que me devuelvan el dinero de mi pedido.\"}"
```

En los logs de `app` sale el dict del clasificador (`noul`) y, si el agente consulta el almacén, `USING TOOL: search_memory`. La respuesta reconoce la solicitud y no confirma que el reembolso ya esté procesado: eso lo piden las instrucciones del prompt enriquecido.
