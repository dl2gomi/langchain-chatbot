"""
AWS Lambda handler for FastAPI application
Supports both API Gateway REST API and HTTP API formats
"""

import json
from mangum import Mangum
from api import app

# Create Mangum adapter for Lambda
# This allows FastAPI to work seamlessly with AWS Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler_with_logging(event, context):
    """
    Lambda handler with enhanced logging
    Useful for debugging
    """
    print("=" * 60)
    print("Lambda Invocation")
    print("=" * 60)
    print(f"Event: {json.dumps(event, indent=2)}")
    print(f"Context: {context}")
    print("=" * 60)
    
    try:
        response = handler(event, context)
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "message": "Internal server error"
            })
        }

# Uncomment for enhanced logging
# handler = lambda_handler_with_logging
