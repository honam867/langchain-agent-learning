import stat
import sys
import os
from pathlib import Path

from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from urllib3 import response

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import chat_model, get_graph_png

import sqlite3

# In memory
conn = sqlite3.connect(":memory:", check_same_thread=False)

# pull file if it doesn't exist and connect to local db


db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
print(conn)
memory = SqliteSaver(conn)


class State(MessagesState):
    summary: str


def call_model(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = chat_model.invoke(messages)

    return {"messages": response}


def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = chat_model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:2]]
    return {"summary": response.content, "messages": delete_messages}


def should_continue(state: State):
    """Return the next node to execute."""

    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"

    return END


workflow = StateGraph(State)

# Nodes:
workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

# Edges
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges(
    "conversation",
    should_continue,
    {
        END: END,
        "summarize_conversation": "summarize_conversation",
    },
)

# Build graph
graph = workflow.compile(checkpointer=memory)

# get_graph_png(graph, "chatbot_external_memory.png")


# Create a thread
config = {"configurable": {"thread_id": "1"}}

# Start conversation
# input_message = HumanMessage(content="hi! I'm Minh")
# output = graph.invoke({"messages": [input_message]}, config)
# for m in output["messages"][-1:]:
#     m.pretty_print()

# input_message = HumanMessage(content="what's my name?")
# output = graph.invoke({"messages": [input_message]}, config)
# for m in output["messages"][-1:]:
#     m.pretty_print()

input_message = HumanMessage(
    content="What's my name? I like swimming and playing football !"
)
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()
