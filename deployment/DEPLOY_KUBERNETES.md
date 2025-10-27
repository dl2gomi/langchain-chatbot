# Deploy to Kubernetes (AWS EKS)

Complete guide for deploying the chatbot API to Kubernetes on AWS EKS.

## Prerequisites

1. **AWS CLI** installed and configured
2. **kubectl** installed
3. **Docker** installed
4. **eksctl** (optional, for cluster creation)
5. **AWS EKS Cluster** running

## Quick Start

### Automated Deployment

```bash
cd deployment
chmod +x deploy_eks.sh
export EKS_CLUSTER_NAME="your-cluster-name"
./deploy_eks.sh
```

## Manual Deployment

### Step 1: Create EKS Cluster (if needed)

```bash
eksctl create cluster \
    --name chatbot-cluster \
    --region us-east-1 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3 \
    --nodes-min 2 \
    --nodes-max 5 \
    --managed
```

### Step 2: Configure kubectl

```bash
aws eks update-kubeconfig --name chatbot-cluster --region us-east-1
kubectl get nodes
```

### Step 3: Build and Push Docker Image

```bash
# Set variables
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="chatbot-api"
ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Create ECR repository
aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REPO_URI}

# Build and push
docker build -f deployment/Dockerfile -t ${ECR_REPO_NAME}:latest .
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO_URI}:latest
docker push ${ECR_REPO_URI}:latest
```

### Step 4: Update Kubernetes Manifests

Edit `deployment/kubernetes/deployment.yaml`:

```yaml
# Replace:
image: YOUR_ECR_REPO/chatbot-api:latest

# With:
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/chatbot-api:latest
```

### Step 5: Create Secrets

**Option A: From .env file (recommended)**
```bash
kubectl create secret generic chatbot-secrets \
    --from-env-file=.env \
    --namespace=chatbot
```

**Option B: Manual**
```bash
kubectl create secret generic chatbot-secrets \
    --from-literal=AWS_ACCESS_KEY_ID=your_key \
    --from-literal=AWS_SECRET_ACCESS_KEY=your_secret \
    --namespace=chatbot
```

**Option C: Use IAM Roles for Service Accounts (IRSA) - Best Practice**

See [Setting Up IRSA](#setting-up-irsa) below.

### Step 6: Deploy to Kubernetes

```bash
cd deployment/kubernetes

# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml  # Skip if using IRSA
kubectl apply -f serviceaccount.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f ingress.yaml  # Optional
```

**Or use Kustomize:**
```bash
kubectl apply -k deployment/kubernetes/
```

### Step 7: Verify Deployment

```bash
# Check all resources
kubectl get all -n chatbot

# Check pods
kubectl get pods -n chatbot

# View logs
kubectl logs -n chatbot -l app=chatbot-api --tail=100

# Check deployment status
kubectl rollout status deployment/chatbot-api -n chatbot
```

## Accessing the API

### Method 1: Port Forward (Testing)

```bash
kubectl port-forward -n chatbot svc/chatbot-api 8000:80

# Test
curl http://localhost:8000/health
```

### Method 2: LoadBalancer Service

Edit `deployment/kubernetes/service.yaml`:

```yaml
spec:
  type: LoadBalancer  # Change from ClusterIP
```

Apply and get external IP:

```bash
kubectl apply -f service.yaml
kubectl get svc -n chatbot chatbot-api

# Wait for EXTERNAL-IP
# Access via: http://<EXTERNAL-IP>
```

### Method 3: Ingress (Production)

**Install AWS Load Balancer Controller:**

```bash
# Add Helm repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=chatbot-cluster \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller
```

**Apply Ingress:**

```bash
kubectl apply -f ingress.yaml

# Get ALB address
kubectl get ingress -n chatbot
```

## Configuration

### Update ConfigMap

```bash
kubectl edit configmap chatbot-config -n chatbot

# Or
kubectl create configmap chatbot-config \
    --from-literal=AWS_REGION=us-east-1 \
    --from-literal=BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0 \
    --from-literal=DYNAMODB_TABLE_NAME=ChatbotConversations \
    --namespace=chatbot \
    --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up changes
kubectl rollout restart deployment/chatbot-api -n chatbot
```

### Update Secrets

```bash
kubectl create secret generic chatbot-secrets \
    --from-literal=AWS_ACCESS_KEY_ID=new_key \
    --from-literal=AWS_SECRET_ACCESS_KEY=new_secret \
    --namespace=chatbot \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/chatbot-api -n chatbot
```

## Scaling

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment/chatbot-api -n chatbot --replicas=5

# Check status
kubectl get pods -n chatbot
```

### Auto-Scaling (HPA)

Horizontal Pod Autoscaler is configured in `hpa.yaml`:

```bash
# Check HPA status
kubectl get hpa -n chatbot

# View detailed info
kubectl describe hpa chatbot-hpa -n chatbot
```

**Modify HPA:**

```bash
kubectl edit hpa chatbot-hpa -n chatbot
```

## Setting Up IRSA

**IAM Roles for Service Accounts** is the recommended way to grant AWS permissions.

### Step 1: Create OIDC Provider

```bash
eksctl utils associate-iam-oidc-provider \
    --cluster chatbot-cluster \
    --approve
```

### Step 2: Create IAM Policy

**policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ChatbotConversations"
    }
  ]
}
```

```bash
aws iam create-policy \
    --policy-name ChatbotEKSPolicy \
    --policy-document file://policy.json
```

### Step 3: Create Service Account with IAM Role

```bash
eksctl create iamserviceaccount \
    --name chatbot-sa \
    --namespace chatbot \
    --cluster chatbot-cluster \
    --attach-policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/ChatbotEKSPolicy \
    --approve \
    --override-existing-serviceaccounts
```

### Step 4: Update Deployment

The deployment already references `chatbot-sa`. Just remove AWS credentials from environment:

```yaml
# In deployment.yaml, remove these:
- name: AWS_ACCESS_KEY_ID
  valueFrom:
    secretKeyRef:
      name: chatbot-secrets
      key: AWS_ACCESS_KEY_ID
- name: AWS_SECRET_ACCESS_KEY
  valueFrom:
    secretKeyRef:
      name: chatbot-secrets
      key: AWS_SECRET_ACCESS_KEY
```

## Monitoring

### View Logs

```bash
# All pods
kubectl logs -n chatbot -l app=chatbot-api --tail=100 -f

# Specific pod
kubectl logs -n chatbot chatbot-api-xxxxx-yyyy -f

# Previous container (if crashed)
kubectl logs -n chatbot chatbot-api-xxxxx-yyyy --previous
```

### Metrics

```bash
# Install metrics server (if not already)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View metrics
kubectl top nodes
kubectl top pods -n chatbot
```

### Events

```bash
kubectl get events -n chatbot --sort-by='.lastTimestamp'
```

## Updating the Application

### Rolling Update

```bash
# Build new image with tag
docker build -f deployment/Dockerfile -t ${ECR_REPO_URI}:v2.0 .
docker push ${ECR_REPO_URI}:v2.0

# Update deployment
kubectl set image deployment/chatbot-api \
    chatbot-api=${ECR_REPO_URI}:v2.0 \
    -n chatbot

# Watch rollout
kubectl rollout status deployment/chatbot-api -n chatbot

# Rollback if needed
kubectl rollout undo deployment/chatbot-api -n chatbot
```

### Blue-Green Deployment

1. Create new deployment with different name
2. Test the new deployment
3. Update service selector to point to new deployment
4. Delete old deployment

### Canary Deployment

Use a service mesh like Istio or AWS App Mesh for canary deployments.

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod -n chatbot chatbot-api-xxxxx-yyyy
kubectl logs -n chatbot chatbot-api-xxxxx-yyyy
```

### ImagePullBackOff

```bash
# Check ECR permissions
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin ${ECR_REPO_URI}

# Verify image exists
aws ecr describe-images --repository-name chatbot-api
```

### CrashLoopBackOff

```bash
# Check logs
kubectl logs -n chatbot chatbot-api-xxxxx-yyyy --previous

# Check environment variables
kubectl exec -n chatbot chatbot-api-xxxxx-yyyy -- env
```

### Connection to AWS Services Failing

- Verify IAM permissions
- Check security groups
- Verify VPC configuration
- Check if using IRSA correctly

## Production Best Practices

1. **Security**
   - Use IRSA instead of access keys
   - Enable Pod Security Standards
   - Use Network Policies
   - Scan images for vulnerabilities

2. **High Availability**
   - Run at least 3 replicas across AZs
   - Configure Pod Disruption Budgets
   - Use node affinity rules

3. **Resource Management**
   - Set resource requests and limits
   - Use HPA for auto-scaling
   - Configure cluster autoscaler

4. **Monitoring**
   - Use Prometheus + Grafana
   - Configure CloudWatch Container Insights
   - Set up alerts

5. **Cost Optimization**
   - Use spot instances for non-critical workloads
   - Right-size resource requests
   - Use cluster autoscaler

## Clean Up

```bash
# Delete application
kubectl delete namespace chatbot

# Delete ECR repository
aws ecr delete-repository --repository-name chatbot-api --force

# Delete EKS cluster
eksctl delete cluster --name chatbot-cluster
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                   Internet                       │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │  AWS ALB       │
         │  (Ingress)     │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │  Kubernetes    │
         │  Service       │
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ Pod 1 │   │ Pod 2 │   │ Pod 3 │
│       │   │       │   │       │
│FastAPI│   │FastAPI│   │FastAPI│
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼──────┐        ┌───────▼─────┐
│  Bedrock │        │  DynamoDB   │
│  (LLM)   │        │  (History)  │
└──────────┘        └─────────────┘
```

## Additional Resources

- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

---

**Questions?**
- Main documentation: [README.md](../README.md)
- Deployment overview: [README.md](README.md)
- Testing guide: [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)

