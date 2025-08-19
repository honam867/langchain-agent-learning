import sys
import os
from pathlib import Path

from langgraph.graph import END, START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    RemoveMessage,
    trim_messages,
)
from config import chat_model, get_graph_png


# Node
# def filter_messages_node(state: MessagesState):
#     delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:2]]
#     return {"messages": delete_messages}


def chat_model_node(state: MessagesState):
    msg = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o"),
        allow_partial=False,
    )
    return {"messages": chat_model.invoke(msg)}


# Build graph
builder = StateGraph(MessagesState)
# builder.add_node("filter_messages", filter_messages_node)
builder.add_node("chat_model", chat_model_node)

builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()


# Message list with a preamble
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Lance", id="2"))
messages.append(
    AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3")
)
messages.append(
    HumanMessage(
        "Yes, I know about whales. But what others should I learn about?",
        name="Lance",
        id="4",
    )
)

output = graph.invoke({"messages": messages})

# for m in output["messages"]:
#     m.pretty_print()
messages.append(output["messages"][-1])
messages.append(HumanMessage(f"Tell me where Orcas live!", name="Lance"))

output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()
