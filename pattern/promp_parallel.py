from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import chat_model, get_graph_png


class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str


llm = chat_model

graph_builder = StateGraph(State)


# Nodes
def write_joke(state: State):
    msg = chat_model.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}


def write_story(state: State):
    msg = chat_model.invoke(f"Write a short story about {state['topic']}")
    return {"story": msg.content}


def write_poem(state: State):
    msg = chat_model.invoke(f"Write a short poem about {state['topic']}")
    return {"poem": msg.content}


def aggregate_output(state: State):
    msg = chat_model.invoke(
        f"Combine the following outputs into a single output and translated it in Vietnamese: Joke: {state['joke']}\n\nStory: {state['story']}\n\nPoem: {state['poem']}"
    )
    return {"combined_output": msg.content}


graph_builder.add_node("write_joke", write_joke)
graph_builder.add_node("write_story", write_story)
graph_builder.add_node("write_poem", write_poem)
graph_builder.add_node("aggregate_output", aggregate_output)

# Add edge
graph_builder.add_edge(START, "write_joke")
graph_builder.add_edge(START, "write_story")
graph_builder.add_edge(START, "write_poem")

graph_builder.add_edge("write_joke", "aggregate_output")
graph_builder.add_edge("write_story", "aggregate_output")
graph_builder.add_edge("write_poem", "aggregate_output")
graph_builder.add_edge("aggregate_output", END)

graph = graph_builder.compile()


state = graph.invoke({"topic": "Cat"})
print(state["combined_output"])

get_graph_png(graph, "promp_parallel.png")
