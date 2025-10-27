# Deployment Guide

Comprehensive deployment options for the AWS Bedrock Chatbot API.

## Deployment Options

| Method | Best For | Complexity | Cost | Scalability |
|--------|----------|------------|------|-------------|
| **Local Docker** | Development, Testing | ⭐ Low | Free | Single instance |
| **AWS Lambda** | Serverless, Pay-per-use | ⭐⭐ Medium | Very Low | Auto-scales |
| **Kubernetes (EKS)** | Production, High traffic | ⭐⭐⭐ High | Medium | Highly scalable |

## Quick Links

- **[Local Docker Deployment](#local-docker-deployment)** - Test locally with Docker
- **[AWS Lambda Deployment](DEPLOY_LAMBDA.md)** - Serverless deployment with Docker containers
- **[Kubernetes/EKS Deployment](DEPLOY_KUBERNETES.md)** - Production-ready Kubernetes deployment

---

## Local Docker Deployment

Perfect for development and testing.

### Using Docker

```bash
# Build image
docker build -f deployment/Dockerfile -t chatbot-api .

# Run container
docker run -p 8000:8000 \
    -e AWS_ACCESS_KEY_ID=your_key \
    -e AWS_SECRET_ACCESS_KEY=your_secret \
    -e AWS_REGION=us-east-1 \
    -e BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0 \
    chatbot-api
```

### Using Docker Compose

```bash
# Create .env file first
cp ../.env.example ../.env
# Edit .env with your AWS credentials

# Start services
docker-compose -f deployment/docker-compose.yml up

# Or run in background
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop services
docker-compose -f deployment/docker-compose.yml down
```

**Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## AWS Lambda Deployment

Deploy as a serverless function using AWS Lambda with Docker container images.

### 🚀 Quick Deploy

**Linux/Mac:**
```bash
cd deployment
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

**Windows:**
```bash
cd deployment
deploy_lambda.bat
```

### Architecture

```
Internet → Function URL → Lambda (Docker) → Bedrock + DynamoDB
```

### Features

✅ **Serverless** - No server management  
✅ **Auto-scaling** - Handles any traffic  
✅ **Pay-per-use** - Only pay for requests  
✅ **Container support** - Full FastAPI app  
✅ **300s timeout** - Handles long conversations  

### Detailed Guide

See **[DEPLOY_LAMBDA.md](DEPLOY_LAMBDA.md)** for:
- Manual deployment steps
- API Gateway integration
- Environment configuration
- Cost optimization
- Monitoring and logs
- Troubleshooting

### Estimated Costs

- **Lambda**: ~$0.20 per 1M requests (1GB memory)
- **Bedrock**: Variable by model (~$0.003-0.015 per 1K tokens)
- **DynamoDB**: ~$1.25 per 1M writes
- **ECR**: $0.10 per GB-month storage

**Example:** 10K requests/day = ~$6-15/month

---

## Kubernetes (EKS) Deployment

Production-ready deployment on AWS Elastic Kubernetes Service.

### 🚀 Quick Deploy

```bash
cd deployment
chmod +x deploy_eks.sh
export EKS_CLUSTER_NAME="your-cluster-name"
./deploy_eks.sh
```

### Architecture

```
Internet → ALB (Ingress) → Kubernetes Service → Pods (3+)
                                                   ↓
                                          Bedrock + DynamoDB
```

### Features

✅ **High Availability** - Multi-AZ deployment  
✅ **Auto-scaling** - HPA + Cluster Autoscaler  
✅ **Load Balancing** - AWS ALB integration  
✅ **Zero-downtime** - Rolling updates  
✅ **Production-ready** - Monitoring, logging  

### Kubernetes Resources

- `namespace.yaml` - Isolated namespace
- `configmap.yaml` - Configuration
- `secret.yaml` - AWS credentials
- `serviceaccount.yaml` - IRSA support
- `deployment.yaml` - Pod deployment (3 replicas)
- `service.yaml` - Internal service
- `ingress.yaml` - ALB ingress
- `hpa.yaml` - Auto-scaling rules
- `kustomization.yaml` - Kustomize config

### Detailed Guide

See **[DEPLOY_KUBERNETES.md](DEPLOY_KUBERNETES.md)** for:
- EKS cluster setup
- IRSA (IAM Roles for Service Accounts)
- Ingress configuration
- Scaling strategies
- Monitoring setup
- Production best practices

### Estimated Costs

- **EKS Control Plane**: $73/month
- **Worker Nodes**: 3x t3.medium = ~$75/month
- **ALB**: ~$23/month
- **Bedrock + DynamoDB**: Variable

**Example:** ~$180-250/month for 3-node cluster

---

## Comparison Matrix

### When to Use Each

| Scenario | Recommended Deployment |
|----------|----------------------|
| **Development** | Local Docker |
| **Small project, low traffic** | AWS Lambda |
| **Cost-sensitive, sporadic usage** | AWS Lambda |
| **Production, high traffic** | Kubernetes (EKS) |
| **Microservices architecture** | Kubernetes (EKS) |
| **Need fine-grained control** | Kubernetes (EKS) |
| **Multi-region deployment** | Kubernetes (EKS) |

### Performance Comparison

| Metric | Lambda | Kubernetes |
|--------|--------|------------|
| **Cold Start** | 1-3s | 0s (always warm) |
| **Latency** | Variable | Consistent |
| **Max Timeout** | 900s | Unlimited |
| **Concurrent Requests** | 1000+ (limit) | Unlimited |
| **Memory** | Up to 10GB | Node-dependent |

---

## Prerequisites

### All Deployments
- AWS Account with credentials
- AWS CLI installed and configured
- Docker installed
- DynamoDB table created (run `python setup_dynamodb.py`)
- Bedrock models enabled

### Lambda-Specific
- ECR access
- Lambda permissions
- IAM role creation rights

### Kubernetes-Specific
- kubectl installed
- EKS cluster running (or eksctl to create one)
- ECR access
- Helm (optional, for ingress controller)

---

## Post-Deployment

### Testing

```bash
# Health check
curl https://your-endpoint/health

# Send message
curl -X POST https://your-endpoint/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello!"}'

# List models
curl -X POST https://your-endpoint/models/list
```

### Monitoring

**Lambda:**
- CloudWatch Logs: `/aws/lambda/chatbot-api`
- CloudWatch Metrics: Invocations, Duration, Errors

**Kubernetes:**
```bash
# View logs
kubectl logs -n chatbot -l app=chatbot-api -f

# View metrics
kubectl top pods -n chatbot

# View HPA status
kubectl get hpa -n chatbot
```

### Updating

**Lambda:**
```bash
# Rebuild and push
docker build -f deployment/Dockerfile.lambda -t chatbot-lambda:latest .
docker push ${ECR_REPO_URI}:latest

# Update function
aws lambda update-function-code \
    --function-name chatbot-api \
    --image-uri ${ECR_REPO_URI}:latest
```

**Kubernetes:**
```bash
# Rebuild and push
docker build -f deployment/Dockerfile -t chatbot-api:v2 .
docker push ${ECR_REPO_URI}:v2

# Update deployment
kubectl set image deployment/chatbot-api \
    chatbot-api=${ECR_REPO_URI}:v2 \
    -n chatbot
```

---

## Security Best Practices

### 1. Credentials Management

**❌ Never commit:**
- AWS access keys
- Secret keys
- `.env` files with real credentials

**✅ Do use:**
- IAM Roles (Lambda)
- IRSA (Kubernetes)
- AWS Secrets Manager
- Environment variables at runtime

### 2. Network Security

**Lambda:**
- Use VPC for DynamoDB access
- Enable encryption in transit

**Kubernetes:**
- Use Network Policies
- Enable Pod Security Standards
- Use private subnets for nodes

### 3. API Security

- Enable authentication (API Gateway, Ingress)
- Use HTTPS only
- Rate limiting
- Input validation

---

## Troubleshooting

### Common Issues

**1. ECR Login Failed**
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin ${ECR_REPO_URI}
```

**2. Lambda Timeout**
```bash
aws lambda update-function-configuration \
    --function-name chatbot-api \
    --timeout 300
```

**3. Kubernetes ImagePullBackOff**
```bash
# Check if image exists
aws ecr describe-images --repository-name chatbot-api

# Verify image URI in deployment.yaml
kubectl describe pod -n chatbot <pod-name>
```

**4. Bedrock Access Denied**
- Enable model access in AWS Console
- Check IAM permissions
- Verify model ID is correct (`us.amazon.nova-pro-v1:0`)

### Getting Help

- Check main [README.md](../README.md)
- View [API Examples](../docs/API_EXAMPLES.md)
- See [Model Configuration](../docs/CHANGE_MODEL.md)
- Review AWS documentation

---

## File Structure

```
deployment/
├── README.md                    # This file
├── DEPLOY_LAMBDA.md            # Lambda deployment guide
├── DEPLOY_KUBERNETES.md        # Kubernetes deployment guide
│
├── Dockerfile                   # Standard Docker image
├── Dockerfile.lambda           # Lambda-specific image
├── docker-compose.yml          # Local Docker Compose
├── .dockerignore               # Docker ignore rules
│
├── deploy_lambda.sh            # Lambda deploy script (Linux/Mac)
├── deploy_lambda.bat           # Lambda deploy script (Windows)
├── deploy_eks.sh               # EKS deploy script
│
├── lambda_handler.py           # Lambda function handler
├── lambda_deploy.py            # Legacy Lambda deployment
├── cloudformation_template.yaml # AWS CloudFormation template
│
└── kubernetes/                 # Kubernetes manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── serviceaccount.yaml
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    └── kustomization.yaml
```

---

## Next Steps

1. **Choose your deployment method** based on your needs
2. **Follow the specific guide** (Lambda or Kubernetes)
3. **Test the deployment** with the test endpoints
4. **Set up monitoring** and alerts
5. **Configure auto-scaling** for production
6. **Implement security** measures

---

## Additional Resources

- [AWS Lambda with Docker](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Docker Documentation](https://docs.docker.com/)

---

**Ready to deploy?** Choose your deployment method above and follow the guide!
