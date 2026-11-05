# hooks

Agente de archivos por consola. Listar, leer y escribir corren solos. Borrar se detiene y pide un sí en la terminal.

Código: [`src/hooks/app.py`](../src/hooks/app.py).

## Descripción

Le pides al agente que trabaje con archivos del contenedor. Antes de borrar uno, el hook interrumpe la tool y espera `y` o cualquier otra respuesta.

## Temas

- Tools de archivos: listar, leer, escribir y borrar. Si la ruta no existe, listar, leer y borrar devuelven un texto de error.
- Hook `BeforeToolCallEvent`: corre antes de la tool y puede cancelarla.
- Aprobación solo de `delete_file`. Las otras tres tools no pasan por esa pregunta.
- Interrupción: el agente se detiene con `stop_reason == "interrupt"` y el bucle reenvía la respuesta de la persona.

## Pieza de código

`DeleteApprovalHook` se registra en `BeforeToolCallEvent`. Si la tool no es `delete_file`, vuelve sin hacer nada. Si lo es, pide aprobación y cancela la llamada cuando la respuesta no es `y`:

```67:83:01/src/hooks/app.py
class DeleteApprovalHook(HookProvider):
    """Only intercepts delete operations — all other file tools run freely."""

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_delete)

    def check_delete(self, event: BeforeToolCallEvent) -> None:
        if event.tool_use["name"] != "delete_file":
            return

        approval = event.interrupt(
            "delete-approval",
            reason={"path": event.tool_use["input"]["path"]}
        )

        if approval.lower() != "y":
            event.cancel_tool = "User denied file deletion"
```

El agente recibe las cuatro tools y una instancia de ese hook:

```86:93:01/src/hooks/app.py
agent = Agent(
    model=OllamaModel(
    host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
    model_id="llama3.1",
    ),
    tools=[list_files, read_file, write_file, delete_file],
    hooks=[DeleteApprovalHook()],
)
```

Cuando el modelo quiere borrar, `agent(...)` vuelve con la interrupción. El bucle pregunta en la consola y reanuda con `interruptResponse`:

```110:120:01/src/hooks/app.py
    while result.stop_reason == "interrupt":
        for interrupt in result.interrupts:
            approval = input(f"\n  Delete '{interrupt.reason['path']}'? (y/N): ")
            result = agent([
                {
                    "interruptResponse": {
                        "interruptId": interrupt.id,
                        "response": approval,
                    }
                }
            ])
```

## Qué usa

- Modelo `llama3.1` en Ollama (`OLLAMA_HOST`).
- El sistema de archivos del contenedor. Un archivo creado aquí desaparece al recrear el contenedor.
- No abre el puerto 8000. Necesita TTY por `input()`.

## Activar

El entrypoint sigue siendo el servidor de sesiones. Este ejercicio se lanza en el contenedor que ya está corriendo. El directorio de trabajo puede ser `/app`.

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
docker compose exec -it app python -u src/hooks/app.py
```

El prompt es `You:`. `quit`, `exit` o `q` cierran el bucle.

## Probar

En esa consola, en tres turnos:

```text
You: lista los archivos de /app
You: escribe "hola" en /tmp/nota.txt
You: borra /tmp/nota.txt
```

Listar y escribir no preguntan. Al borrar aparece `Delete '/tmp/nota.txt'? (y/N):`. Con `y` la tool corre. Con otra respuesta, `cancel_tool` deja el mensaje `User denied file deletion` y el archivo sigue ahí.
