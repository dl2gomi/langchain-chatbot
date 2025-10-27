# Deployment Options

This folder contains deployment configurations for different environments.

## Docker Deployment

### Using Docker Compose (Easiest)

```bash
# From project root
cd deployment
docker-compose up
```

Or build and run manually:

```bash
# Build
docker build -f deployment/Dockerfile -t chatbot-api .

# Run
docker run -p 8000:8000 --env-file .env chatbot-api
```

### Configuration

Create a `.env` file in the project root:
```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
DYNAMODB_TABLE_NAME=ChatbotConversations
```

## AWS Lambda Deployment

Deploy as a serverless function:

```bash
python lambda_deploy.py
```

This will:
1. Package your code
2. Create/update Lambda function
3. Configure environment variables
4. Set up IAM roles (if needed)

### Requirements

- AWS CLI configured
- IAM role with permissions:
  - AWSLambdaBasicExecutionRole
  - AmazonBedrockFullAccess
  - AmazonDynamoDBFullAccess

## AWS ECS/Fargate

Use the Dockerfile to deploy to:
- Amazon ECS
- AWS Fargate
- Amazon EKS

## CloudFormation

Use `cloudformation_template.yaml` to deploy complete infrastructure:

```bash
aws cloudformation create-stack \
  --stack-name chatbot-api \
  --template-body file://cloudformation_template.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

## Other Cloud Providers

The Docker container can be deployed to:
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku**
- **DigitalOcean App Platform**
- **Fly.io**
- Any Kubernetes cluster

## Environment Variables

Required:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

Optional:
- `BEDROCK_MODEL_ID` (default: amazon.nova-pro-v1:0)
- `DYNAMODB_TABLE_NAME` (default: ChatbotConversations)

## Health Check

All deployments should configure health checks:
- **Endpoint:** `GET /health`
- **Expected Status:** 200
- **Interval:** 30s
- **Timeout:** 10s

