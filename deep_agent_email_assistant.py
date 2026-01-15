"""Main implementation of the Deep Agent Email Assistant.

This module brings together all components to create a functional
email processing agent with planning, research, and response capabilities.
"""

import json
from typing import Optional

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from email_agent_state import EmailAgentState
from email_tools import read_latest_email, write_email_draft, get_email_context
from search_tools import web_search, think_tool
from file_tools import ls, read_file, write_file
from todo_tools import write_todos, read_todos
from subagent_tools import create_task_delegation_tool
from prompts import COORDINATOR_PROMPT, RESEARCH_AGENT_PROMPT, RESPONSE_AGENT_PROMPT
from subagent_tools import SubAgent

subagents: list[SubAgent] = [
    {
        "name": "research-agent",
        "description": "Gather and summarize information from the web",
        "prompt": RESEARCH_AGENT_PROMPT,
        "tools": ["web_search", "think_tool", "ls", "read_file", "write_file"]
    },
    {
        "name": "response-agent",
        "description": "Compose professional email responses",
        "prompt": RESPONSE_AGENT_PROMPT,
        "tools": ["get_email_context", "ls", "read_file", "think_tool", "write_file"]
    }
]


def create_email_agent(model_name: str = "anthropic:claude-sonnet-4-20250514"):
    """Create the Deep Agent Email Assistant.
    
    This function assembles all tools and creates the main coordinator agent
    with sub-agent delegation capabilities.
    
    Args:
        model_name: Language model to use (default: Claude Sonnet 4)
        
    Returns:
        Configured agent ready to process emails
    """
    # Initialize the language model
    model = init_chat_model(model_name)
    
    # Collect base tools (available to coordinator)
    base_tools = [
        # Email tools
        read_latest_email,
        write_email_draft,
        get_email_context,
        
        # Research tools
        web_search,
        think_tool,
        
        # File system tools
        ls,
        read_file,
        write_file,
        
        # TODO management
        write_todos,
        read_todos,
    ]
    
    # Create task delegation tool (this creates sub-agents internally)
    task_tool = create_task_delegation_tool(
        tools=base_tools,
        subagents=subagents,
        model=model,
        state_schema=EmailAgentState
    )
    
    # Add task tool to coordinator's tools
    coordinator_tools = base_tools + [task_tool]
    
    # Create the main coordinator agent
    agent = create_react_agent(
        model,
        prompt=COORDINATOR_PROMPT,
        tools=coordinator_tools,
        state_schema=EmailAgentState
    )
    
    return agent


def process_email(
    agent,
    instruction: Optional[str] = None,
    verbose: bool = True
) -> dict:
    """Process an email using the Deep Agent.
    
    Args:
        agent: The configured email agent
        instruction: Optional specific instruction (default: process latest email)
        verbose: Whether to print progress (default: True)
        
    Returns:
        Dictionary containing:
        - email: The processed email
        - draft: The composed response
        - files: Research and context files
        - messages: Conversation history
    """
    if instruction is None:
        instruction = "Please process the latest email and compose an appropriate response."
    
    # Initialize state
    initial_state = {
        "messages": [{"role": "user", "content": instruction}]
    }
    
    if verbose:
        print("🤖 Deep Agent Email Assistant Starting...")
        print(f"📝 Instruction: {instruction}")
        print("=" * 60)
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    if verbose:
        print("\n" + "=" * 60)
        print("✅ Processing Complete")
        print("=" * 60)
    
    # Extract results
    output = {
        "email": result.get("current_email"),
        "draft": result.get("email_draft"),
        "files": result.get("files", {}),
        "todos": result.get("todos", []),
        "messages": result.get("messages", [])
    }
    
    return output


def format_output(result: dict, show_files: bool = False) -> str:
    """Format the agent output for display.
    
    Args:
        result: Output from process_email()
        show_files: Whether to include file contents (default: False)
        
    Returns:
        Formatted string representation
    """
    output = []
    
    output.append("=" * 80)
    output.append("DEEP AGENT EMAIL ASSISTANT - RESULTS")
    output.append("=" * 80)
    
    # Email Context
    if result.get("email"):
        email = result["email"]
        output.append("\n📧 PROCESSED EMAIL:")
        output.append(f"From: {email['from_address']}")
        output.append(f"Subject: {email['subject']}")
        output.append(f"Received: {email['received_at']}")
    
    # Email Draft
    if result.get("draft"):
        output.append("\n✉️ COMPOSED RESPONSE:")
        output.append("-" * 80)
        output.append(result["draft"])
        output.append("-" * 80)
    
    # TODOs (if any)
    if result.get("todos"):
        output.append("\n📋 WORKFLOW TODOS:")
        for i, todo in enumerate(result["todos"], 1):
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            emoji = status_emoji.get(todo["status"], "❓")
            output.append(f"{i}. {emoji} {todo['content']} ({todo['status']})")
    
    # Files
    if result.get("files"):
        output.append(f"\n📁 GENERATED FILES ({len(result['files'])} total):")
        for filename in result["files"].keys():
            output.append(f"  - {filename}")
        
        if show_files:
            output.append("\n📄 FILE CONTENTS:")
            for filename, content in result["files"].items():
                output.append(f"\n--- {filename} ---")
                output.append(content[:500] + "..." if len(content) > 500 else content)
    
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)


def export_to_json(result: dict, filepath: str = "email_result.json"):
    """Export results to JSON file.
    
    Args:
        result: Output from process_email()
        filepath: Where to save the JSON (default: email_result.json)
    """
    # Convert to JSON-serializable format
    export_data = {
        "email": result.get("email"),
        "draft": result.get("draft"),
        "files": result.get("files", {}),
        "todos": result.get("todos", []),
        "message_count": len(result.get("messages", []))
    }
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✓ Results exported to {filepath}")
