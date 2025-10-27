# Deploy to AWS Lambda with Docker

Complete guide for deploying the chatbot API to AWS Lambda using Docker container images.

## Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Docker** installed and running

3. **AWS Account** with appropriate permissions:
   - Lambda
   - ECR (Elastic Container Registry)
   - IAM
   - Bedrock
   - DynamoDB

## Deployment Options

### Option 1: Automated Deployment (Recommended)

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

This script will:
1. Create ECR repository
2. Build Docker image
3. Push to ECR
4. Create/update Lambda function
5. Set up Function URL
6. Display the endpoint URL

### Option 2: Manual Deployment

#### Step 1: Set Variables

```bash
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="chatbot-lambda"
LAMBDA_FUNCTION_NAME="chatbot-api"
```

#### Step 2: Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION}
```

#### Step 3: Login to ECR

```bash
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

#### Step 4: Build and Push Docker Image

```bash
# Build
docker build -f deployment/Dockerfile.lambda -t ${ECR_REPO_NAME}:latest .

# Tag
docker tag ${ECR_REPO_NAME}:latest \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

# Push
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
```

#### Step 5: Create IAM Role

**Trust Policy (trust-policy.json):**
```json
{
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
}
```

```bash
# Create role
aws iam create-role \
    --role-name chatbot-lambda-role \
    --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name chatbot-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name chatbot-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-role-policy \
    --role-name chatbot-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

#### Step 6: Create Lambda Function

```bash
aws lambda create-function \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --package-type Image \
    --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/chatbot-lambda-role \
    --timeout 300 \
    --memory-size 1024 \
    --environment "Variables={
        AWS_REGION=${AWS_REGION},
        BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0,
        DYNAMODB_TABLE_NAME=ChatbotConversations
    }"
```

#### Step 7: Create Function URL (Optional)

```bash
# Create Function URL
aws lambda create-function-url-config \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --auth-type NONE

# Add permissions
aws lambda add-permission \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE

# Get URL
aws lambda get-function-url-config \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --query 'FunctionUrl' \
    --output text
```

## Configuration

### Environment Variables

Update Lambda function environment variables:

```bash
aws lambda update-function-configuration \
    --function-name chatbot-api \
    --environment "Variables={
        AWS_REGION=us-east-1,
        BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0,
        DYNAMODB_TABLE_NAME=ChatbotConversations
    }"
```

### Increase Memory/Timeout

```bash
aws lambda update-function-configuration \
    --function-name chatbot-api \
    --timeout 300 \
    --memory-size 2048
```

## Testing

### Test Health Endpoint

```bash
FUNCTION_URL=$(aws lambda get-function-url-config --function-name chatbot-api --query 'FunctionUrl' --output text)
curl ${FUNCTION_URL}health
```

### Test Chat Endpoint

```bash
curl -X POST ${FUNCTION_URL}chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, how are you?"}'
```

### Test via Python

```python
import requests

FUNCTION_URL = "https://your-function-url.lambda-url.us-east-1.on.aws/"

# Health check
response = requests.get(f"{FUNCTION_URL}health")
print(response.json())

# Send message
response = requests.post(
    f"{FUNCTION_URL}chat",
    json={"message": "What is AWS Lambda?"}
)
print(response.json())
```

## API Gateway Integration (Optional)

For production, use API Gateway instead of Function URL:

### Create REST API

```bash
# Create API
API_ID=$(aws apigatewayv2 create-api \
    --name chatbot-api \
    --protocol-type HTTP \
    --target arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:chatbot-api \
    --query 'ApiId' \
    --output text)

# Grant API Gateway permission
aws lambda add-permission \
    --function-name chatbot-api \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${AWS_REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*/*"

# Get API endpoint
aws apigatewayv2 get-api --api-id ${API_ID} --query 'ApiEndpoint' --output text
```

## Updating the Function

When you make code changes:

```bash
# Build new image
docker build -f deployment/Dockerfile.lambda -t chatbot-lambda:latest .

# Tag and push
docker tag chatbot-lambda:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chatbot-lambda:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chatbot-lambda:latest

# Update function
aws lambda update-function-code \
    --function-name chatbot-api \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chatbot-lambda:latest
```

## Monitoring

### View Logs

```bash
# Get log group
aws logs tail /aws/lambda/chatbot-api --follow

# Or with specific time range
aws logs tail /aws/lambda/chatbot-api \
    --since 1h \
    --format short
```

### CloudWatch Dashboard

Access CloudWatch console to view:
- Invocations
- Duration
- Errors
- Throttles
- Memory usage

## Cost Optimization

1. **Right-size memory**: Start with 1024 MB, adjust based on usage
2. **Use provisioned concurrency** for consistent performance (costs more)
3. **Enable X-Ray** for detailed tracing
4. **Set up alarms** for cost monitoring

```bash
# Set provisioned concurrency
aws lambda put-provisioned-concurrency-config \
    --function-name chatbot-api \
    --provisioned-concurrent-executions 2 \
    --qualifier '$LATEST'
```

## Troubleshooting

### Cold Start Issues

- Increase memory (improves CPU and reduces cold start)
- Use provisioned concurrency
- Implement connection pooling

### Timeout Errors

```bash
# Increase timeout
aws lambda update-function-configuration \
    --function-name chatbot-api \
    --timeout 300
```

### Permission Errors

Check IAM role has:
- `AmazonBedrockFullAccess`
- `AmazonDynamoDBFullAccess`
- `AWSLambdaBasicExecutionRole`

### View Function Configuration

```bash
aws lambda get-function-configuration --function-name chatbot-api
```

## Clean Up

```bash
# Delete function
aws lambda delete-function --function-name chatbot-api

# Delete ECR repository
aws ecr delete-repository --repository-name chatbot-lambda --force

# Delete IAM role
aws iam detach-role-policy --role-name chatbot-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name chatbot-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam detach-role-policy --role-name chatbot-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam delete-role --role-name chatbot-lambda-role
```

## Best Practices

1. **Security**
   - Use IAM roles instead of access keys
   - Enable encryption at rest
   - Use VPC for production
   - Implement API Gateway authentication

2. **Performance**
   - Keep Lambda warm with CloudWatch Events
   - Use connection pooling
   - Optimize Docker image size

3. **Monitoring**
   - Enable X-Ray tracing
   - Set up CloudWatch alarms
   - Log structured JSON

4. **Cost**
   - Right-size memory allocation
   - Use ARM64 architecture for cost savings
   - Implement caching where possible

## Additional Resources

- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Lambda Performance Optimization](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Mangum - ASGI adapter for Lambda](https://mangum.io/)

---

**Questions?** 
- Main documentation: [README.md](../README.md)
- Deployment overview: [README.md](README.md)
- Testing guide: [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)

