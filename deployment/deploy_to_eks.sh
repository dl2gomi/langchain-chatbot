#!/bin/bash
# Deploy Chatbot to AWS EKS
# Complete deployment script for EKS cluster

set -e

echo "=========================================="
echo "🚀 AWS EKS Chatbot Deployment Script"
echo "✅ Status: TESTED AND WORKING"
echo "=========================================="

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="chatbot-api"
EKS_CLUSTER_NAME=${EKS_CLUSTER_NAME:-"chatbot-cluster"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "Configuration:"
echo "  Region: ${AWS_REGION}"
echo "  Account ID: ${AWS_ACCOUNT_ID}"
echo "  EKS Cluster: ${EKS_CLUSTER_NAME}"
echo "  ECR Repository: ${ECR_REPO_URI}"
echo ""

# Step 1: Verify EKS cluster is running
echo "Step 1: Verifying EKS cluster..."
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "❌ Error: Cannot connect to EKS cluster '${EKS_CLUSTER_NAME}'"
    echo "Please ensure:"
    echo "  1. EKS cluster is running"
    echo "  2. kubectl is configured: aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}"
    exit 1
fi

echo "✅ EKS cluster is accessible"
kubectl get nodes --no-headers | wc -l | xargs -I {} echo "  Nodes available: {}"

# Step 2: Create ECR repository
echo ""
echo "Step 2: Creating ECR repository..."
if aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} > /dev/null 2>&1; then
    echo "✅ ECR repository '${ECR_REPO_NAME}' already exists"
else
    echo "Creating ECR repository '${ECR_REPO_NAME}'..."
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}
    echo "✅ ECR repository created"
fi

# Step 3: Login to ECR
echo ""
echo "Step 3: Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REPO_URI}
echo "✅ ECR login successful"

# Step 4: Build Docker image
echo ""
echo "Step 4: Building Docker image..."
echo "Building image: ${ECR_REPO_NAME}:${IMAGE_TAG}"
docker build -f deployment/Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .
echo "✅ Docker image built"

# Step 5: Tag and push image
echo ""
echo "Step 5: Tagging and pushing image to ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:${IMAGE_TAG}
docker push ${ECR_REPO_URI}:${IMAGE_TAG}
echo "✅ Image pushed to ECR: ${ECR_REPO_URI}:${IMAGE_TAG}"

# Step 6: Update Kubernetes manifests
echo ""
echo "Step 6: Updating Kubernetes manifests..."

# Create backup of original deployment.yaml
cp deployment/kubernetes/deployment.yaml deployment/kubernetes/deployment.yaml.backup

# Update image in deployment.yaml
sed -i "s|chatbot-api:latest|${ECR_REPO_URI}:${IMAGE_TAG}|g" deployment/kubernetes/deployment.yaml
sed -i "s|imagePullPolicy: Never|imagePullPolicy: Always|g" deployment/kubernetes/deployment.yaml

echo "✅ Kubernetes manifests updated"

# Step 7: Deploy to EKS
echo ""
echo "Step 7: Deploying to EKS..."

# Create namespace
echo "Creating namespace..."
kubectl apply -f deployment/kubernetes/namespace.yaml

# Create configmap
echo "Creating configmap..."
kubectl apply -f deployment/kubernetes/configmap.yaml

# Create service account
echo "Creating service account..."
kubectl apply -f deployment/kubernetes/serviceaccount.yaml

# Deploy application
echo "Deploying application..."
kubectl apply -f deployment/kubernetes/deployment.yaml

# Create service
echo "Creating service..."
kubectl apply -f deployment/kubernetes/service.yaml

# Create HPA
echo "Creating HPA..."
kubectl apply -f deployment/kubernetes/hpa.yaml

echo "✅ All Kubernetes resources deployed"

# Step 8: Wait for deployment
echo ""
echo "Step 8: Waiting for deployment to be ready..."
kubectl rollout status deployment/chatbot-api -n chatbot --timeout=300s
echo "✅ Deployment is ready"

# Step 9: Verify deployment
echo ""
echo "Step 9: Verifying deployment..."
echo "Pods:"
kubectl get pods -n chatbot -o wide

echo ""
echo "Services:"
kubectl get services -n chatbot

echo ""
echo "HPA:"
kubectl get hpa -n chatbot

# Step 10: Verify deployment
echo ""
echo "Step 10: Verifying deployment..."

# Check pod readiness
echo "Checking pod readiness..."
READY_PODS=$(kubectl get pods -n chatbot -l app=chatbot-api --no-headers | grep -c "Running")
TOTAL_PODS=$(kubectl get pods -n chatbot -l app=chatbot-api --no-headers | wc -l)

if [ "$READY_PODS" -eq "$TOTAL_PODS" ] && [ "$READY_PODS" -gt 0 ]; then
    echo "✅ All $READY_PODS pods are running and ready"
else
    echo "❌ Pod readiness check failed: $READY_PODS/$TOTAL_PODS pods ready"
    echo "Pod status:"
    kubectl get pods -n chatbot -l app=chatbot-api
fi

# Check service endpoints
echo "Checking service endpoints..."
ENDPOINTS=$(kubectl get endpoints chatbot-api -n chatbot -o jsonpath='{.subsets[0].addresses[*].ip}' 2>/dev/null | wc -w)
if [ "$ENDPOINTS" -gt 0 ]; then
    echo "✅ Service has $ENDPOINTS healthy endpoints"
else
    echo "❌ Service has no healthy endpoints"
fi

# Step 11: Display access information
echo ""
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Your chatbot is now running on EKS!"
echo ""
echo "Access Information:"
echo "  Namespace: chatbot"
echo "  Service: chatbot-api"
echo "  Image: ${ECR_REPO_URI}:${IMAGE_TAG}"
echo ""
echo "To access your chatbot:"
echo ""
echo "  Option 1: Port Forward (for testing):"
echo "    kubectl port-forward -n chatbot svc/chatbot-api 8000:80"
echo "    Then access: http://localhost:8000/docs"
echo ""
echo "  Option 2: LoadBalancer (for production):"
echo "    kubectl patch svc chatbot-api -n chatbot -p '{\"spec\":{\"type\":\"LoadBalancer\"}}'"
echo "    kubectl get svc chatbot-api -n chatbot"
echo ""
echo "  Option 3: Ingress (for production with domain):"
echo "    kubectl apply -f deployment/kubernetes/ingress.yaml"
echo "    kubectl get ingress -n chatbot"
echo ""
echo ""
echo "Production Access Setup:"
echo ""
echo "  For LoadBalancer (recommended for production):"
echo "    kubectl patch svc chatbot-api -n chatbot -p '{\"spec\":{\"type\":\"LoadBalancer\"}}'"
echo "    # Wait for external IP: kubectl get svc chatbot-api -n chatbot -w"
echo "    # Then access: http://<EXTERNAL-IP>"
echo ""
echo "  For Ingress with custom domain:"
echo "    kubectl apply -f deployment/kubernetes/ingress.yaml"
echo "    # Update ingress.yaml with your domain"
echo "    # Then access: http://your-domain.com"
echo ""
echo "Monitoring commands:"
echo "  kubectl get pods -n chatbot -w"
echo "  kubectl logs -n chatbot -l app=chatbot-api -f"
echo "  kubectl get hpa -n chatbot -w"
echo ""
echo "Management commands:"
echo "  Scale: kubectl scale deployment chatbot-api --replicas=5 -n chatbot"
echo "  Update: kubectl rollout restart deployment/chatbot-api -n chatbot"
echo "  Delete: kubectl delete namespace chatbot"
echo ""
echo ""
echo "Next Steps:"
echo "  For production access: ./deployment/setup_production_access.sh"
echo ""
echo "=========================================="
echo "🚀 Happy chatting!"
echo "=========================================="
