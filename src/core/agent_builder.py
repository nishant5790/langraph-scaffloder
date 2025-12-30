"""Core LangGraph agent builder for dynamic agent creation."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import Tool

from .model_factory import ModelFactory
from .tools import ToolManager
from ..models import AgentConfig, AgentStatus, Agent


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: List[BaseMessage]
    iteration_count: int
    tool_calls: List[Dict[str, Any]]
    session_id: str
    context: Dict[str, Any]


class LangGraphAgentBuilder:
    """Builder for creating LangGraph-based agents dynamically."""
    
    def __init__(self):
        self.tool_manager = ToolManager()
        self.agents: Dict[str, Any] = {}
    
    def build_agent(self, config: AgentConfig) -> str:
        """Build a new LangGraph agent from configuration.
        
        Args:
            config: Agent configuration
            
        Returns:
            Agent ID
        """
        # Validate model configuration
        ModelFactory.validate_model_config(config.model)
        
        # Create unique agent ID
        agent_id = str(uuid.uuid4())
        
        # Create the language model
        llm = ModelFactory.create_model(config.model)
        
        # Create tools
        tools = self.tool_manager.create_tools_from_configs(config.tools)
        
        # Create system message with instructions
        system_message = f"""You are {config.name}. {config.description}

{config.instructions}

You have access to the following tools: {[tool.name for tool in tools] if tools else 'No tools available'}

Important guidelines:
- Follow the instructions carefully
- Use tools when appropriate to help answer questions
- Provide clear and helpful responses
- If you need to use a tool, call it and wait for the result before continuing
- Maximum iterations allowed: {config.max_iterations}
"""
        
        # Build the agent using create_react_agent for simplicity and reliability
        if tools:
            # Use the prebuilt ReAct agent for tool-enabled agents
            agent_graph = create_react_agent(llm, tools, prompt=system_message)
        else:
            # For agents without tools, create a simple graph
            workflow = StateGraph(AgentState)
            workflow.add_node("agent", self._simple_agent_node(llm, system_message))
            workflow.set_entry_point("agent")
            workflow.add_edge("agent", END)
            agent_graph = workflow.compile()
        
        # Store agent information
        agent = Agent(
            id=agent_id,
            name=config.name,
            description=config.description,
            config=config,
            status=AgentStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.agents[agent_id] = {
            "agent": agent,
            "graph": agent_graph,
            "llm": llm,
            "tools": tools,
            "system_message": system_message
        }
        
        return agent_id
    
    def _simple_agent_node(self, llm: Any, system_message: str):
        """Create a simple agent node for non-tool agents.
        
        Args:
            llm: Language model
            system_message: System instructions
            
        Returns:
            Agent node function
        """
        def agent(state: AgentState) -> AgentState:
            # Prepare messages with system instructions
            messages = [HumanMessage(content=system_message)] + state["messages"]
            
            # Get response from LLM
            response = llm.invoke(messages)
            
            # Update state
            return {
                **state,
                "messages": state["messages"] + [response],
                "iteration_count": state["iteration_count"] + 1
            }
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent information or None if not found
        """
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Agent]:
        """List all agents.
        
        Returns:
            List of agent information
        """
        return [info["agent"] for info in self.agents.values()]
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if deleted, False if not found
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def execute_agent(
        self, 
        agent_id: str, 
        input_message: str, 
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an agent with input.
        
        Args:
            agent_id: Agent ID
            input_message: Input message
            session_id: Session ID for conversation continuity
            context: Additional context
            
        Returns:
            Execution result
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.agents[agent_id]
        graph = agent_info["graph"]
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # For ReAct agents, use simpler state structure
        if agent_info["tools"]:
            # ReAct agent expects just messages
            initial_state = {"messages": [HumanMessage(content=input_message)]}
        else:
            # Custom agent uses our state structure
            initial_state = AgentState(
                messages=[HumanMessage(content=input_message)],
                iteration_count=0,
                tool_calls=[],
                session_id=session_id,
                context=context or {}
            )
        
        # Execute the graph
        start_time = datetime.utcnow()
        try:
            result = graph.invoke(initial_state)
            
            # Update agent execution count and timestamp
            agent_info["agent"].execution_count += 1
            agent_info["agent"].last_executed_at = datetime.utcnow()
            agent_info["agent"].status = AgentStatus.COMPLETED
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract response from the last AI message
            messages = result.get("messages", [])
            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
            response_content = ai_messages[-1].content if ai_messages else "No response generated"
            
            # Extract tool calls if any
            tool_calls = []
            for msg in messages:
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_calls.append({
                            "tool_name": tool_call.get("name", "unknown"),
                            "tool_args": tool_call.get("args", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            return {
                "agent_id": agent_id,
                "session_id": session_id,
                "response": response_content,
                "status": AgentStatus.COMPLETED,
                "execution_time": execution_time,
                "tool_calls": tool_calls,
                "iteration_count": result.get("iteration_count", 1),
                "messages": [
                    {
                        "type": type(msg).__name__,
                        "content": msg.content,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    for msg in messages
                ]
            }
            
        except Exception as e:
            agent_info["agent"].status = AgentStatus.FAILED
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "agent_id": agent_id,
                "session_id": session_id,
                "response": f"Error executing agent: {str(e)}",
                "status": AgentStatus.FAILED,
                "execution_time": execution_time,
                "tool_calls": [],
                "iteration_count": 0,
                "error": str(e)
            } 