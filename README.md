# 🤖 Custom AI Agent with LangChain, Grok & Real-Time Tools

A custom AI agent built from scratch using **LangChain** and **Grok**, capable of deciding when to use external tools to answer user queries.

The agent currently integrates two real-time tools:

- 🌤️ **Weather Tool** — Fetches current weather information using OpenWeather API
- 📰 **News Tool** — Searches for recent city-related news using Tavily

Unlike using a pre-built agent constructor such as `create_agent()`, this project implements the **agent reasoning loop manually**, providing a clearer understanding of how tool-calling agents work internally.

---

## 🚀 Features

- 🤖 Custom AI agent built from scratch
- 🧠 LLM-based tool selection
- 🔧 Dynamic tool calling
- 🌤️ Real-time weather information
- 📰 Real-time news search
- 👤 Human approval before executing tools
- 🔄 Multi-step agent loop
- 🔐 API keys managed using `.env`
- 🐍 Python + LangChain implementation

---

## 🧠 How the Agent Works

The basic workflow is:

```text
                 User
                   │
                   ▼
             ┌───────────┐
             │   Grok    │
             │    LLM    │
             └─────┬─────┘
                   │
          Does it need a tool?
             /            \
           No              Yes
           │                │
           ▼                ▼
      Final Answer     Tool Request
                            │
                            ▼
                    Human Approval
                       /       \
                     Yes        No
                      │          │
                      ▼          ▼
                 Execute Tool   Denied
                      │
                      ▼
                 Tool Result
                      │
                      ▼
                     Grok
                      │
                      ▼
                Final Answer
```

### Example

User:

```text
What's the temperature in Bhopal?
```

The agent can determine that it needs the weather tool:

```text
Grok → get_weather(city="Bhopal")
```

The user is asked:

```text
Approve tool call? (yes/no)
```

After approval, the weather API is called and the result is returned to Grok.

Grok then generates the final response.

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | LLM and tool integration |
| Grok | Large Language Model |
| LangChain-XAI | Grok integration |
| OpenWeather API | Real-time weather data |
| Tavily | Web/news search |
| python-dotenv | Environment variable management |
| Requests | HTTP API requests |

---

# 🔧 Available Tools

## 1. Weather Tool

The weather tool uses the OpenWeather API to retrieve current weather information.

Example:

```text
User:
What's the weather in Bhopal?

Agent:
Uses get_weather(city="Bhopal")

Tool:
Weather in Bhopal: 23°C, broken clouds

Agent:
The current temperature in Bhopal is 23°C with broken clouds.
```

---

## 2. News Tool

The news tool uses Tavily to search for recent information related to a city.

Example:

```text
User:
What's the latest news in Bhopal?

Agent:
Uses get_news(city="Bhopal")

Tool:
Returns relevant recent news articles.

Agent:
Summarizes the latest news for the user.
```

---

# 🧩 Custom Agent Implementation

One of the main goals of this project is to understand how an agent works **without relying on a high-level agent constructor**.

The tools are stored in a dictionary:

```python
tools = {
    "get_weather": get_weather,
    "get_news": get_news
}
```

The tools are then provided to the LLM:

```python
llm_with_tools = llm.bind_tools(list(tools.values()))
```

The agent repeatedly calls the LLM:

```python
while True:
    response = llm_with_tools.invoke(messages)
```

If the LLM doesn't request a tool:

```python
if not response.tool_calls:
    return response.content
```

The final response is returned.

If the LLM requests a tool, the agent identifies it:

```python
tool_name = tool_call["name"]
tool_args = tool_call["args"]
```

The corresponding Python tool is then executed.

This creates the fundamental agent loop:

```text
LLM
 ↓
Tool Decision
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Response
```

---

# 👤 Human-in-the-Loop

This project also includes a simple human approval mechanism.

Before executing a tool, the agent asks:

```text
Approve tool call? (yes/no)
```

For example:

```text
🔧 Grok wants to use: get_weather
Arguments: {'city': 'Bhopal'}

Approve tool call? (yes/no):
```

If the user enters:

```text
yes
```

the tool is executed.

If the user enters:

```text
no
```

the tool call is rejected and the agent is informed that the tool execution was denied.

This provides a basic **human-in-the-loop safety mechanism**.

---

# 📁 Project Structure

```text
chatmodels/
│
├── agents.py
├── chatbot.py
├── anothertest.py
├── test.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

> `.env` should never be committed to GitHub.

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
XAI_API_KEY=your_xai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Never upload real API keys to GitHub.

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate into the project:

```bash
cd YOUR_REPOSITORY
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or install the main packages directly:

```bash
pip install langchain langchain-xai python-dotenv requests tavily-python
```

---

# ▶️ Running the Agent

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python agents.py
```

The agent will start an interactive conversation.

Example:

```text
You: temperature in Bhopal

🔧 Grok wants to use: get_weather
Arguments: {'city': 'Bhopal'}

Approve tool call? (yes/no): yes

📦 Tool Result:
Weather in Bhopal: 23.15°C, broken clouds

🤖 Agent:
The current temperature in Bhopal is 23.15°C with broken clouds.
```

---

# 💬 Example Queries

The agent can handle queries such as:

### Weather

```text
What's the weather in Bhopal?
```

```text
What is the temperature in Sehore?
```

### News

```text
What's the latest news in Bhopal?
```

```text
Give me recent news about Indore.
```

### Tool selection

```text
Tell me the current weather in Bhopal and also give me the latest news.
```

For the last query, the LLM can determine that **both tools are required**.

---

# 🧠 Key Concepts Learned

This project demonstrates several important concepts in modern AI application development:

### 1. Tool Calling

The LLM can decide that it needs an external function to answer a question.

```text
User → LLM → Tool → LLM → Answer
```

### 2. Agent Loop

An agent isn't simply an LLM.

It contains a loop that allows the model to:

```text
Think/Decide
    ↓
Request Action
    ↓
Execute Action
    ↓
Observe Result
    ↓
Continue
```

### 3. Tool Binding

Tools are connected to the LLM using:

```python
llm.bind_tools(...)
```

### 4. Tool Messages

The result of a tool is sent back to the LLM using a tool message.

```python
ToolMessage(
    content=str(result),
    tool_call_id=tool_id
)
```

### 5. Human-in-the-Loop

The user can approve or reject tool execution.

---

# 🔮 Future Improvements

Planned improvements include:

- [ ] Add more tools
- [ ] Add calculator tool
- [ ] Add web search
- [ ] Add Wikipedia search
- [ ] Add currency conversion
- [ ] Add database tools
- [ ] Add conversation memory
- [ ] Add streaming responses
- [ ] Build a Streamlit interface
- [ ] Add LangGraph-based orchestration
- [ ] Improve error handling
- [ ] Add tool execution logs
- [ ] Deploy the agent

---

# 📌 Why This Project?

This project was built to understand the fundamentals of **Agentic AI** rather than treating an agent as a black box.

Instead of simply writing:

```python
create_agent(...)
```

the project explores what happens underneath:

```text
LLM
 ↓
Tool Selection
 ↓
Tool Call
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

This provides a practical foundation for understanding more advanced frameworks such as **LangGraph** and multi-agent systems.

---

# 👩‍💻 Author

**Smriti Sitoke**

B.Tech — Computer Science & Business Systems

Interested in:

- 🤖 Artificial Intelligence
- 🧠 Machine Learning
- 🔗 Agentic AI
- 📊 Data Analytics
- 💻 Software Development

---

## ⭐ If you found this project useful

Feel free to star ⭐ the repository and explore the code to understand how a custom tool-calling AI agent works.
