from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langchain_tavily import TavilySearch
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from config import chat_model, get_graph_png
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

from pathlib import Path

TOOLS_NODE = "tools"
CHATBOT_NODE = "chatbot"


llm = chat_model


class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str


graph_builder = StateGraph(State)


@tool
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)


search_tool = TavilySearch(
    max_results=2,
)
tools = [search_tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)


def node_1(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}


graph_builder.add_node(CHATBOT_NODE, node_1)

node_2 = ToolNode(tools=tools)
graph_builder.add_node(TOOLS_NODE, node_2)

graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)

graph_builder.add_edge(TOOLS_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

get_graph_png(graph, "customize-state.png")