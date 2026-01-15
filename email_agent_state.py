"""State management for Deep Agent Email Assistant.

This module defines the extended agent state structure that supports:
- Email tracking and context
- Task planning through TODO lists
- Virtual file system for context offloading
- Email drafts and research findings
"""

from typing import Annotated, Literal, NotRequired
from typing_extensions import TypedDict

from langgraph.prebuilt.chat_agent_executor import AgentState


class Todo(TypedDict):
    """A structured task item for tracking email processing workflow.

    Attributes:
        content: Short, specific description of the task
        status: Current state - pending, in_progress, or completed
    """
    content: str
    status: Literal["pending", "in_progress", "completed"]


class Email(TypedDict):
    """Email message structure.
    
    Attributes:
        id: Unique email identifier
        from_address: Sender email address
        subject: Email subject line
        body: Email content
        received_at: Timestamp of receipt
    """
    id: str
    from_address: str
    subject: str
    body: str
    received_at: str


def file_reducer(left, right):
    """Merge two file dictionaries, with right side taking precedence.

    Args:
        left: Left side dictionary (existing files)
        right: Right side dictionary (new/updated files)

    Returns:
        Merged dictionary with right values overriding left values
    """
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return {**left, **right}


class EmailAgentState(AgentState):
    """Extended agent state for email processing workflows.

    Inherits from LangGraph's AgentState and adds:
    - todos: List of Todo items for task planning
    - files: Virtual file system for storing research and context
    - current_email: The email being processed
    - email_draft: The draft response being composed
    """
    todos: NotRequired[list[Todo]]
    files: Annotated[NotRequired[dict[str, str]], file_reducer]
    current_email: NotRequired[Email]
    email_draft: NotRequired[str]