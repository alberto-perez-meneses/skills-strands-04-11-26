import operator
from typing import Literal
import os
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from strands import Agent, tool
from strands.models.ollama import OllamaModel

_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
}

@tool
def weather_forecast(city: str, days: int = 3) -> str:
    """Get the weather forecast for a city for the next number of days.
    
    Args:
        city: The city to get the weather forecast for.
        days: The number of days to get the weather forecast for.
    Returns:
        str: The weather forecast for the city for the next number of days.
    """

    return f"Weather forecast for {city} for the next {days} days..."



@tool
def calculator(a: float, b: float, op: Literal["+", "-", "*", "/", "**"]) -> float:
    """Apply an arithmetic operator to two numbers.

    Args:
        a: Left operand.
        b: Right operand.
        op: One of "+", "-", "*", "/", "**".
    """
    return _OPS[op](a, b)


# FastAPI app
app = FastAPI()


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


# Function to start server without blocking


async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_server())