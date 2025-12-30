"""FastAPI routes for the LangGraph Agent Builder System."""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse

from ..core import LangGraphAgentBuilder, ToolManager
from ..models import (
    AgentCreateRequest,
    AgentExecuteRequest,
    AgentResponse,
    Agent,
    ToolConfig,
    ModelProvider
)
from ..monitoring import metrics_collector, PerformanceMonitor
from ..config import get_settings

# Initialize router
router = APIRouter()

# Global agent builder instance
agent_builder = LangGraphAgentBuilder()
tool_manager = ToolManager()


@router.post("/agents", response_model=Dict[str, str])
async def create_agent(request: AgentCreateRequest):
    """Create a new agent.
    
    Args:
        request: Agent creation request
        
    Returns:
        Agent ID and creation status
    """
    try:
        agent_id = agent_builder.build_agent(request.config)
        
        # Update metrics
        metrics_collector.update_active_agents(len(agent_builder.list_agents()))
        
        return {
            "agent_id": agent_id,
            "status": "created",
            "message": f"Agent '{request.config.name}' created successfully"
        }
    except Exception as e:
        metrics_collector.record_error("agent_creation_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/agents", response_model=List[Agent])
async def list_agents():
    """List all agents.
    
    Returns:
        List of all agents
    """
    try:
        agents = agent_builder.list_agents()
        return agents
    except Exception as e:
        metrics_collector.record_error("list_agents_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent by ID.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Agent information
    """
    try:
        agent_info = agent_builder.get_agent(agent_id)
        if not agent_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        return agent_info["agent"]
    except HTTPException:
        raise
    except Exception as e:
        metrics_collector.record_error("get_agent_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Deletion status
    """
    try:
        deleted = agent_builder.delete_agent(agent_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Update metrics
        metrics_collector.update_active_agents(len(agent_builder.list_agents()))
        
        return {"message": f"Agent {agent_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        metrics_collector.record_error("delete_agent_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post("/agents/execute", response_model=Dict[str, Any])
async def execute_agent(request: AgentExecuteRequest):
    """Execute an agent with input.
    
    Args:
        request: Agent execution request
        
    Returns:
        Agent execution result
    """
    try:
        with PerformanceMonitor(metrics_collector, request.agent_id) as monitor:
            result = agent_builder.execute_agent(
                agent_id=request.agent_id,
                input_message=request.input_message,
                session_id=request.session_id,
                context=request.context
            )
            
            # Add metrics information to monitor
            if "token_usage" in result:
                monitor.add_token_usage(result["token_usage"])
            
            if "tool_calls" in result:
                for tool_call in result["tool_calls"]:
                    monitor.add_tool_call(tool_call)
            
            monitor.set_status(result["status"])
            
            return result
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        metrics_collector.record_error("agent_execution_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}"
        )


@router.get("/tools", response_model=List[ToolConfig])
async def list_available_tools():
    """List all available tools.
    
    Returns:
        List of available tools
    """
    try:
        tools = tool_manager.get_available_tools()
        return tools
    except Exception as e:
        metrics_collector.record_error("list_tools_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/models", response_model=Dict[str, List[str]])
async def list_supported_models():
    """List all supported models by provider.
    
    Returns:
        Dictionary of supported models by provider
    """
    try:
        from ..core.model_factory import ModelFactory
        models = ModelFactory.get_supported_models()
        return {provider.value: model_list for provider, model_list in models.items()}
    except Exception as e:
        metrics_collector.record_error("list_models_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/metrics/agents/{agent_id}")
async def get_agent_metrics(agent_id: str):
    """Get metrics for a specific agent.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Agent metrics
    """
    try:
        metrics = metrics_collector.get_agent_metrics(agent_id)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No metrics found for agent {agent_id}"
            )
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        metrics_collector.record_error("get_agent_metrics_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent metrics: {str(e)}"
        )


@router.get("/metrics/system")
async def get_system_metrics():
    """Get system-wide metrics.
    
    Returns:
        System metrics
    """
    try:
        metrics = metrics_collector.get_system_metrics()
        return metrics
    except Exception as e:
        metrics_collector.record_error("get_system_metrics_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Get metrics in Prometheus format.
    
    Returns:
        Prometheus metrics as plain text
    """
    try:
        metrics = metrics_collector.export_prometheus_metrics()
        return metrics
    except Exception as e:
        metrics_collector.record_error("export_prometheus_metrics_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export Prometheus metrics: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "active_agents": len(agent_builder.list_agents()),
        "timestamp": metrics_collector.get_system_metrics()["timestamp"]
    } 