from operator import add
from typing import Annotated, TypedDict
from langgraph.errors import InvalidUpdateError
from langgraph.graph import StateGraph, START, END
from config import get_graph_png


class State(TypedDict):
    foo: Annotated[list[int], add]


graph_builder = StateGraph(State)


def node_1(state):
    print("---Node 1---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1]}


def node_2(state):
    print("---Node 2---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1]}


def node_3(state):
    print("---Node 3---", state["foo"][-1])
    return {"foo": [state["foo"][-1] + 1]}


# Add node:
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
    result = graph.invoke({"foo": [5, 5, 5]})
    print(result)
except InvalidUpdateError as e:
    print(f"InvalidUpdateError occurred: {e}")

# get_graph_png(graph, "state_reducers.png")
