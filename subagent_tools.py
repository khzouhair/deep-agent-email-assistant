"""Task delegation tools for creating specialized sub-agents with isolated contexts.

This module implements the sub-agent pattern for context isolation,
allowing the coordinator to delegate specialized tasks to focused agents.
"""

from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.types import Command

from email_agent_state import EmailAgentState
from prompts import TASK_DESCRIPTION_PREFIX


class SubAgent(TypedDict):
    """Configuration for a specialized sub-agent."""

    name: str
    description: str
    prompt: str
    tools: NotRequired[list[str]]


def create_task_delegation_tool(tools, subagents: list[SubAgent], model, state_schema=EmailAgentState):
    """Create a task delegation tool that spawns specialized sub-agents.
    
    This implements context isolation by creating sub-agents that only see
    their specific task description, preventing context pollution.
    
    Args:
        tools: List of available tools
        model: Language model to use for agents
        state_schema: State schema (default: EmailAgentState)
        
    Returns:
        A 'task' tool that can delegate to specialized sub-agents
    """
    # Build tool registry
    tools_by_name = {}
    for tool_obj in tools:
        if not isinstance(tool_obj, BaseTool):
            tool_obj = tool(tool_obj)
        tools_by_name[tool_obj.name] = tool_obj
    

    agents={}
    # Create specialized sub-agents based on configurations
    for _agent in subagents:
        if "tools" in _agent:
            # Use specific tools if specified
            _tools = [tools_by_name[t] for t in _agent["tools"]]
        else:
            # Default to all tools
            _tools = tools
        agents[_agent["name"]] = create_react_agent(
            model, prompt=_agent["prompt"], tools=_tools, state_schema=state_schema
        )

    # Generate description of available sub-agents for the tool description
    other_agents_string = [
        f"- {_agent['name']}: {_agent['description']}" for _agent in subagents
    ]

    
    @tool(description=TASK_DESCRIPTION_PREFIX.format(
        other_agents="\n".join(other_agents_string)
    ))
    def task(
        description: str,
        subagent_type: str,
        state: Annotated[EmailAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Delegate a task to a specialized sub-agent with isolated context.
        
        Args:
            description: Clear, complete description of the task
            subagent_type: Type of agent to use ('research-agent' or 'response-agent')
            state: Injected agent state
            tool_call_id: Injected tool call identifier
            
        Returns:
            Command updating state with sub-agent results
        """
        # Validate requested agent type exists
        if subagent_type not in agents:
            return f"Error: invoked agent of type {subagent_type}, the only allowed types are {[f'`{k}`' for k in agents]}"
        
        # Get the requested sub-agent
        sub_agent = agents[subagent_type]
        
        # Create isolated context - key to preventing context pollution
        # Sub-agent only sees the task description, not parent history
        isolated_state = state.copy()
        isolated_state["messages"] = [{"role": "user", "content": description}]
        
        # Execute sub-agent in isolation
        result = sub_agent.invoke(isolated_state)
        
        # Merge results back to parent context
        return Command(
            update={
                "files": result.get("files", {}),  # Merge file changes
                "messages": [
                    ToolMessage(
                        result["messages"][-1].content,
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )
    
    return task