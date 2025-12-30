"""Monitoring and metrics system for the LangGraph Agent Builder."""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import structlog

logger = structlog.get_logger()


class MetricsCollector:
    """Collects and manages metrics for agent performance monitoring."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collector.
        
        Args:
            registry: Prometheus registry, creates new one if None
        """
        self.registry = registry or CollectorRegistry()
        
        # Agent execution metrics
        self.agent_executions_total = Counter(
            'agent_executions_total',
            'Total number of agent executions',
            ['agent_id', 'status'],
            registry=self.registry
        )
        
        self.agent_execution_duration = Histogram(
            'agent_execution_duration_seconds',
            'Duration of agent executions',
            ['agent_id'],
            registry=self.registry
        )
        
        self.agent_token_usage = Counter(
            'agent_token_usage_total',
            'Total tokens used by agents',
            ['agent_id', 'token_type'],
            registry=self.registry
        )
        
        self.agent_tool_calls = Counter(
            'agent_tool_calls_total',
            'Total tool calls made by agents',
            ['agent_id', 'tool_name'],
            registry=self.registry
        )
        
        self.active_agents = Gauge(
            'active_agents',
            'Number of active agents',
            registry=self.registry
        )
        
        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active sessions',
            registry=self.registry
        )
        
        # System metrics
        self.system_errors = Counter(
            'system_errors_total',
            'Total system errors',
            ['error_type'],
            registry=self.registry
        )
        
        # In-memory storage for detailed metrics
        self.detailed_metrics: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_agent_execution(
        self,
        agent_id: str,
        status: str,
        duration: float,
        token_usage: Optional[Dict[str, int]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ):
        """Record agent execution metrics.
        
        Args:
            agent_id: Agent ID
            status: Execution status
            duration: Execution duration in seconds
            token_usage: Token usage statistics
            tool_calls: Tool calls made during execution
        """
        # Record Prometheus metrics
        self.agent_executions_total.labels(agent_id=agent_id, status=status).inc()
        self.agent_execution_duration.labels(agent_id=agent_id).observe(duration)
        
        if token_usage:
            for token_type, count in token_usage.items():
                self.agent_token_usage.labels(
                    agent_id=agent_id, 
                    token_type=token_type
                ).inc(count)
        
        if tool_calls:
            for tool_call in tool_calls:
                self.agent_tool_calls.labels(
                    agent_id=agent_id,
                    tool_name=tool_call.get('tool_name', 'unknown')
                ).inc()
        
        # Store detailed metrics
        if agent_id not in self.detailed_metrics:
            self.detailed_metrics[agent_id] = []
        
        self.detailed_metrics[agent_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'status': status,
            'duration': duration,
            'token_usage': token_usage or {},
            'tool_calls': tool_calls or []
        })
        
        # Keep only last 1000 records per agent
        if len(self.detailed_metrics[agent_id]) > 1000:
            self.detailed_metrics[agent_id] = self.detailed_metrics[agent_id][-1000:]
        
        logger.info(
            "Agent execution recorded",
            agent_id=agent_id,
            status=status,
            duration=duration,
            token_usage=token_usage,
            tool_calls_count=len(tool_calls) if tool_calls else 0
        )
    
    def record_error(self, error_type: str, error_details: str):
        """Record system error.
        
        Args:
            error_type: Type of error
            error_details: Error details
        """
        self.system_errors.labels(error_type=error_type).inc()
        
        logger.error(
            "System error recorded",
            error_type=error_type,
            error_details=error_details
        )
    
    def update_active_agents(self, count: int):
        """Update active agents count.
        
        Args:
            count: Number of active agents
        """
        self.active_agents.set(count)
    
    def update_active_sessions(self, count: int):
        """Update active sessions count.
        
        Args:
            count: Number of active sessions
        """
        self.active_sessions.set(count)
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a specific agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent metrics summary
        """
        if agent_id not in self.detailed_metrics:
            return {}
        
        executions = self.detailed_metrics[agent_id]
        
        # Calculate summary statistics
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e['status'] == 'completed'])
        failed_executions = len([e for e in executions if e['status'] == 'failed'])
        
        durations = [e['duration'] for e in executions]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        total_tokens = sum(
            sum(e['token_usage'].values()) for e in executions
        )
        
        # Last 7 days executions
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_executions = [
            e for e in executions
            if datetime.fromisoformat(e['timestamp']) > seven_days_ago
        ]
        
        return {
            'agent_id': agent_id,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
            'average_duration': avg_duration,
            'total_tokens': total_tokens,
            'last_7_days_executions': len(recent_executions),
            'last_execution': executions[-1]['timestamp'] if executions else None
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics summary.
        
        Returns:
            System metrics summary
        """
        total_agents = len(self.detailed_metrics)
        total_executions = sum(len(executions) for executions in self.detailed_metrics.values())
        
        all_executions = []
        for executions in self.detailed_metrics.values():
            all_executions.extend(executions)
        
        successful_executions = len([e for e in all_executions if e['status'] == 'completed'])
        failed_executions = len([e for e in all_executions if e['status'] == 'failed'])
        
        return {
            'total_agents': total_agents,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'system_success_rate': successful_executions / total_executions if total_executions > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format.
        
        Returns:
            Prometheus metrics as string
        """
        return generate_latest(self.registry).decode('utf-8')


class PerformanceMonitor:
    """Performance monitoring context manager."""
    
    def __init__(self, metrics_collector: MetricsCollector, agent_id: str):
        """Initialize performance monitor.
        
        Args:
            metrics_collector: Metrics collector instance
            agent_id: Agent ID being monitored
        """
        self.metrics_collector = metrics_collector
        self.agent_id = agent_id
        self.start_time = None
        self.status = "unknown"
        self.token_usage = {}
        self.tool_calls = []
    
    def __enter__(self):
        """Start monitoring."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End monitoring and record metrics."""
        if self.start_time is None:
            return
        
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.status = "failed"
            self.metrics_collector.record_error(
                error_type=exc_type.__name__,
                error_details=str(exc_val)
            )
        elif self.status == "unknown":
            self.status = "completed"
        
        self.metrics_collector.record_agent_execution(
            agent_id=self.agent_id,
            status=self.status,
            duration=duration,
            token_usage=self.token_usage,
            tool_calls=self.tool_calls
        )
    
    def set_status(self, status: str):
        """Set execution status.
        
        Args:
            status: Execution status
        """
        self.status = status
    
    def add_token_usage(self, token_usage: Dict[str, int]):
        """Add token usage information.
        
        Args:
            token_usage: Token usage statistics
        """
        for token_type, count in token_usage.items():
            self.token_usage[token_type] = self.token_usage.get(token_type, 0) + count
    
    def add_tool_call(self, tool_call: Dict[str, Any]):
        """Add tool call information.
        
        Args:
            tool_call: Tool call details
        """
        self.tool_calls.append(tool_call)


# Global metrics collector instance
metrics_collector = MetricsCollector() 