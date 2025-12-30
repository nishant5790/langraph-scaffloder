#!/bin/bash

# LangGraph Agent Builder System - cURL Examples
# These examples show how to interact with the API using curl commands

BASE_URL="http://localhost:8000/api/v1"

echo "=== LangGraph Agent Builder System - cURL Examples ==="
echo ""

# Check if server is running
echo "1. Health Check"
curl -s "$BASE_URL/health" | jq '.'
echo ""

# List available tools
echo "2. List Available Tools"
curl -s "$BASE_URL/tools" | jq '.'
echo ""

# List supported models
echo "3. List Supported Models"
curl -s "$BASE_URL/models" | jq '.'
echo ""

# Create a simple chat agent
echo "4. Create Simple Chat Agent"
AGENT_RESPONSE=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "name": "Simple Chat Assistant",
      "description": "A helpful chat assistant",
      "instructions": "You are a helpful assistant. Answer questions clearly and concisely.",
      "model": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7
      },
      "tools": [],
      "max_iterations": 5
    }
  }')

echo "$AGENT_RESPONSE" | jq '.'
AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.agent_id')
echo "Agent ID: $AGENT_ID"
echo ""

# Execute the agent
echo "5. Execute Agent"
curl -s -X POST "$BASE_URL/agents/execute" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"input_message\": \"Hello! Tell me a joke about programming.\"
  }" | jq '.'
echo ""

# Create an agent with tools
echo "6. Create Agent with Tools"
TOOL_AGENT_RESPONSE=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "name": "Calculator Assistant",
      "description": "An assistant that can perform calculations",
      "instructions": "You are a helpful assistant with access to a calculator. Use it to solve math problems.",
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
      ],
      "max_iterations": 10
    }
  }')

echo "$TOOL_AGENT_RESPONSE" | jq '.'
TOOL_AGENT_ID=$(echo "$TOOL_AGENT_RESPONSE" | jq -r '.agent_id')
echo "Tool Agent ID: $TOOL_AGENT_ID"
echo ""

# Execute the tool agent
echo "7. Execute Tool Agent"
curl -s -X POST "$BASE_URL/agents/execute" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$TOOL_AGENT_ID\",
    \"input_message\": \"What is 15 * 23 + 47 - 12?\"
  }" | jq '.'
echo ""

# List all agents
echo "8. List All Agents"
curl -s "$BASE_URL/agents" | jq '.'
echo ""

# Get specific agent details
echo "9. Get Agent Details"
curl -s "$BASE_URL/agents/$AGENT_ID" | jq '.'
echo ""

# Get agent metrics
echo "10. Get Agent Metrics"
curl -s "$BASE_URL/metrics/agents/$AGENT_ID" | jq '.'
echo ""

# Get system metrics
echo "11. Get System Metrics"
curl -s "$BASE_URL/metrics/system" | jq '.'
echo ""

# Get Prometheus metrics (first few lines)
echo "12. Get Prometheus Metrics (sample)"
curl -s "$BASE_URL/metrics/prometheus" | head -20
echo "..."
echo ""

# Create a Bedrock agent (if AWS credentials are configured)
echo "13. Create Bedrock Agent (optional - requires AWS credentials)"
BEDROCK_RESPONSE=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "name": "Bedrock Assistant",
      "description": "An assistant powered by AWS Bedrock",
      "instructions": "You are a knowledgeable assistant. Provide helpful and detailed responses.",
      "model": {
        "provider": "bedrock",
        "model_name": "anthropic.claude-3-haiku-20240307-v1:0",
        "temperature": 0.5
      },
      "tools": [],
      "max_iterations": 5
    }
  }')

if echo "$BEDROCK_RESPONSE" | jq -e '.agent_id' > /dev/null; then
  echo "$BEDROCK_RESPONSE" | jq '.'
  BEDROCK_AGENT_ID=$(echo "$BEDROCK_RESPONSE" | jq -r '.agent_id')
  
  # Execute Bedrock agent
  echo "14. Execute Bedrock Agent"
  curl -s -X POST "$BASE_URL/agents/execute" \
    -H "Content-Type: application/json" \
    -d "{
      \"agent_id\": \"$BEDROCK_AGENT_ID\",
      \"input_message\": \"Explain the concept of machine learning in simple terms.\"
    }" | jq '.'
else
  echo "Bedrock agent creation failed (likely due to missing AWS credentials)"
  echo "$BEDROCK_RESPONSE" | jq '.'
fi
echo ""

# Clean up - delete agents
echo "15. Cleanup - Delete Agents"
echo "Deleting simple chat agent..."
curl -s -X DELETE "$BASE_URL/agents/$AGENT_ID" | jq '.'

echo "Deleting tool agent..."
curl -s -X DELETE "$BASE_URL/agents/$TOOL_AGENT_ID" | jq '.'

if [ ! -z "$BEDROCK_AGENT_ID" ]; then
  echo "Deleting Bedrock agent..."
  curl -s -X DELETE "$BASE_URL/agents/$BEDROCK_AGENT_ID" | jq '.'
fi

echo ""
echo "=== Examples completed! ===" 