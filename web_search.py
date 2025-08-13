from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

API_KEY = "sk-4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"
BASE_URL = "https://gpt1.shupremium.com/v1"
MODEL = "gpt-4o"
TEMPERATURE = 0

# 1. Initialize chat model:
chat_model = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)

# 2. Define a prompt template with placeholders for search results and user questions:

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that uses web search results to answer questions.",
        ),
        (
            "user",
            "Search results:\n{search_results}\n\nQuestion: {question}\nAnswer:",
        ),
    ]
)

search_tool = DuckDuckGoSearchRun()


def run_app(user_question: str):
    search_results = search_tool.run(user_question)

    prompt = prompt_template.invoke(
        {
            "search_results": search_results,
            "question": user_question,
        }
    )

    response = chat_model.invoke(prompt.to_messages())

    return response.content


user_input = "Who is the current president of the United States?"
answer = run_app(user_input)
print(answer)
