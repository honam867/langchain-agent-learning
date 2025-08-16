from langchain_core.messages import ToolMessage
from langchain_tavily import TavilySearch
import os
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

os.environ["TAVILY_API_KEY"] = "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"
MODEL = "gpt-4o"
TEMPERATURE = 0.0
BASE_URL = "https://gpt1.shupremium.com/v1"
API_KEY = "4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"

TOOLS_NODE = "tools"
CHATBOT_NODE = "chatbot"


llm = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)
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

# class BasicToolNode:
#     """A node that runs the tools requested in the last AIMessage."""

#     def __init__(self, tools: list) -> None:
#         self.tools_by_name = {tool.name: tool for tool in tools}

#     def __call__(self, inputs: dict):
#         if messages := inputs.get("messages", []):
#             print("❤️ messages from ai", messages)
#             message = messages[-1]
#         else:
#             raise ValueError("No message found in input")
#         outputs = []
#         for tool_call in message.tool_calls:
#             tool_result = self.tools_by_name[tool_call["name"]].invoke(
#                 tool_call["args"]
#             )
#             outputs.append(
#                 ToolMessage(
#                     content=json.dumps(tool_result),
#                     name=tool_call["name"],
#                     tool_call_id=tool_call["id"],
#                 )
#             )
#         return {"messages": outputs}


tool_node = ToolNode(tools=tools)
graph_builder.add_node(TOOLS_NODE, tool_node)


# def route_tools(
#     state: State,
# ):
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get("messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(f"No messages found in input state to tool_edge: {state}")
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"
#     return END


graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)

graph_builder.add_edge(TOOLS_NODE, CHATBOT_NODE)
graph_builder.add_edge(START, CHATBOT_NODE)
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
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
