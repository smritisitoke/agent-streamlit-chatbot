from dotenv import load_dotenv
import os

load_dotenv()

print("Mistral key loaded:", bool(os.getenv("MISTRAL_API_KEY")))