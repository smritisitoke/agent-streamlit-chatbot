import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from tavily import TavilyClient


load_dotenv(override=True)


# ------------------------------------------------------------
# Tools
# ------------------------------------------------------------

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city in India."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OPENWEATHER_API_KEY is missing."

    url = (
        f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    )
    response = requests.get(url, timeout=15)
    data = response.json()

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return f"Weather in {city}: {description}, {temp}°C"


# Tavily client for news tool
try:
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
except Exception:
    tavily_client = None


@tool
def get_news(city: str) -> str:
    """Get the latest news about a city."""
    if tavily_client is None:
        return "TAVILY_API_KEY is missing."

    response = tavily_client.search(
        query=f"latest news in {city}",
        search_depth="basic",
        max_results=3,
    )
    results = response.get("results", [])

    if not results:
        return f"No news found for {city}"

    news_list = []
    for item in results:
        title = item.get("title", "No title")
        url = item.get("url", "")
        snippet = item.get("content", "")
        news_list.append(f"- {title}\n  URL: {url}\n  Summary: {snippet[:200]}...")

    return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)


# ------------------------------------------------------------
# Groq model
# ------------------------------------------------------------

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=api_key,
)


tools = {
    "get_weather": get_weather,
    "get_news": get_news,
}

llm_with_tools = llm.bind_tools(list(tools.values()))


MIN_SECONDS_BETWEEN_CALLS = 0.5
_last_call_time = 0.0


def rate_limited_invoke(llm_obj, messages, retries=3):
    global _last_call_time

    for attempt in range(retries):
        elapsed = time.time() - _last_call_time
        if elapsed < MIN_SECONDS_BETWEEN_CALLS:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)

        try:
            result = llm_obj.invoke(messages)
            _last_call_time = time.time()
            return result
        except Exception as e:
            _last_call_time = time.time()
            is_rate_limit = "429" in str(e) or "rate_limited" in str(e).lower()
            if is_rate_limit and attempt < retries - 1:
                wait_time = 3 * (attempt + 1)
                time.sleep(wait_time)
                continue
            raise


def run_agent(user_input: str) -> str:
    messages = [HumanMessage(content=user_input)]

    for _ in range(6):
        try:
            response = rate_limited_invoke(llm_with_tools, messages)
        except Exception as e:
            return f"⚠️ Failed to get a response from Groq: {e}"

        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id")

            if tool_name not in tools:
                messages.append(
                    ToolMessage(
                        content=f"Tool '{tool_name}' not found.",
                        tool_call_id=tool_id,
                    )
                )
                continue

            result = tools[tool_name].invoke(tool_args)
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id,
                )
            )

    return "I reached the maximum tool loop. Please try again."


# ------------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------------

st.set_page_config(page_title="Groq City Agent", page_icon="🤖", layout="centered")
st.title("🤖 Groq City Agent")
st.caption("Ask for the weather or the latest city news.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant. "
                "Use tools when needed for weather or city news. "
                "Answer briefly and clearly."
            )
        )
    ]

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

prompt = st.chat_input("Ask about weather or news in a city...")

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Thinking..."):
        answer = run_agent(prompt)

    st.session_state.messages.append(AIMessage(content=answer))

    with st.chat_message("assistant"):
        st.write(answer)
