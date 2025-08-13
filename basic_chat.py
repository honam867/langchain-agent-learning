from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

API_KEY = "sk-4eGENK1I1kNtvgiGrKgKJZk1y3eEeVPIJWNAMTeFugIiyht3"
template = "You are a witty assistant. Answer the following question: {question}"
prompt = PromptTemplate(input_variables=["question"], template=template)


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url="https://gpt1.shupremium.com/v1",
    api_key=API_KEY,
)

chain = LLMChain(llm=llm, prompt=prompt)

print(chain.invoke({"question": "Why is the sky blue?"})["text"])
