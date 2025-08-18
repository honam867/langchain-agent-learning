from typing import Annotated, List, Literal, TypedDict
import operator
from langchain_tavily import TavilySearch

import sys
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import chat_model, get_graph_png


class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str


class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not"
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it"
    )


evaluator = chat_model.with_structured_output(Feedback)


# Nodes
def llm_call_generator(state: State):
    """LLM generate a joke"""
    if state.get("feedback"):
        msg = chat_model.invoke(
            f"Write a joke about {state['topic']} but take into account the feedback: {state['feedback']}"
        )
    else:
        msg = chat_model.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}


def llm_call_evaluator(state: State):
    """LLM evaluate the joke"""
    grade = evaluator.invoke(f"Grade the joke: {state['joke']}")
    return {"feedback": grade.feedback, "funny_or_not": grade.grade}


def route_joke(state: State):
    """Route the joke to the evaluator or the optimizer"""
    if state["funny_or_not"] == "funny":
        return "Accepted"
    elif state["funny_or_not"] == "not funny":
        return "Rejected + Feedback"


optimizer_builder = StateGraph(State)
# Add node
optimizer_builder.add_node("llm_call_generator", llm_call_generator)
optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)

# Edges
optimizer_builder.add_edge(START, "llm_call_generator")
optimizer_builder.add_edge("llm_call_generator", "llm_call_evaluator")
optimizer_builder.add_conditional_edges(
    "llm_call_evaluator",
    route_joke,
    {"Accepted": END, "Rejected + Feedback": "llm_call_generator"},
)

optimizer = optimizer_builder.compile()


state = optimizer.invoke({"topic": "Dog"})
print(state["joke"])
