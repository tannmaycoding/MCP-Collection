import os
import datetime
import pandas as pd
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
# --- Init MCP ---
mcp = FastMCP("todo-mcp")

TASKS_FILE = os.environ.get("TASKS_FILE")


def initialize_tasks_file():
    """Initializes the tasks.csv file if it doesn't exist."""
    if not os.path.exists(TASKS_FILE):
        df = pd.DataFrame(columns=["Date", "Time", "Task", "Status"])
        df.to_csv(TASKS_FILE, index=False)


initialize_tasks_file()


# --- Helper Functions for Data Persistence ---
def read_tasks():
    try:
        return pd.read_csv(TASKS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["Date", "Time", "Task", "Status"])


def write_tasks(df):
    df.to_csv(TASKS_FILE, index=False)


# --- Tools ---

@mcp.tool()
def add_task(task: str, status: str = "Not Started") -> str:
    """
    Add a new task to the to-do list.
    """
    if not task:
        return "❌ Task cannot be empty."

    df = read_tasks()
    df2 = pd.DataFrame([{
        "Date": datetime.datetime.now().strftime("%d/%m/%Y"),
        "Time": datetime.datetime.now().strftime("%H:%M"),
        "Task": task,
        "Status": status
    }])
    df3 = pd.concat([df, df2], ignore_index=True)
    write_tasks(df3)
    return f"✅ Task '{task}' added successfully with status '{status}'."


@mcp.tool()
def list_tasks() -> list:
    """
    List all tasks in reverse chronological order.
    """
    df = read_tasks()
    if df.empty:
        return []
    return df[::-1].to_dict(orient="records")


@mcp.tool()
def modify_task(index: int, new_status: str) -> str:
    """
    Modify the status of a task by its index (0-based, newest task = 0).
    """
    df = read_tasks()
    if df.empty:
        return "❌ No tasks found."
    df = df[::-1].reset_index(drop=True)  # reverse for display order
    if index < 0 or index >= len(df):
        return f"❌ Invalid index {index}. Valid range: 0 to {len(df) - 1}."
    df.at[index, "Status"] = new_status
    # Reverse back before saving
    df = df[::-1]
    write_tasks(df)
    return f"✅ Task '{df.iloc[::-1].iloc[index]['Task']}' updated to '{new_status}'."


@mcp.tool()
def delete_task(index: int) -> str:
    """
    Delete a task by its index (0-based, newest task = 0).
    """
    df = read_tasks()
    if df.empty:
        return "❌ No tasks found."
    df = df[::-1].reset_index(drop=True)
    if index < 0 or index >= len(df):
        return f"❌ Invalid index {index}. Valid range: 0 to {len(df) - 1}."
    task = df.at[index, "Task"]
    df = df.drop(index).reset_index(drop=True)
    # Reverse back before saving
    df = df[::-1]
    write_tasks(df)
    return f"🗑️ Task '{task}' deleted successfully."


# --- Run server ---
if __name__ == "__main__":
    mcp.run()
