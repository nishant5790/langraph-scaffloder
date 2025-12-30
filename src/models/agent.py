"""Pydantic models for agent configuration and management."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported model providers."""
    OPENAI = "openai"
    BEDROCK = "bedrock"


class AgentStatus(str, Enum):
    """Agent execution status."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolConfig(BaseModel):
    """Configuration for a tool that can be used by an agent."""
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    function_name: str = Field(..., description="Python function name to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    required_params: List[str] = Field(default_factory=list, description="Required parameters")


class ModelConfig(BaseModel):
    """Configuration for the language model."""
    provider: ModelProvider = Field(..., description="Model provider (openai or bedrock)")
    model_name: str = Field(..., description="Name of the model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")


class AgentConfig(BaseModel):
    """Configuration for creating a new agent."""
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent's purpose")
    instructions: str = Field(..., description="System instructions for the agent")
    model: ModelConfig = Field(..., description="Model configuration")
    tools: List[ToolConfig] = Field(default_factory=list, description="Available tools")
    max_iterations: int = Field(10, ge=1, le=100, description="Maximum number of iterations")
    memory_enabled: bool = Field(True, description="Whether to enable conversation memory")
    streaming: bool = Field(False, description="Whether to enable streaming responses")


class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent."""
    config: AgentConfig = Field(..., description="Agent configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentExecuteRequest(BaseModel):
    """Request model for executing an agent."""
    agent_id: str = Field(..., description="ID of the agent to execute")
    input_message: str = Field(..., description="Input message for the agent")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class AgentResponse(BaseModel):
    """Response from agent execution."""
    agent_id: str = Field(..., description="ID of the agent")
    session_id: str = Field(..., description="Session ID")
    response: str = Field(..., description="Agent's response")
    status: AgentStatus = Field(..., description="Execution status")
    execution_time: float = Field(..., description="Execution time in seconds")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tools called during execution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Agent(BaseModel):
    """Agent model for database storage."""
    id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    config: AgentConfig = Field(..., description="Agent configuration")
    status: AgentStatus = Field(AgentStatus.CREATED, description="Current status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    execution_count: int = Field(0, description="Number of times agent has been executed")
    last_executed_at: Optional[datetime] = Field(None, description="Last execution timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentSession(BaseModel):
    """Agent session for conversation continuity."""
    id: str = Field(..., description="Session ID")
    agent_id: str = Field(..., description="Associated agent ID")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class AgentMetrics(BaseModel):
    """Metrics for agent performance monitoring."""
    agent_id: str = Field(..., description="Agent ID")
    total_executions: int = Field(0, description="Total number of executions")
    successful_executions: int = Field(0, description="Number of successful executions")
    failed_executions: int = Field(0, description="Number of failed executions")
    average_execution_time: float = Field(0.0, description="Average execution time in seconds")
    total_tokens_used: int = Field(0, description="Total tokens consumed")
    last_7_days_executions: int = Field(0, description="Executions in the last 7 days")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Metrics creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp") 