import asyncio
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import create_react_agent

API_KEY = "sk-4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"
BASE_URL = "https://gpt1.shupremium.com/v1"
MODEL = "gpt-4o"
TEMPERATURE = 0

search_tool = DuckDuckGoSearchResults()

tools = [search_tool]

chat_model = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)

agent = create_react_agent(chat_model, tools)


async def main():
    chat_history = []
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() == "exit":
            break
        chat_history.append({"role": "user", "content": user_input})
        
        print("Bot: ", end="", flush=True)
        
        # Stream the response using astream with "messages" mode for token-by-token streaming
        assistant_message = ""
        async for token, metadata in agent.astream(
            {"messages": chat_history},
            stream_mode="messages"
        ):
            if token.content:
                print(token.content, end="", flush=True)
                assistant_message += token.content
        
        print()  # New line after streaming is complete
        chat_history.append({"role": "assistant", "content": assistant_message})


if __name__ == "__main__":
    asyncio.run(main())
