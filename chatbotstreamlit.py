
import streamlit as st
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
    st.error("GOOGLE_API_KEY is missing. Check your .env file.")
    st.stop()


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
# 4. Page configuration
# -----------------------------------

st.set_page_config(
    page_title="Smriti's First Chatbot",
    page_icon="🤖",
    layout="centered"
)


# -----------------------------------
# 5. Title
# -----------------------------------

st.title("🤖 AI PERSONALITY")

st.write("Choose a personality and start chatting with Gemini!")


# -----------------------------------
# 6. Choose AI personality
# -----------------------------------

mode = st.selectbox(
    "Choose your AI mode:",
    [
        "😡 Angry mode",
        "😂 Funny mode",
        "😢 Sad mode"
    ]
)


# -----------------------------------
# 7. Personality prompts
# -----------------------------------

if mode == "😡 Angry mode":

    system_prompt = """
    You are an angry AI assistant.
    Respond in an irritated and impatient tone.
    Keep your answers concise.
    Do not be abusive or threatening.
    """

elif mode == "😂 Funny mode":

    system_prompt = """
    You are a funny AI assistant.
    Respond with humor and light jokes.
    Keep your answers concise.
    """

else:

    system_prompt = """
    You are a sad and emotional AI assistant.
    Respond in a melancholic and emotional tone.
    Keep your answers concise.
    """


# -----------------------------------
# 8. Initialize conversation
# -----------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [
        SystemMessage(content=system_prompt)
    ]

    st.session_state.mode = mode


# -----------------------------------
# 9. Change personality
# -----------------------------------

if st.session_state.mode != mode:

    st.session_state.mode = mode

    st.session_state.messages = [
        SystemMessage(content=system_prompt)
    ]


# -----------------------------------
# 10. Display previous conversation
# -----------------------------------

for message in st.session_state.messages:

    if isinstance(message, HumanMessage):

        with st.chat_message("user"):
            st.write(message.content)

    elif isinstance(message, AIMessage):

        with st.chat_message("assistant"):
            st.write(message.content)


# -----------------------------------
# 11. Chat input
# -----------------------------------

prompt = st.chat_input("Type your message...")


if prompt:

    # Show user's message
    with st.chat_message("user"):
        st.write(prompt)

    # Add HumanMessage
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

    try:

        # Exactly like your main.py
        response = model.invoke(
            st.session_state.messages[-6:]
        )

        # Extract text
        reply = extract_text(response.content)

        # Add AI response
        st.session_state.messages.append(
            AIMessage(content=reply)
        )

        # Display response
        with st.chat_message("assistant"):
            st.write(reply)

    except Exception as e:

        st.error("Something went wrong.")
        st.error(str(e))