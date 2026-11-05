# sessions

La misma API de streaming, con memoria por `session_id`. Es el ejemplo que [`entrypoint.sh`](../entrypoint.sh) ejecuta ahora (`exec python -u src/sessions/app.py`).

Código: [`src/sessions/app.py`](../src/sessions/app.py).

## Descripción

La misma API de streaming recuerda lo dicho en turnos anteriores cuando el cliente repite el mismo `session_id`.

## Temas

- Sesión: el historial de la conversación vive fuera del proceso de una sola petición.
- Identificador de sesión: lo elige quien llama, en el cuerpo JSON.
- Almacén local: cada sesión se guarda como snapshot en una carpeta del contenedor.
- Agente sin tools: aquí el tema es la memoria, no las herramientas.

## Pieza de código

El contrato HTTP añade el id. Sin ese campo, FastAPI rechaza el cuerpo:

```18:20:01/src/sessions/app.py
class PromptRequest(BaseModel):
    prompt: str
    session_id: str
```

`get_session_manager` abre (o crea) el snapshot de ese id en `./sessions/`:

```28:33:01/src/sessions/app.py
def get_session_manager(session_id: str):
# Create a snapshot session manager with a unique session ID
    return SnapshotSessionManager(
        session_id=session_id,
        storage=LocalFileStorage("./sessions/"),
    )
```

Dentro de cada `POST`, `generate` carga ese manager y se lo pasa al `Agent`. La lista de tools va vacía:

```45:50:01/src/sessions/app.py
    async def generate():
        session_manager = get_session_manager(request.session_id)
        agent =  Agent(model=model,
        session_manager=session_manager,
        tools=[],
        callback_handler=custom_callback_handler)
```

Dos llamadas con el mismo `session_id` leen y escriben el mismo snapshot. Otro id apunta a otro archivo bajo `./sessions/`.

## Qué usa

- Modelo `llama3.1` en Ollama.
- `POST /stream` con cuerpo `{"prompt": "...", "session_id": "..."}`.
- `SnapshotSessionManager` guarda la conversación en `./sessions/` dentro del contenedor (`LocalFileStorage`).
- El agente se crea sin tools. El callback imprime `MODEL OUTPUT` y `USING TOOL` en los logs.
- Dos peticiones con el mismo `session_id` comparten historial. Otro `session_id` empieza una conversación nueva.

El servidor escucha en `0.0.0.0:8000`. La carpeta `./sessions/` vive en el sistema de archivos del contenedor. Recrear el contenedor borra esas sesiones.

## Activar

En [`entrypoint.sh`](../entrypoint.sh):

```sh
python src/sessions/app.py
```

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
```

## Probar

Primera petición. Elige un id y dile al agente un dato concreto:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Me llamo Alberto.\",\"session_id\":\"demo-1\"}"
```

Segunda petición, mismo id. La respuesta debe usar el nombre del turno anterior:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Como me llamo?\",\"session_id\":\"demo-1\"}"
```

Con otro id, el agente no tiene ese dato:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Como me llamo?\",\"session_id\":\"demo-2\"}"
```
