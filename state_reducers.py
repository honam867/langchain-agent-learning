from operator import add, mul
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.errors import InvalidUpdateError
from langgraph.graph import MessagesState, StateGraph, START, END, add_messages
from config import get_graph_png


class State(TypedDict):
    foo: Annotated[list[int], add]
    bar: Annotated[list[int], add]


class CustomMessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    add_key_1: str
    add_key_2: str


class ExtendMessagesState(MessagesState):
    add_key_1: str
    add_key_2: str


# Subgraph
def subgraph_node_1(state):
    print("---Subgraph Node 1---", state["bar"][-1])
    return {"bar": [state["bar"][-1] * 2]}


sub_graph_builder = StateGraph(State)
sub_graph_builder.add_node(subgraph_node_1)
sub_graph_builder.add_edge(START, "subgraph_node_1")
sub_graph = sub_graph_builder.compile()


# Main Graph
def node_1(state):
    print("---Node 1---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1], "bar": [state["bar"][-1] * 2]}


def node_2(state):
    print("---Node 2---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1]}


def node_3(state):
    print("---Node 3---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1]}


graph_builder = StateGraph(State)
# Add node:
# graph_builder.add_node("subgraph", sub_graph)
graph_builder.add_node("node_1", node_1)
graph_builder.add_node("node_2", node_2)
graph_builder.add_node("node_3", node_3)


# Logic:
graph_builder.add_edge(START, "node_1")
graph_builder.add_edge("node_1", "node_2")
graph_builder.add_edge("node_1", "node_3")
graph_builder.add_edge("node_2", END)
graph_builder.add_edge("node_3", END)

graph = graph_builder.compile()

try:
    result = graph.invoke({"foo": [1], "bar": [2]})
    print(result)
except InvalidUpdateError as e:
    print(f"InvalidUpdateError occurred: {e}")

get_graph_png(graph, "state_reducers.png")
