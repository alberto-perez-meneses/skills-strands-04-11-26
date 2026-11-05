# stream

API que envía la respuesta del agente token a token.

Código: [`src/stream/app.py`](../src/stream/app.py).

## Descripción

Una API recibe un prompt y va devolviendo el texto del agente a medida que el modelo lo genera, mientras el agente puede llamar a una calculadora o a un pronóstico simulado.

## Temas

- Tools con tipos acotados: `calculator` solo acepta cinco operadores.
- Callback del agente: ver cada fragmento de texto y el nombre de la tool en uso.
- Streaming: `stream_async` produce eventos; la API reenvía los que traen texto.
- Un agente nuevo por petición: esta ruta no guarda la conversación.

## Pieza de código

Las dos tools viven en el mismo archivo. `weather_forecast` no llama a ningún servicio: arma un texto con la ciudad y los días. `calculator` aplica el operador con la tabla `_OPS`:

```36:45:01/src/stream/app.py
@tool
def calculator(a: float, b: float, op: Literal["+", "-", "*", "/", "**"]) -> float:
    """Apply an arithmetic operator to two numbers.

    Args:
        a: Left operand.
        b: Right operand.
        op: One of "+", "-", "*", "/", "**".
    """
    return _OPS[op](a, b)
```

`custom_callback_handler` es el observador. Si el evento trae `data`, imprime el fragmento del modelo. Si trae `current_tool_use` con nombre, imprime qué tool está usando:

```62:67:01/src/stream/app.py
def custom_callback_handler(**kwargs):
    # Process stream data
    if "data" in kwargs:
        print(f"MODEL OUTPUT: {kwargs['data']}")
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\nUSING TOOL: {kwargs['current_tool_use']['name']}")
```

`stream_response` es la pieza HTTP. Crea el `Agent` dentro de la petición, recorre `stream_async` y cede al cliente solo los eventos que tienen `data`:

```70:83:01/src/stream/app.py
@app.post("/stream")
async def stream_response(request: PromptRequest):
    async def generate():
        agent =  Agent(model=model,
        tools=[calculator, weather_forecast],
        callback_handler=custom_callback_handler)
        try:
            async for event in agent.stream_async(request.prompt):
                if "data" in event:
                    yield event["data"]
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")
```

Ese `Agent` recibe modelo, tools y callback. No recibe `session_manager`, así que la siguiente petición empieza de cero.

## Qué usa

- Modelo `llama3.1` en Ollama.
- `POST /stream` con cuerpo `{"prompt": "..."}`.
- La respuesta es `text/plain` y llega por streaming (`agent.stream_async`).
- Tools: `calculator` (`+`, `-`, `*`, `/`, `**`) y `weather_forecast`. El pronóstico devuelve un texto fijo; no consulta un servicio del tiempo.
- Un callback imprime en la consola del contenedor `MODEL OUTPUT` y `USING TOOL`.

El servidor escucha en `0.0.0.0:8000`.

## Activar

En [`entrypoint.sh`](../entrypoint.sh):

```sh
python src/stream/app.py
```

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
```

## Probar

Cuando el log muestre que Uvicorn está escuchando:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Cuanto es 7 * 6?\"}"
```

En los logs de `app` debe aparecer `USING TOOL: calculator` y, en la terminal del `curl`, el texto de la respuesta a medida que llega.

Otro prompt, para la segunda tool:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Pronostico del tiempo en Monterrey para 2 dias\"}"
```
