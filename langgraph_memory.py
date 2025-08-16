from langchain_tavily import TavilySearch
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
import config
from langgraph.checkpoint.memory import InMemorySaver

TOOLS_NODE = "tools"
CHATBOT_NODE = "chatbot"

memory = InMemorySaver()


llm = config.chat_model
search_tool = TavilySearch(
    max_results=2,
)
tools = [search_tool]


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node(CHATBOT_NODE, chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node(TOOLS_NODE, tool_node)

graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)

graph_builder.add_edge(TOOLS_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]}, config
    ):
        for value in event.values():
            print("❤️ Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
