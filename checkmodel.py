from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

response = requests.get(
    "https://api.mistral.ai/v1/models",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

print("Status:", response.status_code)

data = response.json()

if response.ok:
    for model in data["data"]:
        print(model["id"])
else:
    print(data)