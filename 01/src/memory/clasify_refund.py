import httpx
import os

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://ollama:11434"
)

DECIDER_MODEL = os.getenv(
    "DECIDER_MODEL",
    "d1-omni:latest"
)

DECIDER_THRESHOLD = float(
    os.getenv("DECIDER_THRESHOLD", "0.80")
)


async def classify_refund(message: str):

    payload = {
        "model": DECIDER_MODEL,
        "state": message,
        "questions": {
            "refund_request": {
                "type": "noul",
                "instructions": (
                    "¿El usuario está solicitando explícitamente "
                    "un reembolso de dinero por una compra u orden?"
                ),
                "criteria": {
                    "true": (
                        "El usuario solicita que le devuelvan el dinero "
                        "de una compra o pedido."
                    ),
                    "false": (
                        "El usuario solamente pregunta por políticas, "
                        "consulta el estado de un reembolso, solicita "
                        "un cambio o reporta un problema sin pedir "
                        "la devolución de dinero."
                    )
                }
            }
        }
    }

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