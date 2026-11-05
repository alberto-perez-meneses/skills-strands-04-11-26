# skills

Agente de atención al cliente por consola. Las tools consultan datos fijos y dos archivos markdown le dicen al agente qué pasos seguir.

Código: [`src/skills/app.py`](../src/skills/app.py), [`src/skills/skills/order-tracking/SKILL.md`](../src/skills/skills/order-tracking/SKILL.md) y [`src/skills/skills/account-troubleshooting/SKILL.md`](../src/skills/skills/account-troubleshooting/SKILL.md).

## Descripción

El cliente escribe en la terminal. El agente busca el cliente y sus pedidos, y puede simular un reembolso. Según el caso activa la skill de seguimiento de pedidos o la de problemas de cuenta.

## Temas

- Plugin `AgentSkills`: carga skills desde una carpeta y el agente puede activarlas por nombre.
- Skill en markdown: el frente `name` y `description` dice cuándo usarla; el cuerpo es la guía de pasos.
- Tools de dominio: ficha del cliente, historial de pedidos y reembolso.
- Bucle de consola: cada línea es un turno del mismo agente, hasta `quit`.

## Pieza de código

Las tres tools leen diccionarios en memoria. `process_refund` no cobra ni guarda nada: siempre responde que el reembolso quedó procesado.

```102:110:01/src/skills/app.py
@tool
def process_refund(order_id: str, amount: float) -> str:
    """Process a refund for an order.

    Args:
        order_id: The order ID to refund
        amount: The refund amount in dollars
    """
    return f"Refund of ${amount:.2f} processed for order {order_id}. Expect 3-5 business days."
```

`AgentSkills` apunta a `./skills`, relativo al directorio desde el que se arranca el proceso. El agente recibe esas skills como plugin, junto con las tres tools:

```128:138:01/src/skills/app.py
skills_plugin = AgentSkills(skills=["./skills"])

agent = Agent(
    model=OllamaModel(
        host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
        model_id="llama3.1",
    ),
    tools=[lookup_customer, get_order_history, process_refund],
    plugins=[skills_plugin],
    system_prompt=SYSTEM_PROMPT,
)
```

El bucle lee la consola y llama al mismo `agent` en cada turno:

```144:152:01/src/skills/app.py
    while True:
        user_input = input("\nCustomer: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        print()
        agent(user_input)
```

Cada skill declara su nombre y cuándo aplica. Pedidos:

```1:4:01/src/skills/skills/order-tracking/SKILL.md
---
name: order-tracking
description: Help customers check the status of their orders, understand delivery timelines, and escalate delayed shipments.
---
```

Cuenta:

```1:4:01/src/skills/skills/account-troubleshooting/SKILL.md
---
name: account-troubleshooting
description: Guide for helping customers with account issues including password resets, identity verification, and account updates.
---
```

## Qué usa

- Modelo `llama3.1` en Ollama (`OLLAMA_HOST`).
- Datos fijos: `C-1001` es Sarah Johnson, cuenta activa, pedidos ORD-5521 (entregado) y ORD-5488 (enviado). `C-1002` es Mike Chen, cuenta bloqueada, pedido ORD-5390 (retrasado).
- No abre el puerto 8000. Necesita una terminal con TTY porque usa `input()`.

## Activar

[`entrypoint.sh`](../entrypoint.sh) sigue con el servidor de sesiones. Este ejercicio se abre en otra sesión del mismo contenedor, y el directorio de trabajo tiene que ser `src/skills` para que `./skills` encuentre los markdown.

Desde la raíz de `ejercicios`, con la app ya en marcha:

```powershell
docker compose up --build app
docker compose exec -it app sh
cd src/skills
python -u app.py
```

El prompt es `Customer:`. `quit`, `exit` o `q` cierran el bucle.

## Probar

En esa consola:

```text
Customer: quiero saber el estado de mi pedido, mi cliente es C-1002
```

El agente debe llamar a `lookup_customer` y `get_order_history`. La cuenta está bloqueada y ORD-5390 figura como retrasado. Si pides cancelarlo y confirmas, `process_refund` responde que el reembolso de ORD-5390 quedó procesado en 3 a 5 días hábiles. Esa respuesta sale del `return` de la tool; no hay un pedido real que cambiar.
