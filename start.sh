#!/bin/bash

# LangGraph Agent Builder System - Startup Script

set -e

echo "🚀 Starting LangGraph Agent Builder System"
echo "=========================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env file with your API keys before running again"
        exit 1
    else
        echo "❌ No configuration template found"
        exit 1
    fi
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install dependencies if requirements.txt is newer than last install
if [ ! -f ".install_timestamp" ] || [ "requirements.txt" -nt ".install_timestamp" ]; then
    echo "📦 Installing/updating dependencies..."
    uv pip install -r requirements.txt
    touch .install_timestamp
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies up to date"
fi

# Create logs directory
mkdir -p logs
echo "✅ Logs directory ready"

# Check if we're running in Docker
if [ -n "$DOCKER_CONTAINER" ]; then
    echo "🐳 Running in Docker container"
    export HOST=0.0.0.0
else
    echo "💻 Running locally"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Health check function
check_health() {
    local max_attempts=30
    local attempt=1
    
    echo "🏥 Checking server health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            echo "✅ Server is healthy!"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - waiting for server..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Server health check failed after $max_attempts attempts"
    return 1
}

# Function to show usage information
show_usage() {
    echo ""
    echo "🎯 Server is running!"
    echo ""
    echo "📍 Endpoints:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check:      http://localhost:8000/api/v1/health"
    echo "   • Metrics:           http://localhost:8000/api/v1/metrics/prometheus"
    echo ""
    echo "🧪 Try the examples:"
    echo "   • Basic usage:       python examples/basic_usage.py"
    echo "   • Advanced examples: python examples/advanced_example.py"
    echo "   • cURL examples:     ./examples/curl_examples.sh"
    echo ""
    echo "📊 If using Docker Compose (with monitoring):"
    echo "   • Prometheus:        http://localhost:9090"
    echo "   • Grafana:           http://localhost:3000 (admin/admin)"
    echo ""
}

# Start the server
echo "🚀 Starting server..."

if [ "$1" = "--dev" ]; then
    echo "🔧 Development mode with auto-reload"
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8100 --reload &
elif [ "$1" = "--docker" ]; then
    echo "🐳 Docker mode"
    python -m src.main &
else
    echo "🏭 Production mode"
    python -m src.main &
fi

SERVER_PID=$!

# Wait for server to start and perform health check
sleep 5

if check_health; then
    show_usage
    
    echo "📝 Server logs will appear below. Press Ctrl+C to stop."
    echo "=================================================="
    
    # Wait for server process
    wait $SERVER_PID
else
    echo "❌ Failed to start server"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi 