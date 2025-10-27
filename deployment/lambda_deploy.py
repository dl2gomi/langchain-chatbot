"""
AWS Lambda Deployment Script
Packages and deploys the chatbot to AWS Lambda
"""

import os
import zipfile
import boto3
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def create_deployment_package(output_file="lambda_deployment.zip"):
    """Create a deployment package for Lambda"""
    
    print("Creating Lambda deployment package...")
    
    # Files to include
    files_to_include = [
        'lambda_handler.py',
        'chatbot_aws.py',
    ]
    
    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Python files
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  Added: {file}")
        
        # Note: Dependencies need to be installed in a package directory
        print("\n  Note: Install dependencies with:")
        print("    pip install -r requirements.txt -t ./package")
        print("    Add ./package/* to the zip file")
    
    print(f"\n✓ Deployment package created: {output_file}")
    return output_file


def create_lambda_function(
    function_name="ChatbotFunction",
    role_arn=None,
    region=None
):
    """
    Create or update Lambda function
    
    Args:
        function_name: Name for the Lambda function
        role_arn: IAM role ARN with Lambda and Bedrock permissions
        region: AWS region
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    
    if not role_arn:
        print("❌ IAM Role ARN is required")
        print("   Create a role with these permissions:")
        print("   - AWSLambdaBasicExecutionRole")
        print("   - AmazonBedrockFullAccess")
        print("   - AmazonDynamoDBFullAccess")
        return None
    
    lambda_client = boto3.client('lambda', region_name=region)
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Read zip file
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Try to create function
        print(f"\nCreating Lambda function '{function_name}'...")
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_handler.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30,
            MemorySize=512,
            Environment={
                'Variables': {
                    'AWS_REGION': region,
                    'DYNAMODB_TABLE_NAME': os.getenv('DYNAMODB_TABLE_NAME', 'ChatbotConversations')
                }
            },
            Tags={
                'Application': 'LangChainChatbot',
                'Environment': 'Production'
            }
        )
        
        print(f"✓ Lambda function created successfully!")
        print(f"  ARN: {response['FunctionArn']}")
        return response
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        print(f"Function exists, updating...")
        
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✓ Lambda function updated successfully!")
        print(f"  ARN: {response['FunctionArn']}")
        return response
        
    except Exception as e:
        print(f"❌ Error deploying Lambda: {str(e)}")
        return None


def create_api_gateway(lambda_arn, region=None):
    """Create API Gateway for the Lambda function"""
    region = region or os.getenv("AWS_REGION", "us-east-1")
    
    apigw = boto3.client('apigatewayv2', region_name=region)
    
    try:
        print("\nCreating API Gateway...")
        
        # Create HTTP API
        response = apigw.create_api(
            Name='ChatbotAPI',
            ProtocolType='HTTP',
            Description='API Gateway for AWS Chatbot',
            CorsConfiguration={
                'AllowOrigins': ['*'],
                'AllowMethods': ['POST', 'GET', 'OPTIONS'],
                'AllowHeaders': ['Content-Type', 'Authorization']
            }
        )
        
        api_id = response['ApiId']
        api_endpoint = response['ApiEndpoint']
        
        print(f"✓ API Gateway created")
        print(f"  API ID: {api_id}")
        print(f"  Endpoint: {api_endpoint}")
        
        # Create integration
        integration_response = apigw.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=lambda_arn,
            PayloadFormatVersion='2.0'
        )
        
        integration_id = integration_response['IntegrationId']
        
        # Create route
        route_response = apigw.create_route(
            ApiId=api_id,
            RouteKey='POST /chat',
            Target=f'integrations/{integration_id}'
        )
        
        # Create stage
        stage_response = apigw.create_stage(
            ApiId=api_id,
            StageName='prod',
            AutoDeploy=True
        )
        
        full_url = f"{api_endpoint}/prod/chat"
        print(f"\n✓ API Gateway configured")
        print(f"  Chat endpoint: {full_url}")
        
        return {
            'api_id': api_id,
            'endpoint': full_url
        }
        
    except Exception as e:
        print(f"❌ Error creating API Gateway: {str(e)}")
        return None


def main():
    """Main deployment function"""
    print("=" * 60)
    print("AWS Lambda Deployment")
    print("=" * 60)
    print()
    
    # Get configuration
    function_name = input("Lambda function name [ChatbotFunction]: ").strip() or "ChatbotFunction"
    role_arn = input("IAM Role ARN (required): ").strip()
    
    if not role_arn:
        print("\n❌ IAM Role ARN is required")
        print("\nTo create an IAM role:")
        print("1. Go to AWS Console -> IAM -> Roles")
        print("2. Create role for Lambda")
        print("3. Attach policies:")
        print("   - AWSLambdaBasicExecutionRole")
        print("   - AmazonBedrockFullAccess")
        print("   - AmazonDynamoDBFullAccess")
        return
    
    # Deploy Lambda
    result = create_lambda_function(function_name, role_arn)
    
    if result:
        print("\n" + "=" * 60)
        print("✓ Deployment Complete!")
        print("=" * 60)
        print(f"\nLambda Function: {result['FunctionArn']}")
        print("\nYou can now:")
        print("1. Test the function in AWS Lambda console")
        print("2. Create an API Gateway to expose it as REST API")
        print("3. Use it in your applications")


if __name__ == "__main__":
    # Check if this is being run for package creation only
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'package':
        create_deployment_package()
    else:
        main()

