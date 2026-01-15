"""Email management tools for the Deep Agent Email Assistant.

This module provides tools for reading emails and composing responses.
"""

from typing import Annotated
from datetime import datetime

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from email_agent_state import EmailAgentState, Email


# Mock email database
MOCK_EMAILS = [
    {
        "id": "email_001",
        "from_address": "john.doe@techcorp.com",
        "subject": "Partnership Proposal - AI Integration",
        "body": """Hi there,

I hope this email finds you well. I'm reaching out from TechCorp regarding a potential partnership opportunity.

We're looking to integrate advanced AI capabilities into our customer service platform, and we've been impressed by your company's work in the field. We currently handle about 50,000 customer inquiries per month and are looking for solutions that can:

1. Automate routine responses
2. Provide intelligent routing
3. Maintain high customer satisfaction

Would you be available for a call next week to discuss this further? We're particularly interested in understanding your pricing models and implementation timelines.

Looking forward to hearing from you.

Best regards,
John Doe
Director of Technology
TechCorp Inc.
john.doe@techcorp.com
""",
        "received_at": "2026-01-14T09:30:00Z"
    },
    {
        "id": "email_002",
        "from_address": "sarah.smith@startup.io",
        "subject": "Research Collaboration Inquiry",
        "body": """Hello,

I'm a PhD student at Stanford researching multi-agent systems and I came across your recent work on context isolation in agent architectures.

I'm wondering if you'd be interested in collaborating on a research paper exploring scalability challenges in production LLM agent deployments. I have some interesting findings from our lab that complement your approach.

Would you be open to a brief discussion about this?

Thanks,
Sarah Smith
PhD Candidate, Computer Science
Stanford University
""",
        "received_at": "2026-01-14T14:15:00Z"
    }
]


@tool(parse_docstring=True)
def read_latest_email(
    state: Annotated[EmailAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Read the most recent email from the inbox.

    Retrieves the latest email and stores it in the agent state for processing.
    In production, this would connect to an actual email API (Gmail, Outlook, etc.).

    Args:
        state: Injected agent state
        tool_call_id: Injected tool call identifier

    """
    # Get the most recent email (mock implementation)
    latest_email = MOCK_EMAILS[-1]
    
    email_obj: Email = {
        "id": latest_email["id"],
        "from_address": latest_email["from_address"],
        "subject": latest_email["subject"],
        "body": latest_email["body"],
        "received_at": latest_email["received_at"]
    }
    
    # Format email for display
    email_summary = f"""📧 Latest Email Retrieved:

**From:** {email_obj['from_address']}
**Subject:** {email_obj['subject']}
**Received:** {email_obj['received_at']}

**Body:**
{email_obj['body'][:300]}...

Email stored in state for processing."""

    return Command(
        update={
            "current_email": email_obj,
            "messages": [
                ToolMessage(email_summary, tool_call_id=tool_call_id)
            ]
        }
    )


@tool(parse_docstring=True)
def write_email_draft(
    draft_content: str,
    state: Annotated[EmailAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write or update the email response draft.

    Creates a properly formatted email draft with appropriate headers and signature.
    This draft can be reviewed and edited before sending.

    Args:
        draft_content: The main body content of the email response
        state: Injected agent state
        tool_call_id: Injected tool call identifier

    """
    current_email = state.get("current_email")
    
    if not current_email:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        "Error: No email in context. Use read_latest_email first.",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )
    
    # Format the draft with proper email structure
    draft = f"""To: {current_email['from_address']}
Subject: Re: {current_email['subject']}

{draft_content}

---
This draft is ready for review and sending.
"""
    
    return Command(
        update={
            "email_draft": draft,
            "messages": [
                ToolMessage(
                    f"✅ Email draft created and saved.\n\nPreview:\n{draft[:200]}...",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )


@tool(parse_docstring=True)
def get_email_context(
    state: Annotated[EmailAgentState, InjectedState],
) -> str:
    """Get current email context for analysis.

    Retrieves the current email being processed from state.
    Useful for sub-agents that need email context.

    Args:
        state: Injected agent state

    """
    current_email = state.get("current_email")
    
    if not current_email:
        return "No email currently loaded in context."
    
    return f"""Current Email Context:

From: {current_email['from_address']}
Subject: {current_email['subject']}
Received: {current_email['received_at']}

Body:
{current_email['body']}
"""