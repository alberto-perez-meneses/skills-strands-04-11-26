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
from mcp.client.sse import sse_client

from mcp import stdio_client, StdioServerParameters

from strands.tools.mcp import MCPClient

# Create MCP client with stdio transport
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
))

playwright_mcp_client = MCPClient(lambda: sse_client("http://playwright-mcp:8931/sse"))
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
        tools=[mcp_client, playwright_mcp_client],
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
    print("Starting server...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    print("Server started")


if __name__ == "__main__":
    asyncio.run(start_server())