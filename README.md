# 🤖 AI Todo Agent — Function Calling Project

An intelligent, conversational **task management assistant** powered by **OpenAI function calling**.  
Talk to it naturally — in any language — and it will add, update, list, or delete your tasks automatically.

---

## 🧠 How It Works

The app is split into two parts:

```
┌─────────────────────┐        ┌──────────────────────────┐
│   React Frontend    │ ──────▶│  FastAPI Backend (Python) │
│  (Chat UI / Vite)   │◀────── │  + OpenAI GPT-4o Agent   │
└─────────────────────┘  HTTP  └──────────────────────────┘
```

1. 💬 You type a message in the chat (e.g. *"Add a meeting for tomorrow"*)
2. 🌐 The frontend sends it to the FastAPI backend via `/chat`
3. 🤖 The backend passes it to **GPT-4o** along with tool definitions
4. ⚙️ GPT decides which function to call (`add_task`, `get_tasks`, `update_task`, `delete_task`)
5. 🐍 Python executes the function on the in-memory task store
6. 📨 The result is sent back to GPT, which writes a friendly human reply
7. ✅ The reply is displayed in the chat UI

---

## 📁 Project Structure

```
function calling/
├── main.py            # FastAPI server — exposes the /chat endpoint
├── agent_service.py   # OpenAI agent logic + function/tool definitions
├── todo_service.py    # In-memory task CRUD operations
└── client/            # React + Vite frontend
    ├── src/
    │   ├── App.jsx    # Chat UI component
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

---

## 🚀 Getting Started

### 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- An **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))

---

### 🔧 Backend Setup

```bash
# 1. Navigate to the backend folder
cd "function calling"

# 2. Install Python dependencies
pip install fastapi uvicorn openai httpx certifi pydantic

# 3. Set your OpenAI API key
$env:OPENAI_API_KEY = "sk-..."       # PowerShell
# or
set OPENAI_API_KEY=sk-...            # CMD

# 4. Start the backend server
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

---

### 🎨 Frontend Setup

Open a **second terminal**:

```bash
# 1. Navigate to the client folder
cd "function calling/client"

# 2. Install npm dependencies
npm install

# 3. Start the dev server
npm run dev
```

The chat UI will be available at: `http://localhost:5173`

---

## 💬 Example Conversations

Here are some things you can say to the agent:

---

### ➕ Adding Tasks

> **You:** Add a task to prepare the quarterly report by May 20th  
> **Agent:** ✅ Done! I've added "Prepare quarterly report" with a due date of 2025-05-20.

> **You:** Schedule a team meeting for next Monday, type: meeting  
> **Agent:** 📅 Added a meeting task for next Monday!

---

### 📋 Listing Tasks

> **You:** Show me all my open tasks  
> **Agent:** Here are your open tasks: 1. Prepare quarterly report (due May 20)...

> **You:** What meetings do I have?  
> **Agent:** You have 1 meeting task: "Team meeting" scheduled for...

> **You:** Show tasks due before May 31  
> **Agent:** Here are tasks due before May 31st: ...

---

### ✏️ Updating Tasks

> **You:** Mark "quarterly report" as done  
> **Agent:** ✅ Updated! The task is now marked as done.

> **You:** Change the due date of task abc12345 to June 1  
> **Agent:** 📝 Due date updated to 2025-06-01.

---

### 🗑️ Deleting Tasks

> **You:** Delete the meeting task  
> **Agent:** 🗑️ Done, the meeting task has been deleted.

---

## ⚙️ Available Agent Tools

| 🔧 Function | 📝 What it does |
|---|---|
| `get_tasks` | List tasks, with optional filters (status, type, date range) |
| `add_task` | Create a new task with title, description, type, dates, and status |
| `update_task` | Update any field of an existing task by ID |
| `delete_task` | Remove a task permanently by ID |

### Task fields:
- **title** — Short name for the task *(required)*
- **description** — More detail about the task
- **task_type** — Category: `meeting`, `report`, `personal`, `general`, etc.
- **start_date** — When it starts (`YYYY-MM-DD`, defaults to today)
- **end_date** — Due date (`YYYY-MM-DD`)
- **status** — `open`, `in_progress`, or `done`

---

## 🌍 Multi-language Support

The agent automatically **responds in the same language you write in**.  
You can chat in English, Hebrew, French, Spanish, or any other language — GPT adapts automatically!

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🤖 AI Model | OpenAI GPT-4o (function calling) |
| 🐍 Backend | Python + FastAPI + Uvicorn |
| ⚛️ Frontend | React 18 + Vite |
| 💾 Storage | In-memory (no database required) |

---

## ⚠️ Notes

- Tasks are stored **in memory only** — they reset when the server restarts. This is by design for a simple demo.
- Make sure both the backend (`port 8000`) and frontend (`port 5173`) are running at the same time.
- The Vite dev server is pre-configured to **proxy `/chat` requests** to the backend automatically.
