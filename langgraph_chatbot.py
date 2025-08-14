from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

MODEL = "gpt-4o"
TEMPERATURE = 0.0
BASE_URL = "https://gpt1.shupremium.com/v1"
API_KEY = "4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"

llm = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


def stream_graph_update(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True: 
     try:
         user_input = input("User: ")
         if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
         stream_graph_update(user_input)
     except:
        user_input = "What do you know about LangGraph?"
        print(f"User: {user_input}")
        stream_graph_update(user_input)
        break


graph_builder = StateGraph(State)
