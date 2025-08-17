from typing import Annotated
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from config import chat_model
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

TOOLS_NODE = "tools"
CHATBOT_NODE = "chatbot"


llm = chat_model


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]


search_tool = TavilySearch(
    max_results=2,
)
tools = [search_tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}


graph_builder.add_node(CHATBOT_NODE, chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node(TOOLS_NODE, tool_node)

graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)

graph_builder.add_edge(TOOLS_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)


user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()


human_response = (
    "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
    " It's much more reliable and extensible than simple autonomous agents."
)

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")

for event in events:
    event["messages"][-1].pretty_print()
