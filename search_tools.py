"""Search and research tools for the Deep Agent Email Assistant.

This module provides web search capabilities using Tavily API for gathering
external information needed to craft informed email responses.
"""

import os
from datetime import datetime
from typing import Annotated, Literal

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolArg, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from email_agent_state import EmailAgentState
from prompts import get_today_str

# def get_today_str() -> str:
#     """Get current date in a human-readable format."""
#     return datetime.now().strftime("%a %b %d, %Y")


def mock_tavily_search(query: str, max_results: int = 2) -> dict:
    """Mock implementation of Tavily search for demonstration.
    
    In production, this would call the actual Tavily API.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        Mock search results
    """
    # Mock results based on common queries
    mock_results = {
        "results": [
            {
                "title": f"Search Result for: {query}",
                "url": f"https://example.com/search/{query.replace(' ', '-')}",
                "content": f"This is a mock search result for '{query}'. In production, this would contain actual search results from Tavily API.",
                "score": 0.95
            },
            {
                "title": f"Additional Information: {query}",
                "url": f"https://example.com/info/{query.replace(' ', '-')}",
                "content": f"Additional context and information related to '{query}'. This demonstrates how multiple search results would be processed.",
                "score": 0.87
            }
        ][:max_results]
    }
    return mock_results


@tool(parse_docstring=True)
def web_search(
    query: str,
    state: Annotated[EmailAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    max_results: Annotated[int, InjectedToolArg] = 2,
) -> Command:
    """Search the web for information and save results to files.

    Performs web search and saves detailed results to the virtual filesystem
    for context offloading. Returns a summary to help the agent decide next steps.

    Args:
        query: Search query to execute
        state: Injected agent state for file storage
        tool_call_id: Injected tool call identifier
        max_results: Maximum number of results (default: 2)

    """
    # Execute search (mock implementation)
    search_results = mock_tavily_search(query, max_results=max_results)
    
    # Prepare files and summaries
    files = state.get("files", {})
    saved_files = []
    summaries = []
    
    for i, result in enumerate(search_results.get("results", [])):
        # Create filename based on query and index
        filename = f"search_{query.replace(' ', '_')[:30]}_{i+1}.md"
        
        # Create file content
        file_content = f"""# Search Result: {result['title']}

**URL:** {result['url']}
**Query:** {query}
**Date:** {get_today_str()}
**Relevance Score:** {result.get('score', 'N/A')}

## Content
{result['content']}

---
*This information can be used to inform email responses.*
"""
        
        files[filename] = file_content
        saved_files.append(filename)
        summaries.append(f"- {filename}: {result['title']}")
    
    # Create summary for tool message
    summary_text = f"""🔍 Found {len(search_results.get('results', []))} result(s) for '{query}':

{chr(10).join(summaries)}

Files saved: {', '.join(saved_files)}
💡 Use read_file() to access full details when crafting your response."""
    
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(summary_text, tool_call_id=tool_call_id)
            ]
        }
    )


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection during email processing.

    Use this tool to pause and reflect on:
    - What information have I gathered so far?
    - What do I still need to know?
    - Am I ready to compose the response?
    - What should be my next step?

    Args:
        reflection: Your detailed reflection on progress and next steps

    """
    return f"✓ Reflection recorded: {reflection[:100]}..."