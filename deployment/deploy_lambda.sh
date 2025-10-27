#!/bin/bash
# Deploy to AWS Lambda using Docker Container Image

set -e

echo "=========================================="
echo "AWS Lambda Docker Deployment Script"
echo "=========================================="

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="chatbot-lambda"
LAMBDA_FUNCTION_NAME="chatbot-api"
IMAGE_TAG="latest"

ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "Region: ${AWS_REGION}"
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "ECR Repository: ${ECR_REPO_URI}"
echo ""

# Step 1: Create ECR repository if it doesn't exist
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
docker build -f deployment/Dockerfile.lambda -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 4: Tag image for ECR
echo "Step 4: Tagging image..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:${IMAGE_TAG}

# Step 5: Push to ECR
echo "Step 5: Pushing image to ECR..."
docker push ${ECR_REPO_URI}:${IMAGE_TAG}

# Step 6: Create or update Lambda function
echo "Step 6: Creating/Updating Lambda function..."

# Check if function exists
if aws lambda get-function --function-name ${LAMBDA_FUNCTION_NAME} --region ${AWS_REGION} > /dev/null 2>&1; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --image-uri ${ECR_REPO_URI}:${IMAGE_TAG} \
        --region ${AWS_REGION}
else
    echo "Creating new Lambda function..."
    
    # Create IAM role for Lambda
    ROLE_NAME="chatbot-lambda-role"
    TRUST_POLICY='{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'
    
    # Create role if it doesn't exist
    aws iam get-role --role-name ${ROLE_NAME} > /dev/null 2>&1 || \
        aws iam create-role --role-name ${ROLE_NAME} --assume-role-policy-document "${TRUST_POLICY}"
    
    # Attach policies
    aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
    aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
    
    ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
    
    echo "Waiting 10 seconds for IAM role to propagate..."
    sleep 10
    
    # Create function
    aws lambda create-function \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --package-type Image \
        --code ImageUri=${ECR_REPO_URI}:${IMAGE_TAG} \
        --role ${ROLE_ARN} \
        --timeout 300 \
        --memory-size 1024 \
        --environment "Variables={AWS_REGION=${AWS_REGION},BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0,DYNAMODB_TABLE_NAME=ChatbotConversations}" \
        --region ${AWS_REGION}
fi

# Step 7: Create function URL (for easy testing)
echo "Step 7: Creating Function URL..."
aws lambda create-function-url-config \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --auth-type NONE \
    --region ${AWS_REGION} > /dev/null 2>&1 || \
    echo "Function URL already exists"

# Add permissions for Function URL
aws lambda add-permission \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region ${AWS_REGION} > /dev/null 2>&1 || \
    echo "Permission already exists"

# Get Function URL
FUNCTION_URL=$(aws lambda get-function-url-config --function-name ${LAMBDA_FUNCTION_NAME} --region ${AWS_REGION} --query 'FunctionUrl' --output text)

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo "Function Name: ${LAMBDA_FUNCTION_NAME}"
echo "Function URL: ${FUNCTION_URL}"
echo ""
echo "Test with:"
echo "curl ${FUNCTION_URL}health"
echo ""
echo "Or send a chat message:"
echo "curl -X POST ${FUNCTION_URL}chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello!\"}'"
echo "=========================================="

