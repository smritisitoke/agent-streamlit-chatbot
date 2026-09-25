from dotenv import load_dotenv

import os
import time
import requests

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(override=True)


# =========================================================
# 🌦️ WEATHER TOOL
# =========================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather of a city in India."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = (
        f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    return f"Weather in {city}: {description}, {temp}°C"


# =========================================================
# 📰 NEWS TOOL
# =========================================================

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def get_news(city: str) -> str:
    """Get the latest news about a city."""

    response = tavily_client.search(
        query=f"latest news in {city}",
        search_depth="basic",
        max_results=3
    )

    results = response.get("results", [])

    if not results:
        return f"No news found for {city}"

    news_list = []

    for r in results:

        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")

        news_list.append(
            f"- {title}\n"
            f"  URL: {url}\n"
            f"  Summary: {snippet[:200]}..."
        )

    return (
        f"Latest news in {city}:\n\n"
        + "\n\n".join(news_list)
    )


# =========================================================
# 🧠 GROQ LLM
# =========================================================
#
# Requires GROQ_API_KEY in your .env file.
# Get a free key at: https://console.groq.com/keys
#
# llama-3.3-70b-versatile supports tool calling and has a generous
# free tier (as of writing: 30 requests/min, ~12-14k tokens/min).

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)


# =========================================================
# 🔧 TOOLS
# =========================================================

tools = {
    "get_weather": get_weather,
    "get_news": get_news
}


# =========================================================
# 🔗 BIND TOOLS TO MISTRAL
# =========================================================

llm_with_tools = llm.bind_tools(
    list(tools.values())
)


# =========================================================
# ⏱️ RATE-LIMITED / RETRY-SAFE INVOKE
# =========================================================
#
# Groq's free tier is much more generous than Mistral's free tier, but
# it still has limits (check https://console.groq.com/settings/limits
# for your account's exact numbers — commonly ~30 requests/min for
# llama-3.3-70b-versatile). Your agent loop can fire multiple LLM calls
# back-to-back within the same turn (once for the initial response, then
# again after each tool result comes back), so a small buffer between
# calls plus a retry-on-429 is kept here as a safety net.

MIN_SECONDS_BETWEEN_CALLS = 0.5  # small buffer; Groq's limits are looser than Mistral's
_last_call_time = 0.0


def rate_limited_invoke(llm_obj, messages, retries=3):
    global _last_call_time

    for attempt in range(retries):

        # --- enforce minimum spacing before every call ---
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
                wait_time = 3 * (attempt + 1)  # backoff: 3s, 6s, 9s...
                print(f"\n⏳ Rate limited by Groq. Waiting {wait_time}s and retrying "
                      f"(attempt {attempt + 1}/{retries})...")
                time.sleep(wait_time)
                continue

            # Not a rate-limit error, or out of retries -> re-raise
            raise


# =========================================================
# 🤖 OUR OWN AGENT
# =========================================================

def my_agent(user_input):

    messages = [
        HumanMessage(content=user_input)
    ]

    while True:

        # -----------------------------------------
        # STEP 1: Ask Groq what to do
        # -----------------------------------------

        try:
            response = rate_limited_invoke(llm_with_tools, messages)
        except Exception as e:
            return f"⚠️ Failed to get a response from Groq: {e}"

        # Save Groq's response
        messages.append(response)


        # -----------------------------------------
        # STEP 2: Check if Groq wants a tool
        # -----------------------------------------

        if not response.tool_calls:

            # No tool required
            # Groq has generated final answer

            return response.content


        # -----------------------------------------
        # STEP 3: Execute requested tools
        # -----------------------------------------

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            print(
                f"\n🔧 Groq wants to use: {tool_name}"
            )

            print(
                f"Arguments: {tool_args}"
            )


            # -----------------------------------------
            # HUMAN APPROVAL
            # -----------------------------------------

            approval = input(
                "Approve tool call? (yes/no): "
            )


            if approval.lower() != "yes":

                tool_result = ToolMessage(
                    content="Tool call denied by user.",
                    tool_call_id=tool_id
                )

                messages.append(tool_result)

                continue


            # -----------------------------------------
            # FIND TOOL
            # -----------------------------------------

            selected_tool = tools[tool_name]


            # -----------------------------------------
            # EXECUTE TOOL
            # -----------------------------------------

            result = selected_tool.invoke(
                tool_args
            )


            print("\n Tool Result:")
            print(result)


            # -----------------------------------------
            # SEND RESULT BACK TO GROQ
            # -----------------------------------------

            tool_result = ToolMessage(
                content=str(result),
                tool_call_id=tool_id
            )

            messages.append(tool_result)


# =========================================================
# 💬 CHAT LOOP
# =========================================================

print("\n My Groq City Agent")
print("Type 'exit' to quit.\n")


while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Agent stopped.")
        break

    answer = my_agent(user_input)

    print("\n🤖 Agent:", answer)