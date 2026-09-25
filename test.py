from dotenv import load_dotenv
import os

from langchain_mistralai import ChatMistralAI

load_dotenv()

llm = ChatMistralAI(
    model="mistral-small-latest"
)

response = llm.invoke("Say hello in one sentence.")

print(response.content)