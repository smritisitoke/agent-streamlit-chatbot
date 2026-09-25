from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model

model = init_chat_model("google_genai:gemini-3.7-flash")

response = model.invoke("why do parrots talk?")

print(response.content)