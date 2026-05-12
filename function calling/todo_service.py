from datetime import datetime
from typing import Optional
import uuid

# In-memory task storage (no database needed for this demo)
tasks: list[dict] = []


def get_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """
    Retrieve tasks with optional filters.
    - status: filter by task status (e.g. 'open', 'in_progress', 'done')
    - task_type: filter by task type (e.g. 'meeting', 'report', 'personal')
    - start_date: return tasks whose start_date >= this value (YYYY-MM-DD)
    - end_date: return tasks whose end_date <= this value (YYYY-MM-DD)
    """
    result = tasks[:]

    if status:
        result = [t for t in result if t.get("status", "").lower() == status.lower()]

    if task_type:
        result = [t for t in result if t.get("task_type", "").lower() == task_type.lower()]

    if start_date:
        result = [t for t in result if t.get("start_date", "") >= start_date]

    if end_date:
        result = [t for t in result if t.get("end_date", "") <= end_date]

    return result


def add_task(
    title: str,
    description: str = "",
    task_type: str = "general",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: str = "open",
) -> dict:
    """
    Add a new task.
    Returns the created task including its generated ID.
    """
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": description,
        "task_type": task_type,
        "start_date": start_date or datetime.today().strftime("%Y-%m-%d"),
        "end_date": end_date or "",
        "status": status,
        "created_at": datetime.now().isoformat(),
    }
    tasks.append(task)
    return task


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    task_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[dict]:
    """
    Update an existing task by ID.
    Only the fields that are provided (not None) will be updated.
    Returns the updated task, or None if not found.
    """
    for task in tasks:
        if task["id"] == task_id:
            if title is not None:
                task["title"] = title
            if description is not None:
                task["description"] = description
            if task_type is not None:
                task["task_type"] = task_type
            if start_date is not None:
                task["start_date"] = start_date
            if end_date is not None:
                task["end_date"] = end_date
            if status is not None:
                task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            return task
    return None


def delete_task(task_id: str) -> bool:
    """
    Delete a task by ID.
    Returns True if deleted, False if not found.
    """
    global tasks
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    return len(tasks) < original_len
