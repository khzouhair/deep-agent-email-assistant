"""TODO management tools for task planning and tracking.

This module provides tools for creating and managing structured task lists
that enable the agent to plan email processing workflows systematically.
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from email_agent_state import EmailAgentState, Todo


@tool(parse_docstring=True)
def write_todos(
    todos: list[Todo],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create or update the agent's TODO list for workflow planning.
    
    Use this tool to break down email processing into manageable steps:
    - Read and analyze email
    - Research necessary information
    - Delegate tasks to sub-agents
    - Compose and review draft
    - Finalize response
    
    Structure:
    - Only one task should be 'in_progress' at a time
    - Mark tasks 'completed' immediately when done
    - Keep the list focused and actionable
    
    Args:
        todos: List of Todo items with content and status
        tool_call_id: Injected tool call identifier
        
    """
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(
                    f"✓ TODO list updated with {len(todos)} tasks",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )


@tool(parse_docstring=True)
def read_todos(
    state: Annotated[EmailAgentState, InjectedState],
) -> str:
    """Read the current TODO list from agent state.
    
    Use this to review remaining tasks and track progress through
    the email processing workflow.
    
    Args:
        state: Injected agent state
        
    """
    todos = state.get("todos", [])
    if not todos:
        return "No TODOs currently in the list."
    
    result = "Current TODO List:\n"
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅"
    }
    
    for i, todo in enumerate(todos, 1):
        emoji = status_emoji.get(todo["status"], "❓")
        result += f"{i}. {emoji} {todo['content']} ({todo['status']})\n"
    
    return result.strip()