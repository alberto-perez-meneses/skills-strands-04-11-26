from datetime import datetime, timezone
from strands import Agent
from strands.vended_plugins.context_injector import ContextInjector
from strands.models.ollama import OllamaModel
import os
import json

agent = Agent(
    model=OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",),
    plugins=[
        ContextInjector(
            lambda context: f"<now>{datetime.now(timezone.utc).isoformat()}</now>"
        ),
    ],
)

result = agent("Hi, I'm customer C-1001. Can you check on my recent orders?")

print(f"Total messages: {len(agent.messages)}")

for msg in agent.messages:
    role = msg["role"]
    for block in msg.get("content", []):
        if "text" in block:
            print(f"{role}: {block['text'][:100]}")
        elif "toolUse" in block:
            tu = block["toolUse"]
            print(f"tool call: {tu['name']}({json.dumps(tu.get('input', {}))})")

print(f"Cycles: {result.metrics.get_summary()['total_cycles']}")
print(f"Tokens: {result.metrics.accumulated_usage['totalTokens']}")