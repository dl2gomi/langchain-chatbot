@echo off
REM Deploy to AWS Lambda using Docker Container Image (Windows)

echo ==========================================
echo AWS Lambda Docker Deployment Script
echo ==========================================

REM Configuration
set AWS_REGION=us-east-1
set ECR_REPO_NAME=chatbot-lambda
set LAMBDA_FUNCTION_NAME=chatbot-api
set IMAGE_TAG=latest

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%%i
set ECR_REPO_URI=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPO_NAME%

echo Region: %AWS_REGION%
echo Account ID: %AWS_ACCOUNT_ID%
echo ECR Repository: %ECR_REPO_URI%
echo.

REM Step 1: Create ECR repository
echo Step 1: Creating ECR repository...
aws ecr describe-repositories --repository-names %ECR_REPO_NAME% --region %AWS_REGION% >nul 2>&1
if errorlevel 1 (
    aws ecr create-repository --repository-name %ECR_REPO_NAME% --region %AWS_REGION%
)

REM Step 2: Login to ECR
echo Step 2: Logging in to ECR...
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %AWS_REGION%') do set ECR_PASSWORD=%%i
echo %ECR_PASSWORD% | docker login --username AWS --password-stdin %ECR_REPO_URI%

REM Step 3: Build Docker image
echo Step 3: Building Docker image...
cd ..
docker build -f deployment\Dockerfile.lambda -t %ECR_REPO_NAME%:%IMAGE_TAG% .

REM Step 4: Tag image
echo Step 4: Tagging image...
docker tag %ECR_REPO_NAME%:%IMAGE_TAG% %ECR_REPO_URI%:%IMAGE_TAG%

REM Step 5: Push to ECR
echo Step 5: Pushing image to ECR...
docker push %ECR_REPO_URI%:%IMAGE_TAG%

REM Step 6: Update Lambda function
echo Step 6: Updating Lambda function...
aws lambda update-function-code --function-name %LAMBDA_FUNCTION_NAME% --image-uri %ECR_REPO_URI%:%IMAGE_TAG% --region %AWS_REGION%

REM Get Function URL
for /f "tokens=*" %%i in ('aws lambda get-function-url-config --function-name %LAMBDA_FUNCTION_NAME% --region %AWS_REGION% --query FunctionUrl --output text') do set FUNCTION_URL=%%i

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo Function Name: %LAMBDA_FUNCTION_NAME%
echo Function URL: %FUNCTION_URL%
echo.
echo Test with:
echo curl %FUNCTION_URL%health
echo ==========================================

cd deployment
pause

