from strands import Agent
from strands.vended_tools.web_fetch import web_fetch
from strands.models.ollama import OllamaModel
import os

model = OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",)
researcher = Agent(
    model=model,
    name="researcher",
    system_prompt="You are a research specialist. Find factual information.",
    tools=[web_fetch],
)

writer = Agent(
    model=model,
    name="writer",
    system_prompt="You are a technical writer. Use the researcher to gather facts.",
    tools=[researcher],  # Pass agent directly as a tool
)

writer("Research the FastAPI GitHub repo and write a 3-sentence summary.")