import json
import os
import ssl
import certifi
import httpx
from openai import OpenAI
import todo_service

# Client is created lazily so the server can start even before the key is set
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it before starting the server."
            )
        # Python 3.14 enforces stricter SSL (RFC 5280 key usage).
        # Some CAs in the OpenAI chain don't meet this requirement yet.
        # Disabling SSL verification is acceptable for this local demo.
        http_client = httpx.Client(verify=False)
        _client = OpenAI(api_key=api_key, http_client=http_client)
    return _client

# ─────────────────────────────────────────────
# Tool / function definitions sent to GPT
# ─────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Retrieve tasks from the system with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: 'open', 'in_progress', or 'done'.",
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Filter by task type (e.g. 'meeting', 'report', 'personal').",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Return tasks whose start_date >= this date (YYYY-MM-DD).",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Return tasks whose end_date <= this date (YYYY-MM-DD).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title of the task.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the task.",
                    },
                    "task_type": {
                        "type": "string",
                        "description": "Type of task (e.g. 'meeting', 'report', 'personal', 'general').",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD). Defaults to today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Due / end date (YYYY-MM-DD).",
                    },
                    "status": {
                        "type": "string",
                        "description": "Initial status: 'open', 'in_progress', or 'done'. Defaults to 'open'.",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update fields of an existing task by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique ID of the task to update.",
                    },
                    "title": {"type": "string", "description": "New title."},
                    "description": {"type": "string", "description": "New description."},
                    "task_type": {"type": "string", "description": "New type."},
                    "start_date": {"type": "string", "description": "New start date (YYYY-MM-DD)."},
                    "end_date": {"type": "string", "description": "New end date (YYYY-MM-DD)."},
                    "status": {"type": "string", "description": "New status."},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique ID of the task to delete.",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
]

# Map function names to actual Python callables
FUNCTION_MAP = {
    "get_tasks": todo_service.get_tasks,
    "add_task": todo_service.add_task,
    "update_task": todo_service.update_task,
    "delete_task": todo_service.delete_task,
}

SYSTEM_PROMPT = (
    "You are a helpful personal task-management assistant. "
    "Today'\''s date is {today}. "
    "Use the provided functions to manage tasks on behalf of the user. "
    "Be concise, friendly and answer in the same language the user used."
)


def agent(query: str) -> str:
    """
    Main agent function.
    1. Sends the user query to GPT together with tool definitions.
    2. If GPT requests a function call, executes it.
    3. Sends the function result back to GPT for a human-readable answer.
    4. Returns the final text response.
    """
    from datetime import date

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(today=date.today().isoformat())},
        {"role": "user", "content": query},
    ]

    # ── Step 1: initial GPT call ──
    response = _get_client().chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # ── Step 2: handle tool calls (if any) ──
    if message.tool_calls:
        messages.append(message)  # assistant message with tool_calls

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            func = FUNCTION_MAP.get(func_name)
            if func is None:
                result = {"error": f"Unknown function: {func_name}"}
            else:
                result = func(**func_args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

        # ── Step 3: second GPT call to get human-readable answer ──
        follow_up = _get_client().chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return follow_up.choices[0].message.content

    # No tool call – GPT answered directly
    return message.content
