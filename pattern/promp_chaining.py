from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import chat_model


class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str


llm = chat_model


# Nodes
def generate_joke(state: State):
    msg = chat_model.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}


def check_punchline(state: State):
    print("Checking punchline: ", state["joke"])
    if "?" in state["joke"] and "!" in state["joke"]:
        return "Pass"
    return "Fail"


def improve_joke(state: State):
    msg = chat_model.invoke(
        f"Make this joke funnier by adding a punchline: {state['joke']}"
    )
    return {"improved_joke": msg.content}


def final_joke(state: State):
    msg = chat_model.invoke(f"Add a twist to the joke: {state['improved_joke']}")
    return {"final_joke": msg.content}


graph_builder = StateGraph(State)

# Add node
graph_builder.add_node("generate_joke", generate_joke)
graph_builder.add_node("improve_joke", improve_joke)
graph_builder.add_node("final_joke", final_joke)

# Add edge
graph_builder.add_edge(START, "generate_joke")
graph_builder.add_conditional_edges(
    "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
)
graph_builder.add_edge("improve_joke", "final_joke")
graph_builder.add_edge("final_joke", END)

graph = graph_builder.compile()


state = graph.invoke({"topic": "Cat"})
print("Initial joke:")
print(state["joke"])

print("\n--- --- ---\n")

if "improved_joke" in state:
    print("Improved joke:")
    print(state["improved_joke"])
    print("\n--- --- ---\n")

    print("Final joke:")
    print(state["final_joke"])
else:
    print("Joke failed quality gate - no punchline detected!")

# get_graph_png(graph, "promp_chaining.png")
