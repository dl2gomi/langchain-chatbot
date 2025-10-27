# 🚀 Deployment Summary

Your AWS Bedrock Chatbot is now ready for deployment in **AWS Lambda** or **Kubernetes (EKS)**!

## ✅ Status: ALL DEPLOYMENTS TESTED AND WORKING

- **AWS Lambda**: ✅ Successfully deployed and tested
- **AWS EKS**: ✅ Successfully deployed and tested  
- **Local Kubernetes**: ✅ Successfully deployed and tested

## ✅ What's Been Set Up

### 1. Lambda Deployment (Serverless)

**Files Created:**
- `deployment/Dockerfile.lambda` - Lambda-specific Docker image
- `deployment/lambda_handler.py` - FastAPI → Lambda adapter (using Mangum)
- `deployment/deploy_lambda.sh` - Automated deployment script (Linux/Mac)
- `deployment/deploy_lambda.bat` - Automated deployment script (Windows)
- `deployment/DEPLOY_LAMBDA.md` - Complete deployment guide

**Features:**
✅ Serverless architecture  
✅ Auto-scaling (handles any traffic)  
✅ Pay-per-use pricing  
✅ Fast deployment (~5 minutes)  
✅ Function URL for easy testing  
✅ **TESTED AND WORKING** - Function URL: `https://wg44knbnaeduajys7vbnaoa4le0qosdt.lambda-url.us-east-1.on.aws/`  

### 2. Kubernetes (EKS) Deployment

**Files Created:**
- `deployment/Dockerfile` - Standard Docker image
- `deployment/deploy_eks.sh` - Automated deployment script
- `deployment/DEPLOY_KUBERNETES.md` - Complete deployment guide
- `deployment/kubernetes/` - Full Kubernetes manifests:
  - `namespace.yaml` - Isolated namespace
  - `configmap.yaml` - Configuration
  - `secret.yaml` - AWS credentials
  - `serviceaccount.yaml` - IRSA support
  - `deployment.yaml` - Pod deployment (3 replicas)
  - `service.yaml` - Internal service
  - `ingress.yaml` - ALB ingress (public access)
  - `hpa.yaml` - Auto-scaling (2-10 pods)
  - `kustomization.yaml` - Kustomize config

**Features:**
✅ Production-ready  
✅ High availability (Multi-AZ)  
✅ Auto-scaling (HPA + Cluster Autoscaler)  
✅ Zero-downtime deployments  
✅ Advanced monitoring  
✅ **TESTED AND WORKING** - Cluster: `chatbot-cluster` (3 nodes, Kubernetes 1.32.9)  

### 3. Documentation

**Comprehensive Guides:**
- `deployment/README.md` - Overview & comparison
- `deployment/DEPLOY_LAMBDA.md` - Lambda step-by-step
- `deployment/DEPLOY_KUBERNETES.md` - Kubernetes step-by-step
- `deployment/ARCHITECTURE.md` - System architecture & design
- `docs/MODEL_IDS.md` - Model ID reference (fixes the model ID issue!)

### 4. Updated Requirements

Added `mangum>=0.17.0` to `requirements.txt` for Lambda support.

---

## 🎯 Quick Deploy

### Option 1: AWS Lambda (Easiest)

**Windows:**
```bash
cd deployment
deploy_lambda.bat
```

**Linux/Mac:**
```bash
cd deployment
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

This will:
1. Create ECR repository
2. Build & push Docker image
3. Create Lambda function
4. Set up Function URL
5. Display endpoint URL

**Test it:**
```bash
# Get the Function URL from the output, then:
curl https://your-function-url.lambda-url.us-east-1.on.aws/health
```

### Option 2: Kubernetes (EKS)

**Prerequisites:**
- EKS cluster running
- kubectl configured

**Deploy:**
```bash
cd deployment
chmod +x deploy_eks.sh
export EKS_CLUSTER_NAME="your-cluster-name"
./deploy_eks.sh
```

This will:
1. Create ECR repository
2. Build & push Docker image
3. Deploy to Kubernetes
4. Set up auto-scaling
5. Configure ingress

**Test it:**
```bash
# Port forward for testing
kubectl port-forward -n chatbot svc/chatbot-api 8000:80

# Test
curl http://localhost:8000/health
```

### Option 3: Local Docker (Testing)

```bash
# From project root
docker-compose -f deployment/docker-compose.yml up

# Test
curl http://localhost:8000/health
```

---

## 📊 Comparison

| Feature | Lambda | Kubernetes | Local Docker |
|---------|--------|------------|--------------|
| **Setup Time** | 5 min | 30 min | 2 min |
| **Complexity** | ⭐ Low | ⭐⭐⭐ High | ⭐ Low |
| **Cold Start** | 1-3s | None | None |
| **Scaling** | Automatic | Automatic | Manual |
| **Cost (low traffic)** | $5-10/mo | $180/mo | Free |
| **Cost (high traffic)** | $50-100/mo | $200-300/mo | N/A |
| **Best For** | MVP, Low-Medium traffic | Production, High traffic | Development |

---

## 🔧 Configuration

### Environment Variables

Both deployments use the same environment variables:

```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0  # Note: use region prefix!
DYNAMODB_TABLE_NAME=ChatbotConversations
```

**Important:** Use region-prefixed model IDs (`us.`, `eu.`, etc.)

See `docs/MODEL_IDS.md` for correct model ID formats.

### Changing the Model

Edit `.env` file:
```bash
# Faster, cheaper
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0

# Balanced (default)
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

# Best quality
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

Then restart/redeploy.

---

## 📝 Next Steps

### 1. Deploy to Your Preferred Platform

Choose based on your needs:
- **MVP/Testing?** → Lambda
- **Production?** → Kubernetes
- **Just testing locally?** → Docker

### 2. Test the Deployment

```bash
# Health check
curl https://your-endpoint/health

# Send a message
curl -X POST https://your-endpoint/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# List available models
curl -X POST https://your-endpoint/models/list
```

### 3. Set Up Monitoring

**Lambda:**
- CloudWatch Logs: `/aws/lambda/chatbot-api`
- CloudWatch Metrics: View invocations, errors, duration

**Kubernetes:**
```bash
# View logs
kubectl logs -n chatbot -l app=chatbot-api -f

# View metrics
kubectl top pods -n chatbot

# Check auto-scaling
kubectl get hpa -n chatbot
```

### 4. Enable Production Features

- [ ] Set up authentication (API Gateway or Ingress)
- [ ] Configure custom domain
- [ ] Set up SSL/TLS certificates
- [ ] Implement rate limiting
- [ ] Configure backups (DynamoDB PITR)
- [ ] Set up alerts (CloudWatch Alarms)

### 5. Optimize Costs

**Lambda:**
- Right-size memory allocation
- Use ARM architecture (20% cheaper)
- Implement caching

**Kubernetes:**
- Use Spot instances (70% cheaper)
- Right-size pod resources
- Enable Cluster Autoscaler

---

## 🎓 Learn More

### Architecture & Design
Read `deployment/ARCHITECTURE.md` to understand:
- System architecture diagrams
- Data flow
- Scaling strategies
- Security architecture
- Cost optimization
- High availability design

### Detailed Deployment Guides

**Lambda:**
- `deployment/DEPLOY_LAMBDA.md` - Complete Lambda guide
  - Manual deployment steps
  - API Gateway integration
  - Monitoring & troubleshooting
  - Cost optimization tips

**Kubernetes:**
- `deployment/DEPLOY_KUBERNETES.md` - Complete K8s guide
  - EKS cluster setup
  - IRSA (IAM Roles for Service Accounts)
  - Ingress configuration
  - Scaling strategies
  - Production best practices

---

## 🆘 Troubleshooting

### Common Issues

**1. Model ID Error**
```
Error: Invocation of model ID amazon.nova-pro-v1:0 isn't supported
```
**Fix:** Use region-prefixed ID: `us.amazon.nova-pro-v1:0`  
See `docs/MODEL_IDS.md` for details.

**2. Lambda Timeout**
```bash
# Increase timeout (default: 300s, max: 900s)
aws lambda update-function-configuration \
  --function-name chatbot-api \
  --timeout 900
```

**3. Kubernetes ImagePullBackOff**
```bash
# Check if image exists
aws ecr describe-images --repository-name chatbot-api

# Verify image URI in deployment.yaml
kubectl describe pod -n chatbot <pod-name>
```

**4. Bedrock Access Denied**
- Enable model access in AWS Bedrock Console
- Check IAM permissions
- Verify model ID format

---

## 📈 Monitoring Dashboard

### Lambda Metrics
```bash
# View recent logs
aws logs tail /aws/lambda/chatbot-api --follow

# Get metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chatbot-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Kubernetes Metrics
```bash
# Watch pods
kubectl get pods -n chatbot -w

# View logs
kubectl logs -n chatbot -l app=chatbot-api --tail=100 -f

# Check HPA
kubectl get hpa -n chatbot -w

# Check node resources
kubectl top nodes
```

---

## 🎉 Congratulations!

Your AWS Bedrock Chatbot is now deployment-ready with:

✅ **Two production-ready deployment options**  
✅ **Automated deployment scripts**  
✅ **Comprehensive documentation**  
✅ **Monitoring & logging setup**  
✅ **Auto-scaling configured**  
✅ **Security best practices**  

**Ready to deploy?** Pick your platform and follow the guide!

- **Quick start:** `deployment/README.md`
- **Lambda guide:** `deployment/DEPLOY_LAMBDA.md`
- **Kubernetes guide:** `deployment/DEPLOY_KUBERNETES.md`
- **Architecture:** `deployment/ARCHITECTURE.md`

---

**Questions?** Check the documentation or refer to the main [README.md](README.md).

Happy deploying! 🚀

