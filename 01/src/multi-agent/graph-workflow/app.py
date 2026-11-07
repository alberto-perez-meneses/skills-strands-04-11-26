from strands import Agent
from strands.multiagent import GraphBuilder
from strands.vended_tools.web_fetch import web_fetch
from strands.models.ollama import OllamaModel
import os
from web_search import web_search

model = OllamaModel(host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"), model_id="llama3.1",)



researcher = Agent(
    model=model,
    name="researcher",
    system_prompt="Gather comprehensive information from the web.",
    tools=[web_fetch, web_search],
)

analyst = Agent(
    model=model,
    name="analyst",
    system_prompt="Identify patterns, trends, and key insights from research.",
)

summarizer = Agent(
    model=model,
    name="summarizer",
    system_prompt="Condense raw research into concise key points.",
)

report_writer = Agent(
    model=model,
    name="report_writer",
    system_prompt="Synthesize analysis and summaries into a final report.",
)

builder = GraphBuilder()
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(summarizer, "summarize")
builder.add_node(report_writer, "report")

builder.add_edge("research", "analysis")
builder.add_edge("research", "summarize")   # analyst + summarizer run in parallel
builder.add_edge("analysis", "report")
builder.add_edge("summarize", "report")      # report waits for both

builder.set_execution_timeout(600)
graph = builder.build()

result = graph("Research the impact of AI on healthcare")