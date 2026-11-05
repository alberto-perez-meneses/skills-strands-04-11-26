import operator
from typing import Literal
import os
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from strands import Agent
from strands.models.ollama import OllamaModel

from clasify_refund import classify_refund

from strands.memory import MemoryManager
from strands.vended_memory_stores.file_memory_store import (FileMemoryStore,)


app = FastAPI()

store = FileMemoryStore(name="agent-memory")

async def add_memory():
    key = await store.add("# Travel preferences\n- Prefers aisle seats"
    )
    print(f"Memory added with key: {key}")

class PromptRequest(BaseModel):
    prompt: str


model = OllamaModel(
    host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
    model_id="llama3.1",
)


def custom_callback_handler(**kwargs):
    # Process stream data
    if "data" in kwargs:
        print(f"MODEL OUTPUT: {kwargs['data']}")
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\nUSING TOOL: {kwargs['current_tool_use']['name']}")


@app.post("/stream")
async def stream(request: PromptRequest):

    # 1. Obtener decisión de Strands Decider
    decision = await get_decision_context(request.prompt)
   

    # 2. Construir contexto para el agente
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
    """

    async def generate():
        agent =  Agent(model=model,
        memory_manager=MemoryManager(stores=[store]),
        tools=[],
        callback_handler=custom_callback_handler)

        async for event in agent.stream_async(enriched_prompt):
            # Ajustar según el formato de eventos de tu versión
            # de Strands Agents.
            if "data" in event:
                yield event["data"]

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

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

# Function to start server without blocking


async def start_server():
    print("Starting server...")
    await add_memory()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    print("Server started")


if __name__ == "__main__":
    asyncio.run(start_server())