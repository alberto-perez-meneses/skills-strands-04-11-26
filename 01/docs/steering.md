# steering

El mismo agente de atención al cliente, con dos controles que corren aparte del modelo: uno fija el orden del reembolso y otro revisa el tono de la respuesta.

Código: [`src/steering/app.py`](../src/steering/app.py), [`src/steering/steering_handlers.py`](../src/steering/steering_handlers.py) y [`src/steering/customer_service_tools.py`](../src/steering/customer_service_tools.py).

## Descripción

El cliente escribe en la consola. Antes de `process_refund`, un handler determinista exige haber consultado al cliente y sus pedidos, y que el monto coincida con el pedido. Después de cada respuesta del modelo, otro handler evalúa el tono.

## Temas

- Steering determinista: `RefundWorkflowHandler` decide `Proceed` o `Guide` antes de la tool, mirando el historial de llamadas.
- Ledger: `LedgerProvider` guarda qué tools ya terminaron con `success`.
- Steering con modelo: `ToneGuardrailHandler` revisa la respuesta en `steer_after_model`.
- Skills en la misma carpeta: `order-tracking`, `account-troubleshooting`, `refund-processing` y `pdf-processing`.
- Las tools siguen siendo datos fijos. `lookup_customer` busca por id (`C-1001`), no por correo.

## Pieza de código

El agente junta el plugin de skills y los dos handlers:

```21:32:01/src/steering/app.py
agent = Agent(
    model=OllamaModel(
        host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
        model_id="llama3.1",
    ),
    tools=[lookup_customer, get_order_history, process_refund],
    plugins=[
        skills_plugin,              # On-demand workflow instructions
        RefundWorkflowHandler(),    # Deterministic: enforce refund steps
        tone_handler,               # LLM-based: enforce communication quality
    ],
    system_prompt=SYSTEM_PROMPT,
)
```

`steer_before_tool` solo actúa sobre `process_refund`. Si en el ledger no hay un `lookup_customer` o un `get_order_history` con estado `success`, devuelve `Guide` y la tool no corre:

```23:44:01/src/steering/steering_handlers.py
    async def steer_before_tool(self, *, agent, tool_use, **kwargs) -> ToolSteeringAction:
        if tool_use.get("name") != "process_refund":
            return Proceed(reason="Not a refund operation")

        print("[STEERING] 🔍 process_refund attempted — checking workflow...")

        # Get execution history through managed ledger
        ledger = self.steering_context.data.get("ledger", {})
        tool_calls = ledger.get("tool_calls", [])
        print(f"[STEERING] 📋 Ledger has {len(tool_calls)} tool calls: {[c.get('tool_name', '?') + ':' + c.get('status', '?') for c in tool_calls]}")

        # Must look up customer first
        customer_verified = any(
            c["tool_name"] == "lookup_customer" and c["status"] == "success"
            for c in tool_calls
        )
        if not customer_verified:
            print("[STEERING] ⚠️  Blocked: must look up customer first")
            return Guide(
                reason="You must look up the customer with lookup_customer "
                "before processing a refund."
            )
```

Si el id del pedido no está en el texto del historial, o el monto no coincide con el `$` de ese pedido, también devuelve `Guide`. Si todo cuadra, `Proceed`.

`ToneGuardrailHandler` llama al steering del SDK después de la respuesta y escribe `[TONE]` en la consola. `Approved` es un `Proceed`. Cualquier otra acción imprime el `reason`:

```113:118:01/src/steering/steering_handlers.py
    async def steer_after_model(self, **kwargs):
        print("[TONE] 🔍 Evaluating agent response...")
        result = await super().steer_after_model(**kwargs)
        action_type = type(result).__name__
        print(f"[TONE] {'✅ Approved' if action_type == 'Proceed' else '⚠️  Guided: ' + getattr(result, 'reason', '')}")
        return result
```

Las tools viven en `customer_service_tools.py`. `process_refund` sigue siendo un texto fijo: no cambia el diccionario `ORDERS`.

## Qué usa

- Modelo `llama3.1` en Ollama. El handler de tono también llama a ese modelo.
- `C-1001`: Sarah Johnson, `sarah.johnson@email.com`, cuenta activa. Pedidos ORD-5521 (audífonos, 79.99, entregado) y ORD-5488 (USB-C Hub, 45.00, enviado).
- `C-1002`: Mike Chen, `mike.chen@email.com`, cuenta bloqueada. Pedido ORD-5390 (teclado, 149.99, retrasado).
- No abre el puerto 8000. Necesita TTY.

## Activar

El entrypoint sigue en sesiones. Este ejercicio se abrió en el contenedor, con el directorio de trabajo en `src/steering`, igual que skills, para que `./skills` resuelva.

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
docker compose exec -it app sh
cd src/steering
python -u app.py
```

El prompt es `Customer:`. `quit`, `exit` o `q` cierran el bucle.

## Probar

Pide revisar el pedido con el id, no con el correo. La tool solo acepta `C-1001` o `C-1002`:

```text
Customer: soy Sarah, mi cliente es C-1001, quiero el estado de mi USB-C Hub
```

En la consola debe aparecer `Tool #1: lookup_customer` o `get_order_history`, y líneas `[TONE]`.

Para ver el bloqueo del reembolso, pide devolver el hub en el primer mensaje, antes de que existan esas dos llamadas. El log muestra `[STEERING]` y un `Guide` pidiendo `lookup_customer` y después `get_order_history`. Si el monto no es `45.00` para ORD-5488, el mismo handler lo rechaza.

En una corrida, después de pedir el reembolso del USB-C Hub el proceso terminó con `TypeError: must resume from interrupt with list of interruptResponse's`. El bucle siempre llama `agent(user_input)` con un string. Si el turno anterior dejó una interrupción pendiente, el siguiente mensaje de texto no es la lista de `interruptResponse` que el SDK espera para reanudar.
