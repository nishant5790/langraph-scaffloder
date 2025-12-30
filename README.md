# LangGraph Agent Builder System

A production-ready system for dynamically creating and managing LangGraph-based agents with comprehensive monitoring, tracing, and multi-model support.

## 🚀 Features

- **Dynamic Agent Creation**: Create LangGraph agents from simple instructions
- **Multi-Model Support**: OpenAI and AWS Bedrock integration
- **Built-in Tools**: Calculator, file operations, web search, time, HTTP requests, shell commands
- **Production Monitoring**: Prometheus metrics, structured logging, performance tracking
- **LangSmith Integration**: Advanced tracing and debugging capabilities
- **REST API**: Easy-to-use endpoints for agent management and execution
- **Session Management**: Conversation continuity and context preservation
- **Error Handling**: Comprehensive error tracking and recovery
- **Security**: Safe tool execution with built-in restrictions

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Monitoring](#monitoring)
- [Development](#development)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

- Python 3.8+
- OpenAI API Key (for OpenAI models)
- AWS Credentials (for Bedrock models)
- Redis (optional, for advanced session management)

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd langraph-scaffloder

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

1. Copy the configuration template:
```bash
cp config.env.example .env
```

2. Edit `.env` with your credentials:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# AWS Bedrock Configuration (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# LangSmith Configuration (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
```

## ⚡ Quick Start

### 1. Start the Server

```bash
python -m src.main
```

The server will start on `http://localhost:8000`

### 2. Create Your First Agent

```python
import asyncio
import httpx

async def create_simple_agent():
    async with httpx.AsyncClient() as client:
        # Create agent
        response = await client.post("http://localhost:8000/api/v1/agents", json={
            "config": {
                "name": "My First Agent",
                "description": "A helpful assistant",
                "instructions": "You are a helpful assistant. Answer questions clearly.",
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-3.5-turbo",
                    "temperature": 0.7
                },
                "tools": []
            }
        })
        
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        
        # Execute agent
        response = await client.post("http://localhost:8000/api/v1/agents/execute", json={
            "agent_id": agent_id,
            "input_message": "Hello! What can you help me with?"
        })
        
        result = response.json()
        print(f"Agent response: {result['response']}")

asyncio.run(create_simple_agent())
```

### 3. Using cURL

```bash
# Create an agent
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "name": "Calculator Agent",
           "description": "An agent that can perform calculations",
     "instructions": "You are a helpful calculator. Use the calculate tool for math problems.",
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
        }
      ]
    }
  }'
```

## 📖 API Documentation

### Endpoints

#### Agent Management

- `POST /api/v1/agents` - Create a new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `DELETE /api/v1/agents/{agent_id}` - Delete an agent
- `POST /api/v1/agents/execute` - Execute an agent

#### Tools and Models

- `GET /api/v1/tools` - List available tools
- `GET /api/v1/models` - List supported models

#### Monitoring

- `GET /api/v1/metrics/agents/{agent_id}` - Get agent metrics
- `GET /api/v1/metrics/system` - Get system metrics
- `GET /api/v1/metrics/prometheus` - Get Prometheus metrics
- `GET /api/v1/health` - Health check

### Agent Configuration Schema

```json
{
  "config": {
    "name": "Agent Name",
    "description": "Agent description",
    "instructions": "System instructions for the agent",
    "model": {
      "provider": "openai|bedrock",
      "model_name": "model-name",
      "temperature": 0.7,
      "max_tokens": 1000,
      "top_p": 0.9
    },
    "tools": [
      {
        "name": "tool_name",
        "description": "Tool description",
        "function_name": "function_name",
        "parameters": {},
        "required_params": []
      }
    ],
    "max_iterations": 10,
    "memory_enabled": true,
    "streaming": false
  }
}
```

## 🛠️ Built-in Tools

The system includes several built-in tools:

- **calculate**: Safe mathematical expression evaluation
- **get_current_time**: Get current date and time
- **web_search**: Perform web searches (mock implementation)
- **read_file**: Read file contents
- **write_file**: Write content to files
- **execute_shell_command**: Execute shell commands (with safety restrictions)
- **http_request**: Make HTTP requests

## 📊 Monitoring

### Prometheus Metrics

The system exposes comprehensive metrics:

- `agent_executions_total` - Total agent executions by status
- `agent_execution_duration_seconds` - Execution duration histogram
- `agent_token_usage_total` - Token usage by agent and type
- `agent_tool_calls_total` - Tool calls by agent and tool
- `active_agents` - Number of active agents
- `system_errors_total` - System errors by type

### LangSmith Integration

Enable advanced tracing by setting:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
```

**Note**: LangSmith tracing is optional and disabled by default. Only enable it if you have a valid LangSmith API key to avoid authentication errors in the logs.

### Structured Logging

All operations are logged with structured JSON logs for easy parsing and analysis.

## 🎯 Examples

### Example 1: Simple Chat Agent

```python
agent_config = {
    "config": {
        "name": "Chat Assistant",
        "description": "A helpful chat assistant",
        "instructions": "You are a helpful assistant. Answer questions clearly.",
        "model": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        "tools": []
    }
}
```

### Example 2: Multi-Tool Agent

```python
agent_config = {
    "config": {
        "name": "Multi-Tool Assistant",
        "description": "An assistant with multiple tools",
        "instructions": "Use appropriate tools to help answer questions.",
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
        ]
    }
}
```

### Example 3: AWS Bedrock Agent

```python
agent_config = {
    "config": {
        "name": "Bedrock Assistant",
        "description": "An assistant powered by AWS Bedrock",
        "instructions": "You are a knowledgeable research assistant.",
        "model": {
            "provider": "bedrock",
            "model_name": "anthropic.claude-3-sonnet-20240229-v1:0",
            "temperature": 0.5
        },
        "tools": []
    }
}
```

## 🔧 Development

### Running Examples

```bash
# Python examples
python examples/basic_usage.py

# cURL examples
./examples/curl_examples.sh
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ examples/

# Sort imports
isort src/ examples/

# Type checking
mypy src/
```

## 🏗️ Architecture

The system is built with a modular architecture:

```
src/
├── core/                 # Core agent building logic
│   ├── agent_builder.py  # LangGraph agent builder
│   ├── model_factory.py  # Multi-model support
│   └── tools.py          # Tool management
├── models/               # Pydantic models
├── api/                  # FastAPI routes
├── monitoring/           # Metrics and monitoring
└── config.py            # Configuration management
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running the server
- **Issues**: Report issues on GitHub
- **Discussions**: Join our community discussions

## 🔗 Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangSmith](https://smith.langchain.com/)

---

**Made with ❤️ for the AI community** 