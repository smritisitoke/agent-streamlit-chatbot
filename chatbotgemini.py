
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# -----------------------------------
# 1. Load API key
# -----------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")


# -----------------------------------
# 2. Create Gemini model
# -----------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key
)


# -----------------------------------
# 3. Extract only actual text
# -----------------------------------

def extract_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        texts = []

        for item in content:

            if isinstance(item, dict):
                if item.get("type") == "text":
                    texts.append(item.get("text", ""))

        return "\n".join(texts)

    return str(content)


# -----------------------------------
# 4. Choose AI personality
# -----------------------------------

print("\nChoose your AI mode:")
print("1. Angry mode")
print("2. Funny mode")
print("3. Sad mode")

while True:

    try:

        choice = int(input("\nEnter your choice: "))

        if choice == 1:

            mode = """
            You are an angry AI assistant.
            Respond in an irritated and impatient tone.
            Keep your answers concise.
            Do not be abusive or threatening.
            """

            break

        elif choice == 2:

            mode = """
            You are a funny AI assistant.
            Respond with humor and light jokes.
            Keep your answers concise.
            """

            break

        elif choice == 3:

            mode = """
            You are a sad and emotional AI assistant.
            Respond in a melancholic and emotional tone.
            Keep your answers concise.
            """

            break

        else:

            print("Invalid choice. Please enter 1, 2, or 3.")

    except ValueError:

        print("Please enter only 1, 2, or 3.")


# -----------------------------------
# 5. Conversation memory
# -----------------------------------

messages = [
    SystemMessage(content=mode)
]


# -----------------------------------
# 6. Start chatbot
# -----------------------------------

print("\n----------------------------------------")
print("Chatbot started!")
print("Type 0 to exit.")
print("----------------------------------------\n")


while True:

    prompt = input("You : ")

    # Exit
    if prompt == "0":
        print("\nConversation ended.")
        break

    # Ignore empty input
    if not prompt.strip():
        continue

    # Add user's message
    messages.append(
        HumanMessage(content=prompt)
    )

    try:

        # Send recent conversation to Gemini
        response = model.invoke(messages[-6:])

        # Extract only text
        reply = extract_text(response.content)

        # Save AI response
        messages.append(
            AIMessage(content=reply)
        )

        # Display clean response
        print("Bot :", reply)

    except Exception as e:

        print("Something went wrong.")
        print("Error:", e)

