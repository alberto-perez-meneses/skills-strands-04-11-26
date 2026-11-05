import os
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.session import SnapshotSessionManager
from strands.storage import LocalFileStorage


# FastAPI app
app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str
    session_id: str


model = OllamaModel(
    host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
    model_id="llama3.1",
)

def get_session_manager(session_id: str):
# Create a snapshot session manager with a unique session ID
    return SnapshotSessionManager(
        session_id=session_id,
        storage=LocalFileStorage("./sessions/"),
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
        session_manager = get_session_manager(request.session_id)
        agent =  Agent(model=model,
        session_manager=session_manager,
        tools=[],
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