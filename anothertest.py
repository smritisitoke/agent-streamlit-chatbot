from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print("Groq key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing.")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=api_key,
)

response = llm.invoke("Say hello in one sentence.")
print(response.content)