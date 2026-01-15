"""Virtual file system tools for context offloading.

This module provides tools for managing a virtual filesystem stored in agent state,
enabling efficient context management during email processing.
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from email_agent_state import EmailAgentState


@tool(parse_docstring=True)
def ls(state: Annotated[EmailAgentState, InjectedState]) -> list[str]:
    """List all files in the virtual filesystem.
    
    Shows what files currently exist in agent memory. Use this to orient
    yourself before other file operations.
    
    Args:
        state: Injected agent state
        

    """
    return list(state.get("files", {}).keys())


@tool(parse_docstring=True)
def read_file(
    file_path: str,
    state: Annotated[EmailAgentState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read content from a file in the virtual filesystem.
    
    Returns file content with line numbers and supports pagination
    for large files to avoid context overflow.
    
    Args:
        file_path: Path to the file to read
        state: Injected agent state
        offset: Line number to start reading from (default: 0)
        limit: Maximum number of lines to read (default: 2000)

    """
    files = state.get("files", {})
    if file_path not in files:
        return f"Error: File '{file_path}' not found. Use ls() to see available files."
    
    content = files[file_path]
    if not content:
        return "File exists but is empty."
    
    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))
    
    if start_idx >= len(lines):
        return f"Error: Offset {offset} exceeds file length ({len(lines)} lines)"
    
    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i][:2000]  # Truncate very long lines
        result_lines.append(f"{i + 1:6d}\t{line_content}")
    
    return "\n".join(result_lines)


@tool(parse_docstring=True)
def write_file(
    file_path: str,
    content: str,
    state: Annotated[EmailAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a file in the virtual filesystem.
    
    Creates new files or completely overwrites existing files.
    Use for storing email context, research findings, or draft notes.
    
    Args:
        file_path: Path where file should be created/overwritten
        content: Complete content to write
        state: Injected agent state
        tool_call_id: Injected tool call identifier
        
    """
    files = state.get("files", {})
    files[file_path] = content
    
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(
                    f"✓ File '{file_path}' written successfully",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )