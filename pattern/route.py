from typing import TypedDict
from pydantic import BaseModel, Field
from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import chat_model, get_graph_png


class Route(BaseModel):
    step: Literal["poem", "story", "joke"] = Field(
        None, description="The next step is the routing process"
    )


router = chat_model.with_structured_output(Route)


class State(TypedDict):
    input: str
    decision: str
    output: str


graph_builder = StateGraph(State)


# Nodes
def write_joke(state: State):
    msg = chat_model.invoke(state["input"])
    return {"output": msg.content}


def write_story(state: State):
    msg = chat_model.invoke(state["input"])
    return {"output": msg.content}


def write_poem(state: State):
    msg = chat_model.invoke(state["input"])
    return {"output": msg.content}


def chat_model_call_router(state: State):
    decision = router.invoke(
        [
            SystemMessage(
                content="Route the input to story, joke, or poem based on the user's request."
            ),
            HumanMessage(content=state["input"]),
        ]
    )
    print("❤️ decision", decision)
    return {"decision": decision.step}


def route_decision(state: State):
    if state["decision"] == "poem":
        return "write_poem"
    elif state["decision"] == "story":
        return "write_story"
    else:
        return "write_joke"


# Add Nodes
graph_builder.add_node("write_joke", write_joke)
graph_builder.add_node("write_story", write_story)
graph_builder.add_node("write_poem", write_poem)
graph_builder.add_node("chat_model_call_router", chat_model_call_router)


# Add logic
graph_builder.add_edge(START, "chat_model_call_router")
graph_builder.add_conditional_edges(
    "chat_model_call_router",
    route_decision,
    {
        "write_joke": "write_joke",
        "write_story": "write_story",
        "write_poem": "write_poem",
    },
)

graph_builder.add_edge("write_joke", END)
graph_builder.add_edge("write_story", END)
graph_builder.add_edge("write_poem", END)


router_workflow = graph_builder.compile()


# get_graph_png(graph, "route.png")
# Invoke
state = router_workflow.invoke({"input": "Write me a poem about the girl"})
print(state["output"])
