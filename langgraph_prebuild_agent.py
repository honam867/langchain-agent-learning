from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

MODEL = "gpt-4o"
TEMPERATURE = 0.0
BASE_URL = "https://gpt1.shupremium.com/v1"
API_KEY = "4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"

chat_model = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)


def get_weather(city: str) -> str:
    """Get the weather in a given city"""
    return f"The weather in {city} is sunny"


tools = [get_weather]

agent = create_react_agent(chat_model, tools, checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
vn_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in Vietnam?"}]},
    config
)

sf_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in San Francisco?"}]},
    config,
)
print(vn_response["messages"][-1].content)
print(sf_response["messages"][-1].content)
