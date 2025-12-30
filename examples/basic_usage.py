"""Basic usage example for the LangGraph Agent Builder System."""

import asyncio
import httpx
import json
from typing import Dict, Any


class AgentBuilderClient:
    """Client for interacting with the LangGraph Agent Builder API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, str]:
        """Create a new agent.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            Agent creation response
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/agents",
                json=agent_config
            )
            response.raise_for_status()
            return response.json()
    
    async def execute_agent(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Execute an agent with a message.
        
        Args:
            agent_id: Agent ID
            message: Input message
            
        Returns:
            Agent execution response
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/agents/execute",
                json={
                    "agent_id": agent_id,
                    "input_message": message
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def list_agents(self) -> list:
        """List all agents.
        
        Returns:
            List of agents
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base}/agents")
            response.raise_for_status()
            return response.json()
    
    async def get_available_tools(self) -> list:
        """Get available tools.
        
        Returns:
            List of available tools
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base}/tools")
            response.raise_for_status()
            return response.json()
    
    async def get_supported_models(self) -> Dict[str, list]:
        """Get supported models.
        
        Returns:
            Dictionary of supported models by provider
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base}/models")
            response.raise_for_status()
            return response.json()


async def example_1_simple_chat_agent():
    """Example 1: Create a simple chat agent without tools."""
    print("=== Example 1: Simple Chat Agent ===")
    
    client = AgentBuilderClient()
    
    # Create a simple chat agent
    agent_config = {
        "config": {
            "name": "Simple Chat Assistant",
            "description": "A helpful chat assistant that can answer questions",
            "instructions": "You are a helpful assistant. Answer questions clearly and concisely.",
            "model": {
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7
            },
            "tools": [],
            "max_iterations": 5,
            "memory_enabled": True
        }
    }
    
    try:
        # Create the agent
        create_response = await client.create_agent(agent_config)
        agent_id = create_response["agent_id"]
        print(f"Created agent: {agent_id}")
        
        # Execute the agent
        response = await client.execute_agent(
            agent_id, 
            "Hello! Can you tell me about artificial intelligence?"
        )
        
        print(f"Agent response: {response['response']}")
        print(f"Execution time: {response['execution_time']:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_2_agent_with_tools():
    """Example 2: Create an agent with built-in tools."""
    print("\n=== Example 2: Agent with Tools ===")
    
    client = AgentBuilderClient()
    
    # Get available tools
    available_tools = await client.get_available_tools()
    print(f"Available tools: {[tool['name'] for tool in available_tools]}")
    
    # Create an agent with tools
    agent_config = {
        "config": {
            "name": "Multi-Tool Assistant",
            "description": "An assistant that can perform calculations, get time, and search",
            "instructions": """You are a helpful assistant with access to various tools. 
            Use the appropriate tools to help answer questions. For math problems, use the calculator.
            For time-related questions, use the get_current_time tool.""",
            "model": {
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.3
            },
            "tools": [
                {
                    "name": "calculate",
                    "description": "Safely evaluate a mathematical expression",
                    "function_name": "calculate",
                    "parameters": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required_params": ["expression"]
                },
                {
                    "name": "get_current_time",
                    "description": "Get the current date and time",
                    "function_name": "get_current_time",
                    "parameters": {},
                    "required_params": []
                }
            ],
            "max_iterations": 10
        }
    }
    
    try:
        # Create the agent
        create_response = await client.create_agent(agent_config)
        agent_id = create_response["agent_id"]
        print(f"Created agent: {agent_id}")
        
        # Test with a math question
        response = await client.execute_agent(
            agent_id, 
            "What is 15 * 23 + 47? Also, what time is it now?"
        )
        
        print(f"Agent response: {response['response']}")
        print(f"Tools used: {len(response['tool_calls'])}")
        for tool_call in response['tool_calls']:
            print(f"  - {tool_call['tool_name']}: {tool_call['result']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_3_bedrock_agent():
    """Example 3: Create an agent using AWS Bedrock."""
    print("\n=== Example 3: AWS Bedrock Agent ===")
    
    client = AgentBuilderClient()
    
    # Create an agent using Bedrock
    agent_config = {
        "config": {
            "name": "Bedrock Research Assistant",
            "description": "A research assistant powered by AWS Bedrock",
            "instructions": """You are a knowledgeable research assistant. 
            Help users with research questions, provide detailed explanations, 
            and offer insights on various topics.""",
            "model": {
                "provider": "bedrock",
                "model_name": "anthropic.claude-3-sonnet-20240229-v1:0",
                "temperature": 0.5
            },
            "tools": [
                {
                    "name": "web_search",
                    "description": "Perform a web search",
                    "function_name": "web_search",
                    "parameters": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required_params": ["query"]
                }
            ],
            "max_iterations": 8
        }
    }
    
    try:
        # Create the agent
        create_response = await client.create_agent(agent_config)
        agent_id = create_response["agent_id"]
        print(f"Created agent: {agent_id}")
        
        # Execute the agent
        response = await client.execute_agent(
            agent_id, 
            "Can you research and explain the latest developments in quantum computing?"
        )
        
        print(f"Agent response: {response['response']}")
        print(f"Execution time: {response['execution_time']:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_4_file_operations_agent():
    """Example 4: Create an agent that can work with files."""
    print("\n=== Example 4: File Operations Agent ===")
    
    client = AgentBuilderClient()
    
    # Create an agent with file operation tools
    agent_config = {
        "config": {
            "name": "File Operations Assistant",
            "description": "An assistant that can read and write files",
            "instructions": """You are a helpful assistant that can work with files. 
            You can read files, write files, and help users manage their documents.
            Always be careful with file operations and ask for confirmation when needed.""",
            "model": {
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.2
            },
            "tools": [
                {
                    "name": "read_file",
                    "description": "Read content from a file",
                    "function_name": "read_file",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required_params": ["file_path"]
                },
                {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "function_name": "write_file",
                    "parameters": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required_params": ["file_path", "content"]
                }
            ],
            "max_iterations": 6
        }
    }
    
    try:
        # Create the agent
        create_response = await client.create_agent(agent_config)
        agent_id = create_response["agent_id"]
        print(f"Created agent: {agent_id}")
        
        # Execute the agent to create a sample file
        response = await client.execute_agent(
            agent_id, 
            "Please create a file called 'example.txt' with a welcome message"
        )
        
        print(f"Agent response: {response['response']}")
        
        # Execute the agent to read the file
        response = await client.execute_agent(
            agent_id, 
            "Now please read the content of 'example.txt' and tell me what it contains"
        )
        
        print(f"Agent response: {response['response']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples."""
    print("LangGraph Agent Builder System - Examples")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                print("✓ Server is running")
            else:
                print("✗ Server is not responding correctly")
                return
    except Exception:
        print("✗ Server is not running. Please start the server first with:")
        print("  python -m src.main")
        return
    
    # Run examples
    await example_1_simple_chat_agent()
    await example_2_agent_with_tools()
    await example_3_bedrock_agent()
    await example_4_file_operations_agent()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 