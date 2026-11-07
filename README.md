# Ejercicios de Strands

Práctica local de los módulos 5 y 6 (Strands) con Docker y Ollama. El código de los ejemplos está en [`01/`](01/). El detalle de cada ejemplo y el avance del curso están en [`01/docs/progreso.md`](01/docs/progreso.md).

## Prerrequisitos

- Docker Desktop en ejecución.
- GPU disponible para el servicio `ollama`. [`docker-compose.yml`](docker-compose.yml) pide `gpus: all`.

## Levantar el entorno

Desde esta carpeta, en PowerShell:

```powershell
docker compose up --build
```

Eso arranca cuatro servicios:

| Servicio | Qué hace | Puerto |
|----------|----------|--------|
| `ollama` | Sirve el modelo | 11434 |
| `ollama-pull` | Descarga `llama3.1` y `d1-omni:latest`, y termina | — |
| `app` | Ejecuta el ejemplo activo de `01/` | 8000 |
| `playwright-mcp` | Navegador headless para el ejemplo MCP | 8931 |

La app recibe `OLLAMA_HOST=http://ollama:11434`. El ejemplo que corre lo decide [`01/entrypoint.sh`](01/entrypoint.sh). Hoy es `exec python -u src/sessions/app.py`.

`skills`, `hooks` y `steering` leen la consola con `input()`. `context` y `multi-agent/as-tool` son scripts de un solo turno. Todos se abren con `docker compose exec -it` sobre el contenedor que ya está en marcha. El detalle está en [`01/README.md`](01/README.md).
