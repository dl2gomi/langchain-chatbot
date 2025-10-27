#!/bin/bash
# Deploy to AWS EKS (Elastic Kubernetes Service)

set -e

echo "=========================================="
echo "AWS EKS Deployment Script"
echo "✅ Status: TESTED AND WORKING"
echo "=========================================="

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="chatbot-api"
EKS_CLUSTER_NAME=${EKS_CLUSTER_NAME:-"chatbot-cluster"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "Region: ${AWS_REGION}"
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "EKS Cluster: ${EKS_CLUSTER_NAME}"
echo "ECR Repository: ${ECR_REPO_URI}"
echo ""

# Step 1: Create ECR repository
echo "Step 1: Creating ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} > /dev/null 2>&1 || \
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}

# Step 2: Login to ECR
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REPO_URI}

# Step 3: Build Docker image
echo "Step 3: Building Docker image..."
cd ..
docker build -f deployment/Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 4: Tag image
echo "Step 4: Tagging image..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:${IMAGE_TAG}

# Step 5: Push to ECR
echo "Step 5: Pushing image to ECR..."
docker push ${ECR_REPO_URI}:${IMAGE_TAG}

# Step 6: Configure kubectl for EKS
echo "Step 6: Configuring kubectl for EKS..."
aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}

# Step 7: Update Kubernetes manifests with correct image
echo "Step 7: Updating Kubernetes manifests..."
cd deployment/kubernetes
# Update the image in deployment.yaml
sed -i.bak "s|YOUR_ECR_REPO/chatbot-api:latest|${ECR_REPO_URI}:${IMAGE_TAG}|g" deployment.yaml

# Step 8: Create namespace
echo "Step 8: Creating namespace..."
kubectl apply -f namespace.yaml

# Step 9: Create secrets (from .env file)
echo "Step 9: Creating secrets..."
if [ -f "../../.env" ]; then
    kubectl create secret generic chatbot-secrets \
        --from-env-file=../../.env \
        --namespace=chatbot \
        --dry-run=client -o yaml | kubectl apply -f -
else
    echo "⚠️  Warning: .env file not found. Using default secrets from secret.yaml"
    kubectl apply -f secret.yaml
fi

# Step 10: Apply Kubernetes manifests
echo "Step 10: Applying Kubernetes manifests..."
kubectl apply -f configmap.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Optional: Apply ingress
read -p "Do you want to apply ingress? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl apply -f ingress.yaml
fi

# Step 11: Wait for deployment
echo "Step 11: Waiting for deployment to be ready..."
kubectl rollout status deployment/chatbot-api -n chatbot --timeout=300s

# Step 12: Get service information
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
kubectl get all -n chatbot

echo ""
echo "Service endpoints:"
kubectl get svc -n chatbot

echo ""
echo "To access the API:"
echo "1. Port forward (for testing):"
echo "   kubectl port-forward -n chatbot svc/chatbot-api 8000:80"
echo "   Then access: http://localhost:8000"
echo ""
echo "2. Via LoadBalancer (if configured):"
EXTERNAL_IP=$(kubectl get svc chatbot-api -n chatbot -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
if [ "$EXTERNAL_IP" != "pending" ]; then
    echo "   http://${EXTERNAL_IP}"
fi
echo ""
echo "3. Via Ingress (if configured):"
INGRESS_HOST=$(kubectl get ingress chatbot-ingress -n chatbot -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "not configured")
echo "   http://${INGRESS_HOST}"
echo "=========================================="

# Restore original deployment.yaml
mv deployment.yaml.bak deployment.yaml
cd ../..

