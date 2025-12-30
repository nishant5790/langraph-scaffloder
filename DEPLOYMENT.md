# Deployment Guide

This guide covers different deployment options for the LangGraph Agent Builder System.

## 🚀 Quick Start (Local Development)

### 1. Basic Setup

```bash
# Clone and setup
git clone <repository-url>
cd langraph-scaffloder

# Quick start with script
./start.sh
```

### 2. Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp config.env.example .env
# Edit .env with your API keys

# Start server
python -m src.main
```

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t langraph-agent-builder .

# Run container
docker run -d \
  --name langraph-agent-builder \
  -p 8000:8000 \
  --env-file .env \
  langraph-agent-builder
```

### Docker Compose (Recommended for Production)

```bash
# Start full stack with monitoring
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This includes:
- Main application
- Redis (session management)
- PostgreSQL (data persistence)
- Prometheus (metrics)
- Grafana (visualization)

## ☁️ Cloud Deployment

### AWS ECS

1. **Build and push image to ECR:**

```bash
# Create ECR repository
aws ecr create-repository --repository-name langraph-agent-builder

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t langraph-agent-builder .
docker tag langraph-agent-builder:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/langraph-agent-builder:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/langraph-agent-builder:latest
```

2. **Create ECS task definition:**

```json
{
  "family": "langraph-agent-builder",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "langraph-agent-builder",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/langraph-agent-builder:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-openai-api-key"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/langraph-agent-builder",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/langraph-agent-builder

# Deploy to Cloud Run
gcloud run deploy langraph-agent-builder \
  --image gcr.io/PROJECT-ID/langraph-agent-builder \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars OPENAI_API_KEY=your-key
```

### Azure Container Instances

```bash
# Create resource group
az group create --name langraph-rg --location eastus

# Deploy container
az container create \
  --resource-group langraph-rg \
  --name langraph-agent-builder \
  --image langraph-agent-builder:latest \
  --dns-name-label langraph-unique-name \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your-key
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | No* | None |
| `AWS_ACCESS_KEY_ID` | AWS access key | No* | None |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | No* | None |
| `AWS_DEFAULT_REGION` | AWS region | No | us-east-1 |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | No | false |
| `LANGCHAIN_API_KEY` | LangSmith API key | No | None |
| `REDIS_URL` | Redis connection URL | No | redis://localhost:6379 |
| `DATABASE_URL` | Database connection URL | No | sqlite:///./agent_system.db |
| `HOST` | Server host | No | 0.0.0.0 |
| `PORT` | Server port | No | 8000 |
| `DEBUG` | Enable debug mode | No | false |
| `LOG_LEVEL` | Logging level | No | INFO |

*At least one model provider (OpenAI or AWS) is required.

### LangSmith Configuration (Optional)

LangSmith provides advanced tracing and debugging capabilities for LangChain applications. To enable it:

1. **Get a LangSmith API key** from [LangSmith](https://smith.langchain.com/)
2. **Configure environment variables**:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   ```

**Important**: LangSmith is disabled by default. Only enable it if you have a valid API key to avoid authentication errors in the logs.

**Benefits of LangSmith**:
- Detailed execution traces
- Performance monitoring
- Debugging capabilities
- Usage analytics

### Production Settings

For production deployments, consider these settings:

```bash
# Production environment
DEBUG=false
LOG_LEVEL=WARNING

# Security
SECRET_KEY=your-secure-secret-key

# Database (use PostgreSQL for production)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (for session management)
REDIS_URL=redis://redis-host:6379

# Monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

## 📊 Monitoring Setup

### Prometheus + Grafana

The Docker Compose setup includes monitoring stack:

1. **Prometheus** (http://localhost:9090)
   - Collects metrics from the application
   - Configuration in `monitoring/prometheus.yml`

2. **Grafana** (http://localhost:3000)
   - Visualizes metrics
   - Default login: admin/admin
   - Dashboards in `monitoring/grafana/`

### Custom Monitoring

To integrate with existing monitoring:

```python
# Access metrics endpoint
GET /api/v1/metrics/prometheus

# Or use the metrics collector directly
from src.monitoring import metrics_collector

# Custom metrics
metrics_collector.record_agent_execution(
    agent_id="agent-123",
    status="completed",
    duration=1.5,
    token_usage={"input": 100, "output": 50}
)
```

## 🔐 Security Considerations

### API Security

1. **Authentication**: Implement API key authentication for production
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Input Validation**: All inputs are validated via Pydantic models
4. **Tool Safety**: Built-in restrictions on dangerous commands

### Network Security

```bash
# Firewall rules (example for AWS Security Group)
# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Allow monitoring (restrict to monitoring networks)
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 9090 \
  --cidr 10.0.0.0/8
```

### Secrets Management

Use cloud secret managers:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name langraph-agent-builder/openai-key \
  --secret-string "your-openai-api-key"

# Then reference in ECS task definition
"secrets": [
  {
    "name": "OPENAI_API_KEY",
    "valueFrom": "arn:aws:secretsmanager:region:account:secret:langraph-agent-builder/openai-key"
  }
]
```

## 🔄 Scaling

### Horizontal Scaling

The application is stateless and can be scaled horizontally:

```bash
# Docker Compose scaling
docker-compose up -d --scale langraph-agent-builder=3

# Kubernetes deployment
kubectl scale deployment langraph-agent-builder --replicas=3
```

### Load Balancing

Use a load balancer to distribute traffic:

```nginx
# Nginx configuration
upstream langraph_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://langraph_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/v1/health

# Component health
curl http://localhost:8000/api/v1/metrics/system
```

### Backup and Recovery

```bash
# Database backup (if using PostgreSQL)
pg_dump -h localhost -U postgres agent_builder > backup.sql

# Restore
psql -h localhost -U postgres agent_builder < backup.sql
```

### Log Management

```bash
# View application logs
docker-compose logs -f langraph-agent-builder

# Log rotation (add to logrotate)
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check logs
   docker-compose logs langraph-agent-builder
   
   # Verify environment variables
   docker-compose exec langraph-agent-builder env | grep -E "(OPENAI|AWS)"
   ```

2. **Agent creation fails**
   - Verify API keys are correct
   - Check model names are supported
   - Review error logs

3. **High memory usage**
   - Monitor agent execution metrics
   - Consider reducing `max_iterations`
   - Implement agent cleanup policies

4. **Slow response times**
   - Check model provider latency
   - Monitor tool execution times
   - Consider caching strategies

### Performance Tuning

```bash
# Monitor resource usage
docker stats

# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Tune worker processes
export WEB_CONCURRENCY=4
```

---

For more help, check the [README.md](README.md) or open an issue on GitHub. 