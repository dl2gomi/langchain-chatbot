# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Client                            │
│                   (Web, Mobile, CLI)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTPS
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼───────┐               ┌────────▼────────┐
│  Lambda URL   │               │  ALB/Ingress    │
│  (Serverless) │               │  (Kubernetes)   │
└───────┬───────┘               └────────┬────────┘
        │                                │
        │                                │
┌───────▼───────┐               ┌────────▼────────┐
│ Lambda        │               │  K8s Service    │
│ (FastAPI      │               │                 │
│  Container)   │               │  ┌──────────┐   │
│               │               │  │  Pod 1   │   │
│               │               │  │ (FastAPI)│   │
└───────┬───────┘               │  └──────────┘   │
        │                       │  ┌──────────┐   │
        │                       │  │  Pod 2   │   │
        │                       │  │ (FastAPI)│   │
        │                       │  └──────────┘   │
        │                       │  ┌──────────┐   │
        │                       │  │  Pod 3   │   │
        │                       │  │ (FastAPI)│   │
        │                       │  └──────────┘   │
        │                       └────────┬────────┘
        │                                │
        └────────────┬───────────────────┘
                     │
        ┌────────────┴────────────────┐
        │                             │
┌───────▼────────┐         ┌──────────▼─────────┐
│ AWS Bedrock    │         │   AWS DynamoDB     │
│ (Nova Models)  │         │ (Conversation      │
│                │         │  History)          │
└────────────────┘         └────────────────────┘
```

## Components

### 1. FastAPI Application

**File:** `api.py`

The REST API server that:
- Handles HTTP requests
- Manages chat sessions
- Interfaces with AWS services
- Provides API documentation (Swagger)

**Key Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Send messages
- `GET /history/{session_id}` - Get conversation history
- `POST /models/list` - List available models

### 2. Chatbot Core Logic

**File:** `chatbot_aws.py`

Core chatbot functionality:
- AWS Bedrock integration (LLM)
- DynamoDB conversation history
- Session management
- Message processing

**Key Features:**
- Configurable model selection
- Persistent conversation memory
- Error handling and retry logic

### 3. Deployment Options

#### Option A: AWS Lambda (Serverless)

**Files:**
- `deployment/Dockerfile.lambda`
- `deployment/lambda_handler.py`
- `deployment/deploy_lambda.sh`

**Flow:**
```
Client → Function URL → Lambda Container → Bedrock/DynamoDB
```

**Characteristics:**
- Cold start: 1-3 seconds
- Auto-scaling: Automatic
- Cost: Pay per request
- Timeout: 300 seconds (configurable up to 900s)

#### Option B: Kubernetes (EKS)

**Files:**
- `deployment/Dockerfile`
- `deployment/kubernetes/*.yaml`
- `deployment/deploy_eks.sh`

**Flow:**
```
Client → ALB (Ingress) → Service → Pods → Bedrock/DynamoDB
```

**Characteristics:**
- Cold start: None (always warm)
- Auto-scaling: HPA + Cluster Autoscaler
- Cost: Fixed + variable
- High availability: Multi-AZ

### 4. AWS Services

#### AWS Bedrock (LLM)

- **Purpose:** AI model inference
- **Models:** Amazon Nova (Pro, Lite, Micro)
- **API:** `bedrock-runtime.InvokeModel`
- **Cost:** Per token (~$0.003-0.015 per 1K tokens)

#### DynamoDB (Storage)

- **Purpose:** Conversation history
- **Table:** `ChatbotConversations`
- **Keys:** 
  - Partition Key: `SessionId`
  - Sort Key: `Timestamp`
- **Cost:** On-demand pricing

## Data Flow

### 1. Chat Request Flow

```
1. Client sends POST /chat
   └─> Body: {"message": "Hello", "session_id": "abc123"}

2. API receives request
   └─> Validates input
   └─> Retrieves session or creates new

3. Chatbot processes message
   └─> Loads conversation history from DynamoDB
   └─> Prepares context
   └─> Calls Bedrock API

4. Bedrock generates response
   └─> Returns AI-generated text

5. Save to DynamoDB
   └─> Store user message
   └─> Store AI response

6. Return to client
   └─> {"response": "...", "session_id": "abc123"}
```

### 2. Session Management

```
SessionId (UUID)
    │
    ├─> In-memory (chatbot_sessions dict)
    │   └─> Fast access for active sessions
    │
    └─> DynamoDB (persistent storage)
        └─> Full conversation history
        └─> Survives restarts
```

### 3. Model Configuration

```
.env file
    ├─> BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
    │
    └─> chatbot_aws.py __init__()
        │
        ├─> Default model (from env)
        │
        └─> Per-request override
            └─> POST /chat {"model_id": "us.amazon.nova-micro-v1:0"}
```

## Scaling Strategy

### Lambda Scaling

```
Requests → Lambda Auto-scales
    │
    ├─> 1 concurrent request = 1 Lambda instance
    ├─> 1000 concurrent = 1000 instances
    │   (configurable limit)
    │
    └─> Cold start mitigation:
        ├─> Provisioned concurrency
        └─> Keep-warm pings
```

### Kubernetes Scaling

```
Load → HPA monitors metrics
    │
    ├─> CPU > 70% → Scale up
    ├─> Memory > 80% → Scale up
    │
    └─> Pods: 2 (min) to 10 (max)
        │
        └─> Cluster Autoscaler
            └─> Add nodes if needed
```

**HPA Configuration:**
- Min replicas: 2
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

## Security Architecture

### 1. Authentication & Authorization

```
Client Request
    │
    ├─> Lambda:
    │   └─> Function URL (public) or API Gateway (auth)
    │
    └─> Kubernetes:
        └─> Ingress with:
            ├─> AWS WAF
            ├─> Cognito Auth
            └─> API Keys
```

### 2. AWS Credentials

```
Lambda:
    └─> IAM Role (chatbot-lambda-role)
        ├─> AWSLambdaBasicExecutionRole
        ├─> AmazonBedrockFullAccess
        └─> AmazonDynamoDBFullAccess

Kubernetes:
    └─> IRSA (IAM Roles for Service Accounts)
        └─> Pod → Service Account → IAM Role
            ├─> Bedrock permissions
            └─> DynamoDB permissions
```

### 3. Network Security

```
Lambda in VPC:
    ├─> Private Subnets
    ├─> Security Groups
    └─> NAT Gateway (for internet)

Kubernetes (EKS):
    ├─> Private Subnets (nodes)
    ├─> Public Subnets (ALB)
    ├─> Security Groups
    └─> Network Policies
```

## High Availability

### Lambda HA

- **Multi-AZ:** Automatic
- **Redundancy:** Built-in AWS infrastructure
- **Failover:** Automatic retry
- **Availability:** 99.95% SLA

### Kubernetes HA

```
EKS Cluster
    │
    ├─> Control Plane (AWS managed, Multi-AZ)
    │
    └─> Worker Nodes
        ├─> Node Group 1 (us-east-1a)
        ├─> Node Group 2 (us-east-1b)
        └─> Node Group 3 (us-east-1c)
            │
            └─> Pods distributed across AZs
                └─> Pod Anti-Affinity rules
```

**SLA:** 99.95% (EKS) + 99.99% (with multi-region)

## Monitoring & Observability

### Lambda Monitoring

```
CloudWatch
    ├─> Logs: /aws/lambda/chatbot-api
    ├─> Metrics:
    │   ├─> Invocations
    │   ├─> Duration
    │   ├─> Errors
    │   ├─> Throttles
    │   └─> Concurrent Executions
    │
    └─> X-Ray (optional)
        └─> Distributed tracing
```

### Kubernetes Monitoring

```
CloudWatch Container Insights
    ├─> Logs
    │   └─> Pod logs
    │
    ├─> Metrics
    │   ├─> CPU/Memory per pod
    │   ├─> Node metrics
    │   └─> Cluster metrics
    │
    └─> Optional: Prometheus + Grafana
        ├─> Custom metrics
        ├─> Dashboards
        └─> Alerts
```

## Cost Optimization

### Lambda Cost Model

```
Cost = Compute + Storage + Data Transfer

Compute:
    = (Memory in GB) × (Duration in seconds) × $0.0000166667
    = 1 GB × 3s × $0.0000166667 = $0.00005 per request
    
Example (1M requests/month):
    = 1,000,000 × $0.00005 = $50/month
```

### Kubernetes Cost Model

```
Fixed Costs:
    ├─> EKS Control Plane: $73/month
    ├─> 3× t3.medium nodes: $75/month
    └─> ALB: $23/month
    Total Fixed: ~$171/month

Variable Costs:
    ├─> Additional nodes (auto-scaling)
    ├─> Data transfer
    └─> EBS volumes
```

### Cost Optimization Tips

**Lambda:**
- Right-size memory (more memory = more CPU)
- Use ARM architecture (20% cheaper)
- Minimize cold starts
- Optimize code for speed

**Kubernetes:**
- Use Spot instances (70% cheaper)
- Right-size pod requests/limits
- Use Cluster Autoscaler
- Consider Fargate for variable workloads

## Performance Optimization

### API Response Times

```
Target Latency:
    ├─> P50: < 2s
    ├─> P95: < 5s
    └─> P99: < 10s

Breakdown:
    ├─> API processing: ~100ms
    ├─> DynamoDB query: ~50ms
    ├─> Bedrock inference: 1-8s (depends on model & response length)
    └─> DynamoDB write: ~50ms
```

### Optimization Strategies

1. **Caching:**
   - Cache model list (TTL: 1 hour)
   - Cache frequently accessed conversations

2. **Connection Pooling:**
   - Reuse boto3 clients
   - Keep connections warm

3. **Async Processing:**
   - Non-blocking I/O
   - Concurrent DynamoDB operations

4. **Model Selection:**
   - Nova Micro: Fastest, cheapest
   - Nova Lite: Balanced
   - Nova Pro: Best quality (slower)

## Disaster Recovery

### Backup Strategy

```
DynamoDB:
    ├─> Point-in-Time Recovery (PITR)
    │   └─> 35-day recovery window
    │
    └─> On-demand backups
        └─> Long-term retention

Lambda:
    ├─> Code in ECR
    │   └─> Image retention: 365 days
    │
    └─> CloudFormation/Terraform
        └─> Infrastructure as Code

Kubernetes:
    ├─> Velero backups
    │   └─> Cluster + persistent volume backups
    │
    └─> GitOps (ArgoCD/Flux)
        └─> Declarative configuration
```

### Recovery Procedures

**RTO (Recovery Time Objective):** < 1 hour  
**RPO (Recovery Point Objective):** < 5 minutes

## Future Enhancements

### Potential Improvements

1. **Multi-Region Deployment**
   - Global ALB
   - DynamoDB Global Tables
   - Multi-region EKS clusters

2. **Advanced Features**
   - WebSocket support for real-time streaming
   - Voice input/output integration
   - Multi-modal support (images, documents)

3. **Analytics**
   - User behavior tracking
   - Model performance metrics
   - Cost analytics dashboard

4. **Security Enhancements**
   - End-to-end encryption
   - Rate limiting per user
   - DDoS protection (AWS Shield)

---

## Additional Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Kubernetes Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/)

---

**Questions about the architecture?**
- Deployment guide: [README.md](README.md)
- Main documentation: [README.md](../README.md)
- Project structure: [docs/PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md)

