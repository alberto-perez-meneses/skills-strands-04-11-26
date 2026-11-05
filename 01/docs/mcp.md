# mcp

El agente del endpoint `/stream` recibe tools de dos servidores MCP.

Código: [`src/mcp/app.py`](../src/mcp/app.py).

## Descripción

El agente responde por streaming y, para hacerlo, puede usar tools que no están escritas en este archivo: las publica un servidor MCP de documentación de AWS y otro de Playwright.

## Temas

- MCP: un protocolo para que el agente descubra y llame tools de otro proceso.
- Transporte stdio: el cliente arranca el servidor como subproceso (`uvx`).
- Transporte SSE: el cliente se conecta a un servidor que ya está corriendo (Playwright en el compose).
- El `Agent` recibe clientes MCP en `tools`; el SDK incorpora las tools de esos servidores.

## Pieza de código

`mcp_client` arranca, cuando hace falta, el servidor de documentación de AWS. El comando es `uvx` y el paquete va en `args`:

```19:24:01/src/mcp/app.py
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
))
```

`playwright_mcp_client` no lanza un proceso. Abre una conexión SSE al servicio `playwright-mcp` del compose:

```26:26:01/src/mcp/app.py
playwright_mcp_client = MCPClient(lambda: sse_client("http://playwright-mcp:8931/sse"))
```

La unión con el agente está en la lista `tools` de `stream_response`. Ahí no hay funciones `@tool` de este archivo: hay dos clientes.

```52:54:01/src/mcp/app.py
        agent =  Agent(model=model,
        tools=[mcp_client, playwright_mcp_client],
        callback_handler=custom_callback_handler)
```

## Qué usa

- Modelo `llama3.1` en Ollama.
- `POST /stream` con cuerpo `{"prompt": "..."}`.
- Cliente MCP por stdio: `uvx awslabs.aws-documentation-mcp-server@latest`. La primera llamada descarga ese servidor y puede tardar. Hace falta red de salida desde el contenedor `app`.
- Cliente MCP por SSE: `http://playwright-mcp:8931/sse`. Ese servicio ya está en el compose (`playwright-mcp`, Chromium headless, puerto 8931).
- El callback imprime `MODEL OUTPUT` y `USING TOOL` en los logs.

El servidor de la app escucha en `0.0.0.0:8000`.

## Activar

En [`entrypoint.sh`](../entrypoint.sh):

```sh
python src/mcp/app.py
```

Desde la raíz de `ejercicios`. Conviene levantar también Playwright, por si el compose anterior no lo dejó en marcha:

```powershell
docker compose up --build app playwright-mcp
```

## Probar

Documentación de AWS:

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Busca en la documentacion de AWS que es Amazon S3 y resume en dos frases.\"}"
```

Navegador (Playwright):

```powershell
curl.exe -N -X POST http://localhost:8000/stream -H "Content-Type: application/json" -d "{\"prompt\":\"Abre https://example.com y dime el titulo de la pagina.\"}"
```

En los logs de `app` debe aparecer el nombre de la tool MCP que el agente eligió. Si la primera petición al servidor de documentación de AWS falla por tiempo, repítela cuando `uvx` haya terminado la descarga.
