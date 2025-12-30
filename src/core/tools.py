"""Built-in tools and tool management for LangGraph agents."""

import json
import os
import subprocess
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from langchain_core.tools import Tool
from pydantic import BaseModel, Field

from ..models import ToolConfig


class BuiltInTools:
    """Collection of built-in tools that agents can use."""
    
    @staticmethod
    def get_current_time() -> str:
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Result of the calculation
        """
        try:
            # Only allow safe mathematical operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def web_search(query: str, num_results: int = 5) -> str:
        """Perform a web search (mock implementation).
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Search results as formatted string
        """
        # This is a mock implementation
        # In production, you would integrate with a real search API
        return f"Mock search results for '{query}' (top {num_results} results):\n" \
               f"1. Example result 1 for {query}\n" \
               f"2. Example result 2 for {query}\n" \
               f"3. Example result 3 for {query}"
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read content from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content or error message
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(file_path: str, content: str) -> str:
        """Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            
        Returns:
            Success or error message
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    @staticmethod
    def execute_shell_command(command: str) -> str:
        """Execute a shell command (with safety restrictions).
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output or error message
        """
        # Safety restrictions - only allow safe commands
        dangerous_commands = ['rm', 'del', 'format', 'sudo', 'su', 'chmod', 'chown']
        if any(cmd in command.lower() for cmd in dangerous_commands):
            return "Error: Command not allowed for security reasons"
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return f"Exit code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    @staticmethod
    def http_request(url: str, method: str = "GET", data: Optional[str] = None) -> str:
        """Make an HTTP request.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            data: Request data (for POST requests)
            
        Returns:
            Response content or error message
        """
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=data, headers=headers, timeout=30)
            else:
                return f"Error: Unsupported HTTP method: {method}"
            
            return f"Status: {response.status_code}\nContent: {response.text[:1000]}"
        except Exception as e:
            return f"Error making HTTP request: {str(e)}"


class ToolManager:
    """Manager for creating and managing tools for agents."""
    
    def __init__(self):
        self.built_in_tools = self._get_built_in_tools()
        self.custom_tools: Dict[str, Callable] = {}
    
    def _get_built_in_tools(self) -> Dict[str, ToolConfig]:
        """Get configurations for built-in tools."""
        return {
            "get_current_time": ToolConfig(
                name="get_current_time",
                description="Get the current date and time",
                function_name="get_current_time",
                parameters={},
                required_params=[]
            ),
            "calculate": ToolConfig(
                name="calculate",
                description="Safely evaluate a mathematical expression",
                function_name="calculate",
                parameters={
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                required_params=["expression"]
            ),
            "web_search": ToolConfig(
                name="web_search",
                description="Perform a web search",
                function_name="web_search",
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                required_params=["query"]
            ),
            "read_file": ToolConfig(
                name="read_file",
                description="Read content from a file",
                function_name="read_file",
                parameters={
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                required_params=["file_path"]
            ),
            "write_file": ToolConfig(
                name="write_file",
                description="Write content to a file",
                function_name="write_file",
                parameters={
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                required_params=["file_path", "content"]
            ),
            "execute_shell_command": ToolConfig(
                name="execute_shell_command",
                description="Execute a shell command (with safety restrictions)",
                function_name="execute_shell_command",
                parameters={
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    }
                },
                required_params=["command"]
            ),
            "http_request": ToolConfig(
                name="http_request",
                description="Make an HTTP request",
                function_name="http_request",
                parameters={
                    "url": {
                        "type": "string",
                        "description": "URL to request"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, etc.)",
                        "default": "GET"
                    },
                    "data": {
                        "type": "string",
                        "description": "Request data (for POST requests)",
                        "default": None
                    }
                },
                required_params=["url"]
            )
        }
    
    def create_tool(self, tool_config: ToolConfig) -> Tool:
        """Create a LangChain Tool from a ToolConfig.
        
        Args:
            tool_config: Configuration for the tool
            
        Returns:
            LangChain Tool instance
        """
        if tool_config.name in self.built_in_tools:
            # Use built-in tool function
            func = getattr(BuiltInTools, tool_config.function_name)
        elif tool_config.name in self.custom_tools:
            # Use custom tool function
            func = self.custom_tools[tool_config.name]
        else:
            raise ValueError(f"Tool '{tool_config.name}' not found")
        
        return Tool(
            name=tool_config.name,
            description=tool_config.description,
            func=func
        )
    
    def register_custom_tool(self, name: str, func: Callable, config: ToolConfig):
        """Register a custom tool.
        
        Args:
            name: Tool name
            func: Tool function
            config: Tool configuration
        """
        self.custom_tools[name] = func
        # You could also store the config for later use
    
    def get_available_tools(self) -> List[ToolConfig]:
        """Get list of all available tools.
        
        Returns:
            List of available tool configurations
        """
        return list(self.built_in_tools.values())
    
    def create_tools_from_configs(self, tool_configs: List[ToolConfig]) -> List[Tool]:
        """Create multiple tools from configurations.
        
        Args:
            tool_configs: List of tool configurations
            
        Returns:
            List of LangChain Tool instances
        """
        tools = []
        for config in tool_configs:
            try:
                tool = self.create_tool(config)
                tools.append(tool)
            except Exception as e:
                print(f"Warning: Failed to create tool '{config.name}': {e}")
        return tools 