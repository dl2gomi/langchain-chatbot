"""
DynamoDB Table Setup Script
Creates the necessary DynamoDB table for storing conversation history
"""

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def create_dynamodb_table(table_name="ChatbotConversations", region=None):
    """
    Create DynamoDB table for conversation storage
    
    Args:
        table_name: Name of the DynamoDB table
        region: AWS region (defaults to env var or us-east-1)
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    try:
        # Check if table already exists
        existing_tables = dynamodb.list_tables()['TableNames']
        
        if table_name in existing_tables:
            print(f"✓ Table '{table_name}' already exists")
            
            # Get table info
            response = dynamodb.describe_table(TableName=table_name)
            status = response['Table']['TableStatus']
            print(f"  Status: {status}")
            print(f"  Region: {region}")
            return True
        
        # Create table
        print(f"Creating DynamoDB table '{table_name}'...")
        
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'SessionId',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'Timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'SessionId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'LangChainChatbot'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Development'
                }
            ]
        )
        
        print(f"✓ Table '{table_name}' created successfully!")
        print(f"  Status: {response['TableDescription']['TableStatus']}")
        print(f"  ARN: {response['TableDescription']['TableArn']}")
        print(f"  Region: {region}")
        print("\nNote: Table is being created. It may take a few moments to become ACTIVE.")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        if error_code == 'ResourceInUseException':
            print(f"✓ Table '{table_name}' already exists")
            return True
        else:
            print(f"❌ Error creating table: {error_msg}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def delete_dynamodb_table(table_name="ChatbotConversations", region=None):
    """
    Delete DynamoDB table (use with caution!)
    
    Args:
        table_name: Name of the DynamoDB table
        region: AWS region
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    try:
        print(f"Deleting table '{table_name}'...")
        dynamodb.delete_table(TableName=table_name)
        print(f"✓ Table '{table_name}' deleted successfully")
        return True
    except ClientError as e:
        print(f"❌ Error deleting table: {e.response['Error']['Message']}")
        return False


def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("✓ AWS Credentials configured")
        print(f"  Account: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print("❌ AWS Credentials not configured properly")
        print(f"  Error: {str(e)}")
        print("\nPlease configure AWS credentials:")
        print("  1. Run: aws configure")
        print("  2. Or set environment variables in .env file")
        return False


def check_bedrock_access(region=None):
    """Check if we have access to AWS Bedrock"""
    region = region or os.getenv("AWS_REGION", "us-east-1")
    
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        
        # Try to list foundation models
        response = bedrock.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        print(f"✓ AWS Bedrock access confirmed ({region})")
        print(f"  Available models: {len(models)}")
        
        # Show some popular models
        claude_models = [m for m in models if 'claude' in m.get('modelId', '').lower()]
        if claude_models:
            print(f"  Claude models available: {len(claude_models)}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ No access to AWS Bedrock in {region}")
            print("  You may need to:")
            print("  1. Request access to Bedrock models in AWS Console")
            print("  2. Check IAM permissions")
            print("  3. Verify Bedrock is available in your region")
        else:
            print(f"❌ Error accessing Bedrock: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error checking Bedrock access: {str(e)}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("AWS Chatbot Setup")
    print("=" * 60)
    print()
    
    # Check AWS credentials
    print("Step 1: Checking AWS Credentials...")
    if not check_aws_credentials():
        return
    print()
    
    # Check Bedrock access
    region = os.getenv("AWS_REGION", "us-east-1")
    print(f"Step 2: Checking AWS Bedrock Access ({region})...")
    bedrock_ok = check_bedrock_access(region)
    print()
    
    if not bedrock_ok:
        print("⚠️  Warning: Bedrock access check failed")
        print("   The chatbot may not work without Bedrock access")
        response = input("   Continue with DynamoDB setup anyway? (y/n): ")
        if response.lower() != 'y':
            return
        print()
    
    # Create DynamoDB table
    print("Step 3: Setting up DynamoDB Table...")
    table_name = os.getenv("DYNAMODB_TABLE_NAME", "ChatbotConversations")
    create_dynamodb_table(table_name, region)
    print()
    
    print("=" * 60)
    print("✓ Setup Complete!")
    print("=" * 60)
    print("\nYou can now run the chatbot:")
    print("  python chatbot_aws.py")
    print()


if __name__ == "__main__":
    main()

