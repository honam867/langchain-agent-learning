import os
from langchain_openai import ChatOpenAI

# Model Configuration
MODEL = "gpt-4o"
TEMPERATURE = 0.0
BASE_URL = "https://gpt1.shupremium.com/v1"
API_KEY = "4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"

# Tavily API Key
os.environ["TAVILY_API_KEY"] = "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"

# LangSmith Configuration
# You need to get your API key from: https://smith.langchain.com/
LANGSMITH_API_KEY = "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"  # Replace with your actual API key
LANGSMITH_PROJECT = "learning-langgraph"  # Your project name

def setup_langsmith_tracing():
    """Configure LangSmith tracing environment variables."""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

# Pre-configured chat model for reuse
chat_model = ChatOpenAI(
    model=MODEL,
    temperature=TEMPERATURE,
    base_url=BASE_URL,
    api_key=API_KEY,
)

# Enable LangSmith tracing (call this function to activate)
# Uncomment the line below once you've set your API key
setup_langsmith_tracing()